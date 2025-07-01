import subprocess
import tkinter as tk
from tkinter import messagebox

def get_adapters():
    # grab all non-loopback interfaces
    p = subprocess.run(
        ["netsh", "interface", "show", "interface"],
        capture_output=True, text=True
    )
    lines = p.stdout.splitlines()[3:]
    names = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 4 and parts[0] != 'Disabled':
            names.append(" ".join(parts[3:]))
    return names

def apply_dns():
    dns1 = entry1.get().strip()
    dns2 = entry2.get().strip()
    if not dns1:
        messagebox.showerror("Error", "Main DNS can’t be empty")
        return
    iface = var_iface.get()
    # set primary
    cmd1 = ["netsh", "interface", "ip", "set", "dns", f'name={iface}', "static", dns1, "primary"]
    cmds = [cmd1]
    # alt, if provided
    if dns2:
        cmds.append(
            ["netsh", "interface", "ip", "add", "dns", f'name={iface}', dns2, "index=2"]
        )
    for cmd in cmds:
        subprocess.run(cmd, shell=True)
    messagebox.showinfo("Done", f"DNS set to {dns1}" + (f", {dns2}" if dns2 else ""))

def clear_dns():
    iface = var_iface.get()
    cmd = ["netsh", "interface", "ip", "set", "dns", f'name={iface}', "dhcp"]
    subprocess.run(cmd, shell=True)
    messagebox.showinfo("Done", "DNS cleared (now using DHCP)")

root = tk.Tk()
root.title("DNS Switcher")
root.geometry("350x200")
# Interface dropdown
tk.Label(root, text="Interface:").pack(pady=(10,0))
var_iface = tk.StringVar(root)
adapters = get_adapters()
if not adapters:
    messagebox.showerror("Error", "No network adapters found")
    root.destroy()
var_iface.set(adapters[0])
tk.OptionMenu(root, var_iface, *adapters).pack()
# DNS entries
tk.Label(root, text="Primary DNS:").pack(pady=(10,0))
entry1 = tk.Entry(root); entry1.pack()
tk.Label(root, text="Alternate DNS (opt):").pack(pady=(5,0))
entry2 = tk.Entry(root); entry2.pack()
# Buttons
frm = tk.Frame(root); frm.pack(pady=15)
tk.Button(frm, text="Apply", width=10, command=apply_dns).grid(row=0, column=0, padx=5)
tk.Button(frm, text="Clear/DHCP", width=10, command=clear_dns).grid(row=0, column=1, padx=5)
root.mainloop()
