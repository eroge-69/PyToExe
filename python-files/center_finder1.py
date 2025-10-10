# center_finder.py
import numpy as np
from scipy.optimize import minimize

def calculate_centroid(vertices):
    # Функция для расчета суммы расстояний
    def distance_sum(point):
        return sum(np.linalg.norm(point - v) for v in vertices)
    
    # Начальная точка - центр масс
    initial_point = np.mean(vertices, axis=0)
    
    # Оптимизация
    result = minimize(
        fun=distance_sum,
        x0=initial_point,
        method='BFGS',
        tol=1e-6,
        options={'maxiter': 1000}
    )
    
    return result.x, result.fun

def main():
    # Пример использования
    try:
        # Ввод координат вершин
        vertices_input = input("Введите координаты вершин через пробел (x1 y1 x2 y2 ...): ")
        vertices = np.array(list(map(float, vertices_input.split()))).reshape(-1, 2)
        
        center, distance = calculate_centroid(vertices)
        print(f"\nНайденный центр: ({center[0]:.4f}, {center[1]:.4f})")
        print(f"Минимальная сумма расстояний: {distance:.4f}")
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")

if __name__ == "__main__":
    main()