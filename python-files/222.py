import winreg
import os
import psutil
import sys
import time
import subprocess  # 新增：用于无窗口执行命令
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QSlider, QLabel, QFrame, QSpacerItem, QSizePolicy,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, pyqtSlot
from PyQt5.QtGui import QFont

# ========== 数据采集函数（保持不变） ==========
def get_cpu_temp():
    try:
        key_path = r"Software\FinalWire\AIDA64\SensorValues"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "Value.TCPUPKG")
            return float(value)
    except Exception:
        return None

def get_gpu_temp():
    try:
        key_path = r"Software\FinalWire\AIDA64\SensorValues"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "Value.TGPU1")
            return float(value)
    except Exception:
        return None

def get_cpu_usage(interval: float = 0.1) -> float:
    try:
        return round(psutil.cpu_percent(interval=interval), 1)
    except Exception:
        return -1.0


def get_command_output(command, timeout=1.0):
    """无窗口执行命令并获取输出"""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW  # 关键修复点：禁止创建窗口
        )
        stdout, _ = process.communicate(timeout=timeout)
        return stdout.decode('utf-8').strip()
    except Exception as e:
        print(f"命令执行失败: {str(e)}")
        return None

# ===== 修改后的GPU使用率获取函数 =====
def get_gpu_usage(timeout: float = 1.0) -> float:
    """通过nvidia-smi获取GPU利用率（兼容多显卡）"""
    try:
        # 无窗口执行命令，指定目标GPU索引（默认首张显卡）
        output = get_command_output(
            "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits",
            timeout=timeout
        )
        if output:
            # 处理多显卡：取第一张卡的数据
            usage_str = output.split('\n')[0].strip()
            return float(usage_str)  # 直接转换为浮点数
    except Exception as e:
        print(f"GPU利用率获取失败: {str(e)}")
    return -1.0  # 错误标识




# ========== 风扇模式函数（核心修改：无窗口执行命令） ==========
def run_command(command):
    """无窗口执行外部命令"""
    try:
        # CREATE_NO_WINDOW 标志确保不显示CMD窗口
        subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,  # 重定向输出，避免窗口
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW  # Windows专用：无窗口
        )
    except Exception as e:
        print(f"命令执行失败: {str(e)}")  # 仅调试用，可注释

def fanConfig1(): 
    print("安静模式")
    # 替换os.system为无窗口执行（取消注释时生效）
    # run_command("FanControl.exe -c QuietMode.json")

def fanConfig2(): 
    print("普通模式")
    # run_command("FanControl.exe -c NormalMode.json")

def fanConfig3(): 
    print("性能模式")
    # run_command("FanControl.exe -c PerfMode.json")

def fanConfig4(): 
    print("极限模式")
    # run_command("FanControl.exe -c CrazyMode.json")

# ========== 后台数据采集线程（保持不变） ==========
class SensorThread(QThread):
    data_updated = pyqtSignal(float, float, float, float)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = True
        self._interval = 1.0
    
    def run(self):
        while self._running:
            try:
                cpu_temp = get_cpu_temp()
                gpu_temp = get_gpu_temp()
                cpu_usage = get_cpu_usage()
                gpu_usage = get_gpu_usage()
                
                cpu_temp_val = cpu_temp if cpu_temp is not None else -1.0
                gpu_temp_val = gpu_temp if gpu_temp is not None else -1.0
                
                self.data_updated.emit(cpu_temp_val, gpu_temp_val, cpu_usage, gpu_usage)
                
                if cpu_temp is None:
                    self.error_occurred.emit("无法获取CPU温度，请确保AIDA64已运行")
                if gpu_temp is None:
                    self.error_occurred.emit("无法获取GPU温度，请确保AIDA64已运行")
                if cpu_usage == -1.0:
                    self.error_occurred.emit("无法获取CPU使用率")
                if gpu_usage == -1.0:
                    self.error_occurred.emit("无法获取GPU使用率")
            
            except Exception as e:
                self.error_occurred.emit(f"数据采集异常: {str(e)}")
            
            time.sleep(self._interval)
    
    def stop(self):
        self._running = False
        self.wait(1000)

# ========== 主界面类（保持不变） ==========
class DarkInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cpu_temp_label = None
        self.gpu_temp_label = None
        self.cpu_usage_label = None
        self.gpu_usage_label = None
        self.cpu_temp_slider = None
        self.gpu_temp_slider = None
        self.cpu_usage_slider = None
        self.gpu_usage_slider = None
        self.error_cache = {}
        
        self.initUI()
        
        self.sensor_thread = SensorThread()
        self.sensor_thread.data_updated.connect(self.update_ui)
        self.sensor_thread.error_occurred.connect(self.show_error)
        self.sensor_thread.start()
    
    def initUI(self):
        self.setWindowTitle("性能控制面板")
        self.setGeometry(300, 300, 1000, 600)
        self.setStyleSheet("background-color: #2a2a2a;")
        
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧导航栏
        left_nav = QFrame()
        left_nav.setStyleSheet("background-color: #252525;")
        left_nav.setFixedWidth(200)
        left_nav_layout = QVBoxLayout()
        left_nav_layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel("性能控制面板")
        title_label.setStyleSheet("color: #cccccc; font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(60)
        left_nav_layout.addWidget(title_label)
        
        top_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
        left_nav_layout.addItem(top_spacer)
        
        # 导航按钮
        btn_texts = ["安静模式", "普通模式", "性能模式", "极限模式"]
        for text in btn_texts:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #353535; color: #ffffff;
                    border: none; border-radius: 6px;
                    font-size: 20px; font-weight: bold;
                    padding: 10px;
                }}
                QPushButton:hover {{ background-color: #404040; }}
            """)
            btn.setFixedHeight(80)
            left_nav_layout.addWidget(btn)
            
            if text != "极限模式":
                spacer = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
                left_nav_layout.addItem(spacer)
            
            if text == "安静模式": btn.clicked.connect(fanConfig1)
            elif text == "普通模式": btn.clicked.connect(fanConfig2)
            elif text == "性能模式": btn.clicked.connect(fanConfig3)
            elif text == "极限模式": btn.clicked.connect(fanConfig4)
        
        left_nav_layout.addStretch(1)
        left_nav.setLayout(left_nav_layout)
        main_layout.addWidget(left_nav)
        
        # 右侧内容区
        right_content = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(30, 20, 30, 20)
        right_layout.setSpacing(30)
        
        top_content = self.create_content_row("温度", 1)
        bottom_content = self.create_content_row("占用", 3)
        
        spacer_middle = QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed)
        right_layout.addItem(spacer_middle)
        right_layout.addLayout(top_content)
        right_layout.addItem(spacer_middle)
        right_layout.addLayout(bottom_content)
        right_content.setLayout(right_layout)
        main_layout.addWidget(right_content, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def create_content_row(self, row_name, start_index):
        row_layout = QVBoxLayout()
        row_layout.setSpacing(20)
        
        row_label = QLabel(row_name)
        row_label.setStyleSheet("color: #aaaaaa; font-size: 24px;")
        row_label.setAlignment(Qt.AlignLeft)
        row_layout.addWidget(row_label)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        for i in range(2):
            index = start_index + i
            group = QFrame()
            group.setFixedHeight(180)
            group.setStyleSheet("background-color: #353535; border-radius: 10px;")
            group_layout = QVBoxLayout()
            group_layout.setContentsMargins(20, 20, 20, 20)
            group_layout.setSpacing(20)
            
            num_label = QLabel("加载中...")
            num_label.setStyleSheet("color: #ff5555; font-size: 36px; font-weight: bold;")
            num_label.setAlignment(Qt.AlignCenter)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(0)
            slider.setEnabled(False)
            slider.setFixedHeight(40)
            slider.setStyleSheet("""
                QSlider::groove:horizontal { background: #444444; height: 6px; border-radius: 3px; }
                QSlider::handle:horizontal { background: #ffffff; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
                QSlider::sub-page:horizontal { background: #ff5555; border-radius: 3px; }
            """)
            
            text_label = QLabel("CPU" if index in (1, 3) else "GPU")
            text_label.setStyleSheet("color: #dddddd; font-size: 20px;")
            text_label.setAlignment(Qt.AlignCenter)
            
            if index == 1:
                self.cpu_temp_label = num_label
                self.cpu_temp_slider = slider
            elif index == 2:
                self.gpu_temp_label = num_label
                self.gpu_temp_slider = slider
            elif index == 3:
                self.cpu_usage_label = num_label
                self.cpu_usage_slider = slider
            elif index == 4:
                self.gpu_usage_label = num_label
                self.gpu_usage_slider = slider
            
            group_layout.addWidget(num_label)
            group_layout.addWidget(slider)
            group_layout.addWidget(text_label)
            group.setLayout(group_layout)
            content_layout.addWidget(group)
        
        row_layout.addLayout(content_layout)
        return row_layout
    
    @pyqtSlot(float, float, float, float)
    def update_ui(self, cpu_temp, gpu_temp, cpu_usage, gpu_usage):
        if cpu_temp != -1.0:
            self.cpu_temp_label.setText(f"{cpu_temp:.1f}℃")
            self.cpu_temp_slider.setValue(min(max(int(cpu_temp), 0), 100))
        else:
            self.cpu_temp_label.setText("N/A")
        
        if gpu_temp != -1.0:
            self.gpu_temp_label.setText(f"{gpu_temp:.1f}℃")
            self.gpu_temp_slider.setValue(min(max(int(gpu_temp), 0), 100))
        else:
            self.gpu_temp_label.setText("N/A")
        
        if cpu_usage != -1.0:
            self.cpu_usage_label.setText(f"{cpu_usage:.1f}%")
            self.cpu_usage_slider.setValue(int(cpu_usage))
        else:
            self.cpu_usage_label.setText("N/A")
        
        if gpu_usage != -1.0:
            self.gpu_usage_label.setText(f"{gpu_usage:.1f}%")
            self.gpu_usage_slider.setValue(int(gpu_usage))
        else:
            self.gpu_usage_label.setText("N/A")
    
    @pyqtSlot(str)
    def show_error(self, message):
        current_time = time.time()
        if message in self.error_cache and current_time - self.error_cache[message] < 5:
            return
        self.error_cache[message] = current_time
        QMessageBox.warning(self, "警告", message)
    
    def closeEvent(self, event):
        if hasattr(self, 'sensor_thread') and self.sensor_thread.isRunning():
            self.sensor_thread.stop()
        event.accept()

# ========== 程序入口 ==========
if __name__ == "__main__":
    if os.name != "nt":
        QMessageBox.critical(None, "错误", "此程序仅支持Windows系统")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    window = DarkInterface()
    window.show()
    sys.exit(app.exec_())
    
