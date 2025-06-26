import tkinter as tk
import math
from tkinter import font as tkfont

def center_window(window, width, height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def interpolate_color(color1, color2, t):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"

def update_colors():
    global phase
    phase += 0.01
    if phase >= 2 * math.pi:
        phase = 0

    t = (math.sin(phase) + 1) / 2
    
    current_color = interpolate_color(purple, blue, t)
    
    root.configure(bg=current_color)
    
    label.config(bg=current_color)
    root.after(30, update_colors)

def change_text():
    global current_text_index
    current_text_index = (current_text_index + 1) % len(texts)
    label.config(text=texts[current_text_index])
    root.after(250, change_text)

purple = (128, 0, 128)
blue = (0, 191, 255)
texts = [
    "•w•",
    "•w•",
    "•w•",
    "•w•",
    "•w•",
    "•w•",
    "•w•",
    "•w•",
    "•w•",
    "•w•",
    "-w-"
]

current_text_index = 0
phase = 0

root = tk.Tk()
root.title(":3")
root.geometry("500x350")

window_width = 500
window_height = 350
center_window(root, window_width, window_height)

try:
    custom_font = tkfont.Font(family="Calibri", size=15, weight="bold")
except:
    custom_font = tkfont.Font(family="Arial", size=15, weight="bold")

label = tk.Label(
    root,
    text=texts[current_text_index],
    font=custom_font,
    fg="white",
    bg="black",
    padx=20,
    pady=10
)
label.place(relx=0.5, rely=0.5, anchor="center")

update_colors()
change_text()

root.mainloop()