#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RemoteControlGUI.py

شرح (فارسی):
این برنامه یک رابط گرافیکی «کلید خیلی خفن» برای روشن/خاموش کردن یک دستگاه از طریق
درخواست‌های HTTP می‌سازد. برنامه:
 - وضعیت اولیه را از state2.txt می‌خواند (1 => فعال، 0 => غیرفعال)
 - یک دکمه‌ی بزرگ و زیبا برای روشن/خاموش دارد
 - وقتی دکمه را می‌زنیم، یک درخواست به remote_control.php?action=on|off ارسال می‌شود
 - وضعیت را پس از ارسال درخواست بررسی و UI را به‌روز می‌کند
 - امکان رفرش دستی و رفرش خودکار (Timer) وجود دارد

نیازمندی‌ها:
    pip install PyQt5 requests

نحوه اجرا:
    python RemoteControlGUI.py

تذکر امنیتی:
    این برنامه فقط یک کلاینت HTTP ساده است. مراقب باشید URLها و شبکه‌ای که
    به آن متصل می‌شوید امن باشد.

"""

import sys
import requests
import traceback
from datetime import datetime

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QStatusBar,
)

# ------------------------ تنظیمات URL ------------------------
CONTROL_BASE_URL = "https://x9t3m7q2b1.apiot.ir/remote_control.php"
STATE_URL = "https://x9t3m7q2b1.apiot.ir/state2.txt"
# -------------------------------------------------------------


class NetworkWorker(QThread):
    """یک Worker ساده برای انجام درخواست‌های HTTP در ترد جداگانه
    سیگنال finished: (success: bool, payload: str, op: str)
    op می‌تواند 'fetch_state' یا 'send_action' باشد
    """

    finished = pyqtSignal(bool, str, str)

    def __init__(self, op: str, url: str, action: str = None, timeout: int = 8):
        super().__init__()
        self.op = op
        self.url = url
        self.action = action
        self.timeout = timeout

    def run(self):
        try:
            if self.op == "fetch_state":
                r = requests.get(self.url, timeout=self.timeout)
                r.raise_for_status()
                payload = r.text
                self.finished.emit(True, payload, self.op)

            elif self.op == "send_action":
                # می‌سازیم: remote_control.php?action=on یا off
                if not self.action:
                    raise ValueError("action is required for send_action")
                full = f"{self.url}?action={self.action}"
                r = requests.get(full, timeout=self.timeout)
                r.raise_for_status()
                payload = r.text
                self.finished.emit(True, payload, self.op)

            else:
                self.finished.emit(False, f"Unknown op: {self.op}", self.op)

        except Exception as e:
            tb = traceback.format_exc()
            self.finished.emit(False, f"{e}\n{tb}", self.op)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("کلید خفن - کنترل از راه دور")
        self.setMinimumSize(420, 300)

        # state: None = unknown, 0 = off, 1 = on
        self.current_state = None

        self._build_ui()

        # تایمر رفرش خودکار
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.fetch_state)

        # وضعیت اولیه را بگیریم
        self.fetch_state()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("کلید بسیار پیشرفته")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Sans Serif", 18, QFont.Bold))
        layout.addWidget(title)

        self.state_label = QLabel("وضعیت: در حال بارگزاری...")
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setFont(QFont("Sans Serif", 14))
        layout.addWidget(self.state_label)

        # دکمه بزرگ کلید
        self.toggle_btn = QPushButton("بارگذاری...")
        self.toggle_btn.setFixedSize(300, 120)
        self.toggle_btn.setFont(QFont("Sans Serif", 18, QFont.Bold))
        self.toggle_btn.clicked.connect(self.on_toggle_clicked)
        self._apply_off_style()  # استایل اولیه
        layout.addWidget(self.toggle_btn, alignment=Qt.AlignCenter)

        # ردیف کنترل‌ها
        controls = QHBoxLayout()
        self.refresh_btn = QPushButton("رفرش")
        self.refresh_btn.clicked.connect(self.fetch_state)
        controls.addWidget(self.refresh_btn)

        self.auto_checkbox = QCheckBox("رفرش خودکار (هر 5 ثانیه)")
        self.auto_checkbox.stateChanged.connect(self.on_auto_changed)
        controls.addWidget(self.auto_checkbox)

        layout.addLayout(controls)

        self.last_update_label = QLabel("آخرین به‌روزرسانی: -")
        self.last_update_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.last_update_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # نوار وضعیت
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    # ---------- استایل‌های دکمه ----------
    def _apply_on_style(self):
        self.toggle_btn.setText("روشن است — لمس برای خاموش")
        self.toggle_btn.setStyleSheet(
            """
            QPushButton {
                color: white;
                border-radius: 18px;
                padding: 8px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4caf50, stop:1 #2e7d32);
            }
            QPushButton:pressed { transform: translateY(1px); }
            QPushButton:disabled { background: #999999; color: #dddddd; }
            """
        )

    def _apply_off_style(self):
        self.toggle_btn.setText("خاموش است — لمس برای روشن")
        self.toggle_btn.setStyleSheet(
            """
            QPushButton {
                color: white;
                border-radius: 18px;
                padding: 8px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9e9e9e, stop:1 #616161);
            }
            QPushButton:pressed { transform: translateY(1px); }
            QPushButton:disabled { background: #999999; color: #dddddd; }
            """
        )

    # ---------- عملیات شبکه ----------
    def fetch_state(self):
        self.status.showMessage("در حال دریافت وضعیت...", 5000)
        self.refresh_btn.setEnabled(False)
        self.toggle_btn.setEnabled(False)
        worker = NetworkWorker("fetch_state", STATE_URL)
        worker.finished.connect(self.on_network_finished)
        worker.start()

    def send_action(self, action: str):
        self.status.showMessage(f"ارسال دستور: {action} ...")
        self.toggle_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        worker = NetworkWorker("send_action", CONTROL_BASE_URL, action=action)
        worker.finished.connect(self.on_network_finished)
        worker.start()

    def on_network_finished(self, success: bool, payload: str, op: str):
        # توجه: این تابع از ترد جداگانه صدا زده می‌شود ولی خود سیگنال به نخ اصلی می‌آید
        if op == "fetch_state":
            self.refresh_btn.setEnabled(True)
            if success:
                text = payload.strip()
                # ممکن است فایل وضعیت خط جدید داشته باشد یا محتوای غیرمنتظره
                if len(text) > 0 and text[0] in ("0", "1"):
                    val = text[0]
                    if val == "1":
                        self.current_state = 1
                        self.state_label.setText("وضعیت: فعال (1)")
                        self._apply_on_style()
                    else:
                        self.current_state = 0
                        self.state_label.setText("وضعیت: غیرفعال (0)")
                        self._apply_off_style()
                    self.status.showMessage("وضعیت به‌روز شد", 3000)
                else:
                    self.current_state = None
                    self.state_label.setText(f"وضعیت: پاسخ نامعتبر: '{text}'")
                    self.status.showMessage("پاسخ وضعیت نامعتبر بود", 6000)

            else:
                self.state_label.setText("وضعیت: خطا در دریافت")
                self.status.showMessage(f"خطا در دریافت وضعیت: {payload}", 8000)

            self.last_update_label.setText("آخرین به‌روزرسانی: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            # دکمه فقط وقتی وضعیت مشخص است فعال می‌شود
            self.toggle_btn.setEnabled(self.current_state is not None)

        elif op == "send_action":
            # payload ممکن است پیغام ساده‌ای باشد؛ بعد از ارسال، وضعیت را مجدداً بخوانید
            if success:
                self.status.showMessage("دستور ارسال شد، در حال بررسی وضعیت...", 4000)
                # پس از ارسال، سریع وضعیت را بررسی می‌کنیم تا UI همگام شود
                # کمی تاخیر نمی‌گذاریم؛ کافیست fetch_state را صدا بزنیم
                self.fetch_state()
            else:
                self.status.showMessage(f"خطا در ارسال دستور: {payload}", 8000)
                # اگر ارسال ناموفق بود، دکمه را مجدداً فعال می‌کنیم
                self.toggle_btn.setEnabled(True)
                self.refresh_btn.setEnabled(True)

    # ---------- رویداد کلیک روی دکمه ----------
    def on_toggle_clicked(self):
        # بدون اطلاع از وضعیت، کاری نمی‌کنیم
        if self.current_state is None:
            self.status.showMessage("وضعیت نامشخص است؛ ابتدا رفرش کنید.")
            return

        # اگر الان روشن است، می‌خواهیم خاموش کنیم
        if self.current_state == 1:
            self.send_action("off")
        else:
            self.send_action("on")

    # ---------- رفرش خودکار ----------
    def on_auto_changed(self, state):
        if state == Qt.Checked:
            self.auto_timer.start(5000)  # هر 5 ثانیه
            self.status.showMessage("رفرش خودکار فعال شد")
        else:
            self.auto_timer.stop()
            self.status.showMessage("رفرش خودکار غیرفعال شد")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
