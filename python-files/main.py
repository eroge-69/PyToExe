import sys
import os
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer


class ScatterToXMLConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scatter to XML Converter - Light UI")
        self.setGeometry(200, 100, 850, 600)
        self.scatter_file = ""
        self.partitions = []

        self.setup_ui()

    def setup_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { height: 40px; width: 150px; font-size: 14px; }")

        # Tabs
        self.main_tab = QWidget()
        self.about_tab = QWidget()
        self.tabs.addTab(self.main_tab, "📁 Converter")
        self.tabs.addTab(self.about_tab, "👨‍💻 About Me")

        self.setup_main_tab()
        self.setup_about_tab()

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def setup_main_tab(self):
        layout = QVBoxLayout()

        self.label = QLabel("🔍 Select a scatter file to convert into XML format")
        self.label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(self.label)

        btn_layout = QHBoxLayout()

        self.select_button = QPushButton("📂 Select Scatter File")
        self.select_button.clicked.connect(self.load_scatter_file)
        btn_layout.addWidget(self.select_button)

        self.convert_button = QPushButton("💾 Convert to XML")
        self.convert_button.clicked.connect(self.convert_to_xml)
        self.convert_button.setEnabled(False)
        btn_layout.addWidget(self.convert_button)

        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Partition", "File", "Start Addr", "Size"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.main_tab.setLayout(layout)

    def setup_about_tab(self):
        layout = QVBoxLayout()
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setFont(QFont("Consolas", 10))
        about_text.setText(
            "👨‍💻 MD Shamim Hossain — aka Script Coder\n"
            "🚀 Full-Stack Developer | 🤖 AI & OSINT Automation Architect | 🔓 Mobile Unlock Specialist\n"
            "🔴 Founder of Red Hackers | 💥 Reverse Engineer | 🦠 Malware & Virus Analyst\n"
            "📡 Telegram Bot Developer | 🔐 PHP ionCube Decoder Specialist | 📂 Data Scraping Expert\n\n"
            "🧠 About Me\n"
            "I'm a passionate developer bridging software engineering, AI, offensive security, and mobile technology.\n"
            "I create tools that automate, secure, and unlock potential in the digital world.\n"
            "From Laravel SaaS platforms and Telegram bots to UFSTool-based mobile unlock systems and ionCube decryption tools,\n"
            "my work pushes boundaries while prioritizing ethical use.\n\n"
            "As the founder of Red Hackers, I lead research in:\n"
            "• AI-Driven Malware Analysis & Botnet Simulations\n"
            "• OSINT & MegaLeak Tracking\n"
            "• Mobile IMEI/FRP Unlock Tools\n"
            "• PHP ionCube Decoder Development\n"
            "• Telegram Automation & Data Scraping\n\n"
            "🔗 GitHub: https://github.com/laravelgpt"
        )
        layout.addWidget(about_text)
        self.about_tab.setLayout(layout)

    def load_scatter_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Scatter File", "", "Scatter Files (*.txt)")
        if path:
            self.scatter_file = path
            self.label.setText(f"✅ Loaded file: {os.path.basename(path)}")
            self.partitions = []
            self.table.setRowCount(0)
            QTimer.singleShot(100, self.process_scatter_file)

    def process_scatter_file(self):
        try:
            with open(self.scatter_file, "r") as f:
                lines = f.readlines()

            current = {}
            for line in lines:
                line = line.strip()
                if line.startswith("partition_name:"):
                    current = {"name": line.split(":")[1].strip()}
                elif line.startswith("file_name:"):
                    current["file"] = line.split(":")[1].strip()
                elif line.startswith("linear_start_addr:"):
                    current["start"] = line.split(":")[1].strip()
                elif line.startswith("partition_size:"):
                    current["size"] = line.split(":")[1].strip()
                    self.partitions.append(current.copy())
                    self.add_table_row(current)

            self.convert_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_table_row(self, part):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(part.get("name", "")))
        self.table.setItem(row, 1, QTableWidgetItem(part.get("file", "")))
        self.table.setItem(row, 2, QTableWidgetItem(part.get("start", "")))
        self.table.setItem(row, 3, QTableWidgetItem(part.get("size", "")))

    def convert_to_xml(self):
        if not self.partitions:
            QMessageBox.warning(self, "No Data", "No partition data available.")
            return

        output_path, _ = QFileDialog.getSaveFileName(self, "Save XML File", "", "XML Files (*.xml)")
        if not output_path:
            return

        try:
            root = ET.Element("Partitions")
            for part in self.partitions:
                p = ET.SubElement(root, "Partition")
                ET.SubElement(p, "Name").text = part.get("name", "")
                ET.SubElement(p, "File").text = part.get("file", "")
                ET.SubElement(p, "StartAddress").text = part.get("start", "")
                ET.SubElement(p, "Size").text = part.get("size", "")

            tree = ET.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            QMessageBox.information(self, "Success", f"✅ XML saved to:\n{output_path}")

            # Open the folder in file explorer
            folder = os.path.dirname(output_path)
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                os.system(f"open '{folder}'")
            else:
                os.system(f"xdg-open '{folder}'")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScatterToXMLConverter()
    window.show()
    sys.exit(app.exec_())
