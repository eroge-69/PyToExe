import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QComboBox, 
                             QTabWidget, QToolBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class ApMegaBro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ApMegaBro")
        self.setGeometry(100, 100, 1024, 768)
        
        # Создаем главный виджет и вертикальный layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Создаем панель инструментов с адресной строкой и кнопками
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        # Кнопки навигации
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.navigate_back)
        self.toolbar.addWidget(self.back_button)
        
        self.forward_button = QPushButton("→")
        self.forward_button.clicked.connect(self.navigate_forward)
        self.toolbar.addWidget(self.forward_button)
        
        self.reload_button = QPushButton("↻")
        self.reload_button.clicked.connect(self.reload_page)
        self.toolbar.addWidget(self.reload_button)
        
        self.home_button = QPushButton("⌂")
        self.home_button.clicked.connect(self.navigate_home)
        self.toolbar.addWidget(self.home_button)
        
        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)
        
        # Выбор поисковой системы
        self.search_engine = QComboBox()
        self.search_engine.addItem("Google")
        self.search_engine.addItem("Yandex")
        self.toolbar.addWidget(self.search_engine)
        
        # Кнопка поиска
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.search)
        self.toolbar.addWidget(self.search_button)
        
        # Создаем виджет вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.layout.addWidget(self.tabs)
        
        # Добавляем первую вкладку
        self.add_new_tab(QUrl("https://www.google.com"), "Главная")
        
        # Показываем окно
        self.show()
    
    def add_new_tab(self, qurl=None, label="Новая вкладка"):
        if qurl is None:
            qurl = QUrl("https://www.google.com")
        
        # Создаем новый веб-вью
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Добавляем вкладку
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Обновляем URL при изменении страницы
        browser.urlChanged.connect(lambda qurl, browser=browser: 
                                  self.update_urlbar(qurl, browser))
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
    
    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.back()
    
    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.forward()
    
    def reload_page(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.reload()
    
    def navigate_home(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl("https://www.google.com"))
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))
    
    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)
    
    def search(self):
        query = self.url_bar.text()
        if not query:
            return
        
        search_engine = self.search_engine.currentText()
        
        if search_engine == "Google":
            url = f"https://www.google.com/search?q={query}"
        else:  # Yandex
            url = f"https://yandex.ru/search/?text={query}"
        
        current_browser = self.tabs.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = ApMegaBro()
    sys.exit(app.exec_())