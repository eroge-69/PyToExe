import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QLineEdit, QProgressBar, QMessageBox,
    QHBoxLayout, QTextEdit, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QDateTime
from PyQt6.QtGui import QIntValidator

# --- (Bagian PdfSplitterThread tanpa logika pembatalan) ---
class PdfSplitterThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str, dict)

    def __init__(self, source_folder, destination_folder, size_limit_mb, parent=None):
        super().__init__(parent)
        self.source_folder = source_folder
        self.destination_folder = destination_folder
        self.size_limit_bytes = size_limit_mb * 1024 * 1024

    def _log(self, message):
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.log_signal.emit(f"[{timestamp}] {message}")

    def run(self):
        folder_sizes = {}
        try:
            self._log("Memulai proses pembagian PDF...")
            self.status_signal.emit("Memvalidasi folder dan mencari file PDF...")

            if not os.path.isdir(self.source_folder):
                self._log(f"Error: Folder sumber '{self.source_folder}' tidak ditemukan atau bukan direktori.")
                self.finished_signal.emit(False, "Folder sumber tidak ditemukan.", {})
                return

            if not os.path.exists(self.destination_folder):
                os.makedirs(self.destination_folder)
                self.status_signal.emit(f"Membuat folder tujuan: {self.destination_folder}")
                self._log(f"Membuat folder tujuan: {self.destination_folder}")
            else:
                self._log(f"Folder tujuan sudah ada: {self.destination_folder}")

            pdf_files = []
            self._log(f"Mencari file PDF di '{self.source_folder}'...")
            for root, _, files in os.walk(self.source_folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            pdf_files.append((file_path, file_size))
                            self._log(f"Ditemukan: '{os.path.basename(file_path)}' ({file_size / (1024 * 1024):.2f} MB)")
                        except OSError as e:
                            self._log(f"Peringatan: Gagal mendapatkan ukuran file '{os.path.basename(file_path)}': {e}. Melewatkan file ini.")

            if not pdf_files:
                self._log("Tidak ada file PDF yang ditemukan di folder sumber.")
                self.finished_signal.emit(False, "Tidak ada file PDF yang ditemukan di folder sumber.", {})
                return

            self._log(f"Total {len(pdf_files)} file PDF ditemukan.")
            self._log("Mengurutkan file berdasarkan ukuran (dari terbesar ke terkecil) untuk efisiensi...")
            pdf_files.sort(key=lambda x: x[1], reverse=True)

            current_folder_index = 1
            current_folder_size = 0
            current_folder_path = os.path.join(self.destination_folder, f"Folder {current_folder_index:01d}")
            os.makedirs(current_folder_path, exist_ok=True)
            folder_sizes[current_folder_path] = 0
            self._log(f"Membuat folder output awal: {os.path.basename(current_folder_path)}")
            self.status_signal.emit(f"Mulai menyalin ke '{os.path.basename(current_folder_path)}' (0.00 MB)")

            total_files = len(pdf_files)
            processed_files = 0

            for file_path, file_size in pdf_files:
                if current_folder_size > 0 and (current_folder_size + file_size > self.size_limit_bytes):
                    current_folder_size_mb = current_folder_size / (1024 * 1024)
                    limit_mb = self.size_limit_bytes / (1024 * 1024)
                    self._log(f"Batas {limit_mb:.2f} MB tercapai untuk '{os.path.basename(current_folder_path)}'. Ukuran final folder ini: {current_folder_size_mb:.2f} MB")

                    current_folder_index += 1
                    current_folder_size = 0
                    current_folder_path = os.path.join(self.destination_folder, f"Folder {current_folder_index:01d}")
                    os.makedirs(current_folder_path, exist_ok=True)
                    folder_sizes[current_folder_path] = 0
                    self._log(f"Membuat folder output baru: {os.path.basename(current_folder_path)}")
                    self.status_signal.emit(f"Pindah ke folder baru: '{os.path.basename(current_folder_path)}' (0.00 MB)")

                dest_file_path = os.path.join(current_folder_path, os.path.basename(file_path))
                try:
                    file_size_mb = file_size / (1024 * 1024)
                    self._log(f"Menyalin '{os.path.basename(file_path)}' ({file_size_mb:.2f} MB) ke '{os.path.basename(current_folder_path)}'")
                    shutil.copy2(file_path, dest_file_path)
                    current_folder_size += file_size
                    folder_sizes[current_folder_path] += file_size
                    self.status_signal.emit(f"Menyalin '{os.path.basename(file_path)}' ({current_folder_size / (1024 * 1024):.2f} MB)")
                except Exception as e:
                    self._log(f"Gagal menyalin '{os.path.basename(file_path)}': {e}")
                    self.status_signal.emit(f"Gagal menyalin '{os.path.basename(file_path)}'")

                processed_files += 1
                progress = int((processed_files / total_files) * 100)
                self.progress_signal.emit(progress)

            self._log("Proses pembagian PDF selesai. Melakukan verifikasi ukuran akhir folder...")
            final_folder_sizes_display = {}
            for folder_path, _ in folder_sizes.items():
                if os.path.exists(folder_path):
                    total_size_bytes_in_folder = sum(os.path.getsize(os.path.join(folder_path, f))
                                                     for f in os.listdir(folder_path)
                                                     if os.path.isfile(os.path.join(folder_path, f)))
                    final_folder_sizes_display[os.path.basename(folder_path)] = total_size_bytes_in_folder
                else:
                    final_folder_sizes_display[os.path.basename(folder_path)] = 0

            self._log("Semua file telah diproses.")
            self.finished_signal.emit(True, "Pembagian file PDF selesai!", final_folder_sizes_display)

        except Exception as e:
            self._log(f"Terjadi kesalahan fatal selama proses: {e}")
            self.finished_signal.emit(False, f"Terjadi kesalahan: {e}", {})

# --- (Bagian PdfSplitterApp tanpa tombol batal) ---
class PdfSplitterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF File Splitter")
        self.setGeometry(100, 100, 500, 400)

        self.source_folder = ""
        self.destination_folder = ""
        self.splitter_thread = None

        self.init_ui()

    def init_ui(self):
        # Menerapkan stylesheet global untuk tema gelap pada jendela utama
        # MODIFIKASI DIMULAI DI SINI UNTUK TEMA SUPER DARK
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a; /* Sangat gelap */
                color: #e0e0e0; /* Teks sedikit lebih gelap dari putih murni */
                font-family: Arial, sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #2a2a2a; /* Lebih gelap dari sebelumnya */
                border: 1px solid #444; /* Border lebih gelap */
                color: #e0e0e0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #007bff; /* Warna biru gelap yang umum untuk dark mode */
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3; /* Sedikit lebih gelap saat hover */
            }
            QPushButton:disabled {
                background-color: #333; /* Tombol non-aktif sangat gelap */
                color: #777; /* Teks non-aktif lebih gelap */
            }
            QTextEdit {
                background-color: #2a2a2a; /* Lebih gelap dari sebelumnya */
                color: #e0e0e0;
                border: 1px solid #444; /* Border lebih gelap */
                border-radius: 3px;
                padding: 5px;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                border: 1px solid #333; /* Border scrollbar lebih gelap */
                background: #2a2a2a; /* Latar scrollbar lebih gelap */
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555; /* Handle scrollbar tetap terlihat */
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: 1px solid #333;
                background: #2a2a2a;
                height: 10px;
                subcontrol-origin: margin;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: #e0e0e0; /* Panah tetap terang */
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        # MODIFIKASI BERAKHIR DI SINI UNTUK TEMA SUPER DARK

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # --- Bagian Pilihan Folder Sumber ---
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("<b>Folder Sumber PDF:</b>"))
        self.source_path_display = QLineEdit()
        self.source_path_display.setReadOnly(True)
        self.source_path_display.setPlaceholderText("Pilih folder yang berisi file PDF...")
        source_layout.addWidget(self.source_path_display)
        self.source_button = QPushButton("Pilih Folder")
        self.source_button.clicked.connect(self.select_source_folder)
        source_layout.addWidget(self.source_button)
        main_layout.addLayout(source_layout)

        # --- Bagian Pilihan Folder Tujuan ---
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("<b>Folder Tujuan Output:</b>"))
        self.dest_path_display = QLineEdit()
        self.dest_path_display.setReadOnly(True)
        self.dest_path_display.setPlaceholderText("Pilih folder untuk menyimpan output...")
        self.dest_button = QPushButton("Pilih Folder")
        self.dest_button.clicked.connect(self.select_destination_folder)
        dest_layout.addWidget(self.dest_path_display)
        dest_layout.addWidget(self.dest_button)
        main_layout.addLayout(dest_layout)

        # --- Batas Ukuran Input ---
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("<b>Batas Ukuran Per Folder (MB):</b>"))
        self.size_input = QLineEdit()
        self.size_input.setText("100")
        self.size_input.setValidator(QIntValidator(1, 10000, self))
        self.size_input.setMaximumWidth(100)
        size_layout.addWidget(self.size_input)
        size_layout.addStretch()
        main_layout.addLayout(size_layout)

        # --- Tombol Mulai (Hanya ada tombol ini) ---
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Mulai Pembagian PDF")
        self.start_button.clicked.connect(self.start_splitting)
        self.start_button.setEnabled(False)
        # Menyesuaikan warna tombol Mulai agar tetap terlihat di tema super dark
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8; /* Biru toska yang lebih tenang */
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #333; /* Konsisten dengan tombol non-aktif lainnya */
                color: #777;
            }
        """)
        button_layout.addWidget(self.start_button)
        main_layout.addLayout(button_layout)

        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- DESAIN PROGRESS BAR TEMA GELAP (Diperbarui) ---
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444; /* Border lebih gelap */
                border-radius: 5px;
                background-color: #2a2a2a; /* Latar progress bar lebih gelap */
                text-align: center;
                color: #e0e0e0; /* Teks progress bar terang */
                height: 25px;
            }

            QProgressBar::chunk {
                background-color: #6a1b9a; /* Warna ungu yang lebih dalam */
                width: 20px;
                margin: 0.5px;
                border-radius: 3px;
            }
        """)
        # --- AKHIR DESAIN PROGRESS BAR TEMA GELAP ---

        main_layout.addWidget(self.progress_bar)

        # --- Label Status ---
        self.status_label = QLabel("Siap untuk memulai...")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-weight: bold; color: #b0b0b0;") # Teks status sedikit lebih terang dari default
        main_layout.addWidget(self.status_label)

        # --- Area Log Display ---
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("Log proses akan muncul di sini...")
        self.log_display.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; background-color: #2a2a2a; border: 1px solid #444; color: #a0a0a0;") # Log area juga lebih gelap
        
        log_scroll_area = QScrollArea()
        log_scroll_area.setWidgetResizable(True)
        log_scroll_area.setWidget(self.log_display)
        log_scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(log_scroll_area)

        self.update_start_button_state()

    # --- Metode Pembantu UI (sama seperti sebelumnya) ---

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Sumber PDF")
        if folder:
            self.source_folder = folder
            self.source_path_display.setText(folder)
            self.update_start_button_state()

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Tujuan Output")
        if folder:
            self.destination_folder = folder
            self.dest_path_display.setText(folder)
            self.update_start_button_state()

    def update_start_button_state(self):
        is_ready = bool(self.source_folder and self.destination_folder and self.size_input.text())
        self.start_button.setEnabled(is_ready)

    def append_log(self, message):
        self.log_display.append(message)
        self.log_display.verticalScrollBar().setValue(self.log_display.verticalScrollBar().maximum())

    # --- Metode Logika Utama (tanpa pembatalan) ---

    def start_splitting(self):
        try:
            size_limit_text = self.size_input.text()
            if not size_limit_text:
                QMessageBox.warning(self, "Input Error", "Batas ukuran tidak boleh kosong.")
                return

            size_limit_mb = int(size_limit_text)
            if size_limit_mb <= 0:
                QMessageBox.warning(self, "Input Error", "Batas ukuran harus lebih besar dari 0 MB.")
                return

            if os.path.abspath(self.source_folder) == os.path.abspath(self.destination_folder):
                reply = QMessageBox.question(self, 'Peringatan Folder',
                                             "Folder sumber dan tujuan sama. Ini dapat menimpa atau mengganggu file asli. Lanjutkan?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                             QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return

            self.log_display.clear()
            self.append_log("--- Memulai Sesi Baru ---")
            self.append_log(f"Folder Sumber: {self.source_folder}")
            self.append_log(f"Folder Tujuan: {self.destination_folder}")
            self.append_log(f"Batas Ukuran Per Folder: {size_limit_mb} MB")

            self.start_button.setEnabled(False)
            self.source_button.setEnabled(False)
            self.dest_button.setEnabled(False)
            self.size_input.setReadOnly(True)
            self.status_label.setText("Memulai proses pembagian...")
            self.progress_bar.setValue(0)

            self.splitter_thread = PdfSplitterThread(
                self.source_folder, self.destination_folder, size_limit_mb
            )
            self.splitter_thread.progress_signal.connect(self.progress_bar.setValue)
            self.splitter_thread.status_signal.connect(self.status_label.setText)
            self.splitter_thread.log_signal.connect(self.append_log)
            self.splitter_thread.finished_signal.connect(self.on_splitting_finished)
            self.splitter_thread.start()

        except ValueError:
            QMessageBox.warning(self, "Input Error", "Batas ukuran harus berupa angka integer yang valid.")
            self.update_start_button_state()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan yang tidak terduga saat memulai: {e}")
            self.on_splitting_finished(False, f"Error tak terduga: {e}", {})

    def on_splitting_finished(self, success, message, folder_sizes):
        if success:
            QMessageBox.information(self, "Selesai", message)
            self.status_label.setText("Pembagian file PDF selesai!")
            self.append_log("--- Pembagian Selesai ---")
            self.append_log("Ukuran Akhir Setiap Folder:")
            if folder_sizes:
                sorted_folder_sizes = sorted(folder_sizes.items(), key=lambda item: int(item[0].split('_')[-1]))
                for folder_name, size_bytes in sorted_folder_sizes:
                    size_mb = size_bytes / (1024 * 1024)
                    self.append_log(f"  - {folder_name}: {size_mb:.2f} MB")
            else:
                self.append_log("  Tidak ada folder output yang dibuat atau informasi ukuran tidak tersedia.")
        else:
            QMessageBox.critical(self, "Gagal", message)
            self.status_label.setText(f"Gagal: {message}")
            self.append_log(f"--- Proses Gagal: {message} ---")

        self.start_button.setEnabled(True)
        self.source_button.setEnabled(True)
        self.dest_button.setEnabled(True)
        self.size_input.setReadOnly(False)
        self.update_start_button_state()

        self.splitter_thread = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfSplitterApp()
    window.show()
    sys.exit(app.exec())