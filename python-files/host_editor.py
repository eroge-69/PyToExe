
# Save this as host_editor.py
import os
import sys
import tkinter as tk
from tkinter import messagebox

class HostEntry:
    def __init__(self, master, row, ip='', domain='', enabled=True):
        self.var_ip = tk.StringVar(value=ip)
        self.var_domain = tk.StringVar(value=domain)
        self.var_enabled = tk.BooleanVar(value=enabled)

        self.ip_entry = tk.Entry(master, textvariable=self.var_ip, width=15)
        self.domain_entry = tk.Entry(master, textvariable=self.var_domain, width=30)
        self.toggle = tk.Checkbutton(master, variable=self.var_enabled)
        self.remove_button = tk.Button(master, text="Remove", command=self.remove)

        self.ip_entry.grid(row=row, column=0, padx=2, pady=2)
        self.domain_entry.grid(row=row, column=1, padx=2, pady=2)
        self.toggle.grid(row=row, column=2, padx=2, pady=2)
        self.remove_button.grid(row=row, column=3, padx=2, pady=2)

        self.master = master
        self.row = row

    def remove(self):
        self.ip_entry.destroy()
        self.domain_entry.destroy()
        self.toggle.destroy()
        self.remove_button.destroy()
        app.entries.remove(self)
        app.refresh_rows()

    def get_data(self):
        return (self.var_ip.get(), self.var_domain.get(), self.var_enabled.get())

class HostEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hosts File Editor")
        self.entries = []

        # Header
        tk.Label(root, text="IP Address").grid(row=0, column=0)
        tk.Label(root, text="Domain").grid(row=0, column=1)
        tk.Label(root, text="On/Off").grid(row=0, column=2)

        # Buttons
        tk.Button(root, text="Add Entry", command=self.add_entry).grid(row=999, column=0, pady=10)
        tk.Button(root, text="Apply Changes", command=self.apply_changes).grid(row=999, column=1, pady=10)
        tk.Button(root, text="Exit", command=root.quit).grid(row=999, column=2, pady=10)

        # Load existing
        self.hosts_path = self.get_hosts_file_path()
        self.original_lines = self.read_hosts_file()
        self.load_entries()

    def get_hosts_file_path(self):
        if os.name == 'nt':
            return r"C:\Windows\System32\drivers\etc\hosts"
        else:
            return "/etc/hosts"

    def read_hosts_file(self):
        try:
            with open(self.hosts_path, 'r') as file:
                return file.readlines()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read hosts file: {e}")
            return []

    def load_entries(self):
        for line in self.original_lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                ip, domain = parts[0], parts[1]
                self.add_entry(ip, domain, True)

    def add_entry(self, ip='', domain='', enabled=True):
        row = len(self.entries) + 1
        entry = HostEntry(self.root, row, ip, domain, enabled)
        self.entries.append(entry)

    def refresh_rows(self):
        for i, entry in enumerate(self.entries, start=1):
            entry.ip_entry.grid(row=i, column=0)
            entry.domain_entry.grid(row=i, column=1)
            entry.toggle.grid(row=i, column=2)
            entry.remove_button.grid(row=i, column=3)

    def apply_changes(self):
        try:
            new_lines = []
            for line in self.original_lines:
                if not any(domain in line for _, domain, _ in [e.get_data() for e in self.entries]):
                    new_lines.append(line)

            for ip, domain, enabled in self.entries:
                if enabled and ip and domain:
                    new_lines.append(f"{ip} {domain}\n")

            with open(self.hosts_path, 'w') as file:
                file.writelines(new_lines)

            messagebox.showinfo("Success", "Hosts file updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write hosts file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HostEditorApp(root)
    root.mainloop()
