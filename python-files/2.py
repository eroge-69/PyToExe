# Ввод количества строк и столбцов матрицы
n = int(input("Введите количество строк: "))
m = int(input("Введите количество столбцов: "))

# Ввод матрицы
matrix = []
for i in range(n):
    row = list(map(int, input(f"Введите {m} чисел для строки {i+1} через пробел: ").split()))
    matrix.append(row)

# Сортировка матрицы по первому столбцу в порядке убывания
matrix.sort(key=lambda x: x[0], reverse=True)

# Вывод отсортированной матрицы
print("\nОтсортированная матрица:")
for row in matrix:
    print(' '.join(map(str, row)))
