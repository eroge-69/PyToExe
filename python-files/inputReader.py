import serial.tools.list_ports
import serial
import os
import psutil


def is_process_running(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and proc.info['name'].lower() == name.lower():
            return True
    return False


ports = serial.tools.list_ports.comports()
port_list = [port.device for port in ports]
serial_connections = []
if port_list:
    print("Available ports:", port_list)


def UpdateSerials():
    global port_list
    global serial_connections
    current_ports = [p.device for p in serial.tools.list_ports.comports()]
    if set(current_ports) != set(port_list):
        print("Ports changed.")
        print("Available ports:", current_ports)

        for ser in serial_connections:
            try:
                if ser.is_open:
                    ser.close()
                    print(f"Closed {ser.port}")
            except Exception as e:
                print(f"Error closing {ser.port}: {e}")

        port_list = current_ports[:]
        serial_connections = []

    else:
        return

    for port in port_list:
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            serial_connections.append(ser)
            print(f"Opened {port}")
        except Exception as e:
            print(f"Could not open {port}: {e}")


print("the application is started...")
while True:
    UpdateSerials()
    for ser in serial_connections:
        if ser.in_waiting:
            process_name = "notepad.exe"
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line == "TRIGGER" and is_process_running(process_name):
                try:
                    os.system(f"taskkill /f /im {process_name}")
                except:
                    pass
