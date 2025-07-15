
import pyautogui
import pytesseract
from playsound import playsound
from plyer import notification
import time, os, sys

# Tesseract yo‘li
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

TRIGGERS = ["long", "short"]

def resource_path(rel):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, rel)

ALERT_SOUND = resource_path("alert.mp3")

def check_screen():
    img = pyautogui.screenshot()
    text = pytesseract.image_to_string(img).lower()
    for w in TRIGGERS:
        if w in text:
            playsound(ALERT_SOUND)
            notification.notify(
                title="📢 Signal aniqlandi!",
                message=f"Ekranda '{w.upper()}' so‘zi topildi.",
                timeout=5
            )
            break

print("🔍 Monitoring boshlandi (Ctrl+C - to‘xtatish)...")
try:
    while True:
        check_screen()
        time.sleep(3)
except KeyboardInterrupt:
    print("🛑 Monitoring to‘xtatildi.")
