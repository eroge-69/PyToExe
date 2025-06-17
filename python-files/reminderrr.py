import time
from plyer import notification

def remind():
    while True:
        notification.notify(
            title="Eye Strain Reminder",
            message="Look away!",
            timeout=10  # seconds
        )
        time.sleep(25 * 60)  # wait 25 minutes

if __name__ == "__main__":
    remind()
