#!/usr/bin/env python3
"""
Galleria GNOME - Applicazione di galleria moderna per PC
Con supporto per album, cartelle, privacy e editing avanzato
"""

import sys
import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import sqlite3

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


# Configurazione dell'applicazione
APP_NAME = "THe B3St gaLlEr1 Ev3R"
APP_VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".config" / "gnome-gallery"
PRIVACY_DIR = CONFIG_DIR / "privacy"
DATABASE_PATH = CONFIG_DIR / "gallery.db"

# Estensioni supportate
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}

class DatabaseManager:
    """Gestisce il database SQLite per album e metadati"""
    
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DATABASE_PATH))
        self.init_db()
    
    def init_db(self):
        """Inizializza le tabelle del database"""
        cursor = self.conn.cursor()
        
        # Tabella album
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cover_path TEXT
            )
        ''')
        
        # Tabella media negli album
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS album_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                album_id INTEGER,
                file_path TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (album_id) REFERENCES albums (id)
            )
        ''')
        
        # Tabella configurazioni
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        self.conn.commit()
    
    def create_album(self, name: str) -> bool:
        """Crea un nuovo album"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO albums (name) VALUES (?)", (name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_albums(self) -> List[Dict]:
        """Ottiene tutti gli album"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, created_at, cover_path FROM albums ORDER BY name")
        return [{"id": row[0], "name": row[1], "created_at": row[2], "cover_path": row[3]} 
                for row in cursor.fetchall()]
    
    def add_to_album(self, album_id: int, file_path: str):
        """Aggiunge un file a un album"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO album_media (album_id, file_path) VALUES (?, ?)", 
                      (album_id, file_path))
        self.conn.commit()
    
    def get_album_media(self, album_id: int) -> List[str]:
        """Ottiene i media di un album"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT file_path FROM album_media WHERE album_id = ?", (album_id,))
        return [row[0] for row in cursor.fetchall()]
    
    def set_config(self, key: str, value: str):
        """Imposta una configurazione"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()
    
    def get_config(self, key: str, default: str = None) -> Optional[str]:
        """Ottiene una configurazione"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else default

class PrivacyManager:
    """Gestisce la cartella privacy con PIN"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        PRIVACY_DIR.mkdir(parents=True, exist_ok=True)
    
    def is_pin_set(self) -> bool:
        """Verifica se il PIN è già impostato"""
        return self.db.get_config("privacy_pin_hash") is not None
    
    def set_pin(self, pin: str):
        """Imposta il PIN (con hash)"""
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        self.db.set_config("privacy_pin_hash", pin_hash)
    
    def verify_pin(self, pin: str) -> bool:
        """Verifica il PIN"""
        stored_hash = self.db.get_config("privacy_pin_hash")
        if not stored_hash:
            return False
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        return pin_hash == stored_hash
    
    def get_privacy_files(self) -> List[Path]:
        """Ottiene i file nella cartella privacy"""
        files = []
        for ext in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            files.extend(PRIVACY_DIR.glob(f"*{ext}"))
        return sorted(files)

class ThumbnailProvider(QObject):
    """Provider per le miniature con cache"""
    
    thumbnail_ready = pyqtSignal(str, QPixmap)
    
    def __init__(self):
        super().__init__()
        self.cache_dir = CONFIG_DIR / "thumbnails"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = {}
    
    def get_thumbnail(self, file_path: str, size: int = 256) -> QPixmap:
        """Ottiene o genera una miniatura"""
        cache_key = f"{file_path}_{size}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Genera miniatura
        pixmap = QPixmap()
        if Path(file_path).suffix.lower() in IMAGE_EXTENSIONS:
            pixmap.load(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, 
                                     Qt.TransformationMode.SmoothTransformation)
        else:
            # Icona per video
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(50, 50, 50))
        
        self.cache[cache_key] = pixmap
        return pixmap

class MediaViewer(QDialog):
    """Visualizzatore/Editor di media avanzato"""
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.is_video = Path(file_path).suffix.lower() in VIDEO_EXTENSIONS
        self.setup_ui()
        self.load_media()
    
    def setup_ui(self):
        """Configura l'interfaccia del visualizzatore"""
        self.setWindowTitle(f"Visualizzatore - {Path(self.file_path).name}")
        self.setMinimumSize(900, 700)
        self.showMaximized()
        
        # Stile moderno
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1a1a1a, stop:1 #2d2d2d);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px 15px;
                color: white;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a, stop:1 #4a4a4a);
            }
            QPushButton:pressed {
                background: #2a2a2a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Toolbar moderna
        toolbar = QHBoxLayout()
        
        if not self.is_video:
            # Pulsanti per immagini
            self.btn_rotate_left = QPushButton("🔄")
            self.btn_rotate_right = QPushButton("🔄")
            self.btn_zoom_in = QPushButton("🔍+")
            self.btn_zoom_out = QPushButton("🔍-")
            self.btn_fit = QPushButton("📐 Adatta")
            self.btn_edit = QPushButton("✏️ Modifica")
            
            toolbar.addWidget(self.btn_rotate_left)
            toolbar.addWidget(self.btn_rotate_right)
            toolbar.addWidget(self.btn_zoom_in)
            toolbar.addWidget(self.btn_zoom_out)
            toolbar.addWidget(self.btn_fit)
            toolbar.addWidget(self.btn_edit)
        
        self.btn_fullscreen = QPushButton("🔳 Schermo intero")
        self.btn_close = QPushButton("❌ Chiudi")
        
        toolbar.addStretch()
        toolbar.addWidget(self.btn_fullscreen)
        toolbar.addWidget(self.btn_close)
        
        layout.addLayout(toolbar)
        
        # Area di visualizzazione
        if self.is_video:
            self.setup_video_player()
        else:
            self.setup_image_viewer()
        
        layout.addWidget(self.media_widget)
        
        # Connetti segnali
        if not self.is_video:
            self.btn_rotate_left.clicked.connect(lambda: self.rotate_image(-90))
            self.btn_rotate_right.clicked.connect(lambda: self.rotate_image(90))
            self.btn_zoom_in.clicked.connect(self.zoom_in)
            self.btn_zoom_out.clicked.connect(self.zoom_out)
            self.btn_fit.clicked.connect(self.fit_to_window)
            self.btn_edit.clicked.connect(self.open_editor)
        
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        self.btn_close.clicked.connect(self.close)
    
    def setup_image_viewer(self):
        """Configura il visualizzatore di immagini"""
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.media_widget = self.scroll_area
        self.zoom_factor = 1.0
    
    def setup_video_player(self):
        """Configura il player video - VERSIONE CORRETTA"""
        self.media_widget = QWidget()
        self.media_widget.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self.media_widget)
        
        # Widget video con bordi arrotondati
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background-color: #000000;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.video_widget)
        
        # Controlli video moderni
        controls_container = QWidget()
        controls_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a, stop:1 #2a2a2a);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        controls_layout = QHBoxLayout(controls_container)
        
        # Pulsanti di controllo
        self.btn_play = QPushButton("▶️")
        self.btn_pause = QPushButton("⏸️")
        self.btn_stop = QPushButton("⏹️")
        
        for btn in [self.btn_play, self.btn_pause, self.btn_stop]:
            btn.setFixedSize(50, 40)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    border-radius: 20px;
                    min-width: 40px;
                }
            """)
        
        # Slider posizione
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #555;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #3584e4;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -5px 0;
            }
        """)
        
        # Label tempo
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: white; font-weight: bold;")
        
        # Slider volume
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setStyleSheet(self.position_slider.styleSheet())
        
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("color: white; font-size: 16px;")
        
        # Aggiungi controlli
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(QLabel(""))  # Spacer
        controls_layout.addWidget(self.position_slider)
        controls_layout.addWidget(self.time_label)
        controls_layout.addStretch()
        controls_layout.addWidget(volume_label)
        controls_layout.addWidget(self.volume_slider)
        
        layout.addWidget(controls_container)
        
        # Inizializza media player CORRETTO
        try:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
            self.media_player.setVideoOutput(self.video_widget)
            
            # Connetti segnali
            self.btn_play.clicked.connect(self.play_video)
            self.btn_pause.clicked.connect(self.pause_video)
            self.btn_stop.clicked.connect(self.stop_video)
            self.volume_slider.valueChanged.connect(self.set_volume)
            self.position_slider.sliderMoved.connect(self.set_position)
            
            # Segnali del media player
            self.media_player.positionChanged.connect(self.position_changed)
            self.media_player.durationChanged.connect(self.duration_changed)
            self.media_player.playbackStateChanged.connect(self.state_changed)
            
        except Exception as e:
            print(f"Errore inizializzazione media player: {e}")
    
    def play_video(self):
        """Avvia la riproduzione"""
        if self.media_player:
            self.media_player.play()
    
    def pause_video(self):
        """Mette in pausa"""
        if self.media_player:
            self.media_player.pause()
    
    def stop_video(self):
        """Ferma la riproduzione"""
        if self.media_player:
            self.media_player.stop()
    
    def set_volume(self, volume):
        """Imposta il volume"""
        if self.audio_output:
            self.audio_output.setVolume(volume / 100.0)
    
    def set_position(self, position):
        """Imposta la posizione"""
        if self.media_player:
            self.media_player.setPosition(position)
    
    def position_changed(self, position):
        """Aggiorna la posizione del slider"""
        self.position_slider.blockSignals(True)
        self.position_slider.setValue(position)
        self.position_slider.blockSignals(False)
        
        # Aggiorna label tempo
        current_time = self.format_time(position)
        total_time = self.format_time(self.media_player.duration())
        self.time_label.setText(f"{current_time} / {total_time}")
    
    def duration_changed(self, duration):
        """Aggiorna la durata"""
        self.position_slider.setMaximum(duration)
    
    def state_changed(self, state):
        """Gestisce il cambio di stato"""
        pass
    
    def format_time(self, ms):
        """Formatta il tempo in mm:ss"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def load_media(self):
        """Carica il media"""
        if self.is_video and self.media_player:
            url = QUrl.fromLocalFile(os.path.abspath(self.file_path))
            self.media_player.setSource(url)
        elif not self.is_video:
            self.pixmap = QPixmap(self.file_path)
            if self.pixmap.isNull():
                QMessageBox.warning(self, "Errore", "Impossibile caricare l'immagine")
                return
            self.display_image()
    
    def toggle_fullscreen(self):
        """Attiva/disattiva schermo intero"""
        if self.isFullScreen():
            self.showNormal()
            self.btn_fullscreen.setText("🔳 Schermo intero")
        else:
            self.showFullScreen()
            self.btn_fullscreen.setText("🔳 Finestra")
    
    def display_image(self):
        """Visualizza l'immagine"""
        if hasattr(self, 'pixmap') and not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(
                self.pixmap.size() * self.zoom_factor,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
    
    def rotate_image(self, angle: int):
        """Ruota l'immagine"""
        if hasattr(self, 'pixmap'):
            transform = QTransform().rotate(angle)
            self.pixmap = self.pixmap.transformed(transform)
            self.display_image()
    
    def zoom_in(self):
        """Ingrandisce l'immagine"""
        self.zoom_factor *= 1.25
        self.display_image()
    
    def zoom_out(self):
        """Rimpicciolisce l'immagine"""
        self.zoom_factor /= 1.25
        self.display_image()
    
    def fit_to_window(self):
        """Adatta l'immagine alla finestra"""
        if hasattr(self, 'pixmap'):
            scroll_size = self.scroll_area.size()
            self.zoom_factor = min(
                scroll_size.width() / self.pixmap.width(),
                scroll_size.height() / self.pixmap.height()
            )
            self.display_image()
    
    def open_editor(self):
        """Apre l'editor di immagini"""
        editor = ImageEditor(self.file_path, self)
        editor.exec()

class ImageEditor(QDialog):
    """Editor di immagini avanzato"""
    
    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.original_pixmap = QPixmap(file_path)
        self.current_pixmap = self.original_pixmap.copy()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia dell'editor"""
        self.setWindowTitle(f"Editor - {Path(self.file_path).name}")
        self.setMinimumSize(1000, 700)
        
        layout = QHBoxLayout(self)
        
        # Pannello strumenti
        tools_panel = QVBoxLayout()
        tools_widget = QWidget()
        tools_widget.setFixedWidth(200)
        tools_widget.setLayout(tools_panel)
        
        # Controlli luminosità/contrasto
        tools_panel.addWidget(QLabel("Luminosità:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        tools_panel.addWidget(self.brightness_slider)
        
        tools_panel.addWidget(QLabel("Contrasto:"))
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        tools_panel.addWidget(self.contrast_slider)
        
        # Filtri
        tools_panel.addWidget(QLabel("Filtri:"))
        self.btn_grayscale = QPushButton("Scala di grigi")
        self.btn_sepia = QPushButton("Seppia")
        self.btn_blur = QPushButton("Sfocatura")
        self.btn_sharpen = QPushButton("Nitidezza")
        
        tools_panel.addWidget(self.btn_grayscale)
        tools_panel.addWidget(self.btn_sepia)
        tools_panel.addWidget(self.btn_blur)
        tools_panel.addWidget(self.btn_sharpen)
        
        tools_panel.addStretch()
        
        # Pulsanti azione
        self.btn_reset = QPushButton("Ripristina")
        self.btn_save = QPushButton("Salva")
        self.btn_save_as = QPushButton("Salva come...")
        
        tools_panel.addWidget(self.btn_reset)
        tools_panel.addWidget(self.btn_save)
        tools_panel.addWidget(self.btn_save_as)
        
        layout.addWidget(tools_widget)
        
        # Area di anteprima
        self.scroll_area = QScrollArea()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        
        layout.addWidget(self.scroll_area)
        
        # Connetti segnali
        self.brightness_slider.valueChanged.connect(self.apply_adjustments)
        self.contrast_slider.valueChanged.connect(self.apply_adjustments)
        self.btn_grayscale.clicked.connect(self.apply_grayscale)
        self.btn_reset.clicked.connect(self.reset_image)
        self.btn_save.clicked.connect(self.save_image)
        self.btn_save_as.clicked.connect(self.save_image_as)
        
        self.update_preview()
    
    def apply_adjustments(self):
        """Applica regolazioni di luminosità e contrasto"""
        brightness = self.brightness_slider.value()
        contrast = self.contrast_slider.value()
        
        # Simulazione semplice (in una versione completa useresti PIL/OpenCV)
        self.current_pixmap = self.original_pixmap.copy()
        self.update_preview()
    
    def apply_grayscale(self):
        """Applica filtro scala di grigi"""
        # Conversione semplificata
        image = self.current_pixmap.toImage()
        for y in range(image.height()):
            for x in range(image.width()):
                pixel = image.pixel(x, y)
                gray = qGray(pixel)
                image.setPixel(x, y, qRgb(gray, gray, gray))
        
        self.current_pixmap = QPixmap.fromImage(image)
        self.update_preview()
    
    def update_preview(self):
        """Aggiorna l'anteprima"""
        if not self.current_pixmap.isNull():
            scaled = self.current_pixmap.scaled(
                800, 600, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
    
    def reset_image(self):
        """Ripristina l'immagine originale"""
        self.current_pixmap = self.original_pixmap.copy()
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.update_preview()
    
    def save_image(self):
        """Salva l'immagine"""
        self.current_pixmap.save(self.file_path)
        QMessageBox.information(self, "Salvato", "Immagine salvata con successo!")
    
    def save_image_as(self):
        """Salva l'immagine con un nuovo nome"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salva immagine", "", "Immagini (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.current_pixmap.save(file_path)
            QMessageBox.information(self, "Salvato", "Immagine salvata con successo!")

class PinDialog(QDialog):
    """Dialog per inserimento PIN"""
    
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.pin = ""
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(message))
        
        self.pin_edit = QLineEdit()
        self.pin_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_edit.setMaxLength(10)
        layout.addWidget(self.pin_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_pin(self) -> str:
        """Ottiene il PIN inserito"""
        return self.pin_edit.text()

class MediaGrid(QWidget):
    """Grid per visualizzare i media con miniature"""
    
    media_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.files = []
        self.thumbnail_provider = ThumbnailProvider()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia del grid"""
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
    
    def set_files(self, files: List[str]):
        """Imposta i file da visualizzare"""
        self.files = files
        self.refresh_grid()
    
    # CORREZIONE 1: Aggiungere questo metodo alla classe MediaGrid (intorno alla riga 500)
    def refresh_grid(self):
        """Aggiorna il grid con le miniature"""
        # Pulisci il layout esistente
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
    
        # Aggiungi le nuove miniature
        cols = 4
        for i, file_path in enumerate(self.files):
            row, col = divmod(i, cols)
        
            # Container per miniatura
            container = QWidget()
            container.setObjectName("media_container")
            container.setFixedSize(200, 180)
            container_layout = QVBoxLayout(container)
        
            # Pulsante con miniatura
            btn = QPushButton()
            btn.setFixedSize(180, 140)
            btn.setObjectName("media_button")
        
            # FIX: Usa mouseReleaseEvent per evitare doppio click
            def make_click_handler(path):
                def mouse_release_handler(event):
                    if event.button() == Qt.MouseButton.LeftButton:
                        self.media_selected.emit(path)
                return mouse_release_handler
        
            btn.mouseReleaseEvent = make_click_handler(file_path)
        
            # Carica miniatura
            thumbnail = self.thumbnail_provider.get_thumbnail(file_path, 180)
            btn.setIcon(QIcon(thumbnail))
            btn.setIconSize(QSize(170, 130))
        
            container_layout.addWidget(btn)
        
            # Nome file
            name_label = QLabel(Path(file_path).name)
            name_label.setObjectName("media_name")
            name_label.setWordWrap(True)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(name_label)
        
            self.grid_layout.addWidget(container, row, col)

class AlbumSelectionDialog(QDialog):
    """Dialog per selezionare album o privacy durante l'importazione"""
    
    def __init__(self, albums: List[Dict], parent=None):
        super().__init__(parent)
        self.albums = albums
        self.selected_album_id = None
        self.save_to_privacy = False
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia del dialog"""
        self.setWindowTitle("Dove salvare i file?")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 12px;
            }
            QLabel {
                color: #2e3436;
                font-size: 14px;
            }
            QRadioButton {
                color: #2e3436;
                font-size: 13px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #c1c1c1;
                border-radius: 8px;
                background: white;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #3584e4;
                border-radius: 8px;
                background: #3584e4;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3584e4, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
            }
            QPushButton#cancelBtn {
                background: #f8f9fa;
                color: #6c757d;
                border: 1px solid #e9ecef;
            }
            QPushButton#cancelBtn:hover {
                background: #e9ecef;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titolo
        title = QLabel("Seleziona dove salvare i file importati:")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2e3436; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Gruppo radio button
        self.radio_group = QButtonGroup()
        
        # Scroll area per album
        if self.albums:
            scroll_area = QScrollArea()
            scroll_area.setFixedHeight(150)
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    background: #fafafa;
                }
            """)
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            for album in self.albums:
                radio = QRadioButton(f"📂 {album['name']}")
                radio.album_id = album['id']
                self.radio_group.addButton(radio)
                scroll_layout.addWidget(radio)
            
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)
        
        # Opzione Privacy (sempre disponibile)
        privacy_radio = QRadioButton("🔒 Cartella Privacy")
        privacy_radio.album_id = -1  # ID speciale per privacy
        self.radio_group.addButton(privacy_radio)
        layout.addWidget(privacy_radio)
        
        # Se non ci sono album, seleziona privacy di default
        if not self.albums:
            privacy_radio.setChecked(True)
            info_label = QLabel("💡 Non hai ancora album. Crea un album per organizzare meglio i tuoi file!")
            info_label.setStyleSheet("color: #6c757d; font-style: italic; padding: 10px; background: #f8f9fa; border-radius: 6px;")
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Annulla")
        cancel_btn.setObjectName("cancelBtn")
        ok_btn = QPushButton("Salva qui")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        
        layout.addLayout(buttons_layout)
        
        # Connetti segnali
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self.accept_selection)
    
    def accept_selection(self):
        """Conferma la selezione"""
        selected_button = self.radio_group.checkedButton()
        if selected_button:
            if selected_button.album_id == -1:
                self.save_to_privacy = True
            else:
                self.selected_album_id = selected_button.album_id
            self.accept()
        else:
            QMessageBox.warning(self, "Selezione richiesta", "Seleziona dove salvare i file!")

def get_improved_media_grid_style():
    """Restituisce il CSS migliorato per MediaGrid"""
    return """
        QScrollArea {
            border: none;
            background-color: #fafafa;
        }
        
        QWidget#media_container {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 12px;
            margin: 5px;
        }
        
        QWidget#media_container:hover {
            border-color: #3584e4;
            background: #f8f9fa;
        }
        
        QPushButton#media_button {
            border: none;
            border-radius: 8px;
            background: transparent;
        }
        
        QLabel#media_name {
            color: #2e3436;
            font-weight: 500;
            font-size: 12px;
            padding: 5px;
        }
    """

class AlbumGridView(QWidget):
    """Vista a griglia per gli album"""
    
    album_selected = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Configura l'interfaccia della griglia album"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("I tuoi Album")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2e3436;
                padding: 10px 0;
            }
        """)
        
        self.btn_new_album = QPushButton("➕ Nuovo Album")
        self.btn_new_album.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3584e4, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
            }
        """)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_new_album)
        
        layout.addLayout(header)
        
        # Scroll area per album
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.albums_widget = QWidget()
        self.albums_layout = QGridLayout(self.albums_widget)
        self.albums_layout.setSpacing(20)
        
        self.scroll_area.setWidget(self.albums_widget)
        layout.addWidget(self.scroll_area)
        
        # Connetti segnale
        self.btn_new_album.clicked.connect(self.create_album)
    
    def refresh_albums(self):
        """Aggiorna la vista degli album"""
        # Pulisci layout esistente
        for i in reversed(range(self.albums_layout.count())):
            child = self.albums_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        albums = self.db.get_albums()
        cols = 3
        
        for i, album in enumerate(albums):
            row, col = divmod(i, cols)
            album_card = self.create_album_card(album)
            self.albums_layout.addWidget(album_card, row, col)

    # CORREZIONE 2: Sistemare il metodo create_album_card nella classe AlbumGridView (intorno alla riga 900)
    def create_album_card(self, album):
        """Crea una card per l'album"""
        card = QWidget()
        card.setFixedSize(250, 200)
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: 1px solid #e9ecef;
                border-radius: 12px;
            }
            QWidget:hover {
                border-color: #3584e4;
            }
        """)
    
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
    
        # Immagine di copertina o icona
        cover_label = QLabel()
        cover_label.setFixedSize(200, 120)
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        if album.get('cover_path') and Path(album['cover_path']).exists():
            pixmap = QPixmap(album['cover_path'])
            scaled_pixmap = pixmap.scaled(200, 120, Qt.AspectRatioMode.KeepAspectRatio, 
                                        Qt.TransformationMode.SmoothTransformation)
            cover_label.setPixmap(scaled_pixmap)
        else:
            cover_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
                    border-radius: 8px;
                    color: #6c757d;
                    font-size: 48px;
                }
            """)
            cover_label.setText("📷")
    
        layout.addWidget(cover_label)
    
        # Nome album
        name_label = QLabel(album['name'])
        name_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2e3436;
                padding: 0 10px;
            }
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
    
        # Info album
        media_count = len(self.db.get_album_media(album['id']))
        info_label = QLabel(f"{media_count} elementi")
        info_label.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font-size: 12px;
                padding: 0 10px;
            }
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
    
        # FIX: Usa mouseReleaseEvent invece di mousePressEvent per evitare doppio click
        def mouse_release_handler(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.album_selected.emit(album)
        
        card.mouseReleaseEvent = mouse_release_handler
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        
        return card
    
    # CORREZIONE 3: Spostare il metodo create_album dentro la classe AlbumGridView (corretto indentamento)
    def create_album(self):
        """Crea un nuovo album"""
        dialog = QInputDialog(self)
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        dialog.setWindowTitle("Nuovo Album")
        dialog.setLabelText("Nome dell'album:")
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3584e4;
            }
        """)
    
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.textValue().strip()
            if name:
                if self.db.create_album(name):
                    self.refresh_albums()
                    QMessageBox.information(self, "Successo", f"Album '{name}' creato!")
                else:
                    QMessageBox.warning(self, "Errore", "Album già esistente!")


class GalleryApp(QMainWindow):
    """Applicazione principale della galleria"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.privacy_manager = PrivacyManager(self.db)
        self.privacy_unlocked = False
        self.setup_ui()
        self.setStyleSheet(get_improved_media_grid_style())
        self.load_default_view()
    
    def setup_ui(self):
        """Configura l'interfaccia principale"""
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(1200, 800)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principale
        main_layout = QHBoxLayout(central_widget)
        
        # Sidebar
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar, 0)
        self.sidebar.setObjectName("sidebar")
        
        # Area principale
        self.main_area = QStackedWidget()
        main_layout.addWidget(self.main_area, 1)
        
        # Media grid
        self.media_grid = MediaGrid()
        self.media_grid.media_selected.connect(self.open_media_viewer)
        self.main_area.addWidget(self.media_grid)
        
        # Menubar
        self.setup_menubar()
        
        # Statusbar
        self.statusBar().showMessage("Pronto")
    
    def setup_sidebar(self):
        """Configura la sidebar"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("QWidget { background-color: #f6f5f4; }")
        
        layout = QVBoxLayout(self.sidebar)
        
        # Titolo
        title = QLabel("Galleria")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Lista navigazione
        self.nav_list = QListWidget()
        self.nav_list.setFrameStyle(QFrame.Shape.NoFrame)
        
        nav_items = [
            ("📷 Tutte le foto", "all_photos"),
            ("🎥 Tutti i video", "all_videos"),
            ("📁 Cartelle", "folders"),
            ("📂 Album", "albums"),
            ("🔒 Privacy", "privacy")
        ]
        
        for text, data in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, data)
            self.nav_list.addItem(item)
        
        self.nav_list.currentItemChanged.connect(self.nav_changed)
        layout.addWidget(self.nav_list)
        
        layout.addStretch()
    
    def setup_menubar(self):
        """Configura la barra dei menu"""
        menubar = self.menuBar()
        
        # Menu File
        file_menu = menubar.addMenu("File")
        
        import_action = QAction("Importa...", self)
        import_action.triggered.connect(self.import_files)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Esci", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Album
        album_menu = menubar.addMenu("Album")
        
        new_album_action = QAction("Nuovo album...", self)
        new_album_action.triggered.connect(self.create_new_album)
        album_menu.addAction(new_album_action)
        
        # Menu Vista
        view_menu = menubar.addMenu("Vista")
        
        refresh_action = QAction("Aggiorna", self)
        refresh_action.triggered.connect(self.refresh_current_view)
        view_menu.addAction(refresh_action)
    
    def nav_changed(self, current, previous):
        """Gestisce il cambio di navigazione"""
        if not current:
            return
        
        nav_type = current.data(Qt.ItemDataRole.UserRole)
        
        if nav_type == "all_photos":
            self.show_all_photos()
        elif nav_type == "all_videos":
            self.show_all_videos()
        elif nav_type == "folders":
            self.show_folders()
        elif nav_type == "albums":
            self.show_albums_improved()
        elif nav_type == "privacy":
            self.show_privacy()
    
    def show_all_photos(self):
        """Mostra tutte le foto"""
        photos = []
        for folder in [Path.home() / "Pictures", Path.home() / "Desktop"]:
            if folder.exists():
                for ext in IMAGE_EXTENSIONS:
                    photos.extend([str(f) for f in folder.rglob(f"*{ext}")])
        
        self.media_grid.set_files(photos)
        self.statusBar().showMessage(f"{len(photos)} foto trovate")
    
    def show_all_videos(self):
        """Mostra tutti i video"""
        videos = []
        for folder in [Path.home() / "Videos", Path.home() / "Desktop"]:
            if folder.exists():
                for ext in VIDEO_EXTENSIONS:
                    videos.extend([str(f) for f in folder.rglob(f"*{ext}")])
        
        self.media_grid.set_files(videos)
        self.statusBar().showMessage(f"{len(videos)} video trovati")
    
    def show_folders(self):
        """Mostra la vista cartelle"""
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella")
        if folder:
            files = []
            folder_path = Path(folder)
            for ext in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
                files.extend([str(f) for f in folder_path.glob(f"*{ext}")])
            
            self.media_grid.set_files(files)
            self.statusBar().showMessage(f"{len(files)} file in {folder}")
    
    def show_albums_improved(self):
        """Mostra gli album in vista griglia - VERSIONE MIGLIORATA"""
        # Rimuovi widget esistente se presente
        for i in range(self.main_area.count()):
            if isinstance(self.main_area.widget(i), AlbumGridView):
                self.main_area.removeWidget(self.main_area.widget(i))
        
        # Crea vista album
        self.album_view = AlbumGridView(self.db)
        self.album_view.album_selected.connect(self.open_album)
        self.album_view.refresh_albums()
        
        self.main_area.addWidget(self.album_view)
        self.main_area.setCurrentWidget(self.album_view)
        
        albums_count = len(self.db.get_albums())
        self.statusBar().showMessage(f"{albums_count} album trovati")

    def open_album(self, album):
        """Apre un album specifico - NUOVO METODO"""
        files = self.db.get_album_media(album["id"])
        if files:
            self.media_grid.set_files(files)
            self.main_area.setCurrentWidget(self.media_grid)
            self.statusBar().showMessage(f"Album: {album['name']} ({len(files)} file)")
        else:
            QMessageBox.information(self, "Album vuoto", 
                                  f"L'album '{album['name']}' non contiene ancora file.")
    
    def show_privacy(self):
        """Mostra la cartella privacy"""
        if not self.privacy_unlocked:
            if not self.privacy_manager.is_pin_set():
                # Prima volta - imposta PIN
                dialog = PinDialog("Imposta PIN", "Imposta un PIN per la cartella privacy:")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    pin = dialog.get_pin()
                    if pin:
                        self.privacy_manager.set_pin(pin)
                        self.privacy_unlocked = True
                        QMessageBox.information(self, "PIN impostato", "PIN impostato con successo!")
                    else:
                        return
                else:
                    return
            else:
                # Verifica PIN
                dialog = PinDialog("Inserisci PIN", "Inserisci il PIN per accedere alla cartella privacy:")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    pin = dialog.get_pin()
                    if self.privacy_manager.verify_pin(pin):
                        self.privacy_unlocked = True
                    else:
                        QMessageBox.warning(self, "PIN errato", "PIN non corretto!")
                        return
                else:
                    return
        
        # Mostra file privacy
        files = [str(f) for f in self.privacy_manager.get_privacy_files()]
        self.media_grid.set_files(files)
        self.statusBar().showMessage(f"Privacy: {len(files)} file")
    
    def load_default_view(self):
        """Carica la vista predefinita"""
        self.nav_list.setCurrentRow(0)  # Seleziona "Tutte le foto"
    
    def open_media_viewer(self, file_path: str):
        """Apre il visualizzatore di media"""
        viewer = MediaViewer(file_path, self)
        viewer.exec()
    
    # CORREZIONE 4: Aggiungere questo metodo alla classe GalleryApp (intorno alla riga 1400)
    def import_files(self):
        """Importa file nella libreria con selezione album/privacy"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Importa file", "",
            "Media (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.mp4 *.avi *.mkv *.mov)")
    
        if files:
            albums = self.db.get_albums()
        
            # Mostra dialog di selezione
            dialog = AlbumSelectionDialog(albums, self)
        
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if dialog.save_to_privacy:
                    # Salva in privacy
                    if not self.privacy_unlocked:
                        self.show_privacy()
                        if not self.privacy_unlocked:
                            return
                    
                    # Copia file nella cartella privacy
                    for file_path in files: 
                        dest_path = PRIVACY_DIR / Path(file_path).name
                        shutil.copy2(file_path, dest_path)
                
                    QMessageBox.information(self, "Importato", 
                        f"✓ {len(files)} file importati nella cartella Privacy!")
                    
                elif dialog.selected_album_id:
                    # Salva nell'album selezionato
                    for file_path in files:
                        self.db.add_to_album(dialog.selected_album_id, file_path)
                    
                    # Trova nome album per messaggio
                    album_name = next((a['name'] for a in albums if a['id'] == dialog.selected_album_id), "Album")
                    
                    QMessageBox.information(self, "Importato", 
                        f"✓ {len(files)} file importati nell'album '{album_name}'!")
    
    def create_new_album(self):
        """Crea un nuovo album"""
        name, ok = QInputDialog.getText(self, "Nuovo album", "Nome album:")
        if ok and name:
            if self.db.create_album(name):
                QMessageBox.information(self, "Album creato", f"Album '{name}' creato con successo!")
            else:
                QMessageBox.warning(self, "Errore", "Album già esistente o errore nella creazione!")
    
    def refresh_current_view(self):
        """Aggiorna la vista corrente"""
        current_item = self.nav_list.currentItem()
        if current_item:
            self.nav_changed(current_item, None)
    
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        self.db.conn.close()
        event.accept()


def apply_modern_gnome_style(app: QApplication):
    """Applica lo stile GNOME moderno - Solo tema chiaro"""
    
    style = """
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f8f9fa);
    }
    
    QWidget {
        font-family: 'SF Pro Display', 'Segoe UI', 'Inter', 'Cantarell', sans-serif;
        color: #2e3436;
        font-size: 13px;
    }
    
    /* Sidebar moderna */
    QWidget#sidebar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ffffff, stop:1 #fdfdfd);
        border-right: 1px solid #e1e5e9;
    }
    
    QListWidget {
        background: transparent;
        border: none;
        outline: none;
        padding: 12px;
    }
    
    QListWidget::item {
        padding: 16px 20px;
        border-radius: 12px;
        margin: 4px 0;
        font-size: 14px;
        font-weight: 500;
        color: #495057;
    }
    
    QListWidget::item:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #3584e4, stop:1 #2563eb);
        color: white;
        font-weight: 600;
    }
    
    QListWidget::item:hover:!selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f1f3f4, stop:1 #e8eaed);
        color: #2e3436;
    }
    
    /* Media Grid migliorato */
    QScrollArea {
        border: none;
        background-color: #fafafa;
    }
    
    QWidget#media_container {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #fefefe);
        border: 1px solid #e9ecef;
        border-radius: 16px;
        margin: 8px;
    }
    
    QWidget#media_container:hover {
        border-color: #3584e4;
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f8f9fa);
        box-shadow: 0 4px 12px rgba(53, 132, 228, 0.12);
    }
    
    QPushButton#media_button {
        border: none;
        border-radius: 12px;
        background: transparent;
    }
    
    QPushButton#media_button:hover {
        background: rgba(53, 132, 228, 0.05);
    }
    
    QLabel#media_name {
        color: #2e3436;
        font-weight: 500;
        font-size: 12px;
        padding: 8px;
    }
    
    /* Pulsanti moderni */
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #f8f9fa);
        border: 1.5px solid #e1e5e9;
        border-radius: 10px;
        padding: 12px 18px;
        font-weight: 500;
        font-size: 13px;
        color: #495057;
    }
    
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #f8f9fa, stop:1 #e9ecef);
        border-color: #3584e4;
        color: #2e3436;
    }
    
    QPushButton:pressed {
        background: #e9ecef;
        border-color: #2563eb;
    }
    
    /* Menu moderni */
    QMenuBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #ffffff, stop:1 #fdfdfd);
        border-bottom: 1px solid #e1e5e9;
        padding: 6px;
    }
    
    QMenuBar::item {
        padding: 10px 18px;
        border-radius: 8px;
        margin: 2px;
        color: #495057;
        font-weight: 500;
    }
    
    QMenuBar::item:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #3584e4, stop:1 #2563eb);
        color: white;
    }
    
    QMenu {
        background: white;
        border: 1px solid #e1e5e9;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    QMenu::item {
        padding: 12px 18px;
        border-radius: 8px;
        color: #495057;
        font-weight: 500;
    }
    
    QMenu::item:selected {
        background: #3584e4;
        color: white;
    }
    
    /* Scrollbar elegante */
    QScrollBar:vertical {
        background: #f8f9fa;
        width: 10px;
        border-radius: 5px;
        margin: 0;
    }
    
    QScrollBar::handle:vertical {
        background: #ced4da;
        border-radius: 5px;
        min-height: 25px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #adb5bd;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    /* Status bar elegante */
    QStatusBar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #fdfdfd, stop:1 #f8f9fa);
        border-top: 1px solid #e1e5e9;
        color: #6c757d;
        font-weight: 500;
        padding: 8px;
    }
    
    /* Input fields */
    QLineEdit {
        background: white;
        border: 2px solid #e1e5e9;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 14px;
        color: #2e3436;
    }
    
    QLineEdit:focus {
        border-color: #3584e4;
        box-shadow: 0 0 0 3px rgba(53, 132, 228, 0.1);
    }
    """
    
    app.setStyleSheet(style)


def main():
    """Funzione principale"""
    app = QApplication(sys.argv)
    
    # Configura l'applicazione
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("GNOME Gallery")
    
    # Applica lo stile GNOME
    apply_modern_gnome_style(app)
    
    # Crea e mostra la finestra principale
    window = GalleryApp()
    window.show()
    
    # Avvia il loop degli eventi
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
