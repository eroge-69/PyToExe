# Installation Instructions (at top of script as comments)
"""
To install the required dependencies and run this landing rater application:

1. Install Python (if not already): https://www.python.org/downloads/
2. Open your terminal or command prompt
3. Run the following command to install dependencies:

   pip install PySide6 numpy

4. Save this script as landing_rater.py
5. Run the script:

   python landing_rater.py

This will launch the MSFS Landing Rater GUI.
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer
import numpy as np

# Dummy SimConnect interface (replace with actual pysimconnect integration)
class SimConnectDummy:
    def get_data(self):
        # Simulate landing data
        return {
            "vertical_speed": np.random.uniform(-800, -50),
            "airspeed": np.random.uniform(110, 150),
            "g_force": np.random.uniform(1.0, 2.0),
            "centerline_offset": np.random.uniform(0.0, 10.0),
            "weight_on_wheels": True
        }

class LandingRater(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSFS Landing Rater")
        self.sim = SimConnectDummy()  # Replace with real SimConnect interface

        self.v_layout = QVBoxLayout()
        self.vs_label = QLabel("Vertical Speed: -")
        self.gs_label = QLabel("Touchdown Speed: -")
        self.gf_label = QLabel("G-Force: -")
        self.cl_label = QLabel("Centerline Offset: -")
        self.score_label = QLabel("Smoothness Rating: -")

        self.save_button = QPushButton("Save Landing")
        self.clear_button = QPushButton("Clear")
        self.save_button.clicked.connect(self.save_landing)
        self.clear_button.clicked.connect(self.clear_labels)

        self.v_layout.addWidget(self.vs_label)
        self.v_layout.addWidget(self.gs_label)
        self.v_layout.addWidget(self.gf_label)
        self.v_layout.addWidget(self.cl_label)
        self.v_layout.addWidget(self.score_label)
        self.v_layout.addWidget(self.save_button)
        self.v_layout.addWidget(self.clear_button)

        self.setLayout(self.v_layout)

        self.landing_data = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_landing)
        self.timer.start(1000)  # Check every second

    def check_landing(self):
        data = self.sim.get_data()
        if data['weight_on_wheels']:
            self.landing_data = data
            score = self.calculate_score(data)

            self.vs_label.setText(f"Vertical Speed: {data['vertical_speed']:.1f} ft/min")
            self.gs_label.setText(f"Touchdown Speed: {data['airspeed']:.1f} kts")
            self.gf_label.setText(f"G-Force: {data['g_force']:.2f} G")
            self.cl_label.setText(f"Centerline Offset: {data['centerline_offset']:.1f} ft")
            self.score_label.setText(f"Smoothness Rating: {score:.0f} / 100")

    def calculate_score(self, data):
        vs_score = max(0, 100 - abs(data['vertical_speed']) / 8)  # ~100 if VS is low
        g_score = max(0, 100 - (data['g_force'] - 1.0) * 100)  # Ideal: 1.0 G
        cl_score = max(0, 100 - data['centerline_offset'] * 5)

        total_score = (vs_score * 0.4) + (g_score * 0.3) + (cl_score * 0.3)
        return total_score

    def save_landing(self):
        if self.landing_data:
            with open("landing_log.csv", "a") as f:
                f.write(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')},{self.landing_data['vertical_speed']:.1f},{self.landing_data['airspeed']:.1f},{self.landing_data['g_force']:.2f},{self.landing_data['centerline_offset']:.1f}\n"
                )

    def clear_labels(self):
        self.vs_label.setText("Vertical Speed: -")
        self.gs_label.setText("Touchdown Speed: -")
        self.gf_label.setText("G-Force: -")
        self.cl_label.setText("Centerline Offset: -")
        self.score_label.setText("Smoothness Rating: -")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LandingRater()
    window.show()
    sys.exit(app.exec())
