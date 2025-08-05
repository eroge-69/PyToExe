import tkinter as tk
from tkinter import messagebox
import threading
import time
import random

# FAKE PHASE 🌀 GUI with ANIMATED STARS

class Star:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2.5)
        self.star = canvas.create_oval(self.x, self.y, self.x + self.size, self.y + self.size, fill="white", outline="")

    def move(self, height):
        self.y += self.speed
        if self.y > height:
            self.y = 0
            self.x = random.randint(0, self.canvas.winfo_width())
        self.canvas.coords(self.star, self.x, self.y, self.x + self.size, self.y + self.size)

def animate_stars():
    while True:
        for star in stars:
            star.move(height)
        time.sleep(0.02)

def fake_inject():
    log_console("[PHASE] Initiating space link...")
    time.sleep(1)
    log_console("[PHASE] Aligning with orbit path...")
    time.sleep(1)
    log_console("[✔] PHASE is ready. Injection sequence complete.")
    messagebox.showinfo("PHASE 🌀", "Stabilized. You may now phase in your script.")

def fake_execute():
    script = script_box.get("1.0", tk.END).strip()
    if script:
        log_console(f"[PHASE] Phasing script into reality...")
        time.sleep(1)
        log_console(f"[✔] Script phased successfully!")
    else:
        log_console("[!] Empty script detected.")

def log_console(msg):
    console.config(state=tk.NORMAL)
    console.insert(tk.END, msg + "\n")
    console.see(tk.END)
    console.config(state=tk.DISABLED)

def inject_thread():
    threading.Thread(target=fake_inject).start()

def execute_thread():
    threading.Thread(target=fake_execute).start()

# GUI Window
root = tk.Tk()
root.title("PHASE 🌀")
root.geometry("800x550")
root.resizable(False, False)

# Star Canvas BG
width, height = 800, 550
canvas = tk.Canvas(root, width=width, height=height, bg="#0b0b1c", highlightthickness=0)
canvas.place(x=0, y=0)

stars = [Star(canvas, width, height) for _ in range(100)]
threading.Thread(target=animate_stars, daemon=True).start()

# UI Frame
frame = tk.Frame(root, bg="#151526")
frame.place(relx=0.5, rely=0.5, anchor="center", width=700, height=450)

title = tk.Label(frame, text="PHASE 🌀", font=("Segoe UI", 20, "bold"), fg="#00ffff", bg="#151526")
title.pack(pady=10)

# Script Box
script_box = tk.Text(frame, height=8, width=80, bg="#1e1e2f", fg="white", insertbackground="white", font=("Consolas", 10), bd=0)
script_box.pack(pady=10)

# Buttons Frame
btns = tk.Frame(frame, bg="#151526")
btns.pack(pady=5)

inject_btn = tk.Button(btns, text="Inject", command=inject_thread, bg="#00bcd4", fg="white", font=("Segoe UI", 10, "bold"), width=15, bd=0)
inject_btn.grid(row=0, column=0, padx=10)

execute_btn = tk.Button(btns, text="Execute", command=execute_thread, bg="#4caf50", fg="white", font=("Segoe UI", 10, "bold"), width=15, bd=0)
execute_btn.grid(row=0, column=1, padx=10)

# Console Output
console = tk.Text(frame, height=8, width=80, bg="#101018", fg="#00ff88", state=tk.DISABLED, font=("Consolas", 10), bd=0)
console.pack(pady=10)

# Run app
root.mainloop()
