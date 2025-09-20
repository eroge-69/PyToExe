import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QLineEdit, QSpinBox, QComboBox, QFileDialog, 
                             QScrollArea, QFrame, QMessageBox, QProgressBar,
                             QGroupBox, QCheckBox, QDoubleSpinBox, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon, QPalette, QColor, QDragEnterEvent, QDropEvent
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4, A3, A2, A1, A0
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, cm
import math

class ImageProcessor(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, images, page_size, copies, cut_margin, output_path):
        super().__init__()
        self.images = images
        self.page_size = page_size
        self.copies = copies
        self.cut_margin = cut_margin
        self.output_path = output_path
        
    def run(self):
        try:
            # Sayfa boyutlarını belirle
            page_sizes = {
                'A4': A4,
                'A3': A3, 
                'A2': A2,
                'A1': A1,
                'A0': A0
            }
            
            if self.page_size not in page_sizes:
                raise ValueError("Geçersiz sayfa boyutu")
                
            page_width, page_height = page_sizes[self.page_size]
            
            # PDF oluştur
            c = canvas.Canvas(self.output_path, pagesize=page_sizes[self.page_size])
            
            margin = 10 * mm
            usable_width = page_width - (2 * margin)
            usable_height = page_height - (2 * margin)
            
            current_page = 1
            images_on_page = 0
            
            # Her görsel için
            total_images = len(self.images) * self.copies
            processed = 0
            
            for image_path in self.images:
                for copy in range(self.copies):
                    if processed % 10 == 0:
                        self.progress.emit(int((processed / total_images) * 100))
                    
                    try:
                        # Görseli yükle
                        img = Image.open(image_path)
                        
                        # Görsel boyutlarını al
                        img_width, img_height = img.size
                        
                        # Sayfa boyutuna göre ölçekle
                        scale_w = (usable_width * 0.8) / img_width
                        scale_h = (usable_height * 0.8) / img_height
                        scale = min(scale_w, scale_h)
                        
                        new_width = img_width * scale
                        new_height = img_height * scale
                        
                        # Sayfa merkezine yerleştir
                        x = margin + (usable_width - new_width) / 2
                        y = margin + (usable_height - new_height) / 2
                        
                        # Kesim çizgisi çiz (dış çerçeve)
                        cut_x = x - self.cut_margin * mm
                        cut_y = y - self.cut_margin * mm
                        cut_width = new_width + (2 * self.cut_margin * mm)
                        cut_height = new_height + (2 * self.cut_margin * mm)
                        
                        # Kesim çizgisi (kesikli çizgi)
                        c.setDash(3, 3)
                        c.setStrokeColor((0.5, 0.5, 0.5))
                        c.setLineWidth(0.5)
                        c.rect(cut_x, cut_y, cut_width, cut_height)
                        
                        # Normal çizgi moduna dön
                        c.setDash()
                        c.setStrokeColor((0, 0, 0))
                        c.setLineWidth(1)
                        
                        # Görseli PDF'e ekle
                        c.drawImage(image_path, x, y, width=new_width, height=new_height)
                        
                        images_on_page += 1
                        processed += 1
                        
                        # Eğer birden fazla görsel varsa yeni sayfa oluştur
                        if processed < total_images:
                            c.showPage()
                            current_page += 1
                            images_on_page = 0
                            
                    except Exception as e:
                        print(f"Görsel işlenirken hata: {e}")
                        continue
            
            # PDF'i kaydet
            c.save()
            self.finished.emit(f"PDF başarıyla oluşturuldu: {self.output_path}")
            
        except Exception as e:
            self.error.emit(f"PDF oluşturulurken hata: {str(e)}")

class ImagePreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(150, 150)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Görsel\nYok")

class ModernButton(QPushButton):
    def __init__(self, text, color="#007bff"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {self.darker_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darker_color(color, 0.8)};
            }}
            QPushButton:disabled {{
                background-color: #6c757d;
            }}
        """)
    
    def darker_color(self, color, factor=0.9):
        # Basit renk koyulaştırma
        if color == "#007bff":
            return "#0056b3" if factor == 0.9 else "#004085"
        elif color == "#28a745":
            return "#1e7e34" if factor == 0.9 else "#155724"
        elif color == "#dc3545":
            return "#c82333" if factor == 0.9 else "#bd2130"
        return color

class MatbaaMontajProgrami(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Matbaa Montaj Programı v2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Sol panel - Kontroller
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        
        # Logo ve başlık
        title_label = QLabel("🖨️ MATBAA MONTAJ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #343a40;
                padding: 15px;
                background-color: white;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        left_layout.addWidget(title_label)
        
        # Görsel yükleme grubu
        image_group = QGroupBox("📷 Görseller")
        image_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        image_layout = QVBoxLayout(image_group)
        
        self.load_images_btn = ModernButton("🖼️ Görselleri Yükle")
        self.load_images_btn.clicked.connect(self.load_images)
        image_layout.addWidget(self.load_images_btn)
        
        self.clear_images_btn = ModernButton("🗑️ Görselleri Temizle", "#dc3545")
        self.clear_images_btn.clicked.connect(self.clear_images)
        image_layout.addWidget(self.clear_images_btn)
        
        self.image_count_label = QLabel("Yüklenen görsel: 0")
        self.image_count_label.setStyleSheet("color: #6c757d; padding: 5px;")
        image_layout.addWidget(self.image_count_label)
        
        left_layout.addWidget(image_group)
        
        # Ayarlar grubu
        settings_group = QGroupBox("⚙️ Montaj Ayarları")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        settings_layout = QGridLayout(settings_group)
        
        # Sayfa boyutu
        settings_layout.addWidget(QLabel("📏 Sayfa Boyutu:"), 0, 0)
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(['A4', 'A3', 'A2', 'A1', 'A0'])
        self.page_size_combo.setCurrentText('A4')
        settings_layout.addWidget(self.page_size_combo, 0, 1)
        
        # Kopya sayısı
        settings_layout.addWidget(QLabel("📊 Her Görsel için Kopya:"), 1, 0)
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 100)
        self.copies_spin.setValue(1)
        settings_layout.addWidget(self.copies_spin, 1, 1)
        
        # Kesim marjı
        settings_layout.addWidget(QLabel("✂️ Kesim Marjı (mm):"), 2, 0)
        self.cut_margin_spin = QDoubleSpinBox()
        self.cut_margin_spin.setRange(0, 20)
        self.cut_margin_spin.setValue(3)
        self.cut_margin_spin.setSuffix(" mm")
        settings_layout.addWidget(self.cut_margin_spin, 2, 1)
        
        left_layout.addWidget(settings_group)
        
        # İşlem grubu
        process_group = QGroupBox("🚀 İşlemler")
        process_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        process_layout = QVBoxLayout(process_group)
        
        self.generate_pdf_btn = ModernButton("📄 PDF Oluştur", "#28a745")
        self.generate_pdf_btn.clicked.connect(self.generate_pdf)
        self.generate_pdf_btn.setEnabled(False)
        process_layout.addWidget(self.generate_pdf_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #007bff;
                border-radius: 8px;
                text-align: center;
                padding: 2px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 6px;
            }
        """)
        process_layout.addWidget(self.progress_bar)
        
        left_layout.addWidget(process_group)
        
        # Bilgi alanı
        info_group = QGroupBox("ℹ️ Bilgiler")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setPlainText("""• Desteklenen formatlar: JPG, PNG, BMP, TIFF
• Her görsel ayrı sayfaya yerleştirilir
• Kesim çizgileri otomatik eklenir
• PDF çıktısı yüksek kalitede olur""")
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 8px;
                font-size: 11px;
            }
        """)
        info_layout.addWidget(self.info_text)
        
        left_layout.addWidget(info_group)
        left_layout.addStretch()
        
        # Sağ panel - Önizleme
        right_panel = QWidget()
        right_panel.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        
        preview_title = QLabel("👁️ Görsel Önizleme")
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #343a40;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        right_layout.addWidget(preview_title)
        
        # Scroll area for image previews
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        self.preview_widget = QWidget()
        self.preview_layout = QGridLayout(self.preview_widget)
        scroll_area.setWidget(self.preview_widget)
        
        right_layout.addWidget(scroll_area)
        
        # Ana layout'a panelleri ekle
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 2)
        
        # Style sheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #e9ecef;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                background-color: white;
            }
            QLabel {
                color: #495057;
            }
        """)
        
    def load_images(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Görselleri Seç",
            "",
            "Görsel Dosyaları (*.jpg *.jpeg *.png *.bmp *.tiff *.tif)"
        )
        
        if file_paths:
            self.images = file_paths
            self.update_preview()
            self.update_ui()
            
    def clear_images(self):
        self.images = []
        self.update_preview()
        self.update_ui()
        
    def update_preview(self):
        # Önceki önizlemeleri temizle
        for i in reversed(range(self.preview_layout.count())): 
            self.preview_layout.itemAt(i).widget().setParent(None)
        
        if not self.images:
            no_image_label = QLabel("Görsel yüklenmedi\n\n📷\n\nGörsel yüklemek için\n'Görselleri Yükle' butonunu kullanın")
            no_image_label.setAlignment(Qt.AlignCenter)
            no_image_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font-size: 14px;
                    border: 2px dashed #adb5bd;
                    border-radius: 10px;
                    padding: 50px;
                    background-color: white;
                }
            """)
            self.preview_layout.addWidget(no_image_label, 0, 0)
            return
        
        # Görselleri grid'de göster (3 sütun)
        row, col = 0, 0
        for i, image_path in enumerate(self.images):
            try:
                # Container widget
                container = QFrame()
                container.setFrameStyle(QFrame.Box)
                container.setStyleSheet("""
                    QFrame {
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        background-color: white;
                        padding: 10px;
                    }
                """)
                container_layout = QVBoxLayout(container)
                
                # Görsel önizleme
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    preview_label = QLabel()
                    preview_label.setFixedSize(150, 150)
                    
                    # Görüntüyü boyutlandır
                    scaled_pixmap = pixmap.scaled(
                        150, 150, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    
                    preview_label.setPixmap(scaled_pixmap)
                    preview_label.setAlignment(Qt.AlignCenter)
                    preview_label.setStyleSheet("""
                        QLabel {
                            border: 1px solid #ced4da;
                            border-radius: 5px;
                            background-color: #f8f9fa;
                        }
                    """)
                    container_layout.addWidget(preview_label)
                
                # Dosya adı
                file_name = os.path.basename(image_path)
                if len(file_name) > 20:
                    file_name = file_name[:17] + "..."
                
                name_label = QLabel(file_name)
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setStyleSheet("""
                    QLabel {
                        font-size: 11px;
                        color: #6c757d;
                        padding: 5px;
                    }
                """)
                container_layout.addWidget(name_label)
                
                self.preview_layout.addWidget(container, row, col)
                
                col += 1
                if col >= 3:  # 3 sütunluk grid
                    col = 0
                    row += 1
                    
            except Exception as e:
                print(f"Önizleme hatası: {e}")
                continue
    
    def update_ui(self):
        self.image_count_label.setText(f"Yüklenen görsel: {len(self.images)}")
        self.generate_pdf_btn.setEnabled(len(self.images) > 0)
        
    def generate_pdf(self):
        if not self.images:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce görselleri yükleyin!")
            return
        
        # Çıktı dosyası seç
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "PDF Kaydet",
            f"montaj_{len(self.images)}_gorsel.pdf",
            "PDF Dosyaları (*.pdf)"
        )
        
        if not output_path:
            return
        
        # Progress bar göster
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.generate_pdf_btn.setEnabled(False)
        
        # İşlem thread'i başlat
        self.processor = ImageProcessor(
            self.images,
            self.page_size_combo.currentText(),
            self.copies_spin.value(),
            self.cut_margin_spin.value(),
            output_path
        )
        
        self.processor.progress.connect(self.progress_bar.setValue)
        self.processor.finished.connect(self.on_pdf_finished)
        self.processor.error.connect(self.on_pdf_error)
        self.processor.start()
    
    def on_pdf_finished(self, message):
        self.progress_bar.setVisible(False)
        self.generate_pdf_btn.setEnabled(True)
        QMessageBox.information(self, "Başarılı", message)
        
    def on_pdf_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.generate_pdf_btn.setEnabled(True)
        QMessageBox.critical(self, "Hata", error_message)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern görünüm
    
    # Uygulama ikonunu ayarla (varsa)
    app.setApplicationName("Matbaa Montaj Programı")
    app.setApplicationVersion("2.0")
    
    window = MatbaaMontajProgrami()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()