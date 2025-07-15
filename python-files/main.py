import os
import sys
import subprocess
import threading
import time
import requests
import ctypes
import psutil
import tkinter as tk
from tkinter import messagebox, simpledialog
import win32com.client
import glob
import zipfile
import winreg

# --- CONFIGURATION ---

INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], "MyApp")
CHECK_INTERVAL_SECONDS = 300  # 5 minutes
AGENT_API = "https://yourserver.com/get-agent-name"  # Replace with your actual URL

# Apps info
APP_1 = {
    "display_name": "AppOne",
    "installer_url": "https://example.com/app1_installer.exe",  # Replace URLs
    "installer_path": os.path.join(os.environ["TEMP"], "app1_installer.exe"),
    "uninstall_key": "AppOne",
    "silent_args": "/S"
}
APP_2 = {
    "display_name": "AppTwo",
    "installer_url": "https://example.com/app2_installer.exe",
    "installer_path": os.path.join(os.environ["TEMP"], "app2_installer.exe"),
    "uninstall_key": "AppTwo",
    "silent_args": "/S"
}

PRINTER_APP = {
    "process_name": "PrinterManager.exe",
    "uninstall_key": "Printer Manager",
    "installer_url": "https://example.com/printer_manager_installer.exe",
    "installer_path": os.path.join(os.environ["TEMP"], "printer_manager_installer.exe"),
    "download_folder_path": os.path.join(os.environ["USERPROFILE"], "Downloads", "printer_manager_installer.exe"),
    "silent_args": "/S"
}

CHROME_INSTALLER_URL = "https://dl.google.com/chrome/install/standalonesetup64.exe"
CHROME_INSTALLER_PATH = os.path.join(os.environ["TEMP"], "chrome_installer.exe")
CHROME_URL = "https://example.com/dashboard"  # URL for Chrome shortcut

ZIP_URL = "https://example.com/yourapp.zip"  # Zip file for Display mode

# --- UTILITIES ---

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

def download_file(url, dest_path):
    try:
        print(f"Downloading {url}...")
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded to {dest_path}")
    except Exception as e:
        print(f"Failed downloading {url}: {e}")
        raise

def install_application(installer_path, silent_args=""):
    print(f"Installing {installer_path}...")
    subprocess.call([installer_path] + silent_args.split())

def is_app_installed(display_name):
    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for root_key in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for uninstall_key in uninstall_keys:
            try:
                key = winreg.OpenKey(root_key, uninstall_key)
            except FileNotFoundError:
                continue
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    if name.lower() == display_name.lower():
                        return True
                except FileNotFoundError:
                    pass
                except OSError:
                    pass
            winreg.CloseKey(key)
    return False

def find_chrome_path():
    paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def delete_extra_chrome_shortcuts():
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcuts = glob.glob(os.path.join(desktop, "*.lnk"))
    shell = win32com.client.Dispatch("WScript.Shell")
    for sc in shortcuts:
        try:
            shortcut = shell.CreateShortcut(sc)
            target = shortcut.TargetPath.lower() if shortcut.TargetPath else ""
            if "chrome.exe" in target and not sc.endswith("Open App Dashboard.lnk"):
                os.remove(sc)
                print(f"Deleted shortcut: {sc}")
        except Exception as e:
            print(f"Error checking shortcut {sc}: {e}")

def create_chrome_shortcut(url, name="Open App Dashboard"):
    desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop, f"{name}.lnk")
    chrome_path = find_chrome_path()
    if not chrome_path:
        print("Chrome not found.")
        return False
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = chrome_path
    shortcut.Arguments = f'--new-window {url}'
    shortcut.IconLocation = chrome_path
    shortcut.WorkingDirectory = os.path.dirname(chrome_path)
    shortcut.Save()
    print("Created Chrome shortcut.")
    return True

def is_process_running(proc_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == proc_name.lower():
            return True
    return False

def start_printer_manager():
    installed_path = r"C:\Program Files\PrinterManager\PrinterManager.exe"  # Adjust if needed
    if os.path.exists(installed_path):
        subprocess.Popen([installed_path])
        print("Started Printer Manager.")
        return True
    print("Printer Manager executable not found.")
    return False

def download_and_install_printer_manager():
    installer_path = PRINTER_APP["installer_path"]
    if os.path.exists(PRINTER_APP["download_folder_path"]):
        installer_path = PRINTER_APP["download_folder_path"]
        print("Using installer from Downloads folder.")
    else:
        print("Downloading printer manager installer...")
        download_file(PRINTER_APP["installer_url"], installer_path)
    print("Installing printer manager...")
    install_application(installer_path, PRINTER_APP["silent_args"])

def check_and_fix_printer_manager():
    if is_process_running(PRINTER_APP["process_name"]):
        print("Printer Manager running.")
    else:
        print("Printer Manager NOT running.")
        if is_app_installed(PRINTER_APP["uninstall_key"]):
            print("Installed but not running, starting...")
            if not start_printer_manager():
                print("Failed to start. Reinstalling...")
                download_and_install_printer_manager()
        else:
            print("Not installed. Installing...")
            download_and_install_printer_manager()

def notify_user(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(title, message)
    root.destroy()

def is_connected():
    try:
        requests.get("http://clients3.google.com/generate_204", timeout=5)
        return True
    except:
        return False

def ask_mode():
    root = tk.Tk()
    root.withdraw()
    choice = simpledialog.askstring("Setup Mode", "Is this 'casher' or 'display'? (type exactly)")
    root.destroy()
    if choice:
        return choice.strip().lower()
    return None

def check_and_fix_time():
    # Your real time sync/fix code here; placeholder:
    print("Checking and fixing system time... (stub)")

def setup_apps_and_chrome():
    for app in [APP_1, APP_2]:
        if not is_app_installed(app["uninstall_key"]):
            download_file(app["installer_url"], app["installer_path"])
            install_application(app["installer_path"], app["silent_args"])
        else:
            print(f"{app['display_name']} already installed.")

    chrome_path = find_chrome_path()
    if not chrome_path:
        print("Chrome not found, installing...")
        download_file(CHROME_INSTALLER_URL, CHROME_INSTALLER_PATH)
        install_application(CHROME_INSTALLER_PATH, "/silent /install")
        time.sleep(30)  # wait for install

    delete_extra_chrome_shortcuts()
    create_chrome_shortcut(CHROME_URL)

def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted zip to {extract_to}")

def download_and_extract_zip():
    zip_path = os.path.join(os.environ["TEMP"], "app_zip.zip")
    if not os.path.exists(INSTALL_DIR):
        os.makedirs(INSTALL_DIR)
    download_file(ZIP_URL, zip_path)
    extract_zip(zip_path, INSTALL_DIR)

def self_destruct():
    print("Self-destruct triggered. Deleting executable...")
    try:
        os.remove(sys.argv[0])
    except Exception as e:
        print("Failed to delete self:", e)
    sys.exit(1)

def get_agent_name():
    try:
        response = requests.get(AGENT_API, timeout=10)
        if response.status_code != 200:
            print(f"Agent server error: {response.status_code}")
            self_destruct()
        agent = response.text.strip()
        print(f"Agent received: {agent}")
        return agent
    except Exception as e:
        print(f"Failed to get agent: {e}")
        self_destruct()

def modify_batch_file(agent):
    bat_path = os.path.join(INSTALL_DIR, "Run_GenericAndSlideWindow.bat")
    if not os.path.exists(bat_path):
        print("Batch file not found:", bat_path)
        return
    with open(bat_path, "r") as f:
        content = f.read()
    new_content = content.replace('agent=AELKPS', f'agent={agent}')
    with open(bat_path, "w") as f:
        f.write(new_content)
    print("Batch file modified with agent.")

def run_time_sync_loop():
    while True:
        check_and_fix_time()
        time.sleep(CHECK_INTERVAL_SECONDS)

def run_printer_manager_loop():
    while True:
        check_and_fix_printer_manager()
        time.sleep(CHECK_INTERVAL_SECONDS)

def main():
    mode = ask_mode()
    if mode not in ("casher", "display"):
        print("Invalid mode selected. Exiting.")
        sys.exit(1)

    if not is_admin():
        run_as_admin()
        return

    setup_apps_and_chrome()

    threading.Thread(target=run_time_sync_loop, daemon=True).start()
    threading.Thread(target=run_printer_manager_loop, daemon=True).start()

    if mode == "display":
        download_and_extract_zip()
        agent = get_agent_name()
        if agent:
            modify_batch_file(agent)
        # You can add display orientation and extend mode enforcement here if you want.

    # Keep the program running
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
