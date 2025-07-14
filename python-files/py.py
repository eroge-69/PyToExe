import random

num = random.randint(1,100)

lox = 1

while lox != 1:
    num2 = int(input("Какое число: "))
    if num2 > num:
        print("Число больше")
    if num2 < num:
        print("Число Меньше")
    if num2 == num:
        print("Угадал")
        lox = 0
        break
