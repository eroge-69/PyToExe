#!/usr/bin/env python3
# SRQ/SQR (SREQ/STQR) Patcher GUI for Resident Evil 5
# Looks/works similarly to MT Framework tools: open file, inspect table, swap/map/zero columns, save.
# Requires: Python 3.9+ and PySide6
import sys
import struct
from typing import List, Tuple
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QLineEdit, QTableView, QHeaderView, QComboBox, QStatusBar, QAction
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt

def parse_u32_le(buf: bytes) -> List[int]:
    if len(buf) % 4 != 0:
        buf = buf[: len(buf) // 4 * 4]
    count = len(buf) // 4
    return list(struct.unpack("<" + "I" * count, buf))

def pack_u32_le(values: List[int]) -> bytes:
    return struct.pack("<" + "I" * len(values), *values)

def detect_signature(data: bytes) -> str:
    if len(data) < 4:
        return "????"
    return data[:4].decode("latin1", errors="replace")

def candidates_record_sizes(u32: List[int], min_size=8, max_size=64) -> List[Tuple[int,int,int]]:
    out = []
    total = len(u32)
    for size in range(min_size, max_size + 1):
        nrec = total // size
        if nrec >= 4:
            rem = total - nrec * size
            out.append((size, nrec, rem))
    out.sort(key=lambda x: (x[2], -x[1]))  # prefer minimal remainder, then more records
    return out

def reshape_records(u32: List[int], size: int) -> Tuple[List[List[int]], List[int]]:
    nrec = len(u32) // size
    body = u32[: nrec * size]
    tail = u32[nrec * size :]
    records = [body[i*size:(i+1)*size] for i in range(nrec)]
    return records, tail

def swap_values_in_column(records: List[List[int]], col: int, a: int, b: int) -> int:
    changed = 0
    for rec in records:
        if 0 <= col < len(rec):
            if rec[col] == a:
                rec[col] = b; changed += 1
            elif rec[col] == b:
                rec[col] = a; changed += 1
    return changed

def map_values_in_column(records: List[List[int]], col: int, mapping) -> int:
    changed = 0
    for rec in records:
        if 0 <= col < len(rec):
            old = rec[col]
            if old in mapping and mapping[old] != old:
                rec[col] = mapping[old]; changed += 1
    return changed

def zero_column(records: List[List[int]], col: int) -> int:
    changed = 0
    for rec in records:
        if 0 <= col < len(rec) and rec[col] != 0:
            rec[col] = 0; changed += 1
    return changed

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRQ/SQR Patcher (RE5) – MT-Style")
        self.resize(1100, 720)
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

        # Data
        self.path = None
        self.orig_bytes: bytes = b""
        self.header_size = 4
        self.u32: List[int] = []
        self.records: List[List[int]] = []
        self.tail_u32: List[int] = []
        self.record_size = 37  # default common guess

        # UI
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Top controls
        top = QHBoxLayout()
        self.btn_open = QPushButton("Open SRQ/SQR…")
        self.btn_save = QPushButton("Save As…")
        self.btn_save.setEnabled(False)
        self.cmb_recsize = QComboBox()
        self.cmb_recsize.setEditable(False)
        self.cmb_recsize.setMinimumWidth(180)
        self.lbl_sig = QLabel("Signature: —")
        top.addWidget(self.btn_open)
        top.addWidget(self.btn_save)
        top.addWidget(QLabel("Record size:"))
        top.addWidget(self.cmb_recsize)
        top.addStretch(1)
        top.addWidget(self.lbl_sig)
        root.addLayout(top)

        # Table
        self.table = QTableView()
        self.model = QStandardItemModel(self)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        root.addWidget(self.table, 1)

        # Bottom controls
        bottom = QHBoxLayout()
        self.spin_col = QSpinBox(); self.spin_col.setRange(0, 999); self.spin_col.setPrefix("col ")
        self.spin_a = QSpinBox(); self.spin_a.setRange(0, 2**31-1); self.spin_a.setPrefix("A=")
        self.spin_b = QSpinBox(); self.spin_b.setRange(0, 2**31-1); self.spin_b.setPrefix("B=")
        self.ed_map = QLineEdit(); self.ed_map.setPlaceholderText("Mapping: e.g. 0:1 2:0 85:0")
        self.btn_swap = QPushButton("Swap A↔B")
        self.btn_map = QPushButton("Map pairs")
        self.btn_zero = QPushButton("Zero column")
        bottom.addWidget(QLabel("Column:"))
        bottom.addWidget(self.spin_col)
        bottom.addWidget(self.spin_a)
        bottom.addWidget(self.spin_b)
        bottom.addWidget(self.btn_swap)
        bottom.addSpacing(16)
        bottom.addWidget(self.ed_map, 1)
        bottom.addWidget(self.btn_map)
        bottom.addSpacing(16)
        bottom.addWidget(self.btn_zero)
        root.addLayout(bottom)

        # Menu: export CSV
        act_export = QAction("Export CSV…", self)
        act_export.triggered.connect(self.on_export_csv)
        self.menuBar().addAction(act_export)

        # Signals
        self.btn_open.clicked.connect(self.on_open)
        self.btn_save.clicked.connect(self.on_save_as)
        self.btn_swap.clicked.connect(self.on_swap)
        self.btn_map.clicked.connect(self.on_map)
        self.btn_zero.clicked.connect(self.on_zero)
        self.cmb_recsize.currentIndexChanged.connect(self.on_recsize_changed)

        self.update_ui_state(False)

    def update_ui_state(self, has_data: bool):
        self.btn_save.setEnabled(has_data)
        self.btn_swap.setEnabled(has_data)
        self.btn_map.setEnabled(has_data)
        self.btn_zero.setEnabled(has_data)
        self.cmb_recsize.setEnabled(has_data)

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open SRQ/SQR", "", "Sound Request (*.srq *.sqr);;All Files (*)")
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")
            return
        self.path = path
        self.orig_bytes = data
        sig = detect_signature(data)
        self.lbl_sig.setText(f"Signature: {sig!r}")
        if len(data) < 8:
            QMessageBox.warning(self, "Warning", "File is too small.")
            return

        self.u32 = parse_u32_le(data[self.header_size:])
        cands = candidates_record_sizes(self.u32, 8, 64)
        self.cmb_recsize.blockSignals(True)
        self.cmb_recsize.clear()
        for size, nrec, rem in cands[:30]:
            self.cmb_recsize.addItem(f"{size} u32  –  {nrec} records  (rem {rem})", size)
        # select default or first
        idx = 0
        for i in range(self.cmb_recsize.count()):
            if self.cmb_recsize.itemData(i) == 37:
                idx = i; break
        self.cmb_recsize.setCurrentIndex(idx if self.cmb_recsize.count() else -1)
        self.cmb_recsize.blockSignals(False)

        if self.cmb_recsize.count() == 0:
            QMessageBox.warning(self, "Warning", "Could not infer record sizes (not enough data).")
            self.update_ui_state(False)
            return

        self.record_size = self.cmb_recsize.currentData()
        self.records, self.tail_u32 = reshape_records(self.u32, self.record_size)
        self.populate_table()
        self.status.showMessage(f"Opened {path} – {len(self.records)} records, record size {self.record_size} u32", 7000)
        self.update_ui_state(True)

    def populate_table(self):
        self.model.clear()
        if not self.records:
            return
        cols = len(self.records[0])
        headers = [f"field_{i}" for i in range(cols)]
        self.model.setColumnCount(cols)
        self.model.setHorizontalHeaderLabels(headers)
        # show up to 5000 rows for performance
        max_rows = min(5000, len(self.records))
        self.model.setRowCount(max_rows)
        for r in range(max_rows):
            rec = self.records[r]
            for c, val in enumerate(rec):
                item = QStandardItem(str(val))
                item.setEditable(False)
                # right-align numbers
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.model.setItem(r, c, item)

    def on_recsize_changed(self, idx: int):
        if idx < 0: return
        size = self.cmb_recsize.itemData(idx)
        if not size: return
        self.record_size = size
        self.records, self.tail_u32 = reshape_records(self.u32, self.record_size)
        self.populate_table()
        self.status.showMessage(f"Record size set to {size} u32 – {len(self.records)} records", 5000)

    def on_swap(self):
        if not self.records:
            return
        col = self.spin_col.value()
        a = self.spin_a.value()
        b = self.spin_b.value()
        changed = swap_values_in_column(self.records, col, a, b)
        self.populate_table()
        QMessageBox.information(self, "Swap done", f"Swapped {changed} occurrences of {a}↔{b} in column {col}.")

    def on_map(self):
        if not self.records:
            return
        col = self.spin_col.value()
        text = self.ed_map.text().strip()
        if not text:
            QMessageBox.warning(self, "Mapping empty", "Enter mapping pairs like: 0:1 2:0 85:0")
            return
        mapping = {}
        try:
            for token in text.split():
                a, b = token.split(":")
                mapping[int(a)] = int(b)
        except Exception:
            QMessageBox.critical(self, "Error", "Bad mapping format. Use pairs like '0:1 2:0 85:0'")
            return
        changed = map_values_in_column(self.records, col, mapping)
        self.populate_table()
        QMessageBox.information(self, "Map done", f"Changed {changed} values in column {col} using mapping.")

    def on_zero(self):
        if not self.records:
            return
        col = self.spin_col.value()
        changed = zero_column(self.records, col)
        self.populate_table()
        QMessageBox.information(self, "Zero done", f"Zeroed {changed} entries in column {col}.")

    def on_export_csv(self):
        if not self.records:
            QMessageBox.warning(self, "No data", "Open a file first.")
            return
        out, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV (*.csv)")
        if not out:
            return
        try:
            import csv
            with open(out, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                headers = [f"field_{i}" for i in range(len(self.records[0]))]
                w.writerow(["record_index"] + headers)
                for i, rec in enumerate(self.records):
                    w.writerow([i] + rec)
            QMessageBox.information(self, "Exported", f"CSV saved to:\n{out}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{e}")

    def build_bytes(self) -> bytes:
        body_u32 = [x for rec in self.records for x in rec]
        body_bytes = pack_u32_le(body_u32 + self.tail_u32)
        original_u32_region = self.orig_bytes[self.header_size:]
        header = self.orig_bytes[:self.header_size]
        if len(body_bytes) <= len(original_u32_region):
            tail_bytes = original_u32_region[len(body_bytes):]
            out = header + body_bytes + tail_bytes
        else:
            out = header + body_bytes
        return out

    def on_save_as(self):
        if not self.records:
            return
        out, _ = QFileDialog.getSaveFileName(self, "Save Patched SRQ", "", "Sound Request (*.srq *.sqr);;All Files (*)")
        if not out:
            return
        try:
            data = self.build_bytes()
            with open(out, "wb") as f:
                f.write(data)
            QMessageBox.information(self, "Saved", f"Patched file saved to:\n{out}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
