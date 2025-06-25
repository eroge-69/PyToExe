
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Configurar el navegador
options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
##options.add_argument('--headless')
options.add_argument("--ignore-ssl-errors")
driver = webdriver.Chrome(options=options)

# Abrir la página de inicio de sesión
driver.get("https://cloudp-ui.spamtitan.com/auth/sign-in")

# Ingresar el usuario y contraseña
username = "jrecoba+spamtitan@isco.com.pe"
password = "8kJFy270VN"

try:
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "address"))
    )
    username_field.send_keys(username)
    print("Campo de usuario encontrado y completado.")
except TimeoutException:
    print("Error: No se encontró el campo de usuario en el tiempo esperado.")
    driver.quit()
    exit()

try:
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "passwd"))
    )
    password_field.send_keys(password)
    print("Campo de contraseña encontrado y completado.")
except TimeoutException:
    print("Error: No se encontró el campo de contraseña en el tiempo esperado.")
    driver.quit()
    exit()

try:
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "loginButton"))
    )
    login_button.click()
    print("Se hizo clic en el botón de inicio de sesión.")
except TimeoutException:
    print("Error: No se encontró el botón de inicio de sesión en el tiempo esperado.")
    driver.quit()
    exit()

time.sleep(5)

# Encontrar todos los botones de inicio de sesión utilizando selectores CSS
login_buttons = driver.find_elements(By.CSS_SELECTOR, "input.button[type='submit']")
if len(login_buttons) >= 2:
    second_login_button = login_buttons[1]
    second_login_button.click()
    print("Se hizo clic en el segundo botón de inicio de sesión.")
else:
    print("No se encontraron suficientes botones de inicio de sesión adicionales.")

# Redirigir directamente a la página "history.php"
driver.get("https://cloudp-ui.spamtitan.com/domain/history")

# Verificar que estamos en la página "history.php"
if "history.php" in driver.current_url:
    print("Se ha redirigido correctamente a la página 'history.php'.")
else:
    print("La redirección a la página 'history.php' ha fallado.")

time.sleep(10)

# Configurar el rango de fechas personalizado
try:
    # Obtener las fechas de ayer y hoy
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # Convertir fechas al formato requerido por el sitio web
    start_date = yesterday.strftime("%Y-%m-%d")  # Formato: YYYY-MM-DD
    end_date = today.strftime("%Y-%m-%d")  # Formato: YYYY-MM-DD

    # Localizar los campos de fecha
    start_date_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "startDate"))
    )
    end_date_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "endDate"))
    )

    # Limpiar y establecer las fechas
    start_date_field.clear()
    start_date_field.send_keys(start_date)
    end_date_field.clear()
    end_date_field.send_keys(end_date)

    # Aplicar los filtros
    apply_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "applyfilters"))
    )
    apply_button.click()
    print(f"Rango de fechas configurado: {start_date} a {end_date}")

    time.sleep(5)
except TimeoutException as e:
    print(f"Error al configurar el rango de fechas: {e}")
    driver.quit()
    exit()

# Localizar el elemento <select> para mostrar 500 registros
try:
    select_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "yui-pg-rpp-options"))
    )
    select = Select(select_element)
    select.select_by_value("500")
    print("Se seleccionaron 500 registros por página.")
except TimeoutException:
    print("No se pudo localizar el selector de registros.")

time.sleep(5)

# Exportar el archivo CSV
try:
    export_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "toolbar-tab4"))
    )
    export_button.click()
    print("Se logró hacer clic en el botón 'Export to CSV'.")
    time.sleep(2)
except TimeoutException:
    print("No se pudo encontrar el botón 'Export to CSV'.")

# Cerrar el navegador
driver.quit()
