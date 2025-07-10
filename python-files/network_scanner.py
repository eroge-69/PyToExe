import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import scapy.all as scapy
import socket
import nmap
import requests
import pandas as pd
import netifaces
import ipaddress

# MAC vendor lookup funkcija sa fallback-om
def get_mac_vendor(mac):
    try:
        r1 = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
        if r1.status_code == 200 and r1.text.strip():
            return r1.text.strip()
    except:
        pass

    try:
        r2 = requests.get(f"https://api.maclookup.app/v2/macs/{mac}", timeout=5)
        if r2.status_code == 200:
            data = r2.json()
            return data.get("company", "Unknown")
    except:
        pass

    return "Unknown"

def scan_ports(ip, scan_type):
    scanner = nmap.PortScanner()
    try:
        scanner.scan(ip, arguments=scan_type)
        ports = []
        for proto in scanner[ip].all_protocols():
            for port in scanner[ip][proto]:
                state = scanner[ip][proto][port]['state']
                ports.append(f"{port}/{state}")
        return ", ".join(ports)
    except:
        return "N/A"

def scan_network(ip_range, scan_type):
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    devices = []

    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "Unknown"
        vendor = get_mac_vendor(mac)
        ports = scan_ports(ip, scan_type)
        devices.append({
            "IP": ip,
            "Hostname": hostname,
            "MAC": mac,
            "Vendor": vendor,
            "Ports": ports
        })

    return devices

class NetworkScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Scanner GUI")
        self.root.geometry("980x550")
        self.devices = []

        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Mrežni Interfejs:").grid(row=0, column=0)

        self.interfaces = self.get_interfaces()
        self.interface_var = tk.StringVar()
        self.interface_menu = ttk.Combobox(frame, textvariable=self.interface_var, values=self.interfaces, width=30)
        self.interface_menu.grid(row=0, column=1)
        self.interface_menu.bind("<<ComboboxSelected>>", self.set_ip_range)
        self.interface_menu.current(0)

        tk.Label(frame, text="IP Range:").grid(row=0, column=2, padx=10)
        self.ip_entry = tk.Entry(frame, width=22)
        self.ip_entry.grid(row=0, column=3)
        self.set_ip_range()

        tk.Label(frame, text="Scan Type:").grid(row=0, column=4, padx=10)
        self.scan_type = ttk.Combobox(frame, values=[
            "-T4 -F (Quick Scan)", "-T4 -p- (Full Scan)", "Custom"
        ])
        self.scan_type.current(0)
        self.scan_type.grid(row=0, column=5)

        self.custom_args = tk.Entry(frame, width=20)
        self.custom_args.grid(row=0, column=6, padx=10)
        self.custom_args.insert(0, "-T4 -F")

        tk.Button(frame, text="Start Scan", command=self.start_scan).grid(row=0, column=7, padx=10)

        self.tree = ttk.Treeview(root, columns=("IP", "Hostname", "MAC", "Vendor", "Ports"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=180)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        tk.Button(root, text="💾 Sačuvaj u CSV", command=self.save_csv).pack(pady=5)

    def get_interfaces(self):
        interfaces = []
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                ip_info = addrs[netifaces.AF_INET][0]
                ip_addr = ip_info.get("addr")
                netmask = ip_info.get("netmask")
                if ip_addr and netmask:
                    try:
                        cidr = ipaddress.IPv4Network(f"{ip_addr}/{netmask}", strict=False)
                        interfaces.append(f"{iface} ({ip_addr})|{cidr.with_prefixlen}")
                    except:
                        pass
        return interfaces

    def set_ip_range(self, event=None):
        selected = self.interface_var.get()
        if "|" in selected:
            _, ip_range = selected.split("|")
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, ip_range)

    def start_scan(self):
        ip_range = self.ip_entry.get().strip()
        scan_type = self.scan_type.get()

        if "Custom" in scan_type:
            scan_args = self.custom_args.get().strip()
        elif "Quick" in scan_type:
            scan_args = "-T4 -F"
        elif "Full" in scan_type:
            scan_args = "-T4 -p-"
        else:
            scan_args = "-T4 -F"

        self.tree.delete(*self.tree.get_children())
        try:
            self.devices = scan_network(ip_range, scan_args)
            for dev in self.devices:
                self.tree.insert("", "end", values=(
                    dev["IP"], dev["Hostname"], dev["MAC"], dev["Vendor"], dev["Ports"]
                ))
        except Exception as e:
            messagebox.showerror("Greška", f"Greška pri skeniranju: {e}")

    def save_csv(self):
        if not self.devices:
            messagebox.showwarning("Upozorenje", "Nema podataka za čuvanje.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.DataFrame(self.devices)
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Uspeh", f"Fajl sačuvan: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerApp(root)
    root.mainloop()
