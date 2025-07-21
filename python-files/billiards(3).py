import pygame
import math
import asyncio
import platform
import random
import numpy as np

# Constants
WIDTH, HEIGHT = 800, 400
TABLE_COLOR = (0, 100, 0)
BORDER_COLOR = (139, 69, 19)
BALL_RADIUS = 10
POCKET_RADIUS = 15
BALL_COLORS = [
    (255, 255, 0), (0, 0, 255), (255, 0, 0), (128, 0, 128), (255, 165, 0),
    (0, 255, 0), (165, 42, 42), (0, 0, 0),  # Solids (1-7) + Black (8)
    (255, 255, 0), (0, 0, 255), (255, 0, 0), (128, 0, 128), (255, 165, 0),
    (0, 255, 0), (165, 42, 42), (255, 255, 255)  # Stripes (9-15) + Cue
]
POCKETS = [(0, 0), (WIDTH/2, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH/2, HEIGHT), (WIDTH, HEIGHT)]
FRICTION = 0.992
SPIN_FRICTION = 0.98
RESTITUTION = 0.9
MIN_SPEED = 0.05  # Stop balls below this speed to prevent vibration
FPS = 60
MAX_POWER = 50
TURN_TIME = 30
MENU_BUTTONS = [
    {"text": "2 Players", "rect": pygame.Rect(300, 100, 200, 50)},
    {"text": "Easy AI", "rect": pygame.Rect(300, 175, 200, 50)},
    {"text": "Hard AI", "rect": pygame.Rect(300, 250, 200, 50)},
    {"text": "Quit", "rect": pygame.Rect(300, 325, 200, 50)}
]

# Generate sounds
def generate_sound(frequency=440, duration=0.1, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return pygame.sndarray.make_sound((wave * 32767).astype(np.int16))

# Ball class
class Ball:
    def __init__(self, x, y, color, number, is_cue=False):
        self.pos = [x, y]
        self.vel = [0, 0]
        self.spin = [0, 0]
        self.color = color
        self.number = number
        self.is_cue = is_cue
        self.pocketed = False
        self.pocket_anim = 0

    def update(self):
        if self.pocketed:
            if self.pocket_anim > 0:
                self.pocket_anim -= 0.1
            return
        speed = math.sqrt(self.vel[0]**2 + self.vel[1]**2)
        if speed > 0:
            factor = max(0, (speed - 0.03) / speed) * FRICTION
            self.vel[0] *= factor
            self.vel[1] *= factor
            if speed < MIN_SPEED:
                self.vel = [0, 0]
        spin_magnitude = math.sqrt(self.spin[0]**2 + self.spin[1]**2)
        if spin_magnitude > 0:
            self.spin[0] *= SPIN_FRICTION
            self.spin[1] *= SPIN_FRICTION
            self.vel[0] += self.spin[0] * 0.02
            self.vel[1] += self.spin[1] * 0.02
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] <= BALL_RADIUS or self.pos[0] >= WIDTH - BALL_RADIUS:
            self.vel[0] *= -RESTITUTION
            self.spin[0] *= -0.7
            self.pos[0] = max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, self.pos[0]))
        if self.pos[1] <= BALL_RADIUS or self.pos[1] >= HEIGHT - BALL_RADIUS:
            self.vel[1] *= -RESTITUTION
            self.spin[1] *= -0.7
            self.pos[1] = max(BALL_RADIUS, min(HEIGHT - BALL_RADIUS, self.pos[1]))
        for pocket in POCKETS:
            dx = self.pos[0] - pocket[0]
            dy = self.pos[1] - pocket[1]
            if math.sqrt(dx**2 + dy**2) < POCKET_RADIUS:
                if self.is_cue:
 /

System: The provided code is truncated again. I'll complete it with all requested improvements, focusing on fixing the collision vibration bug by implementing a more robust collision resolution, adding a minimum speed threshold, and ensuring other potential bugs (e.g., foul handling, group assignment, timer resets, and AI behavior) are addressed. The game will maintain all features: 8-ball rules, fault handling with ball-in-hand, victory/defeat screens, two-player mode, animations, timer-based scoring, and Pyodide compatibility using NumPy for sounds.

<xaiArtifact artifact_id="9e38b3ea-10b2-4743-a1e1-b35a6391fe11" artifact_version_id="5df0737b-ae6c-4ef7-8d1a-fcb88318a663" title="billiards.py" contentType="text/python">
import pygame
import math
import asyncio
import platform
import random
import numpy as np

# Constants
WIDTH, HEIGHT = 800, 400
TABLE_COLOR = (0, 100, 0)
BORDER_COLOR = (139, 69, 19)
BALL_RADIUS = 10
POCKET_RADIUS = 15
BALL_COLORS = [
    (255, 255, 0), (0, 0, 255), (255, 0, 0), (128, 0, 128), (255, 165, 0),
    (0, 255, 0), (165, 42, 42), (0, 0, 0),  # Solids (1-7) + Black (8)
    (255, 255, 0), (0, 0, 255), (255, 0, 0), (128, 0, 128), (255, 165, 0),
    (0, 255, 0), (165, 42, 42), (255, 255, 255)  # Stripes (9-15) + Cue
]
POCKETS = [(0, 0), (WIDTH/2, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH/2, HEIGHT), (WIDTH, HEIGHT)]
FRICTION = 0.992
SPIN_FRICTION = 0.98
RESTITUTION = 0.9
MIN_SPEED = 0.05  # Stop balls below this speed to prevent vibration
FPS = 60
MAX_POWER = 50
TURN_TIME = 30
MENU_BUTTONS = [
    {"text": "2 Players", "rect": pygame.Rect(300, 100, 200, 50)},
    {"text": "Easy AI", "rect": pygame.Rect(300, 175, 200, 50)},
    {"text": "Hard AI", "rect": pygame.Rect(300, 250, 200, 50)},
    {"text": "Quit", "rect": pygame.Rect(300, 325, 200, 50)}
]

# Generate sounds
def generate_sound(frequency=440, duration=0.1, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return pygame.sndarray.make_sound((wave * 32767).astype(np.int16))

# Ball class
class Ball:
    def __init__(self, x, y, color, number, is_cue=False):
        self.pos = [x, y]
        self.vel = [0, 0]
        self.spin = [0, 0]
        self.color = color
        self.number = number
        self.is_cue = is_cue
        self.pocketed = False
        self.pocket_anim = 0

    def update(self):
        if self.pocketed:
            if self.pocket_anim > 0:
                self.pocket_anim -= 0.1
            return
        speed = math.sqrt(self.vel[0]**2 + self.vel[1]**2)
        if speed > 0:
            factor = max(0, (speed - 0.03) / speed) * FRICTION
            self.vel[0] *= factor
            self.vel[1] *= factor
            if speed < MIN_SPEED:
                self.vel = [0, 0]
        spin_magnitude = math.sqrt(self.spin[0]**2 + self.spin[1]**2)
        if spin_magnitude > 0:
            self.spin[0] *= SPIN_FRICTION
            self.spin[1] *= SPIN_FRICTION
            self.vel[0] += self.spin[0] * 0.02
            self.vel[1] += self.spin[1] * 0.02
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        if self.pos[0] <= BALL_RADIUS or self.pos[0] >= WIDTH - BALL_RADIUS:
            self.vel[0] *= -RESTITUTION
            self.spin[0] *= -0.7
            self.pos[0] = max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, self.pos[0]))
        if self.pos[1] <= BALL_RADIUS or self.pos[1] >= HEIGHT - BALL_RADIUS:
            self.vel[1] *= -RESTITUTION
            self.spin[1] *= -0.7
            self.pos[1] = max(BALL_RADIUS, min(HEIGHT - BALL_RADIUS, self.pos[1]))
        for pocket in POCKETS:
            dx = self.pos[0] - pocket[0]
            dy = self.pos[1] - pocket[1]
            if math.sqrt(dx**2 + dy**2) < POCKET_RADIUS:
                if self.is_cue:
                    self.pos = [0, 0]
                    self.vel = [0, 0]
                    self.spin = [0, 0]
                    self.pocketed = False
                    global current_player, foul, ball_in_hand
                    foul = True
                    ball_in_hand = True
                    current_player = "player2" if current_player == "player1" else "player1"
                    pocket_sound.play()
                elif self.number == 8:
                    global game_state, winner
                    group_cleared = all(ball.pocketed for ball in balls if not ball.is_cue and
                                        ((current_player == "player1" and player1_group == ("solids" if ball.number <= 7 else "stripes")) or
                                         (current_player == "player2" and player2_group == ("solids" if ball.number <= 7 else "stripes"))))
                    if group_cleared:
                        winner = current_player
                    else:
                        winner = "player2" if current_player == "player1" else "player1"
                    game_state = "game_over"
                    self.pocket_anim = 1
                    pocket_sound.play()
                else:
                    self.pocket_anim = 1
                    self.pocketed = True
                    global player1_score, player2_score, player1_group, player2_group
                    score = 100
                    if current_player == "player1":
                        if (player1_group == "solids" and self.number <= 7) or \
                           (player1_group == "stripes" and self.number >= 9):
                            player1_score += score
                        else:
                            foul = True
                            current_player = "player2"
                    else:
                        if (player2_group == "solids" and self.number <= 7) or \
                           (player2_group == "stripes" and self.number >= 9):
                            player2_score += score
                        else:
                            foul = True
                            current_player = "player1"
                    pocket_sound.play()

    def draw(self, screen):
        if self.pocketed and self.pocket_anim <= 0:
            return
        radius = int(BALL_RADIUS * max(self.pocket_anim, 0.5))
        for r in range(radius, 0, -1):
            shade = [min(255, c + (radius - r) * 10) for c in self.color]
            pygame.draw.circle(screen, shade, (int(self.pos[0]), int(self.pos[1])), r)
        spin_magnitude = math.sqrt(self.spin[0]**2 + self.spin[1]**2)
        if spin_magnitude > 0.1:
            angle = math.atan2(self.spin[1], self.spin[0])
            end_x = self.pos[0] + radius * math.cos(angle)
            end_y = self.pos[1] + radius * math.sin(angle)
            pygame.draw.line(screen, (200, 200, 200), self.pos, (end_x, end_y), 2)

# AI opponent
def ai_turn():
    global cue_active, power, ai_difficulty
    cue_ball = next(ball for ball in balls if ball.is_cue)
    if cue_ball.pocketed:
        return
    best_score = -float('inf')
    best_angle = 0
    best_power = 0
    best_spin = [0, 0]
    target_ball = None
    group_cleared = all(ball.pocketed for ball in balls if not ball.is_cue and player2_group == ("solids" if ball.number <= 7 else "stripes"))
    for ball in balls:
        if ball.pocketed or ball.is_cue or (ball.number == 8 and not group_cleared):
            continue
        for pocket in POCKETS:
            dist_to_pocket = math.sqrt((ball.pos[0] - pocket[0])**2 + (ball.pos[1] - pocket[1])**2)
            dist_to_cue = math.sqrt((ball.pos[0] - cue_ball.pos[0])**2 + (ball.pos[1] - cue_ball.pos[1])**2)
            score = -dist_to_pocket - 0.5 * dist_to_cue
            if (player2_group == "solids" and ball.number <= 7) or (player2_group == "stripes" and ball.number >= 9) or (ball.number == 8 and group_cleared):
                score += 50
            for opp_ball in balls:
                if opp_ball.pocketed or opp_ball.is_cue or \
                   (player1_group == "solids" and opp_ball.number > 7) or \
                   (player1_group == "stripes" and opp_ball.number < 8):
                    continue
                score -= 20 / (1 + math.sqrt((opp_ball.pos[0] - pocket[0])**2 + (opp_ball.pos[1] - pocket[1])**2))
            for angle in np.linspace(0, 2 * math.pi, 12):
                test_angle = angle + random.uniform(-0.26 / ai_difficulty, 0.26 / ai_difficulty)
                test_power = random.uniform(20, MAX_POWER)
                test_spin = [random.uniform(-2, 2), random.uniform(-2, 2)]
                dx = ball.pos[0] - cue_ball.pos[0]
                dy = ball.pos[1] - cue_ball.pos[1]
                target_angle = math.atan2(dy, dx)
                angle_diff = abs((test_angle - target_angle + math.pi) % (2 * math.pi) - math.pi)
                shot_score = score - 50 * angle_diff
                if shot_score > best_score:
                    best_score = shot_score
                    best_angle = test_angle
                    best_power = test_power
                    best_spin = test_spin
                    target_ball = ball
    if target_ball:
        cue_ball.vel[0] = math.cos(best_angle) * best_power * 0.15
        cue_ball.vel[1] = math.sin(best_angle) * best_power * 0.15
        cue_ball.spin = best_spin
        shot_sound.play()
    cue_active = False
    global current_player
    current_player = "player1"

# Game setup
def setup(mode="2 Players"):
    global screen, balls, cue_active, power, player1_score, player2_score, font, game_state, current_player, player1_group, player2_group, ai_difficulty, foul, ball_in_hand, turn_timer, turn_transition, winner, ai_mode
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Billiards Game")
    balls = [Ball(200, 200, BALL_COLORS[15], 0, True)]
    rack_x, rack_y = 500, HEIGHT / 2
    positions = [(0, 0), (1, -1), (1, 1), (2, -2), (2, 0), (2, 2), (3, -3), (3, -1), (3, 1), (3, 3), (4, -4), (4, -2), (4, 0), (4, 2), (4, 4)]
    random.shuffle(positions)  # Randomize rack
    for i, (row, col) in enumerate(positions):
        x = rack_x + col * BALL_RADIUS * 1.732
        y = rack_y + row * BALL_RADIUS * 2
        balls.append(Ball(x, y, BALL_COLORS[i], i + 1))
    global cue_active, power, player1_score, player2_score, game_state, current_player, player1_group, player2_group, foul, ball_in_hand, turn_timer, turn_transition, winner, ai_mode
    cue_active = False
    power = 0
    player1_score = 0
    player2_score = 0
    game_state = "menu"
    current_player = "player1"
    player1_group = None
    player2_group = None
    ai_difficulty = 1
    foul = False
    ball_in_hand = False
    turn_timer = TURN_TIME
    turn_transition = 0
    winner = None
    ai_mode = mode != "2 Players"
    global shot_sound, pocket_sound
    shot_sound = generate_sound(440, 0.1)
    pocket_sound = generate_sound(220, 0.2)

# Collision detection
def handle_collisions():
    for i, ball1 in enumerate(balls):
        if ball1.pocketed and ball1.pocket_anim <= 0:
            continue
        for ball2 in balls[i+1:]:
            if ball2.pocketed and ball2.pocket_anim <= 0:
                continue
            dx = ball2.pos[0] - ball1.pos[0]
            dy = ball2.pos[1] - ball1.pos[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 2 * BALL_RADIUS:
                angle = math.atan2(dy, dx)
                sin_a = math.sin(angle)
                cos_a = math.cos(angle)
                v1x = ball1.vel[0] * cos_a + ball1.vel[1] * sin_a
                v2x = ball2.vel[0] * cos_a + ball2.vel[1] * sin_a
                v1y = ball1.vel[1] * cos_a - ball1.vel[0] * sin_a
                v2y = ball2.vel[1] * cos_a - ball2.vel[0] * sin_a
                spin_effect = 0.05 * (ball1.spin[0] + ball2.spin[0])
                ball1.vel[0] = (v2x * cos_a - v1y * sin_a) * RESTITUTION + spin_effect
                ball1.vel[1] = (v2x * sin_a + v1y * cos_a) * RESTITUTION + spin_effect
                ball2.vel[0] = (v1x * cos_a - v2y * sin_a) * RESTITUTION - spin_effect
                ball2.vel[1] = (v1x * sin_a + v2y * cos_a) * RESTITUTION - spin_effect
                # Robust separation to prevent sticking
                overlap = 2 * BALL_RADIUS - dist
                if overlap > 0:
                    correction = overlap / (dist + 1e-6) * 0.5
                    ball1.pos[0] -= correction * dx
                    ball1.pos[1] -= correction * dy
                    ball2.pos[0] += correction * dx
                    ball2.pos[1] += correction * dy
                spin_transfer_x = (ball1.spin[0] - ball2.spin[0]) * 0.3
                spin_transfer_y = (ball1.spin[1] - ball2.spin[1]) * 0.3
                ball1.spin[0] -= spin_transfer_x
                ball1.spin[1] -= spin_transfer_y
                ball2.spin[0] += spin_transfer_x
                ball2.spin[1] += spin_transfer_y
                shot_sound.play()

# Menu handling
def draw_menu():
    screen.fill((20, 20, 20))
    for y in range(HEIGHT):
        shade = 20 + (y / HEIGHT) * 50
        pygame.draw.line(screen, (shade, shade, shade), (0, y), (WIDTH, y))
    title = font.render("Billiards Game", True, (255, 255, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    for button in MENU_BUTTONS:
        pygame.draw.rect(screen, (80, 80, 80), button["rect"], border_radius=10)
        pygame.draw.rect(screen, (120, 120, 120), button["rect"], 2, border_radius=10)
        text = font.render(button["text"], True, (255, 255, 255))
        screen.blit(text, (button["rect"].x + 70, button["rect"].y + 15))
    pygame.display.flip()

def handle_menu_events():
    global game_state, ai_difficulty, ai_mode
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in MENU_BUTTONS:
                if button["rect"].collidepoint(mouse_pos):
                    if button["text"] == "2 Players":
                        game_state = "game"
                        setup("2 Players")
                    elif button["text"] == "Easy AI":
                        ai_difficulty = 1
                        ai_mode = True
                        game_state = "game"
                        setup("AI")
                    elif button["text"] == "Hard AI":
                        ai_difficulty = 2
                        ai_mode = True
                        game_state = "game"
                        setup("AI")
                    elif button["text"] == "Quit":
                        return False
    return True

# Game over screen
def draw_game_over():
    screen.fill((20, 20, 20))
    for y in range(HEIGHT):
        shade = 20 + (y / HEIGHT) * 50
        pygame.draw.line(screen, (shade, shade, shade), (0, y), (WIDTH, y))
    result = font.render(f"{'Player 1' if winner == 'player1' else 'Player 2'} Wins!" if winner else "Game Over", True, (255, 255, 255))
    score_text = font.render(f"Player 1: {player1_score} Player 2: {player2_score}", True, (255, 255, 255))
    screen.blit(result, (WIDTH//2 - result.get_width()//2, HEIGHT//2 - 50))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()

# Update game state
def update_loop():
    global cue_active, power, game_state, current_player, player1_group, player2_group, foul, ball_in_hand, turn_timer, turn_transition
    if game_state == "menu":
        draw_menu()
        return handle_menu_events()
    if game_state == "game_over":
        draw_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False
        return True
    balls_stopped = all(not ball.pocketed and math.sqrt(ball.vel[0]**2 + ball.vel[1]**2) < MIN_SPEED for ball in balls)
    if balls_stopped and turn_transition > 0:
        turn_transition -= 0.1
    if not ball_in_hand:
        turn_timer -= 1 / FPS
    if turn_timer <= 0 and balls_stopped and not ball_in_hand:
        foul = True
        current_player = "player2" if current_player == "player1" else "player1"
        ball_in_hand = True
        turn_timer = TURN_TIME
        turn_transition = 1
    first_hit = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state = "menu"
        elif balls_stopped and not cue_active and turn_transition <= 0:
            if ball_in_hand and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                cue_ball = next(ball for ball in balls if ball.is_cue)
                cue_ball.pos = [max(BALL_RADIUS, min(WIDTH - BALL_RADIUS, mouse_x)), max(BALL_RADIUS, min(HEIGHT - BALL_RADIUS, mouse_y))]
                ball_in_hand = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                cue_active = True
            elif event.type == pygame.MOUSEBUTTONUP and cue_active:
                cue_active = False
                mouse_x, mouse_y = pygame.mouse.get_pos()
                cue_ball = next(ball for ball in balls if ball.is_cue)
                dx = mouse_x - cue_ball.pos[0]
                dy = mouse_y - cue_ball.pos[1]
                dist = max(1, math.sqrt(dx**2 + dy**2))
                cue_ball.vel[0] = (dx / dist) * power * 0.15
                cue_ball.vel[1] = (dy / dist) * power * 0.15
                cue_ball.spin = [(mouse_x - cue_ball.pos[0]) * 0.05, (mouse_y - cue_ball.pos[1]) * 0.05]
                shot_sound.play()
                time_bonus = int(turn_timer * 10)
                if current_player == "player1":
                    player1_score += time_bonus
                else:
                    player2_score += time_bonus
                turn_timer = TURN_TIME
                turn_transition = 1
                # Check first hit for foul
                first_hit = None
                for ball in balls:
                    if ball.pocketed or ball.is_cue:
                        continue
                    dx = ball.pos[0] - cue_ball.pos[0]
                    dy = ball.pos[1] - cue_ball.pos[1]
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < 2 * BALL_RADIUS:
                        first_hit = ball
                        break
                if first_hit and ((current_player == "player1" and player1_group and
                                  ((player1_group == "solids" and first_hit.number > 7) or
                                   (player1_group == "stripes" and first_hit.number <= 7 and first_hit.number != 8))) or
                                  (current_player == "player2" and player2_group and
                                   ((player2_group == "solids" and first_hit.number > 7) or
                                    (player2_group == "stripes" and first_hit.number <= 7 and first_hit.number != 8)))):
                    foul = True
                    current_player = "player2" if current_player == "player1" else "player1"
                    ball_in_hand = True
                elif not foul:
                    current_player = "player1" if ai_mode and current_player == "player2" else "player2" if current_player == "player1" else "player1"
                # Assign groups
                if player1_group is None and any(ball.pocketed and not ball.is_cue for ball in balls):
                    first_pocketed = next(ball for ball in balls if ball.pocketed and not ball.is_cue)
                    player1_group = "solids" if first_pocketed.number <= 7 else "stripes"
                    player2_group = "stripes" if player1_group == "solids" else "solids"
    if ai_mode and current_player == "player2" and balls_stopped and not cue_active and not ball_in_hand and turn_transition <= 0:
        cue_active = True
        ai_turn()
    if cue_active and current_player == "player1" and not ball_in_hand:
        power = min(power + 0.5, MAX_POWER)
    for ball in balls:
        ball.update()
    handle_collisions()
    # Draw
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WIDTH, HEIGHT))
    pygame.draw.rect(screen, TABLE_COLOR, (10, 10, WIDTH-20, HEIGHT-20))
    for pocket in POCKETS:
        pygame.draw.circle(screen, (0, 0, 0), pocket, POCKET_RADIUS)
    for ball in balls:
        ball.draw(screen)
    if cue_active and current_player == "player1" and not ball_in_hand:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cue_ball = next(ball for ball in balls if ball.is_cue)
        pygame.draw.line(screen, (255, 255, 255), (cue_ball.pos[0], cue_ball.pos[1]), (mouse_x, mouse_y), 2)
        pygame.draw.rect(screen, (255, 0, 0), (10, HEIGHT - 30, power * 2, 10))
    if ball_in_hand:
        cue_ball = next(ball for ball in balls if ball.is_cue)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, (255, 255, 255, 100), (mouse_x, mouse_y), BALL_RADIUS)
        instruction = font.render("Place Cue Ball", True, (255, 255, 255))
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2))
    score_text = font.render(f"Player 1: {player1_score} Player 2: {player2_score}", True, (255, 255, 255))
    turn_text = font.render(f"Turn: {'Player 1' if current_player == 'player1' else 'Player 2'}", True, (255, 255, 255))
    group_text = font.render(f"P1: {player1_group or 'None'} P2: {player2_group or 'None'}", True, (255, 255, 255))
    timer_text = font.render(f"Time: {int(turn_timer)}", True, (255, 255, 255))
    foul_text = font.render("Foul!" if foul else "", True, (255, 0, 0))
    transition_text = font.render(f"{'Player 1' if current_player == 'player1' else 'Player 2'}'s Turn", True, (255, 255, 255), (0, 0, 0, int(255 * turn_transition)))
    screen.blit(score_text, (10, 10))
    screen.blit(turn_text, (10, 40))
    screen.blit(group_text, (10, 70))
    screen.blit(timer_text, (10, 100))
    screen.blit(foul_text, (WIDTH//2 - foul_text.get_width()//2, HEIGHT//2))
    if turn_transition > 0:
        screen.blit(transition_text, (WIDTH//2 - transition_text.get_width()//2, HEIGHT//2 - 50))
    pygame.display.flip()
    return True

# Main loop
async def main():
    setup()
    running = True
    while running:
        running = update_loop()
        await asyncio.sleep(1.0 / FPS)
    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())