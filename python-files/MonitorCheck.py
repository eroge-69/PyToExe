
import tkinter as tk
import time
import random

def flicker():
    root = tk.Tk()
    root.configure(bg='black')
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    root.update()
    time.sleep(random.uniform(0.05, 0.15))
    root.destroy()

for _ in range(random.randint(5, 10)):
    time.sleep(random.uniform(2, 6))
    flicker()
