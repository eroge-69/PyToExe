import pygame
import random
import sys

# Ініціалізація
pygame.init()

# Розміри
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20

# Кольори
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Вікно гри
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змійка — безсмертна, з рахунком")

# Шрифт для тексту
font = pygame.font.SysFont("Arial", 24)

class Snake:
    def __init__(self):
        self.body = [[100, 100]]
        self.direction = "RIGHT"
        self.next_direction = "RIGHT"

    def move(self):
        self.direction = self.next_direction
        head = self.body[0][:]
        new_head = head[:]

        if self.direction == "UP":
            new_head[1] -= CELL_SIZE
        elif self.direction == "DOWN":
            new_head[1] += CELL_SIZE
        elif self.direction == "LEFT":
            new_head[0] -= CELL_SIZE
        elif self.direction == "RIGHT":
            new_head[0] += CELL_SIZE

        # Якщо в межах поля — рухаємось
        if 0 <= new_head[0] < WIDTH and 0 <= new_head[1] < HEIGHT:
            self.body.insert(0, new_head)
            self.body.pop()
        # Якщо втикнулась — стоїмо (нічого не змінюється)

    def grow(self):
        self.body.append(self.body[-1])

    def draw(self, surface):
        for part in self.body:
            pygame.draw.rect(surface, GREEN, pygame.Rect(part[0], part[1], CELL_SIZE, CELL_SIZE))

class Apple:
    def __init__(self):
        self.position = self.random_position()

    def random_position(self):
        x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        return [x, y]

    def draw(self, surface):
        pygame.draw.rect(surface, RED, pygame.Rect(self.position[0], self.position[1], CELL_SIZE, CELL_SIZE))

def draw_score(surface, score):
    text = font.render(f"Яблука: {score}", True, WHITE)
    surface.blit(text, (10, 10))

def show_win(surface):
    win.fill(BLACK)
    text = font.render("🎉 ВИГРАШ! Ти зібрав 10 яблук!", True, WHITE)
    surface.blit(text, (WIDTH // 2 - 180, HEIGHT // 2 - 20))
    pygame.display.update()
    pygame.time.wait(3000)

def game():
    clock = pygame.time.Clock()
    snake = Snake()
    apple = Apple()
    score = 0
    running = True

    while running:
        clock.tick(5)  # Повільна змійка

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != "DOWN":
                    snake.next_direction = "UP"
                elif event.key == pygame.K_DOWN and snake.direction != "UP":
                    snake.next_direction = "DOWN"
                elif event.key == pygame.K_LEFT and snake.direction != "RIGHT":
                    snake.next_direction = "LEFT"
                elif event.key == pygame.K_RIGHT and snake.direction != "LEFT":
                    snake.next_direction = "RIGHT"

        snake.move()

        if snake.body[0] == apple.position:
            snake.grow()
            score += 1
            apple = Apple()

        if score >= 10:
            show_win(win)
            running = False
            continue

        win.fill(BLACK)
        snake.draw(win)
        apple.draw(win)
        draw_score(win, score)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    game()
