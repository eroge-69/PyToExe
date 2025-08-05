import random
import curses

# Инициализация экрана
screen = curses.initscr()
curses.curs_set(0)  # Скрыть курсор
height, width = 20, 60
win = curses.newwin(height, width, 0, 0)
win.keypad(1)
win.timeout(100)

# Начальная позиция змейки и еды
snake = [[10, 30], [10, 29], [10, 28]]
food = [random.randint(1, height-2), random.randint(1, width-2)]
win.addch(food[0], food[1], '*')

# Начальное направление
key = curses.KEY_RIGHT

while True:
    next_key = win.getch()
    key = key if next_key == -1 else next_key

    # Вычисляем новое положение головы
    head = [snake[0][0], snake[0][1]]

    if key == curses.KEY_DOWN:
        head[0] += 1
    elif key == curses.KEY_UP:
        head[0] -= 1
    elif key == curses.KEY_LEFT:
        head[1] -= 1
    elif key == curses.KEY_RIGHT:
        head[1] += 1

    # Проверка на столкновение со стеной или собой
    if (
        head in snake or
        head[0] in [0, height - 1] or
        head[1] in [0, width - 1]
    ):
        curses.endwin()
        quit()

    # Добавляем новую голову
    snake.insert(0, head)

    # Проверка на еду
    if head == food:
        food = [random.randint(1, height - 2), random.randint(1, width - 2)]
        win.addch(food[0], food[1], '*')
    else:
        tail = snake.pop()
        win.addch(tail[0], tail[1], ' ')

    # Отображаем голову
    win.addch(snake[0][0], snake[0][1], '#')