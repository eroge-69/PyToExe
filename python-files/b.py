import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

if __name__ == '__main__':
    # 1. Tạo ứng dụng
    app = QApplication(sys.argv)
    window = QMainWindow()
    
    # 2. Tạo WebEngineView và đặt URL
    browser = QWebEngineView()
    browser.setUrl(QUrl("https://www.google.com"))
    window.setCentralWidget(browser)
    
    # 3. Hiển thị cửa sổ
    window.setWindowTitle("Kiểm Tra WebEngine")
    window.resize(800, 600)
    window.show()
    
    # 4. Chạy vòng lặp ứng dụng
    sys.exit(app.exec())
