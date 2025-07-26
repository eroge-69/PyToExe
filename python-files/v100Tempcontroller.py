import time
import serial
from serial.serialutil import SerialException
from serial.tools import list_ports
from pynvml import *

# Initialize NVML (NVIDIA Management Library)
nvmlInit()
TARGET_VENDOR_ID = 0x10DE  # NVIDIA
TARGET_DEVICE_ID = [0x20B0, 0x1DB8]

handle = None
gpu_count = nvmlDeviceGetCount()

for i in range(gpu_count):
    h = nvmlDeviceGetHandleByIndex(i)
    pci_info = nvmlDeviceGetPciInfo(h)
    pci_id = pci_info.pciDeviceId

    device_id = (pci_id >> 16) & 0xFFFF
    vendor_id = pci_id & 0xFFFF

    print(f"GPU {i} - Vendor: {vendor_id:04X}, Device: {device_id:04X}")

    if vendor_id == TARGET_VENDOR_ID and device_id in TARGET_DEVICE_ID:
        handle = h
        print(f"Matched GPU {i} with PCI ID {vendor_id:04X}:{device_id:04X}")
        break

if handle is None:
    raise RuntimeError("Target GPU with PCI ID 10DE:20B0 not found.")

# Explicit temperature-to-fan-percentage profile (temp °C → fan %)
temp_fan_profile = [
    (20, 20), (25, 20), (30, 20), (35, 20), (40, 20), (45, 20),
    (50, 20), (55, 20), (60, 30), (65, 42), (70, 55),
    (75, 67), (80, 80), (85, 92), (90, 100), (95, 100), (100, 100)
]

def get_fan_percent(temp):
    if temp <= temp_fan_profile[0][0]:
        return temp_fan_profile[0][1]
    if temp >= temp_fan_profile[-1][0]:
        return temp_fan_profile[-1][1]
    for i in range(1, len(temp_fan_profile)):
        t0, f0 = temp_fan_profile[i - 1]
        t1, f1 = temp_fan_profile[i]
        if t0 <= temp <= t1:
            return round(f0 + (f1 - f0) * (temp - t0) / (t1 - t0))

def connect_serial():
    while True:
        ports = list(list_ports.comports())
        print(f"Available COM ports: {[p.device for p in ports]}")
        for port in ports:
            try:
                ser = serial.Serial(
                    port=port.device,
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1,
                    rtscts=False,
                    dsrdtr=False
                )
                print(f"Connected to {port.device}")
                return ser
            except SerialException as e:
                print(f"Failed to connect to {port.device}: {e}")
        print("No available serial ports or all failed. Retrying in 5 seconds...")
        time.sleep(5)

ser = connect_serial()

try:
    while True:
        try:
            # Try to get hotspot temperature if available
            try:
                temp_info = nvmlDeviceGetTemperatureReading(handle)
                hotspot_temp = temp_info.temperatureGpu
            except Exception:
                hotspot_temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU) + 15

            print(f"Hotspot Temp: {hotspot_temp} °C")

            pwm = get_fan_percent(hotspot_temp)
            print(f"Fan PWM: {pwm}%")

            command = f"pwm {pwm}\r\n"
            for c in command:
                try:
                    ser.write(c.encode())
                except SerialException:
                    print("Serial disconnected while writing. Reconnecting...")
                    ser.close()
                    ser = connect_serial()
                    break  # Exit character loop
                time.sleep(0.01)

        except SerialException:
            print("Serial connection lost. Reconnecting...")
            ser.close()
            ser = connect_serial()

        except Exception as e:
            print(f"Unexpected error: {e}")

        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    try:
        if ser.is_open:
            ser.close()
    except:
        pass
    nvmlShutdown()
