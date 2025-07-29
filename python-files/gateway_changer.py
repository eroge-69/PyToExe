
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re

def get_network_adapters():
    result = subprocess.run(["netsh", "interface", "ipv4", "show", "interfaces"], capture_output=True, text=True)
    adapters = []
    for line in result.stdout.splitlines():
        match = re.search(r'\d+\s+[\d\.]+\s+\w+\s+(\w.+)', line)
        if match:
            adapters.append(match.group(1).strip())
    return adapters

def set_gateway(adapter, gateway):
    try:
        subprocess.run(["netsh", "interface", "ip", "set", "address",
                        f'name={adapter}', "source=dhcp"], check=True)
        subprocess.run(["netsh", "interface", "ip", "set", "address",
                        f'name={adapter}', "static", "dhcp", gateway, "255.255.255.0"], check=True)
        messagebox.showinfo("Thành công", f"Đã đổi gateway thành {gateway} cho adapter {adapter}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Lỗi", "Không thể đổi gateway. Vui lòng chạy tool bằng quyền Administrator.")

def apply_gateway():
    adapter = adapter_var.get()
    gateway = gateway_var.get()
    if adapter and gateway:
        set_gateway(adapter, gateway)
    else:
        messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn adapter và gateway.")

# GUI
root = tk.Tk()
root.title("Tool Đổi Gateway 3 Line")
root.geometry("400x250")

ttk.Label(root, text="Chọn Adapter Mạng:").pack(pady=5)
adapter_var = tk.StringVar()
adapter_combo = ttk.Combobox(root, textvariable=adapter_var, width=40)
adapter_combo['values'] = get_network_adapters()
adapter_combo.pack(pady=5)

gateway_var = tk.StringVar()
ttk.Label(root, text="Chọn Gateway:").pack(pady=5)

for ip in ["192.168.1.1", "192.168.1.2", "192.168.1.3"]:
    ttk.Radiobutton(root, text=ip, value=ip, variable=gateway_var).pack()

ttk.Button(root, text="Đổi Gateway", command=apply_gateway).pack(pady=20)

root.mainloop()
