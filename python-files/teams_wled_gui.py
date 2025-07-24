# Teams WLED Monitor with Emoji Notifications and Current Color Display 🖥️✨

import subprocess, sys, os, json, time, threading

def install(package): subprocess.check_call([sys.executable, "-m", "pip", "install", package])
for pkg in ["requests", "pygetwindow", "PyQt5", "pywin32", "winshell"]:
    try: __import__(pkg if pkg != "pywin32" else "win32com.client")
    except: install(pkg)

import requests, pygetwindow as gw
from PyQt5 import QtWidgets, QtGui, QtCore
import win32com.client, winshell

CONFIG_PATH = "teams_wled_config.json"
settings = {
    "wled_ip": "192.168.1.100",
    "call_color": [255, 0, 0],
    "idle_color": [0, 255, 0],
    "threshold": 2,
    "auto_start": False,
    "tray_icon_path": "",
    "launch_minimized": False
}

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f: settings.update(json.load(f))

def set_wled_color(color):
    url = f"http://{settings['wled_ip']}/json/state"
    payload = {"seg": [{"col": [color]}]}
    try: requests.post(url, json=payload)
    except: pass

def get_current_color():
    try:
        url = f"http://{settings['wled_ip']}/json/state"
        response = requests.get(url, timeout=2)
        data = response.json()
        return data.get("seg", [{}])[0].get("col", [[0,0,0]])[0]
    except:
        return [0, 0, 0]

def count_teams_windows():
    return len([w for w in gw.getWindowsWithTitle("Teams") if "Meeting" in w.title or "Microsoft Teams" in w.title])

class TrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, window):
        super().__init__(icon)
        self.window = window
        self.setToolTip("Teams WLED Monitor")
        self.last_state = None
        menu = QtWidgets.QMenu()
        menu.addAction("Open Settings", window.show)
        menu.addAction("Exit", QtWidgets.qApp.quit)
        self.setContextMenu(menu)
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def monitor_loop(self):
        while True:
            count = count_teams_windows()
            state = "call" if count >= settings["threshold"] else "idle"

            if state != self.last_state:
                msg = ("🚨 Teams Alert", "🔴 You're in a meeting!") if state == "call" else ("💤 Teams Status", "🟢 You're idle.")
                self.showMessage(*msg, QtWidgets.QSystemTrayIcon.Information, 2000)
                self.last_state = state

            color = settings["call_color"] if state == "call" else settings["idle_color"]
            self.setToolTip(f"Teams Windows: {count}")
            set_wled_color(color)
            time.sleep(5)

class SettingsWidget(QtWidgets.QWidget):
    def __init__(self, mainwin):
        super().__init__()
        self.mainwin = mainwin
        layout = QtWidgets.QVBoxLayout()

        self.ip_input = QtWidgets.QLineEdit(settings["wled_ip"])
        layout.addWidget(QtWidgets.QLabel("WLED IP Address"))
        layout.addWidget(self.ip_input)

        self.threshold_spin = QtWidgets.QSpinBox()
        self.threshold_spin.setMinimum(1)
        self.threshold_spin.setValue(settings["threshold"])
        layout.addWidget(QtWidgets.QLabel("Teams Window Threshold"))
        layout.addWidget(self.threshold_spin)

        self.call_btn, self.call_swatch = self.color_picker("Choose Call Color", settings["call_color"])
        self.idle_btn, self.idle_swatch = self.color_picker("Choose Idle Color", settings["idle_color"])
        layout.addWidget(self.call_btn), layout.addWidget(self.call_swatch)
        layout.addWidget(self.idle_btn), layout.addWidget(self.idle_swatch)

        self.auto_start_box = QtWidgets.QCheckBox("Start with Windows")
        self.auto_start_box.setChecked(settings["auto_start"])
        layout.addWidget(self.auto_start_box)

        self.minimized_box = QtWidgets.QCheckBox("Launch Minimized")
        self.minimized_box.setChecked(settings["launch_minimized"])
        layout.addWidget(self.minimized_box)

        self.icon_btn = QtWidgets.QPushButton("Choose Tray Icon")
        self.icon_path_label = QtWidgets.QLabel(settings["tray_icon_path"] or "No icon selected")
        self.icon_btn.clicked.connect(self.pick_icon)
        layout.addWidget(self.icon_btn), layout.addWidget(self.icon_path_label)

        # 🟩 Current Color Display
        layout.addWidget(QtWidgets.QLabel("Current WLED Color"))
        self.current_swatch = QtWidgets.QLabel()
        self.current_swatch.setFixedSize(40, 20)
        self.current_swatch.setStyleSheet("border:1px solid #333")
        layout.addWidget(self.current_swatch)

        self.color_timer = QtCore.QTimer()
        self.color_timer.timeout.connect(self.refresh_current_color)
        self.color_timer.start(10000)
        self.refresh_current_color()

        save_btn = QtWidgets.QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def color_picker(self, label, rgb):
        btn = QtWidgets.QPushButton(label)
        swatch = QtWidgets.QLabel(); swatch.setFixedSize(40, 20)
        swatch.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border:1px solid #333")
        btn.clicked.connect(lambda: self.pick_color(btn, swatch, label))
        return btn, swatch

    def pick_color(self, btn, swatch, label):
        key = "call_color" if "Call" in label else "idle_color"
        c = QtWidgets.QColorDialog.getColor(QtGui.QColor(*settings[key]))
        if c.isValid():
            rgb = [c.red(), c.green(), c.blue()]
            settings[key] = rgb
            swatch.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border:1px solid #333")

    def refresh_current_color(self):
        rgb = get_current_color()
        self.current_swatch.setStyleSheet(f"background-color: rgb({rgb[0]}, {rgb[1]}, {rgb[2]}); border:1px solid #333")

    def pick_icon(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Tray Icon", "", "Images (*.png *.ico *.svg)")
        if path:
            settings["tray_icon_path"] = path
            self.icon_path_label.setText(path)
            icon = QtGui.QIcon(path)
            self.mainwin.tray.setIcon(icon)

    def save_settings(self):
        settings.update({
            "wled_ip": self.ip_input.text(),
            "threshold": self.threshold_spin.value(),
            "auto_start": self.auto_start_box.isChecked(),
            "launch_minimized": self.minimized_box.isChecked()
        })
        with open(CONFIG_PATH, "w") as f: json.dump(settings, f)

        if settings["auto_start"]:
            script_path = os.path.abspath(sys.argv[0])
            startup = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            shortcut = os.path.join(startup, "TeamsWLED.lnk")
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut_obj = shell.CreateShortcut(shortcut)
            shortcut_obj.TargetPath = sys.executable
            shortcut_obj.Arguments = f'"{script_path}"'
            shortcut_obj.WorkingDirectory = os.path.dirname(script_path)
            shortcut_obj.IconLocation = script_path
            shortcut_obj.save()

        QtWidgets.QMessageBox.information(self, "Saved", "✅ Settings have been saved.")

class ControlPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teams WLED Settings")
        self.resize(420, 360)
        icon = QtGui.QIcon(settings["tray_icon_path"]) if settings["tray_icon_path"] else QtGui.QIcon(QtGui.QPixmap(16,16))
        self.setWindowIcon(icon)

        layout = QtWidgets.QVBoxLayout()
        scroll = QtWidgets.QScrollArea(); scroll.setWidgetResizable(True)
        self.settings_widget = SettingsWidget(self)
        scroll.setWidget(self.settings_widget)
        layout.addWidget(scroll); self.setLayout(layout)

        self.tray = TrayApp(icon, self)
        self.tray.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage("Teams WLED", "📥 Minimized to tray", QtWidgets.QSystemTrayIcon.Information, 2000)

app = QtWidgets.QApplication([])
window = ControlPanel()
if not settings.get("launch_minimized", False): window.show()
sys.exit(app.exec_())