import pygame
import random

pygame.init()
WIDTH, HEIGHT = 480, 640
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platform Zıplama Oyunu")

WHITE = (255, 255, 255)
GREEN = (60, 200, 80)
BROWN = (120, 80, 40)
BLUE = (80, 180, 255)
RED = (220, 40, 40)

clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.w = 40
        self.h = 40
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 100
        self.vel_y = 0
        self.jump_power = 15
        self.on_ground = False

    def move(self, keys):
        if keys[pygame.K_a] and self.x > 0:
            self.x -= 5
        if keys[pygame.K_d] and self.x < WIDTH - self.w:
            self.x += 5

    def jump(self):
        if self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

    def update(self):
        self.vel_y += 0.7
        self.y += self.vel_y

    def draw(self, win):
        pygame.draw.rect(win, GREEN, (self.x, self.y, self.w, self.h), border_radius=8)

class Platform:
    def __init__(self, x, y, w=100, h=15):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, win):
        pygame.draw.rect(win, BROWN, (self.x, self.y, self.w, self.h), border_radius=6)

def generate_platforms():
    plats = [Platform(WIDTH//2-50, HEIGHT-40, 100, 15)]
    y = HEIGHT - 100
    while y > 0:
        x = random.randint(0, WIDTH-100)
        plats.append(Platform(x, y, 100, 15))
        y -= random.randint(60, 120)
    return plats

def main():
    run = True
    player = Player()
    platforms = generate_platforms()
    score = 0
    font = pygame.font.SysFont("Arial", 28)
    game_over = False

    while run:
        clock.tick(60)
        win.fill(BLUE)

        if not game_over:
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.update()

            # Platform çarpışma
            player.on_ground = False
            for plat in platforms:
                if (player.x + player.w > plat.x and player.x < plat.x + plat.w and
                    player.y + player.h > plat.y and player.y + player.h < plat.y + plat.h and
                    player.vel_y > 0):
                    player.y = plat.y - player.h
                    player.vel_y = 0
                    player.on_ground = True
                    score = max(score, HEIGHT - plat.y)

            # Yukarı çıkınca platformları aşağı kaydır
            if player.y < HEIGHT // 2:
                offset = HEIGHT // 2 - player.y
                player.y = HEIGHT // 2
                for plat in platforms:
                    plat.y += offset
                score += offset

            # Platformlar ekle/sil
            while platforms and platforms[0].y > HEIGHT:
                platforms.pop(0)
            while len(platforms) < 8:
                x = random.randint(0, WIDTH-100)
                y = platforms[-1].y - random.randint(60, 120)
                platforms.append(Platform(x, y, 100, 15))

            # Oyun bitti kontrolü
            if player.y > HEIGHT:
                game_over = True

        for plat in platforms:
            plat.draw(win)
        player.draw(win)

        score_text = font.render(f"Skor: {score//10}", True, WHITE)
        win.blit(score_text, (20, 20))

        if game_over:
            over_text = font.render("Oyun Bitti!", True, RED)
            win.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                    player.jump()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()