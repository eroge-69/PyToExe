import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QLabel, QFileDialog, QMessageBox,
                            QProgressBar, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
import io

class DocumentProcessor(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, doc_path, signature_path, output_path):
        super().__init__()
        self.doc_path = doc_path
        self.signature_path = signature_path
        self.output_path = output_path
        
    def convert_to_transparent_png(self, image_path):
        """Chuyển đổi ảnh sang PNG với background trong suốt"""
        try:
            # Mở ảnh
            img = Image.open(image_path).convert("RGBA")
            
            # Tạo ảnh mới với background trong suốt
            transparent_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
            
            # Nếu ảnh gốc có background trắng, làm cho nó trong suốt
            data = img.getdata()
            new_data = []
            for item in data:
                # Thay đổi tất cả pixel trắng (hoặc gần trắng) thành trong suốt
                if item[0] > 200 and item[1] > 200 and item[2] > 200:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            transparent_img.putdata(new_data)
            
            # Lưu vào bộ nhớ tạm
            temp_path = "temp_signature.png"
            transparent_img.save(temp_path, "PNG")
            return temp_path
            
        except Exception as e:
            raise Exception(f"Lỗi khi xử lý ảnh chữ ký: {str(e)}")
    
    def process_pdf(self):
        """Xử lý file PDF"""
        doc = fitz.open(self.doc_path)
        
        # Chuyển đổi chữ ký sang PNG trong suốt
        signature_png = self.convert_to_transparent_png(self.signature_path)
        
        self.progress.emit(30)
        
        # Tìm vị trí "Người lập kế hoạch" trong tài liệu
        signature_inserted = False
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_instances = page.search_for("Người lập kế hoạch")
            
            if text_instances:
                # Lấy vị trí đầu tiên tìm thấy
                rect = text_instances[0]
                
                # Tính toán vị trí chèn chữ ký (dưới text)
                x = rect.x0
                y = rect.y1 + 3  # Cách text 10 pixel
                
                # Chèn ảnh chữ ký
                img_rect = fitz.Rect(x, y, x + 80, y + 50)  # Kích thước 70x50
                page.insert_image(img_rect, filename=signature_png)
                signature_inserted = True
                break
        
        # Nếu không tìm thấy "Người lập kế hoạch", tìm các từ khóa thay thế
        if not signature_inserted:
            alt_keywords = ["Người lập", "kế hoạch", "lập kế hoạch", "Lập kế hoạch"]
            for keyword in alt_keywords:
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text_instances = page.search_for(keyword)
                    
                    if text_instances:
                        # Lấy vị trí đầu tiên tìm thấy
                        rect = text_instances[0]
                        
                        # Tính toán vị trí chèn chữ ký
                        x = rect.x0 + 100  # Bên phải text 100 pixel
                        y = rect.y0
                        
                        # Chèn ảnh chữ ký
                        img_rect = fitz.Rect(x, y, x + 60, y + 40)  # Kích thước nhỏ hơn
                        page.insert_image(img_rect, filename=signature_png)
                        signature_inserted = True
                        break
                
                if signature_inserted:
                    break
        
        self.progress.emit(80)
        
        # Lưu file
        doc.save(self.output_path)
        doc.close()
        
        # Xóa file tạm
        if os.path.exists(signature_png):
            os.remove(signature_png)
            
        self.progress.emit(100)
        
        if not signature_inserted:
            raise Exception("Không tìm thấy vị trí phù hợp để chèn chữ ký. Vui lòng kiểm tra lại tài liệu có chứa text 'Người lập kế hoạch' hoặc các từ khóa liên quan.")
    
    def run(self):
        try:
            file_ext = Path(self.doc_path).suffix.lower()
            
            if file_ext == '.pdf':
                self.process_pdf()
            else:
                self.error.emit("Chỉ hỗ trợ file PDF!")
                return
                
            self.finished.emit("Chèn chữ ký vào PDF thành công!")
            
        except Exception as e:
            self.error.emit(f"Lỗi xử lý: {str(e)}")

class SignatureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.document_path = ""
        self.signature_path = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Phần mềm chèn chữ ký vào file PDF")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget chính
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Tiêu đề
        title = QLabel("PHẦN MỀM CHÈN CHỮ KÝ VÀO FILE PDF")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2E86C1; margin: 20px;")
        layout.addWidget(title)
        
        # Group box cho chọn file PDF
        doc_group = QGroupBox("1. Chọn file PDF cần chèn chữ ký")
        doc_group.setFont(QFont("Arial", 11))
        doc_layout = QVBoxLayout(doc_group)
        
        doc_info = QLabel("Chỉ hỗ trợ file PDF (.pdf)")
        doc_info.setStyleSheet("color: #666; font-style: italic;")
        doc_layout.addWidget(doc_info)
        
        doc_button_layout = QHBoxLayout()
        self.doc_button = QPushButton("Chọn file PDF")
        self.doc_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        self.doc_button.clicked.connect(self.select_document)
        
        self.doc_label = QLabel("Chưa chọn file PDF")
        self.doc_label.setStyleSheet("color: #E74C3C; font-style: italic;")
        
        doc_button_layout.addWidget(self.doc_button)
        doc_button_layout.addWidget(self.doc_label)
        doc_button_layout.addStretch()
        
        doc_layout.addLayout(doc_button_layout)
        layout.addWidget(doc_group)
        
        # Group box cho chọn chữ ký
        sig_group = QGroupBox("2. Chọn ảnh chữ ký")
        sig_group.setFont(QFont("Arial", 11))
        sig_layout = QVBoxLayout(sig_group)
        
        sig_info = QLabel("Hỗ trợ: JPG, PNG, BMP (sẽ tự động loại bỏ background trắng)")
        sig_info.setStyleSheet("color: #666; font-style: italic;")
        sig_layout.addWidget(sig_info)
        
        sig_button_layout = QHBoxLayout()
        self.sig_button = QPushButton("Chọn ảnh chữ ký")
        self.sig_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.sig_button.clicked.connect(self.select_signature)
        
        self.sig_label = QLabel("Chưa chọn ảnh")
        self.sig_label.setStyleSheet("color: #E74C3C; font-style: italic;")
        
        # Preview ảnh chữ ký
        self.signature_preview = QLabel()
        self.signature_preview.setMaximumSize(200, 100)
        self.signature_preview.setStyleSheet("border: 1px solid #BDC3C7; background: #F8F9FA;")
        self.signature_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.signature_preview.setText("Xem trước chữ ký")
        
        sig_button_layout.addWidget(self.sig_button)
        sig_button_layout.addWidget(self.sig_label)
        sig_button_layout.addStretch()
        sig_button_layout.addWidget(self.signature_preview)
        
        sig_layout.addLayout(sig_button_layout)
        layout.addWidget(sig_group)
        
        # Group box cho xử lý
        process_group = QGroupBox("3. Xử lý và lưu file PDF")
        process_group.setFont(QFont("Arial", 11))
        process_layout = QVBoxLayout(process_group)
        
        # Thông tin xử lý
        process_info = QLabel("Chữ ký sẽ được chèn tại vị trí text 'Người lập kế hoạch' trong PDF")
        process_info.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        process_layout.addWidget(process_info)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        process_layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.process_button = QPushButton("Chèn chữ ký vào PDF")
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #E67E22;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D35400;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        self.process_button.clicked.connect(self.process_document)
        self.process_button.setEnabled(False)
        
        self.clear_button = QPushButton("Xóa tất cả")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        self.clear_button.clicked.connect(self.clear_all)
        
        button_layout.addWidget(self.process_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        
        process_layout.addLayout(button_layout)
        layout.addWidget(process_group)
        
        # Log area
        log_group = QGroupBox("Nhật ký hoạt động")
        log_group.setFont(QFont("Arial", 11))
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("background-color: #F8F9FA; border: 1px solid #BDC3C7;")
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Add stretch
        layout.addStretch()
        
        self.log("Ứng dụng đã khởi động. Sẵn sàng xử lý file PDF.")
    
    def log(self, message):
        """Thêm message vào log"""
        self.log_text.append(f"[{QDateTime.currentDateTime().toString('hh:mm:ss')}] {message}")
        
    def select_document(self):
        """Chọn file PDF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Chọn file PDF",
            "",
            "PDF files (*.pdf)"
        )
        
        if file_path:
            self.document_path = file_path
            file_name = Path(file_path).name
            self.doc_label.setText(f"✓ {file_name}")
            self.doc_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            self.log(f"Đã chọn file PDF: {file_name}")
            self.check_ready()
    
    def select_signature(self):
        """Chọn ảnh chữ ký"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn ảnh chữ ký", 
            "",
            "Image files (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if file_path:
            self.signature_path = file_path
            file_name = Path(file_path).name
            self.sig_label.setText(f"✓ {file_name}")
            self.sig_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            
            # Hiển thị preview
            try:
                pixmap = QPixmap(file_path)
                scaled_pixmap = pixmap.scaled(180, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.signature_preview.setPixmap(scaled_pixmap)
                self.log(f"Đã chọn chữ ký: {file_name}")
            except Exception as e:
                self.log(f"Lỗi hiển thị preview: {str(e)}")
            
            self.check_ready()
    
    def check_ready(self):
        """Kiểm tra xem đã sẵn sàng xử lý chưa"""
        if self.document_path and self.signature_path:
            self.process_button.setEnabled(True)
        else:
            self.process_button.setEnabled(False)
    
    def process_document(self):
        """Xử lý chèn chữ ký vào PDF"""
        if not self.document_path or not self.signature_path:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn đầy đủ file PDF và ảnh chữ ký!")
            return
        
        # Chọn nơi lưu file
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file PDF đã chèn chữ ký",
            "signed_document.pdf",
            "PDF files (*.pdf)"
        )
        
        if not output_path:
            return
        
        # Hiển thị progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.process_button.setEnabled(False)
        self.log("Bắt đầu xử lý chèn chữ ký vào PDF...")
        
        # Tạo và chạy thread xử lý
        self.processor_thread = DocumentProcessor(
            self.document_path, 
            self.signature_path, 
            output_path
        )
        self.processor_thread.progress.connect(self.progress_bar.setValue)
        self.processor_thread.finished.connect(self.on_process_finished)
        self.processor_thread.error.connect(self.on_process_error)
        self.processor_thread.start()
    
    def on_process_finished(self, message):
        """Xử lý khi hoàn thành"""
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        self.log(message)
        QMessageBox.information(self, "Thành công", message)
    
    def on_process_error(self, error_message):
        """Xử lý khi có lỗi"""
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        self.log(f"Lỗi: {error_message}")
        QMessageBox.critical(self, "Lỗi", error_message)
    
    def clear_all(self):
        """Xóa tất cả lựa chọn"""
        self.document_path = ""
        self.signature_path = ""
        
        self.doc_label.setText("Chưa chọn file PDF")
        self.doc_label.setStyleSheet("color: #E74C3C; font-style: italic;")
        
        self.sig_label.setText("Chưa chọn ảnh")
        self.sig_label.setStyleSheet("color: #E74C3C; font-style: italic;")
        
        self.signature_preview.clear()
        self.signature_preview.setText("Xem trước chữ ký")
        
        self.process_button.setEnabled(False)
        self.log("Đã xóa tất cả lựa chọn")

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("PDF Signature Inserter")
    app.setApplicationVersion("1.0")
    
    window = SignatureApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()