from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib
import os
from pathlib import Path
import base64

# ---- CONFIG ----
FILE_PATH = r"C:\Users\Administrator\AppData\Roaming\MetaQuotes\Terminal\Common\Files\control.txt"
HOST = "0.0.0.0"
PORT = 5000
USERNAME = "admin"       # 👈 cámbialo
PASSWORD = "miClave123"  # 👈 cámbiala
# ----------------

def ensure_dir_and_file(path: str):
    p = Path(path)
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("ON", encoding="utf-8")

class ControlHandler(BaseHTTPRequestHandler):
    def _auth_required(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Control EA"')
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Autenticacion requerida")
    
    def _check_auth(self):
        auth_header = self.headers.get("Authorization")
        if auth_header is None:
            return False
        try:
            auth_type, encoded = auth_header.split(" ")
            if auth_type != "Basic":
                return False
            decoded = base64.b64decode(encoded).decode("utf-8")
            user, pw = decoded.split(":", 1)
            return (user == USERNAME and pw == PASSWORD)
        except Exception:
            return False

    def _set_headers(self, content_type="text/html"):
        self.send_response(200)
        self.send_header("Content-type", content_type + "; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        if not self._check_auth():
            self._auth_required()
            return

        parsed = urllib.parse.urlparse(self.path)
        route = parsed.path.lower()
        if route == "/" or route == "/index":
            self._set_headers("text/html")
            status = self._read_status()
            html = f"""
            <html>
            <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
            <body style="font-family:Arial; text-align:center; padding:20px;">
              <h2>Control EA</h2>
              <p>Estado actual: <strong style="color: {'green' if status=='ON' else 'red'}">{status}</strong></p>
              <div style="margin:20px;">
                <a href='/on'><button style='background:green;color:white;font-size:18px;padding:12px 18px;margin:8px;border-radius:8px;border:none'>Encender EA</button></a>
                <a href='/off'><button style='background:red;color:white;font-size:18px;padding:12px 18px;margin:8px;border-radius:8px;border:none'>Apagar EA</button></a>
              </div>
              <p><a href="/status">Ver estado (texto)</a></p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            return
        elif route == "/on":
            self._write_status("ON")
            self._set_headers("text/html")
            self.wfile.write(b"<h2 style='color:green'>✅ EA ACTIVADO</h2><a href='/'>Volver</a>")
            return
        elif route == "/off":
            self._write_status("OFF")
            self._set_headers("text/html")
            self.wfile.write(b"<h2 style='color:red'>❌ EA APAGADO</h2><a href='/'>Volver</a>")
            return
        elif route == "/status":
            self._set_headers("text/plain")
            status = self._read_status()
            self.wfile.write(status.encode("utf-8"))
            return
        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):
        return

    def _read_status(self):
        try:
            if not os.path.exists(FILE_PATH):
                ensure_dir_and_file(FILE_PATH)
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                txt = f.read().strip().upper()
                return "ON" if txt != "OFF" else "OFF"
        except Exception:
            return "ON"

    def _write_status(self, status):
        try:
            ensure_dir_and_file(FILE_PATH)
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                f.write(status.upper())
        except Exception as e:
            print("Error:", e)

def run_server():
    ensure_dir_and_file(FILE_PATH)
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, ControlHandler)
    print(f"Servidor en http://{HOST}:{PORT}/ (archivo: {FILE_PATH})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()
