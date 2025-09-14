import sys
import time
import signal
import os

def signal_handler(sig, frame):
    print("Закрытие невозможно.")

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while True:
    try:
        time.sleep(1)
    except:
        pass