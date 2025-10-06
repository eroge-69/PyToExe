import math

def half_interval(a, b):
    return (a + b) / 2

def get_function():
    #раньше я думал просто в код вставлять функцию, ноооооооооооооооооо Артем Андреевич дал люлей и сказал вставлять функцию во время работы кода
    print("Введите функцию f(x) используя x как переменную")
    print("Пример: 2*math.log(x+7)-5*math.sin(x), math.sin(2 * x) - math.log(x),  4 * math.cos(x) + 0.3 * x ")
    print("Доступны функции из math: sin, cos, tan, log, sqrt, exp и др.")
    
    func_str = input("f(x) = ")
    
    def f(x):
        return eval(func_str, {'math': math, 'x': x})
    
    return f

def get_parameters():
    a = float(input("Введите точку a: "))
    b = float(input("Введите точку b: "))
    E = float(input("Введите точность E: "))
    return a, b, E

def start():
    func = get_function()
    a, b, E = get_parameters()
    counter = 0
    max_counter = 200

    print(f"\nНачало вычислений...")
    print(f"Интервал: [{a}, {b}]")
    print(f"Точность: {E}")

    while abs(b - a) > E:
        counter += 1
        if counter >= max_counter:
            print('Слишком много шагов')
            break

        fa = func(a)
        c = half_interval(a, b)
        fc = func(c)
        
        if abs(fc) < 1e-15:
            a = c
            b = c
            break
        
        if fa * fc < 0:
            b = c  
        else:
            a = c

       
        if counter % 10 == 0:
            print(f"Итерация {counter}, интервал: [{a:.6f}, {b:.6f}]")
    
    root = (a + b) / 2
    
    print(f'\nРЕЗУЛЬТАТ:')
    print(f'Корень: x ≈ {root:.15f}')
    print(f'f(x) ≈ {func(root):.15e}')
    print(f'Погрешность: {abs(b - a):.2e}')
    print(f'Итерации: {counter}')
    
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    start()
    # пж
    #  не бейте меня
    # я малю