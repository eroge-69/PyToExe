import sys
import re
import asyncio
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QComboBox, QTextEdit, QLabel, QMenu, QAction, QCheckBox, QLineEdit, QStyle
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from bleak import BleakScanner, BleakClient
from PyQt5.QtCore import QTimer

# 检查是否在 Windows 系统上运行，如果是，则导入 ctypes
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes

NOTIFY_UUID = "f000c0c2-0451-4000-b000-000000000000"
WRITE_UUID = "f000c0c1-0451-4000-b000-000000000000"

# MAC 地址正则 (XX:XX:XX:XX:XX:XX)
MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")

# ---------------------------
# 后台 BLE 线程 (无修改)
# ---------------------------
class BleakWorker(QThread):
    device_found = pyqtSignal(str, str)  # address, name
    log_message = pyqtSignal(str)
    connection_status = pyqtSignal(bool)
    notification_received = pyqtSignal(bytes)
    scan_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.selected_address = None
        self.scanning = False
        self.loop = None
        self.auto_read_sn = False
        self.is_stopping = False 

    # CRC-8 校验计算函数
    def crc8_direct(self, data):
        CRC8_POLY = 0x1D
        crc = 0xA5
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ CRC8_POLY
                else:
                    crc <<= 1
            crc &= 0xFF
        return crc
    
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop(self):
        self.is_stopping = True
        if self.client and self.client.is_connected:
            future = asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop)
            try:
                future.result(timeout=5.0)
                self.log_message.emit("Disconnect completed successfully.")
            except asyncio.TimeoutError:
                self.log_message.emit("Disconnect timed out, forcing stop.")
            except Exception as e:
                self.log_message.emit(f"Disconnect error: {e}")
        
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.client:
            self.client = None
        
        self.wait()

    async def scan_devices(self, filter_target=True):
        if self.scanning:
            self.log_message.emit("Scan already in progress.")
            return

        self.scanning = True
        self.log_message.emit("Starting scan for devices...")
        found_devices = {}

        def detection_callback(d, adv_data):
            name = d.name or "Unknown"

            if filter_target and name != "BI_ECG_Respiration":
                return
            if not filter_target and name in (None, "Unknown"):
                return

            if d.address not in found_devices:
                self.device_found.emit(d.address, name)
                found_devices[d.address] = name
                self.log_message.emit(f"Found device: {name} ({d.address}) RSSI: {adv_data.rssi}")

        try:
            scanner = BleakScanner(detection_callback)
            await scanner.start()
            await asyncio.sleep(5.0)
            await scanner.stop()

            if not found_devices:
                self.log_message.emit("No target BLE devices found.")
        except Exception as e:
            self.log_message.emit(f"Scan error: {e}")
        finally:
            self.scanning = False
            if not self.is_stopping:
                self.log_message.emit("Scan finished.")
                self.scan_completed.emit()
        
    async def connect_device(self, address):
        self.selected_address = address
        if not address:
            self.log_message.emit("No device address selected for connection.")
            self.connection_status.emit(False)
            return

        if self.client and self.client.is_connected:
            if self.client.address == address:
                self.log_message.emit(f"Already connected to {address}")
                self.connection_status.emit(True)
                return
            else:
                self.log_message.emit("Disconnecting from previous device...")
                try:
                    await self.client.disconnect()
                    self.client = None
                    self.connection_status.emit(False)
                    self.log_message.emit("Disconnected.")
                except Exception as e:
                    self.log_message.emit(f"Error disconnecting: {e}")
                    self.connection_status.emit(False)
                    return

        try:
            self.client = BleakClient(address)
            await self.client.connect()
            self.log_message.emit(f"Successfully connected to {address}.")
            self.connection_status.emit(True)
            await self.enable_notify()

        except Exception as e:
            self.log_message.emit(f"Failed to connect to {address}: {e}")
            self.connection_status.emit(False)
            self.client = None

    async def disconnect_device(self):
        if self.client and self.client.is_connected:
            self.log_message.emit(f"Disconnecting from {self.client.address}...")
            try:
                await self.client.disconnect()
                self.log_message.emit("设备已经断开.")
                self.connection_status.emit(False)
            except Exception as e:
                self.log_message.emit(f"Error during disconnection: {e}")
            finally:
                self.client = None
        else:
            self.log_message.emit("Not connected to any device.")
            self.connection_status.emit(False)

    async def enable_notify(self):
        if self.client and self.client.is_connected:
            try:
                await self.client.start_notify(NOTIFY_UUID, self._notification_handler)
                if self.auto_read_sn:
                    command = bytearray([0x42, 0x49, 0x45, 0x52, 0x08, 0x01, 0x00, 0x01, 0xA4])
                    await self.client.write_gatt_char(WRITE_UUID, command)
            except Exception as e:
                self.log_message.emit(f"Failed to enable notifications for {NOTIFY_UUID}: {e}")
        else:
            self.log_message.emit("Cannot enable notify: Not connected to any device.")

    async def write_sn(self, sn):
        if self.client and self.client.is_connected:
            try:
                sn_bytes = sn.encode('utf-8')
                s_byte = b'S'
                e_byte = b'E'
                cmd_prefix = bytearray.fromhex("42494552070D00") + s_byte + sn_bytes + e_byte
                crc = self.crc8_direct(cmd_prefix)
                final_data = cmd_prefix + bytearray([crc])
                await self.client.write_gatt_char(WRITE_UUID, final_data)
            except Exception as e:
                self.log_message.emit(f"Failed to write SN to {WRITE_UUID}: {e}")
        else:
            self.log_message.emit("Cannot write SN: Not connected to any device.")

    def _notification_handler(self, sender, data):
        data_bytes = bytes(data) if isinstance(data, bytearray) else data
        self.notification_received.emit(data_bytes)

    def start_scan_threadsafe(self, filter_target=True):
        asyncio.run_coroutine_threadsafe(self.scan_devices(filter_target), self.loop)

    def connect_device_threadsafe(self, address):
        asyncio.run_coroutine_threadsafe(self.connect_device(address), self.loop)

    def disconnect_device_threadsafe(self):
        asyncio.run_coroutine_threadsafe(self.disconnect_device(), self.loop)

    def enable_notify_threadsafe(self):
        asyncio.run_coroutine_threadsafe(self.enable_notify(), self.loop)

    def write_sn_threadsafe(self, sn):
        asyncio.run_coroutine_threadsafe(self.write_sn(sn), self.loop)

# ---------------------------
# 主窗口 GUI
# ---------------------------
class BleTool(QWidget):
    def __init__(self):
        super().__init__()
        self.device_map = {}
        self.current_selected_address = None
        self.filter_target_only = True
        self.is_closing = False
        
        self.log_dir = "sn_logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.init_ui()
        self.init_bleak_worker()
        self.update_connection_status(False)

        # ------------------- 新增代码块：在Win11上恢复直角边框 -------------------
        if sys.platform == 'win32':
            try:
                # 获取窗口句柄 (HWND)
                hwnd = self.winId()
                
                # 定义 Windows API 所需的常量
                # DWMWA_WINDOW_CORNER_PREFERENCE = 33
                # DWMWCP_DONOTROUND = 1
                DWMWA_WINDOW_CORNER_PREFERENCE = 33
                DWMWCP_DONOTROUND = 1
                
                # 将 Python 整数转换为 C 语言的 int 类型
                preference = ctypes.c_int(DWMWCP_DONOTROUND)
                
                # 调用 DwmSetWindowAttribute 函数
                # 参数: 窗口句柄, 属性(边角偏好), 值, 值的大小
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_WINDOW_CORNER_PREFERENCE,
                    ctypes.byref(preference),
                    ctypes.sizeof(preference)
                )
            except (AttributeError, TypeError, Exception):
                # 如果在不支持此功能的旧版 Windows 上运行，会安全地忽略错误
                pass
        # --------------------------- 代码块结束 ---------------------------

    def init_ui(self):
        self.setWindowTitle("Set SN for BI_ECG_Respiration")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # 控制区
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        control_layout.setContentsMargins(10, 10, 10, 10)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)
        self.scan_button = QPushButton("扫描设备")
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setMinimumSize(120, 40)
        self.scan_button.setStyleSheet("font-size: 14px; padding: 8px;")
        button_layout.addWidget(self.scan_button)

        self.set_sn_button = QPushButton("设置SN")
        self.set_sn_button.clicked.connect(self.set_sn)
        self.set_sn_button.setEnabled(False)
        self.set_sn_button.setMinimumSize(120, 40)
        self.set_sn_button.setStyleSheet("font-size: 14px; padding: 8px;")
        button_layout.addWidget(self.set_sn_button)
        control_layout.addLayout(button_layout)

        device_layout = QVBoxLayout()
        device_layout.setSpacing(8)
        self.device_combo = QComboBox()
        self.device_combo.setPlaceholderText("Select or enter a device address")
        self.device_combo.setEditable(True)
        self.device_combo.currentIndexChanged.connect(self.device_selection_changed)
        self.device_combo.editTextChanged.connect(self.validate_manual_input)
        
        self.device_combo.lineEdit().returnPressed.connect(self.connect_device)
        
        validator = QRegExpValidator(QRegExp(r'^([0-9A-Fa-f]{2}:){0,5}[0-9A-Fa-f]{0,2}$'))
        self.device_combo.setValidator(validator)
        self.device_combo.setMinimumSize(200, 30)
        
        self.device_combo.setProperty("validationState", "neutral")
        self.device_combo.setStyleSheet("""
            QComboBox[validationState="neutral"] { border: 1px solid #ccc; }
            QComboBox[validationState="valid"] { border: 2px solid green; }
            QComboBox[validationState="invalid"] { border: 2px solid red; }
            QComboBox { font-size: 14px; padding: 5px; }
            QComboBox QAbstractItemView::vertical-scrollbar { border: none; background: #f0f0f0; width: 15px; margin: 0px; }
            QComboBox QAbstractItemView::vertical-scrollbar::handle { background: #c0c0c0; min-height: 20px; border-radius: 5px; }
            QComboBox QAbstractItemView::vertical-scrollbar::handle:hover { background: #a0a0a0; }
            QComboBox QAbstractItemView::vertical-scrollbar::add-line, QComboBox QAbstractItemView::vertical-scrollbar::sub-line { height: 0px; background: none; }
        """)
        
        device_layout.addWidget(self.device_combo)

        self.sn_input = QLineEdit()
        self.sn_input.setPlaceholderText("Enter SN")
        self.sn_input.setMaxLength(11)
        self.sn_input.textChanged.connect(self.validate_sn_input)
        self.sn_input.setMinimumSize(200, 30)
        self.sn_input.setStyleSheet("font-size: 14px; padding: 5px; border: 1px solid #ccc;")
        self.sn_input.returnPressed.connect(self.set_sn)
        device_layout.addWidget(self.sn_input)
        control_layout.addLayout(device_layout)

        self.connect_button = QPushButton("连接设备")
        self.connect_button.clicked.connect(self.connect_device)
        self.connect_button.setEnabled(False)
        self.connect_button.setMinimumSize(120, 40)
        self.connect_button.setStyleSheet("font-size: 14px; padding: 8px;")
        control_layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("断开设备")
        self.disconnect_button.clicked.connect(self.disconnect_device)
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setMinimumSize(120, 40)
        self.disconnect_button.setStyleSheet("font-size: 14px; padding: 8px;")
        control_layout.addWidget(self.disconnect_button)

        main_layout.addLayout(control_layout)
        
        status_layout = QHBoxLayout()
        status_label = QLabel("连接状态:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(20, 20)

        self.status_text = QLabel("未连接")
        self.status_text.setStyleSheet("font-size: 14px;")

        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()

        main_layout.addLayout(status_layout)

        log_label = QLabel("Logs:")
        log_label.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(log_label)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setContextMenuPolicy(Qt.CustomContextMenu)
        self.log_display.customContextMenuRequested.connect(self.show_log_context_menu)
        self.log_display.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.log_display)

        self.show_all_checkbox = QCheckBox("Show All Devices")
        self.show_all_checkbox.stateChanged.connect(self.toggle_filter)
        self.show_all_checkbox.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(self.show_all_checkbox)

        self.auto_read_sn_checkbox = QCheckBox("Auto Read SN")
        self.auto_read_sn_checkbox.stateChanged.connect(self.toggle_auto_read_sn)
        self.auto_read_sn_checkbox.setStyleSheet("font-size: 14px;")
        self.auto_read_sn_checkbox.setChecked(False)
        main_layout.addWidget(self.auto_read_sn_checkbox)

        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)

    def init_bleak_worker(self):
        self.bleak_worker = BleakWorker()
        self.bleak_worker.device_found.connect(self.add_device_to_combo)
        self.bleak_worker.log_message.connect(self.add_log_message)
        self.bleak_worker.connection_status.connect(self.update_connection_status)
        self.bleak_worker.notification_received.connect(self.handle_notification_data)
        self.bleak_worker.scan_completed.connect(self.on_scan_completed)        
        self.bleak_worker.start()

    def log_sn_to_file(self, address, sn):
        try:
            log_date = datetime.now().strftime('%Y-%m-%d')
            log_filename = os.path.join(self.log_dir, f"sn_log_{log_date}.txt")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            log_entry = f"{timestamp}, {address}, {sn}\n"

            with open(log_filename, 'a', encoding='utf-8') as f:
                f.write(log_entry)

            self.add_log_message(f"记录成功 -> 文件: {log_filename}")
        except Exception as e:
            self.add_log_message(f"错误: 无法写入日志文件: {e}")

    def toggle_filter(self, state):
        self.filter_target_only = state != Qt.Checked

    def toggle_auto_read_sn(self, state):
        self.bleak_worker.auto_read_sn = (state == Qt.Checked)
        self.add_log_message(f"Auto Read Serial Number: {'Enabled' if state == Qt.Checked else 'Disabled'}")

    def _update_combo_style(self, state_str):
        self.device_combo.setProperty("validationState", state_str)
        self.device_combo.style().unpolish(self.device_combo)
        self.device_combo.style().polish(self.device_combo)

    def validate_manual_input(self, text):
        text = text.strip()
        if not text:
            self._update_combo_style("neutral")
            return
            
        if MAC_REGEX.match(text):
            self.current_selected_address = text
            self.connect_button.setEnabled(True)
            self._update_combo_style("valid")
            self.add_log_message(f"手动输入有效地址: {text}")
        else:
            self.current_selected_address = None
            self.connect_button.setEnabled(False)
            self._update_combo_style("invalid")

    def validate_sn_input(self, text):
        text = text.strip()
        is_connected = self.bleak_worker.client and self.bleak_worker.client.is_connected
        if len(text) == 11:
            self.sn_input.setStyleSheet("font-size: 14px; padding: 5px; border: 2px solid green;")
            if is_connected:
                self.set_sn_button.setEnabled(True)
        else:
            self.sn_input.setStyleSheet("font-size: 14px; padding: 5px; border: 2px solid red;")
            self.set_sn_button.setEnabled(False)


    def start_scan(self):
        self.log_display.clear()
        self.device_combo.clear()
        self.device_map.clear()
        self.current_selected_address = None
        self.connect_button.setEnabled(False)
        self.set_sn_button.setEnabled(False)
        self.scan_button.setEnabled(False)
        self.bleak_worker.start_scan_threadsafe(filter_target=self.filter_target_only)

    def add_device_to_combo(self, address, name):
        if address not in self.device_map:
            self.device_map[address] = name
            self.device_combo.addItem(f"{name} ({address})", address)
            self.connect_button.setEnabled(True)
            self._update_combo_style("valid")

    def device_selection_changed(self, index):
        address = self.device_combo.itemData(index)
        if index >= 0 and address:
            self.current_selected_address = address
            self._update_combo_style("valid")
            self.add_log_message(
                f"已选择设备: {self.device_map.get(self.current_selected_address, 'Unknown')} ({self.current_selected_address})"
            )
            if not (self.bleak_worker.client and self.bleak_worker.client.is_connected):
                self.add_log_message(f"开始自动连接设备: {self.current_selected_address}")
                self.connect_device()
                self.scan_button.setEnabled(False)
            else:
                self.add_log_message(f"设备 {self.current_selected_address} 已连接，无需重新连接")
        
    def connect_device(self):
        text = self.device_combo.currentText().strip()
        if not text:
            self.add_log_message("请输入或选择一个设备地址以连接。")
            return

        index = self.device_combo.currentIndex()
        if index >= 0 and self.device_combo.itemData(index):
            address = self.device_combo.itemData(index)
        else:
            address = text

        if not MAC_REGEX.match(address):
            self.add_log_message(f"无效的地址格式: {address}，预期格式: XX:XX:XX:XX:XX:XX")
            self._update_combo_style("invalid")
            return

        self.current_selected_address = address
        self.connect_button.setText("连接设备中...")
        self.status_text.setText("连接设备中...")
        self.add_log_message(f"Attempting to connect to: {self.current_selected_address}")
        self.bleak_worker.connect_device_threadsafe(self.current_selected_address)

    def set_sn(self):
        sn = self.sn_input.text().strip()
        if not sn or len(sn) != 11:
            self.add_log_message("错误: SN 必须正好是 11 位长度，请重新输入。")
            self.sn_input.setStyleSheet("font-size: 14px; padding: 5px; border: 2px solid red;")
            return

        if not self.current_selected_address:
            self.add_log_message("错误: 没有有效的设备地址，无法记录日志。")
            return

        self.log_sn_to_file(self.current_selected_address, sn)
        
        self.bleak_worker.write_sn_threadsafe(sn)
        QTimer.singleShot(500, self.disconnect_device)

    def disconnect_device(self):
        self.add_log_message("尝试自动断开连接，请等待...")
        self.bleak_worker.disconnect_device_threadsafe()

    def update_connection_status(self, is_connected):
        if is_connected:
            self.status_indicator.setStyleSheet("QLabel { background-color: #4CAF50; border: 1px solid #388E3C; border-radius: 10px; }")
            self.status_text.setText("已连接")
            self.status_text.setStyleSheet("font-size: 14px; color: #4CAF50;")
            
            self.scan_button.setEnabled(False)
            self.device_combo.setEnabled(False)
            self.connect_button.setText("设备已连接")
            
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.set_sn_button.setEnabled(len(self.sn_input.text()) == 11)
            self.add_log_message("设备连接成功....")
        else:
            self.status_indicator.setStyleSheet("QLabel { background-color: #F44336; border: 1px solid #D32F2F; border-radius: 10px; }")
            self.status_text.setText("未连接")
            self.status_text.setStyleSheet("font-size: 14px; color: #F44336;")
            
            self.scan_button.setEnabled(True)
            self.device_combo.setEnabled(True)
            self.connect_button.setText("连接设备")
            
            self.connect_button.setEnabled(self.current_selected_address is not None)
            self.disconnect_button.setEnabled(False)
            self.set_sn_button.setEnabled(False)
            self._update_combo_style("neutral")
            self.sn_input.setStyleSheet("font-size: 14px; padding: 5px; border: 1px solid #ccc;")

    def add_log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.log_display.append(f"[{timestamp}] {message}")

    def handle_notification_data(self, data):
        if len(data) < 7:
            self.add_log_message(f"错误: 数据长度不足，实际 {len(data)} 字节，需至少 7 字节")
            return

        header = data[:4]
        if header != b'BIRE':
            self.add_log_message(f"错误: 无效头部 {header.hex()}，预期 42495245")
            return

        cmd_type = data[4]
        data_length = int.from_bytes(data[5:7], byteorder='little')

        if len(data) < 7 + data_length:
            self.add_log_message(f"错误: 数据长度不足，预期 {7 + data_length} 字节，实际 {len(data)} 字节")
            return

        data_content = data[7:7 + data_length]

        if cmd_type == 0x07:
            if data_content == b'OK':
                self.add_log_message("序列号设置成功(OK)")
            else:
                self.add_log_message(f"序列号设置命令返回失败: 数据内容: {data_content.decode('utf-8', errors='ignore')}")
        elif cmd_type == 0x08:
            self.add_log_message(f"读取到序列号: ({data_content.decode('utf-8', errors='ignore')})")
        else:
            self.add_log_message(f"未知命令类型: {cmd_type:02x}")

        if len(data) == 7 + data_length + 1:
            received_crc = data[-1]
            calculated_crc = self.bleak_worker.crc8_direct(data[:-1])
            if received_crc != calculated_crc:
                self.add_log_message(f"CRC 校验失败: 收到 {received_crc:02x}，计算 {calculated_crc:02x}")

    def show_log_context_menu(self, pos):
        menu = QMenu()
        clear_action = QAction("Clear Log", self)
        clear_action.triggered.connect(self.log_display.clear)
        menu.addAction(clear_action)
        menu.exec_(self.log_display.mapToGlobal(pos))
        
    def on_scan_completed(self):
        if not self.is_closing:
            self.scan_button.setEnabled(True)
            
    def closeEvent(self, event):
        self.is_closing = True 
        self.add_log_message("Closing application...")
        if self.bleak_worker and self.bleak_worker.isRunning():
            self.bleak_worker.stop()
            self.bleak_worker.wait(5000)
        import time
        time.sleep(1)
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BleTool()
    window.show()
    sys.exit(app.exec_())