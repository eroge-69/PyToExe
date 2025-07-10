```python
import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QLabel, QPushButton, QMessageBox, QComboBox, QTextEdit)
from PyQt5.QtCore import Qt

class BewertungApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Abschlussprüfung Bewertungsbogen - Köche')
        self.setGeometry(100, 100, 1000, 700)
        self.prueflinge = {}  # Dictionary zur Speicherung der Prüflinge und Bewertungen
        self.current_pruefling = None
        self.data_file = "prueflinge.json"
        self.load_data()
        self.initUI()

    def initUI(self):
        # Haupt-Widget und Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Prüfling-Auswahl und Hinzufügen
        pruefling_layout = QHBoxLayout()
        self.pruefling_combo = QComboBox()
        self.pruefling_combo.addItem("Neuer Prüfling auswählen")
        self.pruefling_combo.addItems(self.prueflinge.keys())
        self.pruefling_combo.currentTextChanged.connect(self.load_pruefling_data)
        pruefling_layout.addWidget(QLabel("Prüfling:"))
        pruefling_layout.addWidget(self.pruefling_combo)

        self.pruefling_name_input = QLineEdit()
        self.pruefling_name_input.setPlaceholderText("Neuer Prüfling Name")
        pruefling_layout.addWidget(self.pruefling_name_input)

        add_pruefling_btn = QPushButton("Prüfling hinzufügen")
        add_pruefling_btn.clicked.connect(self.add_pruefling)
        pruefling_layout.addWidget(add_pruefling_btn)

        main_layout.addLayout(pruefling_layout)

        # Tab-Widget für AP Teil 1, AP Teil 2 und Zusammenfassung
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # AP Teil 1
        self.tab1 = QWidget()
        self.tab1_layout = QVBoxLayout()
        self.tab1.setLayout(self.tab1_layout)
        self.tabs.addTab(self.tab1, "AP Teil 1")

        # AP Teil 2
        self.tab2 = QWidget()
        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)
        self.tabs.addTab(self.tab2, "AP Teil 2")

        # Zusammenfassung
        self.tab_summary = QWidget()
        self.tab_summary_layout = QVBoxLayout()
        self.tab_summary.setLayout(self.tab_summary_layout)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.tab_summary_layout.addWidget(self.summary_text)
        self.tabs.addTab(self.tab_summary, "Zusammenfassung")

        # Eingabefelder für AP Teil 1
        self.ap1_inputs = {}
        self.setup_ap1_ui()

        # Eingabefelder für AP Teil 2
        self.ap2_inputs = {}
        self.setup_ap2_ui()

        # Buttons für Berechnen und Zurücksetzen
        button_layout = QHBoxLayout()
        calculate_btn = QPushButton("Ergebnis berechnen")
        calculate_btn.clicked.connect(self.calculate_results)
        reset_btn = QPushButton("Zurücksetzen")
        reset_btn.clicked.connect(self.reset_inputs)
        button_layout.addWidget(calculate_btn)
        button_layout.addWidget(reset_btn)
        main_layout.addLayout(button_layout)

    def setup_ap1_ui(self):
        # Fachgespräch
        self.ap1_inputs['fachgesprach'] = QLineEdit()
        self.ap1_inputs['fachgesprach'].setPlaceholderText("0-100")
        self.ap1_inputs['fachgesprach'].textChanged.connect(self.calculate_results)
        fachgesprach_layout = QFormLayout()
        fachgesprach_layout.addRow("Fachgespräch (Gewichtung: 0.2):", self.ap1_inputs['fachgesprach'])
        self.tab1_layout.addLayout(fachgesprach_layout)

        # Hygiene, Arbeitssicherheit, Umweltschutz
        hygiene_layout = QFormLayout()
        self.ap1_inputs['hygiene'] = QLineEdit()
        self.ap1_inputs['hygiene'].setPlaceholderText("0-100")
        self.ap1_inputs['hygiene'].textChanged.connect(self.calculate_results)
        self.ap1_inputs['arbeitssicherheit'] = QLineEdit()
        self.ap1_inputs['arbeitssicherheit'].setPlaceholderText("0-100")
        self.ap1_inputs['arbeitssicherheit'].textChanged.connect(self.calculate_results)
        self.ap1_inputs['umweltschutz'] = QLineEdit()
        self.ap1_inputs['umweltschutz'].setPlaceholderText("0-100")
        self.ap1_inputs['umweltschutz'].textChanged.connect(self.calculate_results)
        hygiene_layout.addRow("Hygienevorschriften (Faktor: 0.5):", self.ap1_inputs['hygiene'])
        hygiene_layout.addRow("Arbeitssicherheit (Faktor: 0.15):", self.ap1_inputs['arbeitssicherheit'])
        hygiene_layout.addRow("Umweltschutz (Faktor: 0.35):", self.ap1_inputs['umweltschutz'])
        self.tab1_layout.addWidget(QLabel("Hygiene, Arbeitssicherheit, Umweltschutz (Gewichtung: 0.2)"))
        self.tab1_layout.addLayout(hygiene_layout)

        # Vor- & Zubereitung
        zubereitung_layout = QFormLayout()
        self.ap1_inputs['vorspeise'] = QLineEdit()
        self.ap1_inputs['vorspeise'].setPlaceholderText("0-100")
        self.ap1_inputs['vorspeise'].textChanged.connect(self.calculate_results)
        self.ap1_inputs['hauptgang'] = QLineEdit()
        self.ap1_inputs['hauptgang'].setPlaceholderText("0-100")
        self.ap1_inputs['hauptgang'].textChanged.connect(self.calculate_results)
        zubereitung_layout.addRow("Vorspeise/Suppe (Faktor: 0.4):", self.ap1_inputs['vorspeise'])
        zubereitung_layout.addRow("Hauptgang (Faktor: 0.6):", self.ap1_inputs['hauptgang'])
        self.tab1_layout.addWidget(QLabel("Vor- & Zubereitung (Gewichtung: 0.4)"))
        self.tab1_layout.addLayout(zubereitung_layout)

        # Präsentation
        praesentation_layout = QFormLayout()
        self.ap1_inputs['praesentation_vorspeise'] = QLineEdit()
        self.ap1_inputs['praesentation_vorspeise'].setPlaceholderText("0-100")
        self.ap1_inputs['praesentation_vorspeise'].textChanged.connect(self.calculate_results)
        self.ap1_inputs['praesentation_hauptgang'] = QLineEdit()
        self.ap1_inputs['praesentation_hauptgang'].setPlaceholderText("0-100")
        self.ap1_inputs['praesentation_hauptgang'].textChanged.connect(self.calculate_results)
        praesentation_layout.addRow("Vorspeise/Suppe (Faktor: 0.4):", self.ap1_inputs['praesentation_vorspeise'])
        praesentation_layout.addRow("Hauptgang (Faktor: 0.6):", self.ap1_inputs['praesentation_hauptgang'])
        self.tab1_layout.addWidget(QLabel("Präsentation (Gewichtung: 0.1)"))
        self.tab1_layout.addLayout(praesentation_layout)

        # Geschmack
        geschmack_layout = QFormLayout()
        self.ap1_inputs['geschmack_vorspeise'] = QLineEdit()
        self.ap1_inputs['geschmack_vorspeise'].setPlaceholderText("0-100")
        self.ap1_inputs['geschmack_vorspeise'].textChanged.connect(self.calculate_results)
        self.ap1_inputs['geschmack_hauptgang'] = QLineEdit()
        self.ap1_inputs['geschmack_hauptgang'].setPlaceholderText("0-100")
        self.ap1_inputs['geschmack_hauptgang'].textChanged.connect(self.calculate_results)
        geschmack_layout.addRow("Vorspeise/Suppe (Faktor: 0.4):", self.ap1_inputs['geschmack_vorspeise'])
        geschmack_layout.addRow("Hauptgang (Faktor: 0.6):", self.ap1_inputs['geschmack_hauptgang'])
        self.tab1_layout.addWidget(QLabel("Geschmack (Gewichtung: 0.1)"))
        self.tab1_layout.addLayout(geschmack_layout)

        # Gesamtergebnis
        self.ap1_result_label = QLabel("Gesamtergebnis: 0.00")
        self.tab1_layout.addWidget(self.ap1_result_label)

    def setup_ap2_ui(self):
        # Arbeitsablaufplan
        self.ap2_inputs['arbeitsablaufplan'] = QLineEdit()
        self.ap2_inputs['arbeitsablaufplan'].setPlaceholderText("0-100")
        self.ap2_inputs['arbeitsablaufplan'].textChanged.connect(self.calculate_results)
        arbeitsablauf_layout = QFormLayout()
        arbeitsablauf_layout.addRow("Arbeitsablaufplan (Gewichtung: 0.1):", self.ap2_inputs['arbeitsablaufplan'])
        self.tab2_layout.addLayout(arbeitsablauf_layout)

        # Fachgespräch
        self.ap2_inputs['fachgesprach'] = QLineEdit()
        self.ap2_inputs['fachgesprach'].setPlaceholderText("0-100")
        self.ap2_inputs['fachgesprach'].textChanged.connect(self.calculate_results)
        fachgesprach_layout = QFormLayout()
        fachgesprach_layout.addRow("Fachgespräch (Gewichtung: 0.1):", self.ap2_inputs['fachgesprach'])
        self.tab2_layout.addLayout(fachgesprach_layout)

        # Hygiene, Arbeitssicherheit, Umweltschutz
        hygiene_layout = QFormLayout()
        self.ap2_inputs['hygiene'] = QLineEdit()
        self.ap2_inputs['hygiene'].setPlaceholderText("0-100")
        self.ap2_inputs['hygiene'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['arbeitssicherheit'] = QLineEdit()
        self.ap2_inputs['arbeitssicherheit'].setPlaceholderText("0-100")
        self.ap2_inputs['arbeitssicherheit'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['umweltschutz'] = QLineEdit()
        self.ap2_inputs['umweltschutz'].setPlaceholderText("0-100")
        self.ap2_inputs['umweltschutz'].textChanged.connect(self.calculate_results)
        hygiene_layout.addRow("Hygienevorschriften (Faktor: 0.5):", self.ap2_inputs['hygiene'])
        hygiene_layout.addRow("Arbeitssicherheit (Faktor: 0.15):", self.ap2_inputs['arbeitssicherheit'])
        hygiene_layout.addRow("Umweltschutz (Faktor: 0.35):", self.ap2_inputs['umweltschutz'])
        self.tab2_layout.addWidget(QLabel("Hygiene, Arbeitssicherheit, Umweltschutz (Gewichtung: 0.2)"))
        self.tab2_layout.addLayout(hygiene_layout)

        # Vor- & Zubereitung
        zubereitung_layout = QFormLayout()
        self.ap2_inputs['vorspeise'] = QLineEdit()
        self.ap2_inputs['vorspeise'].setPlaceholderText("0-100")
        self.ap2_inputs['vorspeise'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['hauptgang'] = QLineEdit()
        self.ap2_inputs['hauptgang'].setPlaceholderText("0-100")
        self.ap2_inputs['hauptgang'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['dessert'] = QLineEdit()
        self.ap2_inputs['dessert'].setPlaceholderText("0-100")
        self.ap2_inputs['dessert'].textChanged.connect(self.calculate_results)
        zubereitung_layout.addRow("Vorspeise (Faktor: 0.3):", self.ap2_inputs['vorspeise'])
        zubereitung_layout.addRow("Hauptgang (Faktor: 0.4):", self.ap2_inputs['hauptgang'])
        zubereitung_layout.addRow("Dessert (Faktor: 0.3):", self.ap2_inputs['dessert'])
        self.tab2_layout.addWidget(QLabel("Vor- & Zubereitung (Gewichtung: 0.4)"))
        self.tab2_layout.addLayout(zubereitung_layout)

        # Präsentation
        praesentation_layout = QFormLayout()
        self.ap2_inputs['praesentation_vorspeise'] = QLineEdit()
        self.ap2_inputs['praesentation_vorspeise'].setPlaceholderText("0-100")
        self.ap2_inputs['praesentation_vorspeise'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['praesentation_hauptgang'] = QLineEdit()
        self.ap2_inputs['praesentation_hauptgang'].setPlaceholderText("0-100")
        self.ap2_inputs['praesentation_hauptgang'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['praesentation_dessert'] = QLineEdit()
        self.ap2_inputs['praesentation_dessert'].setPlaceholderText("0-100")
        self.ap2_inputs['praesentation_dessert'].textChanged.connect(self.calculate_results)
        praesentation_layout.addRow("Vorspeise (Faktor: 0.3):", self.ap2_inputs['praesentation_vorspeise'])
        praesentation_layout.addRow("Hauptgang (Faktor: 0.4):", self.ap2_inputs['praesentation_hauptgang'])
        praesentation_layout.addRow("Dessert (Faktor: 0.3):", self.ap2_inputs['praesentation_dessert'])
        self.tab2_layout.addWidget(QLabel("Präsentation (Gewichtung: 0.1)"))
        self.tab2_layout.addLayout(praesentation_layout)

        # Geschmack
        geschmack_layout = QFormLayout()
        self.ap2_inputs['geschmack_vorspeise'] = QLineEdit()
        self.ap2_inputs['geschmack_vorspeise'].setPlaceholderText("0-100")
        self.ap2_inputs['geschmack_vorspeise'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['geschmack_hauptgang'] = QLineEdit()
        self.ap2_inputs['geschmack_hauptgang'].setPlaceholderText("0-100")
        self.ap2_inputs['geschmack_hauptgang'].textChanged.connect(self.calculate_results)
        self.ap2_inputs['geschmack_dessert'] = QLineEdit()
        self.ap2_inputs['geschmack_dessert'].setPlaceholderText("0-100")
        self.ap2_inputs['geschmack_dessert'].textChanged.connect(self.calculate_results)
        geschmack_layout.addRow("Vorspeise (Faktor: 0.3):", self.ap2_inputs['geschmack_vorspeise'])
        geschmack_layout.addRow("Hauptgang (Faktor: 0.4):", self.ap2_inputs['geschmack_hauptgang'])
        geschmack_layout.addRow("Dessert (Faktor: 0.3):", self.ap2_inputs['geschmack_dessert'])
        self.tab2_layout.addWidget(QLabel("Geschmack (Gewichtung: 0.1)"))
        self.tab2_layout.addLayout(geschmack_layout)

        # Gesamtergebnis
        self.ap2_result_label = QLabel("Gesamtergebnis: 0.00")
        self.tab2_layout.addWidget(self.ap2_result_label)

    def add_pruefling(self):
        name = self.pruefling_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie einen Namen ein.")
            return
        if name in self.prueflinge:
            QMessageBox.warning(self, "Fehler", "Prüfling existiert bereits.")
            return
        self.prueflinge[name] = {
            "ap1": {key: "" for key in self.ap1_inputs},
            "ap2": {key: "" for key in self.ap2_inputs},
            "results": {"ap1": 0.0, "ap2": 0.0}
        }
        self.pruefling_combo.addItem(name)
        self.pruefling_combo.setCurrentText(name)
        self.pruefling_name_input.clear()
        self.save_data()

    def load_pruefling_data(self, name):
        if name == "Neuer Prüfling auswählen":
            self.current_pruefling = None
            self.reset_inputs()
            return
        self.current_pruefling = name
        pruefling_data = self.prueflinge.get(name, {})
        # AP Teil 1
        for key, input_field in self.ap1_inputs.items():
            input_field.setText(pruefling_data.get("ap1", {}).get(key, ""))
        # AP Teil 2
        for key, input_field in self.ap2_inputs.items():
            input_field.setText(pruefling_data.get("ap2", {}).get(key, ""))
        self.calculate_results()

    def save_data(self):
        if self.current_pruefling:
            self.prueflinge[self.current_pruefling]["ap1"] = {key: input_field.text() for key, input_field in self.ap1_inputs.items()}
            self.prueflinge[self.current_pruefling]["ap2"] = {key: input_field.text() for key, input_field in self.ap2_inputs.items()}
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.prueflinge, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {str(e)}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.prueflinge = json.load(f)
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Laden: {str(e)}")

    def validate_input(self, value):
        try:
            num = float(value)
            return 0 <= num <= 100
        except ValueError:
            return False

    def calculate_results(self):
        if not self.current_pruefling:
            return

        ap1_total = 0.0
        ap2_total = 0.0

        # AP Teil 1 Berechnungen
        # Fachgespräch
        fachgesprach = self.ap1_inputs['fachgesprach'].text()
        if self.validate_input(fachgesprach):
            ap1_total += float(fachgesprach) * 0.2

        # Hygiene, Arbeitssicherheit, Umweltschutz
        hygiene_sum = 0.0
        if self.validate_input(self.ap1_inputs['hygiene'].text()):
            hygiene_sum += float(self.ap1_inputs['hygiene'].text()) * 0.5
        if self.validate_input(self.ap1_inputs['arbeitssicherheit'].text()):
            hygiene_sum += float(self.ap1_inputs['arbeitssicherheit'].text()) * 0.15
        if self.validate_input(self.ap1_inputs['umweltschutz'].text()):
            hygiene_sum += float(self.ap1_inputs['umweltschutz'].text()) * 0.35
        ap1_total += hygiene_sum * 0.2

        # Vor- & Zubereitung
        zubereitung_sum = 0.0
        if self.validate_input(self.ap1_inputs['vorspeise'].text()):
            zubereitung_sum += float(self.ap1_inputs['vorspeise'].text()) * 0.4
        if self.validate_input(self.ap1_inputs['hauptgang'].text()):
            zubereitung_sum += float(self.ap1_inputs['hauptgang'].text()) * 0.6
        ap1_total += zubereitung_sum * 0.4

        # Präsentation
        praesentation_sum = 0.0
        if self.validate_input(self.ap1_inputs['praesentation_vorspeise'].text()):
            praesentation_sum += float(self.ap1_inputs['praesentation_vorspeise'].text()) * 0.4
        if self.validate_input(self.ap1_inputs['praesentation_hauptgang'].text()):
            praesentation_sum += float(self.ap1_inputs['praesentation_hauptgang'].text()) * 0.6
        ap1_total += praesentation_sum * 0.1

        # Geschmack
        geschmack_sum = 0.0
        if self.validate_input(self.ap1_inputs['geschmack_vorspeise'].text()):
            geschmack_sum += float tagli self.ap1_inputs['geschmack_vorspeise'].text()) * 0.4
        if self.validate_input(self.ap1_inputs['geschmack_hauptgang'].text()):
            geschmack_sum += float(self.ap1_inputs['geschmack_hauptgang'].text()) * 0.6
        ap1_total += geschmack_sum * 0.1

        self.ap1_result_label.setText(f"Gesamtergebnis: {ap1_total:.2f}")

        # AP Teil 2 Berechnungen
        # Arbeitsablaufplan
        arbeitsablauf = self.ap2_inputs['arbeitsablaufplan'].text()
        if self.validate_input(arbeitsablauf):
            ap2_total += float(arbeitsablauf) * 0.1

        # Fachgespräch
        fachgesprach = self.ap2_inputs['fachgesprach'].text()
        if self.validate_input(fachgesprach):
            ap2_total += float(fachgesprach) * 0.1

        # Hygiene, Arbeitssicherheit, Umweltschutz
        hygiene_sum = 0.0
        if self.validate_input(self.ap2_inputs['hygiene'].text()):
            hygiene_sum += float(self.ap2_inputs['hygiene'].text()) * 0.5
        if self.validate_input(self.ap2_inputs['arbeitssicherheit'].text()):
            hygiene_sum += float(self.ap2_inputs['arbeitssicherheit'].text()) * 0.15
        if self.validate_input(self.ap2_inputs['umweltschutz'].text()):
            hygiene_sum += float(self.ap2_inputs['umweltschutz'].text()) * 0.35
        ap2_total += hygiene_sum * 0.2

        # Vor- & Zubereitung
        zubereitung_sum = 0.0
        if self.validate_input(self.ap2_inputs['vorspeise'].text()):
            zubereitung_sum += float(self.ap2_inputs['vorspeise'].text()) * 0.3
        if self.validate_input(self.ap2_inputs['hauptgang'].text()):
            zubereitung_sum += float(self.ap2_inputs['hauptgang'].text()) * 0.4
        if self.validate_input(self.ap2_inputs['dessert'].text()):
            zubereitung_sum += float(self.ap2_inputs['dessert'].text()) * 0.3
        ap2_total += zubereitung_sum * 0.4

        # Präsentation
        praesentation_sum = 0.0
        if self.validate_input(self.ap2_inputs['praesentation_vorspeise'].text()):
            praesentation_sum += float(self.ap2_inputs['praesentation_vorspeise'].text()) * 0.3
        if self.validate_input(self.ap2_inputs['praesentation_hauptgang'].text()):
            praesentation_sum += float(self.ap2_inputs['praesentation_hauptgang'].text()) * 0.4
        if self.validate_input(self.ap2_inputs['praesentation_dessert'].text()):
            praesentation_sum += float(self.ap2_inputs['praesentation_dessert'].text()) * 0.3
        ap2_total += praesentation_sum * 0.1

        # Geschmack
        geschmack_sum = 0.0
        if self.validate_input(self.ap2_inputs['geschmack_vorspeise'].text()):
            geschmack_sum += float(self.ap2_inputs['geschmack_vorspeise'].text()) * 0.3
        if self.validate_input(self.ap2_inputs['geschmack_hauptgang'].text()):
            geschmack_sum += float(self.ap2_inputs['geschmack_hauptgang'].text()) * 0.4
        if self.validate_input(self.ap2_inputs['geschmack_dessert'].text()):
            geschmack_sum += float(self.ap2_inputs['geschmack_dessert'].text()) * 0.3
        ap2_total += geschmack_sum * 0.1

        self.ap2_result_label.setText(f"Gesamtergebnis: {ap2_total:.2f}")

        # Zusammenfassung
        summary = f"Zusammenfassung für {self.current_pruefling}\n\n"
        summary += "AP Teil 1:\n"
        summary += f"  Fachgespräch: {self.ap1_inputs['fachgesprach'].text() or '0'} (Gewichtung: 0.2)\n"
        summary += "  Hygiene, Arbeitssicherheit, Umweltschutz:\n"
        summary += f"    Hygienevorschriften: {self.ap1_inputs['hygiene'].text() or '0'} (Faktor: 0.5)\n"
        summary += f"    Arbeitssicherheit: {self.ap1_inputs['arbeitssicherheit'].text() or '0'} (Faktor: 0.15)\n"
        summary += f"    Umweltschutz: {self.ap1_inputs['umweltschutz'].text() or '0'} (Faktor: 0.35)\n"
        summary += "  Vor- & Zubereitung:\n"
        summary += f"    Vorspeise/Suppe: {self.ap1_inputs['vorspeise'].text() or '0'} (Faktor: 0.4)\n"
        summary += f"    Hauptgang: {self.ap1_inputs['hauptgang'].text() or '0'} (Faktor: 0.6)\n"
        summary += "  Präsentation:\n"
        summary += f"    Vorspeise/Suppe: {self.ap1_inputs['praesentation_vorspeise'].text() or '0'} (Faktor: 0.4)\n"
        summary += f"    Hauptgang: {self.ap1_inputs['praesentation_hauptgang'].text() or '0'} (Faktor: 0.6)\n"
        summary += "  Geschmack:\n"
        summary += f"    Vorspeise/Suppe: {self.ap1_inputs['geschmack_vorspeise'].text() or '0'} (Faktor: 0.4)\n"
        summary += f"    Hauptgang: {self.ap1_inputs['geschmack_hauptgang'].text() or '0'} (Faktor: 0.6)\n"
        summary += f"\nGesamtergebnis AP Teil 1: {ap1_total:.2f}\n\n"

        summary += "AP Teil 2:\n"
        summary += f"  Arbeitsablaufplan: {self.ap2_inputs['arbeitsablaufplan'].text() or '0'} (Gewichtung: 0.1)\n"
        summary += f"  Fachgespräch: {self.ap2_inputs['fachgesprach'].text() or '0'} (Gewichtung: 0.1)\n"
        summary += "  Hygiene, Arbeitssicherheit, Umweltschutz:\n"
        summary += f"    Hygienevorschriften: {self.ap2_inputs['hygiene'].text() or '0'} (Faktor: 0.5)\n"
        summary += f"    Arbeitssicherheit: {self.ap2_inputs['arbeitssicherheit'].text() or '0'} (Faktor: 0.15)\n"
        summary += f"    Umweltschutz: {self.ap2_inputs['umweltschutz'].textಮ

System: * Today's date and time is 09:53 AM CEST on Thursday, July 10, 2025.