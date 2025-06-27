
import tkinter as tk
from datetime import datetime, timedelta
import threading
from tkinter import simpledialog

# เวลาเริ่มต้น 1 ชั่วโมงจากตอนเปิด
countdown_time = timedelta(hours=1)
end_time = datetime.now() + countdown_time

def update_timer():
    global end_time
    while True:
        now = datetime.now()
        remaining = end_time - now

        if remaining.total_seconds() <= 0:
            label.config(text="หมดเวลา!")
        else:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            hrs, mins = divmod(mins, 60)
            timer_text = f"{hrs:02d}:{mins:02d}:{secs:02d}"
            label.config(text=timer_text)

        label.after(1000, lambda: None)
        root.update()
        if remaining.total_seconds() <= 0:
            break

def listen_for_password():
    global end_time
    while True:
        root.withdraw()
        password = simpledialog.askstring("Password", "ใส่รหัสเพื่อรีเซ็ตเวลา (เช่น 1996+):", show='*')
        root.deiconify()
        if password == "1996+":
            end_time = datetime.now() + timedelta(hours=1)

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.8)
root.configure(bg='black')

screen_width = root.winfo_screenwidth()
label = tk.Label(root, text="", fg="white", bg="black", font=("Courier", 16))
label.pack()

window_width = 100
window_height = 40
x = screen_width - window_width - 10
y = 10
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

threading.Thread(target=update_timer, daemon=True).start()
threading.Thread(target=listen_for_password, daemon=True).start()

root.mainloop()
