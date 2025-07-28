import pyautogui
import tkinter as tk
from PIL import Image, ImageTk

class Magnifier:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry("200x200+500+300")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.9)
        self.label = tk.Label(self.root)
        self.label.pack()
        self.zoom = 4
        self.update()
        self.root.bind("<Alt-F8>", lambda e: self.root.destroy())
        self.root.mainloop()

    def update(self):
        img = pyautogui.screenshot(region=(
            self.root.winfo_x() + 100 - 25, 
            self.root.winfo_y() + 100 - 25, 
            50, 50))
        img = img.resize((200, 200), Image.NEAREST)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.config(image=imgtk)
        self.root.after(30, self.update)

Magnifier()