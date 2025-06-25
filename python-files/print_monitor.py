import tkinter as tk
from tkinter import simpledialog, messagebox
import win32print
import win32event
import win32con
import threading
import os
import json

CONFIG_FILE = "config.json"
ID_WHITELIST_FILE = "allowed_ids.txt"
PRINT_LIMIT = 100

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"count": 0}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_allowed_ids():
    if not os.path.exists(ID_WHITELIST_FILE):
        return []
    with open(ID_WHITELIST_FILE, "r") as f:
        return [line.strip() for line in f if line.strip().isdigit() and len(line.strip()) == 9]

def prompt_for_id():
    root = tk.Tk()
    root.withdraw()
    user_id = simpledialog.askstring("Authentication", "Enter your ID number to print:")
    root.destroy()
    return user_id

def monitor_print_jobs():
    printer_name = win32print.GetDefaultPrinter()
    printer_handle = win32print.OpenPrinter(printer_name)

    printer_change_handle = win32print.FindFirstPrinterChangeNotification(
        printer_handle, win32print.PRINTER_CHANGE_JOB, 0, None
    )

    config = load_config()

    while True:
        win32event.WaitForSingleObject(printer_change_handle, win32con.INFINITE)
        job_info = win32print.EnumJobs(printer_handle, 0, 1, 1)

        if job_info:
            if config["count"] >= PRINT_LIMIT:
                win32print.SetJob(printer_handle, job_info[0]["JobId"], 0, None, win32print.JOB_CONTROL_DELETE)
                messagebox.showwarning("Print Limit Reached", "You have reached the print limit.")
                continue

            allowed_ids = load_allowed_ids()
            user_id = prompt_for_id()

            if user_id and user_id in allowed_ids:
                config["count"] += 1
                save_config(config)
            else:
                win32print.SetJob(printer_handle, job_info[0]["JobId"], 0, None, win32print.JOB_CONTROL_DELETE)
                messagebox.showerror("Unauthorized ID", "This ID is not authorized to print.")

threading.Thread(target=monitor_print_jobs, daemon=True).start()
tk.Tk().mainloop()
