from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from update_manager import download_and_apply_update

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Safari System")
        self.setGeometry(300, 200, 400, 200)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        update_button = QPushButton("🔄 تحديث البرنامج")
        update_button.clicked.connect(lambda: download_and_apply_update(self))

        layout.addWidget(update_button)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)