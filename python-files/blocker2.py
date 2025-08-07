import os
import time
import threading
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import psutil

class ProcessBlockerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Blocker GUI")
        self.stop_event = threading.Event()
        self.worker_thread = None

        # Layout
        tk.Label(root, text="Executable Path:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Browse...", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        self.start_button = tk.Button(root, text="Start Blocking", command=self.start_blocking)
        self.start_button.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.stop_button = tk.Button(root, text="Stop Blocking", command=self.stop_blocking, state="disabled")
        self.stop_button.grid(row=1, column=1, sticky="e", padx=5, pady=5)

        self.log_area = scrolledtext.ScrolledText(root, width=70, height=20, state="disabled")
        self.log_area.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if file_path:
            self.path_var.set(file_path)

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.configure(state="disabled")
        self.log_area.yview(tk.END)

    def start_blocking(self):
        exe_path = self.path_var.get().strip('"')
        if not os.path.isfile(exe_path) or not exe_path.lower().endswith('.exe'):
            messagebox.showerror("Error", "Invalid executable path.")
            return

        self.process_name = os.path.basename(exe_path)
        self.log(f"Starting to block process: {self.process_name}")

        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        self.stop_event.clear()
        self.worker_thread = threading.Thread(target=self.block_loop, daemon=True)
        self.worker_thread.start()

    def stop_blocking(self):
        self.log(f"Stopping blocking of: {self.process_name}")
        self.stop_event.set()
        if self.worker_thread:
            self.worker_thread.join()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def block_loop(self):
        while not self.stop_event.is_set():
            for proc in psutil.process_iter(['name']):
                if proc.info.get('name', '').lower() == self.process_name.lower():
                    try:
                        proc.kill()
                        self.root.after(0, self.log, f"Killed process {self.process_name} (PID {proc.pid})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        self.root.after(0, self.log, f"Error killing process: {e}")
            time.sleep(1)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == '__main__':
    if not is_admin():
        messagebox.showerror("Administrator Privileges Required", "Please run this script as Administrator.")
        exit(1)

    root = tk.Tk()
    app = ProcessBlockerGUI(root)
    root.mainloop()
