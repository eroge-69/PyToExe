import time
import telebot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ====== НАСТРОЙКИ ======
TELEGRAM_TOKEN = "8364561466:AAGZlPjiHNPxOzBfJJzHulx7qdhpYWXBVHs"
CHAT_ID = "1064743796"
TARGET_ITEM = "Prismatic: Explosive Burst"
STEAM_URL = "https://skins.cash"
CHECK_INTERVAL = 30  # Интервал проверки в секундах
LOGIN_WAIT = 60  # Время на авторизацию
# =======================

bot = telebot.TeleBot(TELEGRAM_TOKEN)
driver = None

def send_notification(message):
    print(message)
    bot.send_message(CHAT_ID, message)

def init_browser():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    service = Service()
    return webdriver.Chrome(service=service, options=options)

def check_price():
    try:
        items = driver.find_elements(By.XPATH, f"//*[contains(text(), '{TARGET_ITEM}')]")
        if not items:
            return {"status": "not_found", "price": None}
        
        # Ищем цену только у первого найденного предмета
        try:
            parent = items[0].find_element(By.XPATH, "./ancestor::div[1]")
            price_element = parent.find_element(By.XPATH, ".//*[contains(@class, 'price') or contains(text(), '$')]")
            return {"status": "price_found", "price": price_element.text.strip()}
        except:
            return {"status": "no_price", "price": None}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    global driver
    driver = init_browser()
    
    try:
        # Первоначальная настройка
        driver.get(STEAM_URL)
        send_notification("🔍 Начинаю мониторинг предмета...")
        send_notification(f"⚠ У тебя есть {LOGIN_WAIT} секунд чтобы залогиниться")
        time.sleep(LOGIN_WAIT)

        # Проверка загрузки инвентаря
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'item') or contains(@class, 'skin')]"))
        )
        send_notification("✅ Инвентарь загружен. Ищу предмет...")

        # Основной цикл проверки
        item_found = False
        price_found = False
        
        while True:
            result = check_price()
            
            if result["status"] == "not_found" and not item_found:
                send_notification(f"❌ Предмет '{TARGET_ITEM}' не найден")
                item_found = True
            elif result["status"] == "no_price" and not item_found:
                send_notification(f"ℹ️ Предмет '{TARGET_ITEM}' найден, но цена отсутствует")
                item_found = True
            elif result["status"] == "price_found" and not price_found:
                send_notification(f"💰 Цена появилась! {TARGET_ITEM} - {result['price']}")
                price_found = True
                break  # Останавливаем после нахождения цены
            elif result["status"] == "error":
                send_notification(f"⚠ Ошибка: {result['error']}")
            
            time.sleep(CHECK_INTERVAL)
            
    except Exception as e:
        send_notification(f"🚨 Критическая ошибка: {str(e)}")
    finally:
        if driver:
            driver.quit()
        send_notification("🛑 Мониторинг завершен")

if __name__ == "__main__":
    main()