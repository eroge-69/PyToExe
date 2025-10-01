import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def main():
    # Настройка опций Chrome для режима инкогнито
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    
    # Автоматическая установка и настройка ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Открытие страницы
        driver.get("https://www.e1.ru/text/education/2025/10/02/76050666/")
        print("Страница открыта")
        
        # Поиск и клик по элементу
        wait = WebDriverWait(driver, 10)
        element = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Мария Шикина')]"))
        )
        element.click()
        print("Клик выполнен на элемент 'Мария Шикина'")
        
        # Ожидание 0.5 секунды после клика
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
    finally:
        driver.quit()
        print("Браузер закрыт")

if __name__ == "__main__":
    main()