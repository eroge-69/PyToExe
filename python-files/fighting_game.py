"""
2D Fighting Game - Single-file Pygame
Filename: fighting_game.py
Requires: Python 3.8+ and pygame
Install pygame: pip install pygame

Controls:
 Player 1 (left): A = left, D = right, W = jump, S = attack
 Player 2 (right): LEFT = left, RIGHT = right, UP = jump, DOWN = attack

How to run:
 python fighting_game.py
"""

import pygame
import sys
from dataclasses import dataclass

# ---- Settings ----
WIDTH, HEIGHT = 1000, 600
FPS = 60
GRAVITY = 1.0
GROUND_Y = HEIGHT - 100

# Player settings
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 100
PLAYER_SPEED = 6
JUMP_SPEED = -16
ATTACK_DURATION = 12  # frames
ATTACK_COOLDOWN = 30  # frames
ATTACK_RANGE = 40
ATTACK_DAMAGE = 10
MAX_HEALTH = 100

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (200,30,30)
GREEN = (40,200,40)
BLUE = (50,120,220)
GREY = (130,130,130)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Fighting Game - Simple Pygame")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 56)

@dataclass
class Player:
    x: float
    y: float
    w: int
    h: int
    facing: int  # -1 left, 1 right
    color: tuple
    keys: dict

    vel_x: float = 0
    vel_y: float = 0
    on_ground: bool = False
    attacking: bool = False
    attack_timer: int = 0
    attack_cooldown: int = 0
    health: int = MAX_HEALTH
    alive: bool = True

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def attack_hitbox(self):
        if self.facing >= 0:
            hx = self.x + self.w
        else:
            hx = self.x - ATTACK_RANGE
        hy = self.y + 20
        return pygame.Rect(int(hx), int(hy), ATTACK_RANGE, self.h - 40)

    def start_attack(self):
        if self.attack_cooldown == 0 and not self.attacking and self.alive:
            self.attacking = True
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = ATTACK_COOLDOWN

    def update(self):
        if not self.on_ground:
            self.vel_y += GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y

        if self.y + self.h >= GROUND_Y:
            self.y = GROUND_Y - self.h
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.x < 0:
            self.x = 0
        if self.x + self.w > WIDTH:
            self.x = WIDTH - self.w

    def take_hit(self, damage, knockback):
        if not self.alive:
            return
        self.health -= damage
        self.vel_x += knockback
        if self.health <= 0:
            self.health = 0
            self.alive = False

def draw_ground(surface):
    pygame.draw.rect(surface, GREY, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

def draw_health_bar(surface, x, y, w, h, health):
    pygame.draw.rect(surface, RED, (x, y, w, h))
    inner_w = max(0, int((health / MAX_HEALTH) * w))
    pygame.draw.rect(surface, GREEN, (x, y, inner_w, h))
    pygame.draw.rect(surface, BLACK, (x, y, w, h), 2)

p1_keys = {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w, 'attack': pygame.K_s}
p2_keys = {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_UP, 'attack': pygame.K_DOWN}

player1 = Player(150, GROUND_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, 1, BLUE, p1_keys)
player2 = Player(WIDTH - 150 - PLAYER_WIDTH, GROUND_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, -1, RED, p2_keys)

ROUND_TIME = 60

def reset_round():
    global player1, player2, round_over, round_winner, timer_frames
    player1.x = 150
    player1.y = GROUND_Y - PLAYER_HEIGHT
    player1.vel_x = 0
    player1.vel_y = 0
    player1.health = MAX_HEALTH
    player1.alive = True
    player1.attacking = False
    player1.attack_cooldown = 0

    player2.x = WIDTH - 150 - PLAYER_WIDTH
    player2.y = GROUND_Y - PLAYER_HEIGHT
    player2.vel_x = 0
    player2.vel_y = 0
    player2.health = MAX_HEALTH
    player2.alive = True
    player2.attacking = False
    player2.attack_cooldown = 0

    round_over = False
    round_winner = None
    timer_frames = ROUND_TIME * FPS

round_over = False
round_winner = None
timer_frames = ROUND_TIME * FPS
reset_round()

def handle_input(keys_pressed):
    if player1.alive:
        mv = 0
        if keys_pressed[player1.keys['left']]:
            mv -= 1
        if keys_pressed[player1.keys['right']]:
            mv += 1
        player1.vel_x = mv * PLAYER_SPEED
        if mv != 0:
            player1.facing = mv
        if keys_pressed[player1.keys['jump']] and player1.on_ground:
            player1.vel_y = JUMP_SPEED
            player1.on_ground = False
        if keys_pressed[player1.keys['attack']]:
            player1.start_attack()
    else:
        player1.vel_x = 0

    if player2.alive:        mv = 0
        if keys_pressed[player2.keys['left']]:
            mv -= 1
        if keys_pressed[player2.keys['right']]:
            mv += 1
        player2.vel_x = mv * PLAYER_SPEED
        if mv != 0:            player2.facing = mv
        if keys_pressed[player2.keys['jump']] and player2.on_ground:
            player2.vel_y = JUMP_SPEED
            player2.on_ground = False
        if keys_pressed[player2.keys['attack']]:
            player2.start_attack()
    else:
        player2.vel_x = 0

def check_attacks():
    if player1.attacking and player1.attack_timer == ATTACK_DURATION - 1:
        hb = player1.attack_hitbox()
        if hb.colliderect(player2.rect()):
            kb = 8 * player1.facing
            player2.take_hit(ATTACK_DAMAGE, kb)

    if player2.attacking and player2.attack_timer == ATTACK_DURATION - 1:
        hb = player2.attack_hitbox()
        if hb.colliderect(player1.rect()):
            kb = 8 * player2.facing
            player1.take_hit(ATTACK_DAMAGE, kb)

def draw_player(surface, p: Player):
    pygame.draw.rect(surface, p.color, p.rect())
    eye_x = p.x + (p.w - 10) if p.facing >= 0 else p.x + 5
    pygame.draw.circle(surface, WHITE, (int(eye_x), int(p.y + 25)), 6)
    if p.attacking:
        hb = p.attack_hitbox()
        pygame.draw.rect(surface, (255,180,50), hb, 2)

running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and round_over:
                reset_round()

    keys = pygame.key.get_pressed()
    if not round_over:
        handle_input(keys)
        player1.update()
        player2.update()

        if player1.rect().colliderect(player2.rect()):
            overlap = (player1.x + player1.w) - player2.x if player1.x < player2.x else (player2.x + player2.w) - player1.x
            sep = overlap / 2 + 1
            if player1.x < player2.x:
                player1.x -= sep
                player2.x += sep
            else:
                player1.x += sep
                player2.x -= sep

        check_attacks()
        timer_frames -= 1
        if timer_frames <= 0:
            round_over = True
            if player1.health > player2.health:
                round_winner = 'Player 1'
            elif player2.health > player1.health:
                round_winner = 'Player 2'
            else:
                round_winner = 'Draw'

        if not player1.alive or not player2.alive:
            round_over = True
            if not player1.alive and player2.alive:
                round_winner = 'Player 2'
            elif not player2.alive and player1.alive:
                round_winner = 'Player 1'
            else:
                round_winner = 'Draw'

    screen.fill((30,30,30))
    draw_ground(screen)
    draw_player(screen, player1)
    draw_player(screen, player2)

    draw_health_bar(screen, 20, 20, 350, 24, player1.health)
    draw_health_bar(screen, WIDTH - 370, 20, 350, 24, player2.health)
    label1 = font.render('Player 1', True, WHITE)
    label2 = font.render('Player 2', True, WHITE)
    screen.blit(label1, (20, 48))
    screen.blit(label2, (WIDTH - 120, 48))

    seconds_left = max(0, timer_frames // FPS)
    timer_surf = font.render(f'Time: {seconds_left}', True, WHITE)
    screen.blit(timer_surf, (WIDTH//2 - 40, 20))

    if round_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,170))
        screen.blit(overlay, (0,0))
        if round_winner == 'Draw':
            text = big_font.render('DRAW', True, WHITE)
        else:
            text = big_font.render(f'{round_winner} WINS!', True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 60))
        info = font.render('Press R to restart', True, WHITE)
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 10))

    hint = font.render('P1: A/D move, W jump, S attack   |   P2: Arrows move/jump/down to attack', True, WHITE)
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
sys.exit()
