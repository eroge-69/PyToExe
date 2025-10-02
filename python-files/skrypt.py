"""
Edukacyjny przykład: wypełnienie formularza raz (pierwszy email z emails.txt).
Zależności:
  pip install selenium webdriver-manager

Uwaga: jeśli strona używa dynamicznego ładowania (AJAX), XPath/ID mogą wymagać dopracowania.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# --- konfig ---
URL = "https://osp.loteriaharnas.pl/"  # strona docelowa
EMAILS_FILE = "emails.txt"             # plik z adresami (użyjemy tylko pierwszego)
IMPLICIT_WAIT = 0.5
EXPLICIT_WAIT = 15

# --- helpery ---
def read_first_email(filename):
    """Wczytaj pierwszy niepusty wiersz z pliku jako email."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    return line
    except FileNotFoundError:
        return None
    return None

def select_by_label(driver, label_snippet, option_text):
    """
    Próbuj znaleźć <label> zawierający label_snippet i wybrać pierwsze <select> następujące po nim.
    Fallback: wyszukaj selecty i wybierz ten, który zawiera opcję option_text.
    """
    try:
        # 1) label -> following select
        label = driver.find_element(By.XPATH, f"//label[contains(normalize-space(.), '{label_snippet}')]")
        select_elem = label.find_element(By.XPATH, ".//following::select[1]")
        Select(select_elem).select_by_visible_text(option_text)
        return True
    except Exception:
        pass

    # 2) fallback: przeszukaj wszystkie selecty i wybierz ten który ma opcję o takim tekście
    selects = driver.find_elements(By.TAG_NAME, "select")
    for s in selects:
        try:
            Select(s).select_by_visible_text(option_text)
            return True
        except Exception:
            continue
    return False

def click_checkbox_by_label(driver, label_snippet):
    """
    Kliknij checkbox powiązany z etykietą zawierającą label_snippet.
    Najpierw próbujemy znaleźć <label> i odwołać się do 'for' -> input.
    Jeśli to się nie uda, klikamy sam label.
    """
    try:
        label = driver.find_element(By.XPATH, f"//label[contains(normalize-space(.), '{label_snippet}')]")
        for_attr = label.get_attribute("for")
        if for_attr:
            inp = driver.find_element(By.ID, for_attr)
            driver.execute_script("arguments[0].scrollIntoView(true);", inp)
            inp.click()
            return True
        else:
            # kliknij label (często powoduje zaznaczenie checkboxa)
            driver.execute_script("arguments[0].scrollIntoView(true);", label)
            label.click()
            return True
    except Exception:
        pass

    # fallback: spróbuj znaleźć input typu checkbox z tekstem obok
    try:
        chk = driver.find_element(By.XPATH, f"//input[@type='checkbox' and (contains(@id,'{label_snippet}') or contains(@name,'{label_snippet}'))]")
        driver.execute_script("arguments[0].scrollIntoView(true);", chk)
        chk.click()
        return True
    except Exception:
        return False

# --- główny skrypt ---
def main():
    email = read_first_email(EMAILS_FILE)
    if not email:
        print(f"Nie znaleziono adresu w pliku {EMAILS_FILE}. Wstaw przynajmniej jeden adres e-mail w pliku i uruchom ponownie.")
        return

    # uruchomienie przeglądarki
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")  # odkomentuj jeśli chcesz bez headless (dla debugowania lepiej widoczna)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(3)

    wait = WebDriverWait(driver, EXPLICIT_WAIT)

    try:
        driver.get(URL)

        # czekamy, aż strona się załaduje - tu czekamy na jakieś selecty na stronie
        # (dostosuj selektor jeśli strona ma niestandardową strukturę)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))

        time.sleep(1)  # krótka pauza by JS zdążył z populacją opcji

        # wybory (jeżeli selecty/etykiety są napisane inaczej, zmień label_snippet lub option_text)
        ok = select_by_label(driver, "Województwo", "wielkopolskie")
        if not ok:
            print("Uwaga: nie udało się wybrać województwa automatycznie. Sprawdź selektory.")
        else:
            print("Wybrane województwo: wielkopolskie")

        # krótka przerwa i odczekanie aby powiaty się doładowały (często zależne od wyboru województwa)
        time.sleep(1.5)
        ok = select_by_label(driver, "Powiat", "ostrowski")
        if not ok:
            print("Uwaga: nie udało się wybrać powiatu automatycznie. Sprawdź selektory.")
        else:
            print("Wybrany powiat: ostrowski")

        time.sleep(1)
        ok = select_by_label(driver, "Miejscowość", "Sośnie")
        if not ok:
            print("Uwaga: nie udało się wybrać miejscowości automatycznie. Sprawdź selektory.")
        else:
            print("Wybrana miejscowość: Sośnie")

        # wprowadź e-mail - spróbuj znaleźć pola typu email lub tekstowe z nazwą 'email'
        try:
            email_input = None
            # najpierw spróbuj pola typu email
            try:
                email_input = driver.find_element(By.XPATH, "//input[@type='email']")
            except Exception:
                # fallback: input zawierający 'email' w id/name/placeholder
                email_input = driver.find_element(By.XPATH, "//input[contains(translate(@id,'EMAIL','email'),'email') or contains(translate(@name,'EMAIL','email'),'email') or contains(translate(@placeholder,'EMAIL','email'),'email')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
            email_input.clear()
            email_input.send_keys(email)
            print(f"Wpisano email: {email}")
        except Exception:
            print("Nie znaleziono pola e-mail - sprawdź strukturę strony i popraw XPath'y.")

        # zaznacz checkboxy (regulamin i 18+)
        ok1 = click_checkbox_by_label(driver, "regulamin")
        ok2 = click_checkbox_by_label(driver, "18")
        # alternatywne etykiety: "Regulamin", "ukończyłem", "mam 18" - w razie potrzeby dopasuj
        print(f"Checkbox regulamin: {'OK' if ok1 else 'BRAK'}, checkbox 18+: {'OK' if ok2 else 'BRAK'}")

        # kliknij przycisk "Głosuj" (znajdujemy button/a zawierający tekst 'Głosuj')
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(normalize-space(.), 'Głosuj') or //a[contains(normalize-space(.), 'Głosuj')]]")
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            btn.click()
            print("Kliknięto Głosuj")
        except Exception:
            # drugi fallback: przycisk z wartością 'glosuj' w id/name
            try:
                btn2 = driver.find_element(By.XPATH, "//input[contains(translate(@id,'GLOSUJ','glosuj'),'glosuj') or contains(translate(@name,'GLOSUJ','glosuj'),'glosuj')]")
                driver.execute_script("arguments[0].scrollIntoView(true);", btn2)
                btn2.click()
                print("Kliknięto Głosuj (fallback input)")
            except Exception:
                print("Nie udało się znaleźć/kliknąć przycisku Głosuj. Sprawdź selektory.")

        # poczekaj trochę by zobaczyć efekt
        time.sleep(5)

    finally:
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()
