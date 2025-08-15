"""
Очень простая 2D игра "Прыгающий квадрат"
Управление: Пробел - прыжок, Стрелки - движение
Цель: избегать падающих блоков
"""

import pygame
import random
import sys

# Инициализация pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.vel_y = 0
        self.on_ground = False
        self.color = BLUE
        
    def update(self):
        # Гравитация
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Ограничение по экрану
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.rect.bottom = SCREEN_HEIGHT - 50
            self.vel_y = 0
            self.on_ground = True
            
    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            
    def move_left(self):
        self.rect.x -= 5
        if self.rect.left < 0:
            self.rect.left = 0
            
    def move_right(self):
        self.rect.x += 5
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class Obstacle:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = random.randint(3, 7)
        
    def update(self):
        self.rect.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        
    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Прыгающий квадрат - Простая 2D игра")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Игровые объекты
        self.player = Player(100, SCREEN_HEIGHT - 100)
        self.obstacles = []
        self.score = 0
        self.game_over = False
        
        # Рекорд
        self.high_score = self.load_high_score()
        
        # Таймер для создания препятствий
        self.obstacle_timer = 0
        self.obstacle_interval = 60  # кадров
        
    def spawn_obstacle(self):
        width = random.randint(30, 80)
        height = random.randint(30, 80)
        x = random.randint(0, SCREEN_WIDTH - width)
        y = -height
        
        colors = [RED, GREEN, YELLOW]
        color = random.choice(colors)
        
        self.obstacles.append(Obstacle(x, y, width, height, color))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.player.jump()
                elif event.key == pygame.K_r and self.game_over:
                    self.restart()
                elif event.key == pygame.K_ESCAPE:
                    return False
                    
        # Непрерывное управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
            
        return True
        
    def update(self):
        if not self.game_over:
            self.player.update()
            
            # Обновление препятствий
            for obstacle in self.obstacles[:]:
                obstacle.update()
                if obstacle.is_off_screen():
                    self.obstacles.remove(obstacle)
                    self.score += 1
                    
            # Проверка столкновений
            for obstacle in self.obstacles:
                if self.player.rect.colliderect(obstacle.rect):
                    self.game_over = True
                    
            # Создание новых препятствий
            self.obstacle_timer += 1
            if self.obstacle_timer >= self.obstacle_interval:
                self.spawn_obstacle()
                self.obstacle_timer = 0
                
    def draw(self):
        self.screen.fill(BLACK)
        
        # Земля
        pygame.draw.rect(self.screen, WHITE, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        
        # Игрок
        self.player.draw(self.screen)
        
        # Препятствия
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        # Счет и рекорд
        score_text = self.font.render(f"Счет: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        high_score_text = self.font.render(f"Рекорд: {self.high_score}", True, YELLOW)
        self.screen.blit(high_score_text, (SCREEN_WIDTH - 200, 10))
        
        # Инструкции
        if not self.game_over:
            instructions = [
                "Управление:",
                "Пробел - прыжок",
                "Стрелки - движение влево/вправо",
                "ESC - выход"
            ]
            for i, instruction in enumerate(instructions):
                text = self.small_font.render(instruction, True, WHITE)
                self.screen.blit(text, (10, 50 + i * 25))
        else:
            game_over_text = self.font.render("Игра окончена!", True, RED)
            restart_text = self.small_font.render("Нажмите R для перезапуска", True, WHITE)
            score_text = self.font.render(f"Финальный счет: {self.score}", True, WHITE)
            
            # Показ нового рекорда
            if self.score == self.high_score and self.score > 0:
                new_record_text = self.font.render("НОВЫЙ РЕКОРД!", True, GREEN)
                self.screen.blit(new_record_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100))
            
            self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2))
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 50))
            
    def load_high_score(self):
        """Загрузка рекорда из файла"""
        try:
            with open('high_score.txt', 'r') as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0
    
    def save_high_score(self):
        """Сохранение рекорда в файл"""
        try:
            with open('high_score.txt', 'w') as f:
                f.write(str(self.high_score))
        except Exception as e:
            print(f"Ошибка сохранения рекорда: {e}")
    
    def restart(self):
        # Проверка и сохранение рекорда
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            
        self.player = Player(100, SCREEN_HEIGHT - 100)
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.obstacle_timer = 0
        
    def run(self):
        running = True
        
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

def main():
    """Главная функция"""
    print("Запуск простой 2D игры...")
    print("Управление:")
    print("  Пробел - прыжок")
    print("  Стрелки влево/вправо - движение")
    print("  ESC - выход")
    print("  R - перезапуск после проигрыша")
    
    try:
        game = Game()
        game.run()
    except ImportError as e:
        print(f"Ошибка: {e}")
        print("Установите pygame: pip install pygame")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
