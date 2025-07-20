import socketserver
import http.server

LISTEN_IP = '192.168.137.1'
LISTEN_PORT = 8888

UPSTREAM_PROXY = '127.0.0.1'
UPSTREAM_PORT = 10809

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_CONNECT(self):
        self.send_response(200, 'Connection Established')
        self.end_headers()

        conn = socketserver.socket(socketserver.AF_INET, socketserver.SOCK_STREAM)
        conn.connect((UPSTREAM_PROXY, UPSTREAM_PORT))

        self.connection.setblocking(0)
        conn.setblocking(0)

        while True:
            try:
                data = self.connection.recv(8192)
                if data:
                    conn.sendall(data)
            except:
                pass
            try:
                data = conn.recv(8192)
                if data:
                    self.connection.sendall(data)
            except:
                pass

httpd = socketserver.ThreadingTCPServer((LISTEN_IP, LISTEN_PORT), ProxyHandler)
print(f"Serving HTTPS proxy bridge on {LISTEN_IP}:{LISTEN_PORT} -> {UPSTREAM_PROXY}:{UPSTREAM_PORT}")
httpd.serve_forever()