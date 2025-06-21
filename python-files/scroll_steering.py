
import sys
import threading
import tkinter as tk
from pynput import mouse
import pyvjoy

# إنشاء نافذة واجهة بسيطة
root = tk.Tk()
root.title("Scroll Steering")
root.geometry("300x150")
label = tk.Label(root, text="لف السكرول لتحريك الدريكسيون", font=("Arial", 12))
label.pack(pady=20)

status_label = tk.Label(root, text="القيمة الحالية: 0.50", font=("Arial", 10))
status_label.pack()

# ربط مع vJoy
j = pyvjoy.VJoyDevice(1)
steer = 0.5

def update_status():
    status_label.config(text=f"القيمة الحالية: {steer:.2f}")

def on_scroll(x, y, dx, dy):
    global steer
    if dy > 0:
        steer = max(0.0, steer - 0.02)
    elif dy < 0:
        steer = min(1.0, steer + 0.02)
    j.set_axis(pyvjoy.HID_USAGE_X, int(steer * 32767))
    update_status()

# تفعيل الاستماع للسكرول
listener = mouse.Listener(on_scroll=on_scroll)
listener.start()

# تشغيل الواجهة
threading.Thread(target=root.mainloop).start()
