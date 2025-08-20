import sys
import uiautomator2 as u2
import adbutils
import time
import random
import threading
import json
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QCheckBox, QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
    QTextEdit, QApplication, QTableWidget, QTableWidgetItem, QListWidget,
    QInputDialog, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Hàm để lấy đường dẫn cơ sở, hỗ trợ cả .py và .exe
def get_base_path():
    if getattr(sys, 'frozen', False):  # Nếu chạy dưới dạng .exe
        return os.path.dirname(sys.executable)
    else:  # Nếu chạy dưới dạng .py
        return os.path.dirname(os.path.abspath(__file__))

CAU_HINH = {
    'goi_tiktok': 'com.zhiliaoapp.musically',
    'do_phan_giai_muc_tieu': [1080, 1920]
}
adb = adbutils.AdbClient(host='127.0.0.1', port=5037)
running = True
device_logs = {}
stop_event = threading.Event()

class TextEditLogger:
    def __init__(self, device_serial, table_widget, row):
        self.device_serial = device_serial
        self.table_widget = table_widget
        self.row = row

    def write(self, message):
        global device_logs
        if self.device_serial not in device_logs:
            device_logs[self.device_serial] = []
        device_logs[self.device_serial].append(f"[{time.strftime('%H:%M:%S')}] {message}")
        log_text = "\n".join(device_logs[self.device_serial][-5:])
        item = QTableWidgetItem(log_text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table_widget.setItem(self.row, 2, item)
        self.table_widget.resizeRowsToContents()
        QApplication.processEvents()

    def flush(self):
        pass

class TikTokApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TikTok Automation")
        self.setWindowIcon(QIcon('icon1.png'))
        self.setGeometry(100, 100, 800, 700)
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_config()
        self.running = True

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)

        height = 30
        label_width = 150

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)
        
        device_group = QGroupBox("Chọn thiết bị")
        device_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.select_all_button = QPushButton("Chọn tất cả")
        self.select_all_button.setFixedHeight(height)
        self.select_all_button.clicked.connect(self.select_all_devices)
        button_layout.addWidget(self.select_all_button)
        self.deselect_all_button = QPushButton("Bỏ chọn tất cả")
        self.deselect_all_button.setFixedHeight(height)
        self.deselect_all_button.clicked.connect(self.deselect_all_devices)
        button_layout.addWidget(self.deselect_all_button)
        self.refresh_button = QPushButton("Làm mới thiết bị")
        self.refresh_button.setFixedHeight(height)
        self.refresh_button.clicked.connect(self.refresh_devices)
        button_layout.addWidget(self.refresh_button)
        device_layout.addLayout(button_layout)
        
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(3)
        self.device_table.setHorizontalHeaderLabels(["Chọn", "Thiết bị", "Log thiết bị"])
        self.device_table.setColumnWidth(0, 50)
        self.device_table.setColumnWidth(1, 200)
        self.device_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.device_table.setMinimumHeight(250)
        self.device_table.setShowGrid(True)
        self.device_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        device_layout.addWidget(self.device_table)
        
        self.save_group_button = QPushButton("Lưu Nhóm Phone")
        self.save_group_button.setFixedHeight(height)
        self.save_group_button.clicked.connect(self.save_phone_group)
        device_layout.addWidget(self.save_group_button)
        self.load_group_list = QListWidget()
        self.load_group_list.setFixedHeight(100)
        self.load_group_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.load_group_list.itemSelectionChanged.connect(self.load_phone_group)
        device_layout.addWidget(self.load_group_list)
        self.selected_groups_label = QLabel("Nhóm đã chọn: Không có")
        self.selected_groups_label.setFixedHeight(height)
        device_layout.addWidget(self.selected_groups_label)
        device_group.setLayout(device_layout)
        top_layout.addWidget(device_group)
        
        config_group = QGroupBox("Cấu hình chức năng")
        config_layout = QGridLayout()
        config_layout.setSpacing(10)
        self.bat_thich = QCheckBox()
        self.bat_thich.setFixedHeight(height)
        label_thich = QLabel("Bật thích:")
        label_thich.setFixedHeight(height)
        label_thich.setFixedWidth(label_width)
        config_layout.addWidget(label_thich, 0, 0)
        config_layout.addWidget(self.bat_thich, 0, 1)

        self.ti_le_thich = QDoubleSpinBox()
        self.ti_le_thich.setRange(0.0, 1.0)
        self.ti_le_thich.setSingleStep(0.1)
        self.ti_le_thich.setFixedHeight(height)
        label_ti_le_thich = QLabel("Tỷ lệ thích tối đa:")
        label_ti_le_thich.setFixedHeight(height)
        label_ti_le_thich.setFixedWidth(label_width)
        config_layout.addWidget(label_ti_le_thich, 1, 0)
        config_layout.addWidget(self.ti_le_thich, 1, 1)

        self.bat_binh_luan = QCheckBox()
        self.bat_binh_luan.setFixedHeight(height)
        label_binh_luan = QLabel("Bật bình luận:")
        label_binh_luan.setFixedHeight(height)
        label_binh_luan.setFixedWidth(label_width)
        config_layout.addWidget(label_binh_luan, 2, 0)
        config_layout.addWidget(self.bat_binh_luan, 2, 1)

        self.ti_le_binh_luan = QDoubleSpinBox()
        self.ti_le_binh_luan.setRange(0.0, 1.0)
        self.ti_le_binh_luan.setSingleStep(0.1)
        self.ti_le_binh_luan.setFixedHeight(height)
        label_ti_le_bl = QLabel("Tỷ lệ bình luận tối đa:")
        label_ti_le_bl.setFixedHeight(height)
        label_ti_le_bl.setFixedWidth(label_width)
        config_layout.addWidget(label_ti_le_bl, 3, 0)
        config_layout.addWidget(self.ti_le_binh_luan, 3, 1)

        self.bat_follow = QCheckBox()
        self.bat_follow.setFixedHeight(height)
        label_follow = QLabel("Bật follow:")
        label_follow.setFixedHeight(height)
        label_follow.setFixedWidth(label_width)
        config_layout.addWidget(label_follow, 4, 0)
        config_layout.addWidget(self.bat_follow, 4, 1)

        self.ti_le_follow = QDoubleSpinBox()
        self.ti_le_follow.setRange(0.0, 1.0)
        self.ti_le_follow.setSingleStep(0.1)
        self.ti_le_follow.setFixedHeight(height)
        label_ti_le_follow = QLabel("Tỷ lệ follow tối đa:")
        label_ti_le_follow.setFixedHeight(height)
        label_ti_le_follow.setFixedWidth(label_width)
        config_layout.addWidget(label_ti_le_follow, 5, 0)
        config_layout.addWidget(self.ti_le_follow, 5, 1)

        self.bat_xem_live = QCheckBox()
        self.bat_xem_live.setFixedHeight(height)
        label_xem_live = QLabel("Bật xem live:")
        label_xem_live.setFixedHeight(height)
        label_xem_live.setFixedWidth(label_width)
        config_layout.addWidget(label_xem_live, 6, 0)
        config_layout.addWidget(self.bat_xem_live, 6, 1)

        self.ti_le_xem_live = QDoubleSpinBox()
        self.ti_le_xem_live.setRange(0.0, 1.0)
        self.ti_le_xem_live.setSingleStep(0.1)
        self.ti_le_xem_live.setFixedHeight(height)
        label_ti_le_live = QLabel("Tỷ lệ xem live tối đa:")
        label_ti_le_live.setFixedHeight(height)
        label_ti_le_live.setFixedWidth(label_width)
        config_layout.addWidget(label_ti_le_live, 7, 0)
        config_layout.addWidget(self.ti_le_xem_live, 7, 1)

        self.bat_kiem_tra_xuat_hien = QCheckBox()
        self.bat_kiem_tra_xuat_hien.setFixedHeight(height)
        label_kiem_tra = QLabel("Kiểm tra xuất hiện:")
        label_kiem_tra.setFixedHeight(height)
        label_kiem_tra.setFixedWidth(label_width)
        config_layout.addWidget(label_kiem_tra, 8, 0)
        config_layout.addWidget(self.bat_kiem_tra_xuat_hien, 8, 1)

        self.bat_chuyen_tai_khoan = QCheckBox()
        self.bat_chuyen_tai_khoan.setFixedHeight(height)
        label_chuyen_tai_khoan = QLabel("Bật chuyển tài khoản:")
        label_chuyen_tai_khoan.setFixedHeight(height)
        label_chuyen_tai_khoan.setFixedWidth(label_width)
        config_layout.addWidget(label_chuyen_tai_khoan, 9, 0)
        config_layout.addWidget(self.bat_chuyen_tai_khoan, 9, 1)

        self.chu_ky_thay_doi_tk = QSpinBox()
        self.chu_ky_thay_doi_tk.setRange(1, 100)
        self.chu_ky_thay_doi_tk.setFixedHeight(height)
        label_chu_ky_tk = QLabel("Chu kỳ thay đổi TK:")
        label_chu_ky_tk.setFixedHeight(height)
        label_chu_ky_tk.setFixedWidth(label_width)
        config_layout.addWidget(label_chu_ky_tk, 10, 0)
        config_layout.addWidget(self.chu_ky_thay_doi_tk, 10, 1)
        
        config_group.setLayout(config_layout)
        top_layout.addWidget(config_group)

        keyword_group = QGroupBox("Từ khóa bình luận")
        keyword_layout = QVBoxLayout()
        keyword_layout.setAlignment(Qt.AlignCenter)
        label_keywords = QLabel("Từ khóa (phẩy):")
        label_keywords.setFixedHeight(height)
        label_keywords.setFixedWidth(label_width)
        keyword_layout.addWidget(label_keywords)
        self.binh_luan_keywords = QLineEdit()
        self.binh_luan_keywords.setFixedHeight(40)
        keyword_layout.addWidget(self.binh_luan_keywords)
        keyword_group.setLayout(keyword_layout)
        top_layout.addWidget(keyword_group)

        count_group = QGroupBox("Số lượng")
        count_layout = QGridLayout()
        count_layout.setSpacing(10)
        self.so_video_toi_thieu = QSpinBox()
        self.so_video_toi_thieu.setRange(1, 100)
        self.so_video_toi_thieu.setFixedHeight(height)
        label_vid_min = QLabel("Số video tối thiểu:")
        label_vid_min.setFixedHeight(height)
        label_vid_min.setFixedWidth(label_width)
        count_layout.addWidget(label_vid_min, 0, 0)
        count_layout.addWidget(self.so_video_toi_thieu, 0, 1)

        self.so_video_toi_da = QSpinBox()
        self.so_video_toi_da.setRange(1, 100)
        self.so_video_toi_da.setFixedHeight(height)
        label_vid_max = QLabel("Số video tối đa:")
        label_vid_max.setFixedHeight(height)
        label_vid_max.setFixedWidth(label_width)
        count_layout.addWidget(label_vid_max, 1, 0)
        count_layout.addWidget(self.so_video_toi_da, 1, 1)

        self.so_live_toi_thieu = QSpinBox()
        self.so_live_toi_thieu.setRange(1, 100)
        self.so_live_toi_thieu.setFixedHeight(height)
        label_live_min = QLabel("Số live tối thiểu:")
        label_live_min.setFixedHeight(height)
        label_live_min.setFixedWidth(label_width)
        count_layout.addWidget(label_live_min, 2, 0)
        count_layout.addWidget(self.so_live_toi_thieu, 2, 1)

        self.so_live_toi_da = QSpinBox()
        self.so_live_toi_da.setRange(1, 100)
        self.so_live_toi_da.setFixedHeight(height)
        label_live_max = QLabel("Số live tối đa:")
        label_live_max.setFixedHeight(height)
        label_live_max.setFixedWidth(label_width)
        count_layout.addWidget(label_live_max, 3, 0)
        count_layout.addWidget(self.so_live_toi_da, 3, 1)

        self.so_lan_thu_lai = QSpinBox()
        self.so_lan_thu_lai.setRange(1, 10)
        self.so_lan_thu_lai.setFixedHeight(height)
        label_thu_lai = QLabel("Số lần thử lại:")
        label_thu_lai.setFixedHeight(height)
        label_thu_lai.setFixedWidth(label_width)
        count_layout.addWidget(label_thu_lai, 4, 0)
        count_layout.addWidget(self.so_lan_thu_lai, 4, 1)

        self.thoi_gian_xem_video_min = QSpinBox()
        self.thoi_gian_xem_video_min.setRange(1, 60)
        self.thoi_gian_xem_video_min.setFixedHeight(height)
        label_xem_video_min = QLabel("Thời gian xem video tối thiểu (giây):")
        label_xem_video_min.setFixedHeight(height)
        label_xem_video_min.setFixedWidth(label_width)
        count_layout.addWidget(label_xem_video_min, 5, 0)
        count_layout.addWidget(self.thoi_gian_xem_video_min, 5, 1)

        self.thoi_gian_xem_video_max = QSpinBox()
        self.thoi_gian_xem_video_max.setRange(1, 60)
        self.thoi_gian_xem_video_max.setFixedHeight(height)
        label_xem_video_max = QLabel("Thời gian xem video tối đa (giây):")
        label_xem_video_max.setFixedHeight(height)
        label_xem_video_max.setFixedWidth(label_width)
        count_layout.addWidget(label_xem_video_max, 6, 0)
        count_layout.addWidget(self.thoi_gian_xem_video_max, 6, 1)

        self.thoi_gian_xem_live_min = QSpinBox()
        self.thoi_gian_xem_live_min.setRange(1, 60)
        self.thoi_gian_xem_live_min.setFixedHeight(height)
        label_xem_live_min = QLabel("Thời gian xem live tối thiểu (giây):")
        label_xem_live_min.setFixedHeight(height)
        label_xem_live_min.setFixedWidth(label_width)
        count_layout.addWidget(label_xem_live_min, 7, 0)
        count_layout.addWidget(self.thoi_gian_xem_live_min, 7, 1)

        self.thoi_gian_xem_live_max = QSpinBox()
        self.thoi_gian_xem_live_max.setRange(1, 60)
        self.thoi_gian_xem_live_max.setFixedHeight(height)
        label_xem_live_max = QLabel("Thời gian xem live tối đa (giây):")
        label_xem_live_max.setFixedHeight(height)
        label_xem_live_max.setFixedWidth(label_width)
        count_layout.addWidget(label_xem_live_max, 8, 0)
        count_layout.addWidget(self.thoi_gian_xem_live_max, 8, 1)
        
        count_group.setLayout(count_layout)
        top_layout.addWidget(count_group)

        control_group = QGroupBox("Điều khiển")
        control_layout = QVBoxLayout()
        control_layout.setAlignment(Qt.AlignCenter)
        self.run_button = QPushButton("Chạy")
        self.run_button.setFixedWidth(100)
        self.run_button.setFixedHeight(height)
        self.run_button.clicked.connect(self.start_automation)
        control_layout.addWidget(self.run_button)
        self.stop_button = QPushButton("Dừng")
        self.stop_button.setFixedWidth(100)
        self.stop_button.setFixedHeight(height)
        self.stop_button.clicked.connect(self.stop_automation)
        control_layout.addWidget(self.stop_button)
        self.save_button = QPushButton("Lưu Config")
        self.save_button.setFixedWidth(100)
        self.save_button.setFixedHeight(height)
        self.save_button.clicked.connect(self.save_config)
        control_layout.addWidget(self.save_button)
        self.fullscreen_button = QPushButton("Full Screen")
        self.fullscreen_button.setFixedWidth(100)
        self.fullscreen_button.setFixedHeight(height)
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)
        control_layout.addWidget(self.fullscreen_button)
        control_group.setLayout(control_layout)
        top_layout.addWidget(control_group)

        main_layout.addLayout(top_layout)
        
        self.refresh_devices()
        self.load_phone_groups()

    def load_config(self):
        default_config = {
            'goi_tiktok': 'com.zhiliaoapp.musically',
            'do_phan_giai_muc_tieu': [1080, 1920],
            'bat_thich': True,
            'ti_le_thich': 1.0,
            'bat_binh_luan': True,
            'ti_le_binh_luan': 1.0,
            'danh_sach_binh_luan': ['hay quá', 'tuyệt vời'],
            'bat_follow': True,
            'ti_le_follow': 1.0,
            'bat_xem_live': True,
            'ti_le_xem_live': 1.0,
            'bat_kiem_tra_xuat_hien': True,
            'bat_chuyen_tai_khoan': True,
            'so_video_toi_thieu': 1,
            'so_video_toi_da': 2,
            'so_live_toi_thieu': 1,
            'so_live_toi_da': 2,
            'so_lan_thu_lai': 5,
            'chu_ky_thay_doi_tk': 1,
            'thoi_gian_vuot': [0.03, 0.08],
            'thoi_gian_xem_video_min': 5,
            'thoi_gian_xem_video_max': 15,
            'thoi_gian_xem_live_min': 5,
            'thoi_gian_xem_live_max': 15
        }
        config_path = os.path.join(get_base_path(), 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.bat_thich.setChecked(config.get('bat_thich', default_config['bat_thich']))
                self.ti_le_thich.setValue(config.get('ti_le_thich', default_config['ti_le_thich']))
                self.bat_binh_luan.setChecked(config.get('bat_binh_luan', default_config['bat_binh_luan']))
                self.ti_le_binh_luan.setValue(config.get('ti_le_binh_luan', default_config['ti_le_binh_luan']))
                self.bat_follow.setChecked(config.get('bat_follow', default_config['bat_follow']))
                self.ti_le_follow.setValue(config.get('ti_le_follow', default_config['ti_le_follow']))
                self.bat_xem_live.setChecked(config.get('bat_xem_live', default_config['bat_xem_live']))
                self.ti_le_xem_live.setValue(config.get('ti_le_xem_live', default_config['ti_le_xem_live']))
                self.bat_kiem_tra_xuat_hien.setChecked(config.get('bat_kiem_tra_xuat_hien', default_config['bat_kiem_tra_xuat_hien']))
                self.bat_chuyen_tai_khoan.setChecked(config.get('bat_chuyen_tai_khoan', default_config['bat_chuyen_tai_khoan']))
                self.so_video_toi_thieu.setValue(config.get('so_video_toi_thieu', default_config['so_video_toi_thieu']))
                self.so_video_toi_da.setValue(config.get('so_video_toi_da', default_config['so_video_toi_da']))
                self.so_live_toi_thieu.setValue(config.get('so_live_toi_thieu', default_config['so_live_toi_thieu']))
                self.so_live_toi_da.setValue(config.get('so_live_toi_da', default_config['so_live_toi_da']))
                self.so_lan_thu_lai.setValue(config.get('so_lan_thu_lai', default_config['so_lan_thu_lai']))
                self.chu_ky_thay_doi_tk.setValue(config.get('chu_ky_thay_doi_tk', default_config['chu_ky_thay_doi_tk']))
                self.thoi_gian_xem_video_min.setValue(config.get('thoi_gian_xem_video_min', default_config['thoi_gian_xem_video_min']))
                self.thoi_gian_xem_video_max.setValue(config.get('thoi_gian_xem_video_max', default_config['thoi_gian_xem_video_max']))
                self.thoi_gian_xem_live_min.setValue(config.get('thoi_gian_xem_live_min', default_config['thoi_gian_xem_live_min']))
                self.thoi_gian_xem_live_max.setValue(config.get('thoi_gian_xem_live_max', default_config['thoi_gian_xem_live_max']))
                binh_luan_list = config.get('danh_sach_binh_luan', default_config['danh_sach_binh_luan'])
                self.binh_luan_keywords.setText(', '.join(binh_luan_list))
                for row in range(self.device_table.rowCount()):
                    self.device_table.item(row, 2).setText("Tải config thành công từ config.json")
            except Exception as e:
                for row in range(self.device_table.rowCount()):
                    self.device_table.item(row, 2).setText(f"Lỗi khi tải config: {str(e)}. Sử dụng cấu hình mặc định.")
                self.apply_default_config(default_config)
        else:
            for row in range(self.device_table.rowCount()):
                self.device_table.item(row, 2).setText("Không tìm thấy config.json. Sử dụng cấu hình mặc định.")
            self.apply_default_config(default_config)

    def save_config(self):
        config = self.get_config()
        config_path = os.path.join(get_base_path(), 'config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            for row in range(self.device_table.rowCount()):
                self.device_table.item(row, 2).setText("Lưu config thành công vào config.json")
        except Exception as e:
            for row in range(self.device_table.rowCount()):
                self.device_table.item(row, 2).setText(f"Lỗi khi lưu config: {str(e)}")

    def apply_default_config(self, config):
        self.bat_thich.setChecked(config['bat_thich'])
        self.ti_le_thich.setValue(config['ti_le_thich'])
        self.bat_binh_luan.setChecked(config['bat_binh_luan'])
        self.ti_le_binh_luan.setValue(config['ti_le_binh_luan'])
        self.bat_follow.setChecked(config['bat_follow'])
        self.ti_le_follow.setValue(config['ti_le_follow'])
        self.bat_xem_live.setChecked(config['bat_xem_live'])
        self.ti_le_xem_live.setValue(config['ti_le_xem_live'])
        self.bat_kiem_tra_xuat_hien.setChecked(config['bat_kiem_tra_xuat_hien'])
        self.bat_chuyen_tai_khoan.setChecked(config['bat_chuyen_tai_khoan'])
        self.so_video_toi_thieu.setValue(config['so_video_toi_thieu'])
        self.so_video_toi_da.setValue(config['so_video_toi_da'])
        self.so_live_toi_thieu.setValue(config['so_live_toi_thieu'])
        self.so_live_toi_da.setValue(config['so_live_toi_da'])
        self.so_lan_thu_lai.setValue(config['so_lan_thu_lai'])
        self.chu_ky_thay_doi_tk.setValue(config['chu_ky_thay_doi_tk'])
        self.thoi_gian_xem_video_min.setValue(config['thoi_gian_xem_video_min'])
        self.thoi_gian_xem_video_max.setValue(config['thoi_gian_xem_video_max'])
        self.thoi_gian_xem_live_min.setValue(config['thoi_gian_xem_live_min'])
        self.thoi_gian_xem_live_max.setValue(config['thoi_gian_xem_live_max'])
        self.binh_luan_keywords.setText(', '.join(config['danh_sach_binh_luan']))

    def save_phone_group(self):
        selected_devices = []
        for row in range(self.device_table.rowCount()):
            checkbox = self.device_table.cellWidget(row, 0)
            if checkbox.isChecked():
                selected_devices.append(self.device_table.item(row, 1).text())
        if not selected_devices:
            for row in range(self.device_table.rowCount()):
                self.device_table.item(row, 2).setText("Vui lòng chọn ít nhất một thiết bị để lưu nhóm!")
            return
        group_name, ok = QInputDialog.getText(self, "Lưu Nhóm Phone", "Nhập tên nhóm:")
        if ok and group_name:
            try:
                groups = {}
                phone_groups_path = os.path.join(get_base_path(), 'phone_groups.json')
                if os.path.exists(phone_groups_path):
                    with open(phone_groups_path, 'r', encoding='utf-8') as f:
                        groups = json.load(f)
                groups[group_name] = selected_devices
                with open(phone_groups_path, 'w', encoding='utf-8') as f:
                    json.dump(groups, f, indent=4, ensure_ascii=False)
                for row in range(self.device_table.rowCount()):
                    self.device_table.item(row, 2).setText(f"Lưu nhóm phone '{group_name}' thành công!")
                self.load_phone_groups()
            except Exception as e:
                for row in range(self.device_table.rowCount()):
                    self.device_table.item(row, 2).setText(f"Lỗi khi lưu nhóm phone: {str(e)}")

    def load_phone_groups(self):
        self.load_group_list.clear()
        phone_groups_path = os.path.join(get_base_path(), 'phone_groups.json')
        if os.path.exists(phone_groups_path):
            try:
                with open(phone_groups_path, 'r', encoding='utf-8') as f:
                    groups = json.load(f)
                for group_name in groups.keys():
                    self.load_group_list.addItem(group_name)
                for row in range(self.device_table.rowCount()):
                    self.device_table.item(row, 2).setText("Tải danh sách nhóm phone thành công!")
            except Exception as e:
                for row in range(self.device_table.rowCount()):
                    self.device_table.item(row, 2).setText(f"Lỗi khi tải danh sách nhóm phone: {str(e)}")
        self.update_selected_groups_label()

    def update_selected_groups_label(self):
        selected_groups = [item.text() for item in self.load_group_list.selectedItems()]
        if selected_groups:
            self.selected_groups_label.setText(f"Nhóm đã chọn: {', '.join(selected_groups)}")
        else:
            self.selected_groups_label.setText("Nhóm đã chọn: Không có")

    def toggle_fullscreen(self):
        self.showMaximized()

    def refresh_devices(self):
        global device_logs
        self.device_table.setRowCount(0)
        device_logs.clear()
        devices = lay_danh_sach_thiet_bi()
        for row, device in enumerate(devices):
            self.device_table.insertRow(row)
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            checkbox.setFixedHeight(30)
            self.device_table.setCellWidget(row, 0, checkbox)
            device_item = QTableWidgetItem(device)
            device_item.setFlags(device_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(row, 1, device_item)
            log_item = QTableWidgetItem("")
            log_item.setFlags(log_item.flags() & ~Qt.ItemIsEditable)
            self.device_table.setItem(row, 2, log_item)
        self.device_table.resizeRowsToContents()

    def select_all_devices(self):
        for row in range(self.device_table.rowCount()):
            checkbox = self.device_table.cellWidget(row, 0)
            checkbox.setChecked(True)

    def deselect_all_devices(self):
        for row in range(self.device_table.rowCount()):
            checkbox = self.device_table.cellWidget(row, 0)
            checkbox.setChecked(False)

    def mouseDoubleClickEvent(self, event):
        if event.pos().y() < 100:
            self.select_all_devices()

    def get_config(self):
        return {
            'goi_tiktok': CAU_HINH['goi_tiktok'],
            'do_phan_giai_muc_tieu': CAU_HINH['do_phan_giai_muc_tieu'],
            'bat_thich': self.bat_thich.isChecked(),
            'ti_le_thich': self.ti_le_thich.value(),
            'bat_binh_luan': self.bat_binh_luan.isChecked(),
            'ti_le_binh_luan': self.ti_le_binh_luan.value(),
            'danh_sach_binh_luan': [x.strip() for x in self.binh_luan_keywords.text().split(',') if x.strip()],
            'bat_follow': self.bat_follow.isChecked(),
            'ti_le_follow': self.ti_le_follow.value(),
            'bat_xem_live': self.bat_xem_live.isChecked(),
            'ti_le_xem_live': self.ti_le_xem_live.value(),
            'bat_kiem_tra_xuat_hien': self.bat_kiem_tra_xuat_hien.isChecked(),
            'bat_chuyen_tai_khoan': self.bat_chuyen_tai_khoan.isChecked(),
            'so_video_toi_thieu': self.so_video_toi_thieu.value(),
            'so_video_toi_da': self.so_video_toi_da.value(),
            'so_live_toi_thieu': self.so_live_toi_thieu.value(),
            'so_live_toi_da': self.so_live_toi_da.value(),
            'so_lan_thu_lai': self.so_lan_thu_lai.value(),
            'chu_ky_thay_doi_tk': self.chu_ky_thay_doi_tk.value(),
            'thoi_gian_vuot': [0.03, 0.08],
            'thoi_gian_xem_video_min': self.thoi_gian_xem_video_min.value(),
            'thoi_gian_xem_video_max': self.thoi_gian_xem_video_max.value(),
            'thoi_gian_xem_live_min': self.thoi_gian_xem_live_min.value(),
            'thoi_gian_xem_live_max': self.thoi_gian_xem_live_max.value()
        }

    def start_automation(self):
        global CAU_HINH, running, stop_event
        CAU_HINH = self.get_config()
        stop_event.clear()
        selected_devices = []
        for row in range(self.device_table.rowCount()):
            checkbox = self.device_table.cellWidget(row, 0)
            if checkbox.isChecked():
                selected_devices.append(self.device_table.item(row, 1).text())
        if not selected_devices:
            for row in range(self.device_table.rowCount()):
                self.device_table.item(row, 2).setText("Vui lòng chọn ít nhất một thiết bị!")
            return
        self.running = True
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        threads = []
        for serial in selected_devices:
            thread = threading.Thread(target=mo_tiktok_thiet_bi, args=(serial, self.device_table))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if stop_event.is_set():
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            return

        threading.Thread(target=chay_dong_loat_thiet_bi, args=(selected_devices, lambda: not stop_event.is_set())).start()

    def stop_automation(self):
        global running, stop_event
        self.running = False
        stop_event.set()
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        for row in range(self.device_table.rowCount()):
            self.device_table.item(row, 2).setText("Đã dừng automation!")

def mo_tiktok_thiet_bi(serial, device_table):
    try:
        d = u2.connect(serial)
        row = [r for r in range(device_table.rowCount()) if device_table.item(r, 1).text() == serial][0]
        sys.stdout = TextEditLogger(serial, device_table, row)
        print(f"Tắt TikTok trên thiết bị {serial}")
        d.app_stop(CAU_HINH['goi_tiktok'])
        safe_sleep(0.1)
        if stop_event.is_set():
            return
        print(f"Mở TikTok trên thiết bị {serial}")
        d.app_start(CAU_HINH['goi_tiktok'])
        for _ in range(100):
            if stop_event.is_set():
                return
            safe_sleep(0.1)
    except Exception as e:
        print(f"Lỗi khi đóng/mở TikTok trên thiết bị {serial}: {str(e)}")
        print(f"Thiết bị {serial} đã mất kết nối, yêu cầu kiểm tra quyền truyền tệp")

def safe_sleep(seconds):
    for _ in range(int(seconds * 10)):
        if stop_event.is_set():
            return
        time.sleep(0.1)

def cho_xuat_hien(d, selector, timeout=5):
    if stop_event.is_set():
        return False
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if stop_event.is_set():
                return False
            if selector.exists(timeout=0.1):
                return True
            time.sleep(0.1)
        return False
    except Exception as e:
        print(f"Lỗi kiểm tra xuất hiện: {str(e)}")
        return False

def lay_danh_sach_thiet_bi():
    try:
        devices = [d.serial for d in adb.device_list()]
        return devices
    except Exception as e:
        print(f"Lỗi khi lấy danh sách thiết bị: {str(e)}")
        return []

def tinh_toa_do(x, y, w, h):
    w0, h0 = CAU_HINH['do_phan_giai_muc_tieu']
    return int(x * w / w0), int(y * h / h0)

def kiem_tra_tiktok(d):
    if stop_event.is_set():
        return False
    try:
        package = d.app_current().get('package', '')
        return package == CAU_HINH['goi_tiktok']
    except Exception as e:
        print(f"Lỗi kiểm tra TikTok: {str(e)}")
        return False

def mo_tiktok(d):
    if stop_event.is_set():
        return
    try:
        d.app_stop(CAU_HINH['goi_tiktok'])
        safe_sleep(2)
        if stop_event.is_set():
            return
        d.app_start(CAU_HINH['goi_tiktok'])
        safe_sleep(10)
    except Exception as e:
        print(f"Lỗi mở TikTok: {str(e)}")

def kiem_tra_for_you(d):
    if stop_event.is_set():
        return False
    try:
        for id in [f"{CAU_HINH['goi_tiktok']}:id/cnv"]:
            if cho_xuat_hien(d, d(resourceId=id)):
                return True
        return cho_xuat_hien(d, d(text="For You"))
    except Exception as e:
        print(f"Lỗi kiểm tra For You: {str(e)}")
        return False

def kiem_tra_dang_xem_live(d):
    if stop_event.is_set():
        return False
    try:
        return not cho_xuat_hien(d, d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/h3j"), timeout=1)
    except Exception as e:
        print(f"Lỗi kiểm tra Live: {str(e)}")
        return False

def dam_bao_tiktok_mo(d, serial):
    for _ in range(CAU_HINH['so_lan_thu_lai']):
        if stop_event.is_set():
            return False
        try:
            if not kiem_tra_tiktok(d):
                mo_tiktok(d)
            for id in ['bte', 'ay8']:
                selector = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/{id}")
                while cho_xuat_hien(d, selector):
                    if stop_event.is_set():
                        return False
                    selector.click()
                    safe_sleep(2)
                    if not selector.exists(timeout=1):
                        break
            for id in [f"{CAU_HINH['goi_tiktok']}:id/close", "android:id/button1"]:
                selector = d(resourceId=id)
                if cho_xuat_hien(d, selector):
                    if stop_event.is_set():
                        return False
                    selector.click()
                    safe_sleep(2)
            if kiem_tra_for_you(d):
                return True
            d.press("back")
            safe_sleep(3)
        except Exception as e:
            print(f"Lỗi đảm bảo TikTok mở trên thiết bị {serial}: {str(e)}")
            print(f"Thiết bị {serial} đã mất kết nối, yêu cầu kiểm tra quyền truyền tệp")
            return False
    return False

def thich_video(d, ti_le_thich):
    if stop_event.is_set():
        return
    if CAU_HINH['bat_thich'] and random.random() < ti_le_thich:
        try:
            selector = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/cnv")
            if cho_xuat_hien(d, selector):
                print("Thích video")
                selector.click()
                safe_sleep(0.5)
        except Exception as e:
            print(f"Lỗi khi thích video: {str(e)}")

def follow_tai_khoan(d, ti_le_follow, serial):
    if stop_event.is_set():
        return
    if CAU_HINH['bat_follow'] and random.random() < ti_le_follow:
        try:
            selector = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/e1n")
            if cho_xuat_hien(d, selector, timeout=3):
                print(f"Follow tài khoản trên thiết bị {serial}")
                selector.click()
                safe_sleep(1)
                return True
            selector_text = d(text="Follow")
            if cho_xuat_hien(d, selector_text, timeout=3):
                print(f"Follow tài khoản bằng text trên thiết bị {serial}")
                selector_text.click()
                safe_sleep(1)
                return True
            print(f"Không tìm thấy nút follow trên thiết bị {serial}")
            return False
        except Exception as e:
            print(f"Lỗi khi follow tài khoản trên thiết bị {serial}: {str(e)}")
            return False

def binh_luan(d, serial, ti_le_binh_luan):
    if stop_event.is_set():
        return False
    if not (CAU_HINH['bat_binh_luan'] and random.random() < ti_le_binh_luan):
        return True
    try:
        nut_binh_luan = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/buv")
        if not cho_xuat_hien(d, nut_binh_luan, timeout=5):
            print(f"Không tìm thấy nút bình luận trên thiết bị {serial}")
            return False
        print(f"Nhấn nút bình luận trên thiết bị {serial}")
        nut_binh_luan.click()
        safe_sleep(3)
        if stop_event.is_set():
            return False
        khung_nhap = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/bui")
        if not cho_xuat_hien(d, khung_nhap, timeout=5):
            print(f"Không tìm thấy khung nhập bình luận trên thiết bị {serial}")
            return False
        print(f"Nhấn khung nhập bình luận trên thiết bị {serial}")
        khung_nhap.click()
        safe_sleep(1)
        if stop_event.is_set():
            return False
        binh_luan_text = random.choice(CAU_HINH['danh_sach_binh_luan'])
        print(f"Nhập bình luận '{binh_luan_text}' trên thiết bị {serial}")
        try:
            khung_nhap.set_text(binh_luan_text)
            safe_sleep(2)
        except Exception:
            print(f"Lỗi nhập bình luận trên thiết bị {serial}")
            return False
        if stop_event.is_set():
            return False
        nut_gui = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/bwe")
        if not cho_xuat_hien(d, nut_gui, timeout=30):
            print(f"Không tìm thấy nút gửi bình luận trên thiết bị {serial} sau 30 giây")
            return False
        print(f"Gửi bình luận trên thiết bị {serial}")
        nut_gui.click()
        safe_sleep(2)
        if stop_event.is_set():
            return False
        if cho_xuat_hien(d, d(text=binh_luan_text), timeout=5):
            print(f"Bình luận '{binh_luan_text}' đã xuất hiện trên thiết bị {serial}")
        elif cho_xuat_hien(d, d(text="Bình luận sẽ xuất hiện tại đây"), timeout=2):
            print(f"Bình luận '{binh_luan_text}' không thành công trên thiết bị {serial}")
        nut_dong = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/aio")
        start_time = time.time()
        while nut_dong.exists(timeout=1) and time.time() - start_time < 45:
            if stop_event.is_set():
                return False
            print(f"Đóng khung bình luận trên thiết bị {serial}")
            nut_dong.click()
            safe_sleep(1)
        if time.time() - start_time >= 45:
            print(f"Vẫn ở khung bình luận sau 45 giây trên thiết bị {serial}, nhấn nút trở về")
            for _ in range(2):
                d.press("back")
                safe_sleep(1)
            return False
        print(f"Khung bình luận đã đóng trên thiết bị {serial}")
        return True
    except Exception as e:
        print(f"Lỗi khi bình luận trên thiết bị {serial}: {str(e)}")
        return False

def vuot_video(d, w, h):
    if stop_event.is_set():
        return
    try:
        print("Vuốt video")
        x1 = random.randint(400, 600)
        y1 = random.randint(1400, 1600)
        x2 = x1 + random.randint(-20, 20)
        y2 = random.randint(50, 150)
        x1, y1 = tinh_toa_do(x1, y1, w, h)
        x2, y2 = tinh_toa_do(x2, y2, w, h)
        t = random.uniform(*CAU_HINH['thoi_gian_vuot'])
        d.swipe(x1, y1, x2, y2, t)
        safe_sleep(random.uniform(CAU_HINH['thoi_gian_xem_video_min'], CAU_HINH['thoi_gian_xem_video_max']))
    except Exception as e:
        print(f"Lỗi khi vuốt video: {str(e)}")

def xem_live(d, w, h, serial, running, ti_le_xem_live):
    if stop_event.is_set():
        return False
    try:
        if random.random() < ti_le_xem_live:
            selector = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/jg3")
            if not cho_xuat_hien(d, selector):
                return False
            print(f"Nhấn nút Live trên thiết bị {serial}")
            selector.click()
            safe_sleep(5)
            if stop_event.is_set():
                return False
            n = random.randint(CAU_HINH['so_live_toi_thieu'], CAU_HINH['so_live_toi_da'])
            for i in range(n):
                if stop_event.is_set():
                    return False
                print(f"Live {i+1}/{n} trên thiết bị {serial}")
                x1 = random.randint(400, 600)
                y1 = random.randint(1400, 1600)
                x2 = x1 + random.randint(-20, 20)
                y2 = random.randint(30, 100)
                x1, y1 = tinh_toa_do(x1, y1, w, h)
                x2, y2 = tinh_toa_do(x2, y2, w, h)
                t = random.uniform(*CAU_HINH['thoi_gian_vuot'])
                d.swipe(x1, y1, x2, y2, t)
                safe_sleep(random.uniform(CAU_HINH['thoi_gian_xem_live_min'], CAU_HINH['thoi_gian_xem_live_max']))
                if stop_event.is_set():
                    return False
            selector = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/bpr")
            if cho_xuat_hien(d, selector):
                print(f"Đóng live trên thiết bị {serial}")
                selector.click()
                safe_sleep(5)
                if stop_event.is_set():
                    return False
                return True
            return False
        return False
    except Exception as e:
        print(f"Lỗi khi xem live trên thiết bị {serial}: {str(e)}")
        return False

def xu_ly_video(d, w, h, serial, running, ti_le_thich, ti_le_binh_luan, ti_le_follow):
    if stop_event.is_set():
        return False
    try:
        if not dam_bao_tiktok_mo(d, serial):
            return False
        n = random.randint(CAU_HINH['so_video_toi_thieu'], CAU_HINH['so_video_toi_da'])
        for i in range(n):
            if stop_event.is_set():
                return False
            print(f"Video {i+1}/{n} trên thiết bị {serial}")
            follow_tai_khoan(d, ti_le_follow, serial)
            if stop_event.is_set():
                return False
            thich_video(d, ti_le_thich)
            if stop_event.is_set():
                return False
            if not binh_luan(d, serial, ti_le_binh_luan):
                continue
            if stop_event.is_set():
                return False
            vuot_video(d, w, h)
            if stop_event.is_set():
                return False
        return True
    except Exception as e:
        print(f"Lỗi khi xử lý video trên thiết bị {serial}: {str(e)}")
        print(f"Thiết bị {serial} đã mất kết nối, yêu cầu kiểm tra quyền truyền tệp")
        return False

def chuyen_tai_khoan(d, serial):
    if stop_event.is_set():
        return False
    try:
        if kiem_tra_dang_xem_live(d):
            return False
        profile_btn = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/h3j")
        if cho_xuat_hien(d, profile_btn):
            profile_btn.click()
            safe_sleep(2)
        else:
            return False
        if stop_event.is_set():
            return False
        switch_btn = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/hol")
        if cho_xuat_hien(d, switch_btn):
            switch_btn.click()
            safe_sleep(2)
        else:
            return False
        if stop_event.is_set():
            return False
        users = d(resourceId=f"{CAU_HINH['goi_tiktok']}:id/gg_")
        if len(users) > 1:
            current_text = users[0].get_text()
            next_user = users[1]
            if next_user.get_text() != current_text:
                print(f"Chuyển sang tài khoản: {next_user.get_text()} trên thiết bị {serial}")
                next_user.click()
                safe_sleep(5)
                if stop_event.is_set():
                    return False
                d.press("back")
                safe_sleep(2)
                return True
            return False
        return False
    except Exception as e:
        print(f"Lỗi khi chuyển tài khoản trên thiết bị {serial}: {str(e)}")
        print(f"Thiết bị {serial} đã mất kết nối, yêu cầu kiểm tra quyền truyền tệp")
        return False

def xu_ly_noi_dung(d, w, h, serial, running, ti_le_thich, ti_le_binh_luan, ti_le_follow, ti_le_xem_live):
    chu_ky_count = 0
    while running() and not stop_event.is_set():
        print(f"Bắt đầu chu kỳ {chu_ky_count + 1} trên thiết bị {serial}")
        try:
            if CAU_HINH.get('bat_thich', False) or CAU_HINH.get('bat_binh_luan', False) or CAU_HINH.get('bat_follow', False):
                if not xu_ly_video(d, w, h, serial, running, ti_le_thich, ti_le_binh_luan, ti_le_follow):
                    safe_sleep(10)
                    if stop_event.is_set():
                        return False
                    continue
            if CAU_HINH.get('bat_xem_live', False):
                if xem_live(d, w, h, serial, running, ti_le_xem_live):
                    print(f"Hoàn thành xem live trên thiết bị {serial}")
            chu_ky_count += 1
            if CAU_HINH.get('bat_chuyen_tai_khoan', False) and chu_ky_count >= CAU_HINH['chu_ky_thay_doi_tk']:
                if not kiem_tra_dang_xem_live(d):
                    if chuyen_tai_khoan(d, serial):
                        chu_ky_count = 0
                        print(f"Hoàn thành chuyển tài khoản trên thiết bị {serial}")
            if not (CAU_HINH.get('bat_thich', False) or CAU_HINH.get('bat_binh_luan', False) or CAU_HINH.get('bat_follow', False) or CAU_HINH.get('bat_xem_live', False)):
                safe_sleep(random.uniform(5, 10))
                if stop_event.is_set():
                    return False
        except Exception as e:
            print(f"Lỗi trong xu_ly_noi_dung trên thiết bị {serial}: {str(e)}")
            print(f"Thiết bị {serial} đã mất kết nối, yêu cầu kiểm tra quyền truyền tệp")
            return False
    return True

def ket_noi_thiet_bi(serial):
    for _ in range(CAU_HINH['so_lan_thu_lai']):
        if stop_event.is_set():
            return None, None, None
        try:
            d = u2.connect(serial)
            info = d.info
            print(f"Kết nối lại thành công thiết bị {serial}")
            return d, info['displayWidth'], info['displayHeight']
        except Exception as e:
            print(f"Lỗi khi kết nối thiết bị {serial}: {str(e)}")
            print(f"Thiết bị {serial} đã mất kết nối, yêu cầu kiểm tra quyền truyền tệp")
            safe_sleep(3)
    print(f"Không thể kết nối lại thiết bị {serial}, dừng automation")
    return None, None, None

def xu_ly_thiet_bi(serial, running):
    ti_le_thich = random.uniform(0.0, CAU_HINH.get('ti_le_thich', 1.0))
    ti_le_binh_luan = random.uniform(0.0, CAU_HINH.get('ti_le_binh_luan', 1.0))
    ti_le_follow = random.uniform(0.0, CAU_HINH.get('ti_le_follow', 1.0))
    ti_le_xem_live = random.uniform(0.0, CAU_HINH.get('ti_le_xem_live', 1.0))
    print(f"Tỷ lệ cho thiết bị {serial}: thích={ti_le_thich:.2f}, bình luận={ti_le_binh_luan:.2f}, follow={ti_le_follow:.2f}, xem live={ti_le_xem_live:.2f}")
    while running() and not stop_event.is_set():
        d, w, h = ket_noi_thiet_bi(serial)
        if not d:
            break
        if not xu_ly_noi_dung(d, w, h, serial, running, ti_le_thich, ti_le_binh_luan, ti_le_follow, ti_le_xem_live):
            safe_sleep(10)
            continue
        safe_sleep(10)

def chay_dong_loat_thiet_bi(devices, running):
    print("Chạy đồng loạt các thiết bị")
    threads = []
    for serial in devices:
        thread = threading.Thread(target=xu_ly_thiet_bi, args=(serial, running))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TikTokApp()
    window.show()
    sys.exit(app.exec_())