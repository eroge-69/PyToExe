import sys
import random
from pathlib import Path
from PyQt5.QtCore import QUrl, QStandardPaths, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QTabWidget, QFileDialog, QMessageBox, QDialog, QVBoxLayout,
    QTextEdit, QPushButton
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEngineProfile, QWebEnginePage
)


# Custom page: allow links to navigate inside the view
class CustomWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, nav_type, isMainFrame):
        # allow clicking links to navigate inside the view
        # (do not open external browser)
        return super().acceptNavigationRequest(url, nav_type, isMainFrame)


# Simple dialogs for history and downloads
class HistoryDialog(QDialog):
    def __init__(self, history_file: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("History")
        self.resize(700, 500)
        layout = QVBoxLayout(self)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)
        self.history_file = history_file
        self.load()

    def load(self):
        if self.history_file.exists():
            try:
                self.text.setPlainText(self.history_file.read_text(encoding="utf-8"))
            except Exception as e:
                self.text.setPlainText(f"Failed to load history:\n{e}")
        else:
            self.text.setPlainText("No history.")


class DownloadsDialog(QDialog):
    def __init__(self, downloads_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.resize(700, 500)
        layout = QVBoxLayout(self)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)
        self.downloads_list = downloads_list
        self.load()

    def load(self):
        if self.downloads_list:
            self.text.setPlainText("\n".join(self.downloads_list))
        else:
            self.text.setPlainText("No downloads.")


class Browser(QMainWindow):
    MAX_TABS_WARNING = 10

    WARNING_MESSAGES = [
        "ur compuetr gonna explode",
        "too many tabs nigger",
        "asshole your computer egst slower",
        "close tabs before your pc turns into a nuke",
        "stop"
    ]

    DOWNLOAD_MESSAGES = [
        "download complete lol",
        "File saved. Did you really need that?",
        "Download finished. Your data is safe... probably.",
        "Congrats! Another file in the wild.",
        "Downloaded like a pro. Nice one."
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("goggley hromimum")
        self.resize(1200, 800)

        # profiles
        self.normal_profile = QWebEngineProfile.defaultProfile()
        self.incognito_profile = QWebEngineProfile(parent=None)
        # configure incognito-like profile
        self.incognito_profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.incognito_profile.setCachePath("")  # disable cache path
        self.incognito_profile.setPersistentStoragePath("")  # disable storage

        # ensure we handle download requests from profiles once
        self.normal_profile.downloadRequested.connect(self.handle_download)
        self.incognito_profile.downloadRequested.connect(self.handle_download)

        self.is_incognito = False

        # history & downloads
        self.history_file = Path("history.txt")
        self.downloads_list = []

        # tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.setCentralWidget(self.tabs)

        # toolbar - text-only actions
        tb = QToolBar("Navigation")
        self.addToolBar(tb)

        act_back = QAction("Back", self); act_back.triggered.connect(self.go_back); tb.addAction(act_back)
        act_forward = QAction("Forward", self); act_forward.triggered.connect(self.go_forward); tb.addAction(act_forward)
        act_reload = QAction("Reload", self); act_reload.triggered.connect(self.reload_page); tb.addAction(act_reload)
        tb.addSeparator()
        self.act_incognito = QAction("Incognito", self); self.act_incognito.setCheckable(True)
        self.act_incognito.triggered.connect(self.toggle_incognito); tb.addAction(self.act_incognito)
        tb.addSeparator()
        act_new = QAction("New Tab", self); act_new.triggered.connect(lambda: self.add_new_tab(start_page=True)); tb.addAction(act_new)
        tb.addSeparator()
        act_downloads = QAction("Downloads", self); act_downloads.triggered.connect(self.show_downloads); tb.addAction(act_downloads)
        act_history = QAction("History", self); act_history.triggered.connect(self.show_history); tb.addAction(act_history)
        tb.addSeparator()
        self.urlbar = QLineEdit(); self.urlbar.returnPressed.connect(self.navigate_to_url); tb.addWidget(self.urlbar)

        # status/loading animation (90s style)
        self.status = self.statusBar()
        self.loading_text = "Loading"
        self.loading_idx = 0
        self.loading_timer = QTimer(self)
        self.loading_timer.setInterval(500)
        self.loading_timer.timeout.connect(self._update_loading)

        # create initial tab: start page is local file
        start_url = QUrl.fromLocalFile("/home/stepan/startpage.html")
        self.add_new_tab(qurl=start_url, label="Start", start_page=False)

    # --- tab / page creation ---
    def create_browser_view(self, qurl: QUrl = None):
        profile = self.incognito_profile if self.is_incognito else self.normal_profile
        page = CustomWebEnginePage(profile, self)
        view = QWebEngineView()
        view.setPage(page)
        if qurl:
            view.load(qurl)
        # connect signals for loading, url updates
        view.urlChanged.connect(self.update_urlbar_for_view)
        view.loadStarted.connect(self._on_load_started)
        view.loadFinished.connect(self._on_load_finished)
        return view

    def add_new_tab(self, qurl: QUrl = None, label: str = "New Tab", start_page: bool = False):
        # if start_page True, load local startpage file
        if start_page:
            qurl = QUrl.fromLocalFile("/home/stepan/startpage.html")
        if qurl is None:
            qurl = QUrl("https://www.google.com")
        # warn if many tabs
        if self.tabs.count() >= self.MAX_TABS_WARNING:
            QMessageBox.warning(self, "RAM Warning", random.choice(self.WARNING_MESSAGES))
        view = self.create_browser_view(qurl)
        idx = self.tabs.addTab(view, label)
        self.tabs.setCurrentIndex(idx)

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            return
        self.tabs.removeTab(index)

    def on_tab_changed(self, index):
        # update urlbar to reflect active tab
        view = self.tabs.widget(index)
        if view:
            cur = view.url().toString()
            self.urlbar.setText(cur)

    # --- navigation / address bar ---
    def navigate_to_url(self):
        text = self.urlbar.text().strip()
        if not text:
            return
        if not text.startswith(("http://", "https://", "file://")):
            text = "http://" + text
        view = self.tabs.currentWidget()
        if view and hasattr(view, "load"):
            view.load(QUrl(text))

    def update_urlbar_for_view(self, qurl):
        # update address bar only if widget that emitted is current
        view = self.sender()
        if view is self.tabs.currentWidget():
            self.urlbar.setText(qurl.toString())
            # append to history on main-frame navigation
            try:
                with open(self.history_file, "a", encoding="utf-8") as f:
                    f.write(qurl.toString() + "\n")
            except Exception:
                pass

    # --- back/forward/reload ---
    def go_back(self):
        view = self.tabs.currentWidget()
        if view:
            view.back()

    def go_forward(self):
        view = self.tabs.currentWidget()
        if view:
            view.forward()

    def reload_page(self):
        view = self.tabs.currentWidget()
        if view:
            view.reload()

    # --- loading animation (90s style) ---
    def _on_load_started(self):
        # start status animation
        self.loading_idx = 0
        if not self.loading_timer.isActive():
            self.loading_timer.start()

    def _on_load_finished(self, ok):
        # stop animation
        if self.loading_timer.isActive():
            self.loading_timer.stop()
        self.status.clearMessage()
        # if load failed (ok == False) show simple offline page
        if not ok:
            view = self.sender()
            try:
                view.setHtml(self._no_internet_html())
            except Exception:
                pass

    def _update_loading(self):
        dots = "." * (self.loading_idx % 4)
        self.status.showMessage(self.loading_text + dots)
        self.loading_idx += 1

    def _no_internet_html(self):
        return """
        <html><body style="background:#2a2a2a;color:#ff5555;font-family:Arial;text-align:center;margin-top:12%;">
        <svg width="120" height="120" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
          <circle cx="32" cy="32" r="28" stroke="#ff5555" stroke-width="4" fill="none"/>
          <line x1="12" y1="12" x2="52" y2="52" stroke="#ff5555" stroke-width="4"/>
        </svg>
        <h1>No Internet</h1><p>Check connection and try again.</p></body></html>
        """

    # --- downloads handling ---
    def handle_download(self, download):
        # `download` is a QWebEngineDownloadItem
        downloads_path = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        if not downloads_path:
            downloads_path = str(Path.home() / "Downloads")
        suggested = str(Path(downloads_path) / download.downloadFileName())
        path, _ = QFileDialog.getSaveFileName(self, "Save File", suggested)
        if path:
            download.setPath(path)
            download.accept()
            # record when finished
            download.finished.connect(lambda: self._on_download_finished(path))
        else:
            download.cancel()

    def _on_download_finished(self, path):
        self.downloads_list.append(path)
        msg = random.choice(self.DOWNLOAD_MESSAGES)
        QMessageBox.information(self, "Download", f"{msg}\nSaved to:\n{path}")

    # --- history / downloads dialogs ---
    def show_history(self):
        dlg = HistoryDialog(self.history_file, self)
        dlg.exec_()

    def show_downloads(self):
        dlg = DownloadsDialog(self.downloads_list, self)
        dlg.exec_()

    # --- incognito mode ---
    def toggle_incognito(self):
        self.is_incognito = not self.is_incognito
        self.act_incognito.setChecked(self.is_incognito)
        # show requested two-step message when enabling
        if self.is_incognito:
            self._show_incognito_messages()
        # rebuild tabs preserving current URLs and labels using new profile
        urls = []
        labels = []
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            urls.append(w.url())
            labels.append(self.tabs.tabText(i))
        # remove all tabs
        while self.tabs.count():
            self.tabs.removeTab(0)
        # re-add tabs with same urls (pages will use the selected profile)
        for i, u in enumerate(urls):
            view = self.create_browser_view(u)
            idx = self.tabs.addTab(view, labels[i] or "Tab")
            # keep current index as previous
        if urls:
            self.tabs.setCurrentIndex(0)

    def _show_incognito_messages(self):
        mb = QMessageBox(self)
        mb.setWindowTitle("Incognito Mode")
        mb.setText("cool youre now just think your stuff are secret when actually not")
        mb.show()
        # after 1 second change text
        QTimer.singleShot(5000, lambda: mb.setText("YOU CAN STILL VIEW WHAT YOU HAVE SEEN"))

    # --- utility ---
    def closeEvent(self, event):
        # clean shutdown
        try:
            if self.loading_timer.isActive():
                self.loading_timer.stop()
        except Exception:
            pass
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    win = Browser()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

