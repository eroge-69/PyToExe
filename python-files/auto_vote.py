import time
import random
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_vote.log"),
        logging.StreamHandler()
    ]
)

class TeamVoter:
    def __init__(self, headless=False):
        """
        Инициализация класса для автоматического голосования за команду
        
        Args:
            headless (bool): Запускать ли браузер в фоновом режиме
        """
        self.headless = headless
        
    def _setup_browser(self):
        """Настройка и запуск браузера"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")  # Новый headless режим
        
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Добавляем аргументы для уменьшения вероятности обнаружения автоматизации
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Предварительно разрешаем геолокацию
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1,  # 1 = разрешить, 2 = блокировать
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        
        # Случайный User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        ]
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Инициализируем драйвер
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # Устанавливаем скрипт для маскировки Selenium
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        return driver
    
    def _human_scroll_to_bottom(self, driver):
        """Имитация человеческого скроллинга до конца страницы"""
        # Получаем высоту страницы
        total_height = driver.execute_script("return document.body.scrollHeight")
        
        # Скроллим постепенно с разной скоростью
        current_position = 0
        while current_position < total_height:
            scroll_step = random.randint(200, 500)
            current_position += scroll_step
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.2, 0.5))
    
    def _random_mouse_movement(self, driver, element=None):
        """Имитация случайных движений мыши"""
        action = ActionChains(driver)
        
        if element:
            try:
                action.move_to_element(element)
                action.perform()
                time.sleep(random.uniform(0.2, 0.5))
            except:
                pass
        
        for _ in range(random.randint(2, 5)):
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            try:
                action.move_by_offset(x_offset, y_offset)
                action.perform()
                time.sleep(random.uniform(0.1, 0.3))
            except:
                pass
    
    def _clear_browser_data(self, driver):
        """Очистка кеша и куки браузера"""
        try:
            # Очистка куки
            driver.delete_all_cookies()
            
            # Очистка кеша через Chrome DevTools Protocol
            if hasattr(driver, "execute_cdp_cmd"):
                driver.execute_cdp_cmd('Network.clearBrowserCache', {})
                driver.execute_cdp_cmd('Storage.clearDataForOrigin', {
                    'origin': '*',
                    'storageTypes': 'all',
                })
            
            logging.info("Кеш и куки успешно очищены")
        except Exception as e:
            logging.warning(f"Ошибка при очистке данных браузера: {e}")











    def vote_for_team(self, url, team_id=15, team_name="Центр ВОИН", num_votes=10, delay_between_votes=(5, 15)):
        """
        Автоматическое голосование за команду
        
        Args:
            url (str): URL сайта с голосованием
            team_id (int): ID команды (из атрибута onclick="confirmation(ID)")
            team_name (str): Название команды для голосования (для поиска на странице)
            num_votes (int): Количество голосований
            delay_between_votes (tuple): Диапазон задержки между голосованиями в секундах
        """
        successful_votes = 0
        
        for vote_num in range(1, num_votes + 1):
            logging.info(f"Попытка голосования #{vote_num} из {num_votes}")
            
            driver = None
            try:
                # Настраиваем и запускаем браузер
                driver = self._setup_browser()
                driver.maximize_window()
                
                # Переходим на сайт голосования
                logging.info(f"Открываем URL: {url}")
                driver.get(url)
                
                # Ждем загрузки страницы и добавляем случайную задержку
                time.sleep(random.uniform(2, 5))
                
                # Скроллим страницу до конца, чтобы найти команду
                logging.info("Скроллим страницу до конца")
                self._human_scroll_to_bottom(driver)
                
                # Ищем блок с нужной командой по названию
                logging.info(f"Ищем команду: {team_name}")
                
                # Пробуем найти команду по разным селекторам
                team_selectors = [
                    f"//div[contains(@class, 'pvn') and contains(., '{team_name}')]",
                    f"//div[contains(@class, 'pvn-title') and contains(text(), '{team_name}')]/..",
                    f"//div[contains(@class, 'pvn-title') and text()='{team_name}']/.."
                ]
                
                team_element = None
                for selector in team_selectors:
                    try:
                        team_element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        logging.info(f"Команда найдена по селектору: {selector}")
                        break
                    except:
                        continue
                
                if not team_element:
                    logging.error(f"Не удалось найти команду: {team_name}")
                    raise NoSuchElementException(f"Команда {team_name} не найдена на странице")
                
                # Имитируем движение мыши к элементу команды
                self._random_mouse_movement(driver, team_element)
                
                # Вместо клика по элементу, напрямую вызываем JavaScript функцию confirmation
                logging.info(f"Вызываем JavaScript функцию confirmation({team_id})")
                driver.execute_script(f"confirmation({team_id})")
                
                # Ждем появления окна голосования
                time.sleep(random.uniform(1, 2))
                
                # Проверяем, что окно голосования открылось
                try:
                    vote_window = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.vote"))
                    )
                    logging.info("Окно голосования успешно открылось")
                except TimeoutException:
                    logging.warning("Окно голосования не появилось. Пробуем альтернативный метод.")
                    # Если окно не появилось, пробуем кликнуть по элементу
                    team_element.click()
                    time.sleep(random.uniform(1, 2))
                    
                    # Повторно проверяем наличие окна голосования
                    vote_window = WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.vote"))
                    )
                
                # ВАЖНО: Сначала проверяем наличие предупреждения и закрываем его
                try:
                    warning = WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.warning"))
                    )
                    # Если предупреждение появилось, закрываем его
                    logging.info("Обнаружено предупреждение, закрываем его")
                    warning.click()
                    # Ждем, пока предупреждение исчезнет
                    WebDriverWait(driver, 5).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.warning"))
                    )
                    logging.info("Предупреждение закрыто")
                    # Небольшая пауза после закрытия предупреждения
                    time.sleep(random.uniform(0.5, 1.0))
                except:
                    logging.info("Предупреждение не обнаружено, продолжаем")
                    
                # Теперь находим кнопку голосования
                vote_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div.vote-btn"))
                )
                
                # Имитируем движение мыши к кнопке голосования
                self._random_mouse_movement(driver, vote_button)
                
                # Кликаем по кнопке голосования
                logging.info("Кликаем по кнопке голосования")
                vote_button.click()
                
                # Ждем появления запроса на геолокацию
                time.sleep(random.uniform(1, 2))
                
                # Обрабатываем возможное уведомление в Chrome
                try:
                    # Проверяем наличие диалогового окна
                    alert = driver.switch_to.alert
                    alert.accept()
                    logging.info("Приняли диалоговое окно")
                except:
                    # Если диалогового окна нет, пробуем нажать Enter
                    try:
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        logging.info("Нажали Enter для подтверждения")
                    except Exception as e:
                        logging.warning(f"Не удалось обработать уведомление: {e}")
                
                # Проверяем, не появилось ли снова предупреждение после голосования
                try:
                    warning = WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.warning"))
                    )
                    # Если предупреждение появилось, закрываем его
                    warning.click()
                    logging.info("Закрыли предупреждение после голосования")
                except:
                    logging.info("Предупреждение после голосования не обнаружено")
                
                # Проверяем, не появилось ли окно с сообщением об успешном голосовании
                try:
                    success_message = WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.success-message"))
                    )
                    logging.info("Обнаружено сообщение об успешном голосовании")
                except:
                    # Если нет специального сообщения, считаем голосование успешным по умолчанию
                    logging.info("Сообщение об успешном голосовании не обнаружено, но продолжаем")
                
                # Ждем некоторое время для завершения голосования
                time.sleep(random.uniform(2, 4))
                
                # Проверяем успешность голосования
                # Можно добавить дополнительную проверку, если на сайте есть индикатор успешного голосования
                
                logging.info("Голосование успешно выполнено")
                successful_votes += 1
                
            except TimeoutException:
                logging.error(f"Таймаут при поиске элемента на странице")
            except NoSuchElementException as e:
                logging.error(f"Элемент не найден на странице: {e}")
            except ElementClickInterceptedException as e:
                logging.error(f"Не удалось кликнуть по элементу (перехвачено): {e}")
                
                # Пробуем обработать ситуацию, когда клик перехвачен
                try:
                    if driver:
                        # Проверяем наличие предупреждения
                        warning = WebDriverWait(driver, 2).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.warning"))
                        )
                        # Если предупреждение есть, закрываем его
                        warning.click()
                        logging.info("Закрыли перехватившее предупреждение")
                        
                        # Пробуем снова кликнуть по кнопке голосования
                        time.sleep(1)
                        vote_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.vote-btn"))
                        )
                        vote_button.click()
                        logging.info("Повторно кликнули по кнопке голосования после закрытия предупреждения")
                        
                        # Ждем завершения голосования
                        time.sleep(3)
                        successful_votes += 1
                except:
                    logging.error("Не удалось обработать перехват клика")
                    
            except Exception as e:
                logging.error(f"Ошибка при голосовании: {e}")
            finally:
                if driver:
                    # Очищаем кеш и куки перед закрытием браузера
                    self._clear_browser_data(driver)
                    
                    # Закрываем браузер
                    try:
                        driver.quit()
                        logging.info("Браузер закрыт")
                    except Exception as e:
                        logging.warning(f"Ошибка при закрытии браузера: {e}")
            
            # Если это не последнее голосование, делаем паузу перед следующим
            if vote_num < num_votes:
                delay = random.uniform(delay_between_votes[0], delay_between_votes[1])
                logging.info(f"Ожидание {delay:.2f} секунд перед следующим голосованием...")
                time.sleep(delay)
        
        logging.info(f"Голосование завершено. Успешно: {successful_votes} из {num_votes}")
        return successful_votes






















def vote_with_proxy(url, team_id=15, team_name="Центр ВОИН", num_votes=10, 
                   delay_between_votes=(5, 15), proxy_list=None, headless=False):
    """
    Автоматическое голосование с использованием списка прокси
    
    Args:
        url (str): URL сайта с голосованием
        team_id (int): ID команды (из атрибута onclick="confirmation(ID)")
        team_name (str): Название команды для голосования
        num_votes (int): Количество голосований
        delay_between_votes (tuple): Диапазон задержки между голосованиями в секундах
        proxy_list (list): Список прокси-серверов в формате ["ip:port", ...]
        headless (bool): Запускать ли браузер в фоновом режиме
    """
    if not proxy_list:
        logging.warning("Список прокси пуст. Голосование будет выполнено без прокси.")
        voter = TeamVoter(headless=headless)
        return voter.vote_for_team(url, team_id, team_name, num_votes, delay_between_votes)
    
    successful_votes = 0
    
    for vote_num in range(1, num_votes + 1):
        # Выбираем случайный прокси из списка
        if proxy_list:
            proxy = random.choice(proxy_list)
            logging.info(f"Используем прокси: {proxy}")
        else:
            proxy = None
            logging.info("Прокси не используется")
        
        # Настраиваем браузер с прокси
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")  # Новый headless режим
        
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Предварительно разрешаем геолокацию
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1,  # 1 = разрешить, 2 = блокировать
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.notifications": 1
        })
        
        # Добавляем прокси, если он есть
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Добавляем аргументы для уменьшения вероятности обнаружения автоматизации
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Случайный User-Agent
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        ]
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        driver = None
        try:
            # Инициализируем драйвер
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.maximize_window()
            
            # Устанавливаем скрипт для маскировки Selenium
            driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            
            # Переходим на сайт голосования
            logging.info(f"Открываем URL: {url}")
            driver.get(url)
            
            # Ждем загрузки страницы
            time.sleep(random.uniform(2, 5))
            
            # Скроллим страницу до конца, чтобы найти команду
            logging.info("Скроллим страницу до конца")
            total_height = driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            while current_position < total_height:
                scroll_step = random.randint(200, 500)
                current_position += scroll_step
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(random.uniform(0.2, 0.5))
            
            # Ищем блок с нужной командой по названию
            logging.info(f"Ищем команду: {team_name}")
            
            # Пробуем найти команду по разным селекторам
            team_selectors = [
                f"//div[contains(@class, 'pvn') and contains(., '{team_name}')]",
                f"//div[contains(@class, 'pvn-title') and contains(text(), '{team_name}')]/..",
                f"//div[contains(@class, 'pvn-title') and text()='{team_name}']/.."
            ]
            
            team_element = None
            for selector in team_selectors:
                try:
                    team_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    logging.info(f"Команда найдена по селектору: {selector}")
                    break
                except:
                    continue
            
            if not team_element:
                logging.error(f"Не удалось найти команду: {team_name}")
                raise NoSuchElementException(f"Команда {team_name} не найдена на странице")
            
            # Имитируем движение мыши к элементу команды
            action = ActionChains(driver)
            action.move_to_element(team_element)
            action.perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # Вместо клика по элементу, напрямую вызываем JavaScript функцию confirmation
            logging.info(f"Вызываем JavaScript функцию confirmation({team_id})")
            driver.execute_script(f"confirmation({team_id})")
            
            # Ждем появления окна голосования
            time.sleep(random.uniform(1, 2))
            
            # Проверяем, что окно голосования открылось
            try:
                vote_window = WebDriverWait(driver, 4).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.vote"))
                )
                logging.info("Окно голосования успешно открылось")
            except TimeoutException:
                logging.warning("Окно голосования не появилось. Пробуем альтернативный метод.")
                # Если окно не появилось, пробуем кликнуть по элементу
                team_element.click()
                time.sleep(random.uniform(1, 2))
            
            # Повторно проверяем наличие окна голосования
            vote_window = WebDriverWait(driver, 4).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.vote"))
            )
            
            # Находим кнопку голосования
            vote_button = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.vote-btn"))
            )
            
            # Имитируем движение мыши к кнопке голосования
            action = ActionChains(driver)
            action.move_to_element(vote_button)
            action.perform()
            time.sleep(random.uniform(0.5, 1.0))
            
            # Кликаем по кнопке голосования
            logging.info("Кликаем по кнопке голосования")
            vote_button.click()
            
            # Ждем появления запроса на геолокацию
            time.sleep(random.uniform(1, 2))
            
            # Обрабатываем возможное уведомление в Chrome
            try:
                # Проверяем наличие диалогового окна
                alert = driver.switch_to.alert
                alert.accept()
                logging.info("Приняли диалоговое окно")
            except:
                # Если диалогового окна нет, пробуем нажать Enter
                try:
                    ActionChains(driver).send_keys(Keys.ENTER).perform()
                    logging.info("Нажали Enter для подтверждения")
                except Exception as e:
                    logging.warning(f"Не удалось обработать уведомление: {e}")
            
            # Проверяем, появилось ли предупреждение (warning)
            try:
                warning = WebDriverWait(driver, 4).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.warning"))
                )
                # Если предупреждение появилось, закрываем его
                warning.click()
                logging.info("Закрыли предупреждение")
            except:
                logging.info("Предупреждение не обнаружено")
            
            # Ждем некоторое время для завершения голосования
            time.sleep(random.uniform(1, 2))
            
            logging.info(f"Голосование #{vote_num} с прокси {proxy} успешно выполнено")
            successful_votes += 1
            
        except TimeoutException:
            logging.error(f"Таймаут при поиске элемента на странице с прокси {proxy}")
        except NoSuchElementException as e:
            logging.error(f"Элемент не найден на странице с прокси {proxy}: {e}")
        except ElementClickInterceptedException as e:
            logging.error(f"Не удалось кликнуть по элементу (перехвачено) с прокси {proxy}: {e}")
        except Exception as e:
            logging.error(f"Ошибка при голосовании с прокси {proxy}: {e}")
        finally:
            if driver:
                # Очищаем кеш и куки перед закрытием браузера
                try:
                    driver.delete_all_cookies()
                    if hasattr(driver, "execute_cdp_cmd"):
                        driver.execute_cdp_cmd('Network.clearBrowserCache', {})
                        driver.execute_cdp_cmd('Storage.clearDataForOrigin', {
                            'origin': '*',
                            'storageTypes': 'all',
                        })
                except Exception as e:
                    logging.warning(f"Ошибка при очистке данных браузера: {e}")
                
                # Закрываем браузер
                try:
                    driver.quit()
                    logging.info("Браузер закрыт")
                except Exception as e:
                    logging.warning(f"Ошибка при закрытии браузера: {e}")
        
        # Если это не последнее голосование, делаем паузу перед следующим
        if vote_num < num_votes:
            delay = random.uniform(delay_between_votes[0], delay_between_votes[1])
            logging.info(f"Ожидание {delay:.2f} секунд перед следующим голосованием...")
            time.sleep(delay)
    
    logging.info(f"Голосование с прокси завершено. Успешно: {successful_votes} из {num_votes}")
    return successful_votes


def load_proxies_from_file(file_path):
    """
    Загружает список прокси из файла
    
    Args:
        file_path (str): Путь к файлу со списком прокси (один прокси на строку в формате ip:port)
    
    Returns:
        list: Список прокси-серверов
    """
    try:
        with open(file_path, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
        logging.info(f"Загружено {len(proxies)} прокси из файла {file_path}")
        return proxies
    except Exception as e:
        logging.error(f"Ошибка при загрузке прокси из файла {file_path}: {e}")
        return []


def rotate_ip_via_vpn(vpn_name=None):
    """
    Функция для смены IP через VPN (заглушка)
    В реальном сценарии здесь должен быть код для управления VPN-клиентом
    
    Args:
        vpn_name (str): Название VPN-соединения (опционально)
    """
    logging.info("Смена IP через VPN...")
    # Здесь должен быть код для отключения и подключения VPN
    # Например, через командную строку или API VPN-клиента
    time.sleep(5)  # Имитация времени на переподключение
    logging.info("IP успешно изменен через VPN")


def main():
    """
    Основная функция для запуска голосования
    """
    # Параметры голосования
    vote_url = input("Введите URL сайта с голосованием: ")
    team_name = input("Введите название команды для голосования (по умолчанию 'Центр ВОИН'): ")
    if not team_name:
        team_name = "Центр ВОИН"
    try:
        team_id = int(input("Введите ID команды из атрибута onclick='confirmation(ID)' (по умолчанию 15): "))
    except ValueError:
        team_id = 15
        print(f"Некорректный ввод. Будет использовано значение по умолчанию: {team_id}")
    
    try:
        num_votes = int(input("Введите количество голосований: "))
    except ValueError:
        num_votes = 10
        print(f"Некорректный ввод. Будет использовано значение по умолчанию: {num_votes}")
    
    try:
        min_delay = float(input("Введите минимальную задержку между голосованиями (в секундах): "))
    except ValueError:
        min_delay = 5
        print(f"Некорректный ввод. Будет использовано значение по умолчанию: {min_delay}")
    
    try:
        max_delay = float(input("Введите максимальную задержку между голосованиями (в секундах): "))
    except ValueError:
        max_delay = 15
        print(f"Некорректный ввод. Будет использовано значение по умолчанию: {max_delay}")
    
    use_proxy = input("Использовать прокси? (y/n): ").lower() == 'y'
    proxies = []
    
    if use_proxy:
        proxy_file = input("Введите путь к файлу со списком прокси (или оставьте пустым): ")
        if proxy_file:
            proxies = load_proxies_from_file(proxy_file)
        else:
            proxy_input = input("Введите прокси вручную через запятую (ip:port,ip:port,...): ")
            if proxy_input:
                proxies = [p.strip() for p in proxy_input.split(',')]
    
    use_vpn = input("Использовать VPN для смены IP? (y/n): ").lower() == 'y'
    headless = input("Запустить браузер в фоновом режиме? (y/n): ").lower() == 'y'
    
    print("\nНачинаем процесс голосования...")
    
    if use_proxy and proxies:
        successful = vote_with_proxy(
            url=vote_url,
            team_id=team_id,
            team_name=team_name,
            num_votes=num_votes,
            delay_between_votes=(min_delay, max_delay),
            proxy_list=proxies,
            headless=headless
        )
    elif use_vpn:
        successful = 0
        voter = TeamVoter(headless=headless)
        
        for i in range(num_votes):
            logging.info(f"Голосование #{i+1} из {num_votes}")
            
            # Голосуем один раз
            result = voter.vote_for_team(
                url=vote_url,
                team_id=team_id,
                team_name=team_name,
                num_votes=1,
                delay_between_votes=(1, 2)  # Минимальная задержка, так как меняем IP
            )
            
            successful += result
            
            # Если это не последнее голосование, меняем IP через VPN
            if i < num_votes - 1:
                rotate_ip_via_vpn()
                delay = random.uniform(min_delay, max_delay)
                logging.info(f"Ожидание {delay:.2f} секунд перед следующим голосованием...")
                time.sleep(delay)
    else:
        voter = TeamVoter(headless=headless)
        successful = voter.vote_for_team(
            url=vote_url,
            team_id=team_id,
            team_name=team_name,
            num_votes=num_votes,
            delay_between_votes=(min_delay, max_delay)
        )
    
    print(f"\nГолосование завершено. Успешно выполнено {successful} из {num_votes} голосований.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
    except Exception as e:
        logging.error(f"Непредвиденная ошибка: {e}")
        print(f"\nПроизошла ошибка: {e}")
        print("Подробности смотрите в файле логов auto_vote.log")





