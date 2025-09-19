import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit,
    QFileDialog, QMessageBox, QMenuBar
)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Program z oknami dialogowymi - PySide6")
        self.resize(800, 600)

        # Pole tekstowe w centrum
        self.text_edit = QTextEdit()
        self.setCentralWidget(self.text_edit)

        # Pasek menu
        menu_bar = self.menuBar()

        # Menu Plik
        file_menu = menu_bar.addMenu("Plik")

        open_action = QAction("Otwórz...", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Zapisz jako...", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        exit_action = QAction("Zakończ", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Pomoc
        help_menu = menu_bar.addMenu("Pomoc")

        about_action = QAction("O programie", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def open_file(self):
        """Dialog otwierania pliku"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Otwórz plik", "", "Pliki tekstowe (*.txt);;Wszystkie pliki (*.*)")
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.text_edit.setText(content)
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć pliku:\n{e}")

    def save_file(self):
        """Dialog zapisywania pliku"""
        file_name, _ = QFileDialog.getSaveFileName(self, "Zapisz plik", "", "Pliki tekstowe (*.txt);;Wszystkie pliki (*.*)")
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    content = self.text_edit.toPlainText()
                    f.write(content)
                QMessageBox.information(self, "Sukces", "Plik został zapisany.")
            except Exception as e:
                QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać pliku:\n{e}")

    def show_about(self):
        """Okno dialogowe - o programie"""
        QMessageBox.information(self, "O programie", "To jest przykładowy program z oknami dialogowymi w PySide6.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
