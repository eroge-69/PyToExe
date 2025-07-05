import sys, os, shutil, subprocess, datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QMessageBox, QStackedWidget, QGridLayout
)
from PyQt6.QtGui import QFont, QAction, QIcon
from PyQt6.QtCore import Qt, QTimer

# --- Helferfunktionen ---

def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S")

def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

# --- Taschenrechner-Widget (Startfenster) ---

class CalculatorWidget(QWidget):
    def __init__(self, on_unlock):
        super().__init__()
        self.on_unlock = on_unlock
        self.setWindowTitle("🧮 KAZA Rechner - Zugangscode eingeben")
        self.setFixedSize(400, 550)
        self.setStyleSheet("background-color: #121212; color: #00ffcc; font-family: Consolas;")
        self.expression = ""
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setFixedHeight(50)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setStyleSheet("background-color: #222; font-size: 28px; padding: 10px; border-radius: 8px; color: #00ffcc;")
        main_layout.addWidget(self.display)

        # Tastatur-Buttons
        buttons = [
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
            ('C','⌫','🔓','')
        ]

        grid = QGridLayout()
        grid.setSpacing(8)
        for r, row in enumerate(buttons):
            for c, btn_text in enumerate(row):
                if btn_text == '':
                    continue
                btn = QPushButton(btn_text)
                btn.setFixedSize(80,60)
                btn.setStyleSheet("background-color: #333; color: #00ffcc; font-size: 20px; border-radius: 10px;")
                btn.clicked.connect(self.btn_clicked)
                grid.addWidget(btn, r, c)
        main_layout.addLayout(grid)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #ff5555; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def btn_clicked(self):
        sender = self.sender()
        text = sender.text()
        if text == 'C':
            self.expression = ""
            self.display.setText(self.expression)
            self.status_label.setText("")
        elif text == '⌫':
            self.expression = self.expression[:-1]
            self.display.setText(self.expression)
            self.status_label.setText("")
        elif text == '=':
            # Statt Rechnung: Code prüfen
            if self.expression == "983":
                self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")
                self.status_label.setText("✅ Zugangscode korrekt! Cleaner startet...")
                QTimer.singleShot(1000, self.on_unlock)
            else:
                self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
                self.status_label.setText("❌ Falscher Zugangscode!")
                self.expression = ""
                self.display.setText(self.expression)
        else:
            self.expression += text
            self.display.setText(self.expression)


# --- Cleaner Hauptfenster ---

class CleanerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧼 KAZA CLEANER PREMIUM EDITION ✨")
        self.setFixedSize(1100, 800)
        self.setStyleSheet("background-color: #121212; color: #00ffcc; font-family: Consolas;")
        self.init_ui()
        self.cheat_keywords = [
            "cheat", "loader", "injector", "bypass", "aim", "rage", "esp",
            "dll", "menu", "hack", "crack", "exploit", "wallhack", "trigger",
            "silent", "spinbot", "aimbot", "mod", "hacktool", "trainer"
        ]

    def init_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("🧼 KAZA MAXIMUM CLEANER V3.0 ✨")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffcc;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        subtitle = QLabel("💣 Vollständige Spurenentfernung & Cheat-Ordner-Scanner")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        # Log-Ausgabe
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(
            "background-color: #222; color: #00ffcc; font-family: Consolas; font-size: 14px; padding: 12px; border-radius: 10px;"
        )
        main_layout.addWidget(self.log_output, stretch=1)

        # Buttons in mehreren Reihen
        btn_layout = QGridLayout()
        btn_layout.setSpacing(15)

        buttons = [
            ("🧹 TEMP Dateien löschen", self.clean_temp),
            ("🧩 Prefetch löschen", self.clean_prefetch),
            ("📂 Recent löschen", self.clean_recent),
            ("🗑️ Papierkorb leeren", self.clean_trash),
            ("🧽 Cheat-Ordner entfernen", self.clean_cheat_folders),
            ("🔍 Explorer Verlauf löschen", self.clear_explorer_history),
            ("📓 System Logs entfernen", self.remove_system_logs),
            ("⌨️ PowerShell History löschen", self.clear_ps_history),
            ("🌐 DNS Cache leeren", self.flush_dns),
            ("🔐 Registry Spuren löschen", self.clean_registry_traces),
            ("🔥 DEEP CLEAN (Alles)", self.deep_clean)
        ]

        for i, (text, func) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setStyleSheet(
                "background-color: #005f5f; color: #00ffcc; font-size: 16px; font-weight: bold; border-radius: 12px;"
            )
            if "DEEP" in text:
                btn.setStyleSheet(
                    "background-color: #ff0033; color: white; font-size: 18px; font-weight: bold; border-radius: 12px;"
                )
            btn.clicked.connect(func)
            btn_layout.addWidget(btn, i//3, i%3)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Beim Start prüfen ob Admin
        if not is_admin():
            self.log(f"⚠️ Hinweis: Programm ohne Administrator-Rechte gestartet! Einige Funktionen könnten fehlschlagen.")

    def log(self, message: str):
        self.log_output.append(f"[{timestamp()}] {message}")
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def clean_dir(self, path, label):
        if not path or not os.path.exists(path):
            self.log(f"⚠️ Pfad für {label} existiert nicht: {path}")
            return
        deleted = 0
        for root, dirs, files in os.walk(path):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                    deleted += 1
                except Exception as e:
                    self.log(f"❌ Datei löschen fehlgeschlagen: {os.path.join(root, name)} -> {e}")
            for name in dirs:
                try:
                    shutil.rmtree(os.path.join(root, name))
                    deleted +=1
                except Exception as e:
                    self.log(f"❌ Ordner löschen fehlgeschlagen: {os.path.join(root, name)} -> {e}")
        self.log(f"✅ {label} bereinigt, {deleted} Dateien/Ordner entfernt.")

    # Einzelne Cleaner-Methoden

    def clean_temp(self):
        temp1 = os.getenv('TEMP')
        temp2 = os.path.join(os.path.expanduser('~'), "AppData", "Local", "Temp")
        self.clean_dir(temp1, "TEMP (System)")
        self.clean_dir(temp2, "TEMP (User)")

    def clean_prefetch(self):
        path = r"C:\Windows\Prefetch"
        self.clean_dir(path, "Prefetch")

    def clean_recent(self):
        path = os.path.join(os.path.expanduser('~'), "AppData", "Roaming", "Microsoft", "Windows", "Recent")
        self.clean_dir(path, "Recent")

    def clean_trash(self):
        try:
            subprocess.run("PowerShell.exe Clear-RecycleBin -Force", shell=True, check=True)
            self.log("🗑️ Papierkorb geleert")
        except Exception as e:
            self.log(f"❌ Fehler beim Leeren des Papierkorbs: {e}")

    def clean_cheat_folders(self):
        base = os.path.expanduser('~')
        deleted = 0
        self.log(f"🔎 Suche nach Cheat-Ordnern in {base}...")
        for root, dirs, _ in os.walk(base):
            for d in dirs:
                low_d = d.lower()
                if any(keyword in low_d for keyword in self.cheat_keywords):
                    path_to_delete = os.path.join(root, d)
                    try:
                        shutil.rmtree(path_to_delete)
                        self.log(f"🧽 Gelöscht: {path_to_delete}")
                        deleted += 1
                    except Exception as e:
                        self.log(f"❌ Fehler beim Löschen von {path_to_delete}: {e}")
        if deleted == 0:
            self.log("✅ Keine verdächtigen Cheat-Ordner gefunden.")

    def clear_explorer_history(self):
        try:
            subprocess.run("reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU /f", shell=True, check=True)
            self.log("🔍 Explorer Dateiverlauf gelöscht")
        except Exception as e:
            self.log(f"❌ Fehler beim Löschen des Explorer-Verlaufs: {e}")

    def remove_system_logs(self):
        logs = ["Application", "Security", "System"]
        for log_name in logs:
            try:
                subprocess.run(f"wevtutil cl {log_name}", shell=True, check=True)
                self.log(f"📓 {log_name} Logs gelöscht")
            except Exception as e:
                self.log(f"❌ Fehler beim Löschen der {log_name} Logs: {e}")

    def clear_ps_history(self):
        try:
            path = os.path.join(os.path.expanduser('~'), "AppData", "Roaming", "Microsoft", "Windows", "PowerShell", "PSReadline", "ConsoleHost_history.txt")
            if os.path.exists(path):
                open(path, 'w').close()
                self.log("⌨️ PowerShell History gelöscht")
            else:
                self.log("⚠️ PowerShell History Datei nicht gefunden")
        except Exception as e:
            self.log(f"❌ Fehler beim Löschen der PowerShell History: {e}")

    def flush_dns(self):
        try:
            subprocess.run("ipconfig /flushdns", shell=True, check=True)
            self.log("🌐 DNS Cache geleert")
        except Exception as e:
            self.log(f"❌ Fehler beim Leeren des DNS Cache: {e}")

    def clean_registry_traces(self):
        try:
            # Beispiel: Registry-Eintrag 'suspicious' löschen aus Run-Key (nur Beispiel)
            subprocess.run("reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v suspicious /f", shell=True, check=True)
            self.log("🔐 Registry Spuren bereinigt")
        except Exception as e:
            self.log(f"❌ Fehler bei Registry Reinigung: {e}")

    def deep_clean(self):
        self.log("🔥 Starte Komplettbereinigung...")
        self.clean_temp()
        self.clean_prefetch()
        self.clean_recent()
        self.clean_trash()
        self.clean_cheat_folders()
        self.clear_explorer_history()
        self.remove_system_logs()
        self.clear_ps_history()
        self.flush_dns()
        self.clean_registry_traces()
        self.log("💀 KOMPLETTE SPURENENTFERNUNG ABGESCHLOSSEN")

# --- Hauptprogramm ---

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.calculator = CalculatorWidget(self.unlock_cleaner)
        self.cleaner = CleanerWindow()

        self.addWidget(self.calculator)  # Index 0
        self.addWidget(self.cleaner)     # Index 1

        self.setWindowTitle("🔐 KAZA ACCESS PANEL")
        self.setFixedSize(400, 550)
        self.setCurrentIndex(0)  # Start mit Taschenrechner

    def unlock_cleaner(self):
        self.setFixedSize(1100, 800)
        self.setCurrentIndex(1)
        self.cleaner.show()
        self.calculator.hide()


if __name__ == "__main__":
    if sys.platform != "win32":
        QMessageBox.critical(None, "Unsupported OS", "Dieses Programm läuft nur unter Windows!")
        sys.exit(1)

    app = QApplication(sys.argv)
    main = MainApp()
    main.show()
    sys.exit(app.exec())
