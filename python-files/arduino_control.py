import serial
import time
import subprocess
import signal
import sys

COM_PORT = 'COM4'  # nastavení tvého COM portu
BAUD_RATE = 9600

chrome_process = None

def open_chrome():
    global chrome_process
    if chrome_process is None:
        # otevře Chrome s cílovou stránkou
        chrome_process = subprocess.Popen(['start', 'chrome', 'https://umimecesky.cz'], shell=True)
        print("Chrome otevřen")

def close_chrome():
    global chrome_process
    if chrome_process:
        # zavře Chrome proces
        chrome_process.terminate()
        chrome_process = None
        print("Chrome zavřen")

def main():
    global chrome_process
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
        print(f"Připojeno na {COM_PORT} s baudrate {BAUD_RATE}")

        while True:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue
            print(f"Přijato: {line}")

            if line == 'MOTION':
                open_chrome()
            elif line == 'NOMOTION':
                time.sleep(5)
                close_chrome()
    except serial.SerialException as e:
        print(f"Chyba připojení: {e}")
    except KeyboardInterrupt:
        print("Ukončuji program.")
        if chrome_process:
            close_chrome()
        sys.exit(0)

if __name__ == '__main__':
    main()
