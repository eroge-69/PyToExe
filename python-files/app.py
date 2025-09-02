import time
import mss
import cv2
import numpy as np
import random
import string
import datetime
import json
from pyzbar.pyzbar import decode, ZBarSymbol
from flask import Flask, jsonify, send_file, send_from_directory, render_template
import os
import threading

# =============================
# Configuración y datos globales
# =============================

DATA_FILE = "qrs.json"
SCREENSHOTS_DIR = "static/screenshots"
STATIC_DIR = "static"

# Lista global con QR detectados
qr_detectados = []

app = Flask(__name__, static_folder=STATIC_DIR, template_folder="templates")

# =============================
# Utilidades
# =============================

def cargar_qrs():
    global qr_detectados
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                qr_detectados = json.load(f)
            except json.JSONDecodeError:
                qr_detectados = []
    else:
        qr_detectados = []

def guardar_qrs():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(qr_detectados, f, indent=4, ensure_ascii=False)

def generar_id():
    return ''.join(random.choices(string.digits, k=8))

# =============================
# Rutas Web
# =============================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/source/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(STATIC_DIR, "css"), filename)

@app.route("/source/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(STATIC_DIR, "js"), filename)

@app.route("/api/qrs", methods=["GET"])
def api_qrs():
    return jsonify(qr_detectados)

@app.route("/api/qrs/<qr_id>/screenshot", methods=["GET"])
def api_screenshot(qr_id):
    path = os.path.join(SCREENSHOTS_DIR, f"{qr_id}.jpg")
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return jsonify({"error": "Captura no encontrada"}), 404

# =============================
# Detección de QR
# =============================

def detectar_qr():
    print("Iniciando detección de QR con OpenCV (multi) | cache por frame + TTL 3min...")
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        detector = cv2.QRCodeDetector()

        last_frame_set = set()        # QR visibles en el frame anterior
        last_event_time = {}          # { contenidoQR: timestamp_ultimo_registro }
        TTL = 180                     # 3 minutos

        while True:
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            ahora = time.time()

            for k, t in list(last_event_time.items()):
                if ahora - t > 7200:
                    last_event_time.pop(k, None)

            try:
                result = detector.detectAndDecodeMulti(img)

                if isinstance(result, tuple) and len(result) == 4:
                    ok, decoded_list, points, _ = result
                else:
                    decoded_list, points, _ = result
                    ok = decoded_list is not None and len(decoded_list) > 0

                if ok:
                    current_set = {d for d in decoded_list if d}

                    appear_new = current_set - last_frame_set

                    refresh_new = {
                        d for d in (current_set & last_frame_set)
                        if (d not in last_event_time) or (ahora - last_event_time[d] >= TTL)
                    }

                    to_register = appear_new | refresh_new

                    for datos in to_register:
                        qr_id = generar_id()
                        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        qr_info = {"date": fecha, "id": qr_id, "content": datos}
                        qr_detectados.append(qr_info)
                        guardar_qrs()

                        cv2.imwrite(
                            os.path.join(SCREENSHOTS_DIR, f"{qr_id}.jpg"),
                            img,
                            [cv2.IMWRITE_JPEG_QUALITY, 70]
                        )

                        print("QR detectado:", qr_info)
                        last_event_time[datos] = ahora

                    last_frame_set = current_set
                    
            except Exception as e:
                print("Error detectando QR:", e)

            time.sleep(0.5)

# =============================
# Main
# =============================

if __name__ == "__main__":
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "css"), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "js"), exist_ok=True)

    cargar_qrs()

    # t = threading.Thread(target=detectar_qr, daemon=True)
    # t.start()

    print("============================================")
    print("   QR Web Tool - Software by NilPM © 2025   ")
    print("============================================")
    print("Servidor web en http://localhost:5000")

    app.run(host="0.0.0.0", port=5000)
