import sys
import json
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QProgressBar, QTextEdit, QLabel, QStatusBar, QFileDialog, QComboBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QBrush

class ComparisonWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self, aao_file_path):
        super().__init__()
        self.aao_file_path = aao_file_path

    def run(self):
        try:
            self.log.emit("Lade aktuelle Einsätze von der API...")
            einsaetze_resp = requests.get("https://www.leitstellenspiel.de/einsaetze.json", timeout=30)
            einsaetze_resp.raise_for_status()
            einsaetze = einsaetze_resp.json()
            self.log.emit(f"{len(einsaetze)} Einsätze geladen.")

            self.log.emit(f"Lade AAO-Daten aus Datei: {self.aao_file_path}...")
            with open(self.aao_file_path, "r", encoding="utf-8") as f:
                aaos = json.load(f)
            self.log.emit(f"{len(aaos)} AAO-Einträge geladen.")

            aao_map = {str(a['caption']): a['vehicle_classes'] for a in aaos}

            einsatz_map = {}
            for einsatz in einsaetze:
                name = einsatz.get('name', 'Unbekannt')
                reward = einsatz.get('reward', 0)
                if name not in einsatz_map or reward > einsatz_map[name].get('reward', 0):
                    einsatz_map[name] = einsatz

            filtered_einsaetze = list(einsatz_map.values())
            total = len(filtered_einsaetze)
            results = []

            for idx, einsatz in enumerate(filtered_einsaetze, 1):
                name = einsatz.get('name', 'Unbekannt')
                requirements = einsatz.get('requirements', {})
                entry_log = {'name': name, 'issues': []}

                aao_vehicles = aao_map.get(name)
                if not aao_vehicles:
                    entry_log['issues'].append('AAO fehlt')
                else:
                    for key, val in requirements.items():
                        if not isinstance(val, int):
                            continue
                        aao_val = aao_vehicles.get(key, 0)
                        if not isinstance(aao_val, int):
                            continue
                        if aao_val < val:
                            entry_log['issues'].append(f"Zu wenig {key}: {aao_val} statt {val}")
                        elif aao_val > val:
                            entry_log['issues'].append(f"Zu viel {key}: {aao_val} statt {val}")
                    for key, val in aao_vehicles.items():
                        if not isinstance(val, int):
                            continue
                        if key not in requirements:
                            entry_log['issues'].append(f"Fahrzeug {key} in AAO, aber nicht im Einsatz")

                results.append(entry_log)
                self.progress.emit(int((idx / total) * 100))

            self.finished.emit(results)

        except Exception as e:
            self.log.emit(f"Fehler: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AAO Checker by NinoRossi")
        self.resize(1000, 700)

        main_layout = QVBoxLayout()

        self.label = QLabel("Status: Bereit")
        main_layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.progress)

        button_layout = QHBoxLayout()
        self.select_aao_button = QPushButton("AAO-Datei auswählen")
        self.select_aao_button.clicked.connect(self.select_aao_file)
        button_layout.addWidget(self.select_aao_button)

        self.start_button = QPushButton("Starte Vergleich")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_comparison)
        button_layout.addWidget(self.start_button)

        main_layout.addLayout(button_layout)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter nach Typ:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Alle")
        self.filter_combo.addItem("Zu wenig")
        self.filter_combo.addItem("Zu viel")
        self.filter_combo.addItem("AAO fehlt")
        self.filter_combo.setStyleSheet("QComboBox { color: black; }")  # Schriftfarbe dunkler
        self.filter_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_combo)
        main_layout.addLayout(filter_layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(QLabel("Log / Ergebnis:"))
        main_layout.addWidget(self.log_output, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("AAO Checker v1.6 © 2025 by NinoRossi")

        self.aao_file_path = None
        self.full_results = []

    def select_aao_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "AAO-Datei auswählen", "", "JSON Files (*.json)")
        if path:
            self.aao_file_path = path
            self.write_log(f"AAO-Datei ausgewählt: {path}")
            self.start_button.setEnabled(True)

    def start_comparison(self):
        if not self.aao_file_path:
            self.write_log("Keine AAO-Datei ausgewählt!")
            return

        self.start_button.setEnabled(False)
        self.log_output.clear()
        self.label.setText("Status: Vergleich läuft…")

        self.worker = ComparisonWorker(self.aao_file_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.write_log)
        self.worker.finished.connect(self.comparison_done)
        self.worker.start()

    def update_progress(self, val):
        self.progress.setValue(val)

    def write_log(self, msg):
        self.log_output.append(msg)

    def comparison_done(self, results):
        self.label.setText("Status: Vergleich abgeschlossen")
        self.start_button.setEnabled(True)
        self.full_results = results
        self.apply_filter()

    def apply_filter(self):
        filter_type = self.filter_combo.currentText()
        self.log_output.clear()
        self.log_output.append("--- Vergleichsergebnisse ---")
        for entry in self.full_results:
            issues = entry['issues']
            if filter_type == "Zu wenig" and not any('Zu wenig' in i for i in issues):
                continue
            if filter_type == "Zu viel" and not any('Zu viel' in i for i in issues):
                continue
            if filter_type == "AAO fehlt" and not any('AAO fehlt' in i for i in issues):
                continue
            if not issues and filter_type != "Alle":
                continue

            if issues:
                self.log_output.append(f"Einsatz {entry['name']}:")
                for issue in issues:
                    self.log_output.append(f"  - {issue}")
        self.log_output.append("\nFertig.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(200, 200, 200))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
