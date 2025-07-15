import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import winreg

reg_path = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}}"
MAC_BACKUP_FILE = "mac_backup.txt"

def get_adapters():
    adapters = []
    for i in range(1000):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{reg_path[:-1]}\\{i:04d}")
            name, _ = winreg.QueryValueEx(key, "DriverDesc")
            adapters.append((name, f"{reg_path[:-1]}\\{i:04d}"))
        except:
            continue
    return adapters

def get_mac_from_registry(adapter_key):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, adapter_key)
        mac, _ = winreg.QueryValueEx(key, "NetworkAddress")
        return mac
    except:
        return None

def set_mac(adapter_key, new_mac):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, adapter_key, 0, winreg.KEY_ALL_ACCESS)
    if new_mac:
        winreg.SetValueEx(key, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
    else:
        try:
            winreg.DeleteValue(key, "NetworkAddress")
        except FileNotFoundError:
            pass

def disable_enable_adapter(name):
    os.system(f'netsh interface set interface name="{name}" admin=disable')
    os.system(f'netsh interface set interface name="{name}" admin=enable')

def spoof_mac():
    name = combo.get()
    key = adapter_dict.get(name)
    if not key:
        messagebox.showerror("Помилка", "Адаптер не вибрано")
        return

    old_mac = get_mac_from_registry(key)
    with open(MAC_BACKUP_FILE, "w") as f:
        f.write(f"{name}|{old_mac if old_mac else ''}")

    new_mac = "02" + "".join([f"{i:02X}" for i in os.urandom(5)])
    set_mac(key, new_mac)
    disable_enable_adapter(name)
    messagebox.showinfo("Готово", f"Новий MAC: {new_mac}")

def restore_mac():
    if not os.path.exists(MAC_BACKUP_FILE):
        messagebox.showerror("Помилка", "Немає збереженого MAC")
        return

    with open(MAC_BACKUP_FILE, "r") as f:
        line = f.read().strip()
        name, mac = line.split("|")

    key = adapter_dict.get(name)
    if not key:
        messagebox.showerror("Помилка", "Адаптер не знайдено")
        return

    set_mac(key, mac if mac else "")
    disable_enable_adapter(name)
    messagebox.showinfo("Відновлено", f"MAC адаптера '{name}' відновлено")

# GUI
root = tk.Tk()
root.title("MAC Spoofer")
root.geometry("400x200")

tk.Label(root, text="Вибери адаптер:").pack(pady=5)
combo = ttk.Combobox(root, width=50)
combo.pack(pady=5)

adapter_list = get_adapters()
adapter_dict = {name: key for name, key in adapter_list}
combo["values"] = list(adapter_dict.keys())
if adapter_list:
    combo.set(adapter_list[0][0])

tk.Button(root, text="Спуфнути MAC", command=spoof_mac, height=2).pack(fill="x", padx=10, pady=10)
tk.Button(root, text="Відновити MAC", command=restore_mac, height=2).pack(fill="x", padx=10)

root.mainloop()
