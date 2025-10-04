"""
paranoid_tor_browser_windows_cleanup.py

Extends previous paranoid browser with Windows deep cleanup:
 - flush Windows DNS cache
 - clear temp directories (Windows\Temp, user temp, Prefetch)
 - runs cleanup on each search if paranoid clean enabled, and also on panic
Requirements:
 - Must be run with rights able to delete in those temp directories; some operations may fail otherwise.
"""

import sys
import os
import uuid
import tempfile
import shutil
import random
import subprocess
import platform
import time
import json
from pathlib import Path

from qtpy.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton, QToolButton, QCheckBox, QLabel, QComboBox
)
from qtpy.QtCore import QUrl, Qt, QTimer
from qtpy.QtGui import QIcon

# Chromium flags
chromium_flags = [
    "--no-sandbox",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-webgl",
    "--disable-accelerated-2d-canvas",
    "--disable-accelerated-video-decode",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-component-extensions-with-background-pages",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-plugins",
    "--disable-popup-blocking",
]
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(chromium_flags)

from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage, QWebEngineSettings

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
]

SPOOF_FONTS = [
    "Arial, Helvetica, sans-serif",
    "Segoe UI, Arial, sans-serif",
    "Roboto, Noto Sans, sans-serif",
    "Times New Roman, Times, serif",
    "Georgia, 'Times New Roman', Times, serif"
]

OLED_BLACK_CSS = """
:root, html, body, * {
    background-color: #000000 !important;
    color: #FFFFFF !important;
    border-color: #0a0a0a !important;
    box-shadow: none !important;
    text-shadow: none !important;
}
a { color: #66ccff !important; }
img, video { background: transparent !important; }
"""

HARDEN_JS_TEMPLATE = r"""
(function(){
    try {
        var css = `%s`;
        var s = document.createElement('style');
        s.type='text/css';
        s.id='paranoid_oled';
        s.appendChild(document.createTextNode(css));
        (document.head || document.documentElement).appendChild(s);
    } catch(e){}

    try {
        var payload = %s;

        // spoof navigator
        var nav = navigator;
        var spoof = payload.navigator;
        Object.defineProperty(nav, 'userAgent', { get: function(){ return spoof.userAgent; } });
        Object.defineProperty(nav, 'platform', { get: function(){ return spoof.platform; } });
        Object.defineProperty(nav, 'language', { get: function(){ return spoof.language; } });
        Object.defineProperty(nav, 'languages', { get: function(){ return spoof.languages; } });
        Object.defineProperty(nav, 'hardwareConcurrency', { get: function(){ return spoof.hardwareConcurrency; } });
        Object.defineProperty(nav, 'maxTouchPoints', { get: function(){ return spoof.maxTouchPoints; } });
        Object.defineProperty(nav, 'plugins', { get: function(){ return spoof.plugins; } });
        Object.defineProperty(nav, 'mimeTypes', { get: function(){ return spoof.mimeTypes; } });
    } catch(e){}

    try {
        // Timezone spoof etc.
        var realDate = Date;
        Date = function(){
            var d = new realDate();
            return d;
        };
        Date.prototype = realDate.prototype;
        Date.now = function(){ return realDate.now(); };
        if (Date.prototype.toLocaleString) {
            var orig = Date.prototype.toLocaleString;
            Date.prototype.toLocaleString = function(locale, opts){
                opts = opts || {};
                if (!opts.timeZone) opts.timeZone = payload.timezone;
                return orig.call(this, locale, opts);
            };
        }
    } catch(e){}

    try {
        // Disable WebRTC/Audio/Canvas/WebGL
        window.RTCPeerConnection = function(){ throw new Error('disabled'); };
        window.webkitRTCPeerConnection = window.RTCPeerConnection;
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
            navigator.mediaDevices.getUserMedia = function(){ return Promise.reject(new Error('disabled')); };
    } catch(e){}

    try {
        var origGet = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type){
            if (String(type).toLowerCase().indexOf('webgl') !== -1) 
                return null;
            return origGet.apply(this, arguments);
        };
        HTMLCanvasElement.prototype.toDataURL = function(){ return ''; };
        HTMLCanvasElement.prototype.toBlob = function(){ return null; };
    } catch(e){}
})();
"""

def run_subproc(cmd_list, shell=False):
    """Run a subprocess, return (success, stdout+stderr)"""
    try:
        res = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, timeout=15)
        return (res.returncode == 0, res.stdout.decode(errors='ignore'))
    except Exception as e:
        return (False, str(e))

def windows_flush_dns():
    """Flush DNS cache on Windows; requires admin."""
    # ipconfig /flushdns
    ok1, out1 = run_subproc(["ipconfig", "/flushdns"], shell=False)
    # PowerShell Clear-DnsClientCache if available
    ok2, out2 = run_subproc(["powershell", "-Command", "Clear-DnsClientCache"], shell=False)
    return ok1 or ok2

def windows_clear_temp(prefetch=True):
    """Delete temp folders in Windows."""
    paths = []
    try:
        system_temp = os.environ.get("SystemRoot", r"C:\Windows") + r"\Temp"
        paths.append(system_temp)
    except Exception:
        pass
    try:
        user_temp = os.environ.get("TEMP") or os.environ.get("TMP")
        if user_temp:
            paths.append(user_temp)
    except Exception:
        pass
    if prefetch:
        paths.append(r"C:\Windows\Prefetch")
    for p in paths:
        try:
            # Delete all files in the dir, then subdirs
            for root, dirs, files in os.walk(p):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        os.remove(fp)
                    except Exception:
                        pass
                for d in dirs:
                    dp = os.path.join(root, d)
                    try:
                        shutil.rmtree(dp, ignore_errors=True)
                    except Exception:
                        pass
        except Exception:
            pass

def deep_windows_cleanup():
    """Flush DNS + clear temp + prefetch directories."""
    windows_flush_dns()
    windows_clear_temp(prefetch=True)

def random_viewport():
    sizes = [
        (1366, 768), (1440, 900), (1536, 864),
        (1600, 900), (1680, 1050), (1920, 1080),
        (2560, 1440)
    ]
    return random.choice(sizes)

def find_local_tor_bin():
    p = Path(".")
    candidates = ["tor.exe", "tor"]
    for c in candidates:
        if (p / c).exists() and os.access(p / c, os.X_OK):
            return str((p / c).resolve())
    return None

# HARDEN_JS_TEMPLATE, etc. (same as above) …

class ParanoidTorBrowserWindowsCleanup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ParanoidTorBrowserWinCleanup")
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(6,6,6,6)

        # Layout similar: controls left, proxy/tor/panic right
        top_row = QHBoxLayout()
        left_group = QHBoxLayout()
        self.back_btn = QToolButton(); self.back_btn.setText("◀")
        self.forward_btn = QToolButton(); self.forward_btn.setText("▶")
        self.reload_btn = QToolButton(); self.reload_btn.setText("⟳")
        self.urlbar = QLineEdit(); self.urlbar.setPlaceholderText("Enter URL or search and press Enter")
        self.go_btn = QPushButton("Go")
        left_group.addWidget(self.back_btn)
        left_group.addWidget(self.forward_btn)
        left_group.addWidget(self.reload_btn)
        left_group.addWidget(self.urlbar, stretch=1)
        left_group.addWidget(self.go_btn)

        right_group = QHBoxLayout()
        self.proxy_checkbox = QCheckBox("Use Tor proxy (127.0.0.1:9050)")
        self.tor_toggle_btn = QPushButton("Start Tor")
        self.panic_btn = QPushButton("PANIC (wipe / cleanup)")
        right_group.addWidget(self.proxy_checkbox)
        right_group.addWidget(self.tor_toggle_btn)
        right_group.addWidget(self.panic_btn)

        options_group = QHBoxLayout()
        self.js_checkbox = QCheckBox("JS")
        self.js_checkbox.setChecked(True)
        self.paranoid_clean_checkbox = QCheckBox("Paranoid clean")
        self.paranoid_clean_checkbox.setChecked(False)
        self.ua_combo = QComboBox()
        self.ua_combo.addItems(["Random UA", "Custom UA..."])
        options_group.addWidget(self.js_checkbox)
        options_group.addWidget(self.paranoid_clean_checkbox)
        options_group.addWidget(QLabel("UA:"))
        options_group.addWidget(self.ua_combo)

        self.layout().addLayout(top_row)
        self.layout().addLayout(options_group)

        self.view_container = QVBoxLayout()
        self.layout().addLayout(self.view_container, stretch=1)

        self.current_view = None
        self.current_tmpdir = None
        self.current_profile = None
        self.tor_process = None
        self.tor_bin = find_local_tor_bin()

        self.back_btn.clicked.connect(self.go_back)
        self.forward_btn.clicked.connect(self.go_forward)
        self.reload_btn.clicked.connect(self.reload)
        self.go_btn.clicked.connect(self.on_go)
        self.urlbar.returnPressed.connect(self.on_go)
        self.tor_toggle_btn.clicked.connect(self.toggle_tor)
        self.panic_btn.clicked.connect(self.panic)

        self.resize(1100, 800)

    def toggle_tor(self):
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=4)
            except Exception:
                try:
                    self.tor_process.kill()
                except:
                    pass
            self.tor_process = None
            self.tor_toggle_btn.setText("Start Tor")
        else:
            if not self.tor_bin:
                self.tor_toggle_btn.setText("No tor.exe found")
                QTimer.singleShot(3000, lambda: self.tor_toggle_btn.setText("Start Tor"))
                return
            tor_data = tempfile.mkdtemp(prefix="tor_data_")
            tor_cmd = [self.tor_bin, "--SocksPort", "9050", "--DataDirectory", tor_data, "--Log", "notice stdout"]
            try:
                self.tor_process = subprocess.Popen(tor_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.tor_toggle_btn.setText("Stop Tor")
            except Exception:
                self.tor_toggle_btn.setText("Failed Start")
                QTimer.singleShot(3000, lambda: self.tor_toggle_btn.setText("Start Tor"))
                self.tor_process = None
                shutil.rmtree(tor_data, ignore_errors=True)

    def create_profile(self, ua_override=None):
        tmpdir = tempfile.mkdtemp(prefix="ppb_profile_")
        name = str(uuid.uuid4())
        from qtpy.QtWebEngineWidgets import QWebEngineProfile
        profile = QWebEngineProfile(name, self)
        profile.setPersistentStoragePath(tmpdir)
        profile.setCachePath(tmpdir)
        try:
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            profile.setHttpCacheType(QWebEngineProfile.NoCache)
            if hasattr(profile, "setOffTheRecord"):
                profile.setOffTheRecord(True)
        except:
            pass
        ua = ua_override or random.choice(USER_AGENTS)
        try:
            profile.setHttpUserAgent(ua)
        except:
            pass
        return profile, tmpdir, ua

    def on_go(self):
        text = self.urlbar.text().strip()
        if not text:
            return
        if " " in text or not text.startswith(("http://", "https://")):
            import urllib.parse
            q = urllib.parse.quote_plus(text)
            url = f"https://duckduckgo.com/?q={q}"
        else:
            url = text

        ua_custom = None
        if self.ua_combo.currentText() == "Custom UA...":
            from qtpy.QtWidgets import QInputDialog
            ua_custom, ok = QInputDialog.getText(self, "Custom UA", "Enter custom User-Agent string:")
            if not ok or not ua_custom:
                ua_custom = None

        use_proxy = self.proxy_checkbox.isChecked()

        profile, tmpdir, ua = self.create_profile(ua_override=ua_custom)
        page = QWebEnginePage(profile, self)
        view = QWebEngineView()
        view.setPage(page)

        page.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, self.js_checkbox.isChecked())
        page.settings().setAttribute(QWebEngineSettings.PluginsEnabled, False)
        page.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        page.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, False)
        page.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)

        w, h = random_viewport()
        self.resize(w, h + 160)

        payload = {
            "navigator": {
                "userAgent": ua,
                "platform": random.choice(["Win32","Linux x86_64","MacIntel"]),
                "language": random.choice(["en-US","en-GB","en"]),
                "languages": [random.choice(["en-US","en"]), "en"],
                "hardwareConcurrency": random.choice([2,4,8]),
                "maxTouchPoints": random.choice([0,0,0,1]),
                "plugins": [], "mimeTypes": []
            },
            "fonts": random.choice(SPOOF_FONTS),
            "timezone": random.choice(["UTC","Europe/London","America/New_York","Asia/Tokyo"])
        }

        harden_js = HARDEN_JS_TEMPLATE % (OLED_BLACK_CSS.replace("\n"," "), json.dumps(payload))

        def inject():
            try:
                if self.js_checkbox.isChecked():
                    page.runJavaScript(harden_js)
                else:
                    page.runJavaScript("(function(){ try { var css=`%s`; var s=document.createElement('style'); s.appendChild(document.createTextNode(css)); (document.head||document.documentElement).appendChild(s);}catch(e){} })();" % OLED_BLACK_CSS.replace("\n"," "))
            except:
                pass

        page.loadFinished.connect(lambda ok: inject())

        self._swap_view(view, tmpdir)

        if use_proxy:
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "") + " --proxy-server=socks5://127.0.0.1:9050"

        view.load(QUrl(url))

        if self.paranoid_clean_checkbox.isChecked():
            # run Windows deep cleanup
            deep_windows_cleanup()
            time.sleep(random.uniform(0.1, 0.4))

    def _swap_view(self, new_view, new_tmpdir):
        if self.current_view:
            old = self.current_view
            old_tmp = self.current_tmpdir
            old.setParent(None)
            old.deleteLater()
            if old_tmp:
                try:
                    shutil.rmtree(old_tmp, ignore_errors=True)
                except:
                    pass
            self.current_view = None
            self.current_tmpdir = None

        self.view_container.addWidget(new_view)
        self.current_view = new_view
        self.current_tmpdir = new_tmpdir

    def go_back(self):
        if self.current_view:
            self.current_view.back()

    def go_forward(self):
        if self.current_view:
            self.current_view.forward()

    def reload(self):
        if self.current_view:
            self.current_view.reload()

    def panic(self):
        # same as before + deep cleanup
        if self.tor_process:
            try:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=3)
            except:
                try:
                    self.tor_process.kill()
                except:
                    pass
            self.tor_process = None
            self.tor_toggle_btn.setText("Start Tor")

        if self.current_view:
            try:
                self.current_view.setParent(None)
                self.current_view.deleteLater()
            except:
                pass
            if self.current_tmpdir:
                try:
                    shutil.rmtree(self.current_tmpdir, ignore_errors=True)
                except:
                    pass
            self.current_view = None
            self.current_tmpdir = None

        # application-level temp cleaning
        deep_windows_cleanup()

        # also wipe any profile and tor_data directories in temp
        tmp = Path(tempfile.gettempdir())
        for item in tmp.iterdir():
            try:
                if item.name.startswith("ppb_profile_") or item.name.startswith("tor_data_"):
                    if item.is_dir():
                        shutil.rmtree(str(item), ignore_errors=True)
            except:
                pass

    def closeEvent(self, ev):
        try:
            self.panic()
        except:
            pass
        super().closeEvent(ev)

def main():
    try:
        from qtpy.QtCore import Qt
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    except:
        pass
    app = QApplication(sys.argv)
    w = ParanoidTorBrowserWindowsCleanup()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
