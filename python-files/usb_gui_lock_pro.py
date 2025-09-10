import os
import stat
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import simpledialog, messagebox
import psutil
import threading
import time

# সেটিংস
PASSWORD = "1234"
FOLDER_NAME = "Secret"   # ফোল্ডার যা লক/আনলক হবে
KEY_FILE = "locker.key"
LOCKER_EXE_NAME = "usb_gui_lock_pro.exe"  # exe নাম

# কী ফাইল বানানো
def create_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as keyfile:
        keyfile.write(key)

def load_key():
    return open(KEY_FILE, "rb").read()

# ফোল্ডার এনক্রিপ্ট/ডিক্রিপ্ট
def encrypt_folder(folder):
    if not os.path.exists(folder):
        messagebox.showerror("Error", f"'{folder}' ফোল্ডার পাওয়া যায়নি!")
        return
    key = load_key()
    fernet = Fernet(key)
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            with open(path, "rb") as f:
                data = f.read()
            encrypted = fernet.encrypt(data)
            with open(path, "wb") as f:
                f.write(encrypted)
    messagebox.showinfo("Success", "🔒 Folder Locked Successfully!")

def decrypt_folder(folder):
    if not os.path.exists(folder):
        messagebox.showerror("Error", f"'{folder}' ফোল্ডার পাওয়া যায়নি!")
        return
    pwd = simpledialog.askstring("Password", "Enter Password:", show="*")
    if pwd != PASSWORD:
        messagebox.showerror("Error", "❌ Wrong Password!")
        return
    key = load_key()
    fernet = Fernet(key)
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            with open(path, "rb") as f:
                data = f.read()
            decrypted = fernet.decrypt(data)
            with open(path, "wb") as f:
                f.write(decrypted)
    messagebox.showinfo("Success", "✅ Folder Unlocked Successfully!")

# Read-Only / Write-Only
def set_read_only(folder):
    if not os.path.exists(folder):
        messagebox.showerror("Error", f"'{folder}' ফোল্ডার পাওয়া যায়নি!")
        return
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            os.chmod(path, stat.S_IREAD)
    messagebox.showinfo("Success", "📖 Folder set to Read-Only!")

def set_write_only(folder):
    if not os.path.exists(folder):
        messagebox.showerror("Error", f"'{folder}' ফোল্ডার পাওয়া যায়নি!")
        return
    for root, dirs, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            os.chmod(path, stat.S_IWRITE)
    messagebox.showinfo("Success", "✍️ Folder set to Write-Only!")

# Auto-detect USB and launch Locker
def auto_detect_usb():
    while True:
        drives = [d.device for d in psutil.disk_partitions() if 'removable' in d.opts]
        for drive in drives:
            exe_path = os.path.join(drive, LOCKER_EXE_NAME)
            folder_path = os.path.join(drive, FOLDER_NAME)
            if os.path.exists(exe_path) and os.path.exists(folder_path):
                threading.Thread(target=lambda: decrypt_folder(folder_path)).start()
                return
        time.sleep(5)  # প্রতি 5 সেকেন্ডে চেক করবে

# কী ফাইল না থাকলে বানানো হবে
if not os.path.exists(KEY_FILE):
    create_key()

# GUI তৈরি
root = tk.Tk()
root.title("USB Locker Pro - Full Security")
root.geometry("350x300")
root.resizable(False, False)

tk.Label(root, text="🔐 USB Locker Pro", font=("Arial", 14, "bold")).pack(pady=10)

tk.Button(root, text="Lock Folder", command=lambda: encrypt_folder(FOLDER_NAME),
          width=25, bg="red", fg="white").pack(pady=5)
tk.Button(root, text="Unlock Folder", command=lambda: decrypt_folder(FOLDER_NAME),
          width=25, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Set Read-Only", command=lambda: set_read_only(FOLDER_NAME),
          width=25, bg="blue", fg="white").pack(pady=5)
tk.Button(root, text="Set Write-Only", command=lambda: set_write_only(FOLDER_NAME),
          width=25, bg="orange", fg="black").pack(pady=5)

# Auto-detect USB চালু
threading.Thread(target=auto_detect_usb, daemon=True).start()

root.mainloop()