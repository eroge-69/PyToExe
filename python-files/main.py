import clr
import os
import time
import serial

# Путь к OpenHardwareMonitorLib.dll (укажите свой путь)
dll_path = os.path.join(os.getcwd(), "OpenHardwareMonitorLib.dll")
clr.AddReference(dll_path)

from OpenHardwareMonitor import Hardware

# Настройки COM-порта
PORT = 'COM11'      # Укажите ваш порт
BAUD = 115200

def initialize_ohm():
    computer = Hardware.Computer()
    computer.MainboardEnabled = True
    computer.CPUEnabled = True
    computer.RAMEnabled = False
    computer.GPUEnabled = False
    computer.HDDEnabled = False
    computer.Open()
    return computer

def get_cpu_temperature(computer):
    temps = []
    for hardware in computer.Hardware:
        if hardware.HardwareType == Hardware.HardwareType.CPU:
            hardware.Update()
            for sensor in hardware.Sensors:
                if str(sensor.SensorType) == "Temperature":
                    # Обычно "CPU Package" или "CPU Core" — нужные сенсоры
                    if "CPU Package" in sensor.Name or "CPU Core" in sensor.Name:
                        temps.append(sensor.Value)
            if temps:
                return max(temps)
    return None

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)  # Инициализация порта

    computer = initialize_ohm()

    try:
        while True:
            temp = get_cpu_temperature(computer)
            if temp is not None:
                data = f"{temp:.1f}\n"
                ser.write(data.encode())
                print(f"Sent CPU temperature: {data.strip()} °C")
            else:
                print("CPU temperature not found")
            time.sleep(1)
    except KeyboardInterrupt:
        ser.close()
        print("Serial port closed.")

if __name__ == "__main__":
    main()
