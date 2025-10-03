import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore

class AhkLauncher(QtWidgets.QWidget):
    def __init__(self, folder):
        super().__init__()
        self.folder = folder
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AHK Launcher")
        self.setGeometry(200, 200, 400, 300)

        layout = QtWidgets.QVBoxLayout(self)

        # список файлов
        self.listWidget = QtWidgets.QListWidget()
        layout.addWidget(self.listWidget)

        # кнопки
        btnLayout = QtWidgets.QHBoxLayout()
        self.runBtn = QtWidgets.QPushButton("Запустить")
        self.refreshBtn = QtWidgets.QPushButton("Обновить")
        btnLayout.addWidget(self.runBtn)
        btnLayout.addWidget(self.refreshBtn)
        layout.addLayout(btnLayout)

        # загрузка списка
        self.refreshList()

        # события
        self.runBtn.clicked.connect(self.runScript)
        self.refreshBtn.clicked.connect(self.refreshList)

    def refreshList(self):
        """Обновить список скриптов"""
        self.listWidget.clear()
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        for f in os.listdir(self.folder):
            if f.lower().endswith(".ahk"):
                self.listWidget.addItem(f)

    def runScript(self):
        """Запуск выбранного скрипта"""
        item = self.listWidget.currentItem()
        if item:
            filepath = os.path.join(self.folder, item.text())
            try:
                subprocess.Popen([filepath], shell=True)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Ошибка", str(e))
        else:
            QtWidgets.QMessageBox.information(self, "Нет выбора", "Выберите скрипт.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    folder = r"C:\Users\Astolfo\Desktop\СКРИПТЫ АХК"  # 👉 папка с AHK-скриптами (измени под себя)
    win = AhkLauncher(folder)
    win.show()
    sys.exit(app.exec_())
