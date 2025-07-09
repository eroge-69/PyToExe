# import the pygame module
import traceback
import pygame
from time import sleep
from random import randint
from math import floor
import time
import math


# import pygame.locals for easier
# access to key coordinates
from pygame.locals import *

# Define our square object and call super to
# give it all the properties and methods of pygame.sprite.Sprite
# Define the class for our square objects

# initialize pygame
pygame.init()

# Define the dimensions of screen object
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width = pygame.display.Info().current_w
height = pygame.display.Info().current_h

x_list = []
y_list = []
mass_list = []

Spheres = []

zoom = 119396250

camera_x = 599400000000
camera_y = -30000000000


class Sphere:
    def __init__(self, x, y, dx, dy, mass, radius, color, index):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.dx_history = []
        self.dy_history = []
        self.mass = mass
        self.radius = radius
        self.color = color
        self.index = index
        self.touched = False
        Spheres.append(self)
        x_list.append(self.x)
        y_list.append(self.y)
        mass_list.append(self.mass)

    def listify(self):
        return [self.x, self.y, self.dx, self.dy, self.mass, self.radius, self.color, self.index]

    def force(self):
        global objects
        for i in x_list:
            if x_list.index(i) != self.index:
                i1 = y_list[x_list.index(i)]
                try:
                    if math.hypot(self.x - Spheres[x_list.index(i)].x,
                                  self.y - Spheres[x_list.index(i)].y) > self.radius + Spheres[
                        x_list.index(i)].radius:
                        force = 6.6743 * (10 ** (-12)) * (
                                (mass_list[x_list.index(i)]) / math.hypot(self.x - i, self.y - i1) ** 2)
                    else:
                        force = 6.6743 * (10 ** (-12)) * (
                                (mass_list[x_list.index(i)]) / (self.radius + Spheres[x_list.index(i)].radius) ** 2)
                except:
                    traceback.print_exc()
                try:
                    if i - self.x > 0:
                        self.dx += (math.cos(math.atan((i1 - self.y) / (i - self.x)))) * force
                        self.dy += (math.sin(math.atan((i1 - self.y) / (i - self.x)))) * force
                    elif i - self.x < 0:
                        self.dx -= (math.cos(math.atan((i1 - self.y) / (i - self.x)))) * force
                        self.dy -= (math.sin(math.atan((i1 - self.y) / (i - self.x)))) * force

                except:
                    traceback.print_exc()

        try:
            x_list[self.index] = self.x
            y_list[self.index] = self.y
        except:
            traceback.print_exc()
        # self.dx_history.append(self.dx)
        # self.dy_history.append(self.dy)

    def move(self):
        self.x += self.dx / 10
        self.y += self.dy / 10

    def show(self):
        if math.hypot(self.x - Spheres[len(Spheres) - 1].x, self.y - Spheres[len(Spheres) - 1].y) < self.radius + \
                Spheres[len(Spheres) - 1].radius and self != Spheres[len(Spheres) - 1]:
            self.touched = True
        if self.index != len(Spheres) - 1:
            pygame.draw.circle(screen, self.color, (((self.x + camera_x - (width / 2)) / zoom) + (width / 2),
                                                    ((self.y - camera_y - (height / 2)) / zoom) + (height / 2)),
                               self.radius / zoom)
        else:
            pygame.draw.circle(screen, self.color, (((self.x + camera_x - (width / 2)) / zoom) + (width / 2),
                                                    ((self.y - camera_y - (height / 2)) / zoom) + (height / 2)),
                               self.radius)



Particles = []


class Particle:

    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.age = 0
        Particles.append(self)

    def show(self):
        if zoom < 4 * 119396250:
            pygame.draw.circle(screen, (255, 180, 0), (self.x, self.y),
                               4 * ((-1 / 50) * self.age + 1))
        else:
            pygame.draw.circle(screen, (255, 180, 0), (self.x, self.y),
                               (2 * 119396250 * 4 * ((-1 / 50) * self.age + 1)) / zoom)

        self.age += 1
        if self.age == 50:
            Particles.remove(self)
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.9999
        self.dy *= 0.9999




Times_New_Roman = pygame.font.SysFont("Times New Roman", 72)
Times_New_Roman2 = pygame.font.SysFont("Times New Roman", 36)


def run():
    global Spheres
    global x_list
    global y_list
    global mass_list
    global Particles
    global camera_x
    global camera_y
    global zoom
    global Times_New_Roman
    global Times_New_Roman2

    Spheres = []
    x_list = []
    y_list = []
    mass_list = []

    zoom = 119396250

    camera_x = 599400000000
    camera_y = -30000000000

    Sphere(0, 0, 0, 0, 19891000000000000000000000000000000000000, 18000000000, (255, 225, 225), 0)
    Sphere(608400000000, 0, 0, 1350000000, 5972000000000000000000000000000000, 12000000000, (0, 225, 0), 1)
    Sphere(269732000000, 0, 0, 2100000000, 3285000000000000000000000000000, 9400000000, (138, 138, 138), 2)

    for i in range(6):
        Sphere(randint(-400000000000, 400000000000), randint(-400000000000, 400000000000),
               randint(-200, 200) * 10000000,
               randint(-200, 200) * 10000000, randint(2500000000000000, 5000000000000000000000000000000),
               randint(6000000000, 10000000000),
               (randint(100, 255), randint(100, 255), randint(100, 255)), len(Spheres))

    Sphere(599400000000, -30000000000, 110000000, 1350000000, 597200, 5, (0, 0, 255), len(Spheres))

    choose_mode = True
    running = True
    victory = True
    mode = 1
    mode_selected = False
    for i in range(255):
        screen.fill((i, 0, 0))
        screen.blit(Times_New_Roman.render('Use W, A, S, D to move your spaceship.', 1, (i, i, i)), (219, 50))
        screen.blit(Times_New_Roman2.render('(Left and Right Arrow Keys zoom in and out.)', 1, (i, i, i)),
                    (462, 150))
        screen.blit(Times_New_Roman.render('Crash into every celestial body to win!', 1, (i, i, i)), (242, 200))
        screen.blit(Times_New_Roman.render('Choose Difficulty:', 1, (i, i, i)), (532, 350))
        if mode == 0:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Easy', 1, (0, floor(((45/51)*i)), 0)), (181.6, 500))
            else:
                screen.blit(Times_New_Roman.render('Easy', 1, (i, i, i)), (181.6, 500))
        else:
            screen.blit(Times_New_Roman.render('Easy', 1, (floor(((183/255)*i)), floor((183/255)*i), floor((183/255)*i))), (181.6, 500))
        if mode == 1:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Normal', 1, (0, floor((45/51)*i), 0)), (503.16, 500))
            else:
                screen.blit(Times_New_Roman.render('Normal', 1, (i, i, i)), (503.16, 500))
        else:
            screen.blit(Times_New_Roman.render('Normal', 1, (floor((183/255)*i), floor((183/255)*i), floor((183/255)*i))), (503.16, 500))
        if mode == 2:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Hard', 1, (0, floor((45/51)*i), 0)), (904.7, 500))
            else:
                screen.blit(Times_New_Roman.render('Hard', 1, (i, i, i)), (904.7, 500))
        else:
            screen.blit(Times_New_Roman.render('Hard', 1, (floor((183/255)*i), floor((183/255)*i), floor((183/255)*i))), (904.7, 500))
        if mode == 3:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Insane', 1, (0, floor((45/51)*i), 0)), (1230.23, 500))
            else:
                screen.blit(Times_New_Roman.render('Insane', 1, (i, i, i)), (1230.23, 500))
        else:
            screen.blit(Times_New_Roman.render('Insane', 1, (floor((183/255)*i), floor((183/255)*i), floor((183/255)*i))), (1230.23, 500))
        screen.blit(Times_New_Roman.render('Press Space to Start the Game!', 1, (i, i, i)), (355, 650))
        screen.blit(Times_New_Roman2.render('(Use Backspace to Deselect)', 1, (i, i, i)), (594, 750))
        pygame.display.flip()
    while choose_mode:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                choose_mode = False
                running = False
                victory = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    choose_mode = False
                    running = False
                    victory = False
                elif event.key == K_RIGHT and not mode_selected:
                    mode += 1
                    if mode == 4:
                        mode = 0
                elif event.key == K_LEFT and not mode_selected:
                    mode -= 1
                    if mode == -1:
                        mode = 3
                elif event.key == K_SPACE and mode_selected:
                    choose_mode = False
                elif event.key == K_SPACE and not mode_selected:
                    mode_selected = True
                elif event.key == K_BACKSPACE and mode_selected:
                    mode_selected = False

        screen.fill((255, 0, 0))
        screen.blit(Times_New_Roman.render('Use W, A, S, D to move your spaceship.', 1, (255, 255, 255)), (219, 50))
        screen.blit(Times_New_Roman2.render('(Left and Right Arrow Keys zoom in and out.)', 1, (255, 255, 255)), (462, 150))
        screen.blit(Times_New_Roman.render('Crash into every celestial body to win!', 1, (255, 255, 255)),(242, 200))
        screen.blit(Times_New_Roman.render('Choose Difficulty:', 1, (255, 255, 255)), (532, 350))
        if mode == 0:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Easy', 1, (0, 225, 0)), (181.6, 500))
            else:
                screen.blit(Times_New_Roman.render('Easy', 1, (255, 255, 255)), (181.6, 500))
        else:
            screen.blit(Times_New_Roman.render('Easy', 1, (183, 183, 183)), (181.6, 500))
        if mode == 1:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Normal', 1, (0, 225, 0)), (503.16, 500))
            else:
                screen.blit(Times_New_Roman.render('Normal', 1, (255, 255, 255)), (503.16, 500))
        else:
            screen.blit(Times_New_Roman.render('Normal', 1, (183, 183, 183)), (503.16, 500))
        if mode == 2:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Hard', 1, (0, 225, 0)), (904.7, 500))
            else:
                screen.blit(Times_New_Roman.render('Hard', 1, (255, 255, 255)), (904.7, 500))
        else:
            screen.blit(Times_New_Roman.render('Hard', 1, (183, 183, 183)), (904.7, 500))
        if mode == 3:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Insane', 1, (0, 225, 0)), (1230.23, 500))
            else:
                screen.blit(Times_New_Roman.render('Insane', 1, (255, 255, 255)), (1230.23, 500))
        else:
            screen.blit(Times_New_Roman.render('Insane', 1, (183, 183, 183)), (1230.23, 500))
        if not mode_selected:
            screen.blit(Times_New_Roman.render('Press Space to Select your Difficulty', 1, (255, 255, 255)), (270, 650))
            screen.blit(Times_New_Roman2.render('(Use Arrow Keys to Change)', 1, (255, 255, 255)), (589, 750))
        else:
            screen.blit(Times_New_Roman.render('Press Space to Start the Game!', 1, (255, 255, 255)), (355, 650))
            screen.blit(Times_New_Roman2.render('(Use Backspace to Deselect)', 1, (255, 255, 255)), (594, 750))
        pygame.display.flip()

    for i in range(255):
        screen.fill((255 - i, 0, 0))
        screen.blit(Times_New_Roman.render('Use W, A, S, D to move your spaceship.', 1, (255-i, 255-i, 255-i)), (219, 50))
        screen.blit(Times_New_Roman2.render('(Left and Right Arrow Keys zoom in and out.)', 1, (255-i, 255-i, 255-i)),
                    (462, 150))
        screen.blit(Times_New_Roman.render('Crash into every celestial body to win!', 1, (255-i, 255-i, 255-i)), (242, 200))
        screen.blit(Times_New_Roman.render('Choose Difficulty:', 1, (255-i, 255-i, 255-i)), (532, 350))
        if mode == 0:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Easy', 1, (0, 225-floor(((45/51)*i)), 0)), (181.6, 500))
            else:
                screen.blit(Times_New_Roman.render('Easy', 1, (255-i, 255-i, 255-i)), (181.6, 500))
        else:
            screen.blit(Times_New_Roman.render('Easy', 1, (floor((183-(183/255)*i)), 183-floor((183/255)*i), 183-floor((183/255)*i))), (181.6, 500))
        if mode == 1:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Normal', 1, (0, 225-floor((45/51)*i), 0)), (503.16, 500))
            else:
                screen.blit(Times_New_Roman.render('Normal', 1, (255-i, 255-i, 255-i)), (503.16, 500))
        else:
            screen.blit(Times_New_Roman.render('Normal', 1, (183-floor((183/255)*i), 183-floor((183/255)*i), 183-floor((183/255)*i))), (503.16, 500))
        if mode == 2:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Hard', 1, (0, 225-floor((45/51)*i), 0)), (904.7, 500))
            else:
                screen.blit(Times_New_Roman.render('Hard', 1, (255-i, 255-i, 255-i)), (904.7, 500))
        else:
            screen.blit(Times_New_Roman.render('Hard', 1, (183-floor((183/255)*i), 183-floor((183/255)*i), 183-floor((183/255)*i))), (904.7, 500))
        if mode == 3:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Insane', 1, (0, 225-floor((45/51)*i), 0)), (1230.23, 500))
            else:
                screen.blit(Times_New_Roman.render('Insane', 1, (255-i, 255-i, 255-i)), (1230.23, 500))
        else:
            screen.blit(Times_New_Roman.render('Insane', 1, (183-floor((183/255)*i), 183-floor((183/255)*i), 183-floor((183/255)*i))), (1230.23, 500))
        screen.blit(Times_New_Roman.render('Press Space to Start the Game!', 1, (255-i, 255-i, 255-i)), (355, 650))
        screen.blit(Times_New_Roman2.render('(Use Backspace to Deselect)', 1, (255-i, 255-i, 255-i)), (594, 750))
        if mode < 2:
            if i < 127.5:
                pygame.draw.line(screen, (floor(((255-91.5)/(-127.5))*i+255), floor((183/255)*i), floor((183/255)*i)),
                             (875.3792452,701.2641591),
                                 (875.3792452,900), 1)
                pygame.draw.line(screen, (
                floor(((255 - 91.5) / (-127.5)) * i + 255), floor((183 / 255) * i), floor((183 / 255) * i)),
                                 (800, 450),
                                 (823.0323825, 732.6721), 1)
            else:
                pygame.draw.line(screen, (
                floor(((91.5- 183)/ (127.5-255)) * (i-127.5) + 91.5), floor((183 / 255) * i), floor((183 / 255) * i)),
                                 (875.3792452, 701.2641591),
                                 (875.3792452, 900), 1)
                pygame.draw.line(screen, (
                    floor(((91.5- 183)/ (127.5-255)) * (i-127.5) + 91.5), floor((183 / 255) * i), floor((183 / 255) * i)),
                                 (800, 450),
                                 (823.0323825, 732.6721), 1)
        pygame.draw.circle(screen, (255 - i, (255 / 255) * i, 0), (875.3792452, 701.2641691), 100.5056691)
        pygame.draw.circle(screen, (255 - i, 0, i), (800, 450), 5)

        pygame.display.flip()

    if mode == 0:
        thrust = 5000000
    elif 0<mode<3:
        thrust = 500000
    else:
        thrust = 50000

    while running:
        if len(Spheres) > 1:
            screen.fill((0, 0, 0))
        else:
            running = False
        try:
            for i in Spheres:
                i.force()
                i.move()
        except:
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                victory = False
        try:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                run()
            if keys[pygame.K_RIGHT]:
                zoom *= 0.99
            if keys[pygame.K_LEFT]:
                zoom *= (1 / 0.99)
            if keys[pygame.K_w]:
                if randint(0, 10) == 10:
                    Particle(randint(-4, 4) + (width / 2), 7.5 + (height / 2), 0, 1.5)
                Spheres[len(Spheres) - 1].dy -= thrust
            if keys[pygame.K_s]:
                if randint(0, 10) == 10:
                    Particle(randint(-4, 4) + (width / 2), -7.5 + (height / 2), 0, -1.5)
                Spheres[len(Spheres) - 1].dy += thrust
            if keys[pygame.K_d]:
                if randint(0, 10) == 10:
                    Particle(-7.5 + (width / 2), randint(-4, 4) + (height / 2), -1.5, 0)
                Spheres[len(Spheres) - 1].dx += thrust
            if keys[pygame.K_a]:
                if randint(0, 10) == 10:
                    Particle(7.5 + (width / 2), randint(-4, 4) + (height / 2), 1.5, 0)
                Spheres[len(Spheres) - 1].dx -= thrust
        except:
            pass
        try:
            camera_x = -Spheres[len(Spheres) - 1].x
            camera_y = Spheres[len(Spheres) - 1].y
        except:
            pass

        future = []
        try:
            for i in Spheres:
                future.append([i.x, i.y, i.dx, i.dy, i.mass, i.radius, i.index])
            for i in Spheres:
                if i.touched:
                    for j in Spheres:
                        if j.index > i.index:
                            j.index -= 1
                    x_list.pop(j.index)
                    y_list.pop(j.index)
                    mass_list.pop(j.index)
                    Spheres.remove(i)
        except:
            pass

        if mode < 2:
            try:
                for i in Spheres:
                    pygame.draw.line(screen, (183, 183, 183),
                                     (((i.x + 25 * i.dx + camera_x - (width / 2)) / zoom) + (width / 2),
                                      ((i.y + 25 * i.dy - camera_y - (height / 2)) / zoom) + (height / 2)),
                                     (((i.x + camera_x - (width / 2)) / zoom) + (width / 2),
                                      ((i.y - camera_y - (height / 2)) / zoom) + (height / 2)), 1)
            except:
                pass
        for i in Particles:
            i.show()
        try:
            for i in Spheres:
                i.show()
        except:
            pass
        pygame.display.flip()
        sleep(0.001)
    mode = 0
    mode_selected = False
    for i in range(510):
        if i < 255.5:
            screen.fill((0,0,0))
            pygame.draw.circle(screen,(0,0,255-i),(800,450),5)
            pygame.draw.line(screen, (183-floor((183/255)*i), 183-floor((183/255)*i), 183-floor((183/255)*i)),
                             (((Spheres[len(Spheres)-1].x + 25 * Spheres[len(Spheres)-1].dx + camera_x - (width / 2)) / zoom) + (width / 2),
                              ((Spheres[len(Spheres)-1].y + 25 * Spheres[len(Spheres)-1].dy - camera_y - (height / 2)) / zoom) + (height / 2)),
                             (((Spheres[len(Spheres)-1].x + camera_x - (width / 2)) / zoom) + (width / 2),
                              ((Spheres[len(Spheres)-1].y - camera_y - (height / 2)) / zoom) + (height / 2)), 1)
            pygame.display.flip()
        else:
            screen.fill((0,i-255,0))
            screen.blit(Times_New_Roman.render('CONGRATULATIONS!!!!', 1, (i-255, i-255, i-255)),
                        (406, 50))
            screen.blit(Times_New_Roman.render('YOU WON!!!!!', 1, (i-255, i-255, i-255)),
                        (567, 150))
            screen.blit(Times_New_Roman.render('Do you want to play again?', 1, (i-255, i-255, i-255)),
                        (403, 400))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    victory = False
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        victory = False
                    elif event.key == K_RIGHT and not mode_selected:
                        mode += 1
                        if mode == 2:
                            mode = 0
                    elif event.key == K_LEFT and not mode_selected:
                        mode -= 1
                        if mode == -1:
                            mode = 1
                    elif event.key == K_SPACE and mode_selected:
                        victory = False
                    elif event.key == K_SPACE and not mode_selected:
                        mode_selected = True
                    elif event.key == K_BACKSPACE and mode_selected:
                        mode_selected = False

            if mode == 0:
                if mode_selected:
                    screen.blit(Times_New_Roman.render('Yes', 1, (floor((225/255)*(i-255)), 0, 0)), (535, 650))
                else:
                    screen.blit(Times_New_Roman.render('Yes', 1, (i-255, i-255, i-255)), (535, 650))
            else:
                screen.blit(Times_New_Roman.render('Yes', 1, (floor((183/255)*(i-255)), floor((183/255)*(i-255)), floor((183/255)*(i-255)))), (535, 650))
            if mode == 1:
                if mode_selected:
                    screen.blit(Times_New_Roman.render('No', 1, (floor((225/255)*(i-255)), 0, 0)), (960, 650))
                else:
                    screen.blit(Times_New_Roman.render('No', 1, (i-255, i-255, i-255)), (960, 650))
            else:
                screen.blit(Times_New_Roman.render('No', 1, (floor((183/255)*(i-255)), floor((183/255)*(i-255)), floor((183/255)*(i-255)))), (960, 650))
            pygame.display.flip()
    while victory:
        screen.fill((0, 255, 0))
        screen.blit(Times_New_Roman.render('CONGRATULATIONS!!!!', 1, (255, 255, 255)),
                    (406, 50))
        screen.blit(Times_New_Roman.render('YOU WON!!!!!', 1, (255, 255, 255)),
                    (567, 150))
        screen.blit(Times_New_Roman.render('Do you want to play again?', 1, (255, 255, 255)),
                    (403, 400))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                victory = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    victory = False
                elif event.key == K_RIGHT and not mode_selected:
                    mode += 1
                    if mode == 2:
                        mode = 0
                elif event.key == K_LEFT and not mode_selected:
                    mode -= 1
                    if mode == -1:
                        mode = 1
                elif event.key == K_SPACE and mode_selected:
                    victory = False
                elif event.key == K_SPACE and not mode_selected:
                    mode_selected = True
                elif event.key == K_BACKSPACE and mode_selected:
                    mode_selected = False

        if mode == 0:
            if mode_selected:
                screen.blit(Times_New_Roman.render('Yes', 1, (225, 0, 0)), (535, 650))
            else:
                screen.blit(Times_New_Roman.render('Yes', 1, (255, 255, 255)), (535, 650))
        else:
            screen.blit(Times_New_Roman.render('Yes', 1, (183, 183, 183)), (535, 650))
        if mode == 1:
            if mode_selected:
                screen.blit(Times_New_Roman.render('No', 1, (225, 0, 0)), (960, 650))
            else:
                screen.blit(Times_New_Roman.render('No', 1, (255, 255, 255)), (960, 650))
        else:
            screen.blit(Times_New_Roman.render('No', 1, (183, 183, 183)), (960, 650))
        pygame.display.flip()

    if mode == 0:
        run()

run()
