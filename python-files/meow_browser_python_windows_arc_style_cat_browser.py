"""
MeowBrowser — Arc‑style, cat‑themed, Chromium‑based browser in Python (Windows)
==============================================================================

Quick start (Windows):
1) Install Python 3.11+ (add to PATH).
2) In Terminal (PowerShell or cmd):
   pip install PySide6 PySide6-Addons PySide6-Essentials
3) Run:  python meowbrowser.py
4) Package (optional):
   pip install pyinstaller
   pyinstaller -F -w meowbrowser.py

Notes:
- Uses Qt WebEngine (Chromium under the hood) via PySide6.
- Arc‑like layout: left Spaces bar, middle vertical Tabs for each Space, right main page.
- Cat theme, soft blur, large rounded corners. Meow.
- Persists spaces/tabs to %APPDATA%/MeowBrowser/session.json.

© 2025 KyrKat & ChatGPT — MIT License
"""
from __future__ import annotations

import json
import os
import sys
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QListWidgetItem, QStackedWidget,
    QFrame, QLabel, QFileDialog, QMessageBox, QMenu
)
from PySide6.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineDownloadRequest

APP_NAME = "MeowBrowser"
CAT = "🐱"

# --------------------------- Utilities & Persistence ---------------------------

def appdata_dir() -> Path:
    base = os.getenv("APPDATA") or str(Path.home() / ".config")
    d = Path(base) / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d

SESSION_FILE = appdata_dir() / "session.json"

@dataclass
class TabState:
    title: str = "New Tab"
    url: str = "https://duckduckgo.com/"

@dataclass
class SpaceState:
    name: str = "Space"
    icon: str = CAT
    tabs: List[TabState] = field(default_factory=lambda: [TabState()])
    active_tab_index: int = 0

@dataclass
class SessionState:
    spaces: List[SpaceState] = field(default_factory=lambda: [
        SpaceState(name="Home", icon="🏠"),
        SpaceState(name="Study", icon="📚"),
        SpaceState(name="Fun", icon="🎮"),
    ])
    active_space_index: int = 0

    @staticmethod
    def load() -> "SessionState":
        if SESSION_FILE.exists():
            try:
                data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
                spaces = []
                for s in data.get("spaces", []):
                    tabs = [TabState(**t) for t in s.get("tabs", [])]
                    spaces.append(SpaceState(
                        name=s.get("name", "Space"),
                        icon=s.get("icon", CAT),
                        tabs=tabs or [TabState()],
                        active_tab_index=int(s.get("active_tab_index", 0))
                    ))
                return SessionState(
                    spaces=spaces or SessionState().spaces,
                    active_space_index=int(data.get("active_space_index", 0))
                )
            except Exception:
                pass
        return SessionState()

    def save(self) -> None:
        data = {
            "spaces": [
                {
                    "name": s.name,
                    "icon": s.icon,
                    "tabs": [{"title": t.title, "url": t.url} for t in s.tabs],
                    "active_tab_index": s.active_tab_index,
                }
                for s in self.spaces
            ],
            "active_space_index": self.active_space_index,
        }
        SESSION_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# --------------------------- Core UI Components ---------------------------

class UrlBar(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Type URL or search… meow 🐾")
        self.setClearButtonEnabled(True)
        self.setMinimumHeight(36)
        self.setStyleSheet("""
            QLineEdit { padding: 8px 12px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.15);
                        background: rgba(255,255,255,0.08); color: white; selection-background-color: #9c88ff; }
        """)

class Toolbar(QWidget):
    navigate = QtCore.Signal(str)
    go_back = QtCore.Signal()
    go_forward = QtCore.Signal()
    reload = QtCore.Signal()
    new_tab = QtCore.Signal()

    def __init__(self):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(8)

        def btn(txt: str, tip: str) -> QPushButton:
            b = QPushButton(txt)
            b.setToolTip(tip)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedHeight(34)
            b.setStyleSheet("""
                QPushButton { border-radius: 12px; padding: 6px 10px; background: rgba(255,255,255,0.08); color: white; }
                QPushButton:hover { background: rgba(255,255,255,0.14); }
                QPushButton:pressed { background: rgba(255,255,255,0.2); }
            """)
            return b

        self.back = btn("⟵", "Back")
        self.fwd = btn("⟶", "Forward")
        self.refresh = btn("⟳", "Reload")
        self.add = btn("＋", "New Tab (meow)")
        self.cat = btn(CAT, "Meow Menu")

        self.url = UrlBar()

        lay.addWidget(self.back)
        lay.addWidget(self.fwd)
        lay.addWidget(self.refresh)
        lay.addWidget(self.url, 1)
        lay.addWidget(self.add)
        lay.addWidget(self.cat)

        self.back.clicked.connect(self.go_back)
        self.fwd.clicked.connect(self.go_forward)
        self.refresh.clicked.connect(self.reload)
        self.add.clicked.connect(self.new_tab)
        self.url.returnPressed.connect(self._nav)

    def _nav(self):
        self.navigate.emit(self.url.text())

class VerticalTabs(QWidget):
    currentChanged = QtCore.Signal(int)
    closeRequested = QtCore.Signal(int)

    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setUniformItemSizes(True)
        self.list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list.setStyleSheet("""
            QListWidget { background: transparent; color: white; border: none; }
            QListWidget::item { padding: 10px; margin: 2px 0; border-radius: 12px; }
            QListWidget::item:selected { background: rgba(255,255,255,0.18); }
            QListWidget::item:hover { background: rgba(255,255,255,0.12); }
        """)
        self.new_btn = QPushButton("＋ New Tab")
        self.new_btn.setCursor(Qt.PointingHandCursor)
        self.new_btn.setStyleSheet("QPushButton{border-radius:12px;padding:10px;color:white;background:rgba(255,255,255,0.08);} QPushButton:hover{background:rgba(255,255,255,0.14);}")
        lay.addWidget(self.list, 1)
        lay.addWidget(self.new_btn)
        self.list.currentRowChanged.connect(self.currentChanged)
        self.new_btn.clicked.connect(lambda: self.currentChanged.emit(-1))
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._menu)

    def _menu(self, pos):
        row = self.list.currentRow()
        if row < 0: return
        menu = QMenu(self)
        act_close = menu.addAction("Close Tab")
        act_dup = menu.addAction("Duplicate Tab")
        act = menu.exec(self.list.mapToGlobal(pos))
        if act == act_close:
            self.closeRequested.emit(row)
        elif act == act_dup:
            self.currentChanged.emit(row | (1<<16))  # signal special dup

    def add_tab(self, title: str):
        item = QListWidgetItem(title)
        item.setToolTip(title)
        self.list.addItem(item)
        self.list.setCurrentItem(item)

    def set_title(self, index: int, title: str):
        it = self.list.item(index)
        if it:
            it.setText(title)
            it.setToolTip(title)

    def remove(self, index: int):
        it = self.list.takeItem(index)
        del it

class SpaceBar(QWidget):
    spaceChanged = QtCore.Signal(int)
    addSpaceRequested = QtCore.Signal()

    def __init__(self, session: SessionState):
        super().__init__()
        self.session = session
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)
        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget { background: transparent; color: white; border: none; }
            QListWidget::item { padding: 10px; margin: 4px 0; border-radius: 16px; }
            QListWidget::item:selected { background: rgba(255,255,255,0.18); }
            QListWidget::item:hover { background: rgba(255,255,255,0.12); }
        """)
        self.add_btn = QPushButton("＋")
        self.add_btn.setToolTip("New Space")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFixedSize(40, 40)
        self.add_btn.setStyleSheet("QPushButton{border-radius:14px;color:white;background:rgba(255,255,255,0.08);} QPushButton:hover{background:rgba(255,255,255,0.14);}")

        lay.addWidget(self.list, 1)
        lay.addWidget(self.add_btn, 0, alignment=Qt.AlignHCenter)

        self.list.currentRowChanged.connect(self.spaceChanged)
        self.add_btn.clicked.connect(self.addSpaceRequested)

    def refresh(self):
        self.list.clear()
        for s in self.session.spaces:
            item = QListWidgetItem(f"{s.icon}  {s.name}")
            self.list.addItem(item)
        self.list.setCurrentRow(self.session.active_space_index)

# --------------------------- WebView & Pages ---------------------------

class MeowWebView(QWebEngineView):
    titleChangedForTab = QtCore.Signal(str)

    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(parent)
        self.setPage(self.page())
        self.setZoomFactor(1.0)
        self.profile = profile
        self.setPage(self.profile.instantiatedPage()) if hasattr(self.profile, 'instantiatedPage') else None
        self.titleChanged.connect(self.titleChangedForTab)
        self.downloadRequested.connect(self._on_download)

    def _on_download(self, item: QWebEngineDownloadRequest):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", item.downloadFileName())
        if path:
            item.setDownloadFileName(Path(path).name)
            item.setPath(path)
            item.accept()

# --------------------------- Main Window ---------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{CAT} MeowBrowser — Arc‑style Browser")
        self.resize(1400, 900)
        self._apply_theme()

        self.session = SessionState.load()

        # Shared web profile for disk cache/cookies per app (Chromium)
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setCachePath(str(appdata_dir() / "Cache"))
        self.profile.setPersistentStoragePath(str(appdata_dir() / "Storage"))

        # Layout: SpaceBar | VerticalTabs | Content
        root = QWidget()
        root_lay = QHBoxLayout(root)
        root_lay.setContentsMargins(12, 12, 12, 12)
        root_lay.setSpacing(12)

        # Panels
        self.spacebar = SpaceBar(self.session)
        self.tabs_panel = VerticalTabs()
        self.content = QStackedWidget()

        # Toolbar on top of content
        content_wrap = QVBoxLayout()
        content_wrap.setContentsMargins(0, 0, 0, 0)
        content_wrap.setSpacing(8)
        self.toolbar = Toolbar()
        content_container = QWidget()
        content_container.setLayout(self.content)
        content_wrap.addWidget(self.toolbar)
        content_wrap.addWidget(content_container, 1)
        content_widget = QWidget()
        content_widget.setLayout(content_wrap)

        # Add panels to root
        left_frame = self._glass_panel(self.spacebar, width=200)
        mid_frame = self._glass_panel(self.tabs_panel, width=220)
        right_frame = self._glass_panel(content_widget)

        root_lay.addWidget(left_frame, 0)
        root_lay.addWidget(mid_frame, 0)
        root_lay.addWidget(right_frame, 1)
        self.setCentralWidget(root)

        # Wire signals
        self.spacebar.spaceChanged.connect(self._on_space_changed)
        self.spacebar.addSpaceRequested.connect(self._add_space)
        self.tabs_panel.currentChanged.connect(self._on_tab_changed)
        self.tabs_panel.closeRequested.connect(self._close_tab)
        self.toolbar.navigate.connect(self._navigate_from_bar)
        self.toolbar.go_back.connect(lambda: self._current_view().back() if self._current_view() else None)
        self.toolbar.go_forward.connect(lambda: self._current_view().forward() if self._current_view() else None)
        self.toolbar.reload.connect(lambda: self._current_view().reload() if self._current_view() else None)
        self.toolbar.new_tab.connect(lambda: self._new_tab(self.session.active_space_index))

        # Shortcuts
        self._mk_shortcut("Ctrl+L", lambda: self.toolbar.url.setFocus())
        self._mk_shortcut("Ctrl+T", lambda: self._new_tab(self.session.active_space_index))
        self._mk_shortcut("Ctrl+W", lambda: self._close_tab(self._active_tab_index()))
        self._mk_shortcut("Ctrl+Tab", self._next_tab)
        self._mk_shortcut("Ctrl+Shift+Tab", self._prev_tab)

        # Populate UI from session
        self.spacebar.refresh()
        self._load_space(self.session.active_space_index)

        # Meow easter egg
        self.toolbar.cat.clicked.connect(self._meow_menu)

    # ---------- Helpers ----------

    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f0f13; }
            QWidget#Glass { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; }
            QLabel, QLineEdit, QListWidget, QPushButton { font-size: 14px; }
            QToolTip { color: white; background: rgba(0,0,0,0.7); border: 1px solid rgba(255,255,255,0.15); }
        """)
        app.setWindowIcon(QIcon.fromTheme("applications-internet"))

    def _glass_panel(self, inner: QWidget, width: Optional[int]=None) -> QFrame:
        frame = QFrame()
        frame.setObjectName("Glass")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(12,12,12,12)
        lay.addWidget(inner)
        if width: frame.setFixedWidth(width)
        return frame

    def _mk_shortcut(self, seq: str, func):
        sc = QAction(self)
        sc.setShortcut(QKeySequence(seq))
        sc.triggered.connect(func)
        self.addAction(sc)

    def _sanitize(self, text: str) -> str:
        text = text.strip()
        if not text:
            return "https://duckduckgo.com/"
        # Prepend scheme if missing
        if re.match(r"^[a-zA-Z]+://", text):
            return text
        if "." in text and " " not in text:
            return "https://" + text
        # Treat as search
        return "https://duckduckgo.com/?q=" + QtCore.QUrl.toPercentEncoding(text).data().decode()

    def _current_view(self) -> Optional[MeowWebView]:
        w = self.content.currentWidget()
        return w if isinstance(w, MeowWebView) else None

    def _active_tab_index(self) -> int:
        s = self.session.spaces[self.session.active_space_index]
        return s.active_tab_index

    def _set_active_tab_index(self, idx: int):
        s = self.session.spaces[self.session.active_space_index]
        s.active_tab_index = max(0, min(idx, len(s.tabs)-1))

    # ---------- Session <-> UI ----------

    def _load_space(self, i: int):
        self.session.active_space_index = max(0, min(i, len(self.session.spaces)-1))
        self.tabs_panel.list.clear()
        self.content.clear()
        space = self.session.spaces[self.session.active_space_index]
        for tab in space.tabs:
            self._materialize_tab(tab)
        self.tabs_panel.list.setCurrentRow(space.active_tab_index)
        self._sync_urlbar()
        self.session.save()

    def _materialize_tab(self, tab: TabState):
        self.tabs_panel.add_tab(tab.title)
        view = MeowWebView(self.profile)
        view.titleChangedForTab.connect(self._update_current_tab_title)
        view.load(QUrl(tab.url))
        self.content.addWidget(view)

    def _update_current_tab_title(self, title: str):
        idx = self.content.currentIndex()
        self.tabs_panel.set_title(idx, title or "(no title)")
        # Update state
        s = self.session.spaces[self.session.active_space_index]
        if 0 <= idx < len(s.tabs):
            s.tabs[idx].title = title or s.tabs[idx].title
        self.session.save()
        self.setWindowTitle(f"{CAT} MeowBrowser — {title[:60]}")

    def _on_space_changed(self, i: int):
        if i < 0: return
        self._load_space(i)

    def _add_space(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "New Space", "Space name:", text="New Space")
        if not ok or not name.strip():
            return
        icon, ok2 = QtWidgets.QInputDialog.getText(self, "New Space Icon", "Emoji/Icon:", text=CAT)
        if not ok2 or not icon.strip():
            icon = CAT
        self.session.spaces.append(SpaceState(name=name.strip(), icon=icon.strip()))
        self.spacebar.refresh()
        self._load_space(len(self.session.spaces)-1)

    def _on_tab_changed(self, raw_index: int):
        # raw_index == -1 means add new; high-bit flag means duplicate
        dup = False
        if raw_index >= (1<<16):
            dup = True
            index = raw_index & ((1<<16)-1)
        else:
            index = raw_index

        space = self.session.spaces[self.session.active_space_index]
        if index == -1:
            self._new_tab(self.session.active_space_index)
            return
        if 0 <= index < len(space.tabs):
            self._set_active_tab_index(index)
            self.content.setCurrentIndex(index)
            self._sync_urlbar()
            if dup:
                tab = space.tabs[index]
                space.tabs.insert(index+1, TabState(title=tab.title+" (copy)", url=tab.url))
                view = MeowWebView(self.profile)
                view.titleChangedForTab.connect(self._update_current_tab_title)
                view.load(QUrl(tab.url))
                self.content.insertWidget(index+1, view)
                self.tabs_panel.list.insertItem(index+1, QListWidgetItem(tab.title+" (copy)"))
                self.tabs_panel.list.setCurrentRow(index+1)
            self.session.save()

    def _close_tab(self, index: int):
        space = self.session.spaces[self.session.active_space_index]
        if not (0 <= index < len(space.tabs)):
            return
        if len(space.tabs) == 1:
            # Replace last tab with a fresh one
            space.tabs[0] = TabState()
            self.content.removeWidget(self.content.widget(0))
            view = MeowWebView(self.profile)
            view.titleChangedForTab.connect(self._update_current_tab_title)
            view.load(QUrl(space.tabs[0].url))
            self.content.insertWidget(0, view)
            self.tabs_panel.set_title(0, "New Tab")
            self.tabs_panel.list.setCurrentRow(0)
        else:
            space.tabs.pop(index)
            w = self.content.widget(index)
            self.content.removeWidget(w)
            w.deleteLater()
            self.tabs_panel.remove(index)
            self._set_active_tab_index(max(0, index-1))
            self.content.setCurrentIndex(self._active_tab_index())
            self.tabs_panel.list.setCurrentRow(self._active_tab_index())
        self._sync_urlbar()
        self.session.save()

    def _new_tab(self, space_index: int, url: str = "https://start.duckduckgo.com/"):
        space = self.session.spaces[space_index]
        space.tabs.append(TabState(url=url))
        view = MeowWebView(self.profile)
        view.titleChangedForTab.connect(self._update_current_tab_title)
        view.load(QUrl(url))
        self.content.addWidget(view)
        self.tabs_panel.add_tab("New Tab")
        self.tabs_panel.list.setCurrentRow(self.content.count()-1)
        self._set_active_tab_index(self.content.count()-1)
        self._sync_urlbar()
        self.session.save()

    def _navigate_from_bar(self, text: str):
        url = self._sanitize(text)
        view = self._current_view()
        if view:
            view.load(QUrl(url))
            # Update state
            s = self.session.spaces[self.session.active_space_index]
            s.tabs[self._active_tab_index()].url = url
            self.session.save()

    def _sync_urlbar(self):
        view = self._current_view()
        if not view:
            self.toolbar.url.setText("")
            return
        self.toolbar.url.setText(view.url().toString())

    def _next_tab(self):
        s = self.session.spaces[self.session.active_space_index]
        if not s.tabs: return
        idx = (self._active_tab_index() + 1) % len(s.tabs)
        self.tabs_panel.list.setCurrentRow(idx)

    def _prev_tab(self):
        s = self.session.spaces[self.session.active_space_index]
        if not s.tabs: return
        idx = (self._active_tab_index() - 1) % len(s.tabs)
        self.tabs_panel.list.setCurrentRow(idx)

    def _meow_menu(self):
        m = QMenu(self)
        m.addAction("New Tab (Meow)", lambda: self._new_tab(self.session.active_space_index))
        m.addAction("New Space", self._add_space)
        m.addSeparator()
        m.addAction("Open File…", self._open_file)
        m.addAction("Save Session Now", self.session.save)
        m.addSeparator()
        m.addAction("About MeowBrowser", self._about)
        m.addAction("Exit", self.close)
        m.exec(QtGui.QCursor.pos())

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open HTML", "", "HTML Files (*.html *.htm);;All Files (*.*)")
        if path:
            self._new_tab(self.session.active_space_index, QUrl.fromLocalFile(path).toString())

    def _about(self):
        QMessageBox.information(self, "About MeowBrowser",
            f"""
{CAT} MeowBrowser
Arc‑style, cat‑themed, Chromium‑powered browser.

— Spaces on the left, vertical tabs in the middle.
— URL bar with search, keyboard shortcuts: Ctrl+L, Ctrl+T, Ctrl+W.
— Session persistence to your profile.

Made with purr‑pose for KyrKat.
            """)

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        self.session.save()
        return super().closeEvent(e)

# --------------------------- App Entry ---------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # High‑DPI & font rendering improvements
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    QtGui.QFontDatabase.addApplicationFontFromData(b"")  # placeholder to allow custom fonts later
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
