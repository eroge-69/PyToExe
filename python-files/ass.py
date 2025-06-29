import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QCheckBox, QListWidget, QMessageBox, QGroupBox, QSizePolicy,
    QMenu, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt

SAVE_FOLDER = "auto_javitasok"


class AutoJavitasApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧰 Autók-Nyilvántartás")
        self.setFixedSize(800, 580)
        self.init_ui()
        self.setStyleSheet(self.stylesheet())

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)

        main_layout.addWidget(self._label("🚗 Autó márka:"))
        self.auto_input = QComboBox()
        self.auto_input.addItems([
            "Audi", "Abarth", "Acura", "Alfa Romeo", "Alpina", "Alpina", "Aston Martin", "Bentley",
    "BMW", "Bugatti", "Buick", "Cadillac", "Chevrolet", "Chrysler", "Citroën", "Dacia",
    "Daewoo", "Daihatsu", "Dodge", "DS Automobiles", "Ferrari", "Fiat", "Fisker", "Ford",
    "Genesis", "GMC", "Honda", "Hummer", "Hyundai", "Infiniti", "Isuzu", "Iveco", "Jaguar",
    "Jeep", "Kia", "Koenigsegg", "Lada", "Lamborghini", "Lancia", "Land Rover", "Lexus",
    "Lincoln", "Lotus", "Maserati", "Mazda", "McLaren", "Mercedes-Benz", "Mini", "Mitsubishi",
    "Nissan", "Opel", "Pagani", "Peugeot", "Pontiac", "Polestar", "Porsche", "Ram", "Renault",
    "Rolls-Royce", "Saab", "Saturn", "Scion", "Seat", "Škoda", "Smart", "SsangYong", "Subaru",
    "Suzuki", "Tata", "Tesla", "Toyota", "Vauxhall", "Volkswagen", "Volvo", "Westfield",
    "Zotye", "Yamaha", "Mahindra", "BYD", "Great Wall", "Lucid", "Rivian", "Foton",
    "Chery", "Geely", "BAIC", "Dongfeng", "JAC Motors", "Haval", "NIO", "XPeng",
    "VinFast", "Baojun", "Wuling", "Togg", "Sehol", "Zhidou", "Arcfox", "Fisker",
    "CUPRA", "Genesis", "Vespa (Piaggio)", "GMC", "Ram Trucks", "Isuzu", "Dodge", "Mopar",
    "Lucid Motors", "Rimac", "KTM", "Morgan", "Troller", "Hennessey", "Rezvani",
    "Ginetta", "BAC", "Caterham", "Ariel", "DeLorean", "Dodge", "Eicher Motors",
    "Fisker", "Polestar", "Smart", "SsangYong", "Tesla"
        ])
        self.auto_input.setFixedHeight(22)
        main_layout.addWidget(self.auto_input)

        tipus_ev_layout = QHBoxLayout()

        self.tipus_input = QLineEdit()
        self.tipus_input.setPlaceholderText("Autó típus . . .")
        self.tipus_input.setFixedHeight(22)
        tipus_ev_layout.addWidget(self.tipus_input)

        self.evjarat_combo = QComboBox()
        self.evjarat_combo.setFixedHeight(22)
        self.evjarat_combo.setEditable(True)  # Ezzel engedélyezed a kézi beírást
        self.evjarat_combo.addItems([str(ev) for ev in range(1970, 2031)])
        tipus_ev_layout.addWidget(self.evjarat_combo)

        main_layout.addLayout(tipus_ev_layout)

        main_layout.addWidget(self._label("𝄃𝄃𝄂 Alvázszám (VIN):"))
        self.alvaz_input = QLineEdit()
        self.alvaz_input.setFixedHeight(22)
        main_layout.addWidget(self.alvaz_input)

        main_layout.addWidget(self._label("⏲ KM állás:"))
        self.kmallas_input = QLineEdit()
        self.kmallas_input.setFixedHeight(22)
        self.kmallas_input.setValidator(QIntValidator(0, 10000000))
        main_layout.addWidget(self.kmallas_input)

        main_layout.addWidget(self._label("🛠️ Javítások listája:"))
        self.javitas_input = QTextEdit()
        self.javitas_input.setFixedHeight(34)
        self.javitas_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(self.javitas_input)

        main_layout.addWidget(self._label("Általános ellenőrzési pontok:"))
        self.checkboxes = {}
        check_group = QGroupBox()
        check_layout = QHBoxLayout()
        check_layout.setSpacing(10)
        check_layout.setContentsMargins(5, 5, 5, 5)

        opciok = [
            "💡Fények", "🛢️Folyadékok", "🚘Ablaktörlők", "🚅Ablakemelők", "⚡️Akksicsere", "🚿Motormosás", "✨ LámpaPolír"
        ]
        for nev in opciok:
            cb = QCheckBox(nev)
            cb.setStyleSheet("font-size:11px;")
            self.checkboxes[nev] = cb
            check_layout.addWidget(cb)

        check_group.setLayout(check_layout)
        main_layout.addWidget(check_group)

        self.akksi_input = QLineEdit()
        self.akksi_input.setPlaceholderText("Akksi erősség (pl. 60Ah)")
        self.akksi_input.setFixedHeight(22)
        self.akksi_input.setVisible(False)
        main_layout.addWidget(self.akksi_input)
        self.checkboxes["⚡️Akksicsere"].stateChanged.connect(self.akksi_mezo_megjelenitese)

        main_layout.addWidget(self._label("📝 Megjegyzés:"))
        self.megjegyzes_input = QTextEdit()
        self.megjegyzes_input.setFixedHeight(34)
        main_layout.addWidget(self.megjegyzes_input)

        main_layout.addWidget(self._label("🔍 Keresés (alvázszám, típus):"))
        self.kereso_input = QLineEdit()
        self.kereso_input.setPlaceholderText("🔍︎ Keresés az adatbázisban . . .")
        self.kereso_input.setFixedHeight(22)
        self.kereso_input.textChanged.connect(self.kereses)
        main_layout.addWidget(self.kereso_input)

        self.lista = QListWidget()
        self.lista.setFixedHeight(80)
        self.lista.itemClicked.connect(self.fajl_megjelenites)
        self.lista.itemDoubleClicked.connect(self.fajl_dupla_kattintas_megjelenites)
        self.lista.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lista.customContextMenuRequested.connect(self.fajl_context_menu)
        self.lista.setVisible(False)
        main_layout.addWidget(self.lista)

        main_layout.addWidget(self._label("📂 Fájl tartalma:"))
        self.eredmeny_box = QTextEdit()
        self.eredmeny_box.setReadOnly(True)
        self.eredmeny_box.setFixedHeight(90)
        self.eredmeny_box.setVisible(False)
        main_layout.addWidget(self.eredmeny_box)

        alsosor_layout = QHBoxLayout()
        alsosor_layout.setContentsMargins(0, 0, 0, 0)

        copyright_label = QLabel("CreatedBy*𝙕𝙨𝙤𝙡𝙙𝙤𝙨𝙍")
        copyright_label.setStyleSheet("""
            color: #777777;
            font-size: 12px;
            font-style: italic;
            margin-left: 5px;
            margin-bottom: 2px;
        """)
        alsosor_layout.addWidget(copyright_label, 0, Qt.AlignLeft)
        alsosor_layout.addStretch()

        self.ment_btn = QPushButton("💾 Mentés")
        self.ment_btn.setFixedHeight(29)
        self.ment_btn.setMinimumWidth(190)
        kilep_btn = QPushButton("❌ Kilépés")
        kilep_btn.setFixedHeight(29)
        kilep_btn.setMinimumWidth(190)
        self.ment_btn.clicked.connect(self.mentes)
        kilep_btn.clicked.connect(self.close)
        alsosor_layout.addWidget(self.ment_btn)
        alsosor_layout.addWidget(kilep_btn)

        main_layout.addLayout(alsosor_layout)

        os.makedirs(SAVE_FOLDER, exist_ok=True)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: bold; margin-top: 2px; margin-bottom:2px; font-size: 11px;")
        return lbl

    def mentes(self):
        alvaz = self.alvaz_input.text().strip()
        auto = self.auto_input.currentText().strip()
        tipus = self.tipus_input.text().strip()
        evjarat = self.evjarat_combo.currentText()
        kmallas = self.kmallas_input.text().strip()
        javitasok = self.javitas_input.toPlainText().strip()
        megjegyzes = self.megjegyzes_input.toPlainText().strip()

        if not alvaz or not auto:
            QMessageBox.warning(self, "Hiányzó mező", "Az alvázszám és autómárka megadása kötelező.")
            return

        adat = f"Alvázszám: {alvaz}\nAutó márka: {auto}\nTípus: {tipus}\nÉvjárat: {evjarat}\n"
        adat += f"KM állás: {kmallas} km\n\nJavítások:\n{javitasok}\n\n"
        adat += "Ellenőrizve:\n"

        for nev, cb in self.checkboxes.items():
            if cb.isChecked():
                if nev == "Akksicsere":
                    er = self.akksi_input.text().strip()
                    adat += f"- {nev} ✅✅✅ (Erősség: {er})\n" if er else f"- {nev} ✅✅✅\n"
                else:
                    adat += f"- {nev} ✅✅✅\n"
            else:
                adat += f"- {nev} ❌❌❌\n"

        adat += f"\nMegjegyzés:\n{megjegyzes}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        adat += f"\n\nMentés ideje: {now}"

        fajlnev = f"{auto}_{alvaz}.dat".replace(" ", "_")
        utvonal = os.path.join(SAVE_FOLDER, fajlnev)
        with open(utvonal, "w", encoding="utf-8") as f:
            f.write(adat)

        QMessageBox.information(self, "Siker", "Az adatok elmentve.")
        self._torles()
        self.kereso_input.setText("")
        self.kereses()

    def _torles(self):
        self.alvaz_input.clear()
        self.auto_input.setCurrentIndex(0)  # ComboBox visszaállítása az első márkára
        self.kmallas_input.clear()
        self.javitas_input.clear()
        self.megjegyzes_input.clear()
        self.akksi_input.clear()
        self.akksi_input.setVisible(False)
        for cb in self.checkboxes.values():
            cb.setChecked(False)

    def kereses(self):
        szoveg = self.kereso_input.text().strip().lower()
        self.lista.clear()
        self.eredmeny_box.clear()

        if not szoveg:
            self.lista.clear()
            self.lista.setVisible(False)
            self.eredmeny_box.clear()
            self.eredmeny_box.setVisible(False)
            return

        self.lista.setVisible(True)
        self.eredmeny_box.setVisible(True)

        talalatok = []
        for f in os.listdir(SAVE_FOLDER):
            if not f.lower().endswith(".dat"):
                continue

            fajlnev = f.lower()
            utvonal = os.path.join(SAVE_FOLDER, f)
            mod_ido = os.path.getmtime(utvonal)
            mod_datum = datetime.fromtimestamp(mod_ido).strftime("%Y-%m-%d %H:%M")

            if len(szoveg) == 2 or szoveg in fajlnev:
                talalatok.append((mod_ido, f, mod_datum))

        talalatok.sort(reverse=True, key=lambda x: x[0])

        for _, f, datum in talalatok:
            self.lista.addItem(f"{f} ({datum})")

    def fajl_megjelenites(self, item):
        fajlnev = item.text().split(" (")[0]
        self.kivalasztott_fajl = os.path.join(SAVE_FOLDER, fajlnev)
        try:
            with open(self.kivalasztott_fajl, "r", encoding="utf-8") as f:
                self.eredmeny_box.setPlainText(f.read())
        except:
            self.eredmeny_box.setPlainText("Nem sikerült megnyitni a fájlt.")

    def fajl_dupla_kattintas_megjelenites(self, item):
        fajlnev = item.text().split(" (")[0]
        fajl_path = os.path.join(SAVE_FOLDER, fajlnev)
        try:
            with open(fajl_path, "r", encoding="utf-8") as f:
                tartalom = f.read()
        except:
            QMessageBox.warning(self, "Hiba", "Nem sikerült megnyitni a fájlt.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(f"📄 Tartalom: {fajlnev}")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)

        text_box = QTextEdit()
        text_box.setReadOnly(True)
        text_box.setPlainText(tartalom)
        layout.addWidget(text_box)

        gombok = QDialogButtonBox(QDialogButtonBox.Close)
        gombok.rejected.connect(dlg.reject)
        layout.addWidget(gombok)

        dlg.exec_()

    def akksi_mezo_megjelenitese(self, state):
        self.akksi_input.setVisible(state == Qt.Checked)

    def fajl_context_menu(self, position):
        item = self.lista.itemAt(position)
        if not item:
            return

        fajlnev = item.text().split(" (")[0]
        fajl_path = os.path.join(SAVE_FOLDER, fajlnev)

        menu = QMenu()
        szerkeszt = menu.addAction("✏️ Szerkesztés")
        torol = menu.addAction("🗑️ Törlés")
        action = menu.exec_(self.lista.mapToGlobal(position))

        if action == szerkeszt:
            self.szerkeszto_ablak(fajl_path)
        elif action == torol:
            self.fajl_torles(fajl_path)

    def szerkeszto_ablak(self, fajl_path):
        try:
            with open(fajl_path, "r", encoding="utf-8") as f:
                tartalom = f.read()
        except:
            QMessageBox.warning(self, "Hiba", "Nem sikerült megnyitni a fájlt szerkesztésre.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Fájl szerkesztése")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)

        editor = QTextEdit()
        editor.setPlainText(tartalom)
        layout.addWidget(editor)

        gombok = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        gombok.accepted.connect(dlg.accept)
        gombok.rejected.connect(dlg.reject)
        layout.addWidget(gombok)

        if dlg.exec_() == QDialog.Accepted:
            try:
                with open(fajl_path, "w", encoding="utf-8") as f:
                    f.write(editor.toPlainText())
                QMessageBox.information(self, "Siker", "A fájl módosítva lett.")
                self.kereses()
            except:
                QMessageBox.warning(self, "Hiba", "Nem sikerült menteni a fájlt.")

    def fajl_torles(self, fajl_path):
        reply = QMessageBox.question(
            self,
            "Biztos törlés?",
            f"Biztosan törlöd a következő fájlt?\n\n{os.path.basename(fajl_path)}",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                os.remove(fajl_path)
                QMessageBox.information(self, "Törölve", "A fájl törölve lett.")
                self.kereses()
            except:
                QMessageBox.warning(self, "Hiba", "Nem sikerült törölni a fájlt.")

    def stylesheet(self):
        return """
        QWidget {
            font-family: Segoe UI, sans-serif;
            font-size: 11px;
            background-color: #2b2b2b;
            color: #eeeeee;
        }
        QLineEdit, QTextEdit, QListWidget {
            background-color: #3c3f41;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
            font-size: 11px;
        }
        QPushButton {
            background-color: #007acc;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 3px;
            font-size: 11px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QCheckBox {
            padding: 3px;
            font-size: 11px;
        }
        QGroupBox {
            border: 1px solid #444;
            margin-top: 6px;
        }
        QLabel {
            color: #cccccc;
            font-size: 11px;
        }
        QListWidget {
            font-size: 11px;
        }
        """


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoJavitasApp()
    screen = app.primaryScreen().availableGeometry()
    window.move((screen.width() - window.width()) // 2, 20)
    window.show()
    sys.exit(app.exec_())
