import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile
from PyQt5.QtGui import QPalette, QBrush

from ui import LoginWindow, MainWindow
from models import init_db

def main():
    # Инициализация базы данных
    init_db()

    app = QApplication(sys.argv)

    # Применение стилей
    style_file = "resources/styles/style.qss"
    try:
        with open(style_file, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print(f"Файл стилей {style_file} не найден. Используются стандартные стили.")

    login = LoginWindow()
    main_window = MainWindow()

    # Обработка успешного входа
    def show_main(role, group, user_id):
        main_window.set_user_role(role, group, user_id)  # Теперь передаём и группу и ID
        main_window.show()
        login.hide()

    # Обработка выхода из аккаунта
    def handle_logout():
        main_window.hide()
        login.username_input.clear()
        login.password_input.clear()
        login.show()

    login.login_successful.connect(show_main)
    main_window.logout_requested.connect(handle_logout)

    login.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()