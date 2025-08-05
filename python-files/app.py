import ctypes
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

SPI_SETDESKWALLPAPER = 20

# Function to set desktop background
def set_wallpaper(image_path):
    abs_path = os.path.abspath(image_path)
    if not os.path.exists(abs_path):
        messagebox.showerror("Error", "File not found!")
        return
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, abs_path, 3)
    messagebox.showinfo("Success", "Wallpaper changed!")

# GUI App
app = tk.Tk()
app.title("Desktop Background Changer")
app.geometry("400x200")

label = tk.Label(app, text="Choose an image to set as desktop background", wraplength=380)
label.pack(pady=10)

image_path_var = tk.StringVar()
entry = tk.Entry(app, textvariable=image_path_var, width=40)
entry.pack(pady=5)

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")])
    if file_path:
        image_path_var.set(file_path)

def apply_wallpaper():
    set_wallpaper(image_path_var.get())

browse_btn = tk.Button(app, text="Browse", command=browse_file)
browse_btn.pack(pady=5)

apply_btn = tk.Button(app, text="Set as Background", command=apply_wallpaper)
apply_btn.pack(pady=20)

app.mainloop()
