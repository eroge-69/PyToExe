
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

class ProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def proxy_request(self):
        try:
            url = f"http://localhost:11434{self.path}"
            data = self.rfile.read(int(self.headers.get('Content-Length', 0))) if self.command == 'POST' else None
            headers = {key: val for key, val in self.headers.items()}
            method = getattr(requests, self.command.lower())
            resp = method(url, headers=headers, data=data)

            self.send_response(resp.status_code)
            self.send_header('Access-Control-Allow-Origin', '*')
            for key, value in resp.headers.items():
                if key.lower() != 'content-encoding':
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(resp.content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

if __name__ == '__main__':
    port = 3000
    print(f"Proxy läuft auf http://localhost:{port}")
    server = HTTPServer(('localhost', port), ProxyHandler)
    server.serve_forever()
