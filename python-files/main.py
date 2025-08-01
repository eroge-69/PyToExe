# main.py - Aplikasi Manajemen Kost (GUI) dalam Satu File
import sys
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QTabWidget, QComboBox, QDialog, QFormLayout, QLineEdit, QTextEdit,
    QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate

# ==================== MODEL ====================
@dataclass
class Kamar:
    nomor: str
    harga: float
    fasilitas: str
    status: str  # "tersedia" atau "terisi"
    penyewa: Optional[str] = None
    tanggal_masuk: Optional[str] = None
    tanggal_keluar: Optional[str] = None
    kontak: Optional[str] = None

# ==================== DATABASE ====================
class Database:
    def __init__(self, db_file: str = "kost_data.json"):
        self.db_file = db_file
        self.data: Dict[str, Kamar] = {}
        self._init_db()
    
    def _init_db(self):
        if not Path(self.db_file).exists():
            with open(self.db_file, 'w') as f:
                json.dump({}, f)
        self._load_data()
    
    def _load_data(self):
        with open(self.db_file, 'r') as f:
            data = json.load(f)
            for nomor, kamar_data in data.items():
                self.data[nomor] = Kamar(**kamar_data)
    
    def _save_data(self):
        with open(self.db_file, 'w') as f:
            data_to_save = {nomor: asdict(kamar) for nomor, kamar in self.data.items()}
            json.dump(data_to_save, f, indent=4)
    
    def tambah_kamar(self, kamar: Kamar):
        if kamar.nomor in self.data:
            raise ValueError(f"Kamar {kamar.nomor} sudah ada")
        self.data[kamar.nomor] = kamar
        self._save_data()
    
    def get_kamar(self, nomor: str) -> Optional[Kamar]:
        return self.data.get(nomor)
    
    def get_semua_kamar(self) -> List[Kamar]:
        return list(self.data.values())
    
    def update_kamar(self, nomor: str, **kwargs):
        if nomor not in self.data:
            raise ValueError(f"Kamar {nomor} tidak ditemukan")
        
        kamar = self.data[nomor]
        for key, value in kwargs.items():
            if hasattr(kamar, key):
                setattr(kamar, key, value)
        self._save_data()
    
    def hapus_kamar(self, nomor: str):
        if nomor not in self.data:
            raise ValueError(f"Kamar {nomor} tidak ditemukan")
        del self.data[nomor]
        self._save_data()
    
    def cari_kamar(self, status: str = None) -> List[Kamar]:
        if status:
            return [k for k in self.data.values() if k.status == status]
        return self.get_semua_kamar()

# ==================== DIALOGS ====================
class KamarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Form Kamar")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Form Input
        form = QFormLayout()
        
        self.input_nomor = QLineEdit()
        self.input_harga = QLineEdit()
        self.input_fasilitas = QTextEdit()
        self.input_status = QComboBox()
        self.input_status.addItems(["Tersedia", "Terisi"])
        
        form.addRow("Nomor Kamar:", self.input_nomor)
        form.addRow("Harga Sewa:", self.input_harga)
        form.addRow("Fasilitas:", self.input_fasilitas)
        form.addRow("Status:", self.input_status)
        
        # Penyewa Section
        self.penyewa_section = QWidget()
        penyewa_layout = QFormLayout()
        
        self.input_nama = QLineEdit()
        self.input_tgl_masuk = QDateEdit()
        self.input_tgl_masuk.setDate(QDate.currentDate())
        self.input_tgl_keluar = QDateEdit()
        self.input_tgl_keluar.setDate(QDate.currentDate().addMonths(1))
        self.input_kontak = QLineEdit()
        
        penyewa_layout.addRow("Nama Penyewa:", self.input_nama)
        penyewa_layout.addRow("Tanggal Masuk:", self.input_tgl_masuk)
        penyewa_layout.addRow("Tanggal Keluar:", self.input_tgl_keluar)
        penyewa_layout.addRow("Kontak:", self.input_kontak)
        
        self.penyewa_section.setLayout(penyewa_layout)
        self.penyewa_section.setVisible(False)
        
        # Buttons
        button_box = QHBoxLayout()
        self.btn_simpan = QPushButton("Simpan")
        self.btn_batal = QPushButton("Batal")
        
        button_box.addStretch()
        button_box.addWidget(self.btn_simpan)
        button_box.addWidget(self.btn_batal)
        
        layout.addLayout(form)
        layout.addWidget(QLabel("Data Penyewa:"))
        layout.addWidget(self.penyewa_section)
        layout.addLayout(button_box)
        
        self.setLayout(layout)
        
        # Connect signals
        self.input_status.currentTextChanged.connect(self.toggle_penyewa_section)
        self.btn_simpan.clicked.connect(self.validasi_input)
        self.btn_batal.clicked.connect(self.reject)
    
    def toggle_penyewa_section(self, status):
        self.penyewa_section.setVisible(status == "Terisi")
    
    def validasi_input(self):
        if not self.input_nomor.text():
            QMessageBox.warning(self, "Peringatan", "Nomor kamar harus diisi")
            return
        if not self.input_harga.text():
            QMessageBox.warning(self, "Peringatan", "Harga sewa harus diisi")
            return
        
        if self.input_status.currentText() == "Terisi":
            if not self.input_nama.text():
                QMessageBox.warning(self, "Peringatan", "Nama penyewa harus diisi")
                return
            if not self.input_kontak.text():
                QMessageBox.warning(self, "Peringatan", "Kontak penyewa harus diisi")
                return
        
        self.accept()

# ==================== MAIN WINDOW ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kost Management System")
        self.setMinimumSize(800, 600)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header = QLabel("Sistem Manajemen Kost")
        header.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(header)
        
        # Tab Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Setup Tabs
        self.setup_kamar_tab()
        self.setup_penyewa_tab()
        self.setup_laporan_tab()
    
    def setup_kamar_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_tambah = QPushButton("Tambah Kamar")
        self.btn_edit = QPushButton("Edit Kamar")
        self.btn_hapus = QPushButton("Hapus Kamar")
        self.btn_refresh = QPushButton("Refresh")
        
        toolbar.addWidget(self.btn_tambah)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_hapus)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_refresh)
        
        # Table
        self.table_kamar = QTableWidget()
        self.table_kamar.setColumnCount(5)
        self.table_kamar.setHorizontalHeaderLabels([
            "No. Kamar", "Harga", "Fasilitas", "Status", "Penyewa"
        ])
        self.table_kamar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(toolbar)
        layout.addWidget(self.table_kamar)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Manajemen Kamar")
    
    def setup_penyewa_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.btn_checkin = QPushButton("Check-in")
        self.btn_checkout = QPushButton("Check-out")
        self.btn_bayar = QPushButton("Pembayaran")
        
        toolbar.addWidget(self.btn_checkin)
        toolbar.addWidget(self.btn_checkout)
        toolbar.addWidget(self.btn_bayar)
        toolbar.addStretch()
        
        # Table
        self.table_penyewa = QTableWidget()
        self.table_penyewa.setColumnCount(6)
        self.table_penyewa.setHorizontalHeaderLabels([
            "Nama", "Kamar", "Tgl. Masuk", "Tgl. Keluar", "Kontak", "Status"
        ])
        self.table_penyewa.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addLayout(toolbar)
        layout.addWidget(self.table_penyewa)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Manajemen Penyewa")
    
    def setup_laporan_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Filter
        filter_layout = QHBoxLayout()
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["Semua", "Tersedia", "Terisi"])
        self.btn_filter = QPushButton("Filter")
        
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.combo_filter)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addStretch()
        
        # Table
        self.table_laporan = QTableWidget()
        self.table_laporan.setColumnCount(4)
        self.table_laporan.setHorizontalHeaderLabels([
            "Kamar", "Status", "Pendapatan", "Keterangan"
        ])
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.table_laporan)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Laporan")

# ==================== CONTROLLER ====================
class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.db = Database()
        self.connect_signals()
        self.load_data()
    
    def connect_signals(self):
        self.main_window.btn_tambah.clicked.connect(self.tambah_kamar)
        self.main_window.btn_edit.clicked.connect(self.edit_kamar)
        self.main_window.btn_hapus.clicked.connect(self.hapus_kamar)
        self.main_window.btn_refresh.clicked.connect(self.load_data)
        self.main_window.btn_checkin.clicked.connect(self.checkin_penyewa)
        self.main_window.btn_checkout.clicked.connect(self.checkout_penyewa)
        self.main_window.btn_bayar.clicked.connect(self.pembayaran)
        self.main_window.btn_filter.clicked.connect(self.filter_laporan)
    
    def load_data(self):
        try:
            kamar_list = self.db.get_semua_kamar()
            self.main_window.table_kamar.setRowCount(len(kamar_list))
            
            for row, kamar in enumerate(kamar_list):
                self.main_window.table_kamar.setItem(row, 0, QTableWidgetItem(kamar.nomor))
                self.main_window.table_kamar.setItem(row, 1, QTableWidgetItem(f"Rp {kamar.harga:,.2f}"))
                self.main_window.table_kamar.setItem(row, 2, QTableWidgetItem(kamar.fasilitas))
                status_item = QTableWidgetItem("Terisi" if kamar.status == "terisi" else "Tersedia")
                status_item.setData(Qt.UserRole, kamar.status)
                self.main_window.table_kamar.setItem(row, 3, status_item)
                self.main_window.table_kamar.setItem(row, 4, QTableWidgetItem(kamar.penyewa if kamar.penyewa else "-"))
            
            self.main_window.statusBar().showMessage("Data berhasil dimuat", 3000)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Gagal memuat data:\n{str(e)}")
    
    def tambah_kamar(self):
        try:
            dialog = KamarDialog(self.main_window)
            if dialog.exec_() == QDialog.Accepted:
                data = {
                    'nomor': dialog.input_nomor.text(),
                    'harga': float(dialog.input_harga.text()),
                    'fasilitas': dialog.input_fasilitas.toPlainText(),
                    'status': dialog.input_status.currentText().lower()
                }
                
                if data['status'] == 'terisi':
                    data.update({
                        'penyewa': dialog.input_nama.text(),
                        'tanggal_masuk': dialog.input_tgl_masuk.date().toString("dd-MM-yyyy"),
                        'tanggal_keluar': dialog.input_tgl_keluar.date().toString("dd-MM-yyyy"),
                        'kontak': dialog.input_kontak.text()
                    })
                
                kamar = Kamar(**data)
                self.db.tambah_kamar(kamar)
                self.load_data()
                QMessageBox.information(self.main_window, "Sukses", "Kamar berhasil ditambahkan")
        except ValueError as e:
            QMessageBox.warning(self.main_window, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Gagal menambah kamar:\n{str(e)}")
    
    def edit_kamar(self):
        try:
            selected = self.main_window.table_kamar.currentRow()
            if selected < 0:
                QMessageBox.warning(self.main_window, "Peringatan", "Pilih kamar yang akan diedit")
                return
            
            nomor = self.main_window.table_kamar.item(selected, 0).text()
            kamar = self.db.get_kamar(nomor)
            if not kamar:
                raise ValueError("Kamar tidak ditemukan")
            
            dialog = KamarDialog(self.main_window)
            dialog.input_nomor.setText(kamar.nomor)
            dialog.input_harga.setText(str(kamar.harga))
            dialog.input_fasilitas.setPlainText(kamar.fasilitas)
            dialog.input_status.setCurrentText("Terisi" if kamar.status == "terisi" else "Tersedia")
            
            if kamar.status == "terisi":
                dialog.input_nama.setText(kamar.penyewa)
                dialog.input_tgl_masuk.setDate(QDate.fromString(kamar.tanggal_masuk, "dd-MM-yyyy"))
                dialog.input_tgl_keluar.setDate(QDate.fromString(kamar.tanggal_keluar, "dd-MM-yyyy"))
                dialog.input_kontak.setText(kamar.kontak)
            
            if dialog.exec_() == QDialog.Accepted:
                # Implementasi update data
                pass
                
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Gagal mengedit kamar:\n{str(e)}")
    
    def hapus_kamar(self):
        try:
            selected = self.main_window.table_kamar.currentRow()
            if selected < 0:
                QMessageBox.warning(self.main_window, "Peringatan", "Pilih kamar yang akan dihapus")
                return
            
            nomor = self.main_window.table_kamar.item(selected, 0).text()
            confirm = QMessageBox.question(
                self.main_window,
                "Konfirmasi",
                f"Hapus kamar {nomor}?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.db.hapus_kamar(nomor)
                self.load_data()
                QMessageBox.information(self.main_window, "Sukses", "Kamar berhasil dihapus")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Gagal menghapus kamar:\n{str(e)}")
    
    def checkin_penyewa(self):
        QMessageBox.information(self.main_window, "Info", "Fitur check-in akan diimplementasikan")
    
    def checkout_penyewa(self):
        QMessageBox.information(self.main_window, "Info", "Fitur check-out akan diimplementasikan")
    
    def pembayaran(self):
        QMessageBox.information(self.main_window, "Info", "Fitur pembayaran akan diimplementasikan")
    
    def filter_laporan(self):
        QMessageBox.information(self.main_window, "Info", "Fitur filter akan diimplementasikan")

# ==================== MAIN APPLICATION ====================
class KostApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
        self.controller = MainController(self.main_window)
        self.setup_style()
    
    def setup_style(self):
        self.app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 12px;
                min-width: 80px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTableWidget {
                alternate-background-color: #f9f9f9;
                gridline-color: #ddd;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                margin-top: 5px;
            }
            QTabBar::tab {
                padding: 8px 15px;
                background: #e0e0e0;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #f5f5f5;
                border-bottom: 2px solid #4CAF50;
                font-weight: bold;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 13px;
            }
            QStatusBar {
                font-size: 12px;
            }
        """)
    
    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    try:
        app = KostApp()
        app.run()
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error", f"Aplikasi tidak dapat dijalankan:\n{str(e)}")
