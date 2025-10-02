import cv2
import numpy as np
import time
import os
import sys
import subprocess
import socket
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from datetime import datetime
import gphoto2 as gp
import qrcode

# =============================================================================
# --- CONFIGURACIÓN PERSONALIZABLE ---
# =============================================================================
NUM_FOTOS = 4
COUNTDOWN_SECONDS = 3
OUTPUT_DIR = "fotomatón_output"
PUERTO_SERVIDOR = 8000

# --- CONFIGURACIÓN DE HARDWARE ---
NOMBRE_IMPRESORA_DNP = "DNP RX1HS" 

# --- ÍNDICES DE LAS CÁMARAS USB (WEBCAM/GOPRO) ---
# Puedes necesitar cambiar estos valores si tienes varios dispositivos USB
INDICE_WEBCAM_CAPTURA = 0     # Índice para una webcam estándar
INDICE_GOPRO_WEB = 1          # Índice para una GoPro en modo webcam

# --- RESOLUCIÓN DE SALIDA DE LAS FOTOS ---
ANCHO_SALIDA = 1200
ALTO_SALIDA = 1800

# --- CONTROL DE TECLAS ---
TECLA_DISPARO = 13 
TECLA_CAMARA = ord('c')       # Tecla 'C' para cambiar de cámara
TECLA_IMPRESION = ord('p')
TECLA_REPETIR = ord('r')
TECLA_NUEVO = ord('n')
TECLA_SALIR = 27 # ESC

# --- ESTILO VISUAL ---
TEXTO_TIRA_FOTOS = "Fotomatón Multi-Cámara\n¡Sonríe!"
TEXTO_QR = "Escanea para descargar tu foto"
FUENTE = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
TAMANO_FUENTE_TEXTO_TIRA = 1.5
GROSOR_FUENTE_TEXTO_TIRA = 2
COLOR_TEXTO_TIRA = (50, 50, 50)
COLOR_FONDO_TIRA = (255, 255, 255)
GROSOR_BORDE_FOTO = 5
COLOR_BORDE_FOTO = (200, 200, 200)
# =============================================================================

# --- VARIABLES GLOBALES ---
local_ip = "127.0.0.1"
server_thread = None
# Variables para manejar las cámaras detectadas
available_cameras = []
selected_camera_index = 0
selected_camera_type = ''
capture_cameras = {} # Diccionario para guardar los objetos de cámara de OpenCV

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def start_server():
    os.chdir(OUTPUT_DIR)
    with TCPServer(("", PUERTO_SERVIDOR), SimpleHTTPRequestHandler) as httpd:
        print(f"🌐 Servidor web iniciado en http://{local_ip}:{PUERTO_SERVIDOR}")
        httpd.serve_forever()

def crear_texto_en_imagen(img, text, pos, font, size, color, thickness):
    lines = text.split('\n')
    y_offset = pos[1]
    for i, line in enumerate(lines):
        text_size = cv2.getTextSize(line, font, size, thickness)[0]
        x = pos[0] + (img.shape[1] - text_size[0]) // 2
        cv2.putText(img, line, (x, y_offset), font, size, color, thickness, cv2.LINE_AA)
        y_offset += text_size[1] + 10

def generar_qr_code(url, size=150):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    qr_img = np.array(img)
    qr_img = cv2.resize(qr_img, (size, size))
    return qr_img

# --- ¡NUEVO! Función para detectar las cámaras conectadas ---
def detectar_camaras():
    """Detecta qué cámaras están disponibles y las inicializa."""
    detected = []
    # 1. Detectar Canon
    try:
        temp_camera = gp.Camera()
        temp_camera.init()
        temp_camera.exit()
        detected.append('canon')
        print("✅ Cámara Canon detectada.")
    except gp.GPhoto2Error:
        print("❌ Cámara Canon no encontrada.")
    
    # 2. Detectar Webcam
    try:
        temp_cam = cv2.VideoCapture(INDICE_WEBCAM_CAPTURA)
        if temp_cam.isOpened():
            detected.append('webcam')
            print(f"✅ Webcam detectada en índice {INDICE_WEBCAM_CAPTURA}.")
        temp_cam.release()
    except Exception:
        print(f"❌ Webcam no encontrada en índice {INDICE_WEBCAM_CAPTURA}.")

    # 3. Detectar GoPro
    try:
        temp_cam = cv2.VideoCapture(INDICE_GOPRO_WEB)
        if temp_cam.isOpened():
            detected.append('gopro')
            print(f"✅ GoPro detectada en índice {INDICE_GOPRO_WEB}.")
        temp_cam.release()
    except Exception:
        print(f"❌ GoPro no encontrada en índice {INDICE_GOPRO_WEB}.")

    return detected

# --- Funciones de Captura (sin cambios) ---
def capturar_foto_canon():
    try:
        camera = gp.Camera()
        camera.init()
        print('Disparando cámara Canon...')
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
        temp_dir = 'temp_fotos'
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        target_path = os.path.join(temp_dir, file_path.name)
        camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(target_path)
        camera.exit()
        img = cv2.imread(target_path)
        if img is not None:
            os.remove(target_path)
            print(f"Redimensionando foto a {ANCHO_SALIDA}x{ALTO_SALIDA} píxeles...")
            img = cv2.resize(img, (ANCHO_SALIDA, ALTO_SALIDA), interpolation=cv2.INTER_AREA)
            return img
        else: return None
    except gp.GPhoto2Error as e:
        print(f"❌ Error al capturar con la cámara Canon: {e}")
        return None

def capturar_foto_cv2(tipo_camara):
    global capture_cameras
    if tipo_camara not in capture_cameras or not capture_cameras[tipo_camara].isOpened():
        print(f"Cámara {tipo_camara} no inicializada.")
        return None
    print(f'Disparando cámara {tipo_camara}...')
    ret, frame = capture_cameras[tipo_camara].read()
    if ret:
        print(f"Redimensionando foto a {ANCHO_SALIDA}x{ALTO_SALIDA} píxeles...")
        img = cv2.resize(frame, (ANCHO_SALIDA, ALTO_SALIDA), interpolation=cv2.INTER_AREA)
        return img
    else:
        print("❌ Error al leer el frame de la cámara.")
        return None

# --- ¡NUEVO! Función de Captura Universal ---
def capturar_foto():
    """Usa la cámara seleccionada actualmente para tomar una foto."""
    if selected_camera_type == 'canon':
        return capturar_foto_canon()
    elif selected_camera_type in ['gopro', 'webcam']:
        return capturar_foto_cv2(selected_camera_type)
    else:
        return None

def imprimir_archivo(ruta_archivo, nombre_impresora):
    try:
        print(f"Enviando a imprimir: {ruta_archivo}")
        if sys.platform == "win32":
            subprocess.run(['powershell', '-Command', f'Start-Process -FilePath "{ruta_archivo}" -PrinterName "{nombre_impresora}" -Verb Print'], check=True)
        elif sys.platform == "darwin":
            subprocess.run(['lp', '-d', nombre_impresora, ruta_archivo], check=True)
        else:
            subprocess.run(['lp', '-d', nombre_impresora, ruta_archivo], check=True)
        print("✅ Trabajo de impresión enviado.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ Error al imprimir: {e}")
        return False

def crear_tira_fotos(fotos, qr_image):
    if not fotos: return None
    h, w, _ = fotos[0].shape
    fotos_con_borde = [cv2.copyMakeBorder(f, GROSOR_BORDE_FOTO, GROSOR_BORDE_FOTO, GROSOR_BORDE_FOTO, GROSOR_BORDE_FOTO, cv2.BORDER_CONSTANT, value=COLOR_BORDE_FOTO) for f in fotos]
    tira_fotos_vertical = np.vstack(fotos_con_borde)
    alto_qr = qr_image.shape[0]
    padding = 20
    alto_panel = alto_qr + padding * 2
    panel_inferior = np.full((alto_panel, tira_fotos_vertical.shape[1], 3), COLOR_FONDO_TIRA, dtype=np.uint8)
    pos_texto = (padding, padding + 40)
    crear_texto_en_imagen(panel_inferior, TEXTO_TIRA_FOTOS, pos_texto, FUENTE, TAMANO_FUENTE_TEXTO_TIRA, COLOR_TEXTO_TIRA, GROSOR_FUENTE_TEXTO_TIRA)
    cv2.putText(panel_inferior, TEXTO_QR, (padding, alto_panel - padding), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_TEXTO_TIRA, 2, cv2.LINE_AA)
    pos_x_qr = panel_inferior.shape[1] - qr_image.shape[1] - padding
    pos_y_qr = (panel_inferior.shape[0] - qr_image.shape[0]) // 2
    panel_inferior[pos_y_qr:pos_y_qr+qr_image.shape[0], pos_x_qr:pos_x_qr+qr_image.shape[1]] = qr_image
    tira_final = np.vstack([tira_fotos_vertical, panel_inferior])
    return tira_final

def main():
    global local_ip, server_thread, available_cameras, selected_camera_index, selected_camera_type, capture_cameras

    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

    # --- Detección e Inicialización de Cámaras ---
    print("Detectando cámaras conectadas...")
    available_cameras = detectar_camaras()
    
    if not available_cameras:
        print("Error: No se encontraron cámaras. Conecta al menos una e intenta de nuevo.")
        input("Presiona Enter para salir.") # Pausa para que el usuario pueda leer el error
        return

    # Inicializar cámaras de OpenCV (Webcam y GoPro)
    if 'webcam' in available_cameras:
        capture_cameras['webcam'] = cv2.VideoCapture(INDICE_WEBCAM_CAPTURA)
    if 'gopro' in available_cameras:
        capture_cameras['gopro'] = cv2.VideoCapture(INDICE_GOPRO_WEB)
        
    # Establecer la primera cámara disponible como la seleccionada
    selected_camera_type = available_cameras[selected_camera_index]
    print(f"Cámara inicial: {selected_camera_type.upper()}")

    local_ip = get_local_ip()
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    preview_cam = cv2.VideoCapture(0) # Usamos la primera cámara para la vista previa
    if not preview_cam.isOpened():
        print("Error: No se pudo abrir la cámara de vista previa.")
        # Liberar cámaras antes de salir
        for cam in capture_cameras.values():
            cam.release()
        return

    cv2.namedWindow('Fotomatón Profesional', cv2.WINDOW_AUTOSIZE)

    while True:
        # --- Pantalla de Inicio con Selección de Cámara ---
        while True:
            ret, frame = preview_cam.read()
            if not ret: continue
            
            # Mostrar cámara actual y disponibles
            texto_camara_actual = f"Cámara ACTUAL: {selected_camera_type.upper()}"
            texto_cambio = "Presiona 'C' para cambiar"
            texto_disponibles = f"Disponibles: {', '.join([c.upper() for c in available_cameras])}"
            
            cv2.putText(frame, texto_camara_actual, (50, 50), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, texto_cambio, (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (200, 200, 200), 2, cv2.LINE_AA)
            cv2.putText(frame, texto_disponibles, (50, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 150), 2, cv2.LINE_AA)
            cv2.putText(frame, "Presiona ENTER para tomar fotos", (50, frame.shape[0] - 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2, cv2.LINE_AA)
            cv2.putText(frame, "Presiona ESC para salir", (50, frame.shape[0] - 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2, cv2.LINE_AA)
            
            cv2.imshow('Fotomatón Profesional', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == TECLA_SALIR:
                preview_cam.release()
                for cam in capture_cameras.values(): cam.release()
                cv2.destroyAllWindows()
                return
            if key == TECLA_CAMARA:
                # Cambiar a la siguiente cámara disponible
                selected_camera_index = (selected_camera_index + 1) % len(available_cameras)
                selected_camera_type = available_cameras[selected_camera_index]
                print(f"--- Cámara cambiada a: {selected_camera_type.upper()} ---")
            if key == TECLA_DISPARO:
                break

        # ... (El resto del código de captura y opciones es igual) ...
        # Aquí iría el bucle de captura de fotos, que usa la función capturar_foto()
        # que ya hemos modificado para usar selected_camera_type
        # Por brevedad, asumo que el resto del código es idéntico al anterior
        # y solo llamo a la función de captura.
        
        # Bucle de captura
        fotos = []
        for i in range(1, NUM_FOTOS + 1):
            for j in range(COUNTDOWN_SECONDS, 0, -1):
                ret, frame = preview_cam.read()
                if not ret: continue
                cv2.circle(frame, (frame.shape[1]//2, frame.shape[0]//2), 80, (255, 255, 255), -1)
                cv2.circle(frame, (frame.shape[1]//2, frame.shape[0]//2), 80, (0, 0, 0), 5)
                cv2.putText(frame, str(j), (frame.shape[1]//2 - 40, frame.shape[0]//2 + 20), cv2.FONT_HERSHEY_TRIPLEX, 3, (0,0,255), 5, cv2.LINE_AA)
                cv2.imshow('Fotomatón Profesional', frame)
                cv2.waitKey(1000)

            foto = capturar_foto()
            if foto is not None:
                fotos.append(foto)
                cv2.imshow('Fotomatón Profesional', foto)
                cv2.waitKey(1000)
            else:
                print("Error al capturar la foto. Abortando secuencia.")
                break
        
        if not fotos: continue

        print("Creando tu tira de fotos...")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"tira_{timestamp}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        url = f"http://{local_ip}:{PUERTO_SERVIDOR}/{filename}"
        print(f"Generando QR para la URL: {url}")
        qr_image = generar_qr_code(url)
        tira_final = crear_tira_fotos(fotos, qr_image)
        
        if tira_final is not None:
            cv2.imwrite(filepath, tira_final)
            print(f"Tira de fotos guardada en: {filepath}")
            img_opciones = tira_final.copy()
            texto_opciones = f"[P] Imprimir  [R] Repetir  [N] Nueva Tira"
            cv2.putText(img_opciones, texto_opciones, (20, img_opciones.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2, cv2.LINE_AA)
            cv2.imshow('Fotomatón Profesional - ¡Listo!', img_opciones)
            
            key = cv2.waitKey(0) & 0xFF
            if key == TECLA_IMPRESION:
                imprimir_archivo(filepath, NOMBRE_IMPRESORA_DNP)
                time.sleep(2)
            elif key == TECLA_REPETIR:
                continue
            elif key == TECLA_NUEVO or key == TECLA_DISPARO:
                continue
            elif key == TECLA_SALIR:
                preview_cam.release()
                for cam in capture_cameras.values(): cam.release()
                cv2.destroyAllWindows()
                return

    # Limpieza final
    preview_cam.release()
    for cam in capture_cameras.values():
        cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()