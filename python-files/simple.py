# safe_demo_decoy.py
# Harmless demo: opens an image and writes a local log entry.
# DOES NOT REPLICATE, DOES NOT NETWORK, DOES NOT PERSIST.

import tkinter as tk
from PIL import Image, ImageTk    # requires Pillow: pip install Pillow
import time
import os

IMAGE_PATH = "decoy.jpg"   # place a harmless jpg here
LOG_PATH   = "run_log.txt"

def write_log():
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    pid = os.getpid()
    with open(LOG_PATH, "a") as f:
        f.write(f"{ts} - safe_demo_decoy started (pid={pid})\n")

def show_image():
    root = tk.Tk()
    root.title("Sample Photo")
    img = Image.open(IMAGE_PATH)
    tkimg = ImageTk.PhotoImage(img)
    label = tk.Label(root, image=tkimg)
    label.pack()
    # close after a short while so you don't leave windows open during lab
    root.after(8000, root.destroy)  # auto-close after 8 seconds
    root.mainloop()

if __name__ == "__main__":
    write_log()
    show_image()
    # benign exit
