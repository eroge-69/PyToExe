import sys
import os
import zipfile
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView

def read_version():
    try:
        with open("version.txt") as f:
            return f.read().strip()
    except:
        return "Versione: 1.21.94"

class FantaLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"FantaCraftMC Launcher – {read_version()}")
        self.setWindowIcon(QIcon("favicon.ico"))
        self.setGeometry(100, 100, 1024, 768)

        self.browser = QWebEngineView()
        self.browser.load(QUrl("https://fantacraftmc.22web.org"))

        # Pulsanti di navigazione
        backBtn = QPushButton("← Indietro")
        forwardBtn = QPushButton("→ Avanti")
        reloadBtn = QPushButton("⟳ Ricarica")

        backBtn.clicked.connect(self.browser.back)
        forwardBtn.clicked.connect(self.browser.forward)
        reloadBtn.clicked.connect(self.browser.reload)

        # Pulsante blu slime
        downloadBtn = QPushButton("📥 Scarica l'app ufficiale della FantaCraftMC")
        downloadBtn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #005EA6;
            }
        """)
        downloadBtn.clicked.connect(self.create_zip)

        # Layout
        navLayout = QHBoxLayout()
        navLayout.addWidget(backBtn)
        navLayout.addWidget(forwardBtn)
        navLayout.addWidget(reloadBtn)
        navLayout.addWidget(downloadBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(navLayout)
        mainLayout.addWidget(self.browser)

        self.setLayout(mainLayout)

    def create_zip(self):
        folder_to_zip = "fantacraftmc"

        if not os.path.isdir(folder_to_zip):
            QMessageBox.critical(self, "Errore", "La cartella 'fantacraftmc' non esiste nella directory corrente.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva l'app FantaCraftMC come ZIP",
            "FantaCraftMC_Ufficiale.zip",
            "Archivio ZIP (*.zip)"
        )
        if not path:
            return

        try:
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_to_zip):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder_to_zip)
                        zipf.write(file_path, os.path.join(folder_to_zip, arcname))
            QMessageBox.information(self, "Download completato", f"ZIP salvato con successo in:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la creazione dello ZIP:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = FantaLauncher()
    launcher.show()
    sys.exit(app.exec_())
