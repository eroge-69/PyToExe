import curses
import numpy as np
import random
import time

# Инициализация экрана
def init_screen(scr):
    global screen
    screen = scr.subwin(20, 30, 0, 0)
    screen.keypad(True)

# Определение фигур Тетриса и их вращения
shapes = [
    [[1, 1, 1, 1]],
    [[1, 0, 0, 0], [1, 1, 1, 1]],
    [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
    [[1, 1, 0, 0], [0, 1, 1, 0]],
    [[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [1, 1, 1, 1]],
    [[0, 0, 0, 1], [0, 0, 0, 1], [1, 1, 1, 1]]
]

rotations = [
    lambda x: np.rot90(x, axes=(1, 0)).T,
    lambda x: np.rot90(x, axes=(1, 0)) if random.random() < 0.5 else np.rot90(x, axes=(1, 0), k=2).T,
    lambda x: np.rot90(x, axes=(1, 0)),
    lambda x: np.rot90(x, axes=(1, 0)) if random.random() < 0.5 else np.rot90(x, axes=(1, 0), k=2).T,
    lambda x: np.rot90(x, axes=(1, 0)),
    lambda x: np.rot90(x, axes=(1, 0)) if random.random() < 0.5 else np.rot90(x, axes=(1, 0), k=2).T
]

# Отрисовка фигур на экране
def draw_figure(scr, figure, x, y):
    for i in range(len(figure)):
        for j in range(len(figure[i])):
            if figure[i][j]:
                scr.addch(y + i, x + j, curses.ACS_CKBOARD)

# Проверка столкновения фигуры с границами или уже размещенными блоками
def check_collision(scr, figure, x, y):
    for i in range(len(figure)):
        for j in range(len(figure[i])):
            if figure[i][j]:
                if (x + j < 0) or (x + j >= scr.getmaxyx()[1]) or \
                        (y + i >= scr.getmaxyx()[0]) or \
                        (screen.inch(y + i, x + j)[2] != curses.color_pair(0)):
                    return True
    return False

# Добавление фигур к уже размещенным блокам
def add_to_board(board, figure, x, y):
    for i in range(len(figure)):
        for j in range(len(figure[i])):
            if figure[i][j]:
                board[y + i][x + j] = 1

# Удаление полных строк из доски
def remove_full_rows(board):
    full_rows = []
    for i in range(len(board)):
        if np.all(board[i]):
            full_rows.append(i)
    for row in full_rows:
        del board[row]
        board.insert(0, [0] * len(board[0]))
    return len(full_rows)

# Основная функция игры
def game(scr):
    screen.clear()
    scr.refresh()

    board = np.zeros((20, 30), dtype=int)
    current_figure = random.choice(shapes)
    next_figure = random.choice(shapes)
    x, y = 5, 0

    while True:
        # Отрисовка доски и текущей фигуры
        screen.clear()
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j]:
                    screen.addch(i, j, curses.ACS_CKBOARD)
        draw_figure(screen, current_figure, x, y)
        screen.refresh()

        # Проверка столкновения и обработка ввода
        if check_collision(screen, current_figure, x, y):
            add_to_board(board, current_figure, x, y)

            # Проверка на проигрыш
            if y == 0:
                break

            # Удаление полных строк
            full_rows = remove_full_rows(board)
            if full_rows > 0:
                time.sleep(0.5)

            # Генерирование следующей фигуры
            current_figure = next_figure.copy()
            next_figure = random.choice(shapes)
            x, y = 5, 0

        # Обработка ввода
        key = screen.getch()

        if key == ord('a'):
            rotated = rotations[shapes.index(current_figure)](current_figure)
            if not check_collision(screen, rotated, x - 1, y):
                current_figure = rotated
                x -= 1

        elif key == ord('d'):
            rotated = rotations[shapes.index(current_figure)}(current_figure)
            if not check_collision(screen, rotated, x + 1, y):
                current_figure = rotated
                x += 1

        elif key == ord('w'):
            rotated = rotations[shapes.index(current_figure)](current_figure)
            if not check_collision(screen, rotated, x, y - 1):
                current_figure = rotated
                y -= 1

        elif key == ord('s'):
            if not check_collision(screen, current_figure, x, y + 1):
                y += 1

        # Сдвиг текущей фигуры вниз
        elif key in (curses.KEY_DOWN, b'\x0a'):
            if not check_collision(screen, current_figure, x, y + 1):
                y += 1
            else:
                add_to_board(board, current_figure, x, y)

                # Проверка на проигрыш
                if y == 0:
                    break

                # Удаление полных строк
                full_rows = remove_full_rows(board)
                if full_rows > 0:
                    time.sleep(0.5)

                # Генерирование следующей фигуры
                current_figure = next_figure.copy()
                next_figure = random.choice(shapes)
                x, y = 5, 0

    # Конец игры
    screen.clear()
    screen.addstr("Game Over!")
    screen.refresh()
    time.sleep(2)

# Точка входа в программу
if __name__ == "__main__":
    curses.wrapper(game)
