#!/usr/bin/env python3
"""
grab_lastpass_export.py
Semi-automated helper to capture LastPass CSV export from Chrome on Windows.

Usage:
  python grab_lastpass_export.py
  python grab_lastpass_export.py --timeout 300 --out "C:\\Users\\You\\Desktop\\lastpass_export.csv"

Notes:
 - This script uses your existing Chrome profile so you remain logged in.
 - You must still perform the LastPass steps in the browser (Advanced Options -> Export).
 - The script watches for a new tab whose body looks like CSV and saves it.
"""

import os
import time
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

CSV_MARKERS = [\"url,username,password\", \"url,username,password,extra,name,grouping\", \"URL,Username,Password\"]

def default_chrome_user_data_dir():
    local = os.getenv(\"LOCALAPPDATA\")
    if local:
        return os.path.join(local, \"Google\", \"Chrome\", \"User Data\")
    # fallback
    return None

def find_csv_text_in_driver(driver):
    # Check all tabs for plaintext CSV-like text
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        try:
            body = driver.execute_script(\"return document.body ? document.body.innerText : ''\")
            if not body:
                continue
            lowered = body.lower()
            # crude detection: look for csv header markers
            for marker in CSV_MARKERS:
                if marker in lowered:
                    return body
            # also detect if the page is long and comma-heavy (heuristic)
            if body.count(\",\") > 50 and \"\\n\" in body:
                return body
        except Exception:
            continue
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(\"--timeout\", type=int, default=300, help=\"Seconds to wait for you to trigger export in the browser\")
    parser.add_argument(\"--out\", \"-o\", help=\"Output CSV path (optional)\")
    args = parser.parse_args()

    user_data = default_chrome_user_data_dir()
    if not user_data or not os.path.isdir(user_data):
        print(\"Couldn't find Chrome user data dir automatically. If Chrome is installed in a custom location, set it manually in the script.\")
        print(\"Default looked for:\", user_data)
        return

    chrome_options = Options()
    # Use your default profile so you're already logged in to LastPass
    chrome_options.add_argument(f\"--user-data-dir={user_data}\")
    # use default profile folder (Profile 1 is typical; blank lets Chrome choose Default)
    # If you use multiple profiles, you can point to the specific profile dir:
    # chrome_options.add_argument(r'--profile-directory=Default')

    # Disable automation infobar
    chrome_options.add_experimental_option(\"excludeSwitches\", [\"enable-automation\"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print(\"Launching Chrome (will reuse your profile). Do NOT enter a different profile when Chrome opens.\")
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        print(\"Error launching Chrome via webdriver. Ensure chromedriver is installed and on PATH and matches your Chrome version.\")
        print(\"Full error:\", e)
        return

    try:
        # open LastPass web vault
        driver.get(\"https://lastpass.com/?ac=1\")
        print(\"Chrome opened to LastPass web vault. Please complete any login prompts in the browser if asked.\")
        print(\"Then: use Advanced Options -> Export (or extension Export) in the LastPass UI.\")
        print(\"This script will wait up to\", args.timeout, \"seconds for the CSV to appear in a tab and will save it automatically.\")

        start = time.time()
        csv_text = None
        while time.time() - start < args.timeout:
            csv_text = find_csv_text_in_driver(driver)
            if csv_text:
                break
            time.sleep(1)

        if not csv_text:
            print(\"Timed out waiting for CSV to appear. Did you trigger LastPass -> Export and confirm any email verification?\")
            return

        # determine output filename
        if args.out:
            outpath = args.out
        else:
            ts = datetime.now().strftime(\"%Y%m%d_%H%M%S\")
            outpath = os.path.join(os.getcwd(), f\"lastpass_export_{ts}.csv\")

        # Save file as UTF-8 (LastPass CSV is plain text)
        with open(outpath, \"w\", encoding=\"utf-8\", newline=\"\\n\") as f:
            f.write(csv_text)

        print(f\"Export captured and saved to: {outpath}\")
        print(\"IMPORTANT: this file contains plaintext credentials. Import it into Bitwarden, then securely delete it.\")
    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == \"__main__\":
    main()
