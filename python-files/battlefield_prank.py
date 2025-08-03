import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class BattlefieldWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Battlefield 6 - BETA 0.17.0")
        self.setGeometry(100, 100, 800, 600)
        
        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a mock game label
        label = QLabel("Battlefield 6 - BETA 0.17.0\nLoading Game Assets...\n[PRANK VERSION]", self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 24, QFont.Bold))
        label.setStyleSheet("color: white; background-color: black;")
        layout.addWidget(label)
        
        # Set window background to dark for game-like feel
        self.setStyleSheet("background-color: #1a1a1a;")
        
        # Make window appear more authentic by disabling maximize
        self.setFixedSize(800, 600)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BattlefieldWindow()
    window.show()
    sys.exit(app.exec_())