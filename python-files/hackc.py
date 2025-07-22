import subprocess
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QMessageBox
import sys

class WifiHotspotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wi-Fi Hotspot Yönetimi")
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        self.start_button = QPushButton("Hotspot Başlat")
        self.start_button.clicked.connect(self.start_hotspot)
        layout.addWidget(self.start_button)

        self.show_devices_button = QPushButton("Bağlı Cihazları Göster")
        self.show_devices_button.clicked.connect(self.list_connected_devices)
        layout.addWidget(self.show_devices_button)

        self.stop_button = QPushButton("Hotspot Durdur")
        self.stop_button.clicked.connect(self.stop_hotspot)
        layout.addWidget(self.stop_button)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

        self.setLayout(layout)

    def start_hotspot(self):
        ssid = "WİFİNET"
        password = "wifi123s"
        try:
            subprocess.run(f'netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}', shell=True, check=True)
            subprocess.run('netsh wlan start hostednetwork', shell=True, check=True)
            QMessageBox.information(self, "Başarılı", f"Hotspot başlatıldı: {ssid}")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Hata", "Hotspot başlatılamadı. Lütfen yönetici olarak çalıştır.")

    def list_connected_devices(self):
        try:
            result = subprocess.check_output("arp -a", shell=True).decode()
            self.output_area.setPlainText(result)
        except Exception as e:
            self.output_area.setPlainText("Cihazlar alınamadı:\n" + str(e))

    def stop_hotspot(self):
        try:
            subprocess.run("netsh wlan stop hostednetwork", shell=True, check=True)
            QMessageBox.information(self, "Hotspot Durduruldu", "Hotspot başarıyla kapatıldı.")
        except subprocess.CalledProcessError:
            QMessageBox.warning(self, "Hata", "Hotspot kapatılamadı.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WifiHotspotApp()
    window.show()
    sys.exit(app.exec_())
