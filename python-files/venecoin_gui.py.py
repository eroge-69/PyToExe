import sys, os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QGridLayout, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QPixmap

CONFIG_FILE = "venecoin_config.txt"

class VenecoinMiner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minero + Venecoin")
        self.setFixedSize(750, 420)
        self.setStyleSheet("""
            QWidget { background-color: #F8FAFC; color: #2E3440; }
            QLabel#header { font-size: 20px; font-weight: bold; color: #3B4252; }
            QLineEdit { padding: 6px; border: 2px solid #88C0D0; border-radius: 4px; }
            QPushButton {
                background-color: #88C0D0;
                color: #2E3440;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #81A1C1; }
        """)
        self.build_ui()
        self.load_config()
        self.start_clock()
        self.add_translucent_logo()

    def build_ui(self):
        layout = QVBoxLayout(self)

        # Encabezado y reloj
        header_layout = QHBoxLayout()
        header = QLabel("Bienvenidos a Venecoin ingresar sus datos")
        header.setObjectName("header")
        header_layout.addWidget(header)
        header_layout.addStretch()
        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(self.clock)
        layout.addLayout(header_layout)

        # Campos
        grid = QGridLayout()
        fields = [
            ("Usuario", False),
            ("Contraseña", True),
            ("Dirección de la wallet", False),
            ("Ruta de venecoin.exe", False),
            ("Ruta del minero cpuminer", False)
        ]
        self.inputs = {}
        for i, (label, is_pass) in enumerate(fields):
            lbl = QLabel(label)
            grid.addWidget(lbl, i, 0)
            le = QLineEdit()
            if is_pass:
                le.setEchoMode(QLineEdit.Password)
            grid.addWidget(le, i, 1)
            if "Ruta" in label:
                btn = QPushButton("Examinar")
                btn.clicked.connect(lambda _, e=le: self.browse_file(e))
                grid.addWidget(btn, i, 2)
            self.inputs[label] = le
        layout.addLayout(grid)

        # Botones
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar configuración")
        save_btn.clicked.connect(self.save_config)
        run_btn = QPushButton("Ejecutar minero")
        run_btn.clicked.connect(self.run_miner)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(run_btn)
        layout.addLayout(btn_layout)

    def start_clock(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

    def update_clock(self):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd  hh:mm:ss")
        self.clock.setText(now)

    def browse_file(self, line_edit):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo", "", "Ejecutables (*.exe);;Todos (*.*)"
        )
        if path:
            line_edit.setText(path)

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            for label, le in self.inputs.items():
                f.write(f"{label}={le.text()}\n")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                for line in f:
                    if "=" in line:
                        key, val = line.strip().split("=", 1)
                        if key in self.inputs:
                            self.inputs[key].setText(val)

    def run_miner(self):
        cfg = {k: le.text() for k, le in self.inputs.items()}
        miner_dir = os.path.dirname(cfg["Ruta del minero cpuminer"]) or "C:/"
        commands = [
            "@echo off",
            "title Minero + Venecoin",
            f'cd /d "{miner_dir}"',
            f'start "" "{cfg["Ruta de venecoin.exe"]}"',
            f'minerd.exe -a scrypt -o http://127.0.0.1:22557 '
            f'-u {cfg["Usuario"]} -p {cfg["Contraseña"]} '
            f'--coinbase-addr={cfg["Dirección de la wallet"]}'
        ]
        with open("run_venecoin.bat", "w") as f:
            f.write("\n".join(commands))
        os.startfile("run_venecoin.bat")

    def add_translucent_logo(self):
        logo = QLabel(self)
        pixmap = QPixmap("venecoin_logo.png")  # Asegúrate de tener esta imagen en tu carpeta
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setGeometry(520, 180, 200, 200)
        opacity = QGraphicsOpacityEffect()
        opacity.setOpacity(0.25)
        logo.setGraphicsEffect(opacity)
        logo.lower()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VenecoinMiner()
    win.show()
    sys.exit(app.exec())