import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox, QLineEdit
)
from PyQt6.QtGui import QIcon, QPalette, QColor, QTextCursor
from PyQt6.QtCore import Qt
from docx import Document
from docx.opc.exceptions import PackageNotFoundError

DARK_STYLESHEET = """
QWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-size: 10pt;
}
QMainWindow {
    background-color: #2b2b2b;
}
QPushButton {
    background-color: #3c3f41;
    border: 1px solid #555;
    padding: 8px;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #4f5254;
}
QPushButton:pressed {
    background-color: #5a5e60;
}
QTextEdit {
    background-color: #313335;
    border: 1px solid #555;
    font-family: Consolas, Courier New, monospace;
}
QLabel {
    color: #f0f0f0;
    padding: 2px;
}
QLineEdit {
    background-color: #313335;
    border: 1px solid #555;
    padding: 5px;
    color: #f0f0f0;
}
QMessageBox {
    background-color: #2b2b2b;
}
QMessageBox QLabel {
    color: #f0f0f0;
}
"""


class DocxCleanerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.input_doc_path = None
        self.output_doc_path = None

        self.watermark_char_map_preview = {
            '°': '[°]',
            '\u202F': '[U+202F]',
            '\u00A0': '[U+00A0]',
            ' ': '·',
            '\t': '[\\t]',
            '\n': '[\\n]\n'
        }
        self.chars_to_replace_in_doc = ['°', '\u202F', '\u00A0']
        self.replacement_char_for_doc = ' '

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Docx Watermark Cleaner")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        file_io_layout = QHBoxLayout()

        self.btn_load_input = QPushButton("1. Загрузить DOCX")
        self.btn_load_input.clicked.connect(self.load_input_file)
        file_io_layout.addWidget(self.btn_load_input)

        self.input_file_label = QLineEdit("")
        self.input_file_label.setPlaceholderText("Файл не выбран")
        self.input_file_label.setReadOnly(True)
        file_io_layout.addWidget(self.input_file_label, 1)

        self.btn_select_output = QPushButton("2. Куда сохранить")
        self.btn_select_output.clicked.connect(self.select_output_file)
        file_io_layout.addWidget(self.btn_select_output)

        self.output_file_label = QLineEdit("")
        self.output_file_label.setPlaceholderText("Место не выбрано")
        self.output_file_label.setReadOnly(True)
        file_io_layout.addWidget(self.output_file_label, 1)

        main_layout.addLayout(file_io_layout)

        preview_label = QLabel("Предпросмотр (спец. символы отмечены):")
        main_layout.addWidget(preview_label)
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        main_layout.addWidget(self.preview_area, 1)

        process_layout = QHBoxLayout()
        self.btn_process = QPushButton("3. Очистить документ")
        self.btn_process.clicked.connect(self.process_document)
        process_layout.addWidget(self.btn_process)

        self.status_label = QLabel("Статус: Готов")
        process_layout.addWidget(self.status_label, 1)

        main_layout.addLayout(process_layout)

        self.btn_select_output.setEnabled(False)
        self.btn_process.setEnabled(False)

    def load_input_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите DOCX файл", "", "Word Documents (*.docx)")
        if path:
            self.input_doc_path = path
            self.input_file_label.setText(os.path.basename(path))
            self.status_label.setText(f"Загружен: {os.path.basename(path)}")
            self.preview_document()
            self.btn_select_output.setEnabled(True)
            self.output_doc_path = None
            self.output_file_label.setText("")
            self.btn_process.setEnabled(False)

    def select_output_file(self):
        if not self.input_doc_path:
            QMessageBox.warning(self, "Внимание", "Сначала загрузите исходный файл.")
            return

        input_dir = os.path.dirname(self.input_doc_path)
        input_filename = os.path.basename(self.input_doc_path)
        name, ext = os.path.splitext(input_filename)
        default_output_name = os.path.join(input_dir, f"{name}_cleaned{ext}")

        path, _ = QFileDialog.getSaveFileName(self, "Сохранить очищенный DOCX", default_output_name,
                                              "Word Documents (*.docx)")
        if path:
            self.output_doc_path = path
            self.output_file_label.setText(os.path.basename(path))
            self.status_label.setText(f"Готов к сохранению в: {os.path.basename(path)}")
            if self.input_doc_path:
                self.btn_process.setEnabled(True)

    def preview_document(self):
        if not self.input_doc_path:
            return
        self.preview_area.clear()
        self.preview_area.setText("Загрузка предпросмотра...")
        QApplication.processEvents()

        try:
            doc = Document(self.input_doc_path)
            full_preview_text = ""

            def generate_preview_for_text_segment(text_segment):
                preview_parts = []
                for char_code in text_segment:
                    char = char_code
                    handled = False
                    for key, val in self.watermark_char_map_preview.items():
                        if char == key:
                            preview_parts.append(val)
                            handled = True
                            break
                    if not handled:
                        if 0 <= ord(char) < 32 and char not in ['\n', '\t', '\r']:
                            preview_parts.append(f'[0x{ord(char):02X}]')
                        else:
                            preview_parts.append(char)
                return "".join(preview_parts)

            for para_idx, para in enumerate(doc.paragraphs):
                full_preview_text += generate_preview_for_text_segment(para.text)
                full_preview_text += "[P]\n"

            if doc.tables:
                full_preview_text += "\n--- ТАБЛИЦЫ ---\n"
            for table_idx, table in enumerate(doc.tables):
                full_preview_text += f"\nТаблица {table_idx + 1}:\n"
                for row_idx, row in enumerate(table.rows):
                    row_preview_parts = []
                    for cell_idx, cell in enumerate(row.cells):
                        cell_content_preview = generate_preview_for_text_segment(cell.text)
                        row_preview_parts.append(f"[Ячейка {row_idx + 1},{cell_idx + 1}: {cell_content_preview}]")
                    full_preview_text += " | ".join(row_preview_parts) + "\n"
                full_preview_text += "---\n"

            self.preview_area.setText(full_preview_text.strip())
            self.status_label.setText("Предпросмотр загружен.")
        except PackageNotFoundError:
            self.preview_area.setText("Ошибка: Не удалось открыть файл (возможно, он поврежден или это не .docx).")
            self.status_label.setText("Ошибка загрузки предпросмотра.")
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть файл. Убедитесь, что это корректный .docx файл.")
            self.input_doc_path = None
            self.input_file_label.setText("")
            self.btn_select_output.setEnabled(False)
            self.btn_process.setEnabled(False)
        except Exception as e:
            self.preview_area.setText(f"Ошибка при генерации предпросмотра: {str(e)}")
            self.status_label.setText("Ошибка загрузки предпросмотра.")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def process_document(self):
        if not self.input_doc_path or not self.output_doc_path:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите исходный и конечный файлы.")
            return

        self.status_label.setText("Обработка...")
        QApplication.processEvents()

        try:
            doc = Document(self.input_doc_path)
            total_replacements_count = 0

            def clean_runs_in_element(runs_collection):
                nonlocal total_replacements_count
                for run in runs_collection:
                    original_text = run.text
                    modified_text = original_text
                    current_run_replacements = 0
                    for char_to_find in self.chars_to_replace_in_doc:
                        if char_to_find in modified_text:
                            current_run_replacements += modified_text.count(char_to_find)
                            modified_text = modified_text.replace(char_to_find, self.replacement_char_for_doc)

                    if original_text != modified_text:
                        run.text = modified_text
                        total_replacements_count += current_run_replacements

            for para in doc.paragraphs:
                clean_runs_in_element(para.runs)

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for para in cell.paragraphs:
                            clean_runs_in_element(para.runs)

            doc.save(self.output_doc_path)
            self.status_label.setText(
                f"Готово! Замен: {total_replacements_count}. Сохранено в {os.path.basename(self.output_doc_path)}")
            QMessageBox.information(self, "Успех",
                                    f"Документ успешно очищен и сохранен.\nПроизведено замен: {total_replacements_count}")

        except Exception as e:
            self.status_label.setText(f"Ошибка обработки: {str(e)}")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при обработке или сохранении файла: {str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)

    window = DocxCleanerApp()
    window.show()
    sys.exit(app.exec())
