from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurazione ChromeDriver
service = Service("C:/Users/magazzino10/Documents/Selenium/Test selenium/chromedriver.exe")
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)  # aspetta max 15 secondi

try:
    # Apri la pagina
    driver.get("http://192.168.1.27:8080/apex/f?p=STAMPE:1:10415936408272:::::")

    # 1. Clicca "Giacenza"
    giacenze = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Giacenze")))
    giacenze.click()

    # 2. Clicca "Actions"
    actions_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Actions')]")))
    actions_btn.click()

    # 3. Aspetta che compaia "Filter" e cliccaci
    filter_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Filter')]")))
    filter_btn.click()

    # 4. Campo Expression → scrivi "P"
    # Trova il label "Expression", poi il primo input dopo di esso
    label = wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='Expression']")))
    expression_input = label.find_element(By.XPATH, "following::input[1]")
    wait.until(EC.visibility_of(expression_input))
    time.sleep(1)  # piccola pausa per sicurezza
    expression_input.clear()
    time.sleep(1)  # piccola pausa per sicurezza
    expression_input.send_keys("P")
    time.sleep(1)

    # 5. Clicca "Apply"
    apply_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')]")))
    apply_btn.click()
    time.sleep(1)

    # 6. Clicca di nuovo "Actions"
    actions_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Actions')]")))
    actions_btn.click()
    time.sleep(1)

    # 7. Clicca "Download"
    download_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Download')]")))
    download_btn.click()
    time.sleep(1)

    # 8. Clicca "CSV"
    csv_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'CSV')]")))
    csv_btn.click()

    time.sleep(20)  # aspetta che scarichi

finally:
    driver.quit()
