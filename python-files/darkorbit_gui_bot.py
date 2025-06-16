
import tkinter as tk
from threading import Thread
import cv2
import numpy as np
import pyautogui
import mss
import time
import random

running = False

# Színtartományok (RGB)
resource_colors = {
    "Palladium": ([200, 200, 200], [255, 255, 255]),
    "Cargo":     ([130, 80, 0],    [200, 150, 50]),
    "Prometium": ([180, 0, 0],     [255, 80, 80]),
    "Endurium":  ([0, 180, 0],     [80, 255, 80]),
    "Terbium":   ([0, 0, 180],     [80, 80, 255]),
}

def random_delay(min_d=0.5, max_d=1.5):
    time.sleep(random.uniform(min_d, max_d))

def find_and_collect(update_log):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = np.array(sct.grab(monitor))
        image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        for name, (lower, upper) in resource_colors.items():
            mask = cv2.inRange(image, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if 5 < w < 40 and 5 < h < 40:
                    cx = x + w // 2 + random.randint(-3, 3)
                    cy = y + h // 2 + random.randint(-3, 3)
                    pyautogui.moveTo(cx, cy, duration=0.1)
                    pyautogui.click()
                    update_log(f"[{name}] Kattintás: ({cx}, {cy})")
                    random_delay(2, 3)
                    return
        update_log("Nem található nyersanyag.")

def bot_loop(update_log):
    global running
    while running:
        find_and_collect(update_log)
        random_delay(0.5, 1.0)

def start_bot(update_log):
    global running
    if not running:
        running = True
        Thread(target=bot_loop, args=(update_log,), daemon=True).start()
        update_log("✅ Bot elindítva")

def stop_bot(update_log):
    global running
    running = False
    update_log("⛔ Bot leállítva")

def main():
    window = tk.Tk()
    window.title("DarkOrbit Resource Bot")
    window.geometry("400x300")

    log = tk.Text(window, height=15, width=50)
    log.pack(pady=10)

    def update_log(msg):
        log.insert(tk.END, msg + "\n")
        log.see(tk.END)

    start_btn = tk.Button(window, text="INDÍTÁS", command=lambda: start_bot(update_log), bg="lightgreen")
    start_btn.pack(side=tk.LEFT, padx=20)

    stop_btn = tk.Button(window, text="LEÁLLÍTÁS", command=lambda: stop_bot(update_log), bg="salmon")
    stop_btn.pack(side=tk.RIGHT, padx=20)

    window.mainloop()

if __name__ == "__main__":
    main()
