import numpy as np
import matplotlib.pyplot as plt

class Polynomial:
    def __init__(self, a0: float = 0, a1: float = 0, a2: float = 0):
        self.a0 = a0  # свободный член
        self.a1 = a1  # коэффициент при x
        self.a2 = a2  # коэффициент при x²

def safe_input_int(prompt: str, min_val: int, max_val: int) -> int:
    """Безопасный ввод целого числа с проверкой диапазона"""
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"Ошибка: число должно быть между {min_val} и {max_val}")
        except ValueError:
            print("Ошибка: введите корректное целое число")

def safe_input_float(prompt: str) -> float:
    """Безопасный ввод вещественного числа"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите корректное число")

def linear_approximation(x: np.ndarray, y: np.ndarray) -> Polynomial:
    """Линейная аппроксимация методом наименьших квадратов"""
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x * x)
    
    # Решение системы уравнений
    a1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    a0 = (sum_y - a1 * sum_x) / n
    
    return Polynomial(a0, a1, 0)

def quadratic_approximation(x: np.ndarray, y: np.ndarray) -> Polynomial:
    """Квадратичная аппроксимация методом наименьших квадратов"""
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x * x)
    sum_x3 = np.sum(x ** 3)
    sum_x4 = np.sum(x ** 4)
    sum_x2y = np.sum(x * x * y)
    
    # Матрица коэффициентов
    A = np.array([
        [n, sum_x, sum_x2],
        [sum_x, sum_x2, sum_x3],
        [sum_x2, sum_x3, sum_x4]
    ])
    
    # Вектор свободных членов
    b = np.array([sum_y, sum_xy, sum_x2y])
    
    # Решение системы уравнений
    solution = np.linalg.solve(A, b)
    return Polynomial(solution[0], solution[1], solution[2])

def calculate_error(x: np.ndarray, y: np.ndarray, p: Polynomial) -> float:
    """Вычисление среднеквадратичной погрешности"""
    y_approx = p.a0 + p.a1 * x + p.a2 * x * x
    return np.sqrt(np.mean((y - y_approx) ** 2))

def plot_approximation(x: np.ndarray, y: np.ndarray, 
                      linear: Polynomial, quadratic: Polynomial):
    """Построение графиков"""
    # Создание точек для построения графиков
    x_plot = np.linspace(min(x) - 0.1 * (max(x) - min(x)),
                        max(x) + 0.1 * (max(x) - min(x)), 100)
    y_linear = linear.a0 + linear.a1 * x_plot
    y_quadratic = quadratic.a0 + quadratic.a1 * x_plot + quadratic.a2 * x_plot * x_plot

    # Настройка графика
    plt.figure(figsize=(10, 6))
    plt.grid(True)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Аппроксимация данных')

    # Построение графиков
    plt.scatter(x, y, color='red', label='Исходные точки')
    plt.plot(x_plot, y_linear, 'b-', label='Линейная аппроксимация')
    plt.plot(x_plot, y_quadratic, 'g-', label='Квадратичная аппроксимация')

    plt.legend()
    plt.show()

def main():
    print("=== Программа численной аппроксимации ===\n")

    # Ввод количества точек
    n = safe_input_int("Введите количество точек (2-100): ", 2, 100)

    # Ввод координат точек
    x = np.zeros(n)
    y = np.zeros(n)
    print("\nВвод координат точек:")
    
    for i in range(n):
        print(f"\nТочка {i + 1}:")
        x[i] = safe_input_float("x: ")
        y[i] = safe_input_float("y: ")

    # Вычисление аппроксимаций
    linear = linear_approximation(x, y)
    quadratic = quadratic_approximation(x, y)

    # Вычисление погрешностей
    linear_error = calculate_error(x, y, linear)
    quadratic_error = calculate_error(x, y, quadratic)

    # Вывод результатов
    print("\n=== Результаты аппроксимации ===")
    
    print("\nЛинейная аппроксимация:")
    print(f"y = {linear.a1:.4f}x + {linear.a0:.4f}")
    print(f"Среднеквадратичная погрешность: {linear_error:.4f}")
    print("\nКвадратичная аппроксимация:")
    print(f"y = {quadratic.a2:.4f}x² + {quadratic.a1:.4f}x + {quadratic.a0:.4f}")
    print(f"Среднеквадратичная погрешность: {quadratic_error:.4f}")

    # Построение графиков
    plot_approximation(x, y, linear, quadratic)

if __name__ == "__main__":
    main()