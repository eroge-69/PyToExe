import tkinter as tk
import random
from collections import deque

# --- Константы игры ---
WIDTH = 600  # Ширина игрового поля
HEIGHT = 400 # Высота игрового поля
GRID_SIZE = 20 # Размер одного "квадрата" (сегмента змейки, еды)
GAME_SPEED = 150 # Скорость игры в миллисекундах (меньше = быстрее)

SNAKE_COLOR = "#00FF00" # Зеленый цвет змейки
FOOD_COLOR = "#FF0000"  # Красный цвет еды
BG_COLOR = "#000000"    # Черный фон
TEXT_COLOR = "#FFFFFF"  # Белый цвет текста
GAME_OVER_TEXT_COLOR = "#FFD700" # Золотой цвет для текста "Игра окончена"

# --- Глобальные переменные игры ---
snake = deque() # Используем deque для эффективного добавления/удаления головы/хвоста
food = None
direction = "Right" # Начальное направление движения
score = 0
game_over = False
score_display = None # Объект для отображения счета на холсте

# --- Инициализация Tkinter ---
root = tk.Tk()
root.title("Змейка")
root.resizable(False, False) # Отключаем изменение размера окна

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG_COLOR)
canvas.pack()

# --- Функции игры ---

def start_new_game():
    """Инициализирует или перезапускает игру."""
    global snake, food, direction, score, game_over, score_display

    # Сброс игровых переменных
    snake.clear()
    # Начальная позиция змейки (3 сегмента в центре, двигаясь вправо)
    snake.append((WIDTH // 2, HEIGHT // 2))
    snake.append((WIDTH // 2 - GRID_SIZE, HEIGHT // 2))
    snake.append((WIDTH // 2 - 2 * GRID_SIZE, HEIGHT // 2))

    food = None
    direction = "Right"
    score = 0
    game_over = False

    canvas.delete("all") # Очищаем весь холст
    create_food()
    draw_snake()
    # Создаем или обновляем отображение счета
    score_display = canvas.create_text(WIDTH - 50, 20, text=f"Счет: {score}", fill=TEXT_COLOR, font=("Arial", 12, "bold"))

    game_loop() # Запускаем основной игровой цикл

def create_food():
    """Создает новую еду в случайной позиции."""
    global food
    while True:
        x = random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        # Убеждаемся, что еда не появляется внутри змейки
        if (x, y) not in snake:
            food = (x, y)
            break
    canvas.create_rectangle(x, y, x + GRID_SIZE, y + GRID_SIZE, fill=FOOD_COLOR, tag="food")

def draw_snake():
    """Отрисовывает змейку на холсте."""
    canvas.delete("snake") # Удаляем предыдущие сегменты змейки
    for x, y in snake:
        canvas.create_rectangle(x, y, x + GRID_SIZE, y + GRID_SIZE, fill=SNAKE_COLOR, tag="snake")

def move_snake():
    """Перемещает змейку."""
    global direction, score, game_over, food

    if game_over:
        return

    head_x, head_y = snake[0]

    # Вычисляем новую позицию головы на основе текущего направления
    if direction == "Up":
        new_head = (head_x, head_y - GRID_SIZE)
    elif direction == "Down":
        new_head = (head_x, head_y + GRID_SIZE)
    elif direction == "Left":
        new_head = (head_x - GRID_SIZE, head_y)
    elif direction == "Right":
        new_head = (head_x + GRID_SIZE, head_y)
    else:
        new_head = (head_x, head_y) # Этого не должно происходить

    snake.appendleft(new_head) # Добавляем новую голову в начало deque

    # Проверяем, съела ли змейка еду
    if new_head == food:
        score += 1
        canvas.itemconfig(score_display, text=f"Счет: {score}") # Обновляем счет
        canvas.delete("food") # Удаляем старую еду
        create_food() # Создаем новую еду
    else:
        snake.pop() # Удаляем хвост, если змейка не ела (чтобы она двигалась, не увеличиваясь)

def check_collisions():
    """Проверяет столкновения змейки со стенами или самой собой."""
    global game_over
    head_x, head_y = snake[0]

    # Столкновение со стенами
    if not (0 <= head_x < WIDTH and 0 <= head_y < HEIGHT):
        game_over = True
        return

    # Столкновение с самой собой (голова столкнулась с любым другим сегментом)
    # Используем list(snake)[1:] для создания списка без головы для проверки
    if (head_x, head_y) in list(snake)[1:]:
        game_over = True
        return

def display_game_over():
    """Отображает сообщение "Игра окончена"."""
    canvas.create_text(
        WIDTH / 2, HEIGHT / 2 - 20,
        text=f"Игра окончена! Счет: {score}",
        fill=GAME_OVER_TEXT_COLOR,
        font=("Arial", 24, "bold")
    )
    canvas.create_text(
        WIDTH / 2, HEIGHT / 2 + 20,
        text="Нажмите 'R' для перезапуска",
        fill=TEXT_COLOR,
        font=("Arial", 16)
    )

def game_loop():
    """Основной игровой цикл."""
    if not game_over:
        move_snake()
        check_collisions()
        if not game_over: # Если игра все еще продолжается после проверки столкновений
            draw_snake()
            # Планируем следующий вызов game_loop через GAME_SPEED миллисекунд
            root.after(GAME_SPEED, game_loop)
        else:
            display_game_over() # Если игра закончилась, показываем сообщение
    else:
        display_game_over() # Если игра уже была окончена (например, при нажатии 'R' после Game Over)

def change_direction(event):
    """Изменяет направление движения змейки в ответ на нажатие клавиш."""
    global direction
    new_dir = event.keysym # Получаем имя нажатой клавиши (e.g., "Up", "Down", "r")

    # Предотвращаем немедленное движение в противоположном направлении
    if new_dir == "Up" and direction != "Down":
        direction = "Up"
    elif new_dir == "Down" and direction != "Up":
        direction = "Down"
    elif new_dir == "Left" and direction != "Right":
        direction = "Left"
    elif new_dir == "Right" and direction != "Left":
        direction = "Right"
    # Также поддерживаем клавиши WASD
    elif new_dir == "w" and direction != "Down":
        direction = "Up"
    elif new_dir == "s" and direction != "Up":
        direction = "Down"
    elif new_dir == "a" and direction != "Right":
        direction = "Left"
    elif new_dir == "d" and direction != "Left":
        direction = "Right"
    # Обработка перезапуска игры по клавише 'R'
    elif new_dir.lower() == "r" and game_over:
        start_new_game()

# --- Привязка событий клавиатуры ---
# <Key> будет отслеживать нажатия всех клавиш
root.bind("<Key>", change_direction)

# --- Запуск игры ---
start_new_game() # Вызываем один раз для установки начального состояния и запуска игрового цикла

root.mainloop() # Запускаем основной цикл Tkinter, который будет обрабатывать события и обновлять окно
