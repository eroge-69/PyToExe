```python
import os
import shutil
import datetime
import psutil

# ==============================
# CONFIGURATION AREA
# ==============================
# Add your games here.
# Example entry:
# "Skyrim": {
#     "process": "SkyrimSE.exe",
#     "save_path": os.path.expanduser("~/Documents/My Games/Skyrim Special Edition/Saves")
# }

GAMES = {
    # Empty by default — you add your own games here.
}

# How many backups to keep per game
MAX_BACKUPS = 5

# ==============================
# TOOL LOGIC
# ==============================

def detect_usb_drive():
    """Detect the first removable drive (USB)."""
    import string
    from ctypes import windll
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:\\"
            if windll.kernel32.GetDriveTypeW(drive) == 2:  # DRIVE_REMOVABLE
                drives.append(drive)
        bitmask >>= 1
    return drives[0] if drives else None


def get_backup_root():
    usb = detect_usb_drive()
    if usb:
        return os.path.join(usb, "GameBackups")
    else:
        return os.path.expanduser("~/Documents/GameBackups")


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)


def is_process_running(process_name):
    for proc in psutil.process_iter(attrs=['name']):
        if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
            return True
    return False


def backup_game(game_name, config):
    save_path = config["save_path"]
    if not os.path.exists(save_path):
        print(f"[!] Save path for {game_name} not found: {save_path}")
        return

    backup_root = get_backup_root()
    game_backup_dir = os.path.join(backup_root, game_name)
    ensure_folder(game_backup_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dest = os.path.join(game_backup_dir, f"backup_{timestamp}")
    shutil.copytree(save_path, backup_dest)

    print(f"[+] Backup created for {game_name} at {backup_dest}")

    # Auto-clean old backups
    backups = sorted(os.listdir(game_backup_dir))
    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        shutil.rmtree(os.path.join(game_backup_dir, oldest))
        print(f"[-] Old backup removed: {oldest}")


def list_backups(game_name):
    backup_root = get_backup_root()
    game_backup_dir = os.path.join(backup_root, game_name)
    if not os.path.exists(game_backup_dir):
        print("[!] No backups found.")
        return []
    backups = sorted(os.listdir(game_backup_dir))
    for i, b in enumerate(backups, 1):
        print(f"{i}. {b}")
    return backups


def restore_game(game_name, config):
    if is_process_running(config["process"]):
        print(f"[!] {game_name} is currently running. Close it before restoring.")
        return

    backups = list_backups(game_name)
    if not backups:
        return

    choice = input("Select backup number to restore: ")
    try:
        idx = int(choice) - 1
        selected_backup = backups[idx]
    except:
        print("[!] Invalid choice.")
        return

    backup_root = get_backup_root()
    game_backup_dir = os.path.join(backup_root, game_name, selected_backup)

    save_path = config["save_path"]
    ensure_folder(save_path)

    # Clear current saves
    if os.path.exists(save_path):
        for item in os.listdir(save_path):
            item_path = os.path.join(save_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            else:
                shutil.rmtree(item_path)

    # Copy backup into save folder
    for item in os.listdir(game_backup_dir):
        s = os.path.join(game_backup_dir, item)
        d = os.path.join(save_path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    print(f"[+] Restored {game_name} from {selected_backup}")


# ==============================
# MAIN MENU
# ==============================

def main():
    if not GAMES:
        print("[!] No games configured. Edit the script and add entries to GAMES.")
        return

    print("=== Portable Save USB Tool ===")
    for i, game in enumerate(GAMES.keys(), 1):
        print(f"{i}. {game}")

    choice = input("Select game: ")
    try:
        game_idx = int(choice) - 1
        game_name = list(GAMES.keys())[game_idx]
        config = GAMES[game_name]
    except:
        print("[!] Invalid selection.")
        return

    print("1. Backup now")
    print("2. List backups")
    print("3. Restore backup")
    action = input("Choose action: ")

    if action == "1":
        backup_game(game_name, config)
    elif action == "2":
        list_backups(game_name)
    elif action == "3":
        restore_game(game_name, config)
    else:
        print("[!] Invalid action.")


if __name__ == "__main__":
    main()
```
