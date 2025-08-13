import sys
import re
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile

GOOGLE_HOME = "https://www.google.com/"
GOOGLE_SEARCH = "https://www.google.com/search?q="

def is_probably_url(text: str) -> bool:
    # sehr einfache Heuristik
    return bool(re.match(r"^([a-z]+://)?[^\s]+\.[^\s]+/?", text, re.IGNORECASE))

class PrivateBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Private Browser")
        self.resize(1024, 700)

        # --- PRIVACY-PROFIL (kein Verlauf, keine Cookies, kein Cache auf Platte) ---
        self.profile = QWebEngineProfile(self)               # eigenes Profil
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)
        # optional: nur Speicher-Cache (falls du kurzfristig etwas brauchst)
        # self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)

        # Historie wird von Qt nicht persistent auf Platte gespeichert;
        # wir sorgen zusätzlich dafür, dass beim Beenden alles gelöscht wird.
        app = QApplication.instance()
        app.aboutToQuit.connect(self._wipe_session)

        # --- UI ---
        self.view = QWebEngineView(self)
        self.view.setPage(self.profile.newPage())  # Seite mit privatem Profil
        self.view.setUrl(QUrl(GOOGLE_HOME))

        self.address = QLineEdit(self)
        self.address.setPlaceholderText("Suche oder URL eingeben …")
        self.address.returnPressed.connect(self._go)

        btn_back = QPushButton("←")
        btn_back.clicked.connect(self.view.back)
        btn_fwd = QPushButton("→")
        btn_fwd.clicked.connect(self.view.forward)
        btn_reload = QPushButton("⟳")
        btn_reload.clicked.connect(self.view.reload)
        btn_home = QPushButton("🏠")
        btn_home.clicked.connect(lambda: self.view.setUrl(QUrl(GOOGLE_HOME)))

        top = QHBoxLayout()
        for w in (btn_back, btn_fwd, btn_reload, btn_home, self.address):
            top.addWidget(w)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Adressleiste mit aktueller URL synchronisieren (optional)
        self.view.urlChanged.connect(lambda url: self.address.setText(url.toString()))

        # Popups/„Neues Fenster“ immer in diesem Fenster öffnen
        self.view.page().setViewportSize(self.view.size())

    def _go(self):
        text = self.address.text().strip()
        if not text:
            return
        if is_probably_url(text):
            # https voreinstellen, falls Schema fehlt
            if not re.match(r"^[a-z]+://", text, re.IGNORECASE):
                text = "https://" + text
            self.view.setUrl(QUrl(text))
        else:
            self.view.setUrl(QUrl(GOOGLE_SEARCH + QUrl.toPercentEncoding(text).data().decode()))

    def _wipe_session(self):
        # Cache & Cookies zum Sitzungsende killen (zusätzliche Sicherheitsstufe)
        self.profile.clearHttpCache()
        cookie_store = self.profile.cookieStore()
        cookie_store.deleteAllCookies()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Minimal Private Browser")
    win = PrivateBrowser()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()