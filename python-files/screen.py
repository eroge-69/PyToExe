import telebot
import pyautogui
import os

# --- НАСТРОЙКИ ---
BOT_TOKEN = '7924904605:AAHDRG8dMs0E5gvs-rDp5r9iTcKe1cInWTY'  # <<<--- Вставьте сюда токен вашего бота
USER_ID = 5622791576             # Ваш ID в Telegram, чтобы только вы могли использовать команду

# --- ИНИЦИАЛИЗАЦИЯ БОТА ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- ОБРАБОТЧИКИ КОМАНД ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Отправляет приветственное сообщение."""
    bot.reply_to(message, "Привет! Отправь мне команду /screen, чтобы получить скриншот экрана.")

@bot.message_handler(commands=['screen'])
def send_screenshot(message):
    """Делает скриншот и отправляет его в ответ на команду /screen."""
    # Проверяем, что команду отправил разрешенный пользователь
    if message.from_user.id == USER_ID:
        try:
            bot.reply_to(message, "Секунду, делаю скриншот...")
            
            # Имя файла для скриншота
            file_path = 'screenshot.png'
            
            # Делаем и сохраняем скриншот
            pyautogui.screenshot(file_path)
            
            # Открываем файл и отправляем его как фото
            with open(file_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
            
            # Удаляем файл скриншота после отправки, чтобы не засорять диск
            os.remove(file_path)
            
        except Exception as e:
            bot.reply_to(message, f"Ой, что-то пошло не так: {e}")
    else:
        # Если ID пользователя не совпадает, отправляем сообщение об отказе в доступе
        bot.reply_to(message, "У тебя нет прав на выполнение этой команды.")

# --- ЗАПУСК БОТА ---
print("Бот запущен...")
bot.polling(none_stop=True)