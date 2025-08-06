# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 12:55:54 2025

@author: DIPIG
"""

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QApplication
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from nptdms import TdmsFile
import numpy as np
import sys

class TDMSViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle("Vestas Data Analysis Tool - VDAT")

        layout = QVBoxLayout()

        # File selection
        self.file_label = QLabel("Select TDMS File:")
        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.load_tdms_file)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_button)

        # Group selection
        self.group_label = QLabel("Events")
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.load_channels)
        layout.addWidget(self.group_label)
        layout.addWidget(self.group_combo)

        # Channel selection
        self.channel_label = QLabel("Channels")
        self.channel_combo = QComboBox()
        self.channel_combo.currentIndexChanged.connect(self.plot_all)
        layout.addWidget(self.channel_label)
        layout.addWidget(self.channel_combo)

        # Plot areas
        self.figure1 = plt.figure(figsize=(6, 3))
        self.canvas1 = FigureCanvas(self.figure1)
        layout.addWidget(QLabel("Channel Data Plot:"))
        layout.addWidget(self.canvas1)

        self.figure2 = plt.figure(figsize=(6, 3))
        self.canvas2 = FigureCanvas(self.figure2)
        layout.addWidget(QLabel("Fast Fourier Transform:"))
        layout.addWidget(self.canvas2)

        self.figure3 = plt.figure(figsize=(6, 3))
        self.canvas3 = FigureCanvas(self.figure3)
        layout.addWidget(QLabel("Rainflow Counting (Approx):"))
        layout.addWidget(self.canvas3)

        self.setLayout(layout)

    def load_tdms_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open TDMS File", "", "TDMS Files (*.tdms)")
        if file_path:
            self.tdms_file = TdmsFile.read(file_path)
            self.group_combo.clear()
            self.group_combo.addItems([group.name for group in self.tdms_file.groups()])

    def load_channels(self):
        group_name = self.group_combo.currentText()
        if group_name:
            channels = self.tdms_file[group_name].channels()
            self.channel_combo.clear()
            self.channel_combo.addItems([channel.name for channel in channels])

    def plot_all(self):
        group_name = self.group_combo.currentText()
        channel_name = self.channel_combo.currentText()
        if group_name and channel_name:
            data = self.tdms_file[group_name][channel_name].data
            self.plot_time_series(data, channel_name)
            self.plot_fft(data)
            self.plot_rainflow(data)

    def plot_time_series(self, data, channel_name):
        self.figure1.clear()
        ax = self.figure1.add_subplot(111)
        ax.plot(data, color='blue')
        ax.set_xlabel('Time Index')
        ax.set_ylabel('Value')
        ax.set_title(f'{channel_name} Data Plot')
        ax.grid(True)
        self.canvas1.draw()

    def plot_fft(self, data):
        self.figure2.clear()
        ax = self.figure2.add_subplot(111)
        fft_vals = np.fft.fft(data)
        fft_freqs = np.fft.fftfreq(len(data))
        ax.plot(fft_freqs[:len(data)//2], np.abs(fft_vals[:len(data)//2]), color='green')
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Amplitude')
        ax.set_title('FFT of Signal')
        ax.grid(True)
        self.canvas2.draw()

    def plot_rainflow(self, data):
        self.figure3.clear()
        ax = self.figure3.add_subplot(111)
        ranges = np.abs(np.diff(data))
        ax.hist(ranges, bins=50, color='orange', edgecolor='black')
        ax.set_xlabel('Range')
        ax.set_ylabel('Count')
        ax.set_title('Rainflow Counting (Approximation)')
        ax.grid(True)
        self.canvas3.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = TDMSViewer()
    viewer.show()
    sys.exit(app.exec_())
