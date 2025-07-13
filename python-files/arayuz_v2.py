import sys
import os
import math
import serial
import serial.tools.list_ports
# replaced folium with Leaflet-based HTML
import pyqtgraph as pg
from collections import deque
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer, QDateTime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTextEdit, QGroupBox, QFormLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView

class SerialReader(QThread):
    new_line = pyqtSignal(str)

    def __init__(self, port, baud):
        super().__init__()
        self.port = port
        self.baud = baud
        self.running = True

    def run(self):
        try:
            self.serial = serial.Serial(self.port, self.baud, timeout=1)
            while self.running:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode("utf-8", errors="ignore").strip()
                    if line:
                        self.new_line.emit(line)
        except Exception as e:
            self.new_line.emit(f"⚠️ Hata: {e}")

    def stop(self):
        self.running = False
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()
        self.wait()

class TelemetryUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Roket Telemetri - FlyIST")
        self.setStyleSheet("background-color: #2f2f2f; color: #eeeeee; font-family: 'Segoe UI';")
        self.setGeometry(50, 50, 1600, 900)

        self.reader_thread = None
        self.rssi_data = deque(maxlen=2000)
        self.temp_data = deque(maxlen=2000)
        self.altitude_data = deque(maxlen=2000)

        # Başlangıç koordinatları
        self.current_lat = 41.0082
        self.current_lon = 28.9784
        self.station_lat = 41.0082
        self.station_lon = 28.9784
        self.zoom_level = 15

        # Veri frekansı için zaman damgaları
        self.packet_timestamps = deque(maxlen=100)

        self.init_ui()

        # Grafik güncelleme timer'ı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(500)

        # Saat güncelleme timer'ı
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        # Hz kutucuğunu güncelleyen timer
        self.hz_timer = QTimer()
        self.hz_timer.timeout.connect(self.update_hz_label)
        self.hz_timer.start(500)

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.abspath("C:/Users/zilan/Downloads/logo.jpeg")
        logo_pixmap = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        text_label = QLabel(
            "<span style='font-size: 28px; font-weight: bold; color: #00ccff; font-family: Arial Black;'>"
            "flyIST ROCKET TEAM</span>"
        )
        text_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        header.addWidget(logo_label)
        header.addWidget(text_label)
        header.addStretch()

        # Bağlantı kutusu
        conn_box = self.build_connection_box()
        header.addLayout(self.wrap_with_centering(conn_box))
        header.addStretch()

        # İstasyon koordinatları ve saat
        station_box = self.build_station_box()
        header.addWidget(station_box)

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; padding-right: 20px;")
        header.addWidget(self.clock_label)
        main_layout.addLayout(header)

        # Orta kısım: Harita, telemetri, grafikler
        middle_layout = QHBoxLayout()

        # Harita
        self.map_view = QWebEngineView()
        self.map_html = self.generate_map_html()
        self.map_view.load(QUrl.fromLocalFile(self.map_html))
        middle_layout.addWidget(self.map_view, 3)

        # Telemetri ve ham veri
        telemetry_layout = QVBoxLayout()
        telemetry_layout.addWidget(self.build_telemetry_box())
        self.raw_data = QTextEdit()
        self.raw_data.setReadOnly(True)
        self.raw_data.setStyleSheet("background-color: black; color: lime; font-family: monospace;")
        telemetry_layout.addWidget(self.raw_data)
        middle_layout.addLayout(telemetry_layout, 2)

        # Grafikler
        graph_layout = QVBoxLayout()
        pg.setConfigOption('background', 'k')
        pg.setConfigOption('foreground', 'w')
        self.rssi_plot = pg.PlotWidget(title="RSSI")
        self.rssi_curve = self.rssi_plot.plot(pen=pg.mkPen('c', width=2))
        graph_layout.addWidget(self.rssi_plot)
        self.temp_plot = pg.PlotWidget(title="Sıcaklık (°C)")
        self.temp_curve = self.temp_plot.plot(pen=pg.mkPen('m', width=2))
        graph_layout.addWidget(self.temp_plot)
        self.alt_plot = pg.PlotWidget(title="İrtifa (m)")
        self.alt_curve = self.alt_plot.plot(pen=pg.mkPen('y', width=2))
        graph_layout.addWidget(self.alt_plot)
        middle_layout.addLayout(graph_layout, 4)

        main_layout.addLayout(middle_layout)
        self.setLayout(main_layout)
        self.update_clock()

    def wrap_with_centering(self, widget):
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(widget)
        layout.addStretch()
        return layout

    def build_connection_box(self):
        group = QGroupBox()
        group.setStyleSheet(
            "background-color: rgba(50,50,50,0.85); border: 4px solid white; border-radius:12px; padding:14px;"
        )
        layout = QHBoxLayout()
        port_label = QLabel("Port:")
        baud_label = QLabel("Baud:")
        for lbl in (port_label, baud_label):
            lbl.setStyleSheet("font-size:16px; font-weight:bold; color:white;")
        self.port_combo = QComboBox()
        self.port_combo.addItems([p.device for p in serial.tools.list_ports.comports()])
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600","19200","38400","57600","115200"])
        self.baud_combo.setCurrentText("9600")
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.status_label = QLabel("🔴")
        self.status_label.setStyleSheet("font-size:24px;")
        layout.addWidget(port_label)
        layout.addWidget(self.port_combo)
        layout.addWidget(baud_label)
        layout.addWidget(self.baud_combo)
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.status_label)
        group.setLayout(layout)
        return group

    def build_station_box(self):
        group = QGroupBox("📍 Yer İstasyonu Koordinatları")
        group.setStyleSheet(
            "background-color: rgba(70,70,70,0.95); border:2px solid lightgreen; border-radius:10px; "
            "padding:12px; font-size:16px; color:white;"
        )
        layout = QHBoxLayout()
        self.station_lat_input = QComboBox(); self.station_lat_input.setEditable(True)
        self.station_lat_input.setEditText(f"{self.station_lat:.6f}")
        self.station_lat_input.setMinimumWidth(120)
        self.station_lon_input = QComboBox(); self.station_lon_input.setEditable(True)
        self.station_lon_input.setEditText(f"{self.station_lon:.6f}")
        self.station_lon_input.setMinimumWidth(120)
        self.set_coord_button = QPushButton("Güncelle")
        self.set_coord_button.setStyleSheet("font-weight:bold; background-color:#00cc99; color:white;")
        self.set_coord_button.clicked.connect(self.update_station_coords)
        layout.addWidget(QLabel("LAT:")); layout.addWidget(self.station_lat_input)
        layout.addWidget(QLabel("LON:")); layout.addWidget(self.station_lon_input)
        layout.addWidget(self.set_coord_button)
        group.setLayout(layout)
        return group

    def build_telemetry_box(self):
        group = QGroupBox("📡 Telemetri Verileri")
        group.setStyleSheet(
            "background-color: rgba(50,50,50,0.85); border:2px solid lightblue; border-radius:10px; "
            "padding:10px;"
        )
        layout = QFormLayout()
        self.labels = {k: QLabel("-") for k in ["paket","sicaklik","basinc","irtifa","konum","uydu","rssi","hz","uzaklik"]}
        for k, lbl in self.labels.items():
            lbl.setStyleSheet("font-size:20px; font-weight:bold;")
            key_lbl = QLabel(f"{k.capitalize()}:")
            key_lbl.setStyleSheet("font-size:18px;color:lightblue;font-weight:bold;")
            layout.addRow(key_lbl, lbl)
        group.setLayout(layout)
        return group

    def update_station_coords(self):
        try:
            self.station_lat = float(self.station_lat_input.currentText())
            self.station_lon = float(self.station_lon_input.currentText())
            # Kutucukları xx.xxxxxx formatında güncelle
            self.station_lat_input.setEditText(f"{self.station_lat:.6f}")
            self.station_lon_input.setEditText(f"{self.station_lon:.6f}")
        except ValueError:
            return
        self.update_map_markers()

    def update_clock(self):
        now = QDateTime.currentDateTime()
        self.clock_label.setText(
            f"Saat: {now.toString('HH:mm:ss')}\n"
            f"Tarih: {now.toString('yyyy.MM.dd')}\n"
            f"Yer İstasyonu: {self.station_lat:.6f}, {self.station_lon:.6f}"
        )

    def update_map_markers(self):
        js = f"""
        (function(){{
          var station=[{self.station_lat}, {self.station_lon}];
          var rocket=[{self.current_lat}, {self.current_lon}];
          window.rocketMarker.setLatLng(rocket);
          window.stationMarker.setLatLng(station);
          window.trajectoryLine.setLatLngs([station, rocket]);
          var dist={int(self.haversine_distance(self.station_lat,self.station_lon,self.current_lat,self.current_lon))};
          // Mesafe popup'ı çizgi ortasında güncellenir, harita merkezine dokunulmaz
          window.distancePopup
            .setLatLng([(station[0]+rocket[0])/2,(station[1]+rocket[1])/2])
            .setContent('<b>Uzaklık: '+dist+' m</b>');
        }})();"""
        self.map_view.page().runJavaScript(js)

    def generate_map_html(self):
        path = os.path.abspath("templates/map.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'/>
<title>Rocket Telemetry Map</title>
<meta name='viewport' content='width=device-width, initial-scale=1.0'/>
<link rel='stylesheet' href='https://unpkg.com/leaflet@1.8.0/dist/leaflet.css'/>
<style>html,body{{height:100%;margin:0;padding:0}}#map{{width:100%;height:100%}}</style>
</head>
<body>
<div id='map'></div>
<script src='https://unpkg.com/leaflet@1.8.0/dist/leaflet.js'></script>
<script>
window.onload = function(){{
  var station=[{self.station_lat},{self.station_lon}];
  var rocket=[{self.current_lat},{self.current_lon}];
  window.map = L.map('map').setView(station,{self.zoom_level});
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:19,attribution:'© OpenStreetMap'}}).addTo(window.map);
  window.stationMarker = L.circleMarker(station,{{radius:8,fillColor:'green',color:'white',weight:2,fillOpacity:0.9}})
    .addTo(window.map).bindPopup('📍 Yer İstasyonu');
  window.rocketMarker = L.marker(rocket).addTo(window.map).bindPopup('🚀 Roket');
  window.trajectoryLine = L.polyline([station,rocket],{{color:'blue',weight:3,opacity:0.7}})
    .addTo(window.map);
  var dist={int(self.haversine_distance(self.station_lat,self.station_lon,self.current_lat,self.current_lon))};
  window.distancePopup = L.popup({{closeButton:false,autoClose:false}})
    .setLatLng([(station[0]+rocket[0])/2,(station[1]+rocket[1])/2])
    .setContent('<b>Uzaklık: '+dist+' m</b>').openOn(window.map);
  setTimeout(()=>window.map.invalidateSize(),200);
}};
</script>
</body>
</html>
        """
        with open(path,'w',encoding='utf-8') as f:
            f.write(html)
        return path

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    def toggle_connection(self):
        if self.reader_thread and self.reader_thread.isRunning():
            self.reader_thread.stop()
            self.reader_thread = None
            self.connect_btn.setText('Bağlan')
            self.status_label.setText('🔴')
        else:
            port = self.port_combo.currentText()
            baud = int(self.baud_combo.currentText())
            self.reader_thread = SerialReader(port, baud)
            self.reader_thread.new_line.connect(self.handle_line)
            self.reader_thread.start()
            self.connect_btn.setText('Kes')
            self.status_label.setText('🟢')

    def handle_line(self, line):
        # Yeni paket formatı: [Roket Telemetri] ile başlıyor, ardından 7 satır veri geliyor
        if not hasattr(self, 'packet_buffer'):
            self.packet_buffer = []
        # Paket başlangıcı
        if line.strip() == '[Roket Telemetri]':
            self.packet_buffer = []
            self.packet_started = True
            return
        # Paket satırlarını biriktir
        if hasattr(self, 'packet_started') and self.packet_started:
            self.packet_buffer.append(line)
            # Paket tamamlandı mı?
            if len(self.packet_buffer) == 7:
                # Ham veriyi ekrana yaz
                self.raw_data.append('[Roket Telemetri]')
                for l in self.packet_buffer:
                    self.raw_data.append(l)
                # Satırları işle
                try:
                    # Paket #
                    if self.packet_buffer[0].startswith('Paket #'):
                        self.labels['paket'].setText(self.packet_buffer[0].split('#')[1].strip())
                    # Sıcaklık
                    if self.packet_buffer[1].startswith('Sıcaklık'):
                        val = float(self.packet_buffer[1].split(':')[1].replace('°C','').strip())
                        self.labels['sicaklik'].setText(f"{val}")
                        self.temp_data.append(val)
                    # Basınç
                    if self.packet_buffer[2].startswith('Basınç'):
                        self.labels['basinc'].setText(self.packet_buffer[2].split(':')[1].replace('hPa','').strip())
                    # İrtifa
                    if self.packet_buffer[3].startswith('İrtifa'):
                        val = float(self.packet_buffer[3].split(':')[1].replace('m','').strip())
                        self.labels['irtifa'].setText(f"{val}")
                        self.altitude_data.append(val)
                    # Konum
                    if self.packet_buffer[4].startswith('Konum'):
                        coord = self.packet_buffer[4].split(':')[1].strip()
                        try:
                            lat, lon = map(float, coord.split(','))
                            coord_fmt = f"{lat:.6f}, {lon:.6f}"
                        except Exception:
                            coord_fmt = coord
                        self.labels['konum'].setText(coord_fmt)
                        self.current_lat, self.current_lon = lat, lon
                        self.update_map_markers()
                    # Uydu
                    if self.packet_buffer[5].startswith('Uydu'):
                        self.labels['uydu'].setText(self.packet_buffer[5].split(':')[1].strip())
                    # RSSI
                    if self.packet_buffer[6].startswith('RSSI'):
                        val = int(self.packet_buffer[6].split(':')[1].replace('/100','').strip())
                        self.labels['rssi'].setText(f"{val}")
                        self.rssi_data.append(val)
                    # Uzaklık kutucuğunu güncelle
                    uzaklik = int(self.haversine_distance(self.station_lat, self.station_lon, self.current_lat, self.current_lon))
                    self.labels['uzaklik'].setText(f"{uzaklik} m")
                    # Hz hesaplama için zaman damgası ekle
                    from time import time
                    self.packet_timestamps.append(time())
                except Exception as e:
                    print(f"Veri işleme hatası: {e}")
                self.packet_started = False

    def update_hz_label(self):
        # Son 1 saniyede gelen paket sayısı
        from time import time
        now = time()
        # 1 saniye içinde gelen paketleri say
        hz = len([t for t in self.packet_timestamps if now - t < 1.0])
        self.labels['hz'].setText(f"{hz}")

    def update_graphs(self):
        # Her grafik için kendi veri uzunluğunu kullan
        x_rssi = list(range(len(self.rssi_data)))
        x_temp = list(range(len(self.temp_data)))
        x_alt = list(range(len(self.altitude_data)))
        self.rssi_curve.setData(x_rssi, self.rssi_data)
        self.temp_curve.setData(x_temp, self.temp_data)
        self.alt_curve.setData(x_alt, self.altitude_data)

    def closeEvent(self, event):
        if self.reader_thread:
            self.reader_thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TelemetryUI()
    window.showMaximized()
    sys.exit(app.exec_())