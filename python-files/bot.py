import authsystem

import os
import re
import time
from time import sleep
from urllib.parse import unquote
import mimetypes
import base64
import asyncio
import json
import uuid

bannerc = "	\x1b[38;5;87m"
L1 = "\x1b[38;5;177m"
L = "\x1b[38;5;97m"

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")

def create_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('')
        print(f"File '{file_path}' created.")

def setup_folders_and_files():
    paths = {
        'keys_folder': 'data//keys',
        'keys_file': 'data//keys/keys.json',
        'used_keys_file': 'data//keys//used_keys.json',
        'output_folder': 'data//output',
        'success_file': 'data//output//success.txt',
        'failed_boosts_file': 'data//output//failed_boosts.txt',
        'data_folder': 'data',
        'proxies_file': 'data//3m.txt'
    }

    create_folder(paths['keys_folder'])
    create_folder(paths['keys_file'])
    create_folder(paths['used_keys_file'])
    create_folder(paths['output_folder'])
    create_folder(paths['success_file'])
    create_folder(paths['failed_boosts_file'])
    create_folder(paths['data_folder'])
    create_file(paths['proxies_file'])

setup_folders_and_files()

from discord_webhook import DiscordWebhook, DiscordEmbed
from threading import Thread
import discord
from websockets.exceptions import ConnectionClosedError
from enum import Enum, IntEnum
from discord.interactions import Interaction
from typing import Dict, List, Optional, Tuple, Union
from discord.ui import button
import json, httpx, tls_client, threading, time, random, hashlib, sys, os
from discord.ui.item import Item
from flask import request, Flask, jsonify
from discord.ui import Modal, TextInput
from discord.ext import commands
import requests
from base64 import b64encode
from discord import app_commands
from json.decoder import JSONDecodeError
import websockets
import os
import logging
from pymongo import MongoClient
from colorama import Fore, Style
from fastapi import FastAPI
from fastapi import Request
from fastapi.params import Body
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import datetime
from uvicorn import run
from concurrent.futures import ThreadPoolExecutor
bot = commands.Bot( command_prefix=",", intents=discord.Intents.all())
class Fore:
    RESET     = "\033[0m"
    BLACK     = "\033[30m"
    RED       = "\033[31m"
    GREEN     = "\033[32m"
    YELLOW    = "\033[33m"
    BLUE      = "\033[34m"
    MAGENTA   = "\033[35m"
    CYAN      = "\033[36m"
    WHITE     = "\033[37m"
    UNDERLINE = "\033[4m"



logging.basicConfig(level=logging.INFO, datefmt='%H:%M')
logging.addLevelName(logging.INFO, f'{L}[{Fore.WHITE}#{L}]{L1} |{Style.RESET_ALL}')
logging.addLevelName(logging.ERROR, f'{L}[{Fore.RED}-{L}]{L1} |{Style.RESET_ALL}')
logging.addLevelName(logging.WARNING, f'{L}[{Fore.YELLOW}WARNING{L}]{L1} |{Style.RESET_ALL}')
config = json.load(open("config/config.json", encoding="utf-8"))
oconfig = json.load(open("config/onliner.json", encoding="utf-8"))
logging.basicConfig(level=logging.INFO)
webhook_url = config['webhook_url']
use_log = config['use_log']
def send_webhook_message(webhook_url, content, embed):
    webhook = DiscordWebhook(url=webhook_url, content=content)
    webhook.add_embed(embed)
    response = webhook.execute()
    if response.status_code in [200, 201, 202, 203, 204, 205, 206, 207]:
        pass
    else:
        logging.error(f"Failed to send message. Status code: {response.status_code}")


powerboosts = rf"""{Fore.BLUE}



██████╗ ██╗      █████╗ ██╗  ██╗██╗███████╗██╗   ██╗
██╔══██╗██║     ██╔══██╗██║ ██╔╝██║██╔════╝╚██╗ ██╔╝
██████╦╝██║     ██║  ██║█████═╝ ██║█████╗   ╚████╔╝
██╔══██╗██║     ██║  ██║██╔═██╗ ██║██╔══╝    ╚██╔╝
██████╦╝███████╗╚█████╔╝██║ ╚██╗██║██║        ██║
╚═════╝ ╚══════╝ ╚════╝ ╚═╝  ╚═╝╚═╝╚═╝        ╚═╝
                                                                              
                                                                                                                                           
                                    
                            
{Fore.RESET}"""

gradient_colors = [Fore.BLUE]

def animate_gradient():
    for i in range(len(gradient_colors) * 2):
        os.system('cls' if os.name == 'nt' else 'clear')  
        for line in powerboosts.split('\n'):
            gradient_index = i % len(gradient_colors)
            print(f"{gradient_colors[gradient_index]}{line}{Fore.RESET}")
        time.sleep(0.05)

animation_thread = threading.Thread(target=animate_gradient)
animation_thread.start()
animation_thread.join()

class DiscordWebSocket:
    def __init__(self, *args, **kwargs):
        self.initialize_websocket(*args, **kwargs)

    def initialize_websocket(self, *args, **kwargs):
        # Implementation of websocket_instance
        print("initialize_websocket method called")
        # Add your actual implementation here

    def websocket_instance(self, *args, **kwargs):
        print("websocket_instance method called")
        # Add your actual implementation here

def log_error(error_message):
    log_directory = "database"
    log_file = "errors.txt"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    with open(os.path.join(log_directory, log_file), "a") as file:
        file.write(error_message + "\n")

# Example usage
try:
    socket = DiscordWebSocket()
except Exception as e:
    log_error(f"Error creating DiscordWebSocket instance: {e}")

api_key = config['captcha_solver']['hcoptcha_api_key']
cs_api_key = config['captcha_solver']['capsolver_api_key']
csolver = config['captcha_solver']['capsolver_api_key']

h_proxy = None

def load_tokens_json(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
def save_tokens_json(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

class Status(Enum):
    ONLINE = "online" 
    DND = "dnd"  
    IDLE = "idle" 
    INVISIBLE = "invisible"  
    OFFLINE = "offline" 


class Activity(Enum):
    GAME = 0  
    STREAMING = 1  
    LISTENING = 2  
    WATCHING = 3  
    CUSTOM = 4  
    COMPETING = 5 


class OPCodes(Enum):
    Dispatch = 0  
    Heartbeat = 1
    Identify = 2 
    PresenceUpdate = 3
    VoiceStateUpdate = 4
    Resume = 6  
    Reconnect = 7  
    RequestGuildMembers = (
        8  
    )
    InvalidSession = 9  
    Hello = (
        10  
    )
    HeartbeatACK = 11 


class DiscordIntents(IntEnum):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21


class Presence:
    def __init__(self, online_status: Status) -> None:
        self.online_status: Status = online_status
        self.activities: List[Activity] = []

    def addActivity(
        self, name: str, activity_type: Activity, url: Optional[str]
    ) -> int:

        self.activities.append(
            {
                "name": name,
                "type": activity_type.value, 
                "url": url if activity_type == Activity.STREAMING else None,
            }
        )
        return len(self.activities) - 1

    def removeActivity(self, index: int) -> bool:
        if index < 0 or index >= len(self.activities):
            return False
        self.activities.pop(index)
        return True
class AvatarSocket:
    def __init__(self) -> None:
        self.websocket_instance(
            "wss://gateway.discord.gg/?v=10&encoding=json"
        )
        self.heartbeat_counter = 0

        self.username: str = None
        self.required_action: str = None
        self.heartbeat_interval: int = None
        self.last_heartbeat: float = None

    def get_heatbeat_interval(self) -> None:
        resp: Dict = json.loads(self.websocket_instance.recv())
        self.heartbeat_interval = resp["d"]["heartbeat_interval"]

    def authenticate(self, token: str, rich) -> Union[Dict, bool]:
        self.websocket_instance.send(
            json.dumps(
                {
                    "op": OPCodes.Identify.value,
                    "d": {
                        "token": token,
                        "intents": DiscordIntents.GUILD_MESSAGES
                        | DiscordIntents.GUILDS,  
                        "properties": {
                            "os": "linux",  
                            "browser": "Brave",  
                            "device": "Desktop",
                        },
                        "presence": {
                            "activities": [
                                activity for activity in rich.activities
                            ],  
                            "status": rich.online_status.value,  
                            "since": time.time(),  
                            "afk": False, 
                        },
                    },
                }
            )
        )
        try:
            resp = json.loads(self.websocket_instance.recv())
            self.username: str = resp["d"]["user"]["username"]
            self.required_action = resp["d"].get("required_action")
            self.heartbeat_counter += 1
            self.last_heartbeat = time.time()

            return resp
        except ConnectionClosedError:
            return False

    def send_heartbeat(self) -> websockets.typing.Data:
        self.websocket_instance.send(
            json.dumps(
                {"op": OPCodes.Heartbeat.value, "d": None}
            ) 
        )

        self.heartbeat_counter += 1
        self.last_heartbeat = time.time()

        resp = self.websocket_instance.recv()
        return resp
    

    def avatar_socket(token: str, activity: Presence):
        socket = DiscordWebSocket()
        socket.get_heatbeat_interval()

        auth_resp = socket.authenticate(token, activity)

        if not auth_resp:
            return
        while True:
            try:
                if (
                    time.time() - socket.last_heartbeat
                    >= (socket.heartbeat_interval / 1000) - 5
                ):  
                    resp = socket.send_heartbeat()
                time.sleep(0.5)
            except IndentationError:
                print(resp)
    def run_socket(self, token):
        with open("config/onliner.json", "r") as config_file:
            config: Dict[str, Union[List[str], Dict[str, List[str]]]] = json.loads(config_file.read())

        activity_types: List[Activity] = [
            Activity[x.upper()] for x in config["choose_random_activity_type_from"]
        ]
        online_statuses: List[Status] = [
            Status[x.upper()] for x in config["choose_random_online_status_from"]
        ]
        online_status = random.choice(online_statuses)
        chosen_activity_type = random.choice(activity_types)
        url = None

        if chosen_activity_type:
            if Activity.GAME:
                name = random.choice(config["game"]["choose_random_game_from"])

            elif Activity.STREAMING:
                name = random.choice(config["streaming"]["choose_random_name_from"])
                url = random.choice(config["streaming"]["choose_random_url_from"])

            elif Activity.LISTENING:
                name = random.choice(config["listening"]["choose_random_name_from"])

            elif Activity.WATCHING:
                name = random.choice(config["watching"]["choose_random_name_from"])

            elif Activity.CUSTOM:
                name = random.choice(config["custom"]["choose_random_name_from"])

            elif Activity.COMPETING:
                name = random.choice(config["competing"]["choose_random_name_from"])

        activity = Presence(online_status)
        activity.addActivity(activity_type=chosen_activity_type, name=name, url=url)
        x = Thread(target=main, args=(token, activity))
        x.start()
# avatar changer websocket end

try:
    h_proxy=random.choice(open("data/proxies.txt", "r").read().splitlines())
except:
    h_proxy=None
def h_captcha(sitekey, url, rqdata):
    p1 = {
	"task_type": "hcaptchaEnterprise",
	"api_key": f"{api_key}",
	"data": {
		"sitekey": sitekey,
		"url": url,
		"rqdata": rqdata ,
        "proxy": h_proxy
	}
    }
    h1 = {"Content-Type": "application/json"}

    r1 = requests.post("https://api.hcoptcha.online/api/createTask", headers=h1, json=p1)
    if r1.json()['error'] != True:
        try:    
            a = r1.json()['task_id']
            return a
        except:
            return False
    else:
        logging.error("Unable to create task")
        print(r1.json())       
        return False

def encoded(path: str):
        try:
            with open(path + random.choice(os.listdir(path)), "rb") as f:
                img = f.read()
            return f'data:image/png;base64,{b64encode(img).decode("ascii")}'
        except Exception as e:
            logging.error(f'Encoding Error: {str(e).capitalize()}')
            pass

def h_result(task_id):
    p2 = {
	"api_key": f"{api_key}",
	"task_id": task_id }
    h2 = {"Content-Type": "application/json"}
    r2 = requests.post("https://api.hcoptcha.com/api/getTaskData", headers=h2, json=p2)
    if 'captcha_key' in r2.text:
        try:    
            a = r2.json()
            return a
        except:
            return False
    else:
        if config['advance_mode']:
            logging.error(f"Unable to get solution : {r2.json()}")
        return False


def cs_captcha(sitekey, url, rqdata):
    p1 = {

	"clientKey": cs_api_key,
	"task": {
        	"type": "HCaptchaTaskProxyLess",
		"websiteKey": sitekey,
		"websiteURL": url,
		"enterprisePayload": {
      "rqdata": rqdata,
    },
	}
    }
    h1 = {"Content-Type": "application/json"}

    r1 = requests.post("https://api.capsolver.com/createTask", headers=h1, json=p1)
    if not r1.json()['errorId']:
        try:    
            a = r1.json()['taskId']
            return a
        except:
            return False
    else:
        logging.error("Unable to create task")
        if config['advance_mode'] == True:
            logging.error(f"Reason {r1.json()}")    
        return False

def cs_result(task_id):
    p2 = {
	"clientKey": cs_api_key,
	"taskId": task_id }
    h2 = {"Content-Type": "application/json"}
    r2 = requests.post("https://api.capsolver.com/getTaskResult", headers=h2, json=p2)
    if 'solution' in r2.text:
        try:    
            a = r2.json()
            return a
        except:
            a = r2.json()
            return False
            
    else:
        logging.error("Unable to solve captcha")
        if config['advance_mode'] == True:
            print(r2.json())       
        return False
    
class Joiner:
    def __init__(self) -> None:
        self.proxy = self.getProxy()
        self.crome_v = f'Chrome_{str(random.randint(110, 118))}'
        self.client = tls_client.Session(
            client_identifier=self.crome_v,
            random_tls_extension_order=True,
            ja3_string='771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,18-23-45-11-27-10-0-5-13-65037-16-51-17513-43-35-65281-41,25497-29-23-24,0',            
        )
        self.locale = random.choice(["af", "af-NA", "af-ZA", "agq", "agq-CM", "ak", "ak-GH", "am", "am-ET", "ar", "ar-001", "ar-AE", "ar-BH", "ar-DJ", "ar-DZ", "ar-EG", "ar-EH", "ar-ER", "ar-IL", "ar-IQ", "ar-JO", "ar-KM", "ar-KW", "ar-LB", "ar-LY", "ar-MA", "ar-MR", "ar-OM", "ar-PS", "ar-QA", "ar-SA", "ar-SD", "ar-SO", "ar-SS", "ar-SY", "ar-TD", "ar-TN", "ar-YE", "as", "as-IN", "asa", "asa-TZ", "ast", "ast-ES", "az", "az-Cyrl", "az-Cyrl-AZ", "az-Latn", "az-Latn-AZ", "bas", "bas-CM", "be", "be-BY", "bem", "bem-ZM", "bez", "bez-TZ", "bg", "bg-BG", "bm", "bm-ML", "bn", "bn-BD", "bn-IN", "bo", "bo-CN", "bo-IN", "br", "br-FR", "brx", "brx-IN", "bs", "bs-Cyrl", "bs-Cyrl-BA", "bs-Latn", "bs-Latn-BA", "ca", "ca-AD", "ca-ES", "ca-FR", "ca-IT", "ccp", "ccp-BD", "ccp-IN", "ce", "ce-RU", "cgg", "cgg-UG", "chr", "chr-US", "ckb", "ckb-IQ", "ckb-IR", "cs", "cs-CZ", "cy", "cy-GB", "da", "da-DK", "da-GL", "dav", "dav-KE", "de", "de-AT", "de-BE", "de-CH", "de-DE", "de-IT", "de-LI", "de-LU", "dje", "dje-NE", "dsb", "dsb-DE", "dua", "dua-CM", "dyo", "dyo-SN", "dz", "dz-BT", "ebu", "ebu-KE", "ee", "ee-GH", "ee-TG", "el", "el-CY", "el-GR", "en", "en-001", "en-150", "en-AG", "en-AI", "en-AS", "en-AT", "en-AU", "en-BB", "en-BE", "en-BI", "en-BM", "en-BS", "en-BW", "en-BZ", "en-CA", "en-CC", "en-CH", "en-CK", "en-CM", "en-CX", "en-CY", "en-DE", "en-DG", "en-DK", "en-DM", "en-ER", "en-FI", "en-FJ", "en-FK", "en-FM", "en-GB", "en-GD", "en-GG"])

        self.useragent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {self.crome_v}.0.0.0 Safari/537.36'
        self.failed = []
        self.success = []
        self.captcha = []
        self.getX()
        self.fingerprints()
        self.proxy = self.getProxy()

    def getX(self):
        properties = {
            "os": 'Windows',
            "browser": 'Chrome',
            "device": "",
            "system_locale": self.locale,
            "browser_user_agent": self.useragent,
            "browser_version": f'{self.crome_v}.0.0.0',
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": 236850,
            "client_event_source": None
        }

        self.x = b64encode(json.dumps(properties, separators=(',', ':')).encode("utf-8")).decode()

    def getProxy(self):
        try:
            proxy = random.choice(open("data/proxies.txt", "r").read().splitlines())
            return {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        except Exception as e:
            return None

    def fingerprints(self):
        headers = {
            "authority": "discord.com",
            "method": "GET",
            "path": "/api/v9/experiments",
            "scheme": "https",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": '"Not/A)Brand;v=8", "Chromium;v=126", "Brave;v=126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.useragent
            }
        
        tries = 0
        while tries < 10:
            try:
                r = httpx.get(f'https://discord.com/api/v9/experiments', headers=headers)
                break
            except Exception as e:
                print(f'Failed to Execute Request getting fingerprints: ' + str(e).capitalize())
                tries += 1

                if tries == 10:
                    print(f'Max Reties Completed. Failed to Execute: ' + str(e).capitalize())
                    return
            
        if not (r.status_code in (200, 201)):
            logging.error(f'Failed to Fetch Cookies from discord.com. ' + str(r.text).capitalize())
            return ''
        
        self.fp = r.json()['fingerprint']
        self.ckis = f'locale=en-US; __dcfduid={r.cookies.get("__dcfduid")}; __sdcfduid={r.cookies.get("__sdcfduid")}; __cfruid={r.cookies.get("__cfruid")}; _cfuvid={r.cookies.get("_cfuvid")}'

    def boost(self, token, invite, guild):
        headers = {
            "authority": "discord.com",
            "scheme": "https",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": str(token),
            "Content-Type": "application/json",
            "Cookie": str(self.ckis),
            "Origin": "https://discord.com",
            "Priority": "u=1, i",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not/A)Brand;v=8", "Chromium;v=126", "Brave;v=126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": self.useragent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            'X-fingerprint': self.fp,
            "X-Super-Properties": self.x
            }

        r = self.client.post(
            f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={}
        )

        if r.status_code == 200:
            print("JOINED")

    def humanizer(self, token, nick, bio):
        if ':' in str(token):
            token = str(token).split(':')[2]

        else:
            token = token
        
        apiurl = 'https://discord.com/api/v9/guilds/' + self.guild_id + '/members/@me'
        ap = []
        headers = {
            "authority": "discord.com",
            "scheme": "https",
            'method': 'PATCH',
            'path': f'/api/v9/guilds/' + self.guild_id + '/members/@me',
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": str(token),
            "Content-Type": "application/json",
            "Cookie": str(self.ckis),
            "Origin": "https://discord.com",
            "Priority": "u=1, i",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not/A)Brand;v=8", "Chromium;v=126", "Brave;v=126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": self.useragent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            'X-fingerprint': self.fp,
            "X-Super-Properties": self.x
            }
        
        h = headers
        h['path'] = '/api/v9/users/@me/profile'

        if not (config['customisation']['bio'] == ''):
            tries = 0
            while tries < 10:
                try:
                    b = self.client.patch(
                        f'https://discord.com/api/v9/users/@me/profile',
                        headers=h,
                        json={"bio": bio}
                        )
                    break
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
                    
            if b.status_code == 200:
                ap.append(f'bio')
        if not (config['customisation']['nick'] == ''):
            tries = 0
            while tries < 10:
                try:
                    b= self.client.patch(
                        apiurl,
                        headers=headers,
                        json={"nick": nick}
                        )
                    break
                
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
            if b.status_code == 200:
                ap.append(f'nick')
        
        if config['customisation']['use_custom_pfp']:
            tries = 0
            while tries < 10:
                try:
                    b = self.client.patch(
                        apiurl,
                        headers=headers,
                        json={'avatar': encoded(f'data/avatar/')}
                        )
                    break
                
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
            if b.status_code == 200:
                ap.append(f'avatar')
        
        if config['customisation']['use_custom_banner']:
            tries = 0
            while tries < 10:
                try:
                    b = self.client.patch(
                        apiurl,
                        headers=headers,
                        json={'banner': (f'data/banner/')}
                        )
                    break
                
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
            
            if b.status_code == 200:
                ap.append(f'banner')
        
        if len(ap) in (1,2,3,4):
            logging.info(f'Successfully Humanized. {ap}')
        else:
            logging.error(f'Failed to Humanized.')
            return
    
    def humanizerthread(self, tokens, nick, bio):
        try:
            threads = []
            thr = len(tokens)
            for i in range(thr):
                token = tokens[i]
                t = threading.Thread(target=self.humanizer(token, nick, bio), args=())
                t.daemon = True
                threads.append(t)
                
            for i in range(thr):
                threads[i].start()
                
            for i in range(thr):
                threads[i].join()
        
        except Exception as e:
            logging.error(f'Failed to Execute Threads: '+ str(e).capitalize())
            return

    def thread(self, invite, tokens, guild):
        """"""
        threads = []

        for i in range(len(tokens)):
            token = tokens[i]
            t = threading.Thread(target=self.boost, args=(token, invite, guild))
            t.daemon = True
            threads.append(t)

        for i in range(len(tokens)):
            threads[i].start()

        for i in range(len(tokens)):
            threads[i].join()

        return {
            "success": self.success,
            "failed": self.failed,
            "captcha": self.captcha,
        }
    
def getStock(filename: str):
    tokens = []
    for i in open(filename, "r").read().splitlines():
        if ":" in i:
            i = i.split(":")[2]
            tokens.append(i)
        else:
            tokens.append(i)
    return tokens

def getStock_Auto(filename: str, num_tokens: int):
    with open(filename, "r") as file:
        lines = file.readlines()

    tokens = []
    remaining_lines = []

    for line in lines[:num_tokens]:
        if ":" in line:
            i = line.split(":")[2]
            tokens.append(i)
        else:
            tokens.append(line)    
    remaining_lines.extend(lines[num_tokens:])
    with open(filename, "w") as file:
        for line in remaining_lines:
            file.write(line)

    return tokens

def getinviteCode(inv):
    if "discord.gg" in inv:
        invite = inv.split("discord.gg/")[1]
        return invite
    if "https://discord.gg" in inv:
        invite = inv.split("https://discord.gg/")[1]
        return invite
    if 'discord.com/invite' in inv:
        invite = inv.split("discord.com/invite/")[1]
        return invite
    if 'https://discord.com/invite/' in inv:
        invite = inv.split("https://discord.com/invite/")[1]
        return invite
    else:
        return inv

def checkInvite(invite: str):
    data = requests.get(
        f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true"
    ).json()

    if data["code"] == 10006:
        return False
    elif data:
        return data["guild"]["id"]
    else:
        return False
class JoinerModal(Modal):
    def __init__(self):
        super().__init__(title="Join")
        self.add_item(
            TextInput(
                label="Invite",
                placeholder="Invite code of the server.",
                required=True,
                style=discord.TextStyle.short
            )
        )
        self.add_item(
            TextInput(
                label="Amount",
                placeholder="Amount of joins (must be in numbers).",
                required=True,
                style=discord.TextStyle.short
            )
        )
        
    async def on_submit(self, ctx: discord.Interaction):
        invite = self.children[0].value
        amount = int(self.children[1].value)
        
        await ctx.response.defer()

        inviteCode = getinviteCode(invite)
        inviteData = checkInvite(inviteCode)
        if inviteData is False:
            return await ctx.followup.send(
                embed=discord.Embed(
                    title="`Error`",
                    description=f"`Invalid Invite | .gg/{invite}`",
                    color=config['embed_config']['color'],
                )
            )

        file_path = "data/join.json"
        guild_id = str(ctx.guild.id)

        tokens_json = load_tokens_json(file_path)
        guild_tokens = tokens_json.get(guild_id, [])
        requiredStock = amount

        if requiredStock > len(guild_tokens):
            return await ctx.followup.send(
                embed=discord.Embed(
                    title="`Error`",
                    description="`Not enough stock. Use the command /restockjoin to restock tokens`",
                    color=config['embed_config']['color'],
                )
            )

        tokens_to_use = guild_tokens[:requiredStock]
        tokens_json[guild_id] = guild_tokens[requiredStock:]
        save_tokens_json(tokens_json, file_path)

        token_list = [t["token"] for t in tokens_to_use]

        joiner = Joiner()
        msg = await ctx.followup.send(
            embed=discord.Embed(
                title="- `Join Bot Information`",
                description="Joining Server...",
                color=config['embed_config']['color'],
            )
        )

        start = time.time()
        status = joiner.thread(inviteCode, token_list, inviteData)
        time_taken = round(time.time() - start, 2)

        final_embed = discord.Embed(
            title="Join Bot Information",
            description=(
                f"`Amount:` {amount} join(s)\n"
                f"`Tokens:` {requiredStock}\n"
                f"`Server Link:` .gg/{inviteCode}\n"
                f"`Succeeded Joins:` {len(status['success'])}\n"
                f"`Failed Joins:` {len(status['failed'])}\n"
                f"`Time Took:` {time_taken} seconds\n\n"
            ),
            color=config['embed_config']['color'],
        )
        await msg.edit(embed=final_embed)

class Booster:
    def __init__(self) -> None:
        self.proxy = self.getProxy()
        self.crome_v = f'Chrome_{str(random.randint(110, 118))}'
        self.client = tls_client.Session(
            client_identifier=self.crome_v,
            random_tls_extension_order=True,
            ja3_string='771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,18-23-45-11-27-10-0-5-13-65037-16-51-17513-43-35-65281-41,25497-29-23-24,0',            
        )
        self.locale = random.choice(["af", "af-NA", "af-ZA", "agq", "agq-CM", "ak", "ak-GH", "am", "am-ET", "ar", "ar-001", "ar-AE", "ar-BH", "ar-DJ", "ar-DZ", "ar-EG", "ar-EH", "ar-ER", "ar-IL", "ar-IQ", "ar-JO", "ar-KM", "ar-KW", "ar-LB", "ar-LY", "ar-MA", "ar-MR", "ar-OM", "ar-PS", "ar-QA", "ar-SA", "ar-SD", "ar-SO", "ar-SS", "ar-SY", "ar-TD", "ar-TN", "ar-YE", "as", "as-IN", "asa", "asa-TZ", "ast", "ast-ES", "az", "az-Cyrl", "az-Cyrl-AZ", "az-Latn", "az-Latn-AZ", "bas", "bas-CM", "be", "be-BY", "bem", "bem-ZM", "bez", "bez-TZ", "bg", "bg-BG", "bm", "bm-ML", "bn", "bn-BD", "bn-IN", "bo", "bo-CN", "bo-IN", "br", "br-FR", "brx", "brx-IN", "bs", "bs-Cyrl", "bs-Cyrl-BA", "bs-Latn", "bs-Latn-BA", "ca", "ca-AD", "ca-ES", "ca-FR", "ca-IT", "ccp", "ccp-BD", "ccp-IN", "ce", "ce-RU", "cgg", "cgg-UG", "chr", "chr-US", "ckb", "ckb-IQ", "ckb-IR", "cs", "cs-CZ", "cy", "cy-GB", "da", "da-DK", "da-GL", "dav", "dav-KE", "de", "de-AT", "de-BE", "de-CH", "de-DE", "de-IT", "de-LI", "de-LU", "dje", "dje-NE", "dsb", "dsb-DE", "dua", "dua-CM", "dyo", "dyo-SN", "dz", "dz-BT", "ebu", "ebu-KE", "ee", "ee-GH", "ee-TG", "el", "el-CY", "el-GR", "en", "en-001", "en-150", "en-AG", "en-AI", "en-AS", "en-AT", "en-AU", "en-BB", "en-BE", "en-BI", "en-BM", "en-BS", "en-BW", "en-BZ", "en-CA", "en-CC", "en-CH", "en-CK", "en-CM", "en-CX", "en-CY", "en-DE", "en-DG", "en-DK", "en-DM", "en-ER", "en-FI", "en-FJ", "en-FK", "en-FM", "en-GB", "en-GD", "en-GG"])

        self.useragent = f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {self.crome_v}.0.0.0 Safari/537.36'
        self.failed = []
        self.success = []
        self.captcha = []
        self.getX()
        self.fingerprints()
        self.proxy = self.getProxy()

    def getX(self):
        properties = {
            "os": 'Windows',
            "browser": 'Chrome',
            "device": "",
            "system_locale": self.locale,
            "browser_user_agent": self.useragent,
            "browser_version": f'{self.crome_v}.0.0.0',
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": 236850,
            "client_event_source": None
        }

        self.x = b64encode(json.dumps(properties, separators=(',', ':')).encode("utf-8")).decode()

    def getProxy(self):
        try:
            proxy = random.choice(open("data/proxies.txt", "r").read().splitlines())
            return {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        except Exception as e:
            return None

    def fingerprints(self):
        headers = {
            "authority": "discord.com",
            "method": "GET",
            "path": "/api/v9/experiments",
            "scheme": "https",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Priority": "u=0, i",
            "Sec-Ch-Ua": '"Not/A)Brand;v=8", "Chromium;v=126", "Brave;v=126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Sec-Gpc": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.useragent
            }
        
        tries = 0
        while tries < 10:
            try:
                r = httpx.get(f'https://discord.com/api/v9/experiments', headers=headers)
                break
            except Exception as e:
                print(f'Failed to Execute Request getting fingerprints: ' + str(e).capitalize())
                tries += 1

                if tries == 10:
                    print(f'Max Reties Completed. Failed to Execute: ' + str(e).capitalize())
                    return
            
        if not (r.status_code in (200, 201)):
            logging.error(f'Failed to Fetch Cookies from discord.com. ' + str(r.text).capitalize())
            return ''
        
        self.fp = r.json()['fingerprint']
        self.ckis = f'locale=en-US; __dcfduid={r.cookies.get("__dcfduid")}; __sdcfduid={r.cookies.get("__sdcfduid")}; __cfruid={r.cookies.get("__cfruid")}; _cfuvid={r.cookies.get("_cfuvid")}'

    def boost(self, token, invite, guild):
        headers = {
            "authority": "discord.com",
            "scheme": "https",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": str(token),
            "Content-Type": "application/json",
            "Cookie": str(self.ckis),
            "Origin": "https://discord.com",
            "Priority": "u=1, i",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not/A)Brand;v=8", "Chromium;v=126", "Brave;v=126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": self.useragent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            'X-fingerprint': self.fp,
            "X-Super-Properties": self.x
            }

        slots = self.client.get(
            "https://discord.com/api/v9/users/@me/guilds/premium/subscription-slots",
            headers=headers,
        )

        slot_json = slots.json()
        tkv = token

        if slots.status_code == 401:
            logging.error(f"{tkv} Invalid/No-Nitro")
            return
        
        elif slots.status_code != 200 or len(slot_json) == 0:
            logging.error(f"{tkv} Invalid/No-Nitro")
            return

        r = self.client.post(
            f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={}
        )

        if r.status_code == 200:
            self.guild_id = r.json()["guild"]["id"]
            boostsList = []
            for boost in slot_json:
                boostsList.append(boost["id"])

            payload = {"user_premium_guild_subscription_slot_ids": boostsList}

            headers["method"] = "PUT"
            headers["path"] = f"/api/v9/guilds/{guild}/premium/subscriptions"

            boosted = self.client.put(
                f"https://discord.com/api/v9/guilds/{guild}/premium/subscriptions",
                json=payload,
                headers=headers,
            )

            if boosted.status_code == 201:
              self.success.append(token)
              with open("output/success.txt", "a") as file:
                file.write(token + "\n")
                return True
            else:
             with open("output/failed_boosts.txt", "a") as file:
                file.write(token + "\n")
             self.failed.append(token)

        elif r.status_code != 200:
            join_outcome = False
            max_retries = None
            solve_captcha = None
            tr = 1
            tr0 = 1
            try:
                solve_captcha = config['captcha_solver']['solve_captcha']
            except:
                solve_captcha = False    
            try:
                max_retries = config['captcha_solver']['max_retries']

            except:
                max_retries = 2
            cap_service = None
            try:
                if config['captcha_solver']['use'] == "hcoptcha":
                    cap_service = 1
                elif config['captcha_solver']['use'] == "capsolver":
                    cap_service = 2
                else:
                    cap_service = 3
            except:
                logging.error("Captcha service can be either hcoptcha or capsolver please update it in config file!")

            if "captcha" in r.text:
              logging.error(f"Captcha Detected : {tkv}")
              with open ("data/output/captcha.txt", "a") as f:
                  f.write(token + "\n")
                  self.captcha.append(token)
              if config['captcha_solver']['solve_captcha'] == True:
                retry = 0
                while join_outcome != True and retry < max_retries and cap_service != None:
                    r = self.client.post(
                f"https://discord.com/api/v9/invites/{invite}", headers=headers, json={}
            )
                    response = r.json()
                    if cap_service != 3:
                        if cap_service == 1:
                            s1 = h_captcha(response['captcha_sitekey'], f"https://discord.com/invite/{invite}", response['captcha_rqdata'])
                        elif cap_service == 2:
                            s1 = cs_captcha(response['captcha_sitekey'], f"https://discord.com/invite/{invite}", response['captcha_rqdata'])
                        task_id = s1
                        logging.info(f"Solving Captcha : {tkv}")
                        time.sleep(10)
                        if cap_service == 1:
                            s2 = h_result(task_id)
                        else:
                            s2 = cs_result(task_id)
                    s3 = None
                    try:
                        if cap_service == 1:
                            s3 = s2['task']['captcha_key']
                        elif cap_service == 2:
                            s3 = s2['solution']['gRecaptchaResponse']
                        else:
                            s3 = csolve(response['captcha_sitekey'], f"https://discord.com/invite/{invite}", response['captcha_rqdata'])
                    except:
                        pass
                    req2headers = headers
                    req2headers.pop("Content-Length", None)
                    try: 
                        req2headers["X-Captcha-Key"] = s3 
                        req2headers["X-Captcha-Rqtoken"] = response['captcha_rqtoken']
                    except:
                        pass
                    response = self.client.post(f'https://discord.com/api/v9/invites/{invite}', json={}, headers = req2headers)
                    if response.status_code in [200, 204]:
                        join_outcome = True
                        self.guild_id = response.json()["guild"]["id"]
                        logging.info(f"Captcha Solved : {tkv}")
                        boostsList = []
                        for boost in slot_json:
                            boostsList.append(boost["id"])

                        payload = {"user_premium_guild_subscription_slot_ids": boostsList}

                        headers["method"] = "PUT"
                        headers["path"] = f"/api/v9/guilds/{guild}/premium/subscriptions"

                        boosted = self.client.put(
                            f"https://discord.com/api/v9/guilds/{guild}/premium/subscriptions",
                            json=payload,
                            headers=headers, proxy=self.proxy
                        )

                        if boosted.status_code == 201:
                            self.success.append(token)
                            with open("output/success.txt", "a") as file:
                                file.write(token + "\n")
                                logging.info(f"Boosts Successful : {tkv}")
                        else:
                            with open("output/failed_boosts.txt", "a") as file:
                                file.write(token + "\n")
                                self.failed.append(token)
                                logging.error(f"Boosts Failed : {tkv}")
                        break
                    else:
                        if "10008" in response.text:
                            logging.error(f"Token Flagged [ Unable To Join Even After A Valid Captcha Solution ]: {tkv}")
                            self.failed.append(token)
                            break
                        retry += 1
                        logging.info(f"Retrying Solving Captcha : {tkv} [ {retry}/{max_retries} ]")
            elif not "captcha" in r.text:
                tkv = token[:-8] + "*" * 8

                boostsList = []
                for boost in slot_json:
                    boostsList.append(boost["id"])

                payload = {"user_premium_guild_subscription_slot_ids": boostsList}

                headers["method"] = "PUT"
                headers["path"] = f"/api/v9/guilds/{guild}/premium/subscriptions"

                boosted = self.client.put(
                    f"https://discord.com/api/v9/guilds/{guild}/premium/subscriptions",
                    json=payload,
                    headers=headers, proxy=self.proxy
                )

                if boosted.status_code == 201:
                    self.success.append(token)
                    with open("output/success.txt", "a") as file:
                        file.write(token + "\n")
                        logging.info(f"Boosts Successful : {tkv}")
                        return True
                else:
                    with open("output/failed_boosts.txt", "a") as file:
                        file.write(token + "\n")
                        self.failed.append(token)
                        logging.error(f"Boosts Failed : {tkv}")
                


    def humanizer(self, token, nick, bio):
        if ':' in str(token):
            token = str(token).split(':')[2]

        else:
            token = token
        
        apiurl = 'https://discord.com/api/v9/guilds/' + self.guild_id + '/members/@me'
        ap = []
        headers = {
            "authority": "discord.com",
            "scheme": "https",
            'method': 'PATCH',
            'path': f'/api/v9/guilds/' + self.guild_id + '/members/@me',
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": str(token),
            "Content-Type": "application/json",
            "Cookie": str(self.ckis),
            "Origin": "https://discord.com",
            "Priority": "u=1, i",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Not/A)Brand;v=8", "Chromium;v=126", "Brave;v=126"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": self.useragent,
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "Asia/Calcutta",
            'X-fingerprint': self.fp,
            "X-Super-Properties": self.x
            }
        
        h = headers
        h['path'] = '/api/v9/users/@me/profile'

        if not (config['customisation']['bio'] == ''):
            tries = 0
            while tries < 10:
                try:
                    b = self.client.patch(
                        f'https://discord.com/api/v9/users/@me/profile',
                        headers=h,
                        json={"bio": bio}
                        )
                    break
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
                    
            if b.status_code == 200:
                ap.append(f'bio')
        if not (config['customisation']['nick'] == ''):
            tries = 0
            while tries < 10:
                try:
                    b= self.client.patch(
                        apiurl,
                        headers=headers,
                        json={"nick": nick}
                        )
                    break
                
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
            if b.status_code == 200:
                ap.append(f'nick')
        
        if config['customisation']['use_custom_pfp']:
            tries = 0
            while tries < 10:
                try:
                    b = self.client.patch(
                        apiurl,
                        headers=headers,
                        json={'avatar': encoded(f'data/avatar/')}
                        )
                    break
                
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
            if b.status_code == 200:
                ap.append(f'avatar')
        
        if config['customisation']['use_custom_banner']:
            tries = 0
            while tries < 10:
                try:
                    b = self.client.patch(
                        apiurl,
                        headers=headers,
                        json={'banner': (f'data/banner/')}
                        )
                    break
                
                except Exception as e:
                    logging.error(f'Failed to execute Requests: '+str(e).capitalize())
                    tries += 1
                    if tries == 10:
                        return
            
            if b.status_code == 200:
                ap.append(f'banner')
        
        if len(ap) in (1,2,3,4):
            logging.info(f'Successfully Humanized. {ap}')
        else:
            logging.error(f'Failed to Humanized.')
            return
    
    def humanizerthread(self, tokens,nick, bio):
        try:
            threads = []
            thr = len(tokens)
            for i in range(thr):
                token = tokens[i]
                t = threading.Thread(target=self.humanizer(token, nick, bio), args=())
                t.daemon = True
                threads.append(t)
                
            for i in range(thr):
                threads[i].start()
                
            for i in range(thr):
                threads[i].join()
        
        except Exception as e:
            logging.error(f'Failed to Execute Threads: '+ str(e).capitalize())
            return

    def thread(self, invite, tokens, guild):
        """"""
        threads = []

        for i in range(len(tokens)):
            token = tokens[i]
            t = threading.Thread(target=self.boost, args=(token, invite, guild))
            t.daemon = True
            threads.append(t)

        for i in range(len(tokens)):
            threads[i].start()

        for i in range(len(tokens)):
            threads[i].join()

        return {
            "success": self.success,
            "failed": self.failed,
            "captcha": self.captcha,
        }
    
def getStock(filename: str):
    tokens = []
    for i in open(filename, "r").read().splitlines():
        if ":" in i:
            i = i.split(":")[2]
            tokens.append(i)
        else:
            tokens.append(i)
    return tokens

def getStock_Auto(filename: str, num_tokens: int):
    with open(filename, "r") as file:
        lines = file.readlines()

    tokens = []
    remaining_lines = []

    for line in lines[:num_tokens]:
        if ":" in line:
            i = line.split(":")[2]
            tokens.append(i)
        else:
            tokens.append(line)    
    remaining_lines.extend(lines[num_tokens:])
    with open(filename, "w") as file:
        for line in remaining_lines:
            file.write(line)

    return tokens

def getinviteCode(inv):
    if "discord.gg" in inv:
        invite = inv.split("discord.gg/")[1]
        return invite
    if "https://discord.gg" in inv:
        invite = inv.split("https://discord.gg/")[1]
        return invite
    if 'discord.com/invite' in inv:
        invite = inv.split("discord.com/invite/")[1]
        return invite
    if 'https://discord.com/invite/' in inv:
        invite = inv.split("https://discord.com/invite/")[1]
        return invite
    else:
        return inv

def checkInvite(invite: str):
    data = requests.get(
        f"https://discord.com/api/v9/invites/{invite}?inputValue={invite}&with_counts=true&with_expiration=true"
    ).json()

    if data["code"] == 10006:
        return False
    elif data:
        return data["guild"]["id"]
    else:
        return False
class BoostModal(Modal):
    def __init__(self):
        super().__init__(title = "Boost")
        self.add_item(
            TextInput(
                label = "Invite",
                placeholder = "Invite code of the server.",
                required = True,
                style = discord.TextStyle.short
            )
        )

        self.add_item(
            TextInput(
                label = "Amount",
                placeholder = "Amount of boosts (must be in numbers).",
                required = True,
                style = discord.TextStyle.short
            )
        )

        self.add_item(
            TextInput(
                label = "Months",
                placeholder = "Number of months (1/3).",
                required = True,
                style = discord.TextStyle.short
            )
        )

        self.add_item(
            TextInput(
                label = "NickName",
                placeholder = ".gg/legendboosts",
                required = False,
                style = discord.TextStyle.short
            )
        )

        self.add_item(
            TextInput(
                label = "Bio",
                placeholder = ".gg/legendboosts",
                required = False,
                style = discord.TextStyle.long
            )
        )
        
    async def on_submit(self, ctx: discord.Interaction):
        invite = self.children[0].value
        amount = int(self.children[1].value)
        months = int(self.children[2].value)
        # Remove conversion to int; these are expected to be strings
        nick = self.children[3].value
        bio = self.children[4].value

        await ctx.response.defer()

        if amount % 2 != 0:
            return await ctx.followup.send(
                embed=discord.Embed(
                    title="`Error`",
                    description="`Number of boosts should be in even numbers`",
                    color=config['embed_config']['color'],
                )
            )

        if months not in [1, 3]:
            return await ctx.followup.send(
                embed=discord.Embed(
                    title="`Error`",
                    description="`Invalid Input`",
                    color=config['embed_config']['color'],
                )
            )

        inviteCode = getinviteCode(invite)
        inviteData = checkInvite(inviteCode)

        if inviteData is False:
            return await ctx.followup.send(
                embed=discord.Embed(
                    title="`Error`",
                    description=f"`Invalid Invite | .gg/{invite}`",
                    color=config['embed_config']['color'],
                )
            )

        file_path = f"data/{months}m.json"
        guild_id = str(ctx.guild.id)

        tokens_json = load_tokens_json(file_path)
        guild_tokens = tokens_json.get(guild_id, [])
        requiredStock = int(amount / 2)

        if requiredStock > len(guild_tokens):
            return await ctx.followup.send(
                embed=discord.Embed(
                    title="`Error`",
                    description="`Not enough stock. Use the command /restock to restock tokens`",
                    color=config['embed_config']['color'],
                )
            )

        # Extract and remove tokens
        tokens_to_use = guild_tokens[:requiredStock]
        tokens_json[guild_id] = guild_tokens[requiredStock:]
        save_tokens_json(tokens_json, file_path)

        # Prepare only token strings for the booster
        token_list = [t["token"] for t in tokens_to_use]

        boost = Booster()
        msg = await ctx.followup.send(
            embed=discord.Embed(
                title="- `Boost Bot Information`",
                description="Joining And Boosting...",
                color=config['embed_config']['color'],
            )
        )

        start = time.time()
        status = boost.thread(inviteCode, token_list, inviteData)
        time_taken = round(time.time() - start, 2)

        final_embed = discord.Embed(
            title="Boost Bot Information",
            description=(f"`Amount:` {amount}x {months}m Boosts\n"
                        f"`Tokens:` {requiredStock}\n"
                        f"`Server Link:` .gg/{inviteCode}\n"
                        f"`Succeeded Boosts:` {len(status['success']) * 2}\n"
                        f"`Failed Boosts:` {len(status['failed'])}\n"
                        f"`Time Took:` {time_taken} seconds\n\n"),
            color=config['embed_config']['color'],
        )
        await msg.edit(embed=final_embed)

        # Optional Webhook Log
        if webhook_url and use_log:
            embed = DiscordEmbed(
                title="- ```Boost Bot Information```",
                description=(f"`Amount:` {amount}x {months}m Boosts\n"
                            f"`Tokens:` {requiredStock}\n"
                            f"`Server Link:` .gg/{inviteCode}\n"
                            f"`Succeeded Boosts:` {len(status['success']) * 2}\n"
                            f"`Failed Boosts:` {len(status['failed'])}\n"
                            f"`Time Took:` {time_taken} seconds\n\n"
                            f"**Failed**\n```{status['failed']}```\n"
                            f"**Captcha**\n```{status['captcha']}```\n"
                            f"**Success**\n```{status['success']}```"),
                color=config['embed_config']['color']
            )
            send_webhook_message(webhook_url, "", embed)

        # Optional Humanizer
        try:
            if config['customisation']['enable']:
                # Use nick and bio if they are provided, otherwise use the values from config
                if nick.strip() and bio.strip():
                    boost.humanizerthread(tokens=token_list, nick=nick, bio=bio)
                else:
                    boost.humanizerthread(
                        tokens=token_list,
                        nick=config['customisation'].get('nick', ''),
                        bio=config['customisation'].get('bio', '')
                    )
        except Exception as e:
            print(e)


statusb = config['status']
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name=f'{statusb}'))
    print(f"{L}[{Fore.WHITE}APP{L}]{L1} |{Style.RESET_ALL} {bot.user} Got Active Using Port 8000.{Fore.RESET}")
    try:        
        await bot.tree.sync()
        logging.info(f'Loaded Successfully In 21ms')
    except Exception as e:
        print(e)

@bot.tree.command(
    name="join", description="Boost a server by using that command."
)
async def join(
    ctx: discord.Interaction
):

    if str(ctx.user.id) not in config["owners_ids"]:
     member = ctx.guild.get_member(ctx.user.id)
     if str(ctx.user.id) not in config["owners_ids"] and not any(str(role.id) in config["admin_role_ids"] for role in member.roles):

        return await ctx.response.send_message(
            embed=discord.Embed(
                title="`Error`",
                description="`Missing Permistions`",
                color=config['embed_config']['color'],
            )
        )

    modal = JoinerModal()
    await ctx.response.send_modal(modal)

@bot.tree.command(
    name="boost", description="Boost a server by using that command."
)
async def boost(
    ctx: discord.Interaction
):

    if str(ctx.user.id) not in config["owners_ids"]:
     member = ctx.guild.get_member(ctx.user.id)
     if str(ctx.user.id) not in config["owners_ids"] and not any(str(role.id) in config["admin_role_ids"] for role in member.roles):

        return await ctx.response.send_message(
            embed=discord.Embed(
                title="`Error`",
                description="`Missing Permistions`",
                color=config['embed_config']['color'],
            )
        )

    modal = BoostModal()
    await ctx.response.send_modal(modal)

def remove(token: str, filename: str):
    tokens = getStock(filename)
    tokens.pop(tokens.index(token))
    f = open(filename, "w")

    for x in tokens:
        f.write(f"{x}\n")

    f.close()


@bot.tree.command(
 name="restockjoin", description="Add new join tokens to the boost bot!"
)
async def restockjoin(
    ctx,
    file: discord.Attachment
):
    member = ctx.guild.get_member(ctx.user.id)
    if str(ctx.user.id) not in config["owners_ids"] and not any(str(role.id) in config["admin_role_ids"] for role in member.roles):
        return await ctx.response.send_message(
            embed=discord.Embed(
                title=f"⚠️`WARNING` - **{bot.user}**",
                description="⚠️ - ```You are not allowed to be using this```",
                color=0xffa600,
            )
        )


    file_path = f"data/join.json"

    content = await file.read()
    lines = content.decode().splitlines()
    guild_id = str(ctx.guild.id)

    tokens_json = load_tokens_json(file_path)

    if guild_id not in tokens_json:
        tokens_json[guild_id] = []

    added_count = 0

    for line in lines:
        parts = line.strip().split(":")
        if len(parts) < 3:
            continue

        email_pass = ":".join(parts[:-1])
        token = parts[-1]

        tokens_json[guild_id].append({
            "email/passwort": email_pass,
            "token": token
        })
        added_count += 1

    save_tokens_json(tokens_json, file_path)

    return await ctx.response.send_message(
        embed=discord.Embed(
            title="✅ JOIN Restock Complete",
            description=f"➕ `{added_count}` tokens added to `join.json` for guild `{guild_id}`",
            color=config['embed_config']['color'],
        )
    )


@bot.tree.command(
 name="restock", description="Add new nitro tokens to the boost bot!"
)
async def restock(
    ctx,
    type: int,  # 1 = 1M, 3 = 3M
    file: discord.Attachment
):
    member = ctx.guild.get_member(ctx.user.id)
    if str(ctx.user.id) not in config["owners_ids"] and not any(str(role.id) in config["admin_role_ids"] for role in member.roles):
        return await ctx.response.send_message(
            embed=discord.Embed(
                title=f"⚠️`WARNING` - **{bot.user}**",
                description="⚠️ - ```You are not allowed to be using this```",
                color=0xffa600,
            )
        )

    if type not in [1, 3]:
        return await ctx.response.send_message(
            embed=discord.Embed(
                title=f"👎 `404 ERROR` - **{bot.user}**",
                description="👎 - ```Wrong input. Use 1 or 3```",
                color=config['embed_config']['color'],
            )
        )

    file_path = f"data/{type}m.json"

    content = await file.read()
    lines = content.decode().splitlines()
    guild_id = str(ctx.guild.id)

    tokens_json = load_tokens_json(file_path)

    if guild_id not in tokens_json:
        tokens_json[guild_id] = []

    added_count = 0

    for line in lines:
        parts = line.strip().split(":")
        if len(parts) < 3:
            continue

        email_pass = ":".join(parts[:-1])
        token = parts[-1]

        tokens_json[guild_id].append({
            "email/passwort": email_pass,
            "token": token
        })
        added_count += 1

    save_tokens_json(tokens_json, file_path)

    return await ctx.response.send_message(
        embed=discord.Embed(
            title="✅ Restock Complete",
            description=f"➕ `{added_count}` tokens added to `{type}m.json` for guild `{guild_id}`",
            color=config['embed_config']['color'],
        )
    )

from discord.ext import commands, tasks


class StockModal(Modal):
    def __init__(self):
        super().__init__(title="Normal Stocks")

        self.add_item(
            TextInput(
                label="Duration",
                placeholder="Months? [1/3]",
                required=True,
                style=discord.TextStyle.short
            )
        )

    async def on_submit(self, ctx: Interaction):
        duration = int(self.children[0].value)
        await ctx.response.defer(ephemeral=True)

        if duration not in [1, 3]:
            return await ctx.followup.send(
                embed=discord.Embed(
                    title="**ERROR**",
                    description="❎ | Invalid type. [1/3] are valid inputs.",
                    color=config['embed_config']['color'],
                ), ephemeral=True
            )

        file_path = f"data/{duration}m.json"
        guild_id = str(ctx.guild.id)

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            stock = len(data.get(guild_id, []))
        except (FileNotFoundError, json.JSONDecodeError):
            stock = 0

        return await ctx.followup.send(
            embed=discord.Embed(
                title=f"```{duration}m Tokens Normal Stock```",
                description=f"\n *`{stock}` Nitro Tokens In Stock* \n *`{stock * 2}` Boosts Available In Stock*",
                color=config['embed_config']['color'],
            ), ephemeral=True
        )

@bot.tree.command(
 name="stock", description="Display the stock of boosts and tokens."
)
async def stock(
    ctx
): 
     member = ctx.guild.get_member(ctx.user.id)
     if str(ctx.user.id) in config["owners_ids"] or any(str(role.id) in config["admin_role_ids"] for role in member.roles): 
      await ctx.response.send_modal(StockModal())
     else:
         await ctx.response.send_message("unauthorised")

@bot.tree.command(name='failed', description="Command to get failed tokens and send them to DMs")
async def get_failed_tokens(ctx):
    member = ctx.guild.get_member(ctx.user.id)
    if str(ctx.user.id) in config["owners_ids"] or any(str(role.id) in config["admin_role_ids"] for role in member.roles):
        try:
            with open("output/failed_boosts.txt", "r") as file:
                failed_tokens = file.read()

            await ctx.user.send(failed_tokens)

            embed = discord.Embed(
                title="Success",
                description="Failed tokens successfully sent to your DMs.",
                color=config['embed_config']['color']
            )
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=f"An error occurred: {str(e)}",
                color=config['embed_config']['color']
            )
    else:
        embed = discord.Embed(
            title="Unauthorized",
            description="You are not authorized to use this command.",
            color=config['embed_config']['color']
        )

    await ctx.response.send_message(embed=embed)

@bot.tree.command(name="send-stock", description="Send stored nitro tokens to a user via DM")
@app_commands.describe(
    type="1 = 1 Month, 3 = 3 Month",
    user="The user to receive the tokens",
    amount="How many tokens to send"
)
async def send_stock(
    interaction: discord.Interaction,
    type: int,
    user: discord.User,
    amount: int
):
    # permissions
    member = interaction.guild.get_member(interaction.user.id)
    is_owner = str(interaction.user.id) in map(str, config["owners_ids"])
    is_admin = any(str(r.id) in map(str, config["admin_role_ids"]) for r in member.roles)
    if not (is_owner or is_admin):
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="⚠️ WARNING",
                description="You are not allowed to use this command.",
                color=0xFFA600
            ),
            ephemeral=True
        )

    # validate type
    if type not in (1, 3):
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="👎 404 ERROR",
                description="Wrong input. Use `1` or `3`.",
                color=config["embed_config"]["color"]
            ),
            ephemeral=True
        )

    # load tokens
    guild_id = str(interaction.guild.id)
    file_path = f"data/{type}m.json"
    with open(file_path, "r") as f:
        tokens_json = json.load(f)
    guild_tokens = tokens_json.get(guild_id, [])

    # validate amount
    if amount < 1 or amount > len(guild_tokens):
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="👎 400 ERROR",
                description=f"Amount must be between 1 and {len(guild_tokens)}.",
                color=config["embed_config"]["color"]
            ),
            ephemeral=True
        )

    # select and remove
    selected = guild_tokens[:amount]
    tokens_json[guild_id] = guild_tokens[amount:]
    with open(file_path, "w") as f:
        json.dump(tokens_json, f, indent=2)

    # write to .txt
    random_id = uuid.uuid4().hex[:8]
    filename = f"{bot.user.name}_{random_id}.txt"
    txt_path = f"data/{filename}"
    with open(txt_path, "w") as f:
        f.write("\n".join(f"{e['email/passwort']}:{e['token']}" for e in selected))

    # DM embed
    dm_embed = discord.Embed(
        title="You have received tokens",
        description=(
            "View the details of the tokens sent to you.\n\n"
            f"**Stock:** {type} Month\n"
            f"**Sent:** {amount} token(s)\n\n"
            "**Fetched Details:**\n"
            f"`You have received {amount} token(s)`"
        ),
        color=config["embed_config"]["color"]
    ).set_footer(text="All Rights Reserved.")

    try:
        await user.send(embed=dm_embed, file=discord.File(txt_path, filename))
    except discord.Forbidden:
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Could not deliver tokens",
                description="I was unable to send a DM to that user.",
                color=0xFF0000
            ),
            ephemeral=True
        )

    # confirm
    await interaction.response.send_message(
        embed=discord.Embed(
        title="You have received tokens",
        description=(
            "View the details of the tokens sent to you.\n\n"
            f"**Stock:** {type} Month\n"
            f"**Sent:** {amount} token(s)\n\n"
            "**Fetched Details:**\n"
            f"`You have received {amount} token(s)`"
        ),
        color=config["embed_config"]["color"]
    ).set_footer(text="All Rights Reserved.")
    )

app = FastAPI()
@app.post('/sellauth/')
async def handle_sellauth_order(data: dict):
    try:
        if data.get("event") != "INVOICE.ITEM.DELIVER-DYNAMIC":
            return "Ignoring non-delivery event."

        email = data["customer"]["email"]
        product_name = data["item"]["product"]["name"]
        quantity = int(data["item"]["quantity"])
        custom_fields = data["item"]["custom_fields"]

        invite = custom_fields.get(config["sellauth"]["custom_field_name"])
        if not invite:
            return "Missing invite field."

        # Extract Boost Info
        match = re.search(r"\d+", product_name)
        amount = int(match.group()) if match else quantity

        months = 1  # default
        if "[" in product_name and "]" in product_name:
            months_str = product_name.split("[")[1].split("]")[0]
            months = int("".join(filter(str.isdigit, months_str)))

        inviteCode = getinviteCode(invite)
        inviteData = checkInvite(inviteCode)

        file_path = f"data/{months}m.json"
        tokens_json = load_tokens_json(file_path)

        # Kombiniere alle Tokens aller Guilds (da keine Guild übergeben wird)
        all_tokens = []
        for guild_tokens in tokens_json.values():
            all_tokens.extend(guild_tokens)

        requiredStock = int(amount / 2)

        if inviteData is False:
            embed = DiscordEmbed(
                title="❌ Invalid Invite - Sellauth",
                description=f"```Email: {email}\nInvite: {invite}```",
                color=config["embed_config"]["color"]
            )
            send_webhook_message(webhook_url, "", embed)
            return "Invalid invite."

        if requiredStock > len(all_tokens):
            embed = DiscordEmbed(
                title="⚠️ Stock Out - Sellauth",
                description=f"```Boosts Needed: {amount}\nStock Available: {len(all_tokens) * 2}```",
                color=config["embed_config"]["color"]
            )
            send_webhook_message(webhook_url, "", embed)
            return "Stock out."

        # Extract and remove tokens
        selected = all_tokens[:requiredStock]
        used_tokens = selected.copy()
        token_strs = [t["token"] for t in selected]

        # Entferne die verwendeten Tokens aus JSON
        for guild_id in list(tokens_json.keys()):
            tokens_json[guild_id] = [t for t in tokens_json[guild_id] if t not in selected]
        save_tokens_json(tokens_json, file_path)

        # Start boost
        boost = Booster()
        start = time.time()
        status = boost.thread(inviteCode, token_strs, inviteData)

        # Retry bei Bedarf
        retry = config['auto_config']['max_retry_on_failure']
        i = 0
        while len(status['success']) < requiredStock and i < retry:
            # Lade erneut aus JSON
            tokens_json = load_tokens_json(file_path)
            all_tokens = []
            for guild_tokens in tokens_json.values():
                all_tokens.extend(guild_tokens)

            retry_amount = requiredStock - len(status['success'])
            retry_tokens = all_tokens[:retry_amount]
            if not retry_tokens:
                break

            retry_token_strs = [t["token"] for t in retry_tokens]
            for guild_id in list(tokens_json.keys()):
                tokens_json[guild_id] = [t for t in tokens_json[guild_id] if t not in retry_tokens]
            save_tokens_json(tokens_json, file_path)

            new_status = boost.thread(inviteCode, retry_token_strs, inviteData)
            status['success'].extend(new_status['success'])
            status['failed'].extend(new_status['failed'])
            status['captcha'].extend(new_status['captcha'])
            i += 1

        time_taken = round(time.time() - start, 2)

        embed = DiscordEmbed(
            title="✅ Boost Complete - Sellauth",
            description=(
                f"**Amount:** {amount} boosts\n"
                f"**Months:** {months}m\n"
                f"**Invite:** .gg/{inviteCode}\n"
                f"**Success:** {len(status['success']) * 2}\n"
                f"**Failed:** {len(status['failed'])}\n"
                f"**Captcha:** {len(status['captcha'])}\n"
                f"**Email:** {email}\n"
                f"**Time:** {time_taken}s\n"
                f"**Retry:** {i}/{retry}"
            ),
            color=config["embed_config"]["color"]
        )

        if config['auto_config']['Use_customization']:
            try:
                boost.humanizerthread(tokens=status['success'])
            except Exception as e:
                print(f"[Customization Error] {e}")

        if len(status['success']) == requiredStock:
            return config['sellauth']['boosts_success_note']
        else:
            return config['sellauth']['boosts_fail_note']

    except Exception as e:
        logging.exception("Sellauth Webhook Error")
        return f"Sellauth Webhook Error: {str(e)}"
    

@app.get("/api/{guild_id}/livestock")
async def get_guild_livestock(guild_id: str):
    try:
        allowed_guilds = config.get("allowed_guilds", [])
        if allowed_guilds and guild_id not in allowed_guilds:
            return {"error": "Guild not authorized"}

        tokens_1m = load_tokens_json("data/1m.json")
        tokens_3m = load_tokens_json("data/3m.json")

        stock_1m = len(tokens_1m.get(guild_id, []))
        stock_3m = len(tokens_3m.get(guild_id, []))

        return {
            "guild_id": guild_id,
            "stock": {
                "1m_tokens": stock_1m,
                "1m_boosts": stock_1m * 2,
                "3m_tokens": stock_3m,
                "3m_boosts": stock_3m * 2
            }
        }
    except Exception as e:
        return {"error": str(e)}


templates = Jinja2Templates(directory="templates")

@app.get("/guild/{guild_id}/livestock", response_class=HTMLResponse)
async def show_stock_page(request: Request, guild_id: str):
    tokens_1m = load_tokens_json("data/1m.json")
    tokens_3m = load_tokens_json("data/3m.json")

    stock_1m = len(tokens_1m.get(guild_id, []))
    stock_3m = len(tokens_3m.get(guild_id, []))

    return templates.TemplateResponse("livestock.html", {
        "request": request,
        "stock_1m": stock_1m,
        "stock_3m": stock_3m,
        "store_name": config["shop"]["shops"][str(guild_id)]["name"],
        "store_url": config["shop"]["shops"][str(guild_id)]["url"],
        "discord_url": config["shop"]["shops"][str(guild_id)]["support_server"],
        "highlight_color": config["shop"]["shops"][str(guild_id)]["color"]
    })

# onliner start
class Status(Enum):
    ONLINE = "online"
    DND = "dnd"
    IDLE = "idle"

class Activity(Enum):
    GAME = 0  
    STREAMING = 1 
    LISTENING = 2 
    WATCHING = 3 
    CUSTOM = 4 
    COMPETING = 5  

class OPCodes(Enum):
    Dispatch = 0  
    Heartbeat = 1
    Identify = 2  
    PresenceUpdate = 3  
    VoiceStateUpdate = 4  
    Resume = 6  
    Reconnect = 7  
    RequestGuildMembers = (
        8  
    )
    InvalidSession = 9 
    Hello = (
        10 
    )
    HeartbeatACK = 11 

class DiscordIntents(IntEnum):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EMOJIS_AND_STICKERS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21

class Presence:
    def __init__(self, online_status: Status) -> None:
        self.online_status: Status = online_status
        self.activities: List[Activity] = []

    def addActivity(
        self, name: str, activity_type: Activity, url: Optional[str]
    ) -> int:
        self.activities.append(
            {
                "name": name,
                "type": activity_type.value,
                "url": url if activity_type == Activity.STREAMING else None,
            }
        )
        return len(self.activities) - 1

    def removeActivity(self, index: int) -> bool:

        if index < 0 or index >= len(self.activities):
            return False
        self.activities.pop(index)
        return True

class DiscordWebSocket:
    def __init__(self) -> None:
        gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        proxies = open("data/proxies.txt", "r").read().splitlines()

        try:
            self.connect(gateway_url, proxy=random.choice(proxies))
        except Exception as e:
            print(f"[!] Proxy connect failed: {e}, retrying without proxy...")
            self.connect(gateway_url)

        self.heartbeat_counter = 0
        self.username: str = None
        self.required_action: str = None
        self.heartbeat_interval: int = None
        self.last_heartbeat: float = None

    def connect(self, gateway_url, proxy=None):
        print(f"Connecting to {gateway_url} with proxy: {proxy}")

    def get_heatbeat_interval(self) -> None:
        resp: Dict = json.loads(self.websocket_instance.recv())
        self.heartbeat_interval = resp["d"]["heartbeat_interval"]

    def authenticate(self, token: str, rich: Presence) -> Union[Dict, bool]:
        self.websocket_instance.send(
            json.dumps(
                {
                    "op": OPCodes.Identify.value, 
                    "d": {
                        "token": token, 
                        "intents": DiscordIntents.GUILD_MESSAGES
                        | DiscordIntents.GUILDS,  
                        "properties": {
                            "os": "linux",
                            "browser": "Brave", 
                            "device": "Desktop", 
                        },
                        "presence": {
                            "activities": [
                                activity for activity in rich.activities
                            ],
                            "status": rich.online_status.value, 
                            "since": time.time(), 
                            "afk": False, 
                        },
                    },
                }
            )
        )
        try:
            resp = json.loads(self.websocket_instance.recv())
            self.username: str = resp["d"]["user"]["username"]
            self.required_action = resp["d"].get("required_action")
            self.heartbeat_counter += 1
            self.last_heartbeat = time.time()

            return resp
        except ConnectionClosedError:
            return False

    def send_heartbeat(self) -> websockets.typing.Data:
        self.websocket_instance.send(
            json.dumps(
                {"op": OPCodes.Heartbeat.value, "d": None}
            ) 
        )

        self.heartbeat_counter += 1
        self.last_heartbeat = time.time()

        resp = self.websocket_instance.recv()
        return resp
def main(token: str, activity: Presence):
    socket = DiscordWebSocket()
    socket.get_heatbeat_interval()

    auth_resp = socket.authenticate(token, activity)
    if not auth_resp:
        return
    while True:
        try:
            if (
                time.time() - socket.last_heartbeat
                >= (socket.heartbeat_interval / 1000) - 5
            ): 
                resp = socket.send_heartbeat()
            time.sleep(0.5)
        except IndentationError:
            print(resp)
def encoded(folder_path: str) -> str:
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    if not files:
        raise Exception(f"No images found in {folder_path}.")
    
    file = random.choice(files)
    path = os.path.join(folder_path, file)

    mime_type, _ = mimetypes.guess_type(path)
    with open(path, "rb") as image:
        b64 = base64.b64encode(image.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"

def onliner(t=None):
    try:
        global tokens
        global encountered_tokens
        tokens = []
        encountered_tokens = set() 
        
        if t is None:
            for file_path in oconfig['onliner_paths']:
                with open(file_path, "r") as token_file:
                    old_tokens: List[str] = token_file.read().splitlines()
                    for token in old_tokens:
                        if "@" in token:
                            new_token = token.split(':')[2]
                            if new_token not in encountered_tokens: 
                                tokens.append(new_token)
                                encountered_tokens.add(new_token)
                        else:
                            if token not in encountered_tokens:  
                                tokens.append(token)
                                encountered_tokens.add(token)
        else:
            encountered_tokens = t                       

        with open("config/onliner.json", "r") as config_file:
            config: Dict[str, Union[List[str], Dict[str, List[str]]]] = json.loads(config_file.read())

        activity_types: List[Activity] = [Activity[x.upper()] for x in config["choose_random_activity_type_from"]]
        online_statuses: List[Status] = [Status[x.upper()] for x in config["choose_random_online_status_from"]]

    except KeyError:
        print("Invalid onliner config! Exiting...")
        exit()

    thrds = []    
    for token in encountered_tokens:
        online_status = random.choice(online_statuses)
        chosen_activity_type = random.choice(activity_types)
        url = None

        if chosen_activity_type == Activity.GAME:
            name = random.choice(config["game"]["choose_random_game_from"])
        elif chosen_activity_type == Activity.STREAMING:
            name = random.choice(config["streaming"]["choose_random_name_from"])
            url = random.choice(config["streaming"]["choose_random_url_from"])
        elif chosen_activity_type == Activity.LISTENING:
            name = random.choice(config["listening"]["choose_random_name_from"])
        elif chosen_activity_type == Activity.WATCHING:
            name = random.choice(config["watching"]["choose_random_name_from"])
        elif chosen_activity_type == Activity.CUSTOM:
            name = random.choice(config["custom"]["choose_random_name_from"])   
        elif chosen_activity_type == Activity.COMPETING:
            name = random.choice(config["competing"]["choose_random_name_from"])

        # Status setzen
        activity = Presence(online_status)
        activity.addActivity(activity_type=chosen_activity_type, name=name, url=url)

        # Avatar & Banner setzen
        patch_payload = {}
        headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

        if oconfig["customisation"].get("use_custom_pfp"):
            try:
                patch_payload["avatar"] = encoded("data/avatar/")
            except Exception as e:
                print(f"[Avatar] Error for token {token[:20]}...: {e}")

        if oconfig["customisation"].get("use_custom_banner"):
            try:
                patch_payload["banner"] = encoded("data/banner/")
            except Exception as e:
                print(f"[Banner] Error for token {token[:20]}...: {e}")

        if patch_payload:
            try:
                res = requests.patch(
                    "https://discord.com/api/v9/users/@me",
                    headers=headers,
                    json=patch_payload
                )
                if res.status_code == 200:
                    print(f"[✓] Avatar/Banner gesetzt für {token[:20]}...")
                else:
                    print(f"[✗] PATCH failed für {token[:20]}... Code: {res.status_code}")
            except Exception as e:
                print(f"[PATCH] Exception für {token[:20]}: {e}")

        # Thread starten für Online-Präsenz
        x = Thread(target=main, args=(token, activity))
        thrds.append(x)
        x.start()
#onliner end
def start_bot():
    bot.run(config["token"])


def start_bot_thread():
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
if True:
    if __name__ == "__main__":
        if oconfig['use_onliner']:
            onliner()
        start_bot_thread()
        if config['auto_config']['use_autoboosting'] == True:
            port = config['port']
            run("__main__:app", host="0.0.0.0", port=port)
else:
       logging.error("Invalid Key [ Unauthorised ]")
       time.sleep(5)
       sys.exit()