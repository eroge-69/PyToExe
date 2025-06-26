
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time, re, csv, os

# Настройки логирования сетевых запросов
caps = DesiredCapabilities.CHROME
caps["goog:loggingPrefs"] = {"performance": "ALL"}

options = Options()
options.add_argument("--start-maximized")

print("Запуск браузера...")
driver = webdriver.Chrome(options=options, desired_capabilities=caps)

driver.get("https://dataset.mib.uz/")
time.sleep(2)

# Авторизация
print("Вход в систему...")
driver.find_element(By.NAME, "username").send_keys("Toshkent_shah")
driver.find_element(By.NAME, "password").send_keys("1230123")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
time.sleep(5)

# Фильтр по "Matn kiritilmagan"
print("Установка фильтра 'Matn kiritilmagan'...")
filter_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Jami')]/ancestor::button")
filter_button.click()
time.sleep(1)
filter_button.click()
time.sleep(4)

collected = []

for page in range(70):  # Страниц может быть до 65-70
    print(f"Обработка страницы {page + 1}...")
    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    for row in rows:
        try:
            id_text = row.find_element(By.XPATH, ".//td[1]").text.strip()
            menu_btn = row.find_element(By.CSS_SELECTOR, "button[aria-label='Harakatlar']")
            driver.execute_script("arguments[0].click();", menu_btn)
            time.sleep(0.5)

            download_btn = driver.find_element(By.XPATH, '//span[contains(text(), "Скачать")]/ancestor::li')
            driver.execute_script("arguments[0].click();", download_btn)
            time.sleep(1.5)

            logs = driver.get_log("performance")
            for entry in logs[::-1]:
                msg = entry["message"]
                if "stt-data-audio?uuid=" in msg:
                    match = re.search(r'uuid=([a-f0-9\-]{36})', msg)
                    if match:
                        uuid = match.group(1)
                        print(f"→ ID: {id_text}  |  UUID: {uuid}")
                        collected.append((id_text, uuid))
                        break

        except Exception as e:
            print(f"[!] Ошибка при обработке строки: {e}")
            continue

    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Следующая страница']")
        if not next_btn.is_enabled():
            break
        next_btn.click()
    except:
        print("Кнопка 'Следующая страница' не найдена или недоступна.")
        break

driver.quit()

# Сохранение в CSV
out_path = os.path.join(os.getcwd(), "audio_links.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "UUID"])
    writer.writerows(collected)

print(f"✅ Готово! Сохранено: {out_path}")
input("Нажмите Enter для выхода...")
