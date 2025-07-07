# app.py – Polished Qt6 application with aligned text, proper singular/plural, and 3-decimal precision

import sys
import os
import json
from collections import Counter

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QGroupBox,
    QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton,
    QMessageBox, QDialog, QScrollArea, QFormLayout,
    QDialogButtonBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pyperclip

# Optional modern Qt styling
try:
    import qtmodern.styles, qtmodern.windows
    USE_MODERN = True
except ImportError:
    USE_MODERN = False

CONFIG_FILE = "StatusMappings.json"

def load_mappings(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_mappings(path, mappings):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2)

def format_output_text(statuses, total, show_percentage):
    lines = []
    # Header
    success = sum(1 for s in statuses if s == 'FINISHED (SUCCESS)')
    noun_total = "device" if total == 1 else "devices"
    verb = "was" if success == 1 else "were"
    lines.append("RTMS US Deployment Mechanism")
    lines.append("")
    header = f"{success} of {total} scheduled {noun_total} {verb} patched:"
    lines.append(header)

    # Indent subsequent lines under "of"
    idx = header.find('of')
    indent = ' ' * (idx if idx >= 0 else 0)

    # Group counts
    groups = Counter(statuses)
    items = sorted(groups.items(), key=lambda x: x[1], reverse=True)
    max_txt = max((len(f"{cnt} {'device' if cnt==1 else 'devices'} - {stat}") for stat, cnt in items), default=0)
    pad = 5

    for stat, cnt in items:
        noun = "device" if cnt == 1 else "devices"
        txt = f"{cnt} {noun} - {stat}"
        if show_percentage and total:
            pct = round(cnt / total * 100, 3)
            spaces = ' ' * (max_txt - len(txt) + pad)
            txt = txt + spaces + f"({pct}%)"
        lines.append(indent + txt)

    return "\n".join(lines)

class MapDialog(QDialog):
    def __init__(self, parent, statuses, mappings):
        super().__init__(parent)
        self.setWindowTitle("Map New Statuses")
        self.resize(600, 400)
        self.mappings = mappings
        self.statuses = statuses
        self.combos = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        container = QWidget(); form = QFormLayout(container)

        options = [
            "FINISHED (SUCCESS)", "FINISHED (FAILED)", "PRECHECKS",
            "PENDING", "IN PROGRESS", "NOT STARTED", "CANCELLED",
            "FAILED", "UNKNOWN"
        ]
        options += [v for v in self.mappings.values() if v not in options]

        for status in sorted(self.statuses):
            combo = QComboBox()
            combo.addItem("-- Select classification --")
            combo.addItems(options)
            if status in self.mappings:
                idx = combo.findText(self.mappings[status])
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            form.addRow(QLabel(status), combo)
            self.combos[status] = combo

        container.setLayout(form)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        changed = False
        for status, combo in self.combos.items():
            val = combo.currentText()
            if val != "-- Select classification --":
                if self.mappings.get(status) != val:
                    self.mappings[status] = val
                    changed = True
            elif status in self.mappings:
                del self.mappings[status]
                changed = True
        QMessageBox.information(
            self,
            "Mappings",
            "Mappings updated successfully." if changed else "No changes made."
        )
        self.accept()

class HelpDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.resize(500, 400)
        text = QPlainTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
"""Status Report Analyzer Help

1. Copy your 'Status' column from Excel or similar.
2. Paste into the input box.
3. Click 'Execute' to analyze.
4. Click 'Show %' to toggle percentages on the summary.
5. Click 'Map Statuses' to define mappings for any new statuses.
"""
        )
        layout = QVBoxLayout(self)
        layout.addWidget(text)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Status Report Analyzer")
        self.resize(900, 600)

        self.mappings = load_mappings(CONFIG_FILE)
        self.statuses = []
        self.show_pct = False

        self._build_ui()

    def _build_ui(self):
        mono = QFont("Consolas", 10)
        central = QWidget(); self.setCentralWidget(central)
        v = QVBoxLayout(central)

        lbl = QLabel("Paste 'Status' column below and click Execute:")
        v.addWidget(lbl)

        self.input = QPlainTextEdit(); self.input.setFont(mono)
        v.addWidget(self.input, 2)

        h1 = QHBoxLayout()
        for txt, fn in [("Paste", self._do_paste), ("Execute", self._execute), ("Clear", self._clear)]:
            b = QPushButton(txt); b.clicked.connect(fn); h1.addWidget(b)
        v.addLayout(h1)

        self.output = QPlainTextEdit(); self.output.setFont(mono); self.output.setReadOnly(True)
        v.addWidget(self.output, 4)

        h2 = QHBoxLayout()
        self.btn_pct = QPushButton("Show %")
        self.btn_pct.setEnabled(False)
        self.btn_pct.clicked.connect(self._toggle_pct)
        self.btn_map = QPushButton("Map Statuses")
        self.btn_map.setEnabled(False)
        self.btn_map.clicked.connect(self._map_statuses)
        self.btn_help = QPushButton("Help")
        self.btn_help.clicked.connect(self._show_help)
        for btn in (self.btn_pct, self.btn_map, self.btn_help):
            h2.addWidget(btn)
        h2.addStretch()
        v.addLayout(h2)

        self.lbl_count = QLabel("Devices: 0")
        v.addWidget(self.lbl_count, alignment=Qt.AlignRight)

    def _do_paste(self):
        self.input.setPlainText(pyperclip.paste())

    def _clear(self):
        self.input.clear()
        self.output.clear()
        self.btn_pct.setEnabled(False)
        self.btn_map.setEnabled(False)
        self.lbl_count.setText("Devices: 0")

    def _execute(self):
        lines = [l.strip() for l in self.input.toPlainText().splitlines() if l.strip()]
        total = len(lines)
        self.lbl_count.setText(f"Devices: {total}")
        new = []
        self.statuses = []
        for l in lines:
            cls = self.mappings.get(l)
            if not cls:
                cls = self._classify(l)
                new.append(l)
            self.statuses.append(cls)

        text = format_output_text(self.statuses, total, self.show_pct)
        self.output.setPlainText(text)

        self.btn_pct.setEnabled(True)
        self.btn_map.setEnabled(bool(new))
        self.show_pct = False
        self.btn_pct.setText("Show %")

    def _classify(self, text):
        u = text.upper()
        if 'FINISHED' in u and 'FAILED' in u:
            return 'FINISHED (FAILED)'
        if 'FINISHED' in u and 'SUCCESS' in u:
            return 'FINISHED (SUCCESS)'
        if 'PRECHECKS' in u:
            return 'PRECHECKS'
        if 'FAILED' in u:
            return 'FAILED'
        return text

    def _toggle_pct(self):
        self.show_pct = not self.show_pct
        self.btn_pct.setText("Hide %" if self.show_pct else "Show %")
        # re-render percentages
        self._execute()

    def _map_statuses(self):
        new = [s for s in set(self.statuses) if s not in self.mappings.values()]
        dlg = MapDialog(self, new, self.mappings)
        if dlg.exec_():
            save_mappings(CONFIG_FILE, self.mappings)
            self._execute()

    def _show_help(self):
        dlg = HelpDialog(self)
        dlg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if USE_MODERN:
        qtmodern.styles.light(app)
        w = MainWindow()
        mw = qtmodern.windows.ModernWindow(w)
        mw.show()
    else:
        w = MainWindow()
        w.show()
    sys.exit(app.exec())
