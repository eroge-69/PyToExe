import sys
import struct
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout,
    QSpinBox, QCheckBox, QStatusBar, QMessageBox
)
from PyQt5.QtCore import QTimer
from pymodbus.client import ModbusTcpClient, ModbusSerialClient


class ModScanWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModScan Tool")
        self.setGeometry(100, 100, 600, 500)
        self.client = None
        self.polling_timer = QTimer()
        self.polling_timer.timeout.connect(self.read_data)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Connection Config
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QFormLayout(conn_group)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["TCP", "RTU"])

        self.ip_edit = QLineEdit("127.0.0.1")
        self.port_edit = QSpinBox()
        self.port_edit.setRange(1, 65535)
        self.port_edit.setValue(502)

        self.serial_port_edit = QLineEdit("COM3")
        self.baudrate_edit = QSpinBox()
        self.baudrate_edit.setRange(1200, 115200)
        self.baudrate_edit.setValue(9600)

        self.slave_id_edit = QSpinBox()
        self.slave_id_edit.setRange(1, 255)
        self.slave_id_edit.setValue(1)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_modbus)

        conn_layout.addRow("Mode:", self.mode_combo)
        conn_layout.addRow("IP Address:", self.ip_edit)
        conn_layout.addRow("Port:", self.port_edit)
        conn_layout.addRow("Serial Port:", self.serial_port_edit)
        conn_layout.addRow("Baudrate:", self.baudrate_edit)
        conn_layout.addRow("Slave ID:", self.slave_id_edit)
        conn_layout.addRow(self.connect_btn)

        # Read Config
        read_group = QGroupBox("Read Settings")
        read_layout = QFormLayout(read_group)

        self.function_combo = QComboBox()
        self.function_combo.addItems(["Read Coils", "Read Discrete Inputs", "Read Holding Registers", "Read Input Registers"])

        self.address_edit = QSpinBox()
        self.address_edit.setRange(0, 65535)
        self.address_edit.setValue(0)

        self.count_edit = QSpinBox()
        self.count_edit.setRange(1, 125)
        self.count_edit.setValue(10)

        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["uint16", "int16", "float32", "hex", "ascii"])

        self.read_btn = QPushButton("Read Now")
        self.read_btn.clicked.connect(self.read_data)

        self.poll_checkbox = QCheckBox("Poll Continuously")
        self.poll_checkbox.stateChanged.connect(self.toggle_polling)

        read_layout.addRow("Function:", self.function_combo)
        read_layout.addRow("Address:", self.address_edit)
        read_layout.addRow("Count:", self.count_edit)
        read_layout.addRow("Data Type:", self.data_type_combo)
        read_layout.addRow(self.read_btn)
        read_layout.addRow(self.poll_checkbox)

        # Table to display data
        self.data_table = QTableWidget()

        layout.addWidget(conn_group)
        layout.addWidget(read_group)
        layout.addWidget(self.data_table)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def connect_modbus(self):
        if self.client:
            self.client.close()
            self.client = None

        mode = self.mode_combo.currentText()
        unit_id = self.slave_id_edit.value()

        try:
            if mode == "TCP":
                ip = self.ip_edit.text()
                port = self.port_edit.value()
                self.client = ModbusTcpClient(ip, port=port)
            else:
                port = self.serial_port_edit.text()
                baudrate = self.baudrate_edit.value()
                self.client = ModbusSerialClient(method='rtu', port=port, baudrate=baudrate, timeout=1)

            if self.client.connect():
                self.status_bar.showMessage(f"Connected to Modbus ({mode}, Slave ID: {unit_id})")
            else:
                self.status_bar.showMessage("Connection failed")
                self.client = None
        except Exception as e:
            self.status_bar.showMessage(f"Error: {e}")
            self.client = None

    def read_data(self):
        if not self.client:
            QMessageBox.warning(self, "Error", "Not connected to any Modbus device.")
            return

        function = self.function_combo.currentText()
        address = self.address_edit.value()
        count = self.count_edit.value()
        slave_id = self.slave_id_edit.value()

        try:
            if function == "Read Coils":
                result = self.client.read_coils(address=address, count=count, slave=slave_id)
                data = result.bits if not result.isError() else []
            elif function == "Read Discrete Inputs":
                result = self.client.read_discrete_inputs(address=address, count=count, slave=slave_id)
                data = result.bits if not result.isError() else []
            elif function == "Read Holding Registers":
                result = self.client.read_holding_registers(address=address, count=count, slave=slave_id)
                data = result.registers if not result.isError() else []
            elif function == "Read Input Registers":
                result = self.client.read_input_registers(address=address, count=count, slave=slave_id)
                data = result.registers if not result.isError() else []
            else:
                data = []

            if result.isError():
                self.status_bar.showMessage(f"Read Error: {result}")
                return

            data_type = self.data_type_combo.currentText()
            converted = self.convert_data(data, data_type)
            self.display_data(converted)
            self.status_bar.showMessage("Read successful")
        except Exception as e:
            self.status_bar.showMessage(f"Read error: {e}")

    def convert_data(self, data, data_type):
        try:
            if data_type == "uint16":
                return data
            elif data_type == "int16":
                return [struct.unpack('>h', struct.pack('>H', reg))[0] for reg in data]
            elif data_type == "float32":
                floats = []
                for i in range(0, len(data) - 1, 2):
                    packed = struct.pack('>HH', data[i], data[i + 1])
                    floats.append(struct.unpack('>f', packed)[0])
                return floats
            elif data_type == "hex":
                return [hex(reg) for reg in data]
            elif data_type == "ascii":
                chars = ''
                for reg in data:
                    chars += chr((reg >> 8) & 0xFF) + chr(reg & 0xFF)
                return [chars.strip()]
        except Exception as e:
            return [f"Conversion error: {e}"]

    def display_data(self, data):
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Index", "Value"])
        for i, val in enumerate(data):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(i)))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(val)))

    def toggle_polling(self, state):
        if state == 2:  # Checked
            self.polling_timer.start(1000)
        else:
            self.polling_timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModScanWindow()
    window.show()
    sys.exit(app.exec_())
