import sys
import os
import math
import threading
import time
import json
import subprocess
import urllib.request
import urllib.parse
from dataclasses import dataclass
from typing import List, Optional

from PyQt6 import QtWidgets, QtCore, QtGui

try:
    import yt_dlp as ytdl
except Exception:
    ytdl = None


@dataclass
class FormatEntry:
    fmt_id: str
    ext: str
    resolution: str
    filesize: Optional[int]
    note: str


class YTDLPWorker(QtCore.QObject):
    formats_ready = QtCore.pyqtSignal(list)
    info_error = QtCore.pyqtSignal(str)
    info_ready = QtCore.pyqtSignal(dict)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    @QtCore.pyqtSlot()
    def run(self):
        if ytdl is None:
            self.info_error.emit('yt-dlp not installed')
            return
        try:
            opts = {'quiet': True, 'no_warnings': True}
            with ytdl.YoutubeDL(opts) as yd:
                info = yd.extract_info(self.url, download=False)
            formats = info.get('formats', [])
            # emit full info for title and other UI
            self.info_ready.emit(info)
            entries: List[FormatEntry] = []
            for f in formats:
                fmt_id = str(f.get('format_id') or f.get('id') or '')
                ext = f.get('ext', '')
                resolution = f.get('resolution') or f.get('height') or f.get('format') or ''
                if isinstance(resolution, int):
                    resolution = f"{resolution}p"
                filesize = f.get('filesize') or f.get('filesize_approx')
                note = f.get('format_note') or f.get('format') or ''
                entries.append(FormatEntry(fmt_id=fmt_id, ext=ext, resolution=str(resolution), filesize=filesize, note=str(note)))
            self.formats_ready.emit(entries)
        except Exception as e:
            self.info_error.emit(str(e))


class DownloadWorker(QtCore.QObject):
    progress = QtCore.pyqtSignal(float, float, float)  # percent, speed (bytes/s), eta (s)
    finished = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)

    def __init__(self, url: str, fmt: str, outdir: str, outtmpl: Optional[str] = None):
        super().__init__()
        self.url = url
        self.fmt = fmt
        self.outdir = outdir
        self.outtmpl = outtmpl
        self._pause_event = threading.Event()
        # EMA smoothing for download speed and throttling UI updates
        self._ema_speed = 0.0
        self._last_emit = 0.0
        self._ema_alpha = 0.3
        self._throttle = 0.25  # seconds between UI updates

    def _progress_hook(self, d):
        # if paused, block here until resumed
        try:
            while self._pause_event.is_set():
                time.sleep(0.1)
        except Exception:
            pass
        now = time.time()
        status = d.get('status')
        if status == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes') or 0
            inst_speed = float(d.get('speed') or 0.0)
            # update EMA for speed
            if self._ema_speed == 0.0:
                self._ema_speed = inst_speed
            else:
                self._ema_speed = self._ema_alpha * inst_speed + (1.0 - self._ema_alpha) * self._ema_speed

            percent = (downloaded / total_bytes * 100.0) if total_bytes else 0.0
            eta = ((total_bytes - downloaded) / self._ema_speed) if (self._ema_speed and total_bytes and downloaded < total_bytes) else 0.0

            # throttle UI emits
            if now - self._last_emit >= self._throttle:
                self.progress.emit(percent, float(self._ema_speed), float(eta))
                self._last_emit = now
        elif status == 'finished':
            # emit final state immediately
            self.progress.emit(100.0, 0.0, 0.0)

    @QtCore.pyqtSlot()
    def run(self):
        if ytdl is None:
            self.error.emit('yt-dlp not installed')
            return
        attempts = 3
        last_exc = None
        for attempt in range(1, attempts + 1):
            try:
                opts = {
                    'format': self.fmt,
                    'outtmpl': (self.outtmpl if self.outtmpl else os.path.join(self.outdir, '%(title)s.%(ext)s')),
                    'progress_hooks': [self._progress_hook],
                    'noprogress': True,
                    'quiet': True,
                    'no_warnings': True,
                    # resilient network / fragment settings
                    'continuedl': True,            # allow resume of partial downloads
                    'retries': 10,
                    'fragment_retries': 10,
                    'socket_timeout': 30,
                    'nopart': False,               # keep .part files so resume works
                    'skip_unavailable_fragments': True,
                }
                with ytdl.YoutubeDL(opts) as yd:
                    yd.download([self.url])
                self.finished.emit('done')
                return
            except Exception as e:
                last_exc = e
                errstr = str(e)
                # handle common partial-read errors by retrying (resume should pick up)
                if attempt < attempts:
                    try:
                        import time
                        time.sleep(1.5 * attempt)
                    except Exception:
                        pass
                    continue
                # final failure
                self.error.emit(f'Download failed after {attempts} attempts: {errstr}')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Video Downloader')
        self.resize(900, 560)

        # Main layout
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        # URL input
        url_layout = QtWidgets.QHBoxLayout()
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText('Paste video page URL here (yt-dlp supports many sites)')
        url_layout.addWidget(self.url_edit)
        self.analyze_btn = QtWidgets.QPushButton('Analyze')
        url_layout.addWidget(self.analyze_btn)
        layout.addLayout(url_layout)

        # video title label (below URL field)
        self.title_label = QtWidgets.QLabel('Title: —')
        layout.addWidget(self.title_label)

        # Site / Info label (with favicon)
        self.site_label = QtWidgets.QLabel('site: —')
        site_layout = QtWidgets.QHBoxLayout()
        self.site_icon_label = QtWidgets.QLabel()
        self.site_icon_label.setFixedSize(16, 16)
        site_layout.addWidget(self.site_icon_label)
        site_layout.addWidget(QtWidgets.QLabel(' '))
        site_layout.addWidget(self.site_label)
        layout.addLayout(site_layout)

        # formats table
        self.formats_table = QtWidgets.QTableWidget(0, 5)
        self.formats_table.setHorizontalHeaderLabels(['Format ID', 'Ext', 'Resolution', 'Filesize', 'Note'])
        self.formats_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.formats_table)

        # bottom controls
        bottom = QtWidgets.QHBoxLayout()

        folder_layout = QtWidgets.QHBoxLayout()
        self.folder_edit = QtWidgets.QLineEdit(os.path.expanduser('~'))
        self.folder_btn = QtWidgets.QPushButton('Change...')
        folder_layout.addWidget(QtWidgets.QLabel('Download folder:'))
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.folder_btn)
        bottom.addLayout(folder_layout, stretch=3)

        controls = QtWidgets.QVBoxLayout()
        self.download_btn = QtWidgets.QPushButton('Download Selected')
        self.download_btn.setEnabled(False)
        controls.addWidget(self.download_btn)
        self.pause_btn = QtWidgets.QPushButton('Pause')
        self.pause_btn.setEnabled(False)
        controls.addWidget(self.pause_btn)
        self.cancel_btn = QtWidgets.QPushButton('Cancel')
        self.cancel_btn.setEnabled(False)
        controls.addWidget(self.cancel_btn)
        bottom.addLayout(controls, stretch=1)

        layout.addLayout(bottom)

        # progress and stats
        stats = QtWidgets.QHBoxLayout()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        stats.addWidget(self.progress_bar)
        self.speed_label = QtWidgets.QLabel('Speed: 0 B/s')
        stats.addWidget(self.speed_label)
        self.eta_label = QtWidgets.QLabel('ETA: 00:00')
        stats.addWidget(self.eta_label)
        layout.addLayout(stats)

        # connections
        self.analyze_btn.clicked.connect(self.on_analyze)
        self.folder_btn.clicked.connect(self.on_change_folder)
        self.download_btn.clicked.connect(self.on_download)
        self.pause_btn.clicked.connect(self.on_pause_resume)
        self.cancel_btn.clicked.connect(self.on_cancel)

        self._workers = []
        self._download_thread = None
        self._download_worker = None
        self._current_target_path = None

        # load persisted state (download folder, lifetime stats)
        self._state_path = os.path.join(os.path.dirname(__file__), 'video_downloader_data.json')
        self._state = self._load_state()
        if self._state.get('download_folder'):
            self.folder_edit.setText(self._state.get('download_folder'))

        # bottom labels: lifetime stats and created-by
        footer = QtWidgets.QHBoxLayout()
        self.stats_label = QtWidgets.QLabel('Lifetime: 0 B — 0 downloads')
        footer.addWidget(self.stats_label)
        footer.addStretch(1)
        self.created_label = QtWidgets.QLabel('Created by Sbyer')
        footer.addWidget(self.created_label)
        layout.addLayout(footer)
        self._update_stats_label()

        # Style
        self.setStyleSheet('''
            QMainWindow { background: #121212; color: #EEE }
            QLabel { color: #DDD }
            QLineEdit { background: #222; color: #EEE; padding: 6px; border-radius: 4px }
            QPushButton { background: #2b6; color: #012; padding: 6px; border-radius: 6px }
            QPushButton:disabled { background: #444; color: #888 }
            QTableWidget { background: #101010; color: #EEE }
            QHeaderView::section { background: #1b1b1b; color: #ccc }
        ''')

    def on_pause_resume(self):
        """Toggle pause/resume for the active download worker."""
        if not self._download_worker:
            return
        ev = getattr(self._download_worker, '_pause_event', None)
        if ev is None:
            return
        # If currently running (not paused) -> pause
        if not ev.is_set():
            ev.set()
            self.pause_btn.setText('Resume')
        else:
            ev.clear()
            self.pause_btn.setText('Pause')

    def _load_state(self) -> dict:
        try:
            if os.path.exists(self._state_path):
                with open(self._state_path, 'r', encoding='utf-8') as fh:
                    return json.load(fh) or {}
        except Exception:
            pass
        return {}

    def _save_state(self) -> None:
        try:
            d = os.path.dirname(self._state_path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            with open(self._state_path, 'w', encoding='utf-8') as fh:
                json.dump(self._state or {}, fh, indent=2)
        except Exception:
            pass

    def _update_stats_label(self) -> None:
        try:
            lb = self._state.get('lifetime_bytes', 0)
            cnt = self._state.get('downloads_count', 0)
            self.stats_label.setText(f'Lifetime: {self._human_size(lb)} — {cnt} downloads')
        except Exception:
            self.stats_label.setText('Lifetime: 0 B — 0 downloads')

    def detect_site(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            p = urlparse(url)
            return p.netloc or 'unknown'
        except Exception:
            return 'unknown'

    def _load_favicon(self, host: str) -> None:
        """Try to load favicon from host and set it to site_icon_label (best-effort)."""
        try:
            if not host:
                return
            # try common favicon locations
            tried = []
            for scheme in ('https', 'http'):
                url = f"{scheme}://{host}/favicon.ico"
                tried.append(url)
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=2) as resp:
                        data = resp.read()
                        if data:
                            pix = QtGui.QPixmap()
                            if pix.loadFromData(data):
                                self.site_icon_label.setPixmap(pix.scaled(16, 16, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
                                return
                except Exception:
                    pass
        except Exception:
            pass

    def _numbered_name(self, path: str) -> str:
        """Return a new path with a numeric prefix to avoid name collisions."""
        try:
            d, base = os.path.split(path)
            for i in range(1, 10000):
                newbase = f"{i} - {base}"
                newpath = os.path.join(d, newbase)
                if not os.path.exists(newpath):
                    return newpath
        except Exception:
            pass
        return path

    def on_analyze(self):
        url = self.url_edit.text().strip()
        if not url:
            QtWidgets.QMessageBox.warning(self, 'No URL', 'Please paste a URL first')
            return

        site = self.detect_site(url)
        self.site_label.setText(f'site: {site}')
        # try to load favicon for the host
        try:
            from urllib.parse import urlparse
            host = urlparse(url).netloc
            self._load_favicon(host)
        except Exception:
            pass

        self.formats_table.setRowCount(0)
        self.download_btn.setEnabled(False)

        # spawn worker thread to parse formats
        self.analyze_btn.setEnabled(False)
        worker = YTDLPWorker(url)
        thread = QtCore.QThread(self)
        worker.moveToThread(thread)
        worker.formats_ready.connect(self.on_formats_ready)
        worker.info_ready.connect(self.on_info_ready)
        worker.info_error.connect(self.on_info_error)
        thread.started.connect(worker.run)
        thread.start()
        # keep references to avoid GC
        self._workers.append((thread, worker))

    def on_info_error(self, err: str):
        QtWidgets.QMessageBox.critical(self, 'Error', f'Failed to get info: {err}')
        self.analyze_btn.setEnabled(True)

    def on_info_ready(self, info: dict):
        """Receive full info dict from YTDLPWorker and update UI (title)."""
        try:
            title = info.get('title') if isinstance(info, dict) else None
            if title:
                self.title_label.setText(f'Title: {title}')
            else:
                self.title_label.setText('Title: —')
        except Exception:
            self.title_label.setText('Title: —')

    def on_formats_ready(self, entries: List[FormatEntry]):
        self.analyze_btn.setEnabled(True)
        # Sort by resolution (best first) then filesize (largest first)
        def score(e: FormatEntry):
            h = 0
            try:
                h = int(''.join([c for c in e.resolution if c.isdigit()]) or 0)
            except Exception:
                h = 0
            fs = e.filesize or 0
            return (-h, -fs)

        entries = sorted(entries, key=score)
        self.formats_table.setRowCount(len(entries))
        for i, e in enumerate(entries):
            self.formats_table.setItem(i, 0, QtWidgets.QTableWidgetItem(e.fmt_id))
            self.formats_table.setItem(i, 1, QtWidgets.QTableWidgetItem(e.ext))
            self.formats_table.setItem(i, 2, QtWidgets.QTableWidgetItem(e.resolution))
            fs_str = f"{e.filesize / 1024 / 1024:.2f} MB" if e.filesize else '—'
            self.formats_table.setItem(i, 3, QtWidgets.QTableWidgetItem(fs_str))
            self.formats_table.setItem(i, 4, QtWidgets.QTableWidgetItem(e.note))
        self.formats_table.resizeRowsToContents()
        self.download_btn.setEnabled(True if entries else False)

    def on_change_folder(self):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose download folder', self.folder_edit.text())
        if d:
            self.folder_edit.setText(d)

    def _selected_format(self) -> Optional[str]:
        items = self.formats_table.selectedItems()
        if not items:
            # if none selected, pick top row
            if self.formats_table.rowCount() == 0:
                return None
            return self.formats_table.item(0, 0).text()
        # selectedItems returns multiple items across columns; take first row's format id
        row = items[0].row()
        return self.formats_table.item(row, 0).text()

    def on_download(self):
        url = self.url_edit.text().strip()
        fmt = self._selected_format()
        outdir = self.folder_edit.text().strip() or os.path.expanduser('~')
        if not url or not fmt:
            QtWidgets.QMessageBox.warning(self, 'Missing', 'Please provide URL and select a format')
            return

        # persist chosen folder
        self._state['download_folder'] = outdir
        self._save_state()

        # Determine expected filename and filesize using yt-dlp info
        expected_path = None
        expected_filesize = None
        try:
            if ytdl is not None:
                with ytdl.YoutubeDL({'quiet': True, 'no_warnings': True}) as yd:
                    info = yd.extract_info(url, download=False)
                    info_format = info.copy()
                    info_format['format_id'] = fmt
                    expected_name = yd.prepare_filename(info_format)
                    if not os.path.isabs(expected_name):
                        expected_name = os.path.join(outdir, expected_name)
                    expected_path = expected_name
                    formats = info.get('formats', [])
                    for f in formats:
                        if str(f.get('format_id') or f.get('id') or '') == str(fmt):
                            expected_filesize = f.get('filesize') or f.get('filesize_approx')
                            break
        except Exception:
            expected_path = None
            expected_filesize = None

        # check for existing final file or .part file
        outtmpl = None
        if expected_path:
            part_path = expected_path + '.part'
            if os.path.exists(expected_path):
                if expected_filesize and os.path.getsize(expected_path) < expected_filesize:
                    resp = QtWidgets.QMessageBox.question(self, 'File exists', f"Target file exists but is smaller than expected ({self._human_size(os.path.getsize(expected_path))} < {self._human_size(expected_filesize)}).\nContinue from last download? (Yes = resume, No = restart, Cancel = abort)", QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No | QtWidgets.QMessageBox.StandardButton.Cancel)
                    if resp == QtWidgets.QMessageBox.StandardButton.Cancel:
                        return
                    if resp == QtWidgets.QMessageBox.StandardButton.No:
                        resp2 = QtWidgets.QMessageBox.question(self, 'Download anyway', 'Start a fresh download and keep the existing file (create new numbered name)?', QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                        if resp2 == QtWidgets.QMessageBox.StandardButton.Yes:
                            outtmpl = self._numbered_name(expected_path)
                        else:
                            try:
                                os.remove(expected_path)
                            except Exception:
                                pass
                else:
                    resp = QtWidgets.QMessageBox.question(self, 'File exists', 'Target file already exists. Overwrite?', QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No | QtWidgets.QMessageBox.StandardButton.Cancel)
                    if resp == QtWidgets.QMessageBox.StandardButton.Cancel:
                        return
                    if resp == QtWidgets.QMessageBox.StandardButton.No:
                        resp2 = QtWidgets.QMessageBox.question(self, 'Download anyway', 'Download as a new file (add numeric prefix)?', QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
                        if resp2 == QtWidgets.QMessageBox.StandardButton.Yes:
                            outtmpl = self._numbered_name(expected_path)
                        else:
                            return
                    else:
                        try:
                            os.remove(expected_path)
                        except Exception:
                            pass
            elif os.path.exists(part_path):
                resp = QtWidgets.QMessageBox.question(self, 'Partial file found', 'A partial (.part) file exists. Continue download (resume) or start over?\nYes = resume, No = start over', QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No | QtWidgets.QMessageBox.StandardButton.Cancel)
                if resp == QtWidgets.QMessageBox.StandardButton.Cancel:
                    return
                if resp == QtWidgets.QMessageBox.StandardButton.No:
                    try:
                        os.remove(part_path)
                    except Exception:
                        pass

        # store current target for updating stats after finish
        self._current_target_path = outtmpl if outtmpl else expected_path
        # disable UI
        self.download_btn.setEnabled(False)
        self.analyze_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)

        # start download thread
        self._download_worker = DownloadWorker(url=url, fmt=fmt, outdir=outdir, outtmpl=outtmpl)
        self._download_thread = QtCore.QThread(self)
        self._download_worker.moveToThread(self._download_thread)
        self._download_worker.progress.connect(self._on_progress)
        self._download_worker.finished.connect(self._on_finished)
        self._download_worker.error.connect(self._on_download_error)
        self._download_thread.started.connect(self._download_worker.run)
        self._download_thread.start()

    def _on_progress(self, percent: float, speed: float, eta: float):
        self.progress_bar.setValue(int(percent))
        # human readable speed
        speed_str = self._human_size(speed) + '/s' if speed else '0 B/s'
        self.speed_label.setText(f'Speed: {speed_str}')
        self.eta_label.setText('ETA: ' + self._format_eta(eta))

    def _format_eta(self, s: float) -> str:
        try:
            s = max(0, int(s))
            m, sec = divmod(s, 60)
            h, m = divmod(m, 60)
            if h:
                return f'{h:d}h {m:02d}m'
            if m:
                return f'{m:d}m {sec:02d}s'
            return f'{sec:d}s'
        except Exception:
            return '--'

    def _human_size(self, n: float) -> str:
        if n is None:
            return '0 B'
        n = float(n)
        if n < 1024:
            return f'{n:.0f} B'
        for unit in ['KB', 'MB', 'GB', 'TB']:
            n /= 1024.0
            if abs(n) < 1024.0:
                return f"{n:.2f} {unit}"
        return f"{n:.2f} PB"

    def _on_finished(self, msg: str):
        self.progress_bar.setValue(100)
        # update lifetime stats if we know the target path
        try:
            if self._current_target_path and os.path.exists(self._current_target_path):
                size = os.path.getsize(self._current_target_path)
                self._state['lifetime_bytes'] = self._state.get('lifetime_bytes', 0) + int(size)
                self._state['downloads_count'] = self._state.get('downloads_count', 0) + 1
                self._save_state()
                self._update_stats_label()
        except Exception:
            pass

        # finished dialog with Open button
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle('Download finished')
        dlg.setText('Download completed successfully')
        open_btn = dlg.addButton('Open', QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        ok_btn = dlg.addButton('OK', QtWidgets.QMessageBox.ButtonRole.RejectRole)
        dlg.exec()
        if dlg.clickedButton() == open_btn:
            # open file location in explorer and select file if possible
            try:
                if self._current_target_path and os.path.exists(self._current_target_path):
                    subprocess.Popen(['explorer', '/select,', os.path.normpath(self._current_target_path)])
                else:
                    os.startfile(os.path.normpath(self.folder_edit.text()))
            except Exception:
                try:
                    os.startfile(os.path.normpath(self.folder_edit.text()))
                except Exception:
                    pass

        self._cleanup_after_download()

    def _on_download_error(self, err: str):
        QtWidgets.QMessageBox.critical(self, 'Download error', err)
        self._cleanup_after_download()

    def _cleanup_after_download(self):
        self.download_btn.setEnabled(True)
        self.analyze_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        try:
            if self._download_thread:
                self._download_thread.quit()
                self._download_thread.wait(2000)
        except Exception:
            pass
        self._download_thread = None
        self._download_worker = None

    def on_cancel(self):
        # yt-dlp doesn't provide an easy cancel hook from here; best-effort: terminate thread
        if self._download_thread and self._download_thread.isRunning():
            # no clean cancel; inform user
            QtWidgets.QMessageBox.information(self, 'Cancel', 'Cancel will stop after current chunk (best-effort).')
        self._cleanup_after_download()


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
