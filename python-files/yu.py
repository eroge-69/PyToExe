# my_code_editor.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog,
    QTabWidget, QWidget, QVBoxLayout, QAction, QMenu
)
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt

# Класс редактора кода
class CodeEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 12))
        self.setStyleSheet("""
            background-color: #1e1e2f;
            color: #ffffff;
            selection-background-color: #ff9800;
            border: none;
        """)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

# Основное окно редактора
class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌟 PyCode Editor 🌟")
        self.resize(1000, 700)
        self.setStyleSheet("background-color: #2b2b3f; color: #ffffff;")

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Добавляем первую вкладку
        self.add_tab()

        # Создаем меню
        self.create_menu()

    def create_menu(self):
        menu = self.menuBar()
        menu.setStyleSheet("background-color: #111; color: #fff;")

        # Файл
        file_menu = menu.addMenu("Файл")
        new_action = QAction("Новый", self)
        new_action.triggered.connect(self.add_tab)
        open_action = QAction("Открыть...", self)
        open_action.triggered.connect(self.open_file)
        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)

        # Правка
        edit_menu = menu.addMenu("Правка")
        undo_action = QAction("Отменить", self)
        undo_action.triggered.connect(self.undo)
        redo_action = QAction("Повторить", self)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

    def add_tab(self):
        editor = CodeEditor()
        tab_index = self.tabs.addTab(editor, "Новый файл")
        self.tabs.setCurrentIndex(tab_index)

    def close_tab(self, index):
        self.tabs.removeTab(index)

    def current_editor(self):
        return self.tabs.currentWidget()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Python Files (*.py);;All Files (*)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            editor = CodeEditor()
            editor.setText(text)
            filename = path.split("/")[-1]
            tab_index = self.tabs.addTab(editor, filename)
            self.tabs.setCurrentIndex(tab_index)

    def save_file(self):
        editor = self.current_editor()
        if editor:
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Python Files (*.py);;All Files (*)")
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(editor.toPlainText())
                filename = path.split("/")[-1]
                self.tabs.setTabText(self.tabs.currentIndex(), filename)

    def undo(self):
        editor = self.current_editor()
        if editor:
            editor.undo()

    def redo(self):
        editor = self.current_editor()
        if editor:
            editor.redo()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    sys.exit(app.exec())
