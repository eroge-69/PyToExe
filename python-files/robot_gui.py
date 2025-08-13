import sys, serial, serial.tools.list_ports, json, time
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
                             QSlider, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

SERVO_COUNT = 3  # Arduino ile aynı olmalı
BAUDRATE = 115200

class RobotControl(QWidget):
    def __init__(self):
        super().__init__()
        self.ser = None
        self.recording = False
        self.records = []
        self.sliders = []

        self.setWindowTitle("Robot Kol Kontrol Paneli")
        layout = QVBoxLayout()

        # Bağlan butonu
        btn_connect = QPushButton("Arduino'ya Bağlan")
        btn_connect.clicked.connect(self.connect_serial)
        layout.addWidget(btn_connect)

        # Servo sliderları
        for i in range(SERVO_COUNT):
            label = QLabel(f"Servo {i+1}")
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 180)
            slider.valueChanged.connect(self.update_servos)
            self.sliders.append(slider)
            layout.addWidget(label)
            layout.addWidget(slider)

        # Kayıt / Play
        btn_rec = QPushButton("Kayıt Başlat / Durdur")
        btn_rec.clicked.connect(self.toggle_record)
        layout.addWidget(btn_rec)

        btn_play = QPushButton("Oynat")
        btn_play.clicked.connect(self.play_record)
        layout.addWidget(btn_play)

        # Export / Import
        btn_exp = QPushButton("Kayıt Dışa Aktar")
        btn_exp.clicked.connect(self.export_record)
        layout.addWidget(btn_exp)

        btn_imp = QPushButton("Kayıt İçe Aktar")
        btn_imp.clicked.connect(self.import_record)
        layout.addWidget(btn_imp)

        self.setLayout(layout)

    def connect_serial(self):
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            QMessageBox.critical(self, "Hata", "Hiçbir seri port bulunamadı.")
            return
        port = ports[0].device
        self.ser = serial.Serial(port, BAUDRATE, timeout=1)
        QMessageBox.information(self, "Bağlantı", f"{port} portuna bağlandı.")

    def update_servos(self):
        if self.ser:
            angles = [str(s.value()) for s in self.sliders]
            data = ",".join(angles) + "\n"
            self.ser.write(data.encode())
            if self.recording:
                self.records.append([s.value() for s in self.sliders])

    def toggle_record(self):
        if not self.recording:
            self.records.clear()
            self.recording = True
            QMessageBox.information(self, "Kayıt", "Kayıt başladı.")
        else:
            self.recording = False
            QMessageBox.information(self, "Kayıt", f"Kayıt durdu. {len(self.records)} adım kaydedildi.")

    def play_record(self):
        if self.ser and self.records:
            for step in self.records:
                data = ",".join(map(str, step)) + "\n"
                self.ser.write(data.encode())
                time.sleep(0.05)

    def export_record(self):
        path, _ = QFileDialog.getSaveFileName(self, "Kayıt Kaydet", "", "JSON Files (*.json)")
        if path:
            with open(path, "w") as f:
                json.dump(self.records, f)

    def import_record(self):
        path, _ = QFileDialog.getOpenFileName(self, "Kayıt Aç", "", "JSON Files (*.json)")
        if path:
            with open(path, "r") as f:
                self.records = json.load(f)
            QMessageBox.information(self, "Kayıt", f"{len(self.records)} adım yüklendi.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RobotControl()
    win.show()
    sys.exit(app.exec_())