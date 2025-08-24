import sys
import os
import shutil
import platform
import subprocess
import pandas as pd
from pptx import Presentation
from pptx.util import Inches
from datetime import datetime
from zipfile import ZipFile
import requests
import json
import io
import base64
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class WorkerThread(QThread):
    """Sertifikat yaratish uchun alohida thread"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    
    def __init__(self, data_list, output_format, sensorika_logo_url="", kwork_logo_url=""):
        super().__init__()
        self.data_list = data_list
        self.output_format = output_format
        self.sensorika_logo_url = sensorika_logo_url
        self.kwork_logo_url = kwork_logo_url
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, 'output')
    
    def find_libreoffice_path(self):
        """LibreOffice (soffice) dasturining yo'lini avtomatik topadi."""
        if platform.system() == "Windows":
            possible_paths = [
                "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
                "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        elif platform.system() == "Linux":
            return "libreoffice"
        elif platform.system() == "Darwin":  # macOS
            return "/Applications/LibreOffice.app/Contents/MacOS/soffice"
        return None
    
    def create_qr_code(self, text, logo_url, save_path=None, qr_type="sensorika"):
        """QR kod yaratish - qrcode-monkey API orqali"""
        url = "https://api.qrcode-monkey.com/qr/custom"
        
        if qr_type == "kwork":
            config = {
                "body": "square",
                "eye": "frame0", 
                "eyeBall": "ball0",
                "erf1": [],
                "erf2": [],
                "erf3": [],
                "brf1": [],
                "brf2": [],
                "brf3": [],
                "bodyColor": "#000000",
                "bgColor": "#FFFFFF",
                "eye1Color": "#000000",
                "eye2Color": "#000000",
                "eye3Color": "#000000",
                "eyeBall1Color": "#666666",
                "eyeBall2Color": "#666666",
                "eyeBall3Color": "#666666",
                "gradientColor1": "#000000",
                "gradientColor2": "#333333",
                "gradientType": "linear",
                "gradientOnEyes": False,
                "logo": logo_url if logo_url else "",
                "logoMode": "clean"
            }
        else:  # sensorika
            config = {
                "body": "circle",
                "eye": "frame13", 
                "eyeBall": "ball14",
                "erf1": [],
                "erf2": [],
                "erf3": [],
                "brf1": [],
                "brf2": [],
                "brf3": [],
                "bodyColor": "#000000",
                "bgColor": "#FFFFFF",
                "eye1Color": "#000000",
                "eye2Color": "#000000",
                "eye3Color": "#000000",
                "eyeBall1Color": "#666666",
                "eyeBall2Color": "#666666",
                "eyeBall3Color": "#666666",
                "gradientColor1": "#000000",
                "gradientColor2": "#333333",
                "gradientType": "radial",
                "gradientOnEyes": False,
                "logo": logo_url if logo_url else "",
                "logoMode": "clean"
            }
        
        payload = {
            "data": text,
            "config": config,
            "size": 1000,
            "download": "imageUrl",
            "file": "png"
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if "imageUrl" in response_data:
                    image_url = "https:" + response_data["imageUrl"]
                    image_response = requests.get(image_url, timeout=30)
                    
                    if image_response.status_code == 200:
                        if save_path:
                            with open(save_path, 'wb') as f:
                                f.write(image_response.content)
                        return {"success": True}
                    
            return {"success": False, "error": "API xatosi"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def replace_placeholders(self, presentation, replacements):
        """Prezentatsiyadagi belgilangan matnlarni almashtiradi."""
        for slide in presentation.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            for key, value in replacements.items():
                                if key in run.text:
                                    run.text = run.text.replace(key, str(value))
    
    def convert_to_format(self, input_pptx, output_folder, file_format):
        """PPTX faylni PDF yoki PNG ga o'tkazadi."""
        if file_format == 'pptx':
            return
        
        libreoffice_path = self.find_libreoffice_path()
        if not libreoffice_path:
            raise FileNotFoundError("LibreOffice o'rnatilmagan")
        
        cmd = [
            libreoffice_path,
            '--headless',
            '--convert-to', file_format,
            '--outdir', output_folder,
            input_pptx
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    def run(self):
        """Sertifikatlarni generatsiya qiladi."""
        try:
            # Eski fayllarni tozalash
            if os.path.exists(self.output_dir):
                shutil.rmtree(self.output_dir)
            os.makedirs(self.output_dir)
            
            generated_files = []
            total = len(self.data_list)
            
            for i, data in enumerate(self.data_list):
                # Progress yuborish
                progress = int(((i + 1) / total) * 100)
                self.progress.emit(progress, f"{i + 1}/{total} - {data['fullname']} yaratilmoqda...")
                
                # Fayl nomini yaratish
                current_date = datetime.now().strftime("%Y-%m-%d")
                safe_fullname = "".join(c for c in data['fullname'] if c.isalnum() or c in " _-").rstrip()
                safe_course = "".join(c for c in data['course'] if c.isalnum() or c in " _-").rstrip()
                base_filename = f"{safe_fullname}_{safe_course}_{current_date}"

                # QR kodlar uchun fayllar
                student_qr_path = os.path.join(self.output_dir, f"student_qr_{i}.png")
                kwork_qr_path = os.path.join(self.output_dir, f"kwork_qr_{i}.png")
                
                # Sensorika QR kodi (student_url)
                self.create_qr_code(data['student_url'], self.sensorika_logo_url, student_qr_path, "sensorika")
                
                # Kwork QR kodi (kwork_profile)
                self.create_qr_code(data['kwork_profile'], self.kwork_logo_url, kwork_qr_path, "kwork")

                # Prezentatsiyani ochish
                template_path = os.path.join(self.base_dir, 'demo.pptx')
                if not os.path.exists(template_path):
                    raise FileNotFoundError(f"Shablon fayl topilmadi: {template_path}")
                
                prs = Presentation(template_path)
                slide = prs.slides[0]

                # Matnlarni almashtirish
                replacements = {
                    "{{FULLNAME}}": data['fullname'],
                    "{{COURSE}}": data['course'],
                    "{{STARTDATE}}": data['startdate'],
                    "{{ENDDATE}}": data['enddate'],
                    "{{CERT_ID}}": data['certid'],
                    "{{STUDENT_URL}}": data['student_url'],
                    "{{KWORK}}": data['kwork_profile']
                }
                self.replace_placeholders(prs, replacements)
                
                # QR kodlarni qo'shish
                slide.shapes.add_picture(student_qr_path, Inches(5.0), Inches(5.5), width=Inches(1.0))
                slide.shapes.add_picture(kwork_qr_path, Inches(6.5), Inches(5.5), width=Inches(1.0))

                # PPTX saqlash
                temp_pptx_path = os.path.join(self.output_dir, f"{base_filename}.pptx")
                prs.save(temp_pptx_path)

                # Format o'zgartirish
                if self.output_format != 'pptx':
                    self.convert_to_format(temp_pptx_path, self.output_dir, self.output_format)
                    output_filename = f"{base_filename}.{self.output_format}"
                    os.remove(temp_pptx_path)
                else:
                    output_filename = f"{base_filename}.pptx"
                
                generated_files.append(output_filename)

                # Vaqtinchalik fayllarni o'chirish
                if os.path.exists(student_qr_path):
                    os.remove(student_qr_path)
                if os.path.exists(kwork_qr_path):
                    os.remove(kwork_qr_path)

            # Zip yaratish (ko'p fayllar bo'lsa)
            if len(generated_files) > 1:
                current_date = datetime.now().strftime("%Y-%m-%d")
                zip_filename = f"sertifikatlar_{current_date}.zip"
                zip_path = os.path.join(self.output_dir, zip_filename)
                
                with ZipFile(zip_path, 'w') as zipf:
                    for file in generated_files:
                        zipf.write(os.path.join(self.output_dir, file), arcname=file)
                
                self.finished.emit({'status': 'success', 'path': zip_path, 'filename': zip_filename})
            else:
                self.finished.emit({
                    'status': 'success', 
                    'path': os.path.join(self.output_dir, generated_files[0]), 
                    'filename': generated_files[0]
                })

        except Exception as e:
            self.finished.emit({'status': 'error', 'message': str(e)})


class CertificateGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.base_dir, 'output')
        self.excel_data = []
        
        # Kerakli papkalarni yaratish
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """UI elementlarini yaratish"""
        self.setWindowTitle("Sertifikat Generator")
        self.setGeometry(100, 100, 1400, 900)  # Increased window size
        self.setMinimumSize(1000, 700)  # Set minimum size
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #e5e5e5;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 12px 24px;
                margin-right: 2px;
                border: 1px solid #e5e5e5;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #000000;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #e5e5e5;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #000000;
            }
            QPushButton {
                background-color: #000000;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLabel {
                font-weight: 500;
                margin-bottom: 8px;
            }
            QProgressBar {
                border: 1px solid #e5e5e5;
                border-radius: 4px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #000000;
                border-radius: 3px;
            }
            QRadioButton {
                font-size: 14px;
                spacing: 8px;
            }
            QRadioButton::indicator:checked {
                background-color: #000000;
                border: 2px solid #000000;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                padding-top: 15px;
                margin-top: 10px;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollArea {
                border: 1px solid #e5e5e5;
                border-radius: 4px;
                background-color: #fafafa;
            }
            QTabWidget > QWidget {
                background-color: white;
            }
        """)
        
        # Central widget with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("Sertifikat Generator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 10px;")
        
        subtitle = QLabel("Professional sertifikatlar yaratish tizimi")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #666666; margin-bottom: 30px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Single Certificate Tab
        self.single_tab = self.create_single_tab()
        self.tabs.addTab(self.single_tab, "Bitta sertifikat")
        
        # Batch Certificate Tab
        self.batch_tab = self.create_batch_tab()
        self.tabs.addTab(self.batch_tab, "Ko'plab sertifikat")
        
        # Settings Tab
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "Sozlamalar")
        
        main_layout.addWidget(self.tabs)
        
        # Format Selection
        self.format_group = self.create_format_group()
        main_layout.addWidget(self.format_group)
        
        # Progress Section
        self.progress_group = self.create_progress_group()
        self.progress_group.setVisible(False)
        main_layout.addWidget(self.progress_group)
        
        # Generate Button
        self.generate_btn = QPushButton("Sertifikat yaratish")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.generate_btn.clicked.connect(self.generate_certificates)
        main_layout.addWidget(self.generate_btn)
        
        # Result Section
        self.result_group = self.create_result_group()
        self.result_group.setVisible(False)
        main_layout.addWidget(self.result_group)
        
        # Tab change event
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Window resize event
        self.resizeEvent = self.on_resize_event
        
    def create_single_tab(self):
        """Bitta sertifikat tab'ini yaratish"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        # Form fields in a grid layout
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        grid_layout.setColumnStretch(1, 1)  # Make second column stretchable
        
        # Form fields
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Sevinova Jasmina")
        grid_layout.addWidget(QLabel("To'liq ismi (F.I.Sh):"), 0, 0)
        grid_layout.addWidget(self.fullname_input, 0, 1)
        
        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("Kompyuter savodxonligi")
        grid_layout.addWidget(QLabel("Kurs nomi:"), 1, 0)
        grid_layout.addWidget(self.course_input, 1, 1)
        
        self.startdate_input = QDateEdit()
        self.startdate_input.setDate(QDate.currentDate().addMonths(-2))
        self.startdate_input.setCalendarPopup(True)
        grid_layout.addWidget(QLabel("Boshlangan sana:"), 2, 0)
        grid_layout.addWidget(self.startdate_input, 2, 1)
        
        self.enddate_input = QDateEdit()
        self.enddate_input.setDate(QDate.currentDate())
        self.enddate_input.setCalendarPopup(True)
        grid_layout.addWidget(QLabel("Yakunlangan sana:"), 3, 0)
        grid_layout.addWidget(self.enddate_input, 3, 1)
        
        self.certid_input = QLineEdit()
        self.certid_input.setPlaceholderText("CERT-2212")
        grid_layout.addWidget(QLabel("Sertifikat ID:"), 4, 0)
        grid_layout.addWidget(self.certid_input, 4, 1)
        
        self.student_url_input = QLineEdit()
        self.student_url_input.setPlaceholderText("https://sensorika.uz/students/...")
        grid_layout.addWidget(QLabel("Student URL (Sensorika):"), 5, 0)
        grid_layout.addWidget(self.student_url_input, 5, 1)
        
        self.kwork_profile_input = QLineEdit()
        self.kwork_profile_input.setPlaceholderText("https://kwork.ru/user/smart_admin")
        grid_layout.addWidget(QLabel("Kwork Profile URL:"), 6, 0)
        grid_layout.addWidget(self.kwork_profile_input, 6, 1)
        
        form_layout.addLayout(grid_layout)
        form_layout.addStretch()
        
        scroll_area.setWidget(form_widget)
        layout.addWidget(scroll_area)
        
        return widget
    
    def create_batch_tab(self):
        """Ko'plab sertifikat tab'ini yaratish"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Description
        desc_label = QLabel("Ko'plab sertifikat yaratish uchun Excel faylga ma'lumotlarni kiriting")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 16px; color: #666666; margin-bottom: 20px;")
        content_layout.addWidget(desc_label)
        
        # Template download button
        self.template_btn = QPushButton("Excel shablonini yuklab olish")
        self.template_btn.clicked.connect(self.create_excel_template)
        content_layout.addWidget(self.template_btn)
        
        # File selection area
        file_area = QFrame()
        file_area.setFrameStyle(QFrame.StyledPanel)
        file_area.setStyleSheet("""
            QFrame {
                border: 2px dashed #cccccc;
                border-radius: 8px;
                padding: 40px;
                background-color: #fafafa;
            }
        """)
        file_layout = QVBoxLayout(file_area)
        
        file_icon = QLabel("📁")
        file_icon.setAlignment(Qt.AlignCenter)
        file_icon.setStyleSheet("font-size: 48px;")
        file_layout.addWidget(file_icon)
        
        self.file_btn = QPushButton("Excel faylni tanlash uchun bosing")
        self.file_btn.clicked.connect(self.select_excel_file)
        file_layout.addWidget(self.file_btn)
        
        file_info = QLabel(".xlsx formatdagi fayllar qo'llab-quvvatlanadi")
        file_info.setAlignment(Qt.AlignCenter)
        file_info.setStyleSheet("color: #666666; margin-top: 10px;")
        file_layout.addWidget(file_info)
        
        content_layout.addWidget(file_area)
        
        # File info
        self.file_info_label = QLabel()
        self.file_info_label.setVisible(False)
        self.file_info_label.setStyleSheet("""
            background-color: #f0f8f0;
            padding: 15px;
            border: 1px solid #d4edda;
            border-radius: 4px;
            color: #155724;
        """)
        content_layout.addWidget(self.file_info_label)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        return widget
    
    def create_settings_tab(self):
        """Sozlamalar tab'ini yaratish"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Sozlamalar")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 30px;")
        content_layout.addWidget(title)
        
        # QR Logo Settings
        qr_group = QGroupBox("QR Kod Logo Sozlamalari")
        qr_layout = QVBoxLayout(qr_group)
        qr_layout.setSpacing(15)
        
        self.sensorika_logo_input = QLineEdit()
        self.sensorika_logo_input.setPlaceholderText("Sensorika logo URL")
        qr_layout.addWidget(QLabel("Sensorika Logo URL:"))
        qr_layout.addWidget(self.sensorika_logo_input)
        
        self.kwork_logo_input = QLineEdit()
        self.kwork_logo_input.setPlaceholderText("Kwork logo URL")
        qr_layout.addWidget(QLabel("Kwork Logo URL:"))
        qr_layout.addWidget(self.kwork_logo_input)
        
        content_layout.addWidget(qr_group)
        
        # Default Format Settings
        format_group = QGroupBox("Standart Chiqish Formati")
        format_layout = QVBoxLayout(format_group)
        format_layout.setSpacing(10)
        
        self.default_format_group = QButtonGroup()
        self.pdf_default_radio = QRadioButton("PDF")
        self.png_default_radio = QRadioButton("PNG")
        self.pptx_default_radio = QRadioButton("PPTX")
        
        self.pdf_default_radio.setChecked(True)
        
        self.default_format_group.addButton(self.pdf_default_radio)
        self.default_format_group.addButton(self.png_default_radio)
        self.default_format_group.addButton(self.pptx_default_radio)
        
        format_layout.addWidget(self.pdf_default_radio)
        format_layout.addWidget(self.png_default_radio)
        format_layout.addWidget(self.pptx_default_radio)
        
        content_layout.addWidget(format_group)
        
        # Save button
        self.save_settings_btn = QPushButton("Sozlamalarni saqlash")
        self.save_settings_btn.clicked.connect(self.save_settings)
        content_layout.addWidget(self.save_settings_btn)
        
        # Status message
        self.settings_status = QLabel()
        self.settings_status.setAlignment(Qt.AlignCenter)
        self.settings_status.setVisible(False)
        self.settings_status.setStyleSheet("color: green; font-weight: bold; padding: 10px;")
        content_layout.addWidget(self.settings_status)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        return widget
    
    def create_format_group(self):
        """Format tanlash guruhi"""
        group = QGroupBox("Chiqish formati")
        layout = QHBoxLayout(group)
        layout.setSpacing(20)
        
        self.format_group_buttons = QButtonGroup()
        self.pdf_radio = QRadioButton("PDF")
        self.png_radio = QRadioButton("PNG")
        self.pptx_radio = QRadioButton("PPTX")
        
        self.pdf_radio.setChecked(True)
        
        self.format_group_buttons.addButton(self.pdf_radio)
        self.format_group_buttons.addButton(self.png_radio)
        self.format_group_buttons.addButton(self.pptx_radio)
        
        layout.addWidget(self.pdf_radio)
        layout.addWidget(self.png_radio)
        layout.addWidget(self.pptx_radio)
        layout.addStretch()
        
        return group
    
    def create_progress_group(self):
        """Progress guruhi"""
        group = QGroupBox("Jarayon")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.status_label)
        
        return group
    
    def create_result_group(self):
        """Natija guruhi"""
        group = QGroupBox("Natija")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        
        success_label = QLabel("Muvaffaqiyat!")
        success_label.setAlignment(Qt.AlignCenter)
        success_label.setStyleSheet("font-size: 20px; font-weight: bold; color: green; margin-bottom: 10px;")
        layout.addWidget(success_label)
        
        desc_label = QLabel("Sertifikatlar muvaffaqiyatli yaratildi")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #666666; margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        self.open_folder_btn = QPushButton("Papkani ochish")
        self.open_folder_btn.clicked.connect(self.open_output_folder)
        layout.addWidget(self.open_folder_btn)
        
        return group
    
    def on_tab_changed(self, index):
        """Tab o'zgartirilganda chaqiriladigan funksiya"""
        if index == 2:  # Settings tab
            self.format_group.setVisible(False)
            self.generate_btn.setVisible(False)
        else:
            self.format_group.setVisible(True)
            self.generate_btn.setVisible(True)
    
    def on_resize_event(self, event):
        """Oyna o'lchami o'zgartirilganda chaqiriladigan funksiya"""
        super().resizeEvent(event)
        # Ensure minimum size is maintained
        if self.width() < 1000:
            self.resize(1000, self.height())
        if self.height() < 700:
            self.resize(self.width(), 700)
    
    def select_excel_file(self):
        """Excel fayl tanlash"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel faylni tanlang",
            "",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                df = pd.read_excel(file_path)
                df = df.astype(str)
                df.fillna("", inplace=True)
                
                self.excel_data = df.to_dict('records')
                
                # Show file info
                file_name = os.path.basename(file_path)
                self.file_info_label.setText(f"Tanlangan fayl: {file_name}\nMa'lumotlar soni: {len(self.excel_data)} ta yozuv")
                self.file_info_label.setVisible(True)
                
            except Exception as e:
                QMessageBox.critical(self, "Xato", f"Excel faylini o'qishda xatolik: {str(e)}")
    
    def create_excel_template(self):
        """Excel shablon yaratish"""
        try:
            data = {
                'fullname': ['Sevinova Jasmina'],
                'course': ['Kompyuter savodxonligi'],
                'startdate': ['2024-01-10'],
                'enddate': ['2024-03-10'],
                'certid': ['CERT-2212'],
                'student_url': ['https://sensorika.uz/students/kompyuter-savodxonligi/2212-sevinova-jasmina.html'],
                'kwork_profile': ['https://kwork.ru/user/smart_admin']
            }
            df = pd.DataFrame(data)
            template_path = os.path.join(self.output_dir, 'sertifikat_template.xlsx')
            df.to_excel(template_path, index=False)
            
            QMessageBox.information(self, "Muvaffaqiyat", f"Excel shablon yaratildi:\n{template_path}")
            self.open_output_folder()
            
        except Exception as e:
            QMessageBox.critical(self, "Xato", f"Shablon yaratishda xatolik: {str(e)}")
    
    def load_settings(self):
        """Sozlamalarni yuklash"""
        settings = QSettings("SertifikatGenerator", "Settings")
        
        # Default values
        sensorika_logo = settings.value("sensorikaLogo", 
            "https://sensorika.uz/uploads/posts/2021-06/1624529825_1522820181_photo233710126177036760.jpg")
        kwork_logo = settings.value("kworkLogo", 
            "https://habrastorage.org/getpro/moikrug/uploads/company/100/005/814/4/logo/big_95d7025a918905157a814ccc1168fc08.jpg")
        default_format = settings.value("defaultFormat", "pdf")
        
        # Apply to settings tab
        self.sensorika_logo_input.setText(sensorika_logo)
        self.kwork_logo_input.setText(kwork_logo)
        
        if default_format == "pdf":
            self.pdf_default_radio.setChecked(True)
            self.pdf_radio.setChecked(True)
        elif default_format == "png":
            self.png_default_radio.setChecked(True)
            self.png_radio.setChecked(True)
        elif default_format == "pptx":
            self.pptx_default_radio.setChecked(True)
            self.pptx_radio.setChecked(True)
    
    def save_settings(self):
        """Sozlamalarni saqlash"""
        settings = QSettings("SertifikatGenerator", "Settings")
        
        settings.setValue("sensorikaLogo", self.sensorika_logo_input.text().strip())
        settings.setValue("kworkLogo", self.kwork_logo_input.text().strip())
        
        if self.pdf_default_radio.isChecked():
            default_format = "pdf"
            self.pdf_radio.setChecked(True)
        elif self.png_default_radio.isChecked():
            default_format = "png"
            self.png_radio.setChecked(True)
        elif self.pptx_default_radio.isChecked():
            default_format = "pptx"
            self.pptx_radio.setChecked(True)
        
        settings.setValue("defaultFormat", default_format)
        
        # Show success message
        self.settings_status.setText("Sozlamalar muvaffaqiyatli saqlandi!")
        self.settings_status.setVisible(True)
        
        # Hide message after 3 seconds
        QTimer.singleShot(3000, lambda: self.settings_status.setVisible(False))
    
    def get_selected_format(self):
        """Tanlangan formatni olish"""
        if self.pdf_radio.isChecked():
            return "pdf"
        elif self.png_radio.isChecked():
            return "png"
        elif self.pptx_radio.isChecked():
            return "pptx"
        return "pdf"
    
    def generate_certificates(self):
        """Sertifikatlarni generatsiya qilish"""
        current_tab = self.tabs.currentIndex()
        data_list = []
        
        # Get settings
        settings = QSettings("SertifikatGenerator", "Settings")
        sensorika_logo = settings.value("sensorikaLogo", "")
        kwork_logo = settings.value("kworkLogo", "")
        
        if current_tab == 0:  # Single certificate
            # Validate single form
            if not all([
                self.fullname_input.text().strip(),
                self.course_input.text().strip(),
                self.certid_input.text().strip(),
                self.student_url_input.text().strip(),
                self.kwork_profile_input.text().strip()
            ]):
                QMessageBox.warning(self, "Xato", "Iltimos, barcha maydonlarni to'ldiring")
                return
            
            data = {
                'fullname': self.fullname_input.text().strip(),
                'course': self.course_input.text().strip(),
                'startdate': self.startdate_input.date().toString("yyyy-MM-dd"),
                'enddate': self.enddate_input.date().toString("yyyy-MM-dd"),
                'certid': self.certid_input.text().strip(),
                'student_url': self.student_url_input.text().strip(),
                'kwork_profile': self.kwork_profile_input.text().strip()
            }
            data_list = [data]
            
        elif current_tab == 1:  # Batch certificates
            if not self.excel_data:
                QMessageBox.warning(self, "Xato", "Excel fayl tanlanmagan yoki ma'lumot yo'q")
                return
            data_list = self.excel_data
        
        if not data_list:
            QMessageBox.warning(self, "Xato", "Ma'lumot kiritilmagan")
            return
        
        # Check template file
        template_path = os.path.join(self.base_dir, 'demo.pptx')
        if not os.path.exists(template_path):
            QMessageBox.critical(
                self, 
                "Xato", 
                f"Shablon fayl topilmadi: {template_path}\n\nIltimos, demo.pptx faylini dastur papkasiga joylashtiring."
            )
            return
        
        # Start generation
        output_format = self.get_selected_format()
        
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Yaratilmoqda...")
        self.progress_group.setVisible(True)
        self.result_group.setVisible(False)
        
        # Create worker thread
        self.worker = WorkerThread(data_list, output_format, sensorika_logo, kwork_logo)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.generation_finished)
        self.worker.start()
    
    def update_progress(self, progress, message):
        """Progress yangilash"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
    
    def generation_finished(self, result):
        """Generatsiya tugallanganda"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Sertifikat yaratish")
        
        if result['status'] == 'success':
            self.result_group.setVisible(True)
            # Scroll to result
            QTimer.singleShot(100, self.scroll_to_result)
        else:
            QMessageBox.critical(self, "Xato", f"Xatolik yuz berdi:\n{result['message']}")
        
        # Hide progress after 2 seconds
        QTimer.singleShot(2000, lambda: self.progress_group.setVisible(False))
    
    def scroll_to_result(self):
        """Natijaga scroll qilish"""
        # Scroll to the result section
        scroll_area = self.centralWidget()
        if isinstance(scroll_area, QScrollArea):
            # Find the result group widget and scroll to it
            central_widget = scroll_area.widget()
            if central_widget:
                # Get the position of the result group
                result_pos = self.result_group.mapTo(central_widget, QPoint(0, 0))
                scroll_area.verticalScrollBar().setValue(result_pos.y())
    
    def open_output_folder(self):
        """Output papkasini ochish"""
        try:
            if platform.system() == 'Windows':
                os.startfile(self.output_dir)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', self.output_dir])
            else:
                subprocess.run(['xdg-open', self.output_dir])
        except Exception as e:
            QMessageBox.warning(self, "Xato", f"Papkani ochib bo'lmadi: {str(e)}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sertifikat Generator")
    app.setOrganizationName("SertifikatGenerator")
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("icon.ico"))  # Add icon file if available
    except:
        pass
    
    window = CertificateGenerator()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()