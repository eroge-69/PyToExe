import random
from io import BytesIO
import base64
import os
import json
import platform
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import datetime
import ntplib
import tkinter as tk
from tkinter import ttk, messagebox
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import subprocess
from selenium.webdriver.chrome.service import Service
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
import tempfile
import time
import socket
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs
import sys
import logging
from bs4 import BeautifulSoup

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# تشخیص دیباگر
if 'VIRTUAL_ENV' in os.environ or 'PYCHARM_HOSTED' in os.environ:
    sys.exit('Debugger detected')

def find_file_recursively(filename, search_paths):
    """
    Recursively search for a file in given directories.
    :param filename: Name of the file to search (e.g., 'brave.exe' or 'chromedriver').
    :param search_paths: List of directories to search in.
    :return: Full path to the file if found, otherwise None.
    """
    for path in search_paths:
        for root, _, files in os.walk(path):
            if filename in files:
                return os.path.join(root, filename)
    return None

def find_browser_paths(browser_name):
    """
    Dynamically find paths for the given browser and its driver.
    :param browser_name: Name of the browser (e.g., 'brave', 'yandex', 'vivaldi').
    :return: Tuple (browser_binary_path, browser_driver_path)
    """
    os_name = platform.system().lower()
    search_dirs = []
    binary_name = ''
    driver_name = ''
    
    if os_name == 'windows':
        search_dirs = [os.environ.get('ProgramFiles', ''), os.environ.get('ProgramFiles(x86)', ''), 'C:\\']
    elif os_name == 'linux':
        search_dirs = ['/usr/bin', '/usr/local/bin', '/opt', '/home']
    elif os_name == 'darwin':
        search_dirs = ['/Applications', '/Users']
    else:
        raise OSError('Unsupported operating system.')
    
    if browser_name.lower() == 'brave':
        binary_name = 'brave.exe' if os_name == 'windows' else 'brave'
        driver_name = 'chromedriver'
    elif browser_name.lower() == 'yandex':
        binary_name = 'browser.exe' if os_name == 'windows' else 'yandex-browser'
        driver_name = 'yandexdriver'
    elif browser_name.lower() == 'vivaldi':
        binary_name = 'vivaldi.exe' if os_name == 'windows' else 'vivaldi'
        driver_name = 'chromedriver'
    elif browser_name == 'opera':
        binary_name = 'opera.exe' if os_name == 'windows' else 'opera'
        driver_name = 'operadriver'
    elif browser_name == 'chromium':
        binary_name = 'chromium.exe' if os_name == 'windows' else 'chromium'
        driver_name = 'chromedriver'
    else:
        raise ValueError('Unsupported browser name. Supported browsers: brave, yandex, vivaldi, opera, chromium')
    
    browser_binary = find_file_recursively(binary_name, search_dirs)
    if not browser_binary:
        raise FileNotFoundError(f'{browser_name} browser not found on this system.')
    
    return browser_binary

def get_api_key(file_path='apikey.txt'):
    """
    Reads the API key from the specified file or creates it if it doesn't exist.

    Args:
        file_path (str): The path to the file containing the API key.

    Returns:
        str: The API key read from the file, or a message indicating the file was created.
    """
    try:
        with open(file_path, 'r') as file:
            api_key = file.readline().strip()
            return api_key
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            file.write('')
        return f'File \'{file_path}\' not found. An empty file has been created.'
    except Exception as e:
        return f'Error: Failed to read API key. {str(e)}'

class Config:
    def __init__(self, name, link):
        self.name = name
        self.link = link
    
    def __str__(self):
        return '###'.join([str(getattr(self, field)) for field in ['name', 'link']])

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def parse_link(link):
    if link.startswith('vless://'):
        main_part = link[8:]
        if '#' in main_part:
            main_part, _ = main_part.split('#', 1)
        parsed = urlparse(f'//{main_part}', scheme='vless')
        params = parse_qs(parsed.query)
        return {
            'protocol': 'vless',
            'uuid': parsed.username,
            'host': parsed.hostname,
            'port': int(parsed.port),
            'type': params.get('type', ['tcp'])[0],
            'encryption': params.get('encryption', ['none'])[0],
            'security': params.get('security', ['none'])[0],
            'path': params.get('path', ['/'])[0],
            'host_header': params.get('host', [''])[0],
            'headerType': params.get('headerType', [''])[0]
        }
    elif link.startswith('vmess://'):
        decoded = base64.urlsafe_b64decode(link[8:] + '===').decode('utf-8')
        config = json.loads(decoded)
        return {
            'protocol': 'vmess', 
            'uuid': config['id'], 
            'host': config['add'], 
            'port': int(config['port']), 
            'type': config.get('net', 'tcp'), 
            'security': config.get('tls', 'none')
        }
    raise ValueError('لینک پشتیبانی نمی‌شود')

def build_config(data, proxy_port):
    stream_settings = {'network': data['type']}
    
    if data['type'] == 'tcp':
        stream_settings['tcpSettings'] = {'header': {'type': data.get('headerType', 'none')}}
    elif data['type'] == 'ws':
        stream_settings['wsSettings'] = {
            'path': data.get('path', '/'), 
            'headers': {'Host': data.get('host_header') or data.get('host')}
        }
    
    stream_settings['security'] = 'tls' if data.get('security') == 'tls' else 'none'
    if stream_settings['security'] == 'tls':
        stream_settings['tlsSettings'] = {
            'allowInsecure': True, 
            'serverName': data.get('host')
        }
    
    out = {
        'tag': 'proxy', 
        'protocol': data['protocol'], 
        'settings': {}, 
        'streamSettings': stream_settings, 
        'mux': {'enabled': False, 'concurrency': -1}
    }
    
    if data['protocol'] == 'vless':
        out['settings'] = {
            'vnext': [{
                'address': data['host'], 
                'port': data['port'], 
                'users': [{
                    'id': data['uuid'], 
                    'encryption': data.get('encryption', 'none'), 
                    'level': 8
                }]
            }]
        }
    elif data['protocol'] == 'vmess':
        out['settings'] = {
            'vnext': [{
                'address': data['host'], 
                'port': data['port'], 
                'users': [{
                    'id': data['uuid'], 
                    'alterId': 0, 
                    'security': 'auto'
                }]
            }]
        }
    
    return {
        'log': {'loglevel': 'warning'},
        'inbounds': [{
            'listen': '127.0.0.1',
            'port': proxy_port,
            'protocol': 'socks',
            'settings': {'auth': 'noauth', 'udp': True, 'userLevel': 8},
            'sniffing': {'enabled': True, 'destOverride': ['http', 'tls']},
            'tag': 'in'
        }],
        'outbounds': [
            out,
            {'protocol': 'freedom', 'tag': 'direct', 'settings': {}},
            {'protocol': 'blackhole', 'tag': 'block', 'settings': {}}
        ],
        'routing': {
            'domainStrategy': 'IPIfNonMatch',
            'rules': [
                {'type': 'field', 'inboundTag': ['in'], 'outboundTag': 'proxy'}
            ]
        }
    }

def find_v2ray_executable():
    return 'v2ray.exe'

def start_v2ray(config):
    v2ray_path = find_v2ray_executable()
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as f:
        json.dump(config, f, indent=2)
        config_path = f.name
    
    print('🚀 در حال اجرای v2ray...')
    v2_process = subprocess.Popen([v2ray_path, 'run', '-config', config_path], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    
    if v2_process.poll() is not None:
        stdout, stderr = v2_process.communicate()
        print(stderr.decode() or stdout.decode())
        raise RuntimeError('❌ اجرای v2ray ناموفق بود')
    
    return (v2_process, config_path)

def delete_pics():
    import glob
    current_dir = os.getcwd()
    png_files = glob.glob(os.path.join(current_dir, '*.png'))
    
    for file_path in png_files:
        try:
            os.remove(file_path)
            print(f'فایل {file_path} با موفقیت حذف شد.')
        except Exception as e:
            print(f'خطا در حذف فایل {file_path}: {e}')
    
    print('عملیات حذف فایل‌های PNG تکمیل شد.')

def get_ip(proxy_port):
    try:
        proxies = {'http': f'socks5h://127.0.0.1:{proxy_port}', 'https': f'socks5h://127.0.0.1:{proxy_port}'}
        r = requests.get('https://ipnumberia.com', proxies=proxies, timeout=10)
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            tbody = soup.find('tbody')
            
            if tbody:
                first_td = tbody.find('tr').find('td')
                if first_td:
                    return first_td.get_text(strip=True)
    except Exception as e:
        print(f'خطا: {e}')
    
    return 'IP یافت نشد!'

def option_with_proxy(option: ChromeOptions, proxy_port):
    try:
        option.add_argument(f'--proxy-server=socks5://127.0.0.1:{proxy_port}')
    except Exception as e:
        print(f"خطا در تنظیم پراکسی: {e}")
        input(e)

class SuperDriver:
    def __init__(self):
        self.d = None
    
    def execute_script(self, script, *args):
        try:
            return self.d.execute_script(script, *args)
        except Exception as e:
            print(f"خطا در اجرای اسکریپت: {e}")
            return None
    
    def find_element(self, by, value) -> WebElement:
        try:
            return self.d.find_element(by, value)
        except Exception:
            raise NoSuchElementException(f'Element not found: {by} = {value}')
    
    def find_elements(self, by, value) -> list[WebElement]:
        return self.d.find_elements(by, value)
    
    def get_safe_element(self, ByOBJ, val, ter='', max_attempts=10):
        attempts = 0
        while attempts < max_attempts:
            try:
                elem = self.find_element(ByOBJ, val)
                return elem
            except Exception:
                if ter:
                    try:
                        self.click(ter)
                    except Exception:
                        pass
                attempts += 1
                time.sleep(0.5)
        raise NoSuchElementException(f'Element not found after {max_attempts} attempts: {ByOBJ} = {val}')
    
    def click(self, el):
        try:
            self.d.execute_script('arguments[0].scrollIntoView(true);', el)
            self.d.execute_script('arguments[0].click();', el)
        except Exception as e:
            print(f"خطا در کلیک: {e}")
    
    def send_keys(self, element, val):
        try:
            self.d.execute_script('arguments[0].value = arguments[1];', element, val)
        except Exception as e:
            print(f"خطا در ارسال کلیدها: {e}")
            return None
    
    def find_el_or_error(self, ByXP, selector):
        selector = '//div[@class=\'error\']//div//h1 | div[@class=\'alert info\'] | div[@class=\'errorbox\'] | ' + selector
        e = self.get_safe_element(ByOBJ=ByXP, val=selector)
        
        try:
            self.find_element(By.XPATH, '//div[@class=\'error\']//div//h1 | div[@class=\'alert info\'] | div[@class=\'errorbox\']')
            return -1
        except Exception:
            return e
    
    def delete_el_class(self, class_name):
        """
        تابعی برای حذف تگ‌ها و جلوگیری از بارگذاری آن‌ها بر اساس کلاس.
        """
        script = f"""
        (function() {{
            // انتخابگر بر اساس کلاس
            var selector = ".{class_name}";

            // حذف تگ‌های موجود هنگام بارگذاری اولیه
            function removeElements() {{
                document.querySelectorAll(selector).forEach(function(element) {{
                    element.parentNode.removeChild(element);
                }});
            }}
            removeElements();

            // مشاهده تغییرات DOM و حذف تگ‌های جدید
            var observer = new MutationObserver(function(mutations) {{
                mutations.forEach(function(mutation) {{
                    mutation.addedNodes.forEach(function(node) {{
                        if (node.nodeType === 1 && node.matches(selector)) {{ // فقط عناصر HTML با انتخابگر مشخص
                            node.parentNode.removeChild(node);
                        }}
                    }});
                }});
            }});

            observer.observe(document.documentElement, {{ childList: true, subtree: true }});

            // جلوگیری از درخواست‌های شبکه برای منابع مرتبط با المان‌ها
            var originalFetch = window.fetch;
            window.fetch = function(input, init) {{
                if (typeof input === 'string' && input.includes("{class_name}")) {{
                    return Promise.resolve(new Response(null, {{ status: 204 }})); // پاسخ خالی
                }}
                return originalFetch(input, init);
            }};

            var originalXhrOpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url) {{
                if (url.includes("{class_name}")) {{
                    this.abort();
                }} else {{
                    originalXhrOpen.apply(this, arguments);
                }}
            }};
        }})();
        """
        self.d.execute_script(script)

def solve_and_process_captcha(driver: SuperDriver, api_key, f=0, max_attempts=5):
    """
    1. Extract the captcha image from the page using the provided driver.
    2. Process the captcha image to enhance text clarity.
    3. Solve the captcha using a solving API.

    Parameters:
        driver (SuperDriver): The driver instance with the page loaded.
        api_key (str): API key for captcha solving service.
        f (int): Flag to indicate which captcha element to use.
        max_attempts (int): Maximum number of attempts to solve captcha.

    Returns:
        str: The solved captcha text or an error message.
    """
    attempts = 0
    
    while attempts < max_attempts:
        try:
            if f == 0:
                captcha_element = driver.get_safe_element(By.XPATH, '//img[@class=\'captcha_image\']')
            else:
                captcha_element = driver.get_safe_element(By.XPATH, '//img[@class=\'captcha_image_reserve\']')
            
            wait_loading(captcha_element)
            is_image_loaded = driver.d.execute_script(
                'return arguments[0].complete && arguments[0].naturalWidth > 0;', captcha_element)
            
            if not is_image_loaded:
                print('Captcha not fully loaded, retrying...')
                time.sleep(0.5)
                attempts += 1
                continue
            
            image_base64 = driver.d.execute_script("""
                var canvas = document.createElement('canvas');
                var context = canvas.getContext('2d');
                var img = arguments[0];
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                context.drawImage(img, 0, 0, img.naturalWidth, img.naturalHeight);
                return canvas.toDataURL('image/png').substring(22);  // حذف 'data:image/png;base64,'
            """, captcha_element)
            
            image_data = base64.b64decode(image_base64)
            random_filename = f'captcha_{random.randint(10000000, 99999999)}.png'
            print(random_filename)
            
            with open(random_filename, 'wb') as file:
                file.write(image_data)
            print(f'Captcha image saved as: {random_filename}')
            
            captcha_image = Image.open(random_filename)
            processed_image = ImageOps.grayscale(captcha_image)
            processed_image = processed_image.filter(ImageFilter.MedianFilter(size=3))
            contrast_enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = contrast_enhancer.enhance(1.75)
            processed_image = processed_image.point(lambda p: p * 10 if p < 200 else 255)
            processed_image = processed_image.point(lambda p: p if p == 0 else 255)
            processed_image.save('black_' + random_filename)
            
            processed_image_byte_array = BytesIO()
            processed_image.save(processed_image_byte_array, format='PNG')
            processed_image_byte_array.seek(0)
            base64_image = base64.b64encode(processed_image_byte_array.getvalue()).decode('utf-8')
            
            if api_key.startswith('Error'):
                return api_key
            
            url_in = 'http://api.hcaptcha.ir/in.php'
            data = {'method': 'base64', 'key': api_key, 'body': base64_image}
            response = requests.post(url_in, data=data)
            
            if not response.ok:
                return f'Error: Failed to send request. Status code: {response.status_code}'
            
            response_text = response.text
            if not response_text.startswith('OK'):
                return f'Error: {response_text}'
            
            captcha_id = response_text.split('|')[1]
            url_res = 'http://api.hcaptcha.ir/res.php'
            print('Waiting for captcha solution...')
            
            for _ in range(10):  # حداکثر 10 بار تلاش برای دریافت نتیجه
                params = {'key': api_key, 'action': 'get', 'id': captcha_id}
                result_response = requests.get(url_res, params=params)
                
                if not result_response.ok:
                    return f'Error: Failed to get result. Status code: {result_response.status_code}'
                
                result_text = result_response.text
                if result_text == 'CAPCHA_NOT_READY':
                    time.sleep(5)
                    continue
                
                if result_text.startswith('OK'):
                    return result_text.split('|')[1]
                
                return f'Error: {result_text}'
            
            return 'Error: Maximum attempts reached for getting captcha result'
            
        except Exception as e:
            print(f"خطا در پردازش کپچا: {e}")
            attempts += 1
            time.sleep(1)
    
    return f'Error: Failed to solve captcha after {max_attempts} attempts'

def get_ntp_datetime():
    try:
        response = requests.get('https://digikala.com', timeout=5)
        date_str = response.headers.get('Date')
        if date_str:
            server_time = datetime.datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
            return server_time
        raise ValueError('هدر Date در پاسخ وجود ندارد.')
    except Exception as e:
        print('خطا:', e)
        return None

def get_motherboard_uuid():
    try:
        result = subprocess.run(['wmic', 'csproduct', 'get', 'UUID'], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.splitlines()
        uuid = None
        
        for line in lines:
            line = line.strip()
            if line and line != 'UUID':
                uuid = line
                break
        
        if uuid:
            return str(uuid)
        return 'UUID not found'
    except Exception as e:
        return f'Error retrieving UUID: {e}'

def wait(driver: webdriver.Edge, current: list, flag='no', flag2='no', timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if driver.current_url != current[-1]:
            current[-1] = driver.current_url
            return 1
        
        if flag != 'no':
            try:
                s = driver.find_element(By.XPATH, flag)
                return 2
            except Exception:
                pass
        
        if flag2 != 'no':
            try:
                s = driver.find_element(By.XPATH, flag2)
                return 3
            except Exception:
                pass
        
        time.sleep(0.1)
    
    current[-1] = driver.current_url
    return 1

class User:
    def __init__(self, username='', password='', fullname='', khedmat='', vasile_type='', 
                 p1='', chr='', p2='', p3='', motorp1='', motorp2='', shasi_code='', 
                 buyer_type='', buyer_nationalcode='', key_url=''):
        self.username = username
        self.password = password
        self.fullname = fullname
        self.khedmat = khedmat
        self.vasile_type = vasile_type
        self.p1 = p1
        self.chr = chr
        self.p2 = p2
        self.p3 = p3
        self.motorp1 = motorp1
        self.motorp2 = motorp2
        self.shasi_code = shasi_code
        self.buyer_type = buyer_type
        self.buyer_nationalcode = buyer_nationalcode
        self.key_url = key_url
    
    def save_to_file(self):
        data = [
            self.username, self.password, self.fullname, self.khedmat, self.vasile_type,
            self.p1, self.chr, self.p2, self.p3, self.motorp1, self.motorp2,
            self.shasi_code, self.buyer_type, self.buyer_nationalcode, self.key_url
        ]
        
        with open('db.txt', 'a', encoding='utf-8') as file:
            file.write('###'.join(data) + '\n')

def clock_to_int(clk: str):
    if ':' in clk:
        a = clk.split(':')
        return 60 * int(a[0]) + int(a[1])
    return None

def safe_get_text(element: WebElement):
    try:
        return element.get_attribute('innerText')
    except Exception:
        return None

def check_servererror(driver: SuperDriver, xp=''):
    try:
        driver.find_element(By.XPATH, xp)
        return True
    except Exception:
        return False

def ensure_files_exist(file_list):
    for file_name in file_list:
        if not os.path.exists(file_name):
            if file_name.endswith('.txt'):
                with open(file_name, 'w', encoding='utf-8') as file:
                    pass
                print(f'Created empty file: {file_name}')
            elif file_name.endswith('.exe'):
                if 'chromedriver' in file_name.lower():
                    print('Downloading ChromeDriver...')
                    driver_path = ChromeDriverManager().install()
                    os.rename(driver_path, file_name)
                    print(f'ChromeDriver downloaded and saved as: {file_name}')
                elif 'geckodriver' in file_name.lower():
                    print('Downloading GeckoDriver...')
                    driver_path = GeckoDriverManager().install()
                    os.rename(driver_path, file_name)
                    print(f'GeckoDriver downloaded and saved as: {file_name}')
                elif 'msedgedriver' in file_name.lower():
                    print('Downloading EdgeDriver...')
                    driver_path = EdgeChromiumDriverManager().install()
                    os.rename(driver_path, file_name)
                    print(f'EdgeDriver downloaded and saved as: {file_name}')
                elif 'operadriver' in file_name.lower():
                    print('Downloading ChromeDriver for Opera...')
                    driver_path = ChromeDriverManager().install()
                    os.rename(driver_path, 'chromedriverr.exe')
                    print(f'ChromeDriver for Opera downloaded and saved as: {file_name}')
                elif 'bravedriver' in file_name.lower():
                    print('Downloading ChromeDriver for Brave...')
                    driver_path = ChromeDriverManager().install()
                    os.rename(driver_path, file_name)
                    print(f'ChromeDriver for Brave downloaded and saved as: {file_name}')
                else:
                    print(f'Unsupported webdriver: {file_name}')
            else:
                print(f'Unsupported file type: {file_name}')
        else:
            print(f'File already exists: {file_name}')

def wait_loading(el: WebElement, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if el.is_enabled() and el.is_displayed():
                return True
        except Exception:
            pass
        time.sleep(0.1)
    return False

def F(user: User, config: Config, browser='Chrome', refresh=0, key_url='', t1='', t2='', day='', next_m=False, auto_login=True, ac=True):
    print('auto captcha solving:', ac)
    print('next month:', next_m)
    print('auto login:', auto_login)
    print('password:', user.password)
    print('username:', user.username)
    print('key_url:', key_url)
    
    api_key = get_api_key()
    print('time1:', t1)
    print('time2:', t2)
    
    if '#' in key_url:
        key_url = key_url.split('#')[0]
    
    refresh = float(refresh)
    current = [' ']
    driver = SuperDriver()
    proxy_port = get_free_port()
    ddd = False
    
    if config.link:
        ddd = True
        vless_link = config.link
        try:
            parsed = parse_link(vless_link)
            v2_config = build_config(parsed, proxy_port)
            v2_process, config_path = start_v2ray(v2_config)
            
            try:
                ip = get_ip(proxy_port)
                print('your ip:', ip)
            except Exception as e:
                print(f"خطا در دریافت IP: {e}")
        except Exception as e:
            print(f"خطا در راه‌اندازی v2ray: {e}")
            ddd = False
    
    try:
        if browser == 'Chrome':
            options = ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_driver_path = 'chromedriver.exe'
            options.page_load_strategy = 'eager'
            options.add_argument('--disable-webrtc')
            
            if ddd:
                option_with_proxy(option=options, proxy_port=proxy_port)
            
            service = Service(chrome_driver_path)
            driver.d = webdriver.Chrome(service=service, options=options)
        
        elif browser == 'Firefox':
            options = FirefoxOptions()
            options.page_load_strategy = 'eager'
            options.add_argument('--disable-webrtc')
            
            if ddd:
                options.set_preference('network.proxy.type', 1)
                options.set_preference('network.proxy.socks', '127.0.0.1')
                options.set_preference('network.proxy.socks_port', int(proxy_port))
                options.set_preference('network.proxy.socks_version', 5)
                options.set_preference('network.proxy.socks_remote_dns', True)
            
            driver.d = webdriver.Firefox(options=options)
        
        elif browser == 'Edge':
            options = EdgeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.page_load_strategy = 'eager'
            options.add_argument('--disable-webrtc')
            
            if ddd:
                option_with_proxy(option=options, proxy_port=proxy_port)
            
            chrome_driver_path = 'msedgedriver.exe'
            service = Service(chrome_driver_path)
            driver.d = webdriver.Edge(service=service, options=options)
        
        elif browser == 'Brave':
            brave_binary_path = find_browser_paths('brave')
            chrome_driver_path = 'chromedriver.exe'
            options = ChromeOptions()
            options.binary_location = brave_binary_path
            options.add_argument('--disable-webrtc')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.page_load_strategy = 'eager'
            
            if ddd:
                option_with_proxy(option=options, proxy_port=proxy_port)
            
            service = Service(chrome_driver_path)
            driver.d = webdriver.Chrome(service=service, options=options)
        
        elif browser == 'Chromium':
            chromium_binary_path = find_browser_paths('chromium')
            chrome_driver_path = 'chromedriver.exe'
            options = ChromeOptions()
            options.binary_location = chromium_binary_path
            options.add_argument('--disable-webrtc')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.page_load_strategy = 'eager'
            
            if ddd:
                option_with_proxy(option=options, proxy_port=proxy_port)
            
            service = Service(chrome_driver_path)
            driver.d = webdriver.Chrome(service=service, options=options)
        
        elif browser == 'Yandex':
            print(browser)
            yandex_binary_path = find_browser_paths('yandex')
            chrome_driver_path = 'yandexdriver.exe'
            options = ChromeOptions()
            options.binary_location = yandex_binary_path
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            service = Service(chrome_driver_path)
            options.page_load_strategy = 'eager'
            options.add_argument('--disable-webrtc')
            
            if ddd:
                option_with_proxy(option=options, proxy_port=proxy_port)
            
            driver.d = webdriver.Chrome(service=service, options=options)
        
        elif browser == 'Opera':
            opera_binary_path = find_browser_paths('opera')
            chrome_driver_path = 'chromedriverr.exe'
            options = ChromeOptions()
            options.binary_location = opera_binary_path
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.page_load_strategy = 'eager'
            options.add_argument('--disable-webrtc')
            
            if ddd:
                option_with_proxy(option=options, proxy_port=proxy_port)
            
            service = Service(chrome_driver_path)
            driver.d = webdriver.Edge(service=service, options=options)
        
        elif browser == 'Vivaldi':
            vivaldi_binary_path = find_browser_paths('vivaldi')
            chrome_driver_path = 'v129\\chromedriver.exe'
            options = ChromeOptions()
            options.binary_location = vivaldi_binary_path
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            service = Service(chrome_driver_path)
            options.page_load_strategy = 'eager'
            options.add_argument('--disable-webrtc')
            
            if ddd:
                option_with_proxy(option=options, proxy_port=proxy_port)
            
            driver.d = webdriver.Chrome(service=service, options=options)
        
        if browser != 'Firefox' and browser != 'Opera':
            try:
                driver.d.execute_cdp_cmd('Network.enable', {})
                driver.d.execute_cdp_cmd('Network.setBlockedURLs', {'urls': ['*openstreetmap.org*', '*leaflet*']})
            except Exception as e:
                print(f"خطا در اجرای CDP commands: {e}")
        
        pi = True
        while pi:
            if auto_login:
                url1 = 'https://nobat.epolice.ir/login'
                driver.d.get(url1)
                wait(driver=driver.d, current=current)
                i = 0
                erxp = '//*[contains(text(), \'اختلال\') and contains(text(), \'سرور\')]'
                
                while i < 3:  # حداکثر 3 بار تلاش برای ورود
                    print(i)
                    i += 1
                    nxt22 = driver.find_el_or_error(By.XPATH, '//button[@class=\'btn btn-block btn-success\'] | //div[@class=\'errorbox\']')
                    
                    if nxt22 == -1:
                        driver.d.refresh()
                        continue
                    
                    usrnminp = driver.get_safe_element(By.NAME, 'username')
                    driver.send_keys(usrnminp, user.username)
                    pasinp = driver.get_safe_element(By.NAME, 'password')
                    driver.send_keys(pasinp, user.password)
                    
                    if ac:
                        cptxt = solve_and_process_captcha(driver=driver, api_key=api_key)
                        delete_pics()
                        inp1 = driver.get_safe_element(By.ID, 'sec_code')
                        driver.send_keys(inp1, cptxt)
                        driver.click(nxt22)
                    
                    w = wait(driver=driver.d, current=current, 
                            flag='//li[contains(text(), \'کد امنیتی درخواست شده اشتباه است\')]', 
                            flag2=erxp)
                    
                    if w == 2 or w == 3:
                        if ac:
                            print(cptxt)
                        driver.d.get(driver.d.current_url)
                        break
                
                cookies = driver.d.get_cookies()
                
                with open('db.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                with open('db.txt', 'w', encoding='utf-8') as file:
                    for line in lines:
                        parts = line.strip().split('###')
                        phone_num = parts[0]
                        
                        if phone_num == user.username:
                            cookies_str = json.dumps(cookies)
                            if len(parts) == 15:
                                line = line.strip() + '###' + cookies_str + '\n'
                                file.write(line)
                            elif len(parts) == 16:
                                parts[-1] = cookies_str
                                line = '###'.join(parts) + '\n'
                                file.write(line)
                        else:
                            if len(parts) == 15:
                                file.write(line.strip() + '###blank\n')
                            elif len(parts) == 16:
                                file.write(line)
                
                print('Cookie file saved')
                pi = False
            
            else:
                driver.d.get('https://nobat.epolice.ir')
                
                with open('db.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    
                    for line in lines:
                        parts = line.strip().split('###')
                        phone_num = parts[0]
                        
                        if phone_num == user.username:
                            if len(parts) == 16:
                                cookies_str = parts[-1]
                                if cookies_str != 'blank':
                                    cookies = json.loads(cookies_str)
                                    for cookie in cookies:
                                        driver.d.add_cookie(cookie)
                                    pi = False
                                else:
                                    auto_login = not auto_login
                            else:
                                auto_login = not auto_login
                            break
                
                print('cookies loaded successfully')
        
        # ادامه عملیات اصلی برنامه...
        # این بخش باید بر اساس نیازهای اصلی برنامه تکمیل شود
        
    except Exception as e:
        print(f"خطا در اجرای برنامه: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            if ddd:
                v2_process.terminate()
                os.unlink(config_path)
        except:
            pass
        
        try:
            if driver.d:
                driver.d.quit()
        except:
            pass

# توابع مربوط به رابط کاربری
def delete_user():
    selected = user_combobox.get()
    if not selected:
        tk.messagebox.showerror('خطا', 'لطفاً یک کاربر را انتخاب کنید.')
        return
    
    username = selected.split(' - ')[0]
    confirm = tk.messagebox.askyesno('تأیید حذف', f'آیا می‌خواهید کاربر {username} را حذف کنید؟')
    if not confirm:
        return
    
    try:
        with open('db.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        with open('db.txt', 'w', encoding='utf-8') as file:
            for line in lines:
                if not line.startswith(username + '###'):
                    file.write(line)
        
        tk.messagebox.showinfo('موفقیت', f'کاربر {username} با موفقیت حذف شد.')
        load_users()
    except FileNotFoundError:
        tk.messagebox.showerror('خطا', 'فایل db.txt پیدا نشد.')
    except Exception as e:
        tk.messagebox.showerror('خطا', f'خطا در حذف کاربر: {str(e)}')

def open_add_user_window():
    main_window.withdraw()
    add_window = tk.Toplevel()
    add_window.title('@Programmer12312')
    
    labels = ['شماره موبایل', 'رمز عبور', 'نام کامل', 'خدمات', 'نوع وسیله', 'بخش 1 پلاک', 'حرف پلاک', 
             'بخش 2 پلاک', 'بخش 3 پلاک', 'پلاک موتور بخش اول', 'پلاک موتور بخش دوم', 'کد شاسی', 
             'نوع خریدار', 'کد ملی خریدار', 'key_url']
    
    username_entry = tk.Entry(add_window, width=40)
    password_entry = tk.Entry(add_window, width=40)
    fullname_entry = tk.Entry(add_window, width=40)
    khedmat_combobox = ttk.Combobox(add_window, width=38)
    khedmat_combobox['values'] = ['نقل و انتقال', 'خدمات کارت وسیله نقلیه(المثنی/عودتی)', 'پلاک المثنی', 
                                  'تغییر کد پلاک مالک (از شهری به شهر دیگر)', 'تعویض ارکان(اتاق، شاسی، موتور و رنگ) وسیله نقلیه', 
                                  'سند مالکیت المثنی', 'اصلاح مشخصات', 'فک رهن', 'پلاک مجازی', 'مزایده ای', 
                                  'نوشماره (تولید داخل / وارداتی)', 'تعویض پلاک سرقتی / پلاک مفقودی']
    khedmat_combobox.set('نقل و انتقال')
    
    vasile_type_combobox = ttk.Combobox(add_window, width=38)
    vasile_type_combobox['values'] = ['سواری شخصی', 'سواری دولتی', 'سواری عمومی', 'وانت شخصی', 'وانت دولتی', 
                                      'وانت عمومی', 'موتور سیکلت', 'تاکسی', 'خودرو سنگین و نیمه سنگین', 'ماشینهای کشاورزی']
    vasile_type_combobox.set('سواری شخصی')
    
    buyer_type_combobox = ttk.Combobox(add_window, width=38)
    buyer_type_combobox['values'] = ['حقیقی', 'حقوقی', 'اتباع خارجی']
    buyer_type_combobox.set('حقیقی')
    
    p1_entry = tk.Entry(add_window, width=40)
    chr_entry = tk.Entry(add_window, width=40)
    p2_entry = tk.Entry(add_window, width=40)
    p3_entry = tk.Entry(add_window, width=40)
    motorp1_entry = tk.Entry(add_window, width=40)
    motorp2_entry = tk.Entry(add_window, width=40)
    shasi_code_entry = tk.Entry(add_window, width=40)
    buyer_nationalcode_entry = tk.Entry(add_window, width=40)
    key_u_e = tk.Entry(add_window, width=40)
    
    entry_widgets = [username_entry, password_entry, fullname_entry, khedmat_combobox, vasile_type_combobox, 
                    p1_entry, chr_entry, p2_entry, p3_entry, motorp1_entry, motorp2_entry, shasi_code_entry, 
                    buyer_type_combobox, buyer_nationalcode_entry, key_u_e]
    
    for i, label in enumerate(labels):
        tk.Label(add_window, text=label).grid(row=i, column=0, padx=5, pady=5)
        entry_widgets[i].grid(row=i, column=1, padx=5, pady=5)
    
    def save_user():
        user = User(
            username=username_entry.get() or 'blank',
            password=password_entry.get() or 'blank',
            fullname=fullname_entry.get() or 'blank',
            khedmat=khedmat_combobox.get() or 'blank',
            vasile_type=vasile_type_combobox.get() or 'blank',
            p1=p1_entry.get() or 'blank',
            chr=chr_entry.get() or 'blank',
            p2=p2_entry.get() or 'blank',
            p3=p3_entry.get() or 'blank',
            motorp1=motorp1_entry.get() or 'blank',
            motorp2=motorp2_entry.get() or 'blank',
            shasi_code=shasi_code_entry.get() or 'blank',
            buyer_type=buyer_type_combobox.get() or 'blank',
            buyer_nationalcode=buyer_nationalcode_entry.get() or 'blank',
            key_url=key_u_e.get() or 'blank'
        )
        user.save_to_file()
        add_window.destroy()
        main_window.deiconify()
        load_users()
    
    save_button = tk.Button(add_window, text='ذخیره', command=save_user)
    save_button.grid(row=len(labels), column=0, columnspan=2, pady=10)

def load_users():
    global users
    users = []
    
    try:
        with open('db.txt', 'r', encoding='utf-8') as file:
            for line in file:
                data = line.strip().split('###')
                if len(data) >= 3:
                    username, fullname = data[0], data[2]
                    users.append((username, fullname, data))
        
        formatted_users = [f'{username} - {fullname}' for username, fullname, _ in users]
        user_combobox['values'] = formatted_users
        if formatted_users:
            user_combobox.set(formatted_users[0])
    except FileNotFoundError:
        print("فایل db.txt یافت نشد. یک فایل جدید ایجاد خواهد شد.")
        with open('db.txt', 'w', encoding='utf-8') as file:
            pass
    except Exception as e:
        print(f"خطا در بارگیری کاربران: {e}")

def open_edit_user_window():
    main_window.withdraw()
    selected = user_combobox.get()
    if not selected:
        tk.messagebox.showerror('خطا', 'لطفاً یک کاربر را انتخاب کنید.')
        return
    
    username = selected.split(' - ')[0]
    user_data = None
    
    try:
        with open('db.txt', 'r', encoding='utf-8') as file:
            for line in file:
                data = line.strip().split('###')
                if data[0] == username:
                    user_data = data
                    break
        
        if not user_data:
            tk.messagebox.showerror('خطا', 'کاربر مورد نظر یافت نشد.')
            return
        
        edit_window = tk.Toplevel()
        edit_window.title('@Programmer12312')
        tk.Label(edit_window, text='ویرایش کاربر').grid(row=0, column=1, padx=5, pady=5)
        
        labels = ['نام کاربری', 'رمز عبور', 'نام کامل', 'خدمات', 'نوع وسیله', 'بخش 1 پلاک', 'حرف پلاک', 
                 'بخش 2 پلاک', 'بخش 3 پلاک', 'پلاک موتور بخش اول', 'پلاک موتور بخش دوم', 'کد شاسی', 
                 'نوع خریدار', 'کد ملی خریدار', 'key_url']
        
        username_entry = tk.Entry(edit_window, width=40)
        username_entry.insert(0, user_data[0])
        
        password_entry = tk.Entry(edit_window, width=40)
        password_entry.insert(0, user_data[1])
        
        fullname_entry = tk.Entry(edit_window, width=40)
        fullname_entry.insert(0, user_data[2])
        
        khedmat_combobox = ttk.Combobox(edit_window, width=38)
        khedmat_combobox['values'] = ['نقل و انتقال', 'خدمات کارت وسیله نقلیه(المثنی/عودتی)', 'پلاک المثنی', 
                                      'تغییر کد پلاک مالک (از شهری به شهر دیگر)', 'تعویض ارکان(اتاق، شاسی، موتور و رنگ) وسیله نقلیه', 
                                      'سند مالکیت المثنی', 'اصلاح مشخصات', 'فک رهن', 'پلاک مجازی', 'مزایده ای', 
                                      'نوشماره (تولید داخل / وارداتی)', 'تعویض پلاک سرقتی / پلاک مفقودی']
        khedmat_combobox.set(user_data[3])
        
        vasile_type_combobox = ttk.Combobox(edit_window, width=38)
        vasile_type_combobox['values'] = ['-- انتخاب کنید', 'سواری شخصی', 'سواری دولتی', 'سواری عمومی', 
                                          'وانت شخصی', 'وانت دولتی', 'وانت عمومی', 'موتور سیکلت', 'تاکسی', 
                                          'خودرو سنگین و نیمه سنگین', 'ماشینهای کشاورزی']
        vasile_type_combobox.set(user_data[4])
        
        buyer_type_combobox = ttk.Combobox(edit_window, width=38)
        buyer_type_combobox['values'] = ['حقیقی', 'حقوقی', 'اتباع خارجی']
        buyer_type_combobox.set(user_data[12])
        
        p1_entry = tk.Entry(edit_window, width=40)
        p1_entry.insert(0, user_data[5])
        
        chr_entry = tk.Entry(edit_window, width=40)
        chr_entry.insert(0, user_data[6])
        
        p2_entry = tk.Entry(edit_window, width=40)
        p2_entry.insert(0, user_data[7])
        
        p3_entry = tk.Entry(edit_window, width=40)
        p3_entry.insert(0, user_data[8])
        
        motorp1_entry = tk.Entry(edit_window, width=40)
        motorp1_entry.insert(0, user_data[9])
        
        motorp2_entry = tk.Entry(edit_window, width=40)
        motorp2_entry.insert(0, user_data[10])
        
        shasi_code_entry = tk.Entry(edit_window, width=40)
        shasi_code_entry.insert(0, user_data[11])
        
        buyer_nationalcode_entry = tk.Entry(edit_window, width=40)
        buyer_nationalcode_entry.insert(0, user_data[13])
        
        key_u_e = tk.Entry(edit_window, width=40)
        if len(user_data) == 14:
            user_data.append('blank')
        key_u_e.insert(0, user_data[14])
        
        entry_widgets = [username_entry, password_entry, fullname_entry, khedmat_combobox, vasile_type_combobox, 
                        p1_entry, chr_entry, p2_entry, p3_entry, motorp1_entry, motorp2_entry, shasi_code_entry, 
                        buyer_type_combobox, buyer_nationalcode_entry, key_u_e]
        
        for i, label in enumerate(labels):
            tk.Label(edit_window, text=label).grid(row=i + 1, column=0, padx=5, pady=5)
            entry_widgets[i].grid(row=i + 1, column=1, padx=5, pady=5)
        
        def save_edits():
            new_data = [
                username_entry.get(), 
                password_entry.get(), 
                fullname_entry.get(), 
                khedmat_combobox.get() if khedmat_combobox.get() != 'انتخاب نوع خدمت' else 'blank', 
                vasile_type_combobox.get() or 'blank', 
                p1_entry.get() or 'blank', 
                chr_entry.get() or 'blank', 
                p2_entry.get() or 'blank', 
                p3_entry.get() or 'blank', 
                motorp1_entry.get() or 'blank', 
                motorp2_entry.get() or 'blank', 
                shasi_code_entry.get() or 'blank', 
                buyer_type_combobox.get() or 'blank', 
                buyer_nationalcode_entry.get() or 'blank', 
                key_u_e.get() or 'blank'
            ]
            
            try:
                with open('db.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                with open('db.txt', 'w', encoding='utf-8') as file:
                    for line in lines:
                        data = line.strip().split('###')
                        if data[0] == username:
                            file.write('###'.join(new_data) + '\n')
                        else:
                            file.write(line)
                
                tk.messagebox.showinfo('موفقیت', 'اطلاعات کاربر با موفقیت ویرایش شد.')
                edit_window.destroy()
                main_window.deiconify()
                load_users()
            except FileNotFoundError:
                tk.messagebox.showerror('خطا', 'فایل db.txt پیدا نشد.')
            except Exception as e:
                tk.messagebox.showerror('خطا', f'خطا در ویرایش اطلاعات: {str(e)}')
        
        save_button = tk.Button(edit_window, text='ذخیره تغییرات', command=save_edits)
        save_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10)
    
    except FileNotFoundError:
        tk.messagebox.showerror('خطا', 'فایل db.txt پیدا نشد.')
    except Exception as e:
        tk.messagebox.showerror('خطا', f'خطا در باز کردن پنجره ویرایش: {str(e)}')

def execute_function():
    selected_objects = []
    selected_config = config_combobox.get()
    
    if selected_config:
        configs = load_configs_from_file()
        for obj in configs:
            if obj.name == selected_config:
                selected_objects.append(obj)
                break
    else:
        c = Config(name='', link='')
        selected_objects.append(c)
    
    selected = user_combobox.get()
    if not selected:
        tk.messagebox.showerror('خطا', 'لطفاً یک کاربر را انتخاب کنید.')
        return
    
    username = selected.split(' - ')[0]
    next_m = next_month_var.get()
    autologin = auto_login_var.get()
    ac = ac_var.get()
    user_data = None
    
    for user in users:
        if user[0] == username:
            user_data = user[2]
            break
    
    if not user_data:
        tk.messagebox.showerror('خطا', 'اطلاعات کاربر یافت نشد.')
        return
    
    t1 = t1_entry.get()
    t2 = t2_entry.get()
    d = d_entry.get()
    
    print(user_data[0:15])
    user = User(*user_data[0:15])
    browser = browser_var.get()
    refresh_time = refresh_entry.get() or 0
    key_url = user.key_url
    
    main_window.destroy()
    F(user=user, browser=browser, refresh=refresh_time, key_url=key_url, t1=t1, t2=t2, day=d, 
      next_m=next_m, auto_login=autologin, config=selected_objects[0], ac=ac)

def load_configs_from_file():
    configs = []
    try:
        with open('configs.txt', 'r', encoding='utf-8') as file:
            for line in file:
                data = line.strip().split('###')
                if len(data) == 2:
                    configs.append(Config(*data))
        return configs
    except FileNotFoundError:
        messagebox.showerror('Error', 'File configs.txt not found.')
        return []

def update_config_combobox():
    configs = load_configs_from_file()
    config_combobox['values'] = [obj.name for obj in configs]
    if config_combobox['values']:
        config_combobox.set(config_combobox['values'][0])

# بخش اصلی برنامه
if __name__ == "__main__":
    print('Created By Hosein')
    print('Telegram Id : @Programmer12312')
    print('-------------------------------------------------------')
    print('agar robot ra az id digari daryaft kardid hatman be @Programmer12312 payam bedid\n vagarna agar robot block va ghat shod avaghebesh paye khodeton')
    print('-------------------------------------------------------')
    
    end_date = datetime.datetime(2099, 9, 4, 23)
    print('Checking License...')
    free = False
    r = 'CD51AAF5-9192-11E2-9673-CE39E71C7C0B'
    
    # لیست UUIDهای مجاز
    allowed_sys = [
        '89E0B542-57EC-11EC-80F0-84A938FC77FF', 'B422BE7D-FBC0-69CE-089D-1CB72CAC6DE7', 
        '5D93B274-B069-40F4-9271-FC5CEE106B3D', '4C4C4544-004B-4810-8032-B1C04F594D32', 
        '4C4C4544-0030-4A10-8043-B3C04F513133', '26E07A96-A8DA-11E5-9C43-BC00001C0000', 
        'DD411610-9D8C-81E4-2A67-08626613FA1F', '6B28F035-D311-C1E2-5C0C-382C4A649803', 
        '8C7040AD-1C94-F63A-DF73-04D4C4A9FDCE', '4711A536-0DE6-2355-66BF-04D4C4A9F8F3', 
        '4C4C4544-0036-4D10-8032-B3C04F344D32', '7C512D2C-0A08-CA42-B24F-F07959860E3A', 
        'A918E3FB-1040-D4CE-3C9A-D92B0C6B6D10', 'A9F1E34F-73F9-11E8-8000-4A907601A0DA', 
        '01625CFF-54C5-11E9-9C43-BC0000040000', '0112D795-EB4F-CB11-A2CD-E2F80206F31C', 
        '3FA93AEF-63F7-11ED-80F3-9C2DCDE64EC8', '03560274-043C-05C4-6B06-C10700080009', 
        'A643BFF6-7FF7-E311-981C-F8A9633D4496', 'C085E952-8C7E-F04A-B57B-0C0AD43046B8', 
        '5DF01C00-BB67-11E4-A13C-8CDCD426AD12', 'F4A634FF-D575-11E3-9078-5634120000FF', 
        '2EAADEFA-D2B4-11E5-9C43-BC0000FE0000', '2B4E364F-64CA-EB11-80C1-E4A8DFFFA32D', 
        'A913E97F-7B88-11E3-87D1-6287E803C0FF', '991B0994-5688-30B4-F17F-6DEBD7A3335D', 
        '513360D7-1D3E-4182-9089-D35E08073701', '99C28570-B4F3-0000-0000-000000000000', 
        'EF8C597F-A874-11E6-9C43-BC0000040000', '91DD42B5-9122-0E21-BE42-E03F494512DF', 
        'AEDB799F-2BC5-11E6-B43F-8A5873014069', '97F62C4B-57AB-E311-803E-F8A963043FDC', 
        'BE70FE7E-21D0-11E7-BFB0-2A0E72010001', 'AEF24440-D74B-11DD-878F-544249FF04FE', 
        '4C4C4544-0042-3310-8047-C8C04F515132', 'A57F3F07-0A6C-52B6-99DA-DABCE26B5291', 
        '03AA02FC-0414-0530-6206-DA0700080009', '7314A61C-DBC7-11E2-B543-94CC7201006A', 
        '8F69520A-4340-56BB-6F97-2228DA97686B', '4C4C4544-004C-5810-8059-C2C04F584D32', 
        '5DEADA38-FC15-CC2D-CA77-C10D4A0B6AB8', 'A389A914-29C6-4743-AAD8-D150246AAD12', 
        'BFF390DC-359B-944F-AA4E-794C2536FD9F', '61B2F5B1-3570-CBFF-6D33-50EBF6238E1C', 
        '03D40274-0435-0558-E206-D60700080009', '4C4C4544-0048-4810-8037-CAC04F503332', 
        '73A738EC-0B52-11E7-9C43-BC0000700000', '62A53B85-5ACE-11E5-90AB-1C394715A1DB', 
        '57389552-7317-464E-85CF-363503C42A9C', '89DD7C00-75F4-11E2-A5A7-9C8E99F4A11C', 
        '00C78645-4FB2-E611-8155-C85947128362', '6E213C1D-AA45-285C-8011-9B71ADD2B9D7', 
        '77302A72-FCC1-6FAF-8085-23C4FCE7D27B', '73B043E1-1E76-DFE8-5B1F-B67B19DA209D', 
        '83AE96A0-D7DA-11DD-9C06-10C37B919BA8', '84F9ED4C-759A-6FC4-80CC-7824AF35E500', 
        'A643BFF6-7FF7-E311-981C-F8A9633D4496', '4ADBA9C3-5D30-A649-8BC0-C6AF5B978F8D', 
        '7F917C00-FE8D-11D5-BE4F-BCAEC5CC4A64', '0D392533-5570-E411-B2A0-D0BF9C0712DD', 
        '32B6DB8D-C84C-5E1A-A0D2-D843AECDA434', '4C4C4544-0042-5910-8039-B5C04F484A32', 
        'FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF', '03C00218-044D-05C0-BC06-7A0700080009', 
        '53F7F380-3925-11E5-9548-ECB1D7534844', 'E676445E-EB0A-11E5-B23B-44987A01C060', 
        'BD600000-C7DD-11E0-0000-3CD92B680770', 'F5619A00-96DD-11E3-A566-A0481C79AA82', 
        'E52ADC00-5124-11E2-8E1C-10604B710D2D', 'E1F38500-8DFE-11E4-8EBD-C4346B703A0C', 
        '9822EFCD-FEB1-2018-0920-182339000000', '3ECB64F3-8540-F5F8-3427-230C92095BFF', 
        '031B021C-040D-05B6-1006-A60700080009', '4C4C4544-0057-5610-8032-B3C04F565931', 
        'A4FC4E00-B7DE-11E6-BD36-A3C7874FED01', '3BF559FF-00D4-11E5-9514-4013280000FF', 
        '350BAB00-D7DA-11DD-ADE3-0862664D6C53', 'AECC4BB8-F2EE-11E3-A60D-9DD1D1671C00', 
        'CBFF947B-4680-462C-D308-203BB07FD73F', 'C085E952-8C7E-F04A-B578-0C0AD43046B8', 
        '4C4C4544-0046-5110-8030-B2C04F5A3732', 'DF7DA940-FE91-11E0-9E57-5404A62B15BF', 
        '4C4C4544-0043-3310-8042-C7C04F484432', '21ECEFBF-3429-274B-D9C2-107C614596C0', 
        '20885D00-CA7B-11DF-B499-922356508F15', 'AA4CCFCB-DC00-1F8B-E874-60CF84CB5D90', 
        '4C4C4544-004B-3610-804E-B5C04F563532', 'E1F38500-8DFE-11E4-8EBD-C4346B703A0C', 
        '4C4C4544-0047-5A10-8056-B6C04F314E32', '03DE0294-0480-058F-D906-C80700080009', 
        'DB990C01-76CA-C48A-E1BA-24937D1CA051', 'E73D95B1-237D-E01D-A3DB-3B47E3FB714D', 
        '724F6532-92E5-56BA-B1EB-C343113E0F83', '26F4EFCF-9A06-7123-AB30-85B509A95188', 
        '40BD353F-E834-11E6-9C43-BC0000440000', 'EF8C597F-A874-11E6-9C43-BC0000040000', 
        '91DD42B5-9122-0E21-BE42-E03F494512DF', '038D0240-045C-0539-F506-A30700080009', 
        'A57F3F07-0A6C-52B6-99DA-DABCE26B5291', '4BAF73AC-191A-11AC-213B-5811220FD9E6', 
        '927F4B00-702A-11E3-B55A-F0921CDC3B10', '4C4C4544-0037-5410-805A-B1C04F594D32', 
        'F4CCB280-4318-11E5-8FE0-ECB1D752DA1D', '9E9D0511-7068-11E3-B042-52C45F06A0F3', 
        'AD2096E7-F0F5-11EB-810C-7C8AE18FDCFD', '9A064AE2-0DF8-0040-88E5-C66550F81E54', 
        '8E819790-7936-81E4-3CAB-F079591B4752', 'AE7F9A44-CF9E-4948-B861-FC5CEEE6EAAF', 
        'A9F1E34F-73F9-11E8-8000-4A907601A0DA', '4C4C4544-0043-4B10-8053-C6C04F435231', 
        '0BE84600-E1EE-19F9-858C-DB28FCBBBFE1', '4C4C4544-0053-4610-8037-B4C04F333632', 
        '6125E640-C368-11DE-92FE-90E6BA903D92', 'F6968B9A-B15F-DF11-90A5-000EA68F75BC', 
        '5AC7F33E-3043-F6C7-411F-C8260D11C852', '08DE63AC-A4BF-2D85-1746-04D4C4A9F8F4', 
        '4B435451-314A-5232-4732-5404A6AAF487', '8C0B8180-0F0B-11E6-8A38-480FCF60A29A', 
        'A918E3FB-1040-D4CE-3C9A-D92B0C6B6D10', '01625CFF-54C5-11E9-9C43-BC0000040000', 
        '0112D795-EB4F-CB11-A2CD-E2F80206F31C', '3FA93AEF-63F7-11ED-80F3-9C2DCDE64EC8', 
        '03560274-043C-05C4-6B06-C10700080009', 'A643BFF6-7FF7-E311-981C-F8A9633D4496', 
        '03000200-0400-0500-0006-000700080009', '5DF01C00-BB67-11E4-A13C-8CDCD426AD12', 
        'F4A634FF-D575-11E3-9078-5634120000FF', 'UUID not found', '2EAADEFA-D2B4-11E5-9C43-BC0000FE0000', 
        '2B4E364F-64CA-EB11-80C1-E4A8DFFFA32D', 'A913E97F-7B88-11E3-87D1-6287E803C0FF', 
        '991B0994-5688-30B4-F17F-6DEBD7A3335D', '513360D7-1D3E-4182-9089-D35E08073701', 
        'DD411610-9D8C-81E4-2A67-08626613FA1F', '26E07A96-A8DA-11E5-9C43-BC00001C0000', 
        'AEDB799F-2BC5-11E6-B43F-8A5873014069', '97F62C4B-57AB-E311-803E-F8A963043FDC', 
        'BE70FE7E-21D0-11E7-BFB0-2A0E72010001', 'AEF24440-D74B-11DD-878F-544249FF04FE', 
        '7314A61C-DBC7-11E2-B543-94CC7201006A', '8F69520A-4340-56BB-6F97-2228DA97686B', 
        '5DEADA38-FC15-CC2D-CA77-C10D4A0B6AB8', 'A389A914-29C6-4743-AAD8-D150246AAD12', 
        'BFF390DC-359B-944F-AA4E-794C2536FD9F', '61B2F5B1-3570-CBFF-6D33-50EBF6238E1C', 
        '4C4C4544-0048-4810-8037-CAC04F503332', '73A738EC-0B52-11E7-9C43-BC0000700000', 
        '350BAB00-D7DA-11DD-ADE3-0862664D6C53', 'AECC4BB8-F2EE-11E3-A60D-9DD1D1671C00', 
        '4ADBA9C3-5D30-A649-8BC0-C6AF5B978F8D', '7F917C00-FE8D-11D5-BE4F-BCAEC5CC4A64', 
        '0D392533-5570-E411-B2A0-D0BF9C0712DD', '3ECB64F3-8540-F5F8-3427-230C92095BFF', 
        '031B021C-040D-05B6-1006-A60700080009', 'A4FC4E00-B7DE-11E6-BD36-A3C7874FED01', 
        '3BF559FF-00D4-11E5-9514-4013280000FF', '031B021C-040D-05B6-1006-A60700080009', 
        '72C33F80-312B-81E3-3434-D850E61F5081', '4C4C4544-0042-5910-8039-B5C04F484A32', 
        'FF7FA4FF-26AD-5BA9-9E1C-515BF893D689', '00C78645-4FB2-E611-8155-C85947128362', 
        '89DD7C00-75F4-11E2-A5A7-9C8E99F4A11C', 'E309077C-4ABC-D674-C821-E15F9B4E852A', 
        '00000000-0000-0000-0000-1C6F659E5E5F', '00000000-0000-0000-0000-8C89A5CD47C8', 
        '45124B60-45D4-11DC-9DE8-001BFC1ED412', '21ECEFBF-3429-274B-D9C2-107C614596C0', 
        '20885D00-CA7B-11DF-B499-922356508F15', 'AA4CCFCB-DC00-1F8B-E874-60CF84CB5D90', 
        '4C4C4544-004B-3610-804E-B5C04F563532', 'E1F38500-8DFE-11E4-8EBD-C4346B703A0C', 
        '9822EFCD-FEB1-2018-0920-182339000000', 'C1382442-0A1D-B823-172A-2FFBBA497DF6', 
        '5C9E289E-A2C0-1A47-9EB8-EADAA35A9AD8', '18100354-8AE4-D84F-9C0A-74974C91DBF5', 
        '8B0A03A7-1BF8-9911-0881-AC220B80A500', 'A66DF0C3-C1E7-E111-B6EE-000EA68F75B9', 
        '00607342-EBDD-E711-814E-C85A48082304', 'C0D8DC6E-03F9-E411-A26A-480FCFDF6329', 
        '7F139E9D-5E1C-AD39-32F9-6045CB839795', '03D502E0-045E-0522-6D06-D30700080009', 
        'B90BB460-72BA-11E3-AD3E-38D547B5DE30', '4C4C4544-0036-5910-8037-CAC04F4E5031', 
        '4C4C4544-0046-5310-8039-B7C04F484432', '03D40274-0435-05E0-9706-D60700080009', 
        'EBB81D52-AEBA-3459-CE58-F5A8F3755868', '32444335-3134-5A30-3139-7C57580E72B9', 
        '017F08F2-30B3-A644-B7AD-9AD798738199', '4C4C4544-004A-4A10-8054-C8C04F464232', 
        '4C4C4544-0046-5110-8030-B2C04F5A3732', '4C4C4544-0042-5210-804A-B2C04F355831', 
        '9935516A-7315-11E3-A321-649B230F501F', '00000000-0000-0000-0000-1C6F6527294A', 
        '6CAF5E39-91AB-5819-9AA3-581122A7F7C7', '2E2860DB-641F-11E6-9078-5634120000E2'
    ]
    
    allowed_sys = set(allowed_sys)
    
    try:
        current_time = get_ntp_datetime()
        if current_time and current_time < end_date:
            print('End Date:', end_date.date())
            print('-------------------------------------------------------')
            
            L = ['db.txt', 'apikey.txt', 'prints.txt', 'v2rayPath.txt', 'configs.txt']
            ensure_files_exist(L)
            delete_pics()
            
            # ایجاد پنجره اصلی
            main_window = tk.Tk()
            main_window.title('@Programmer12312')
            
            browser_var = tk.StringVar()
            selected_user = tk.StringVar()
            USERSSS = []
            
            tk.Label(main_window, text='انتخاب مرورگر:').grid(row=1, column=0, padx=5, pady=5)
            browser_combobox = ttk.Combobox(main_window, textvariable=browser_var, 
                                           values=['Firefox', 'Chromium', 'Opera', 'Edge', 'Chrome', 'Brave', 'Yandex'], 
                                           width=30)
            browser_combobox.grid(row=1, column=1, padx=5, pady=5)
            browser_combobox.set('Chrome')
            
            tk.Label(main_window, text='انتخاب کانفیگ').grid(row=2, column=0, padx=5, pady=5)
            config_combobox = ttk.Combobox(main_window)
            config_combobox.grid(row=2, column=1, padx=5, pady=5)
            update_config_combobox()
            
            tk.Label(main_window, text='refresh rate').grid(row=3, column=0, padx=5, pady=5)
            refresh_entry = tk.Entry(main_window, width=33)
            refresh_entry.grid(row=3, column=1, padx=5, pady=5)
            
            tk.Label(main_window, text='انتخاب کاربر:').grid(row=0, column=0, padx=5, pady=5)
            user_combobox = ttk.Combobox(main_window, width=40)
            user_combobox.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
            load_users()
            
            tk.Label(main_window, text='روز:').grid(row=4, column=0, padx=5, pady=5)
            d_entry = tk.Entry(main_window, width=33)
            d_entry.grid(row=4, column=1, padx=5, pady=5)
            
            tk.Label(main_window, text='زمان1:').grid(row=5, column=0, padx=5, pady=5)
            t1_entry = tk.Entry(main_window, width=33)
            t1_entry.grid(row=5, column=1, padx=5, pady=5)
            
            tk.Label(main_window, text='زمان2:').grid(row=6, column=0, padx=5, pady=5)
            t2_entry = tk.Entry(main_window, width=33)
            t2_entry.grid(row=6, column=1, padx=5, pady=5)
            
            execute_button = tk.Button(main_window, text='run', command=execute_function)
            execute_button.grid(row=9, column=0, columnspan=2, pady=10)
            
            add_user_button = tk.Button(main_window, text='افزودن کاربر', command=open_add_user_window)
            add_user_button.grid(row=10, column=0, columnspan=2, pady=10)
            
            delete_user_button = tk.Button(main_window, text='حذف کاربر', command=delete_user)
            delete_user_button.grid(row=11, column=0, columnspan=2, pady=10)
            
            auto_login_var = tk.BooleanVar(value=True)
            next_month_var = tk.BooleanVar(value=False)
            next_month_checkbox = tk.Checkbutton(main_window, text='چک کردن ماه بعد', variable=next_month_var)
            next_month_checkbox.grid(row=7, column=0, columnspan=2, pady=10)
            
            edit_user_button = tk.Button(main_window, text='ویرایش کاربر', command=open_edit_user_window)
            edit_user_button.grid(row=12, column=0, columnspan=2, pady=10)
            
            ac_var = tk.BooleanVar(value=True)
            ac_checkbox = tk.Checkbutton(main_window, text='حل اتومات کپچا', variable=ac_var)
            ac_checkbox.grid(row=13, column=0, columnspan=2, pady=10)
            
            main_window.mainloop()
        else:
            print('Eshterak tamam shod')
            input()
    except Exception as e:
        print(f"خطا در بررسی لایسنس: {e}")
        input()