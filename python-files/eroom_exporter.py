import os, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

urls = [
    "https://www.eroomcloud.no/eRoom/PN028/BVCSupplier/0_2c84",
    "https://www.eroomcloud.no/eRoom/PN028/BVCSupplier/0_34ed",
    "https://www.eroomcloud.no/eRoom/PN028/BVCSupplier/0_30f7",
    "https://www.eroomcloud.no/eRoom/PN028/BVCSupplier/0_2aab",
    "https://www.eroomcloud.no/eRoom/PN028/BVCSupplier/0_15dee",
    "https://www.eroomcloud.no/eRoom/PN028/YCR-CIMC/0_875a",
    "https://www.eroomcloud.no/eRoom/PN028/YCR-CIMC/0_92cd",
    "https://www.eroomcloud.no/eRoom/PN028/YCR-CIMC/0_10d62",
    "https://www.eroomcloud.no/eRoom/PN028/YCR-CIMC/0_1ec8c",
    "https://www.eroomcloud.no/eRoom/PN028/MKIIGolar/0_b82"
]

download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

for idx, url in enumerate(urls):
    print(f"[{idx+1}/{len(urls)}] Processing: {url}")
    driver.get(url)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Reset']")))
    except:
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Show Search"))).click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@value='Reset']")))
    driver.find_element(By.XPATH, "//input[@value='Reset']").click()
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//nobr[text()='export']"))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@value='OK' and @type='button']"))).click()
    csv_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '.csv')]")))
    driver.get(csv_link.get_attribute("href"))
    time.sleep(5)
    for f in os.listdir(download_dir):
        if f.endswith(".csv"):
            os.rename(os.path.join(download_dir, f), os.path.join(download_dir, f"export_{idx+1}.csv"))
            break

driver.quit()
print("✅ All exports complete.")
