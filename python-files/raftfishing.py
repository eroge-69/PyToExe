import pyautogui
import time
import threading
import keyboard
import cv2
import numpy as np
from PIL import ImageGrab

# === KONFIGURACJA ===
REGION = (960, 540, 100, 100)  # Obszar do monitorowania brania (x, y, szer, wys)
THRESHOLD = 30                 # Czułość zmiany pikseli (im niższa, tym bardziej czułe)

active = False  # Czy autołowienie jest aktywne?

def toggle_active():
    global active
    active = not active
    print(f"[INFO] Autołowienie {'AKTYWNE' if active else 'ZATRZYMANE'}")

def cast_fishing_rod():
    pyautogui.mouseDown(button='left')
    time.sleep(1.2)
    pyautogui.mouseUp(button='left')
    print("[CAST] Rzut wędki.")

def pull_fishing_rod():
    pyautogui.click(button='left')
    print("[PULL] Zaciągnięcie!")

def detect_bite(timeout=15):
    start_time = time.time()
    base_image = grab_region()

    while time.time() - start_time < timeout:
        current_image = grab_region()
        diff = cv2.absdiff(base_image, current_image)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, THRESHOLD, 255, cv2.THRESH_BINARY)
        non_zero_count = cv2.countNonZero(thresh)

        if non_zero_count > 200:
            print("[BITE] Wykryto branie!")
            return True

        time.sleep(0.2)

    print("[TIMEOUT] Nie wykryto brania.")
    return False

def grab_region():
    x, y, w, h = REGION
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def fishing_loop():
    global active
    time.sleep(3)
    print("[START] Autołowienie włączone. Naciśnij F8, aby zatrzymać.")

    while True:
        if not active:
            time.sleep(0.5)
            continue

        cast_fishing_rod()
        if detect_bite():
            pull_fishing_rod()

        time.sleep(2)  # Chwila przerwy przed następnym rzutem

def hotkey_listener():
    keyboard.add_hotkey("f8", toggle_active)
    keyboard.wait()  # Zatrzymuje się, aż użytkownik zakończy (Ctrl+C)

if __name__ == "__main__":
    # Uruchamiamy wątki równolegle
    threading.Thread(target=fishing_loop, daemon=True).start()
    hotkey_listener()
