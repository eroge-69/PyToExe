import tkinter as tk
import serial
import time

# Initialize serial connection to Arduino
try:
    arduino = serial.Serial('COM8', 9600, timeout=1)  # Replace 'COM3' with your Arduino's port
    time.sleep(2)  # Wait for connection to establish
except serial.SerialException:
    print("Error: Could not connect to Arduino. Check the port and connection.")
    exit()

# Create the main GUI window
root = tk.Tk()
root.title("Arduino LED Control")
root.geometry("400x300")

# Function to send command to Arduino
def send_command(command):
    try:
        arduino.write(command.encode())
        print(f"Sent command: {command}")
    except serial.SerialException:
        print("Error: Could not send command to Arduino.")

# Functions for each button
def led1_on(): send_command('1')
def led1_off(): send_command('2')
def led2_on(): send_command('3')
def led2_off(): send_command('4')
def led3_on(): send_command('5')
def led3_off(): send_command('6')
def led4_on(): send_command('7')
def led4_off(): send_command('8')

# Create and place buttons
tk.Button(root, text="Yellow ON", command=led1_on, bg="green", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
tk.Button(root, text="Yellow OFF", command=led1_off, bg="red", fg="white", font=("Arial", 12)).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
tk.Button(root, text="Red ON", command=led2_on, bg="green", fg="white", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="ew")
tk.Button(root, text="Red 2 OFF", command=led2_off, bg="red", fg="white", font=("Arial", 12)).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
tk.Button(root, text="Green 3 ON", command=led3_on, bg="green", fg="white", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="ew")
tk.Button(root, text="Green 3 OFF", command=led3_off, bg="red", fg="white", font=("Arial", 12)).grid(row=2, column=1, padx=10, pady=10, sticky="ew")
tk.Button(root, text="blue 4 ON", command=led4_on, bg="green", fg="white", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="ew")
tk.Button(root, text="blue 4 OFF", command=led4_off, bg="red", fg="white", font=("Arial", 12)).grid(row=3, column=1, padx=10, pady=10, sticky="ew")

# Configure grid weights for responsive layout
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
for i in range(4):
    root.grid_rowconfigure(i, weight=1)

# Start the GUI main loop
root.mainloop()

# Close serial connection when window is closed
arduino.close()
