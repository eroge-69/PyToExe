import os
import json
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QSpacerItem, 
    QSizePolicy, QProgressBar, QPushButton, QApplication, QMainWindow, QDialog, 
    QDialogButtonBox, QFileDialog, QCheckBox, QSpinBox, QGroupBox, QFormLayout
)
from PyQt5.QtGui import QPixmap
from minecraft_launcher_lib.utils import get_minecraft_directory, get_version_list
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command

from random_username.generate import generate_username
from uuid import uuid1
from subprocess import call
from sys import argv, exit
import json

# Путь к директории Minecraft
minecraft_directory = get_minecraft_directory().replace('minecraft', 'super/Minecraft/game')

# Получаем путь к директории для настроек
user_data_dir = os.path.join(os.getenv('APPDATA'), '.super')  # Путь: C:\Users\<имя_пользователя>\AppData\Roaming\.super
if not os.path.exists(user_data_dir):
    os.makedirs(user_data_dir)

settings_file = os.path.join(user_data_dir, 'settings.json')  # Полный путь к файлу настроек

# Стандартные настройки
java_path = "path_to_java_here"
memory_allocated = 2048  # в мегабайтах
java_arguments = "-Xmx2G -Xms2G"  # стандартные аргументы
fullscreen = False
resolution = "1920x1080"
mods = []  # Список модов
resource_packs = []  # Список ресурс паков
datapacks = []  # Список дата паков

# Функции для сохранения и загрузки настроек
def save_settings():
    settings = {
        'minecraft_directory': minecraft_directory,
        'java_path': java_path,
        'memory_allocated': memory_allocated,
        'java_arguments': java_arguments,
        'fullscreen': fullscreen,
        'resolution': resolution,
        'mods': mods,
        'resource_packs': resource_packs,
        'datapacks': datapacks
    }
    with open(settings_file, 'w') as f:
        json.dump(settings, f)

def load_settings():
    global minecraft_directory, java_path, memory_allocated, java_arguments, fullscreen, resolution, mods, resource_packs, datapacks
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            minecraft_directory = settings.get('minecraft_directory', minecraft_directory)
            java_path = settings.get('java_path', java_path)
            memory_allocated = settings.get('memory_allocated', memory_allocated)
            java_arguments = settings.get('java_arguments', java_arguments)
            fullscreen = settings.get('fullscreen', fullscreen)
            resolution = settings.get('resolution', resolution)
            mods = settings.get('mods', mods)
            resource_packs = settings.get('resource_packs', resource_packs)
            datapacks = settings.get('datapacks', datapacks)

# Загрузка настроек при старте
load_settings()

# Функция для получения всех версий Minecraft включая Forge и Fabric
def get_all_versions():
    # Получаем стандартные версии Minecraft
    versions = get_version_list()

    # Добавляем версии Forge и Fabric
    fabric_versions = [
        "fabric-loader-1.18.2",
        "fabric-loader-1.19.2",
        "fabric-loader-1.20.1"
    ]
    for version in fabric_versions:
        versions.append({"id": version, "name": version})

    # Пример для добавления версий Forge
    forge_versions = [
        "1.18.2-forge-40.1.0",
        "1.19.2-forge-41.0.0",
        "1.20.1-forge-43.2.0"
    ]
    for version in forge_versions:
        versions.append({"id": version, "name": version})

    return versions

class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str)
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)

    version_id = ''
    username = ''

    progress = 0
    progress_max = 0
    progress_label = ''

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)

    def launch_setup(self, version_id, username):
        self.version_id = version_id
        self.username = username
    
    def update_progress_label(self, value):
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    
    def update_progress(self, value):
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)
    
    def update_progress_max(self, value):
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def run(self):
        self.state_update_signal.emit(True)

        install_minecraft_version(versionid=self.version_id, minecraft_directory=minecraft_directory, callback={ 'setStatus': self.update_progress_label, 'setProgress': self.update_progress, 'setMax': self.update_progress_max })

        if self.username == '':
            self.username = generate_username()[0]
        
        options = {
            'username': self.username,
            'uuid': str(uuid1()),
            'token': ''
        }

        # Добавление настроек Java
        call(get_minecraft_command(version=self.version_id, minecraft_directory=minecraft_directory, options=options))

        self.state_update_signal.emit(False)

# Окно для настроек
class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 600)

        # Путь к Minecraft
        self.minecraft_path_label = QLabel("Minecraft Directory:", self)
        self.minecraft_path_input = QLineEdit(self)
        self.minecraft_path_input.setText(minecraft_directory)

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_minecraft_directory)

        # Путь к Java
        self.java_path_label = QLabel("Java Path:", self)
        self.java_path_input = QLineEdit(self)
        self.java_path_input.setText(java_path)

        # Аргументы Java
        self.java_args_label = QLabel("Java Arguments:", self)
        self.java_args_input = QLineEdit(self)
        self.java_args_input.setText(java_arguments)

        # Выделение памяти
        self.memory_label = QLabel("Memory Allocation (MB):", self)
        self.memory_input = QSpinBox(self)
        self.memory_input.setRange(1024, 8192)
        self.memory_input.setValue(memory_allocated)

        # Полный экран
        self.fullscreen_checkbox = QCheckBox("Fullscreen", self)
        self.fullscreen_checkbox.setChecked(fullscreen)

        # Разрешение
        self.resolution_label = QLabel("Resolution:", self)
        self.resolution_input = QComboBox(self)
        self.resolution_input.addItems(["1920x1080", "1280x720", "1366x768", "1600x900"])
        self.resolution_input.setCurrentText(resolution)

        # Моды
        self.mods_group = QGroupBox("Mods", self)
        self.mods_layout = QVBoxLayout(self.mods_group)
        self.add_mod_button = QPushButton("Add Mod", self)
        self.add_mod_button.clicked.connect(self.add_mod)
        self.mods_layout.addWidget(self.add_mod_button)
        
        # Ресурс паки
        self.resource_pack_group = QGroupBox("Resource Packs", self)
        self.resource_pack_layout = QVBoxLayout(self.resource_pack_group)
        self.add_resource_pack_button = QPushButton("Add Resource Pack", self)
        self.add_resource_pack_button.clicked.connect(self.add_resource_pack)
        self.resource_pack_layout.addWidget(self.add_resource_pack_button)
        
        # Дата паки
        self.datapack_group = QGroupBox("Datapacks", self)
        self.datapack_layout = QVBoxLayout(self.datapack_group)
        self.add_datapack_button = QPushButton("Add Datapack", self)
        self.add_datapack_button.clicked.connect(self.add_datapack)
        self.datapack_layout.addWidget(self.add_datapack_button)

        # Кнопки OK и Cancel
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.save_and_accept)
        self.button_box.rejected.connect(self.reject)

        # Макет
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.minecraft_path_label)
        self.layout.addWidget(self.minecraft_path_input)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.java_path_label)
        self.layout.addWidget(self.java_path_input)
        self.layout.addWidget(self.java_args_label)
        self.layout.addWidget(self.java_args_input)
        self.layout.addWidget(self.memory_label)
        self.layout.addWidget(self.memory_input)
        self.layout.addWidget(self.fullscreen_checkbox)
        self.layout.addWidget(self.resolution_label)
        self.layout.addWidget(self.resolution_input)
        self.layout.addWidget(self.mods_group)
        self.layout.addWidget(self.resource_pack_group)
        self.layout.addWidget(self.datapack_group)
        self.layout.addWidget(self.button_box)

    def browse_minecraft_directory(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Minecraft Directory", minecraft_directory)
        if folder:
            self.minecraft_path_input.setText(folder)

    def add_mod(self):
        mod_file, _ = QFileDialog.getOpenFileName(self, "Select Mod", "", "JAR Files (*.jar);;All Files (*)")
        if mod_file:
            mods.append(mod_file)
            print(f"Added mod: {mod_file}")
    
    def add_resource_pack(self):
        resource_pack_folder = QFileDialog.getExistingDirectory(self, "Select Resource Pack Folder")
        if resource_pack_folder:
            resource_packs.append(resource_pack_folder)
            print(f"Added resource pack: {resource_pack_folder}")
    
    def add_datapack(self):
        datapack_folder = QFileDialog.getExistingDirectory(self, "Select Datapack Folder")
        if datapack_folder:
            datapacks.append(datapack_folder)
            print(f"Added datapack: {datapack_folder}")

    def save_and_accept(self):
        global minecraft_directory, java_path, memory_allocated, java_arguments, fullscreen, resolution
        minecraft_directory = self.minecraft_path_input.text()
        java_path = self.java_path_input.text()
        java_arguments = self.java_args_input.text()
        memory_allocated = self.memory_input.value()
        fullscreen = self.fullscreen_checkbox.isChecked()
        resolution = self.resolution_input.currentText()
        
        save_settings()
        self.accept()

# Основное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(300, 283)
        self.centralwidget = QWidget(self)

        self.logo = QLabel(self.centralwidget)
        self.logo.setMaximumSize(QSize(256, 37))
        self.logo.setPixmap(QPixmap('assets/title.png'))
        self.logo.setScaledContents(True)
        
        self.titlespacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        
        self.username = QLineEdit(self.centralwidget)
        self.username.setPlaceholderText('Username')
        
        self.version_select = QComboBox(self.centralwidget)

        # Добавляем все версии, включая Forge и Fabric
        for version in get_all_versions():
            self.version_select.addItem(version['id'])
        
        self.progress_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        self.start_progress_label = QLabel(self.centralwidget)
        self.start_progress_label.setText('')
        self.start_progress_label.setVisible(False)

        self.start_progress = QProgressBar(self.centralwidget)
        self.start_progress.setProperty('value', 24)
        self.start_progress.setVisible(False)
        
        self.start_button = QPushButton(self.centralwidget)
        self.start_button.setText('Play')
        self.start_button.clicked.connect(self.launch_game)

        # Кнопка настроек
        self.settings_button = QPushButton(self.centralwidget)
        self.settings_button.setText('Settings')
        self.settings_button.clicked.connect(self.open_settings)

        self.vertical_layout = QVBoxLayout(self.centralwidget)
        self.vertical_layout.setContentsMargins(15, 15, 15, 15)
        self.vertical_layout.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignHCenter)
        self.vertical_layout.addItem(self.titlespacer)
        self.vertical_layout.addWidget(self.username)
        self.vertical_layout.addWidget(self.version_select)
        self.vertical_layout.addItem(self.progress_spacer)
        self.vertical_layout.addWidget(self.start_progress_label)
        self.vertical_layout.addWidget(self.start_progress)
        self.vertical_layout.addWidget(self.start_button)
        self.vertical_layout.addWidget(self.settings_button)

        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)  # Подключение к обновлению прогресса
        
        self.setCentralWidget(self.centralwidget)
    
    def update_progress(self, value, max_value, label):
        """Обновление прогресса"""
        self.start_progress.setMaximum(max_value)
        self.start_progress.setValue(value)
        self.start_progress_label.setText(label)

    def state_update(self, state):
        if state:
            self.start_button.setDisabled(True)
            self.start_progress.setVisible(True)
            self.start_progress_label.setVisible(True)
        else:
            self.start_button.setEnabled(True)
            self.start_progress.setVisible(False)
            self.start_progress_label.setVisible(False)

    def launch_game(self):
        """Запуск игры"""
        version = self.version_select.currentText()
        username = self.username.text() or "player"
        self.launch_thread.launch_setup_signal.emit(version, username)
        self.launch_thread.start()
    
    def open_settings(self):
        """Открытие настроек"""
        settings_window = SettingsWindow()
        settings_window.exec()


if __name__ == '__main__':
    app = QApplication(argv)
    main_window = MainWindow()
    main_window.show()
    exit(app.exec())