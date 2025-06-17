import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import webbrowser

# ฟังก์ชันตรวจสอบรหัสผ่าน
def check_password():
    password = password_entry.get()
    if password == "1234":
        window.destroy()
        play_video()
    else:
        messagebox.showerror("รหัสผิด", "Key Error")

# ฟังก์ชันเล่นวิดีโอ
def play_video():
    # วิธีที่ 1: เปิด YouTube (ใส่ URL จริงได้เลย)
    # webbrowser.open("https://www.youtube.com/shorts/3hb4XRuLR4U?feature=share")

    # วิธีที่ 2: เปิดไฟล์ video.mp4 ที่อยู่ในโฟลเดอร์เดียวกัน
    os.startfile("video.mp4")

# ---------- สร้างหน้าต่างหลัก ---------- #
window = tk.Tk()
window.title("Jeelight CMD")
window.geometry("600x400")
window.resizable(False, False)

# ---------- โหลดและตั้งค่ารูปพื้นหลัง ---------- #
bg_image = Image.open("background.png")
bg_image = bg_image.resize((600, 400), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(window, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# ---------- ช่องกรอกรหัส ---------- #
password_entry = tk.Entry(window, show="*", font=("Arial", 14))
password_entry.place(x=200, y=250, width=200)

submit_btn = tk.Button(window, text="ENTER", font=("Arial", 12), command=check_password)
submit_btn.place(x=260, y=290)

window.mainloop()
