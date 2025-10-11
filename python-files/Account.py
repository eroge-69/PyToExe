import os
import sys
import ctypes
import json
import subprocess
import tempfile
import requests
import webbrowser
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

# ---------------- CONFIG ----------------
DATA_FILE = "accounts.json"
CONFIG_FILE = "launcher_config.json"
GITHUB_BLOB_URL = "https://github.com/lazzyont7t/launcher/blob/main/Launcher.exe"
TARGET_DIR = Path(os.getenv("APPDATA", Path.home())) / "dglauncher"
TARGET_PATH = TARGET_DIR / "Launcher.exe"
NODE_INSTALLER_URL = "https://nodejs.org/dist/latest/win-x64/node.msi"

# Platforms (lowercase)
PLATFORMS = [
    "uea8", "u88", "tgb88", "surewin", "mzplay", "me88",
    "maxwin", "god55", "boda8", "betsuper", "aw8", "ap33"
]

# ---------------- ADMIN CHECK ----------------
def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False
    if not is_admin:
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

ensure_admin()

# ---------------- HELPERS ----------------
def convert_blob_to_raw(github_url: str) -> str:
    if "github.com" not in github_url:
        return github_url
    try:
        parts = github_url.split("github.com/", 1)[1]
        if "/blob/" in parts:
            user_repo, rest = parts.split("/blob/", 1)
            return f"https://raw.githubusercontent.com/{user_repo}/{rest}"
        return github_url
    except Exception:
        return github_url

def safe_download(url: str, dest: Path) -> bool:
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(dest, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        messagebox.showerror("Download Error", str(e))
        return False

# ---------------- NODE & PUPPETEER ----------------
def install_node_and_puppeteer():
    try:
        subprocess.check_output(["node", "-v"], shell=True)
        messagebox.showinfo("Node.js", "Node.js is already installed.")
    except Exception:
        messagebox.showinfo("Node.js", "Node.js not found. Downloading installer...")
        tmp = Path(tempfile.mkdtemp())
        installer_path = tmp / "node_installer.msi"
        if safe_download(NODE_INSTALLER_URL, installer_path):
            messagebox.showinfo("Installer", "Launching Node.js installer. Follow the setup wizard, then click OK when finished.")
            subprocess.Popen(["msiexec", "/i", str(installer_path)], shell=True)
        else:
            messagebox.showerror("Error", "Failed to download Node.js installer.")
            return
        messagebox.showinfo("Continue", "Once Node.js installation is complete, click OK to continue.")

    # Verify Node installation
    try:
        subprocess.check_output(["node", "-v"], shell=True)
    except Exception:
        messagebox.showerror("Error", "Node.js installation not detected. Please install it manually from https://nodejs.org/")
        return

    # Install Puppeteer in the launcher directory
    try:
        subprocess.check_call(["npm", "init", "-y"], cwd=TARGET_DIR, shell=True)
        subprocess.check_call(["npm", "install", "puppeteer"], cwd=TARGET_DIR, shell=True)
        messagebox.showinfo("Success", f"Puppeteer installed successfully in:\n{TARGET_DIR}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Install Failed", f"Failed to install puppeteer:\n{e}")

# ---------------- SETUP / REPAIR ----------------
def run_setup(repair=False):
    action = "repair" if repair else "setup"
    msg = "Do you want to run a full repair? This will reinstall Launcher.exe, Node.js, and Puppeteer." if repair \
        else "Run first-time setup now?"
    if not messagebox.askyesno("Confirm", msg):
        return

    raw_url = convert_blob_to_raw(GITHUB_BLOB_URL)

    messagebox.showinfo("Download", f"Downloading Launcher.exe from:\n{raw_url}")
    ok = safe_download(raw_url, TARGET_PATH)
    if ok:
        messagebox.showinfo("Downloaded", f"Saved to:\n{TARGET_PATH}")
    else:
        messagebox.showerror("Error", "Launcher download failed.")
        return

    install_node_and_puppeteer()

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"setup_done": True, "last_action": action}, f)
    messagebox.showinfo("Done", f"{action.title()} complete.")

# ---------------- ACCOUNTS ----------------
def load_accounts():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_accounts(accounts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=4)

# ---------------- GUI ----------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Modern Account Launcher (Admin Mode)")
app.geometry("780x600")

accounts = load_accounts()

def add_account():
    u, p = entry_username.get().strip(), entry_password.get().strip()
    plat = combo_platform.get().strip().lower()
    if not (u and p and plat):
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return
    accounts.append({"username": u, "password": p, "platform": plat})
    save_accounts(accounts)
    refresh_table()
    entry_username.delete(0, "end")
    entry_password.delete(0, "end")

def delete_selected():
    sel = table.get_selected()
    if not sel:
        messagebox.showwarning("No Selection", "Select an account first.")
        return
    for i, acc in enumerate(accounts):
        if tuple(acc.values()) == sel:
            del accounts[i]
            save_accounts(accounts)
            refresh_table()
            return

def launch_selected():
    sel = table.get_selected()
    if not sel:
        messagebox.showwarning("No Selection", "Please select an account first.")
        return
    username, password, platform = sel
    if not os.path.exists(TARGET_PATH):
        messagebox.showerror("Missing Launcher", f"Launcher.exe not found at:\n{TARGET_PATH}\nTry running 'Repair Setup'.")
        return
    cmd = [str(TARGET_PATH), username, password, platform]
    try:
        subprocess.Popen(cmd, shell=True)
        messagebox.showinfo("Launching", f"Launching {platform} with {username}")
    except Exception as e:
        messagebox.showerror("Launch Failed", str(e))

# ---------------- Table ----------------
class SimpleTable(ctk.CTkScrollableFrame):
    def __init__(self, master, headers):
        super().__init__(master)
        self.headers = headers
        self.rows = []
        self.selected_index = None
        header = ctk.CTkFrame(self)
        header.pack(fill="x")
        for i, h in enumerate(headers):
            ctk.CTkLabel(header, text=h, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=i, padx=40, sticky="w")
        self.body = ctk.CTkFrame(self)
        self.body.pack(fill="both", expand=True)

    def insert_row(self, values):
        idx = len(self.rows)
        frame = ctk.CTkFrame(self.body)
        frame.pack(fill="x", pady=2)
        for i, v in enumerate(values):
            lbl = ctk.CTkLabel(frame, text=v)
            lbl.grid(row=0, column=i, padx=40, sticky="w")
        frame.bind("<Button-1>", lambda e, i=idx: self.select(i))
        for w in frame.winfo_children():
            w.bind("<Button-1>", lambda e, i=idx: self.select(i))
        self.rows.append((frame, values))

    def clear(self):
        for f, _ in self.rows:
            f.destroy()
        self.rows = []
        self.selected_index = None

    def select(self, index):
        for i, (f, _) in enumerate(self.rows):
            f.configure(fg_color="#377dff" if i == index else "transparent")
        self.selected_index = index

    def get_selected(self):
        return self.rows[self.selected_index][1] if self.selected_index is not None else None

# ---------------- Layout ----------------
frame_top = ctk.CTkFrame(app)
frame_top.pack(fill="x", padx=20, pady=10)

ctk.CTkLabel(frame_top, text="Username / Phone:").grid(row=0, column=0, sticky="w")
entry_username = ctk.CTkEntry(frame_top, width=250)
entry_username.grid(row=0, column=1, padx=6, pady=6)

ctk.CTkLabel(frame_top, text="Password:").grid(row=1, column=0, sticky="w")
entry_password = ctk.CTkEntry(frame_top, width=250)
entry_password.grid(row=1, column=1, padx=6, pady=6)

ctk.CTkLabel(frame_top, text="Platform:").grid(row=2, column=0, sticky="w")
combo_platform = ctk.CTkOptionMenu(frame_top, values=PLATFORMS)
combo_platform.grid(row=2, column=1, padx=6, pady=6)
combo_platform.set(PLATFORMS[0])

ctk.CTkButton(frame_top, text="Add Account", command=add_account).grid(row=3, column=0, pady=10)
ctk.CTkButton(frame_top, text="Delete Selected", fg_color="#d9534f", command=delete_selected).grid(row=3, column=1, pady=10)

frame_table = ctk.CTkFrame(app)
frame_table.pack(fill="both", expand=True, padx=20, pady=10)

table = SimpleTable(frame_table, ["Username", "Password", "Platform"])
table.pack(fill="both", expand=True)

def refresh_table():
    table.clear()
    for a in accounts:
        table.insert_row(tuple(a.values()))
refresh_table()

frame_bottom = ctk.CTkFrame(app)
frame_bottom.pack(fill="x", padx=20, pady=(10, 20))

ctk.CTkButton(frame_bottom, text="Launch Selected Account", fg_color="#28a745", command=launch_selected).pack(side="left", padx=10)
ctk.CTkButton(frame_bottom, text="Repair Setup", fg_color="#f39c12", command=lambda: run_setup(repair=True)).pack(side="right", padx=10)

if not os.path.exists(CONFIG_FILE):
    app.after(200, lambda: run_setup(repair=False))

app.mainloop()
