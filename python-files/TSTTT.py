

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import pyodbc
from datetime import datetime
import time

# ----------------------------
# SQL Server Configuration
# ----------------------------
DB_CONNECTION_STRING = (
    "Driver={SQL Server};"
    "Server=10.20.164.24;"
    "Database=EnvironmentDB;"
    "UID=EnvironmentDB;"
    "PWD=Ee@123456;"
)

# ----------------------------
# Define Station Modbus Mappings
# ----------------------------

stations = [
    {
        "ip": "10.20.183.230",  # Station 1
        "port": 502,
        "registers": {
            "NO conc":     (0,  "ppm"),
            "SO2 conc":    (6,  "ppm"),
            "NO2 conc":    (12, "ppm"),
            "H2O conc":    (18, "%"),
            "CO conc":     (24, "ppm"),
            "CO2 conc":    (30, "%"),
            "O2":          (36, "%"),
            "Temp":        (38, "°C"),
            "Pressure":    (40, "kpa"),
        }
    },
    {
        "ip": "10.20.183.231",  # Station 2
        "port": 502,
        "registers": {
            "NO conc P1":   (0,   "ppm"),
            "SO2 conc P1":  (6,   "ppm"),
            "NO2 conc P1":  (12,  "ppm"),
            "NO conc P2":   (18,  "ppm"),
            "SO2 conc P2":  (24,  "ppm"),
            "NO2 conc P2":  (30,  "ppm"),
            "H2O conc P1":  (36,  "%"),
            "CO conc P1":   (42,  "ppm"),
            "CO2 conc P1":  (48,  "%"),
            "H2O conc P2":  (54,  "%"),
            "CO conc P2":   (60,  "ppm"),
            "CO2 conc P2":  (66,  "%"),
            "O2-P1":        (72,  "%"),
            "O2-P2":        (74,  "%"),
            "Temp P1":      (76,  "°C"),
            "Pressure P1":  (78,  "kpa"),
            "Temp P2":      (80,  "°C"),
            "Pressure P2":  (82,  "kpa")
        }
    },
    {
        "ip": "10.20.183.232",  # Station 3
        "port": 502,
        "registers": {
            "NO conc":      (0,   "ppm"),
            "SO2 conc":     (6,   "ppm"),
            "NO2 conc":     (12,  "ppm"),
            "H2O conc":     (18,  "%"),
            "CO conc":      (24,  "ppm"),
            "CO2 conc":     (30,  "%"),
            "O2":           (36,  "%"),
            "DUST":         (38,  "Mg/m3"),
            "Temp":         (40,  "°C"),
            "Pressure":     (42,  "kpa")
        }
    },
    {
        "ip": "10.20.183.233",  # Station 4 - CCP1
        "port": 502,
        "registers": {
            "NO conc":     (0,  "ppm"),
            "SO2 conc":    (6,  "ppm"),
            "NO2 conc":    (12, "ppm"),
            "H2O conc":    (18, "%"),
            "CO conc":     (24, "ppm"),
            "CO2 conc":    (30, "%"),
            "O2":          (36, "%"),
            "DUST":        (38, "Mg/m3"),
            "Temp":        (40, "°C"),
            "Pressure":    (42, "kpa"),
        }
    },
    {
        "ip": "10.20.183.234",  # Station 5 - CCP2 Compaction
        "port": 502,
        "registers": {
            "NO conc":     (0,  "ppm"),
            "SO2 conc":    (6,  "ppm"),
            "NO2 conc":    (12, "ppm"),
            "H2O conc":    (18, "%"),
            "CO conc":     (24, "ppm"),
            "CO2 conc":    (30, "%"),
            "O2":          (36, "%"),
            "DUST-1":      (38, "Mg/m3"),
            "DUST-2":      (40, "Mg/m3"),
            "DUST-3":      (42, "Mg/m3"),
            "Temp":        (44, "°C"),
            "Pressure":    (46, "kpa")
        }
    },
    {
        "ip": "10.20.183.235",  # Station 6 - CCP2 Main Dryer
        "port": 502,
        "registers": {
            "NO conc":     (0,  "ppm"),
            "SO2 conc":    (6,  "ppm"),
            "NO2 conc":    (12, "ppm"),
            "H2O conc":    (18, "%"),
            "CO conc":     (24, "ppm"),
            "CO2 conc":    (30, "%"),
            "O2":          (36, "%"),
            "DUST":        (38, "Mg/m3"),
            "Temp":        (40, "°C"),
            "Pressure":    (42, "kpa")
        }
    }
]

# ----------------------------
# Read Float from Modbus (BADC)
# ----------------------------
def read_float_badc(client, address):
    try:
        rr = client.read_holding_registers(address, 2, unit=1)
        if rr.isError():
            return None
        decoder = BinaryPayloadDecoder.fromRegisters(
            rr.registers,
            byteorder=Endian.Big,
            wordorder=Endian.Little
        )
        return decoder.decode_32bit_float()
    except Exception as e:
        print(f"[{datetime.now()}] Error reading float at address {address}: {e}")
        return None

# ----------------------------
# Read Station Data
# ----------------------------
def read_station_data(station):
    client = ModbusTcpClient(station["ip"], port=station["port"])
    values = {}
    if not client.connect():
        print(f"[{datetime.now()}] ❌ Failed to connect to {station['ip']}")
        return None
    for param, (address, unit) in station["registers"].items():
        val = read_float_badc(client, address)
        values[param] = (val, unit)
    client.close()
    return values

# ----------------------------
# Save to SQL Server
# ----------------------------
def save_to_database(station_ip, values):
    try:
        station_id = {
            "10.20.183.230": 1,
            "10.20.183.231": 2,
            "10.20.183.232": 3,
            "10.20.183.233": 4,
            "10.20.183.234": 5,
            "10.20.183.235": 6
        }.get(station_ip, 0)

        timestamp = datetime.now()
        temp = values.get("Temp", (0, ""))[0]
        pressure = values.get("Pressure", (0, ""))[0]

        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        for param, (value, unit) in values.items():
            if value is None or not (-1e6 < value < 1e6):
                continue
            value = round(float(value), 3)
            cursor.execute("""
                INSERT INTO GasReadings (
                    StationID, ParameterName, Value, Unit, Timestamp, Quality, AlarmStatus,
                    Temperature, Pressure, Flow
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                station_id,
                param,
                value,
                unit,
                timestamp,
                1,
                "OK",
                round(temp or 0, 2),
                round(pressure or 0, 2),
                0
            ))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[{datetime.now()}] ✅ Station {station_id} saved successfully.")

    except Exception as e:
        print(f"[{datetime.now()}] ❌ DB error for {station_ip}: {e}")

# ----------------------------
# Main Loop: Every 60 Seconds
# ----------------------------
if __name__ == "__main__":
    while True:
        for station in stations:
            data = read_station_data(station)
            if data:
                save_to_database(station["ip"], data)
        time.sleep(60)
