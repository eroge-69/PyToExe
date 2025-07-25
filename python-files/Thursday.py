import math

def calculate_triangle_properties(a, b, c):
    # Проверка существования треугольника
    if not (a + b > c and a + c > b and b + c > a):
        return None
    
    # Вычисление углов по теореме косинусов (в радианах)
    alpha = math.acos((b**2 + c**2 - a**2) / (2 * b * c))
    beta = math.acos((a**2 + c**2 - b**2) / (2 * a * c))
    gamma = math.acos((a**2 + b**2 - c**2) / (2 * a * b))
    
    # Перевод углов в градусы
    alpha_deg = math.degrees(alpha)
    beta_deg = math.degrees(beta)
    gamma_deg = math.degrees(gamma)
    
    # Вычисление высот
    h_a = 2 * (math.sqrt(s * (s - a) * (s - b) * (s - c))) / a
    h_b = 2 * (math.sqrt(s * (s - a) * (s - b) * (s - c))) / b
    h_c = 2 * (math.sqrt(s * (s - a) * (s - b) * (s - c))) / c
    
    # Вычисление медиан
    m_a = 0.5 * math.sqrt(2 * b**2 + 2 * c**2 - a**2)
    m_b = 0.5 * math.sqrt(2 * a**2 + 2 * c**2 - b**2)
    m_c = 0.5 * math.sqrt(2 * a**2 + 2 * b**2 - c**2)
    
    return {
        'angles': {
            'α': alpha_deg,
            'β': beta_deg,
            'γ': gamma_deg
        },
        'heights': {
            'hₐ': h_a,
            'h_b': h_b,
            'h_c': h_c
        },
        'medians': {
            'mₐ': m_a,
            'm_b': m_b,
            'm_c': m_c
        }
    }

def print_results(props):
    if props is None:
        print("Треугольник с такими сторонами не существует!")
        return
    
    print("\nРезультаты расчётов:")
    print("---------------------")
    print("Углы (в градусах):")
    for angle, value in props['angles'].items():
        print(f"{angle}: {value:.2f}°")
    
    print("\nВысоты:")
    for height, value in props['heights'].items():
        print(f"{height}: {value:.2f}")
    
    print("\nМедианы:")
    for median, value in props['medians'].items():
        print(f"{median}: {value:.2f}")

# Основная программа
print("Расчёт параметров треугольника")
print("Введите длины сторон:")
a = float(input("Сторона a = "))
b = float(input("Сторона b = "))
c = float(input("Сторона c = "))

# Полупериметр для формулы Герона
s = (a + b + c) / 2

props = calculate_triangle_properties(a, b, c)
print_results(props)

# Для создания bat-файла:
with open('run_triangle.bat', 'w') as f:
    f.write("@echo off\n")
    f.write("python triangle_props.py\n")
    f.write("pause\n")