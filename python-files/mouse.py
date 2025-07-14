import tkinter as tk
import pyautogui

def update_coords():
    x, y = pyautogui.position()
    label.config(text=f"X: {x}, Y: {y}")
    root.after(100, update_coords)

root = tk.Tk()
root.title("مختصات ماوس")
label = tk.Label(root, font=("Arial", 24))
label.pack(padx=20, pady=20)

update_coords()
root.mainloop()
