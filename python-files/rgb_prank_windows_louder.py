# Aktualisiert: Extrem schriller & lauter Ton, 200 RGB/Flash/Statisch Fenster

import ctypes
import threading
import time
import winsound
import random
import tkinter as tk

NUM_WINDOWS = 200

screen_width = ctypes.windll.user32.GetSystemMetrics(0)
screen_height = ctypes.windll.user32.GetSystemMetrics(1)

def play_extreme_beeps():
    def beep_single():
        for _ in range(50):
            # Maximale schrille Frequenz (fast Schmerzgrenze)
            winsound.Beep(8000, 800)  # 8000 Hz, 800 ms Dauer
            time.sleep(0.05)

    # 5 gleichzeitige Beep-Loops für extra Lautstärke
    threads = []
    for _ in range(5):
        t = threading.Thread(target=beep_single)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def rgb_loop(window):
    def change():
        while True:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            color = f"#{r:02x}{g:02x}{b:02x}"
            window.configure(bg=color)
            time.sleep(0.1)
    threading.Thread(target=change, daemon=True).start()

COLORS = ["red", "yellow", "lime", "cyan", "magenta", "orange", "purple", "white"]

def flash_colors(window):
    def change():
        while True:
            color = random.choice(COLORS)
            window.configure(bg=color)
            time.sleep(0.2)
    threading.Thread(target=change, daemon=True).start()

def open_window(index):
    root = tk.Tk()
    root.title(f"PRANK #{index+1}")
    root.geometry("250x100")
    x = random.randint(0, screen_width - 250)
    y = random.randint(0, screen_height - 100)
    root.geometry(f"250x100+{x}+{y}")

    mode = random.choice(["rgb", "flash", "static"])
    if mode == "rgb":
        rgb_loop(root)
    elif mode == "flash":
        flash_colors(root)
    else:
        root.configure(bg=random.choice(COLORS))

    label = tk.Label(root, text="DU WURDEST GETROLLT! 😜", font=("Arial", 12), bg="black", fg="white")
    label.pack(expand=True)

    root.attributes('-topmost', True)
    root.mainloop()

threads = []
for i in range(NUM_WINDOWS):
    t = threading.Thread(target=open_window, args=(i,))
    t.start()
    threads.append(t)

beep_thread = threading.Thread(target=play_extreme_beeps)
beep_thread.start()

for t in threads:
    t.join()
beep_thread.join()
