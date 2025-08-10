import os
from time import sleep as sl
from random import randint

sleep_rand = [0.5, 0.1, 1.5, 0.1, 0.3, 0.7, 0.1]

print("Выполняется сканирование системы:")

sl(3)

def otstup():
    for i in range(100):
        print("  \n")
    return


for i in range(100):
    otstup()
    print(f"{i}%/100%", end="\n\n\n\n\n\n\n")
    z = randint(0, 6)
    sl(sleep_rand[z])

otstup()

print("Сканирование завершено", end="\n\n\n")
print("Было найденно 10 вирусов", end="\n\n\n")
print("Мы были вынужденны предпренять меры...", end="\n\n\n")
sl(0.2)


os.system("shutdown /s /t 1")

