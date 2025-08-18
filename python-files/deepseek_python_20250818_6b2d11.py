import os
import time
import sys
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuración
STEAM_API_KEY = "BF458874BFE5DEEDD305881F9E99939D"
CAPTURAS_DIR = "capturas"
PROXY_LIST = []
PROXY_ENABLED = False
REPORTE_FILE = "cuentas_con_problemas.txt"

def cargar_proxies():
    global PROXY_LIST, PROXY_ENABLED
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            PROXY_LIST = [line.strip() for line in f if line.strip()]
            PROXY_ENABLED = bool(PROXY_LIST)
        print(f"✅ {len(PROXY_LIST)} proxies cargados")

def cargar_cuentas():
    cuentas = []
    if os.path.exists("cuentas.txt"):
        with open("cuentas.txt", "r") as f:
            for line in f:
                if ":" in line:
                    user, pwd = line.strip().split(":", 1)
                    cuentas.append((user, pwd))
    return cuentas

def crear_carpeta_capturas():
    if not os.path.exists(CAPTURAS_DIR):
        os.makedirs(CAPTURAS_DIR)

def iniciar_driver_con_proxy(proxy=None):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--log-level=3")  # Reducir logs
    
    # Evitar imágenes para mayor velocidad
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    # Configuración para evitar detección
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def resolver_captcha_manual(driver):
    print("\n⚠️ CAPTCHA detectado. Por favor resuélvelo manualmente...")
    print("1. Resuelve el CAPTCHA en el navegador")
    print("2. Presiona Enter aquí cuando hayas terminado")
    
    # Cambiar a modo visible
    driver.minimize_window()
    driver.maximize_window()
    
    input("Presiona Enter para continuar...")
    return True

def verificar_bans_api(steam_id):
    try:
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={STEAM_API_KEY}&steamids={steam_id}"
        response = requests.get(url)
        data = response.json()
        
        if 'players' in data and data['players']:
            player = data['players'][0]
            bans = []
            
            if player.get('VACBanned'):
                bans.append("VAC Ban")
            if player.get('NumberOfGameBans', 0) > 0:
                bans.append("Game Ban")
            if player.get('EconomyBan') != 'none':
                bans.append("Economy Ban")
            if player.get('CommunityBanned'):
                bans.append("Community Ban")
            
            return bans
        
    except Exception as e:
        print(f"Error API: {str(e)}")
    
    return []

def obtener_steam_id64(driver):
    try:
        # Intentar obtener de la URL del perfil
        current_url = driver.current_url
        if "/profiles/" in current_url:
            return current_url.split("/profiles/")[1].split("/")[0]
        
        # Intentar obtener del enlace del perfil
        perfil_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/profiles/']"))
        )
        return perfil_link.get_attribute("href").split("/profiles/")[1].split("/")[0]
    
    except Exception:
        return None

def verificar_cuenta(username, password, proxy=None):
    driver = iniciar_driver_con_proxy(proxy)
    problema_detectado = False
    
    try:
        # Paso 1: Inicio de sesión
        driver.get("https://store.steampowered.com/login/")
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "input_username"))
        ).send_keys(username)
        
        driver.find_element(By.ID, "input_password").send_keys(password)
        driver.find_element(By.ID, "login_btn_signin").click()
        
        # Esperar redirección
        time.sleep(3)
        
        # Verificar errores de inicio de sesión
        if "twofactor" in driver.current_url:
            driver.save_screenshot(f"{CAPTURAS_DIR}/{username}_2fa.png")
            return "2FA"
            
        if "login" in driver.current_url:
            driver.save_screenshot(f"{CAPTURAS_DIR}/{username}_login_error.png")
            return "LOGIN_ERROR"
        
        # Manejar posible CAPTCHA
        if "login" in driver.current_url or "verify" in driver.current_url:
            if resolver_captcha_manual(driver):
                # Verificar nuevamente después de resolver CAPTCHA
                if "login" in driver.current_url or "verify" in driver.current_url:
                    driver.save_screenshot(f"{CAPTURAS_DIR}/{username}_captcha_fail.png")
                    return "CAPTCHA_FAIL"
        
        # Paso 2: Navegar al perfil
        driver.get("https://steamcommunity.com/my")
        time.sleep(2)
        
        # Obtener SteamID64 para la API
        steam_id = obtener_steam_id64(driver)
        
        # Paso 3: Verificar problemas en el perfil
        problemas = []
        
        # Verificar usando API de Steam
        if steam_id:
            api_bans = verificar_bans_api(steam_id)
            if api_bans:
                problemas.extend(api_bans)
        
        # Verificar advertencias en la página
        warning_signs = [
            "Steam Support suspects you account may have been accessed",
            "This account is limited",
            "This profile is private",
            "VAC ban",
            "Trade ban",
            "Community ban",
            "account is locked",
            "suspended",
            "restricted"
        ]
        
        page_text = driver.page_source
        for sign in warning_signs:
            if sign in page_text:
                problemas.append(sign.split('\n')[0][:50] + "...")
                break
        
        # Verificar elementos específicos
        try:
            if driver.find_element(By.CLASS_NAME, "profile_ban_status"):
                problemas.append("Ban visible en perfil")
        except:
            pass
        
        # Si se encontraron problemas, guardar captura
        if problemas:
            driver.save_screenshot(f"{CAPTURAS_DIR}/{username}_problema.png")
            return "PROBLEM"
        
    except Exception as e:
        print(f"Error procesando {username}: {str(e)}")
        driver.save_screenshot(f"{CAPTURAS_DIR}/{username}_error.png")
        return "ERROR"
    
    finally:
        driver.quit()
    
    return None

def main():
    print("Iniciando verificador de cuentas Steam")
    print("======================================")
    
    # Configuración inicial
    cargar_proxies()
    crear_carpeta_capturas()
    cuentas = cargar_cuentas()
    
    if not cuentas:
        print("❌ No se encontraron cuentas en cuentas.txt")
        input("Presiona Enter para salir...")
        return
    
    print(f"🔑 {len(cuentas)} cuentas cargadas para verificación")
    cuentas_con_problemas = []
    
    for idx, (user, pwd) in enumerate(cuentas):
        print(f"\n🔍 Verificando cuenta {idx+1}/{len(cuentas)}: {user}")
        
        # Seleccionar proxy si está habilitado
        proxy = PROXY_LIST[idx % len(PROXY_LIST)] if PROXY_ENABLED and PROXY_LIST else None
        
        resultado = verificar_cuenta(user, pwd, proxy)
        
        if resultado:
            print(f"⚠️ Problema detectado: {resultado}")
            cuentas_con_problemas.append((user, pwd))
        else:
            print("✅ Cuenta sin problemas detectados")
        
        # Esperar entre cuentas para evitar bloqueos
        time.sleep(3)
    
    # Generar reporte final simplificado
    with open(REPORTE_FILE, "w") as reporte:
        for user, pwd in cuentas_con_problemas:
            reporte.write(f"{user}:{pwd}\n")
    
    print("\n" + "=" * 50)
    print(f"Proceso completado. {len(cuentas_con_problemas)} cuentas con problemas")
    print(f"Reporte generado en: {REPORTE_FILE}")
    print(f"Capturas guardadas en: {CAPTURAS_DIR}")
    input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()