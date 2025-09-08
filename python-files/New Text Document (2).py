# remote_control.py
import os
import sys
import time
import ctypes
import socket
import struct
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# تنظیمات
SECRET_KEY = "mohammad_secure_key_2024"
AUTH_TOKEN = "home_token_mohammad_5678"
PORT = 5000
MAC_ADDRESS = "D8-FE-E3-2F-CB-17"  # آدرس MAC کامپیوتر خود را اینجا وارد کنید
BROADCAST_IP = "192.168.1.255"     # آدرس broadcast شبکه خود را اینجا وارد کنید

def get_public_ip():
    """دریافت IP عمومی کامپیوتر"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "قابل تشخیص نیست"

def send_wake_on_lan():
    """ارسال بسته Wake-on-Lan"""
    try:
        mac_bytes = bytes.fromhex(MAC_ADDRESS.replace(':', '').replace('-', ''))
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, (BROADCAST_IP, 9))
        
        return True
    except Exception as e:
        print(f"خطا در ارسال Wake-on-LAN: {e}")
        return False

def shutdown_computer(delay=0):
    time.sleep(delay)
    if os.name == 'nt':
        os.system('shutdown /s /f /t 0')

def restart_computer(delay=0):
    time.sleep(delay)
    if os.name == 'nt':
        os.system('shutdown /r /f /t 0')

def sleep_computer(delay=0):
    time.sleep(delay)
    if os.name == 'nt':
        ctypes.windll.powrprof.SetSuspendState(0, 1, 0)

@app.route('/control', methods=['POST'])
def control_computer():
    try:
        auth_header = request.headers.get('X-Auth-Token')
        if not auth_header or auth_header != AUTH_TOKEN:
            return jsonify({"status": "error", "message": "خطای احراز هویت"}), 401
        
        data = request.get_json()
        if not data or data.get('key') != SECRET_KEY:
            return jsonify({"status": "error", "message": "کلید نامعتبر"}), 401
        
        action = data.get('action')
        delay = data.get('delay', 0)
        
        if action == 'shutdown':
            threading.Thread(target=shutdown_computer, args=(delay,)).start()
            return jsonify({"status": "success", "message": "دستور خاموش کردن ارسال شد"})
        elif action == 'restart':
            threading.Thread(target=restart_computer, args=(delay,)).start()
            return jsonify({"status": "success", "message": "دستور راه اندازی مجدد ارسال شد"})
        elif action == 'sleep':
            threading.Thread(target=sleep_computer, args=(delay,)).start()
            return jsonify({"status": "success", "message": "دستور خواب ارسال شد"})
        elif action == 'wake':
            success = send_wake_on_lan()
            if success:
                return jsonify({"status": "success", "message": "دستور روشن کردن ارسال شد"})
            else:
                return jsonify({"status": "error", "message": "خطا در ارسال دستور روشن کردن"})
        else:
            return jsonify({"status": "error", "message": "دستور نامعتبر"}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "service": "remote-computer-control",
        "message": "سرور فعال است - طراحی شده برای آقا محمد",
        "public_ip": get_public_ip(),
        "timestamp": time.time()
    })

def main():
    print("=" * 60)
    print("🖥️ سرور کنترل کامپیوتر از راه دور - آقا محمد")
    print("=" * 60)
    print(f"📡 پورت: {PORT}")
    print(f"🔑 کلید امنیتی: {SECRET_KEY}")
    print(f"🔐 توکن احراز هویت: {AUTH_TOKEN}")
    print(f"🌐 IP عمومی: {get_public_ip()}")
    print("=" * 60)
    print("⚠️  برای توقف سرور، Ctrl+C را فشار دهید")
    print("=" * 60)
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n⛔ سرور متوقف شد.")

if __name__ == '__main__':
    main()