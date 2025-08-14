
import sys
import os
import json
import subprocess
import ast
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QFormLayout, QLineEdit,
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
    QHBoxLayout, QSplitter, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt


class InputModuleEditor(QWidget):
    def __init__(self, title, data, original_dict_str=None):
        super().__init__()
        self.title = title
        self.data = data
        self.original_dict_str = original_dict_str
        self.widgets = {}
        self.color_windows = {}
        
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        self.layout = QFormLayout(content_widget)
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        self._populate_form()

    def _populate_form(self):
        """Populate the form with widgets based on data types"""
        for key, value in self.data.items():
            if isinstance(value, bool):
                cb = QCheckBox()
                cb.setChecked(value)
                self.widgets[key] = cb
                self.layout.addRow(key, cb)

            elif isinstance(value, int):
                sb = QSpinBox()
                sb.setMinimum(-999999)
                sb.setMaximum(999999)
                sb.setValue(value)
                self.widgets[key] = sb
                self.layout.addRow(key, sb)

            elif isinstance(value, float):
                dsb = QDoubleSpinBox()
                dsb.setDecimals(4)
                dsb.setMinimum(-999999.0)
                dsb.setMaximum(999999.0)
                dsb.setValue(value)
                self.widgets[key] = dsb
                self.layout.addRow(key, dsb)

            elif isinstance(value, str):
                le = QLineEdit(value)
                self.widgets[key] = le
                self.layout.addRow(key, le)

            elif isinstance(value, dict) and key == "colour":
                col_button = QPushButton("Edit Colours...")
                col_button.clicked.connect(lambda checked, v=value, k=key: self.open_color_editor(v, k))
                self.widgets[key] = value
                self.layout.addRow("Colour Dictionary", col_button)

            else:
                # For unsupported types, show as read-only text
                label = QLabel(f"{type(value).__name__}: {str(value)[:100]}...")
                label.setWordWrap(True)
                self.layout.addRow(f"{key}:", label)
                # Store original value
                self.widgets[key] = value

    def open_color_editor(self, color_dict, key):
        """Open a simple color editor dialog"""
        # This is a placeholder - you might want to implement a proper color editor
        QMessageBox.information(self, "Color Editor", f"Color editing for {key} not yet implemented")

    def get_data(self):
        """Get updated data from all widgets"""
        updated = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, QCheckBox):
                updated[key] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                updated[key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                updated[key] = widget.value()
            elif isinstance(widget, QLineEdit):
                text = widget.text()
                # Try to convert to appropriate type
                try:
                    # Try to evaluate as Python literal first
                    evaluated = ast.literal_eval(text)
                    updated[key] = evaluated
                except (ValueError, SyntaxError):
                    # Keep as string if can't evaluate
                    updated[key] = text
            else:
                # For other types (like dicts), keep original value
                updated[key] = widget
        return updated


class TableEditor(QWidget):
    def __init__(self, name, table_data):
        super().__init__()
        self.name = name
        self.table_data = table_data if table_data else [[""]]
        
        layout = QVBoxLayout(self)
        
        # Add/Remove row buttons
        button_layout = QHBoxLayout()
        add_row_btn = QPushButton("Add Row")
        remove_row_btn = QPushButton("Remove Row")
        add_row_btn.clicked.connect(self.add_row)
        remove_row_btn.clicked.connect(self.remove_row)
        button_layout.addWidget(add_row_btn)
        button_layout.addWidget(remove_row_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Ensure table_data is not empty
        if not self.table_data or not self.table_data[0]:
            self.table_data = [[""]]

        self.table = QTableWidget(len(self.table_data), len(self.table_data[0]))
        
        # Set headers based on data structure
        if name == "plot_list":
            headers = ["Object", "Parameter", "Page", "Plot Name", "Color", "Line Style", "Error Bands", "Normalize", "Norm Value", "Label"]
        elif name == "measured_list":
            headers = ["Name", "Parameter", "Page", "Plot Name", "Color", "Line Style", "Error Bands", "Normalize", "Norm Value"]
        elif name == "page_list":
            headers = ["Page Name", "Layout", "Orientation"]
        else:
            headers = [f"Col {i}" for i in range(len(self.table_data[0]))]
        
        if len(headers) > self.table.columnCount():
            self.table.setColumnCount(len(headers))
        
        self.table.setHorizontalHeaderLabels(headers[:self.table.columnCount()])
        
        # Populate table
        for i, row in enumerate(self.table_data):
            for j, val in enumerate(row):
                if j < self.table.columnCount():
                    self.table.setItem(i, j, QTableWidgetItem(str(val)))
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.table)

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.setRowCount(row_count + 1)
        
        # Add empty items to new row
        for j in range(self.table.columnCount()):
            self.table.setItem(row_count, j, QTableWidgetItem(""))

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0 and self.table.rowCount() > 1:
            self.table.removeRow(current_row)

    def get_data(self):
        """Get table data as list of lists"""
        updated = []
        for i in range(self.table.rowCount()):
            row = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                text = item.text() if item else ""
                
                # Try to convert to appropriate type
                if text.strip():
                    try:
                        # Try to evaluate as Python literal
                        evaluated = ast.literal_eval(text)
                        row.append(evaluated)
                    except (ValueError, SyntaxError):
                        # Keep as string if can't evaluate
                        row.append(text)
                else:
                    row.append(text)
            updated.append(row)
        return updated


class ConfigFileManager:
    """Handles reading and writing the Variables_Model_Update.py file"""
    
    @staticmethod
    def read_config_file(filepath):
        """Read and parse the config file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Execute to get values
        namespace = {}
        exec(content, namespace)
        
        # Extract relevant variables
        config_data = {}
        for name in namespace:
            if (name.startswith('input_data_modul') or 
                name in ['plot_list', 'measured_list', 'page_list']):
                config_data[name] = namespace[name]
        
        return config_data, content

    @staticmethod
    def write_config_file(filepath, config_data, original_content):
        """Write updated config back to file preserving format"""
        lines = original_content.split('\n')
        new_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line starts a variable assignment we care about
            assignment_match = re.match(r'^(\w+)\s*=\s*', line.strip())
            if assignment_match:
                var_name = assignment_match.group(1)
                
                if var_name in config_data:
                    # Replace this variable's definition
                    new_value = config_data[var_name]
                    
                    if isinstance(new_value, dict):
                        # Handle dictionary formatting
                        new_lines.append(f"{var_name} = {ConfigFileManager._format_dict(new_value, var_name)}")
                    elif isinstance(new_value, list):
                        # Handle list formatting
                        new_lines.append(f"{var_name} = {ConfigFileManager._format_list(new_value, var_name)}")
                    else:
                        new_lines.append(f"{var_name} = {repr(new_value)}")
                    
                    # Skip lines until we find the end of this assignment
                    bracket_count = line.count('{') - line.count('}') + line.count('[') - line.count(']')
                    i += 1
                    while i < len(lines) and bracket_count > 0:
                        next_line = lines[i]
                        bracket_count += (next_line.count('{') - next_line.count('}') + 
                                        next_line.count('[') - next_line.count(']'))
                        i += 1
                    i -= 1  # Back up one since we'll increment at end of loop
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
            
            i += 1
        
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))

    @staticmethod
    def _format_dict(d, var_name):
        """Format dictionary with proper indentation"""
        if var_name == 'input_data_modul00':
            # Special formatting for module 00
            items = []
            for k, v in d.items():
                if isinstance(v, str):
                    items.append(f"                      '{k}' : {repr(v)} ,")
                else:
                    items.append(f"                      '{k}' : {repr(v)} ,")
            return "{ " + "\n".join(items) + "\n    }"
        
        elif "colour" in var_name or (isinstance(d, dict) and "red" in d):
            # Color dictionary formatting
            items = []
            for k, v in d.items():
                items.append(f"                        \"{k}\": {v},")
            return "{\n" + "\n".join(items) + "\n                        }"
        
        else:
            # Default dictionary formatting
            items = []
            for k, v in d.items():
                items.append(f"                      \"{k}\" : {repr(v)} ,")
            return "{ " + "\n".join(items) + "\n                    }"

    @staticmethod
    def _format_list(lst, var_name):
        """Format list with proper indentation"""
        if not lst:
            return "[]"
        
        if var_name in ['plot_list', 'measured_list']:
            # Multi-line list formatting for plot/measured lists
            items = []
            for item in lst:
                items.append(f"    {repr(item)},")
            return "[\n" + "\n".join(items) + "\n]"
        elif var_name == 'page_list':
            # Page list formatting
            items = []
            for item in lst:
                items.append(f"    {repr(item)},")
            return "[\n" + "\n".join(items) + "\n]"
        else:
            # Single line for simple lists
            return repr(lst)


class ConfigEditorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Variables Model Update Editor")
        self.resize(1400, 800)
        
        self.config_file = "Variables_Model_Update.py"
        self.config_data = {}
        self.original_content = ""
        
        # Initialize UI
        self.init_ui()
        self.load_config()

    def init_ui(self):
        # Main layout with splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left Panel (buttons)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # File operations
        load_btn = QPushButton("📂 Load Config File")
        load_btn.clicked.connect(self.load_config)
        load_btn.setMinimumHeight(40)
        left_layout.addWidget(load_btn)
        
        save_btn = QPushButton("💾 Save to File")
        save_btn.clicked.connect(self.save_config)
        save_btn.setMinimumHeight(40)
        left_layout.addWidget(save_btn)
     
        left_layout.addWidget(QLabel(""))  # Spacer
        
        # Script execution buttons
        run0_btn = QPushButton("▶️ Run MEM to CSV")
        run0_btn.clicked.connect(lambda: self.run_script("membatch.py"))
        run0_btn.setMinimumHeight(40)
        left_layout.addWidget(run0_btn)
        
        left_layout.addWidget(QLabel(""))  # Spacer

        run1_btn = QPushButton("▶️ Run Step 1-4")
        run1_btn.clicked.connect(lambda: self.run_script("Step 1_4 Convert & Calculate.py"))
        run1_btn.setMinimumHeight(40)
        left_layout.addWidget(run1_btn)
        
        run2_btn = QPushButton("▶️ Run Step 5")
        run2_btn.clicked.connect(lambda: self.run_script("Step 5 Import to PF.py"))
        run2_btn.setMinimumHeight(40)
        left_layout.addWidget(run2_btn)

        left_layout.addWidget(QLabel(""))  # Spacer

        run3_btn = QPushButton("▶️ Run Files Server")
        run3_btn.clicked.connect(lambda: self.run_script("files.py"))
        run3_btn.setMinimumHeight(40)
        left_layout.addWidget(run3_btn)

        run4_btn = QPushButton("▶️ Run Plot V11")
        run4_btn.clicked.connect(lambda: self.run_script("v11.py"))
        run4_btn.setMinimumHeight(40)
        left_layout.addWidget(run4_btn)

        
        left_layout.addWidget(QLabel(""))  # Spacer
        
        mem_btn = QPushButton("📁 Open HIOKI MEM")
        mem_btn.clicked.connect(lambda: self.open_folder("HIOKI MEM"))
        mem_btn.setMinimumHeight(40)
        left_layout.addWidget(mem_btn)

        csv_btn = QPushButton("📁 Open HIOKI CSV")
        csv_btn.clicked.connect(lambda: self.open_folder("HIOKI CSV"))
        csv_btn.setMinimumHeight(40)
        left_layout.addWidget(csv_btn)
        
        final_btn = QPushButton("📁 Open Final Folder")
        final_btn.clicked.connect(lambda: self.open_folder("Final Folder"))
        final_btn.setMinimumHeight(40)
        left_layout.addWidget(final_btn)
        
        left_layout.addStretch()  # Push buttons to top
        
        main_splitter.addWidget(left_panel)

        # Right Panel (Tabs)
        self.tabs = QTabWidget()
        main_splitter.addWidget(self.tabs)
        main_splitter.setStretchFactor(1, 4)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(main_splitter)

        self.editors = {}

    def load_config(self):
        """Load the configuration file"""
        try:
            if not os.path.exists(self.config_file):
                QMessageBox.warning(self, "File Not Found", f"Config file '{self.config_file}' not found")
                return
            
            self.config_data, self.original_content = ConfigFileManager.read_config_file(self.config_file)
            
            # Clear existing tabs
            self.tabs.clear()
            self.editors.clear()
            
            # Create tabs for each config section
            module_vars = {k: v for k, v in self.config_data.items() if k.startswith('input_data_modul')}
            list_vars = {k: v for k, v in self.config_data.items() if k in ['plot_list', 'measured_list', 'page_list']}
            
            # Add module editors
            for name, data in module_vars.items():
                display_name = name.replace('input_data_modul', 'Module ')
                editor = InputModuleEditor(display_name, data)
                self.editors[name] = editor
                self.tabs.addTab(editor, display_name)
            
            # Add list editors
            for name, data in list_vars.items():
                display_name = name.replace('_', ' ').title()
                editor = TableEditor(name, data)
                self.editors[name] = editor
                self.tabs.addTab(editor, display_name)
            
            QMessageBox.information(self, "Success", f"Loaded {len(self.config_data)} configuration sections")
            
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load config: {str(e)}")

    def save_config(self):
        """Save the configuration back to file"""
        try:
            # Get updated data from all editors
            updated_config = {}
            for name, editor in self.editors.items():
                updated_config[name] = editor.get_data()
            
            # Write back to file
            ConfigFileManager.write_config_file(self.config_file, updated_config, self.original_content)
            
            QMessageBox.information(self, "Success", f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save config: {str(e)}")

    def run_script(self, script_name):
        """Run external Python script"""
        try:
            script_path = os.path.join(os.path.dirname(__file__), script_name)
            if not os.path.exists(script_path):
                QMessageBox.warning(self, "File Not Found", f"Script {script_name} not found")
                return
            
            subprocess.Popen([sys.executable, script_path])
            QMessageBox.information(self, "Script Started", f"Running {script_name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run {script_name}: {str(e)}")

    def open_folder(self, folder_name):
        """Open folder based on configuration"""
        try:
            # Check if Module 00 is available
            if "input_data_modul00" not in self.editors:
                QMessageBox.warning(self, "Error", "Module 00 not available")
                return
                
            module00_data = self.editors["input_data_modul00"].get_data()
            proj_dir = module00_data.get("proj_dir", "")
                
            if not proj_dir:
                QMessageBox.warning(self, "Error", "Project directory not set in Module 00")
                return
                
            # Get the folder path dynamically from Module 00 or fallback to folder_name
            folder_subdir = module00_data.get(folder_name, folder_name)
            folder_path = os.path.join(proj_dir, folder_subdir)
            folder_path = os.path.normpath(folder_path)
                
            # Check if folder exists
            if not os.path.exists(folder_path):
                QMessageBox.warning(self, "Folder Not Found", f"Folder {folder_path} does not exist")
                return
                
            # Open the folder (cross-platform compatible)
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', folder_path])
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open folder {folder_name}: {str(e)}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = ConfigEditorApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
