import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Простая 2D Игра")
clock = pygame.time.Clock()

# Класс игрока
class Player:
    def __init__(self):
        self.width = 50
        self.height = 50
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 5
        self.color = BLUE
        self.score = 0
        self.lives = 3
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed

# Класс врага
class Enemy:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)
        self.color = RED
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()
    
    def reset(self):
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.speed = random.randint(2, 5)

# Класс бонуса
class Bonus:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-100, -40)
        self.speed = 3
        self.color = GREEN
    
    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()
    
    def reset(self):
        self.x = random.randint(0, WIDTH - self.width)
        self.y = random.randint(-100, -40)

# Проверка столкновений
def check_collision(player, obj):
    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
    obj_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
    return player_rect.colliderect(obj_rect)

# Основная функция игры
def main():
    player = Player()
    enemies = [Enemy() for _ in range(5)]
    bonuses = [Bonus() for _ in range(3)]
    
    font = pygame.font.SysFont('Arial', 36)
    small_font = pygame.font.SysFont('Arial', 24)
    game_over = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Перезапуск игры
                    player = Player()
                    enemies = [Enemy() for _ in range(5)]
                    bonuses = [Bonus() for _ in range(3)]
                    game_over = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            
            # Обновление врагов
            for enemy in enemies:
                enemy.update()
                if check_collision(player, enemy):
                    player.lives -= 1
                    enemy.reset()
                    if player.lives <= 0:
                        game_over = True
            
            # Обновление бонусов
            for bonus in bonuses:
                bonus.update()
                if check_collision(player, bonus):
                    player.score += 10
                    bonus.reset()
        
        # Отрисовка
        screen.fill(BLACK)
        
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bonus in bonuses:
            bonus.draw()
        
        # Отображение счета и жизней
        score_text = font.render(f"Счет: {player.score}", True, WHITE)
        lives_text = font.render(f"Жизни: {player.lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        
        # Отображение управления
        controls_text = small_font.render("Управление: Стрелки - двигаться, R - перезапуск, ESC - выход", True, WHITE)
        screen.blit(controls_text, (10, HEIGHT - 30))
        
        if game_over:
            game_over_text = font.render("ИГРА ОКОНЧЕНА! Нажмите R для перезапуска", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - 250, HEIGHT//2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()