import sys
import subprocess
import uuid
import minecraft_launcher_lib as mclib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QPushButton, 
                             QLineEdit, QProgressBar, QLabel, QVBoxLayout, QWidget,
                             QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class InstallThread(QThread):
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, version, minecraft_dir):
        super().__init__()
        self.version = version
        self.minecraft_dir = minecraft_dir

    def run(self):
        try:
            max_progress = [0]
            
            def set_status(status):
                self.progress_signal.emit(0, status)
                
            def set_progress(progress):
                self.progress_signal.emit(progress, "")
                
            def set_max(max_val):
                max_progress[0] = max_val
                
            callback = {
                "setStatus": set_status,
                "setProgress": set_progress,
                "setMax": set_max
            }
            
            mclib.install.install_minecraft_version(
                versionid=self.version,
                minecraft_directory=self.minecraft_dir,
                callback=callback
            )
            self.finished_signal.emit(True)
        except Exception as e:
            self.progress_signal.emit(0, f"Error: {str(e)}")
            self.finished_signal.emit(False)

class OpenCraftLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenCraft Launcher")
        self.setGeometry(300, 300, 800, 600)
        
        # Основные переменные
        self.minecraft_dir = mclib.utils.get_minecraft_directory()
        self.install_thread = None
        
        # Создаем виджеты
        self.create_widgets()
        self.load_versions()

    def create_widgets(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("OpenCraft Launcher")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Поле для имени пользователя
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit("Player")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        main_layout.addLayout(username_layout)
        
        # Список версий
        versions_label = QLabel("Available Versions:")
        self.versions_list = QListWidget()
        main_layout.addWidget(versions_label)
        main_layout.addWidget(self.versions_list)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh Versions")
        self.install_btn = QPushButton("Install Version")
        self.launch_btn = QPushButton("Launch Minecraft")
        buttons_layout.addWidget(self.refresh_btn)
        buttons_layout.addWidget(self.install_btn)
        buttons_layout.addWidget(self.launch_btn)
        main_layout.addLayout(buttons_layout)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_label = QLabel("Ready")
        self.progress_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel("Status: Not installed")
        main_layout.addWidget(self.status_label)
        
        # Подключение сигналов
        self.refresh_btn.clicked.connect(self.load_versions)
        self.install_btn.clicked.connect(self.install_version)
        self.launch_btn.clicked.connect(self.launch_minecraft)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Блокировка кнопок при установке
        self.launch_btn.setEnabled(False)

    def load_versions(self):
        self.versions_list.clear()
        self.progress_label.setText("Loading versions...")
        try:
            versions = mclib.utils.get_version_list()
            release_versions = [v for v in versions if v["type"] == "release"]
            snapshot_versions = [v for v in versions if v["type"] == "snapshot"]
            
            self.versions_list.addItem("=== Release Versions ===")
            for version in release_versions[-10:]:  # Последние 10 релизов
                self.versions_list.addItem(version["id"])
            
            self.versions_list.addItem("=== Snapshots ===")
            for version in snapshot_versions[-5:]:  # Последние 5 снапшотов
                self.versions_list.addItem(version["id"])
                
            self.progress_label.setText("Versions loaded successfully")
        except Exception as e:
            self.progress_label.setText(f"Error loading versions: {str(e)}")

    def install_version(self):
        selected_version = self.versions_list.currentItem()
        if not selected_version or selected_version.text().startswith("==="):
            QMessageBox.warning(self, "Error", "Please select a valid version")
            return
            
        version_id = selected_version.text()
        self.status_label.setText(f"Status: Installing {version_id}...")
        
        # Запуск потока установки
        self.install_thread = InstallThread(version_id, self.minecraft_dir)
        self.install_thread.progress_signal.connect(self.update_progress)
        self.install_thread.finished_signal.connect(self.installation_finished)
        self.install_thread.start()
        
        # Блокировка кнопок при установке
        self.install_btn.setEnabled(False)
        self.launch_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)

    def update_progress(self, value, status):
        if status:
            self.progress_label.setText(status)
        if value > 0:
            self.progress_bar.setValue(value)

    def installation_finished(self, success):
        if success:
            self.status_label.setText("Status: Installation completed!")
            self.launch_btn.setEnabled(True)
            QMessageBox.information(self, "Success", "Version installed successfully!")
        else:
            self.status_label.setText("Status: Installation failed")
            QMessageBox.critical(self, "Error", "Installation failed")
        
        # Разблокировка кнопок
        self.install_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.progress_bar.setValue(0)

    def generate_offline_uuid(self, username):
        """Генерирует UUID на основе имени пользователя для офлайн-режима"""
        # Создаем UUID на основе MD5-хэша имени пользователя
        return uuid.uuid3(uuid.NAMESPACE_OID, username).hex

    def launch_minecraft(self):
        selected_version = self.versions_list.currentItem()
        if not selected_version or selected_version.text().startswith("==="):
            QMessageBox.warning(self, "Error", "Please select a valid version")
            return
            
        version_id = selected_version.text()
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username")
            return
            
        try:
            # Используем нашу собственную функцию для генерации UUID
            player_uuid = self.generate_offline_uuid(username)
            
            options = {
                "username": username,
                "uuid": player_uuid,
                "token": ""
            }
            
            # Для версий 1.17 и выше требуется Java 16+
            # Проверим, какая версия Java установлена
            java_path = None
            if mclib.utils.is_version_ge(version_id, "1.17"):
                java_path = mclib.java.find_java(16)
                if not java_path:
                    QMessageBox.warning(self, "Java Error", 
                                        "Для этой версии Minecraft требуется Java 16 или выше.\n"
                                        "Установите Java 16+ и попробуйте снова.")
                    return
            
            command = mclib.command.get_minecraft_command(
                version=version_id,
                minecraft_directory=self.minecraft_dir,
                options=options,
                command=None if not java_path else [java_path]
            )
            
            self.progress_label.setText(f"Launching Minecraft {version_id}...")
            
            # Для Windows используем CREATE_NEW_CONSOLE, для Linux/Mac используем стандартный вызов
            creation_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            
            subprocess.Popen(
                command, 
                shell=True,
                creationflags=creation_flags
            )
            
            self.status_label.setText(f"Status: Minecraft {version_id} launched")
            
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", f"Failed to launch Minecraft:\n{str(e)}")
            self.status_label.setText("Status: Launch failed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpenCraftLauncher()
    window.show()
    sys.exit(app.exec_())