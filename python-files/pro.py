# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import requests
import subprocess
from PyPDF2 import PdfReader
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve


class AnimatedButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)

    def enterEvent(self, event):
        rect = self.geometry()
        bigger_rect = rect.adjusted(-5, -3, 5, 3)
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(bigger_rect)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        rect = self.geometry()
        smaller_rect = rect.adjusted(5, 3, -5, -3)
        self.anim.stop()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(smaller_rect)
        self.anim.start()
        super().leaveEvent(event)


class Ui_MainWindow(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("MainDialog")
        Dialog.resize(700, 600)
        Dialog.setWindowTitle("Packing List Extractor")
        Dialog.setStyleSheet("background-color: #f0f8ff; font-family: Segoe UI;")

        self.stacked_widget = QtWidgets.QStackedWidget(Dialog)
        self.stacked_widget.setGeometry(QtCore.QRect(0, 0, 700, 600))

        self.setup_home_page()
        self.setup_main_page()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.setCurrentWidget(self.home_page)

        self.pdf_files = []
        self.output_file = "Extracted_Packing_List_Data.xlsx"

    def setup_home_page(self):
        self.home_page = QtWidgets.QWidget()
        home_layout = QtWidgets.QVBoxLayout(self.home_page)
        home_layout.setContentsMargins(40, 20, 40, 20)
        home_layout.setSpacing(20)

        url = "https://www.computerworld.com/wp-content/uploads/2024/03/cw-pdf-to-excel-100928235-orig.jpg?resize=1024%2C682&quality=50&strip=all"
        try:
            image = QtGui.QPixmap()
            image.loadFromData(requests.get(url).content)
        except Exception:
            image = QtGui.QPixmap()

        self.banner_label = QtWidgets.QLabel()
        self.banner_label.setPixmap(image)
        self.banner_label.setScaledContents(True)
        self.banner_label.setFixedHeight(250)
        self.banner_label.setStyleSheet("border-radius: 15px;")
        home_layout.addWidget(self.banner_label)

        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)

        self.label_title = QtWidgets.QLabel("📦 Packing List PDF Extractor")
        self.label_title.setFont(QtGui.QFont("Arial", 22, QtGui.QFont.Bold))
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setStyleSheet("color: #007ACC;")
        container_layout.addWidget(self.label_title)

        self.label_sub = QtWidgets.QLabel("Upload packing list PDFs and extract clean Excel data.")
        self.label_sub.setFont(QtGui.QFont("Arial", 13))
        self.label_sub.setAlignment(QtCore.Qt.AlignCenter)
        self.label_sub.setStyleSheet("color: #444444;")
        container_layout.addWidget(self.label_sub)

        self.btn_enter = AnimatedButton("Start Extracting")
        self.btn_enter.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_enter.setFixedWidth(200)
        self.btn_enter.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border-radius: 12px;
                font-size: 16px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #005F99;
            }
        """)
        self.btn_enter.clicked.connect(lambda: self.switch_page_with_fade(self.main_page))
        container_layout.addWidget(self.btn_enter, alignment=QtCore.Qt.AlignCenter)

        home_layout.addWidget(container)

    def setup_main_page(self):
        self.main_page = QtWidgets.QWidget()
        self.main_page.setStyleSheet("background-color: #f5faff;")

        self.btn_back = AnimatedButton("⬅ Back", self.main_page)
        self.btn_back.setGeometry(590, 560, 90, 30)
        self.btn_back.clicked.connect(lambda: self.switch_page_with_fade(self.home_page))
        self.btn_back.setStyleSheet(self.nav_button_style())

        self.btn_upload = self.create_main_button("📁 Select PDF(s)", 60, 20, self.upload_pdfs)
        self.btn_remove = self.create_main_button(" Remove Selected", 480, 20, self.remove_selected_pdfs)
        self.btn_clear_all = self.create_main_button(" Clear All", 320, 20, self.clear_all_pdfs)

        self.pdf_list = QtWidgets.QListWidget(self.main_page)
        self.pdf_list.setGeometry(60, 70, 580, 180)
        self.pdf_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #d3d3d3;
                padding: 8px;
                font-size: 13px;
            }
        """)

        self.progress_bar = QtWidgets.QProgressBar(self.main_page)
        self.progress_bar.setGeometry(60, 260, 580, 25)
        self.progress_bar.setVisible(False)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)

        self.table = QTableWidget(self.main_page)
        self.table.setGeometry(60, 300, 580, 150)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["File Name", "Packing List", "Issue Date", "PO Number", "Item Qty"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background: white; font-size: 12px;")

        self.btn_start = self.create_main_button("🚀 Start Extraction", 220, 470, self.start_processing)
        self.btn_see_results = self.create_main_button("📊 See Results", 400, 470, self.open_excel_file)
        self.btn_start.setEnabled(False)
        self.btn_see_results.setEnabled(False)

        self.label = QtWidgets.QLabel(self.main_page)
        self.label.setGeometry(60, 510, 580, 30)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 13px; color: #333333;")
        self.label.setText("Please upload PDF files to start.")

    def create_main_button(self, text, x, y, callback):
        btn = AnimatedButton(self.main_page)
        btn.setGeometry(x, y, 160, 40)
        btn.setText(text)
        btn.clicked.connect(callback)
        btn.setStyleSheet(self.button_style())
        return btn

    def button_style(self):
        return """
            QPushButton {
                background-color: #1e90ff;
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #187bcd;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """

    def nav_button_style(self):
        return """
            QPushButton {
                background-color: #007ACC;
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005F99;
            }
        """

    def switch_page_with_fade(self, target_page):
        self.stacked_widget.setCurrentWidget(target_page)

    def upload_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(None, "Select PDF Files", "", "PDF Files (*.pdf)")
        for file in files:
            if file not in self.pdf_files:
                self.pdf_files.append(file)
                item = QListWidgetItem(os.path.basename(file))
                item.setToolTip(file)
                self.pdf_list.addItem(item)
        self.btn_start.setEnabled(bool(self.pdf_files))
        self.label.setText(f"{len(self.pdf_files)} PDF(s) selected.")

    def remove_selected_pdfs(self):
        for item in self.pdf_list.selectedItems():
            file_path = item.toolTip()
            self.pdf_files.remove(file_path)
            self.pdf_list.takeItem(self.pdf_list.row(item))
        self.btn_start.setEnabled(bool(self.pdf_files))
        self.label.setText(f"{len(self.pdf_files)} PDF(s) remaining.")

    def clear_all_pdfs(self):
        self.pdf_files.clear()
        self.pdf_list.clear()
        self.table.setRowCount(0)
        self.btn_start.setEnabled(False)
        self.btn_see_results.setEnabled(False)
        self.label.setText("Please upload PDF files to start.")

    def extract_pdf_data(self, file_path):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"

        lines = text.splitlines()
        packing_list_number = issue_date = po_number = item_qty = None

        for i, line in enumerate(lines):
            if "Packing List Number" in line and i + 1 < len(lines):
                values = lines[i + 1].strip().split()
                if len(values) >= 2:
                    packing_list_number = values[0]
                    issue_date = values[1]
            if "PO Number(s)" in line and i + 1 < len(lines):
                values = lines[i + 1].strip().split()
                if len(values) >= 2:
                    po_number = values[0]
                    item_qty = values[1]

        return {
            "File Name": os.path.basename(file_path),
            "Packing List Number": packing_list_number,
            "Issue Date": issue_date,
            "PO Number": po_number,
            "Item Qty": item_qty
        }

    def start_processing(self):
        if not self.pdf_files:
            return

        self.label.setText("⏳ Processing...")
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.pdf_files))
        self.progress_bar.setVisible(True)
        self.table.setRowCount(0)
        QtWidgets.QApplication.processEvents()

        results = []
        for i, file in enumerate(self.pdf_files):
            try:
                data = self.extract_pdf_data(file)
                results.append(data)
                self.add_to_table(data)
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Failed to process:\n{file}\n\n{str(e)}")
            self.progress_bar.setValue(i + 1)
            QtWidgets.QApplication.processEvents()

        self.progress_bar.setVisible(False)

        if results:
            df = pd.DataFrame(results)
            df.to_excel(self.output_file, index=False)
            self.label.setText("✅ Extraction complete! Click 'See Results'.")
            self.btn_see_results.setEnabled(True)
        else:
            self.label.setText("⚠️ No data extracted.")

    def add_to_table(self, data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, key in enumerate(["File Name", "Packing List Number", "Issue Date", "PO Number", "Item Qty"]):
            item = QTableWidgetItem(data.get(key, ""))
            self.table.setItem(row, col, item)

    def open_excel_file(self):
        if os.path.exists(self.output_file):
            try:
                if sys.platform.startswith('win'):
                    os.startfile(self.output_file)
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', self.output_file])
                else:
                    subprocess.run(['xdg-open', self.output_file])
            except Exception as e:
                QMessageBox.warning(None, "Error", f"Failed to open file:\n{e}")
        else:
            QMessageBox.warning(None, "Not Found", "Excel file not found. Please run extraction first.")


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        Dialog = QtWidgets.QDialog()
        ui = Ui_MainWindow()
        ui.setupUi(Dialog)
        Dialog.show()
        sys.exit(app.exec_())
    except Exception as e:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(str(e))
