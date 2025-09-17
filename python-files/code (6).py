
import telebot
import os
import subprocess
import time
from telebot import types

# Замените на свой токен бота
TOKEN = '8273213885:AAHI6Z4M4__QS8z1LzjsZzoErTaJVYof2rY'
bot = telebot.TeleBot(TOKEN)

# Замените на ID вашего администратора Telegram
ADMIN_ID = 7948912553

# Путь к папке, с которой начинается навигация
START_PATH = "C:\\"

# Словарь для хранения текущего пути для каждого пользователя
user_paths = {}

# Функция для создания клавиатуры с файлами и папками
def create_keyboard(path, user_id, is_main_menu=False):
    markup = types.InlineKeyboardMarkup(row_width=2)
    try:
        items = os.listdir(path)
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                button_text = f"📄 {item}"  # Символ файла
                callback_data = f"file:{item_path}"
            elif os.path.isdir(item_path):
                button_text = f"📁 {item}"  # Символ папки
                callback_data = f"folder:{item_path}"
            else:
                continue # Пропускаем элементы, которые не являются файлами или папками
            markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
    except PermissionError:
        markup.add(types.InlineKeyboardButton("⚠️ Отказано в доступе", callback_data="no_access"))

    # Кнопка "Назад"
    if path != START_PATH and not is_main_menu:
        parent_path = os.path.dirname(path)
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"folder:{parent_path}"))

    #Кнопки главных команд
    if is_main_menu:
        markup.add(types.InlineKeyboardButton("📁 Открыть файл", callback_data="open_file"))
        markup.add(types.InlineKeyboardButton("📷 Скриншот", callback_data="screenshot"))
        markup.add(types.InlineKeyboardButton("❌ Завершение работы", callback_data="shutdown"))
        markup.add(types.InlineKeyboardButton("📝 Текст в файл", callback_data="text_to_file"))
    elif not is_main_menu:
        markup.add(types.InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu"))


    return markup

# Проверка, является ли пользователь администратором
def is_admin(user_id):
    return user_id == ADMIN_ID

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    user_id = message.from_user.id
    user_paths[user_id] = START_PATH
    markup = create_keyboard(START_PATH, user_id, is_main_menu=True)
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите действие:", reply_markup=markup)

# Обработчик callback-запросов (нажатия на кнопки)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "У вас нет прав для выполнения этой команды.")  # Уведомление вверху экрана
        return

    user_id = call.from_user.id
    data = call.data

    if data.startswith("folder:"):
        path = data[7:]
        user_paths[user_id] = path
        markup = create_keyboard(path, user_id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif data.startswith("file:"):
        file_path = data[5:]
        try:
            # Отправляем команду на открытие файла (замените на ваш метод)
            # Здесь предполагается, что у вас есть client.exe, который умеет открывать файлы
            #subprocess.Popen(['python', 'client.py', 'open_file', file_path])  # Запуск скрипта на том же компьютере
            send_command_to_client('open_file', file_path)
            bot.send_message(call.message.chat.id, f"Файл открыт: {os.path.basename(file_path)}")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка при открытии файла: {e}")
    elif data == "open_file":
        user_paths[user_id] = START_PATH
        markup = create_keyboard(START_PATH, user_id)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif data == "screenshot":
        try:
            # Отправляем команду на создание скриншота
            #subprocess.Popen(['python', 'client.py', 'screenshot'])  # Запуск скрипта на том же компьютере
            send_command_to_client('screenshot')
            bot.send_message(call.message.chat.id, "Делаю скриншот...")
            time.sleep(5) # Даем время на создание скриншота
            try:
                 with open('screenshot.png', 'rb') as photo:
                    bot.send_photo(call.message.chat.id, photo)
            except FileNotFoundError:
                bot.send_message(call.message.chat.id, "Не удалось найти скриншот")

        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка при создании скриншота: {e}")
    elif data == "shutdown":
         try:
            # Отправляем команду на завершение работы
            #subprocess.Popen(['python', 'client.py', 'shutdown'])  # Запуск скрипта на том же компьютере
            send_command_to_client('shutdown')
            bot.send_message(call.message.chat.id, "Выключаю компьютер...")
         except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка при выключении: {e}")
    elif data == "text_to_file":
        bot.send_message(call.message.chat.id, "Введите текст для файла:")
        bot.register_next_step_handler(call.message, create_text_file)
    elif data == "main_menu":
        markup = create_keyboard(START_PATH, user_id, is_main_menu=True)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

def create_text_file(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    text = message.text
    try:
        # Отправляем команду на создание текстового файла
        #subprocess.Popen(['python', 'client.py', 'create_text_file', text])
        send_command_to_client('create_text_file', text)
        bot.send_message(message.chat.id, "Файл создан и открыт на компьютере.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при создании файла: {e}")

def send_command_to_client(command, *args):
    # Замените 'client.exe' на имя вашего скомпилированного файла
    cmd = ['client.exe', command] + list(args)
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)  # Скрытие окна
# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
