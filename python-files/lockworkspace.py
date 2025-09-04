import getpass
import os
import platform
import shutil
import time

# === CONFIG ===
FOLDER_NAME = "nigga56"  # Change this to the folder you want to lock
PASSWORD = "1234"  # Set your desired password


# === INTRO ART ===
def show_intro():
    print(r"""
|￣￣￣￣￣￣￣￣￣￣￣￣￣￣|
  Welcome to Folder Locker
|＿＿＿＿＿＿＿＿＿＿＿＿＿＿|
         \ (•◡•) /
           \     /
""")
    time.sleep(1)


# === ACCESS DENIED ART ===
def access_denied():
    print(r"""
|￣￣￣￣￣￣￣￣￣￣￣￣￣￣|
         Access Denied!
|＿＿＿＿＿＿＿＿＿＿＿＿＿＿|
         \ (•◡•) /
           \     /
""")
    print("❌ Wrong password.")


# === FOLDER LOCK / UNLOCK ===


def is_hidden_windows(path):
    import ctypes

    attribute = ctypes.windll.kernel32.GetFileAttributesW(path)
    return attribute & 2  # FILE_ATTRIBUTE_HIDDEN == 2


def hide_folder(path):
    if platform.system() == "Windows":
        os.system(f'attrib +h +s "{path}"')
    else:
        if not path.startswith("."):
            hidden_path = "." + path
            os.rename(path, hidden_path)
            return hidden_path
    return path


def unhide_folder(path):
    if platform.system() == "Windows":
        os.system(f'attrib -h -s "{path}"')
    else:
        if os.path.basename(path).startswith("."):
            visible_path = path.lstrip(".")
            os.rename(path, visible_path)
            return visible_path
    return path


def folder_exists(path):
    return os.path.exists(path)


# === PASSWORD PROMPT ===
def ask_access():
    print("\nDo you want to access the locked folder? (yes/no)")
    choice = input(">> ").strip().lower()
    return choice in ["yes", "y"]


def verify_password():
    print("\n🔐 Enter password to unlock the folder.")
    try:
        pwd = getpass.getpass("Password: ")
    except Exception:
        print("⚠️ Could not hide password input. Falling back to visible input.")
        pwd = input("Password (visible): ")
    return pwd == PASSWORD


# === MAIN ===
def main():
    os.system("cls" if os.name == "nt" else "clear")
    show_intro()

    folder_path = FOLDER_NAME
    hidden_folder_path = (
        "." + FOLDER_NAME if platform.system() != "Windows" else FOLDER_NAME
    )

    if not folder_exists(folder_path) and not folder_exists(hidden_folder_path):
        print(f"⚠️ Folder '{FOLDER_NAME}' not found. Creating it for you...")
        os.makedirs(folder_path)
        hide_folder(folder_path)
        print("✅ Folder created and locked.")
        return

    if not ask_access():
        print("Goodbye!")
        return

    if verify_password():
        # Unlock folder
        visible_path = unhide_folder(
            hidden_folder_path if folder_exists(hidden_folder_path) else folder_path
        )
        print("\n✅ Folder Unlocked:", visible_path)
        time.sleep(1)
        os.system(
            f'explorer "{visible_path}"'
            if platform.system() == "Windows"
            else f'open "{visible_path}"'
        )
    else:
        access_denied()


if __name__ == "__main__":
    main()
