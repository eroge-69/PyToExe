# Required packages:
# pip install PyQt5 PyQtWebEngine adblockparser requests python-whois openai

import sys
import os
import json
import csv
import requests
import whois
import socket
from datetime import datetime
from openai import OpenAI
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QMenu,
    QAction, QLineEdit, QStatusBar, QDialog,
    QFormLayout, QDialogButtonBox, QCheckBox,
    QVBoxLayout, QDockWidget, QWidget,
    QPushButton, QTextEdit, QHBoxLayout, QListWidget,
    QListWidgetItem, QFileDialog, QTabWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from adblockparser import AdblockRules

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY',''))

# File paths
FILTER_LIST_URL = "https://easylist.to/easylist/easylist.txt"
BOOKMARKS_FILE = os.path.expanduser('~/.pyadblock_bookmarks.json')
HISTORY_FILE = os.path.expanduser('~/.pyadblock_history.json')
CREDENTIALS_FILE = os.path.expanduser('~/.pyadblock_credentials.json')

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, rules, send_dnt=False):
        super().__init__()
        self.rules = rules
        self.send_dnt = send_dnt
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if self.rules.should_block(url):
            info.block(True)
        elif self.send_dnt:
            info.setHttpHeader(b"DNT", b"1")

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.home_edit = QLineEdit()
        self.bg_edit = QLineEdit()
        form.addRow("Homepage URL:", self.home_edit)
        form.addRow("Background Image/GIF URL:", self.bg_edit)
        self.dnt_check = QCheckBox("Send 'Do Not Track' header")
        self.cookie_check = QCheckBox("Disable third-party cookies")
        self.clear_check = QCheckBox("Clear cookies and cache on exit")
        form.addRow(self.dnt_check)
        form.addRow(self.cookie_check)
        form.addRow(self.clear_check)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self):
        return {
            'homepage': self.home_edit.text().strip(),
            'background': self.bg_edit.text().strip(),
            'dnt': self.dnt_check.isChecked(),
            'disable_third_party': self.cookie_check.isChecked(),
            'clear_on_exit': self.clear_check.isChecked(),
        }

class OSINTDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("OSINT Tools", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        for name in ("WHOIS Lookup", "IP Geolocation", "DNS Lookup", "Page Metadata"):
            btn = QPushButton(name)
            btn.clicked.connect(self.handle_tool)
            btn.setStyleSheet("font-size:14px;")
            layout.addWidget(btn)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color:#444;color:#fff;font-size:14px;")
        layout.addWidget(self.output)
        self.setWidget(widget)
        widget.setLayout(layout)

    def handle_tool(self):
        sender = self.sender()
        domain = self.parent().url_bar.text().strip()
        if not domain:
            self.output.setText("Enter a URL/domain.")
            return
        if domain.startswith(('http://','https://')):
            domain = domain.split('://')[1].split('/')[0]
        try:
            if sender.text()=="WHOIS Lookup":
                self.output.setText(str(whois.whois(domain)))
            elif sender.text()=="IP Geolocation":
                ip = socket.gethostbyname(domain)
                data = requests.get(f"https://ipinfo.io/{ip}/json").json()
                self.output.setText(json.dumps(data, indent=2))
            elif sender.text()=="DNS Lookup":
                ips = sorted({r[4][0] for r in socket.getaddrinfo(domain, None)})
                self.output.setText("\n".join(ips))
            elif sender.text()=="Page Metadata":
                r = requests.get('http://' + domain)
                m = {'status_code':r.status_code, 'headers':dict(r.headers)}
                self.output.setText(json.dumps(m, indent=2))
        except Exception as e:
            self.output.setText(f"Error: {e}")

class AIDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("AI Assistant", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("background-color:#444;color:#fff;font-size:14px;")
        layout.addWidget(self.chat)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask me...")
        self.input.setStyleSheet("font-size:14px;")
        send = QPushButton("Send")
        send.clicked.connect(self.send_query)
        send.setStyleSheet("font-size:14px;")
        box = QHBoxLayout()
        box.addWidget(self.input)
        box.addWidget(send)
        layout.addLayout(box)
        self.setWidget(widget)
        widget.setLayout(layout)

    def send_query(self):
        prompt = self.input.text().strip()
        if not prompt: return
        self.chat.append(f"You: {prompt}")
        self.input.clear()
        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role":"system","content":"You are a helpful assistant."},
                    {"role":"user","content":prompt}
                ]
            )
            text = resp.choices[0].message.content
            self.chat.append(f"AI: {text}\n")
        except Exception as e:
            self.chat.append(f"Error: {e}\n")

class BookmarkDock(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Bookmarks", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        widget=QWidget(); layout=QVBoxLayout(widget)
        self.list=QListWidget()
        self.list.setStyleSheet("font-size:14px;")
        self.list.itemClicked.connect(self.navigate)
        layout.addWidget(self.list)
        add=QPushButton("Add Bookmark")
        add.clicked.connect(self.add_bookmark)
        add.setStyleSheet("font-size:14px;")
        layout.addWidget(add)
        self.setWidget(widget)
        widget.setLayout(layout)
        self.load_bookmarks()

    def load_bookmarks(self):
        try: data=json.load(open(BOOKMARKS_FILE))
        except: data=[]
        self.list.clear()
        for b in data:
            item=QListWidgetItem(b['title'])
            item.setData(Qt.UserRole,b['url'])
            self.list.addItem(item)

    def add_bookmark(self):
        url=self.parent().url_bar.text().strip()
        if not url: return
        try: data=json.load(open(BOOKMARKS_FILE))
        except: data=[]
        data.append({'title':url,'url':url})
        with open(BOOKMARKS_FILE,'w') as f: json.dump(data,f)
        self.load_bookmarks()

    def navigate(self,item):
        self.parent().current_view().load(QUrl(item.data(Qt.UserRole)))

class HistoryDock(QDockWidget):
    def __init__(self,parent=None):
        super().__init__("History",parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        widget=QWidget(); layout=QVBoxLayout(widget)
        self.list=QListWidget(); self.list.setStyleSheet("font-size:14px;")
        self.list.itemClicked.connect(self.navigate)
        clear=QPushButton("Clear History"); clear.clicked.connect(self.clear_history)
        layout.addWidget(self.list); layout.addWidget(clear)
        self.setWidget(widget); widget.setLayout(layout)
        self.load_history()

    def load_history(self):
        try:
            data = json.load(open(HISTORY_FILE))
        except:
            data = []
        self.list.clear()
        for e in reversed(data):
            ts = e.get('timestamp') or e.get('time','')
            url = e.get('url','')
            display = f"{ts} - {url}" if ts else url
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, url)
            self.list.addItem(item)

    def navigate(self, item):
        """Navigate to selected history entry"""
        url = item.data(Qt.UserRole)
        self.parent().current_view().load(QUrl(url))

    def clear_history(self):
        with open(HISTORY_FILE,'w') as f:
            json.dump([], f)
        self.load_history()

class CredentialsDock(QDockWidget):
    def __init__(self,parent=None):
        super().__init__("Credentials",parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        widget=QWidget(); layout=QVBoxLayout(widget)
        imp=QPushButton("Import CSV")
        imp.clicked.connect(self.import_csv); imp.setStyleSheet("font-size:14px;")
        self.list=QListWidget(); self.list.setStyleSheet("font-size:14px;")
        self.list.itemClicked.connect(self.show_details)
        self.details=QTextEdit(); self.details.setReadOnly(True)
        self.details.setStyleSheet("background:#444;color:#fff;font-size:14px;")
        layout.addWidget(imp); layout.addWidget(self.list); layout.addWidget(self.details)
        self.setWidget(widget); widget.setLayout(layout)
        self.creds=[]

    def import_csv(self):
        path,_=QFileDialog.getOpenFileName(self,"Open CSV","","CSV Files (*.csv)")
        if not path: return
        with open(path) as f:
            reader=csv.DictReader(f)
            self.creds=[row for row in reader]
        self.list.clear()
        for c in self.creds:
            item=QListWidgetItem(f"{c.get('website')} - {c.get('username')}")
            item.setData(Qt.UserRole,c)
            self.list.addItem(item)

    def show_details(self,item):
        c=item.data(Qt.UserRole)
        self.details.setText(json.dumps(c,indent=2))

class DiscordDock(QDockWidget):
    def __init__(self,parent=None):
        super().__init__("Discord",parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        widget=QWidget(); layout=QVBoxLayout(widget)
        self.token=QLineEdit(); self.token.setEchoMode(QLineEdit.Password)
        self.token.setPlaceholderText("Discord token")
        login=QPushButton("Login"); login.clicked.connect(self.login); login.setStyleSheet("font-size:14px;")
        self.info=QTextEdit(); self.info.setReadOnly(True)
        self.info.setStyleSheet("background:#444;color:#fff;font-size:14px;")
        layout.addWidget(self.token); layout.addWidget(login); layout.addWidget(self.info)
        self.setWidget(widget); widget.setLayout(layout)

    def login(self):
        token=self.token.text().strip()
        if not token: return
        r=requests.get('https://discord.com/api/v9/users/@me',headers={'Authorization':token})
        if r.status_code==200:
            u=r.json(); self.info.setText(f"Logged in as {u['username']}#{u['discriminator']}")
        else:
            self.info.setText(f"Login failed: {r.status_code}")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ricks fun browser")
        self.resize(1600,900)
        self.settings=QApplication.instance().settings
        
        # Tabs
        self.tabs=QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        # Shared profile
        profile=QWebEngineProfile.defaultProfile()
        if self.settings['disable_third_party']: profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setUrlRequestInterceptor(AdBlockInterceptor(self.load_rules(),send_dnt=self.settings['dnt']))
        
        # Toolbar
        nav=QToolBar()
        nav.setMovable(False)
        nav.setStyleSheet("QToolBar{background:#000; border-bottom:2px solid #f00;}"
                        "QToolBar QLineEdit{font-size:14px;padding:6px;background:#111;color:#fff;}"
                        "QToolBar QPushButton,QToolBar QToolButton{font-size:16px;color:#fff;}")
        self.addToolBar(nav)
        # New Tab
        nav.addAction(QAction("+",self,triggered=self.add_tab))
        # Back/Forward
        nav.addAction(QAction("⟨",self,triggered=self.go_back))
        nav.addAction(QAction("⟩",self,triggered=self.go_forward))
        # URL bar
        self.url_bar=QLineEdit(); self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav.addWidget(self.url_bar)
        # Home/Settings
        nav.addAction(QAction("🏠",self,triggered=self.go_home))
        nav.addAction(QAction(QIcon.fromTheme("preferences-system"),"Settings",self,triggered=self.open_settings))
        
        # Docks
        self.osint=OSINTDock(self)
        self.ai=AIDock(self)
        self.bookmarks=BookmarkDock(self)
        self.history=HistoryDock(self)
        self.creds=CredentialsDock(self)
        self.discord=DiscordDock(self)
        for dock,area in [(self.osint,Qt.RightDockWidgetArea),(self.ai,Qt.LeftDockWidgetArea),
                          (self.bookmarks,Qt.LeftDockWidgetArea),(self.history,Qt.RightDockWidgetArea),
                          (self.creds,Qt.LeftDockWidgetArea),(self.discord,Qt.LeftDockWidgetArea)]:
            self.addDockWidget(area,dock)
        
        # View menu
        vm=self.menuBar().addMenu("View")
        for name,d in [("OSINT Tools",self.osint),("AI Assistant",self.ai),("Bookmarks",self.bookmarks),
                       ("History",self.history),("Credentials",self.creds),("Discord",self.discord)]:
            act=QAction(name,self,checkable=True,checked=True)
            act.triggered.connect(lambda chk,d=d: d.setVisible(chk))
            vm.addAction(act)
        
        # First tab
        self.add_tab()
        self.apply_styles()

    def add_tab(self):
        view=QWebEngineView()
        view.urlChanged.connect(self.update_urlbar)
        self.tabs.addTab(view,"New Tab")
        self.tabs.setCurrentWidget(view)
        self.go_home()

    def close_tab(self,index):
        if self.tabs.count()>1:
            self.tabs.removeTab(index)

    def current_view(self):
        return self.tabs.currentWidget()

    def navigate_to_url(self):
        text=self.url_bar.text().strip()
        if ' ' in text or '.' not in text:
            url=f"https://www.google.com/search?q={requests.utils.quote(text)}"
        else:
            url=text if text.startswith(('http://','https://')) else 'http://'+text
        self.current_view().load(QUrl(url))

    def update_urlbar(self,qurl):
        url=qurl.toString()
        self.url_bar.setText(url)
        self.log_history(url)

    def go_back(self): self.current_view().back()
    def go_forward(self): self.current_view().forward()

    def go_home(self):
        home=self.settings.get('homepage') or 'about:blank'; bg=self.settings.get('background')
        if home=='about:blank':
            html=f"""
<html><body style='margin:0;padding:20px;background:{f"url('{bg}')" if bg else '#000'};'>
<h1 style='color:#fff;font-size:24px'>Welcome to Ricks fun browser</h1>
<p style='color:#fff;'>Use the address bar or tabs.</p></body></html>"""
            self.current_view().setHtml(html)
        else:
            self.current_view().load(QUrl(home))

    def open_settings(self):
        dlg=SettingsDialog(self)
        dlg.home_edit.setText(self.settings.get('homepage','about:blank'))
        dlg.bg_edit.setText(self.settings.get('background',''))
        dlg.dnt_check.setChecked(self.settings.get('dnt',False))
        dlg.cookie_check.setChecked(self.settings.get('disable_third_party',False))
        dlg.clear_check.setChecked(self.settings.get('clear_on_exit',False))
        if dlg.exec_()==QDialog.Accepted:
            self.settings.update(dlg.get_values())
            self.statusBar().showMessage('Settings saved; restart to apply.',5000)

    def load_rules(self):
        r=requests.get(FILTER_LIST_URL); lines=[ln for ln in r.text.splitlines() if ln and not ln.startswith(('!','['))]; return AdblockRules(lines)
    def apply_styles(self): self.setStyleSheet("QMainWindow{background:#000;}QStatusBar{background:#111;color:#fff;}")
    def clear_data(self):
        p=QWebEngineProfile.defaultProfile(); p.clearHttpCache(); p.cookieStore().deleteAllCookies()
    def log_history(self,url):
        entry={'url':url,'timestamp':datetime.now().isoformat()}
        try: hist=json.load(open(HISTORY_FILE))
        except: hist=[]
        hist.append(entry); json.dump(hist,open(HISTORY_FILE,'w'))

if __name__=='__main__':
    app=QApplication(sys.argv)
    app.settings={'homepage':'about:blank','background':'','dnt':True,'disable_third_party':True,'clear_on_exit':False}
    win=Browser(); win.show(); sys.exit(app.exec_())
