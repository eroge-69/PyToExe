'''

            Online Python Compiler.
    Code, Compile and Run python program online.
Write your code and press "Run" button to execute it.

'''
# Функция для сложения двух чисел
def add(x, y):
  """Возвращает сумму x и y."""
  return x + y

# Функция для вычитания двух чисел
def subtract(x, y):
  """Возвращает разность x и y."""
  return x - y

# Функция для умножения двух чисел
def multiply(x, y):
  """Возвращает произведение x и y."""
  return x * y

# Функция для деления двух чисел
def divide(x, y):
  """Возвращает частное x и y. Проверяет деление на ноль."""
  if y == 0:
    return "Деление на ноль!"
  else:
    return x / y

# Основной цикл калькулятора
while True:
  print("Выберите операцию:")
  print("1. Сложение")
  print("2. Вычитание")
  print("3. Умножение")
  print("4. Деление")
  print("5. Выход")

  choice = input("Введите номер операции (1-5): ")

  if choice in ('1', '2', '3', '4'):
    try:
      num1 = float(input("Введите первое число: "))
      num2 = float(input("Введите второе число: "))
    except ValueError:
      print("Некорректный ввод. Пожалуйста, введите число.")
      continue

    if choice == '1':
      print(num1, "+", num2, "=", add(num1, num2))
    elif choice == '2':
      print(num1, "-", num2, "=", subtract(num1, num2))
    elif choice == '3':
      print(num1, "*", num2, "=", multiply(num1, num2))
    elif choice == '4':
      print(num1, "/", num2, "=", divide(num1, num2))
  elif choice == '5':
    break
  else:
    print("Некорректный ввод. Пожалуйста, выберите операцию из списка.")
