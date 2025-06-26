import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import uuid
import os
import random
import string
from cryptography.fernet import Fernet
import time

# --- DANE DO BAZY DANYCH ---
DB_HOST = 'sql161.lh.pl'
DB_USER = 'serwer363456_fotka'
DB_PASSWORD = 'Loltolol-18235'
DB_NAME = 'serwer363456_fotka'
LOCAL_LICENSE_FILE = 'license.lic'

ENCRYPTION_KEY = b"rlCXDriYSTJ0nCQi57yVn1cW2CZLFM0V4ZP2zzKzAjw="
fernet = Fernet(ENCRYPTION_KEY)

# --- FUNKCJE SZYFROWANIA ---
def save_encrypted_license(filename, license_key):
    encrypted = fernet.encrypt(license_key.encode())
    with open(filename, 'wb') as f:
        f.write(encrypted)

def load_encrypted_license(filename):
    with open(filename, 'rb') as f:
        encrypted = f.read()
    return fernet.decrypt(encrypted).decode()

# --- FUNKCJE POMOCNICZE ---
def wait_and_click(driver, by, selector, timeout=20):
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    element.click()

def wait_and_send_keys(driver, by, selector, text, timeout=20):
    element = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )
    element.clear()
    element.send_keys(text)

def element_exists(driver, by, identifier):
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((by, identifier)))
        return True
    except:
        return False

def generate_license_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

def get_machine_uuid():
    return str(uuid.getnode())

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = db.cursor()

    machine_id = get_machine_uuid()

    if os.path.exists(LOCAL_LICENSE_FILE):
        # Odczytaj zaszyfrowany klucz lokalnie
        MY_LICENSE_KEY = load_encrypted_license(LOCAL_LICENSE_FILE)
    else:
        MY_LICENSE_KEY = generate_license_key()

        # Zapisz lokalnie
        save_encrypted_license(LOCAL_LICENSE_FILE, MY_LICENSE_KEY)

        # Wstaw do bazy z aktywacją = 0
        insert_query = """
                INSERT INTO licenses (machine_id, license_key, active) 
                VALUES (%s, %s, %s)
            """
        cursor.execute(insert_query, (machine_id, MY_LICENSE_KEY, 0))
        db.commit()

        print("🆕 Nowy klucz został wygenerowany i przesłany do bazy danych.")
        print("⏳ Poczekaj na aktywację klucza przez administratora.")
        input("Naciśnij Enter, aby zamknąć program.")
        sys.exit()

    # Sprawdź status klucza w bazie
    check_query = "SELECT active FROM licenses WHERE license_key = %s AND machine_id = %s"
    cursor.execute(check_query, (MY_LICENSE_KEY, machine_id))
    result = cursor.fetchone()

    if result and result[0]:
        print("✅ Licencja jest aktywna. Bot uruchomiony.")

        # Zaktualizuj datę ostatniego uruchomienia
        update_query = "UPDATE licenses SET last_run = NOW() WHERE license_key = %s AND machine_id = %s"
        cursor.execute(update_query, (MY_LICENSE_KEY, machine_id))
        db.commit()

        login = input("Podaj login: ")
        password = input("Podaj haslo: ")
        WIADOMOSC = input("Podaj tresc wiadomosci: ")

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.page_load_strategy = 'eager'

        service = Service("chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://fotka.com/zaloguj")

        # Akceptacja cookies
        wait_and_click(driver, By.XPATH, '/html/body/div[8]/div[1]/div[2]/div[2]/div[2]/button[2]')

        # Logowanie
        wait_and_send_keys(driver, By.ID, "email-login", login)
        wait_and_send_keys(driver, By.ID, "password-login", password)
        wait_and_click(driver, By.XPATH, '/html/body/div[3]/div[2]/div[5]/div[1]/div[2]/div[2]/div/div/div/div/form/div[2]/button')

        # Sprawdź, czy trzeba zamknąć popup
        time.sleep(3)
        try:
            close_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "close-button"))
            )
            close_button.click()
        except:
            print("")


        # Kliknij menu__logo
        driver.get("https://fotka.com/")

        # Sprawdź, czy trzeba zamknąć popup
        time.sleep(3)
        try:
            close_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, "close-button"))
            )
            close_button.click()
        except:
            print("")

        print("✅ Bot gotowy. Rozpoczynam wysyłanie wiadomości.")

        # --- GŁÓWNA PĘTLA ---
        while True:
            try:
                if element_exists(driver, By.ID, "close-button"):
                    driver.find_element(By.ID, "close-button").click()
                # Kliknij w użytkownika (karuzela)
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div/div/div[4]/div/div/div/div[2]/div/div[1]/div"))
                ).click()

                # Sprawdź czy można wysłać wiadomość
                if element_exists(driver, By.CLASS_NAME, "typography__ButtonBase-sc-19wsb7h-9"):
                    time.sleep(1)
                    if element_exists(driver, By.ID, "close-button"):
                        driver.find_element(By.ID, "close-button").click()
                    driver.find_element(By.CLASS_NAME, "typography__ButtonBase-sc-19wsb7h-9").click()

                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "messageFieldstyled__Field-sc-1q3m943-7"))
                    ).send_keys(WIADOMOSC)

                    wait_and_click(driver, By.CSS_SELECTOR,
                                   "button[type='submit']")

                    # Powrót do głównego widoku
                    wait_and_click(driver, By.ID, "menu__logo")
                    time.sleep(1)
                    if element_exists(driver, By.ID, "close-button"):
                        driver.find_element(By.ID, "close-button").click()

                else:
                    try:
                        wait_and_click(driver, By.CLASS_NAME, "rynS3USfrvGjj6DvpheC")
                    except Exception as e:
                        print("")

                time.sleep(1)

            except Exception as e:
                print("⚠️ Błąd w pętli:", e)
                time.sleep(3)

    elif result:
        print("❌ Licencja jest nieaktywna. Poczekaj na zatwierdzenie.")
        input("Naciśnij Enter, aby zamknąć program.")
        sys.exit()
    else:
        print("❌ Klucz nie istnieje w bazie. Usuń plik license.lic i spróbuj ponownie.")
        input("Naciśnij Enter, aby zamknąć program.")
        sys.exit()

except mysql.connector.Error as err:
    print("❌ Błąd połączenia z bazą:", err)

except Exception as e:
    print("❌ Błąd działania bota:", e)

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals():
        db.close()

# NIE zamykamy przeglądarki automatycznie
input("\n🛑 Bot zakończył działanie. Naciśnij Enter, aby zamknąć.")
