Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import time
... import random
... import undetected_chromedriver as uc
... from selenium.webdriver.common.by import By
... 
... # =============================
... # SETTINGS (Customize This)
... # =============================
... KEYWORD = "4th of July shirt"
... TARGET_URL = "https://www.etsy.com/listing/4321991057/4th-of-july-t-shirt-for-men-women"
... CLICK_COUNT = 20
... USE_PROXIES = True
... 
... # =============================
... # Load Proxies
... # =============================
... def load_proxies():
...     try:
...         with open("proxies.txt", "r") as f:
...             proxies = [line.strip() for line in f if line.strip()]
...             return proxies
...     except:
...         print("[!] proxies.txt not found.")
...         return []
... 
... # =============================
... # Build WebDriver with Options
... # =============================
... def build_driver(proxy=None):
...     options = uc.ChromeOptions()
...     options.add_argument("--headless")
...     options.add_argument("--disable-blink-features=AutomationControlled")
...     options.add_argument("--disable-gpu")
...     options.add_argument("--no-sandbox")
... 
...     # User-Agent Spoof
...     agents = [
...         "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
...         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
...         "Mozilla/5.0 (X11; Linux x86_64)"
    ]
    options.add_argument(f"user-agent={random.choice(agents)}")

    # Set Proxy if available
    if proxy:
        print(f"[Proxy] Using {proxy}")
        options.add_argument(f'--proxy-server=http://{proxy}')

    driver = uc.Chrome(options=options)
    return driver

# =============================
# Main Bot Function
# =============================
def search_and_click(keyword, target_url, proxy=None):
    driver = build_driver(proxy)
    try:
        driver.get("https://www.etsy.com")
        time.sleep(random.uniform(3, 5))

        search_box = driver.find_element(By.NAME, "search_query")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.submit()
        time.sleep(random.uniform(4, 6))

        links = driver.find_elements(By.CSS_SELECTOR, 'a.listing-link')

        for link in links:
            href = link.get_attribute("href")
            if href and target_url.split("?")[0] in href:
                print("[✔] Product found. Clicking...")
                time.sleep(random.uniform(1.5, 3))
                link.click()
                time.sleep(random.uniform(10, 15))  # stay on page
                return True
        print("[✘] Product not found in search results.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        driver.quit()
    return False

# =============================
# Loop the Bot
# =============================
def run_bot():
    proxies = load_proxies() if USE_PROXIES else []
    for i in range(CLICK_COUNT):
        print(f"\n[•] Click {i+1} of {CLICK_COUNT}")
        proxy = random.choice(proxies) if USE_PROXIES and proxies else None
        success = search_and_click(KEYWORD, TARGET_URL, proxy)
        wait_time = random.uniform(10, 20)
        print(f"[↻] Waiting {int(wait_time)} seconds before next run...\n")
        time.sleep(wait_time)

# =============================
# Start Bot
# =============================
if _name_ == "_main_":
