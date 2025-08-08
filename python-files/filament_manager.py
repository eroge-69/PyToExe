
# -*- coding: utf-8 -*-
"""
3D Filament Manager (Windows) – PySide6
Requirements: pip install PySide6
Launch: python filament_manager.py
"""
import json
import os
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Tuple

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QColor, QIcon, QIntValidator
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFileDialog, QLineEdit, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QSplitter, QFormLayout, QFrame, QStatusBar,
    QGroupBox, QTextEdit
)

APP_TITLE = "Filament Manager"
DB_FILE = "filament_manager.db"

# ----------------------------- Seed catalogs (baked in) -----------------------------

BAMBU_PLA_MATTE = [
    ("Ivory White", "#FFFFFF"),
    ("Bone White", "#CBC6B8"),
    ("Desert Tan", "#E8DBB7"),
    ("Latte Brown", "#D3B7A7"),
    ("Caramel", "#AE835B"),
    ("Terracotta", "#B15533"),
    ("Dark Brown", "#7D6556"),
    ("Dark Chocolate", "#4D3324"),
    ("Lilac Purple", "#AE96D4"),
    ("Sakura Pink", "#E8AFCF"),
    ("Mandarin Orange", "#F99963"),
    ("Lemon Yellow", "#F7D959"),
    ("Plum", "#950051"),
    ("Scarlet Red", "#DE4343"),
    ("Dark Red", "#BB3D43"),
    ("Dark Green", "#68724D"),
    ("Grass Green", "#61C680"),
    ("Apple Green", "#C2E189"),
    ("Ice Blue", "#A3D8E1"),
    ("Sky Blue", "#56B7E6"),
    ("Marine Blue", "#0078BF"),
    ("Dark Blue", "#042F56"),
    ("Ash Gray", "#9B9EA0"),
    ("Nardo Gray", "#757575"),
    ("Charcoal", "#000000"),
]

POLYTERRA_PLA_MATTE = [
    ("Charcoal Black", "#101010"),
    ("Cotton White", "#F5F5F5"),
    ("Fossil Grey", "#8C8C8C"),
    ("Lava Red", "#C0392B"),
    ("Mint", "#98D9B6"),
    ("Sapphire Blue", "#0F52BA"),
    ("Candy", "#FF69B4"),
    ("Sunrise Orange", "#FFA500"),
    ("Arctic Teal", "#4CA6A8"),
    ("Earth Brown", "#7B4F2A"),
    ("Savannah Yellow", "#FFD44D"),
    ("Pastel Rainbow", "#E6C9F2"),
    ("Army Dark Green", "#556B2F"),
    ("Rose", "#F4C2C2"),
    ("Peanut", "#C6A664"),
    ("Muted Blue", "#6FA8DC"),
    ("Wood Brown", "#8B5A2B"),
    ("Muted White", "#F0F0F0"),
    ("Forrest Green", "#228B22"),
    ("Periwinkle", "#CCCCFF"),
    ("Peach", "#FFDAB9"),
    ("Lime Green", "#32CD32"),
    ("Army Brown", "#6B4423"),
    ("Army Purple", "#7D3C98"),
    ("Marble White", "#EAEAEA"),
    ("Marble Slate Grey", "#B0B0B0"),
    ("Marble Limestone", "#D9D9D9"),
    ("Marble Sandstone", "#D3C4A7"),
    ("Electric Indigo", "#6F00FF"),
    ("Banana", "#FFE135"),
]

# ----------------------------- Data layer -----------------------------

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS manufacturers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS filament_types(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(manufacturer_id, name),
            FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id) ON DELETE CASCADE
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS colors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER NOT NULL,
            type_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            hex TEXT NOT NULL,
            UNIQUE(manufacturer_id, type_id, name),
            FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id) ON DELETE CASCADE,
            FOREIGN KEY(type_id) REFERENCES filament_types(id) ON DELETE CASCADE
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color_id INTEGER NOT NULL,
            in_stock INTEGER NOT NULL DEFAULT 0,
            on_order INTEGER NOT NULL DEFAULT 0,
            min_level INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(color_id) REFERENCES colors(id) ON DELETE CASCADE
        );
        """)
        conn.commit()

def seed_catalog_if_empty():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM manufacturers;")
        if c.fetchone()[0] > 0:
            return
        # Insert manufacturers
        c.execute("INSERT INTO manufacturers(name) VALUES (?)", ("Bambu Lab",))
        bambu_id = c.lastrowid
        c.execute("INSERT INTO filament_types(manufacturer_id, name) VALUES(?,?)", (bambu_id, "PLA Matte"))
        bambu_type_id = c.lastrowid

        for name, hx in BAMBU_PLA_MATTE:
            c.execute("INSERT INTO colors(manufacturer_id, type_id, name, hex) VALUES(?,?,?,?)",
                      (bambu_id, bambu_type_id, name, hx))
            color_id = c.lastrowid
            c.execute("INSERT INTO inventory(color_id, in_stock, on_order, min_level) VALUES(?,?,?,?)",
                      (color_id, 0, 0, 0))

        c.execute("INSERT INTO manufacturers(name) VALUES (?)", ("Polymaker",))
        poly_id = c.lastrowid
        c.execute("INSERT INTO filament_types(manufacturer_id, name) VALUES(?,?)", (poly_id, "PolyTerra PLA (Matte)"))
        poly_type_id = c.lastrowid

        for name, hx in POLYTERRA_PLA_MATTE:
            c.execute("INSERT INTO colors(manufacturer_id, type_id, name, hex) VALUES(?,?,?,?)",
                      (poly_id, poly_type_id, name, hx))
            color_id = c.lastrowid
            c.execute("INSERT INTO inventory(color_id, in_stock, on_order, min_level) VALUES(?,?,?,?)",
                      (color_id, 0, 0, 0))

        conn.commit()

# ----------------------------- UI helpers -----------------------------

def color_swatch(hex_code: str, size: QSize = QSize(24, 24)) -> QIcon:
    from PySide6.QtGui import QPixmap, QPainter, QBrush
    pix = QPixmap(size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setBrush(QBrush(QColor(hex_code)))
    p.setPen(Qt.black if QColor(hex_code).lightness() > 128 else Qt.white)
    p.drawRect(0, 0, size.width()-1, size.height()-1)
    p.end()
    return QIcon(pix)

# ----------------------------- Main Window -----------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1300, 800)
        self._build_ui()
        self._load_filters()
        self._load_catalog_tree()
        self._load_table()
        self._update_statusbars()

    # UI layout
    def _build_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout(central)

        # Toolbar actions
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Datei")
        act_export = QAction("Exportieren…", self)
        act_export.triggered.connect(self.export_json)
        file_menu.addAction(act_export)
        act_import = QAction("Importieren…", self)
        act_import.triggered.connect(self.import_json)
        file_menu.addAction(act_import)

        edit_menu = menubar.addMenu("Bearbeiten")
        act_add_manu = QAction("Hersteller hinzufügen…", self)
        act_add_manu.triggered.connect(self.add_manufacturer_dialog)
        edit_menu.addAction(act_add_manu)
        act_add_type = QAction("Filamenttyp hinzufügen…", self)
        act_add_type.triggered.connect(self.add_type_dialog)
        edit_menu.addAction(act_add_type)
        act_add_color = QAction("Farbe hinzufügen…", self)
        act_add_color.triggered.connect(self.add_color_dialog)
        edit_menu.addAction(act_add_color)
        act_del_color = QAction("Farbe löschen…", self)
        act_del_color.triggered.connect(self.delete_color_dialog)
        edit_menu.addAction(act_del_color)

        # Filters row
        filters = QHBoxLayout()
        self.cmb_manu = QComboBox()
        self.cmb_type = QComboBox()
        self.cmb_manu.currentIndexChanged.connect(self._on_filter_changed)
        self.cmb_type.currentIndexChanged.connect(self._on_filter_changed)
        filters.addWidget(QLabel("Hersteller:"))
        filters.addWidget(self.cmb_manu)
        filters.addWidget(QLabel("Typ:"))
        filters.addWidget(self.cmb_type)
        filters.addStretch(1)

        # Splitter: left catalog (collapsible), right table (inventory)
        splitter = QSplitter()
        # Left: catalog
        left = QWidget()
        left_layout = QVBoxLayout(left)
        lbl_cat = QLabel("Katalog")
        lbl_cat.setStyleSheet("font-weight:600; font-size:16px;")
        left_layout.addWidget(lbl_cat)
        self.tree = QTreeWidget()
        self.tree.setIconSize(QSize(32,32))
        self.tree.setHeaderLabels(["Farbe", "Hex"])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        left_layout.addWidget(self.tree)
        splitter.addWidget(left)

        # Right: inventory table
        right = QWidget()
        right_layout = QVBoxLayout(right)
        lbl_inv = QLabel("Bestand")
        lbl_inv.setStyleSheet("font-weight:600; font-size:16px;")
        right_layout.addWidget(lbl_inv)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels([
            "Farbe", "Hersteller", "Typ", "Hex", "Bestand", "Bestellt", "Mindestbestand", "Δ Fehlend", "_color_id"
        ])
        self.table.setColumnHidden(8, True)
        self.table.itemChanged.connect(self._on_item_changed)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        right_layout.addWidget(self.table)

        # Editor row with +/- and direct input
        editor = QHBoxLayout()
        self.btn_minus = QPushButton("–")
        self.btn_plus = QPushButton("+")
        self.btn_minus.setFixedWidth(40)
        self.btn_plus.setFixedWidth(40)
        self.btn_minus.clicked.connect(lambda: self.adjust_selected(-1))
        self.btn_plus.clicked.connect(lambda: self.adjust_selected(1))
        editor.addWidget(self.btn_minus)
        editor.addWidget(self.btn_plus)
        editor.addSpacing(12)
        editor.addWidget(QLabel("Setzen:"))
        self.edit_set = QLineEdit()
        self.edit_set.setPlaceholderText("Zahl eingeben…")
        self.edit_set.setValidator(QIntValidator(0, 9999, self))
        btn_apply = QPushButton("Anwenden")
        btn_apply.clicked.connect(self.apply_set_value)
        editor.addWidget(self.edit_set)
        editor.addWidget(btn_apply)
        editor.addStretch(1)
        right_layout.addLayout(editor)

        splitter.addWidget(right)
        splitter.setStretchFactor(1, 3)

        main_layout.addLayout(filters)
        main_layout.addWidget(splitter)

        # Status bars
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.lbl_missing = QLabel("Fehlend: –")
        self.lbl_existing = QLabel("Bestand: –")
        self.status.addWidget(self.lbl_missing, 1)
        self.status.addPermanentWidget(self.lbl_existing, 1)

        self.setCentralWidget(central)

        # Style
        self.setStyleSheet("""
            QMainWindow { background:#171717; color:#EAEAEA; }
            QLabel { color:#EAEAEA; }
            QTreeWidget, QTableWidget { background:#1F1F1F; color:#EAEAEA; border:1px solid #2A2A2A; }
            QHeaderView::section { background:#2A2A2A; color:#EAEAEA; padding:6px; border: none; }
            QLineEdit { background:#1F1F1F; color:#EAEAEA; border:1px solid #2A2A2A; padding:6px; border-radius:6px; }
            QPushButton { background:#2A2A2A; color:#EAEAEA; border:1px solid #3A3A3A; padding:8px 12px; border-radius:8px; }
            QPushButton:hover { background:#3A3A3A; }
        """)

    # Load filters
    def _load_filters(self):
        with get_conn() as conn:
            c = conn.cursor()
            self.cmb_manu.blockSignals(True)
            self.cmb_type.blockSignals(True)
            self.cmb_manu.clear()
            for (mid, name) in c.execute("SELECT id, name FROM manufacturers ORDER BY name;"):
                self.cmb_manu.addItem(name, mid)
            self.cmb_manu.blockSignals(False)
            self._load_types_for_current_manu()
            self.cmb_type.blockSignals(False)

    def _load_types_for_current_manu(self):
        self.cmb_type.clear()
        manu_id = self.cmb_manu.currentData()
        if manu_id is None:
            return
        with get_conn() as conn:
            c = conn.cursor()
            for (tid, name) in c.execute(
                "SELECT id, name FROM filament_types WHERE manufacturer_id=? ORDER BY name;", (manu_id,)
            ):
                self.cmb_type.addItem(name, tid)

    def _on_filter_changed(self):
        self._load_types_for_current_manu()
        self._load_catalog_tree()
        self._load_table()
        self._update_statusbars()

    # Catalog tree
    def _load_catalog_tree(self):
        self.tree.clear()
        manu_id = self.cmb_manu.currentData()
        type_id = self.cmb_type.currentData()
        if manu_id is None or type_id is None:
            return
        manu_name = self.cmb_manu.currentText()
        type_name = self.cmb_type.currentText()
        root = QTreeWidgetItem([f"{manu_name} – {type_name}", ""])
        self.tree.addTopLevelItem(root)
        with get_conn() as conn:
            c = conn.cursor()
            for (cid, name, hx) in c.execute(
                "SELECT id, name, hex FROM colors WHERE manufacturer_id=? AND type_id=? ORDER BY name;",
                (manu_id, type_id)
            ):
                item = QTreeWidgetItem([name, hx])
                item.setIcon(0, color_swatch(hx, QSize(24, 24)))
                root.addChild(item)
        self.tree.expandAll()

    # Inventory table
    def _load_table(self):
        manu_id = self.cmb_manu.currentData()
        type_id = self.cmb_type.currentData()
        with get_conn() as conn:
            c = conn.cursor()
            rows = list(c.execute("""
                SELECT colors.name, m.name, t.name, colors.hex, inventory.in_stock, inventory.on_order, inventory.min_level, colors.id
                FROM inventory
                JOIN colors ON colors.id = inventory.color_id
                JOIN manufacturers m ON m.id = colors.manufacturer_id
                JOIN filament_types t ON t.id = colors.type_id
                WHERE colors.manufacturer_id = ? AND colors.type_id = ?
                ORDER BY colors.name;
            """, (manu_id, type_id)))
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            name, manu, typ, hx, stock, on_order, minlvl, color_id = row
            delta_missing = stock - minlvl
            values = [name, manu, typ, hx, stock, on_order, minlvl, delta_missing, color_id]
            for cidx, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                if cidx in (4,5,6,7):
                    item.setTextAlignment(Qt.AlignCenter)
                if cidx == 3:
                    item.setIcon(color_swatch(hx, QSize(16,16)))
                # Editable columns: stock (4), on_order (5), minlvl (6)
                if cidx in (4,5,6):
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, cidx, item)

            # Row highlight for low stock
            if stock < minlvl:
                self._set_row_color(r, QColor(60, 0, 0))  # red-ish
            elif on_order > 0 and stock < minlvl:
                self._set_row_color(r, QColor(60, 40, 0))  # amber-ish
            elif on_order > 0:
                self._set_row_color(r, QColor(35, 35, 0))  # subtle amber
            else:
                self._set_row_color(r, QColor(25, 25, 25))

        self.table.resizeRowsToContents()

    def _set_row_color(self, row: int, color: QColor):
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(color)

    # Adjust stock
    def _selected_color_id(self) -> int | None:
        sel = self.table.currentRow()
        if sel < 0:
            return None
        return int(self.table.item(sel, 7).data(Qt.DisplayRole) or 0)  # color_id was not stored here; adapt approach

    def _selected_row_ids(self) -> Tuple[int, int] | Tuple[None, None]:
        sel = self.table.currentRow()
        if sel < 0:
            return None, None
        color_id = int(self.table.item(sel, 8).text())
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM inventory WHERE color_id=?", (color_id,))
            res = c.fetchone()
            if res:
                return color_id, res[0]
        return None, None

    def adjust_selected(self, delta: int):
        color_id, inv_id = self._selected_row_ids()
        if inv_id is None:
            return
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("UPDATE inventory SET in_stock = MAX(0, in_stock + ?) WHERE id=?;", (delta, inv_id))
            conn.commit()
        self._load_table()
        self._update_statusbars()

    
    def _on_item_changed(self, item: QTableWidgetItem):
        row = item.row()
        col = item.column()
        if col not in (4,5,6):
            return
        try:
            val = int(item.text())
        except ValueError:
            return
        color_id = int(self.table.item(row, 8).text())
        with get_conn() as conn:
            c = conn.cursor()
            if col == 4:
                c.execute("UPDATE inventory SET in_stock=? WHERE color_id=?", (val, color_id))
            elif col == 5:
                c.execute("UPDATE inventory SET on_order=? WHERE color_id=?", (val, color_id))
            elif col == 6:
                c.execute("UPDATE inventory SET min_level=? WHERE color_id=?", (val, color_id))
            conn.commit()
        # Prevent recursive signals by temporarily blocking
        self.table.blockSignals(True)
        self._load_table()
        self.table.blockSignals(False)
        self._update_statusbars()


    def apply_set_value(self):
        if not self.edit_set.text():
            return
        val = int(self.edit_set.text())
        color_id, inv_id = self._selected_row_ids()
        if inv_id is None:
            return
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("UPDATE inventory SET in_stock=? WHERE id=?;", (val, inv_id))
            conn.commit()
        self.edit_set.clear()
        self._load_table()
        self._update_statusbars()

    # Status bars aggregation
    def _update_statusbars(self):
        manu_id = self.cmb_manu.currentData()
        type_id = self.cmb_type.currentData()
        with get_conn() as conn:
            c = conn.cursor()
            missing = list(c.execute("""
                SELECT colors.name, (inventory.min_level - inventory.in_stock) AS need
                FROM inventory JOIN colors ON colors.id = inventory.color_id
                WHERE colors.manufacturer_id=? AND colors.type_id=? AND inventory.min_level > inventory.in_stock
                ORDER BY colors.name;
            """, (manu_id, type_id)))
            existing = list(c.execute("""
                SELECT colors.name, inventory.in_stock
                FROM inventory JOIN colors ON colors.id = inventory.color_id
                WHERE colors.manufacturer_id=? AND colors.type_id=? AND inventory.in_stock > 0
                ORDER BY colors.name;
            """, (manu_id, type_id)))
        miss_txt = ", ".join([f"{n} (–{need})" for n, need in missing]) if missing else "–"
        ex_txt = ", ".join([f"{n} ({qty})" for n, qty in existing]) if existing else "–"
        self.lbl_missing.setText(f"Fehlend: {miss_txt}")
        self.lbl_existing.setText(f"Bestand: {ex_txt}")

    # CRUD dialogs
    def add_manufacturer_dialog(self):
        name, ok = self._simple_prompt("Neuer Hersteller", "Name")
        if not ok or not name:
            return
        with get_conn() as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO manufacturers(name) VALUES (?)", (name,))
                conn.commit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Hinweis", "Hersteller existiert bereits.")
                return
        self._load_filters()

    def add_type_dialog(self):
        manu_id = self.cmb_manu.currentData()
        if manu_id is None:
            return
        name, ok = self._simple_prompt("Neuer Filamenttyp", "Name (z. B. PLA Matte)")
        if not ok or not name:
            return
        with get_conn() as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO filament_types(manufacturer_id, name) VALUES(?,?)", (manu_id, name))
                conn.commit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Hinweis", "Filamenttyp existiert bereits.")
                return
        self._load_filters()
        self._load_catalog_tree()
        self._load_table()

    def add_color_dialog(self):
        manu_id = self.cmb_manu.currentData()
        type_id = self.cmb_type.currentData()
        if manu_id is None or type_id is None:
            return
        dlg = QWidget()
        dlg.setWindowTitle("Neue Farbe hinzufügen")
        layout = QFormLayout(dlg)
        name = QLineEdit()
        hx = QLineEdit()
        hx.setPlaceholderText("#RRGGBB")
        layout.addRow("Name:", name)
        layout.addRow("Hex:", hx)
        btns = QHBoxLayout()
        okb = QPushButton("Hinzufügen")
        cancel = QPushButton("Abbrechen")
        btns.addWidget(okb); btns.addWidget(cancel)
        layout.addRow(btns)
        okb.clicked.connect(dlg.accept if hasattr(dlg, "accept") else lambda: None)
        cancel.clicked.connect(dlg.close)
        # emulate modal
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.show()
        app = QApplication.instance()
        while dlg.isVisible():
            app.processEvents()
        # After close, read values
        n = name.text().strip()
        h = hx.text().strip() or "#808080"
        if not n:
            return
        with get_conn() as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO colors(manufacturer_id, type_id, name, hex) VALUES(?,?,?,?)",
                          (manu_id, type_id, n, h))
                color_id = c.lastrowid
                c.execute("INSERT INTO inventory(color_id, in_stock, on_order, min_level) VALUES(?,?,?,?)",
                          (color_id, 0, 0, 0))
                conn.commit()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Hinweis", "Farbe existiert bereits.")
                return
        self._load_catalog_tree()
        self._load_table()

    def delete_color_dialog(self):
        sel = self.table.currentRow()
        if sel < 0:
            return
        name = self.table.item(sel, 0).text()
        if QMessageBox.question(self, "Löschen", f"„{name}“ löschen?") != QMessageBox.Yes:
            return
        manu = self.table.item(sel, 1).text()
        typ = self.table.item(sel, 2).text()
        with get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                DELETE FROM colors
                WHERE id IN (
                    SELECT colors.id
                    FROM colors
                    JOIN manufacturers m ON m.id = colors.manufacturer_id
                    JOIN filament_types t ON t.id = colors.type_id
                    WHERE colors.name=? AND m.name=? AND t.name=?
                )
            """, (name, manu, typ))
            conn.commit()
        self._load_catalog_tree()
        self._load_table()

    # Import/Export
    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exportieren", "filament_export.json", "JSON (*.json)")
        if not path:
            return
        data = {}
        with get_conn() as conn:
            c = conn.cursor()
            # manufacturers
            data["manufacturers"] = [{"id": mid, "name": name} for (mid, name) in c.execute("SELECT id, name FROM manufacturers;")]
            data["filament_types"] = [
                {"id": tid, "manufacturer_id": mid, "name": name}
                for (tid, mid, name) in c.execute("SELECT id, manufacturer_id, name FROM filament_types;")
            ]
            data["colors"] = [
                {"id": cid, "manufacturer_id": mid, "type_id": tid, "name": name, "hex": hx}
                for (cid, mid, tid, name, hx) in c.execute("SELECT id, manufacturer_id, type_id, name, hex FROM colors;")
            ]
            data["inventory"] = [
                {"color_id": cid, "in_stock": s, "on_order": oo, "min_level": ml}
                for (cid, s, oo, ml) in c.execute("""
                    SELECT color_id, in_stock, on_order, min_level FROM inventory;
                """)
            ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importieren", "", "JSON (*.json)")
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with get_conn() as conn:
            c = conn.cursor()
            # Clear current
            c.execute("DELETE FROM inventory;")
            c.execute("DELETE FROM colors;")
            c.execute("DELETE FROM filament_types;")
            c.execute("DELETE FROM manufacturers;")
            # Recreate
            for m in data.get("manufacturers", []):
                try:
                    c.execute("INSERT INTO manufacturers(id, name) VALUES(?, ?)", (m["id"], m["name"]))
                except sqlite3.IntegrityError:
                    pass
            for t in data.get("filament_types", []):
                try:
                    c.execute("INSERT INTO filament_types(id, manufacturer_id, name) VALUES(?, ?, ?)", (t["id"], t["manufacturer_id"], t["name"]))
                except sqlite3.IntegrityError:
                    pass
            for col in data.get("colors", []):
                try:
                    c.execute("INSERT INTO colors(id, manufacturer_id, type_id, name, hex) VALUES(?, ?, ?, ?, ?)",
                              (col["id"], col["manufacturer_id"], col["type_id"], col["name"], col["hex"]))
                except sqlite3.IntegrityError:
                    pass
            for inv in data.get("inventory", []):
                c.execute("INSERT INTO inventory(color_id, in_stock, on_order, min_level) VALUES(?,?,?,?)",
                          (inv["color_id"], inv.get("in_stock", 0), inv.get("on_order", 0), inv.get("min_level", 0)))
            conn.commit()
        self._load_filters()
        self._load_catalog_tree()
        self._load_table()
        self._update_statusbars()

    # Simple input helper
    def _simple_prompt(self, title: str, label: str) -> Tuple[str, bool]:
        w = QWidget()
        w.setWindowTitle(title)
        fl = QFormLayout(w)
        field = QLineEdit()
        fl.addRow(label + ":", field)
        btns = QHBoxLayout()
        okb = QPushButton("OK")
        cancel = QPushButton("Abbrechen")
        btns.addWidget(okb); btns.addWidget(cancel)
        fl.addRow(btns)
        result = {"ok": False}
        def do_ok():
            result["ok"] = True
            w.close()
        okb.clicked.connect(do_ok)
        cancel.clicked.connect(w.close)
        w.setWindowModality(Qt.ApplicationModal)
        w.show()
        app = QApplication.instance()
        while w.isVisible():
            app.processEvents()
        return field.text().strip(), result["ok"]

def main():
    init_db()
    seed_catalog_if_empty()
    app = QApplication([])
    win = MainWindow()
    win.show()
    app.exec()

if __name__ == "__main__":
    main()
