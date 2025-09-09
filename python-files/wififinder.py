import subprocess
import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import csv
from datetime import datetime

# CMD command runner with unicode safe
def run_cmd(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True, errors='ignore')
        return result
    except subprocess.CalledProcessError as e:
        return e.output

# Fetch all saved Wi-Fi profiles
def get_wifi_profiles():
    result = run_cmd("netsh wlan show profiles")
    profiles = re.findall(r"All User Profile\s*:\s*([^\r\n]+)", result)
    return [wifi.strip() for wifi in profiles]

# Show all Wi-Fi in popup
def show_all_wifi():
    profiles = get_wifi_profiles()
    if profiles:
        wifi_list = "\n".join(profiles)
        messagebox.showinfo("Saved Wi-Fi Networks", wifi_list)
    else:
        messagebox.showwarning("No Wi-Fi", "No saved Wi-Fi profiles found.\nRun app as Administrator if needed.")

# Show password for selected Wi-Fi from dropdown
def show_password():
    wifi_name = wifi_combobox.get()
    if wifi_name:
        result = run_cmd(f'netsh wlan show profile name="{wifi_name}" key=clear')
        password_match = re.search(r"Key Content\s*:\s*(.*)", result)
        password = password_match.group(1).strip() if password_match else "No Password Saved"
        messagebox.showinfo("Wi-Fi Password", f"{wifi_name} → {password}")
    else:
        messagebox.showwarning("Select Wi-Fi", "Please select a Wi-Fi network from the dropdown.")

# Download all Wi-Fi passwords to CSV
def download_all_passwords():
    profiles = get_wifi_profiles()
    if not profiles:
        messagebox.showwarning("No Wi-Fi", "No saved Wi-Fi profiles found.")
        return
    
    all_data = []
    for wifi in profiles:
        result = run_cmd(f'netsh wlan show profile name="{wifi}" key=clear')
        password_match = re.search(r"Key Content\s*:\s*(.*)", result)
        password = password_match.group(1).strip() if password_match else "No Password Saved"
        all_data.append([wifi, password])
    
    filename = f"KiranTech_WiFiPasswords_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Wi-Fi Name (SSID)", "Password"])
            writer.writerows(all_data)
        messagebox.showinfo("Download Complete", f"All Wi-Fi passwords saved to:\n{filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save CSV:\n{str(e)}")

# Close App
def close_app():
    root.destroy()

# ===================== GUI =====================
root = tk.Tk()
root.title("Kiran Tech - Wi-Fi Password Checker")
root.geometry("500x400")
root.resizable(False, False)
root.configure(bg="#1e1e2f")  # Dark background

# Title Label
title_label = tk.Label(root, text="Kiran Tech", font=("Helvetica", 22, "bold"), bg="#1e1e2f", fg="#00ffff")
title_label.pack(pady=10)

subtitle_label = tk.Label(root, text="Wi-Fi Password Checker", font=("Helvetica", 14), bg="#1e1e2f", fg="#ffffff")
subtitle_label.pack(pady=5)

# Show All Wi-Fi Button
btn1 = tk.Button(
    root,
    text="Show All Wi-Fi",
    command=show_all_wifi,
    width=40,
    height=2,
    bg="#3a3a5c",
    fg="#ffffff",
    font=("Arial", 12, "bold"),
    activebackground="#00ffff",
    activeforeground="#000000"
)
btn1.pack(pady=10)

# Dropdown for Wi-Fi selection
wifi_profiles = get_wifi_profiles()
wifi_label = tk.Label(root, text="Select Wi-Fi to Show Password:", font=("Arial", 12), bg="#1e1e2f", fg="#ffffff")
wifi_label.pack(pady=5)

wifi_combobox = ttk.Combobox(root, values=wifi_profiles, width=35, font=("Arial", 11))
wifi_combobox.pack(pady=5)

# Show Password Button
btn2 = tk.Button(
    root,
    text="Show Wi-Fi Password",
    command=show_password,
    width=40,
    height=2,
    bg="#3a5c3a",
    fg="#ffffff",
    font=("Arial", 12, "bold"),
    activebackground="#00ff00",
    activeforeground="#000000"
)
btn2.pack(pady=10)

# Download All Wi-Fi & Passwords Button
btn3 = tk.Button(
    root,
    text="Download All Wi-Fi & Passwords",
    command=download_all_passwords,
    width=40,
    height=2,
    bg="#5c3a3a",
    fg="#ffffff",
    font=("Arial", 12, "bold"),
    activebackground="#ff0000",
    activeforeground="#ffffff"
)
btn3.pack(pady=10)

# Close App Button
btn_close = tk.Button(
    root,
    text="Close App",
    command=close_app,
    width=40,
    height=2,
    bg="#888888",
    fg="#000000",
    font=("Arial", 12, "bold"),
    activebackground="#cccccc",
    activeforeground="#000000"
)
btn_close.pack(pady=10)

root.mainloop()
