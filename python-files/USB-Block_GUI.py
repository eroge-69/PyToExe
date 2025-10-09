import tkinter as tk
from tkinter import messagebox
import winreg

# Function to show popup
def show_popup(message):
    messagebox.showinfo("USB Control", message)

# Block USB
def block_usb():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
        winreg.CloseKey(key)
        show_popup("USB storage devices are now BLOCKED.")
    except PermissionError:
        show_popup("Error: Run as Administrator!")
    except Exception as e:
        show_popup(f"Error: {e}")

# Unblock USB
def unblock_usb():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 3)
        winreg.CloseKey(key)
        show_popup("USB storage devices are now UNBLOCKED.")
    except PermissionError:
        show_popup("Error: Run as Administrator!")
    except Exception as e:
        show_popup(f"Error: {e}")

# GUI window
root = tk.Tk()
root.title("USB Blocker")
root.geometry("250x120")
root.resizable(False, False)

# Buttons
btn_block = tk.Button(root, text="ON (Block USB)", width=20, command=block_usb, bg="red", fg="white")
btn_block.pack(pady=10)

btn_unblock = tk.Button(root, text="OFF (Unblock USB)", width=20, command=unblock_usb, bg="green", fg="white")
btn_unblock.pack(pady=10)

root.mainloop()
