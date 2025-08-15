import http.server
import ssl
import os
import shutil

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # serve index.html for root
        if self.path == "/":
            self.path = "/index.html"

        # normalize request path (remove query/hash)
        req_path = self.path.split('?',1)[0].split('#',1)[0]
        accept_encoding = self.headers.get('Accept-Encoding', '')

        # translate to local filesystem path using built-in helper
        fs_path = self.translate_path(req_path)

        # If client explicitly requested a .br file -> serve it with Content-Encoding: br
        if req_path.endswith('.br') and os.path.exists(fs_path):
            orig_path = req_path[:-3]  # used to detect Content-Type
            ctype = self.guess_type(orig_path)
            try:
                f = open(fs_path, 'rb')
            except OSError:
                return super().do_GET()
            try:
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Encoding", "br")
                self.send_header("Vary", "Accept-Encoding")
                fs = os.fstat(f.fileno())
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
            finally:
                f.close()
            return

        # If client accepts brotli and precompressed .br exists -> serve that with Content-Encoding: br
        if 'br' in accept_encoding and os.path.exists(fs_path + '.br'):
            br_fs_path = fs_path + '.br'
            ctype = self.guess_type(req_path)
            try:
                f = open(br_fs_path, 'rb')
            except OSError:
                return super().do_GET()
            try:
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Encoding", "br")
                self.send_header("Vary", "Accept-Encoding")
                fs = os.fstat(f.fileno())
                self.send_header("Content-Length", str(fs.st_size))
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
            finally:
                f.close()
            return

        # otherwise fall back to default behavior
        return super().do_GET()

host = "localhost"
port = 8080

httpd = http.server.HTTPServer((host, port), MyHandler)
# SSL: key.pem и cert.pem должны быть в той же папке
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="key.pem", certfile="cert.pem", server_side=True)

print(f"HTTPS сервер запущен на https://{host}:{port}")
print("Файлы в текущей папке:", os.listdir("."))
httpd.serve_forever()
