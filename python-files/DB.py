import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random
import logging
import concurrent.futures
import argparse
import json
import os
import re
import hashlib
import csv
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import threading
from queue import Queue
import pickle
import gzip
import base64
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global configuration
CONFIG = {
    'max_retries': 3,
    'timeout': 30,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ],
    'rate_limit_delay': (1, 3),
    'max_concurrent_requests': 10,
    'cache_size': 1000,
    'backup_interval': 3600  # 1 hour
}

# Initialize NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

# Initialize stemmer
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

# Thread-safe cache
class ThreadSafeCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            return self.cache.get(key)
    
    def set(self, key, value):
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            self.cache[key] = value
    
    def clear(self):
        with self.lock:
            self.cache.clear()

# Global cache instance
url_cache = ThreadSafeCache(CONFIG['cache_size'])

# Enhanced database schema
DATABASE_SCHEMA = {
    'code_snippets': '''
        CREATE TABLE IF NOT EXISTS code_snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            code TEXT,
            language TEXT,
            file_extension TEXT,
            line_count INTEGER,
            complexity_score REAL,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            hash TEXT UNIQUE,
            is_duplicate BOOLEAN DEFAULT FALSE
        )
    ''',
    'urls': '''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            description TEXT,
            status_code INTEGER,
            response_time REAL,
            content_length INTEGER,
            last_scraped TIMESTAMP,
            scrape_count INTEGER DEFAULT 0,
            is_valid BOOLEAN DEFAULT TRUE
        )
    ''',
    'analytics': '''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT,
            metric_value REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''',
    'clusters': '''
        CREATE TABLE IF NOT EXISTS clusters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_id INTEGER,
            snippet_id INTEGER,
            similarity_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (snippet_id) REFERENCES code_snippets (id)
        )
    ''',
    'keywords': '''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE,
            frequency INTEGER DEFAULT 1,
            category TEXT,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
}

# Enhanced database management
class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.lock = threading.Lock()
    
    def connect(self):
        with self.lock:
            if self.conn is None:
                self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
            return self.conn
    
    def close(self):
        with self.lock:
            if self.conn:
                self.conn.close()
                self.conn = None
    
    def execute_query(self, query, params=None):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()  # Fixed indentation
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Database error: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()
    
    def create_tables(self):
        for table_name, schema in DATABASE_SCHEMA.items():
            self.execute_query(schema)
        logging.info("Database tables created successfully")
    
    def backup_database(self, backup_path=None):
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_name}.backup_{timestamp}.db"
        
        try:
            # Create backup
            source_conn = sqlite3.connect(self.db_name)
            backup_conn = sqlite3.connect(backup_path)
            source_conn.backup(backup_conn)
            source_conn.close()
            backup_conn.close()
            logging.info(f"Database backed up to {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return None

# Function to create a database and table
def create_database(db_name):
    db_manager = DatabaseManager(db_name)
    db_manager.create_tables()
    db_manager.close()
    return db_manager

# Enhanced URL validation and processing
def validate_url(url):
    """Validate and normalize URL"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'https://' + url
            parsed = urlparse(url)
        return url if parsed.netloc else None
    except:
        return None

def get_url_hash(url):
    """Generate hash for URL to detect duplicates"""
    return hashlib.md5(url.encode()).hexdigest()

def get_code_hash(code):
    """Generate hash for code content to detect duplicates"""
    return hashlib.sha256(code.encode()).hexdigest()

# Language detection and analysis
def detect_language(code):
    """Detect programming language from code snippet"""
    language_patterns = {
        'python': [r'def\s+\w+', r'import\s+\w+', r'from\s+\w+\s+import', r'if\s+__name__\s*==\s*["\']__main__["\']'],
        'javascript': [r'function\s+\w+', r'const\s+\w+', r'let\s+\w+', r'var\s+\w+', r'=>\s*'],
        'java': [r'public\s+class\s+\w+', r'private\s+\w+', r'System\.out\.print', r'import\s+java\.'],
        'cpp': [r'#include\s*<', r'int\s+main\s*\(', r'std::', r'using\s+namespace\s+std'],
        'c': [r'#include\s*<', r'int\s+main\s*\(', r'printf\s*\('],
        'html': [r'<html>', r'<head>', r'<body>', r'<!DOCTYPE'],
        'css': [r'\{[^}]*\}', r'@media', r'@import'],
        'sql': [r'SELECT\s+', r'INSERT\s+INTO', r'UPDATE\s+', r'DELETE\s+FROM'],
        'bash': [r'#!/bin/bash', r'#!/bin/sh', r'\$\w+', r'if\s+\[\s*'],
        'php': [r'<\?php', r'\$\w+', r'echo\s+', r'function\s+\w+']
    }
    
    code_lower = code.lower()
    scores = {}
    
    for lang, patterns in language_patterns.items():
        score = sum(len(re.findall(pattern, code_lower)) for pattern in patterns)
        if score > 0:
            scores[lang] = score
    
    return max(scores, key=scores.get) if scores else 'unknown'

def calculate_complexity(code):
    """Calculate code complexity score"""
    lines = code.split('\n')
    line_count = len([line for line in lines if line.strip()])
    
    # Count various complexity indicators
    complexity_indicators = {
        'loops': len(re.findall(r'\b(for|while|do)\b', code)),
        'conditionals': len(re.findall(r'\b(if|elif|else|switch|case)\b', code)),
        'functions': len(re.findall(r'\b(def|function|class|method)\b', code)),
        'nested_blocks': len(re.findall(r'\{[^{}]*\{', code)),
        'recursion': len(re.findall(r'\b(recursive|recursion)\b', code, re.IGNORECASE))
    }
    
    # Calculate weighted complexity score
    complexity_score = (
        line_count * 0.1 +
        complexity_indicators['loops'] * 2 +
        complexity_indicators['conditionals'] * 1.5 +
        complexity_indicators['functions'] * 1 +
        complexity_indicators['nested_blocks'] * 3 +
        complexity_indicators['recursion'] * 5
    )
    
    return complexity_score, line_count

def extract_keywords(code, language='unknown'):
    """Extract keywords from code snippet"""
    # Remove comments and strings
    code_clean = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code_clean = re.sub(r'/\*.*?\*/', '', code_clean, flags=re.DOTALL)
    code_clean = re.sub(r'"[^"]*"', '', code_clean)
    code_clean = re.sub(r"'[^']*'", '', code_clean)
    
    # Tokenize and clean
    tokens = word_tokenize(code_clean)
    tokens = [token.lower() for token in tokens if token.isalpha() and len(token) > 2]
    tokens = [token for token in tokens if token not in stop_words]
    tokens = [stemmer.stem(token) for token in tokens]
    
    # Count frequency
    keyword_counts = Counter(tokens)
    
    # Return top keywords as JSON string
    top_keywords = dict(keyword_counts.most_common(10))
    return json.dumps(top_keywords)

# Enhanced web scraping with retry logic and better error handling
def make_request(url, max_retries=CONFIG['max_retries']):
    """Make HTTP request with retry logic and proper headers"""
    headers = {
        'User-Agent': random.choice(CONFIG['user_agents']),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            response = requests.get(
                url, 
                headers=headers, 
                timeout=CONFIG['timeout'],
                allow_redirects=True
            )
            response_time = time.time() - start_time
            
            response.raise_for_status()  # Fixed indentation
            
            # Store URL info in cache
            url_info = {
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': len(response.content),
                'last_scraped': datetime.now().isoformat()
            }
            url_cache.set(url, url_info)
            
            return response, url_info
            
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(*CONFIG['rate_limit_delay']))
            else:
                logging.error(f"All attempts failed for {url}")
                return None, None
    
    return None, None

# Enhanced scraping functions
def scrape_url(url, db_manager, extract_metadata=True):
    """Enhanced URL scraping with metadata extraction and duplicate detection"""
    try:
        # Validate URL
        url = validate_url(url)
        if not url:
            logging.warning(f"Invalid URL: {url}")
            return False
        
        # Check cache first
        cached_info = url_cache.get(url)
        if cached_info and extract_metadata:
            logging.info(f"Using cached data for {url}")
            return True
        
        # Make request with retry logic
        response, url_info = make_request(url)
        if not response:
            return False
        
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract page metadata
        title = soup.find('title')
        title = title.get_text().strip() if title else "No title"
        
        description = soup.find('meta', attrs={'name': 'description'})
        description = description.get('content', '') if description else ""
        
        # Extract code snippets from various sources
        code_snippets = []
        
        # Standard pre/code blocks
        for code_block in soup.find_all(['pre', 'code']):
            code_text = code_block.get_text().strip()
            if len(code_text) > 10:  # Filter out very short snippets
                code_snippets.append({
                    'code': code_text,
                    'element': code_block.name,
                    'class': code_block.get('class', [])
                })
        
        # GitHub-specific extraction
        if 'github.com' in url:
            code_snippets.extend(extract_github_code(soup))
        
        # Stack Overflow specific extraction
        if 'stackoverflow.com' in url:
            code_snippets.extend(extract_stackoverflow_code(soup))
        
        # Process and store code snippets
        snippets_stored = 0
        for snippet_data in code_snippets:
            code = snippet_data['code']
            
            # Skip if too short or too long
            if len(code) < 20 or len(code) > 50000:
                continue
            
            # Detect language and calculate metrics
            language = detect_language(code)
            complexity_score, line_count = calculate_complexity(code)
            keywords = extract_keywords(code, language)
            code_hash = get_code_hash(code)
            
            # Check for duplicates
            existing = db_manager.execute_query(
                "SELECT id FROM code_snippets WHERE hash = ?", 
                (code_hash,)
            )
            
            is_duplicate = len(existing) > 0 if existing else False
            
            # Determine file extension
            file_extension = get_file_extension(language)
            
            # Store in database
            result = db_manager.execute_query('''
                INSERT OR IGNORE INTO code_snippets 
                (url, code, language, file_extension, line_count, complexity_score, 
                 keywords, hash, is_duplicate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (url, code, language, file_extension, line_count, 
                  complexity_score, keywords, code_hash, is_duplicate))
            
            if result is not None:
                snippets_stored += 1
                
                # Update keywords table
                update_keywords(keywords, db_manager)
        
        # Store URL metadata
        db_manager.execute_query('''
            INSERT OR REPLACE INTO urls 
            (url, title, description, status_code, response_time, content_length, 
             last_scraped, scrape_count, is_valid)
            VALUES (?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT scrape_count + 1 FROM urls WHERE url = ?), 1), ?)
        ''', (url, title, description, url_info['status_code'], 
              url_info['response_time'], url_info['content_length'],
              url_info['last_scraped'], url, True))
        
        logging.info(f"Scraped {url}: {snippets_stored} snippets stored")
        return True
        
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return False

def extract_github_code(soup):
    """Extract code from GitHub pages"""
    code_snippets = []
    
    # GitHub file viewer
    for file_div in soup.find_all('div', class_='file'):
        for code_block in file_div.find_all('td', class_='blob-code'):
            code_text = code_block.get_text()
            if code_text.strip():
                code_snippets.append({
                    'code': code_text,
                    'element': 'github_file',
                    'class': ['github']
                })
    
    # GitHub gists
    for gist_div in soup.find_all('div', class_='gist-file'):
        for code_block in gist_div.find_all('pre'):
            code_text = code_block.get_text()
            if code_text.strip():
                code_snippets.append({
                    'code': code_text,
                    'element': 'github_gist',
                    'class': ['gist']
                })
    
    return code_snippets

def extract_stackoverflow_code(soup):
    """Extract code from Stack Overflow pages"""
    code_snippets = []
    
    # Stack Overflow code blocks
    for code_block in soup.find_all('pre', class_='s-code-block'):
        code_text = code_block.get_text()
        if code_text.strip():
            code_snippets.append({
                'code': code_text,
                'element': 'stackoverflow',
                'class': ['so-code']
            })
    
    return code_snippets

def get_file_extension(language):
    """Get file extension for programming language"""
    extensions = {
        'python': '.py',
        'javascript': '.js',
        'java': '.java',
        'cpp': '.cpp',
        'c': '.c',
        'html': '.html',
        'css': '.css',
        'sql': '.sql',
        'bash': '.sh',
        'php': '.php',
        'ruby': '.rb',
        'go': '.go',
        'rust': '.rs',
        'swift': '.swift',
        'kotlin': '.kt',
        'typescript': '.ts',
        'csharp': '.cs',
        'r': '.r',
        'scala': '.scala'
    }
    return extensions.get(language, '.txt')

def update_keywords(keywords_json, db_manager):
    """Update keywords frequency table"""
    try:
        keywords_dict = json.loads(keywords_json)
        for keyword, frequency in keywords_dict.items():
            db_manager.execute_query('''
                INSERT OR REPLACE INTO keywords (keyword, frequency, last_seen)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (keyword, frequency))
    except Exception as e:
        logging.error(f"Error updating keywords: {e}")

# Advanced scraping and analysis functions
def scrape_multiple_urls(urls, db_manager, max_workers=CONFIG['max_concurrent_requests']):
    """Enhanced concurrent URL scraping with progress tracking"""
    successful = 0
    failed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(scrape_url, url, db_manager): url 
            for url in urls
        }
        
        # Process completed tasks
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                logging.error(f"Exception in {url}: {e}")
                failed += 1
    
    logging.info(f"Scraping completed: {successful} successful, {failed} failed")
    return successful, failed

def search_web_content(query, db_manager, max_results=50):
    """Enhanced web search with multiple search engines"""
    search_engines = [
        f"https://www.google.com/search?q={query}&num=20",
        f"https://www.bing.com/search?q={query}&count=20",
        f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
    ]
    
    all_links = set()
    
    for search_url in search_engines:
        try:
            response, _ = make_request(search_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')  # Fixed indentation

            # Extract links based on search engine
            if 'google.com' in search_url:
                links = extract_google_links(soup)
            elif 'bing.com' in search_url:
                links = extract_bing_links(soup)
            else:  # DuckDuckGo
                links = extract_duckduckgo_links(soup)
            
            all_links.update(links)
            
            if len(all_links) >= max_results:
                break
                
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logging.error(f"Search error for {search_url}: {e}")
    
    # Convert to list and limit results
    links_list = list(all_links)[:max_results]
    
    # Scrape found URLs
    if links_list:
        successful, failed = scrape_multiple_urls(links_list, db_manager)
        logging.info(f"Search '{query}': {successful} URLs scraped successfully")
    
    return links_list

def extract_google_links(soup):
    """Extract links from Google search results"""
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'url?q=' in href and 'webcache' not in href and 'google.com' not in href:
            try:
                clean_url = href.split('url?q=')[1].split('&sa=U')[0]
                if clean_url.startswith('http'):
                    links.append(clean_url)
            except:
                continue
    return links

def extract_bing_links(soup):
    """Extract links from Bing search results"""
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http') and 'bing.com' not in href and 'microsoft.com' not in href:
            links.append(href)
    return links

def extract_duckduckgo_links(soup):
    """Extract links from DuckDuckGo search results"""
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http') and 'duckduckgo.com' not in href:
            links.append(href)
    return links

def scrape_github_repos(query, db_manager, max_pages=10, sort_by='stars'):
    """Enhanced GitHub repository scraping with detailed metadata"""
    github_api_url = 'https://api.github.com/search/repositories'
    params = {
        'q': query,
        'per_page': 100,
        'sort': sort_by,
        'order': 'desc'
    }
    
    total_repos = 0

    for page in range(1, max_pages + 1):
        params['page'] = page
        try:
            response, _ = make_request(github_api_url)
            if not response or response.status_code != 200:
                logging.error(f"GitHub API error: {response.status_code if response else 'No response'}")
                time.sleep(random.uniform(2, 5))
                continue  # Fixed indentation

            data = response.json()
            repos = data.get('items', [])

            if not repos:
                break

            # Process each repository
            for repo in repos:
                repo_url = repo['html_url']
                repo_name = repo['name']
                repo_description = repo.get('description', '')
                stars = repo.get('stargazers_count', 0)
                forks = repo.get('forks_count', 0)
                language = repo.get('language', 'unknown')
                
                # Store repository metadata
                db_manager.execute_query('''
                    INSERT OR REPLACE INTO urls 
                    (url, title, description, status_code, response_time, content_length, 
                     last_scraped, scrape_count, is_valid)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                ''', (repo_url, repo_name, repo_description, 200, 0, 0, 
                      datetime.now().isoformat(), True))
                
                # Scrape the repository
                success = scrape_url(repo_url, db_manager)
                if success:
                    total_repos += 1
                
                # Also scrape raw file URLs for better code extraction
                scrape_github_raw_files(repo, db_manager)
            
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logging.error(f"Error processing GitHub page {page}: {e}")
            time.sleep(random.uniform(2, 5))
    
    logging.info(f"GitHub scraping completed: {total_repos} repositories processed")
    return total_repos

def scrape_github_raw_files(repo, db_manager):
    """Scrape raw files from GitHub repository"""
    try:
        # Get repository contents
        contents_url = f"https://api.github.com/repos/{repo['full_name']}/contents"
        response, _ = make_request(contents_url)
        
        if not response or response.status_code != 200:
            return
        
        contents = response.json()
        
        # Process files (limit to first 20 files to avoid rate limiting)
        for item in contents[:20]:
            if item['type'] == 'file' and item['size'] < 100000:  # Skip large files
                file_url = item['download_url']
                if file_url:
                    # Scrape raw file content
                    file_response, _ = make_request(file_url)
                    if file_response:
                        code = file_response.text
                        if len(code) > 20:
                            # Process and store the file content
                            language = detect_language(code)
                            complexity_score, line_count = calculate_complexity(code)
                            keywords = extract_keywords(code, language)
                            code_hash = get_code_hash(code)
                            
                            db_manager.execute_query('''
                                INSERT OR IGNORE INTO code_snippets 
                                (url, code, language, file_extension, line_count, complexity_score, 
                                 keywords, hash, is_duplicate)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (file_url, code, language, get_file_extension(language), 
                                  line_count, complexity_score, keywords, code_hash, False))
        
    except Exception as e:
        logging.error(f"Error scraping GitHub files: {e}")

# Data analysis and clustering functions
def analyze_code_patterns(db_manager):
    """Analyze patterns in collected code snippets"""
    try:
        # Get all code snippets
        snippets = db_manager.execute_query('''
            SELECT id, code, language, complexity_score, keywords 
            FROM code_snippets 
            WHERE is_duplicate = FALSE
        ''')
        
        if not snippets:
            logging.warning("No code snippets found for analysis")
            return
        
        # Language distribution
        language_counts = defaultdict(int)
        complexity_scores = []
        
        for snippet in snippets:
            language_counts[snippet['language']] += 1
            complexity_scores.append(snippet['complexity_score'])
        
        # Store analytics
        for lang, count in language_counts.items():
            db_manager.execute_query('''
                INSERT INTO analytics (metric_name, metric_value, metadata)
                VALUES (?, ?, ?)
            ''', (f'language_count_{lang}', count, json.dumps({'language': lang})))
        
        # Complexity statistics
        if complexity_scores:
            avg_complexity = np.mean(complexity_scores)
            max_complexity = np.max(complexity_scores)
            min_complexity = np.min(complexity_scores)
            
            db_manager.execute_query('''
                INSERT INTO analytics (metric_name, metric_value, metadata)
                VALUES (?, ?, ?)
            ''', ('avg_complexity', avg_complexity, json.dumps({'type': 'statistics'})))
            
            db_manager.execute_query('''
                INSERT INTO analytics (metric_name, metric_value, metadata)
                VALUES (?, ?, ?)
            ''', ('max_complexity', max_complexity, json.dumps({'type': 'statistics'})))
        
        logging.info(f"Code analysis completed: {len(snippets)} snippets analyzed")
        
    except Exception as e:
        logging.error(f"Error in code analysis: {e}")

def cluster_similar_code(db_manager, n_clusters=10):
    """Cluster similar code snippets using TF-IDF and K-means"""
    try:
        # Get code snippets for clustering
        snippets = db_manager.execute_query('''
            SELECT id, code, language FROM code_snippets 
            WHERE is_duplicate = FALSE AND LENGTH(code) > 50
        ''')
        
        if len(snippets) < n_clusters:
            logging.warning("Not enough snippets for clustering")
            return
        
        # Prepare text data
        texts = [snippet['code'] for snippet in snippets]
        
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        # Store cluster assignments
        for i, snippet in enumerate(snippets):
            db_manager.execute_query('''
                INSERT INTO clusters (cluster_id, snippet_id, similarity_score)
                VALUES (?, ?, ?)
            ''', (int(cluster_labels[i]), snippet['id'], 0.0))
        
        logging.info(f"Clustering completed: {len(snippets)} snippets clustered into {n_clusters} groups")
        
    except Exception as e:
        logging.error(f"Error in clustering: {e}")

def generate_analytics_report(db_manager, output_file='analytics_report.html'):
    """Generate comprehensive analytics report"""
    try:
        # Get analytics data
        analytics = db_manager.execute_query('SELECT * FROM analytics ORDER BY timestamp DESC')
        language_stats = db_manager.execute_query('''
            SELECT language, COUNT(*) as count, AVG(complexity_score) as avg_complexity
            FROM code_snippets 
            WHERE is_duplicate = FALSE
            GROUP BY language
            ORDER BY count DESC
        ''')
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Code Database Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Code Database Analytics Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Language Distribution</h2>
                <table>
                    <tr><th>Language</th><th>Count</th><th>Average Complexity</th></tr>
        """
        
        for stat in language_stats:
            html_content += f"""
                    <tr>
                        <td>{stat['language']}</td>
                        <td>{stat['count']}</td>
                        <td>{stat['avg_complexity']:.2f}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>Recent Analytics</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th><th>Timestamp</th></tr>
        """
        
        for metric in analytics[:20]:  # Show last 20 metrics
            html_content += f"""
                    <tr>
                        <td>{metric['metric_name']}</td>
                        <td>{metric['metric_value']:.2f}</td>
                        <td>{metric['timestamp']}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        # Write report to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info(f"Analytics report generated: {output_file}")
        
    except Exception as e:
        logging.error(f"Error generating analytics report: {e}")

def export_data(db_manager, format='csv', output_dir='exports'):
    """Export database data in various formats"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        if format == 'csv':
            # Export code snippets
            snippets = db_manager.execute_query('SELECT * FROM code_snippets')
            if snippets:
                df = pd.DataFrame(snippets)
                df.to_csv(f'{output_dir}/code_snippets.csv', index=False)
            
            # Export URLs
            urls = db_manager.execute_query('SELECT * FROM urls')
            if urls:
                df = pd.DataFrame(urls)
                df.to_csv(f'{output_dir}/urls.csv', index=False)
            
            # Export analytics
            analytics = db_manager.execute_query('SELECT * FROM analytics')
            if analytics:
                df = pd.DataFrame(analytics)
                df.to_csv(f'{output_dir}/analytics.csv', index=False)
        
        elif format == 'json':
            # Export as JSON
            data = {
                'code_snippets': [dict(row) for row in db_manager.execute_query('SELECT * FROM code_snippets')],
                'urls': [dict(row) for row in db_manager.execute_query('SELECT * FROM urls')],
                'analytics': [dict(row) for row in db_manager.execute_query('SELECT * FROM analytics')]
            }
            
            with open(f'{output_dir}/database_export.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        logging.info(f"Data exported to {output_dir} in {format} format")
        
    except Exception as e:
        logging.error(f"Error exporting data: {e}")

def cleanup_database(db_manager, days_old=30):
    """Clean up old and duplicate data"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Remove old URLs that haven't been scraped recently
        old_urls = db_manager.execute_query('''
            DELETE FROM urls 
            WHERE last_scraped < ? AND is_valid = FALSE
        ''', (cutoff_date.isoformat(),))
        
        # Remove duplicate code snippets (keep the first one)
        duplicates = db_manager.execute_query('''
            DELETE FROM code_snippets 
            WHERE id NOT IN (
                SELECT MIN(id) FROM code_snippets 
                GROUP BY hash
            ) AND is_duplicate = TRUE
        ''')
        
        # Clean up old analytics data
        old_analytics = db_manager.execute_query('''
            DELETE FROM analytics 
            WHERE timestamp < ?
        ''', (cutoff_date.isoformat(),))
        
        logging.info("Database cleanup completed")
        
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")

# Enhanced main function
def main(args):
    db_manager = create_database(args.db_name)

    try:
        # List of URLs to scrape for general coding content
        general_coding_urls = [
            'https://github.com/torvalds/linux',
            'https://github.com/facebook/react',
            'https://github.com/tensorflow/tensorflow',
            'https://github.com/microsoft/vscode',
            'https://github.com/pytorch/pytorch',
            'https://github.com/kubernetes/kubernetes',
            'https://github.com/docker/docker',
            'https://github.com/ansible/ansible',
            'https://github.com/hashicorp/terraform',
            'https://github.com/elastic/elasticsearch'
        ]

        # Scrape general coding content
        logging.info("Starting general coding content scraping...")
        successful, failed = scrape_multiple_urls(general_coding_urls, db_manager)
        logging.info(f"General scraping: {successful} successful, {failed} failed")

        # Search for various programming content
        search_queries = [
            'python programming examples',
            'javascript tutorials',
            'machine learning code',
            'web development snippets',
            'data science python',
            'react components',
            'node.js examples',
            'docker configurations',
            'kubernetes yaml',
            'terraform infrastructure'
        ]

        for query in search_queries:
            logging.info(f"Searching for: {query}")
            search_web_content(query, db_manager, max_results=20)

        # Scrape GitHub repositories
        github_queries = [
            'language:python stars:>1000',
            'language:javascript stars:>1000',
            'language:java stars:>1000',
            'language:go stars:>1000',
            'language:rust stars:>1000',
            'machine learning',
            'web framework',
            'data science',
            'devops tools',
            'security tools'
        ]

        for query in github_queries:
            logging.info(f"Scraping GitHub: {query}")
            scrape_github_repos(query, db_manager, max_pages=args.max_pages)

        # Perform analysis
        logging.info("Performing code analysis...")
        analyze_code_patterns(db_manager)
        
        # Cluster similar code
        logging.info("Clustering similar code...")
        cluster_similar_code(db_manager, n_clusters=15)
        
        # Generate analytics report
        logging.info("Generating analytics report...")
        generate_analytics_report(db_manager, f'{args.db_name}_report.html')
        
        # Export data
        logging.info("Exporting data...")
        export_data(db_manager, format='csv', output_dir=f'{args.db_name}_exports')
        export_data(db_manager, format='json', output_dir=f'{args.db_name}_exports')
        
        # Cleanup old data
        logging.info("Cleaning up database...")
        cleanup_database(db_manager, days_old=30)
        
        # Create backup
        logging.info("Creating database backup...")
        backup_path = db_manager.backup_database()
        if backup_path:
            logging.info(f"Database backed up to: {backup_path}")
        
        logging.info("All tasks completed successfully!")
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
    finally:
        db_manager.close()

# Additional utility functions
def search_code_by_language(db_manager, language, limit=100):
    """Search for code snippets by programming language"""
    try:
        results = db_manager.execute_query('''
            SELECT id, url, code, complexity_score, line_count, created_at
            FROM code_snippets 
            WHERE language = ? AND is_duplicate = FALSE
            ORDER BY complexity_score DESC
            LIMIT ?
        ''', (language, limit))
        
        logging.info(f"Found {len(results)} {language} code snippets")
        return results
    except Exception as e:
        logging.error(f"Error searching by language: {e}")
        return []

def search_code_by_complexity(db_manager, min_complexity=0, max_complexity=1000):
    """Search for code snippets by complexity range"""
    try:
        results = db_manager.execute_query('''
            SELECT id, url, code, language, complexity_score, line_count
            FROM code_snippets 
            WHERE complexity_score BETWEEN ? AND ? AND is_duplicate = FALSE
            ORDER BY complexity_score DESC
        ''', (min_complexity, max_complexity))
        
        logging.info(f"Found {len(results)} code snippets with complexity {min_complexity}-{max_complexity}")
        return results
    except Exception as e:
        logging.error(f"Error searching by complexity: {e}")
        return []

def get_database_stats(db_manager):
    """Get comprehensive database statistics"""
    try:
        stats = {}
        
        # Code snippets count
        snippets_result = db_manager.execute_query('SELECT COUNT(*) as count FROM code_snippets')
        snippets_count = snippets_result[0]['count'] if snippets_result else 0
        stats['total_snippets'] = snippets_count
        
        # URLs count
        urls_result = db_manager.execute_query('SELECT COUNT(*) as count FROM urls')
        urls_count = urls_result[0]['count'] if urls_result else 0
        stats['total_urls'] = urls_count
        
        # Language distribution
        language_dist = db_manager.execute_query('''
            SELECT language, COUNT(*) as count 
            FROM code_snippets 
            WHERE is_duplicate = FALSE
            GROUP BY language 
            ORDER BY count DESC
        ''')
        stats['language_distribution'] = {row['language']: row['count'] for row in language_dist} if language_dist else {}
        
        # Average complexity
        complexity_result = db_manager.execute_query('''
            SELECT AVG(complexity_score) as avg_complexity 
            FROM code_snippets 
            WHERE is_duplicate = FALSE
        ''')
        avg_complexity = complexity_result[0]['avg_complexity'] if complexity_result else 0
        stats['average_complexity'] = avg_complexity or 0
        
        # Duplicate count
        duplicates_result = db_manager.execute_query('SELECT COUNT(*) as count FROM code_snippets WHERE is_duplicate = TRUE')
        duplicates_count = duplicates_result[0]['count'] if duplicates_result else 0
        stats['duplicates'] = duplicates_count
        
        return stats
    except Exception as e:
        logging.error(f"Error getting database stats: {e}")
        return {}

def create_word_cloud(db_manager, output_file='wordcloud.png'):
    """Create word cloud from code keywords"""
    try:
        # Get all keywords
        keywords = db_manager.execute_query('SELECT keyword, frequency FROM keywords ORDER BY frequency DESC LIMIT 100')
        
        if not keywords:
            logging.warning("No keywords found for word cloud")
            return
        
        # Create word frequency dictionary
        word_freq = {row['keyword']: row['frequency'] for row in keywords}
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate_from_frequencies(word_freq)
        
        # Save word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Code Keywords Word Cloud', fontsize=16)
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Word cloud saved to: {output_file}")
        
    except Exception as e:
        logging.error(f"Error creating word cloud: {e}")

def monitor_scraping_progress(db_manager):
    """Monitor and display scraping progress"""
    try:
        # Get current statistics
        stats = get_database_stats(db_manager)
        
        print("\n" + "="*50)
        print("SCRAPING PROGRESS REPORT")
        print("="*50)
        print(f"Total Code Snippets: {stats.get('total_snippets', 0)}")
        print(f"Total URLs: {stats.get('total_urls', 0)}")
        print(f"Duplicates Found: {stats.get('duplicates', 0)}")
        print(f"Average Complexity: {stats.get('average_complexity', 0):.2f}")
        
        print("\nLanguage Distribution:")
        for lang, count in list(stats.get('language_distribution', {}).items())[:10]:
            print(f"  {lang}: {count}")
        
        print("="*50)
        
    except Exception as e:
        logging.error(f"Error monitoring progress: {e}")

def setup_database_indexes(db_manager):
    """Create database indexes for better performance"""
    try:
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_code_language ON code_snippets(language)",
            "CREATE INDEX IF NOT EXISTS idx_code_complexity ON code_snippets(complexity_score)",
            "CREATE INDEX IF NOT EXISTS idx_code_created ON code_snippets(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_code_hash ON code_snippets(hash)",
            "CREATE INDEX IF NOT EXISTS idx_urls_scraped ON urls(last_scraped)",
            "CREATE INDEX IF NOT EXISTS idx_urls_valid ON urls(is_valid)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_clusters_cluster ON clusters(cluster_id)",
            "CREATE INDEX IF NOT EXISTS idx_keywords_frequency ON keywords(frequency)"
        ]
        
        for index_sql in indexes:
            db_manager.execute_query(index_sql)
        
        logging.info("Database indexes created successfully")
        
    except Exception as e:
        logging.error(f"Error creating indexes: {e}")

def validate_database_integrity(db_manager):
    """Validate database integrity and consistency"""
    try:
        issues = []
        
        # Check for orphaned records
        orphaned_clusters = db_manager.execute_query('''
            SELECT COUNT(*) as count FROM clusters c
            LEFT JOIN code_snippets cs ON c.snippet_id = cs.id
            WHERE cs.id IS NULL
        ''')
        
        orphaned_count = orphaned_clusters[0]['count'] if orphaned_clusters else 0
        if orphaned_count > 0:
            issues.append(f"Found {orphaned_count} orphaned cluster records")
        
        # Check for invalid complexity scores
        invalid_complexity = db_manager.execute_query('''
            SELECT COUNT(*) as count FROM code_snippets 
            WHERE complexity_score < 0 OR complexity_score > 10000
        ''')
        
        invalid_count = invalid_complexity[0]['count'] if invalid_complexity else 0
        if invalid_count > 0:
            issues.append(f"Found {invalid_count} records with invalid complexity scores")
        
        # Check for empty code snippets
        empty_code = db_manager.execute_query('''
            SELECT COUNT(*) as count FROM code_snippets 
            WHERE LENGTH(TRIM(code)) = 0
        ''')
        
        empty_count = empty_code[0]['count'] if empty_code else 0
        if empty_count > 0:
            issues.append(f"Found {empty_count} empty code snippets")
        
        if issues:
            logging.warning("Database integrity issues found:")
            for issue in issues:
                logging.warning(f"  - {issue}")
        else:
            logging.info("Database integrity check passed")
        
        return len(issues) == 0
        
    except Exception as e:
        logging.error(f"Error validating database integrity: {e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Advanced web scraping and code analysis system.')
    parser.add_argument('--db_name', type=str, default='coding.db', help='Name of the database file')
    parser.add_argument('--max_pages', type=int, default=10, help='Maximum number of pages to scrape from GitHub')
    parser.add_argument('--analyze_only', action='store_true', help='Only perform analysis on existing data')
    parser.add_argument('--export_only', action='store_true', help='Only export existing data')
    parser.add_argument('--stats_only', action='store_true', help='Only show database statistics')
    parser.add_argument('--cleanup', action='store_true', help='Only perform database cleanup')
    parser.add_argument('--validate', action='store_true', help='Only validate database integrity')
    parser.add_argument('--wordcloud', action='store_true', help='Generate word cloud from keywords')
    parser.add_argument('--monitor', action='store_true', help='Monitor scraping progress')
    
    args = parser.parse_args()
    
    if args.stats_only or args.monitor:
        # Just show statistics
        db_manager = DatabaseManager(args.db_name)
        try:
            if args.monitor:
                monitor_scraping_progress(db_manager)
            else:
                stats = get_database_stats(db_manager)
                print(json.dumps(stats, indent=2))
        finally:
            db_manager.close()
    elif args.analyze_only:
        # Only perform analysis
        db_manager = DatabaseManager(args.db_name)
        try:
            analyze_code_patterns(db_manager)
            cluster_similar_code(db_manager)
            generate_analytics_report(db_manager, f'{args.db_name}_report.html')
        finally:
            db_manager.close()
    elif args.export_only:
        # Only export data
        db_manager = DatabaseManager(args.db_name)
        try:
            export_data(db_manager, format='csv', output_dir=f'{args.db_name}_exports')
            export_data(db_manager, format='json', output_dir=f'{args.db_name}_exports')
        finally:
            db_manager.close()
    elif args.cleanup:
        # Only cleanup
        db_manager = DatabaseManager(args.db_name)
        try:
            cleanup_database(db_manager)
        finally:
            db_manager.close()
    elif args.validate:
        # Only validate
        db_manager = DatabaseManager(args.db_name)
        try:
            validate_database_integrity(db_manager)
        finally:
            db_manager.close()
    elif args.wordcloud:
        # Only generate word cloud
        db_manager = DatabaseManager(args.db_name)
        try:
            create_word_cloud(db_manager, f'{args.db_name}_wordcloud.png')
        finally:
            db_manager.close()
    else:
        # Full execution
        main(args)