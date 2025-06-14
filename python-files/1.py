def is_prime(n):
    """
    Проверяет, является ли число n простым.
    Условия:
      - Числа меньше 2 не являются простыми.
      - 2 и 3 — простые.
      - Числа, делящиеся на 2 или 3, не простые (кроме 2 и 3).
      - Проверка делителей до корня из n с шагом 6.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# Ввод данных
n = int(input("Введите количество элементов в массиве: "))
arr = list(map(int, input("Введите элементы массива через пробел: ").split()))
m = int(input("Введите число m: "))

# Обработка элементов массива
print("Элементы, чей остаток от деления на m — простое число:")
for index, value in enumerate(arr):
    remainder = value % m  # Вычисление остатка
    if remainder < 2:  # Простые числа начинаются с 2
        continue
    if is_prime(remainder):
        print(f"Индекс: {index}, Значение: {value}, Остаток: {remainder}")
