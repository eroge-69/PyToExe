import os
import time
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

# === Configuración de CapMonster ===
API_KEY_CAPMONSTER = 'c96a2d2d3c33deba13c079e3de96fe96'  # clave API CapMonster c96a2d2d3c33deba13c079e3de96fe96

def resolver_captcha_capmonster(image_bytes):
    import base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    data = {
        'clientKey': API_KEY_CAPMONSTER,
        'task': {
            'type': 'ImageToTextTask',
            'body': image_base64
        }
    }
    response = requests.post('https://api.capmonster.cloud/createTask', json=data)
    if response.json().get('errorId') != 0:
        raise Exception(f"Error al enviar CAPTCHA a CapMonster: {response.json().get('errorDescription')}")
    task_id = response.json().get('taskId')

    for _ in range(20):
        time.sleep(5)
        res = requests.post('https://api.capmonster.cloud/getTaskResult', json={
            'clientKey': API_KEY_CAPMONSTER,
            'taskId': task_id
        })
        result = res.json()
        if result.get('status') == 'processing':
            continue
        if result.get('status') == 'ready':
            return result['solution']['text']
        else:
            raise Exception(f"Error al obtener resultado de CapMonster: {result.get('errorDescription')}")
    raise TimeoutError("Tiempo de espera agotado para resolver el CAPTCHA")

# === Validar archivo Excel ===
excel_file = 'entrada.xlsx'
if not os.path.exists(excel_file):
    raise FileNotFoundError(f"El archivo {excel_file} no existe.")
df = pd.read_excel(excel_file)
if 'CUIL' not in df.columns or 'DNI' not in df.columns:
    raise ValueError("El archivo Excel debe contener las columnas 'CUIL' y 'DNI'.")

# === Configuración de Edge con Selenium Stealth ===
edge_path = 'msedgedriver.exe'
service = Service(edge_path)
options = Options()
options.use_chromium = True
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

# === Lista para guardar resultados ===
resultados = []

# === URL objetivo ===
url = 'https://www.sssalud.gob.ar/index.php?user=GRAL&page=bus650'

# === Navegador con Selenium Stealth ===
with webdriver.Edge(service=service, options=options) as driver:
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32",
            webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

    for index, row in df.iterrows():
        cuil = str(row['CUIL'])
        dni = str(row['DNI'])
        print(f'\nProcesando CUIL: {cuil}, DNI: {dni}')
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'cuil')))
            driver.find_element(By.NAME, 'cuil').send_keys(cuil)
            driver.find_element(By.NAME, 'nro_doc').send_keys(dni)

            # === Capturar imagen CAPTCHA ===
            captcha_element = driver.find_element(By.ID, 'captcha')
            captcha_url = captcha_element.get_attribute('src')
            response = requests.get(captcha_url)
            image_bytes = BytesIO(response.content).getvalue()

            # === Resolver CAPTCHA con CapMonster ===
            captcha_text = resolver_captcha_capmonster(image_bytes)
            print(f"Captcha resuelto: {captcha_text}")

            # === Ingresar CAPTCHA resuelto ===
            driver.find_element(By.NAME, 'captcha').send_keys(captcha_text)
            driver.find_element(By.NAME, 'btsend').click()

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'resultado')))
            tabla = driver.find_element(By.CLASS_NAME, 'resultado')
            texto = tabla.text
            cuil_result = ''
            codigo_os = ''
            for linea in texto.split('\n'):
                if 'CUIL' in linea:
                    cuil_result = linea.split(':')[-1].strip()
                elif 'CÓDIGO' in linea or 'Codigo' in linea:
                    codigo_os = linea.split(':')[-1].strip()
            resultados.append({
                'CUIL': cuil,
                'DNI': dni,
                'CUIL Encontrado': cuil_result,
                'Código Obra Social': codigo_os
            })
        except Exception as e:
            print(f"❌ Error en CUIL {cuil}: {e}")
            resultados.append({
                'CUIL': cuil,
                'DNI': dni,
                'CUIL Encontrado': '',
                'Código Obra Social': '',
                'Error': str(e)
            })

# === Guardar resultados en Excel ===
df_resultado = pd.DataFrame(resultados)
df_resultado.to_excel('salida_capmonster.xlsx', index=False)
print("\n✅ Proceso completado. Resultados guardados en salida_capmonster.xlsx")
