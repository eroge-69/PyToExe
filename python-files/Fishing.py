import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import pytesseract
import time
import keyboard
import threading
import tkinter as tk

# ❗ Tesseract-Pfad anpassen, falls notwendig
pytesseract.pytesseract.tesseract_cmd = r""C:\Users\Passi\Downloads\tesseract-ocr-w64-setup-5.5.0.20241111.exe""

# Farbbereiche
BLAU_MIN = np.array([130, 0, 0])
BLAU_MAX = np.array([255, 50, 50])

ROT_MIN = np.array([0, 0, 150])
ROT_MAX = np.array([50, 50, 255])

GUELTIGE_TASTEN = {"W", "A", "S", "D", "Q", "E"}
AUSSCHNITT_HALB = 100

# Bildschirmmitte
screen_width, screen_height = pyautogui.size()
cx, cy = screen_width // 2, screen_height // 2
REGION = (cx - AUSSCHNITT_HALB, cy - AUSSCHNITT_HALB, cx + AUSSCHNITT_HALB, cy + AUSSCHNITT_HALB)

# Zustand
aktiv = False

# --- Funktionen ---
def farbe_erkannt(img, farb_min, farb_max, name, schwelle):
    maske = cv2.inRange(img, farb_min, farb_max)
    count = cv2.countNonZero(maske)
    return count > schwelle

def ocr_buchstabe(img):
    h, w, _ = img.shape
    mitte = img[h//2 - 25:h//2 + 25, w//2 - 25:w//2 + 25]
    grau = cv2.cvtColor(mitte, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(grau, config="--psm 10 -c tessedit_char_whitelist=WASDQE")
    buchstabe = text.strip().upper()
    if buchstabe in GUELTIGE_TASTEN:
        print(f"🎯 Taste erkannt: {buchstabe}")
        return buchstabe
    return None

def toggle():
    global aktiv
    aktiv = not aktiv
    status = "AKTIV" if aktiv else "INAKTIV"
    print(f"🔁 Status geändert: {status}")
    update_overlay()

# --- Overlay ---
root = tk.Tk()
root.overrideredirect(True)  # Kein Fensterrahmen
root.attributes("-topmost", True)  # Immer im Vordergrund
root.geometry("150x40+10+10")  # Position & Größe
root.wm_attributes("-transparentcolor", "black")  # Hintergrund durchsichtig (optional)

canvas = tk.Canvas(root, width=150, height=40, bg="black", highlightthickness=0)
canvas.pack()

def update_overlay():
    canvas.delete("all")
    status_text = "Script aktiv" if aktiv else "Script inaktiv"
    farbe = "green" if aktiv else "red"
    canvas.create_text(60, 20, text=status_text, fill="white", font=("Arial", 12))
    canvas.create_oval(10, 10, 30, 30, fill=farbe)

update_overlay()

# --- Hauptloop ---
def main_loop():
    global aktiv
    while True:
        if aktiv:
            screenshot = ImageGrab.grab(bbox=REGION)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            blau = farbe_erkannt(img, BLAU_MIN, BLAU_MAX, "Blau", schwelle=100)
            rot = farbe_erkannt(img, ROT_MIN, ROT_MAX, "Rot", schwelle=20)

            if blau and rot:
                taste = ocr_buchstabe(img)
                if taste:
                    print(f"✅ Bedingung erfüllt – drücke Taste '{taste}'")
                    pyautogui.press(taste.lower())
                    time.sleep(0.5)
            else:
                time.sleep(0.1)
        else:
            time.sleep(0.1)

# Hotkey
keyboard.add_hotkey("F7", toggle)

# Threads starten
threading.Thread(target=main_loop, daemon=True).start()
threading.Thread(target=keyboard.wait, daemon=True).start()

# Overlay starten
root.mainloop()
