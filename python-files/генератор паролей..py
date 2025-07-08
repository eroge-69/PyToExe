from random import *
from time import *
def generate_password(length,chars):
    if len(chars) < length:
        for i in range(1,length):
            chars = chars + choice(chars)
            if len(chars) >= length:
                break
            else:
                continue
    return "".join(sample(chars,length))
digits = "0123456789"
lowercase_letters = "abcdefghijklmnopqrstuvwxyz"
uppercase_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
punctuation = "!#$%&*+-=?@^_"
chars = ""
while True:
    n = input("Количество паролей для генерации: ")
    if n.isdigit():
        n = int(n)
        break
    else:
        print("Введите число")
while True:
    length = str(int(input("Длина одного пароля: ")))
    if length.isdigit():
        length = int(length)
        break
    else:
        print("Введите число")
x1,xa,xA,x_,xi = None,None,None,None,None
while True:
    otv = input("Включать ли цифры?: ")
    if (otv.lower() == "да") or (otv.lower() == "нет"):
        if otv.lower() == "да":
            x1 = True
        else:
            x1 = False
        break
    else:
        print("Введите \"да\" или \"нет\".")
while True:
    otv = input("Включать ли прописные буквы?: ")
    if (otv.lower() == "да") or (otv.lower() == "нет"):
        if otv.lower() == "да":
            xa = True
        else:
            xa = False
        break
    else:
        print("Введите \"да\" или \"нет\".")
while True:
    otv = input("Включать ли строчные буквы?: ")
    if (otv.lower() == "да") or (otv.lower() == "нет"):
        if otv.lower() == "да":
            xA = True
        else:
            xA = False
        break
    else:
        print("Введите \"да\" или \"нет\".")
while True:
    otv = input("Включать ли символы !#$%&*+-=?@^_?: ")
    if (otv.lower() == "да") or (otv.lower() == "нет"):
        if otv.lower() == "да":
            x_ = True
        else:
            x_ = False
        if x1 or xa or xA or x_ or xi:
            break
        else:
            print("необходимо ввести хотябы одну граппу символов")
    else:
        print("Введите \"да\" или \"нет\".")
while True:
    otv = input("Исключать ли неоднозначные символы il1Lo0O ?: ")
    if (otv.lower() == "да") or (otv.lower() == "нет"):
        if otv.lower() == "да":
            xi = True
        else:
            xi = False
        break
    else:
        print("Введите \"да\" или \"нет\".")
if x1 == True:
    chars += digits
if xa == True:
    chars += lowercase_letters
if xA == True:
    chars += uppercase_letters
if x_ == True:
    chars += punctuation
if xi == True:
    chars = list(chars)
    for i in "il1Lo0O":
        chars.remove(i)
    chars = "".join(chars)
print(len(chars))
for _ in range(n):
    print(generate_password(length,chars))
sleep(1)
while True:
    K = input("Для завершения программы введите \"выход\": ")
    if K.lower() == "выход":
        break
    else:
        print("Неверный ввод")
