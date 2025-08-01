import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidget, QLineEdit, 
                             QPushButton, QTabWidget, QFileDialog, QLabel)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt

class ProgramLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.programs = []
        self.load_programs()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Game Launcher")
        self.setGeometry(300, 300, 600, 400)

        # Поиск
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Поиск...")
        self.search_bar.textChanged.connect(self.update_list)
        self.search_bar.move(10, 10)

        # Вкладки (категории)
        self.tabs = QTabWidget(self)
        self.tabs.setGeometry(10, 50, 580, 300)

        # Список программ
        self.program_list = QListWidget(self.tabs)
        self.program_list.itemDoubleClicked.connect(self.run_program)
        self.tabs.addTab(self.program_list, "Все")

        # Кнопки
        self.add_btn = QPushButton("Добавить", self)
        self.add_btn.clicked.connect(self.add_program)
        self.add_btn.move(10, 360)

        self.del_btn = QPushButton("Удалить", self)
        self.del_btn.clicked.connect(self.delete_program)
        self.del_btn.move(120, 360)

        self.update_list()

    def load_programs(self):
        if os.path.exists("programs.json"):
            with open("programs.json", "r", encoding="utf-8") as f:
                self.programs = json.load(f)

    def save_programs(self):
        with open("programs.json", "w", encoding="utf-8") as f:
            json.dump(self.programs, f, ensure_ascii=False, indent=4)

    def update_list(self):
        self.program_list.clear()
        search_text = self.search_bar.text().lower()
        
        for prog in self.programs:
            if search_text in prog["name"].lower():
                item = QListWidgetItem(QIcon(prog.get("icon", "")), prog["name"])
                self.program_list.addItem(item)

    def add_program(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if path:
            name = os.path.basename(path).split('.')[0]
            icon = QFileDialog.getOpenFileName(self, "Выберите иконку (опционально)", "", "*.ico")[0]
            category = "Игры"  # Можно добавить выбор категории
            
            self.programs.append({"name": name, "path": path, "icon": icon, "category": category})
            self.save_programs()
            self.update_list()

    def delete_program(self):
        selected = self.program_list.currentRow()
        if selected >= 0:
            self.programs.pop(selected)
            self.save_programs()
            self.update_list()

    def run_program(self, item):
        selected = self.program_list.row(item)
        if selected >= 0:
            os.startfile(self.programs[selected]["path"])
            self.close()  # Закрываем лаунчер после запуска

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = ProgramLauncher()
    launcher.show()
    sys.exit(app.exec())