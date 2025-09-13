import sys
import random
import pygame
import webbrowser
import time

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
GREEN = (0, 200, 0)
BLUE = (50, 100, 200)
YELLOW = (255, 220, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elimination Game D")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 20)
BIG_FONT = pygame.font.SysFont("Arial", 28)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.width = 40
        self.height = 20
        self.speed = 5
        self.projectiles = []
        self.weapon = "Pistol"  
        self.hp = 10
        self.weapon_damage = {
            "Pistol": 1,
            "Rifle": 2,
            "Sniper": 5,
            "RPG": 4,
            "Katana": 3
        }
        self.unlocked_weapons = ["Pistol"]

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed

    def shoot(self):
        dmg = self.weapon_damage.get(self.weapon, 1)
        if self.weapon == "Rifle" or self.weapon == "Pistol":
            self.projectiles.append([self.x + self.width//2, self.y, -7, dmg])
        elif self.weapon == "Sniper":
            self.projectiles.append([self.x + self.width//2, self.y, -12, dmg])
        elif self.weapon == "RPG":
            self.projectiles.append([self.x, self.y, -5, dmg])
            self.projectiles.append([self.x + self.width, self.y, -5, dmg])
        elif self.weapon == "Katana":
            self.projectiles.append([self.x, self.y, 0, dmg])  

    def update(self):
        for p in self.projectiles:
            p[1] += p[2]
        self.projectiles = [p for p in self.projectiles if p[1] > -20]

    def draw(self, surf):
        pygame.draw.rect(surf, BLUE, (self.x, self.y, self.width, self.height))
        for p in self.projectiles:
            if self.weapon == "Katana":
                pygame.draw.rect(surf, YELLOW, (self.x-10, self.y-10, 60, 30))
            else:
                pygame.draw.rect(surf, RED, (p[0], p[1], 5, 10))

class Enemy:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 30)
        self.y = random.randint(20, 150)
        self.width = 30
        self.height = 20
        self.speed = random.choice([2, 3])
        self.max_health = random.randint(3, 8)
        self.health = self.max_health
        self.damage = 1

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()

    def reset(self):
        self.y = random.randint(-100, -40)
        self.x = random.randint(0, WIDTH - self.width)
        self.max_health = random.randint(3, 8)
        self.health = self.max_health

    def draw(self, surf):
        pygame.draw.rect(surf, GREEN, (self.x, self.y, self.width, self.height))
        health_ratio = self.health / self.max_health
        pygame.draw.rect(surf, RED, (self.x, self.y - 5, self.width * health_ratio, 5))


shop_items = {
    "RPG": "https://buy.stripe.com/bJecN51M5cqfckQ4Eoawo04",
    "Rifle": "https://buy.stripe.com/00w3cvaiBfCr84A6Mwawo03",
    "Sniper": "https://buy.stripe.com/6oU4gzduN2PFdoU1scawo05",
    "Katana": "https://buy.stripe.com/6oU4gzduN2PFdoU1scawo05"
}
shop_buttons = []

def draw_shop():
    screen.fill(WHITE)
    draw_text_center(screen, "Shop - Click to buy. Payment currency: zł (PLN)", BIG_FONT, 50)
    y = 120
    shop_buttons.clear()
    for weapon, link in shop_items.items():
        rect = pygame.Rect(WIDTH//2 - 100, y, 200, 50)
        pygame.draw.rect(screen, BLUE, rect)
        draw_text_center(screen, weapon, FONT, y + 25, WHITE)
        shop_buttons.append((rect, weapon, link))
        y += 80
    draw_text_center(screen, "ESC to exit", FONT, HEIGHT - 50, BLACK)

def draw_text_center(surf, text, font, y, color=BLACK):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=(WIDTH//2, y))
    surf.blit(txt, rect)


def main():
    player = Player()
    enemies = [Enemy() for _ in range(6)]
    score = 0

    entering_code = False
    code_text = ""
    in_shop = False

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if in_shop:
                    if event.key == pygame.K_ESCAPE:
                        in_shop = False
                elif entering_code:
                    if event.key == pygame.K_RETURN:
                        code = code_text.strip()
                        if code == "rifle59012687" and "Rifle" not in player.unlocked_weapons:
                            player.unlocked_weapons.append("Rifle")
                        elif code == "rpgpurchased5678901" and "RPG" not in player.unlocked_weapons:
                            player.unlocked_weapons.append("RPG")
                        elif code == "katanapurchase14" and "Katana" not in player.unlocked_weapons:
                            player.unlocked_weapons.append("Katana")
                        elif code == "sniperpurchase3" and "Sniper" not in player.unlocked_weapons:
                            player.unlocked_weapons.append("Sniper")
                        entering_code = False
                        code_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        code_text = code_text[:-1]
                    else:
                        code_text += event.unicode
                else:
                    if event.key == pygame.K_SPACE:
                        player.shoot()
                    if event.key == pygame.K_k:
                        entering_code = True
                        code_text = ""
                    if event.key == pygame.K_b:
                        in_shop = True
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                        index = event.key - pygame.K_1
                        if index < len(player.unlocked_weapons):
                            player.weapon = player.unlocked_weapons[index]

            if event.type == pygame.MOUSEBUTTONDOWN and in_shop:
                mx, my = pygame.mouse.get_pos()
                for rect, weapon, link in shop_buttons:
                    if rect.collidepoint(mx, my):
                        webbrowser.open(link)

        keys = pygame.key.get_pressed()
        if not in_shop and not entering_code:
            player.move(keys)
            player.update()

            for e in enemies:
                e.update()
                if (player.x < e.x + e.width and player.x + player.width > e.x and
                    player.y < e.y + e.height and player.y + player.height > e.y):
                    player.hp -= e.damage
                    e.reset()

            for p in player.projectiles:
                for e in enemies:
                    if (p[0] in range(e.x, e.x + e.width) and p[1] in range(e.y, e.y + e.height)):
                        e.health -= p[3]
                        if e.health <= 0:
                            score += 1
                            e.reset()
                        if p in player.projectiles:
                            player.projectiles.remove(p)
                        break

        screen.fill(WHITE)
        if in_shop:
            draw_shop()
        else:
            player.draw(screen)
            for e in enemies:
                e.draw(screen)
            if player.hp > 0:
                screen.blit(FONT.render(f"Score: {score}", True, BLACK), (10, 10))
                draw_text_center(screen, f"Weapon: {player.weapon}", FONT, 30, RED)
                draw_text_center(screen, f"HP: {player.hp}", FONT, 50, RED)
                if entering_code:
                    screen.blit(FONT.render("Code: " + code_text, True, BLACK), (10, HEIGHT - 30))
            else:
                draw_text_center(screen, "GAME OVER", BIG_FONT, HEIGHT // 2, RED)
                time.sleep(2)
                pygame.quit()
                sys.exit()

        pygame.display.flip()

if __name__ == "__main__":
    main()
