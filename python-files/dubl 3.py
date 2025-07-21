# deduplication_tool.py
# Простий GUI-інструмент на PyQt6 для пошуку та видалення дублікатів з другого файлу відносно першого

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import QDateTime

class DeduplicationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пошук дублікатів")
        self.resize(600, 300)

        central = QWidget(self)
        layout = QVBoxLayout(central)

        self.file1Edit = QLineEdit(self)
        btn1 = QPushButton("Обрати", self)
        btn1.clicked.connect(self.chooseFile1)

        self.file2Edit = QLineEdit(self)
        btn2 = QPushButton("Обрати", self)
        btn2.clicked.connect(self.chooseFile2)

        self.logEdit = QLineEdit(self)
        btn3 = QPushButton("Обрати", self)
        btn3.clicked.connect(self.chooseLogFile)

        self.progressBar = QProgressBar(self)
        runBtn = QPushButton("Почати", self)
        runBtn.clicked.connect(self.startDeduplication)

        layout.addWidget(QLabel("Еталонний файл:"))
        layout.addWidget(self.file1Edit)
        layout.addWidget(btn1)
        layout.addWidget(QLabel("Файл для очищення:"))
        layout.addWidget(self.file2Edit)
        layout.addWidget(btn2)
        layout.addWidget(QLabel("Лог-файл:"))
        layout.addWidget(self.logEdit)
        layout.addWidget(btn3)
        layout.addWidget(self.progressBar)
        layout.addWidget(runBtn)

        self.setCentralWidget(central)

    def chooseFile1(self):
        path, _ = QFileDialog.getOpenFileName(self, "Виберіть еталонний файл")
        if path:
            self.file1Edit.setText(path)

    def chooseFile2(self):
        path, _ = QFileDialog.getOpenFileName(self, "Виберіть файл для очищення")
        if path:
            self.file2Edit.setText(path)

    def chooseLogFile(self):
        path, _ = QFileDialog.getSaveFileName(self, "Виберіть лог-файл", filter="Text Files (*.txt)")
        if path:
            self.logEdit.setText(path)

    def startDeduplication(self):
        file1Path = self.file1Edit.text()
        file2Path = self.file2Edit.text()
        logPath = self.logEdit.text()

        if not file1Path or not file2Path or not logPath:
            QMessageBox.warning(self, "Помилка", "Заповніть всі поля.")
            return

        try:
            with open(file1Path, 'r', encoding='utf-8') as f1:
                seen = set(line.strip() for line in f1 if line.strip())
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити еталонний файл.\n{e}")
            return

        try:
            with open(file2Path, 'r', encoding='utf-8') as f2:
                lines = [line.strip() for line in f2]
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити файл для очищення.\n{e}")
            return

        total = len(lines)
        cleaned = [line for line in lines if line and line not in seen]
        removed = total - len(cleaned)

        try:
            with open(file2Path, 'w', encoding='utf-8') as f2:
                for line in cleaned:
                    f2.write(line + '\n')
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося перезаписати файл.\n{e}")
            return

        try:
            with open(logPath, 'w', encoding='utf-8') as log:
                log.write(f"Загальна кількість рядків у другому файлі: {total}\n")
                log.write(f"Залишено: {len(cleaned)}\n")
                log.write(f"Видалено дублікатів: {removed}\n")
                log.write(f"Час завершення: {QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')}\n")
        except Exception as e:
            QMessageBox.warning(self, "Увага", f"Не вдалося записати лог.\n{e}")

        QMessageBox.information(self, "Готово", f"Очищення завершено. Видалено дублікатів: {removed}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeduplicationTool()
    window.show()
    sys.exit(app.exec())
