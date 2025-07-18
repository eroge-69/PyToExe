import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import Fore, Style, init
import os

init(autoreset=True)

def print_colored(text, color):
    print(color + text + Style.RESET_ALL)

def check_code(driver, code):
    try:
        driver.get("https://redeem.microsoft.com/")
        
        # Wait for the code input field to be visible
        code_input = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "redeem-code-text-box"))
        )
        code_input.clear()
        code_input.send_keys(code)
        
        # Click the next button
        next_button = driver.find_element(By.ID, "redeem-next-button")
        next_button.click()
        
        # Wait for the result to load
        time.sleep(5) # Give some time for the page to update after clicking next

        # Check for different outcomes
        page_source = driver.page_source.lower()
        
        if "this code has already been used" in page_source or "already been redeemed" in page_source:
            return "USED"
        elif "check the instructions" in page_source or "this code isn\'t valid" in page_source or "not valid" in page_source:
            return "INVALID"
        elif "you\'ll get" in page_source or "confirm your purchase" in page_source or "redeem" in page_source:
            # This means the code is valid and it\'s asking for confirmation
            return "VALID"
        else:
            return "UNKNOWN"

    except Exception as e:
        print_colored(f"[ERROR] An error occurred while checking code {code}: {e}", Fore.RED)
        return "ERROR"

def main():
    print_colored("\n" + "="*50, Fore.CYAN)
    print_colored("Xbox Code Checker - By Omar Mo", Fore.CYAN)
    print_colored("="*50 + "\n", Fore.CYAN)

    codes_file = "codes.txt"
    valid_codes = []
    used_codes = []
    invalid_codes = []
    total_codes = 0

    try:
        with open(codes_file, "r") as f:
            codes = [line.strip() for line in f if line.strip()]
        total_codes = len(codes)
    except FileNotFoundError:
        print_colored(f"[ERROR] \'{codes_file}\' not found. Please create a file named \'{codes_file}\' and put your codes in it (one code per line).", Fore.RED)
        input("Press Enter to exit...")
        return

    print_colored(f"Found {total_codes} codes to check.\n", Fore.YELLOW)

    # Setup Chrome options for headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3") # Suppress warnings
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Selenium Manager will automatically download and manage the driver
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print_colored(f"[ERROR] Failed to start Chrome driver: {e}", Fore.RED)
        print_colored("Please make sure you have Google Chrome installed on your system.", Fore.RED)
        input("Press Enter to exit...")
        return

    for i, code in enumerate(codes):
        print_colored(f"Checking code {i+1}/{total_codes}: {code}", Fore.WHITE)
        status = check_code(driver, code)

        if status == "VALID":
            print_colored(f"[+] {code} is VALID!", Fore.GREEN)
            valid_codes.append(code)
        elif status == "USED":
            print_colored(f"[-] {code} is USED!", Fore.YELLOW)
            used_codes.append(code)
        elif status == "INVALID":
            print_colored(f"[-] {code} is INVALID!", Fore.RED)
            invalid_codes.append(code)
        else:
            print_colored(f"[?] {code} status UNKNOWN or ERROR.", Fore.MAGENTA)

        # Random delay between 10 and 15 seconds as requested
        if i < len(codes) - 1:  # Don\'t wait after the last code
            delay = random.randint(10, 15)
            print_colored(f"Waiting for {delay} seconds...", Fore.BLUE)
            time.sleep(delay)

    driver.quit()

    print_colored("\n" + "="*50, Fore.CYAN)
    print_colored("Statistics", Fore.CYAN)
    print_colored("="*50, Fore.CYAN)
    print_colored(f"Total Codes   : {total_codes}", Fore.WHITE)
    print_colored(f"Valid Codes   : {len(valid_codes)}", Fore.GREEN)
    print_colored(f"Used Codes    : {len(used_codes)}", Fore.YELLOW)
    print_colored(f"Invalid Codes : {len(invalid_codes)}", Fore.RED)
    print_colored("By Omar Mo", Fore.CYAN)
    print_colored("\nFinished checking codes!", Fore.CYAN)

    # Save results to files
    with open("valid_codes.txt", "w") as f:
        for c in valid_codes:
            f.write(c + "\n")
    with open("used_codes.txt", "w") as f:
        for c in used_codes:
            f.write(c + "\n")
    with open("invalid_codes.txt", "w") as f:
        for c in invalid_codes:
            f.write(c + "\n")

    print_colored("Results saved to valid_codes.txt, used_codes.txt, and invalid_codes.txt", Fore.CYAN)
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()


