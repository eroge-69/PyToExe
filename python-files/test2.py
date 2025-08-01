import sys
import serial
import serial.tools.list_ports
import threading
import json
from PyQt5 import QtWidgets, QtCore

class BarcodeRelayApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barcode Relay App")
        self.setGeometry(100, 100, 600, 400)
        self.serial_in = None
        self.serial_out = None
        self.thread = None
        self.running = False

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()
        self.input_port = QtWidgets.QLineEdit("COM4")
        self.output_port = QtWidgets.QLineEdit("COM5")
        self.baudrate = QtWidgets.QLineEdit("9600")
        self.trigger = QtWidgets.QLineEdit("start")
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(["ASCII", "HEX"])
        form_layout.addRow("Input Port:", self.input_port)
        form_layout.addRow("Output Port:", self.output_port)
        form_layout.addRow("Baudrate:", self.baudrate)
        form_layout.addRow("Trigger:", self.trigger)
        form_layout.addRow("Format:", self.format_combo)

        layout.addLayout(form_layout)

        self.start_btn = QtWidgets.QPushButton("Start service")
        self.stop_btn = QtWidgets.QPushButton("Stop service")
        self.send_btn = QtWidgets.QPushButton("Send trigger")
        self.save_btn = QtWidgets.QPushButton("Save config")
        self.load_btn = QtWidgets.QPushButton("Load config")
        self.auto_send_check = QtWidgets.QCheckBox("Auto send on startup")
        self.output_text = QtWidgets.QTextEdit()
        self.output_text.setReadOnly(True)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.send_btn)
        layout.addLayout(btn_layout)
        layout.addWidget(self.auto_send_check)

        config_layout = QtWidgets.QHBoxLayout()
        config_layout.addWidget(self.save_btn)
        config_layout.addWidget(self.load_btn)
        layout.addLayout(config_layout)

        layout.addWidget(self.output_text)
        self.footer = QtWidgets.QLabel("Made by Ivan")
        self.footer.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(self.footer)

        self.setLayout(layout)

        self.start_btn.clicked.connect(self.start_service)
        self.stop_btn.clicked.connect(self.stop_service)
        self.send_btn.clicked.connect(self.send_trigger)
        self.save_btn.clicked.connect(self.save_config)
        self.load_btn.clicked.connect(self.load_config)

        if self.auto_send_check.isChecked():
            self.send_trigger()

    def start_service(self):
        self.running = True
        self.thread = threading.Thread(target=self.listen_and_forward)
        self.thread.start()
        self.output_text.append("Service started.")

    def stop_service(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.serial_in:
            self.serial_in.close()
        if self.serial_out:
            self.serial_out.close()
        self.output_text.append("Service stopped.")

    def listen_and_forward(self):
        try:
            self.serial_in = serial.Serial(self.input_port.text(), int(self.baudrate.text()))
            self.serial_out = serial.Serial(self.output_port.text(), int(self.baudrate.text()))
            while self.running:
                if self.serial_in.in_waiting:
                    data = self.serial_in.read(self.serial_in.in_waiting)
                    self.serial_out.write(data)
                    self.output_text.append(f"Forwarded: {data.decode(errors='ignore')}")
        except Exception as e:
            self.output_text.append(f"Error: {str(e)}")

    def send_trigger(self):
        try:
            port = serial.Serial(self.input_port.text(), int(self.baudrate.text()))
            trigger = self.trigger.text()
            if self.format_combo.currentText() == "HEX":
                trigger_bytes = bytes.fromhex(trigger)
            else:
                trigger_bytes = trigger.encode()
            port.write(trigger_bytes)
            port.close()
            self.output_text.append(f"Trigger sent: {trigger}")
        except Exception as e:
            self.output_text.append(f"Trigger error: {str(e)}")

    def save_config(self):
        config = {
            "input_port": self.input_port.text(),
            "output_port": self.output_port.text(),
            "baudrate": self.baudrate.text(),
            "trigger": self.trigger.text(),
            "format": self.format_combo.currentText(),
            "auto_send": self.auto_send_check.isChecked()
        }
        with open("config.json", "w") as f:
            json.dump(config, f)
        self.output_text.append("Configuration saved.")

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.input_port.setText(config["input_port"])
                self.output_port.setText(config["output_port"])
                self.baudrate.setText(config["baudrate"])
                self.trigger.setText(config["trigger"])
                self.format_combo.setCurrentText(config["format"])
                self.auto_send_check.setChecked(config["auto_send"])
                self.output_text.append("Configuration loaded.")
        except Exception as e:
            self.output_text.append(f"Load error: {str(e)}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BarcodeRelayApp()
    window.show()
    sys.exit(app.exec_())
