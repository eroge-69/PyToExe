Python 2.7.18 (v2.7.18:8d21aa21f2, Apr 20 2020, 13:19:08) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QFileDialog, QMessageBox, QHBoxLayout
)
import subprocess

MISC_SLOT_SUFFIX_OFFSET = 0x1000  # Offset to slot_suffix in misc partition
SLOT_A = b'--slot_suffix=_a'
SLOT_B = b'--slot_suffix=_b'

class MiscEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qualcomm Boot Slot Switcher")
        self.misc_data = None
        self.misc_path = None
        self.firehose_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("No file loaded.")
        layout.addWidget(self.label)

        btn_load = QPushButton("Load MISC File")
        btn_load.clicked.connect(self.load_misc)
        layout.addWidget(btn_load)

        hbox = QHBoxLayout()
        btn_a = QPushButton("Set Slot A")
        btn_a.clicked.connect(lambda: self.set_slot("a"))
        hbox.addWidget(btn_a)

        btn_b = QPushButton("Set Slot B")
        btn_b.clicked.connect(lambda: self.set_slot("b"))
        hbox.addWidget(btn_b)
        layout.addLayout(hbox)

        btn_save = QPushButton("Save Modified File")
        btn_save.clicked.connect(self.save_file)
        layout.addWidget(btn_save)

        btn_flash = QPushButton("Flash to Device (EDL)")
        btn_flash.clicked.connect(self.flash_misc)
        layout.addWidget(btn_flash)

        btn_load_firehose = QPushButton("Load Firehose Programmer")
        btn_load_firehose.clicked.connect(self.load_firehose)
        layout.addWidget(btn_load_firehose)

        self.setLayout(layout)

    def load_misc(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select MISC Partition File", "", "BIN Files (*.bin *.img)")
        if path:
            with open(path, "rb") as f:
                self.misc_data = bytearray(f.read())
            self.misc_path = path
            current = self.detect_slot()
            self.label.setText(f"Loaded: {path}\nCurrent Slot: {current}")

    def detect_slot(self):
        if not self.misc_data:
            return "Unknown"
        part = self.misc_data[MISC_SLOT_SUFFIX_OFFSET:MISC_SLOT_SUFFIX_OFFSET+20]
        if SLOT_A in part:
            return "Slot A"
        elif SLOT_B in part:
            return "Slot B"
        return "Unknown"

    def set_slot(self, slot):
        if not self.misc_data:
            QMessageBox.warning(self, "Error", "Please load a MISC file first.")
            return
        if slot == "a":
            self.misc_data[MISC_SLOT_SUFFIX_OFFSET:MISC_SLOT_SUFFIX_OFFSET+len(SLOT_B)] = SLOT_A.ljust(len(SLOT_B), b'\x00')
        else:
            self.misc_data[MISC_SLOT_SUFFIX_OFFSET:MISC_SLOT_SUFFIX_OFFSET+len(SLOT_A)] = SLOT_B.ljust(len(SLOT_A), b'\x00')
        self.label.setText(f"Modified to Slot {slot.upper()} ✅")

    def save_file(self):
        if not self.misc_data:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Modified MISC", "modified_misc.bin", "BIN Files (*.bin)")
        if path:
            with open(path, "wb") as f:
                f.write(self.misc_data)
            QMessageBox.information(self, "Saved", f"File saved to:\n{path}")

    def load_firehose(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Firehose Programmer", "", "MBN Files (*.mbn)")
        if path:
            self.firehose_path = path
            QMessageBox.information(self, "Firehose Loaded", f"Firehose:\n{path}")

    def flash_misc(self):
        if not self.firehose_path:
            QMessageBox.warning(self, "Firehose Missing", "Please load firehose programmer first.")
            return
        if not self.misc_data:
            QMessageBox.warning(self, "MISC Missing", "Load and modify a misc file first.")
            return

        # Save temp file
        temp_path = "temp_misc_for_flash.bin"
        with open(temp_path, "wb") as f:
            f.write(self.misc_data)

        try:
            subprocess.run([
                "edl.exe",
                "--loader", self.firehose_path,
                "--memory", "ufs",
                "--upload", temp_path, "@misc"
            ], check=True)
            QMessageBox.information(self, "Success", "MISC flashed to device successfully!")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Flash Error", f"Failed to flash:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MiscEditor()
    window.show()
    sys.exit(app.exec_())
