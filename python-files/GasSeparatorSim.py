import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QLCDNumber, QFrame, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg


class DCSMain(QMainWindow):
    def __init__(self):
        super().__init__()

        # Simulation state variables
        self.pressure = 800  # psi
        self.oil_level = 50  # bbl (% capacity)
        self.water_level = 30  # bbl (% capacity)
        self.gas_flow = 12.0  # MMSCFD

        self.well_flows = [4.0, 4.0, 4.0]  # MMSCFD from 3 wells

        # Alarm states
        self.alarms = []

        self.setWindowTitle("Horizontal 3-Phase Separator - 3 Wells DCS Simulator")
        self.setGeometry(100, 100, 1400, 800)

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left panel: Wells control
        well_panel = QVBoxLayout()
        well_panel.addWidget(QLabel("WELL FLOW CONTROL (MMSCFD)"))
        self.well_sliders = []
        for i in range(3):
            lbl = QLabel(f"Well {i+1}")
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(10)
            slider.setValue(int(self.well_flows[i]))
            slider.valueChanged.connect(self.update_well_flows)
            self.well_sliders.append(slider)
            well_panel.addWidget(lbl)
            well_panel.addWidget(slider)

        # ESD Button
        self.esd_button = QPushButton("🚨 ESD - Emergency Shutdown")
        self.esd_button.setStyleSheet("background-color: red; color: white; font-weight: bold; font-size: 16px;")
        self.esd_button.clicked.connect(self.esd_trip)
        well_panel.addWidget(self.esd_button)

        # Middle panel: Process indicators
        process_panel = QVBoxLayout()
        process_panel.addWidget(QLabel("SEPARATOR PROCESS VARIABLES"))

        self.lcd_pressure = self.make_lcd("Pressure (psi)")
        process_panel.addWidget(self.lcd_pressure[0])

        self.lcd_oil = self.make_lcd("Oil Level (%)")
        process_panel.addWidget(self.lcd_oil[0])

        self.lcd_water = self.make_lcd("Water Level (%)")
        process_panel.addWidget(self.lcd_water[0])

        self.lcd_gas = self.make_lcd("Gas Flow (MMSCFD)")
        process_panel.addWidget(self.lcd_gas[0])

        # Right panel: Alarms + Trends
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("ACTIVE ALARMS"))
        self.alarm_box = QTextEdit()
        self.alarm_box.setReadOnly(True)
        right_panel.addWidget(self.alarm_box)

        # Trend graph
        right_panel.addWidget(QLabel("TRENDS"))
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.addLegend()
        self.plot_widget.showGrid(x=True, y=True)
        self.pressure_curve = self.plot_widget.plot(pen='r', name="Pressure")
        self.oil_curve = self.plot_widget.plot(pen='y', name="Oil Level")
        self.water_curve = self.plot_widget.plot(pen='b', name="Water Level")
        right_panel.addWidget(self.plot_widget)

        self.trend_data = {"time": [], "pressure": [], "oil": [], "water": []}
        self.time_counter = 0

        # Assemble layout
        main_layout.addLayout(well_panel, 2)
        main_layout.addLayout(process_panel, 2)
        main_layout.addLayout(right_panel, 4)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Timer for simulation
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulation_step)
        self.timer.start(1000)  # update every second

    def make_lcd(self, label):
        frame = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(label))
        lcd = QLCDNumber()
        lcd.setDigitCount(7)
        layout.addWidget(lcd)
        frame.setLayout(layout)
        return frame, lcd

    def update_well_flows(self):
        for i, slider in enumerate(self.well_sliders):
            self.well_flows[i] = slider.value()

    def esd_trip(self):
        self.well_flows = [0, 0, 0]
        for s in self.well_sliders:
            s.setValue(0)
        self.log_alarm("🚨 ESD Activated: All wells shut in, blowdown initiated!")

    def log_alarm(self, text):
        if text not in self.alarms:
            self.alarms.append(text)
            self.alarm_box.append(text)

    def simulation_step(self):
        # Update process based on well flows
        total_inlet_gas = sum(self.well_flows)
        self.gas_flow = total_inlet_gas

        # Simplified dynamics
        self.pressure += (total_inlet_gas - 12.0) * 2.0
        self.oil_level += (total_inlet_gas * 0.2) - 0.1
        self.water_level += (total_inlet_gas * 0.1) - 0.05

        # Safety logic
        if self.pressure > 900:
            self.log_alarm("⚠️ PSV Lift: Pressure > 900 psi")
        if self.pressure > 920:
            self.log_alarm("🚨 HH Pressure Shutdown")
            self.esd_trip()
        if self.pressure < 600:
            self.log_alarm("🚨 LL Pressure Shutdown")
            self.esd_trip()
        if self.oil_level > 95:
            self.log_alarm("🚨 HH Oil Level Shutdown")
            self.esd_trip()
        if self.oil_level < 5:
            self.log_alarm("🚨 LL Oil Level Trip - Pump Protection")
        if self.water_level > 95:
            self.log_alarm("🚨 HH Water Level Shutdown")
            self.esd_trip()

        # Clamp values
        self.pressure = max(0, min(self.pressure, 1000))
        self.oil_level = max(0, min(self.oil_level, 100))
        self.water_level = max(0, min(self.water_level, 100))

        # Update LCDs
        self.lcd_pressure[1].display(f"{self.pressure:.1f}")
        self.lcd_oil[1].display(f"{self.oil_level:.1f}")
        self.lcd_water[1].display(f"{self.water_level:.1f}")
        self.lcd_gas[1].display(f"{self.gas_flow:.1f}")

        # Update trends
        self.time_counter += 1
        self.trend_data["time"].append(self.time_counter)
        self.trend_data["pressure"].append(self.pressure)
        self.trend_data["oil"].append(self.oil_level)
        self.trend_data["water"].append(self.water_level)

        self.pressure_curve.setData(self.trend_data["time"], self.trend_data["pressure"])
        self.oil_curve.setData(self.trend_data["time"], self.trend_data["oil"])
        self.water_curve.setData(self.trend_data["time"], self.trend_data["water"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DCSMain()
    window.show()
    sys.exit(app.exec_())
