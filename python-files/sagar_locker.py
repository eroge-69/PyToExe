import os
import ctypes
import hashlib

FOLDER_NAME = "Private"
PASSWORD_HASH = "5f4dcc3b5aa765d61d8327deb882cf99"  # md5("password")

def is_folder_hidden(path):
    attrs = ctypes.windll.kernel32.GetFileAttributesW(path)
    return bool(attrs & 2)

def hide_folder(path):
    os.system(f'attrib +h +s "{path}"')

def unhide_folder(path):
    os.system(f'attrib -h -s "{path}"')

def main():
    if not os.path.exists(FOLDER_NAME):
        os.makedirs(FOLDER_NAME)
        print(f"[+] Created folder: {FOLDER_NAME}")

    user_input = input("Enter password to toggle lock: ").strip()
    input_hash = hashlib.md5(user_input.encode()).hexdigest()

    if input_hash != PASSWORD_HASH:
        print("[-] Incorrect password.")
        return

    if is_folder_hidden(FOLDER_NAME):
        print("[*] Folder is currently hidden. Unlocking...")
        unhide_folder(FOLDER_NAME)
        print("[+] Folder is now visible.")
    else:
        print("[*] Folder is visible. Locking...")
        hide_folder(FOLDER_NAME)
        print("[+] Folder is now locked and hidden.")

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")
