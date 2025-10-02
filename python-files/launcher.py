import os
import sys
import subprocess
import time
import json

# ========== SOZLAMALAR ==========
BOT_TOKEN = "7908116465:AAG2ACIryQfg-iQDW8WLsPqB4lwZc3dvl3Q"
ADMIN_CHAT_ID = "6990611858"
REQUIRED_PACKAGES = ["telethon", "pyautogui", "psutil", "pillow"]
# ================================

def send_telegram_message(text):
    try:
        import urllib.request
        import urllib.parse
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": ADMIN_CHAT_ID, "text": text}).encode()
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req)
    except:
        pass  # Xabar yuborish muvaffaqiyatsiz bo'lsa ham davom et

def run_command(cmd, shell=False):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout
    except:
        return False, ""

def install_python():
    print("[*] Python topilmadi. O'rnatishga harakat qilinmoqda...")
    success, _ = run_command(["winget", "install", "Python.Python.3"], shell=True)
    if not success:
        # MSI orqali yuklab o'rnatish
        import urllib.request
        url = "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
        exe_path = os.path.join(os.environ["TEMP"], "python-installer.exe")
        try:
            urllib.request.urlretrieve(url, exe_path)
            run_command([exe_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"], shell=True)
            os.remove(exe_path)
        except:
            pass
    time.sleep(5)

def install_packages():
    print("[*] Kerakli kutubxonalarni o'rnatish...")
    for package in REQUIRED_PACKAGES:
        print(f"  - {package}")
        run_command([sys.executable, "-m", "pip", "install", "--quiet", package], shell=True)

def main():
    # Python versiyasini tekshirish
    if not sys.version_info >= (3, 8):
        print("[!] Python 3.8+ kerak.")
        send_telegram_message("⚠️ Python 3.8+ topilmadi. O'rnatish kerak.")
        install_python()
        return

    # Pip mavjudligini tekshirish
    try:
        import pip
    except ImportError:
        print("[!] pip topilmadi.")
        send_telegram_message("⚠️ pip topilmadi. Python qayta o'rnatish kerak.")
        return

    # Kutubxonalarni tekshirish
    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"[!] Yo'q kutubxonalar: {missing}")
        send_telegram_message(f"📦 Yo'q kutubxonalar: {', '.join(missing)}\n🔄 O'rnatish boshlandi...")
        install_packages()

    # bot.py ni ishga tushirish
    bot_path = os.path.join(os.path.dirname(__file__), "bot.py")
    if not os.path.exists(bot_path):
        send_telegram_message("❌ bot.py fayli topilmadi!")
        return

    print("[*] bot.py ishga tushirilmoqda...")
    success, _ = run_command([sys.executable, bot_path], shell=False)
    if not success:
        send_telegram_message("💥 bot.py ishlamadi! Xatolik yuz berdi.")
    else:
        print("[+] bot.py muvaffaqiyatli ishga tushdi.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        send_telegram_message(f"🚨 Launcher xatosi: {str(e)}")