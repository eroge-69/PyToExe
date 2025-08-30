import asyncio
import ctypes
from datetime import datetime
import math
import os
class Log:
    def title(title):
        ctypes.windll.kernel32.SetConsoleTitleW(title)

os.system('cls')
Log.title("Discord Token Gennerator")  
import aiohttp
from patchright.async_api import async_playwright
import random
import string
import requests
import re
import argparse
from colorama import init, Fore, Style
import time
from pystyle import Colors, Colorate



red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
orange = Fore.RED + Fore.YELLOW
pink = Fore.LIGHTMAGENTA_EX + Fore.LIGHTCYAN_EX
magenta = Fore.MAGENTA
lightblue = Fore.LIGHTBLUE_EX
cyan = Fore.YELLOW
gray = Fore.LIGHTBLACK_EX + Fore.WHITE
reset = Fore.RESET

def get_time_rn():
    date = datetime.now()
    hour = date.hour
    minute = date.minute
    second = date.second
    timee = "[ {:02d}:{:02d}:{:02d} ]".format(hour, minute, second)
    return timee


init(autoreset=True)


session = requests.Session()


def generate_realistic_name():
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", 
                   "alice", "bob", "charlie", "david", "eva",
                   "frank", "grace", "hannah", "ivy", "jack",
                   "katherine", "liam", "mason", "nora", "olivia",
                   "paul", "quincy", "rachel", "sam", "tom",
                   "ursula", "victor", "wendy", "xander", "yara",
                   "zach", "smith", "johnson", "williams", "brown", "jones",
                   "miller", "davis", "garcia", "martinez", "hernandez",
                   "lopez", "gonzalez", "perez", "wilson", "anderson",
                   "thomas", "taylor", "moore", "jackson", "martin",
                   "lee", "perez", "white", "harris", "clark"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    first = random.choice(first_names)
    last = random.choice(last_names)
    return f"{first}{random.randint(1, 999)}"

def generate_username(global_name):
    base = global_name.replace(" ", "").lower()
    return f"{base}{random.randint(1000, 9999)}"

def generate_alternative_username(base_username):
    return f"{base_username}{random.randint(10000, 99999)}"

def generate_strong_password():
    chars = (random.choices(string.ascii_lowercase, k=6) +
             random.choices(string.ascii_uppercase, k=2) +
             random.choices(string.digits, k=2) +
             random.choices("!@#$%^&*", k=1))
    random.shuffle(chars)
    return "".join(chars)

blocked_domains = ['gx.pigeonprotocol.com','pigeonprotocol.com', 'jailbreakeverything.com','8d.vertexium.net','vertexium.net', 'awesome47.com', 'm4.vertexium.net']

def domain_blocked(domain: str) -> bool:
    domain = domain.lower()
    for blocked in blocked_domains:
        blocked = blocked.lower()
        if domain == blocked or domain.endswith('.' + blocked):
            return True
    return False

def get_email():
    while True:
            try:
                r = requests.get('https://api.tempmail.lol/generate', timeout=10)
                if r.status_code != 200:
                    print("INFO", "GREEN", f"[!] Api Error Return...")
                    continue

                data = r.json()
                address = data.get("address")
                token = data.get("token")

                if address and token:
                    domain = address.split('@')[-1].lower()

                    if domain_blocked(domain):
                        print(f"[!] Domain Block: {domain} Return Domain...")
                        continue

                    return address, token

                else:
                    print(f"[!] don't have (address/token) Return...")

            except Exception as e:
                print(f"[!] Error: {e} Return...")

async def get_verification_link(token):
    found_link = False
    while not found_link:
        time.sleep(1)
        r = requests.get(f"https://api.tempmail.lol/v2/inbox?token={token}")
        json_data = r.json()
        emails = json_data.get("emails", [])
        for email in emails:
            subject = email.get("subject", "")
            if subject == "ยืนยันที่อยู่อีเมลกับ Discord" or subject == "Verify Email Address for Discord":
                body = email.get("body", "")
                if "Thanks for registering for an account on Discord!" in body:
                    all_links = re.findall(r'https://click\.discord\.com/ls/click\?[^"]+', body)
                    if all_links:
                        found_link = True
                        return all_links[0]

async def fill_registration_form(page, email, global_name, username, password):
    await page.goto("https://discord.com/register")
    await page.locator("input[name='email']").fill(email)
    await page.locator("input[name='global_name']").fill(global_name)

    for _ in range(5):
        await page.locator("input[name='username']").fill(username)
        await asyncio.sleep(1)
        error = await page.evaluate("""() => document.querySelector('[class*="errorMessage"]')?.textContent""")
        if not error or "Username is unavailable" not in error:
            break
        username = generate_alternative_username(username)
        print(f"{Fore.YELLOW}Username taken, trying new username: {username}")

    await page.locator("input[name='password']").fill(password)

    await page.locator(".month_b0f4cc").click()
    await page.locator("[id*='-option-4']").first.click()
    await page.locator(".day_b0f4cc").click()
    await page.locator("[id*='-option-4']").first.click()
    await page.locator(".year_b0f4cc").click()
    await page.locator("div[class*='option']").filter(has_text="1999").first.click()

    await page.locator("input[type='checkbox']").click()
    await page.locator("button[type='submit']").click()

    await asyncio.sleep(2)
    error_message = await page.evaluate("""() => document.querySelector('[class*="errorMessage"]')?.textContent""")
    if error_message:
        print(f"{Fore.RED}Registration error for {username}: {error_message}")
        return False, username
    return True, username

async def handle_verification(context, email_token):
    print(f"{pink}{get_time_rn()}{reset} Waiting verification link ⏰")
    verification_link = await get_verification_link(email_token)
    if verification_link:
        print(f"{pink}{get_time_rn()}{reset} Verification Link", verification_link)
        verification_page = await context.new_page()
        await verification_page.goto(verification_link)
        await verification_page.wait_for_load_state('networkidle')
        
        await asyncio.sleep(10)
        
        await verification_page.close()
        print(f"{pink}{get_time_rn()}{reset} Verification completed ✅")
        return True 
    return False


async def get_discord_token(email, password):
    url = 'https://discord.com/api/v10/auth/login'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Accept-Encoding': 'gzip, compress, deflate, br'
    }
    payload = {
        'login': email,
        'password': password  
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            token = response.json().get('token')
            return token
        else:
            print(f'Error: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'Error during login: {e}')

async def register_discord_account(headless=False, window_id=1, num_windows=1):
    global_name = generate_realistic_name()
    username = generate_username(global_name)

    email, password = get_email()  

    print(f"{pink}{get_time_rn()}{reset} Name: {global_name}")
    print(f"{pink}{get_time_rn()}{reset} Username: {username}")
    print(f"{pink}{get_time_rn()}{reset} Email: {email}")
    print(f"{pink}{get_time_rn()}{reset} Password: {password}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(viewport={"width": 800, "height": 600})
        page = await context.new_page()

        try:
            success, username = await fill_registration_form(page, email, global_name, username, password)

            if not success:
                return False

            if password:
                verification_success = await handle_verification(context, password)
                if verification_success:
                    print(f"{pink}{get_time_rn()}{reset} Email verified successfully ✅")
                    token = await get_discord_token(email, password)
                    if token:
                        print(f"{pink}{get_time_rn()}{reset} Token: {token[:25]}***")
                        with open("tokens.txt", "a") as f:
                            f.write(f"{email}:{password}:{token}\n")
                    else:
                        print(f"{Fore.RED}Failed to retrieve token")
                else:
                    print(f"{Fore.YELLOW}Verification failed")
            else:
                print(f"{Fore.YELLOW}No email token available")

            return True
        except Exception as e:
            print(f"{Fore.RED}Error during registration: {str(e)}")
            return False
        finally:
            await asyncio.sleep(5)
            await browser.close()

async def main(num_accounts, headless, infinite_loop=False):
    banner = rf"""
     ____  ___  _______________   _____ ___  _______  ______  ______   ________  ___   __
    / __ \/   |/_  __/_  __/   | / ___//   |/_  __/ |/ / __ \/ ____/  / ____/ / / / | / /
   / /_/ / /| | / /   / / / /| | \__ \/ /| | / /  |   / / / / /      / /_  / / / /  |/ / 
  / _, _/ ___ |/ /   / / / ___ |___/ / ___ |/ /  /   / /_/ / /___   / __/ / /_/ / /|  /  
 /_/ |_/_/  |_/_/   /_/ /_/  |_/____/_/  |_/_/  /_/|_\___\_\____/  /_/    \____/_/ |_/   
                                                                                        
                 TOKEN GENERATOR NEW RECODE NEXT NEXT NEXT ! ! !
                 
"""
    print(Colorate.Vertical(Colors.blue_to_cyan, banner, 1))
    print(F"{pink}{get_time_rn()}{reset} Starting Discord Token Generator...")
    success_count = 0
    attempt_count = 0

    while True:
        if not infinite_loop and attempt_count >= num_accounts:
            break

        attempt_count += 1

        success = await register_discord_account(headless)
        if success:
            success_count += 1

        print(f"\n{Fore.MAGENTA}Summary: {success_count}/{attempt_count} accounts created successfully")
        
        if infinite_loop:
            print(f"{Fore.YELLOW}Waiting 2 minutes before next attempt...")
            await asyncio.sleep(80) 
        else:
            if attempt_count < num_accounts:
                print(f"{Fore.YELLOW}Waiting 2 minutes before next attempt...")
                await asyncio.sleep(80) 

    print(f"\n{Fore.GREEN}All tasks completed! Total: {success_count}/{attempt_count} accounts created.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Discord Account Registration Bot")
    parser.add_argument("--num-accounts", type=int, default=20, help="Number of accounts to register (default: 20)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--infinite", action="store_true", help="Run in infinite loop")
    args = parser.parse_args()

    asyncio.run(main(args.num_accounts, args.headless, args.infinite))
