from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
import random
from datetime import datetime, timedelta

from seleniumwire import webdriver as wire_webdriver
from selenium.webdriver.remote.webelement import WebElement
import time

data = pd.read_csv("accounts.csv")

def human_type(element: WebElement, text: str, min_delay=0.07, max_delay=0.15):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(min_delay, max_delay))

def generate_random_dob(min_age=22, max_age=80):
    today = datetime.today()
    start_date = today - timedelta(days=365 * max_age)
    end_date = today - timedelta(days=365 * min_age)

    random_birth_date = start_date + (end_date - start_date) * random.random()
    return random_birth_date.strftime("%m%d%Y")

def create_driver_with_proxy(proxy_string):
    try:
        parts = proxy_string.strip().split(":")
        if len(parts) != 4:
            raise ValueError("Proxy string must be in format host:port:user:pass")

        proxy_host, proxy_port, proxy_user, proxy_pass = parts
        print(f"Using Selenium Wire for Proxy: {proxy_host}:{proxy_port}")

        seleniumwire_options = {
            'proxy': {
                'https': f'https://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}'
            }
        }

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--allow-running-insecure-content")

        driver = wire_webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
            seleniumwire_options=seleniumwire_options
        )
        return driver
    except ImportError:
        print("selenium-wire not installed. Install with: pip install selenium-wire")
        return None


for account in data.iloc:
    account.Password = f'{account.Password}11'

    driver = create_driver_with_proxy(account["Proxy"])
    driver.get("https://tickets.masters.com/")
    while True:
        try:
            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "createAccountForm")))
            form = driver.find_element(By.ID, "createAccountForm")

            # Fill form
            firstname = form.find_element(By.CSS_SELECTOR, 'input[name="firstName"]')
            lastname = form.find_element(By.CSS_SELECTOR, 'input[name="lastName"]')
            email = form.find_element(By.CSS_SELECTOR, 'input[name="emailAddress"]')
            password = form.find_element(By.CSS_SELECTOR, 'input[name="password"]')
            confirm_password = form.find_element(By.CSS_SELECTOR, 'input[name="confirmPassword"]')
            sign_up_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Sign Up"]')

            human_type(firstname, account["First_Name"])
            human_type(lastname, account["Last_Name"])
            human_type(email, account["Email"])
            human_type(password, account["Password"])
            human_type(confirm_password, account["Password"])

            time.sleep(10)

            # Submit form
            form.submit()

            # Wait for either success or known error
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((
                        By.XPATH, "//div[contains(@class, 'error-text')]"
                    ))
                )
                print("❌ System error detected. Restarting driver for this account.")
                driver.refresh()
                continue  # Restart from top of the while loop for this account

            except:
                pass  # No error, proceed

            # Check for success
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "account-confirmation"))
                )
                print("✅ Account created successfully!")
                break  # Exit retry loop
            except:
                print("⚠️ Unknown issue after submission. Retrying...")
                driver.refresh()
                continue

        except Exception as e:
            print(f"❌ Critical error during signup: {e}")
            driver.refresh()
            continue

    verification_link = str(input("Enter the Verification Link from your email: "))
    driver.get(verification_link)

    time.sleep(5)

    # Log in process
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "logInForm")))
        login_form = driver.find_element(By.ID, "logInForm")
        login_form.find_element(By.ID, "emailAddress").clear()
        login_form.find_element(By.ID, "emailAddress").send_keys(account["Email"])
        login_form.find_element(By.ID, "password").send_keys(account["Password"])
        login_form.submit()
    except Exception as e:
        print(f"An error occurred while locating the login form: {e}")

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "button")))
        accept_button = driver.find_element(By.XPATH, "//div[@class='button' and text()='Accept and Continue']")
        accept_button.click()
    except Exception as e:
        print(f"An error occurred while clicking the accept button: {e}")

    time.sleep(5)

    try:
        driver.find_element(By.NAME, "address1").send_keys(account["Address"])
        driver.find_element(By.NAME, "city").send_keys(account["City"])
        driver.find_element(By.NAME, "stateProvince").send_keys(account["State"])
        driver.find_element(By.NAME, "phone").send_keys(account["Phone"])
        driver.find_element(By.NAME, "zipPostalCode").send_keys(str(account["ZIP"]))
    except Exception as e:
        print(f"An error occurred while filling in the address details: {e}")

    print("Set Country to Denmark manually in the browser.")
    os.system("pause")

    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='button secondary' and text()='Next']"))
        )
        next_button.click()
    except Exception as e:
        print(f"An error occurred while clicking the next button: {e}")

    time.sleep(5)

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, "birthDate")))
        driver.find_element(By.NAME, "birthDate").send_keys(generate_random_dob())
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='button secondary' and normalize-space()='Next']"))
        )
        next_button.click()
    except Exception as e:
        print("An error occurred while filling in the birth date or clicking next: {e}")

    time.sleep(5)
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='button secondary' and normalize-space()='Next']"))
        )
        next_button.click()
    except Exception as e:
        print(f"An error occurred while clicking the next button: {e}")

    time.sleep(5)

    try:
        driver.find_element(By.NAME, "mainAddress").click()
        driver.find_element(By.NAME, "permanentAddress").click()
        driver.find_element(By.NAME, "onlyResident").click()
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='button secondary' and normalize-space()='Next']"))
        )
        next_button.click()
    except Exception as e:
        print(f"An error occurred while filling in the residency details: {e}")

    print("next steps are manual after completion press any key")
    os.system("pause")
    driver.quit()
    break