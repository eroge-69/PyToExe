# vks_broadcast.py

import sys
import os
import time
from datetime import datetime, timedelta

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen
import vlc
import subprocess
import json
import hashlib

ALLOWED_EMAIL = "selvaesackyk3@gmail.com"

class VKSBroadcast(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VKS Broadcast")
        self.setWindowIcon(QtGui.QIcon("vks_logo.png"))
        self.setGeometry(100, 100, 1300, 750)

        self.license_file = "vks_license.key"
        self.authenticated_user = None
        if not self.check_license():
            sys.exit()

        self.init_ui()
        self.player = vlc.MediaPlayer()
        self.live_preview_player = vlc.MediaPlayer()

        self.play_history = []
        self.history_file = "play_history.txt"
        self.load_play_history()

        self.cg_labels = []
        self.setup_cg_layers()

    def check_license(self):
        if not os.path.exists(self.license_file):
            return self.login_and_generate_license()

        try:
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            email = license_data.get("email")
            key = license_data.get("key")
            if self.generate_key(email) == key and email == ALLOWED_EMAIL:
                self.authenticated_user = email
                return True
            else:
                QtWidgets.QMessageBox.critical(self, "Invalid License", "License verification failed.")
                return False
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"License file error: {e}")
            return False

    def login_and_generate_license(self):
        email, ok = QtWidgets.QInputDialog.getText(self, "Login", "Enter your Gmail:")
        if ok and email:
            if email != ALLOWED_EMAIL:
                QtWidgets.QMessageBox.critical(self, "Access Denied", "This Gmail is not authorized to use this app.")
                return False
            key = self.generate_key(email)
            try:
                with open(self.license_file, 'w') as f:
                    json.dump({"email": email, "key": key}, f)
                self.authenticated_user = email
                QtWidgets.QMessageBox.information(self, "Registered", f"Welcome {email}")
                return True
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Could not save license: {e}")
                return False
        return False

    def generate_key(self, email):
        return hashlib.sha256((email + "VKS_BROADCAST_SALT").encode()).hexdigest()

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        self.play_button = QtWidgets.QPushButton("Play")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.crawler_button = QtWidgets.QPushButton("Add Crawler Text")
        self.cg_layer_button = QtWidgets.QPushButton("Add CG Layer")
        self.sms_overlay_button = QtWidgets.QPushButton("Add SMS Overlay")

        self.crawler_input = QtWidgets.QLineEdit()
        self.crawler_input.setPlaceholderText("Enter Crawler Text")

        self.cg_file_input = QtWidgets.QLineEdit()
        self.cg_file_input.setPlaceholderText("Enter CG File Path (PNG, MOV, AVI, etc.)")

        self.sms_input = QtWidgets.QLineEdit()
        self.sms_input.setPlaceholderText("Enter SMS Text")

        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.crawler_input)
        layout.addWidget(self.crawler_button)
        layout.addWidget(self.cg_file_input)
        layout.addWidget(self.cg_layer_button)
        layout.addWidget(self.sms_input)
        layout.addWidget(self.sms_overlay_button)

        # Connect buttons to dummy functions for now
        self.play_button.clicked.connect(self.play_media)
        self.stop_button.clicked.connect(self.stop_media)
        self.crawler_button.clicked.connect(self.add_crawler_text)
        self.cg_layer_button.clicked.connect(self.add_cg_layer)
        self.sms_overlay_button.clicked.connect(self.add_sms_overlay)

    def play_media(self):
        print("Playing media...")

    def stop_media(self):
        print("Stopping media...")

    def add_crawler_text(self):
        crawler_text = self.crawler_input.text()
        print(f"Crawler Text: {crawler_text}")

    def add_cg_layer(self):
        cg_path = self.cg_file_input.text()
        print(f"CG Layer File: {cg_path}")

    def add_sms_overlay(self):
        sms_text = self.sms_input.text()
        print(f"SMS Overlay: {sms_text}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Splash screen with VKS logo
    splash_pix = QPixmap("vks_logo.png")
    splash = QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    time.sleep(3)

    # Main app window
    window = VKSBroadcast()
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())
