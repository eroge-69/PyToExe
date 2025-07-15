from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Get browser choice from user
putBrowser = input("Please enter the number to choose your browser (1 is Chrome, 2 is Safari, 3 is Firefox): ")

# Select browser
match putBrowser:
    case "1":
        print("Ok. Starting Chrome... ")
        browser = webdriver.Chrome()
    case "2":
        print("Ok. Starting Safari... ")
        browser = webdriver.Safari()
    case "3":
        print("Ok. Starting Firefox... ")
        browser = webdriver.Firefox()
    case _:
        print("Unknown browser!")
        exit()

# Read multiple accounts from accounts.txt (each line formatted as: username:password)
try:
    with open("accounts.txt", "r") as file:
        accounts = [line.strip().split(":") for line in file.readlines() if ":" in line]
except FileNotFoundError:
    print("❌ Error: 'accounts.txt' file not found!")
    exit()

print("\nStarting Follow Process...\n")

# Iterate over each account
for putUsername, putPassword in accounts:
    print(f"\n🔄 Logging in as {putUsername}...")

    # Navigate to login page
    browser.get("https://roblox.com/login")
    time.sleep(3)

    try:
        # Enter credentials
        username = browser.find_element(By.ID, "login-username")
        password = browser.find_element(By.ID, "login-password")

        username.send_keys(putUsername)
        password.send_keys(putPassword)

        loginBtn = browser.find_element(By.ID, "login-button")
        loginBtn.click()
        time.sleep(10)  # Allow time for login

        # Open id.txt and iterate through user IDs
        with open("id.txt", "r+") as f:
            for line in f:
                user_id = line.strip()
                if not user_id.isdigit():
                    continue  # Skip invalid lines

                print(f"Following user ID: {user_id}...")

                # Visit the user's profile
                browser.get(f"https://roblox.com/users/{user_id}")
                time.sleep(3)

                try:
                    # Click on follow button
                    userOptions = browser.find_element(By.ID, "popover-link")
                    userOptions.click()
                    time.sleep(2)

                    followUser = browser.find_element(By.LINK_TEXT, "Follow")
                    followUser.click()
                    print(f"✅ {putUsername} followed {user_id}!")
                    time.sleep(3)
                except:
                    print(f"⚠️ Could not follow {user_id}, might already be followed!")

    except Exception as e:
        print(f"❌ Error for {putUsername}: {e}")

    print(f"\n🔒 Logging out {putUsername} and switching accounts...\n")
    time.sleep(5)  # Delay before switching to next account

print("✅ Finished following users!")
browser.quit()