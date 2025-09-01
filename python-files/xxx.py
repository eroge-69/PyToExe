import shutil
import os
import time
import sys
import ctypes
import string
from pathlib import Path
import winsound
import random

# رنگ سبز روی مشکی
os.system("color 0A")

# فول‌اسکرین
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
SW_MAXIMIZE = 3
hWnd = kernel32.GetConsoleWindow()
user32.ShowWindow(hWnd, SW_MAXIMIZE)

# گرفتن مسیر پوشه از کاربر
source_folder = input("📂 Enter the folder path to copy: ").strip()
if not os.path.exists(source_folder):
    print("❌ Folder not found!")
    os.system("pause >nul")
    sys.exit()

# پیدا کردن اولین فلش وصل شده
def get_removable_drives():
    drives = []
    bitmask = kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:\\"
            if kernel32.GetDriveTypeW(drive) == 2:  # removable
                drives.append(drive)
        bitmask >>= 1
    return drives

usb_drives = get_removable_drives()
if not usb_drives:
    print("❌ No USB drive found. Insert a flash and try again.")
    os.system("pause >nul")
    sys.exit()

# مسیر hack داخل فلش
usb_hack_path = os.path.join(usb_drives[0], "hack")
os.makedirs(usb_hack_path, exist_ok=True)

print(f"[+] Copying to: {usb_hack_path}\n")
time.sleep(1)

# شروع کپی با افکت تایپ و صدای کلیک
try:
    dest_path = os.path.join(usb_hack_path, os.path.basename(source_folder))
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            src = os.path.join(root, file)
            rel_path = os.path.relpath(src, source_folder)
            dst = os.path.join(dest_path, rel_path)

            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

            # نمایش فیلمی
            for char in f"{rel_path}\n":
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(random.uniform(0.002, 0.008))  # افکت تایپ

            # صدای کلیک کوتاه
            winsound.Beep(800, 15)

    print("\n✅ Mission Complete. All files copied successfully!")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\nPress any key to exit...")
os.system("pause >nul")
