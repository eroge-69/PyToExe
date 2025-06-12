import http.server
import socketserver
import os

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

os.chdir('www')
PORT = 8080
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Server läuft auf http://localhost:{PORT}")
    httpd.serve_forever()
