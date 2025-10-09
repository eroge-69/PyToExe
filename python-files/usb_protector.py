import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import shutil
import json
from datetime import datetime
import sys

USB_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(USB_ROOT, "config.json")
HISTORY_FILE = os.path.join(USB_ROOT, ".access_history.json")
INIT_FLAG_FILE = os.path.join(USB_ROOT, ".system_initialized")
BACKUP_FOLDER = os.path.join(USB_ROOT, "archivos_importantes")

def load_config():
    default_config = {
        "password": "alpha",
        "email_to": "alexiscastelan735@gmail.com",
        "email_from": "alexiscastelan735@gmail.com",
        "app_password": "vtwikoawhndnkltv",
        "debug": True
    }
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print("⚙️  Archivo de configuración creado: config.json")
        print("⚠️  IMPORTANTE: Edita config.json con tus credenciales antes de usar el sistema")
        print("💡 Puedes usar config.example.json como referencia")
        sys.exit(0)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
PASSWORD = config.get("password", "alpha")
EMAIL_TO = config.get("email_to", "")
EMAIL_FROM = config.get("email_from", "")
APP_PASSWORD = config.get("app_password", "")
DEBUG = config.get("debug", True)

def debug_print(msg):
    if DEBUG:
        print(msg)

def get_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception as e:
        debug_print(f"Error al obtener IP: {e}")
        return "IP no disponible"

def get_geolocation(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,country,countryCode,region,regionName,city,zip,lat,lon,isp,org,as', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'pais': data.get('country', 'Desconocido'),
                    'codigo_pais': data.get('countryCode', 'N/A'),
                    'region': data.get('regionName', 'Desconocido'),
                    'ciudad': data.get('city', 'Desconocido'),
                    'codigo_postal': data.get('zip', 'N/A'),
                    'latitud': data.get('lat', 0),
                    'longitud': data.get('lon', 0),
                    'isp': data.get('isp', 'Desconocido'),
                    'organizacion': data.get('org', 'Desconocido'),
                    'as': data.get('as', 'N/A')
                }
    except Exception as e:
        debug_print(f"Error al obtener geolocalización: {e}")
    
    return {
        'pais': 'Desconocido',
        'codigo_pais': 'N/A',
        'region': 'Desconocido',
        'ciudad': 'Desconocido',
        'codigo_postal': 'N/A',
        'latitud': 0,
        'longitud': 0,
        'isp': 'Desconocido',
        'organizacion': 'Desconocido',
        'as': 'N/A'
    }

def create_backup_zip():
    try:
        if os.path.exists(BACKUP_FOLDER):
            backup_path = os.path.join(USB_ROOT, "respaldo_usb.zip")
            shutil.make_archive(backup_path.replace('.zip', ''), 'zip', BACKUP_FOLDER)
            debug_print(f"Respaldo creado: {backup_path}")
            return backup_path
    except Exception as e:
        debug_print(f"Error al crear respaldo: {e}")
    return None

def send_alert_with_backup(ip, geo_data, include_backup=False):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = '🚨 ALERTA DE SEGURIDAD - USB PROTEGIDO'
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        
        ubicacion_map = f"https://www.google.com/maps?q={geo_data['latitud']},{geo_data['longitud']}"
        
        cuerpo = f"""
        ¡ALERTA! Alguien intentó acceder a tu USB protegido con contraseña incorrecta.
        
        📍 INFORMACIÓN DE UBICACIÓN:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        🌐 Dirección IP: {ip}
        🗺️  País: {geo_data['pais']} ({geo_data['codigo_pais']})
        🏙️  Ciudad: {geo_data['ciudad']}
        📮 Región: {geo_data['region']}
        📫 Código Postal: {geo_data['codigo_postal']}
        
        📡 INFORMACIÓN DE RED:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        🔌 ISP (Proveedor): {geo_data['isp']}
        🏢 Organización: {geo_data['organizacion']}
        🔢 Sistema Autónomo: {geo_data['as']}
        
        🗺️  COORDENADAS GPS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        📍 Latitud: {geo_data['latitud']}
        📍 Longitud: {geo_data['longitud']}
        🗺️  Ver en Google Maps: {ubicacion_map}
        
        ⏰ FECHA Y HORA:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        
        ⚠️  RECOMENDACIONES:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        • Revisa si reconoces esta ubicación
        • Verifica el historial de accesos
        • Considera cambiar tu contraseña
        
        Sistema de Protección USB v2.0
        """
        
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        if include_backup:
            backup_file = create_backup_zip()
            if backup_file and os.path.exists(backup_file):
                with open(backup_file, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(backup_file)}")
                    msg.attach(part)
                debug_print("Respaldo adjuntado al correo")
        
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(EMAIL_FROM, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        debug_print("Correo de alerta enviado con éxito")
        
    except Exception as e:
        debug_print(f"No se pudo enviar el correo: {e}")

def save_access_history(ip, geo_data, password_correct):
    try:
        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        access_record = {
            'fecha_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'ip': ip,
            'pais': geo_data['pais'],
            'ciudad': geo_data['ciudad'],
            'isp': geo_data['isp'],
            'latitud': geo_data['latitud'],
            'longitud': geo_data['longitud'],
            'acceso_exitoso': password_correct
        }
        
        history.append(access_record)
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        os.system(f'attrib +h "{HISTORY_FILE}"' if os.name == 'nt' else f'chflags hidden "{HISTORY_FILE}"')
        debug_print("Acceso registrado en historial")
        
    except Exception as e:
        debug_print(f"Error al guardar historial: {e}")

def auto_replicate():
    try:
        script_name = os.path.basename(__file__)
        script_path = os.path.abspath(__file__)
        
        replica_locations = [
            os.path.join(USB_ROOT, "Documentos", ".system_config.py"),
            os.path.join(USB_ROOT, "Datos", ".backup.py"),
            os.path.join(USB_ROOT, ".security", "config.py")
        ]
        
        for replica_path in replica_locations:
            replica_dir = os.path.dirname(replica_path)
            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)
                if os.name == 'nt':
                    os.system(f'attrib +h "{replica_dir}"')
            
            if not os.path.exists(replica_path):
                shutil.copy2(script_path, replica_path)
                if os.name == 'nt':
                    os.system(f'attrib +h +s "{replica_path}"')
                debug_print(f"Réplica creada: {replica_path}")
        
    except Exception as e:
        debug_print(f"Error en auto-replicación: {e}")

def initialize_system():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        if os.name == 'nt':
            os.system(f'attrib +h "{HISTORY_FILE}"')
        debug_print("Historial inicializado")
    
    if not os.path.exists(INIT_FLAG_FILE):
        with open(INIT_FLAG_FILE, 'w') as f:
            f.write(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        if os.name == 'nt':
            os.system(f'attrib +h "{INIT_FLAG_FILE}"')
        debug_print("Sistema inicializado")

def check_usb_integrity():
    try:
        is_first_run = not os.path.exists(INIT_FLAG_FILE)
        
        if is_first_run:
            initialize_system()
        else:
            if not os.path.exists(HISTORY_FILE):
                debug_print("⚠️  ADVERTENCIA: Historial eliminado - Posible intento de formateo detectado")
                ip = get_ip()
                geo_data = get_geolocation(ip)
                send_alert_with_backup(ip, geo_data, include_backup=True)
                with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                if os.name == 'nt':
                    os.system(f'attrib +h "{HISTORY_FILE}"')
            
    except Exception as e:
        debug_print(f"Error al verificar integridad: {e}")

def main():
    debug_print("=" * 50)
    debug_print("🔒 SISTEMA DE PROTECCIÓN USB AVANZADO v2.0")
    debug_print("=" * 50)
    
    auto_replicate()
    check_usb_integrity()
    
    password = input("\n🔑 Ingresa la contraseña para acceder: ")
    
    ip = get_ip()
    debug_print(f"📡 IP detectada: {ip}")
    
    geo_data = get_geolocation(ip)
    debug_print(f"📍 Ubicación: {geo_data['ciudad']}, {geo_data['pais']}")
    
    if password == PASSWORD:
        debug_print("\n✅ Contraseña correcta. Acceso permitido.")
        debug_print(f"🌍 Ubicación actual: {geo_data['ciudad']}, {geo_data['pais']}")
        save_access_history(ip, geo_data, True)
    else:
        debug_print("\n❌ Contraseña incorrecta. Enviando alerta...")
        save_access_history(ip, geo_data, False)
        send_alert_with_backup(ip, geo_data, include_backup=True)
        debug_print("📧 Alerta enviada con respaldo de archivos")
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
n()
