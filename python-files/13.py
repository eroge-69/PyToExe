import os
import time
import msvcrt



def clear_screen():
    """Очищает экран консоли."""
    os.system('cls' if os.name == 'nt' else 'clear')


def is_solvable(board, n):
    """Проверяет, имеет ли заданная конфигурация доски решение."""
    tiles = []
    empty_row = -1

    for i in range(n):
        for j in range(n):
            tile = board[i][j]
            if tile == 0:
                empty_row = i
            else:
                tiles.append(tile)

    inv_count = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inv_count += 1

    if n % 2 == 1:
        return inv_count % 2 == 0
    else:
        row_from_bottom = n - empty_row
        return (inv_count + row_from_bottom) % 2 == 1


def heuristic(board, n):
    """Вычисляет манхэттенское расстояние для текущего состояния."""
    h = 0
    for i in range(n):
        for j in range(n):
            num = board[i][j]
            if num != 0:
                target_row, target_col = divmod(num - 1, n)
                h += abs(i - target_row) + abs(j - target_col)
    return h


def solve_puzzle(start_board, n):
    """Основная функция решения головоломки с использованием IDA* алгоритма."""
    empty_pos = next(((i, j) for i in range(n) for j in range(n) if start_board[i][j] == 0), None)
    start = tuple(tuple(row) for row in start_board)
    threshold = heuristic(start, n)

    def search(node, empty, g, threshold, path):
        h_val = heuristic(node, n)
        f = g + h_val

        if f > threshold:
            return (f, None)
        if h_val == 0:
            return (f, path.copy())

        min_thresh = float('inf')
        directions = [('Up', (-1, 0)), ('Down', (1, 0)),
                      ('Left', (0, -1)), ('Right', (0, 1))]

        for move, (di, dj) in directions:
            ni, nj = empty[0] + di, empty[1] + dj

            if 0 <= ni < n and 0 <= nj < n:
                if path and ((path[-1] == 'Up' and move == 'Down') or
                             (path[-1] == 'Down' and move == 'Up') or
                             (path[-1] == 'Left' and move == 'Right') or
                             (path[-1] == 'Right' and move == 'Left')):
                    continue

                new_board = [list(r) for r in node]
                new_board[empty[0]][empty[1]], new_board[ni][nj] = new_board[ni][nj], 0
                new_board_tuple = tuple(map(tuple, new_board))
                res_thresh, res_path = search(new_board_tuple, (ni, nj), g + 1,
                                              threshold, path + [move])

                if res_path is not None:
                    return (res_thresh, res_path)
                if res_thresh < min_thresh:
                    min_thresh = res_thresh

        return (min_thresh, None)

    while True:
        res_thresh, result = search(start, empty_pos, 0, threshold, [])
        if result is not None:
            return result
        if res_thresh == float('inf'):
            return None
        threshold = res_thresh


def get_key():
    """Ожидает нажатия клавиши и возвращает её код."""
    return msvcrt.getch()


def print_board_with_highlight(board, n, current_pos, move_number, total_moves):
    """Красиво выводит доску с подсветкой текущего состояния."""
    print("┌" + "─" * (n * 6 - 1) + "┐")

    # Заголовок с номером хода
    header = f" ХОД {move_number}/{total_moves} "
    padding = (n * 6 - 1 - len(header)) // 2
    print("│" + " " * padding + header + " " * padding + "│")
    print("├" + "─" * (n * 6 - 1) + "┤")

    for i in range(n):
        print("│", end="")
        for j in range(n):
            if board[i][j] == 0:
                cell = "   ██   "
            else:
                cell = f"   {board[i][j]:2d}   "

            # Подсветка текущей позиции
            if (i, j) == current_pos:
                cell = f"\033[42m{cell}\033[0m"  # Зеленый фон
            elif board[i][j] == 0:
                cell = f"\033[44m{cell}\033[0m"  # Синий фон для пустой клетки

            print(cell, end="")
        print("│")
        if i < n - 1:
            print("├" + "─" * (n * 6 - 1) + "┤")

    print("└" + "─" * (n * 6 - 1) + "┘")


def print_controls():
    """Выводит информацию об управлении."""
    print("\n" + "═" * 50)
    print(" 🎮 УПРАВЛЕНИЕ:")
    print(" ⬅️  Стрелка ВЛЕВО  - предыдущий ход")
    print(" ➡️  Стрелка ВПРАВО - следующий ход")
    print(" 🔄 R - перезапуск")
    print(" 🚪 Q - выход")
    print("═" * 50)


def display_solution_interactive(initial_board, solution, n):
    """Интерактивный показ решения с управлением стрелочками."""
    if not solution:
        print("❌ Решение не найдено!")
        return

    current_step = 0
    total_steps = len(solution)

    # Создаем копию начальной доски
    current_board = [row[:] for row in initial_board]
    empty_pos = next(((i, j) for i in range(n) for j in range(n) if current_board[i][j] == 0), None)

    # Предварительно вычисляем все состояния
    board_states = [([row[:] for row in current_board], empty_pos)]

    for move in solution:
        di, dj = 0, 0
        if move == 'Up':
            di, dj = -1, 0
        elif move == 'Down':
            di, dj = 1, 0
        elif move == 'Left':
            di, dj = 0, -1
        elif move == 'Right':
            di, dj = 0, 1

        ni, nj = empty_pos[0] + di, empty_pos[1] + dj
        current_board[empty_pos[0]][empty_pos[1]] = current_board[ni][nj]
        current_board[ni][nj] = 0
        empty_pos = (ni, nj)

        board_states.append(([row[:] for row in current_board], empty_pos))

    # Основной цикл интерактивного показа
    while True:
        clear_screen()

        # Отображаем заголовок
        print("🎯 РЕШЕНИЕ ПЯТНАШЕК - ИНТЕРАКТИВНЫЙ РЕЖИМ")
        print("═" * 50)

        # Отображаем текущее состояние доски
        current_board, empty_pos = board_states[current_step]
        print_board_with_highlight(current_board, n, empty_pos, current_step, total_steps)

        # Отображаем информацию о текущем ходе
        if current_step > 0:
            print(f"\n📋 Последний ход: {solution[current_step - 1]}")
        else:
            print(f"\n📋 Начальное состояние")

        print_controls()

        # Ожидаем ввод пользователя
        key = get_key()

        if key == b'q' or key == b'Q':  # Выход
            break
        elif key == b'r' or key == b'R':  # Перезапуск
            current_step = 0
        elif key == b'M' or key == b'P':  # Стрелка вправо (следующий ход)
            if current_step < total_steps:
                current_step += 1
        elif key == b'K' or key == b'H':  # Стрелка влево (предыдущий ход)
            if current_step > 0:
                current_step -= 1
        # Обработка escape-последовательностей для стрелок
        elif key == b'\xe0':
            second_key = get_key()
            if second_key == b'M':  # Стрелка вправо
                if current_step < total_steps:
                    current_step += 1
            elif second_key == b'K':  # Стрелка влево
                if current_step > 0:
                    current_step -= 1
            elif second_key == b'P':  # Стрелка вниз (также следующий)
                if current_step < total_steps:
                    current_step += 1
            elif second_key == b'H':  # Стрелка вверх (также предыдущий)
                if current_step > 0:
                    current_step -= 1


def main():
    """Основная функция программы."""
    clear_screen()
    print("🎯 РЕШАТЕЛЬ ПЯТНАШЕК")
    print("═" * 50)

    try:
        n = int(input("📏 Введите размер поля (2-4): "))
        if n < 2 or n > 4:
            print("❌ Размер должен быть от 2 до 4!")
            return
    except ValueError:
        print("❌ Пожалуйста, введите число!")
        return

    print(f"\n📝 Введите начальное состояние поля {n}x{n}:")
    print("   (числа через пробел, 0 - пустая клетка)")
    print("─" * 40)

    board = []
    for i in range(n):
        while True:
            try:
                row_input = input(f"Строка {i + 1}: ").strip()
                if not row_input:
                    print("❌ Строка не может быть пустой!")
                    continue

                row = list(map(int, row_input.split()))
                if len(row) != n:
                    print(f"❌ Нужно ввести ровно {n} чисел!")
                    continue

                # Проверяем, что все числа в диапазоне 0..n²-1
                valid_numbers = set(range(n * n))
                if not all(num in valid_numbers for num in row):
                    print(f"❌ Числа должны быть от 0 до {n * n - 1}!")
                    continue

                # Проверяем уникальность чисел
                if len(set(row)) != len(row):
                    print("❌ Числа не должны повторяться!")
                    continue

                board.append(row)
                break
            except ValueError:
                print("❌ Пожалуйста, вводите только числа!")
            except KeyboardInterrupt:
                print("\n👋 Выход из программы...")
                return

    print("\n⏳ Проверяем разрешимость...")
    if not is_solvable(board, n):
        print("❌ Данная конфигурация не имеет решения!")
        print("💡 Попробуйте другую начальную расстановку.")
        return

    print("✅ Конфигурация разрешима!")
    print("⏳ Ищем решение... (это может занять некоторое время)")

    start_time = time.time()
    solution = solve_puzzle(board, n)
    end_time = time.time()

    if solution:
        solving_time = end_time - start_time
        print(f"✅ Решение найдено за {solving_time:.2f} секунд!")
        print(f"📊 Количество ходов: {len(solution)}")

        # Показываем краткую последовательность ходов
        print("\n🗺️  Краткая последовательность ходов:")
        compact_moves = []
        count = 1
        current_move = solution[0]

        for i in range(1, len(solution)):
            if solution[i] == current_move:
                count += 1
            else:
                if count > 1:
                    compact_moves.append(f"{count}×{current_move}")
                else:
                    compact_moves.append(current_move)
                current_move = solution[i]
                count = 1

        if count > 1:
            compact_moves.append(f"{count}×{current_move}")
        else:
            compact_moves.append(current_move)

        print(" → ".join(compact_moves))

        # Запускаем интерактивный режим
        input("\n🎮 Нажмите Enter для перехода в интерактивный режим...")
        display_solution_interactive(board, solution, n)

    else:
        print("❌ Не удалось найти решение!")
        print("💡 Возможно, произошла ошибка в алгоритме.")

    print("\n👋 Спасибо за использование решателя пятнашек!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Выход из программы...")