import os
import sys
import json
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QCheckBox, QPushButton, 
                             QLabel, QTabWidget, QProgressBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
import win32api
import win32con
import win32ui

class ProgramInstaller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Установщик программ")
        self.setMinimumSize(800, 600)
        
        # Создаем папки если их нет
        self.soft_dir = os.path.join(os.path.dirname(__file__), "soft")
        self.icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        os.makedirs(self.soft_dir, exist_ok=True)
        os.makedirs(self.icons_dir, exist_ok=True)
        
        # Загружаем историю установки
        self.history_file = os.path.join(os.path.dirname(__file__), "history.json")
        self.installed_programs = self.load_history()
        
        self.init_ui()
        self.load_programs()
        
    def init_ui(self):
        # Основные вкладки
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Вкладка установки
        self.install_tab = QWidget()
        self.install_layout = QVBoxLayout()
        
        # Выбрать все
        self.select_all = QCheckBox("Выбрать все программы")
        self.select_all.stateChanged.connect(self.toggle_select_all)
        self.install_layout.addWidget(self.select_all)
        
        # Список программ
        self.programs_list = QListWidget()
        self.programs_list.setIconSize(QSize(32, 32))
        self.install_layout.addWidget(self.programs_list)
        
        # Прогресс бар
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.install_layout.addWidget(self.progress)
        
        # Кнопки
        self.button_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить список")
        self.refresh_btn.clicked.connect(self.load_programs)
        self.install_btn = QPushButton("Установить выбранные")
        self.install_btn.clicked.connect(self.install_selected)
        self.button_layout.addWidget(self.refresh_btn)
        self.button_layout.addWidget(self.install_btn)
        self.install_layout.addLayout(self.button_layout)
        
        self.install_tab.setLayout(self.install_layout)
        self.tabs.addTab(self.install_tab, "Установка программ")
        
        # Вкладка истории
        self.history_tab = QWidget()
        self.history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.history_layout.addWidget(self.history_list)
        self.history_tab.setLayout(self.history_layout)
        self.tabs.addTab(self.history_tab, "История установки")
    
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.installed_programs, f, ensure_ascii=False, indent=2)
    
    def extract_icon(self, exe_path):
        try:
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            
            large, small = win32api.ExtractIconEx(exe_path, 0)
            win32api.DestroyIcon(small[0])
            
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject(hbmp)
            hdc.DrawIcon((0,0), large[0])
            
            bmp_str = hbmp.GetBitmapBits(True)
            img = QImage(bmp_str, ico_x, ico_y, QImage.Format_ARGB32)
            pixmap = QPixmap.fromImage(img)
            
            win32api.DestroyIcon(large[0])
            return QIcon(pixmap)
        except:
            return QIcon(":/icons/default.ico")
    
    def load_programs(self):
        self.programs_list.clear()
        self.programs = []
        
        if not os.path.exists(self.soft_dir):
            item = QListWidgetItem("Папка 'soft' не найдена")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.programs_list.addItem(item)
            return
        
        for file in os.listdir(self.soft_dir):
            if file.lower().endswith(('.exe', '.msi')):
                file_path = os.path.join(self.soft_dir, file)
                program_name = os.path.splitext(file)[0]
                is_installed = any(p['name'] == program_name and p['installed'] 
                                 for p in self.installed_programs)
                
                # Создаем элемент списка
                item = QListWidgetItem(program_name)
                item.setData(Qt.UserRole, file_path)
                
                # Иконка
                if file.lower().endswith('.exe'):
                    icon = self.extract_icon(file_path)
                else:
                    icon = QIcon(":/icons/msi.ico")
                item.setIcon(icon)
                
                # Чекбокс для не установленных программ
                if not is_installed:
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                    item.setToolTip("Уже установлено")
                
                self.programs_list.addItem(item)
                self.programs.append({
                    'name': program_name,
                    'path': file_path,
                    'installed': is_installed
                })
        
        if self.programs_list.count() == 0:
            item = QListWidgetItem("В папке 'soft' нет программ для установки")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.programs_list.addItem(item)
    
    def toggle_select_all(self, state):
        for i in range(self.programs_list.count()):
            item = self.programs_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Checked if state else Qt.Unchecked)
    
    def install_selected(self):
        selected = []
        for i in range(self.programs_list.count()):
            item = self.programs_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append({
                    'path': item.data(Qt.UserRole),
                    'name': item.text()
                })
        
        if not selected:
            self.statusBar().showMessage("Не выбрано ни одной программы", 3000)
            return
        
        self.progress.setMaximum(len(selected))
        self.progress.setValue(0)
        self.progress.setVisible(True)
        self.install_btn.setEnabled(False)
        
        for i, program in enumerate(selected, 1):
            self.statusBar().showMessage(f"Устанавливается {program['name']} ({i}/{len(selected)})...")
            
            try:
                if program['path'].lower().endswith('.msi'):
                    cmd = ['msiexec', '/i', program['path'], '/qn']
                else:
                    cmd = [program['path'], '/S', '/silent', '/verysilent', '/qn', '/norestart']
                
                subprocess.run(cmd, check=True)
                
                # Добавляем в историю
                self.installed_programs.append({
                    'name': program['name'],
                    'path': program['path'],
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'installed': True
                })
                
                self.progress.setValue(i)
                QApplication.processEvents()  # Обновляем интерфейс
                
            except subprocess.CalledProcessError as e:
                self.statusBar().showMessage(f"Ошибка установки {program['name']}: {e}", 5000)
        
        self.save_history()
        self.statusBar().showMessage("Установка завершена", 3000)
        self.progress.setVisible(False)
        self.install_btn.setEnabled(True)
        self.load_programs()  # Обновляем список
    
    def load_history(self):
        self.history_list.clear()
        for program in sorted(self.installed_programs, 
                            key=lambda x: x.get('date', ''), 
                            reverse=True):
            if program.get('installed', False):
                item = QListWidgetItem(f"{program['name']} - {program.get('date', '')}")
                self.history_list.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    installer = ProgramInstaller()
    installer.show()
    sys.exit(app.exec_())