import sys, os, numpy as np, sounddevice as sd, soundfile as sf
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QIcon, QPolygon
from PyQt6.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QHBoxLayout

# ===== CONFIG =====
BAR_COUNT = 80
COLOR_THEMES = ["Bright", "Neon", "Pastel"]
current_theme_index = 0
visual_modes = ["Bar","Circle","Triangle","Waveform"]
visual_mode_index = 0
ICON_FILE = "appicon.ico"  # your .ico file here

# ---------- MP3 Detection ----------
mp3_files = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
if not mp3_files:
    print("No .mp3 files found in current folder.")
    sys.exit()

# Shared state
current_index = 0
data = None
samplerate = None
start_idx = 0
levels = np.zeros(BAR_COUNT)
stream = None
paused = False
volume = 1.0
is_muted = False
saved_volume = 1.0

# ---------- Audio Load ----------
def load_audio(file):
    global data, samplerate, start_idx
    d, sr = sf.read(file, dtype="float32")
    if d.ndim > 1:
        d = np.mean(d, axis=1)
    d /= np.max(np.abs(d))
    data, samplerate, start_idx = d, sr, 0

# ---------- Visualizer ----------
class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizer")
        self.setWindowIcon(QIcon(ICON_FILE))
        self.resize(900,450)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        self.show()
        self.rotation = 0.0
        self.pulse = 0.0

    def paintEvent(self, event):
        global levels, visual_mode_index, visual_modes, current_theme_index
        mode = visual_modes[visual_mode_index]
        theme = COLOR_THEMES[current_theme_index]

        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        w,h = self.width(), self.height()
        cx, cy = w//2, h//2

        def get_color(idx, intensity=1.0):
            t = theme
            if t == "Bright":
                hue = idx/BAR_COUNT
                return QColor.fromHsvF(hue,1,0.7+0.3*intensity)
            elif t == "Neon":
                hue = 0.5 + 0.5*np.sin(idx + self.rotation)
                return QColor.fromHsvF(hue%1.0,1,1)
            elif t == "Pastel":
                return QColor(min(255,int(200+55*intensity)),
                              min(255,int(180+55*intensity)),
                              min(255,int(220*intensity)))
            return QColor(255,255,255)

        if mode == "Bar":
            bar_width = w / BAR_COUNT
            for i,l in enumerate(levels):
                height = l*h*0.45
                qp.setBrush(get_color(i,l))
                qp.setPen(Qt.PenStyle.NoPen)
                x, y = int(i*bar_width), int(h/2-height)
                qp.drawRect(x, y, int(bar_width*0.8), int(height*2))
        elif mode == "Circle":
            radius = min(w,h)//4
            pulse_radius = radius + np.sin(self.pulse)*30
            for i,l in enumerate(levels):
                angle = (i/BAR_COUNT)*360 + self.rotation
                rad = np.radians(angle)
                x1 = int(cx + np.cos(rad)*pulse_radius)
                y1 = int(cy + np.sin(rad)*pulse_radius)
                x2 = int(cx + np.cos(rad)*(pulse_radius + l*pulse_radius))
                y2 = int(cy + np.sin(rad)*(pulse_radius + l*pulse_radius))
                qp.setPen(get_color(i, l))
                qp.drawLine(x1,y1,x2,y2)
            self.rotation += 3
            self.pulse += 0.08
            if self.rotation >= 360: self.rotation -= 360
        elif mode == "Triangle":
            radius = min(w,h)//4
            points = []
            for i,l in enumerate(levels):
                angle = (i/BAR_COUNT)*360 + self.rotation
                rad = np.radians(angle)
                x = int(cx + np.cos(rad)*(radius + l*radius))
                y = int(cy + np.sin(rad)*(radius + l*radius))
                points.append(QPoint(x,y))
            if points:
                polygon = QPolygon(points)
                qp.setPen(get_color(0))
                qp.setBrush(Qt.BrushStyle.NoBrush)
                qp.drawPolygon(polygon)
            self.rotation += 2
            if self.rotation >= 360: self.rotation -= 360
        elif mode == "Waveform":
            qp.setPen(get_color(0))
            prev_x, prev_y = 0, h//2
            for i,l in enumerate(levels):
                x = int(i*(w/len(levels)))
                y = int(h/2 - l*h*0.45)
                qp.drawLine(prev_x, prev_y, x, y)
                prev_x, prev_y = x, y

# ---------- Media Player ----------
class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Player")
        self.setWindowIcon(QIcon(ICON_FILE))
        self.resize(400,550)

        layout = QVBoxLayout()
        self.song_label = QLabel(mp3_files[current_index])
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.song_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⏮ Prev")
        self.prev_btn.clicked.connect(prev_song)
        self.play_btn = QPushButton("▶ Play/Pause")
        self.play_btn.clicked.connect(toggle_play)
        self.next_btn = QPushButton("⏭ Next")
        self.next_btn.clicked.connect(next_song)
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.next_btn)
        layout.addLayout(btn_layout)

        # Volume
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0,100)
        self.vol_slider.setValue(100)
        self.vol_slider.valueChanged.connect(self.change_volume)
        layout.addWidget(QLabel("Volume"))
        layout.addWidget(self.vol_slider)

        # Extra Controls
        self.mute_btn = QPushButton("🔊 Mute")
        self.mute_btn.setCheckable(True)
        self.mute_btn.clicked.connect(self.toggle_mute)
        layout.addWidget(self.mute_btn)

        self.vis_btn = QPushButton("Switch Visualizer")
        self.vis_btn.clicked.connect(self.toggle_visual)
        layout.addWidget(self.vis_btn)

        self.theme_btn = QPushButton("Switch Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        # Playlist
        self.list_widget = QListWidget()
        self.list_widget.addItems(mp3_files)
        self.list_widget.itemClicked.connect(self.play_song)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.show()
        self.highlight_current()

    def highlight_current(self):
        self.list_widget.setCurrentRow(current_index)
        self.song_label.setText(mp3_files[current_index])

    def play_song(self, item):
        global current_index
        current_index = self.list_widget.row(item)
        load_audio(mp3_files[current_index])
        start_stream()
        self.highlight_current()

    def change_volume(self, value):
        global volume
        volume = value/100

    def toggle_mute(self):
        global is_muted, volume, saved_volume
        if is_muted:
            volume = saved_volume
            self.mute_btn.setText("🔊 Mute")
        else:
            saved_volume = volume
            volume = 0
            self.mute_btn.setText("🔇 Unmute")
        is_muted = not is_muted

    def toggle_visual(self):
        global visual_mode_index
        visual_mode_index = (visual_mode_index +1)%len(visual_modes)

    def toggle_theme(self):
        global current_theme_index
        current_theme_index = (current_theme_index +1)%len(COLOR_THEMES)

# ---------- Audio callback ----------
def audio_callback(outdata, frames, time_info, status):
    global start_idx, levels
    chunk = data[start_idx:start_idx+frames]
    if len(chunk) < frames:
        outdata[:len(chunk),0] = chunk*volume
        outdata[len(chunk):] = 0
        next_song()
        raise sd.CallbackStop
    else:
        outdata[:,0] = chunk*volume

    step = max(1, len(chunk)//BAR_COUNT)
    lv = np.abs(chunk[::step])
    lv = np.clip(lv,0,1)
    levels[:] = 0.7*levels + 0.3*lv[:BAR_COUNT]
    start_idx += frames

# ---------- Stream control ----------
def start_stream(resume=False):
    global stream
    stop_stream()
    stream = sd.OutputStream(channels=1, samplerate=samplerate,
                             callback=audio_callback, blocksize=1024, latency="low")
    stream.start()
    media_win.highlight_current()

def stop_stream():
    global stream
    if stream:
        stream.stop()
        stream.close()

def toggle_play():
    global paused
    if paused:
        start_stream(resume=True)
    else:
        stop_stream()
    paused = not paused

def next_song():
    global current_index
    current_index = (current_index+1)%len(mp3_files)
    load_audio(mp3_files[current_index])
    start_stream()

def prev_song():
    global current_index
    current_index = (current_index-1)%len(mp3_files)
    load_audio(mp3_files[current_index])
    start_stream()

# ---------- Run App ----------
app = QApplication(sys.argv)
visual_win = Visualizer()
media_win = MediaPlayer()
media_win.move(visual_win.x()+visual_win.width()+10, visual_win.y())

load_audio(mp3_files[current_index])
start_stream()

sys.exit(app.exec())
