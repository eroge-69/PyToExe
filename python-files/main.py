from time import sleep
from opentele.td import TDesktop
from opentele.api import API, CreateNewSession
import os
import asyncio
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


with open("proxy.txt", "r", encoding="utf-8") as f:
    proxy = f.read()



def get_folders_pathlib(path):
    path = Path(path)
    return [folder.name for folder in path.iterdir() if folder.is_dir()]



def wait_for_element(driver, locator, timeout=10, condition="visible"):
    conditions = {
        "visible": EC.visibility_of_element_located,
        "present": EC.presence_of_element_located,
        "clickable": EC.element_to_be_clickable
    }

    if condition not in conditions:
        raise ValueError(f"Неподдерживаемый тип ожидания: {condition}")

    return WebDriverWait(driver, timeout).until(
        conditions[condition](locator)
    )

async def get_telegram_code(client):
        telegram_entity = await client.get_entity(777000)

        messages = await client.get_messages(telegram_entity, limit=5)

        for msg in messages:
            if not msg.out:
                code = extract_code_from_text(msg.text)
                if code:
                    print(f"Найден код подтверждения: {code}")
                    return code

        print("Сообщение с кодом не найдено")
        return None


def extract_code_from_text(text):

    match = re.search(r'\b\d{5}\b', text)
    if match:
        return match.group(0)

    match_long = re.search(r'\b\d{6,8}\b', text)
    if match_long:
        return match_long.group(0)

    alt_formats = [
        r'код: (\d{5})',
        r'code: (\d{5})',
        r'(\d{5}) is your code',
        r'使用代码 (\d{5})'
    ]

    for pattern in alt_formats:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None

async def main(tdataPath, card):
    try:
        cardData = card.split(" ")
        try:
            os.remove("Session.session")
        except:
            pass

        print(f"Начали вход в аккаунт по пути {tdataPath} и карты {cardData[0]}")
        try:
            tdesk = TDesktop(tdataPath)
        except:
            print("Произошла ошибка при подключении к tdata")
            return "tdataError"

        api = API.TelegramDesktop.Generate()

        client = await tdesk.ToTelethon("Session.session", CreateNewSession, api)

        await client.connect()

        await client.send_message("PremiumBot", "/start")

        me = await client.get_me()
        print(f"Мы усппешно подключились к аккаунту @{me.username}\nId: {me.id}\nПриступаем к покупке премиума\n\n")
        try:

            chrome_options = Options()
            chrome_options.add_argument(f"--proxy-server={proxy}")
            chrome_options.add_argument("--headless")  # Фоновый режим

            driver = webdriver.Chrome()

            driver.get("https://web.telegram.org/k/#@PremiumBot")
            el = wait_for_element(
                driver,
                (By.CSS_SELECTOR, ".btn-primary.btn-secondary.btn-primary-transparent.primary.rp"),
                timeout=20,
                condition="visible"
            )
            el.click()

            l = wait_for_element(
                driver,
                (By.CSS_SELECTOR, "[inputmode=\"decimal\"]"),
                timeout=20,
                condition="visible"
            )
            l.click()
            l.clear()
            l.send_keys(f"{me.phone}")
            btn = driver.find_element(By.CSS_SELECTOR, ".btn-primary.btn-color-primary.rp")
            btn.click()

            k = wait_for_element(
                driver,
                (By.CSS_SELECTOR, "[autocomplete=\"off\"]"),
                timeout=20,
                condition="visible"
            )

            sleep(1)
            code = await  get_telegram_code(client)
            k.click()
            k.send_keys(code)

            r = wait_for_element(
                driver,
                (By.CSS_SELECTOR, ".is-buy.is-first.is-last.reply-markup-button.rp .c-ripple"),
                timeout=20,
                condition="visible"
            )
            r.click()
            z = wait_for_element(
                driver,
                (By.CSS_SELECTOR, "[class=\"row no-wrap row-with-icon row-with-padding row-clickable hover-effect rp payment-item-row payment-item-method-row\"]"),
                timeout=20,
                condition="visible"
            )
            z.click()
            sleep(2)

            iframe = driver.find_element(
                By.CSS_SELECTOR,
                'iframe'
            )
            driver.switch_to.frame(iframe)

            v = wait_for_element(
                driver,
                (By.CSS_SELECTOR,
                 "[class=\"i10db8us ipdffau ijwne1g\"]"),
                timeout=20,
                condition="visible"
            )

            v.click()
            v.clear()
            v.send_keys(cardData[0])

            y = wait_for_element(
                driver,
                (By.CSS_SELECTOR,
                 "[class=\"ii5f1jm if3xil7 ipdffau ijwne1g\"]"),
                timeout=20,
                condition="visible"
            )
            y.clear()
            y.send_keys(cardData[1])


            f = wait_for_element(
                driver,
                (By.CSS_SELECTOR,
                 "[class=\"ighm5a8 if3xil7 ipdffau ijwne1g\"]"),
                timeout=20,
                condition="visible"
            )
            f.clear()
            f.send_keys(cardData[2])

            enterButt= wait_for_element(
                driver,
                (By.CSS_SELECTOR,
                 "[class=\"r166jolf\"]"),
                timeout=20,
                condition="visible"
            )
            enterButt.click()
            print(f"Купили премиум для @{me.username} | {me.id} прступаем к следующему аккаунту")
            sleep(5)
            driver.quit()
        except Exception as ex:
            print("Произошла ошибка при покупке премиума" )
            print(ex)
    except Exception as e:
        print(e)

tdatas = get_folders_pathlib("TdataLibs")

with open("Cards.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

nm = 0
i = 0
for t in tdatas:
    try:
        asyncio.run(main(f"TdataLibs/{t}", lines[i]))
        nm += 1
        if nm == 4:
            i += 1
            nm = 0
    except:
        print("У вас закончились карты")
        break

