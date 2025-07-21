"""
Kalbe e-Approval Document Scraper
Optimized for EXE compilation with PyInstaller
"""

import sys
import os
import json
from pathlib import Path
import traceback

# Add error handling for imports
def safe_import():
    """Safely import required packages with detailed error messages"""
    missing_packages = []
    
    try:
        import requests
    except ImportError:
        missing_packages.append('requests')
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_packages.append('beautifulsoup4')
    
    try:
        import pandas as pd
    except ImportError:
        missing_packages.append('pandas')
    
    try:
        import urllib3
    except ImportError:
        missing_packages.append('urllib3')
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    return requests, BeautifulSoup, pd, urllib3

# Import packages
requests, BeautifulSoup, pd, urllib3 = safe_import()

import time
from urllib.parse import urljoin
import re
from datetime import datetime

# Disable SSL warnings for internal networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class KalbeApprovalScraper:
    def __init__(self, verify_ssl=False):
        self.session = requests.Session()
        self.verify_ssl = verify_ssl
        self.base_url = "https://eapproval.kalbe.co.id"
        self.login_url = "https://eapproval.kalbe.co.id/Account/LoginView"
        self.documents_url = "https://eapproval.kalbe.co.id/DocApprovals/Index"
        self.config_file = "kalbe_config.json"
        
        # Headers to mimic real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
        
        # Default configuration
        return {
            "username": "",
            "password": "",
            "max_pages": 100,
            "delay_seconds": 1.5
        }
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")
    
    def get_credentials(self):
        """Get credentials from user or config file"""
        config = self.load_config()
        
        print("\n🔐 LOGIN CREDENTIALS")
        print("-" * 30)
        
        # Get username
        if config.get("username"):
            print(f"Current username: {config['username']}")
            use_saved = input("Use saved username? (y/n): ").lower().strip()
            if use_saved == 'y':
                username = config["username"]
            else:
                username = input("Enter username/email: ").strip()
        else:
            username = input("Enter username/email: ").strip()
        
        # Get password
        if config.get("password"):
            print("Password is saved in config")
            use_saved_pwd = input("Use saved password? (y/n): ").lower().strip()
            if use_saved_pwd == 'y':
                password = config["password"]
            else:
                password = input("Enter password: ").strip()
        else:
            password = input("Enter password: ").strip()
        
        # Ask to save credentials
        if username != config.get("username") or password != config.get("password"):
            save_creds = input("Save credentials for next time? (y/n): ").lower().strip()
            if save_creds == 'y':
                config["username"] = username
                config["password"] = password
                self.save_config(config)
        
        return username, password
    
    def test_connection(self):
        """Test connection to internal network"""
        try:
            print("🔗 Testing connection to Kalbe internal network...")
            response = self.session.get(self.base_url, timeout=15, verify=self.verify_ssl)
            
            if response.status_code == 200:
                print("✅ Successfully connected to Kalbe e-approval system!")
                return True
            else:
                print(f"⚠️ Connected but received status code: {response.status_code}")
                return True
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("Make sure you're connected to Kalbe's internal network")
            return False
    
    def login(self, username, password):
        """Login with enhanced error handling"""
        try:
            print(f"👤 Attempting to login as: {username}")
            
            # Get login page
            response = self.session.get(self.login_url, verify=self.verify_ssl, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find login form
            form = soup.find('form')
            if not form:
                print("❌ Login form not found")
                return False
            
            # Prepare login data
            login_data = {
                'Email': username,
                'Password': password
            }
            
            # Extract hidden fields (CSRF tokens, etc.)
            hidden_inputs = soup.find_all('input', type='hidden')
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value', '')
                if name:
                    login_data[name] = value
                    print(f"🔑 Found token: {name}")
            
            # Submit login
            login_response = self.session.post(
                self.login_url,
                data=login_data,
                verify=self.verify_ssl,
                allow_redirects=True,
                timeout=30
            )
            
            # Check login success
            success_indicators = [
                'dashboard', 'docapprovals', 'logout', 'daftar dokumen',
                'gustiana', 'compliance engineering supervisor'
            ]
            
            page_text = login_response.text.lower()
            url_text = login_response.url.lower()
            
            login_successful = any(
                indicator in page_text or indicator in url_text 
                for indicator in success_indicators
            )
            
            if login_successful:
                print("✅ Login successful!")
                print(f"📍 Redirected to: {login_response.url}")
                return True
            else:
                print("❌ Login failed")
                print(f"Status: {login_response.status_code}")
                print(f"URL: {login_response.url}")
                
                # Look for error messages
                error_soup = BeautifulSoup(login_response.content, 'html.parser')
                error_msgs = error_soup.find_all(string=re.compile(r'error|invalid|salah|gagal', re.I))
                if error_msgs:
                    print("Error messages:")
                    for msg in error_msgs[:3]:
                        if msg.strip():
                            print(f"  - {msg.strip()}")
                
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_page_data(self, page_num=1):
        """Extract data from specific page"""
        try:
            # Try different URL patterns
            page_urls = [
                f"{self.documents_url}?page={page_num}",
                f"{self.documents_url}#!/page/{page_num}",
                f"{self.documents_url}&page={page_num}",
            ]
            
            response = None
            for url in page_urls:
                try:
                    response = self.session.get(url, verify=self.verify_ssl, timeout=30)
                    if response.status_code == 200:
                        break
                except:
                    continue
            
            if not response or response.status_code != 200:
                print(f"❌ Failed to access page {page_num}")
                return [], False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find table
            table = None
            selectors = [
                {'id': 'mytable'},
                {'class': re.compile(r'table.*striped')},
                {'class': 'table'},
            ]
            
            for selector in selectors:
                table = soup.find('table', selector)
                if table:
                    break
            
            if not table:
                print(f"❌ Table not found on page {page_num}")
                return [], False
            
            print(f"📄 Processing page {page_num}...")
            
            # Extract rows
            rows = []
            tbody = table.find('tbody')
            if tbody:
                tr_elements = tbody.find_all('tr')
                
                for i, tr in enumerate(tr_elements):
                    cells = tr.find_all(['td', 'th'])
                    
                    if len(cells) < 5:
                        continue
                    
                    try:
                        row_data = {
                            'No': cells[0].get_text(strip=True),
                            'Nomor_Transaksi': cells[1].get_text(strip=True),
                            'Nomor_Dokumen': cells[2].get_text(strip=True),
                            'Tipe_Dokumen': cells[3].get_text(strip=True),
                            'Status_Dokumen': cells[4].get_text(strip=True),
                            'Page_Number': page_num,
                            'Row_Index': i + 1
                        }
                        
                        # Extract detail link
                        if len(cells) > 5:
                            detail_cell = cells[5]
                            detail_link = detail_cell.find('a', href=True)
                            if detail_link:
                                href = detail_link.get('href')
                                if href:
                                    row_data['Detail_Link'] = urljoin(self.base_url, href)
                                    # Extract ID from link
                                    id_match = re.search(r'/(\d+)/?$', href)
                                    if id_match:
                                        row_data['Document_ID'] = id_match.group(1)
                        
                        if not row_data.get('Detail_Link'):
                            row_data['Detail_Link'] = ''
                            row_data['Document_ID'] = ''
                        
                        # Skip empty rows
                        if any(row_data[key] for key in ['Nomor_Transaksi', 'Nomor_Dokumen']):
                            rows.append(row_data)
                            
                    except Exception as e:
                        print(f"⚠️ Error parsing row {i+1}: {e}")
                        continue
            
            print(f"✅ Found {len(rows)} valid rows on page {page_num}")
            
            # Check for next page
            has_next = self.has_next_page(soup, page_num)
            
            return rows, has_next
            
        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")
            return [], False
    
    def has_next_page(self, soup, current_page):
        """Check if there's a next page"""
        try:
            # Look for pagination controls
            pagination = soup.find(['ul', 'div'], class_=re.compile(r'pag', re.I))
            if pagination:
                # Look for Next button
                next_links = pagination.find_all('a', string=re.compile(r'next|selanjutnya|›|»', re.I))
                for link in next_links:
                    parent_classes = link.parent.get('class', [])
                    if 'disabled' not in ' '.join(parent_classes).lower():
                        return True
                
                # Look for page numbers higher than current
                page_links = pagination.find_all('a', href=True)
                for link in page_links:
                    text = link.get_text(strip=True)
                    if text.isdigit() and int(text) > current_page:
                        return True
            
            # Check "Showing X to Y of Z" text
            showing_pattern = re.compile(r'showing\s+(\d+)\s+to\s+(\d+)\s+of\s+(\d+)', re.I)
            showing_text = soup.find(string=showing_pattern)
            if showing_text:
                match = showing_pattern.search(showing_text)
                if match:
                    current_end = int(match.group(2))
                    total = int(match.group(3))
                    has_more = current_end < total
                    print(f"📊 Showing {match.group(1)} to {current_end} of {total} entries")
                    return has_more
            
            # Check if current page has full rows (indicating more might exist)
            table = soup.find('table', id='mytable')
            if table:
                tbody = table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')
                    if len(rows) >= 10:  # Full page usually means more pages
                        print(f"📄 Page {current_page} has {len(rows)} rows, checking for more...")
                        return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking next page: {e}")
            return False
    
    def scrape_all_documents(self, max_pages=100, delay=1.5):
        """Scrape all documents with progress tracking"""
        all_documents = []
        page = 1
        consecutive_empty = 0
        
        print(f"🚀 Starting scrape (max {max_pages} pages)...")
        
        while page <= max_pages and consecutive_empty < 3:
            print(f"\n--- Page {page} ---")
            
            rows, has_next = self.get_page_data(page)
            
            if rows:
                all_documents.extend(rows)
                consecutive_empty = 0
                print(f"✅ Page {page}: {len(rows)} documents (Total: {len(all_documents)})")
            else:
                consecutive_empty += 1
                print(f"⚠️ Page {page}: No data found (Empty count: {consecutive_empty})")
            
            # Stop if no more pages indicated
            if not has_next:
                print(f"🏁 No more pages after page {page}")
                break
            
            page += 1
            
            # Respectful delay
            time.sleep(delay)
        
        return all_documents
    
    def save_results(self, documents):
        """Save results to multiple formats"""
        if not documents:
            print("❌ No documents to save")
            return None
        
        # Create output directory
        output_dir = Path("kalbe_output")
        output_dir.mkdir(exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(documents)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to CSV
        csv_filename = output_dir / f'kalbe_documents_{timestamp}.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"💾 CSV saved: {csv_filename}")
        
        # Save to Excel
        try:
            excel_filename = output_dir / f'kalbe_documents_{timestamp}.xlsx'
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Documents')
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Total Documents', 'Total Pages Scraped', 'Unique Document Types', 'Date Scraped'],
                    'Value': [
                        len(documents),
                        df['Page_Number'].nunique() if 'Page_Number' in df.columns else 'N/A',
                        df['Tipe_Dokumen'].nunique() if 'Tipe_Dokumen' in df.columns else 'N/A',
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, index=False, sheet_name='Summary')
            
            print(f"📊 Excel saved: {excel_filename}")
        except Exception as e:
            print(f"⚠️ Excel save failed: {e}")
        
        # Display summary
        print(f"\n📈 SCRAPING SUMMARY")
        print("=" * 40)
        print(f"Total documents: {len(documents)}")
        print(f"Output directory: {output_dir.absolute()}")
        
        # Show document types
        if 'Tipe_Dokumen' in df.columns:
            print(f"\n📋 Document types:")
            doc_types = df['Tipe_Dokumen'].value_counts()
            for doc_type, count in doc_types.head(10).items():
                print(f"  {doc_type}: {count}")
        
        # Show status distribution
        if 'Status_Dokumen' in df.columns:
            print(f"\n📊 Status distribution:")
            status_dist = df['Status_Dokumen'].value_counts()
            for status, count in status_dist.items():
                print(f"  {status}: {count}")
        
        return df

def show_menu():
    """Show main menu"""
    print("\n" + "=" * 60)
    print("🏢 KALBE E-APPROVAL DOCUMENT SCRAPER")
    print("=" * 60)
    print("1. Start scraping with default settings")
    print("2. Configure settings and scrape")
    print("3. View current configuration")
    print("4. Exit")
    print("-" * 60)
    
    choice = input("Select option (1-4): ").strip()
    return choice

def configure_settings(scraper):
    """Configure scraping settings"""
    config = scraper.load_config()
    
    print("\n⚙️ CONFIGURATION")
    print("-" * 30)
    
    # Max pages
    current_max = config.get('max_pages', 100)
    print(f"Current max pages: {current_max}")
    new_max = input(f"Enter max pages to scrape (current: {current_max}): ").strip()
    if new_max.isdigit():
        config['max_pages'] = int(new_max)
    
    # Delay
    current_delay = config.get('delay_seconds', 1.5)
    print(f"Current delay between pages: {current_delay} seconds")
    new_delay = input(f"Enter delay in seconds (current: {current_delay}): ").strip()
    try:
        if new_delay:
            config['delay_seconds'] = float(new_delay)
    except ValueError:
        print("Invalid delay value, keeping current setting")
    
    scraper.save_config(config)
    return config

def main():
    """Main execution function with menu"""
    try:
        while True:
            choice = show_menu()
            
            if choice == '1':
                # Quick start
                scraper = KalbeApprovalScraper()
                
                if not scraper.test_connection():
                    print("❌ Cannot connect to Kalbe network.")
                    input("Press Enter to continue...")
                    continue
                
                username, password = scraper.get_credentials()
                
                if not scraper.login(username, password):
                    print("❌ Login failed.")
                    input("Press Enter to continue...")
                    continue
                
                config = scraper.load_config()
                documents = scraper.scrape_all_documents(
                    max_pages=config.get('max_pages', 100),
                    delay=config.get('delay_seconds', 1.5)
                )
                
                if documents:
                    scraper.save_results(documents)
                    print(f"\n🎉 SUCCESS: {len(documents)} documents scraped!")
                else:
                    print("\n❌ No documents were scraped.")
                
                input("Press Enter to continue...")
                
            elif choice == '2':
                # Configure and scrape
                scraper = KalbeApprovalScraper()
                config = configure_settings(scraper)
                
                if not scraper.test_connection():
                    print("❌ Cannot connect to Kalbe network.")
                    input("Press Enter to continue...")
                    continue
                
                username, password = scraper.get_credentials()
                
                if not scraper.login(username, password):
                    print("❌ Login failed.")
                    input("Press Enter to continue...")
                    continue
                
                documents = scraper.scrape_all_documents(
                    max_pages=config.get('max_pages', 100),
                    delay=config.get('delay_seconds', 1.5)
                )
                
                if documents:
                    scraper.save_results(documents)
                    print(f"\n🎉 SUCCESS: {len(documents)} documents scraped!")
                else:
                    print("\n❌ No documents were scraped.")
                
                input("Press Enter to continue...")
                
            elif choice == '3':
                # View configuration
                scraper = KalbeApprovalScraper()
                config = scraper.load_config()
                
                print("\n📋 CURRENT CONFIGURATION")
                print("-" * 40)
                print(f"Username: {config.get('username', 'Not set')}")
                print(f"Password: {'*' * len(config.get('password', '')) if config.get('password') else 'Not set'}")
                print(f"Max pages: {config.get('max_pages', 100)}")
                print(f"Delay (seconds): {config.get('delay_seconds', 1.5)}")
                
                input("Press Enter to continue...")
                
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                input("Press Enter to continue...")
                
    except KeyboardInterrupt:
        print("\n\n❌ Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    # Set working directory to script location for EXE compatibility
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        os.chdir(os.path.dirname(sys.executable))
    else:
        # Running in normal Python environment
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    main()