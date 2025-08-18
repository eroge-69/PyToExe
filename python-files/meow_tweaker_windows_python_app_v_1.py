# MeowTweaker 🐾 — Windows Tweaks via Python Registry Edits
# -----------------------------------------------------------
# Requirements:
#   • Python 3.9+ on Windows 10/11
#   • Run as Administrator (the script will auto‑elevate if needed)
#   • tkinter (bundled with Python on Windows)
#
# Features:
#   ✔ Restore classic (old) right‑click context menu on Windows 11
#   ✔ Show file extensions
#   ✔ Show hidden files
#   ✔ Show protected operating system files
#   ✔ Align taskbar to the left (Windows 11)
#   ✔ Restart Explorer to apply changes
#   ✔ Read current state from registry on launch
#
# Notes:
#   • Most tweaks are in HKCU (per‑user), but we still elevate to be safe and future‑proof.
#   • Classic context menu tweak creates a CLSID key with empty InprocServer32 default value.
#   • Reverting removes that key. Explorer restart is needed for immediate effect.

import sys
import os
import ctypes
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from contextlib import suppress
try:
    import winreg
except ImportError:
    winreg = None

APP_TITLE = "MeowTweaker 🐾"
CLASSIC_CTXT_GUID = "{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
CLASSIC_CTXT_KEY = rf"Software\\Classes\\CLSID\\{CLASSIC_CTXT_GUID}\\InprocServer32"
EXPLORER_ADVANCED = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"

# --------------- Admin & OS checks ---------------
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def relaunch_as_admin():
    # Relaunch the current Python executable with admin rights
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    except Exception as e:
        messagebox.showerror(APP_TITLE, f"Failed to elevate: {e}")
    sys.exit(0)

# --------------- Registry helpers ---------------

def reg_open_or_create(root, subkey):
    try:
        return winreg.CreateKeyEx(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE)
    except PermissionError:
        # Retry with 64-bit view if available
        return winreg.CreateKeyEx(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE | getattr(winreg, 'KEY_WOW64_64KEY', 0))


def reg_read_dword(root, subkey, value_name, default=None):
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ) as k:
            v, t = winreg.QueryValueEx(k, value_name)
            return int(v) if t == winreg.REG_DWORD else default
    except FileNotFoundError:
        return default
    except OSError:
        return default


def reg_set_dword(root, subkey, value_name, value):
    k = reg_open_or_create(root, subkey)
    with k:
        winreg.SetValueEx(k, value_name, 0, winreg.REG_DWORD, int(value))


def reg_key_exists(root, subkey):
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ):
            return True
    except FileNotFoundError:
        return False


def reg_set_empty_default_sz(root, subkey):
    k = reg_open_or_create(root, subkey)
    with k:
        # Set default value "" (REG_SZ)
        winreg.SetValueEx(k, None, 0, winreg.REG_SZ, "")


def reg_delete_tree(root, subkey):
    # Recursively delete a key and all subkeys (Py >=3.9 has winreg.DeleteKeyEx, but we'll be robust)
    try:
        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as k:
            while True:
                try:
                    sub = winreg.EnumKey(k, 0)
                except OSError:
                    break
                reg_delete_tree(root, subkey + "\\" + sub)
        winreg.DeleteKey(root, subkey)
    except FileNotFoundError:
        pass
    except PermissionError:
        # Try 64-bit view
        with suppress(Exception):
            winreg.DeleteKeyEx(root, subkey, getattr(winreg, 'KEY_WOW64_64KEY', 0), 0)

# --------------- Tweaks ---------------

def get_classic_context_enabled() -> bool:
    return reg_key_exists(winreg.HKEY_CURRENT_USER, CLASSIC_CTXT_KEY)


def set_classic_context(enabled: bool):
    if enabled:
        reg_set_empty_default_sz(winreg.HKEY_CURRENT_USER, CLASSIC_CTXT_KEY)
    else:
        # Delete the parent CLSID key to fully revert
        parent = CLASSIC_CTXT_KEY.rsplit("\\", 1)[0]  # ...\\CLSID\\{GUID}
        reg_delete_tree(winreg.HKEY_CURRENT_USER, parent)


def get_show_file_extensions() -> bool:
    # HideFileExt: 0 = show, 1 = hide
    v = reg_read_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "HideFileExt", 1)
    return v == 0


def set_show_file_extensions(show: bool):
    reg_set_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "HideFileExt", 0 if show else 1)


def get_show_hidden_files() -> bool:
    # Hidden: 1 = show, 2 = don't show
    v = reg_read_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "Hidden", 2)
    return v == 1


def set_show_hidden_files(show: bool):
    reg_set_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "Hidden", 1 if show else 2)


def get_show_protected_files() -> bool:
    # ShowSuperHidden: 1 = show, 0 = hide
    v = reg_read_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "ShowSuperHidden", 0)
    return v == 1


def set_show_protected_files(show: bool):
    reg_set_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "ShowSuperHidden", 1 if show else 0)


def get_taskbar_left() -> bool:
    # TaskbarAl: 0 = left, 1 = center
    v = reg_read_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "TaskbarAl", 1)
    return v == 0


def set_taskbar_left(left: bool):
    reg_set_dword(winreg.HKEY_CURRENT_USER, EXPLORER_ADVANCED, "TaskbarAl", 0 if left else 1)


def restart_explorer():
    # Kill and restart Explorer cleanly
    try:
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], check=False, capture_output=True)
    except Exception:
        pass
    subprocess.Popen(["explorer.exe"])  # non-blocking

# --------------- GUI ---------------
class MeowTweakerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("520x380")
        self.root.resizable(False, False)

        main = ttk.Frame(root, padding=16)
        main.pack(fill=tk.BOTH, expand=True)

        title = ttk.Label(main, text="MeowTweaker — Windows Tweaks", font=("Segoe UI", 14, "bold"))
        subtitle = ttk.Label(main, text="Tweak safely. Changes apply per user. 🐱", foreground="#555")
        title.pack(anchor="w")
        subtitle.pack(anchor="w", pady=(0, 10))

        self.var_classic = tk.BooleanVar(value=False)
        self.var_show_ext = tk.BooleanVar(value=False)
        self.var_show_hidden = tk.BooleanVar(value=False)
        self.var_show_protected = tk.BooleanVar(value=False)
        self.var_taskbar_left = tk.BooleanVar(value=False)
        self.var_restart = tk.BooleanVar(value=True)

        card = ttk.LabelFrame(main, text="Explorer & UI")
        card.pack(fill=tk.X, pady=8)

        ttk.Checkbutton(card, text="Restore classic right‑click menu (Windows 11)", variable=self.var_classic).pack(anchor="w", padx=8, pady=6)
        ttk.Checkbutton(card, text="Show file extensions", variable=self.var_show_ext).pack(anchor="w", padx=8, pady=6)
        ttk.Checkbutton(card, text="Show hidden files", variable=self.var_show_hidden).pack(anchor="w", padx=8, pady=6)
        ttk.Checkbutton(card, text="Show protected OS files (careful)", variable=self.var_show_protected).pack(anchor="w", padx=8, pady=6)
        ttk.Checkbutton(card, text="Align taskbar to the left", variable=self.var_taskbar_left).pack(anchor="w", padx=8, pady=6)

        actions = ttk.Frame(main)
        actions.pack(fill=tk.X, pady=(12, 0))

        ttk.Checkbutton(actions, text="Restart Explorer after applying", variable=self.var_restart).pack(side=tk.LEFT)

        ttk.Button(actions, text="Apply Tweaks", command=self.apply_tweaks).pack(side=tk.RIGHT)
        ttk.Button(actions, text="Restore Defaults", command=self.restore_defaults).pack(side=tk.RIGHT, padx=(0, 8))

        footer = ttk.Label(main, text="Changes affect current user. Create a system restore point for safety.", foreground="#777")
        footer.pack(anchor="w", pady=(12, 0))

        self.load_state()

    def load_state(self):
        try:
            self.var_classic.set(get_classic_context_enabled())
            self.var_show_ext.set(get_show_file_extensions())
            self.var_show_hidden.set(get_show_hidden_files())
            self.var_show_protected.set(get_show_protected_files())
            self.var_taskbar_left.set(get_taskbar_left())
        except Exception as e:
            messagebox.showwarning(APP_TITLE, f"Could not read current settings: {e}")

    def apply_tweaks(self):
        try:
            set_classic_context(self.var_classic.get())
            set_show_file_extensions(self.var_show_ext.get())
            set_show_hidden_files(self.var_show_hidden.get())
            set_show_protected_files(self.var_show_protected.get())
            set_taskbar_left(self.var_taskbar_left.get())
            if self.var_restart.get():
                restart_explorer()
            messagebox.showinfo(APP_TITLE, "Tweaks applied successfully.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to apply tweaks: {e}")

    def restore_defaults(self):
        if not messagebox.askyesno(APP_TITLE, "Restore Microsoft defaults for all listed tweaks?"):
            return
        try:
            # Defaults: classic menu OFF; extensions hidden; hidden files hidden; protected files hidden; taskbar centered
            set_classic_context(False)
            set_show_file_extensions(False)
            set_show_hidden_files(False)
            set_show_protected_files(False)
            set_taskbar_left(False)
            if self.var_restart.get():
                restart_explorer()
            self.load_state()
            messagebox.showinfo(APP_TITLE, "Defaults restored.")
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Failed to restore defaults: {e}")


def main():
    if platform.system() != "Windows" or winreg is None:
        tk.Tk().withdraw()
        messagebox.showerror(APP_TITLE, "MeowTweaker runs on Windows only.")
        return

    # Ensure admin (elevation)
    if not is_admin():
        # Show minimal UI before relaunch for clarity
        root = tk.Tk()
        root.withdraw()
        if messagebox.askokcancel(APP_TITLE, "Administrator rights are required. Relaunch as Administrator now?"):
            root.destroy()
            relaunch_as_admin()
        else:
            root.destroy()
            return

    # Start GUI
    root = tk.Tk()
    # Use system theme where available
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    style = ttk.Style(root)
    with suppress(Exception):
        style.theme_use("vista")
    MeowTweakerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
