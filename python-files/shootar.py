import pygame
import random
import sys

pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Платформер с улучшениями героя и врагов")
clock = pygame.time.Clock()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

# Статистика игрока и апгрейды
player_stats = {
    'speed': 5,
    'jump_power': 15,
    'max_health': 100,
    'damage': 10
}
upgrades = {
    'speed': {'level': 1, 'cost': 10},
    'jump': {'level': 1, 'cost': 10},
    'health': {'level': 1, 'cost': 15},
    'damage': {'level': 1, 'cost': 20},
    'special_ability': {'unlocked': False, 'cost': 50}
}
player_resources = 100

# --- Классы ---

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height=20):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.lifetime = None

    def update(self):
        if self.lifetime:
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.kill()

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height=20, speed=2, horizontal=True):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.horizontal = horizontal

    def update(self):
        super().update()
        if self.horizontal:
            self.rect.x += self.speed
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.speed *= -1
        else:
            self.rect.y += self.speed
            if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
                self.speed *= -1

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width=40, height=40):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))

class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y, size=20):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.create_coin_image()
        self.rect = self.image.get_rect(center=(x, y))

    def create_coin_image(self):
        radius = 10
        for r in range(radius, 0, -1):
            color_value = 255 - int(r * 15)
            color = (255, color_value, 0, 255)
            pygame.draw.circle(self.image, color, (10, 10), r)
        pygame.draw.circle(self.image, (255, 255, 255, 128), (6, 6), 3)

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, bonus_type):
        super().__init__()
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.bonus_type = bonus_type
        color_map = {
            'shield': (0, 0, 255),
            'magnet': CYAN,
            'score': (0, 255, 255),
            'speed': ORANGE,
            'invincibility': YELLOW
        }
        self.image.fill(color_map.get(bonus_type, WHITE))
        self.rect = self.image.get_rect(center=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_size = 30
        self.image = pygame.Surface((self.original_size, self.original_size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (self.original_size // 2, self.original_size // 2), self.original_size // 2)
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 100))
        self.vel_x = 0
        self.vel_y = 0
        self.stats = player_stats.copy()
        self.speed = self.stats['speed']
        self.jump_power = self.stats['jump_power']
        self.max_health = self.stats['max_health']
        self.current_health = self.max_health
        self.damage = self.stats['damage']
        self.on_ground = False
        self.score = 0

        # Эффекты
        self.invincible = False
        self.invincible_timer = 0
        self.magnet_active = False
        self.magnet_timer = 0
        self.speed_bonus_active = False
        self.speed_timer = 0
        self.base_speed = self.speed

        self.is_flashing = False
        self.flash_counter = 0
        self.flash_duration = FPS // 2
        self.original_image = self.image.copy()

        self.colors = {
            'normal': GREEN,
            'invincible': (0, 255, 255),
            'speed': ORANGE
        }

        self.is_crouching = False  # Инициализация

    def update(self):
        # Таймеры эффектов
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        if self.magnet_active:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.magnet_active = False
        if self.speed_bonus_active:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed -= 2
                if self.speed <= self.base_speed:
                    self.speed = self.base_speed
                    self.speed_bonus_active = False
                self.update_color()

        # Мигание при уроне
        if self.is_flashing:
            self.flash_counter += 1
            if self.flash_counter % 10 < 5:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
            if self.flash_counter >= self.flash_duration:
                self.is_flashing = False
                self.image.set_alpha(255)
                self.flash_counter = 0

        # Управление
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -self.jump_power
        if keys[pygame.K_DOWN]:
            if not self.is_crouching:
                self.is_crouching = True
                self.scale_player(0.6)
        else:
            if self.is_crouching:
                self.is_crouching = False
                self.scale_player(1.0)

        # Гравитация
        self.vel_y += 0.8
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)

        # Границы
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top > HEIGHT:
            self.rect.bottom = HEIGHT
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.update_color()

    def scale_player(self, scale):
        old_center = self.rect.center
        size = int(self.original_size * scale)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.get_current_color(), (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=old_center)

    def get_current_color(self):
        if self.invincible:
            return self.colors['invincible']
        elif self.speed_bonus_active:
            return self.colors['speed']
        return self.colors['normal']

    def update_color(self):
        self.image.fill((0, 0, 0, 0))
        size = self.rect.width
        pygame.draw.circle(self.image, self.get_current_color(), (size // 2, size // 2), size // 2)

    def jump(self):
        if self.on_ground:
            self.vel_y = -self.jump_power

    def activate_invincibility(self, duration):
        self.invincible = True
        self.invincible_timer = duration
        self.is_flashing = True
        self.flash_counter = 0
        self.update_color()

    def activate_speed_bonus(self, duration, speed_increase=2):
        self.speed += speed_increase
        self.speed_timer = duration
        self.speed_bonus_active = True
        self.update_color()

    def upgrade_stat(self, stat_name):
        global player_resources
        if stat_name == 'speed':
            level = upgrades['speed']['level']
            cost = upgrades['speed']['cost']
            if player_resources >= cost:
                player_resources -= cost
                upgrades['speed']['level'] += 1
                self.stats['speed'] += 1
                self.speed = self.stats['speed']
                return True
        elif stat_name == 'jump':
            level = upgrades['jump']['level']
            cost = upgrades['jump']['cost']
            if player_resources >= cost:
                player_resources -= cost
                upgrades['jump']['level'] += 1
                self.stats['jump_power'] += 1
                self.jump_power = self.stats['jump_power']
                return True
        elif stat_name == 'health':
            level = upgrades['health']['level']
            cost = upgrades['health']['cost']
            if player_resources >= cost:
                player_resources -= cost
                upgrades['health']['level'] += 1
                self.stats['max_health'] += 10
                self.current_health = self.stats['max_health']
                return True
        elif stat_name == 'damage':
            level = upgrades['damage']['level']
            cost = upgrades['damage']['cost']
            if player_resources >= cost:
                player_resources -= cost
                upgrades['damage']['level'] += 1
                self.stats['damage'] += 2
                self.damage = self.stats['damage']
                return True
        return False

    def unlock_special_ability(self):
        global player_resources
        if not upgrades['special_ability']['unlocked']:
            cost = upgrades['special_ability']['cost']
            if player_resources >= cost:
                player_resources -= cost
                upgrades['special_ability']['unlocked'] = True
                return True
        return False

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            self.die()
        self.is_flashing = True
        self.flash_counter = 0
        self.update_color()

    def die(self):
        print("Герой погиб. Игра окончена.")
        pygame.quit()
        sys.exit()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2, health=30, damage=5, patrol_range=100):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.health = health
        self.damage = damage
        self.start_x = x
        self.patrol_range = patrol_range
        self.direction = 1

    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) >= self.patrol_range:
            self.direction *= -1

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()

# --- Генерация уровня ---
def generate_level(level):
    platforms = pygame.sprite.Group()
    platforms.add(Platform(0, HEIGHT - 40, WIDTH, 40))
    num_platforms = 8 + level * 2
    for _ in range(num_platforms):
        w = random.randint(80, 200)
        x = random.randint(0, WIDTH - w)
        y = random.randint(100, HEIGHT - 150)
        if random.random() < 0.4:
            speed = random.choice([2 + level, -2 - level])
            horizontal = random.random() < 0.5
            platforms.add(MovingPlatform(x, y, w, 20, speed=speed, horizontal=horizontal))
        else:
            platforms.add(Platform(x, y, w))
    # Добавляем препятствия
    for _ in range(level + 4):
        w, h = random.randint(20, 60), random.randint(20, 60)
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 150)
        platforms.add(Obstacle(x, y, w, h))
    # Шипы
    for _ in range(level + 2):
        size = random.randint(20, 30)
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 100)
        platforms.add(Spike(x, y, size))
    # Исчезающие платформы
    for _ in range(level // 2):
        w = random.randint(100, 150)
        x = random.randint(50, WIDTH - 150)
        y = random.randint(150, HEIGHT - 200)
        p = Platform(x, y, w, 20)
        p.lifetime = FPS * 3
        platforms.add(p)
    # Границы
    platforms.add(Platform(0, 0, 10, HEIGHT))
    platforms.add(Platform(WIDTH - 10, 0, 10, HEIGHT))
    return platforms

def create_level_objects(level, platforms):
    coins = pygame.sprite.Group()
    for _ in range(12 + level * 3):
        while True:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 150)
            temp_rect = pygame.Rect(x - 10, y - 10, 20, 20)
            if not any(obstacle.rect.colliderect(temp_rect) for obstacle in platforms):
                break
        coins.add(Coin(x, y))
    enemies = pygame.sprite.Group()
    for _ in range(2 + level):
        x = random.randint(50, WIDTH - 50)
        y = HEIGHT - 80
        speed_value = random.choice([3 + level, -3 - level])
        patrol_range = random.randint(50, 150)
        enemies.add(Enemy(x, y, speed=speed_value, patrol_range=patrol_range))
    bonuses = pygame.sprite.Group()
    for _ in range(2):
        bonus_type = random.choice(['shield', 'magnet', 'score', 'speed', 'invincibility'])
        while True:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 150)
            temp_rect = pygame.Rect(x - 15, y - 15, 30, 30)
            if not any(obstacle.rect.colliderect(temp_rect) for obstacle in platforms):
                break
        bonuses.add(Bonus(x, y, bonus_type))
    return coins, enemies, bonuses

def draw_active_bonuses(surface, player):
    font = pygame.font.SysFont(None, 24)
    y_offset = 10
    if player.invincible:
        surface.blit(font.render("Неуязвимость: ∞", True, WHITE), (10, y_offset))
        y_offset += 25
    if player.magnet_active:
        surface.blit(font.render(f"Магнит: {player.magnet_timer // FPS}s", True, WHITE), (10, y_offset))
        y_offset += 25
    if player.speed_bonus_active:
        surface.blit(font.render(f"Ускорение: {player.speed_timer // FPS}s", True, WHITE), (10, y_offset))
        y_offset += 25

def show_upgrade_menu(screen, player):
    global player_resources
    font = pygame.font.SysFont(None, 24)
    menu_active = True

    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False
                elif event.key == pygame.K_1:
                    if player.upgrade_stat('speed'):
                        print("Скорость улучшена!")
                elif event.key == pygame.K_2:
                    if player.upgrade_stat('jump'):
                        print("Прыжок улучшен!")
                elif event.key == pygame.K_3:
                    if player.upgrade_stat('health'):
                        print("Здоровье улучшено!")
                elif event.key == pygame.K_4:
                    if player.upgrade_stat('damage'):
                        print("Урон увеличен!")
                elif event.key == pygame.K_s:
                    if player.unlock_special_ability():
                        print("Специальная способность разблокирована!")

        # Визуальное меню
        screen.fill(BLACK)
        y = 50
        lines = [
            f"Очки: {player.score}",
            "Нажмите:",
            "1 - Улучшить скорость (уровень {})".format(upgrades['speed']['level']),
            "2 - Улучшить прыжок (уровень {})".format(upgrades['jump']['level']),
            "3 - Улучшить здоровье (уровень {})".format(upgrades['health']['level']),
            "4 - Улучшить урон (уровень {})".format(upgrades['damage']['level']),
            "S - Разблокировать спец. способность (стоимость {})".format(upgrades['special_ability']['cost']),
            "ESC - Выйти"
        ]
        for line in lines:
            text = font.render(line, True, WHITE)
            surface_rect = text.get_rect(topleft=(50, y))
            screen.blit(text, surface_rect)
            y += 30
        pygame.display.flip()
        clock.tick(FPS)

def main():
    global player_resources
    level = 1
    player = Player()

    all_sprites = pygame.sprite.Group()
    platforms = generate_level(level)
    coins, enemies, bonuses = create_level_objects(level, platforms)
    all_sprites.add(platforms, coins, bonuses, player)
    for enemy in enemies:
        all_sprites.add(enemy)

    # Защита
    player.activate_invincibility(3 * FPS)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_u:
                    show_upgrade_menu(screen, player)

        all_sprites.update()

        # Коллизии с платформами
        player.on_ground = False
        for platform in platforms:
            if player.rect.colliderect(platform.rect):
                if player.vel_y > 0 and player.rect.bottom - player.vel_y <= platform.rect.top + 5:
                    player.rect.bottom = platform.rect.top
                    player.vel_y = 0
                    player.on_ground = True

        # Магнит
        if player.magnet_active:
            for coin in coins:
                dist = ((coin.rect.centerx - player.rect.centerx) ** 2 + (coin.rect.centery - player.rect.centery) ** 2) ** 0.5
                if dist < 100:
                    dx = (player.rect.centerx - coin.rect.centerx) * 0.1
                    dy = (player.rect.centery - coin.rect.centery) * 0.1
                    coin.rect.x += int(dx)
                    coin.rect.y += int(dy)

        # Собираем монеты
        collected_coins = pygame.sprite.spritecollide(player, coins, True)
        player.score += len(collected_coins) * 10

        # Враги
        if not player.invincible:
            if pygame.sprite.spritecollideany(player, enemies):
                print("Вы проиграли! Герой погиб.")
                running = False

        # Враг атакует героя
        for enemy in enemies:
            if enemy.rect.colliderect(player.rect):
                print("Герой получил 10 урона!")
                player.take_damage(10)

        # Бонусы
        collided_bonuses = pygame.sprite.spritecollide(player, bonuses, True)
        for bonus in collided_bonuses:
            if bonus.bonus_type == 'score':
                player.score += 50
            elif bonus.bonus_type == 'shield':
                print("Щит активирован!")
            elif bonus.bonus_type == 'magnet':
                print("Магнит активирован!")
                player.magnet_active = True
                player.magnet_timer = FPS * 5
            elif bonus.bonus_type == 'speed':
                print("Ускорение!")
                player.activate_speed_bonus(FPS * 5, speed_increase=2)
            elif bonus.bonus_type == 'invincibility':
                print("Неуязвимость!")
                player.activate_invincibility(FPS * 5)

        # Исчезающие платформы
        for p in platforms:
            if hasattr(p, 'lifetime') and p.lifetime is not None:
                p.lifetime -= 1
                if p.lifetime <= 0:
                    p.kill()

        # Переход на следующий уровень
        if len(coins) == 0:
            print(f"Переход на уровень {level + 1}")
            level += 1
            platforms = generate_level(level)
            coins, enemies, bonuses = create_level_objects(level, platforms)
            all_sprites.empty()
            all_sprites.add(platforms, coins, bonuses, player)
            for enemy in enemies:
                all_sprites.add(enemy)
            player.activate_invincibility(3 * FPS)

        # Рендеринг
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_active_bonuses(screen, player)

        # HUD
        font = pygame.font.SysFont(None, 36)
        screen.blit(font.render(f"Очки: {player.score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Ресурсы: {player_resources}", True, WHITE), (WIDTH - 200, 10))
        screen.blit(font.render(f"Здоровье: {player.current_health}/{player.stats['max_health']}", True, WHITE), (10, 50))
        # Характеристики
        y_off = 80
        for key in ['speed', 'jump_power', 'damage']:
            text = font.render(f"{key}: {player.stats[key]}", True, WHITE)
            screen.blit(text, (WIDTH - 250, y_off))
            y_off += 25

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()