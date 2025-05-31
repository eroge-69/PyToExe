import os
import sys
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pygame

class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración Pomodoro")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout()
        
        # Configuración de tiempos
        time_group = QGroupBox("Duración (minutos)")
        time_layout = QFormLayout()
        
        self.work_time = QSpinBox()
        self.work_time.setRange(1, 120)
        self.work_time.setValue(25)
        
        self.short_break = QSpinBox()
        self.short_break.setRange(1, 30)
        self.short_break.setValue(5)
        
        self.long_break = QSpinBox()
        self.long_break.setRange(1, 60)
        self.long_break.setValue(15)
        
        self.pomodoros_for_long = QSpinBox()
        self.pomodoros_for_long.setRange(1, 10)
        self.pomodoros_for_long.setValue(4)
        
        time_layout.addRow("Trabajo:", self.work_time)
        time_layout.addRow("Descanso corto:", self.short_break)
        time_layout.addRow("Descanso largo:", self.long_break)
        time_layout.addRow("Pomodoros para descanso largo:", self.pomodoros_for_long)
        time_group.setLayout(time_layout)
        
        # Configuración de música
        music_group = QGroupBox("Directorios de Música")
        music_layout = QVBoxLayout()
        
        self.work_music_btn = QPushButton("Seleccionar carpeta trabajo")
        self.break_music_btn = QPushButton("Seleccionar carpeta descanso")
        self.long_break_music_btn = QPushButton("Seleccionar carpeta descanso largo")
        
        self.work_music_label = QLabel("No seleccionado")
        self.break_music_label = QLabel("No seleccionado")
        self.long_break_music_label = QLabel("No seleccionado")
        
        music_layout.addWidget(QLabel("Trabajo:"))
        music_layout.addWidget(self.work_music_btn)
        music_layout.addWidget(self.work_music_label)
        music_layout.addWidget(QLabel("Descanso corto:"))
        music_layout.addWidget(self.break_music_btn)
        music_layout.addWidget(self.break_music_label)
        music_layout.addWidget(QLabel("Descanso largo:"))
        music_layout.addWidget(self.long_break_music_btn)
        music_layout.addWidget(self.long_break_music_label)
        music_group.setLayout(music_layout)
        
        # Botones
        self.save_btn = QPushButton("Guardar Configuración")
        
        layout.addWidget(time_group)
        layout.addWidget(music_group)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
        
        # Conexiones
        self.work_music_btn.clicked.connect(lambda: self.select_music_dir("work"))
        self.break_music_btn.clicked.connect(lambda: self.select_music_dir("break"))
        self.long_break_music_btn.clicked.connect(lambda: self.select_music_dir("long_break"))
        self.save_btn.clicked.connect(self.save_config)
        
        self.config = {}
        self.load_config()
    
    def select_music_dir(self, dir_type):
        path = QFileDialog.getExistingDirectory(self, f"Seleccionar carpeta para {dir_type}")
        if path:
            if dir_type == "work":
                self.work_music_label.setText(path)
            elif dir_type == "break":
                self.break_music_label.setText(path)
            else:
                self.long_break_music_label.setText(path)
    
    def load_config(self):
        try:
            with open('pomodoro_config.json', 'r') as f:
                self.config = json.load(f)
                self.work_time.setValue(self.config.get('work_time', 25))
                self.short_break.setValue(self.config.get('short_break', 5))
                self.long_break.setValue(self.config.get('long_break', 15))
                self.pomodoros_for_long.setValue(self.config.get('pomodoros_for_long', 4))
                
                work_path = self.config.get('work_music_path', '')
                break_path = self.config.get('break_music_path', '')
                long_break_path = self.config.get('long_break_music_path', '')
                
                self.work_music_label.setText(work_path if work_path else "No seleccionado")
                self.break_music_label.setText(break_path if break_path else "No seleccionado")
                self.long_break_music_label.setText(long_break_path if long_break_path else "No seleccionado")
        except FileNotFoundError:
            pass
    
    def save_config(self):
        self.config = {
            'work_time': self.work_time.value(),
            'short_break': self.short_break.value(),
            'long_break': self.long_break.value(),
            'pomodoros_for_long': self.pomodoros_for_long.value(),
            'work_music_path': self.work_music_label.text(),
            'break_music_path': self.break_music_label.text(),
            'long_break_music_path': self.long_break_music_label.text()
        }
        
        with open('pomodoro_config.json', 'w') as f:
            json.dump(self.config, f)
        
        self.accept()

class PomodoroTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(400, 300)
        
        # Estado inicial
        self.state = "work"  # work, short_break, long_break
        self.time_left = 0
        self.timer_running = False
        self.pomodoro_count = 0
        self.config = self.load_config()
        
        # Inicializar pygame para audio
        pygame.mixer.init()
        self.current_track = None
        
        # Configurar interfaz
        self.setup_ui()
        
        # Actualizar temporizador
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
    
    def load_config(self):
        try:
            with open('pomodoro_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'work_time': 25,
                'short_break': 5,
                'long_break': 15,
                'pomodoros_for_long': 4,
                'work_music_path': '',
                'break_music_path': '',
                'long_break_music_path': ''
            }
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Etiqueta de estado
        self.state_label = QLabel("Trabajo")
        self.state_label.setAlignment(Qt.AlignCenter)
        self.state_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        # Temporizador
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px; font-weight: bold;")
        
        # Botones
        self.start_btn = QPushButton("Iniciar")
        self.pause_btn = QPushButton("Pausar")
        self.pause_btn.setEnabled(False)
        self.reset_btn = QPushButton("Reiniciar")
        self.config_btn = QPushButton("Configuración")
        
        # Contador Pomodoro
        self.counter_label = QLabel(f"Pomodoros completados: {self.pomodoro_count}")
        self.counter_label.setAlignment(Qt.AlignCenter)
        
        # Diseño
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)
        
        layout.addWidget(self.state_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.counter_label)
        layout.addLayout(btn_layout)
        layout.addWidget(self.config_btn)
        
        central_widget.setLayout(layout)
        
        # Conexiones
        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn.clicked.connect(self.pause_timer)
        self.reset_btn.clicked.connect(self.reset_timer)
        self.config_btn.clicked.connect(self.show_config)
        
        self.reset_timer()
    
    def show_config(self):
        config_dialog = ConfigWindow(self)
        if config_dialog.exec_() == QDialog.Accepted:
            self.config = self.load_config()
            self.reset_timer()
    
    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.start_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.play_music_for_state()
    
    def pause_timer(self):
        self.timer_running = False
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        pygame.mixer.music.pause()
    
    def reset_timer(self):
        self.timer_running = False
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        
        if self.state == "work":
            self.time_left = self.config['work_time'] * 60
        elif self.state == "short_break":
            self.time_left = self.config['short_break'] * 60
        else:
            self.time_left = self.config['long_break'] * 60
            
        self.update_display()
        pygame.mixer.music.stop()
    
    def update_timer(self):
        if not self.timer_running:
            return
            
        self.time_left -= 1
        
        if self.time_left <= 0:
            self.timer_running = False
            self.switch_state()
            return
            
        self.update_display()
    
    def update_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def switch_state(self):
        pygame.mixer.music.stop()
        
        if self.state == "work":
            self.pomodoro_count += 1
            self.counter_label.setText(f"Pomodoros completados: {self.pomodoro_count}")
            
            if self.pomodoro_count % self.config['pomodoros_for_long'] == 0:
                self.state = "long_break"
                self.state_label.setText("Descanso Largo")
                self.time_left = self.config['long_break'] * 60
            else:
                self.state = "short_break"
                self.state_label.setText("Descanso Corto")
                self.time_left = self.config['short_break'] * 60
        else:
            self.state = "work"
            self.state_label.setText("Trabajo")
            self.time_left = self.config['work_time'] * 60
        
        self.play_music_for_state()
        self.update_display()
        self.timer_running = True
    
    def play_music_for_state(self):
        if self.state == "work":
            music_path = self.config['work_music_path']
        elif self.state == "short_break":
            music_path = self.config['break_music_path']
        else:
            music_path = self.config['long_break_music_path']
        
        if not music_path or not os.path.exists(music_path):
            return
        
        # Obtener lista de archivos de música
        music_files = [f for f in os.listdir(music_path) 
                      if f.endswith(('.mp3', '.wav', '.ogg'))]
        
        if not music_files:
            return
        
        # Seleccionar una canción aleatoria
        selected_track = os.path.join(music_path, music_files[0])
        
        try:
            pygame.mixer.music.load(selected_track)
            pygame.mixer.music.play(-1)  # -1 para reproducir en bucle
            self.current_track = selected_track
        except Exception as e:
            print(f"Error al reproducir música: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec_())