import os
import shutil
import tempfile
import tkinter as tk
from tkinter import messagebox
import ctypes
import winshell
from pathlib import Path

def delete_files_in_folder(folder):
    deleted_count = 0
    for root, dirs, files in os.walk(folder):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                os.remove(file_path)
                deleted_count += 1
            except:
                pass
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                shutil.rmtree(dir_path)
                deleted_count += 1
            except:
                pass
    return deleted_count

def get_browser_cache_paths():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    paths = [
        os.path.join(local, 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
        os.path.join(local, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
        os.path.join(roaming, 'Mozilla', 'Firefox', 'Profiles')
    ]

    firefox_cache = []
    if os.path.exists(paths[2]):
        for profile in os.listdir(paths[2]):
            cache_path = os.path.join(paths[2], profile, 'cache2')
            if os.path.exists(cache_path):
                firefox_cache.append(cache_path)

    return [paths[0], paths[1]] + firefox_cache

def empty_recycle_bin():
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        return True
    except:
        return False

def clean_temp_files():
    answer = messagebox.askyesno("ยืนยัน", "คุณต้องการลบไฟล์ขยะทั้งหมดหรือไม่?")
    if not answer:
        return

    temp_dirs = [tempfile.gettempdir(), r"C:\Windows\Temp"]
    browser_cache = get_browser_cache_paths()
    total_deleted = 0

    for folder in temp_dirs + browser_cache:
        if os.path.exists(folder):
            total_deleted += delete_files_in_folder(folder)

    if empty_recycle_bin():
        messagebox.showinfo("สำเร็จ", f"ลบไฟล์ขยะสำเร็จแล้ว {total_deleted} ไฟล์/โฟลเดอร์\nรวมถึง Recycle Bin")
    else:
        messagebox.showinfo("สำเร็จบางส่วน", f"ลบไฟล์ขยะได้ {total_deleted} ไฟล์/โฟลเดอร์\n(ไม่สามารถล้าง Recycle Bin ได้)")

root = tk.Tk()
root.withdraw()

if ctypes.windll.shell32.IsUserAnAdmin():
    clean_temp_files()
else:
    messagebox.showerror("ต้องใช้สิทธิ์ Admin", "กรุณารันโปรแกรมด้วยสิทธิ์ผู้ดูแลระบบ (Run as Administrator)")
