import subprocess
import os
import xml.etree.ElementTree as ET
import winreg
import re
from time import sleep

def netsh_method():
    try:
        profiles = subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.PIPE).decode('utf-8', errors='ignore')
        wifi_names = [line.split(":")[1].strip() for line in profiles.split("\n") if "All User Profile" in line]
        passwords = []
        for name in wifi_names:
            try:
                result = subprocess.check_output(
                    f'netsh wlan show profile name="{name}" key=clear',
                    shell=True,
                    stderr=subprocess.PIPE
                ).decode('utf-8', errors='ignore')
                if "Key Content" in result:
                    password = re.search(r"Key Content\s*:\s*(.*)", result).group(1).strip()
                    passwords.append(f"{name}: {password}")
            except:
                continue
        if passwords:
            with open("wifi_passwords.txt", "w", encoding='utf-8') as f:
                f.write("\n".join(passwords))
            return True
    except:
        pass
    return False

def xml_method():
    try:
        wifi_path = r"C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces"
        if not os.path.exists(wifi_path):
            return False
        passwords = []
        for root, _, files in os.walk(wifi_path):
            for file in files:
                if file.endswith(".xml"):
                    try:
                        tree = ET.parse(os.path.join(root, file))
                        name = tree.find('.//name').text
                        password = tree.find('.//keyMaterial').text
                        passwords.append(f"{name}: {password}")
                    except:
                        continue
        if passwords:
            with open("wifi_passwords.txt", "w", encoding='utf-8') as f:
                f.write("\n".join(passwords))
            return True
    except:
        pass
    return False

def credman_method():
    try:
        output = subprocess.check_output("cmdkey /list", shell=True, stderr=subprocess.PIPE).decode('utf-8', errors='ignore')
        wifi_creds = [line.strip() for line in output.split("\n") if "Wireless" in line]
        if wifi_creds:
            with open("wifi_passwords.txt", "w", encoding='utf-8') as f:
                f.write("\n".join(wifi_creds))
            return True
    except:
        pass
    return False

def registry_method():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles")
        passwords = []
        for i in range(winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                name = winreg.QueryValueEx(subkey, "Description")[0]
                passwords.append(f"{name}: [Password requires Admin]")
            except:
                continue
        if passwords:
            with open("wifi_passwords.txt", "w", encoding='utf-8') as f:
                f.write("\n".join(passwords))
            return True
    except:
        pass
    return False

def check_success():
    return os.path.exists("wifi_passwords.txt") and os.path.getsize("wifi_passwords.txt") > 0

if __name__ == "__main__":
    methods = [netsh_method, xml_method, credman_method, registry_method]
    success = False
    
    for method in methods:
        if method():
            success = True
            break
    
    if success and check_success():
        sleep(1)  # Ensure file is written
        exit()  # Close on success
    else:
        print("Failed to extract passwords. Try running as Admin.")
        sleep(5)  # Stay open for 5 sec on failure