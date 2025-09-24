import tkinter as tk
import threading
import random
import os
from PIL import Image, ImageTk
import pygame

windows = []
running = True

pygame.mixer.init()

def close_all_windows(event=None):
    global running
    running = False
    for win in windows:
        try:
            win.destroy()
        except:
            pass

def play_sound(sound_obj):
    sound_obj.play()

def spawn_window(root, img, sound_obj):
    if running:
        x = random.randint(0, 1920)
        y = random.randint(0, 1080)
        win = tk.Toplevel(root)
        win.title("DINOSAURIO")
        win.geometry(f"200x150+{x}+{y}")
        windows.append(win)
        label = tk.Label(win, image=img)
        label.image = img
        label.pack(expand=True, fill="both")
        win.bind('<Return>', close_all_windows)
        threading.Thread(target=play_sound, args=(sound_obj,), daemon=True).start()
        root.after(90, lambda: spawn_window(root, img, sound_obj))

root = tk.Tk()
root.withdraw()

img_path = os.path.join(os.path.dirname(__file__), "dino.png")
sound_path = os.path.join(os.path.dirname(__file__), "saurio.mp3")
pil_img = Image.open(img_path)
pil_img = pil_img.resize((150, 150), Image.LANCZOS)
img = ImageTk.PhotoImage(pil_img)

sound_obj = pygame.mixer.Sound(sound_path)

root.after(0, lambda: spawn_window(root, img, sound_obj))
root.mainloop()