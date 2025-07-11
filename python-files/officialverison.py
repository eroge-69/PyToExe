import pygame, math, random, sys

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Kolory
WHITE, BLACK, BLUE, RED, ORANGE, GRAY = (255,255,255),(0,0,0),(0,0,255),(255,0,0),(255,165,0),(100,100,100)

# Stałe
TILE_SIZE = 64
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
MAX_DEPTH = 800
WALL_HEIGHT = 500
PROJ_COEFF = 3 * NUM_RAYS * 50

# Załaduj tekstury
wall_texture = pygame.image.load("wall1.png").convert()
exit_texture = pygame.image.load("exit_texture.png").convert()  # **Nowa tekstura wyjścia**

texture_width = wall_texture.get_width()
texture_height = wall_texture.get_height()

MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Gracz
player_x, player_y = TILE_SIZE * 1.5, TILE_SIZE * 1.5
player_angle = 0
player_speed = 2
rotation_speed = 0.05

# Menu tło
menu_bg = pygame.image.load("menu_bg.png").convert()

# Muzyka
pygame.mixer.init()
meow_sound = pygame.mixer.Sound("miauuu.mp3")

# Kotek
class Cat:
    def __init__(self):
        self.texture = pygame.image.load("cat.png").convert_alpha()
        self.speed = 1.2
        self.find_valid_spawn()
        self.is_attacking = 0
        self.active = False  # rusza się dopiero po narracji

    def find_valid_spawn(self):
        while True:
            x = random.randint(1, len(MAP[0])-2)
            y = random.randint(1, len(MAP)-2)
            if MAP[y][x] == 0:
                self.x = x * TILE_SIZE + TILE_SIZE // 2
                self.y = y * TILE_SIZE + TILE_SIZE // 2
                return

    def can_move_to(self, x, y):
        mx, my = int(x // TILE_SIZE), int(y // TILE_SIZE)
        return MAP[my][mx] == 0

    def move(self, px, py):
        if not self.active: return
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        if dist == 0: return
        dir_x, dir_y = dx / dist, dy / dist
        nx, ny = self.x + dir_x * self.speed, self.y + dir_y * self.speed
        if self.can_move_to(nx, ny):
            self.x, self.y = nx, ny
        else:
            for _ in range(8):
                angle = random.random() * math.tau
                rx = self.x + math.cos(angle) * self.speed
                ry = self.y + math.sin(angle) * self.speed
                if self.can_move_to(rx, ry):
                    self.x, self.y = rx, ry
                    break
        self.is_attacking = 1 if dist < 50 else 0

cat = Cat()
next_meow_time = pygame.time.get_ticks() + random.randint(4000, 12000)  # pierwsze miauknięcie za 4-12 sekund

def cast_rays():
    rays = []
    ray_angle = player_angle - HALF_FOV
    for ray in range(NUM_RAYS):
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        depth = 0
        while depth < MAX_DEPTH:
            x = player_x + depth * cos_a
            y = player_y + depth * sin_a
            mx, my = int(x // TILE_SIZE), int(y // TILE_SIZE)
            if 0 <= my < len(MAP) and 0 <= mx < len(MAP[0]):
                tile = MAP[my][mx]
                if tile in (1, 2):
                    depth_corrected = depth * math.cos(player_angle - ray_angle)
                    wall_height = min(int(WALL_HEIGHT / (depth_corrected + 0.0001) * 200), HEIGHT)

                    hit_x = x % TILE_SIZE
                    hit_y = y % TILE_SIZE

                    prev_x = player_x + (depth - 1) * cos_a
                    prev_y = player_y + (depth - 1) * sin_a
                    if int(prev_x // TILE_SIZE) != mx:
                        texture_x = int(hit_y / TILE_SIZE * texture_width)
                    else:
                        texture_x = int(hit_x / TILE_SIZE * texture_width)

                    rays.append((ray, wall_height, texture_x, tile))
                    break
            depth += 1
        ray_angle += FOV / NUM_RAYS
    return rays

def draw_3d_view(rays):
    pygame.draw.rect(screen, (30, 30, 30), (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, (20, 20, 20), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
    column_width = WIDTH // NUM_RAYS
    for ray, height, texture_x, tile in rays:
        texture = wall_texture if tile == 1 else exit_texture  # wybierz teksturę po tile
        texture_column = texture.subsurface(texture_x, 0, 1, texture_height)
        texture_column = pygame.transform.scale(texture_column, (column_width + 1, height))
        pos_y = HEIGHT // 2 - height // 2
        pos_x = ray * column_width
        screen.blit(texture_column, (pos_x, pos_y))

def is_visible(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    steps = int(dist / 5)
    for i in range(1, steps):
        px = x1 + dx * i / steps
        py = y1 + dy * i / steps
        map_x, map_y = int(px // TILE_SIZE), int(py // TILE_SIZE)
        if MAP[map_y][map_x] == 1:
            return False
    return True

def render_cat_if_visible():
    dx, dy = cat.x - player_x, cat.y - player_y
    dist = math.hypot(dx, dy)
    angle_to_cat = math.atan2(dy, dx)
    delta_angle = (angle_to_cat - player_angle + math.pi) % (2 * math.pi) - math.pi
    if -HALF_FOV < delta_angle < HALF_FOV and is_visible(player_x, player_y, cat.x, cat.y):
        proj_height = PROJ_COEFF / (dist + 0.0001)
        ray_index = delta_angle / (FOV / NUM_RAYS)
        sprite_x = WIDTH // 2 + int(ray_index) * (WIDTH // NUM_RAYS) - int(proj_height // 2)
        sprite_y = HEIGHT // 2 - proj_height // 2
        scaled = pygame.transform.scale(cat.texture, (int(proj_height), int(proj_height)))
        screen.blit(scaled, (sprite_x, sprite_y))

def draw_minimap():
    scale = 10
    offset = 20
    for y in range(len(MAP)):
        for x in range(len(MAP[0])):
            color = WHITE if MAP[y][x] == 1 else BLUE if MAP[y][x] == 2 else BLACK
            pygame.draw.rect(screen, color, (x * scale + offset, y * scale + offset, scale, scale))
    pygame.draw.circle(screen, RED, (int(player_x / TILE_SIZE * scale) + offset, int(player_y / TILE_SIZE * scale) + offset), 4)
    pygame.draw.circle(screen, ORANGE, (int(cat.x / TILE_SIZE * scale) + offset, int(cat.y / TILE_SIZE * scale) + offset), 4)

def draw_menu():
    screen.blit(pygame.transform.scale(menu_bg, (WIDTH, HEIGHT)), (0, 0))
    font = pygame.font.SysFont(None, 80)
    t = font.render("MENU", True, WHITE)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 100))
    bf = pygame.font.SysFont(None, 60)
    play = bf.render("PLAY", True, BLACK)
    exit = bf.render("EXIT", True, BLACK)
    pr = pygame.Rect(WIDTH // 2 - 100, 300, 200, 80)
    er = pygame.Rect(WIDTH // 2 - 100, 420, 200, 80)
    pygame.draw.rect(screen, GRAY, pr)
    pygame.draw.rect(screen, GRAY, er)
    screen.blit(play, (pr.centerx - play.get_width() // 2, pr.centery - play.get_height() // 2))
    screen.blit(exit, (er.centerx - exit.get_width() // 2, er.centery - exit.get_height() // 2))
    pygame.display.flip()
    return pr, er

def menu_loop():
    while True:
        pr, er = draw_menu()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                pygame.mixer.music.load("narracja.mp3")

                if pr.collidepoint(ev.pos): return
                if er.collidepoint(ev.pos): pygame.quit(); sys.exit()

menu_loop()

# Odtwórz narrację i poczekaj, aż się skończy
while pygame.mixer.music.get_busy():
    pygame.time.delay(100)
pygame.mixer.music.load("1.mp3")
pygame.mixer.music.play(-1)

cat.active = True

# Pętla gry
running = True
win = False
lose = False

while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    if not win and not lose:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player_angle -= rotation_speed
        if keys[pygame.K_RIGHT]: player_angle += rotation_speed
        player_angle %= 2 * math.pi
        # Losowe miauknięcia
        current_time = pygame.time.get_ticks()
        if current_time >= next_meow_time:
            meow_sound.play()
            next_meow_time = current_time + random.randint(1000, 5000)


        move_x, move_y = 0, 0
        if keys[pygame.K_w]:
            move_x += math.cos(player_angle) * player_speed
            move_y += math.sin(player_angle) * player_speed
        if keys[pygame.K_s]:
            move_x -= math.cos(player_angle) * player_speed
            move_y -= math.sin(player_angle) * player_speed

        new_x = player_x + move_x
        new_y = player_y + move_y
        if MAP[int(new_y // TILE_SIZE)][int(new_x // TILE_SIZE)] != 1:
            player_x, player_y = new_x, new_y

        cat.move(player_x, player_y)

        if MAP[int(player_y // TILE_SIZE)][int(player_x // TILE_SIZE)] == 2:
            win = True
            pygame.mixer.music.stop()

        if math.hypot(player_x - cat.x, player_y - cat.y) < 20 and cat.is_attacking:
            lose = True
            pygame.mixer.music.stop()

    draw_3d_view(cast_rays())
    render_cat_if_visible()
    draw_minimap()

    if win:
        font = pygame.font.SysFont(None, 72)
        text = font.render("WYGRANA!", True, BLUE)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))
    elif lose:
        font = pygame.font.SysFont(None, 72)
        text = font.render("PRZEGRANA!", True, RED)
        screen.blit(text, (WIDTH // 2 - 120, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
