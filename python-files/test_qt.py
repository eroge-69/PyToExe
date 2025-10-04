import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Тестовое окно PyQt6")
    window.resize(400, 200)

    label = QLabel("✅ Приложение работает!")
    label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    layout = QVBoxLayout()
    layout.addStretch()
    layout.addWidget(label)
    layout.addStretch()
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()