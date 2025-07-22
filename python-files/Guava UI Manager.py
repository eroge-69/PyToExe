import sys
from PyQt5 import QtWidgets, QtGui, QtCore

# --- Модели данных ---
class Project:
    def __init__(self, name, category, path, published=False):
        self.name = name
        self.category = category  # 'app', 'game', 'site', 'file'
        self.path = path
        self.published = published

class User:
    def __init__(self, email, is_registered=False, is_subscribed=False, guava_balance=0):
        self.email = email
        self.is_registered = is_registered
        self.is_subscribed = is_subscribed
        self.guava_balance = guava_balance

# --- Основное окно ---
class GuavaUIManager(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guava UI Manager")
        self.setWindowIcon(QtGui.QIcon())
        self.resize(1200, 700)
        self.languages = ['Русский', 'English', 'Deutsch', 'Español', 'Français', '中文', '日本語', '한국어', 'Italiano', 'Português', 'العربية', 'हिन्दी', 'Türkçe', 'Українська', 'Polski', 'Čeština', 'Nederlands', 'עברית', 'فارسی', 'ไทย', 'Tiếng Việt', 'Ελληνικά', 'Magyar', 'Română', 'Svenska', 'Suomi', 'Norsk', 'Dansk', 'Slovenčina', 'Slovenščina', 'Hrvatski', 'Български', 'Српски', 'ქართული', 'Қазақша', 'Oʻzbekcha', 'Azərbaycanca', 'Հայերեն', 'ქართული', 'Latviešu', 'Lietuvių', 'Eesti', 'Bahasa Indonesia', 'Bahasa Melayu', 'Filipino', 'Català', 'Galego', 'Euskara', 'Afrikaans', 'Shqip', 'Македонски', 'Монгол', 'ქართული', 'Қазақша', 'Oʻzbekcha', 'Azərbaycanca', 'Հայերեն', 'ქართული', 'Latviešu', 'Lietuvių', 'Eesti', 'Bahasa Indonesia', 'Bahasa Melayu', 'Filipino', 'Català', 'Galego', 'Euskara', 'Afrikaans', 'Shqip', 'Македонски', 'Монгол']
        self.current_language = 'Русский'
        self.themes = {
            "Светлая": "",
            "Тёмная": "QWidget { background-color: #23272e; color: #f8f8f2; } QPushButton { background-color: #44475a; color: #f8f8f2; border-radius: 6px; padding: 6px; } QPushButton:hover { background-color: #6272a4; } QLineEdit, QComboBox { background-color: #282a36; color: #f8f8f2; border-radius: 4px; }"
        }
        self.current_theme = "Светлая"
        self.user = None
        self.projects = []
        self.init_ui()

    def init_ui(self):
        # --- Верхняя панель ---
        top_bar = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout()
        top_bar.setLayout(top_layout)

        # Язык
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItems(self.languages)
        self.lang_combo.setCurrentText(self.current_language)
        self.lang_combo.currentTextChanged.connect(self.change_language)
        top_layout.addWidget(QtWidgets.QLabel("Язык:"))
        top_layout.addWidget(self.lang_combo)

        # Тема
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(self.themes.keys())
        self.theme_combo.setCurrentText(self.current_theme)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        top_layout.addWidget(QtWidgets.QLabel("Тема:"))
        top_layout.addWidget(self.theme_combo)

        # Баланс
        self.balance_label = QtWidgets.QLabel("Баланс: 0 гуав")
        top_layout.addWidget(self.balance_label)

        # Вход/регистрация
        self.login_btn = QtWidgets.QPushButton("Войти / Зарегистрироваться")
        self.login_btn.clicked.connect(self.show_login_dialog)
        top_layout.addWidget(self.login_btn)

        # Подписка
        self.subs_btn = QtWidgets.QPushButton("Оформить подписку")
        self.subs_btn.clicked.connect(self.subscribe)
        top_layout.addWidget(self.subs_btn)
        
        # Кнопка активации
        self.activate_btn = QtWidgets.QPushButton("Активация")
        self.activate_btn.clicked.connect(self.activate_subscription)
        top_layout.addWidget(self.activate_btn)

        # --- Основная область ---
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Левая колонка: Продолжить редактирование
        self.left_col = QtWidgets.QGroupBox("Продолжить редактирование")
        self.left_layout = QtWidgets.QVBoxLayout()
        self.left_col.setLayout(self.left_layout)
        self.project_lists = {}
        for cat, name in [('app', 'Приложения'), ('game', 'Игры'), ('site', 'Сайты'), ('file', 'Файлы')]:
            group = QtWidgets.QGroupBox(name)
            vbox = QtWidgets.QVBoxLayout()
            listw = QtWidgets.QListWidget()
            listw.itemDoubleClicked.connect(self.open_project)
            vbox.addWidget(listw)
            group.setLayout(vbox)
            self.left_layout.addWidget(group)
            self.project_lists[cat] = listw

        # Правая колонка: Создать
        self.right_col = QtWidgets.QGroupBox("Создать")
        self.right_layout = QtWidgets.QVBoxLayout()
        self.right_col.setLayout(self.right_layout)
        self.create_btns = {}
        for cat, name in [('app', 'Приложение'), ('game', 'Игру'), ('site', 'Сайт'), ('file', 'Файл')]:
            btn = QtWidgets.QPushButton(f"Создать {name}")
            btn.clicked.connect(lambda _, c=cat: self.create_project(c))
            self.right_layout.addWidget(btn)
            self.create_btns[cat] = btn

        # Кнопка загрузки расширений
        self.ext_btn = QtWidgets.QPushButton("Загрузить расширение")
        self.ext_btn.clicked.connect(self.load_extension)
        self.right_layout.addWidget(self.ext_btn)

        # Кнопка публикации и скачивания
        self.publish_btn = QtWidgets.QPushButton("Опубликовать проект")
        self.publish_btn.clicked.connect(self.publish_project)
        self.right_layout.addWidget(self.publish_btn)
        self.download_btn = QtWidgets.QPushButton("Скачать проект")
        self.download_btn.clicked.connect(self.download_project)
        self.right_layout.addWidget(self.download_btn)

        # Перевод гуавов
        self.transfer_btn = QtWidgets.QPushButton("Перевести гуавы")
        self.transfer_btn.clicked.connect(self.transfer_guava)
        self.right_layout.addWidget(self.transfer_btn)

        # --- Сборка интерфейса ---
        main_layout.addWidget(self.left_col, 2)
        main_layout.addWidget(self.right_col, 1)

        # --- Центральный виджет ---
        central = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(top_bar)
        vbox.addWidget(main_widget)
        central.setLayout(vbox)
        self.setCentralWidget(central)

        self.update_ui()

    def update_ui(self):
        # Обновить баланс
        if self.user:
            self.balance_label.setText(f"Баланс: {self.user.guava_balance} гуав")
            if self.user.is_subscribed:
                self.subs_btn.setText("Подписка активна")
                self.subs_btn.setEnabled(False)
            else:
                self.subs_btn.setText("Оформить подписку")
                self.subs_btn.setEnabled(True)
            self.login_btn.setText(f"Аккаунт: {self.user.email}")
        else:
            self.balance_label.setText("Баланс: 0 гуав")
            self.subs_btn.setText("Оформить подписку")
            self.subs_btn.setEnabled(False)
            self.login_btn.setText("Войти / Зарегистрироваться")

        # Обновить списки проектов
        for cat in self.project_lists:
            self.project_lists[cat].clear()
        for p in self.projects:
            item = QtWidgets.QListWidgetItem(p.name + (" [Опубликовано]" if p.published else ""))
            item.setData(QtCore.Qt.UserRole, p)
            self.project_lists[p.category].addItem(item)

    def change_language(self, lang):
        self.current_language = lang
        # Здесь должна быть логика смены языка интерфейса (i18n)
        QtWidgets.QMessageBox.information(self, "Язык", f"Язык интерфейса изменён на: {lang}")

    def change_theme(self, theme):
        self.current_theme = theme
        self.setStyleSheet(self.themes[theme])

    def show_login_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Вход / Регистрация")
        layout = QtWidgets.QFormLayout(dialog)
        email_edit = QtWidgets.QLineEdit()
        layout.addRow("Email:", email_edit)
        pass_edit = QtWidgets.QLineEdit()
        pass_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addRow("Пароль:", pass_edit)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(btns)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            email = email_edit.text().strip()
            if not email:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите email")
                return
            # Проверка на popik.gon@gmail.com
            is_sub = email == "popik.gon@gmail.com"
            self.user = User(email, is_registered=True, is_subscribed=is_sub, guava_balance=10000 if is_sub else 0)
            self.update_ui()
            QtWidgets.QMessageBox.information(self, "Успех", "Вход выполнен!")

    def subscribe(self):
        if not self.user:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сначала войдите в аккаунт")
            return
        if self.user.is_subscribed:
            QtWidgets.QMessageBox.information(self, "Подписка", "У вас уже есть подписка!")
            return
        if self.user.guava_balance < 600:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Недостаточно гуав для подписки (600 гуав)")
            return
        self.user.guava_balance -= 600
        self.user.is_subscribed = True
        # Перевод гуавов на аккаунт popik.gon@gmail.com
        # (В реальном приложении - транзакция)
        QtWidgets.QMessageBox.information(self, "Подписка", "Подписка Ai Guava активирована!")
        self.update_ui()

    def create_project(self, category):
        if category == 'game':
            self.open_game_creator()
        elif category == 'app':
            self.open_app_creator()
        elif category == 'site':
            self.open_site_creator()
        elif category == 'file':
            self.open_file_creator()

    def open_project(self, item):
        project = item.data(QtCore.Qt.UserRole)
        if project.category == 'game':
            self.open_game_creator(project)
        elif project.category == 'app':
            self.open_app_creator(project)
        elif project.category == 'site':
            self.open_site_creator(project)
        elif project.category == 'file':
            self.open_file_creator(project)

    def open_game_creator(self, project=None):
        # Платформа, похожая на Cocos Creator, с поддержкой смены языка интерфейса
        QtWidgets.QMessageBox.information(self, "Game Creator", "Открывается редактор игр (аналог Cocos Creator) с поддержкой смены языка интерфейса.")
        if not project:
            name, ok = QtWidgets.QInputDialog.getText(self, "Создать игру", "Название игры:")
            if ok and name:
                p = Project(name, 'game', f"/games/{name}")
                self.projects.append(p)
                self.update_ui()
        # Здесь должен быть полноценный редактор

    def open_app_creator(self, project=None):
        # Интерфейс как Appsfera, с поддержкой смены языка интерфейса
        QtWidgets.QMessageBox.information(self, "App Creator", "Открывается редактор приложений (аналог Appsfera) с поддержкой смены языка интерфейса.")
        if not project:
            name, ok = QtWidgets.QInputDialog.getText(self, "Создать приложение", "Название приложения:")
            if ok and name:
                p = Project(name, 'app', f"/apps/{name}")
                self.projects.append(p)
                self.update_ui()
        # Здесь должен быть полноценный редактор

    def open_site_creator(self, project=None):
        # Суперпрофессиональный интерфейс для сайтов (AI-генерация)
        QtWidgets.QMessageBox.information(self, "Site Creator", "Открывается профессиональный редактор сайтов с поддержкой смены языка интерфейса и AI-инструментами.")
        if not project:
            name, ok = QtWidgets.QInputDialog.getText(self, "Создать сайт", "Название сайта:")
            if ok and name:
                p = Project(name, 'site', f"/sites/{name}")
                self.projects.append(p)
                self.update_ui()
        # Здесь должен быть полноценный редактор

    def open_file_creator(self, project=None):
        # Интерфейс для работы с файлами (AI-генерация)
        QtWidgets.QMessageBox.information(self, "File Creator", "Открывается редактор файлов с поддержкой смены языка интерфейса и AI-инструментами.")
        if not project:
            name, ok = QtWidgets.QInputDialog.getText(self, "Создать файл", "Название файла:")
            if ok and name:
                p = Project(name, 'file', f"/files/{name}")
                self.projects.append(p)
                self.update_ui()
        # Здесь должен быть полноценный редактор

    def publish_project(self):
        if not self.user or not self.user.is_registered:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Для публикации необходимо зарегистрироваться.")
            return
        # Выбор проекта
        all_projects = [p for p in self.projects if not p.published]
        if not all_projects:
            QtWidgets.QMessageBox.information(self, "Публикация", "Нет проектов для публикации.")
            return
        items = [p.name for p in all_projects]
        idx, ok = QtWidgets.QInputDialog.getItem(self, "Публикация", "Выберите проект:", items, 0, False)
        if ok:
            for p in all_projects:
                if p.name == idx:
                    p.published = True
                    QtWidgets.QMessageBox.information(self, "Публикация", f"Проект '{p.name}' опубликован!")
                    self.update_ui()
                    break

    def download_project(self):
        # Выбор проекта
        if not self.projects:
            QtWidgets.QMessageBox.information(self, "Скачивание", "Нет проектов для скачивания.")
            return
        items = [p.name for p in self.projects]
        idx, ok = QtWidgets.QInputDialog.getItem(self, "Скачивание", "Выберите проект:", items, 0, False)
        if ok:
            QtWidgets.QMessageBox.information(self, "Скачивание", f"Проект '{idx}' скачан (заглушка).")

    def load_extension(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Загрузить расширение", "", "Файлы расширений (*.guavaext)")
        if fname:
            QtWidgets.QMessageBox.information(self, "Расширение", f"Расширение '{fname}' успешно загружено (заглушка).")

    def transfer_guava(self):
        if not self.user:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сначала войдите в аккаунт")
            return
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Перевести гуавы")
        layout = QtWidgets.QFormLayout(dialog)
        to_edit = QtWidgets.QLineEdit()
        layout.addRow("Кому (email):", to_edit)
        amount_edit = QtWidgets.QSpinBox()
        amount_edit.setRange(1, self.user.guava_balance)
        layout.addRow("Сумма:", amount_edit)
        comment_edit = QtWidgets.QLineEdit()
        layout.addRow("Комментарий:", comment_edit)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(btns)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            to_email = to_edit.text().strip()
            amount = amount_edit.value()
            comment = comment_edit.text()
            if not to_email or amount <= 0:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Заполните все поля корректно.")
                return
            if self.user.guava_balance < amount:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Недостаточно гуав.")
                return
            self.user.guava_balance -= amount
            # В реальном приложении: перевод гуавов на другой аккаунт
            QtWidgets.QMessageBox.information(self, "Перевод", f"Переведено {amount} гуав на {to_email}.\nКомментарий: {comment}")
            self.update_ui()

# --- Запуск приложения ---
def main():
    app = QtWidgets.QApplication(sys.argv)
    win = GuavaUIManager()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
