import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import win32gui
import win32process
import win32api
import win32con
import win32security
import time
import threading
import os
from datetime import datetime
import csv


class HPProcessMonitor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HP Process Monitor")
        self.root.geometry("500x300")
        self.root.resizable(True, True)
        
        # Create logs directory if it doesn't exist
        self.logs_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        self.current_log_file = None
        self.file_counter = 0
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="HP Process Monitor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status display
        self.status_var = tk.StringVar(value="Status: Stopped")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 12))
        status_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Current log file display
        self.log_file_var = tk.StringVar(value="Log File: None")
        log_file_label = ttk.Label(main_frame, textvariable=self.log_file_var, 
                                  font=("Arial", 10), foreground="blue")
        log_file_label.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Monitoring", 
                                      command=self.start_monitoring, width=15)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop Monitoring", 
                                     command=self.stop_monitoring, width=15, 
                                     state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(10, 0))
        
        # Process count display
        self.process_count_var = tk.StringVar(value="HP Processes Found: 0")
        process_count_label = ttk.Label(main_frame, textvariable=self.process_count_var, 
                                       font=("Arial", 10))
        process_count_label.grid(row=4, column=0, columnspan=3, pady=(20, 0))
        
        # File counter display
        self.file_count_var = tk.StringVar(value="Files Created: 0")
        file_count_label = ttk.Label(main_frame, textvariable=self.file_count_var, 
                                    font=("Arial", 10), foreground="green")
        file_count_label.grid(row=5, column=0, columnspan=3, pady=(5, 0))
        
        # Log display area
        log_frame = ttk.LabelFrame(main_frame, text="Recent Log Entries", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, pady=(20, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Text widget for log display with scrollbar
        self.log_text = tk.Text(log_frame, height=8, width=60, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def get_process_owner(self, pid):
        """Get the owner of a process"""
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
            token = win32security.OpenProcessToken(handle, win32security.TOKEN_QUERY)
            user_sid = win32security.GetTokenInformation(token, win32security.TokenUser)[0]
            username = win32security.LookupAccountSid(None, user_sid)[0]
            win32api.CloseHandle(token)
            win32api.CloseHandle(handle)
            return username
        except Exception:
            return "N/A"

    def get_window_title(self, pid):
        """Get window title for a process"""
        def enum_windows_proc(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        windows.append(title)
            return True
        
        windows = []
        try:
            win32gui.EnumWindows(enum_windows_proc, windows)
            return windows[0] if windows else "N/A"
        except Exception:
            return "N/A"

    def get_hp_processes(self):
        """Get all processes that start with HP"""
        hp_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                if proc.info['name'].upper().startswith('HP'):
                    pid = proc.info['pid']
                    process_name = proc.info['name']
                    
                    # Get window title and owner
                    window_title = self.get_window_title(pid)
                    owner = self.get_process_owner(pid)
                    
                    hp_processes.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'pid': pid,
                        'process_name': process_name,
                        'window_title': window_title,
                        'owner': owner
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return hp_processes

    def log_processes(self, processes):
        """Log processes to CSV file - creates a NEW file every time (every 2 seconds)"""
        if not processes:
            return
        
        # Create a NEW file for each 2-second interval with precise timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        log_file = os.path.join(self.logs_dir, f"hp_processes_{timestamp}.csv")
        
        # Create new file with header and data
        with open(log_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'pid', 'process_name', 'window_title', 'owner']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for process in processes:
                writer.writerow(process)
        
        # Increment file counter
        self.file_counter += 1
        
        # Update current log file display
        self.current_log_file = log_file
        self.root.after(0, self.update_current_file_display, os.path.basename(log_file))
        self.root.after(0, self.file_count_var.set, f"Files Created: {self.file_counter}")
        
        # Update UI log display
        self.root.after(0, self.update_log_display, processes)

    def update_log_display(self, processes):
        """Update the log display in the UI"""
        for process in processes[-5:]:  # Show only last 5 entries
            log_entry = (f"{process['timestamp']} - PID: {process['pid']}, "
                        f"Name: {process['process_name']}, "
                        f"Title: {process['window_title']}, "
                        f"Owner: {process['owner']}\n")
            self.log_text.insert(tk.END, log_entry)
        
        # Keep only last 20 lines
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 20:
            self.log_text.delete("1.0", f"{len(lines) - 20}.0")
        
        # Auto-scroll to bottom
        self.log_text.see(tk.END)

    def update_current_file_display(self, filename):
        """Update the current log file display"""
        self.log_file_var.set(f"Current File: {filename}")

    def monitor_processes(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                processes = self.get_hp_processes()
                
                if processes:
                    self.log_processes(processes)
                
                # Update process count
                self.root.after(0, self.process_count_var.set, 
                               f"HP Processes Found: {len(processes)}")
                
                # Wait 2 seconds
                time.sleep(2)
                
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(2)

    def start_monitoring(self):
        """Start the monitoring process"""
        if self.monitoring:
            return
        
        # Reset file counter for new session
        self.file_counter = 0
        
        # Update UI
        self.monitoring = True
        self.status_var.set("Status: Monitoring... (Creating new file every 2 seconds)")
        self.log_file_var.set("Current File: Starting...")
        self.file_count_var.set("Files Created: 0")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Clear log display
        self.log_text.delete("1.0", tk.END)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        self.monitor_thread.start()
        
        messagebox.showinfo("Started", "Monitoring started!\nA NEW file will be created every 2 seconds\nuntil you click 'Stop'.")

    def stop_monitoring(self):
        """Stop the monitoring process"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        
        # Update UI
        self.status_var.set("Status: Stopped")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        messagebox.showinfo("Stopped", "Monitoring stopped.")

    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_monitoring()


if __name__ == "__main__":
    app = HPProcessMonitor()
    app.run()
