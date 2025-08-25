# accurate_app_final.py
"""
Versi final yang lebih stabil dan teruji secara statis.
Fitur utama:
- Urutan tab: 1) Faktur, 2) Transport, 3) HPP, 4) Harga Jual, 5) Export (Preview editable)
- Transport: Add / Replace, alokasi Proporsional NetLine / QtyBase
- HPP: validasi LineDiscRaw, perhitungan HPP termasuk TransportAlloc
- Harga Jual: rekomendasi berdasarkan MARGIN_RULES, kolom HargaJualLama (PriceOld)
- Export: preview, editable, metadata ID/TRANSACTIONID/STANDARDNO editable
- Dark Mode: stylesheet + per-cell foreground/background untuk keterbacaan

Catatan: file ini menggunakan PyQt6 dan pandas. Pastikan environment sudah terpasang:
    pip install PyQt6 pandas

Jalankan:
    python accurate_app_final.py

"""
import sys
import os
import traceback
import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import List, Dict, Any

import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QMessageBox, QHeaderView, QAbstractItemView, QMenu, QMenuBar, QComboBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

# --------------------------
# Configuration
# --------------------------
MARGIN_RULES = [
    (Decimal('20000'), [Decimal('0.50'), Decimal('0.65'), Decimal('0.80')]),
    (Decimal('100000'), [Decimal('0.40'), Decimal('0.50'), Decimal('0.60')]),
    (Decimal('500000'), [Decimal('0.25'), Decimal('0.35'), Decimal('0.45')]),
    (Decimal('9999999999'), [Decimal('0.15'), Decimal('0.20'), Decimal('0.30')])
]

# --------------------------
# Helpers
# --------------------------

def safe_decimal(x) -> Decimal:
    if x is None:
        return Decimal(0)
    s = str(x).strip()
    if s == "":
        return Decimal(0)
    s = s.replace('Rp', '').replace('rp', '')
    s = s.replace(' ', '')
    # Normalize number formats
    if s.count(',') and s.count('.'):
        s = s.replace('.', '')
        s = s.replace(',', '.')
    else:
        # If only commas (likely thousand sep in some locales) remove them
        if s.count(',') and not s.count('.'):
            # assume comma is thousand sep unless there's exactly one and it's decimal
            parts = s.split(',')
            if len(parts[-1]) in (1, 2):
                # treat last comma as decimal
                s = ''.join(parts[:-1]) + '.' + parts[-1]
            else:
                s = ''.join(parts)
    if s.startswith('#'):
        s = s[1:]
    # remove any non-digit except dot and minus
    cleaned = ''.join(ch for ch in s if ch.isdigit() or ch in '.-')
    try:
        return Decimal(cleaned) if cleaned not in ['', '.', '-'] else Decimal(0)
    except InvalidOperation:
        return Decimal(0)


def rupiah_str(v: Decimal | float | int) -> str:
    try:
        d = Decimal(str(v))
    except Exception:
        d = Decimal(0)
    q = d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    s = f"{q:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"Rp {s}"


def int_if_whole(v: Decimal) -> str:
    if isinstance(v, Decimal):
        if v == v.to_integral():
            return f"{int(v):,}".replace(',', '.')
        else:
            return f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return str(v)

# --------------------------
# XML parser (menghasilkan kolom internal bahasa Inggris)
# --------------------------

def parse_purchase_invoices(path: str) -> List[Dict[str, Any]]:
    rows = []
    tree = ET.parse(path)
    root = tree.getroot()

    for inv in root.findall('.//PURCHASEINVOICE'):
        invno = (inv.findtext('INVOICENO') or '').strip()
        invdate = (inv.findtext('INVOICEDATE') or '').strip()
        vendor = (inv.findtext('VENDORID') or '').strip()

        tax_total = Decimal(0)
        for ap in inv.findall('.//APINVDET'):
            gl = (ap.findtext('GLACCOUNT') or '').strip()
            amt = safe_decimal(ap.findtext('GLAMOUNT'))
            if gl.startswith('2100'):
                tax_total += amt

        cash_disc_amount = safe_decimal(inv.findtext('CASHDISCOUNT'))
        cash_disc_pc = safe_decimal(inv.findtext('CASHDISCPC'))

        temp = []
        gross_sum = Decimal(0)
        for line in inv.findall('ITEMLINE'):
            itemno = (line.findtext('ITEMNO') or '').strip()
            desc = (line.findtext('ITEMOVDESC') or '').strip()
            qty = safe_decimal(line.findtext('QUANTITY') or '0')
            unit = (line.findtext('ITEMUNIT') or '').strip()
            unitratio = safe_decimal(line.findtext('UNITRATIO') or '1')
            bruto = safe_decimal(line.findtext('BRUTOUNITPRICE') or line.findtext('UNITPRICE') or '0')
            gross_line = qty * bruto
            gross_sum += gross_line

            disc_raw = (line.findtext('ITEMDISCPC') or '') or ''
            disc_raw = disc_raw.strip()
            disc_type = None
            line_disc_amt = Decimal(0)
            if disc_raw != '':
                if disc_raw.startswith('#'):
                    disc_type = 'nominal'
                    val = safe_decimal(disc_raw)
                    line_disc_amt = val * qty
                else:
                    val = safe_decimal(disc_raw)
                    if val > 0 and val <= 1:
                        disc_type = 'fraction'
                        line_disc_amt = gross_line * val
                    elif val > 1 and val <= 100:
                        disc_type = 'percent'
                        line_disc_amt = gross_line * (val / Decimal(100))
                    else:
                        disc_type = 'nominal'
                        line_disc_amt = val

            temp.append({
                'SourceFile': os.path.basename(path),
                'InvoiceNo': invno,
                'InvoiceDate': invdate,
                'VendorID': vendor,
                'ItemNo': itemno,
                'Description': desc,
                'Qty': qty,
                'ItemUnit': unit,
                'UnitRatio': unitratio,
                'QtyBase': qty * (unitratio if unitratio > 0 else Decimal(1)),
                'BrutoUnit': bruto,
                'GrossLine': gross_line,
                'LineDiscRaw': disc_raw,
                'LineDiscAmount': line_disc_amt,
                'LineDiscType': disc_type
            })

        if cash_disc_amount == 0 and cash_disc_pc > 0 and gross_sum > 0:
            if cash_disc_pc <= 1:
                cash_disc_amount = gross_sum * cash_disc_pc
            else:
                cash_disc_amount = gross_sum * (cash_disc_pc / Decimal(100))

        net_sum = Decimal(0)
        for r in temp:
            share = (r['GrossLine'] / gross_sum) if gross_sum > 0 else Decimal(0)
            r['CashDiscAlloc'] = (cash_disc_amount * share).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            r['NetLineBeforeTax'] = (r['GrossLine'] - r['LineDiscAmount'] - r['CashDiscAlloc'])
            if r['NetLineBeforeTax'] < 0:
                r['NetLineBeforeTax'] = Decimal(0)
            net_sum += r['NetLineBeforeTax']

        for r in temp:
            share = (r['NetLineBeforeTax'] / net_sum) if net_sum > 0 else Decimal(0)
            r['PPNAlloc'] = (tax_total * share).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            r['Taxable'] = True
            qtybase = r['QtyBase'] if r['QtyBase'] > 0 else Decimal(1)
            r['HPPperUnit'] = ((r['NetLineBeforeTax'] + r['PPNAlloc']) / qtybase).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            r['LineDisc%OfGross'] = (((r['LineDiscAmount'] / r['GrossLine'] * 100) if r['GrossLine'] else Decimal(0))).quantize(Decimal('0.01'))
            r['CashDisc%OfGross'] = (((r['CashDiscAlloc'] / r['GrossLine'] * 100) if r['GrossLine'] else Decimal(0))).quantize(Decimal('0.01'))
            r['PPN%OfNet'] = (((r['PPNAlloc'] / r['NetLineBeforeTax'] * 100) if r['NetLineBeforeTax'] else Decimal(0))).quantize(Decimal('0.01'))

            r['TransportAlloc'] = Decimal(0)
            r['TransportPerUnit'] = Decimal(0)

            rows.append(r)

    return rows

# --------------------------
# Main app
# --------------------------
class AccurateApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Accurate HPP & Harga Jual — (1) Faktur → (2) Transport → (3) HPP → (4) Harga Jual → (5) Export')
        self.resize(1400, 820)

        self.font_size = 10
        self.dark_mode = False

        # dataframes
        self.df_raw = pd.DataFrame()
        self.df_hpp = pd.DataFrame()
        self.df_jual = pd.DataFrame()

        # transport maps
        self.transport_map: Dict[str, Decimal] = {}
        self.transport_carrier_map: Dict[str, str] = {}

        # column label map
        self.column_label_map: Dict[str, str] = {
            'SourceFile': 'FileSumber',
            'InvoiceNo': 'NoFaktur',
            'InvoiceDate': 'TglFaktur',
            'VendorID': 'VendorID',
            'ItemNo': 'KodeBarang',
            'Description': 'Deskripsi',
            'Qty': 'Qty',
            'ItemUnit': 'Satuan',
            'UnitRatio': 'RasioUnit',
            'QtyBase': 'QtyDasar',
            'BrutoUnit': 'HargaBruto',
            'GrossLine': 'TotalBruto',
            'LineDiscRaw': 'DiskonBarisRaw',
            'LineDiscAmount': 'DiskonBaris',
            'LineDisc%OfGross': 'Diskon%DariBruto',
            'CashDiscAlloc': 'DiskonTunaiAlloc',
            'CashDisc%OfGross': 'DiskonTunai%DariBruto',
            'NetLineBeforeTax': 'NetSebelumPajak',
            'PPNAlloc': 'PPNAlloc',
            'PPN%OfNet': 'PPN%DariNet',
            'HPPperUnit': 'HPPPerUnit',
            'Taxable': 'DapatPajak',
            'TransportAlloc': 'TransportAlloc',
            'TransportPerUnit': 'TransportPerUnit',
            'LineDiscType': 'JenisDiskon',
            'InvoiceTransportTotal': 'InvoiceTransportTotal',
            'PriceOld': 'HargaJualLama'
        }

        # UI
        menubar = QMenuBar(self)
        view_menu = QMenu('Tampilan', self)
        menubar.addMenu(view_menu)
        zoom_in = view_menu.addAction('Zoom In (+)')
        zoom_out = view_menu.addAction('Zoom Out (-)')
        zoom_reset = view_menu.addAction('Reset Zoom')
        zoom_in.triggered.connect(lambda: self.change_font(1))
        zoom_out.triggered.connect(lambda: self.change_font(-1))
        zoom_reset.triggered.connect(lambda: self.set_font(10))
        self.act_dark = view_menu.addAction('Dark Mode')
        self.act_dark.setCheckable(True)
        self.act_dark.triggered.connect(lambda checked: self.apply_dark_mode(checked))
        self.setMenuBar(menubar)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Tab 1 Faktur
        self.tab_faktur = QWidget()
        tabs.addTab(self.tab_faktur, '1) Faktur (Load XML)')
        self._init_tab_faktur()

        # Tab 2 Transport
        self.tab_transport = QWidget()
        tabs.addTab(self.tab_transport, '2) Transport (Biaya Manual)')
        self._init_tab_transport()

        # Tab 3 HPP
        self.tab_hpp = QWidget()
        tabs.addTab(self.tab_hpp, '3) Hitung Harga Beli (HPP)')
        self._init_tab_hpp()

        # Tab 4 Harga Jual
        self.tab_jual = QWidget()
        tabs.addTab(self.tab_jual, '4) Tentukan Harga Jual')
        self._init_tab_jual()

        # Tab 5 Export
        self.tab_export = QWidget()
        tabs.addTab(self.tab_export, '5) Preview & Export')
        self._init_tab_export()

    # ---------- Tab initializers ----------
    def _init_tab_faktur(self):
        layout = QVBoxLayout()
        info = QLabel('<b>Langkah 1 — Load file XML faktur pembelian (boleh banyak).</b>')
        layout.addWidget(info)

        row = QHBoxLayout()
        self.btn_load = QPushButton('1. Load Banyak XML Faktur...')
        self.btn_load.clicked.connect(self.load_many_files)
        row.addWidget(self.btn_load)
        self.btn_refresh = QPushButton('Refresh HPP (pakai data saat ini)')
        self.btn_refresh.clicked.connect(self.refresh_hpp_from_raw)
        row.addWidget(self.btn_refresh)
        row.addStretch()
        layout.addLayout(row)

        self.tbl_faktur = QTableWidget()
        self.tbl_faktur.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        layout.addWidget(self.tbl_faktur)

        self.tab_faktur.setLayout(layout)

    def _init_tab_transport(self):
        layout = QVBoxLayout()
        info = QLabel('<b>Langkah 2 — Masukkan biaya transport manual</b>')
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel('<b>Daftar Faktur (centang yang ingin diberi biaya transport)</b>'))
        self.tbl_invoices_transport = QTableWidget()
        self.tbl_invoices_transport.setColumnCount(5)
        hdrs = ['Pilih', self.column_label_map.get('InvoiceNo', 'InvoiceNo'), self.column_label_map.get('VendorID','VendorID'), 'InvoiceNet', self.column_label_map.get('InvoiceTransportTotal','InvoiceTransportTotal')]
        self.tbl_invoices_transport.setHorizontalHeaderLabels(hdrs)
        left.addWidget(self.tbl_invoices_transport)

        btn_row_left = QHBoxLayout()
        self.btn_refresh_invoices = QPushButton('Refresh Daftar Faktur')
        self.btn_refresh_invoices.clicked.connect(self._load_invoice_list_for_transport)
        btn_row_left.addWidget(self.btn_refresh_invoices)
        btn_row_left.addStretch()
        left.addLayout(btn_row_left)

        row.addLayout(left, 2)

        right = QVBoxLayout()
        right.addWidget(QLabel('<b>Atur biaya transport untuk faktur terpilih</b>'))
        h1 = QHBoxLayout()
        h1.addWidget(QLabel('Carrier / Jasa Kirim:'))
        self.ed_carrier = QLineEdit()
        self.ed_carrier.setPlaceholderText('Nama pengirim / jasa kirim')
        h1.addWidget(self.ed_carrier)
        right.addLayout(h1)

        h2 = QHBoxLayout()
        h2.addWidget(QLabel('Jumlah Total Transport (Rp):'))
        self.ed_transport_amount = QLineEdit()
        self.ed_transport_amount.setPlaceholderText('mis. 150000')
        h2.addWidget(self.ed_transport_amount)
        right.addLayout(h2)

        h3 = QHBoxLayout()
        h3.addWidget(QLabel('Mode Alokasi:'))
        self.cbo_alloc_mode = QComboBox()
        self.cbo_alloc_mode.addItems(['Proporsional NetLine', 'Proporsional QtyBase'])
        h3.addWidget(self.cbo_alloc_mode)
        right.addLayout(h3)

        h4 = QHBoxLayout()
        h4.addWidget(QLabel('Operasi Transport:'))
        self.rb_add = QRadioButton('Add (tambah)')
        self.rb_replace = QRadioButton('Replace (ganti)')
        self.rb_replace.setChecked(True)
        self.op_group = QButtonGroup()
        self.op_group.addButton(self.rb_add)
        self.op_group.addButton(self.rb_replace)
        h4.addWidget(self.rb_add)
        h4.addWidget(self.rb_replace)
        right.addLayout(h4)

        btn_apply = QPushButton('Apply ke Faktur Terpilih')
        btn_apply.clicked.connect(self.apply_transport_to_selected)
        right.addWidget(btn_apply)

        btn_remove = QPushButton('Hapus Transport dari Faktur Terpilih')
        btn_remove.clicked.connect(self.remove_transport_from_selected)
        right.addWidget(btn_remove)

        right.addStretch()
        row.addLayout(right, 1)

        layout.addLayout(row)
        self.tab_transport.setLayout(layout)

    def _init_tab_hpp(self):
        layout = QVBoxLayout()
        info = QLabel('<b>Langkah 3 — Hitung Harga Beli (HPP)</b>')
        info.setWordWrap(True)
        layout.addWidget(info)

        ctrl = QHBoxLayout()
        self.btn_hitung_hpp = QPushButton('Hitung Ulang HPP')
        self.btn_hitung_hpp.clicked.connect(self.compute_hpp_from_raw)
        ctrl.addWidget(self.btn_hitung_hpp)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.tbl_hpp = QTableWidget()
        self.tbl_hpp.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        layout.addWidget(self.tbl_hpp)

        self.tab_hpp.setLayout(layout)

    def _init_tab_jual(self):
        layout = QVBoxLayout()
        info = QLabel('<b>Langkah 4 — Tentukan Harga Jual</b>')
        info.setWordWrap(True)
        layout.addWidget(info)

        ctrl = QHBoxLayout()
        self.btn_rekom = QPushButton('Buat Rekomendasi Harga Jual')
        self.btn_rekom.clicked.connect(self.build_price_recommendations)
        ctrl.addWidget(self.btn_rekom)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.tbl_jual = QTableWidget()
        self.tbl_jual.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        layout.addWidget(self.tbl_jual)

        self.lbl_status = QLabel('Ringkasan status: -')
        layout.addWidget(self.lbl_status)

        btn_apply = QPushButton('Simpan Final ke Set Harga (preview)')
        btn_apply.clicked.connect(self._apply_final_to_set)
        layout.addWidget(btn_apply)

        self.tab_jual.setLayout(layout)

    def _init_tab_export(self):
        layout = QVBoxLayout()
        info = QLabel('<b>Langkah 5 — Preview & Ekspor ke XML Accurate</b>')
        info.setWordWrap(True)
        layout.addWidget(info)

        meta_row = QHBoxLayout()
        meta_row.addWidget(QLabel('ID:'))
        self.ed_export_id = QLineEdit()
        self.ed_export_id.setPlaceholderText('Auto generated or editable')
        meta_row.addWidget(self.ed_export_id)
        meta_row.addWidget(QLabel('TRANSACTIONID:'))
        self.ed_export_txid = QLineEdit()
        self.ed_export_txid.setPlaceholderText('Auto generated or editable')
        meta_row.addWidget(self.ed_export_txid)
        meta_row.addWidget(QLabel('STANDARDNO:'))
        self.ed_standardno = QLineEdit()
        self.ed_standardno.setPlaceholderText('mis. SHP2025/00415 (boleh kosong untuk auto)')
        meta_row.addWidget(self.ed_standardno)
        meta_row.addStretch()
        layout.addLayout(meta_row)

        layout.addWidget(QLabel('<b>Preview Set Harga (editable)</b>'))
        self.tbl_export_preview = QTableWidget()
        self.tbl_export_preview.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        layout.addWidget(self.tbl_export_preview)

        btn_row = QHBoxLayout()
        self.btn_build_preview = QPushButton('Bangun Preview dari Harga Final')
        self.btn_build_preview.clicked.connect(self.build_export_preview)
        btn_row.addWidget(self.btn_build_preview)

        self.btn_validate_preview = QPushButton('Validasi Preview (cek Final > 0)')
        self.btn_validate_preview.clicked.connect(self.validate_export_preview)
        btn_row.addWidget(self.btn_validate_preview)

        btn_row.addStretch()
        self.btn_export_xml = QPushButton('Export XML Set Harga Jual (MATERIALSTANDARDCOST)')
        self.btn_export_xml.clicked.connect(self.export_setharga_xml)
        btn_row.addWidget(self.btn_export_xml)

        layout.addLayout(btn_row)
        self.tab_export.setLayout(layout)

    # ---------- Actions ----------
    def load_many_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Pilih file XML Accurate (multi)', '', 'XML Files (*.xml)')
        if not files:
            return
        rows = []
        for f in files:
            try:
                rows += parse_purchase_invoices(f)
            except Exception as e:
                print(f'Error parse {f}: {e}')
        if not rows:
            QMessageBox.warning(self, 'Info', 'Tidak ada data terbaca dari file yang dipilih.')
            return
        df = pd.DataFrame(rows)
        cols = [
            'SourceFile','InvoiceNo','InvoiceDate','VendorID',
            'ItemNo','Description','Qty','ItemUnit','UnitRatio','QtyBase',
            'BrutoUnit','GrossLine','LineDiscRaw','LineDiscAmount','LineDisc%OfGross',
            'CashDiscAlloc','CashDisc%OfGross','NetLineBeforeTax','PPNAlloc','PPN%OfNet',
            'HPPperUnit','Taxable','TransportAlloc','TransportPerUnit'
        ]
        for c in cols:
            if c not in df.columns:
                df[c] = Decimal(0) if c in ['Qty','UnitRatio','QtyBase','BrutoUnit','GrossLine','LineDiscAmount','CashDiscAlloc','NetLineBeforeTax','PPNAlloc','HPPperUnit','TransportAlloc','TransportPerUnit'] else ''
        df = df[cols]
        for col in ['Qty','UnitRatio','QtyBase','BrutoUnit','GrossLine','LineDiscAmount','CashDiscAlloc','NetLineBeforeTax','PPNAlloc','HPPperUnit','TransportAlloc','TransportPerUnit']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: Decimal(str(x)) if x != '' else Decimal(0))

        self.df_raw = df
        self._show_table(self.tbl_faktur, df, editable=True)
        self.refresh_hpp_from_raw()
        self._load_invoice_list_for_transport()

    def _load_invoice_list_for_transport(self):
        df = self.df_hpp if (hasattr(self, 'df_hpp') and not self.df_hpp.empty) else self.df_raw
        if df is None or df.empty:
            self.tbl_invoices_transport.setRowCount(0)
            return
        invoices = []
        transport_totals: Dict[str, Decimal] = {}
        for inv, grp in df.groupby('InvoiceNo'):
            transport_totals[inv] = self.transport_map.get(inv, Decimal(0))
        for inv, grp in df.groupby('InvoiceNo'):
            vendor = grp['VendorID'].iloc[0] if 'VendorID' in grp.columns else ''
            inv_net = grp['NetLineBeforeTax'].sum()
            inv_trans = transport_totals.get(inv, Decimal(0))
            invoices.append((inv, vendor, inv_net, inv_trans))
        self.tbl_invoices_transport.setRowCount(len(invoices))
        for i, (inv, vendor, inv_net, inv_trans) in enumerate(invoices):
            it_chk = QTableWidgetItem('')
            it_chk.setFlags(it_chk.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            it_chk.setCheckState(Qt.CheckState.Unchecked)
            self.tbl_invoices_transport.setItem(i, 0, it_chk)
            self.tbl_invoices_transport.setItem(i, 1, QTableWidgetItem(str(inv)))
            self.tbl_invoices_transport.setItem(i, 2, QTableWidgetItem(str(vendor)))
            it_net = QTableWidgetItem(rupiah_str(inv_net if isinstance(inv_net, Decimal) else Decimal(str(inv_net))))
            it_net.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tbl_invoices_transport.setItem(i, 3, it_net)
            it_trans = QTableWidgetItem(rupiah_str(inv_trans if isinstance(inv_trans, Decimal) else Decimal(str(inv_trans))))
            it_trans.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tbl_invoices_transport.setItem(i, 4, it_trans)
        self.tbl_invoices_transport.resizeColumnsToContents()

    def apply_transport_to_selected(self):
        rows = self.tbl_invoices_transport.rowCount()
        selected = []
        for r in range(rows):
            chk = self.tbl_invoices_transport.item(r, 0)
            if chk and chk.checkState() == Qt.CheckState.Checked:
                invno = self.tbl_invoices_transport.item(r, 1).text()
                selected.append(invno)
        if not selected:
            QMessageBox.information(self, 'Info', 'Pilih minimal satu faktur dulu.')
            return
        amt_text = self.ed_transport_amount.text().strip()
        if amt_text == '':
            QMessageBox.information(self, 'Info', 'Masukkan jumlah transport dulu.')
            return
        try:
            amt = safe_decimal(amt_text)
        except Exception:
            QMessageBox.information(self, 'Info', 'Jumlah transport tidak valid.')
            return
        if amt <= 0:
            QMessageBox.information(self, 'Info', 'Jumlah harus lebih dari 0.')
            return
        carrier = self.ed_carrier.text().strip()
        mode = self.cbo_alloc_mode.currentText()
        op_add = self.rb_add.isChecked()

        df = self.df_hpp if (hasattr(self, 'df_hpp') and not self.df_hpp.empty) else self.df_raw
        inv_net_sums: Dict[str, Decimal] = {}
        inv_qty_sums: Dict[str, Decimal] = {}
        for inv, grp in df.groupby('InvoiceNo'):
            inv_net_sums[inv] = grp['NetLineBeforeTax'].sum()
            inv_qty_sums[inv] = grp['QtyBase'].sum()

        basis_total = Decimal(0)
        basis_map: Dict[str, Decimal] = {}
        for inv in selected:
            if mode == 'Proporsional NetLine':
                b = inv_net_sums.get(inv, Decimal(0))
            else:
                b = inv_qty_sums.get(inv, Decimal(0))
            basis_map[inv] = b
            basis_total += b

        alloc_map: Dict[str, Decimal] = {}
        if basis_total == 0:
            per = (amt / Decimal(len(selected))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            for inv in selected:
                alloc_map[inv] = per
        else:
            for inv in selected:
                share = (basis_map[inv] / basis_total) if basis_total > 0 else Decimal(0)
                alloc_map[inv] = (amt * share).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        for inv in alloc_map:
            if op_add and inv in self.transport_map:
                self.transport_map[inv] = (self.transport_map[inv] + alloc_map[inv]).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                self.transport_map[inv] = alloc_map[inv]
            if carrier:
                self.transport_carrier_map[inv] = carrier

        self._update_transport_allocations()
        self.compute_hpp_from_raw()
        QMessageBox.information(self, 'Sukses', f'Transport sebesar {rupiah_str(amt)} telah diapply ke {len(selected)} faktur.')

    def remove_transport_from_selected(self):
        rows = self.tbl_invoices_transport.rowCount()
        removed = 0
        for r in range(rows):
            chk = self.tbl_invoices_transport.item(r, 0)
            if chk and chk.checkState() == Qt.CheckState.Checked:
                invno = self.tbl_invoices_transport.item(r, 1).text()
                if invno in self.transport_map:
                    del self.transport_map[invno]
                    if invno in self.transport_carrier_map:
                        del self.transport_carrier_map[invno]
                    removed += 1
        if removed == 0:
            QMessageBox.information(self, 'Info', 'Tidak ada transport yang dihapus (pilih faktur yang ada transport).')
            return
        self._update_transport_allocations()
        self.compute_hpp_from_raw()
        QMessageBox.information(self, 'Sukses', f'Transport dihapus dari {removed} faktur.')

    def _update_transport_allocations(self):
        if self.df_hpp is None or self.df_hpp.empty:
            return
        df = self.df_hpp
        inv_net_sums: Dict[str, Decimal] = {}
        inv_qty_sums: Dict[str, Decimal] = {}
        for inv, grp in df.groupby('InvoiceNo'):
            inv_net_sums[inv] = grp['NetLineBeforeTax'].sum()
            inv_qty_sums[inv] = grp['QtyBase'].sum()

        df['TransportAlloc'] = Decimal(0)
        df['TransportPerUnit'] = Decimal(0)
        invoice_transport_total: Dict[str, Decimal] = {}

        for inv, tot in self.transport_map.items():
            if tot == 0:
                invoice_transport_total[inv] = Decimal(0)
                continue
            inv_net = inv_net_sums.get(inv, Decimal(0))
            inv_qty = inv_qty_sums.get(inv, Decimal(0))
            mask = df['InvoiceNo'] == inv
            if inv_net > 0:
                for idx in df[mask].index:
                    line_net = df.at[idx, 'NetLineBeforeTax']
                    share = (line_net / inv_net) if inv_net > 0 else Decimal(0)
                    line_alloc = (tot * share).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    df.at[idx, 'TransportAlloc'] = line_alloc
                    qtybase = df.at[idx, 'QtyBase'] if df.at[idx, 'QtyBase'] and df.at[idx, 'QtyBase'] > 0 else Decimal(1)
                    df.at[idx, 'TransportPerUnit'] = (line_alloc / qtybase).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            elif inv_qty > 0:
                for idx in df[mask].index:
                    line_qty = df.at[idx, 'QtyBase']
                    share = (line_qty / inv_qty) if inv_qty > 0 else Decimal(0)
                    line_alloc = (tot * share).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    df.at[idx, 'TransportAlloc'] = line_alloc
                    qtybase = df.at[idx, 'QtyBase'] if df.at[idx, 'QtyBase'] and df.at[idx, 'QtyBase'] > 0 else Decimal(1)
                    df.at[idx, 'TransportPerUnit'] = (line_alloc / qtybase).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                lines_idx = df[mask].index.tolist()
                if not lines_idx:
                    invoice_transport_total[inv] = Decimal(0)
                    continue
                per_line = (tot / Decimal(len(lines_idx))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                for idx in lines_idx:
                    df.at[idx, 'TransportAlloc'] = per_line
                    qtybase = df.at[idx, 'QtyBase'] if df.at[idx, 'QtyBase'] and df.at[idx, 'QtyBase'] > 0 else Decimal(1)
                    df.at[idx, 'TransportPerUnit'] = (per_line / qtybase).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            invoice_transport_total[inv] = tot

        df['InvoiceTransportTotal'] = df['InvoiceNo'].map(lambda x: invoice_transport_total.get(x, self.transport_map.get(x, Decimal(0))))
        self.df_hpp = df
        try:
            self._show_table(self.tbl_hpp, self.df_hpp, editable=True)
        except Exception:
            pass

    def refresh_hpp_from_raw(self):
        if self.df_raw is None or self.df_raw.empty:
            self._show_table(self.tbl_hpp, pd.DataFrame(), editable=False)
            return
        self.df_hpp = self.df_raw.copy()
        if 'TransportAlloc' not in self.df_hpp.columns:
            self.df_hpp['TransportAlloc'] = Decimal(0)
        if 'TransportPerUnit' not in self.df_hpp.columns:
            self.df_hpp['TransportPerUnit'] = Decimal(0)
        self._update_transport_allocations()
        self._show_table(self.tbl_hpp, self.df_hpp, editable=True)

    def compute_hpp_from_raw(self):
        if self.df_raw is None or self.df_raw.empty:
            QMessageBox.information(self, 'Info', 'Belum ada data raw. Load file di tab Faktur dulu.')
            return
        self._sync_table_to_df(self.tbl_faktur, self.df_raw)
        df = self.df_raw.copy()

        if 'TransportAlloc' not in df.columns:
            df['TransportAlloc'] = Decimal(0)
        if 'TransportPerUnit' not in df.columns:
            df['TransportPerUnit'] = Decimal(0)

        invalid_lines = []
        for idx in df.index:
            raw = df.at[idx, 'LineDiscRaw']
            bruto = df.at[idx, 'BrutoUnit']
            qty = df.at[idx, 'Qty']
            gross = df.at[idx, 'GrossLine']
            disc_amt = Decimal(0)
            if isinstance(raw, str) and raw.strip() != '':
                s = raw.strip()
                try:
                    if s.startswith('#'):
                        val = safe_decimal(s)
                        disc_amt = val * qty
                    else:
                        val = safe_decimal(s)
                        if val <= 1:
                            disc_amt = gross * val
                        elif val <= 100:
                            disc_amt = gross * (val / Decimal(100))
                        else:
                            disc_amt = safe_decimal(s)
                except Exception:
                    invalid_lines.append((idx, raw))
            else:
                try:
                    if df.at[idx, 'LineDiscAmount'] != '':
                        disc_amt = df.at[idx, 'LineDiscAmount']
                except Exception:
                    disc_amt = Decimal(0)

            df.at[idx, 'LineDiscAmount'] = (disc_amt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if isinstance(disc_amt, Decimal) else Decimal(0))

        if invalid_lines:
            msg = '
'.join(f'Baris {i}: "{r}"' for i, r in invalid_lines[:10])
            QMessageBox.warning(self, 'Validasi Diskon', f'Terdapat baris dengan format Diskon tidak valid (contoh):
{msg}
Nilai diskon akan diperlakukan sebagai 0 untuk baris bermasalah.')

        for idx in df.index:
            gross = df.at[idx, 'GrossLine']
            line_disc = df.at[idx, 'LineDiscAmount']
            cash_alloc = df.at[idx, 'CashDiscAlloc']
            net = gross - line_disc - cash_alloc
            if net < 0:
                net = Decimal(0)
            df.at[idx, 'NetLineBeforeTax'] = net.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        invoices = df['InvoiceNo'].unique()
        for inv in invoices:
            mask = df['InvoiceNo'] == inv
            df_inv = df[mask]
            tax_total = df_inv['PPNAlloc'].sum()
            df_taxable = df_inv[df_inv['Taxable'] == True]
            sum_net_taxable = df_taxable['NetLineBeforeTax'].sum()
            for idx in df_inv.index:
                if df.at[idx, 'Taxable']:
                    share = (df.at[idx, 'NetLineBeforeTax'] / sum_net_taxable) if sum_net_taxable > 0 else Decimal(0)
                    df.at[idx, 'PPNAlloc'] = (tax_total * share).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                else:
                    df.at[idx, 'PPNAlloc'] = Decimal(0)

        self.df_hpp = df.copy()
        self._update_transport_allocations()
        df = self.df_hpp

        for idx in df.index:
            qtybase = df.at[idx, 'QtyBase'] if df.at[idx, 'QtyBase'] and df.at[idx, 'QtyBase'] > 0 else Decimal(1)
            hpp = (df.at[idx, 'NetLineBeforeTax'] + df.at[idx, 'PPNAlloc'] + df.at[idx, 'TransportAlloc']) / qtybase
            df.at[idx, 'HPPperUnit'] = hpp.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            gross = df.at[idx, 'GrossLine']
            df.at[idx, 'LineDisc%OfGross'] = (((df.at[idx, 'LineDiscAmount'] / gross * 100) if gross else Decimal(0))).quantize(Decimal('0.01'))
            df.at[idx, 'CashDisc%OfGross'] = (((df.at[idx, 'CashDiscAlloc'] / gross * 100) if gross else Decimal(0))).quantize(Decimal('0.01'))
            df.at[idx, 'PPN%OfNet'] = (((df.at[idx, 'PPNAlloc'] / df.at[idx, 'NetLineBeforeTax'] * 100) if df.at[idx, 'NetLineBeforeTax'] else Decimal(0))).quantize(Decimal('0.01'))

        self.df_hpp = df
        self._show_table(self.tbl_hpp, df, editable=True)
        self._load_invoice_list_for_transport()

    def build_price_recommendations(self):
        if self.df_hpp is None or self.df_hpp.empty:
            QMessageBox.information(self, 'Info', 'Hitung HPP dulu (Tab 3).')
            return
        self._sync_table_to_df(self.tbl_hpp, self.df_hpp)
        recs = []
        for _, r in self.df_hpp.iterrows():
            cost = r['HPPperUnit'] if r['HPPperUnit'] else Decimal(0)
            margins = None
            for max_cost, ms in MARGIN_RULES:
                if cost <= max_cost:
                    margins = ms
                    break
            if margins is None:
                margins = MARGIN_RULES[-1][1]

            prices = []
            for m in margins:
                denom = (Decimal(1) - m)
                if denom == 0:
                    p = cost
                else:
                    p = (cost / denom).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
                prices.append(int(p))

            final = prices[1] if len(prices) > 1 else prices[0]
            margin_final_pct = (((Decimal(final) - cost) / Decimal(final) * 100) if final and cost else Decimal(0))
            status = 'Baik' if margin_final_pct >= Decimal(20) else ('Cukup' if margin_final_pct >= Decimal(10) else 'Perlu Naik')
            recs.append({
                'InvoiceNo': r['InvoiceNo'],
                'ItemNo': r['ItemNo'],
                'Description': r['Description'],
                'HPPperUnit': r['HPPperUnit'],
                'RecLow': prices[0],
                'RecMid': prices[1] if len(prices) > 1 else prices[0],
                'RecHigh': prices[2] if len(prices) > 2 else prices[-1],
                'Final': final,
                'PriceOld': 0,
                'Margin%': round(float(margin_final_pct), 2),
                'Status': status
            })

        dfj = pd.DataFrame(recs)
        self.df_jual = dfj
        self._show_table(self.tbl_jual, dfj, editable=True)
        self._refresh_status_summary()

    def _refresh_status_summary(self):
        if self.df_jual is None or self.df_jual.empty:
            self.lbl_status.setText('Ringkasan status: -')
            return
        counts = self.df_jual['Status'].value_counts().to_dict()
        s = ' | '.join(f'{k}: {v}' for k, v in counts.items())
        self.lbl_status.setText(f'Ringkasan status: {s}')

    def _apply_final_to_set(self):
        self._sync_table_to_df(self.tbl_jual, self.df_jual)
        QMessageBox.information(self, 'Info', 'Harga Final disiapkan untuk preview & export (cek tab Export).')

    def build_export_preview(self):
        if self.df_jual is None or self.df_jual.empty:
            QMessageBox.information(self, 'Info', 'Belum ada data harga jual (buat rekomendasi & atur Final di Tab 4).')
            return
        self._sync_table_to_df(self.tbl_jual, self.df_jual)
        df = self.df_jual.copy()
        for c in ['ItemNo', 'Final', 'PriceOld']:
            if c not in df.columns:
                df[c] = ''
        preview = df[['ItemNo', 'Final', 'PriceOld']].copy()
        preview = preview.rename(columns={'ItemNo': 'ITEMNO', 'Final': 'PRICE1', 'PriceOld': 'PRICE2'})
        self._show_table(self.tbl_export_preview, preview, editable=True)

    def validate_export_preview(self):
        if not hasattr(self, 'tbl_export_preview') or self.tbl_export_preview is None:
            QMessageBox.information(self, 'Info', 'Bangun preview dulu.')
            return
        rows = self.tbl_export_preview.rowCount()
        bad = []
        for r in range(rows):
            itemno = self.tbl_export_preview.item(r, 0).text() if self.tbl_export_preview.item(r, 0) else ''
            price1_txt = self.tbl_export_preview.item(r, 1).text() if self.tbl_export_preview.item(r, 1) else ''
            price1 = safe_decimal(price1_txt)
            if price1 <= 0:
                bad.append((r + 1, itemno, price1_txt))
        if bad:
            msg = '
'.join(f'Baris {row} Item {it}: Final="{p}"' for row, it, p in bad[:20])
            QMessageBox.warning(self, 'Validasi Preview', f'Terdapat item dengan Final <= 0:
{msg}
Perbaiki sebelum export.')
        else:
            QMessageBox.information(self, 'Validasi Preview', 'Semua baris memiliki Final > 0.')

    def export_setharga_xml(self):
        # build preview if empty
        if not hasattr(self, 'tbl_export_preview') or self.tbl_export_preview.rowCount() == 0:
            self.build_export_preview()
            if self.tbl_export_preview.rowCount() == 0:
                QMessageBox.warning(self, 'Export', 'Belum ada data untuk diexport.')
                return

        self.validate_export_preview()
        id_val = self.ed_export_id.text().strip() or None
        txid_val = self.ed_export_txid.text().strip() or None
        stdno = self.ed_standardno.text().strip() or f"SHP{date.today().strftime('%Y%m%d')}"
        today_str = date.today().isoformat()

        root = ET.Element('NMEXML', {'EximID': '249399', 'BranchCode': '1317163777', 'ACCOUNTANTCOPYID': ''})
        trans = ET.SubElement(root, 'TRANSACTIONS', {'OnError': 'CONTINUE'})
        msc = ET.SubElement(trans, 'MATERIALSTANDARDCOST', {'operation': 'Add', 'REQUESTID': '1'})
        ET.SubElement(msc, 'ID').text = id_val or '2613'
        ET.SubElement(msc, 'TRANSACTIONID').text = txid_val or '524666'

        rows = self.tbl_export_preview.rowCount()
        cols = self.tbl_export_preview.columnCount()
        for r in range(rows):
            itemno = self.tbl_export_preview.item(r, 0).text() if self.tbl_export_preview.item(r, 0) else ''
            price1_txt = self.tbl_export_preview.item(r, 1).text() if self.tbl_export_preview.item(r, 1) else '0'
            price2_txt = self.tbl_export_preview.item(r, 2).text() if cols > 2 and self.tbl_export_preview.item(r, 2) else '0'
            p1 = str(int(safe_decimal(price1_txt))) if safe_decimal(price1_txt) >= 0 else '0'
            p2 = str(int(safe_decimal(price2_txt))) if safe_decimal(price2_txt) >= 0 else '0'
            det = ET.SubElement(msc, 'MATERIALSTDCOSTDET', {'operation': 'Add'})
            ET.SubElement(det, 'ITEMNO').text = str(itemno)
            ET.SubElement(det, 'STANDARDCOST').text = '0'
            ET.SubElement(det, 'PRICE1').text = p1
            ET.SubElement(det, 'PRICE2').text = p2
            ET.SubElement(det, 'PRICE3').text = '0'
            ET.SubElement(det, 'PRICE4').text = '0'
            ET.SubElement(det, 'PRICE5').text = '0'

        ET.SubElement(msc, 'STANDARDNO').text = stdno
        ET.SubElement(msc, 'STANDARDDATE').text = today_str
        ET.SubElement(msc, 'EFFECTIVEDATE').text = today_str
        ET.SubElement(msc, 'DESCRIPTION').text = ''

        def indent(elem, level=0):
            i = '
' + level * '  '
            if len(elem):
                if not elem.text or not elem.text.strip():
                    elem.text = i + '  '
                for child in elem:
                    indent(child, level + 1)
                if not child.tail or not child.tail.strip():
                    child.tail = i
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        indent(root)

        out_path, _ = QFileDialog.getSaveFileName(self, 'Simpan XML Set Harga Jual', f'set_harga_{date.today().isoformat()}.xml', 'XML Files (*.xml)')
        if not out_path:
            return
        tree = ET.ElementTree(root)
        tree.write(out_path, encoding='utf-8', xml_declaration=True)
        QMessageBox.information(self, 'Sukses', f'XML berhasil disimpan:
{out_path}')

    # ---------- Table helpers ----------
    def _show_table(self, table: QTableWidget, df: pd.DataFrame, editable: bool = False):
        table.clear()
        if df is None or df.empty:
            table.setRowCount(0)
            table.setColumnCount(0)
            return
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        display_labels = [self.column_label_map.get(c, str(c)) for c in df.columns]
        table.setHorizontalHeaderLabels(display_labels)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.setAlternatingRowColors(True)
        if getattr(self, 'dark_mode', False):
            table.setStyleSheet('alternate-background-color: #181818; background: #1e1e1e; gridline-color: #2e2e2e;')
        else:
            table.setStyleSheet('alternate-background-color: #f6f7fb; background: white; gridline-color: #e6e6e6;')
        font = QFont()
        font.setPointSize(self.font_size)
        table.setFont(font)

        dark = getattr(self, 'dark_mode', False)
        for i, row in df.iterrows():
            for j, col in enumerate(df.columns):
                val = row[col]
                if isinstance(val, Decimal):
                    if any(k in col.lower() for k in ['bruto','gross','line','net','ppn','hpp','alloc','price','transport']):
                        text = rupiah_str(val)
                    else:
                        text = int_if_whole(val)
                else:
                    text = str(val)
                item = QTableWidgetItem(text)
                if editable:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if isinstance(val, (Decimal, int, float)):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                lc = col.lower()
                if dark:
                    if 'disc' in lc:
                        bg = QColor(65, 20, 25)
                    elif 'net' in lc or 'hpp' in lc:
                        bg = QColor(15, 45, 15)
                    elif 'ppn' in lc or 'tax' in lc:
                        bg = QColor(15, 30, 45)
                    elif 'status' in lc:
                        sval = str(row[col]).lower()
                        if sval.startswith('baik'):
                            bg = QColor(30, 80, 30)
                        elif sval.startswith('cukup'):
                            bg = QColor(90, 80, 30)
                        else:
                            bg = QColor(80, 30, 40)
                    else:
                        bg = QColor(30, 30, 30)
                    fg = QColor(224, 224, 224)
                else:
                    if 'disc' in lc:
                        bg = QColor(255, 235, 238)
                    elif 'net' in lc or 'hpp' in lc:
                        bg = QColor(232, 245, 233)
                    elif 'ppn' in lc or 'tax' in lc:
                        bg = QColor(232, 244, 255)
                    elif 'status' in lc:
                        sval = str(row[col]).lower()
                        if sval.startswith('baik'):
                            bg = QColor(197, 238, 197)
                        elif sval.startswith('cukup'):
                            bg = QColor(255, 249, 196)
                        else:
                            bg = QColor(255, 205, 210)
                    else:
                        bg = QColor(255, 255, 255)
                    fg = QColor(0, 0, 0)
                try:
                    item.setBackground(bg)
                    item.setForeground(fg)
                except Exception:
                    pass
                table.setItem(i, j, item)
        table.horizontalHeader().setSectionsMovable(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)

    def _sync_table_to_df(self, table: QTableWidget, df: pd.DataFrame):
        if df is None or df.empty:
            return
        rows = table.rowCount()
        cols = table.columnCount()
        headers = [table.horizontalHeaderItem(c).text() for c in range(cols)]
        display_to_internal = {v: k for k, v in self.column_label_map.items()}
        for r in range(rows):
            for c, h in enumerate(headers):
                item = table.item(r, c)
                if item is None:
                    continue
                text = item.text().strip()
                internal_col = display_to_internal.get(h, h)
                if internal_col not in df.columns:
                    continue
                if any(k in internal_col.lower() for k in ['qty','ratio','bruto','gross','line','disc','alloc','ppn','hpp','price','transport']):
                    txt = text.replace('Rp', '').replace('.', '').replace(' ', '').replace(',', '.')
                    try:
                        df.at[df.index[r], internal_col] = Decimal(txt) if txt not in ['', None] else Decimal(0)
                    except Exception:
                        pass
                else:
                    df.at[df.index[r], internal_col] = text

    # ---------- Zoom / Dark ----------
    def change_font(self, delta: int):
        self.font_size = max(6, self.font_size + delta)
        self.set_font(self.font_size)

    def set_font(self, size: int):
        self.font_size = size
        f = QFont()
        f.setPointSize(size)
        self.setFont(f)
        try:
            self._show_table(self.tbl_faktur, self.df_raw, editable=True)
        except Exception:
            pass
        try:
            self._show_table(self.tbl_hpp, self.df_hpp, editable=True)
        except Exception:
            pass
        try:
            self._show_table(self.tbl_jual, self.df_jual, editable=True)
        except Exception:
            pass

    def apply_dark_mode(self, enable: bool):
        app = QApplication.instance()
        self.dark_mode = bool(enable)
        if enable:
            qss = """
            QMainWindow, QWidget { background-color: #121212; color: #e0e0e0; }
            QTableWidget { background-color: #1e1e1e; color: #e0e0e0; gridline-color: #2e2e2e; alternate-background-color: #181818; }
            QHeaderView::section { background-color: #2b2b2b; color: #e0e0e0; }
            QPushButton { background-color: #2a2a2a; color: #e0e0e0; border: 1px solid #3a3a3a; padding: 6px; border-radius: 6px; }
            QLineEdit, QComboBox, QSpinBox { background-color: #1e1e1e; color: #e0e0e0; border: 1px solid #3a3a3a; }
            QLabel { color: #e0e0e0; }
            QMessageBox { background-color: #1e1e1e; color: #e0e0e0; }
            QMenuBar { background-color: #121212; color: #e0e0e0; }
            QTabWidget::pane { background: #121212; }
            QTableWidget::item { background-color: transparent; }
            """
            app.setStyleSheet(qss)
        else:
            app.setStyleSheet("")
        # refresh tables
        try:
            self._show_table(self.tbl_faktur, self.df_raw, editable=True)
        except Exception:
            pass
        try:
            self._show_table(self.tbl_hpp, self.df_hpp, editable=True)
        except Exception:
            pass
        try:
            self._show_table(self.tbl_jual, self.df_jual, editable=True)
        except Exception:
            pass
        try:
            if not (self.df_jual is None or self.df_jual.empty):
                self.build_export_preview()
        except Exception:
            pass

# --------------------------
# Global exception handler
# --------------------------

def excepthook(exc_type, exc_value, exc_tb):
    tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(tb)
    try:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle('Error Aplikasi')
        msg.setText(str(exc_value))
        msg.setDetailedText(tb)
        msg.exec()
    except Exception:
        pass

# --------------------------
# Run
# --------------------------
if __name__ == '__main__':
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    win = AccurateApp()
    win.show()
    sys.exit(app.exec())
