import math


def get_valid_coordinate(prompt):
    while True:
        try:
            value = input(prompt).replace(',', '.')
            if any(char.isalpha() for char in value):
                print("Ошибка ввода! Число не должно содержать букв!")
                continue
            return float(value)
        except ValueError:
            print("Ошибка ввода! Ввести нужно ЧИСЛО!")


def calculate_distance():
    print("\n1) Введите координаты первой точки.")
    x1 = get_valid_coordinate("Координата x первой точки (x1): ")
    y1 = get_valid_coordinate("Координата y первой точки (y1): ")

    print("\n2) Введите координаты второй точки.")
    x2 = get_valid_coordinate("Координата x второй точки (x2): ")
    y2 = get_valid_coordinate("Координата y второй точки (y2): ")

    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    print(f"\nРасстояние между точками ({x1}; {y1}) и ({x2}; {y2}) равно {distance:.5f}")


def main():
    while True:
        calculate_distance()

        while True:
            repeat = input("\nХотите повторить вычисление? (да/нет/y/n): ").lower()
            if repeat in ['да', 'нет', 'y', 'n']:
                break
            print('Пожалуйста, введите "да", "нет", "y" (что значит "yes") или "n" (что значит "no").')

        if repeat in ['нет', 'n']:
            print("Программа завершена!")
            break


if __name__ == "__main__":
    print("Программа для вычисления расстояния между двумя точками")
    main()