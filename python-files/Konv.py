import sys
import os
import ezdxf
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
)
from PyQt5.QtCore import Qt

class BatchDXFProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DXF Batch Processor")
        self.setGeometry(300, 150, 900, 600)

        self.files = []

        self.layout = QVBoxLayout()

        self.header = QLabel("<h2 style='color: #2c3e50;'>Обработка DXF файлов</h2>")
        self.header.setAlignment(Qt.AlignCenter)

        self.select_btn = QPushButton("Выбрать DXF файлы")
        self.process_btn = QPushButton("Модифицировать")
        self.status_label = QLabel("")

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Путь к файлу", "Порог удаления текста"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.select_btn.clicked.connect(self.select_files)
        self.process_btn.clicked.connect(self.modify_files)

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.select_btn)
        self.layout.addWidget(self.process_btn)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)
        self.setStyleSheet("""
            QWidget { font-family: 'Segoe UI', sans-serif; font-size: 10pt; background-color: #f9f9f9; }
            QPushButton {
                padding: 10px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget { border: 1px solid #ccc; background-color: white; }
            QHeaderView::section { background-color: #ecf0f1; padding: 4px; border: 1px solid #ddd; }
            QLabel { padding: 10px; }
        """)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выбрать DXF файлы", "", "DXF files (*.dxf)")
        if files:
            self.files = files
            self.table.setRowCount(len(files))
            for row, file in enumerate(files):
                self.table.setItem(row, 0, QTableWidgetItem(file))
                self.table.setItem(row, 1, QTableWidgetItem(""))

    def modify_files(self):
        if not self.files:
            QMessageBox.warning(self, "Нет файлов", "Сначала выберите DXF файлы.")
            return

        for row in range(self.table.rowCount()):
            file_path = self.table.item(row, 0).text()
            threshold_item = self.table.item(row, 1)
            threshold = None

            if threshold_item:
                try:
                    text = threshold_item.text().replace(',', '.')
                    threshold = float(text)
                except ValueError:
                    threshold = None

            try:
                doc = ezdxf.readfile(file_path)
                msp = doc.modelspace()

                for insert in msp.query('INSERT'):
                    for attrib in list(insert.attribs):
                        msp.add_text(attrib.dxf.text, dxfattribs={
                            'insert': attrib.dxf.insert,
                            'height': getattr(attrib.dxf, 'height', 2.5),
                            'layer': attrib.dxf.layer
                        })
                        attrib.destroy()

                entities_to_remove = [e for e in msp if e.dxf.layer.upper() == "PLAST"]
                for e in entities_to_remove:
                    msp.delete_entity(e)
                try:
                    doc.layers.remove("PLAST")
                except ValueError:
                    pass

                text_entities = list(msp.query("TEXT MTEXT"))
                for e in text_entities:
                    value = None
                    if e.dxftype() == 'TEXT':
                        try:
                            value = float(e.dxf.text.replace(',', '.'))
                        except:
                            pass
                        e.dxf.height = 0.09
                        ins = e.dxf.insert
                        e.dxf.insert = (ins.x, ins.y + 0.5, ins.z)
                    elif e.dxftype() == 'MTEXT':
                        try:
                            value = float(e.text.replace(',', '.'))
                        except:
                            pass
                        e.dxf.char_height = 0.09
                        ins = e.dxf.insert
                        e.dxf.insert = (ins.x, ins.y + 0.5, ins.z)

                    if threshold is not None and value is not None and value < threshold:
                        msp.delete_entity(e)

                dir_name = os.path.dirname(file_path)
                base_name = os.path.basename(file_path)
                new_name = os.path.join(dir_name, f"Mod_{base_name}")
                doc.saveas(new_name)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка обработки {file_path}:\n{str(e)}")
                return

        self.status_label.setText("<b>Обработка завершена. Файлы сохранены.</b>")
        QMessageBox.information(self, "Готово", "Все файлы успешно модифицированы.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BatchDXFProcessor()
    window.show()
    sys.exit(app.exec_())
