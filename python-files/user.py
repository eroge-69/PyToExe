import tkinter as tk
from tkinter import messagebox
import random
import string
import webbrowser
import time

def generate_usernames(length, count=20):
    chars = string.ascii_lowercase + string.digits
    usernames = set()
    while len(usernames) < count:
        usernames.add(''.join(random.choice(chars) for _ in range(length)))
    return list(usernames)

def open_usernames(usernames):
    for u in usernames:
        url = f"https://www.tiktok.com/@{u}"
        webbrowser.open(url)
        time.sleep(3)

def on_generate():
    try:
        length = int(entry_length.get())
        if length not in [2, 3]:
            messagebox.showerror("خطأ", "اختر طول 2 أو 3 فقط")
            return
        count = int(entry_count.get())
        usernames = generate_usernames(length, count)
        text_box.delete("1.0", tk.END)
        for u in usernames:
            text_box.insert(tk.END, u + "\n")
    except ValueError:
        messagebox.showerror("خطأ", "دخل رقم صحيح")

def on_open():
    usernames = text_box.get("1.0", tk.END).strip().split("\n")
    if usernames:
        open_usernames(usernames[:10])  # يفتح أول 10 فقط لتجربة
    else:
        messagebox.showinfo("معلومة", "مفيش يوزرات في القائمة")

root = tk.Tk()
root.title("Username Checker - TikTok")

tk.Label(root, text="طول اليوزر (2 أو 3):").pack()
entry_length = tk.Entry(root)
entry_length.pack()

tk.Label(root, text="عدد اليوزرات:").pack()
entry_count = tk.Entry(root)
entry_count.insert(0, "20")
entry_count.pack()

tk.Button(root, text="توليد يوزرات", command=on_generate).pack(pady=5)
tk.Button(root, text="فتح الروابط في المتصفح", command=on_open).pack(pady=5)

text_box = tk.Text(root, height=15, width=30)
text_box.pack()

root.mainloop()
