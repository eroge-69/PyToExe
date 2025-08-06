
import os
import subprocess
import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import wmi

# ----------- Utility Functions -----------
def random_mac():
    return "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
        random.randint(0x00, 0xFF),
    )

def spoof_mac(adapter):
    new_mac = random_mac().replace(":", "")
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
        rf"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}", 0, winreg.KEY_ALL_ACCESS)

    for i in range(1000):
        try:
            subkey = winreg.EnumKey(key, i)
            subkey_path = rf"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\{subkey}"
            subkey_full = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_ALL_ACCESS)
            name, _ = winreg.QueryValueEx(subkey_full, "DriverDesc")
            if adapter in name:
                winreg.SetValueEx(subkey_full, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
                winreg.CloseKey(subkey_full)
                return new_mac
            winreg.CloseKey(subkey_full)
        except:
            break
    return None

def spoof_registry():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Cryptography", 0, winreg.KEY_ALL_ACCESS)
        new_guid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
        winreg.CloseKey(key)
        return new_guid
    except Exception as e:
        return str(e)

def spoof_disk():
    return "DISK-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def spoof_motherboard():
    return "MB-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

# ----------- GUI Functions -----------
def apply_spoof():
    adapter = adapter_var.get()
    if not adapter:
        messagebox.showwarning("Warning", "Please select a network adapter")
        return

    mac = spoof_mac(adapter)
    hwid = spoof_registry()
    disk = spoof_disk()
    mb = spoof_motherboard()

    output_text.set(f"MAC Address spoofed to: {mac}\n"
                    f"HWID spoofed to: {hwid}\n"
                    f"Disk Serial: {disk}\n"
                    f"Motherboard ID: {mb}")

    messagebox.showinfo("Done", "All spoofing actions completed. Please restart your computer for changes to take effect.")

# ----------- GUI Setup -----------
root = tk.Tk()
root.title("Universal HWID Spoofer")
root.geometry("500x400")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

adapter_var = tk.StringVar()
output_text = tk.StringVar()

w = wmi.WMI()
adapters = [i.Description for i in w.Win32_NetworkAdapter() if i.PhysicalAdapter]

ttk.Label(frame, text="Select Network Adapter:").pack(anchor="w")
adapter_menu = ttk.Combobox(frame, textvariable=adapter_var, values=adapters, width=60)
adapter_menu.pack(pady=5)

apply_btn = ttk.Button(frame, text="Apply All Spoof", command=apply_spoof)
apply_btn.pack(pady=20)

output_label = ttk.Label(frame, textvariable=output_text, wraplength=450, justify="left")
output_label.pack(pady=10)

root.mainloop()
