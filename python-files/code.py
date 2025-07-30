import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QProgressBar,
    QFrame
)
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QCursor


class LanguageSelection(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Установка Windows")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #1a005e;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Windows 12")
        title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        combo_layout = QVBoxLayout()
        self.lang_combo = self.addDropdown(combo_layout, "Устанавливаемый язык:", ["Русский (Россия)", "English (United States)"])
        self.time_combo = self.addDropdown(combo_layout, "Формат времени и денежных единиц:", ["Русский (Россия)", "English (US)"])
        self.keyboard_combo = self.addDropdown(combo_layout, "Метод ввода (раскладка клавиатуры):", ["Русская", "US Keyboard"])
        layout.addLayout(combo_layout)

        hint = QLabel("Выберите нужный язык и другие параметры, а затем нажмите кнопку \"Далее\".")
        hint.setFont(QFont("Segoe UI", 12))
        hint.setStyleSheet("color: white;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        button = QPushButton("Далее")
        button.setFixedWidth(140)
        button.setFont(QFont("Segoe UI", 12))
        button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #aaa;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c8c8c8;
            }
        """)
        button.clicked.connect(self.startInstallation)
        layout.addWidget(button, alignment=Qt.AlignCenter)

        copyright = QLabel("© Корпорация Майкрософт (Microsoft Corporation). Все права защищены.")
        copyright.setFont(QFont("Segoe UI", 9))
        copyright.setStyleSheet("color: white;")
        copyright.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright)

        self.setLayout(layout)

    def addDropdown(self, parent_layout, label_text, options):
        hbox = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 14))
        label.setStyleSheet("color: white;")
        combo = QComboBox()
        combo.addItems(options)
        combo.setStyleSheet("padding: 6px; font-size: 14px;")
        hbox.addWidget(label)
        hbox.addWidget(combo)
        parent_layout.addLayout(hbox)
        return combo

    def startInstallation(self):
        self.hide()
        self.installer = InstallationProgress()
        self.installer.showFullScreen()


class InstallationProgress(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Установка Windows")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #1a005e;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Установка Windows 12")
        title.setFont(QFont("Segoe UI", 30, QFont.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.progress = QProgressBar()
        self.progress.setFixedWidth(650)
        self.progress.setValue(0)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 3px solid grey;
                border-radius: 8px;
                text-align: center;
                background-color: white;
                font-size: 18px;
            }
            QProgressBar::chunk {
                background-color: #00aaff;
                width: 20px;
            }
        """)
        layout.addWidget(self.progress)

        self.status_label = QLabel("Копирование файлов Windows...")
        self.status_label.setFont(QFont("Segoe UI", 16))
        self.status_label.setStyleSheet("color: white;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(90)
        self.progress_value = 0

    def updateProgress(self):
        if self.progress_value < 100:
            self.progress_value += 1
            self.progress.setValue(self.progress_value)

            if self.progress_value == 25:
                self.status_label.setText("Установка компонентов...")
            elif self.progress_value == 50:
                self.status_label.setText("Установка обновлений...")
            elif self.progress_value == 75:
                self.status_label.setText("Завершение установки...")
        else:
            self.timer.stop()
            self.status_label.setText("Перезагрузка системы...")
            QTimer.singleShot(1800, self.rebootScreen)

    def rebootScreen(self):
        self.hide()
        self.reboot = RebootScreen()
        self.reboot.showFullScreen()


class RebootScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Перезагрузка...")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Перезагрузка...")
        label.setFont(QFont("Segoe UI", 20))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

        QTimer.singleShot(3500, self.showPreparing)


    def showPreparing(self):
        self.hide()
        self.preparing = PreparingScreen()
        self.preparing.showFullScreen()


class PreparingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Подготовка")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #0078d7;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Подождите, идет подготовка устройств...")
        label.setFont(QFont("Segoe UI", 24))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

        QTimer.singleShot(4500, self.showWelcome)


    def showWelcome(self):
        self.hide()
        self.welcome = WelcomeScreen()
        self.welcome.showFullScreen()


class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добро пожаловать")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #0078d7;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Добро пожаловать в Windows 12")
        label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

        QTimer.singleShot(4000, self.launchDesktop)

    def launchDesktop(self):
        self.hide()
        self.desktop = FakeDesktop()
        self.desktop.showFullScreen()


class FakeDesktop(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 12")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #0047ab;")
        self.initUI()

    def initUI(self):
        self.resize(1280, 720)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        # Фон — заливка цветом (можно заменить на изображение)
        self.background = QLabel()
        self.background.setStyleSheet("background-color: #0047ab;")
        self.background.setAlignment(Qt.AlignCenter)

        # Панель задач (низу)
        self.taskbar = QFrame()
        self.taskbar.setFixedHeight(40)
        self.taskbar.setStyleSheet("background-color: #1f1f1f;")

        taskbar_layout = QHBoxLayout()
        taskbar_layout.setContentsMargins(10, 0, 10, 0)
        taskbar_layout.setSpacing(15)

        # Кнопка "Пуск"
        self.start_button = QPushButton("⊞ Пуск")
        self.start_button.setFont(QFont("Segoe UI", 12))
        self.start_button.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #0078d7;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        self.start_button.clicked.connect(self.toggleStartMenu)
        taskbar_layout.addWidget(self.start_button, alignment=Qt.AlignLeft)

        # Спейсер
        taskbar_layout.addStretch()

        # Часы — обновляемое время
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Segoe UI", 12))
        self.clock_label.setStyleSheet("color: white;")
        self.clock_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        taskbar_layout.addWidget(self.clock_label, alignment=Qt.AlignRight)

        self.taskbar.setLayout(taskbar_layout)

        # Иконка "Корзина" на рабочем столе
        self.recycle_bin = QPushButton("🗑️ Корзина")
        self.recycle_bin.setFont(QFont("Segoe UI", 14))
        self.recycle_bin.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: transparent;
                border: none;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.15);
            }
        """)
        self.recycle_bin.setFixedSize(120, 40)
        self.recycle_bin.clicked.connect(self.recycleBinClicked)

        # Главный слой
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 0)
        main_layout.addWidget(self.recycle_bin, alignment=Qt.AlignTop | Qt.AlignLeft)
        main_layout.addStretch()
        main_layout.addWidget(self.taskbar)

        self.setLayout(main_layout)

        # Обновление времени каждую секунду
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateClock)
        self.timer.start(1000)
        self.updateClock()

        # Меню Пуск (скрыто изначально)
        self.start_menu = StartMenuPopup(self)
        self.start_menu.hide()

    def updateClock(self):
        current_time = QTime.currentTime().toString('HH:mm')
        self.clock_label.setText(current_time)

    def toggleStartMenu(self):
        if self.start_menu.isVisible():
            self.start_menu.hide()
        else:
            self.start_menu.showAt(self.start_button.mapToGlobal(QPoint(0, -self.start_menu.height())))

    def recycleBinClicked(self):
        # Просто показать окно с сообщением
        self.bin_window = RecycleBinWindow()
        self.bin_window.show()

    def mousePressEvent(self, event):
        # Закрывать меню Пуск при клике вне его
        if self.start_menu.isVisible() and not self.start_menu.geometry().contains(event.globalPos()) and not self.start_button.geometry().contains(self.mapFromGlobal(event.globalPos())):
            self.start_menu.hide()


class StartMenuPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFixedSize(280, 360)
        self.setStyleSheet("""
            background-color: #1f1f1f;
            border: 2px solid #0078d7;
            border-radius: 6px;
        """)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        title = QLabel("Меню Пуск")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        # Список пунктов меню (просто фейки)
        buttons = [
            ("Параметры", self.showSettings),
            ("Документы", self.showDocs),
            ("Завершить работу", self.shutdownClicked),
            ("Перезагрузить", self.restartClicked),
            ("Выход", self.exitClicked)
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setFont(QFont("Segoe UI", 14))
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #0078d7;
                    border: none;
                    padding: 10px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #005a9e;
                }
            """)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        self.setLayout(layout)

    def showAt(self, pos):
        self.move(pos)
        self.show()

    def showSettings(self):
        self.hide()
        self.settings_window = MessageWindow("Параметры", "Это фейковое окно параметров.")
        self.settings_window.show()

    def showDocs(self):
        self.hide()
        self.docs_window = MessageWindow("Документы", "Ваши документы пусты.")
        self.docs_window.show()

    def shutdownClicked(self):
        self.hide()
        self.parent().hide()
        self.bsod = BSODScreen()
        self.bsod.showFullScreen()

    def restartClicked(self):
        self.hide()
        self.parent().hide()
        self.reboot = RebootScreen()
        self.reboot.showFullScreen()

    def exitClicked(self):
        QApplication.quit()


class RecycleBinWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Корзина")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #0078d7;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("Корзина пуста")
        label.setFont(QFont("Segoe UI", 18))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)


class MessageWindow(QWidget):
    def __init__(self, title, message):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #0078d7;")
        self.initUI(message)

    def initUI(self, message):
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setFont(QFont("Segoe UI", 16))
        label.setStyleSheet("color: white;")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn = QPushButton("Закрыть")
        btn.setFont(QFont("Segoe UI", 12))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #aaa;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c8c8c8;
            }
        """)
        btn.clicked.connect(self.close)
        layout.addWidget(btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)


class BSODScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Синий экран смерти")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()
        self.setStyleSheet("background-color: #010080;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        sad_face = QLabel(":(")
        sad_face.setFont(QFont("Segoe UI", 120, QFont.Bold))
        sad_face.setStyleSheet("color: white;")
        sad_face.setAlignment(Qt.AlignCenter)
        layout.addWidget(sad_face)

        error_msg = QLabel(
            "Ваш компьютер столкнулся с проблемой и нуждается в перезагрузке.\n"
            "Мы собираем некоторые данные об ошибке, после чего будет выполнена автоматическая перезагрузка.\n\n"
            "Если вы хотите узнать больше, вы можете позже поискать эту ошибку в интернете: FAKE_ERROR_0x12345678"
        )
        error_msg.setFont(QFont("Segoe UI", 18))
        error_msg.setStyleSheet("color: white;")
        error_msg.setAlignment(Qt.AlignCenter)
        error_msg.setWordWrap(True)
        layout.addWidget(error_msg)

        self.setLayout(layout)

        QTimer.singleShot(10000, self.fakeReboot)

    def fakeReboot(self):
        self.close()
        app.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lang_select = LanguageSelection()
    lang_select.show()
    sys.exit(app.exec_())