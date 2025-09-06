import os
import subprocess
import telebot

bot = telebot.TeleBot('8062702509:AAEeRIOLWAQXDJQoqcygd4Y47ZOlD9ibQws')

cmd = "quser"
out = subprocess.check_output(cmd).decode("cp866")
a = out.split('\n')[1:]
for i in a:
    if i and i[0]=='>':
        s = i.split('  ')
        s.extend(s[-1].split(' '))
        while '' in s:
            s.remove('')
        s.pop(-3)
        session = {"user":s[0][1:], "dat":f"{s[-2]} {s[-1][:-1]}"}

bot.send_message(chat_id=1802442780, text=f"{session['dat']} пользователь {session['user']} вошел в систему.")