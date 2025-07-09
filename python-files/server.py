import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import sys
import os
import torch
import socket
import threading
from queue import Queue

from TTS.api import TTS
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup,
    QLineEdit, QFileDialog, QComboBox, QMessageBox, QHBoxLayout, QSpinBox
)
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QTimer

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Голосовой синтезатор (TTS)")
        self.setGeometry(100, 100, 520, 420)
        self.tts = None
        self.device = None
        self.cpu_threads = 2
        self.flask_queue = Queue()
        self.init_ui()
        # Таймер для проверки очереди от Flask
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_flask_queue)
        self.timer.start(200)

    def init_ui(self):
        self.layout = QVBoxLayout()

        # --- Блок выбора устройства ---
        self.device_label = QLabel("Выберите устройство для загрузки модели:")
        self.layout.addWidget(self.device_label)

        self.cpu_radio = QRadioButton("CPU")
        self.gpu_radio = QRadioButton("GPU")
        if torch.cuda.is_available():
            self.gpu_radio.setChecked(True)
        else:
            self.cpu_radio.setChecked(True)

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.cpu_radio)
        self.radio_group.addButton(self.gpu_radio)

        self.layout.addWidget(self.cpu_radio)
        self.layout.addWidget(self.gpu_radio)

        # --- Параметр мощности CPU ---
        self.cpu_power_label = QLabel("Мощность CPU (число потоков):")
        self.cpu_power_spin = QSpinBox()
        self.cpu_power_spin.setMinimum(1)
        self.cpu_power_spin.setMaximum(max(2, (os.cpu_count() or 4)))
        self.cpu_power_spin.setValue(min(4, self.cpu_power_spin.maximum()))
        self.cpu_power_spin.setEnabled(self.cpu_radio.isChecked())
        self.layout.addWidget(self.cpu_power_label)
        self.layout.addWidget(self.cpu_power_spin)

        self.cpu_radio.toggled.connect(self.toggle_cpu_power)

        # --- Кнопка загрузки модели ---
        self.load_button = QPushButton("Загрузить модель")
        self.load_button.clicked.connect(self.load_model)
        self.layout.addWidget(self.load_button)

        # --- Блок TTS ---
        self.text_label = QLabel("Введите текст для озвучивания:")
        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.text_input)

        self.speaker_label = QLabel("Файл с голосом (WAV):")
        self.speaker_input = QLineEdit("Starfire.wav")
        self.speaker_input.setEnabled(False)
        self.speaker_btn = QPushButton("Выбрать файл")
        self.speaker_btn.setEnabled(False)
        hbox = QHBoxLayout()
        hbox.addWidget(self.speaker_input)
        hbox.addWidget(self.speaker_btn)
        self.layout.addWidget(self.speaker_label)
        self.layout.addLayout(hbox)

        self.lang_label = QLabel("Язык:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "ru", "en", "de", "fr", "es", "it", "pt", "pl", "tr", "nl", "cs", "ar", "zh", "ja", "ko"
        ])
        self.layout.addWidget(self.lang_label)
        self.layout.addWidget(self.lang_combo)

        self.play_btn = QPushButton("Озвучить")
        self.play_btn.clicked.connect(self.speak)
        self.save_btn = QPushButton("Сохранить в файл")
        self.save_btn.clicked.connect(self.save_to_file)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.save_btn)
        self.layout.addLayout(btn_layout)

        # --- Блок запуска веб-сервера ---
        self.server_label = QLabel("Веб-сервер:")
        self.layout.addWidget(self.server_label)

        self.server_ip_label = QLabel(f"IP для сервера: {get_my_ip()}")
        self.layout.addWidget(self.server_ip_label)

        self.server_port_input = QLineEdit("4")
        self.server_port_input.setEnabled(False)
        self.layout.addWidget(self.server_port_input)

        self.server_btn = QPushButton("Запустить веб-сервер")
        self.server_btn.clicked.connect(self.start_web_server)
        self.layout.addWidget(self.server_btn)

        self.setLayout(self.layout)
        self.set_tts_controls_enabled(False)

    def toggle_cpu_power(self):
        self.cpu_power_spin.setEnabled(self.cpu_radio.isChecked())

    def set_tts_controls_enabled(self, enabled):
        self.text_input.setEnabled(enabled)
        self.lang_combo.setEnabled(enabled)
        self.play_btn.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)
        self.server_btn.setEnabled(enabled)

    def load_model(self):
        self.load_button.setEnabled(False)
        self.cpu_radio.setEnabled(False)
        self.gpu_radio.setEnabled(False)
        self.cpu_power_spin.setEnabled(False)
        if self.cpu_radio.isChecked():
            self.device = "cpu"
            self.cpu_threads = self.cpu_power_spin.value()
            torch.set_num_threads(self.cpu_threads)
        else:
            self.device = "cuda"
        try:
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            self.set_tts_controls_enabled(True)
            self.device_label.setText(
                f"Модель успешно загружена на {('CPU (' + str(self.cpu_threads) + ' потоков)') if self.device == 'cpu' else 'GPU'}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить модель:\n{e}")
            self.load_button.setEnabled(True)
            self.cpu_radio.setEnabled(True)
            self.gpu_radio.setEnabled(True)
            self.cpu_power_spin.setEnabled(self.cpu_radio.isChecked())

    def speak(self):
        text = self.text_input.text()
        speaker_wav = self.speaker_input.text()
        language = self.lang_combo.currentText()
        if not text or not speaker_wav:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите текст.")
            return
        wav = self.tts.tts(text=text, speaker_wav=speaker_wav, language=language)
        import soundfile as sf
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, wav, 24000)
            QSound.play(f.name)

    def save_to_file(self):
        text = self.text_input.text()
        speaker_wav = self.speaker_input.text()
        language = self.lang_combo.currentText()
        if not text or not speaker_wav:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите текст.")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "WAV Files (*.wav)")
        if save_path:
            self.tts.tts_to_file(text=text, speaker_wav=speaker_wav, language=language, file_path=save_path)
            QMessageBox.information(self, "Успех", f"Файл сохранён: {save_path}")

    def process_flask_queue(self):
        if not self.flask_queue.empty():
            text, language = self.flask_queue.get()
            self.text_input.setText(text)
            self.lang_combo.setCurrentText(language)
            self.speak()  # Автоматически синтезировать и воспроизвести

    def start_web_server(self):
        ip = get_my_ip()
        port = 4  # фиксированный порт
        threading.Thread(
            target=self.run_flask_server,
            args=(ip, port),
            daemon=True
        ).start()
        QMessageBox.information(self, "Сервер", f"Веб-сервер запущен на http://{ip}:{port}/")

    def run_flask_server(self, ip, port):
        from flask import Flask, request, jsonify
        app = Flask(__name__)

        @app.route('/synthesize', methods=['POST'])
        def synthesize():
            data = request.json
            text = data.get('text')
            language = data.get('language', 'ru')
            if not (self.tts and text):
                return jsonify({'error': 'Модель не загружена или не переданы параметры'}), 400
            # Положить задачу в очередь для главного потока PyQt5
            self.flask_queue.put((text, language))
            return jsonify({'status': 'accepted'})

        app.run(host=ip, port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TTSApp()
    window.show()
    sys.exit(app.exec_())
