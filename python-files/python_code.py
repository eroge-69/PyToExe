import pygame
import random

# Инициализация Pygame
pygame.init()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Настройки окна
WIDTH = 600
HEIGHT = 400
FPS = 60

# Размеры объектов
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 60
BALL_SIZE = 15

# Создание экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pинг-Понг")

# Скорости объектов
paddle_speed = 5
ball_speed_x = 4 * random.choice((1, -1))
ball_speed_y = 4 * random.choice((1, -1))

# Игровые объекты
paddle = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Функция для отображения счета
def draw_score():
    font = pygame.font.SysFont('Arial', 30)
    score_text = font.render('Ping Pong!', True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))

# Главная функция игры
def game():
    global ball_speed_x, ball_speed_y
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BLACK)

        # Проверка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Управление ракеткой
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and paddle.top > 0:
            paddle.y -= paddle_speed
        if keys[pygame.K_DOWN] and paddle.bottom < HEIGHT:
            paddle.y += paddle_speed

        # Движение мяча
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Отскок мяча от верхней и нижней стенок
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y = -ball_speed_y

        # Отскок мяча от ракетки
        if ball.colliderect(paddle):
            ball_speed_x = -ball_speed_x

        # Если мяч вышел за пределы экрана (не отскочил от ракетки)
        if ball.left <= 0 or ball.right >= WIDTH:
            ball.x = WIDTH // 2 - BALL_SIZE // 2
            ball.y = HEIGHT // 2 - BALL_SIZE // 2
            ball_speed_x = 4 * random.choice((1, -1))
            ball_speed_y = 4 * random.choice((1, -1))

        # Отображение объектов
        pygame.draw.rect(screen, GREEN, paddle)  # Ракетка
        pygame.draw.ellipse(screen, WHITE, ball)  # Мяч
        draw_score()  # Счет

        # Обновление экрана
        pygame.display.flip()

        # Ограничение FPS
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    game()
