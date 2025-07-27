import ctypes
import sys
import os
import subprocess
import re
import random
import urllib.request
import zipfile
import string
import shutil
import winreg
import platform
import uuid
import socket
import psutil
import random
import re
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# API Configuration
API_URL = "https://lime342.pythonanywhere.com/validate_key"

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

def load_settings():
    """Load settings from settings.json"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
    return {}

def save_settings(settings):
    """Save settings to settings.json"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def save_license_key(key):
    """Save license key to settings"""
    settings = load_settings()
    settings['license_key'] = key
    return save_settings(settings)

def get_saved_license_key():
    """Get saved license key from settings"""
    settings = load_settings()
    return settings.get('license_key', '')

def save_windows_version(version):
    """Save selected Windows version to settings"""
    settings = load_settings()
    settings['windows_version'] = version
    return save_settings(settings)

def get_saved_windows_version():
    """Get saved Windows version from settings"""
    settings = load_settings()
    return settings.get('windows_version', 'auto')

def detect_windows_version():
    """Detect Windows version automatically"""
    try:
        version = platform.version()
        build = int(version.split('.')[-1])
        
        # Windows 11 starts from build 22000
        if build >= 22000:
            return "11"
        else:
            return "10"
    except:
        return "10"  # Default fallback

print(r"    __  ______  _____ _   __   ________                               ")
print(r"   / / / / __ \/ ___// | / /  / ____/ /_  ____ _____  ____ ____  _____")
print(r"  / /_/ / / / /\__ \/  |/ /  / /   / __ \/ __ `/ __ \/ __ `/ _ \/ ___/")
print(r" / __  / /_/ /___/ / /|  /  / /___/ / / / /_/ / / / / /_/ /  __/ /    ")
print(r"/_/ /_/_____//____/_/ |_/   \____/_/ /_/\__,_/_/ /_/\__, /\___/_/     ")
print(r"                                                   /____/             ")
print("Hard Disk Serial Number Changer + PC Name Changer + Rockstar Cleaner")
print("Made by Lime   Youtube: https://www.youtube.com/@limekanacke")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

def get_hwid():
    """Get system HWID"""
    try:
        # Method 1: Using wmic
        result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and line.upper() != 'UUID':
                    return line
        
        # Method 2: Using registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ)
            hwid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            return hwid
        except:
            pass
            
        return "Unable to retrieve HWID"
    except Exception as e:
        return f"Error: {str(e)}"

def get_pc_name():
    """Get current PC name"""
    try:
        return platform.node()
    except:
        return "Unable to retrieve PC Name"

def download_volumeid(dest_folder):
    volumeid_exe_path = os.path.join(dest_folder, "volumeid.exe")

    if os.path.exists(volumeid_exe_path):
        return True

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    else:
        for f in os.listdir(dest_folder):
            path = os.path.join(dest_folder, f)
            if os.path.isfile(path) and f.lower() != "volumeid.exe":
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")

    url = "https://download.sysinternals.com/files/VolumeId.zip"
    zip_path = os.path.join(dest_folder, "VolumeID.zip")

    print("Downloading VolumeID...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/zip,application/octet-stream'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response, open(zip_path, 'wb') as out_file:
            file_size = int(response.headers['Content-Length'])
            print(f"File size: {file_size/1024:.1f} KB")
            downloaded = 0
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                downloaded += len(chunk)
                out_file.write(chunk)
                percent = int(downloaded * 100 / file_size)
                print(f"\rDownloading: {percent}%", end='', flush=True)
        print("\nDownload complete!")
    except Exception as e:
        print(f"Download failed: {e}")
        return False

    print("Extracting files...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder)
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

    try:
        os.remove(zip_path)
    except:
        pass

    if os.path.exists(volumeid_exe_path):
        print("Download and extraction complete.")
        return True
    else:
        print("volumeid.exe not found after extraction.")
        return False

def get_current_volume_id(drive_letter):
    try:
        output = subprocess.check_output(f"vol {drive_letter}:", shell=True, text=True)
        match = re.search(r"(Volume Serial Number|Volumeseriennummer|Seriennummer des Volumes)\s*[:is]*\s*([\w-]+)", output)
        if match:
            return match.group(2)
    except subprocess.CalledProcessError:
        pass
    return None

def generate_random_volume_id():
    return f"{random.randint(0, 0xFFFF):04X}-{random.randint(0, 0xFFFF):04X}"

def change_volume_id(volumeid_path, drive_letter, new_id):
    cmd = f'"{volumeid_path}" {drive_letter}: {new_id}'
    print(f"Executing: {cmd}")
    result = os.system(cmd)
    return result == 0

def list_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        if os.path.exists(f"{letter}:\\"):
            drives.append(letter)
    return drives

def generate_random_computer_name():
    return "DESKTOP-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def change_computer_name_win10(new_name):
    """Windows 10 method for changing computer name"""
    try:
        # Method 1: Registry approach (Windows 10)
        registry_paths = [
            r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName",
            r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName"
        ]
        
        for path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "ComputerName", 0, winreg.REG_SZ, new_name)
                winreg.CloseKey(key)
                print(f"Updated registry path: {path}")
            except Exception as e:
                print(f"Failed to update registry path {path}: {e}")
                return False
        
        # Method 2: WMIC command
        try:
            result = subprocess.run(['wmic', 'computersystem', 'where', f'name="{platform.node()}"', 
                                   'call', 'rename', f'name="{new_name}"'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("WMIC command executed successfully")
            else:
                print(f"WMIC command failed: {result.stderr}")
        except Exception as e:
            print(f"WMIC command error: {e}")
        
        print(f"Computer name changed to {new_name} (Windows 10 method)")
        return True
        
    except Exception as e:
        print(f"Failed to change computer name (Windows 10): {e}")
        return False

def change_computer_name_win11(new_name):
    """Windows 11 method for changing computer name"""
    try:
        # Method 1: PowerShell Rename-Computer (Windows 11)
        try:
            powershell_cmd = f'powershell.exe -Command "Rename-Computer -NewName \'{new_name}\' -Force"'
            result = subprocess.run(powershell_cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("PowerShell Rename-Computer executed successfully")
            else:
                print(f"PowerShell command failed: {result.stderr}")
                # Fall back to alternative methods
        except Exception as e:
            print(f"PowerShell command error: {e}")
        
        # Method 2: Registry approach with additional Windows 11 specific keys
        registry_paths = [
            r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName",
            r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName",
            r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"  # Additional for Windows 11
        ]
        
        for path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_SET_VALUE)
                if "Tcpip" in path:
                    # For the Tcpip path, use different value names
                    winreg.SetValueEx(key, "Hostname", 0, winreg.REG_SZ, new_name)
                    winreg.SetValueEx(key, "NV Hostname", 0, winreg.REG_SZ, new_name)
                else:
                    winreg.SetValueEx(key, "ComputerName", 0, winreg.REG_SZ, new_name)
                winreg.CloseKey(key)
                print(f"Updated registry path: {path}")
            except Exception as e:
                print(f"Failed to update registry path {path}: {e}")
        
        # Method 3: NETDOM command (if available)
        try:
            netdom_cmd = f'netdom renamecomputer {platform.node()} /newname:{new_name} /force'
            result = subprocess.run(netdom_cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("NETDOM command executed successfully")
            else:
                print(f"NETDOM command not available or failed: {result.stderr}")
        except Exception as e:
            print(f"NETDOM command error: {e}")
        
        # Method 4: Alternative PowerShell method
        try:
            alt_powershell_cmd = f'powershell.exe -Command "$computer = Get-WmiObject -Class Win32_ComputerSystem; $computer.Rename(\'{new_name}\')"'
            result = subprocess.run(alt_powershell_cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                print("Alternative PowerShell method executed successfully")
        except Exception as e:
            print(f"Alternative PowerShell method error: {e}")
        
        print(f"Computer name changed to {new_name} (Windows 11 method)")
        return True
        
    except Exception as e:
        print(f"Failed to change computer name (Windows 11): {e}")
        return False

def change_computer_name(new_name, windows_version="auto"):
    """Change computer name based on Windows version"""
    if windows_version == "auto":
        detected_version = detect_windows_version()
        print(f"Auto-detected Windows version: {detected_version}")
        windows_version = detected_version
    
    print(f"Using Windows {windows_version} method for PC name change")
    
    if windows_version == "11":
        return change_computer_name_win11(new_name)
    else:
        return change_computer_name_win10(new_name)

def delete_rockstar_games():
    paths = [
        r"C:\Program Files\Rockstar Games",
        r"C:\Program Files (x86)\Rockstar Games",
        os.path.expandvars(r"%LOCALAPPDATA%\Rockstar Games"),
        os.path.expandvars(r"%PROGRAMDATA%\Rockstar Games"),
        os.path.expandvars(r"%USERPROFILE%\Documents\Rockstar Games")
    ]
    
    found = False
    for path in paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"Deleted Rockstar Games folder: {path}")
                found = True
            except Exception as e:
                print(f"Failed to delete {path}: {e}")
    
    if not found:
        print("No Rockstar Games folders found")

def get_mac_address():
    """Get MAC address of the first active network adapter (not virtual/loopback)"""
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK or getattr(socket, 'AF_PACKET', None) == addr.family:
                mac = addr.address
                if mac and len(mac.split(':')) == 6 and not iface.lower().startswith(('loopback', 'vmware', 'virtual', 'npcap', 'npf')):
                    return mac.upper()
    return "Unknown"

def spoof_mac_address():
    """Spoof MAC address of all enabled Ethernet/WLAN adapters"""
    import psutil
    import winreg
    import random
    import re
    changed = 0
    for iface, addrs in psutil.net_if_addrs().items():
        if iface.lower().startswith(('ethernet', 'wi-fi', 'wlan', 'lan')) and not iface.lower().startswith(('loopback', 'vmware', 'virtual', 'npcap', 'npf')):
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}')
                for i in range(100):
                    try:
                        subkey_name = f"{i:04d}"
                        subkey = winreg.OpenKey(key, subkey_name, 0, winreg.KEY_ALL_ACCESS)
                        try:
                            name, _ = winreg.QueryValueEx(subkey, "DriverDesc")
                            if iface.lower() in name.lower():
                                # Generate random MAC
                                new_mac = ''.join(random.choices('02468ACE' + '13579BDF', k=12))
                                new_mac = re.sub(r'(.{2})', r'\1-', new_mac)[:-1]
                                winreg.SetValueEx(subkey, "NetworkAddress", 0, winreg.REG_SZ, new_mac.replace('-', ''))
                                winreg.CloseKey(subkey)
                                # Disable/enable adapter
                                os.system(f'wmic path win32_networkadapter where NetConnectionID="{iface}" call disable')
                                os.system(f'wmic path win32_networkadapter where NetConnectionID="{iface}" call enable')
                                changed += 1
                                break
                        except Exception:
                            pass
                        winreg.CloseKey(subkey)
                    except Exception:
                        break
                winreg.CloseKey(key)
            except Exception:
                continue
    return changed > 0

def clean_registry():
    """Clean registry entries"""
    try:
        # Clean common registry locations
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\LastVisitedPidlMRU"
        ]
        
        for path in registry_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteKey(key, "")
                winreg.CloseKey(key)
                print(f"Cleaned registry: {path}")
            except:
                pass
        
        return True
    except Exception as e:
        print(f"Failed to clean registry: {e}")
        return False

def kill_suspicious_processes():
    """Kill suspicious processes"""
    suspicious_processes = [
        "cheatengine", "x64dbg", "ollydbg", "ida64", "ida32", "ghidra",
        "wireshark", "fiddler", "processhacker", "procexp", "procexp64"
    ]
    
    killed = 0
    for proc in suspicious_processes:
        try:
            subprocess.run(['taskkill', '/f', '/im', f"{proc}.exe"], 
                         capture_output=True, shell=True)
            killed += 1
            print(f"Killed process: {proc}")
        except:
            pass
    
    return killed > 0

def optimize_system():
    """Optimize system performance"""
    try:
        # Disable unnecessary services
        services_to_disable = [
            "SysMain", "WSearch", "Themes", "TabletInputService"
        ]
        
        for service in services_to_disable:
            try:
                subprocess.run(['sc', 'config', service, 'start=', 'disabled'], 
                             capture_output=True, shell=True)
                print(f"Disabled service: {service}")
            except:
                pass
        
        # Clear temp files
        temp_paths = [
            os.path.expandvars(r"%TEMP%"),
            os.path.expandvars(r"%WINDIR%\Temp"),
            os.path.expandvars(r"%LOCALAPPDATA%\Temp")
        ]
        
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    for file in os.listdir(temp_path):
                        file_path = os.path.join(temp_path, file)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except:
                            pass
                    print(f"Cleaned temp: {temp_path}")
                except:
                    pass
        
        return True
    except Exception as e:
        print(f"Failed to optimize system: {e}")
        return False

def clear_browser_data():
    """Clear browser data"""
    browsers = {
        "Chrome": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default"),
        "Firefox": os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
        "Edge": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default")
    }
    
    cleared = 0
    for browser, path in browsers.items():
        if os.path.exists(path):
            try:
                # Clear cache, cookies, history
                cache_dirs = ["Cache", "Code Cache", "GPUCache", "Cookies", "History"]
                for cache_dir in cache_dirs:
                    cache_path = os.path.join(path, cache_dir)
                    if os.path.exists(cache_path):
                        shutil.rmtree(cache_path)
                        print(f"Cleared {browser} {cache_dir}")
                        cleared += 1
            except Exception as e:
                print(f"Failed to clear {browser}: {e}")
    
    return cleared > 0

def validate_key(key):
    """Validate key against API"""
    try:
        data = {
            'key': key,
            'hwid': get_hwid()
        }
        
        # Convert data to JSON
        json_data = json.dumps(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(API_URL, data=json_data, headers={
            'Content-Type': 'application/json',
            'User-Agent': 'KanackenHub-Spoofer/1.0'
        })
        
        # Send request
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('valid', False), result.get('message', 'Unknown error')
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KanackenHub - License Verification")
        self.setFixedSize(500, 700)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0d1117, stop:1 #161b22);
                border: 2px solid #4a9eff;
                border-radius: 20px;
            }
            QWidget {
                color: #ffffff;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
        """)
        
        # Center window
        self.center_window()
        
        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with close button
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1f25;
                border-top-left-radius: 18px;
                border-top-right-radius: 18px;
                border-bottom: 1px solid #4a9eff;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Logo and title
        logo_title_widget = QWidget()
        logo_title_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1f25;
                border: none;
            }
        """)
        logo_title_layout = QHBoxLayout(logo_title_widget)
        logo_title_layout.setContentsMargins(0, 0, 0, 0)
        logo_title_layout.setSpacing(12)
        
        kh_label = QLabel("KH")
        kh_label.setFont(QFont("Segoe UI Black", 24, QFont.Bold))
        kh_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9eff, stop:1 #6bb6ff);
                background: transparent;
                border: none;
                padding: 0;
            }
        """)
        
        title_label = QLabel("License Verification")
        title_label.setFont(QFont("Segoe UI Semibold", 16))
        title_label.setStyleSheet("color: #4a9eff; background: none; border: none;")
        
        logo_title_layout.addWidget(kh_label)
        logo_title_layout.addWidget(title_label)
        logo_title_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setFont(QFont("Segoe UI", 16))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #bfc9d1;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(logo_title_widget)
        header_layout.addWidget(close_btn)
        main_layout.addWidget(header_widget)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                border: none;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Welcome section
        welcome_widget = QWidget()
        welcome_widget.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                border: none;
            }
        """)
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(15)
        
        welcome_title = QLabel("Welcome to KanackenHub")
        welcome_title.setFont(QFont("Segoe UI Semibold", 20))
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("color: #4a9eff; background: none; border: none;")
        
        welcome_subtitle = QLabel("Enter your license key to access the spoofer")
        welcome_subtitle.setFont(QFont("Segoe UI", 12))
        welcome_subtitle.setAlignment(Qt.AlignCenter)
        welcome_subtitle.setStyleSheet("color: #bfc9d1; background: none; border: none;")
        
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_subtitle)
        content_layout.addWidget(welcome_widget)
        
        # License key input section
        key_section = QWidget()
        key_section.setStyleSheet("""
            QWidget {
                background-color: #161b22;
                border-radius: 15px;
                border: 2px solid #232a36;
            }
        """)
        key_layout = QVBoxLayout(key_section)
        key_layout.setContentsMargins(30, 30, 30, 30)
        key_layout.setSpacing(20)
        
        # Key input with icon
        key_header = QWidget()
        key_header.setStyleSheet("""
            QWidget {
                background-color: #161b22;
                border: none;
            }
        """)
        key_header_layout = QHBoxLayout(key_header)
        key_header_layout.setContentsMargins(0, 0, 0, 0)
        key_header_layout.setSpacing(10)
        
        key_icon = QLabel("")
        key_icon.setFont(QFont("Segoe UI", 16))
        key_icon.setStyleSheet("color: #4a9eff; background: none; border: none;")
        
        key_label = QLabel("License Key")
        key_label.setFont(QFont("Segoe UI Semibold", 14))
        key_label.setStyleSheet("color: #4a9eff; background: none; border: none;")
        
        key_header_layout.addWidget(key_icon)
        key_header_layout.addWidget(key_label)
        key_header_layout.addStretch()
        
        self.key_input = QLineEdit()
        self.key_input.setFont(QFont("Segoe UI", 12))
        self.key_input.setFixedHeight(50)
        self.key_input.setPlaceholderText("Enter your license key here...")
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1f25;
                border: 2px solid #4a9eff;
                border-radius: 10px;
                padding: 0 20px;
                color: #ffffff;
                font-weight: bold;
            }
            QLineEdit:focus {
                border: 2px solid #6bb6ff;
                background-color: #232a36;
                box-shadow: 0 0 15px rgba(74, 158, 255, 0.3);
            }
            QLineEdit::placeholder {
                color: #666666;
                font-weight: normal;
            }
        """)
        
        # Load saved license key if exists
        saved_key = get_saved_license_key()
        if saved_key:
            self.key_input.setText(saved_key)
        
        key_layout.addWidget(key_header)
        key_layout.addWidget(self.key_input)
        content_layout.addWidget(key_section)
        
        # Login button section
        button_section = QWidget()
        button_section.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                border: none;
            }
        """)
        button_layout = QVBoxLayout(button_section)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.setFont(QFont("Segoe UI Black", 14))
        self.login_btn.setFixedHeight(55)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9eff, stop:1 #6bb6ff);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                letter-spacing: 1px;
                box-shadow: 0 4px 20px rgba(74, 158, 255, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6bb6ff, stop:1 #8cc6ff);
                box-shadow: 0 6px 25px rgba(74, 158, 255, 0.6);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d5a88, stop:1 #4a9eff);
            }
            QPushButton:disabled {
                background: #232a36;
                color: #666666;
                box-shadow: none;
            }
        """)
        self.login_btn.clicked.connect(self.validate_login)
        
        # Status section
        self.status_widget = QWidget()
        self.status_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1f25, stop:1 #232a36);
                border-radius: 10px;
                border: 1px solid #232a36;
            }
        """)
        self.status_widget.hide()
        status_layout = QVBoxLayout(self.status_widget)
        status_layout.setContentsMargins(20, 15, 20, 15)
        
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #ff6b6b; background: none; border: none;")
        self.status_label.setWordWrap(True)
        
        status_layout.addWidget(self.status_label)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.status_widget)
        content_layout.addWidget(button_section)
        
        # Info section
        info_section = QWidget()
        info_section.setStyleSheet("""
            QWidget {
                background-color: #101a2b;
                border-radius: 12px;
                border: 1px solid #4a9eff;
            }
        """)
        info_layout = QVBoxLayout(info_section)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(10)
        
        info_title = QLabel("ℹ️ License Information")
        info_title.setFont(QFont("Segoe UI Semibold", 12))
        info_title.setStyleSheet("color: #4a9eff; background: none; border: none;")
        
        info_text = QLabel("• Your license key is tied to your hardware ID\n• One license per device\n• Contact support for assistance")
        info_text.setFont(QFont("Segoe UI", 10))
        info_text.setStyleSheet("color: #bfc9d1; background: none; border: none; line-height: 1.5;")
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        content_layout.addWidget(info_section)
        
        # Footer
        footer_widget = QWidget()
        footer_widget.setFixedHeight(50)
        footer_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1f25;
                border-bottom-left-radius: 18px;
                border-bottom-right-radius: 18px;
                border-top: 1px solid #4a9eff;
            }
        """)
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        
        discord_label = QLabel("discord.gg/kanackenhub")
        discord_label.setFont(QFont("Segoe UI Semibold", 12))
        discord_label.setStyleSheet("color: #4a9eff; background: none; border: none;")
        
        footer_layout.addStretch()
        footer_layout.addWidget(discord_label)
        footer_layout.addStretch()
        
        main_layout.addWidget(content_widget)
        main_layout.addWidget(footer_widget)
        
        # Enter key to login
        self.key_input.returnPressed.connect(self.validate_login)
        
        # Store main window reference
        self.main_window = None
        
        # Auto-login if saved key exists
        if saved_key:
            QTimer.singleShot(1000, self.auto_login)
    
    def auto_login(self):
        """Automatically login with saved key"""
        saved_key = get_saved_license_key()
        if saved_key:
            self.show_status("Auto-login with saved key...", "info")
            self.validate_login()
    

    
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def validate_login(self):
        """Validate the entered key"""
        key = self.key_input.text().strip()
        
        if not key:
            self.show_status("Please enter a license key", "error")
            return
        
        # Disable login button and show loading
        self.login_btn.setEnabled(False)
        self.login_btn.setText("Login...")
        self.show_status("Connecting to server...", "info")
        
        # Validate key in background
        self.worker = KeyValidationWorker(key)
        self.worker.finished.connect(self.login_result)
        self.worker.start()
    
    def show_status(self, message, status_type="info"):
        """Show status message with different styles"""
        self.status_label.setText(message)
        self.status_widget.show()
        
        if status_type == "error":
            self.status_label.setStyleSheet("color: #ff6b6b; background: none; border: none;")
            self.status_widget.setStyleSheet("""
                QWidget {
                    background-color: #2a1a1a;
                    border-radius: 10px;
                    border: 1px solid #ff6b6b;
                }
            """)
        elif status_type == "success":
            self.status_label.setStyleSheet("color: #51cf66; background: none; border: none;")
            self.status_widget.setStyleSheet("""
                QWidget {
                    background-color: #1a2a1a;
                    border-radius: 10px;
                    border: 1px solid #51cf66;
                }
            """)
        else:  # info
            self.status_label.setStyleSheet("color: #4a9eff; background: none; border: none;")
            self.status_widget.setStyleSheet("""
                QWidget {
                    background-color: #1a1f25;
                    border-radius: 10px;
                    border: 1px solid #4a9eff;
                }
            """)
    
    def login_result(self, success, message):
        """Handle login result"""
        self.login_btn.setEnabled(True)
        self.login_btn.setText("Login")
        
        if success:
            # Save the license key
            key = self.key_input.text().strip()
            if key:
                save_license_key(key)
            
            self.show_status("Login successful! Opening application...", "success")
            
            # Create and show main window
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            self.show_status(message, "error")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

class KeyValidationWorker(QThread):
    finished = pyqtSignal(bool, str)
    
    def __init__(self, key):
        super().__init__()
        self.key = key
    
    def run(self):
        """Validate key in background thread"""
        try:
            valid, message = validate_key(self.key)
            self.finished.emit(valid, message)
        except Exception as e:
            self.finished.emit(False, f"Validation error: {str(e)}")

class SpoofWorker(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)

    def __init__(self, action, selected_drive="C", windows_version="auto"):
        super().__init__()
        self.action = action
        self.selected_drive = selected_drive
        self.windows_version = windows_version

    def run(self):
        try:
            if self.action == "all":
                self.progress.emit("Changing HWID...")
                appdata = os.getenv("APPDATA")
                volumeid_folder = os.path.join(appdata, "hdsn changer")
                volumeid_exe = os.path.join(volumeid_folder, "volumeid.exe")
                
                if not download_volumeid(volumeid_folder):
                    self.finished.emit(False, "Failed to download VolumeID")
                    return

                drives = list_available_drives()
                if not drives:
                    self.finished.emit(False, "No drives found")
                    return

                drive = self.selected_drive
                old_id = get_current_volume_id(drive)
                if not old_id:
                    self.finished.emit(False, f"Could not get current HWID for drive {drive}:")
                    return

                new_id = generate_random_volume_id()
                if not change_volume_id(volumeid_exe, drive, new_id):
                    self.finished.emit(False, f"Failed to change HWID for drive {drive}:")
                    return

                self.progress.emit("Changing PC Name...")
                new_name = generate_random_computer_name()
                if not change_computer_name(new_name, self.windows_version):
                    self.finished.emit(False, "Failed to change PC Name")
                    return

                self.progress.emit("Cleaning Rockstar Games...")
                delete_rockstar_games()

                self.finished.emit(True, "All operations completed successfully!")
            
            elif self.action == "volume":
                self.progress.emit("Changing HWID...")
                appdata = os.getenv("APPDATA")
                volumeid_folder = os.path.join(appdata, "hdsn changer")
                volumeid_exe = os.path.join(volumeid_folder, "volumeid.exe")
                
                if not download_volumeid(volumeid_folder):
                    self.finished.emit(False, "Failed to download VolumeID")
                    return

                drives = list_available_drives()
                if not drives:
                    self.finished.emit(False, "No drives found")
                    return

                drive = self.selected_drive
                old_id = get_current_volume_id(drive)
                if not old_id:
                    self.finished.emit(False, f"Could not get current HWID for drive {drive}:")
                    return

                new_id = generate_random_volume_id()
                if not change_volume_id(volumeid_exe, drive, new_id):
                    self.finished.emit(False, f"Failed to change HWID for drive {drive}:")
                    return

                self.finished.emit(True, f"HWID changed successfully for drive {drive}:!")
            
            elif self.action == "pcname":
                self.progress.emit("Changing PC Name...")
                new_name = generate_random_computer_name()
                if not change_computer_name(new_name, self.windows_version):
                    self.finished.emit(False, "Failed to change PC Name")
                    return
                self.finished.emit(True, "PC Name changed successfully!")
            
            elif self.action == "rockstar":
                self.progress.emit("Cleaning Rockstar Games...")
                delete_rockstar_games()
                self.finished.emit(True, "Rockstar Games cleaned successfully!")

        except Exception as e:
            self.finished.emit(False, str(e))

class CustomButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 9))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(35)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1f25;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton:hover {
                background-color: #2d5a88;
            }
            QPushButton:pressed {
                background-color: #1e3d5c;
            }
            QPushButton:disabled {
                background-color: #1a1f25;
                color: #666666;
            }
        """)

class CategoryLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI Semibold", 12))
        self.setStyleSheet("color: #4a9eff; background: none; border: none; border-radius: 0; box-shadow: none; padding: 0;")

class InfoBox(QWidget):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1f25;
                border-radius: 8px;
                border: 1px solid #2d5a88;
            }
        """)
        self.setFixedHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 9))
        title_label.setStyleSheet("color: #4a9eff; background: none; border: none;")
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.value_label.setStyleSheet("color: #ffffff; background: none; border: none;")
        self.value_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
    
    def update_value(self, value):
        self.value_label.setText(value)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("discord.gg/kanackenhub")
        self.setFixedSize(1000, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QWidget {
                color: #ffffff;
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }
            QFrame#separator {
                background-color: #232a36;
                max-height: 1px;
            }
        """)

        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Panel
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #161b22;
                border-radius: 20px;
                box-shadow: 0 8px 32px 0 rgba(74,158,255,0.18);
                border: 1px solid #232a36;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Logo Section
        logo_widget = QWidget()
        logo_widget.setFixedHeight(80)
        logo_widget.setStyleSheet("background: transparent; border: none;")
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(20, 15, 20, 15)
        
        kh_label = QLabel("KH")
        kh_label.setFont(QFont("Segoe UI Black", 42, QFont.Bold))
        kh_label.setAlignment(Qt.AlignCenter)
        kh_label.setStyleSheet("""
            QLabel {
                color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9eff, stop:1 #bfc9d1);
                background: transparent;
                border: none;
                padding: 0;
            }
        """)
        logo_layout.addWidget(kh_label)
        left_layout.addWidget(logo_widget)

        # Separator
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFixedHeight(1)
        left_layout.addWidget(separator)

        # Navigation Section
        nav_widget = QWidget()
        nav_widget.setStyleSheet("background: transparent; border: none;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 20, 20, 20)
        nav_layout.setSpacing(12)

        # Information Category
        info_label = CategoryLabel("Information")
        nav_layout.addWidget(info_label)

        info_btn = CustomButton("System Info")
        info_btn.clicked.connect(self.show_info)
        nav_layout.addWidget(info_btn)

        # Spacing
        nav_layout.addSpacing(10)

        # Spoofing Category
        spoof_label = CategoryLabel("Spoofing")
        nav_layout.addWidget(spoof_label)

        self.spoof_buttons = []
        
        # All Spoof Button
        all_btn = CustomButton("Spoof All")
        all_btn.setFixedHeight(45)
        all_btn.setFont(QFont("Segoe UI Semibold", 13))
        all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9eff, stop:1 #bfc9d1);
                color: #fff;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d5a88, stop:1 #4a9eff);
                color: #eaf6ff;
            }
            QPushButton:pressed {
                background: #1e3d5c;
                color: #bfc9d1;
            }
            QPushButton:disabled {
                background: #232a36;
                color: #666666;
            }
        """)
        all_btn.clicked.connect(lambda: self.start_spoof("all"))
        self.spoof_buttons.append(all_btn)
        nav_layout.addWidget(all_btn)
        nav_layout.addSpacing(18)  # Mehr Abstand nach Spoof All

        # Individual Spoof Buttons
        volume_btn = CustomButton("HWID")
        volume_btn.clicked.connect(lambda: self.start_spoof("volume"))
        self.spoof_buttons.append(volume_btn)
        nav_layout.addWidget(volume_btn)

        pcname_btn = CustomButton("PC Name")
        pcname_btn.clicked.connect(lambda: self.start_spoof("pcname"))
        self.spoof_buttons.append(pcname_btn)
        nav_layout.addWidget(pcname_btn)

        rockstar_btn = CustomButton("Rockstar Cleaner")
        rockstar_btn.clicked.connect(lambda: self.start_spoof("rockstar"))
        self.spoof_buttons.append(rockstar_btn)
        nav_layout.addWidget(rockstar_btn)

        # Drive Selection Category
        nav_layout.addSpacing(10)
        drive_label = CategoryLabel("Drive Selection")
        nav_layout.addWidget(drive_label)

        # Drive selection dropdown
        self.drive_combo = QComboBox()
        self.drive_combo.setFont(QFont("Segoe UI", 10))
        self.drive_combo.setFixedHeight(35)
        self.drive_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1f25;
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 8px;
                padding: 0 15px;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 2px solid #6bb6ff;
                background-color: #232a36;
            }
            QComboBox:focus {
                border: 2px solid #6bb6ff;
                background-color: #232a36;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4a9eff;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1f25;
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 8px;
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
            }
        """)
        
        # Populate drive list
        drives = list_available_drives()
        for drive in drives:
            self.drive_combo.addItem(f"Drive {drive}:", drive)
        
        # Set default to C: if available
        default_index = self.drive_combo.findData("C")
        if default_index >= 0:
            self.drive_combo.setCurrentIndex(default_index)
        
        nav_layout.addWidget(self.drive_combo)

        # Windows Version Selection Category
        nav_layout.addSpacing(10)
        windows_label = CategoryLabel("Windows Version")
        nav_layout.addWidget(windows_label)

        # Windows version selection dropdown
        self.windows_combo = QComboBox()
        self.windows_combo.setFont(QFont("Segoe UI", 10))
        self.windows_combo.setFixedHeight(35)
        self.windows_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1f25;
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 8px;
                padding: 0 15px;
                font-weight: bold;
            }
            QComboBox:hover {
                border: 2px solid #6bb6ff;
                background-color: #232a36;
            }
            QComboBox:focus {
                border: 2px solid #6bb6ff;
                background-color: #232a36;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4a9eff;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1f25;
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 8px;
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
            }
        """)
        
        # Add Windows version options
        self.windows_combo.addItem("Auto-detect", "auto")
        self.windows_combo.addItem("Windows 10", "10")
        self.windows_combo.addItem("Windows 11", "11")
        
        # Load saved Windows version
        saved_version = get_saved_windows_version()
        version_index = self.windows_combo.findData(saved_version)
        if version_index >= 0:
            self.windows_combo.setCurrentIndex(version_index)
        
        # Save selection when changed
        self.windows_combo.currentTextChanged.connect(self.save_windows_version_setting)
        
        nav_layout.addWidget(self.windows_combo)

        nav_layout.addStretch()
        left_layout.addWidget(nav_widget)

        # User Section
        user_widget = QWidget()
        user_widget.setFixedHeight(50)
        user_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1f25;
                border-top: 1px solid #2d5a88;
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        user_layout = QHBoxLayout(user_widget)
        user_layout.setContentsMargins(20, 10, 20, 10)
        
        name = QLabel("kanackenhub")
        name.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name.setStyleSheet("color: #4a9eff; background: none; border: none;")
        user_layout.addWidget(name)
        user_layout.addStretch()
        left_layout.addWidget(user_widget)

        # Right Content Area
        self.content = QWidget()
        self.content.setStyleSheet("""
            QWidget {
                background-color: #10141b;
                border-radius: 20px;
                box-shadow: 0 4px 20px 0 rgba(0,0,0,0.3);
            }
        """)
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Title Bar
        title_bar = QWidget()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background: transparent; border: none;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("System Spoofer")
        title.setFont(QFont("Segoe UI Semibold", 16))
        title.setStyleSheet("color: #4a9eff; background: none; border: none;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        # Window Controls
        controls_widget = QWidget()
        controls_widget.setFixedWidth(80)
        controls_widget.setStyleSheet("background: transparent; border: none;")
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(5)
        
        min_btn = QPushButton("−")
        close_btn = QPushButton("×")
        
        for btn in [min_btn, close_btn]:
            btn.setFixedSize(30, 30)
            btn.setFont(QFont("Segoe UI", 14))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #bfc9d1;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #232a36;
                }
            """)
        
        min_btn.clicked.connect(self.showMinimized)
        close_btn.clicked.connect(self.close)
        
        controls_layout.addWidget(min_btn)
        controls_layout.addWidget(close_btn)
        title_layout.addWidget(controls_widget)
        content_layout.addWidget(title_bar)

        # Status Section
        self.status_label = QLabel("Welcome to KanackenHub Spoofer")
        self.status_label.setFont(QFont("Segoe UI Semibold", 18))
        self.status_label.setStyleSheet("color: #4a9eff; background: none; border: none;")
        self.status_label.setAlignment(Qt.AlignHCenter)
        self.status_label.setWordWrap(True)
        content_layout.addWidget(self.status_label)

        # Progress Bar
        self.spinner = QProgressBar()
        self.spinner.setRange(0, 0)
        self.spinner.setFixedHeight(8)
        self.spinner.setTextVisible(False)
        self.spinner.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background: #232a36;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a9eff, stop:1 #bfc9d1);
                border-radius: 4px;
            }
        """)
        self.spinner.hide()
        content_layout.addWidget(self.spinner)

        # Information Display Area
        self.info_widget = QWidget()
        self.info_widget.hide()
        self.info_widget.setStyleSheet("background: transparent; border: none;")
        info_layout = QVBoxLayout(self.info_widget)
        info_layout.setSpacing(20)

        info_title = QLabel("System Information")
        info_title.setFont(QFont("Segoe UI Semibold", 16))
        info_title.setStyleSheet("color: #4a9eff; background: none; border: none;")
        info_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_title)

        # Info boxes
        info_boxes_widget = QWidget()
        info_boxes_widget.setStyleSheet("background: transparent; border: none;")
        info_boxes_layout = QVBoxLayout(info_boxes_widget)
        info_boxes_layout.setSpacing(15)

        self.pcname_box = InfoBox("PC Name", "Loading...")
        self.volumeid_box = InfoBox("HWID", "Loading...")
        self.windows_version_box = InfoBox("Windows Version", "Loading...")

        info_boxes_layout.addWidget(self.pcname_box)
        info_boxes_layout.addWidget(self.volumeid_box)
        info_boxes_layout.addWidget(self.windows_version_box)

        info_layout.addWidget(info_boxes_widget)
        content_layout.addWidget(self.info_widget)

        content_layout.addStretch()

        # Credits Section
        credits_widget = QWidget()
        credits_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #101a2b, stop:1 #22334a);
                border-radius: 15px;
                border: 2px solid #4a9eff;
            }
        """)
        credits_layout = QVBoxLayout(credits_widget)
        credits_layout.setContentsMargins(20, 15, 20, 15)
        
        credits = QLabel("discord.gg/kanackenhub")
        credits.setFont(QFont("Segoe UI Semibold", 16))
        credits.setStyleSheet("color: #4a9eff; background: none; border: none;")
        credits.setAlignment(Qt.AlignCenter)
        credits_layout.addWidget(credits)
        
        content_layout.addWidget(credits_widget)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.content)

    def save_windows_version_setting(self):
        """Save Windows version selection to settings"""
        selected_version = self.windows_combo.currentData()
        if selected_version:
            save_windows_version(selected_version)

    def show_info(self):
        """Show system information"""
        self.status_label.setText("")
        self.spinner.hide()
        self.info_widget.show()
        
        # Update info boxes with current values
        pc_name = get_pc_name()
        selected_drive = self.drive_combo.currentData() or "C"
        volume_id = get_current_volume_id(selected_drive) or "Unknown"
        
        # Get Windows version info
        detected_version = detect_windows_version()
        selected_version = self.windows_combo.currentData()
        if selected_version == "auto":
            version_display = f"Windows {detected_version} (Auto-detected)"
        else:
            version_display = f"Windows {selected_version} (Selected)"
        
        self.pcname_box.update_value(pc_name)
        self.volumeid_box.update_value(f"{volume_id} (Drive {selected_drive}:)")
        self.windows_version_box.update_value(version_display)

    def start_spoof(self, action):
        """Start spoofing operation"""
        self.info_widget.hide()
        
        for btn in self.spoof_buttons:
            btn.setEnabled(False)
        
        # Get selected drive from combo box
        selected_drive = self.drive_combo.currentData()
        if not selected_drive:
            selected_drive = "C"  # Default fallback
        
        # Get selected Windows version
        windows_version = self.windows_combo.currentData()
        if not windows_version:
            windows_version = "auto"  # Default fallback
        
        self.worker = SpoofWorker(action, selected_drive, windows_version)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.spoof_finished)
        self.worker.start()

    def update_status(self, message):
        self.status_label.setText(message)
        if message:
            self.spinner.show()
        else:
            self.spinner.hide()

    def spoof_finished(self, success, message):
        for btn in self.spoof_buttons:
            btn.setEnabled(True)
        if success:
            self.status_label.setText('Successfully completed')
            self.spinner.hide()
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setText(message)
            msg.setInformativeText("discord.gg/kanackenhub")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #161b22;
                    color: #ffffff;
                }
                QLabel {
                    color: #4a9eff;
                }
                QPushButton {
                    background-color: #4a9eff;
                    color: #fff;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 18px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2d5a88;
                }
            """)
            msg.exec_()
        else:
            self.spinner.hide()
            QMessageBox.warning(self, "Error", message)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Check for admin rights first
    if not is_admin():
        QMessageBox.information(None, "Admin Rights Required", 
                               "This application requires administrator privileges.\n"
                               "The application will restart with admin rights.")
        run_as_admin()
        sys.exit()
    
    # Only show login window if we have admin rights
    login_window = LoginWindow()
    login_window.setWindowFlags(Qt.FramelessWindowHint)
    login_window.setAttribute(Qt.WA_TranslucentBackground)
    login_window.show()
    sys.exit(app.exec_())