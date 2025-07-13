import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import ctypes

# Open Phone Link app
def open_phone_link():
    os.system("start ms-phone:")

# Real exit button after prank is revealed
def reveal_exit():
    messagebox.showinfo("Prank Revealed", "😄 Chill bro! This was just a prank!")
    root.destroy()

# Disable closing by override
def disable_close():
    pass

# Setup GUI
root = tk.Tk()
root.title("Phone Link - Windows Security")
root.geometry("500x550")
root.configure(bg="white")
root.protocol("WM_DELETE_WINDOW", disable_close)
root.resizable(False, False)
root.attributes("-topmost", True)

# Frame
frame = tk.Frame(root, bg="white")
frame.pack(pady=20)

# Load Microsoft logo (local placeholder or skip if error)
try:
    img = Image.open("mslogo.png").resize((60, 60))
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(frame, image=logo, bg="white")
    logo_label.pack()
except:
    tk.Label(frame, text="Microsoft", font=("Segoe UI", 16, "bold"), bg="white").pack()

# Main text
tk.Label(frame, text="Enhance Your Device Security", font=("Segoe UI", 14, "bold"), bg="white", pady=10).pack()
tk.Label(frame, text="Link your phone to enable advanced protection features.", font=("Segoe UI", 10), bg="white").pack()

# Features
features = [
    "✔ Cross-device authentication",
    "✔ Real-time suspicious activity alerts",
    "✔ Secure file sharing",
    "✔ Enhanced network protection"
]
for feat in features:
    tk.Label(frame, text=feat, font=("Segoe UI", 10), bg="white", anchor="w", padx=20).pack(fill="x", pady=2)

# Warning
tk.Label(frame, text="⚠ Your device is currently not linked.", fg="red", font=("Segoe UI", 10), bg="white", pady=10).pack()

# Info
tk.Label(frame, text="This prompt will stay on top until you connect your phone.", font=("Segoe UI", 9), fg="gray", bg="white").pack()

# Button
tk.Button(frame, text="Connect Phone", font=("Segoe UI", 12, "bold"), bg="#0078D7", fg="white",
          padx=20, pady=5, command=lambda:[open_phone_link(), reveal_exit()]).pack(pady=20)

root.mainloop()
