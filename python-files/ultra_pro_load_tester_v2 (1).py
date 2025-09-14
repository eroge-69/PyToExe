# Ultra Pro Load Tester Extreme v8.1 - Avancerad version
from __future__ import annotations
import sys, asyncio, traceback, time, subprocess, contextlib
from dataclasses import dataclass
from typing import List

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt, pyqtSignal, QObject

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

import httpx

print("Ultra Pro Load Tester Extreme v8.1 starting...")

# ----------------------------- Stats -----------------------------
@dataclass
class UrlStats:
    url: str
    total: int = 0
    success: int = 0
    failure: int = 0

    def update(self, ok: bool):
        self.total += 1
        if ok:
            self.success += 1
        else:
            self.failure += 1

# ----------------------------- Stock/Indicator Canvas -----------------------------
class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(8,4), tight_layout=True)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Request Index")
        self.ax.set_ylabel("Current Level")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_ylim(0, 1000)
        self.line, = self.ax.plot([0], [0], color='green', lw=2)
        self.level = 0

    def update_level(self, delta: int):
        self.level += delta
        if self.level < 0:
            self.level = 0
        ydata = list(self.line.get_ydata()) + [self.level]
        xdata = list(range(len(ydata)))
        self.line.set_xdata(xdata)
        self.line.set_ydata(ydata)
        self.ax.relim()
        self.ax.autoscale_view(scalex=True, scaley=True)
        self.draw_idle()

# ----------------------------- Locust Helper -----------------------------
def start_locust_auto(urls: list, user_count: int = 100, spawn_rate: int = 10):
    locust_code = """
from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def index(self):
        self.client.get("/")
"""
    with open("locustfile.py", "w") as f:
        f.write(locust_code)

    process = subprocess.Popen(["locust", "-f", "locustfile.py", "-H", urls[0]])
    time.sleep(3)  # Vänta på Locust-webbservern

    for url in urls:
        try:
            with httpx.Client() as client:
                client.post(
                    "http://localhost:8089/swarm",
                    data={
                        "user_count": str(user_count),
                        "spawn_rate": str(spawn_rate),
                        "host": url
                    }
                )
        except Exception as e:
            print(f"Misslyckades att starta Locust för {url}: {e}")
    return process
# ----------------------------- LoadWorker -----------------------------
class LoadWorker(QObject):
    statsUpdate = pyqtSignal(int)
    logLine = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, targets: List[str], total_per_url: int, concurrency: int, timeout_s: float, batch_size: int = 50):
        super().__init__()
        self.targets = targets
        self.total_per_url = total_per_url
        self.concurrency = concurrency
        self.timeout_s = timeout_s
        self.batch_size = batch_size
        self._stop = asyncio.Event()

    @QtCore.pyqtSlot()
    def stop(self):
        self._stop.set()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            asyncio.run(self._run_async())
        except Exception as e:
            self.logLine.emit(f"Worker ERROR: {e!r}\n{traceback.format_exc()}")
        finally:
            self.finished.emit()

    async def _run_async(self):
        limits = httpx.Limits(max_keepalive_connections=self.concurrency, max_connections=self.concurrency*2)
        timeout = httpx.Timeout(self.timeout_s)
        async with httpx.AsyncClient(http2=False, limits=limits, timeout=timeout) as client:
            sem = asyncio.Semaphore(self.concurrency)

            async def fetch_batch(url: str, batch_count: int):
                delta = 0
                for _ in range(batch_count):
                    if self._stop.is_set(): break
                    ok = False
                    try:
                        resp = await client.get(url)
                        ok = 200 <= resp.status_code < 400
                        if resp.status_code == 429:
                            await asyncio.sleep(0.1)
                    except Exception as e:
                        self.logLine.emit(f"Request ERROR {url}: {type(e).__name__}")
                        ok = False
                    delta += 1 if ok else -1
                if delta != 0:
                    self.statsUpdate.emit(delta)

            async def process_url(url: str):
                for i in range(0, self.total_per_url, self.batch_size):
                    await fetch_batch(url, min(self.batch_size, self.total_per_url - i))

            hb = asyncio.create_task(self.heartbeat())
            try:
                await asyncio.gather(*(process_url(u) for u in self.targets))
            finally:
                hb.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await hb

    async def heartbeat(self):
        try:
            while not self._stop.is_set():
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            return
# ----------------------------- MainWindow -----------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultra Pro Load Tester Extreme v8.1")
        self.resize(1500,950)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main = QtWidgets.QVBoxLayout(central)

        # Canvas
        self.canvas = MplCanvas()
        main.addWidget(self.canvas, 3)

        # Controls
        self.controls = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.controls)
        self.url_input = QtWidgets.QLineEdit(); layout.addRow("URLs (komma-separerade):", self.url_input)
        self.total_input = QtWidgets.QSpinBox(); self.total_input.setMaximum(1000000); self.total_input.setValue(200); layout.addRow("Total per URL:", self.total_input)
        self.conc_input = QtWidgets.QSpinBox(); self.conc_input.setMaximum(1000); self.conc_input.setValue(50); layout.addRow("Concurrency:", self.conc_input)
        self.locust_users_input = QtWidgets.QSpinBox(); self.locust_users_input.setMaximum(10000); self.locust_users_input.setValue(500); layout.addRow("Locust Users:", self.locust_users_input)
        self.start_btn = QtWidgets.QPushButton("Start Test"); layout.addRow(self.start_btn)
        self.stop_btn = QtWidgets.QPushButton("Stop Test"); layout.addRow(self.stop_btn)
        self.locust_btn = QtWidgets.QPushButton("Start Locust Auto"); layout.addRow(self.locust_btn)
        self.stop_locust_btn = QtWidgets.QPushButton("Stop Locust"); layout.addRow(self.stop_locust_btn)

        dock = QtWidgets.QDockWidget("Controls", self)
        dock.setWidget(self.controls)
        dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        # Log
        self.log_widget = QtWidgets.QPlainTextEdit(); self.log_widget.setReadOnly(True)
        logdock = QtWidgets.QDockWidget("Log", self); logdock.setWidget(self.log_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, logdock)

        # State
        self.worker = None
        self.thread = None
        self.locust_process = None

        # Signals
        self.start_btn.clicked.connect(self.start_test)
        self.stop_btn.clicked.connect(self.stop_test)
        self.locust_btn.clicked.connect(self.start_locust)
        self.stop_locust_btn.clicked.connect(self.stop_locust)

    # ---------------- Test ----------------
    def start_test(self):
        urls = [u.strip() for u in self.url_input.text().split(',') if u.strip()]
        if not urls:
            self.log_widget.appendPlainText("Ingen URL angiven!")
            return
        total = self.total_input.value()
        conc = self.conc_input.value()
        self.worker = LoadWorker(urls, total, conc, timeout_s=10.0)
        self.worker.statsUpdate.connect(self.canvas.update_level)
        self.worker.logLine.connect(lambda line: self.log_widget.appendPlainText(line))
        self.thread = QtCore.QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(lambda: self.log_widget.appendPlainText("Test finished"))
        self.thread.start()

    def stop_test(self):
        if self.worker:
            self.worker.stop()

    # ---------------- Locust ----------------
    def start_locust(self):
        urls = [u.strip() for u in self.url_input.text().split(',') if u.strip()]
        if not urls:
            self.log_widget.appendPlainText("Ingen URL angiven för Locust!")
            return
        user_count = self.locust_users_input.value()
        self.locust_process = start_locust_auto(urls, user_count=user_count, spawn_rate=10)
        self.log_widget.appendPlainText(f"Locust swarm startad med {user_count} users! Kontrollera http://localhost:8089")

    def stop_locust(self):
        if self.locust_process:
            self.locust_process.terminate()
            self.locust_process = None
            self.log_widget.appendPlainText("Locust swarm stoppad!")

# ----------------------------- Main -----------------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
