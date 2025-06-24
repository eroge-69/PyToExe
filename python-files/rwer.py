import sys import socket from PyQt5.QtWidgets import ( QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox )

class LicenseWindow(QWidget): def init(self): super().init() self.setWindowTitle("License Verification") self.setFixedSize(400, 200)

layout = QVBoxLayout()

    # PC Name
    self.pc_label = QLabel("Your PC Name:")
    self.pc_name = QLineEdit()
    self.pc_name.setText(socket.gethostname())
    self.pc_name.setReadOnly(True)

    # License key input
    self.license_label = QLabel("Enter your license key:")
    self.license_input = QLineEdit()
    self.license_input.setPlaceholderText("Enter key here")

    # Check button
    self.check_btn = QPushButton("Check License")
    self.check_btn.clicked.connect(self.check_license)

    layout.addWidget(self.pc_label)
    layout.addWidget(self.pc_name)
    layout.addWidget(self.license_label)
    layout.addWidget(self.license_input)
    layout.addWidget(self.check_btn)

    self.setLayout(layout)

def check_license(self):
    key = self.license_input.text().strip()
    valid_keys = [
        "NETFLIX-3YTZ-VALIDKEY",
        "VIP-BGB-ACCESS",
        "BGB-TECH-UNLOCK"
    ]
    if key in valid_keys:
        QMessageBox.information(self, "License Activated", "✅ License is valid!\nExpires: License key is valid")
        self.close()  # Proceed to next step
    else:
        QMessageBox.critical(self, "License Failed", "❌ Invalid license key.\nAccess denied.")

if name == "main": app = QApplication(sys.argv) window = LicenseWindow() window.show() sys.exit(app.exec_())