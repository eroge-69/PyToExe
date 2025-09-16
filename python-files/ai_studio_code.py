import sys
import os
import subprocess
from pathlib import Path

# --- Imports & Exception Handler ---
# Try to import PyQt5 components, show an error if missing.
try:
    from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QLabel, QLineEdit, QFileDialog,
                                 QListWidget, QListWidgetItem, QGroupBox, QPlainTextEdit,
                                 QMessageBox, QCheckBox, QAbstractItemView)
    from PyQt5.QtCore import Qt, QProcess
    from PyQt5.QtGui import QIcon
except ImportError:
    print("错误：缺少 PyQt5 库。")
    print("请在您的环境中运行 'pip install PyQt5' 进行安装。")
    input("按 Enter 键退出...")
    sys.exit(1)


class PyInstallerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.output_dir = "dist"

        self.setWindowTitle("PyInstaller 图形化打包工具")
        self.setGeometry(300, 300, 800, 650)
        self.set_icon()

        self._init_ui()
        self._connect_signals()
        self.prefill_paths()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Settings Group ---
        settings_group = QGroupBox("1. 打包设置")
        settings_layout = QVBoxLayout(settings_group)

        # Python Script
        script_layout = QHBoxLayout()
        script_layout.addWidget(QLabel("主脚本:"))
        self.script_path_input = QLineEdit()
        self.script_path_input.setPlaceholderText("选择要打包的 .py 文件")
        self.select_script_btn = QPushButton("浏览...")
        script_layout.addWidget(self.script_path_input)
        script_layout.addWidget(self.select_script_btn)
        settings_layout.addLayout(script_layout)

        # UPX Executable
        upx_layout = QHBoxLayout()
        upx_layout.addWidget(QLabel("UPX路径:"))
        self.upx_path_input = QLineEdit()
        self.upx_path_input.setPlaceholderText("选择您的 upx.exe (可选)")
        self.select_upx_btn = QPushButton("浏览...")
        upx_layout.addWidget(self.upx_path_input)
        upx_layout.addWidget(self.select_upx_btn)
        settings_layout.addLayout(upx_layout)
        
        # App Name and Icon
        app_details_layout = QHBoxLayout()
        app_details_layout.addWidget(QLabel("程序名称:"))
        self.app_name_input = QLineEdit("TTS_Local_App")
        app_details_layout.addWidget(self.app_name_input)
        
        app_details_layout.addSpacing(20)
        
        app_details_layout.addWidget(QLabel("程序图标:"))
        self.icon_path_input = QLineEdit()
        self.icon_path_input.setPlaceholderText("选择 .ico 文件 (可选)")
        self.select_icon_btn = QPushButton("浏览...")
        app_details_layout.addWidget(self.icon_path_input)
        app_details_layout.addWidget(self.select_icon_btn)
        settings_layout.addLayout(app_details_layout)
        
        self.no_console_checkbox = QCheckBox("无控制台窗口 (图形界面程序)")
        self.no_console_checkbox.setChecked(True)
        settings_layout.addWidget(self.no_console_checkbox)

        main_layout.addWidget(settings_group)

        # --- Data Group ---
        data_group = QGroupBox("2. 附加数据 (资源文件、模型等)")
        data_layout = QVBoxLayout(data_group)

        self.data_list_widget = QListWidget()
        self.data_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.data_list_widget.setToolTip("这里列出了将包含在打包程序中的额外文件和文件夹。")
        data_layout.addWidget(self.data_list_widget)

        data_btn_layout = QHBoxLayout()
        self.add_folder_btn = QPushButton("添加文件夹")
        self.add_file_btn = QPushButton("添加文件")
        self.remove_item_btn = QPushButton("移除选中项")
        data_btn_layout.addWidget(self.add_folder_btn)
        data_btn_layout.addWidget(self.add_file_btn)
        data_btn_layout.addStretch()
        data_btn_layout.addWidget(self.remove_item_btn)
        data_layout.addLayout(data_btn_layout)
        
        main_layout.addWidget(data_group)
        
        # --- Action & Log Group ---
        log_group = QGroupBox("3. 执行与日志")
        log_layout = QVBoxLayout(log_group)
        
        action_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始打包")
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; height: 30px; font-size: 14px; }")
        self.open_dir_btn = QPushButton("打开输出目录")
        self.open_dir_btn.setEnabled(False)
        action_layout.addWidget(self.start_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.open_dir_btn)
        log_layout.addLayout(action_layout)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("PyInstaller 的输出日志将显示在这里...")
        log_layout.addWidget(self.log_output)
        
        main_layout.addWidget(log_group)

    def _connect_signals(self):
        self.select_script_btn.clicked.connect(self.select_script)
        self.select_upx_btn.clicked.connect(self.select_upx)
        self.select_icon_btn.clicked.connect(self.select_icon)
        self.add_folder_btn.clicked.connect(self.add_data_folder)
        self.add_file_btn.clicked.connect(self.add_data_file)
        self.remove_item_btn.clicked.connect(self.remove_selected_data)
        self.start_btn.clicked.connect(self.start_packaging)
        self.open_dir_btn.clicked.connect(self.open_output_directory)

    def set_icon(self):
        # A simple embedded icon for the tool itself
        icon_path = 'assets/icon.ico'
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def prefill_paths(self):
        """Automatically find and fill common paths for the TTS Local script."""
        base_path = Path(".")
        
        # Prefill script path
        script_file = base_path / "TTS_Local.py"
        if script_file.exists():
            self.script_path_input.setText(str(script_file.resolve()))

        # Prefill icon path
        icon_file = base_path / "assets" / "icon.ico"
        if icon_file.exists():
            self.icon_path_input.setText(str(icon_file.resolve()))

        # Prefill common data directories
        common_dirs = ["assets", "modules", "themes", "tts_models_cache"]
        for d in common_dirs:
            dir_path = base_path / d
            if dir_path.is_dir():
                self.add_data_item(str(dir_path.resolve()), is_folder=True)

    def select_script(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择 Python 脚本", "", "Python 文件 (*.py)")
        if filepath:
            self.script_path_input.setText(filepath)

    def select_upx(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择 UPX 程序", "", "可执行文件 (*.exe)")
        if filepath:
            self.upx_path_input.setText(filepath)

    def select_icon(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择图标文件", "", "图标 (*.ico)")
        if filepath:
            self.icon_path_input.setText(filepath)
            
    def add_data_folder(self):
        dirpath = QFileDialog.getExistingDirectory(self, "选择要添加的文件夹")
        if dirpath:
            self.add_data_item(dirpath, is_folder=True)

    def add_data_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "选择要添加的文件", "", "所有文件 (*.*)")
        if filepath:
            self.add_data_item(filepath, is_folder=False)
            
    def add_data_item(self, path, is_folder):
        prefix = "[文件夹] " if is_folder else "[文件] "
        item = QListWidgetItem(prefix + path)
        item.setData(Qt.UserRole, {"path": path, "is_folder": is_folder})
        self.data_list_widget.addItem(item)
        
    def remove_selected_data(self):
        for item in self.data_list_widget.selectedItems():
            self.data_list_widget.takeItem(self.data_list_widget.row(item))

    def start_packaging(self):
        script_path = self.script_path_input.text()
        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(self, "错误", "请选择一个有效的主脚本文件。")
            return
            
        upx_path = self.upx_path_input.text()
        if upx_path and not os.path.exists(upx_path):
            QMessageBox.warning(self, "错误", "指定的 UPX 路径无效。")
            return

        self.set_ui_busy(True)
        self.log_output.clear()
        
        # 'pyinstaller' 将作为命令列表的第一个元素
        command = [
            'pyinstaller', 
            script_path,
            '--name', self.app_name_input.text() or "packaged_app",
            '--noconfirm', # Overwrite output directory without asking
        ]
        
        # Packaging mode (always one-dir as requested)
        command.append('--onedir')

        if self.no_console_checkbox.isChecked():
            command.append('--windowed')
        
        if self.icon_path_input.text():
            command.extend(['--icon', self.icon_path_input.text()])
            
        if upx_path:
            # --upx-dir 需要的是 upx.exe 所在的目录
            command.extend(['--upx-dir', os.path.dirname(upx_path)])
            
        for i in range(self.data_list_widget.count()):
            item_data = self.data_list_widget.item(i).data(Qt.UserRole)
            src_path = item_data['path']
            dest_name = os.path.basename(src_path)
            # PyInstaller uses ';' on Windows and ':' on other OSes as a separator
            data_arg = f"{src_path}{os.pathsep}{dest_name}"
            command.extend(['--add-data', data_arg])

        self.log_message("--- 开始打包 ---")
        # 将命令列表转换为一个字符串，以便在日志中清晰地显示
        log_command_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in command)
        self.log_message(f"命令: {log_command_str}\n")


        # 使用 QProcess 进行非阻塞执行
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.finished.connect(self.on_process_finished)
        
        # ------------------- 这是关键的修复点 -------------------
        # 第一个参数是程序，第二个参数是程序的参数列表
        self.process.start(command[0], command[1:])
        # --------------------------------------------------------

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self.log_message(data, newline=False)
        
    def on_process_finished(self, exit_code, exit_status):
        self.log_message("\n--- 打包结束 ---")
        if exit_code == 0:
            self.log_message("打包成功完成！")
            QMessageBox.information(self, "成功", "应用程序打包成功！")
            self.output_dir = os.path.join('dist', self.app_name_input.text())
            self.open_dir_btn.setEnabled(True)
        else:
            self.log_message(f"打包失败！退出代码: {exit_code}")
            QMessageBox.critical(self, "失败", f"打包过程中发生错误！\n请查看日志获取详细信息。")
        self.set_ui_busy(False)
        self.process = None

    def log_message(self, message, newline=True):
        if newline:
            self.log_output.appendPlainText(message)
        else:
            self.log_output.insertPlainText(message)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def set_ui_busy(self, busy):
        self.start_btn.setEnabled(not busy)
        self.start_btn.setText("正在打包..." if busy else "开始打包")
        # Disable all settings widgets while busy
        for widget in self.findChildren(QWidget):
            if isinstance(widget, (QPushButton, QLineEdit, QListWidget, QCheckBox)) and widget != self.start_btn:
                widget.setEnabled(not busy)
                
    def open_output_directory(self):
        path = os.path.realpath(self.output_dir)
        if os.path.exists(path):
            try:
                if sys.platform == 'win32':
                    os.startfile(path)
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', path])
                else:
                    subprocess.Popen(['xdg-open', path])
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开文件夹: {e}")
        else:
            QMessageBox.warning(self, "错误", f"输出目录 '{path}' 不存在。")
            
    def closeEvent(self, event):
        if self.process and self.process.state() == QProcess.Running:
            reply = QMessageBox.question(self, '退出确认',
                                       "打包仍在进行中。确定要强制退出吗？",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.process.kill()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("错误：未找到 PyInstaller。")
        print("请在您的环境中运行 'pip install pyinstaller' 进行安装。")
        input("按 Enter 键退出...")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = PyInstallerGUI()
    window.show()
    sys.exit(app.exec_())