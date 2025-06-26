import http.server
import socketserver
import re
import http.client


class DuolingoHackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def proxy_request(self):
        if "duolingo.com" not in self.path:
            return

        hacked_path = self.path.replace("hearts=0", "hearts=5")

        headers = {k: v for k, v in self.headers.items()}
        headers["Host"] = "www.duolingo.com"

        try:
            conn = http.client.HTTPSConnection("www.duolingo.com", timeout=10)

            # ФИКС: правильное чтение тела запроса
            body = None
            if self.command == "POST":
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)

            conn.request(self.command, hacked_path, body, headers)  # ФИКС: синтаксис
            response = conn.getresponse()

            content = response.read()
            if b'"hearts":' in content:
                content = re.sub(b'"hearts":\d', b'"hearts":5', content)
                content = re.sub(b'"max_hearts":\d', b'"max_hearts":5', content)

            self.send_response(response.status)
            for header, value in response.getheaders():
                if header.lower() not in ['content-encoding', 'content-length']:
                    self.send_header(header, value)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)

            conn.close()
        except Exception as e:
            print(f"Ошибка прокси: {str(e)}")


def run_proxy():
    PORT = 8080
    with socketserver.TCPServer(("", PORT), DuolingoHackHandler) as httpd:
        print(f"Прокси-сервер запущен на порту {PORT}")
        print("Настройте браузер: HTTP/HTTPS прокси → localhost:8080")
        print("Откройте: https://www.duolingo.com")
        httpd.serve_forever()


if __name__ == "__main__":
    run_proxy()