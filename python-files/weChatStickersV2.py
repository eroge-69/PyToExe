#!/usr/bin/env python3
"""
Advanced WeChat Sticker Exporter for macOS and Windows
Supports multiple WeChat installations, encrypted data parsing, and comprehensive error recovery
"""

import os
import sys
import re
import time
import tempfile
import shutil
import subprocess
import platform
import logging
import json
import sqlite3
import hashlib
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import glob
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

# For HTTP requests with retry
import urllib.request
import urllib.error
import socket
import ssl

# Windows-specific imports
if platform.system() == 'Windows':
    import winreg
    import win32api
    import win32con
    import win32security
    import ctypes
    from ctypes import wintypes

# Configure advanced logging with colors and file output
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if platform.system() != 'Windows' or 'ANSICON' in os.environ:
            log_color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler with colors
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = ColoredFormatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler for detailed logs
log_file = 'wechat_sticker_exporter.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

class StickerType(Enum):
    """Sticker file types"""
    CUSTOM = "custom"
    FAVORITE = "favorite"
    DOWNLOADED = "downloaded"
    EMOJI = "emoji"

@dataclass
class WeChatAccount:
    """Represents a WeChat account found on the system"""
    account_id: str
    nickname: str = ""
    wechat_id: str = ""
    data_path: str = ""
    avatar_path: str = ""
    last_active: Optional[datetime] = None
    
@dataclass
class Sticker:
    """Enhanced sticker class with more metadata"""
    id: str
    url: str = ""
    local_path: str = ""
    encrypted_path: str = ""
    downloaded_path: str = ""
    mtime: float = 0
    size: int = 0
    md5: str = ""
    type: StickerType = StickerType.CUSTOM
    account: Optional[WeChatAccount] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Sticker):
            return self.id == other.id
        return False

class WeChatDataParser:
    """Advanced parser for WeChat data files"""
    
    # WeChat magic bytes for different file types
    MAGIC_BYTES = {
        b'\x89PNG': '.png',
        b'GIF8': '.gif',
        b'\xFF\xD8\xFF': '.jpg',
        b'RIFF': '.webp',
        b'BM': '.bmp',
    }
    
    # XOR keys commonly used by WeChat for simple encryption
    XOR_KEYS = [0x51, 0x5A, 0x5D, 0x63, 0x66, 0x69, 0x6C, 0x72, 0x75, 0x78, 0x7B, 0x81]
    
    @staticmethod
    def detect_file_type(data: bytes, try_decrypt: bool = True) -> Tuple[str, bytes]:
        """Detect file type and optionally decrypt data"""
        if len(data) < 16:
            return '.dat', data
            
        # Check if already a known format
        for magic, ext in WeChatDataParser.MAGIC_BYTES.items():
            if data.startswith(magic):
                return ext, data
        
        # Try XOR decryption if enabled
        if try_decrypt:
            for key in WeChatDataParser.XOR_KEYS:
                decrypted = bytes([b ^ key for b in data[:1024]])  # Check first 1KB
                for magic, ext in WeChatDataParser.MAGIC_BYTES.items():
                    if decrypted.startswith(magic):
                        # Decrypt full data
                        return ext, bytes([b ^ key for b in data])
        
        return '.dat', data
    
    @staticmethod
    def parse_db_file(db_path: str) -> List[Dict[str, Any]]:
        """Parse WeChat SQLite database files"""
        results = []
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                if 'emoji' in table_name.lower() or 'sticker' in table_name.lower():
                    try:
                        cursor.execute(f"SELECT * FROM {table_name}")
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            record = dict(zip(columns, row))
                            results.append({
                                'table': table_name,
                                'data': record
                            })
                    except Exception as e:
                        logger.debug(f"Error reading table {table_name}: {e}")
            
            conn.close()
        except Exception as e:
            logger.debug(f"Error parsing DB file {db_path}: {e}")
        
        return results

class WindowsWeChatLocator:
    """Advanced WeChat locator for Windows systems"""
    
    def __init__(self):
        self.wechat_paths = []
        self.accounts = []
        
    def find_wechat_installations(self) -> List[str]:
        """Find all WeChat installations on Windows"""
        installations = set()
        
        # Method 1: Check registry
        try:
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\WeChat"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tencent\WeChat"),
            ]
            
            for hkey, path in registry_paths:
                try:
                    with winreg.OpenKey(hkey, path) as key:
                        # Try to get installation path
                        for value_name in ["InstallPath", "Path", "FileSavePath"]:
                            try:
                                value, _ = winreg.QueryValueEx(key, value_name)
                                if value and os.path.exists(value):
                                    installations.add(value)
                                    logger.info(f"Found WeChat in registry: {value}")
                            except WindowsError:
                                continue
                except WindowsError:
                    continue
        except Exception as e:
            logger.debug(f"Registry search error: {e}")
        
        # Method 2: Check common installation directories
        common_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Tencent', 'WeChat'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Tencent', 'WeChat'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Tencent', 'WeChat'),
            os.path.join(os.environ.get('APPDATA', ''), 'Tencent', 'WeChat'),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                installations.add(path)
                logger.info(f"Found WeChat in common path: {path}")
        
        # Method 3: Search for WeChat.exe in Program Files
        for drive in ['C:', 'D:', 'E:']:
            if os.path.exists(drive):
                patterns = [
                    f"{drive}\\*\\Tencent\\WeChat",
                    f"{drive}\\*\\WeChat",
                    f"{drive}\\Program Files*\\Tencent\\WeChat",
                ]
                for pattern in patterns:
                    for path in glob.glob(pattern):
                        if os.path.exists(os.path.join(path, 'WeChat.exe')):
                            installations.add(path)
                            logger.info(f"Found WeChat via search: {path}")
        
        return list(installations)
    
    def find_wechat_data_directories(self) -> List[str]:
        """Find WeChat data directories containing user data"""
        data_dirs = set()
        
        # Method 1: Documents folder
        documents = os.path.expanduser('~\\Documents')
        wechat_files = os.path.join(documents, 'WeChat Files')
        if os.path.exists(wechat_files):
            data_dirs.add(wechat_files)
            logger.info(f"Found WeChat Files in Documents: {wechat_files}")
        
        # Method 2: Check for redirected Documents folder
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            docs_folder = shell.SpecialFolders("MyDocuments")
            wechat_files = os.path.join(docs_folder, 'WeChat Files')
            if os.path.exists(wechat_files):
                data_dirs.add(wechat_files)
        except:
            pass
        
        # Method 3: Search in user profile
        user_profile = os.environ.get('USERPROFILE', '')
        if user_profile:
            patterns = [
                os.path.join(user_profile, '*', 'WeChat Files'),
                os.path.join(user_profile, 'WeChat Files'),
            ]
            for pattern in patterns:
                for path in glob.glob(pattern):
                    if os.path.exists(path):
                        data_dirs.add(path)
                        logger.info(f"Found WeChat data: {path}")
        
        # Method 4: Check AppData locations
        appdata_paths = [
            os.environ.get('APPDATA', ''),
            os.environ.get('LOCALAPPDATA', ''),
        ]
        
        for appdata in appdata_paths:
            if appdata:
                wechat_path = os.path.join(appdata, 'Tencent', 'WeChat')
                if os.path.exists(wechat_path):
                    # Look for user data
                    user_data = os.path.join(wechat_path, 'Users')
                    if os.path.exists(user_data):
                        data_dirs.add(user_data)
                        logger.info(f"Found WeChat user data: {user_data}")
        
        return list(data_dirs)
    
    def parse_wechat_accounts(self, data_dir: str) -> List[WeChatAccount]:
        """Parse WeChat accounts from a data directory"""
        accounts = []
        
        # Look for account folders (typically named wxid_* or custom names)
        try:
            for entry in os.listdir(data_dir):
                entry_path = os.path.join(data_dir, entry)
                if os.path.isdir(entry_path):
                    # Skip special folders
                    if entry in ['All Users', 'Applet', 'WMPF']:
                        continue
                    
                    # Check if it's an account folder
                    account_markers = [
                        'FileStorage',
                        'CustomEmotion',
                        'Msg',
                        'config',
                    ]
                    
                    is_account = any(
                        os.path.exists(os.path.join(entry_path, marker))
                        for marker in account_markers
                    )
                    
                    if is_account:
                        account = WeChatAccount(
                            account_id=entry,
                            data_path=entry_path
                        )
                        
                        # Try to get account info from config
                        config_path = os.path.join(entry_path, 'config', 'AccInfo.dat')
                        if os.path.exists(config_path):
                            try:
                                with open(config_path, 'rb') as f:
                                    data = f.read()
                                    # Parse account info (simplified - actual format is complex)
                                    account.nickname = self._extract_nickname(data)
                            except:
                                pass
                        
                        # Get last active time
                        try:
                            mtime = os.path.getmtime(entry_path)
                            account.last_active = datetime.fromtimestamp(mtime)
                        except:
                            pass
                        
                        accounts.append(account)
                        logger.info(f"Found WeChat account: {account.account_id}")
        except Exception as e:
            logger.error(f"Error parsing accounts in {data_dir}: {e}")
        
        return accounts
    
    def _extract_nickname(self, data: bytes) -> str:
        """Extract nickname from account data (simplified)"""
        # This is a simplified extraction - actual format is more complex
        try:
            # Look for UTF-8 strings
            text = data.decode('utf-8', errors='ignore')
            # Extract readable strings
            import string
            printable = set(string.printable)
            text = ''.join(filter(lambda x: x in printable, text))
            # Return first word-like string
            words = re.findall(r'\b\w+\b', text)
            if words:
                return words[0]
        except:
            pass
        return ""

class MacOSWeChatLocator:
    """WeChat locator for macOS systems"""
    
    def find_wechat_data(self) -> List[Tuple[str, str]]:
        """Find WeChat data on macOS"""
        results = []
        home = Path.home()
        
        # Standard WeChat paths on macOS
        patterns = [
            home / "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/*/*/Stickers",
            home / "Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/*/Stickers",
        ]
        
        for pattern in patterns:
            for path in glob.glob(str(pattern)):
                if os.path.exists(path):
                    fav_archive = os.path.join(path, 'fav.archive')
                    if os.path.exists(fav_archive):
                        results.append((fav_archive, path))
                        logger.info(f"Found WeChat stickers: {path}")
        
        return results

class AdvancedStickerExtractor:
    """Advanced sticker extraction with multiple methods"""
    
    def __init__(self, system: str):
        self.system = system
        self.parser = WeChatDataParser()
        
    def extract_from_windows_account(self, account: WeChatAccount) -> List[Sticker]:
        """Extract stickers from a Windows WeChat account"""
        stickers = []
        
        # Method 1: CustomEmotion folder
        custom_emotion_path = os.path.join(account.data_path, 'FileStorage', 'CustomEmotion')
        if os.path.exists(custom_emotion_path):
            stickers.extend(self._extract_from_custom_emotion(custom_emotion_path, account))
        
        # Method 2: FavTemp folder
        fav_temp_path = os.path.join(account.data_path, 'FileStorage', 'FavTemp')
        if os.path.exists(fav_temp_path):
            stickers.extend(self._extract_from_fav_temp(fav_temp_path, account))
        
        # Method 3: Parse emotion database
        db_paths = [
            os.path.join(account.data_path, 'Msg', 'Emotion.db'),
            os.path.join(account.data_path, 'CustomEmotions.db'),
        ]
        
        for db_path in db_paths:
            if os.path.exists(db_path):
                stickers.extend(self._extract_from_database(db_path, account))
        
        # Method 4: Search for image cache
        cache_paths = [
            os.path.join(account.data_path, 'FileStorage', 'Cache'),
            os.path.join(account.data_path, 'FileStorage', 'Image'),
        ]
        
        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                stickers.extend(self._extract_from_cache(cache_path, account))
        
        return stickers
    
    def _extract_from_custom_emotion(self, emotion_path: str, account: WeChatAccount) -> List[Sticker]:
        """Extract stickers from CustomEmotion folder"""
        stickers = []
        
        try:
            for root, dirs, files in os.walk(emotion_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Skip small files (likely not images)
                    if os.path.getsize(file_path) < 1024:  # Less than 1KB
                        continue
                    
                    # Generate sticker ID from file
                    sticker_id = os.path.splitext(file)[0]
                    if not sticker_id:
                        sticker_id = hashlib.md5(file.encode()).hexdigest()
                    
                    sticker = Sticker(
                        id=sticker_id,
                        local_path=file_path,
                        type=StickerType.CUSTOM,
                        account=account,
                        mtime=os.path.getmtime(file_path),
                        size=os.path.getsize(file_path)
                    )
                    
                    # Try to read and detect actual file type
                    try:
                        with open(file_path, 'rb') as f:
                            data = f.read(1024)
                            ext, _ = self.parser.detect_file_type(data, try_decrypt=True)
                            sticker.metadata['detected_type'] = ext
                    except:
                        pass
                    
                    stickers.append(sticker)
                    logger.debug(f"Found custom emotion: {file}")
                    
        except Exception as e:
            logger.error(f"Error extracting from CustomEmotion: {e}")
        
        return stickers
    
    def _extract_from_fav_temp(self, fav_path: str, account: WeChatAccount) -> List[Sticker]:
        """Extract stickers from FavTemp folder"""
        stickers = []
        
        try:
            for file in os.listdir(fav_path):
                if file.lower().endswith(('.gif', '.png', '.jpg', '.jpeg', '.webp')):
                    file_path = os.path.join(fav_path, file)
                    
                    sticker_id = os.path.splitext(file)[0]
                    sticker = Sticker(
                        id=sticker_id,
                        local_path=file_path,
                        type=StickerType.FAVORITE,
                        account=account,
                        mtime=os.path.getmtime(file_path),
                        size=os.path.getsize(file_path)
                    )
                    
                    stickers.append(sticker)
                    logger.debug(f"Found favorite: {file}")
                    
        except Exception as e:
            logger.error(f"Error extracting from FavTemp: {e}")
        
        return stickers
    
    def _extract_from_database(self, db_path: str, account: WeChatAccount) -> List[Sticker]:
        """Extract sticker info from database"""
        stickers = []
        
        try:
            records = self.parser.parse_db_file(db_path)
            
            for record in records:
                data = record['data']
                
                # Look for URL and MD5 fields
                url = None
                md5 = None
                
                for key, value in data.items():
                    if value and isinstance(value, str):
                        if value.startswith('http'):
                            url = value
                        elif len(value) == 32 and all(c in '0123456789abcdef' for c in value.lower()):
                            md5 = value
                
                if url or md5:
                    sticker_id = md5 or hashlib.md5(url.encode()).hexdigest()
                    sticker = Sticker(
                        id=sticker_id,
                        url=url or "",
                        md5=md5 or "",
                        type=StickerType.EMOJI,
                        account=account,
                        metadata={'db_record': data}
                    )
                    stickers.append(sticker)
                    
        except Exception as e:
            logger.debug(f"Error extracting from database: {e}")
        
        return stickers
    
    def _extract_from_cache(self, cache_path: str, account: WeChatAccount) -> List[Sticker]:
        """Extract stickers from cache folders"""
        stickers = []
        
        try:
            for root, dirs, files in os.walk(cache_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if it might be an image
                    try:
                        with open(file_path, 'rb') as f:
                            header = f.read(16)
                            
                        # Check for image signatures (including encrypted)
                        is_image = False
                        for magic in self.parser.MAGIC_BYTES.keys():
                            if header.startswith(magic):
                                is_image = True
                                break
                        
                        # Try XOR decryption check
                        if not is_image:
                            for key in self.parser.XOR_KEYS:
                                decrypted = bytes([b ^ key for b in header])
                                for magic in self.parser.MAGIC_BYTES.keys():
                                    if decrypted.startswith(magic):
                                        is_image = True
                                        break
                        
                        if is_image and os.path.getsize(file_path) > 1024:
                            sticker_id = os.path.splitext(file)[0]
                            sticker = Sticker(
                                id=sticker_id,
                                local_path=file_path,
                                encrypted_path=file_path,
                                type=StickerType.DOWNLOADED,
                                account=account,
                                mtime=os.path.getmtime(file_path),
                                size=os.path.getsize(file_path)
                            )
                            stickers.append(sticker)
                            
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.debug(f"Error extracting from cache: {e}")
        
        return stickers
    
    def extract_from_macos_archive(self, archive_path: str, sticker_dir: str) -> List[Sticker]:
        """Extract stickers from macOS fav.archive"""
        stickers = []
        
        try:
            # Convert plist to XML
            result = subprocess.run(
                ["plutil", "-convert", "xml1", "-o", "-", archive_path],
                capture_output=True,
                check=True,
                timeout=10
            )
            
            root = ET.fromstring(result.stdout)
            strings = root.findall(".//array/string")
            
            id_pattern = re.compile(r'^[0-9a-f]+$')
            url_pattern = re.compile(r'^https?://')
            
            persistence_dir = os.path.join(os.path.dirname(sticker_dir), "Persistence")
            
            for i, elem in enumerate(strings):
                text = elem.text or ""
                
                if url_pattern.match(text):
                    if i > 0:
                        prev_text = strings[i-1].text or ""
                        if id_pattern.match(prev_text):
                            sticker_id = prev_text
                            url = text
                            
                            encrypted_path = os.path.join(persistence_dir, sticker_id)
                            mtime = 0
                            if os.path.exists(encrypted_path):
                                mtime = os.path.getmtime(encrypted_path)
                            
                            sticker = Sticker(
                                id=sticker_id,
                                url=url,
                                encrypted_path=encrypted_path,
                                type=StickerType.FAVORITE,
                                mtime=mtime
                            )
                            stickers.append(sticker)
                            
        except Exception as e:
            logger.error(f"Error extracting from macOS archive: {e}")
        
        return stickers

class AdvancedDownloader:
    """Advanced downloader with parallel downloads and resume support"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
    def download_stickers(self, stickers: List[Sticker], output_dir: str) -> Tuple[List[Sticker], List[Sticker]]:
        """Download multiple stickers in parallel"""
        successful = []
        failed = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_sticker = {
                executor.submit(self._download_single, sticker, output_dir): sticker
                for sticker in stickers
            }
            
            total = len(stickers)
            completed = 0
            
            for future in as_completed(future_to_sticker):
                sticker = future_to_sticker[future]
                completed += 1
                
                try:
                    result = future.result()
                    if result:
                        successful.append(sticker)
                        print(f"[{completed}/{total}] ✓ Downloaded: {sticker.id}")
                    else:
                        failed.append(sticker)
                        print(f"[{completed}/{total}] ✗ Failed: {sticker.id}")
                except Exception as e:
                    failed.append(sticker)
                    logger.error(f"Download exception for {sticker.id}: {e}")
                    print(f"[{completed}/{total}] ✗ Error: {sticker.id}")
        
        return successful, failed
    
    def _download_single(self, sticker: Sticker, output_dir: str) -> bool:
        """Download a single sticker with advanced error handling"""
        try:
            # If local file exists, try to decrypt/copy it
            if sticker.local_path and os.path.exists(sticker.local_path):
                return self._process_local_file(sticker, output_dir)
            
            # If URL exists, download it
            if sticker.url:
                return self._download_from_url(sticker, output_dir)
            
            logger.warning(f"Sticker {sticker.id} has no valid source")
            return False
            
        except Exception as e:
            logger.error(f"Error downloading sticker {sticker.id}: {e}")
            return False
    
    def _process_local_file(self, sticker: Sticker, output_dir: str) -> bool:
        """Process a local sticker file (decrypt if needed)"""
        try:
            with open(sticker.local_path, 'rb') as f:
                data = f.read()
            
            # Detect and decrypt if needed
            ext, decrypted_data = WeChatDataParser.detect_file_type(data, try_decrypt=True)
            
            # Generate output filename
            output_file = os.path.join(output_dir, f"{sticker.id}{ext}")
            
            # Write to file
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
            
            # Preserve timestamp
            if sticker.mtime > 0:
                os.utime(output_file, (sticker.mtime, sticker.mtime))
            
            sticker.downloaded_path = output_file
            logger.info(f"Processed local file: {sticker.id} -> {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing local file {sticker.local_path}: {e}")
            return False
    
    def _download_from_url(self, sticker: Sticker, output_dir: str, max_retries: int = 3) -> bool:
        """Download sticker from URL with retry logic"""
        for attempt in range(max_retries):
            try:
                # Create request
                req = urllib.request.Request(sticker.url, headers=self.session_headers)
                
                # SSL context
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                # Download with timeout
                with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
                    if response.status != 200:
                        raise urllib.error.HTTPError(
                            sticker.url, response.status, 
                            f"HTTP {response.status}", {}, None
                        )
                    
                    data = response.read()
                
                # Detect file type
                ext, _ = WeChatDataParser.detect_file_type(data, try_decrypt=False)
                
                # Save file
                output_file = os.path.join(output_dir, f"{sticker.id}{ext}")
                
                with open(output_file, 'wb') as f:
                    f.write(data)
                
                # Set timestamp
                if sticker.mtime > 0:
                    os.utime(output_file, (sticker.mtime, sticker.mtime))
                
                sticker.downloaded_path = output_file
                logger.info(f"Downloaded from URL: {sticker.id} -> {output_file}")
                return True
                
            except Exception as e:
                logger.warning(f"Download attempt {attempt + 1} failed for {sticker.url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        return False

class WeChatStickerExporter:
    """Main application class with advanced features"""
    
    def __init__(self):
        self.system = platform.system()
        self.root_dir = self._get_root_dir()
        self.data_dir = os.path.join(self.root_dir, "WeChat_Stickers_Export")
        self._ensure_data_dir()
        
        # Initialize components
        self.downloader = AdvancedDownloader(max_workers=5)
        self.extractor = AdvancedStickerExtractor(self.system)
        
        # Statistics
        self.stats = {
            'accounts_found': 0,
            'stickers_found': 0,
            'stickers_downloaded': 0,
            'stickers_failed': 0,
            'stickers_skipped': 0,
            'start_time': time.time(),
        }
        
        logger.info(f"="*60)
        logger.info(f"WeChat Sticker Exporter - Advanced Edition")
        logger.info(f"System: {self.system}")
        logger.info(f"Export Directory: {self.data_dir}")
        logger.info(f"="*60)
    
    def _get_root_dir(self) -> str:
        """Get the root directory for the application"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))
    
    def _ensure_data_dir(self):
        """Ensure export directory exists with subdirectories"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Create subdirectories for organization
            subdirs = ['custom', 'favorites', 'downloaded', 'emoji']
            for subdir in subdirs:
                os.makedirs(os.path.join(self.data_dir, subdir), exist_ok=True)
                
        except Exception as e:
            logger.error(f"Failed to create export directory: {e}")
            sys.exit(1)
    
    def get_existing_stickers(self) -> Set[str]:
        """Get set of already exported sticker IDs"""
        existing = set()
        
        try:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    # Extract ID from filename
                    name = os.path.splitext(file)[0]
                    if name:
                        existing.add(name)
                        
        except Exception as e:
            logger.error(f"Error scanning existing stickers: {e}")
        
        return existing
    
    def find_all_stickers(self) -> List[Sticker]:
        """Find all stickers on the system"""
        all_stickers = []
        
        if self.system == "Windows":
            logger.info("Searching for WeChat installations on Windows...")
            
            locator = WindowsWeChatLocator()
            
            # Find installations
            installations = locator.find_wechat_installations()
            logger.info(f"Found {len(installations)} WeChat installation(s)")
            
            # Find data directories
            data_dirs = locator.find_wechat_data_directories()
            logger.info(f"Found {len(data_dirs)} WeChat data directory(ies)")
            
            # Parse accounts from each data directory
            all_accounts = []
            for data_dir in data_dirs:
                accounts = locator.parse_wechat_accounts(data_dir)
                all_accounts.extend(accounts)
            
            self.stats['accounts_found'] = len(all_accounts)
            logger.info(f"Found {len(all_accounts)} WeChat account(s)")
            
            # Extract stickers from each account
            for account in all_accounts:
                logger.info(f"Processing account: {account.account_id}")
                stickers = self.extractor.extract_from_windows_account(account)
                all_stickers.extend(stickers)
                logger.info(f"  Found {len(stickers)} stickers")
        
        elif self.system == "Darwin":  # macOS
            logger.info("Searching for WeChat data on macOS...")
            
            locator = MacOSWeChatLocator()
            wechat_data = locator.find_wechat_data()
            
            for archive_path, sticker_dir in wechat_data:
                stickers = self.extractor.extract_from_macos_archive(archive_path, sticker_dir)
                all_stickers.extend(stickers)
                logger.info(f"Found {len(stickers)} stickers in {archive_path}")
        
        else:
            logger.error(f"Unsupported system: {self.system}")
        
        # Remove duplicates
        unique_stickers = list({s.id: s for s in all_stickers}.values())
        self.stats['stickers_found'] = len(unique_stickers)
        
        return unique_stickers
    
    def organize_stickers(self, stickers: List[Sticker]) -> Dict[str, List[Sticker]]:
        """Organize stickers by type"""
        organized = {
            'custom': [],
            'favorites': [],
            'downloaded': [],
            'emoji': [],
        }
        
        for sticker in stickers:
            if sticker.type == StickerType.CUSTOM:
                organized['custom'].append(sticker)
            elif sticker.type == StickerType.FAVORITE:
                organized['favorites'].append(sticker)
            elif sticker.type == StickerType.DOWNLOADED:
                organized['downloaded'].append(sticker)
            elif sticker.type == StickerType.EMOJI:
                organized['emoji'].append(sticker)
        
        return organized
    
    def export_stickers(self, stickers: List[Sticker]):
        """Export stickers with organization"""
        existing = self.get_existing_stickers()
        logger.info(f"Found {len(existing)} existing exported stickers")
        
        # Filter out existing stickers
        new_stickers = [s for s in stickers if s.id not in existing]
        self.stats['stickers_skipped'] = len(stickers) - len(new_stickers)
        
        if not new_stickers:
            logger.info("No new stickers to export")
            return
        
        logger.info(f"Exporting {len(new_stickers)} new stickers...")
        
        # Organize by type
        organized = self.organize_stickers(new_stickers)
        
        all_successful = []
        all_failed = []
        
        for sticker_type, sticker_list in organized.items():
            if not sticker_list:
                continue
            
            output_dir = os.path.join(self.data_dir, sticker_type)
            logger.info(f"\nExporting {len(sticker_list)} {sticker_type} stickers...")
            
            successful, failed = self.downloader.download_stickers(sticker_list, output_dir)
            all_successful.extend(successful)
            all_failed.extend(failed)
        
        self.stats['stickers_downloaded'] = len(all_successful)
        self.stats['stickers_failed'] = len(all_failed)
    
    def generate_report(self):
        """Generate and save export report"""
        elapsed = time.time() - self.stats['start_time']
        
        report = f"""
╔════════════════════════════════════════════════════════════╗
║          WeChat Sticker Export Report                      ║
╠════════════════════════════════════════════════════════════╣
║ System:             {self.system:38} ║
║ Export Directory:   {os.path.basename(self.data_dir):38} ║
║ Execution Time:     {f"{elapsed:.2f} seconds":38} ║
╠════════════════════════════════════════════════════════════╣
║ Accounts Found:     {self.stats['accounts_found']:38} ║
║ Stickers Found:     {self.stats['stickers_found']:38} ║
║ Stickers Skipped:   {self.stats['stickers_skipped']:38} ║
║ Stickers Downloaded:{self.stats['stickers_downloaded']:38} ║
║ Stickers Failed:    {self.stats['stickers_failed']:38} ║
╚════════════════════════════════════════════════════════════╝
        """
        
        print(report)
        
        # Save report to file
        report_file = os.path.join(self.data_dir, 'export_report.txt')
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
                f.write(f"\n\nExport completed at: {datetime.now()}\n")
            logger.info(f"Report saved to: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def run(self):
        """Main execution flow"""
        try:
            # Find all stickers
            stickers = self.find_all_stickers()
            
            if not stickers:
                logger.warning("No stickers found on this system")
                print("\n⚠ No WeChat stickers found. Please ensure WeChat is installed and has been used.")
                return
            
            # Export stickers
            self.export_stickers(stickers)
            
            # Generate report
            self.generate_report()
            
            # Open export directory
            if self.stats['stickers_downloaded'] > 0:
                try:
                    if self.system == "Windows":
                        os.startfile(self.data_dir)
                    elif self.system == "Darwin":
                        subprocess.run(["open", self.data_dir])
                except:
                    pass
            
        except KeyboardInterrupt:
            logger.info("Export interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Critical error: {e}", exc_info=True)
            sys.exit(1)

def main():
    """Entry point"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     WeChat Sticker Exporter - Advanced Edition            ║")
    print("║     Version 2.0 - Full Windows & macOS Support            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    exporter = WeChatStickerExporter()
    exporter.run()
    
    print("\n✓ Export complete! Press Enter to exit...")
    input()

if __name__ == "__main__":
    main()