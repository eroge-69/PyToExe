def calculate_time():
    print("\n🧮 Калькулятор времени для пиксель-арта")
    print("----------------------------------------")
    
    try:
        # Запрос данных у пользователя
        total_pixels = int(input("Введите общее количество пикселей: "))
        time_per_pixel = int(input("Время на один пиксель (в секундах): "))
        people_count = int(input("Количество людей: "))
        hours_per_day = float(input("Сколько часов в день на арт?: "))
        
        # Проверка на корректность ввода
        if total_pixels <= 0 or time_per_pixel <= 0 or people_count <= 0 or hours_per_day <= 0:
            print("Ошибка: все значения должны быть положительными числами!")
            return
        
        # Вычисление общего времени в секундах
        total_time_seconds = (total_pixels * time_per_pixel) / people_count
        
        # Перевод в другие единицы
        total_time_minutes = total_time_seconds / 60
        total_time_hours = total_time_minutes / 60
        total_days = total_time_hours / hours_per_day
        
        # Вывод результатов
        print("\n🔮 Результаты расчета:")
        print("----------------------------------------")
        print(f"Общее время: {int(total_time_seconds)} секунд")
        print(f"Общее время: {total_time_minutes:.2f} минут")
        print(f"Общее время: {total_time_hours:.2f} часов")
        print(f"При работе по {hours_per_day} часов в день: {total_days:.2f} дней")
        
        # Дополнительно: вывод в формате дней:часов:минут
        days = int(total_days)
        remaining_hours = (total_days - days) * hours_per_day
        hours = int(remaining_hours)
        minutes = int((remaining_hours - hours) * 60)
        
        print(f"📅 В деталях: {days} дней, {hours} часов, {minutes} минут")
        
    except ValueError:
        print("Ошибка: пожалуйста, вводите только числа!")

def main():
    while True:
        calculate_time()
        
        # ⭐⭐⭐ ДОБАВЛЕНО: Возможность продолжить или выйти ⭐⭐⭐
        choice = input("\nХотите сделать еще один расчет? (да/нет): ").lower()
        if choice not in ['да', 'д', 'yes', 'y']:
            print("До свидания! 👋")
            break

# Запуск программы
if __name__ == "__main__":
    main()
