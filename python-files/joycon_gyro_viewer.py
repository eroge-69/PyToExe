#!/usr/bin/env python3
"""
JoyCon Gyro Viewer (Standalone)
Lightweight desktop app showing Joy-Con gyro data or simulation.
Works offline (simulated) or with UDP JSON data on port 26760.
Author: ali + GPT-5
"""

import sys, math, json, socket, threading, time
import numpy as np
from collections import deque
from PyQt6 import QtCore, QtWidgets
import pyqtgraph as pg

# ===== SETTINGS =====
UPDATE_MS = 30          # Refresh every X ms
PLOT_SECONDS = 5        # How many seconds of data to show
UDP_PORT = 26760        # If using real UDP gyro source
SIMULATE_ALWAYS = True  # True = always simulate; False = wait for UDP
# =====================

class GyroModel(QtCore.QObject):
    updated = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.gyro = np.zeros(3)
        self.angles = np.zeros(3)
        self.times = deque(maxlen=int(PLOT_SECONDS*1000/UPDATE_MS))
        self.hist = deque(maxlen=int(PLOT_SECONDS*1000/UPDATE_MS))
        self.last_time = None
        self.has_data = False

    def push(self, gx, gy, gz):
        now = time.time()
        with self.lock:
            self.gyro[:] = [gx, gy, gz]
            self.times.append(now)
            self.hist.append(self.gyro.copy())
            if self.last_time:
                dt = now - self.last_time
                self.angles += np.degrees(self.gyro) * dt
            self.last_time = now
            self.has_data = True
        self.updated.emit()

    def parse_json(self, txt):
        try:
            d = json.loads(txt)
            if "gyro" in d:
                g = d["gyro"]
                self.push(g[0], g[1], g[2])
            elif all(k in d for k in ("gyroX", "gyroY", "gyroZ")):
                self.push(d["gyroX"], d["gyroY"], d["gyroZ"])
        except Exception:
            pass

    def get_latest(self):
        with self.lock:
            return *self.gyro, *self.angles, self.has_data

    def get_history(self):
        with self.lock:
            if not self.times:
                return np.array([]), np.empty((0,3))
            t0 = self.times[0]
            t = np.array(self.times) - t0
            d = np.vstack(self.hist)
            return t, d


class UDPListener(threading.Thread):
    def __init__(self, model):
        super().__init__(daemon=True)
        self.model = model
        self.running = True

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.bind(("0.0.0.0", UDP_PORT))
            s.settimeout(0.5)
            while self.running:
                try:
                    data, _ = s.recvfrom(4096)
                    txt = data.decode("utf-8", errors="ignore").strip()
                    self.model.parse_json(txt)
                except socket.timeout:
                    continue
                except Exception:
                    continue
        finally:
            s.close()

    def stop(self):
        self.running = False


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Joy-Con Gyro Viewer")
        self.resize(760, 440)

        # layout
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)

        self.label = QtWidgets.QLabel("Waiting for data...")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size:18px; font-weight:bold;")
        v.addWidget(self.label)

        self.plot = pg.PlotWidget()
        self.plot.addLegend()
        self.plot.setLabel("bottom", "Time (s)")
        self.plot.setLabel("left", "Gyro (°/s)")
        self.curves = [
            self.plot.plot(pen=pg.mkPen('r'), name='X'),
            self.plot.plot(pen=pg.mkPen('g'), name='Y'),
            self.plot.plot(pen=pg.mkPen('b'), name='Z')
        ]
        v.addWidget(self.plot)

        self.orientation = QtWidgets.QLabel()
        self.orientation.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.orientation.setStyleSheet("font-size:16px; color:#555;")
        v.addWidget(self.orientation)

        self.setCentralWidget(w)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(UPDATE_MS)

    def refresh(self):
        gx, gy, gz, ax, ay, az, has_data = self.model.get_latest()

        # Simulate if needed
        if SIMULATE_ALWAYS or not has_data:
            t = time.time()
            gx = math.sin(t) * 2.0
            gy = math.cos(t*0.8) * 1.5
            gz = math.sin(t*1.3) * 2.2
            self.model.push(gx, gy, gz)
            has_data = True

        # Update labels
        if has_data:
            self.label.setText(f"Gyro:  X={gx:6.2f}   Y={gy:6.2f}   Z={gz:6.2f}")
            self.orientation.setText(f"Orientation (°):  Roll={ax:6.1f}  Pitch={ay:6.1f}  Yaw={az:6.1f}")
        else:
            self.label.setText("Waiting for Joy-Con data...")

        # Update plot
        t, d = self.model.get_history()
        if len(t) > 2:
            for i in range(3):
                self.curves[i].setData(t, d[:, i])


def main():
    app = QtWidgets.QApplication(sys.argv)
    model = GyroModel()
    win = MainWindow(model)
    win.show()

    listener = None
    if not SIMULATE_ALWAYS:
        listener = UDPListener(model)
        listener.start()

    ret = app.exec()
    if listener:
        listener.stop()
    return ret


if __name__ == "__main__":
    sys.exit(main())
