import winreg
import ctypes
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import pystray
import threading

# Check USB status
def get_usb_status():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                             0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, "Start")
        winreg.CloseKey(key)
        return value  # 3=unblocked, 4=blocked
    except:
        return None

# Show popup
def show_popup(message):
    ctypes.windll.user32.MessageBoxW(0, message, "USB Control", 0x40)

# Block USB
def block_usb(icon=None, item=None):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
        winreg.CloseKey(key)
        show_popup("USB storage devices are now BLOCKED.")
        update_icon()
    except:
        show_popup("Error: Run as Administrator!")

# Unblock USB
def unblock_usb(icon=None, item=None):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 3)
        winreg.CloseKey(key)
        show_popup("USB storage devices are now UNBLOCKED.")
        update_icon()
    except:
        show_popup("Error: Run as Administrator!")

# Create tray icon image
def create_icon(color):
    image = Image.new('RGB', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((8, 8, 56, 56), fill=color)  # colored dot
    draw.rectangle((26, 18, 38, 46), fill="white")  # simple USB icon
    draw.rectangle((30, 14, 34, 18), fill="white")  # top of USB
    return image

# Open GUI window
def open_gui(icon=None, item=None):
    def gui_thread():
        root = tk.Tk()
        root.title("USB Control")
        root.geometry("200x120")
        root.resizable(False, False)

        btn_block = tk.Button(root, text="ON (Block USB)", bg="red", fg="white", width=20, command=block_usb)
        btn_block.pack(pady=10)

        btn_unblock = tk.Button(root, text="OFF (Unblock USB)", bg="green", fg="white", width=20, command=unblock_usb)
        btn_unblock.pack(pady=10)

        root.mainloop()
    threading.Thread(target=gui_thread).start()

# Update tray menu dynamically
def get_menu():
    status = get_usb_status()
    if status == 4:  # blocked
        return pystray.Menu(
            pystray.MenuItem("Open Control", open_gui),
            pystray.MenuItem("Block USB", block_usb, enabled=False),  # greyed out
            pystray.MenuItem("Unblock USB", unblock_usb),
            pystray.MenuItem("Exit", lambda icon, item: icon.stop())
        )
    else:  # unblocked
        return pystray.Menu(
            pystray.MenuItem("Open Control", open_gui),
            pystray.MenuItem("Block USB", block_usb),
            pystray.MenuItem("Unblock USB", unblock_usb, enabled=False),  # greyed out
            pystray.MenuItem("Exit", lambda icon, item: icon.stop())
        )

# Update tray icon and menu
def update_icon():
    status = get_usb_status()
    if status == 4:
        icon.icon = create_icon("red")
    else:
        icon.icon = create_icon("green")
    icon.menu = get_menu()
    icon.visible = True

# Start tray icon
icon = pystray.Icon("usb_tray", create_icon("green"), "USB Control", get_menu())
update_icon()
icon.run()
