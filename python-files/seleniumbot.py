import os
import sys
import json
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---- CONFIG ----
DISPLAY_NAME = "bot"
ROOM_NAME = f"moderated/39e97a5113846f29c0e6c97cf65494b4408b4679b5e733aa7f1e21ebb6b40f72#config.startWithAudioMuted=true&userInfo.displayName={DISPLAY_NAME}&config.startWithVideoMuted=true&config.prejoinPageEnabled=false"
JITSI_URL = f"https://meet.jit.si/{ROOM_NAME}"


# ---- Detect OS + Chrome User Data Dir ----
def get_chrome_user_data_dir():
    home = str(Path.home())
    
    if sys.platform.startswith("win"):
        return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data")
    elif sys.platform == "darwin":  # macOS
        return os.path.join(home, "Library", "Application Support", "Google", "Chrome")
    else:  # Linux
        return os.path.join(home, ".config", "google-chrome")

USER_DATA_DIR = get_chrome_user_data_dir()

# ---- Detect Last Used Profile from Local State ----
def get_last_used_profile(user_data_dir):
    local_state_path = os.path.join(user_data_dir, "Local State")
    if not os.path.exists(local_state_path):
        print(" Could not find Chrome 'Local State' file. Using 'Default'.")
        return "Default"

    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        profile = data.get("profile", {}).get("last_used", "Default")
        return profile
    except Exception as e:
        print(f" Failed to read Local State: {e}")
        return "Default"

PROFILE_NAME = get_last_used_profile(USER_DATA_DIR)
print(f" Auto-selected last used Chrome profile: {PROFILE_NAME}")

# ---- Setup Chrome with existing profile ----
chrome_options = Options()
temp_profile = os.path.join(os.getcwd(), "selenium_profile")
os.makedirs(temp_profile, exist_ok=True)

chrome_options.add_argument(f"--user-data-dir={temp_profile}")
chrome_options.add_argument(f"--profile-directory={PROFILE_NAME}")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_experimental_option("detach", True)  # keep browser open after script ends
print("a")
driver = webdriver.Chrome(options=chrome_options)
print("b")
time.sleep(4)
print("c")
driver.get(JITSI_URL)
print(f"Opening Jitsi room: {JITSI_URL}")

wait = WebDriverWait(driver, 15)

# # ---- Set display name ----
# try:
#     name_input = wait.until(EC.presence_of_element_located(
#         (By.XPATH, "//input[@id='premeeting-name-input' or @name='username' or contains(@placeholder,'name')]")
#     ))
#     name_input.clear()
#     name_input.send_keys(DISPLAY_NAME)
#     print(f"✅ Entered name: {DISPLAY_NAME}")
# except Exception:
#     print("ℹ️ No pre-meeting name input found.")

# ---- Try login if button appears ----
try:
    login_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Log-in')]")
    ))
    login_btn.click()
    print(" Clicked Log-in button.")
    time.sleep(3)
except Exception:
    print("No login button found — continuing without login.")

# ---- Try join if button appears ----
try:
    join_btn = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Join meeting')]")
    ))
    join_btn.click()
    print(" Joined the meeting.")
except Exception:
    print(" No explicit join button found — likely auto-joined.")

print(" Bot is now in the meeting.")
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    driver.quit()
    print("Closed.")
