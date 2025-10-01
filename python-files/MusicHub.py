import sys
import os
import json
import pygame
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QFileDialog, QSlider, QLabel, QDesktopWidget, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView

# --- КОНФІГУРАЦІЯ СТАНУ (Оригінальний шлях) ---
CONFIG_FILE = 'config.json'

def check_welcomed():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('welcomed', False)
        except json.JSONDecodeError:
            return False
    return False

def set_welcomed():
    config = {'welcomed': True}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# --- ОСНОВНИЙ КЛАС ДОДАТКУ ---

class MusicHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MusicHub 🎶 - Динамічні Ефекти')
        self.setMinimumSize(850, 650)
        
        # Pygame ініціалізація тут (Оригінальний порядок)
        pygame.mixer.init() 
        self.music_file = None
        self.is_playing = False 
        self.effects_enabled = True 
        pygame.mixer.music.set_volume(0.5)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground) 

        self.init_ui()
        
        # --- ТАЙМЕР ДЛЯ ПУЛЬСАЦІЇ ТІНІ ТА КНОПОК ---
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.animate_effects)
        self.pulse_timer_counter = 0

        self.pulse_timer.start(100) # Оновлення кожні 100 мс


    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # --- 1. Ліва Панель (Керування) ---
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        self.left_panel.setFixedWidth(200) 
        
        # ЕФЕКТ: Тінь для бічної панелі
        self.shadow_effect = QGraphicsDropShadowEffect(self.left_panel)
        self.shadow_effect.setColor(Qt.cyan)
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(0)
        self.left_panel.setGraphicsEffect(self.shadow_effect)
        
        # --- UI ЕЛЕМЕНТИ ---
        window_controls_layout = QHBoxLayout()
        self.minimize_button = QPushButton("—")
        self.minimize_button.clicked.connect(self.showMinimized)
        self.close_button = QPushButton("✕")
        self.close_button.clicked.connect(self.close)
        window_controls_layout.addWidget(self.minimize_button)
        window_controls_layout.addWidget(self.close_button)
        left_layout.addLayout(window_controls_layout)
        left_layout.addSpacing(25) 
        
        self.play_pause_button = QPushButton("▶️ Play")
        self.play_pause_button.setObjectName("play_pause_button")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        left_layout.addWidget(self.play_pause_button)
        left_layout.addSpacing(15)
        
        volume_label = QLabel("Гучність 🔊")
        volume_label.setAlignment(Qt.AlignCenter)
        volume_label.setObjectName("volume_label")
        left_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50) 
        self.volume_slider.valueChanged.connect(self.set_volume)
        left_layout.addWidget(self.volume_slider)
        left_layout.addSpacing(15)
        
        # --- КНОПКА: КЕРУВАННЯ ЕФЕКТАМИ ---
        self.effects_button = QPushButton("✨ Ефекти: УВІМК")
        self.effects_button.setObjectName("effects_button")
        self.effects_button.clicked.connect(self.toggle_effects)
        left_layout.addWidget(self.effects_button)
        left_layout.addSpacing(15)
        
        self.load_button = QPushButton("📥 Завантажити музику")
        self.load_button.setObjectName("load_button")
        self.load_button.clicked.connect(self.load_local_music)
        left_layout.addWidget(self.load_button)
        left_layout.addStretch(1)

        # --- 2. Вбудований Веб-Переглядач (YouTube Music) ---
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl("https://music.youtube.com"))
        
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.web_view)

        # --- 3. Стилізація (QSS) ---
        self.setStyleSheet(self.get_stylesheet())
        
        self.left_panel.setObjectName("left_panel")
        self.close_button.setObjectName("close_button")
        self.minimize_button.setObjectName("minimize_button")


    def toggle_effects(self):
        """Вмикає або вимикає динамічні ефекти."""
        self.effects_enabled = not self.effects_enabled
        
        if self.effects_enabled:
            self.effects_button.setText("✨ Ефекти: УВІМК")
            self.effects_button.setStyleSheet("#effects_button { background-color: #50E3C2; color: #212121; }")
            if self.is_playing:
                 self.pulse_timer_counter = 0 
        else:
            self.effects_button.setText("🚫 Ефекти: ВИМК")
            self.effects_button.setStyleSheet("#effects_button { background-color: #FF6B6B; color: white; }")
            self.reset_effects()


    def reset_effects(self):
        """Скидає всі візуальні ефекти до стандартного стану."""
        self.shadow_effect.setColor(Qt.black)
        self.shadow_effect.setBlurRadius(15)
        self.play_pause_button.setStyleSheet("")
        self.pulse_timer_counter = 0


    def animate_effects(self):
        """Змінює тінь та розмір кнопки для імітації "биття" музики."""
        if self.is_playing and self.effects_enabled:
            self.pulse_timer_counter += 1
            
            # ЕФЕКТ 1: Пульсуюча Тінь (Neon-Glow)
            radius = 15 + 20 * abs(self.pulse_timer_counter % 20 - 10) / 10 
            self.shadow_effect.setBlurRadius(radius)
            
            colors = [Qt.cyan, Qt.magenta, Qt.yellow, Qt.green]
            color_index = (self.pulse_timer_counter // 5) % len(colors)
            self.shadow_effect.setColor(colors[color_index])
            
            # ЕФЕКТ 2: Пульсуюча кнопка Play/Pause
            padding = 10 + 2 * (self.pulse_timer_counter % 10) // 5 
            self.play_pause_button.setStyleSheet(f"#play_pause_button {{ padding: {padding}px; background-color: #38C7A5; }}")
            
        elif not self.effects_enabled:
            pass
        else:
            self.reset_effects()


    def get_stylesheet(self):
        """Повертає стилі QSS."""
        return """
            MusicHub, WelcomeWindow {
                background-color: transparent; 
            }
            QWidget#left_panel { 
                background-color: rgba(30, 30, 30, 200);
                border-radius: 20px; 
                padding: 15px;
            }
            
            QLabel#volume_label { color: #50E3C2; font-size: 14px; font-weight: bold; }
            
            QSlider::groove:horizontal {
                border: 1px solid #4A90E2; 
                height: 10px; 
                background: #555555;
                margin: 2px 0;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #F1C40F; 
                border: 2px solid #FFFFFF;
                width: 22px; 
                margin: -6px 0;
                border-radius: 11px;
            }
            
            QPushButton {
                background-color: #4A90E2; color: white; border: none; padding: 10px; border-radius: 8px; font-size: 14px; font-weight: bold;
                transition: background-color 0.3s, padding 0.1s;
            }
            QPushButton:hover { background-color: #357ABD; }
            
            #close_button, #minimize_button { background-color: transparent; padding: 5px; font-size: 16px; width: 30px; height: 30px; border-radius: 15px; }
            #close_button { color: #FF6B6B; }
            #close_button:hover { background-color: rgba(255, 107, 107, 0.2); }
            #minimize_button { color: #FFE66B; }
            #minimize_button:hover { background-color: rgba(255, 230, 107, 0.2); }
            
            #play_pause_button { background-color: #50E3C2; color: #212121; }
            #play_pause_button:hover { background-color: #38C7A5; }
            #load_button { background-color: #BD10E0; }
            #load_button:hover { background-color: #8C0B9F; }
            
            /* Стилі для кнопки Ефектів */
            #effects_button { background-color: #50E3C2; color: #212121; }
            #effects_button:hover { background-color: #38C7A5; }
            
            /* Стилі для WelcomeWindow */
            QWidget#welcome_panel {
                background-color: rgba(30, 30, 30, 230);
                border-radius: 30px; 
                border: 2px solid #50E3C2;
            }
            QLabel#welcome_text {
                color: #FFFFFF;
                font-size: 20px;
                font-weight: bold;
                text-align: center;
                padding: 20px;
            }
            QPushButton#start_button {
                background-color: #50E3C2;
                color: #212121;
                padding: 15px;
                font-size: 18px;
                border-radius: 10px;
            }
        """

    # --- Методи керування музикою (без змін) ---
    def set_volume(self, value):
        volume = value / 100.0
        pygame.mixer.music.set_volume(volume)

    def toggle_play_pause(self):
        if not self.music_file:
            self.play_pause_button.setText("▶️ Play (Обери файл)")
            return
            
        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_pause_button.setText("▶️ Play")
            self.is_playing = False
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                try:
                    pygame.mixer.music.load(self.music_file)
                    pygame.mixer.music.play()
                except pygame.error:
                    return
                    
            self.play_pause_button.setText("⏸️ Pause")
            self.is_playing = True

    def load_local_music(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Обери свою музику 🎵", "", "Аудіо Файли (*.mp3 *.wav *.ogg);;Усі Файли (*)", options=options
        )
        if file_name:
            self.music_file = file_name
            if self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False
                
            self.load_button.setText(f"📥 {os.path.basename(file_name)} ✅")
            self.play_pause_button.setText("▶️ Play")
            
    # Додаємо можливість перетягувати вікно без рамки
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()


# --- КЛАС ВІКНА ПРИВІТАННЯ (без змін) ---
class WelcomeWindow(QWidget):
    def __init__(self, main_app_ref):
        super().__init__()
        self.main_app_ref = main_app_ref 
        self.setWindowTitle('Привітання')
        self.setFixedSize(400, 250)
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground) 

        self.init_ui()
        self.setStyleSheet(main_app_ref.get_stylesheet())
        self.center_on_screen()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        welcome_panel = QWidget()
        welcome_panel.setObjectName("welcome_panel")
        panel_layout = QVBoxLayout(welcome_panel)
        
        welcome_text = QLabel("👋 Ласкаво просимо до MusicHub! \n Стильного музичного хабу.")
        welcome_text.setAlignment(Qt.AlignCenter)
        welcome_text.setObjectName("welcome_text")
        
        start_button = QPushButton("Почати 🚀")
        start_button.setObjectName("start_button")
        start_button.clicked.connect(self.start_app)

        panel_layout.addWidget(welcome_text)
        panel_layout.addStretch(1)
        panel_layout.addWidget(start_button)
        
        layout.addWidget(welcome_panel)

    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_app(self):
        set_welcomed()
        self.main_app_ref.show() 
        self.close() 

# --- ТОЧКА ВХОДУ ---
if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        hub = MusicHub()

        if check_welcomed():
            hub.show()
        else:
            welcome = WelcomeWindow(hub)
            welcome.show()

        sys.exit(app.exec_())
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.quit()