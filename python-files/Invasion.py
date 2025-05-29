#!/usr/bin/env python

import random, os.path, os, pygame

# import basic pygame modules
import pygame
from pygame.locals import *

# see if we can load more than standard BMP
if not pygame.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


# game constants
MAX_MAGIC = 2  # most player magic onscreen
ENEMY_ODDS = 60  # chances a new enemy appears
BOMB_ODDS = 95  # chances a new bomb will drop
ENEMY_RELOAD = 9  # frames between new enemies
SCREENRECT = Rect(0, 0, 960, 540)
SCORE = 0


main_dir = os.path.split(os.path.abspath(__file__))[0]


def menu():
    pygame.init()
    screen = pygame.display.set_mode(SCREENRECT.size)
    pygame.display.set_caption("Invasion - Menu")
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    while True:
        screen.fill((0, 0, 0))
        title = font.render("INVASION", True, (255, 255, 255))
        prompt = small_font.render("Press SPACE to Start", True, (255, 255, 255))
        control = small_font.render("Controls", True, (255, 220, 255))
        shoot = small_font.render("Press space to shoot", True, (255, 220, 255))
        retry = small_font.render("Press r to retry", True, (255, 220, 255))
        key = small_font.render("Press arrow keys to move", True, (255, 220, 255))
        screen.blit(title, (SCREENRECT.centerx - title.get_width() // 2, 150))
        screen.blit(prompt, (SCREENRECT.centerx - prompt.get_width() // 2, 250))
        screen.blit(control, (SCREENRECT.centerx - control.get_width() // 2, 300))
        screen.blit(shoot, (SCREENRECT.centerx - shoot.get_width() // 2, 350))
        screen.blit(retry, (SCREENRECT.centerx - retry.get_width() // 2, 400))
        screen.blit(key, (SCREENRECT.centerx - key.get_width() // 2, 450))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return  # Start the game

        clock.tick(30)


def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
    return surface.convert()


def load_images(*files):
    imgs = []
    for file in files:
        imgs.append(load_image(file))
    return imgs


class dummysound:
    def play(self):
        pass


def load_sound(file):
    if not pygame.mixer:
        return dummysound()
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pygame.mixer.Sound(file)
        return sound
    except pygame.error:
        print("Warning, unable to load, %s" % file)
    return dummysound()


class Player(pygame.sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        if direction:
            self.facing = direction
        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Enemy(pygame.sprite.Sprite):
    speed = 13
    animcycle = 12
    images = []

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Enemy.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % 3]


class Explosion(pygame.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


class Magic(pygame.sprite.Sprite):
    speed = -11
    images = []

    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class Bomb(pygame.sprite.Sprite):
    speed = 9
    images = []

    def __init__(self, enemy):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=enemy.rect.move(0, 5).midbottom)

    def update(self):
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 470:
            Explosion(self)
            self.kill()


class Score(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, 40)
        self.font.set_italic(1)
        self.color = Color("white")
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self):
        if SCORE != self.lastscore:
            self.lastscore = SCORE
            msg = "Score: %d" % SCORE
            self.image = self.font.render(msg, 0, self.color)


def main(winstyle=0):
    # Initialise pygame
    if pygame.get_sdl_version()[0] == 2:
        pygame.mixer.pre_init(44100, 32, 2, 1024)
    pygame.init()
    if pygame.mixer and not pygame.mixer.get_init():
        print("Warning, no sound")
        pygame.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img = load_image("player.gif")
    Player.images = [img, pygame.transform.flip(img, 1, 0)]
    img = load_image("explosion1.gif")
    Explosion.images = [img, pygame.transform.flip(img, 1, 1)]
    Enemy.images = load_images("enemy1.gif", "enemy2.gif", "enemy3.gif")
    Bomb.images = [load_image("bomb.gif")]
    Magic.images = [load_image("magic.gif")]

    # decorate the game window
    icon = pygame.transform.scale(Player.images[0], (32, 32))
    pygame.display.set_icon(icon)
    pygame.display.set_caption("Invasion")
    pygame.mouse.set_visible(0)

    # create the background, tile the bgd image
    bgdtile = load_image("background.png")
    background = pygame.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pygame.display.flip()

    # load the sound effects
    boom_sound = load_sound("boom.wav")
    shoot_sound = load_sound("car_door.wav")
    if pygame.mixer:
        music = os.path.join(main_dir, "data", "house_lo.wav")
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(-1)

    # Game Groups
    enemies = pygame.sprite.Group()
    magic = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    all = pygame.sprite.RenderUpdates()
    lastenemy = pygame.sprite.GroupSingle()

    # assign default groups to each sprite class
    Player.containers = all
    Enemy.containers = enemies, all, lastenemy
    Magic.containers = magic, all
    Bomb.containers = bombs, all
    Explosion.containers = all
    Score.containers = all

    # Create Some Starting Values
    global score
    enemyreload = ENEMY_RELOAD
    kills = 0
    clock = pygame.time.Clock()

    # initialise starting sprites
    global SCORE
    player = Player()
    Enemy()  # note, this 'lives' because it goes into a sprite group
    if pygame.font:
        all.add(Score())

    while player.alive():

        # get input
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return
            elif event.type == KEYDOWN:
                if event.key == K_r:
                    print("Restarting game")
                    SCORE = 0
                    return main(winstyle)
                if event.key == pygame.K_f:
                    if not fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pygame.display.set_mode(
                            SCREENRECT.size, winstyle | FULLSCREEN, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pygame.display.set_mode(
                            SCREENRECT.size, winstyle, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    # screen.fill((255, 0, 0))
                    pygame.display.flip()
                    fullscreen = not fullscreen

        keystate = pygame.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # handle player input
        direction = keystate[K_RIGHT] - keystate[K_LEFT]
        player.move(direction)
        firing = keystate[K_SPACE]
        if not player.reloading and firing and len(magic) < MAX_MAGIC:
            Magic(player.gunpos())
            shoot_sound.play()
        player.reloading = firing

        # Create new enemies
        if enemyreload:
            enemyreload = enemyreload - 1
        elif not int(random.random() * ENEMY_ODDS):
            Enemy()
            enemyreload = ENEMY_RELOAD

        # Drop bombs
        if lastenemy and not int(random.random() * BOMB_ODDS):
            Bomb(lastenemy.sprite)

        # Detect collisions
        for enemy in pygame.sprite.spritecollide(player, enemies, 1):
            boom_sound.play()
            Explosion(enemy)
            Explosion(player)
            SCORE = SCORE + 1
            player.kill()

        for enemy in pygame.sprite.groupcollide(magic, enemies, 1, 1).keys():
            boom_sound.play()
            Explosion(enemy)
            SCORE = SCORE + 1

        for bomb in pygame.sprite.spritecollide(player, bombs, 1):
            boom_sound.play()
            Explosion(player)
            Explosion(bomb)
            player.kill()

        # draw the scene
        dirty = all.draw(screen)
        pygame.display.update(dirty)

        # cap the framerate
        clock.tick(40)

    # player has died
    if pygame.mixer:
        pygame.mixer.music.fadeout(1000)
    small_font = pygame.font.Font(None, 36)
    while True:
        over = small_font.render("GAME OVER", True, (255, 220, 255))
        score_text = small_font.render(f"Score: {SCORE}", True, (255, 220, 255))
        screen.blit(over, (SCREENRECT.centerx - over.get_width() // 2, 150))
        screen.blit(score_text, (SCREENRECT.centerx - score_text.get_width() // 2, 250))
        pygame.display.flip()
        clock.tick(30)
        pygame.time.wait(1500)
        SCORE = 0
        return main(winstyle)


# menu and main functions
if __name__ == "__main__":
    menu()
    main()
