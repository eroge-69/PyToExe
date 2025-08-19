import sys, os, json, importlib
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLineEdit, QToolBar, QAction, QStatusBar, QDialog, QCheckBox,
    QPushButton, QLabel
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

# Plugin arayüzü
class PluginBase:
    def activate(self, browser):
        raise NotImplementedError("Eklenti 'activate' metodunu tanımlamalı.")

# Tarayıcı sekmesi
class BrowserTab(QWidget):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        self.layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

# Eklenti yöneticisi
class PluginManager(QDialog):
    def __init__(self, plugin_config_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔌 Eklenti Yöneticisi")
        self.layout = QVBoxLayout()
        self.plugin_config_path = plugin_config_path

        with open(plugin_config_path, "r") as f:
            self.config = json.load(f)

        self.checkboxes = {}
        for plugin_name, enabled in self.config.items():
            cb = QCheckBox(plugin_name)
            cb.setChecked(enabled)
            self.checkboxes[plugin_name] = cb
            self.layout.addWidget(cb)

        save_btn = QPushButton("Kaydet ve Yeniden Başlat")
        save_btn.clicked.connect(self.save_config)
        self.layout.addWidget(save_btn)
        self.setLayout(self.layout)

    def save_config(self):
        for name, cb in self.checkboxes.items():
            self.config[name] = cb.isChecked()
        with open(self.plugin_config_path, "w") as f:
            json.dump(self.config, f, indent=4)
        self.accept()

# Eklenti mağazası
class PluginStore(QDialog):
    def __init__(self, store_dir="plugin_store", plugin_dir="plugins", parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛍️ Eklenti Mağazası")
        self.layout = QVBoxLayout()
        self.store_dir = store_dir
        self.plugin_dir = plugin_dir

        if not os.path.exists(store_dir):
            os.makedirs(store_dir)

        files = [f for f in os.listdir(store_dir) if f.endswith(".py")]
        if not files:
            self.layout.addWidget(QLabel("Mağazada eklenti bulunamadı."))

        for filename in files:
            btn = QPushButton(f"Eklentiyi Yükle: {filename}")
            btn.clicked.connect(lambda _, f=filename: self.install_plugin(f))
            self.layout.addWidget(btn)

        self.setLayout(self.layout)

    def install_plugin(self, filename):
        src = os.path.join(self.store_dir, filename)
        dst = os.path.join(self.plugin_dir, filename)
        if not os.path.exists(dst):
            with open(src, "r") as fsrc, open(dst, "w") as fdst:
                fdst.write(fsrc.read())
        self.accept()

# Ana tarayıcı
class KamiBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kamibrowser 🌐")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        self.add_navigation_buttons()
        self.add_plugin_buttons()
        self.add_new_tab("https://www.google.com")

        self.load_plugins()

    def add_navigation_buttons(self):
        back_btn = QAction("←", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        self.toolbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        self.toolbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        self.toolbar.addAction(reload_btn)

        new_tab_btn = QAction("➕ Yeni Sekme", self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        self.toolbar.addAction(new_tab_btn)

    def add_plugin_buttons(self):
        plugin_btn = QAction("🔌 Eklenti Yöneticisi", self)
        plugin_btn.triggered.connect(lambda: PluginManager("plugins/config.json", self).exec_())
        self.toolbar.addAction(plugin_btn)

        store_btn = QAction("🛍️ Mağaza", self)
        store_btn.triggered.connect(lambda: PluginStore(parent=self).exec_())
        self.toolbar.addAction(store_btn)

    def current_browser(self):
        return self.tabs.currentWidget().browser

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

    def add_new_tab(self, url="https://www.google.com"):
        new_tab = BrowserTab(url)
        self.tabs.addTab(new_tab, "Yeni Sekme")
        self.tabs.setCurrentWidget(new_tab)

    def load_plugins(self):
        plugin_dir = "plugins"
        config_path = os.path.join(plugin_dir, "config.json")

        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)

        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                json.dump({}, f)

        with open(config_path, "r") as f:
            config = json.load(f)

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                plugin_name = filename[:-3]
                if not config.get(plugin_name, False):
                    continue
                module = importlib.import_module(f"{plugin_dir}.{plugin_name}")
                for attr in dir(module):
                    plugin_class = getattr(module, attr)
                    if isinstance(plugin_class, type) and issubclass(plugin_class, PluginBase):
                        plugin_instance = plugin_class()
                        plugin_instance.activate(self)

# Başlat
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KamiBrowser()
    window.show()
    sys.exit(app.exec_())