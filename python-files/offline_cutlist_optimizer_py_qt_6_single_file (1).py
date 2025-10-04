"""
Offline Cutlist Optimizer - single-file PyQt6 application

Features:
- Parts table (name, length mm, qty)
- Stock table (name, length mm, qty)
- Kerf and min offcut settings
- First-Fit-Decreasing 1D optimizer (kerf-aware)
- Visual result per stock in a QGraphicsView (simple horizontal bars)
- Save / Load project (.json), Export CSV of cut patterns

Requirements:
- Python 3.9+
- PyQt6

Install:
    pip install PyQt6

Run:
    python cutlist_offline.py

To build a Windows single exe (optional):
    pip install pyinstaller
    pyinstaller --onefile --windowed cutlist_offline.py

"""

import sys
import json
import csv
from dataclasses import dataclass, asdict
from typing import List, Tuple
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QGraphicsScene, QGraphicsRectItem, QGraphicsSimpleTextItem
)

# ---------------------- Data classes & optimizer ----------------------
@dataclass
class Part:
    name: str
    length: float
    qty: int

@dataclass
class Stock:
    name: str
    length: float
    qty: int

@dataclass
class CutPattern:
    stock_name: str
    parts: List[Tuple[str, float]]  # (part name, length)
    waste: float


def first_fit_decreasing(parts: List[Part], stocks: List[Stock], kerf=0.0, min_offcut=0.0) -> List[CutPattern]:
    # expand parts into individual items
    items = []
    for p in parts:
        for i in range(p.qty):
            items.append((p.name, float(p.length)))
    # sort descending
    items.sort(key=lambda x: x[1], reverse=True)

    # expand stock pool into individual pieces
    stock_pool = []  # dict with id, name, length, available, parts
    for s in stocks:
        for i in range(s.qty):
            stock_pool.append({
                'name': s.name,
                'length': float(s.length),
                'available': float(s.length),
                'parts': [],
                'used_length': 0.0
            })

    # attempt to place each item
    for item_name, item_len in items:
        placed = False
        # try fit into existing partially used stock pieces: prefer smallest leftover that fits -> best-fit
        # compute candidate list
        candidates = []
        for idx, sp in enumerate(stock_pool):
            # required space: if not first part in piece, kerf applies
            required = item_len + (kerf if len(sp['parts']) > 0 else 0.0)
            if required <= sp['available']:
                candidates.append((idx, sp['available'] - required))
        if candidates:
            # choose candidate with smallest leftover after placement (best fit)
            candidates.sort(key=lambda x: x[1])
            chosen_idx = candidates[0][0]
            sp = stock_pool[chosen_idx]
            sp['parts'].append((item_name, item_len))
            sp['used_length'] += item_len + (kerf if len(sp['parts']) > 1 else 0.0)
            sp['available'] -= item_len + (kerf if len(sp['parts']) > 1 else 0.0)
            placed = True
        else:
            # try to open a fresh stock piece that hasn't been used yet
            opened = False
            for sp in stock_pool:
                if len(sp['parts']) == 0 and item_len <= sp['available']:
                    sp['parts'].append((item_name, item_len))
                    sp['used_length'] += item_len
                    sp['available'] -= item_len
                    opened = True
                    placed = True
                    break
            if not opened:
                # no space found - cannot place
                raise RuntimeError(f"Cannot place item {item_name} length {item_len} — not enough stock.")

    # build CutPattern results and filter only used pieces
    patterns = []
    for sp in stock_pool:
        if sp['parts']:
            waste = sp['available']
            # if leftover smaller than min_offcut, treat as waste (already waste)
            patterns.append(CutPattern(stock_name=sp['name'], parts=sp['parts'], waste=waste))
    return patterns

# ---------------------- GUI Application ----------------------
class CutlistApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Offline Cutlist Optimizer')
        self.setGeometry(200, 100, 1100, 700)
        self._create_ui()
        self.current_patterns: List[CutPattern] = []

    def _create_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # Top Buttons
        top_row = QtWidgets.QHBoxLayout()
        btn_new = QtWidgets.QPushButton('New Project')
        btn_open = QtWidgets.QPushButton('Open Project')
        btn_save = QtWidgets.QPushButton('Save Project')
        btn_export = QtWidgets.QPushButton('Export CSV')
        top_row.addWidget(btn_new); top_row.addWidget(btn_open); top_row.addWidget(btn_save); top_row.addWidget(btn_export)
        top_row.addStretch()
        layout.addLayout(top_row)

        btn_new.clicked.connect(self.new_project)
        btn_open.clicked.connect(self.open_project)
        btn_save.clicked.connect(self.save_project)
        btn_export.clicked.connect(self.export_csv)

        # Splitter for input tables and results
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        left_w = QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_w)

        # Parts table
        parts_label = QtWidgets.QLabel('Parts (length in mm)')
        left_layout.addWidget(parts_label)
        self.parts_table = QtWidgets.QTableWidget(0, 3)
        self.parts_table.setHorizontalHeaderLabels(['Name', 'Length (mm)', 'Qty'])
        self.parts_table.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.parts_table)
        parts_btn_row = QtWidgets.QHBoxLayout()
        btn_add_part = QtWidgets.QPushButton('Add Part')
        btn_remove_part = QtWidgets.QPushButton('Remove Selected')
        parts_btn_row.addWidget(btn_add_part); parts_btn_row.addWidget(btn_remove_part); parts_btn_row.addStretch()
        left_layout.addLayout(parts_btn_row)
        btn_add_part.clicked.connect(self.add_part_row)
        btn_remove_part.clicked.connect(self.remove_selected_part)

        # Stock table
        stock_label = QtWidgets.QLabel('Stock (length in mm)')
        left_layout.addWidget(stock_label)
        self.stock_table = QtWidgets.QTableWidget(0, 3)
        self.stock_table.setHorizontalHeaderLabels(['Name', 'Length (mm)', 'Qty'])
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        left_layout.addWidget(self.stock_table)
        stock_btn_row = QtWidgets.QHBoxLayout()
        btn_add_stock = QtWidgets.QPushButton('Add Stock')
        btn_remove_stock = QtWidgets.QPushButton('Remove Selected')
        stock_btn_row.addWidget(btn_add_stock); stock_btn_row.addWidget(btn_remove_stock); stock_btn_row.addStretch()
        left_layout.addLayout(stock_btn_row)
        btn_add_stock.clicked.connect(self.add_stock_row)
        btn_remove_stock.clicked.connect(self.remove_selected_stock)

        # Parameters
        param_box = QtWidgets.QGroupBox('Parameters')
        pb_layout = QtWidgets.QFormLayout(param_box)
        self.kerf_input = QtWidgets.QDoubleSpinBox(); self.kerf_input.setSuffix(' mm'); self.kerf_input.setDecimals(2); self.kerf_input.setRange(0, 100)
        self.min_offcut_input = QtWidgets.QDoubleSpinBox(); self.min_offcut_input.setSuffix(' mm'); self.min_offcut_input.setDecimals(2); self.min_offcut_input.setRange(0, 1000)
        pb_layout.addRow('Kerf (mm):', self.kerf_input)
        pb_layout.addRow('Min offcut size (mm):', self.min_offcut_input)
        left_layout.addWidget(param_box)

        # Optimize button
        self.optimize_btn = QtWidgets.QPushButton('Run Optimization')
        left_layout.addWidget(self.optimize_btn)
        self.optimize_btn.clicked.connect(self.run_optimization)
        left_layout.addStretch()

        splitter.addWidget(left_w)

        # Right pane: results + visualization
        right_w = QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_w)
        summary_label = QtWidgets.QLabel('Results')
        right_layout.addWidget(summary_label)

        # Results list
        self.result_list = QtWidgets.QListWidget()
        right_layout.addWidget(self.result_list)
        self.result_list.currentRowChanged.connect(self.show_pattern_visual)

        # Graphics view
        self.scene = QGraphicsScene()
        self.graphics = QtWidgets.QGraphicsView(self.scene)
        self.graphics.setMinimumHeight(300)
        right_layout.addWidget(self.graphics)

        # Export buttons
        export_row = QtWidgets.QHBoxLayout()
        btn_export_pdf = QtWidgets.QPushButton('Export Project JSON')
        btn_clear = QtWidgets.QPushButton('Clear Results')
        export_row.addWidget(btn_export_pdf); export_row.addWidget(btn_clear); export_row.addStretch()
        right_layout.addLayout(export_row)
        btn_export_pdf.clicked.connect(self.save_project)
        btn_clear.clicked.connect(self.clear_results)

        splitter.addWidget(right_w)
        splitter.setSizes([500, 600])

        # initialize with one row each
        self.add_part_row()
        self.add_stock_row()

    # ---------------------- Table helpers ----------------------
    def add_part_row(self):
        r = self.parts_table.rowCount()
        self.parts_table.insertRow(r)
        self.parts_table.setItem(r, 0, QTableWidgetItem(f'Part{r+1}'))
        self.parts_table.setItem(r, 1, QTableWidgetItem('1000'))
        self.parts_table.setItem(r, 2, QTableWidgetItem('1'))

    def remove_selected_part(self):
        rows = sorted({i.row() for i in self.parts_table.selectedItems()}, reverse=True)
        for r in rows:
            self.parts_table.removeRow(r)

    def add_stock_row(self):
        r = self.stock_table.rowCount()
        self.stock_table.insertRow(r)
        self.stock_table.setItem(r, 0, QTableWidgetItem(f'Stock{r+1}'))
        self.stock_table.setItem(r, 1, QTableWidgetItem('3000'))
        self.stock_table.setItem(r, 2, QTableWidgetItem('1'))

    def remove_selected_stock(self):
        rows = sorted({i.row() for i in self.stock_table.selectedItems()}, reverse=True)
        for r in rows:
            self.stock_table.removeRow(r)

    # ---------------------- Project Save / Load / Export ----------------------
    def new_project(self):
        self.parts_table.setRowCount(0)
        self.stock_table.setRowCount(0)
        self.add_part_row(); self.add_stock_row()
        self.clear_results()

    def open_project(self):
        fn, _ = QFileDialog.getOpenFileName(self, 'Open Project', '', 'Cutlist JSON (*.json);;All Files (*)')
        if not fn:
            return
        try:
            with open(fn, 'r') as f:
                data = json.load(f)
            self._load_from_data(data)
            QMessageBox.information(self, 'Open', 'Project loaded successfully')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to open project: {e}')

    def save_project(self):
        fn, _ = QFileDialog.getSaveFileName(self, 'Save Project', '', 'Cutlist JSON (*.json)')
        if not fn:
            return
        data = self._gather_project_data()
        try:
            with open(fn, 'w') as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, 'Save', 'Project saved successfully')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save project: {e}')

    def export_csv(self):
        if not self.current_patterns:
            QMessageBox.warning(self, 'Export', 'No results to export. Run optimization first.')
            return
        fn, _ = QFileDialog.getSaveFileName(self, 'Export CSV', '', 'CSV File (*.csv)')
        if not fn:
            return
        try:
            with open(fn, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Stock Name', 'Part Name', 'Part Length', 'Waste (mm)'])
                for pat in self.current_patterns:
                    for pn, pl in pat.parts:
                        writer.writerow([pat.stock_name, pn, pl, pat.waste])
            QMessageBox.information(self, 'Export', 'CSV exported successfully')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to export CSV: {e}')

    def _gather_project_data(self):
        parts = []
        for r in range(self.parts_table.rowCount()):
            try:
                name = self.parts_table.item(r, 0).text()
                length = float(self.parts_table.item(r, 1).text())
                qty = int(float(self.parts_table.item(r, 2).text()))
                parts.append({'name': name, 'length': length, 'qty': qty})
            except Exception:
                continue
        stocks = []
        for r in range(self.stock_table.rowCount()):
            try:
                name = self.stock_table.item(r, 0).text()
                length = float(self.stock_table.item(r, 1).text())
                qty = int(float(self.stock_table.item(r, 2).text()))
                stocks.append({'name': name, 'length': length, 'qty': qty})
            except Exception:
                continue
        data = {
            'parts': parts,
            'stocks': stocks,
            'kerf': float(self.kerf_input.value()),
            'min_offcut': float(self.min_offcut_input.value())
        }
        return data

    def _load_from_data(self, data):
        self.parts_table.setRowCount(0)
        for p in data.get('parts', []):
            r = self.parts_table.rowCount()
            self.parts_table.insertRow(r)
            self.parts_table.setItem(r, 0, QTableWidgetItem(str(p.get('name', ''))))
            self.parts_table.setItem(r, 1, QTableWidgetItem(str(p.get('length', ''))))
            self.parts_table.setItem(r, 2, QTableWidgetItem(str(p.get('qty', ''))))
        self.stock_table.setRowCount(0)
        for s in data.get('stocks', []):
            r = self.stock_table.rowCount()
            self.stock_table.insertRow(r)
            self.stock_table.setItem(r, 0, QTableWidgetItem(str(s.get('name', ''))))
            self.stock_table.setItem(r, 1, QTableWidgetItem(str(s.get('length', ''))))
            self.stock_table.setItem(r, 2, QTableWidgetItem(str(s.get('qty', ''))))
        self.kerf_input.setValue(float(data.get('kerf', 0.0)))
        self.min_offcut_input.setValue(float(data.get('min_offcut', 0.0)))
        self.clear_results()

    # ---------------------- Optimization & Visualization ----------------------
    def run_optimization(self):
        data = self._gather_project_data()
        parts = []
        stocks = []
        for p in data['parts']:
            parts.append(Part(name=p['name'], length=p['length'], qty=p['qty']))
        for s in data['stocks']:
            stocks.append(Stock(name=s['name'], length=s['length'], qty=s['qty']))
        kerf = data['kerf']
        min_offcut = data['min_offcut']
        try:
            patterns = first_fit_decreasing(parts, stocks, kerf=kerf, min_offcut=min_offcut)
        except RuntimeError as e:
            QMessageBox.critical(self, 'Optimization Error', str(e))
            return
        self.current_patterns = patterns
        self.populate_results_list()
        QMessageBox.information(self, 'Done', f'Optimization produced {len(patterns)} used stock pieces')

    def populate_results_list(self):
        self.result_list.clear()
        total_waste = 0.0
        total_parts = 0
        for i, pat in enumerate(self.current_patterns, 1):
            total_waste += pat.waste
            total_parts += len(pat.parts)
            self.result_list.addItem(f'#{i} - Stock: {pat.stock_name} | Parts: {len(pat.parts)} | Waste: {pat.waste:.1f} mm')
        # summary
        self.result_list.insertItem(0, f'SUMMARY: pieces used: {len(self.current_patterns)}, parts placed: {total_parts}, total waste: {total_waste:.1f} mm')
        self.result_list.setCurrentRow(1 if len(self.current_patterns) > 0 else 0)

    def show_pattern_visual(self, idx):
        # idx 0 is summary; result items start from 1
        if idx <= 0:
            self.scene.clear(); return
        pat = self.current_patterns[idx-1]
        self.scene.clear()
        view_w = max(600, int(self.graphics.width()))
        view_h = max(200, int(self.graphics.height()))
        margin = 20
        # determine scale: map stock length -> view_w - 2*margin
        stock_length = 0
        # find stock definition length from stock table
        for r in range(self.stock_table.rowCount()):
            if self.stock_table.item(r,0).text() == pat.stock_name:
                try:
                    stock_length = float(self.stock_table.item(r,1).text())
                except Exception:
                    stock_length = sum(pl for _,pl in pat.parts) + pat.waste
                break
        if stock_length <= 0:
            stock_length = sum(pl for _,pl in pat.parts) + pat.waste
        scale = (view_w - 2*margin) / stock_length if stock_length > 0 else 1.0

        x = margin
        y = margin
        h = 50
        # draw full stock background
        bg = QGraphicsRectItem(x, y, stock_length * scale, h)
        bg.setBrush(QtGui.QBrush(QtGui.QColor('#f0f0f0')))
        bg.setPen(QtGui.QPen(QtGui.QColor('#000000')))
        self.scene.addItem(bg)
        # draw parts
        colors = ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5']
        cx = 0
        for i, (pn, pl) in enumerate(pat.parts):
            w = pl * scale
            rect = QGraphicsRectItem(x + cx, y, w, h)
            rect.setBrush(QtGui.QBrush(QtGui.QColor(colors[i % len(colors)])))
            rect.setPen(QtGui.QPen(QtGui.QColor('#222222')))
            self.scene.addItem(rect)
            # label
            txt = QGraphicsSimpleTextItem(f'{pn} ({pl} mm)')
            txt.setPos(x + cx + 4, y + 4)
            self.scene.addItem(txt)
            cx += w
            # draw kerf indicator if not last
            # (kerf not visually subtracted here; simplified view)
        # leftover / waste
        if pat.waste > 0:
            w = pat.waste * scale
            rect = QGraphicsRectItem(x + cx, y, w, h)
            rect.setBrush(QtGui.QBrush(QtGui.QColor('#ffffff')))
            rect.setPen(QtGui.QPen(QtGui.QColor('#cc0000'), 1, QtCore.Qt.PenStyle.DashLine))
            self.scene.addItem(rect)
            txt = QGraphicsSimpleTextItem(f'WASTE {pat.waste:.1f} mm')
            txt.setPos(x + cx + 4, y + 4)
            self.scene.addItem(txt)
        # fit view
        self.graphics.fitInView(self.scene.sceneRect(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def clear_results(self):
        self.current_patterns = []
        self.result_list.clear()
        self.scene.clear()

# ---------------------- Main ----------------------

def main():
    app = QApplication(sys.argv)
    w = CutlistApp()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
