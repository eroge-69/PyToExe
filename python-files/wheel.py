import serial
import pyautogui
import time

# Replace 'COM3' with your Arduino port
arduino = serial.Serial('COM3', 9600)
time.sleep(2)  # Give Arduino time to reset

# Track which keys are currently held
keys_held = {"LEFT": False, "RIGHT": False, "GAS": False}
key_mapping = {"LEFT": "left", "RIGHT": "right", "GAS": "up"}

print("Listening for Arduino...")

while True:
    if arduino.in_waiting > 0:
        command = arduino.readline().decode().strip()
        # print for debugging
        print("Got:", command)
        
        # Hold key while pressed
        if command in key_mapping:
            if not keys_held[command]:
                pyautogui.keyDown(key_mapping[command])
                keys_held[command] = True

        # Release keys if no signal received for 0.3 sec
    # Check all keys
    for cmd, held in keys_held.items():
        if held:
            # Read pin states from Arduino again
            # We'll rely on repeated messages from Arduino
            pass  # The Arduino sketch sends repeated messages while pressed

    time.sleep(0.01)
