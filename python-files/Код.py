# Основные функции для расчета параметров размещения
def L(sv, cr, n):
    s1, s2 = 0, 0
    for i in range(9):
        if i != n and sv[n][i] != 0:
            d = abs(cr[n][0] - cr[i][0]) + abs(cr[n][1] - cr[i][1])
            s1 += d * sv[n][i]
            s2 += sv[n][i]
    return s1 / s2 if s2 != 0 else 0

def st(sv, cr, n):
    s, t = 0, 0
    p = 0
    for i in range(9):
        if sv[n][i] != 0:
            t += cr[i][1] * sv[n][i]
            s += cr[i][0] * sv[n][i]
            p += sv[n][i]
    return round(s/p, 3) if p != 0 else 0, round(t/p, 3) if p != 0 else 0

# Визуализация размещения вершин на сетке
def print_grid(coor):
    grid = [[0,0,0],[0,0,0],[0,0,0]]
    for i, (x, y) in enumerate(coor):
        grid[y][x] = i + 1
    for row in grid:
        print(' '.join(map(str, row)))

def find_vertex_at_coord(coor, target_coord):
    for i, coord in enumerate(coor):
        if coord == target_coord:
            return i
    return -1

# Исходные данные: матрица связей и начальные координаты
svaz = [
    [0, 2, 0, 3, 1, 0, 0, 0, 0],
    [2, 0, 1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 5, 0, 0],
    [3, 0, 0, 0, 2, 7, 0, 0, 0],
    [1, 0, 0, 2, 0, 2, 0, 1, 0],
    [0, 0, 0, 7, 2, 0, 0, 1, 0],
    [0, 0, 5, 0, 0, 0, 0, 0, 3],
    [0, 1, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 3, 0, 0]]
coor = [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0,2],[1,2],[2,2]]

# Основной цикл оптимизации размещения
iteration = 1
max_iterations = 10
while iteration <= max_iterations:
    print(f"=== Итерация {iteration} ===")
    print("Текущие позиции:")
    print_grid(coor)
    
    # Расчет текущих значений критерия для всех вершин
    Li = [round(L(svaz, coor, i), 3) for i in range(9)]
    print(f"\nL1={Li[0]}\nL2={Li[1]}\nL3={Li[2]}\nL4={Li[3]}\nL5={Li[4]}\nL6={Li[5]}\nL7={Li[6]}\nL8={Li[7]}\nL9={Li[8]}")
    
    # Поиск вершины с наихудшим значением критерия
    n_max = Li.index(max(Li))
    print(f"\nНаибольший L у x{n_max+1} (L={Li[n_max]})")
    
    # Расчет центра тяжести для улучшения размещения
    s_c, t_c = st(svaz, coor, n_max)
    print(f"Центр тяжести для x{n_max+1}: s={s_c}, t={t_c}")
    
    # Перебор возможных перестановок с соседними вершинами
    sv_n_max = [i for i in range(9) if svaz[n_max][i] != 0]
    improvements = []
    
    print("\nВычисление перестановок:")
    for j in sv_n_max:
        temp_coor = [coord[:] for coord in coor]
        temp_coor[n_max], temp_coor[j] = temp_coor[j], temp_coor[n_max]
        
        L_j_new = round(L(svaz, temp_coor, j), 3)
        L_n_max_new = round(L(svaz, temp_coor, n_max), 3)
        sigma_j = Li[j] - L_j_new
        sigma_n_max = Li[n_max] - L_n_max_new
        delta = sigma_n_max + sigma_j
        improvements.append((j, delta, L_j_new, L_n_max_new, sigma_j, sigma_n_max))
        print(f"L{j+1}{n_max+1}={L_j_new}")
        print(f"L{n_max+1}{j+1}={L_n_max_new}")
        print(f"σ{j+1}{n_max+1}={sigma_j:.3f}\nσ{n_max+1}{j+1}={sigma_n_max:.3f}\nδ={delta:.3f}\n")

    # Применение наилучшей найденной перестановки
    if improvements:
        best_j, best_delta, _, _, _, _ = max(improvements, key=lambda x: x[1])
        if best_delta > 0:
            print(f"Меняем местами вершины {n_max+1} и {best_j+1}\n")
            coor[n_max], coor[best_j] = coor[best_j], coor[n_max]
        else:
            print("Улучшений не найдено\n")
            break
    else:
        print("\nНет кандидатов для перестановки")
        break
    iteration += 1

# Вывод финального результата
print(f"\nФинальное размещение после {iteration-1} итераций:")
print_grid(coor)

# Расчет суммарной длины соединений
total_length = 0
for i in range(9):
    for j in range(i+1, 9):
        if svaz[i][j] > 0:
            d = abs(coor[i][0] - coor[j][0]) + abs(coor[i][1] - coor[j][1])
            total_length += d * svaz[i][j]
print(f"Суммарная длина соединений: L(G) = {total_length}")
