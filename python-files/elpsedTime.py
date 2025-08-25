import os
import math
from datetime import datetime

def round_up_to_two_decimals(number):
    return math.ceil(number * 100) / 100
    
def time_diff(t1: str, t2: str) -> float:
    fmt = "%H:%M"
    time1 = datetime.strptime(t1, fmt)
    time2 = datetime.strptime(t2, fmt)

    diff = time2 - time1
    return round_up_to_two_decimals(diff.total_seconds() / 3600)

start_time = input("Enter The Start Time: ")
end_time = input("Enter The End Time: ")

print(f"Elapsed Time: {time_diff(start_time, end_time)}")

os.system("pause")
