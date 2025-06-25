import os
import re
import json
import tkinter as tk
from tkinter import simpledialog, messagebox
import win32print
import win32api
import win32con
import win32job
import win32event
import threading
from datetime import datetime

# Constants
ALLOWED_IDS_FILE = "allowed_ids.txt"
CONFIG_FILE = "config.json"
MAX_PRINTS = 100

class PrintController:
    def __init__(self):
        self.load_allowed_ids()
        self.load_config()
        self.setup_gui()
        
    def load_allowed_ids(self):
        """Load allowed IDs from file"""
        self.allowed_ids = set()
        if os.path.exists(ALLOWED_IDS_FILE):
            with open(ALLOWED_IDS_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and line.isdigit() and len(line) == 9:
                        self.allowed_ids.add(line)
    
    def load_config(self):
        """Load or create config file"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {"count": 0}
            self.save_config()
    
    def save_config(self):
        """Save config to file"""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)
    
    def is_valid_id(self, id_num):
        """Validate Israeli ID number"""
        return id_num in self.allowed_ids
    
    def increment_print_count(self):
        """Increment and save print count"""
        self.config["count"] += 1
        self.save_config()
    
    def has_reached_limit(self):
        """Check if print limit reached"""
        return self.config["count"] >= MAX_PRINTS
    
    def show_id_prompt(self):
        """Show dialog to enter ID"""
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        id_num = simpledialog.askstring("Print Authorization", 
                                       "Enter your 9-digit Israeli ID number:", 
                                       parent=root)
        root.destroy()
        return id_num
    
    def show_error(self, message):
        """Show error message"""
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Print Error", message)
        root.destroy()
    
    def show_info(self, message):
        """Show info message"""
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Print Info", message)
        root.destroy()
    
    def setup_gui(self):
        """Setup system tray icon (minimized)"""
        # Minimal GUI - runs in background
        pass
    
    def monitor_print_jobs(self):
        """Monitor and control print jobs"""
        printer_name = win32print.GetDefaultPrinter()
        hprinter = win32print.OpenPrinter(printer_name)
        
        try:
            while True:
                # Check print jobs
                jobs = win32print.EnumJobs(hprinter, 0, -1, 1)
                if jobs:
                    job_id = jobs[0]["JobId"]
                    job_info = win32print.GetJob(hprinter, job_id)
                    
                    # Check if we've already processed this job
                    if not job_info.get("pStatus", 0) == win32print.JOB_STATUS_USER_INTERVENTION:
                        if self.has_reached_limit():
                            win32print.SetJob(hprinter, job_id, 0, None, win32print.JOB_CONTROL_CANCEL)
                            self.show_error("You have reached the print limit.")
                            continue
                        
                        # Pause the job for authorization
                        win32print.SetJob(hprinter, job_id, 0, None, win32print.JOB_CONTROL_PAUSE)
                        
                        # Ask for ID
                        id_num = self.show_id_prompt()
                        
                        if id_num and len(id_num) == 9 and id_num.isdigit():
                            if self.is_valid_id(id_num):
                                # Resume job
                                win32print.SetJob(hprinter, job_id, 0, None, win32print.JOB_CONTROL_RESUME)
                                self.increment_print_count()
                                self.show_info(f"Print job authorized. Total prints: {self.config['count']}/{MAX_PRINTS}")
                            else:
                                win32print.SetJob(hprinter, job_id, 0, None, win32print.JOB_CONTROL_CANCEL)
                                self.show_error("Invalid ID number. Print job canceled.")
                        else:
                            win32print.SetJob(hprinter, job_id, 0, None, win32print.JOB_CONTROL_CANCEL)
                            self.show_error("Invalid ID format. Must be 9 digits. Print job canceled.")
                
                # Wait before checking again
                win32event.WaitForSingleObject(win32event.CreateEvent(None, False, False, None), 5000)
        
        finally:
            win32print.ClosePrinter(hprinter)

def main():
    controller = PrintController()
    controller.monitor_print_jobs()

if __name__ == "__main__":
    # Run in a separate thread to allow for GUI operations
    threading.Thread(target=main, daemon=True).start()
    
    # Keep the program running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Print controller exiting...")