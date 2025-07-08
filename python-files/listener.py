import os
import sys
import platform
import win32com.client
from telegram.ext import Updater, CommandHandler

# === НАСТРОЙКИ ===
TELEGRAM_BOT_TOKEN = "8126146148:AAEufdsps2nkpRmxG3IC1LnBIcMJEUIcCvA"
AUTHORIZED_USER_ID = 1371784792  # ← ВАШ Telegram ID (как число)

# === Добавление в автозагрузку ===
def add_to_startup():
    startup_path = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    script_path = sys.executable
    shortcut_path = os.path.join(startup_path, "Listener.lnk")

    if not os.path.exists(shortcut_path):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = script_path
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = script_path
            shortcut.save()
            print("Добавлено в автозагрузку.")
        except Exception as e:
            print(f"Ошибка автозагрузки: {e}")

# === Обработчики команд ===
def shutdown(update, context):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        update.message.reply_text("Доступ запрещён.")
        return

    update.message.reply_text("Выключаю компьютер...")
    if platform.system() == "Windows":
        os.system("shutdown /s /t 0")
    elif platform.system() == "Linux":
        os.system("shutdown now")

def reboot(update, context):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        update.message.reply_text("Доступ запрещён.")
        return

    update.message.reply_text("Перезагружаю компьютер...")
    if platform.system() == "Windows":
        os.system("shutdown /r /t 0")
    elif platform.system() == "Linux":
        os.system("reboot")

# === Запуск ===
def main():
    add_to_startup()

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("shutdown", shutdown))
    dp.add_handler(CommandHandler("reboot", reboot))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
