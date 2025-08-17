
"""
YouTube All‑in‑One Downloader (Advanced+)
- GUI: PyQt5
- Engine: yt_dlp + FFmpeg (audio always merged with video by default)
- Scheduler: APScheduler (Daily/Weekly/Custom times)
- Queue + History, playlists, channels, shorts, lives (replays), proxies, subtitles, segments, audio-only mode.

NOTE: Use responsibly. Download only content you own or have permission to download.
"""

import os
import sys
import json
import re
import threading
from datetime import datetime
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets
from yt_dlp import YoutubeDL
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

APP_NAME = "YouTube All‑in‑One Downloader"
CONFIG_FILE = "config.json"
HISTORY_FILE = "history.json"

# ---------- Utilities ----------

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Failed to save json:", e)

def sanitize_filename(name: str) -> str:
    # Remove characters not allowed in Windows filenames
    return re.sub(r'[\\/:*?"<>|]+', "_", name)

# ---------- Worker Thread ----------

class DownloadWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(str)        # text log
    finished_item = QtCore.pyqtSignal(int, str, bool)  # row, filepath, success

    def __init__(self, queue_item, options, row_index):
        super().__init__()
        self.queue_item = queue_item
        self.options = options
        self.row_index = row_index
        self._stop_event = threading.Event()

    def run(self):
        url = self.queue_item["url"]
        ydl_opts = self._build_ydl_opts(self.options)
        success = False
        outpath = ""

        def hook(d):
            if d["status"] == "downloading":
                p = d.get("_percent_str", "").strip()
                s = d.get("_speed_str", "").strip()
                eta = d.get("eta")
                eta_str = f"{eta}s" if eta is not None else ""
                self.progress.emit(f"[{self.queue_item['label']}] {p} {s} ETA:{eta_str}")
            elif d["status"] == "finished":
                self.progress.emit(f"Done downloading, post-processing…")

        ydl_opts["progress_hooks"] = [hook]

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Determine output filename
                if ydl.params.get('outtmpl'):
                    try:
                        outpath = ydl.prepare_filename(info)
                    except Exception:
                        pass
                success = True
        except Exception as e:
            self.progress.emit(f"Error: {e}")
            success = False

        self.finished_item.emit(self.row_index, outpath, success)

    def stop(self):
        self._stop_event.set()

    def _build_ydl_opts(self, opt):
        # Format selection
        quality_map = {
            "Auto (best)": "bv*+ba/b",
            "144p": "bv*[height=144]+ba/b[height=144]",
            "240p": "bv*[height=240]+ba/b[height=240]",
            "360p": "bv*[height=360]+ba/b[height=360]",
            "480p": "bv*[height=480]+ba/b[height=480]",
            "720p": "bv*[height=720]+ba/b[height=720]",
            "1080p": "bv*[height=1080]+ba/b[height=1080]",
            "1440p": "bv*[height=1440]+ba/b[height=1440]",
            "4K": "bv*[height=2160]+ba/b[height=2160]",
            "8K": "bv*[height=4320]+ba/b[height=4320]",
        }
        format_sel = quality_map.get(opt["quality"], "bv*+ba/b")

        # Audio-only override
        if opt.get("audio_only"):
            abr = opt.get("audio_bitrate", "192")
            format_sel = f"bestaudio/best"
            postprocessors = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": opt.get("audio_format", "mp3"),
                "preferredquality": str(abr),
            }]
        else:
            # Merge A+V to chosen container
            postprocessors = [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": opt.get("container", "mp4"),
            }]

        outtmpl = os.path.join(opt["output_dir"], "%(uploader)s", "%(playlist_title|live_title|title)s.%(ext)s")
        if opt.get("folder_mode") == "playlist":
            outtmpl = os.path.join(opt["output_dir"], "%(playlist_title)s", "%(title)s.%(ext)s")
        elif opt.get("folder_mode") == "channel":
            outtmpl = os.path.join(opt["output_dir"], "%(uploader)s", "%(title)s.%(ext)s")
        elif opt.get("folder_mode") == "date":
            outtmpl = os.path.join(opt["output_dir"], "%(upload_date>%Y-%m-%d)s", "%(title)s.%(ext)s")

        ydl_opts = {
            "format": format_sel,
            "outtmpl": outtmpl,
            "merge_output_format": opt.get("container", "mp4"),
            "noplaylist": not opt.get("treat_as_playlist", False),
            "ignoreerrors": True,
            "writesubtitles": opt.get("subs", False),
            "subtitleslangs": [opt.get("subs_lang", "en")] if opt.get("subs", False) else [],
            "embedsubtitles": opt.get("burn_subs", False),
            "source_address": "0.0.0.0",  # avoid IPv6 issues
            "concurrent_fragment_downloads": opt.get("concurrent", 3),
            "retries": 10,
            "fragment_retries": 10,
            "continuedl": True,
            "postprocessors": postprocessors,
            "quiet": True,
            "no_warnings": True,
            "ffmpeg_location": opt.get("ffmpeg_path") or None,
        }

        if opt.get("proxy"):
            ydl_opts["proxy"] = opt["proxy"]

        # Segment (start/end)
        if opt.get("segment_start") or opt.get("segment_end"):
            ydl_opts["download_ranges"] = lambda info: [{
                "start_time": opt.get("segment_start") or 0,
                "end_time": opt.get("segment_end")
            }]

        # Cookies for member videos (optional)
        if opt.get("cookies_file"):
            ydl_opts["cookiefile"] = opt["cookies_file"]

        return ydl_opts

# ---------- Main Window ----------

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 720)
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.active_workers = []

        self.config = load_json(CONFIG_FILE, {
            "output_dir": str(Path.home() / "Downloads" / "YouTube"),
            "quality": "Auto (best)",
            "container": "mp4",
            "audio_only": False,
            "audio_format": "mp3",
            "audio_bitrate": "192",
            "folder_mode": "channel",  # playlist/channel/date/none
            "proxy": "",
            "ffmpeg_path": "",
            "subs": False,
            "subs_lang": "en",
            "burn_subs": False,
            "concurrent": 3,
            "cookies_file": "",
            "schedule_enabled": False,
            "schedule_cron": "0 1 * * *",  # 01:00 daily
            "watchlist": [],   # urls for auto-download new videos
        })
        self.history = load_json(HISTORY_FILE, {"items": []})

        self._build_ui()
        self._refresh_schedule()

    # ----- UI Building -----
    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # URL row
        url_row = QtWidgets.QHBoxLayout()
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText("Paste YouTube video/playlist/channel URL…")
        paste_btn = QtWidgets.QPushButton("Paste")
        paste_btn.clicked.connect(self._paste_clipboard)
        add_btn = QtWidgets.QPushButton("Add to Queue")
        add_btn.clicked.connect(self._add_to_queue)
        url_row.addWidget(self.url_edit, 1)
        url_row.addWidget(paste_btn)
        url_row.addWidget(add_btn)
        layout.addLayout(url_row)

        # Options grid
        grid = QtWidgets.QGridLayout()

        # Quality
        grid.addWidget(QtWidgets.QLabel("Quality"), 0, 0)
        self.quality_combo = QtWidgets.QComboBox()
        self.quality_combo.addItems(["Auto (best)","144p","240p","360p","480p","720p","1080p","1440p","4K","8K"])
        self.quality_combo.setCurrentText(self.config.get("quality","Auto (best)"))
        grid.addWidget(self.quality_combo, 0, 1)

        # Container
        grid.addWidget(QtWidgets.QLabel("Format"), 0, 2)
        self.container_combo = QtWidgets.QComboBox()
        self.container_combo.addItems(["mp4","mkv","webm"])
        self.container_combo.setCurrentText(self.config.get("container","mp4"))
        grid.addWidget(self.container_combo, 0, 3)

        # Audio-only
        self.audio_only_chk = QtWidgets.QCheckBox("Audio only")
        self.audio_only_chk.setChecked(self.config.get("audio_only", False))
        grid.addWidget(self.audio_only_chk, 0, 4)

        self.audio_fmt_combo = QtWidgets.QComboBox()
        self.audio_fmt_combo.addItems(["mp3","m4a","flac","wav"])
        self.audio_fmt_combo.setCurrentText(self.config.get("audio_format","mp3"))
        grid.addWidget(self.audio_fmt_combo, 0, 5)

        self.audio_br_combo = QtWidgets.QComboBox()
        self.audio_br_combo.addItems(["64","96","128","160","192","256","320"])
        self.audio_br_combo.setCurrentText(self.config.get("audio_bitrate","192"))
        grid.addWidget(self.audio_br_combo, 0, 6)

        # Folder mode
        grid.addWidget(QtWidgets.QLabel("Folder by"), 1, 0)
        self.folder_combo = QtWidgets.QComboBox()
        self.folder_combo.addItems(["channel","playlist","date","none"])
        self.folder_combo.setCurrentText(self.config.get("folder_mode","channel"))
        grid.addWidget(self.folder_combo, 1, 1)

        # Output dir
        grid.addWidget(QtWidgets.QLabel("Save to"), 1, 2)
        self.output_edit = QtWidgets.QLineEdit(self.config.get("output_dir"))
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self._choose_output_dir)
        grid.addWidget(self.output_edit, 1, 3, 1, 3)
        grid.addWidget(browse_btn, 1, 6)

        # Subtitles
        self.subs_chk = QtWidgets.QCheckBox("Download subtitles")
        self.subs_chk.setChecked(self.config.get("subs", False))
        grid.addWidget(self.subs_chk, 2, 0)
        grid.addWidget(QtWidgets.QLabel("Lang"), 2, 1)
        self.subs_lang_edit = QtWidgets.QLineEdit(self.config.get("subs_lang","en"))
        self.subs_lang_edit.setFixedWidth(80)
        grid.addWidget(self.subs_lang_edit, 2, 2)
        self.burn_chk = QtWidgets.QCheckBox("Burn subtitles into video")
        self.burn_chk.setChecked(self.config.get("burn_subs", False))
        grid.addWidget(self.burn_chk, 2, 3)

        # Segment
        grid.addWidget(QtWidgets.QLabel("Segment start (s)"), 3, 0)
        self.seg_start = QtWidgets.QLineEdit()
        self.seg_start.setPlaceholderText("e.g., 0")
        grid.addWidget(self.seg_start, 3, 1)
        grid.addWidget(QtWidgets.QLabel("end (s)"), 3, 2)
        self.seg_end = QtWidgets.QLineEdit()
        self.seg_end.setPlaceholderText("leave empty for full")
        grid.addWidget(self.seg_end, 3, 3)

        # Proxy / Cookies / FFmpeg
        grid.addWidget(QtWidgets.QLabel("Proxy (optional)"), 4, 0)
        self.proxy_edit = QtWidgets.QLineEdit(self.config.get("proxy",""))
        grid.addWidget(self.proxy_edit, 4, 1, 1, 2)
        grid.addWidget(QtWidgets.QLabel("Cookies.txt (opt)"), 4, 3)
        self.cookies_edit = QtWidgets.QLineEdit(self.config.get("cookies_file",""))
        ck_btn = QtWidgets.QPushButton("…")
        ck_btn.clicked.connect(self._choose_cookies)
        grid.addWidget(self.cookies_edit, 4, 4, 1, 2)
        grid.addWidget(ck_btn, 4, 6)

        grid.addWidget(QtWidgets.QLabel("FFmpeg path (opt)"), 5, 0)
        self.ffmpeg_edit = QtWidgets.QLineEdit(self.config.get("ffmpeg_path",""))
        ff_btn = QtWidgets.QPushButton("…")
        ff_btn.clicked.connect(self._choose_ffmpeg)
        grid.addWidget(self.ffmpeg_edit, 5, 1, 1, 5)
        grid.addWidget(ff_btn, 5, 6)

        layout.addLayout(grid)

        # Queue/Table
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["URL/Label", "Status", "Saved Path", "When"])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        layout.addWidget(self.table)

        # Buttons row
        btn_row = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton("Start Queue")
        self.start_btn.clicked.connect(self._start_queue)
        self.stop_btn = QtWidgets.QPushButton("Stop All")
        self.stop_btn.clicked.connect(self._stop_all)
        self.update_core_btn = QtWidgets.QPushButton("Update yt-dlp Core")
        self.update_core_btn.clicked.connect(self._update_core)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.update_core_btn)
        layout.addLayout(btn_row)

        # Log
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(2000)
        layout.addWidget(self.log)

        # Scheduling Panel
        sched_group = QtWidgets.QGroupBox("Scheduling & Watchlist")
        sched_layout = QtWidgets.QGridLayout(sched_group)

        self.enable_sched = QtWidgets.QCheckBox("Enable scheduler")
        self.enable_sched.setChecked(self.config.get("schedule_enabled", False))
        sched_layout.addWidget(self.enable_sched, 0, 0)

        self.cron_edit = QtWidgets.QLineEdit(self.config.get("schedule_cron","0 1 * * *"))
        sched_layout.addWidget(QtWidgets.QLabel("Cron (min hour dom mon dow)"), 0, 1)
        sched_layout.addWidget(self.cron_edit, 0, 2)

        self.watchlist_edit = QtWidgets.QPlainTextEdit("\n".join(self.config.get("watchlist", [])))
        sched_layout.addWidget(QtWidgets.QLabel("Auto-download new uploads from these playlist/channel URLs (one per line):"), 1, 0, 1, 3)
        sched_layout.addWidget(self.watchlist_edit, 2, 0, 1, 3)

        sched_btn_row = QtWidgets.QHBoxLayout()
        apply_sched = QtWidgets.QPushButton("Apply Scheduler")
        apply_sched.clicked.connect(self._apply_scheduler)
        run_now = QtWidgets.QPushButton("Run Watchlist Now")
        run_now.clicked.connect(self._run_watchlist_now)
        sched_btn_row.addWidget(apply_sched)
        sched_btn_row.addWidget(run_now)
        sched_layout.addLayout(sched_btn_row, 3, 0, 1, 3)

        layout.addWidget(sched_group)

        self._append_log("Ready. Remember: video downloads always include audio by default.")

    # ----- Helper actions -----
    def closeEvent(self, event: QtGui.QCloseEvent):
        self._save_config()
        self.scheduler.shutdown(wait=False)
        super().closeEvent(event)

    def _append_log(self, text):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.appendPlainText(f"[{ts}] {text}")

    def _paste_clipboard(self):
        cb = QtWidgets.QApplication.clipboard()
        self.url_edit.setText(cb.text())

    def _choose_output_dir(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose output folder", self.output_edit.text())
        if d:
            self.output_edit.setText(d)

    def _choose_cookies(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose cookies.txt", "", "Text files (*.txt);;All files (*.*)")
        if f:
            self.cookies_edit.setText(f)

    def _choose_ffmpeg(self):
        f, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose ffmpeg executable", "", "Executable (*.exe *.bin *.app *.*)")
        if f:
            self.ffmpeg_edit.setText(f)

    # Queue handling
    def _add_to_queue(self):
        url = self.url_edit.text().strip()
        if not url:
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        when = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(url))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem("Queued"))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(""))
        self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(when))
        self._append_log(f"Added to queue: {url}")
        self.url_edit.clear()

    def _collect_options(self):
        opt = dict(self.config)
        opt.update({
            "output_dir": self.output_edit.text().strip() or self.config["output_dir"],
            "quality": self.quality_combo.currentText(),
            "container": self.container_combo.currentText(),
            "audio_only": self.audio_only_chk.isChecked(),
            "audio_format": self.audio_fmt_combo.currentText(),
            "audio_bitrate": self.audio_br_combo.currentText(),
            "folder_mode": self.folder_combo.currentText(),
            "subs": self.subs_chk.isChecked(),
            "subs_lang": self.subs_lang_edit.text().strip() or "en",
            "burn_subs": self.burn_chk.isChecked(),
            "proxy": self.proxy_edit.text().strip(),
            "cookies_file": self.cookies_edit.text().strip(),
            "ffmpeg_path": self.ffmpeg_edit.text().strip(),
            "segment_start": float(self.seg_start.text()) if self.seg_start.text().strip() else None,
            "segment_end": float(self.seg_end.text()) if self.seg_end.text().strip() else None,
            "treat_as_playlist": False,  # yt-dlp will detect playlists automatically; override if needed
        })
        Path(opt["output_dir"]).mkdir(parents=True, exist_ok=True)
        return opt

    def _start_queue(self):
        opt = self._collect_options()
        for row in range(self.table.rowCount()):
            status = self.table.item(row, 1).text()
            if status in ("Queued", "Failed"):
                url = self.table.item(row, 0).text()
                label = url if len(url) < 60 else url[:57]+"…"
                qi = {"url": url, "label": label}
                worker = DownloadWorker(qi, opt, row)
                worker.progress.connect(self._append_log)
                worker.finished_item.connect(self._item_finished)
                self.active_workers.append(worker)
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem("Downloading…"))
                worker.start()

    def _stop_all(self):
        for w in list(self.active_workers):
            try:
                w.terminate()
            except Exception:
                pass
        self.active_workers.clear()
        self._append_log("Stopped all workers.")

    def _item_finished(self, row, outpath, success):
        try:
            if success:
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem("Done"))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(outpath))
                self._append_log(f"Finished: saved to {outpath}")
                self._add_history(self.table.item(row,0).text(), outpath, True)
            else:
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem("Failed"))
                self._add_history(self.table.item(row,0).text(), outpath, False)
        finally:
            # remove worker
            self.active_workers = [w for w in self.active_workers if w.isRunning()]

    def _add_history(self, url, path, ok):
        self.history["items"].append({
            "url": url,
            "path": path,
            "ok": ok,
            "ts": datetime.now().isoformat(timespec="seconds")
        })
        save_json(HISTORY_FILE, self.history)

    # Scheduler
    def _apply_scheduler(self):
        self.config["schedule_enabled"] = self.enable_sched.isChecked()
        self.config["schedule_cron"] = self.cron_edit.text().strip()
        wl = [u.strip() for u in self.watchlist_edit.toPlainText().splitlines() if u.strip()]
        self.config["watchlist"] = wl
        self._save_config()
        self._refresh_schedule()

    def _refresh_schedule(self):
        # Clear jobs
        for job in self.scheduler.get_jobs():
            job.remove()

        if self.config.get("schedule_enabled"):
            try:
                fields = self.config["schedule_cron"].split()
                if len(fields) != 5:
                    raise ValueError("Cron must have 5 fields: m h dom mon dow")
                trigger = CronTrigger.from_crontab(self.config["schedule_cron"])
                self.scheduler.add_job(self._scheduled_run, trigger=trigger, id="ytdl_sched")
                self._append_log(f"Scheduler armed with cron: {self.config['schedule_cron']}")
            except Exception as e:
                self._append_log(f"Scheduler error: {e}")

    def _scheduled_run(self):
        self._append_log("Scheduled run started (watchlist).")
        self._run_watchlist_now()

    def _run_watchlist_now(self):
        urls = self.config.get("watchlist", [])
        if not urls:
            self._append_log("Watchlist is empty.")
            return
        for u in urls:
            self.url_edit.setText(u)
            self._add_to_queue()
        self._start_queue()

    # Core update
    def _update_core(self):
        self._append_log("Updating yt-dlp core (if installed via pip)…")
        import subprocess, sys as _sys
        try:
            subprocess.check_call([_sys.executable, "-m", "pip", "install", "-U", "yt-dlp"])
            self._append_log("yt-dlp updated.")
        except Exception as e:
            self._append_log(f"Update failed: {e}")

    def _save_config(self):
        self.config.update({
            "output_dir": self.output_edit.text().strip(),
            "quality": self.quality_combo.currentText(),
            "container": self.container_combo.currentText(),
            "audio_only": self.audio_only_chk.isChecked(),
            "audio_format": self.audio_fmt_combo.currentText(),
            "audio_bitrate": self.audio_br_combo.currentText(),
            "folder_mode": self.folder_combo.currentText(),
            "proxy": self.proxy_edit.text().strip(),
            "cookies_file": self.cookies_edit.text().strip(),
            "ffmpeg_path": self.ffmpeg_edit.text().strip(),
            "subs": self.subs_chk.isChecked(),
            "subs_lang": self.subs_lang_edit.text().strip() or "en",
            "burn_subs": self.burn_chk.isChecked(),
            "watchlist": [u.strip() for u in self.watchlist_edit.toPlainText().splitlines() if u.strip()],
        })
        save_json(CONFIG_FILE, self.config)

# ---------- App entry ----------

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    mw = MainWindow()
    # Dark-ish default palette
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(45, 45, 45))
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    app.setPalette(palette)

    mw.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
