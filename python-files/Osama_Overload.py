import pygame as pg
import sys
import os
import time
import random
import math
import subprocess
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
pg.init()
pg.mixer.init()
pg.mixer.set_num_channels(10)
#screen
width = 1280
height = 720
screen = pg.display.set_mode((width,height))
pg.display.set_caption("Osama Overload")

screen_width = screen.get_width()
screen_height = screen.get_height()


#the clock

clock = pg.time.Clock()

#score
score = 0  #score now
#GAME
mute = False

###special assets##
no_image = pg.Surface((1, 1), pg.SRCALPHA)
#bullets blueprint 
bullet_width = 10
bullet_height = 20
bullet_speed = 800
bullets = []
bullet_cooldown = 0.1
last_shot = 0
can_shoot = True
bullet_img = pg.image.load('bullet.png').convert_alpha()
bullet_img = pg.transform.scale(bullet_img, (bullet_width,bullet_height))

#dash
dash_cooldown = 2
dash_power = 2000
dash_duration = 0.1
dash_time = 0
last_dash = 0

#enemy part




keys = None
#input part
def inputs():
    keys = pg.key.get_pressed()
    return keys

#player's things
player_x = random.randint(30,screen.get_width())
player_y = 300
player_width,player_height = 50,70
pixle_speed = 400

gravity = 15
jump_strength = -6
player_Vy = 0
player_rect = pg.Rect(player_x,player_y,player_width,player_height)
player_direction = 0
is_jumping = True

#player idle stand
player_idle_images = []
for i in range (1,3):
    player_idle_image_path = f'player/idle/idle_{i}.png'
    player_idle_image = pg.image.load(player_idle_image_path).convert_alpha()
    player_idle_image = pg.transform.scale(player_idle_image,(player_width,player_height))
    player_idle_images.append(player_idle_image)
    


player_running_images_left = []
player_running_images_right = []
for i in range (12):
    player_running_image_path = f'player/running/running_{i:02}.png'
    player_running_image = pg.image.load(player_running_image_path).convert_alpha()
    player_running_image_left = pg.transform.scale(player_running_image,(player_width,player_height))

    player_running_image_right = pg.transform.flip(player_running_image,True,False)
    player_running_image_right = pg.transform.scale(player_running_image_right,(player_width,player_height))
    player_running_images_left.append(player_running_image_left)
    player_running_images_right.append(player_running_image_right)




class Player:
    def __init__(self):
        self.player = pg.image.load('player.png').convert_alpha()
        self.player = pg.transform.scale(self.player, (player_width,player_height))
        self.idle_img_frame = 0
        self.running_img_frame = 0
        self.player_rect = player_rect
        self.is_moving = False 
         
    def move_player(self,keys):
        global player_direction,game_over
        self.is_moving = False

        speed = pixle_speed*dt
        if keys[pg.K_LEFT]:
            self.player_rect.x -= speed
            self.is_moving = True
            player_direction = -1

        if keys[pg.K_RIGHT]:
            self.player_rect.x += speed
            self.is_moving = True
            player_direction = 1

        if keys[pg.K_UP]:
            self.player_rect.y -= speed
        if keys[pg.K_DOWN]:
            self.player_rect.y += speed

        if player.player_rect.y >= screen_height - player.player_rect.height:
            game_over = True #fall over
        
#jumping part
    def jump_player(self,keys,player_Vy,is_jumping):
        if keys[pg.K_SPACE] and is_jumping:
            player_Vy = jump_strength
            is_jumping = False
            self.is_moving = True
        return player_Vy,is_jumping
        
    def idle_animation(self,screen):
        if not self.is_moving:
            self.idle_img_frame += 0.03
            self.current_idle_img_frame = int(self.idle_img_frame)
            if self.current_idle_img_frame < len(player_idle_images):
                screen.blit(player_idle_images[self.current_idle_img_frame],self.player_rect)
                self.current_image = player_idle_images[self.current_idle_img_frame]
                self.player_mask = pg.mask.from_surface(self.current_image)
            else:
                self.idle_img_frame = 0
                screen.blit(self.player,self.player_rect)

    def running_animation(self,screen):
        
        if self.is_moving:
            self.running_img_frame += 0.4
            self.current_running_frame = int(self.running_img_frame)
            if self.current_running_frame < 11:
                if player_direction == -1:
                    screen.blit(player_running_images_right[self.current_running_frame],self.player_rect)
                    self.current_image= player_running_images_right[self.current_running_frame]
                    self.player_mask = pg.mask.from_surface(self.current_image)
               
                if player_direction == 1:
                    screen.blit(player_running_images_left[self.current_running_frame],self.player_rect)
                    self.current_image = player_running_images_left[self.current_running_frame]
                    self.player_mask = pg.mask.from_surface(self.current_image)
            else:
                self.running_img_frame = 0
                if player_direction == -1:
                    screen.blit(player_running_images_right[0],self.player_rect)
                if player_direction == 1:
                    screen.blit(player_running_images_left[0],player_rect)

    def draw_player(self,screen):
        player.idle_animation(screen)
        player.running_animation(screen)

player = Player()



#platform part
ground_img = pg.image.load('visuals/platform/ground_block.png')

blocks = []
platform_y = 500
block_height = 50

#onground_explosion animation:
ground_explosion_size = (100,100)
ground_explosion_images = []
for i in range (1,10):
    ground_explosion_img_path = f'visuals\ground_destruction\ground_{i}.png'
    ground_explosion_img = pg.image.load(ground_explosion_img_path)
    ground_explosion_img = pg.transform.scale(ground_explosion_img,ground_explosion_size)
    ground_explosion_images.append(ground_explosion_img)



class Platform:
    def __init__(self):
        self.block_y = platform_y
        self.block_count = 40
        self.block_width = screen.get_width() /self.block_count
        self.ground_scaled_img = pg.transform.scale(ground_img, (self.block_width,block_height))
        for i in range(self.block_count):
            x = i*self.block_width
            blocks.append(pg.Rect(x,self.block_y,self.block_width,block_height))
        self.on_ground_explosion = pg.mixer.Sound('sounds/explosion/ground_explosion.mp3')
        self.on_ground_explosion.set_volume(0.3)
        
        self.explosion_frame = 0
    def on_platform(self,player_Vy):
        global is_jumping,game_over
        
        for block in blocks:
            if player_rect.colliderect(block) and player_Vy > 0:
                player_rect.bottom = block.top
                is_jumping = True
                player_Vy = 0
        return player_Vy
    def check_bomb_collision(self,bombs,dt):
        for bomb in bombs[:]:  # iterate over a copy so we can safely remove
            if bomb.hit:
                bomb.explosion_timer -= dt
                
                #bomb.explosion_frame = 0
                
                bomb.explosion_frame += 0.3
                bomb.explosion_frame_num = int(bomb.explosion_frame) 
                
                if bomb.explosion_frame_num < len(ground_explosion_images):
                    bomb.explosion_frame_num = int(bomb.explosion_frame) 
                    bomb.image = ground_explosion_images[bomb.explosion_frame_num]
                    
                    
                else:
                    bomb.explosion_frame_num = 0
                    bomb.explosion_frame = 0
              

            
                if bomb.explosion_timer <= 0:
                    bombs.remove(bomb)
                continue
                  # skip collision check if already hit

            for block in blocks[:]:
                if bomb.rect.colliderect(block) and bomb.rect.bottom <= block.top + 5:     
                    bomb.rect.y = platform_y - 2*block_height
                    bomb.rect.x = block.centerx - bomb.rect.width // 2
                    bomb.hit = True
                    screen_shake.apply_shake(0.3,10)
                    bomb.explosion_timer = 0.3 
                    if not mute:
                        channel = pg.mixer.find_channel()
                        if channel:
                            self.on_ground_explosion.play()
                    blocks.remove(block)
                    break


    def respawn_blocks(self):
        blocks.clear()
        for i in range(self.block_count):
            x = i*self.block_width
            blocks.append(pg.Rect(x,self.block_y,self.block_width,block_height))
            
    def draw_blocks(self,surface):
        for block in blocks:
            surface.blit(self.ground_scaled_img,block)



platform = Platform()

#airplane things


airplane_enemy_max_speed = 100
airplane_enemy_min_speed = 200

airplane_enemy_directory = "enemies/airplanes"
airplane_image = [f for f in os.listdir(airplane_enemy_directory) if f.endswith('.png') or f.endswith('.jpg')]





plane_types = {
    "kamikaze": "kamikaze",
    "stealth" : "stealth",
    "trump"   : "trump"
}
special_enemy_keywords = [key.lower() for key in plane_types.keys()]
airplane_image_objects = []
airplane_image_cache = {}

normal_image_objects = []
special_image_objects = []

for fname in airplane_image:
    key = fname.lower()
    img = pg.image.load(os.path.join(airplane_enemy_directory, fname)).convert_alpha()
    img = pg.transform.scale(img, (80,40))
    airplane_image_cache[key] = img

    if any(keyword in key for keyword in special_enemy_keywords):
        special_image_objects.append((key, img))
    else:
        normal_image_objects.append((key, img))
    

#bomb part for airplanes
bomb_directory = "enemies/airplanes/bombs"
bomb_images = [f for f in os.listdir(bomb_directory) if f.endswith('png') or f.endswith('.jpg')]
bombs = []
bomb_storage = []

#explosion part
explosion_directory = 'enemies/destruction'
#mid_air_explosion_img = pg.transform.scale(pg.image.load('enemies/destruction/mid_air_explosion/mid_air_explosion.png').convert_alpha(),(80,60))
mid_air_explosion_images = []
for i in range (1,8):
    mid_air_explosion_path = f"enemies/destruction/mid_air_explosion/explosion_{i}.PNG"
    mid_air_explosion_img = pg.image.load(mid_air_explosion_path).convert_alpha()
    mid_air_explosion_img = pg.transform.scale(mid_air_explosion_img,(80,60))
    mid_air_explosion_images.append(mid_air_explosion_img)

ground_explosion_img = pg.transform.scale(pg.image.load('enemies/destruction/ground_explosion.png').convert_alpha(),(60,90))




class BaseAirplaneEnemy:
    def __init__(self):
        self.airplane_enemy_max_speed = 400
        self.airplane_enemy_min_speed = 100
        self.y = random.randint(0,100)
        self.speed = random.randint(self.airplane_enemy_min_speed, self.airplane_enemy_max_speed)
        self.can_drop_bombs = random.choice([True,False,True])
        self.bomb_start_time = 0  
        self.bomb_drop_interval = random.uniform(1,3)
        self.type = 'normal'
        self.explosion_timer = 0.2
        filename,self.image = random.choice(normal_image_objects)
        self.is_exploding = False
       # self.mid_air_explosion_img = mid_air_explosion_img
        self.on_air_explosion_played = False
        self.on_air_explosion = pg.mixer.Sound('sounds/explosion/explosion.wav')
        self.on_air_explosion.set_volume(0.3)
        self.explosion_image = 0
        #flip they way
        self.flip_choice = random.choice([True,False]) 
        if self.flip_choice:
            self.image = pg.transform.flip(self.image, True,False)
            self.speed *= -1  #starts from right side and goes to left
            self.x = screen.get_width() + self.image.get_width() 
            
        else:
            self.x = 0 - self.image.get_width() # starts from left side and goes to right
            
        self.rect = self.image.get_rect(topleft = (self.x,self.y))

    def move(self,dt):
        
        if self.is_exploding:
            self.explosion_image += 0.3
            explosion_number = int(self.explosion_image)
            if self.explosion_image < len(mid_air_explosion_images):
                self.image = mid_air_explosion_images[explosion_number]
            else:
                self.explosion_image = 0
            self.explosion_timer -=dt
            if not self.on_air_explosion_played:
                if not mute:
                    self.on_air_explosion.play()
                self.on_air_explosion_played = True

            if self.explosion_timer <= 0:
                    air_enemies.remove(self)
            return
        self.rect.x += self.speed*dt
        if not self.flip_choice and self.rect.left > screen.get_width():
            air_enemies.remove(self)
            
        elif self.flip_choice and self.rect.right < 0:
            air_enemies.remove(self)
            

    def drop_bomb(self,dt):
        
        if not self.can_drop_bombs:
            return
        self.bomb_start_time += dt

        if self.bomb_start_time >= self.bomb_drop_interval:
            bomb_x = self.rect.centerx
            bomb_y = self.rect.centery
            bomb = bomb_spawn(bomb_x,bomb_y)
            bombs.append(bomb)
            self.bomb_start_time = 0
            self.bomb_drop_interval = random.uniform(1,2)
            
    def make_hp(self,dt):
        pass

    def draw(self,sky):
        sky.blit(self.image,self.rect)

kamikaze_image = pg.image.load('enemies/airplanes/Kamikaze_airplane.png').convert_alpha()
kamikaze_image = pg.transform.scale(kamikaze_image, (80,60))
kamekaze_bomb_image = pg.image.load('enemies/airplanes/bombs/special_bombs/kamikaze_bomb.png').convert_alpha()
kamekaze_bomb_image = pg.transform.scale(kamekaze_bomb_image, (40, 60))
class kamikazePlane(BaseAirplaneEnemy):
    def __init__(self):
        super().__init__()

        self.type = 'kamikaze'
        self.can_drop_bombs = True
        self.image = kamikaze_image
        self.bomb_image = kamekaze_bomb_image
        self.speed = max(self.speed*0.3,50)

        if self.flip_choice:
            self.image = pg.transform.flip(self.image, True, False)
            self.speed *= -1  #starts from right side and goes to left
            self.x = screen.get_width() + self.image.get_width() 
        
    def drop_bomb(self,dt):
        if not self.can_drop_bombs:
            return
        
        self.bomb_start_time += dt

        if self.bomb_start_time >= self.bomb_drop_interval:
            bomb_x = self.rect.centerx
            bomb_y = self.rect.centery
            bomb = bomb_spawn(bomb_x,bomb_y, image=self.bomb_image)
            bombs.append(bomb)
            self.bomb_start_time = 0
            self.bomb_drop_interval = random.uniform(0.3,1)


stealth_width = 60
stealth_height = 60
stealth_image = pg.image.load('enemies/airplanes/stealth_airplane.png').convert_alpha()
stealth_image = pg.transform.scale(stealth_image,(stealth_width,stealth_height))



class StealthPlane(BaseAirplaneEnemy):
    def __init__(self):
        super().__init__()
        self.type = "stealth"
        self.can_drop_bombs = False
        self.image = stealth_image
        self.rect = self.image.get_rect()
        self.speed = max(self.speed*0.4,250)
        self.stealth_mask = pg.mask.from_surface(stealth_image)
        self.rect.x = random.randint(100,screen_width)
        self.rect.y = 0 - stealth_height 
        
        if self.flip_choice:
            self.image = pg.transform.flip(self.image, True, False)
            self.stealth_mask = pg.mask.from_surface(self.image)
            self.speed *= -1  #starts from right side and goes to left 
            self.rect.x = screen.get_width() + self.image.get_width()

        self.player = player_rect
        self.dx = self.player.x - self.rect.x
        self.dy = self.player.y - self.rect.y

        self.angle_rad = math.atan2(-self.dy,self.dx)
        self.angle = math.degrees(self.angle_rad)

        self.image = pg.transform.rotate(self.image,self.angle)
        self.stealth_mask = pg.mask.from_surface(self.image)

        self.sound = pg.mixer.Sound('sounds/stealth_plane/stealth_plane.mp3')
        self.sound.set_volume(0.7)
        self.sound_played = False    


    def move(self, dt):
        global game_over

        if self.is_exploding:
            self.explosion_image += 0.3
            explosion_number = int(self.explosion_image)
            if self.explosion_image < len(mid_air_explosion_images):
                self.image = mid_air_explosion_images[explosion_number]
            self.explosion_timer -= dt
            if not self.on_air_explosion_played:
                if not mute:
                    self.on_air_explosion.play()
                self.on_air_explosion_played = True
            if self.explosion_timer <= 0:
                if self in air_enemies:
                    air_enemies.remove(self)
                self.sound.stop()
                self.sound_played = False
            return  # don't process anything else during explosion

        self.rect.x += round(0.005 * self.dx * self.speed * dt)
        self.rect.y += round(0.005 * self.dy * self.speed * dt)

        if not mute and not self.sound_played:
            self.sound.play()    
            self.sound_played = True
        if self.rect.y > screen_height or self.rect.x > screen_width:
            air_enemies.remove(self)
            self.sound.stop()
            self.sound_played = False

        self.offset_x = self.rect.x - player.player_rect.x
        self.offset_y = self.rect.y - player.player_rect.y

        if self.rect.colliderect(player_rect):
            if self.stealth_mask.overlap(player.player_mask, (self.offset_x, self.offset_y)):
                game_over = True
                if self in air_enemies:
                    air_enemies.remove(self)
                    self.sound.stop()
                    self.sound_played = False




trump_plane_height = 60
trump_plane_width= 80
trump_image = pg.image.load('enemies/airplanes/trump_airplane.png').convert_alpha()
trump_image = pg.transform.scale(trump_image,(trump_plane_width,trump_plane_height))

hp_img = pg.image.load('enemies/airplanes/bombs/special_bombs/hp_up.png').convert_alpha()
hp_img = pg.transform.scale(hp_img,(40,40))


drops = []

class TrumpPlane(BaseAirplaneEnemy):
    def __init__(self):
        super().__init__()
        self.type = "trump"
        self.image = trump_image
        self.rect = self.image.get_rect()
        self.can_drop_help = True
        self.speed = random.uniform(100,250)
  
        self.drop = hp_img
        self.drop_sound = pg.mixer.Sound('sounds/hp_up/hp_up.wav')
        self.drop_sound.set_volume(0.4)
        self.drop_interval = random.uniform(1,6)
        self.drop_rect = self.drop.get_rect()
        self.last_drop_time = 0

        self.drop_active = False

        self.ready_to_drop = False

        self.can_drop_bombs = False

        self.hp_up_played = False

        self.rect.y = random.randint(0,100)
        self.x = 0 - self.image.get_width()
        if self.flip_choice:
            self.image = pg.transform.flip(self.image, True, False)
            self.speed *= -1  #starts from right side and goes to left
            self.x = screen.get_width() + self.image.get_width()
            self.rect.x = self.x

        self.explosion_image = 0
    def make_hp(self,dt):
        if self.ready_to_drop:
            drop = {
                "image": hp_img,
                "rect" : hp_img.get_rect(center=self.rect.center),
                "speed": 100,
                "owner": self
            }   
            drops.append(drop)

            
            self.drop_active = True
            self.ready_to_drop = False

    def drop_hp(self,dt):
        if self.drop_active:    
            for drop in drops[:]:
                if drop.get('owner') == self:
                    drop['rect'].y += drop['speed']*dt

                if player.player_rect.colliderect(drop["rect"]):
                    drops.remove(drop)
                    if self in air_enemies:
                        air_enemies.remove(self)
                 
                    self.drop_active = False
                    if not self.hp_up_played and not mute:
                        self.drop_sound.play()
                        self.hp_up_played = True
                    platform.respawn_blocks()

    def move(self,dt):
            if self.is_exploding:
                if not self.drop_active and not self.ready_to_drop:
                    self.ready_to_drop = True
                    self.make_hp(dt)

                self.explosion_timer -=dt
                self.explosion_image += 0.3
                explosion_number = int(self.explosion_image)
                if self.explosion_image < len(mid_air_explosion_images):
                    self.image = mid_air_explosion_images[explosion_number]
                    
                else:
                    self.explosion_image = 0
                    explosion_number = 0

                if not self.on_air_explosion_played:
                    if not mute:
                        self.on_air_explosion.play()
                    self.on_air_explosion_played = True

                if self.explosion_timer <= 0:
                    self.image = pg.Surface((1, 1), pg.SRCALPHA)
                    self.is_exploding = False
                    

                if not self.drop_active:
                    air_enemies.remove(self)
                   

            if self.drop_active:
                self.drop_hp(dt)

                for drop in drops[:]:
                    if drop["rect"].top > screen_height:
                        drops.remove(drop)
                        
                        self.drop_active = False

            self.rect.x += self.speed*dt

            if not self.flip_choice and self.rect.left > screen.get_width():
                if not self.drop_active:
                    if self in air_enemies:
                        air_enemies.remove(self)
                
                
            elif self.flip_choice and self.rect.right < 0:
                if not self.drop_active:
                    if self in air_enemies:
                        air_enemies.remove(self)
                


    def draw(self,sky):
        for drop in drops:
            if drop.get('owner') == self: 
                sky.blit(drop['image'], drop['rect'])
        sky.blit(self.image,self.rect)
        
enemy_powers = {
    "normal": {
        "class":BaseAirplaneEnemy,
        "spawn_rate":1
    },
    "kamikaze":{
        "class":kamikazePlane,
        "spawn_rate": 0.3
    },
    "stealth":{
        "class": StealthPlane,
        'spawn_rate': 0.1
    },
    "trump":{
        "class": TrumpPlane,
        "spawn_rate":0.1
    }
}

def  spawn_wave_airplanes():
        enemy_power = [data["class"] for data in enemy_powers.values()]
        spawn_rate = [data['spawn_rate'] for data in enemy_powers.values()]

        for _ in range(random.randint(5,10)):
            enemy_class = random.choices(enemy_power,weights = spawn_rate, k=1) [0] 
            air_enemies.append(enemy_class())

air_enemies = []
   
for bomb in bomb_images:
    image = pg.image.load(os.path.join(bomb_directory,bomb)).convert_alpha()
    image = pg.transform.scale(image,(40,60))
    bomb_storage.append(image)

class bomb_spawn:
    def __init__(self,x,y,image=None):
        self.image = image if image is not None else random.choice(bomb_storage)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(midtop = (x,y))
        self.speed = 100
        self.hit = False
        self.explosion_timer = 0
        self.bomb_mask = pg.mask.from_surface(self.image)
        self.explosion_frame = 0
    def move(self,dt):
        if not self.hit: 
            self.rect.y += self.speed*dt

    def bomb_collision(self):
        global game_over
        if self.rect.colliderect(player.player_rect):
            self.offset = (self.rect.x - player.player_rect.x, self.rect.y - player.player_rect.y)
            if self.bomb_mask.overlap(player.player_mask, self.offset):
                #print('get bombed')
                game_over = True #bomb over
                pass

    def draw(self,surface):
        surface.blit(self.image,self.rect)
        



def update_bombs(dt,surface):
    platform.check_bomb_collision(bombs,dt)
    for bomb in bombs[:]:
        bomb.move(dt)
        bomb.draw(surface)
        bomb.bomb_collision()
        if bomb.rect.y > screen.get_height():
            bombs.remove(bomb)

tank_warehouse = []
chosen_tank = []
tank_width = 200
tank_height = 70

tank_directory = 'enemies/tanks' 
tank_img_names = [f for f in os.listdir(tank_directory) if f.endswith(('jpg','png'))]

for tank_name in tank_img_names:

    tank_img = os.path.join(tank_directory,tank_name) 
    tank_img = pg.image.load(tank_img).convert_alpha()
    tank_img = pg.transform.scale(tank_img,(tank_width,tank_height))

    tank_warehouse.append(tank_img)

tank_smoke_images_right= []
tank_smoke_images_left= []

tank_smoke_width = 70
tank_smoke_height = 70
for i in range(1,6):
    tank_smoke_image_path = f'enemies/tanks/ground_impact/effect_{i}.png'
    

    tank_smoke_image = pg.image.load(tank_smoke_image_path).convert_alpha()
    tank_smoke_image = pg.transform.scale(tank_smoke_image,(tank_smoke_width,tank_smoke_height))
   
    tank_smoke_images_right.append(tank_smoke_image)
    tank_smoke_images_left.append(pg.transform.flip(tank_smoke_image, True,False))



last_tank_spawn = 0
class Tank:
    def __init__(self,player_rect):
        global tank_img
        self.base_img = random.choice(tank_warehouse)
        self.tank = self.base_img
        self.tank_y = 0 - tank_height
        self.tank_x = player_rect.centerx - tank_width/2
        self.tank_position = self.tank.get_rect(topleft=(self.tank_x,self.tank_y))
        self.wait_on_ground = 0
        self.speed = 200
        self.direction = None
        self.gravity = 15
        self.smoke_frame = 0
        self.current_smoke_frame = 0
        self.on_ground = False
        self.smoke_images = tank_smoke_images_right
        self.tank_mask = pg.mask.from_surface(self.tank)
        chosen_tank.append(self)
        
        #shake
        self.shake = False

        ##sounds
        self.falling_sound_played = False
        self.falling_sound = pg.mixer.Sound('sounds/tank/falling.wav')
        self.falling_sound.set_volume(0.25)

        self.falling_sound_channel = pg.mixer.find_channel()
       

        self.landing_sound_played = False
        self.landing_sound = pg.mixer.Sound('sounds/tank/landing.wav')
        self.landing_sound.set_volume(0.5)

        self.tank_moving_sound_played = False
        self.tank_moving = pg.mixer.Sound('sounds/tank/tank_moving.mp3')
        
        self.tank_moving.set_volume(0.15)

    def drop_tank(self,blocks):
        self.on_ground = False 
        if not self.on_ground:
            for block in blocks:
                if self.tank_position.colliderect(block):
                    
                    if not self.shake:
                        screen_shake.apply_shake(0.1,5) ## MAKE SHAKE
                        self.shake = True
                    self.on_ground = True
                    self.gravity = 15
                    break

            if not self.on_ground:
                self.tank_position.y += min(self.gravity*0.3, 500)
                self.collision_check(player)

        if not self.on_ground and not self.falling_sound_played:
            if not mute:
                channel = pg.mixer.find_channel()
                if channel:
                    channel.play(self.falling_sound)
            self.falling_sound_played = True
            if self.tank_moving_sound_played: #
                self.tank_moving.stop()
            return
        if self.on_ground:
            self.falling_sound_played = False
            self.shake = False


    def move_tank(self,player_rect):
        if not self.on_ground:
                        
            if player_rect.x > self.tank_position.x and self.direction != 1:
                self.direction = 1
                self.smoke_images = tank_smoke_images_right
                self.tank = self.base_img
                self.tank_mask = pg.mask.from_surface(self.tank)

            elif player_rect.x < self.tank_position.x and self.direction != -1:
                self.direction = -1
                self.tank = pg.transform.flip(self.tank, True, False)
                self.tank_mask = pg.mask.from_surface(self.tank)
                self.smoke_images = tank_smoke_images_left
                
        if self.on_ground:
            self.smoke_position_right = (
            self.tank_position.right - tank_smoke_width + 50,
            self.tank_position.bottom - tank_smoke_height
            )
            self.smoke_position_left = (
            self.tank_position.left - 50,
            self.tank_position.bottom - tank_smoke_height
            )
            self.smoke_frame += 0.1

            self.wait_on_ground += 0.2


            screen_shake.apply_shake(1,2)

            if not self.landing_sound_played:
                if not mute:
                    self.landing_sound.play()
                self.falling_sound.stop()
                self.landing_sound_played = True

            if self.on_ground and not self.tank_moving_sound_played:
                if not mute:
                    self.tank_moving.play()
                self.tank_moving_sound_played = True


            self.current_smoke_frame = int(self.smoke_frame)

            if self.on_ground and self.wait_on_ground > 20:
                self.tank_position.x += self.speed*dt*self.direction

                if  self.tank_position.x > screen_width + tank_width or self.tank_position.x < -tank_width:
                    chosen_tank.remove(self)
                if self.tank_position.y > screen_height + tank_height:
                    chosen_tank.remove(self)


    def draw(self,screen):
        screen.blit(self.tank,self.tank_position)

        if self.current_smoke_frame < len(self.smoke_images) and self.on_ground:
                screen.blit(tank_smoke_images_left[self.current_smoke_frame],self.smoke_position_left)
                screen.blit(tank_smoke_images_right[self.current_smoke_frame],self.smoke_position_right)
    
    def collision_check(self,player):
        global game_over
        if self.tank_position.colliderect(player.player_rect):
            self.offset = (self.tank_position.x - player.player_rect.x , self.tank_position.y - player.player_rect.y )
            if self.tank_mask.overlap(player.player_mask,self.offset):
                game_over = True # tank_over
                pass


    def spawn_tank():
        global last_tank_spawn
        
        for tank in chosen_tank[:]:
            tank.drop_tank(blocks)
            tank.move_tank(player_rect)
            tank.collision_check(player)

# Spawn a new tank every 10 seconds
        current_time = pg.time.get_ticks() / 1000 
        if current_time - last_tank_spawn >= 10:
            chosen_tank.append(Tank(player_rect))

            last_tank_spawn = current_time

#bar stuff
bar_width = 200
bar_height = 20
fill_bar_width = 0

is_dash = False
def dash(keys):
    current_time_for_dash = pg.time.get_ticks()/1000
    global dash_time,last_dash,is_dash,fill_bar_width

    if (current_time_for_dash - last_dash) > dash_cooldown:
        is_dash = True

    if keys[pg.K_LSHIFT] and (current_time_for_dash - last_dash) > dash_cooldown and is_dash :
        dash_time = current_time_for_dash  # Start dash
        last_dash = current_time_for_dash
        is_dash = False
        fill_bar_width = 0
    
    #Dash logic: Apply dash over time (gradual motion)
    if current_time_for_dash - dash_time < dash_duration:
        player_rect.x += player_direction * dash_power * dt

#dash cooldown bar (UX)
def dash_cooldown_bar():
    
    global fill_bar_width,is_dash
    bar_x = screen.get_width() - (bar_width+10)
    bar_y = screen.get_height() - (bar_height + 10)
    fill_speed = bar_width/dash_cooldown
    pg.draw.rect(screen, (255,0,0), (bar_x,bar_y, bar_width,bar_height) )
    if not is_dash:
        fill_bar_width += fill_speed*dt
        pg.draw.rect(screen, (0,255,0), (bar_x,bar_y, fill_bar_width, bar_height))
    if is_dash:
        pg.draw.rect(screen, (0,255,0), (bar_x,bar_y, bar_width, bar_height))
    
 #shooting part   
bullets = []
gun_shot = pg.mixer.Sound("sounds/gun/gun_shot.wav")
gun_shot.set_volume(0.3)
max_bullets = 10
bullet_hit_boss_left = 0
bullet_hit_boss_right = 0
explosion_image = 0

def shooting(keys):
    global last_shot, bullet_img, score, mute, bullet_hit_boss_left, bullet_hit_boss_right,explosion_image
    
    current_time_for_shooting = pg.time.get_ticks()/1000
    
    if keys[pg.K_f] and (current_time_for_shooting - last_shot > bullet_cooldown):
        if not mute:
            gun_shot.play()
        shot_side = random.choice([True,False])

        if shot_side:
            bullet_x = player_rect.left - bullet_width
        else:
            bullet_x = player_rect.right - bullet_width

        bullet_y = player_rect.top - bullet_height
        bullet = pg.Rect(bullet_x,bullet_y,bullet_width,bullet_height)
        if len(bullets) < max_bullets:
            bullets.append((bullet_img,bullet))
        
        last_shot = current_time_for_shooting
    
    # FIXED: Use list comprehension instead of removing during iteration
    bullets_to_keep = []
    
    for bullet_data in bullets:
        bullet_img, bullet = bullet_data
        bullet.y -= bullet_speed * dt
        
        keep_bullet = True
        
        # Check if bullet is off-screen
        if bullet.y < 0:
            keep_bullet = False
        
        # Check collisions with enemies
        elif keep_bullet:
            for enemy in air_enemies[:]:
                if bullet.colliderect(enemy.rect) and not enemy.is_exploding:
                    enemy.is_exploding = True
                    score += 1
                    keep_bullet = False
                    break
        
        # Check collisions with bombs
        if keep_bullet:
            for bomb in bombs[:]:
                if bullet.colliderect(bomb.rect):
                    bomb.hit = True  # Mark bomb as hit instead of removing
                    keep_bullet = False
                    break
        
        # Check boss collisions
        if keep_bullet and boss.boss_active:
            if bullet.colliderect(boss.hit_left):
                bullet_hit_boss_left += 1
                keep_bullet = False     
            elif bullet.colliderect(boss.hit_right):
                bullet_hit_boss_right += 1
                keep_bullet = False
        
        # Only keep bullets that shouldn't be removed
        if keep_bullet:
            screen.blit(bullet_img, bullet)
            bullets_to_keep.append(bullet_data)
    
    # Replace the entire bullets list (much faster than multiple removes)
    bullets[:] = bullets_to_keep
    
def apply_gravity(dt,player_rect,player_Vy,gravity):
    
    on_block = False

    for block in blocks:
        if player_rect.colliderect(block):
         on_block = True
         break
    if not on_block:
        player_Vy += gravity * dt
        player_rect.y += player_Vy   
    return player_Vy



def update_enemies(dt):

    for enemy in air_enemies:
        enemy.move(dt)
        enemy.drop_bomb(dt)




    if len(air_enemies) < random.randint(4,10):
        spawn_wave_airplanes()

    Tank.spawn_tank()


def update_player(keys):


      #movement and jumping        
    player.move_player(keys)
     #jumping part
    global player_Vy,is_jumping
    player_Vy, is_jumping = player.jump_player(keys,player_Vy,is_jumping)
   #dash
    dash(keys)
    
    #shooting
    shooting(keys)
    #gravity part
    player_Vy = apply_gravity(dt,player_rect,player_Vy,gravity)
   #collision with screen
    player_rect.clamp_ip(screen.get_rect())
   #collision check with platform
    player_Vy = platform.on_platform(player_Vy)

    mutebutton.update()
bg_x = 0

background_image = pg.image.load('visuals/background.jpg').convert()
background_image = pg.transform.scale(background_image,(width,height))
bg_width = background_image.get_width()

bg_tiles = math.ceil((screen_width/bg_width)+2)

font=  pg.font.Font("fonts/Pixel Game.otf", 50)

class Score_counter:
    def __init__(self):
        global score
        self.width = 300
        self.height = 200
        self.score_board = pg.image.load('score_board.png').convert_alpha()
        self.score_board = pg.transform.scale(self.score_board,(self.width,self.height))
        
        self.score_board_position = self.score_board.get_rect()
        self.score_text = font.render(str(score),True,(0,0,0))
        self.score_board_x = 0
        self.score_board_y = screen.get_height() - self.height + 20

        self.score_text_rect = self.score_text.get_rect(center=(self.score_board_x + self.width // 2 - 20, self.score_board_y + 20 +self.height // 2))
        
        self.shake_duration = 15
        self.shake_amount = 10


        self.previous_score = score

    def shake_screen(self):

        self.shake_offset_x = random.randint(-self.shake_amount,self.shake_amount)
        self.shake_offset_y = random.randint(-self.shake_amount,self.shake_amount)
        screen.blit(self.score_text, (self.score_text_rect.x + self.shake_offset_x, self.score_text_rect.y + self.shake_offset_y))
        screen.blit(self.score_board, (self.score_board_x + self.shake_offset_x, self.score_board_y + self.shake_offset_y))
        

    def draw_score(self,screen):
        self.score_text = font.render(str(score),True,(0,0,0))
        
        screen.blit(self.score_board,(self.score_board_x, self.score_board_y))
        screen.blit(self.score_text,self.score_text_rect)

score_counter = Score_counter()
### shake effect

class ScreenShake:
    def __init__(self):
        self.shakes = []  # Queue of shakes
        self.offset_x = 0
        self.offset_y = 0

    def apply_shake(self, duration, intensity):
        # Add a new shake to the queue
        self.shakes.append({
            'end_time': time.time() + duration,
            'intensity': intensity
        })

    def make(self):
        # Reset offset before calculating new shake
        total_offset_x = 0
        total_offset_y = 0   
                                #now
        # Remove shakes that have ended
        self.shakes = [shake for shake in self.shakes if time.time() < shake['end_time']]

        # Apply all active shakes (stack intensities)
        for shake in self.shakes:
            total_offset_x += random.randint(-shake['intensity'], shake['intensity'])
            total_offset_y += random.randint(-shake['intensity'], shake['intensity'])

        # Set final offset
        self.offset_x = total_offset_x
        self.offset_y = total_offset_y


screen_shake = ScreenShake()

def background():
    global bg_x
    bg_x -= 0.5

    if bg_x <= -bg_width:
        bg_x = 0
    screen_shake.make()

    for i in range(bg_tiles):
        shake_x = screen_shake.offset_x
        shake_y = screen_shake.offset_y
        screen.blit(background_image, (int((bg_width * i) + bg_x+shake_x), 0+shake_y))

#mute button
mute_button_img = pg.image.load('sounds/mute.png')
mute_button_img = pg.transform.scale(mute_button_img,(50,50))

unmute_button_img = pg.image.load('sounds/unmute.png')
unmute_button_img = pg.transform.scale(unmute_button_img,(50,50))

clicked = False

class MuteButton:
    def __init__(self):
        
        self.clicked = False
        self.button_rect = mute_button_img.get_rect()
        self.x = screen_width // 2
        self.y = screen_height - mute_button_img.get_width()
        self.button_image = unmute_button_img
        self.button_rect.x = self.x
        self.button_rect.y = self.y
        self.button_image = mute_button_img if mute else unmute_button_img
    def update(self):
        global mute
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_clicked = pg.mouse.get_pressed()

        if self.button_rect.collidepoint(self.mouse_pos):
            if self.mouse_clicked[0] and not self.clicked:  # Only process click once
                if not mute:  # If currently unmuted, mute it
                    print('mute')
                    mute = True
                    self.clicked = True  # Set clicked to True to prevent repeat clicks
                    self.button_image = mute_button_img
                    pg.mixer.stop()
                else:  # If currently muted, unmute it
                    print('unmute')
                    mute = False
                    self.clicked = True  # Set clicked to True to prevent repeat clicks
                    self.button_image = unmute_button_img
                    pg.mixer.unpause()
        if not self.mouse_clicked[0]:
            self.clicked = False



    def draw(self,screen):
        screen.blit(self.button_image, (self.button_rect.x, self.button_rect.y))
        self.update()


mutebutton = MuteButton()


fps_on = False
fps_key_pressed = False
def fps(keys):
    global fps_on,fps_key_pressed
    
    if keys[pg.K_p] and not fps_on and not fps_key_pressed:
        fps_on = True
        fps_key_pressed = True
    elif keys[pg.K_p] and fps_on and fps_key_pressed:
        fps_on = False
        fps_key_pressed = False
    if fps_on:
        fps_font=  pg.font.Font("fonts/Pixel Game.otf", 30)
        fps = str(int(clock.get_fps()))
        fps_text = fps_font.render(f"FPS: {fps}", True, "black")
        screen.blit(fps_text, (10, 10))

restart_button_size = (200,100)

restart_button_img = pg.image.load("menu/restart.png")
restart_button_img = pg.transform.scale(restart_button_img,restart_button_size)

restart_button_2_img = pg.image.load("menu/restart_2.png")
restart_button_2_img = pg.transform.scale(restart_button_2_img,restart_button_size)

class RestartButton():
    def __init__(self):
        self.default = restart_button_img
        self.hover = restart_button_2_img
        self.image = self.default
        self.rect = self.image.get_rect()
        self.x = self.rect.x
        self.y = self.rect.y
        self.clicked = False

    def make_button(self):
        self.mouse_pos = pg.mouse.get_pos()
        self.mouse_clicked = pg.mouse.get_pressed()

        self.y = screen_height - 200
        self.x = 0 + self.image.get_width()/2 + 30

        self.pos = self.x,self.y
        self.rect.x, self.rect.y = self.pos

        if self.rect.collidepoint(self.mouse_pos):
            self.image = restart_button_2_img
            if self.mouse_clicked[0] and not self.clicked:
                self.restart_game()
                self.clicked = True
        else:
            self.image = restart_button_img

    def restart_game(self):
    # Check if running from .exe or .py
        if getattr(sys, 'frozen', False):
            # If running as .exe, use the current path
            exe_path = sys.executable
        else:
            # If running as .py, use this script's path and convert to .exe
            exe_path = os.path.abspath(__file__).replace(".py", ".exe")

        try:
            # Run the exe, this should restart the game properly now
            subprocess.Popen([exe_path])
            sys.exit()
        except Exception as e:
            print(f"Error restarting game: {e}")

    def make(self):
        
        max_width = max(self.default.get_width(), self.hover.get_width())
        max_height = max(self.default.get_height(), self.hover.get_height())

        clear_rect = pg.Rect(self.x - 5, self.y - 5, max_width + 10, max_height + 10)
        pg.draw.rect(screen, (0, 0, 0), clear_rect)
        self.make_button()
        screen.blit(self.image,self.pos)

restart_button = RestartButton()





play_btn_width,play_btn_height = 200,100
help_btn_size = (200,100)
help_screen_size = (screen_width,screen_height)

play_button = pg.image.load('menu/play.png')
play_button = pg.transform.scale(play_button,(play_btn_width,play_btn_height))

play_button_2 = pg.image.load('menu/play_2.png')
play_button_2 = pg.transform.scale(play_button_2,(play_btn_width,play_btn_height))

help_btn = pg.image.load('menu/help.png')
help_btn = pg.transform.scale(help_btn,help_btn_size)

help_btn_2 = pg.image.load('menu/help_2.png')
help_btn_2 = pg.transform.scale(help_btn_2,help_btn_size)

help_screen = pg.image.load('menu/help_screen.png')
help_screen = pg.transform.scale(help_screen,help_screen_size)

back_btn_size = (150,100)

back_btn = pg.image.load('menu/back.png')
back_btn = pg.transform.scale(back_btn,back_btn_size)

back_btn_2 = pg.image.load('menu/back_2.png')
back_btn_2 = pg.transform.scale(back_btn_2,back_btn_size)

game_on = False # game on now


class Menu:
    def __init__(self):
        
        self.play_btn = play_button


        self.hover = pg.mixer.Sound('sounds/menu/hover.mp3')


        self.hover_played_play = False
        self.hover_played_help = False
        self.hover_played_back = False

        self.hover.set_volume(0.6)


        self.button_pressed = False
        self.help_pressed = False
        self.in_help = False
        self.play_rect = self.play_btn.get_rect(center=(screen_width/2, screen_height/2))
        self.menu_btn_sound = pg.mixer.Sound('sounds\menu\play_pressed.wav')

        self.help_btn = help_btn
        self.help_rect = self.help_btn.get_rect(center=(self.play_rect.centerx, (50+ self.play_rect.bottom)))

        self.back_clicked = False

        self.in_menu = 1

    def click_play(self):
        global game_on
        if not game_on and self.in_menu == 1:
            self.mouse_pos = pg.mouse.get_pos()
            self.mouse_clicked = pg.mouse.get_pressed()

            if self.play_rect.collidepoint(self.mouse_pos):
                if not self.hover_played_play and not mute:
                    self.hover.play()
                    self.hover_played_play = True
                self.play_btn = play_button_2

                if self.mouse_clicked[0] and not self.button_pressed:
                    self.button_pressed = True
                    if not mute:
                        self.menu_btn_sound.play()
                    game_on = True
            else:
                self.play_btn = play_button
              
                self.hover_played_play = False
        screen.blit(self.play_btn,self.play_rect) 
    
    def click_help(self):
        global game_on
        if not game_on and self.in_menu == 1:
            if self.help_rect.collidepoint(self.mouse_pos):
                self.help_btn = help_btn_2
                if not self.hover_played_help and not mute:
                    self.hover.play()
                    self.hover_played_help = True

                if self.mouse_clicked[0] and not self.help_pressed:
                    self.help_pressed = True
                    print('help')
                    self.in_help = True
                    self.in_menu = 2
                    self.show_help()
                    if not mute:
                        self.menu_btn_sound.play()
            else:
                self.help_btn = help_btn
                self.help_pressed = False
                self.hover_played_help = False
        screen.blit(self.help_btn,self.help_rect)

    def show_help(self):
        if self.in_menu == 2:
            self.mouse_pos = pg.mouse.get_pos()
            self.mouse_clicked = pg.mouse.get_pressed()
            self.help_btn = no_image
            self.play_btn = no_image
            self.help_screen = help_screen

        
            self.back_btn = back_btn
            self.back_rect = self.back_btn.get_rect()

            if self.back_rect.collidepoint(self.mouse_pos):
                if not self.hover_played_back and not mute:
                    self.hover.play()
                    self.hover_played_back = True

                self.back_btn = back_btn_2
                if self.mouse_clicked[0] and not self.back_clicked:
                    print('back')
                    self.back_clicked = True
                    if not mute:
                        self.menu_btn_sound.play()
                    self.in_menu = 1
            else:
                self.back_btn = back_btn
                self.back_clicked = False
                self.hover_played_back = False
            screen.blit(self.help_screen,(0,0))
            screen.blit(self.back_btn, (5,10))

            self.help_text = [
                    ("Made by:", (255, 255, 255)),  # White
                    ("Apurbo Da Vinci", (255, 215, 0)), # gold
                    ("Use A to go left and D to go right", (0,0,0)),  # black
                    ("Press Space to jump and Shift to dash", (0,0,0)),
                    ("dash is usefull for dodging tanks :D", (0,0,128)), #navy
                    ("Press F to shoot bullets and destroy planes and missiles", (192,192,192)),  # silver
                    ("Trump plane will give you an Osama head", (0,128,128)),  # green
                    ("Which will repair your platform", (0,128,0)),  # green
                    ("Reach 500 score to fight the final boss", (25,25,112)),
                    ("Pro tip: don't die :)", (255, 0, 0)),  # Red

                ]
            text_y_offset = 100
            text_x_offset = 100
            for line,color in self.help_text:
                self.help_text_surface = font.render(line, True, color)
                screen.blit(self.help_text_surface,(text_x_offset,text_y_offset))
                text_y_offset += 30

                if line == "Apurbo Da Vinci":
                    text_y_offset += 30

    def draw(self):
        self.click_play()
        self.click_help()
        self.show_help()

menu = Menu()

## boss 
boss_offset = 100 # one tower has a bigger height, this fixes the issue 

boss_width_right = 100
boss_height_right = 200
boss_width_left = boss_width_right
boss_height_left = boss_height_right + boss_offset

boss_img_right = pg.image.load("boss/boss_right.png").convert_alpha()
boss_img_right = pg.transform.scale(boss_img_right, (boss_width_right,boss_height_right))
boss_img_left = pg.image.load('boss/boss_left.png').convert_alpha()
boss_img_left = pg.transform.scale(boss_img_left, (boss_width_left,boss_height_left))        


boss_img_left_destroyed = pg.image.load('boss/destroyed_left.png')
boss_img_left_destroyed = pg.transform.scale(boss_img_left_destroyed, (boss_width_left,boss_height_left)) 

boss_img_right_destroyed = pg.image.load('boss/destroyed_right.png')
boss_img_right_destroyed = pg.transform.scale(boss_img_right_destroyed, (boss_width_right,boss_height_right)) 

life_image = pg.image.load("boss/life.png")
life_image = pg.transform.scale(life_image,(40,40))


#boss ammo#

boss_dead = False

ammos = []
for i in range(1,10):
    ammo_path = f"boss/ammo/airplane ({i}).png"
    ammo = pg.image.load(ammo_path).convert_alpha()
    ammo = pg.transform.scale(ammo,(100,70))
    ammos.append(ammo)

class Boss:
    def __init__(self):
        global boss_offset

        self.rand_move = random.choice([-1,1])
        self.life_gone = 0
        self.image_left = boss_img_left
        self.image_right = boss_img_right
        self.distance = 200
        self.x = 300 ## change this for the position
        self.x_right = self.x + self.distance
        self.y =  -boss_height_left
        self.y_left  = self.y - boss_offset
        self.hit_left = self.image_left.get_rect()
        self.hit_right = self.image_right.get_rect()
        self.speed = 400
        self.rand_move_y = random.choice([-1,1])

        self.active_planes = []
        self.life = []
        self.move_timer = 100
        self.ammo_timer = 0
        self.ammo_cooldown = random.uniform(1,3)

        self.left_active = True
        self.right_active = True

        self.phase_2 = False

        self.health_bar_width = 70
        self.new_bar_left = self.health_bar_width
        self.new_bar_right = self.health_bar_width

        
        self.shake_Death = False

        self.boss_active = False

        self.blocks_restored = False

    def spawn_boss(self):
        if not self.blocks_restored:
            platform.respawn_blocks()
            self.blocks_restored = True
        if self.y < 100:
            self.y += 4
            self.y_left  = self.y - boss_offset
        else:
            if self.left_active or self.right_active:
                self.move_boss(dt)
                self.health_bar_left()
                self.health_bar_right()
                self.boss_active = True
    def move_boss(self,dt):
        
        if random.randint(1,120) == 1:
            self.rand_move = random.choice([-1,1])


        if self.x_right + self.image_right.get_width() > screen_width or self.x < 0:
            self.rand_move *= -1

        self.x += self.speed*dt*self.rand_move
        self.x_right = self.x + self.distance

        self.hit_left.topleft = (self.x, self.y_left)
        self.hit_right.topleft = (self.x_right, self.y)
        
        self.spawn_plane(dt)
        

    def spawn_plane(self,dt):
            self.ammo_timer += dt
            if self.ammo_timer >= self.ammo_cooldown:
                self.ammo_timer = 0
                self.ammo_timer = 0


                #pick plane
                self.plane = random.choice(ammos)

                self.plane_mask = pg.mask.from_surface(self.plane)

                #install the plane
                self.plane_rect = self.plane.get_rect()
                self.plane_rect.x = (self.hit_left.x + self.hit_right.x)/ 2
                self.plane_rect.y = boss_height_left/2
                
                #rotate to player
                dx = player.player_rect.x - self.plane_rect.centerx
                dy = player.player_rect.y - self.plane_rect.centery

                hit = 0

                self.plane_sound_played = False
                self.plane_sound = pg.mixer.Sound('boss/ammo/shoot.mp3')
                self.plane_sound.set_volume(0.5)
                #final install

                plane_data = {
                    'image': self.plane,
                    'rect': self.plane_rect,
                    'timer': 0,
                    'dx': dx,
                    'dy': dy,
                    'mask': self.plane_mask,
                    'hit': hit,
                    'sound_played': self.plane_sound_played,
                    'sound': self.plane_sound
                }

                self.active_planes.append(plane_data)

    def rotate_plane(self,plane):
        dx = player.player_rect.x - plane['rect'].centerx
        dy = player.player_rect.y - plane['rect'].centery
        
        self.angle = math.atan2(-dy,dx)
        plane['image'] = pg.transform.rotate(self.plane, math.degrees(self.angle))
        plane['mask'] = pg.mask.from_surface(plane['image'])

    def move_plane(self,dt):
        for plane in self.active_planes:
            


            plane['timer'] += 1
            if plane['timer'] > self.move_timer:                
                plane['rect'].y +=  round(0.005*plane['dy']*self.speed*dt)
                plane['rect'].x +=  round(0.005*plane['dx']*self.speed*dt)
                
                if not plane['sound_played'] and not mute:
                    plane['sound'].play()
                    plane['sound_played'] = True

                if (plane['rect'].right < 0 or plane['rect'].left > screen_width or
                    plane['rect'].bottom < 0 or plane['rect'].top > screen_height):
                    self.active_planes.remove(plane)
                    plane['sound'].stop()
                    
            else:
                plane['rect'].x = (self.hit_left.x + self.hit_right.x)/ 2
                self.rotate_plane(plane)

            if plane['timer'] == self.move_timer + 1:  # ← just when it starts moving
                dx = player.player_rect.x - plane['rect'].centerx
                dy = player.player_rect.y - plane['rect'].centery
                plane['dx'] = dx
                plane['dy'] = dy
                self.angle = math.atan2(-dy,dx)
                plane['image'] = pg.transform.rotate(self.plane, math.degrees(self.angle))

            screen.blit(plane['image'],plane['rect'])
            self.check_collision_plane(plane)
            
    def check_collision_plane(self,plane):

        offset = (player.player_rect.x - plane['rect'].x, player.player_rect.y - plane['rect'].y)

        if plane['rect'].colliderect(player.player_rect):
            if plane['mask'].overlap(player.player_mask, offset) and not plane['hit']:
                
                self.life_gone += 1
                plane['hit'] = True

    def draw_life(self):
        global game_over,game_on
        self.life_pos_y = 10
        self.life_pos_x = 10
        
        num_of_life = 10 - self.life_gone ##life now

        if num_of_life <= 0:
          game_over = True
          return

        for i in range(num_of_life):
            screen.blit(life_image,(self.life_pos_x,self.life_pos_y))
            self.life_pos_x += 30
    def health_bar_left(self):

        self.bullets_will_take = 75
        self.damage_done = self.health_bar_width/self.bullets_will_take

        self.new_bar_left = (self.health_bar_width - self.damage_done*bullet_hit_boss_left)
        self.health_bar_height = 10
        outline = 4

        x = (self.x + self.image_left.get_width()/2 - (self.health_bar_width/2))
        y = (self.y_left + self.image_left.get_height()/2 + 10)

        
        outline_x = x - outline/2
        outline_y = y - outline/2

        pg.draw.rect(screen,(0,0,0),(outline_x,outline_y,self.health_bar_width+outline,self.health_bar_height+outline))

        pg.draw.rect(screen,(0,255,0),(x,y,self.new_bar_left,self.health_bar_height))

        if self.new_bar_left <= 0:
            self.image_left = boss_img_left_destroyed # DIE 
            self.left_active = False
        
    def health_bar_right(self):
        self.damage_done = self.health_bar_width/self.bullets_will_take
        self.new_bar_right = (self.health_bar_width - bullet_hit_boss_right*self.damage_done)

        outline = 4

        x = (self.x_right + self.image_right.get_width()/2 - (self.health_bar_width/2))
        y = (self.y_left + self.image_left.get_height()/2 + 10)

        
        outline_x = x - outline/2
        outline_y = y - outline/2

        pg.draw.rect(screen,(0,0,0),(outline_x,outline_y,self.health_bar_width+outline,self.health_bar_height+outline))

        pg.draw.rect(screen,(0,255,0),(x,y,self.new_bar_right,self.health_bar_height))
    
        if self.new_bar_right <= 0:
            self.image_right = None
            self.image_right = boss_img_right_destroyed
            self.right_active = False


    def activate_phase_2(self):
    
        if (self.new_bar_left + self.new_bar_right) <= (self.health_bar_width):
            if not self.phase_2:
                self.phase_2 = True
                self.move_timer = 50
                self.speed = 600
                self.ammo_cooldown = random.uniform(0.5,1)
                boss_phase_2.change_bg()
            if not (self.new_bar_left + self.new_bar_right) <= 0:
                boss_phase_2.draw()

    def make(self):
        
        screen.blit(self.image_left,(self.x,self.y_left))
        screen.blit(self.image_right, (self.x_right,self.y))


        self.spawn_boss()
        self.draw_life()

        self.move_plane(dt)

        self.activate_phase_2()

        if not self.left_active and not self.right_active:
            boss_death.make()
            if not self.shake_Death:
                screen_shake.apply_shake(10, 10)
                self.shake_Death = True

boss = Boss()

boss_is_dead = False
class Boss_death:
    def __init__(self):
        global boss_is_dead,ost
        self.explosion_image = mid_air_explosion_images[0]
        self.left = boss.hit_left
        self.right = boss.hit_right 
        self.position_left = []
        self.position_right = []
        self.offset_x = self.explosion_image.get_width() // 2
        self.offset_y = self.explosion_image.get_height() // 2
        self.frame_num = 0
        self.explosion_timer = 0
        self.boss_left = boss.hit_left
        self.boss_right = boss.hit_right

        self.death_sound = pg.mixer.Sound('boss/boss_death.wav')
        self.death_sound.set_volume(0.7)
        self.death_sound_played = False

        self.earth_quake_sound = pg.mixer.Sound('boss/earthquake.mp3')
        self.earth_quake_sound.set_volume(1.5)
        self.down_speed = 1

        
        
        
    def move_boss_down(self):
        global boss_death
        global boss_phase_2
        global boss
        global boss_dead
        ost.stop()
        if boss.hit_left.y < screen_height:
            self.boss_left.y += self.down_speed
            boss.y += self.down_speed
            boss.y_left +=self.down_speed
            for data in self.position_left:
                data['y'] += self.down_speed
            if not self.death_sound_played and not mute:
                self.death_sound.play()
                self.earth_quake_sound.play()
                self.death_sound_played = True
        else:
            print('done')
            boss_dead = True
            self.death_sound.stop()
            del boss
            del boss_death
            del boss_phase_2

        if self.boss_right.y < screen_width + self.boss_right.height:
            self.boss_right.y += self.down_speed
            for data in self.position_right:
                data['y'] += self.down_speed

        
    def make_explosions_left(self):
        height_fix = 100 # for the large thing on top of the building
        x,y = self.left.x,self.left.y+height_fix
        w,h = self.left.width,self.left.height-height_fix

        rand_x = random.randint(x, x+w)
        rand_y = random.randint(y, y+h)

        data = {
            "x": rand_x,
            "y": rand_y,
            'frame_num': 0,
            'rand_num': random.randint(0,len(mid_air_explosion_images)-1)
        }
        
        self.position_left.append(data)
       # print(self.position_left)
        self.explosion_timer = 0
        pass

    def make_explosion_right(self):
        x,y = self.right.x,self.right.y
        w,h = self.right.width,self.right.height

        rand_x = random.randint(x, x+w)
        rand_y = random.randint(y, y+h)

        self.frame_num += 1
        frame = int(self.frame_num) 
        if frame < len(mid_air_explosion_images):
           mid_air_explosion_images[frame]
        else:
            self.frame_num = 0
            frame = 0

        data_right = {
            "x": rand_x,
            "y": rand_y,
            'frame_num': 0,
            'rand_num': random.randint(0,len(mid_air_explosion_images)-1)
        }
        self.position_right.append(data_right)
       # print(self.position_left)
        self.explosion_timer = 0
    def make(self):
        self.explosion_timer += 1
        if len(self.position_left) < 70:
            if self.explosion_timer > 10:
                self.make_explosions_left()
                self.make_explosion_right()
                
        for data in self.position_left: 
            data['frame_num'] += 0.3
            frame_left = int(data['frame_num'])
            if frame_left < len(mid_air_explosion_images):
                explosion_left = mid_air_explosion_images[frame_left]
                screen.blit(explosion_left,(data['x']- self.offset_x, data['y']-self.offset_y))
            else:
                explosion_left = mid_air_explosion_images[data['rand_num']]
                screen.blit(explosion_left,(data['x']- self.offset_x, data['y']-self.offset_y))

        for data_right in self.position_right:
            data_right['frame_num'] += 0.3
            frame_right = int(data_right['frame_num'])
            if frame_right < len(mid_air_explosion_images):
                explosion_right = mid_air_explosion_images[frame_right]
                screen.blit(explosion_right,(data_right['x']- self.offset_x, data_right['y']-self.offset_y))
            else:
                explosion_right = mid_air_explosion_images[data_right['rand_num']]
                screen.blit(explosion_right,(data_right['x']- self.offset_x, data_right['y']-self.offset_y))
        self.move_boss_down()
        pass
#finishing this = done
#hmmm..change the bg to normal = NO



boss_death = Boss_death()


lighting_image_width = 50
lighting_image_height = 600
lighting_images = []
lighting_mask_images = []
boss_bg = pg.image.load('boss/bg.png').convert_alpha()
boss_bg = pg.transform.scale(boss_bg,(width,height))
for i in range (1,6):
    lighting_path = f"boss\lighting\lighting ({i}).png"
    lighting_img = pg.image.load(lighting_path).convert_alpha()
    lighting_img = pg.transform.scale(lighting_img,(lighting_image_width,lighting_image_height))
    lighting_img_mask = pg.mask.from_surface(lighting_img)
    lighting_mask_images.append(lighting_img_mask)
    lighting_images.append(lighting_img)
   

class Boss_phase_2:
    def __init__(self):
        self.image = lighting_images[0]
        self.num = 0
        self.y = 0
        self.x = random.randint(0,screen_width)
        self.timer = 0

        self.thunder = pg.mixer.Sound('boss/lighting/thunder.wav')
        self.thunder.set_volume(0.3)
        self.thunder_played = False

        self.fade_alpha = 0
        self.fade_done = False
        self.fade_surface = boss_bg.copy()

        self.block_masks = {}

        self.player_hit = False
    def make_lighting(self):
        if self.timer <= 100:
            self.timer += 1
            return
        
        self.num += 0.2
        new_num = int(self.num)
        
        if not self.thunder_played and not mute: #no play if mute
            self.thunder.play()
            self.thunder_played = True

        screen_shake.apply_shake(0.2, 10) ## shake the screen

        if new_num < len(lighting_images):
            self.image = lighting_images[new_num]
            self.mask =  lighting_mask_images[new_num]
            screen.blit(self.image,(self.x,0))
            self.collision_detect() 
        else:
            self.num = 0
            self.x = random.randint(0,screen_width)
            self.image = no_image
            self.timer = 0
            self.thunder_played = False 
        
    def change_bg(self):
        global background_image
        if self.fade_done:
            return

        self.fade_surface.set_alpha(int(self.fade_alpha))
        for i in range(bg_tiles):
            screen.blit(self.fade_surface, (int((bg_width * i) + bg_x), 0))

        self.fade_alpha += 200*dt
        if self.fade_alpha >= 255:
            background_image = boss_bg
            self.fade_done = True
            self.fade_alpha = 0

    def collision_detect(self):
        if self.num == 0 or int(self.num) >= len(lighting_images):
            return
        blocks_to_remove = []
        for block in blocks:
            block_id = id(block)  # Get unique ID of the object
            if block_id not in self.block_masks:
                self.block_masks[block_id] = pg.Mask((block.width, block.height), fill=True)
        
            offset = (block.x - self.x, block.y - self.y)
            if self.mask.overlap(self.block_masks[block_id], offset):
                blocks_to_remove.append(block)

        for block in blocks_to_remove:
            blocks.remove(block)
            block_id = id(block)
            if block_id in self.block_masks:
                del self.block_masks[block_id]

        offset_for_p = (player.player_rect.x - self.x, player.player_rect.y - self.y)
        
        if self.mask.overlap(player.player_mask,offset_for_p) and not self.player_hit:
            
            boss.life_gone += 1
            self.player_hit = True

    def draw(self):
        self.make_lighting() 
        self.change_bg()
boss_phase_2 = Boss_phase_2()
     ###making a phase 2, lighting strikes 


game_over = False

clip = VideoFileClip("binladen.mp4")

class Game_over:
    def __init__(self):
        self.image = None
        self.start_time = None
        self.sound = pg.mixer.Sound('dead.mp3')
        self.sound.set_volume(0.5)
        self.sound_channel = pg.mixer.find_channel(force=True)
        game_on = False
        self.sound_played = False
    def make_vid(self):


        
        if self.start_time is None:
            self.start_time = time.time()

        current_time = time.time() - self.start_time

        self.dead()

        if current_time >= clip.duration:
            return

        # Get the frame at the current time
        if self.image is None or current_time - getattr(self, 'last_frame_time', 0) > 0.033:
            frame = clip.get_frame(current_time)
            self.image = pg.surfarray.make_surface(frame.swapaxes(0, 1))
            self.image = pg.transform.scale(self.image, screen.get_size())
            self.last_frame_time = current_time
        
        screen.blit(self.image, (0, 0))
        
    def dead(self):
        if not self.sound_played and not mute:
           self.sound_channel.play(self.sound)
           self.sound_played = True

g_over = Game_over()

boss_score = 100



missino_passed_size = (600,300)
mission_passed = pg.image.load('mission_passed.png')
mission_passed = pg.transform.scale(mission_passed,missino_passed_size)
game_done = False
class Done():
    def __init__(self):
        global ost
        self.image = mission_passed
        self.rect = self.image.get_rect()
        self.x = screen_width//2 - self.rect.width//2
        self.y = 100
        self.pos = (self.x,self.y)
        self.sound = pg.mixer.Sound('mission_passed.mp3')
        self.sound_played = False
        
        self.alpha = 0

        self.image.set_alpha(self.alpha)
        
    def place(self):
        #global game_done
        #game_done = True
        self.rect.x,self.rect.y = self.pos
        if not self.sound_played:
            ost.stop()
            
            self.sound.play()
            self.sound_played = True
    def transparent(self):
        if self.alpha < 255:
            self.alpha += 0.5
            self.image.set_alpha(self.alpha)
    def draw(self):
        self.place()
        self.transparent()
        screen.blit(self.image,self.pos)
    pass

done = Done()



def draw_all():
    global boss_dead,game_over

   # if game_over:
   #    game_over = False

    if game_over:
        
        return



    if not game_over:
        background()
        mutebutton.draw(screen)
       
        platform.draw_blocks(screen)
    
    if game_on and not game_over:
        player.draw_player(screen)

        dash_cooldown_bar()

        score_counter.draw_score(screen)

        

        fps(keys)

        for tank in chosen_tank:
            tank.draw(screen)
            if score >= boss_score:
                chosen_tank.remove(tank)

        for enemy in air_enemies:
            enemy.draw(screen)
            if score >= boss_score:
                air_enemies.remove(enemy)

        for bullet_img,bullet in bullets:
            screen.blit(bullet_img,bullet)

        for bomb in bombs:
            bomb.draw(screen)  
            if score >= boss_score:
                bombs.remove(bomb)
    elif not game_on:
        menu.draw()

    if not game_over and game_on:
        if score >= boss_score:
            if not boss_dead:
                boss.make()

    if boss_dead:
        done.draw()

ost = pg.mixer.Sound('ost.mp3')

ost_played = False
def play_ost():
    global ost_played

    
    ost.set_volume(0.4)
    if not ost_played and not mute:
        ost.play()
        ost_played = True
    

running = True

while running:
    dt = clock.tick(100)/1000
    keys = inputs()
    
    if not ost_played and not mute and game_on:
        play_ost()
    if game_over:
        ost.stop()
 
    for event in pg.event.get(): 
        if event.type == pg.QUIT:
            running = False
    if game_on and not game_over: 
        if not game_done:
            update_player(keys)
        if not score >= boss_score:
            update_enemies(dt)
            update_bombs(dt,screen)
    elif not game_on:
        menu.click_play()   


    if game_over:
       # screen.fill((0, 0, 0))
        g_over.make_vid()
        restart_button.make()

    

    draw_all()



    pg.display.flip()

   
   

    


