import sys
import webbrowser
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt


class MTALauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Launcher MTA RP")
        self.setFixedSize(900, 600)

        # Imagem de fundo
        self.set_background("background.jpg")

        # Logo do servidor
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap("logo.png").scaled(220, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo.move(340, 30)

        # Banner decorativo (opcional)
        if os.path.exists("banner.png"):
            self.banner = QLabel(self)
            self.banner.setPixmap(QPixmap("banner.png").scaled(800, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.banner.move(50, 130)

        # Botões
        self.add_button("Iniciar MTA", 240, self.start_mta)
        self.add_button("Site Oficial", 310, lambda: webbrowser.open("https://www.youtube.com/watch?v=VbSKO6AoaD4"))
        self.add_button("Discord", 380, lambda: webbrowser.open("https://discord.gg/yw5bG3Ru"))

        # Rodapé
        self.footer = QLabel("Servidor Roleplay © 2025", self)
        self.footer.setStyleSheet("color: white; font-size: 12px;")
        self.footer.move(20, 570)

    def set_background(self, image_path):
        self.setAutoFillBackground(True)
        palette = self.palette()
        pixmap = QPixmap(image_path).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

    def add_button(self, text, y, action):
        btn = QPushButton(text, self)
        btn.setGeometry(350, y, 200, 40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border: 2px solid #555;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        btn.clicked.connect(action)

def start_mta(self):
    try:
        ip = "192.168.0.100"  # 🡐 Coloque aqui o IP do seu servidor
        porta = "22003"       # 🡐 Coloque a porta do seu servidor
        caminho = '"C:\\Program Files (x86)\\MTA San Andreas 1.6\\Multi Theft Auto.exe"'
        os.system(f'{caminho} mtasa://192.168.56.1:22003')
    except Exception as e:
        print("Erro ao iniciar o MTA:", e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    launcher = MTALauncher()
    launcher.show()
    sys.exit(app.exec_())
