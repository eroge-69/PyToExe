import sys, os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLabel, QSlider
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QDir
from PyQt5.QtGui import QPalette, QColor

class DualVideoPlayer(QWidget):
    def _init_(self):
        super()._init_()
        self.setWindowTitle("Created by Mr Roman")
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet("background-color: #6a0dad; color: white;")

        self.player1 = QMediaPlayer()
        self.player2 = QMediaPlayer()

        self.videoWidget1 = QVideoWidget()
        self.videoWidget2 = QVideoWidget()
        self.player1.setVideoOutput(self.videoWidget1)
        self.player2.setVideoOutput(self.videoWidget2)

        self.playPause1 = QPushButton("Play/Pause 1")
        self.playPause2 = QPushButton("Play/Pause 2")
        self.open1 = QPushButton("Open Video 1")
        self.open2 = QPushButton("Open Video 2")

        self.volumeSlider1 = QSlider(Qt.Horizontal)
        self.volumeSlider2 = QSlider(Qt.Horizontal)
        self.volumeSlider1.setValue(50)
        self.volumeSlider2.setValue(50)

        self.speedSlider1 = QSlider(Qt.Horizontal)
        self.speedSlider2 = QSlider(Qt.Horizontal)
        self.speedSlider1.setMinimum(5)
        self.speedSlider1.setMaximum(20)
        self.speedSlider1.setValue(10)
        self.speedSlider2.setMinimum(5)
        self.speedSlider2.setMaximum(20)
        self.speedSlider2.setValue(10)

        self.label = QLabel("💜 Created by Mr Roman 💜")
        self.label.setAlignment(Qt.AlignCenter)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.open1)
        controlLayout.addWidget(self.playPause1)
        controlLayout.addWidget(QLabel("Volume 1"))
        controlLayout.addWidget(self.volumeSlider1)
        controlLayout.addWidget(QLabel("Speed 1"))
        controlLayout.addWidget(self.speedSlider1)

        controlLayout.addWidget(self.open2)
        controlLayout.addWidget(self.playPause2)
        controlLayout.addWidget(QLabel("Volume 2"))
        controlLayout.addWidget(self.volumeSlider2)
        controlLayout.addWidget(QLabel("Speed 2"))
        controlLayout.addWidget(self.speedSlider2)

        videoLayout = QHBoxLayout()
        videoLayout.addWidget(self.videoWidget1)
        videoLayout.addWidget(self.videoWidget2)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addLayout(videoLayout)
        layout.addLayout(controlLayout)

        self.setLayout(layout)

        self.open1.clicked.connect(lambda: self.open_file(self.player1))
        self.open2.clicked.connect(lambda: self.open_file(self.player2))
        self.playPause1.clicked.connect(lambda: self.toggle_play(self.player1))
        self.playPause2.clicked.connect(lambda: self.toggle_play(self.player2))
        self.volumeSlider1.valueChanged.connect(lambda val: self.player1.setVolume(val))
        self.volumeSlider2.valueChanged.connect(lambda val: self.player2.setVolume(val))
        self.speedSlider1.valueChanged.connect(lambda val: self.player1.setPlaybackRate(val / 10.0))
        self.speedSlider2.valueChanged.connect(lambda val: self.player2.setPlaybackRate(val / 10.0))

        self.player1.mediaStatusChanged.connect(lambda status: self.handle_playlist(self.player1, self.playlist1) if status == QMediaPlayer.EndOfMedia else None)
        self.player2.mediaStatusChanged.connect(lambda status: self.handle_playlist(self.player2, self.playlist2) if status == QMediaPlayer.EndOfMedia else None)

        self.playlist1 = []
        self.playlist2 = []
        self.index1 = 0
        self.index2 = 0

        self.setAcceptDrops(True)

    def open_file(self, player):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            videos = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]
            videos.sort()
            if player == self.player1:
                self.playlist1 = videos
                self.index1 = 0
                self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(self.playlist1[self.index1])))
                self.player1.play()
            else:
                self.playlist2 = videos
                self.index2 = 0
                self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(self.playlist2[self.index2])))
                self.player2.play()

    def handle_playlist(self, player, playlist):
        if player == self.player1:
            self.index1 += 1
            if self.index1 < len(playlist):
                self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(playlist[self.index1])))
                self.player1.play()
        else:
            self.index2 += 1
            if self.index2 < len(playlist):
                self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(playlist[self.index2])))
                self.player2.play()

    def toggle_play(self, player):
        if player.state() == QMediaPlayer.PlayingState:
            player.pause()
        else:
            player.play()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.toggle_play(self.player1)
            self.toggle_play(self.player2)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = [url.toLocalFile() for url in event.mimeData().urls()]
        if urls:
            for file in urls:
                if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                    if not self.player1.mediaStatus() == QMediaPlayer.LoadedMedia:
                        self.player1.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
                        self.player1.play()
                    elif not self.player2.mediaStatus() == QMediaPlayer.LoadedMedia:
                        self.player2.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
                        self.player2.play()

if _name_ == '_main_':
    app = QApplication(sys.argv)
    window = DualVideoPlayer()
    window.show()
    sys.exit(app.exec_())