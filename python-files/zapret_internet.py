#!/usr/bin/env python3
"""
ZapretInternet — simple local proxy GUI (PyQt5)

Features:
- GUI with list of proxied sites (default list prefilled)
- Add site dialog ("Добавить сайт")
- Connect / Disconnect button to start/stop local HTTP proxy
- Saves sites to allowed_sites.json next to the script

WARNING / LIMITATIONS:
- This is a minimal educational proxy. It does NOT bypass national-level censorship or
  sophisticated TLS/HTTPS blocking. For HTTPS it supports simple CONNECT tunneling.
- It may not handle all edge cases, websockets, or advanced headers.

Dependencies:
- Python 3.8+
- PyQt5 (pip install pyqt5)
- requests (pip install requests)

Run: python ZapretInternet.py

"""

import sys
import os
import json
import threading
import socket
import socketserver
import select
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit
import requests

from PyQt5 import QtWidgets, QtCore

DEFAULT_SITES = [
    "discord.gifts",
    "discord.gg",
    "discord.media",
    "discord.new",
    "discord.store",
    "discord.status",
    "discord-activities.com",
    "discordactivities.com",
    "discordapp.com",
    "discordapp.net",
    "discordcdn.com",
    "discordmerch.com",
    "discordpartygames.com",
    "discordsays.com",
    "discordsez.com",
    "yt3.ggpht.com",
    "yt4.ggpht.com",
    "yt3.googleusercontent.com",
    "googlevideo.com",
    "jnn-pa.googleapis.com",
    "stable.dl2.discordapp.net",
    "wide-youtube.l.google.com",
    "youtube-nocookie.com",
    "youtube-ui.l.google.com",
    "youtube.com",
    "youtubeembeddedplayer.googleapis.com",
    "youtubekids.com",
    "youtubei.googleapis.com",
    "youtu.be",
    "yt-video-upload.l.google.com",
    "ytimg.com",
    "ytimg.l.google.com",
    "frankerfacez.com",
    "ffzap.com",
    "betterttv.net",
    "7tv.app",
    "7tv.io",
    "chatgpt.com",
    "chat.openai.com",
    "searchgpt.com",
]

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "allowed_sites.json")
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 8888


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class ProxyRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _is_allowed(self, host):
        # Access allowed_sites via server attribute
        allowed = self.server.allowed_sites
        host_only = host.split(":")[0].lower()
        return any(host_only == a.lower() or host_only.endswith("." + a.lower()) for a in allowed)

    def do_CONNECT(self):
        # HTTPS tunneling
        host_port = self.path
        host, sep, port = host_port.partition(":")
        port = int(port) if sep else 443
        if not self._is_allowed(host):
            self.send_error(403, "Host not allowed by ZapretInternet")
            return
        try:
            remote = socket.create_connection((host, port), timeout=10)
        except Exception as e:
            self.send_error(502, "Cannot connect to %s: %s" % (host_port, e))
            return
        self.send_response(200, "Connection Established")
        self.end_headers()
        # Tunnel data
        self.connection.setblocking(False)
        remote.setblocking(False)
        sockets = [self.connection, remote]
        try:
            while True:
                r, w, x = select.select(sockets, [], sockets, 0.5)
                if x:
                    break
                for s in r:
                    data = None
                    try:
                        data = s.recv(8192)
                    except Exception:
                        data = None
                    if not data:
                        raise Exception("no data")
                    if s is self.connection:
                        remote.sendall(data)
                    else:
                        self.connection.sendall(data)
        except Exception:
            pass
        try:
            remote.close()
        except Exception:
            pass

    def _proxy_request(self):
        # For HTTP methods like GET/POST
        url = self.path
        # If path is absolute URI, ok. If relative, build from Host header
        if not url.startswith("http://") and not url.startswith("https://"):
            host = self.headers.get("Host")
            scheme = "http"
            url = f"{scheme}://{host}{url}"
        parts = urlsplit(url)
        host = parts.hostname
        if not self._is_allowed(host):
            self.send_error(403, "Host not allowed by ZapretInternet")
            return

        method = self.command
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'proxy-connection'}
        # Remove hop-by-hop headers
        for h in ['Connection', 'Keep-Alive', 'Proxy-Authenticate', 'Proxy-Authorization', 'TE', 'Trailers', 'Transfer-Encoding', 'Upgrade']:
            headers.pop(h, None)
        try:
            data = None
            if 'Content-Length' in self.headers:
                length = int(self.headers.get('Content-Length'))
                data = self.rfile.read(length)
            resp = requests.request(method, url, headers=headers, data=data, stream=True, timeout=15, allow_redirects=False)
        except Exception as e:
            self.send_error(502, f"Bad gateway: {e}")
            return

        self.send_response(resp.status_code)
        # Copy response headers
        excluded = ['Content-Encoding', 'Transfer-Encoding', 'Connection', 'Keep-Alive']
        for k, v in resp.headers.items():
            if k not in excluded:
                self.send_header(k, v)
        # Always set connection close to avoid complicated keep-alive handling
        self.send_header('Connection', 'close')
        self.end_headers()
        try:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
            self.wfile.flush()
        except Exception:
            pass

    def do_GET(self):
        self._proxy_request()

    def do_POST(self):
        self._proxy_request()

    def do_PUT(self):
        self._proxy_request()

    def do_DELETE(self):
        self._proxy_request()

    def log_message(self, format, *args):
        # Silence or route to server log
        self.server.log(format % args)


class ProxyServerThread(threading.Thread):
    def __init__(self, host, port, allowed_sites, log_callback=None):
        super().__init__(daemon=True)
        self._host = host
        self._port = port
        self._allowed_sites = allowed_sites
        self._httpd = None
        self._log = log_callback or (lambda *a, **k: None)

    def run(self):
        try:
            with ThreadedTCPServer((self._host, self._port), ProxyRequestHandler) as httpd:
                httpd.allowed_sites = self._allowed_sites
                httpd.log = self._log
                self._httpd = httpd
                self._log(f"Proxy running on {self._host}:{self._port}")
                httpd.serve_forever()
        except Exception as e:
            self._log(f"Proxy stopped with error: {e}")

    def stop(self):
        if self._httpd:
            try:
                self._httpd.shutdown()
                self._httpd.server_close()
            except Exception:
                pass
            self._log("Proxy stopped")


# -------------------- GUI --------------------

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZapretInternet")
        self.resize(660, 420)
        layout = QtWidgets.QVBoxLayout(self)

        header = QtWidgets.QLabel("<h2>ZapretInternet — локальный прокси</h2>")
        layout.addWidget(header)

        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Добавить сайт")
        self.remove_btn = QtWidgets.QPushButton("Удалить выбранный")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        self.connect_btn = QtWidgets.QPushButton("Подключить")
        self.connect_btn.setCheckable(True)
        layout.addWidget(self.connect_btn)

        self.status_label = QtWidgets.QLabel("Отключен")
        layout.addWidget(self.status_label)

        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        # Data
        self.allowed_sites = []
        self.proxy_thread = None

        # Signals
        self.add_btn.clicked.connect(self.on_add)
        self.remove_btn.clicked.connect(self.on_remove)
        self.connect_btn.toggled.connect(self.on_toggle_connect)

        self.load_sites()
        self.refresh_list()

    def log(self, msg):
        def append():
            self.log_output.append(msg)
        QtCore.QMetaObject.invokeMethod(self, append, QtCore.Qt.QueuedConnection)

    def load_sites(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.allowed_sites = data
            except Exception:
                self.allowed_sites = DEFAULT_SITES.copy()
        else:
            self.allowed_sites = DEFAULT_SITES.copy()
            self.save_sites()

    def save_sites(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.allowed_sites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"Error saving config: {e}")

    def refresh_list(self):
        self.list_widget.clear()
        for s in self.allowed_sites:
            self.list_widget.addItem(s)

    def on_add(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Добавить сайт", "Адрес сайта (например: example.com):")
        if ok:
            site = text.strip()
            if site:
                # sanitize: remove protocol and slashes
                site = site.replace('http://', '').replace('https://', '').split('/')[0]
                if site not in self.allowed_sites:
                    self.allowed_sites.append(site)
                    self.save_sites()
                    self.refresh_list()
                    self.log(f"Добавлен сайт: {site}")
                else:
                    QtWidgets.QMessageBox.information(self, "Инфо", "Сайт уже в списке")

    def on_remove(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        for it in items:
            text = it.text()
            if text in self.allowed_sites:
                self.allowed_sites.remove(text)
        self.save_sites()
        self.refresh_list()
        self.log("Удалены выбранные сайты")

    def on_toggle_connect(self, checked):
        if checked:
            # start proxy
            self.connect_btn.setText("Отключить")
            self.status_label.setText(f"Подключение... (локальный прокси {PROXY_HOST}:{PROXY_PORT})")
            self.proxy_thread = ProxyServerThread(PROXY_HOST, PROXY_PORT, self.allowed_sites, log_callback=self.log)
            self.proxy_thread.start()
            self.status_label.setText(f"Подключено (локальный прокси {PROXY_HOST}:{PROXY_PORT})")
            self.log(f"Proxy started on {PROXY_HOST}:{PROXY_PORT}")
        else:
            # stop proxy
            self.connect_btn.setText("Подключить")
            self.status_label.setText("Отключен")
            if self.proxy_thread:
                try:
                    self.proxy_thread.stop()
                except Exception:
                    pass
                self.proxy_thread = None
            self.log("Proxy stopped by user")


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    QtWidgets.QMessageBox.information(w, "Инструкция", f"Запуск локального прокси на {PROXY_HOST}:{PROXY_PORT}.\n\n\nЧтобы использовать: в браузере или системе укажите HTTP proxy {PROXY_HOST}:{PROXY_PORT} (или для HTTPS — тот же хост/порт, браузер использует CONNECT).\n\nВажно: этот локальный прокси пропускает только сайты из списка. Другие хосты будут блокироваться.")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
