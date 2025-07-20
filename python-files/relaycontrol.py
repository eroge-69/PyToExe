import serial
import serial.tools.list_ports
import PySimpleGUI as sg

def list_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

layout = [
    [sg.Text('Select COM port:'), sg.Combo(values=list_com_ports(), key='-PORT-', size=(10,1)), sg.Button('Connect')],
    [sg.Frame('Relay Control', [
        [sg.Button('Relay 1 ON'), sg.Button('Relay 1 OFF')],
        [sg.Button('Relay 2 ON'), sg.Button('Relay 2 OFF')],
        [sg.Button('Relay 3 ON'), sg.Button('Relay 3 OFF')],
        [sg.Button('Relay 4 ON'), sg.Button('Relay 4 OFF')],
        [sg.Button('Relay 5 ON'), sg.Button('Relay 5 OFF')],
    ], visible=False, key='-CONTROL-')],
    [sg.Output(size=(40,10))]
]

window = sg.Window('Relay Control', layout)

ser = None

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event == 'Connect':
        port = values['-PORT-']
        if not port:
            print('Please select a COM port.')
            continue
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            print(f'Connected to {port}')
            window['-CONTROL-'].update(visible=True)
        except serial.SerialException as e:
            print(f'Failed to connect to {port}: {e}')
            ser = None

    elif ser and event.startswith('Relay'):
        try:
            ser.write((event + '\n').encode())
            response = ser.readline().decode().strip()
            print(f"Sent: {event}, Received: {response}")
        except Exception as e:
            print(f"Communication error: {e}")

if ser:
    ser.close()
window.close()

