import zipfile
import rarfile
import py7zr
from tqdm import tqdm
import argparse
import os

def crack_zip(zip_file, password_list):
    with zipfile.ZipFile(zip_file) as zf:
        for password in tqdm(password_list, desc="Testing ZIP passwords"):
            try:
                zf.extractall(pwd=password.encode())
                print(f"\n[+] Password found: {password}")
                return password
            except (RuntimeError, zipfile.BadZipFile):
                pass
    return None

def crack_rar(rar_file, password_list):
    with rarfile.RarFile(rar_file) as rf:
        for password in tqdm(password_list, desc="Testing RAR passwords"):
            try:
                rf.extractall(pwd=password)
                print(f"\n[+] Password found: {password}")
                return password
            except (rarfile.BadRarFile, rarfile.PasswordRequired):
                pass
    return None

def crack_7z(sevenz_file, password_list):
    with py7zr.SevenZipFile(sevenz_file, mode='r') as zf:
        for password in tqdm(password_list, desc="Testing 7Z passwords"):
            try:
                zf.extractall(pwd=password)
                print(f"\n[+] Password found: {password}")
                return password
            except py7zr.Bad7zFile:
                pass
    return None

def main():
    parser = argparse.ArgumentParser(description="Archive Password Cracker")
    parser.add_argument("archive", help="Path to the archive file (.zip, .rar, .7z)")
    parser.add_argument("wordlist", help="Path to the password wordlist")
    args = parser.parse_args()

    if not os.path.exists(args.archive):
        print("[-] Archive file not found!")
        return
    if not os.path.exists(args.wordlist):
        print("[-] Wordlist file not found!")
        return

    with open(args.wordlist, "r", encoding="utf-8", errors="ignore") as f:
        passwords = [line.strip() for line in f]

    ext = os.path.splitext(args.archive)[1].lower()

    if ext == ".zip":
        result = crack_zip(args.archive, passwords)
    elif ext == ".rar":
        result = crack_rar(args.archive, passwords)
    elif ext == ".7z":
        result = crack_7z(args.archive, passwords)
    else:
        print("[-] Unsupported archive format!")
        return

    if not result:
        print("[-] Password not found in the wordlist.")

if __name__ == "__main__":
    main()
