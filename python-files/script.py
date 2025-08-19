import random
r = random.randint(1,100)
attempts_count = 10
print("Загадано число от 1 до 100")
print(f"У тебя есть {attempts_count} попыток")
for i in range(attempts_count):
    a = input("Давай кабанчиком вводи ")
    while not a.isdigit():
        print("Ты тупой? Введи еще раз")
        a = input("Давай кабанчиком вводи ")
    a = int(a)
    if a == r:
        print("Красавчик!")
        break
    if a < r:
        print("Мое число больше чем введенное")
        continue
    if a > r:
        print("Мое число меньше чем введенное")
if a != r:
    print("хуесос")
