import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, 
                             QLineEdit, QAction, QTabWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon

class TabBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Создаем систему вкладок
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_double_click)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        self.setCentralWidget(self.tabs)
        
        # Панель инструментов
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Кнопки навигации
        back_btn = QAction("←", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        toolbar.addAction(back_btn)
        
        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        toolbar.addAction(forward_btn)
        
        reload_btn = QAction("↻", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        toolbar.addAction(reload_btn)
        
        # Кнопка новой вкладки
        new_tab_btn = QAction("+", self)
        new_tab_btn.triggered.connect(self.add_new_tab)
        toolbar.addAction(new_tab_btn)
        
        # Поле URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Добавляем первую вкладку
        self.add_new_tab(QUrl('https://www.google.com'), 'Главная')
        
        # Настройки окна
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowTitle("Python Browser")
        self.show()
    
    def add_new_tab(self, qurl=None, label="Новая вкладка"):
        if qurl is None:
            qurl = QUrl('https://www.google.com')
        
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        browser.urlChanged.connect(lambda qurl, browser=browser: 
            self.update_url(qurl, browser))
        
        browser.loadFinished.connect(lambda _, i=i, browser=browser: 
            self.tabs.setTabText(i, browser.page().title()[:20] + "..."))
    
    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
    
    def current_browser(self):
        return self.tabs.currentWidget()
    
    def tab_double_click(self, i):
        if i == -1:  # Двойной клик на пустом месте
            self.add_new_tab()
    
    def current_tab_changed(self, i):
        if i >= 0:
            qurl = self.current_browser().url()
            self.update_url(qurl, self.current_browser())
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith('http'):
            url = 'https://' + url
        
        self.current_browser().setUrl(QUrl(url))
    
    def update_url(self, q, browser=None):
        if browser != self.current_browser():
            return
        self.url_bar.setText(q.toString())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = TabBrowser()
    sys.exit(app.exec_())