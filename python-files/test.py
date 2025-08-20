import os
import sys
import subprocess
import tkinter as tk
from tkinter import Listbox, StringVar, END, SINGLE
import threading
import time
import ctypes
from ctypes import wintypes

# Windows constants for Start Menu paths
CSIDL_STARTMENU = 0x0b
CSIDL_COMMON_STARTMENU = 0x16

# Use SHGetFolderPath to get Start Menu folders
def get_start_menu_paths():
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_STARTMENU, None, 0, buf)
    start_menu = buf.value
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_COMMON_STARTMENU, None, 0, buf)
    common_start_menu = buf.value
    return [start_menu, common_start_menu]

# Find all .lnk shortcuts in Start Menu folders
def find_shortcuts():
    shortcuts = []
    for base in get_start_menu_paths():
        for root, _, files in os.walk(base):
            for file in files:
                if file.lower().endswith('.lnk'):
                    full_path = os.path.join(root, file)
                    shortcuts.append(full_path)
    return shortcuts

# Resolve .lnk shortcut target using COM
def resolve_shortcut(path):
    import pythoncom
    from win32com.shell import shell, shellcon

    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None,
                                          pythoncom.CLSCTX_INPROC_SERVER,
                                          shell.IID_IShellLink)
    persist_file = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
    persist_file.Load(path)
    return shortcut.GetPath(shell.SLGP_UNCPRIORITY)[0]

# Launch the resolved path
def launch_target(path):
    try:
        subprocess.Popen(path)
    except Exception as e:
        print("Failed to launch:", e)

# GUI app
class PowerRun(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PowerRun")
        self.geometry("400x300")
        self.resizable(False, False)

        self.shortcuts = find_shortcuts()
        self.names = [os.path.splitext(os.path.basename(s))[0] for s in self.shortcuts]

        self.var = StringVar()
        self.var.trace("w", self.update_list)

        self.entry = tk.Entry(self, textvariable=self.var, font=("Segoe UI", 14))
        self.entry.pack(fill="x", padx=10, pady=10)
        self.entry.focus()

        self.listbox = Listbox(self, font=("Segoe UI", 12), selectmode=SINGLE)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.listbox.bind("<Double-Button-1>", self.on_launch)
        self.listbox.bind("<Return>", self.on_launch)

        self.update_list()

    def update_list(self, *args):
        query = self.var.get().lower()
        self.listbox.delete(0, END)
        for i, name in enumerate(self.names):
            if query in name.lower():
                self.listbox.insert(END, name)

    def on_launch(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        selected_name = self.listbox.get(selection[0])
        # Find shortcut full path
        try:
            idx = self.names.index(selected_name)
        except ValueError:
            return
        shortcut_path = self.shortcuts[idx]
        try:
            target = resolve_shortcut(shortcut_path)
            if target:
                launch_target(target)
                self.destroy()
        except Exception as e:
            print("Error resolving or launching:", e)

if __name__ == "__main__":
    # COM initialization needed for pywin32
    try:
        import pythoncom
        pythoncom.CoInitialize()
    except ImportError:
        print("pywin32 is required to run this script (for shortcut resolution).")
        sys.exit(1)

    app = PowerRun()
    app.mainloop()
