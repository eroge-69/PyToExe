import os
import re
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

os.environ['GLOG_minloglevel'] = '2'  # Отключает логи INFO и WARNING
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Отключает вывод TensorFlow

def parse_accounts(file_path):
    accounts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        email_pattern = r'Email: (.+)'
        password_pattern = r'Password: (.+)'
        
        emails = re.findall(email_pattern, content)
        passwords = re.findall(password_pattern, content)
        
        for email, password in zip(emails, passwords):
            accounts.append({'email': email, 'password': password})
        
        print(f"✓ Found {len(accounts)} accounts to process")
        return accounts
    except Exception as e:
        print(f"✗ Error reading accounts file: {e}")
        return []

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--log-level=OFF')
    chrome_options.addArguments("--disable-notifications")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def switch_to_new_window(driver, original_windows, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.window_handles) > len(original_windows)
        )
        
        new_windows = [window for window in driver.window_handles if window not in original_windows]
        
        if new_windows:
            driver.switch_to.window(new_windows[0])
            #print(f"✓ Switched to new window: {driver.current_url}")
            return True
        else:
            print("[-] New window not found")
            return False
    except TimeoutException:
        print("[-] Timeout waiting for new window")
        return False

def wait_for_page_load(driver, timeout=20, expected_url_contains=None):
    try:
        start_time = time.time()
        previous_url = driver.current_url
        
        while time.time() - start_time < timeout:
            time.sleep(1)
            current_url = driver.current_url
            if current_url == previous_url:
                print(f"[+] Page loaded: {current_url}")
                
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                if expected_url_contains:
                    if expected_url_contains in current_url:
                        return True
                    else:
                        #print(f"✗ Current URL doesn't contain expected string. Expected: {expected_url_contains}, Got: {current_url}")
                        return False
                
                return True
            previous_url = current_url
        
        print("[-] Timeout waiting for URL to stabilize")
        return False
        
    except Exception as e:
        print(f"[-] Error waiting for page load: {e}")
        return False

def find_and_click_astrum_button(driver, timeout=15):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ph-social-btn, .social-btn, [class*='btn'], a[href*='astrum']"))
        )
        
        astrum_selectors = [
            "a.ph-social-btn_astrum",
            "a.js-social-btn-astrum",
            "a[href*='astrum']",
            "a[class*='astrum']",
            "button[data-provider*='astrum']",
            "div[data-provider*='astrum']",
            "a[onclick*='astrum']",
            "a[title*='Astrum']",
            "a img[alt*='Astrum']",
            "a:has(img[alt*='Astrum'])",
            ".ph-social-btn_outline"
        ]
        
        for selector in astrum_selectors:
            try:
                astrum_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                href = astrum_button.get_attribute("href") or ""
                class_name = astrum_button.get_attribute("class") or ""
                outer_html = astrum_button.get_attribute("outerHTML") or ""
                
                if "astrum" in href.lower() or "astrum" in class_name.lower() or "astrum" in outer_html.lower():
                    astrum_button.click()
                    print(f"[+] Clicked Astrum button with selector: {selector}")
                    return True
            except:
                continue
        
        xpath_selectors = [
            "//a[contains(@href, 'astrum')]",
            "//a[contains(@class, 'astrum')]",
            "//*[contains(text(), 'Astrum')]",
            "//img[contains(@alt, 'Astrum')]/..",
            "//a[contains(@class, 'ph-social-btn_outline')]"
        ]
        
        for xpath in xpath_selectors:
            try:
                astrum_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                astrum_button.click()
                print(f"[+] Clicked Astrum button with XPath: {xpath}")
                return True
            except:
                continue
        
        print("[-] Could not find Astrum button with any selector")
        return False
        
    except Exception as e:
        print(f"[-] Error finding Astrum button: {e}")
        return False

def wait_for_astrum_login_form(driver, timeout=30):
    try:
        print("[+] Waiting for Astrum login form...")
        
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                "input[type='email'], " +
                "input[name='email'], " +
                "form, " +
                "button[type='submit'], " +
                "[data-testid*='auth'], " +
                ".auth-form"))
        )
        
        current_url = driver.current_url
        if "astrum" not in current_url.lower():
            print(f"[-] URL doesn't contain astrum: {current_url}")
            return False
        
        print("[+] Astrum login form loaded successfully")
        return True
        
    except TimeoutException:
        print("[-] Timeout waiting for Astrum login form")
        print(f"Current URL: {driver.current_url}")
        return False
    except Exception as e:
        print(f"[-] Error waiting for Astrum login form: {e}")
        return False

def fill_astrum_login_form(driver, email, password):
    try:
        email_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 
                "input[data-testid='auth-login-form-email-input'], " +
                "input[type='email'], " +
                "input[name='email']"))
        )
        email_input.clear()
        email_input.send_keys(email)
        print("[+] Entered email")
        time.sleep(2)
        
        continue_selectors = [
            "button[data-testid='auth-login-form-continue-button']",
            "button[type='submit']",
            "button:contains('Продолжить')",
            "button:contains('Continue')",
            "button:contains('Далее')",
            "button:contains('Next')"
        ]
        
        continue_button = None
        for selector in continue_selectors:
            try:
                if "contains" in selector:
                    text = selector.split("'")[1]
                    continue_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]"))
                    )
                else:
                    continue_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                if continue_button and continue_button.is_displayed() and continue_button.is_enabled():
                    print(f"[+] Found 'Continue' button with selector: {selector}")
                    break
                else:
                    continue_button = None
            except:
                continue
        
        if continue_button:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
            time.sleep(1)
            
            try:
                continue_button.click()
            except:
                driver.execute_script("arguments[0].click();", continue_button)
            
            print("[+] Clicked 'Continue' button")
            time.sleep(3)
        else:
            print("[+] Could not find 'Continue' button")
            return False
        
        password_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 
                "input[data-testid='auth-login-form-password-input'], " +
                "input[type='password'], " +
                "input[name='password']"))
        )
        
        password_input.clear()
        password_input.send_keys(password)
        print("[+] Entered password")
        time.sleep(1)
        
        login_button_selectors = [
            "button[data-testid='auth-login-form-enter-button']",
            "button[type='submit']",
            "button:contains('Войти')",
            "button:contains('Sign in')",
            "button:contains('Login')"
        ]
        
        login_button = None
        for selector in login_button_selectors:
            try:
                if "contains" in selector:
                    text = selector.split("'")[1]
                    login_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{text}')]"))
                    )
                else:
                    login_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                
                if login_button and login_button.is_displayed() and login_button.is_enabled():
                    print(f"[+] Found 'Login' button with selector: {selector}")
                    break
                else:
                    login_button = None
            except:
                continue
        
        if login_button:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
            time.sleep(1)
            
            try:
                login_button.click()
            except:
                driver.execute_script("arguments[0].click();", login_button)
            
            print("[+] Clicked 'Login' button")
            return True
        else:
            print("[-] Could not find 'Login' button")
            return False
        
    except Exception as e:
        print(f"[-] Error filling login form: {e}")
        return False

def handle_oauth_continue_button(driver, timeout=20):
    try:
        print(f"[+] Current OAuth URL: {driver.current_url}")
        
        WebDriverWait(driver, timeout).until(
            lambda d: "account.astrum-play.ru/oauth2" in d.current_url
        )
        
        continue_selectors = [
            "button[type='submit']",
            "button._root_1k1jp_1",
            "button[class*='_root_']",
            "button[class*='_variant_filled_']",
            "button[class*='_color_primary_']",
            "button:contains('Продолжить')",
            "button:contains('Continue')",
            "span:contains('Продолжить')",
            "//button[.//span[contains(text(), 'Продолжить')]]",
            "//span[contains(text(), 'Продолжить')]/.."
        ]
        
        continue_button = None
        max_wait = 10
        start_time = time.time()
        
        while time.time() - start_time < max_wait and not continue_button:
            for selector in continue_selectors:
                try:
                    if "//" in selector:
                        continue_button = driver.find_element(By.XPATH, selector)
                    elif "contains" in selector:
                        text = selector.split("'")[1]
                        continue_button = driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                    else:
                        continue_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if continue_button and continue_button.is_displayed():
                        print(f"✓ Found 'Continue' button with selector: {selector}")
                        break
                    else:
                        continue_button = None
                except:
                    continue_button = None
                    continue
            
            if not continue_button:
                time.sleep(1)
                print("[+] Still looking for 'Continue' button...")
        
        if not continue_button:
            print("[-] 'Continue' button not found after all attempts")
            return False
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", continue_button)
        time.sleep(1)
        
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(continue_button)
        )
        
        try:
            continue_button.click()
            print("[+] 'Continue' button clicked")
        except:
            try:
                driver.execute_script("arguments[0].click();", continue_button)
                print("[+] 'Continue' button clicked via JavaScript")
            except:
                try:
                    ActionChains(driver).move_to_element(continue_button).click().perform()
                    print("[+] 'Continue' button clicked via ActionChains")
                except Exception as e:
                    print(f"[-] Failed to click 'Continue' button: {e}")
                    return False
        
        time.sleep(3)

        # After clicking "Continue" in OAuth, check if VKPlay terms page appears
        current_url = driver.current_url
        if "account.vkplay.ru" in current_url and ("signup_terms" in current_url):
            print("[+] Detected VKPlay terms page")
            if not handle_vkplay_terms(driver):
                print("[-] Failed to handle VKPlay terms")
                return False
        
        return True
        
    except Exception as e:
        print(f"[-] Error handling OAuth continue button: {e}")
        return False

def handle_vkplay_terms(driver, timeout=20):
    """Handle VKPlay terms in current window"""
    try:
        print("[+] Handling VKPlay terms...")
        
        # Wait for consent checkbox to appear
        checkbox = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='confirm-checkbox']"))
        )
        
        # Click the checkbox
        checkbox.click()
        print("[+] Clicked consent checkbox")
        time.sleep(2)
        
        # Wait for "Continue" button to become active
        continue_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button#approve-button:not([disabled])"))
        )
        
        # Click the "Continue" button
        continue_button.click()
        print("[+] Clicked 'Continue' button in terms window")
        
        # Wait for redirect
        time.sleep(5)
        return True
        
    except Exception as e:
        print(f"[-] Error handling VKPlay terms: {e}")
        return False

def handle_vkplay_continue_button(driver, timeout=20):
    try:
        print("[+] Waiting for 'Continue' button on VKPlay page...")
        
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ph-form__btn.ph-btn.ph-btn_main.ph-btn_lg"))
        )
        
        continue_button = driver.find_element(By.CSS_SELECTOR, "button.ph-form__btn.ph-btn.ph-btn_main.ph-btn_lg")
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
        time.sleep(1)
        
        continue_button.click()
        print("[+] Clicked 'Continue' button on VKPlay page")
        
        return True
        
    except Exception as e:
        print(f"[-] Error clicking 'Continue' button on VKPlay: {e}")
        return False

def get_nickname_from_profile(driver):
    """Get nickname from Warface profile"""
    try:
        driver.get("https://ru.warface.com/profile")
        print("[+] Loading profile page...")
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.user-tab.active"))
        )
        
        nickname_element = driver.find_element(By.CSS_SELECTOR, "div.user-tab.active")
        nickname = nickname_element.text.strip()
        print(f"[+] Nickname retrieved: {nickname}")
        return nickname
        
    except Exception as e:
        print(f"[-] Error getting nickname: {e}")
        return None

def check_achievement(driver, nickname):
    """Check for achievement on wfts.su"""
    try:
        encoded_nickname = urllib.parse.quote(nickname)
        achievements_url = f"https://wfts.su/achievements/{encoded_nickname}"
        driver.get(achievements_url)
        print(f"[+] Checking account...")
        
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/top/achievements/375197']"))
        )
        
        achievement_element = driver.find_element(By.CSS_SELECTOR, "a[href*='/top/achievements/375197']")
        achievement_text = achievement_element.text.strip()
        print(f"[+] Stage checking success!")
        
        if "Непримиримые враги" in achievement_text:
            print("[+] Fully checking account success!")
            return True
            
        print("[-] Target COOP not found")
        return False
        
    except Exception as e:
        print(f"[-] Error checking account: {e}")
        return False

def save_approved_account(account):
    """Save approved account to file"""
    os.makedirs("accounts_approve", exist_ok=True)
    file_path = "accounts_approve/accounts.txt"
    
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"Email: {account['email']}\n")
        f.write(f"Password: {account['password']}\n")
        f.write(f"Nickname: {account['nickname']}\n")
        f.write("COOP: Success!\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("------------------------\n\n")
    
    print(f"[+] Account {account['email']} saved to {file_path}")

def process_account(driver, account):
    try:
        print(f"\n{'='*60}")
        print(f"[?] Processing account: {account['email']}")
        print(f"{'='*60}")
        
        driver.get("https://ru.warface.com")
        
        original_windows = driver.window_handles
        
        try:
            login_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.item.js-login, div.wf__button.wf__button_red.js-reg"))
            )
            login_button.click()
            print("[+] Clicked login/register button")
        except:
            try:
                login_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Войти') or contains(text(), 'ЗАРЕГИСТРИРОВАТЬСЯ')]"))
                )
                login_button.click()
                print("[+] Clicked login/register button via XPath")
            except Exception as e:
                print(f"[-] Could not find login button: {e}")
                return None
        
        if not switch_to_new_window(driver, original_windows):
            print("[-] Failed to switch to new window after login click")
            return None
        
        if not wait_for_page_load(driver, 20, "vkplay.ru"):
            print("[-] Failed to wait for VKPlay page load")
            return None
        
        if not find_and_click_astrum_button(driver):
            print("[-] Failed to find and click Astrum button")
            return None
        
        time.sleep(3)
        if len(driver.window_handles) > 2:
            driver.switch_to.window(driver.window_handles[2])
            print(f"[+] Switched to Astrum window: {driver.current_url}")
        else:
            print("[-] No new windows found after clicking Astrum")
            return None
        
        if not wait_for_astrum_login_form(driver):
            print("[-] Failed to wait for Astrum login form")
            return None
        
        if not fill_astrum_login_form(driver, account['email'], account['password']):
            print("[-] Failed to fill Astrum login form")
            return None
        
        time.sleep(5)
        
        current_url = driver.current_url
        if "account.astrum-play.ru/oauth2" in current_url:
            print(f"[+] Detected OAuth page: {current_url}")
            
            if not handle_oauth_continue_button(driver):
                print("[-] Failed to handle OAuth continue button")
                return None
        else:
            print(f"[-] Unexpected URL after login: {current_url}")
            return None
        

        # After OAuth processing, check if there are additional windows
        if len(driver.window_handles) > 1:
            # Switch to VKPlay window (index 1)
            driver.switch_to.window(driver.window_handles[1])
            print(f"[+] Switched to VKPlay window: {driver.current_url}")
            
            if not handle_vkplay_continue_button(driver):
                print("[-] Failed to click 'Continue' button on VKPlay")
                return None
        
        time.sleep(5)
        
        # Switch to main Warface window
        driver.switch_to.window(driver.window_handles[0])
        print(f"[+] Switched to Warface window: {driver.current_url}")
        
        current_url = driver.current_url
        print(f"[+] Final URL after authorization: {current_url}")
        
        if ("warface" in current_url or 
            "vkplay" in current_url or 
            "success" in current_url.lower() or 
            "code=" in current_url):
            print(f"[+] Successful login for {account['email']}!")
            
            nickname = get_nickname_from_profile(driver)
            if not nickname:
                print("[-] Failed to get nickname from profile")
                return None
                
            if not check_achievement(driver, nickname):
                print("[-] Account doesn't have the target achievement")
                return None
                
            return nickname
        else:
            print(f"[-] Undefined login status for {account['email']}")
            return None
        
    except Exception as e:
        print(f"[-] Error processing account {account['email']}: {str(e)}")
        return None
    
def main():
    accounts = parse_accounts("accounts_list.txt")
    if not accounts:
        print("[-] No accounts found or error reading file")
        return
    
    approved_accounts = []
    
    for account in accounts:
        driver = setup_driver()
        try:
            nickname = process_account(driver, account)
            if nickname:
                account['nickname'] = nickname
                approved_accounts.append(account)
                save_approved_account(account)
                print(f"[+] Account {account['email']} successfully processed and saved")
            else:
                print(f"[-] Account {account['email']} not processed or doesn't have the required achievement")
        except Exception as e:
            print(f"[-] Error processing account {account['email']}: {str(e)}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        time.sleep(2)
    
    # Write summary file
    if approved_accounts:
        with open("accounts_approve/accounts.txt", "w", encoding="utf-8") as f:
            f.write(f"===== ACCOUNTS LIST ({len(approved_accounts)}) =====\n\n")
            for account in approved_accounts:
                f.write(f"Email: {account['email']}\n")
                f.write(f"Password: {account['password']}\n")
                f.write(f"Nickname: {account['nickname']}\n")
                f.write("COOP: Success!\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("------------------------\n\n")
        
        print(f"\n[+] Successfully processed {len(approved_accounts)} accounts")
        print("[+] Results saved to accounts_approve/accounts.txt")
    else:
        print("\n[-] No accounts were successfully processed")
    
    # Delete accounts_list.txt after processing all accounts
    try:
        if os.path.exists("accounts_list.txt"):
            os.remove("accounts_list.txt")
            print("[+] accounts_list.txt deleted")
    except Exception as e:
        print(f"[-] Error deleting accounts_list.txt: {e}")

if __name__ == "__main__":
    main()