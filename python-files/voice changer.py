import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSlider, QLabel, QPushButton, QComboBox, QGroupBox, QCheckBox,
    QDoubleSpinBox, QFileDialog, QStatusBar, QSplitter
)
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
import pyaudio
import wave
import os
from scipy.signal import butter, lfilter
import math
import threading
import time

class VoiceChanger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VoiceMaster Pro - Ultimate Voice Changer")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QGroupBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QLabel {
                color: #ecf0f1;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #34495e;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ecf0f1;
                border: 1px solid #777;
                width: 18px;
                margin: -4px 0;
                border-radius: 9px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QComboBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 3px;
            }
            QCheckBox {
                color: #ecf0f1;
            }
            QDoubleSpinBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #3498db;
                border-radius: 5px;
                padding: 3px;
            }
        """)
        
        # Audio parameters
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.is_playing = False
        self.is_processing = False
        self.output_frames = []
        
        # Voice effect parameters
        self.pitch_shift = 0.0
        self.formant_shift = 1.0
        self.distortion_level = 0.0
        self.reverb_level = 0.0
        self.robot_level = 0.0
        self.volume = 1.0
        self.echo_delay = 0.0
        self.echo_decay = 0.0
        self.eq_low = 1.0
        self.eq_mid = 1.0
        self.eq_high = 1.0
        self.compression = 0.0
        self.noise_reduction = 0.0
        self.chorus = 0.0
        self.vibrato = 0.0
        
        # Initialize UI
        self.init_ui()
        
        # Start audio processing thread
        self.start_audio_processing()
        
    def init_ui(self):
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Voice effects
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Voice templates group
        template_group = QGroupBox("Voice Templates")
        template_layout = QVBoxLayout()
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Normal Voice", 
            "Deep Voice", 
            "Chipmunk", 
            "Robot", 
            "Alien", 
            "Demon", 
            "Underwater", 
            "Radio", 
            "Helium", 
            "Giant"
        ])
        self.template_combo.currentIndexChanged.connect(self.apply_template)
        template_layout.addWidget(self.template_combo)
        
        apply_template_btn = QPushButton("Apply Template")
        apply_template_btn.clicked.connect(self.apply_template)
        template_layout.addWidget(apply_template_btn)
        
        template_group.setLayout(template_layout)
        left_layout.addWidget(template_group)
        
        # Pitch control group
        pitch_group = QGroupBox("Pitch & Formant Control")
        pitch_layout = QVBoxLayout()
        
        pitch_layout.addWidget(QLabel("Pitch Shift:"))
        self.pitch_slider = QSlider(Qt.Horizontal)
        self.pitch_slider.setRange(-1200, 1200)  # Semitones * 100
        self.pitch_slider.setValue(0)
        self.pitch_slider.valueChanged.connect(self.update_pitch)
        pitch_layout.addWidget(self.pitch_slider)
        
        pitch_layout.addWidget(QLabel("Formant Shift:"))
        self.formant_slider = QSlider(Qt.Horizontal)
        # FIXED: Removed extra parenthesis and fixed comment formatting
        self.formant_slider.setRange(50, 200)  # Represents 0.5 to 2.0
        self.formant_slider.setValue(100)
        self.formant_slider.valueChanged.connect(self.update_formant)
        pitch_layout.addWidget(self.formant_slider)
        
        pitch_group.setLayout(pitch_layout)
        left_layout.addWidget(pitch_group)
        
        # Effects group
        effects_group = QGroupBox("Special Effects")
        effects_layout = QVBoxLayout()
        
        effects_layout.addWidget(QLabel("Distortion:"))
        self.distortion_slider = QSlider(Qt.Horizontal)
        self.distortion_slider.setRange(0, 100)
        self.distortion_slider.setValue(0)
        self.distortion_slider.valueChanged.connect(self.update_distortion)
        effects_layout.addWidget(self.distortion_slider)
        
        effects_layout.addWidget(QLabel("Reverb:"))
        self.reverb_slider = QSlider(Qt.Horizontal)
        self.reverb_slider.setRange(0, 100)
        self.reverb_slider.setValue(0)
        self.reverb_slider.valueChanged.connect(self.update_reverb)
        effects_layout.addWidget(self.reverb_slider)
        
        effects_layout.addWidget(QLabel("Robot Effect:"))
        self.robot_slider = QSlider(Qt.Horizontal)
        self.robot_slider.setRange(0, 100)
        self.robot_slider.setValue(0)
        self.robot_slider.valueChanged.connect(self.update_robot)
        effects_layout.addWidget(self.robot_slider)
        
        effects_layout.addWidget(QLabel("Echo:"))
        self.echo_slider = QSlider(Qt.Horizontal)
        self.echo_slider.setRange(0, 100)
        self.echo_slider.setValue(0)
        self.echo_slider.valueChanged.connect(self.update_echo)
        effects_layout.addWidget(self.echo_slider)
        
        effects_group.setLayout(effects_layout)
        left_layout.addWidget(effects_group)
        
        # EQ group
        eq_group = QGroupBox("Equalizer")
        eq_layout = QVBoxLayout()
        
        eq_layout.addWidget(QLabel("Low Frequencies:"))
        self.eq_low_slider = QSlider(Qt.Horizontal)
        self.eq_low_slider.setRange(0, 200)
        self.eq_low_slider.setValue(100)
        self.eq_low_slider.valueChanged.connect(self.update_eq_low)
        eq_layout.addWidget(self.eq_low_slider)
        
        eq_layout.addWidget(QLabel("Mid Frequencies:"))
        self.eq_mid_slider = QSlider(Qt.Horizontal)
        self.eq_mid_slider.setRange(0, 200)
        self.eq_mid_slider.setValue(100)
        self.eq_mid_slider.valueChanged.connect(self.update_eq_mid)
        eq_layout.addWidget(self.eq_mid_slider)
        
        eq_layout.addWidget(QLabel("High Frequencies:"))
        self.eq_high_slider = QSlider(Qt.Horizontal)
        self.eq_high_slider.setRange(0, 200)
        self.eq_high_slider.setValue(100)
        self.eq_high_slider.valueChanged.connect(self.update_eq_high)
        eq_layout.addWidget(self.eq_high_slider)
        
        eq_group.setLayout(eq_layout)
        left_layout.addWidget(eq_group)
        
        # Right panel - Visualization and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Visualization
        vis_group = QGroupBox("Voice Visualization")
        vis_layout = QVBoxLayout()
        
        # Waveform plot
        self.wave_plot = pg.PlotWidget()
        self.wave_plot.setBackground('#2c3e50')
        self.wave_plot.setYRange(-32768, 32767)
        self.wave_plot.setMouseEnabled(x=False, y=False)
        self.wave_plot.hideAxis('bottom')
        self.wave_plot.hideAxis('left')
        self.wave_plot.setTitle("Voice Waveform", color='#ecf0f1', size='12pt')
        self.wave_curve = self.wave_plot.plot(pen=pg.mkPen('#3498db', width=2))
        vis_layout.addWidget(self.wave_plot)
        
        # Spectrum plot
        self.spec_plot = pg.PlotWidget()
        self.spec_plot.setBackground('#2c3e50')
        self.spec_plot.setLogMode(x=True, y=False)
        self.spec_plot.setYRange(0, 100)
        self.spec_plot.setMouseEnabled(x=False, y=False)
        self.spec_plot.setTitle("Frequency Spectrum", color='#ecf0f1', size='12pt')
        self.spec_curve = self.spec_plot.plot(pen=pg.mkPen('#e74c3c', width=2))
        vis_layout.addWidget(self.spec_plot)
        
        vis_group.setLayout(vis_layout)
        right_layout.addWidget(vis_group)
        
        # Control buttons
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.record_btn)
        
        self.play_btn = QPushButton("Play Last Recording")
        self.play_btn.clicked.connect(self.play_recording)
        control_layout.addWidget(self.play_btn)
        
        self.discord_btn = QPushButton("Connect to Discord")
        self.discord_btn.clicked.connect(self.connect_to_discord)
        control_layout.addWidget(self.discord_btn)
        
        control_group.setLayout(control_layout)
        right_layout.addWidget(control_group)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 600])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Select a voice template or adjust effects.")
        
        # Timer for visualization updates
        self.vis_timer = QTimer()
        self.vis_timer.timeout.connect(self.update_visualization)
        self.vis_timer.start(50)  # Update every 50ms
        
    def start_audio_processing(self):
        self.is_processing = True
        self.audio_thread = threading.Thread(target=self.audio_processing_loop)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
    def audio_processing_loop(self):
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
            stream_callback=self.audio_callback
        )
        
        self.stream.start_stream()
        
        while self.is_processing:
            time.sleep(0.1)
            
    def audio_callback(self, in_data, frame_count, time_info, status):
        # Convert raw data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Apply voice effects
        processed_data = self.apply_effects(audio_data)
        
        # Store for visualization
        self.last_audio_data = processed_data
        
        # Store for recording if active
        if self.is_recording:
            self.output_frames.append(processed_data.tobytes())
            
        # Return processed audio
        return (processed_data.tobytes(), pyaudio.paContinue)
    
    def apply_effects(self, data):
        # Convert to float for processing
        float_data = data.astype(np.float32) / 32768.0
        
        # Apply pitch shift (simple method)
        if self.pitch_shift != 0:
            # In a real implementation, this would use phase vocoding or granular synthesis
            # For simplicity, we'll use a simple resampling method
            factor = 2.0 ** (self.pitch_shift / 1200.0)
            new_length = int(len(float_data) * factor)
            indices = np.clip(np.round(np.arange(new_length) / factor), 0, len(float_data)-1).astype(int)
            float_data = float_data[indices]
        
        # Apply formant shift (simplified)
        if self.formant_shift != 1.0:
            # Formant shifting requires more advanced processing
            # This is a simplified version
            float_data = np.interp(
                np.arange(0, len(float_data)),
                np.arange(0, len(float_data)) * self.formant_shift, 
                float_data
            )
        
        # Apply distortion
        if self.distortion_level > 0:
            distortion_amount = self.distortion_level / 100.0
            float_data = np.tanh(float_data * (1 + distortion_amount * 10))
        
        # Apply EQ
        if self.eq_low != 1.0 or self.eq_mid != 1.0 or self.eq_high != 1.0:
            # Simple EQ implementation
            n = len(float_data)
            freq = np.fft.rfftfreq(n, d=1.0/self.RATE)
            fft_data = np.fft.rfft(float_data)
            
            # Apply EQ gains
            for i, f in enumerate(freq):
                if f < 300:
                    fft_data[i] *= self.eq_low
                elif f < 3000:
                    fft_data[i] *= self.eq_mid
                else:
                    fft_data[i] *= self.eq_high
            
            float_data = np.fft.irfft(fft_data, n)
        
        # Apply volume
        float_data = float_data * self.volume
        
        # Convert back to int16
        processed_data = (float_data * 32768.0).astype(np.int16)
        
        return processed_data
    
    def update_visualization(self):
        if hasattr(self, 'last_audio_data'):
            # Update waveform plot
            self.wave_curve.setData(self.last_audio_data)
            
            # Update spectrum plot
            n = len(self.last_audio_data)
            fft_data = np.abs(np.fft.rfft(self.last_audio_data))
            freq = np.fft.rfftfreq(n, d=1.0/self.RATE)
            # Convert to dB scale
            fft_data = 20 * np.log10(fft_data + 1e-6)
            # Normalize
            fft_data = np.clip(fft_data - np.max(fft_data) + 100, 0, 100)
            self.spec_curve.setData(freq, fft_data)
    
    def update_pitch(self, value):
        self.pitch_shift = value
        self.status_bar.showMessage(f"Pitch shifted by {value/100.0:.1f} semitones")
    
    def update_formant(self, value):
        self.formant_shift = value / 100.0
        self.status_bar.showMessage(f"Formant shifted by factor {self.formant_shift:.2f}")
    
    def update_distortion(self, value):
        self.distortion_level = value
        self.status_bar.showMessage(f"Distortion level: {value}%")
    
    def update_reverb(self, value):
        self.reverb_level = value
        self.status_bar.showMessage(f"Reverb level: {value}%")
    
    def update_robot(self, value):
        self.robot_level = value
        self.status_bar.showMessage(f"Robot effect: {value}%")
    
    def update_echo(self, value):
        self.echo_delay = value / 100.0
        self.status_bar.showMessage(f"Echo delay: {self.echo_delay:.2f}s")
    
    def update_eq_low(self, value):
        self.eq_low = value / 100.0
        self.status_bar.showMessage(f"Low EQ: {self.eq_low:.2f}")
    
    def update_eq_mid(self, value):
        self.eq_mid = value / 100.0
        self.status_bar.showMessage(f"Mid EQ: {self.eq_mid:.2f}")
    
    def update_eq_high(self, value):
        self.eq_high = value / 100.0
        self.status_bar.showMessage(f"High EQ: {self.eq_high:.2f}")
    
    def apply_template(self):
        template = self.template_combo.currentText()
        
        if template == "Normal Voice":
            self.pitch_slider.setValue(0)
            self.formant_slider.setValue(100)
            self.distortion_slider.setValue(0)
            self.reverb_slider.setValue(0)
            self.robot_slider.setValue(0)
            self.echo_slider.setValue(0)
            self.eq_low_slider.setValue(100)
            self.eq_mid_slider.setValue(100)
            self.eq_high_slider.setValue(100)
        
        elif template == "Deep Voice":
            self.pitch_slider.setValue(-400)  # -4 semitones
            self.formant_slider.setValue(70)   # Formant shift to 0.7
            self.eq_low_slider.setValue(150)   # Boost bass
            self.eq_mid_slider.setValue(80)    # Reduce mids
            self.eq_high_slider.setValue(60)   # Reduce highs
            self.reverb_slider.setValue(30)
            
        elif template == "Chipmunk":
            self.pitch_slider.setValue(800)    # +8 semitones
            self.formant_slider.setValue(150)  # Formant shift to 1.5
            self.eq_high_slider.setValue(150)  # Boost highs
            
        elif template == "Robot":
            self.robot_slider.setValue(100)
            self.distortion_slider.setValue(40)
            self.eq_mid_slider.setValue(150)
            self.eq_high_slider.setValue(150)
            
        elif template == "Alien":
            self.pitch_slider.setValue(300)
            self.formant_slider.setValue(180)
            self.reverb_slider.setValue(70)
            self.robot_slider.setValue(30)
            
        elif template == "Demon":
            self.pitch_slider.setValue(-600)
            self.formant_slider.setValue(50)
            self.distortion_slider.setValue(70)
            self.reverb_slider.setValue(50)
            
        elif template == "Underwater":
            self.eq_low_slider.setValue(200)
            self.eq_mid_slider.setValue(30)
            self.eq_high_slider.setValue(10)
            self.reverb_slider.setValue(80)
            
        elif template == "Radio":
            self.eq_mid_slider.setValue(200)
            self.eq_low_slider.setValue(30)
            self.eq_high_slider.setValue(30)
            self.distortion_slider.setValue(20)
            
        elif template == "Helium":
            self.pitch_slider.setValue(1000)
            self.formant_slider.setValue(180)
            
        elif template == "Giant":
            self.pitch_slider.setValue(-800)
            self.formant_slider.setValue(60)
            self.eq_low_slider.setValue(200)
            self.reverb_slider.setValue(100)
            
        self.status_bar.showMessage(f"Applied {template} template")
    
    def toggle_recording(self):
        if not self.is_recording:
            self.output_frames = []
            self.is_recording = True
            self.record_btn.setText("Stop Recording")
            self.status_bar.showMessage("Recording started...")
        else:
            self.is_recording = False
            self.record_btn.setText("Start Recording")
            self.save_recording()
            self.status_bar.showMessage("Recording saved to output.wav")
    
    def save_recording(self):
        wf = wave.open("output.wav", 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.output_frames))
        wf.close()
    
    def play_recording(self):
        if hasattr(self, 'output_frames') and self.output_frames:
            # Create temporary WAV file
            filename = "temp_playback.wav"
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.output_frames))
            wf.close()
            
            # Play the audio
            if not self.is_playing:
                self.is_playing = True
                self.play_btn.setText("Stop Playback")
                self.play_thread = threading.Thread(target=self.play_audio, args=(filename,))
                self.play_thread.daemon = True
                self.play_thread.start()
            else:
                self.is_playing = False
                self.play_btn.setText("Play Last Recording")
    
    def play_audio(self, filename):
        wf = wave.open(filename, 'rb')
        stream = self.audio.open(
            format=self.audio.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        data = wf.readframes(self.CHUNK)
        while data and self.is_playing:
            stream.write(data)
            data = wf.readframes(self.CHUNK)
        
        stream.stop_stream()
        stream.close()
        wf.close()
        os.remove(filename)
        self.is_playing = False
        self.play_btn.setText("Play Last Recording")
    
    def connect_to_discord(self):
        self.status_bar.showMessage("Connecting to Discord... (In a real app, this would set your mic input to VoiceMaster's virtual output)")
        # In a real implementation, this would guide the user to set their Discord input
        # to the virtual audio cable that our app outputs to
        
    def closeEvent(self, event):
        self.is_processing = False
        self.is_playing = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceChanger()
    window.show()
    sys.exit(app.exec_())