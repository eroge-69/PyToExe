#from tkinter 
import tkinter as tk
from tkinter import font
from tkinter import simpledialog
import socket

import logging
import time
import threading
#from pymodbus.server import ModbusTcpServer
import pymodbus
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification
import asyncio
#from pymodbus.server.async_io import StartTcpServer

##################################################################################
# GLOBAL VARIABLES
net = 0
palet = 0
tare1 = 0
tare2 = 0
stable = False
sheets = 0

##################################################################################
def read_register(context, address=0):
    """ Reads the value of a holding register """
    value = context[0].getValues(3, address, count=1)  # Function code 3 (Holding Registers)
    return value[0]

##################################################################################
def parse_values(data):
    """
    Extracts the three values (Net Weight, Palette Weight, and Number of Items) from the incoming string.
    The format is:
      - Net Weight: Starts at byte 6, length 10.
      - Palette Weight: Starts at byte 17, length 10.
      - Number of Items: Starts at byte 30, length 10.
    """
    try:
        # Convert the received data (hex bytes as a string) into ASCII
        ascii_string = "".join(chr(int(byte, 16)) for byte in data.split(","))
        
        # Extract the values based on the specified positions
        net = int(ascii_string[5:15].strip())
        palet = int(ascii_string[17:28].strip())
        #sheet = int(ascii_string[30:39].strip())
        stable = ascii_string[2:4].strip()
        if stable == "ST":
            bStable = True
        else:
            bStable = False
        
        return net, palet, bStable
    except Exception as e:
        print(f"Error parsing values: {e}")
        return -1,-1,True

##################################################################################
def update_display(net, palet, tare1, tare2, sheets):
    """
    Updates the display with the parsed values.
    """
    weight_label.config(text=f"Καθαρό: {str(net - tare1 - tare2)}")
    palette_label.config(text=f"Παλέτα: {str(palet)}")
    tare1_label.config(text=f"Tare1: {str(tare1)}")
    tare2_label.config(text=f"Tare2: {str(tare2)}")
    sheet_label.config(text=f"Sheets: {str(sheets)}")

##################################################################################
def on_click_tare1_label(event):
    global tare1
    global net
    if tare1 <= 0:
        if stable:
            tare1 = net
    else:
        tare1 = 0

##################################################################################
def on_right_click_tare1_label(event):
    """Handles right-click event to input a new numerical value."""
    global tare1
    global net
    new_value = simpledialog.askinteger("Input", "Enter a new value:", minvalue=0, maxvalue=1000)
    if new_value is not None:  # If the user enters a value
        tare1 = int(new_value)
        tare1_label.config(text=tare1)  # Update the label text

##################################################################################
def on_click_tare2_label(event):
    global tare2
    global net
    if tare2 <= 0:
        if stable:
            tare2 = net
    else:
        tare2 = 0

##################################################################################
def start_tcp_client():
    global net
    global palet
    global tare1
    global tare2
    global stable
    global sheets
    while True:
        """
        Starts the TCP client to receive data and updates the tkinter display.
        """
        ip_address = "10.5.254.248"
        port = 502

        buffer = ""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                print(f"Connecting to TCP server at {ip_address}:{port}...")
                client_socket.connect((ip_address, port))
                print(f"Connected to {ip_address}:{port}")
                
                while True:
                    value1 = read_register(context)
                    if value1 != sheets:
                        sheets = value1
                        print(f"PLC Value: {sheets}")

                    data = client_socket.recv(1024)  # Adjust the buffer size if needed
                    if not data:
                        print("Connection closed by the server.")
                        break
                    # Convert the received data to a comma-separated string of hex values
                    hex_data = ",".join(f"{byte:02x}" for byte in data)
                    # Add received data to the buffer and process it
                    buffer += hex_data
                    # Split the buffer into lines based on the marker (0d,0a)
                    lines = buffer.split(",0d,0a")
                    # Keep the last part as it may be an incomplete line
                    buffer = lines.pop() if lines else ""
                    # Process each complete line
                    for line in lines:
                        if line:  # Skip empty lines
                            # Parse the three values from the received data
                            net, palet, stable = parse_values(hex_data)
                            update_display(net, palet, tare1, tare2, sheets)
                    print("Received data:", lines[0])
                    time.sleep(0.5)
                    
        except Exception as e:
            print(f"An error occurred in the TCP client: {e}")
            update_display(-1, -1, -1, -1, -1)

##################################################################################
# Setup logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Create a datastore (10 holding registers, all initialized to 0)
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 10)
)
context = ModbusServerContext(slaves=store, single=True)

# Optional device info
identity = ModbusDeviceIdentification()
identity.VendorName = "Prometal"
identity.ProductCode = "Line3"
identity.VendorUrl = ""
identity.ProductName = "PythonModbusServer"
identity.ModelName = "ModbusTCP"
identity.MajorMinorRevision = "1.0"

async def run_async_modbus_server():
    print("🚀 Modbus server starting on 0.0.0.0:502")
    await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=("0.0.0.0", 502)
    )

def start_modbus_server_in_thread():
    # Each thread needs its own asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(run_async_modbus_server())
    loop.run_forever()

# Start Modbus server in a background thread
modbus_thread = threading.Thread(target=start_modbus_server_in_thread, daemon=True)
modbus_thread.start()

print("✅ Modbus server thread started")



# GUI setupgetValues
root = tk.Tk()
root.title("Digital Scale")


# Make the window always on top
root.wm_attributes("-topmost", True)

# # Define a font for the digital scale
scale_font = font.Font(family="Courier", size=18, weight="bold")

# Create a frame to hold the labels side by side
frame = tk.Frame(root)
frame.pack(padx=20, pady=10)

# Create labels to display the values
weight_label = tk.Label(frame, text="Net: 0", font=scale_font, bg="black", fg="green", width=13, anchor="w")
weight_label.pack(side=tk.LEFT, padx=10)

palette_label = tk.Label(frame, text="Palette : 0", font=scale_font, bg="black", fg="green", width=13, anchor="w")
palette_label.pack(side=tk.LEFT, padx=10)

tare1_label = tk.Label(frame, text="Tare1", font=scale_font, bg="black", fg="green", width=13, anchor="w")
tare1_label.pack(side=tk.LEFT, padx=5)
tare1_label.bind("<Button-1>", on_click_tare1_label)
tare1_label.bind("<Button-3>", on_right_click_tare1_label)

tare2_label  = tk.Label(frame, text="Tare2", font=scale_font, bg="black", fg="green", width=13, anchor="w")
tare2_label.pack(side=tk.LEFT, padx=5)
tare2_label.bind("<Button-1>", on_click_tare2_label)

sheet_label  = tk.Label(frame, text="Sheets", font=scale_font, bg="black", fg="green", width=13, anchor="w")
sheet_label.pack(side=tk.LEFT, padx=5)

# Run the TCP client in a separate thread to avoid freezing the GUI
import threading
thread = threading.Thread(target=start_tcp_client, daemon=True)
thread.start()

# Start the server
# print("Starting Modbus TCP server on port 5020...")
# thread1 = threading.Thread(target=StartTcpServerD, daemon=True)
# thread1.start()
# Start the server


# Start the tkinter main loop
root.mainloop()
