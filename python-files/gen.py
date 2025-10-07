import sys
import os
import hashlib
import platform
import time
from time import sleep
import random
import string
import json as jsond # Usado como alias para evitar conflicto con KeyAuth SDK
import re
import socket
import binascii 
import subprocess 
import uuid 
import asyncio
import requests
import httpx
import base64
import tls_client
import hmac
from datetime import datetime, timezone, timedelta, UTC
from dateutil.parser import isoparse
from colorama import Fore, Style, init
from pystyle import Colorate, Colors, Center
import websocket
from notifypy import Notify
import pyautogui as ca
import pyautogui as ca
import os
import sys
import asyncio
import requests
import zendriver as zd
import random
import string
import json
import re
import socket
import httpx
import base64
import tls_client
import time
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from dateutil.parser import isoparse
from colorama import Fore, Style, init
from pystyle import Colorate, Colors, Center
import websocket
from notifypy import Notify


# Importaciones de librerías opcionales/Windows
try:
    import win32security  
    # Si usas estas, asegúrate de que están instaladas
    # import qrcode
    # from discord_interactions import verify_key
    # from PIL import Image
except ImportError:
    pass
# Si usas zendriver, asegúrate de tenerlo instalado.
try:
    import zendriver as zd
except ImportError:
    pass

init(autoreset=True)

# --------------------------------------------------------------------------
# --- 1. CONFIGURACIÓN, VARIABLES Y FUNCIONES BÁSICAS (Cargadas de funcion de generador.py) ---
# --------------------------------------------------------------------------

# Variables globales de configuración
USE_HUMANIZER = False
USE_VPN = False 
WEBHOOK_URL = ""
incognito_domain = "vorlentis.xyz"

# Carga de la configuración y API de correo
try:
    with open('config.json', 'r') as f:
        config = jsond.load(f)
except FileNotFoundError:
    config = {}

incognito_api_url = config.get("mail_api", "https://api.incognitomail.co/")
incognito_domain = config.get("mail_domain", "vorlentis.xyz")
    
# Funciones Helper (clear, log, etc.)
def set_console_title(title="DedSec Token Gen"):
    if platform.system() == 'Windows':
        os.system(f'title {title}')
    else:
        sys.stdout.write(f"\033]0;{title}\007")
        sys.stdout.flush() 

def clear():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def vertical_gradient(lines, start_rgb=(0, 255, 200), end_rgb=(0, 100, 180)):
    total = len(lines)
    result = []
    for i, line in enumerate(lines):
        r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i // max(1, total - 1)
        g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i // max(1, total - 1)
        b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i // max(1, total - 1)
        result.append(f'\033[38;2;{r};{g};{b}m{line}\033[0m')
    return result

def print_ascii_logo():
    ascii_art = [
        r"""

 ______ ___________  _____ _____ _____   _____  _____ _   _ 
|  _  \  ___|  _  \/  ___|  ___/  __ \ |  __ \|  ___| \ | |
| | | | |__ | | | |\ `--.| |__ | /  \/ | |  \/| |__ |  \| |
| | | |  __|| | | | `--. \  __|| |     | | __ |  __|| . ` |
| |/ /| |___| |/ / /\__/ / |___| \__/\ | |_\ \| |___| |\  |
___/ \____/|___/  \____/\____/ \____/  \____/\____/\_| \_/
                                                           
                                                           
                                      
                                      
                                      


"""
    ]

    print('\n' * 2)
    gradient_lines = vertical_gradient(ascii_art)
    for colored_line in gradient_lines:
        print(Center.XCenter(colored_line))
    print('\n' * 2)

def log(type, message):
    now = datetime.now().strftime("%H:%M:%S")
    type_map = {
        "SUCCESS": Fore.GREEN + Style.BRIGHT + "SUCCESS" + Style.RESET_ALL,
        "ERROR": Fore.RED + Style.BRIGHT + "ERROR" + Style.RESET_ALL,
        "INFO": Fore.CYAN + Style.BRIGHT + "INFO" + Style.RESET_ALL,
        "WARNING": Fore.YELLOW + Style.BRIGHT + "WARNING" + Style.RESET_ALL
    }
    tag = type_map.get(type.upper(), type.upper())
    
    # Lógica mejorada para que los mensajes INFO/SUCCESS sean más expresivos
    final_message = message
    if type.upper() == "INFO":
        final_message = f"{Style.BRIGHT}{message}{Style.RESET_ALL}" # Usamos BRIGHT para que se vea más fuerte
    elif type.upper() == "SUCCESS":
        # Le damos un color brillante al mensaje de éxito
        final_message = f"{Style.BRIGHT + Fore.LIGHTGREEN_EX}{message}{Style.RESET_ALL}" 
    elif ':' in message:
        # Intenta un formato clave:valor si el mensaje lo contiene
        parts = message.split(':', 1)
        key = parts[0].upper().strip()
        val = parts[1].strip()
        final_message = f"{Style.BRIGHT}{Fore.MAGENTA}{key}:{Style.RESET_ALL} {val}" # Key en magenta brillante

    print(f"{Fore.LIGHTBLACK_EX}{now}{Style.RESET_ALL} - {tag} • {final_message}")

def get_webhook():
    global WEBHOOK_URL
    webhook = config.get("webhook", "")
    if webhook:
        log("INFO", f"Webhook cargado: {webhook[:30]}...")
        time.sleep(0.5)
        clear()
        print_ascii_logo()
        WEBHOOK_URL = webhook
        return webhook
    
    webhook = input(f"{Fore.CYAN}[?] Ingresa la URL del webhook de Discord: {Style.RESET_ALL}").strip()
    config["webhook"] = webhook
    with open('config.json', 'w') as f:
        jsond.dump(config, f, indent=4)
    log("SUCCESS", "Webhook guardado en config!")
    time.sleep(0.5)
    clear()
    print_ascii_logo()
    WEBHOOK_URL = webhook
    return webhook

def get_user_input(prompt, valid_options=["yes", "no", "y", "n"]):
    while True:
        try:
            response = input(f"{Fore.CYAN}[+] {prompt}: {Style.RESET_ALL}").strip().lower()
            if response in valid_options:
                return response
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            pass

def print_config_logo():
    ascii_art = [
        r"""


  /$$$$$$   /$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$  /$$$$$$ 
 /$$__  $$ /$$__  $$| $$$ | $$| $$_____/|_  $$_/ /$$__  $$      discord.gg/DedSec
| $$  \__/| $$  \ $$| $$$$| $$| $$        | $$  | $$  \__/       DedSec.dev (Soon)
| $$      | $$  | $$| $$ $$ $$| $$$$$     | $$  | $$ /$$$$        
| $$      | $$  | $$| $$  $$$$| $$__/     | $$  | $$|_  $$              t.me/DedSec
| $$    $$| $$  | $$| $$\  $$$| $$        | $$  | $$  \ $$
|  $$$$$$/|  $$$$$$/| $$ \  $$| $$       /$$$$$$|  $$$$$$/
 \______/  \______/ |__/  \__/|__/      |______/ \______/ 
                                                          
                                 V 2.5                         
                                                          
                                      
                Configuracion de DedSec Gen.              
                                      


"""
    ]

    print('\n' * 2)
    gradient_lines = vertical_gradient(ascii_art)
    for colored_line in gradient_lines:
        print(Center.XCenter(colored_line))
    print('\n' * 2)

def configure_user_options():
    global USE_HUMANIZER, USE_VPN
    
    print_config_logo()
    
    humanizer_choice = get_user_input("Usar Humanizer (y/n)")
    USE_HUMANIZER = humanizer_choice in ["yes", "y"]
    
    vpn_choice = get_user_input("Usas VPN (y/n)")
    USE_VPN = vpn_choice in ["yes", "y"]
    
    print(f"\n{Fore.GREEN} Configuracion Completada {Style.RESET_ALL}\n")
    time.sleep(0.5)
    clear()

def check_chrome_installation():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return True
    
    log("ERROR", "Chrome no encontrado")
    log("INFO", "Instalar desde: https://www.google.com/chrome/")
    return False

def cleanup_zendriver():
    try:
        import gc
        gc.collect()
        
        for task in asyncio.all_tasks() if hasattr(asyncio, 'all_tasks') else ():
            if not task.done() and task != asyncio.current_task():
                task.cancel()
    except Exception as e:
        log("ERROR", f"Cleanup error: {e}")
        pass

def account_ratelimit(email=None, username=None):
    # Lógica de verificación de Rate Limit (igual que en tu código)
    try:
        headers = {
            "Accept": "*/*",
            # ... (otras headers)
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            # ...
        }
        
        test_email = email if email else ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10)) + "@gmail.com"
        test_username = username if username else ''.join(random.choices(string.ascii_letters, k=8))
        
        data = {
            'email': test_email,
            'password': "TestPassword123!",
            'date_of_birth': "2000-01-01",
            'username': test_username,
            'global_name': test_username,
            'consent': True,
            'captcha_service': 'hcaptcha',
            'captcha_key': None,
            'invite': None,
            'promotional_email_opt_in': False,
            'gift_code_sku_id': None
        }
        
        req = requests.post('https://discord.com/api/v9/auth/register', json=data, headers=headers)
        try:
            resp_data = req.json()
        except Exception:
            return 1
            
        if req.status_code == 429 or 'retry_after' in resp_data:
            limit = resp_data.get('retry_after', 1)
            return int(float(limit)) + 1 if limit else 1
        else:
            return 1
    except Exception as e:
        log("ERROR", f"Rate limit check failed: {e}")
        return 1

def send_to_webhook(token, email, password, webhook_url):
    payload = {
        "content": f"**🎉 NUEVO TOKEN GENERADO 🎉**",
        "embeds": [{
            "title": "Token Generado",
            "description": f"**Email:** `{email}`\n**Password:** `{password}`\n**Token:** `{token}`",
            "color": 65280 
        }]
    }
    try:
        requests.post(webhook_url, json=payload)
        log("SUCCESS", "Token enviado al Webhook.")
    except Exception as e:
        log("ERROR", f"Fallo al enviar el webhook: {e}")


# ---------------- CLASES DEL GENERADOR DE TOKENS (Tu Código) ----------------

class IncognitoMailClient:
    def __init__(self):
        self.email = None
        self.inbox_id = None
        self.inbox_token = None
        self.session = requests.Session()
        self.secret_key = None
        self._initialize_secret()

    def _initialize_secret(self):
        scrambled = "4O)QqiTV+(U+?Vi]qe|6..Xe"
        self.secret_key = ''.join([chr(ord(c) - 2) for c in scrambled])

    def _sign_payload(self, payload: dict) -> str:
        message = jsond.dumps(payload, separators=(',', ':')).encode()
        key = self.secret_key.encode()
        return hmac.new(key, message, hashlib.sha256).hexdigest()

    def _get_random_fr_ip(self):
        return f"90.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

    # ... (métodos debug_inbox_status, create_temp_email, check_verification_email)

    async def create_temp_email(self):
        for attempt in range(1, 3):
            try:
                timestamp = int(time.time() * 1000)
                payload = {
                    "ts": timestamp,
                    "domain": incognito_domain
                }
                payload["key"] = self._sign_payload(payload)
                
                fake_ip = self._get_random_fr_ip()
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                    "X-Forwarded-For": fake_ip,
                    "X-Real-IP": fake_ip,
                    "Via": fake_ip
                }
                
                response = httpx.post(
                    f"{incognito_api_url}inbox/v2/create", 
                    json=payload, 
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and "token" in data:
                        self.inbox_id = data["id"]
                        self.inbox_token = data["token"]
                        self.email = data["id"]
                        # CAMBIO CLAVE: Print mejorado
                        log("SUCCESS", f"Correo temporal creado con éxito. 📩 {Fore.YELLOW}{self.email}{Style.RESET_ALL}")
                        return self.email
                
            except Exception as e:
                if attempt == 2:
                    log("ERROR", f"Failed to create email: {e}")
                await asyncio.sleep(2)
                    
        return None

    def check_verification_email(self):
        if not self.inbox_id or not self.inbox_token:
            return None
            
        for attempt in range(1, 30):
            try:
                ts = int(time.time() * 1000)
                payload = {
                    "inboxId": self.inbox_id,
                    "inboxToken": self.inbox_token,
                    "ts": ts
                }
                payload["key"] = self._sign_payload(payload)
                
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.post(
                    f"{incognito_api_url}inbox/v1/list", 
                    json=payload, 
                    headers=headers, 
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    if items:
                        for item in items:
                            message_url = item.get("messageURL")
                            if message_url:
                                try:
                                    email_data = requests.get(message_url, timeout=5).json()
                                    subject = email_data.get("subject", "")
                                    
                                    if "verify" in subject.lower():
                                        content = str(email_data.get("text", "")) + str(email_data.get("html", ""))
                                        
                                        patterns = [
                                            r'https:\/\/click\.discord\.com[^\s"\'\'<>\\]+',
                                            r'https://click\.discord\.com[^\s"\'\'<>\\]+',
                                            r'https://discord\.com/verify[^\s"\'\'<>\\]+'
                                        ]
                                        
                                        for pattern in patterns:
                                            match = re.search(pattern, content)
                                            if match:
                                                link = match.group(0).replace('\\/', '/').split("\n")[0].strip()
                                                link = link.replace('&amp;', '&')
                                                log("SUCCESS", f"{Style.BRIGHT + Fore.MAGENTA}¡ENLACE ENCONTRADO! 🚀 Iniciando Verificación...{Style.RESET_ALL}")
                                                return link
                                except:
                                    continue
                    
            except:
                pass
            
            time.sleep(3.0)  # Slowed down from 0.5
        
        log("ERROR", "Verification email not received")
        return None


class BrowserManager:
    def __init__(self):
        self.browser = None

    async def start(self, url):
        # Asegúrate de que zendriver esté disponible si vas a usarlo
        if 'zd' not in sys.modules:
             log("ERROR", "Zendriver no está importado/instalado. No se puede iniciar el navegador.")
             return None

        self.browser = await zd.start()
            
        page = await self.browser.get(url)
        await page.wait_for_ready_state('complete', timeout=30000)
        
        # Press enter after page loads
        ca.press('enter')
        await asyncio.sleep(0.1)
                
        log("SUCCESS", "Registration page opened")
        return page

    async def stop(self):
        if self.browser:
            try:
                await asyncio.wait_for(self.browser.stop(), timeout=5.0)
            except asyncio.TimeoutError:
                log("WARNING", "Browser stop timed out")
            except Exception as e:
                log("ERROR", f"Browser stop error: {e}")
            finally:
                self.browser = None
                log("SUCCESS", "Browser terminated")

class DiscordHumanizer:
    def __init__(self):
        self.config = self.load_config()
        self.customization = self.config.get("CustomizationSettings", {})
        self.load_data_files()
        self.session = tls_client.Session(client_identifier="chrome_115", random_tls_extension_order=True)

    def load_config(self):
        try:
            with open("config.json", "r", encoding="utf-8") as file:
                return jsond.load(file) # Usamos jsond para evitar conflictos
        except Exception as e:
            log("ERROR", f"Failed to load config.json: {e}")
            return {}

    def load_data_files(self):
        try:
            # Lógica de carga de archivos de personalización (pronouns, bios, etc.)
            if self.customization.get("Pronouns", False):
                with open("data/pronouns.txt", "r", encoding="utf-8") as f:
                    self.pronouns = [line.strip() for line in f if line.strip()]
            
            if self.customization.get("Bio", False):
                with open("data/bios.txt", "r", encoding="utf-8") as f:
                    self.bios = [line.strip() for line in f if line.strip()]
            
            if self.customization.get("DisplayName", False):
                with open("data/displays.txt", "r", encoding="utf-8") as f:
                    self.names = [line.strip() for line in f if line.strip()]
            
            if self.customization.get("Avatar", False):
                if not os.path.exists("avatar"):
                    os.makedirs("avatar")
                self.avatars = [f for f in os.listdir("avatar") if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

        except Exception as e:
            log("ERROR", f"Failed to load data files: {e}")

    def go_online(self, token):
        # Lógica de Gateway para poner el token online
        try:
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=6&encoding=json')
            hello = jsond.loads(ws.recv())
            heartbeat_interval = hello['d']['heartbeat_interval'] / 1000
            status = random.choice(['online', 'dnd', 'idle'])
            activity_type = random.choice(['Playing', 'Streaming', 'Watching', 'Listening', ''])
            
            if activity_type == "Playing": gamejson = {"name": "EV GEN", "type": 0}
            elif activity_type == 'Streaming': gamejson = {"name": "EV GEN", "type": 1, "url": "https://twitch.tv/c_mposee"}
            elif activity_type == "Listening": gamejson = {"name": random.choice(["EV GEN", "EV GEN"]), "type": 2}
            elif activity_type == "Watching": gamejson = {"name": "EV GEN", "type": 3}
            else: gamejson = None
                
            auth = {
                "op": 2, "d": { "token": token,
                    "properties": { "$os": "windows", "$browser": "Chrome", "$device": "Windows" },
                    "presence": {
                        "activities": [gamejson] if gamejson else [],
                        "status": status, "since": 0, "afk": False
                    }
                }
            }
            ws.send(jsond.dumps(auth))
            return ws, heartbeat_interval
        except Exception as e:
            log("ERROR", f"WebSocket Error: {e}")
            return None, None

    def set_offline(self, ws):
        # Lógica para poner el token offline
        try:
            if ws:
                offline_payload = { "op": 3, "d": { "status": "invisible", "since": 0, "activities": [], "afk": False } }
                ws.send(jsond.dumps(offline_payload))
                time.sleep(1)
        except Exception as e:
            log("ERROR", f"Error setting offline: {e}")

    async def humanize_account(self, token, email, password):
        if not USE_HUMANIZER: return True
        log("INFO", f"HUMANIZING TOKEN : {token[:12]}...")
        try:
            ws, _ = self.go_online(token)
            if any([self.customization.get("Pronouns"), self.customization.get("DisplayName"), self.customization.get("Bio"), self.customization.get("HypeSquad")]):
                await self.update_profile_fields(token)
            
            # if self.customization.get("Avatar", False) and self.avatars:
            #     avatar_path = os.path.join("avatar", random.choice(self.avatars))
            #     self.update_avatar(token, avatar_path) # Esta función no está en el snippet, se omite.
            
            if ws: self.set_offline(ws)
            log("SUCCESS", f"FINISHED HUMANIZING TOKEN : {token[:12]}...")
            return True
        except Exception as e:
            log("ERROR", f"Failed to humanize account: {str(e)}")
            return False

    async def update_profile_fields(self, token):
        # Lógica para actualizar campos del perfil de Discord
        headers = { 
            # ... (headers)
            "authorization": token,
            # ...
        }
        
        payload = {}
        
        if self.customization.get("DisplayName", False) and hasattr(self, 'names'):
            global_name = random.choice(self.names)
            payload = {"global_name": global_name}
            try:
                response = self.session.patch(
                    "https://discord.com/api/v9/users/@me", headers=headers, json=payload
                )
                if response.status_code == 200:
                    log("SUCCESS", f"GLOBAL NAME UPDATED : {global_name}")
                else:
                    log("ERROR", f"FAILED TO UPDATE GLOBAL NAME : {response.text}")
            except Exception as e:
                log("ERROR", f"Exception updating global name: {str(e)}")
            
            payload = {} # Resetear payload para el siguiente PATCH/POST
        
        # Agregamos pronombres y bio al payload si están configurados
        if self.customization.get("Pronouns", False) and hasattr(self, 'pronouns'):
            payload["pronouns"] = random.choice(self.pronouns)
        
        if self.customization.get("Bio", False) and hasattr(self, 'bios'):
            payload["bio"] = random.choice(self.bios)
            
        if payload:
            url = "https://discord.com/api/v9/users/@me/profile"
            try:
                response = self.session.patch(url, headers=headers, json=payload)
                # Manejo de la respuesta...
            except Exception as e:
                log("ERROR", f"Exception updating profile fields: {str(e)}")


# --------------------------------------------------------------------------
# --- 2. CORE DEL SDK DE KEYAUTH (Reutilizado del código anterior) ---
# --------------------------------------------------------------------------

class User: 
    def __init__(self):
        self.username = None
        self.ip = None
        self.hwid = None
        self.createdate = None
        self.lastlogin = None
        self.subscriptions = []
        self.expires = None
        
class others:
    @staticmethod
    def get_hwid():
        # Lógica de HWID (igual que en el código anterior)
        if platform.system() == "Linux":
            with open("/etc/machine-id") as f:
                hwid = f.read().strip()
                return hwid
        elif platform.system() == 'Windows' and 'win32security' in sys.modules:
            try:
                winuser = os.getlogin()
                sid = win32security.LookupAccountName(None, winuser)[0] 
                hwid = win32security.ConvertSidToStringSid(sid)
                return hwid
            except Exception:
                cmd = subprocess.Popen("wmic csproduct get uuid", stdout=subprocess.PIPE, shell=True)
                hwid = cmd.communicate()[0].split()[1].decode().strip()
                return hwid
        elif platform.system() == 'Darwin':
            output = subprocess.Popen("ioreg -l | grep IOPlatformSerialNumber", stdout=subprocess.PIPE, shell=True)
            hwid = output.communicate()[0].decode().split("=")[1].strip().strip('"')
            return hwid
        
        return str(uuid.getnode())

def getchecksum():
    md5_hash = hashlib.md5()
    try:
        with open(sys.argv[0], "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
    except FileNotFoundError:
        log("ERROR", "No se puede calcular el checksum del script.")
        os._exit(1)
        
    return md5_hash.hexdigest()

class api:
    def __init__(self, name, ownerid, version, hash_to_check):
        if len(ownerid) != 10:
            log("ERROR", "ID de propietario inválido.")
            time.sleep(3)
            os._exit(1)
    
        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check
        self.sessionid = ""
        self.initialized = False
        self.user_data = User()
        self.init() 
        
    def __do_request(self, post_data):
        try:
            # Usar 'requests' ya que el KeyAuth SDK original lo hace
            response = requests.post("https://keyauth.win/api/1.2/", data=post_data, verify=True)
            return response.text
        except Exception as e:
            log("ERROR", f"Error de conexión con KeyAuth: {e}")
            time.sleep(3)
            os._exit(1)
            
    def __load_user_data(self, data):
        self.user_data.username = data["username"]
        self.user_data.ip = data["ip"]
        self.user_data.hwid = data["hwid"] or "N/A"
        self.user_data.subscriptions = data["subscriptions"]
        
        if data["subscriptions"]:
            self.user_data.expires = data["subscriptions"][0]["expiry"]
        else:
            self.user_data.expires = "N/A"
            
        self.user_data.createdate = data["createdate"]
        self.user_data.lastlogin = data["lastlogin"]

    def checkinit(self):
        if not self.initialized:
            log("ERROR", "Debe llamar a init() primero!")
            time.sleep(3)
            os._exit(1)

    def init(self):
        # Lógica de init (igual que en el código anterior)
        if self.sessionid != "":
            log("ERROR", "Ya has inicializado!")
            time.sleep(3)
            os._exit(1)
        
        post_data = {
            "type": "init", "ver": self.version, "hash": self.hash_to_check,
            "name": self.name, "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)
        if response == "KeyAuth_Invalid":
            log("ERROR", "La aplicación no existe o el propietario es incorrecto.")
            time.sleep(3)
            os._exit(1)
        try:
            json_response = jsond.loads(response)
        except jsond.JSONDecodeError:
            log("ERROR", f"Respuesta inválida del servidor: {response[:100]}")
            time.sleep(3)
            os._exit(1)

        if json_response.get("message") == "invalidver":
            log("ERROR", "Versión Inválida. Contacta al propietario.")
            time.sleep(3)
            os._exit(1)
        if not json_response["success"]:
            log("ERROR", f"Fallo en init: {json_response['message']}")
            time.sleep(3)
            os._exit(1)

        self.sessionid = json_response["sessionid"]
        self.initialized = True
        log("SUCCESS", f"KeyAuth Initialized. Session ID: {self.sessionid[:8]}...")
        return True

    def register(self, user, password, license, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()

        post_data = {
            "type": "register", "username": user, "pass": password, "key": license, "hwid": hwid,
            "sessionid": self.sessionid, "name": self.name, "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)
        json_response = jsond.loads(response)

        if json_response["success"]:
            log("SUCCESS", f"Registro exitoso: {json_response['message']}")
            self.__load_user_data(json_response["info"])
            return True
        else:
            log("ERROR", f"Fallo en registro: {json_response['message']}")
            time.sleep(3)
            os._exit(1)

    def login(self, user, password, code=None, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()
        
        post_data = {
            "type": "login", "username": user, "pass": password, "hwid": hwid,
            "sessionid": self.sessionid, "name": self.name, "ownerid": self.ownerid
        }
        if code is not None:
            post_data["code"] = code

        response = self.__do_request(post_data)
        json_response = jsond.loads(response)

        if json_response["success"]:
            log("SUCCESS", f"Login exitoso: {json_response['message']}")
            self.__load_user_data(json_response["info"])
            return True
        else:
            log("ERROR", f"Fallo en login: {json_response['message']}")
            time.sleep(3)
            os._exit(1)

    def license(self, key, code=None, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()

        post_data = {
            "type": "license", "key": key, "hwid": hwid,
            "sessionid": self.sessionid, "name": self.name, "ownerid": self.ownerid
        }
        if code is not None:
            post_data["code"] = code

        response = self.__do_request(post_data)
        json_response = jsond.loads(response)

        if json_response["success"]:
            self.__load_user_data(json_response["info"])
            log("SUCCESS", f"Licencia exitosa: {json_response['message']}")
            return True
        else:
            log("ERROR", f"Fallo en licencia: {json_response['message']}")
            time.sleep(3)
            os._exit(1)
            
# Coloca esta función en la sección de tus funciones básicas (cerca de log o get_webhook):
def save_autologin_data(username, password):
    """Guarda las credenciales localmente para el auto-login con el mismo HWID."""
    global config
    # Nota: Usamos 'jsond' porque es el alias que usa tu código para el módulo json.
    config['autologin'] = {
        'username': username,
        'password': password
    }
    with open('config.json', 'w') as f:
        jsond.dump(config, f, indent=4)
    log("SUCCESS", "Credenciales guardadas para Auto-Login (mismo HWID).")


# --------------------------------------------------------------------------
# --- 3. FLUJO DE AUTENTICACIÓN KEYAUTH ---
# --------------------------------------------------------------------------
# Configura tus credenciales aquí:
KEYAUTH_NAME = "Faze1clapedyuu's Application"
KEYAUTH_OWNERID = "nWpyBrgm0A"
KEYAUTH_VERSION = "1.0" 

set_console_title("Inicializando KeyAuth...")
keyauthapp = api(
    name = KEYAUTH_NAME, 
    ownerid = KEYAUTH_OWNERID,
    version = KEYAUTH_VERSION,
    hash_to_check = getchecksum()
)

def answer():
    # Loop hasta que la autenticación sea exitosa
    while True:
        clear()
        
        # ------------------------------------
        # --- LÓGICA DE AUTO-LOGIN ---
        # ------------------------------------
        global config
        autologin_data = config.get('autologin')
        
        if autologin_data:
            print(Colorate.Vertical(Colors.blue_to_red, Center.Center("--- KeyAuth - Autenticación ---\n")))
            log("INFO", f"Intentando Auto-Login para usuario: {autologin_data['username']}...")
            
            try:
                # 1. Intento de Auto-Login
                if keyauthapp.login(autologin_data['username'], autologin_data['password']):
                    log("SUCCESS", "Auto-Login exitoso. Iniciando generador...")
                    sleep(1)
                    break # Éxito: salimos del bucle
                
                # 2. Si falló (ej: por 2FA o HWID cambiado), preguntamos al usuario
                log("WARNING", "Auto-Login fallido. Posiblemente por 2FA, HWID diferente o clave expirada.")
                choice = input(f"{Fore.CYAN}[?] Auto-Login fallido. ¿Intentar 2FA (t) o ir al menú principal (m)? {Style.RESET_ALL}").strip().lower()
                
                if choice == 't':
                    code = input('Ingresa código 2FA: ')
                    if keyauthapp.login(autologin_data['username'], autologin_data['password'], code):
                         log("SUCCESS", "Auto-Login (2FA) exitoso. Iniciando generador...")
                         sleep(1)
                         break # Éxito: salimos del bucle
                
                # Si falla o el usuario elige 'm', eliminamos los datos guardados y seguimos al menú.
                del config['autologin']
                with open('config.json', 'w') as f:
                    jsond.dump(config, f, indent=4)
                log("INFO", "Credenciales de Auto-Login eliminadas. Continuando al menú manual.")
                sleep(2)
                clear()
                
            except Exception as e:
                 # Si el SDK lanza una excepción (mal password, hwid no corresponde, etc.)
                 log("ERROR", f"Error durante el intento de Auto-Login: {e}. Eliminando credenciales guardadas.")
                 if 'autologin' in config:
                     del config['autologin']
                     with open('config.json', 'w') as f:
                        jsond.dump(config, f, indent=4)
                 sleep(2)
                 clear()

# ------------------------------------
        # --- LÓGICA DE MENÚ MANUAL (MÁXIMA COMPACTACIÓN) ---
        # ------------------------------------
        
        # 1. Mostrar el logo ASCII (Asumimos que esta función ya hace el print/centrado)
        # NOTA: Si tu logo tiene muchas líneas en blanco al final, debes editarlas en la función print_ascii_logo()
        print_ascii_logo() 
        
        # 3. HWID centrado (sin '\n' al final)
        hwid_display = f"Tu HWID para vinculación: {others.get_hwid()[:10]}..."
        print(Colorate.Horizontal(Colors.cyan_to_green, Center.Center(hwid_display)))
        
        try:
            # 4. Opciones del menú compactas
            # Usamos un solo string con '\n' solo para las opciones.
            menu_options = "\n1. Iniciar Sesión (Username/Pass)\n2. Registrarse (Username/Pass/License)\n3. Solo Licencia (License Key)\n"
            
            # Imprime el menú de opciones.
            print(Colorate.Diagonal(Colors.rainbow, Center.Center(menu_options)))
            
            # Input de selección de opción
            ans = input(Colorate.Horizontal(Colors.white_to_green, "Selecciona Opción: ")).strip()
            
            # --- Lógica de Manejo de Opciones ---
            if ans == "1":
                user = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Proporciona nombre de usuario: '))
                password = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Proporciona contraseña: '))
                code = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Ingresa código 2FA: (¿No usas? Pulsa Enter)')) or None
                keyauthapp.login(user, password, code) 
                save_autologin_data(user, password)
                break
            elif ans == "2":
                user = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Proporciona nombre de usuario: '))
                password = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Proporciona contraseña: '))
                license = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Proporciona Licencia: '))
                keyauthapp.register(user, password, license)
                save_autologin_data(user, password)
                break
            elif ans == "3":
                key = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Ingresa tu licencia: '))
                code = input(Colorate.Horizontal(Colors.cyan_to_blue, 'Ingresa código 2FA: (¿No usas? Pulsa Enter)')) or None
                keyauthapp.license(key, code)
                log("WARNING", "Usando Solo Licencia. No se guardarán credenciales para Auto-Login (necesitas user/pass).")
                break
            else:
                log("ERROR", "Opción inválida")
                sleep(1)
        
        except KeyboardInterrupt:
            os._exit(1)
        except Exception as e:
            # Captura el error lanzado por el SDK
            log("ERROR", f"Fallo de autenticación: {e}")
            sleep(3)
            # El bucle se reinicia, volviendo a mostrar el menú.

    # ------------------------------------
    # --- PANTALLA FINAL DE ÉXITO ---
    # ------------------------------------
    clear()
    print(Colorate.Vertical(Colors.blue_to_red, Center.Center("--- DATOS DE USUARIO ---\n")))
    print(f"Username: {keyauthapp.user_data.username}")
    
    subs = keyauthapp.user_data.subscriptions  
    for i in range(len(subs)):
        sub = subs[i]["subscription"]
        expiry = datetime.fromtimestamp(int(subs[i]["expiry"]), UTC).strftime('%Y-%m-%d %H:%M:%S')
        timeleft = "N/A" 
        print(f"[{i + 1} / {len(subs)}] | Suscripción: {sub} - Expira: {expiry} - Tiempo Restante: {timeleft}")

    print("\n" + Colorate.Horizontal(Colors.green_to_blue, "✅ Autenticación Exitosa. Presiona Enter para iniciar el Generador..."))
    input()
    clear()

# --------------------------------------------------------------------------
# --- 4. FUNCIÓN PRINCIPAL DEL GENERADOR (Tu versión) ---
# --------------------------------------------------------------------------

async def main_application_flow():
    
    set_console_title()
    clear()
    
def send_notification(title, message):
    if not config.get("notify", False):
        return
    try:
        notification = Notify()
        notification.application_name = "DedSecGenDiscord"
        notification.title = title
        notification.message = message
        icon_path = "data/pack.ico"
        if icon_path and os.path.isfile(icon_path):
            notification.icon = icon_path
        notification.send()
    except Exception as e:
        pass

def log(type, message):
    if type.upper() in ["SUCCESS", "ERROR"]:
        now = datetime.now().strftime("%H:%M:%S")
        type_map = {
            "SUCCESS": Fore.GREEN + "SUCCESS" + Style.RESET_ALL,
            "ERROR": Fore.RED + "ERROR" + Style.RESET_ALL
        }
        tag = type_map.get(type.upper(), type.upper())
        print(f"{Fore.LIGHTBLACK_EX}{now}{Style.RESET_ALL} - {tag} • {message}")

def clear():
    
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
def account_ratelimit(email=None, username=None):
    try:
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json",
            "DNT": "1",
            "Host": "discord.com",
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/register",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-GPC": "1",
            "TE": "trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "America/New_York",
        }
        
        test_email = email if email else ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10)) + "@gmail.com"
        test_username = username if username else ''.join(random.choices(string.ascii_letters, k=8))
        
        data = {
            'email': test_email,
            'password': "TestPassword123!",
            'date_of_birth': "2000-01-01",
            'username': test_username,
            'global_name': test_username,
            'consent': True,
            'captcha_service': 'hcaptcha',
            'captcha_key': None,
            'invite': None,
            'promotional_email_opt_in': False,
            'gift_code_sku_id': None
        }
        
        req = requests.post('https://discord.com/api/v9/auth/register', json=data, headers=headers)
        try:
            resp_data = req.json()
        except Exception:
            return 1
            
        if req.status_code == 429 or 'retry_after' in resp_data:
            limit = resp_data.get('retry_after', 1)
            return int(float(limit)) + 1 if limit else 1
        else:
            return 1
    except Exception as e:
        log("ERROR", f"Rate limit check failed: {e}")
        return 1

def log(type, message):
    now = datetime.now().strftime("%H:%M:%S")
    type_map = {
        "SUCCESS": Fore.GREEN + "SUCCESS" + Style.RESET_ALL,
        "ERROR": Fore.RED + "ERROR" + Style.RESET_ALL,
        "INFO": Fore.CYAN + "INFO" + Style.RESET_ALL,
        "WARNING": Fore.YELLOW + "WARNING" + Style.RESET_ALL
    }
    tag = type_map.get(type.upper(), type.upper())

    if type.upper() == "INFO":
        message = f"{Fore.LIGHTBLACK_EX}{message}{Style.RESET_ALL}"
    elif ':' in message:
        parts = message.split(':', 1)
        key = parts[0].upper().strip()
        val = parts[1].strip()
        message = f"{key}: {Fore.LIGHTBLACK_EX}{val}{Style.RESET_ALL}"

    print(f"{Fore.LIGHTBLACK_EX}{now}{Style.RESET_ALL} - {tag} • {message}")

def get_device_id():
    return socket.gethostname()

def set_console_title(title="DedSec Token Gen"):
    if os.name == 'nt':
        os.system(f"title {title}")
    else:
        print(f"\33]0;{title}\a", end='', flush=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def cleanup_zendriver():
    try:
        import gc
        gc.collect()
        
        for task in asyncio.all_tasks() if hasattr(asyncio, 'all_tasks') else ():
            if not task.done() and task != asyncio.current_task():
                task.cancel()
    except Exception as e:
        log("ERROR", f"Cleanup error: {e}")
        pass

def vertical_gradient(lines, start_rgb=(0, 255, 200), end_rgb=(0, 100, 180)):
    total = len(lines)
    result = []
    for i, line in enumerate(lines):
        r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i // max(1, total - 1)
        g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i // max(1, total - 1)
        b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i // max(1, total - 1)
        result.append(f'\033[38;2;{r};{g};{b}m{line}\033[0m')
    return result

def print_ascii_logo():
    ascii_art = [
        r"""

 ______ ___________  _____ _____ _____   _____  _____ _   _ 
|  _  \  ___|  _  \/  ___|  ___/  __ \ |  __ \|  ___| \ | |
| | | | |__ | | | |\ `--.| |__ | /  \/ | |  \/| |__ |  \| |
| | | |  __|| | | | `--. \  __|| |     | | __ |  __|| . ` |
| |/ /| |___| |/ / /\__/ / |___| \__/\ | |_\ \| |___| |\  |
|___/ \____/|___/  \____/\____/ \____/  \____/\____/\_| \_/
                                                           
                                                           
                                      
                                      
                                      



"""
    ]

    print('\n' * 2)
    gradient_lines = vertical_gradient(ascii_art)
    for colored_line in gradient_lines:
        print(Center.XCenter(colored_line))
    print('\n' * 2)

def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def random_username():
    return 'DedSec' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def get_user_input(prompt, valid_options=["yes", "no", "y", "n"]):
    while True:
        try:
            response = input(f"{Fore.CYAN}[+] {prompt}: {Style.RESET_ALL}").strip().lower()
            if response in valid_options:
                return response
        except KeyboardInterrupt:
            exit(0)
        except Exception as e:
            pass

def print_config_logo():
    ascii_art = [
        r"""


  /$$$$$$   /$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$  /$$$$$$ 
 /$$__  $$ /$$__  $$| $$$ | $$| $$_____/|_  $$_/ /$$__  $$      discord.gg/DedSec
| $$  \__/| $$  \ $$| $$$$| $$| $$        | $$  | $$  \__/       DedSec.dev (Soon)
| $$      | $$  | $$| $$ $$ $$| $$$$$     | $$  | $$ /$$$$        
| $$      | $$  | $$| $$  $$$$| $$__/     | $$  | $$|_  $$              t.me/DedSec
| $$    $$| $$  | $$| $$\  $$$| $$        | $$  | $$  \ $$
|  $$$$$$/|  $$$$$$/| $$ \  $$| $$       /$$$$$$|  $$$$$$/
 \______/  \______/ |__/  \__/|__/      |______/ \______/ 
                                                          
                                 V 2.5                         
                                                          
                                      
                Configuracion de DedSec Gen.              
                                      



"""
    ]

    print('\n' * 2)
    gradient_lines = vertical_gradient(ascii_art)
    for colored_line in gradient_lines:
        print(Center.XCenter(colored_line))
    print('\n' * 2)

                                                          
                                                          
def configure_user_options():
    global USE_HUMANIZER, USE_VPN
    
    print_config_logo()
    
    humanizer_choice = get_user_input("Usar IA? (y/n)")
    USE_HUMANIZER = humanizer_choice in ["yes", "y"]
    
    vpn_choice = get_user_input("Usas VPN (y/n)")
    USE_VPN = vpn_choice in ["yes", "y"]
    
    print(f"\n{Fore.GREEN} Configuracion Completada {Style.RESET_ALL}\n")
    time.sleep(0.5)
    clear()
    


async def validate_license_key(license_key: str):
    return True

class IncognitoMailClient:
    def __init__(self):
        self.email = None
        self.inbox_id = None
        self.inbox_token = None
        self.session = requests.Session()
        self.secret_key = None
        self._initialize_secret()

    def _initialize_secret(self):
        scrambled = "4O)QqiTV+(U+?Vi]qe|6..Xe"
        self.secret_key = ''.join([chr(ord(c) - 2) for c in scrambled])

    def _sign_payload(self, payload: dict) -> str:
        message = json.dumps(payload, separators=(',', ':')).encode()
        key = self.secret_key.encode()
        return hmac.new(key, message, hashlib.sha256).hexdigest()

    def _get_random_fr_ip(self):
        return f"90.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"

    def debug_inbox_status(self):
        if not self.inbox_id or not self.inbox_token:
            log("ERROR", "No inbox credentials for debugging")
            return False
            
        try:
            ts = int(time.time() * 1000)
            payload = {
                "inboxId": self.inbox_id,
                "inboxToken": self.inbox_token,
                "ts": ts
            }
            payload["key"] = self._sign_payload(payload)
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.post(
                f"{incognito_api_url}inbox/v1/list", 
                json=payload, 
                headers=headers, 
                timeout=10
            )
            
            log("INFO", f"API Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                log("INFO", f"Inbox accessible, {len(items)} emails found")
                
                for i, item in enumerate(items[:3]):
                    log("INFO", f"Email {i+1}: messageURL present = {bool(item.get('messageURL'))}")
                    
                return True
            else:
                log("ERROR", f"API Error: {response.text[:100]}")
                return False
                
        except Exception as e:
            log("ERROR", f"Exception: {e}")
            return False

    async def create_temp_email(self):
        for attempt in range(1, 3):
            try:
                timestamp = int(time.time() * 1000)
                payload = {
                    "ts": timestamp,
                    "domain": incognito_domain
                }
                payload["key"] = self._sign_payload(payload)
                
                fake_ip = self._get_random_fr_ip()
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                    "X-Forwarded-For": fake_ip,
                    "X-Real-IP": fake_ip,
                    "Via": fake_ip
                }
                
                response = httpx.post(
                    f"{incognito_api_url}inbox/v2/create", 
                    json=payload, 
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and "token" in data:
                        self.inbox_id = data["id"]
                        self.inbox_token = data["token"]
                        self.email = self.inbox_id
                        log("SUCCESS", f"Email created: {self.email}")
                        return self.email
                
            except Exception as e:
                if attempt == 2:
                    log("ERROR", f"Failed to create email: {e}")
                await asyncio.sleep(2)
                    
        return None

    def check_verification_email(self):
        if not self.inbox_id or not self.inbox_token:
            return None
            
        for attempt in range(1, 30):
            try:
                ts = int(time.time() * 1000)
                payload = {
                    "inboxId": self.inbox_id,
                    "inboxToken": self.inbox_token,
                    "ts": ts
                }
                payload["key"] = self._sign_payload(payload)
                
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                response = requests.post(
                    f"{incognito_api_url}inbox/v1/list", 
                    json=payload, 
                    headers=headers, 
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    if items:
                        for item in items:
                            message_url = item.get("messageURL")
                            if message_url:
                                try:
                                    email_data = requests.get(message_url, timeout=5).json()
                                    subject = email_data.get("subject", "")
                                    
                                    if "verify" in subject.lower():
                                        content = str(email_data.get("text", "")) + str(email_data.get("html", ""))
                                        
                                        patterns = [
                                            r'https:\/\/click\.discord\.com[^\s"\'\'<>\\]+',
                                            r'https://click\.discord\.com[^\s"\'\'<>\\]+',
                                            r'https://discord\.com/verify[^\s"\'\'<>\\]+'
                                        ]
                                        
                                        for pattern in patterns:
                                            match = re.search(pattern, content)
                                            if match:
                                                link = match.group(0).replace('\\/', '/').split("\n")[0].strip()
                                                link = link.replace('&amp;', '&')
                                                log("SUCCESS", "Verification link found")
                                                return link
                                except:
                                    continue
                    
            except:
                pass
            
            time.sleep(3.0)  # Slowed down from 0.5
        
        log("ERROR", "Verification email not received")
        return None

def check_chrome_installation():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME', '')),
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            return True
    
    log("ERROR", "Chrome not found")
    log("INFO", "Install from: https://www.google.com/chrome/")
    return False

class BrowserManager:
    def __init__(self):
        self.browser = None

    async def start(self, url):
        self.browser = await zd.start()
            
        page = await self.browser.get(url)
        await page.wait_for_ready_state('complete', timeout=30000)
        
        # Press enter after page loads
        ca.press('enter')
        await asyncio.sleep(0.1)
                
        log("SUCCESS", "Registration page opened")
        return page

    async def stop(self):
        if self.browser:
            try:
                await asyncio.wait_for(self.browser.stop(), timeout=5.0)
            except asyncio.TimeoutError:
                log("WARNING", "Browser stop timed out")
            except Exception as e:
                log("ERROR", f"Browser stop error: {e}")
            finally:
                self.browser = None
                log("SUCCESS", "Browser terminated")

class DiscordHumanizer:
    def __init__(self):
        self.config = self.load_config()
        self.customization = self.config.get("CustomizationSettings", {})
        self.load_data_files()
        self.session = tls_client.Session(client_identifier="chrome_115", random_tls_extension_order=True)

    def load_config(self):
        try:
            with open("config.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            log("ERROR", f"Failed to load config.json: {e}")
            return {}

    def load_data_files(self):
        try:
            if self.customization.get("Pronouns", False):
                with open("data/pronouns.txt", "r", encoding="utf-8") as f:
                    self.pronouns = [line.strip() for line in f if line.strip()]
            
            if self.customization.get("Bio", False):
                with open("data/bios.txt", "r", encoding="utf-8") as f:
                    self.bios = [line.strip() for line in f if line.strip()]
            
            if self.customization.get("DisplayName", False):
                with open("data/displays.txt", "r", encoding="utf-8") as f:
                    self.names = [line.strip() for line in f if line.strip()]
            
            if self.customization.get("Avatar", False):
                if not os.path.exists("avatar"):
                    os.makedirs("avatar")
                self.avatars = [f for f in os.listdir("avatar") if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

        except Exception as e:
            log("ERROR", f"Failed to load data files: {e}")

    def go_online(self, token):
        try:
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=6&encoding=json')
            hello = json.loads(ws.recv())
            heartbeat_interval = hello['d']['heartbeat_interval'] / 1000

            status = random.choice(['online', 'dnd', 'idle'])
            activity_type = random.choice(['Playing', 'Streaming', 'Watching', 'Listening', ''])

            if activity_type == "Playing":
                gamejson = {"name": "EV GEN", "type": 0}
            elif activity_type == 'Streaming':
                gamejson = {"name": "EV GEN", "type": 1, "url": "https://twitch.tv/c_mposee"}
            elif activity_type == "Listening":
                gamejson = {"name": random.choice(["EV GEN", "EV GEN"]), "type": 2}
            elif activity_type == "Watching":
                gamejson = {"name": "EV GEN", "type": 3}
            else:
                gamejson = None

            auth = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "$os": "windows",
                        "$browser": "Chrome",
                        "$device": "Windows"
                    },
                    "presence": {
                        "activities": [gamejson] if gamejson else [],
                        "status": status,
                        "since": 0,
                        "afk": False
                    }
                }
            }
            ws.send(json.dumps(auth))
            return ws, heartbeat_interval
        except Exception as e:
            log("ERROR", f"WebSocket Error: {e}")
            return None, None

    def set_offline(self, ws):
        try:
            if ws:
                offline_payload = {
                    "op": 3,
                    "d": {
                        "status": "invisible",
                        "since": 0,
                        "activities": [],
                        "afk": False
                    }
                }
                ws.send(json.dumps(offline_payload))
                time.sleep(1)
        except Exception as e:
            log("ERROR", f"Error setting offline: {e}")

    async def humanize_account(self, token, email, password):
        if not USE_HUMANIZER:
            return True

        log("INFO", f"HUMANIZING TOKEN : {token[:12]}...")
        
        try:
            ws, _ = self.go_online(token)
            
            if any([self.customization.get("Pronouns"), self.customization.get("DisplayName"), 
                   self.customization.get("Bio"), self.customization.get("HypeSquad")]):
                await self.update_profile_fields(token)

            if self.customization.get("Avatar", False) and self.avatars:
                avatar_path = os.path.join("avatar", random.choice(self.avatars))
                self.update_avatar(token, avatar_path)

            if ws:
                self.set_offline(ws)

            log("SUCCESS", f"FINISHED HUMANIZING TOKEN : {token[:12]}...")
            return True
        except Exception as e:
            log("ERROR", f"Failed to humanize account: {str(e)}")
            return False

    async def update_profile_fields(self, token):
        headers = {
            "authority": "discord.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": token,
            "content-type": "application/json",
            "origin": "https://discord.com",
            "referer": "https://discord.com/channels/@me",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzExNi4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTE2LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwLjAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUxNDQxLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
        }
        
        if self.customization.get("DisplayName", False) and self.names:
            global_name = random.choice(self.names)
            payload = {"global_name": global_name}
            try:
                response = self.session.patch(
                    "https://discord.com/api/v9/users/@me",
                    headers=headers,
                    json=payload
                )
                if response.status_code == 200:
                    log("SUCCESS", f"GLOBAL NAME UPDATED : {global_name}")
                else:
                    log("ERROR", f"FAILED TO UPDATE GLOBAL NAME : {response.text}")
            except Exception as e:
                log("ERROR", f"Exception updating global name: {str(e)}")
        
        payload = {}
        
        if self.customization.get("Pronouns", False) and self.pronouns:
            payload["pronouns"] = random.choice(self.pronouns)
        
        if self.customization.get("Bio", False) and self.bios:
            payload["bio"] = random.choice(self.bios)
        
        if payload:
            url = "https://discord.com/api/v9/users/@me/profile"
            try:
                response = self.session.patch(url, headers=headers, json=payload)
                if response.status_code == 200:
                    log("SUCCESS", "PROFILE FIELDS UPDATED SUCCESSFULLY")
                else:
                    log("ERROR", f"FAILED TO UPDATE PROFILE FIELDS : {response.text}")
            except Exception as e:
                log("ERROR", f"Exception updating profile fields: {str(e)}")
        
        if self.customization.get("HypeSquad", False):
            house_ids = {"bravery": 1, "brilliance": 2, "balance": 3}
            house = random.choice(list(house_ids.keys()))
            hypesquad_payload = {"house_id": house_ids[house]}
            url = "https://discord.com/api/v9/hypesquad/online"
            
            try:
                response = self.session.post(url, headers=headers, json=hypesquad_payload)
                if response.status_code == 204:
                    log("SUCCESS", f"HYPESQUAD UPDATED : {house.capitalize()}")
                else:
                    log("ERROR", f"FAILED TO UPDATE HYPESQUAD : {response.text}")
            except Exception as e:
                log("ERROR", f"Exception updating HypeSquad: {str(e)}")

    def update_avatar(self, token, image_path):
        try:
            if not os.path.exists(image_path):
                log("ERROR", f"AVATAR IMAGE NOT FOUND : {image_path}")
                return False

            with open(image_path, "rb") as f:
                img_data = f.read()
                ext = os.path.splitext(image_path)[1].lower().replace('.', '')
                mime_type = "image/gif" if ext == "gif" else f"image/{'jpeg' if ext == 'jpg' else ext}"
                b64 = base64.b64encode(img_data).decode()
                avatar_data = f"data:{mime_type};base64,{b64}"

            headers = {
                "authorization": token,
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwLjAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUxNDQxLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
            }

            payload = {"avatar": avatar_data}

            response = self.session.patch(
                "https://discord.com/api/v9/users/@me",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                log("SUCCESS", f"Avatar Updated : {os.path.basename(image_path)}")
                return True
            else:
                log("ERROR", f"Avatar Update Failed : {response.text}")
                return False
        except Exception as silk:
            log("ERROR", f"Update Avatar Exception : {str(silk)}")
            return False

class DiscordFormFiller:
    def __init__(self, account_number=1):
        self.mail_client = IncognitoMailClient()
        self.browser_mgr = BrowserManager()
        self.humanizer = DiscordHumanizer()
        self.password = None
        self.email = None
        self.token = None
        self.account_number = account_number

    async def fill_form(self):
        try:
            send_notification("Generacion De Cuenta", "Generando nueva Cuenta")
            email = await self.mail_client.create_temp_email()
            if not email:
                send_notification("Error", "Failed to create temporary email")
                log("ERROR", "Failed to create email")
                return None
            self.email = email
            try:
                page = await self.browser_mgr.start("https://discord.com/register")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log("ERROR", f"Failed to start browser: {e}")
                return None
            try:
                await self._fill_basic_fields(page, email)
                await self._select_birth_date(page, quick=True)
                log("SUCCESS", "Fields filled!")
                await self._wait_for_captcha_completion(page)
                token = await self._verify_email()
                await self.browser_mgr.stop()
                if token:
                    send_notification("Success", f"Account: {token[:12]}...")
                    # Set DND status and s.jpg avatar
                    await self.set_dnd_and_avatar(token)
                    # Log to webhook
                    await self.log_to_webhook(token)
                    return token
                else:
                    send_notification("Error", "Failed to complete account verification")
                    return None
            except asyncio.CancelledError:
                log("INFO", "Form filling cancelled")
                raise
            except Exception as e:
                log("ERROR", f"Form filling failed: {e}")
                try:
                    await self.browser_mgr.stop()
                except Exception:
                    pass
                return None
        except asyncio.CancelledError:
            log("INFO", "Account generation cancelled")
            try:
                await self.browser_mgr.stop()
            except Exception:
                pass
            raise
        except Exception as e:
            log("ERROR", f"Account generation failed: {e}")
            try:
                await self.browser_mgr.stop()
            except Exception:
                pass
            return None

    async def set_dnd_and_avatar(self, token):
        # Set DND status
        try:
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=6&encoding=json')
            hello = json.loads(ws.recv())
            heartbeat_interval = hello['d']['heartbeat_interval'] / 1000
            presence = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "$os": "windows",
                        "$browser": "Chrome",
                        "$device": "Windows"
                    },
                    "presence": {
                        "activities": [],
                        "status": "dnd",
                        "since": 0,
                        "afk": False
                    }
                }
            }
            ws.send(json.dumps(presence))
            log("SUCCESS", "Set DND status!")
        except Exception as e:
            log("ERROR", f"Failed to set DND status: {e}")
        try:
            avatar_path = os.path.join("avatar", "s.jpg")
            self.humanizer.update_avatar(token, avatar_path)
            log("SUCCESS", "Set avatar to s.jpg!")
        except Exception as e:
            log("ERROR", f"Failed to set avatar: {e}")

    async def log_to_webhook(self, token):
        webhook_url = get_webhook()
        password = self.password or "?"
        email = self.email or "?"
        if "@" in email:
            parts = email.split("@", 1)
            email_fmt = f"{parts[0][:4]}||{parts[0][4:]}||@{parts[1]}"
        else:
            email_fmt = email
        avatar_url = "https://discord.com/channels/@me/1413190875089080350/1425099046300942468"
        embed = {
            "title": "Nueva cuenta Generada",
            "color": 0x00bfff,
            "fields": [
                {"name": "🔑 Token", "value": f"`||{token}||`", "inline": False},
                {"name": "🔐 Password", "value": f"||{password}||", "inline": True},
                {"name": "📩 Email", "value": f"{email_fmt}", "inline": True}
            ],
            "thumbnail": {"url": avatar_url},
            "footer": {"text": ".gg/GenDedSec"}
        }
        data = {
            "username": "gg/GenDedSec",
            "avatar_url": avatar_url,
            "embeds": [embed]
        }
        try:
            import requests
            resp = requests.post(webhook_url, json=data)
            if resp.status_code in [200, 204]:
                log("SUCCESS", "Logged to webhook!")
            else:
                log("ERROR", f"Webhook log failed: {resp.text}")
        except Exception as e:
            log("ERROR", f"Webhook log exception: {e}")

    async def set_random_dnd_status(self, token):
        try:
            status_file = os.path.join("data", "status.txt")
            if not os.path.exists(status_file):
                log("ERROR", "data/status.txt not found!")
                return
            with open(status_file, "r", encoding="utf-8") as f:
                statuses = [line.strip() for line in f if line.strip()]
            if not statuses:
                log("ERROR", "No statuses found in data/status.txt!")
                return
            chosen_status = random.choice(statuses)
            ws = websocket.WebSocket()
            ws.connect('wss://gateway.discord.gg/?v=6&encoding=json')
            hello = json.loads(ws.recv())
            heartbeat_interval = hello['d']['heartbeat_interval'] / 1000
            presence = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {
                        "$os": "windows",
                        "$browser": "Chrome",
                        "$device": "Windows"
                    },
                    "presence": {
                        "activities": [{"name": chosen_status, "type": 0}],
                        "status": "dnd",
                        "since": 0,
                        "afk": False
                    }
                }
            }
            ws.send(json.dumps(presence))
            log("SUCCESS", f"Set DND status: {chosen_status}")
            # Keep status forever
            while True:
                ws.send(json.dumps({"op": 1, "d": None}))
                time.sleep(heartbeat_interval)
        except Exception as e:
            log("ERROR", f"Failed to set DND status: {e}")

    async def _countdown_timer(self, duration):
        for i in range(duration):
            remaining = duration - i
            log("INFO", f"Waiting... {remaining}s remaining")
            await asyncio.sleep(1)

    async def _fill_basic_fields(self, page, email):
        # Press enter first when loading the page
        ca.press('enter')
        await asyncio.sleep(0.1)
        
        display_name = ".gg/DedSec"
        username = random_username()
        password = self.mail_client.inbox_token
        
        if not password:
            password = "SUSHISILK$" + generate_random_string(8) + "@7836"

        email_field = await page.wait_for('input[name="email"]', timeout=15000)
        await email_field.send_keys(self.mail_client.inbox_id)
        await asyncio.sleep(0.05)

        display_name_field = await page.wait_for('input[name="global_name"]', timeout=15000)
        await display_name_field.send_keys(display_name)
        await asyncio.sleep(0.05)

        username_field = await page.wait_for('input[name="username"]', timeout=15000)
        await username_field.send_keys(username)
        await asyncio.sleep(0.05)

        password_field = await page.wait_for('input[name="password"]', timeout=15000)
        await password_field.send_keys(password)
        
        self.password = password
        self.email = self.mail_client.inbox_id

    async def _select_birth_date(self, page, quick=False):
        try:
            # Faster birthday selection if quick=True
            sleep = (lambda s: asyncio.sleep(s/2)) if quick else asyncio.sleep
            await sleep(0.5)
            ca.press('tab')
            await sleep(0.2)
            ca.press('space')
            await sleep(0.2)
            ca.press('enter')
            await sleep(0.5)
            ca.press('tab')
            await sleep(0.2)
            ca.press('space')
            await sleep(0.5)
            ca.press('enter')
            await sleep(0.5)
            ca.press('tab')
            await sleep(0.2)
            ca.press('space')
            await sleep(0.2)
            for _ in range(20):
                ca.press('down')
                await sleep(0.05)
            await sleep(1.0)
            ca.press('enter')
            await sleep(0.5)
            # Click the register button directly
            try:
                await page.evaluate('''
                    (function() {
                        const selectors = [
                            'button[type="submit"]',
                            'button[class*="button"]',
                            'button'
                        ];
                        for (let i = 0; i < selectors.length; i++) {
                            const selector = selectors[i];
                            const buttons = document.querySelectorAll(selector);
                            for (let j = 0; j < buttons.length; j++) {
                                const button = buttons[j];
                                if (button.offsetParent !== null && !button.disabled) {
                                    const text = button.textContent.toLowerCase();
                                    if (text.includes('register') || text.includes('sign up') || text.includes('continue') || text.includes('next')) {
                                        button.click();
                                        return true;
                                    }
                                }
                            }
                        }
                        return false;
                    })();
                ''')
            except Exception:
                ca.press('enter')
            await sleep(1.0)
        except Exception:
            pass

    async def _wait_for_captcha_completion(self, page):
        try:
            captcha_detected = False
            attempt = 0
            while True:
                try:
                    captcha_elements = [
                        'iframe[src*="hcaptcha"]',
                        'iframe[src*="recaptcha"]', 
                        'div[class*="captcha"]',
                        '.h-captcha',
                        '.g-recaptcha',
                        '[data-sitekey]'
                    ]
                    
                    captcha_found = False
                    for selector in captcha_elements:
                        captcha = await page.query_selector(selector)
                        if captcha:
                            captcha_found = True
                            break
                    
                    if captcha_found and not captcha_detected:
                        log("INFO", "Waiting for you to solve captcha...")
                        send_notification("Captcha", "Please solve the CAPTCHA manually")
                        captcha_detected = True
                    
                    if not captcha_found:
                        if captcha_detected:
                            log("SUCCESS", "Captcha solved successfully!")
                            send_notification("Success", "CAPTCHA solved, continuing...")
                        return True
                    
                    await asyncio.sleep(1.0)  # Slowed down from 0.2
                    attempt += 1
                        
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass
                    
        except asyncio.CancelledError:
            log("INFO", "Captcha wait cancelled")
            raise
        except Exception as e:
            log("WARNING", f"Captcha wait error: {e}")
            return True

    def get_token(self, inbox_id=None, inbox_token=None):
        try:
            login_id = inbox_id or self.mail_client.inbox_id
            login_password = inbox_token or self.mail_client.inbox_token
            
            if not login_id or not login_password:
                return None
                
            payload = {
                'login': login_id,
                'password': login_password
            }
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Origin': 'https://discord.com',
                'Referer': 'https://discord.com/login'
            }
            
            res = requests.post('https://discord.com/api/v9/auth/login', json=payload, headers=headers)
            
            if res.status_code == 200:
                try:
                    response_data = res.json()
                    if 'token' in response_data:
                        token = response_data['token']
                        log("SUCCESS", f"Token: {token[:12]}...")
                        
                        os.makedirs("silk_output", exist_ok=True)
                        
                        with open("silk_output/tokens.txt", "a", encoding="utf-8") as tf:
                            tf.write(f"{login_id}:{login_password}:{token}\n")
                        
                        with open("silk_output/logins.txt", "a", encoding="utf-8") as af:
                            af.write(f"{login_id}:{login_password}:{token}\n")
                        
                        self.token = token
                        return token
                except json.JSONDecodeError:
                    pass
                
        except Exception:
            pass
        return None

    def check_email_verified_api(self, token):
        url = "https://discord.com/api/v9/users/@me"
        headers = {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwLjAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MjUxNDQxLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
        }
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                verified = data.get("verified", False)
                email = data.get("email", "No Email")
                return verified, email
            else:
                return None, None
        except:
            return None, None

    async def _verify_email(self):
        for attempt in range(150):
            try:
                verification_link = self.mail_client.check_verification_email()
                if verification_link:
                    break
                await asyncio.sleep(1.0)
            except asyncio.CancelledError:
                log("INFO", "Verification check cancelled")
                return None
            except Exception:
                pass
        
        if not verification_link:
            return None

        verification_browser = None
        try:
            log("SUCCESS", "Opening verification link...")
            verification_browser = await zd.start()
            page = await verification_browser.get(verification_link)
            await asyncio.sleep(1.0)

            token = None
            for check_attempt in range(80):
                try:
                    token = self.get_token(self.mail_client.inbox_id, self.mail_client.inbox_token)
                    if token:
                        break
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    log("INFO", "Token check cancelled")
                    return None
                except Exception:
                    pass

            if not token:
                return None

            verification_complete = False
            
            for verify_attempt in range(300):
                try:
                    verified, email_address = self.check_email_verified_api(token)
                    if verified:
                        verification_complete = True
                        log("SUCCESS", "Email verified successfully!")
                        break
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    log("INFO", "Email verification cancelled")
                    return None
                except Exception:
                    pass
            
            if not verification_complete:
                return None
                
            if USE_HUMANIZER and self.humanizer.config.get("Humanize", False):
                try:
                    await self.humanizer.humanize_account(
                        token, 
                        self.mail_client.inbox_id, 
                        self.mail_client.inbox_token
                    )
                    log("SUCCESS", "Account humanized successfully")
                except asyncio.CancelledError:
                    log("INFO", "Humanization cancelled")
                except Exception as e:
                    log("ERROR", f"Humanization failed: {e}")
            
            return token
            
        except asyncio.CancelledError:
            log("INFO", "Verification process cancelled")
            return None
        except Exception as e:
            log("ERROR", f"Verification error: {e}")
            return None
        finally:
            if verification_browser:
                try:
                    await asyncio.wait_for(verification_browser.stop(), timeout=3.0)
                except:
                    pass

async def main():
    clear_screen()
    set_console_title()
    
    if not check_chrome_installation():
        log("ERROR", "Chrome not installed")
        input("Press Enter to exit...")
        return
    
    configure_user_options()
    print_ascii_logo()
    
    try:
        amt = int(input(f"{Fore.CYAN}[?] Amount of accounts: {Style.RESET_ALL}"))
    except ValueError:
        amt = 1
    
    run_count = 0
    
    try:
        while True:
            if amt != 0 and run_count >= amt:
                break
                
            run_count += 1
            log("SUCCESS", f"Starting account {run_count} generation...")
            
            try:
                filler = DiscordFormFiller(account_number=run_count)
                token = await filler.fill_form()
                
                if token:
                    log("SUCCESS", "Account created successfully")
                else:
                    log("ERROR", f"Account {run_count} generation failed")
            except asyncio.CancelledError:
                log("INFO", "Generation task cancelled")
                break
            except Exception as e:
                log("ERROR", f"Error generating account: {e}")
            
            if amt == 1:
                break
            elif amt != 0 and run_count >= amt:
                break
            else:
                wait_time = 30 if USE_VPN else 200  
                
                # Mensaje de inicio de la espera con más estilo
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}*** ⏸️ INICIANDO PAUSA ({wait_time} segundos) ***{Style.RESET_ALL}")
                log("INFO", f"Modo de espera: {'VPN' if USE_VPN else 'IP Local'} ☕")
                
                try:
                    # Contador visual con efecto de movimiento (refresco de línea)
                    for i in range(wait_time, 0, -1):
                        # \r hace que la línea se reescriba, creando el efecto de "movimiento"
                        sys.stdout.write(f"\r{Fore.YELLOW}⏳ Próxima generación en: {Fore.WHITE}{Style.BRIGHT}{i}{Fore.YELLOW} segundos...{Style.RESET_ALL}")
                        sys.stdout.flush()
                        await asyncio.sleep(1)
                    
                    # Mensaje final de reanudación
                    print(f"\r{Fore.GREEN}✔️ Reanudando la generación de cuentas... ¡Listo!{Style.RESET_ALL}   ") # Los espacios al final limpian la línea anterior.
                
                except asyncio.CancelledError:
                    break
                
    except KeyboardInterrupt:
        log("SUCCESS", "Exiting...")
    except asyncio.CancelledError:
        log("INFO", "Main task cancelled")
    except Exception as e:
        log("ERROR", f"Generation error: {e}")
    finally:
        cleanup_zendriver()
        log("SUCCESS", "Finished generating tokens!")


# --------------------------------------------------------------------------
# --- 5. PUNTO DE ENTRADA (Flow de autenticación primero) ---
# --------------------------------------------------------------------------
if __name__ == '__main__':
    # 1. Autenticación KeyAuth. Bloquea la ejecución hasta que sea exitosa.
    answer() 
    
    # 2. Iniciar el programa principal asíncrono SOLO si la autenticación fue exitosa
    try:
        # Llamamos a 'main()' que contiene toda tu lógica de generación.
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario. Saliendo...")
    except asyncio.CancelledError:
        print("\nAsyncio tasks were cancelled. Saliendo...")
    except Exception as e:
        print(f"\nError inesperado: {e}")