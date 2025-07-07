import serial
import time
import datetime
import signal

def handler(signum, frame):
    global ser
    print("exiting ...")
    ser.setRTS(False)
    exit(0)

if __name__ == '__main__':
    ser = serial.Serial(port="COM5", baudrate=115200, bytesize=8, timeout=0.2, stopbits=serial.STOPBITS_ONE)
    signal.signal(signal.SIGINT, handler)

    ser.setRTS(True)
    print(f'[{datetime.datetime.now()}] RTS ON')
    # DTR és RTS alapértelmezésben aktívak, de itt kézzel kapcsoljuk őket
    ser.dtr = False  # DTR vonal LOW (nem kapcsolva)
    ser.rts = False  # RTS vonal LOW (nem kapcsolva)
    time.sleep(2)

    while True:
        try:
            msg = b'abcd1234'
            ser.write(msg)
            time.sleep(0.5)

            resp = ser.readall()
            print(f'Elkuldve: {msg} | Visszajott: {resp} | ', end='')
            print(f'Eredmeny: {"OK" if msg == resp else "HIBA"}')
            if msg == resp:
               ser.dtr = True  # DTR vonal HIGH (kapcsolva)
               ser.rts = False  # RTS vonal LOW (nem kapcsolva) 
            else:
               ser.dtr = False  # DTR vonal HIGH (nem kapcsolva)
               ser.rts = True  # RTS vonal LOW (kapcsolva) 
        except Exception as ex:
            print(f'EX: {ex}')

