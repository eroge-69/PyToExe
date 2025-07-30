import tkinter as tk
from tkinter import ttk
from pynput.keyboard import Controller
import threading
import time

keyboard = Controller()
spamming = False
spam_thread = None

def spam_loop():
    while spamming:
        if e_var.get():
            keyboard.press('e')
            keyboard.release('e')
        if r_var.get():
            keyboard.press('r')
            keyboard.release('r')
        time.sleep(float(delay_entry.get()))

def toggle_spam():
    global spamming, spam_thread
    spamming = not spamming
    toggle_btn.config(text="⏹ Stop" if spamming else "▶ Start")
    if spamming:
        spam_thread = threading.Thread(target=spam_loop, daemon=True)
        spam_thread.start()

# GUI
root = tk.Tk()
root.title("Nebi's Free Macro")
root.geometry("360x170")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

# Custom dark style
style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="#cccccc", font=("Segoe UI", 10))
style.configure("TCheckbutton", background="#1e1e1e", foreground="#00ccff", font=("Segoe UI", 10))
style.configure("TButton", background="#2e2e2e", foreground="#ffffff", font=("Segoe UI", 10), padding=6)
style.map("TButton", background=[("active", "#00aaff")])

# Title
title = tk.Label(root, text="⭒ Press Start :D ⭒", font=("Segoe UI", 16, "bold"),
                 bg="#1e1e1e", fg="#00ccff")
title.pack(pady=(10, 5))

frame = ttk.Frame(root)
frame.pack(pady=10)

# Buttons and options
toggle_btn = ttk.Button(frame, text="▶ Start", command=toggle_spam)
toggle_btn.grid(row=0, column=0, padx=10)

e_var = tk.BooleanVar(value=True)
r_var = tk.BooleanVar(value=True)

ttk.Checkbutton(frame, text="E", variable=e_var).grid(row=0, column=1, padx=5)
ttk.Checkbutton(frame, text="R", variable=r_var).grid(row=0, column=2, padx=5)

ttk.Label(frame, text="Delay (s):").grid(row=0, column=3, padx=5)
delay_entry = ttk.Entry(frame, width=6)
delay_entry.insert(0, "0.1")
delay_entry.grid(row=0, column=4)

root.mainloop()
