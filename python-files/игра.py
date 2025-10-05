import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 50
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 30
PLAYER_SPEED = 8
OBSTACLE_SPEED = 5
FPS = 60

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Избегай препятствий!")
clock = pygame.time.Clock()

# Класс игрока
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = PLAYER_SPEED
        self.score = 0
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - PLAYER_SIZE:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - PLAYER_SIZE:
            self.y += self.speed
            
    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, PLAYER_SIZE, PLAYER_SIZE))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)

# Класс препятствий
class Obstacle:
    def __init__(self):
        self.x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
        self.y = -OBSTACLE_HEIGHT
        self.speed = OBSTACLE_SPEED + random.randint(0, 3)
        
    def move(self):
        self.y += self.speed
        return self.y > HEIGHT
        
    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

# Основная функция игры
def main():
    player = Player()
    obstacles = []
    spawn_timer = 0
    game_over = False
    font = pygame.font.Font(None, 36)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Перезапуск игры
                    return main()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        
        if not game_over:
            # Движение игрока
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.score += 0.1
            
            # Спавн препятствий
            spawn_timer += 1
            if spawn_timer >= 30:  # Спавн каждые 0.5 секунды
                obstacles.append(Obstacle())
                spawn_timer = 0
                
            # Движение препятствий и проверка столкновений
            for obstacle in obstacles[:]:
                if obstacle.move():
                    obstacles.remove(obstacle)
                elif player.get_rect().colliderect(obstacle.get_rect()):
                    game_over = True
        
        # Отрисовка
        screen.fill(BLACK)
        
        # Отрисовка игрока и препятствий
        player.draw()
        for obstacle in obstacles:
            obstacle.draw()
            
        # Отрисовка счета
        score_text = font.render(f"Счет: {int(player.score)}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Сообщение о Game Over
        if game_over:
            game_over_text = font.render("ИГРА ОКОНЧЕНА! Нажми R для рестарта или Q для выхода", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - 300, HEIGHT//2))
            
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()