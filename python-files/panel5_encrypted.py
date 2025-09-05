import sys, json, mysql.connector, re, base64
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtCore import QUrl, QTimer, QByteArray

# ─── Obfuscated Configuration ─────────────────────────────────────────────────

class _DbConfig:
    """Internal configuration handler"""
    @staticmethod
    def _d(s):
        """Simple decoder"""
        return base64.b64decode(s.encode()).decode()
    
    @staticmethod
    def _get_config():
        # Obfuscated values (base64 encoded)
        _h = "NDUuMzMuMTIwLjE2OA=="  # host
        _u = "ZWxiYXph"              # user
        _p = "Tm9Nb3JlTWVyY3kyOEA="  # password
        _db = "ZWxiYXph"             # database
        
        return {
            "host": _DbConfig._d(_h),
            "port": 0xcea,  # 3306 in hex
            "user": _DbConfig._d(_u),
            "password": _DbConfig._d(_p),
            "database": _DbConfig._d(_db),
            "autocommit": True
        }

# Get configuration
DB_CFG = _DbConfig._get_config()

# Alternative approach using environment variables (recommended for production):
# import os
# DB_CFG = {
#     "host": os.environ.get("DB_HOST", "localhost"),
#     "port": int(os.environ.get("DB_PORT", "3306")),
#     "user": os.environ.get("DB_USER", ""),
#     "password": os.environ.get("DB_PASS", ""),
#     "database": os.environ.get("DB_NAME", ""),
#     "autocommit": True
# }

TARGET_URL   = "https://rfrqgsmq.com/poker"
TARGET_HOST  = re.sub(r"^https?://", "", TARGET_URL).split("/")[0]

class MostbetBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mostbet Browser with DB Cookies")
        self.resize(1200, 800)

        self.view     = QWebEngineView(self)
        self.profile  = QWebEngineProfile.defaultProfile()
        self.view.setUrl(QUrl(TARGET_URL))

        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText("Введите ID записи")
        self.id_input.returnPressed.connect(self.on_load_clicked)

        self.load_btn = QPushButton("LOAD", self)
        self.load_btn.clicked.connect(self.on_load_clicked)

        hbox = QHBoxLayout()
        hbox.addWidget(self.id_input)
        hbox.addWidget(self.load_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addLayout(hbox)

    def on_load_clicked(self):
        rec_id = self.id_input.text().strip()
        if not rec_id.isdigit():
            QMessageBox.warning(self, "Ошибка", "ID должен быть числом")
            return

        cookies_json = self.fetch_cookies_by_id(int(rec_id))
        if cookies_json is None:
            QMessageBox.warning(self, "Не найдено", f"Запись с id={rec_id} отсутствует")
            return

        try:
            cookies = json.loads(cookies_json)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Ошибка", "Cookie-поле не JSON")
            return

        cookies = self.inject_missing_cookies(cookies)

        store = self.profile.cookieStore()
        store.deleteAllCookies()
        QTimer.singleShot(500, lambda: self.second_clear_then_set(store, cookies))

    def second_clear_then_set(self, store, cookies):
        store.deleteAllCookies()
        QTimer.singleShot(500, lambda: self.set_cookies_and_reload(store, cookies))

    def set_cookies_and_reload(self, store, cookies):
        for c in cookies:
            name    = c.get("name", "")
            value   = c.get("value", "")
            domain  = c.get("domain", "").lstrip(".")
            path    = c.get("path", "/")
            secure  = c.get("secure", False)
            httponly = c.get("httpOnly", False)

            if name == "theme":
                value = "desktop"

            if TARGET_HOST not in domain:
                continue

            qcookie = QNetworkCookie(QByteArray(name.encode()), QByteArray(value.encode()))
            qcookie.setDomain(domain)
            qcookie.setPath(path)
            qcookie.setSecure(secure)
            qcookie.setHttpOnly(httponly)
            store.setCookie(qcookie)

        self.view.setUrl(QUrl("about:blank"))
        QTimer.singleShot(500, lambda: self.view.setUrl(QUrl(TARGET_URL)))

    def fetch_cookies_by_id(self, rec_id: int) -> str | None:
        try:
            with mysql.connector.connect(**DB_CFG) as conn, conn.cursor() as cur:
                cur.execute("SELECT cookie FROM elbaza WHERE id = %s", (rec_id,))
                row = cur.fetchone()
                return row[0] if row else None
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "MySQL error", str(e))
            return None

    def inject_missing_cookies(self, cookies: list) -> list:
        names = {c['name']: c for c in cookies}
        uid = names.get("uid", {}).get("value", "")
        jwt = names.get("jwt_bridge", {}).get("value", "")
        rulid = names.get("rulid", {}).get("value", "")

        def template(name, value, extra):
            return {
                "name": name,
                "value": value,
                "domain": "rfrqgsmq.com",
                "hostOnly": True,
                "path": "/",
                "secure": extra.get("secure", False),
                "httpOnly": extra.get("httpOnly", False),
                "sameSite": "no_restriction",
                "session": extra.get("session", False),
                "expirationDate": extra.get("expirationDate", 1774806262),
                "storeId": "0"
            }

        def add(name, value, extra):
            if name not in names:
                cookies.append(template(name, value, extra))

        add("rst4-uid", uid, {"secure": True})
        add("feature_ab_cdn", "cf", {"secure": False, "session": True})
        add("user_token", jwt, {"secure": False, "expirationDate": 1752357898})
        add("_odd_format", "decimal", {"secure": True, "expirationDate": 1782684284.023262})
        add("multiAuthRepeatAfter", "true", {"secure": False, "expirationDate": 1751234686})
        add("design", "old", {"secure": False, "expirationDate": 1782684287.821172})
        add("User_cookie_key", rulid, {"secure": False, "expirationDate": 1782684288.486091})

        return cookies

# ─── Запуск ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MostbetBrowser()
    win.show()
    sys.exit(app.exec())