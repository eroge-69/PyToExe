import tkinter as tk
import time
import threading
import winsound
import ctypes
import subprocess
import random

# منع إغلاق النافذة
def disable_event():
    pass

# تعطيل الكيبورد والماوس
def block_input(seconds=6):
    try:
        ctypes.windll.user32.BlockInput(True)
        time.sleep(seconds)
    finally:
        ctypes.windll.user32.BlockInput(False)

# تشغيل صوت مزعج
def beep_loop():
    for _ in range(60):
        winsound.Beep(random.choice([400, 600, 800]), 200)
        time.sleep(1)

# نافذة CMD وهمية
def fake_cmd():
    for i in range(3):
        subprocess.Popen("start cmd /k echo Injecting ransomware payload... && timeout 2", shell=True)
        time.sleep(2)

# واجهة مقلب الرعب
def ransomware_window():
    root = tk.Tk()
    root.title("Dark Hacker Mode")
    root.attributes('-fullscreen', True)
    root.configure(bg="black")
    root.protocol("WM_DELETE_WINDOW", disable_event)

    frame = tk.Frame(root, bg="black")
    frame.pack(expand=True)

    # شعار هكر
    ascii_art = """\
██████╗  █████╗ ██████╗ ██╗  ██╗███████╗██████╗ 
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██████╔╝███████║██████╔╝█████╔╝ █████╗  ██████╔╝
██╔═══╝ ██╔══██║██╔═══╝ ██╔═██╗ ██╔══╝  ██╔══██╗
██║     ██║  ██║██║     ██║  ██╗███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""
    logo = tk.Label(frame, text=ascii_art, font=("Consolas", 10), fg="lime", bg="black", justify="center")
    logo.pack()

    title = tk.Label(frame, text="YOU'VE BEEN HACKED!", font=("Consolas", 32, "bold"), fg="red", bg="black")
    title.pack(pady=20)

    message = tk.Label(frame, text="Your system is being formatted...\nAll files will be lost in:",
                       font=("Consolas", 18), fg="white", bg="black")
    message.pack(pady=10)

    # عداد تنازلي
    countdown_label = tk.Label(frame, font=("Consolas", 36, "bold"), fg="red", bg="black")
    countdown_label.pack()

    # شريط "حذف ملفات"
    progress_label = tk.Label(frame, text="Formatting Drive C: [0%]", font=("Consolas", 16), fg="yellow", bg="black")
    progress_label.pack(pady=10)

    def countdown():
        for i in range(60, -1, -1):
            countdown_label.config(text=f"{i} seconds")
            time.sleep(1)

        # الانفجار الوهمي
        title.config(text="💣 ALL DATA LOST!")
        message.config(text="Goodbye, user. Your system has been wiped.")
        countdown_label.pack_forget()
        progress_label.pack_forget()
        root.configure(bg="blue")

        # شاشة الموت الزرقاء
        bsod = tk.Label(frame, text="A problem has been detected and Windows has been shut down to prevent damage...\n\n*** STOP: 0x000000D1",
                        font=("Consolas", 18), fg="white", bg="blue", justify="left")
        bsod.pack(pady=40)

        time.sleep(3)
        root.configure(bg="green")
        bsod.pack_forget()
        title.config(text="😂 GOTCHA!")
        message.config(text="This was just a prank. Your files are safe.")
        final_msg = tk.Label(frame, text="Made by your dark hacker friend 👽", font=("Consolas", 18), fg="black", bg="green")
        final_msg.pack(pady=30)
        exit_btn = tk.Button(frame, text="Click to Exit", font=("Consolas", 14), command=root.destroy)
        exit_btn.pack()

    # شريط التحميل الوهمي
    def fake_format():
        for i in range(0, 101, 5):
            progress_label.config(text=f"Formatting Drive C: [{i}%]")
            time.sleep(0.25)

    # تحريك الخلفية (Glitch وهمي)
    def background_glitch():
        colors = ["black", "#111111", "#220000", "#000022"]
        for _ in range(30):
            root.configure(bg=random.choice(colors))
            time.sleep(0.1)

    threading.Thread(target=block_input, daemon=True).start()
    threading.Thread(target=beep_loop, daemon=True).start()
    threading.Thread(target=fake_cmd, daemon=True).start()
    threading.Thread(target=fake_format, daemon=True).start()
    threading.Thread(target=background_glitch, daemon=True).start()
    threading.Thread(target=countdown, daemon=True).start()

    root.mainloop()

# تشغيل المقلب
if __name__ == "__main__":
    ransomware_window()
