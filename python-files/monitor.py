import psutil
import os
import time
from datetime import datetime
import sys

# ตำแหน่งไฟล์ log (เก็บไว้ที่เดียวกับ .exe/.py)
log_file = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "process_log.txt")

# สร้าง shortcut ไว้ใน Startup (ครั้งเดียว)
def create_startup_shortcut():
    try:
        import win32com.client
        startup = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_path = os.path.join(startup, "monitor.lnk")
        if not os.path.exists(shortcut_path):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.WorkingDirectory = os.path.dirname(sys.executable)
            shortcut.IconLocation = sys.executable
            shortcut.save()
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Failed to create startup shortcut: {e}\n")

# สร้าง shortcut ถ้ายังไม่มี
create_startup_shortcut()

# เซตชื่อโปรแกรมที่เคยเจอไว้
seen = set()

# วนลูปทุก 3 วินาที
while True:
    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name and name.lower() not in seen:
                seen.add(name.lower())
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {name} started\n")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    time.sleep(3)
