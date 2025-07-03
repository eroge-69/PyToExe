def generate_table(center_value, initial_weight, step_multiplier, weight_multiplier, steps_count):
    # Генератор правого ряда
    def right_values(center_value):
        current_step = 1.0
        local_center = center_value
        for _ in range(steps_count + 1):
            yield local_center
            local_center += current_step
            current_step *= step_multiplier  # Исправлено: было step_multiplier (опечатка)

    # Генератор левого ряда
    def left_values(center_value):
        current_step = 1.0  # Исправлено: начинаем с положительного шага
        local_center = center_value
        for _ in range(steps_count + 1):
            yield local_center
            local_center -= current_step  # Исправлено: просто вычитаем current_step
            current_step *= step_multiplier  # Исправлено: было step_multiplier (опечатка)

    # Проверка входных параметров
    if steps_count < 0:
        raise ValueError("Количество шагов должно быть неотрицательным")
    if initial_weight < 0:
        raise ValueError("Начальный вес должен быть неотрицательным")

    # Расчёт веса
    weights = [initial_weight * (weight_multiplier ** i) for i in range(steps_count + 1)]
    
    # Исправлено: экранирование табуляции и добавлены заголовки
    print("№ шага\tПравые значения\tЛевые значения\tВес")
    
    # Создаем генераторы один раз перед циклом
    right_gen = right_values(center_value)
    left_gen = left_values(center_value)
    
    for i in range(steps_count + 1):
        right_val = next(right_gen)
        left_val = next(left_gen)
        weight = weights[i]
        print(f"{i}\t{right_val:.6f}\t{left_val:.6f}\t{weight:.6f}")

if __name__ == "__main__":
    try:
        center_value = float(input("Центральное значение: "))
        initial_weight = float(input("Начальный вес: "))
        step_multiplier = float(input("Коэффициент увеличения шага: "))
        weight_multiplier = float(input("Коэффициент увеличения веса: "))
        steps_count = int(input("Количество шагов в обе стороны: "))
        
        if steps_count < 0:
            print("Ошибка: количество шагов должно быть неотрицательным")
        else:
            generate_table(center_value, initial_weight, step_multiplier, weight_multiplier, steps_count)
    except ValueError as e:
        print("Ошибка ввода:", str(e))