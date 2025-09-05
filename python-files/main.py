#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SubTransPlayer — Simple video player with hover translation on subtitles.
- Plays videos via VLC engine (python-vlc)
- Loads .srt subtitles and shows the active line
- Hover or click on any word to see Google Translate meaning (auto EN↔FA)
- NEW: Bookmarks panel to save vocabulary with context, export CSV
Author: ChatGPT
License: MIT
"""
import os
import sys
import re
import json
import time
import requests
import srt
import vlc

from datetime import timedelta, datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint, QStandardPaths, QDateTime
from PySide6.QtGui import QCursor, QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QSlider, QComboBox, QTextBrowser, QToolTip,
    QDockWidget, QListWidget, QListWidgetItem, QLineEdit, QMessageBox, QMenu
)

APP_NAME = "SubTransPlayer"
VERSION = "0.2.0"

def get_api_key():
    key = os.environ.get("GOOGLE_TRANSLATE_API_KEY")
    if key:
        return key.strip()
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            key = data.get("GOOGLE_TRANSLATE_API_KEY")
            if key:
                return key.strip()
        except Exception:
            pass
    return None

def is_farsi_text(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))

def tokenize_to_anchors(text: str) -> str:
    tokens = re.findall(r'[\w\u0600-\u06FF]+|[^\w\s]', text, flags=re.UNICODE)
    out = []
    for tok in tokens:
        if re.match(r'[\w\u0600-\u06FF]+$', tok):
            safe = tok.replace('"', '&quot;')
            out.append(f'<a href="{safe}">{tok}</a>')
        else:
            out.append(tok)
    return ''.join(out).replace('\n', '<br>')

def google_translate(text: str, target_lang: str, api_key: str, source_lang: str = None) -> str:
    url = "https://translation.googleapis.com/language/translate/v2"
    params = {"key": api_key}
    data = {"q": text, "target": target_lang}
    if source_lang:
        data["source"] = source_lang
    try:
        r = requests.post(url, params=params, data=data, timeout=6)
        r.raise_for_status()
        res = r.json()
        return res["data"]["translations"][0]["translatedText"]
    except Exception as e:
        return f"(ترجمه نشد: {e})"

# ----------------- Bookmarks Store -----------------
def app_data_dir() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation) or str(Path.home() / f".{APP_NAME}")
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p

def bookmarks_path() -> Path:
    return app_data_dir() / "bookmarks.json"

def load_bookmarks() -> list:
    p = bookmarks_path()
    if p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_bookmarks(items: list):
    p = bookmarks_path()
    try:
        with open(p, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def export_bookmarks_csv(items: list, out_path: str):
    fieldnames = ["word", "translation", "direction", "video", "timecode", "context", "created_at"]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for it in items:
            writer.writerow({k: it.get(k, "") for k in fieldnames})

class SubtitleIndex:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def find_by_time(self, t_seconds: float):
        n = len(self.items)
        if n == 0:
            return None
        t = timedelta(seconds=max(0.0, t_seconds))
        while self.index > 0 and self.items[self.index].start > t:
            self.index -= 1
        while self.index < n and self.items[self.index].end <= t:
            self.index += 1
        if 0 <= self.index < n:
            cur = self.items[self.index]
            if cur.start <= t < cur.end:
                return cur
        lo, hi = 0, n - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            it = self.items[mid]
            if it.start <= t < it.end:
                self.index = mid
                return it
            if t < it.start:
                hi = mid - 1
            else:
                lo = mid + 1
        return None

class PlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1100, 680)

        # VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # UI
        central = QWidget(self)
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)

        # Video area
        self.video_widget = QWidget(self)
        self.video_widget.setStyleSheet("background-color: black;")
        root.addWidget(self.video_widget, stretch=6)

        # Subtitle view
        self.subtitle_view = QTextBrowser(self)
        self.subtitle_view.setOpenExternalLinks(False)
        self.subtitle_view.setOpenLinks(False)
        self.subtitle_view.setStyleSheet("font-size: 20px; padding: 6px;")
        self.subtitle_view.anchorHovered.connect(self.on_anchor_hovered)
        self.subtitle_view.anchorClicked.connect(self.on_anchor_clicked)
        root.addWidget(self.subtitle_view, stretch=2)

        # Controls
        controls = QHBoxLayout()
        root.addLayout(controls)

        self.btn_open_video = QPushButton("باز کردن ویدیو")
        self.btn_open_sub = QPushButton("بارگذاری زیرنویس (.srt)")
        self.btn_play = QPushButton("▶️/⏸️")
        self.combo_dir = QComboBox()
        self.combo_dir.addItems(["خودکار EN↔FA", "EN → FA", "FA → EN"])
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)

        controls.addWidget(self.btn_open_video)
        controls.addWidget(self.btn_open_sub)
        controls.addWidget(self.btn_play)
        controls.addWidget(QLabel("جهت ترجمه:"))
        controls.addWidget(self.combo_dir)
        controls.addWidget(self.slider, stretch=1)

        # Dock: Bookmarks
        self.bookmarks = load_bookmarks()
        self.dock = QDockWidget("بوکمارک‌ها (Ctrl+B برای افزودن)", self)
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.on_bm_context_menu)
        self.dock.setWidget(self.list_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.refresh_bookmark_list()

        # Actions
        self.act_add_bm = QAction("افزودن به بوکمارک (Ctrl+B)", self)
        self.act_add_bm.setShortcut(QKeySequence("Ctrl+B"))
        self.act_add_bm.triggered.connect(self.add_current_word_bookmark)
        self.addAction(self.act_add_bm)

        self.act_export_bm = QAction("خروجی CSV", self)
        self.act_export_bm.triggered.connect(self.export_bm_csv)
        self.menuBar().addAction(self.act_add_bm)
        self.menuBar().addAction(self.act_export_bm)

        # Wire
        self.btn_open_video.clicked.connect(self.open_video)
        self.btn_open_sub.clicked.connect(self.open_subtitle)
        self.btn_play.clicked.connect(self.toggle_play)
        self.slider.sliderMoved.connect(self.on_slider_moved)

        # Timers
        self.tick = QTimer(self)
        self.tick.setInterval(100)
        self.tick.timeout.connect(self.on_tick)
        self.tick.start()

        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.setInterval(350)
        self.hover_timer.timeout.connect(self._do_hover_translate)

        # State
        self.media = None
        self.duration_ms = 0
        self.sub_index = None
        self.current_sub_id = None
        self.translation_cache = {}
        self.last_hover_word = None
        self.last_translated = None  # (word, translation)
        self.api_key = get_api_key()
        self.current_video_path = None

        # Bind VLC to our widget
        if sys.platform.startswith("win"):
            self.player.set_hwnd(int(self.video_widget.winId()))
        elif sys.platform.startswith("linux"):
            self.player.set_xwindow(int(self.video_widget.winId()))
        elif sys.platform == "darwin":
            self.player.set_nsobject(int(self.video_widget.winId()))

    # ------------- Player controls -------------
    def open_video(self):
        file, _ = QFileDialog.getOpenFileName(self, "انتخاب ویدیو", "", "Video Files (*.mp4 *.mkv *.avi *.mov)")
        if not file:
            return
        self.media = self.instance.media_new(file)
        self.player.set_media(self.media)
        self.current_video_path = file
        self.player.play()
        QTimer.singleShot(500, self.fetch_duration)

    def fetch_duration(self):
        self.duration_ms = self.player.get_length()

    def open_subtitle(self):
        file, _ = QFileDialog.getOpenFileName(self, "انتخاب زیرنویس", "", "SubRip (*.srt)")
        if not file:
            return
        try:
            with open(file, "r", encoding="utf-8-sig") as f:
                subs = list(srt.parse(f.read()))
            self.sub_index = SubtitleIndex(subs)
            self.current_sub_id = None
            self.subtitle_view.setHtml('<i>زیرنویس بارگذاری شد. پخش را شروع کنید…</i>')
        except Exception as e:
            self.subtitle_view.setHtml(f"<b>خطا در خواندن زیرنویس:</b> {e}")

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def on_slider_moved(self, val):
        if self.duration_ms > 0:
            t = int(val * self.duration_ms / 1000)
            self.player.set_time(t)

    def on_tick(self):
        if not self.player:
            return
        if self.duration_ms <= 0:
            self.duration_ms = self.player.get_length()
        cur = self.player.get_time()
        dur = max(self.duration_ms, 1)
        self.slider.blockSignals(True)
        self.slider.setValue(int(1000 * cur / dur))
        self.slider.blockSignals(False)

        if self.sub_index:
            cur_sec = cur / 1000.0
            sub = self.sub_index.find_by_time(cur_sec)
            if sub is None:
                if self.current_sub_id is not None:
                    self.current_sub_id = None
                    self.subtitle_view.setHtml("")
            else:
                if self.current_sub_id != sub.index:
                    self.current_sub_id = sub.index
                    html = tokenize_to_anchors(sub.content)
                    self.subtitle_view.setHtml(html)

    # ------------- Translation logic -------------
    def _resolve_direction(self, word: str):
        mode = self.combo_dir.currentIndex()
        if mode == 1:
            return ("en", "fa")
        if mode == 2:
            return ("fa", "en")
        if is_farsi_text(word):
            return (None, "en")
        else:
            return (None, "fa")

    def on_anchor_hovered(self, href: str):
        if not href:
            return
        self.last_hover_word = href
        self.hover_timer.start()

    def on_anchor_clicked(self, url):
        word = url.toString()
        self.translate_and_tip(word, immediate=True)

    def _do_hover_translate(self):
        if self.last_hover_word:
            self.translate_and_tip(self.last_hover_word, immediate=False)

    def translate_and_tip(self, word: str, immediate: bool = False):
        if not word.strip():
            return
        source, target = self._resolve_direction(word)
        cache_key = f"{source or 'auto'}->{target}:{word}"
        if cache_key in self.translation_cache:
            trans = self.translation_cache[cache_key]
        else:
            if not self.api_key:
                trans = "(کلید Google Translate تنظیم نشده است)"
            else:
                trans = google_translate(word, target, self.api_key, source_lang=source)
            self.translation_cache[cache_key] = trans

        self.last_translated = (word, trans, f"{(source or 'auto')}→{target}")
        msg = f"{word} → {trans}\n(برای ذخیره در بوکمارک: Ctrl+B)"
        QToolTip.showText(QCursor.pos(), msg, self.subtitle_view)

    # ------------- Bookmarks UI -------------
    def refresh_bookmark_list(self):
        self.list_widget.clear()
        for it in self.bookmarks:
            display = f"{it.get('word','')} — {it.get('translation','')}   [{it.get('direction','')}]"
            self.list_widget.addItem(display)

    def add_current_word_bookmark(self):
        if not self.last_translated:
            QMessageBox.information(self, "بوکمارک", "اول روی یک واژه هاور یا کلیک کن تا ترجمه‌اش بیاد، بعد Ctrl+B.")
            return
        word, translation, direction = self.last_translated
        context = ""
        if self.sub_index and self.current_sub_id is not None:
            try:
                context = self.sub_index.items[self.current_sub_id].content.strip().replace("\n", " ")
            except Exception:
                context = ""
        cur_ms = self.player.get_time() or 0
        timecode = self._format_timecode(max(0, cur_ms // 1000))
        item = {
            "word": word,
            "translation": translation,
            "direction": direction,
            "video": self.current_video_path or "",
            "timecode": timecode,
            "context": context,
            "created_at": datetime.now().isoformat(timespec="seconds")
        }
        self.bookmarks.append(item)
        save_bookmarks(self.bookmarks)
        self.refresh_bookmark_list()
        QToolTip.showText(QCursor.pos(), "✅ به بوکمارک‌ها اضافه شد", self.subtitle_view)

    def export_bm_csv(self):
        out, _ = QFileDialog.getSaveFileName(self, "خروجی CSV", "bookmarks.csv", "CSV (*.csv)")
        if not out:
            return
        try:
            export_bookmarks_csv(self.bookmarks, out)
            QMessageBox.information(self, "خروجی CSV", "فایل CSV ذخیره شد.")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"ذخیره‌سازی ناموفق بود:\n{e}")

    def on_bm_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        idx = self.list_widget.row(item)
        m = QMenu(self)
        act_jump = m.addAction("پرش به زمان")
        act_remove = m.addAction("حذف")
        chosen = m.exec(QCursor.pos())
        if chosen == act_remove:
            del self.bookmarks[idx]
            save_bookmarks(self.bookmarks)
            self.refresh_bookmark_list()
        elif chosen == act_jump:
            # seek to bookmark time
            tc = self.bookmarks[idx].get("timecode", "0:00")
            seconds = self._parse_timecode(tc)
            self.player.set_time(int(seconds * 1000))

    @staticmethod
    def _format_timecode(sec: int) -> str:
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

    @staticmethod
    def _parse_timecode(tc: str) -> int:
        parts = tc.split(":")
        try:
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
            if len(parts) == 2:
                m, s = map(int, parts)
                return m * 60 + s
            return int(parts[0])
        except Exception:
            return 0

def main():
    app = QApplication(sys.argv)
    win = PlayerWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
