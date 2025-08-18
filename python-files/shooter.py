import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
TILE_SIZE = 40
ROWS = 16
COLS = 150
SCROLL_THRESH = 200
bg_scroll = 0
level = 1
MAX_LEVELS = 3
start_game = False
start_intro = False

# define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# load music and sounds
mixer.music.load('audio/music2.mp3')
mixer.music.set_volume(0.3)
mixer.music.play(-1, 0.0, 5000)

jump_fx = mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)

# load images
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

# store tiles in a list
img_list = []
for x in range(TILE_SIZE):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# bullet
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

# pick up boxes
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# define colours
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump and not self.in_air:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # check for collision with floor
        if self.rect.bottom + dy > SCREEN_HEIGHT - 50:
            dy = SCREEN_HEIGHT - 50 - self.rect.bottom
            self.in_air = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction),
                            self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1
            shot_fx.play()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100

        prev_midbottom = self.rect.midbottom

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.midbottom = prev_midbottom

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    self.obstacle_list.append(tile_data)

                if tile == 15:
                    spawn_x = x * TILE_SIZE + TILE_SIZE // 2
                    spawn_y = y * TILE_SIZE + TILE_SIZE
                    player = Soldier('player', spawn_x, spawn_y, 1.65, 5, 20, 5)
        return player

    def draw(self):
        for img, rect in self.obstacle_list:
            screen.blit(img, rect)

# create sprite groups
bullet_group = pygame.sprite.Group()

def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

def reset_level():
    bullet_group.empty()
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)
    return world_data

world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player = world.process_data(world_data)

run = True
while run:
    clock.tick(FPS)
    draw_bg()
    world.draw()
    player.update()
    player.draw()

    # update player actions
    if player.alive:
        if shoot:
            player.shoot()
        if player.in_air:
            player.update_action(2) # jump
        elif moving_left or moving_right:
            player.update_action(1) # run
        else:
            player.update_action(0) # idle

        player.move(moving_left, moving_right)
    else:
        player.update_action(3)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
