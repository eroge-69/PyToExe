import time
import random

def generate_code():
    part1 = str(random.randint(0, 9999)).zfill(4)
    part2 = str(random.randint(0, 99999)).zfill(5)
    part3 = str(random.randint(0, 9999)).zfill(4)
    return f"{part1}-{part2}-{part3}"
    
i = int(input("Enter card bin: "))

if i in ['4645', '4649', '4613']:
    print()
else:
    print('Invalid bin')
    exit()

try:
    b = int(input("Enter rest of the numbers"))
except:
    print("Failed")
    exit()

p = input("Enter proxy")
if p == "" or " ":
    print("Running on LOCAL proxy")
else:
    print(f"Using proxy: {p}")

print("Performing operations")    
time.sleep(15)

code = generate_code()
print("CODE GENERATED 50$ BINANCE " + code)

