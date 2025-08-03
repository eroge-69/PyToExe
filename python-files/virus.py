import time
from datetime import datetime

target = datetime(2025, 8, 6, 0, 0, 0)

while True:
    now = datetime.now()
    remaining = target - now

    if remaining.total_seconds() <= 0:
        print("Time's up!")
        break

    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"{hours}h {minutes}m {seconds}s left until the deadline")
    time.sleep(1)
