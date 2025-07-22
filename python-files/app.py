import glob
import os
import re
import socket
import sys
from os.path import isfile
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QComboBox, QPushButton, QLineEdit, QSpinBox, \
    QTableWidget, QTableWidgetItem, QStatusBar


class UI(QMainWindow):

    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi('gui.ui', self)
        self.print_template_btn = self.findChild(QPushButton, 'print_template_btn')
        self.status_label = self.findChild(QLabel, 'status_label')
        self.templates_combo = self.findChild(QComboBox, 'template_select')
        self.templates_combo.currentIndexChanged.connect(lambda: self.read_template(self.templates_combo.currentData()))
        self.ean_input = self.findChild(QLineEdit, 'ean_input')
        self.qty_input = self.findChild(QSpinBox, 'qty_input')
        self.printer_select = self.findChild(QComboBox, 'printer_select')
        self.tableWidget = self.findChild(QTableWidget, 'tableWidget')
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 150)
        self.printer_select.addItem('DEV', '127.0.0.1')
        self.print_template_btn.clicked.connect(lambda: self.get_all_values())
        self.statusBar = self.findChild(QStatusBar, 'statusbar')
        self.statusBar.showMessage('Ready')

        for file in glob.glob('templates/*.txt'):
            if isfile(file):
                filename = os.path.basename(file)
                full_path = file
                self.templates_combo.addItem(filename, full_path)

        self.show()

    def read_template(self, path):
        with open(path, 'r') as f:
            data = f.read()
            pattern = r'{[A-z]*[0-9]*}'
            found = re.findall(pattern, data)
            row = {}
            list_of_rows = []
            for i in found:
                item = {'col_1': i, 'col_2': ''}
                item_copy = item.copy()
                list_of_rows.append(item_copy)

        self.load_data_from_file(list_of_rows)

    def load_data_from_file(self, list_of_rows):
        row = 0
        self.tableWidget.setRowCount(len(list_of_rows))

        for slot in list_of_rows:
            self.tableWidget.setItem(row, 0, QTableWidgetItem(slot['col_1'], ))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(slot['col_2'], ))
            row = row+1

    # Get all values from template and load them to tableWidget
    def get_all_values(self):
        template_name = self.templates_combo.currentData()
        with open(template_name, 'r') as f:
            data = f.read()
            for row in range(self.tableWidget.rowCount()):
                col_name = self.tableWidget.item(row, 0).text()
                col_value = self.tableWidget.item(row, 1).text()
                data = data.replace(col_name, col_value)

            self.print_zpl_label(data)

    # Send data as bytes to printer
    def print_zpl_label(self, label):
        cur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create a socket object
        host = self.printer_select.currentData()
        port = 9100
        self.statusBar.showMessage('Connecting to ' + host)
        try:
            cur_socket.connect((host, port))  # connecting to host
            cur_socket.send(bytes(label, encoding='utf-8'))  # using bytes
            cur_socket.close()  # closing connection
            self.statusBar.showMessage('Printing label')
        except:
            self.statusBar.showMessage('Error connecting to ' + host)

            # print(host)
            print("Error with the connection")


app = QApplication(sys.argv)
UIWindow = UI()
sys.exit(app.exec_())
