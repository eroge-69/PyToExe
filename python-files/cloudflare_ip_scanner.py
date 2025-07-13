
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import socket
import subprocess
import requests
import random

def get_cloudflare_ips(limit):
    try:
        ipv4_list = requests.get("https://www.cloudflare.com/ips-v4").text.strip().split('\n')
        all_ips = []
        for ip_range in ipv4_list:
            base_ip = ip_range.split('/')[0]
            all_ips.append(base_ip)
        random.shuffle(all_ips)
        return all_ips[:limit]
    except Exception as e:
        return []

def ping_ip(ip):
    try:
        result = subprocess.run(["ping", "-n", "1", "-w", "500", ip], capture_output=True, text=True)
        if "time=" in result.stdout:
            return result.stdout.split("time=")[1].split("ms")[0].strip() + " ms"
        else:
            return "Timeout"
    except:
        return "Error"

def scan_ports(ip, ports):
    open_ports = []
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=0.5):
                open_ports.append(port)
        except:
            pass
    return open_ports

def run_scan(limit, update_ui_callback, finish_callback):
    ips = get_cloudflare_ips(limit)
    ports_to_scan = list(range(1, 1025))
    for ip in ips:
        ping_result = ping_ip(ip)
        open_ports = scan_ports(ip, ports_to_scan)
        update_ui_callback(ip, ping_result, open_ports)
    finish_callback()

class IPScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloudflare IP Scanner")

        self.frame = ttk.Frame(root, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.frame, text="تعداد IP برای اسکن:").grid(row=0, column=0, sticky="w")
        self.ip_count = tk.IntVar(value=10)
        ttk.Entry(self.frame, textvariable=self.ip_count).grid(row=0, column=1, sticky="ew")

        self.start_button = ttk.Button(self.frame, text="شروع اسکن", command=self.start_scan)
        self.start_button.grid(row=0, column=2, padx=5)

        self.tree = ttk.Treeview(self.frame, columns=("ip", "ping", "ports"), show="headings")
        self.tree.heading("ip", text="IP")
        self.tree.heading("ping", text="پینگ")
        self.tree.heading("ports", text="پورت‌های باز")
        self.tree.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")

        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.save_button = ttk.Button(self.frame, text="ذخیره خروجی", command=self.save_results)
        self.save_button.grid(row=2, column=2, sticky="e")

        self.results = []

    def update_ui(self, ip, ping_result, open_ports):
        self.tree.insert("", "end", values=(ip, ping_result, ", ".join(map(str, open_ports))))
        self.results.append((ip, ping_result, open_ports))

    def finish_scan(self):
        messagebox.showinfo("پایان", "اسکن IPها به پایان رسید.")

    def start_scan(self):
        self.tree.delete(*self.tree.get_children())
        self.results = []
        count = self.ip_count.get()
        if count <= 0:
            messagebox.showerror("خطا", "تعداد IP باید بزرگتر از صفر باشد.")
            return
        threading.Thread(target=run_scan, args=(count, self.update_ui, self.finish_scan), daemon=True).start()

    def save_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if not file_path:
            return
        with open(file_path, "w") as f:
            for ip, ping, ports in self.results:
                f.write(f"{ip}\t{ping}\t{', '.join(map(str, ports))}\n")
        messagebox.showinfo("ذخیره شد", "نتایج با موفقیت ذخیره شدند.")

if __name__ == "__main__":
    root = tk.Tk()
    app = IPScannerApp(root)
    root.mainloop()
