import serial
import time
import requests

PORT = 'COM3'
BAUD = 9600

def get_sensor_data():
    try:
        response = requests.get("http://localhost:8085/data.json")
        data = response.json()

        cpu_load = 0
        cpu_temp = 0
        gpu_load = 0
        gpu_temp = 0

        for hw in data["Children"]:
            name = hw["Text"].lower()

            if "cpu" in name and "amd" in name:
                for sensor in hw["Children"]:
                    for s in sensor["Children"]:
                        if "load" in s["Text"].lower() and "%" in s["Value"]:
                            cpu_load = int(float(s["Value"].replace("%", "")))
                        if "temperature" in s["Text"].lower() and "package" in s["Text"].lower():
                            cpu_temp = int(float(s["Value"].replace("°C", "")))

            if "gpu" in name or "radeon" in name or "rx" in name:
                for sensor in hw["Children"]:
                    for s in sensor["Children"]:
                        if "load" in s["Text"].lower() and "%" in s["Value"]:
                            gpu_load = int(float(s["Value"].replace("%", "")))
                        if "temperature" in s["Text"].lower() and "core" in s["Text"].lower():
                            gpu_temp = int(float(s["Value"].replace("°C", "")))

        return cpu_load, cpu_temp, gpu_load, gpu_temp
    except:
        return 0, 0, 0, 0

ser = serial.Serial(PORT, BAUD)
time.sleep(2)

while True:
    cpu_load, cpu_temp, gpu_load, gpu_temp = get_sensor_data()

    line1 = f"CPU:{cpu_load:>3}% T:{cpu_temp:>3}C"
    line2 = f"GPU:{gpu_load:>3}% T:{gpu_temp:>3}C"

    line1 = line1[:16]
    line2 = line2[:16]
    
    ser.write(f"{line1};{line2}\n".encode('utf-8'))
    time.sleep(1)
