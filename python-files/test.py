import pygame
import random
import math
import asyncio
import platform

# Khởi tạo Pygame
pygame.init()
WIDTH, HEIGHT = 1000, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ngày thay đêm Vội trôi giấc mơ êm đềm Tôi lênh đênh trên biển vắng Hoàng hôn chờ em chưa buông nắng Đừng tìm nhau Vào hôm gió mưa tơi bời Sợ lời sắp nói vỡ tan thương đau Hẹn kiếp sau có nhau trọn đời")

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WIN_COLOR = (34, 177, 76)  # Màu #22b14c

# Thông số game
num = random.randint(0, 1)
if num == 1:
    maze = pygame.image.load("test2.png")
else:
    maze = pygame.image.load("real.png")
maze = pygame.transform.scale(maze, (1000, 1000))
yay = pygame.image.load("yay.png")
yay = pygame.transform.scale(yay, (1000, 500))
gigi = pygame.image.load("gigi.png")
gigi = pygame.transform.scale(gigi, (1000, 500))
PLAYER_SIZE = 20
BULLET_SIZE = 25
PLAYER_SPEED = 5
BULLET_SPEED = 3
SPAWN_RATE = 0.02

# Hàm kiểm tra va chạm với pixel màu đen hoặc màu thắng
def check_map_collision(x, y, maze_surface):
    if 0 <= int(x) < WIDTH and 0 <= int(y) < HEIGHT:
        pixel_color = maze_surface.get_at((int(x), int(y)))
        # Kiểm tra pixel màu đen (ngăn di chuyển)
        if pixel_color[0] < 50 and pixel_color[1] < 50 and pixel_color[2] < 50:
            return "black"
        # Kiểm tra pixel màu #22b14c (thắng)
        elif pixel_color[0] == WIN_COLOR[0] and pixel_color[1] == WIN_COLOR[1] and pixel_color[2] == WIN_COLOR[2]:
            return "win"
        return None
    return "black"  # Ngoài giới hạn, coi như va chạm

# Lớp người chơi
class Player:
    def __init__(self):
        self.x = WIDTH // 2 - 25
        self.y = 10
        self.rect = pygame.Rect(self.x - PLAYER_SIZE // 2, self.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)

    def move(self, keys):
        old_x, old_y = self.x, self.y
        collision_result = None
        if keys[pygame.K_a] and self.x - PLAYER_SIZE // 2 > 0:
            self.x -= PLAYER_SPEED
            collision_result = check_map_collision(self.x, self.y, maze)
            if collision_result == "black":
                self.x = old_x
        if keys[pygame.K_d] and self.x + PLAYER_SIZE // 2 < WIDTH:
            self.x += PLAYER_SPEED
            collision_result = check_map_collision(self.x, self.y, maze)
            if collision_result == "black":
                self.x = old_x
        if keys[pygame.K_w] and self.y - PLAYER_SIZE // 2 > 0:
            self.y -= PLAYER_SPEED
            collision_result = check_map_collision(self.x, self.y, maze)
            if collision_result == "black":
                self.y = old_y
        if keys[pygame.K_s] and self.y + PLAYER_SIZE // 2 < HEIGHT:
            self.y += PLAYER_SPEED
            collision_result = check_map_collision(self.x, self.y, maze)
            if collision_result == "black":
                self.y = old_y
        self.rect = pygame.Rect(self.x - PLAYER_SIZE // 2, self.y - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
        return collision_result

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)

# Lớp đạn
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.rect = pygame.Rect(self.x - BULLET_SIZE // 2, self.y - BULLET_SIZE // 2, BULLET_SIZE, BULLET_SIZE)

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.rect = pygame.Rect(self.x - BULLET_SIZE // 2, self.y - BULLET_SIZE // 2, BULLET_SIZE, BULLET_SIZE)

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), BULLET_SIZE // 2)

# Hàm reset game
def reset_game():
    global player, bullets, running, game_won, game_lost, spawn_rate, maze
    num = random.randint(0, 1)
    print(f"Random map selected: {num} ({'test2.png' if num == 1 else 'real.png'})")
    if num == 1:
        maze = pygame.image.load("test2.png")
    else:
        maze = pygame.image.load("real.png")
    maze = pygame.transform.scale(maze, (1000, 1000))
    player = Player()
    bullets = []
    running = True
    game_won = False
    game_lost = False
    spawn_rate = SPAWN_RATE

# Khởi tạo đối tượng
player = Player()
bullets = []
running = True
game_won = False
game_lost = False
clock = pygame.time.Clock()

def spawn_bullet():
    edge = random.randint(0, 3)
    if edge == 0:
        x, y = 0, random.randint(0, HEIGHT)
        angle = random.uniform(-math.pi / 4, math.pi / 4)
    elif edge == 1:
        x, y = WIDTH, random.randint(0, HEIGHT)
        angle = random.uniform(math.pi * 3 / 4, math.pi * 5 / 4)
    elif edge == 2:
        x, y = random.randint(0, WIDTH), 0
        angle = random.uniform(math.pi / 4, math.pi * 3 / 4)
    else:
        x, y = random.randint(0, WIDTH), HEIGHT
        angle = random.uniform(-math.pi * 3 / 4, -math.pi / 4)
    
    dx = BULLET_SPEED * math.cos(angle)
    dy = BULLET_SPEED * math.sin(angle)
    return Bullet(x, y, dx, dy)

def setup():
    global running, game_won, game_lost
    running = True
    game_won = False
    game_lost = False

async def update_loop(spawn_rate=0.02, tick=0):
    global running, game_won, game_lost
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
             running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for bullet in bullets[:]:
                    if bullet.rect.collidepoint(mouse_pos):
                        bullets.remove(bullet)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and (game_won or game_lost):
                reset_game()

        if not game_won and not game_lost:
            keys = pygame.key.get_pressed()
            collision_result = player.move(keys)
            if collision_result == "win":
                game_won = True

            if random.random() < spawn_rate:
                bullets.append(spawn_bullet())
            tick += 1
            if tick == 100:
                spawn_rate += 0.01
                tick = 0

            for bullet in bullets[:]:
                bullet.move()
                if bullet.x < -BULLET_SIZE or bullet.x > WIDTH + BULLET_SIZE or bullet.y < -BULLET_SIZE or bullet.y > HEIGHT + BULLET_SIZE:
                    bullets.remove(bullet)
                elif bullet.rect.colliderect(player.rect):
                    game_lost = True

        screen.fill(WHITE)
        screen.blit(maze, (0, 0))
        player.draw()
        for bullet in bullets:
            bullet.draw()
        if game_won:
            screen.blit(yay, (0, 250))
        elif game_lost:
            screen.blit(gigi, (0, 250))
        pygame.display.flip()

        await asyncio.sleep(1.0 / 60)

if platform.system() == "Emscripten":
    asyncio.ensure_future(update_loop(spawn_rate=SPAWN_RATE))
else:
    if __name__ == "__main__":
        asyncio.run(update_loop(spawn_rate=SPAWN_RATE))