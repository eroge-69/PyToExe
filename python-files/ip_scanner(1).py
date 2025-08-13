import socket
import requests
import ipaddress
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import base64
import io

# Placeholder base64 string for the Corsair Solutions logo (replace with actual base64 string)
LOGO_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAAAXNSR0IArs4c6QAAAARnQU1BAACx
jwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAABYSURBVEhL7c4xAQAwDAPB/P9f4oM3FuxG3ZQA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAY/wcX1AABV5rK5gAAAABJRU5ErkJggg==
"""
# Note: Replace LOGO_BASE64 with the actual base64 string of the Corsair Solutions logo from www.corsairsolutions.com.au

def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception as e:
        return f"Error fetching external IP: {e}"

def get_internal_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal_ip = s.getsockname()[0]
        s.close()
        return internal_ip
    except Exception as e:
        return f"Error fetching internal IP: {e}"

def scan_network(ip_base, start, end, queue):
    active_hosts = []
    for i in range(start, end + 1):
        ip = ip_base + str(i)
        try:
            socket.setdefaulttimeout(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, 80))
            active_hosts.append(ip)
            s.close()
        except:
            pass
    queue.put(active_hosts)

def scan_local_network(callback):
    internal_ip = get_internal_ip()
    if "Error" in internal_ip:
        callback(internal_ip)
        return
    
    try:
        network = ipaddress.ip_network(f"{internal_ip}/24", strict=False)
        ip_base = ".".join(internal_ip.split('.')[:-1]) + "."
        
        threads = []
        queue_result = queue.Queue()
        chunk_size = 256 // 4
        for i in range(4):
            start = i * chunk_size + 1
            end = start + chunk_size - 1 if i < 3 else 256
            thread = threading.Thread(target=scan_network, args=(ip_base, start, end, queue_result))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        active_hosts = []
        while not queue_result.empty():
            active_hosts.extend(queue_result.get())
        
        if active_hosts:
            callback("\n".join(active_hosts))
        else:
            callback("No active hosts found")
    except Exception as e:
        callback(f"Error scanning network: {e}")

class IPScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Corsair Solutions IP Scanner")
        self.root.geometry("600x500")
        
        # Decode and display logo
        try:
            logo_data = base64.b64decode(LOGO_BASE64)
            logo_image = Image.open(io.BytesIO(logo_data))
            logo_image = logo_image.resize((150, 50), Image.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(root, image=self.logo)
            logo_label.pack(pady=10)
        except:
            tk.Label(root, text="Corsair Solutions Logo (Failed to load)", font=("Arial", 12)).pack(pady=10)
        
        # GUI elements
        tk.Label(root, text="Corsair Solutions IP Scanner", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.external_ip_label = tk.Label(root, text="External IP: Not fetched", font=("Arial", 12))
        self.external_ip_label.pack(pady=5)
        
        self.internal_ip_label = tk.Label(root, text="Internal IP: Not fetched", font=("Arial", 12))
        self.internal_ip_label.pack(pady=5)
        
        self.scan_button = ttk.Button(root, text="Scan Network", command=self.start_scan)
        self.scan_button.pack(pady=10)
        
        self.result_text = tk.Text(root, height=10, width=50, font=("Arial", 10))
        self.result_text.pack(pady=10)
        self.result_text.insert(tk.END, "Scan results will appear here...")
        self.result_text.config(state='disabled')
        
        # Fetch IPs on startup
        self.fetch_ips()
    
    def fetch_ips(self):
        external_ip = get_external_ip()
        internal_ip = get_internal_ip()
        self.external_ip_label.config(text=f"External IP: {external_ip}")
        self.internal_ip_label.config(text=f"Internal IP: {internal_ip}")
    
    def start_scan(self):
        self.scan_button.config(state='disabled')
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Scanning local network, please wait...")
        self.result_text.config(state='disabled')
        
        def callback(result):
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            self.result_text.config(state='disabled')
            self.scan_button.config(state='normal')
        
        threading.Thread(target=scan_local_network, args=(callback,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = IPScannerApp(root)
    root.mainloop()