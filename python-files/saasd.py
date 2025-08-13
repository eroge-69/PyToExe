import pygame
import random
import sys
from pygame.locals import *

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Настройки экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50
PANEL_HEIGHT = 100

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Стратегическая игра')

# Шрифты
font_small = pygame.font.SysFont('Arial', 16)
font_medium = pygame.font.SysFont('Arial', 24)
font_large = pygame.font.SysFont('Arial', 32)

class Game:
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.player = Player(0, 0)
        self.resources = self.generate_resources()
        self.buildings = []
        self.enemies = self.generate_enemies()
        self.day = 1
        self.camera_x = 0
        self.camera_y = 0
        self.selected_building = None
        self.message = ""
        self.message_timer = 0
        
    def generate_resources(self):
        resources = []
        for _ in range(15):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            resource_type = random.choice(['wood', 'stone', 'gold'])
            amount = random.randint(10, 50)
            resources.append(Resource(x, y, resource_type, amount))
        return resources
    
    def generate_enemies(self):
        enemies = []
        for _ in range(5):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            health = random.randint(30, 70)
            attack = random.randint(5, 15)
            enemies.append(Enemy(x, y, health, attack))
        return enemies
    
    def move_player(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            self.player.x = new_x
            self.player.y = new_y
            self.check_position()
            self.center_camera()
            return True
        return False
    
    def center_camera(self):
        # Центрируем камеру на игроке
        self.camera_x = (self.player.x * TILE_SIZE + TILE_SIZE // 2) - SCREEN_WIDTH // 2
        self.camera_y = (self.player.y * TILE_SIZE + TILE_SIZE // 2) - (SCREEN_HEIGHT - PANEL_HEIGHT) // 2
        
        # Ограничиваем камеру границами карты
        self.camera_x = max(0, min(self.camera_x, self.width * TILE_SIZE - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.height * TILE_SIZE - (SCREEN_HEIGHT - PANEL_HEIGHT)))
    
    def check_position(self):
        # Проверка ресурсов
        for resource in self.resources[:]:
            if self.player.x == resource.x and self.player.y == resource.y:
                self.player.resources[resource.type] += resource.amount
                self.show_message(f"Собрано {resource.amount} {resource.type}!")
                self.resources.remove(resource)
        
        # Проверка зданий
        for building in self.buildings:
            if self.player.x == building.x and self.player.y == building.y:
                self.show_message(f"Вы у здания: {building.type} (уровень {building.level})")
        
        # Проверка врагов
        for enemy in self.enemies[:]:
            if self.player.x == enemy.x and self.player.y == enemy.y:
                self.battle(self.player, enemy)
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.show_message("Враг побежден!")
    
    def build(self, building_type):
        cost = {
            'house': {'wood': 20, 'stone': 10},
            'mine': {'wood': 10, 'stone': 20},
            'barracks': {'wood': 30, 'stone': 30}
        }
        
        if building_type in cost:
            can_build = True
            for res, amount in cost[building_type].items():
                if self.player.resources.get(res, 0) < amount:
                    can_build = False
                    self.show_message(f"Не хватает {res}!")
                    break
            
            if can_build:
                for res, amount in cost[building_type].items():
                    self.player.resources[res] -= amount
                self.buildings.append(Building(self.player.x, self.player.y, building_type))
                self.show_message(f"Построено здание: {building_type}!")
        else:
            self.show_message("Неизвестный тип здания")
    
    def battle(self, player, enemy):
        self.show_message(f"Бой с врагом (Здоровье: {enemy.health}, Атака: {enemy.attack})")
        
        while player.health > 0 and enemy.health > 0:
            # Игрок атакует
            enemy.health -= player.attack
            self.show_message(f"Вы атакуете врага! У врага осталось {max(0, enemy.health)} здоровья")
            
            if enemy.health <= 0:
                break
                
            # Враг атакует
            player.health -= enemy.attack
            self.show_message(f"Враг атакует вас! У вас осталось {max(0, player.health)} здоровья")
        
        if player.health <= 0:
            self.show_message("Вы проиграли битву!")
            player.health = 1  # Воскрешаем с 1 HP
    
    def next_day(self):
        self.day += 1
        # Восстановление здоровья игрока
        self.player.health = min(100, self.player.health + 20)
        self.show_message(f"Наступил день {self.day}. Здоровье восстановлено до {self.player.health}")
        
        # Генерация новых ресурсов
        if random.random() < 0.3 and len(self.resources) < 20:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            resource_type = random.choice(['wood', 'stone', 'gold'])
            amount = random.randint(10, 30)
            self.resources.append(Resource(x, y, resource_type, amount))
            self.show_message("Появились новые ресурсы на карте!")
        
        # Перемещение врагов
        for enemy in self.enemies:
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            new_x = enemy.x + dx
            new_y = enemy.y + dy
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                enemy.x = new_x
                enemy.y = new_y
    
    def show_message(self, text):
        self.message = text
        self.message_timer = 180  # ~3 секунды при 60 FPS
    
    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def draw(self, screen):
        # Очистка экрана
        screen.fill(BLACK)
        
        # Рисуем карту
        self.draw_map(screen)
        
        # Рисуем панель информации
        self.draw_panel(screen)
        
        # Рисуем сообщение, если есть
        if self.message_timer > 0:
            self.draw_message(screen)
    
    def draw_map(self, screen):
        # Определяем видимую область карты
        start_x = max(0, self.camera_x // TILE_SIZE)
        end_x = min(self.width, (self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_y = min(self.height, (self.camera_y + SCREEN_HEIGHT - PANEL_HEIGHT) // TILE_SIZE + 1)
        
        # Рисуем землю
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                rect = pygame.Rect(
                    x * TILE_SIZE - self.camera_x,
                    y * TILE_SIZE - self.camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(screen, GREEN, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
        
        # Рисуем ресурсы
        for resource in self.resources:
            if start_x <= resource.x < end_x and start_y <= resource.y < end_y:
                rect = pygame.Rect(
                    resource.x * TILE_SIZE - self.camera_x,
                    resource.y * TILE_SIZE - self.camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                color = {
                    'wood': BROWN,
                    'stone': GRAY,
                    'gold': GOLD
                }[resource.type]
                pygame.draw.rect(screen, color, rect)
                text = font_small.render(str(resource.amount), True, WHITE)
                screen.blit(text, (rect.x + 5, rect.y + 5))
        
        # Рисуем здания
        for building in self.buildings:
            if start_x <= building.x < end_x and start_y <= building.y < end_y:
                rect = pygame.Rect(
                    building.x * TILE_SIZE - self.camera_x,
                    building.y * TILE_SIZE - self.camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                color = {
                    'house': BLUE,
                    'mine': GRAY,
                    'barracks': RED
                }[building.type]
                pygame.draw.rect(screen, color, rect)
                text = font_small.render(building.type[0].upper(), True, WHITE)
                screen.blit(text, (rect.x + 20, rect.y + 20))
        
        # Рисуем врагов
        for enemy in self.enemies:
            if start_x <= enemy.x < end_x and start_y <= enemy.y < end_y:
                rect = pygame.Rect(
                    enemy.x * TILE_SIZE - self.camera_x,
                    enemy.y * TILE_SIZE - self.camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(screen, RED, rect)
                text = font_small.render("E", True, WHITE)
                screen.blit(text, (rect.x + 20, rect.y + 20))
                
                # Полоска здоровья
                health_width = int(TILE_SIZE * (enemy.health / 100))
                health_rect = pygame.Rect(rect.x, rect.y - 10, health_width, 5)
                pygame.draw.rect(screen, GREEN, health_rect)
        
        # Рисуем игрока
        if start_x <= self.player.x < end_x and start_y <= self.player.y < end_y:
            rect = pygame.Rect(
                self.player.x * TILE_SIZE - self.camera_x,
                self.player.y * TILE_SIZE - self.camera_y,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, YELLOW, rect)
            text = font_small.render("P", True, BLACK)
            screen.blit(text, (rect.x + 20, rect.y + 20))
            
            # Полоска здоровья
            health_width = int(TILE_SIZE * (self.player.health / 100))
            health_rect = pygame.Rect(rect.x, rect.y - 10, health_width, 5)
            pygame.draw.rect(screen, GREEN, health_rect)
    
    def draw_panel(self, screen):
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - PANEL_HEIGHT, SCREEN_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(screen, GRAY, panel_rect)
        
        # Информация о дне
        day_text = font_medium.render(f"День: {self.day}", True, WHITE)
        screen.blit(day_text, (20, SCREEN_HEIGHT - PANEL_HEIGHT + 20))
        
        # Здоровье игрока
        health_text = font_medium.render(f"Здоровье: {self.player.health}", True, WHITE)
        screen.blit(health_text, (20, SCREEN_HEIGHT - PANEL_HEIGHT + 50))
        
        # Ресурсы
        resources_text = font_medium.render(
            f"Ресурсы: Дерево: {self.player.resources.get('wood', 0)}  Камень: {self.player.resources.get('stone', 0)}  Золото: {self.player.resources.get('gold', 0)}", 
            True, WHITE
        )
        screen.blit(resources_text, (200, SCREEN_HEIGHT - PANEL_HEIGHT + 20))
        
        # Кнопки
        self.draw_button(screen, 500, SCREEN_HEIGHT - PANEL_HEIGHT + 20, 120, 30, "Построить дом", 'house')
        self.draw_button(screen, 500, SCREEN_HEIGHT - PANEL_HEIGHT + 60, 120, 30, "След. день", 'next_day')
        self.draw_button(screen, 650, SCREEN_HEIGHT - PANEL_HEIGHT + 20, 120, 30, "Улучшить атаку", 'upgrade')
    
    def draw_button(self, screen, x, y, width, height, text, action):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        button_rect = pygame.Rect(x, y, width, height)
        
        if button_rect.collidepoint(mouse):
            pygame.draw.rect(screen, WHITE, button_rect)
            if click[0] == 1:
                if action == 'house':
                    self.build('house')
                elif action == 'next_day':
                    self.next_day()
                elif action == 'upgrade':
                    self.player.upgrade_attack()
        else:
            pygame.draw.rect(screen, BLUE, button_rect)
        
        text_surf = font_small.render(text, True, BLACK if button_rect.collidepoint(mouse) else WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)
    
    def draw_message(self, screen):
        message_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 20, 400, 40)
        pygame.draw.rect(screen, BLACK, message_rect)
        pygame.draw.rect(screen, WHITE, message_rect, 2)
        
        text_surf = font_medium.render(self.message, True, WHITE)
        text_rect = text_surf.get_rect(center=message_rect.center)
        screen.blit(text_surf, text_rect)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.attack = 15
        self.resources = {'wood': 0, 'stone': 0, 'gold': 0}
    
    def upgrade_attack(self):
        if self.resources.get('gold', 0) >= 10:
            self.resources['gold'] -= 10
            self.attack += 5
            return f"Атака улучшена до {self.attack}!"
        else:
            return "Нужно 10 золота для улучшения атаки"

class Resource:
    def __init__(self, x, y, type, amount):
        self.x = x
        self.y = y
        self.type = type
        self.amount = amount

class Building:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.level = 1

class Enemy:
    def __init__(self, x, y, health, attack):
        self.x = x
        self.y = y
        self.health = health
        self.attack = attack

def main():
    clock = pygame.time.Clock()
    game = Game(20, 15)
    game.center_camera()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_w:
                    game.move_player(0, -1)
                elif event.key == K_s:
                    game.move_player(0, 1)
                elif event.key == K_a:
                    game.move_player(-1, 0)
                elif event.key == K_d:
                    game.move_player(1, 0)
                elif event.key == K_n:
                    game.next_day()
                elif event.key == K_u:
                    msg = game.player.upgrade_attack()
                    game.show_message(msg)
        
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()