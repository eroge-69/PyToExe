import pygame
import random
import sys
import os
import math

os.system('cls' if os.name == 'nt' else 'clear')

# --- Configurations ---
WIDTH, HEIGHT = 800, 700
FPS = 60
FONT_SIZE = 36
WORD_DROP_INTERVAL = 2000  # milliseconds
MIN_INTERVAL = 900         # minimum interval (ms) between new words
SPEEDUP_SCORE_STEP = 100   # how often drop speed increases
LIVES = 10

#word list
WORDS = [
"python", "keyboard", "game", "challenge", "code", "speed", "window", "score",
"pygame", "fun", "logic", "mouse", "screen", "random", "loop", "event", "space",
"life", "function", "variable", "object", "sprite", "input", "output", "integer",
"string", "boolean", "list", "array", "tuple", "dictionary", "while", "for", "break",
"continue", "return", "import", "from", "class", "init", "main", "except", "try",
"except", "finally", "with", "open", "file", "read", "write", "append", "close",
"scoreboard", "highscore", "restart", "pause", "level", "bonus", "combo", "timer",
"slow", "fast", "easy", "hard", "medium", "practice", "perfect", "miss", "lose", "silly",
"win", "start", "finish", "exit", "reset", "play", "type", "letter", "word", "text",
"display", "color", "sound", "effect", "music", "volume", "mute", "background", "goofy",
"foreground", "update", "frame", "delta", "collision", "detect", "move", "jump", "umbrella","galaxy","engine","puzzle","volcano","crystal","lantern","harmony","orbit","thunder","cactus","whisper","jungle","comet","dragon","ripple","velvet","midnight","prism","tornado", "adventure","breeze","cascade","dawn","echo","feather","glacier","harbor","illusion","jigsaw","kettle","labyrinth","meadow","pixel","quiver","ripple","summit","timber","utopia","vortex","wander","yarn","zenith", "nectar","pixel","quiver","ripple","summit","timber","utopia","vortex","wander","yarn","zenith", "opal","pixel","quiver","ripple","summit","timber","utopia","vortex","wander","yarn","zenith", "pebble","pixel","quiver","ripple",  "xenon", "yonder","zephyr","alpine","blizzard","coral","doodle","ember","fjord", "grove","horizon", "island","jade","knoll","lunar","mirage","nymph","oasis","pixel","quiver","ripple","summit","timber","utopia","vortex","wander","yarn","zenith","noodle","puddle","quokka","rocket","saffron","tulip","unicorn","velvet","whimsy","xylophone","yogurt","zodiac", "lopsided","mystic","nectar","opal","pixel","quiver","ripple","summit","timber","utopia","vortex","wander","yarn", "racket","sizzle","tango","umpire","velcro","whisker","xenial","yodel","zesty", "poll", "jazz", "buzz", "fizz", "hiss", "whizz", "dazzle", "puzzle", "fizzle", "muzzle", "sizzle"
]
# --- Classes ---
class Word:
    def __init__(self, text, x, y, speed, direction="down"):
        self.text = text
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction  # "down" or "right"

    def move(self):
        if self.direction == "down":
            self.y += self.speed
        elif self.direction == "right":
            self.x += self.speed

    def draw(self, surface, font):
        img = font.render(self.text, True, (255,255,255))
        surface.blit(img, (self.x, self.y))

    def off_screen(self):
        if self.direction == "down":
            return self.y > HEIGHT
        elif self.direction == "right":
            return self.x > WIDTH

class Poof:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 18  # frames
        self.max_life = 18
        # Pick the word ONCE
        words = ["Good!", "Great!", "Yay!", "Cool!", "Nice!", "Wow!", "Amazing!"]
        self.text = random.choice(words)

    def draw(self, surface):
        # Fade out and grow
        alpha = int(255 * (self.life / self.max_life))
        size = int(30 + 25 * (1 - self.life / self.max_life))
        font = pygame.font.SysFont(None, size)
        img = font.render(self.text, True, (255,255,100))
        img.set_alpha(alpha)
        rect = img.get_rect(center=(self.x, self.y))
        surface.blit(img, rect)
        self.life -= 1

    def is_alive(self):
        return self.life > 0

class MissedWord:
    def __init__(self, text):
        self.text = text
        self.life = 60  # frames to display (short time)

    def is_alive(self):
        return self.life > 0

class Sparkle:
    def __init__(self, x, y):
        self.x = x + random.randint(-15, 15)
        self.y = y + random.randint(-15, 15)
        self.vx = random.uniform(-1.5, 1.5)
        self.vy = random.uniform(-2, -0.5)
        self.life = 18
        self.max_life = 18
        self.size = random.randint(8, 14)
        self.img = pygame.image.load("sparkle.png").convert_alpha()

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        img = pygame.transform.scale(self.img, (self.size, self.size))
        img.set_alpha(alpha)
        surface.blit(img, (self.x, self.y))
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def is_alive(self):
        return self.life > 0

def draw_gradient_background(surface, top_color, bottom_color):
    """Draw a vertical gradient background from top_color to bottom_color."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

class MissPoof:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 18  # frames
        self.max_life = 18

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size = int(30 + 25 * (1 - self.life / self.max_life))
        font = pygame.font.SysFont(None, size)
        img = font.render("Miss!", True, (255, 60, 60))
        img.set_alpha(alpha)
        rect = img.get_rect(center=(self.x, self.y))
        surface.blit(img, rect)
        self.life -= 1

    def is_alive(self):
        return self.life > 0

# --- Main Game ---
def game_loop(word_speed, drop_interval):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, FONT_SIZE)
    input_font = pygame.font.SysFont(None, 32)

    # --- Load SFX & Music ---
    try:
        sfx_correct = pygame.mixer.Sound("correct.mp3")
        sfx_lose_life = pygame.mixer.Sound("hit.mp3")
        sfx_game_over = pygame.mixer.Sound("game_over.mp3")
        sfx_sparkle = pygame.mixer.Sound("sparkle.mp3") if os.path.exists("sparkle.mp3") else None
        if os.path.exists("bgm.mp3"):
            pygame.mixer.music.load("bgm.mp3")
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
    except Exception as e:
        print("Sound loading error:", e)
        sfx_correct = sfx_lose_life = sfx_game_over = sfx_sparkle = None

    words = []
    poofs = []
    miss_poofs = []
    sparkles = []
    user_input = ""
    score = 0
    lives = LIVES
    next_word_time = pygame.time.get_ticks() + WORD_DROP_INTERVAL

    # Detect hard mode (add this logic where you set up the game)
    hard_mode = (word_speed == 1.0 and drop_interval == 1300)

    running = True
    lost = False
    paused = False
    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                lost = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    user_input = ""
                elif event.unicode.isprintable():
                    user_input += event.unicode

        # --- Pause Menu ---
        if paused:
            choice = pause_menu(screen, font)
            if choice == "continue":
                paused = False
                continue
            elif choice == "menu":
                return None

        # --- Add new word if it's time ---
        if now >= next_word_time:
            text = random.choice(WORDS)
            if hard_mode:
                if random.choice([True, False]):
                    # Vertical word
                    x = random.randint(30, WIDTH - 140)
                    y = 0
                    words.append(Word(text, x, y, word_speed, direction="down"))
                else:
                    # Horizontal word
                    x = 0
                    y = random.randint(30, HEIGHT - 140)
                    words.append(Word(text, x, y, word_speed, direction="right"))
            else:
                x = random.randint(30, WIDTH - 140)
                words.append(Word(text, x, 0, word_speed, direction="down"))
            next_word_time = now + drop_interval

        # --- Move words ---
        for word in words:
            word.move()

        # --- Check for matches ---
        for word in words[:]:
            if user_input.strip() == word.text:
                score += 1
                poofs.append(Poof(word.x + 50, word.y + 20))
                # Add sparkles burst
                for _ in range(12):
                    sparkles.append(Sparkle(word.x + 50, word.y + 20))
                words.remove(word)
                user_input = ""
                if sfx_correct: sfx_correct.play()
                if sfx_sparkle: sfx_sparkle.play()
                if score % SPEEDUP_SCORE_STEP == 0 and drop_interval > MIN_INTERVAL:
                    drop_interval = max(MIN_INTERVAL, drop_interval - 60)
                    word_speed += 0.12
                break

        # --- Remove words off screen, lose lives ---
        for word in words[:]:
            if word.off_screen():
                words.remove(word)
                lives -= 1
                # Place "Miss!" at the bottom for vertical, at the right edge for horizontal
                if word.direction == "down":
                    miss_poofs.append(MissPoof(word.x + 50, HEIGHT - 60))
                elif word.direction == "right":
                    miss_poofs.append(MissPoof(WIDTH - 60, word.y + 20))
                user_input = ""  # Clear input when life is lost
                if sfx_lose_life: sfx_lose_life.play()
                if lives <= 0:
                    running = False
                    lost = True

        # --- Draw everything ---
        draw_gradient_background(screen, (30, 30, 80), (10, 10, 30))
        for word in words:
            word.draw(screen, font)
        for poof in poofs:
            poof.draw(screen)
        poofs = [poof for poof in poofs if poof.is_alive()]
        for miss_poof in miss_poofs:
            miss_poof.draw(screen)
        miss_poofs = [mp for mp in miss_poofs if mp.is_alive()]
        for sparkle in sparkles:
            sparkle.draw(screen)
        sparkles = [s for s in sparkles if s.is_alive()]

        # UI: Score, Lives, Input
        score_img = font.render(f"Score: {score}", True, (255,255,0))
        lives_img = font.render(f"Lives: {lives}", True, (255,60,60))
        input_img = input_font.render(user_input, True, (255,255,255))
        screen.blit(score_img, (10, 10))
        screen.blit(lives_img, (WIDTH-170, 10))
        pygame.draw.rect(screen, (0,0,0), (0, HEIGHT-50, WIDTH, 50))
        screen.blit(input_img, (12, HEIGHT-40))

        pygame.display.flip()

    # --- Game Over Screen ---
    if lost:
        if sfx_game_over: sfx_game_over.play()
        screen.fill((30, 30, 40))
        end_img = font.render("Game Over!", True, (255,50,50))
        score_img = font.render(f"Final Score: {score}", True, (255,255,0))
        hint_img = input_font.render("Press R to restart or ESC to exit...", True, (200,200,200))
        screen.blit(end_img, (WIDTH//2-100, HEIGHT//2-70))
        screen.blit(score_img, (WIDTH//2-110, HEIGHT//2-10))
        screen.blit(hint_img, (WIDTH//2-170, HEIGHT//2+50))
        pygame.display.flip()
        pygame.event.clear()
        wait = True
        while wait:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True  # Restart
                    elif event.key == pygame.K_ESCAPE:
                        return False  # Exit
                elif event.type == pygame.QUIT:
                    return False
    return False

def draw_keyboard(surface, y, key_color=(60,60,60), text_color=(255,255,255), highlight_key=None):
    # Simple QWERTY keyboard layout
    rows = [
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM"
    ]
    key_w, key_h = 48, 54
    font = pygame.font.SysFont(None, 32)
    start_x = (WIDTH - key_w * 10) // 2
    for row_idx, row in enumerate(rows):
        row_y = y + row_idx * (key_h + 6)
        offset = 0
        if row_idx == 1:
            offset = key_w // 2
        if row_idx == 2:
            offset = key_w * 1.5
        for i, letter in enumerate(row):
            rect = pygame.Rect(start_x + offset + i * key_w, row_y, key_w-6, key_h)
            # Highlight if this is the pressed key
            if highlight_key and letter == highlight_key.upper():
                pygame.draw.rect(surface, (255, 220, 0), rect, border_radius=8)
                pygame.draw.rect(surface, (255,220,0), rect, 3, border_radius=8)
            else:
                pygame.draw.rect(surface, key_color, rect, border_radius=8)
                pygame.draw.rect(surface, (100,100,100), rect, 2, border_radius=8)
            img = font.render(letter, True, text_color)
            img_rect = img.get_rect(center=rect.center)
            surface.blit(img, img_rect)

def main_menu(screen, font, input_font):
    menu_items = ["Start Game", "How to Play", "Quit"]
    selected = 0
    title_font = pygame.font.SysFont(None, 110)
    t = 0
    # Pre-render menu item rects for mouse detection
    item_rects = []
    for i, item in enumerate(menu_items):
        img = font.render(item, True, (255,255,255))
        rect = img.get_rect()
        rect.center = (WIDTH//2, 200 + i*60 + rect.height//2)
        item_rects.append(rect)
    last_key = None
    key_timer = 0
    while True:
        # Draw gradient background
        draw_gradient_background(screen, (30, 30, 80), (10, 10, 30))
        bounce = int(18 * abs(math.sin(t/36)))
        title = title_font.render("TypeTime", True, (255,220,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60 + bounce))
        t += 1
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                # Only highlight A-Z keys
                if event.unicode.isalpha() and len(event.unicode) == 1:
                    last_key = event.unicode.upper()
                    key_timer = pygame.time.get_ticks()
        # Draw menu items and check mouse hover/click
        for i, item in enumerate(menu_items):
            rect = item_rects[i]
            is_hover = rect.collidepoint(mouse_pos)
            color = (255,255,255) if is_hover else (180,180,180)
            img = font.render(item, True, color)
            screen.blit(img, (WIDTH//2 - img.get_width()//2, 200 + i*60))
            if is_hover and mouse_clicked:
                return menu_items[i].lower().replace(" ", "_")
        # Only highlight the key for 100ms after press
        highlight = last_key if last_key and pygame.time.get_ticks() - key_timer < 100 else None
        draw_keyboard(screen, HEIGHT - 3*60 - 30, highlight_key=highlight)
        pygame.display.flip()

def difficulty_menu(screen, font):
    difficulties = [
        ("Easy", 1.0, 2200),
        ("Medium", 1.4, 1500),
        ("Hard", 1.0, 1300),
    ]
    # Pre-render rects for mouse detection
    item_rects = []
    for i, (name, _, _) in enumerate(difficulties):
        img = font.render(name, True, (255,255,255))
        rect = img.get_rect()
        rect.center = (WIDTH//2, 200 + i*60 + rect.height//2)
        item_rects.append(rect)
    while True:
        screen.fill((30, 30, 40))
        title = font.render("Select Difficulty", True, (255,255,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        # Draw "Press ESC to return to menu" hint
        hint_img = font.render("Press ESC to return to menu", True, (180,180,180))
        screen.blit(hint_img, (WIDTH//2 - hint_img.get_width()//2, HEIGHT - 120))
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None  # Return to menu
        for i, (name, speed, interval) in enumerate(difficulties):
            rect = item_rects[i]
            is_hover = rect.collidepoint(mouse_pos)
            color = (255,255,255) if is_hover else (180,180,180)
            img = font.render(name, True, color)
            screen.blit(img, (WIDTH//2 - img.get_width()//2, 200 + i*60))
            if is_hover and mouse_clicked:
                return speed, interval
        pygame.display.flip()

def how_to_play(screen, font, input_font):
    lines = [
        "Type the falling words before they reach the bottom.",
        "Press Enter to clear your input.",
        "Backspace deletes a letter.",
        "Each missed word costs a life.",
        "Game speeds up as you score!",
        "",
        "Press ESC to return to menu."
    ]
    while True:
        screen.fill((30, 30, 40))
        title = font.render("How to Play", True, (255,255,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        for i, line in enumerate(lines):
            img = input_font.render(line, True, (255,255,255))
            screen.blit(img, (WIDTH//2 - img.get_width()//2, 160 + i*38))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

def pause_menu(screen, font):
    menu_items = ["Continue", "Return to Menu"]
    title_font = pygame.font.SysFont(None, 80)
    item_rects = []
    for i, item in enumerate(menu_items):
        img = font.render(item, True, (255,255,255))
        rect = img.get_rect()
        rect.center = (WIDTH//2, 240 + i*70)
        item_rects.append(rect)
    while True:
        screen.fill((30, 30, 40))
        title = title_font.render("Paused", True, (255,220,0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "continue"
        for i, item in enumerate(menu_items):
            rect = item_rects[i]
            is_hover = rect.collidepoint(mouse_pos)
            color = (255,255,255) if is_hover else (180,180,180)
            img = font.render(item, True, color)
            screen.blit(img, rect.topleft)
            if is_hover and mouse_clicked:
                return "continue" if i == 0 else "menu"
        pygame.display.flip()

def main():
    pygame.init()
    pygame.mixer.init()
    # --- Load and play background music once at startup ---
    try:
        if os.path.exists("bgm.mp3"):
            pygame.mixer.music.load("bgm.mp3")
            pygame.mixer.music.set_volume(0.25)
            pygame.mixer.music.play(-1)
    except Exception as e:
        print("Music loading error:", e)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, FONT_SIZE)
    input_font = pygame.font.SysFont(None, 32)
    while True:
        menu_choice = main_menu(screen, font, input_font)
        if menu_choice == "quit":
            break
        elif menu_choice == "how_to_play":
            how_to_play(screen, font, input_font)
        elif menu_choice == "start_game":
            while True:
                diff = difficulty_menu(screen, font)
                if diff is None:
                    # Return to main menu if ESC pressed or window closed
                    break
                word_speed, drop_interval = diff
                restart = game_loop(word_speed, drop_interval)
                if not restart:
                    break
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()