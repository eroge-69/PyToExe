import configparser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load credentials and ads from config.ini
config = configparser.ConfigParser(interpolation=None)
config.read('config.ini')

EMAIL = config.get('credentials', 'email')
PASSWORD = config.get('credentials', 'password')

confirm_text = "Prefer not to say"

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(service=Service(), options=options)

def login(driver, wait):
    print("🔐 Navigating to login page...")
    driver.get("https://id.kijiji.ca/login?service=https%3A%2F%2Fid.kijiji.ca%2Foauth2.0%2FcallbackAuthorize%3Fclient_id%3Dkijiji_horizontal_web_gpmPihV3%26redirect_uri%3Dhttps%253A%252F%252Fwww.kijiji.ca%252Fapi%252Fauth%252Fcallback%252Fcis%26response_type%3Dcode%26client_name%3DCasOAuthClient&locale=en")
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(EMAIL)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(5)

def go_to_my_ads(driver):
    print("📂 Navigating to My Ads...")
    driver.get("https://www.kijiji.ca/m-my-ads/active")

def find_ad_by_title(driver, wait, ad_title):
    print(f"🔍 Searching for ad titled: '{ad_title}'")
    try:
        ad_element = wait.until(EC.presence_of_element_located((
            By.XPATH,
            f"//td[contains(@class, 'titleCell')]//a[normalize-space(text())='{ad_title}']"
        )))
        print(f"✅ Found ad titled '{ad_title}'.")
        return ad_element
    except Exception:
        print(f"❌ Ad titled '{ad_title}' not found.")
        return None

def delete_ad(driver, ad_element):
    ad_container = ad_element.find_element(By.XPATH, "./ancestor::tr")
    delete_button = ad_container.find_element(
        By.XPATH,
        ".//button[contains(@class, 'actionLink-2017387589') and contains(@class, 'button-3081539300')]"
    )
    delete_button.click()
    print("🗑 Delete button clicked.")

    prefer_not_button = driver.find_element(
        By.XPATH,
        "//button[normalize-space(text())='Prefer not to say']"
    )
    prefer_not_button.click()

    confirm_button = driver.find_element(
        By.XPATH,
        "//button[contains(@class, 'actionButton-50733545') and contains(@class, 'button__primary-305176206') and contains(@class, 'button__small-2954259315')]"
    )
    confirm_button.click()
    print(f"✅ Confirmed deletion with '{confirm_text}'.")

def close_popup(driver):
    close_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close modal']"))
    )
    driver.execute_script("arguments[0].click();", close_button)
    print("❎ Closed popup.")

def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)

    try:
        login(driver, wait)
        go_to_my_ads(driver)

        ad_sections = [section for section in config.sections() if section.startswith('ad')]
        for ad_section in ad_sections:
            ad_title = config.get(ad_section, 'title')
            ad_element = find_ad_by_title(driver, wait, ad_title)
            if ad_element:
                delete_ad(driver, ad_element)
                close_popup(driver)
                time.sleep(3)  # Small pause between deletions
            else:
                print(f"Skipping deletion for '{ad_title}', ad not found.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

    finally:
        time.sleep(5)
        driver.quit()
        print("🚪 Browser closed. Exiting script.")

if __name__ == "__main__":
    main()
