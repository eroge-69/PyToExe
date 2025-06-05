import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QFileDialog, QSlider
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
import pygame

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Music Player")
        self.setGeometry(300, 100, 600, 400)

        pygame.mixer.init()

        self.playlist = []
        self.current_index = -1
        self.is_playing = False

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label for song info
        self.song_label = QLabel("No song playing")
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.song_label)

        # Playlist list widget
        self.list_widget = QListWidget()
        self.list_widget.doubleClicked.connect(self.play_selected)
        layout.addWidget(self.list_widget)

        # Playback controls
        controls = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_pause)
        controls.addWidget(self.play_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop)
        controls.addWidget(self.stop_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_song)
        controls.addWidget(self.next_btn)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_song)
        controls.addWidget(self.prev_btn)

        layout.addLayout(controls)

        # Button to load files
        load_btn = QPushButton("Load Music Folder")
        load_btn.clicked.connect(self.load_folder)
        layout.addWidget(load_btn)

        self.setLayout(layout)

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if folder:
            self.playlist = []
            self.list_widget.clear()
            for file in os.listdir(folder):
                if file.endswith((".mp3", ".wav", ".ogg")):
                    full_path = os.path.join(folder, file)
                    self.playlist.append(full_path)
                    self.list_widget.addItem(file)
            if self.playlist:
                self.current_index = 0
                self.list_widget.setCurrentRow(0)
                self.update_song_label()

    def play_selected(self):
        self.current_index = self.list_widget.currentRow()
        self.play_song()

    def play_song(self):
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            return
        song = self.playlist[self.current_index]
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        self.is_playing = True
        self.update_song_label()
        self.play_btn.setText("Pause")

    def play_pause(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_btn.setText("Play")
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.play_btn.setText("Pause")
            else:
                self.play_song()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_btn.setText("Play")
        self.song_label.setText("No song playing")

    def next_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.list_widget.setCurrentRow(self.current_index)
        self.play_song()

    def prev_song(self):
        if not self.playlist:
            return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.list_widget.setCurrentRow(self.current_index)
        self.play_song()

    def update_song_label(self):
        if self.current_index < 0 or self.current_index >= len(self.playlist):
            self.song_label.setText("No song playing")
        else:
            song_name = os.path.basename(self.playlist[self.current_index])
            self.song_label.setText(f"Playing: {song_name}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec())