from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Siempre devuelve licencia válida
        response = { "status": "ok", "license": "valid" }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        # Si el EA manda POST, igual devolvemos válido
        response = { "status": "ok", "license": "valid" }
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

# Corre en el puerto 80 para simular el servidor original
server = HTTPServer(("0.0.0.0", 8080), MockHandler)
print("Servidor falso corriendo en http://license.myaccount-pow.com ...")
server.serve_forever()
