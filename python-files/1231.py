# Программа для сложения двух чисел с обработкой ошибок

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: Введите корректное число.")

# Запрос ввода первого числа
num1 = get_number("Введите первое число: ")

# Запрос ввода второго числа
num2 = get_number("Введите второе число: ")

# Сложение чисел
result = num1 + num2

# Вывод результата
print(f"Результат сложения: {result}")