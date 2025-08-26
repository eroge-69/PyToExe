import socket
import datetime

def aprs_to_nmea(lat, lon, speed=0.0, course=0.0):
    now = datetime.datetime.utcnow()
    time_str = now.strftime('%H%M%S')
    date_str = now.strftime('%d%m%y')
    lat_deg = int(abs(lat))
    lat_min = (abs(lat) - lat_deg) * 60
    lat_hem = 'N' if lat >= 0 else 'S'
    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_hem = 'E' if lon >= 0 else 'W'
    nmea = f'GPRMC,{time_str}.00,A,{lat_deg:02d}{lat_min:05.2f},{lat_hem},{lon_deg:03d}{lon_min:05.2f},{lon_hem},{speed:.1f},{course:.1f},{date_str},,,A'
    checksum = 0
    for c in nmea:
        checksum ^= ord(c)
    return f"${nmea}*{checksum:02X}"

def parse_aprs(packet):
    # Très simple parseur d'exemple
    try:
        if '!' not in packet:
            return None
        pos_data = packet.split('!')[1]
        lat = float(pos_data[0:2]) + float(pos_data[2:4])/60
        lon = float(pos_data[5:8]) + float(pos_data[8:10])/60
        return lat, lon
    except Exception:
        return None

HOST = '127.0.0.1'
PORT = 8000  # port par défaut d'AGWPE

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        data = s.recv(1024)
        if not data:
            break
        packet = data.decode(errors='ignore')
        if packet.startswith('\x00'):  # trame AGWPE
            parts = packet.split(':')
            if len(parts) > 1:
                aprs = parts[-1]
                coords = parse_aprs(aprs)
                if coords:
                    nmea = aprs_to_nmea(*coords)
                    print(nmea)