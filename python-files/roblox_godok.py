# === AUTO-INSTALL MISSING PACKAGES ===
import subprocess
import sys

required = ["undetected_chromedriver", "selenium", "keyboard"]
for package in required:
    try:
        __import__(package)
    except ImportError:
        print(f"Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# === IMPORTS ===
import time
import threading
import keyboard
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# === CONFIGURATION ===

# Put your Roblox .ROBLOSECURITY cookies here
COOKIES = [
    "_|WARNING:-DO-NOT-SHARE-THIS...|_CAEaAhAB...",  # example
    "",  # Add more if needed
]

GROUP_ID = "7099450"

MESSAGES = [
    "FREE MFR Pets??? Click my Profile And Join Me!!!",
    "FREE MFR Pets??? Click my Profile And Join Me!!",
    "FREE MFR Pets??? Click my Profile And Join Me!",
    "FREE MFR Pets??? Click my Profile And Join Me",
]

POST_INTERVAL = 3
CYCLE_SLEEP = 60
MESSAGE_ROTATE_INTERVAL = 18 * 60

# === SPAM FUNCTION FOR ONE ACCOUNT ===
def spam_with_account(cookie, account_index):
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)
    driver.get("https://www.roblox.com")
    driver.delete_all_cookies()
    driver.add_cookie({
        "name": ".ROBLOSECURITY",
        "value": cookie,
        "domain": ".roblox.com",
        "path": "/",
        "secure": True,
        "httpOnly": True
    })

    message_index = 0
    last_rotate_time = time.time()
    print(f"[Account {account_index}] Started spamming... Press ESC to stop.")

    try:
        while True:
            if keyboard.is_pressed('esc'):
                print(f"\n[Account {account_index}] Stopped by user.")
                break

            if time.time() - last_rotate_time >= MESSAGE_ROTATE_INTERVAL:
                message_index = (message_index + 1) % len(MESSAGES)
                last_rotate_time = time.time()
                print(f"[Account {account_index}] Rotated message to: {MESSAGES[message_index]}")

            for i in range(3):
                if keyboard.is_pressed('esc'):
                    print(f"\n[Account {account_index}] Stopped by user.")
                    return

                driver.get(f"https://www.roblox.com/groups/{GROUP_ID}/about")
                time.sleep(5)

                textareas = driver.find_elements(By.TAG_NAME, "textarea")
                if not textareas:
                    print(f"[Account {account_index}] Message box not found.")
                    time.sleep(POST_INTERVAL)
                    continue

                text_box = textareas[0]
                text_box.clear()
                text_box.send_keys(MESSAGES[message_index])
                time.sleep(1)

                buttons = driver.find_elements(By.TAG_NAME, "button")
                post_button = next((btn for btn in buttons if "post" in btn.text.lower()), None)

                if post_button:
                    post_button.click()
                else:
                    print(f"[Account {account_index}] Post button not found.")
                    time.sleep(POST_INTERVAL)
                    continue

                time.sleep(3)

                if "You are posting too fast" in driver.page_source:
                    print(f"[Account {account_index}] Rate limited. Sleeping...")
                    time.sleep(CYCLE_SLEEP)
                    break
                else:
                    print(f"[Account {account_index}] Posted successfully ({i+1}/3)")
                    time.sleep(POST_INTERVAL)

            print(f"[Account {account_index}] Sleeping for {CYCLE_SLEEP} seconds...\n")
            time.sleep(CYCLE_SLEEP)

    except Exception as e:
        print(f"[Account {account_index}] Error: {e}")

    finally:
        driver.quit()
        print(f"[Account {account_index}] Closed browser.")

# === MAIN FUNCTION ===
def main():
    print("Starting all accounts...")

    threads = []
    for idx, cookie in enumerate(COOKIES, start=1):
        if not cookie.strip():
            continue
        t = threading.Thread(target=spam_with_account, args=(cookie, idx), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(5)

    print("Press ESC anytime to stop...\n")
    try:
        while True:
            if keyboard.is_pressed('esc'):
                print("Stopping all...")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted.")

if __name__ == "__main__":
    main()
