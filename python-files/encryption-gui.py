import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkcalendar import Calendar
from cryptography.fernet import Fernet
import json
import os
import datetime
import sys

# === SAME KEY as your service script ===
FERNET_KEY = b'K9rq_DvwPLvpevjmE_mdGxG7cq0h6HSU8pqukpljI7g='
fernet = Fernet(FERNET_KEY)

# Determine base path for exe or script
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

def generate_config():
    try:
        logging_enabled = logging_var.get()
        monitoring_enabled = monitoring_var.get()
        raw_date_str = date_var.get()
        if not raw_date_str:
            messagebox.showwarning("Validation", "⚠️ Please select an expiration date.")
            return
        raw_date = datetime.datetime.strptime(raw_date_str, "%Y-%m-%d").date()
        expiration_date = raw_date.strftime("%Y-%m-%d") + "T12:00:00"
        services = [services_listbox.get(i) for i in range(services_listbox.size())]

        if not services:
            messagebox.showwarning("Validation", "⚠️ You must add at least one service.")
            return
        if raw_date < datetime.date.today():
            messagebox.showwarning("Validation", "⚠️ Expiration date cannot be in the past.")
            return

        config = {
            "LoggingEnabled": logging_enabled,
            "MonitoringEnabled": monitoring_enabled,
            "ExpirationDate": expiration_date,
            "ServicesToMonitor": services
        }

        # Use safe default folder
        user_docs = os.path.expanduser("~/Documents")
        output_file = filedialog.asksaveasfilename(
            initialfile="config.json.enc",
            defaultextension=".json.enc",
            filetypes=[("Encrypted JSON", "*.json.enc")],
            initialdir=user_docs
        )
        if not output_file:
            return

        status_var.set("Encrypting...")
        root.update()

        encrypted_data = fernet.encrypt(json.dumps(config).encode())
        with open(output_file, "wb") as f:
            f.write(encrypted_data)

        status_var.set("✅ Done")
        messagebox.showinfo("Success", f"Encrypted config written to:\n{output_file}")
    except Exception as e:
        status_var.set("❌ Error")
        messagebox.showerror("Error", f"Failed: {str(e)}")

def add_service():
    service_name = simpledialog.askstring("Add Service", "Enter Windows Service name:")
    if service_name:
        services_listbox.insert(tk.END, service_name.strip())

def remove_service():
    selected = services_listbox.curselection()
    for index in reversed(selected):
        services_listbox.delete(index)

def pick_date():
    def on_select():
        selected = cal.selection_get()
        date_var.set(selected.strftime("%Y-%m-%d"))
        top.destroy()

    top = tk.Toplevel(root)
    top.grab_set()  # make popup modal
    cal = Calendar(top, selectmode='day', year=datetime.date.today().year,
                   month=datetime.date.today().month, day=datetime.date.today().day)
    cal.pack(padx=10, pady=10)
    tk.Button(top, text="Select", command=on_select).pack(pady=5)

# === GUI ===
root = tk.Tk()
root.title("SAP Config Encryptor")
root.geometry("500x600")
root.resizable(False, False)

# Correct icon path for exe or script
icon_path = os.path.join(base_path, "service_icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

tk.Label(root, text="🔐 SAP Config Encryptor", font=("Arial", 16, "bold")).pack(pady=10)

logging_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Enable Logging (writes log file)", variable=logging_var).pack(anchor="w", padx=20, pady=5)

monitoring_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Enable Monitoring (check SAP services)", variable=monitoring_var).pack(anchor="w", padx=20, pady=5)

# Expiration Date Picker
tk.Label(root, text="Expiration Date:").pack(anchor="w", padx=20, pady=(15,0))
date_var = tk.StringVar()
date_frame = tk.Frame(root)
date_frame.pack(padx=20, pady=5, fill="x")
tk.Entry(date_frame, textvariable=date_var, state="readonly").pack(side="left", fill="x", expand=True)
tk.Button(date_frame, text="Pick Date", command=pick_date, bg="#2196F3", fg="white").pack(side="left", padx=5)

# Services input
tk.Label(root, text="Services to Monitor:").pack(anchor="w", padx=20, pady=(15,0))
services_frame = tk.Frame(root, bd=1, relief=tk.SUNKEN)
services_frame.pack(padx=20, pady=5, fill="both", expand=False)

services_listbox = tk.Listbox(services_frame, height=10, width=50, selectmode=tk.MULTIPLE)
services_listbox.pack(side=tk.LEFT, fill="both", expand=True)

scrollbar = tk.Scrollbar(services_frame)
scrollbar.pack(side=tk.RIGHT, fill="y")
services_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=services_listbox.yview)

default_services = ["B1ServerTools64", "B1ServerToolsAuthentication"]
for svc in default_services:
    services_listbox.insert(tk.END, svc)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)
tk.Button(btn_frame, text="➕ Add Service", command=add_service, bg="#2196F3", fg="white").grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="➖ Remove Service", command=remove_service, bg="#f44336", fg="white").grid(row=0, column=1, padx=5)

tk.Button(root, text="Generate Encrypted Config", command=generate_config, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).pack(pady=20)

status_var = tk.StringVar(value="Ready ✅")
status_label = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor="w")
status_label.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
