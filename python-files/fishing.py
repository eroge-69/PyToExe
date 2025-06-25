import random
import time
import threading
import telebot

# Токен вашего бота (получите его у @BotFather)
API_TOKEN = '7914309453:AAFcI3cztaF-omY_Ek3WUDrvLpBT1X4yqBo'

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Список рыб с их минимальным и максимальным размерами
FISH_LIST = [
    {"name": "Карась", "min_size": 50, "medium_size": 750, "max_size": 3000},
    {"name": "Щука", "min_size": 300, "medium_size": 2000, "max_size": 7000},
    {"name": "Сом", "min_size": 500, "medium_size": 5000, "max_size": 15000},
    {"name": "Окунь", "min_size": 20, "medium_size": 1000, "max_size": 4000},
    {"name": "Золотая рыбка", "min_size": 7, "medium_size": 777, "max_size": 7777}
]

# Словарь для хранения состояния пользователей
user_states = {}

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    print(f"/start by: {message}")


    welcome_message = "🐟 Добро пожаловать в Рыбалка Бот! 🎣 \nВот что вы можете делать: \n• Отправьте команду /fish, чтобы закинуть удочку. \n• Отправьте команду /cancel, чтобы отменить заброс. \n• Отправьте команду /start, чтобы увидеть эту справку снова. \n\n📋 Список доступной рыбы:\n• Карась\n• Щука \n• Сом \n• Окунь\n• Золотая рыбка \n\n💡 Особенности рыбалки:\n• Время ожидания после заброса составляет от 3 до 10 секунд.\n• Размер пойманной рыбы зависит от её вида и вашей удачи!\n• Рыба может быть небольшой или трофейной — всё решает случайность. Рыба меньшего размера попадается в большей вероятность. Постарайтесь поймать рыбу как можно большего размера! \n\nЛовите рыбу вместе с друзьями и соревнуйтесь по размеру рыб! - Пригласите товарищей, поделившись сслыкой: https://t.me/omegafisher_bot (кликабельно)\n\nУдачи в рыбалке! 🍀\n\nПоддержка бота: @disccsz"




    bot.send_photo(
        message.chat.id,
        photo=open("C://Users/artem/Desktop/start.png", "rb"),
        caption=welcome_message, reply_to_message_id=message.message_id
            )

# Команда /fish - закинуть удочку
@bot.message_handler(commands=['fish'])
def start_fishing(message):
    user_id = message.from_user.id
    print(f"/fish by: {user_id}")

    # Проверяем, не ловит ли пользователь уже рыбу
    if user_id in user_states and user_states[user_id].get("fishing", False):
        bot.reply_to(message, "Вы уже ловите рыбу! Подождите или отмените заброс командой /cancel.")
        return

    # Устанавливаем состояние "ловит рыбу"
    user_states[user_id] = {"fishing": True, "cancel": False}

    bot.send_photo(
        message.chat.id,
        photo=open("C://Users/artem/Desktop/fish.png", "rb"),
        caption="Вы закинули удочку... Ждите поклёвку!" ,
        reply_to_message_id=message.message_id
            )

    # Запускаем процесс ловли рыбы в отдельном потоке
    threading.Thread(target=fishing_process, args=(message,), daemon=True).start()

# Функция для процесса ловли рыбы
def fishing_process(message):
    user_id = message.from_user.id

    # Случайное время ожидания (от 3 до 10 секунд)
    wait_time = random.randint(3, 10)
    print(wait_time)

    # Разделяем ожидание на маленькие интервалы для проверки отмены
    for _ in range(wait_time):
        if user_id not in user_states or user_states[user_id].get("cancel", False):
            bot.send_message(user_id, "Заброс отменён!")
            return
        time.sleep(1)  # Ждём по 1 секунде

    # Проверяем ещё раз после завершения ожидания
    if user_id not in user_states or user_states[user_id].get("cancel", False):
        bot.send_message(user_id, "Заброс отменён!")
        return

    # Ловим случайную рыбу
    fish = random.choice(FISH_LIST)
    # Обновляем состояние пользователя
    user_states[user_id]["fishing"] = False

    fish_name = fish["name"]
    x = random.randint(1, 10)
    if x < 8: 
        fish_size = random.randint(fish["min_size"], fish["medium_size"])
    else:
        fish_size = random.randint(fish["medium_size"], fish["max_size"])
    
    if int(fish_size) < 1000:
        # Отправляем результат
        bot.send_message(user_id, f"Поздравляем! Вы поймали {fish_name} весом {fish_size} гр!")
    else:
        kgs = fish_size // 10**3
        grms = fish_size % 10**3
        bot.send_message(user_id, f"Поздравляем! Вы поймали {fish_name} весом {kgs} кг {grms} гр!")
    print(f"Fished: {user_id}")

# Команда /cancel - отменить заброс
@bot.message_handler(commands=['cancel'])
def cancel_fishing(message):
    user_id = message.from_user.id

    # Проверяем, ловит ли пользователь рыбу
    if user_id in user_states and user_states[user_id].get("fishing", False):
        user_states[user_id] = {"fishing": False, "cancel": True}
        bot.reply_to(message, "Заброс отменён!")
    else:
        bot.reply_to(message, "Вы сейчас не ловите рыбу.")

    print(f"/сancel by: {user_id}")

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)