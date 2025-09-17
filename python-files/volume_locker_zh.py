import sys
import time
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSlider, QPushButton, QComboBox, QLabel, 
                             QMenuBar, QAction, QMessageBox)
from PyQt5.QtCore import Qt
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import psutil
import comtypes

class VolumeLocker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 音量锁定工具")
        self.setGeometry(100, 100, 400, 300)
        self.locked = False
        self.target_volume = 50  # 默认音量 (0-100)
        self.selected_app = "系统音量"
        self.init_ui()
        self.start_volume_monitor()

    def init_ui(self):
        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        help_menu = menubar.addMenu("帮助")

        # 文件菜单项
        refresh_action = QAction("刷新应用程序列表", self)
        refresh_action.triggered.connect(self.refresh_app_list)
        file_menu.addAction(refresh_action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 帮助菜单项
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # 主界面布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # 音量滑块
        self.slider_label = QLabel(f"目标音量: {self.target_volume}%")
        layout.addWidget(self.slider_label)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.target_volume)
        self.volume_slider.valueChanged.connect(self.update_volume)
        layout.addWidget(self.volume_slider)

        # 应用程序选择
        self.app_label = QLabel("选择应用程序:")
        layout.addWidget(self.app_label)
        self.app_combo = QComboBox()
        self.app_combo.addItem("系统音量")
        self.populate_app_list()
        self.app_combo.currentTextChanged.connect(self.update_selected_app)
        layout.addWidget(self.app_combo)

        # 锁定/解锁按钮
        button_layout = QHBoxLayout()
        self.lock_button = QPushButton("锁定音量")
        self.lock_button.clicked.connect(self.lock_volume)
        button_layout.addWidget(self.lock_button)
        self.unlock_button = QPushButton("解锁音量")
        self.unlock_button.clicked.connect(self.unlock_volume)
        self.unlock_button.setEnabled(False)
        button_layout.addWidget(self.unlock_button)
        layout.addLayout(button_layout)

        # 状态标签
        self.status_label = QLabel("状态: 未锁定")
        layout.addWidget(self.status_label)

    def populate_app_list(self):
        # 获取运行中的应用程序音频会话
        self.app_combo.clear()
        self.app_combo.addItem("系统音量")
        sessions = AudioUtilities.GetAllSessions()
        app_names = set()
        for session in sessions:
            if session.Process:
                app_names.add(session.Process.name())
        for app in sorted(app_names):
            self.app_combo.addItem(app)

    def refresh_app_list(self):
        # 刷新应用程序列表
        self.populate_app_list()
        self.status_label.setText("状态: 应用程序列表已刷新")

    def show_about(self):
        # 显示关于对话框
        QMessageBox.information(self, "关于", "Windows 音量锁定工具\n版本: 1.0\n作者: xAI Assistant\n用于锁定系统或应用程序音量。")

    def update_volume(self, value):
        self.target_volume = value
        self.slider_label.setText(f"目标音量: {value}%")
        if self.locked:
            self.set_volume(value)

    def update_selected_app(self, app_name):
        self.selected_app = app_name

    def set_volume(self, volume):
        # 将 0-100 转换为 0.0-1.0
        volume_normalized = volume / 100.0
        sessions = AudioUtilities.GetAllSessions()
        if self.selected_app == "系统音量":
            # 控制系统音量
            for session in sessions:
                if session.Process is None:  # 系统音量
                    volume_interface = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume_interface.SetMasterVolume(volume_normalized, None)
        else:
            # 控制特定应用程序音量
            for session in sessions:
                if session.Process and session.Process.name() == self.selected_app:
                    volume_interface = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume_interface.SetMasterVolume(volume_normalized, None)

    def lock_volume(self):
        self.locked = True
        self.lock_button.setEnabled(False)
        self.unlock_button.setEnabled(True)
        self.status_label.setText(f"状态: 已锁定在 {self.target_volume}%")
        self.set_volume(self.target_volume)

    def unlock_volume(self):
        self.locked = False
        self.lock_button.setEnabled(True)
        self.unlock_button.setEnabled(False)
        self.status_label.setText("状态: 未锁定")

    def monitor_volume(self):
        while True:
            if self.locked:
                self.set_volume(self.target_volume)
            time.sleep(1)

    def start_volume_monitor(self):
        monitor_thread = threading.Thread(target=self.monitor_volume, daemon=True)
        monitor_thread.start()

    def closeEvent(self, event):
        comtypes.CoUninitialize()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VolumeLocker()
    window.show()
    sys.exit(app.exec_())