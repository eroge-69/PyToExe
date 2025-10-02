import sys
import os
import ctypes
from ctypes import wintypes
import struct
import psutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Windows API constants
PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008

class MemoryScanner:
    def __init__(self):
        self.process_handle = None
        self.current_pid = None
        self.scan_results = []
        
    def open_process(self, pid):
        """Open a process for memory operations"""
        try:
            if self.process_handle:
                ctypes.windll.kernel32.CloseHandle(self.process_handle)
                
            self.process_handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION, 
                False, pid
            )
            
            if self.process_handle:
                self.current_pid = pid
                return True
            return False
        except:
            return False
    
    def read_memory(self, address, data_type):
        """Read memory from the process"""
        try:
            if data_type == "4 Bytes":
                buffer = ctypes.c_uint32()
                bytes_read = ctypes.c_size_t()
                if ctypes.windll.kernel32.ReadProcessMemory(
                    self.process_handle, 
                    ctypes.c_void_p(address), 
                    ctypes.byref(buffer), 
                    ctypes.sizeof(buffer), 
                    ctypes.byref(bytes_read)
                ):
                    return buffer.value
            elif data_type == "Float":
                buffer = ctypes.c_float()
                bytes_read = ctypes.c_size_t()
                if ctypes.windll.kernel32.ReadProcessMemory(
                    self.process_handle, 
                    ctypes.c_void_p(address), 
                    ctypes.byref(buffer), 
                    ctypes.sizeof(buffer), 
                    ctypes.byref(bytes_read)
                ):
                    return buffer.value
        except:
            pass
        return None
    
    def write_memory(self, address, value, data_type):
        """Write memory to the process"""
        try:
            if data_type == "4 Bytes":
                buffer = ctypes.c_uint32(int(value))
                bytes_written = ctypes.c_size_t()
                return ctypes.windll.kernel32.WriteProcessMemory(
                    self.process_handle, 
                    ctypes.c_void_p(address), 
                    ctypes.byref(buffer), 
                    ctypes.sizeof(buffer), 
                    ctypes.byref(bytes_written)
                )
            elif data_type == "Float":
                buffer = ctypes.c_float(float(value))
                bytes_written = ctypes.c_size_t()
                return ctypes.windll.kernel32.WriteProcessMemory(
                    self.process_handle, 
                    ctypes.c_void_p(address), 
                    ctypes.byref(buffer), 
                    ctypes.sizeof(buffer), 
                    ctypes.byref(bytes_written)
                )
        except:
            pass
        return False

class CheatEngine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scanner = MemoryScanner()
        self.frozen_addresses = {}
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Python Cheat Engine")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Process selection
        process_group = QGroupBox("Process Selection")
        process_layout = QHBoxLayout(process_group)
        
        self.process_combo = QComboBox()
        self.process_combo.setMinimumWidth(300)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_processes)
        self.attach_btn = QPushButton("Attach")
        self.attach_btn.clicked.connect(self.attach_process)
        
        process_layout.addWidget(QLabel("Process:"))
        process_layout.addWidget(self.process_combo)
        process_layout.addWidget(self.refresh_btn)
        process_layout.addWidget(self.attach_btn)
        process_layout.addStretch()
        
        layout.addWidget(process_group)
        
        # Scan section
        scan_group = QGroupBox("Memory Scanner")
        scan_layout = QVBoxLayout(scan_group)
        
        # Scan options
        options_layout = QHBoxLayout()
        self.value_type = QComboBox()
        self.value_type.addItems(["4 Bytes", "Float"])
        self.scan_type = QComboBox()
        self.scan_type.addItems(["Exact Value", "Changed", "Increased", "Decreased"])
        
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Value to scan for...")
        
        self.first_scan_btn = QPushButton("First Scan")
        self.first_scan_btn.clicked.connect(self.first_scan)
        self.next_scan_btn = QPushButton("Next Scan")
        self.next_scan_btn.clicked.connect(self.next_scan)
        self.next_scan_btn.setEnabled(False)
        
        options_layout.addWidget(QLabel("Type:"))
        options_layout.addWidget(self.value_type)
        options_layout.addWidget(QLabel("Scan Type:"))
        options_layout.addWidget(self.scan_type)
        options_layout.addWidget(QLabel("Value:"))
        options_layout.addWidget(self.value_input)
        options_layout.addWidget(self.first_scan_btn)
        options_layout.addWidget(self.next_scan_btn)
        
        scan_layout.addLayout(options_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.add_to_address_list)
        scan_layout.addWidget(self.results_list)
        
        layout.addWidget(scan_group)
        
        # Address list
        address_group = QGroupBox("Address List")
        address_layout = QVBoxLayout(address_group)
        
        self.address_table = QTableWidget()
        self.address_table.setColumnCount(5)
        self.address_table.setHorizontalHeaderLabels(["Address", "Value", "Type", "Frozen", "Description"])
        self.address_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        address_layout.addWidget(self.address_table)
        
        # Address controls
        controls_layout = QHBoxLayout()
        self.change_btn = QPushButton("Change Value")
        self.change_btn.clicked.connect(self.change_value)
        self.freeze_btn = QPushButton("Freeze/Unfreeze")
        self.freeze_btn.clicked.connect(self.toggle_freeze)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_address)
        
        controls_layout.addWidget(self.change_btn)
        controls_layout.addWidget(self.freeze_btn)
        controls_layout.addWidget(self.delete_btn)
        controls_layout.addStretch()
        
        address_layout.addLayout(controls_layout)
        layout.addWidget(address_group)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Attach to a process to begin")
        
        # Refresh processes on start
        self.refresh_processes()
        
    def refresh_processes(self):
        """Refresh the list of running processes"""
        self.process_combo.clear()
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes.append(f"{proc.info['pid']}: {proc.info['name']}")
            except:
                pass
        
        self.process_combo.addItems(sorted(processes, key=lambda x: x.lower()))
        
    def attach_process(self):
        """Attach to the selected process"""
        if not self.process_combo.currentText():
            QMessageBox.warning(self, "Error", "No process selected")
            return
            
        pid = int(self.process_combo.currentText().split(":")[0])
        
        if self.scanner.open_process(pid):
            self.status_bar.showMessage(f"Attached to process: {self.process_combo.currentText()}")
            self.first_scan_btn.setEnabled(True)
        else:
            QMessageBox.warning(self, "Error", "Failed to attach to process")
            
    def first_scan(self):
        """Perform first memory scan"""
        if not self.scanner.process_handle:
            QMessageBox.warning(self, "Error", "No process attached")
            return
            
        if self.scan_type.currentText() == "Exact Value" and not self.value_input.text():
            QMessageBox.warning(self, "Error", "Enter a value to scan for")
            return
            
        # For demonstration, we'll simulate scanning
        # In a real implementation, you would scan the process memory
        self.simulate_first_scan()
        
    def simulate_first_scan(self):
        """Simulate finding memory addresses (for demonstration)"""
        self.results_list.clear()
        
        # Generate some fake addresses for demonstration
        base_address = 0x400000
        num_results = 50
        
        for i in range(num_results):
            address = base_address + (i * 4)
            value = 100 + i * 10
            item = QListWidgetItem(f"0x{address:08X} - Value: {value}")
            item.setData(Qt.UserRole, {"address": address, "value": value})
            self.results_list.addItem(item)
            
        self.scanner.scan_results = [base_address + (i * 4) for i in range(num_results)]
        self.next_scan_btn.setEnabled(True)
        self.status_bar.showMessage(f"First scan completed: {num_results} results found")
        
    def next_scan(self):
        """Perform next scan to filter results"""
        if not self.scanner.scan_results:
            return
            
        # Simulate filtering results
        current_results = self.scanner.scan_results
        filtered_results = current_results[:len(current_results) // 2]  # Keep half
        
        self.results_list.clear()
        for i, address in enumerate(filtered_results):
            value = 150 + i * 5  # Simulate changed values
            item = QListWidgetItem(f"0x{address:08X} - Value: {value}")
            item.setData(Qt.UserRole, {"address": address, "value": value})
            self.results_list.addItem(item)
            
        self.scanner.scan_results = filtered_results
        self.status_bar.showMessage(f"Next scan completed: {len(filtered_results)} results remaining")
        
    def add_to_address_list(self, item):
        """Add selected address to the address list"""
        data = item.data(Qt.UserRole)
        if not data:
            return
            
        address = data["address"]
        value = data["value"]
        value_type = self.value_type.currentText()
        
        # Check if address already exists
        for row in range(self.address_table.rowCount()):
            if self.address_table.item(row, 0).text() == f"0x{address:08X}":
                return
                
        # Add to table
        row = self.address_table.rowCount()
        self.address_table.insertRow(row)
        
        self.address_table.setItem(row, 0, QTableWidgetItem(f"0x{address:08X}"))
        self.address_table.setItem(row, 1, QTableWidgetItem(str(value)))
        self.address_table.setItem(row, 2, QTableWidgetItem(value_type))
        
        # Frozen checkbox
        frozen_checkbox = QCheckBox()
        frozen_checkbox.stateChanged.connect(lambda state, addr=address: self.update_frozen_status(addr, state))
        frozen_cell = QWidget()
        frozen_layout = QHBoxLayout(frozen_cell)
        frozen_layout.addWidget(frozen_checkbox)
        frozen_layout.setAlignment(Qt.AlignCenter)
        frozen_layout.setContentsMargins(0, 0, 0, 0)
        frozen_cell.setLayout(frozen_layout)
        self.address_table.setCellWidget(row, 3, frozen_cell)
        
        self.address_table.setItem(row, 4, QTableWidgetItem("Added from scan"))
        
        self.status_bar.showMessage(f"Added address 0x{address:08X} to address list")
        
    def change_value(self):
        """Change value of selected address"""
        selected = self.address_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "No address selected")
            return
            
        address_item = self.address_table.item(selected, 0)
        current_value_item = self.address_table.item(selected, 1)
        type_item = self.address_table.item(selected, 2)
        
        if not all([address_item, current_value_item, type_item]):
            return
            
        address_text = address_item.text()
        current_value = current_value_item.text()
        value_type = type_item.text()
        
        # Get new value
        new_value, ok = QInputDialog.getText(
            self, "Change Value", 
            f"New value for {address_text}:", 
            text=current_value
        )
        
        if ok and new_value:
            # In real implementation: self.scanner.write_memory(address, new_value, value_type)
            current_value_item.setText(new_value)
            self.status_bar.showMessage(f"Changed {address_text} to {new_value}")
            
    def toggle_freeze(self):
        """Toggle freeze on selected address"""
        selected = self.address_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "No address selected")
            return
            
        address_item = self.address_table.item(selected, 0)
        if not address_item:
            return
            
        address_text = address_item.text()
        frozen_widget = self.address_table.cellWidget(selected, 3)
        frozen_checkbox = frozen_widget.findChild(QCheckBox)
        
        if frozen_checkbox.isChecked():
            frozen_checkbox.setChecked(False)
            self.status_bar.showMessage(f"Unfrozen {address_text}")
        else:
            frozen_checkbox.setChecked(True)
            self.status_bar.showMessage(f"Frozen {address_text}")
            
    def update_frozen_status(self, address, state):
        """Update frozen status for an address"""
        if state == Qt.Checked:
            self.frozen_addresses[address] = True
        else:
            self.frozen_addresses.pop(address, None)
            
    def delete_address(self):
        """Delete selected address from list"""
        selected = self.address_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Error", "No address selected")
            return
            
        address_item = self.address_table.item(selected, 0)
        if address_item:
            address_text = address_item.text()
            self.address_table.removeRow(selected)
            self.status_bar.showMessage(f"Removed {address_text} from address list")

def main():
    app = QApplication(sys.argv)
    
    # Set dark theme for Cheat Engine-like appearance
    app.setStyle('Fusion')
    
    # Create and show window
    window = CheatEngine()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()