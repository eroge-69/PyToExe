import pygame
import os
import sys
import random

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("DBL FG - Fan Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

# Load assets (placeholder colors if no images)
def load_sprite(name, color):
    path = os.path.join("Sprites", name)
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    else:
        surface = pygame.Surface((150, 150))
        surface.fill(color)
        return surface

player_sprite = load_sprite("player.png", (0, 0, 255))
enemy_sprite = load_sprite("enemy.png", (255, 0, 0))
attack_card = load_sprite("attack_card.png", (255, 80, 80))
defend_card = load_sprite("defend_card.png", (80, 255, 80))
heal_card = load_sprite("heal_card.png", (80, 80, 255))

# Ensure Mods folder exists
if not os.path.exists("Mods"):
    os.makedirs("Mods")

# Load mods
mod_loaded = "None"
invincible = False
for filename in os.listdir("Mods"):
    if filename.endswith(".geode") and "invincible" in filename.lower():
        mod_loaded = "Invincibility Mod"
        invincible = True
        break

def draw_text(text, x, y, size=48, color=(255, 255, 255)):
    fnt = pygame.font.SysFont(None, size)
    txt = fnt.render(text, True, color)
    screen.blit(txt, (x, y))

def main_menu():
    while True:
        screen.fill((0, 0, 0))
        draw_text("DBL FG - Fan Game", 480, 150)
        draw_text("Mod Active: " + mod_loaded, 480, 200)
        pygame.draw.rect(screen, (30,144,255), (540, 300, 200, 50))
        pygame.draw.rect(screen, (30,144,255), (540, 370, 200, 50))
        pygame.draw.rect(screen, (255,69,0), (540, 440, 200, 50))
        draw_text("Start", 610, 310, 36)
        draw_text("Continue", 580, 380, 36)
        draw_text("Quit", 615, 450, 36)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(540, 300, 200, 50).collidepoint(event.pos):
                    return "character_select"
                elif pygame.Rect(540, 370, 200, 50).collidepoint(event.pos):
                    return "story_mode"
                elif pygame.Rect(540, 440, 200, 50).collidepoint(event.pos):
                    pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(60)

def character_select():
    characters = ["Goku", "Vegeta", "Piccolo"]
    selected = 0
    while True:
        screen.fill((10, 10, 20))
        draw_text("Select Your Character", 450, 150)
        for i, name in enumerate(characters):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            draw_text(name, 580, 250 + i * 60, 40, color)

        draw_text("Press Enter to Confirm", 480, 500, 30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(characters)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(characters)
                elif event.key == pygame.K_RETURN:
                    return characters[selected]

        pygame.display.flip()
        clock.tick(60)

def draw_cards():
    screen.blit(attack_card, (250, 500))
    draw_text("A", 310, 570, 36)
    screen.blit(defend_card, (550, 500))
    draw_text("D", 610, 570, 36)
    screen.blit(heal_card, (850, 500))
    draw_text("R", 910, 570, 36)

def battle_stage(character):
    player_hp = 100
    enemy_hp = 100
    action = ""
    msg = ""

    while True:
        screen.fill((30, 30, 30))
        screen.blit(player_sprite, (200, 250))
        screen.blit(enemy_sprite, (900, 250))
        draw_text(f"{character} HP: {player_hp}", 100, 50, 36)
        draw_text(f"Enemy HP: {enemy_hp}", 900, 50, 36)
        draw_cards()
        draw_text(msg, 420, 460, 30, (255, 255, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    dmg = random.randint(10, 25)
                    enemy_hp -= dmg
                    action = "attack"
                    msg = f"You attacked! -{dmg} HP to enemy."
                elif event.key == pygame.K_d:
                    action = "defend"
                    msg = "You defended!"
                elif event.key == pygame.K_r:
                    heal = random.randint(5, 15)
                    player_hp += heal
                    player_hp = min(player_hp, 100)
                    msg = f"You recovered +{heal} HP!"

        if action != "":
            enemy_action = random.choice(["attack", "attack", "recover"])
            if enemy_action == "attack":
                if action == "defend":
                    dmg = random.randint(2, 7)
                else:
                    dmg = random.randint(10, 20)
                if not invincible:
                    player_hp -= dmg
                msg += f" Enemy attacked! -{dmg} HP to you."
            elif enemy_action == "recover":
                heal = random.randint(5, 15)
                enemy_hp = min(enemy_hp + heal, 100)
                msg += f" Enemy recovered +{heal} HP."
            action = ""

        if player_hp <= 0:
            draw_text("You Lose!", 560, 300, 60, (255, 0, 0))
            draw_text("Press Enter to return", 500, 400, 36)
            pygame.display.flip()
            wait_key()
            return
        elif enemy_hp <= 0:
            draw_text("You Win!", 560, 300, 60, (0, 255, 0))
            draw_text("Press Enter to return", 500, 400, 36)
            pygame.display.flip()
            wait_key()
            return

        pygame.display.flip()
        clock.tick(60)

def wait_key():
    while True:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                return
            elif e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

def story_mode(character):
    stage = 1
    while True:
        battle_stage(character)
        stage += 1
        draw_text(f"Stage {stage} begins!", 500, 300)
        draw_text("Press Enter to continue", 480, 360)
        pygame.display.flip()
        wait_key()

while True:
    result = main_menu()
    if result == "character_select":
        char = character_select()
        story_mode(char)
    elif result == "story_mode":
        story_mode("Default Fighter")
