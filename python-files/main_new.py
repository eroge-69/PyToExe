import sys
import os
import cv2
import numpy as np
import mediapipe as mp
import smtplib
import threading
import requests
import shutil
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QMessageBox, QListWidget,
    QListWidgetItem, QStackedWidget, QSizePolicy, QDialog, QFormLayout,
    QScrollArea, QGridLayout, QFrame, QComboBox
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QIcon, QTransform, QFont, QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect, QSize
from PIL import Image, ImageDraw, ImageFont

# ---------------------------
# KONFIGURASI SMTP EMAIL
# ---------------------------
SMTP_SERVER = os.environ.get("PHOTOMAIL_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("PHOTOMAIL_PORT", 587))
SMTP_USERNAME = os.environ.get("PHOTOMAIL_USER", "")
SMTP_PASSWORD = os.environ.get("PHOTOMAIL_PASS", "")

def send_email_with_attachment(sender_email, sender_password, receiver_email, subject, body, attachment_path):
    """Kirim email dengan satu attachment (tetap dipertahankan untuk kompatibilitas)"""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment_path)}"')
            msg.attach(part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

def send_email_with_attachments(sender_email, sender_password, receiver_email, subject, body, attachment_paths):
    """Kirim email dengan banyak attachment (fitur baru)"""
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        for path in attachment_paths:
            try:
                with open(path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
                    msg.attach(part)
            except Exception:
                # Lewati file yang gagal dibuka agar pengiriman tetap jalan
                pass

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)

# ---------------------------
# HELPER FUNCTIONS UNTUK DETEKSI SLOT TRANSPARAN
# ---------------------------
def detect_transparent_slots_from_rgba(layout_rgba):
    """Mendeteksi area transparan dalam layout untuk penempatan foto"""
    alpha = layout_rgba[:, :, 3]
    mask = (alpha == 0).astype(np.uint8) * 255
    if mask.sum() == 0:
        return []
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bboxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w < 10 or h < 10:
            continue
        bboxes.append((x, y, w, h))
    bboxes.sort(key=lambda b: (b[1]//10, b[0]))
    return bboxes

# --------------------------------
# FUNGSI PERBAIKAN MASK SEGMENTASI
# --------------------------------
def refine_mask(raw_mask, kernel_size=3, blur_ksize=8):
    """Memperbaiki mask segmentasi untuk hasil yang lebih halus"""
    m = np.clip(raw_mask, 0.0, 1.0)
    m_u8 = (m * 255).astype(np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    m_open = cv2.morphologyEx(m_u8, cv2.MORPH_OPEN, kernel)
    m_close = cv2.morphologyEx(m_open, cv2.MORPH_CLOSE, kernel)

    blur = cv2.GaussianBlur(m_close, (blur_ksize, blur_ksize), 0)

    alpha = blur.astype(np.float32) / 255.0
    alpha = np.expand_dims(alpha, axis=2)  # HxWx1
    return alpha

def composite_foreground_background(fg_bgr, bg_bgr, alpha):
    """Menggabungkan foreground dan background dengan alpha blending"""
    fg = fg_bgr.astype(np.float32)
    bg = bg_bgr.astype(np.float32)
    out = alpha * fg + (1.0 - alpha) * bg
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------------------------
# KELAS UTAMA PHOTOBOOTH
# ---------------------------
class PhotoBooth(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Photobooth BMKN ")
        self.setGeometry(100, 50, 1400, 900)

        # Tema terang untuk UI
        self.setStyleSheet("""
            QWidget { 
                background-color: #FFFFFF; 
                color: #333333; 
                font-family: "Segoe UI", Roboto, Arial; 
            }
            QLabel { color: #333333; }
            QPushButton { 
                background-color: #007ACC; 
                border: none; 
                padding: 12px 20px; 
                border-radius: 8px; 
                color: white; 
                font-weight: 600; 
                font-size: 14px;
            }
            QPushButton:hover { background-color: #005A9E; }
            QPushButton:pressed { background-color: #004578; }
            QLineEdit { 
                background: #F8F9FA; 
                border: 2px solid #E1E5E9; 
                padding: 12px; 
                border-radius: 8px; 
                color: #333; 
                font-size: 16px; 
            }
            QLineEdit:focus { border-color: #007ACC; }
            QListWidget { 
                background-color: #F8F9FA; 
                border: 2px solid #E1E5E9; 
                border-radius: 8px;
                padding: 8px; 
            }
            QLabel#videoLabel { 
                border: 4px solid #007ACC; 
                border-radius: 12px; 
                background-color: #000000;
            }
            QLabel#editorLabel { 
                border: 4px solid #007ACC; 
                border-radius: 12px; 
                background-color: #000000;
            }
            QListWidget::item { 
                padding: 8px; 
                margin: 4px;
                border-radius: 6px;
            }
            QListWidget::item:selected { 
                background-color: #007ACC; 
                color: white;
            }
            QListWidget::item:hover { 
                background-color: #E3F2FD; 
            }
            QFrame#panelFrame {
                background-color: #F8F9FA;
                border: 2px solid #E1E5E9;
                border-radius: 10px;
                padding: 10px;
            }
            QLabel#panelHeader {
                font-size: 16px;
                font-weight: bold;
                color: #007ACC;
                padding: 5px;
            }
        """)

        # Variabel state aplikasi
        self.family_name = ""
        self.email_address = ""  # input email opsional
        self.backgrounds = []
        self.selected_background = None
        self.bg_selected_index = None

        self.layouts = []
        self.selected_layout = None
        self.layout_selected_index = None

        self.photo = None
        self.raw_photos = []
        self.stickers = [] 
        self.sticker_files = []
        self.sticker_selected_index = None
        self.dragging_sticker_index = None
        self.resizing_sticker_index = None
        self.resize_corner = None
        self.drag_offset = QPoint()

        # Data sesi foto
        self.session_photos = []
        self.photo_counter = 1

        # Konfigurasi kamera - resolusi 16:9
        self.cap = None
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.update_frame)
        self.preview_interval = 30
        
        self.cam_width = 1280
        self.cam_height = 720
        
        # Canvas editor 960x540 (16:9)
        self.display_width = 960
        self.display_height = 540

        # Sesi timer (5 menit)
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.session_timeout)
        self.session_time_limit = 5 * 60 * 1000

        # Variabel untuk sesi capture dan slot
        self.capturing = False
        self.active_layout_rgba = None
        self.active_composed_rgba = None
        self.active_slots = []
        self.current_slot_index = 0
        self.countdown_active = False
        self.countdown_value = 0
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._on_countdown_tick)
        self.countdown_slot_rect = None
        self._slot_capture_result = None

        # Efek flash
        self.flash_active = False

        # Inisialisasi MediaPipe untuk segmentasi
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

        # State pilihan kamera
        self.camera_mode = "internal"  # 'internal' | 'external' | 'ip'
        self.ip_camera_url = ""

        # Setup UI
        self.stack = QStackedWidget()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stack)
        
        self.init_family_name_page()
        self.init_camera_page()
        self.init_editor_page()
        self.init_contest_page()

    # --- HALAMAN 1: INPUT NAMA FAMILY DAN EMAIL ---
    def init_family_name_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        form_container = QWidget()
        form_container.setFixedWidth(600)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_container.setStyleSheet("""
            QWidget { 
                background: qlineargradient(spread:pad, x1:0,y1:0,x2:1,y2:1, stop:0 #F8F9FA, stop:1 #E3F2FD);
                border: 3px solid #007ACC; 
                border-radius: 15px; 
            }
        """)

        title = QLabel("Photobooth BMKN")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #007ACC; margin-bottom: 10px;")
        form_layout.addWidget(title)

        subtitle = QLabel("Masukkan data untuk memulai sesi photobooth")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #666666; margin-bottom: 20px;")
        form_layout.addWidget(subtitle)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nama Family (wajib diisi)")
        self.name_input.setFixedHeight(50)
        self.name_input.returnPressed.connect(self.start_session)
        form_layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (opsional)")
        self.email_input.setFixedHeight(50)
        self.email_input.returnPressed.connect(self.start_session)
        form_layout.addWidget(self.email_input)

        start_btn = QPushButton("Mulai Sesi Photobooth")
        start_btn.setFixedHeight(50)
        start_btn.setStyleSheet("font-weight: bold; color: #007ACC;")
        start_btn.clicked.connect(self.start_session)
        form_layout.addWidget(start_btn)

        timer_info = QLabel("⏰ Waktu sesi: 5 menit per family")
        timer_info.setAlignment(Qt.AlignCenter)
        timer_info.setStyleSheet("font-size: 12px; color: #888888; margin-top: 10px;")
        form_layout.addWidget(timer_info)

        layout.addStretch()
        layout.addWidget(form_container, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.stack.addWidget(page)

    # --- HALAMAN 2: KAMERA + PILIHAN BACKGROUND & LAYOUT ---
    def init_camera_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Panel kiri - Background
        bg_panel = self.create_selection_panel("Background", 180)
        self.bg_list = bg_panel.findChild(QListWidget)
        main_layout.addWidget(bg_panel)

        # Bagian tengah - Preview kamera
        center_layout = QVBoxLayout()
        
        info_layout = QHBoxLayout()
        self.family_label = QLabel("")
        self.family_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007ACC;")
        self.timer_label = QLabel("")
        self.timer_label.setStyleSheet("font-size: 16px; color: #666666;")
        self.timer_label.setAlignment(Qt.AlignRight)
        info_layout.addWidget(self.family_label)
        info_layout.addStretch()
        info_layout.addWidget(self.timer_label)
        center_layout.addLayout(info_layout)

        # Pilihan kamera
        cam_select_row = QHBoxLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Kamera Internal (0)", "Kamera Eksternal (1)", "IP Webcam URL"])
        self.camera_combo.currentIndexChanged.connect(self.on_camera_source_changed)
        self.ip_url_input = QLineEdit()
        self.ip_url_input.setPlaceholderText("http://IP:8080/video")
        self.ip_url_input.setFixedWidth(300)
        self.ip_url_input.setEnabled(False)
        self.connect_cam_btn = QPushButton("Sambungkan Kamera")
        self.connect_cam_btn.clicked.connect(self.apply_camera_selection)
        self.camera_status_label = QLabel("")
        self.camera_status_label.setStyleSheet("font-size: 12px; color: #666;")
        cam_select_row.addWidget(self.camera_combo)
        cam_select_row.addWidget(self.ip_url_input)
        cam_select_row.addWidget(self.connect_cam_btn)
        cam_select_row.addStretch()
        center_layout.addLayout(cam_select_row)

        self.video_label = QLabel(objectName="videoLabel")
        self.video_label.setFixedSize(self.display_width, self.display_height)
        center_layout.addWidget(self.video_label, alignment=Qt.AlignCenter)

        controls = QHBoxLayout()
        self.capture_btn = QPushButton("Ambil Foto")
        self.capture_btn.setFixedHeight(45)
        self.capture_btn.setFixedWidth(180)
        self.capture_btn.clicked.connect(self.capture_photo)
        
        self.status_label = QLabel("Pilih background dan layout, lalu ambil foto")
        self.status_label.setStyleSheet("color: #666666; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        controls.addWidget(self.capture_btn)
        controls.addStretch()
        controls.addWidget(self.status_label)
        controls.addStretch()
        
        center_layout.addLayout(controls)
        main_layout.addLayout(center_layout)

        # Panel kanan - Layout
        layout_panel = self.create_selection_panel("Layout", 180)
        self.layout_list = layout_panel.findChild(QListWidget)
        main_layout.addWidget(layout_panel)

        self.stack.addWidget(page)

    # --- HALAMAN 3: EDITOR FOTO + STICKER ---
    def init_editor_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        sticker_panel = self.create_selection_panel("Sticker", 180)
        self.sticker_list = sticker_panel.findChild(QListWidget)
        main_layout.addWidget(sticker_panel)

        center_layout = QVBoxLayout()
        
        editor_info = QHBoxLayout()
        self.editor_family_label = QLabel("")
        self.editor_family_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #007ACC;")
        self.editor_timer_label = QLabel("")
        self.editor_timer_label.setStyleSheet("font-size: 16px; color: #666666;")
        self.editor_timer_label.setAlignment(Qt.AlignRight)
        
        editor_info.addWidget(self.editor_family_label)
        editor_info.addStretch()
        editor_info.addWidget(self.editor_timer_label)
        center_layout.addLayout(editor_info)

        self.editor_label = QLabel(objectName="editorLabel")
        self.editor_label.setFixedSize(960, 540)
        self.editor_label.setMouseTracking(True)
        self.editor_label.mousePressEvent = self.editor_mousePressEvent
        self.editor_label.mouseMoveEvent = self.editor_mouseMoveEvent
        self.editor_label.mouseReleaseEvent = self.editor_mouseReleaseEvent
        self.editor_label.mouseDoubleClickEvent = self.editor_mouseDoubleClickEvent
        center_layout.addWidget(self.editor_label, alignment=Qt.AlignCenter)

        controls = QVBoxLayout()
        instructions = QLabel("Klik sticker untuk menambah • Drag untuk pindah • Resize di sudut • Double-click untuk hapus")
        instructions.setStyleSheet("color: #666666; font-size: 12px; margin: 10px;")
        instructions.setAlignment(Qt.AlignCenter)
        controls.addWidget(instructions)
        
        btn_layout = QHBoxLayout()
        retake_btn = QPushButton("Ambil Ulang Foto")
        retake_btn.setToolTip("Ulangi foto terakhir (tidak disimpan)")
        retake_btn.clicked.connect(self.retake_photo)
        
        take_more_btn = QPushButton("Ambil Lagi Foto")
        take_more_btn.setToolTip("Simpan foto ini dan ambil foto tambahan")
        take_more_btn.clicked.connect(self.take_more_photo)
        
        finish_btn = QPushButton("Selesai")
        finish_btn.setToolTip("Simpan foto dan lanjut ke halaman lomba")
        finish_btn.clicked.connect(self.finish_session)
        
        btn_layout.addWidget(retake_btn)
        btn_layout.addWidget(take_more_btn)
        btn_layout.addWidget(finish_btn)
        controls.addLayout(btn_layout)
        
        center_layout.addLayout(controls)
        main_layout.addLayout(center_layout)

        info_panel = QFrame()
        info_panel.setFrameStyle(QFrame.StyledPanel)
        info_panel.setFixedWidth(200)
        info_panel.setStyleSheet("QFrame { background-color: #F8F9FA; border: 2px solid #E1E5E9; border-radius: 10px; }")
        
        info_layout = QVBoxLayout(info_panel)
        
        info_header = QLabel("Info Sesi")
        info_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #007ACC; padding: 5px;")
        info_layout.addWidget(info_header)
        
        self.photo_count_label = QLabel("Foto ke: 1")
        self.photo_count_label.setStyleSheet("font-size: 14px; color: #333333; padding: 5px;")
        info_layout.addWidget(self.photo_count_label)
        
        self.total_photos_label = QLabel("Total foto: 0")
        self.total_photos_label.setStyleSheet("font-size: 14px; color: #333333; padding: 5px;")
        info_layout.addWidget(self.total_photos_label)
        
        info_layout.addStretch()
        main_layout.addWidget(info_panel)

        self.stack.addWidget(page)

    # --- HALAMAN 4: LOMBA DAN PILIHAN FOTO + KIRIM EMAIL ---
    def init_contest_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        contest_title = QLabel("Pilih Foto Favorit untuk Lomba")
        contest_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #007ACC;")
        
        self.contest_timer_label = QLabel("")
        self.contest_timer_label.setStyleSheet("font-size: 16px; color: #666666;")
        self.contest_timer_label.setAlignment(Qt.AlignRight)
        
        header_layout.addWidget(contest_title)
        header_layout.addStretch()
        header_layout.addWidget(self.contest_timer_label)
        layout.addLayout(header_layout)

        instructions = QLabel("Klik pada foto untuk memilih sebagai foto lomba favorit")
        instructions.setStyleSheet("font-size: 14px; color: #666666; margin: 10px 0;")
        layout.addWidget(instructions)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 2px solid #E1E5E9; border-radius: 10px; }")
        
        self.photo_gallery_widget = QWidget()
        self.photo_gallery_layout = QGridLayout(self.photo_gallery_widget)
        self.photo_gallery_layout.setSpacing(15)
        
        scroll_area.setWidget(self.photo_gallery_widget)
        layout.addWidget(scroll_area)

        # Bar kirim email
        email_bar = QHBoxLayout()
        self.email_send_input = QLineEdit()
        self.email_send_input.setPlaceholderText("Email tujuan (default dari halaman awal)")
        self.email_send_input.setFixedWidth(320)
        self.email_send_status = QLabel("")
        self.email_send_status.setStyleSheet("font-size: 12px; color: #666666;")
        send_email_btn = QPushButton("Kirim Semua Foto via Email")
        send_email_btn.clicked.connect(self.on_send_all_photos_clicked)
        email_bar.addWidget(self.email_send_input)
        email_bar.addWidget(send_email_btn)
        email_bar.addWidget(self.email_send_status)
        email_bar.addStretch()
        layout.addLayout(email_bar)

        contest_controls = QHBoxLayout()
        self.selected_photo_label = QLabel("Belum ada foto yang dipilih")
        self.selected_photo_label.setStyleSheet("font-size: 14px; color: #666666;")
        
        end_session_btn = QPushButton("Akhiri Session")
        end_session_btn.setToolTip("Akhiri sesi family dan kembali ke halaman utama")
        end_session_btn.clicked.connect(self.end_session)
        
        contest_controls.addWidget(self.selected_photo_label)
        contest_controls.addStretch()
        contest_controls.addWidget(end_session_btn)
        
        layout.addLayout(contest_controls)
        self.stack.addWidget(page)

    # --- HELPER: MEMBUAT PANEL SELEKSI ---
    def create_selection_panel(self, title, width):
        panel = QFrame(objectName="panelFrame")
        panel.setFixedWidth(width)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        
        header = QLabel(title, objectName="panelHeader")
        panel_layout.addWidget(header)
        
        list_widget = QListWidget()
        list_widget.setIconSize(QSize(80, 80))
        
        if title == "Background":
            list_widget.itemClicked.connect(self.toggle_background)
        elif title == "Layout":
            list_widget.itemClicked.connect(self.toggle_layout)
        elif title == "Sticker":
            list_widget.itemClicked.connect(self.add_sticker)
            
        panel_layout.addWidget(list_widget)
        
        if title == "Background":
            url_btn = QPushButton("Tambah dari URL")
            url_btn.setFixedHeight(35)
            url_btn.clicked.connect(self.show_input_dialog)
            panel_layout.addWidget(url_btn)
        
        return panel

    # --- MANAJEMEN SESI ---
    def start_session(self):
        self.family_name = self.name_input.text().strip()
        if not self.family_name:
            QMessageBox.warning(self, "Peringatan", "Nama family harus diisi!")
            return

        self.email_address = self.email_input.text().strip()

        # Reset data sesi
        self.session_photos = []
        self.raw_photos = []
        self.photo_counter = 1
        
        # Direktori output
        self.family_output_dir = os.path.join("output", self.family_name)
        os.makedirs(self.family_output_dir, exist_ok=True)
        
        # Load resource
        self.load_backgrounds()
        self.load_layouts()
        self.load_stickers()

        # Inisialisasi kamera sesuai pilihan awal (default internal 0)
        # Set combo default ke internal (index 0)
        self.camera_combo.setCurrentIndex(0)
        self.on_camera_source_changed(0)
        if not self.open_camera_from_state():
            return
            
        # Mulai timer sesi
        self.session_timer.start(self.session_time_limit)
        self.update_timer_display()
        
        family_text = f"Family: {self.family_name}"
        if self.email_address:
            family_text += f" | Email: {self.email_address}"
        self.family_label.setText(family_text)
        self.editor_family_label.setText(family_text)
        
        # Halaman kamera
        self.stack.setCurrentIndex(1)

    def on_camera_source_changed(self, idx):
        if idx == 0:
            self.camera_mode = "internal"
            self.ip_url_input.setEnabled(False)
        elif idx == 1:
            self.camera_mode = "external"
            self.ip_url_input.setEnabled(False)
        else:
            self.camera_mode = "ip"
            self.ip_url_input.setEnabled(True)

    def apply_camera_selection(self):
        self.ip_camera_url = self.ip_url_input.text().strip() if self.camera_mode == "ip" else ""
        if not self.open_camera_from_state():
            QMessageBox.critical(self, "Error", "Tidak dapat membuka kamera dengan konfigurasi saat ini.")

    def open_camera_from_state(self):
        """Buka kamera sesuai state pilihan user"""
        # Release sebelumnya
        try:
            if self.preview_timer.isActive():
                self.preview_timer.stop()
        except:
            pass
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
        # Pilih sumber
        if self.camera_mode == "internal":
            self.cap = cv2.VideoCapture(0)
        elif self.camera_mode == "external":
            self.cap = cv2.VideoCapture(1)
        else:
            url = self.ip_camera_url if self.ip_camera_url else "http://127.0.0.1:8080/video"
            self.cap = cv2.VideoCapture(url)

        if not self.cap or not self.cap.isOpened():
            self.camera_status_label.setText("Kamera: gagal dibuka")
            return False

        # Set resolusi 16:9
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Penyesuaian rasio
        if actual_height > 0 and abs((actual_width / actual_height) - (16/9)) > 0.01:
            if actual_width / actual_height > 16/9:
                self.cam_width = int(actual_height * 16/9)
                self.cam_height = actual_height
            else:
                self.cam_width = actual_width
                self.cam_height = int(actual_width * 9/16)

        self.preview_timer.start(self.preview_interval)
        self.camera_status_label.setText("Kamera: aktif")
        return True

    def session_timeout(self):
        QMessageBox.information(self, "Waktu Habis", "Sesi 5 menit telah berakhir. Kembali ke halaman utama.")
        self.end_session()

    def update_timer_display(self):
        if self.session_timer.isActive():
            remaining = self.session_timer.remainingTime()
            minutes = remaining // 60000
            seconds = (remaining % 60000) // 1000
            timer_text = f"⏰ {minutes:02d}:{seconds:02d}"
            self.timer_label.setText(timer_text)
            self.editor_timer_label.setText(timer_text)
            self.contest_timer_label.setText(timer_text)
            QTimer.singleShot(1000, self.update_timer_display)

    # --- LOADING RESOURCE FILES ---
    def load_backgrounds(self):
        self.bg_list.clear()
        self.backgrounds.clear()
        self.bg_selected_index = None
        bg_dir = "backgrounds"
        os.makedirs(bg_dir, exist_ok=True)

        for file in sorted(os.listdir(bg_dir)):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(bg_dir, file)
                img = cv2.imread(path)
                if img is not None:
                    self.backgrounds.append(img)
                    icon_pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item = QListWidgetItem(QIcon(icon_pixmap), "")
                    item.setToolTip(file)
                    self.bg_list.addItem(item)

    def load_layouts(self):
        self.layout_list.clear()
        self.layouts.clear()
        self.selected_layout = None
        layout_dir = "layouts"
        os.makedirs(layout_dir, exist_ok=True)
        
        for file in sorted(os.listdir(layout_dir)):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(layout_dir, file)
                self.layouts.append(path)
                icon_pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item = QListWidgetItem(QIcon(icon_pixmap), "")
                item.setToolTip(file)
                self.layout_list.addItem(item)

    def load_stickers(self):
        self.sticker_list.clear()
        self.sticker_files.clear()
        self.sticker_selected_index = None
        st_dir = "stickers"
        os.makedirs(st_dir, exist_ok=True)
        
        for file in sorted(os.listdir(st_dir)):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(st_dir, file)
                self.sticker_files.append(path)
                icon_pixmap = QPixmap(path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item = QListWidgetItem(QIcon(icon_pixmap), "")
                item.setToolTip(file)
                self.sticker_list.addItem(item)

    # --- TOGGLE SELECTION FUNCTIONS ---
    def toggle_background(self, item):
        idx = self.bg_list.row(item)
        if self.bg_selected_index == idx:
            self.bg_selected_index = None
            self.selected_background = None
            self.bg_list.clearSelection()
            self.status_label.setText("Background dibatalkan.")
        else:
            self.bg_selected_index = idx
            self.selected_background = self.backgrounds[idx]
            self.status_label.setText(f"Background dipilih")

    def toggle_layout(self, item):
        idx = self.layout_list.row(item)
        if self.layout_selected_index == idx:
            self.layout_list.clearSelection()
            self.selected_layout = None
            self.layout_selected_index = None
            self.status_label.setText("Layout dibatalkan.")
            if self.capturing:
                self._cancel_session()
        else:
            self.layout_list.setCurrentRow(idx)
            self.selected_layout = self.layouts[idx]
            self.layout_selected_index = idx
            self.status_label.setText(f"Layout dipilih")
            if self.capturing:
                self._cancel_session()

    def add_sticker(self, item):
        idx = self.sticker_list.row(item)
        sticker_path = self.sticker_files[idx]
        original_pixmap = QPixmap(sticker_path)
        
        default_width = 200
        default_height = int(original_pixmap.height() * (default_width / original_pixmap.width()))
        current_pixmap = original_pixmap.scaled(default_width, default_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        default_x = (self.editor_label.width() - current_pixmap.width()) // 2
        default_y = (self.editor_label.height() - current_pixmap.height()) // 2
        
        self.stickers.append({
            'original_pixmap': original_pixmap,
            'current_pixmap': current_pixmap,
            'position': QPoint(default_x, default_y),
            'size': current_pixmap.size(),
            'original_file_path': sticker_path
        })
        self.update_editor_display()

    # --- LOOP PREVIEW KAMERA ---
    def update_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame_raw = self.cap.read()
        if not ret or frame_raw is None:
            return

        h, w = frame_raw.shape[:2]
        target_aspect = 16/9
        current_aspect = w/h
        
        if current_aspect > target_aspect:
            new_width = int(h * target_aspect)
            start_x = (w - new_width) // 2
            frame_raw = frame_raw[:, start_x:start_x + new_width]
        elif current_aspect < target_aspect:
            new_height = int(w / target_aspect)
            start_y = (h - new_height) // 2
            frame_raw = frame_raw[start_y:start_y + new_height, :]

        frame_raw = cv2.flip(frame_raw, 1)
        processed_frame = frame_raw.copy()

        # SEGMENTASI BACKGROUND
        if self.selected_background is not None:
            try:
                frame_rgb = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2RGB)
                results = self.mp_selfie_segmentation.process(frame_rgb)
                if results and results.segmentation_mask is not None:
                    raw_mask = results.segmentation_mask.astype(np.float32)
                    alpha = refine_mask(raw_mask, kernel_size=5, blur_ksize=21)
                    bg = cv2.resize(
                        self.selected_background,
                        (frame_raw.shape[1], frame_raw.shape[0]),
                        interpolation=cv2.INTER_LANCZOS4
                    )
                    processed_frame = composite_foreground_background(frame_raw, bg, alpha)
            except Exception:
                processed_frame = frame_raw.copy()

        display_frame = processed_frame.copy()

        # OVERLAY LAYOUT
        overlay_rgba = None
        if self.capturing and self.active_composed_rgba is not None:
            overlay_rgba = self.active_composed_rgba.copy()
        elif self.selected_layout and not self.capturing:
            try:
                layout_img = cv2.imread(self.selected_layout, cv2.IMREAD_UNCHANGED)
                if layout_img is not None:
                    layout_resized = cv2.resize(
                        layout_img,
                        (display_frame.shape[1], display_frame.shape[0]),
                        interpolation=cv2.INTER_LANCZOS4
                    )
                    if layout_resized.shape[2] == 3:
                        bgr = layout_resized
                        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                        alpha = np.ones((layout_resized.shape[0], layout_resized.shape[1]), dtype=np.uint8) * 255
                        overlay_rgba = np.dstack([rgb, alpha])
                    else:
                        bgr = layout_resized[:, :, :3]
                        alpha = layout_resized[:, :, 3]
                        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                        overlay_rgba = np.dstack([rgb, alpha])
            except Exception:
                overlay_rgba = None

        # COMPOSITE
        if overlay_rgba is not None:
            try:
                overlay_bgr = cv2.cvtColor(overlay_rgba[:, :, :3], cv2.COLOR_RGB2BGR)
                alpha_layout = overlay_rgba[:, :, 3:] / 255.0

                if self.capturing and self.current_slot_index < len(self.active_slots):
                    bx, by, bw, bh = self.active_slots[self.current_slot_index]
                    cam_h, cam_w = processed_frame.shape[:2]

                    slot_aspect = bw / max(1, bh)
                    cam_aspect = cam_w / max(1, cam_h)
                    if cam_aspect > slot_aspect:
                        new_w = int(cam_h * slot_aspect)
                        start_x = (cam_w - new_w) // 2
                        crop = processed_frame[0:cam_h, start_x:start_x+new_w]
                    else:
                        new_h = int(cam_w / slot_aspect)
                        start_y = max(0, (cam_h - new_h) // 2)
                        crop = processed_frame[start_y:start_y+new_h, 0:cam_w]

                    if crop is not None and crop.size != 0:
                        resized_cam_for_slot = cv2.resize(crop, (bw, bh), interpolation=cv2.INTER_LANCZOS4)
                        overlay_bgr[by:by+bh, bx:bx+bw] = resized_cam_for_slot
                        alpha_layout[by:by+bh, bx:bx+bw] = 1.0

                h2, w2 = overlay_bgr.shape[:2]
                roi = display_frame[0:h2, 0:w2].astype(np.float32)
                blended = (1.0 - alpha_layout) * roi + alpha_layout * overlay_bgr.astype(np.float32)
                display_frame[0:h2, 0:w2] = blended.astype(np.uint8)
            except Exception:
                pass

        # FLASH
        if self.flash_active:
            flash_overlay = np.ones_like(display_frame, dtype=np.uint8) * 255
            display_frame = cv2.addWeighted(flash_overlay, 0.9, display_frame, 0.1, 0)

        # COUNTDOWN OVERLAY
        if self.countdown_active and self.countdown_slot_rect is not None:
            x, y, w3, h3 = self.countdown_slot_rect
            overlay = display_frame.copy()
            cv2.rectangle(overlay, (x, y), (x + w3, y + h3), (0, 165, 255), -1)
            display_frame = cv2.addWeighted(overlay, 0.25, display_frame, 0.75, 0)
            cv2.rectangle(display_frame, (x, y), (x + w3, y + h3), (0, 165, 255), 4)
            cv2.putText(display_frame, str(self.countdown_value),
                        (x + max(10, w3 // 2 - 30), y + max(40, h3 // 2 + 30)),
                        cv2.FONT_HERSHEY_SIMPLEX, 2.2, (255, 255, 255), 6, cv2.LINE_AA)

        frame_resized = cv2.resize(
            display_frame,
            (self.display_width, self.display_height),
            interpolation=cv2.INTER_AREA
        )

        img_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        qimg = QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], img_rgb.strides[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimg))

    # --- FUNGSI CAPTURE FOTO ---
    def capture_photo(self):
        if not self.cap or not self.cap.isOpened():
            QMessageBox.warning(self, "Error", "Kamera tidak tersedia.")
            return

        # Capture tunggal (tanpa layout)
        if not self.selected_layout:
            ret, frame = self.cap.read()
            if not ret:
                QMessageBox.warning(self, "Error", "Gagal mengambil foto!")
                return
                
            frame = self.process_captured_frame(frame)
            raw_photo = frame.copy()
            self.raw_photos.append(raw_photo)
            
            if self.selected_background is not None:
                try:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.mp_selfie_segmentation.process(frame_rgb)
                    if results and results.segmentation_mask is not None:
                        raw_mask = results.segmentation_mask.astype(np.float32)
                        alpha = refine_mask(raw_mask, kernel_size=5, blur_ksize=21)
                        bg = cv2.resize(
                            self.selected_background,
                            (frame.shape[1], frame.shape[0]),
                            interpolation=cv2.INTER_LANCZOS4
                        )
                        frame = composite_foreground_background(frame, bg, alpha)
                except Exception:
                    pass

            self.photo = frame.copy()
            self.stickers.clear()
            self.show_editor()
            return

        # Multi-slot dengan layout
        if not self.capturing:
            ret, preview_frame = self.cap.read()
            if not ret:
                QMessageBox.warning(self, "Error", "Gagal membaca kamera saat memulai capture.")
                return
                
            preview_frame = self.process_captured_frame(preview_frame)
            cam_h, cam_w = preview_frame.shape[:2]
            
            layout_img = cv2.imread(self.selected_layout, cv2.IMREAD_UNCHANGED)
            if layout_img is None:
                QMessageBox.warning(self, "Error", f"Gagal membuka layout: {self.selected_layout}")
                return
            layout_resized = cv2.resize(layout_img, (cam_w, cam_h), interpolation=cv2.INTER_LANCZOS4)

            if layout_resized.shape[2] == 3:
                bgr = layout_resized
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                alpha = np.ones((cam_h, cam_w), dtype=np.uint8) * 255
                layout_rgba = np.dstack([rgb, alpha])
            else:
                bgr = layout_resized[:, :, :3]
                alpha = layout_resized[:, :, 3]
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                layout_rgba = np.dstack([rgb, alpha])

            slots = detect_transparent_slots_from_rgba(layout_rgba)
            if not slots:
                slots = [(0, 0, cam_w, cam_h)]

            self.capturing = True
            self.active_layout_rgba = layout_rgba.copy()
            self.active_composed_rgba = layout_rgba.copy()
            self.active_slots = slots
            self.current_slot_index = 0
            self.countdown_active = False
            self.countdown_slot_rect = None
            self.status_label.setText(f"Sesi layout dimulai — slot 1 / {len(self.active_slots)}. Tekan Ambil Foto untuk mulai countdown.")
            self._start_countdown_for_current_slot()
            return

        if self.capturing and not self.countdown_active:
            if self.current_slot_index >= len(self.active_slots):
                self._finalize_session()
                return
            self._start_countdown_for_current_slot()
            return

    def process_captured_frame(self, frame):
        h, w = frame.shape[:2]
        target_aspect = 16/9
        current_aspect = w/h
        
        if current_aspect > target_aspect:
            new_width = int(h * target_aspect)
            start_x = (w - new_width) // 2
            frame = frame[:, start_x:start_x + new_width]
        elif current_aspect < target_aspect:
            new_height = int(w / target_aspect)
            start_y = (h - new_height) // 2
            frame = frame[start_y:start_y + new_height, :]

        frame = cv2.flip(frame, 1)
        return frame

    # --- COUNTDOWN DAN SESI CAPTURE ---
    def _start_countdown_for_current_slot(self):
        if not self.capturing or self.current_slot_index >= len(self.active_slots):
            return
        self.countdown_value = 5
        self.countdown_active = True
        self.countdown_slot_rect = self.active_slots[self.current_slot_index]
        self._slot_capture_result = None
        self.countdown_timer.start(1000)
        self.status_label.setText(f"Countdown slot {self.current_slot_index + 1} ...")

    def _on_countdown_tick(self):
        self.countdown_value -= 1
        if self.countdown_value <= 0:
            self.countdown_timer.stop()
            self.countdown_active = False

            ret, frame_raw = self.cap.read()
            if not ret:
                self._slot_capture_result = None
            else:
                frame_raw = self.process_captured_frame(frame_raw)
                raw_photo = frame_raw.copy()
                self.raw_photos.append(raw_photo)
                
                frame_to_use = frame_raw.copy()
                if self.selected_background is not None:
                    try:
                        frame_rgb = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2RGB)
                        results = self.mp_selfie_segmentation.process(frame_rgb)
                        if results and results.segmentation_mask is not None:
                            raw_mask = results.segmentation_mask.astype(np.float32)
                            alpha = refine_mask(raw_mask, kernel_size=5, blur_ksize=21)
                            bg = cv2.resize(
                                self.selected_background,
                                (frame_raw.shape[1], frame_raw.shape[0]),
                                interpolation=cv2.INTER_LANCZOS4
                            )
                            frame_to_use = composite_foreground_background(frame_raw, bg, alpha)
                    except Exception:
                        frame_to_use = frame_raw.copy()
                self._slot_capture_result = frame_to_use

            self._flash_once()

            if self._slot_capture_result is not None:
                bbox = self.active_slots[self.current_slot_index]
                self.active_composed_rgba = self._place_photo_into_layout_bbox(self.active_composed_rgba, self._slot_capture_result, bbox)
                n = len(self.active_slots)
                self.status_label.setText(f"Slot {self.current_slot_index+1} terisi ({self.current_slot_index+1}/{n}). Tekan Ambil Foto untuk slot berikutnya.")
                self.current_slot_index += 1
            else:
                self.status_label.setText("Gagal mengambil foto. Tekan Ambil Foto untuk coba lagi.")

            if self.current_slot_index >= len(self.active_slots):
                QTimer.singleShot(250, self._finalize_session)

            QTimer.singleShot(300, self._clear_countdown_slot)

    def _flash_once(self):
        self.flash_active = True
        QTimer.singleShot(120, lambda: setattr(self, "flash_active", False))

    def _clear_countdown_slot(self):
        self.countdown_slot_rect = None

    def _finalize_session(self):
        final_rgba = self.active_composed_rgba.copy()
        final_bgr = cv2.cvtColor(final_rgba[:, :, :3], cv2.COLOR_RGB2BGR)

        self.photo = final_bgr.copy()
        self.stickers.clear()
        self.capturing = False
        self.active_layout_rgba = None
        self.active_composed_rgba = None
        self.active_slots = []
        self.current_slot_index = 0
        self.countdown_active = False
        self.countdown_slot_rect = None
        self.status_label.setText("Selesai — foto siap diedit.")
        self.show_editor()

    def _cancel_session(self):
        try:
            self.countdown_timer.stop()
        except:
            pass
        self.capturing = False
        self.active_layout_rgba = None
        self.active_composed_rgba = None
        self.active_slots = []
        self.current_slot_index = 0
        self.countdown_active = False
        self.countdown_slot_rect = None
        self.status_label.setText("Session layout dibatalkan.")

    def _place_photo_into_layout_bbox(self, layout_rgba, frame_bgr, bbox):
        x, y, w, h = bbox
        composed = layout_rgba.copy()
        photo_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        ph, pw = photo_rgb.shape[:2]
        scale = max(w / pw, h / ph)
        new_w = max(1, int(pw * scale))
        new_h = max(1, int(ph * scale))
        resized = cv2.resize(photo_rgb, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        start_x = (new_w - w) // 2
        start_y = (new_h - h) // 2
        cropped = resized[start_y:start_y + h, start_x:start_x + w]
        if cropped.shape[0] != h or cropped.shape[1] != w:
            tmp = np.zeros((h, w, 3), dtype=np.uint8)
            th, tw = cropped.shape[:2]
            tmp[0:th, 0:tw] = cropped
            cropped = tmp
        region_alpha = (layout_rgba[y:y+h, x:x+w, 3] == 0)
        for c in range(3):
            dst_region = composed[y:y+h, x:x+w, c]
            src_region = cropped[:, :, c]
            dst_region[region_alpha] = src_region[region_alpha]
            composed[y:y+h, x:x+w, c] = dst_region
        a_region = composed[y:y+h, x:x+w, 3]
        a_region[region_alpha] = 255
        composed[y:y+h, x:x+w, 3] = a_region
        return composed

    # --- FUNGSI EDITOR ---
    def show_editor(self):
        self.update_photo_counter()
        self.stack.setCurrentIndex(2)
        self.update_editor_display()

    def update_editor_display(self):
        if self.photo is None:
            return

        img_rgb = cv2.cvtColor(self.photo, cv2.COLOR_BGR2RGB)
        qimg = QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], img_rgb.strides[0], QImage.Format_RGB888)
        photo_pixmap = QPixmap.fromImage(qimg)

        canvas_width = 960
        canvas_height = 540
        scaled_pixmap = photo_pixmap.scaled(canvas_width, canvas_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        canvas_pixmap = QPixmap(canvas_width, canvas_height)
        canvas_pixmap.fill(Qt.black)

        painter = QPainter(canvas_pixmap)
        x_offset = (canvas_width - scaled_pixmap.width()) // 2
        y_offset = (canvas_height - scaled_pixmap.height()) // 2
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)

        # Gambar sticker + handle resize
        handle_size = 12
        handle_brush = QBrush(QColor(255, 255, 255))
        handle_pen = QPen(QColor(0, 122, 204))
        handle_pen.setWidth(2)
        border_pen = QPen(QColor(0, 122, 204, 180))
        border_pen.setWidth(2)

        for sticker_data in self.stickers:
            painter.save()  # penting: isolasi state pen/brush untuk tiap sticker

            pixmap = sticker_data['current_pixmap']
            pos = sticker_data['position']

            # 1) Gambar sticker
            painter.drawPixmap(pos, pixmap)

            # 2) Border sticker (tanpa fill)
            painter.setPen(border_pen)
            painter.setBrush(Qt.NoBrush)  # perbaikan: cegah fill putih menutupi sticker
            painter.drawRect(QRect(pos, pixmap.size()))

            # 3) Handle sudut (fill putih kecil)
            painter.setPen(handle_pen)
            painter.setBrush(handle_brush)
            rect = pixmap.rect().translated(pos)
            tl = QRect(rect.left(), rect.top(), handle_size, handle_size)
            tr = QRect(rect.right() - handle_size + 1, rect.top(), handle_size, handle_size)
            bl = QRect(rect.left(), rect.bottom() - handle_size + 1, handle_size, handle_size)
            br = QRect(rect.right() - handle_size + 1, rect.bottom() - handle_size + 1, handle_size, handle_size)
            for hrect in (tl, tr, bl, br):
                painter.drawRect(hrect)

            painter.restore()  # kembalikan state agar iterasi berikutnya bersih

        painter.end()
        self.editor_label.setPixmap(canvas_pixmap)

    def update_photo_counter(self):
        self.photo_count_label.setText(f"Foto ke: {self.photo_counter}")
        self.total_photos_label.setText(f"Total foto: {len(self.session_photos)}")

    # --- AKSI EDITOR ---
    def retake_photo(self):
        self.photo = None
        self.stickers.clear()
        if self.raw_photos:
            self.raw_photos.pop()
        self.stack.setCurrentIndex(1)
        self.status_label.setText("Foto tidak disimpan. Ambil foto baru.")

    def take_more_photo(self):
        if self.photo is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada foto untuk disimpan.")
            return
            
        self.save_current_photo()
        self.photo = None
        self.stickers.clear()
        self.photo_counter += 1
        self.stack.setCurrentIndex(1)
        self.status_label.setText(f"Foto disimpan! Siap untuk foto ke-{self.photo_counter}")

    def finish_session(self):
        if self.photo is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada foto untuk disimpan.")
            return
            
        self.save_current_photo()
        self.load_contest_photos()
        # Prefill email tujuan
        self.email_send_input.setText(self.email_address)
        self.stack.setCurrentIndex(3)

    def save_current_photo(self):
        if self.photo is None:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        img_rgb = cv2.cvtColor(self.photo, cv2.COLOR_BGR2RGB)
        qimg = QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], img_rgb.strides[0], QImage.Format_RGB888)
        painter_pix = QPixmap.fromImage(qimg)
        
        painter = QPainter(painter_pix)
        for sticker_data in self.stickers:
            pixmap = sticker_data['current_pixmap']
            pos = sticker_data['position']
            painter.drawPixmap(pos, pixmap)
        painter.end()
        
        final_img_rgb = self.qpixmap_to_cv(painter_pix)
        final_img_bgr = cv2.cvtColor(final_img_rgb, cv2.COLOR_RGB2BGR)

        base_name = self.family_name.lower().replace(" ", "_")
        
        # Simpan foto murni
        if self.raw_photos:
            if len(self.raw_photos) == 1:
                raw_filename = f"{base_name}-raw.png"
                raw_path = os.path.join(self.family_output_dir, raw_filename)
                cv2.imwrite(raw_path, self.raw_photos[0], [cv2.IMWRITE_PNG_COMPRESSION, 0])
            else:
                for i, raw_photo in enumerate(self.raw_photos):
                    raw_filename = f"{base_name}-layout{len(self.raw_photos)}-{i+1}.png"
                    raw_path = os.path.join(self.family_output_dir, raw_filename)
                    cv2.imwrite(raw_path, raw_photo, [cv2.IMWRITE_PNG_COMPRESSION, 0])

        no_watermark_filename = f"{base_name}-no_watermark-{self.photo_counter}.png"
        no_watermark_path = os.path.join(self.family_output_dir, no_watermark_filename)
        cv2.imwrite(no_watermark_path, final_img_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        
        watermark_filename = f"{base_name}-watermark-{self.photo_counter}.png"
        watermark_path = os.path.join(self.family_output_dir, watermark_filename)
        self.apply_watermark_and_save(final_img_rgb, watermark_path)
        
        photo_info = {
            'counter': self.photo_counter,
            'timestamp': timestamp,
            'no_watermark_path': no_watermark_path,
            'watermark_path': watermark_path,
            'raw_count': len(self.raw_photos)
        }
        self.session_photos.append(photo_info)
        
        self.raw_photos = []

    def apply_watermark_and_save(self, img_rgb, save_path):
        img_pil = Image.fromarray(img_rgb).convert("RGBA")
        
        try:
            watermark_path = os.path.join("assets", "watermark.png")
            watermark = Image.open(watermark_path).convert("RGBA")
            
            max_wm_width = img_pil.width // 5
            if watermark.width > max_wm_width:
                ratio = max_wm_width / watermark.width
                new_size = (int(watermark.width * ratio), int(watermark.height * ratio))
                watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)

            margin = 10
            position = (margin, img_pil.height - watermark.height - margin)

            transparent = Image.new("RGBA", img_pil.size)
            transparent.paste(watermark, position, mask=watermark)
            combined = Image.alpha_composite(img_pil, transparent)
            final_img_rgba = combined
        except Exception:
            final_img_rgba = img_pil

        final_img_rgba.save(save_path, format="PNG", compress_level=0)

    # --- FUNGSI HALAMAN LOMBA ---
    def load_contest_photos(self):
        for i in reversed(range(self.photo_gallery_layout.count())): 
            w = self.photo_gallery_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        if not self.session_photos:
            no_photos_label = QLabel("Tidak ada foto dalam sesi ini")
            no_photos_label.setStyleSheet("font-size: 16px; color: #666666; padding: 50px;")
            no_photos_label.setAlignment(Qt.AlignCenter)
            self.photo_gallery_layout.addWidget(no_photos_label, 0, 0)
            return

        cols = 3
        for i, photo_info in enumerate(self.session_photos):
            row = i // cols
            col = i % cols
            photo_widget = self.create_contest_photo_widget(photo_info, i)
            self.photo_gallery_layout.addWidget(photo_widget, row, col)

    def create_contest_photo_widget(self, photo_info, index):
        widget = QWidget()
        widget.setFixedSize(280, 220)
        widget.setStyleSheet("""
            QWidget { 
                border: 3px solid #E1E5E9; 
                border-radius: 10px; 
                background-color: white;
            }
            QWidget:hover { 
                border-color: #007ACC; 
                background-color: #F0F8FF;
            }
        """)
        widget.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        photo_label = QLabel()
        photo_label.setFixedSize(260, 150)
        photo_label.setStyleSheet("border: 1px solid #DDD; border-radius: 5px;")
        
        if os.path.exists(photo_info['watermark_path']):
            pixmap = QPixmap(photo_info['watermark_path'])
            scaled_pixmap = pixmap.scaled(260, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            photo_label.setPixmap(scaled_pixmap)
            photo_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(photo_label)
        
        info_label = QLabel(f"Foto {photo_info['counter']} - {photo_info['timestamp'][9:17]}")
        info_label.setStyleSheet("font-size: 12px; color: #666666; text-align: center;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        widget.mousePressEvent = lambda event, idx=index: self.select_contest_photo(idx)
        return widget

    def select_contest_photo(self, index):
        if index >= len(self.session_photos):
            return
            
        photo_info = self.session_photos[index]
        
        lomba_dir = os.path.join("lomba", self.family_name)
        os.makedirs(lomba_dir, exist_ok=True)
        
        contest_filename = f"{self.family_name.lower().replace(' ', '_')}-contest.png"
        contest_path = os.path.join(lomba_dir, contest_filename)
        
        try:
            shutil.copy2(photo_info['watermark_path'], contest_path)
            self.selected_photo_label.setText(f"Foto terpilih: Foto {photo_info['counter']}")
            QMessageBox.information(self, "Foto Lomba Dipilih", 
                                  f"Foto {photo_info['counter']} telah dipilih sebagai foto lomba dan disimpan di folder lomba!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal menyimpan foto lomba: {str(e)}")

    # --- KIRIM EMAIL SEMUA FOTO FAMILY ---
    def on_send_all_photos_clicked(self):
        recipient = self.email_send_input.text().strip()
        if not recipient:
            QMessageBox.warning(self, "Peringatan", "Email tujuan belum diisi.")
            return

        # Kumpulkan semua file gambar di folder family
        if not hasattr(self, "family_output_dir") or not os.path.isdir(self.family_output_dir):
            QMessageBox.warning(self, "Error", "Folder output family tidak ditemukan.")
            return

        files = []
        for f in sorted(os.listdir(self.family_output_dir)):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                files.append(os.path.join(self.family_output_dir, f))

        if not files:
            QMessageBox.information(self, "Info", "Tidak ada file foto untuk dikirim.")
            return

        self.email_send_status.setText("Mengirim email...")
        self.email_send_status.repaint()
        send_btn_disabled = True

        def _worker():
            subject = f"Foto Photobooth - {self.family_name}"
            body = f"Berikut terlampir semua file foto untuk family: {self.family_name}"
            ok, err = send_email_with_attachments(
                SMTP_USERNAME, SMTP_PASSWORD, recipient, subject, body, files
            )
            def _after():
                if ok:
                    self.email_send_status.setText("Email terkirim.")
                    QMessageBox.information(self, "Sukses", "Email berhasil dikirim.")
                else:
                    self.email_send_status.setText("Gagal mengirim email.")
                    QMessageBox.warning(self, "Gagal", f"Gagal mengirim email: {err}")
            QTimer.singleShot(0, _after)

        threading.Thread(target=_worker, daemon=True).start()

    def end_session(self):
        self.session_timer.stop()
        if self.preview_timer.isActive():
            self.preview_timer.stop()
        
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None
        
        self.family_name = ""
        self.email_address = ""
        self.session_photos = []
        self.raw_photos = []
        self.photo_counter = 1
        self.photo = None
        self.stickers.clear()
        self.selected_background = None
        self.selected_layout = None
        self.bg_selected_index = None
        self.layout_selected_index = None
        
        self.name_input.clear()
        self.email_input.clear()
        self.selected_photo_label.setText("Belum ada foto yang dipilih")
        
        self._cancel_session()
        
        self.stack.setCurrentIndex(0)
        QMessageBox.information(self, "Sesi Berakhir", "Sesi photobooth telah berakhir. Terima kasih!")

    # --- INTERAKSI STICKER (DRAG, RESIZE, DELETE) ---
    def editor_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            click_pos = event.pos()
            
            # Prioritaskan handle resize
            for i in reversed(range(len(self.stickers))):
                sticker_data = self.stickers[i]
                pixmap = sticker_data['current_pixmap']
                pos = sticker_data['position']
                rect = pixmap.rect().translated(pos)
                
                handle_size = 15
                top_left = QRect(pos.x(), pos.y(), handle_size, handle_size)
                top_right = QRect(pos.x() + rect.width() - handle_size, pos.y(), handle_size, handle_size)
                bottom_left = QRect(pos.x(), pos.y() + rect.height() - handle_size, handle_size, handle_size)
                bottom_right = QRect(pos.x() + rect.width() - handle_size, pos.y() + rect.height() - handle_size, handle_size, handle_size)

                if bottom_right.contains(click_pos):
                    self.resizing_sticker_index = i
                    self.resize_corner = 'bottom_right'
                    self.drag_offset = click_pos - pos - QPoint(rect.width(), rect.height())
                    return
                elif bottom_left.contains(click_pos):
                    self.resizing_sticker_index = i
                    self.resize_corner = 'bottom_left'
                    self.drag_offset = click_pos - pos - QPoint(0, rect.height())
                    return
                elif top_right.contains(click_pos):
                    self.resizing_sticker_index = i
                    self.resize_corner = 'top_right'
                    self.drag_offset = click_pos - pos - QPoint(rect.width(), 0)
                    return
                elif top_left.contains(click_pos):
                    self.resizing_sticker_index = i
                    self.resize_corner = 'top_left'
                    self.drag_offset = click_pos - pos
                    return

            # Drag
            for i in reversed(range(len(self.stickers))):
                sticker_data = self.stickers[i]
                pixmap = sticker_data['current_pixmap']
                pos = sticker_data['position']
                rect = pixmap.rect().translated(pos)
                if rect.contains(click_pos):
                    self.dragging_sticker_index = i
                    self.drag_offset = click_pos - pos
                    # bawa ke depan
                    sticker_to_move = self.stickers.pop(i)
                    self.stickers.append(sticker_to_move)
                    self.dragging_sticker_index = len(self.stickers) - 1
                    self.update_editor_display()
                    break

    def editor_mouseMoveEvent(self, event):
        # Resize
        if self.resizing_sticker_index is not None:
            sticker_data = self.stickers[self.resizing_sticker_index]
            original_pixmap = sticker_data['original_pixmap']
            current_pos = sticker_data['position']
            current_size = sticker_data['size']
            new_mouse_pos = event.pos()
            
            if self.resize_corner == 'bottom_right':
                new_width = new_mouse_pos.x() - current_pos.x()
                new_height = new_mouse_pos.y() - current_pos.y()
            elif self.resize_corner == 'bottom_left':
                new_width = current_pos.x() + current_size.width() - new_mouse_pos.x()
                new_height = new_mouse_pos.y() - current_pos.y()
                new_pos_x = new_mouse_pos.x()
                sticker_data['position'].setX(new_pos_x)
            elif self.resize_corner == 'top_right':
                new_width = new_mouse_pos.x() - current_pos.x()
                new_height = current_pos.y() + current_size.height() - new_mouse_pos.y()
                new_pos_y = new_mouse_pos.y()
                sticker_data['position'].setY(new_pos_y)
            elif self.resize_corner == 'top_left':
                new_width = current_pos.x() + current_size.width() - new_mouse_pos.x()
                new_height = current_pos.y() + current_size.height() - new_mouse_pos.y()
                new_pos_x = new_mouse_pos.x()
                new_pos_y = new_mouse_pos.y()
                sticker_data['position'].setX(new_pos_x)
                sticker_data['position'].setY(new_pos_y)

            # Pertahankan rasio
            if original_pixmap.width() > 0 and original_pixmap.height() > 0:
                aspect_ratio = original_pixmap.width() / original_pixmap.height()
                if new_width / max(1, new_height) > aspect_ratio:
                    new_width = int(new_height * aspect_ratio)
                else:
                    new_height = int(new_width / aspect_ratio)

            min_size = 20
            new_width = max(min_size, new_width)
            new_height = max(min_size, new_height)

            sticker_data['current_pixmap'] = original_pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            sticker_data['size'] = sticker_data['current_pixmap'].size()
            self.update_editor_display()
            return

        # Drag
        if self.dragging_sticker_index is not None:
            move_pos = event.pos() - self.drag_offset
            sticker_data = self.stickers[self.dragging_sticker_index]
            sticker_data['position'] = move_pos
            self.update_editor_display()
            return
        
        # Cursor feedback
        click_pos = event.pos()
        cursor_changed = False
        for i in reversed(range(len(self.stickers))):
            sticker_data = self.stickers[i]
            pixmap = sticker_data['current_pixmap']
            pos = sticker_data['position']
            rect = pixmap.rect().translated(pos)
            
            handle_size = 15
            top_left = QRect(pos.x(), pos.y(), handle_size, handle_size)
            top_right = QRect(pos.x() + rect.width() - handle_size, pos.y(), handle_size, handle_size)
            bottom_left = QRect(pos.x(), pos.y() + rect.height() - handle_size, handle_size, handle_size)
            bottom_right = QRect(pos.x() + rect.width() - handle_size, pos.y() + rect.height() - handle_size, handle_size, handle_size)

            if bottom_right.contains(click_pos) or top_left.contains(click_pos):
                self.editor_label.setCursor(Qt.SizeFDiagCursor)
                cursor_changed = True
                break
            elif bottom_left.contains(click_pos) or top_right.contains(click_pos):
                self.editor_label.setCursor(Qt.SizeBDiagCursor)
                cursor_changed = True
                break
            elif rect.contains(click_pos):
                self.editor_label.setCursor(Qt.OpenHandCursor)
                cursor_changed = True
                break
        
        if not cursor_changed:
            self.editor_label.setCursor(Qt.ArrowCursor)

    def editor_mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging_sticker_index = None
            self.resizing_sticker_index = None
            self.resize_corner = None
            self.editor_label.setCursor(Qt.ArrowCursor)

    def editor_mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            click_pos = event.pos()
            for i in reversed(range(len(self.stickers))):
                sticker_data = self.stickers[i]
                pixmap = sticker_data['current_pixmap']
                pos = sticker_data['position']
                rect = pixmap.rect().translated(pos)
                if rect.contains(click_pos):
                    del self.stickers[i]
                    self.update_editor_display()
                    break

    # --- DIALOG INPUT URL BACKGROUND ---
    def show_input_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Tambah Background dari URL")
        dialog.setFixedSize(400, 150)
        layout = QFormLayout(dialog)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Masukkan URL gambar background")
        layout.addRow("URL Background:", self.url_input)

        submit_btn = QPushButton("Tambahkan")
        submit_btn.clicked.connect(lambda: self.submit_background_url(dialog))
        layout.addRow(submit_btn)

        dialog.exec_()

    def submit_background_url(self, dialog):
        url = self.url_input.text().strip()
        if url:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if img is not None:
                        self.backgrounds.append(img)
                        icon_pixmap = QPixmap()
                        icon_pixmap.loadFromData(response.content)
                        icon_pixmap = icon_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        item = QListWidgetItem(QIcon(icon_pixmap), "")
                        item.setToolTip("Background dari URL")
                        self.bg_list.addItem(item)
                        QMessageBox.information(self, "Sukses", "Background berhasil ditambahkan.")
                        dialog.close()
                    else:
                        QMessageBox.warning(self, "Error", "Gagal memuat gambar dari URL.")
                else:
                    QMessageBox.warning(self, "Error", "URL tidak valid atau tidak dapat diakses.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Gagal memuat gambar dari URL: {str(e)}")
        else:
            QMessageBox.warning(self, "Peringatan", "URL tidak boleh kosong.")

    # --- UTILITY FUNCTIONS ---
    def qpixmap_to_cv(self, pixmap):
        image = pixmap.toImage().convertToFormat(QImage.Format_RGB888)
        width, height = image.width(), image.height()
        ptr = image.bits()
        ptr.setsize(height * width * 3)
        arr = np.array(ptr).reshape(height, width, 3)
        return arr

    def overlay_transparent(self, background, overlay, x, y):
        try:
            if overlay is None:
                return background
            if overlay.shape[2] == 3:
                alpha = np.ones((overlay.shape[0], overlay.shape[1]), dtype=np.uint8) * 255
                overlay = np.dstack([overlay, alpha])

            h, w = overlay.shape[0], overlay.shape[1]
            if x >= background.shape[1] or y >= background.shape[0]:
                return background

            if x + w > background.shape[1]:
                w = background.shape[1] - x
                overlay = overlay[:, :w]
            if y + h > background.shape[0]:
                h = background.shape[0] - y
                overlay = overlay[:h]

            overlay_img = overlay[:, :, :3].astype(np.float32)
            mask = overlay[:, :, 3:].astype(np.float32) / 255.0
            roi = background[y:y+h, x:x+w].astype(np.float32)
            blended = (mask * overlay_img) + ((1.0 - mask) * roi)
            background[y:y+h, x:x+w] = blended.astype(np.uint8)
        except Exception:
            pass
        return background

    def closeEvent(self, event):
        if self.session_timer.isActive():
            self.session_timer.stop()
        if self.preview_timer.isActive():
            self.preview_timer.stop()
        if self.countdown_timer.isActive():
            self.countdown_timer.stop()
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
        event.accept()

# ---------------------------
# MENJALANKAN APLIKASI
# ---------------------------
if __name__ == "__main__":
    required_dirs = [
        "backgrounds",
        "layouts",
        "stickers",
        "assets",
        "output",
        "lomba"
    ]
    for dir_name in required_dirs:
        os.makedirs(dir_name, exist_ok=True)
    
    app = QApplication(sys.argv)
    window = PhotoBooth()
    window.show()
    sys.exit(app.exec_())