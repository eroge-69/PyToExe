import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtCore import QUrl

class PrivateBrowser(QMainWindow)
    def __init__(self)
        super().__init__()
        self.setWindowTitle(متصفح خاص - سام)

        # ملف بروفايل خاص (off-the-record ضمنيًا)
        profile = QWebEngineProfile(self)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)

        # صفحة ويب مربوطة بالبروفايل
        page = QWebEnginePage(profile, self)

        # عرض الويب
        view = QWebEngineView()
        view.setPage(page)
        view.setUrl(QUrl(httpswww.google.com))

        self.setCentralWidget(view)

def main()
    app = QApplication(sys.argv)
    window = PrivateBrowser()
    window.show()
    app.exec_()

if __name__ == '__main__'
    try
        main()
    except Exception
        traceback.print_exc()
    finally
        input(اضغط Enter للخروج...)
