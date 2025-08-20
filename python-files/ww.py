import datetime
from datetime import date

def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

# Get the current date
base_date = datetime.datetime(2025, 8, 18)
current_ww = 34
current_date = date.today()
diff = days_between(current_date.strftime("%Y-%m-%d"), base_date.strftime("%Y-%m-%d"))

print("Current Diff is: ")
print(diff)

if diff >= 7:
    current_ww = current_ww + 1

# Print the current date
#print(base_date.strftime("%x"))


print("Current Workweek is: ")
print(current_ww)