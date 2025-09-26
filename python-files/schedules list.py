import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен вашего бота
BOT_TOKEN = "7281550229:AAFAC6yaf-efQYjodElsLsHO9tZXYlSsnpU"

# Состояния для ConversationHandler
SELECT_PERSON, SELECT_DAY = range(2)

# Расписание для трех человек на разные дни недели
SCHEDULES = {
    "Егор": {
        "Понедельник": [
            "08:30-9:10 - Псевдо РОВ",
            "09:20-10:00 - Информатика",
            "10:10-11:50 - Информатика",
            "11:00-11:40 - Математика",
            "12:00-12:40 - Компьютерное моделирование",
            "13:00-13:40 - История",
            "14:00-14:40 -  ️❗️️️️️ФИЗ-РА❗️"
        ],
        "Вторник": [
            "08:30-9:10 - Информатика",
            "09:20-10:00 - Физика",
            "10:10-11:50 - География",
            "11:00-11:40 - Обществознание",
            "12:00-12:40 - История",
            "13:00-13:40 - Компьютерное моделирование",
            "14:00-14:40 - Математика"
        ],
        "Среда": [
            "08:30-9:10 - Математика",
            "09:20-10:00 - Биология",
            "10:10-11:50 - Русский",
            "11:00-11:40 - ОБЖ",
            "12:00-12:40 - Лит-ра",
            "13:00-13:40 - Англ",
            "14:00-14:40 - Физика"
        ],
        "Четверг": [
            "08:30-9:10 - ❕Пусто❕",
            "09:20-10:00 - Химия",
            "10:10-11:50 - Лит-ра",
            "11:00-11:40 - ️❗️️️️️ФИЗ-РА❗️",
            "12:00-12:40 - Русский",
            "13:00-13:40 - Вероятность",
            "14:00-14:40 - Англ"
        ],
        "Пятница": [
            "08:30-9:10 - Информатика",
            "09:20-10:00 - Информатика",
            "10:10-11:50 - Математика",
            "11:00-11:40 - ️Обществознание",
            "12:00-12:40 - Обществознание",
            "13:00-13:40 - Лит-ра",
            "14:00-14:40 - Англ",
            "17:00-18:00 - Репетитор по русскому"
        ],
        "Суббота": [
            "нет дел в расписании"
        ],
        "Воскресенье": [
            "нет дел в расписании"
        ]
    },
    "Таня": {
        "Понедельник": [
            "08:00-08:40 - РОВ",
            "08:50-09:30 - Матеметика",
            "09:50-10:30 - Русский язык",
            "10:45-11:25 - ИЗО",
            "11:40-12:20 - Чтение",
            "12:30-13:10 - ОРКСЭ",
            "14:00-15:20 - Шанс Классический(Шубина ВГ:купальник, велосипедки, белые носки"
        ],
        "Вторник": [
            "08:00-08:40 - Математика",
            "08:50-09:30 - Русский",
            "09:50-10:30 - ❗️ФИЗ-РА❗️",
            "10:45-11:25 - Окр.мир",
            "11:40-12:20 - Труд",
            "14:00-15:20 - Шанс Современный"
        ],
        "Среда": [
            "08:00-08:40 - Русский",
            "08:50-09:30 - Англ.яз",
            "09:50-10:30 - Математика",
            "10:45-11:25 - Чтение",
            "11:40-12:20 - Функц.гр",
            "13:30-14:10 - Арт-проект",
            "??:?? - Вокал 17 каб."
        ],
        "Четверг": [
            "08:00-08:40 - Русский",
            "08:50-09:30 - ️❗️ФИЗ-РА❗️",
            "09:50-10:30 - Математика",
            "10:45-11:25 - Музыка",
            "11:40-12:20 - Окр.мир"
        ],
        "Пятница": [
            "08:00-08:40 - Англ.яз",
            "08:50-09:30 - Математика",
            "09:50-10:30 - Русский",
            "10:45-11:25 - Чтение",
            "11:40-12:20 - Орляята",
            "13:30-14:10 - Арт-проект",
            "16:00-18:00 - Джаз-модерн"
        ],
        "Суббота": [
            "11:00-13:00 - Шанс репетиция",
            "15:40-16:20 - Арт-проект, хореография",
            "16:20-17:00 - Арт-проект,акт.маст."
        ],
        "Воскресенье": [
            "нет дел в расписании"
        ]
    },
    "Саша": {
        "Понедельник": [
            "13:15-13:55 - РОВ",
            "14:00-14:40 - Математика",
            "14:55-15:35 - Русский",
            "15:50-16:30 - ❗️ФИЗ-РА❗️",
            "16:40-17:20 - Чтение",
            "17:30-18:10 - Орлята"
        ],
        "Вторник": [
            "09:00-10:30 - Родничок",
            "10:30-12:00 - Вязание",
            "13:15-13:55 - ❕Пусто❕",
            "14:00-14:40 - Русский",
            "14:55-15:35 - Математика",
            "15:50-16:30 - Ин-яз",
            "16:40-17:20 - Окр.мир",
            "17:30-18:10 - Чтение"

        ],
        "Среда": [
            "09:00-10:30 - Апельсин",
            "13:15-13:55 - Чтение",
            "14:00-14:40 - Математика",
            "14:55-15:35 - Русский",
            "15:50-16:30 - ИЗО",
            "16:40-17:20 - Функц.гр"
        ],
        "Четверг": [
            "08:00-09:30 - Рисование",
            "10:30-12:00 - Вязание",
            "13:15-13:55 - Математика",
            "14:00-14:40 - Русский",
            "14:55-15:35 - Окр.мир",
            "15:50-16:30 - Ин-яз",
            "16:40-17:20 - Музыка"
        ],
        "Пятница": [
            "09:00-10:30 - Апельсин",
            "13:15-13:55 - Русский",
            "14:00-14:40 - ❗️ФИЗ-РА❗️",
            "14:55-15:35 - Математика",
            "15:50-16:30 - Чтение",
            "16:40-17:20 - Труд"
        ],
        "Суббота": [
            "11:00-12:30 - Родничок"
        ],
        "Воскресенье": [
            "нет дел в расписании"
        ]
    }
}


# Клавиатура для выбора человека
def get_person_keyboard():
    keyboard = [["Егор", "Таня", "Саша"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# Клавиатура для выбора дня недели
def get_day_keyboard():
    keyboard = [
        ["Понедельник", "Вторник", "Среда"],
        ["Четверг", "Пятница", "Суббота"],
        ["Воскресенье", "Сегодня"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Привет! Я бот для просмотра расписания на разные дни недели.\n"
        "Выбери человека, чье расписание хочешь увидеть:",
        reply_markup=get_person_keyboard()
    )
    return SELECT_PERSON


# Обработка выбора человека
async def select_person(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text

    if user_choice in SCHEDULES:
        context.user_data['selected_person'] = user_choice
        await update.message.reply_text(
            f"Отлично! Теперь выбери день недели для {user_choice}:",
            reply_markup=get_day_keyboard()
        )
        return SELECT_DAY
    else:
        await update.message.reply_text(
            "Пожалуйста, выбери человека из предложенного списка:",
            reply_markup=get_person_keyboard()
        )
        return SELECT_PERSON


# Обработка выбора дня недели
async def select_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day_choice = update.message.text
    person = context.user_data.get('selected_person')

    # Определяем текущий день, если выбран "Сегодня"
    if day_choice == "Сегодня":
        today = datetime.now().weekday()
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        day_choice = days[today]

    if person and day_choice in SCHEDULES[person]:
        schedule = SCHEDULES[person][day_choice]
        schedule_text = f"📅 Расписание для {person} на {day_choice}:\n\n"

        for i, item in enumerate(schedule, 1):
            schedule_text += f"⏰ {item}\n"

        await update.message.reply_text(schedule_text)
        await update.message.reply_text(
            "Хочешь посмотреть еще расписание? Выбери человека:",
            reply_markup=get_person_keyboard()
        )
        return SELECT_PERSON
    else:
        await update.message.reply_text(
            "Пожалуйста, выбери день из предложенного списка:",
            reply_markup=get_day_keyboard()
        )
        return SELECT_DAY


# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать справку\n"
        "/cancel - отменить текущее действие\n\n"
        "Как пользоваться:\n"
        "1. Выбери человека из списка\n"
        "2. Выбери день недели\n"
        "3. Получи подробное расписание!\n"
        "Можно смотреть расписание на разные дни для разных людей!"
    )


# Команда /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Действие отменено. Используйте /start для начала работы.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_PERSON: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_person)],
            SELECT_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_day)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()