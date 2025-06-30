import subprocess
import sys
import os
from urllib.parse import urlparse, parse_qs
import datetime
import requests
import random
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to install modules
def install_module(module_name, version=None):
    try:
        __import__(module_name)
        return True
    except ImportError:
        try:
            print(f"Installing module {module_name}...")
            if version:
                subprocess.check_call([sys.executable, "-m", "pip", "install", f"{module_name}=={version}"])
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            print(f"Module {module_name} installed successfully.")
            return True
        except OSError as e:
            print(f"Error installing {module_name}: {e}")
            return False

# Function to check and install required modules
def check_and_install_modules():
    required_modules = [
        ("requests", None),
        ("termcolor", None),
        ("tqdm", None),
        ("bs4", None)
    ]
    missing_modules = []

    for module_name, version in required_modules:
        if not install_module(module_name, version):
            missing_modules.append(module_name)

    if missing_modules:
        print(f"Failed to install the following modules: {', '.join(missing_modules)}.")
        if "termcolor" in missing_modules:
            print("Continuing without termcolor (colors will not be available).")
        else:
            print(f"Install the missing modules manually: pip install {' '.join(missing_modules)}")
            sys.exit(1)

# Importing modules
try:
    from termcolor import colored
    colors_available = True
except ImportError:
    colors_available = False

# Function to format text
def print_styled(text, style='normal', color=None, end='\n'):
    if colors_available and style != 'normal':
        if style == 'header':
            text = colored(text, 'cyan', attrs=['bold'])
        elif style == 'error':
            text = colored(text, 'red')
        elif style == 'info':
            text = colored(text, 'yellow', attrs=['bold']) if color is None else colored(text, color, attrs=['bold'])
        elif style == 'success':
            text = colored(text, 'green', attrs=['bold'])
    else:
        if style == 'header':
            text = f"===== {text} ====="
        elif style == 'error':
            text = f"[ERROR] {text}"
        elif style == 'info':
            text = f"[INFO] {text}"
        elif style == 'success':
            text = f"[SUCCESS] {text}"
    print(text, end=end)
    sys.stdout.flush()

# Function to color the "Max. devices" line
def print_max_connections(max_connections):
    try:
        max_conn = int(max_connections)
        text = f"Maximum number of devices: {max_conn}"
        prefix = "├● "
        if colors_available:
            if max_conn > 2:
                print(f"{prefix}{colored(text, 'green')}")
            elif max_conn == 2:
                print(f"{prefix}{colored(text, 'yellow')}")
            else:
                print(f"{prefix}{text}")
        else:
            print(f"{prefix}{text}")
    except:
        print(f"├● Maximum number of devices: {max_connections}")

# Function to save results to a file (only for max_connections >= 2)
def save_to_file(m3u_url, user_info, username, password, server, filename, categories):
    try:
        max_connections = int(user_info.get('max_connections', '0'))
        if max_connections < 1:
            return  # Skip saving if max_connections < 2

        hits_dir = "/storage/emulated/0/hits"
        if not os.path.exists(hits_dir):
            os.makedirs(hits_dir)
        
        with open(filename, 'a', encoding='utf-8') as f:
            # Section header
            f.write("🔥 IPTV Premium Report 🔥\n")
            f.write("=" * 60 + "\n")
            f.write(f"📡 M3U Link: {m3u_url}\n")
            status = "✅ 𝐀𝐂𝐓𝐈𝐕𝐄" if user_info.get('status') == "Active" else "❌ 𝐍𝐎𝐓 𝐀𝐂𝐓𝐈𝐕𝐄"
            f.write(f"🌐 Status: {status}\n")
            f.write(f"🔄 Current connections: {user_info.get('active_cons', '0')}\n")
            f.write(f"📊 Maximum number of devices: {user_info.get('max_connections', '0')}\n")
            f.write(f"📅 Expiry date: {format_expiry_date(user_info.get('exp_date', '0'))}\n")
            f.write(f"👤 Username: {username}\n")
            f.write(f"🔒 Password: {password}\n")
            f.write(f"🌍 Server: {server}\n")
            f.write("-" * 60 + "\n")
            f.write("📺 Channel categories:\n")
            if categories:
                for category in categories:
                    f.write(f"  ➤ {category.get('category_name', 'Unknown')}\n")
            else:
                f.write("  ➤ No data\n")
            f.write("=" * 60 + "\n\n")
        print_styled(f"Results saved to file: {filename}", 'success')
    except Exception as e:
        print_styled(f"Error saving to file: {e}", 'error')

# Function to parse M3U URL
def parse_m3u_url(m3u_url):
    try:
        parsed_url = urlparse(m3u_url)
        if not parsed_url.scheme:
            m3u_url = 'http://' + m3u_url
            parsed_url = urlparse(m3u_url)
        query_params = parse_qs(parsed_url.query)
        username = query_params.get('username', [None])[0]
        password = query_params.get('password', [None])[0]
        if parsed_url.port is None:
            port = '80' if parsed_url.scheme == 'http' else '443'
        else:
            port = str(parsed_url.port)
        server = f"{parsed_url.scheme}://{parsed_url.hostname}:{port}"
        if not username or not password:
            print_styled("Failed to extract username or password from URL.", 'error')
            return None, None, None
        return server, username, password
    except Exception as e:
        print_styled(f"Error parsing M3U URL: {e}", 'error')
        return None, None, None

# Function returning headers simulating OTT Player on Android
def get_ott_player_headers():
    return {
        "User-Agent": "OTTPlayer/4.0.2 (Android 13; arm64-v8a; SM-G990B)",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "X-Requested-With": "com.ottplayermobile",
        "Referer": "https://ottplayer.tv/",
        "X-OTT-Device-ID": f"android_{random.randint(1000000000, 9999999999)}",
        "X-OTT-Version": "4.0.2",
        "X-OTT-Platform": "android",
        "Content-Type": "application/json; charset=UTF-8",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    }

# Function to fetch proxy list from vakhov/fresh-proxy-list
def get_proxy_list():
    allowed_countries = {'PL': 'Poland', 'GB': 'United Kingdom', 'DE': 'Germany', 'NL': 'Netherlands', 'US': 'United States', 'SE': 'Sweden', 'BE': 'Belgium'}
    proxy_list = []
    sources = [
        "https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt"
    ]

    def fetch_proxy_source(source):
        proxies = []
        try:
            response = requests.get(source, timeout=5)
            response.raise_for_status()
            lines = response.text.splitlines()
            for line in lines:
                if ':' in line:
                    ip_port = line.strip()
                    proxies.append(ip_port)
            return proxies
        except OSError as e:
            print_styled(f"Error fetching proxies from {source}: {e}", 'error')
            return []

    print_styled("Fetching proxy list...", 'info')
    with ThreadPoolExecutor(max_workers=1) as executor:
        future_to_source = {executor.submit(fetch_proxy_source, source): source for source in sources}
        pbar = tqdm(total=len(sources), desc="Proxy sources", unit="source", dynamic_ncols=True, bar_format="{desc}: {percentage:3.0f}% |{n}/{total}|", mininterval=0.1)
        for future in as_completed(future_to_source):
            proxy_list.extend(future.result())
            pbar.update(1)
        pbar.close()

    # Remove duplicates
    proxy_list = list(set(proxy_list))
    
    print_styled(f"Fetched {len(proxy_list)} proxies.", 'success')
    return proxy_list

# Function to test if a proxy is working (parallel GET test on httpbin.org)
def test_proxy(proxy, local_ip):
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=5, headers=get_ott_player_headers())
        if response.status_code == 200:
            proxy_ip = response.json().get('origin')
            if proxy_ip != local_ip:  # Proxy works if IP is different from local
                country, ip = get_ip_info(proxy)
                if country != "Unknown" and ip != "Unknown":
                    return True
        return False
    except:
        return False

# Function to load saved proxies from a file
def load_saved_proxies():
    proxy_file = os.path.join(os.path.dirname(__file__), "saved_proxies.txt")
    saved_proxies = []
    try:
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r', encoding='utf-8') as f:
                saved_proxies = [line.strip() for line in f if line.strip()]
            print_styled(f"Loaded {len(saved_proxies)} saved proxies from file.", 'info')
    except Exception as e:
        print_styled(f"Error loading saved proxies: {e}", 'error')
    return saved_proxies[:30]  # Limit to max 30

# Function to save working proxies to a file
def save_proxies(proxies):
    proxy_file = os.path.join(os.path.dirname(__file__), "saved_proxies.txt")
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(proxy_file), exist_ok=True)
        with open(proxy_file, 'w', encoding='utf-8') as f:
            for proxy in proxies:
                f.write(f"{proxy}\n")
        print_styled(f"Updated saved_proxies.txt with {len(proxies)} proxies.", 'success')
    except Exception as e:
        print_styled(f"Error saving proxies to file: {e}", 'error')

# Function to get working proxies (checks saved ones, fetches new ones if needed)
def get_working_proxies():
    proxy_list = get_proxy_list()
    working_proxies = []
    local_ip = requests.get("https://ipinfo.io/json", timeout=5).json().get('ip')

    # Load saved proxies
    saved_proxies = load_saved_proxies()

    if saved_proxies:
        print_styled("Checking saved proxies...", 'info')
        sys.stdout.flush()

        # Test saved proxies
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_proxy = {executor.submit(test_proxy, proxy, local_ip): proxy for proxy in saved_proxies}
            with tqdm(total=len(saved_proxies), desc="Testing saved proxies", unit="proxy", dynamic_ncols=True, bar_format="{desc}: {percentage:3.0f}% |{n}/{total}|", mininterval=0.1) as pbar:
                for future in as_completed(future_to_proxy):
                    proxy = future_to_proxy[future]
                    pbar.update(1)
                    try:
                        if future.result():
                            working_proxies.append(proxy)
                            print(f"\033[1B\rFound working proxies: {len(working_proxies)}/30\033[1A", end="")
                            sys.stdout.flush()
                    except:
                        continue
        print("\033[1B")

        if len(working_proxies) == 30:
            print_styled("All saved proxies are working. Proceeding.", 'success', end='\n')
            return working_proxies

    # If not enough proxies, fetch new ones
    needed_proxies = 30 - len(working_proxies)
    print_styled(f"Found {len(working_proxies)} working proxies.", 'info', end='\n')
    print_styled(f"Searching for {needed_proxies} new proxies...", 'info', end='\n')

    # Remove already tested proxies from the list
    proxy_list = [p for p in proxy_list if p not in saved_proxies]

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy, local_ip): proxy for proxy in proxy_list}
        with tqdm(total=len(proxy_list), desc="Testing new proxies", unit="proxy", dynamic_ncols=True, bar_format="{desc}: {percentage:3.0f}% |{n}/{total}|", mininterval=0.1) as pbar:
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                pbar.update(1)
                try:
                    if future.result():
                        working_proxies.append(proxy)
                        print(f"\033[1B\rFound working proxies: {len(working_proxies)}/30\033[1A", end="")
                        sys.stdout.flush()
                        if len(working_proxies) >= 30:
                            pbar.close()
                            executor.shutdown(wait=False, cancel_futures=True)
                            break
                except:
                    continue
    print("\033[1B")

    if len(working_proxies) < 30:
        print_styled(f"Found only {len(working_proxies)} working proxies. 30 are required. Program terminated.", 'error', end='\n')
        sys.exit(1)

    working_proxies = working_proxies[:30]  # Limit to exactly 30
    print_styled(f"Found {len(working_proxies)} working proxies.", 'success', end='\n')

    # Save working proxies to file
    save_proxies(working_proxies)

    return working_proxies

# Function to get IP information
def get_ip_info(proxy=None):
    try:
        jitter = random.uniform(0.2, 0.5)
        time.sleep(jitter + 1)
        headers = get_ott_player_headers()
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"} if proxy else None
        response = requests.get("http://ip-api.com/json/", headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            return data.get('countryCode', 'Unknown'), data.get('query', 'Unknown')
        return "Unknown", "Unknown"
    except:
        return "Unknown", "Unknown"

# Function to fetch account info and categories using a proxy
def get_account_info(server, username, password, proxy):
    try:
        jitter = random.uniform(0.5, 1.5)
        time.sleep(jitter)
        headers = get_ott_player_headers()
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        
        # Fetch user information
        api_url = f"{server}/player_api.php?username={username}&password={password}&action=user_info"
        response = requests.get(api_url, headers=headers, proxies=proxies, verify=False, timeout=10)
        user_info = None
        if response.status_code == 200:
            user_info = response.json()
        
        # Fetch channel categories
        categories = []
        api_url = f"{server}/player_api.php?username={username}&password={password}&action=get_live_categories"
        response = requests.get(api_url, headers=headers, proxies=proxies, verify=False, timeout=10)
        if response.status_code == 200:
            categories = response.json()
        
        if user_info:
            return user_info, categories
        
        # If player_api fails, try panel_api for user_info
        api_url = f"{server}/panel_api.php?username={username}&password={password}&action=user_info"
        response = requests.get(api_url, headers=headers, proxies=proxies, verify=False, timeout=10)
        if response.status_code == 200:
            user_info = response.json()
        
        return user_info, categories
    except:
        return None, []

# Function to format date
def format_expiry_date(timestamp):
    try:
        if timestamp == "null" or timestamp == "0":
            return "Unlimited"
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "Unknown"

# Function to load M3U URLs from a file
def load_m3u_urls_from_file():
    m3u_dir = "/storage/emulated/0/M3U"
    try:
        if not os.path.exists(m3u_dir):
            print_styled(f"Directory {m3u_dir} does not exist. Create the directory and place text files with M3U links in it.", 'error')
            return []

        txt_files = [f for f in os.listdir(m3u_dir) if f.endswith('.txt')]
        if not txt_files:
            print_styled(f"No text files found in directory {m3u_dir}.", 'error')
            return []

        print_styled("Available text files in M3U directory:", 'header')
        for i, file_name in enumerate(txt_files, 1):
            print(f"{i}. {file_name}")
        print_styled("Select the file number (or enter 0 to exit): ", 'info')
        
        while True:
            try:
                choice = int(input().strip())
                if choice == 0:
                    return []
                if 1 <= choice <= len(txt_files):
                    selected_file = txt_files[choice - 1]
                    break
                else:
                    print_styled("Invalid number. Choose a number from the list.", 'error')
            except ValueError:
                print_styled("Enter a valid number.", 'error')

        file_path = os.path.join(m3u_dir, selected_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            m3u_urls = [line.strip() for line in f if line.strip()]
        
        if not m3u_urls:
            print_styled(f"File {selected_file} is empty.", 'error')
            return []
        
        print_styled(f"Loaded {len(m3u_urls)} links from file {selected_file}.", 'success')
        return m3u_urls

    except Exception as e:
        print_styled(f"Error loading file: {e}", 'error')
        return []

# Function to check a single IPTV link with a proxy
def check_iptv(m3u_url, filename, working_proxies):
    server, username, password = parse_m3u_url(m3u_url)
    if not server or not username or not password:
        print_styled("Failed to parse M3U URL. Check the format.", 'error')
        return False

    attempts = 0
    max_attempts = 3
    used_proxies = []

    while attempts < max_attempts:
        if not working_proxies:
            print_styled("No working proxies available.", 'error')
            return False
        
        # Choose a random proxy not yet used for this link
        available_proxies = [p for p in working_proxies if p not in used_proxies]
        if not available_proxies:
            print_styled("Exhausted all available proxies for this link.", 'error')
            return False
        
        proxy = random.choice(available_proxies)
        used_proxies.append(proxy)
        
        country, ip = get_ip_info(proxy)
        if country == "Unknown" or ip == "Unknown":
            print_styled(f"Skipping proxy {proxy}: IP or country unknown.", 'error')
            continue
        
        attempts += 1
        print_styled(f"Attempt {attempts}/{max_attempts} with proxy: {proxy}", 'info')
        print_styled(f"Current IP: {ip}, Country: {country}", 'info')

        account_info, categories = get_account_info(server, username, password, proxy)
        if not account_info:
            print_styled(f"Attempt {attempts}/{max_attempts}: Failed", 'error')
            continue

        try:
            user_info = account_info.get('user_info', {})
            status = "💚 𝐀𝐂𝐓𝐈𝐕𝐄" if user_info.get('status') == "Active" else "💔 𝐍𝐎�{T 𝐀𝐂𝐓𝐈𝐕𝐄"
            print_styled(f"Attempt {attempts}/{max_attempts}: Success", 'success')
            print_styled("IPTV account information:", 'header')
            print(f"╭● Status: {status}")
            print(f"├● Current connections: {user_info.get('active_cons', '0')}")
            print_max_connections(user_info.get('max_connections', '0'))
            print(f"├● Expiry date: {format_expiry_date(user_info.get('exp_date', '0'))}")
            print(f"├● Username: {username}")
            print(f"├● Password: {password}")
            print(f"├● Server: {server}")
            print(f"╰● Country: {country}")
            
            save_to_file(m3u_url, user_info, username, password, server, filename, categories)
            return True
        except Exception as e:
            print_styled(f"Attempt {attempts}/{max_attempts}: Failed", 'error')
            continue
    
    print_styled(f"Failed to check link after {max_attempts} attempts.", 'error')
    return False

# Main loop
def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    check_and_install_modules()

    print_styled("\nIPTV M3U List Analyzer", 'header')
    
    # First, select the file with M3U links
    m3u_urls = load_m3u_urls_from_file()
    if not m3u_urls:
        print_styled("No links loaded. Program terminated.", 'error')
        return

    # Fetch working proxies (exactly 30)
    working_proxies = get_working_proxies()

    # Generate a unique filename for results
    hits_dir = "/storage/emulated/0/hits"
    if not os.path.exists(hits_dir):
        os.makedirs(hits_dir)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(hits_dir, f"iptv_results_{timestamp}.txt")
    
    # Check links
    for i, m3u_url in enumerate(m3u_urls, 1):
        print_styled(f"Checking link:", 'header', color='cyan')
        print_styled(m3u_url, 'info', color='white')
        success = check_iptv(m3u_url, filename, working_proxies)

    print_styled("\nCheck another M3U list? (y/n): ", 'info')
    answer = input().strip().lower()
    if answer == 'y':
        main()  # Recursive call for another list
    else:
        print_styled("Program terminated.", 'info')

if __name__ == "__main__":
    main()