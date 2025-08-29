import os, random, string, time, re, imaplib, email, json, mimetypes
from email.header import decode_header
from email.utils import getaddresses
from datetime import datetime
from curl_cffi import requests as req
import names
from itertools import product
from curl_cffi import CurlMime
import os
import random
from instagrapi import Client

import requests  # For Telegram notifications

def send_telegram_message(message):
    """Send message to Telegram bot"""
    try:
        with open("bot.json", "r") as f:
            bot_config = json.load(f)
            bot_token = bot_config.get("bot_token", "")
            chat_id = bot_config.get("chat_id", "")
        
        if not bot_token or not chat_id:
            print("[⚠] Telegram bot token or chat_id not configured in bot.json")
            return False
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print("[✅] Telegram notification sent")
            return True
        else:
            print(f"[✖] Failed to send Telegram message: {response.text}")
            return False
    except Exception as e:
        print(f"[✖] Telegram error: {e}")
        return False

def clean_banned_credentials():
    """Remove banned credentials from credentials.txt file"""
    try:
        # Load banned emails
        banned_emails = []
        if os.path.exists('banned_emails.json'):
            with open('banned_emails.json', 'r') as f:
                data = json.load(f)
                banned_emails = data.get('banned_emails', [])
        
        if not banned_emails:
            print("[+] No banned emails found")
            return
        
        # Load current credentials
        valid_credentials = []
        removed_count = 0
        
        with open('credentials.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    email = line.split(':', 1)[0].strip()
                    if email not in banned_emails:
                        valid_credentials.append(line)
                    else:
                        removed_count += 1
                        print(f"[+] Removing banned credential: {email}")
        
        # Write back only valid credentials
        with open('credentials.txt', 'w') as f:
            for cred in valid_credentials:
                f.write(cred + '\n')
        
        print(f"[+] Cleaned credentials.txt - Removed {removed_count} banned credentials")
        print(f"[+] {len(valid_credentials)} valid credentials remaining")
        
    except Exception as e:
        print(f"[⚠] Error cleaning credentials: {e}")

def load_credentials():
    """Load credentials from credentials.txt file"""
    # Clean banned credentials first
    clean_banned_credentials()
    
    try:
        with open('credentials.txt', 'r') as f:
            credentials = []
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    email, app_password = line.split(':', 1)
                    credentials.append({
                        'email': email.strip(),
                        'app_password': app_password.strip()
                    })
            return credentials
    except FileNotFoundError:
        print("❌ credentials.txt file not found!")
        return []
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return []

class InstagramBot:
    BANNED_FILE = "banned_emails.json"

    def __init__(self, credentials_list, proxies=None):
        self.session = req.Session()
        self.session.impersonate = 'chrome110'
        self.proxies = proxies
        self.original_credentials_list = credentials_list.copy()  # Keep original list
        self.available_credentials = credentials_list.copy()  # Working list
        self.current_credential = None
        self.current_dot_emails_file = None
        self.code = None
        self.headers = None
        self.load_banned_emails_and_filter()
        self.select_next_credential()

    def reset_session(self):
        """Reset the session to clear any cached state"""
        print("[🔄] Resetting session state...")
        self.session.close()
        self.session = req.Session()
        self.session.impersonate = 'chrome110'
        self.headers = None
        time.sleep(2)  # Brief pause after reset

    def get_dot_emails_filename(self, email):
        """Generate unique dot emails filename for each credential"""
        clean_email = email.replace('@', '_').replace('.', '_')
        return f"dot_emails_{clean_email}.txt"

    def load_banned_emails(self):
        """Load banned emails from banned_emails.json"""
        try:
            if os.path.exists(self.BANNED_FILE):
                with open(self.BANNED_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("banned_emails", [])
        except Exception as e:
            print(f"[⚠] Error loading banned emails: {e}")
        return []

    def save_banned_email(self, email):
        """Add email to banned list and remove from available credentials"""
        try:
            banned_list = self.load_banned_emails()
            if email not in banned_list:
                banned_list.append(email)
                
            data = {"banned_emails": banned_list}
            with open(self.BANNED_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[+] Added email to banned list: {email}")
            
            # Remove from available credentials
            self.available_credentials = [cred for cred in self.available_credentials 
                                        if cred["email"] != email]
            print(f"[+] Removed {email} from available credentials")
            
        except Exception as e:
            print(f"[⚠] Error saving banned email: {e}")

    def load_banned_emails_and_filter(self):
        """Load banned emails and filter them from available credentials"""
        banned_emails = self.load_banned_emails()
        if banned_emails:
            print(f"[+] Found {len(banned_emails)} banned emails, filtering...")
            self.available_credentials = [cred for cred in self.available_credentials 
                                        if cred["email"] not in banned_emails]
            print(f"[+] {len(self.available_credentials)} credentials available after filtering")

    def cleanup_old_dot_emails(self):
        """Clean up old dot emails file when switching credentials"""
        if self.current_dot_emails_file and os.path.exists(self.current_dot_emails_file):
            try:
                os.remove(self.current_dot_emails_file)
                print(f"[+] Cleaned up old dot emails file: {self.current_dot_emails_file}")
            except Exception as e:
                print(f"[⚠] Error cleaning up dot emails file: {e}")

    def select_next_credential(self):
        """Select next available credential"""
        if not self.available_credentials:
            print("[✖] No credentials found - all have been banned or used")
            return False
            
        # Clean up old dot emails file before switching
        if self.current_credential:
            self.cleanup_old_dot_emails()
            
        # Get the first available credential
        self.current_credential = self.available_credentials[0]
        self.current_dot_emails_file = self.get_dot_emails_filename(self.current_credential["email"])
        print(f"[+] Using credential: {self.current_credential['email']}")
        print(f"[+] Dot emails file: {self.current_dot_emails_file}")
        print(f"[+] Remaining credentials: {len(self.available_credentials)}")
        return True

    def switch_to_next_credential(self):
        """Switch to next available credential by removing current one"""
        if self.current_credential:
            # Remove current credential from available list
            self.available_credentials = [cred for cred in self.available_credentials 
                                        if cred["email"] != self.current_credential["email"]]
        
        return self.select_next_credential()

    def get_random_profile_image(self, folder="Avatars"):
        if not os.path.exists(folder):
            print(f"[✖] Folder not found: {folder}")
            return None
        images = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        if not images:
            print(f"[✖] No images found in folder: {folder}")
            return None
        return os.path.join(folder, random.choice(images))

    def follow_targets(self, sessionid, settings=None, settings_path="settings.json"):
        """Follow target accounts"""
        if settings is None:
            try:
                with open(settings_path, "r") as f:
                    settings = json.load(f)
            except Exception as e:
                print(f"[✖] Failed to read settings.json: {e}")
                return

        target_usernames = settings.get("follow_targets", [])
        if not target_usernames:
        
            return

        max_to_follow = min(len(target_usernames), 3)
        max_retries = settings.get("max_retries", 3)
        retry_delay = settings.get("retry_delay", 2)

        cl = Client()
        try:
            cl.login_by_sessionid(sessionid)
        except Exception as e:
            print(f"[✖] Failed to login with session: {e}")
            return

        for i, username in enumerate(target_usernames[:max_to_follow], 1):
            print(f"[ ] Following user {i}/{max_to_follow}: {username}…")
            retries = 0
            while retries < max_retries:
                try:
                    user_id = cl.user_id_from_username(username)
                    cl.user_follow(user_id)
                    print(f"✅ Successfully followed: {username}")
                    break
                except Exception as e:
                    retries += 1
                    print(f"[⚠] Retry {retries}/{max_retries} for {username}: {e}")
                    time.sleep(retry_delay)
            else:
                print(f"[✖] Could not follow {username} after {max_retries} retries.")

    def upload_random_post(self, sessionid, folder="Posts"):
        print("[ ] Uploading post…")
        image_path = self.get_random_profile_image(folder)
        if not image_path:
            print("[✖] No image found to upload as post.")
            return

        captions = [
            "Feeling good today! 😎",
            "Just another day in paradise 🌴",
            "Life is better with smiles 😄",
            "Capturing the little moments 📸",
            "Enjoying every bit of today ✨",
            "Sunshine mixed with a little bit of happiness ☀️",
            "Mood: chill and relaxed 🛋️",
            "Sharing this little vibe with you all 💛"
        ]
        caption = random.choice(captions)

        cl = Client()
        try:
            cl.login_by_sessionid(sessionid)
            cl.photo_upload(image_path, caption=caption)
            print(f"✅ Post uploaded successfully: {os.path.basename(image_path)}")
            print(f"Caption: {caption}")
        except Exception as e:
            print(f"[✖] Failed to upload post: {e}")

    def upload_profile_picture(self, sessionid, headers, username, folder="Avatars"):
        print("[ ] Uploading profile picture…")
        image_path = self.get_random_profile_image(folder)
        if not image_path:
            return

        url = f"https://www.instagram.com/api/v1/web/accounts/web_change_profile_picture/"
        cookies = {
            "sessionid": sessionid,
            "ig_did": "IG_DID_HERE",
        }

        multipart_data = CurlMime()
        content_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        multipart_data.addpart(
            name="profile_pic",
            filename=os.path.basename(image_path),
            local_path=image_path,
            content_type=content_type
        )

        web_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
            "x-csrftoken": "1234567890abcdef",
            "x-ig-app-id": "936619743392459",
            "x-instagram-ajax": "1001234567", 
        }

        resp = req.post(url, headers=web_headers, cookies=cookies, multipart=multipart_data)
        if resp.status_code == 200 and '"status":"ok"' in resp.text:
            print(f"✅ Profile picture uploaded successfully: {os.path.basename(image_path)}")
        else:
            print(f"[✖] Failed to upload profile picture:\n{resp.text}")

    def _random_agent(self):
        return (f'Mozilla/5.0 (Linux; Android {random.randint(9,13)}; '
                f'{"".join(random.choices(string.ascii_uppercase, k=3))}{random.randint(111,999)}) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36')

    def init_headers(self):
        max_retries = 5  # Limit the number of retries
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                agent = self._random_agent()
                r = self.session.get('https://www.instagram.com/', headers={'user-agent': agent},
                                     proxies=self.proxies, timeout=30)
                
                # Check if required cookies exist before accessing them
                if 'datr' not in r.cookies:
                    print(f"[⚠] 'datr' cookie not found in response (attempt {retry_count + 1}/{max_retries})")
                    retry_count += 1
                    time.sleep(2)  # Wait longer between retries
                    continue
                    
                mid = r.text.split('{"mid":{"value":"')[1].split('",')[0]
                datr = r.cookies['datr']
                csrftoken = r.cookies['csrftoken']
                ig_did = r.cookies['ig_did']
        
                resp = self.session.get('https://www.instagram.com/', headers={'user-agent': agent},
                                        proxies=self.proxies, timeout=30)
                appid = resp.text.split('APP_ID":"')[1].split('"')[0]
                rollout = resp.text.split('rollout_hash":"')[1].split('"')[0]
        
                self.headers = {
                    'user-agent': agent,
                    'cookie': f'dpr=3; csrftoken={csrftoken}; mid={mid}; ig_nrcb=1; ig_did={ig_did}; datr={datr}',
                    'x-ig-app-id': appid,
                    'x-instagram-ajax': rollout,
                    'x-csrftoken': csrftoken,
                    'x-web-device-id': ig_did,
                }
                print("[✅] Headers initialized successfully")
                return True
            except Exception as e:
                retry_count += 1
                print(f"[⚠] Error initializing headers (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    time.sleep(2)  # Wait before retrying
                
        print(f"[✖] Failed to initialize headers after {max_retries} attempts")
        return False

    def verify_auth(self):
        if not self.current_credential:
            print("[✖] No current credential selected")
            return False
            
        email = self.current_credential["email"]
        app_password = self.current_credential["app_password"]

        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(email, app_password)
            mail.logout()
            print(f"✅ Gmail authentication successful for {email}")
            return True
        except imaplib.IMAP4.error as e:
            print(f"[✖] Gmail authentication failed (IMAP error): {e}")
            return False
        except Exception as e:
            print(f"[✖] Gmail authentication failed (Other error): {e}")
            return False

    def _init_dot_emails(self):
        """Initialize dot emails for current credential"""
        if not os.path.exists(self.current_dot_emails_file):
            print(f"[+] Generating dot emails for {self.current_credential['email']}...")
            base = self.current_credential["email"].split("@")[0].replace(".", "")
            domain = self.current_credential["email"].split("@")[1]
            positions = len(base)-1
            all_combs = product([0,1], repeat=positions)
            with open(self.current_dot_emails_file, "w") as f:
                for comb in all_combs:
                    s = base[0]
                    for i in range(positions):
                        if comb[i]:
                            s += "."
                        s += base[i+1]
                    f.write(s + "@" + domain + "\n")
            print(f"[+] Dot emails saved to {self.current_dot_emails_file}")

    def get_dot_emails(self):
        if not os.path.exists(self.current_dot_emails_file):
            return []
        with open(self.current_dot_emails_file, "r") as f:
            return [line.strip() for line in f if line.strip()]

    def get_random_dot_email(self):
        emails = self.get_dot_emails()
        if not emails:
            raise Exception(f"[✖] No dot emails left for {self.current_credential['email']}")
        return random.choice(emails)

    def remove_dot_email(self, email_to_remove):
        emails = self.get_dot_emails()
        emails = [e for e in emails if e != email_to_remove]
        with open(self.current_dot_emails_file, "w") as f:
            f.write("\n".join(emails) + "\n")

    def get_email_code(self, target_email, interval=2, max_wait=60):
        waited = 0
        checked_ids = set()
        email_addr = self.current_credential["email"]
        app_password = self.current_credential["app_password"]
        
        while waited < max_wait:
            print(f"⏳ Waiting for code: {waited}s / {max_wait}s...", end="\r")
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(email_addr, app_password)
                mail.select("inbox")
                status, data = mail.search(None, 'FROM', '"no-reply@mail.instagram.com"')
                mail_ids = data[0].split()
                if mail_ids:
                    latest_id = mail_ids[-1]
                    if latest_id not in checked_ids:
                        checked_ids.add(latest_id)
                        status, msg_data = mail.fetch(latest_id, "(RFC822)")
                        for response_part in msg_data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                subject, encoding = decode_header(msg["subject"])[0]
                                if isinstance(subject, bytes):
                                    subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                                match = re.search(r'\b\d{6}\b', subject)
                                code = match.group() if match else None
                                to_emails = [addr[1] for addr in getaddresses([msg["to"]])]
                                if target_email in to_emails and code:
                                    print(f"\n✅ Code received: {code}")
                                    self.code = code
                                    return code
            except Exception as e:
                print(f"[⚠] Error fetching email: {e}")

            time.sleep(interval)
            waited += interval

        print("\n[✖] Could not fetch code after waiting.")
        return None

    def get_username(self, name, email):
        try:
            data = {'email': email, 'name': name + str(random.randint(1, 99))}
            response = self.session.post(
                'https://www.instagram.com/api/v1/web/accounts/username_suggestions/',
                headers=self.headers, data=data, proxies=self.proxies, timeout=30
            )
            if 'status":"ok' in response.text:
                return random.choice(response.json()['suggestions'])
        except Exception as e:
            print(f"[⚠] Username error: {e}")
        return f"{name}{random.randint(100,999)}"

    def send_verification(self, email):
        try:
            print(f"[ ] Sending verification email to {email}...")
            mid = self.headers['cookie'].split('mid=')[1].split(';')[0]
            return self.session.post(
                'https://www.instagram.com/api/v1/accounts/send_verify_email/',
                headers=self.headers, data={'device_id': mid, 'email': email},
                proxies=self.proxies, timeout=30
            ).text
        except Exception as e:
            print(f"[⚠] Verification error: {e}")

    def validate_code(self, email, code):
        try:
            print(f"[ ] Validating code {code} for {email}...")
            mid = self.headers['cookie'].split('mid=')[1].split(';')[0]
            return self.session.post(
                'https://www.instagram.com/api/v1/accounts/check_confirmation_code/',
                headers=self.headers, data={'code': code, 'device_id': mid, 'email': email},
                proxies=self.proxies, timeout=30
            )
        except Exception as e:
            print(f"[⚠] Validate code error: {e}")

    def create_account(self, email, signup_code):
        first_name = names.get_first_name()
        username = self.get_username(first_name, email)
        password = f'{first_name.strip()}@{random.randint(111,999)}'
        print("[ ] Creating account on Instagram...")
        mid = self.headers['cookie'].split('mid=')[1].split(';')[0]

        data = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{password}',
            'email': email,
            'username': username,
            'first_name': first_name,
            'month': random.randint(1,12),
            'day': random.randint(1,28),
            'year': random.randint(1990,2001),
            'client_id': mid,
            'seamless_login_enabled': '1',
            'tos_version': 'row',
            'force_sign_up_code': signup_code,
        }

        resp = self.session.post(
            'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
            headers=self.headers, data=data, proxies=self.proxies, timeout=30
        )

        if '"account_created":true' in resp.text:
            sessionid = resp.cookies.get("sessionid", "")
            account_info = {
                "email": email,
                "username": username,
                "password": password,
                "sessionid": sessionid,
                "created_at": datetime.utcnow().isoformat()
            }
            self.save_account(account_info)
            self.remove_dot_email(email)
            print("\n🎉 Account created successfully!\n")
            print(f"Email: {account_info['email']}")
            print(f"Username: {account_info['username']}")
            print(f"Password: {account_info['password']}")
            print(f"SessionID: {account_info['sessionid']}")
            print(f"Created At: {account_info['created_at']}\n")
            return account_info
        else:
            # Check for IP proxy error - ban the PRIMARY EMAIL, not the dot email
            if '"error_type":"signup_block"' in resp.text and 'open proxy' in resp.text:
                primary_email = self.current_credential['email']
                print(f"[✖] IP flagged as proxy for primary email: {primary_email}")
                print(f"[+] Banning primary email (not the dot email): {primary_email}")
                self.save_banned_email(primary_email)  # Ban the primary email
                return "SWITCH_CREDENTIAL"
            else:
                print(f"[✖] Failed to create account:\n{resp.text}")
                return None

    def save_account(self, account):
        os.makedirs("accounts", exist_ok=True)
        os.makedirs("sessions", exist_ok=True)

        with open(os.path.join("accounts", "accounts_userpass.txt"), "a") as f:
            f.write(f"{account['username']}:{account['password']}\n")
        
        with open(os.path.join("accounts", "accounts_emailpass.txt"), "a") as f:
            f.write(f"{account['email']}:{account['password']}\n")
        
        accounts_full = []
        full_path = os.path.join("accounts", "accounts_full.json")
        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                try:
                    accounts_full = json.load(f)
                except:
                    accounts_full = []
        accounts_full.append(account)
        with open(full_path, "w") as f:
            json.dump(accounts_full, f, indent=2)
        
        if account.get("sessionid"):
            with open(os.path.join("sessions", "usersession.txt"), "a") as f:
                f.write(f"{account['username']}:{account['sessionid']}\n")
            with open(os.path.join("sessions", "session.txt"), "a") as f:
                f.write(f"{account['sessionid']}\n")

# -------------------- Main flow --------------------
if __name__ == "__main__":
    print(r"""
 ___ _    _          
| __(_)__| |_ _ __ _ 
| _|| / _` | '_/ _` |
|_| |_c__,_|_| \__,_|

Instagram accounts generator by @f09l - hexa
Channels: https://t.me/ifostn | https://t.me/HexGalaxy
""")
    # Load credentials from credentials.txt
    credentials_list = load_credentials()
    if not credentials_list:
        print("[✖] No credentials found in credentials.txt")
        exit()

    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
            max_wait = settings.get("max_wait", 60)
            interval = settings.get("interval", 2)
    except:
        max_wait = 60
        interval = 2

    bot = InstagramBot(credentials_list)
    
    # Check if we have any available credentials after filtering banned ones
    if not bot.available_credentials:
        print("[✖] No credentials found - all credentials have been banned")
        exit()

    print(f"[+] Starting continuous account creation with {len(bot.available_credentials)} credentials")
    
    # Continuous loop until all credentials are banned
    total_accounts_created = 0
    
    while bot.available_credentials:
        current_credential = bot.current_credential['email'] if bot.current_credential else "Unknown"
        print(f"\n[+] Using credential: {current_credential}")
        print(f"[+] Remaining credentials: {len(bot.available_credentials)}")
        print(f"[+] Total accounts created so far: {total_accounts_created}")
        
        # Step 1: Verify Gmail authentication
        auth_success = False
        while not auth_success:
            if not bot.verify_auth():
                print("[✖] Gmail authentication failed, switching to next credential...")
                if not bot.switch_to_next_credential():
                    print("[✖] No more credentials available")
                    break
                continue
            auth_success = True
        
        if not bot.available_credentials:
            break
    
        # Step 2: Initialize Instagram headers with restart logic
        headers_success = False
        while not headers_success:
            if not bot.init_headers():
                print("[✖] Failed to initialize headers after 5 attempts")
                print("[🔄] Restarting from authentication step...")
                bot.reset_session()  # Reset session state
                time.sleep(10)  # Wait before restarting
                # Restart from authentication step - don't switch credential
                break  # This will go back to Step 1 (authentication)
            headers_success = True
        
        if not headers_success:
            continue  # Restart from authentication step
        
        # Step 3: Initialize dot emails
        bot._init_dot_emails()
        
        # Step 4: Get random dot email
        try:
            dot_email = bot.get_random_dot_email()
            print(f"[+] Using dot email: {dot_email}")
        except Exception as e:
            print(f"[✖] Error getting dot email: {e}")
            if not bot.switch_to_next_credential():
                print("[✖] No more credentials available")
                break
            continue
        
        # Step 5: Account creation process
        start_time = time.time()
        resp = bot.send_verification(dot_email)

        if 'email_sent":true' in resp:
            code = bot.get_email_code(dot_email, max_wait=max_wait, interval=interval)
            if not code:
                print("[✖] Could not fetch code for", dot_email)
                continue  # Try again with same credential
            else:
                validation = bot.validate_code(dot_email, code)
                if 'status":"ok' in validation.text:
                    signup_code = validation.json()['signup_code']
                    account_info = bot.create_account(dot_email, signup_code)

                    if account_info == "SWITCH_CREDENTIAL":
                        print("[+] IP blocked, switching to next credential...")
                        if not bot.switch_to_next_credential():
                            print("[✖] No more credentials available")
                            break
                        continue
                    elif account_info:
                        # Account created successfully
                        total_accounts_created += 1
                        
                        # Send immediate Telegram notification
                        telegram_message = f"🎉 <b>New Instagram Account Created!</b>\n\n" \
                                         f"📧 <b>Email:</b> <code>{account_info['email']}</code>\n" \
                                         f"👤 <b>Username:</b> <code>{account_info['username']}</code>\n" \
                                         f"🔑 <b>Password:</b> <code>{account_info['password']}</code>\n" \
                                         f"🆔 <b>SessionID:</b> <code>{account_info['sessionid']}</code>\n" \
                                         f"⏰ <b>Created:</b> {account_info['created_at']}\n" \
                                         f"📊 <b>Account #{total_accounts_created}</b>\n\n" \
                                       
                        
                        send_telegram_message(telegram_message)
                        
                        # Continue with profile setup
                        print(f"[+] Setting up profile for account #{total_accounts_created}...")
                        
                        upload_result = bot.upload_profile_picture(
                            sessionid=account_info["sessionid"],
                            headers=bot.headers,
                            username=account_info["username"],
                            folder=r"Avatars"
                        )
                        
                        if upload_result == "ACCOUNT_SUSPENDED":
                            print("[⚠] Account was suspended during profile setup")
                            suspension_message = f"⚠️ <b>Account Suspended</b>\n\n" \
                                               f"👤 <b>Username:</b> <code>{account_info['username']}</code>\n" \
                                               f"📧 <b>Email:</b> <code>{account_info['email']}</code>\n" \
                                               f"🚫 <b>Status:</b> Suspended during profile picture upload"
                            send_telegram_message(suspension_message)
                            continue  # Continue with same credential
                        
                        bot.upload_random_post(
                            sessionid=account_info["sessionid"],
                            folder=r"Posts"
                        )
                        
                        # Follow targets
                        bot.follow_targets(
                            sessionid=account_info["sessionid"],
                            settings=settings
                        )
                        
                        end_time = time.time()
                        print(f"⏱ Account creation time: {round(end_time - start_time, 2)} seconds")
                        
                        # Save account and continue
                        print(f"[+] Account #{total_accounts_created} completed! Continuing...")
                        bot.reset_session()  # Reset session for next account
                        time.sleep(5)  # Brief pause before next account
                        continue
                    else:
                        print("[✖] Account creation failed, trying again...")
                        continue  # Try again with same credential
                else:
                    print("[✖] Code validation failed, trying again...")
                    continue  # Try again with same credential
        else:
            print("[✖] Failed to send verification, trying again...")
            continue  # Try again with same credential
    
    # Final summary
    print(f"\n🏁 Session completed!")
    print(f"📊 Total accounts created: {total_accounts_created}")
    if not bot.available_credentials:
        print("[✖] All credentials have been used or banned")
    else:
        print("[+] Session ended with available credentials remaining")
        
    summary_message = f"🏁 <b>Instagram Bot Session Completed</b>\n\n" \
                     f"📊 <b>Total Accounts Created:</b> <code>{total_accounts_created}</code>\n" \
                     f"🚫 <b>Status:</b> All credentials exhausted"
    send_telegram_message(summary_message)
