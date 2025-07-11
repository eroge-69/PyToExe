import sys
import os
import tempfile
import shutil
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSizePolicy, QSlider
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent


class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(35)
        self.setStyleSheet("background-color: #111;")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(10)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #03fcf4; font: bold 14px 'Courier New';")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.btn_min = QPushButton("—")
        self.style_btn(self.btn_min)
        self.btn_min.setToolTip("Minimize")
        self.btn_min.clicked.connect(self.parent.showMinimized)

        self.btn_max = QPushButton("⛶")
        self.style_btn(self.btn_max)
        self.btn_max.setToolTip("Maximize")
        self.btn_max.clicked.connect(self.toggle_max_restore)

        self.btn_close = QPushButton("✕")
        self.style_btn(self.btn_close)
        self.btn_close.setToolTip("Close")
        self.btn_close.clicked.connect(self.parent.close)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_max)
        self.layout.addWidget(self.btn_close)

        self._startPos = None
        self._clickPos = None
        self._isTracking = False

    def style_btn(self, btn):
        btn.setFixedSize(30, 25)
        btn.setFont(QFont("Courier New", 12, QFont.Bold))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #111;
                color: #03fcf4;
                border: none;
            }
            QPushButton:hover {
                background-color: #03fcf4;
                color: black;
            }
        """)

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.btn_max.setToolTip("Maximize")
        else:
            self.parent.showMaximized()
            self.btn_max.setToolTip("Restore")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._isTracking = True
            self._startPos = self.mapToGlobal(event.pos())
            self._clickPos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._isTracking:
            movePos = event.globalPos()
            diff = movePos - self._startPos
            newPos = self.parent.pos() + diff
            self.parent.move(newPos)
            self._startPos = movePos
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._isTracking = False
        super().mouseReleaseEvent(event)


class DarkwebMusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(400, 220)
        self.setStyleSheet("background-color: black; color: #03fcf4;")

        self.file_path = r"DXKIO2QMZ\AUDIO"  # Your audio file path (no extension)
        self.display_title = "BARBOZABRAVO"        # Title for header and label

        self.temp_file = self.prepare_temp_audio(self.file_path)

        self.init_ui()
        self.connect_signals()
        self.load_audio()

    def prepare_temp_audio(self, original_path):
        if not os.path.exists(original_path):
            raise FileNotFoundError(f"Audio file not found: {original_path}")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        shutil.copyfile(original_path, tmp.name)
        return tmp.name

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Custom Title Bar
        self.title_bar = CustomTitleBar(self, title=f"▶ {self.display_title} - PLAYER")
        self.layout.addWidget(self.title_bar)

        # Track label
        self.track_label = QLabel(self.display_title)
        self.track_label.setFont(QFont("Courier New", 14, QFont.Bold))
        self.track_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.track_label)

        # Timeline slider (seek bar)
        self.timeline_slider = QSlider(Qt.Horizontal)
        self.timeline_slider.setRange(0, 0)
        self.timeline_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px; background: #222;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #03fcf4;
                width: 16px;
                margin: -3px 0;
                border-radius: 8px;
            }
        """)
        self.layout.addWidget(self.timeline_slider)

        # Controls layout
        controls = QHBoxLayout()

        # Play / Pause button
        self.play_btn = QPushButton("▶ PLAY / PAUSE")
        self.play_btn.setFont(QFont("Courier New", 12, QFont.Bold))
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: #03fcf4;
                border: 2px solid #03fcf4;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #03fcf4;
                color: black;
            }
        """)
        controls.addWidget(self.play_btn)

        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)  # Default volume 50%
        self.volume_slider.setFixedWidth(150)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px; background: #222;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #03fcf4;
                width: 16px;
                margin: -3px 0;
                border-radius: 8px;
            }
        """)
        controls.addWidget(self.volume_slider)

        self.layout.addLayout(controls)

        self.player = QMediaPlayer()
        self.player.setVolume(50)

    def connect_signals(self):
        self.play_btn.clicked.connect(self.toggle_play_pause)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.timeline_slider.sliderMoved.connect(self.seek_position)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.check_finished)

    def load_audio(self):
        url = QUrl.fromLocalFile(self.temp_file)
        self.player.setMedia(QMediaContent(url))
        # Don't auto-play

    def toggle_play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def set_volume(self, value):
        self.player.setVolume(value)

    def seek_position(self, position):
        self.player.setPosition(position)

    def update_position(self, position):
        # Block slider signals temporarily to avoid recursion
        self.timeline_slider.blockSignals(True)
        self.timeline_slider.setValue(position)
        self.timeline_slider.blockSignals(False)

    def update_duration(self, duration):
        self.timeline_slider.setRange(0, duration)

    def check_finished(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.close()

    def closeEvent(self, event):
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DarkwebMusicPlayer()
    window.show()
    sys.exit(app.exec_())
