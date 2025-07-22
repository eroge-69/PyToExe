import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSpinBox
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QBrush, QPainterPath

class CountdownTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.total_seconds = 0
        self.timer = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Zaman Sayacı')
        self.setFixedSize(int(480 * 1.15), int(320 * 1.15))

        # Pembe ve beyaz tema
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor('#ffe4ec'))  # Açık pembe
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # Süre ayarlama alanı
        self.input_layout = QHBoxLayout()
        self.hour_input = QSpinBox()
        self.hour_input.setRange(0, 999)
        self.hour_input.setSuffix(' saat')
        self.minute_input = QSpinBox()
        self.minute_input.setRange(0, 59)
        self.minute_input.setSuffix(' dk')
        self.second_input = QSpinBox()
        self.second_input.setRange(0, 59)
        self.second_input.setSuffix(' sn')
        self.start_button = QPushButton('Başlat')
        self.start_button.setStyleSheet('background-color: #e75480; color: white; font-weight: bold;')
        self.start_button.clicked.connect(self.on_start)
        self.input_layout.addWidget(self.hour_input)
        self.input_layout.addWidget(self.minute_input)
        self.input_layout.addWidget(self.second_input)
        self.input_layout.addWidget(self.start_button)
        self.layout.addLayout(self.input_layout)

        self.timer_label = QLabel(self.format_time(0))
        self.timer_label.setFont(QFont('Arial', 36, QFont.Bold))
        self.timer_label.setStyleSheet('color: #e75480;')  # Pembe
        self.timer_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.timer_label)

        # Alt pembe bant ve yazı
        self.bottom_bar = QLabel()
        self.bottom_bar.setFixedHeight(70)
        self.bottom_bar.setAlignment(Qt.AlignCenter)
        self.bottom_bar.setStyleSheet('background-color: #e75480; color: white; font-size: 32px; font-weight: bold; border-radius: 20px;')
        self.bottom_bar.setText('DEFNEMİN DÖNMESİNE 0 SAAT')
        self.layout.addStretch()
        self.layout.addWidget(self.bottom_bar)
        self.setLayout(self.layout)

    def on_start(self):
        try:
            hours = self.hour_input.value()
            minutes = self.minute_input.value()
            seconds = self.second_input.value()
            self.total_seconds = hours * 3600 + minutes * 60 + seconds
            if self.total_seconds > 0:
                self.timer_label.setText(self.format_time(self.total_seconds))
                self.update_bottom_bar(self.total_seconds)
                self.startTimer()
            else:
                self.bottom_bar.setText('Lütfen süre girin!')
        except Exception as e:
            print('Başlatırken hata:', e)

    def startTimer(self):
        try:
            if self.timer:
                self.timer.stop()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(1000)  # Her saniye
        except Exception as e:
            print('Timer başlatılırken hata:', e)

    def update_timer(self):
        try:
            if self.total_seconds > 0:
                self.total_seconds -= 1
                self.timer_label.setText(self.format_time(self.total_seconds))
                self.update_bottom_bar(self.total_seconds)
            else:
                self.timer.stop()
                self.timer_label.setText('00:00:00:00')
                self.bottom_bar.setText('Defnem geldi!')
        except Exception as e:
            print('Sayaç güncellenirken hata:', e)

    def format_time(self, seconds):
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_info_text(self, seconds):
        hours_left = seconds // 3600
        return f"Defnemin dönmesine {hours_left} saat"

    def update_bottom_bar(self, seconds):
        if seconds > 0:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                self.bottom_bar.setText(f'DEFNEMİN DÖNMESİNE {hours} SAAT {minutes} DAKİKA')
            elif minutes > 0:
                self.bottom_bar.setText(f'DEFNEMİN DÖNMESİNE {minutes} DAKİKA {secs} SANİYE')
            else:
                self.bottom_bar.setText(f'DEFNEMİN DÖNMESİNE {secs} SANİYE')
        else:
            self.bottom_bar.setText('Defnem geldi!')

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        heart_color = QColor('#e75480')
        painter.setBrush(QBrush(heart_color))
        painter.setPen(Qt.NoPen)
        hearts = [
            (60, 60, 40),
            (380, 50, 30),
            (120, 180, 25),
            (300, 170, 35),
            (220, 100, 50)
        ]
        for x, y, size in hearts:
            path = QPainterPath()
            path.moveTo(x + size/2, y + size/5)
            path.cubicTo(x + size, y, x + size, y + size/2, x + size/2, y + size)
            path.cubicTo(x, y + size/2, x, y, x + size/2, y + size/5)
            painter.drawPath(path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CountdownTimer()
    window.show()
    sys.exit(app.exec_()) 