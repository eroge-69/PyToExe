# -*- coding: utf-8 -*-
"""
Lagerverwaltung – Desktop-App (PyQt6, Einzeldatei)

Funktionen:
- Artikel erfassen/bearbeiten/löschen
- Bilder als Thumbnails in der Liste
- Anhänge-Ordner pro Artikel (attachments/<id>/)
- Kategorien & Regale verwalten
- Suche (Name, Nummer, Hersteller, Kategorie, Preis, Regal, Lagerort, Notiz)
- Sortierung (A–Z Name, Datum neu→alt / alt→neu)
- Spaltenbreiten per Maus einstellbar, Wortumbruch in Zellen aktiviert
- Mindestbestand gelb markiert, Text dann schwarz; Bestandszahl zentriert & fett
- Autosave + JSON-Backups mit Zeitstempel-Dateinamen; CSV Import/Export
- Spalten ein-/ausblendbar; Spaltenbreiten & Einstellungen werden gespeichert

Voraussetzungen:
    pip install PyQt6

Optional (nur für besseres PNG/JPG-Handling nicht nötig):
    pip install pillow

Tipp: Mit auto-py-to-exe oder PyInstaller zu einer .exe packen.
"""
from __future__ import annotations
import sys, os, json, csv, shutil, uuid, datetime
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap, QAction, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QSpinBox, QDoubleSpinBox,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QCheckBox, QSplitter, QDialog, QListWidget, QListWidgetItem,
    QToolBar
)

APP_TITLE = "📦 Lagerverwaltung (Desktop)"
DEFAULT_DATA = {
    "items": [],
    "cats": ["Allgemein"],
    "shelves": {"R1": {"levels": 3, "cols": 5, "bins": 10}},
    "settings": {
        "theme": "dark",
        "autosave": False,
        "sortMode": "name_asc",
        "columns": {
            "img": True, "name": True, "sku": True, "maker": True, "cat": True,
            "shelf": True, "loc": True, "qty": True, "price": True, "note": True
        },
        "colWidths": {}
    }
}

COLS = [
    ("img", "Bild", 80),
    ("name", "Bezeichnung", 240),
    ("sku", "Art.-Nr.", 120),
    ("maker", "Hersteller", 140),
    ("cat", "Kategorie", 120),
    ("shelf", "Regal", 80),
    ("loc", "Lagerort", 110),
    ("qty", "Bestand", 90),
    ("price", "Preis €", 90),
    ("note", "Notiz", 260),
]


@dataclass
class InventoryItem:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    createdAt: int = field(default_factory=lambda: int(datetime.datetime.now().timestamp()*1000))
    name: str = ""
    sku: str = ""
    maker: str = ""
    cat: str = "Allgemein"
    price: float = 0.0
    shelf: str = "R1"
    level: int = 1
    col: int = 1
    bin: int = 1
    qty: int = 0
    minQty: int = 0
    note: str = ""
    image_path: str = ""  # relativ zum Datenordner (images/<id>.<ext>)
    attachments: List[str] = field(default_factory=list)  # Dateinamen in attachments/<id>/

    def location_str(self) -> str:
        return f"B:{self.level} S:{self.col} F:{self.bin}"


class SettingsDialog(QDialog):
    def __init__(self, parent: 'MainWindow'):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen, Spalten, Kategorien & Regale")
        self.parent = parent
        self.resize(820, 520)

        layout = QVBoxLayout(self)

        # Theme + Autosave + Sortierung
        tl = QHBoxLayout()
        layout.addLayout(tl)
        self.cmbTheme = QComboBox(); self.cmbTheme.addItems(["dark", "light"]) 
        self.cmbTheme.setCurrentText(parent.settings.get("theme","dark"))
        tl.addWidget(QLabel("Theme:")); tl.addWidget(self.cmbTheme)

        self.chkAutosave = QCheckBox("Auto‑Speichern")
        self.chkAutosave.setChecked(bool(parent.settings.get("autosave", False)))
        tl.addWidget(self.chkAutosave)

        self.cmbSort = QComboBox(); self.cmbSort.addItems(["name_asc","date_desc","date_asc"]) 
        self.cmbSort.setCurrentText(parent.settings.get("sortMode","name_asc"))
        tl.addWidget(QLabel("Sortierung:")); tl.addWidget(self.cmbSort); tl.addStretch(1)

        # Spalten toggles
        layout.addWidget(QLabel("Spalten ein-/ausblenden:"))
        self.colsWrap = QHBoxLayout(); layout.addLayout(self.colsWrap)
        self.colChecks: Dict[str,QCheckBox] = {}
        for key, title, _ in COLS:
            cb = QCheckBox(title)
            cb.setChecked(bool(parent.settings.get("columns",{}).get(key, True)))
            self.colChecks[key] = cb
            self.colsWrap.addWidget(cb)
        self.colsWrap.addStretch(1)

        # Kategorien
        layout.addWidget(QLabel("Kategorien:"))
        kh = QHBoxLayout(); layout.addLayout(kh)
        self.lstCats = QListWidget(); self.lstCats.addItems(parent.cats)
        self.edCat = QLineEdit(); self.edCat.setPlaceholderText("Neue Kategorie…")
        btnAddCat = QPushButton("+ Hinzufügen"); btnDelCat = QPushButton("Löschen")
        kh.addWidget(self.lstCats, 3)
        right = QVBoxLayout(); kh.addLayout(right,2)
        right.addWidget(self.edCat); right.addWidget(btnAddCat); right.addWidget(btnDelCat); right.addStretch(1)
        btnAddCat.clicked.connect(self.add_cat)
        btnDelCat.clicked.connect(self.del_cat)

        # Regale
        layout.addWidget(QLabel("Regalsystem (Name, Böden, Spalten, Fächer):"))
        sh = QHBoxLayout(); layout.addLayout(sh)
        self.lstShelves = QListWidget();
        for n, s in parent.shelves.items():
            QListWidgetItem(f"{n} – B:{s['levels']} S:{s['cols']} F:{s['bins']}", self.lstShelves)
        self.edShelfName = QLineEdit(); self.edShelfName.setPlaceholderText("Regalname z. B. R1")
        self.spLevels = QSpinBox(); self.spLevels.setRange(1, 999); self.spLevels.setValue(3)
        self.spCols   = QSpinBox(); self.spCols.setRange(1, 999); self.spCols.setValue(5)
        self.spBins   = QSpinBox(); self.spBins.setRange(1, 999); self.spBins.setValue(10)
        btnAddShelf = QPushButton("+ Regal speichern"); btnDelShelf = QPushButton("Regal löschen")
        sh.addWidget(self.lstShelves, 3)
        shelfRight = QGridLayout();
        sh2 = QWidget(); sh2.setLayout(shelfRight); sh.addWidget(sh2,2)
        shelfRight.addWidget(QLabel("Name"),0,0); shelfRight.addWidget(self.edShelfName,0,1)
        shelfRight.addWidget(QLabel("Böden"),1,0); shelfRight.addWidget(self.spLevels,1,1)
        shelfRight.addWidget(QLabel("Spalten"),2,0); shelfRight.addWidget(self.spCols,2,1)
        shelfRight.addWidget(QLabel("Fächer"),3,0); shelfRight.addWidget(self.spBins,3,1)
        shelfRight.addWidget(btnAddShelf,4,0); shelfRight.addWidget(btnDelShelf,4,1)
        btnAddShelf.clicked.connect(self.add_shelf)
        btnDelShelf.clicked.connect(self.del_shelf)

        # Buttons
        bb = QHBoxLayout(); layout.addLayout(bb)
        btnOk = QPushButton("Speichern"); btnCancel = QPushButton("Schließen")
        bb.addStretch(1); bb.addWidget(btnOk); bb.addWidget(btnCancel)
        btnCancel.clicked.connect(self.reject)
        btnOk.clicked.connect(self.apply_and_close)

    def add_cat(self):
        v = self.edCat.text().strip()
        if not v: return
        if v not in self.parent.cats:
            self.parent.cats.append(v)
            self.lstCats.addItem(v)
        self.edCat.clear()

    def del_cat(self):
        it = self.lstCats.currentItem()
        if not it: return
        name = it.text()
        if name == "Allgemein":
            QMessageBox.warning(self, "Hinweis", "Standardkategorie kann nicht gelöscht werden.")
            return
        self.parent.cats = [c for c in self.parent.cats if c != name]
        # Artikel auf Allgemein setzen
        for it2 in self.parent.items:
            if it2.cat == name:
                it2.cat = "Allgemein"
        self.lstCats.takeItem(self.lstCats.currentRow())

    def add_shelf(self):
        n = self.edShelfName.text().strip()
        if not n: return
        self.parent.shelves[n] = {"levels": self.spLevels.value(), "cols": self.spCols.value(), "bins": self.spBins.value()}
        self.lstShelves.addItem(f"{n} – B:{self.spLevels.value()} S:{self.spCols.value()} F:{self.spBins.value()}")
        self.edShelfName.clear()

    def del_shelf(self):
        it = self.lstShelves.currentItem()
        if not it: return
        name = it.text().split(" – ")[0]
        if name in self.parent.shelves:
            del self.parent.shelves[name]
            # Artikel ggf. auf beliebiges vorhandenes Regal umstellen
            fallback = next(iter(self.parent.shelves.keys()), "R1")
            for a in self.parent.items:
                if a.shelf == name:
                    a.shelf = fallback
            self.lstShelves.takeItem(self.lstShelves.currentRow())

    def apply_and_close(self):
        self.parent.settings["theme"] = self.cmbTheme.currentText()
        self.parent.settings["autosave"] = self.chkAutosave.isChecked()
        self.parent.settings["sortMode"] = self.cmbSort.currentText()
        # Spalten
        for key in self.colChecks:
            self.parent.settings.setdefault("columns", {})[key] = self.colChecks[key].isChecked()
        self.parent.apply_theme()
        self.parent.persist()
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1280, 800)

        self.data_folder = None  # wird über "Datenordner auswählen" gesetzt
        self.items: List[InventoryItem] = []
        self.cats: List[str] = DEFAULT_DATA["cats"].copy()
        self.shelves: Dict[str, Dict[str,int]] = json.loads(json.dumps(DEFAULT_DATA["shelves"]))
        self.settings: Dict[str, Any] = json.loads(json.dumps(DEFAULT_DATA["settings"]))

        # Widgets
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central)

        # Toolbar
        tb = QToolBar()
        self.addToolBar(tb)
        actFolder = QAction("Datenordner wählen", self); actFolder.triggered.connect(self.choose_folder)
        actLoad = QAction("Jetzt laden", self); actLoad.triggered.connect(self.load_from_folder)
        actSave = QAction("Jetzt speichern", self); actSave.triggered.connect(lambda: self.save_to_folder(with_backup=True))
        actCSVImp = QAction("CSV Import", self); actCSVImp.triggered.connect(self.import_csv)
        actCSVExp = QAction("CSV Export", self); actCSVExp.triggered.connect(self.export_csv)
        actJSONExp = QAction("JSON Export", self); actJSONExp.triggered.connect(self.export_json)
        actJSONImp = QAction("JSON Import", self); actJSONImp.triggered.connect(self.import_json)
        actSettings = QAction("Einstellungen", self); actSettings.triggered.connect(self.open_settings)
        actDeleteSel = QAction("Auswahl löschen", self); actDeleteSel.triggered.connect(self.delete_selected)
        tb.addAction(actFolder); tb.addAction(actLoad); tb.addAction(actSave)
        tb.addSeparator(); tb.addAction(actCSVImp); tb.addAction(actCSVExp); tb.addAction(actJSONImp); tb.addAction(actJSONExp)
        tb.addSeparator(); tb.addAction(actSettings); tb.addAction(actDeleteSel)

        # Suche
        sh = QHBoxLayout(); root.addLayout(sh)
        self.edSearch = QLineEdit(); self.edSearch.setPlaceholderText("Suche … (z. B. Preis: 9.99, Regal:R1)")
        btnSearch = QPushButton("Suchen"); btnClear = QPushButton("Suche löschen")
        sh.addWidget(self.edSearch, 1); sh.addWidget(btnSearch); sh.addWidget(btnClear)
        btnSearch.clicked.connect(self.apply_search)
        btnClear.clicked.connect(self.clear_search)

        # Splitter: links Formular, rechts Liste
        split = QSplitter(); root.addWidget(split, 1)

        # Links – Formular
        left = QWidget(); split.addWidget(left)
        form = QGridLayout(left); form.setContentsMargins(4,4,4,4)

        row = 0
        self.edName = QLineEdit(); form.addWidget(QLabel("Bezeichnung *"), row, 0); form.addWidget(self.edName, row, 1); row+=1
        self.edSKU = QLineEdit(); form.addWidget(QLabel("Artikelnummer"), row, 0); form.addWidget(self.edSKU, row, 1); row+=1
        self.edMaker = QLineEdit(); form.addWidget(QLabel("Hersteller"), row, 0); form.addWidget(self.edMaker, row, 1); row+=1
        self.cmbCat = QComboBox(); self.cmbCat.addItems(self.cats)
        form.addWidget(QLabel("Kategorie"), row, 0); form.addWidget(self.cmbCat, row, 1); row+=1
        self.cmbShelf = QComboBox(); self.cmbShelf.addItems(list(self.shelves.keys()))
        form.addWidget(QLabel("Regal"), row, 0); form.addWidget(self.cmbShelf, row, 1); row+=1
        self.spLevel = QSpinBox(); self.spLevel.setRange(1, 999)
        form.addWidget(QLabel("Boden"), row, 0); form.addWidget(self.spLevel, row, 1); row+=1
        self.spCol = QSpinBox(); self.spCol.setRange(1, 999)
        form.addWidget(QLabel("Spalte"), row, 0); form.addWidget(self.spCol, row, 1); row+=1
        self.spBin = QSpinBox(); self.spBin.setRange(1, 999)
        form.addWidget(QLabel("Fach"), row, 0); form.addWidget(self.spBin, row, 1); row+=1
        self.spMin = QSpinBox(); self.spMin.setRange(0, 10_000)
        form.addWidget(QLabel("Mindestbestand"), row, 0); form.addWidget(self.spMin, row, 1); row+=1
        self.spQty = QSpinBox(); self.spQty.setRange(0, 1_000_000)
        incRow = QHBoxLayout();
        btnIn = QPushButton("+1"); btnOut = QPushButton("−1")
        btnIn.clicked.connect(lambda: self.spQty.setValue(self.spQty.value()+1))
        btnOut.clicked.connect(lambda: self.spQty.setValue(max(0, self.spQty.value()-1)))
        incWrap = QWidget(); incWrap.setLayout(incRow)
        incRow.addWidget(self.spQty); incRow.addWidget(btnIn); incRow.addWidget(btnOut)
        form.addWidget(QLabel("Bestand"), row, 0); form.addWidget(incWrap, row, 1); row+=1
        self.spPrice = QDoubleSpinBox(); self.spPrice.setRange(0, 1_000_000); self.spPrice.setDecimals(2)
        form.addWidget(QLabel("Preis (€)"), row, 0); form.addWidget(self.spPrice, row, 1); row+=1
        self.edNote = QTextEdit(); self.edNote.setPlaceholderText("z. B. Maße, Farbe, Hinweise …")
        form.addWidget(QLabel("Notiz"), row, 0); form.addWidget(self.edNote, row, 1); row+=1

        # Bild & Anhänge
        imgRow = QHBoxLayout(); imgWrap = QWidget(); imgWrap.setLayout(imgRow)
        self.lblPreview = QLabel(); self.lblPreview.setFixedSize(120, 90); self.lblPreview.setStyleSheet("border:1px solid gray; border-radius:8px;")
        btnPickImg = QPushButton("Bild wählen…")
        btnPickAtt = QPushButton("Anhänge hinzufügen…")
        imgRow.addWidget(self.lblPreview); imgRow.addWidget(btnPickImg); imgRow.addWidget(btnPickAtt); imgRow.addStretch(1)
        form.addWidget(imgWrap, row, 0, 1, 2); row+=1
        btnPickImg.clicked.connect(self.choose_image)
        btnPickAtt.clicked.connect(self.add_attachments)

        # Form-Buttons
        fb = QHBoxLayout(); form.addLayout(fb, row, 0, 1, 2); row+=1
        self.btnSave = QPushButton("Speichern"); self.btnDelete = QPushButton("Löschen"); self.btnReset = QPushButton("Maske leeren")
        fb.addWidget(self.btnSave); fb.addWidget(self.btnDelete); fb.addWidget(self.btnReset); fb.addStretch(1)
        self.btnSave.clicked.connect(self.save_item_from_form)
        self.btnDelete.clicked.connect(self.delete_current)
        self.btnReset.clicked.connect(self.reset_form)

        # Rechts – Tabelle
        right = QWidget(); split.addWidget(right)
        v = QVBoxLayout(right)
        self.table = QTableWidget(0, len(COLS))
        v.addWidget(self.table)
        headers = [title for _, title, _ in COLS]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setWordWrap(True)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self.load_selected_into_form)

        # Column widths
        for i, (_, _, w) in enumerate(COLS):
            self.table.setColumnWidth(i, self.settings.get("colWidths", {}).get(str(i), w))
        self.table.horizontalHeader().sectionResized.connect(self.on_col_resized)

        # Suchtimer (Enter/Tippen)
        self.edSearch.returnPressed.connect(self.apply_search)

        # Interner Zustand fürs Formular
        self.current_edit_id: str | None = None
        self.current_image_temp: str | None = None  # Pfad zu ausgewähltem Bild, noch nicht kopiert
        self.current_attachments_temp: List[str] = []  # Pfade

        # Theme anwenden
        self.apply_theme()

        # Autosave-Timer (falls aktiv)
        self.auto_timer = QTimer(self)
        self.auto_timer.setInterval(5000)
        self.auto_timer.timeout.connect(self.maybe_autosave)
        self.auto_timer.start()

        # Initiales Rendering
        self.render_table()

    # ==== Theme ====
    def apply_theme(self):
        if self.settings.get("theme") == "dark":
            QApplication.setStyle("Fusion")
            from PyQt6.QtGui import QPalette, QColor
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(25,25,30))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(18,18,22))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30,30,36))
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(45,45,55))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            QApplication.setPalette(palette)
        else:
            QApplication.setStyle("Fusion")
            QApplication.setPalette(QApplication.style().standardPalette())

    # ==== Datei/Ordner ====
    def choose_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Datenordner auswählen")
        if d:
            self.data_folder = d
            QMessageBox.information(self, "OK", f"Datenordner gesetzt:\n{d}")
            # sicherstellen: Unterordner
            os.makedirs(self.images_dir(), exist_ok=True)
            os.makedirs(self.attachments_dir(), exist_ok=True)
            self.persist()

    def inventory_path(self):
        return os.path.join(self.data_folder or os.getcwd(), "inventory.json")

    def images_dir(self):
        return os.path.join(self.data_folder or os.getcwd(), "images")

    def attachments_dir(self):
        return os.path.join(self.data_folder or os.getcwd(), "attachments")

    def timestamp_name(self):
        d = datetime.datetime.now()
        return d.strftime("%Y-%m-%d_%H-%M-%S")

    def persist(self):
        data = {
            "items": [asdict(x) for x in self.items],
            "cats": self.cats,
            "shelves": self.shelves,
            "settings": self.settings,
        }
        try:
            with open(self.inventory_path(), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Speichern fehlgeschlagen: {e}")

    def save_to_folder(self, with_backup=False):
        if not self.data_folder:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst einen Datenordner wählen.")
            return
        self.persist()
        if with_backup:
            backup_name = f"inventory_{self.timestamp_name()}.json"
            shutil.copy2(self.inventory_path(), os.path.join(self.data_folder, backup_name))
        QMessageBox.information(self, "Gespeichert", "Daten gespeichert.")

    def load_from_folder(self):
        if not self.data_folder:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst einen Datenordner wählen.")
            return
        try:
            with open(self.inventory_path(), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.items = [InventoryItem(**it) for it in data.get("items", [])]
            self.cats = data.get("cats", self.cats)
            self.shelves = data.get("shelves", self.shelves)
            self.settings.update(data.get("settings", {}))
            # UI aktualisieren
            self.cmbCat.clear(); self.cmbCat.addItems(self.cats)
            self.cmbShelf.clear(); self.cmbShelf.addItems(list(self.shelves.keys()))
            self.apply_theme()
            self.render_table()
            QMessageBox.information(self, "OK", "Aus Ordner geladen.")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Laden fehlgeschlagen: {e}")

    # ==== Tabelle ====
    def current_columns(self):
        cols = []
        for key, title, width in COLS:
            if self.settings.get("columns", {}).get(key, True):
                cols.append((key, title, width))
        return cols

    def render_table(self):
        cols = self.current_columns()
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels([t for _, t, _ in cols])

        src = list(self.items)
        sm = self.settings.get("sortMode", "name_asc")
        if sm == "name_asc":
            src.sort(key=lambda x: (x.name or ""))
        elif sm == "date_desc":
            src.sort(key=lambda x: x.createdAt, reverse=True)
        elif sm == "date_asc":
            src.sort(key=lambda x: x.createdAt)

        q = (self.edSearch.text() or "").strip().lower()
        if q:
            def matches(it: InventoryItem):
                hay = f"{it.name} {it.sku} {it.maker} {it.cat} {it.note} {it.price} {it.shelf} {it.location_str()}".lower()
                return q in hay
            src = [x for x in src if matches(x)]

        self.table.setRowCount(len(src))
        bold_font = QFont(); bold_font.setBold(True)
        for r, it in enumerate(src):
            for c, (key, _, _) in enumerate(cols):
                if key == "img":
                    item = QTableWidgetItem()
                    if it.image_path:
                        p = QPixmap(os.path.join(self.data_folder or os.getcwd(), it.image_path))
                        if not p.isNull():
                            p = p.scaled(QSize(64, 48), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            item.setData(Qt.ItemDataRole.DecorationRole, p)
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                elif key == "loc":
                    item = QTableWidgetItem(it.location_str())
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                elif key == "qty":
                    item = QTableWidgetItem(str(it.qty))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    f = QFont(); f.setBold(True)
                    item.setFont(f)
                elif key == "price":
                    item = QTableWidgetItem(f"{it.price:.2f}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif key == "note":
                    item = QTableWidgetItem(it.note)
                else:
                    item = QTableWidgetItem(getattr(it, key) or "")
                # Mindestbestand: ganze Zeile gelb mit schwarzer Schrift
                if (it.minQty or 0) > 0 and (it.qty or 0) < it.minQty:
                    item.setBackground(Qt.GlobalColor.yellow)
                    item.setForeground(Qt.GlobalColor.black)
                self.table.setItem(r, c, item)
        self.table.resizeRowsToContents()

        # Spaltenbreiten wiederherstellen
        for i in range(len(cols)):
            w = self.settings.get("colWidths", {}).get(str(i))
            if w:
                self.table.setColumnWidth(i, int(w))

    def on_col_resized(self, logicalIndex, oldSize, newSize):
        self.settings.setdefault("colWidths", {})[str(logicalIndex)] = int(newSize)
        self.persist()

    def apply_search(self):
        self.render_table()

    def clear_search(self):
        self.edSearch.clear(); self.render_table()

    def load_selected_into_form(self):
        row = self.table.currentRow()
        if row < 0: return
        # Finde Item anhand sichtbarer Liste
        cols = self.current_columns()
        # Wir nehmen name-Spalte zum Lookup
        name_col = next((i for i,(k,_,_) in enumerate(cols) if k=="name"), None)
        if name_col is None: return
        name = self.table.item(row, name_col).text()
        it = next((x for x in self.items if x.name == name), None)
        if not it: return
        self.fill_form(it)

    # ==== Formular ====
    def fill_form(self, it: InventoryItem):
        self.current_edit_id = it.id
        self.edName.setText(it.name)
        self.edSKU.setText(it.sku)
        self.edMaker.setText(it.maker)
        self.cmbCat.setCurrentText(it.cat)
        self.cmbShelf.setCurrentText(it.shelf)
        self.spLevel.setValue(it.level)
        self.spCol.setValue(it.col)
        self.spBin.setValue(it.bin)
        self.spMin.setValue(it.minQty)
        self.spQty.setValue(it.qty)
        self.spPrice.setValue(it.price)
        self.edNote.setPlainText(it.note)
        self.current_image_temp = None
        self.current_attachments_temp = []
        # Vorschau
        self.lblPreview.clear()
        if it.image_path:
            p = QPixmap(os.path.join(self.data_folder or os.getcwd(), it.image_path))
            if not p.isNull():
                p = p.scaled(QSize(120, 90), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.lblPreview.setPixmap(p)

    def reset_form(self):
        self.current_edit_id = None
        for w in [self.edName, self.edSKU, self.edMaker]:
            w.clear()
        self.cmbCat.clear(); self.cmbCat.addItems(self.cats)
        self.cmbShelf.clear(); self.cmbShelf.addItems(list(self.shelves.keys()))
        self.spLevel.setValue(1); self.spCol.setValue(1); self.spBin.setValue(1)
        self.spMin.setValue(0); self.spQty.setValue(0); self.spPrice.setValue(0.0)
        self.edNote.clear()
        self.lblPreview.clear()
        self.current_image_temp = None
        self.current_attachments_temp = []

    def choose_image(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Bild auswählen", filter="Bilder (*.png *.jpg *.jpeg *.bmp *.gif)")
        if not fn: return
        self.current_image_temp = fn
        p = QPixmap(fn)
        if not p.isNull():
            p = p.scaled(QSize(120, 90), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lblPreview.setPixmap(p)

    def add_attachments(self):
        fns, _ = QFileDialog.getOpenFileNames(self, "Anhänge auswählen")
        if fns:
            self.current_attachments_temp.extend(fns)
            QMessageBox.information(self, "Anhänge", f"{len(fns)} Datei(en) vorgemerkt.")

    def validate_location(self, shelf: str, L: int, C: int, B: int) -> bool:
        s = self.shelves.get(shelf)
        if not s: return False
        return 1 <= L <= s['levels'] and 1 <= C <= s['cols'] and 1 <= B <= s['bins']

    def save_item_from_form(self):
        name = self.edName.text().strip()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bezeichnung ist Pflicht.")
            return
        shelf = self.cmbShelf.currentText()
        L, C, B = self.spLevel.value(), self.spCol.value(), self.spBin.value()
        if not self.validate_location(shelf, L, C, B):
            s = self.shelves.get(shelf)
            QMessageBox.warning(self, "Fehler", f"Lagerort ungültig – max B:{s['levels']} S:{s['cols']} F:{s['bins']}")
            return

        # Neues oder bestehendes Item
        if self.current_edit_id:
            it = next((x for x in self.items if x.id == self.current_edit_id), None)
            if not it:
                it = InventoryItem(); self.items.append(it)
        else:
            it = InventoryItem(); self.items.append(it)

        it.name = name
        it.sku = self.edSKU.text().strip()
        it.maker = self.edMaker.text().strip()
        it.cat = self.cmbCat.currentText() or "Allgemein"
        it.shelf = shelf
        it.level, it.col, it.bin = L, C, B
        it.minQty = int(self.spMin.value())
        it.qty = int(self.spQty.value())
        it.price = float(self.spPrice.value())
        it.note = self.edNote.toPlainText()

        # Bild kopieren
        if self.current_image_temp and self.data_folder:
            ext = os.path.splitext(self.current_image_temp)[1].lower() or ".jpg"
            dest_rel = os.path.join("images", f"{it.id}{ext}")
            dest_abs = os.path.join(self.data_folder, dest_rel)
            os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
            shutil.copy2(self.current_image_temp, dest_abs)
            it.image_path = dest_rel
            self.current_image_temp = None

        # Anhänge kopieren
        if self.current_attachments_temp and self.data_folder:
            att_dir = os.path.join(self.attachments_dir(), it.id)
            os.makedirs(att_dir, exist_ok=True)
            for src in self.current_attachments_temp:
                try:
                    shutil.copy2(src, os.path.join(att_dir, os.path.basename(src)))
                    rel = os.path.join("attachments", it.id, os.path.basename(src))
                    if rel not in it.attachments:
                        it.attachments.append(rel)
                except Exception as e:
                    QMessageBox.warning(self, "Anhang", f"Konnte {src} nicht kopieren: {e}")
            self.current_attachments_temp = []

        self.current_edit_id = it.id
        self.persist()
        if self.settings.get("autosave"):
            self.save_to_folder(with_backup=True)
        self.render_table()
        QMessageBox.information(self, "OK", "Artikel gespeichert.")

    def delete_current(self):
        if not self.current_edit_id:
            return
        reply = QMessageBox.question(self, "Löschen", "Artikel wirklich löschen?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.items = [x for x in self.items if x.id != self.current_edit_id]
        self.current_edit_id = None
        self.persist(); self.render_table(); self.reset_form()

    def delete_selected(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        if not rows:
            QMessageBox.information(self, "Hinweis", "Keine Auswahl.")
            return
        if QMessageBox.question(self, "Löschen", f"{len(rows)} Zeile(n) wirklich löschen?") != QMessageBox.StandardButton.Yes:
            return
        # Löschen anhand Namen (sichtbare Liste)
        cols = self.current_columns()
        name_col = next((i for i,(k,_,_) in enumerate(cols) if k=="name"), None)
        if name_col is None: return
        names = [self.table.item(r, name_col).text() for r in rows]
        self.items = [x for x in self.items if x.name not in names]
        self.persist(); self.render_table()

    # ==== Import/Export ====
    def export_json(self):
        fn, _ = QFileDialog.getSaveFileName(self, "JSON Export", "inventory_backup.json", filter="JSON (*.json)")
        if not fn: return
        data = {
            "items": [asdict(x) for x in self.items],
            "cats": self.cats,
            "shelves": self.shelves,
            "settings": self.settings,
        }
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Export", "JSON exportiert.")

    def import_json(self):
        fn, _ = QFileDialog.getOpenFileName(self, "JSON Import", filter="JSON (*.json)")
        if not fn: return
        with open(fn, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.items = [InventoryItem(**it) for it in data.get("items", [])]
        self.cats = data.get("cats", self.cats)
        self.shelves = data.get("shelves", self.shelves)
        self.settings.update(data.get("settings", {}))
        self.cmbCat.clear(); self.cmbCat.addItems(self.cats)
        self.cmbShelf.clear(); self.cmbShelf.addItems(list(self.shelves.keys()))
        self.persist(); self.render_table()
        QMessageBox.information(self, "Import", "JSON importiert.")

    def export_csv(self):
        fn, _ = QFileDialog.getSaveFileName(self, "CSV Export", "lager_export.csv", filter="CSV (*.csv)")
        if not fn: return
        header = ["Bezeichnung","Artikelnummer","Hersteller","Kategorie","Preis","Regal","Boden","Spalte","Fach","Bestand","Mindestbestand","Notiz"]
        with open(fn, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(header)
            for it in self.items:
                w.writerow([
                    it.name or "", it.sku or "", it.maker or "", it.cat or "",
                    f"{it.price:.2f}", it.shelf or "", it.level or 1, it.col or 1, it.bin or 1,
                    it.qty or 0, it.minQty or 0, it.note or ""
                ])
        QMessageBox.information(self, "Export", "CSV exportiert.")

    def import_csv(self):
        fn, _ = QFileDialog.getOpenFileName(self, "CSV Import", filter="CSV (*.csv);;Alle Dateien (*)")
        if not fn: return
        with open(fn, "r", encoding="utf-8-sig", newline="") as f:
            text = f.read()
        sep = ';' if text.splitlines()[0].count(';') >= text.splitlines()[0].count(',') else ','
        rows = list(csv.reader(text.splitlines(), delimiter=sep))
        if not rows: return
        header = [h.strip().lower() for h in rows[0]]
        def idx(names):
            for n in names:
                if n in header: return header.index(n)
            return -1
        idxs = {
            'name': idx(['bezeichnung','name']),
            'sku': idx(['artikelnummer','art.-nr.','sku','nummer']),
            'maker': idx(['hersteller','brand','maker']),
            'cat': idx(['kategorie','category','cat']),
            'price': idx(['preis','price','eur','€']),
            'shelf': idx(['regal','shelf']),
            'level': idx(['boden','level']),
            'col': idx(['spalte','column']),
            'bin': idx(['fach','bin']),
            'qty': idx(['bestand','qty','menge']),
            'minQty': idx(['mindestbestand','min','min qty']),
            'note': idx(['notiz','note','desc'])
        }
        imported=updated=skipped=0
        for r in rows[1:]:
            def get(k, default=""):
                i = idxs[k]
                return r[i].strip() if 0 <= i < len(r) else default
            name = get('name')
            if not name: continue
            cand = InventoryItem(
                name=name,
                sku=get('sku'), maker=get('maker'), cat=get('cat') or 'Allgemein',
                price=float((get('price') or '0').replace(',','.')),
                shelf=get('shelf') or 'R1', level=int(get('level') or '1'), col=int(get('col') or '1'), bin=int(get('bin') or '1'),
                qty=int(get('qty') or '0'), minQty=int(get('minQty') or '0'), note=get('note')
            )
            # Merge anhand Schlüssel (SKU oder Name+Maker)
            def key(o: InventoryItem):
                return (o.sku.strip().lower() if o.sku else f"NM:{o.name.strip().lower()}|MK:{o.maker.strip().lower()}")
            existing = next((x for x in self.items if key(x)==key(cand)), None)
            if existing:
                # Konfliktbehandlung Menge
                if (cand.qty or 0) != (existing.qty or 0):
                    choice, ok = QInputDialogWrapper.get_text(self, f"Konflikt bei '{existing.name}'", \
                        f"Alt {existing.qty}, neu {cand.qty}.\n1=behalten, 2=überschreiben, 3=addieren", "1")
                    if ok:
                        if choice == "2": existing.qty = cand.qty; updated+=1
                        elif choice == "3": existing.qty = (existing.qty or 0) + (cand.qty or 0); updated+=1
                existing.maker = existing.maker or cand.maker
                existing.cat = existing.cat or cand.cat
                existing.price = existing.price or cand.price
                existing.shelf = existing.shelf or cand.shelf
                existing.level = existing.level or cand.level
                existing.col = existing.col or cand.col
                existing.bin = existing.bin or cand.bin
                existing.minQty = existing.minQty or cand.minQty
                skipped+=1
            else:
                self.items.append(cand); imported+=1
        self.persist(); self.render_table()
        QMessageBox.information(self, "Import", f"{imported} neu, {updated} aktualisiert, {skipped} geprüft.")

    # ==== Autosave ====
    def maybe_autosave(self):
        if self.settings.get("autosave") and self.data_folder:
            self.save_to_folder(with_backup=True)


class QInputDialogWrapper:
    @staticmethod
    def get_text(parent, title, label, default=""):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
        d = QDialog(parent); d.setWindowTitle(title)
        v = QVBoxLayout(d)
        v.addWidget(QLabel(label))
        e = QLineEdit(); e.setText(default); v.addWidget(e)
        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        v.addWidget(bb)
        bb.accepted.connect(d.accept); bb.rejected.connect(d.reject)
        ok = d.exec() == QDialog.DialogCode.Accepted
        return e.text(), ok


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
