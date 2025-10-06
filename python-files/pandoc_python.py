import sys
import os
import tempfile
import subprocess
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QLabel, 
                             QFileDialog, QMessageBox, QGroupBox, QScrollArea,
                             QSplitter, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextDocument
from io import BytesIO

class ConversionWorker(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, markdown_text):
        super().__init__()
        self.markdown_text = markdown_text
    
    def run(self):
        try:
            # Tạo thư mục tạm thời
            temp_dir = tempfile.mkdtemp()
            
            # Đường dẫn files
            md_file = os.path.join(temp_dir, "input.md")
            docx_file = os.path.join(temp_dir, "output.docx")
            
            # Lưu markdown vào file
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(self.markdown_text)
            
            # Chạy pandoc để chuyển đổi
            pandoc_command = [
                "pandoc",
                md_file,
                "-o", docx_file,
                "--from", "markdown",
                "--to", "docx",
                "--standalone"
            ]
            
            result = subprocess.run(
                pandoc_command,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Đọc file Word đã tạo
            with open(docx_file, "rb") as f:
                docx_data = f.read()
            
            # Dọn dẹp thư mục tạm
            shutil.rmtree(temp_dir)
            
            self.finished.emit({
                "success": True,
                "data": docx_data,
                "message": "Chuyển đổi thành công!"
            })
            
        except subprocess.CalledProcessError as e:
            self.finished.emit({
                "success": False,
                "error": f"Lỗi pandoc: {e.stderr}",
                "message": "Chuyển đổi thất bại!"
            })
        except Exception as e:
            self.finished.emit({
                "success": False,
                "error": str(e),
                "message": "Có lỗi xảy ra!"
            })

class MarkdownToWordConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.docx_data = None
        self.init_ui()
        self.apply_styles()
        self.check_pandoc()
    
    def init_ui(self):
        self.setWindowTitle("📝 Markdown to Word Converter")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("📝 Markdown to Word Converter")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("Chuyển đổi Markdown thành file Word một cách dễ dàng")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addWidget(header_frame)
        
        # Splitter cho main content và sidebar
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Main content area
        main_content = QWidget()
        content_layout = QVBoxLayout(main_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Markdown input area
        input_group = QGroupBox("✍️ Nhập nội dung Markdown")
        input_group.setObjectName("cardGroup")
        input_layout = QVBoxLayout(input_group)
        
        self.markdown_input = QTextEdit()
        self.markdown_input.setObjectName("markdownInput")
        self.markdown_input.setPlaceholderText("""# Tiêu đề chính

## Tiêu đề phụ

Đây là đoạn văn bản **in đậm** và *in nghiêng*.

### Danh sách
- Mục 1
- Mục 2
- Mục 3

### Bảng
| Cột 1 | Cột 2 | Cột 3 |
|-------|-------|-------|
| A     | B     | C     |
| 1     | 2     | 3     |

> Đây là một trích dẫn

```python
print("Hello World!")
```
""")
        self.markdown_input.textChanged.connect(self.update_stats)
        
        input_layout.addWidget(self.markdown_input)
        content_layout.addWidget(input_group)
        
        # Preview area
        preview_group = QGroupBox("👀 Xem trước")
        preview_group.setObjectName("cardGroup")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_area = QTextEdit()
        self.preview_area.setObjectName("previewArea")
        self.preview_area.setReadOnly(True)
        
        preview_layout.addWidget(self.preview_area)
        content_layout.addWidget(preview_group)
        
        splitter.addWidget(main_content)
        
        # Sidebar
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 0, 0, 0)
        
        # Author card
        author_frame = QFrame()
        author_frame.setObjectName("authorCard")
        author_layout = QVBoxLayout(author_frame)
        
        avatar_label = QLabel("NP")
        avatar_label.setObjectName("avatarLabel")
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        name_label = QLabel("Nguyễn Hữu Phúc")
        name_label.setObjectName("nameLabel")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        role_label = QLabel("Developer")
        role_label.setObjectName("roleLabel")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        author_layout.addWidget(avatar_label)
        author_layout.addWidget(name_label)
        author_layout.addWidget(role_label)
        sidebar_layout.addWidget(author_frame)
        
        # Features
        features_group = QGroupBox("🎯 Tính năng")
        features_group.setObjectName("cardGroup")
        features_layout = QVBoxLayout(features_group)
        
        features = [
            "✓ Dán markdown trực tiếp",
            "✓ Chuyển đổi sang Word",
            "✓ Hỗ trợ định dạng phong phú",
            "✓ Giao diện thân thiện",
            "✓ Xử lý nhanh chóng"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setObjectName("featureLabel")
            features_layout.addWidget(label)
        
        sidebar_layout.addWidget(features_group)
        
        # Statistics
        stats_group = QGroupBox("📊 Thống kê")
        stats_group.setObjectName("statsGroup")
        stats_layout = QVBoxLayout(stats_group)
        
        self.word_count_label = QLabel("Từ: 0")
        self.char_count_label = QLabel("Ký tự: 0")
        self.line_count_label = QLabel("Dòng: 0")
        
        for label in [self.word_count_label, self.char_count_label, self.line_count_label]:
            label.setObjectName("statLabel")
            stats_layout.addWidget(label)
        
        sidebar_layout.addWidget(stats_group)
        
        # Pandoc status
        self.pandoc_status = QLabel()
        self.pandoc_status.setObjectName("pandocStatus")
        sidebar_layout.addWidget(self.pandoc_status)
        
        # Buttons
        self.convert_btn = QPushButton("🔄 Chuyển đổi sang Word")
        self.convert_btn.setObjectName("convertBtn")
        self.convert_btn.clicked.connect(self.convert_markdown)
        sidebar_layout.addWidget(self.convert_btn)
        
        self.download_btn = QPushButton("⬇️ Tải file Word")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self.download_word)
        self.download_btn.setEnabled(False)
        sidebar_layout.addWidget(self.download_btn)
        
        # Contact info
        contact_group = QGroupBox("📞 Liên hệ")
        contact_group.setObjectName("cardGroup")
        contact_layout = QVBoxLayout(contact_group)
        
        contacts = [
            "📱 Zalo: 0985.692.879",
            "📘 Facebook: nhphuclk",
            "🌐 Website: aiomtpremium.com",
            "📺 YouTube: @aiomtpremium"
        ]
        
        for contact in contacts:
            label = QLabel(contact)
            label.setObjectName("contactLabel")
            contact_layout.addWidget(label)
        
        sidebar_layout.addWidget(contact_group)
        sidebar_layout.addStretch()
        
        splitter.addWidget(sidebar)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Footer
        footer_label = QLabel("💡 Hỗ trợ đầy đủ cú pháp Markdown • Chuyển đổi nhanh chóng • Giao diện thân thiện")
        footer_label.setObjectName("footerLabel")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(footer_label)
    
    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #008080, stop:1 #20b2aa);
                border-radius: 15px;
                padding: 20px;
            }
            
            #titleLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                padding: 10px;
            }
            
            #subtitleLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                padding: 5px;
            }
            
            #cardGroup {
                background-color: white;
                border: 1px solid #e6ffff;
                border-radius: 12px;
                padding: 15px;
                font-weight: bold;
                color: #008080;
            }
            
            #markdownInput, #previewArea {
                border: 2px solid #e6ffff;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                background-color: white;
                font-size: 13px;
            }
            
            #markdownInput:focus, #previewArea:focus {
                border: 2px solid #008080;
            }
            
            #authorCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #008080, stop:1 #20b2aa);
                border-radius: 12px;
                padding: 20px;
            }
            
            #avatarLabel {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                font-size: 32px;
                font-weight: bold;
                border-radius: 40px;
                min-width: 80px;
                max-width: 80px;
                min-height: 80px;
                max-height: 80px;
            }
            
            #nameLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            
            #roleLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                margin-top: 5px;
            }
            
            #statsGroup {
                background: linear-gradient(135deg, #f0fdfd, #e6ffff);
                border: 1px solid #e6ffff;
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
                color: #008080;
            }
            
            #statLabel {
                color: #008080;
                font-weight: bold;
                padding: 5px;
            }
            
            #featureLabel, #contactLabel {
                color: #333;
                padding: 5px;
            }
            
            #convertBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #008080, stop:1 #20b2aa);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #convertBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #006666, stop:1 #008080);
            }
            
            #convertBtn:disabled {
                background: #cccccc;
            }
            
            #downloadBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #28a745, stop:1 #20c997);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #downloadBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #218838, stop:1 #1ea976);
            }
            
            #downloadBtn:disabled {
                background: #cccccc;
            }
            
            #pandocStatus {
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            
            #footerLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0fdfd, stop:1 white);
                color: #008080;
                font-weight: 500;
                padding: 20px;
                border-radius: 12px;
            }
        """)
    
    def check_pandoc(self):
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.split('\n')[0]
            self.pandoc_status.setText(f"✅ {version}")
            self.pandoc_status.setStyleSheet("background-color: #d4edda; color: #155724;")
        except:
            self.pandoc_status.setText("❌ Pandoc chưa được cài đặt")
            self.pandoc_status.setStyleSheet("background-color: #f8d7da; color: #721c24;")
            self.convert_btn.setEnabled(False)
    
    def update_stats(self):
        text = self.markdown_input.toPlainText()
        
        if text.strip():
            words = len(text.split())
            chars = len(text)
            lines = len(text.split('\n'))
            
            self.word_count_label.setText(f"Từ: {words:,}")
            self.char_count_label.setText(f"Ký tự: {chars:,}")
            self.line_count_label.setText(f"Dòng: {lines:,}")
            
            # Update preview
            self.preview_area.setMarkdown(text)
        else:
            self.word_count_label.setText("Từ: 0")
            self.char_count_label.setText("Ký tự: 0")
            self.line_count_label.setText("Dòng: 0")
            self.preview_area.clear()
    
    def convert_markdown(self):
        markdown_text = self.markdown_input.toPlainText()
        
        if not markdown_text.strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập nội dung Markdown!")
            return
        
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText("🔄 Đang chuyển đổi...")
        
        self.worker = ConversionWorker(markdown_text)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.start()
    
    def conversion_finished(self, result):
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText("🔄 Chuyển đổi sang Word")
        
        if result["success"]:
            self.docx_data = result["data"]
            self.download_btn.setEnabled(True)
            QMessageBox.information(self, "Thành công", result["message"])
        else:
            error_msg = result["message"]
            if "error" in result:
                error_msg += f"\n\nChi tiết lỗi: {result['error']}"
            QMessageBox.critical(self, "Lỗi", error_msg)
    
    def download_word(self):
        if not self.docx_data:
            return
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Lưu file Word",
            "converted_document.docx",
            "Word Documents (*.docx)"
        )
        
        if file_name:
            try:
                with open(file_name, "wb") as f:
                    f.write(self.docx_data)
                QMessageBox.information(self, "Thành công", f"Đã lưu file: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Windows')  # Sử dụng style mặc định của Windows
    window = MarkdownToWordConverter()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()