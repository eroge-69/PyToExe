import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QLineEdit,
    QVBoxLayout, QMessageBox, QStackedWidget, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

# === CONFIGURATION ===
GAME_EXECUTABLE_PATH = "C:/Path/To/YourGame.exe"  # Change this
VALID_USERNAME = "player"
VALID_PASSWORD = "1234"
LOGO_PATH = "logo.png"  # Optional

class LoginWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.check_login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            self.stacked_widget.setCurrentIndex(1)  # Go to loading screen
            self.stacked_widget.widget(1).start_loading()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid credentials.")


class LoadingScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Loading...")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Loading...")
        self.label.setFont(QFont("Arial", 14))
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def start_loading(self):
        self.progress.setValue(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        self.timer.start(30)  # Update every 30 ms

    def update_progress(self):
        self.progress_value += 2
        self.progress.setValue(self.progress_value)

        if self.progress_value >= 100:
            self.timer.stop()
            self.stacked_widget.setCurrentIndex(2)  # Go to main launcher


class GameLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Game Launcher")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        if os.path.exists(LOGO_PATH):
            logo = QLabel()
            pixmap = QPixmap(LOGO_PATH).scaled(200, 200, Qt.KeepAspectRatio)
            logo.setPixmap(pixmap)
            logo.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo)

        launch_btn = QPushButton("Launch Game")
        launch_btn.clicked.connect(self.launch_game)
        layout.addWidget(launch_btn)

        self.setLayout(layout)

    def launch_game(self):
        if os.path.exists(GAME_EXECUTABLE_PATH):
            os.startfile(GAME_EXECUTABLE_PATH)
        else:
            QMessageBox.critical(self, "Error", "Game executable not found.")


def main():
    app = QApplication(sys.argv)

    # Stack of windows: [0] login → [1] loading → [2] launcher
    stacked_widget = QStackedWidget()

    login = LoginWindow(stacked_widget)
    loading = LoadingScreen(stacked_widget)
    launcher = GameLauncher()

    stacked_widget.addWidget(login)
    stacked_widget.addWidget(loading)
    stacked_widget.addWidget(launcher)

    stacked_widget.setFixedSize(400, 300)
    stacked_widget.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
