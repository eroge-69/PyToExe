import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === BEÁLLÍTÁSOK ===
chrome_user_data_dir = r"C:\Users\Tomi\AppData\Local\Google\Chrome\User Data"
profile_name = "Default"  # vagy másik profil neve, ha nem Default

# === CHROME INDÍTÁSA SAJÁT PROFILLAL ===
options = Options()
options.add_argument(f"--user-data-dir={chrome_user_data_dir}")
options.add_argument(f"--profile-directory={profile_name}")
driver = webdriver.Chrome(options=options)

def log_success(url):
    with open("log_sikeres.txt", "a", encoding="utf-8") as f:
        f.write("OK: " + url + "\n")

def log_fail(url, reason):
    with open("log_hiba.txt", "a", encoding="utf-8") as f:
        f.write(f"HIBA: {url} → {reason}\n")

with open("DeviantArt_Csoportok.csv", "r", encoding="utf-8") as f:
    links = [line.strip() for line in f if line.strip()]

for url in links:
    try:
        driver.get(url)
        time.sleep(5)

        # Keresd meg a helyi Submit gombot, ne a felsőt
        buttons = driver.find_elements(By.XPATH, '//button[.//span[text()="Submit"]]')
        if not buttons:
            log_fail(url, "Nincs Submit gomb")
            continue

        buttons[0].click()
        time.sleep(2)

        recommend = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Recommend Existing Deviation"]'))
        )
        recommend.click()
        time.sleep(3)

        # Kattints az 'All' galéria fülre
        all_tab = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//div[text()="All"]'))
        )
        all_tab.click()
        time.sleep(2)

        # Kattintás az első képre
        first_thumb = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '(//div[@role="grid"]//img)[1]'))
        )
        first_thumb.click()
        time.sleep(2)

        # 'Select' gomb
        select_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button//span[text()="Select"]'))
        )
        select_btn.click()
        time.sleep(3)

        log_success(url)

    except Exception as e:
        log_fail(url, str(e))
        continue

driver.quit()