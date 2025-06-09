
import sys
import numpy as np
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg

class Salakhi(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("☣ 𝐒𝐚𝐥𝐚𝐤𝐡𝐢 ☣")
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #eeeeee;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QSlider::groove:horizontal {
                background: #555;
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #00e0ff;
                width: 20px;
                border-radius: 10px;
            }
        """)

        
        self.gain = 30.0  
        self.sample_rate = 44100
        self.buffer = np.zeros(1024)

        
        self.gain_label = QLabel(f"🎚️ Gain: {self.gain:.1f}x")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(int(self.gain))
        self.slider.valueChanged.connect(self.set_gain)

        self.plot = pg.PlotWidget()
        self.plot.setYRange(-1, 1)
        self.plot.setBackground('#121212')
        self.curve = self.plot.plot(pen=pg.mkPen('#00f0ff', width=2))

        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>☣ 𝐒𝐚𝐥𝐚𝐤𝐡𝐢 ☣</h2>"))
        layout.addWidget(self.gain_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.plot)
        self.setLayout(layout)

        self.stream = sd.Stream(channels=1, callback=self.audio_callback, samplerate=self.sample_rate)
        self.stream.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)

    def set_gain(self, value):
        self.gain = value
        self.gain_label.setText(f"🎚️ Gain: {self.gain:.1f}x")

    def denoise(self, signal):

        threshold = 0.01
        return np.where(np.abs(signal) < threshold, 0, signal)

    def audio_callback(self, indata, outdata, frames, time, status):
        if status:
            print("⚠️", status)
        input_audio = self.denoise(indata[:, 0])
        boosted = input_audio * self.gain
        clipped = np.clip(boosted, -1.0, 1.0)
        outdata[:, 0] = clipped
        self.buffer = clipped.copy()

    def update_plot(self):
        self.curve.setData(self.buffer)

    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Salakhi()
    window.resize(500, 300)
    window.show()
    sys