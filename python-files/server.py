#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FPV-Race Manager — Live-таймер + конфиг порогов (2025-07-13)
Adapted for Windows and Mac OS, reading data from Base ESP via USB and Wi-Fi.
With pilot synchronization between PilotTab and RaceTab.
"""

# ─────────── imports ───────────
import csv
import json
import socket
import sys
import threading
import time
import queue
from pathlib import Path
from typing import Optional
import serial
import serial.tools.list_ports
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QHBoxLayout, QMessageBox,
    QHeaderView, QAbstractItemView, QComboBox, QLineEdit)

# ─────────── runtime-config ───────────
SERIAL_PORT: Optional[str] = None  # None → auto-detect
SERIAL_BAUD = 115200
BASE_IP = "192.168.4.1"  # Wi-Fi IP (ESP base AP), set to "" to disable Wi-Fi
UDP_PORT = 12345
UDP_LISTEN = True  # Enable UDP for Wi-Fi communication

# ─────────── queues ───────────
q_live = queue.Queue(2000)  # Increased capacity
serial_tx = queue.Queue(200)  # Outgoing to USB

SETTINGS_FILE = "settings.json"
SETTINGS = {
    "SERIAL_PORT": None,
    "BASE_IP": BASE_IP,
}

def loadSettings():
    global SETTINGS, SERIAL_PORT, BASE_IP
    try:
        with open(SETTINGS_FILE, "r") as f:
            SETTINGS.update(json.load(f))
            SERIAL_PORT = SETTINGS.get("SERIAL_PORT", None)
            BASE_IP = SETTINGS.get("BASE_IP", "192.168.4.1")
            print("[settings] loaded:", SETTINGS)
    except FileNotFoundError:
        print("[settings] no settings file, using defaults")

def saveSettings():
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(SETTINGS, f, indent=2)
            print("[settings] saved:", SETTINGS)
    except Exception as e:
        print(f"[settings] failed to save: {e}")

# ═════════ transport helpers ═════════
def _auto_serial() -> Optional[str]:
    """Return suitable serial port for Windows/Mac, if SERIAL_PORT not set"""
    if SERIAL_PORT:
        return SERIAL_PORT
    ports = serial.tools.list_ports.comports()
    for p in ports:
        device_lower = p.device.lower()
        if 'usb' in device_lower or 'acm' in device_lower or 'wch' in device_lower or 'com' in device_lower or 'tty' in device_lower or 'cu.' in device_lower:
            print("[auto-serial] found:", p.device)
            return p.device
    return None

def _serial_worker():
    """Background thread: USB RX and TX"""
    while True:
        port = _auto_serial()
        if not port:
            print("[serial] No port found, retrying...")
            time.sleep(2)
            continue
        try:
            with serial.Serial(port, SERIAL_BAUD, timeout=0.1) as ser:
                print("[serial] open", port)
                buf = b""
                while True:
                    while not serial_tx.empty():
                        ser.write(serial_tx.get_nowait())
                    buf += ser.read(256)
                    while b'\n' in buf:
                        line, buf = buf.split(b'\n', 1)
                        q_live.put_nowait(line)
        except Exception as e:
            print(f"[serial] Error: {e}")
            time.sleep(2)

def _udp_reader():
    if not UDP_LISTEN:
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(("", UDP_PORT))
            print("[udp] Listening on port", UDP_PORT)
            while True:
                data, _ = s.recvfrom(256)
                q_live.put_nowait(data.rstrip(b'\n'))
    except OSError as e:
        print(f"[udp] Error: {e} - UDP listener skipped")
        return
def send_raw(data: bytes, base_ip: str = BASE_IP):
    """Send via USB or UDP to base"""
    if base_ip:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(data, (base_ip, UDP_PORT))
                print(f"[send_raw] Sent via UDP: {data}")
                return
        except Exception as e:
            print(f"[send_raw] UDP failed: {e}, falling back to Serial")
    serial_tx.put_nowait(data)
    print(f"[send_raw] Sent via Serial: {data}")

# ═════════ GUI – tabs ═════════
# ───── PilotTab ─────
class PilotTab(QWidget):
    pilots_updated = Signal()

    def __init__(self):
        super().__init__()
        self.pilots = []  # Unified source of pilot names
        lay = QVBoxLayout(self)
        self.tbl = QTableWidget(100, 1, self)
        self.tbl.setHorizontalHeaderLabels(["Ім'я"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        lay.addWidget(self.tbl)
        self.tbl.itemChanged.connect(self._on_item_changed)

        row = QHBoxLayout()
        row.addWidget(QPushButton("💾 CSV", clicked=self.save_csv))
        row.addWidget(QPushButton("📂 CSV", clicked=self.load_csv))
        row.addWidget(QPushButton("🗑", clicked=self.clear_table))
        row.addWidget(QPushButton("➕ Add Pilot", clicked=self.add_pilot))
        row.addStretch()
        lay.addLayout(row)

    def current_list(self) -> list[str]:
        return self.pilots.copy()

    def _update_pilots_from_table(self):
        self.pilots = [self.tbl.item(r, 0).text().strip() for r in range(self.tbl.rowCount())
                       if self.tbl.item(r, 0) and self.tbl.item(r, 0).text().strip()]

    def _on_item_changed(self, item):
        self._update_pilots_from_table()
        self.pilots_updated.emit()

    def add_pilot(self):
        row = len(self.pilots)
        self.tbl.insertRow(row)
        self.tbl.setItem(row, 0, QTableWidgetItem("New Pilot"))
        self.pilots.append("New Pilot")
        self.pilots_updated.emit()

    def clear_table(self):
        self.tbl.clearContents()
        self.tbl.setRowCount(100)
        self.pilots = []
        self.pilots_updated.emit()

    def save_csv(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save", str(Path.home()), "CSV (*.csv)")
        if fn:
            with open(fn, "w", newline="") as f:
                csv.writer(f).writerows([[n] for n in self.pilots])

    def load_csv(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open", str(Path.home()), "CSV (*.csv)")
        if fn:
            with open(fn) as f:
                r = csv.reader(f)
                self.tbl.blockSignals(True)  # ⛔ отключить временно
                self.tbl.setRowCount(0)
                self.pilots = []
                for i, (name,) in enumerate(r):
                    if i >= 100:
                        break
                    stripped_name = name.strip()
                    self.tbl.insertRow(i)
                    item = QTableWidgetItem(stripped_name)
                    item.setFlags(Qt.ItemIsEnabled)
                    self.tbl.setItem(i, 0, item)
                    self.pilots.append(stripped_name)
                self.tbl.blockSignals(False)  # ✅ включить обратно
                self.pilots_updated.emit()

# ───── SettingsTab ─────
class SettingsTab(QWidget):
    def __init__(self, tx):
        super().__init__()
        self._tx = tx
        self.thresholds = [[780, 790] for _ in range(8)]  # Настроено для 2 Вт
        self.detect_mode = [True] * 8
        self.gate_order = list(range(8))
        lay = QVBoxLayout(self)

        self.tbl = QTableWidget(8, 4)
        self.tbl.setDragEnabled(True)
        self.tbl.setAcceptDrops(True)
        self.tbl.setDragDropMode(QAbstractItemView.InternalMove)
        lay.addWidget(self.tbl)
        self.tbl.setHorizontalHeaderLabels(["Gate", "ON, mV", "OFF, mV", "Detect"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._update_table()

        row = QHBoxLayout()
        row.addWidget(QPushButton("📤 Apply row", clicked=self._apply_row))
        row.addWidget(QPushButton("🛈 Refresh all", clicked=self._refresh_all))
        row.addWidget(QPushButton("🔄 Toggle Detect", clicked=self._toggle_detect))
        row.addWidget(QPushButton("🔼", clicked=self._move_up))
        row.addWidget(QPushButton("🔽", clicked=self._move_down))
        row.addStretch()
        lay.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Serial:"))
        self.cmb = QComboBox()
        self._fill_ports()
        row2.addWidget(self.cmb)
        row2.addWidget(QPushButton("💾 Save", clicked=self._save_port))
        row2.addWidget(QLabel("Base IP:"))
        self.ip_input = QLineEdit(BASE_IP)
        row2.addWidget(self.ip_input)
        row2.addWidget(QPushButton("💾 Save IP", clicked=self._save_ip))
        row2.addStretch()
        lay.addLayout(row2)

        self.timer_id = self.startTimer(30)

    def _fill_ports(self):
        self.cmb.clear()
        self.cmb.addItem("auto")
        self.cmb.addItems([p.device for p in serial.tools.list_ports.comports()])

    def _apply_row(self):
        r = self.tbl.currentRow()
        if r < 0:
            return
        try:
            on = int(self.tbl.item(r, 1).text())
            off = int(self.tbl.item(r, 2).text())
            if on < 0 or off < 0 or off <= on:
                QMessageBox.warning(self, "", f"Неверные пороги для ворот {r+1}: ON={on}, OFF={off}")
                return
            self.thresholds[self.gate_order[r]] = [on, off]
            self._tx(json.dumps({"cfg": "thr", "gate": self.gate_order[r] + 1, "on": on, "off": off}).encode() + b"\n",
                     self.ip_input.text())
            self._update_table()
            print(f"[SettingsTab] Applied gate {self.gate_order[r] + 1}: thrOn={on}, thrOff={off}")
        except (ValueError, TypeError) as e:
            QMessageBox.warning(self, "", f"Введите целые mV: {e}")

    def _refresh_all(self):
        self._tx(b'{"cfg":"get"}\n', self.ip_input.text())
        self._update_table()
        print("[SettingsTab] Refreshed all thresholds")

    def _toggle_detect(self):
        r = self.tbl.currentRow()
        if r < 0:
            return
        self.detect_mode[self.gate_order[r]] = not self.detect_mode[self.gate_order[r]]
        mode = "on" if self.detect_mode[self.gate_order[r]] else "off"
        self._tx(json.dumps({"cfg": "detect", "gate": self.gate_order[r] + 1, "mode": mode}).encode() + b"\n",
                 self.ip_input.text())
        self._update_table()
        print(f"[SettingsTab] Toggled gate {self.gate_order[r] + 1} detect mode to {mode}")

    def _save_port(self):
        global SERIAL_PORT
        SERIAL_PORT = None if self.cmb.currentText() == "auto" else self.cmb.currentText()
        SETTINGS["SERIAL_PORT"] = SERIAL_PORT
        saveSettings()
        QMessageBox.information(self, "", "Порт сохранён. Перезапустите GUI.")

    def _save_ip(self):
        global BASE_IP
        BASE_IP = self.ip_input.text().strip()
        SETTINGS["BASE_IP"] = BASE_IP
        saveSettings()
        QMessageBox.information(self, "", "IP сохранён. Перезапустите GUI.")

    def _update_table(self):
        for g in range(8):
            idx = self.gate_order[g]
            self.tbl.setItem(g, 0, QTableWidgetItem(f"G{idx + 1}"))
            self.tbl.item(g, 0).setFlags(Qt.ItemIsEnabled)
            self.tbl.setItem(g, 1, QTableWidgetItem(str(self.thresholds[idx][0])))
            self.tbl.setItem(g, 2, QTableWidgetItem(str(self.thresholds[idx][1])))
            self.tbl.setItem(g, 3, QTableWidgetItem("ON" if self.detect_mode[idx] else "OFF"))
            self.tbl.item(g, 3).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.tbl.viewport().update()

    def _move_up(self):
        r = self.tbl.currentRow()
        if r > 0:
            self.gate_order[r], self.gate_order[r - 1] = self.gate_order[r - 1], self.gate_order[r]
            self._update_table()
            print(f"[SettingsTab] Moved gate {r + 1} up")

    def _move_down(self):
        r = self.tbl.currentRow()
        if r < 7:
            self.gate_order[r], self.gate_order[r + 1] = self.gate_order[r + 1], self.gate_order[r]
            self._update_table()
            print(f"[SettingsTab] Moved gate {r + 1} down")

    def showThr(self, g, on, off):
        if 1 <= g <= 8:
            try:
                idx = self.gate_order.index(g - 1)
                on = int(on) if isinstance(on, (int, str)) else on
                off = int(off) if isinstance(off, (int, str)) else off
                if on < 0 or off < 0 or off <= on:
                    print(f"[SettingsTab] Invalid thresholds for gate {g}: on={on}, off={off}")
                    return
                self.thresholds[g - 1] = [on, off]
                self.tbl.setItem(idx, 1, QTableWidgetItem(str(on)))
                self.tbl.setItem(idx, 2, QTableWidgetItem(str(off)))
                self.tbl.viewport().update()
                print(f"[SettingsTab] Updated gate {g}: thrOn={on}, thrOff={off}")
            except (ValueError, TypeError) as e:
                print(f"[SettingsTab] Invalid threshold values for gate {g}: {e}")

    def timerEvent(self, event):
        if self.parent().currentWidget() != self:
            return
        while not q_live.empty():
            try:
                raw = q_live.get_nowait()
                print(f"[SettingsTab] Raw packet: {raw}")
                pkt = json.loads(raw.decode('utf-8', 'ignore'))
                print(f"[SettingsTab] Parsed packet: {pkt}")
                if "thrOn" in pkt and "thrOff" in pkt:
                    g = pkt.get("gate", 0)
                    if 1 <= g <= 8:
                        self.showThr(g, pkt["thrOn"], pkt["thrOff"])
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"[SettingsTab] JSON parse error: {e}, raw: {raw}")

# ───── RaceTab ─────
class RaceTab(QWidget):
    def __init__(self, pilot_tab: PilotTab, sett_tab: SettingsTab, tx_func):
        super().__init__()
        self.tx = tx_func
        self.pTab = pilot_tab
        self.sTab = sett_tab
        self.active_idx = 0
        self.start_ts = self.prev_ts = None
        self.total_time = 0.0
        self.prev_mv = None
        self.finished = set()
        self.dq = set()
        self.lastSeen = [0] * 8
        self.FINISH_GATE = 8
        self.last_gate = 0  # For strict sequence
        self.timer_id = self.startTimer(30)

        v = QVBoxLayout(self)
        ind = QHBoxLayout()
        ind.addWidget(QLabel("Індикатори воріт:"))
        self.ind = [QLabel(f"G{i+1} 🔴") for i in range(8)]
        for lab in self.ind:
            lab.setAlignment(Qt.AlignCenter)
            ind.addWidget(lab)
        ind.addStretch()
        v.addLayout(ind)

        cols = ["Учасник"] + [f"G{i}" for i in range(1, 9)] + ["Σ"]
        self.tbl = QTableWidget(0, len(cols))
        self.tbl.setHorizontalHeaderLabels(cols)
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl.itemSelectionChanged.connect(self._on_selection_changed)
        v.addWidget(self.tbl)

        row1 = QHBoxLayout()
        for txt, cb in (("⬅", self.prevPilot), ("➡", self.nextPilot), ("DQ", self.toggleDQ),
                        ("🏁 Фініш", self.finishManual)):
            row1.addWidget(QPushButton(txt, clicked=cb))
        row1.addStretch()
        v.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Finish gate:"))
        self.sel = QComboBox()
        self.sel.addItems([f"G{i}" for i in range(1, 9)])
        self.sel.setCurrentIndex(self.FINISH_GATE - 1)
        self.sel.currentIndexChanged.connect(lambda i: setattr(self, "FINISH_GATE", i + 1))
        row2.addWidget(self.sel)
        row2.addWidget(QPushButton("💾 CSV", clicked=self.save_results))
        row2.addWidget(QPushButton("📂 CSV", clicked=self.load_results))
        row2.addWidget(QPushButton("🏆 Подиум", clicked=self.showWinners))
        row2.addWidget(QPushButton("🗑 Очистити ряд", clicked=self.clearSelectedRow))
        row2.addWidget(QPushButton("🔄 Очистити все", clicked=self.clearTable))
        row2.addStretch()
        v.addLayout(row2)

        self.info_layout = QHBoxLayout()
        self.info = QLabel("Учасників: 0   •   Активний: ")
        self.info_layout.addWidget(self.info)
        self.active_name = QLabel("—")
        self.active_name.setStyleSheet("color: red;")
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self._toggle_blink)
        self.blink_state = True
        self.info_layout.addWidget(self.active_name)
        v.addLayout(self.info_layout)
        self.refreshPilots()

    def sync_pilots(self):
        pilots = self.pTab.current_list()
        self.tbl.setRowCount(len(pilots))
        for i, name in enumerate(pilots):
            self.tbl.setItem(i, 0, QTableWidgetItem(name))  # Копируем значение, новый item
        self._hilite()
        self._updInfo()

    def refreshPilots(self):
        self.sync_pilots()

    def _updInfo(self):
        names = self.pTab.current_list()
        self.info.setText(f"Учасників: {len(names)}   •   Активний: ")
        cur = names[self.active_idx] if self.active_idx < len(names) else "—"
        self.active_name.setText(cur)
        if cur != "—":
            self.blink_timer.start(500)
        else:
            self.blink_timer.stop()
            self.active_name.setStyleSheet("color: black;")

    def _toggle_blink(self):
        if self.blink_state:
            self.active_name.setStyleSheet("color: red;")
        else:
            self.active_name.setStyleSheet("color: black;")
        self.blink_state = not self.blink_state

    def _hilite(self):
        for r in range(self.tbl.rowCount()):
            bg = Qt.yellow if r == self.active_idx else Qt.white
            if r in self.dq:
                bg = Qt.red
            for c in range(self.tbl.columnCount()):
                it = self.tbl.item(r, c) or QTableWidgetItem()
                it.setBackground(bg)
                self.tbl.setItem(r, c, it)

    def _select(self, r):
        self.active_idx = r
        self.start_ts = self.prev_ts = None
        self.total_time = 0.0
        self.prev_mv = None
        self.last_gate = 0
        self._hilite()
        self._updInfo()

    def nextPilot(self):
        self._select(min(self.active_idx + 1, self.tbl.rowCount() - 1))

    def prevPilot(self):
        self._select(max(self.active_idx - 1, 0))

    def toggleDQ(self):
        if self.active_idx in self.dq:
            self.dq.remove(self.active_idx)
        else:
            self.dq.add(self.active_idx)
        self._hilite()

    def _on_selection_changed(self):
        selected = self.tbl.selectedIndexes()
        if selected:
            self._select(selected[0].row())

    def timerEvent(self, event):
        if self.parent().currentWidget() != self:
            return
        upd = False
        while not q_live.empty():
            try:
                raw = q_live.get_nowait()
                print(f"[RaceTab] Raw packet: {raw}")
                pkt = json.loads(raw.decode('utf-8', 'ignore'))
                print(f"[RaceTab] Parsed packet: {pkt}")

                if pkt.get("seq", 0) == 0:
                    g = pkt.get("gate", 0)
                    if 1 <= g <= 8:
                        self.lastSeen[g - 1] = time.time() * 1000
                    continue

                required_keys = {"gate", "ts", "mv", "seq"}
                if not required_keys.issubset(pkt.keys()):
                    print(f"[RaceTab] Missing required keys in JSON: {pkt}")
                    continue
                gate = pkt.get("gate", 0)
                if not 1 <= gate <= 8:
                    print(f"[RaceTab] Invalid gate: {gate}")
                    continue
                mv = pkt.get("mv", 0)
                if mv > 5000:
                    print(f"[RaceTab] Ignoring packet with invalid mv value: {mv} for gate {gate}")
                    continue
                if not self.sTab.detect_mode[self.sTab.gate_order[gate - 1]]:
                    print(f"[RaceTab] Ignoring gate {gate} due to detect mode OFF")
                    continue
                ts = pkt.get("ts", 0)
                if ts <= 0:
                    print(f"[RaceTab] Ignoring packet with invalid ts: {ts} for gate {gate}")
                    continue
                self.lastSeen[gate - 1] = time.time() * 1000

                if self.active_idx >= self.tbl.rowCount() or self.active_idx in self.dq:
                    continue

                expected_gate = self.last_gate + 1
                if gate != expected_gate:
                    print(f"[RaceTab] Ignoring out-of-sequence gate {gate} (expected {expected_gate})")
                    continue

                if gate == 1 and self.start_ts is None:
                    self.start_ts = self.prev_ts = ts
                    self.tbl.setItem(self.active_idx, 1, QTableWidgetItem("0.000"))
                    print(f"[RaceTab] Started race for pilot {self.active_idx} at ts={ts}")
                    self.last_gate = 1
                else:
                    total_time = (ts - self.start_ts) / 1000.0
                    split = (ts - self.prev_ts) / 1000.0
                    self.tbl.setItem(self.active_idx, gate, QTableWidgetItem(f"{split:.3f}"))
                    print(f"[RaceTab] Gate {gate} time: {split:.3f} for pilot {self.active_idx}")
                    self.prev_ts = ts
                    self.last_gate = gate
                    if gate == self.FINISH_GATE:
                        self.tbl.setItem(self.active_idx, 9, QTableWidgetItem(f"{total_time:.3f}"))
                        self.finished.add(self.active_idx)
                        print(f"[RaceTab] Finished pilot {self.active_idx}: {total_time:.3f}")

                upd = True
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"[RaceTab] JSON parse error: {e}, raw: {raw}")
                continue

        now = time.time() * 1000
        for g in range(8):
            alive = now - self.lastSeen[g] < 5000
            txt = self.ind[g].text()
            if alive and "🔴" in txt:
                self.ind[g].setText(txt.replace("🔴", "🟢"))
            if not alive and "🟢" in txt:
                self.ind[g].setText(txt.replace("🟢", "🔴"))
        if upd and self.tbl.rowCount():
            self.tbl.viewport().update()
            self.tbl.scrollToItem(self.tbl.item(self.active_idx, 0))

    def finishManual(self):
        if self.start_ts is None:
            return
        total = self.total_time if hasattr(self, 'total_time') else (int(time.time() * 1000) - self.start_ts) / 1000.0
        self.tbl.setItem(self.active_idx, 9, QTableWidgetItem(f"{total:.3f}"))
        self.finished.add(self.active_idx)
        print(f"[RaceTab] Manual finish for pilot {self.active_idx}: {total:.3f}")

    def clearSelectedRow(self):
        if self.active_idx >= self.tbl.rowCount():
            return
        for c in range(1, 10):
            self.tbl.setItem(self.active_idx, c, QTableWidgetItem(""))
        if self.active_idx in self.finished:
            self.finished.remove(self.active_idx)
        self.start_ts = self.prev_ts = None
        self.total_time = 0.0
        self.prev_mv = None
        self.last_gate = 0
        print(f"[RaceTab] Cleared row for pilot {self.active_idx}")

    def clearTable(self):
        for r in range(self.tbl.rowCount()):
            for c in range(1, 10):
                self.tbl.setItem(r, c, QTableWidgetItem(""))
        self.finished.clear()
        self.start_ts = self.prev_ts = None
        self.total_time = 0.0
        self.prev_mv = None
        self.last_gate = 0
        print("[RaceTab] Table cleared")

    def save_results(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save Results", str(Path.home()), "CSV (*.csv)")
        if fn:
            with open(fn, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Pilot"] + [f"G{i}" for i in range(1, 9)] + ["Sum"])
                for r in range(self.tbl.rowCount()):
                    row_data = [self.tbl.item(r, c).text() if self.tbl.item(r, c) else "" for c in range(self.tbl.columnCount())]
                    writer.writerow(row_data)

    def load_results(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Load Results", str(Path.home()), "CSV (*.csv)")
        if fn:
            with open(fn) as f:
                r = csv.reader(f)
                header = next(r)  # Skip header
                for row in r:
                    pilot_name = row[0]
                    # Find row for pilot
                    found = False
                    for i in range(self.tbl.rowCount()):
                        if self.tbl.item(i, 0).text() == pilot_name:
                            for c in range(1, 10):
                                self.tbl.setItem(i, c, QTableWidgetItem(row[c]))
                            if row[9]:  # If sum is set, add to finished
                                self.finished.add(i)
                            found = True
                            break
                    if not found:
                        QMessageBox.warning(self, "", f"Pilot {pilot_name} not found in current list")

    def showWinners(self):
        res = [(float(self.tbl.item(r, 9).text()), self.tbl.item(r, 0).text())
               for r in self.finished if r not in self.dq and self.tbl.item(r, 9) and self.tbl.item(r, 9).text()]
        if not res:
            QMessageBox.information(self, "", "Пока нет финишей")
            return
        res.sort()
        txt = "\n".join(f"{i+1}. {n} — {t:.3f} c" for i, (t, n) in enumerate(res))
        QMessageBox.information(self, "🏆 Лидеры", txt)

# ═════════ Main window ═════════
class MainWin(QTabWidget):
    def __init__(self):
        super().__init__()
        self.pTab = PilotTab()
        self.sTab = SettingsTab(send_raw)
        self.rTab = RaceTab(self.pTab, self.sTab, send_raw)
        for w, t in ((self.rTab, "Live"), (self.pTab, "Учасники"), (self.sTab, "Налаштування")):
            self.addTab(w, t)
        self.pTab.tbl.itemChanged.connect(self.rTab.refreshPilots)
        self.currentChanged.connect(self.on_tab_changed)
        self.pTab.pilots_updated.connect(self.rTab.sync_pilots)

    def on_tab_changed(self, index):
        race_tab = self.widget(index)
        if isinstance(race_tab, RaceTab) and race_tab.timer_id == 0:
            race_tab.timer_id = race_tab.startTimer(30)
        settings_tab = self.widget(index)
        if isinstance(settings_tab, SettingsTab) and settings_tab.timer_id == 0:
            settings_tab.timer_id = settings_tab.startTimer(30)
        for i in range(self.count()):
            tab = self.widget(i)
            if isinstance(tab, (RaceTab, SettingsTab)) and tab != self.widget(index) and tab.timer_id != 0:
                tab.killTimer(tab.timer_id)
                tab.timer_id = 0

# ═════════ entry-point ═════════
if __name__ == "__main__":
    loadSettings()
    threading.Thread(target=_serial_worker, daemon=True).start()
    threading.Thread(target=_udp_reader, daemon=True).start()

    app = QApplication(sys.argv)
    win = MainWin()
    win.resize(1000, 650)
    win.show()
    sys.exit(app.exec())
