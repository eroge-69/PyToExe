import turtle
import random

# Настройка экрана
window = turtle.Screen()
window.title("Змейка")
window.setup(600, 600)
window.tracer(0)
window.bgcolor("black")

# Переменные
delay = 0.1
direction = "stop"
food_pos = []
score = 0

# Змея
snake = turtle.Turtle()
snake.shape("square")
snake.color("green")
snake.penup()
snake.direction = direction
snake.shapesize(1, 1)
segments = []

# Еда
food = turtle.Turtle()
food.shape("circle")
food.color("red")
food.penup()
food.goto(random.randint(-280, 280), random.randint(-280, 280))

# Счетчик очков
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Счёт: 0", align="center", font=("Arial", 24, "bold"))

# Функции движения
def go_up():
    if snake.direction != "down":
        snake.direction = "up"

def go_down():
    if snake.direction != "up":
        snake.direction = "down"

def go_left():
    if snake.direction != "right":
        snake.direction = "left"

def go_right():
    if snake.direction != "left":
        snake.direction = "right"

def move():
    for index in range(len(segments)-1, 0, -1):
        x = segments[index-1].xcor()
        y = segments[index-1].ycor()
        segments[index].goto(x, y)
        
    if segments:
        x_head = snake.xcor()
        y_head = snake.ycor()
        segments[0].goto(x_head, y_head)

    if snake.direction == "up":
        y = snake.ycor()
        snake.sety(y + 20)
    if snake.direction == "down":
        y = snake.ycor()
        snake.sety(y - 20)
    if snake.direction == "left":
        x = snake.xcor()
        snake.setx(x - 20)
    if snake.direction == "right":
        x = snake.xcor()
        snake.setx(x + 20)

# Обработчики клавиш
window.listen()
window.onkeypress(go_up, "Up")
window.onkeypress(go_down, "Down")
window.onkeypress(go_left, "Left")
window.onkeypress(go_right, "Right")

while True:
    window.update()

    # Проверка столкновения с едой
    if snake.distance(food) < 20:
        x = random.randint(-280, 280)
        y = random.randint(-280, 280)
        food.goto(x, y)

        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("green")
        new_segment.penup()
        segments.append(new_segment)

        score += 1
        pen.clear()
        pen.write(f"Счёт: {score}", align="center", font=("Arial", 24, "bold"))

    # Движение змеи
    move()

    # Проверка столкновения с границами
    if snake.xcor() > 290 or snake.xcor() < -290 or snake.ycor() > 290 or snake.ycor() < -290:
        pen.clear()
        pen.write("Игра окончена!", align="center", font=("Arial", 24, "bold"))
        window.update()
        turtle.done()

    # Проверка столкновения с телом
    for segment in segments:
        if segment.distance(snake) < 20:
            pen.clear()
            pen.write("Игра окончена!", align="center", font=("Arial", 24, "bold"))
            window.update()
            turtle.done()

    # Задержка
    turtle.time.sleep(delay)