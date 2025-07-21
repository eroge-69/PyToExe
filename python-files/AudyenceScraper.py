
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def start_scraper():
    # Set up Chrome options to attach to the already running Chrome in debug mode
    chrome_options = Options()
    chrome_options.debugger_address = "localhost:9222"

    driver = webdriver.Chrome(options=chrome_options)

    campaign_url = input("Paste the full Audyence campaign URL: ").strip()
    driver.get(campaign_url)
    time.sleep(5)  # Allow table to load

    all_data = []
    page_number = 1

    while True:
        print(f"Scraping page {page_number}...")
        time.sleep(2)

        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, "td")
                row_data = [col.text.strip() for col in cols]
                all_data.append(row_data)

            # Try clicking next
            next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next page']")
            if next_button.get_attribute("disabled"):
                break
            next_button.click()
            page_number += 1
            time.sleep(2)
        except Exception as e:
            print(f"Stopped at page {page_number} - No more pages or error: {e}")
            break

    # Save to CSV
    if all_data:
        filename = "output.csv"
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in all_data:
                writer.writerow(row)
        print(f"✅ Scraping complete. Data saved to {filename}")
    else:
        print("⚠️ No data found to write.")

    driver.quit()

if __name__ == "__main__":
    print("📌 Make sure Chrome is running with remote debugging:
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/ChromeDebug"")
    input("After launching Chrome and logging in to Audyence, press Enter to continue...")
    start_scraper()
