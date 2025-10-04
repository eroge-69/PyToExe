def get_positive_number(prompt):
    """Функция для получения положительного числа от пользователя"""
    while True:
        try:
            value = float(input(prompt))
            if value >= 0:
                return value
            else:
                print("Пожалуйста, введите число больше или равное нулю.")
        except ValueError:
            print("Некорректный ввод. Пожалуйста, введите число.")

def get_month_days(month):
    """Функция для определения количества дней в месяце"""
    month_days = {
        1: 31,  # Январь
        2: 28,  # Февраль
        3: 31,  # Март
        4: 30,  # Апрель
        5: 31,  # Май
        6: 30,  # Июнь
        7: 31,  # Июль
        8: 31,  # Август
        9: 30,  # Сентябрь
        10: 31, # Октябрь
        11: 30, # Ноябрь
        12: 31  # Декабрь
    }
    
    if month == 2:
        # Проверка на високосный год
        year = get_positive_number("Введите год: ")
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
    
    return month_days.get(month, None)

def main():
    print("Калькулятор расчета коммуникаций")
    
    # Получаем данные от пользователя
    communications_per_month = get_positive_number("Введите количество коммуникаций в месяц: ")
    month = int(get_positive_number("Введите номер месяца (1-12): "))
    
    # Проверяем корректность номера месяца
    if month < 1 or month > 12:
        print("Ошибка: неверный номер месяца. Введите число от 1 до 12.")
        return
    
    total_days = get_month_days(month)
    
    if total_days is None:
        print("Ошибка при определении количества дней в месяце.")
        return
    
    weekend_days = get_positive_number(f"Введите количество желаемых выходных дней в месяце ({total_days} дней всего): ")
    
    # Проверяем, чтобы количество выходных не превышало общее количество дней
    if weekend_days > total_days:
        print("Ошибка: количество выходных дней не может превышать общее количество дней в месяце.")
        return
    
    working_days = total_days - weekend_days
    
    # Вычисляем среднее количество коммуникаций в день
    try:
        communications_per_day = communications_per_month / working_days
        print(f"\nСреднее количество коммуникаций в день: {communications_per_day:.2f}")
    except ZeroDivisionError:
        print("\nОшибка: деление на ноль. Количество рабочих дней не может быть равно нулю.")

if __name__ == "__main__":
    main()