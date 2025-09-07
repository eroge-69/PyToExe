import os
import sys
import random
import string
from datetime import datetime, timedelta
import subprocess

# =============================
# GLOBAL SETTINGS
# =============================
ADMIN_CODE = "101"
KEY_FILE = "keys.txt"
keys = []
logged_in_key = None

# =============================
# KEY MANAGEMENT
# =============================
def load_keys():
    global keys
    keys = []
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    key, key_type, expire, status = line.split(";")
                    keys.append({"key": key, "type": key_type, "expire": expire, "status": status})

def save_keys():
    with open(KEY_FILE, "w") as f:
        for k in keys:
            f.write(f"{k['key']};{k['type']};{k['expire']};{k['status']}\n")

def generate_key(key_type):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    today = datetime.today()
    if key_type == "Lifetime":
        expire = "2099-12-31"
    elif key_type == "Yearly":
        expire = (today + timedelta(days=365)).strftime("%Y-%m-%d")
    elif key_type == "Monthly":
        expire = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    elif key_type == "Weekly":
        expire = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    else:
        expire = today.strftime("%Y-%m-%d")
    keys.append({"key": key, "type": key_type, "expire": expire, "status": "active"})
    save_keys()
    return key, expire

# =============================
# ADMIN MENU
# =============================
def admin_menu():
    os.system("cls")  # clear console before admin menu
    while True:
        print("\n=== ADMIN MENU ===")
        print("[1] Generate Key")
        print("[2] Show Keys")
        print("[3] Deactivate Key")
        print("[0] Back to Login (clears session)")
        choice = input("Choose: ")

        if choice == "1":
            os.system("cls")
            print("Select Key Type:")
            print("[1] Lifetime")
            print("[2] Yearly")
            print("[3] Monthly")
            print("[4] Weekly")
            type_choice = input("Choose: ")
            type_map = {"1": "Lifetime", "2": "Yearly", "3": "Monthly", "4": "Weekly"}
            key_type = type_map.get(type_choice)
            if not key_type:
                print("Invalid choice")
                continue
            key, expire = generate_key(key_type)
            print(f"Generated Key: {key} | Type: {key_type} | Expire: {expire}")

        elif choice == "2":
            os.system("cls")
            print("Existing Keys:")
            for k in keys:
                print(f"{k['key']} | {k['type']} | {k['expire']} | {k['status']}")
        elif choice == "3":
            os.system("cls")
            del_key = input("Enter Key to deactivate: ")
            found = False
            for k in keys:
                if k["key"] == del_key:
                    k["status"] = "inactive"
                    print(f"Key {del_key} deactivated!")
                    found = True
                    break
            if not found:
                print("Key not found!")
            save_keys()
        elif choice == "0":
            os.system("cls")
            # Clear temp admin session
            return
        else:
            print("Invalid choice!")

# =============================
# LOGIN SYSTEM
# =============================
def login_system():
    global logged_in_key
    load_keys()
    logged_in_key = None
    while True:
        key_input = input("Enter your key: ")
        if key_input == ADMIN_CODE:
            admin_menu()
            # After admin menu, clear login to require new key
            logged_in_key = None
            continue
        # Check normal key
        valid = False
        for k in keys:
            if k["key"] == key_input and k["status"] == "active":
                today = datetime.today().strftime("%Y-%m-%d")
                if k["expire"] >= today:
                    valid = True
                    logged_in_key = k["key"]
                    break
        if valid:
            print("Login successful!")
            break
        else:
            print("Invalid or expired key!")

# =============================
# TWEAK FUNCTIONS
# =============================
def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Warning: Could not execute: {cmd}")

def spielmodus_ein(): run_command('REG ADD "HKEY_CURRENT_USER\\System\\GameConfigStore" /v GameMode /t REG_DWORD /d 1 /f')
def spielmodus_aus(): run_command('REG ADD "HKEY_CURRENT_USER\\System\\GameConfigStore" /v GameMode /t REG_DWORD /d 0 /f')
def gamebar_remove(): run_command('powershell -Command "Get-AppxPackage -AllUsers *Microsoft.XboxGamingOverlay* | Remove-AppxPackage"')
def energieplan(): run_command("powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
def visuelle_effekte(): run_command('REG ADD "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f')
def transparenz():
    run_command('REG ADD "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f')
    run_command('REG ADD "HKEY_CURRENT_USER\\Control Panel\\Desktop" /v UserPreferencesMask /t REG_BINARY /d 90120080 /f')
    run_command('REG ADD "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarAnimations /t REG_DWORD /d 0 /f')
    run_command('REG ADD "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ListviewAlphaSelect /t REG_DWORD /d 0 /f')
def prioritaet(): run_command('REG ADD "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl" /v Win32PrioritySeparation /t REG_DWORD /d 26 /f')
def prefetch():
    run_command('REG ADD "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\Session Manager\\Memory Management\\PrefetchParameters" /v EnablePrefetcher /t REG_DWORD /d 3 /f')
    run_command('REG ADD "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\Session Manager\\Memory Management\\PrefetchParameters" /v EnableSuperfetch /t REG_DWORD /d 0 /f')
def temp_und_papierkorb():
    temp = os.environ.get("TEMP")
    try:
        run_command(f'rd /s /q "{temp}"')
        os.makedirs(temp, exist_ok=True)
        run_command('rd /s /q "C:\\Windows\\Temp"')
        os.makedirs("C:\\Windows\\Temp", exist_ok=True)
        run_command('powershell -Command "Clear-RecycleBin -Force -Confirm:$false"')
    except Exception as e:
        print(f"Warning: {e}")

def do_all():
    spielmodus_ein()
    gamebar_remove()
    energieplan()
    visuelle_effekte()
    transparenz()
    prioritaet()
    prefetch()
    temp_und_papierkorb()

# =============================
# MAIN MENU LOOP
# =============================
def main_menu():
    while True:
        print("\n=== ULTIMATE PERFORMANCE OPTIMIZER ===")
        print("[1] Spielmodus aktivieren")
        print("[2] Spielmodus deaktivieren")
        print("[3] Xbox Game Bar deinstallieren")
        print("[4] Energieplan auf Hoechstleistung setzen")
        print("[5] Visuelle Effekte optimieren")
        print("[6] Transparenz- und Animationseffekte ausschalten")
        print("[7] Hintergrunddienste priorisieren")
        print("[8] Prefetch / Superfetch optimieren")
        print("[9] Temp-Ordner und Papierkorb leeren")
        print("[10] ALLES AUSFUEHREN (Do All)")
        print("[0] Beenden")

        choice = input("Bitte Auswahl eingeben: ")

        if choice == "1": spielmodus_ein()
        elif choice == "2": spielmodus_aus()
        elif choice == "3": gamebar_remove()
        elif choice == "4": energieplan()
        elif choice == "5": visuelle_effekte()
        elif choice == "6": transparenz()
        elif choice == "7": prioritaet()
        elif choice == "8": prefetch()
        elif choice == "9": temp_und_papierkorb()
        elif choice == "10": do_all()
        elif choice == "0":
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice!")

# =============================
# RUN
# =============================
if __name__ == "__main__":
    while True:
        login_system()
        main_menu()
