import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import hashlib
import os
import ctypes
import sys

# ---------------- Configuration ----------------
PASSWORD_HASH = hashlib.sha256("01716848450".encode()).hexdigest()
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
APP_TITLE = "PROTECTIONSERVER"
ICON_FILE = "logo.ico"  # Convert your logo.png to logo.ico
# ------------------------------------------------

# Ensure script runs as admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def require_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

# Password verification
def verify_password():
    input_pw = simpledialog.askstring("Password Required", "Enter Password:", show='*')
    if input_pw:
        return hashlib.sha256(input_pw.encode()).hexdigest() == PASSWORD_HASH
    return False

# Manage Hosts File
def block_domain(domain):
    with open(HOSTS_PATH, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.writelines(lines)
        if any(domain in line for line in lines):
            messagebox.showinfo("Info", f"{domain} already blocked.")
        else:
            f.write(f"{REDIRECT_IP} {domain}\n")
            messagebox.showinfo("Blocked", f"{domain} has been blocked.")

def unblock_domain(domain):
    with open(HOSTS_PATH, 'r') as f:
        lines = f.readlines()
    with open(HOSTS_PATH, 'w') as f:
        for line in lines:
            if domain not in line:
                f.write(line)
    messagebox.showinfo("Unblocked", f"{domain} has been unblocked.")

# GUI Setup
class ProtectionServerApp:
    def __init__(self, master):
        self.master = master
        master.title(APP_TITLE)
        if os.path.exists(ICON_FILE):
            master.iconbitmap(ICON_FILE)
        
        self.label = tk.Label(master, text="Blocked Domains", font=("Arial", 14))
        self.label.pack()

        self.domain_listbox = tk.Listbox(master, width=50)
        self.domain_listbox.pack(pady=10)
        self.load_domains()

        self.add_button = tk.Button(master, text="Add Domain", command=self.add_domain)
        self.add_button.pack(pady=5)

        self.remove_button = tk.Button(master, text="Remove Domain", command=self.remove_domain)
        self.remove_button.pack(pady=5)

        self.uninstall_button = tk.Button(master, text="Uninstall ProtectionServer", command=self.uninstall)
        self.uninstall_button.pack(pady=20)

    def load_domains(self):
        self.domain_listbox.delete(0, tk.END)
        with open(HOSTS_PATH, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if REDIRECT_IP in line:
                domain = line.strip().split()[-1]
                self.domain_listbox.insert(tk.END, domain)

    def add_domain(self):
        domain = simpledialog.askstring("Add Domain", "Enter domain to block:")
        if domain:
            block_domain(domain)
            self.load_domains()

    def remove_domain(self):
        selected = self.domain_listbox.curselection()
        if selected:
            domain = self.domain_listbox.get(selected)
            unblock_domain(domain)
            self.load_domains()
        else:
            messagebox.showwarning("Warning", "Select a domain to remove.")

    def uninstall(self):
        if verify_password():
            with open(HOSTS_PATH, 'r') as f:
                lines = f.readlines()
            with open(HOSTS_PATH, 'w') as f:
                for line in lines:
                    if REDIRECT_IP not in line:
                        f.write(line)
            messagebox.showinfo("Uninstalled", "PROTECTIONSERVER has been uninstalled.")
            self.master.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect password.")


# Main Run
if __name__ == "__main__":
    require_admin()
    if not verify_password():
        messagebox.showerror("Access Denied", "Incorrect password.")
        sys.exit()

    root = tk.Tk()
    app = ProtectionServerApp(root)
    root.mainloop()
