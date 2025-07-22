
import time
import ctypes

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep():
    print("Running... Your computer will stay awake. Press Ctrl+C to stop.")
    try:
        while True:
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
            time.sleep(30)
    except KeyboardInterrupt:
        print("Stopped. Your computer may now sleep as per system settings.")

if __name__ == "__main__":
    prevent_sleep()
