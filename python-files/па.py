import pygame
import sys
import random

# Инициализация
pygame.init()
pygame.joystick.init()

# Проверка геймпадов
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joy in joysticks:
    joy.init()
    print(f"Подключен геймпад: {joy.get_name()}")

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
GROUND = SCREEN_HEIGHT - 100

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
GRAY = (50, 50, 50)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
LIGHTNING_COLOR = (100, 200, 255)
FIRE_COLOR = (255, 69, 0)
WIND_COLOR = (173, 216, 230)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kill YOU")
clock = pygame.time.Clock()

# Шрифты
font_large = pygame.font.SysFont("Arial", 72, bold=True)
font_medium = pygame.font.SysFont("Arial", 48)
font_small = pygame.font.SysFont("Arial", 32)
font_tiny = pygame.font.SysFont("Arial", 24)

# Глобальные переменные
game_mode = None
game_state = "menu"  # "menu", "settings", "select_ultimate", "game", "gameover"

# НАСТРОЙКИ УПРАВЛЕНИЯ
controls_p1 = {
    'left': pygame.K_a,
    'right': pygame.K_d,
    'jump': pygame.K_w,
    'attack_hand': pygame.K_f,
    'attack_leg': pygame.K_g,
    'ultimate': pygame.K_h,
    'attack_hand_btn': 0,
    'attack_leg_btn': 1,
    'ultimate_btn': 2,
    'jump_btn': 3
}

controls_p2 = {
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT,
    'jump': pygame.K_UP,
    'attack_hand': pygame.K_2,
    'attack_leg': pygame.K_3,
    'ultimate': pygame.K_4,
    'attack_hand_btn': 4,
    'attack_leg_btn': 5,
    'ultimate_btn': 6,
    'jump_btn': 7
}

# Словарь для отображения названий клавиш
key_names = {
    pygame.K_a: "A", pygame.K_b: "B", pygame.K_c: "C", pygame.K_d: "D", pygame.K_e: "E",
    pygame.K_f: "F", pygame.K_g: "G", pygame.K_h: "H", pygame.K_i: "I", pygame.K_j: "J",
    pygame.K_k: "K", pygame.K_l: "L", pygame.K_m: "M", pygame.K_n: "N", pygame.K_o: "O",
    pygame.K_p: "P", pygame.K_q: "Q", pygame.K_r: "R", pygame.K_s: "S", pygame.K_t: "T",
    pygame.K_u: "U", pygame.K_v: "V", pygame.K_w: "W", pygame.K_x: "X", pygame.K_y: "Y",
    pygame.K_z: "Z",
    pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4",
    pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8", pygame.K_9: "9",
    pygame.K_UP: "↑", pygame.K_DOWN: "↓", pygame.K_LEFT: "←", pygame.K_RIGHT: "→",
    pygame.K_SPACE: "SPACE", pygame.K_RETURN: "ENTER", pygame.K_ESCAPE: "ESC"
}

# Типы ультимейтов с описанием
ULTIMATE_TYPES = {
    "firestorm": {
        "name": "Огненный Шторм",
        "color": FIRE_COLOR,
        "damage": 25,
        "duration": 60,
        "desc": "Волна огня проносится по земле",
        "icon": "fire"
    },
    "lightning": {
        "name": "Молния",
        "color": LIGHTNING_COLOR,
        "damage": 35,
        "duration": 20,
        "stun": 60,
        "desc": "Мощный удар сверху, оглушает",
        "icon": "lightning"
    },
    "whirlwind": {
        "name": "Вихрь",
        "color": WIND_COLOR,
        "damage": 15,
        "duration": 120,
        "pull": True,
        "desc": "Затягивает противника и бьёт долго",
        "icon": "wind"
    }
}

# Функция рисования иконок ультимейтов
def draw_ultimate_icon(screen, ult_type, x, y, size=50, selected=False):
    color = ULTIMATE_TYPES[ult_type]["color"]
    if selected:
        pygame.draw.rect(screen, YELLOW, (x-5, y-5, size+10, size+10), 3)
    if ult_type == "firestorm":
        # Фаербол
        pygame.draw.circle(screen, color, (x + size//2, y + size//2), size//2 - 5)
        pygame.draw.circle(screen, ORANGE, (x + size//2, y + size//2), size//3)
        # Языки пламени
        pygame.draw.polygon(screen, RED, [
            (x + size//2, y + 5),
            (x + size//2 - 8, y + 20),
            (x + size//2 + 8, y + 20)
        ])
    elif ult_type == "lightning":
        # Молния
        points = [
            (x + size//2, y + 5),
            (x + size//2 - 10, y + 25),
            (x + size//2 + 5, y + 25),
            (x + size//2 - 5, y + size - 5),
            (x + size//2 + 10, y + size - 5),
            (x + size//2, y + size - 5)
        ]
        pygame.draw.polygon(screen, color, points)
    elif ult_type == "whirlwind":
        # Порыв ветра
        cx, cy = x + size//2, y + size//2
        pygame.draw.arc(screen, color, (cx-20, cy-20, 40, 40), 0, 3.14, 3)
        pygame.draw.arc(screen, color, (cx-15, cy-15, 30, 30), 0, 3.14, 3)
        pygame.draw.arc(screen, color, (cx-10, cy-10, 20, 20), 0, 3.14, 3)
        # Линии ветра
        pygame.draw.line(screen, color, (x + 5, y + size//2), (x + 15, y + size//2), 2)
        pygame.draw.line(screen, color, (x + 20, y + size//2 - 5), (x + 30, y + size//2 - 5), 2)
        pygame.draw.line(screen, color, (x + 35, y + size//2 + 5), (x + 45, y + size//2 + 5), 2)

# Класс игрока
class Fighter:
    def __init__(self, x, y, color, name, controls, ultimate_type=None, joystick_id=None, is_ai=False):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 90
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.color = color
        self.name = name
        self.health = 100
        self.max_health = 100
        self.is_jumping = False
        self.is_attacking_hand = False
        self.is_attacking_leg = False
        self.is_ulting = False
        self.ultimate_type = ultimate_type  # УЖЕ ВЫБРАН!
        self.attack_hand_cooldown = 0
        self.attack_leg_cooldown = 0
        self.ultimate_cooldown = 0
        self.ultimate_charge = 0
        self.combo_counter = 0
        self.controls = controls
        self.joystick_id = joystick_id
        self.direction = 1
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.is_ai = is_ai
        self.damage_flash = 0
        self.ultimate_flash = 0
        self.ultimate_effect_timer = 0
        self.stun_timer = 0
        self.whirlwind_center = None

    def move(self, keys, joysticks, opponent=None):
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return

        self.vel_x = 0

        if self.is_ai and opponent:
            self.ai_update(opponent)
        else:
            if not self.joystick_id or self.joystick_id >= len(joysticks):
                if keys[self.controls['left']]:
                    self.vel_x = -self.speed
                    self.direction = -1
                if keys[self.controls['right']]:
                    self.vel_x = self.speed
                    self.direction = 1
                if keys[self.controls['jump']] and not self.is_jumping:
                    self.vel_y = self.jump_power
                    self.is_jumping = True

                if keys[self.controls['attack_hand']] and self.attack_hand_cooldown <= 0:
                    self.attack_hand()
                if keys[self.controls['attack_leg']] and self.attack_leg_cooldown <= 0:
                    self.attack_leg()
                if keys[self.controls['ultimate']] and self.ultimate_cooldown <= 0 and self.ultimate_charge >= 100:
                    self.trigger_ultimate()

            else:
                joy = joysticks[self.joystick_id]
                axis_x = joy.get_axis(0)
                if abs(axis_x) > 0.1:
                    self.vel_x = axis_x * self.speed
                    self.direction = 1 if axis_x > 0 else -1
                if joy.get_button(self.controls['jump_btn']) and not self.is_jumping:
                    self.vel_y = self.jump_power
                    self.is_jumping = True

                if joy.get_button(self.controls['attack_hand_btn']) and self.attack_hand_cooldown <= 0:
                    self.attack_hand()
                if joy.get_button(self.controls['attack_leg_btn']) and self.attack_leg_cooldown <= 0:
                    self.attack_leg()
                if joy.get_button(self.controls['ultimate_btn']) and self.ultimate_cooldown <= 0 and self.ultimate_charge >= 100:
                    self.trigger_ultimate()

        self.vel_y += GRAVITY
        self.y += self.vel_y

        if self.y > GROUND - self.height:
            self.y = GROUND - self.height
            self.vel_y = 0
            self.is_jumping = False

        self.x += self.vel_x

        if self.x < 0: self.x = 0
        if self.x > SCREEN_WIDTH - self.width: self.x = SCREEN_WIDTH - self.width

        self.hitbox.topleft = (self.x, self.y)

        if self.attack_hand_cooldown > 0: self.attack_hand_cooldown -= 1
        if self.attack_leg_cooldown > 0: self.attack_leg_cooldown -= 1
        if self.ultimate_cooldown > 0: self.ultimate_cooldown -= 1
        if self.damage_flash > 0: self.damage_flash -= 1
        if self.ultimate_flash > 0: self.ultimate_flash -= 1
        if self.ultimate_effect_timer > 0: self.ultimate_effect_timer -= 1
        if self.stun_timer > 0: self.stun_timer -= 1

        if self.ultimate_charge > 0 and self.ultimate_cooldown <= 0:
            self.ultimate_charge = max(0, self.ultimate_charge - 0.2)

    def ai_update(self, opponent):
        if self.stun_timer > 0:
            return

        dx = opponent.x - self.x
        distance = abs(dx)

        if distance > 40:
            self.vel_x = self.speed if dx > 0 else -self.speed
            self.direction = 1 if dx > 0 else -1
        else:
            self.vel_x = 0

        if opponent.y < self.y - 20 and not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True

        if distance < 70:
            if self.attack_hand_cooldown <= 0:
                self.attack_hand()
            elif distance < 50 and self.attack_leg_cooldown <= 0:
                self.attack_leg()
            elif self.ultimate_charge >= 100 and self.ultimate_cooldown <= 0:
                self.trigger_ultimate()

    def attack_hand(self):
        self.is_attacking_hand = True
        self.attack_hand_cooldown = 20

    def attack_leg(self):
        self.is_attacking_leg = True
        self.attack_leg_cooldown = 30

    def trigger_ultimate(self):
        if not self.ultimate_type:
            return  # не должно случиться
        self.is_ulting = True
        self.ultimate_cooldown = 300
        self.ultimate_charge = 0
        self.ultimate_flash = 60
        self.ultimate_effect_timer = ULTIMATE_TYPES[self.ultimate_type]["duration"]
        if "stun" in ULTIMATE_TYPES[self.ultimate_type]:
            self.stun_timer = ULTIMATE_TYPES[self.ultimate_type]["stun"]

    def add_combo_charge(self, damage):
        self.combo_counter += 1
        bonus = 20 if self.combo_counter >= 3 else 0
        self.ultimate_charge = min(100, self.ultimate_charge + 10 + bonus)

    def take_damage(self, amount):
        self.health -= amount
        self.damage_flash = 15
        self.combo_counter = 0
        if self.health < 0:
            self.health = 0

    def draw(self, screen):
        color = (255, 100, 100) if self.damage_flash > 0 and self.damage_flash % 3 < 2 else self.color
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

        face_color = WHITE if self.color != WHITE else BLACK
        pygame.draw.circle(screen, face_color, (int(self.x + self.width//2), int(self.y + 20)), 8)
        pygame.draw.circle(screen, face_color, (int(self.x + self.width//2 + 10), int(self.y + 20)), 8)
        pygame.draw.line(screen, face_color, (self.x + 15, self.y + 40), (self.x + self.width - 15, self.y + 40), 3)

        # Атаки
        if self.is_attacking_hand and 10 < self.attack_hand_cooldown < 18:
            attack_x = self.x + self.width // 2 + (40 * self.direction)
            pygame.draw.circle(screen, YELLOW, (int(attack_x), int(self.y + self.height // 3)), 20)
            pygame.draw.circle(screen, ORANGE, (int(attack_x), int(self.y + self.height // 3)), 10)

        if self.is_attacking_leg and 15 < self.attack_leg_cooldown < 25:
            attack_x = self.x + self.width // 2 + (30 * self.direction)
            pygame.draw.circle(screen, GREEN, (int(attack_x), int(self.y + self.height - 20)), 25)
            pygame.draw.circle(screen, WHITE, (int(attack_x), int(self.y + self.height - 20)), 12)

        # Эффекты ультимейтов
        if self.ultimate_effect_timer > 0 and self.ultimate_type:
            ut = ULTIMATE_TYPES[self.ultimate_type]
            if self.ultimate_type == "firestorm":
                for i in range(5):
                    fx = self.x + i * 30 - 60
                    alpha = int(200 * (self.ultimate_effect_timer / ut["duration"]))
                    pygame.draw.circle(screen, (*FIRE_COLOR, alpha), (int(fx), GROUND - 10), 20)
            elif self.ultimate_type == "lightning":
                if self.ultimate_effect_timer > ut["duration"] - 10:
                    lx = self.x + self.width // 2
                    pygame.draw.line(screen, LIGHTNING_COLOR, (lx, 0), (lx, SCREEN_HEIGHT), 5)
                    pygame.draw.line(screen, WHITE, (lx-5, 50), (lx+5, 55), 3)
            elif self.ultimate_type == "whirlwind":
                wx = self.x + self.width // 2
                alpha = int(150 * (self.ultimate_effect_timer / ut["duration"]))
                pygame.draw.circle(screen, (*WIND_COLOR, alpha), (int(wx), int(self.y + self.height//2)), 50, 5)

        self.is_attacking_hand = self.attack_hand_cooldown > 15
        self.is_attacking_leg = self.attack_leg_cooldown > 20

    def get_attack_rects(self):
        rects = []
        if self.is_attacking_hand and 12 < self.attack_hand_cooldown < 16:
            rects.append((
                pygame.Rect(
                    self.x + self.width//2 + (40 * self.direction) - 20,
                    self.y + self.height//3 - 20,
                    40, 40
                ),
                5, "hand"
            ))
        if self.is_attacking_leg and 18 < self.attack_leg_cooldown < 22:
            rects.append((
                pygame.Rect(
                    self.x + self.width//2 + (30 * self.direction) - 25,
                    self.y + self.height - 45,
                    50, 50
                ),
                8, "leg"
            ))
        if self.is_ulting and self.ultimate_effect_timer > 0:
            ut = ULTIMATE_TYPES[self.ultimate_type]
            if self.ultimate_type == "firestorm":
                rects.append((
                    pygame.Rect(0, GROUND - 50, SCREEN_WIDTH, 50),
                    ut["damage"], "ultimate"
                ))
            elif self.ultimate_type == "lightning":
                rects.append((
                    pygame.Rect(self.x - 50, 0, 100, SCREEN_HEIGHT),
                    ut["damage"], "ultimate"
                ))
            elif self.ultimate_type == "whirlwind":
                self.whirlwind_center = (self.x + self.width//2, self.y + self.height//2)
                rects.append((
                    pygame.Rect(self.x - 30, self.y - 30, self.width + 60, self.height + 60),
                    ut["damage"] // 10, "ultimate"
                ))
        return rects

    def update_whirlwind(self, opponent):
        if self.ultimate_type == "whirlwind" and self.ultimate_effect_timer > 0 and self.whirlwind_center:
            cx, cy = self.whirlwind_center
            dx = cx - (opponent.x + opponent.width//2)
            dy = cy - (opponent.y + opponent.height//2)
            dist = max(1, (dx**2 + dy**2)**0.5)
            if dist < 200:
                opponent.x += dx * 0.05
                opponent.y += dy * 0.05

# Меню выбора ультимейта
def select_ultimate_menu(screen, player_name, player_color, is_ai=False):
    if is_ai:
        return random.choice(list(ULTIMATE_TYPES.keys()))

    ult_types = list(ULTIMATE_TYPES.keys())
    selected = 0
    info_timer = 0
    show_info_for = None

    while True:
        screen.fill(BLACK)

        title = font_large.render(f"{player_name}: Выберите ультимейт", True, player_color)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        # Рисуем иконки
        start_x = SCREEN_WIDTH//2 - (len(ult_types) * 150) // 2
        for i, ult in enumerate(ult_types):
            x = start_x + i * 150
            y = 200
            draw_ultimate_icon(screen, ult, x, y, 80, i == selected)

            name = font_small.render(ULTIMATE_TYPES[ult]["name"], True, WHITE)
            screen.blit(name, (x + 40 - name.get_width()//2, y + 90))

            if i == selected and info_timer > 0:
                desc = font_tiny.render(ULTIMATE_TYPES[ult]["desc"], True, YELLOW)
                screen.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, 350))

        hint = font_tiny.render("← → — выбрать | ENTER — подтвердить", True, GRAY)
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(ult_types)
                    info_timer = 60
                    show_info_for = ult_types[selected]
                elif event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(ult_types)
                    info_timer = 60
                    show_info_for = ult_types[selected]
                elif event.key == pygame.K_RETURN:
                    return ult_types[selected]

        if info_timer > 0:
            info_timer -= 1

# Рисование шипованного "KILL"
def draw_spiky_text(screen, text, x, y, size=60, color=RED):
    letters = {
        "K": [(0,0), (0,4), (2,2), (0,2), (4,0), (4,4)],
        "I": [(0,0), (0,4), (2,0), (2,4), (4,0), (4,4)],
        "L": [(0,0), (0,4), (4,4)],
    }
    letter_width = size // 2
    letter_height = size
    offset_x = x
    for char in text.upper():
        if char in letters:
            points = letters[char]
            scaled_points = [(offset_x + p[0]*letter_width//4, y + p[1]*letter_height//4) for p in points]
            if len(scaled_points) > 1:
                pygame.draw.lines(screen, color, False, scaled_points, 5)
                for px, py in scaled_points:
                    pygame.draw.circle(screen, color, (px, py), 6)
        offset_x += letter_width + 10

# Аркадная полоска здоровья + шкала ультимейта + иконка
def draw_health_bars(screen, p1, p2):
    bar_width = 250
    bar_height = 30
    y_pos = 30

    # Здоровье
    pygame.draw.rect(screen, GRAY, (50, y_pos, bar_width, bar_height))
    pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 50 - bar_width, y_pos, bar_width, bar_height))

    pygame.draw.circle(screen, p1.color, (30, y_pos + bar_height//2), 20)
    pygame.draw.circle(screen, p2.color, (SCREEN_WIDTH - 30, y_pos + bar_height//2), 20)

    health_width1 = int(bar_width * (p1.health / p1.max_health))
    health_color1 = get_health_color(p1.health)
    pygame.draw.rect(screen, health_color1, (50, y_pos, health_width1, bar_height))

    health_width2 = int(bar_width * (p2.health / p2.max_health))
    health_color2 = get_health_color(p2.health)
    pygame.draw.rect(screen, health_color2, (SCREEN_WIDTH - 50 - bar_width, y_pos, health_width2, bar_height))

    # Имена
    p1_name = font_small.render(p1.name, True, WHITE)
    p2_name = font_small.render(p2.name, True, WHITE)
    screen.blit(p1_name, (50, y_pos - 25))
    screen.blit(p2_name, (SCREEN_WIDTH - 50 - p2_name.get_width(), y_pos - 25))

    # Шкала ультимейта
    ult_height = 10
    ult_y = y_pos + bar_height + 5

    pygame.draw.rect(screen, GRAY, (50, ult_y, bar_width, ult_height))
    charge_width1 = int(bar_width * (p1.ultimate_charge / 100))
    pygame.draw.rect(screen, YELLOW, (50, ult_y, charge_width1, ult_height))

    pygame.draw.rect(screen, GRAY, (SCREEN_WIDTH - 50 - bar_width, ult_y, bar_width, ult_height))
    charge_width2 = int(bar_width * (p2.ultimate_charge / 100))
    pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH - 50 - bar_width, ult_y, charge_width2, ult_height))

    # Иконки ультимейтов
    if p1.ultimate_type:
        draw_ultimate_icon(screen, p1.ultimate_type, 50 + bar_width + 10, y_pos, 30)
    if p2.ultimate_type:
        draw_ultimate_icon(screen, p2.ultimate_type, SCREEN_WIDTH - 50 - bar_width - 40, y_pos, 30)

def get_health_color(health):
    if health > 70: return GREEN
    elif health > 30: return YELLOW
    else: return RED

# Меню настроек (без изменений)
def settings_menu(screen, controls_p1, controls_p2):
    selected_player = 1
    selected_action = 0
    actions = ['left', 'right', 'jump', 'attack_hand', 'attack_leg', 'ultimate']
    action_names = {
        'left': 'Влево',
        'right': 'Вправо',
        'jump': 'Прыжок',
        'attack_hand': 'Атака рукой',
        'attack_leg': 'Атака ногой',
        'ultimate': 'Ультимейт'
    }
    waiting_for_key = False

    while True:
        screen.fill(BLACK)
        title = font_large.render("НАСТРОЙКИ УПРАВЛЕНИЯ", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        hint = font_tiny.render("Выберите действие и нажмите ENTER, затем нужную клавишу", True, GRAY)
        screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 120))

        p1_title = font_medium.render("Игрок 1", True, BLUE)
        screen.blit(p1_title, (200, 180))
        for i, action in enumerate(actions):
            color = YELLOW if selected_player == 1 and selected_action == i else WHITE
            key_name = key_names.get(controls_p1[action], "???")
            text = font_small.render(f"{action_names[action]}: {key_name}", True, color)
            screen.blit(text, (220, 230 + i * 40))

        p2_title = font_medium.render("Игрок 2", True, RED)
        screen.blit(p2_title, (SCREEN_WIDTH - 200 - p2_title.get_width(), 180))
        for i, action in enumerate(actions):
            color = YELLOW if selected_player == 2 and selected_action == i else WHITE
            key_name = key_names.get(controls_p2[action], "???")
            text = font_small.render(f"{action_names[action]}: {key_name}", True, color)
            screen.blit(text, (SCREEN_WIDTH - 400, 230 + i * 40))

        nav = font_tiny.render("↑↓ — выбор действия | ←→ — выбор игрока | ESC — назад", True, GRAY)
        screen.blit(nav, (SCREEN_WIDTH//2 - nav.get_width()//2, SCREEN_HEIGHT - 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_RETURN:
                    waiting_for_key = True
                    break
                elif event.key == pygame.K_UP:
                    selected_action = (selected_action - 1) % len(actions)
                elif event.key == pygame.K_DOWN:
                    selected_action = (selected_action + 1) % len(actions)
                elif event.key == pygame.K_LEFT:
                    selected_player = 1
                elif event.key == pygame.K_RIGHT:
                    selected_player = 2

        if waiting_for_key:
            waiting_text = font_medium.render("Нажмите новую клавишу...", True, YELLOW)
            screen.blit(waiting_text, (SCREEN_WIDTH//2 - waiting_text.get_width()//2, SCREEN_HEIGHT//2))
            pygame.display.update()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if selected_player == 1:
                            controls_p1[actions[selected_action]] = event.key
                        else:
                            controls_p2[actions[selected_action]] = event.key
                        waiting = False
            waiting_for_key = False

# Главное меню
def draw_menu(screen):
    screen.fill(BLACK)
    draw_spiky_text(screen, "KILL", SCREEN_WIDTH//2 - 220, 100, 80, RED)
    you_text = font_large.render("YOU", True, WHITE)
    screen.blit(you_text, (SCREEN_WIDTH//2 + 50, 100))

    pvp_text = font_medium.render("▶ Против игрока", True, WHITE)
    ai_text = font_medium.render("▶ Против ИИ", True, WHITE)
    settings_text = font_medium.render("⚙ Настройки управления", True, CYAN)

    pvp_rect = pvp_text.get_rect(center=(SCREEN_WIDTH//2, 300))
    ai_rect = ai_text.get_rect(center=(SCREEN_WIDTH//2, 400))
    settings_rect = settings_text.get_rect(center=(SCREEN_WIDTH//2, 500))

    screen.blit(pvp_text, pvp_rect)
    screen.blit(ai_text, ai_rect)
    screen.blit(settings_text, settings_rect)

    pygame.display.update()
    return pvp_rect, ai_rect, settings_rect

# Конец игры
def draw_gameover(screen, winner_name):
    screen.fill(BLACK)
    text = font_large.render(f"{winner_name} ПОБЕДИЛ!", True, YELLOW)
    restart = font_small.render("Нажмите ENTER для новой игры или ESC для выхода", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
    screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 50))
    pygame.display.update()

# Основной игровой цикл
def game_loop(mode):
    global game_state

    # Сначала выбираем ультимейты
    ult1 = select_ultimate_menu(screen, "Игрок 1", BLUE)
    if mode == "pvp":
        ult2 = select_ultimate_menu(screen, "Игрок 2", RED)
    else:
        ult2 = select_ultimate_menu(screen, "ИИ", RED, is_ai=True)

    player1 = Fighter(200, GROUND - 90, BLUE, "Игрок 1", controls_p1, ult1, joystick_id=0 if len(joysticks) > 0 else None)
    if mode == "pvp":
        player2 = Fighter(700, GROUND - 90, RED, "Игрок 2", controls_p2, ult2, joystick_id=1 if len(joysticks) > 1 else None)
    else:
        player2 = Fighter(700, GROUND - 90, RED, "ИИ", controls_p2, ult2, is_ai=True)

    running = True
    winner = None

    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    return

        keys = pygame.key.get_pressed()

        player1.move(keys, joysticks, player2 if player1.is_ai else None)
        player2.move(keys, joysticks, player1 if player2.is_ai else None)

        if player1.ultimate_type == "whirlwind" and player1.ultimate_effect_timer > 0:
            player1.update_whirlwind(player2)
        if player2.ultimate_type == "whirlwind" and player2.ultimate_effect_timer > 0:
            player2.update_whirlwind(player1)

        for rect, damage, atk_type in player1.get_attack_rects():
            if rect.colliderect(player2.hitbox):
                player2.take_damage(damage)
                player1.add_combo_charge(damage)
        for rect, damage, atk_type in player2.get_attack_rects():
            if rect.colliderect(player1.hitbox):
                player1.take_damage(damage)
                player2.add_combo_charge(damage)

        if player1.health <= 0:
            winner = player2.name
            running = False
        elif player2.health <= 0:
            winner = player1.name
            running = False

        draw_health_bars(screen, player1, player2)
        player1.draw(screen)
        player2.draw(screen)
        pygame.draw.line(screen, WHITE, (0, GROUND), (SCREEN_WIDTH, GROUND), 5)

        pygame.display.update()

    draw_gameover(screen, winner)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = "menu"
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# Главный цикл
while True:
    if game_state == "menu":
        pvp_rect, ai_rect, settings_rect = draw_menu(screen)
        choosing = True
        while choosing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pvp_rect.collidepoint(event.pos):
                        game_mode = "pvp"
                        game_state = "game"
                        choosing = False
                    elif ai_rect.collidepoint(event.pos):
                        game_mode = "ai"
                        game_state = "game"
                        choosing = False
                    elif settings_rect.collidepoint(event.pos):
                        game_state = "settings"
                        choosing = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        game_mode = "pvp"
                        game_state = "game"
                        choosing = False
                    elif event.key == pygame.K_2:
                        game_mode = "ai"
                        game_state = "game"
                        choosing = False
                    elif event.key == pygame.K_s:
                        game_state = "settings"
                        choosing = False

    elif game_state == "settings":
        settings_menu(screen, controls_p1, controls_p2)
        game_state = "menu"

    elif game_state == "game":
        game_loop(game_mode)