import os
import sys
import queue
import subprocess
import re
import pyautogui
import wmi
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Set your Vosk model path here (no spaces in path!)
MODEL_PATH = "vosk-model-small-en-us-0.15"  # Change to your model folder

if not os.path.exists(MODEL_PATH):
    print(f"Model not found at {MODEL_PATH}")
    print("Download from https://alphacephei.com/vosk/models and unzip there.")
    sys.exit()

q = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

apps = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notebook": "notepad",
    "calculator": "calc",
    "whatsapp": r"C:\Users\YourUserName\AppData\Local\WhatsApp\WhatsApp.exe",
    "telegram": r"C:\Users\YourUserName\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "studio": r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
    "file": "explorer",
    "chatgpt": r"C:\Path\To\Your\ChatGPTApp.exe"
}

def set_volume(percent):
    if percent < 0 or percent > 100:
        print("Volume percent must be 0-100")
        return
    print(f"(Manual) Set volume to {percent}% - for precise control use external lib")

def set_brightness(percent):
    if percent < 0 or percent > 100:
        print("Brightness percent must be 0-100")
        return
    try:
        wmi_obj = wmi.WMI(namespace='wmi')
        methods = wmi_obj.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(percent, 0)
        print(f"Brightness set to {percent}%")
    except Exception as e:
        print(f"Brightness control failed: {e}")

def set_wifi(on):
    state = "enable" if on else "disable"
    try:
        subprocess.run(f'netsh interface set interface "Wi-Fi" {state}', shell=True)
        print(f"WiFi turned {'ON' if on else 'OFF'}")
    except Exception as e:
        print(f"WiFi toggle failed: {e}")

def set_bluetooth(on):
    try:
        state = 'Enable' if on else 'Disable'
        ps_cmd = f"Get-PnpDevice -FriendlyName '*Bluetooth*' | Where-Object {{$_.Status -eq 'OK'}} | ForEach-Object {{Disable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false}}" if not on else f"Get-PnpDevice -FriendlyName '*Bluetooth*' | Where-Object {{$_.Status -ne 'OK'}} | ForEach-Object {{Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false}}"
        subprocess.run(["powershell", "-Command", ps_cmd], check=True)
        print(f"Bluetooth turned {'ON' if on else 'OFF'}")
    except Exception as e:
        print(f"Bluetooth toggle failed: {e}")

def set_energy_saver(on):
    try:
        val = '0' if on else '1'
        subprocess.run(f'powercfg /setdcvalueindex SCHEME_CURRENT SUB_ENERGYSAVER ES_SETTINGINDEX {val}', shell=True)
        subprocess.run(f'powercfg /setacvalueindex SCHEME_CURRENT SUB_ENERGYSAVER ES_SETTINGINDEX {val}', shell=True)
        subprocess.run('powercfg /S SCHEME_CURRENT', shell=True)
        print(f"Energy saver turned {'ON' if on else 'OFF'}")
    except Exception as e:
        print(f"Energy saver toggle failed: {e}")

def number_to_word(num):
    words = {
        10: "ten",
        20: "twenty",
        30: "thirty",
        40: "forty",
        50: "fifty",
        60: "sixty",
        70: "seventy",
        80: "eighty",
        90: "ninety",
        100: "hundred"
    }

def run_command(command):
    command = command.lower()
    print(f"Recognized command: '{command}'")

    vol_match = re.search(r"volume (\d{1,3})", command)
    if vol_match:
        vol = int(vol_match.group(1))
        set_volume(vol)
        return

    bright_match = re.search(r"brightness (\d{1,3})", command)
    if bright_match:
        bright = int(bright_match.group(1))
        set_brightness(100)
        return

    if "network on" in command:
        set_wifi(True)
        return
    elif "network off" in command:
        set_wifi(False)
        return
    
    if "dark" in command:
        set_brightness(0)
        return

    
    if "brightness twenty" in command:
        set_brightness(20)
        return

    if "brightness fourty" in command:
        set_brightness(40)
        return
    
    if "brightness sixty" in command:
        set_brightness(60)
        return
           
    if "brightness eighty" in command:
        set_brightness(80)
        return
    
    if "brightness hundred" in command:
        set_brightness(100)
        return
    
    if "volume hundred" in command:
        set_volume(100)
        return
    
    if "volume eighty" in command:
        set_volume(80)
        return
    
    if "volume sixty" in command:
        set_volume(60)
        return
    
    if "volume fourty" in command:
        set_volume(40)
        return
    
    if "volume twenty" in command:
        set_volume(20)
        return
    
    if "mute" in command:
        set_volume(0)
        return

    if "bluetooth on" in command:
        set_bluetooth(True)
        return
    elif "bluetooth off" in command:
        set_bluetooth(False)
        return

    if "energy saver on" in command:
        set_energy_saver(True)
        return
    elif "energy saver off" in command:
        set_energy_saver(False)
        return

    for app in apps:
        if app in command:
            print(f"Opening {app}...")
            os.startfile(apps[app])
            return

    if "hide" in command:
        print("Showing Desktop (Win+D)...")
        pyautogui.hotkey('win', 'd')
        return

    if "exit" in command or "close" in command:
        print("Exiting program.")
        sys.exit()

    print("Command not recognized.")

def listen():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback):
        print("🎙️ Voice Assistant started, say commands...")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                import json
                text = json.loads(recognizer.Result()).get("text", "")
                if text:
                    run_command(text)

if __name__ == "__main__":
    listen()
