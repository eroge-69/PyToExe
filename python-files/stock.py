import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

# Конфигурация
BOT_TOKEN = "8168734235:AAFEdGgxGzmOZFTPl72JDAZIopbRU0SMWIQ"
FRUITYBLOX_URL = "https://fruityblox.com/stock"
CHECK_INTERVAL = 300  # 5 минут
CHANNEL_ID = "@bloxfruits_stock1"  # Лучше использовать числовой ID (например: -1001234567890)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bloxfruits_bot.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные
last_stock = None
subscribed_users = set()
monitor_task = None

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def setup_driver():
    """Настройка и инициализация ChromeDriver"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--ignore-certificate-errors")
    options.page_load_strategy = 'eager'
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logger.error(f"Ошибка инициализации ChromeDriver: {str(e)}")
        return None

def fetch_stock():
    """Получение данных о стоке с сайта"""
    driver = setup_driver()
    if not driver:
        return None
        
    try:
        logger.info("Попытка загрузки страницы...")
        driver.get(FRUITYBLOX_URL)
        
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".border-secondary"))
            )
            logger.info("Страница успешно загружена")
        except TimeoutException:
            logger.error("Таймаут при загрузке элементов стока")
            return None
            
        # Парсинг таймера обновления
        try:
            timer_text = driver.find_element(By.XPATH, 
                "//div[contains(text(), 'Normal Stock')]/following-sibling::div").text
            logger.info(f"Таймер обновления: {timer_text}")
        except Exception as e:
            logger.error(f"Ошибка парсинга таймера: {str(e)}")
            timer_text = "не определено"
        
        # Парсинг стока
        items = driver.find_elements(By.CSS_SELECTOR, ".border-secondary")[:25]
        stock = []
        
        for item in items:
            try:
                name = item.find_element(By.CSS_SELECTOR, "h3").text
                stock_type = item.find_element(By.CSS_SELECTOR, ".text-gray-400").text
                money_price = item.find_element(By.CSS_SELECTOR, ".text-\\[\\#21C55D\\]").text
                robux_price = item.find_element(By.CSS_SELECTOR, ".text-\\[\\#FACC14\\]").text
                
                stock.append(f"🍉 {name} ({stock_type})\n💵 {money_price} | 🪙 {robux_price}\n\n")
            except Exception as e:
                logger.warning(f"Ошибка парсинга элемента: {str(e)}")
                continue
                
        return {
            'stock': stock if stock else ["❌ Нет данных о фруктах"],
            'timer': timer_text
        }
        
    except Exception as e:
        logger.error(f"Критическая ошибка при получении стока: {str(e)}")
        return None
    finally:
        driver.quit()

async def get_stock():
    """Асинхронное получение стока"""
    try:
        return await asyncio.wait_for(asyncio.to_thread(fetch_stock), timeout=60)
    except asyncio.TimeoutError:
        logger.error("Таймаут при получении стока")
        return None
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return None

def normalize_stock(stock_data):
    """Нормализует данные стока для сравнения"""
    if not stock_data or not stock_data.get('stock'):
        return None
    return "".join(stock_data['stock']).strip().lower()

async def send_updates(user_id, data, is_update=False):
    """Отправка обновлений в ЛС и канал"""
    if not data:
        logger.error("Нет данных для отправки!")
        return
    
    try:
        message = ("🔔 ОБНОВЛЕНИЕ СТОКА!\n\n" if is_update else "📊 Текущий сток:\n\n") + \
                  "".join(data['stock']) + f"\n⏳ Следующее обновление: {data['timer']}"
        
        # Отправка в ЛС
        logger.info(f"Пытаюсь отправить сообщение пользователю {user_id}")
        await bot.send_message(user_id, message)
        
        # Отправка в канал (только при обновлении)
        if is_update:
            logger.info(f"Пытаюсь отправить сообщение в канал {CHANNEL_ID}")
            await bot.send_message(CHANNEL_ID, message)
    except Exception as e:
        logger.error(f"Ошибка отправки: {str(e)}")

async def monitor_stock():
    """Мониторинг изменений стока"""
    global last_stock
    
    logger.info("Запуск мониторинга стока...")
    
    while True:
        try:
            data = await get_stock()
            
            if data:
                current_stock = normalize_stock(data)
                
                if last_stock is None:
                    last_stock = current_stock
                    # Первая отправка всем подписчикам
                    for user_id in subscribed_users.copy():
                        try:
                            await send_updates(user_id, data)
                        except Exception as e:
                            logger.error(f"Ошибка отправки пользователю {user_id}: {str(e)}")
                            subscribed_users.discard(user_id)
                
                elif current_stock != last_stock:
                    last_stock = current_stock
                    logger.info("Обнаружено обновление стока! Рассылаем уведомления...")
                    
                    # Отправка в канал
                    try:
                        await bot.send_message(
                            CHANNEL_ID,
                            "🔔 ОБНОВЛЕНИЕ СТОКА!\n\n" + "".join(data['stock']) + \
                            f"\n⏳ Следующее обновление: {data['timer']}"
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки в канал: {str(e)}")
                    
                    # Отправка подписчикам
                    for user_id in subscribed_users.copy():
                        try:
                            await send_updates(user_id, data, is_update=True)
                        except Exception as e:
                            logger.error(f"Ошибка отправки пользователю {user_id}: {str(e)}")
                            subscribed_users.discard(user_id)
            
            await asyncio.sleep(CHECK_INTERVAL)
            
        except asyncio.CancelledError:
            logger.info("Мониторинг остановлен")
            break
        except Exception as e:
            logger.error(f"Ошибка в мониторинге: {str(e)}")
            await asyncio.sleep(60)

async def start_monitoring():
    """Запуск мониторинга"""
    global monitor_task
    if monitor_task is None or monitor_task.done():
        monitor_task = asyncio.create_task(monitor_stock())
        logger.info("✅ Мониторинг стока запущен!")

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Обработка команды /start"""
    try:
        user_id = message.from_user.id
        subscribed_users.add(user_id)
        
        await message.answer(
            "🤖 Бот мониторинга стока Blox Fruits\n\n"
            "Я буду присылать уведомления об обновлениях стока здесь.\n"
            "Используйте /stock для ручной проверки.\n"
            "Используйте /stop для отключения уведомлений."
        )
        
        await start_monitoring()
        
    except Exception as e:
        logger.error(f"Ошибка в /start: {str(e)}")

@dp.message(Command("stop"))
async def stop_command(message: types.Message):
    """Обработка команды /stop"""
    try:
        user_id = message.from_user.id
        if user_id in subscribed_users:
            subscribed_users.remove(user_id)
            await message.answer("🔕 Вы отписались от уведомлений.")
        else:
            await message.answer("ℹ️ Вы и так не подписаны на уведомления.")
    except Exception as e:
        logger.error(f"Ошибка в /stop: {str(e)}")

@dp.message(Command("stock"))
async def stock_command(message: types.Message):
    """Ручная проверка стока"""
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        msg = await message.answer("🔄 Получаю данные о стоке...")
        
        data = await get_stock()
        
        if data:
            await bot.edit_message_text(
                "📊 Текущий сток:\n\n" + "".join(data['stock']) + \
                f"\n⏳ Следующее обновление: {data['timer']}",
                chat_id=message.chat.id,
                message_id=msg.message_id
            )
        else:
            await bot.edit_message_text(
                "❌ Не удалось получить данные о стоке. Попробуйте позже.",
                chat_id=message.chat.id,
                message_id=msg.message_id
            )
    except Exception as e:
        logger.error(f"Ошибка в /stock: {str(e)}")

async def on_startup():
    """Действия при запуске бота"""
    logger.info("Бот запускается...")
    
    # Проверка прав бота в канале
    try:
        chat = await bot.get_chat(CHANNEL_ID)
        logger.info(f"Бот имеет доступ к каналу: {chat.title}")
    except Exception as e:
        logger.error(f"Ошибка доступа к каналу: {str(e)}")
        raise  # Останавливаем бота, если нет доступа
    
    await start_monitoring()

async def main():
    """Основная функция"""
    try:
        dp.startup.register(on_startup)
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка: {str(e)}")
    finally:
        logger.info("Бот завершил работу")
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную")
    except Exception as e:
        logger.critical(f"Ошибка запуска: {str(e)}")