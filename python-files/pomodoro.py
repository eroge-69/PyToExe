import tkinter as tk
from tkinter import messagebox
import time
import threading
import winsound   # Windows only

WORK_MIN  = 25
BREAK_MIN = 5
running   = False

def countdown(seconds):
    global running
    while seconds and running:
        mins, secs = divmod(seconds, 60)
        label_time.config(text=f"{mins:02d}:{secs:02d}")
        time.sleep(1)
        seconds -= 1
    if running:
        winsound.Beep(1000, 800)   # آلارم
        swap_phase()

def swap_phase():
    global phase_seconds
    if label_phase.cget("text") == "کار":
        # رفتن به استراحت
        phase_seconds = BREAK_MIN * 60
        label_phase.config(text="استراحت")
    else:
        # برگشت به کار
        phase_seconds = WORK_MIN * 60
        label_phase.config(text="کار")
    threading.Thread(target=countdown, args=(phase_seconds,), daemon=True).start()

def start_stop():
    global running, phase_seconds
    if running:
        running = False
        btn_start.config(text="ادامه")
        return
    running = True
    btn_start.config(text="توقف")
    # اگر اولین بار یا بعد از ری‌ست هستیم
    if label_time.cget("text") in (f"{WORK_MIN:02d}:00", f"{BREAK_MIN:02d}:00"):
        phase_seconds = WORK_MIN * 60
        label_phase.config(text="کار")
    threading.Thread(target=countdown, args=(phase_seconds,), daemon=True).start()

def reset():
    global running, phase_seconds
    running = False
    phase_seconds = WORK_MIN * 60
    label_time.config(text=f"{WORK_MIN:02d}:00")
    label_phase.config(text="کار")
    btn_start.config(text="شروع")

# ساخت پنجره
phase_seconds = WORK_MIN * 60   # مقدار اولیه: ۲۵ دقیقه کار

root = tk.Tk()
root.title("Pomodoro Timer")
root.geometry("220x160")
root.resizable(False, False)

label_phase = tk.Label(root, text="کار", font=("Tahoma", 16))
label_phase.pack(pady=5)
label_time  = tk.Label(root, text=f"{WORK_MIN:02d}:00", font=("Tahoma", 32))
label_time.pack()

btn_start = tk.Button(root, text="شروع", width=10, command=start_stop)
btn_start.pack(side="left", padx=15, pady=10)

btn_reset = tk.Button(root, text="ری‌استارت", width=10, command=reset)
btn_reset.pack(side="right", padx=15, pady=10)

root.mainloop()
