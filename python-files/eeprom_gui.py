
import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from intelhex import IntelHex

EEPROM_SIZE = 1024
PAGE_SIZE = 16  # מספר בתים בשורה בטבלה

class EEPROMGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EEPROM Programmer - P24C08C")
        self.serial_port = None
        self.data = bytearray([0xFF]*EEPROM_SIZE)
        self.initUI()
        self.detect_serial()

    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # סטטוס בר
        self.status_label = QLabel("No device connected")
        layout.addWidget(self.status_label)

        # טבלה להצגת ה-HEX וה-ASCII
        self.table = QTableWidget()
        self.table.setRowCount(EEPROM_SIZE // PAGE_SIZE)
        self.table.setColumnCount(PAGE_SIZE + 1)  # 16 בתים + עמודת ASCII
        self.table.setHorizontalHeaderLabels(
            [f"{i:02X}" for i in range(PAGE_SIZE)] + ["ASCII"]
        )
        self.table.verticalHeader().setVisible(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        layout.addWidget(self.table)

        # כפתורים
        btn_layout = QHBoxLayout()

        self.btn_read = QPushButton("Read EEPROM")
        self.btn_read.clicked.connect(self.read_eeprom)
        btn_layout.addWidget(self.btn_read)

        self.btn_write = QPushButton("Write EEPROM")
        self.btn_write.clicked.connect(self.write_eeprom)
        btn_layout.addWidget(self.btn_write)

        self.btn_open = QPushButton("Open HEX")
        self.btn_open.clicked.connect(self.open_hex)
        btn_layout.addWidget(self.btn_open)

        self.btn_save = QPushButton("Save HEX")
        self.btn_save.clicked.connect(self.save_hex)
        btn_layout.addWidget(self.btn_save)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_data)
        btn_layout.addWidget(self.btn_clear)

        layout.addLayout(btn_layout)

        self.populate_table()

    def detect_serial(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                s = serial.Serial(port.device, 115200, timeout=1)
                s.write(b'\n')
                line = s.readline().decode(errors='ignore').strip()
                if "EEPROM Ready" in line:
                    self.serial_port = s
                    self.status_label.setText(f"Connected to {port.device}")
                    return
                s.close()
            except Exception:
                continue
        self.status_label.setText("No device connected")

    def populate_table(self):
        for row in range(self.table.rowCount()):
            ascii_str = ""
            for col in range(PAGE_SIZE):
                index = row * PAGE_SIZE + col
                val = self.data[index]
                item = QTableWidgetItem(f"{val:02X}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
                # ASCII
                ascii_char = chr(val) if 32 <= val < 127 else '.'
                ascii_str += ascii_char
            ascii_item = QTableWidgetItem(ascii_str)
            ascii_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, PAGE_SIZE, ascii_item)

    def read_table_to_data(self):
        for row in range(self.table.rowCount()):
            for col in range(PAGE_SIZE):
                item = self.table.item(row, col)
                if item is None:
                    continue
                text = item.text().strip()
                try:
                    val = int(text, 16)
                    if 0 <= val <= 255:
                        self.data[row * PAGE_SIZE + col] = val
                except ValueError:
                    pass

    def clear_data(self):
        self.data = bytearray([0xFF]*EEPROM_SIZE)
        self.populate_table()

    def open_hex(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Intel HEX", "", "HEX Files (*.hex)")
        if path:
            try:
                ih = IntelHex()
                ih.loadhex(path)
                self.data = bytearray([ih[i] if i in ih else 0xFF for i in range(EEPROM_SIZE)])
                self.populate_table()
                self.status_label.setText(f"Loaded HEX from {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load HEX: {e}")

    def save_hex(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Intel HEX", "", "HEX Files (*.hex)")
        if path:
            try:
                ih = IntelHex()
                for i in range(EEPROM_SIZE):
                    ih[i] = self.data[i]
                ih.write_hex_file(path)
                self.status_label.setText(f"Saved HEX to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save HEX: {e}")

    def read_eeprom(self):
        if self.serial_port is None:
            self.status_label.setText("No device connected")
            return
        self.status_label.setText("Reading EEPROM...")
        QApplication.processEvents()

        addr = 0
        length = EEPROM_SIZE
        data = bytearray()
        try:
            # פקודת קריאה: R + addr(2) + length(2)
            self.serial_port.reset_input_buffer()
            self.serial_port.write(b'R')
            self.serial_port.write(addr.to_bytes(2, 'big'))
            self.serial_port.write(length.to_bytes(2, 'big'))
            while len(data) < length:
                chunk = self.serial_port.read(length - len(data))
                if not chunk:
                    break
                data.extend(chunk)
            if len(data) == length:
                self.data = data
                self.populate_table()
                self.status_label.setText("EEPROM read successfully")
            else:
                self.status_label.setText("Failed to read full EEPROM")
        except Exception as e:
            self.status_label.setText(f"Error reading EEPROM: {e}")

    def write_eeprom(self):
        if self.serial_port is None:
            self.status_label.setText("No device connected")
            return
        self.status_label.setText("Writing EEPROM...")
        QApplication.processEvents()

        self.read_table_to_data()
        addr = 0
        length = EEPROM_SIZE
        try:
            # מחלקים כתיבה לדפים של 16 בתים (או פחות)
            pos = 0
            while pos < length:
                chunk_len = min(16, length - pos)
                self.serial_port.reset_input_buffer()
                self.serial_port.write(b'W')
                self.serial_port.write((addr + pos).to_bytes(2, 'big'))
                self.serial_port.write(bytes([chunk_len]))
                self.serial_port.write(self.data[pos:pos+chunk_len])
                # מחכים ל־ACK על כל בית
                acks = self.serial_port.read(chunk_len)
                if len(acks) != chunk_len or any(b != 0xAA for b in acks):
                    self.status_label.setText("Write failed (ACK error)")
                    return
                pos += chunk_len
            self.status_label.setText("EEPROM written successfully")
        except Exception as e:
            self.status_label.setText(f"Error writing EEPROM: {e}")

def main():
    app = QApplication(sys.argv)
    window = EEPROMGui()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
