import sys
import os
from colorama import Fore, init
import colorama
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
init()

sys.stdout.write("\x1b]0;[+] [BW] Check the remaining quota of WE [Mostafa Mohamed] [+]\x07")
print(Fore.MAGENTA + """
888       888 8888888888       .d88888b.  888     888  .d88888b. 88888888888     d8888 
888   o   888 888             d88P" "Y88b 888     888 d88P" "Y88b    888        d88888 
888  d8b  888 888             888     888 888     888 888     888    888       d88P888 
888 d888b 888 8888888         888     888 888     888 888     888    888      d88P 888 
888d88888b888 888             888     888 888     888 888     888    888     d88P  888 
88888P Y88888 888             888 Y8b 888 888     888 888     888    888    d88P   888 
8888P   Y8888 888             Y88b.Y8b88P Y88b. .d88P Y88b. .d88P    888   d8888888888 
888P     Y888 8888888888       "Y888888"   "Y88888P"   "Y88888P"     888  d88P     888 
                                     Y8b                                               
                                                                 """)
print("")
print(Fore.YELLOW + "                [+]",Fore.CYAN +" Dev : Mostafa Mohamed ",Fore.YELLOW+"[+]")
print(Fore.YELLOW + "                    [+]",Fore.WHITE +" Fb.com/vk0x65 ",Fore.YELLOW+"[+]")
print(Fore.YELLOW + "                 [+]",Fore.MAGENTA +" WE REMAINING QUOTA ",Fore.YELLOW+"[+]")
print(Fore.YELLOW + "                 [+]",Fore.MAGENTA +" Updated by : Omar Elwaziry ",Fore.YELLOW+"[+]")
print(Fore.YELLOW + "                 [+]",Fore.MAGENTA +" Fb.com/MadWeZZa ",Fore.YELLOW+"[+]")
print("")

def try_login():
    try:
        os.environ['MOZ_HEADLESS'] = '1'
        driver = webdriver.Firefox()
        driver.get("https://my.te.eg/user/login")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            print(Fore.RED + "Error: Page failed to load")
            raise
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/section/main/div/div/div/div[2]/div/div[2]/div/div[1]/div/form/div/div/div/div/div/div[1]/input'))
            )
            element.send_keys("0222605109") ##### EDIT USERNAME HERE !! #####
            print(Fore.YELLOW + "Username entered...")
        except TimeoutException:
            print(Fore.RED + "Error: Username field not found")
            raise
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/section/main/div/div/div/div[2]/div/div[2]/div/div[2]/form/div/div/div/div/input'))
            )
            element.send_keys("husseinK12;)") ##### EDIT PASSWORD HERE !! #####
            print(Fore.YELLOW + "Password entered...")
        except TimeoutException:
            print(Fore.RED + "Error: Password field not found")
            raise
        try:
            service_type = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ant-select-selector"))
            )
            service_type.click()
            time.sleep(1)
            internet_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ant-select-item-option-content')]//span[contains(text(), 'Internet')]"))
            )
            internet_option.click()
            time.sleep(1)
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login-withecare"))
            )

        except Exception as e:
            print(Fore.RED + f"Service type selection error: {str(e)}")
            raise
        
        try:
            button.click()
            try:
                result = WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "ant-progress-circle")),
                        EC.presence_of_element_located((By.CLASS_NAME, "ant-message-error"))
                    )
                )
                
                if "ant-message-error" in result.get_attribute("class"):
                    raise Exception("Login failed - error message shown")   
            except TimeoutException:
                print(Fore.RED + "Navigation timeout")
                raise
            
        except Exception as e:
            print(Fore.RED + f"Login error: {str(e)}")
            raise
        time.sleep(5)
        WebDriverWait(driver, 10).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "ant-spin-spinning"))
        )
        parent_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                "//div[contains(@style, 'display: flex') and contains(@style, 'margin-top: -20px')]"
            ))
        )
        remaining = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, 
                ".//span[contains(@style, 'font-size: 2.1875rem') and contains(@style, 'color: var(--ec-brand-primary)')]"
            ))
        )
        print(Fore.CYAN + " REMAINING QUOTA : " + Fore.GREEN + remaining.text + Fore.WHITE + " GB")
        return driver
    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        raise
try:
    driver = try_login()
    input("Press Enter to close...")
except Exception as e:
    input("Press Enter to close...")
finally:
    if 'driver' in locals() and driver:
        driver.quit()