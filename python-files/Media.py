import sys
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlexBit MEDIA")
        self.resize(900, 600)
        self._setup_ui()

    def _setup_ui(self):
        # Основной медиаплеер
        self.player = QtMultimedia.QMediaPlayer(None,
            QtMultimedia.QMediaPlayer.VideoSurface)
        video_widget = QtMultimediaWidgets.QVideoWidget()
        self.player.setVideoOutput(video_widget)

        # Плейлист и связанный виджет
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.playlist_widget = QtWidgets.QListWidget()
        self.playlist_widget.setStyleSheet(
            "background-color: #2d2d30; color: white; border: none;"
        )
        self.playlist_widget.currentRowChanged.connect(
            self.playlist.setCurrentIndex
        )
        self.playlist.currentIndexChanged.connect(
            self.playlist_widget.setCurrentRow
        )

        # Кнопки управления
        btn_prev  = QtWidgets.QPushButton("⏮")
        btn_play  = QtWidgets.QPushButton("▶")
        btn_stop  = QtWidgets.QPushButton("⏹")
        btn_next  = QtWidgets.QPushButton("⏭")
        btn_open  = QtWidgets.QPushButton("Open")

        btn_prev.clicked.connect(self.playlist.previous)
        btn_play.clicked.connect(self._toggle_play)
        btn_stop.clicked.connect(self.player.stop)
        btn_next.clicked.connect(self.playlist.next)
        btn_open.clicked.connect(self._open_files)

        # Слайдер позиции
        self.pos_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.pos_slider.setRange(0, 0)
        self.pos_slider.sliderMoved.connect(self.player.setPosition)
        self.player.positionChanged.connect(self.pos_slider.setValue)
        self.player.durationChanged.connect(
            lambda d: self.pos_slider.setRange(0, d)
        )

        # Слайдер громкости
        vol_label = QtWidgets.QLabel("Vol")
        vol_label.setStyleSheet("color: white;")
        vol_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        vol_slider.setRange(0, 100)
        vol_slider.setValue(50)
        vol_slider.valueChanged.connect(
            lambda v: self.player.setVolume(v)
        )
        self.player.setVolume(50)

        # Раскладка контролов
        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(10)
        controls.addWidget(btn_prev)
        controls.addWidget(btn_play)
        controls.addWidget(btn_stop)
        controls.addWidget(btn_next)
        controls.addStretch()
        controls.addWidget(vol_label)
        controls.addWidget(vol_slider)
        controls.addStretch()
        controls.addWidget(btn_open)

        # Основная сетка
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(5, 5, 5, 5)
        grid.addWidget(self.playlist_widget, 0, 0)
        grid.addWidget(video_widget,            0, 1)
        grid.addWidget(self.pos_slider,         1, 0, 1, 2)
        grid.addLayout(controls,                2, 0, 1, 2)

        container = QtWidgets.QWidget()
        container.setLayout(grid)
        container.setStyleSheet("background-color: #1e1e1e;")
        self.setCentralWidget(container)

    def _open_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Open Media",
            filter="Media Files (*.mp4 *.mp3 *.wav *.avi *.mkv);;All Files (*)"
        )
        for path in files:
            url = QtCore.QUrl.fromLocalFile(path)
            self.playlist.addMedia(QtMultimedia.QMediaContent(url))
            self.playlist_widget.addItem(path.split("/")[-1])

        if self.playlist.mediaCount() > 0:
            self.playlist.setCurrentIndex(0)
            self.player.play()

    def _toggle_play(self):
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
