from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import requests
import time
import random
import string
import secrets
import re

MAIL_TM_API = "https://api.mail.tm"

def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_username():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def create_temp_mail_account():
    # 1. Get list of valid domains
    domain_res = requests.get(f"{MAIL_TM_API}/domains")
    domains = domain_res.json()["hydra:member"]

    if not domains:
        raise Exception("❌ No valid domains available on mail.tm")

    domain = random.choice(domains)["domain"]
    username = generate_username()
    email = f"{username}@{domain}"
    password = generate_password()

    # 2. Create new account
    res = requests.post(f"{MAIL_TM_API}/accounts", json={
        "address": email,
        "password": password
    })

    if res.status_code != 201:
        raise Exception(f"Failed to create account: {res.text}")

    # 3. Login to get token
    login = requests.post(f"{MAIL_TM_API}/token", json={
        "address": email,
        "password": password
    })

    if login.status_code != 200:
        raise Exception(f"Failed to login: {login.text}")

    token = login.json()["token"]
    return email, password, token


def wait_for_verification_email(token, timeout=90):
    headers = {"Authorization": f"Bearer {token}"}
    start_time = time.time()

    while time.time() - start_time < timeout:
        messages = requests.get(f"{MAIL_TM_API}/messages", headers=headers).json()
        for msg in messages.get("hydra:member", []):
            if "FaceFusion" in msg["subject"]:
                msg_id = msg["id"]
                message = requests.get(f"{MAIL_TM_API}/messages/{msg_id}", headers=headers).json()
                return message["text"]
        time.sleep(5)

    raise Exception("⚠️ Verification email did not arrive.")

def extract_code(text):
    match = re.search(r"\b\d{6}\b", text)
    if match:
        return match.group(0)
    return None

def stealth_chrome_options():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    return options

def click_sign_up(driver):
    selectors = [
        (By.XPATH, "//button[@class='theme-btn ghost-btn' and contains(text(), 'Sign up')]"),
        (By.XPATH, "//button[contains(@class, 'ghost-btn') and contains(., 'Sign up')]"),
        (By.CSS_SELECTOR, "button.theme-btn.ghost-btn"),
        (By.XPATH, "/html/body/header/div[1]/div/div[2]/div[1]/nav/button[2]")
    ]
    for by, selector in selectors:
        try:
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, selector)))
            ActionChains(driver).move_to_element(button).pause(random.uniform(0.2, 0.7)).click().perform()
            return True
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
    return False

def automate_signup():
    driver = webdriver.Chrome(options=stealth_chrome_options())
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        email, mail_password, token = create_temp_mail_account()
        form_password = generate_password()

        print("🌐 Wait for process to finish...")
        driver.get("https://www.facefusion.co/image-to-video")

        if not click_sign_up(driver):
            raise Exception("Sign Up button was not found")

        wait = WebDriverWait(driver, 30)
        
        # Email
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
        email_input.send_keys(email)

        # Password
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        password_input.send_keys(form_password)

        # Send code
        send_code_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), 'Send code')]]")))
        send_code_btn.click()

        # Wait for code
        body = wait_for_verification_email(token)
        code = extract_code(body)
        if not code:
            raise Exception("Verification code not found in email!")

        # Enter code
        code_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Verification code']")))
        code_input.send_keys(code)

        time.sleep(1)
        signup_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Sign up')]")
        signup_button.click()

        input("✅ Done! You can start generating videos...")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        driver.save_screenshot("error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    automate_signup()
