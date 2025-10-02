import serial
import time
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import serial.tools.list_ports

# --- COM-Port automatisch erkennen ---
ports = list(serial.tools.list_ports.comports())
arduino_port = None
for p in ports:
    if "Arduino" in p.description or "USB Serial" in p.description:
        arduino_port = p.device
        break
if not arduino_port:
    raise Exception("Arduino Pro Micro nicht gefunden!")

arduino = serial.Serial(arduino_port, 9600)
time.sleep(2)  # Arduino Reset abwarten

# --- Lautst�rke Interface ---
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

print(f"Verbunden mit {arduino_port}. Systemlautst�rke wird an Arduino gesendet.")

while True:
    # Systemlautst�rke 0-100%
    level = volume.GetMasterVolumeLevelScalar()
    level_percent = int(level * 100)

    # an Arduino senden
    arduino.write(f"{level_percent}\n".encode())

    time.sleep(0.2)  # 200ms Intervall
