import requests
import json
import asyncio
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, date, timedelta
from icalendar import Calendar
import logging
import re

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = "8429629815:AAFIY8J0tzeQZsMFkL1-emxDARk9TMoSejk"
ICS_URL = "https://schedule.sevsu.ru/calendar/group/F5C5E2EC5F63B649"
OPENWEATHER_KEY = "a2aef88ad3a307f5b7debce4019ea732"
CITY = "Sevastopol"

# Определяем путь к файлу настроек в той же папке, где находится скрипт
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

try:
    with open(SETTINGS_PATH, "r") as f:
        user_settings = json.load(f)
except FileNotFoundError:
    user_settings = {}

def save_settings():
    with open(SETTINGS_PATH, "w") as f:
        json.dump(user_settings, f)

# ====== Погода ======
def get_weather(city=CITY):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=ru"
        resp = requests.get(url).json()
        temp = round(resp["main"]["temp"])
        desc = resp["weather"][0]["description"]
        return f"{temp}°C, {desc}"
    except Exception:
        return "Не удалось загрузить погоду 🌦"

# ====== Расписание ======
def get_schedule_for_day(target_date: date):
    try:
        resp = requests.get(ICS_URL)
        resp.raise_for_status()
        cal = Calendar.from_ical(resp.content)

        events = []
        for ev in cal.walk():
            if ev.name == "VEVENT":
                dt = ev.get("DTSTART").dt
                summary = str(ev.get("SUMMARY", "Без названия"))
                location = str(ev.get("LOCATION", "Аудитория не указана"))
                description = str(ev.get("DESCRIPTION", "Преподаватель не указан"))

                if isinstance(dt, datetime):
                    event_date = dt.date()
                    event_time = dt.strftime("%H:%M")
                else:
                    event_date = dt
                    event_time = ""

                if event_date == target_date:
                    # Форматируем информацию о паре
                    event_info = f"🕒 {event_time} — {summary}"
                    if location and location != "Аудитория не указана":
                        event_info += f"\n📍 Аудитория: {location}"
                    if description and description != "Преподаватель не указан":
                        # Очищаем описание от HTML тегов и лишних пробелов
                        description_clean = re.sub('<[^<]+?>', '', description).strip()
                        # Извлекаем ФИО преподавателя (обычно в начале описания)
                        teacher_match = re.search(r'([А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+(?:\s[А-ЯЁ][а-яё]+)?)', description_clean)
                        if teacher_match:
                            teacher_name = teacher_match.group(1)
                            event_info += f"\n👨‍🏫 Преподаватель: {teacher_name}"
                    
                    events.append(event_info)

        return events if events else ["🎉 Занятий нет"]
    except Exception as e:
        logging.error(f"Ошибка при получении расписания: {e}")
        return ["❌ Не удалось загрузить расписание"]

def get_schedule_today():
    return get_schedule_for_day(date.today())

def get_schedule_tomorrow():
    return get_schedule_for_day(date.today() + timedelta(days=1))

def get_schedule_week():
    today = date.today()
    result = []
    
    # Словарь для перевода дней недели
    days_translation = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник', 
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
    }
    
    for i in range(7):
        day = today + timedelta(days=i)
        events = get_schedule_for_day(day)
        day_name_en = day.strftime('%A')
        day_name_ru = days_translation.get(day_name_en, day_name_en)
        
        day_schedule = f"**{day_name_ru} {day.strftime('%d.%m')}:**\n"
        if events and events[0] != "🎉 Занятий нет":
            day_schedule += "\n".join(events)
        else:
            day_schedule += "🎉 Занятий нет"
        
        result.append(day_schedule)
    return result

# ====== Команды ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    if chat_id not in user_settings:
        user_settings[chat_id] = {"time": "06:00"}  # стандартное время
        save_settings()

    keyboard = [
        ["Сегодня 📅", "Завтра 📆"],
        ["Неделя 📖", "Погода 🌤"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = (
        "Привет! Я бот с расписанием 📚\n"
        f"⏰ Время утреннего уведомления: {user_settings[chat_id]['time']}\n"
        "Ты можешь изменить его командой: /time 07:30\n\n"
        "Доступные команды:\n"
        "/today - расписание на сегодня\n"
        "/tomorrow - расписание на завтра\n" 
        "/week - расписание на неделю\n"
        "/weather - погода в Севастополе\n"
        "/time HH:MM - изменить время уведомлений"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = get_schedule_today()
    await update.message.reply_text("📅 Расписание на сегодня:\n\n" + "\n\n".join(events))

async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = get_schedule_tomorrow()
    await update.message.reply_text("📆 Расписание на завтра:\n\n" + "\n\n".join(events))

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events = get_schedule_week()
    # Разбиваем на несколько сообщений если слишком длинное
    week_text = "📖 Расписание на неделю:\n\n" + "\n\n".join(events)
    if len(week_text) > 4096:
        # Если сообщение слишком длинное, разбиваем на части
        for i in range(0, len(week_text), 4096):
            await update.message.reply_text(week_text[i:i+4096])
    else:
        await update.message.reply_text(week_text)

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    forecast = get_weather()
    await update.message.reply_text(f"🌤 Погода в {CITY}:\n{forecast}")

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    if len(context.args) == 1:
        new_time = context.args[0]
        try:
            datetime.strptime(new_time, "%H:%M")  # проверка формата
            if chat_id not in user_settings:
                user_settings[chat_id] = {}
            user_settings[chat_id]["time"] = new_time
            save_settings()
            await update.message.reply_text(f"✅ Время уведомления изменено на {new_time}")
        except ValueError:
            await update.message.reply_text("⚠️ Неверный формат. Используй /time HH:MM (например, /time 07:30)")
    else:
        await update.message.reply_text("⚠️ Укажи время: /time HH:MM")

# Обработчики для текстовых кнопок
async def button_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await today(update, context)

async def button_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await tomorrow(update, context)

async def button_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await week(update, context)

async def button_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await weather(update, context)

# ====== Умные уведомления ======
async def morning_notification_task():
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            for chat_id, settings in user_settings.items():
                if settings.get("time") == now:
                    events = get_schedule_today()
                    weather_info = get_weather()
                    text = f"🌅 Доброе утро!\nПогода: {weather_info}\n\n📅 Расписание на сегодня:\n\n" + "\n\n".join(events)
                    await app.bot.send_message(chat_id=chat_id, text=text)
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Ошибка в morning_notification_task: {e}")
            await asyncio.sleep(60)

# Глобальная переменная для приложения
app = None

# ====== Запуск ======
def main():
    global app
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Команды с слешем
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today))
    app.add_handler(CommandHandler("tomorrow", tomorrow))
    app.add_handler(CommandHandler("week", week))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("time", set_time))
    
    # Обработчики текстовых кнопок
    app.add_handler(MessageHandler(filters.Regex("^Сегодня 📅$"), button_today))
    app.add_handler(MessageHandler(filters.Regex("^Завтра 📆$"), button_tomorrow))
    app.add_handler(MessageHandler(filters.Regex("^Неделя 📖$"), button_week))
    app.add_handler(MessageHandler(filters.Regex("^Погода 🌤$"), button_weather))

    # Запускаем задачу уведомлений в фоне
    loop = asyncio.get_event_loop()
    loop.create_task(morning_notification_task())

    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    # Для Windows может потребоваться эта строка:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    main()