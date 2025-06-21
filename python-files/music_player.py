import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QPushButton, QSlider, QLabel, QFileDialog, QProgressBar)
from PySide6.QtGui import QPixmap, QImage, QMovie
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PySide6.QtWidgets import QGraphicsOpacityEffect
import pygame
from mutagen.mp3 import MP3
import urllib.request
import tempfile

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shaaake")
        
        # Обычное окно с фиксированным начальным размером
        self.setGeometry(100, 100, 800, 600)

        # Установка фона
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.set_background_image("https://i.pinimg.com/736x/82/c1/17/82c1176d6b11d78e3e85a0b6ab204f8d.jpg")

        # Анимация тряски фона
        self.shake_animation = QPropertyAnimation(self.background_label, b"pos")
        self.shake_animation.setDuration(100)
        self.shake_animation.setLoopCount(-1)
        self.shake_animation.setKeyValueAt(0, self.background_label.pos())
        self.shake_animation.setKeyValueAt(0.25, self.background_label.pos() + QPoint(5, 0))
        self.shake_animation.setKeyValueAt(0.5, self.background_label.pos())
        self.shake_animation.setKeyValueAt(0.75, self.background_label.pos() + QPoint(-5, 0))
        self.shake_animation.setKeyValueAt(1, self.background_label.pos())

        # Стили для прозрачных "пузырьковых" кнопок
        self.setStyleSheet("""
            QMainWindow {
                background-color: transparent;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.5);
                border-radius: 15px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.8);
                transform: scale(1.05);
            }
            QSlider::groove:horizontal {
                height: 8px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: rgba(255, 255, 255, 0.8);
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background-color: rgba(44, 44, 44, 0.7);
                padding: 5px;
                border-radius: 5px;
            }
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 5px;
            }
        """)

        # Инициализация pygame для музыки
        pygame.mixer.init()

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(50, 50, 50, 50)
        self.layout.setSpacing(20)

        # GIF-анимация в левом верхнем углу
        self.gif_label = QLabel(self)
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setFixedSize(200, 150)  # Компактный размер
        self.gif_label.setScaledContents(True)  # Растягивать содержимое
        self.gif_label.setGeometry(20, 20, 200, 150)  # Левый верхний угол
        self.set_gif("https://i.pinimg.com/originals/7a/0a/95/7a0a95838c7df5d043351b8f79755e6b.gif")

        # Заполнитель для сохранения пространства
        self.layout.addStretch(1)

        # Панель управления
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(15)
        
        # Кнопки управления
        self.play_button = QPushButton("▶ Воспроизвести")
        self.play_button.clicked.connect(self.play_pause)
        self.controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton("■ Стоп")
        self.stop_button.clicked.connect(self.stop)
        self.controls_layout.addWidget(self.stop_button)

        self.next_button = QPushButton("⏭ Далее")
        self.next_button.clicked.connect(self.next_song)
        self.controls_layout.addWidget(self.next_button)

        self.prev_button = QPushButton("⏮ Назад")
        self.prev_button.clicked.connect(self.prev_song)
        self.controls_layout.addWidget(self.prev_button)

        self.layout.addLayout(self.controls_layout)

        # Ползунок громкости
        self.volume_layout = QHBoxLayout()
        self.volume_label = QLabel("Громкость:")
        self.volume_layout.addWidget(self.volume_label)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_layout.addWidget(self.volume_slider)
        self.layout.addLayout(self.volume_layout)

        # Ползунок прогресса
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Кнопка добавления музыки
        self.add_button = QPushButton("Добавить музыку")
        self.add_button.clicked.connect(self.add_music)
        self.layout.addWidget(self.add_button)

        # Таймер для обновления прогресса
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(1000)

        # Переменные состояния
        self.current_song = None
        self.is_playing = False
        self.songs = []
        self.current_index = -1
        self.song_length = 0

        # Загрузка сохраненного плейлиста
        self.load_playlist()

    def resizeEvent(self, event):
        # Обновление размеров фона и положения GIF при изменении размера окна
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.set_background_image("https://i.pinimg.com/736x/82/c1/17/82c1176d6b11d78e3e85a0b6ab204f8d.jpg")
        self.gif_label.setGeometry(20, 20, 200, 150)  # Сохраняем положение GIF в левом верхнем углу
        super().resizeEvent(event)

    def set_background_image(self, url):
        try:
            data = urllib.request.urlopen(url).read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.background_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        except Exception as e:
            print(f"Ошибка загрузки фона: {e}")

    def set_gif(self, url):
        try:
            # Кэширование GIF во временный файл
            data = urllib.request.urlopen(url).read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as tmp_file:
                tmp_file.write(data)
                tmp_file_path = tmp_file.name

            self.movie = QMovie(tmp_file_path)
            if not self.movie.isValid():
                print("Ошибка: GIF невалидна")
                return
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        except Exception as e:
            print(f"Ошибка загрузки GIF: {e}")

    def load_playlist(self):
        try:
            with open("playlist.json", "r") as f:
                data = json.load(f)
                self.songs = data.get("songs", [])
        except FileNotFoundError:
            pass

    def save_playlist(self):
        data = {"songs": self.songs}
        with open("playlist.json", "w") as f:
            json.dump(data, f)

    def add_music(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите музыкальные файлы", "", "MP3 Files (*.mp3)")
        for file in files:
            if file not in self.songs:
                self.songs.append(file)
        self.save_playlist()
        if self.songs and self.current_index == -1:
            self.current_index = 0
            self.play_song()

    def play_song(self):
        if self.current_index >= 0 and self.current_index < len(self.songs):
            self.current_song = self.songs[self.current_index]
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()
            self.is_playing = True
            self.play_button.setText("⏸ Пауза")
            self.shake_animation.start()

            # Получение длительности песни
            audio = MP3(self.current_song)
            self.song_length = audio.info.length
            self.progress_bar.setMaximum(int(self.song_length))

    def play_pause(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.setText("▶ Воспроизвести")
            self.shake_animation.stop()
        else:
            if self.current_song:
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.play_button.setText("⏸ Пауза")
                self.shake_animation.start()
            elif self.songs:
                self.current_index = 0
                self.play_song()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_button.setText("▶ Воспроизвести")
        self.shake_animation.stop()
        self.progress_bar.setValue(0)

    def next_song(self):
        if self.songs:
            self.current_index = (self.current_index + 1) % len(self.songs)
            self.play_song()

    def prev_song(self):
        if self.songs:
            self.current_index = (self.current_index - 1) % len(self.songs)
            self.play_song()

    def set_volume(self, value):
        pygame.mixer.music.set_volume(value / 100.0)

    def update_progress(self):
        if self.is_playing:
            pos = pygame.mixer.music.get_pos() / 1000
            self.progress_bar.setValue(int(pos))
            if pos >= self.song_length - 1:
                self.next_song()

    def closeEvent(self, event):
        self.save_playlist()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())