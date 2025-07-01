# [ширина шины памяти] * [частота памяти] = [х бит пропуск] / [бит в байте (8бит) ] 
# Т. е. пропускная способность равна 51.2 Гб/сек.
print("Расчет пропускной способности видеокарты.")
print("Copyright (c) 2025. Crumagaming\n")
a = 0;
b = 0;

while True:
    try:
        a = int(input('Разрядность Шины памяти: '))
        break
    except ValueError:
        print("Вы ввели не число. Попробуйте снова: ")

while True:
    try:
        b = int(input('Частота памяти: '))
        break
    except ValueError:
        print("Вы ввели не число. Попробуйте снова: ")

result = a * b // 8

print("Пропускная способность равна " + str(result).rstrip('0') +" Гб/сек.")