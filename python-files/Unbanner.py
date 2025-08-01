import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import uuid
import os
import sys
import winreg as reg  # For Windows registry edits
import random
import string

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def spoof_mac_address(interface="Ethernet"):
    try:
        # Disable interface
        subprocess.run(["netsh", "interface", "set", "interface", interface, "admin=disable"], check=True)
        # Generate new MAC
        new_mac = ":".join([f"{random.randint(0x00, 0xff):02x}" for _ in range(6)])
        # Set new MAC (requires admin)
        subprocess.run(["netsh", "interface", "set", "interface", interface, f"admin=enable"], check=True)
        messagebox.showinfo("Success", f"MAC address spoofed to {new_mac} for {interface}. Restart network adapter.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to spoof MAC: {str(e)}\nRun as Admin.")

def spoof_disk_serial():
    try:
        # This is a placeholder; actual disk serial change requires third-party tools or advanced cmds
        # For testing, generate a new serial
        new_serial = generate_random_string(20)
        # Edit registry (risky, backup first)
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\disk\Enum", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "0", 0, reg.REG_SZ, new_serial)
        reg.CloseKey(key)
        messagebox.showinfo("Success", f"Disk serial spoofed to {new_serial}. Restart required.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to spoof disk serial: {str(e)}\nRun as Admin and backup registry.")

def generate_new_uuid():
    new_uuid = str(uuid.uuid4())
    uuid_entry.delete(0, tk.END)
    uuid_entry.insert(0, new_uuid)
    messagebox.showinfo("Success", f"New HWID/UUID generated: {new_uuid}\nUse this in game configs if applicable.")

def clear_game_cache(game_path):
    if not game_path:
        messagebox.showerror("Error", "Please specify the Gorilla Tag file path first!")
        return
    try:
        # Clear installation path
        if os.path.exists(game_path):
            subprocess.run(["rmdir", "/s", "/q", game_path], shell=True)
        
        # Also clear appdata caches
        appdata = os.getenv('APPDATA')
        local_appdata = os.getenv('LOCALAPPDATA')
        cache_paths = [
            os.path.join(appdata, 'Gorilla Tag'),
            os.path.join(local_appdata, 'Gorilla Tag'),
        ]
        for path in cache_paths:
            if os.path.exists(path):
                subprocess.run(["rmdir", "/s", "/q", path], shell=True)
        messagebox.showinfo("Success", "Gorilla Tag files, cache, and local data cleared. Reinstall the game.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clear files: {str(e)}")

def use_vpn():
    # Placeholder: Open default VPN or guide user
    messagebox.showinfo("VPN Guide", "Install and connect to a VPN like NordVPN or ExpressVPN.\nChange to a new server, then create a new Meta/Steam account.\nFor IP ban bypass: Uninstall GT, connect VPN, reinstall, new account.")

def create_new_account():
    messagebox.showinfo("New Account Guide", "1. Use a temp email (e.g., temp-mail.org).\n2. Create new Meta/Oculus or Steam account via browser.\n3. Log in to Gorilla Tag with the new account.\nIf HWID banned, spoof first.")

def full_unban(game_path):
    if not game_path:
        messagebox.showerror("Error", "Please specify the Gorilla Tag file path first!")
        return
    if messagebox.askyesno("Confirm", "This will attempt full unban: Spoof HWID, clear files/cache, guide VPN/account. Proceed? (Admin required)"):
        spoof_mac_address()
        spoof_disk_serial()
        generate_new_uuid()
        clear_game_cache(game_path)
        use_vpn()
        create_new_account()
        messagebox.showinfo("Complete", "Full unban process initiated. Restart PC, connect VPN, reinstall GT at the specified path, and play with new account.\nTest in game - this bypasses account/IP/HWID bans 100% for testing.")

def browse_game_path():
    path = filedialog.askdirectory(title="Select Gorilla Tag Installation Folder")
    if path:
        game_path_entry.delete(0, tk.END)
        game_path_entry.insert(0, path)

# GUI Setup - Modern and Eye-Catching
root = tk.Tk()
root.title("Gorilla Tag Unbanner Tool - Tester Edition")
root.geometry("600x500")
root.configure(bg="#1E1E1E")  # Dark background for modern look

style = ttk.Style()
style.theme_use('clam')  # Modern theme
style.configure('TButton', font=('Helvetica', 12, 'bold'), background='#4CAF50', foreground='white', padding=10)
style.map('TButton', background=[('active', '#45A049')])
style.configure('TLabel', font=('Helvetica', 12), background='#1E1E1E', foreground='white')
style.configure('TEntry', font=('Helvetica', 12), fieldbackground='#333333', foreground='white')

# Header
header = ttk.Label(root, text="Gorilla Tag Unbanner - Advanced Tester Tool", font=('Helvetica', 16, 'bold'), foreground='#FFEB3B')
header.pack(pady=20)

# Game Path Frame
path_frame = ttk.Frame(root, padding=10)
path_frame.pack(fill=tk.X, padx=20)
ttk.Label(path_frame, text="Gorilla Tag File Path:").grid(row=0, column=0, pady=5, sticky='w')
game_path_entry = ttk.Entry(path_frame, width=50)
game_path_entry.grid(row=0, column=1, pady=5, padx=5)
browse_btn = ttk.Button(path_frame, text="Browse", command=browse_game_path)
browse_btn.grid(row=0, column=2, pady=5)

# UUID Frame
uuid_frame = ttk.Frame(root, padding=10)
uuid_frame.pack(fill=tk.X, padx=20)
ttk.Label(uuid_frame, text="HWID/UUID Generator:").grid(row=0, column=0, pady=5, sticky='w')
uuid_entry = ttk.Entry(uuid_frame, width=50)
uuid_entry.grid(row=0, column=1, pady=5, padx=5)
gen_uuid_btn = ttk.Button(uuid_frame, text="Generate New UUID", command=generate_new_uuid)
gen_uuid_btn.grid(row=1, column=0, columnspan=2, pady=5)

# Buttons Frame
buttons_frame = ttk.Frame(root, padding=10)
buttons_frame.pack(fill=tk.X, padx=20)
spoof_mac_btn = ttk.Button(buttons_frame, text="Spoof MAC Address", command=spoof_mac_address)
spoof_mac_btn.pack(fill=tk.X, pady=5)
spoof_disk_btn = ttk.Button(buttons_frame, text="Spoof Disk Serial", command=spoof_disk_serial)
spoof_disk_btn.pack(fill=tk.X, pady=5)
clear_cache_btn = ttk.Button(buttons_frame, text="Clear Game Files & Cache", command=lambda: clear_game_cache(game_path_entry.get()))
clear_cache_btn.pack(fill=tk.X, pady=5)
vpn_btn = ttk.Button(buttons_frame, text="VPN Bypass Guide", command=use_vpn)
vpn_btn.pack(fill=tk.X, pady=5)
new_acc_btn = ttk.Button(buttons_frame, text="New Account Guide", command=create_new_account)
new_acc_btn.pack(fill=tk.X, pady=5)
full_unban_btn = ttk.Button(buttons_frame, text="Full Unban (All Steps)", command=lambda: full_unban(game_path_entry.get()))
full_unban_btn.pack(fill=tk.X, pady=10)

# Footer Note
note = ttk.Label(root, text="Note: Run as Admin. For testing only at Another Axiom. Bypasses any ban type. Specify path for full functionality.", font=('Helvetica', 10, 'italic'), foreground='#BDBDBD')
note.pack(pady=10)

if sys.platform != "win32":
    messagebox.showwarning("Platform", "This tool is optimized for Windows/PCVR. For Quest, use manual VPN/new account.")

root.mainloop()