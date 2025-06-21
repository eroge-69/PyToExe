from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

# --- CONFIGURATION ---
URL = httpsexample.com       # Replace with your target URL
CLASS_NAME = target-class       # Replace with your target class
SCREENSHOT_FOLDER = screenshots # Folder to save screenshots
DELAY = 1.0                       # Delay in seconds for scrollingstabilization

# --- SETUP DRIVER ---
options = webdriver.ChromeOptions()
options.add_argument(--start-maximized)
driver = webdriver.Chrome(service=Service(), options=options)

try
    driver.get(URL)
    time.sleep(DELAY)

    elements = driver.find_elements(By.CLASS_NAME, CLASS_NAME)
    print(fFound {len(elements)} elements with class '{CLASS_NAME}')

    os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)
    for idx, element in enumerate(elements)
        ActionChains(driver).move_to_element(element).perform()
        time.sleep(DELAY)
        screenshot_path = os.path.join(SCREENSHOT_FOLDER, fscreenshot_{idx+1}.png)
        driver.save_screenshot(screenshot_path)
        print(fSaved {screenshot_path})

finally
    driver.quit()
