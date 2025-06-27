import pygame
import json
import os
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cute Cozy Cat game (Made by CatEnd)")
clock = pygame.time.Clock()
FPS = 60

# Colors
WALL_COLOR = (200, 180, 160)
FLOOR_COLOR = (150, 100, 50)
CARPET_COLOR = (180, 100, 100)
WINDOW_COLOR = (150, 200, 255)
NAP_ZONE_COLOR = (255, 220, 200)
CAT_COLOR = (200, 150, 100)
EAR_COLOR = (160, 110, 70)
HAPPY_COLOR = (255, 192, 203)
BOWL_COLOR = (150, 75, 0)
STRETCH_COLOR = (180, 140, 100)
COUCH_COLOR = (100, 60, 40)
BOT_CAT_COLOR = (120, 120, 200)
MENU_BG_COLOR = (30, 30, 30)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = (230, 230, 230)
DOOR_COLOR = (139, 69, 19)
DOG_COLOR = (100, 50, 50)

# Load sounds safely
def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    else:
        print(f"Warning: Sound file '{filename}' not found.")
        return None

ambient_music = "ambient.mp3"
purr_sound_file = "purr.wav"

music_on = False
if os.path.exists(ambient_music):
    pygame.mixer.music.load(ambient_music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    music_on = True
else:
    print("Ambient music file not found, continuing without it.")

purr_sound = load_sound(purr_sound_file)

class NapZone:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 60)
    def draw(self, surf):
        pygame.draw.rect(surf, NAP_ZONE_COLOR, self.rect)
        pygame.draw.ellipse(surf, (255, 240, 245), self.rect.inflate(-10, -10))

class FoodBowl:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 30)
    def draw(self, surf):
        pygame.draw.ellipse(surf, BOWL_COLOR, self.rect)
        pygame.draw.ellipse(surf, (255, 215, 0), self.rect.inflate(-10, -15))
    def interact(self, cat):
        if self.rect.colliderect(cat.rect):
            cat.hunger = min(100, cat.hunger + 0.3)
            cat.happiness = min(100, cat.happiness + 0.1)

class WaterBowl:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 30)
    def draw(self, surf):
        pygame.draw.ellipse(surf, (0, 150, 255), self.rect)
        pygame.draw.ellipse(surf, (100, 200, 255), self.rect.inflate(-10, -15))
    def interact(self, cat):
        if self.rect.colliderect(cat.rect):
            cat.thirst = min(100, cat.thirst + 0.3)
            cat.happiness = min(100, cat.happiness + 0.1)

class Cat:
    def __init__(self):
        self.rect = pygame.Rect(400, 300, 50, 60)
        self.speed = 3
        self.napping = False
        self.nap_timer = 0
        self.stretch_timer = 0
        self.happiness = 50
        self.hunger = 100
        self.thirst = 100

    def update(self, keys, napzones, barriers):
        if self.napping:
            self.nap_timer -= 1
            if purr_sound:
                if not pygame.mixer.Channel(1).get_busy():
                    pygame.mixer.Channel(1).play(purr_sound, loops=-1)
            if self.nap_timer <= 0:
                self.napping = False
                self.stretch_timer = FPS * 2
                pygame.mixer.Channel(1).stop()
            return

        if purr_sound:
            pygame.mixer.Channel(1).stop()

        if self.stretch_timer > 0:
            self.stretch_timer -= 1
            return

        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = self.speed

        self.rect.x += dx
        for barrier in barriers:
            if self.rect.colliderect(barrier):
                self.rect.x -= dx
        self.rect.y += dy
        for barrier in barriers:
            if self.rect.colliderect(barrier):
                self.rect.y -= dy

        for zone in napzones:
            if self.rect.colliderect(zone.rect) and keys[pygame.K_SPACE]:
                self.napping = True
                self.nap_timer = FPS * 5

        self.hunger = max(0, self.hunger - 0.01)
        self.thirst = max(0, self.thirst - 0.015)

        if self.hunger < 20 or self.thirst < 20:
            self.happiness = max(0, self.happiness - 0.05)
        elif self.happiness < 100:
            self.happiness += 0.02

    def draw(self, surf):
        x, y = self.rect.topleft
        if self.stretch_timer > 0:
            pygame.draw.rect(surf, STRETCH_COLOR, (x, y + 60, 50, 10))

        pygame.draw.rect(surf, CAT_COLOR, (x, y + 20, 50, 40))
        pygame.draw.rect(surf, CAT_COLOR, (x + 5, y, 40, 30))
        pygame.draw.polygon(surf, EAR_COLOR, [(x + 10, y), (x + 5, y - 15), (x + 20, y)])
        pygame.draw.polygon(surf, EAR_COLOR, [(x + 40, y), (x + 45, y - 15), (x + 30, y)])
        pygame.draw.circle(surf, (0, 0, 0), (x + 15, y + 10), 3)
        pygame.draw.circle(surf, (0, 0, 0), (x + 35, y + 10), 3)

        if self.napping:
            font = pygame.font.SysFont(None, 24)
            surf.blit(font.render("Zzz...", True, (100, 100, 100)), (x, y - 30))

        pygame.draw.rect(surf, (100, 100, 100), (WIDTH - 210, 10, 200, 20))
        pygame.draw.rect(surf, HAPPY_COLOR, (WIDTH - 210, 10, self.happiness * 2, 20))
        pygame.draw.rect(surf, (100, 100, 100), (WIDTH - 210, 40, 200, 20))
        pygame.draw.rect(surf, (255, 100, 50), (WIDTH - 210, 40, self.hunger * 2, 20))
        pygame.draw.rect(surf, (100, 100, 100), (WIDTH - 210, 70, 200, 20))
        pygame.draw.rect(surf, (50, 150, 255), (WIDTH - 210, 70, self.thirst * 2, 20))

class BotCat:
    def __init__(self, x, y, color=BOT_CAT_COLOR):
        self.rect = pygame.Rect(x, y, 50, 60)
        self.speed = random.uniform(1, 2.5)
        self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.move_timer = random.randint(30, 120)
        self.color = color

    def update(self, barriers):
        dx, dy = self.direction
        self.rect.x += int(dx * self.speed)
        self.rect.y += int(dy * self.speed)

        for barrier in barriers:
            if self.rect.colliderect(barrier):
                self.rect.x -= int(dx * self.speed)
                self.rect.y -= int(dy * self.speed)
                self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                break

        self.move_timer -= 1
        if self.move_timer <= 0:
            self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            self.move_timer = random.randint(30, 120)

    def draw(self, surf):
        x, y = self.rect.topleft
        pygame.draw.rect(surf, self.color, (x, y + 20, 50, 40))
        pygame.draw.rect(surf, self.color, (x + 5, y, 40, 30))
        ear_color = (max(0,self.color[0]-40), max(0,self.color[1]-40), max(0,self.color[2]-40))
        pygame.draw.polygon(surf, ear_color, [(x + 10, y), (x + 5, y - 15), (x + 20, y)])
        pygame.draw.polygon(surf, ear_color, [(x + 40, y), (x + 45, y - 15), (x + 30, y)])
        pygame.draw.circle(surf, (0, 0, 0), (x + 15, y + 10), 3)
        pygame.draw.circle(surf, (0, 0, 0), (x + 35, y + 10), 3)

class Dog:
    def __init__(self):
        self.rect = pygame.Rect(100, HEIGHT//2 + 100, 60, 40)
        self.speed = 2
        self.direction = 1

    def update(self, barriers):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH - 50 or self.rect.left <= 50:
            self.direction *= -1
        for barrier in barriers:
            if self.rect.colliderect(barrier):
                self.direction *= -1
                self.rect.x += self.speed * self.direction * 2

    def draw(self, surf):
        pygame.draw.rect(surf, DOG_COLOR, self.rect)
        pygame.draw.circle(surf, (0,0,0), (self.rect.centerx - 10, self.rect.centery), 10)
        pygame.draw.circle(surf, (0,0,0), (self.rect.centerx + 10, self.rect.centery), 10)

door_inside = pygame.Rect(370, HEIGHT//2 - 60, 60, 60)
door_outside = pygame.Rect(370, HEIGHT//2 - 60, 60, 60)

barriers_inside = [pygame.Rect(0, 0, WIDTH, 50), pygame.Rect(0, 0, 50, HEIGHT), pygame.Rect(WIDTH-50, 0, 50, HEIGHT), pygame.Rect(0, HEIGHT-50, WIDTH, 50)]
barriers_outside = [pygame.Rect(0, 0, WIDTH, 50), pygame.Rect(0, 0, 50, HEIGHT), pygame.Rect(WIDTH-50, 0, 50, HEIGHT), pygame.Rect(0, HEIGHT-50, WIDTH, 50)]

napzones = [NapZone(100, 100), NapZone(600, 150)]
food_bowl = FoodBowl(100, HEIGHT - 100)
water_bowl = WaterBowl(600, HEIGHT - 100)

cat = Cat()

bots = [
    BotCat(200, 200, (180, 130, 120)),
    BotCat(300, 300, (120, 180, 140)),
    BotCat(500, 400, (160, 160, 200)),
    BotCat(600, 250, (130, 160, 180)),
]

dog = Dog()
font = pygame.font.SysFont(None, 36)
menu_open = False
button_width = 180
button_height = 40
buttons = {
    "Resume": pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 - 90, button_width, button_height),
    "Save": pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 - 40, button_width, button_height),
    "Load": pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 10, button_width, button_height),
    "Exit": pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 60, button_width, button_height),
}

outside = False

def fade(surf, fade_in=True, speed=5):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0,0,0))
    for alpha in (range(0, 255, speed) if fade_in else range(255, -1, -speed)):
        fade_surface.set_alpha(alpha)
        surf.blit(fade_surface, (0,0))
        pygame.display.flip()
        pygame.time.delay(10)

def draw_living_room(surf):
    surf.fill(FLOOR_COLOR)
    pygame.draw.rect(surf, WALL_COLOR, (0, 0, WIDTH, 50))
    pygame.draw.rect(surf, WALL_COLOR, (0, 0, 50, HEIGHT))
    pygame.draw.rect(surf, WALL_COLOR, (WIDTH - 50, 0, 50, HEIGHT))
    pygame.draw.rect(surf, WALL_COLOR, (0, HEIGHT - 50, WIDTH, 50))
    pygame.draw.rect(surf, CARPET_COLOR, (150, 250, 500, 200))
    pygame.draw.rect(surf, COUCH_COLOR, (600, 200, 150, 150))
    for zone in napzones: zone.draw(surf)
    food_bowl.draw(surf)
    water_bowl.draw(surf)
    pygame.draw.rect(surf, DOOR_COLOR, door_inside)

def draw_outside(surf):
    surf.fill((100, 180, 100))
    pygame.draw.rect(surf, (70, 130, 70), (0, 0, WIDTH, 50))
    pygame.draw.rect(surf, (70, 130, 70), (0, HEIGHT-50, WIDTH, 50))
    pygame.draw.rect(surf, (70, 130, 70), (0, 0, 50, HEIGHT))
    pygame.draw.rect(surf, (70, 130, 70), (WIDTH-50, 0, 50, HEIGHT))
    pygame.draw.rect(surf, DOOR_COLOR, door_outside)

def draw_menu(surf):
    surf.fill(MENU_BG_COLOR)
    for text, rect in buttons.items():
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(surf, color, rect)
        label = font.render(text, True, TEXT_COLOR)
        label_rect = label.get_rect(center=rect.center)
        surf.blit(label, label_rect)

def save_game():
    data = {
        "cat_x": cat.rect.x,
        "cat_y": cat.rect.y,
        "hunger": cat.hunger,
        "thirst": cat.thirst,
        "happiness": cat.happiness,
        "outside": outside,
        "bots": [(b.rect.x, b.rect.y, b.color) for b in bots]
    }
    with open("savegame.json", "w") as f:
        json.dump(data, f)

def load_game():
    global outside
    if os.path.exists("savegame.json"):
        with open("savegame.json", "r") as f:
            data = json.load(f)
            cat.rect.x = data.get("cat_x", 400)
            cat.rect.y = data.get("cat_y", 300)
            cat.hunger = data.get("hunger", 100)
            cat.thirst = data.get("thirst", 100)
            cat.happiness = data.get("happiness", 50)
            outside = data.get("outside", False)
            bots_data = data.get("bots", [])
            bots.clear()
            for x, y, color in bots_data:
                bots.append(BotCat(x, y, tuple(color)))

running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                menu_open = not menu_open
            if not menu_open and event.key == pygame.K_e:
                if not outside and cat.rect.colliderect(door_inside):
                    fade(screen, True)
                    outside = True
                    cat.rect.centerx = door_outside.centerx
                    cat.rect.top = door_outside.bottom + 5
                    fade(screen, False)
                elif outside and cat.rect.colliderect(door_outside):
                    fade(screen, True)
                    outside = False
                    cat.rect.centerx = door_inside.centerx
                    cat.rect.bottom = door_inside.top - 5
                    fade(screen, False)
        elif event.type == pygame.MOUSEBUTTONDOWN and menu_open:
            mx, my = pygame.mouse.get_pos()
            for text, rect in buttons.items():
                if rect.collidepoint(mx, my):
                    if text == "Resume":
                        menu_open = False
                    elif text == "Save":
                        save_game()
                    elif text == "Load":
                        load_game()
                        menu_open = False
                    elif text == "Exit":
                        running = False

    if not menu_open:
        if outside:
            cat.update(keys, [], barriers_outside)
            for bot in bots: bot.update(barriers_outside)
            dog.update(barriers_outside)
        else:
            cat.update(keys, napzones, barriers_inside)
            food_bowl.interact(cat)
            water_bowl.interact(cat)

    if menu_open:
        draw_menu(screen)
    elif outside:
        draw_outside(screen)
        for bot in bots: bot.draw(screen)
        dog.draw(screen)
        cat.draw(screen)
    else:
        draw_living_room(screen)
        cat.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()