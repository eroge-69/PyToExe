import http.server
import socketserver
import os
import tempfile
import webbrowser
import time
import sys

HOSTS_LINE = "127.0.0.1 puertasliscanarias.com\n"
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
PORT = 80

HTML_CONTENT = '''<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>XSS Simulado</title></head>
<body>
<h2>Simulación de XSS en puertasliscanarias.com</h2>
<script>
  // Obtenemos parámetro "q" y lo inyectamos sin filtro (XSS)
  const params = new URLSearchParams(window.location.search);
  const q = params.get('q');
  if (q) {
    document.body.innerHTML += "<p>Payload XSS inyectado:</p><pre>" + q + "</pre>";
    eval(q); // Ejecuta el script inyectado
  } else {
    document.body.innerHTML += "<p>No hay payload en parámetro 'q'</p>";
  }
</script>
</body>
</html>'''

def add_hosts_entry():
    with open(HOSTS_PATH, "r") as f:
        lines = f.readlines()
    if HOSTS_LINE in lines:
        print("La entrada ya existe en hosts.")
        return
    with open(HOSTS_PATH, "a") as f:
        f.write(HOSTS_LINE)
    print("Entrada añadida a hosts.")

def start_server(directory):
    os.chdir(directory)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Servidor iniciado en http://puertasliscanarias.com:{PORT}")
        httpd.serve_forever()

def main():
    if os.name != 'nt':
        print("Este script está diseñado para Windows.")
        sys.exit(1)

    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        # Windows fallback
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        print("Este script debe ejecutarse como Administrador (elevado).")
        sys.exit(1)

    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, "test-xss.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"Archivo HTML creado en: {filepath}")

    add_hosts_entry()

    url = "http://puertasliscanarias.com/test-xss.html?q=<script>alert('XSS')</script>"
    time.sleep(1)
    webbrowser.open(url)

    start_server(tmpdir)

if __name__ == "__main__":
    main()
