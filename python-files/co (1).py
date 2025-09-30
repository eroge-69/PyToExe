import subprocess
import uuid
import re
import base64
import time
import requests
subprocess.call([
    'pip',
    'install',
    'requests'])
import requests
import telebot
subprocess.call([
    'pip',
    'install',
    'telebot'])
import telebot
import psutil
subprocess.call([
    'pip',
    'install',
    'psutil'])
import psutil
import os
from telebot import types
session_bypass = 'yy'
token = open('Token.txt', 'r').read()
myid = int(open('chatid.txt', 'r').read())
bot = telebot.TeleBot(token)
sessionmain = 'yy'
ses2 = 'yy'
ses3 = 'yy'
def login(message):
    i = message.text.split('/login ')[1]
    user = i.split(':')[0]
    password = i.split(':')[1]

    SaheHead = {
        'X-Fb-Connection-Type': 'WIFI',
        'X-Ig-Connection-Type': 'WIFI',
        'X-Ig-Capabilities': '3brTv10=',
        'X-Ig-App-Id': '567067343352427',
        'Priority': 'u=3',
        'User-Agent': 'Instagram 389.0.0.14.102 Android',
        'Accept-Language': 'en-US',
        'X-Mid': 'Y2OyGAABAAHUuMwRNWwnswHWeQXQ',
        'Ig-Intended-User-Id': '0',
        'Ig-U-Ds-User-Id': '0',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Fb-Http-Engine': 'Liger',
        'X-Fb-Client-Ip': 'True',
        'X-Fb-Server-Cluster': 'True'
    }

    data = {
        'phone_id': str(uuid.uuid4()),
        'adid': str(uuid.uuid4()),
        'guid': str(uuid.uuid4()),
        'device_id': 'android-' + str(uuid.uuid4()),
        'username': user,
        'enc_password': '#PWD_INSTAGRAM_BROWSER:0:1589682409:' + password
    }

    Req = requests.post(
        'https://i.instagram.com/api/v1/accounts/login/',
        data=data,
        headers=SaheHead
    )

    if 'logged_in_user' in Req.text:
        sessionid = Req.cookies.get('sessionid')
        if not sessionid:
            after = str(base64.b64decode(
                Req.headers.get('ig-set-authorization').split(':')[2]
            ))
            sessionid = re.search('"sessionid":"(.*?)"', after).groups()[0]

        bot.reply_to(message, text=f'''*{sessionid}*''', parse_mode='markdown')

    elif '2F3:verify_email_code:1:button::,2F3:select_verification_method:2:button::,AD1:login_landing:3:button::' in Req.text:
        bot.reply_to(message, text='* Challenge Required Accept And Try Again*',
                     parse_mode='markdown')

    else:
        bot.reply_to(message, text='* Wrong Information.*',
                     parse_mode='markdown')
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == myid:
        bot.reply_to(
            message,
            text=f"* Welcome to Flex V1 {message.chat.first_name}*",
            parse_mode='markdown'
        )
        button = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button.row('Swap')
        button.row('Bypass')
        button.row('Settings')
        bot.reply_to(
            message,
            text='* Select Mode*',
            parse_mode='markdown',
            reply_markup=button
        )

@bot.message_handler(func=lambda message: message.chat.id == myid)
def kb_answer(message):
    # SETTINGS MENU
    if message.text == 'Settings':
        button = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button.row('Proxy Swap', 'Proxy Bypass')
        button.row('name', 'bio', 'gif')
        button.row('Webhook Swap', 'Webhook Bypass', 'Auto Releaser')
        button.row('Back')
        bot.reply_to(message, '* Select Mode*', parse_mode='markdown', reply_markup=button)

    elif message.text == 'Webhook Swap':
        dd = bot.reply_to(message, '* Send*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_discord)

    elif message.text == 'Webhook Bypass':
        dd = bot.reply_to(message, '* Send*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_discordb)

    elif message.text == 'gif':
        dd = bot.reply_to(message, '* Send*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_gif)

    elif message.text == 'BackUp':
        dd = bot.reply_to(message, '* Do You Want To use Backup (on/off) *', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_backupchoise)

    elif message.text == 'Checkblock':
        dd = bot.reply_to(message, '*Checkblock (on/off) *', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_checkblock)

    elif message.text == 'name':
        dd = bot.reply_to(message, '* Send*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_name)

    elif message.text == 'bio':
        dd = bot.reply_to(message, '* Send Bio*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_bio)

    elif message.text == 'Auto Releaser':
        dd = bot.reply_to(message, '* Enable Relase in Auto (on/off)*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_releaser)

    elif message.text == 'Proxy Swap':
        dd = bot.reply_to(message, '* Send Swap Proxy*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_proxys)

    elif message.text == 'Proxy Bypass':
        dd = bot.reply_to(message, '* Send Bypass Proxy*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_proxyb)

    elif message.text == 'Back':
        button = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button.row('Swap')
        button.row('Bypass')
        button.row('Settings')
        bot.reply_to(message, '* Select Mode*', parse_mode='markdown', reply_markup=button)

    # BYPASS MENU
    elif message.text == 'Bypass':
        button = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button.row('Run Bypass', 'Stop Bypass')
        button.row('Set Bypass Session', 'Set Threads Auto')
        button.row('Set Auto Sessions', 'R/s release')
        button.row('Back')
        bot.reply_to(message, '* Select Bypass Mode*', parse_mode='markdown', reply_markup=button)

    elif message.text == 'Set Bypass Session':
        dd = bot.reply_to(message, '* Send Session*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_session)

    elif message.text == 'R/s release':
        dd = bot.reply_to(message, '* Send R/s*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_rs)

    elif message.text == 'Run Bypass':
        args = ['bypass.exe', session_bypass]
        subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=False)

    elif message.text == 'Stop Bypass':
        for proc in psutil.process_iter():
            if proc.name() == 'bypass.exe':
                proc.kill()
        subprocess.call(['taskkill', '/F', '/IM', 'bypass.exe'])
        bot.reply_to(message, '*Bypassing tool closed*', parse_mode='markdown')

    elif message.text == 'Set Auto Sessions':
        dd = bot.reply_to(message, '* Send Sessions*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_sessions)

    elif message.text == 'Set Threads Auto':
        dd = bot.reply_to(message, '* Send Threads*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_threadbypass)

    # SWAP MENU
    elif message.text == 'Swap':
        button = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button.row('Run', 'Close')
        button.row('Set Main Session', 'Set Target Session')
        button.row('Checkblock', 'Threads Swap')
        button.row('Back')
        bot.reply_to(message, '* Select Swap Mode*', parse_mode='markdown', reply_markup=button)

    elif message.text == 'Set Main Session':
        dd = bot.reply_to(message, '* Send Session Main *', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_mainsession)

    elif message.text == 'Set Target Session':
        dd = bot.reply_to(message, '* Send Session Target *', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_targetsession)

    elif message.text == 'Threads Swap':
        dd = bot.reply_to(message, '* Send Swap Threads *', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_threadswap)

    elif message.text == 'Backup Session':
        dd = bot.reply_to(message, '* Send Backup Session *', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_backupsession)

    elif message.text == 'Run':
        args = ['swap.exe']
        subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=False)

    elif message.text == 'Close':
        for proc in psutil.process_iter():
            if proc.name() == 'swap.exe':
                proc.kill()
        subprocess.call(['taskkill', '/F', '/IM', 'swap.exe'])
        bot.reply_to(message, '*Swapping tool closed*', parse_mode='markdown')

    elif message.text == 'Grab Sessions':
        dd = bot.reply_to(message, '* Send File Of Accounts*', parse_mode='markdown')
        bot.register_next_step_handler(dd, set_sessionsgrabber)
def set_sessions(message):
    file_path = 'sess.txt'
    os.remove('accounts.txt')
    if FileNotFoundError:
        pass
    if message.content_type == 'text':
        x = open('accounts.txt', 'a', encoding = 'utf-8')
        x.write(message.text)
        None(None, None)
        if not None:
            pass
        bot.reply_to(message, ' Done Save Sessions', parse_mode = 'markdown')
    if message.content_type == 'document':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        x = open(file_path, 'wb')
        x.write(downloaded_file)
        None(None, None)
        if not None:
            pass
        x = open('accounts.txt', 'a')
        for line in open(file_path, 'r').read().splitlines():
            x.write(line + '\n')
            None(None, None)
            if not None:
                pass
        bot.reply_to(message, ' Done Save Sessions', parse_mode = 'markdown')
        os.remove(file_path)
    args = [
        'check.exe']
    process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, shell = False)
    time.sleep(15)
    process.kill()


def set_sessionsgrabber(message):
    file_path = 'zx.txt'
    os.remove('acc.txt')
    if FileNotFoundError:
        pass
    if message.content_type == 'text':
        x = open('acc.txt', 'a', encoding = 'utf-8')
        x.write(message.text)
        None(None, None)
        if not None:
            pass
        bot.reply_to(message, ' Done Save Sessions', parse_mode = 'markdown')
    if message.content_type == 'document':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        x = open(file_path, 'wb')
        x.write(downloaded_file)
        None(None, None)
        if not None:
            pass
        x = open('acc.txt', 'a', encoding = 'utf-8')
        for i in open(file_path, 'r', encoding = 'utf-8').read().splitlines():
            x.write(i + '\n')
            None(None, None)
            if not None:
                pass
        bot.reply_to(message, ' Done Save Sessions', parse_mode = 'markdown')
        os.remove(file_path)
    args = [
        'Ex.exe']
    process = subprocess.run(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, shell = False)
    time.sleep(35)
    process.kill()


def set_threadbypass(message):
    open('autothread.txt', 'w', encoding = 'utf-8').write('')
    x = open('autothread.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '*Done save threads*', parse_mode = 'markdown')


def set_threadswap(message):
    open('swapthread.txt', 'w', encoding = 'utf-8').write('')
    x = open('swapthread.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '*Done save threads*', parse_mode = 'markdown')


def set_checkblock(message):
    open('checkblock.txt', 'w', encoding = 'utf-8').write('')
    x = open('checkblock.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Save Your Choise*', parse_mode = 'markdown')


def set_backupchoise(message):
    open('backupchoise.txt', 'w', encoding = 'utf-8').write('')
    x = open('backupchoise.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Save Your Choise*', parse_mode = 'markdown')


def set_releaser(message):
    open('releaser.txt', 'w', encoding = 'utf-8').write('')
    x = open('releaser.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Save Your Choise*', parse_mode = 'markdown')


def set_discord(message):
    open('discord.txt', 'w', encoding = 'utf-8').write('')
    x = open('discord.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Saved*', parse_mode = 'markdown')


def set_discordb(message):
    open('discordb.txt', 'w', encoding = 'utf-8').write('')
    x = open('discordb.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Saved*', parse_mode = 'markdown')


def set_gif(message):
    open('gif.txt', 'w', encoding = 'utf-8').write('')
    x = open('gif.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Gif Saved*', parse_mode = 'markdown')


def set_name(message):
    open('name.txt', 'w', encoding = 'utf-8').write('')
    x = open('name.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Name Saved*', parse_mode = 'markdown')


def set_bio(message):
    open('bio.txt', 'w', encoding = 'utf-8').write('')
    x = open('bio.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Bio Saved*', parse_mode = 'markdown')


def set_rs(message):
    open('rsrelease.txt', 'w', encoding = 'utf-8').write('')
    x = open('rsrelease.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done save r/s*', parse_mode = 'markdown')


def set_mainsession(message):
    global session_bypass
    session_bypass = message.text
    open('mainsession.txt', 'w', encoding = 'utf-8').write('')
    x = open('mainsession.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Save Main Session*', parse_mode = 'markdown')
    args = [
        'login.exe',
        session_bypass]
    process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, shell = False)


def set_targetsession(message):
    global session_bypass
    session_bypass = message.text
    open('targetsession.txt', 'w', encoding = 'utf-8').write('')
    x = open('targetsession.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Save Target Session*', parse_mode = 'markdown')
    args = [
        'login.exe',
        session_bypass]
    process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, shell = False)


def set_backupsession(message):
    global session_bypass
    session_bypass = message.text
    open('backupsession.txt', 'w', encoding = 'utf-8').write('')
    x = open('backupsession.txt', 'a', encoding = 'utf-8')
    x.write(message.text)
    None(None, None)
    if not None:
        pass
    bot.reply_to(message, '* Done Save Session*', parse_mode = 'markdown')
    args = [
        'login.exe',
        session_bypass]
    process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, shell = False)


def set_proxyb(message):
    if message.content_type == 'text':
        open('proxyb.txt', 'w', encoding = 'utf-8').write('')
        x = open('proxyb.txt', 'a', encoding = 'utf-8')
        x.write(message.text)
        None(None, None)
        if not None:
            pass
        bot.reply_to(message, '* Done Save Proxy*', parse_mode = 'markdown')
        return None
    if None.content_type == 'document':
        open('proxyb.txt', 'w', encoding = 'utf-8').write('')
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        x = open('proxyb.txt', 'wb')
        x.write(downloaded_file)
        None(None, None)
        if not None:
            pass
        bot.reply_to(message, '* Done Save Proxy*', parse_mode = 'markdown')
        return None


def set_proxys(message):
    if message.content_type == 'text':
        open('proxys.txt', 'w', encoding = 'utf-8').write('')
        x = open('proxys.txt', 'a', encoding = 'utf-8')
        x.write(message.text)
        None(None, None)
        if not None:
            pass
        bot.reply_to(message, '* Done Save Proxy*', parse_mode = 'markdown')
        return None
    if None.content_type == 'document':
        open('proxys.txt', 'w', encoding = 'utf-8').write('')
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        x = open('proxys.txt', 'wb')
        x.write(downloaded_file)
        None(None, None)
        if not None:
            pass
        bot.reply_to(message, '* Done Save Proxy*', parse_mode = 'markdown')
        return None


def set_session(message):
    global session_bypass
    session_bypass = message.text
    bot.reply_to(message, '* Done Save Session*', parse_mode = 'markdown')
    args = [
        'login.exe',
        session_bypass]
    process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True, shell = False)

bot.infinity_polling()
