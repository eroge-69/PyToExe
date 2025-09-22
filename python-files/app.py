import serial
import time
import requests

# === Arduino setup ===
arduino = serial.Serial('COM3', 9600)  # Apna COM port lagao (Windows me Device Manager se check karo)
time.sleep(2)  # wait for Arduino to reset

# === Gemi API setup ===
API_URL = "https://api.gemi.com/v1/command"  # Example URL (replace with actual)
API_KEY = "AIzaSyD4vw5R8X-eBihjxxsGufPFPYolgGsT0ks"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def send_to_arduino(cmd):
    arduino.write((cmd + "\n").encode())
    print("Sent to Arduino:", cmd)

def get_gemi_command(user_text):
    payload = {
        "input": user_text
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()

    # Assume API returns like: {"action": "RED_ON"}
    return data.get("action", "")

# === Main Loop ===
while True:
    user = input("Enter command for Gemi: ")  # tum yahan text likh sakte ho ya voice se input kara sakte ho
    action = get_gemi_command(user)

    if action:
        send_to_arduino(action)
    else:
        print("No valid action from Gemi API.")
