import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота - ЗАМЕНИТЕ НА ВАШ!
BOT_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 Привет! Я бот с погодой и новостями.\n\n"
        "Доступные команды:\n"
        "/weather [город] - Узнать погоду\n"
        "/news - Последние новости\n\n"
        "Пример:\n/weather Москва\n/weather London"
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        city = " ".join(context.args) if context.args else "Москва"
        logger.info(f"Запрос погоды: {city}")
        
        # Форматированный запрос погоды
        url = f"https://wttr.in/{city}?format=%l:\n+%c+%t\n🌬️Ветер:%w\n💧Влажность:%h\n🌡Ощущается:%f\n"
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        )
        
        if response.status_code == 200:
            weather_text = response.text.replace("°F", "°C").replace("mph", "м/с")
            await update.message.reply_text(f"🌤️ Погода:\n{weather_text}")
        else:
            await update.message.reply_text("❌ Не удалось получить погоду. Попробуйте другой город.")
    
    except Exception as e:
        await update.message.reply_text("⚠️ Ошибка при получении погоды.")
        logger.error(f"Ошибка weather: {e}")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info("Запрос новостей")
        
        # Используем Tass.ru как стабильный источник новостей
        url = "https://tass.ru/rss/v2.xml"
        response = requests.get(url)
        response.raise_for_status()
        
        # Парсим XML с помощью BeautifulSoup
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:5]  # Берем 5 последних новостей
        
        news_text = "📰 Последние новости (TASS):\n\n"
        for i, item in enumerate(items, 1):
            title = item.title.text.strip()
            link = item.link.text.strip()
            news_text += f"{i}. {title}\n{link}\n\n"
        
        await update.message.reply_text(news_text.strip())
        logger.info("Новости успешно отправлены")
    
    except Exception as e:
        await update.message.reply_text("⚠️ Не удалось загрузить новости. Попробуйте позже.")
        logger.error(f"Ошибка news: {e}")
        logger.error(f"Ответ сервера: {response.text[:200] if 'response' in locals() else 'Нет ответа'}")

def main():
    try:
        logger.info("Запуск бота...")
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("weather", weather))
        application.add_handler(CommandHandler("news", news))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        application.run_polling()
        logger.info("Бот запущен")
    
    except Exception as e:
        logger.critical(f"Ошибка запуска: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)
    if update:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Произошла ошибка. Попробуйте другую команду."
        )

if __name__ == "__main__":
    main()