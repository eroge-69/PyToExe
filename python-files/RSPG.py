

import math
import re
import sys
from turtle import Screen
import pygame
import random
import time
import sys
import os
import csv
import json
import threading
import pygame.display
import pygame.mixer

class GameCamera:
    def __init__(self, display_surface, world_map_surface, items_list):
        self.display_surface = display_surface
        self.world_map_surface = world_map_surface
        self.items_list = items_list

        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0

        self.min_zoom = 0.25
        self.max_zoom = 3.0
        self.zoom_speed = 0.1

    def set_zoom(self, level):
        self.zoom = max(self.min_zoom, min(self.max_zoom, level))

    def zoom_in(self):
        self.set_zoom(self.zoom + self.zoom_speed)

    def zoom_out(self):
        self.set_zoom(self.zoom - self.zoom_speed)

    def _apply_rect(self, world_rect, current_zoom):
        scaled_x = int(world_rect.x * current_zoom + self.offset_x)
        scaled_y = int(world_rect.y * current_zoom + self.offset_y)
        scaled_width = int(world_rect.width * current_zoom)
        scaled_height = int(world_rect.height * current_zoom)
        return pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)

    def _get_visible_world_rect(self, current_zoom):
        world_x_topleft = -self.offset_x / current_zoom
        world_y_topleft = -self.offset_y / current_zoom
        world_visible_width = self.display_surface.get_width() / current_zoom
        world_visible_height = self.display_surface.get_height() / current_zoom
        return pygame.Rect(world_x_topleft, world_y_topleft, world_visible_width, world_visible_height)

    def camera_render(self, target_x, target_y, zoom=1.0):
        self.set_zoom(zoom)
       
        # Scale entire map
        scaled_world_map_width = int(self.world_map_surface.get_width() * self.zoom)
        scaled_world_map_height = int(self.world_map_surface.get_height() * self.zoom)

        # Scale the target for offset centering
        scaled_target_x = target_x * self.zoom
        scaled_target_y = target_y * self.zoom

        # Recalculate offset
        self.offset_x = -scaled_target_x + self.display_surface.get_width() / 2
        self.offset_y = -scaled_target_y + self.display_surface.get_height() / 2

        # Center the entire map if it's smaller than the screen
        if scaled_world_map_width < self.display_surface.get_width():
            self.offset_x = (self.display_surface.get_width() - scaled_world_map_width) / 2
        if scaled_world_map_height < self.display_surface.get_height():
            self.offset_y = (self.display_surface.get_height() - scaled_world_map_height) / 2

        # Create the scaled map surface
        current_scaled_map_surface = pygame.transform.scale(
            self.world_map_surface, (scaled_world_map_width, scaled_world_map_height)
        )

        # Blit the map directly using offset
        self.display_surface.blit(current_scaled_map_surface, (self.offset_x, self.offset_y))

        # Get the visible area in world coords
        visible_world_rect = self._get_visible_world_rect(self.zoom)

        # Render all items in visible area
        for item in self.items_list:
            if not item.rect.colliderect(visible_world_rect):
                continue

            scaled_width = int(item.original_image.get_width() * self.zoom)
            scaled_height = int(item.original_image.get_height() * self.zoom)

            if scaled_width > 0 and scaled_height > 0:
                item.image = pygame.transform.scale(item.original_image, (scaled_width, scaled_height))
            else:
                item.image = pygame.Surface((1, 1))

            screen_rect = self._apply_rect(item.rect, self.zoom)
            self.display_surface.blit(item.image, screen_rect)

try:
    with open("planes/levels.json","r") as file:
        levels = json.load(file)
    level1 = levels["level1"]
    level2 = levels['level2']
except json.decoder.JSONDecodeError:
    level1 = ["pt-17",'sopwith_camel',"fokker_dr1"]
    level2 = ["f4f_wildcat","bear_cat"]

pygame.init()
runing = True
WORLD_WIDTH = 5000
WORLD_HIGHT = 5000 
loops = 0
Map = pygame.Surface((WORLD_WIDTH,WORLD_WIDTH))
tiles = []
display = pygame.display.set_mode((1500,750))
display.fill((49, 104, 158))
center_x = display.get_width() / 2
center_y = display.get_height() / 2
camra = GameCamera(display,Map,tiles)
display.fill([30, 94, 148])
Map.fill([49, 104, 158])
pygame.display.flip()
clock = pygame.Clock()

text_font = pygame.font.SysFont("Arial", 20)
text_font_big = pygame.font.SysFont("Arial", 50)

def disp_text(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    display.blit(img, rect)
    return rect

class Parical():
    def __init__(self,WT,x,y,direction,user_name=None):
        self.WT = WT
        self.x = x
        self.y = y
        self.speed = 0
        with open(f"images/{WT}.json") as file:
            data = json.load(file)
        self.amount = data['amount']
        self.sizex = data['sizex']
        self.sizey = data['sizey']
        self.life_time = data['life_time']
        rad = math.radians(direction)
        delta_x = -self.speed * math.sin(rad)
        delta_y = -self.speed * math.cos(rad)
        self.x += delta_x
        self.y += delta_y
        self.dx = delta_x
        self.dy = delta_y
        self.original_image = pygame.image.load(f"images/{WT}.png")
        self.image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.original_image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.rect = self.image.get_rect(center=(500, 350))
        self.owner = user_name
        self.screen_rect = self.rect

        self.update(display,camra)

    def update(self, display_surface, camera_obj):
        self.x += self.dx
        self.y += self.dy
        self.life_time -= 1
        self.rect.center = (self.x, self.y)
        scaled_width = int(self.original_image.get_width() * camera_obj.zoom)
        scaled_height = int(self.original_image.get_height() * camera_obj.zoom)
        current_scaled_image = self.image 
        if scaled_width > 0 and scaled_height > 0:
            current_scaled_image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
        else:
            current_scaled_image = pygame.Surface((1,1))
        if self.life_time >= 0: 
            screen_x = (self.x * camera_obj.zoom) + camera_obj.offset_x
            screen_y = (self.y * camera_obj.zoom) + camera_obj.offset_y
            screen_rect = current_scaled_image.get_rect(center=(screen_x, screen_y))
            display_surface.blit(current_scaled_image, screen_rect)
            self.screen_rect = screen_rect
            self.current_scaled_image = current_scaled_image
            return screen_rect

    def blit(self,display_surface):
        display_surface.blit(self.current_scaled_image, self.screen_rect)

class AI():
    def __init__(self,all_planes,all_bullets,all_xp):
        self.all_xp = all_xp
        self.all_bullets = all_bullets
        self.all_planes = all_planes
        self.plane = Plane(random.choice(["Bob","ai","plz_dont_kill","James","I_am_not_heare"]),random.choice(level1))
        self.fired = self.plane.fired
        self.health = self.plane.health
        self.target = None
        all_planes.append(self.plane)
        self.all_planes.remove(self.plane)

    def find_target(self, all_objects, distance):
        closest = None
        closest_dist = float('inf')
        for obj in all_objects:
            dx = obj.x - self.plane.x
            dy = obj.y - self.plane.y
            dist = math.hypot(dx, dy)
            if dist < closest_dist and dist <= distance:
              if not obj.PT == "pNone":
                closest = obj
                closest_dist = dist
        return closest


    def whay_ops(self):
        if self.target != None:
            C_health = self.plane.health - self.target.health
            C_top_speed = self.plane.top_speed - self.target.top_speed
            C_turn_speed = self.plane.turn_speed - self.target.turn_speed
            C_fire_speed = self.plane.fire_speed - self.target.fire_speed
            C_armor = self.plane.armor - self.target.armor
            C_acceleration = self.plane.acceleration - self.target.acceleration
            B_health = 1 if C_health >= 0 else 0
            B_top_speed = 1 if C_top_speed >= 0 else 0
            B_turn_speed = 1 if C_turn_speed >= 0 else 0
            B_fire_speed = 1 if C_fire_speed >= 0 else 0
            B_armor = 1 if C_armor >= 0 else 0
            B_acceleration = 1 if C_acceleration >= 0 else 0
            average_score = (B_health + B_top_speed + B_turn_speed +
                             B_fire_speed + B_armor + B_acceleration) / 6
            return average_score

    def whay_xp(self):
        if self.all_xp != None:
            xp_amount = len(self.all_xp)
            conf = xp_amount / 800
            return conf
        else: 
            return 0

    def attack(self, target):
        # Calculate relative position
        dx = target.x - self.plane.x
        dy = target.y - self.plane.y
        distance = math.hypot(dx, dy)

        # Angle to the target (in degrees)
        angle_to_target = (math.degrees(math.atan2(-dx, -dy)) + 360) % 360
        angle_diff = (angle_to_target - self.plane.angle + 360) % 360
        if angle_diff > 180:
            angle_diff -= 360  # Convert to range -180 to 180

        # Speed difference
        speed_diff = self.plane.speed - target.speed

        # Turning decision
        if angle_diff > 10:
            leftRite = 1  # turn right
        elif angle_diff < -10:
            leftRite = 2  # turn left
        else:
            leftRite = 0  # aligned enough

        # Forward/back decision
        if distance > 250 and speed_diff < 0:
            frontBack = 1  # go faster to catch up
        elif distance < 150 and speed_diff > 0:
            frontBack = 2  # slow down
        else:
            frontBack = 0  # maintain speed

        # Fire if roughly aligned and within shooting range
        if abs(angle_diff) < 5 and distance < 300:
            spaceShif = 1
        else:
            spaceShif = 0

        # num_k can be used to indicate level of confidence, or tactic mode
        num_k = 1 if spaceShif == 1 else 0

        return frontBack, leftRite, spaceShif, num_k

    def choose_op(self):
        choice = 0
        frontBack, leftRite, spaceShif, num_k = 0,0,0,0
        self.target = self.find_target(self.all_planes,800)
        confidance = self.whay_ops()
        xp_conf = self.whay_xp()
        if self.target != None:
            
            if confidance >= 0.6 and xp_conf <= confidance:
                print(f"{self.plane.PT} is atacking PT>{self.target.PT}")
                frontBack, leftRite, spaceShif, num_k = self.attack(self.target)
                self.plane.ai_event(loops,frontBack, leftRite, spaceShif, 0)
            elif xp_conf >= 0.6:
                print("colecting xp")
                self.plane.ai_event(loops,frontBack, leftRite, spaceShif, 0)
            else:
                print("runing")
                self.plane.ai_event(loops,frontBack, leftRite, spaceShif, 0)
        else:
            if xp_conf >= 0.5:
                print("gathering xp")
                self.plane.ai_event(loops,frontBack, leftRite, spaceShif, 0)
            else:
                print("wandering")
                self.plane.ai_event(loops,frontBack, leftRite, spaceShif, 0)

class Wepons():
    def __init__(self,WT,x,y,direction,user_name):
        self.WT = WT
        self.x = x
        self.y = y
        with open(f"wepons/wepon_stats/{WT}.json") as file:
            data = json.load(file)
        self.speed = data['speed']
        self.damage = data['damage']
        self.sizex = data['sizex']
        self.sizey = data['sizey']
        self.life_time = data['life_time']
        self.fire_sound = data['fire_sound']
        self.hit_sound = data['hit_sound']
        rad = math.radians(direction)
        delta_x = -self.speed * math.sin(rad)
        delta_y = -self.speed * math.cos(rad)
        self.x += delta_x
        self.y += delta_y
        self.dx = delta_x
        self.dy = delta_y
        self.original_image = pygame.image.load(f"wepons/{WT}.png")
        self.image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.original_image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.rect = self.image.get_rect(center=(500, 350))
        self.owner = user_name
        self.screen_rect = self.rect

    def update(self, display_surface, camera_obj):
        self.x += self.dx
        self.y += self.dy
        self.life_time -= 1
        self.rect.center = (self.x, self.y)
        scaled_width = int(self.original_image.get_width() * camera_obj.zoom)
        scaled_height = int(self.original_image.get_height() * camera_obj.zoom)
        current_scaled_image = self.image 
        if scaled_width > 0 and scaled_height > 0:
            current_scaled_image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
        else:
            current_scaled_image = pygame.Surface((1,1))
        if self.life_time >= 0: 
            screen_x = (self.x * camera_obj.zoom) + camera_obj.offset_x
            screen_y = (self.y * camera_obj.zoom) + camera_obj.offset_y
            screen_rect = current_scaled_image.get_rect(center=(screen_x, screen_y))
            display_surface.blit(current_scaled_image, screen_rect)
            return screen_rect
            

    def fire(self):
        sound = pygame.mixer_music.load(f"sounds/{self.fire_sound}.mp3")
        pygame.mixer_music.set_volume(0.6)
        pygame.mixer_music.play()

class Plane(pygame.sprite.Sprite):

    def __init__(self,user_name,PT):
        self.user_name = user_name
        self.angle = 0
        self.speed = 1
        self.x = random.randint(0,WORLD_WIDTH)
        self.y = random.randint(0,WORLD_HIGHT)
        self.PT = PT
        try:
            with open(f"planes/stats/{PT}.json") as file:
                data = json.load(file)
        except Exception:
            with open(f"planes/stats/{PT}.json") as file:
                data = json.load(file)
        self.acceleration = data['acceleration']
        self.armor = data['armor']
        self.fire_speed = data['fire_speed']
        self.max_health = data['health']
        self.health = self.max_health
        self.reload_speed = data['reload_speed']
        self.sizex = data['sizex']
        self.sizey = data['sizey']
        self.top_speed = data['top_speed']
        self.turn_speed = data['turn_speed']
        self.wepons = data['wepons']
        self.wepon = self.wepons[0]
        self.wepon_amounts = data['wepon_amounts']
        self.xp_value = data['xp_value']
        self.curent_leval = data['leval']
        self.C_amo = self.wepon_amounts[0]
        self.original_image = pygame.image.load(f"planes/{PT}.png")
        self.image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.original_image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.Rect = self.image.get_rect(center=(center_x, center_y))
        self.num = 0
        self.xp = 0
        self.fired = []

    def respawn(self,PT):
        self.PT = PT
        with open(f"planes/stats/{PT}.json") as file:
            data = json.load(file)
        self.acceleration = data['acceleration']
        self.armor = data['armor']
        self.fire_speed = data['fire_speed']
        self.max_health = data['health']
        self.health = self.max_health
        self.reload_speed = data['reload_speed']
        self.sizex = data['sizex']
        self.sizey = data['sizey']
        self.top_speed = data['top_speed']
        self.turn_speed = data['turn_speed']
        self.wepons = data['wepons']
        if self.wepons != []:
            self.wepon = self.wepons[0]
        self.wepon_amounts = data['wepon_amounts']
        self.xp_value = data['xp_value']
        self.curent_leval = data['leval']
        if self.wepon_amounts != []:
            self.C_amo = self.wepon_amounts[0]
        self.original_image = pygame.image.load(f"planes/{PT}.png")
        self.image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.original_image = pygame.transform.scale(self.original_image,(self.sizex,self.sizey))
        self.Rect = self.image.get_rect(center=(center_x, center_y))

    def rotate(self):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.Rect = self.image.get_rect(center=(center_x, center_y))

    def blit(self):
        global camra_zoom
        if not self.health <= 0:
            camra.camera_render(self.x, self.y)
            display.blit(self.image, self.Rect.topleft)
            print(f"{self.user_name}s health is {self.health}")
        else:
            camra.camera_render(self.x, self.y,camra_zoom)
            return True
        rec = disp_text(self.user_name,text_font,(0,10,0),self.Rect.centerx,self.Rect.y -30)
        pygame.draw.rect(display,(0,100,0),(center_x-self.health/2,rec.y+30,self.health,10),border_radius=3)

    def drop_xp(self):
        global all_xp
        for i in range(int(self.xp_value/10)):
            Xp = Parical("xp",random.randint(0,self.sizex),random.randint(0,self.sizey),0)
            Xp.update(display,camra)
            all_xp.append(Xp)

    def move(self):
        amount = self.speed
        direction = self.angle
        rad = math.radians(direction)
        delta_x = -amount * math.sin(rad)
        delta_y = -amount * math.cos(rad)
        self.x += delta_x
        self.y += delta_y
        
    def wep(self,num):
        if num != None:
            num -= 1
            WL = len(self.wepons)
            num = (num % WL)
            self.wepon = self.wepons[num]
            self.C_amo = self.wepon_amounts[num]
            self.num = num

    def fire(self):
        if len(self.fired) <= self.C_amo:
            B1 = Wepons(self.wepon,self.x,self.y,self.angle,self.user_name)
            B1.fire()
            self.fired.append(B1)
            
    def clean(self):
        for B in self.fired:
            if B.life_time <= 0:
                self.fired.remove(B)

    def update_bullets(self,all_bullets,owners_bullets=False):
        for fired in all_bullets:
            for bullet in fired:
                if bullet.owner != self.user_name:
                    if bullet.rect.colliderect((self.x,self.y,self.sizex,self.sizey)):
                        self.health -= bullet.damage / self.armor
                        bullet.life_time = 5

    def collect_xp(self):
        global all_xp
        for xp in all_xp:
            if self.Rect.colliderect(xp.screen_rect):
                print(f"{self.user_name} has colected {xp.amount} XP")
                self.xp += xp.amount
                all_xp.remove(xp)
                del xp
                         
    def event(self,loops):
        global all_planes,R_menue_G,button_rects,respawn_lev
        presed = False
        num = None
        button = pygame.key.get_pressed()
        if button[pygame.K_w]:
            if self.speed <= self.top_speed:
                self.speed += self.acceleration
            presed = True
        elif button[pygame.K_s]:
            if self.speed >= 2:
                self.speed -= self.acceleration
            presed = True
        if button[pygame.K_a]:
            self.angle += self.turn_speed
            self.rotate()
            presed = True
        elif button[pygame.K_d]:
            self.angle -= self.turn_speed
            self.rotate()
            presed = True
        if button[pygame.K_SPACE]:
            if loops % self.fire_speed == 0:
                self.fire()

        if self.speed > self.top_speed:
            self.speed -= self.acceleration

        if button[pygame.K_1]:
            num = 1
        elif button[pygame.K_2]:
            num = 2
        elif button[pygame.K_3]:
            num = 3
        elif button[pygame.K_4]:
            num = 4
        elif button[pygame.K_5]:
            num = 5
        elif button[pygame.K_6]:
            num = 6
        elif button[pygame.K_7]:
            num = 7
        elif button[pygame.K_8]:
            num = 8
        elif button[pygame.K_9]:
            num = 9
        elif button[pygame.K_0]:
            num = 10

        self.wep(num)
        self.move()
        self.clean()
        if self.health <= 0 and self.PT != "pNone":
            self.respawn("pNone")
            obj = all_planes.index(self)
            all_planes[obj].PT = "pNone"
            pygame.mixer.music.load("sounds/death_song.mp3")
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play()
            respawn_lev = None
            button_rects = []
            R_menue_G = None

            self.drop_xp()

        print(f"user >{self.user_name} is at x>{self.x} y>{self.y}")
        print(f"the speed is {self.speed}")
        self.blit()
        return presed

    def ai_move(self):
        amount = self.speed
        rad = math.radians(self.angle)
        delta_x = -amount * math.sin(rad)
        delta_y = -amount * math.cos(rad)
        self.x += delta_x
        self.y += delta_y

        #  HARD BORDER ENFORCEMENT FOR AI ONLY
        out_of_bounds = False

        if self.x < 0:
            self.x = 0
            out_of_bounds = True
        elif self.x > WORLD_WIDTH:
            self.x = WORLD_WIDTH
            out_of_bounds = True

        if self.y < 0:
            self.y = 0
            out_of_bounds = True
        elif self.y > WORLD_HIGHT:
            self.y = WORLD_HIGHT
            out_of_bounds = True

        if out_of_bounds:
            # Optional: snap AI to face toward center
            dx = (WORLD_WIDTH // 2) - self.x
            dy = (WORLD_HIGHT // 2) - self.y
            angle_rad = math.atan2(dx, -dy)
            self.angle = math.degrees(angle_rad)

    def ai_blit(self, display_surface, camera_obj):
        if self.health <= 0:
            return

        scaled_width = int(self.original_image.get_width() * camera_obj.zoom)
        scaled_height = int(self.original_image.get_height() * camera_obj.zoom)

        if scaled_width > 0 and scaled_height > 0:
            scaled_image = pygame.transform.scale(self.original_image, (scaled_width, scaled_height))
        else:
            scaled_image = pygame.Surface((1,1))

        rotated_image = pygame.transform.rotate(scaled_image, self.angle)
        rect = rotated_image.get_rect()
    
        screen_x = (self.x * camera_obj.zoom) + camera_obj.offset_x
        screen_y = (self.y * camera_obj.zoom) + camera_obj.offset_y
        rect.center = (screen_x, screen_y)

        display_surface.blit(rotated_image, rect)

        # Optional: Draw name above AI plane
        rec = disp_text(self.user_name, text_font, (0, 0, 0), rect.centerx, rect.top - 15)
        pygame.draw.rect(display,(0,100,0),(rect.centerx-self.health/2,rec.y+30,self.health,10),border_radius=3)

    def ai_event(self,loops,frontBack,leftRite,spaceShif,num_k):
        global all_planesd
        presed = False
        num = None
        if frontBack == 1:
            if self.speed <= self.top_speed:
                self.speed += self.acceleration
            presed = True
        elif frontBack == 2:
            if self.speed >= 2:
                self.speed -= self.acceleration
            presed = True
        if leftRite == 1:
            self.angle += self.turn_speed
            self.rotate()
            presed = True
        elif leftRite == 2:
            self.angle -= self.turn_speed
            self.rotate()
            presed = True
        if spaceShif == 1:
            if loops % self.fire_speed == 0:
                self.fire()
        elif spaceShif == 2:
            print("shift is not bound")

        if num_k == 1:
            num = 1
        elif num_k == 2:
            num = 2
        elif num_k == 3:
            num = 3
        elif num_k == 4:
            num = 4
        elif num_k == 5:
            num = 5
        elif num_k == 6:
            num = 6
        elif num_k == 7:
            num = 7
        elif num_k == 8:
            num = 8
        elif num_k == 9:
            num = 9
        elif num_k == 10:
            num = 10

        self.wep(num)
        self.ai_move()
        self.clean()       
        self.ai_blit(display,camra)
        if self.health <= 0 and self.PT != "pNone":
            self.respawn("pNone")
            obj = all_planes.index(self)
            all_planes[obj].PT = "pNone"
            
            self.xp = self.xp / 2
            self.drop_xp()

        print(f"AI>{self.user_name} is at x>{self.x} y>{self.y} at speed {self.speed}")
        print(f"AI>{self.user_name}s health is {self.health}")
        return presed

class Tools():
    def __init__(self):
        pass

    def click(self,ob_rect, detect_click=False):
        mouse_pos = pygame.mouse.get_pos()  
        mouse_pressed = pygame.mouse.get_pressed()
        #------------------------------------------------------------------------------------------------------------------------


def event():
    global runing,g,text,Menue,camra_zoom,all_xp
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runing = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player1.health += 20
            if event.key == pygame.K_f:
                player1.speed += 50
            if event.key == pygame.K_ESCAPE:
                Menue = 0
                pygame.mixer.music.load("sounds/still_alive.mp3")
                pygame.mixer_music.play(-1)
            if event.key == pygame.K_LSHIFT:
                lev = random.randint(0,2)
                if lev == 0:
                    PT = random.choice(level1)
                elif lev == 1:
                    PT = random.choice(level2)
                else:
                    PT = "pt-17"
                player1.respawn(PT)
            if event.key == pygame.K_k:
                player1.xp += 10

def update_B(all_B):
    for fired in all_B:
        for bullet in fired:
            bullet.update(display,camra)

def main_menue():
    global runing,g,text,typing,user_name,Menue,player1,all_planes
    DT = "enter username"
    if text != "":
        DT = text
    # text box
    pygame.draw.rect(display,(100,100,100,100),(center_x-200,center_y-50,400,50),border_radius=20)
    pygame.draw.rect(display,(50,50,50,0),(center_x-200,center_y-50,400,50),width= 4,border_radius=15)
    disp_text(DT,pygame.font.SysFont("Arial", 25),(80,80,80),center_x,center_y-25)
    # play button
    play_rect = pygame.draw.rect(display,(50,150,50),(center_x-100,center_y+10,200,60),border_radius=20)
    disp_text("play",text_font_big,(0,0,0),center_x,center_y+35)
    # setings button
    settintg_rect = pygame.draw.rect(display,(100,150,100),(display.get_width()-200,display.get_height()-50,150,30),border_radius=3)
    disp_text("settings ",text_font,(7,0,0),display.get_width()-150,display.get_height()-36)
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runing = False
        if typing:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_RETURN:
                    if text != "" and text != " ":
                        Menue = 1
                        user_name = text
                        display.fill([49, 104, 158])
                        player1 = Plane(text,random.choice(level1))
                        all_bullets.append(player1.fired)
                        all_planes.append(player1)
                        pygame.mixer_music.stop()
                else:
                    if len(text) <= 24:
                        text += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            mouse_button = event.button
            if play_rect.collidepoint(mouse_pos[0],mouse_pos[1]) and mouse_button == 1 and text != "" and text != " ":
                Menue = 1
                user_name = text
                display.fill([49, 104, 158])
                if player1 != None:
                    xp = player1.xp
                else:
                    xp = 0
                player1 = Plane(text,random.choice(level1))
                player1.xp = int(xp/2)
                all_bullets.append(player1.fired)
                all_planes.append(player1)
                pygame.mixer_music.stop()
            if settintg_rect.collidepoint(mouse_pos[0],mouse_pos[1]) and mouse_button == 1:
                #  settings_menue()
                Menue = 2
                print("settings was presed")

def settings_menue():
    global runing,g,text,typing,user_name,Menue
    display.fill([49, 104, 158])

    with open("data/settings.json","r") as file:
        data = json.load(file)
    test_rect = pygame.draw.rect(display,(100,100,100),(50,30,200,50))
    disp_text(f"test {data['test']}",text_font_big,(0,0,0),150,55)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runing = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Menue = 0
                camra.camera_render(random.randint(0, int(float(WORLD_WIDTH) / 1.1)),random.randint(0,int(float(WORLD_HIGHT) / 1.1)))
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            mouse_button = event.button
            if mouse_button == 1 and test_rect.collidepoint(mouse_pos[0],mouse_pos[1]):
                if data['test'] == 1:
                    data['test'] = 0
                elif data['test'] == 0:
                    data['test'] = 1
                with open("data/settings.json","w") as file:
                    json.dump(data,file,indent=4)

def respawn_menue(level,create_surf=True, p_size_x=100, p_size_y=100, y_pos=20):
    if create_surf:
        rects = []
        plane_count = len(level)
        total_sizeX = p_size_x * plane_count
        total_sizeY = p_size_y
        menu_surface = pygame.Surface((total_sizeX, total_sizeY), pygame.SRCALPHA)
        menu_surface.fill((0, 0, 0, 0)) 
        background_rect = pygame.Rect(0, 0, total_sizeX, total_sizeY)
        pygame.draw.rect(menu_surface, (100, 100, 100), background_rect, border_radius=10)
        for ind, plane in enumerate(level):
            img = pygame.image.load(f"planes/{plane}.png").convert_alpha()
            img = pygame.transform.scale(img, (p_size_x, p_size_y))
            menu_surface.blit(img, (p_size_x * ind, 0))
            rects.append({plane:img.get_rect()})
        print(f"planes in level >{plane_count}")
        return menu_surface,rects

def respawn_check(plane,is_ai):
    global lev_data,Menue,R_menue_G,button_rects,respawn_lev
    ind = -1
    plane_lev = plane.curent_leval
    next_lev = plane_lev + 1
    next_lev_amount = next_lev * lev_data['level_amount']
    plane_xp = plane.xp
    if plane.PT == "pNone":
        plane.x = random.randint(0,WORLD_WIDTH)
        plane.y = random.randint(0,WORLD_HIGHT)
        Menue = 0
        plane.xp = plane.xp/2
    if plane_xp >= next_lev_amount:
        if is_ai:
            if next_lev <= lev_data['last_level']:
                choice = random.choice(lev_data[f"level{next_lev}"])
                plane.respawn(choice)
                plane.xp -= next_lev_amount
        else:
            if next_lev <= lev_data['last_level'] and button_rects == []:
                respawn_lev = lev_data[f"level{next_lev}"]
                R_menue_G,button_rects = respawn_menue(lev_data[f"level{next_lev}"],True)
    else:
        respawn_lev = None
        button_rects = []
        R_menue_G = None
            
def manage_ais():
    global all_ais,all_bullets,all_planes,loops
    if len(all_ais) <= 10:
        ai = AI(all_planes,all_bullets,[])
        all_ais.append(ai)
        all_planes.append(ai.plane)
    if all_ais != []:
        for ai in all_ais:
            ai.all_planes = [p for p in all_planes if p is not ai.plane]
            ai.choose_op()
            ai.plane.ai_blit(display,camra)
            all_bullets.append(ai.plane.fired)
            ai.plane.update_bullets(all_bullets)
            ai.plane.collect_xp()
            if loops % 40 == 0 and ai.plane.xp >= 50 :
                respawn_check(ai.plane,True)

            if ai.plane.health <= 0:
                all_planes.remove(ai.plane)
                del ai.plane
                all_ais.remove(ai)
                del ai

def manage_xp():
    global all_xp,all_planes
    if len(all_xp) <= len(all_planes)*20:
        Xp = Parical("xp",random.randint(0,WORLD_WIDTH),random.randint(0,WORLD_HIGHT),0)
        Xp.update(display,camra)
        all_xp.append(Xp)
    for xp in all_xp:
        xp.update(display,camra)
        if xp.life_time <= 0:
            all_xp.remove(xp)
            del xp


with open("planes/levels.json","r") as file1:
    lev_data = json.load(file1)
              
planeT = random.choice(level1)
player1 = None
Menue = 0
text = ""
typing = True
user_name = text
tools = Tools()
all_xp = []
all_bullets = []
all_ais = []
all_planes = []
ai_count = 0
camra_zoom = 1
respawn_lev = None
button_rects = []
R_menue_G = None


img = pygame.image.load("tarane/map1.png")
img2 = pygame.transform.scale(img,(WORLD_WIDTH,WORLD_HIGHT))
Map.blit(img2,(0,0))
camra.camera_render(random.randint(0, int(float(WORLD_WIDTH) / 1.1)),random.randint(0,int(float(WORLD_HIGHT) / 1.1)))
pygame.display.flip()
pygame.mixer.music.load("sounds/still_alive.mp3")
pygame.mixer_music.play(-1)
main_menue()


while runing:
    all_bullets = []
    
    if Menue == 0:
        main_menue()
    elif Menue == 1:
        event()
        all_bullets.append(player1.fired)
        player1.event(loops)
        print(f"======= all_planes> {len(all_planes)}")
        manage_xp()
        manage_ais()
        update_B(all_bullets)
        player1.update_bullets(all_bullets)
        player1.collect_xp()
        if loops % 8:
            respawn_check(player1,False)

        if respawn_lev != None and R_menue_G != None:
            display.blit(R_menue_G,(center_x-R_menue_G.get_width()/2,20))

            
        
        

        disp_text(f"XP -> {player1.xp}",text_font,(0,0,0),100,50)
    elif Menue == 2:
        settings_menue()

    pygame.display.flip()
    loops += 1
    print(f"loops are at {loops}")
    clock.tick(20)