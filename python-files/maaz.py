import pygame, sys, random, math

# ---------- تنظیمات اولیه ----------
pygame.init()
WIDTH, HEIGHT = 1000, 800
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Battle Offline - Full Version")
clock = pygame.time.Clock()

# ---------- رنگ‌ها ----------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (34, 139, 34)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
SKY = (135, 206, 235)

font = pygame.font.Font(None, 30)

# ---------- سازنده‌ها ----------
left_creator = "hasan namadi"
right_creator = "mohammad obaidi"

# ---------- تنظیمات پیشفرض ----------
player_name = "mpanho"
difficulty = "Normal"
current_theme = "Green"
lives = 20
score = 0
coins = 50
game_mode = "Deathmatch"
num_allies = 1
num_enemies = 3

themes = {
    "Green": {"bg": GREEN, "tank_colors": [RED, BLUE, YELLOW, PURPLE]},
    "Pixel": {"bg": (120, 180, 120), "tank_colors": [RED, BLUE, YELLOW, PURPLE]},
    "Neon": {"bg": (20, 20, 40), "tank_colors": [RED, BLUE, YELLOW, PURPLE]},
    "Desert": {"bg": (245, 222, 179), "tank_colors": [RED, BLUE, YELLOW, PURPLE]},
    "Sky": {"bg": SKY, "tank_colors": [RED, BLUE, YELLOW, PURPLE]}
}

tank_skins = [RED, BLUE, YELLOW, PURPLE]
bullet_skins = [ORANGE, RED, BLUE, YELLOW]
player_skins = [BLACK, GRAY, SKY, ORANGE]
bullet_effects = [ORANGE, RED, BLUE, YELLOW]

# ---------- اضافه کردن تانک Minecraft ----------
minecraft_tank_pattern = [(34, 139, 34), (102, 51, 0)]  # سبز و قهوه‌ای
tank_skins.append("Minecraft")  # اضافه کردن نام به لیست skins

# ---------- کلاس‌ها ----------
class Tank:
    def __init__(self, x, y, color, is_bot=False, team=1):
        self.x = x
        self.y = y
        self.color = color
        self.angle = 0
        self.is_bot = is_bot
        self.team = team
        self.width = 50
        self.height = 70
        self.speed = 4 if not is_bot else (2 if difficulty=="Normal" else 3 if difficulty=="Hard" else 1)
        self.reload_time = 0
        self.lives = 3
        self.max_lives = 3
        self.shield_time = 0
        self.speed_time = 0
        self.level = 1
        self.xp = 0
        self.xp_to_level = 50

    def draw(self, win):
        tank_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if self.color == "Minecraft":
            tank_surface.fill(BROWN)
            for i in range(0, self.width, 10):
                for j in range(0, self.height, 10):
                    color = random.choice(minecraft_tank_pattern)
                    pygame.draw.rect(tank_surface, color, (i, j, 10, 10))
        else:
            c = self.color if self.shield_time <= 0 else SKY
            pygame.draw.rect(tank_surface, c, (0, 0, self.width, self.height), border_radius=8)
        pygame.draw.rect(tank_surface, GRAY, (self.width//3, -10, self.width//3, 35))
        rotated = pygame.transform.rotate(tank_surface, self.angle)
        win.blit(rotated, (max(0, min(WIDTH-rotated.get_width(), self.x-rotated.get_width()//2)),
                           max(0, min(HEIGHT-rotated.get_height(), self.y-rotated.get_height()//2))))
        team_text = font.render(f"Team {self.team}", True, BLACK)
        win.blit(team_text, (self.x - team_text.get_width()//2, self.y - self.height//2 - 15))

    def move(self, keys_pressed=None, mouse_pos=None):
        speed = self.speed*1.5 if self.speed_time > 0 else self.speed
        if self.is_bot:
            self.bot_move()
        else:
            if keys_pressed:
                if keys_pressed[pygame.K_w]: self.y -= speed
                if keys_pressed[pygame.K_s]: self.y += speed
                if keys_pressed[pygame.K_a]: self.x -= speed
                if keys_pressed[pygame.K_d]: self.x += speed
            if mouse_pos:
                dx = mouse_pos[0] - self.x
                dy = mouse_pos[1] - self.y
                self.angle = -math.degrees(math.atan2(dy, dx)) - 90
        if self.shield_time > 0: self.shield_time -= 1
        if self.speed_time > 0: self.speed_time -= 1

    def bot_move(self):
        target = self.find_target()
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            distance = math.hypot(dx, dy)
            if distance > 150:
                self.x += (dx/distance)*self.speed
                self.y += (dy/distance)*self.speed
            self.angle = -math.degrees(math.atan2(dy, dx)) - 90
            if random.random() < 0.02 and self.reload_time <= 0:
                bullets.append(Bullet(self.x, self.y, self.angle, bullet_effects[0], self))
                self.reload_time = 30
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))
        if self.reload_time > 0: self.reload_time -= 1

    def find_target(self):
        enemies = [t for t in bots if t.team != self.team] + ([player] if self.team != 1 else [])
        if not enemies: return None
        target = min(enemies, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))
        return target

    def shoot(self):
        if self.reload_time <= 0:
            bullets.append(Bullet(self.x, self.y, self.angle, bullet_effects[0], self))
            self.reload_time = 20

# ---------- کلاس گلوله ----------
class Bullet:
    def __init__(self, x, y, angle, color, owner):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.color = color
        self.owner = owner
        self.radius = 5

    def move(self):
        rad = math.radians(-self.angle - 90)
        self.x += math.cos(rad) * self.speed
        self.y += math.sin(rad) * self.speed

    def draw(self, win):
        if 0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT:
            pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)

# ---------- زمین و آیتم ----------
bunkers = [(150, 150), (850, 150), (150, 650), (850, 650), (500, 150), (500, 650)]
items = []
item_types = ["heart", "ammo", "shield", "speed"]
for _ in range(8):
    items.append({"type": random.choice(item_types), "x": random.randint(50, 950), "y": random.randint(50, 750)})

def draw_ground():
    win.fill(themes[current_theme]["bg"])
    for bx, by in bunkers:
        pygame.draw.rect(win, BROWN, (bx-40, by-40, 80, 80), border_radius=5)
    for item in items:
        color = RED if item["type"]=="heart" else YELLOW if item["type"]=="ammo" else BLUE if item["type"]=="shield" else GRAY
        pygame.draw.circle(win, color, (item["x"], item["y"]), 10)

def check_item_pickup(tank):
    for item in items.copy():
        if math.hypot(tank.x - item["x"], tank.y - item["y"]) < 30:
            if item["type"]=="heart":
                tank.lives = min(tank.lives+1, tank.max_lives)
            elif item["type"]=="shield":
                tank.shield_time = 300
            elif item["type"]=="speed":
                tank.speed_time = 300
            elif item["type"]=="ammo":
                tank.reload_time = max(0, tank.reload_time-10)
            items.remove(item)

# ---------- HUD ----------
def draw_lives():
    for i in range(lives):
        pygame.draw.rect(win, RED, (10 + i*40, 10, 30, 30))

def draw_score():
    score_text = font.render(f"Score: {score}  Coins: {coins}  Level: {player.level}  XP: {player.xp}/{player.xp_to_level}  Player Lives: {player.lives}", True, BLACK)
    win.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))

def draw_creators():
    left_text = font.render(left_creator, True, BLACK)
    right_text = font.render(right_creator, True, BLACK)
    win.blit(left_text, (10, HEIGHT - 30))
    win.blit(right_text, (WIDTH - right_text.get_width() - 10, HEIGHT - 30))

# ---------- تعریف بازیکن و بات‌ها ----------
player = Tank(WIDTH//2, HEIGHT//2, tank_skins[0], is_bot=False, team=1)
bots = [Tank(random.randint(100,900), random.randint(100,700), random.choice(tank_skins), is_bot=True, team=2) for _ in range(num_enemies)]
bullets = []

# ---------- فروشگاه ----------
def open_shop():
    global coins, player
    shop_running = True
    buttons = {
        "Minecraft": pygame.Rect(100, 200, 200, 50),
        "back": pygame.Rect(100, 300, 200, 50)
    }
    while shop_running:
        win.fill(WHITE)
        title = font.render("Shop - Click Tank to Equip, ESC to Exit", True, BLACK)
        win.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        coins_text = font.render(f"Coins: {coins}", True, BLACK)
        win.blit(coins_text, (WIDTH//2 - coins_text.get_width()//2, 100))

        for name, rect in buttons.items():
            pygame.draw.rect(win, GRAY, rect, border_radius=5)
            text = font.render(name, True, BLACK)
            win.blit(text, (rect.x + 10, rect.y + 10))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                shop_running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for name, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        if name == "Minecraft":
                            player.color = "Minecraft"
                        elif name == "back":
                            shop_running = False

# ---------- SETTINGS ----------
def open_settings():
    global current_theme, difficulty, player_name
    settings_running = True
    buttons = {
        "shop": pygame.Rect(100, 150, 200, 50),
        "difficulty": pygame.Rect(100, 250, 200, 50),
        "theme": pygame.Rect(100, 350, 200, 50),
        "name": pygame.Rect(100, 450, 200, 50),
        "back": pygame.Rect(100, 550, 200, 50)
    }
    theme_list = list(themes.keys())
    theme_index = theme_list.index(current_theme)
    difficulty_list = ["Easy", "Normal", "Hard"]
    diff_index = difficulty_list.index(difficulty)

    while settings_running:
        win.fill(WHITE)
        title = font.render("Settings - Click to Change", True, BLACK)
        win.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        for name, rect in buttons.items():
            pygame.draw.rect(win, GRAY, rect, border_radius=5)
            if name == "shop":
                text = font.render("Open Shop", True, BLACK)
            elif name == "difficulty":
                text = font.render(f"Difficulty: {difficulty_list[diff_index]}", True, BLACK)
            elif name == "theme":
                text = font.render(f"Theme: {theme_list[theme_index]}", True, BLACK)
            elif name == "name":
                text = font.render(f"Player Name: {player_name}", True, BLACK)
            else:
                text = font.render("Back", True, BLACK)
            win.blit(text, (rect.x + 10, rect.y + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for name, rect in buttons.items():
                    if rect.collidepoint(mx, my):
                        if name == "shop":
                            open_shop()
                        elif name == "difficulty":
                            diff_index = (diff_index + 1) % len(difficulty_list)
                            difficulty = difficulty_list[diff_index]
                        elif name == "theme":
                            theme_index = (theme_index + 1) % len(theme_list)
                            current_theme = theme_list[theme_index]
                        elif name == "name":
                            name_input = True
                            temp_name = ""
                            while name_input:
                                for e in pygame.event.get():
                                    if e.type == pygame.QUIT:
                                        pygame.quit()
                                        sys.exit()
                                    if e.type == pygame.KEYDOWN:
                                        if e.key == pygame.K_RETURN:
                                            if temp_name != "":
                                                player_name = temp_name
                                            name_input = False
                                        elif e.key == pygame.K_BACKSPACE:
                                            temp_name = temp_name[:-1]
                                        else:
                                            temp_name += e.unicode
                                win.fill(WHITE)
                                prompt = font.render("Enter Name (Press Enter to Confirm):", True, BLACK)
                                win.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 300))
                                typed = font.render(temp_name, True, BLACK)
                                win.blit(typed, (WIDTH//2 - typed.get_width()//2, 350))
                                pygame.display.update()
                        elif name == "back":
                            settings_running = False

# ---------- MAIN MENU ----------
def main_menu():
    running = True
    while running:
        win.fill(WHITE)
        title = font.render("Tank Battle Offline - Press Enter to Start", True, BLACK)
        win.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        settings_text = font.render("Press T to Open Settings", True, BLACK)
        win.blit(settings_text, (WIDTH//2 - settings_text.get_width()//2, HEIGHT//2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False
                if event.key == pygame.K_t:
                    open_settings()

# ---------- اجرای بازی ----------
main_menu()

running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.move(keys, mouse)
    for bot in bots:
        bot.move()

    if keys[pygame.K_SPACE]:
        player.shoot()

    for bullet in bullets[:]:
        bullet.move()
        if not (0 <= bullet.x <= WIDTH and 0 <= bullet.y <= HEIGHT):
            bullets.remove(bullet)
            continue
        if bullet.owner != player and math.hypot(bullet.x - player.x, bullet.y - player.y) < 35:
            player.lives -= 1
            bullets.remove(bullet)
            continue
        for bot in bots:
            if bullet.owner != bot and math.hypot(bullet.x - bot.x, bullet.y - bot.y) < 35:
                bot.lives -= 1
                bullets.remove(bullet)
                break
    bots = [bot for bot in bots if bot.lives > 0]

    check_item_pickup(player)
    draw_ground()
    draw_lives()
    draw_score()
    draw_creators()
    player.draw(win)
    for bot in bots:
        bot.draw(win)
    for bullet in bullets:
        bullet.draw(win)

    pygame.display.update()

pygame.quit()
sys.exit()