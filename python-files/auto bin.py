import pyautogui
import pytesseract
import cv2
import numpy as np
import threading
import time
import keyboard
from PIL import ImageGrab

DETECT_REGION = (40, 130, 300, 300)  # (left, top, right, bottom)

running = True

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_player():
    screen = ImageGrab.grab(bbox=DETECT_REGION)
    gray = cv2.cvtColor(np.array(screen), cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='eng')
    return bool(text.strip())  

def auto_pk():
    while running:
        if detect_player():
            pyautogui.click()
            time.sleep(PK_DELAY)
        else:
            time.sleep(0.2)

def auto_follow():
    while running:
        if not detect_player():
            pyautogui.press('f')
        time.sleep(F_DELAY)

def listen_stop_key():
    global running
    keyboard.wait(stop_key)
    running = False
    print(">>> Auto đã dừng!")

if __name__ == "__main__":
    print(">>> Auto chạy... nhấn '/' để dừng.")

    threading.Thread(target=listen_stop_key, daemon=True).start()
    threading.Thread(target=auto_pk).start()
    threading.Thread(target=auto_follow).start()
