import os
import shutil
import subprocess
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import pyautogui
import pyperclip
import win32com.client
import pygetwindow as gw

user_home = os.path.expanduser("~")
desktop_path = os.path.join(user_home, "Desktop")

def create_shortcut(target_path, shortcut_path, working_directory=None, description=None):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.WorkingDirectory = working_directory or os.path.dirname(target_path)
    shortcut.Description = description or "GroundTruth Annotator"
    shortcut.save()
    print(f"[SUCCESS] Shortcut created at: {shortcut_path}")

def select_version_gui():
    root = tk.Tk()
    root.title("Select GroundTruth Version")
    root.geometry("350x150")
    version_var = tk.StringVar(value="9370")
    versions = ["9370", "9405"]

    tk.Label(root, text="Select GroundTruthAnnotator version:").pack(pady=10)
    dropdown = ttk.Combobox(root, values=versions, textvariable=version_var, state="readonly")
    dropdown.pack()

    def submit():
        root.quit()
        root.destroy()

    tk.Button(root, text="OK", command=submit).pack(pady=10)
    root.mainloop()
    return version_var.get()

def ask_project_folder():
    root = tk.Tk()
    root.withdraw()
    return simpledialog.askstring("Project Folder", "Enter the project folder name:")

def search_for_exe(version_substring):
    search_dirs = [
        os.path.join(user_home, "Downloads"),
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Documents"),
        "C:\\", "D:\\", "E:\\"
    ]

    for base in search_dirs:
        for root, dirs, files in os.walk(base):
            if any(skip in root.lower() for skip in ["windows", "program files", "$recycle", "system volume information"]):
                continue
            if "groundtruth" in root.lower() and version_substring in root:
                for file in files:
                    if file.lower() == "groundtruthannotator.exe":
                        return os.path.join(root, file)
    return None

def find_or_copy_project(folder_name):
    project_folder = os.path.join(user_home, "GroundTruthProjects", folder_name)
    if os.path.exists(project_folder):
        print(f"[INFO] Found project folder locally: {project_folder}")
        return project_folder

    # Search for the project if not found locally
    search_dirs = [
        os.path.join(user_home, "Downloads"),
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Documents"),
        "C:\\", "D:\\", "E:\\"
    ]
    for base in search_dirs:
        for root, dirs, _ in os.walk(base):
            for d in dirs:
                if d.lower() == folder_name.lower():
                    source_path = os.path.join(root, d)
                    try:
                        shutil.copytree(source_path, project_folder)
                        print(f"[INFO] Copied project folder to: {project_folder}")
                    except Exception as e:
                        print(f"[ERROR] Failed to copy project folder: {e}")
                    return project_folder
    return None

# --- MAIN LOGIC ---

selected_version = select_version_gui()
print(f"[INFO] Version selected: {selected_version}")

exe_path = search_for_exe(selected_version)
if not exe_path:
    messagebox.showerror("Error", f"Could not find GroundTruthAnnotator.exe for version {selected_version}")
    exit()

print(f"[INFO] Found EXE at: {exe_path}")

# Create app and project folders
app_folder = os.path.join(user_home, f"GroundTruthAnnotator {selected_version}")
project_base_folder = os.path.join(user_home, "GroundTruthProjects")
os.makedirs(app_folder, exist_ok=True)
os.makedirs(project_base_folder, exist_ok=True)

# Create shortcut in app folder and desktop
shortcut_in_app = os.path.join(app_folder, "GroundTruthAnnotator.lnk")
shortcut_on_desktop = os.path.join(desktop_path, f"GroundTruthAnnotator_{selected_version}.lnk")
create_shortcut(exe_path, shortcut_in_app)
create_shortcut(exe_path, shortcut_on_desktop)

# Ask for project folder
folder_name = ask_project_folder()
if not folder_name:
    messagebox.showwarning("Cancelled", "No project folder name provided. Exiting.")
    exit()

project_path = find_or_copy_project(folder_name)
if not project_path:
    messagebox.showerror("Not Found", f"Folder '{folder_name}' not found anywhere on system.")
    exit()

print(f"[INFO] Ensured folders:\n - {app_folder}\n - {project_path}")

# Launch application via shortcut
print(f"[INFO] Launching app from: {exe_path}")
subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
time.sleep(5)

# Focus application window
print("[INFO] Waiting for window...")
for _ in range(10):
    try:
        win = next(w for w in gw.getWindowsWithTitle("GroundTruthAnnotator") if w.isVisible)
        win.activate()
        break
    except:
        time.sleep(1)

# Automate "Load Project"
try:
    print(f"[INFO] Automating Load Project with: {project_path}")
    
    pyautogui.hotkey('alt', 'f')     # Open File menu
    time.sleep(1)
    pyautogui.press('enter')         # Select "Load Project"
    time.sleep(2)

    pyautogui.hotkey('alt', 'd')     # Focus address bar
    pyperclip.copy(project_path)
    pyautogui.hotkey('ctrl', 'v')    # Paste folder path
    pyautogui.press('enter')         # Navigate to folder
    time.sleep(1)

    pyautogui.press('enter')         # Press "Select Folder"
    pyautogui.press('enter')         # Confirm again if needed
    pyautogui.press('enter')         # Final confirmation

    print(f"[SUCCESS] Project folder loaded: {project_path}")

except Exception as e:
    print("[ERROR] Automation failed:", e)
    messagebox.showerror("Automation Error", str(e))
