import sys, os, threading, time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QSlider, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from pydub import AudioSegment
from pydub.playback import play
import librosa
import simpleaudio as sa

class Track:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.bpm = 0
        self.key = ''
        self.duration = 0
        self.audio = None
        self.load_info()

    def load_info(self):
        y, sr = librosa.load(self.path, sr=None)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        self.bpm = round(tempo)
        chroma = librosa.feature.chroma_cens(y=y, sr=sr)
        self.key = self.detect_key(chroma)
        self.duration = librosa.get_duration(y=y, sr=sr)
        self.audio = AudioSegment.from_file(self.path)

    def detect_key(self, chroma):
        avg_chroma = chroma.mean(axis=1)
        key_index = avg_chroma.argmax()
        keys = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
        return keys[key_index]

class DJApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DJ Autônomo")
        self.setGeometry(100, 100, 900, 500)
        self.setStyleSheet("background-color:#1E1E1E; color:white; font-family:Arial;")
        self.tracks = []
        self.current_index = 0
        self.is_playing = False
        self.play_obj = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Playlist
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected_track)
        main_layout.addWidget(self.playlist_widget)

        # Deck info
        deck_layout = QHBoxLayout()
        self.track_label = QLabel("Nenhuma faixa carregada")
        deck_layout.addWidget(self.track_label)
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0,100)
        self.progress_slider.sliderReleased.connect(self.seek_track)
        deck_layout.addWidget(self.progress_slider)
        main_layout.addLayout(deck_layout)

        # Controls
        controls_layout = QHBoxLayout()
        self.load_btn = QPushButton("Carregar Pasta")
        self.load_btn.clicked.connect(self.load_folder)
        controls_layout.addWidget(self.load_btn)

        self.play_btn = QPushButton("▶ Play/Pause")
        self.play_btn.clicked.connect(self.toggle_play)
        controls_layout.addWidget(self.play_btn)

        self.next_btn = QPushButton("⏭ Próxima")
        self.next_btn.clicked.connect(self.play_next)
        controls_layout.addWidget(self.next_btn)

        self.crossfade_slider = QSlider(Qt.Horizontal)
        self.crossfade_slider.setRange(0,100)
        self.crossfade_slider.setValue(50)
        controls_layout.addWidget(QLabel("Crossfade"))
        controls_layout.addWidget(self.crossfade_slider)

        main_layout.addLayout(controls_layout)

        self.setLayout(main_layout)

        # Timer para atualizar progresso
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(500)

    def load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta")
        if folder:
            self.tracks.clear()
            self.playlist_widget.clear()
            for file in os.listdir(folder):
                if file.endswith(('.mp3', '.wav', '.flac')):
                    track = Track(os.path.join(folder, file))
                    self.tracks.append(track)
                    self.playlist_widget.addItem(f"{track.name} | BPM: {track.bpm} | Key: {track.key}")
            self.current_index = 0
            self.update_track_info()

    def update_track_info(self):
        if self.tracks:
            track = self.tracks[self.current_index]
            self.track_label.setText(f"{track.name} | BPM: {track.bpm} | Key: {track.key}")
        else:
            self.track_label.setText("Nenhuma faixa carregada")

    def play_selected_track(self):
        self.current_index = self.playlist_widget.currentRow()
        self.start_playback()

    def toggle_play(self):
        if self.is_playing:
            if self.play_obj:
                self.play_obj.stop()
            self.is_playing = False
        else:
            self.start_playback()

    def start_playback(self):
        if not self.tracks: return
        self.is_playing = True
        track = self.tracks[self.current_index]
        self.update_track_info()

        def play_thread():
            self.play_obj = sa.play_buffer(
                track.audio.raw_data,
                num_channels=track.audio.channels,
                bytes_per_sample=track.audio.sample_width,
                sample_rate=track.audio.frame_rate
            )
            self.play_obj.wait_done()
            self.play_next()
        threading.Thread(target=play_thread, daemon=True).start()

    def play_next(self):
        if not self.tracks: return
        self.current_index = (self.current_index + 1) % len(self.tracks)
        self.start_playback()

    def seek_track(self):
        # Placeholder, precisa de implementação de seek em pydub/simpleaudio
        pass

    def update_progress(self):
        if self.is_playing and self.tracks:
            # Placeholder para atualizar barra de progresso
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dj = DJApp()
    dj.show()
    sys.exit(app.exec())
