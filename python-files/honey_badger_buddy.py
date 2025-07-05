import tkinter as tk
from tkinter import messagebox
import random
import threading
import time
import ctypes
import sys
import os
import base64

# Base64 encoded 64x64 transparent PNG honey badger sprite
b64_image = """
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIAAAAlC+aJAAAAGXRFWHRTb2Z0d2Fy
ZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAANdJREFUeNrs1DEOwjAMheGv//VYOYb
Tgj1LcNNMPXFrxT8T8Dh4kQRV3W/RCbBZ8vl1ZQG8dHuIQDFeAwHq9YYcRTE4XY
dpAzjPXBeNJ0zjm3tHgEWh7GslECAiKBgGoPDx7EF2HL0th7CZbCmAAz0SYYAEj
iNTA69hDwVvzn1p53ULdxBwzMD7H7ZC4dAocFgZ7FbC0YsAzBcOd7c1EGEe28KI
Prll3eXACBSlEhxYAQJ0BpACv1bGYCsBgAPXZXugGJ2raAAAAAElFTkSuQmCC
"""

def move_mouse(dx, dy):
    ctypes.windll.user32.mouse_event(1, dx, dy, 0, 0)

class HoneyBadgerBuddy(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "white")

        self.geometry("64x64+100+100")

        self.canvas = tk.Canvas(self, width=64, height=64, bg='white', highlightthickness=0)
        self.canvas.pack()

        # Decode image from base64 and create PhotoImage
        image_data = base64.b64decode(b64_image)
        self.img = tk.PhotoImage(data=image_data)
        self.sprite = self.canvas.create_image(32, 32, image=self.img)

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.x = 100
        self.y = 100
        self.direction = 1

        self.bind("<Button-3>", self.close_buddy)

        threading.Thread(target=self.move_loop, daemon=True).start()
        threading.Thread(target=self.mischief_loop, daemon=True).start()

    def move_loop(self):
        while True:
            self.x += 10 * self.direction
            if self.x > self.screen_width - 64:
                self.direction = -1
            elif self.x < 0:
                self.direction = 1
            self.geometry(f"+{self.x}+{self.y}")
            time.sleep(0.2)

    def mischief_loop(self):
        quotes = [
            "Honey badger don't care!",
            "Messing things up... just because.",
            "I'm the baddest honey badger around!",
            "Stay out of my way!",
            "Oops! Did I do that?"
        ]
        while True:
            time.sleep(random.randint(15, 30))
            self.after(0, lambda q=random.choice(quotes): messagebox.showinfo("Honey Badger", q))
            move_mouse(random.choice([-50, -30, 30, 50]), random.choice([-30, 30]))

    def close_buddy(self, event):
        self.destroy()

if __name__ == "__main__":
    app = HoneyBadgerBuddy()
    app.mainloop()
