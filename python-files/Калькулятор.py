def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y != 0:
        return x / y
    else:
        return "Ошибка: Деление на ноль!"

# Функция для выбора операции
def calculator():
    print("Выберите операцию:")
    print("1.Сложение")
    print("2.Вычитание")
    print("3.Умножение")
    print("4.Деление")
    
    choice = input("Введите номер операции (1/2/3/4): ")
    
    num1 = float(input("Введите первое число: "))
    num2 = float(input("Введите второе число: "))

    # Выполняем соответствующую операцию
    if choice == '1':
        print(f"{num1} + {num2} = {add(num1, num2)}")
    elif choice == '2':
        print(f"{num1} - {num2} = {subtract(num1, num2)}")
    elif choice == '3':
        print(f"{num1} * {num2} = {multiply(num1, num2)}")
    elif choice == '4':
        result = divide(num1, num2)
        print(result)
    else:
        print("Некорректный ввод операции!")

if __name__ == "__main__":
    while True:
        calculator()
        again = input("Хотите произвести ещё одну операцию? (y/n): ").lower()
        if again != 'y':
            break
