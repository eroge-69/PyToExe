#!/usr/bin/env python3.11
"""
IServ GUI Browser - Eine GUI-Anwendung mit eingebettetem Browser zum Öffnen von IServ mit gespeicherten Cookies
"""

import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QLabel, 
                             QFileDialog, QMessageBox, QStatusBar)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineCookieStore
from datetime import datetime

class IServBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IServ GUI Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Variablen
        self.cookie_file = "cookies.json"
        self.iserv_url = "https://thg-kiel.de/iserv"
        
        # GUI erstellen
        self.init_ui()
        
    def init_ui(self):
        # Hauptwidget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Hauptlayout
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Titel
        title_label = QLabel("IServ GUI Browser")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Cookie-Datei Bereich
        cookie_layout = QHBoxLayout()
        cookie_label = QLabel("Cookie-Datei:")
        cookie_label.setMinimumWidth(100)
        cookie_layout.addWidget(cookie_label)
        
        self.cookie_input = QLineEdit(self.cookie_file)
        cookie_layout.addWidget(self.cookie_input)
        
        browse_btn = QPushButton("Durchsuchen")
        browse_btn.clicked.connect(self.browse_cookie_file)
        browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        cookie_layout.addWidget(browse_btn)
        
        layout.addLayout(cookie_layout)
        
        # URL Bereich
        url_layout = QHBoxLayout()
        url_label = QLabel("IServ URL:")
        url_label.setMinimumWidth(100)
        url_layout.addWidget(url_label)
        
        self.url_input = QLineEdit(self.iserv_url)
        url_layout.addWidget(self.url_input)
        
        layout.addLayout(url_layout)
        
        # Button Bereich
        button_layout = QHBoxLayout()
        
        load_btn = QPushButton("IServ mit Cookies laden")
        load_btn.clicked.connect(self.load_iserv_with_cookies)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        button_layout.addWidget(load_btn)
        
        reload_btn = QPushButton("Seite neu laden")
        reload_btn.clicked.connect(self.reload_page)
        reload_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        button_layout.addWidget(reload_btn)
        
        clear_btn = QPushButton("Cookies löschen")
        clear_btn.clicked.connect(self.clear_cookies)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # WebEngine View
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("about:blank"))
        layout.addWidget(self.browser)
        
        # Statusleiste
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Bereit")
        
        # Cookie Store
        self.profile = QWebEngineProfile.defaultProfile()
        self.cookie_store = self.profile.cookieStore()
        
    def browse_cookie_file(self):
        """Datei-Browser für Cookie-Datei öffnen"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Cookie-Datei auswählen",
            "",
            "JSON Dateien (*.json);;Alle Dateien (*.*)"
        )
        if file_name:
            self.cookie_input.setText(file_name)
            self.cookie_file = file_name
    
    def load_cookies_from_file(self):
        """Cookies aus der JSON-Datei laden"""
        cookie_path = self.cookie_input.text()
        
        if not os.path.exists(cookie_path):
            QMessageBox.critical(self, "Fehler", f"Cookie-Datei nicht gefunden: {cookie_path}")
            return None
        
        try:
            with open(cookie_path, 'r') as f:
                cookies = json.load(f)
            return cookies
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Cookies:\n{str(e)}")
            return None
    
    def set_cookies(self, cookies):
        """Cookies im Browser setzen"""
        from PyQt5.QtNetwork import QNetworkCookie
        
        for cookie_data in cookies:
            try:
                # QNetworkCookie erstellen
                cookie = QNetworkCookie()
                cookie.setName(cookie_data['name'].encode())
                cookie.setValue(cookie_data['value'].encode())
                cookie.setDomain(cookie_data.get('domain', ''))
                cookie.setPath(cookie_data.get('path', '/'))
                cookie.setSecure(cookie_data.get('secure', False))
                cookie.setHttpOnly(cookie_data.get('httpOnly', False))
                
                # Expires behandeln
                if 'expires' in cookie_data and cookie_data['expires'] != -1:
                    from PyQt5.QtCore import QDateTime
                    expiry_date = QDateTime.fromSecsSinceEpoch(cookie_data['expires'])
                    cookie.setExpirationDate(expiry_date)
                
                # Cookie zum Store hinzufügen
                self.cookie_store.setCookie(cookie, QUrl(f"https://{cookie_data.get('domain', '')}"))
                
            except Exception as e:
                print(f"Warnung: Cookie konnte nicht gesetzt werden: {cookie_data.get('name', 'unknown')}, Fehler: {str(e)}")
    
    def load_iserv_with_cookies(self):
        """IServ mit den gespeicherten Cookies laden"""
        self.status_bar.showMessage("Cookies werden geladen...")
        
        # Cookies laden
        cookies = self.load_cookies_from_file()
        if cookies is None:
            self.status_bar.showMessage("Fehler beim Laden der Cookies")
            return
        
        # Zuerst zur Seite navigieren, um die Domain zu etablieren
        url = self.url_input.text()
        self.status_bar.showMessage("Navigiere zu IServ...")
        
        # Cookies setzen
        self.set_cookies(cookies)
        
        # Zur IServ-Seite navigieren
        self.browser.setUrl(QUrl(url))
        self.status_bar.showMessage("IServ mit Cookies geladen")
        
        QMessageBox.information(self, "Erfolg", "IServ wurde mit Ihren Cookies geladen!")
    
    def reload_page(self):
        """Seite neu laden"""
        self.browser.reload()
        self.status_bar.showMessage("Seite wird neu geladen...")
    
    def clear_cookies(self):
        """Alle Cookies löschen"""
        self.cookie_store.deleteAllCookies()
        self.status_bar.showMessage("Alle Cookies wurden gelöscht")
        QMessageBox.information(self, "Info", "Alle Cookies wurden gelöscht")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = IServBrowser()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
