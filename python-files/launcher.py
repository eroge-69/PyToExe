import sys, os, json, tempfile, subprocess, shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMainWindow, QWidget,
    QVBoxLayout, QLabel, QPushButton, QLineEdit, QDateEdit, QTimeEdit,
    QMessageBox, QCheckBox, QTextEdit, QScrollArea, QHBoxLayout, QDialog,
    QFileDialog, QFrame
)
from PyQt5.QtCore import QTimer, Qt, QDate, QTime
from PyQt5.QtGui import QIcon, QTextCharFormat, QSyntaxHighlighter, QColor, QFont
from plyer import notification

DATA_FILE = "termine.json"
PLUGIN_STORAGE_DIR = os.path.join(os.getenv('LOCALAPPDATA') or os.path.expanduser('~'), "timep")
os.makedirs(PLUGIN_STORAGE_DIR, exist_ok=True)

SETTINGS = {"sound": True}

def get_tray_icon():
    icon = QApplication.style().standardIcon(QApplication.style().SP_ComputerIcon)
    return icon

def load_data():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r") as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=2)

def play_sound():
    if SETTINGS["sound"]:
        try:
            import winsound
            winsound.Beep(1000, 400)
        except:
            pass

def notify(title, message):
    notification.notify(title=title, message=message, timeout=5)

def write_batch(content, console=True):
    bat_path = os.path.join(tempfile.gettempdir(), f"task_{int(datetime.now().timestamp())}.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(content)
    if console:
        subprocess.Popen(['start', '', bat_path], shell=True)
    else:
        subprocess.Popen(['start', '/B', bat_path], shell=True)

def get_plugins():
    return [f for f in os.listdir(PLUGIN_STORAGE_DIR) if f.endswith(".bat")]

def plugin_name_no_ext(filename):
    return os.path.splitext(filename)[0]

class BatchSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#008000"))  # grün

        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#0000FF"))  # blau
        self.keyword_format.setFontWeight(QFont.Bold)

        self.variable_format = QTextCharFormat()
        self.variable_format.setForeground(QColor("#FF00FF"))  # magenta

        self.keywords = ["echo", "set", "if", "goto", "pause", "exit", "call", "rem", "start"]

    def highlightBlock(self, text):
        import re
        comment_pattern = re.compile(r"^\s*(rem|::).*$", re.IGNORECASE)
        if comment_pattern.match(text):
            self.setFormat(0, len(text), self.comment_format)
            return
        for kw in self.keywords:
            for m in re.finditer(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE):
                self.setFormat(m.start(), len(kw), self.keyword_format)
        for m in re.finditer(r'%[^%]+%', text):
            self.setFormat(m.start(), m.end() - m.start(), self.variable_format)

class ExecuteEditorDialog(QDialog):
    def __init__(self, initial_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Execute-Code Editor")
        self.resize(600, 400)
        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(initial_text)
        self.highlighter = BatchSyntaxHighlighter(self.text_edit.document())
        layout.addWidget(self.text_edit)

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

    def get_text(self):
        return self.text_edit.toPlainText()

class PluginsManageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plugins verwalten")
        self.resize(400, 300)
        layout = QVBoxLayout(self)

        self.plugins = get_plugins()
        self.plugin_list = QVBoxLayout()

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        content = QWidget()
        content.setLayout(self.plugin_list)
        self.scroll.setWidget(content)

        layout.addWidget(self.scroll)

        btn_close = QPushButton("Schließen")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.refresh_plugins()

    def refresh_plugins(self):
        while self.plugin_list.count():
            item = self.plugin_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.plugins = get_plugins()
        for p in self.plugins:
            hbox = QHBoxLayout()
            lbl = QLabel(plugin_name_no_ext(p))
            btn_del = QPushButton("Löschen")
            btn_del.clicked.connect(lambda _, plg=p: self.delete_plugin(plg))
            hbox.addWidget(lbl)
            hbox.addStretch()
            hbox.addWidget(btn_del)
            container = QWidget()
            container.setLayout(hbox)
            self.plugin_list.addWidget(container)

    def delete_plugin(self, plugin_file):
        full_path = os.path.join(PLUGIN_STORAGE_DIR, plugin_file)
        if os.path.exists(full_path):
            os.remove(full_path)
        self.refresh_plugins()

class PluginsAddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plugin hinzufügen")
        self.resize(400, 150)
        layout = QVBoxLayout(self)

        self.label = QLabel("Wähle eine .ptn Datei aus, die als Plugin hinzugefügt wird:")
        layout.addWidget(self.label)

        self.btn_browse = QPushButton("Datei auswählen")
        self.btn_browse.clicked.connect(self.browse_file)
        layout.addWidget(self.btn_browse)

        self.selected_file_label = QLabel("")
        layout.addWidget(self.selected_file_label)

        btn_add = QPushButton("Hinzufügen")
        btn_add.clicked.connect(self.add_plugin)
        layout.addWidget(btn_add)

        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

        self.selected_file = None

    def browse_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Plugin Datei auswählen", "", "Plugin Dateien (*.ptn)")
        if file:
            self.selected_file = file
            self.selected_file_label.setText(os.path.basename(file))

    def add_plugin(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Fehler", "Keine Datei ausgewählt!")
            return
        base_name = os.path.splitext(os.path.basename(self.selected_file))[0]
        dest_file = os.path.join(PLUGIN_STORAGE_DIR, base_name + ".bat")
        shutil.copy2(self.selected_file, dest_file)
        QMessageBox.information(self, "Erfolg", f"Plugin '{base_name}' hinzugefügt.")
        self.accept()

class PluginsSelectDialog(QDialog):
    def __init__(self, selected_plugins, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plugins auswählen")
        self.resize(400, 300)
        layout = QVBoxLayout(self)

        self.plugins = get_plugins()
        self.checkboxes = []

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        content = QWidget()
        vlayout = QVBoxLayout()
        content.setLayout(vlayout)
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)

        for p in self.plugins:
            cb = QCheckBox(plugin_name_no_ext(p))
            if plugin_name_no_ext(p) in selected_plugins:
                cb.setChecked(True)
            vlayout.addWidget(cb)
            self.checkboxes.append((p, cb))

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

    def get_selected_plugins(self):
        return [plugin_name_no_ext(p) for p, cb in self.checkboxes if cb.isChecked()]

class TerminPlaner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terminplaner")
        self.setWindowIcon(get_tray_icon())
        self.resize(600, 650)

        self.data = load_data()
        self.command_code = ""
        self.selected_plugins = []

        self.init_ui()

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_appointments)
        self.check_timer.start(30000)

    def init_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        top_right_layout = QHBoxLayout()
        top_right_layout.addStretch()
        plugins_btn = QPushButton("Plugins")
        plugins_btn.clicked.connect(self.plugins_menu)
        top_right_layout.addWidget(plugins_btn)
        main_layout.addLayout(top_right_layout)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Titel des Termins")
        main_layout.addWidget(self.title_input)

        dt_layout = QHBoxLayout()
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDate(QDate.currentDate())
        dt_layout.addWidget(QLabel("Datum:"))
        dt_layout.addWidget(self.date_input)

        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        dt_layout.addWidget(QLabel("Uhrzeit:"))
        dt_layout.addWidget(self.time_input)
        main_layout.addLayout(dt_layout)

        cb_layout = QHBoxLayout()
        self.mute_checkbox = QCheckBox("Stumm")
        self.console_checkbox = QCheckBox("Mit Konsole ausführen")
        cb_layout.addWidget(self.mute_checkbox)
        cb_layout.addWidget(self.console_checkbox)
        main_layout.addLayout(cb_layout)

        plugin_select_btn = QPushButton("Plugins für Termin auswählen")
        plugin_select_btn.clicked.connect(self.select_plugins_for_termin)
        main_layout.addWidget(plugin_select_btn)

        exec_btn = QPushButton("Execute-Code bearbeiten")
        exec_btn.clicked.connect(self.open_command_editor)
        main_layout.addWidget(exec_btn)

        add_btn = QPushButton("Termin hinzufügen / speichern")
        add_btn.clicked.connect(self.add_or_update_termin)
        main_layout.addWidget(add_btn)

        self.canvas_layout = QVBoxLayout()
        self.canvas_layout.setSpacing(10)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.canvas_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setMinimumHeight(300)
        main_layout.addWidget(scroll_area)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.redraw_canvas()

    def plugins_menu(self):
        menu = QMenu()
        manage_action = QAction("Plugins verwalten", self)
        manage_action.triggered.connect(self.plugins_manage)
        menu.addAction(manage_action)
        add_action = QAction("Plugin hinzufügen", self)
        add_action.triggered.connect(self.plugins_add)
        menu.addAction(add_action)
        pos = self.mapToGlobal(self.sender().pos())
        menu.exec_(pos)

    def plugins_manage(self):
        dlg = PluginsManageDialog(self)
        dlg.exec_()

    def plugins_add(self):
        dlg = PluginsAddDialog(self)
        if dlg.exec_():
            QMessageBox.information(self, "Info", "Plugin hinzugefügt.")

    def select_plugins_for_termin(self):
        dlg = PluginsSelectDialog(self.selected_plugins, self)
        if dlg.exec_():
            self.selected_plugins = dlg.get_selected_plugins()

    def open_command_editor(self):
        dlg = ExecuteEditorDialog(self.command_code, self)
        if dlg.exec_():
            self.command_code = dlg.get_text()

    def add_or_update_termin(self):
        name = self.title_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte einen Termin-Titel eingeben.")
            return

        dt = datetime.combine(self.date_input.date().toPyDate(), self.time_input.time().toPyTime())
        if dt < datetime.now():
            QMessageBox.warning(self, "Fehler", "Datum und Uhrzeit müssen in der Zukunft liegen.")
            return

        # Doppelten Termin löschen
        self.data = [t for t in self.data if not (t['name'] == name and t['datetime'] == dt.isoformat())]

        termin = {
            "name": name,
            "datetime": dt.isoformat(),
            "mute": self.mute_checkbox.isChecked(),
            "console": self.console_checkbox.isChecked(),
            "command": self.command_code,
            "plugins": self.selected_plugins,
            "command_executed": False
        }

        self.data.append(termin)
        save_data(self.data)
        self.redraw_canvas()

    def redraw_canvas(self):
        while self.canvas_layout.count():
            item = self.canvas_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        now = datetime.now()
        self.data.sort(key=lambda t: t['datetime'])
        for termin in self.data:
            dt = datetime.fromisoformat(termin['datetime'])
            if dt < now:
                continue  # Nur zukünftige anzeigen

            widget = QFrame()
            widget.setFrameShape(QFrame.StyledPanel)
            layout = QVBoxLayout(widget)

            layout.addWidget(QLabel(f"<b>{termin['name']}</b>"))
            layout.addWidget(QLabel(f"{dt.strftime('%d.%m.%Y %H:%M')}"))

            flags = []
            if termin.get("mute"): flags.append("Stumm")
            if termin.get("console"): flags.append("Konsole")
            if termin.get("plugins"):
                flags.append(f"Plugins: {', '.join(termin.get('plugins'))}")
            layout.addWidget(QLabel(", ".join(flags)))

            btn_layout = QHBoxLayout()
            exec_btn = QPushButton("Ausführen")
            exec_btn.clicked.connect(lambda _, t=termin: self.execute_termin(t))
            del_btn = QPushButton("Löschen")
            del_btn.clicked.connect(lambda _, t=termin: self.delete_termin(t))
            btn_layout.addWidget(exec_btn)
            btn_layout.addWidget(del_btn)
            layout.addLayout(btn_layout)

            self.canvas_layout.addWidget(widget)

    def delete_termin(self, termin):
        self.data = [t for t in self.data if t != termin]
        save_data(self.data)
        self.redraw_canvas()

    def execute_termin(self, termin):
        if not termin.get("mute", False):
            play_sound()
            notify("Termin erreicht", termin["name"])

        cmd = termin.get("command", "").strip()
        if cmd:
            write_batch(cmd, console=termin.get("console", True))

        # Plugins ausführen
        for plugin_name in termin.get("plugins", []):
            batch_file = os.path.join(PLUGIN_STORAGE_DIR, plugin_name + ".bat")
            if os.path.exists(batch_file):
                subprocess.Popen(['start', '', batch_file], shell=True)

        # Termin nach Ausführung löschen
        self.delete_termin(termin)

    def check_appointments(self):
        now = datetime.now()
        for termin in self.data[:]:
            dt = datetime.fromisoformat(termin['datetime'])
            if dt <= now and not termin.get("command_executed", False):
                self.execute_termin(termin)

    def closeEvent(self, event):
        # Beim Schließen nur verstecken, Programm läuft im Tray weiter
        event.ignore()
        self.hide()

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.main_window = TerminPlaner()

        self.tray = QSystemTrayIcon(get_tray_icon())
        self.tray.setToolTip("Terminplaner")

        menu = QMenu()
        exit_action = QAction("Beenden")
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self.on_tray_activated)

        self.tray.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Linksklick
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.main_window.show()
                self.main_window.raise_()
                self.main_window.activateWindow()

    def exit_app(self):
        self.main_window.close()
        self.quit()

def main():
    app = App(sys.argv)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
