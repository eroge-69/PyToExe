import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Dados simulados da produção
producao = {"pecas_produzidas": 0, "falhas": 0}

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/producao":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(producao).encode())
        elif self.path == "/display":
            html = f"""
            <html><head>
            <meta http-equiv="refresh" content="2">
            <style>body{{font-size:50px;text-align:center;}}</style>
            </head><body>
            <h1>Produção</h1>
            <div>Peças: {producao['pecas_produzidas']}</div>
            <div>Falhas: {producao['falhas']}</div>
            </body></html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path.startswith("/admin"):
            html = """
            <html><body>
            <h1>Atualizar Produção</h1>
            <form method="POST" action="/api/producao">
              Peças: <input name="pecas" type="number"><br>
              Falhas: <input name="falhas" type="number"><br>
              <button type="submit">Enviar</button>
            </form>
            </body></html>
            """
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/producao":
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length).decode()
            params = parse_qs(body)

            if "pecas" in params and "falhas" in params:
                producao["pecas_produzidas"] = int(params["pecas"][0])
                producao["falhas"] = int(params["falhas"][0])

            self.send_response(302)
            self.send_header("Location", "/display")
            self.end_headers()

def run(server_class=HTTPServer, handler_class=MyHandler):
    server = server_class(("0.0.0.0", 5000), handler_class)
    print("Servidor rodando em http://localhost:5000")
    server.serve_forever()

if __name__ == "__main__":
    run()
