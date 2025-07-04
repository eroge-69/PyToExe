# -*- coding: utf-8 -*-

import os
import webbrowser
import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from winreg import *
import ctypes
import sys
import tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class PcHelper(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pc Helper")
        self.geometry("900x600")
        self.resizable(False, False)

        self.configure(bg="#000000")

        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=10, fg_color="#000000")
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="Pc Helper",
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        self.logo_label.pack(pady=(20, 10))
        self.logo_label.configure(fg_color="#000000")

        self.footer_label = ctk.CTkLabel(self.sidebar, text="Made by deathmane", font=("Arial", 12, "italic"), text_color="white")
        self.footer_label.pack(pady=(10, 10))

        # Define interactive glowing button style
        button_style = {
            "text_color": "white",
            "fg_color": "#1a1a1a",
            "hover_color": "#888888",
            "border_width": 2,
            "border_color": "#ffffff"
        }

        self.btn_file_clean = ctk.CTkButton(self.sidebar, text="Clean Files", command=self.clean_files, **button_style)
        self.btn_file_clean.pack(pady=10, fill="x")

        self.btn_browser_history = ctk.CTkButton(self.sidebar, text="Clear Browser History", command=self.clear_browser_history, **button_style)
        self.btn_browser_history.pack(pady=10, fill="x")

        self.btn_registry = ctk.CTkButton(self.sidebar, text="Clean Registry", command=self.clean_registry, **button_style)
        self.btn_registry.pack(pady=10, fill="x")

        self.btn_downloads = ctk.CTkButton(self.sidebar, text="Clear Downloads", command=self.clear_downloads, **button_style)
        self.btn_downloads.pack(pady=10, fill="x")

        self.btn_scan_only = ctk.CTkButton(self.sidebar, text="Scan System", command=self.scan_system, **button_style)
        self.btn_scan_only.pack(pady=10, fill="x")

        self.btn_delete_selected = ctk.CTkButton(self.sidebar, text="Delete Selected", command=self.delete_selected, **button_style)
        self.btn_delete_selected.pack(pady=10, fill="x")

        # Main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#000000")
        self.main_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Status Output:", font=("Arial", 16), text_color="white")
        self.status_label.pack(pady=(20, 10), anchor="w", padx=20)

        self.output_box = ctk.CTkTextbox(self.main_frame, width=600, height=300, corner_radius=10)
        self.output_box.pack(padx=20, pady=10, fill="x")
        self.output_box.configure(font=("Courier New", 12), text_color="white", fg_color="#1a1a1a")

        self.checkbox_frame = ctk.CTkScrollableFrame(self.main_frame, width=600, height=200, fg_color="#000000")
        self.checkbox_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.check_vars = []
        self.found_files = []

    def log(self, message):
        self.output_box.insert("end", f"{message}\n")
        self.output_box.see("end")

    def clean_files(self):
        targets = [
            os.path.expanduser("~\\AppData\\Local\\Temp"),
            os.path.expanduser("~\\Downloads"),
        ]
        keywords = [
            "cheat", "injector", "aimbot", ".dll", "esp", "client", "loader",
            "serial checker", "temp-woofer", "dllhost", "k9839", "scoped_dir", "mttrdx"
        ]
        deleted = 0

        for path in targets:
            if os.path.exists(path):
                for file in os.listdir(path):
                    file_lower = file.lower()
                    for keyword in keywords:
                        if keyword in file_lower:
                            try:
                                os.remove(os.path.join(path, file))
                                self.log(f"Deleted: {file}")
                                deleted += 1
                            except:
                                self.log(f"Failed to delete: {file}")

        self.log(f"Finished. {deleted} file(s) deleted.")

    def clear_browser_history(self):
        ...  # Code unchanged

    def clean_registry(self):
        keys_to_check = [
            (HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
            (HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU"),
            (HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\OpenSavePidlMRU"),
            (HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\LastVisitedPidlMRU"),
            (HKEY_CURRENT_USER, r"Software\\Microsoft\\Internet Explorer\\Download"),
            (HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\LastVisitedPidlMRULegacy"),
            (HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\OpenSaveMRU")
        ]
        deleted = 0

        for root, subkey in keys_to_check:
            try:
                with OpenKey(root, subkey, 0, KEY_ALL_ACCESS) as key:
                    i = 0
                    while True:
                        try:
                            value = EnumValue(key, i)
                            name, data = value[0], value[1]
                            if isinstance(data, str):
                                if any(k in data.lower() for k in ["cheat", "inject", "aim", "setup", "loader", "crack"]):
                                    DeleteValue(key, name)
                                    self.log(f"Deleted registry value: {subkey}\\{name}")
                                    deleted += 1
                                else:
                                    i += 1
                            else:
                                i += 1
                        except WindowsError:
                            break
            except Exception as e:
                self.log(f"Error accessing registry key {subkey}: {e}")

        self.log(f"Finished. {deleted} registry entries deleted.")

    def clear_downloads(self):
        ...  # Code unchanged

    def scan_system(self):
        self.checkbox_frame.destroy()
        self.checkbox_frame = ctk.CTkScrollableFrame(self.main_frame, width=600, height=200, fg_color="#000000")
        self.checkbox_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.check_vars = []
        self.found_files = []
        keywords = [
            "cheat", "injector", "aimbot", ".dll", "esp", "client", "loader",
            "serial checker", "temp-woofer", "dllhost", "k9839", "scoped_dir", "mttrdx"
        ]

        for root, dirs, files in os.walk("C:\\"):
            for file in files:
                file_lower = file.lower()
                for keyword in keywords:
                    if keyword in file_lower:
                        full_path = os.path.join(root, file)
                        var = ctk.BooleanVar()
                        ctk.CTkCheckBox(self.checkbox_frame, text=full_path, variable=var, text_color="white", fg_color="#1a1a1a", hover_color="#333333").pack(anchor="w")
                        self.check_vars.append((var, full_path))

        self.log("Scan complete. Select files to delete.")

    def delete_selected(self):
        ...  # Code unchanged

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        script = os.path.abspath(__file__)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
    else:
        msg_root = tk.Tk()
        msg_root.withdraw()
        consent = messagebox.askyesno("Permission Required", "This program requires full access to your PC to function properly. Do you agree?")
        msg_root.destroy()

        if consent:
            app = PcHelper()
            app.mainloop()
        else:
            sys.exit()
