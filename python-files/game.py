import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1000, 600
TILE_SIZE = 50
FPS = 60
GRAVITY = 1.0
SAFE_ZONE = TILE_SIZE * 40  # 2000 px safe flat ground before obstacles

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Infinite Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

high_score = 0

def load_image(name, scale=None):
    img = pygame.image.load(f"assets/{name}").convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

background = load_image("michaelhouse.png", (WIDTH, HEIGHT))
player_img = load_image("mario.png", (40, 60))
enemy_img = load_image("baba.png", (40, 60))
coin_img = load_image("coin.png", (30, 30))

blocks = []
spikes = []
coins = []
overhead_blocks = []
generated_chunks = set()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.speed = 6
        self.controls = controls
        self.on_ground = False
        self.distance = 0
        self.coins_collected = 0

    def update(self, keys):
        dx = 0
        left = keys[self.controls['left']]
        right = keys[self.controls['right']]
        jump = keys[self.controls['jump']]

        if left and not right:
            dx = -self.speed
        elif right and not left:
            dx = self.speed

        if jump and self.on_ground:
            self.vel_y = -18
            self.on_ground = False

        self.vel_y += GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20
        dy = self.vel_y

        self.rect.x += dx
        self.collide(dx, 0)

        self.rect.y += dy
        self.on_ground = False
        self.collide(0, dy)

        if self.rect.left < 0:
            self.rect.left = 0

        if dx > 0:
            self.distance = max(self.distance, self.rect.x)

        for coin in coins[:]:
            if self.rect.colliderect(coin):
                coins.remove(coin)
                self.coins_collected += 1

    def collide(self, dx, dy):
        for block in blocks + overhead_blocks:
            if self.rect.colliderect(block):
                if dx > 0:
                    self.rect.right = block.left
                if dx < 0:
                    self.rect.left = block.right
                if dy > 0:
                    self.rect.bottom = block.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = block.bottom
                    self.vel_y = 0

        for spike in spikes:
            if self.rect.colliderect(spike):
                game_over()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, controls=None):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 5
        self.vel_y = 0
        self.controls = controls
        self.on_ground = False

    def update(self, keys=None, target=None):
        dx = 0

        if self.controls and keys:
            left = keys[self.controls['left']]
            right = keys[self.controls['right']]
            jump = keys[self.controls['jump']]

            if left and not right:
                dx = -self.speed
            elif right and not left:
                dx = self.speed

            if jump and self.on_ground:
                self.vel_y = -18
                self.on_ground = False

        elif target:
            if self.rect.x < target.rect.x - 10:
                dx = self.speed
            elif self.rect.x > target.rect.x + 10:
                dx = -self.speed

        self.vel_y += GRAVITY
        if self.vel_y > 20:
            self.vel_y = 20
        dy = self.vel_y

        self.rect.x += dx
        self.collide(dx, 0)

        self.rect.y += dy
        self.on_ground = False
        self.collide(0, dy)

    def collide(self, dx, dy):
        collided_with_block = False
        for block in blocks + overhead_blocks:
            if self.rect.colliderect(block):
                collided_with_block = True
                if dx > 0:
                    self.rect.right = block.left
                if dx < 0:
                    self.rect.left = block.right
                if dy > 0:
                    self.rect.bottom = block.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = block.bottom
                    self.vel_y = 0

        # Ignore spikes and holes (no game over for enemy)
        if dy > 0 and not collided_with_block:
            # Cancel falling to simulate hovering over holes
            self.rect.y -= dy
            self.vel_y = 0
            self.on_ground = True

def generate_chunk(chunk_x):
    if chunk_x in generated_chunks:
        return
    generated_chunks.add(chunk_x)
    start_x = chunk_x * TILE_SIZE * 20

    for i in range(20):
        x = start_x + i * TILE_SIZE

        if x < SAFE_ZONE:
            blocks.append(pygame.Rect(x, HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE))
        else:
            if random.random() < 0.15:
                continue
            blocks.append(pygame.Rect(x, HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE))

            if random.random() < 0.10:
                spikes.append(pygame.Rect(x, HEIGHT - TILE_SIZE - 20, TILE_SIZE, 20))

            if random.random() < 0.10:
                overhead_blocks.append(pygame.Rect(x, HEIGHT - TILE_SIZE * 3, TILE_SIZE, TILE_SIZE))

            if random.random() < 0.15:
                coins.append(pygame.Rect(x + TILE_SIZE//4, HEIGHT - TILE_SIZE * 2, 30, 30))

def draw_rect_list(lst, color, scroll):
    for rect in lst:
        pygame.draw.rect(screen, color, pygame.Rect(rect.x - scroll, rect.y, rect.width, rect.height))

def draw_coins(scroll):
    for coin in coins:
        screen.blit(coin_img, (coin.x - scroll, coin.y))

def draw_text(player):
    global high_score
    if player.distance > high_score:
        high_score = player.distance

    # Text with black background rectangles per line (for crisp text with background)
    dist_text = font.render(f"Distance: {player.distance//10}", True, (255, 255, 255))
    coins_text = font.render(f"Coins: {player.coins_collected}", True, (255, 255, 255))
    high_text = font.render(f"High Score: {high_score//10}", True, (255, 255, 255))

    # Get rects for text
    dist_rect = dist_text.get_rect(topleft=(10, 10))
    coins_rect = coins_text.get_rect(topleft=(10, 35))
    high_rect = high_text.get_rect(topleft=(10, 60))

    # Draw black rect behind each text line individually (for sharp edges)
    pygame.draw.rect(screen, (0,0,0), dist_rect)
    pygame.draw.rect(screen, (0,0,0), coins_rect)
    pygame.draw.rect(screen, (0,0,0), high_rect)

    # Blit texts on top
    screen.blit(dist_text, dist_rect)
    screen.blit(coins_text, coins_rect)
    screen.blit(high_text, high_rect)

def game_over():
    global game_state
    game_state = "game_over"

def reset_game():
    global blocks, spikes, overhead_blocks, coins, generated_chunks, player, enemy

    blocks.clear()
    spikes.clear()
    overhead_blocks.clear()
    coins.clear()
    generated_chunks.clear()

    player.rect.topleft = (100, HEIGHT - TILE_SIZE - 60)
    player.vel_y = 0
    player.on_ground = False
    player.distance = 0
    player.coins_collected = 0

    enemy.rect.topleft = (-50, HEIGHT - TILE_SIZE - 60)
    enemy.vel_y = 0
    enemy.on_ground = False

def main_menu():
    global game_state, mode

    while True:
        screen.fill((0, 0, 50))
        title = font.render("Mario Infinite Runner", True, (255, 255, 0))
        single = font.render("Press 1 for Single Player", True, (255, 255, 255))
        two = font.render("Press 2 for Two Player", True, (255, 255, 255))

        screen.blit(title, (WIDTH//3, HEIGHT//4))
        screen.blit(single, (WIDTH//3, HEIGHT//2))
        screen.blit(two, (WIDTH//3, HEIGHT//2 + 40))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = "single"
                    reset_game()
                    game_state = "play"
                    return
                if event.key == pygame.K_2:
                    mode = "two"
                    reset_game()
                    game_state = "play"
                    return

player_controls = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP}
enemy_controls = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w}

player = Player(100, HEIGHT - TILE_SIZE - 60, player_controls)
enemy = Enemy(-50, HEIGHT - TILE_SIZE - 60, controls=enemy_controls)

game_state = "menu"
mode = None

def game_loop():
    global game_state

    scroll = 0

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        if game_state == "menu":
            main_menu()

        elif game_state == "play":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            scroll = player.rect.x - 100

            current_chunk = player.rect.x // (TILE_SIZE * 20)
            for offset in range(-2, 5):
                generate_chunk(current_chunk + offset)

            player.update(keys)

            if player.rect.top > HEIGHT:
                game_over()

            if mode == "single":
                enemy.update(target=player)
            else:
                enemy.update(keys=keys)

            if enemy.rect.top > HEIGHT:
                # enemy fell into hole: ignore death per your request
                # Just reset Y to ground level to keep chasing
                enemy.rect.y = HEIGHT - TILE_SIZE - enemy.rect.height
                enemy.vel_y = 0
                enemy.on_ground = True

            if player.rect.colliderect(enemy.rect):
                game_over()

            screen.blit(background, (0, 0))
            draw_rect_list(blocks, (0, 150, 0), scroll)
            draw_rect_list(spikes, (255, 0, 0), scroll)
            draw_rect_list(overhead_blocks, (0, 100, 255), scroll)
            draw_coins(scroll)
            screen.blit(player.image, (player.rect.x - scroll, player.rect.y))
            screen.blit(enemy.image, (enemy.rect.x - scroll, enemy.rect.y))
            draw_text(player)

            pygame.display.update()

        elif game_state == "game_over":
            screen.fill((50, 0, 0))
            over_text = font.render("You got expelled! Press any key to restart.", True, (255, 255, 255))
            esc_text = font.render("Press ESC to go back to menu.", True, (255, 255, 255))
            screen.blit(over_text, (WIDTH//6, HEIGHT//2 - 20))
            screen.blit(esc_text, (WIDTH//6, HEIGHT//2 + 20))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"
                    else:
                        reset_game()
                        game_state = "play"

if __name__ == "__main__":
    game_loop()
