import cv2
import numpy as np
import pyautogui
import time
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QVBoxLayout, QWidget, QLabel, QFileDialog, QCheckBox
from PyQt5.QtCore import Qt
import threading
import sounddevice as sd
import scipy.io.wavfile as wavfile
import ffmpeg
import os

class ScreenRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recording = False
        self.mic_muted = False
        self.resolutions = {
            "480p": (640, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080),
            "Custom": (1366, 768)
        }
        self.formats = ["MP4", "MKV"]
        self.selected_resolution = "720p"
        self.selected_format = "MP4"
        self.output_file = None
        self.temp_audio_file = "temp_audio.wav"
        self.audio_data = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Screen Recorder")
        self.setGeometry(100, 100, 300, 300)

 
        layout = QVBoxLayout()

        self.resolution_label = QLabel("Select Resolution:", self)
        layout.addWidget(self.resolution_label)

        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItems(self.resolutions.keys())
        self.resolution_combo.setCurrentText("720p")
        self.resolution_combo.currentTextChanged.connect(self.update_resolution)
        layout.addWidget(self.resolution_combo)

       
        self.format_label = QLabel("Select Output Format:", self)
        layout.addWidget(self.format_label)

        self.format_combo = QComboBox(self)
        self.format_combo.addItems(self.formats)
        self.format_combo.setCurrentText("MP4")
        self.format_combo.currentTextChanged.connect(self.update_format)
        layout.addWidget(self.format_combo)

        
        self.mic_checkbox = QCheckBox("Mute Microphone", self)
        self.mic_checkbox.stateChanged.connect(self.toggle_mic)
        layout.addWidget(self.mic_checkbox)

  
        self.start_button = QPushButton("Start Recording", self)
        self.start_button.clicked.connect(self.start_recording)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Recording", self)
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

     
        self.status_label = QLabel("Status: Not Recording", self)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_resolution(self, resolution):
        self.selected_resolution = resolution

    def update_format(self, format):
        self.selected_format = format

    def toggle_mic(self, state):
        self.mic_muted = state == Qt.Checked

    def start_recording(self):
    
        file_filter = f"Video Files (*.{self.selected_format.lower()})"
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Video As", "", file_filter)
        
        if not output_file:
            self.status_label.setText("Status: No file selected")
            return
      
        if not output_file.lower().endswith(f".{self.selected_format.lower()}"):
            output_file += f".{self.selected_format.lower()}"
        
        self.output_file = output_file
        self.recording = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.resolution_combo.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.mic_checkbox.setEnabled(False)
        self.status_label.setText("Status: Recording")

        # Start video and audio recording threads
        self.temp_video_file = self.output_file + ".temp.avi"  # Temporary video file
        self.video_thread = threading.Thread(target=self.record_screen)
        self.video_thread.start()
        if not self.mic_muted:
            self.audio_thread = threading.Thread(target=self.record_audio)
            self.audio_thread.start()

    def stop_recording(self):
        self.recording = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.resolution_combo.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.mic_checkbox.setEnabled(True)
        self.status_label.setText("Status: Finalizing...")

        # Wait for threads to finish
        self.video_thread.join()
        if not self.mic_muted:
            self.audio_thread.join()

        # Merge video and audio into final file
        self.merge_audio_video()
        self.status_label.setText("Status: Not Recording")

    def record_screen(self):
        resolution = self.resolutions[self.selected_resolution]
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        out = cv2.VideoWriter(self.temp_video_file, fourcc, 20.0, resolution)

        while self.recording:
            screen = pyautogui.screenshot()
            frame = np.array(screen)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, resolution)
            out.write(frame)
            time.sleep(0.05)

        out.release()

    def record_audio(self):
        self.audio_data = []
        sample_rate = 44100

        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())

        with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
            while self.recording:
                time.sleep(0.1)

        # Save audio to temporary WAV file
        if self.audio_data:
            audio_array = np.concatenate(self.audio_data, axis=0)
            wavfile.write(self.temp_audio_file, sample_rate, audio_array)

    def merge_audio_video(self):
        try:
            # Use FFmpeg to merge video and audio into final file
            video_stream = ffmpeg.input(self.temp_video_file)
            output_args = {
                "vcodec": "libx264",
                "acodec": "aac",
                "map": "0:v:0"
            }
            if self.selected_format == "MKV":
                output_args["c:v"] = "copy"

            if not self.mic_muted and os.path.exists(self.temp_audio_file):
                audio_stream = ffmpeg.input(self.temp_audio_file)
                output = ffmpeg.output(video_stream, audio_stream, self.output_file, **output_args)
            else:
                output = ffmpeg.output(video_stream, self.output_file, **output_args)

            ffmpeg.run(output, overwrite_output=True)

            # Clean up temporary files
            if os.path.exists(self.temp_video_file):
                os.remove(self.temp_video_file)
            if os.path.exists(self.temp_audio_file):
                os.remove(self.temp_audio_file)

        except ffmpeg.Error as e:
            self.status_label.setText(f"Status: Error merging files: {e.stderr.decode()}")
            print(f"FFmpeg error: {e.stderr.decode()}")

def main():
    app = QApplication(sys.argv)
    recorder = ScreenRecorder()
    recorder.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()