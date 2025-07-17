from pysmu import Session
import time
import math
import sys
from datetime import datetime

# ====== Print Your Info ======
print(" ADALM1000  ")
print(" Author : Prince Kumar ")
print(" About  : Electronics Student at IIT Madras ")
print(" Date   :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(" Function: Generate 1 Hz Sine Wave on Channel A ")

# ====== Read Frequency Argument ======
if len(sys.argv) > 1:
    try:
        frequency = float(sys.argv[1])
    except ValueError:
        print("Invalid frequency! Using default 1 Hz.")
        frequency = 1
else:
    frequency = 1

# ====== ADALM1000 Setup ======
session = Session()
device = session.devices[0]
channel = device.channels['A']
channel.mode = 'SVMI'

# ====== Generate Waveform ======
amplitude = 2.5
offset = 2.5
sampling_rate = 1000
samples_per_cycle = int(sampling_rate / frequency)
waveform = [offset + amplitude * math.sin(2 * math.pi * i / samples_per_cycle) for i in range(samples_per_cycle)]

print(f" Outputting {frequency} Hz sine wave on Channel A...")
print(" Press Ctrl+C to stop.\n")

try:
    while True:
        for v in waveform:
            channel.voltage = v
            time.sleep(1 / sampling_rate)
except KeyboardInterrupt:
    channel.voltage = 0
    print("\nStopped output.")
