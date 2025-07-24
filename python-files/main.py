import tkinter as tk
from tkinter import messagebox
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pythoncom
import threading
import time
import pystray
from PIL import Image
import gc
import atexit
running = False
icon = None
closing = False
icon_lock_img = Image.open("icon_lock.ico")      # ไอคอนตอนล็อก
icon_unlock_img = Image.open("icon_unlock.ico")  # ไอคอนตอนปลดล็อก
def cleanup():
    gc.collect()
atexit.register(cleanup)
def get_mic_interface():
    """ดึง Interface ของไมค์ พร้อม Initialize/Uninitialize COM"""
    pythoncom.CoInitialize()
    devices = AudioUtilities.GetMicrophone()
    if not devices:
        pythoncom.CoUninitialize()
        return None
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    mic = cast(interface, POINTER(IAudioEndpointVolume))
    pythoncom.CoUninitialize()
    return mic
def set_mic_volume(level):
    mic = get_mic_interface()
    if mic:
        mic.SetMasterVolumeLevelScalar(level, None)
def get_mic_volume():
    try:
        mic = get_mic_interface()
        if mic:
            return mic.GetMasterVolumeLevelScalar()
    except Exception:
        return 0  # ถ้า error ให้รีเทิร์น 0 หรือค่าปลอดภัย
    return 0
def lock_volume():
    global running
    target = volume_scale.get() / 100
    while running:
        current = get_mic_volume()
        if abs(current - target) > 0.01:
            set_mic_volume(target)
            status_label.config(text=f"รีเซ็ตเสียงกลับ: {volume_scale.get()}%")
        else:
            status_label.config(text=f"เสียงคงที่: {volume_scale.get()}%")
        time.sleep(0.1)
def start_lock():
    global running
    if not running:
        running = True
        threading.Thread(target=lock_volume, daemon=True).start()
        messagebox.showinfo("เริ่มทำงาน", "เริ่มล็อกระดับเสียงไมค์แล้ว")
        update_tray_icon()
def stop_lock():
    global running
    running = False
    status_label.config(text="หยุดล็อกเสียง")
    update_tray_icon()
def create_tray_icon():
    """สร้าง Tray Icon ตอนเริ่มโปรแกรม"""
    global icon
    menu = pystray.Menu(
        pystray.MenuItem('Show', show_window),
        pystray.MenuItem('Exit', quit_program)
    )
    icon = pystray.Icon("Mic Lock", icon_unlock_img, "Mic Lock", menu)
    threading.Thread(target=icon.run, daemon=True).start()
def update_tray_icon():
    """อัปเดตไอคอนตามสถานะเรียลไทม์"""
    global icon
    if icon:
        icon.icon = icon_lock_img if running else icon_unlock_img
def show_window(icon_item=None, item=None):
    root.after(0, root.deiconify)
def quit_program(icon_item=None, item=None):
    global running, closing
    closing = True
    running = False
    if icon:
        icon.stop()
    gc.collect()
    root.destroy()
def check_minimize():
    """ตรวจสอบ minimize → ซ่อนไป Tray"""
    if root.state() == "iconic" and not closing:
        root.withdraw()
    root.after(100, check_minimize)
root = tk.Tk()
root.title("Mic Volume Lock")
root.geometry("200x220")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", quit_program)
tk.Label(root, text="เลือกระดับเสียง (%)").pack(pady=10)
volume_scale = tk.Scale(root, from_=0, to=100, orient="horizontal")
volume_scale.set(80)
volume_scale.pack()
tk.Button(root, text="Start Lock", command=start_lock).pack(pady=5)
tk.Button(root, text="Stop Lock", command=stop_lock).pack(pady=5)
status_label = tk.Label(
    root,
    text="ยังไม่เริ่มทำงาน",
    font=("Arial", 12),
    anchor="center",
    width=20,
    wraplength=180
)
status_label.pack(pady=20)
create_tray_icon()
check_minimize()
root.mainloop()