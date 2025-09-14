import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import random
import string
import json
import os

# File to save licenses
LICENSE_FILE = "licenses.json"

# Load existing licenses
if os.path.exists(LICENSE_FILE):
    with open(LICENSE_FILE, "r") as f:
        licenses = json.load(f)
else:
    licenses = {}

# Function to generate random license key
def generate_license(length=16):
    chars = string.ascii_uppercase + string.digits
    return '-'.join(''.join(random.choices(chars, k=4)) for _ in range(length // 4))

# Function to save license
def save_license():
    user = entry_user.get().strip()
    days = entry_days.get().strip()

    if not user or not days.isdigit():
        messagebox.showerror("Error", "Please enter valid username and expiry days.")
        return

    expiry_date = (datetime.now() + timedelta(days=int(days))).strftime("%Y-%m-%d")
    license_key = generate_license()
    
    licenses[license_key] = {"user": user, "expiry": expiry_date}
    
    with open(LICENSE_FILE, "w") as f:
        json.dump(licenses, f, indent=4)
    
    messagebox.showinfo("License Generated", f"License Key: {license_key}\nExpires: {expiry_date}")
    entry_user.delete(0, tk.END)
    entry_days.delete(0, tk.END)

# GUI setup
root = tk.Tk()
root.title("Offline License Key Generator")
root.geometry("400x200")

tk.Label(root, text="Username:").pack(pady=5)
entry_user = tk.Entry(root, width=30)
entry_user.pack(pady=5)

tk.Label(root, text="Expiry Days:").pack(pady=5)
entry_days = tk.Entry(root, width=30)
entry_days.pack(pady=5)

tk.Button(root, text="Generate License", command=save_license, bg="green", fg="white").pack(pady=20)

root.mainloop()
