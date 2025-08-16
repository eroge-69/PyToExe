import os
import time
def shutdown_after_delay(seconds):
    print(f"Shutdown will occur in {seconds} seconds. Press Ctrl+C to cancel.")
    try:
        time.sleep(seconds)
        os.system("shutdown /s /t 0")
        os.system("shutdown -h now")
    except KeyboardInterrupt:
        print("Shutdown cancelled.")