from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import winsound
import requests
import json
import os

# Список игр для мониторинга
GAMES = [
    "https://www.roblox.com/games/86611914946922/Grows-up-Plants",
    "https://www.roblox.com/games/125680876148344/Growing-the-Plants", 
    "https://www.roblox.com/games/104982244504345/Grow-an-Modded-garden",
    "https://www.roblox.com/games/102453099848530/Grow-An-Garden-but-MODDED",
    "https://www.roblox.com/games/126884695634066/Grow-a-Garden",
    "https://www.roblox.com/games/113789809644283/Grow-a-Garden-MODDED"
]

TARGET_TEXT = "[ Content Deleted ]"
CHECK_INTERVAL = 10  # секунд
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1390355007290736721/HckRoPmeyD2mHcNAiI6mqvS4H-vQsKYdIwGTQHlsI6bWy-Hzgs3HqzKPaUZSYv5cwdWG"
USER_ID = "pcelovbogdan_andikeu"

# Настройка Chrome для максимальной скорости
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-background-timer-throttling")
chrome_options.add_argument("--disable-backgrounding-occluded-windows")
chrome_options.add_argument("--disable-renderer-backgrounding")
chrome_options.add_argument("--disable-features=TranslateUI")
chrome_options.add_argument("--disable-ipc-flooding-protection")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--disable-javascript")
chrome_options.add_argument("--disable-webgl")
chrome_options.add_argument("--disable-webgl2")
chrome_options.add_argument("--disable-3d-apis")
chrome_options.add_argument("--disable-accelerated-2d-canvas")
chrome_options.add_argument("--disable-accelerated-video-decode")
chrome_options.add_argument("--no-first-run")
chrome_options.add_argument("--no-default-browser-check")
chrome_options.add_argument("--disable-default-apps")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--metrics-recording-only")
chrome_options.add_argument("--disable-crash-reporter")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

# Отключаем логирование Chrome
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--silent")

# Настройка Service для отключения логов
service = Service(log_path=os.devnull)

def send_discord_message(game_url, game_name):
    """Отправляет сообщение в Discord 5 раз"""
    current_time = time.strftime('%Y-%m-%d %H:%M:%S UTC')
    message = {
        "content": f"@everyone 🚨 **ИГРА УДАЛЕНА!** 🚨\n\n**Игра:** {game_name}\n**URL:** {game_url}\n**Время:** {current_time}"
    }
    
    for i in range(5):
        try:
            response = requests.post(DISCORD_WEBHOOK, json=message, timeout=5)
            if response.status_code == 204:
                print(f"✅ Discord #{i+1}")
            time.sleep(0.5)  # Сокращенная пауза
        except:
            pass

def get_game_name(url):
    """Извлекает название игры из URL"""
    try:
        return url.split('/')[-1].replace('-', ' ')
    except:
        return "Unknown"

def check_single_game_fast(url):
    """Быстрая проверка одной игры"""
    driver = webdriver.Chrome(service=service, options=chrome_options)
    game_name = get_game_name(url)
    
    try:
        driver.set_page_load_timeout(10)  # Максимум 10 сек на загрузку
        driver.implicitly_wait(1)  # Минимальное ожидание
        
        driver.get(url)
        time.sleep(2)  # Минимальная пауза
        
        # Быстрая проверка через requests (альтернативный способ)
        try:
            response = requests.get(url, timeout=3)
            if TARGET_TEXT in response.text:
                print(f"🚨 УДАЛЕНА: {game_name}")
                
                # Звук
                for _ in range(2):
                    winsound.Beep(1500, 300)
                
                send_discord_message(url, game_name)
                driver.quit()
                return True
        except:
            pass
        
        # Проверка через Selenium как backup
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if TARGET_TEXT in page_text:
                print(f"🚨 УДАЛЕНА: {game_name}")
                
                for _ in range(2):
                    winsound.Beep(1500, 300)
                
                send_discord_message(url, game_name)
                driver.quit()
                return True
        except:
            pass
        
        driver.quit()
        return False
            
    except Exception:
        try:
            driver.quit()
        except:
            pass
        return False

def check_all_games_fast():
    """Быстрая проверка всех игр"""
    deleted_games = []
    
    for i, game_url in enumerate(GAMES, 1):
        game_name = get_game_name(game_url)
        print(f"[{i}/{len(GAMES)}] {game_name}... ", end="")
        
        if check_single_game_fast(game_url):
            deleted_games.append((game_url, game_name))
        else:
            print("✅")
    
    return deleted_games

def main():
    print("🎮 FAST ROBLOX MONITOR")
    print("=" * 50)
    print(f"👤 {USER_ID}")
    print(f"🎯 {len(GAMES)} игр")
    print(f"⏱️ Каждые {CHECK_INTERVAL}s")
    print(f"🕐 Старт: {time.strftime('%H:%M:%S')}")
    print("=" * 50)
    
    check_count = 0
    total_deleted = 0
    
    while True:
        check_count += 1
        print(f"\n🔄 Проверка #{check_count} [{time.strftime('%H:%M:%S')}]")
        
        start_time = time.time()
        deleted_games = check_all_games_fast()
        end_time = time.time()
        
        if deleted_games:
            total_deleted += len(deleted_games)
            print(f"🚨 Удалено: {len(deleted_games)} | Всего: {total_deleted}")
        else:
            print("✅ Все доступны")
        
        check_time = round(end_time - start_time, 1)
        print(f"⚡ Время проверки: {check_time}s")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Отключаем вывод ошибок Python
    import warnings
    warnings.filterwarnings("ignore")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Остановлено")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")