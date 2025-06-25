import os
import time
import subprocess  # Fixed typo: 'subpocess' -> 'subprocess'

def shutdown_and_cancel():
    while True:  # Fixed typo: 'Tue' -> 'True'
        # Shutdown system
        os.system("shutdown /s /f /t 5")  # 5 second timer
        print("Shutdown initiated....")  # Fixed typo: 'pint' -> 'print'

        # Wait 1 second
        time.sleep(1)

        # Cancel shutdown
        os.system("shutdown /a")  # Stops shutdown
        print("Shutdown aborted")  # Fixed typo: 'pint' -> 'print'

        # Wait 1 second
        time.sleep(1)

if __name__ == "__main__":  # Fixed syntax: 'if__name__' -> 'if __name__'
    shutdown_and_cancel()
