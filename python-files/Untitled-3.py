
import pygame
import random
from pygame.locals import (
    QUIT
)

pygame.mixer.init()
pygame.init()

# Screen
screen_width = 1200
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("AmiR's Mario - 2 Player Edition")

clock = pygame.time.Clock()


# Sounds
pygame.mixer.music.load("D:/tarkibiat/New folder/Mario/Background.mp3")
jump_sound = pygame.mixer.Sound("D:/tarkibiat/New folder/Mario/jump.mp3")
win_sound = pygame.mixer.Sound("D:/tarkibiat/New folder/Mario/win.mp3")
lose_sound = pygame.mixer.Sound("D:/tarkibiat/New folder/Mario/lose.mp3")

zoom = 2.5
camera_x = 0

map_img = pygame.image.load("D:/tarkibiat/New folder/Mario/map.png").convert()
world_width = map_img.get_width()
world_height = map_img.get_height()

map_scaled = pygame.transform.scale(
    map_img,
    (int(world_width * zoom), int(world_height * zoom))
)

GROUND_Y = world_height - 50


# Mario class and functions
class Mario(pygame.sprite.Sprite):
    def __init__(self, player_num, start_x=20):
        super().__init__()
        self.player_num = player_num
        
        if self.player_num == 1:
            path_right = "D:/tarkibiat/New folder/Mario/mario.png"
            path_left = "D:/tarkibiat/New folder/Mario/mario_Back.png"
            path_up = "D:/tarkibiat/New folder/Mario/mario_Up.png"

        else:
            path_right = "D:/tarkibiat/New folder/Mario/mario1.png"
            path_left = "D:/tarkibiat/New folder/Mario/mario_Back1.png"
            path_up = "D:/tarkibiat/New folder/Mario/mario_Up1.png"

        self.image_idle = pygame.image.load(path_right).convert_alpha()
        self.image_right = pygame.image.load(path_right).convert_alpha()
        self.image_left = pygame.image.load(path_left).convert_alpha()
        self.image_jump = pygame.image.load(path_up).convert_alpha()

        self.original_surf = self.image_idle 
        self.image = self.image_idle 

        
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.gravity = 0.2
        self.jump_requested = False

        self.world_x = start_x
        self.world_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True
        self.is_big = False
        self.lives = 3
        self.score = 0
        self.is_active = True 

    def get_screen_rect(self, camera_x, zoom):
        screen_x = int((self.world_x - camera_x) * zoom)
        screen_y = int(self.world_y * zoom)
        return pygame.Rect(
            screen_x,
            screen_y,
            int(self.width * zoom),
            int(self.height * zoom),
        )

    def grow(self):
        if not self.is_big:
            self.is_big = True

            self.width = self.original_surf.get_width() * 1.5
            self.height = self.original_surf.get_height() * 1.5

    def take_hit(self):
        if self.is_big:
            self.is_big = False
            self.width = self.original_surf.get_width()
            self.height = self.original_surf.get_height()
        else:
            self.lives -= 1
            if self.lives <= 0:
                self.is_active = False 


    def update(self, move_list):
        if not self.is_active:
            self.velocity_x = 0
            return

        if move_list[0]:
            self.jump_requested = True

        self.velocity_x = 0
        if move_list[1]: 
            self.velocity_x = 2

        if move_list[2]: 
            self.velocity_x = -2

        if self.jump_requested and self.on_ground:
            self.velocity_y = -6
            jump_sound.play()
            self.on_ground = False
            self.jump_requested = False 

        if self.world_x < 0:
            self.world_x = 0

        if move_list[2]: 
            self.image = self.image_left

        elif move_list[1]: 
            self.image = self.image_right

        elif not self.on_ground:
             self.image = self.image_jump

        else:
             self.image = self.image_idle

        self.velocity_y += self.gravity
        self.world_x += self.velocity_x
        self.world_y += self.velocity_y

        if self.world_y >= screen_height / zoom:
            self.lives = 0
            self.is_active = False


    def reset(self, start_x):
        self.world_x = start_x
        self.world_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = True
        self.is_big = False
        self.lives = 1
        self.score = 0
        self.is_active = True
        self.width = self.original_surf.get_width()
        self.height = self.original_surf.get_height()



# Enemy's Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("D:/tarkibiat/New folder/Mario/enemy1.png").convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.world_x = x
        self.world_y = y
        self.velocity_x = -0.65 
        self.velocity_y = 0
        self.gravity = 0.2
        self.on_ground = False

    def get_screen_rect(self, camera_x, zoom):
        screen_x = int((self.world_x - camera_x) * zoom)
        screen_y = int(self.world_y * zoom)
        return pygame.Rect(screen_x, screen_y,
                           int(self.width * zoom), int(self.height * zoom))

    def is_visible_on_screen(self, camera_x, screen_width, zoom):
        screen_x = (self.world_x - camera_x) * zoom
        return -self.width * zoom < screen_x < screen_width + self.width * zoom

    def handle_collision(self, obj):
        enemy_rect = pygame.Rect(self.world_x, self.world_y, self.width, self.height)
        obj_rect = pygame.Rect(obj.world_x, obj.world_y, obj.image.get_width(), obj.image.get_height())

        if not enemy_rect.colliderect(obj_rect):
            return

        dx = (enemy_rect.centerx - obj_rect.centerx)
        dy = (enemy_rect.centery - obj_rect.centery)
        combined_half_widths = (enemy_rect.width + obj_rect.width) // 2
        combined_half_heights = (enemy_rect.height + obj_rect.height) // 2

        overlap_x = combined_half_widths - abs(dx)
        overlap_y = combined_half_heights - abs(dy)

        if overlap_x < overlap_y:
            if dx > 0:  
                self.world_x = obj.world_x + obj.image.get_width()
            else:
                self.world_x = obj.world_x - self.width
            self.velocity_x *= -1

        else:
            if dy > 0:
                self.world_y = obj.world_y + obj.image.get_height()
                self.velocity_y = 0
            else:
                self.world_y = obj.world_y - self.height
                self.velocity_y = 0
                self.on_ground = True


    def update(self, pipes, platforms):
        self.velocity_y += self.gravity

        self.world_x += self.velocity_x
        self.world_y += self.velocity_y

        self.on_ground = False
        for obj in pipes.sprites() + platforms.sprites():
            self.handle_collision(obj)



class obstacles(pygame.sprite.Sprite):
    def __init__(self, x, y , image_path = "D:/tarkibiat/New folder/Mario/pipe1.png"):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()

        self.world_x = x
        self.world_y = y

        self.screen_rect = self.rect.copy()


    def get_screen_rect(self, camera_x, zoom):

        screen_x = int((self.world_x - camera_x) * zoom)
        screen_y = int(self.world_y * zoom)
        return pygame.Rect(
            screen_x,
            screen_y,
            int(self.image.get_width() * zoom),
            int(self.image.get_height() * zoom),
        )

    def update(self, camera_x, zoom):

        self.screen_rect = self.get_screen_rect(camera_x, zoom)


class Pipe1(obstacles):
    def __init__(self, x, y,image_path = "D:/tarkibiat/New folder/Mario/pipe1.png"):
        super().__init__(x,y,image_path)


class Pipe2(obstacles):
    def __init__(self, x, y,image_path ="D:/tarkibiat/New folder/Mario/pipe2.png"):
        super().__init__(x, y,image_path)


class Pipe3(obstacles):
    def __init__(self, x, y,image_path ="D:/tarkibiat/New folder/Mario/pipe3.png"):
        super().__init__(x, y,image_path)


class Platform1(obstacles):
    def __init__(self, x, y,image_path ="D:/tarkibiat/New folder/Mario/platform1.png"):
        super().__init__(x, y,image_path)

class Platform2(obstacles):
    def __init__(self, x, y,image_path = "D:/tarkibiat/New folder/Mario/platform2.png"):
        super().__init__(x, y,image_path)

class Platform3(obstacles):
    def __init__(self, x, y,image_path = "D:/tarkibiat/New folder/Mario/platform3.png"):
        super().__init__(x, y,image_path)

class Platform4(obstacles):
    def __init__(self, x, y,image_path = "D:/tarkibiat/New folder/Mario/platform4.png"):
        super().__init__(x, y,image_path)

class Brick(obstacles):
    def __init__(self,x,y,image_path = "D:/tarkibiat/New folder/Mario/brick1.png"):
        super().__init__(x,y,image_path)

class Stair(obstacles):
    def __init__(self,x,y,image_path = "D:/tarkibiat/New folder/Mario/stair.png"):
        super().__init__(x,y,image_path)

class Box(obstacles):
    def __init__(self,x,y,image_path = "D:/tarkibiat/New folder/Mario/box.png"):
        super().__init__(x,y,image_path)

class Castle(obstacles):
    def __init__(self,x,y,image_path="D:/tarkibiat/New folder/Mario/castle.png"):
        super().__init__(x,y,image_path)



class Mushroom(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load("D:/tarkibiat/New folder/Mario/mushroom.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.velocity_x = 1.2
        self.velocity_y = -3  
        self.rising = True  

    def update(self, pipes, platforms):
        if self.rising:
            self.world_y += self.velocity_y
            self.velocity_y += self.gravity
            if self.velocity_y >= 0:
                self.rising = False
            return

        super().update(pipes, platforms)



class Gift(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("D:/tarkibiat/New folder/Mario/coin.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.world_x = x
        self.world_y = y
        self.velocity_y = -3
        self.gravity = 0.1
        self.life_time = 30

    def update(self):
        self.velocity_y += self.gravity
        self.world_y += self.velocity_y
        self.life_time -= 1
        if self.life_time <= 0:
            self.kill() 

    def get_screen_rect(self, camera_x, zoom):
        screen_x = int((self.world_x - camera_x) * zoom)
        screen_y = int(self.world_y * zoom)
        return pygame.Rect(screen_x, screen_y, int(self.image.get_width() * zoom), int(self.image.get_height() * zoom))



class QuestionBox(obstacles):
    def __init__(self, x, y, image_path="D:/tarkibiat/New folder/Mario/box.png"):
        super().__init__(x, y, image_path)
        self.hit = False
        self.gift_released = False

    def release_gift(self, player):
        if self.gift_released:
            return
        self.gift_released = True
        self.image = pygame.image.load("D:/tarkibiat/New folder/Mario/box_used.png").convert_alpha()

        kind = random.choice(["coin", "mushroom"])
        if kind == "coin":
            gift = Gift(self.world_x + 8, self.world_y - 20)
            player.score += 10 
        else:
            gift = Mushroom(self.world_x + 8, self.world_y - 20)

        gifts.add(gift)


# Sprite Groups
enemies = pygame.sprite.Group()
pipes = pygame.sprite.Group()
platforms = pygame.sprite.Group()
gifts = pygame.sprite.Group()

# Player instances
mario1 = Mario(player_num=1, start_x=20)
mario2 = Mario(player_num=2, start_x=40)
players = pygame.sprite.Group(mario1, mario2)


def populate_world():
    # Clear all previous sprites
    enemies.empty()
    pipes.empty()
    platforms.empty()
    gifts.empty()
    
    # Map's Details 
    add_question_box(256, 144) 
    add_question_box(336, 144) 
    add_question_box(1248, 144) 
    add_question_box(1744, 80) 

    add_box(256,144)
    add_box(368,144)
    add_box(352,80)
    add_box(1505,80)
    add_box(1696,144)
    add_box(1744,144)
    add_box(1792,144)
    add_box(2064,80)
    add_box(2080,80)
    add_box(2720,144)

    add_enemy(352,192)
    add_enemy(640,192)
    add_enemy(816,192)
    add_enemy(840,192)
    add_enemy(1280,64)
    add_enemy(1312,64)
    add_enemy(1552,192)
    add_enemy(1578,192)
    add_enemy(1825,192)
    add_enemy(1848,192)
    add_enemy(1986,192)
    add_enemy(2010,192)
    add_enemy(2050,192)
    add_enemy(2078,192)
    add_enemy(2785,192)
    add_enemy(2808,192)

    add_pipe1(448, 176)
    add_pipe2(608,158)
    add_pipe3(734,144)
    add_pipe3(913,144)
    add_pipe1(2608,176)
    add_pipe1(2864,176)

    add_platform1(0,208)
    add_platform2(1136,208)
    add_platform3(1424,208)
    add_platform4(2480,208)

    add_brick1(320,144)
    add_brick1(352,144)
    add_brick1(384,144)
    add_brick1(1232,144)
    add_brick1(1264,144)
    add_brick1(1504,144)
    add_brick1(1888,144)
    add_brick1(2736,144)
    add_brick1(1280,80)
    add_brick1(1296,80)
    add_brick1(1312,80)
    add_brick1(1328,80)
    add_brick1(1344,80)
    add_brick1(1360,80)
    add_brick1(1376,80)
    add_brick1(1392,80)
    add_brick1(1456,80)
    add_brick1(1472,80)
    add_brick1(1488,80)
    add_brick1(1600,144)
    add_brick1(1616,144)
    add_brick1(1616,144)
    add_brick1(1936,80)
    add_brick1(1952,80)
    add_brick1(1968,80)
    add_brick1(2048,80)
    add_brick1(2096,80)
    add_brick1(2064,144)
    add_brick1(2080,144)
    add_brick1(2688,144)
    add_brick1(2704,144)

    add_stair(2145,192)
    add_stair(2161,192)
    add_stair(2177,192)
    add_stair(2193,192)
    add_stair(2161,176)
    add_stair(2177,176)
    add_stair(2193,176)
    add_stair(2177,160)
    add_stair(2193,160)
    add_stair(2193,144)

    add_stair(2240,192)
    add_stair(2256,192)
    add_stair(2272,192)
    add_stair(2288,192)
    add_stair(2240,176)
    add_stair(2256,176)
    add_stair(2272,176)
    add_stair(2240,160)
    add_stair(2256,160)
    add_stair(2240,144)

    add_stair(2368,192)
    add_stair(2384,192)
    add_stair(2400,192)
    add_stair(2416,192)
    add_stair(2432,192)
    add_stair(2384,176)
    add_stair(2400,176)
    add_stair(2416,176)
    add_stair(2432,176)
    add_stair(2400,160)
    add_stair(2416,160)
    add_stair(2432,160)
    add_stair(2416,144)
    add_stair(2432,144)

    add_stair(2480,192)
    add_stair(2496,192)
    add_stair(2512,192)
    add_stair(2528,192)
    add_stair(2480,176)
    add_stair(2496,176)
    add_stair(2512,176)
    add_stair(2480,160)
    add_stair(2496,160)
    add_stair(2480,144)

    add_stair(2914,192)
    add_stair(2930,192)
    add_stair(2946,192)
    add_stair(2962,192)
    add_stair(2978,192)
    add_stair(2994,192)
    add_stair(3010,192)
    add_stair(3026,192)
    add_stair(3042,192)
    add_stair(2930,176)
    add_stair(2946,176)
    add_stair(2962,176)
    add_stair(2978,176)
    add_stair(2994,176)
    add_stair(3010,176)
    add_stair(3026,176)
    add_stair(3042,176)
    add_stair(2946,160)
    add_stair(2962,160)
    add_stair(2978,160)
    add_stair(2994,160)
    add_stair(3010,160)
    add_stair(3026,160)
    add_stair(3042,160)
    add_stair(2962,144)
    add_stair(2978,144)
    add_stair(2994,144)
    add_stair(3010,144)
    add_stair(3026,144)
    add_stair(3042,144)
    add_stair(2978,128)
    add_stair(2994,128)
    add_stair(3010,128)
    add_stair(3026,128)
    add_stair(3042,128)
    add_stair(2994,112)
    add_stair(3010,112)
    add_stair(3026,112)
    add_stair(3042,112)
    add_stair(3010,96)
    add_stair(3026,96)
    add_stair(3042,96)
    add_stair(3026,80)
    add_stair(3042,80)

    add_castle(3232,130)


# Add Functions 
def add_pipe1(x, y):
    pipe = Pipe1(x, y)
    pipes.add(pipe)

def add_pipe2(x, y):
    pipe = Pipe2(x, y)
    pipes.add(pipe)

def add_pipe3(x, y):
    pipe = Pipe3(x, y)
    pipes.add(pipe)

def add_platform1(x,y):
    Platform = Platform1(x,y)
    platforms.add(Platform)

def add_platform2(x,y):
    Platform = Platform2(x,y)
    platforms.add(Platform)

def add_platform3(x,y):
    Platform = Platform3(x,y)
    platforms.add(Platform)

def add_platform4(x,y):
    Platform = Platform4(x,y)
    platforms.add(Platform)

def add_brick1(x,y):
    brick = Brick(x,y)
    platforms.add(brick)

def add_stair(x,y):
    stair = Stair(x,y)
    platforms.add(stair)

def add_enemy(x, y):
    en = Enemy(x, y)
    enemies.add(en)

def add_question_box(x, y):
    qbox = QuestionBox(x, y)
    platforms.add(qbox)

def add_box(x,y):
    box = Box(x,y)
    platforms.add(box)

def add_castle(x,y):
    castle = Castle(x,y)
    platforms.add(castle)



# Collision Functions 
def handle_collision_screen(mario, obj, camera_x, zoom):
    if not mario.is_active: return

    m_rect = mario.get_screen_rect(camera_x, zoom)
    o_rect = obj.get_screen_rect(camera_x, zoom)

    if not m_rect.colliderect(o_rect):
        return

    dx = m_rect.centerx - o_rect.centerx
    dy = m_rect.centery - o_rect.centery

    combined_half_widths = (m_rect.width + o_rect.width) / 2
    combined_half_heights = (m_rect.height + o_rect.height) / 2

    overlap_x = combined_half_widths - abs(dx)
    overlap_y = combined_half_heights - abs(dy)

    if overlap_x < overlap_y:
        if dx > 0:
            mario.world_x = obj.world_x + obj.image.get_width()
        else:
            mario.world_x = obj.world_x - mario.width
        mario.velocity_x = 0
    else:
        if dy > 0:
            mario.world_y = obj.world_y + obj.image.get_height()
            mario.velocity_y = 0
            if isinstance(obj, QuestionBox) and not obj.hit:
                obj.hit = True
                obj.release_gift(mario)
        else:
            mario.world_y = obj.world_y - mario.height
            mario.velocity_y = 0
            mario.on_ground = True



def handle_mario_enemy_collision(mario, enemy, camera_x, zoom):
    if not mario.is_active: return None

    m_rect = mario.get_screen_rect(camera_x, zoom)
    e_rect = enemy.get_screen_rect(camera_x, zoom)

    if not m_rect.colliderect(e_rect):
        return None

    vertical_overlap = m_rect.bottom - e_rect.top

    if mario.velocity_y > 0 and 0 < vertical_overlap < 15:
        return "stomp"
    else:
        return "hit"


# Remach
def reset_game():
    global win, game_over, camera_x
    win = False
    game_over = False
    camera_x = 0
    
    mario1.reset(start_x=20)
    mario2.reset(start_x=40)
    
    populate_world()
    
    pygame.mixer.music.play(loops=-1)


# Controller Setup
pygame.joystick.init()
joysticks = []
font = pygame.font.SysFont(None, 50)

while len(joysticks) < 2:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.JOYDEVICEADDED:
            print("Game Pad is CONECTED.")

        if event.type == pygame.JOYDEVICEREMOVED:
            print("Game Pad is DISCONECTED.")


    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    num_connected = len(joysticks)


    screen.fill((20, 20, 40))
    message = f"Waiting for 2 controllers... {num_connected} connected."
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width / 2, screen_height / 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    clock.tick(20) 

print(f"{len(joysticks)} Contoller is Recognaiz. start GAMMING..")


# Initial Game Setup
reset_game()
running = True


# LOOP
while running:
    dt = clock.tick(60)

    move_list1 = [False, False, False]  # [jump, right, left]
    move_list2 = [False, False, False]


    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == pygame.JOYBUTTONDOWN:

            if event.instance_id == 1:
                if event.button == 0:  
                    move_list1[0] = True


            elif event.instance_id == 0:
                if event.button == 0:  
                    move_list2[0] = True


            if event.button == 9 and (game_over or win):
                reset_game()

    p1_moved_with_stick = False

    try:
        axis_x_p1 = joysticks[0].get_axis(0)
        if axis_x_p1 > 0.5:
            move_list1[1] = True
            p1_moved_with_stick = True

        elif axis_x_p1 < -0.5:
            move_list1[2] = True
            p1_moved_with_stick = True

    except pygame.error: pass
    
    if not p1_moved_with_stick:
        try:
            hat_p1 = joysticks[0].get_hat(0)
            if hat_p1[0] == 1: move_list1[1] = True

            elif hat_p1[0] == -1: move_list1[2] = True

        except pygame.error: pass


    p2_moved_with_stick = False
    try:
        axis_x_p2 = joysticks[1].get_axis(0)
        if axis_x_p2 > 0.5:
            move_list2[1] = True
            p2_moved_with_stick = True

        elif axis_x_p2 < -0.5:
            move_list2[2] = True
            p2_moved_with_stick = True

    except pygame.error: pass
    
    if not p2_moved_with_stick:
        try:
            hat_p2 = joysticks[1].get_hat(0)
            if hat_p2[0] == 1: move_list2[1] = True
            elif hat_p2[0] == -1: move_list2[2] = True
        except pygame.error: pass


    if not game_over and not win:

        mario1.update(move_list1)
        mario2.update(move_list2)
        

        for en in enemies:
            if en.is_visible_on_screen(camera_x, screen_width, zoom): en.update(pipes, platforms)

        for gift in gifts:
            if isinstance(gift, Mushroom):
                gift.update(pipes, platforms)
            else:
                gift.update()


        for mario in players:
            if not mario.is_active: continue
            for obj in pipes.sprites() + platforms.sprites():
                handle_collision_screen(mario, obj, camera_x, zoom)

            for en in enemies.copy():
                result = handle_mario_enemy_collision(mario, en, camera_x, zoom)

                if result == "stomp":
                    enemies.remove(en); mario.velocity_y = -3; mario.score += 100

                elif result == "hit":
                    mario.take_hit()
                    break
                
            for gift in gifts.copy():

                if mario.get_screen_rect(camera_x, zoom).colliderect(gift.get_screen_rect(camera_x, zoom)):

                    if isinstance(gift, Mushroom): mario.grow()
                    mario.score += 50
                    gifts.remove(gift)



    active_players = [p for p in players if p.is_active]

    if active_players:
        leading_player_x = max(p.world_x for p in active_players)
        half_screen_world = (screen_width / 2) / zoom
        camera_x = leading_player_x - half_screen_world

        if camera_x < 0:
            camera_x = 0

        max_camera_x = world_width - (screen_width / zoom)

        if camera_x > max_camera_x:
            camera_x = max_camera_x

    if any(p.world_x >= 3380 for p in players if p.is_active) and not win:
        win = True; win_sound.play()
        pygame.mixer.music.stop()

    if all(not p.is_active for p in players) and not game_over and not win:
        game_over = True
        lose_sound.play()
        pygame.mixer.music.stop()


    screen.fill((0, 0, 0))
    screen.blit(map_scaled, (-int(camera_x * zoom), 0))

    all_obstacles = pipes.sprites() + platforms.sprites()

    for obj in all_obstacles:
        obj_rect = obj.get_screen_rect(camera_x, zoom)
        obj_img_scaled = pygame.transform.scale(obj.image, (obj_rect.width, obj_rect.height))
        screen.blit(obj_img_scaled, obj_rect.topleft)
        
    for en in enemies:
        en_rect = en.get_screen_rect(camera_x, zoom)
        en_img_scaled = pygame.transform.scale(en.image, (en_rect.width, en_rect.height))
        screen.blit(en_img_scaled, en_rect.topleft)

    for gift in gifts:
        g_rect = gift.get_screen_rect(camera_x, zoom)
        gift_img_scaled = pygame.transform.scale(gift.image, (g_rect.width, g_rect.height))
        screen.blit(gift_img_scaled, g_rect.topleft)

    for mario in players:
        if mario.is_active:
            m_rect = mario.get_screen_rect(camera_x, zoom)
            mario_img_scaled = pygame.transform.scale(mario.image, (int(mario.width * zoom), int(mario.height * zoom)))
            screen.blit(mario_img_scaled, m_rect.topleft)


    font = pygame.font.SysFont("chiller", 36)
    p1 = font.render("<Player1>", True, (0, 0, 0))

    p1_score_text = font.render(f"Score: {mario1.score}", True, (255, 255, 0))
    p1_lives_text = font.render(f"Lives: {mario1.lives}", True, (255, 0, 0))

    screen.blit(p1, (8, 10))
    screen.blit(p1_score_text, (20, 45))
    screen.blit(p1_lives_text, (20, 75))

    p2 = font.render(f"<Player2>", True, (0, 0, 0))
    p2_lives_text = font.render(f"Lives: {mario2.lives}", True, (255, 0, 0))

    p2_score_text = font.render(f"Score: {mario2.score}", True, (255, 255, 0))


    screen.blit(p2, (1050,10))
    screen.blit(p2_score_text, (1065,45))
    screen.blit(p2_lives_text, (1065,75))


    if game_over or win:
        font_large, font_small = pygame.font.SysFont(None, 100), pygame.font.SysFont(None, 40)
        message_text = "You Win!" if win else "GAME OVER"

        color = (255, 215, 0) if win else (0, 0, 0)
        main_msg = font_large.render(message_text, True, color)
        rematch_msg = font.render("Press START to Play Again", True, (255, 255, 255))

        font22 = pygame.font.SysFont(None, 30)

        if game_over:
            text_programmer = font.render("Powered by AmiR ",True,(0,0,0))
        
        else:
            text_programmer = font.render("Powered by AmiR",True,(255,215,0))


        main_rect = main_msg.get_rect(center=(screen_width / 2, screen_height / 2 - 30))
        rematch_rect = rematch_msg.get_rect(center=(screen_width / 2 , screen_height / 2 + 150))
        text2_rect = text_programmer.get_rect(center=(screen_width // 2, screen_height // 2 + 15))

        screen.blit(main_msg, main_rect)
        screen.blit(rematch_msg, rematch_rect)
        screen.blit(text_programmer, text2_rect)

    
    pygame.display.flip()

pygame.quit()
