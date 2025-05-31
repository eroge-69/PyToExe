# -*- coding: utf-8 -*-
"""
Created on Sat May 31 10:35:07 2025

@author: Fynn Michael Nissen Prozura
"""

import sys
import time
import pandas as pd
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QPushButton, QLabel,
    QVBoxLayout, QWidget, QMessageBox, QProgressBar, QAction
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QMovie

class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prozurmat wird geladen...")
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)

        layout = QVBoxLayout()
        self.label_animation = QLabel()
        self.movie = QMovie("loading.gif")
        self.label_animation.setMovie(self.movie)
        layout.addWidget(self.label_animation)

        self.label_text = QLabel("Willkommen bei Prozurmat")
        self.label_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_text)

        self.setLayout(layout)
        self.movie.start()

class ProzurmatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prozurmat - powered by Prozura")
        self.setGeometry(100, 100, 600, 350)

        self.files = []
        self.output_path = ""

        self.label = QLabel("Wähle Dateien oder einen Ordner aus")
        self.progress = QProgressBar()
        self.progress.setVisible(False)

        self.btn_select_files = QPushButton("Dateien auswählen")
        self.btn_select_folder = QPushButton("Ordner auswählen")
        self.btn_select_output = QPushButton("Zielpfad auswählen")
        self.btn_merge = QPushButton("Dateien zusammenführen")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_select_files)
        layout.addWidget(self.btn_select_folder)
        layout.addWidget(self.btn_select_output)
        layout.addWidget(self.btn_merge)
        layout.addWidget(self.progress)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.btn_select_files.clicked.connect(self.select_files)
        self.btn_select_folder.clicked.connect(self.select_folder)
        self.btn_select_output.clicked.connect(self.select_output_path)
        self.btn_merge.clicked.connect(self.merge_files)

        about_action = QAction("Über Prozurmat", self)
        about_action.triggered.connect(self.show_about_dialog)
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Hilfe")
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        QMessageBox.information(self, "Über Prozurmat",
                                "Prozurmat v1.0\nErstellt von der Firma Prozura\n© 2025 Prozura Software")

    def select_files(self):
        self.files, _ = QFileDialog.getOpenFileNames(self, "Dateien auswählen", "", "Textdateien (*.txt)")
        self.label.setText(f"{len(self.files)} Dateien ausgewählt.")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Ordner auswählen")
        if folder:
            self.files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".txt")]
            self.label.setText(f"{len(self.files)} Dateien im Ordner gefunden.")

    def select_output_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "Zielpfad auswählen", "Prozurmat_Merged.csv", "CSV Dateien (*.csv)")
        if path:
            self.output_path = path
            self.label.setText(f"Zielpfad gesetzt.")

    def merge_files(self):
        if not self.files or not self.output_path:
            QMessageBox.warning(self, "Fehler", "Bitte Dateien und Zielpfad auswählen.")
            return

        try:
            self.progress.setVisible(True)
            self.progress.setValue(0)
            header = pd.read_csv(self.files[0], sep=';', dtype=str, nrows=0).columns
            df_all = []

            for i, file in enumerate(self.files):
                try:
                    df = pd.read_csv(file, sep=';', dtype=str, skiprows=1, header=None)
                    df.columns = header
                    df_all.append(df)
                    self.progress.setValue(int((i+1)/len(self.files)*100))
                except Exception as fe:
                    print(f"Fehler in Datei {file}: {fe}")

            df_final = pd.concat(df_all, ignore_index=True)
            df_final.to_csv(self.output_path, sep=';', index=False)
            QMessageBox.information(self, "Erfolg", "Dateien erfolgreich zusammengeführt!")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
        finally:
            self.progress.setVisible(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    splash = LoadingScreen()
    splash.show()

    def start_main_app():
        global window
        splash.close()
        window = ProzurmatApp()
        window.show()

    QTimer.singleShot(2500, start_main_app)

    sys.exit(app.exec_())
