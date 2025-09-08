# remote_control_server.py - ذخیره و اجرای این فایل روی کامپیوتر شما
import os
import sys
import time
import ctypes
import socket
import struct
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# تنظیمات - این مقادیر را مطابق نیاز تغییر دهید
SECRET_KEY = "my_secure_password_123"  # باید با کلید در Worker یکسان باشد
AUTH_TOKEN = "home_computer_token_456"  # توکن احراز هویت
PORT = 5000  # پورت سرور
MAC_ADDRESS = "D8-FE-E3-2F-CB-17"  # آدرس MAC کامپیوتر شما (برای Wake-on-LAN)
BROADCAST_IP = "192.168.1.255"  # آدرس broadcast شبکه شما

def send_wake_on_lan():
    """ارسال بسته Wake-on-Lan برای روشن کردن کامپیوتر"""
    try:
        # تبدیل آدرس MAC به فرمت مناسب
        mac_bytes = bytes.fromhex(MAC_ADDRESS.replace(':', '').replace('-', ''))
        
        # ساخت بسته Magic Packet
        magic_packet = b'\xff' * 6 + mac_bytes * 16
        
        # ایجاد socket و ارسال بسته
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, (BROADCAST_IP, 9))  # پورت 9 برای Wake-on-LAN
        
        print("Wake-on-LAN packet sent successfully")
        return True
    except Exception as e:
        print(f"Error sending Wake-on-LAN: {e}")
        return False

def shutdown_computer(delay=0):
    time.sleep(delay)
    if os.name == 'nt':  # برای ویندوز
        os.system('shutdown /s /f /t 0')
    elif os.name == 'posix':  # برای لینوکس و مک
        os.system('shutdown -h now')

def restart_computer(delay=0):
    time.sleep(delay)
    if os.name == 'nt':  # برای ویندوز
        os.system('shutdown /r /f /t 0')
    elif os.name == 'posix':  # برای لینوکس و مک
        os.system('reboot')

def sleep_computer(delay=0):
    time.sleep(delay)
    if os.name == 'nt':  # برای ویندوز
        ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
    elif os.name == 'posix':  # برای لینوکس و مک
        if sys.platform == 'darwin':  # مک
            os.system('pmset sleepnow')
        else:  # لینوکس
            os.system('systemctl suspend')

@app.route('/control', methods=['POST'])
def control_computer():
    try:
        # بررسی احراز هویت از طریق هدر
        auth_header = request.headers.get('X-Auth-Token')
        if not auth_header or auth_header != AUTH_TOKEN:
            return jsonify({"status": "error", "message": "Unauthorized: Invalid token"}), 401
        
        # بررسی کلید امنیتی از بدنه درخواست
        data = request.get_json()
        if not data or data.get('key') != SECRET_KEY:
            return jsonify({"status": "error", "message": "Unauthorized: Invalid key"}), 401
        
        action = data.get('action')
        delay = data.get('delay', 0)
        
        if action == 'shutdown':
            threading.Thread(target=shutdown_computer, args=(delay,)).start()
            return jsonify({"status": "success", "message": "Shutdown command sent"})
        elif action == 'restart':
            threading.Thread(target=restart_computer, args=(delay,)).start()
            return jsonify({"status": "success", "message": "Restart command sent"})
        elif action == 'sleep':
            threading.Thread(target=sleep_computer, args=(delay,)).start()
            return jsonify({"status": "success", "message": "Sleep command sent"})
        elif action == 'wake':
            # ارسال دستور Wake-on-LAN
            success = send_wake_on_lan()
            if success:
                return jsonify({"status": "success", "message": "Wake-on-LAN command sent"})
            else:
                return jsonify({"status": "error", "message": "Failed to send Wake-on-LAN"})
        else:
            return jsonify({"status": "error", "message": "Invalid action"}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "service": "remote-computer-control",
        "timestamp": time.time()
    })

def main():
    print("=" * 50)
    print("سرور کنترل کامپیوتر از راه دور")
    print("=" * 50)
    print(f"در حال اجرا روی پورت: {PORT}")
    print(f"کلید امنیتی: {SECRET_KEY}")
    print(f"توکن احراز هویت: {AUTH_TOKEN}")
    print(f"آدرس MAC برای Wake-on-LAN: {MAC_ADDRESS}")
    print("=" * 50)
    print("برای توقف سرور، Ctrl+C را فشار دهید")
    print("=" * 50)
    
    try:
        # اجرای سرور (برای تولید از waitress یا gunicorn استفاده کنید)
        app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nسرور متوقف شد.")

if __name__ == '__main__':
    main()