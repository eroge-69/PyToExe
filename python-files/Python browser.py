import sys
from urllib.parse import quote
from PyQt5.QtCore import QUrl, QSize, QByteArray, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, 
                            QLineEdit, QVBoxLayout, QWidget, QTabWidget,
                            QPushButton, QStyle, QLabel, QHBoxLayout,
                            QSpacerItem, QSizePolicy, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtSvg import QSvgRenderer


class PythonBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Установка иконки приложения
        self.setWindowIcon(self.create_python_icon())
        
        # Основной виджет и layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Создаем панель инструментов
        self.create_toolbar()
        
        # Главный экран с логотипом и поиском
        self.create_home_screen()
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.hide()  # Сначала показываем главный экран
        self.main_layout.addWidget(self.tabs)
        
        # Настройка стиля
        self.setup_styles()

    def setup_styles(self):
        """Настройка стилей интерфейса"""
        self.setStyleSheet("""
            QToolBar {
                background-color: #f0f0f0;
                border: none;
                padding: 2px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #3873d9;
                border-radius: 5px;
                margin: 0 5px;
                font-size: 14px;
            }
            QTabBar::tab {
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton {
                padding: 5px 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            #searchBox {
                border: 2px solid #3873d9;
                font-size: 16px;
                min-width: 500px;
                padding: 12px;
            }
            #homeScreen {
                background-color: white;
            }
            .search-button {
                background-color: #3873d9;
                color: white;
                border-radius: 5px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 16px;
                min-width: 100px;
            }
            .search-button:hover {
                background-color: #2a5cb0;
            }
            .title-label {
                font-size: 28px;
                font-weight: bold;
                color: #3873d9;
                margin-bottom: 20px;
            }
        """)

    def create_python_icon(self, size=64):
        """Создает иконку Python из SVG данных"""
        python_logo_svg = """
        <svg viewBox="0 0 128 128">
          <path fill="#FFD43B" d="M63.391 1.988c-4.222.02-8.252.379-11.8 1.007-10.45 1.846-12.346 5.71-12.346 12.837v9.411h24.693v3.137H29.977c-7.176 0-13.46 4.313-15.426 12.521-2.268 9.405-2.368 15.275 0 25.096 1.755 7.311 5.947 12.519 13.124 12.519h8.491V67.234c0-8.151 7.051-15.34 15.426-15.34h24.665c6.866 0 12.346-5.654 12.346-12.548V15.833c0-6.703-5.646-11.72-12.346-12.837-4.244-.706-8.645-1.027-12.866-1.008zM50.037 9.557c2.55 0 4.634 2.117 4.634 4.721 0 2.593-2.083 4.69-4.634 4.69-2.56 0-4.633-2.097-4.633-4.69-.001-2.604 2.073-4.721 4.633-4.721z" transform="translate(0 10)"/>
          <path fill="#646464" d="M91.682 28.38v10.966c0 8.149-7.052 15.342-15.426 15.342H51.591c-6.866 0-12.346 5.654-12.346 12.548v23.515c0 6.703 5.647 11.72 12.346 12.837 3.5.577 7.6.936 11.7.926 4.1.01 8.2-.349 11.7-.926 6.7-1.117 12.347-6.134 12.347-12.837V84.675h-24.693v-3.138H94.15c7.176 0 9.852-5.005 12.348-12.519 2.578-7.735 2.467-15.174 0-25.096-1.774-7.145-5.161-12.521-12.348-12.521H91.682zM77.809 87.927c2.56 0 4.634 2.097 4.634 4.692 0 2.602-2.074 4.719-4.634 4.719-2.55 0-4.633-2.117-4.633-4.719 0-2.595 2.083-4.692 4.633-4.692z"/>
        </svg>
        """
        
        try:
            svg_renderer = QSvgRenderer()
            svg_renderer.load(QByteArray(python_logo_svg.encode('utf-8')))
            python_pixmap = QPixmap(size, size)
            python_pixmap.fill(Qt.transparent)
            painter = QPainter(python_pixmap)
            svg_renderer.render(painter)
            painter.end()
            return QIcon(python_pixmap)
        except Exception as e:
            print(f"Ошибка создания иконки: {e}")
            return QIcon()

    def create_home_screen(self):
        """Создает главный экран с логотипом и поиском"""
        self.home_screen = QWidget()
        self.home_screen.setObjectName("homeScreen")
        
        layout = QVBoxLayout(self.home_screen)
        layout.setAlignment(Qt.AlignCenter)
        
        # Вертикальный спейсер сверху
        layout.addItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Логотип Python
        logo_label = QLabel()
        logo_pixmap = self.create_python_icon(150).pixmap(150, 150)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Название браузера
        title_label = QLabel("Python Browser")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("class", "title-label")
        layout.addWidget(title_label)
        
        # Горизонтальный layout для поиска
        search_layout = QHBoxLayout()
        search_layout.setAlignment(Qt.AlignCenter)
        
        # Поле поиска
        self.home_search_box = QLineEdit()
        self.home_search_box.setObjectName("searchBox")
        self.home_search_box.setPlaceholderText("Введите поисковый запрос...")
        self.home_search_box.returnPressed.connect(self.perform_search_from_home)
        search_layout.addWidget(self.home_search_box)
        
        # Кнопка поиска
        search_btn = QPushButton('Поиск')
        search_btn.setObjectName("searchButton")
        search_btn.setProperty("class", "search-button")
        search_btn.clicked.connect(self.perform_search_from_home)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Вертикальный спейсер снизу
        layout.addItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.main_layout.addWidget(self.home_screen)

    def create_toolbar(self):
        """Создает панель инструментов с кнопками и элементами управления"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(20, 20))
        self.main_layout.addWidget(toolbar)
        
        # Кнопки навигации
        back_btn = QPushButton()
        back_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        back_btn.setToolTip('Назад')
        back_btn.clicked.connect(self.navigate_back)
        toolbar.addWidget(back_btn)
        
        forward_btn = QPushButton()
        forward_btn.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        forward_btn.setToolTip('Вперед')
        forward_btn.clicked.connect(self.navigate_forward)
        toolbar.addWidget(forward_btn)
        
        reload_btn = QPushButton()
        reload_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        reload_btn.setToolTip('Обновить')
        reload_btn.clicked.connect(self.navigate_reload)
        toolbar.addWidget(reload_btn)
        
        home_btn = QPushButton()
        home_btn.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        home_btn.setToolTip('Домой')
        home_btn.clicked.connect(self.show_home_screen)
        toolbar.addWidget(home_btn)
        
        # Поле адреса
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL адрес или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Кнопка новой вкладки
        new_tab_btn = QPushButton()
        new_tab_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        new_tab_btn.setToolTip('Новая вкладка')
        new_tab_btn.clicked.connect(lambda: self.add_new_tab(QUrl('about:blank'), 'Новая вкладка'))
        toolbar.addWidget(new_tab_btn)

    def perform_search_from_home(self):
        """Выполняет поиск с главного экрана"""
        try:
            search_text = self.home_search_box.text().strip()
            if not search_text:
                QMessageBox.information(self, "Пустой запрос", "Пожалуйста, введите поисковый запрос")
                return

            encoded_query = quote(search_text)
            search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_"
            
            if self.tabs.count() == 0:
                self.add_new_tab(QUrl(search_url), "Поиск: " + search_text[:15])
            else:
                self.current_browser().setUrl(QUrl(search_url))
            
            self.show_browser_view()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка поиска", 
                               f"Не удалось выполнить поиск:\n{str(e)}")

    def perform_search(self):
        """Выполняет поиск из адресной строки"""
        try:
            search_text = self.url_bar.text().strip()
            if not search_text:
                return

            if not any(search_text.startswith(proto) for proto in ('http://', 'https://', 'ftp://', 'file://')):
                encoded_query = quote(search_text)
                search_url = f"https://duckduckgo.com/?q={encoded_query}&t=h_"
                self.current_browser().setUrl(QUrl(search_url))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка поиска", 
                               f"Не удалось выполнить поиск:\n{str(e)}")

    def show_home_screen(self):
        """Показывает главный экран"""
        self.tabs.hide()
        self.home_screen.show()
        self.url_bar.clear()
        self.home_search_box.clear()
        self.home_search_box.setFocus()

    def show_browser_view(self):
        """Показывает интерфейс браузера"""
        self.home_screen.hide()
        self.tabs.show()
        self.url_bar.setFocus()

    def current_browser(self):
        """Возвращает текущий QWebEngineView"""
        if self.tabs.count() > 0:
            return self.tabs.currentWidget()
        return None

    def add_new_tab(self, qurl=None, label="Новая вкладка"):
        """Добавляет новую вкладку"""
        try:
            if qurl is None:
                qurl = QUrl('about:blank')
            
            browser = QWebEngineView()
            browser.setUrl(qurl)
            
            i = self.tabs.addTab(browser, label)
            self.tabs.setCurrentIndex(i)
            
            browser.urlChanged.connect(lambda qurl, browser=browser: 
                                    self.update_url(qurl, browser))
            browser.loadFinished.connect(lambda _, i=i, browser=browser: 
                                       self.update_tab_title(i, browser))
            
            self.show_browser_view()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", 
                               f"Не удалось открыть вкладку:\n{str(e)}")
            self.show_home_screen()

    def close_tab(self, index):
        """Закрывает вкладку"""
        try:
            if self.tabs.count() <= 1:
                self.tabs.removeTab(index)
                self.show_home_screen()
            else:
                self.tabs.removeTab(index)
        except Exception as e:
            print(f"Ошибка закрытия вкладки: {e}")

    def navigate_back(self):
        """Навигация назад"""
        if self.tabs.isVisible() and self.current_browser():
            self.current_browser().back()

    def navigate_forward(self):
        """Навигация вперед"""
        if self.tabs.isVisible() and self.current_browser():
            self.current_browser().forward()

    def navigate_reload(self):
        """Обновление страницы"""
        if self.tabs.isVisible() and self.current_browser():
            self.current_browser().reload()

    def navigate_to_url(self):
        """Переход по URL из адресной строки"""
        try:
            url = self.url_bar.text().strip()
            if not url:
                return
                
            # Если это не URL, выполняем поиск
            if not any(url.startswith(proto) for proto in ('http://', 'https://', 'ftp://', 'file://')):
                self.perform_search()
                return
                
            # Добавляем https:// если нет указания протокола
            if not url.startswith(('http://', 'https://', 'ftp://', 'file://')):
                url = 'https://' + url
                
            if self.tabs.count() == 0:
                self.add_new_tab(QUrl(url), url[:15])
            elif self.current_browser():
                self.current_browser().setUrl(QUrl(url))
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", 
                               f"Неверный URL или произошла ошибка:\n{str(e)}")

    def update_url(self, qurl=None, browser=None):
        """Обновляет URL в адресной строке"""
        try:
            if browser != self.current_browser():
                return
            
            if qurl is None and self.current_browser():
                qurl = self.current_browser().url()
            
            if qurl:
                self.url_bar.setText(qurl.toString())
                self.url_bar.setCursorPosition(0)
        except Exception as e:
            print(f"Ошибка обновления URL: {e}")

    def update_tab_title(self, index, browser):
        """Обновляет заголовок вкладки"""
        try:
            title = browser.page().title()
            if not title:
                title = "Новая вкладка"
            short_title = (title[:20] + '...') if len(title) > 20 else title
            self.tabs.setTabText(index, short_title)
        except Exception as e:
            print(f"Ошибка обновления заголовка вкладки: {e}")


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # Установка шрифта по умолчанию для лучшей читаемости
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        app.setFont(font)
        
        browser = PythonBrowser()
        browser.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        sys.exit(1)