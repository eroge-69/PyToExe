import pygame
import math
import random
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PS1 Style Horror")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
BROWN = (101, 67, 33)
LIGHT_BROWN = (150, 111, 51)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)

# Шрифт
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 16)

# Текстуры для стен
def create_texture(color, size=64):
    texture = pygame.Surface((size, size))
    texture.fill(color)
    for i in range(size):
        for j in range(size):
            if random.random() > 0.7:
                noise = random.randint(-10, 10)
                new_color = (
                    max(0, min(255, color[0] + noise)),
                    max(0, min(255, color[1] + noise)),
                    max(0, min(255, color[2] + noise))
                )
                texture.set_at((i, j), new_color)
    return texture

# Создание текстур
wall_texture = create_texture(BROWN)
floor_texture = create_texture(DARK_GRAY)
fridge_texture = create_texture(WHITE)
store_texture = create_texture(LIGHT_BROWN)
food_texture = create_texture(GREEN)

# Игрок
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.fov = math.pi / 3
        self.speed = 0.05
        self.rot_speed = 0.03
        self.health = 100
        self.has_food = False
        self.is_looking_at_fridge = False
        self.is_in_store = False

    def move(self, map_data, dx, dy):
        # Проверка столкновений
        if 0 <= int(self.x + dx) < len(map_data[0]) and 0 <= int(self.y + dy) < len(map_data):
            if map_data[int(self.y + dy)][int(self.x + dx)] == 0:
                self.x += dx
                self.y += dy

    def cast_ray(self, map_data, ray_angle):
        # Бросок луча для определения расстояния до стены
        ray_x, ray_y = self.x, self.y
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)
        
        distance = 0
        max_distance = 20
        
        while distance < max_distance:
            ray_x += ray_dir_x * 0.05
            ray_y += ray_dir_y * 0.05
            distance += 0.05
            
            # Проверка выхода за границы карты
            if ray_x < 0 or ray_x >= len(map_data[0]) or ray_y < 0 or ray_y >= len(map_data):
                return max_distance, 0
            
            # Проверка столкновения со стеной
            if map_data[int(ray_y)][int(ray_x)] != 0:
                # Определение типа стены для текстуры
                wall_type = map_data[int(ray_y)][int(ray_x)]
                return distance, wall_type
        
        return max_distance, 0

    def render(self, screen, map_data):
        # Рендеринг 3D сцены
        for x in range(WIDTH):
            # Вычисление угла луча
            ray_angle = self.angle - self.fov / 2 + (x / WIDTH) * self.fov
            
            # Бросок луча
            distance, wall_type = self.cast_ray(map_data, ray_angle)
            
            # Коррекция искажения (fisheye)
            distance = distance * math.cos(ray_angle - self.angle)
            
            # Вычисление высоты стены
            wall_height = min(int(HEIGHT / (distance + 0.0001)), HEIGHT * 5)
            
            # Определение цвета стены в зависимости от расстояния
            if wall_type == 1:
                color = BROWN
                texture = wall_texture
            elif wall_type == 2:
                color = WHITE
                texture = fridge_texture
            elif wall_type == 3:
                color = LIGHT_BROWN
                texture = store_texture
            elif wall_type == 4:
                color = GREEN
                texture = food_texture
            else:
                color = BLACK
            
            # Рисование текстурированной стены
            if distance < 20:
                # Вычисление смещения текстуры
                wall_offset = int((ray_angle * 10) % texture.get_width())
                
                # Масштабирование текстуры
                wall_slice = pygame.transform.scale(texture, (1, wall_height))
                
                # Рисование среза стены
                screen.blit(wall_slice, (x, HEIGHT // 2 - wall_height // 2), 
                           (wall_offset, 0, 1, texture.get_height()))
            
            # Рисование пола и потолка
            pygame.draw.rect(screen, DARK_GRAY, (x, 0, 1, HEIGHT // 2 - wall_height // 2))
            pygame.draw.rect(screen, GRAY, (x, HEIGHT // 2 + wall_height // 2, 1, HEIGHT))

    def check_interaction(self, map_data):
        # Проверка взаимодействия с объектами
        int_x, int_y = int(self.x), int(self.y)
        
        # Проверка холодильника
        for y in range(max(0, int_y-1), min(len(map_data), int_y+2)):
            for x in range(max(0, int_x-1), min(len(map_data[0]), int_x+2)):
                if map_data[y][x] == 2:  # Холодильник
                    self.is_looking_at_fridge = True
                    return
                
                if map_data[y][x] == 4 and self.is_in_store:  # Еда в магазине
                    self.has_food = True
                    map_data[y][x] = 0  # Убираем еду с карты
                    return
        
        self.is_looking_at_fridge = False

# Враги
class Enemy:
    def __init__(self, x, y, speed=0.02):
        self.x = x
        self.y = y
        self.speed = speed
        self.visible = False
        self.attack_cooldown = 0
    
    def move_towards(self, target_x, target_y, map_data):
        # Простое преследование игрока
        dx = target_x - self.x
        dy = target_y - self.y
        dist = max(0.0001, math.sqrt(dx*dx + dy*dy))
        
        dx /= dist
        dy /= dist
        
        # Проверка столкновений
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        if 0 <= int(new_x) < len(map_data[0]) and 0 <= int(new_y) < len(map_data):
            if map_data[int(new_y)][int(new_x)] == 0:
                self.x = new_x
                self.y = new_y
    
    def render(self, screen, player):
        # Рендеринг врага, если он видим
        if self.visible:
            # Проекция врага на экран
            dx = self.x - player.x
            dy = self.y - player.y
            
            # Угол между игроком и врагом
            enemy_angle = math.atan2(dy, dx) - player.angle
            
            # Ограничение угла
            while enemy_angle > math.pi:
                enemy_angle -= 2 * math.pi
            while enemy_angle < -math.pi:
                enemy_angle += 2 * math.pi
            
            # Расстояние до врага
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Если враг в поле зрения
            if abs(enemy_angle) < player.fov / 2 and dist < 10:
                # Позиция на экране
                screen_x = int((enemy_angle + player.fov / 2) / player.fov * WIDTH)
                
                # Размер врага на экране
                size = int(100 / dist)
                
                # Рисование врага
                pygame.draw.rect(screen, RED, 
                                (screen_x - size//2, 
                                 HEIGHT//2 - size//2, 
                                 size, size))
                
                # Атака, если близко
                if dist < 0.5 and self.attack_cooldown <= 0:
                    player.health -= 10
                    self.attack_cooldown = 30

# Создание карты дома
def create_house_map():
    return [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

# Создание карты магазина
def create_store_map():
    return [
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
        [3, 0, 0, 0, 0, 0, 0, 0, 4, 3],
        [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    ]

# Основная функция игры
def main():
    clock = pygame.time.Clock()
    
    # Инициализация игрока
    player = Player(1.5, 1.5)
    
    # Создание карт
    house_map = create_house_map()
    store_map = create_store_map()
    
    # Добавление холодильника в дом
    house_map[2][7] = 2
    
    # Текущая карта
    current_map = house_map
    
    # Враги
    enemies = [
        Enemy(8.5, 8.5, 0.03),  # Враг в доме
        Enemy(5.5, 5.5, 0.02)   # Враг снаружи
    ]
    
    # Состояния игры
    game_state = "start"  # start, playing, game_over, win
    message = ""
    message_timer = 0
    
    # Главный игровой цикл
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN and game_state == "start":
                    game_state = "playing"
                    message = "Осмотритесь. Холодильник пуст... Нужно сходить в магазин."
                    message_timer = 200
                elif event.key == pygame.K_e and game_state == "playing":
                    player.check_interaction(current_map)
                    if player.is_looking_at_fridge and not player.has_food:
                        message = "Холодильник пуст. Нужно сходить в магазин за едой."
                        message_timer = 150
                    elif player.is_looking_at_fridge and player.has_food:
                        game_state = "win"
                        message = "Вы поели и выжили! Победа!"
                    elif player.is_in_store and not player.has_food:
                        message = "Вы в магазине. Найдите еду (зеленый квадрат)."
                        message_timer = 150
                    elif player.is_in_store and player.has_food:
                        message = "У вас есть еда! Возвращайтесь домой быстро!"
                        message_timer = 150
                        current_map = house_map
                        player.is_in_store = False
                        player.x, player.y = 8.5, 8.5
                        # Активируем врагов при выходе из магазина
                        for enemy in enemies:
                            enemy.visible = True
        
        if game_state == "playing":
            # Обработка движения игрока
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_w]:
                player.move(current_map, math.cos(player.angle) * player.speed, math.sin(player.angle) * player.speed)
            if keys[pygame.K_s]:
                player.move(current_map, -math.cos(player.angle) * player.speed, -math.sin(player.angle) * player.speed)
            if keys[pygame.K_a]:
                player.move(current_map, math.cos(player.angle - math.pi/2) * player.speed, math.sin(player.angle - math.pi/2) * player.speed)
            if keys[pygame.K_d]:
                player.move(current_map, math.cos(player.angle + math.pi/2) * player.speed, math.sin(player.angle + math.pi/2) * player.speed)
            
            if keys[pygame.K_LEFT]:
                player.angle -= player.rot_speed
            if keys[pygame.K_RIGHT]:
                player.angle += player.rot_speed
            
            # Проверка перехода в магазин
            if not player.is_in_store and player.x > 8.5 and player.y > 8.5:
                current_map = store_map
                player.is_in_store = True
                player.x, player.y = 1.5, 1.5
                message = "Вы в магазине. Найдите еду (зеленый квадрат)."
                message_timer = 150
            
            # Проверка перехода в дом
            if player.is_in_store and player.x < 1.0 and player.y < 1.0:
                current_map = house_map
                player.is_in_store = False
                player.x, player.y = 8.5, 8.5
            
            # Движение врагов
            for enemy in enemies:
                if enemy.visible:
                    enemy.move_towards(player.x, player.y, current_map)
                    if enemy.attack_cooldown > 0:
                        enemy.attack_cooldown -= 1
            
            # Проверка здоровья игрока
            if player.health <= 0:
                game_state = "game_over"
                message = "Вас поймали! Игра окончена."
        
        # Очистка экрана
        screen.fill(BLACK)
        
        if game_state == "start":
            # Экран начала игры
            title = font.render("PS1 Style Horror Game", True, RED)
            instruction = font.render("Нажмите ENTER чтобы начать", True, WHITE)
            story = small_font.render("Вы проснулись голодным. Холодильник пуст...", True, WHITE)
            story2 = small_font.render("Вам нужно сходить в магазин, но будьте осторожны!", True, WHITE)
            
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2))
            screen.blit(story, (WIDTH//2 - story.get_width()//2, HEIGHT//2 + 50))
            screen.blit(story2, (WIDTH//2 - story2.get_width()//2, HEIGHT//2 + 80))
        
        elif game_state == "playing":
            # Рендеринг 3D сцены
            player.render(screen, current_map)
            
            # Рендеринг врагов
            for enemy in enemies:
                enemy.render(screen, player)
            
            # Интерфейс
            health_text = font.render(f"Здоровье: {player.health}", True, GREEN)
            screen.blit(health_text, (10, 10))
            
            if player.has_food:
                food_text = font.render("Еда: есть", True, GREEN)
            else:
                food_text = font.render("Еда: нет", True, RED)
            screen.blit(food_text, (10, 40))
            
            # Подсказка взаимодействия
            interact_text = small_font.render("Нажмите E для взаимодействия", True, YELLOW)
            screen.blit(interact_text, (WIDTH//2 - interact_text.get_width()//2, HEIGHT - 30))
            
            # Сообщение
            if message_timer > 0:
                msg_text = small_font.render(message, True, WHITE)
                screen.blit(msg_text, (WIDTH//2 - msg_text.get_width()//2, HEIGHT - 60))
                message_timer -= 1
        
        elif game_state == "game_over":
            # Экран проигрыша
            over_text = font.render("ИГРА ОКОНЧЕНА", True, RED)
            restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
            
            screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//3))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # Перезапуск игры
                player = Player(1.5, 1.5)
                player.has_food = False
                player.is_looking_at_fridge = False
                player.is_in_store = False
                
                house_map = create_house_map()
                house_map[2][7] = 2
                current_map = house_map
                
                enemies = [
                    Enemy(8.5, 8.5, 0.03),
                    Enemy(5.5, 5.5, 0.02)
                ]
                
                game_state = "playing"
        
        elif game_state == "win":
            # Экран победы
            win_text = font.render("ПОБЕДА! Вы survived!", True, GREEN)
            restart_text = font.render("Нажмите R для перезапуска", True, WHITE)
            
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//3))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                # Перезапуск игры
                player = Player(1.5, 1.5)
                player.has_food = False
                player.is_looking_at_fridge = False
                player.is_in_store = False
                
                house_map = create_house_map()
                house_map[2][7] = 2
                current_map = house_map
                
                enemies = [
                    Enemy(8.5, 8.5, 0.03),
                    Enemy(5.5, 5.5, 0.02)
                ]
                
                game_state = "playing"
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()