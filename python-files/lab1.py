# -*- coding: utf-8 -*-

#проверка ввода
def input_():
    while True:
        try:
            return float(input())
        except ValueError:
            print("Ошибка. Введите число.")

#1 вектор
print("Введите x1 для вектора a: ")
x1 = input_()
print("Введите y1 для вектора a: ")
y1 = input_()
print("Введите z1 для вектора a: ")
z1 = input_()

#2 вектор
print("Введите x2 для вектора b: ")
x2 = input_()
print("Введите y2 для вектора b: ")
y2 = input_()
print("Введите z2 для вектора b: ")
z2 = input_()

# Вычисление
dx = x2 - x1
dy = y2 - y1
dz = z2 - z1

# Вывод результата
print("Координаты вектора d: (%f, %f, %f)" % (dx, dy, dz))
