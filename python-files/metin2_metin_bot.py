
import pyautogui
import cv2
import numpy as np
import time
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # pyinstaller için
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Metin taşı görseli
template_path = resource_path("metin_tasi.png")
metin_template = cv2.imread(template_path)

def screenshot():
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return image

def find_metin(image):
    result = cv2.matchTemplate(image, metin_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > 0.75:
        return max_loc
    return None

print("BOT 5 saniye içinde başlayacak. Oyuna geç.")
time.sleep(5)

while True:
    img = screenshot()
    metin_pos = find_metin(img)

    if metin_pos:
        x, y = metin_pos
        pyautogui.moveTo(x + 20, y + 20, duration=0.2)
        pyautogui.click()
        print("✅ Metin bulundu, tıklanıyor.")
        time.sleep(15)
    else:
        print("❌ Metin bulunamadı.")
        time.sleep(1)
