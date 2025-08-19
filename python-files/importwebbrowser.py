import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class BrowserWindow(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("BrainRot Radio")

        width, height = 400, 450
        self.setFixedSize(width, height)  # Prevent resizing

        # Create the web view
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.setCentralWidget(self.browser)

        # Inject JavaScript to hide scrollbars after page load
        self.browser.loadFinished.connect(self.hide_scrollbars)

    def hide_scrollbars(self):
        js_code = """
            var style = document.createElement('style');
            style.type = 'text/css';
            style.innerText = '::-webkit-scrollbar { display: none; }';
            document.head.appendChild(style);
        """
        self.browser.page().runJavaScript(js_code)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow("https://www.brainrotradio.com/")  # Replace with your desired URL
    window.show()
    sys.exit(app.exec_())
