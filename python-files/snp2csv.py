# -*- coding: utf-8 -*-


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QApplication, QLabel, QLineEdit,
                            QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout)
from ctypes import windll
from sys import argv, exit
from os import path, walk


################################################################################
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.path    = path.dirname(path.abspath(__file__))
        self.nfls    = 5
        self.ncols   = 5
        self.csvlist = []
        self.setStyleSheet("background-color: #3f3f3f; color: white")
        self.setWindowTitle('snp2csv converter')
        self.main_app()
        self.show()

    def main_app(self):
        self.app_widgets()
        self.app_layout()

    def app_widgets(self):
        self.label_path  = QLabel("directory with snp-files: ")
        self.in_path = QLineEdit()
        self.in_path.setText(self.path+'\\')
        self.in_path.setAlignment(Qt.AlignLeft)
        self.in_path.setStyleSheet("background-color: #4f4f4f")
        self.in_path.returnPressed.connect(self.conv)
        
        self.btn_conv = QPushButton("Convert Files")
        self.btn_conv.clicked.connect(self.conv)


    def app_layout(self):
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)
        self.glayout = QGridLayout()
        self.glayout.setContentsMargins(40, 30, 40, 30)
        self.bottomlayout = QHBoxLayout()
        self.bottomlayout.setContentsMargins(40, 30, 40, 30)
        
        self.glayout.addWidget(self.label_path,1,1,2,1)
        self.glayout.addWidget(self.in_path,1,3,2,50)

        self.bottomlayout.addWidget(self.btn_conv)

        self.mainlayout.addLayout(self.glayout)
        self.mainlayout.addLayout(self.bottomlayout)

        self.in_path.setFocus()
        
        
    def conv(self):
        self.path = self.in_path.text()
        snplist   = []

        for root,dirs,files in walk(self.path+'/'):
            for file in files:
                if file.find('.s2p') > 0:
                    snplist.append(root+'/'+file)


        for file in snplist:
            with open(file,'rb') as fin:
                data = fin.readlines()
            
            for i in range(5):
                del(data[0])
            data[0] = data[0].replace(b'!',b' ')
            
            
            lines = len(data)
            chars = len(data[0])
            flag  = False
            
            
            for line in range(lines):
                data[line] = bytearray(data[line])
                char       = 0
                col        = 0
                while char < chars and col <= self.ncols:
                    if data[line][char] == 10:              # find '\n'
                        break
                    if flag:
                        if data[line][char] == 32:          # find ' '
                            del(data[line][char])           # rem  ' '
                            char -= 1
                            flag = True
                        else:
                            flag = False
                    else:
                        if data[line][char] == 32:          # repl ' '
                            data[line][char] = 59           # by   ';'
                            flag = True
                            col += 1
                    char += 1
                del(data[line][0])
                del(data[line][data[line].rfind(59):])      # rem  ';'[...]
                data[line].append(13)                       # add  '\r'
                data[line].append(10)                       # add  '\n'
                flag = False
            
            
            with open (file[:-4]+'.csv','wb') as fout:
                fout.writelines(data)

        exit()


def main():
    app = QApplication(argv)
    app.setStyle('Fusion')
    win = MainWindow()
    w_gui        = win.width()
    h_gui        = win.height()
    w_screen     = windll.user32.GetSystemMetrics(0)
    h_screen     = windll.user32.GetSystemMetrics(1)
    x            = int((w_screen-w_gui)/2)
    y            = int((h_screen-h_gui)/2)
    win.setGeometry(x, y, w_gui, h_gui)
    exit(app.exec_())

if __name__ == "__main__":
    main()