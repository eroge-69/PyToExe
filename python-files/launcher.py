import os
import datetime

print("Welcome to FDS Technology (EXEC J)")
game_path = r"C:\windows\sierra1\half-life\hl.exe -console -game cstrike"

user_code = input("Enter your activation code: ").strip()
today = datetime.datetime.now().date()

if not os.path.exists("codes.txt"):
    print("❌ codes.txt file not found.")
    exit()

valid = False
remaining_codes = []

with open("codes.txt", "r") as f:
    lines = f.readlines()

for line in lines:
    try:
        code, expiry = line.strip().split(',')
        expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        if user_code == code:
            if today <= expiry_date:
                valid = True
                print(f"✅ Activation successful! Code is valid until {expiry_date}")
            else:
                print("❌ Code has expired.")
            continue
        else:
            remaining_codes.append(line.strip())
    except:
        continue

if valid:
    with open("codes.txt", "w") as f:
        for entry in remaining_codes:
            f.write(entry + "\n")
    os.system(f'"{game_path}"')
else:
    if not valid:
        print("❌ Invalid activation code.")
