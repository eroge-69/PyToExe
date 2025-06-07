import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTextEdit,
    QVBoxLayout, QWidget, QMenuBar, QAction, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView

class H4XEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("H4X Editor")
        self.setGeometry(100, 100, 1000, 600)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Courier", 10))

        self.web_preview = QWebEngineView()

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.web_preview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.filename = None
        self._create_menu()

    def _create_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        file_menu = menubar.addMenu("File")
        run_menu = menubar.addMenu("Run")

        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        run_action = QAction("Run", self)
        run_action.setShortcut("Ctrl+R")
        run_action.triggered.connect(self.run_code)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        run_menu.addAction(run_action)

    def new_file(self):
        self.text_edit.clear()
        self.filename = None

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open H4X File", "", "H4X Files (*.h4x)")
        if file:
            with open(file, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
            self.filename = file

    def save_file(self):
        if not self.filename:
            file, _ = QFileDialog.getSaveFileName(self, "Save H4X File", "", "H4X Files (*.h4x)")
            if file:
                self.filename = file
        if self.filename:
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())

    def run_code(self):
        code = self.text_edit.toPlainText()

        html, python = self.extract_blocks(code)

        if html:
            with open(".temp_preview.html", "w", encoding='utf-8') as f:
                f.write(html)
            self.web_preview.load(QUrl.fromLocalFile(os.path.abspath(".temp_preview.html")))

        if python:
            try:
                exec(python, {})
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def extract_blocks(self, code):
        html, python = '', ''
        in_html, in_py = False, False
        for line in code.splitlines():
            if '<!-- <html> -->' in line:
                in_html = True
            elif '<!-- </html> -->' in line:
                in_html = False
            elif '<!-- <py> -->' in line:
                in_py = True
            elif '<!-- </py> -->' in line:
                in_py = False
            elif in_html:
                html += line + '\n'
            elif in_py:
                python += line + '\n'
        return html.strip(), python.strip()

if __name__ == '__main__':
    from PyQt5.QtCore import QUrl
    app = QApplication(sys.argv)
    editor = H4XEditor()
    editor.show()
    sys.exit(app.exec_())
