import sys
from cProfile import label
from fileinput import close

from PyQt5.QtSensors import QAltimeter
#import check_list

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,QHBoxLayout,
                             QMainWindow, QSizePolicy, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFrame,  QTableWidgetItem)
from PyQt5.QtGui import QFont, QIcon, QPixmap,QIntValidator, QColor  # Импортируем QIcon
from PyQt5.QtCore import Qt, QSize
import pnl
from PyQt5 import QtWidgets
from pnl import entry
from pygments.styles.dracula import background

marks = []
marks_func = []
def entry_res(mark):
    try:
        if mark == 1:
            marks.append('1')
            marks_func.append(1)
        elif mark == 2:
            marks.append('2')
            marks_func.append(2)
        elif mark == 3:
            marks.append('3')
            marks_func.append(3)
        elif mark == 4:
            marks.append('4')
            marks_func.append(4)
        elif mark == 5:
            marks.append('5')
            marks_func.append(5)
        elif mark == "<":
            marks.pop()
            marks_func.pop()
        elif mark == "C":
            marks.clear()
            marks_func.clear()
    except:
        pass
    try:
        result = ''.join(marks)
        entry1.setText(result)

        x = len(marks_func)
        y = sum(marks_func)
        result1 = y/x
        result1 = round(result1, 2)

        if result1 >= 1.5 and result1 < 2.5:
            label_res.setStyleSheet("color: rgb(194, 8, 8)")
        elif result1 >= 2.5 and result1 < 3.5:
            label_res.setStyleSheet("color: rgb(171, 135, 7)")
        elif result1 >= 3.5 and result1 < 4.5:
            label_res.setStyleSheet("color: rgb(145, 179, 9)")
        elif result1 >= 4.5:
            label_res.setStyleSheet("color: rgb(43, 181, 9)")
        elif result1 < 1.5:
            label_res.setStyleSheet("color: rgb(130, 4, 4)")

#
        label_res.setText(str(result1))
    except:
        entry1.setText('')
        label_res.setText('--')
        label_res.setStyleSheet("color: white")





def win():
    global window
    window = QMainWindow()
    window.setWindowTitle('Средняя оценка')
    window.setFixedSize(QSize(400, 250))
    window.setStyleSheet("background-color: rgb(31, 27, 27);")

    central_widget = QWidget(window)
    window.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget) # Основной Layout для всего окна

    label = QtWidgets.QLabel(window)
    label.setText('Средняя оценка:')
    label.setStyleSheet("color: white")
    label.setFont(QFont("Arial", 18, QFont.Bold))
    label.adjustSize()
    label.move(10, 10)

    global entry1
    entry1 = QtWidgets.QLineEdit(window)
    entry1.setFont(QFont("Arial", 18, QFont.Bold))
    int_validator = QIntValidator()
    int_validator.setRange(-9999, 9999)  # Пример: от -10000 до 10000
    entry1.setValidator(int_validator)
    entry1.setFixedWidth(250)
    entry1.setReadOnly(True)
    entry1.setStyleSheet("""
             QLineEdit:read-only { 
                background-color: rgb(36, 34, 34); 
                color: white;             
                border-style: dashed;
                border-radius: 5px;
                padding: 5px 10px;                
            }"""
                         )
    entry1.move(10, 40)



    global label_res
    label_res = QtWidgets.QLabel(window)
    label_res.setText('--')
    label_res.setStyleSheet("color: white")
    label_res.setFont(QFont("Arial", 18, QFont.Bold))
    label_res.move(220, 10)

    global btn1
    btn1 = QtWidgets.QPushButton(window)
    btn1.setText('1')
    btn1.setFont(QFont("Arial", 16, QFont.Bold))
    btn1.setStyleSheet('''
        QPushButton {
            background-color: rgb(130, 4, 4);
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
        }
    ''')
    btn1.setFixedSize(QSize(50, 50))
    btn1.clicked.connect(lambda: entry_res(1))
    btn1.move(20, 100)

    btn2 = QtWidgets.QPushButton(window)
    btn2.setText('2')
    btn2.setFont(QFont("Arial", 16, QFont.Bold))
    btn2.setStyleSheet('''
            QPushButton {
                background-color: rgb(194, 8, 8);
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        ''')
    btn2.setFixedSize(QSize(50, 50))
    btn2.clicked.connect(lambda: entry_res(2))
    btn2.move(80, 100)

    btn3 = QtWidgets.QPushButton(window)
    btn3.setText('3')
    btn3.setFont(QFont("Arial", 16, QFont.Bold))
    btn3.setStyleSheet('''
            QPushButton {
                background-color: rgb(171, 135, 7);
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        ''')
    btn3.setFixedSize(QSize(50, 50))
    btn3.clicked.connect(lambda: entry_res(3))
    btn3.move(140, 100)

    btn4 = QtWidgets.QPushButton(window)
    btn4.setText('4')
    btn4.setFont(QFont("Arial", 16, QFont.Bold))
    btn4.setStyleSheet('''
            QPushButton {
                background-color: rgb(145, 179, 9);
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        ''')
    btn4.setFixedSize(QSize(50, 50))
    btn4.clicked.connect(lambda: entry_res(4))
    btn4.move(200, 100)

    btn5 = QtWidgets.QPushButton(window)
    btn5.setText('5')
    btn5.setFont(QFont("Arial", 16, QFont.Bold))
    btn5.setFixedSize(QSize(50, 50))
    btn5.setStyleSheet('''
            QPushButton {
                background-color: rgb(43, 181, 9);
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        ''')
    btn5.clicked.connect(lambda: entry_res(5))
    btn5.move(260, 100)


    btn_remove = QtWidgets.QPushButton(window)
    btn_remove.setText('<')
    btn_remove.setFont(QFont("Arial", 16, QFont.Bold))
    btn_remove.setFixedSize(QSize(50, 50))
    btn_remove.setStyleSheet('''
            QPushButton {
                background-color: rgb(36, 34, 34);
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        ''')
    btn_remove.clicked.connect(lambda: entry_res('<'))
    btn_remove.move(20, 160)

    f_btn_remove = QtWidgets.QPushButton(window)
    f_btn_remove.setText('C')
    f_btn_remove.setFont(QFont("Arial", 16, QFont.Bold))
    f_btn_remove.setStyleSheet('''
            QPushButton {
                background-color: rgb(36, 34, 34);
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
        ''')
    f_btn_remove.setFixedSize(QSize(50, 50))
    f_btn_remove.clicked.connect(lambda: entry_res('C'))
    f_btn_remove.move(80, 160)





    window.show()

app = QApplication(sys.argv)
win()
sys.exit(app.exec_())