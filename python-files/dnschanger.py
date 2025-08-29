import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import socket
import urllib.request
import json
import time
import threading
import os
import sys
import ctypes
import platform

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def run_as_admin():
    if not is_admin():
        messagebox.showinfo("Admin Required", "Restarting as admin...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def flush_dns():
    try:
        subprocess.run(["ipconfig", "/flushdns"], check=True, capture_output=True)
        messagebox.showinfo("Success", "DNS cache flushed successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to flush DNS: {e}")

def get_network_interfaces():
    interfaces = []
    output = subprocess.run(["netsh", "interface", "ipv4", "show", "addresses"], capture_output=True, text=True).stdout
    lines = output.splitlines()
    current_interface = None
    for line in lines:
        if line.startswith("Configuration for interface"):
            current_interface = line.split('"')[1]
            interfaces.append(current_interface)
    return interfaces

def change_dns(interface, primary, secondary):
    try:
        subprocess.run(["netsh", "interface", "ipv4", "set", "dns", f'name="{interface}"', "static", primary, "primary"], check=True)
        if secondary:
            subprocess.run(["netsh", "interface", "ipv4", "add", "dns", f'name="{interface}"', secondary, "index=2"], check=True)
        messagebox.showinfo("Success", "DNS changed successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to change DNS: {e}")

def get_ip_info():
    try:
        with urllib.request.urlopen("https://ipinfo.io/json") as url:
            data = json.loads(url.read().decode())
            ip = data.get("ip", "N/A")
            isp = data.get("org", "N/A")
            return f"IP: {ip}\nISP: {isp}"
    except Exception as e:
        return f"Error: {e}"

def ping(host):
    try:
        output = subprocess.run(["ping", "-n", "4", host], capture_output=True, text=True)
        return output.stdout
    except Exception as e:
        return f"Error: {e}"

def nslookup(host):
    try:
        output = subprocess.run(["nslookup", host], capture_output=True, text=True)
        return output.stdout
    except Exception as e:
        return f"Error: {e}"

def speedtest():
    try:
        start = time.time()
        with urllib.request.urlopen("http://speedtest1.nyc.ny.speedtest.net/speedtest/random1000x1000.jpg") as response:
            data = response.read()
        end = time.time()
        size = len(data) / 1024 / 1024  # MB
        speed = size / (end - start) * 8  # Mbps
        return f"Download Speed: {speed:.2f} Mbps"
    except Exception as e:
        return f"Error: {e}"

def check_display():
    if platform.system() != "Windows":
        print("This script is designed for Windows with a GUI environment.")
        sys.exit(1)
    try:
        test_root = tk.Tk()
        test_root.destroy()
    except tk.TclError as e:
        print(f"GUI Error: {e}. Ensure you're running on a Windows system with a graphical interface.")
        sys.exit(1)

# GUI Setup
check_display()
root = tk.Tk()
root.title("Network Tool")
root.geometry("600x400")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background="#f0f0f0")
style.configure("TFrame", background="#f0f0f0")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Flush DNS Tab
flush_tab = ttk.Frame(notebook)
notebook.add(flush_tab, text="Flush DNS")
tk.Button(flush_tab, text="Flush DNS", command=flush_dns, width=20).pack(pady=20)

# DNS Changer Tab
dns_tab = ttk.Frame(notebook)
notebook.add(dns_tab, text="DNS Changer")

interfaces = get_network_interfaces()
interface_var = tk.StringVar(value=interfaces[0] if interfaces else "No interfaces")
tk.Label(dns_tab, text="Interface:", bg="#f0f0f0").pack(pady=5)
ttk.OptionMenu(dns_tab, interface_var, *interfaces).pack()

tk.Label(dns_tab, text="Primary DNS:", bg="#f0f0f0").pack(pady=5)
primary_entry = tk.Entry(dns_tab)
primary_entry.pack()

tk.Label(dns_tab, text="Secondary DNS:", bg="#f0f0f0").pack(pady=5)
secondary_entry = tk.Entry(dns_tab)
secondary_entry.pack()

tk.Button(dns_tab, text="Change DNS", command=lambda: change_dns(interface_var.get(), primary_entry.get(), secondary_entry.get()), width=20).pack(pady=10)

# IP Info Tab
ip_tab = ttk.Frame(notebook)
notebook.add(ip_tab, text="IP Info")
ip_label = tk.Label(ip_tab, text="", bg="#f0f0f0", justify="left")
ip_label.pack(pady=20, padx=20)
tk.Button(ip_tab, text="Get IP Info", command=lambda: ip_label.config(text=get_ip_info()), width=20).pack()

# Ping Tab
ping_tab = ttk.Frame(notebook)
notebook.add(ping_tab, text="Ping")
tk.Label(ping_tab, text="Host:", bg="#f0f0f0").pack(pady=5)
ping_entry = tk.Entry(ping_tab)
ping_entry.pack(pady=5)
ping_result = tk.Text(ping_tab, height=10, width=50)
ping_result.pack(pady=5)
tk.Button(ping_tab, text="Ping", command=lambda: [ping_result.delete(1.0, tk.END), ping_result.insert(tk.END, ping(ping_entry.get()))], width=20).pack()

# NSLookup Tab
nslookup_tab = ttk.Frame(notebook)
notebook.add(nslookup_tab, text="NSLookup")
tk.Label(nslookup_tab, text="Host:", bg="#f0f0f0").pack(pady=5)
nslookup_entry = tk.Entry(nslookup_tab)
nslookup_entry.pack(pady=5)
nslookup_result = tk.Text(nslookup_tab, height=10, width=50)
nslookup_result.pack(pady=5)
tk.Button(nslookup_tab, text="NSLookup", command=lambda: [nslookup_result.delete(1.0, tk.END), nslookup_result.insert(tk.END, nslookup(nslookup_entry.get()))], width=20).pack()

# Speedtest Tab
speed_tab = ttk.Frame(notebook)
notebook.add(speed_tab, text="Speedtest")
speed_label = tk.Label(speed_tab, text="", bg="#f0f0f0")
speed_label.pack(pady=20)
def run_speedtest_thread():
    speed_label.config(text="Testing...")
    result = speedtest()
    speed_label.config(text=result)
tk.Button(speed_tab, text="Run Speedtest", command=lambda: threading.Thread(target=run_speedtest_thread).start(), width=20).pack()

if __name__ == "__main__":
    run_as_admin()
    root.mainloop()