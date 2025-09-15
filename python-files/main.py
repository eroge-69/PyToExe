import os
import telebot

# os.startfile("C:\Users\Mserv\Downloads\AnyDesk.exe")

bot = telebot.TeleBot("8050293718:AAGmspDLY7leFlagCkic4k3Ka5tpydhvuKY")

bot.remove_webhook()

@bot.message_handler(commands=["start"])
def start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True,one_time_keyboard=False)

    btn1 = telebot.types.KeyboardButton("запустить")
    btn2 = telebot.types.KeyboardButton("остановить")

    keyboard.add(btn1,btn2)

    bot.send_message(message.chat.id,"Выбери действие",reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def getmessages(message):

    if message.text == "запустить":
        bot.send_message(message.from_user.id,"сервер запускается ожидайте")
        os.stsrtfile(r"C:\Users\Mserv\Desktop\Новая папка\run.bat")
    elif message.text == "остановить":
        bot.send_message(message.from_user.id, "сервер останавливается")
        os.system('taskkill /F /IM java.exe')

bot.polling()
