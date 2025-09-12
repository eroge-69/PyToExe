import sys
import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QFileDialog, QProgressBar, QLabel, QCheckBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
import re
import time

TIMEOUT = 30
MAX_CONCURRENT = 200
CHECK_URL = "http://httpbin.org/ip"
SLOW_THRESHOLD = 25

# Проверка формата прокси
def is_valid_proxy(proxy):
    pattern = re.compile(r'^(\d{1,3}(\.\d{1,3}){3}):(\d+)$')
    return bool(pattern.match(proxy))

# Проверка одной прокси с протоколом
async def check_socks_proxy(proxy, proto):
    connector = ProxyConnector.from_url(f"{proto}://{proxy}")
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    start = time.time()
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(CHECK_URL) as resp:
                if resp.status == 200:
                    elapsed = time.time() - start
                    return True, elapsed
    except:
        return False, None
    return False, None

# Проверка прокси с авто-перепроверкой медленных
async def check_proxy(proxy, proto):
    ok, elapsed = await check_socks_proxy(proxy, proto)
    if ok and elapsed <= SLOW_THRESHOLD:
        return proxy, proto.upper(), "WORKING", elapsed
    elif ok and elapsed > SLOW_THRESHOLD:
        ok2, elapsed2 = await check_socks_proxy(proxy, proto)
        if ok2 and elapsed2 <= SLOW_THRESHOLD:
            return proxy, proto.upper(), "WORKING", elapsed2
        else:
            return proxy, proto.upper(), "DEAD", max(elapsed, elapsed2 if elapsed2 else 0)
    return proxy, proto.upper(), "DEAD", None

# --- GUI ---
class ProxyValidatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SOCKS Proxy Validator")
        self.setGeometry(300, 300, 800, 550)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Лог с белым фоном и синими акцентами ---
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #f0f8ff; color: #000000; font-family: Consolas;")
        self.layout.addWidget(self.log)

        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #0078d7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                width: 1px;
            }
        """)
        self.layout.addWidget(self.progress)

        # --- Чекбоксы SOCKS4/SOCKS5 (только один активен) ---
        proto_layout = QHBoxLayout()
        proto_layout.addWidget(QLabel("Select Protocol:"))
        self.cb_socks4 = QCheckBox("SOCKS4")
        self.cb_socks5 = QCheckBox("SOCKS5")
        self.cb_socks4.stateChanged.connect(self.only_one_checked)
        self.cb_socks5.stateChanged.connect(self.only_one_checked)
        proto_layout.addWidget(self.cb_socks4)
        proto_layout.addWidget(self.cb_socks5)
        self.layout.addLayout(proto_layout)

        # --- Кнопки загрузки и старта ---
        self.load_btn = QPushButton("Load Proxy List")
        self.load_btn.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold;")
        self.load_btn.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_btn)

        self.start_btn = QPushButton("Start Checking")
        self.start_btn.setStyleSheet("background-color: #005a9e; color: white; font-weight: bold;")
        self.start_btn.clicked.connect(self.start_checking)
        self.layout.addWidget(self.start_btn)

        self.proxies = []

    # --- Логика чекбоксов ---
    def only_one_checked(self, state):
        sender = self.sender()
        if sender == self.cb_socks4 and state == Qt.CheckState.Checked.value:
            self.cb_socks5.setChecked(False)
        elif sender == self.cb_socks5 and state == Qt.CheckState.Checked.value:
            self.cb_socks4.setChecked(False)

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Proxy List", "", "Text Files (*.txt)"
        )
        if file_name:
            with open(file_name, "r") as f:
                self.proxies = [line.strip() for line in f if is_valid_proxy(line.strip())]
            self.log.append(f"Loaded {len(self.proxies)} valid proxies.")

    def start_checking(self):
        if not self.proxies:
            self.log.append("No proxies loaded!")
            return
        if self.cb_socks4.isChecked():
            proto = "socks4"
        elif self.cb_socks5.isChecked():
            proto = "socks5"
        else:
            self.log.append("No protocol selected!")
            return
        asyncio.run(self.run_checks(proto))

    async def run_checks(self, proto):
        self.progress.setMaximum(len(self.proxies))
        self.log.append("Starting proxy checking...")
        QApplication.processEvents()

        semaphore = asyncio.Semaphore(MAX_CONCURRENT)

        async def sem_task(proxy):
            async with semaphore:
                return await check_proxy(proxy, proto)

        tasks = [asyncio.create_task(sem_task(p)) for p in self.proxies]

        for idx, task in enumerate(asyncio.as_completed(tasks)):
            proxy, proto_res, status, elapsed = await task
            elapsed_str = f"{elapsed:.2f}s" if elapsed else "-"

            # Цветной лог
            if status == "WORKING":
                color = "green"
                fname = f"{proto_res}.txt"
                with open(fname, "a") as f:
                    f.write(proxy + "\n")
            else:
                color = "red"

            self.log.append(f'<span style="color:{color}">{proxy} | {proto_res} | {status} | {elapsed_str}</span>')
            self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())
            QApplication.processEvents()

            self.progress.setValue(idx + 1)

        self.log.append("Checking finished. Files saved.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProxyValidatorGUI()
    window.show()
    sys.exit(app.exec())
