from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import time
import re
import random

# Настройки
SEARCH_TEXTS = ["Grand Theft Auto V", "Schedule I", "R.E.P.O"]  # Список искомых фраз
BASE_URL = "https://lzt.market/fortnite"
OUTPUT_FILE = "found_ads.txt"
MAX_PAGES = 20  # Макс. страниц для сканирования
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
PREPARATION_TIME = 15  # Время на подготовку в секундах

# Инициализация драйвера
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={USER_AGENT}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1200,900")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=service, options=options)

# Маскировка WebDriver
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

def accept_cookies():
    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Принять') or contains(., 'Accept')]"))
        )
        cookie_btn.click()
        print("Приняты куки")
        time.sleep(1)
    except Exception:
        print("Куки не найдены, продолжаем...")

def get_ad_links():
    """Получение всех ссылок на объявления на текущей странице"""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.marketIndex--itemsContainer"))
        )
        
        items = driver.find_elements(By.CSS_SELECTOR, "div.marketIndexItem")
        print(f"Найдено {len(items)} объявлений на странице")
        
        ad_links = []
        for item in items:
            try:
                item_id = item.get_attribute("id").replace("marketItem--", "")
                ad_url = f"https://lzt.market/{item_id}/"
                ad_links.append(ad_url)
            except Exception as e:
                print(f"Ошибка при получении ID объявления: {str(e)}")
                continue
        
        return ad_links
    
    except TimeoutException:
        print("Таймаут при ожидании загрузки объявлений")
        return []
    except Exception as e:
        print(f"Ошибка при поиске объявлений: {str(e)}")
        return []

def check_for_text():
    """Проверка наличия искомых текстов на странице"""
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        found_texts = []
        for text in SEARCH_TEXTS:
            if text.lower() in page_text:
                found_texts.append(text)
        return found_texts
    except Exception:
        return []

def extract_ad_details():
    """Извлечение деталей объявления: название, цена, продавец"""
    details = {
        "game": "Не найдено",
        "price": "Не найдено",
        "seller": "Не найдено"
    }
    
    try:
        details["game"] = driver.find_element(By.CSS_SELECTOR, "h1.item-view--title").text.strip()
    except NoSuchElementException:
        print("    Не удалось найти название игры")
    
    try:
        details["price"] = driver.find_element(By.CSS_SELECTOR, "div.item--price-value").text.strip()
    except NoSuchElementException:
        print("    Не удалось найти цену")
    
    try:
        details["seller"] = driver.find_element(By.CSS_SELECTOR, "a.seller-info--name").text.strip()
    except NoSuchElementException:
        print("    Не удалось найти продавца")
    
    return details

def human_like_delay(min=1.0, max=3.0):
    """Задержка, имитирующая поведение человека"""
    delay = random.uniform(min, max)
    time.sleep(delay)

def safe_switch_to_window(target_handle):
    """Безопасное переключение на указанную вкладку"""
    try:
        if target_handle in driver.window_handles:
            driver.switch_to.window(target_handle)
            return True
        return False
    except WebDriverException:
        return False

def main():
    print(f"Начало сканирования сайта: {BASE_URL}")
    print(f"Ищем: {', '.join(SEARCH_TEXTS)}")
    print(f"У вас есть {PREPARATION_TIME} секунд для настройки фильтров на сайте")
    
    try:
        driver.get(BASE_URL)
        human_like_delay(2, 4)
        accept_cookies()
        
        print(f"\nПОДГОТОВКА: Установите фильтры в течение {PREPARATION_TIME} секунд")
        for i in range(PREPARATION_TIME, 0, -1):
            print(f"Осталось времени: {i} сек", end='\r')
            time.sleep(1)
        print("\nНачинаем сканирование...")
        
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {str(e)}")
        return
    
    found_items = []
    main_window_handle = driver.current_window_handle
    
    for page in range(1, MAX_PAGES + 1):
        print(f"\nСтраница {page}/{MAX_PAGES}")
        
        if not safe_switch_to_window(main_window_handle):
            print("Основное окно закрыто, создаем новое")
            driver.get(BASE_URL)
            main_window_handle = driver.current_window_handle
            human_like_delay(2, 4)
        
        if page > 1:
            try:
                current_url = driver.current_url
                if "?page=" in current_url:
                    new_url = re.sub(r'\?page=\d+', f'?page={page}', current_url)
                else:
                    separator = '&' if '?' in current_url else '?'
                    new_url = f"{current_url}{separator}page={page}"
                
                driver.get(new_url)
                human_like_delay(2, 4)
            except Exception as e:
                print(f"Ошибка при загрузке страницы {page}: {str(e)}")
                continue
        
        ad_links = get_ad_links()
        
        if not ad_links:
            print(f"На странице {page} не найдено объявлений")
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "a.pagination-next")
                if "disabled" in next_btn.get_attribute("class"):
                    print("Это последняя страница")
                    break
            except:
                print("Не удалось проверить пагинацию")
            continue
        
        print(f"Проверяем {len(ad_links)} объявлений")
        
        for i, ad_url in enumerate(ad_links):
            print(f"  Объявление {i+1}/{len(ad_links)}")
            
            try:
                current_windows = driver.window_handles
                driver.execute_script(f"window.open('{ad_url}');")
                
                WebDriverWait(driver, 6).until(
                    lambda d: len(d.window_handles) > len(current_windows)
                
                new_window = [w for w in driver.window_handles if w not in current_windows][0]
                driver.switch_to.window(new_window)
                
                try:
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.item-view-content"))
                    )
                except TimeoutException:
                    print("    Таймаут при загрузке страницы объявления")
                
                human_like_delay(1.5, 2.5)
                
                found_texts = check_for_text()
                if found_texts:
                    ad_details = extract_ad_details()
                    print(f"    +++ НАЙДЕНО: {', '.join(found_texts)}")
                    print(f"    Игра: {ad_details['game']}")
                    print(f"    Цена: {ad_details['price']}")
                    print(f"    Продавец: {ad_details['seller']}")
                    
                    # Форматируем данные для записи
                    result_entry = (
                        f"Игра: {ad_details['game']} | "
                        f"Цена: {ad_details['price']} | "
                        f"Продавец: {ad_details['seller']} | "
                        f"Ссылка: {ad_url} | "
                        f"Найдено: {', '.join(found_texts)}\n"
                    )
                    
                    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                        f.write(result_entry)
                    
                    found_items.append(result_entry)
            
            except Exception as e:
                print(f"    Ошибка при проверке: {str(e)}")
            
            finally:
                if len(driver.window_handles) > 1:
                    driver.close()
                
                if safe_switch_to_window(main_window_handle):
                    human_like_delay(0.5, 1.5)
                else:
                    print("Основное окно закрыто, создаем новое")
                    driver.get(BASE_URL)
                    main_window_handle = driver.current_window_handle
                    human_like_delay(2, 4)
    
    print(f"\nСканирование завершено! Найдено {len(found_items)} совпадений")
    print(f"Результаты сохранены в: {OUTPUT_FILE}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass
        print("Браузер закрыт")