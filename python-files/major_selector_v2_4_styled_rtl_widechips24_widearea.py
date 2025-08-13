# -*- coding: utf-8 -*-
import sys, os
import pandas as pd
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFileDialog, QLabel, QLineEdit, QPushButton, QAbstractItemView, QDialog,
    QDialogButtonBox, QListWidget, QListWidgetItem, QMessageBox, QTabWidget,
    QSplitter, QSizePolicy, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QColor

DEFAULT_FILE = "انتخاب رشته تجربی 1403 (1).xlsx"

# ---------- Helpers ----------
def _drop_empty(df):
    df = df.dropna(how="all")
    df = df.dropna(how="all", axis=1)
    return df

def _normalize_columns(df):
    cols = []
    for i, c in enumerate(df.columns, start=1):
        name = str(c).strip()
        if name == "" or str(name).lower().startswith("unnamed"):
            name = f"ستون_{i}"
        cols.append(name)
    df.columns = cols
    return df

# ---------- Filter dialog tabs ----------
class FilterTab(QWidget):
    def __init__(self, col_name, values):
        super().__init__()
        self.col = col_name
        self.all_values = sorted(set(str(v) for v in values if pd.notna(v)))
        v = QVBoxLayout(self); v.setContentsMargins(10,10,10,10); v.setSpacing(8)

        top = QHBoxLayout(); top.setSpacing(8)
        self.btn_select_all = QPushButton("انتخاب همه"); self.btn_select_all.setProperty("kind","secondary")
        self.btn_select_none = QPushButton("هیچ"); self.btn_select_none.setProperty("kind","secondary")
        self.btn_clear_column = QPushButton("پاک این ستون"); self.btn_clear_column.setProperty("kind","danger")
        top.addWidget(self.btn_select_all); top.addWidget(self.btn_select_none); top.addStretch(); top.addWidget(self.btn_clear_column)
        v.addLayout(top)

        self.search = QLineEdit(); self.search.setPlaceholderText("جستجو...")
        v.addWidget(self.search)
        self.listw = QListWidget(); self.listw.setSelectionMode(QAbstractItemView.MultiSelection)
        v.addWidget(self.listw)
        self._fill(self.all_values)

        self.search.textChanged.connect(self._on_search)
        self.btn_select_all.clicked.connect(lambda: self.listw.selectAll())
        self.btn_select_none.clicked.connect(lambda: self.listw.clearSelection())
        self.btn_clear_column.clicked.connect(lambda: self.listw.clearSelection())

    def _fill(self, vals):
        self.listw.clear()
        for val in vals:
            self.listw.addItem(QListWidgetItem(val))

    def _on_search(self, text):
        q = text.strip().lower()
        if not q:
            self._fill(self.all_values); return
        self._fill([v for v in self.all_values if q in v.lower()])

    def selected_values(self):
        return [i.text() for i in self.listw.selectedItems()]

    def clear(self):
        self.listw.clearSelection()

class FiltersDialog(QDialog):
    def __init__(self, df, current_sel=None):
        super().__init__()
        self.setWindowTitle("فیلترها")
        self.resize(940, 660)
        self.df = df
        self.tabs = QTabWidget()
        self.tab_by_col = {}

        v = QVBoxLayout(self); v.setContentsMargins(12,12,12,12); v.setSpacing(10)
        v.addWidget(self.tabs)

        for col in df.columns:
            tab = FilterTab(col, df[col].unique())
            self.tabs.addTab(tab, str(col))
            self.tab_by_col[col] = tab

        if current_sel:
            for col, vals in current_sel.items():
                if col in self.tab_by_col:
                    lw = self.tab_by_col[col].listw
                    s = set(map(str, vals))
                    for i in range(lw.count()):
                        it = lw.item(i)
                        if it.text() in s:
                            it.setSelected(True)

        bb = QDialogButtonBox()
        self.btn_apply = bb.addButton("اعمال", QDialogButtonBox.AcceptRole); self.btn_apply.setProperty("kind","primary")
        self.btn_cancel = bb.addButton("انصراف", QDialogButtonBox.RejectRole)
        self.btn_clear_all = bb.addButton("حذف همه فیلترها", QDialogButtonBox.ResetRole); self.btn_clear_all.setProperty("kind","danger")
        v.addWidget(bb)
        self.btn_apply.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_clear_all.clicked.connect(self.clear_all)

    def selections(self):
        sel = {}
        for col, tab in self.tab_by_col.items():
            vals = tab.selected_values()
            if vals:
                sel[col] = vals
        return sel

    def clear_all(self):
        for tab in self.tab_by_col.values():
            tab.clear()

# ---------- Chip button (colored, rounded) ----------
class ChipButton(QPushButton):
    def __init__(self, label, col_key, on_clear, bg="#d1e9ff", fg="#0b3d91"):
        super().__init__(f"{label}  ✕")
        self.col_key = col_key
        self.on_clear = on_clear
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid rgba(0,0,0,0.08);
                border-radius: 14px;
                padding: 6px 24px;
                background: {bg};
                color: {fg};
                font-weight: 600;
            }}
            QPushButton:hover {{ filter: brightness(0.95); }}
        """)
        self.clicked.connect(lambda: self.on_clear(self.col_key))

# ---------- Main Window ----------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("انتخاب رشته — v2.4 (RTL Chips)")
        self.resize(1500, 900)
        self.data = None
        self.filtered_df = None
        self.last_dir = os.getcwd()
        self.selected_texts = set()
        self.current_filters = {}
        self.dark_mode = False

        root = QVBoxLayout(self); root.setContentsMargins(10,10,10,10); root.setSpacing(10)

        # Top bar
        topbar = QHBoxLayout(); topbar.setSpacing(8)
        self.status = QLabel("آماده")
        self.btn_theme = QPushButton("Dark Mode"); self.btn_theme.setProperty("kind","secondary")
        topbar.addWidget(self.status, 1); topbar.addWidget(self.btn_theme, 0)
        root.addLayout(topbar)

        # Active filters area (rounded border, RTL, right-aligned)
        self.chips_frame = QFrame(); self.chips_frame.setObjectName("chipbox")
        chips_outer = QHBoxLayout(self.chips_frame); chips_outer.setContentsMargins(10,8,10,8); chips_outer.setSpacing(8)
        self.chips_label = QLabel("فیلترهای فعال:")
        self.chips_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.chips_scroll = QScrollArea(); self.chips_scroll.setWidgetResizable(True)
        self.chips_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chips_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chips_inner = QWidget(); self.chips_inner.setLayoutDirection(Qt.RightToLeft)
        self.chips_layout = QHBoxLayout(self.chips_inner)
        self.chips_layout.setContentsMargins(0,0,0,0); self.chips_layout.setSpacing(8)
        self.chips_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.chips_scroll.setWidget(self.chips_inner)

        # Place label right; chips start from right inside scroll area
        chips_outer.addWidget(self.chips_label, 0, Qt.AlignRight)
        chips_outer.addWidget(self.chips_scroll, 5)  # increased stretch for wider chip area
        self.chips_frame.setLayoutDirection(Qt.RightToLeft)
        root.addWidget(self.chips_frame)

        # Splitter 50/50
        splitter = QSplitter(Qt.Horizontal); splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(splitter, 1)

        # Left
        left_wrap = QWidget(); left = QVBoxLayout(left_wrap)
        left.setContentsMargins(0,0,0,0); left.setSpacing(8)
        ctrls = QHBoxLayout(); ctrls.setSpacing(8)
        self.btn_load = QPushButton("بارگذاری (CSV/Excel)")
        self.btn_filters = QPushButton("فیلترها")
        self.btn_clear_filters = QPushButton("حذف همه")
        self.btn_export_filtered_csv = QPushButton("CSV نتایج")
        self.btn_export_filtered_xlsx = QPushButton("Excel نتایج")
        for b, role in [(self.btn_load,"primary"), (self.btn_filters,"secondary"), (self.btn_clear_filters,"danger"),
                        (self.btn_export_filtered_csv,"secondary"), (self.btn_export_filtered_xlsx,"secondary")]:
            b.setProperty("kind", role); ctrls.addWidget(b)
        left.addLayout(ctrls)

        self.tbl_left = QTableWidget()
        self.tbl_left.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_left.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tbl_left.doubleClicked.connect(self.add_selected_rows)
        left.addWidget(self.tbl_left, 1)
        splitter.addWidget(left_wrap)

        # Right
        right_wrap = QWidget(); right = QVBoxLayout(right_wrap)
        right.setContentsMargins(0,0,0,0); right.setSpacing(8)
        right.addWidget(QLabel("انتخاب‌شده‌ها"))
        self.tbl_right = QTableWidget()
        self.tbl_right.setColumnCount(2)
        self.tbl_right.setHorizontalHeaderLabels(["ردیف", "آیتم"])
        self.tbl_right.setColumnWidth(0, 70)
        self.tbl_right.horizontalHeader().setStretchLastSection(True)
        self.tbl_right.verticalHeader().setVisible(False)
        right.addWidget(self.tbl_right, 1)

        actions = QHBoxLayout(); actions.setSpacing(8)
        self.btn_add = QPushButton("افزودن →")
        self.btn_remove = QPushButton("حذف")
        self.btn_up = QPushButton("بالا")
        self.btn_down = QPushButton("پایین")
        self.btn_clear_right = QPushButton("حذف همه")
        self.btn_export_right_csv = QPushButton("CSV انتخاب‌ها")
        self.btn_export_right_xlsx = QPushButton("Excel انتخاب‌ها")
        for b, role in [(self.btn_add,"primary"),(self.btn_remove,"danger"),(self.btn_up,"secondary"),(self.btn_down,"secondary"),
                        (self.btn_clear_right,"danger"),(self.btn_export_right_csv,"secondary"),(self.btn_export_right_xlsx,"secondary")]:
            b.setProperty("kind", role); actions.addWidget(b)
        right.addLayout(actions)
        splitter.addWidget(right_wrap)

        QTimer.singleShot(0, lambda: splitter.setSizes([1,1]))

        # Connect
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_load.clicked.connect(self.load_file)
        self.btn_filters.clicked.connect(self.open_filters_dialog)
        self.btn_clear_filters.clicked.connect(self.clear_all_filters)
        self.btn_export_filtered_csv.clicked.connect(self.export_filtered_csv)
        self.btn_export_filtered_xlsx.clicked.connect(self.export_filtered_xlsx)
        self.btn_add.clicked.connect(self.add_selected_rows)
        self.btn_remove.clicked.connect(self.remove_selected_row)
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        self.btn_clear_right.clicked.connect(self.clear_selected_all)
        self.btn_export_right_csv.clicked.connect(self.export_selected_csv)
        self.btn_export_right_xlsx.clicked.connect(self.export_selected_xlsx)

        # Default file autoload
        try_path = os.path.join(os.getcwd(), DEFAULT_FILE)
        if os.path.exists(try_path):
            self.load_specific_file(try_path)

        self.apply_styles(light=True)

    # ---------- Styles / theme ----------
    def apply_styles(self, light=True):
        if light:
            base_bg = "#ffffff"; base_fg = "#0f172a"; card = "#f8fafc"; border = "#e2e8f0"; sel = "#e0f2fe"
            pri_bg, pri_fg = "#2563eb", "#ffffff"
            sec_bg, sec_fg = "#e2e8f0", "#0f172a"
            danger_bg, danger_fg = "#ef4444", "#ffffff"
            tab_bg, tab_active = "#f1f5f9", "#e2e8f0"
            splitter = "#cbd5e1"
            chipbox_bg = "#f8fafc"
        else:
            base_bg = "#0b1220"; base_fg = "#e2e8f0"; card = "#111827"; border = "#374151"; sel = "#1f2937"
            pri_bg, pri_fg = "#3b82f6", "#e2e8f0"
            sec_bg, sec_fg = "#374151", "#e2e8f0"
            danger_bg, danger_fg = "#ef4444", "#e2e8f0"
            tab_bg, tab_active = "#1f2937", "#374151"
            splitter = "#334155"
            chipbox_bg = "#111827"

        app = QApplication.instance()
        app.setStyleSheet(f"""
            QWidget {{ background: {base_bg}; color: {base_fg}; font-size: 13px; }}
            QLabel {{ font-weight: 600; }}

            QPushButton[kind="primary"] {{
                background: {pri_bg}; color: {pri_fg}; border: none; border-radius: 10px; padding: 8px 12px;
            }}
            QPushButton[kind="primary"]:hover {{ filter: brightness(1.05); }}
            QPushButton[kind="secondary"] {{
                background: {sec_bg}; color: {sec_fg}; border: 1px solid {border}; border-radius: 10px; padding: 8px 12px;
            }}
            QPushButton[kind="secondary"]:hover {{ filter: brightness(0.98); }}
            QPushButton[kind="danger"] {{
                background: {danger_bg}; color: {danger_fg}; border: none; border-radius: 10px; padding: 8px 12px;
            }}
            QPushButton[kind="danger"]:hover {{ filter: brightness(1.05); }}

            QTableWidget {{
                gridline-color: {border};
                alternate-background-color: {card};
                selection-background-color: {sel};
                selection-color: {base_fg};
                border: 1px solid {border}; border-radius: 8px;
            }}
            QHeaderView::section {{
                background: {tab_bg}; border: 1px solid {border}; border-radius: 0px; padding: 6px;
            }}
            QTableCornerButton::section {{ background: {tab_bg}; border: 1px solid {border}; }}

            QTabWidget::pane {{ border: 1px solid {border}; border-radius: 8px; background: {card}; }}
            QTabBar::tab {{
                background: {tab_bg}; padding: 8px 14px; border: 1px solid {border}; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{ background: {tab_active}; font-weight: 600; }}

            QSplitter::handle {{ background: {splitter}; width: 6px; }}
            QLineEdit {{ border: 1px solid {border}; border-radius: 8px; padding: 6px 8px; background: {base_bg}; }}
            QScrollArea {{ border: none; }}

            QFrame#chipbox {{
                background: {chipbox_bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
        """)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_styles(light=not self.dark_mode)
        self.btn_theme.setText("Light Mode" if self.dark_mode else "Dark Mode")

    # ---------- Chip colors (deterministic per column) ----------
    @staticmethod
    def _palette():
        return [
            ("#d1e9ff","#0b3d91"),
            ("#ffe4e6","#8a1323"),
            ("#e9d5ff","#4b1d73"),
            ("#dcfce7","#14532d"),
            ("#fde68a","#7a4c00"),
            ("#f5d0fe","#711c91"),
            ("#bae6fd","#0c4a6e"),
            ("#ffd6a5","#7a3d00"),
            ("#c7f9cc","#104d2c"),
        ]

    @staticmethod
    def _color_for_column(col):
        idx = sum(ord(ch) for ch in str(col)) % len(MainWindow._palette())
        return MainWindow._palette()[idx]

    def _refresh_chips(self):
        while self.chips_layout.count():
            item = self.chips_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        if not self.current_filters:
            return
        for col, vals in self.current_filters.items():
            bg, fg = self._color_for_column(col)
            chip = ChipButton(str(col), col, self._clear_column_filter, bg=bg, fg=fg)
            chip.setToolTip("، ".join(map(str, vals)))
            self.chips_layout.addWidget(chip, 0, Qt.AlignRight)

    def _clear_column_filter(self, col):
        if col in self.current_filters:
            del self.current_filters[col]
            self.apply_filters()

    # ---------- Filter dialog ----------
    def open_filters_dialog(self):
        if self.data is None:
            QMessageBox.warning(self, "هشدار", "ابتدا فایل داده را بارگذاری کن."); return
        dlg = FiltersDialog(self.data, self.current_filters)
        if dlg.exec() == QDialog.Accepted:
            self.current_filters = dlg.selections()
            self.apply_filters()

    def clear_all_filters(self):
        self.current_filters = {}; self.apply_filters()

    # ---------- Loading ----------
    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل", self.last_dir, "Data Files (*.csv *.xlsx *.xls)")
        if not path: return
        self.last_dir = os.path.dirname(path); self.load_specific_file(path)

    def load_specific_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(path)
            elif ext in [".xlsx", ".xls"]:
                xls = pd.ExcelFile(path); sheet = xls.sheet_names[0]
                if len(xls.sheet_names) > 1: sheet = xls.sheet_names[0]
                df = pd.read_excel(path, sheet_name=sheet)
            else:
                QMessageBox.warning(self, "خطا", "نوع فایل پشتیبانی نمی‌شود."); return
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خواندن فایل ناموفق:\n{e}"); return

        if df.empty:
            QMessageBox.warning(self, "هشدار", "فایل داده خالی است."); return

        df = _drop_empty(df); df = _normalize_columns(df)
        for c in df.columns: df[c] = df[c].astype(str)
        self.data = df.reset_index(drop=True)

        preview = ", ".join(list(self.data.columns)[:8])
        self.status.setText(f"{len(self.data)} سطر، {len(self.data.columns)} ستون | ستون‌ها: {preview}{'...' if len(self.data.columns)>8 else ''}")
        self.apply_filters()

    # ---------- Filtering ----------
    def apply_filters(self):
        if self.data is None: return
        df = self.data.copy()
        for col, vals in self.current_filters.items():
            df = df[df[col].isin(vals)]
        self.filtered_df = df.reset_index(drop=True)
        self.populate_left(self.filtered_df)
        self._refresh_chips()

    # ---------- Left table ----------
    def populate_left(self, df):
        self.tbl_left.clear()
        self.tbl_left.setAlternatingRowColors(True)
        self.tbl_left.setRowCount(len(df))
        self.tbl_left.setColumnCount(len(df.columns) if df is not None else 0)
        if df is not None and len(df.columns):
            self.tbl_left.setHorizontalHeaderLabels([str(c) for c in df.columns.tolist()])
            for r in range(len(df)):
                for c, col in enumerate(df.columns):
                    it = QTableWidgetItem(str(df.iat[r, c])); it.setFlags(it.flags() ^ Qt.ItemIsEditable)
                    self.tbl_left.setItem(r, c, it)
        self.tbl_left.resizeColumnsToContents()
        max_width = 220
        for i in range(self.tbl_left.columnCount()):
            w = min(self.tbl_left.columnWidth(i), max_width)
            self.tbl_left.setColumnWidth(i, w)

    # ---------- Right table ----------
    def _renumber_right_rows(self):
        for r in range(self.tbl_right.rowCount()):
            it = self.tbl_right.item(r, 0)
            if it is None:
                it = QTableWidgetItem(); self.tbl_right.setItem(r, 0, it)
            it.setText(str(r+1))
            it.setFlags(it.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            it.setBackground(QBrush(QColor(240,240,240)))

    def _swap_right_rows(self, r1, r2):
        for c in range(self.tbl_right.columnCount()):
            it1 = self.tbl_right.takeItem(r1, c); it2 = self.tbl_right.takeItem(r2, c)
            self.tbl_right.setItem(r1, c, it2); self.tbl_right.setItem(r2, c, it1)

    def add_selected_rows(self):
        if self.filtered_df is None or self.filtered_df.empty: return
        rows = [idx.row() for idx in self.tbl_left.selectionModel().selectedRows()]
        for r in rows:
            row_vals = [self.tbl_left.item(r, c).text() if self.tbl_left.item(r, c) else "" for c in range(self.tbl_left.columnCount())]
            text = " | ".join(row_vals)
            row = self.tbl_right.rowCount(); self.tbl_right.insertRow(row)
            idx_item = QTableWidgetItem(str(row+1))
            idx_item.setFlags(idx_item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsSelectable)
            idx_item.setBackground(QBrush(QColor(240,240,240)))
            self.tbl_right.setItem(row, 0, idx_item)
            self.tbl_right.setItem(row, 1, QTableWidgetItem(text))

    def remove_selected_row(self):
        rows = sorted(set(i.row() for i in self.tbl_right.selectionModel().selectedRows()), reverse=True)
        for r in rows: self.tbl_right.removeRow(r)
        self._renumber_right_rows()

    def clear_selected_all(self):
        self.tbl_right.setRowCount(0)

    def move_up(self):
        r = self.tbl_right.currentRow()
        if r > 0:
            self._swap_right_rows(r, r-1); self.tbl_right.setCurrentCell(r-1, 1); self._renumber_right_rows()

    def move_down(self):
        r = self.tbl_right.currentRow()
        if 0 <= r < self.tbl_right.rowCount()-1:
            self._swap_right_rows(r, r+1); self.tbl_right.setCurrentCell(r+1, 1); self._renumber_right_rows()

    # ---------- Export ----------
    def export_filtered_csv(self):
        if self.filtered_df is None:
            QMessageBox.warning(self, "هشدار", "ابتدا داده را بارگذاری و فیلتر کن."); return
        path, _ = QFileDialog.getSaveFileName(self, "ذخیره نتایج فیلتر", self.last_dir, "CSV Files (*.csv)")
        if not path: return
        try:
            self.filtered_df.to_csv(path, index=False, encoding="utf-8-sig")
            QMessageBox.information(self, "موفق", "CSV نتایج فیلتر ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره فایل ناموفق:\n{e}")

    def export_filtered_xlsx(self):
        if self.filtered_df is None:
            QMessageBox.warning(self, "هشدار", "ابتدا داده را بارگذاری و فیلتر کن."); return
        path, _ = QFileDialog.getSaveFileName(self, "ذخیره Excel نتایج", self.last_dir, "Excel Files (*.xlsx)")
        if not path: return
        try:
            self.filtered_df.to_excel(path, index=False, engine="openpyxl")
            QMessageBox.information(self, "موفق", "Excel نتایج فیلتر ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره فایل ناموفق:\n{e}")

    def export_selected_csv(self):
        rows = self.tbl_right.rowCount()
        if rows == 0:
            QMessageBox.warning(self, "هشدار", "لیست انتخاب‌شده‌ها خالی است."); return
        data = [{"order": self.tbl_right.item(r,0).text(), "item": self.tbl_right.item(r,1).text()} for r in range(rows)]
        df = pd.DataFrame(data)
        path, _ = QFileDialog.getSaveFileName(self, "ذخیره انتخاب‌شده‌ها", self.last_dir, "CSV Files (*.csv)")
        if not path: return
        try:
            df.to_csv(path, index=False, encoding="utf-8-sig")
            QMessageBox.information(self, "موفق", "CSV انتخاب‌شده‌ها ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره فایل ناموفق:\n{e}")

    def export_selected_xlsx(self):
        rows = self.tbl_right.rowCount()
        if rows == 0:
            QMessageBox.warning(self, "هشدار", "لیست انتخاب‌شده‌ها خالی است."); return
        data = [{"order": self.tbl_right.item(r,0).text(), "item": self.tbl_right.item(r,1).text()} for r in range(rows)]
        df = pd.DataFrame(data)
        path, _ = QFileDialog.getSaveFileName(self, "ذخیره انتخاب‌شده‌ها", self.last_dir, "Excel Files (*.xlsx)")
        if not path: return
        try:
            df.to_excel(path, index=False, engine="openpyxl")
            QMessageBox.information(self, "موفق", "Excel انتخاب‌شده‌ها ذخیره شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"ذخیره فایل ناموفق:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
