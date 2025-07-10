from PyQt5.QtWidgets import QApplication
import sys
from menu import MenuWindow
import os

# Запускаем проверку
print("start")
list_resources_files()
print("end")

def main():
    app = QApplication(sys.argv)
    menu = MenuWindow()
    menu.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
