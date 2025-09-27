import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar
from PyQt6.QtGui import QIcon

class WebScanner(QWidget):
    def _init_(self):
        super()._init_()
        self.setWindowTitle("Web Tarayıcı - Test Sürümü")
        self.setGeometry(300, 300, 600, 400)
        self.setWindowIcon(QIcon("ikon.ico"))  # Buraya kendi ikon dosyanın yolunu yaz

        # Layout
        layout = QVBoxLayout()

        # URL Girişi
        layout.addWidget(QLabel("Tarama Yapılacak URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("http://localhost:8080")
        layout.addWidget(self.url_input)

        # Başlat Butonu
        self.start_btn = QPushButton("Tarama Başlat")
        self.start_btn.clicked.connect(self.scan_website)
        layout.addWidget(self.start_btn)

        # İlerleme Çubuğu
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # Sonuç Alanı
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def scan_website(self):
        url = self.url_input.text()
        if not url.startswith("http"):
            self.log_area.append("Geçerli bir URL giriniz!")
            return

        endpoints = ["/", "/admin", "/login", "/test"]
        total = len(endpoints)
        self.progress.setMaximum(total)

        for i, endpoint in enumerate(endpoints, 1):
            full_url = url + endpoint
            try:
                response = requests.get(full_url)
                self.log_area.append(f"[{response.status_code}] {full_url}")
            except requests.exceptions.RequestException as e:
                self.log_area.append(f"Hata: {e}")
            self.progress.setValue(i)

        self.log_area.append("\nTarama tamamlandı!")

if _name_ == "_main_":
    app = QApplication(sys.argv)
    window = WebScanner()
    window.show()
    sys.exit(app.exec())