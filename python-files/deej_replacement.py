import serial
import time
import yaml
import psutil
import win32gui
import win32process
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume, IMMDeviceEnumerator, IMMDevice
from ctypes import cast, POINTER
from collections import deque

# ------------------------
# Load config
# ------------------------
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

slider_mapping = config["slider_mapping"]
invert_sliders = config.get("invert_sliders", False)
com_port = config.get("com_port", "COM3")
baud_rate = config.get("baud_rate", 9600)
noise_reduction = config.get("noise_reduction", "default")

# ------------------------
# Serial setup (Arduino)
# ------------------------
ser = serial.Serial(com_port, baud_rate, timeout=1)
time.sleep(2)  # wait for Arduino reset

# ------------------------
# Windows audio setup
# ------------------------
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
master_volume = cast(interface, POINTER(IAudioEndpointVolume))

# ------------------------
# Helpers
# ------------------------
def map_value(raw):
    val = max(0, min(1023, raw)) / 1023.0
    if invert_sliders:
        val = 1.0 - val
    return val

def get_active_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except:
        return None

def set_master_volume(level):
    master_volume.SetMasterVolumeLevelScalar(level, None)

def set_app_volume(process_name, level):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == process_name.lower():
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(level, None)

def set_unmapped_volume(level, mapped_processes):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() not in mapped_processes:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            volume.SetMasterVolume(level, None)

# Noise reduction (simple moving average)
buffers = {i: deque(maxlen=3 if noise_reduction == "low" else 5 if noise_reduction == "default" else 8)
           for i in range(len(slider_mapping))}

# ------------------------
# Main loop
# ------------------------
print("🎚️  Deej Replacement running on", com_port, "@", baud_rate)
print("   Sliders mapped as follows:")
for idx, target in slider_mapping.items():
    print(f"   Slider {idx}: {target}")

while True:
    try:
        line = ser.readline().decode().strip()
        if not line:
            continue

        values = line.split("|")
        if len(values) != len(slider_mapping):
            continue

        for idx, raw_val in enumerate(values):
            try:
                raw = int(raw_val)
            except:
                continue

            buffers[idx].append(raw)
            avg_raw = sum(buffers[idx]) / len(buffers[idx])
            val = map_value(avg_raw)

            target = slider_mapping[idx]

            if target == "master":
                set_master_volume(val)

            elif target == "deej.current":
                proc = get_active_process_name()
                if proc:
                    set_app_volume(proc, val)

            elif target == "deej.unmapped":
                mapped = [t for t in slider_mapping.values() if t not in ["master", "deej.unmapped", "deej.current"]]
                set_unmapped_volume(val, mapped)

            else:
                set_app_volume(target, val)

    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        break
    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(0.5)
