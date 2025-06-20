import tkinter as tk
import turtle
import time
import pygame
import sys
import random
import math

# Глобальные переменные
current_step = 0
sequence = []
root = None
label = None
main_button = None
draw_hearts_button = None
draw_shapes_button = None


def draw_hearts():
    screen = turtle.Screen()
    screen.bgcolor("#E9E95C")
    heart = turtle.Turtle()
    heart.speed(5)
    heart.color("red", "red")
    heart.pensize(3)

    # Рисуем первое сердце
    heart.penup()
    heart.goto(0, 80)
    heart.pendown()
    heart.begin_fill()
    heart.left(140)
    heart.forward(205)
    heart.circle(-104, 200)
    heart.left(120)
    heart.circle(-104, 200)
    heart.forward(205)
    heart.end_fill()
    heart.hideturtle()
    heart.penup()

    # Рисуем второе сердце
    heart.goto(-260, -350)
    heart.showturtle()
    heart.pendown()
    heart.begin_fill()
    heart.left(280)
    heart.forward(205)
    heart.circle(-104, 200)
    heart.left(120)
    heart.circle(-104, 200)
    heart.forward(205)
    heart.end_fill()
    heart.hideturtle()
    heart.penup()

    # Рисуем третье сердце
    heart.goto(260, -350)
    heart.showturtle()
    heart.pendown()
    heart.begin_fill()
    heart.left(280)
    heart.forward(205)
    heart.circle(-104, 200)
    heart.left(120)
    heart.circle(-104, 200)
    heart.forward(205)
    heart.end_fill()
    heart.hideturtle()

    # Надписи
    time.sleep(0.5)
    heart.penup()
    heart.goto(0, 200)
    heart.color("white")
    heart.write("I", align="center", font=("Arial", 50, "bold"))

    heart.goto(-260, -220)
    heart.write("LOVE", align="center", font=("Arial", 50, "bold"))

    heart.goto(260, -220)
    heart.write("YOU", align="center", font=("Arial", 50, "bold"))

    # Буквы имени
    heart.color("red")
    heart.goto(-135, -50)
    heart.write("N", align="center", font=("Arial", 90, "bold"))
    time.sleep(0.3)
    heart.goto(-55, -50)
    heart.write("A", align="center", font=("Arial", 90, "bold"))
    time.sleep(0.3)
    heart.goto(25, -50)
    heart.write("D", align="center", font=("Arial", 90, "bold"))
    time.sleep(0.3)
    heart.goto(80, -50)
    heart.write("I", align="center", font=("Arial", 90, "bold"))
    time.sleep(0.3)
    heart.goto(135, -50)
    heart.write("A", align="center", font=("Arial", 90, "bold"))

    # Обновляем главное окно
    draw_hearts_button.config(state=tk.DISABLED)
    label.config(text="Анимация сердечек завершена!", fg="green")

    time.sleep(5)
    screen.bye()


def run_shapes_program():
    # Инициализация Pygame
    pygame.init()

    # Размеры окна
    WIDTH, HEIGHT = 1200, 900
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Рисуем фигуры")

    # Цвета
    BACKGROUND = (30, 30, 40)
    BUTTON_AREA = (30, 30, 40)
    RED = (255, 80, 100)
    YELLOW = (255, 215, 70)
    PINK = (255, 150, 200)

    def create_heart(size):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        points = []
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x = 16 * (math.sin(rad) ** 3)
            y = 13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad)
            px = size / 2 - x * size / 40
            py = size / 2 - y * size / 40
            points.append((px, py))

        if len(points) > 2:
            pygame.draw.polygon(surf, RED, points)
        return surf

    def create_star(size):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        points = []
        for i in range(5):
            outer_angle = math.radians(90 + i * 72)
            x = size / 2 + size / 2 * math.cos(outer_angle)
            y = size / 2 - size / 2 * math.sin(outer_angle)
            points.append((x, y))

            inner_angle = math.radians(90 + 36 + i * 72)
            x = size / 2 + size / 4 * math.cos(inner_angle)
            y = size / 2 - size / 4 * math.sin(inner_angle)
            points.append((x, y))

        if len(points) > 2:
            pygame.draw.polygon(surf, YELLOW, points)
        return surf

    def create_flower(size):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center_radius = size // 6
        pygame.draw.circle(surf, YELLOW, (size // 2, size // 2), center_radius)

        petal_color = (200, 150, 255)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            distance = size * 0.25
            x = size // 2 + distance * math.cos(rad)
            y = size // 2 + distance * math.sin(rad)

            petal = pygame.Surface((size // 3, size // 5), pygame.SRCALPHA)
            pygame.draw.ellipse(petal, petal_color, (0, 0, size // 3, size // 5))
            petal = pygame.transform.rotate(petal, -angle)
            petal_rect = petal.get_rect(center=(x, y))
            surf.blit(petal, petal_rect.topleft)
        return surf

    # Создание кнопок
    button_size = 60
    buttons = [
        {"type": "heart", "rect": pygame.Rect(400, 20, button_size, button_size), "img": create_heart(button_size)},
        {"type": "star", "rect": pygame.Rect(600, 20, button_size, button_size), "img": create_star(button_size)},
        {"type": "flower", "rect": pygame.Rect(800, 20, button_size, button_size), "img": create_flower(button_size)}
    ]

    drawn_shapes = []
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                for button in buttons:
                    if button["rect"].collidepoint(pos):
                        shape_size = random.randint(50, 150)
                        shape = {
                            "type": button["type"],
                            "x": random.randint(0, WIDTH - shape_size),
                            "y": random.randint(80, HEIGHT - shape_size),
                            "size": shape_size
                        }
                        drawn_shapes.append(shape)
                        break

        screen.fill(BACKGROUND)
        pygame.draw.rect(screen, BUTTON_AREA, (0, 0, WIDTH, 80))

        for button in buttons:
            screen.blit(button["img"], button["rect"])

        for shape in drawn_shapes:
            if shape["type"] == "heart":
                img = create_heart(shape["size"])
            elif shape["type"] == "star":
                img = create_star(shape["size"])
            else:
                img = create_flower(shape["size"])
            screen.blit(img, (shape["x"], shape["y"]))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()


def next_step():
    global current_step, main_button, draw_hearts_button, draw_shapes_button

    if current_step < len(sequence) - 1:
        current_step += 1
        step = sequence[current_step]

        if "text" in step:
            label.config(text=step["text"], fg="black")

        # После прохождения всех сообщений скрываем кнопку "Далее" и показываем две другие
        if current_step == len(sequence) - 1:
            main_button.pack_forget()  # Скрываем кнопку "Далее"
            draw_hearts_button.pack(side=tk.LEFT, padx=20)
            draw_shapes_button.pack(side=tk.LEFT, padx=20)


def main():
    global root, label, main_button, draw_hearts_button, draw_shapes_button, sequence

    root = tk.Tk()
    root.title("День рождения")
    root.geometry("1200x500")
    root.resizable(False, False)

    sequence = [
        {"text": "Привет!", "action": None},
        {"text": "Это специальный подарок для тебя", "action": None},
        {"text": "С днем рождения!", "action": None},
        {"text": "Пусть сбудутся все твои мечты", "action": None},
        {"text": "И каждый день будет наполнен радостью", "action": None},
        {"text": "Выбери, что ты хочешь увидеть:", "action": None}
    ]

    # Основной интерфейс
    label = tk.Label(
        root,
        text=sequence[current_step]["text"],
        font=("Arial", 20, "bold"),
        padx=20,
        pady=20,
        wraplength=1100
    )
    label.pack(pady=20)

    # Фрейм для кнопок
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # Главная кнопка для последовательности сообщений
    main_button = tk.Button(
        button_frame,
        text="Далее",
        command=next_step,
        font=("Arial", 14),
        bg="#4CAF50",
        fg="white",
        padx=20,
        pady=8
    )
    main_button.pack()

    # Дополнительные кнопки (изначально скрыты)
    draw_hearts_button = tk.Button(
        button_frame,
        text="Анимация сердечек",
        command=draw_hearts,
        font=("Arial", 14),
        bg="#FF9800",
        fg="white",
        padx=15,
        pady=8,
        state=tk.NORMAL
    )

    draw_shapes_button = tk.Button(
        button_frame,
        text="Рисовать фигуры",
        command=run_shapes_program,
        font=("Arial", 14),
        bg="#2196F3",
        fg="white",
        padx=15,
        pady=8,
        state=tk.NORMAL
    )

    root.mainloop()


if __name__ == "__main__":
    main()