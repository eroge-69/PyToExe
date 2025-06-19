import os
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

# Kikapcsolás időzítése
def schedule_shutdown(hours):
    seconds = hours * 3600
    shutdown_time = datetime.now() + timedelta(seconds=seconds)
    shutdown_time_str = shutdown_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"A gép {shutdown_time_str}-kor fog leállni.")
    os.system(f"shutdown /s /t {seconds}")
    messagebox.showinfo("Időzítés", f"A gép {hours} óra múlva ({shutdown_time_str}) le fog állni.")

# Leállítás megszakítása
def cancel_shutdown():
    os.system("shutdown /a")
    print("Leállítás megszakítva.")
    messagebox.showinfo("Megszakítva", "A leállítás sikeresen megszakítva.")

# Időzítés indítása szálon
def start_shutdown(hours):
    threading.Thread(target=schedule_shutdown, args=(hours,)).start()

# GUI létrehozása modern dizájnnal
root = tk.Tk()
root.title("Gépkikapcsolás időzítéssel")
root.geometry("500x600")
root.configure(bg="#2e2e2e")

label = tk.Label(root, text="Válassz, hány óra múlva kapcsoljon ki:", font=("Segoe UI", 14, "bold"), bg="#2e2e2e", fg="#ffffff")
label.pack(pady=20)

# Időzítés gombok dinamikus generálása
button_frame = tk.Frame(root, bg="#2e2e2e")
button_frame.pack(pady=10)

button_style = {
    "width": 8, "height": 2, "font": ("Segoe UI", 11),
    "bg": "#4CAF50", "fg": "white",
    "activebackground": "#45a049", "bd": 0, "relief": "ridge"
}

# 1–24 órás opciók elhelyezése 4 oszlopos rácsban
for i in range(24):
    hour = i + 1
    row = i // 4
    col = i % 4
    btn = tk.Button(button_frame, text=f"{hour} óra", command=lambda h=hour: start_shutdown(h), **button_style)
    btn.grid(row=row, column=col, padx=8, pady=8)

# Megszakítás gomb
cancel_button = tk.Button(
    root, text="Megszakítás", font=("Segoe UI", 12, "bold"),
    bg="#f44336", fg="white", activebackground="#e53935",
    bd=0, relief="ridge", command=cancel_shutdown
)
cancel_button.pack(pady=30)

root.mainloop()
