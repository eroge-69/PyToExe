import time
from datetime import datetime

# تاریخ هدف: 1 مهر 1404 = 23 سپتامبر 2025، ساعت 07:00 صبح
target = datetime(2025, 9, 23, 7, 0, 0)

while True:
    now = datetime.now()
    delta = target - now

    if delta.total_seconds() <= 0:
        print("مدارس باز شدند! 🎉")
        break

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"\rمدارس بازگشایی تا: {days} روز، {hours} ساعت، {minutes} دقیقه، {seconds} ثانیه ⏳", end="")
    time.sleep(1)
