#Calendar program by Arjunan

days = " S  M Tu  W Th  F Sa"
months = ["January", "February", "March", "April",
          "May", "June", "July", "August", "September",
          "October", "November", "December"]

def leap(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

calendar_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
print("Year  Month :")
year, month = map(int, input().split())

output_year = year + month
e = 0
l = 20
q = 21
mth = 0

i = year // 4
j = year // 100
k = year // 400
if leap(year):
    first_day = (year + i - j + k + 6) % 7
    calendar_days[1] = 29
else:
    first_day = (year + i - j + k) % 7

dates = [[0 for _ in range(21)] for _ in range(20)]
for month_index in range(12):
    k = month_index // 3
    j = month_index % 3
    week = k * 5
    first_day = first_day % 7 + j * 7
    for day in range(1, calendar_days[month_index] + 1):
        dates[week][first_day] = day
        first_day += 1
        if first_day % 7 == 0 and day < calendar_days[month_index] and (week % 5 == 4):
            first_day = j * 7
            week = k * 5
        elif first_day % 7 == 0:
            first_day = j * 7
            week += 1

m = 0
k = 0
p = 0

if output_year > year:
    k = (month - 1) // 3 * 5
    l = k + 5
    p = (month - 1) % 3 * 7
    q = p + 7
else:
    print("\t\t\t\t   %4d" % year)

for i in range(k, l):
    if output_year == year:
        if i == 0 or i == 5 or i == 10 or i == 15:
            print("\n%15s\t\t%15s\t\t%15s" % (months[m], months[m + 1], months[m + 2]))
            m = m + 3
            print("   %s    %s    %s" % (days, days, days))
    elif  (e==0):
        e= 2
        print("\n       %s  %4d" % (months[month - 1], year))
        print("   %s" % days)
        
    for j in range(p, q):
        if j % 7 == 0:
            print("   ", end='')
        if dates[i][j] < 1:
            print("   ", end='')
        else:
            print("%2d " % dates[i][j], end='')
    print()