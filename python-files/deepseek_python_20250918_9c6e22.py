import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSlider, QFrame, QFileDialog, QListWidget,
                             QStackedWidget, QScrollArea, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QUrl
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor, QLinearGradient, QPainter, QPalette
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget

class GradientButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(50)
        self.setFont(QFont("Segoe UI", 12))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(108, 92, 231))
        gradient.setColorAt(1, QColor(253, 121, 168))
        
        # Draw rounded rectangle with gradient
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 25, 25)
        
        # Draw text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(0, 0, self.width(), self.height(), Qt.AlignCenter, self.text())

class WelcomeScreen(QWidget):
    start_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        # Logo
        logo = QLabel("♫")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 80px; color: #6c5ce7; text-shadow: 0 0 20px rgba(108, 92, 231, 0.7);")
        layout.addWidget(logo)
        
        # Title
        title = QLabel("Welcome to Rhythm Box")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #fd79a8, stop: 1 #6c5ce7);
            -webkit-background-clip: text;
            color: transparent;
        """)
        title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Your ultimate desktop music experience. Play your local music files, create playlists, and enjoy a seamless YouTube Music-like interface with powerful features.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet("font-size: 16px; color: #dfe6e9;")
        desc.setWordWrap(True)
        desc.setMaximumWidth(700)
        layout.addWidget(desc)
        
        # Start button
        self.start_btn = QPushButton("Start Listening")
        self.start_btn.setFixedSize(200, 60)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #6c5ce7, stop: 1 #fd79a8);
                border: none;
                border-radius: 30px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #7d6dec, stop: 1 #fd8ab8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #5d4fd6, stop: 1 #f85a9d);
            }
        """)
        self.start_btn.clicked.connect(self.start_signal.emit)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
        self.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0f0c29, stop: 0.5 #302b63, stop: 1 #24243e);")

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.media_player.setPlaylist(self.playlist)
        self.current_track_index = 0
        self.is_playing = False
        self.tracks = []
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 100);
                border-right: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo
        logo_widget = QWidget()
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(20, 20, 20, 30)
        logo = QLabel("♫ Rhythm Box")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #6c5ce7;")
        logo_layout.addWidget(logo)
        logo_widget.setLayout(logo_layout)
        sidebar_layout.addWidget(logo_widget)
        
        # Navigation
        nav_widget = QWidget()
        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(10, 0, 10, 0)
        nav_layout.setSpacing(5)
        
        nav_items = [
            ("Home", "fas fa-home", True),
            ("Discover", "fas fa-compass", False),
            ("Trending", "fas fa-fire", False),
            ("Favorites", "fas fa-heart", False)
        ]
        
        for name, icon, active in nav_items:
            btn = QPushButton(name)
            if active:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 15px;
                        font-size: 16px;
                        color: white;
                        border: none;
                        background-color: rgba(108, 92, 231, 100);
                        border-radius: 10px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 15px;
                        font-size: 16px;
                        color: white;
                        border: none;
                        background: transparent;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: rgba(108, 92, 231, 50);
                    }
                """)
            nav_layout.addWidget(btn)
        
        nav_widget.setLayout(nav_layout)
        sidebar_layout.addWidget(nav_widget)
        
        # Library section
        library_widget = QWidget()
        library_layout = QVBoxLayout()
        library_layout.setContentsMargins(15, 30, 15, 15)
        
        library_header = QWidget()
        library_header_layout = QHBoxLayout()
        library_header_layout.setContentsMargins(0, 0, 0, 0)
        library_title = QLabel("Your Library")
        library_title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        library_header_layout.addWidget(library_title)
        
        add_button = QPushButton("+")
        add_button.setFixedSize(30, 30)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(108, 92, 231, 100);
                border: none;
                border-radius: 15px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(108, 92, 231, 150);
            }
        """)
        add_button.clicked.connect(self.open_files)
        library_header_layout.addWidget(add_button)
        library_header.setLayout(library_header_layout)
        library_layout.addWidget(library_header)
        
        # Track list
        self.track_list = QListWidget()
        self.track_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 20);
            }
            QListWidget::item:selected {
                background-color: rgba(108, 92, 231, 100);
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: rgba(108, 92, 231, 50);
                border-radius: 5px;
            }
        """)
        self.track_list.itemClicked.connect(self.play_selected_track)
        library_layout.addWidget(self.track_list)
        
        library_widget.setLayout(library_layout)
        sidebar_layout.addWidget(library_widget)
        
        sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(sidebar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 20)
        content_layout.setSpacing(20)
        content_widget.setLayout(content_layout)
        
        # Top bar
        top_bar = QHBoxLayout()
        
        search_bar = QPushButton("🔍 Search for songs, artists, or podcasts")
        search_bar.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                font-size: 14px;
                color: #b2bec3;
                background-color: rgba(255, 255, 255, 25);
                border-radius: 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 35);
            }
        """)
        top_bar.addWidget(search_bar)
        
        user_profile = QPushButton("John Doe")
        user_profile.setIcon(QIcon.fromTheme("user"))
        user_profile.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
                color: white;
                background-color: rgba(255, 255, 255, 25);
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 35);
            }
        """)
        top_bar.addWidget(user_profile)
        
        content_layout.addLayout(top_bar)
        
        # Playlists section
        playlist_label = QLabel("Recently Played")
        playlist_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        content_layout.addWidget(playlist_label)
        
        playlists_widget = QWidget()
        playlists_layout = QHBoxLayout()
        playlists_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sample playlists
        playlists = [
            ("Chill Vibes", "Your daily chill mix"),
            ("Workout Energy", "Powerful beats for your workout"),
            ("Focus Time", "Concentration and productivity"),
            ("Driving Playlist", "Road trip music")
        ]
        
        for name, desc in playlists:
            playlist = QPushButton()
            playlist.setFixedSize(180, 220)
            playlist.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 10);
                    border-radius: 10px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 20);
                }
            """)
            
            playlist_layout = QVBoxLayout()
            playlist_layout.setContentsMargins(0, 0, 0, 0)
            
            # Placeholder for image
            img = QLabel()
            img.setFixedSize(180, 150)
            img.setStyleSheet("background-color: rgba(255, 255, 255, 20); border-top-left-radius: 10px; border-top-right-radius: 10px;")
            playlist_layout.addWidget(img)
            
            # Playlist info
            name_label = QLabel(name)
            name_label.setStyleSheet("font-weight: bold; color: white; padding: 5px;")
            name_label.setAlignment(Qt.AlignCenter)
            playlist_layout.addWidget(name_label)
            
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #b2bec3; padding: 5px;")
            desc_label.setAlignment(Qt.AlignCenter)
            desc_label.setWordWrap(True)
            playlist_layout.addWidget(desc_label)
            
            playlist.setLayout(playlist_layout)
            playlists_layout.addWidget(playlist)
        
        playlists_widget.setLayout(playlists_layout)
        
        # Scroll area for playlists
        scroll = QScrollArea()
        scroll.setWidget(playlists_widget)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_layout.addWidget(scroll)
        
        # Player controls
        controls = QFrame()
        controls.setFixedHeight(150)
        controls.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 50);
                border-radius: 15px;
            }
        """)
        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(20, 15, 20, 15)
        
        # Now playing
        now_playing = QHBoxLayout()
        
        self.album_art = QLabel()
        self.album_art.setFixedSize(70, 70)
        self.album_art.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 10px;
            }
        """)
        now_playing.addWidget(self.album_art)
        
        track_info = QVBoxLayout()
        self.track_name = QLabel("No track selected")
        self.track_name.setStyleSheet("font-weight: bold; color: white;")
        track_info.addWidget(self.track_name)
        
        self.artist_name = QLabel("Select a song to play")
        self.artist_name.setStyleSheet("color: #b2bec3;")
        track_info.addWidget(self.artist_name)
        
        now_playing.addLayout(track_info)
        now_playing.addStretch()
        controls_layout.addLayout(now_playing)
        
        # Progress bar
        progress_layout = QHBoxLayout()
        
        self.current_time = QLabel("0:00")
        self.current_time.setStyleSheet("color: #b2bec3;")
        self.current_time.setFixedWidth(40)
        progress_layout.addWidget(self.current_time)
        
        self.progress_bar = QSlider(Qt.Horizontal)
        self.progress_bar.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 5px;
                background: rgba(255, 255, 255, 25);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #6c5ce7, stop: 1 #fd79a8);
                border-radius: 3px;
            }
        """)
        self.progress_bar.sliderMoved.connect(self.set_position)
        progress_layout.addWidget(self.progress_bar)
        
        self.total_time = QLabel("0:00")
        self.total_time.setStyleSheet("color: #b2bec3;")
        self.total_time.setFixedWidth(40)
        progress_layout.addWidget(self.total_time)
        
        controls_layout.addLayout(progress_layout)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignCenter)
        
        control_buttons = [
            ("Random", "fas fa-random", self.toggle_shuffle),
            ("Previous", "fas fa-step-backward", self.previous_track),
            ("Play", "fas fa-play", self.play_pause),
            ("Next", "fas fa-step-forward", self.next_track),
            ("Repeat", "fas fa-redo", self.toggle_repeat)
        ]
        
        for text, icon, handler in control_buttons:
            btn = QPushButton(text)
            btn.setMinimumSize(50, 50)
            if text == "Play":
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #6c5ce7, stop: 1 #fd79a8);
                        border-radius: 25px;
                        color: white;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #7d6dec, stop: 1 #fd8ab8);
                    }
                """)
                self.play_btn = btn
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background: transparent;
                        border-radius: 25px;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 30);
                    }
                """)
            btn.clicked.connect(handler)
            buttons_layout.addWidget(btn)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_icon = QPushButton("🔊")
        volume_icon.setStyleSheet("color: white; border: none; background: transparent;")
        volume_icon.setFixedSize(30, 30)
        volume_layout.addWidget(volume_icon)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setValue(80)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 5px;
                background: rgba(255, 255, 255, 25);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #6c5ce7;
                border-radius: 3px;
            }
        """)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        buttons_layout.addLayout(volume_layout)
        
        controls_layout.addLayout(buttons_layout)
        controls.setLayout(controls_layout)
        content_layout.addWidget(controls)
        
        main_layout.addWidget(content_widget)
        
        # Set background
        self.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0f0c29, stop: 0.5 #302b63, stop: 1 #24243e);")
        
    def connect_signals(self):
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.stateChanged.connect(self.state_changed)
        
    def open_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Audio files (*.mp3 *.wav *.ogg *.flac *.m4a)")
        if file_dialog.exec_():
            file_names = file_dialog.selectedFiles()
            self.add_files(file_names)
            
    def add_files(self, file_names):
        for file_name in file_names:
            self.tracks.append(file_name)
            track_name = os.path.basename(file_name)
            item = QListWidgetItem(track_name)
            self.track_list.addItem(item)
            
            # Add to playlist
            url = QUrl.fromLocalFile(file_name)
            content = QMediaContent(url)
            self.playlist.addMedia(content)
            
        if len(self.tracks) > 0 and not self.is_playing:
            self.playlist.setCurrentIndex(0)
            self.current_track_index = 0
            self.update_track_info()
            
    def play_selected_track(self, item):
        index = self.track_list.row(item)
        self.playlist.setCurrentIndex(index)
        self.current_track_index = index
        self.media_player.play()
        self.is_playing = True
        self.play_btn.setText("Pause")
        self.update_track_info()
        
    def update_track_info(self):
        if len(self.tracks) > 0:
            track_name = os.path.basename(self.tracks[self.current_track_index])
            self.track_name.setText(track_name)
            self.artist_name.setText("Local Music")
        
    def play_pause(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.is_playing = False
            self.play_btn.setText("Play")
        else:
            if self.playlist.mediaCount() > 0:
                self.media_player.play()
                self.is_playing = True
                self.play_btn.setText("Pause")
                
    def previous_track(self):
        if self.playlist.mediaCount() > 0:
            self.playlist.previous()
            self.current_track_index = self.playlist.currentIndex()
            self.update_track_info()
            
    def next_track(self):
        if self.playlist.mediaCount() > 0:
            self.playlist.next()
            self.current_track_index = self.playlist.currentIndex()
            self.update_track_info()
            
    def toggle_shuffle(self):
        self.playlist.setPlaybackMode(QMediaPlaylist.Random)
        
    def toggle_repeat(self):
        if self.playlist.playbackMode() == QMediaPlaylist.Loop:
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
            
    def set_volume(self, value):
        self.media_player.setVolume(value)
        
    def set_position(self, position):
        self.media_player.setPosition(position)
        
    def position_changed(self, position):
        self.progress_bar.setValue(position)
        minutes = position // 60000
        seconds = (position % 60000) // 1000
        self.current_time.setText(f"{minutes}:{seconds:02d}")
        
    def duration_changed(self, duration):
        self.progress_bar.setRange(0, duration)
        minutes = duration // 60000
        seconds = (duration % 60000) // 1000
        self.total_time.setText(f"{minutes}:{seconds:02d}")
        
    def state_changed(self, state):
        if state == QMediaPlayer.StoppedState:
            self.play_btn.setText("Play")
            self.is_playing = False

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rhythm Box")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #0f0c29, stop: 0.5 #302b63, stop: 1 #24243e);
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Stacked widget to switch between welcome and player
        self.stacked_widget = QStackedWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        central_widget.setLayout(layout)
        
        # Welcome screen
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.start_signal.connect(self.show_player)
        self.stacked_widget.addWidget(self.welcome_screen)
        
        # Player screen
        self.player_screen = MusicPlayer()
        self.stacked_widget.addWidget(self.player_screen)
        
        # Show welcome screen first
        self.stacked_widget.setCurrentIndex(0)
        
    def show_player(self):
        self.stacked_widget.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create a palette for dark mode
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 12, 41))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(15, 12, 41))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(108, 92, 231))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = MainApp()
    window.show()
    
    sys.exit(app.exec_())