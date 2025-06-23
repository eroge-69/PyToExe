import sys
import os
import platform
import vlc
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QSlider, QPushButton, QFileDialog, QLabel, QHBoxLayout,
                            QFrame, QStyle, QSizePolicy, QToolButton, QShortcut)
from PyQt5.QtCore import Qt, QTimer, QSize, QPoint, QMimeData, QUrl, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (QIcon, QFont, QColor, QPalette, QDragEnterEvent, QDropEvent, 
                         QPainter, QLinearGradient, QBrush, QKeySequence, QPainterPath, 
                         QRegion, QGuiApplication)

class GlassMediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Window setup
        self.setWindowTitle("Lucid Media Player")
        self.setWindowIcon(QIcon.fromTheme("multimedia-player"))
        self.setGeometry(100, 100, 1000, 650)
        self.setMinimumSize(800, 500)
        
        # Initialize VLC with error handling
        try:
            self.instance = vlc.Instance("--no-xlib")
            self.media_player = self.instance.media_player_new()
        except Exception as e:
            self.show_error_message("VLC Initialization Error", 
                                  f"Failed to initialize VLC: {str(e)}\n\n"
                                  "Please ensure VLC media player is installed.")
            sys.exit(1)
        
        # UI Setup
        self.setup_ui()
        self.setup_shortcuts()
        self.setup_video_output()
        
        # Initial state
        self.is_fullscreen = False
        self.is_muted = False
        self.normal_geometry = None
        self.media_player.audio_set_volume(80)
        self.last_mouse_pos = None
        
        # Apply glass effect
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
    
    def setup_ui(self):
        """Initialize all UI components with glass theme"""
        self.setAcceptDrops(True)
        self.set_glass_theme()
        
        # Main widget with glass effect
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")
        self.setCentralWidget(self.main_widget)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(0)
        
        # Title bar (custom draggable)
        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(40)
        self.title_bar.mouseMoveEvent = self.move_window
        self.title_bar.mousePressEvent = self.get_mouse_pos
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        self.title_label = QLabel("Lucid Media Player")
        self.title_label.setObjectName("titleLabel")
        
        self.minimize_button = self.create_title_button("window-minimize", self.showMinimized)
        self.maximize_button = self.create_title_button("window-maximize", self.toggle_maximize)
        self.close_button = self.create_title_button("window-close", self.close)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.minimize_button)
        title_layout.addWidget(self.maximize_button)
        title_layout.addWidget(self.close_button)
        
        self.main_layout.addWidget(self.title_bar)
        
        # Video frame with rounded corners
        self.video_frame = QWidget()
        self.video_frame.setObjectName("videoFrame")
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_frame.setMouseTracking(True)
        self.video_frame.mouseDoubleClickEvent = self.toggle_fullscreen
        self.main_layout.addWidget(self.video_frame, 10)
        
        # Drop indicator
        self.drop_indicator = QLabel("Drop media file here")
        self.drop_indicator.setObjectName("dropIndicator")
        self.drop_indicator.hide()
        self.main_layout.addWidget(self.drop_indicator)
        
        # Control bar with glass effect
        self.control_bar = QWidget()
        self.control_bar.setObjectName("controlBar")
        self.control_bar.setFixedHeight(90)
        self.control_bar.setMouseTracking(True)
        
        control_layout = QHBoxLayout(self.control_bar)
        control_layout.setContentsMargins(20, 10, 20, 10)
        control_layout.setSpacing(15)
        
        # Create controls
        self.create_controls(control_layout)
        
        self.main_layout.addWidget(self.control_bar)
        
        # UI update timer
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update_ui)
        
        # Mouse timer for fullscreen controls
        self.mouse_timer = QTimer(self)
        self.mouse_timer.setInterval(3000)
        self.mouse_timer.timeout.connect(self.hide_controls_in_fullscreen)
        
        # Apply styles
        self.apply_styles()
        
        # Initial button states
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
    
    def create_controls(self, layout):
        """Create all control elements with glass buttons"""
        # Media info
        self.media_info = QLabel("No media loaded")
        self.media_info.setObjectName("mediaInfo")
        self.media_info.setMinimumWidth(200)
        
        # Time display
        self.time_label = QLabel("00:00:00 / 00:00:00")
        self.time_label.setObjectName("timeLabel")
        self.time_label.setMinimumWidth(150)
        
        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setObjectName("positionSlider")
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.setFixedWidth(120)
        
        # Buttons with glass effect
        self.open_button = self.create_glass_button("Open", "document-open", "Open file (Ctrl+O)", self.open_file)
        self.play_button = self.create_glass_button("", "media-playback-start", "Play (Space)", self.play)
        self.pause_button = self.create_glass_button("", "media-playback-pause", "Pause (Space)", self.pause)
        self.stop_button = self.create_glass_button("", "media-playback-stop", "Stop", self.stop)
        self.skip_back_button = self.create_glass_button("", "media-skip-backward", "Skip -10s (Left Arrow)", lambda: self.skip(-10))
        self.skip_forward_button = self.create_glass_button("", "media-skip-forward", "Skip +10s (Right Arrow)", lambda: self.skip(10))
        self.volume_button = self.create_glass_button("", "audio-volume-high", "Volume (M/Up/Down)", self.toggle_mute)
        self.fullscreen_button = self.create_glass_button("", "view-fullscreen", "Fullscreen (F/Double Click)", self.toggle_fullscreen)
        
        # Add to layout
        layout.addWidget(self.open_button)
        layout.addWidget(self.skip_back_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.skip_forward_button)
        layout.addWidget(self.media_info)
        layout.addWidget(self.time_label)
        layout.addWidget(self.position_slider, 1)  # Expanded
        layout.addWidget(self.volume_button)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.fullscreen_button)
    
    def create_glass_button(self, text, icon_name, tooltip, callback):
        """Create a glass-style button with icon"""
        button = QToolButton()
        button.setText(text)
        button.setToolTip(tooltip)
        
        # Try to load theme icon, fallback to system icon
        icon = QIcon.fromTheme(icon_name)
        if icon.isNull():
            try:
                icon = self.style().standardIcon(getattr(QStyle, f"SP_{icon_name.replace('-', '_')}"))
            except:
                pass
        
        if not icon.isNull():
            button.setIcon(icon)
            button.setIconSize(QSize(20, 20))
        
        button.clicked.connect(callback)
        return button
    
    def create_title_button(self, icon_name, callback):
        """Create title bar buttons"""
        button = QToolButton()
        button.setIcon(QIcon.fromTheme(icon_name))
        button.setIconSize(QSize(16, 16))
        button.setFixedSize(24, 24)
        button.clicked.connect(callback)
        button.setObjectName("titleButton")
        return button
    
    def apply_styles(self):
        """Apply glass theme styles"""
        self.main_widget.setStyleSheet("""
            #mainWidget {
                background: rgba(40, 40, 40, 0.7);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            #titleBar {
                background: rgba(50, 50, 50, 0.5);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            #titleLabel {
                color: #ddd;
                font-size: 14px;
                font-weight: bold;
            }
            #titleButton {
                background: transparent;
                border: none;
                border-radius: 12px;
            }
            #titleButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            #titleButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
            #videoFrame {
                background-color: #000;
                border-left: 1px solid rgba(255, 255, 255, 0.05);
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
            #dropIndicator {
                background-color: rgba(42, 130, 218, 0.5);
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: 3px dashed rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 40px;
                qproperty-alignment: AlignCenter;
            }
            #controlBar {
                background: rgba(50, 50, 50, 0.6);
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
            #mediaInfo {
                color: rgba(220, 220, 220, 0.9);
                font-size: 12px;
                qproperty-alignment: AlignVCenter;
                background: transparent;
            }
            #timeLabel {
                color: rgba(220, 220, 220, 0.9);
                font-size: 12px;
                qproperty-alignment: AlignCenter;
                background: transparent;
            }
            QSlider::groove:horizontal {
                height: 5px;
                background: rgba(70, 70, 70, 0.5);
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                    stop:0.6 rgba(255, 255, 255, 0.9),
                    stop:0.7 rgba(220, 220, 220, 0.8));
                border: 1px solid rgba(100, 100, 100, 0.8);
                width: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a73e8, stop:1 #6ec6ff);
                border-radius: 2px;
            }
            QToolButton {
                background: rgba(60, 60, 60, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                padding: 8px;
                color: rgba(220, 220, 220, 0.9);
            }
            QToolButton:hover {
                background: rgba(80, 80, 80, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QToolButton:pressed {
                background: rgba(100, 100, 100, 0.9);
            }
            QToolButton:disabled {
                color: rgba(150, 150, 150, 0.7);
                background: rgba(60, 60, 60, 0.3);
            }
        """)
        
        # Special style for close button
        self.close_button.setStyleSheet("""
            QToolButton {
                background: rgba(200, 60, 60, 0.3);
                border: 1px solid rgba(255, 150, 150, 0.1);
                border-radius: 12px;
            }
            QToolButton:hover {
                background: rgba(220, 80, 80, 0.7);
                border: 1px solid rgba(255, 180, 180, 0.3);
            }
            QToolButton:pressed {
                background: rgba(240, 100, 100, 0.9);
            }
        """)
    
    def set_glass_theme(self):
        """Set translucent glass theme palette"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(40, 40, 40, 150))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50, 150))
        palette.setColor(QPalette.ToolTipBase, QColor(50, 50, 50))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(60, 60, 60, 150))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218, 100))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.setPalette(palette)
    
    def setup_shortcuts(self):
        """Configure keyboard shortcuts"""
        # Playback control
        QShortcut(QKeySequence(Qt.Key_Space), self, self.toggle_play_pause)
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_file)
        
        # Fullscreen
        QShortcut(QKeySequence(Qt.Key_F), self, self.toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key_F11), self, self.toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.exit_fullscreen)
        
        # Volume
        QShortcut(QKeySequence(Qt.Key_M), self, self.toggle_mute)
        QShortcut(QKeySequence(Qt.Key_Up), self, self.volume_up)
        QShortcut(QKeySequence(Qt.Key_Down), self, self.volume_down)
        
        # Navigation
        QShortcut(QKeySequence(Qt.Key_Left), self, lambda: self.skip(-10))
        QShortcut(QKeySequence(Qt.Key_Right), self, lambda: self.skip(10))
        QShortcut(QKeySequence(Qt.Key_Comma), self, lambda: self.skip(-5))
        QShortcut(QKeySequence(Qt.Key_Period), self, lambda: self.skip(5))
        
        # Window management
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)
        QShortcut(QKeySequence("Ctrl+M"), self, self.showMinimized)
    
    def setup_video_output(self):
        """Configure VLC video output based on platform"""
        if not hasattr(self, 'media_player') or not self.video_frame.winId():
            return
            
        system = platform.system()
        if system == "Linux":
            self.media_player.set_xwindow(self.video_frame.winId())
        elif system == "Windows":
            self.media_player.set_hwnd(self.video_frame.winId())
        elif system == "Darwin":
            self.media_player.set_nsobject(int(self.video_frame.winId()))
    
    # Window management
    def move_window(self, event):
        """Allow window movement by dragging title bar"""
        if self.isMaximized() or self.isFullScreen():
            return
            
        if event.buttons() == Qt.LeftButton and self.last_mouse_pos:
            self.move(self.pos() + event.pos() - self.last_mouse_pos)
    
    def get_mouse_pos(self, event):
        """Store mouse position for window movement"""
        self.last_mouse_pos = event.pos()
    
    def toggle_maximize(self):
        """Toggle between normal and maximized state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    # Event handlers
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_indicator.show()
    
    def dragLeaveEvent(self, event):
        self.drop_indicator.hide()
    
    def dropEvent(self, event):
        self.drop_indicator.hide()
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.mp3', '.wav')):
                self.load_media(file_path)
                break
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() > self.title_bar.height():
            self.toggle_fullscreen()
    
    def mouseMoveEvent(self, event):
        if self.is_fullscreen:
            self.control_bar.show()
            self.title_bar.show()
            self.mouse_timer.start()
    
    # Media control methods
    def load_media(self, file_path):
        """Load a media file with error handling"""
        try:
            self.media = self.instance.media_new(file_path)
            self.media_player.set_media(self.media)
            self.media_info.setText(os.path.basename(file_path))
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.play()
        except Exception as e:
            self.show_error_message("Media Loading Error", f"Could not load media file:\n{str(e)}")
    
    def open_file(self):
        """Open file dialog with common media formats"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Media File", 
            "", 
            "Media Files (*.mp4 *.avi *.mkv *.mov *.mp3 *.wav *.flac *.m4a);;All Files (*)"
        )
        if filename:
            self.load_media(filename)
    
    def toggle_play_pause(self):
        """Toggle between play and pause states"""
        if self.media_player.is_playing():
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start playback with error handling"""
        if not self.media_player.get_media():
            self.open_file()
            if not self.media_player.get_media():
                return
                
        if self.media_player.play() == -1:
            self.show_error_message("Playback Error", "Could not play the media file")
            return
            
        self.timer.start()
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
    
    def pause(self):
        """Pause playback"""
        self.media_player.pause()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
    
    def stop(self):
        """Stop playback and reset UI"""
        self.media_player.stop()
        self.timer.stop()
        self.time_label.setText("00:00:00 / 00:00:00")
        self.position_slider.setValue(0)
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
    
    def skip(self, seconds):
        """Skip forward or backward in media"""
        if not self.media_player.get_media():
            return
            
        current_time = self.media_player.get_time()
        duration = self.media_player.get_length()
        new_time = max(0, min(current_time + seconds * 1000, duration))
        self.media_player.set_time(new_time)
        self.show_skip_indicator(seconds)
    
    def show_skip_indicator(self, seconds):
        """Show visual feedback for skip operation"""
        label = QLabel(f"{'+' if seconds > 0 else ''}{seconds}s", self)
        label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.7);
                padding: 8px 16px;
                border-radius: 6px;
            }
        """)
        label.setAlignment(Qt.AlignCenter)
        label.adjustSize()
        label.move(
            self.video_frame.width()//2 - label.width()//2,
            self.video_frame.height()//2 - label.height()//2
        )
        label.show()
        
        # Animate fade out
        animation = QPropertyAnimation(label, b"windowOpacity")
        animation.setDuration(1000)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.finished.connect(label.deleteLater)
        animation.start()
    
    def set_position(self, position):
        """Set playback position"""
        if self.media_player.get_media():
            self.media_player.set_position(position / 1000.0)
    
    def set_volume(self, volume):
        """Set volume with visual feedback"""
        self.media_player.audio_set_volume(volume)
        
        # Update volume button icon
        if volume == 0:
            icon = QIcon.fromTheme("audio-volume-muted")
        elif volume < 33:
            icon = QIcon.fromTheme("audio-volume-low")
        elif volume < 66:
            icon = QIcon.fromTheme("audio-volume-medium")
        else:
            icon = QIcon.fromTheme("audio-volume-high")
        
        if icon.isNull():
            try:
                icon = self.style().standardIcon(QStyle.SP_MediaVolume)
            except:
                pass
        
        self.volume_button.setIcon(icon)
    
    def toggle_mute(self):
        """Toggle mute state"""
        self.is_muted = not self.is_muted
        self.media_player.audio_set_mute(self.is_muted)
        
        if self.is_muted:
            icon = QIcon.fromTheme("audio-volume-muted")
        else:
            icon = QIcon.fromTheme("audio-volume-high")
        
        if icon.isNull():
            try:
                icon = self.style().standardIcon(QStyle.SP_MediaVolume)
            except:
                pass
        
        self.volume_button.setIcon(icon)
    
    def volume_up(self):
        """Increase volume by 5%"""
        new_vol = min(self.volume_slider.value() + 5, 100)
        self.volume_slider.setValue(new_vol)
    
    def volume_down(self):
        """Decrease volume by 5%"""
        new_vol = max(self.volume_slider.value() - 5, 0)
        self.volume_slider.setValue(new_vol)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode with animation"""
        if not self.is_fullscreen:
            self.normal_geometry = self.geometry()
            self.showFullScreen()
            self.is_fullscreen = True
            self.mouse_timer.start()
        else:
            self.exit_fullscreen()
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_fullscreen = False
            self.control_bar.show()
            self.title_bar.show()
            self.mouse_timer.stop()
    
    def hide_controls_in_fullscreen(self):
        """Hide controls in fullscreen after timeout"""
        if self.is_fullscreen:
            self.control_bar.hide()
            self.title_bar.hide()
    
    def update_ui(self):
        """Update player UI elements"""
        if self.media_player.get_media():
            media_pos = int(self.media_player.get_position() * 1000)
            self.position_slider.setValue(media_pos)
            
            media_time = self.media_player.get_time()
            media_length = self.media_player.get_length()
            
            if media_length > 0:
                self.time_label.setText(
                    f"{self.format_time(media_time)} / {self.format_time(media_length)}"
                )
    
    def format_time(self, ms):
        """Format milliseconds to HH:MM:SS"""
        seconds = int((ms / 1000) % 60)
        minutes = int((ms / (1000 * 60)) % 60)
        hours = int((ms / (1000 * 60 * 60)) % 24)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def show_error_message(self, title, message):
        """Show error message dialog"""
        error_dialog = QLabel(message, self)
        error_dialog.setWindowTitle(title)
        error_dialog.setStyleSheet("""
            QLabel {
                background: #333;
                color: #eee;
                padding: 20px;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        error_dialog.setAlignment(Qt.AlignCenter)
        error_dialog.setFixedSize(400, 150)
        error_dialog.move(
            self.width()//2 - error_dialog.width()//2,
            self.height()//2 - error_dialog.height()//2
        )
        error_dialog.show()
        
        # Auto-close after 3 seconds
        QTimer.singleShot(3000, error_dialog.close)

if __name__ == "__main__":
    # Check VLC availability
    try:
        import vlc
    except ImportError:
        print("Error: python-vlc not installed. Please install it with:")
        print("pip install python-vlc")
        print("Also ensure VLC media player is installed on your system")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set default font
    if platform.system() == "Windows":
        font = QFont("Segoe UI", 10)
    elif platform.system() == "Darwin":
        font = QFont("Helvetica Neue", 12)
    else:
        font = QFont("Arial", 10)
    app.setFont(font)
    
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    player = GlassMediaPlayer()
    player.show()
    sys.exit(app.exec_())