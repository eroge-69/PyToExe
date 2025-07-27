
import tkinter as tk
import datetime
import time
import threading
import base64
from io import BytesIO
from PIL import Image, ImageTk

# صورة افتراضية مدمجة (صورة حسابك مصغرة)
avatar_base64 = """
iVBORw0KGgoAAAANSUhEUgAAAJYAAACWCAMAAAAL34HQAAAAWlBMVEUAAAD///8/Pz+/v7+9vb3V1dWbm5uampqWlpZ8fHzr6+ubm5uCgoJJSUn8/PzT09OHh4fS0tJ5eXnCwsJ7e3uRkZHMzMyDg4PMzMwkJCTExMS+vr6hoaHWGttRAAACiElEQVR4nO2a25KDIAyFj8EWQZz//3vqYTdSCkkns6HfczAvq1Ml1fVRtGzRrDQUQIkSZIkSZIkSeQp+GcjV5QMjXYiEXwphV9y6f2MQIn4yiE/jkGn93ry6b9fQdDaOihxCHzSlc0qnW9kYj3wlyEO0Jm0hsy6K4e7cDgPkLkRzPA9CEc9w6fsMyKZf3YiPChPV4TzGAVrgje2FsjKREmhFFjKzGWHeQz+qW8soJfWDZRxnTf2j9eBo3D9AY8jJm8LNoT0qXHZvZTnDEMeN3wNmwDHezN2z7Rw9VljDdhzctbAc1tc23+GyyK5ObaZwLNLbEoPf+KON9aUHr2x9Uj9HWRX2zRa0PF/bHPZFrqXl9MBXN9bdS7Uqxttkb2JdnEyaM6xHNW/8ZH9znxZRvWyy5D/VcyU/lsdgj7YkeE3rYhnkWvnPluQVeW3n9nY69x6vdgLWLXTw9u8EftN30Y4mK87PRC6HE/XHa2e0G7DsJ30ZYeR7m6qvq5B3Z21R1HfHuQXHXe6d7A1tLVzUvvTUl57nyzKN41s49R3fqZJfi3XXTXojfD2pRtv5M4/J+u8fpz+zSbgEAAAAAAAAAAAAAAACAP/gD3E6R+/0nHNsAAAAASUVORK5CYII=
"""

image_data = base64.b64decode(avatar_base64)
image = Image.open(BytesIO(image_data))

# التاريخ المستهدف
target_time = datetime.datetime(2026, 1, 1, 6, 27, 0)

messages = [
    "I miss your account...",
    "The game is not the same without you.",
    "Nothing feels right without you.",
    "Waiting for you to come back...",
    "Roblox is quiet without QAXz3fran..."
]

def update_timer():
    while True:
        now = datetime.datetime.now()
        diff = target_time - now
        if diff.total_seconds() <= 0:
            timer_label.config(text="🎉 Unbanned! Welcome back!")
            break
        days = diff.days
        hours, rem = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = diff.microseconds // 1000
        countdown_text = f"{days}d {hours:02}h {minutes:02}m {seconds:02}s {milliseconds:03}ms"
        timer_label.config(text=countdown_text)
        time.sleep(0.01)

def cycle_messages():
    idx = 0
    while True:
        msg_label.config(text=messages[idx])
        idx = (idx + 1) % len(messages)
        time.sleep(4)

root = tk.Tk()
root.title("Roblox Countdown - QAXz3fran")
root.geometry("440x580")
root.configure(bg="#1e1e2f")

# التاريخ
now = datetime.datetime.now()
date_en = now.strftime("%A, %B %d, %Y")
date_ar = now.strftime("%Y/%m/%d") + " هجري"

tk.Label(root, text=date_en, font=("Segoe UI", 12), fg="#aaa", bg="#1e1e2f").pack(pady=(10,0))
tk.Label(root, text=date_ar, font=("Segoe UI", 12), fg="#aaa", bg="#1e1e2f").pack()

tk.Label(root, text="QAXz3fran", font=("Segoe UI", 20, "bold"), fg="#00ffc3", bg="#1e1e2f").pack(pady=(10,5))

# الصورة
img_resized = image.resize((180, 180))
photo = ImageTk.PhotoImage(img_resized)
tk.Label(root, image=photo, bg="#1e1e2f").pack(pady=10)

# التايمر
timer_label = tk.Label(root, text="", font=("Consolas", 20), fg="#00ffcc", bg="#1e1e2f")
timer_label.pack(pady=10)

# الرسالة
msg_label = tk.Label(root, text="", font=("Segoe UI", 14), fg="#ffb3b3", bg="#1e1e2f", wraplength=400, justify="center")
msg_label.pack(pady=20)

tk.Label(root, text="— designed for someone who's missed ❤️", font=("Segoe UI", 10), fg="#666", bg="#1e1e2f").pack(side="bottom", pady=15)

# تشغيل الحلقات
threading.Thread(target=update_timer, daemon=True).start()
threading.Thread(target=cycle_messages, daemon=True).start()

root.mainloop()
