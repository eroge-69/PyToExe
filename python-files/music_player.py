import sys, os, threading, requests
from PyQt5 import QtCore, QtGui, QtWidgets
import vlc, yt_dlp
from ytmusicapi import YTMusic

class GlassMusicPlayer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Glassmorphic Music Player")
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowStaysOnBottomHint
        )

        self.transparency_level = 85
        self.locked = False
        self.base_width = 420
        self.base_height = 140
        self.size_scale = 1.0
        self.setFixedSize(self.base_width, self.base_height)
        self.oldPos = None
        self.search_results = []
        self.current_song_index = -1
        self.is_playing = False
        self.is_paused = False
        self.current_playlist = []

        # VLC setup with error handling - removed deprecated plugin-path option
        try:
            vlc_path = r"C:\Users\Injamam khan\Documents\VLC\libvlc.dll"
            if not os.path.exists(vlc_path):
                # Try default VLC installation paths
                default_paths = [
                    r"C:\Program Files\VideoLAN\VLC\libvlc.dll",
                    r"C:\Program Files (x86)\VideoLAN\VLC\libvlc.dll"
                ]
                vlc_path = None
                for path in default_paths:
                    if os.path.exists(path):
                        vlc_path = path
                        break
                
                if not vlc_path:
                    raise FileNotFoundError("VLC library not found in common locations")
            
            # Initialize VLC without deprecated options
            self.instance = vlc.Instance(['--intf', 'dummy', '--no-video'])
            self.player = self.instance.media_player_new()
            self.player.event_manager().event_attach(
                vlc.EventType.MediaPlayerEndReached, 
                lambda event: self.play_next()
            )
        except Exception as e:
            print(f"VLC initialization failed: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to initialize VLC: {e}\n\nPlease ensure VLC is installed.")
            sys.exit(1)

        # Load icons and default thumbnail
        self.load_icons()
        self.load_default_thumbnail()
        self.setup_ui()

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(300)

    def load_icons(self):
        """Load button icons with fallback to text symbols"""
        try:
            self.backward_icon = QtGui.QIcon(r"C:\Users\Injamam khan\Downloads\backward-step-svgrepo-com.png")
            self.play_icon = QtGui.QIcon(r"C:\Users\Injamam khan\Downloads\play-button-svgrepo-com.png")
            self.pause_icon = QtGui.QIcon(r"C:\Users\Injamam khan\Downloads\pause-button-svgrepo-com.png")
            self.forward_icon = QtGui.QIcon(r"C:\Users\Injamam khan\Downloads\forward-step-svgrepo-com.png")
            self.search_icon = QtGui.QIcon(r"C:\Users\Injamam khan\Downloads\search-svgrepo-com.png")
            self.icons_loaded = True
        except Exception as e:
            print(f"Failed to load icons: {e}")
            self.backward_icon = QtGui.QIcon()
            self.play_icon = QtGui.QIcon()
            self.pause_icon = QtGui.QIcon()
            self.forward_icon = QtGui.QIcon()
            self.search_icon = QtGui.QIcon()
            self.icons_loaded = False

    def load_default_thumbnail(self):
        try:
            default_img = QtGui.QImage()
            default_img.loadFromData(requests.get(
                "https://i.pinimg.com/736x/0f/82/a5/0f82a5e18e41f51805cd56c2e44217e6.jpg",
                timeout=5
            ).content)
            self.default_pixmap = QtGui.QPixmap(default_img).scaled(
                int(85 * self.size_scale), int(85 * self.size_scale), 
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        except:
            self.default_pixmap = QtGui.QPixmap(int(85 * self.size_scale), int(85 * self.size_scale))
            self.default_pixmap.fill(QtGui.QColor(100, 100, 100))

    def setup_ui(self):
        # Clear existing layout if any
        if self.layout():
            QtWidgets.QWidget().setLayout(self.layout())

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(15)

        self.setup_album_art(main_layout)
        self.setup_center_section(main_layout)
        self.setup_right_section(main_layout)
        self.setup_search_popup()

    def setup_album_art(self, parent_layout):
        art_container = QtWidgets.QWidget()
        art_container.setFixedSize(int(90 * self.size_scale), int(90 * self.size_scale))
        
        art_layout = QtWidgets.QVBoxLayout(art_container)
        art_layout.setContentsMargins(0, 0, 0, 0)
        
        self.album_art = QtWidgets.QLabel()
        self.album_art.setFixedSize(int(85 * self.size_scale), int(85 * self.size_scale))
        self.album_art.setPixmap(self.default_pixmap)
        self.album_art.setStyleSheet("""
            QLabel {
                border-radius: 12px;
                background: rgba(0,0,0,0.1);
                border: 2px solid rgba(255,255,255,0.3);
            }
        """)
        self.album_art.setScaledContents(True)
        art_layout.addWidget(self.album_art, alignment=QtCore.Qt.AlignCenter)
        
        parent_layout.addWidget(art_container)

    def setup_center_section(self, parent_layout):
        center_widget = QtWidgets.QWidget()
        center_layout = QtWidgets.QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 5, 0, 5)
        center_layout.setSpacing(8)

        self.song_title = QtWidgets.QLabel("No Song Playing")
        self.song_title.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.song_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: rgba(0,0,0,0.9);
                background: transparent;
                padding: 2px 4px;
            }
        """)
        self.song_title.setWordWrap(True)
        center_layout.addWidget(self.song_title)

        self.artist_name = QtWidgets.QLabel("Unknown Artist")
        self.artist_name.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.artist_name.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: rgba(0,0,0,0.6);
                background: transparent;
                padding: 0px 4px;
            }
        """)
        center_layout.addWidget(self.artist_name)

        timeline_container = QtWidgets.QHBoxLayout()
        timeline_container.setSpacing(8)
        
        self.current_time = QtWidgets.QLabel("0:00")
        self.current_time.setStyleSheet("font-size: 9px; color: rgba(0,0,0,0.6);")
        timeline_container.addWidget(self.current_time)
        
        self.timeline = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.timeline.setRange(0, 1000)
        self.timeline.setValue(0)
        self.timeline.sliderMoved.connect(self.seek_position)
        self.timeline.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(0,0,0,0.2);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: rgba(0,0,0,0.7);
                border: none;
                width: 12px;
                height: 12px;
                border-radius: 6px;
                margin: -4px 0;
            }
            QSlider::sub-page:horizontal {
                background: rgba(0,0,0,0.5);
                border-radius: 2px;
            }
        """)
        timeline_container.addWidget(self.timeline)
        
        self.total_time = QtWidgets.QLabel("0:00")
        self.total_time.setStyleSheet("font-size: 9px; color: rgba(0,0,0,0.6);")
        timeline_container.addWidget(self.total_time)
        
        center_layout.addLayout(timeline_container)

        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.setSpacing(12)
        controls_layout.setContentsMargins(0, 5, 0, 0)

        self.prev_btn = self.create_control_button(self.backward_icon, int(32 * self.size_scale), "⏮")
        self.prev_btn.clicked.connect(self.play_previous)
        
        self.play_btn = self.create_control_button(self.play_icon, int(38 * self.size_scale), "▶", primary=True)
        self.play_btn.clicked.connect(self.toggle_play_pause)
        
        self.next_btn = self.create_control_button(self.forward_icon, int(32 * self.size_scale), "⏭")
        self.next_btn.clicked.connect(self.play_next)
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addStretch()

        center_layout.addLayout(controls_layout)
        parent_layout.addWidget(center_widget, 1)

    def setup_right_section(self, parent_layout):
        right_widget = QtWidgets.QWidget()
        right_widget.setFixedWidth(int(50 * self.size_scale))
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.search_btn = QtWidgets.QPushButton()
        if self.icons_loaded and not self.search_icon.isNull():
            self.search_btn.setIcon(self.search_icon)
        else:
            self.search_btn.setText("🔍")
        self.search_btn.setFixedSize(int(38 * self.size_scale), int(38 * self.size_scale))
        self.search_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.4);
                border: 1px solid rgba(255,255,255,0.6);
                border-radius: 19px;
                font-size: 16px;
                color: rgba(0,0,0,0.8);
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.6);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.3);
            }
        """)
        self.search_btn.clicked.connect(self.show_search_bar)

        self.volume_btn = QtWidgets.QPushButton("🔊")
        self.volume_btn.setFixedSize(int(38 * self.size_scale), int(38 * self.size_scale))
        self.volume_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.volume_btn.setStyleSheet(self.search_btn.styleSheet())

        right_layout.addStretch()
        right_layout.addWidget(self.search_btn, alignment=QtCore.Qt.AlignCenter)
        right_layout.addWidget(self.volume_btn, alignment=QtCore.Qt.AlignCenter)
        right_layout.addStretch()

        parent_layout.addWidget(right_widget)

    def create_control_button(self, icon, size, fallback_text="", primary=False):
        btn = QtWidgets.QPushButton()
        
        if self.icons_loaded and not icon.isNull():
            btn.setIcon(icon)
        else:
            btn.setText(fallback_text)
            
        btn.setFixedSize(size, size)
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        if primary:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(0,0,0,0.7);
                    border: none;
                    border-radius: {size//2}px;
                    font-size: 16px;
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: rgba(0,0,0,0.85);
                }}
                QPushButton:pressed {{
                    background: rgba(0,0,0,0.6);
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.4);
                    border: 1px solid rgba(255,255,255,0.5);
                    border-radius: {size//2}px;
                    font-size: 14px;
                    color: rgba(0,0,0,0.8);
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.6);
                }}
                QPushButton:pressed {{
                    background: rgba(255,255,255,0.3);
                }}
            """)
        return btn

    def setup_search_popup(self):
        self.search_popup = QtWidgets.QWidget()
        self.search_popup.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.search_popup.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Override paintEvent for search popup
        def popup_paint_event(event):
            painter = QtGui.QPainter(self.search_popup)
            if not painter.isActive():
                return
                
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            popup_rect = self.search_popup.rect().adjusted(5, 5, -5, -5)
            popup_path = QtGui.QPainterPath()
            popup_path.addRoundedRect(QtCore.QRectF(popup_rect), 15, 15)
            
            # Apply transparency to popup
            popup_alpha = int(255 * (min(self.transparency_level + 15, 100) / 100.0))
            painter.fillPath(popup_path, QtGui.QColor(255, 255, 255, popup_alpha))
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, int(popup_alpha * 0.8)), 2))
            painter.drawPath(popup_path)
            painter.end()
            
        self.search_popup.paintEvent = popup_paint_event
        self.search_popup.setFixedSize(int(350 * self.size_scale), int(280 * self.size_scale))

        popup_layout = QtWidgets.QVBoxLayout(self.search_popup)
        popup_layout.setContentsMargins(15, 15, 15, 15)
        popup_layout.setSpacing(10)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(8)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search songs...")
        self.search_bar.returnPressed.connect(self.search_song)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                font-size: 13px;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 15px;
                background: rgba(255,255,255,0.8);
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid rgba(0,0,0,0.4);
                background: rgba(255,255,255,0.95);
            }
        """)

        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(int(30 * self.size_scale), int(30 * self.size_scale))
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,0,0,0.8);
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background: rgba(255,0,0,1.0); }
        """)
        close_btn.clicked.connect(self.search_popup.hide)

        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(close_btn)
        popup_layout.addLayout(header_layout)

        self.results_list = QtWidgets.QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(255,255,255,0.5);
                border-radius: 12px;
                font-size: 12px;
                color: black;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background: rgba(0,0,0,0.1);
            }
            QListWidget::item:selected {
                background: rgba(0,0,0,0.2);
            }
        """)
        self.results_list.itemClicked.connect(self.play_selected_song)
        popup_layout.addWidget(self.results_list)

    def resize_player(self, scale):
        self.size_scale = scale
        new_width = int(self.base_width * scale)
        new_height = int(self.base_height * scale)
        
        # Remove fixed size constraints temporarily
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        
        # Resize
        self.resize(new_width, new_height)
        
        # Set new fixed size
        self.setFixedSize(new_width, new_height)
        
        self.load_default_thumbnail()  # Reload default thumbnail with new scale
        self.setup_ui()  # Rebuild UI with new sizes
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if not painter.isActive():
            return
            
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        rect = self.rect().adjusted(3, 3, -3, -3)
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(rect), 20, 20)
        
        # Improved transparency calculation
        alpha = int(255 * (self.transparency_level / 100.0))
        
        # Create glassmorphic gradient
        gradient = QtGui.QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QtGui.QColor(255, 255, 255, alpha))
        gradient.setColorAt(0.5, QtGui.QColor(250, 250, 250, int(alpha * 0.9)))
        gradient.setColorAt(1, QtGui.QColor(240, 240, 240, int(alpha * 0.8)))
        
        painter.fillPath(path, gradient)
        
        # Glass border effect
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, int(alpha * 0.7)), 1.5)
        painter.setPen(pen)
        painter.drawPath(path)

        # Add subtle inner glow
        inner_rect = rect.adjusted(1, 1, -1, -1)
        inner_path = QtGui.QPainterPath()
        inner_path.addRoundedRect(QtCore.QRectF(inner_rect), 19, 19)
        inner_pen = QtGui.QPen(QtGui.QColor(255, 255, 255, int(alpha * 0.4)), 1)
        painter.setPen(inner_pen)
        painter.drawPath(inner_path)
        painter.end()

        # Handle search popup painting separately
        if hasattr(self, 'search_popup') and self.search_popup.isVisible():
            self.paint_search_popup()

    def toggle_play_pause(self):
        """Toggle between play and pause states"""
        try:
            state = self.player.get_state()
            
            if state == vlc.State.Playing:
                # Currently playing, so pause
                self.player.pause()
                self.is_playing = False
                self.is_paused = True
                QtCore.QMetaObject.invokeMethod(
                    self, "update_play_button_icon",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(bool, True)
                )
            elif state == vlc.State.Paused:
                # Currently paused, so resume
                self.player.pause()  # VLC pause() toggles pause/play
                self.is_playing = True
                self.is_paused = False
                QtCore.QMetaObject.invokeMethod(
                    self, "update_play_button_icon",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(bool, False)
                )
            else:
                # Not playing anything, play current song if available
                if self.current_song_index >= 0 and self.current_playlist:
                    self.play_song(self.current_playlist[self.current_song_index])
                
        except Exception as e:
            print(f"Toggle play/pause error: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Error toggling playback: {e}")

    def paint_search_popup(self):
        """Separate method to paint search popup to avoid painter conflicts"""
        if not hasattr(self, 'search_popup') or not self.search_popup.isVisible():
            return
            
        popup_painter = QtGui.QPainter(self.search_popup)
        if not popup_painter.isActive():
            popup_painter.end()
            return
            
        popup_painter.setRenderHint(QtGui.QPainter.Antialiasing)
        popup_rect = self.search_popup.rect().adjusted(5, 5, -5, -5)
        popup_path = QtGui.QPainterPath()
        popup_path.addRoundedRect(QtCore.QRectF(popup_rect), 15, 15)
        
        # Apply same transparency to popup
        popup_alpha = int(255 * (min(self.transparency_level + 15, 100) / 100.0))
        popup_painter.fillPath(popup_path, QtGui.QColor(255, 255, 255, popup_alpha))
        popup_painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, int(popup_alpha * 0.8)), 2))
        popup_painter.drawPath(popup_path)
        popup_painter.end()

    @QtCore.pyqtSlot(bool)
    def update_play_button_icon(self, show_play=True):
        """Update play button icon based on state - now properly decorated as slot"""
        if show_play:
            # Show play icon
            if self.icons_loaded and not self.play_icon.isNull():
                self.play_btn.setIcon(self.play_icon)
            else:
                self.play_btn.setText("▶")
        else:
            # Show pause icon
            if self.icons_loaded and not self.pause_icon.isNull():
                self.play_btn.setIcon(self.pause_icon)
            else:
                self.play_btn.setText("⏸")

    def play_current(self):
        try:
            if self.current_song_index >= 0:
                self.play_song(self.current_playlist[self.current_song_index])
        except Exception as e:
            print(f"Play current error: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Error playing song: {e}")

    def play_previous(self):
        try:
            if self.current_song_index > 0:
                self.current_song_index -= 1
                self.play_song(self.current_playlist[self.current_song_index])
        except Exception as e:
            print(f"Play previous error: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Error playing previous song: {e}")

    def play_next(self):
        try:
            if self.current_song_index < len(self.current_playlist) - 1:
                self.current_song_index += 1
                self.play_song(self.current_playlist[self.current_song_index])
            else:
                # End of playlist
                self.player.stop()
                self.is_playing = False
                self.is_paused = False
                self.song_title.setText("No Song Playing")
                self.artist_name.setText("Unknown Artist")
                self.album_art.setPixmap(self.default_pixmap)
                self.current_time.setText("0:00")
                self.total_time.setText("0:00")
                self.timeline.setValue(0)
                self.update_play_button_icon(True)  # Show play icon
        except Exception as e:
            print(f"Play next error: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Error playing next song: {e}")

    def format_time(self, ms):
        try:
            seconds = ms // 1000
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins}:{secs:02d}"
        except:
            return "0:00"

    def update_ui(self):
        try:
            state = self.player.get_state()
            if state == vlc.State.Playing:
                self.is_playing = True
                self.is_paused = False
                QtCore.QMetaObject.invokeMethod(
                    self, "update_play_button_icon",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(bool, False)
                )
                
                length = self.player.get_length()
                pos = self.player.get_time()
                
                if length > 0:
                    progress = int((pos / length) * 1000)
                    self.timeline.setValue(progress)
                    self.current_time.setText(self.format_time(pos))
                    self.total_time.setText(self.format_time(length))
            elif state == vlc.State.Paused:
                self.is_playing = False
                self.is_paused = True
                QtCore.QMetaObject.invokeMethod(
                    self, "update_play_button_icon",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(bool, True)
                )
            else:
                if state == vlc.State.Ended or state == vlc.State.Stopped:
                    self.is_playing = False
                    self.is_paused = False
                    self.current_time.setText("0:00")
                    self.timeline.setValue(0)
                    QtCore.QMetaObject.invokeMethod(
                        self, "update_play_button_icon",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(bool, True)
                    )
        except Exception as e:
            print(f"UI update error: {e}")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and not self.locked:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos and not self.locked:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(0,0,0,0.2);
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: rgba(0,0,0,0.1);
            }
        """)

        lock_action = menu.addAction("🔒 Lock Panel" if not self.locked else "🔓 Unlock Panel")
        menu.addSeparator()
        
        size_menu = menu.addMenu("📏 Size")
        increase_size = size_menu.addAction("Increase Size")
        decrease_size = size_menu.addAction("Decrease Size")
        
        menu.addSeparator()
        transparency_menu = menu.addMenu("🌫 Transparency")
        t40 = transparency_menu.addAction("40% (More Transparent)")
        t60 = transparency_menu.addAction("60%")
        t80 = transparency_menu.addAction("80%")
        t95 = transparency_menu.addAction("95% (Less Transparent)")
        
        menu.addSeparator()
        quit_action = menu.addAction("❌ Exit")

        action = menu.exec_(event.globalPos())

        if action == lock_action:
            self.locked = not self.locked
        elif action == increase_size:
            self.resize_player(min(self.size_scale + 0.1, 1.5))  # Max 150% size
        elif action == decrease_size:
            self.resize_player(max(self.size_scale - 0.1, 0.5))  # Min 50% size
        elif action == t40:
            self.transparency_level = 40
            self.update()
        elif action == t60:
            self.transparency_level = 60
            self.update()
        elif action == t80:
            self.transparency_level = 80
            self.update()
        elif action == t95:
            self.transparency_level = 95
            self.update()
        elif action == quit_action:
            QtWidgets.qApp.quit()

    def show_search_bar(self):
        pos_x = self.x() + self.width() - self.search_popup.width() + 20
        pos_y = self.y() + self.height() + 10
        self.search_popup.move(pos_x, pos_y)
        self.search_popup.show()
        self.search_bar.setFocus()

    def search_song(self):
        query = self.search_bar.text().strip()
        if not query:
            return
            
        self.results_list.clear()
        self.results_list.addItem("🔍 Searching...")

        def worker():
            try:
                yt = YTMusic()
                results = yt.search(query, filter="songs")[:8]
                self.search_results = results
                self.current_playlist = results
                self.current_song_index = -1
                
                QtCore.QMetaObject.invokeMethod(
                    self, "update_search_results",
                    QtCore.Qt.QueuedConnection
                )
            except Exception as e:
                QtCore.QMetaObject.invokeMethod(
                    self, "search_error",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, str(e))
                )

        threading.Thread(target=worker, daemon=True).start()

    @QtCore.pyqtSlot()
    def update_search_results(self):
        self.results_list.clear()
        for song in self.search_results:
            title = song.get('title', 'Unknown')
            artists = song.get('artists', [])
            artist_names = ", ".join([a.get('name', '') for a in artists]) if artists else 'Unknown Artist'
            self.results_list.addItem(f"♪ {title}\n   {artist_names}")

    @QtCore.pyqtSlot(str)
    def search_error(self, error):
        self.results_list.clear()
        self.results_list.addItem(f"❌ Error: {error}")

    def play_selected_song(self, item):
        try:
            index = self.results_list.row(item)
            if index >= len(self.search_results):
                return
                
            self.current_song_index = index
            self.play_song(self.search_results[index])
        except Exception as e:
            print(f"Play selected song error: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Error playing song: {e}")

    def play_song(self, song):
        try:
            video_id = song.get('videoId', '')
            if not video_id:
                return

            title = song.get('title', 'Unknown Song')
            artists = song.get('artists', [])
            artist_names = ", ".join([a.get('name', '') for a in artists]) if artists else 'Unknown Artist'
            
            self.song_title.setText(title)
            self.artist_name.setText(artist_names)
            self.search_popup.hide()

            self.load_song_thumbnail(song)

            def worker():
                try:
                    url = f"https://music.youtube.com/watch?v={video_id}"
                    ydl_opts = {
                        'format': 'bestaudio[ext=m4a]/bestaudio/best',
                        'quiet': True,
                        'no_warnings': True,
                        'extractaudio': True,
                        'audioformat': 'mp3',
                        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        stream_url = info.get('url')
                        
                    if stream_url:
                        self.player.stop()  # Stop any existing playback
                        media = self.instance.media_new(stream_url)
                        self.player.set_media(media)
                        self.player.play()
                        
                        # Update state
                        self.is_playing = True
                        self.is_paused = False
                        
                        # Update play button icon to pause
                        QtCore.QMetaObject.invokeMethod(
                            self, "update_play_button_icon",
                            QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(bool, False)
                        )
                        
                except Exception as e:
                    print(f"Error playing song: {e}")
                    QtCore.QMetaObject.invokeMethod(
                        self, "show_error",
                        QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(str, f"Error playing song: {e}")
                    )

            threading.Thread(target=worker, daemon=True).start()
        except Exception as e:
            print(f"Play song error: {e}")
            QtWidgets.QMessageBox.warning(self, "Error", f"Error playing song: {e}")

    @QtCore.pyqtSlot(str)
    def show_error(self, error):
        QtWidgets.QMessageBox.warning(self, "Error", error)

    def load_song_thumbnail(self, song):
        def load_thumb():
            try:
                thumbnails = song.get('thumbnails', [])
                if thumbnails:
                    thumb_url = thumbnails[-1].get('url', '')
                    if thumb_url:
                        response = requests.get(thumb_url, timeout=5)
                        img = QtGui.QImage()
                        img.loadFromData(response.content)
                        pixmap = QtGui.QPixmap(img).scaled(
                            int(85 * self.size_scale), int(85 * self.size_scale), 
                            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                        
                        QtCore.QMetaObject.invokeMethod(
                            self.album_art, "setPixmap",
                            QtCore.Qt.QueuedConnection,
                            QtCore.Q_ARG(QtGui.QPixmap, pixmap)
                        )
            except Exception as e:
                print(f"Error loading thumbnail: {e}")

        threading.Thread(target=load_thumb, daemon=True).start()

    def seek_position(self, value):
        try:
            if self.player.get_state() in [vlc.State.Playing, vlc.State.Paused]:
                length = self.player.get_length()
                if length > 0:
                    new_time = int((value / 1000) * length)
                    self.player.set_time(new_time)
        except Exception as e:
            print(f"Seek error: {e}")

if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Check for VLC installation
        vlc_paths = [
            r"C:\Program Files\VideoLAN\VLC\libvlc.dll",
            r"C:\Program Files (x86)\VideoLAN\VLC\libvlc.dll",
            r"C:\Users\Injamam khan\Documents\VLC\libvlc.dll"
        ]
        
        vlc_found = any(os.path.exists(path) for path in vlc_paths)
        if not vlc_found:
            QtWidgets.QMessageBox.critical(
                None, "VLC Not Found", 
                "VLC Media Player not found. Please install VLC from https://www.videolan.org/vlc/"
            )
            sys.exit(1)
        
        player = GlassMusicPlayer()
        player.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {e}")
        QtWidgets.QMessageBox.critical(None, "Error", f"Application failed to start: {e}")
        sys.exit(1)