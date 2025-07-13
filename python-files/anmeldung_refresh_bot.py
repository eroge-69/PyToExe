from plyer import notification
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore
import re
from datetime import datetime, timedelta
import locale
import time
import os
import requests

os.system('title [Zulassungsbeast]: Anmeldung von Neu- oder Gebrauchtwagen')

locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
init(autoreset=True)

def send_telegram_message(message):
    bot_token = "7939989413:AAEsJ6FvTqzsYeh5cAX3J-kayawdT-HMqHY"
    chat_id = "8023549199"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
    response = requests.get(url)
    return response

def get_dates():
    today = datetime.today() #today = datetime(2025, 4, 22)
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    return today, tomorrow, day_after_tomorrow

def get_formatted_date(date):
    return date.strftime('%A, %d.%m.%Y')

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional, falls du den Browser im Hintergrund laufen lassen möchtest
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def navigate_to_appointments(driver):
    driver.get("https://tevis.ekom21.de/fra/select2?md=2")
    print(Fore.YELLOW + "[XY Bot]: Suche nach freien Termin für 'Anmeldung von Neu- oder Gebrauchtwagen'")
    try:
        cookie_banner = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "cookie_msg"))
        )
        cookie_accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@id="cookie_msg_btn_yes"]'))
        )
        cookie_accept_button.click()

        anmeldung_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//h3[contains(text(), "Anmeldung, Abmeldung und sonstige Dienstleistungen")]'))
        )
        anmeldung_button.click()

        full_xpath_button = "/html/body/main/div[1]/div[2]/form/div[1]/div/ul/li[1]/div/div/div[2]/span[2]/button"
        anmeldung_fahrzeug_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, full_xpath_button))
        )
        anmeldung_fahrzeug_button.click()

        weiter_button_xpath = "/html/body/main/div[1]/div[2]/form/input[4]"
        weiter_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, weiter_button_xpath))
        )

        weiter_button.click()

        info_box_ok_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]'))
        )
        info_box_ok_button.click()

        weiter_button_xpath_2 = "/html/body/main/div/div[4]/form/input[5]"
        weiter_button_2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, weiter_button_xpath_2))
        )
        weiter_button_2.click()

        # Warte auf die Seite mit den freien Terminen
        free_appointments_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="infobox_content"]/dl/dd[3]/span'))
        )
    except Exception as e:
        print(Fore.RED + f"[XY Bot]: Fehler beim Navigieren zur Termin-Seite: {e}")
        driver.quit()

def check_for_free_appointments(driver):
    appointments_text = driver.page_source

    # Termine für die nächsten 6 Tage (inkl. heute)
    dates_to_check = [datetime.today() + timedelta(days=i) for i in range(7)]

    for date in dates_to_check:
        formatted_date = get_formatted_date(date)
        if formatted_date in appointments_text:
            print(Fore.GREEN + f"[XY Bot]: Freier Termin gefunden für: {formatted_date}")
            notification.notify(
                title="XY Bot: Anmeldung",
                message=f"Termin für folgendes Datum ist frei: {formatted_date}",
                timeout=10
            )
            send_telegram_message(
                f"[Anmeldung von Neu- oder Gebrauchtwagen]\nFreier Termin gefunden für: {formatted_date}\nLink: https://tevis.ekom21.de/fra/select2?md=2"
            )
            break
    else:
        print(Fore.RED + "[XY Bot]: Keine freien Termine in den nächsten 7 Tagen gefunden")

def refresh_and_check(driver):
    while True:
        check_for_free_appointments(driver)
        driver.refresh()  # Die Seite wird alle 3 Sekunden aktualisiert
        time.sleep(3)

# Driver Setup und Initialisierung
driver = setup_driver()
navigate_to_appointments(driver)
refresh_and_check(driver)  # Startet die Überprüfung und das Aktualisieren der Seite