import tkinter as tk
from tkinter import messagebox
import winsound  

# الإعدادات
goal = 10  
count = 0

def add_ticket(event=None):  
    global count
    count += 1
    label_count.config(text=f"عدد التكتات: {count}")
    if count >= goal:
        winsound.Beep(1000, 500)  
        messagebox.showinfo("مبروك!", f"وصلت الهدف: {goal} تكت 🎉")

# الواجهة
root = tk.Tk()
root.title("حساب تكتات Magic City")
root.geometry("350x300")

# العداد
label_count = tk.Label(root, text=f"عدد التكتات: {count}", font=("Arial", 16))
label_count.pack(pady=30)

# زر بالماوس (اختياري)
btn_add = tk.Button(
    root,
    text="اضغط لإضافة تكت 🎟️",
    font=("Arial", 14),
    command=add_ticket
)
btn_add.pack(pady=20)

# ربط زر الكيبورد "/"
root.bind("/", add_ticket)

root.mainloop()