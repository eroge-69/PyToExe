# Практическая работа №3. Решение задач с использованием условного оператора
import math

# №1
print('1. Дано натуральное число. Определить оканчивается ли оно цифрой 7.')
number = int(input())
if number % 10 == 7:
    print('Число ', number, ' оканчивается на 7!')
else:
    print('Число', number, 'не оканчивается на 7!')

# №2
print('2. Дано двузначное число. Определить: а) является ли сумма его цифр двузначным числом; б) больше ли числа "a" сумма его цифр.')
two_digit_number = int(input())
digit_sum = (two_digit_number // 10) + (two_digit_number % 10)

if 9 < digit_sum < 100:
    print('Сумма цифр ', digit_sum, ' является двузначным числом.')
else:
    print('Сумма цифр ', digit_sum, ' не является двузначным числом.')

a = int(input('Введите число "а" для сравнения: '))
if digit_sum > a:
    print('Сумма цифр ', digit_sum, ' больше числа а = ',a)
else:
    print('Сумма цифр ', digit_sum, ' не больше числа а = ', a)

# №3
print('3. Определить, является ли треугольник со сторонами a, b, c: а) равносторонним; б) равнобедренным.')
side_a = float(input())
side_b = float(input())
side_c = float(input())

if side_a == side_b == side_c:
    print('Треугольник равносторонний!')
elif side_a == side_b or side_a == side_c or side_b == side_c:
    print('Треугольник равнобедренный!')
else:
    print('Проверьте стороны треугольника!')

# №4
print('4. Даны три целых числа. Вывести на экран те из них, которые являются четными.')
num1 = int(input())
num2 = int(input())
num3 = int(input())
print('Четные числа: ')
if num1 % 2 == 0:
    print(num1)
if num2 % 2 == 0:
    print(num2)
if num3 % 2 == 0:
    print(num3)

# №5
print('5. Даны три вещественных числа. Возвести в квадрат те из них, значения которых неотрицательны.')
real_num1 = float(input())
real_num2 = float(input())
real_num3 = float(input())
print('Результат: ')
if real_num1 >= 0:
    print(real_num1 ** 2)
if real_num2 >= 0:
    print(real_num2 ** 2)
if real_num3 >= 0:
    print(real_num3 ** 2)

# №6
print('6. Даны четыре вещественных числа. Определить, сколько из них отрицательных.')
count_negative = 0
n1 = float(input())
if n1 < 0:
    count_negative += 1
n2 = float(input())
if n2 < 0:
    count_negative += 1
n3 = float(input())
if n3 < 0:
    count_negative += 1
n4 = float(input())
if n4 < 0:
    count_negative += 1
print('Количество отрицательных чисел: ', count_negative)

# №7
print('7. Дано двузначное число. Определить: а) какая из его цифр больше: первая или вторая; б) одинаковы ли его цифры.')
two_digit_num = int(input())
first_digit = two_digit_num // 10
second_digit = two_digit_num % 10

if first_digit > second_digit:
    print('Первая цифра больше второй.')
elif second_digit > first_digit:
    print('Вторая цифра больше первой.')
else:
    print('Цифры одинаковы.')

# №8
print('8. Дано двузначное число. Определить: а) кратна ли трем сумма его цифр; б) кратна ли сумма его цифр числу "а".')
number_check = int(input())
sum_digits = (number_check // 10) + (number_check % 10)

if sum_digits % 3 == 0:
    print('Сумма цифр ', sum_digits,' кратна трем.')
else:
    print('Сумма цифр ', sum_digits,' не кратна трем.')

a_check = int(input('Введите число "а": '))
if a_check != 0 and sum_digits % a_check == 0:
    print(' Сумма цифр ', sum_digits,' кратна числу "а" ({a_check}).')
else:
    print(' Сумма цифр ', sum_digits,' не кратна числу "а" ({a_check}).')

# №9
print('9. Даны два числа. Если квадратный корень из второго числа меньше первого числа, то увеличить второе число в пять раз.')
first_number = float(input())
second_number = float(input())
if second_number >= 0 and math.sqrt(second_number) < first_number:
    second_number *= 5
print('Результат для второго числа: ', second_number)

# №10
print('10. Даны три вещественных числа. Вывести на экран те из них, которые принадлежат интервалу [1.6, 3.8].')
r_num1 = float(input())
r_num2 = float(input())
r_num3 = float(input())
print('Числа в интервале [1.6, 3.8]: ')
if 1.6 <= r_num1 <= 3.8:
    print(r_num1)
if 1.6 <= r_num2 <= 3.8:
    print(r_num2)
if 1.6 <= r_num3 <= 3.8:
    print(r_num3)

# №11
print('11. Даны целые положительные числа a, b, c. Если существует треугольник со сторонами a, b, c, то определить, является ли он прямоугольным.')
side_val_a = int(input())
side_val_b = int(input())
side_val_c = int(input())
# проверка существования треугольника
if (side_val_a + side_val_b > side_val_c) and (side_val_a + side_val_c > side_val_b) and (side_val_b + side_val_c > side_val_a):
    # теорема пифагора
    if (side_val_a**2 + side_val_b**2 == side_val_c**2) or \
       (side_val_a**2 + side_val_c**2 == side_val_b**2) or \
       (side_val_b**2 + side_val_c**2 == side_val_a**2):
        print('Треугольник существует и он прямоугольный.')
    else:
        print('Треугольник существует, но он не прямоугольный.')
else:
    print('Проверьте стороны треугольника!')