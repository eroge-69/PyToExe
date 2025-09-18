import PySimpleGUI as sg
import serial
import serial.tools.list_ports
import threading
import time

BAUD = 115200
PINS = [2,3,4,5,6,7,8,9,10,11,12,13]  # match Arduino sketch

def list_coms():
    return [p.device for p in serial.tools.list_ports.comports()]

def serial_reader_thread(ser, window, stop_event):
    buffer = ""
    while not stop_event.is_set():
        try:
            if ser.in_waiting:
                chunk = ser.read(ser.in_waiting).decode(errors='ignore')
                buffer += chunk
                while '\n' in buffer:
                    line, buffer = buffer.split('\n',1)
                    line = line.strip()
                    if line.startswith("STATE "):
                        parts = line.split()
                        if len(parts) >= 3:
                            pin = int(parts[1])
                            val = int(parts[2])
                            window.write_event_value('-PINSTATE-', (pin, val))
                    elif line.startswith("OK ") or line.startswith("ERR ") or line == "READY" or line == "END":
                        window.write_event_value('-LOG-', line)
        except Exception as e:
            window.write_event_value('-ERROR-', str(e))
            break
        time.sleep(0.05)

def connect_serial(com):
    ser = serial.Serial(com, BAUD, timeout=0.1)
    time.sleep(0.2)
    return ser

sg.theme('DarkBlue3')
left_col = [
    [sg.Text('Portas COM:'), sg.Combo(list_coms(), key='-COM-', size=(15,1)), sg.Button('Refresh', key='-REF-')],
    [sg.Button('Conectar', key='-CONNECT-'), sg.Button('Desconectar', key='-DISCONNECT-', disabled=True)],
    [sg.HorizontalSeparator()],
    [sg.Button('Enviar GET (refresh estados)', key='-GET-')],
    [sg.Text('Log:')],
    [sg.Multiline('', key='-ML-', size=(40,10), autoscroll=True, disabled=True)]
]

pin_buttons = []
for i, pin in enumerate(PINS):
    btn = sg.Button(f'PIN {pin}\nOFF', key=f'-BTN-{pin}-', size=(10,2), button_color=('white','firebrick'))
    pin_buttons.append(btn)

right_col = [
    [sg.Text('Controles de pinos:')],
    [sg.Column([pin_buttons[i:i+3] for i in range(0,12,3)], scrollable=False)]
]

layout = [
    [sg.Column(left_col), sg.VerticalSeparator(), sg.Column(right_col)],
    [sg.Text('Status:'), sg.Text('Desconectado', key='-STATUS-')]
]

window = sg.Window('Arduino 12x Control', layout, finalize=True)

ser = None
reader_thread = None
stop_event = None

def send_set(pin, val):
    global ser
    if ser and ser.is_open:
        cmd = f"SET {pin} {1 if val else 0}\n"
        ser.write(cmd.encode())

try:
    while True:
        event, values = window.read(timeout=200)
        if event == sg.WIN_CLOSED:
            break
        if event == '-REF-':
            window['-COM-'].update(values=list_coms())
        if event == '-CONNECT-':
            com = values['-COM-']
            if not com:
                sg.popup('Selecione uma porta COM.')
                continue
            try:
                ser = connect_serial(com)
                stop_event = threading.Event()
                reader_thread = threading.Thread(target=serial_reader_thread, args=(ser, window, stop_event), daemon=True)
                reader_thread.start()
                window['-STATUS-'].update(f'Conectado em {com}')
                window['-CONNECT-'].update(disabled=True)
                window['-DISCONNECT-'].update(disabled=False)
                window['-ML-'].print('Connected.')
                ser.write(b'GET\n')
            except Exception as e:
                sg.popup('Erro ao conectar:', e)
        if event == '-DISCONNECT-':
            if ser:
                try:
                    stop_event.set()
                except:
                    pass
                try:
                    ser.close()
                except:
                    pass
                ser = None
                window['-STATUS-'].update('Desconectado')
                window['-CONNECT-'].update(disabled=False)
                window['-DISCONNECT-'].update(disabled=True)
                window['-ML-'].print('Disconnected.')
        if event == '-GET-':
            if ser and ser.is_open:
                ser.write(b'GET\n')
            else:
                sg.popup('Conecte antes.')
        if isinstance(event, str) and event.startswith('-BTN-'):
            try:
                pin = int(event.split('-')[2])
            except:
                continue
            btn = window[event]
            text = btn.GetText()
            new_state = 1 if 'OFF' in text else 0
            send_set(pin, new_state)
            btn.update(f'PIN {pin}\n{"ON" if new_state else "OFF"}', button_color=('white','darkgreen' if new_state else 'firebrick'))
        if event == '-PINSTATE-':
            pin, val = values['-PINSTATE-']
            key = f'-BTN-{pin}-'
            if key in window.AllKeysDict:
                window[key].update(f'PIN {pin}\n{"ON" if val else "OFF"}', button_color=('white','darkgreen' if val else 'firebrick'))
        if event == '-LOG-':
            line = values['-LOG-']
            window['-ML-'].print(line)
        if event == '-ERROR-':
            err = values['-ERROR-']
            window['-ML-'].print('ERROR: ' + str(err))
except Exception as e:
    sg.popup('Erro inesperado:', e)
finally:
    try:
        if stop_event: stop_event.set()
    except: pass
    try:
        if ser and ser.is_open: ser.close()
    except: pass
    window.close()
