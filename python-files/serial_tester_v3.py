import serial
import serial.tools.list_ports
import time
import datetime
import signal
import sys
from colorama import init, Fore, Back, Style

init(autoreset=True)

# Félkövér ANSI kódok
BOLD = '\033[1m'
RESET = '\033[0m'

def handler(signum, frame):
    global ser
    print("\nKilépés...")
    ser.setRTS(False)
    sys.exit(0)

def list_com_ports():
    ports = serial.tools.list_ports.comports()
    port_list = []
    print("Elérhető COM portok:")
    for port in ports:
        print(f" {port.device} - {port.description}")
        port_list.append(port.device)
    return port_list

def find_next_available_com_port(start='COM1'):
    ports = serial.tools.list_ports.comports()
    sorted_ports = sorted([p.device for p in ports])
    if start in sorted_ports:
        index = sorted_ports.index(start) + 1
        return sorted_ports[index] if index < len(sorted_ports) else None
    elif sorted_ports:
        return sorted_ports[0]
    return None

if __name__ == '__main__':
    available_ports = list_com_ports()
    port_to_use = find_next_available_com_port()

    if not port_to_use:
        print(" Nem található megfelelő COM port a teszt indításához!")
        sys.exit(1)

    print("-----------------------------------------")

    try:
        ser = serial.Serial(
            port=port_to_use,
            baudrate=115200,
            bytesize=8,
            timeout=0.2,
            stopbits=serial.STOPBITS_ONE
        )
    except serial.SerialException:
        print(f" Hiba: Nem lehet megnyitni a {port_to_use} portot!")
        sys.exit(1)
        
    print(f" Adatok küldése a {port_to_use} porton keresztül.")
    signal.signal(signal.SIGINT, handler)
    ser.setRTS(True)
    print(f' [{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] RTS ON')
    print("-----------------------------------------")

    ser.dtr = False
    ser.rts = False
    time.sleep(2)
    print("Adatok küldése folyamatban:")
    print('\033[?25l', end='')
    spinner = ['|', '/', '-', '\\']
    i = 0

    while True:
        try:
            msg = b'abcd1234'
            ser.write(msg)
            time.sleep(0.1)
            resp = ser.readall()

            #sys.stdout.write('\r' + ' ' * 100 + '\r')

            if msg == resp:
                result_text = Back.GREEN + Fore.WHITE + BOLD + "  OK  " + RESET + "\r"
                ser.dtr = True
                ser.rts = False
            else:
                result_text = Back.RED + Fore.WHITE + BOLD + " HIBA " + RESET + "\r"
                ser.dtr = False
                ser.rts = True

            sys.stdout.write(f'{spinner[i % len(spinner)]} Eredmény: {result_text}')
            sys.stdout.flush()
            
            i += 1

        except serial.SerialException as ex:
            print(f"\nKapcsolat megszakadt a {port_to_use} porttal!")
            print(f"{ex}")
            ser.setRTS(False)
            ser.close()
            sys.exit(1)

        except Exception as ex:
            print(f'\nVáratlan hiba! {ex}')
