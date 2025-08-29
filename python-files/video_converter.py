import os
import sys
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QGroupBox, QCheckBox, QComboBox,
                             QFileDialog, QProgressBar, QMessageBox, QGridLayout,
                             QSpinBox, QDoubleSpinBox, QSlider, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

class ConversionWorker(QThread):
    progress_signal = pyqtSignal(str)
    file_progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal(int, int)
    error_signal = pyqtSignal(str)

    def __init__(self, source_dir, target_dir, input_formats, output_format, 
                 max_workers, encoding_params):
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.input_formats = input_formats
        self.output_format = output_format
        self.max_workers = max_workers
        self.encoding_params = encoding_params
        self.is_paused = False
        self.is_stopped = False

    def run(self):
        try:
            video_files = self.find_video_files()
            if not video_files:
                self.progress_signal.emit("Видео файлы не найдены")
                return

            self.progress_signal.emit(f"Найдено {len(video_files)} файлов для обработки")
            
            successful = 0
            failed = 0
            total_files = len(video_files)

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_file = {
                    executor.submit(self.process_file, file_path): file_path 
                    for file_path in video_files
                }
                
                for i, future in enumerate(as_completed(future_to_file)):
                    while self.is_paused and not self.is_stopped:
                        self.msleep(100)
                    
                    if self.is_stopped:
                        self.progress_signal.emit("Конвертация остановлена")
                        break
                    
                    file_path = future_to_file[future]
                    try:
                        if future.result():
                            successful += 1
                        else:
                            failed += 1
                    except Exception as e:
                        self.error_signal.emit(f"Ошибка при обработке {file_path}: {str(e)}")
                        failed += 1
                    
                    self.file_progress_signal.emit(i + 1, total_files)

            if not self.is_stopped:
                self.finished_signal.emit(successful, failed)

        except Exception as e:
            self.error_signal.emit(f"Критическая ошибка: {str(e)}")

    def find_video_files(self):
        video_files = []
        source_path = Path(self.source_dir)
        
        for ext in self.input_formats:
            for file_path in source_path.rglob(f'*{ext}'):
                if file_path.is_file():
                    video_files.append(file_path)
        return video_files

    def process_file(self, source_path):
        if self.is_stopped:
            return False

        target_path = self.get_target_path(source_path)
        
        if target_path.exists():
            self.progress_signal.emit(f"Файл уже существует, пропускаем: {target_path.name}")
            return True
        
        self.create_target_directory(target_path)
        return self.convert_video(source_path, target_path)

    def get_target_path(self, source_path):
        relative_path = source_path.relative_to(self.source_dir)
        return Path(self.target_dir) / relative_path.with_suffix(f'.{self.output_format}')

    def create_target_directory(self, target_path):
        target_dir = target_path.parent
        target_dir.mkdir(parents=True, exist_ok=True)

    def convert_video(self, source_path, target_path):
        try:
            self.progress_signal.emit(f"Конвертация: {source_path.name}")
            
            # Базовые параметры
            ffmpeg_cmd = ['ffmpeg', '-i', str(source_path)]
            
            # Видео кодек и настройки
            ffmpeg_cmd.extend([
                '-c:v', 'libx264',
                '-preset', self.encoding_params['preset'],
                '-tune', self.encoding_params['tune'],
                '-profile:v', self.encoding_params['profile']
            ])
            
            # Битрейт (CBR)
            if self.encoding_params['bitrate_mode'] == 'cbr':
                ffmpeg_cmd.extend([
                    '-b:v', f"{self.encoding_params['bitrate']}M",
                    '-maxrate', f"{self.encoding_params['bitrate']}M",
                    '-minrate', f"{self.encoding_params['bitrate']}M",
                    '-bufsize', f"{self.encoding_params['bitrate'] * 2}M"
                ])
            else:  # VBR
                ffmpeg_cmd.extend(['-crf', str(self.encoding_params['crf'])])
            
            # Разрешение
            width, height = self.encoding_params['resolution']
            if width and height:
                scale_filter = f'scale={width}:{height}'
                
                # Добавляем паддинг для сохранения пропорций
                if self.encoding_params['maintain_aspect']:
                    scale_filter += ':force_original_aspect_ratio=decrease'
                    pad_filter = f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2'
                    ffmpeg_cmd.extend(['-vf', f'{scale_filter},{pad_filter},setsar=1'])
                else:
                    ffmpeg_cmd.extend(['-vf', f'{scale_filter},setsar=1'])
            
            # Частота кадров
            if self.encoding_params['fps']:
                ffmpeg_cmd.extend(['-r', str(self.encoding_params['fps'])])
            
            # Поля (interlacing)
            if self.encoding_params['field_order'] != 'progressive':
                if self.encoding_params['field_order'] == 'tff':
                    ffmpeg_cmd.extend(['-flags', '+ildct+ilme', '-top', '1'])
                elif self.encoding_params['field_order'] == 'bff':
                    ffmpeg_cmd.extend(['-flags', '+ildct+ilme', '-top', '0'])
            
            # Цветовые параметры
            ffmpeg_cmd.extend([
                '-pix_fmt', self.encoding_params['pixel_format'],
                '-colorspace', self.encoding_params['color_space'],
                '-color_primaries', self.encoding_params['color_primaries'],
                '-color_trc', self.encoding_params['color_transfer'],
                '-color_range', self.encoding_params['color_range'],
                '-movflags', '+faststart',
                '-y',
                str(target_path)
            ])
            
            # Аудио кодек
            if self.encoding_params['audio_codec'] == 'aac':
                ffmpeg_cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
            elif self.encoding_params['audio_codec'] == 'copy':
                ffmpeg_cmd.extend(['-c:a', 'copy'])
            else:  # no audio
                ffmpeg_cmd.extend(['-an'])
            
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.progress_signal.emit(f"Успешно: {source_path.name}")
                return True
            else:
                self.error_signal.emit(f"Ошибка конвертации {source_path.name}: {stderr[:500]}...")
                return False
                
        except Exception as e:
            self.error_signal.emit(f"Ошибка обработки {source_path.name}: {str(e)}")
            return False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def stop(self):
        self.is_stopped = True
        self.is_paused = False

class VideoConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Видео Конвертер Pro')
        self.setGeometry(100, 100, 1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Табы для настроек
        self.tabs = QTabWidget()
        
        # Основные настройки
        basic_tab = QWidget()
        self.setup_basic_tab(basic_tab)
        self.tabs.addTab(basic_tab, "Основные")
        
        # Настройки видео
        video_tab = QWidget()
        self.setup_video_tab(video_tab)
        self.tabs.addTab(video_tab, "Видео")
        
        # Настройки аудио
        audio_tab = QWidget()
        self.setup_audio_tab(audio_tab)
        self.tabs.addTab(audio_tab, "Аудио")
        
        layout.addWidget(self.tabs)

        # Прогресс
        progress_group = QGroupBox('Прогресс')
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel('Готов к работе')
        progress_layout.addWidget(self.progress_label)

        layout.addWidget(progress_group)

        # Лог
        log_group = QGroupBox('Лог выполнения')
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton('Старт')
        self.start_btn.clicked.connect(self.start_conversion)
        self.pause_btn = QPushButton('Пауза')
        self.pause_btn.clicked.connect(self.pause_conversion)
        self.pause_btn.setEnabled(False)
        self.stop_btn = QPushButton('Стоп')
        self.stop_btn.clicked.connect(self.stop_conversion)
        self.stop_btn.setEnabled(False)
        self.clear_btn = QPushButton('Очистить лог')
        self.clear_btn.clicked.connect(self.clear_log)

        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.pause_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.clear_btn)
        layout.addLayout(buttons_layout)

    def setup_basic_tab(self, tab):
        layout = QGridLayout(tab)

        # Исходная папка
        layout.addWidget(QLabel('Исходная папка:'), 0, 0)
        self.source_input = QLineEdit(r'\\192.168.0.11\data')
        layout.addWidget(self.source_input, 0, 1)
        self.source_btn = QPushButton('Обзор...')
        self.source_btn.clicked.connect(self.browse_source)
        layout.addWidget(self.source_btn, 0, 2)

        # Конечная папка
        layout.addWidget(QLabel('Конечная папка:'), 1, 0)
        self.target_input = QLineEdit(r'D:\---------архив')
        layout.addWidget(self.target_input, 1, 1)
        self.target_btn = QPushButton('Обзор...')
        self.target_btn.clicked.connect(self.browse_target)
        layout.addWidget(self.target_btn, 1, 2)

        # Форматы ввода
        layout.addWidget(QLabel('Исходные форматы:'), 2, 0)
        formats_widget = QWidget()
        formats_layout = QHBoxLayout(formats_widget)
        self.format_mp4 = QCheckBox('MP4')
        self.format_mp4.setChecked(True)
        self.format_avi = QCheckBox('AVI')
        self.format_avi.setChecked(True)
        self.format_mpg = QCheckBox('MPG')
        self.format_mpg.setChecked(True)
        self.format_mpeg2 = QCheckBox('MPEG2')
        self.format_mpeg2.setChecked(True)
        self.format_mxf = QCheckBox('MXF')
        self.format_mxf.setChecked(True)
        self.format_mov = QCheckBox('MOV')
        self.format_mov.setChecked(True)
        
        formats_layout.addWidget(self.format_mp4)
        formats_layout.addWidget(self.format_avi)
        formats_layout.addWidget(self.format_mpg)
        formats_layout.addWidget(self.format_mpeg2)
        formats_layout.addWidget(self.format_mxf)
        formats_layout.addWidget(self.format_mov)
        formats_layout.addStretch()
        layout.addWidget(formats_widget, 2, 1, 1, 2)

        # Конечный формат
        layout.addWidget(QLabel('Конечный формат:'), 3, 0)
        self.output_format = QComboBox()
        self.output_format.addItems(['mp4', 'mov', 'mkv'])
        self.output_format.setCurrentText('mp4')
        layout.addWidget(self.output_format, 3, 1)

        # Количество потоков
        layout.addWidget(QLabel('Потоки:'), 4, 0)
        self.threads_combo = QComboBox()
        self.threads_combo.addItems(['1', '2', '3', '4'])
        self.threads_combo.setCurrentText('2')
        layout.addWidget(self.threads_combo, 4, 1)

    def setup_video_tab(self, tab):
        layout = QGridLayout(tab)

        # Битрейт
        layout.addWidget(QLabel('Битрейт (Mbps):'), 0, 0)
        self.bitrate_spin = QSpinBox()
        self.bitrate_spin.setRange(1, 50)
        self.bitrate_spin.setValue(10)
        layout.addWidget(self.bitrate_spin, 0, 1)

        # Режим битрейта
        layout.addWidget(QLabel('Режим битрейта:'), 1, 0)
        self.bitrate_mode = QComboBox()
        self.bitrate_mode.addItems(['cbr', 'vbr'])
        self.bitrate_mode.setCurrentText('cbr')
        layout.addWidget(self.bitrate_mode, 1, 1)

        # CRF (для VBR)
        layout.addWidget(QLabel('CRF (VBR):'), 2, 0)
        self.crf_spin = QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(18)
        layout.addWidget(self.crf_spin, 2, 1)

        # Разрешение
        layout.addWidget(QLabel('Разрешение:'), 3, 0)
        self.resolution_combo = QComboBox()
        resolutions = [
            ('Исходное', (0, 0)),
            ('DV (720x576)', (720, 576)),
            ('HD (1280x720)', (1280, 720)),
            ('Full HD (1920x1080)', (1920, 1080)),
            ('2K (2048x1080)', (2048, 1080)),
            ('4K UHD (3840x2160)', (3840, 2160)),
            ('4K DCI (4096x2160)', (4096, 2160))
        ]
        for name, res in resolutions:
            self.resolution_combo.addItem(name, res)
        self.resolution_combo.setCurrentIndex(3)  # Full HD
        layout.addWidget(self.resolution_combo, 3, 1)

        # Сохранять пропорции
        self.maintain_aspect = QCheckBox('Сохранять пропорции')
        self.maintain_aspect.setChecked(True)
        layout.addWidget(self.maintain_aspect, 4, 0, 1, 2)

        # Частота кадров
        layout.addWidget(QLabel('Частота кадров:'), 5, 0)
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['Исходная', '23.976', '24', '25', '29.97', '30', '50', '60'])
        self.fps_combo.setCurrentText('Исходная')
        layout.addWidget(self.fps_combo, 5, 1)

        # Поля
        layout.addWidget(QLabel('Поля:'), 6, 0)
        self.field_order = QComboBox()
        self.field_order.addItems(['progressive', 'tff', 'bff'])
        self.field_order.setCurrentText('progressive')
        layout.addWidget(self.field_order, 6, 1)

        # Preset
        layout.addWidget(QLabel('Preset:'), 7, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'])
        self.preset_combo.setCurrentText('medium')
        layout.addWidget(self.preset_combo, 7, 1)

        # Tune
        layout.addWidget(QLabel('Tune:'), 8, 0)
        self.tune_combo = QComboBox()
        self.tune_combo.addItems(['film', 'animation', 'grain', 'stillimage', 'psnr', 'ssim', 'fastdecode', 'zerolatency'])
        self.tune_combo.setCurrentText('film')
        layout.addWidget(self.tune_combo, 8, 1)

        # Profile
        layout.addWidget(QLabel('Profile:'), 9, 0)
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(['baseline', 'main', 'high', 'high10', 'high422', 'high444'])
        self.profile_combo.setCurrentText('high')
        layout.addWidget(self.profile_combo, 9, 1)

        # Pixel format
        layout.addWidget(QLabel('Pixel Format:'), 10, 0)
        self.pixel_format = QComboBox()
        self.pixel_format.addItems(['yuv420p', 'yuv422p', 'yuv444p', 'yuv420p10le', 'yuv422p10le', 'yuv444p10le'])
        self.pixel_format.setCurrentText('yuv420p')
        layout.addWidget(self.pixel_format, 10, 1)

        # Color space
        layout.addWidget(QLabel('Color Space:'), 11, 0)
        self.color_space = QComboBox()
        self.color_space.addItems(['bt709', 'bt470bg', 'smpte170m', 'bt2020ncl'])
        self.color_space.setCurrentText('bt709')
        layout.addWidget(self.color_space, 11, 1)

    def setup_audio_tab(self, tab):
        layout = QGridLayout(tab)

        # Аудио кодек
        layout.addWidget(QLabel('Аудио кодек:'), 0, 0)
        self.audio_codec = QComboBox()
        self.audio_codec.addItems(['aac', 'copy', 'none'])
        self.audio_codec.setCurrentText('aac')
        layout.addWidget(self.audio_codec, 0, 1)

        # Битрэйт аудио
        layout.addWidget(QLabel('Аудио битрейт:'), 1, 0)
        self.audio_bitrate = QComboBox()
        self.audio_bitrate.addItems(['64k', '96k', '128k', '192k', '256k', '320k'])
        self.audio_bitrate.setCurrentText('128k')
        layout.addWidget(self.audio_bitrate, 1, 1)

    def get_encoding_params(self):
        resolution = self.resolution_combo.currentData()
        fps = None if self.fps_combo.currentText() == 'Исходная' else float(self.fps_combo.currentText())
        
        return {
            'bitrate': self.bitrate_spin.value(),
            'bitrate_mode': self.bitrate_mode.currentText(),
            'crf': self.crf_spin.value(),
            'resolution': resolution,
            'maintain_aspect': self.maintain_aspect.isChecked(),
            'fps': fps,
            'field_order': self.field_order.currentText(),
            'preset': self.preset_combo.currentText(),
            'tune': self.tune_combo.currentText(),
            'profile': self.profile_combo.currentText(),
            'pixel_format': self.pixel_format.currentText(),
            'color_space': self.color_space.currentText(),
            'color_primaries': 'bt709',
            'color_transfer': 'bt709',
            'color_range': 'tv',
            'audio_codec': self.audio_codec.currentText(),
            'audio_bitrate': self.audio_bitrate.currentText() if self.audio_codec.currentText() == 'aac' else None
        }

    def browse_source(self):
        directory = QFileDialog.getExistingDirectory(self, 'Выберите исходную папку')
        if directory:
            self.source_input.setText(directory)

    def browse_target(self):
        directory = QFileDialog.getExistingDirectory(self, 'Выберите конечную папку')
        if directory:
            self.target_input.setText(directory)

    def get_input_formats(self):
        formats = []
        if self.format_mp4.isChecked(): formats.append('.mp4')
        if self.format_avi.isChecked(): formats.append('.avi')
        if self.format_mpg.isChecked(): formats.append('.mpg')
        if self.format_mpeg2.isChecked(): formats.append('.mpeg2')
        if self.format_mxf.isChecked(): formats.append('.mxf')
        if self.format_mov.isChecked(): formats.append('.mov')
        return formats

    def start_conversion(self):
        source_dir = self.source_input.text().strip()
        target_dir = self.target_input.text().strip()
        input_formats = self.get_input_formats()
        output_format = self.output_format.currentText()
        max_workers = int(self.threads_combo.currentText())
        encoding_params = self.get_encoding_params()

        if not source_dir or not target_dir:
            QMessageBox.warning(self, 'Ошибка', 'Укажите исходную и конечную папки')
            return

        if not input_formats:
            QMessageBox.warning(self, 'Ошибка', 'Выберите хотя бы один исходный формат')
            return

        if not os.path.exists(source_dir):
            QMessageBox.warning(self, 'Ошибка', 'Исходная папка не существует')
            return

        os.makedirs(target_dir, exist_ok=True)

        self.worker = ConversionWorker(source_dir, target_dir, input_formats, 
                                     output_format, max_workers, encoding_params)
        self.worker.progress_signal.connect(self.update_log)
        self.worker.file_progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.conversion_finished)
        self.worker.error_signal.connect(self.update_log)

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        self.worker.start()

    def pause_conversion(self):
        if self.worker:
            if self.worker.is_paused:
                self.worker.resume()
                self.pause_btn.setText('Пауза')
                self.update_log("Возобновление конвертации...")
            else:
                self.worker.pause()
                self.pause_btn.setText('Продолжить')
                self.update_log("Пауза...")

    def stop_conversion(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.reset_buttons()
            self.update_log("Конвертация остановлена пользователем")

    def update_log(self, message):
        self.log_text.append(f"{message}")
        QApplication.processEvents()

    def update_progress(self, current, total):
        percentage = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f"Обработано: {current}/{total} файлов ({percentage}%)")

    def conversion_finished(self, successful, failed):
        self.reset_buttons()
        self.progress_bar.setValue(100)
        self.update_log(f"Конвертация завершена! Успешно: {successful}, Ошибок: {failed}")
        QMessageBox.information(self, 'Завершено', 
                               f'Конвертация завершена!\nУспешно: {successful}\nОшибок: {failed}')

    def reset_buttons(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText('Пауза')
        self.stop_btn.setEnabled(False)

    def clear_log(self):
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.progress_label.setText('Готов к работе')

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, 'Подтверждение',
                                       'Конвертация还在进行中。确定要退出吗？',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    converter = VideoConverterApp()
    converter.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()