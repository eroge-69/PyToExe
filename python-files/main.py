import asyncio
import random
import string
import requests
import re
import time
import json
import os
from datetime import datetime
from colorama import Fore, Style, init
from pystyle import *
import zendriver as zd

init(autoreset=True)

# Built-in Configuration
API_ENDPOINT = "http://dv-n6.divahost.net:6094/api/client"
API_KEY = "workerevesgenhere"
PRODUCT = "EVS-GEN"
VERSION = "1.0.0"

# Email API Configuration
EMAIL_API_URL = "https://leveragers.xyz/api/email"
RESULT_API_URL = "https://leveragers.xyz/api/result"
EMAIL_API_KEY = "3PY5ACVKX5YA8QV3U45SG9WAEL0XLWDT"
EMAIL_HEADERS = {
    "Authorization": f"Bearer {EMAIL_API_KEY}",
    "Content-Type": "application/json"
}

# Dashboard Integration Configuration
DATABASE_URL = "http://dv-n1.divahost.net:50345"  # Change this to your dashboard URL
DATABASE_API_ENDPOINT = f"{DATABASE_URL}/api/add_token"

# Server invite links for joining (gaming communities)
SERVER_INVITES = [
    "https://discord.gg/coregen"
]

# Global variables
config = {}
discord_id = ""
tokens_generated = 0

# ASCII Art Banner
BANNER = f"""{Fore.CYAN}{Style.BRIGHT}
 ██████╗ ██████╗ ██████╗ ███████╗     ██████╗ ███████╗███╗   ██╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝    ██╔════╝ ██╔════╝████╗  ██║
██║     ██║   ██║██████╔╝█████╗      ██║  ███╗█████╗  ██╔██╗ ██║
██║     ██║   ██║██╔══██╗██╔══╝      ██║   ██║██╔══╝  ██║╚██╗██║
╚██████╗╚██████╔╝██║  ██║███████╗    ╚██████╔╝███████╗██║ ╚████║
 ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝
{Style.RESET_ALL}"""

BANNER1 = f"""{Fore.CYAN}{Style.BRIGHT}
[+] Discord Token Generator [+]
 [+] Programmed By CoreGen [+]
{Style.RESET_ALL}"""

# Enhanced humanization data
PRONOUNS_LIST = [
    "he/him", "she/her", "they/them", "he/they", "she/they", 
    "any pronouns", "ask me", "ze/zir", "xe/xem", "it/its",
    "fae/faer", "ey/em", "ve/ver", "ne/nem", "co/cos"
]

BIO_LIST = [
    "Just vibing and gaming 🎮",
    "Coffee addict ☕ | Code enthusiast 💻",
    "Gamer | Streamer | Dreamer ✨",
    "Living life one pixel at a time 🎨",
    "Music lover 🎵 | Night owl 🦉",
    "Aspiring developer | Learning everyday 📚",
    "Anime fan | Manga reader 📖",
    "Always down for a good conversation 💬",
    "Tech enthusiast | Future innovator 🚀",
    "Artist at heart | Creator by choice 🎭",
    "Foodie | Traveler | Adventure seeker 🌍",
    "Minimalist | Productivity nerd ⚡",
    "Plant parent 🌱 | Book worm 📚",
    "Fitness enthusiast | Health conscious 💪",
    "Photographer | Capturing moments 📸",
    "Love is all you need 💕",
    "Making memories one day at a time",
    "Exploring the world through pixels",
    "Digital nomad | Creative soul",
    "Building dreams in code",
    "Gaming is my therapy 🎯",
    "Collecting moments, not things",
    "Living in a world of possibilities"
]

def load_config():
    """Load license key from config.json"""
    global config
    try:
        if not os.path.exists("config.json"):
            log("Configuration file not found!", Fore.RED, "ERROR")
            print(f"{Fore.YELLOW}Please create config.json with your license key.{Style.RESET_ALL}")
            input("Press Enter to exit...")
            exit()
        
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        if 'license_key' not in config or not config['license_key'] or config['license_key'] == "YOUR_LICENSE_KEY_HERE":
            log("Missing or invalid license key in config.json!", Fore.RED, "ERROR")
            print(f"{Fore.YELLOW}Please update config.json with a valid license key.{Style.RESET_ALL}")
            input("Press Enter to exit...")
            exit()
        
        log("Configuration loaded successfully", Fore.GREEN, "CONFIG")
        return True
    except Exception as e:
        log(f"Failed to load configuration: {e}", Fore.RED, "ERROR")
        input("Press Enter to exit...")
        exit()

def verify_license():
    """Verify license key with the server"""
    global discord_id
    try:
        log("Verifying license key...", Fore.CYAN, "LICENSE")
        
        headers = {'Authorization': API_KEY}
        data = {
            'license': config['license_key'], 
            'product': PRODUCT, 
            'version': VERSION
        }
        
        response = requests.post(API_ENDPOINT, headers=headers, json=data, timeout=10)
        status = response.json()
        
        if status.get('status_overview') == "success":
            discord_id = status.get('discord_id', 'Unknown')
            log("License key is valid!", Fore.GREEN, "LICENSE")
            log(f"Discord ID: {discord_id}", Fore.CYAN, "USER")
            return True
        else:
            log("License key is invalid!", Fore.RED, "LICENSE")
            log("Create a ticket in our discord server to get one.", Fore.YELLOW, "SUPPORT")
            input("Press Enter to exit...")
            exit()
            
    except Exception as e:
        log(f"License verification failed: {e}", Fore.RED, "ERROR")
        log("Please check your internet connection and API endpoint.", Fore.YELLOW, "NETWORK")
        input("Press Enter to exit...")
        exit()

def check_dashboard_status():
    """Check if dashboard is online and accessible"""
    try:
        response = requests.get(f"{DATABASE_URL}/api/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            log(f"DataBase Status: {status['status']}", Fore.GREEN, "DATABASE")
            return True
        return False
    except Exception as e:
        log(f"DataBase Is Offline Wait Until It ComeBack: Report On CoreGen", Fore.YELLOW, "DATABASE")
        input("Press Enter to exit...")
        exit()

def send_token_to_dashboard(email, password, token, humanized=False, servers_joined=0):
    """Send generated token data to the dashboard"""
    try:
        data = {
            "discord_id": discord_id,
            "email": email,
            "password": password,
            "token": token,
            "license_key": config['license_key'],
            "humanized": humanized,
            "servers_joined": servers_joined
        }
        
        response = requests.post(DATABASE_API_ENDPOINT, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            log("Token data saved successfully", Fore.GREEN, "DATABASE")
            return True
        else:
            log(f"Database error: {response.status_code} - {response.text}", Fore.YELLOW, "DATABASE")
            return False
            
    except Exception as e:
        log(f"Failed to send to database: {e}", Fore.RED, "DATABASE")
        return False

def log(msg, color=Fore.WHITE, prefix="INFO", timestamp=True):
    """Enhanced logging function with professional styling"""
    if timestamp:
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"{Fore.CYAN}[{time_str}]{Style.RESET_ALL} {color}[{prefix}]{Style.RESET_ALL} {msg}")
    else:
        print(f"{color}[{prefix}]{Style.RESET_ALL} {msg}")

def get_discord_api_headers(token=None):
    """Generate Discord API headers that match Chrome browser"""
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'https://discord.com',
        'Referer': 'https://discord.com/',
        'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'X-Debug-Options': 'bugReporterEnabled',
        'X-Discord-Locale': 'en-US',
        'X-Discord-Timezone': 'America/New_York',
        'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExOS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTE5LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiJodHRwczovL3d3dy5nb29nbGUuY29tLyIsInJlZmVycmluZ19kb21haW4iOiJ3d3cuZ29vZ2xlLmNvbSIsInJlZmVycmVyX2N1cnJlbnQiOiIiLCJyZWZlcnJpbmdfZG9tYWluX2N1cnJlbnQiOiIiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyNTU5NzEsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGwsImRlc2lnbl9pZCI6MH0='
    }
    
    if token:
        headers['Authorization'] = token
        
    return headers

def get_discord_cookies():
    """Get Discord cookies for requests"""
    try:
        session = requests.Session()
        response = session.get("https://discord.com")
        cookies = {}
        for cookie in response.cookies:
            if cookie.name.startswith('__') and cookie.name.endswith('uid'):
                cookies[cookie.name] = cookie.value
        return "; ".join([f"{k}={v}" for k, v in cookies.items()]) + "; locale=en-US"
    except:
        return "__dcfduid=4e0a8d504a4411eeb88f7f88fbb5d20a; __sdcfduid=4e0a8d514a4411eeb88f7f88fbb5d20ac488cd4896dae6574aaa7fbfb35f5b22b405bbd931fdcb72c21f85b263f61400; __cfruid=f6965e2d30c244553ff3d4203a1bfdabfcf351bd-1699536665; _cfuvid=rNaPQ7x_qcBwEhO_jNgXapOMoUIV2N8FA_8lzPV89oM-1699536665234-0-604800000; locale=en-US"

def get_email_from_api():
    """Generate temporary email using API"""
    log("Generating temporary email...", Fore.CYAN, "EMAIL")
    try:
        res = requests.post(EMAIL_API_URL, headers=EMAIL_HEADERS, timeout=10)
        if res.status_code == 200:
            email = res.json().get("email")
            if email:
                log(f"Email generated: {email}", Fore.GREEN, "EMAIL")
                return email
            log("Email generation failed: No email in response", Fore.RED, "EMAIL")
        else:
            log(f"Email generation failed: {res.text}", Fore.RED, "EMAIL")
    except Exception as e:
        log(f"Email API Exception: {e}", Fore.RED, "EMAIL")
    return None

def get_token(email, password):
    """Get Discord token using login API with undetectable headers"""
    try:
        payload = {"login": email, "password": password}
        headers = get_discord_api_headers()
        
        # Add session-specific headers for login
        headers.update({
            'Referer': 'https://discord.com/login',
            'X-Context-Properties': 'eyJsb2NhdGlvbiI6IkxvZ2luIn0=',
            'Cookie': get_discord_cookies()
        })
        
        session = requests.Session()
        
        # First, get cookies from Discord
        session.get("https://discord.com/login", headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        
        # Attempt login
        res = session.post("https://discord.com/api/v9/auth/login", json=payload, headers=headers, timeout=10)
        
        if res.status_code == 200 and 'token' in res.json():
            token = res.json()['token']
            log(f"Token retrieved: {token[:25]}...", Fore.GREEN, "TOKEN")
            return token
        else:
            log(f"Token request failed: {res.status_code} - {res.text}", Fore.RED, "TOKEN")
    except Exception as e:
        log(f"Token error: {e}", Fore.RED, "TOKEN")
    return None

async def detect_captcha_on_page(page):
    """Enhanced CAPTCHA detection for any page"""
    captcha_selectors = [
        'iframe[src*="captcha"]', 'iframe[src*="recaptcha"]', 'iframe[src*="hcaptcha"]',
        'div[class*="captcha"]', 'div[class*="recaptcha"]', 'div[class*="hcaptcha"]',
        '[data-sitekey]', '.h-captcha', '.g-recaptcha', '#captcha', '[id*="captcha"]',
        'div[data-testid*="captcha"]', 'div[aria-label*="captcha"]'
    ]
    
    for selector in captcha_selectors:
        element = await page.query_selector(selector)
        if element:
            return True
    
    page_content = await page.get_content()
    captcha_indicators = [
        "captcha", "recaptcha", "hcaptcha", "challenge", 
        "verify you are human", "prove you're not a robot", "security check"
    ]
    
    for indicator in captcha_indicators:
        if indicator.lower() in page_content.lower():
            return True
    
    return False

async def wait_for_user_input(message):
    """Wait for user to press Enter in console"""
    return await asyncio.to_thread(input, message)

async def join_discord_servers(page, servers_to_join=1):
    """Join Discord servers using direct invite links - Simplified and more reliable"""
    log("🚀 Starting direct server joining process...", Fore.CYAN, "NON-CAP")
    servers_joined = 0
    
    try:
        # Select random server invite (just 1)
        selected_invite = random.choice(SERVER_INVITES)
        
        try:
            log(f" Joining server via direct invite: {selected_invite.split('/')[-1]}", Fore.CYAN, "NON-CAP")
            
            # Navigate directly to the invite URL
            await page.get(selected_invite)
            await asyncio.sleep(6)
            
            # Look for accept/join invite buttons
            join_button_selectors = [
                'button:has-text("Accept Invite")',
                'button:has-text("Join Server")',
                'button:has-text("Join")',
                'button[class*="colorBrand"]',
                'button[class*="buttonPrimary"]',
                'button[class*="lookFilled"]',
                'button[type="button"]',
                'div[role="button"]:has-text("Join")',
                'div[role="button"]:has-text("Accept")'
            ]
            
            join_button = None
            for selector in join_button_selectors:
                try:
                    join_button = await page.query_selector(selector)
                    if join_button:
                        # Verify the button is visible and contains join-related text
                        is_visible = await join_button.is_visible()
                        if is_visible:
                            try:
                                button_text = await join_button.get_inner_text()
                                if any(word in button_text.lower() for word in ["join", "accept", "continue"]):
                                    log(f" Found join button: '{button_text}'", Fore.GREEN, "NON-CAP")
                                    break
                            except:
                                log(f" Found potential join button", Fore.GREEN, "NON-CAP")
                                break
                        else:
                            join_button = None
                except:
                    continue
            
            if not join_button:
                log("❌ Could not find join button on invite page", Fore.RED, "NON-CAP")
                return servers_joined
            
            # Click the join button
            await join_button.mouse_click("left")
            await asyncio.sleep(1.5)
            
            # Check for CAPTCHA
            captcha_detected = await detect_captcha_on_page(page)
            
            if captcha_detected:
                print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}CAPTCHA DETECTED ON SERVER JOIN!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Please solve the CAPTCHA manually in the browser.{Style.RESET_ALL}")
                print(f"{Fore.CYAN}After solving, press ENTER to continue...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
                
                await wait_for_user_input("")
                log(" Continuing after CAPTCHA solution...", Fore.GREEN, "CAPTCHA")
                await asyncio.sleep(3)
            
            # Wait a moment for page to load after join
            await asyncio.sleep(5)
            current_url = page.url
            
            # Check if we successfully joined by looking at URL patterns
            success_indicators = [
                # Successfully joined and redirected to server
                "channels" in current_url and "@me" not in current_url,
                "/channels/" in current_url and len(current_url.split('/')) > 5,
                # Alternative success patterns
                "guild" in current_url,
                # Check if we're no longer on invite page
                "invite" not in current_url and "discord.com" in current_url
            ]
            
            # Additional check: look for server-specific content
            try:
                page_content = await page.get_content()
                success_content_indicators = [
                    "guild" in page_content.lower(),
                    "server" in page_content.lower() and "member" in page_content.lower(),
                    "channel" in page_content.lower() and "message" in page_content.lower()
                ]
            except:
                success_content_indicators = []
            
            if any(success_indicators) or any(success_content_indicators):
                servers_joined = 1
                log(f" Successfully joined server via direct invite!", Fore.GREEN, "NON-CAP")
            else:
                # Check for common error messages
                try:
                    page_content = await page.get_content()
                    error_indicators = [
                        "invalid", "expired", "banned", "error", 
                        "unable to accept", "invite not found", "no longer valid"
                    ]
                    
                    if any(error in page_content.lower() for error in error_indicators):
                        log(f" Server join failed - invite may be invalid/expired", Fore.RED, "NON-CAP")
                    else:
                        log(f" Server join status unclear - URL: {current_url[:50]}...", Fore.YELLOW, "NON-CAP")
                        # Give benefit of doubt if no clear error
                        if "discord.com" in current_url and "invite" not in current_url:
                            servers_joined = 1
                            log(f" Assuming successful join based on URL change", Fore.YELLOW, "NON-CAP")
                except:
                    log(f" Could not determine join status", Fore.RED, "NON-CAP")
                
        except Exception as e:
            log(f" Error during direct server join: {str(e)[:50]}...", Fore.RED, "NON-CAP")
        
        log(f" Direct server joining completed: {servers_joined}/1 server joined", 
            Fore.GREEN if servers_joined == 1 else Fore.RED, "NON-CAP")
        return servers_joined
        
    except Exception as e:
        log(f" Direct server joining process failed: {str(e)[:50]}...", Fore.RED, "NON-CAP")
        return servers_joined



def humanize_token(token):
    """Enhanced token humanization with proper Discord API usage"""
    log("Starting token humanization...", Fore.CYAN, "HUMANIZE")
    
    headers = get_discord_api_headers(token)
    headers['Cookie'] = get_discord_cookies()
    
    success_count = 0
    session = requests.Session()
    
    # 1. Set pronouns
    try:
        pronouns = random.choice(PRONOUNS_LIST)
        pronouns_payload = {"pronouns": pronouns}
        
        pronouns_headers = headers.copy()
        pronouns_headers['Referer'] = 'https://discord.com/channels/@me'
        
        res = session.patch("https://discord.com/api/v9/users/@me/profile", 
                           json=pronouns_payload, headers=pronouns_headers, timeout=10)
        if res.status_code == 200:
            log(f"Pronouns set: {pronouns}", Fore.GREEN, "PRONOUNS")
            success_count += 1
        else:
            log(f"Failed to set pronouns: {res.status_code} - {res.text}", Fore.RED, "PRONOUNS")
    except Exception as e:
        log(f"Error setting pronouns: {e}", Fore.RED, "PRONOUNS")
    
    await_time = random.uniform(2, 4)
    time.sleep(await_time)
    
    # 2. Set bio
    try:
        bio = random.choice(BIO_LIST)
        bio_payload = {"bio": bio}
        
        bio_headers = headers.copy()
        bio_headers['Referer'] = 'https://discord.com/channels/@me'
        
        res = session.patch("https://discord.com/api/v9/users/@me/profile", 
                           json=bio_payload, headers=bio_headers, timeout=10)
        if res.status_code == 200:
            log(f"Bio set: {bio[:30]}...", Fore.GREEN, "BIO")
            success_count += 1
        else:
            log(f"Failed to set bio: {res.status_code} - {res.text}", Fore.RED, "BIO")
    except Exception as e:
        log(f"Error setting bio: {e}", Fore.RED, "BIO")
    
    await_time = random.uniform(2, 4)
    time.sleep(await_time)
    
    # 3. Join HyperSquad
    hypersquad_houses = [
        {"house_id": 1, "name": "Bravery"},
        {"house_id": 2, "name": "Brilliance"}, 
        {"house_id": 3, "name": "Balance"}
    ]
    
    selected_house = random.choice(hypersquad_houses)
    
    try:
        hypersquad_payload = {"house_id": selected_house["house_id"]}
        hypersquad_headers = headers.copy()
        hypersquad_headers['Referer'] = 'https://discord.com/settings/hypesquad'
        hypersquad_headers['X-Context-Properties'] = 'eyJsb2NhdGlvbiI6IkpvaW4gSHlwZXJTcXVhZCJ9'
        
        res = session.post("https://discord.com/api/v9/hypesquad/online", 
                          json=hypersquad_payload, headers=hypersquad_headers, timeout=10)
        if res.status_code in [204, 200]:
            log(f"Joined HyperSquad {selected_house['name']}", Fore.GREEN, "HYPERSQUAD")
            success_count += 1
        else:
            log(f"Failed to join HyperSquad: {res.status_code} - {res.text}", Fore.RED, "HYPERSQUAD")
    except Exception as e:
        log(f"Error joining HyperSquad: {e}", Fore.RED, "HYPERSQUAD")
    
    await_time = random.uniform(2, 4)
    time.sleep(await_time)
    
    # 4. Set user settings for more human-like behavior
    try:
        settings_payload = {
            "show_current_game": True,
            "default_guilds_restricted": False,
            "inline_attachment_media": True,
            "inline_embed_media": True,
            "gif_auto_play": True,
            "render_embeds": True,
            "render_reactions": True,
            "animate_emoji": True,
            "enable_tts_command": True,
            "message_display_compact": False,
            "convert_emoticons": True,
            "explicit_content_filter": 1,
            "disable_games_tab": False,
            "timezone_offset": -300,
            "theme": random.choice(["dark", "light"]),
            "developer_mode": False,
            "afk_timeout": 600,
            "locale": "en-US"
        }
        
        settings_headers = headers.copy()
        settings_headers['Referer'] = 'https://discord.com/channels/@me'
        
        res = session.patch("https://discord.com/api/v9/users/@me/settings", 
                           json=settings_payload, headers=settings_headers, timeout=10)
        if res.status_code == 200:
            log("User settings optimized", Fore.GREEN, "SETTINGS")
            success_count += 1
        else:
            log(f"Settings update failed: {res.status_code} - {res.text}", Fore.YELLOW, "SETTINGS")
    except Exception as e:
        log(f"Error updating settings: {e}", Fore.YELLOW, "SETTINGS")
    
    # Summary - Only return True if ALL 4 processes succeed
    if success_count == 4:
        log(f"Humanization completed successfully! (4/4 features)", Fore.GREEN, "HUMANIZE")
        return True
    elif success_count >= 2:
        log(f"Partial humanization successful ({success_count}/4 features)", Fore.YELLOW, "HUMANIZE")
        return False  # Changed to False since not all processes succeeded
    else:
        log(f"Humanization mostly failed ({success_count}/4 features)", Fore.RED, "HUMANIZE")
        return False

def extract_verification_link_from_content(content, email_type="text"):
    """Extract verification link from email content using multiple methods"""
    if not content:
        return None
    
    url_patterns = [
        r'https?://(?:discord\.com|discordapp\.com)/verify[^\s<>"\']+',
        r'https?://(?:discord\.com|discordapp\.com)/api/auth/verify[^\s<>"\']+',
        r'https?://click\.discord\.com/[^\s<>"\']+',
        r'https?://[^\s<>"\']*discord[^\s<>"\']*[?&]token=[^\s<>"\'&]+',
        r'https?://[^\s<>"\']*discord[^\s<>"\']*[^\s<>"\']*(?:verify|confirm|activate)[^\s<>"\']*',
        r'https?://[^\s<>"\']*(?:discord\.com|discordapp\.com)[^\s<>"\']*[a-zA-Z0-9_-]{20,}[^\s<>"\']*'
    ]
    
    found_urls = []
    
    for pattern in url_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            clean_url = match.rstrip('.,;)]}"\'>').strip()
            
            if email_type == "html":
                clean_url = clean_url.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            if clean_url and clean_url not in found_urls:
                found_urls.append(clean_url)
    
    return found_urls

def validate_discord_verification_url(url):
    """Validate if a URL is likely a Discord verification link"""
    if not url:
        return False, "Empty URL"
    
    url_lower = url.lower()
    
    if not any(domain in url_lower for domain in ['discord.com', 'discordapp.com']):
        return False, "Not a Discord domain"
    
    verification_indicators = [
        'verify', 'verification', 'confirm', 'activate', 'auth', 'token='
    ]
    
    has_verification_indicator = any(indicator in url_lower for indicator in verification_indicators)
    has_token_like_string = bool(re.search(r'[a-zA-Z0-9_-]{15,}', url))
    
    if has_verification_indicator and has_token_like_string:
        return True, "Valid verification URL"
    elif has_verification_indicator:
        return True, "Possible verification URL"
    elif 'discord.com' in url_lower and len(url) > 50:
        return True, "Possible Discord URL"
    else:
        return False, "Does not match verification patterns"

def is_verification_email(subject, text, html, sender):
    """Enhanced function to specifically identify Discord verification emails"""
    subject_lower = subject.lower()
    text_lower = text.lower() if text else ""
    html_lower = html.lower() if html else ""
    sender_lower = sender.lower()
    
    # Must be from Discord
    discord_senders = [
        "discord.com", "discordapp.com", "noreply@discord.com",
        "@discord.com", "@discordapp.com", "discord"
    ]
    
    is_from_discord = any(discord_sender in sender_lower for discord_sender in discord_senders)
    if not is_from_discord:
        return False
    
    # Primary verification email indicators (high priority)
    primary_verification_keywords = [
        "verify your email", "email verification", "verify email address", 
        "confirm your email", "email confirmation", "activate your account",
        "verification required", "please verify", "verify account"
    ]
    
    # Secondary verification indicators
    secondary_verification_keywords = [
        "verify", "verification", "confirm", "activate",
    ]
    
    # Check for primary keywords first (most accurate)
    for keyword in primary_verification_keywords:
        if keyword in subject_lower or keyword in text_lower or keyword in html_lower:
            log(f"Primary verification email detected: '{keyword}' found", Fore.GREEN, "EMAIL_FILTER")
            return True
    
    # Check for secondary keywords with additional validation
    has_secondary_keyword = any(keyword in subject_lower for keyword in secondary_verification_keywords)
    
    if has_secondary_keyword:
        # Additional validation for secondary keywords
        verification_content_indicators = [
            "click", "link", "button", "verify", "confirm", "activate", "token"
        ]
        
        has_verification_content = any(
            indicator in text_lower or indicator in html_lower 
            for indicator in verification_content_indicators
        )
        
        if has_verification_content:
            log(f"Secondary verification email detected with content validation", Fore.GREEN, "EMAIL_FILTER")
            return True
    
    # Exclude non-verification emails
    exclusion_keywords = [
        "password reset", "login attempt", "security alert", "new login",
        "suspicious activity", "password changed", "settings updated",
        "newsletter", "notification", "friend request", "message",
        "server invite", "payment", "billing", "receipt"
    ]
    
    for exclusion in exclusion_keywords:
        if exclusion in subject_lower or exclusion in text_lower:
            log(f"Email excluded: '{exclusion}' found", Fore.YELLOW, "EMAIL_FILTER")
            return False
    
    return False

def get_verification_link(email):
    """Get verification link from email with enhanced filtering for verification emails only"""
    log("Waiting for verification email...", Fore.CYAN, "VERIFY")
    
    processed_email_ids = set()
    
    for i in range(150):
        try:
            check_interval = random.uniform(2.5, 3.5)
            
            res = requests.post(RESULT_API_URL, headers=EMAIL_HEADERS, json={"email": email, "parse_links": True}, timeout=15)
            
            if res.status_code == 200:
                data = res.json().get("data", [])
                
                if not data:
                    if i % 10 == 0:
                        log(f"Checking inbox... ({i+1}/30)", Fore.YELLOW, "VERIFY")
                else:
                    log(f"Found {len(data)} email(s), filtering for verification emails...", Fore.CYAN, "VERIFY")
                    
                    try:
                        data.sort(key=lambda x: x.get('timestamp', x.get('date', 0)), reverse=True)
                    except:
                        pass
                    
                    verification_emails_found = 0
                    
                    for email_idx, mail in enumerate(data):
                        email_id = f"{mail.get('subject', '')[:50]}_{mail.get('from', '')}"
                        if email_id in processed_email_ids:
                            continue
                        
                        subject = mail.get("subject", "")
                        text = mail.get("text", "")
                        html = mail.get("html", "")
                        sender = mail.get("from", "")
                        
                        # Enhanced filtering - only process actual verification emails
                        if not is_verification_email(subject, text, html, sender):
                            log(f"Skipping non-verification email: {subject[:40]}...", Fore.YELLOW, "EMAIL_FILTER")
                            continue
                        
                        verification_emails_found += 1
                        log(f"Processing verification email: {subject[:40]}...", Fore.GREEN, "VERIFY")
                        processed_email_ids.add(email_id)
                        
                        verification_urls = []
                        
                        # Extract from structured links
                        if "links" in mail and mail["links"]:
                            for idx, link in enumerate(mail["links"]):
                                link_url = link.get("url", "")
                                
                                if link_url:
                                    is_valid, reason = validate_discord_verification_url(link_url)
                                    
                                    if is_valid:
                                        verification_urls.append(("structured_link", link_url, f"Link {idx+1}"))
                        
                        # Extract from text content
                        if text:
                            text_urls = extract_verification_link_from_content(text, "text")
                            for url in text_urls:
                                is_valid, reason = validate_discord_verification_url(url)
                                if is_valid:
                                    verification_urls.append(("text_content", url, reason))
                        
                        # Extract from HTML content
                        if html:
                            html_urls = extract_verification_link_from_content(html, "html")
                            for url in html_urls:
                                is_valid, reason = validate_discord_verification_url(url)
                                if is_valid:
                                    verification_urls.append(("html_content", url, reason))
                        
                        # Remove duplicates
                        seen_urls = set()
                        unique_verification_urls = []
                        for source, url, description in verification_urls:
                            if url not in seen_urls:
                                seen_urls.add(url)
                                unique_verification_urls.append((source, url, description))
                        
                        # Return first valid URL found
                        if unique_verification_urls:
                            priority_order = ["structured_link", "text_content", "html_content"]
                            
                            for priority_source in priority_order:
                                for source, url, description in unique_verification_urls:
                                    if source == priority_source:
                                        log(f"Verification URL found from {source}: {url[:50]}...", Fore.GREEN, "VERIFY")
                                        return url
                            
                            # Fallback to first URL if no priority match
                            source, url, description = unique_verification_urls[0]
                            log(f"Verification URL found: {url[:50]}...", Fore.GREEN, "VERIFY")
                            return url
                        else:
                            log(f"No verification URLs found in this email", Fore.YELLOW, "VERIFY")
                    
                    if verification_emails_found == 0:
                        log(f"No verification emails found among {len(data)} emails", Fore.YELLOW, "EMAIL_FILTER")
            
            elif res.status_code == 429:
                log("Rate limited, waiting longer...", Fore.YELLOW, "VERIFY")
                time.sleep(10)
                continue
            else:
                if i % 20 == 0:
                    log(f"Email API error: {res.status_code}", Fore.YELLOW, "VERIFY")
        
        except requests.exceptions.Timeout:
            if i % 15 == 0:
                log("Email API timeout, retrying...", Fore.YELLOW, "VERIFY")
        except Exception as e:
            if i % 20 == 0:
                log(f"Error fetching email: {str(e)[:50]}...", Fore.RED, "VERIFY")
        
        time.sleep(check_interval)
    
    log("Verification email not received in time", Fore.RED, "VERIFY")
    return None

def random_username():
    """Generate random username"""
    prefixes = ["stylish_dude_88", "the_desi_dude", "boy_with_swag", "the_urban_dude", "the_boy_in_black", "the_cool_guy_next_door", "the_funky_boy", "the_boy_with_the_swag", "the_boy_with_the_style", "the_boy_with_the_attitude", "Mr_cool_personality", "the_boy_with_the_smile", "the_boy_with_the_edge", "Mr_cool_king", "The_Geek_Genius", "The_Nerd_Whiz", "The_Guru_of_Gadgets", "The_Game_Master", "Mr_Futuristic", "Midnight_Rider", "Shark_Slayer", "The_Inventor_King", "Adrenaline_Junkie", "Danger_Zone_Dude", "Fast_Furious", "Stylish_stud", "Fearless_Fighter_26", "Daring_Dude_28", "Resourceful_Racer_12", "Rebellious_Rocker_13", "Sharp_Shooter_8", "Crazy_Carpenter_22", "Jaunty_Juggler_12", "Wild_Wanderer_2", "Hyper_Hipster_73", "Ambitious_Athlete_38", "Crazy_dude_19", "Unique_Urbanite_32", "Irreverent_Innovator_47", "Brazen_Biker_95", "Unruly_Urbanite_02", "Impetuous_Illusionist_90", "NutsNerd", "WildChildGuy", "FreakyFella", "CrazyCobraKid", "WildWonderBoy", "DarindDude7", "LoopyLad", "ManiacMuscleMan", "FierceFighterDude", "InstaTrendsetter_IG", "Mr_Fashionista_IG", "InstaStylist_IG", "InstaGamer_IG", "WildBoy_IG", "InstaSports_IG", "AlphaMale_IG", "RideOrDie_IG", "TechLover_IG", "KingOfTheCastle_IG", "MrAdventure_IG", "The_Vibrant_One", "Brave_Heart_B", "The_Mysterious_B", "Young_Vibe", "The_Joker_B", "The_Rough_Rider", "The_Free_Spirit_B", "The_Ambitious_One", "Trendy_B", "The_Daredevil_B", "The_Lucky_One", "The_Risk_Taker", "The_Lover_Boy", "King_of_the_City", "KingOfCool", "InstaDude", "DaredevilBoy", "EpicAdventurer", "MrSuperstar", "CoolBoyInTown", "InstaFashionista", "InstaMrTrendy", "TheEmojiiGuy", "MrViral", "AllStarGuy", "InstaJoker", "MrInstaFame", "KingOfStyle", "TheTrendsetter", "InstaMrCool", "InstaMrAdventure", "MrSuperhot", "Glamour_guy", "thestylish_dude", "swag_supreme", "swag_supreme", "traveler_guy", "fashion_frenzy", "mr_hype_dude", "Giggle_Guy", "The_Joke_King", "The_Funny_Guy", "Kidding_Around", "Mr_Laugh_A_Lot", "Humor_Hero", "Not_So_Serious_Guy", "Prankster_Master", "Silly_Boy_007", "Insta_Joker", "Mr_Funny_Boy", "Instagram_Fool", "Chuckle_Master", "Jokester_X", "The_Smiley_Face", "The_Laughing_Machine", "Mr._Punny", "Mr._Funny_Face", "The_Joke_Man", "Hot_Mess_Express", "The_Burp_King", "Mr._Ticklepants", "Master_of_Laughs", "The_Funny_Fella", "The_Giggle_Guru", "UrbanSwagger", "TrendsetterKing", "SophisticatedMan", "ClassyRebel", "TrendyGuru", "TheWarrior", "TheProdigy", "The_Viking", "TheNomad", "Royal_Maratha", "MrBadass", "MrAwe-Inspiring", "Dadofdevil", "MrUnstoppable", "TheTitan", "BossMan", "KingofStyle", "TheRuler", "FearlessFighter", "FearlessFirecracker", "BoldBoss", "TheBoldExplorer", "StyleIcon", "SwaggyKing", "TheBraveheart", "JazzyWolf", "SnazzyGuy", "SuaveDude", "FunkyRider", "BoldFella", "DrivenChap", "SlickSoul", "BrazenPrince", "EnigmaticChap", "GrittyRebel", "EdgyWarrior", "FunkyPrince", "BoldOperator", "SavageSheep", "SwagGuru", "AlphaDude", "CuriousChad", "HumbleSoul", "VibrantHero", "KoolKat", "Shotgun", "UpbeatQuirk", "LivelyOwl", "BitCrazy", "EpicLife", "CrazyKid", "DizzyGuy", "NostalgicGuy", "KingJolly", "BigtimeNerd", "MrRowdy", "GoofyPuppy", "BadBug", "GymWarrior", "PathFinder", "OyeNoob", "RoaringPanda", "Litnitwitz", "AlphaEndless", "Divinepedia"]

    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return random.choice(prefixes) + suffix

def random_disname():
    """Generate random displayname"""
    display_names = ["ntk13", "Glory", "Lil_Drippzz", "TheGlizzyGladiator", "Ooga Booga", "nicojustnico", "Nado", "Duck life 4 (IGN)", "OilyBuht", "pure", "villa", "EH", "ŠtârÄłêx", "𝕮𝖍𝖎𝖕𝖘𝖆𝖓𝖉𝕼𝖚𝖊𝖘𝖔", "Smurda", "Ipoketurtles", "A10WILDFIRE", "Athena The Doe", "Fwooji", "bnicccck", "Mr_Biggerz", "reapz", "Gene10101", "Boggers", "ungawdly", "ToHighToday", "sadTV", "Arvin", "AmITrippingOrWhatBro?", "Wokeie", "Dylaniz", "SANGOKU", "i_no_caleb", "Prodigy", "Rose Nynx", "nydasa", "beysu", "DigitalProtocol", "SlippIsTrash", "Wizzy", "W4vewalker", "Zarrx", "Nomiton", "Zenith", "xiffy", "! woc", "MasonGamerTV", "BlazinChill", "dboss", "FastBands", "Lxllo", "dissa", "KaisasPeachPics", "Flukeykhan", "HiImDusty", "DiamondTrail420", "Gobso", "dragonshark", "RoseLion", "ROBSACK", "Claxtys", "TTVItzyoboizae", "cl_modeshift- love exec +0", "Born2Sin", "TecH", "DrAndr3w", "Daemon", "ImmortalxKingx", "SCooBZGooBZ", "Nyx", "Legend 57", "Kegan", "Hiraeth", "b!", "lucky", "Glam", "urmomsanus101", "porkechop", "2in Punish3r", "RoadRunner", "Juxal", "Smelly", "Chriskolb00", "bxrclipz", "usingsmirnoff", "PERSON", "luc", "Ormsbee", "park bench", "Feenix", "YouThoughtBoi", "nasteigh", "crutches", "Musashi", "Bleach", "Mcvc", "xtopp3r", "Swrrve", "Karl", "Kyubi", "Nikö", "Im Feeling Toxic", "BestEarthWorm", "Jcue", "Keon", "cameronnn", "abandz", "InstinctualJedi", "YOIMHIM", "TTV_ShleptOn", "DMAXD", ".Peppermint.Butler.", "Benji", "vArsxnal", "CommanderPoyo🔆", "1nkblot", "IceKek", "Kilo", "yorvi_collado", "Rick-81x", "Nast", "ninja gaiden thugger", "Trixxster", "Spunky", "Mannyy", "XdemiseXx", "RTX controller", "ChickyNugggiesss", "Holyone", "Kylin", "nirusuki", "lilflame", "dreww", "jawn", "abyss", "ItsJustHell", "Dovah", "TheHandsomeJew", "Doomsdaystomp86", "T3mp3st1986", "SKII_Bunny", "YamiGhost", "TheMentist", "farcii", "Horizim", "Avenger90075", "cc.jayyy", "fez", "A$AP Dizz", "ConnorKaps", "Gandalf", "Domes4Daze20", "CrumbyIzCool", "Braiden", "GBleeezy", "delphini", "Case", "I yoshimitsu l", "jali", "Fear", "JayyGrizz", "Darkz", "Ǝvil", "crondo", "Rezzi", "mitch", "Northern Blue", "Wastah", "Someone.", "mymonitorisbrighterthanmyfuture", "Craven_Moorhead", "Clxsys", "ZapGriz", "zMorphin", "S0L0", "Sinez", "hasantsu", "Hayden|", "Sovernit", "Shane", "evin", "oOK1RAa", "BMO", "debru", "RichyRich.", "Saedah", "FlawlessVP", "†bogan†", "JayMp", "Hazel", "oLycra", "Xstallion777", "Imperial", "scarykosi", "Jibb", "Raankoraav", "Moon<3", "T4H4", "Apex Legends ModMail", "bee~", "Capgun", "iGali1eo", "JackDaniel", "SpecificZod", "THECARPETDEMON", "davidvanbeveren", "Cynn", "digtw0graves", "Kinder", "lukexlft", "MisterDrProf", "Swift", "zinon", "garret", "Sani", "BOTSPIKE", "Dazs", "hodsic", "kirito.rip", "OoeyGooee", "Revan", "stuhni", "Apex Stats", "Beemo", "Zeppelin", "MRVN LFG", "Streamcord", "YAGPDB.xyz", "Your Father", "! Sydarina", "!!ᐱz𝚊ṛᐱ༏ෆ𝘴!!", "Vynadium", "Whyze", "leekon", "Insulted", "a7x", "ActuallyyKevinTV", "bored", "AlterNiteGaming_YT", "Anos Voldigoad", "ApoIIo", "applejUiCe", "archermoment", "Astolfo", "Decahexic", "BSevenKilo", "Baa", "Bats", "BlueJay", "calciferr", "Carrot", "Cqt", "Centricks", "chef", "Chill", "Commander Mars", "Cupcake", "Dempsey😘", "DinoSnax", "DJaysAve", "DunceChungus", "esme!", "Fana", "fes", "Garou the hero hunter", "Psykho", "Pieca", "Hawkster", "Hmm", "HoldMyDog", "hu!", "i like soup 2", "hinata.dragneel", "Ignited", "iiAvy", "♡ Glacy ♡", "Juiced", "IrohThe3rd", "Izuwuphrダーク", "Idk...", "Jadey Pie", "jazzyu", "JdMfX_", "JΩHΠШRLD", "Kalixyッ", "Kaseyy ^_^", "Katz", "La Gata", "lolyツ", "Loomy", "Luce", "Mara", "Meah!", "merky", "novi", "MsV1bez", "nezu", "nimokiru", "NoobAidan", "mocha!!", "pogmaa", "Pregnant Yoda", "Mushka", "Psyco", "RACCOON", "rephii", "Schmoozer", "Shiny", "ShockViper", "salursk", "skidaddle", "Smile moreジ", "smileyivan18", "Snips", "Sticero", "stoobi", "mav!", "Morty", "Ｖｏｒｔｅｘ", "Biggls", "Omplaty", "unforgivable", "Uno", "digitaldevil", "vert", "Useless Teal Protogen", "Xelonor", "yeju", "User", "Gamer", "Player", "Pro", "Cool", "Epic", "Super", "Master", "Elite", "Alpha"]

    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return random.choice(display_names) + suffix

def random_password():
    """Generate secure random password"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=12))

async def wait_for_multiple_selectors(page, selectors, timeout=30):
    """Wait for any of the provided selectors and return the first found element"""
    for _ in range(timeout * 2):
        for selector in selectors:
            el = await page.query_selector(selector)
            if el:
                return el, selector
        await asyncio.sleep(0.5)
    raise Exception(f"Timeout waiting for selectors")

async def fill_form_field(page, field_name, value, selectors_list):
    """Try multiple selectors to fill a form field"""
    try:
        element, used_selector = await wait_for_multiple_selectors(page, selectors_list, 15)
        await element.send_keys(value)
        log(f"{field_name} filled successfully", Fore.GREEN, "FORM")
        return True
    except Exception as e:
        log(f"Failed to fill {field_name}", Fore.RED, "FORM")
        return False

async def click_dropdown_item_with_js(page, label):
    """Click dropdown item using JavaScript"""
    try:
        await asyncio.sleep(1)
        js = f"""(function() {{
            const elements = document.querySelectorAll('div, span, button');
            for (let element of elements) {{
                if (element.innerText && element.innerText.trim() === "{label}") {{
                    element.click();
                    return true;
                }}
            }}
            return false;
        }})();"""
        result = await page.evaluate(js)
        if result:
            log(f"Selected: {label}", Fore.GREEN, "FORM")
        await asyncio.sleep(1)
    except Exception as e:
        log(f"Failed to select {label}", Fore.RED, "FORM")

async def detect_captcha(page):
    """Detect if CAPTCHA is present on the page"""
    captcha_selectors = [
        'iframe[src*="captcha"]', 'iframe[src*="recaptcha"]', 'iframe[src*="hcaptcha"]',
        'div[class*="captcha"]', 'div[class*="recaptcha"]', 'div[class*="hcaptcha"]',
        '[data-sitekey]', '.h-captcha', '.g-recaptcha', '#captcha', '[id*="captcha"]'
    ]
    
    for selector in captcha_selectors:
        element = await page.query_selector(selector)
        if element:
            return True
    
    page_content = await page.get_content()
    captcha_indicators = [
        "captcha", "recaptcha", "hcaptcha", "challenge", 
        "verify you are human", "prove you're not a robot"
    ]
    
    for indicator in captcha_indicators:
        if indicator.lower() in page_content.lower():
            return True
    
    return False

async def wait_for_complete_form(page, timeout=60):
    """Wait for ALL registration form fields to be available"""
    try:
        log(" Waiting for complete registration form...", Fore.CYAN, "FORM")
        
        # All required form selectors
        required_selectors = [
            'input[name="email"], input[type="email"]',
            'input[name="username"]', 
            'input[name="password"], input[type="password"]'
        ]
        
        for i in range(timeout):
            all_ready = True
            
            for selector_group in required_selectors:
                # Check if at least one selector from each group exists
                selectors = [s.strip() for s in selector_group.split(',')]
                found = False
                
                for selector in selectors:
                    element = await page.query_selector(selector)
                    if element:
                        found = True
                        break
                
                if not found:
                    all_ready = False
                    break
            
            if all_ready:
                log(" Complete registration form ready!", Fore.GREEN, "FORM")
                await asyncio.sleep(1)  # Small delay for stability
                return True
                
            await asyncio.sleep(0.5)
        
        log(" Complete form not ready within timeout", Fore.RED, "FORM")
        return False
        
    except Exception as e:
        log(f" Error waiting for complete form: {e}", Fore.RED, "FORM")
        return False


async def create_discord_account():
    """Create a single Discord account with undetectable Chrome usage"""
    global tokens_generated
    
    email = get_email_from_api()
    if not email:
        return False

    username = random_username()
    disname = random_disname()
    password = random_password()
    servers_joined = 0

    try:
        # Configure browser for maximum stealth
        browser = await zd.start(
            headless=False,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        )
        
        log("Opening Discord registration page...", Fore.CYAN, "BROWSER")
        page = await browser.get("https://discord.com/register")
        

        # Enhanced form field selectors
        email_selectors = [
            'input[name="email"]', 
            'input[type="email"]', 
            'input[placeholder*="email" i]',
            'input[aria-label*="email" i]', 
            'input[data-testid*="email"]', 
            'input[id*="email"]',
            'input[autocomplete="email"]'
        ]
        
        username_selectors = [
            'input[name="username"]', 
            'input[placeholder*="username" i]',
            'input[aria-label*="username" i]', 
            'input[data-testid*="username"]',
            'input[autocomplete="username"]'
        ]
        
        global_name_selectors = [
            'input[name="global_name"]', 
            'input[name="globalName"]',
            'input[placeholder*="display" i]', 
            'input[aria-label*="display" i]',
            'input[data-testid*="display"]'
        ]
        
        password_selectors = [
            'input[name="password"]', 
            'input[type="password"]',
            'input[placeholder*="password" i]', 
            'input[aria-label*="password" i]',
            'input[autocomplete="new-password"]'
        ]

        if not await wait_for_complete_form(page, 60):
            log("❌ Registration form not fully loaded, retrying...", Fore.RED, "BROWSER")
            await browser.stop()
            return False


        log("Filling registration form...", Fore.CYAN, "FORM")
    
        log(" Starting form filling immediately...", Fore.GREEN, "FORM")
        
        # Fill form fields with human-like delays
        if not await fill_form_field(page, "Email", email, email_selectors):
            await browser.stop()
            return False
        
        await asyncio.sleep(1)
        
        if not await fill_form_field(page, "Username", username, username_selectors):
            await browser.stop()
            return False
        
        await asyncio.sleep(1)
        
        await fill_form_field(page, "Display Name", disname, global_name_selectors)
        await asyncio.sleep(1)
        
        if not await fill_form_field(page, "Password", password, password_selectors):
            await browser.stop()
            return False
        
        await asyncio.sleep(2)

        # Date of birth selection with current date awareness
        try:
            log("Setting date of birth...", Fore.CYAN, "FORM")
            
            month_selectors = [
                'div[class*="month"]', 
                'select[name*="month"]', 
                'div[data-testid*="month"]',
                'button[aria-label*="month"]'
            ]
            
            try:
                month_element, _ = await wait_for_multiple_selectors(page, month_selectors, 10)
                await month_element.mouse_click("left")
                await asyncio.sleep(1)
                await click_dropdown_item_with_js(page, "May")
            except Exception as e:
                log("Month selection failed", Fore.YELLOW, "FORM")
            
            day_selectors = [
                'div[class*="day"]', 
                'select[name*="day"]', 
                'div[data-testid*="day"]',
                'button[aria-label*="day"]'
            ]
            
            try:
                day_element, _ = await wait_for_multiple_selectors(page, day_selectors, 10)
                await day_element.mouse_click("left")
                await asyncio.sleep(1)
                date_day = random.randint(1, 28)
                await click_dropdown_item_with_js(page, str(date_day))  # Current date
            except Exception as e:
                log("Day selection failed", Fore.YELLOW, "FORM")
            
            year_selectors = [
                'div[class*="year"]', 
                'select[name*="year"]', 
                'div[data-testid*="year"]',
                'button[aria-label*="year"]'
            ]
            
            try:
                year_element, _ = await wait_for_multiple_selectors(page, year_selectors, 10)
                await year_element.mouse_click("left")
                await asyncio.sleep(1)
                # Use a birth year that makes the account adult (18+)
                birth_year = random.randint(1990, 2003)
                await click_dropdown_item_with_js(page, str(birth_year))
            except Exception as e:
                log("Year selection failed", Fore.YELLOW, "FORM")
                
        except Exception as e:
            log("DOB selection failed", Fore.YELLOW, "FORM")

        # Enhanced terms checkbox handling
        try:
            checkbox_selectors = [
                'div[role="checkbox"]', 
                'input[type="checkbox"]',
                'button[role="checkbox"]', 
                'span[role="checkbox"]',
                '[data-testid*="terms"]',
                '[aria-label*="terms"]'
            ]
            
            checkbox_element, _ = await wait_for_multiple_selectors(page, checkbox_selectors, 10)
            await checkbox_element.mouse_click("left")
            log("Terms accepted", Fore.GREEN, "FORM")
        except Exception as e:
            log("Terms checkbox failed", Fore.YELLOW, "FORM")

        await asyncio.sleep(1.5)

        # Enhanced submit button handling
        try:
            submit_selectors = [
                "button[type='submit']", 
                "input[type='submit']",
                "button[data-testid*='submit']", 
                "button[class*='submit']",
                "button[aria-label*='submit']",
                "button:contains('Continue')",
                "button:contains('Register')"
            ]
            
            submit_element, _ = await wait_for_multiple_selectors(page, submit_selectors, 10)
            await submit_element.mouse_click("left")
            log("Registration submitted", Fore.GREEN, "FORM")
        except Exception as e:
            log("Failed to submit registration", Fore.RED, "FORM")
            await browser.stop()
            return False

        await asyncio.sleep(2.5)

        # Enhanced CAPTCHA handling
        captcha_detected = await detect_captcha(page)
        
        if captcha_detected:
            print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}CAPTCHA DETECTED!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please solve the CAPTCHA manually in the browser.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}After solving, press ENTER to continue...{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
            
            await wait_for_user_input("")
            log("Continuing after CAPTCHA solution...", Fore.GREEN, "CAPTCHA")
            await asyncio.sleep(2)
        else:
            log("No CAPTCHA detected", Fore.GREEN, "CAPTCHA")
            await asyncio.sleep(1)

        # Enhanced email verification process
        link = get_verification_link(email)
        if link:
            log("Opening verification link...", Fore.CYAN, "VERIFY")
            try:
                verification_page = await browser.get(link, new_tab=True)
                await asyncio.sleep(0.5)
                
                print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}EMAIL VERIFICATION TAB OPENED!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Complete the verification and press ENTER to continue...{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
                
                await wait_for_user_input("")
                log("Email verification completed", Fore.GREEN, "VERIFY")
                
                try:
                    await verification_page.close()
                except:
                    pass
                
                await page.reload()
                await asyncio.sleep(4)
                
            except Exception as e:
                log(f"Verification error: {e}", Fore.RED, "VERIFY")
        else:
            log("No verification email found", Fore.RED, "VERIFY")
            await browser.stop()
            return False

        # Get token with enhanced error handling
        log("Retrieving token...", Fore.CYAN, "TOKEN")
        token = get_token(email, password)
        
        if token:
            # Enhanced API humanization
            log(" Starting API token humanization...", Fore.CYAN, "HUMANIZE")
            humanization_success = humanize_token(token)
            
            # Browser-based server joining 
            log(" Starting non cap token maker......", Fore.CYAN, "NON-CAP")
            servers_joined = await join_discord_servers(page, 1)
            
            # Save token data (multiple methods)
            log(" Saving token data...", Fore.CYAN, "SAVE")
            
            # 1. Send to dashboard (updated with servers_joined)
            dashboard_success = send_token_to_dashboard(email, password, token, humanization_success, servers_joined)
            
            
            # Update tokens generated counter
            tokens_generated += 1
            
            # Enhanced success reporting with server join status (updated for 1 server)
            if humanization_success and servers_joined == 1:
                log(" Account created and fully humanized with successful server joining!", Fore.GREEN, "SUCCESS")
            elif humanization_success:
                log(" Account created and humanized but failed server joining", Fore.YELLOW, "SUCCESS")
            elif servers_joined == 1:
                log(" Account created with successful server joining but incomplete humanization", Fore.YELLOW, "SUCCESS")
            else:
                log(" Account created with minimal humanization and no server joining", Fore.RED, "SUCCESS")
            
            log(f" Final Stats - Humanized: {humanization_success} | Server: {servers_joined}/1", Fore.CYAN, "STATS")
            
            if dashboard_success:
                log(" Token data saved to database", Fore.GREEN, "SUCCESS")
            else:
                log(" Database save failed", Fore.YELLOW, "ERROR")
            
                
            await browser.stop()
            return True
        else:
            log(" Failed to retrieve token", Fore.RED, "TOKEN")
            await browser.stop()
            return False

    except Exception as e:
        log(f" Account creation error: {e}", Fore.RED, "ERROR")
        if 'browser' in locals():
            await browser.stop()
        return False

def display_stats():
    """Display current statistics"""
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN} Tokens Generated: {tokens_generated}{Style.RESET_ALL}")
    print(f"{Fore.CYAN} Next Generation: 5 seconds{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

async def main():
    """Main function - continuous token generation with server joining (1 server)"""
    # Clear screen and show banner
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Colorate.Vertical(Colors.purple_to_blue, Center.XCenter(BANNER)))
    print(Colorate.Vertical(Colors.green_to_blue, Center.XCenter(BANNER1)))
    
    # Load configuration and verify license
    load_config()
    verify_license()
    
    # Check dashboard status
    dashboard_online = check_dashboard_status()
    if not dashboard_online:
        log("Dashboard is offline", Fore.RED, "DATABASE")
        input("Press Enter to exit...")
        exit()
    
    log(" Starting continuous token generation...", Fore.GREEN, "SYSTEM")
    log(f" Licensed to: {discord_id}", Fore.CYAN, "LICENSE")
    
    while True:
        try:
            log(f" Starting account creation cycle #{tokens_generated + 1}...", Fore.CYAN, "CYCLE")
            
            success = await create_discord_account()
            
            if success:
                display_stats()
                log(" Waiting 5 seconds before next generation...", Fore.CYAN, "CYCLE")
                
                # Enhanced countdown with better visual feedback
                for i in range(5, 0, -1):
                    dots = '.' * (4 - (i % 4))
                    spaces = ' ' * (i % 4)
                    print(f"\r{Fore.YELLOW} Next generation in: {i:2d} seconds {dots}{spaces}{Style.RESET_ALL}", end='', flush=True)
                    time.sleep(1)
                print()  # New line after countdown
                
            else:
                log(" Account creation failed, retrying in 5 seconds...", Fore.RED, "CYCLE")
                for i in range(5, 0, -1):
                    print(f"\r{Fore.RED} Retrying in: {i:2d} seconds...{Style.RESET_ALL}", end='', flush=True)
                    time.sleep(1)
                print()
                
        except KeyboardInterrupt:
            log(" Stopping token generation by user request...", Fore.YELLOW, "SYSTEM")
            break
        except Exception as e:
            log(f" Unexpected error: {e}", Fore.RED, "ERROR")
            log(" Retrying in 5 seconds...", Fore.YELLOW, "SYSTEM")
            for i in range(5, 0, -1):
                print(f"\r{Fore.YELLOW} Retrying in: {i:2d} seconds...{Style.RESET_ALL}", end='', flush=True)
                time.sleep(1)
            print()
    
    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN} Total Tokens Generated: {tokens_generated}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    log(" Token generator stopped successfully", Fore.CYAN, "SYSTEM")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW} Program interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED} Fatal error: {e}{Style.RESET_ALL}")
        input("Press Enter to exit...")