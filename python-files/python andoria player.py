import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QFileDialog, QLabel, QMenuBar, QAction
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer

class AndoriaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Andoria Player")
        self.setGeometry(100, 100, 1000, 700) # Increased size for better layout

        self.video_file_path = None
        self.audio_track2_file_path = None

        self.init_ui()
        self.init_media_players()

    def init_ui(self):
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 1. Video Widget
        self.video_widget = QVideoWidget()
        self.main_layout.addWidget(self.video_widget)

        # 2. Playback Controls
        self.controls_layout = QVBoxLayout()
        self.main_layout.addLayout(self.controls_layout)

        # Progress Slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.controls_layout.addWidget(self.position_slider)

        # Time Labels
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.controls_layout.addWidget(self.time_label)

        # Buttons Layout
        self.buttons_layout = QHBoxLayout()
        self.controls_layout.addLayout(self.buttons_layout)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_media)
        self.buttons_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_media)
        self.buttons_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_media)
        self.buttons_layout.addWidget(self.stop_button)

        # Volume Controls
        self.volume_layout = QHBoxLayout()
        self.controls_layout.addLayout(self.volume_layout)

        self.volume_label_video = QLabel("Video Vol:")
        self.volume_layout.addWidget(self.volume_label_video)
        self.volume_slider_video = QSlider(Qt.Horizontal)
        self.volume_slider_video.setRange(0, 100)
        self.volume_slider_video.setValue(50) # Default volume
        self.volume_slider_video.sliderMoved.connect(self.set_video_volume)
        self.volume_layout.addWidget(self.volume_slider_video)

        self.volume_label_track2 = QLabel("Track 2 Vol:")
        self.volume_layout.addWidget(self.volume_label_track2)
        self.volume_slider_track2 = QSlider(Qt.Horizontal)
        self.volume_slider_track2.setRange(0, 100)
        self.volume_slider_track2.setValue(50) # Default volume
        self.volume_slider_track2.sliderMoved.connect(self.set_track2_volume)
        self.volume_layout.addWidget(self.volume_slider_track2)

        # Menu Bar
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")

        open_video_action = QAction("Open Video (Track 1)", self)
        open_video_action.triggered.connect(self.open_video_file)
        self.file_menu.addAction(open_video_action)

        open_audio_track2_action = QAction("Open Audio (Track 2)", self)
        open_audio_track2_action.triggered.connect(self.open_audio_track2_file)
        self.file_menu.addAction(open_audio_track2_action)

    def init_media_players(self):
        # Player for Video (and its embedded audio)
        self.player_video = QMediaPlayer(self)
        self.player_video.setVideoOutput(self.video_widget)
        self.player_video.positionChanged.connect(self.position_changed)
        self.player_video.durationChanged.connect(self.duration_changed)
        self.player_video.stateChanged.connect(self.media_state_changed)
        self.player_video.setVolume(self.volume_slider_video.value())

        # Player for the second independent audio track
        self.player_audio_track2 = QMediaPlayer(self)
        self.player_audio_track2.setVolume(self.volume_slider_track2.value())

        # Timer to keep track of both players' states (optional, for more robust sync)
        self.sync_timer = QTimer(self)
        self.sync_timer.setInterval(100) # Check every 100ms
        self.sync_timer.timeout.connect(self.check_player_states)
        self.sync_timer.start()


    def open_video_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Media Files (*.mp4 *.avi *.mkv *.mov *.flv *.wmv *.mp3 *.wav *.ogg)")
        file_dialog.setWindowTitle("Open Video (Track 1)")
        if file_dialog.exec_():
            self.video_file_path = file_dialog.selectedFiles()[0]
            self.player_video.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_file_path)))
            self.setWindowTitle(f"Andoria Player - {self.video_file_path.split('/')[-1]}")
            self.stop_media() # Stop current playback before loading new media

    def open_audio_track2_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Audio Files (*.mp3 *.wav *.ogg *.flac)")
        file_dialog.setWindowTitle("Open Audio (Track 2)")
        if file_dialog.exec_():
            self.audio_track2_file_path = file_dialog.selectedFiles()[0]
            self.player_audio_track2.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_track2_file_path)))
            self.stop_media() # Stop current playback before loading new media

    def play_media(self):
        if self.player_video.mediaStatus() == QMediaPlayer.NoMedia and self.video_file_path:
            self.player_video.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_file_path)))
        if self.player_audio_track2.mediaStatus() == QMediaPlayer.NoMedia and self.audio_track2_file_path:
            self.player_audio_track2.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_track2_file_path)))

        if self.player_video.mediaStatus() != QMediaPlayer.NoMedia:
            self.player_video.play()
        if self.player_audio_track2.mediaStatus() != QMediaPlayer.NoMedia:
            self.player_audio_track2.play()

    def pause_media(self):
        self.player_video.pause()
        self.player_audio_track2.pause()

    def stop_media(self):
        self.player_video.stop()
        self.player_audio_track2.stop()
        self.position_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")

    def set_position(self, position):
        # Only seek the video player, as it's typically the primary timeline
        self.player_video.setPosition(position)
        # For perfect sync, you might want to seek player_audio_track2 as well,
        # but it depends on whether it's supposed to follow the video's timeline.
        # For independent tracks, you might not want this.
        # self.player_audio_track2.setPosition(position)

    def position_changed(self, position):
        self.position_slider.setValue(position)
        self.update_time_label(position, self.player_video.duration())

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)
        self.update_time_label(self.player_video.position(), duration)

    def update_time_label(self, current_pos, total_duration):
        current_minutes = (current_pos // 1000) // 60
        current_seconds = (current_pos // 1000) % 60
        total_minutes = (total_duration // 1000) // 60
        total_seconds = (total_duration // 1000) % 60
        self.time_label.setText(
            f"{current_minutes:02}:{current_seconds:02} / {total_minutes:02}:{total_seconds:02}"
        )

    def media_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        elif state == QMediaPlayer.PausedState:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        elif state == QMediaPlayer.StoppedState:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(False) # Enable stop only if media is loaded
            if self.player_video.mediaStatus() != QMediaPlayer.NoMedia or \
               self.player_audio_track2.mediaStatus() != QMediaPlayer.NoMedia:
                self.stop_button.setEnabled(True)

    def set_video_volume(self, volume):
        self.player_video.setVolume(volume)

    def set_track2_volume(self, volume):
        self.player_audio_track2.setVolume(volume)

    def check_player_states(self):
        # This timer helps ensure both players are in sync if one finishes before the other
        # or if there are slight desyncs.
        # For simplicity, we'll just ensure they both stop if the video finishes.
        if self.player_video.state() == QMediaPlayer.StoppedState and \
           self.player_video.mediaStatus() == QMediaPlayer.EndOfMedia:
            self.stop_media()
        # You could add more complex logic here, e.g., restarting track 2 if it's shorter and looped.


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = AndoriaPlayer()
    player.show()
    sys.exit(app.exec_())
