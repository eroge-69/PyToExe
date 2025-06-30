Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import numpy as np

def calculate_priority_matrix(comparison_matrix):
    """
    Вычисление вектора приоритетов методом геометрического среднего
    для матрицы парных сравнений.
    
    Аргументы:
    comparison_matrix: np.array - матрица парных сравнений (n x n)
    
    Возвращает:
    priority_vector: np.array - нормализованный вектор приоритетов
    """
    geom_means = np.exp(np.mean(np.log(comparison_matrix + 1e-9), axis=1))
    priority_vector = geom_means / np.sum(geom_means)
    return priority_vector

def classify_solutions(Q, g):
    """
    Классификация вариантов решений на допустимые, условно допустимые и недопустимые
    
    Аргументы:
    Q: np.array - матрица выполнения требований (требования x варианты)
    g: np.array - вектор уровней критичности требований
    
    Возвращает:
    admissible: list - индексы допустимых вариантов
    conditional: list - индексы условно допустимых вариантов
    inadmissible: list - индексы недопустимых вариантов
    """
    n_req, n_var = Q.shape
    admissible = []
    conditional = []
    inadmissible = []
    
    for j in range(n_var):
        # Проверка критических требований (уровень 3)
        critical_failed = any(Q[i, j] == 0 for i in range(n_req) if g[i] == 3)
        
        if critical_failed:
            inadmissible.append(j)
        else:
            # Проверка важных требований (уровень 2)
            important_failed = any(Q[i, j] == 0 for i in range(n_req) if g[i] == 2)
            
            if important_failed:
                conditional.append(j)
            else:
                admissible.append(j)
    
    return admissible, conditional, inadmissible

def calculate_complexity(alternative_matrices, criteria_matrix):
    """
    Вычисление сложности доработки вариантов
    
    Аргументы:
    alternative_matrices: list - список матриц парных сравнений для каждого требования
    criteria_matrix: np.array - матрица парных сравнений требований
    
    Возвращает:
    complexity: np.array - вектор сложности доработки для каждого варианта
    """
    n_var = alternative_matrices[0].shape[0]
    n_criteria = len(alternative_matrices)
    
    # Матрица локальных приоритетов (варианты x критерии)
    V = np.zeros((n_var, n_criteria))
    
    # Вычисление локальных приоритетов для каждого критерия
    for i, matrix in enumerate(alternative_matrices):
        V[:, i] = calculate_priority_matrix(matrix)
    
    # Вычисление весов критериев
    mu = calculate_priority_matrix(criteria_matrix)
    
    # Расчет сложности доработки
    complexity = V @ mu
    return complexity

def main():
    """Основная функция программы"""
    print("="*50)
    print("Программа для оптимизации выбора проектных решений")
    print("по реконструкции гидротехнических сооружений")
    print("="*50)
    
    # Пример данных для ГТС 2 (Советская Гавань)
    print("\nПример анализа для второго ГТС (г. Советская Гавань)")
    
    # Матрица выполнения требований (7 требований x 3 варианта)
    Q = np.array([
        [1, 1, 1],  # r1,2
        [1, 1, 1],  # r2,2
        [0, 1, 0],  # r3,2
        [0, 1, 1],  # r4,2
        [1, 0, 1],  # r5,2
        [1, 1, 0],  # r6,2
        [1, 1, 1]   # r7,2
    ])
    
    # Вектор критичности требований
    g = np.array([3, 2, 2, 2, 2, 1, 1])  # 3-критическое, 2-важное, 1-некритическое
    
    # Классификация вариантов
    adm, cond, inadm = classify_solutions(Q, g)
    
    print("\nРезультаты классификации вариантов:")
    print(f"Допустимые варианты: {adm}")
    print(f"Условно допустимые варианты: {cond}")
    print(f"Недопустимые варианты: {inadm}")
    
    # Если есть условно допустимые варианты, выполняем анализ сложности
    if cond:
        print("\nАнализ сложности доработки для условно допустимых вариантов")
        
        # Матрицы парных сравнений для каждого требования (3 варианта x 3 варианта)
        # Для r3,2
        matrix_r3 = np.array([
            [1, 9, 0.33],
            [0.11, 1, 0.11],
            [3, 9, 1]
        ])
        
        # Для r4,2
        matrix_r4 = np.array([
            [1, 9, 9],
            [0.11, 1, 1],
            [0.11, 1, 1]
        ])
        
        # Для r5,2
        matrix_r5 = np.array([
            [1, 0.11, 1],
            [9, 1, 9],
            [1, 0.11, 1]
        ])
        
        # Для r6,2
...         matrix_r6 = np.array([
...             [1, 1, 0.11],
...             [1, 1, 0.11],
...             [9, 9, 1]
...         ])
...         
...         # Матрица парных сравнений требований (4x4)
...         criteria_matrix = np.array([
...             [1, 0.25, 0.125, 0.5],
...             [4, 1, 0.5, 2],
...             [8, 2, 1, 4],
...             [2, 0.5, 0.25, 1]
...         ])
...         
...         # Список матриц для каждого требования
...         alternative_matrices = [matrix_r3, matrix_r4, matrix_r5, matrix_r6]
...         
...         # Расчет сложности доработки
...         complexity = calculate_complexity(alternative_matrices, criteria_matrix)
...         
...         # Вывод результатов
...         print("\nСложность доработки для каждого варианта:")
...         for i, c in enumerate(complexity):
...             print(f"Вариант a_{2},{i+1}: {c:.4f}")
...         
...         # Выбор оптимального варианта
...         optimal_idx = np.argmin(complexity)
...         print(f"\nОптимальный вариант: a_{2},{optimal_idx+1} со сложностью {complexity[optimal_idx]:.4f}")
...     
...     # Если есть допустимые варианты
...     elif adm:
...         print("\nНайдены допустимые варианты, не требующие доработки:")
...         for idx in adm:
...             print(f"- Вариант a_{2},{idx+1}")
...     
...     # Если нет допустимых или условно допустимых вариантов
...     else:
...         print("\nТребуется разработка новых вариантов реконструкции")
... 
... if __name__ == "__main__":
...     main()
