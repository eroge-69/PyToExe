import subprocess
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def rename_account(old_name, new_name):
    command = f'Rename-LocalUser -Name "{old_name}" -NewName "{new_name}"'
    subprocess.run(["powershell", "-Command", command], shell=True)

if __name__ == "__main__":
    if not is_admin():
        # Relaunch as admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    print("🧑 Current account name:")
    old_name = input(">> ")
    print("✏️ New account name:")
    new_name = input(">> ")

    print(f"Renaming '{old_name}' to '{new_name}'...")
    rename_account(old_name, new_name)
    print("✅ Done! You may need to restart for changes to fully apply.")
