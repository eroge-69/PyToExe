
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QTextEdit

class FRPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Android FRP App Launcher")
        self.setGeometry(300, 300, 400, 250)

        layout = QVBoxLayout()
        self.status = QLabel("🔌 Connect a device via USB")
        layout.addWidget(self.status)

        self.app_selector = QComboBox()
        self.app_selector.addItems(["Settings", "YouTube", "Chrome", "File Manager"])
        layout.addWidget(self.app_selector)

        self.execute_btn = QPushButton("📲 Launch App")
        self.execute_btn.clicked.connect(self.launch_app)
        layout.addWidget(self.execute_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def launch_app(self):
        app = self.app_selector.currentText()
        package_map = {
            "Settings": "com.android.settings/.Settings",
            "YouTube": "com.google.android.youtube/.HomeActivity",
            "Chrome": "com.android.chrome/.Main",
            "File Manager": "com.android.filemanager/.FileManager"
        }

        # Check if device is connected
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if "device" not in result.stdout.split("\n")[1]:
            self.output.append("❌ No device detected.")
            return

        self.output.append("✅ Device found. Trying to open " + app + "...")
        try:
            intent = f"adb shell am start -n {package_map[app]}"
            launch = subprocess.run(intent.split(), capture_output=True, text=True)
            self.output.append(launch.stdout)
        except Exception as e:
            self.output.append(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FRPApp()
    window.show()
    sys.exit(app.exec_())
