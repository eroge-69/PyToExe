import sys
import os
import tempfile
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt

class ExcelPrinter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel印刷プレビュー（一時ファイル）")
        self.resize(1000, 800)
        self.data = None
        self.current_page = 0
        self.max_preview_pages = 5
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        load_button = QPushButton("CSVまたはExcelファイルを読み込む")
        load_button.clicked.connect(self.load_file)
        self.layout.addWidget(load_button)

        self.column_list = QListWidget()
        self.layout.addWidget(QLabel("列順序と印刷選択"))
        self.layout.addWidget(self.column_list)

        reorder_layout = QHBoxLayout()
        self.up_button = QPushButton("↑ 上へ移動")
        self.up_button.clicked.connect(self.move_column_up)
        reorder_layout.addWidget(self.up_button)
        self.down_button = QPushButton("↓ 下へ移動")
        self.down_button.clicked.connect(self.move_column_down)
        reorder_layout.addWidget(self.down_button)
        self.layout.addLayout(reorder_layout)

        update_button = QPushButton("表の更新")
        update_button.clicked.connect(self.update_table)
        self.layout.addWidget(update_button)

        self.rows_per_page = QSpinBox()
        self.rows_per_page.setRange(10, 100)
        self.rows_per_page.setValue(30)
        self.layout.addWidget(QLabel("1ページあたりの行数"))
        self.layout.addWidget(self.rows_per_page)

        self.repeat_header = QCheckBox("各ページにヘッダーを繰り返す")
        self.repeat_header.setChecked(True)
        self.layout.addWidget(self.repeat_header)

        self.add_borders = QCheckBox("セルに外枠線を追加")
        self.add_borders.setChecked(True)
        self.layout.addWidget(self.add_borders)

        preview_button = QPushButton("Excelでプレビュー（保存せず）")
        preview_button.clicked.connect(self.export_and_preview_excel)
        self.layout.addWidget(preview_button)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("前へ")
        self.prev_button.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_button)
        self.page_label = QLabel("ページ 1 / 1")
        nav_layout.addWidget(self.page_label)
        self.next_button = QPushButton("次へ")
        self.next_button.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_button)
        self.layout.addLayout(nav_layout)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "ファイルを選択", "", "CSVファイル (*.csv);;Excelファイル (*.xlsx *.xls)"
        )
        if file_path:
            try:
                if file_path.endswith(".csv"):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith(".xlsx"):
                    self.data = pd.read_excel(file_path, engine="openpyxl")
                elif file_path.endswith(".xls"):
                    self.data = pd.read_excel(file_path, engine="xlrd")
                self.populate_column_list()
            except Exception as e:
                QMessageBox.critical(self, "ファイル読み込みエラー", f"ファイルの読み込みに失敗しました:\n{e}")

    def populate_column_list(self):
        self.column_list.clear()
        for col in self.data.columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked)
            self.column_list.addItem(item)
        self.current_page = 0
        self.update_table()

    def move_column_up(self):
        current_row = self.column_list.currentRow()
        if current_row > 0:
            item = self.column_list.takeItem(current_row)
            self.column_list.insertItem(current_row - 1, item)
            self.column_list.setCurrentRow(current_row - 1)

    def move_column_down(self):
        current_row = self.column_list.currentRow()
        if current_row < self.column_list.count() - 1:
            item = self.column_list.takeItem(current_row)
            self.column_list.insertItem(current_row + 1, item)
            self.column_list.setCurrentRow(current_row + 1)

    def get_selected_columns(self):
        columns = []
        for i in range(self.column_list.count()):
            item = self.column_list.item(i)
            if item.checkState() == Qt.Checked:
                columns.append(item.text())
        return columns

    def update_table(self):
        if self.data is None:
            return
        selected_columns = self.get_selected_columns()
        filtered_data = self.data[selected_columns]
        rows_per_page = self.rows_per_page.value()
        total_pages = min((len(filtered_data) - 1) // rows_per_page + 1, self.max_preview_pages)
        self.current_page = max(0, min(self.current_page, total_pages - 1))
        start_row = self.current_page * rows_per_page
        end_row = min(start_row + rows_per_page, len(filtered_data))
        self.table.setRowCount(end_row - start_row)
        self.table.setColumnCount(len(selected_columns))
        self.table.setHorizontalHeaderLabels(selected_columns)
        for i in range(start_row, end_row):
            for j, col in enumerate(selected_columns):
                item = QTableWidgetItem(str(filtered_data.iloc[i][col]))
                self.table.setItem(i - start_row, j, item)
        self.table.resizeColumnsToContents()
        self.page_label.setText(f"ページ {self.current_page + 1} / {total_pages}")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        selected_columns = self.get_selected_columns()
        if self.data is None or not selected_columns:
            return
        rows_per_page = self.rows_per_page.value()
        total_pages = min((len(self.data[selected_columns]) - 1) // rows_per_page + 1, self.max_preview_pages)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_table()

    def export_and_preview_excel(self):
        if self.data is None:
            return
        selected_columns = self.get_selected_columns()
        filtered_data = self.data[selected_columns]
        rows_per_page = self.rows_per_page.value()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            output_path = tmp.name
        try:
            with pd.ExcelWriter(
                output_path,
                engine='xlsxwriter',
                engine_kwargs={'options': {'nan_inf_to_errors': True}}
            ) as writer:
                filtered_data.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                worksheet.set_paper(9)  # A4
                worksheet.set_landscape()
                worksheet.set_margins(left=0.2, right=0.2, top=0.2, bottom=0.2)
                worksheet.center_horizontally()
                worksheet.center_vertically()
                worksheet.fit_to_pages(1, 0)
                if self.repeat_header.isChecked():
                    worksheet.repeat_rows(0)
                total_rows = len(filtered_data)
                page_breaks = [i for i in range(rows_per_page, total_rows, rows_per_page)]
                worksheet.set_h_pagebreaks(page_breaks)
                font_size = max(8, 14 - len(selected_columns) // 3)
                header_format = workbook.add_format({
                    'border': 1,
                    'font_size': font_size,
                    'text_wrap': True,
                    'align': 'center',
                    'valign': 'vcenter'
                })
                cell_format = workbook.add_format({
                    'border': 1,
                    'font_size': font_size,
                    'text_wrap': True,
                    'valign': 'vcenter'
                })
                for col_idx, col_name in enumerate(selected_columns):
                    max_len = max(filtered_data[col_name].astype(str).map(len).max(), len(col_name))
                    col_width = min(max_len + 2, 30)
                    worksheet.set_column(col_idx, col_idx, col_width)
                for row in range(len(filtered_data) + 1):
                    for col in range(len(selected_columns)):
                        value = selected_columns[col] if row == 0 else filtered_data.iloc[row - 1][selected_columns[col]]
                        fmt = header_format if row == 0 else cell_format
                        worksheet.write(row, col, value, fmt)
            os.startfile(output_path)
        except Exception as e:
            QMessageBox.critical(self, "Excelプレビューエラー", f"Excelプレビューに失敗しました:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelPrinter()
    window.show()
    sys.exit(app.exec_())
