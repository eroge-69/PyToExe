import os
import zipfile
import patoolib
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog, 
                             QMessageBox, QVBoxLayout, QGraphicsBlurEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPalette, QLinearGradient, QBrush, QPainter, QIcon
from PyQt5 import uic

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        palette = QPalette()
        gradient = QLinearGradient(2, 2, 2, self.height())
        gradient.setColorAt(0, QColor("#00e5ff"))
        gradient.setColorAt(1, QColor("#1200ff"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.palette().window())
        super().paintEvent(event)

class ModInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.png'))
        # Проверка существования UI-файла
        if not os.path.exists('mod_installer.ui'):
            QMessageBox.critical(None, "Ошибка", "Файл интерфейса mod_installer.ui не найден!")
            QApplication.quit()
            return
        
        # Загрузка UI
        uic.loadUi('mod_installer.ui', self)
        
        # Пути
        self.mod_archive_path = ""
        self.install_folder_path = ""
        self.exe_path = ""
        
        # Добавляем анимированный фон
        self.background = AnimatedBackground(self)
        self.background.setGeometry(0, 0, self.width(), self.height())
        self.background.lower()  # Помещаем фон под основной контент
        
        # Настройка анимации размытия
        self.setup_animations()
        
        # Подключение сигналов
        self.select_mod_button.clicked.connect(self.select_mod)
        self.select_exe_button.clicked.connect(self.select_exe_file)
        self.select_folder_button.clicked.connect(self.select_install_folder)
        self.install_button.clicked.connect(self.install_mod)
        self.launch_button.clicked.connect(self.launch_program)
        
        # Инициализация состояния кнопок
        self.select_folder_button.setEnabled(False)
        self.select_exe_button.setEnabled(False)
        self.install_button.setEnabled(False)
        self.launch_button.setEnabled(False)
    
    def resizeEvent(self, event):
        """Обновляем размер фона при изменении окна"""
        self.background.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
    
    def setup_animations(self):
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(20)
        self.background.setGraphicsEffect(self.blur_effect)
        
        self.animation = QPropertyAnimation(self.blur_effect, b"blurRadius")
        self.animation.setDuration(2000)
        self.animation.setStartValue(15)
        self.animation.setEndValue(30)
        self.animation.setEasingCurve(QEasingCurve.SineCurve)
        self.animation.setLoopCount(-1)
        self.animation.start()
    
    def select_mod(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл мода",
            "",
            "Архив с модом (*.zip *.rar)"
        )
        
        if file_path:
            self.mod_archive_path = file_path
            self.mod_info_label.setText(f"Выбран мод: {os.path.basename(file_path)}")
            self.mod_info_label.setStyleSheet("color: #90ff00;")
            self.select_folder_button.setEnabled(True)
            self.select_exe_button.setEnabled(True)
            self.install_button.setEnabled(True)
    
    def select_install_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку установки")
        
        if folder_path:
            self.install_folder_path = folder_path
            self.folder_info_label.setText(f"Папка установки: {folder_path}")
            self.folder_info_label.setStyleSheet("color: #90ff00;")
    
    def select_exe_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите .exe файл",
            "",
            "Исполняемые файлы (*.exe)"
        )
        
        if file_path:
            self.exe_path = file_path
            self.exe_info_label.setText(f"Выбран файл: {os.path.basename(file_path)}")
            self.exe_info_label.setStyleSheet("color: #90ff00;")
            self.launch_button.setEnabled(True)
    
    def install_mod(self):
        if not self.mod_archive_path:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите файл мода")
            return
            
        if not self.install_folder_path:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку установки")
            return
            
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.install_button.setEnabled(False)
            QApplication.processEvents()  # Обновляем интерфейс
            
            ext = os.path.splitext(self.mod_archive_path)[1].lower()
            
            if ext == '.zip':
                with zipfile.ZipFile(self.mod_archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.install_folder_path)
            elif ext == '.rar':
                patoolib.extract_archive(self.mod_archive_path, outdir=self.install_folder_path)
            else:
                raise ValueError(f"Неподдерживаемый формат архива: {ext}")
                
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Успешно", "Мод был успешно установлен!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить мод: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.install_button.setEnabled(True)
    
    def launch_program(self):
        if not self.exe_path:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите .exe файл")
            return
            
        try:
            os.startfile(self.exe_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить программу: {str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = ModInstaller()
    window.show()
    app.exec_()
