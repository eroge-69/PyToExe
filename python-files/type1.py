import time

a = float(input("Введіть число a: "))
b = float(input("Введіть число b: "))
c = float(input("Введіть число c: "))

# Знаходимо найбільше число
if a >= b and a >= c:
    max_num = a
elif b >= a and b >= c:
    max_num = b
else:
    max_num = c

# Знаходимо найменше число
if a <= b and a <= c:
    min_num = a
elif b <= a and b <= c:
    min_num = b
else:
    min_num = c

# Обчислюємо суму
result = max_num + min_num

print(f"Найбільше число: {max_num}")
print(f"Найменше число: {min_num}")
print(f"Сума найбільшого і найменшого: {result}")

# Затримка перед закриттям
time.sleep(5)
