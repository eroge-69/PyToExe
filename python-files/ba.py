import pandas as pd

date = []
names = []

while True:
    print("*" * 50)
    day_input = input("put your day here(1-31): \n")
    try:
        day = int(day_input)
        if day < 1 or day > 31:
            print("day will be 1-31!")
            continue
    except:
        print("day error")
        continue
    month_input = input("put your month here: \n")
    try:
        month = int(month_input)
        if month < 1 or month > 12:
            print("month will be 1-12!")
            continue
    except:
        print("month error")
        continue
    year_input = input("put your year here: \n")
    try:
        year = int(year_input)
    except:
        print("month error!")
        continue
    date.append(f"{year}/{month:02}/{day:02}")
    name = input("put name here: \n")
    lastname = input("put last name here: \n")
    names.append(f"{name} {lastname}")
    quit_input = input("do you want quite?y/n: \n")
    if quit_input.lower() == "y":
        break
input_filename=input("name of file: ")
df = pd.DataFrame({
    "نام و نام خانوادگی": names,
    "تاریخ": date
})
df.to_excel(input_filename+".xlsx", index=False)
input()