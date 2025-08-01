import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QListWidget
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPainter, QColor

class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.zoom = 1
        self.color = QColor(213, 0, 249)  # Magenta

    def set_waveform(self, data):
        self.data = data
        self.update()

    def set_zoom(self, zoom):
        self.zoom = zoom
        self.update()

    def set_color(self, color):
        self.color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        if self.data:
            w = self.width()
            h = self.height()
            step = max(1, int(len(self.data) / (w * self.zoom)))
            painter.setPen(self.color)
            for i in range(int(w * self.zoom)):
                idx = i * step
                if idx < len(self.data):
                    y = h // 2 + int(self.data[idx] * h // 2)
                    painter.drawPoint(int(i / self.zoom), y)

class DVJWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DVJ Software by D'Cruz Brian Jokey")
        self.setGeometry(100, 100, 1200, 800)

        # Decks
        self.playerA = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.playerB = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoA = QVideoWidget()
        self.videoB = QVideoWidget()
        self.playerA.setVideoOutput(self.videoA)
        self.playerB.setVideoOutput(self.videoB)

        # Controls
        self.playA = QPushButton('Play A')
        self.pauseA = QPushButton('Pause A')
        self.cueA = QPushButton('Cue A')
        self.loopA = QPushButton('Loop A')
        self.loopInA = QPushButton('Loop In A')
        self.loopOutA = QPushButton('Loop Out A')
        self.removeA = QPushButton('Remove Selected A')
        self.clearA = QPushButton('Clear Playlist A')
        self.saveA = QPushButton('Save Playlist A')
        self.loadListA = QPushButton('Load Playlist A')
        self.loadA = QPushButton('Load A')
        self.bpmA = QSlider(Qt.Horizontal)
        self.bpmA.setMinimum(60)
        self.bpmA.setMaximum(200)
        self.bpmA.setValue(120)
        self.bpmA.setToolTip('BPM A')
        self.speedA = QSlider(Qt.Horizontal)
        self.speedA.setMinimum(50)
        self.speedA.setMaximum(200)
        self.speedA.setValue(100)
        self.speedA.setToolTip('Speed A')
        self.effectA = QPushButton('Effect A')
        self.waveColorA = QPushButton('Waveform Color A')

        self.playB = QPushButton('Play B')
        self.pauseB = QPushButton('Pause B')
        self.cueB = QPushButton('Cue B')
        self.loopB = QPushButton('Loop B')
        self.loopInB = QPushButton('Loop In B')
        self.loopOutB = QPushButton('Loop Out B')
        self.removeB = QPushButton('Remove Selected B')
        self.clearB = QPushButton('Clear Playlist B')
        self.saveB = QPushButton('Save Playlist B')
        self.loadListB = QPushButton('Load Playlist B')
        self.loadB = QPushButton('Load B')
        self.bpmB = QSlider(Qt.Horizontal)
        self.bpmB.setMinimum(60)
        self.bpmB.setMaximum(200)
        self.bpmB.setValue(120)
        self.bpmB.setToolTip('BPM B')
        self.speedB = QSlider(Qt.Horizontal)
        self.speedB.setMinimum(50)
        self.speedB.setMaximum(200)
        self.speedB.setValue(100)
        self.speedB.setToolTip('Speed B')
        self.effectB = QPushButton('Effect B')
        self.waveColorB = QPushButton('Waveform Color B')

        # Crossfader
        self.crossfader = QSlider(Qt.Horizontal)
        self.crossfader.setMinimum(0)
        self.crossfader.setMaximum(100)
        self.crossfader.setValue(50)
        self.crossfader.valueChanged.connect(self.update_crossfader)

        # Waveform
        self.waveformA = WaveformWidget()
        self.waveformA.setFixedHeight(60)
        self.waveformB = WaveformWidget()
        self.waveformB.setFixedHeight(60)

        # Playlist
        self.playlistA = QListWidget()
        self.playlistB = QListWidget()

        # Layouts
        deckLayout = QHBoxLayout()
        deckA = QVBoxLayout()
        titleLabel = QLabel("DVJ Software by D'Cruz Brian Jokey")
        titleFont = titleLabel.font()
        titleFont.setPointSize(24)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        titleLabel.setStyleSheet("color: #d500f9; font-family: 'Segoe Script', 'Comic Sans MS', cursive;")
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(titleLabel)
        deckA.addWidget(QLabel('Deck A'))
        deckA.addWidget(self.videoA)
        deckA.addWidget(self.waveformA)
        deckA.addWidget(self.playlistA)
        deckA.addWidget(self.playA)
        deckA.addWidget(self.pauseA)
        deckA.addWidget(self.cueA)
        deckA.addWidget(self.loopA)
        deckA.addWidget(self.loopInA)
        deckA.addWidget(self.loopOutA)
        deckA.addWidget(self.removeA)
        deckA.addWidget(self.clearA)
        deckA.addWidget(self.saveA)
        deckA.addWidget(self.loadListA)
        deckA.addWidget(self.loadA)
        deckA.addWidget(QLabel('BPM'))
        deckA.addWidget(self.bpmA)
        deckA.addWidget(QLabel('Speed'))
        deckA.addWidget(self.speedA)
        deckA.addWidget(self.effectA)
        deckA.addWidget(self.waveColorA)
        deckB = QVBoxLayout()
        deckB.addWidget(QLabel('Deck B'))
        deckB.addWidget(self.videoB)
        deckB.addWidget(self.waveformB)
        deckB.addWidget(self.playlistB)
        deckB.addWidget(self.playB)
        deckB.addWidget(self.pauseB)
        deckB.addWidget(self.cueB)
        deckB.addWidget(self.loopB)
        deckB.addWidget(self.loopInB)
        deckB.addWidget(self.loopOutB)
        deckB.addWidget(self.removeB)
        deckB.addWidget(self.clearB)
        deckB.addWidget(self.saveB)
        deckB.addWidget(self.loadListB)
        # Waveform zoom controls
        self.zoomInA = QPushButton('Zoom In Waveform A')
        self.zoomOutA = QPushButton('Zoom Out Waveform A')
        deckA.addWidget(self.zoomInA)
        deckA.addWidget(self.zoomOutA)
        self.zoomInB = QPushButton('Zoom In Waveform B')
        self.zoomOutB = QPushButton('Zoom Out Waveform B')
        deckB.addWidget(self.zoomInB)
        deckB.addWidget(self.zoomOutB)
        deckB.addWidget(self.loadB)
        deckB.addWidget(QLabel('BPM'))
        deckB.addWidget(self.bpmB)
        deckB.addWidget(QLabel('Speed'))
        deckB.addWidget(self.speedB)
        deckB.addWidget(self.effectB)
        deckB.addWidget(self.waveColorB)
        deckLayout.addLayout(deckA)
        deckLayout.addLayout(deckB)

        mainLayout.addLayout(deckLayout)
        mainLayout.addWidget(QLabel('Crossfader'))
        mainLayout.addWidget(self.crossfader)

        centralWidget = QWidget()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        # Connect controls
        self.playA.clicked.connect(lambda: self.playerA.play())
        self.pauseA.clicked.connect(lambda: self.playerA.pause())
        self.cueA.clicked.connect(lambda: self.playerA.setPosition(0))
        self.loopA.clicked.connect(lambda: self.playerA.setLoops(-1))
        self.loopInA.clicked.connect(lambda: self.set_loop_in('A'))
        self.loopOutA.clicked.connect(lambda: self.set_loop_out('A'))
        self.removeA.clicked.connect(lambda: self.remove_selected('A'))
        self.clearA.clicked.connect(lambda: self.clear_playlist('A'))
        self.saveA.clicked.connect(lambda: self.save_playlist('A'))
        self.loadListA.clicked.connect(lambda: self.load_playlist('A'))
        self.zoomInA.clicked.connect(lambda: self.waveformA.set_zoom(self.waveformA.zoom * 1.2))
        self.zoomOutA.clicked.connect(lambda: self.waveformA.set_zoom(self.waveformA.zoom * 0.8))
        self.loadA.clicked.connect(self.load_videoA)
        self.bpmA.valueChanged.connect(lambda v: self.set_bpm('A', v))
        self.speedA.valueChanged.connect(lambda v: self.set_speed('A', v))
        self.effectA.clicked.connect(lambda: self.apply_effect('A'))
        self.waveColorA.clicked.connect(lambda: self.change_wave_color('A'))

        self.playB.clicked.connect(lambda: self.playerB.play())
        self.pauseB.clicked.connect(lambda: self.playerB.pause())
        self.cueB.clicked.connect(lambda: self.playerB.setPosition(0))
        self.loopB.clicked.connect(lambda: self.playerB.setLoops(-1))
        self.loopInB.clicked.connect(lambda: self.set_loop_in('B'))
        self.loopOutB.clicked.connect(lambda: self.set_loop_out('B'))
        self.removeB.clicked.connect(lambda: self.remove_selected('B'))
        self.clearB.clicked.connect(lambda: self.clear_playlist('B'))
        self.saveB.clicked.connect(lambda: self.save_playlist('B'))
        self.loadListB.clicked.connect(lambda: self.load_playlist('B'))
        self.zoomInB.clicked.connect(lambda: self.waveformB.set_zoom(self.waveformB.zoom * 1.2))
        self.zoomOutB.clicked.connect(lambda: self.waveformB.set_zoom(self.waveformB.zoom * 0.8))
        self.loadB.clicked.connect(self.load_videoB)
        self.playlistA.itemClicked.connect(self.playlistA_clicked)
        self.playlistB.itemClicked.connect(self.playlistB_clicked)
    # Loop in/out points
    def set_loop_in(self, deck):
        if deck == 'A':
            self.loop_in_A = self.playerA.position()
        else:
            self.loop_in_B = self.playerB.position()

    def set_loop_out(self, deck):
        if deck == 'A':
            self.loop_out_A = self.playerA.position()
        else:
            self.loop_out_B = self.playerB.position()

    # Playlist remove/clear
    def remove_selected(self, deck):
        if deck == 'A':
            items = self.playlistA.selectedItems()
            for item in items:
                self.playlistA.takeItem(self.playlistA.row(item))
        else:
            items = self.playlistB.selectedItems()
            for item in items:
                self.playlistB.takeItem(self.playlistB.row(item))

    def clear_playlist(self, deck):
        if deck == 'A':
            self.playlistA.clear()
        else:
            self.playlistB.clear()

    # Save/load playlists
    def save_playlist(self, deck):
        if deck == 'A':
            items = [self.playlistA.item(i).text() for i in range(self.playlistA.count())]
        else:
            items = [self.playlistB.item(i).text() for i in range(self.playlistB.count())]
        file, _ = QFileDialog.getSaveFileName(self, 'Save Playlist', '', 'Text Files (*.txt)')
        if file:
            with open(file, 'w') as f:
                for item in items:
                    f.write(item + '\n')

    def load_playlist(self, deck):
        file, _ = QFileDialog.getOpenFileName(self, 'Load Playlist', '', 'Text Files (*.txt)')
        if file:
            with open(file, 'r') as f:
                lines = f.read().splitlines()
            if deck == 'A':
                self.playlistA.clear()
                for line in lines:
                    self.playlistA.addItem(line)
            else:
                self.playlistB.clear()
                for line in lines:
                    self.playlistB.addItem(line)

    def set_bpm(self, deck, value):
        # Placeholder for BPM sync logic
        pass

    def set_speed(self, deck, value):
        speed = value / 100.0
        if deck == 'A':
            self.playerA.setPlaybackRate(speed)
        else:
            self.playerB.setPlaybackRate(speed)

    def apply_effect(self, deck):
        # Simple effect: toggle brightness
        if deck == 'A':
            self.videoA.setStyleSheet('background-color: magenta;')
        else:
            self.videoB.setStyleSheet('background-color: magenta;')

    def change_wave_color(self, deck):
        # Cycle between magenta, purple, green
        colors = [QColor(213,0,249), QColor(142,36,170), QColor(0,255,0)]
        if deck == 'A':
            current = self.waveformA.color
            idx = (colors.index(current) + 1) % len(colors) if current in colors else 0
            self.waveformA.set_color(colors[idx])
        else:
            current = self.waveformB.color
            idx = (colors.index(current) + 1) % len(colors) if current in colors else 0
            self.waveformB.set_color(colors[idx])

    def load_videoA(self):
        try:
            file, _ = QFileDialog.getOpenFileName(self, 'Load Video A', '', 'Video Files (*.mp4 *.avi *.mov)')
            if file:
                self.playerA.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
                self.playlistA.addItem(file)
        except Exception as e:
            print(f"Error loading video A: {e}")

    def load_videoB(self):
        try:
            file, _ = QFileDialog.getOpenFileName(self, 'Load Video B', '', 'Video Files (*.mp4 *.avi *.mov)')
            if file:
                self.playerB.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
                self.playlistB.addItem(file)
        except Exception as e:
            print(f"Error loading video B: {e}")

    def playlistA_clicked(self, item):
        self.playerA.setMedia(QMediaContent(QUrl.fromLocalFile(item.text())))
        self.playerA.play()

    def playlistB_clicked(self, item):
        self.playerB.setMedia(QMediaContent(QUrl.fromLocalFile(item.text())))
        self.playerB.play()

    def update_crossfader(self):
        # Simple crossfader: adjust volume
        value = self.crossfader.value()
        self.playerA.setVolume(100 - value)
        self.playerB.setVolume(value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DVJWindow()
    window.show()
    sys.exit(app.exec_())
