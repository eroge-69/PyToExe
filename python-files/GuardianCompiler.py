import sys
import os
import random
import string
import re
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QFileDialog, QGroupBox, QCheckBox,
                            QSpinBox, QProgressBar, QTabWidget, QMessageBox,
                            QSplitter, QFrame, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
import datetime

class MTALuaObfuscator:
    def __init__(self):
        self.variable_map = {}
        self.function_map = {}
        self.string_counter = 0
        self.used_names = set()
        
    def generate_random_name(self, length=None):
        if length is None:
            length = random.randint(8, 15)
        
        first_char = random.choice(string.ascii_letters + '_')
        rest_chars = ''.join(random.choices(
            string.ascii_letters + string.digits + '_', 
            k=length-1
        ))
        
        name = first_char + rest_chars
        
        while name in self.used_names or self.is_lua_keyword(name):
            name = self.generate_random_name(length)
        
        self.used_names.add(name)
        return name
    
    def is_lua_keyword(self, name):
        lua_keywords = {
            'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for',
            'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat',
            'return', 'then', 'true', 'until', 'while'
        }
        return name.lower() in lua_keywords
    
    def encode_string(self, text):
        encoded = []
        shift = random.randint(1, 50)
        
        for char in text:
            encoded.append(ord(char) + shift)
        
        return encoded, shift
    
    def create_string_decoder(self):
        decoder_name = self.generate_random_name()
        Fun_name = self.generate_random_name()
        helper_var = self.generate_random_name()
        
        decoder_code = f"""
local function {decoder_name}({helper_var}, shift)
    local result = ""
    for i = 1, #{helper_var} do
        result = result .. string.char({helper_var}[i] - shift)
    end
    return result
end
"""
        return decoder_code.strip(), decoder_name
    
    def obfuscate_strings(self, code, decoder_name):
        def replace_string(match):
            string_content = match.group(1)
            encoded_data, shift = self.encode_string(string_content)
            encoded_str = '{' + ', '.join(map(str, encoded_data)) + '}'
            return f'{decoder_name}({encoded_str}, {shift})'
        
        code = re.sub(r'"([^"]*)"', replace_string, code)
        code = re.sub(r"'([^']*)'", replace_string, code)
        
        return code
    
    def add_dummy_code(self, complexity=5):
        dummy_lines = []
        
        for _ in range(random.randint(complexity, complexity*2)):
            var_name = self.generate_random_name()
            var_value = random.randint(1000, 9999)
            dummy_lines.append(f"local {var_name} = {var_value}")
        
        for _ in range(random.randint(2, complexity)):
            func_name = self.generate_random_name()
            param_name = self.generate_random_name()
            dummy_lines.append(f"""
local function {func_name}({param_name})
    local {self.generate_random_name()} = {param_name} * {random.randint(2, 10)}
    return {random.randint(100, 999)}
end""")
        
        return '\n'.join(dummy_lines)
    
    def create_control_flow_obfuscation(self, code, loops=3):
        main_func = self.generate_random_name()
        exec_var = self.generate_random_name()
        flag_var = self.generate_random_name()
        
        obfuscated = f"""
local {flag_var} = false
local function {main_func}()
    if {flag_var} then return end
    {flag_var} = true
{self.indent_code(code, 1)}
end

local {exec_var} = {main_func}
"""
        
        for i in range(loops):
            loop_var = self.generate_random_name()
            start_val = random.randint(1, 5)
            end_val = start_val + random.randint(1, 3)
            
            if i == 0:
                obfuscated += f"""
for {loop_var} = {start_val}, {end_val} do
    if {loop_var} == {start_val} then
        {exec_var}()
    end
end
"""
            else:
                dummy_var = self.generate_random_name()
                obfuscated += f"""
for {loop_var} = {start_val}, {end_val} do
    local {dummy_var} = {loop_var} * {random.randint(2, 10)}
end
"""
        
        return obfuscated
    
    def indent_code(self, code, level):
        indent = "    " * level
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
    
    def add_junk_comments(self):
        comments = [
            'YoAreLoser = "@ !Guardian"'
        ]
        return '\n'.join(comments) + '\n\n'
    
    def obfuscate_variable_names(self, code):
        local_vars = re.findall(r'local\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
        
        for var in local_vars:
            if var not in self.variable_map:
                self.variable_map[var] = self.generate_random_name()
        
        for original, obfuscated in self.variable_map.items():
            pattern = r'\b' + re.escape(original) + r'\b'
            code = re.sub(pattern, obfuscated, code)
        
        return code
    
    def obfuscate(self, lua_code, options=None):
        if options is None:
            options = {
                'string_encoding': True,
                'variable_renaming': True,
                'dummy_code': True,
                'control_flow': True,
                'junk_comments': True,
                'complexity': 5
            }

        code = re.sub(r'--.*$', '', lua_code, flags=re.MULTILINE)
        code = re.sub(r'\n\s*\n', '\n', code).strip()
        
        obfuscated_code = ""
        
        if options.get('junk_comments', True):
            obfuscated_code += self.add_junk_comments()
        
        if options.get('dummy_code', True):
            obfuscated_code += self.add_dummy_code(options.get('complexity', 5)) + '\n\n'
        
        if options.get('string_encoding', True):
            decoder_code, decoder_name = self.create_string_decoder()
            obfuscated_code += decoder_code + '\n\n'
            code = self.obfuscate_strings(code, decoder_name)
        
        if options.get('variable_renaming', True):
            code = self.obfuscate_variable_names(code)
        
        if options.get('control_flow', True):
            code = self.create_control_flow_obfuscation(code, options.get('complexity', 3))
        
        obfuscated_code += code
        
        return obfuscated_code

class CompilationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bytes)
    error = pyqtSignal(str)
    
    def __init__(self, file_path, obfuscate_level, compile_flag, debug_flag, obfuscate_options=None):
        super().__init__()
        self.file_path = file_path
        self.obfuscate_level = obfuscate_level
        self.compile_flag = compile_flag
        self.debug_flag = debug_flag
        self.obfuscate_options = obfuscate_options or {}
    
    def run(self):
        try:
            self.progress.emit(10)
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            self.progress.emit(20)

            if self.obfuscate_options.get('dummy_code', False) or self.obfuscate_options.get('variable_renaming', False):
                obfuscator = MTALuaObfuscator()

                online_options = {
                    'string_encoding': False,
                    'variable_renaming': self.obfuscate_options.get('variable_renaming', False),
                    'dummy_code': self.obfuscate_options.get('dummy_code', False),
                    'control_flow': False,  
                    'junk_comments': self.obfuscate_options.get('junk_comments', False),
                    'complexity': self.obfuscate_options.get('complexity', 3)
                }
                
                file_content = obfuscator.obfuscate(file_content, online_options)
            
            self.progress.emit(30)
            
            url_raw = 'luac.mtasa.com'
            url = f'https://{url_raw}'
            url_file = f'{url}/index.php'
            
            newLine = '\r\n'
            boundary = '------WebKitFormBoundary'
            boundaryLine = f'{boundary}{newLine}'
            
            headers = {
                'Host': url_raw,
                'Origin': url,
                'Referer': url_file,
                'Content-Type': f'multipart/form-data; boundary={boundary[2:]}',
            }
            
            payload = [
                [
                    f'Content-Disposition: form-data; name="luasource"; filename="{os.path.basename(self.file_path)}"'.encode('utf-8'),
                    b'Content-Type: application/octet-stream',
                    f'{newLine}{file_content}'.encode('utf-8')
                ],
                [
                    b'Content-Disposition: form-data; name="compile"',
                    f'{newLine}{1 if self.compile_flag else 0}'.encode('utf-8')
                ],
                [
                    b'Content-Disposition: form-data; name="obfuscate"',
                    f'{newLine}{self.obfuscate_level}'.encode('utf-8')
                ],
                [
                    b'Content-Disposition: form-data; name="debug"',
                    f'{newLine}{1 if self.debug_flag else 0}'.encode('utf-8')
                ],
                [
                    b'Content-Disposition: form-data; name="Submit"',
                    f'{newLine}Submit'.encode('utf-8')
                ]
            ]
            
            data = boundaryLine
            for c in payload:
                for cc in c:
                    data += cc.decode('utf-8') + '\r\n'
                data += boundaryLine
            
            self.progress.emit(60)
            
            response = requests.post(url_file, headers=headers, data=data)
            
            self.progress.emit(90)
            
            if response.content == b'ERROR Could not compile file':
                self.error.emit("Could not compile file!")
                return
            
            self.finished.emit(response.content)
            
        except Exception as e:
            self.error.emit(f"Error occurred: {str(e)}")

class ObfuscationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, input_file, output_file, options):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.options = options
    
    def run(self):
        try:
            self.progress.emit(10)
            
            with open(self.input_file, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            self.progress.emit(30)
            
            obfuscator = MTALuaObfuscator()
            obfuscated_code = obfuscator.obfuscate(original_code, self.options)
            
            self.progress.emit(80)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated_code)
            
            self.progress.emit(100)
            self.finished.emit("Obfuscation completed successfully!")
            
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

class MTAObfuscatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_theme()
        
    def init_ui(self):
        self.setWindowTitle("🔐 MTA Lua Obfuscator & Compiler")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.create_header(main_layout)
        
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        file_tab = self.create_file_tab()
        tab_widget.addTab(file_tab, "📁 File Processing")
        
        editor_tab = self.create_editor_tab()
        tab_widget.addTab(editor_tab, "📝 Code Editor")
        
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "⚙️ Settings")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.statusBar().showMessage("Ready to use")
    
    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Box)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2E3440, stop:1 #3B4252);
                border: 2px solid #4C566A;
                border-radius: 10px;
                margin: 5px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Guardian Ultimate - Compiler")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #88C0D0; margin: 10px;")
        
        subtitle_label = QLabel("Guardian Compiler")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #D8DEE9; margin-bottom: 10px;")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
    
    def create_file_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        mode_group = QGroupBox("Processing Mode")
        mode_layout = QHBoxLayout(mode_group)
        
        self.mode_group = QButtonGroup()
        self.local_mode = QRadioButton("Local Compile")
        self.compile_mode = QRadioButton("Online Compilation")
        self.local_mode.setChecked(True)
        
        self.mode_group.addButton(self.local_mode, 1)
        self.mode_group.addButton(self.compile_mode, 2)
        
        mode_layout.addWidget(self.local_mode)
        mode_layout.addWidget(self.compile_mode)
        layout.addWidget(mode_group)

        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Input File:"))
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("Select .lua file path")
        input_layout.addWidget(self.input_file_edit)
        
        browse_input_btn = QPushButton("📁 Browse")
        browse_input_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(browse_input_btn)
        
        file_layout.addLayout(input_layout)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output File:"))
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("Select output file path")
        output_layout.addWidget(self.output_file_edit)
        
        browse_output_btn = QPushButton("📁 Browse")
        browse_output_btn.clicked.connect(self.browse_output_file)
        output_layout.addWidget(browse_output_btn)
        
        file_layout.addLayout(output_layout)

        self.compile_options_group = QGroupBox("Compilation Options")
        compile_options_layout = QVBoxLayout(self.compile_options_group)
        
        obfuscate_layout = QHBoxLayout()
        obfuscate_layout.addWidget(QLabel("Obfuscation Level:"))
        self.obfuscate_spin = QSpinBox()
        self.obfuscate_spin.setRange(0, 3)
        self.obfuscate_spin.setValue(3)
        obfuscate_layout.addWidget(self.obfuscate_spin)
        obfuscate_layout.addStretch()
        
        self.compile_cb = QCheckBox("Compile to bytecode")
        self.compile_cb.setChecked(True)
        
        self.debug_cb = QCheckBox("Enable debug info")
        self.debug_cb.setChecked(False)

        self.online_dummy_code_cb = QCheckBox("Add Dummy Code (Pre-processing)")
        self.online_dummy_code_cb.setChecked(True)
        
        self.online_variable_renaming_cb = QCheckBox("Variable Renaming (Pre-processing)")
        self.online_variable_renaming_cb.setChecked(True)
        
        self.online_junk_comments_cb = QCheckBox("Add Junk Comments (Pre-processing)")
        self.online_junk_comments_cb.setChecked(True)
        
        complexity_layout = QHBoxLayout()
        complexity_layout.addWidget(QLabel("Pre-processing Complexity:"))
        self.online_complexity_spin = QSpinBox()
        self.online_complexity_spin.setRange(1, 10)
        self.online_complexity_spin.setValue(3)
        complexity_layout.addWidget(self.online_complexity_spin)
        complexity_layout.addStretch()
        
        compile_options_layout.addLayout(obfuscate_layout)
        compile_options_layout.addWidget(self.compile_cb)
        compile_options_layout.addWidget(self.debug_cb)
        compile_options_layout.addWidget(QLabel("Additional Pre-processing Options:"))
        compile_options_layout.addWidget(self.online_dummy_code_cb)
        compile_options_layout.addWidget(self.online_variable_renaming_cb)
        compile_options_layout.addWidget(self.online_junk_comments_cb)
        compile_options_layout.addLayout(complexity_layout)
        
        self.compile_options_group.setVisible(False)
        file_layout.addWidget(self.compile_options_group)
        
        layout.addWidget(file_group)

        process_btn = QPushButton("🚀 Start Processing")
        process_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #A3BE8C, stop:1 #81A1C1);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #B48EAD, stop:1 #5E81AC);
            }
        """)
        process_btn.clicked.connect(self.process_file)
        layout.addWidget(process_btn)

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #D8DEE9;
                border: 1px solid #4C566A;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        layout.addStretch()

        self.mode_group.buttonClicked.connect(self.toggle_mode)
        
        return widget
    
    def create_editor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        input_group = QGroupBox("Original Code")
        input_layout = QVBoxLayout(input_group)
        
        self.input_editor = QTextEdit()
        self.input_editor.setPlaceholderText("Enter your Lua code here...")
        self.input_editor.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #D8DEE9;
                border: 1px solid #4C566A;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        input_layout.addWidget(self.input_editor)
        
        editor_buttons = QHBoxLayout()
        
        load_btn = QPushButton("📂 Load File")
        load_btn.clicked.connect(self.load_code_to_editor)
        editor_buttons.addWidget(load_btn)
        
        obfuscate_btn = QPushButton("🔒 Obfuscate")
        obfuscate_btn.clicked.connect(self.obfuscate_editor_code)
        editor_buttons.addWidget(obfuscate_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_editor_code)
        editor_buttons.addWidget(save_btn)
        
        input_layout.addLayout(editor_buttons)
        splitter.addWidget(input_group)
        
        output_group = QGroupBox("Obfuscated Code")
        output_layout = QVBoxLayout(output_group)
        
        self.output_editor = QTextEdit()
        self.output_editor.setReadOnly(True)
        self.output_editor.setStyleSheet("""
            QTextEdit {
                background-color: #3B4252;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                border-radius: 5px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        output_layout.addWidget(self.output_editor)
        
        splitter.addWidget(output_group)
        layout.addWidget(splitter)
        
        return widget
    
    def create_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        options_group = QGroupBox("Local Obfuscation Options")
        options_layout = QVBoxLayout(options_group)
        
        self.string_encoding_cb = QCheckBox("String Encoding")
        self.string_encoding_cb.setChecked(True)
        options_layout.addWidget(self.string_encoding_cb)
        
        self.variable_renaming_cb = QCheckBox("Variable Renaming")
        self.variable_renaming_cb.setChecked(True)
        options_layout.addWidget(self.variable_renaming_cb)
        
        self.dummy_code_cb = QCheckBox("Add Dummy Code")
        self.dummy_code_cb.setChecked(True)
        options_layout.addWidget(self.dummy_code_cb)
        
        self.control_flow_cb = QCheckBox("Control Flow Obfuscation")
        self.control_flow_cb.setChecked(True)
        options_layout.addWidget(self.control_flow_cb)
        
        self.junk_comments_cb = QCheckBox("Junk Comments")
        self.junk_comments_cb.setChecked(True)
        options_layout.addWidget(self.junk_comments_cb)
        
        complexity_layout = QHBoxLayout()
        complexity_layout.addWidget(QLabel("Complexity Level:"))
        self.complexity_spin = QSpinBox()
        self.complexity_spin.setRange(1, 10)
        self.complexity_spin.setValue(5)
        complexity_layout.addWidget(self.complexity_spin)
        complexity_layout.addStretch()
        
        options_layout.addLayout(complexity_layout)
        layout.addWidget(options_group)
        
        reset_btn = QPushButton("🔄 Reset Settings")
        reset_btn.clicked.connect(self.reset_settings)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        return widget
    
    def setup_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #3B4252;
            }
            QWidget {
                background-color: #3B4252;
                color: #D8DEE9;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4C566A;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4C566A;
                border: 1px solid #5E81AC;
                border-radius: 5px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5E81AC;
            }
            QPushButton:pressed {
                background-color: #434C5E;
            }
            QLineEdit {
                background-color: #2E3440;
                border-radius: 3px;
                padding: 5px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #4C566A;
                background-color: #2E3440;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #A3BE8C;
                background-color: #A3BE8C;
                border-radius: 3px;
            }
            QTabWidget::pane {
                border: 1px solid #4C566A;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #434C5E;
                border: 1px solid #4C566A;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #5E81AC;
            }
            QProgressBar {
                border: 1px solid #4C566A;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #A3BE8C;
                border-radius: 3px;
            }
            QRadioButton {
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #4C566A;
            }
            QRadioButton::indicator:checked {
                background-color: #A3BE8C;
                border: 2px solid #A3BE8C;
            }
        """)
    
    def toggle_mode(self, button):
        if button.text() == "Online Compilation":
            self.compile_options_group.setVisible(True)
        else:
            self.compile_options_group.setVisible(False)
    
    def browse_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Input File", "", "Lua Files (*.lua);;All Files (*)"
        )
        if file_path:
            self.input_file_edit.setText(file_path)
            base_name = os.path.splitext(file_path)[0]
            output_path = f"{base_name}_Compiled.luac"
            self.output_file_edit.setText(output_path)
    
    def browse_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Output File", "", "Lua Files (*.lua);;All Files (*)"
        )
        if file_path:
            self.output_file_edit.setText(file_path)
    
    def get_options(self):
        return {
            'string_encoding': self.string_encoding_cb.isChecked(),
            'variable_renaming': self.variable_renaming_cb.isChecked(),
            'dummy_code': self.dummy_code_cb.isChecked(),
            'control_flow': self.control_flow_cb.isChecked(),
            'junk_comments': self.junk_comments_cb.isChecked(),
            'complexity': self.complexity_spin.value()
        }
    
    def process_file(self):
        input_file = self.input_file_edit.text()
        output_file = self.output_file_edit.text()
        
        if not input_file or not output_file:
            QMessageBox.warning(self, "Error", "Please select input and output files.")
            return
        
        if not os.path.exists(input_file):
            QMessageBox.warning(self, "Error", "Input file does not exist.")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        if self.local_mode.isChecked():
            self.thread = ObfuscationThread(input_file, output_file, self.get_options())
            self.thread.progress.connect(self.progress_bar.setValue)
            self.thread.finished.connect(self.on_process_finished)
            self.thread.error.connect(self.on_process_error)
            self.thread.start()
            
            self.log_text.append(f"🚀 Starting local obfuscation: {input_file}")
        else:
            obfuscate_level = self.obfuscate_spin.value()
            compile_flag = self.compile_cb.isChecked()
            debug_flag = self.debug_cb.isChecked()
            
            self.compile_thread = CompilationThread(
                input_file, 
                obfuscate_level, 
                compile_flag, 
                debug_flag
            )
            self.compile_thread.progress.connect(self.progress_bar.setValue)
            self.compile_thread.finished.connect(self.on_compile_finished)
            self.compile_thread.error.connect(self.on_process_error)
            self.compile_thread.start()
            
            self.log_text.append(f"🚀 Starting online compilation: {input_file}")
    
    def on_compile_finished(self, compiled_data):
        output_file = self.output_file_edit.text()
        
        try:
            with open(output_file, 'wb') as f:
                f.write(compiled_data)
            
            self.progress_bar.setVisible(False)
            self.log_text.append(f"✅ Compilation completed successfully!")
            self.statusBar().showMessage("Compilation completed")
            QMessageBox.information(self, "Success", "File compiled successfully!")
        except Exception as e:
            self.on_process_error(f"Error saving compiled file: {str(e)}")
    
    def on_process_finished(self, message):
        self.progress_bar.setVisible(False)
        self.log_text.append(f"✅ {message}")
        self.statusBar().showMessage("Operation completed successfully")
        QMessageBox.information(self, "Success", message)
    
    def on_process_error(self, error_message):
        self.progress_bar.setVisible(False)
        self.log_text.append(f"❌ {error_message}")
        self.statusBar().showMessage("Error in operation")
        QMessageBox.critical(self, "Error", error_message)
    
    def load_code_to_editor(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Code", "", "Lua Files (*.lua);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                self.input_editor.setPlainText(code)
                self.log_text.append(f"📂 Code loaded from file: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading file: {str(e)}")
    
    def obfuscate_editor_code(self):
        code = self.input_editor.toPlainText()
        if not code.strip():
            QMessageBox.warning(self, "Error", "Please enter code to obfuscate.")
            return
        
        try:
            obfuscator = MTALuaObfuscator()
            obfuscated_code = obfuscator.obfuscate(code, self.get_options())
            self.output_editor.setPlainText(obfuscated_code)
            self.log_text.append("🔒 Code obfuscated successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Obfuscation error: {str(e)}")
    
    def save_editor_code(self):
        code = self.output_editor.toPlainText()
        if not code.strip():
            QMessageBox.warning(self, "Error", "No obfuscated code to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Obfuscated Code", "", "Lua Files (*.lua);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                self.log_text.append(f"💾 Code saved: {file_path}")
                QMessageBox.information(self, "Success", "Code saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {str(e)}")
    
    def reset_settings(self):
        self.string_encoding_cb.setChecked(True)
        self.variable_renaming_cb.setChecked(True)
        self.dummy_code_cb.setChecked(True)
        self.control_flow_cb.setChecked(True)
        self.junk_comments_cb.setChecked(True)
        self.complexity_spin.setValue(5)
        self.log_text.append("🔄 Settings reset to defaults")

def main():
    app = QApplication(sys.argv)
    
    font = QFont("Tahoma", 9)
    app.setFont(font)

    window = MTAObfuscatorGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()