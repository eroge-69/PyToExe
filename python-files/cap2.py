
import os
import sys
import subprocess
import time
import threading
import random
import requests
import re
import string
import cv2
import numpy as np
from colorama import init, Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import json
try:
    from termcolor import colored
    COLOR_AVAILABLE = True
except ImportError:
    COLOR_AVAILABLE = False

# Khởi tạo colorama
init()

# Biến toàn cục
successful_accounts = 0
accounts_lock = threading.Lock()

# Hàm kiểm tra và cài đặt thư viện
def check_and_install_libraries():
    print("Đang kiểm tra và cài đặt các thư viện cần thiết...")
    
    required_libraries = {
        "requests": "requests",
        "colorama": "colorama",
        "selenium": "selenium",
        "opencv-python": "cv2",
        "numpy": "numpy",
        "termcolor": "termcolor"
    }
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"], stdout=subprocess.DEVNULL)
    except:
        print("Không tìm thấy pip. Đang cài đặt pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"], stdout=subprocess.DEVNULL)
            print("Đã cài đặt pip thành công.")
        except:
            print("Không thể cài đặt pip. Vui lòng cài đặt pip thủ công và thử lại.")
            sys.exit(1)
    
    for package_name, import_name in required_libraries.items():
        try:
            __import__(import_name)
            print(f"Thư viện {package_name} đã được cài đặt.")
        except ImportError:
            print(f"Đang cài đặt thư viện {package_name}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name], stdout=subprocess.DEVNULL)
                print(f"Đã cài đặt thư viện {package_name} thành công.")
            except:
                print(f"Không thể cài đặt thư viện {package_name}. Vui lòng cài đặt thủ công.")
                sys.exit(1)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("Đang kiểm tra và cài đặt ChromeDriver...")
        try:
            try:
                __import__("webdriver_manager")
            except ImportError:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"], stdout=subprocess.DEVNULL)
                print("Đã cài đặt webdriver-manager thành công.")
            
            service = Service(ChromeDriverManager().install())
            print("Đã cài đặt ChromeDriver thành công.")
        except Exception as e:
            print(f"Lỗi khi cài đặt ChromeDriver: {str(e)}")
            print("Vui lòng cài đặt ChromeDriver thủ công và đảm bảo nó nằm trong PATH.")
    except:
        print("Lỗi khi kiểm tra ChromeDriver.")
    
    print("Đã hoàn tất kiểm tra và cài đặt thư viện.")

check_and_install_libraries()

# API functions for registration
BASE_URL = "https://mail-temp.site/"

def get_domains():
    try:
        response = requests.get(f"{BASE_URL}list_domain.php")
        data = response.json()
        if data.get("success"):
            return data.get("domains", [])
        else:
            print(f"{Fore.RED}Lỗi khi lấy danh sách domain: {data.get('message', 'Lỗi không xác định')}{Style.RESET_ALL}")
            return []
    except Exception as e:
        print(f"{Fore.RED}Lỗi ngoại lệ khi lấy domain: {str(e)}{Style.RESET_ALL}")
        return []

def generate_random_email(domains):
    if not domains:
        return None
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    random_domain = random.choice(domains)
    return f"{random_string}@{random_domain}"

def check_emails(email):
    try:
        response = requests.get(f"{BASE_URL}checkmail.php", params={"mail": email})
        data = response.json()
        if data.get("success"):
            return data.get("emails", [])
        else:
            print(f"{Fore.RED}Lỗi khi kiểm tra email: {data.get('error', 'Lỗi không xác định')}{Style.RESET_ALL}")
            return []
    except Exception as e:
        print(f"{Fore.RED}Lỗi ngoại lệ khi kiểm tra email: {str(e)}{Style.RESET_ALL}")
        return []

def view_email(email_id):
    try:
        response = requests.get(f"{BASE_URL}viewmail.php", params={"id": email_id})
        data = response.json()
        if data.get("success"):
            return data.get("email", {}).get("body", "")
        else:
            print(f"{Fore.RED}Lỗi khi xem email: {data.get('error', 'Lỗi không xác định')}{Style.RESET_ALL}")
            return ""
    except Exception as e:
        print(f"{Fore.RED}Lỗi ngoại lệ khi xem email: {str(e)}{Style.RESET_ALL}")
        return ""

def extract_code(body):
    match = re.search(r'\b\d{6}\b', body)
    return match.group(0) if match else None

def poll_emails(email, timeout=60, poll_interval=5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        emails = check_emails(email)
        if emails:
            for email_data in emails:
                email_id = email_data.get("id")
                if email_id:
                    body = view_email(email_id)
                    code = extract_code(body)
                    if code:
                        print(f"{Fore.GREEN}Tìm thấy mã xác thực: {code}{Style.RESET_ALL}")
                        return code
                    else:
                        print(f"{Fore.YELLOW}Không tìm thấy mã 6 chữ số trong email.{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Chưa có email mới cho {email}. Đang kiểm tra lại...{Style.RESET_ALL}")
        time.sleep(poll_interval)
    print(f"{Fore.RED}Hết thời gian: Không nhận được email mã xác thực trong {timeout} giây.{Style.RESET_ALL}")
    return None

def save_account(email, password):
    with open("capcut.txt", "a", encoding="utf-8") as f:
        f.write(f"{email}|{password}\n")
    print(f"{Fore.GREEN}Đã lưu tài khoản vào capcut.txt: {email} | {password}{Style.RESET_ALL}")

def create_code_template():
    if not os.path.exists("code.png"):
        print(f"{Fore.YELLOW}Không tìm thấy file code.png. Đang tạo mẫu mặc định...{Style.RESET_ALL}")
        try:
            img = np.zeros((50, 200, 3), dtype=np.uint8)
            img.fill(255)
            for i in range(6):
                x = 10 + i * 30
                cv2.rectangle(img, (x, 10), (x + 25, 40), (200, 200, 200), 1)
            cv2.imwrite("code.png", img)
            print(f"{Fore.GREEN}Đã tạo file code.png mẫu thành công.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Lưu ý: Bạn nên thay thế file này bằng ảnh chụp thực tế của ô nhập mã xác thực để cải thiện độ chính xác.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Lỗi khi tạo file code.png: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Vui lòng tạo file code.png thủ công bằng cách chụp ảnh ô nhập mã xác thực.{Style.RESET_ALL}")

def print_colored(message, color=None, prefix=""):
    if COLOR_AVAILABLE and color:
        print(f"{prefix}{colored(message, color)}")
    else:
        print(f"{prefix}{message}")

def print_section_header(title):
    print_colored(f"\n{'=' * 50}\n{title}\n{'=' * 50}", "cyan")

def login_capcut(email, password):
    url = "https://www.capcut.com/passport/web/email/login/"
    querystring = {
        "aid": "348188",
        "account_sdk_source": "web",
        "sdk_version": "2.1.10-tiktok",
        "language": "en",
        "verifyFp": "verify_meuntikm_fXHE8fEo_YALM_4gxG_9gtE_0f115ctfPJpA"
    }
    payload = {
        "mix_mode": "1",
        "email": email,
        "password": password,
        "fixed_mix_mode": "1"
    }
    headers = {
        "host": "www.capcut.com",
        "connection": "keep-alive",
        "appid": "348188",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
        "sec-ch-ua-mobile": "?0",
        "x-tt-passport-csrf-token": "907f222a65fe1f484ee260e4592530fa",
        "store-country-code-src": "uid",
        "store-country-code": "vn",
        "did": "7543425067741529617",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "accept": "application/json, text/javascript",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.capcut.com",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.capcut.com/login",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "cookie": "capcut_locale=en; ug_capcut_locale=en; receive-cookie-deprecation=1; _gcl_au=1.1.1187390508.1756340542; _ga=GA1.1.222103601.1756340542; _clck=1ww06e^2^fyu^0^2066; _tea_web_id=7543425206984050183; ttwid=1%7CjvFAEfqx3tgEjtYHrZRVsj1iSXA8fvkZ3zt3Mn-teEA%7C1756340554%7C3ea1bfb6251315f7a916ecfac7704d7140f1b093fa99ae96d56e9efb0541566c; s_v_web_id=verify_meuntikm_fXHE8fEo_YALM_4gxG_9gtE_0f115ctfPJpA; cookie-consent={%22ga%22:true%2C%22firstparty_analytics%22:true%2C%22version%22:%22v1%22}; _ut=context%253DReferer%2526medium%253DCapCut%2526source%253Dwww.capcut.com%252F%2526channel_from%253Dlocal%2526session_start_url%253Dhttps%253A%252F%252Fwww.capcut.com%252Fsignup; msToken=0lamzYMsh7CMuj3TI5qrywqcKEt9ocIkzAxRs6vgi8eHDycGQyIJL8GL3k1H5QUBkk-gp2rKD5Fi7c2nB_8xjsgMxBKhePeqXYogmQZuodGqTKUxPud1TgsxEExN; passport_csrf_token=907f222a65fe1f484ee260e4592530fa; passport_csrf_token_default=907f222a65fe1f484ee260e4592530fa; msToken=n5YP5XAQnQi_q1c73X9JywEdRWY2vGADRLZoxNO4mw1nlueuuqqjYs3x5575PZnujRgQLwASdnRwLSxKEMrwUowsR4xW7wry1ociobLY7ktPVCcOeIjsErHjsPfP; x_logid=20250828082256EFBC04D20970E139E2CC; _ga_F9J0QP63RB=GS2.1.s1756340541$o1$g1$t1756340580$j44$l0$h0; _clsk=18yxycd%5E1756340581178%5E2%5E0%5En.clarity.ms%2Fcollect"
    }

    print_section_header("LOGIN TO CAPCUT")
    print_colored(f"Attempting to log in with email: {email}", "yellow")
    try:
        response = requests.post(url, data=payload, headers=headers, params=querystring)
        response.raise_for_status()
        print_colored("Login successful!", "green")
        print_colored("Login Response:", "blue")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json(), response.cookies.get_dict()
    except requests.exceptions.RequestException as e:
        print_colored(f"Login failed: {e}", "red")
        return None, None

def get_user_region(cookies):
    url = "https://edit-api-sg.capcut.com/cc/v1/workspace/get_user_workspaces"
    payload = {
        "cursor": "0",
        "count": 100,
        "need_convert_workspace": True
    }
    headers = {
        "host": "edit-api-sg.capcut.com",
        "connection": "keep-alive",
        "appid": "348188",
        "sec-ch-ua-platform": "\"Windows\"",
        "device-time": "1756340588",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
        "sec-ch-ua-mobile": "?0",
        "store-country-code": "vn",
        "loc": "sg",
        "sign-ver": "1",
        "app-sdk-version": "48.0.0",
        "appvr": "5.8.0",
        "tdid": "",
        "store-country-code-src": "uid",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "sign": "397e8ad7d1eb7ee842ec424047176aea",
        "lan": "en",
        "pf": "7",
        "did": "7543425067741529617",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "origin": "https://www.capcut.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.capcut.com/",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "cookie": "; ".join([f"{key}={value}" for key, value in cookies.items()])
    }

    print_section_header("GET USER REGION")
    print_colored("Fetching region information...", "yellow")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        print_colored("Region API Response:", "blue")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        region = None
        if "region" in data:
            region = data["region"]
        elif "data" in data and isinstance(data["data"], dict) and "region" in data["data"]:
            region = data["data"]["region"]
        else:
            def find_region(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "region":
                            return value
                        result = find_region(value)
                        if result:
                            return result
                elif isinstance(obj, list):
                    for item in obj:
                        result = find_region(item)
                        if result:
                            return result
                return None
            region = find_region(data) or "Unknown"
        print_colored(f"Extracted region: {region}", "green")
        return region, cookies
    except requests.exceptions.RequestException as e:
        print_colored(f"Failed to get region: {e}", "red")
        return None, cookies

def update_bio(cookies, description="TRÙM TOOL"):
    url = "https://edit-api-sg.capcut.com/lv/v1/user/update"
    payload = {"description": description}
    headers = {
        "host": "edit-api-sg.capcut.com",
        "connection": "keep-alive",
        "appid": "348188",
        "sec-ch-ua-platform": "\"Windows\"",
        "device-time": "1756342382",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
        "sec-ch-ua-mobile": "?0",
        "store-country-code": "vn",
        "loc": "sg",
        "sign-ver": "1",
        "app-sdk-version": "48.0.0",
        "appvr": "5.8.0",
        "tdid": "",
        "store-country-code-src": "uid",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "sign": "3d3910a71c2da0622d8ff95149275220",
        "lan": "en",
        "pf": "7",
        "did": "7543425206984050183",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "origin": "https://www.capcut.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.capcut.com/",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
        "cookie": "; ".join([f"{key}={value}" for key, value in cookies.items()])
    }

    print_section_header("UPDATE BIO")
    print_colored(f"Updating bio to: {description}", "yellow")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print_colored("Bio updated successfully!", "green")
        print_colored("Update Bio Response:", "blue")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        return response.json()
    except requests.exceptions.RequestException as e:
        print_colored(f"Failed to update bio: {e}", "red")
        return None

def read_accounts():
    accounts = []
    try:
        with open("capcut.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    email, password = line.split("|")
                    accounts.append((email, password))
        print(f"{Fore.GREEN}Đã đọc {len(accounts)} tài khoản từ capcut.txt{Style.RESET_ALL}")
        return accounts
    except FileNotFoundError:
        print(f"{Fore.RED}Không tìm thấy file capcut.txt{Style.RESET_ALL}")
        return []
    except Exception as e:
        print(f"{Fore.RED}Lỗi khi đọc file capcut.txt: {str(e)}{Style.RESET_ALL}")
        return []

def register_capcut(thread_id=0, target_accounts=1, fixed_password=None):
    global successful_accounts  # Moved to the top of the function
    
    print(f"{Fore.CYAN}[Thread {thread_id}] TOOL REG ACC CAPCUT MAIL ẢO BY NGUYỄN ĐÌNH HÙNG{Style.RESET_ALL}")
    
    with accounts_lock:
        if successful_accounts >= target_accounts:
            print(f"{Fore.YELLOW}[Thread {thread_id}] Đã đạt đủ số lượng tài khoản cần tạo ({target_accounts}).{Style.RESET_ALL}")
            return False
    
    domains = get_domains()
    if not domains:
        print(f"{Fore.RED}[Thread {thread_id}] Không có domain khả dụng. Thoát chương trình.{Style.RESET_ALL}")
        return False

    email = generate_random_email(domains)
    if not email:
        print(f"{Fore.RED}[Thread {thread_id}] Không tạo được email. Thoát chương trình.{Style.RESET_ALL}")
        return False

    print(f"{Fore.YELLOW}[Thread {thread_id}] Đã tạo email: {email}{Style.RESET_ALL}")

    options = webdriver.ChromeOptions()
    #options.add_argument("--headless=new")
    options.add_argument("--lang=en-US")
    options.add_experimental_option("prefs", {"intl.accept_languages": "en-US"})
    
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except:
        driver = webdriver.Chrome(options=options)
    
    wait = WebDriverWait(driver, 10)
    
    screenshot_path = f"screenshot_{thread_id}.png"

    try:
        driver.get("https://www.capcut.com/login?enter_from")
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã truy cập trang đăng nhập CapCut{Style.RESET_ALL}")

        email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="signUsername"]')))
        email_input.send_keys(email)
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhập email{Style.RESET_ALL}")

        continue_button = driver.find_element(By.XPATH, '//button[@type="button"]')
        continue_button.click()
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhấn nút tiếp tục sau email{Style.RESET_ALL}")

        password = fixed_password if fixed_password else ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
        password_input.send_keys(password)
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhập mật khẩu{' cố định' if fixed_password else ' ngẫu nhiên'}{Style.RESET_ALL}")

        signup_button = driver.find_element(By.XPATH, '//button[@type="button"]')
        signup_button.click()
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhấn nút đăng ký{Style.RESET_ALL}")

        current_year = 2025
        birth_year = random.randint(current_year - 25, current_year - 18)
        year_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Year"]')))
        year_input.send_keys(str(birth_year))
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhập năm sinh: {birth_year}{Style.RESET_ALL}")

        month_input = driver.find_element(By.XPATH, '(//div[@role="combobox"])[1]')
        month_input.click()
        month_index = random.randint(1, 12)
        month_option = driver.find_element(By.XPATH, f'(//li[@class="lv-select-option"])[{month_index}]')
        month_option.click()
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã chọn tháng sinh: {month_index}{Style.RESET_ALL}")

        day_input = driver.find_element(By.XPATH, '(//span[@class="lv-select-view-selector"])[2]')
        day_input.click()
        day_index = random.randint(1, 28)
        time.sleep(5)
        day_option = driver.find_element(By.XPATH, f'(//li[@class="lv-select-option"])[{day_index}]')
        day_option.click()
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã chọn ngày sinh: {day_index}{Style.RESET_ALL}")

        continue_button = driver.find_element(By.XPATH, '//button[@type="button"]')
        continue_button.click()
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhấn nút tiếp tục{Style.RESET_ALL}")

        print(f"{Fore.YELLOW}[Thread {thread_id}] Đang chờ email mã xác thực...{Style.RESET_ALL}")
        code = poll_emails(email)
        if not code:
            print(f"{Fore.RED}[Thread {thread_id}] Không lấy được mã xác thực.{Style.RESET_ALL}")
            driver.quit()
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            return False

        driver.save_screenshot(screenshot_path)
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã chụp ảnh màn hình để xử lý bằng OpenCV{Style.RESET_ALL}")

        screenshot = cv2.imread(screenshot_path)
        template = cv2.imread("code.png")
        if screenshot is None or template is None:
            print(f"{Fore.RED}[Thread {thread_id}] Lỗi: Không thể tải ảnh chụp màn hình hoặc code.png{Style.RESET_ALL}")
            driver.quit()
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            return False

        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        threshold = 0.8
        if max_val < threshold:
            print(f"{Fore.RED}[Thread {thread_id}] Lỗi: Điểm khớp mẫu ({max_val}) thấp hơn ngưỡng ({threshold}){Style.RESET_ALL}")
            driver.quit()
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            return False

        template_height, template_width = template_gray.shape
        top_left = max_loc
        center_x = top_left[0] + template_width // 2
        center_y = top_left[1] + template_height // 2
        print(f"{Fore.YELLOW}[Thread {thread_id}] Tìm thấy ô nhập mã tại tọa độ trung tâm: ({center_x}, {center_y}){Style.RESET_ALL}")

        actions = ActionChains(driver)
        actions.move_by_offset(center_x, center_y).click().perform()
        actions.reset_actions()
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhấn vào ô nhập mã{Style.RESET_ALL}")

        for digit in code:
            driver.switch_to.active_element.send_keys(digit)
            time.sleep(0.5)
        print(f"{Fore.YELLOW}[Thread {thread_id}] Đã nhập mã xác thực{Style.RESET_ALL}")

        save_account(email, password)

        time.sleep(10)
        try:
            driver.find_element(By.XPATH, '//button[@type="button"]')
            print(f"{Fore.GREEN}[Thread {thread_id}] Đăng ký tài khoản thành công!{Style.RESET_ALL}")
            
            with accounts_lock:
                successful_accounts += 1  # No global declaration needed here
                current_count = successful_accounts
            
            print(f"{Fore.GREEN}[Thread {thread_id}] Đã tạo {current_count}/{target_accounts} tài khoản.{Style.RESET_ALL}")
            
            driver.quit()
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
                print(f"{Fore.YELLOW}[Thread {thread_id}] Đã xóa ảnh màn hình tạm thời{Style.RESET_ALL}")
            return True
        except:
            print(f"{Fore.RED}[Thread {thread_id}] Đăng ký thất bại: Không tìm thấy nút thành công sau 10 giây.{Style.RESET_ALL}")
            driver.quit()
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)
            return False

    except Exception as e:
        print(f"{Fore.RED}[Thread {thread_id}] Lỗi trong quá trình đăng ký: {str(e)}{Style.RESET_ALL}")
        driver.quit()
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        return False

def check_login_worker(thread_id, accounts, results):
    for email, password in accounts:
        print(f"{Fore.CYAN}[Thread {thread_id}] Kiểm tra đăng nhập cho {email}{Style.RESET_ALL}")
        login_response, cookies = login_capcut(email, password)
        with accounts_lock:
            results.append((email, login_response is not None))
        time.sleep(1)

def check_region_worker(thread_id, accounts, results):
    for email, password in accounts:
        print(f"{Fore.CYAN}[Thread {thread_id}] Kiểm tra vùng quốc gia cho {email}{Style.RESET_ALL}")
        login_response, cookies = login_capcut(email, password)
        if login_response and cookies:
            region, _ = get_user_region(cookies)
            with accounts_lock:
                results.append((email, region if region else "Unknown"))
        else:
            with accounts_lock:
                results.append((email, "Login failed"))
        time.sleep(1)

def update_bio_worker(thread_id, accounts, description, results):
    for email, password in accounts:
        print(f"{Fore.CYAN}[Thread {thread_id}] Cập nhật tiểu sử cho {email}{Style.RESET_ALL}")
        login_response, cookies = login_capcut(email, password)
        if login_response and cookies:
            bio_response = update_bio(cookies, description)
            with accounts_lock:
                results.append((email, bio_response is not None))
        else:
            with accounts_lock:
                results.append((email, False))
        time.sleep(1)

def register_thread_worker(thread_id, target_accounts, fixed_password=None):
    global successful_accounts
    while True:
        with accounts_lock:
            if successful_accounts >= target_accounts:
                print(f"{Fore.YELLOW}[Thread {thread_id}] Đã đạt đủ số lượng tài khoản cần tạo ({target_accounts}). Dừng luồng.{Style.RESET_ALL}")
                break
        register_capcut(thread_id, target_accounts, fixed_password)
        time.sleep(3)

def main():
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ████████╗ ██████╗  ██████╗ ██╗         ██████╗ ███████╗ ║
║   ╚══██╔══╝██╔═══██╗██╔═══██╗██║         ██╔══██╗██╔════╝ ║
║      ██║   ██║   ██║██║   ██║██║         ██████╔╝█████╗   ║
║      ██║   ██║   ██║██║   ██║██║         ██╔══██╗██╔══╝   ║
║      ██║   ╚██████╔╝╚██████╔╝███████╗    ██║  ██║███████╗ ║
║      ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝    ╚═╝  ╚═╝╚══════╝ ║
║                                                          ║
║  CAPCUT ACCOUNT CREATOR BY NGUYỄN ĐÌNH HÙNG             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)
    
    create_code_template()
    
    while True:
        print(f"{Fore.CYAN}Chọn chế độ:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1: Đăng ký tài khoản CapCut{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2: Kiểm tra đăng nhập tài khoản CapCut{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3: Kiểm tra vùng quốc gia tài khoản{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}4: Cập nhật tiểu sử bản quyền tài khoản{Style.RESET_ALL}")
        mode = input(f"{Fore.YELLOW}Nhập số chế độ (1-4): {Style.RESET_ALL}")
        if mode in ['1', '2', '3', '4']:
            break
        print(f"{Fore.RED}Chế độ không hợp lệ. Vui lòng chọn từ 1 đến 4.{Style.RESET_ALL}")
    
    if mode == '1':
        try:
            target_accounts = int(input(f"{Fore.YELLOW}Nhập số lượng tài khoản cần tạo: {Style.RESET_ALL}"))
            if target_accounts < 1:
                print(f"{Fore.RED}Số lượng tài khoản phải lớn hơn 0. Sử dụng 1 tài khoản mặc định.{Style.RESET_ALL}")
                target_accounts = 1
        except ValueError:
            print(f"{Fore.RED}Giá trị không hợp lệ. Sử dụng 1 tài khoản mặc định.{Style.RESET_ALL}")
            target_accounts = 1
        
        try:
            num_threads = int(input(f"{Fore.YELLOW}Nhập số luồng cần chạy: {Style.RESET_ALL}"))
            if num_threads < 1:
                print(f"{Fore.RED}Số luồng phải lớn hơn 0. Sử dụng 1 luồng mặc định.{Style.RESET_ALL}")
                num_threads = 1
        except ValueError:
            print(f"{Fore.RED}Giá trị không hợp lệ. Sử dụng 1 luồng mặc định.{Style.RESET_ALL}")
            num_threads = 1
        
        if num_threads > target_accounts:
            print(f"{Fore.YELLOW}Số luồng ({num_threads}) lớn hơn số tài khoản cần tạo ({target_accounts}). Giảm xuống {target_accounts} luồng.{Style.RESET_ALL}")
            num_threads = target_accounts
        
        while True:
            password_choice = input(f"{Fore.YELLOW}Chọn loại mật khẩu (1: Ngẫu nhiên, 2: Cố định): {Style.RESET_ALL}")
            if password_choice in ['1', '2']:
                break
            print(f"{Fore.RED}Lựa chọn không hợp lệ. Vui lòng chọn 1 hoặc 2.{Style.RESET_ALL}")
        
        fixed_password = None
        if password_choice == '2':
            fixed_password = input(f"{Fore.YELLOW}Nhập mật khẩu cố định (ít nhất 8 ký tự): {Style.RESET_ALL}")
            if len(fixed_password) < 8:
                print(f"{Fore.RED}Mật khẩu phải có ít nhất 8 ký tự. Sử dụng mật khẩu ngẫu nhiên thay thế.{Style.RESET_ALL}")
                fixed_password = None
            else:
                print(f"{Fore.GREEN}Sẽ sử dụng mật khẩu cố định: {fixed_password}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}Bắt đầu tạo {target_accounts} tài khoản với {num_threads} luồng...{Style.RESET_ALL}")
        
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=register_thread_worker, args=(i+1, target_accounts, fixed_password))
            threads.append(thread)
            thread.start()
            time.sleep(2)
        
        for thread in threads:
            thread.join()
        
        print(f"{Fore.GREEN}Hoàn thành! Đã tạo {successful_accounts}/{target_accounts} tài khoản.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Các tài khoản đã được lưu vào file capcut.txt{Style.RESET_ALL}")
    
    else:
        accounts = read_accounts()
        if not accounts:
            print(f"{Fore.RED}Không có tài khoản nào để xử lý. Vui lòng chạy chế độ 1 để tạo tài khoản trước.{Style.RESET_ALL}")
            return
        
        try:
            num_threads = int(input(f"{Fore.YELLOW}Nhập số luồng cần chạy: {Style.RESET_ALL}"))
            if num_threads < 1:
                print(f"{Fore.RED}Số luồng phải lớn hơn 0. Sử dụng 1 luồng mặc định.{Style.RESET_ALL}")
                num_threads = 1
        except ValueError:
            print(f"{Fore.RED}Giá trị không hợp lệ. Sử dụng 1 luồng mặc định.{Style.RESET_ALL}")
            num_threads = 1
        
        if num_threads > len(accounts):
            print(f"{Fore.YELLOW}Số luồng ({num_threads}) lớn hơn số tài khoản ({len(accounts)}). Giảm xuống {len(accounts)} luồng.{Style.RESET_ALL}")
            num_threads = len(accounts)
        
        accounts_per_thread = [accounts[i::num_threads] for i in range(num_threads)]
        threads = []
        results = []
        
        if mode == '2':
            print(f"{Fore.CYAN}Bắt đầu kiểm tra đăng nhập {len(accounts)} tài khoản với {num_threads} luồng...{Style.RESET_ALL}")
            for i in range(num_threads):
                thread = threading.Thread(target=check_login_worker, args=(i+1, accounts_per_thread[i], results))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            print(f"{Fore.CYAN}Kết quả kiểm tra đăng nhập:{Style.RESET_ALL}")
            for email, success in results:
                status = "Thành công" if success else "Thất bại"
                print(f"{Fore.YELLOW}{email}: {Fore.GREEN if success else Fore.RED}{status}{Style.RESET_ALL}")
        
        elif mode == '3':
            print(f"{Fore.CYAN}Bắt đầu kiểm tra vùng quốc gia {len(accounts)} tài khoản với {num_threads} luồng...{Style.RESET_ALL}")
            for i in range(num_threads):
                thread = threading.Thread(target=check_region_worker, args=(i+1, accounts_per_thread[i], results))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            print(f"{Fore.CYAN}Kết quả kiểm tra vùng quốc gia:{Style.RESET_ALL}")
            for email, region in results:
                print(f"{Fore.YELLOW}{email}: {Fore.GREEN if region != 'Unknown' and region != 'Login failed' else Fore.RED}{region}{Style.RESET_ALL}")
        
        elif mode == '4':
            description = input(f"{Fore.YELLOW}Nhập tiểu sử muốn cập nhật (nhấn Enter để sử dụng mặc định 'TRÙM TOOL'): {Style.RESET_ALL}")
            if not description:
                description = "TRÙM TOOL"
            print(f"{Fore.GREEN}Sẽ cập nhật tiểu sử thành: {description}{Style.RESET_ALL}")
            
            print(f"{Fore.CYAN}Bắt đầu cập nhật tiểu sử cho {len(accounts)} tài khoản với {num_threads} luồng...{Style.RESET_ALL}")
            for i in range(num_threads):
                thread = threading.Thread(target=update_bio_worker, args=(i+1, accounts_per_thread[i], description, results))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            print(f"{Fore.CYAN}Kết quả cập nhật tiểu sử:{Style.RESET_ALL}")
            for email, success in results:
                status = "Thành công" if success else "Thất bại"
                print(f"{Fore.YELLOW}{email}: {Fore.GREEN if success else Fore.RED}{status}{Style.RESET_ALL}")
    
    input(f"{Fore.YELLOW}Nhấn Enter để thoát...{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Đã hủy chương trình bởi người dùng.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Lỗi không mong muốn: {str(e)}{Style.RESET_ALL}")
    finally:
        for file in os.listdir():
            if file.startswith("screenshot_") and file.endswith(".png"):
                try:
                    os.remove(file)
                    print(f"{Fore.YELLOW}Đã xóa file tạm thời: {file}{Style.RESET_ALL}")
                except:
                    pass
        print(f"{Fore.CYAN}Cảm ơn bạn đã sử dụng tool!{Style.RESET_ALL}")