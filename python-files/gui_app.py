```python
import tkinter as tk
from tkinter import messagebox
import os

# إعداد النافذة
window = tk.Tk()
window.title("SYA App")
window.geometry("300x400")
window.configure(bg="#1a1a1a")

# وظائف الأزرار
def activate():
    messagebox.showinfo("Activate", "تم تفعيل التطبيق!")

def save():
    client_id = client_id_entry.get()
    top_text = top_text_entry.get()
    bottom_text = bottom_text_entry.get()
    telegram_channel = telegram_channel_entry.get()
    start_time = start_time_entry.get()
    
    data = f"Client ID: {client_id}\nTop Text: {top_text}\nBottom Text: {bottom_text}\nTelegram Channel: {telegram_channel}\nStart Time: {start_time}"
    with open("data.txt", "w", encoding="utf-8") as file:
        file.write(data)
    messagebox.showinfo("Save", "تم حفظ البيانات في data.txt")

def stop():
    if messagebox.askyesno("Stop", "هل تريد إيقاف التطبيق؟"):
        window.quit()

# إعداد العناصر
label_title = tk.Label(window, text="SYA App / Activity", fg="white", bg="#1a1a1a", font=("Arial", 14))
label_title.pack(pady=10)

# حقول الإدخال
fields = [("Client ID", 1), ("Top text", 2), ("Bottom text", 3), ("Telegram Channel", 4), ("Start of session", 5)]
entries = {}

for label_text, row in fields:
    tk.Label(window, text=label_text, fg="white", bg="#1a1a1a").grid(row=row, column=0, pady=5, sticky="e")
    entry = tk.Entry(window)
    entry.grid(row=row, column=1, pady=5)
    entries[label_text] = entry

client_id_entry = entries["Client ID"]
top_text_entry = entries["Top text"]
bottom_text_entry = entries["Bottom text"]
telegram_channel_entry = entries["Telegram Channel"]
start_time_entry = entries["Start of session"]
start_time_entry.insert(0, "00:00")

# الأزرار
button_frame = tk.Frame(window, bg="#1a1a1a")
button_frame.pack(pady=20)

tk.Button(button_frame, text="Activate", command=activate, bg="#4CAF50", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Save", command=save, bg="#2196F3", fg="white", padx=10).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Stop", command=stop, bg="#f44336", fg="white", padx=10).pack(side=tk.LEFT, padx=5)

# أيقونة Discord ومعلومات إضافية
tk.Label(window, text="💬 OP#404", fg="#7289DA", bg="#1a1a1a", font=("Arial", 12)).pack(pady=10)

# تشغيل التطبيق
window.mainloop()
```