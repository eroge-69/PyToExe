import requests
import base64
import urllib3
import os
import time
import json
import jwt
from urllib.parse import quote
from datetime import datetime
import subprocess
import pyautogui
import pygetwindow as gw
import dns.resolver
import logging

urllib3.disable_warnings()


logging.basicConfig(filename="bot.log", level=logging.INFO, encoding="utf-8")

api_key = "HDEV-b0154b8f-cfda-479e-8d00-3b7a553aeaa9"

# Koordinatlar (ekran çözünürlüğünüze göre doğrulayın)
USERNAME_FIELD = (130, 265)  # Kullanıcı adı alanı
PASSWORD_FIELD = (160, 331)  # Şifre alanı
LOGIN_BUTTON = (198, 685)    # Giriş butonu


country_to_region = {
    "and": "eu", "are": "eu", "afg": "eu", "atg": "latam", "aia": "latam", "alb": "eu", "arm": "eu",
    "ago": "eu", "ata": "eu", "arg": "latam", "asm": "ap", "aut": "eu", "aus": "ap", "abw": "latam",
    "ala": "eu", "aze": "eu", "bih": "eu", "brb": "latam", "bgd": "ap", "bel": "eu", "bfa": "eu",
    "bgr": "eu", "bhr": "eu", "bdi": "eu", "ben": "eu", "blm": "eu", "bmu": "latam", "brn": "ap",
    "bol": "latam", "bes": "latam", "bra": "br", "bhs": "latam", "btn": "ap", "bvt": "eu", "bwa": "eu",
    "blr": "eu", "blz": "latam", "can": "na", "cck": "ap", "cod": "eu", "caf": "eu", "cog": "eu",
    "che": "eu", "civ": "eu", "cok": "eu", "chl": "latam", "cmr": "eu", "chn": "ap", "col": "latam",
    "cri": "latam", "cub": "latam", "cpv": "eu", "cuw": "eu", "cxr": "ap", "cyp": "eu", "cze": "eu",
    "deu": "eu", "dji": "eu", "dnk": "eu", "dma": "latam", "dom": "latam", "dza": "eu", "ecu": "latam",
    "est": "eu", "egy": "eu", "esh": "eu", "eri": "eu", "esp": "eu", "eth": "eu", "fin": "eu",
    "fji": "ap", "flk": "latam", "fsm": "ap", "fro": "eu", "fra": "eu", "gab": "eu", "gbr": "eu",
    "grd": "latam", "geo": "eu", "guf": "eu", "ggy": "eu", "gha": "eu", "gib": "eu", "grl": "eu",
    "gmb": "eu", "gin": "eu", "glp": "eu", "gnq": "eu", "grc": "eu", "sgs": "latam", "gtm": "latam",
    "gum": "ap", "gnb": "eu", "guy": "latam", "hkg": "ap", "hmd": "eu", "hnd": "latam", "hrv": "eu",
    "hti": "latam", "hun": "eu", "idn": "ap", "irl": "eu", "isr": "eu", "imn": "eu", "ind": "ap",
    "iot": "ap", "irq": "eu", "irn": "eu", "isl": "eu", "ita": "eu", "jey": "eu", "jam": "latam",
    "jor": "eu", "jpn": "ap", "ken": "eu", "kgz": "eu", "khm": "ap", "kir": "ap", "com": "eu",
    "kna": "latam", "prk": "ap", "kor": "kr", "kwt": "eu", "cym": "latam", "kaz": "eu", "lao": "ap",
    "lbn": "eu", "lca": "latam", "lie": "eu", "lka": "ap", "lbr": "eu", "lso": "eu", "ltu": "eu",
    "lux": "eu", "lva": "eu", "lby": "eu", "mar": "eu", "mco": "eu", "mda": "eu", "mne": "eu",
    "maf": "eu", "mdg": "eu", "mhl": "ap", "mkd": "eu", "mli": "eu", "mmr": "ap", "mng": "ap",
    "mac": "ap", "mnp": "ap", "mtq": "eu", "mrt": "eu", "msr": "latam", "mlt": "eu", "mus": "eu",
    "mdv": "ap", "mwi": "eu", "mex": "latam", "mys": "ap", "moz": "eu", "nam": "eu", "ncl": "eu",
    "ner": "eu", "nfk": "ap", "nga": "eu", "nic": "latam", "nld": "eu", "nor": "eu", "npl": "ap",
    "nru": "ap", "niu": "ap", "nzl": "ap", "omn": "eu", "pan": "latam", "per": "latam", "pyf": "eu",
    "png": "ap", "phl": "ap", "pak": "ap", "pol": "eu", "spm": "eu", "pcn": "ap", "pri": "latam",
    "pse": "eu", "prt": "eu", "plw": "ap", "pry": "latam", "qat": "eu", "reu": "eu", "rou": "eu",
    "srb": "eu", "rus": "eu", "rwa": "eu", "sau": "eu", "slb": "ap", "syc": "eu", "sdn": "eu",
    "swe": "eu", "sgp": "ap", "shn": "eu", "svn": "eu", "sjm": "eu", "svk": "eu", "sle": "eu",
    "smr": "eu", "sen": "eu", "som": "eu", "sur": "latam", "ssd": "eu", "stp": "eu", "slv": "latam",
    "sxm": "eu", "syr": "eu", "swz": "eu", "tca": "latam", "tcd": "eu", "atf": "eu", "tgo": "eu",
    "tha": "ap", "tjk": "eu", "tkl": "ap", "tls": "ap", "tkm": "eu", "tun": "eu", "ton": "ap",
    "tur": "eu", "tto": "latam", "tuv": "ap", "twn": "ap", "tza": "eu", "ukr": "eu", "uga": "eu",
    "umi": "ap", "usa": "na", "ury": "latam", "uzb": "eu", "vat": "eu", "vct": "latam", "ven": "latam",
    "vgb": "latam", "vir": "latam", "vnm": "ap", "vut": "ap", "wlf": "eu", "wsm": "ap", "yem": "eu",
    "myt": "eu", "zaf": "eu", "zmb": "eu", "zwe": "eu"
}



def get_region_from_dat(dat, country="unknown"):
    region_map = {
        "NA1": "na", "EUW1": "eu", "EUN1": "eu", "BR1": "br", "KR": "kr",
        "AP1": "ap", "LA1": "latam", "LA2": "latam", "OC1": "ap", "TR1": "eu",
        "JP1": "ap", "RU": "eu", "ME1": "eu"
    }
    cluster_map = {
        "na1": "na", "br1": "br", "kr": "kr", "ap1": "ap", "la1": "latam",
        "la2": "latam", "oc1": "ap", "tr1": "eu", "ru1": "eu", "jp1": "ap", "me1": "eu"
    }

    try:
        url = f"https://api.henrikdev.xyz/valorant/v1/account/{quote(dat.get('game_name', ''))}/{quote(dat.get('tag_line', ''))}"
        res = requests.get(url, headers={"Authorization": api_key}, timeout=5)
        if res.status_code == 200 and "region" in res.json().get("data", {}):
            region = res.json()["data"]["region"]
            logging.info(f"Bölge alındı: {region}")
            return region
        logging.warning(f"Bölge alınamadı: HTTP {res.status_code} - {res.text}")
    except Exception as e:
        logging.error(f"Bölge doğrulaması başarısız: {e}")

    token_region = None
    if dat.get("r") and dat['r'] in region_map:
        token_region = region_map[dat['r']]
        logging.info(f"Token'dan bölge alındı (r): {token_region}")
    elif dat.get("c") and dat['c'] in cluster_map:
        token_region = cluster_map[dat['c']]
        logging.info(f"Token'dan bölge alındı (c): {token_region}")
    
    if country.lower() in country_to_region:
        country_region = country_to_region[country.lower()]
        if token_region and token_region != country_region:
            logging.warning(f"Bölge tutarsızlığı: Token bölgesi ({token_region}) ile ülke bölgesi ({country_region}) farklı.")
        logging.info(f"Ülke kodundan bölge alındı: {country_region}")
        return country_region

    try:
        ip_info = requests.get("http://ip-api.com/json/", timeout=5).json()
        if ip_info.get("status") == "success" and ip_info.get("countryCode"):
            country_code = ip_info["countryCode"].lower()
            ip_region = country_to_region.get(country_code, "eu")
            if token_region and token_region != ip_region:
                logging.warning(f"Bölge tutarsızlığı: Token bölgesi ({token_region}) ile IP bölgesi ({ip_region}) farklı.")
            logging.info(f"IP tabanlı bölge alındı: {ip_region}")
            return ip_region
    except Exception as e:
        logging.error(f"IP tabanlı bölge tahmini başarısız: {e}")

    logging.info("Varsayılan bölge kullanıldı: eu")
    return "eu"

def flush_dns():
    try:
        subprocess.run("ipconfig /flushdns", shell=True, check=True)
        logging.info("DNS önbelleği temizlendi.")
    except Exception as e:
        logging.error(f"DNS önbelleği temizlenemedi: {e}")

def kill_riot_processes():
    try:
        for proc in ["RiotClientServices.exe", "Valorant.exe", "RiotClientCrashHandler.exe"]:
            result = subprocess.run(f"taskkill /IM {proc} /F", shell=True, check=False, capture_output=True, text=True)
            if result.returncode == 0:
                logging.info(f"{proc} sonlandırıldı.")
            elif "not found" not in result.stderr.lower():
                logging.warning(f"{proc} sonlandırılamadı: {result.stderr}")
        logging.info("Tüm Riot süreçleri sonlandırıldı.")
    except Exception as e:
        logging.error(f"Riot süreçleri sonlandırılamadı: {e}")

def start_riot_client():
    try:
        riot_path = r"C:\Riot Games\Riot Client\RiotClientServices.exe"
        if not os.path.exists(riot_path):
            raise FileNotFoundError(f"Riot Client executable bulunamadı: {riot_path}")
        subprocess.Popen([riot_path, "--launch-product=valorant"])
        time.sleep(10)
        logging.info("Riot Client başlatıldı.")
        return True
    except Exception as e:
        logging.error(f"Riot Client başlatılamadı: {e}")
        return False

def login_to_riot_client(username, password):
    try:
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.2

        time.sleep(5)
        windows = gw.getWindowsWithTitle("Riot Client") or gw.getWindowsWithTitle("Riot") or gw.getWindowsWithTitle("Riot Client Main")
        if not windows:
            logging.warning("Riot Client penceresi bulunamadı. Olası pencere başlıkları kontrol ediliyor...")
            for win in gw.getAllTitles():
                if "riot" in win.lower():
                    logging.info(f"Bulunan pencere başlığı: {win}")
                    windows = gw.getWindowsWithTitle(win)
                    break
            if not windows:
                logging.error("Hala pencere bulunamadı.")
                return False
        
        window = windows[0]
        try:
            window.resizeTo(1280, 720)
            window.moveTo(0, 0)
            window.maximize()
            time.sleep(0.5)
            window.activate()
            time.sleep(1)
            logging.info("Riot Client penceresi maksimize edildi ve aktifleştirildi.")
        except Exception as e:
            logging.error(f"Pencere maksimize/aktifleştirme hatası: {e}")
            return False

        pyautogui.click(USERNAME_FIELD[0], USERNAME_FIELD[1])
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        logging.info(f"Kullanıcı adı yazılıyor: {username}")
        pyautogui.write(username, interval=0.1)
        time.sleep(0.5)

        pyautogui.click(PASSWORD_FIELD[0], PASSWORD_FIELD[1])
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        logging.info(f"Şifre yazılıyor: {password[:3]}...")
        pyautogui.write(password, interval=0.1)
        time.sleep(0.5)

        logging.info("Giriş butonuna basılıyor.")
        pyautogui.click(LOGIN_BUTTON[0], LOGIN_BUTTON[1])
        time.sleep(10)
        return True
    except Exception as e:
        logging.error(f"Giriş işlemi yapılamadı: {e}")
        return False

def refresh_token_if_needed(tokens, lockfile_path):
    try:
        decoded = jwt.decode(tokens["access_token"], options={"verify_signature": False})
        exp = decoded.get("exp", 0)
        current_time = int(time.time())
        if exp - current_time < 300:  # Token 5 dakika içinde bitecekse yenile
            logging.info("Token süresi dolmak üzere, yenileniyor...")
            with open(lockfile_path, "r") as f:
                content = f.read()
                lockfile = content.split(":")
                if len(lockfile) != 5:
                    logging.warning(f"Lockfile formatı hatalı: {lockfile}")
                    return tokens
                port, password = lockfile[2], lockfile[3]
            
            basic_auth = base64.b64encode(f"riot:{password}".encode()).decode()
            headers = {"Authorization": f"Basic {basic_auth}"}
            response = requests.get(f"https://127.0.0.1:{port}/entitlements/v1/token", headers=headers, verify=False, timeout=5)
            if response.status_code == 200:
                data = response.json()
                tokens["access_token"] = data.get("accessToken", tokens["access_token"])
                tokens["entitlements_token"] = data.get("token", tokens["entitlements_token"])
                logging.info("Token yenilendi.")
            else:
                logging.warning(f"Token yenileme başarısız: HTTP {response.status_code} - {response.text}")
        return tokens
    except Exception as e:
        logging.error(f"Token yenileme hatası: {e}")
        return tokens

def get_tokens_from_lockfile():
    lockfile_path = os.path.join(os.environ["LOCALAPPDATA"], "Riot Games", "Riot Client", "Config", "lockfile")
    retries = 3
    for attempt in range(retries):
        try:
            if not os.path.exists(lockfile_path):
                logging.warning(f"Lockfile bulunamadı: {lockfile_path}")
                time.sleep(2)
                continue

            with open(lockfile_path, "r") as f:
                content = f.read()
                logging.info(f"Lockfile içeriği: {content}")
                lockfile = content.split(":")
                
                if len(lockfile) != 5:
                    logging.warning(f"Lockfile formatı hatalı: {lockfile}")
                    time.sleep(2)
                    continue
                
                port, password = lockfile[2], lockfile[3]
            
            basic_auth = base64.b64encode(f"riot:{password}".encode()).decode()
            headers = {"Authorization": f"Basic {basic_auth}"}
            response = requests.get(f"https://127.0.0.1:{port}/entitlements/v1/token", headers=headers, verify=False, timeout=5)
            
            if response.status_code != 200:
                logging.warning(f"Token alınamadı: HTTP {response.status_code} - {response.text}")
                time.sleep(2)
                continue
            
            data = response.json()
            logging.info(f"Token API yanıtı: {data}")
            if "accessToken" not in data or "token" not in data or "subject" not in data:
                logging.warning(f"Token yanıtı eksik: {data}")
                time.sleep(2)
                continue
            
            access_token = data["accessToken"]
            entitlements_token = data["token"]
            puuid = data["subject"]
            
            decoded = jwt.decode(access_token, options={"verify_signature": False})
            dat = decoded.get("dat", {})
            
            user_name, tag, country, email_verified, phone_verified = get_user_info({"access_token": access_token})
            if not user_name or not tag:
                logging.warning("Kullanıcı bilgileri alınamadı, tekrar deneniyor...")
                time.sleep(2)
                continue
                
            region = get_region_from_dat({"r": dat.get("r"), "c": dat.get("c"), 
                                         "game_name": user_name, "tag_line": tag}, country)
            
            tokens = {
                "access_token": access_token,
                "entitlements_token": entitlements_token,
                "puuid": puuid,
                "region": region,
                "game_name": user_name,
                "tag_line": tag,
                "email_verified": email_verified,
                "phone_verified": phone_verified
            }
            
            tokens = refresh_token_if_needed(tokens, lockfile_path)
            return tokens
        except Exception as e:
            logging.error(f"Token alınırken hata (deneme {attempt + 1}/{retries}): {e}")
            time.sleep(2)
    logging.error("lockfile bulunamadı veya token alınamadı.")
    return None

def get_client_headers():
    try:
        version = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientVersion"]
        platform = base64.b64encode(b'{"platformType":"PC","platformOS":"Windows","platformOSVersion":"10.0.19042.1.256.64bit","platformChipset":"Unknown"}').decode()
        logging.info("Client headers alındı.")
        return version, platform
    except Exception as e:
        logging.error(f"Client headers alınırken hata: {e}")
        return None, None

def get_user_info(tokens):
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Content-Type": "application/json"
    }
    try:
        res = requests.get("https://auth.riotgames.com/userinfo", headers=headers, verify=False, timeout=5)
        if res.status_code == 200:
            data = res.json()
            logging.info(f"Kullanıcı bilgisi API yanıtı: {data}")
            game_name = data["acct"].get("game_name", "Bilinmeyen")
            tag_line = data["acct"].get("tag_line", "Bilinmeyen")
            country = data.get("country", "unknown")
            email_verified = data.get("email_verified", False)
            phone_verified = data.get("phone_number_verified", False)
            return game_name, tag_line, country, email_verified, phone_verified
        logging.warning(f"Kullanıcı bilgileri alınamadı: HTTP {res.status_code} - {res.text}")
        return None, None, None, False, False
    except Exception as e:
        logging.error(f"Kullanıcı bilgileri alınırken hata: {e}")
        return None, None, None, False, False

def get_account_level(puuid, tokens, region, version, platform):
    region_endpoints = {
        "na": "pd.na.a.pvp.net",
        "eu": "pd.eu.a.pvp.net",
        "br": "pd.na.a.pvp.net",
        "latam": "pd.na.a.pvp.net",
        "ap": "pd.ap.a.pvp.net",
        "kr": "pd.kr.a.pvp.net"
    }
    endpoint = region_endpoints.get(region, "pd.eu.a.pvp.net")
    url = f"https://{endpoint}/account-xp/v1/players/{puuid}"
    headers = {
        "X-Riot-Entitlements-JWT": tokens["entitlements_token"],
        "Authorization": f"Bearer {tokens['access_token']}",
        "X-Riot-ClientVersion": version,
        "X-Riot-ClientPlatform": platform
    }

    retries = 3
    for attempt in range(retries):
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['1.1.1.1', '1.0.0.1']
            resolver.resolve(endpoint)

            res = requests.get(url, headers=headers, verify=False, timeout=5)
            if res.status_code == 200:
                data = res.json()
                level = data.get("Progress", {}).get("Level", 1)
                if level:
                    logging.info(f"Seviye alındı: {level}")
                    return level
                logging.warning(f"Seviye bilgisi eksik: {data}")
            
            logging.warning(f"Seviye alınamadı: HTTP {res.status_code} - {res.text}")
            time.sleep(2)
        except Exception as e:
            logging.error(f"Seviye alınırken hata (deneme {attempt + 1}/{retries}): {e}")
            time.sleep(2)

    try:
        url = f"https://api.henrikdev.xyz/valorant/v1/account/{quote(tokens.get('game_name', ''))}/{quote(tokens.get('tag_line', ''))}"
        res = requests.get(url, headers={"Authorization": api_key}, timeout=5)
        if res.status_code == 200 and "account_level" in res.json().get("data", {}):
            level = res.json()["data"]["account_level"]
            logging.info(f"Seviye alındı: {level}")
            return level
        logging.warning(f"Seviye alınamadı: HTTP {res.status_code} - {res.text}")
    except Exception as e:
        logging.error(f"Seviye alınırken hata: {e}")

    return "Bilinmeyen"

def get_wallet_info(puuid, tokens, region, version, platform):
    region_endpoints = {
        "na": "pd.na.a.pvp.net",
        "eu": "pd.eu.a.pvp.net",
        "br": "pd.na.a.pvp.net",
        "latam": "pd.na.a.pvp.net",
        "ap": "pd.ap.a.pvp.net",
        "kr": "pd.kr.a.pvp.net"
    }
    endpoint = region_endpoints.get(region, "pd.eu.a.pvp.net")
    headers = {
        "X-Riot-Entitlements-JWT": tokens["entitlements_token"],
        "Authorization": f"Bearer {tokens['access_token']}",
        "X-Riot-ClientVersion": version,
        "X-Riot-ClientPlatform": platform
    }

    endpoints_to_try = [
        f"https://{endpoint}/store/v2/wallet/{puuid}",
        f"https://{endpoint}/store/v1/wallet/{puuid}",
        f"https://{endpoint}/rso-auth/v1/wallet/{puuid}"
    ]

    for url in endpoints_to_try:
        retries = 3
        for attempt in range(retries):
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ["1.1.1.1", "1.0.0.1"]
                resolver.resolve(endpoint)

                logging.info(f"Cüzdan isteği (deneme {attempt + 1}): URL={url}, Headers={headers}")
                res = requests.get(url, headers=headers, verify=False, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    logging.info(f"Cüzdan API yanıtı: {data}")
                    balances = data.get("Balances", {})
                    kingdom_credits = balances.get("85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", 0)
                    valorant_points = balances.get("e59aa87c-4cbf-517a-5983-6e81511be9b7", 0)
                    radianite_points = balances.get("f08d4ae3-939c-4576-ab26-4bf22846e6d8", 0)
                    logging.info(f"Cüzdan bilgileri alındı: KC={kingdom_credits}, VP={valorant_points}, RAD={radianite_points}")
                    return kingdom_credits, valorant_points, radianite_points
                logging.warning(f"Cüzdan isteği başarısız: HTTP {res.status_code} - {res.text}")
                time.sleep(2)
            except Exception as e:
                logging.error(f"Cüzdan isteği hata (deneme {attempt + 1}/{retries}): {e}")
                time.sleep(2)
    
    logging.error("Cüzdan bilgileri alınamadı. Manuel kontrol önerilir.")
    return "Bilinmeyen", "Bilinmeyen", "Bilinmeyen"

def get_rank_and_mmr(region, username, tag):
    try:
        url = f"https://api.henrikdev.xyz/valorant/v1/mmr/{region}/{quote(username)}/{quote(tag)}"
        res = requests.get(url, headers={"Authorization": api_key}, timeout=5)
        if res.status_code == 200:
            data = res.json()["data"]
            current_rank = data.get("currenttierpatched", "Yok")
            mmr_data = f"Elo: {data.get('elo', 0)}, RR: {data.get('ranking_in_tier', 0)}"
            logging.info(f"Rütbe alındı: {current_rank}, MMR: {mmr_data}")
            return current_rank, mmr_data
        if res.status_code == 404:
            logging.warning("Rütbe alınamadı: Maç verisi yok, lütfen hesapla bir maç oynayın.")
            return "Bilinmeyen", "Yok"
        else:
            logging.warning(f"Rütbe alınamadı: HTTP {res.status_code} - {res.text}")
            return "Bilinmeyen", "Yok"
    except Exception as e:
        logging.error(f"Rütbe alınırken hata: {e}")
        return "Bilinmeyen", "Yok"

def get_match_history(region, username, tag):
    try:
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{quote(username)}/{quote(tag)}?size=5"
        res = requests.get(url, headers={"Authorization": api_key}, timeout=5)
        if res.status_code == 200:
            matches = res.json().get("data", [])
            match_list = [
                f"{m['metadata']['map']}: {p['stats']['kills']}/{p['stats']['deaths']}/{p['stats']['assists']}"
                for m in matches for p in m['players']['all_players']
                if p['name'].lower() == username.lower() and p['tag'].lower() == tag.lower()
            ]
            logging.info(f"Maç geçmişi alındı: {match_list}")
            return match_list
        if res.status_code == 404:
            logging.warning("Maç geçmişi alınamadı: Maç verisi yok, lütfen hesapla bir maç oynayın.")
            return []
        else:
            logging.warning(f"Maç geçmişi alınamadı: HTTP {res.status_code} - {res.text}")
            return []
    except Exception as e:
        logging.error(f"Maç geçmişi alınırken hata: {e}")
        return []

def get_account_status(username, tag):
    try:
        url = f"https://api.henrikdev.xyz/valorant/v1/account/{quote(username)}/{quote(tag)}"
        res = requests.get(url, headers={"Authorization": api_key}, timeout=5)
        if res.status_code == 200:
            if "region" in res.json().get("data", {}):
                logging.info(f"Hesap durumu: Aktif")
                return "Aktif"
            logging.warning("Hesap durumu alınamadı: Veri eksik.")
            return "Erişilemez"
        if res.status_code == 404:
            logging.warning("Hesap durumu alınamadı: Maç verisi yok, lütfen hesapla bir maç oynayın.")
            return "Erişilemez"
        logging.warning(f"Hesap durumu alınamadı: HTTP {res.status_code} - {res.text}")
        return "Erişilemez"
    except Exception as e:
        logging.error(f"Hesap durumu alınırken hata: {e}")
        return "Erişilemez"

def get_item_name(item_id):
    try:
        for endpoint in ["weapons/skins", "bundles"]:
            res = requests.get(f"https://valorant-api.com/v1/{endpoint}/{item_id}", timeout=5)
            if res.status_code == 200:
                data = res.json()["data"]
                name = data.get("displayName") or data.get("name")
                if name:
                    logging.info(f"Öğe adı alındı ({endpoint}): {name}")
                    return name
        return None
    except Exception:
        logging.error(f"Öğe adı alınırken hata: {item_id}")
        return None

def get_skins(puuid, tokens, region, version, platform):
    region_endpoints = {
        "na": "pd.na.a.pvp.net",
        "eu": "pd.eu.a.pvp.net",
        "br": "pd.na.a.pvp.net",
        "latam": "pd.na.a.pvp.net",
        "ap": "pd.ap.a.pvp.net",
        "kr": "pd.kr.a.pvp.net"
    }
    endpoint = region_endpoints.get(region, "pd.eu.a.pvp.net")
    headers = {
        "X-Riot-Entitlements-JWT": tokens["entitlements_token"],
        "Authorization": f"Bearer {tokens['access_token']}",
        "X-Riot-ClientVersion": version,
        "X-Riot-ClientPlatform": platform
    }
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['1.1.1.1', '1.0.0.1']
        resolver.resolve(endpoint)
        url = f"https://{endpoint}/personalization/v2/players/{puuid}/playerloadout"
        res = requests.get(url, headers=headers, verify=False, timeout=5)
        if res.status_code == 200:
            data = res.json()
            skins = []
            for gun in data.get("Guns", []):
                skin_id = gun.get("SkinID")
                if skin_id:
                    skin_name = get_item_name(skin_id) or skin_id
                    skins.append(skin_name)
            logging.info(f"Skinler alındı: {'; '.join(skins) if skins else 'Yok'}")
            return "; ".join(skins) if skins else "Yok"
        logging.warning(f"Skinler alınamadı: HTTP {res.status_code} - {res.text}")
        return "Bilinmeyen"
    except Exception as e:
        logging.error(f"Skinler alınırken hata: {e}")
        return "Bilinmeyen"

def save_to_txt(username, password, game_name="Bilinmeyen", tag="Bilinmeyen", region="Bilinmeyen", 
                level="Bilinmeyen", rank="Bilinmeyen", mmr_data="Yok", matches=None, 
                kingdom_credits="Bilinmeyen", valorant_points="Bilinmeyen", radianite_points="Bilinmeyen", 
                email_verified=False, phone_verified=False, status="Bilinmeyen", skins="Bilinmeyen"):
    if matches is None:
        matches = []
    
    try:
        with open("active.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write(f"Giriş Kullanıcı Adı: {username}\n")
            f.write(f"Oyun Adı: {game_name}#{tag}\n")
            f.write(f"Şifre: {password}\n")
            f.write(f"Bölge: {region}\n")
            f.write(f"Seviye: {level}\n")
            f.write(f"Rütbe: {rank}\n")
            f.write(f"MMR Verisi: {mmr_data}\n")
            f.write(f"Hesap Durumu: {status}\n")
            f.write(f"Kingdom Credits: {kingdom_credits}\n")
            f.write(f"Valorant Points: {valorant_points}\n")
            f.write(f"Radianite Points: {radianite_points}\n")
            f.write(f"E-posta Doğrulandı: {'Evet' if email_verified else 'Hayır'}\n")
            f.write(f"Telefon Doğrulandı: {'Evet' if phone_verified else 'Hayır'}\n")
            f.write(f"Skinler: {skins}\n")
            f.write("Son 5 Maç:\n")
            for match in matches:
                f.write(f"- {match}\n")
            f.write("="*30 + "\n")
        logging.info(f"Hesap bilgileri dosyaya kaydedildi: {username}")
    except Exception as e:
        logging.error(f"Dosya kaydedilirken hata: {username} - {e}")

def read_accounts():
       accounts = []
       try:
           with open("accounts.txt", "r", encoding="utf-8") as f:
               for line in f:
                   line = line.strip()
                   if not line:
                       continue
                   try:
                       parts = line.split(":", 1)  # :: yerine : kullanıyoruz
                       if len(parts) != 2:
                           logging.warning(f"Geçersiz format: {line}. Beklenen: kullanıcı_adı:şifre")
                           continue
                       username, password = parts
                       accounts.append((username, password))
                   except Exception as e:
                       logging.error(f"Hatalı satır: {line} - {e}")
                       continue
           logging.info(f"Okunan hesap sayısı: {len(accounts)}")
       except Exception as e:
           logging.error(f"accounts.txt okunamadı: {e}")
       return accounts

def main():
    print("""      
       d88P                                     
      d88P                                      
     d88P                                       
    d88P  88888b.d88b.   .d88b.  888d888 .d88b. 
   d88P   888 "888 "88b d88""88b 888P"  d8P  Y8b
  d88P    888  888  888 888  888 888    88888888
 d88P     888  888  888 Y88..88P 888    Y8b.    
d88P      888  888  888  "Y88P"  888     "Y8888 
          
    discord: erengoboman ///
    github: erenalbayrak ///
  """)

    print("⚠️ ÖNEMLİ: Kodu çalıştırırken yönetici haklarıyla çalıştırın (örneğin, CMD veya IDE'yi 'Yönetici olarak çalıştır').")
    logging.info("Program başlatılıyor.")
    flush_dns()
    
    accounts = read_accounts()
    if not accounts:
        print("❌ accounts.txt dosyası boş veya okunamadı.")
        logging.error("accounts.txt boş veya okunamadı.")
        return

    account_count = 0
    for username, password in accounts:
        try:
            print(f"\n🔍 {username} için kontrol ediliyor...")
            logging.info(f"{username} için kontrol başladı.")
            account_count += 1

            kill_riot_processes()
            if not start_riot_client():
                print(f"⚠️ {username}: Riot Client başlatılamadı.")
                save_to_txt(username, password, status="Riot Client başlatılamadı")
                time.sleep(2)
                continue
            
            if not login_to_riot_client(username, password):
                print(f"⚠️ {username}: Giriş başarısız.")
                save_to_txt(username, password, status="Giriş başarısız")
                kill_riot_processes()
                time.sleep(2)
                continue
            
            tokens = get_tokens_from_lockfile()
            if not tokens:
                print(f"⚠️ {username}: Token alınamadı.")
                save_to_txt(username, password, status="Token alınamadı")
                kill_riot_processes()
                time.sleep(2)
                continue
            
            version, platform = get_client_headers()
            if not version or not platform:
                print(f"⚠️ {username}: Client headers alınamadı.")
                save_to_txt(username, password, status="Client headers alınamadı")
                kill_riot_processes()
                time.sleep(2)
                continue
            
            user_name, tag, country, email_verified, phone_verified = get_user_info(tokens)
            if not user_name or not tag:
                print(f"⚠️ {username}: Kullanıcı bilgileri alınamadı.")
                save_to_txt(username, password, status="Kullanıcı bilgileri alınamadı")
                kill_riot_processes()
                time.sleep(2)
                continue
            
            region = tokens.get("region", "eu")
            print(f"\n=== {user_name}#{tag} ===")
            print(f"Bölge: {region}")
            
            level = get_account_level(tokens["puuid"], tokens, region, version, platform)
            print(f"Seviye: {level}")
            
            rank, mmr_data = get_rank_and_mmr(region, user_name, tag)
            print(f"Rütbe: {rank}")
            print(f"MMR Verisi: {mmr_data}")
            
            kingdom_credits, valorant_points, radianite_points = get_wallet_info(tokens["puuid"], tokens, region, version, platform)
            print(f"Kingdom Credits: {kingdom_credits}")
            print(f"Valorant Points: {valorant_points}")
            print(f"Radianite Points: {radianite_points}")
            
            email_verified_str = "Evet" if email_verified else "Hayır"
            phone_verified_str = "Evet" if phone_verified else "Hayır"
            print(f"E-posta Doğrulandı: {email_verified_str}")
            print(f"Telefon Doğrulandı: {phone_verified_str}")
            
            skins = get_skins(tokens["puuid"], tokens, region, version, platform)
            print(f"Skinler: {skins}")
            
            matches = get_match_history(region, user_name, tag)
            for m in matches:
                print(f"- {m}")
            
            status = get_account_status(user_name, tag)
            print(f"Durum: {status}")
            
            save_to_txt(username, password, user_name, tag, region, level, rank, mmr_data, matches, 
                        kingdom_credits, valorant_points, radianite_points, email_verified, phone_verified, 
                        status, skins)
            
            kill_riot_processes()
            time.sleep(2)

            if account_count % 5 == 0:
                print("ℹ️ 5 hesap kontrol edildi, 30 saniye bekleniyor...")
                logging.info("5 hesap kontrol edildi, 30 saniye bekleniyor...")
                time.sleep(30)
                
        except Exception as e:
            logging.error(f"{username} için genel hata: {e}")
            print(f"⚠️ {username}: Hata oluştu, devam ediliyor: {e}")
            save_to_txt(username, password, status=f"Hata: {str(e)}")
            kill_riot_processes()
            time.sleep(2)
            continue

if __name__ == "__main__":
    main()

