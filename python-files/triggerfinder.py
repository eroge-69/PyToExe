# trigger_finder_window_viewer.py
from __future__ import annotations
import sys, os, re, threading, traceback, time, json as pyjson
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Iterable, Optional, Tuple, Dict

# ---- optionales requests (GUI-Hinweis, falls fehlt) ----
try:
    import requests as _requests
    REQUESTS_OK = True
except ImportError:
    _requests = None
    REQUESTS_OK = False

from PySide6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Signal, QObject,
    QRect, QSize, QPoint, QSettings, QCoreApplication
)
from PySide6.QtGui import (
    QPalette, QColor, QPainter, QTextFormat, QSyntaxHighlighter, QTextCharFormat,
    QFont, QTextOption, QTextCursor, QShortcut, QKeySequence, QGuiApplication
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableView, QProgressBar, QMessageBox, QStatusBar,
    QPlainTextEdit, QTabWidget, QTabBar, QDialog, QDialogButtonBox, QTextBrowser, QSpinBox, QDoubleSpinBox
)

# -------- Einstellungen --------
DEFAULT_START_DIR = r"C:\redENGINE\Dumps"
EXT_WHITELIST = {".lua", ".txt", ".log", ".js"}
MAX_FILE_MB = 5
HTTP_TIMEOUT = 10  # Sekunden

TRIGGER_SUBSTR = "TriggerServerEvent"
TRIGGER_REGEX = re.compile(r"TriggerServerEvent\s*\(\s*(['\"])(.*?)\1", re.IGNORECASE)

# Webhook-Erkennung
WEBHOOK_REGEX = re.compile(r"https://discord\.com/api/webhooks/[^\s'\"()<>]+")
WEBHOOK_URL_FULL_RE = re.compile(
    r"^https?://(?:www\.)?(?:discord\.com|discordapp\.com)/api/webhooks/[^\s]+$", re.IGNORECASE
)

# ---------------- Datenklassen ----------------
@dataclass
class Hit:
    file: str
    line_no: int
    full_line: str  # für Webhooks: nur die URL!

@dataclass
class FolderItem:
    name: str
    path: str

# --------- Globaler Exception-Hook ---------
def _excepthook(exctype, value, tb):
    msg = "".join(traceback.format_exception(exctype, value, tb))
    try:
        QMessageBox.critical(None, "Unerwarteter Fehler", msg)
    finally:
        print(msg, file=sys.stderr)
sys.excepthook = _excepthook

# ---------------- Code Editor ----------------
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor); self.editor = editor
    def sizeHint(self): return QSize(self.editor.lineNumberAreaWidth(), 0)
    def paintEvent(self, event): self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self._settings = QSettings()
        default_size = int(self._settings.value("editor/fontPointSize", 15))

        self._lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setStyleSheet("QPlainTextEdit { background: #1E1E1E; color: #D4D4D4; border: none; }")

        f = QFont("Consolas"); f.setStyleHint(QFont.Monospace); f.setPointSize(default_size)
        self.setFont(f)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        self.highlightCurrentLine()

        QShortcut(QKeySequence("Ctrl+="), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl++"), self, activated=self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, activated=self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, activated=self.zoom_reset)

        self._temp_highlights_active = False

    def _current_point_size(self) -> int: return max(6, self.font().pointSize())
    def _apply_point_size(self, pt: int):
        pt = max(8, min(48, pt))
        f = self.font(); f.setPointSize(pt); self.setFont(f)
        self.setTabStopDistance(4 * self.fontMetrics().horizontalAdvance(' '))
        self.updateLineNumberAreaWidth(0)
        self._settings.setValue("editor/fontPointSize", pt)
    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            self._apply_point_size(self._current_point_size() + (1 if e.angleDelta().y() > 0 else -1)); e.accept()
        else:
            super().wheelEvent(e)
    def zoom_in(self):  self._apply_point_size(self._current_point_size() + 1)
    def zoom_out(self): self._apply_point_size(self._current_point_size() - 1)
    def zoom_reset(self):
        base = int(self._settings.value("editor/defaultBase", 15)); self._apply_point_size(base)

    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance('9') * digits
    def updateLineNumberAreaWidth(self, _): self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    def updateLineNumberArea(self, rect, dy):
        if dy: self._lineNumberArea.scroll(0, dy)
        else:  self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()): self.updateLineNumberAreaWidth(0)
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), QColor(37, 37, 38))
        block = self.firstVisibleBlock()
        n = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(153, 153, 153))
                painter.drawText(0, top, self._lineNumberArea.width()-6, self.fontMetrics().height(),
                                 Qt.AlignRight, str(n+1))
            block = block.next(); top = bottom
            bottom = top + int(self.blockBoundingRect(block).height()); n += 1
    def highlightCurrentLine(self):
        from PySide6.QtWidgets import QTextEdit
        sel = QTextEdit.ExtraSelection()
        sel.format.setBackground(QColor(47, 47, 47))
        sel.format.setProperty(QTextFormat.FullWidthSelection, True)
        sel.cursor = self.textCursor(); sel.cursor.clearSelection()
        self.setExtraSelections([sel])

    def mark_event(self, call_start: int, call_len: int, evt_start: int | None, evt_len: int | None):
        from PySide6.QtWidgets import QTextEdit
        extras = []; extras.extend(self.extraSelections())
        def add_sel(start, length, rgba: QColor, bold=False):
            if start is None or length is None or length <= 0: return
            ex = QTextEdit.ExtraSelection()
            c = self.textCursor(); c.setPosition(start); c.setPosition(start + length, QTextCursor.KeepAnchor)
            ex.cursor = c; fmt = ex.format; fmt.setBackground(rgba)
            if bold: fmt.setFontWeight(QFont.DemiBold)
            fmt.setForeground(QColor("#FFFFFF")); extras.append(ex)
        add_sel(call_start, call_len, QColor(14, 99, 156, 56), False)
        if evt_start is not None and evt_len is not None:
            add_sel(evt_start, evt_len, QColor(14, 99, 156, 112), True)
        self.setExtraSelections(extras)
        c = self.textCursor(); c.setPosition(call_start); self.setTextCursor(c); self.centerCursor()
        self._temp_highlights_active = True
    def clear_temp_highlights(self):
        self._temp_highlights_active = False; self.highlightCurrentLine()
    def mousePressEvent(self, e):
        if self._temp_highlights_active: self.clear_temp_highlights()
        super().mousePressEvent(e)
    def highlight_trigger_in_line(self, line_no: int):
        try:
            text = self.toPlainText(); lines = text.splitlines(keepends=True)
            if not lines: return
            target = max(0, min(len(lines)-1, line_no-1))
            abs_start = sum(len(l) for l in lines[:target]); line_text = lines[target]
            m = TRIGGER_REGEX.search(line_text)
            call_start = abs_start + (m.start() if m else 0)
            call_len   = (m.end() - m.start()) if m else len(line_text)
            evt_start  = abs_start + m.start(2) if m else None
            evt_len    = (m.end(2) - m.start(2)) if m else None
            self.mark_event(call_start, call_len, evt_start, evt_len)
        except Exception: _excepthook(*sys.exc_info())

class LuaHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.fmt_keyword = QTextCharFormat(); self.fmt_keyword.setForeground(QColor("#C586C0"))
        self.fmt_builtin = QTextCharFormat(); self.fmt_builtin.setForeground(QColor("#DCDCAA"))
        self.fmt_string = QTextCharFormat();  self.fmt_string.setForeground(QColor("#CE9178"))
        self.fmt_number = QTextCharFormat();  self.fmt_number.setForeground(QColor("#B5CEA8"))
        self.fmt_comment = QTextCharFormat(); self.fmt_comment.setForeground(QColor("#6A9955"))
        kw = r"\b(and|break|do|else|elseif|end|false|for|function|goto|if|in|local|nil|not|or|repeat|return|then|true|until|while)\b"
        builtins = r"\b(_G|assert|collectgarbage|dofile|error|getmetatable|ipairs|load|next|pairs|pcall|print|rawequal|rawget|rawset|require|select|setmetatable|tonumber|tostring|type|xpcall|string|table|math|io|os|coroutine|debug)\b"
        self.re_kw = re.compile(kw); self.re_bi = re.compile(builtins)
        self.re_num = re.compile(r"\b\d+(\.\d+)?\b")
        self.re_str = re.compile(r"('([^'\\]|\\.)*'|\"([^\"\\]|\\.)*\")")
        self.re_comment = re.compile(r"--.*$")

    def highlightBlock(self, text: str):
        for m in self.re_comment.finditer(text): self.setFormat(m.start(), m.end()-m.start(), self.fmt_comment)
        for m in self.re_str.finditer(text):     self.setFormat(m.start(), m.end()-m.start(), self.fmt_string)
        for m in self.re_kw.finditer(text):      self.setFormat(m.start(), m.end()-m.start(), self.fmt_keyword)
        for m in self.re_bi.finditer(text):      self.setFormat(m.start(), m.end()-m.start(), self.fmt_builtin)
        for m in self.re_num.finditer(text):     self.setFormat(m.start(), m.end()-m.start(), self.fmt_number)

# ---------------- Models ----------------
class HitsModel(QAbstractTableModel):
    HEADERS = ["Zeile (Kontext)"]
    def __init__(self, hits: List['Hit'] | None = None):
        super().__init__(); self._hits: List[Hit] = hits or []
    def rowCount(self, parent=QModelIndex()) -> int: return len(self._hits)
    def columnCount(self, parent=QModelIndex()) -> int: return 1
    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid(): return None
        h = self._hits[index.row()]
        if role == Qt.DisplayRole: return h.full_line.strip()
        if role == Qt.UserRole:    return h.full_line.lower()
        if role == Qt.UserRole+1:  return h.file
        if role == Qt.UserRole+2:  return h.line_no
        return None
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal: return self.HEADERS[section]
        return None
    def setHits(self, hits: List['Hit']):
        self.beginResetModel(); self._hits = hits; self.endResetModel()
    def hitAt(self, row: int) -> 'Hit': return self._hits[row]
    def allHits(self) -> List['Hit']: return list(self._hits)

class FoldersModel(QAbstractTableModel):
    HEADERS = ["Ordner"]
    def __init__(self, items: List[FolderItem] | None = None):
        super().__init__(); self._items: List[FolderItem] = items or []
    def rowCount(self, parent=QModelIndex()) -> int: return len(self._items)
    def columnCount(self, parent=QModelIndex()) -> int: return 1
    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid(): return None
        item = self._items[index.row()]
        if role == Qt.DisplayRole: return item.name
        if role == Qt.UserRole:    return item.name.lower()
        if role == Qt.UserRole+1:  return item.path
        return None
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal: return self.HEADERS[section]
        return None
    def setFolders(self, items: List[FolderItem]):
        self.beginResetModel(); self._items = items; self.endResetModel()
    def itemAt(self, row: int) -> FolderItem: return self._items[row]

# --------- Filter Proxy ---------
class EventFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__(); self._needle = ""; self._category_keyword: Optional[str] = None
    def setNeedle(self, text: str):
        self._needle = (text or "").lower().strip(); self.invalidateFilter()
    def setCategoryKeyword(self, kw: Optional[str]):
        self._category_keyword = kw.lower() if kw else None; self.invalidateFilter()
    def filterAcceptsRow(self, source_row: int, parent: QModelIndex) -> bool:
        idx = self.sourceModel().index(source_row, 0, parent)
        val = (self.sourceModel().data(idx, Qt.UserRole) or "")
        if self._needle and self._needle not in val: return False
        if self._category_keyword and self._category_keyword not in val: return False
        return True

# ---------------- Scanner ----------------
class Scanner(QObject):
    progress = Signal(int); finished = Signal(list); status = Signal(str); aborted = Signal(); total_files = Signal(int)
    MODE_TRIGGER = "trigger"
    MODE_WEBHOOK = "webhook"

    def __init__(self, root: str, mode: str):
        super().__init__(); self.root = root; self.mode = mode
        self._abort = False; self.max_bytes = MAX_FILE_MB * 1024 * 1024

    def abort(self): self._abort = True

    def run(self):
        try:
            files = list(self._iter_files(self.root))
            total = len(files); self.total_files.emit(total)
            if total == 0: self.progress.emit(100); self.finished.emit([]); return
            hits: List[Hit] = []; completed = 0
            max_workers = min(32, (os.cpu_count() or 8) * 2)
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = [pool.submit(self._scan_file, p) for p in files]
                for fut in as_completed(futures):
                    if self._abort: self.status.emit("Abgebrochen."); self.aborted.emit(); return
                    try:
                        res = fut.result()
                        if res: hits.extend(res)
                    except Exception as e:
                        self.status.emit(f"Fehler: {e}")
                    completed += 1; self.progress.emit(int(completed * 100 / total))
            self.finished.emit(hits)
        except Exception as e:
            self.status.emit(f"Scan-Fehler: {e}"); self.finished.emit([])

    def _iter_files(self, root: str) -> Iterable[str]:
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                p = os.path.join(dirpath, name)
                ext = os.path.splitext(name)[1].lower()
                if EXT_WHITELIST and ext not in EXT_WHITELIST: continue
                try:
                    if os.path.getsize(p) > self.max_bytes: continue
                except OSError: continue
                yield p

    def _scan_file(self, path: str) -> List[Hit]:
        out: List[Hit] = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                if self.mode == self.MODE_TRIGGER:
                    for i, line in enumerate(f, start=1):
                        if TRIGGER_SUBSTR not in line: continue
                        if TRIGGER_REGEX.search(line):
                            out.append(Hit(file=path, line_no=i, full_line=line.rstrip("\n")))
                else:
                    for i, line in enumerate(f, start=1):
                        if "discord.com/api/webhooks/" not in line: continue
                        for url in WEBHOOK_REGEX.findall(line):
                            out.append(Hit(file=path, line_no=i, full_line=url))
        except Exception:
            pass
        return out

# ---------------- Viewer ----------------
class ViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Viewer")
        self.resize(1200, 800)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(QPoint(screen.center().x() - self.width()//2, screen.center().y() - self.height()//2))
        self.editor = CodeEditor()
        self.setCentralWidget(self.editor)
        self.highlighter = LuaHighlighter(self.editor.document())
        self.editor.setFocus()

    def open_file_and_highlight(self, file_path: str, line_no: int):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Datei konnte nicht gelesen werden:\n{e}"); return
        self.setWindowTitle(file_path)
        self.editor.setPlainText(text)
        self.editor.highlight_trigger_in_line(line_no)

# ---------------- Spammer Worker & Dialog ----------------
class SpammerWorker(QObject):
    progress = Signal(int)            # gesendet
    status = Signal(str)              # status text
    finished = Signal(int, int)       # sent, failed
    error = Signal(str)

    def __init__(self, url: str, message: str, count: int, delay_s: float):
        super().__init__()
        self.url = url
        self.message = message
        self.count = count            # 0 = unendlich
        self.delay_s = max(0.0, delay_s)
        self._stop = False

    def stop(self): self._stop = True

    def run(self):
        if not REQUESTS_OK:
            self.error.emit("requests nicht installiert"); return
        sent = 0; failed = 0
        session = _requests.Session()
        headers = {"Content-Type": "application/json"}
        self.status.emit("Spammer gestartet …")
        try:
            while not self._stop and (self.count == 0 or sent < self.count):
                try:
                    r = session.post(self.url, headers=headers, json={"content": self.message}, timeout=HTTP_TIMEOUT)
                    if r.status_code in (200, 201, 204):
                        sent += 1
                        self.progress.emit(sent)
                    elif r.status_code == 429:
                        # Discord liefert retry_after (sekunden oder ms). Versuche beides zu handlen.
                        try:
                            data = r.json()
                            ra = data.get("retry_after", 1)
                            retry = float(ra)
                            if retry > 10:  # vermutlich ms
                                retry = retry / 1000.0
                        except Exception:
                            retry = 1.0
                        self.status.emit(f"Rate‑Limit: warte {retry:.2f}s …")
                        time.sleep(min(retry, 5.0))
                        continue
                    else:
                        failed += 1
                        self.status.emit(f"HTTP {r.status_code}")
                except Exception as e:
                    failed += 1
                    self.status.emit(f"Fehler: {e}")
                # Pause zwischen Nachrichten
                if self.delay_s > 0:
                    t = 0.0
                    # fein-granulares Sleep, damit Stop schnell greift
                    while t < self.delay_s and not self._stop:
                        dt = min(0.1, self.delay_s - t)
                        time.sleep(dt); t += dt
        finally:
            self.finished.emit(sent, failed)

class SpammerDialog(QDialog):
    def __init__(self, parent: QWidget, url: str):
        super().__init__(parent)
        self.setWindowTitle("Webhook Spammer")
        self.resize(560, 420)
        self.url = url
        v = QVBoxLayout(self)

        # URL Anzeige
        url_row = QHBoxLayout()
        url_row.addWidget(QLabel("URL:"))
        self.url_edit = QLineEdit(self.url); self.url_edit.setReadOnly(True)
        self.url_edit.setStyleSheet("QLineEdit { background:#202020; color:#cfcfcf; }")
        url_row.addWidget(self.url_edit, 1)
        v.addLayout(url_row)

        # Message
        msg_row = QHBoxLayout()
        msg_row.addWidget(QLabel("Nachricht:"))
        self.msg_edit = QLineEdit()
        self.msg_edit.setPlaceholderText("Deine Spam‑Nachricht …")
        msg_row.addWidget(self.msg_edit, 1)
        v.addLayout(msg_row)

        # Einstellungen: Intervall + Anzahl
        cfg = QHBoxLayout()
        cfg.addWidget(QLabel("Intervall (s):"))
        self.delay_spin = QDoubleSpinBox(); self.delay_spin.setRange(0.0, 60.0); self.delay_spin.setDecimals(2); self.delay_spin.setValue(1.00)
        cfg.addWidget(self.delay_spin)
        cfg.addSpacing(16)
        cfg.addWidget(QLabel("Anzahl (0=∞):"))
        self.count_spin = QSpinBox(); self.count_spin.setRange(0, 100000); self.count_spin.setValue(0)
        cfg.addWidget(self.count_spin)
        cfg.addStretch(1)
        v.addLayout(cfg)

        # Status / Log
        self.info = QTextBrowser()
        self.info.setStyleSheet("QTextBrowser { background:#181818; color:#dcdcdc; border:1px solid #333; }")
        v.addWidget(self.info, 1)

        # Footer: Counter + Start/Stop/Close
        footer = QHBoxLayout()
        self.counter_lbl = QLabel("Gesendet: 0  |  Fehler: 0")
        footer.addWidget(self.counter_lbl, 1)
        self.btn_start = QPushButton("Start")
        self.btn_stop  = QPushButton("Stop"); self.btn_stop.setEnabled(False)
        self.btn_close = QPushButton("Schließen")
        footer.addWidget(self.btn_start); footer.addWidget(self.btn_stop); footer.addWidget(self.btn_close)
        v.addLayout(footer)

        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_close.clicked.connect(self.on_close)

        if not REQUESTS_OK:
            QMessageBox.warning(self, "Hinweis",
                                "Das Modul 'requests' ist nicht installiert.\n"
                                "Bitte installiere es mit:\n\npip install requests")

        self._thread: Optional[threading.Thread] = None
        self._worker: Optional[SpammerWorker] = None
        self._sent = 0; self._fail = 0

    def log(self, html: str): self.info.append(html)
    def set_busy(self, busy: bool):
        self.btn_start.setEnabled(not busy)
        self.btn_stop.setEnabled(busy)
        self.btn_close.setEnabled(not busy)
        QGuiApplication.setOverrideCursor(Qt.WaitCursor if busy else Qt.ArrowCursor)

    def on_start(self):
        url = self.url_edit.text().strip()
        if not WEBHOOK_URL_FULL_RE.match(url):
            QMessageBox.warning(self, "Hinweis", "Ungültige Webhook‑URL."); return
        msg = self.msg_edit.text()
        if not msg:
            QMessageBox.information(self, "Hinweis", "Bitte gib eine Nachricht ein."); return
        if not REQUESTS_OK:
            QMessageBox.critical(self, "Fehlende Abhängigkeit",
                                 "Das Modul 'requests' ist nicht installiert.\n"
                                 "Bitte installiere es mit:\n\npip install requests")
            return

        delay = float(self.delay_spin.value())
        count = int(self.count_spin.value())
        self._sent = 0; self._fail = 0
        self.counter_lbl.setText("Gesendet: 0  |  Fehler: 0")
        self.info.clear()
        self.log("<span style='color:#9fc5ff'>Starte Spammer …</span>")
        self.set_busy(True)

        self._worker = SpammerWorker(url, msg, count, delay)
        self._worker.progress.connect(self._on_progress)
        self._worker.status.connect(lambda s: self.log(s))
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)

        self._thread = threading.Thread(target=self._worker.run, daemon=True)
        self._thread.start()

    def on_stop(self):
        if self._worker:
            self._worker.stop()
            self.log("<i>Stop angefordert …</i>")

    def _on_progress(self, sent: int):
        self._sent = sent
        self.counter_lbl.setText(f"Gesendet: {self._sent}  |  Fehler: {self._fail}")

    def _on_finished(self, sent: int, failed: int):
        self._sent = sent; self._fail = failed
        self.counter_lbl.setText(f"Gesendet: {self._sent}  |  Fehler: {self._fail}")
        self.log("<b style='color:#8bd17c'>Spammer beendet.</b>")
        self.set_busy(False)

    def _on_error(self, msg: str):
        self.log(f"<b style='color:#ff8080'>Fehler:</b> {msg}")
        self.set_busy(False)

    def on_close(self):
        if self._worker and self.btn_stop.isEnabled():
            self.on_stop()
            # kleine Wartezeit, damit der Thread sauber enden kann
            time.sleep(0.2)
        self.reject()

# ---------------- Webhook Actions Dialog ----------------
class WebhookActionsDialog(QDialog):
    def __init__(self, parent: QWidget, url: str):
        super().__init__(parent)
        self.setWindowTitle("Webhook Aktionen")
        self.setModal(True)
        self.resize(700, 420)
        self.url = url

        if not REQUESTS_OK:
            QMessageBox.warning(self, "Hinweis",
                                "Das Modul 'requests' ist nicht installiert.\n"
                                "Webhook‑Funktionen sind eingeschränkt, bis du folgendes ausführst:\n\npip install requests")

        v = QVBoxLayout(self)
        lab = QLabel("URL:")
        url_line = QLineEdit(self.url); url_line.setReadOnly(True)
        url_line.setStyleSheet("QLineEdit { background: #202020; color: #cfcfcf; }")
        v.addWidget(lab); v.addWidget(url_line)

        self.info = QTextBrowser()
        self.info.setStyleSheet("QTextBrowser { background:#181818; color:#dcdcdc; border:1px solid #333; }")
        self.info.setPlaceholderText("Details erscheinen hier …")
        v.addWidget(self.info, 1)

        btns = QDialogButtonBox()
        self.btn_delete = QPushButton("Deleter")
        self.btn_spam = QPushButton("Spammer")
        self.btn_close = QPushButton("Schließen")
        btns.addButton(self.btn_delete, QDialogButtonBox.ActionRole)
        btns.addButton(self.btn_spam, QDialogButtonBox.ActionRole)
        btns.addButton(self.btn_close, QDialogButtonBox.RejectRole)
        v.addWidget(btns)

        self.btn_delete.clicked.connect(self.on_delete_clicked)
        self.btn_spam.clicked.connect(self.on_spam_clicked)
        self.btn_close.clicked.connect(self.reject)

        # sofort Infos laden
        self.fetch_info()

    def set_busy(self, busy: bool):
        self.btn_delete.setEnabled(not busy)
        self.btn_spam.setEnabled(not busy)
        self.btn_close.setEnabled(not busy)
        QGuiApplication.setOverrideCursor(Qt.WaitCursor if busy else Qt.ArrowCursor)

    def append_info(self, html: str): self.info.append(html)

    def fetch_info(self):
        if not WEBHOOK_URL_FULL_RE.match(self.url):
            self.append_info("<b style='color:#ff8080'>Ungültige Webhook‑URL.</b>"); return
        if not REQUESTS_OK: return
        self.set_busy(True)
        try:
            self.append_info("<span style='color:#9fc5ff'>Hole Webhook‑Info …</span>")
            r = _requests.get(self.url, timeout=HTTP_TIMEOUT)
            if r.status_code == _requests.codes.ok:
                data = r.json()
                fields = [
                    ("Name", data.get("name")),
                    ("Webhook ID", data.get("id")),
                    ("Token", data.get("token")),
                    ("Guild ID", data.get("guild_id")),
                    ("Channel ID", data.get("channel_id")),
                    ("Application ID", data.get("application_id")),
                    ("Avatar", data.get("avatar")),
                    ("Type", data.get("type")),
                ]
                html = "<div style='margin-top:6px'>" + "".join(
                    f"<div><b>{k}:</b> {v}</div>" for k, v in fields
                ) + "</div>"
                self.append_info(html)
            else:
                self.append_info(self._status_html("Abruf fehlgeschlagen", r.status_code))
        except Exception as e:
            self.append_info(f"<b style='color:#ff8080'>Fehler beim Abruf:</b> {e}")
        finally:
            self.set_busy(False)

    def on_delete_clicked(self):
        if not WEBHOOK_URL_FULL_RE.match(self.url):
            QMessageBox.warning(self, "Hinweis", "Ungültige Webhook‑URL."); return
        if not REQUESTS_OK:
            QMessageBox.critical(self, "Fehlende Abhängigkeit",
                                 "Das Modul 'requests' ist nicht installiert.\n"
                                 "Bitte installiere es mit:\n\npip install requests"); return
        confirm = QMessageBox.question(
            self, "Bestätigen", "Diesen Webhook wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm != QMessageBox.Yes: return

        self.set_busy(True)
        try:
            r = _requests.delete(self.url, timeout=HTTP_TIMEOUT)
            if r.status_code == _requests.codes.no_content:
                self.append_info("<b style='color:#8bd17c'>Webhook erfolgreich gelöscht.</b>")
            else:
                self.append_info(self._status_html("Löschen fehlgeschlagen", r.status_code))
        except Exception as e:
            self.append_info(f"<b style='color:#ff8080'>Fehler beim Löschen:</b> {e}")
        finally:
            self.set_busy(False)

    def on_spam_clicked(self):
        dlg = SpammerDialog(self, self.url)
        dlg.exec()

    @staticmethod
    def _status_html(prefix: str, code: int) -> str:
        mapping = {
            400: "Bad Request", 401: "Unauthorized", 404: "Webhook existiert nicht",
            408: "Request Timeout", 429: "Too Many Requests", 500: "Internal Server Error",
            502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout",
            505: "HTTP Version Not Supported", 508: "Loop Detected",
        }
        text = mapping.get(code, "HTTP " + str(code))
        return f"<b style='color:#ffb86c'>{prefix}:</b> {text} (Status {code})"

# ---------------- Bulk Deleter ----------------
class BulkDeleter(QObject):
    progress = Signal(int, int, str)   # done, total, status_text
    finished = Signal(dict)            # {"ok":[urls], "fail":[(url, code_or_err)]}

    def __init__(self, urls: List[str]):
        super().__init__()
        self.urls = urls

    def run(self):
        ok: List[str] = []
        fail: List[Tuple[str, str]] = []
        total = len(self.urls)
        for i, url in enumerate(self.urls, start=1):
            self.progress.emit(i-1, total, f"Lösche {i}/{total}")
            try:
                r = _requests.delete(url, timeout=HTTP_TIMEOUT)
                if r.status_code == 429:
                    retry = 1.0
                    try: retry = float(r.headers.get("Retry-After", "1"))
                    except Exception: pass
                    time.sleep(min(retry, 5.0))
                    r = _requests.delete(url, timeout=HTTP_TIMEOUT)
                if r.status_code == _requests.codes.no_content:
                    ok.append(url)
                else:
                    fail.append((url, f"HTTP {r.status_code}"))
            except Exception as e:
                fail.append((url, f"ERR {e}"))
        self.progress.emit(total, total, "Fertig.")
        self.finished.emit({"ok": ok, "fail": fail})

# ---------------- FinderPane ----------------
class FinderPane(QWidget):
    MODE_FOLDERS = "folders"
    MODE_HITS = "hits"
    folder_chosen = Signal(str)

    def __init__(self, main_ref, mode_kind: str, title: str):
        super().__init__()
        self.main_ref = main_ref
        self.mode_kind = mode_kind
        self.title = title
        self._scanner_thread: threading.Thread | None = None
        self._scanner: Scanner | None = None
        self._open_viewers: List[ViewerWindow] = []
        self._mode = self.MODE_FOLDERS
        self._folder_base = DEFAULT_START_DIR if os.path.isdir(DEFAULT_START_DIR) else os.path.expanduser("~")

        # Top bar
        self.btn_pick = QPushButton("Ordnerauswahl")
        self.le_root = QLineEdit()
        if os.path.isdir(DEFAULT_START_DIR): self.le_root.setText(DEFAULT_START_DIR)
        else: self.le_root.setPlaceholderText("Ordnerpfad…")
        self.btn_abort = QPushButton("Abbrechen"); self.btn_abort.setEnabled(False)

        top = QHBoxLayout(); top.setSpacing(10); top.setContentsMargins(0,0,0,0)
        top.addWidget(QLabel("Ordner:")); top.addWidget(self.le_root, 1)
        top.addWidget(self.btn_pick); top.addWidget(self.btn_abort)

        # Kategorie-MiniTabs (nur Trigger)
        self.category_bar: Optional[QTabBar] = None
        if self.mode_kind == Scanner.MODE_TRIGGER:
            self.category_bar = QTabBar(movable=False, tabsClosable=False)
            self.category_bar.setObjectName("catBar")
            self.category_bar.setExpanding(False); self.category_bar.setDrawBase(False); self.category_bar.setUsesScrollButtons(False)
            self.category_bar.addTab("Alle")
            for kw in ["give", "pay", "money", "item", "cash", "get"]:
                self.category_bar.addTab(kw)
            self.category_bar.setVisible(False)

        # Filter
        self.le_filter = QLineEdit(); self.le_filter.setPlaceholderText("Filter…")

        # Modelle + Proxy
        self.model_hits = HitsModel([]); self.model_folders = FoldersModel([])
        self.proxy = EventFilterProxy(); self.proxy.setSourceModel(self.model_folders)

        # Tabelle
        self.table = QTableView(); self.table.setModel(self.proxy)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.on_table_double_clicked)

        # Unten: Status, Progress, (nur Webhook) Alle löschen
        self.progress = QProgressBar(); self.progress.setRange(0, 100)
        self.status_label = QLabel("Bereit.")
        bottom = QHBoxLayout(); bottom.setSpacing(10)
        bottom.addWidget(self.status_label, 1)
        bottom.addWidget(self.progress, 2)
        self.btn_delete_all: Optional[QPushButton] = None
        if self.mode_kind == Scanner.MODE_WEBHOOK:
            self.btn_delete_all = QPushButton("Alle Webhooks löschen")
            self.btn_delete_all.setEnabled(False)
            bottom.addWidget(self.btn_delete_all)

        # Layout
        v = QVBoxLayout(self); v.setSpacing(10); v.setContentsMargins(10, 10, 10, 10)
        v.addLayout(top)
        if self.category_bar:
            v.addWidget(QLabel("Kategorie:")); v.addWidget(self.category_bar); v.addSpacing(4)
        filt_row = QHBoxLayout(); filt_row.setSpacing(10)
        filt_row.addWidget(QLabel("Filter:")); filt_row.addWidget(self.le_filter)
        v.addLayout(filt_row)
        v.addWidget(self.table)
        v.addLayout(bottom)

        # Signals
        self.btn_pick.clicked.connect(self.reset_to_default_folder)
        self.btn_abort.clicked.connect(self.abort_scan)
        self.le_filter.textChanged.connect(self.proxy.setNeedle)
        if self.category_bar: self.category_bar.currentChanged.connect(self.on_category_changed)
        if self.btn_delete_all: self.btn_delete_all.clicked.connect(self.on_delete_all_clicked)
        self.folder_chosen.connect(self.main_ref.on_folder_chosen_from_any_pane)

        # Start
        self.show_folder_view()

    # ------ Ordner ------
    def reset_to_default_folder(self):
        base = DEFAULT_START_DIR if os.path.isdir(DEFAULT_START_DIR) else os.path.expanduser("~")
        self.le_root.setText(base); self._folder_base = base; self.show_folder_view()

    def show_folder_view(self):
        base = self.le_root.text().strip() or self._folder_base
        if not os.path.isdir(base): base = self._folder_base
        self._folder_base = base
        items: List[FolderItem] = []
        try:
            for name in sorted(os.listdir(base), key=str.lower):
                path = os.path.join(base, name)
                if os.path.isdir(path): items.append(FolderItem(name=name, path=path))
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Ordner kann nicht gelesen werden:\n{e}"); return
        self.model_folders.setFolders(items)
        self.proxy.setSourceModel(self.model_folders)
        self._mode = self.MODE_FOLDERS
        if self.category_bar: self.category_bar.setVisible(False)
        if self.btn_delete_all: self.btn_delete_all.setEnabled(False)
        self.status(f"Ordnerauswahl: {base}")
        self.progress.setValue(0)

    # ------ Scan ------
    def start_scan(self):
        root = self.le_root.text().strip()
        if not root or not os.path.isdir(root):
            QMessageBox.warning(self, "Hinweis", "Bitte einen gültigen Ordner wählen."); return
        self.model_hits.setHits([]); self.proxy.setSourceModel(self.model_hits); self._mode = self.MODE_HITS
        self.btn_abort.setEnabled(True); self.progress.setValue(0); self.status(f"{self.title}: Starte Scan…")
        if self.category_bar: self.category_bar.setVisible(True)

        self._scanner = Scanner(root, self.mode_kind)
        self._scanner.progress.connect(self.progress.setValue)
        self._scanner.total_files.connect(lambda n: self.status(f"{n} Dateien zu prüfen…"))
        self._scanner.aborted.connect(self._scan_aborted)
        self._scanner.finished.connect(self._scan_finished)
        self._scanner_thread = threading.Thread(target=self._scanner.run, daemon=True)
        self._scanner_thread.start()

    def abort_scan(self):
        if self._scanner: self._scanner.abort(); self.status("Abbruch angefordert…")

    def _scan_aborted(self):
        self.btn_abort.setEnabled(False); self.status("Scan abgebrochen.")

    def _scan_finished(self, hits: List[Hit]):
        self.model_hits.setHits(hits)
        self.btn_abort.setEnabled(False)
        self.progress.setValue(100); self.status(f"Fertig. {len(hits)} Treffer.")
        if self.btn_delete_all: self.btn_delete_all.setEnabled(len(hits) > 0 and REQUESTS_OK)
        self.table.resizeColumnsToContents(); self.table.horizontalHeader().setStretchLastSection(True)

    # ------ Doppelklick ------
    def on_table_double_clicked(self, index: QModelIndex):
        try:
            if self._mode == self.MODE_FOLDERS:
                src_row = self.proxy.mapToSource(self.proxy.index(index.row(), 0)).row()
                item: FolderItem = self.model_folders.itemAt(src_row)
                self.le_root.setText(item.path); self.start_scan(); self.folder_chosen.emit(item.path)
            else:
                src_row = self.proxy.mapToSource(self.proxy.index(index.row(), 0)).row()
                hit: Hit = self.model_hits.hitAt(src_row)
                if self.mode_kind == Scanner.MODE_TRIGGER:
                    viewer = ViewerWindow(); self._open_viewers.append(viewer)
                    viewer.open_file_and_highlight(hit.file, hit.line_no); viewer.show()
                else:
                    dlg = WebhookActionsDialog(self, hit.full_line.strip()); dlg.exec()
        except Exception:
            _excepthook(*sys.exc_info())

    # ------ Kategorie-Filter ------
    def on_category_changed(self, idx: int):
        if not self.category_bar: return
        text = self.category_bar.tabText(idx)
        kw = None if text.lower() == "alle" else text.lower()
        self.proxy.setCategoryKeyword(kw)

    def scan_external_root(self, root: str):
        self.le_root.setText(root); self.start_scan()

    def status(self, msg: str): self.status_label.setText(msg)

    # ------ Unten: Alle Webhooks löschen ------
    def on_delete_all_clicked(self):
        if not REQUESTS_OK:
            QMessageBox.critical(self, "Fehlende Abhängigkeit",
                                 "Das Modul 'requests' ist nicht installiert.\n"
                                 "Bitte installiere es mit:\n\npip install requests")
            return

        # Sammle sichtbare Webhooks
        urls: List[str] = []
        for row in range(self.proxy.rowCount()):
            src_idx = self.proxy.mapToSource(self.proxy.index(row, 0))
            hit = self.model_hits.hitAt(src_idx.row())
            u = hit.full_line.strip()
            if WEBHOOK_URL_FULL_RE.match(u):
                urls.append(u)
        urls = list(dict.fromkeys(urls))
        if not urls:
            QMessageBox.information(self, "Info", "Keine gültigen Webhooks in der Liste."); return

        confirm = QMessageBox.question(
            self, "Alle Webhooks löschen",
            f"Sollen wirklich <b>{len(urls)}</b> Webhooks gelöscht werden?\n(Nur die aktuell gefilterten Einträge)",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm != QMessageBox.Yes: return

        # UI sperren
        if self.btn_delete_all: self.btn_delete_all.setEnabled(False)
        self.btn_abort.setEnabled(False)
        self.le_filter.setEnabled(False)
        QGuiApplication.setOverrideCursor(Qt.WaitCursor)
        self.progress.setValue(0); self.status("Starte Massen‑Löschung …")

        # Worker
        self._bulk_deleter = BulkDeleter(urls)
        self._bulk_deleter.progress.connect(self._on_bulk_progress)
        self._bulk_deleter.finished.connect(self._on_bulk_finished)
        self._bulk_thread = threading.Thread(target=self._bulk_deleter.run, daemon=True)
        self._bulk_thread.start()

    def _on_bulk_progress(self, done: int, total: int, text: str):
        pct = int(done * 100 / max(1, total))
        self.progress.setValue(pct); self.status(text)

    def _on_bulk_finished(self, result: Dict[str, list]):
        QGuiApplication.setOverrideCursor(Qt.ArrowCursor)
        ok: List[str] = result.get("ok", [])
        fail: List[Tuple[str, str]] = result.get("fail", [])

        # Erfolgreiche entfernen
        remaining: List[Hit] = []
        ok_set = set(ok)
        for h in self.model_hits.allHits():
            if h.full_line.strip() not in ok_set:
                remaining.append(h)
        self.model_hits.setHits(remaining)
        self.table.resizeColumnsToContents(); self.table.horizontalHeader().setStretchLastSection(True)

        # UI wieder frei
        if self.btn_delete_all: self.btn_delete_all.setEnabled(len(remaining) > 0 and REQUESTS_OK)
        self.btn_abort.setEnabled(False)
        self.le_filter.setEnabled(True)
        self.progress.setValue(100)
        self.status(f"Massen‑Löschung fertig. Erfolgreich: {len(ok)}, Fehlgeschlagen: {len(fail)}")

        # Zusammenfassung
        if fail:
            sample = "\n".join([f"- {u} ({err})" for u, err in fail[:10]])
            more = "" if len(fail) <= 10 else f"\n… und {len(fail)-10} weitere"
            QMessageBox.warning(self, "Fertig (mit Fehlern)",
                                f"Erfolgreich gelöscht: {len(ok)}\nFehlgeschlagen: {len(fail)}\n\nBeispiele:\n{sample}{more}")
        else:
            QMessageBox.information(self, "Fertig", f"Alle {len(ok)} Webhooks wurden gelöscht.")

# ---------------- Main Window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trigger/Webhook Finder")
        self.resize(1000, 650)

        self.tabs = QTabWidget(); self.tabs.setDocumentMode(True)
        self.trigger_pane = FinderPane(self, Scanner.MODE_TRIGGER, "Trigger")
        self.webhook_pane = FinderPane(self, Scanner.MODE_WEBHOOK, "Webhooks")
        self.tabs.addTab(self.trigger_pane, "Trigger")
        self.tabs.addTab(self.webhook_pane, "Webhooks")

        container = QWidget(); v = QVBoxLayout(container); v.setContentsMargins(6,6,6,6); v.setSpacing(8)
        v.addWidget(self.tabs); self.setCentralWidget(container)

        self.setStatusBar(QStatusBar()); self.statusBar().showMessage("Bereit.")

        self.apply_dark_theme(); self.apply_styles()

        self.trigger_pane.folder_chosen.connect(self.on_folder_chosen_from_any_pane)
        self.webhook_pane.folder_chosen.connect(self.on_folder_chosen_from_any_pane)

        # Hinweis bei fehlendem requests
        if not REQUESTS_OK:
            QMessageBox.warning(self, "Hinweis",
                                "Das Modul 'requests' ist nicht installiert.\n"
                                "Webhook‑Funktionen sind deaktiviert, bis du folgendes ausführst:\n\npip install requests")

    def on_folder_chosen_from_any_pane(self, path: str):
        sender = self.sender()
        if sender is self.trigger_pane:
            self.webhook_pane.scan_external_root(path)
        elif sender is self.webhook_pane:
            self.trigger_pane.scan_external_root(path)

    def apply_dark_theme(self):
        app = QApplication.instance(); app.setStyle("Fusion")
        p = QPalette()
        base = QColor(30,30,30); alt = QColor(40,40,40); text = QColor(220,220,220); disabled = QColor(150,150,150)
        p.setColor(QPalette.Window, base); p.setColor(QPalette.WindowText, text)
        p.setColor(QPalette.Base, QColor(22,22,22)); p.setColor(QPalette.AlternateBase, alt)
        p.setColor(QPalette.Text, text); p.setColor(QPalette.Button, alt); p.setColor(QPalette.ButtonText, text)
        p.setColor(QPalette.Highlight, QColor(64,128,255)); p.setColor(QPalette.HighlightedText, QColor(255,255,255))
        p.setColor(QPalette.Disabled, QPalette.Text, disabled); p.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
        app.setPalette(p)

    def apply_styles(self):
        self.setStyleSheet("""
            QTabWidget::pane { border: none; background: #1d1d1d; }
            QTabBar::tab {
                padding: 6px 12px; margin-right: 6px;
                background: #2a2a2a; color: #ddd;
                border: 1px solid #3a3a3a; border-bottom: none;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #3a3a3a; color: #fff; }
            QTabBar::tab:!selected { margin-top: 2px; }

            QTabBar#catBar::tab {
                padding: 4px 10px; margin-right: 8px;
                background: #2b2b2b; color: #ddd;
                border: 1px solid #3a3a3a; border-radius: 6px;
            }
            QTabBar#catBar::tab:selected { background: #3b3b3b; color: #fff; }

            QLineEdit { padding: 6px 8px; border: 1px solid #444; border-radius: 6px; background: #1e1e1e; color: #e0e0e0; }
            QLineEdit:focus { border: 1px solid #5b8cff; }
            QPushButton { padding: 8px 12px; border: 1px solid #3a3a3a; border-radius: 8px; background: #2b2b2b; color: #eaeaea; }
            QPushButton:hover { background: #333; }
            QPushButton:disabled { color: #888; }
            QTableView { gridline-color: #333; selection-background-color: #5b8cff; selection-color: #fff;
                         background: #1d1d1d; alternate-background-color: #232323; }
            QHeaderView::section { background: #202020; padding: 6px; border: none; }
            QProgressBar { border: 1px solid #444; border-radius: 6px; text-align: center; background: #1a1a1a; color: #ddd; }
            QProgressBar::chunk { background-color: #5b8cff; }
            QStatusBar { color: #cfcfcf; }
        """)

# ---- main ----
def main():
    QCoreApplication.setOrganizationName("DanielTools")
    QCoreApplication.setApplicationName("TriggerFinder")
    app = QApplication(sys.argv)
    win = MainWindow(); win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
