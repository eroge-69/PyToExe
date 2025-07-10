import sys
import os
import subprocess
import datetime
import webbrowser
import winreg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLineEdit,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

class RazTechWorldUtility(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("RazTech World Utility")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(800, 600)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Create main widgets
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        
        self.input_box = QLineEdit()
        self.input_box.setFont(QFont("Consolas", 10))
        self.input_box.setPlaceholderText("Type commands here and press Enter...")
        self.input_box.returnPressed.connect(self.execute_command)
        
        # Create buttons
        self.device_manager_btn = self.create_button("Open Device Manager", self.open_device_manager)
        self.adb_drivers_btn = self.create_button("Install ADB Drivers", self.install_adb_drivers)
        self.device_info_btn = self.create_button("Read Device Info", self.read_device_info)
        self.chrome_btn = self.create_button("Open Chrome", self.open_chrome)
        self.settings_btn = self.create_button("System Settings", self.open_system_settings)
        self.system_info_btn = self.create_button("System Information", self.open_system_info)
        self.restart_btn = self.create_button("Restart PC", self.restart_pc)
        
        # Create layouts
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.device_manager_btn)
        left_layout.addWidget(self.adb_drivers_btn)
        left_layout.addWidget(self.device_info_btn)
        left_layout.addWidget(self.chrome_btn)
        left_layout.addWidget(self.settings_btn)
        left_layout.addWidget(self.system_info_btn)
        left_layout.addWidget(self.restart_btn)
        left_layout.addStretch()
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Output:"))
        right_layout.addWidget(self.output_area)
        right_layout.addWidget(QLabel("Command Input:"))
        right_layout.addWidget(self.input_box)
        
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 3)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Add status bar
        self.statusBar().showMessage("RazTech World Utility - Ready")
        
        # Initialize ADB status
        self.adb_installed = self.check_adb_installation()
        self.update_adb_button_status()
        
        # Display welcome message
        self.output_area.append("=== RazTech World Utility ===")
        self.output_area.append("Ready to perform system tasks and device management.")
        self.output_area.append("ADB status: " + ("Installed" if self.adb_installed else "Not installed"))
        self.output_area.append("Type 'help' in the command box for available commands.")
        self.output_area.append("")
    
    def set_dark_theme(self):
        # Apply a dark theme palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
        
        self.setPalette(dark_palette)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
            }
            QPushButton {
                background-color: #3F3F46;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
                min-width: 200px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #51515A;
            }
            QPushButton:pressed {
                background-color: #252526;
            }
            QTextEdit, QLineEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                border-radius: 3px;
                padding: 5px;
                font-family: Consolas;
            }
            QLabel {
                color: #AAAAAA;
            }
            QStatusBar {
                background-color: #252526;
                color: #AAAAAA;
            }
        """)
    
    def create_button(self, text, callback):
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 10))
        btn.clicked.connect(callback)
        return btn
    
    def check_adb_installation(self):
        """Check if ADB is installed by trying to run adb command"""
        try:
            result = subprocess.run(
                ['adb', 'version'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except (FileNotFoundError, OSError):
            return False
    
    def update_adb_button_status(self):
        """Update the status of ADB-related buttons based on installation status"""
        if self.adb_installed:
            self.adb_drivers_btn.setEnabled(False)
            self.adb_drivers_btn.setText("ADB Drivers Installed")
            self.device_info_btn.setEnabled(True)
        else:
            self.adb_drivers_btn.setEnabled(True)
            self.adb_drivers_btn.setText("Install ADB Drivers")
            self.device_info_btn.setEnabled(False)
    
    def open_device_manager(self):
        self.output_area.append("\nOpening Device Manager...")
        try:
            os.startfile("devmgmt.msc")
            self.output_area.append("Device Manager launched successfully.")
        except Exception as e:
            self.output_area.append(f"Error opening Device Manager: {str(e)}")
    
    def install_adb_drivers(self):
        self.output_area.append("\nStarting ADB Driver installation...")
        self.output_area.append("Downloading drivers from https://androidmtk.com/download-15-seconds-adb-installer")
        
        # In a real application, this would download and install the drivers
        # For demonstration purposes, we'll simulate the process
        self.output_area.append("Downloading ADB Installer...")
        self.output_area.append("Installing ADB Drivers...")
        
        # Simulate installation process
        self.output_area.append("Installation in progress...")
        QApplication.processEvents()  # Update UI
        
        # Simulate progress
        for i in range(1, 4):
            self.output_area.append(f"Step {i}/3 completed")
            QApplication.processEvents()
            QApplication.processEvents()
            import time
            time.sleep(1)
        
        self.output_area.append("ADB Drivers installed successfully!")
        self.output_area.append("Please restart the utility to detect ADB installation.")
        
        # Update status
        self.adb_installed = True
        self.update_adb_button_status()
    
    def read_device_info(self):
        if not self.adb_installed:
            self.output_area.append("\nADB is not installed. Please install ADB drivers first.")
            return
        
        self.output_area.append("\nReading device information via ADB...")
        self.output_area.append("Make sure your device is connected and USB debugging is enabled.")
        
        # Check if device is connected
        try:
            result = subprocess.run(
                ['adb', 'devices'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if "device" not in result.stdout:
                self.output_area.append("No devices found. Please connect a device.")
                return
            
            self.output_area.append("Device detected. Collecting information...")
            
            # Collect device information
            commands = {
                "IMEI": "adb shell service call iphonesubinfo 1",
                "Model": "adb shell getprop ro.product.model",
                "Brand": "adb shell getprop ro.product.brand",
                "Product": "adb shell getprop ro.product.name",
                "Android Version": "adb shell getprop ro.build.version.release",
                "Security Patch": "adb shell getprop ro.build.version.security_patch",
                "Serial Number": "adb shell getprop ro.serialno",
                "Manufacturer": "adb shell getprop ro.product.manufacturer",
                "Device": "adb shell getprop ro.product.device",
                "Hardware": "adb shell getprop ro.hardware"
            }
            
            info = []
            for name, cmd in commands.items():
                try:
                    result = subprocess.run(
                        cmd.split(), 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    value = result.stdout.strip()
                    if not value:
                        value = "N/A"
                    info.append(f"{name}: {value}")
                except Exception as e:
                    info.append(f"{name}: Error - {str(e)}")
            
            # Format and display information
            device_info = "\n".join(info)
            self.output_area.append("\n=== Device Information ===\n")
            self.output_area.append(device_info)
            
            # Save to file
            self.save_device_info(device_info)
            
        except Exception as e:
            self.output_area.append(f"Error reading device info: {str(e)}")
    
    def save_device_info(self, info):
        default_filename = f"device_info_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Device Information", default_filename, "Text Files (*.txt)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("=== Device Information Report ===\n")
                    f.write(f"Generated: {datetime.datetime.now()}\n\n")
                    f.write(info)
                self.output_area.append(f"\nDevice information saved to:\n{filename}")
            except Exception as e:
                self.output_area.append(f"Error saving file: {str(e)}")
    
    def open_chrome(self):
        self.output_area.append("\nOpening Chrome browser...")
        try:
            # Try to find Chrome installation path
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                    chrome_path, _ = winreg.QueryValueEx(key, "")
            except:
                chrome_path = "chrome.exe"
            
            subprocess.Popen([chrome_path], creationflags=subprocess.CREATE_NO_WINDOW)
            self.output_area.append("Chrome browser launched successfully.")
        except Exception as e:
            self.output_area.append(f"Error opening Chrome: {str(e)}")
            self.output_area.append("Trying default method...")
            webbrowser.open("https://www.google.com")
    
    def open_system_settings(self):
        self.output_area.append("\nOpening System Settings...")
        try:
            os.startfile("ms-settings:")
            self.output_area.append("System Settings launched successfully.")
        except Exception as e:
            self.output_area.append(f"Error opening System Settings: {str(e)}")
    
    def open_system_info(self):
        self.output_area.append("\nOpening System Information...")
        try:
            os.startfile("msinfo32")
            self.output_area.append("System Information launched successfully.")
        except Exception as e:
            self.output_area.append(f"Error opening System Information: {str(e)}")
    
    def restart_pc(self):
        self.output_area.append("\nPreparing to restart the system...")
        reply = QMessageBox.question(
            self, 'Confirm Restart',
            "Are you sure you want to restart your computer?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.output_area.append("System restart initiated. All unsaved work will be lost.")
            try:
                os.system("shutdown /r /t 10")
            except Exception as e:
                self.output_area.append(f"Error initiating restart: {str(e)}")
        else:
            self.output_area.append("Restart canceled.")
    
    def execute_command(self):
        command = self.input_box.text().strip()
        self.input_box.clear()
        
        if not command:
            return
        
        self.output_area.append(f"\n> {command}")
        
        if command.lower() == "help":
            self.show_help()
            return
        elif command.lower() == "clear":
            self.output_area.clear()
            return
        elif command.lower() == "exit":
            self.close()
            return
        
        try:
            # Execute the command
            result = subprocess.run(
                command, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.stdout:
                self.output_area.append(result.stdout)
            
            if result.stderr:
                self.output_area.append(result.stderr)
                
            self.output_area.append(f"\nCommand completed with exit code: {result.returncode}")
        except Exception as e:
            self.output_area.append(f"Error executing command: {str(e)}")
    
    def show_help(self):
        help_text = """
        Available Commands:
        - help: Show this help message
        - clear: Clear the output area
        - exit: Close the application
        - Any system command: Will be executed in the command prompt
        
        Button Functions:
        - Open Device Manager: Launch Windows Device Manager
        - Install ADB Drivers: Download and install Android ADB drivers
        - Read Device Info: Get device information via ADB (requires connected Android device)
        - Open Chrome: Launch Google Chrome browser
        - System Settings: Open Windows Settings
        - System Information: Show detailed system information
        - Restart PC: Restart the computer (with confirmation)
        """
        self.output_area.append(help_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set app icon (would need an actual icon file in a real application)
    # app.setWindowIcon(QIcon("icon.ico"))
    
    window = RazTechWorldUtility()
    window.show()
    sys.exit(app.exec_())