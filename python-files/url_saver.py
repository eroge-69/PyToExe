import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QLineEdit, QPushButton, QHBoxLayout, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class URLSaverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file = "saved_url.txt"
        self.saved_url = ""
        
        self.load_saved_url()
        self.init_ui()
        
    def load_saved_url(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.saved_url = f.read().strip()
    
    def init_ui(self):
        self.setWindowTitle("URL Saver with Embedded Browser")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # URL input area
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit(self.saved_url)
        self.url_input.setPlaceholderText("Enter website URL (e.g., https://example.com)")
        
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_url)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_url)
        
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(open_btn)
        url_layout.addWidget(reset_btn)
        layout.addLayout(url_layout)
        
        # Embedded browser
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        
        # Load saved URL if it exists
        if self.saved_url:
            self.load_url(self.saved_url)
    
    def open_url(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL")
            return
        
        # Add https:// if missing
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        # Save the URL
        with open(self.config_file, "w") as f:
            f.write(url)
        
        # Load in embedded browser
        self.load_url(url)
    
    def load_url(self, url):
        self.browser.setUrl(QUrl(url))
    
    def reset_url(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.url_input.clear()
        self.browser.setUrl(QUrl("about:blank"))
        QMessageBox.information(self, "Reset", "URL has been reset")

if __name__ == "__main__":
    app = QApplication([])
    window = URLSaverApp()
    window.show()
    app.exec_()