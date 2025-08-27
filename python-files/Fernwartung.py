import json
import os
import sys
import uuid
import shutil
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLineEdit, QComboBox, QCheckBox, QTextEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QLabel, QFormLayout,
    QAbstractItemView, QAction
)

APP_NAME = "RemoteLauncher"
IS_WINDOWS = sys.platform.startswith("win")

def appdata_path() -> str:
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path

CONN_FILE = os.path.join(appdata_path(), "connections.json")
SETTINGS_FILE = os.path.join(appdata_path(), "settings.json")

# Templates të paracaktuara (mund të anashkalohen për çdo lidhje me "Befehls-Template")
DEFAULT_TEMPLATES = {
    "RDP": "mstsc /v:{address}",
    "VNC": "vncviewer.exe {address}"  # për UltraVNC mund: vncviewer.exe {address} -password {password}
    # TeamViewer trajtohet veçmas që të përdoret path-i i saktë i exe
}

@dataclass
class Connection:
    id: str
    name: str
    type: str            # "RDP" | "TeamViewer" | "VNC"
    address_or_id: str   # IP/Host ose TeamViewer-ID
    username: str = ""
    password: str = ""
    template: str = ""

class SettingsStore:
    def __init__(self, path: str):
        self.path = path
        self.data = {"teamviewer_path": ""}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {"teamviewer_path": ""}
        else:
            self.save()

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(None, "Speichern fehlgeschlagen",
                                 f"Einstellungen konnten nicht gespeichert werden:\n{e}")

class ConnectionStore:
    def __init__(self, path: str):
        self.path = path
        self.connections: List[Connection] = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self.connections = [Connection(**c) for c in raw]
            except Exception as e:
                QMessageBox.warning(None, "Laden fehlgeschlagen",
                                    f"Konfiguration konnte nicht gelesen werden:\n{e}")
                self.connections = []
        else:
            self.connections = []
            self.save()

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([asdict(c) for c in self.connections], f, indent=2, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(None, "Speichern fehlgeschlagen",
                                 f"Konfiguration konnte nicht gespeichert werden:\n{e}")

    def add(self, conn: Connection):
        self.connections.append(conn)
        self.save()

    def update(self, conn: Connection):
        for i, c in enumerate(self.connections):
            if c.id == conn.id:
                self.connections[i] = conn
                self.save()
                return
        self.add(conn)

    def delete(self, conn_id: str):
        self.connections = [c for c in self.connections if c.id != conn_id]
        self.save()

def set_dark_palette(app: QApplication):
    app.setStyle("Fusion")
    p = QPalette()
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    p.setColor(QPalette.WindowText, Qt.white)
    p.setColor(QPalette.Base, QColor(35, 35, 35))
    p.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipBase, Qt.white)
    p.setColor(QPalette.ToolTipText, Qt.white)
    p.setColor(QPalette.Text, Qt.white)
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.ButtonText, Qt.white)
    p.setColor(QPalette.BrightText, Qt.red)
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(p)

# ---- Zbulim automatik i TeamViewer.exe ----
def detect_teamviewer_path() -> Optional[str]:
    p = shutil.which("TeamViewer.exe")
    if p and os.path.isfile(p):
        return p

    if IS_WINDOWS:
        try:
            import winreg
            for root in (winreg.HKEY_LOCAL_MACHINE, ):
                for subkey in (
                    r"SOFTWARE\TeamViewer",
                    r"SOFTWARE\WOW6432Node\TeamViewer",
                ):
                    try:
                        with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ) as k:
                            for value_name in ("InstallationDirectory", "InstallLocation", "InstallDir", "Path"):
                                try:
                                    val, _ = winreg.QueryValueEx(k, value_name)
                                    candidate = os.path.join(val, "TeamViewer.exe")
                                    if os.path.isfile(candidate):
                                        return candidate
                                except FileNotFoundError:
                                    pass
                    except FileNotFoundError:
                        continue
        except Exception:
            pass

    for c in [
        r"C:\Program Files\TeamViewer\TeamViewer.exe",
        r"C:\Program Files (x86)\TeamViewer\TeamViewer.exe",
    ]:
        if os.path.isfile(c):
            return c
    return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote Launcher")
        self.setMinimumSize(QSize(1000, 600))

        self.settings = SettingsStore(SETTINGS_FILE)
        if not self.settings.data.get("teamviewer_path") or not os.path.isfile(self.settings.data.get("teamviewer_path", "")):
            auto = detect_teamviewer_path()
            if auto:
                self.settings.data["teamviewer_path"] = auto
                self.settings.save()

        self.store = ConnectionStore(CONN_FILE)

        splitter = QSplitter()
        left = QWidget()
        right = QWidget()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        self.setCentralWidget(splitter)

        # ---- Left UI ----
        lyt_left = QVBoxLayout(left)

        quick_box = QGroupBox("Schnellstart")
        quick_lyt = QHBoxLayout(quick_box)
        self.quick_combo = QComboBox()
        self.refresh_quick_combo()
        self.btn_quick_start = QPushButton("Starten")
        self.btn_quick_start.clicked.connect(self.quick_start)
        quick_lyt.addWidget(self.quick_combo, 1)
        quick_lyt.addWidget(self.btn_quick_start)
        lyt_left.addWidget(quick_box)

        filter_box = QGroupBox("Verbindungen")
        filter_lyt = QVBoxLayout(filter_box)
        top_filter_lyt = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Suche nach Name / Typ / Adresse…")
        self.search_edit.textChanged.connect(self.apply_filter)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Alle", "RDP", "TeamViewer", "VNC"])
        self.type_filter.currentIndexChanged.connect(self.apply_filter)
        top_filter_lyt.addWidget(self.search_edit, 1)
        top_filter_lyt.addWidget(self.type_filter)
        filter_lyt.addLayout(top_filter_lyt)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Typ", "Adresse/ID", "Benutzer"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self.on_table_selection)
        filter_lyt.addWidget(self.table, 1)

        btns = QHBoxLayout()
        self.btn_new = QPushButton("Neu")
        self.btn_save = QPushButton("Speichern")
        self.btn_delete = QPushButton("Löschen")
        self.btn_connect = QPushButton("Verbinden")
        self.btn_preview = QPushButton("Befehl anzeigen")
        self.btn_new.clicked.connect(self.new_connection)
        self.btn_save.clicked.connect(self.save_connection)
        self.btn_delete.clicked.connect(self.delete_connection)
        self.btn_connect.clicked.connect(self.connect_selected)
        self.btn_preview.clicked.connect(self.preview_command)
        btns.addWidget(self.btn_new)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_delete)
        btns.addStretch(1)
        btns.addWidget(self.btn_preview)
        btns.addWidget(self.btn_connect)
        filter_lyt.addLayout(btns)

        lyt_left.addWidget(filter_box, 1)

        # ---- Right UI ----
        editor_box = QGroupBox("Verbindung bearbeiten / anlegen")
        form = QFormLayout(editor_box)
        self.edit_id_hidden = QLabel("")
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["RDP", "TeamViewer", "VNC"])
        self.type_combo.currentIndexChanged.connect(self.update_address_label)
        self.address_label = QLabel("Adresse (IP/Host)")
        self.address_edit = QLineEdit()
        self.user_edit = QLineEdit()
        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.show_pw = QCheckBox("Passwort anzeigen")
        self.show_pw.toggled.connect(lambda s: self.pass_edit.setEchoMode(
            QLineEdit.Normal if s else QLineEdit.Password))
        self.tpl_edit = QLineEdit()
        self.tpl_edit.setPlaceholderText("Optional: eigenes Befehls-Template. Leer = Standard")
        self.tpl_hint = QLabel("Hinweis: Platzhalter {address}/{id}, {username}, {password} werden ersetzt.")
        self.tpl_hint.setStyleSheet("color: #aaa; font-size: 11px;")

        form.addRow("Name*", self.name_edit)
        form.addRow("Typ*", self.type_combo)
        form.addRow(self.address_label, self.address_edit)
        form.addRow("Benutzer", self.user_edit)
        form.addRow("Passwort", self.pass_edit)
        form.addRow("", self.show_pw)
        form.addRow("Befehls-Template", self.tpl_edit)
        form.addRow("", self.tpl_hint)

        warn = QLabel("⚠️ Hinweis: Passwörter werden im Klartext in der Konfigurationsdatei gespeichert.")
        warn.setStyleSheet("color: #ffcc66;")
        form.addRow("", warn)

        lyt_right = QVBoxLayout(right)
        lyt_right.addWidget(editor_box)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Protokoll…")
        lyt_right.addWidget(self.log, 1)

        self.populate_table()

        # Menus
        menu_file = self.menuBar().addMenu("Datei")
        act_export = QAction("Exportieren…", self)
        act_import = QAction("Importieren…", self)
        act_export.triggered.connect(self.export_json)
        act_import.triggered.connect(self.import_json)
        menu_file.addAction(act_export)
        menu_file.addAction(act_import)

        menu_settings = self.menuBar().addMenu("Einstellungen")
        act_set_tv = QAction("TeamViewer.exe wählen…", self)
        act_set_tv.triggered.connect(self.choose_teamviewer_path)
        menu_settings.addAction(act_set_tv)

        self.new_connection()

        if not self.get_teamviewer_exe():
            self.log.append("⚠️ TeamViewer.exe nicht gefunden. Gehe zu Einstellungen → TeamViewer.exe wählen…")

    # ---------- helpers ----------
    def log_msg(self, msg: str):
        self.log.append(msg)

    def refresh_quick_combo(self):
        self.quick_combo.clear()
        self.quick_combo.addItems([c.name for c in self.store.connections])

    def apply_filter(self):
        text = self.search_edit.text().strip().lower()
        tfilter = self.type_filter.currentText()
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().lower()
            typ = self.table.item(row, 1).text()
            addr = self.table.item(row, 2).text().lower()
            user = self.table.item(row, 3).text().lower()
            ok_text = (text in name) or (text in addr) or (text in user) or (text in typ.lower())
            ok_type = (tfilter == "Alle") or (typ == tfilter)
            self.table.setRowHidden(row, not (ok_text and ok_type))

    def update_address_label(self):
        typ = self.type_combo.currentText()
        self.address_label.setText("TeamViewer-ID" if typ == "TeamViewer" else "Adresse (IP/Host)")
        if typ == "TeamViewer":
            self.tpl_hint.setText("Platzhalter: {id}, {username}, {password}")
        else:
            self.tpl_hint.setText("Platzhalter: {address}, {username}, {password}")

    def populate_table(self):
        self.table.setRowCount(0)
        for c in self.store.connections:
            self.add_row(c)
        self.apply_filter()
        self.refresh_quick_combo()

    def add_row(self, c: Connection):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(c.name))
        self.table.setItem(row, 1, QTableWidgetItem(c.type))
        self.table.setItem(row, 2, QTableWidgetItem(c.address_or_id))
        self.table.setItem(row, 3, QTableWidgetItem(c.username))
        self.table.item(row, 0).setData(Qt.UserRole, c.id)

    def get_selected_id(self) -> Optional[str]:
        sel = self.table.selectedItems()
        return sel[0].data(Qt.UserRole) if sel else None

    def on_table_selection(self):
        cid = self.get_selected_id()
        if not cid:
            return
        c = next((x for x in self.store.connections if x.id == cid), None)
        if not c:
            return
        self.fill_editor(c)

    def fill_editor(self, c: Connection):
        self.edit_id_hidden.setText(c.id)
        self.name_edit.setText(c.name)
        self.type_combo.setCurrentText(c.type)
        self.address_edit.setText(c.address_or_id)
        self.user_edit.setText(c.username)
        self.pass_edit.setText(c.password)
        self.tpl_edit.setText(c.template or "")
        self.update_address_label()

    def new_connection(self):
        self.edit_id_hidden.setText("")
        self.name_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.address_edit.clear()
        self.user_edit.clear()
        self.pass_edit.clear()
        self.tpl_edit.clear()
        self.update_address_label()

    def save_connection(self):
        name = self.name_edit.text().strip()
        typ = self.type_combo.currentText()
        addr = self.address_edit.text().strip()
        if not name or not typ or not addr:
            QMessageBox.warning(self, "Ungültig", "Bitte Name, Typ und Adresse/ID ausfüllen.")
            return
        cid = self.edit_id_hidden.text().strip() or str(uuid.uuid4())
        c = Connection(
            id=cid, name=name, type=typ, address_or_id=addr,
            username=self.user_edit.text().strip(),
            password=self.pass_edit.text(),
            template=self.tpl_edit.text().strip()
        )
        existed = any(x.id == cid for x in self.store.connections)
        self.store.update(c)
        if existed:
            for r in range(self.table.rowCount()):
                if self.table.item(r, 0).data(Qt.UserRole) == cid:
                    self.table.item(r, 0).setText(c.name)
                    self.table.item(r, 1).setText(c.type)
                    self.table.item(r, 2).setText(c.address_or_id)
                    self.table.item(r, 3).setText(c.username)
                    break
        else:
            self.add_row(c)

        self.apply_filter()
        self.refresh_quick_combo()
        self.log_msg(f"💾 Gespeichert: {c.name} ({c.type})")

    def delete_connection(self):
        cid = self.get_selected_id()
        if not cid:
            QMessageBox.information(self, "Keine Auswahl", "Bitte zuerst eine Verbindung auswählen.")
            return
        c = next((x for x in self.store.connections if x.id == cid), None)
        if not c:
            return
        if QMessageBox.question(self, "Löschen bestätigen",
                                f"Verbindung „{c.name}“ wirklich löschen?") == QMessageBox.StandardButton.Yes:
            self.store.delete(cid)
            for r in range(self.table.rowCount()):
                if self.table.item(r, 0).data(Qt.UserRole) == cid:
                    self.table.removeRow(r)
                    break
            self.refresh_quick_combo()
            self.log_msg(f"🗑️ Gelöscht: {c.name}")

    # --- TeamViewer path handling ---
    def choose_teamviewer_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "TeamViewer.exe wählen…", "",
                                              "TeamViewer (TeamViewer.exe);;EXE (*.exe)")
        if not path:
            return
        if not os.path.isfile(path) or not os.path.basename(path).lower().startswith("teamviewer"):
            if QMessageBox.question(self, "Hinweis",
                                    "Die Datei scheint nicht 'TeamViewer.exe' zu sein. Trotzdem verwenden?",
                                    ) != QMessageBox.Yes:
                return
        self.settings.data["teamviewer_path"] = path
        self.settings.save()
        self.log.append(f"✅ TeamViewer.exe gesetzt: {path}")

    def get_teamviewer_exe(self) -> Optional[str]:
        p = self.settings.data.get("teamviewer_path", "")
        if p and os.path.isfile(p):
            return p
        auto = detect_teamviewer_path()
        if auto:
            self.settings.data["teamviewer_path"] = auto
            self.settings.save()
            return auto
        return None

    # --- Connect / Commands ---
    def quick_start(self):
        name = self.quick_combo.currentText()
        c = next((x for x in self.store.connections if x.name == name), None)
        if c:
            self.start_connection(c)
        else:
            QMessageBox.information(self, "Nicht gefunden", "Diese Verbindung existiert nicht mehr.")

    def connect_selected(self):
        cid = self.get_selected_id()
        if not cid:
            QMessageBox.information(self, "Keine Auswahl", "Bitte zuerst eine Verbindung auswählen.")
            return
        c = next((x for x in self.store.connections if x.id == cid), None)
        if c:
            self.start_connection(c)

    def preview_command(self):
        cid = self.get_selected_id()
        if not cid:
            QMessageBox.information(self, "Keine Auswahl", "Bitte zuerst eine Verbindung auswählen.")
            return
        c = next((x for x in self.store.connections if x.id == cid), None)
        if not c:
            return
        cmds = self.build_commands(c, preview=True)
        if not cmds:
            QMessageBox.warning(self, "Vorschau", "Kein Befehl generiert.")
            return
        QMessageBox.information(self, "Befehlsvorschau", "\n\n".join(cmds))

    def build_commands(self, c: Connection, preview: bool = False) -> List[str]:
        cmds: List[str] = []
        mapping = {
            "address": c.address_or_id,
            "id": c.address_or_id,
            "username": c.username,
            "password": c.password
        }

        if c.type == "RDP":
            tpl = c.template.strip() if c.template else DEFAULT_TEMPLATES["RDP"]
            if c.username and c.password and IS_WINDOWS:
                host = c.address_or_id
                cmds.append(f'cmdkey /generic:TERMSRV/{host} /user:{c.username} /pass:{c.password}')
                try:
                    cmds.append(tpl.format(**mapping))
                except Exception:
                    cmds.append(tpl)
            else:
                try:
                    cmds.append(tpl.format(**mapping))
                except Exception:
                    cmds.append(tpl)

        elif c.type == "TeamViewer":
            if c.template.strip():
                tpl = c.template.strip()
                try:
                    cmds.append(tpl.format(**mapping))
                except Exception:
                    cmds.append(tpl)
            else:
                exe = self.get_teamviewer_exe()
                if not exe:
                    QMessageBox.warning(self, "TeamViewer fehlt",
                                        "TeamViewer.exe nicht gefunden. Einstellungen → TeamViewer.exe wählen…")
                    return []
                exe_q = f'"{exe}"'
                if c.password:
                    cmds.append(f'{exe_q} -i {c.address_or_id} -p {c.password}')
                else:
                    cmds.append(f'{exe_q} -i {c.address_or_id}')

        elif c.type == "VNC":
            tpl = c.template.strip() if c.template else DEFAULT_TEMPLATES["VNC"]
            try:
                cmds.append(tpl.format(**mapping))
            except Exception:
                cmds.append(tpl)
        else:
            if c.template.strip():
                tpl = c.template.strip()
                try:
                    cmds.append(tpl.format(**mapping))
                except Exception:
                    cmds.append(tpl)

        if preview:
            return cmds
        return [x for x in cmds if x.strip()]

    def start_connection(self, c: Connection):
        if not IS_WINDOWS and c.type == "RDP":
            QMessageBox.warning(self, "Nicht Windows",
                                "RDP-Start ist für Windows optimiert (mstsc/cmdkey).")
        cmds = self.build_commands(c)
        if not cmds:
            return

        self.log_msg(f"🚀 Starte: {c.name} ({c.type})")
        try:
            if c.type == "RDP" and len(cmds) >= 2 and cmds[0].strip().lower().startswith("cmdkey"):
                subprocess.run(cmds[0], shell=True)
                subprocess.Popen(cmds[1], shell=True)
                self.log_msg("RDP gestartet (Anmeldedaten via cmdkey gesetzt).")
            else:
                subprocess.Popen(cmds[0], shell=True)
                self.log_msg(f"Befehl gestartet: {cmds[0]}")
        except Exception as e:
            QMessageBox.critical(self, "Start fehlgeschlagen", str(e))
            self.log_msg(f"❌ Fehler: {e}")

    # --- Import / Export ---
    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportieren", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([asdict(c) for c in self.store.connections], f, indent=2, ensure_ascii=False)
            self.log_msg(f"📤 Exportiert nach: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export fehlgeschlagen", str(e))

    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importieren", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for item in raw:
                try:
                    c = Connection(**item)
                except TypeError:
                    c = Connection(
                        id=item.get("id", str(uuid.uuid4())),
                        name=item.get("name", "Unbenannt"),
                        type=item.get("type", "RDP"),
                        address_or_id=item.get("address_or_id") or item.get("address") or item.get("id", ""),
                        username=item.get("username", ""),
                        password=item.get("password", ""),
                        template=item.get("template", "")
                    )
                if any(x.id == c.id for x in self.store.connections):
                    c.id = str(uuid.uuid4())
                self.store.add(c)
            self.populate_table()
            self.log_msg(f"📥 Importiert aus: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Import fehlgeschlagen", str(e))

def main():
    app = QApplication(sys.argv)
    set_dark_palette(app)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
