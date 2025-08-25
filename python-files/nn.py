import os
import time
import requests
import psutil
from telegram.ext import Updater, CommandHandler

# Apna BOT Token aur User ID
TOKEN = '7663326196:AAENGSVfTRfanyNCOlD50EiepgAQf1EdpXY'
USER_ID = 5067707018  # Apna Telegram user ID

# Laptop start hone ka time save karna
boot_time = time.time()

# Laptop start hone par message bhejna
def send_startup_message():
    battery = psutil.sensors_battery()
    battery_percent = f"{battery.percent}%" if battery else "N/A"
    msg = f"💻 Laptop ON ho gaya hai!\n🔋 Battery: {battery_percent}\n⏳ Uptime: 0h 0m 0s"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": USER_ID, "text": msg}
    requests.post(url, data=data)

def start(update, context):
    if update.effective_user.id == USER_ID:
        update.message.reply_text("Laptop ON hai ✅.\n👉 /time bhejo uptime dekhne ke liye.\n👉 /off bhejo to shutdown hoga.")
    else:
        update.message.reply_text("❌ Access denied.")

# 🔹 Laptop kitne time se chal raha hai (uptime)
def uptime(update, context):
    if update.effective_user.id == USER_ID:
        current_time = time.time()
        seconds = int(current_time - boot_time)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        battery = psutil.sensors_battery()
        battery_percent = f"{battery.percent}%" if battery else "N/A"

        update.message.reply_text(f"⏳ Uptime: {hours}h {minutes}m {seconds}s\n🔋 Battery: {battery_percent}")
    else:
        update.message.reply_text("❌ Access denied.")

# 🔹 Sirf command se hi shutdown hoga
def off(update, context):
    if update.effective_user.id == USER_ID:
        update.message.reply_text("⚠️ Laptop shutdown ho raha hai...")
        os.system("shutdown /s /t 1")
    else:
        update.message.reply_text("❌ Access denied.")

if __name__ == "__main__":
    send_startup_message()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("time", uptime))   # new uptime command
    dp.add_handler(CommandHandler("off", off))

    updater.start_polling()
    updater.idle()
