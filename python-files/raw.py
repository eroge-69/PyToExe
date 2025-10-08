
from datetime import datetime

hr, mi = 10, 5

num = 3
db = 1
while True:
    if datetime.now().hour >= hr and datetime.now().minute >= mi: exit()

    prime = True
    for i in range(2,num):
        if (num%i==0):
            prime = False
    if prime:
        db += 1
        print (db, num)
    num += 2