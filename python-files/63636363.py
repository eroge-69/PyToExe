import pygame
import random
import sys
import time
from pygame.locals import *

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Настройки экрана
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 40
PANEL_HEIGHT = 120
INVENTORY_WIDTH = 200

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (70, 120, 70)  # Темный зеленый для земли
BROWN = (100, 70, 40)
GOLD = (200, 170, 50)
GRAY = (90, 90, 90)
BLUE = (50, 80, 150)   # Для домов
RED = (150, 50, 50)    # Для врагов
YELLOW = (200, 200, 0)
PURPLE = (120, 0, 120) # Для торговца
CHEST_COLOR = (160, 110, 60) # Для сундуков
MEDKIT_COLOR = (255, 50, 50) # Для аптечек

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH + INVENTORY_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Стратегическая игра')

# Шрифты
font_small = pygame.font.SysFont('Arial', 14)
font_medium = pygame.font.SysFont('Arial', 18)
font_large = pygame.font.SysFont('Arial', 24)

class Game:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.player = Player(25, 25)
        self.resources = self.generate_resources(150)  # Увеличено количество ресурсов
        self.buildings = []
        self.enemies = self.generate_enemies(15)  # Немного больше врагов
        self.chests = []
        self.medkits = []
        self.trader = None
        self.day = 1
        self.last_day_change = time.time()
        self.day_duration = 600  # 10 минут в секундах
        self.camera_x = 0
        self.camera_y = 0
        self.message = ""
        self.message_timer = 0
        self.trader_spawn_timer = random.randint(1000, 2000)
        self.chest_spawn_timer = random.randint(2000, 3000)
        self.medkit_spawn_timer = random.randint(3000, 4000)
        self.show_building_info = None
        self.in_battle = False
        self.current_enemy = None
        
    def generate_resources(self, count):
        resources = []
        for _ in range(count):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            resource_type = random.choice(['wood', 'stone', 'gold'])
            amount = random.randint(15, 40)  # Увеличено количество ресурсов
            resources.append(Resource(x, y, resource_type, amount))
        return resources
    
    def generate_enemies(self, count):
        enemies = []
        for _ in range(count):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            health = random.randint(30, 60)
            attack = random.randint(5, 12)
            enemies.append(Enemy(x, y, health, attack))
        return enemies
    
    def spawn_trader(self):
        if self.trader is None:
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            self.trader = Trader(x, y)
            self.show_message("Появился торговец! Найдите его для покупок.")
    
    def spawn_chest(self):
        if len(self.chests) < 5:  # Увеличено максимальное количество сундуков
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            contents = {
                'resources': {
                    'wood': random.randint(10, 25),
                    'stone': random.randint(10, 25),
                    'gold': random.randint(5, 15)
                },
                'weapon': random.choice([None, 'sword', 'axe', 'bow']),
                'medkit': random.choice([True, False])
            }
            self.chests.append(Chest(x, y, contents))
            self.show_message("Появился сундук с сокровищами!")
    
    def spawn_medkit(self):
        if len(self.medkits) < 3:  # Увеличено максимальное количество аптечек
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            heal_amount = random.randint(25, 50)  # Увеличено лечение
            self.medkits.append(Medkit(x, y, heal_amount))
            self.show_message("Появилась аптечка!")

    def move_player(self, dx, dy):
        if self.in_battle:
            self.show_message("Закончите бой перед перемещением!")
            return False
            
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        for enemy in self.enemies:
            if new_x == enemy.x and new_y == enemy.y:
                self.show_message("Нельзя пройти через врага! Атакуйте его (SPACE)")
                return False
        
        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            self.player.x = new_x
            self.player.y = new_y
            self.check_position()
            self.center_camera()
            return True
        return False
    
    def center_camera(self):
        self.camera_x = (self.player.x * TILE_SIZE + TILE_SIZE // 2) - (SCREEN_WIDTH // 2)
        self.camera_y = (self.player.y * TILE_SIZE + TILE_SIZE // 2) - ((SCREEN_HEIGHT - PANEL_HEIGHT) // 2)
        
        self.camera_x = max(0, min(self.camera_x, self.width * TILE_SIZE - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.height * TILE_SIZE - (SCREEN_HEIGHT - PANEL_HEIGHT)))
    
    def check_position(self):
        for resource in self.resources[:]:
            if self.player.x == resource.x and self.player.y == resource.y:
                self.player.resources[resource.type] += resource.amount
                self.show_message(f"Собрано {resource.amount} {resource.type}!")
                self.resources.remove(resource)
        
        for building in self.buildings[:]:
            if self.player.x == building.x and self.player.y == building.y:
                self.show_building_info = building
        
        if self.trader and self.player.x == self.trader.x and self.player.y == self.trader.y:
            self.trade_with_trader()
        
        for chest in self.chests[:]:
            if self.player.x == chest.x and self.player.y == chest.y:
                self.open_chest(chest)
                self.chests.remove(chest)
                break
                
        for medkit in self.medkits[:]:
            if self.player.x == medkit.x and self.player.y == medkit.y:
                self.player.health = min(self.player.max_health, self.player.health + medkit.heal_amount)
                self.show_message(f"Использована аптечка! +{medkit.heal_amount} здоровья")
                self.medkits.remove(medkit)
                break
    
    def open_chest(self, chest):
        message = "Вы нашли в сундуке: "
        items = []
        
        for res, amount in chest.contents['resources'].items():
            self.player.resources[res] = self.player.resources.get(res, 0) + amount
            items.append(f"{amount} {res}")
        
        if chest.contents['weapon']:
            weapon = chest.contents['weapon']
            self.player.weapons.append(weapon)
            items.append(f"{weapon}")
            
            if len(self.player.weapons) == 1:
                self.player.equipped_weapon = weapon
                self.update_player_attack()
        
        if chest.contents.get('medkit', False):
            heal_amount = random.randint(25, 50)
            self.player.health = min(self.player.max_health, self.player.health + heal_amount)
            items.append(f"аптечка (+{heal_amount} HP)")
        
        message += ", ".join(items)
        self.show_message(message)
    
    def update_player_attack(self):
        weapon_bonus = {
            None: 0,
            'sword': 5,
            'axe': 8,
            'bow': 3
        }
        self.player.attack = 10 + weapon_bonus.get(self.player.equipped_weapon, 0)
    
    def start_battle(self, enemy):
        self.in_battle = True
        self.current_enemy = enemy
        self.show_message(f"Бой с врагом! Ваш ход (SPACE). Здоровье врага: {enemy.health}")
    
    def player_attack(self):
        if not self.in_battle or not self.current_enemy:
            return
            
        self.current_enemy.health -= self.player.attack
        self.show_message(f"Вы атаковали врага и нанесли {self.player.attack} урона! У врага осталось {max(0, self.current_enemy.health)} здоровья")
        
        if self.current_enemy.health <= 0:
            self.enemies.remove(self.current_enemy)
            self.show_message("Враг побежден!")
            if random.random() < 0.3:
                resource_type = random.choice(['wood', 'stone', 'gold'])
                amount = random.randint(1, 5)
                self.player.resources[resource_type] = self.player.resources.get(resource_type, 0) + amount
                self.show_message(f"Враг выронил {amount} {resource_type}!")
            
            if random.random() < 0.3:  # Увеличена вероятность выпадения аптечки
                heal_amount = random.randint(20, 40)
                self.medkits.append(Medkit(self.current_enemy.x, self.current_enemy.y, heal_amount))
                self.show_message(f"Враг выронил аптечку! Восстанавливает {heal_amount} здоровья")
            
            self.in_battle = False
            self.current_enemy = None
            return
        
        self.enemy_attack()
    
    def enemy_attack(self):
        if not self.in_battle or not self.current_enemy:
            return
            
        self.player.health -= self.current_enemy.attack
        self.show_message(f"Враг атакует вас и наносит {self.current_enemy.attack} урона! У вас осталось {max(0, self.player.health)} здоровья")
        
        if self.player.health <= 0:
            self.show_message("Вы проиграли битву!")
            self.player.health = self.player.max_health // 4
            self.in_battle = False
            self.current_enemy = None
    
    def trade_with_trader(self):
        options = [
            ("Купить 15 дерева за 5 золота", lambda: self.exchange_resources('gold', 5, 'wood', 15)),
            ("Купить 15 камня за 5 золота", lambda: self.exchange_resources('gold', 5, 'stone', 15)),
            ("Продать 15 дерева за 4 золота", lambda: self.exchange_resources('wood', 15, 'gold', 4)),
            ("Продать 15 камня за 4 золота", lambda: self.exchange_resources('stone', 15, 'gold', 4)),
            ("Купить аптечку за 10 золота", lambda: self.buy_medkit(10, 40)),
            ("Выйти", None)
        ]
        
        self.show_trade_menu(options)
    
    def buy_medkit(self, cost, heal_amount):
        if self.player.resources.get('gold', 0) >= cost:
            self.player.resources['gold'] -= cost
            self.player.health = min(self.player.max_health, self.player.health + heal_amount)
            self.show_message(f"Куплена аптечка! +{heal_amount} здоровья")
        else:
            self.show_message(f"Не хватает золота для покупки аптечки!")
    
    def exchange_resources(self, give_type, give_amount, get_type, get_amount):
        if self.player.resources.get(give_type, 0) >= give_amount:
            self.player.resources[give_type] -= give_amount
            self.player.resources[get_type] = self.player.resources.get(get_type, 0) + get_amount
            self.show_message(f"Обмен произведен: {give_amount} {give_type} → {get_amount} {get_type}")
        else:
            self.show_message(f"Не хватает {give_type} для обмена!")
    
    def build(self, building_type):
        cost = {
            'house': {'wood': 40, 'stone': 30},
            'mine': {'wood': 30, 'stone': 40},
            'barracks': {'wood': 50, 'stone': 50}
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
    
    def upgrade_building(self, building):
        upgrade_cost = {
            'house': {'wood': 20 * building.level, 'stone': 15 * building.level, 'gold': 15 * building.level},
            'mine': {'wood': 15 * building.level, 'stone': 20 * building.level, 'gold': 10 * building.level},
            'barracks': {'wood': 25 * building.level, 'stone': 25 * building.level, 'gold': 20 * building.level}
        }.get(building.type, {})
        
        can_upgrade = True
        
        for res, amount in upgrade_cost.items():
            if self.player.resources.get(res, 0) < amount:
                can_upgrade = False
                self.show_message(f"Не хватает {res} для улучшения!")
                break
        
        if can_upgrade:
            for res, amount in upgrade_cost.items():
                self.player.resources[res] -= amount
            building.upgrade()
            
            if building.type == 'house':
                self.player.max_health += 25  # Увеличено здоровье
                self.player.health = min(self.player.max_health, self.player.health + 25)
                self.show_message(f"Дом улучшен до уровня {building.level}! Макс. здоровье +25")
            elif building.type == 'mine':
                self.show_message(f"Шахта улучшена до уровня {building.level}! Ресурсы будут появляться чаще.")
            elif building.type == 'barracks':
                self.player.attack += 3  # Увеличена атака
                self.show_message(f"Казармы улучшены до уровня {building.level}! Атака +3")
    
    def next_day(self):
        self.day += 1
        self.last_day_change = time.time()
        
        self.player.health = min(self.player.max_health, self.player.health + 25)  # Увеличено восстановление
        
        if random.random() < 0.15 and len(self.resources) < 60:  # Чаще появляются новые ресурсы
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            resource_type = random.choice(['wood', 'stone', 'gold'])
            amount = random.randint(10, 25)
            self.resources.append(Resource(x, y, resource_type, amount))
            self.show_message("Появились новые ресурсы на карте!")
        
        for enemy in self.enemies:
            dx = 0
            dy = 0
            if enemy.x < self.player.x:
                dx = 1
            elif enemy.x > self.player.x:
                dx = -1
            
            if enemy.y < self.player.y:
                dy = 1
            elif enemy.y > self.player.y:
                dy = -1
            
            if random.random() < 0.3:
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
            
            new_x = enemy.x + dx
            new_y = enemy.y + dy
            
            can_move = True
            for building in self.buildings:
                if new_x == building.x and new_y == building.y:
                    can_move = False
                    break
            
            if can_move and 0 <= new_x < self.width and 0 <= new_y < self.height:
                enemy.x = new_x
                enemy.y = new_y
        
        self.trader_spawn_timer -= 1
        if self.trader_spawn_timer <= 0 and self.trader is None:
            if random.random() < 0.25:  # Чаще появляется торговец
                self.spawn_trader()
            self.trader_spawn_timer = random.randint(1000, 2000)
        
        self.chest_spawn_timer -= 1
        if self.chest_spawn_timer <= 0:
            if random.random() < 0.2:  # Чаще появляются сундуки
                self.spawn_chest()
            self.chest_spawn_timer = random.randint(2000, 3000)
            
        self.medkit_spawn_timer -= 1
        if self.medkit_spawn_timer <= 0:
            if random.random() < 0.15:  # Чаще появляются аптечки
                self.spawn_medkit()
            self.medkit_spawn_timer = random.randint(3000, 4000)
    
    def check_day_change(self):
        current_time = time.time()
        if current_time - self.last_day_change >= self.day_duration:
            self.next_day()
    
    def show_message(self, text):
        self.message = text
        self.message_timer = 180
    
    def show_trade_menu(self, options):
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 150, 300, 300)
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if not menu_rect.collidepoint(mouse_pos):
                        return
            
            pygame.draw.rect(screen, (80, 80, 100), menu_rect)
            pygame.draw.rect(screen, WHITE, menu_rect, 2)
            
            title = font_medium.render("Торговец", True, WHITE)
            screen.blit(title, (menu_rect.centerx - title.get_width()//2, menu_rect.y + 20))
            
            option_rects = []
            for i, (text, _) in enumerate(options):
                rect = pygame.Rect(menu_rect.x + 50, menu_rect.y + 60 + i*40, 200, 30)
                option_rects.append(rect)
                
                mouse_pos = pygame.mouse.get_pos()
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (120, 120, 200), rect)
                    if pygame.mouse.get_pressed()[0]:
                        if options[i][1] is not None:
                            options[i][1]()
                            pygame.time.delay(200)
                else:
                    pygame.draw.rect(screen, BLUE, rect)
                
                option_text = font_small.render(text, True, WHITE)
                screen.blit(option_text, (rect.x + 10, rect.y + 5))
            
            pygame.display.flip()
            pygame.time.delay(30)
    
    def show_building_menu(self, building):
        menu_rect = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 100, 300, 200)
        
        upgrade_cost = {
            'house': {'wood': 20 * building.level, 'stone': 15 * building.level, 'gold': 15 * building.level},
            'mine': {'wood': 15 * building.level, 'stone': 20 * building.level, 'gold': 10 * building.level},
            'barracks': {'wood': 25 * building.level, 'stone': 25 * building.level, 'gold': 20 * building.level}
        }.get(building.type, {})
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.show_building_info = None
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if not menu_rect.collidepoint(mouse_pos):
                        self.show_building_info = None
                        return
            
            pygame.draw.rect(screen, (80, 80, 100), menu_rect)
            pygame.draw.rect(screen, WHITE, menu_rect, 2)
            
            title = font_medium.render(f"{building.type} (уровень {building.level})", True, WHITE)
            screen.blit(title, (menu_rect.centerx - title.get_width()//2, menu_rect.y + 20))
            
            cost_text = []
            for res, amount in upgrade_cost.items():
                has_enough = self.player.resources.get(res, 0) >= amount
                color = WHITE if has_enough else RED
                cost_text.append(font_small.render(f"{res}: {amount}", True, color))
            
            for i, text in enumerate(cost_text):
                screen.blit(text, (menu_rect.x + 50, menu_rect.y + 60 + i*20))
            
            upgrade_rect = pygame.Rect(menu_rect.x + 50, menu_rect.y + 120, 200, 40)
            mouse_pos = pygame.mouse.get_pos()
            
            can_upgrade = all(self.player.resources.get(res, 0) >= amount for res, amount in upgrade_cost.items())
            
            if upgrade_rect.collidepoint(mouse_pos) and can_upgrade:
                pygame.draw.rect(screen, (150, 200, 150), upgrade_rect)
                if pygame.mouse.get_pressed()[0]:
                    self.upgrade_building(building)
                    self.show_building_info = None
                    return
            else:
                pygame.draw.rect(screen, (100, 150, 100) if can_upgrade else GRAY, upgrade_rect)
            
            upgrade_text = font_small.render("Улучшить", True, BLACK if upgrade_rect.collidepoint(mouse_pos) and can_upgrade else WHITE)
            screen.blit(upgrade_text, (upgrade_rect.centerx - upgrade_text.get_width()//2, upgrade_rect.centery - upgrade_text.get_height()//2))
            
            pygame.display.flip()
            pygame.time.delay(30)
    
    def update(self):
        self.check_day_change()
        
        if self.message_timer > 0:
            self.message_timer -= 1
        
        if self.trader and random.random() < 0.002:
            self.trader = None
            self.show_message("Торговец ушел...")
        
        if not self.in_battle:
            for enemy in self.enemies:
                if abs(self.player.x - enemy.x) <= 1 and abs(self.player.y - enemy.y) <= 1:
                    self.start_battle(enemy)
                    break
    
    def draw(self, screen):
        screen.fill(BLACK)
        self.draw_map(screen)
        self.draw_panel(screen)
        self.draw_inventory(screen)
        
        if self.message_timer > 0:
            self.draw_message(screen)
        
        if self.show_building_info:
            self.show_building_menu(self.show_building_info)
    
    def draw_map(self, screen):
        start_x = max(0, self.camera_x // TILE_SIZE)
        end_x = min(self.width, (self.camera_x + SCREEN_WIDTH) // TILE_SIZE + 1)
        
        start_y = max(0, self.camera_y // TILE_SIZE)
        end_y = min(self.height, (self.camera_y + SCREEN_HEIGHT - PANEL_HEIGHT) // TILE_SIZE + 1)
        
        ground_rect = pygame.Rect(
            start_x * TILE_SIZE - self.camera_x,
            start_y * TILE_SIZE - self.camera_y,
            (end_x - start_x) * TILE_SIZE,
            (end_y - start_y) * TILE_SIZE
        )
        pygame.draw.rect(screen, GREEN, ground_rect)
        
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
                text = font_small.render(f"{building.type[0].upper()}{building.level}", True, WHITE)
                screen.blit(text, (rect.x + 10, rect.y + 10))
        
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
                screen.blit(text, (rect.x + 15, rect.y + 15))
                
                health_width = int(TILE_SIZE * (enemy.health / 100))
                health_rect = pygame.Rect(rect.x, rect.y - 10, health_width, 5)
                pygame.draw.rect(screen, RED, (rect.x, rect.y - 10, TILE_SIZE, 5))
                pygame.draw.rect(screen, GREEN, health_rect)
                pygame.draw.rect(screen, BLACK, (rect.x, rect.y - 10, TILE_SIZE, 5), 1)
        
        if self.trader and start_x <= self.trader.x < end_x and start_y <= self.trader.y < end_y:
            rect = pygame.Rect(
                self.trader.x * TILE_SIZE - self.camera_x,
                self.trader.y * TILE_SIZE - self.camera_y,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, PURPLE, rect)
            text = font_small.render("T", True, WHITE)
            screen.blit(text, (rect.x + 15, rect.y + 15))
        
        for chest in self.chests:
            if start_x <= chest.x < end_x and start_y <= chest.y < end_y:
                rect = pygame.Rect(
                    chest.x * TILE_SIZE - self.camera_x,
                    chest.y * TILE_SIZE - self.camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(screen, CHEST_COLOR, rect)
                pygame.draw.rect(screen, (100, 70, 40), (rect.x + 5, rect.y + 5, TILE_SIZE - 10, TILE_SIZE - 10))
                text = font_small.render("C", True, WHITE)
                screen.blit(text, (rect.x + 15, rect.y + 15))
                
        for medkit in self.medkits:
            if start_x <= medkit.x < end_x and start_y <= medkit.y < end_y:
                rect = pygame.Rect(
                    medkit.x * TILE_SIZE - self.camera_x,
                    medkit.y * TILE_SIZE - self.camera_y,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(screen, MEDKIT_COLOR, rect)
                pygame.draw.rect(screen, (255, 150, 150), (rect.x + 5, rect.y + 5, TILE_SIZE - 10, TILE_SIZE - 10))
                text = font_small.render(f"+{medkit.heal_amount}", True, WHITE)
                screen.blit(text, (rect.x + 5, rect.y + 5))
        
        if start_x <= self.player.x < end_x and start_y <= self.player.y < end_y:
            rect = pygame.Rect(
                self.player.x * TILE_SIZE - self.camera_x,
                self.player.y * TILE_SIZE - self.camera_y,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, YELLOW, rect)
            text = font_small.render("P", True, BLACK)
            screen.blit(text, (rect.x + 15, rect.y + 15))
            
            health_width = int(TILE_SIZE * (self.player.health / self.player.max_health))
            health_rect = pygame.Rect(rect.x, rect.y - 10, health_width, 5)
            pygame.draw.rect(screen, RED, (rect.x, rect.y - 10, TILE_SIZE, 5))
            pygame.draw.rect(screen, GREEN, health_rect)
            pygame.draw.rect(screen, BLACK, (rect.x, rect.y - 10, TILE_SIZE, 5), 1)
    
    def draw_panel(self, screen):
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - PANEL_HEIGHT, SCREEN_WIDTH, PANEL_HEIGHT)
        pygame.draw.rect(screen, (40, 40, 40), panel_rect)
        
        day_text = font_medium.render(f"День: {self.day}", True, WHITE)
        screen.blit(day_text, (20, SCREEN_HEIGHT - PANEL_HEIGHT + 20))
        
        health_text = font_medium.render(f"Здоровье: {self.player.health}/{self.player.max_health}", True, WHITE)
        screen.blit(health_text, (20, SCREEN_HEIGHT - PANEL_HEIGHT + 50))
        
        attack_text = font_medium.render(f"Атака: {self.player.attack}", True, WHITE)
        screen.blit(attack_text, (20, SCREEN_HEIGHT - PANEL_HEIGHT + 80))
        
        self.draw_button(screen, 200, SCREEN_HEIGHT - PANEL_HEIGHT + 70, 120, 30, "Построить дом", 'house')
        self.draw_button(screen, 350, SCREEN_HEIGHT - PANEL_HEIGHT + 70, 120, 30, "Улучшить атаку", 'upgrade')
    
    def draw_inventory(self, screen):
        inventory_rect = pygame.Rect(SCREEN_WIDTH, 0, INVENTORY_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, (50, 50, 70), inventory_rect)
        pygame.draw.rect(screen, WHITE, inventory_rect, 2)
        
        title = font_medium.render("Инвентарь", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH + (INVENTORY_WIDTH - title.get_width()) // 2, 20))
        
        resources_title = font_small.render("Ресурсы:", True, WHITE)
        screen.blit(resources_title, (SCREEN_WIDTH + 20, 60))
        
        y_offset = 90
        for res, amount in self.player.resources.items():
            res_text = font_small.render(f"{res}: {amount}", True, WHITE)
            screen.blit(res_text, (SCREEN_WIDTH + 30, y_offset))
            y_offset += 25
        
        weapons_title = font_small.render("Оружие:", True, WHITE)
        screen.blit(weapons_title, (SCREEN_WIDTH + 20, y_offset + 20))
        y_offset += 50
        
        for i, weapon in enumerate(self.player.weapons):
            weapon_rect = pygame.Rect(SCREEN_WIDTH + 30, y_offset, 140, 30)
            color = BLUE if weapon == self.player.equipped_weapon else (80, 80, 100)
            pygame.draw.rect(screen, color, weapon_rect)
            
            weapon_text = font_small.render(weapon.capitalize(), True, WHITE)
            screen.blit(weapon_text, (weapon_rect.x + 10, weapon_rect.y + 5))
            
            mouse_pos = pygame.mouse.get_pos()
            if weapon_rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]:
                self.player.equipped_weapon = weapon
                self.update_player_attack()
                pygame.time.delay(200)
            
            y_offset += 40
    
    def draw_button(self, screen, x, y, width, height, text, action):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        button_rect = pygame.Rect(x, y, width, height)
        
        if button_rect.collidepoint(mouse):
            pygame.draw.rect(screen, (200, 200, 200), button_rect)
            if click[0] == 1:
                if action == 'house':
                    self.build('house')
                elif action == 'upgrade':
                    msg = self.player.upgrade_attack()
                    self.show_message(msg)
        else:
            pygame.draw.rect(screen, (100, 100, 100), button_rect)
        
        text_surf = font_small.render(text, True, BLACK if button_rect.collidepoint(mouse) else WHITE)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)
    
    def draw_message(self, screen):
        message_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 20, 400, 40)
        pygame.draw.rect(screen, (50, 50, 100), message_rect)
        pygame.draw.rect(screen, WHITE, message_rect, 2)
        
        text_surf = font_medium.render(self.message, True, WHITE)
        text_rect = text_surf.get_rect(center=message_rect.center)
        screen.blit(text_surf, text_rect)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_health = 100
        self.health = self.max_health
        self.attack = 10
        self.resources = {'wood': 0, 'stone': 0, 'gold': 0}
        self.weapons = []
        self.equipped_weapon = None
    
    def upgrade_attack(self):
        if self.resources.get('gold', 0) >= 15:
            self.resources['gold'] -= 15
            self.attack += 3
            return f"Атака улучшена до {self.attack}!"
        else:
            return "Нужно 15 золота для улучшения атаки"

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
    
    def upgrade(self):
        self.level += 1

class Enemy:
    def __init__(self, x, y, health, attack):
        self.x = x
        self.y = y
        self.health = health
        self.attack = attack

class Trader:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Chest:
    def __init__(self, x, y, contents):
        self.x = x
        self.y = y
        self.contents = contents

class Medkit:
    def __init__(self, x, y, heal_amount):
        self.x = x
        self.y = y
        self.heal_amount = heal_amount

def main():
    clock = pygame.time.Clock()
    game = Game()
    game.center_camera()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_w or event.key == K_UP:
                    game.move_player(0, -1)
                elif event.key == K_s or event.key == K_DOWN:
                    game.move_player(0, 1)
                elif event.key == K_a or event.key == K_LEFT:
                    game.move_player(-1, 0)
                elif event.key == K_d or event.key == K_RIGHT:
                    game.move_player(1, 0)
                elif event.key == K_u:
                    msg = game.player.upgrade_attack()
                    game.show_message(msg)
                elif event.key == K_SPACE:
                    if game.in_battle:
                        game.player_attack()
                    else:
                        for enemy in game.enemies:
                            if abs(game.player.x - enemy.x) <= 1 and abs(game.player.y - enemy.y) <= 1:
                                game.start_battle(enemy)
                                break
                        for resource in game.resources[:]:
                            if game.player.x == resource.x and game.player.y == resource.y and resource.type != 'gold':
                                game.player.resources[resource.type] += resource.amount
                                game.show_message(f"Добыто {resource.amount} {resource.type}!")
                                game.resources.remove(resource)
                                break
        
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()