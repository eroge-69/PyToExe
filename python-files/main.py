import psutil
import time
import ctypes

def show_notification(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Alert battery", 0x30)

while True:
    battery = psutil.sensors_battery()
    plugged = battery.power_plugged

    if battery.percent >= 80 and plugged:
        show_notification(f"Battery percentage is above fucking 80🔋\n"
                          f"stop charging")
    elif battery.percent < 71:
        show_notification(f"Battery percentage is below fucking 20🔋\n"
                          f"Please charge the laptop")

    time.sleep(10) #1 minute and 40 seconds