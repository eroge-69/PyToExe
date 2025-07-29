import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
import random

# Функция для случайных задержек
def random_delay(min_delay=0.5, max_delay=2.5):
    time.sleep(random.uniform(min_delay, max_delay))

# Настройки браузера
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Запуск браузера
driver = uc.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

try:
    # 1) Открытие страницы
    driver.get("https://www.avito.ru/profile/pro/items ")
    print("Браузер открыт. Дождитесь, пока вы авторизуетесь.")
    input("Нажмите Enter в терминале, чтобы продолжить...")

    while True:
        try:
            # 4) Перейти во вкладку "Архив"
            print("Поиск вкладки 'Архив'...")
            archive_tab = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Архив")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", archive_tab)
            random_delay()
            archive_tab.click()
            random_delay()

            # 5) Кликнуть по div вместо чекбокса
            print("Клик по div вместо чекбокса...")
            cover_div = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.css-1s1m1fg'))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cover_div)
            random_delay(1, 2)

            try:
                cover_div.click()
            except ElementClickInterceptedException:
                print("Клик заблокирован. Пробую через JS...")
                driver.execute_script("arguments[0].click();", cover_div)

            random_delay()

            # 6) Нажать на кнопку "Удалить" (в списке действий)
            print("Нажатие кнопки 'Удалить' через span...")
            delete_span = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Удалить")]'))
            )
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", delete_span)
            random_delay()

            try:
                delete_span.click()
            except ElementClickInterceptedException:
                print("Клик заблокирован. Пробую через JS...")
                driver.execute_script("arguments[0].click();", delete_span)

            random_delay()

            # 7) Пролистать вниз и подтвердить удаление
            print("Пролистываю вниз и подтверждаю удаление...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            random_delay(1, 2)

            confirm_span = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'span.button-textBox-I7MBX'))
            )

            try:
                confirm_span.click()
            except ElementClickInterceptedException:
                print("Клик заблокирован. Пробую через JS...")
                driver.execute_script("arguments[0].click();", confirm_span)

            random_delay()

            # 8) Обновить страницу
            print("Обновление страницы...")
            driver.refresh()
            random_delay(3, 5)

        except (TimeoutException, ElementClickInterceptedException) as e:
            print(f"Ошибка при выполнении действий: {e}")
            print("Повторная попытка через несколько секунд...")
            driver.refresh()
            random_delay(5, 7)
            continue

except KeyboardInterrupt:
    print("Скрипт остановлен пользователем.")

finally:
    print("Закрытие браузера...")
    driver.quit()