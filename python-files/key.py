import asyncio
import random
import string
import requests  # For license verification
import zendriver as zd
from colorama import Fore, init

init(autoreset=True)

# URL to your license key list (update this!)
LICENSE_URL = "https://gist.githubusercontent.com/PrasoonAgarwal0/0c30065a1a3d983661669a2e439f4f77/raw/85a38677b30aa02a793c1cca845c1b26a4bc7554/licenses.txt"

def log(msg, color=Fore.WHITE, prefix='ℹ️'):
    print(f'{color}[{prefix}] {msg}')

def verify_license(key):
    try:
        response = requests.get(LICENSE_URL, timeout=10)
        if response.status_code == 200:
            valid_keys = response.text.strip().splitlines()
            return key.strip() in valid_keys
        else:
            log(f"⚠️ Failed to fetch license list (status {response.status_code})", Fore.YELLOW)
            return False
    except Exception as e:
        log(f"❌ License check error: {e}", Fore.RED)
        return False

def random_username():
    return 'Coder' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def save_to_file(email, username, password):
    with open("accounts.txt", "a") as f:
        f.write(f"Email: {email}\n")
        f.write(f"Username: {username}\n")
        f.write(f"Password: {password}\n")
        f.write("-" * 26 + "\n")

async def wait_for_selector(page, selector, timeout=15):
    for _ in range(timeout * 2):
        el = await page.query_selector(selector)
        if el:
            return el
        await asyncio.sleep(0.5)
    raise Exception(f'Timeout waiting for selector: {selector}')

async def main(user_email):
    username = random_username()
    password = random_password()

    browser = await zd.start()
    log('Launching browser and opening registration page...', Fore.CYAN, '🌐')
    page = await browser.get('https://discord.com/register')
    await asyncio.sleep(7)

    log('Filling registration form...', Fore.CYAN, '📝')
    await (await wait_for_selector(page, 'input[name="email"]')).send_keys(user_email)
    await (await wait_for_selector(page, 'input[name="username"]')).send_keys(username)
    await (await wait_for_selector(page, 'input[name="global_name"]')).send_keys("Coder Tokens")
    await (await wait_for_selector(page, 'input[name="password"]')).send_keys(password)

    log('❗ DOB not filled. Please select it manually.', Fore.YELLOW)

    try:
        register_btn = await wait_for_selector(page, 'button[type="submit"]')
        await register_btn.click()
        log('✅ Clicked the Register button!', Fore.GREEN)
    except Exception as e:
        log(f'❌ Failed to click register button: {e}', Fore.RED)

    log(f'📧 Email: {user_email}', Fore.GREEN)
    log(f'👤 Username: {username}', Fore.GREEN)
    log(f'🔑 Password: {password}', Fore.GREEN)
    log('🧠 Solve CAPTCHA and fill DOB manually if needed.', Fore.YELLOW)

    save_to_file(user_email, username, password)
    log('💾 Saved to accounts.txt!', Fore.BLUE)

    input(Fore.CYAN + "\nPress Enter to close the browser and finish...")
    await browser.stop()
    log('🛑 Browser closed. Script done.', Fore.CYAN)

if __name__ == '__main__':
    license_key = input("🔐 Enter your license key: ").strip()
    if not verify_license(license_key):
        log("❌ Invalid license key. Exiting...", Fore.RED)
        exit()

    email = input("Enter your email address: ").strip()
    num_accounts = int(input('How many accounts do you want to create? '))
    for i in range(num_accounts):
        log(f'Creating account {i + 1}/{num_accounts}...', Fore.CYAN, '🌀')
        asyncio.run(main(email))
