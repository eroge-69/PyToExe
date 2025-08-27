import pygame
import sys
import random
import math

# Инициализация pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Кликер с сундуками и анимациями")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (100, 200, 100)
RED = (200, 100, 100)
BLUE = (100, 100, 200)
DARK_BLUE = (70, 70, 150)
PURPLE = (150, 100, 200)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)
DARK_GRAY = (80, 80, 80)

# Шрифты
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 48)

# Игровые переменные
clicks = 0
click_power = 1
auto_clicks = 0
current_screen = "main"
chest_progress = 0
chest_goal = 50
chest_available = False
show_chest_reward = False
chest_reward_text = ""
chest_reward_desc = ""
explosion_active = False
explosion_timer = 0
explosion_duration = 10000
button_broken = False
button_break_timer = 0
button_break_duration = 3000
button_pieces = []
show_anton_message = False
anton_message_timer = 0
anton_message_duration = 2000
last_auto_click = pygame.time.get_ticks()
button_move_timer = 0
button_move_delay = 2000  # кнопка движется каждые 2 секунды
button_dx = random.uniform(-1, 1)
button_dy = random.uniform(-1, 1)

# Демотивирующие фразы робота
demotivational_phrases = [
    "У тебя не получится.",
    "Сдавайся.",
    "Это тебе не по силам.",
    "Ты никогда не достигнешь 1000.",
    "Лучше закрой игру.",
    "Твои усилия бесполезны.",
    "Даже не пытайся.",
    "Ты обречен на провал.",
    "Зачем ты продолжаешь?",
    "Это безнадежно."
]
current_phrase = ""
phrase_timer = 0
phrase_duration = 4000

# Анимации
knives = []
explosion_particles = []
hovered_upgrade = None

# Перманентные улучшения
permanent_upgrades = {
    "double_clicks": {
        "name": "Двойные клики", 
        "active": False, 
        "multiplier": 2,
        "desc": "Удваивает силу каждого вашего клика"
    },
    "auto_boost": {
        "name": "Ускорение автокликов", 
        "active": False, 
        "multiplier": 1.5,
        "desc": "Увеличивает эффективность автокликеров на 50%"
    },
    "chest_discount": {
        "name": "Скидка на сундуки", 
        "active": False, 
        "multiplier": 0.8,
        "desc": "Уменьшает требуемое количество кликов для сундука на 20%"
    },
    "explosion_perk": {
        "name": "Взрывная кнопка", 
        "active": False, 
        "multiplier": 2,
        "desc": "Раз в 2 минуты можно активировать взрыв (x2 к кликам на 10 сек)",
        "cooldown": 120000,
        "last_used": 0
    }
}

# Улучшения (без дубликатов и без улучшенного автокликера)
upgrades = [
    {"name": "Усилитель клика", "cost": 15, "power": 1, "count": 0, "type": "click", "desc": "Увеличивает силу клика на +1"},
    {"name": "Автокликер", "cost": 30, "power": 0.5, "count": 0, "type": "auto", "desc": "Автоматически генерирует 0.5 очка/сек"},
    {"name": "Мощный клик", "cost": 200, "power": 5, "count": 0, "type": "click", "desc": "Увеличивает силу клика на +5"}
]

# Кнопки
main_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 100)
original_button_pos = (WIDTH // 2 - 100, 200)
shop_button = pygame.Rect(WIDTH // 2 - 100, 350, 200, 60)
back_button = pygame.Rect(20, 20, 120, 40)
chest_button = pygame.Rect(WIDTH - 120, 20, 100, 100)
close_reward_button = pygame.Rect(WIDTH // 2 - 60, 400, 120, 40)
explosion_button = pygame.Rect(WIDTH - 120, 140, 100, 40)
anton_button = pygame.Rect(WIDTH // 2 - 150, 450, 300, 40)

# Робот в нижнем углу
robot_area = pygame.Rect(20, HEIGHT - 120, 200, 100)

# Главный цикл
clock = pygame.time.Clock()
running = True

def create_explosion():
    """Создает частицы взрыва"""
    global explosion_particles
    explosion_particles = []
    for _ in range(30):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        size = random.randint(3, 8)
        lifetime = random.randint(30, 60)
        explosion_particles.append({
            'x': main_button.centerx,
            'y': main_button.centery,
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed,
            'size': size,
            'color': (random.randint(200, 255), random.randint(100, 200), random.randint(0, 100)),
            'lifetime': lifetime
        })

def break_button():
    """Разламывает кнопку на куски"""
    global button_broken, button_break_timer, button_pieces
    button_broken = True
    button_break_timer = button_break_duration
    button_pieces = []
    
    # Создаем 8 кусков кнопки
    for i in range(8):
        piece_size = random.randint(30, 70)
        button_pieces.append({
            'x': main_button.centerx + random.randint(-50, 50),
            'y': main_button.centery + random.randint(-50, 50),
            'size': piece_size,
            'dx': random.uniform(-5, 5),
            'dy': random.uniform(-5, 5),
            'color': (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-5, 5)
        })

def move_button():
    """Перемещает кнопку в случайное место"""
    new_x = random.randint(100, WIDTH - 300)
    new_y = random.randint(100, HEIGHT - 200)
    main_button.x = new_x
    main_button.y = new_y

def shrink_button():
    """Уменьшает размер кнопки"""
    shrink_amount = random.randint(10, 40)
    main_button.width = max(50, main_button.width - shrink_amount)
    main_button.height = max(30, main_button.height - shrink_amount)

def reset_button():
    """Восстанавливает кнопку после разрушения"""
    global button_broken
    button_broken = False
    main_button.x, main_button.y = original_button_pos
    main_button.width, main_button.height = 200, 100

def add_knife():
    """Добавляет нож для анимации автоклика"""
    knives.append({
        'x': random.randint(WIDTH // 2 - 150, WIDTH // 2 + 150),
        'y': -50,
        'speed': random.uniform(3, 7),
        'target_x': main_button.centerx + random.randint(-40, 40),
        'target_y': main_button.centery + random.randint(-40, 40),
        'active': True
    })

def get_chest_reward():
    """Генерирует случайное перманентное улучшение"""
    available_upgrades = [key for key, upgrade in permanent_upgrades.items() if not upgrade["active"]]
    
    if not available_upgrades:
        return "bonus", random.randint(100, 500), ""
    
    upgrade_key = random.choice(available_upgrades)
    return upgrade_key, permanent_upgrades[upgrade_key]["name"], permanent_upgrades[upgrade_key]["desc"]

def apply_permanent_upgrade(upgrade_key):
    """Применяет перманентное улучшение"""
    if upgrade_key == "bonus":
        return
    
    upgrade = permanent_upgrades[upgrade_key]
    upgrade["active"] = True
    
    if upgrade_key == "double_clicks":
        global click_power
        click_power *= upgrade["multiplier"]
    elif upgrade_key == "auto_boost":
        global auto_clicks
        auto_clicks *= upgrade["multiplier"]
    elif upgrade_key == "chest_discount":
        global chest_goal
        chest_goal = int(chest_goal * upgrade["multiplier"])
    elif upgrade_key == "explosion_perk":
        upgrade["last_used"] = 0

def draw_tooltip(text, x, y):
    """Рисует всплывающую подсказку"""
    lines = text.split('\n')
    max_width = max(small_font.size(line)[0] for line in lines)
    height = len(lines) * 20 + 10
    
    tooltip_rect = pygame.Rect(x + 20, y - height // 2, max_width + 20, height)
    pygame.draw.rect(screen, BLACK, tooltip_rect)
    pygame.draw.rect(screen, YELLOW, tooltip_rect.inflate(-2, -2))
    
    for i, line in enumerate(lines):
        text_surface = small_font.render(line, True, BLACK)
        screen.blit(text_surface, (tooltip_rect.x + 10, tooltip_rect.y + 5 + i * 20))

def draw_robot():
    """Рисует робота с демотивирующей фразой"""
    # Рисуем тело робота
    pygame.draw.rect(screen, DARK_GRAY, robot_area)
    pygame.draw.rect(screen, BLACK, robot_area, 2)
    
    # Голова робота
    pygame.draw.rect(screen, GRAY, (robot_area.x + 70, robot_area.y - 30, 60, 40))
    
    # Глаза
    pygame.draw.circle(screen, RED, (robot_area.x + 85, robot_area.y - 10), 5)
    pygame.draw.circle(screen, RED, (robot_area.x + 115, robot_area.y - 10), 5)
    
    # Текущая фраза
    if current_phrase:
        phrase_text = small_font.render(current_phrase, True, WHITE)
        screen.blit(phrase_text, (robot_area.x + 10, robot_area.y + 10))

def draw_main_screen():
    """Отрисовка главного экрана"""
    screen.fill(WHITE)
    
    # Анимация взрыва
    if explosion_active:
        for particle in explosion_particles[:]:
            pygame.draw.circle(screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 
                             particle['size'])
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['lifetime'] -= 1
            if particle['lifetime'] <= 0:
                explosion_particles.remove(particle)
    
    # Анимация ножей
    for knife in knives[:]:
        if knife['active']:
            dx = knife['target_x'] - knife['x']
            dy = knife['target_y'] - knife['y']
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            
            knife['x'] += dx / dist * knife['speed']
            knife['y'] += dy / dist * knife['speed']
            
            pygame.draw.line(screen, BLACK, (knife['x'], knife['y']), 
                           (knife['x'] + 10, knife['y'] + 20), 2)
            pygame.draw.polygon(screen, GRAY, [
                (knife['x'] + 5, knife['y'] + 15),
                (knife['x'] + 15, knife['y'] + 25),
                (knife['x'] + 5, knife['y'] + 35)
            ])
            
            if abs(knife['x'] - knife['target_x']) < 5 and abs(knife['y'] - knife['target_y']) < 5:
                knife['active'] = False
                knives.remove(knife)
    
    # Анимация разломанной кнопки
    if button_broken:
        for piece in button_pieces:
            pygame.draw.rect(screen, piece['color'], 
                           (piece['x'], piece['y'], piece['size'], piece['size']))
            piece['x'] += piece['dx']
            piece['y'] += piece['dy']
            piece['rotation'] += piece['rotation_speed']
    else:
        # Основная кнопка клика
        button_color = ORANGE if explosion_active else BLUE
        pygame.draw.rect(screen, button_color, main_button)
        pygame.draw.rect(screen, BLACK, main_button, 3)
        
        # Текст кнопки с учетом размера
        click_text = font.render("КЛИКНИ!", True, WHITE)
        if main_button.width > 80 and main_button.height > 30:
            screen.blit(click_text, (main_button.centerx - click_text.get_width() // 2, 
                                   main_button.centery - click_text.get_height() // 2))
    
    # Кнопка магазина
    pygame.draw.rect(screen, PURPLE, shop_button)
    pygame.draw.rect(screen, BLACK, shop_button, 2)
    
    shop_text = font.render("МАГАЗИН", True, WHITE)
    screen.blit(shop_text, (shop_button.centerx - shop_text.get_width() // 2, 
                          shop_button.centery - shop_text.get_height() // 2))
    
    # Кнопка сундука
    chest_color = GOLD if chest_available else GRAY
    pygame.draw.rect(screen, chest_color, chest_button)
    pygame.draw.rect(screen, BLACK, chest_button, 2)
    
    chest_text = font.render("Сундук", True, BLACK)
    screen.blit(chest_text, (chest_button.centerx - chest_text.get_width() // 2, 
                           chest_button.centery - chest_text.get_height() // 2))
    
    # Кнопка взрыва
    explosion_color = RED
    current_time = pygame.time.get_ticks()
    explosion_upgrade = permanent_upgrades["explosion_perk"]
    
    if explosion_upgrade["active"]:
        cooldown_left = max(0, explosion_upgrade["cooldown"] - (current_time - explosion_upgrade["last_used"]))
        if cooldown_left > 0:
            explosion_color = GRAY
        elif explosion_active:
            explosion_color = ORANGE
    
    pygame.draw.rect(screen, explosion_color, explosion_button)
    pygame.draw.rect(screen, BLACK, explosion_button, 2)
    
    explosion_text = small_font.render("ВЗРЫВ!", True, WHITE)
    screen.blit(explosion_text, (explosion_button.centerx - explosion_text.get_width() // 2, 
                               explosion_button.centery - explosion_text.get_height() // 2))
    
    # Кнопка Антона
    anton_color = DARK_RED if clicks >= 1000 else GRAY
    pygame.draw.rect(screen, anton_color, anton_button)
    pygame.draw.rect(screen, BLACK, anton_button, 2)
    
    anton_text = small_font.render("Играть в Stellaris", True, WHITE)
    screen.blit(anton_text, (anton_button.centerx - anton_text.get_width() // 2, 
                           anton_button.centery - anton_text.get_height() // 2))
    
    # Счетчик для кнопки Антона
    if clicks < 1000:
        needed_text = small_font.render(f"Нужно: {1000 - int(clicks)}", True, BLACK)
        screen.blit(needed_text, (anton_button.centerx - needed_text.get_width() // 2, 
                                anton_button.centery + 25))
    
    # Прогресс сундука
    progress_text = small_font.render(f"Сундук: {chest_progress}/{chest_goal}", True, BLACK)
    screen.blit(progress_text, (WIDTH - 120, 130))
    
    # Сообщение Антона
    if show_anton_message:
        anton_msg = large_font.render("НИХУЯ", True, RED)
        screen.blit(anton_msg, (WIDTH // 2 - anton_msg.get_width() // 2, 
                              HEIGHT // 2 - anton_msg.get_height() // 2))
    
    # Статистика
    multiplier = "x2!" if explosion_active else ""
    display_clicks = int(clicks) if clicks < 999 else 999 + (clicks - 999) / 100
    stats_text = font.render(f"Очков: {display_clicks:.2f} {multiplier}", True, BLACK)
    screen.blit(stats_text, (20, 20))
    
    power_text = small_font.render(f"Сила клика: {click_power} | Авто: {auto_clicks:.1f}/сек", True, BLACK)
    screen.blit(power_text, (20, 60))
    
    # Активные перманентные улучшения
    y_offset = 90
    mouse_pos = pygame.mouse.get_pos()
    global hovered_upgrade
    hovered_upgrade = None
    
    for upgrade_key, upgrade in permanent_upgrades.items():
        if upgrade["active"]:
            upgrade_text = small_font.render(f"✓ {upgrade['name']}", True, GREEN)
            text_rect = upgrade_text.get_rect(topleft=(20, y_offset))
            screen.blit(upgrade_text, (20, y_offset))
            
            if text_rect.collidepoint(mouse_pos):
                hovered_upgrade = upgrade_key
            
            y_offset += 25
    
    # Подсказка при наведении
    if hovered_upgrade:
        upgrade = permanent_upgrades[hovered_upgrade]
        draw_tooltip(upgrade["desc"], 20, y_offset - 40)
    
    # Рисуем робота
    draw_robot()

def draw_upgrades_screen():
    """Отрисовка экрана улучшений"""
    screen.fill(GRAY)
    
    # Заголовок
    title = large_font.render("МАГАЗИН УЛУЧШЕНИЙ", True, PURPLE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
    
    # Кнопка назад
    pygame.draw.rect(screen, DARK_BLUE, back_button)
    pygame.draw.rect(screen, BLACK, back_button, 2)
    
    back_text = small_font.render("← Назад", True, WHITE)
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, 
                          back_button.centery - back_text.get_height() // 2))
    
    # Статистика в магазине
    display_clicks = int(clicks) if clicks < 999 else 999 + (clicks - 999) / 100
    stats_text = font.render(f"Ваши очки: {display_clicks:.2f}", True, BLACK)
    screen.blit(stats_text, (WIDTH - 200, 20))
    
    # Сетка улучшений
    for i, upgrade in enumerate(upgrades):
        row = i // 2
        col = i % 2
        
        x = 50 + col * 350
        y = 100 + row * 150
        
        upgrade_rect = pygame.Rect(x, y, 320, 130)
        
        button_color = GREEN if clicks >= upgrade["cost"] else RED
        pygame.draw.rect(screen, button_color, upgrade_rect)
        pygame.draw.rect(screen, BLACK, upgrade_rect, 2)
        
        name_text = font.render(upgrade["name"], True, BLACK)
        screen.blit(name_text, (x + 10, y + 10))
        
        desc_text = small_font.render(upgrade["desc"], True, BLACK)
        screen.blit(desc_text, (x + 10, y + 40))
        
        cost_text = small_font.render(f"Стоимость: {upgrade['cost']} очков", True, BLACK)
        screen.blit(cost_text, (x + 10, y + 70))
        
        count_text = small_font.render(f"Куплено: {upgrade['count']} шт.", True, BLACK)
        screen.blit(count_text, (x + 10, y + 90))
        
        upgrade["rect"] = upgrade_rect

def draw_chest_reward():
    """Отрисовка экрана с наградой из сундука"""
    screen.fill(GOLD)
    
    # Заголовок
    title = large_font.render("🎉 ПОЗДРАВЛЯЕМ! 🎉", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    
    # Текст награды
    reward_text = font.render("Вы получили:", True, BLACK)
    screen.blit(reward_text, (WIDTH // 2 - reward_text.get_width() // 2, 180))
    
    reward_content = font.render(chest_reward_text, True, PURPLE)
    screen.blit(reward_content, (WIDTH // 2 - reward_content.get_width() // 2, 230))
    
    if chest_reward_desc:
        desc_text = small_font.render(chest_reward_desc, True, BLACK)
        screen.blit(desc_text, (WIDTH // 2 - desc_text.get_width() // 2, 270))
    
    # Кнопка закрытия
    pygame.draw.rect(screen, GREEN, close_reward_button)
    pygame.draw.rect(screen, BLACK, close_reward_button, 2)
    
    close_text = font.render("Закрыть", True, WHITE)
    screen.blit(close_text, (close_reward_button.centerx - close_text.get_width() // 2, 
                           close_reward_button.centery - close_text.get_height() // 2))

while running:
    current_time = pygame.time.get_ticks()
    dt = clock.tick(60) / 1000.0
    
    # Автоклики
    if auto_clicks > 0:
        clicks += auto_clicks * dt
        if random.random() < 0.02 * auto_clicks:
            add_knife()
    
    # Таймер взрыва
    if explosion_active:
        explosion_timer -= dt * 1000
        if explosion_timer <= 0:
            explosion_active = False
    
    # Таймер восстановления кнопки
    if button_broken:
        button_break_timer -= dt * 1000
        if button_break_timer <= 0:
            reset_button()
    
    # Таймер сообщения Антона
    if show_anton_message:
        anton_message_timer -= dt * 1000
        if anton_message_timer <= 0:
            show_anton_message = False
    
    # Движение кнопки
    button_move_timer += dt * 1000
    if button_move_timer >= button_move_delay and not button_broken:
        button_move_timer = 0
        
        # Плавное движение кнопки
        main_button.x += button_dx
        main_button.y += button_dy
        
        # Отскок от границ
        if main_button.left <= 0 or main_button.right >= WIDTH:
            button_dx = -button_dx
        if main_button.top <= 0 or main_button.bottom >= HEIGHT:
            button_dy = -button_dy
        
        # Случайное изменение направления
        if random.random() < 0.1:
            button_dx = random.uniform(-1, 1)
            button_dy = random.uniform(-1, 1)
    
    # Смена демотивирующих фраз
    phrase_timer += dt * 1000
    if phrase_timer >= phrase_duration:
        phrase_timer = 0
        current_phrase = random.choice(demotivational_phrases)
    
    # Ограничение очков (никогда не достигнуть 1000)
    if clicks >= 999:
        # После 999 очки растут в 100 раз медленнее
        excess = clicks - 999
        if excess > 0:
            clicks = 999 + excess / 100
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if show_chest_reward:
                if close_reward_button.collidepoint(event.pos):
                    show_chest_reward = False
                    chest_available = False
                    chest_progress = 0
            
            elif current_screen == "main":
                if main_button.collidepoint(event.pos) and not button_broken:
                    actual_power = click_power * (2 if explosion_active else 1)
                    clicks += actual_power
                    chest_progress += 1
                    
                    # Случайное действие с кнопкой (в 3 раза реже ломается)
                    action_roll = random.random()
                    if action_roll < 0.1:  # 10% шанс вместо ~30%
                        break_button()
                    elif action_roll < 0.4:  # 30% шанс
                        # Изменяем направление движения при клике
                        button_dx = random.uniform(-2, 2)
                        button_dy = random.uniform(-2, 2)
                    elif action_roll < 0.6:  # 20% шанс
                        shrink_button()
                    
                    if chest_progress >= chest_goal and not chest_available:
                        chest_available = True
                        chest_progress = chest_goal
                
                elif shop_button.collidepoint(event.pos):
                    current_screen = "upgrades"
                
                elif chest_button.collidepoint(event.pos) and chest_available:
                    reward_type, reward_name, reward_desc = get_chest_reward()
                    chest_reward_desc = reward_desc
                    
                    if reward_type == "bonus":
                        clicks += reward_name
                        chest_reward_text = f"{reward_name} бонусных очков!"
                    else:
                        apply_permanent_upgrade(reward_type)
                        chest_reward_text = f"Перманентное улучшение: {reward_name}!"
                    
                    show_chest_reward = True
                
                elif explosion_button.collidepoint(event.pos):
                    explosion_upgrade = permanent_upgrades["explosion_perk"]
                    if explosion_upgrade["active"]:
                        cooldown_left = explosion_upgrade["cooldown"] - (current_time - explosion_upgrade["last_used"])
                        if cooldown_left <= 0 and not explosion_active:
                            explosion_active = True
                            explosion_timer = explosion_duration
                            explosion_upgrade["last_used"] = current_time
                            create_explosion()
                
                elif anton_button.collidepoint(event.pos) and clicks >= 1000:
                    clicks -= 1000
                    show_anton_message = True
                    anton_message_timer = anton_message_duration
            
            elif current_screen == "upgrades":
                if back_button.collidepoint(event.pos):
                    current_screen = "main"
                else:
                    for upgrade in upgrades:
                        if "rect" in upgrade and upgrade["rect"].collidepoint(event.pos):
                            if clicks >= upgrade["cost"]:
                                clicks -= upgrade["cost"]
                                upgrade["count"] += 1
                                
                                if upgrade["type"] == "click":
                                    click_power += upgrade["power"]
                                elif upgrade["type"] == "auto":
                                    auto_clicks += upgrade["power"]
                                    add_knife()
                                
                                upgrade["cost"] = int(upgrade["cost"] * 1.8)
    
    # Отрисовка
    if show_chest_reward:
        draw_chest_reward()
    elif current_screen == "main":
        draw_main_screen()
    elif current_screen == "upgrades":
        draw_upgrades_screen()
    
    pygame.display.flip()

pygame.quit()
sys.exit()
