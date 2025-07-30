
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import ipaddress
import queue
import platform

class IPScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Scanner")

        # Input fields
        ttk.Label(root, text="Local Adapter IP:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.local_ip_entry = ttk.Entry(root)
        self.local_ip_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(root, text="Subnet Mask:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.subnet_mask_entry = ttk.Entry(root)
        self.subnet_mask_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(root, text="Starting IP (last octet):").grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.start_octet_entry = ttk.Entry(root)
        self.start_octet_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(root, text="Ending IP (last octet):").grid(row=3, column=0, sticky='e', padx=5, pady=5)
        self.end_octet_entry = ttk.Entry(root)
        self.end_octet_entry.grid(row=3, column=1, padx=5, pady=5)

        # Output text box
        self.output_text = scrolledtext.ScrolledText(root, width=60, height=20)
        self.output_text.grid(row=4, column=0, columnspan=2, padx=5, pady=10)

        # Buttons
        self.run_button = ttk.Button(root, text="Run", command=self.start_scan)
        self.run_button.grid(row=5, column=0, sticky='ew', padx=5, pady=5)

        self.cancel_button = ttk.Button(root, text="Cancel", command=self.cancel_scan)
        self.cancel_button.grid(row=5, column=1, sticky='ew', padx=5, pady=5)

        self.exit_button = ttk.Button(root, text="Exit", command=self.exit_program)
        self.exit_button.grid(row=6, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        self.scanning = threading.Event()
        self.queue = queue.Queue()
        self.scan_thread = None

        self.root.protocol("WM_DELETE_WINDOW", self.exit_program)
        self.root.after(100, self.process_queue)

    def start_scan(self):
        if self.scanning.is_set():
            messagebox.showinfo("Info", "Scan already in progress.")
            return
        self.output_text.delete(1.0, tk.END)
        self.scanning.set()
        self.scan_thread = threading.Thread(target=self.scan_ips)
        self.scan_thread.start()

    def cancel_scan(self):
        self.scanning.clear()

    def exit_program(self):
        if self.scanning.is_set():
            self.output_text.insert(tk.END, "\nCancelling scan before exit...\n")
            self.cancel_scan()
            self.root.after(3000, self.finalize_exit)
        else:
            self.finalize_exit()

    def finalize_exit(self):
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join()
        self.root.destroy()

    def scan_ips(self):
        local_ip = self.local_ip_entry.get().strip()
        try:
            base_ip = ".".join(local_ip.split(".")[:3])
            start_octet = int(self.start_octet_entry.get())
            end_octet = int(self.end_octet_entry.get())
        except Exception:
            self.queue.put("Invalid input. Please check IP and octet values.\n")
            self.scanning.clear()
            return

        active_ips = []
        for i in range(start_octet, end_octet + 1):
            if not self.scanning.is_set():
                break
            ip = f"{base_ip}.{i}"
            if platform.system().lower() == "windows":
                result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], stdout=subprocess.DEVNULL)
            else:
                result = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                active_ips.append(ip)
                self.queue.put(f"Active: {ip}\n")
        self.queue.put(f"\nTotal Active IPs: {len(active_ips)}\n")
        self.scanning.clear()

    def process_queue(self):
        try:
            while True:
                line = self.queue.get_nowait()
                self.output_text.insert(tk.END, line)
                self.output_text.see(tk.END)
        except queue.Empty:
            pass
        self.root.after(100, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = IPScannerApp(root)
    root.mainloop()
