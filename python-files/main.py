import os
import sys
import json
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog,
    QVBoxLayout, QListWidget, QMessageBox, QLabel, QHBoxLayout, QListWidgetItem
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize

APP_NAME = "Flashfle AIR"
RUFFLE_EXE = os.path.join("ruffle", "ruffle.exe")
GAMES_JSON = "games.json"
SAVE_BASE_PATH = os.path.expanduser("~\\AppData\\Roaming\\FlashfleAIR\\SaveData")

class RuffleLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setGeometry(200, 100, 700, 500)
        self.setWindowIcon(QIcon("assets/icon.ico"))

        self.games = self.load_games()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(64, 64))

        for game in self.games:
            self.add_game_item(game)
        layout.addWidget(self.list_widget)

        btn_add = QPushButton("Добавить игру")
        btn_add.clicked.connect(self.add_game)
        layout.addWidget(btn_add)

        btn_remove = QPushButton("Удалить выбранную игру")
        btn_remove.clicked.connect(self.remove_game)
        layout.addWidget(btn_remove)

        btn_launch = QPushButton("Запустить игру")
        btn_launch.clicked.connect(self.launch_game)
        layout.addWidget(btn_launch)

        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: Verdana;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #444;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QListWidget {
                background-color: #1e1e1e;
            }
        """)

    def add_game_item(self, game):
        item = QListWidgetItem()
        name = game["name"]
        icon_path = game.get("icon", "")

        if icon_path and os.path.exists(icon_path):
            item.setIcon(QIcon(icon_path))
        else:
            item.setIcon(QIcon("assets/icon.ico"))  # fallback

        item.setText(name)
        self.list_widget.addItem(item)

    def load_games(self):
        if os.path.exists(GAMES_JSON):
            with open(GAMES_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_games(self):
        with open(GAMES_JSON, "w", encoding="utf-8") as f:
            json.dump(self.games, f, indent=4, ensure_ascii=False)

    def add_game(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбери SWF игру", "", "Flash игры (*.swf)")
        if not file_path:
            return

        game_name = os.path.basename(file_path).replace(".swf", "")
        save_path = os.path.join(SAVE_BASE_PATH, game_name)

        icon_path, _ = QFileDialog.getOpenFileName(self, "Выбери иконку игры", "", "Изображения (*.png *.jpg *.ico *.bmp)")
        game_data = {
            "name": game_name,
            "path": file_path,
            "save_dir": save_path,
            "icon": icon_path
        }

        self.games.append(game_data)
        self.save_games()
        self.add_game_item(game_data)

    def remove_game(self):
        selected = self.list_widget.currentRow()
        if selected >= 0:
            self.games.pop(selected)
            self.list_widget.takeItem(selected)
            self.save_games()

    def launch_game(self):
        selected = self.list_widget.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите игру из списка.")
            return

        game = self.games[selected]
        game_path = game["path"]
        save_dir = game["save_dir"]

        os.makedirs(save_dir, exist_ok=True)

        env = os.environ.copy()
        env["FLASH_PLAYER_SAVE_PATH"] = save_dir  # гипотетически

        try:
            subprocess.Popen([RUFFLE_EXE, game_path], env=env)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = RuffleLauncher()
    launcher.show()
    sys.exit(app.exec_())
