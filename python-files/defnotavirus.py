import tkinter as tk
import random
import threading
import time
import winsound
import os

DURATION = 15
WINDOWS = 10

# Scary messages and gibberish
MESSAGES = [
    "IM WATCHING YOU",
    "IM IN YOUR PC",
    "I KNOW WHERE YOU LIVE",
    "SYSTEM FAILURE",
    "CRITICAL ERROR",
    "FATAL EXCEPTION"
]
GIBBERISH = "QWERTYUIOPASDFGHJKLZXCVBNM1234567890!@#$%^&*()"

# List of your sound files
SOUNDS = ["beep1.wav", "beep2.wav", "beep3.wav"]  # make sure these are in the same folder

def make_window():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)

    label = tk.Label(root, text=random.choice(MESSAGES), font=("Consolas", 50), fg="white", bg="black")
    label.pack(expand=True)

    end_time = time.time() + DURATION

    def chaos():
        while time.time() < end_time:
            # Flash background colors
            bg_color = random.choice(["red","green","blue","yellow","magenta","cyan","white","orange"])
            fg_color = random.choice(["black","white"])
            root.configure(bg=bg_color)
            label.configure(bg=bg_color, fg=fg_color)

            # Random text or gibberish
            text_type = random.choice([MESSAGES, [GIBBERISH]])
            label.config(text=random.choice(text_type))

            # Play random sound sometimes
            if random.random() < 0.3:
                sound_file = random.choice(SOUNDS)
                winsound.PlaySound(sound_file, winsound.SND_ASYNC)

            # Small jitter effect
            x = random.randint(-10,10)
            y = random.randint(-10,10)
            root.geometry(f"+{x}+{y}")

            time.sleep(0.05)

        root.destroy()

    threading.Thread(target=chaos).start()
    root.mainloop()

threads = []
for _ in range(WINDOWS):
    t = threading.Thread(target=make_window)
    t.start()
    threads.append(t)
    time.sleep(0.05)

for t in threads:
    t.join()

