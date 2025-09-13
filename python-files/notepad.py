import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit,
    QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction


class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()

        # Главное текстовое поле
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)

        # Параметры окна
        self.setWindowTitle("Блокнот (PyQt6)")
        self.resize(600, 400)

        # Меню
        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()

        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")

        # Кнопки
        open_action = QAction("Открыть", self)
        save_action = QAction("Сохранить", self)
        exit_action = QAction("Выход", self)

        # Добавляем кнопки в меню
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Подключаем действия
        open_action.triggered.connect(self.open_file)
        save_action.triggered.connect(self.save_file)
        exit_action.triggered.connect(self.close)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    self.text_edit.setPlainText(f.read())
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")


def main():
    app = QApplication(sys.argv)
    window = Notepad()
    window.show()
    sys.exit(app.exec())


if name == "__main__":
    main()
