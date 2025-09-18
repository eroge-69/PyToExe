import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 🔹 Nome do grupo exatamente como aparece no WhatsApp
NOME_GRUPO = "Nome do Seu Grupo"
# 🔹 Mensagem a enviar
MENSAGEM = "Bom dia 🌞"

# Configura o ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=selenium")  # mantém login
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Abre o WhatsApp Web
driver.get("https://web.whatsapp.com/")
print("Escaneie o QR Code se for a primeira vez...")
time.sleep(20)  # tempo para escanear

# Procura pelo grupo
grupo = driver.find_element(By.XPATH, f'//span[@title="{NOME_GRUPO}"]')
grupo.click()
time.sleep(2)

# Caixa de mensagem
caixa = driver.find_element(By.XPATH, '//div[@title="Mensagem"]')
caixa.click()
caixa.send_keys(MENSAGEM)
caixa.send_keys(Keys.ENTER)

print(f"Mensagem enviada para o grupo '{NOME_GRUPO}': {MENSAGEM}")
time.sleep(5)
driver.quit()
