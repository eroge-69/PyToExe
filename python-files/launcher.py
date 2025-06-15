import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QGridLayout,
    QScrollArea, QVBoxLayout, QHBoxLayout, QSlider, QComboBox, QDialog
)
from PyQt5.QtCore import Qt, QTimer, QTime, QDate
from PyQt5.QtGui import QIcon
import pygame

SETTINGS_FILE = "settings.json"
GAMES_FOLDER = "games"
ASSETS_FOLDER = "assets"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "music_volume": 0.2,
            "sfx_volume": 0.5,
            "resolution": [640, 480],
            "fullscreen": True,
            "theme": "light",
            "box_color": "#444444"
        }

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

class SettingsWindow(QDialog):
    def __init__(self, settings, on_save_callback):
        super().__init__()
        self.setWindowTitle("Settings")
        self.settings = settings
        self.on_save = on_save_callback
        self.setFixedSize(400, 350)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Music Volume"))
        self.music_slider = QSlider(Qt.Horizontal)
        self.music_slider.setRange(0, 100)
        self.music_slider.setValue(int(self.settings.get("music_volume", 0.2) * 100))
        layout.addWidget(self.music_slider)

        layout.addWidget(QLabel("SFX Volume"))
        self.sfx_slider = QSlider(Qt.Horizontal)
        self.sfx_slider.setRange(0, 100)
        self.sfx_slider.setValue(int(self.settings.get("sfx_volume", 0.5) * 100))
        layout.addWidget(self.sfx_slider)

        layout.addWidget(QLabel("Resolution"))
        self.res_combo = QComboBox()
        resolutions = [
            "640x480", "800x600", "1024x768",
            "1280x720", "1366x768", "1440x900", "1920x1080"
        ]
        for r in resolutions:
            self.res_combo.addItem(r)
        current_res = f"{self.settings.get('resolution', [640,480])[0]}x{self.settings.get('resolution', [640,480])[1]}"
        self.res_combo.setCurrentText(current_res)
        layout.addWidget(self.res_combo)

        layout.addWidget(QLabel("Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "light"))
        layout.addWidget(self.theme_combo)

        layout.addWidget(QLabel("Box Color"))
        self.box_combo = QComboBox()
        self.box_combo.addItems(["#444444", "#666666", "#888888", "#AAAAAA"])
        self.box_combo.setCurrentText(self.settings.get("box_color", "#444444"))
        layout.addWidget(self.box_combo)

        btn_restart = QPushButton("Restart Launcher")
        btn_restart.clicked.connect(self.restart_launcher)
        layout.addWidget(btn_restart)

        btn_shutdown = QPushButton("Shutdown System")
        btn_shutdown.clicked.connect(self.shutdown_system)
        layout.addWidget(btn_shutdown)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_and_close)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def save_and_close(self):
        self.settings["music_volume"] = self.music_slider.value() / 100.0
        self.settings["sfx_volume"] = self.sfx_slider.value() / 100.0
        w, h = map(int, self.res_combo.currentText().split('x'))
        self.settings["resolution"] = [w, h]
        self.settings["theme"] = self.theme_combo.currentText()
        self.settings["box_color"] = self.box_combo.currentText()
        save_settings(self.settings)
        self.on_save()
        self.close()

    def restart_launcher(self):
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def shutdown_system(self):
        if sys.platform == "win32":
            subprocess.call(["shutdown", "/s", "/t", "0"])
        else:
            subprocess.call(["shutdown", "-h", "now"])

class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.sfx_volume = self.settings.get("sfx_volume", 0.5)
        self.setWindowTitle("Game Launcher")
        w, h = self.settings.get("resolution", [640, 480])
        self.setGeometry(0, 0, w, h)

        pygame.mixer.init()
        self.click_sound = None
        self.load_sfx()

        self.initUI()
        self.apply_settings()

    def load_sfx(self):
        click_path = os.path.join(ASSETS_FOLDER, "click.wav")
        if os.path.exists(click_path):
            self.click_sound = pygame.mixer.Sound(click_path)
            self.click_sound.set_volume(self.sfx_volume)

    def play_click(self):
        if self.click_sound:
            self.click_sound.play()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Üstte tam genişlikte başlık
        self.title_label = QLabel("Game Launcher")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
        main_layout.addWidget(self.title_label)

        # Sağ üstte versiyon ve saat için layout
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        self.version_label = QLabel("Launcher v1.0")
        self.version_label.setStyleSheet("color: black; font-weight: bold; font-size: 16px;")
        top_bar.addWidget(self.version_label)

        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: black; font-weight: normal; font-size: 14px; margin-left: 10px;")
        top_bar.addWidget(self.datetime_label)

        main_layout.addLayout(top_bar)

        btn_settings_layout = QHBoxLayout()
        btn_settings_layout.addStretch()
        btn_settings = QPushButton("Settings")
        btn_settings.clicked.connect(self.open_settings)
        btn_settings_layout.addWidget(btn_settings)
        main_layout.addLayout(btn_settings_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid = QGridLayout(scroll_content)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        central_widget.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

        self.load_games()

        music_path = os.path.join(ASSETS_FOLDER, "theme.mp3")
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.settings.get("music_volume", 0.2))
            pygame.mixer.music.play(-1)

    def update_datetime(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        current_date = QDate.currentDate().toString("dd.MM.yyyy")
        self.datetime_label.setText(f"{current_date} {current_time}")

    def load_games(self):
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not os.path.exists(GAMES_FOLDER):
            os.makedirs(GAMES_FOLDER)

        exe_files = []
        for root, dirs, files in os.walk(GAMES_FOLDER):
            for file in files:
                if file.lower().endswith(".exe"):
                    full_path = os.path.join(root, file)
                    exe_files.append(full_path)

        row = 0
        col = 0
        for exe_path in exe_files:
            file_name = os.path.basename(exe_path)
            display_name = file_name[:-4] if file_name.lower().endswith(".exe") else file_name

            btn = QPushButton()
            btn.setFixedSize(150, 150)
            btn.setText(display_name)
            icon = QIcon(exe_path)
            if icon.isNull():
                icon_path = os.path.join(ASSETS_FOLDER, "default_icon.png")
                if os.path.exists(icon_path):
                    icon = QIcon(icon_path)
            btn.setIcon(icon)
            btn.setIconSize(btn.size() * 0.7)
            box_color = self.settings.get("box_color", "#444444")
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: bottom;
                    background-color: {box_color};
                    color: black;
                    border-radius: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #666;
                }}
            """)
            btn.clicked.connect(lambda checked, p=exe_path: self.launch_game(p))
            self.grid.addWidget(btn, row, col)
            col += 1
            if col >= 6:
                col = 0
                row += 1

    def launch_game(self, exe_path):
        self.play_click()
        try:
            subprocess.Popen([exe_path], shell=True)
        except Exception as e:
            print(f"Failed to launch {exe_path}:\n{e}")

    def open_settings(self):
        self.settings_window = SettingsWindow(self.settings, self.apply_settings)
        self.settings_window.show()

    def apply_settings(self):
        pygame.mixer.music.set_volume(self.settings.get("music_volume", 0.2))
        self.sfx_volume = self.settings.get("sfx_volume", 0.5)
        if self.click_sound:
            self.click_sound.set_volume(self.sfx_volume)
        w, h = self.settings.get("resolution", [640, 480])
        self.setGeometry(0, 0, w, h)
        if self.settings.get("fullscreen", True):
            self.showFullScreen()
        else:
            self.showNormal()
        self.load_games()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    launcher = Launcher()
    launcher.showFullScreen()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
