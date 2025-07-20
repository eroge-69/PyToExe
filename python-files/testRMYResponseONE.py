import serial
import time
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import re

class SerialMonitor(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ตั้งค่า Serial Ports
        self.serial_ports = {
            'COM3': None,
            'COM5': None
        }
        
        # ตัวแปรเก็บข้อมูล
        self.data = {
            'wind_speed': [],
            'wind_direction': [],
            'temperature': [],
            'humidity': [],
            'pressure': [],
            'rainfall': [],
            'time': []
        }
        
        self.initUI()
        self.initSerial()
        self.initTimers()
        
    def initUI(self):
        self.setWindowTitle('RM Young ResponseONE Monitor')
        self.setGeometry(100, 100, 1200, 800)
        
        # สร้าง layout หลัก
        main_widget = QtGui.QWidget()
        self.setCentralWidget(main_widget)
        layout = QtGui.QGridLayout()
        main_widget.setLayout(layout)
        
        # กราฟ Wind Speed
        self.wind_speed_plot = pg.PlotWidget(title="Wind Speed (m/s)")
        self.wind_speed_plot.setLabel('left', 'Speed', 'm/s')
        self.wind_speed_plot.showGrid(x=True, y=True)
        layout.addWidget(self.wind_speed_plot, 0, 0)
        
        # กราฟ Wind Direction
        self.wind_dir_plot = pg.PlotWidget(title="Wind Direction (degrees)")
        self.wind_dir_plot.setLabel('left', 'Direction', '°')
        self.wind_dir_plot.showGrid(x=True, y=True)
        layout.addWidget(self.wind_dir_plot, 0, 1)
        
        # กราฟ Temperature
        self.temp_plot = pg.PlotWidget(title="Temperature (°C)")
        self.temp_plot.setLabel('left', 'Temperature', '°C')
        self.temp_plot.showGrid(x=True, y=True)
        layout.addWidget(self.temp_plot, 1, 0)
        
        # กราฟ Humidity
        self.humidity_plot = pg.PlotWidget(title="Humidity (%)")
        self.humidity_plot.setLabel('left', 'Humidity', '%')
        self.humidity_plot.showGrid(x=True, y=True)
        layout.addWidget(self.humidity_plot, 1, 1)
        
        # กราฟ Pressure
        self.pressure_plot = pg.PlotWidget(title="Pressure (hPa)")
        self.pressure_plot.setLabel('left', 'Pressure', 'hPa')
        self.pressure_plot.showGrid(x=True, y=True)
        layout.addWidget(self.pressure_plot, 2, 0)
        
        # กราฟ Rainfall
        self.rain_plot = pg.PlotWidget(title="Rainfall (mm)")
        self.rain_plot.setLabel('left', 'Rainfall', 'mm')
        self.rain_plot.showGrid(x=True, y=True)
        layout.addWidget(self.rain_plot, 2, 1)
        
        # แสดงค่าปัจจุบัน
        self.current_values = QtGui.QLabel()
        self.current_values.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.current_values, 3, 0, 1, 2)
        
        # ไอคอนแสดงสถานะ
        self.temp_icon = QtGui.QLabel()
        self.temp_icon.setPixmap(QtGui.QPixmap("thermometer.png").scaled(64, 64))
        layout.addWidget(self.temp_icon, 0, 2)
        
        self.wind_icon = QtGui.QLabel()
        self.wind_icon.setPixmap(QtGui.QPixmap("anemometer.png").scaled(64, 64))
        layout.addWidget(self.wind_icon, 1, 2)
        
        self.rain_icon = QtGui.QLabel()
        self.rain_icon.setPixmap(QtGui.QPixmap("rain.png").scaled(64, 64))
        layout.addWidget(self.rain_icon, 2, 2)
        
    def initSerial(self):
        """Initialize serial connections"""
        for port in self.serial_ports:
            try:
                ser = serial.Serial(
                    port=port,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=1
                )
                self.serial_ports[port] = ser
                print(f"Connected to {port}")
            except Exception as e:
                print(f"Error opening {port}: {e}")
    
    def initTimers(self):
        """Initialize timers for reading and updating"""
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.readSerial)
        self.timer.start(100)  # Read every 100ms
        
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.updatePlots)
        self.update_timer.start(500)  # Update plots every 500ms
    
    def readSerial(self):
        """Read data from serial ports"""
        for port_name, ser in self.serial_ports.items():
            if ser and ser.in_waiting:
                try:
                    line = ser.readline().decode('ascii').strip()
                    if line:
                        self.parseData(line)
                except Exception as e:
                    print(f"Error reading from {port_name}: {e}")
    
    def parseData(self, data):
        """Parse RM Young ResponseONE data format"""
        # ตัวอย่างข้อมูล: ASCII POLAR FORMAT a www.ww ddd.d ttt.t hhh.h bbbb.b ppppp ss*cc<CR>
        match = re.match(r'a\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+\*\d+)', data)
        if match:
            wind_speed = float(match.group(1))  # m/s
            wind_dir = float(match.group(2))    # degrees
            temp = float(match.group(3))        # °C
            humidity = float(match.group(4))    # %
            pressure = float(match.group(5))    # hPa
            rainfall = int(match.group(6))      # mm
            
            # บันทึกข้อมูล
            timestamp = time.time()
            self.data['wind_speed'].append((timestamp, wind_speed))
            self.data['wind_direction'].append((timestamp, wind_dir))
            self.data['temperature'].append((timestamp, temp))
            self.data['humidity'].append((timestamp, humidity))
            self.data['pressure'].append((timestamp, pressure))
            self.data['rainfall'].append((timestamp, rainfall))
            self.data['time'].append(timestamp)
            
            # อัปเดตค่าปัจจุบัน
            self.current_values.setText(
                f"Current Values: "
                f"Wind: {wind_speed:.1f} m/s, {wind_dir:.0f}° | "
                f"Temp: {temp:.1f}°C | "
                f"Humidity: {humidity:.0f}% | "
                f"Pressure: {pressure:.1f} hPa | "
                f"Rain: {rainfall} mm"
            )
    
    def updatePlots(self):
        """Update all plots with new data"""
        # จำกัดข้อมูลที่แสดง (500 จุดล่าสุด)
        limit = 500
        
        # Wind Speed
        self.wind_speed_plot.clear()
        if self.data['wind_speed']:
            data = self.data['wind_speed'][-limit:]
            x = [item[0] for item in data]
            y = [item[1] for item in data]
            self.wind_speed_plot.plot(x, y, pen='b')
        
        # Wind Direction
        self.wind_dir_plot.clear()
        if self.data['wind_direction']:
            data = self.data['wind_direction'][-limit:]
            x = [item[0] for item in data]
            y = [item[1] for item in data]
            self.wind_dir_plot.plot(x, y, pen='g')
        
        # Temperature
        self.temp_plot.clear()
        if self.data['temperature']:
            data = self.data['temperature'][-limit:]
            x = [item[0] for item in data]
            y = [item[1] for item in data]
            self.temp_plot.plot(x, y, pen='r')
        
        # Humidity
        self.humidity_plot.clear()
        if self.data['humidity']:
            data = self.data['humidity'][-limit:]
            x = [item[0] for item in data]
            y = [item[1] for item in data]
            self.humidity_plot.plot(x, y, pen='m')
        
        # Pressure
        self.pressure_plot.clear()
        if self.data['pressure']:
            data = self.data['pressure'][-limit:]
            x = [item[0] for item in data]
            y = [item[1] for item in data]
            self.pressure_plot.plot(x, y, pen='c')
        
        # Rainfall
        self.rain_plot.clear()
        if self.data['rainfall']:
            data = self.data['rainfall'][-limit:]
            x = [item[0] for item in data]
            y = [item[1] for item in data]
            self.rain_plot.plot(x, y, pen='y')
    
    def closeEvent(self, event):
        """Close serial connections when window is closed"""
        for ser in self.serial_ports.values():
            if ser and ser.is_open:
                ser.close()
        event.accept()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    monitor = SerialMonitor()
    monitor.show()
    app.exec_()