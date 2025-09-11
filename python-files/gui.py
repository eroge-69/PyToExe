#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cyber Force – Risk Posture Diff (Qualys) — GUI (GRC-focused, production ready)
- Premium header (small logo, airy). Responsive re-flow + elided text (no overlaps).
- Sidebar navigation; Dashboard (3 charts), Compare (titled sections), Findings, Hosts, Summary (grouped KPIs + pie).
- Export: Excel, CSV bundle, and PDF (Executive Summary).  ✔ Fixed logo-in-PDF error.
"""

from __future__ import annotations
import sys, warnings, traceback, datetime
from pathlib import Path
import pandas as pd

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSize
from PySide6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QFontMetrics, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel,
    QPushButton, QToolButton, QFileDialog, QLineEdit, QComboBox, QSplitter,
    QListWidget, QListWidgetItem, QTabWidget, QTableView, QMessageBox,
    QProgressBar, QDialog, QFormLayout, QTextEdit, QStyle, QMenu, QSizePolicy,
    QGraphicsDropShadowEffect
)

# Charts
MPL_AVAILABLE = True
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib import image as mpimg
except Exception:
    MPL_AVAILABLE = False

APP_NAME    = "Cyber Force – Risk Posture Diff (Qualys)"
APP_VERSION = "v3.5.0"

# Silence XML-as-HTML warning in GUI (from bs4 when parsing XHTML reports)
try:
    from bs4.builder import XMLParsedAsHTMLWarning  # type: ignore
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
except Exception:
    warnings.filterwarnings("ignore", message="XMLParsedAsHTMLWarning")

# Import real parser
try:
    import CLI
except Exception as e:
    CLI = None
    _cli_import_error = e

# ---------- Helpers ----------
def find_logo() -> str:
    for p in ("logo.png", "assets/logo.png"):
        if Path(p).exists():
            return p
    return ""

def df_or_empty(df: pd.DataFrame | None) -> pd.DataFrame:
    return df if df is not None else pd.DataFrame()

def pct(n, d) -> str:
    if not d: return "0.0%"
    try: return f"{(100.0*float(n)/float(d)):.1f}%"
    except Exception: return "0.0%"

def safe_sum(df: pd.DataFrame | None, col: str) -> int:
    if df is None or df.empty or col not in df.columns: return 0
    return int(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())

# ---------- Eliding label ----------
class ElideLabel(QLabel):
    def __init__(self, text="", parent=None, mode=Qt.ElideRight):
        super().__init__(text, parent)
        self._full = text
        self._mode = mode
        self.setToolTip(text)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    def setText(self, text: str):
        self._full = text or ""
        self.setToolTip(self._full)
        super().setText(self._elided())
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        super().setText(self._elided())
    def _elided(self):
        fm = QFontMetrics(self.font())
        return fm.elidedText(self._full, self._mode, max(10, self.width()-2))

# ---------- Pandas → Qt Model ----------
class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df.copy()
    def setDataFrame(self, df: pd.DataFrame):
        self.beginResetModel(); self._df = df.copy(); self.endResetModel()
    def rowCount(self, parent=QModelIndex()):  return 0 if self._df is None else len(self._df.index)
    def columnCount(self, parent=QModelIndex()): return 0 if self._df is None else len(self._df.columns)
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or self._df is None: return None
        if role in (Qt.DisplayRole, Qt.ToolTipRole):
            v = self._df.iat[index.row(), index.column()]
            return "" if pd.isna(v) else str(v)
        return None
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if self._df is None or role != Qt.DisplayRole: return None
        return str(self._df.columns[section]) if orientation == Qt.Horizontal else str(section+1)
    def df(self): return self._df

# ---------- Details Dialog ----------
class RowDialog(QDialog):
    def __init__(self, title: str, row: pd.Series, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title); self.setMinimumWidth(640)
        form = QFormLayout(self)
        for key, val in row.items():
            if isinstance(val, float) and pd.isna(val): val = ""
            text = QTextEdit(str(val)); text.setReadOnly(True); text.setFixedHeight(56)
            form.addRow(QLabel(f"<b>{key}</b>"), text)
        btn = QPushButton("Close"); btn.clicked.connect(self.accept)
        form.addRow(btn)

# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(1320, 900)
        if find_logo(): self.setWindowIcon(QIcon(find_logo()))

        # State
        self.old_file: Path|None = None
        self.new_file: Path|None = None
        self.results: dict|None = None
        self.hosts_old: pd.DataFrame|None = None
        self.hosts_new: pd.DataFrame|None = None
        self.dark = True

        self._build_ui()
        self._apply_style()

        if CLI is None:
            QMessageBox.critical(self, "CLI.py not found",
                f"Unable to import CLI.py\n\n{_cli_import_error}\n\n"
                "Place gui.py, CLI.py and logo.png in the same folder.")
            self.parse_btn.setEnabled(False)
            self.export_menu_btn.setEnabled(False)

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        # ========= Header =========
        header = QFrame(); header.setObjectName("Header")
        hwrap = QHBoxLayout(header); hwrap.setContentsMargins(0,0,0,0); hwrap.setSpacing(0)

        self.header_inner = QFrame(); self.header_inner.setObjectName("HeaderInner"); self.header_inner.setProperty("maxw", True)
        hin = QHBoxLayout(self.header_inner); hin.setContentsMargins(20,14,20,14); hin.setSpacing(16)

        # add soft shadow so header pops
        hdr_shadow = QGraphicsDropShadowEffect(self)
        hdr_shadow.setBlurRadius(28); hdr_shadow.setXOffset(0); hdr_shadow.setYOffset(10)
        hdr_shadow.setColor(QColor(0, 0, 0, 150))
        self.header_inner.setGraphicsEffect(hdr_shadow)

        # Left: logo + title (elided)
        logo_lbl = QLabel()
        if find_logo():
            logo_lbl.setPixmap(QPixmap(find_logo()).scaled(QSize(32, 32), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_lbl.setPixmap(self.style().standardIcon(QStyle.SP_ComputerIcon).pixmap(28, 28))
        self.title_lbl = ElideLabel(f"{APP_NAME} — {APP_VERSION}")
        self.title_lbl.setObjectName("Title")
        self.left_box = QWidget(); leftwrap = QHBoxLayout(self.left_box); leftwrap.setSpacing(10)
        self.left_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        leftwrap.addWidget(logo_lbl); leftwrap.addWidget(self.title_lbl)

        # Center: chips + Parse
        self.old_chip = QPushButton("OLD: Select…"); self.old_chip.setObjectName("Chip"); self.old_chip.clicked.connect(self._pick_old)
        self.new_chip = QPushButton("NEW: Select…"); self.new_chip.setObjectName("Chip"); self.new_chip.clicked.connect(self._pick_new)
        self.parse_btn = QPushButton("Parse"); self.parse_btn.setProperty("accent", True); self.parse_btn.setObjectName("Primary"); self.parse_btn.clicked.connect(self._parse_files)
        self.center_box = QWidget(); centerwrap = QHBoxLayout(self.center_box); centerwrap.setSpacing(10)
        self.center_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        centerwrap.addWidget(self.old_chip); centerwrap.addWidget(self.new_chip); centerwrap.addWidget(self.parse_btn)

        # Right: search grows; export + theme fixed
        self.search_global = QLineEdit(); self.search_global.setPlaceholderText("Quick search (QID / Title / CVE)")
        self.search_global.textChanged.connect(self._global_search)
        self.search_global.setMinimumWidth(360)

        self.export_menu_btn = QToolButton(); self.export_menu_btn.setText("Export ▾")
        m = QMenu(self)
        act_xlsx = QAction("Excel (.xlsx)", self); act_xlsx.triggered.connect(self._export_excel)
        act_csv  = QAction("CSV bundle", self);  act_csv.triggered.connect(self._export_csvs)
        act_pdf  = QAction("PDF — Executive Summary", self); act_pdf.triggered.connect(self._export_pdf)
        m.addAction(act_xlsx); m.addAction(act_csv); m.addAction(act_pdf)
        self.export_menu_btn.setMenu(m); self.export_menu_btn.setPopupMode(QToolButton.InstantPopup)

        self.theme_btn = QToolButton(); self.theme_btn.setText("Theme"); self.theme_btn.clicked.connect(self._toggle_theme)

        for b in (self.old_chip, self.new_chip, self.parse_btn, self.export_menu_btn, self.theme_btn):
            b.setMinimumHeight(38)
            b.setCursor(Qt.PointingHandCursor)

        self.right_box = QWidget(); rightwrap = QHBoxLayout(self.right_box); rightwrap.setSpacing(10)
        self.right_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        rightwrap.addWidget(self.search_global, 1)
        rightwrap.addWidget(self.export_menu_btn, 0)
        rightwrap.addWidget(self.theme_btn, 0)

        # Compose header (left 2 / center 3 / right 6)
        hin.addWidget(self.left_box,   2)
        hin.addWidget(self.center_box, 3, alignment=Qt.AlignCenter)
        hin.addWidget(self.right_box,  6)

        outer = QHBoxLayout(); outer.setContentsMargins(0,0,0,0)
        outer.addStretch(1); outer.addWidget(self.header_inner, 1); outer.addStretch(1)
        hwrap.addLayout(outer)

        # ========= Body (Sidebar + Content) =========
        split = QSplitter(Qt.Horizontal)

        content = QFrame(); content_v = QVBoxLayout(content); content_v.setContentsMargins(12,12,12,12); content_v.setSpacing(12)
        self.tabs = QTabWidget(); self.tabs.tabBar().hide()
        self.tabs.addTab(self._build_dashboard(), "Dashboard")
        self.tabs.addTab(self._build_compare(),   "Compare")
        self.tabs.addTab(self._build_findings(),  "Findings")
        self.tabs.addTab(self._build_hosts(),     "Hosts")
        self.tabs.addTab(self._build_summary(),   "Summary")
        content_v.addWidget(self.tabs, 1)

        sidebar = QFrame(); sidebar.setObjectName("Sidebar")
        sv = QVBoxLayout(sidebar); sv.setContentsMargins(14,16,14,16); sv.setSpacing(8)
        self.nav = QListWidget(); self.nav.setObjectName("Nav"); self.nav.setIconSize(QSize(18,18))
        for name in ["Dashboard","Compare","Findings","Hosts","Summary"]:
            it = QListWidgetItem(name); it.setSizeHint(QSize(160,40))
            self.nav.addItem(it)
        self.nav.currentRowChanged.connect(self._switch_tab); self.nav.setCurrentRow(0)
        sv.addWidget(QLabel("<b>Navigation</b>")); sv.addWidget(self.nav, 1)

        split.addWidget(sidebar); split.addWidget(content); split.setStretchFactor(1,1); split.setSizes([230, 1100])
        split.setCollapsible(0, False)

        # ========= Footer =========
        footer = QFrame(); footer.setObjectName("Footer")
        f = QHBoxLayout(footer); f.setContentsMargins(18,8,18,8); f.setSpacing(16)
        self.progress = QProgressBar(); self.progress.setMaximumWidth(260); self.progress.setValue(0)
        self.progress.setTextVisible(False); self.progress.setFixedHeight(8)
        left_status = QHBoxLayout(); left_status.setSpacing(10)
        left_status.addWidget(QLabel("Status:")); left_status.addWidget(self.progress)
        left_box2 = QWidget(); left_box2.setLayout(left_status)
        self.pipe_lbl = QLabel("Ready • 0 file(s) loaded • 0 warnings"); self.pipe_lbl.setObjectName("Muted")
        self.sel_lbl  = QLabel("—"); self.sel_lbl.setObjectName("Muted"); self.sel_lbl.setAlignment(Qt.AlignRight)
        f.addWidget(left_box2, 0); f.addWidget(self.pipe_lbl, 1); f.addWidget(self.sel_lbl, 1)

        # Assemble
        root.addWidget(header); root.addWidget(split, 1); root.addWidget(footer)
        self.setCentralWidget(central)

        # Menu: Help
        help_menu = self.menuBar().addMenu("&Help")
        act_short = QAction("Shortcuts", self); act_short.triggered.connect(self._show_shortcuts)
        act_about = QAction("About", self); act_about.triggered.connect(lambda: QMessageBox.information(self,"About",f"{APP_NAME}\n{APP_VERSION}"))
        help_menu.addAction(act_short); help_menu.addAction(act_about)

        # Shortcuts
        a_old = QAction(self); a_old.setShortcut(QKeySequence("Ctrl+O")); a_old.triggered.connect(self._pick_old)
        a_new = QAction(self); a_new.setShortcut(QKeySequence("Ctrl+N")); a_new.triggered.connect(self._pick_new)
        a_go  = QAction(self); a_go.setShortcut(QKeySequence(Qt.Key_Return)); a_go.triggered.connect(self._parse_files)
        self.addAction(a_old); self.addAction(a_new); self.addAction(a_go)

        QApplication.processEvents(); self._reflow_header()

    # ----- Builders -----
    def _toolbar(self, with_sev=True):
        bar = QFrame(); bar.setObjectName("Card"); l = QHBoxLayout(bar); l.setContentsMargins(12,8,12,8); l.setSpacing(8)
        self.search_box = QLineEdit(); self.search_box.setPlaceholderText("Filter (QID / Title / CVE)")
        self.search_box.textChanged.connect(self._apply_filters_in_compare); l.addWidget(self.search_box, 3)
        if with_sev:
            self.sev_combo = QComboBox(); self.sev_combo.addItems(["Severity: All","5","4","3","2","1"])
            self.sev_combo.currentIndexChanged.connect(self._apply_filters_in_compare); l.addWidget(self.sev_combo, 1)
        self.rows_lbl = QLabel("0 rows"); self.rows_lbl.setObjectName("Muted"); l.addWidget(self.rows_lbl)
        return bar

    def _card(self, title: str) -> QFrame:
        c = QFrame(); c.setObjectName("KPI")
        l = QVBoxLayout(c); l.setContentsMargins(14,12,14,12); l.setSpacing(4)
        self_title = QLabel(f"<b>{title}</b>")
        self_value = QLabel("<span style='opacity:.75'>—</span>")
        l.addWidget(self_title); l.addWidget(self_value)
        c._value_label = self_value
        return c

    def _chart_card(self, title: str):
        card = QFrame(); card.setObjectName("Card")
        lay = QVBoxLayout(card); lay.setContentsMargins(12,10,12,10); lay.setSpacing(6)
        lay.addWidget(QLabel(f"<b>{title}</b>"))
        fig = Figure(figsize=(4.6,3.1)); fig.patch.set_alpha(0.0)
        canvas = FigureCanvas(fig); canvas.setMinimumHeight(260)
        lay.addWidget(canvas, 1)
        return card, canvas, fig

    def _build_dashboard(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(12)
        kpi_row = QHBoxLayout(); kpi_row.setSpacing(12)
        self.kpi_intro = self._card("Introduced"); self.kpi_sust = self._card("Sustained")
        self.kpi_ret = self._card("Retired"); self.kpi_dx = self._card("Exposure Δ")
        for c in (self.kpi_intro, self.kpi_sust, self.kpi_ret, self.kpi_dx): kpi_row.addWidget(c, 1)
        v.addLayout(kpi_row)
        charts_row = QHBoxLayout(); charts_row.setSpacing(12)
        if MPL_AVAILABLE:
            self.card_intro, self.canvas_intro, self.fig_intro = self._chart_card("Introduced — severity mix")
            self.card_sust,  self.canvas_sust,  self.fig_sust  = self._chart_card("Sustained — severity mix")
            self.card_ret,   self.canvas_ret,   self.fig_ret   = self._chart_card("Retired — severity mix")
            charts_row.addWidget(self.card_intro, 1); charts_row.addWidget(self.card_sust, 1); charts_row.addWidget(self.card_ret, 1)
        else:
            charts_row.addWidget(QLabel("Install matplotlib to see charts"))
        v.addLayout(charts_row, 1); v.addStretch(1); return w

    def _build_compare(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(12)
        v.addWidget(self._toolbar(with_sev=True))
        def section(title, view):
            frame = QFrame(); frame.setObjectName("Card")
            layout = QVBoxLayout(frame); layout.setContentsMargins(10,8,10,8); layout.setSpacing(6)
            layout.addWidget(QLabel(f"<b>{title}</b>")); layout.addWidget(view); return frame
        self.intro_view = QTableView(); self.intro_model = PandasModel(); self.intro_view.setModel(self.intro_model)
        self.sust_view  = QTableView(); self.sust_model  = PandasModel(); self.sust_view.setModel(self.sust_model)
        self.ret_view   = QTableView(); self.ret_model   = PandasModel(); self.ret_view.setModel(self.ret_model)
        for vv in (self.intro_view, self.sust_view, self.ret_view):
            vv.setSortingEnabled(True); vv.doubleClicked.connect(self._open_row_dialog)
            vv.setWordWrap(False); vv.verticalHeader().setDefaultSectionSize(24); vv.setAlternatingRowColors(True)
        v.addWidget(section("Introduced Findings (NEW only)", self.intro_view))
        v.addWidget(section("Sustained Findings (both)", self.sust_view))
        v.addWidget(section("Retired Findings (OLD only)", self.ret_view))
        return w

    def _build_findings(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(12)
        tabs = QTabWidget(); tabs.tabBar().hide()
        self.intro_view2 = QTableView(); self.intro_view2.setModel(PandasModel()); self.intro_view2.doubleClicked.connect(self._open_row_dialog)
        self.sust_view2  = QTableView(); self.sust_view2.setModel(PandasModel()); self.sust_view2.doubleClicked.connect(self._open_row_dialog)
        self.ret_view2   = QTableView(); self.ret_view2.setModel(PandasModel());  self.ret_view2.doubleClicked.connect(self._open_row_dialog)
        for vv in (self.intro_view2, self.sust_view2, self.ret_view2):
            vv.setWordWrap(False); vv.verticalHeader().setDefaultSectionSize(24); vv.setAlternatingRowColors(True)
        tabs.addTab(self.intro_view2,"Introduced"); tabs.addTab(self.sust_view2,"Sustained"); tabs.addTab(self.ret_view2,"Retired")
        v.addWidget(tabs, 1); return w

    def _build_hosts(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(12)
        v.addWidget(self._toolbar(with_sev=False))
        tabs = QTabWidget(); tabs.tabBar().hide()
        self.old_hosts_view = QTableView(); self.old_hosts_model = PandasModel(); self.old_hosts_view.setModel(self.old_hosts_model)
        self.new_hosts_view = QTableView(); self.new_hosts_model = PandasModel(); self.new_hosts_view.setModel(self.new_hosts_model)
        for vv in (self.old_hosts_view, self.new_hosts_view):
            vv.setSortingEnabled(True); vv.doubleClicked.connect(self._open_row_dialog)
            vv.setWordWrap(False); vv.verticalHeader().setDefaultSectionSize(24); vv.setAlternatingRowColors(True)
        tabs.addTab(self.old_hosts_view,"OLD Hosts"); tabs.addTab(self.new_hosts_view,"NEW Hosts"); v.addWidget(tabs, 1); return w

    def _build_summary(self) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(8,8,8,8); v.setSpacing(12)
        self.summary_kpi_cards = []
        sections = [
            ("Findings", ["Introduced (NEW only)", "Sustained (both)", "Retired (OLD only)", "Total (OLD)", "Total (NEW)", "Net Change"]),
            ("Rates", ["Closure Rate", "Introduction Rate", "Sustained Rate"]),
            ("Exposure", ["Exposure NEW(Introduced)", "Exposure NEW(Sustained)", "Exposure OLD(Sustained)", "Exposure OLD(Retired)", "Exposure Δ Sustained"]),
            ("Exposure Split %", ["Split% Introduced", "Split% Sustained(NEW)", "Split% Retired"])
        ]
        for section_title, kpis in sections:
            section_frame = QFrame(); section_frame.setObjectName("Card")
            section_layout = QVBoxLayout(section_frame); section_layout.setContentsMargins(12,10,12,10)
            section_layout.addWidget(QLabel(f"<b>{section_title}</b>"))
            row_layout = QHBoxLayout(); row_layout.setSpacing(12)
            for kpi in kpis:
                card = self._card(kpi); self.summary_kpi_cards.append((kpi, card._value_label)); row_layout.addWidget(card, 1)
            section_layout.addLayout(row_layout); v.addWidget(section_frame)
        if MPL_AVAILABLE:
            chart_card = QFrame(); chart_card.setObjectName("Card")
            chart_layout = QVBoxLayout(chart_card); chart_layout.setContentsMargins(12,10,12,10)
            chart_layout.addWidget(QLabel("<b>Exposure Split</b>"))
            self.summary_fig = Figure(figsize=(6.0, 3.6)); self.summary_fig.patch.set_alpha(0.0)
            self.summary_canvas = FigureCanvas(self.summary_fig); self.summary_canvas.setMinimumHeight(280)
            chart_layout.addWidget(self.summary_canvas, 1); v.addWidget(chart_card)
        v.addStretch(1); return w

    # ---------- Styling ----------
    def _apply_style(self):
        dark = """
        QWidget { background:#0A0F1A; color:#EAF0FF; }

        QFrame#Header {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #07213D, stop:1 #0B3564);
            border-bottom:1px solid rgba(255,255,255,0.08);
        }
        QFrame#HeaderInner[maxw="true"] {
            min-height: 76px; border-radius:18px; background: rgba(8,15,30,0.85); border:1px solid rgba(255,255,255,0.10);
        }
        QLabel#Title { font-size:19px; font-weight:700; letter-spacing:.2px; color:#FFFFFF; }

        QFrame#Sidebar { background:#0D1424; border-right:1px solid #1E2A44; }
        QListWidget#Nav { background:transparent; border:none; color:#EAF0FF; }
        QListWidget#Nav::item { margin:6px 4px; padding:12px; border-radius:12px; }
        QListWidget#Nav::item:selected { background: rgba(48,128,255,0.30); }

        QFrame#Footer { background: rgba(10,16,30,0.92); border-top:1px solid rgba(255,255,255,0.08); }
        QLabel#Muted { color:#9FB2D9; }

        QLineEdit, QComboBox {
            padding:10px 12px; border-radius:12px; border:1px solid #2A3E66; background:#0E1A33; color:#EAF0FF;
        }
        QLineEdit::placeholder { color:rgba(234,240,255,0.65); }
        QLineEdit { min-width:360px; }

        QPushButton#Primary[accent="true"] {
            background:#2E81FF; border:1px solid #2E81FF; color:white; padding:10px 18px; border-radius:12px; font-weight:700;
        }
        QPushButton#Primary[accent="true"]:hover { background:#4A93FF; }
        QPushButton#Primary[accent="true"]:pressed { background:#1F6FEB; }

        QPushButton#Chip {
            padding:9px 14px; border-radius:999px; background:rgba(255,255,255,0.06);
            border:1px solid rgba(255,255,255,0.28); color:#FFFFFF; max-width:260px;
        }
        QPushButton#Chip:hover { background:rgba(255,255,255,0.10); }

        QPushButton, QToolButton {
            padding:10px 14px; border-radius:12px; border:1px solid #2A3E66; background:#0E1A33; color:#EAF0FF;
        }
        QPushButton:hover, QToolButton:hover { background:#132447; }

        QHeaderView::section { background:#0E1A33; color:#EAF0FF; border:0; padding:8px; }
        QFrame#Card, QFrame#KPI { background:#0E1A33; border:1px solid #20355E; border-radius:14px; }
        """

        light = """
        QWidget { background:#F7F9FE; color:#0A0F1A; }

        QFrame#Header {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #E6F1FF, stop:1 #EDF3FF);
            border-bottom:1px solid #DAE4F5;
        }
        QFrame#HeaderInner[maxw="true"] { min-height: 76px; border-radius:18px; background:#FFFFFF; border:1px solid #E4ECFA; }
        QLabel#Title { font-size:19px; font-weight:700; letter-spacing:.2px; color:#071a33; }

        QFrame#Sidebar { background:#FFFFFF; border-right:1px solid #E4ECFA; }
        QListWidget#Nav { background:transparent; border:none; color:#0A0F1A; }
        QListWidget#Nav::item { margin:6px 4px; padding:12px; border-radius:12px; }
        QListWidget#Nav::item:selected { background: rgba(46,129,255,0.18); }

        QFrame#Footer { background:#FFFFFF; border-top:1px solid #E4ECFA; }
        QLabel#Muted { color:#6B7FA6; }

        QLineEdit, QComboBox {
            padding:10px 12px; border-radius:12px; border:1px solid #DBE6FB; background:#FFFFFF; color:#0A0F1A;
        }
        QLineEdit::placeholder { color:#6B7FA6; }
        QLineEdit { min-width:360px; }

        QPushButton#Primary[accent="true"] { background:#2E81FF; color:white; border:1px solid #2E81FF; padding:10px 18px; border-radius:12px; font-weight:700; }
        QPushButton#Primary[accent="true"]:hover { background:#4A93FF; }
        QPushButton#Chip { padding:9px 14px; border-radius:999px; background:#FFFFFF; border:1px solid #DBE6FB; color:#0A0F1A; max-width:260px; }
        QPushButton, QToolButton { padding:10px 14px; border-radius:12px; border:1px solid #DBE6FB; background:#FFFFFF; color:#0A0F1A; }
        QPushButton:hover, QToolButton:hover { background:#F2F6FF; }

        QHeaderView::section { background:#FFFFFF; color:#0A0F1A; border:0; padding:8px; }
        QFrame#Card, QFrame#KPI { background:#FFFFFF; border:1px solid #E4ECFA; border-radius:14px; }
        """
        self.setStyleSheet(dark if self.dark else light)

    def _toggle_theme(self):
        self.dark = not self.dark
        self._apply_style()
        self._reflow_header()

    # ---------- Responsive header ----------
    def _elide_header_text(self):
        self.title_lbl.setText(f"{APP_NAME} — {APP_VERSION}")
        for btn in (self.old_chip, self.new_chip):
            full: str = btn.property("full_text") or btn.text()
            fm = QFontMetrics(btn.font())
            shown = fm.elidedText(full, Qt.ElideRight, max(80, btn.width()-16))
            btn.setText(shown)
            btn.setToolTip(full)

    def _reflow_header(self):
        total_w = max(0, self.header_inner.width())
        export_w = self.export_menu_btn.sizeHint().width()
        theme_w  = self.theme_btn.sizeHint().width()
        parse_w  = self.parse_btn.sizeHint().width()
        gutters = 20*2 + 16*2
        left_w = self.left_box.sizeHint().width()
        available = total_w - (left_w + export_w + theme_w + parse_w + gutters)
        if available < 200: available = 200
        chips_pool = int(available * 0.38)
        chip_max = max(120, min(260, chips_pool // 2))
        self.old_chip.setMaximumWidth(chip_max); self.new_chip.setMaximumWidth(chip_max)
        search_w = max(300, available - chips_pool)
        self.search_global.setMinimumWidth(search_w); self.search_global.setMaximumWidth(search_w)
        self._elide_header_text()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._reflow_header()

    # ---------- Actions ----------
    def _switch_tab(self, idx: int):
        if not hasattr(self, "tabs") or self.tabs is None: return
        if 0 <= idx < self.tabs.count() and idx != self.tabs.currentIndex():
            self.tabs.setCurrentIndex(idx)

    def _pick_old(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select OLD Qualys report", "", "HTML/XHTML (*.html *.htm *.xhtml)")
        if path:
            self.old_file = Path(path)
            display = f"OLD: {self.old_file.name} ✓"
            self.old_chip.setProperty("full_text", display)
            self._reflow_header()
            self._update_status(False)

    def _pick_new(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select NEW Qualys report", "", "HTML/XHTML (*.html *.htm *.xhtml)")
        if path:
            self.new_file = Path(path)
            display = f"NEW: {self.new_file.name} ✓"
            self.new_chip.setProperty("full_text", display)
            self._reflow_header()
            self._update_status(False)

    def _update_status(self, parsing: bool, progress: int = 0):
        files = (1 if self.old_file else 0) + (1 if self.new_file else 0)
        self.progress.setValue(progress if parsing else (100 if files==2 and self.results is not None else 0))
        self.pipe_lbl.setText(("Parsing…" if parsing else "Ready") + f" • {files} file(s) loaded • 0 warnings")

    def _parse_files(self):
        if CLI is None:
            QMessageBox.critical(self,"Parser missing","CLI.py not found."); return
        if not (self.old_file and self.new_file):
            QMessageBox.warning(self,"Select files","Please choose both OLD and NEW reports."); return
        try:
            self._update_status(True, 10); QApplication.processEvents()
            df_old_f, df_old_h = CLI.parse_report(self.old_file, "old")
            df_new_f, df_new_h = CLI.parse_report(self.new_file, "new")
            self.results = CLI.compare_findings(df_old_f, df_new_f)
            self.hosts_old, self.hosts_new = df_old_h, df_new_h
            self._bind_tables(); self._refresh_kpis(); self._refresh_summary_cards()
            self._refresh_selection(); self._draw_charts()
            self._update_status(False, 100)
        except Exception as ex:
            traceback.print_exc(); QMessageBox.critical(self,"Parse error",f"Failed to parse reports:\n{ex}")
            self._update_status(False, 0)

    def _bind_tables(self):
        r = self.results or {}
        self.intro_model = getattr(self, "intro_model", PandasModel())
        self.sust_model  = getattr(self, "sust_model", PandasModel())
        self.ret_model   = getattr(self, "ret_model", PandasModel())
        self.intro_model.setDataFrame(r.get("introduced", pd.DataFrame()))
        self.sust_model.setDataFrame(r.get("sustained",  pd.DataFrame()))
        self.ret_model.setDataFrame(r.get("retired",    pd.DataFrame()))
        self.intro_view.setModel(self.intro_model); self.sust_view.setModel(self.sust_model); self.ret_view.setModel(self.ret_model)
        for v in (self.intro_view, self.sust_view, self.ret_view): v.resizeColumnsToContents(); v.setSortingEnabled(True)
        self.intro_view2.model().setDataFrame(r.get("introduced", pd.DataFrame()))
        self.sust_view2.model().setDataFrame(r.get("sustained",  pd.DataFrame()))
        self.ret_view2.model().setDataFrame(r.get("retired",    pd.DataFrame()))
        for v in (self.intro_view2, self.sust_view2, self.ret_view2): v.resizeColumnsToContents(); v.setSortingEnabled(True)
        self.old_hosts_model.setDataFrame(df_or_empty(self.hosts_old)); self.new_hosts_model.setDataFrame(df_or_empty(self.hosts_new))
        for v in (self.old_hosts_view, self.new_hosts_view): v.resizeColumnsToContents(); v.setSortingEnabled(True)
        n = sum(len(m.df()) for m in (self.intro_model, self.sust_model, self.ret_model))
        self.rows_lbl.setText(f"{n} rows")

    def _apply_filters_in_compare(self):
        if not self.results: return
        text = self.search_box.text().strip().lower()
        sev = None
        if hasattr(self, "sev_combo") and self.sev_combo.currentText() != "Severity: All":
            sev = int(self.sev_combo.currentText())
        def filt(df: pd.DataFrame) -> pd.DataFrame:
            if df is None or df.empty: return df
            out = df.copy()
            if sev is not None and "severity" in out.columns:
                out = out[out["severity"] == sev]
            if text:
                mask = out.apply(lambda r: text in (" ".join(str(r.get(c,"")) for c in ("qid","title","cves")).lower()), axis=1)
                out = out[mask]
            return out
        self.intro_model.setDataFrame(filt(self.results["introduced"]))
        self.sust_model.setDataFrame(filt(self.results["sustained"]))
        self.ret_model.setDataFrame(filt(self.results["retired"]))
        for v in (self.intro_view, self.sust_view, self.ret_view): v.resizeColumnsToContents()
        total = sum(len(m.df()) for m in (self.intro_model, self.sust_model, self.ret_model))
        self.rows_lbl.setText(f"{total} rows")

    def _global_search(self):
        if hasattr(self, "search_box"): self.search_box.setText(self.search_global.text())

    # ---------- KPI / Summary / Charts ----------
    def _sev_counts(self, df: pd.DataFrame) -> pd.Series:
        if df is None or df.empty or "severity" not in df.columns:
            return pd.Series([0,0,0,0,0], index=[1,2,3,4,5])
        s = pd.to_numeric(df["severity"], errors="coerce").dropna().astype(int)
        return s.value_counts().reindex([1,2,3,4,5]).fillna(0).astype(int)

    def _refresh_kpis(self):
        if not self.results:
            for lbl in (self.kpi_intro._value_label, self.kpi_sust._value_label, self.kpi_ret._value_label, self.kpi_dx._value_label):
                lbl.setText("<span style='opacity:.75'>—</span>")
            return
        r = self.results
        n_intro, n_sust, n_ret = len(r["introduced"]), len(r["sustained"]), len(r["retired"])
        n_old, n_new = len(r["old_all"]), len(r["new_all"])
        a_snew  = safe_sum(r["sustained"], "asset_exposure")
        a_sold  = safe_sum(r["sustained"], "old_asset_exposure")
        self.kpi_intro._value_label.setText(f"{n_intro} <span style='opacity:.75'>({pct(n_intro,n_new)} of NEW)</span>")
        self.kpi_sust._value_label.setText(f"{n_sust} <span style='opacity:.75'>({pct(n_sust,n_old)} of OLD)</span>")
        self.kpi_ret._value_label.setText (f"{n_ret} <span style='opacity:.75'>(closure {pct(n_ret,n_old)})</span>")
        self.kpi_dx._value_label.setText  (f"{a_snew - a_sold}")

    def _refresh_selection(self):
        if not self.results: self.sel_lbl.setText("—"); return
        r = self.results
        count = len(r["introduced"]) + len(r["sustained"]) + len(r["retired"])
        assets = safe_sum(r["introduced"],"asset_exposure")+safe_sum(r["sustained"],"asset_exposure")+safe_sum(r["retired"],"asset_exposure")
        self.sel_lbl.setText(f"Selected: {count} findings • {assets} affected assets")

    def _refresh_summary_cards(self):
        if not self.results:
            for _, lbl in self.summary_kpi_cards: lbl.setText("<span style='opacity:.75'>—</span>")
            if MPL_AVAILABLE and hasattr(self, "summary_fig"): self.summary_fig.clear(); self.summary_canvas.draw_idle()
            return
        r = self.results
        n_intro, n_sust, n_ret = len(r["introduced"]), len(r["sustained"]), len(r["retired"])
        n_old, n_new = len(r["old_all"]), len(r["new_all"])
        a_intro = safe_sum(r["introduced"], "asset_exposure")
        a_snew  = safe_sum(r["sustained"], "asset_exposure")
        a_sold  = safe_sum(r["sustained"], "old_asset_exposure")
        a_ret   = safe_sum(r["retired"], "asset_exposure")
        a_total = max(1, a_intro + a_snew + a_ret)
        values = {
            "Introduced (NEW only)": n_intro, "Sustained (both)": n_sust, "Retired (OLD only)": n_ret,
            "Total (OLD)": n_old, "Total (NEW)": n_new, "Net Change": f"{n_intro - n_ret:+d}",
            "Closure Rate": pct(n_ret, n_old), "Introduction Rate": pct(n_intro, n_new), "Sustained Rate": pct(n_sust, n_old),
            "Exposure NEW(Introduced)": a_intro, "Exposure NEW(Sustained)": a_snew, "Exposure OLD(Sustained)": a_sold,
            "Exposure OLD(Retired)": a_ret, "Exposure Δ Sustained": a_snew - a_sold,
            "Split% Introduced": pct(a_intro, a_total), "Split% Sustained(NEW)": pct(a_snew, a_total), "Split% Retired": pct(a_ret, a_total),
        }
        for key, lbl in self.summary_kpi_cards: lbl.setText(str(values.get(key, "—")))
        if MPL_AVAILABLE:
            self.summary_fig.clear()
            ax = self.summary_fig.add_subplot(111); ax.set_facecolor('none')
            vals = [a_intro, a_snew, a_ret]; labs = ["Introduced", "Sustained (NEW)", "Retired"]
            if sum(vals) == 0: vals = [1,0,0]  # avoid zero-division pie
            ax.pie(vals, labels=labs, autopct='%1.1f%%', startangle=90); ax.axis('equal')
            self.summary_fig.tight_layout(); self.summary_canvas.draw_idle()

    def _draw_charts(self):
        if not MPL_AVAILABLE or not self.results: return
        r = self.results
        for fig, canvas, df, title in (
            (self.fig_intro, self.canvas_intro, r["introduced"], "Introduced — severity mix"),
            (self.fig_sust,  self.canvas_sust,  r["sustained"],  "Sustained — severity mix"),
            (self.fig_ret,   self.canvas_ret,   r["retired"],    "Retired — severity mix"),
        ):
            fig.clear(); ax = fig.add_subplot(111); ax.set_facecolor('none')
            counts = self._sev_counts(df)
            ax.bar([str(k) for k in counts.index], counts.values)
            ax.set_xlabel("Severity"); ax.set_ylabel("Findings")
            ax.set_title(title); ax.grid(axis="y", alpha=.2)
            fig.tight_layout(); canvas.draw_idle()

    # ---------- Row details ----------
    def _open_row_dialog(self, index):
        view = self.sender(); model: PandasModel = view.model(); df = model.df()
        r = df.iloc[index.row()] if not df.empty else None
        if r is None: return
        RowDialog("Row details", r, self).exec()

    # ---------- Export ----------
    def _export_excel(self):
        if CLI is None: return
        if not self.results:
            QMessageBox.information(self,"Nothing to export","Parse reports first."); return
        out, _ = QFileDialog.getSaveFileName(self,"Save Excel","qualys_diff.xlsx","Excel (*.xlsx)")
        if not out: return
        try:
            CLI.write_excel(self.results, df_or_empty(self.hosts_old), df_or_empty(self.hosts_new), Path(out))
            QMessageBox.information(self,"Done",f"Excel written:\n{out}")
        except Exception as ex:
            traceback.print_exc(); QMessageBox.critical(self,"Export error",str(ex))

    def _export_csvs(self):
        if not self.results:
            QMessageBox.information(self,"Nothing to export","Parse reports first."); return
        dir_ = QFileDialog.getExistingDirectory(self,"Select output folder")
        if not dir_: return
        try:
            Path(dir_).mkdir(parents=True, exist_ok=True)
            self.results["introduced"].to_csv(Path(dir_)/"introduced.csv", index=False)
            self.results["sustained"].to_csv(Path(dir_)/"sustained.csv", index=False)
            self.results["retired"].to_csv(Path(dir_)/"retired.csv", index=False)
            df_or_empty(self.hosts_old).to_csv(Path(dir_)/"hosts_old.csv", index=False)
            df_or_empty(self.hosts_new).to_csv(Path(dir_)/"hosts_new.csv", index=False)
            QMessageBox.information(self,"Done",f"CSV bundle saved in:\n{dir_}")
        except Exception as ex:
            traceback.print_exc(); QMessageBox.critical(self,"Export error",str(ex))

    def _export_pdf(self):
        """Export concise executive PDF (logo rendered via matplotlib.image to avoid dtype object error)."""
        if not self.results:
            QMessageBox.information(self,"Nothing to export","Parse reports first."); return
        out, _ = QFileDialog.getSaveFileName(self,"Save PDF","qualys_diff_summary.pdf","PDF (*.pdf)")
        if not out: return

        try:
            r = self.results
            n_intro, n_sust, n_ret = len(r["introduced"]), len(r["sustained"]), len(r["retired"])
            n_old, n_new = len(r["old_all"]), len(r["new_all"])
            a_intro = safe_sum(r["introduced"], "asset_exposure")
            a_snew  = safe_sum(r["sustained"],  "asset_exposure")
            a_sold  = safe_sum(r["sustained"],  "old_asset_exposure")
            a_ret   = safe_sum(r["retired"],    "asset_exposure")
            a_total = max(1, a_intro + a_snew + a_ret)

            with PdfPages(out) as pdf:
                # Page 1 — Title & high-level metrics
                fig = Figure(figsize=(11.69, 8.27))  # A4 landscape
                ax = fig.add_subplot(111); fig.patch.set_facecolor('white'); ax.axis('off')
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                ax.text(0.02, 0.92, f"{APP_NAME} — Executive Summary", fontsize=18, weight='bold')
                ax.text(0.02, 0.88, f"Version {APP_VERSION}  |  Generated {ts}", fontsize=10, color='#666666')

                lines = [
                    ("Introduced (NEW)", f"{n_intro} ({pct(n_intro,n_new)} of NEW)"),
                    ("Sustained (both)", f"{n_sust} ({pct(n_sust,n_old)} of OLD)"),
                    ("Retired (OLD)",    f"{n_ret} (closure {pct(n_ret,n_old)})"),
                    ("Net Change",       f"{n_intro - n_ret:+d}"),
                    ("Exposure NEW(Introduced)", f"{a_intro}"),
                    ("Exposure NEW(Sustained)",  f"{a_snew}"),
                    ("Exposure OLD(Sustained)",  f"{a_sold}"),
                    ("Exposure OLD(Retired)",    f"{a_ret}"),
                    ("Split% Introduced / Sustained / Retired", f"{pct(a_intro,a_total)} / {pct(a_snew,a_total)} / {pct(a_ret,a_total)}"),
                ]
                y = 0.80
                for k, v in lines:
                    ax.text(0.04, y, k, fontsize=12, weight='bold'); ax.text(0.46, y, v, fontsize=12); y -= 0.055

                # Logo (fix): read with matplotlib.image → ndarray → figimage
                lg = find_logo()
                if lg:
                    try:
                        img = mpimg.imread(lg)  # ndarray (float/uint8) — OK for figimage
                        fig.figimage(img, xo=20, yo=20, origin='upper', zorder=10)
                    except Exception:
                        pass

                pdf.savefig(fig, bbox_inches='tight')

                # Page 2 — Exposure Split pie
                fig2 = Figure(figsize=(11.69, 8.27)); ax2 = fig2.add_subplot(111)
                vals = [a_intro, a_snew, a_ret]; labs = ["Introduced","Sustained (NEW)","Retired"]
                if sum(vals) == 0: vals = [1,0,0]
                ax2.pie(vals, labels=labs, autopct='%1.1f%%', startangle=90)
                ax2.axis('equal'); ax2.set_title("Exposure Split", fontsize=14, weight='bold')
                pdf.savefig(fig2, bbox_inches='tight')

                # Pages 3–5 — Severity mix bars
                for df, title in ((r["introduced"],"Introduced — severity mix"),
                                  (r["sustained"], "Sustained — severity mix"),
                                  (r["retired"],   "Retired — severity mix")):
                    figx = Figure(figsize=(11.69, 8.27)); axx = figx.add_subplot(111)
                    counts = self._sev_counts(df)
                    axx.bar([str(k) for k in counts.index], counts.values)
                    axx.set_xlabel("Severity"); axx.set_ylabel("Findings")
                    axx.set_title(title, fontsize=14, weight='bold'); axx.grid(axis='y', alpha=.25)
                    pdf.savefig(figx, bbox_inches='tight')

            QMessageBox.information(self,"Done",f"PDF saved:\n{out}")
        except Exception as ex:
            traceback.print_exc(); QMessageBox.critical(self,"PDF export error",str(ex))

    def _show_shortcuts(self):
        QMessageBox.information(self,"Shortcuts",
            "Ctrl+O: Pick OLD\nCtrl+N: Pick NEW\nEnter: Parse\n"
            "Top Search: quick filter across views\n"
            "Double-click row: details dialog")

# ---------- Run ----------
def main():
    app = QApplication(sys.argv)
    win = MainWindow(); win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
