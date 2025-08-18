import telebot
import subprocess
import psutil
import os
bot = telebot.TeleBot('7805340460:AAHYAMgxwINGhfqo3mm9vtj5Qlp-L7pKGks')


#Тг
@bot.message_handler(commands=['tg'])
def main(message):
    bot.send_message(message.chat.id, 'Открываю Тг...')
    process = subprocess.Popen(["D:\Program Files\Telegram Desktop\Telegram.exe"])
@bot.message_handler(commands=['cltg'])
def main(message):
    bot.send_message(message.chat.id, 'Закрываю Тг...')
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'Telegram.exe':
            proc.terminate()

#Стоп
@bot.message_handler(commands=['stop'])
def main(message):
        bot.send_message(message.chat.id, 'Работа приостоновленна')
        bot.polling(none_stop=False)

#Браузер
@bot.message_handler(commands=['op'])
def main(message):
    bot.send_message(message.chat.id, 'Открываю Браузер...')
    process = subprocess.run([r'C:\Users\piopi\Opera GX\opera.exe'])
@bot.message_handler(commands=['clop'])
def main(message):
    bot.send_message(message.chat.id, 'Закрываю Браузер...')
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'opera.exe':
            proc.terminate()


bot.polling(none_stop=True)




