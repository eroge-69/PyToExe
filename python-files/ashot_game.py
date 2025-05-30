import pygame
import sys
import pickle
import os
import random
from pygame.locals import *

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5

# Цвета
RED = (217, 0, 18)     # Армения
BLUE = (0, 35, 149)    # Армения
ORANGE = (242, 168, 0) # Армения
AZERI_BLUE = (0, 185, 228)
AZERI_RED = (239, 51, 64)
AZERI_GREEN = (80, 158, 47)
BROWN = (139, 69, 19)
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
DARK_BROWN = (101, 67, 33)
MOUNTAIN_COLOR = (120, 110, 100)
HOUSE_COLOR = (200, 150, 100)
ROOF_COLOR = (150, 70, 50)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 60
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_player()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.jumping = False
        self.direction = 1
        self.lives = 3
        self.score = 0
        self.invincible = 0  # Неуязвимость после получения урона

    def draw_player(self):
        # Тело (флаг Армении)
        pygame.draw.rect(self.image, RED, (0, 20, self.width, (self.height-20)//3))
        pygame.draw.rect(self.image, BLUE, (0, 20 + (self.height-20)//3, self.width, (self.height-20)//3))
        pygame.draw.rect(self.image, ORANGE, (0, 20 + 2*(self.height-20)//3, self.width, (self.height-20)//3))
        
        # Голова
        head_radius = 15
        head_center = (self.width//2, head_radius + 5)
        pygame.draw.circle(self.image, (241, 194, 125), head_center, head_radius)
        
        # Длинный нос
        pygame.draw.ellipse(self.image, (220, 150, 90), 
                          (self.width//2, head_center[1] - 3, 15, 8))
        
        # Большие усы (армянский стиль)
        # Левый ус
        pygame.draw.ellipse(self.image, BLACK, 
                          (self.width//2 - 20, head_center[1] + 3, 20, 8))
        # Правый ус
        pygame.draw.ellipse(self.image, BLACK, 
                          (self.width//2, head_center[1] + 3, 20, 8))
        
        # Черная кепка
        pygame.draw.rect(self.image, BLACK, (self.width//2 - 12, head_center[1] - head_radius - 5, 24, 10))
        pygame.draw.polygon(self.image, BLACK, [
            (self.width//2 - 15, head_center[1] - head_radius + 5),
            (self.width//2 + 15, head_center[1] - head_radius + 5),
            (self.width//2, head_center[1] - head_radius - 15)
        ])
        
        # Глаза
        pygame.draw.circle(self.image, WHITE, (self.width//2 - 5, head_center[1] - 2), 3)
        pygame.draw.circle(self.image, WHITE, (self.width//2 + 7, head_center[1] - 4), 3)
        pygame.draw.circle(self.image, BLACK, (self.width//2 - 5, head_center[1] - 2), 1)
        pygame.draw.circle(self.image, BLACK, (self.width//2 + 7, head_center[1] - 4), 1)

    def update(self, platforms):
        # Гравитация
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Счетчик неуязвимости
        if self.invincible > 0:
            self.invincible -= 1
            # Мигание при неуязвимости
            if self.invincible % 10 < 5:
                self.draw_player()
            else:
                # Прозрачная версия для мигания
                self.image.fill((0, 0, 0, 0))
                self.draw_player()
                self.image.set_alpha(150)
        else:
            self.image.set_alpha(255)
            self.draw_player()

        # Проверка коллизий с платформами
        collision = False
        for platform in platforms:
            if pygame.sprite.collide_rect(self, platform):
                if self.vel_y > 0 and self.rect.bottom > platform.rect.top and self.rect.top < platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.jumping = False
                    collision = True
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # Границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

    def respawn(self):
        self.lives -= 1
        if self.lives <= 0:
            return True  # Сигнал для завершения игры
        self.rect.x = 100
        self.rect.y = 300
        self.vel_y = 0
        self.invincible = 90  # 1.5 секунды неуязвимости
        return False

    def jump(self):
        if not self.jumping:
            self.vel_y = JUMP_STRENGTH
            self.jumping = True

    def move(self, dx):
        self.rect.x += dx
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        
        if enemy_type == "shaurma":
            self.width = 40
            self.height = 40
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.draw_shaurma()
            self.rect = self.image.get_rect(topleft=(x, y))
            self.direction = -1
            self.speed = 2
            self.fly_counter = 0
            self.angle = 0
        else:  # Босс
            self.width = 100
            self.height = 150
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            self.draw_boss()
            self.rect = self.image.get_rect(topleft=(x, y))
            self.direction = -1
            self.speed = 1
            self.health = 10

    def draw_shaurma(self):
        # Основа шавермы (треугольник - лаваш)
        pygame.draw.polygon(self.image, (220, 180, 100), [
            (self.width//2, 5),
            (5, self.height - 5),
            (self.width - 5, self.height - 5)
        ])
        
        # Начинка
        pygame.draw.rect(self.image, (160, 100, 60), (self.width//4, self.height//2, self.width//2, 5))
        pygame.draw.rect(self.image, GREEN, (self.width//4, self.height//2 + 5, self.width//2, 3))
        pygame.draw.rect(self.image, (200, 150, 150), (self.width//4, self.height//2 + 8, self.width//2, 4))
        
        # Глаза
        pygame.draw.circle(self.image, WHITE, (self.width//3, self.height//3), 5)
        pygame.draw.circle(self.image, WHITE, (2*self.width//3, self.height//3), 5)
        pygame.draw.circle(self.image, BLACK, (self.width//3, self.height//3), 2)
        pygame.draw.circle(self.image, BLACK, (2*self.width//3, self.height//3), 2)
        
        # Улыбка
        pygame.draw.arc(self.image, BLACK, (self.width//4, self.height//2, self.width//2, self.height//4), 0, 3.14, 2)

    def draw_boss(self):
        # Тело (флаг Азербайджана)
        pygame.draw.rect(self.image, AZERI_BLUE, (0, 30, self.width, self.height//3 - 10))
        pygame.draw.rect(self.image, AZERI_RED, (0, self.height//3 + 20, self.width, self.height//3 - 10))
        pygame.draw.rect(self.image, AZERI_GREEN, (0, 2*self.height//3 + 10, self.width, self.height//3 - 10))
        
        # Голова
        head_radius = 30
        head_center = (self.width//2, head_radius + 10)
        pygame.draw.circle(self.image, (241, 194, 125), head_center, head_radius)
        
        # Борода
        beard_points = [
            (self.width//2 - 25, head_center[1] + 10),
            (self.width//2 - 15, head_center[1] + 40),
            (self.width//2 + 15, head_center[1] + 40),
            (self.width//2 + 25, head_center[1] + 10)
        ]
        pygame.draw.polygon(self.image, (139, 69, 19), beard_points)
        
        # Нос
        nose_points = [
            (self.width//2, head_center[1] + 5),
            (self.width//2 + 15, head_center[1]),
            (self.width//2 + 20, head_center[1] + 5)
        ]
        pygame.draw.polygon(self.image, (220, 150, 90), nose_points)
        
        # Шапка (в цветах флага)
        pygame.draw.rect(self.image, AZERI_BLUE, (self.width//2 - 20, head_center[1] - head_radius - 5, 40, 10))
        pygame.draw.rect(self.image, AZERI_RED, (self.width//2 - 20, head_center[1] - head_radius - 15, 40, 10))
        pygame.draw.rect(self.image, AZERI_GREEN, (self.width//2 - 20, head_center[1] - head_radius - 25, 40, 10))
        
        # Глаза
        pygame.draw.circle(self.image, WHITE, (self.width//2 - 10, head_center[1] - 5), 6)
        pygame.draw.circle(self.image, WHITE, (self.width//2 + 15, head_center[1] - 8), 6)
        pygame.draw.circle(self.image, BLACK, (self.width//2 - 10, head_center[1] - 5), 3)
        pygame.draw.circle(self.image, BLACK, (self.width//2 + 15, head_center[1] - 8), 3)
        
        # Злобные брови
        pygame.draw.line(self.image, BLACK, (self.width//2 - 15, head_center[1] - 15), (self.width//2 - 5, head_center[1] - 12), 3)
        pygame.draw.line(self.image, BLACK, (self.width//2 + 10, head_center[1] - 18), (self.width//2 + 20, head_center[1] - 15), 3)

    def update(self):
        if self.enemy_type == "shaurma":
            # Полет зигзагом
            self.rect.x += self.speed * self.direction
            self.rect.y += 2 * pygame.math.Vector2(0, 1).rotate(self.fly_counter).y
            self.fly_counter = (self.fly_counter + 5) % 360
            
            if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
                self.direction *= -1
        else:
            # Движение босса
            self.rect.x += self.speed * self.direction
            if self.rect.left <= 100 or self.rect.right >= SCREEN_WIDTH - 100:
                self.direction *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((34, 139, 34))
        pygame.draw.rect(self.image, (101, 67, 33), (0, 0, width, height), 3)
        self.rect = self.image.get_rect(topleft=(x, y))

class Background:
    def __init__(self):
        self.mountains = []
        self.houses = []
        self.generate_scenery()
    
    def generate_scenery(self):
        # Горы на заднем плане
        self.mountains.append([(0, SCREEN_HEIGHT), (200, 200), (400, SCREEN_HEIGHT)])
        self.mountains.append([(300, SCREEN_HEIGHT), (500, 150), (700, SCREEN_HEIGHT)])
        self.mountains.append([(600, SCREEN_HEIGHT), (800, 250), (1000, SCREEN_HEIGHT)])
        
        # Деревеньки (опущены ниже, чтобы стояли на земле)
        for i in range(5):
            x = 100 + i * 150
            y = SCREEN_HEIGHT - 40 - 50  # 50 - высота дома, 40 - высота земли
            self.houses.append({
                'rect': pygame.Rect(x, y, 60, 50),
                'roof': [(x-10, y), (x+30, y-30), (x+70, y)]
            })
    
    def draw(self, screen):
        # Небо
        screen.fill(SKY_BLUE)
        
        # Солнце
        pygame.draw.circle(screen, (255, 255, 0), (700, 80), 40)
        
        # Облака
        for i in range(3):
            x = 100 + i * 200
            pygame.draw.circle(screen, WHITE, (x, 100), 30)
            pygame.draw.circle(screen, WHITE, (x+25, 90), 30)
            pygame.draw.circle(screen, WHITE, (x+50, 100), 30)
        
        # Горы
        for mountain in self.mountains:
            pygame.draw.polygon(screen, MOUNTAIN_COLOR, mountain)
            # Снежные вершины
            pygame.draw.polygon(screen, WHITE, [
                mountain[1], 
                (mountain[1][0]-30, mountain[1][1]+30),
                (mountain[1][0]+30, mountain[1][1]+30)
            ])
        
        # Деревеньки (домики)
        for house in self.houses:
            pygame.draw.rect(screen, HOUSE_COLOR, house['rect'])
            pygame.draw.polygon(screen, ROOF_COLOR, house['roof'])
            # Окна
            pygame.draw.rect(screen, (200, 200, 255), 
                            (house['rect'].x + 10, house['rect'].y + 15, 15, 15))
            pygame.draw.rect(screen, (200, 200, 255), 
                            (house['rect'].x + 35, house['rect'].y + 15, 15, 15))
            # Дверь
            pygame.draw.rect(screen, DARK_BROWN, 
                            (house['rect'].x + 25, house['rect'].y + 30, 15, 20))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ашот против Шаверм")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.background = Background()
        self.load_level(1)
        self.game_state = "playing"
        self.save_file = "savegame.dat"

    def load_level(self, level):
        self.level = level
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        
        # Создание платформ
        if level == 1:
            self.player = Player(100, 300)
            platforms_data = [
                (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
                (150, 450, 200, 20),
                (450, 400, 150, 20),
                (250, 350, 100, 20),
                (100, 250, 200, 20),
                (400, 200, 150, 20),
                (200, 150, 100, 20)
            ]
            for data in platforms_data:
                platform = Platform(*data)
                self.platforms.add(platform)
                self.all_sprites.add(platform)
            
            # Шавермы (меньше количество)
            for i in range(3):
                enemy = Enemy(200 + i*180, 100 + i*50, "shaurma")
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                
        elif level == 2:
            self.player = Player(100, 300)
            platforms_data = [
                (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
                (100, 450, 150, 20),
                (350, 400, 150, 20),
                (550, 350, 150, 20),
                (200, 300, 100, 20),
                (400, 250, 150, 20),
                (100, 200, 150, 20),
                (300, 150, 100, 20),
                (500, 100, 150, 20)
            ]
            for data in platforms_data:
                platform = Platform(*data)
                self.platforms.add(platform)
                self.all_sprites.add(platform)
            
            # Шавермы (меньше количество)
            for i in range(4):
                enemy = Enemy(150 + i*150, 80 + i*40, "shaurma")
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                
        elif level == 3:
            self.player = Player(100, 300)
            platforms_data = [
                (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
                (50, 450, 150, 20),
                (250, 400, 150, 20),
                (450, 350, 150, 20),
                (650, 300, 120, 20),
                (100, 250, 150, 20),
                (300, 200, 150, 20),
                (500, 150, 150, 20),
                (200, 100, 100, 20)
            ]
            for data in platforms_data:
                platform = Platform(*data)
                self.platforms.add(platform)
                self.all_sprites.add(platform)
            
            # Босс
            self.boss = Enemy(SCREEN_WIDTH // 2 - 50, 50, "boss")
            self.enemies.add(self.boss)
            self.all_sprites.add(self.boss)
        
        self.all_sprites.add(self.player)

    def save_game(self):
        save_data = {
            'level': self.level,
            'player_lives': self.player.lives,
            'player_score': self.player.score,
            'player_pos': (self.player.rect.x, self.player.rect.y)
        }
        with open(self.save_file, 'wb') as f:
            pickle.dump(save_data, f)

    def load_game(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'rb') as f:
                save_data = pickle.load(f)
            self.level = save_data['level']
            self.player.lives = save_data['player_lives']
            self.player.score = save_data['player_score']
            self.load_level(self.level)
            self.player.rect.x, self.player.rect.y = save_data['player_pos']

    def restart_game(self):
        """Полный рестарт игры на первый уровень"""
        self.player.lives = 3
        self.player.score = 0
        self.load_level(1)
        self.game_state = "playing"

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.player.jump()
                    if event.key == K_s:  # Сохранение по S
                        self.save_game()
                    if event.key == K_l:  # Загрузка по L
                        self.load_game()
                    if event.key == K_r:  # Перезапуск уровня
                        self.load_level(self.level)
                    if event.key == K_ESCAPE:
                        running = False
            
            # Управление персонажем
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[K_LEFT]:
                dx = -PLAYER_SPEED
            if keys[K_RIGHT]:
                dx = PLAYER_SPEED
            self.player.move(dx)
            
            # Обновление
            self.player.update(self.platforms)
            self.enemies.update()
            
            # Проверка столкновений с врагами (только если игрок не неуязвим)
            if self.player.invincible == 0:
                enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
                for enemy in enemy_hits:
                    if enemy.enemy_type == "boss":
                        # Столкновение с боссом
                        if self.player.rect.bottom < enemy.rect.centery:
                            enemy.health -= 1
                            self.player.vel_y = JUMP_STRENGTH
                            if enemy.health <= 0:
                                enemy.kill()
                                self.player.score += 500
                        else:
                            if self.player.respawn():
                                self.restart_game()  # Если жизни кончились, рестарт
                    else:
                        # Столкновение с шавермой
                        if self.player.rect.bottom < enemy.rect.centery:
                            enemy.kill()
                            self.player.score += 100
                            self.player.vel_y = JUMP_STRENGTH
                        else:
                            if self.player.respawn():
                                self.restart_game()  # Если жизни кончились, рестарт
            
            # Проверка падения за экран
            if self.player.rect.top > SCREEN_HEIGHT:
                if self.player.respawn():
                    self.restart_game()  # Если жизни кончились, рестарт
            
            # Проверка завершения уровня
            if self.level < 3 and len(self.enemies) == 0:
                self.level += 1
                self.load_level(self.level)
            elif self.level == 3 and len(self.enemies) == 0:
                self.game_state = "win"
            
            # Отрисовка
            self.background.draw(self.screen)
            self.all_sprites.draw(self.screen)
            
            # Отрисовка UI
            lives_text = self.font.render(f'Жизни: {self.player.lives}', True, WHITE)
            score_text = self.font.render(f'ОЧКО: {self.player.score}', True, WHITE)
            level_text = self.font.render(f'Уровень: {self.level}', True, WHITE)
            self.screen.blit(lives_text, (10, 10))
            self.screen.blit(score_text, (10, 50))
            self.screen.blit(level_text, (10, 90))
            
            # Отрисовка здоровья босса
            if self.level == 3 and len(self.enemies) > 0:
                health_text = self.font.render(f'Здоровье босса: {self.boss.health}', True, WHITE)
                self.screen.blit(health_text, (SCREEN_WIDTH - 250, 10))
            
            # Сообщения о состоянии игры
            if self.game_state == "win":
                win_text = self.font.render("ПОБЕДА! Ашот доказал что Карабах это Армения! Нажмите R для перезапуска", True, GREEN)
                self.screen.blit(win_text, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2))
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
