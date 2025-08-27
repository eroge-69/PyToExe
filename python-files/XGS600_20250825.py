# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 09:41:17 2024

@author: stm_analisis
"""

import sys
import threading
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore, QtWidgets
import os

# Asegúrate de que el script pueda importar desde su propia carpeta
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)
    
from XGS600Driver import XGS600Driver

# Configuración global
INTERVAL = 1  # Intervalo de tiempo en segundos por defecto
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S.%f"

# Configuración de correo (cambia aquí con tus datos)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "stmanalisis2024@gmail.com"
EMAIL_PASSWORD = "bych xegi sanv iosw"  # O app password

EMAIL_TO = "stmanalisis2024@gmail.com"
EMAIL_SUBJECT = "Alerta de presión XGS600"

def send_email(body):
    try:
        msg = MIMEText(body)
        msg["From"] = EMAIL_USER
        msg["To"] = EMAIL_TO
        msg["Subject"] = EMAIL_SUBJECT
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error enviando correo: {e}")

def get_pressure_values():
    STM = float(f"{XGS600Driver().read_all_pressures()[0]:.1e}")
    PREP = float(f"{XGS600Driver().read_all_pressures()[1]:.1e}")
    return STM, PREP

def get_filename():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "Data")
    os.makedirs(data_dir, exist_ok=True)

    now = datetime.now()
    date_str = now.strftime(DATE_FORMAT)
    time_str = now.strftime("%H-%M-%S")
    return os.path.join(data_dir, f"{date_str}_{time_str}_XGS600.txt")

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime(f"{DATE_FORMAT} {TIME_FORMAT}")[:-3] for value in values]

# class ScientificAxisItem(pg.AxisItem):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
    
#     def tickStrings(self, values, scale, spacing):
#         return [f"{value:.2e}" for value in values]

class ScientificAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # Si el eje está en modo log, 'values' son log10(valor_real)
        try:
            if self.logMode:
                return [f"{10**v:.2e}" for v in values]
            else:
                return [f"{v:.2e}" for v in values]
        except Exception:
            return [str(v) for v in values]

class PressureMonitor(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
        self.running = False
        self.data_thread = None
        self.filename = get_filename()
        self.email_sent_stm = False
        self.email_sent_prep = False

    def initUI(self):
        self.setWindowTitle("XGS600")
        self.setGeometry(100, 100, 800, 650)
        
        self.layout = QtWidgets.QVBoxLayout()
        
        self.graphWidget1 = pg.PlotWidget(
            title="STM Pressure (mbar)",
            axisItems={'bottom': TimeAxisItem(orientation='bottom'), 'left': ScientificAxisItem(orientation='left')}
        )
        self.graphWidget2 = pg.PlotWidget(
            title="PREP Pressure (mbar)",
            axisItems={'bottom': TimeAxisItem(orientation='bottom'), 'left': ScientificAxisItem(orientation='left')}
        )
        
        self.graphWidget1.setBackground('w')
        self.graphWidget2.setBackground('w')
        
        # 👉 Cambiar estilo de los títulos
        self.graphWidget1.setTitle("STM Pressure (mbar)", color="black", size="16pt")
        self.graphWidget2.setTitle("PREP Pressure (mbar)", color="black", size="16pt")
        
        # 👉 Fuente más grande y oscura para los números de los ejes
        font = QtGui.QFont()
        font.setPointSize(12)   # tamaño de fuente
        font.setBold(True)      # negrita

        for axis in ['bottom', 'left']:
            self.graphWidget1.getAxis(axis).setStyle(tickFont=font)
            self.graphWidget1.getAxis(axis).setPen('k')  # 'k' = negro

            self.graphWidget2.getAxis(axis).setStyle(tickFont=font)
            self.graphWidget2.getAxis(axis).setPen('k')
        
        self.layout.addWidget(self.graphWidget1)
        self.layout.addWidget(self.graphWidget2)
        
        # Controles para intervalo y cutoff
        self.startButton = QtWidgets.QPushButton("Start/Update")
        self.stopButton = QtWidgets.QPushButton("Stop")
        
        self.intervalLabel = QtWidgets.QLabel("Interval (s):")
        self.intervalInput = QtWidgets.QLineEdit(str(INTERVAL))
        
        self.cutoffSTMLabel = QtWidgets.QLabel("Cutoff STM (mbar):")
        self.cutoffSTMInput = QtWidgets.QLineEdit("1e-7")
        
        self.cutoffPREPLabel = QtWidgets.QLabel("Cutoff PREP (mbar):")
        self.cutoffPREPInput = QtWidgets.QLineEdit("1e-7")
        
        self.startButton.clicked.connect(self.start_monitoring)
        self.stopButton.clicked.connect(self.stop_monitoring)
        
        self.controls = QtWidgets.QFormLayout()
        self.controls.addRow(self.intervalLabel, self.intervalInput)
        self.controls.addRow(self.cutoffSTMLabel, self.cutoffSTMInput)
        self.controls.addRow(self.cutoffPREPLabel, self.cutoffPREPInput)
        self.controls.addWidget(self.startButton)
        self.controls.addWidget(self.stopButton)
        
        self.layout.addLayout(self.controls)
        
        self.stmPressureLabel = QtWidgets.QLabel("STM Pressure: 0.00e+00 mbar")
        self.prepPressureLabel = QtWidgets.QLabel("PREP Pressure: 0.00e+00 mbar")
        self.layout.addWidget(self.stmPressureLabel)
        self.layout.addWidget(self.prepPressureLabel)

        self.dateLabel = QtWidgets.QLabel("Date: YYYY-MM-DD")
        self.timeLabel = QtWidgets.QLabel("Time: HH:MM:SS.mmm")
        self.layout.addWidget(self.dateLabel)
        self.layout.addWidget(self.timeLabel)
        
        self.mousePosLabel = QtWidgets.QLabel("(Pressure = 0)")
        self.layout.addWidget(self.mousePosLabel)
        
        self.setLayout(self.layout)
        
        self.data1 = []
        self.data2 = []
        self.times = []
        
        #self.graphWidget1.setLabel('bottom', 'Time', **{'color': '#000000', 'font-size': '16pt'})
        self.graphWidget2.setLabel('bottom', 'Time', **{'color': '#000000', 'font-size': '16pt'})
        
        self.graphWidget1.getAxis('bottom').enableAutoSIPrefix(False)
        self.graphWidget2.getAxis('bottom').enableAutoSIPrefix(False)

        
        self.curve1 = self.graphWidget1.plot(pen='r')
        self.curve2 = self.graphWidget2.plot(pen='b')
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        
        self.proxy1 = pg.SignalProxy(self.graphWidget1.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMovedSTM)
        self.proxy2 = pg.SignalProxy(self.graphWidget2.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMovedPREP)
        
        self.setStyleSheet("""
            QLabel {
                color: black;
                font-size: 12pt;
            }
            QLineEdit {
                color: black;
                font-size: 12pt;
            }
            QPushButton {
                color: black;
                font-size: 12pt;
            }
            QGraphicsView {
                color: black;
                font-size: 12pt;
            }
        """)
    
    def start_monitoring(self):
        self.running = True
        self.email_sent_stm = False
        self.email_sent_prep = False
        
        if not self.data_thread or not self.data_thread.is_alive():
            self.data_thread = threading.Thread(target=self.monitor_pressure)
            self.data_thread.start()
        self.timer.start(1000)
    
    def stop_monitoring(self):
        self.running = False
        if self.data_thread:
            self.data_thread.join()
        self.timer.stop()
    
    def monitor_pressure(self):
        with open(self.filename, 'a') as f:
            if f.tell() == 0:
                f.write("Date\tHour\tSTM Pressure (mbar)\tPREP Pressure (mbar)\n")
            
            while self.running:
                pressure_stm, pressure_prep = get_pressure_values()
                now = datetime.now()
                date_str = now.strftime(DATE_FORMAT)
                hour_str = now.strftime(TIME_FORMAT)[:-3]
                
                f.write(f"{date_str}\t{hour_str}\t{pressure_stm:.2e}\t{pressure_prep:.2e}\n")
                f.flush()
                
                self.data1.append(pressure_stm)
                self.data2.append(pressure_prep)
                self.times.append(now)
                
                self.stmPressureLabel.setText(f"STM Pressure: {pressure_stm:.2e} mbar")
                self.prepPressureLabel.setText(f"PREP Pressure: {pressure_prep:.2e} mbar")
                self.dateLabel.setText(f"Date: {date_str}")
                self.timeLabel.setText(f"Time: {hour_str}")

                cutoff_stm = self.get_cutoff_stm()
                cutoff_prep = self.get_cutoff_prep()

                if pressure_stm > cutoff_stm and not self.email_sent_stm:
                    body = f"P(STM) over cutoff {cutoff_stm:.2e} mbar\nPresión actual STM: {pressure_stm:.2e} mbar\nFecha y hora: {date_str} {hour_str}"
                    send_email(body)
                    self.email_sent_stm = True

                if pressure_prep > cutoff_prep and not self.email_sent_prep:
                    body = f"P(PREP) over cutoff {cutoff_prep:.2e} mbar\nPresión actual PREP: {pressure_prep:.2e} mbar\nFecha y hora: {date_str} {hour_str}"
                    send_email(body)
                    self.email_sent_prep = True
                
                if pressure_stm <= cutoff_stm:
                    self.email_sent_stm = False
                if pressure_prep <= cutoff_prep:
                    self.email_sent_prep = False
                
                for _ in range(int(self.get_interval() * 10)):
                    if not self.running:
                        break
                    time.sleep(0.1)
    
    def update_plot(self):
        self.curve1.setData([t.timestamp() for t in self.times], self.data1)
        self.curve2.setData([t.timestamp() for t in self.times], self.data2)
    
    def get_interval(self):
        try:
            interval = float(self.intervalInput.text())
        except ValueError:
            interval = 1
        return interval

    def get_cutoff_stm(self):
        try:
            return float(self.cutoffSTMInput.text())
        except ValueError:
            return 1e-9

    def get_cutoff_prep(self):
        try:
            return float(self.cutoffPREPInput.text())
        except ValueError:
            return 1e-7
    
    def mouseMovedSTM(self, event):
        pos = event[0]
        if self.graphWidget1.sceneBoundingRect().contains(pos):
            mousePoint = self.graphWidget1.getPlotItem().vb.mapSceneToView(pos)
            pressure = mousePoint.y()
            timeStamp = mousePoint.x()
            date_time = datetime.fromtimestamp(timeStamp)
            formatted_time = date_time.strftime(f"{DATE_FORMAT} {TIME_FORMAT}")[:-3]
            self.mousePosLabel.setText(f"STM Pressure = {pressure:.2e} mbar, Time = {formatted_time}")

    def mouseMovedPREP(self, event):
        pos = event[0]
        if self.graphWidget2.sceneBoundingRect().contains(pos):
            mousePoint = self.graphWidget2.getPlotItem().vb.mapSceneToView(pos)
            pressure = mousePoint.y()
            timeStamp = mousePoint.x()
            date_time = datetime.fromtimestamp(timeStamp)
            formatted_time = date_time.strftime(f"{DATE_FORMAT} {TIME_FORMAT}")[:-3]
            self.mousePosLabel.setText(f"PREP Pressure = {pressure:.2e} mbar, Time = {formatted_time}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = PressureMonitor()
    ex.show()
    sys.exit(app.exec_())

