
import sys
import os
import subprocess
import json
import psutil
import urllib.parse
from typing import Optional

HARD_CODED_PROXY: Optional[str] = "socks5://127.0.0.1:9050 " 
SETTINGS_FILE = "settings.json"
TOR_SOCKS_PORT = 9050


def load_settings() -> dict:
    defaults = {
        "homepage": "https://duckduckgo.com",
        "dark_mode": False,
        "search_engine": "DuckDuckGo",
        "vpn_proxy": "",
        "tor_only": True,
        "adblock_enabled": True,
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


def find_tor_executable() -> Optional[str]:
    candidates = [
        os.path.join("tor", "tor.exe"),
        os.path.join("tor", "tor"),
        "tor.exe",
        "tor",
    ]
    for c in candidates:
        if os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


def start_tor() -> Optional[subprocess.Popen]:
    tor_path = find_tor_executable()
    if not tor_path:
        print("[WARN] Tor not found. Running without Tor.")
        return None
    print(f"[INFO] Starting Tor from: {tor_path}")
    try:
        proc = subprocess.Popen([tor_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc
    except Exception as e:
        print(f"[ERROR] Failed to start Tor: {e}")
        return None


settings = load_settings()

tor_proc = start_tor()
tor_active = tor_proc is not None

if settings.get("tor_only", True) and not tor_active:
    print("[FATAL] Tor is required (tor_only=True) but Tor could not be started. Place Tor bundle in ./tor/ or tor.exe in this folder.")
    sys.exit(1)

proxy_to_use: Optional[str]
if HARD_CODED_PROXY:
    proxy_to_use = HARD_CODED_PROXY
elif settings.get("vpn_proxy"):
    proxy_to_use = settings.get("vpn_proxy")
elif tor_active:
    proxy_to_use = f"socks5://127.0.0.1:{TOR_SOCKS_PORT}"
else:
    proxy_to_use = None

flags = []
if proxy_to_use:
    flags.append(f"--proxy-server={proxy_to_use}")
flags.extend([
    "--enable-gpu-rasterization",
    "--enable-zero-copy",
    "--disable-background-timer-throttling",
    "--disk-cache-size=200000000",
])

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QToolBar,
    QStatusBar, QMenu, QInputDialog, QPushButton, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
)
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction


class AdBlocker(QWebEngineUrlRequestInterceptor):
    def __init__(self, blocklist=None):
        super().__init__()
        self.blocklist = blocklist or [
            "doubleclick.net", "googlesyndication.com", "google-analytics.com",
            "adservice.", "ads.", "advert", "analytics", "tracker", "track",
        ]

    def interceptRequest(self, info: QWebEngineUrlRequestInfo) -> None:
        try:
            url = info.requestUrl().toString()
            for blk in self.blocklist:
                if blk in url:
                    info.block(True)
                    return
        except Exception:
            pass


class Browser(QMainWindow):
    def __init__(self, tor_active: bool, settings: dict):
        super().__init__()
        self.settings = settings
        self.tor_active = tor_active
        self.setWindowTitle("Secure PyQt Browser")
        self.resize(1200, 800)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        if self.settings.get("adblock_enabled", True):
            self.adblocker = AdBlocker()
            try:
                self.profile.setUrlRequestInterceptor(self.adblocker)
            except Exception:
                pass

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.settings.get("homepage", "https://duckduckgo.com")))
        self.setCentralWidget(self.browser)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

        back_btn = QPushButton("⬅")
        back_btn.clicked.connect(self.browser.back)
        toolbar.addWidget(back_btn)

        fwd_btn = QPushButton("➡")
        fwd_btn.clicked.connect(self.browser.forward)
        toolbar.addWidget(fwd_btn)

        home_btn = QPushButton("🏠")
        home_btn.clicked.connect(self.load_homepage)
        toolbar.addWidget(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)

        settings_menu = QMenu("⚙ Settings", self)

        self.dark_action = QAction("Enable Dark Mode", self, checkable=True)
        self.dark_action.setChecked(self.settings.get("dark_mode", False))
        self.dark_action.triggered.connect(self.toggle_dark_mode)
        settings_menu.addAction(self.dark_action)

        change_home_action = QAction("Change Homepage", self)
        change_home_action.triggered.connect(self.change_homepage)
        settings_menu.addAction(change_home_action)

        search_menu = QMenu("Search Engine", self)
        for engine in ["DuckDuckGo", "Google", "Startpage", "Brave"]:
            act = QAction(engine, self, checkable=True)
            act.setChecked(engine == self.settings.get("search_engine", "DuckDuckGo"))
            act.triggered.connect(lambda checked, e=engine: self.set_search_engine(e))
            search_menu.addAction(act)
        settings_menu.addMenu(search_menu)

        vpn_action = QAction("Set VPN/Proxy", self)
        vpn_action.triggered.connect(self.set_vpn_proxy)
        settings_menu.addAction(vpn_action)

        tor_only_action = QAction("Require Tor (exit if Tor missing)", self, checkable=True)
        tor_only_action.setChecked(self.settings.get("tor_only", True))
        tor_only_action.triggered.connect(self.toggle_tor_only)
        settings_menu.addAction(tor_only_action)

        adblock_action = QAction("Enable AdBlock", self, checkable=True)
        adblock_action.setChecked(self.settings.get("adblock_enabled", True))
        adblock_action.triggered.connect(self.toggle_adblock)
        settings_menu.addAction(adblock_action)

        clear_cache_action = QAction("Clear Cache", self)
        clear_cache_action.triggered.connect(self.clear_cache)
        settings_menu.addAction(clear_cache_action)

        toolbar.addAction(settings_menu.menuAction())

        self.setStatusBar(QStatusBar())
        self.update_status_bar()

        if self.settings.get("dark_mode", False):
            self.apply_dark_mode()

    def update_status_bar(self):
        proxy = self.settings.get("vpn_proxy", "") or (HARD_CODED_PROXY or "")
        if proxy:
            self.statusBar().showMessage(f"Using proxy: {proxy}")
        else:
            self.statusBar().showMessage("Connected via Tor" if self.tor_active else "Direct connection (Tor not active)")

    def load_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if not text.startswith("http"):
            self.browser.setUrl(QUrl(self.get_search_url(text)))
        else:
            self.browser.setUrl(QUrl(text))

    def load_homepage(self):
        self.browser.setUrl(QUrl(self.settings.get("homepage")))

    def update_url(self, url: QUrl):
        self.url_bar.setText(url.toString())

    def toggle_dark_mode(self):
        self.settings["dark_mode"] = not self.settings.get("dark_mode", False)
        save_settings(self.settings)
        if self.settings["dark_mode"]:
            self.apply_dark_mode()
        else:
            self.setStyleSheet("")

    def apply_dark_mode(self):
        self.setStyleSheet("QMainWindow { background-color: #121212; color: white; }"
                           "QLineEdit { background-color: #333; color: white; }"
                           "QToolBar { background-color: #222; }")
        dark_css = "body { background-color: #121212 !important; color: #e0e0e0 !important; } a { color: #bb86fc !important; }"
        self.browser.page().runJavaScript(f"(function(){{var s=document.createElement('style');s.innerHTML=`{dark_css}`;document.head.appendChild(s);}})();")

    def change_homepage(self):
        new_home, ok = QInputDialog.getText(self, "Change Homepage", "Enter homepage URL:")
        if ok and new_home.strip():
            self.settings["homepage"] = new_home.strip()
            save_settings(self.settings)
            self.browser.setUrl(QUrl(self.settings["homepage"]))

    def set_search_engine(self, engine: str):
        self.settings["search_engine"] = engine
        save_settings(self.settings)

    def set_vpn_proxy(self):
        new_proxy, ok = QInputDialog.getText(self, "Set VPN/Proxy", "Enter proxy (e.g. socks5://127.0.0.1:1080):")
        if ok:
            self.settings["vpn_proxy"] = new_proxy.strip()
            save_settings(self.settings)
            QMessageBox.information(self, "Proxy Saved", "Proxy saved. Restart the app to apply proxy settings.")

    def toggle_tor_only(self):
        self.settings["tor_only"] = not self.settings.get("tor_only", True)
        save_settings(self.settings)

    def toggle_adblock(self):
        self.settings["adblock_enabled"] = not self.settings.get("adblock_enabled", True)
        save_settings(self.settings)
        QMessageBox.information(self, "AdBlock", "AdBlock setting saved. Restart app to apply.")

    def get_search_url(self, query: str) -> str:
        q = urllib.parse.quote_plus(query)
        engines = {
            "DuckDuckGo": f"https://duckduckgo.com/?q={q}",
            "Google": f"https://www.google.com/search?q={q}",
            "Startpage": f"https://www.startpage.com/do/dsearch?query={q}",
            "Brave": f"https://search.brave.com/search?q={q}",
        }
        return engines.get(self.settings.get("search_engine"), engines["DuckDuckGo"])

    def clear_cache(self):
        self.profile.clearHttpCache()
        self.statusBar().showMessage("Cache Cleared!", 3000)


def main() -> int:
    app = QApplication(sys.argv)
    window = Browser(tor_active, settings)
    window.show()

    try:
        p = psutil.Process(os.getpid())
        if os.name == "nt":
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
            p.nice(-10)
    except Exception:
        pass

    exit_code = app.exec()

   
    if tor_proc:
        try:
            tor_proc.terminate()
        except Exception:
            pass
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
